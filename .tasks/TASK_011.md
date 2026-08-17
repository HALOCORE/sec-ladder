# TASK_011 — p17, the HTTP suffix-range parser: where memory safety stops helping

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.memory/01-ladder.md` (**finding 9**,
p16 — and note how its headline had to be corrected), `.memory/02-bench-rules.md`,
`.memory/04-verus.md`, `.memory/05-layout.md` ("Adding a pattern", **including
"The five demands steps 1–5 predate"** — those are hard gate failures), then
**`patterns/p16-tlv-walk/` in full**. p16 is the template you clone: same payload
head, same window/Lemire driver, same `work_per_call = stride` convention, same
trusted accessor. p17 is p16 plus signed arithmetic.

Reference material, worth 20 minutes before you design anything:
`../LearnVeri/microbench/CVE-2017-7529/` — `analysis.md`, `root-cause.md`,
`lib.c` (`parse_suffix` at :99, `range_copy` at :150). **Do not port that code**;
it is a full server. Lift the *bug*, not the program.

## Why this pattern is the most important one in the catalogue

Every result so far is about cost. **p17 is about a limit**, and it is the first
pattern where the answer to "does Rust fix it?" is *partly no*.

The CVE: `Range: bytes=-N` with `N` larger than the content length makes
`start = content_length - N` **negative** in signed arithmetic, and the guard
`start < end` still passes. The negative start is then added to a base offset.
One missing `start >= 0` check produces **two different harms** depending on how
negative it goes:

| attacker's suffix `s` | what the unchecked read does | ASan | safe Rust |
|---|---|---|---|
| `s <= content_len` | correct | — | correct |
| `content_len < s <= len` | reads the window's own **metadata** — *in bounds of the allocation* | **silent** | **also reads it** |
| `s > len` | reads **before** the allocation | fires | **panics** |

**The middle row is the point.** That read is in-bounds, so bounds checking
cannot see it — not C's, not Rust's, not a proof of memory safety. It is
Heartbleed's shape: a legal read of the wrong bytes. Safe Rust eliminates the
third row and **does nothing about the second**. The only thing that fixes the
second row is the explicit `start >= 0` check, which is identical in C and Rust.

This gives the project its first negative result about memory safety, and it is
worth more than another cost measurement. **It must be demonstrated, not
asserted** — see "The two controls" below.

There is a second, matching result on the Verus side. A proof that every access
is in bounds discharges the third row and **not** the second, because the second
row *is* in bounds. Only the functional `ensures` (`result == model`) catches it.
So p17 measures the difference between *proving memory safety* and *proving the
program right* — a distinction this project has asserted since finding 2 and has
never been able to put a number on.

## The bug class

CWE-191, integer underflow, and **the sign is the whole pattern.** p16 underflowed
`size_t` and walked forward unboundedly. p17 underflows *signed* and indexes
**backwards**. Different sanitizer signature (`located N bytes before` rather than
`after`), different Rust behaviour, different proof obligation.

## Kernel contract

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Returns `u64`, deliberately. **Do not use a struct out-parameter** — it is a
known harness hard stop (`dloop._apply_call_args` refuses a non-identifier
argument) and this design does not need one. If you find yourself wanting one,
stop and report rather than changing the harness.

### Window layout and semantics

The window is `buf[off .. off+len]`. Everything is window-relative:

```
byte 0..2      nsuf        u16 LE   number of suffix requests
byte 2..2+2n   suffixes    u16 LE each
body_start  =  2 + 2*nsuf
content_len =  len - body_start          # the REAL body length, derived
```

```
if len < 2:                       return 0
nsuf = buf[off] + 256*buf[off+1]
if 2 + 2*nsuf > len:              return 0        # present in EVERY rung
body_start  = 2 + 2*nsuf
content_len = len - body_start
acc = 0; nserved = 0

for i in 0 .. nsuf:
    s     = buf[off+2+2i] + 256*buf[off+3+2i]         # u16, attacker-controlled
    start = content_len as i64 - s as i64             # <<< SIGNED. May be < 0.
    end   = content_len as i64
    if start >= end:              continue            # empty range, skip

    # >>> THE CHECK. R1 omits exactly this line and nothing else. <<<
    if start < 0:                 continue

    abs = body_start as i64 + start
    n   = end - start
    for j in 0 .. n:
        acc = acc *64 31 +64 buf[off + (abs + j) as usize]
    nserved += 1

return acc *64 31 +64 nserved
```

**The identity that makes the whole design work, verified by the manager before
this task was written** (re-verify it anyway — it is load-bearing):

`abs = body_start + start = body_start + content_len - s = len - s`, and
`n = end - start = s`. So the served range is `[len - s, len)` — **exactly the
last `s` bytes of the window**, which is what a suffix range *means*. The kernel
is therefore semantically faithful, not a contrivance, and the three regimes fall
straight out of one attacker-controlled number:

| `len` | `nsuf` | `body_start` | `content_len` | `s` | `start` | `abs` | regime |
|---:|---:|---:|---:|---:|---:|---:|---|
| 64 | 3 | 8 | 56 | 10 | 46 | 54 | correct |
| 64 | 3 | 8 | 56 | 56 | 0 | 8 | correct (whole body) |
| 64 | 3 | 8 | 56 | 58 | **−2** | 6 | **leak** — in bounds, into the suffix table |
| 64 | 3 | 8 | 56 | 64 | −8 | 0 | leak — the whole window incl. `nsuf` |
| 64 | 3 | 8 | 56 | 70 | −14 | **−6** | **OOB** — before the allocation |

Note the read never runs *past* the window (`abs + n == len` always); it only
runs backwards. That is the signed-underflow signature and the reason p17's ASan
message will say *before* where p16's said *after*.

Load-bearing, do not "improve":

- **`start` and `end` are `int64_t` / `i64`.** That is the CVE. Do not make them
  unsigned "to be safe" — you would delete the pattern.
- **R1 omits only `if start < 0`.** It keeps `2 + 2*nsuf > len`, exactly as p16's
  R1 kept `end - p >= 3`. One edit between R1 and R1h.
- **Wrapping `*64`/`+64`**, as p01/p02/p16, so the kernel has no precondition on
  values.
- **`nserved` is folded into the result**, so a rung that skips or serves a
  different number of ranges cannot produce the same checksum.
- **No `Range:` text parsing.** Byte fields, not ASCII. String parsing is p11–p15
  and would add a second new variable.

### Contract

```
requires:  off + len <= buf_len
ensures:   result == range_fold(buf, off, len)
```

`range_fold` is the spec function; `model.py` is its independent Python twin.

**The `ensures` matters more here than in p16, and say so in `NOTES.md`.** In p16
the security property *was* the accessor's `requires`. In p17 the accessor's
`requires` catches only the third row of the table above. The second row is a
**functional** defect that is memory-safe, and only `result == range_fold(...)`
excludes it. That is the measurement this pattern exists to make.

## The two controls — these are the deliverable, not a side quest

1. **`safe_naive_nocheck.rs`** — R2 with `if start < 0 { continue }` deleted,
   built under `.temp/`, never a rung. Run it on **both** adversarial inputs and
   record, separately:
   - on the leak input: does it panic, or does it print a wrong answer? **Predict
     the latter.** If safe Rust silently produces C's leaked value, that is the
     project's first measured limit of memory safety, and it needs the actual
     stdout beside C's in the table.
   - on the OOB input: it should panic (exit 101). Contrast in one sentence.
2. **`verus_nocheck.rs`** — R5 with the same line deleted. Report which of the
   two fails and how:
   - does the *memory-safety* obligation (`get_unchecked`'s `requires`) fail?
   - does the *functional* `ensures` fail?
   **Predict: only the second, on the leak input's shape.** Paste the Verus error
   text for each. If the memory-safety obligation also fails, my model of this is
   wrong and I want to know with the output.

Both controls must appear in `NOTES.md` with real output. A prediction I wrote
that your measurement contradicts is a **finding** — say so plainly.

## Payload and driver

Identical to p16: one `u64 stride` head, then the blob. **`common/head1_u64_bytes`
already exists** (p16 added it in all three languages) — reuse it, add nothing to
`common/`. Driver skeleton is p16's with `stride_w >= 2`:

```
n_blob := bytes.len(); buf := bytes; acc := 0
if stride_w >= 2 and stride_w <= n_blob:
    stride := stride_w as usize; nwin := (n_blob / stride) as u64; it := 0
    while it < n_iters:
        k   := ((acc as u128 * nwin as u128) >> 64) as usize
        r   := kernel(buf, k * stride, stride)
        acc := acc *64 31 +64 r
        it  := it + 1
emit(acc)
```

Generate `driver.canonical` with `python3 harness/dloop.py <rung>.rs`. Do not
hand-write it and do not copy p16's.

`work_per_call = stride`, constant per input, as p16 — **not** bytes folded,
which here is a distribution (each suffix serves a different length). p16's
`model.py` docstring argues the unit; mirror that argument.

## Inputs

| stem | shape | purpose |
|---|---|---|
| `small` | windows tiling L1, well-formed suffixes | perf row |
| `large` | blob past L2, different stride from `small` | perf row |
| `adversarial-leak` | **one window**, a suffix with `content_len < s <= len` | the in-bounds metadata read — **no sanitizer should fire** |
| `adversarial-oob` | **one window**, a suffix with `s > len` | reads before the allocation — ASan must fire |
| `adversarial-nsuf` | `2 + 2*nsuf > len` | the check every rung keeps; all rungs return 0 |

**Both adversarial rows must be exactly one window** (`n_blob == stride`), for
p16's reason: `k` is pseudo-random over `[0, nwin)`, so with several windows the
malformed one is hit probabilistically *and* a backward index from a middle
window stays inside the allocation — silent wrong answer, no ASan, a gate that
passes by luck. With `nwin == 1`, `k` is always 0.

**Miri sizing** (`.memory/02-bench-rules.md`): `n_iters` is **not** the knob — the
gate rewrites it to 4. Cost is driven by bytes folded per call at ~16 900 B/s
against a 180 s budget. Keep strides well under ~700 KiB. p16's largest stride
was 4090 B and all rows finished; there is no reason to go bigger.

Give `small` and `large` **different strides** (the marginal-`Ir` assertion needs
two different `work_per_call`) **and different residues mod 4, 8 and 16**. p16's
modulus turned out to be 4, p02's was 16, p01's was 4 — do not assume.

## Decomposition — mandatory, before any claim

p16's headline was corrected at review for a framing error, and p02's was
retracted outright. **Do not report a single R2-vs-R4 number.** Build under
`.temp/`, measure, then write:

1. R2 as shipped.
2. R2 with the inner byte fold replaced by an iterator/slice fold.
3. R2 with the suffix walk rewritten to reslice.
4. Both.
5. The signed arithmetic done in `i128` (a measurement of what the width costs).

State which loop the delta lives in. **Lead with R3, always** — that rule is in
`.memory/01-ladder.md` finding 3 and its author broke it on p16.

Expect the signed↔unsigned conversions to cost something in the *safe* rungs
specifically (`as i64` / `as usize` with a bounds check on the way back). If they
do, that is a real and new sub-finding: **the cost of the check is not the
comparison, it is the conversion.** Decompose before saying it.

## Expected proof sticking points

- **Signed/unsigned mixing is the whole proof.** Verus needs `start >= 0` before
  `abs as usize` is meaningful. That is not an obstacle — it is the pattern:
  the proof cannot even be *stated* without the check the CVE was missing. Say so
  in `NOTES.md`; it is a cleaner version of p16's `decreases` point.
- Reuse p16's nonlinear driver lemmas verbatim where they apply.
- `assert(buf@.len() == vstd::slice::spec_slice_len(buf));` once before the loop.
- Nested loops: the outer over suffixes, the inner over served bytes. The inner
  needs its own invariant relating `acc` to `range_fold` over the prefix served
  so far. p16's "the walk from here is the whole walk" shape should transfer.

**Budget: one session for R5.** If it stalls, stop and report the exact Verus
error and the obligation you could not discharge — that report *is* the
deliverable for that row (`.memory/02-bench-rules.md`).

## Part 0 — one owed re-measurement, do this first

`results/p02-buffer-copy.json` has been stale since TASK_005 and its precondition
is now met (p16's `common/head1_u64_bytes` has landed, so `common/` will not move
again for p17). **Run `measure.py p02` exactly once**, then re-quote the three
tables in `patterns/p02-buffer-copy/NOTES.md` from that one JSON. Exposure is
`binary_text_bytes` and the wall-clock column only; kernel columns are safe.
While you are there: `p02/NOTES.md` §3c's "with `memcpy`" row does not reproduce
(9200.3 / 10204.3 published, 9200.74 / 10204.74 measured on the gate's own
`c-gcc-h` / `c-clang-h`). Fix the row from the new run and note it.

Do **not** touch p02's sources.

## Done when

1. All cells build at both opt levels and both inline modes; `check.py p17` green
   on a **complete** run, or every non-green row documented with its reason.
2. Checksums agree across rungs on `small`/`large` and against `model.py`.
3. **The adversarial table separates the two harms per rung** — exit code,
   stdout, stderr, ASan/UBSan, panic, silent-wrong-answer. `adversarial-oob` must
   fire ASan on R1; `adversarial-leak` must **not**, and must show a wrong answer.
   If ASan fires on the leak input, the input is mis-targeted — fix the input.
4. Both controls of "The two controls" are built, run and tabulated.
5. The decomposition table exists and the perf claim names a loop, R3 first.
6. Proof mutants: one weakening the accessor's `requires`, one making the kernel's
   `ensures` trivial. Paste both gate failures.
7. `NOTES.md` carries the TCB tally per `.memory/04-verus.md` (every
   `external_body` item, individually), plus the three artefacts p16 needed:
   the `#[cfg(slb_twin)]` twin, `verus.twin_obligations` **with its arithmetic
   written out**, and an `SLB-TRUSTED-ARGUMENT` block with labels (a)(b)(c),
   ≥200 chars.
8. **Say whether the twin is idle again.** If p17's accessor is single-clause like
   p16's, say so — a green twin check proves nothing there, and
   `.memory/04-verus.md` requires the caveat. If p17 naturally needs a
   multi-clause trusted item, say that too: it would be the first, and the review
   that kept the twin said that is where its value starts. **Do not manufacture a
   multi-clause accessor to exercise the mechanism** — that would be gaming the
   gate, and reporting "still idle" is the honest outcome.

## Constraints

No root; no `/tmp` (scratch `.temp/p17/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/` (report durable facts in your final message; the
manager lands them); do not edit p01/p16 sources, and touch p02 only per Part 0.
Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`.

Notes to `.temp/p17/NOTES.md` as you go — agents here die to transient API errors
and notes make a resume cheap.

**If a prescription in this file is wrong, say so with the measurement.** Nine
agents have now contradicted the manager's written instructions and all nine were
right; the last one caught the manager overclaiming a headline. The predictions in
"The two controls" and the `abs = len - s` identity are the least certain things
here and the most load-bearing — check them first.
