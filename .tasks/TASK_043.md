# TASK_043 — p13, `strncpy` truncation: the first bug that is a CORRECTLY-CALLED library function, and the first whose harm lands at a different site

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then `.memory/01-ladder.md` (findings 9 = p11, 12 = p12, and the *"R4 is defined
by permission"* paragraph), **`.memory/02-bench-rules.md`'s *"A WRITE bug forces
the adversarial row"* section — read the inheritance table, because **p13 is
listed there as NOT inheriting p12's rule** and the reason is the design input
for your adversarial rows — then `.memory/03-measurement.md`, `.memory/04-verus.md`,
`.memory/05-layout.md`, then **`patterns/p12-strcat-fixed/` in full** — p12 is
the template you clone (same family, same fixed destination, same NUL
machinery). Where this spec is silent, **do what p12 did.**

## Why this pattern

**1. Every R1 in this project so far omits a line a careful programmer would
have written. p13's omits nothing.** `strncpy(dst, src, sizeof dst)` is textbook
C, correct by the letter of its man page, and still wrong: `strncpy` does not
NUL-terminate when the source is at least as long as `n`. This is the first bug
here that is a **library contract surprise** rather than a missing check, and it
is the single most-cited "safe-looking C function that isn't". The `n` is
**caller-supplied**, which is exactly why `.memory/02-bench-rules.md` says p13
does not inherit p12's forced-adversarial-row rule — here the guard firing is
the *correct* case.

**2. The harm lands at a DIFFERENT SITE from the bug.** The truncating copy is
memory-safe. The out-of-bounds read happens later, in whatever consumes `dst`.
Every prior pattern's bug fires where it is written; this one is the first
**two-site** bug, and that is the proof shape: the obligation is at the *read*,
and what discharges it is an invariant established at the *write* — *"there is a
NUL somewhere in `dst[0..DST_CAP)`"* — carried between two loops. p11 proved a
scan terminates from a sentinel it was **given**; p13 must **establish** the
sentinel first. **Expect that to be the R5 work** and budget for it.

**3. It carries two harms at two different expressiveness levels, from one
omitted line.** Truncation alone is a **memory-safe wrong answer** (p17's shape)
and *every* rung can express it. The missing NUL is an **OOB read** and only C
can express it (p12's shape). One line produces both. No pattern here has had
that structure.

**4. And the library axis is real, on a correctness property rather than a speed
one.** `strncpy` zero-fills the remainder of `n`, so **it is O(DST_CAP) per
string regardless of how short the source is** — a cost essentially nobody
expects from a "copy a string" call. `strlcpy` **is available on this box**
(glibc 2.39; verified) and always terminates without the fill. `snprintf` always
terminates and is far heavier. p11 separated library / spelling / safety on
**speed**; p13 does it on **termination behaviour**, and `.memory/01-ladder.md`
finding 9's rule applies unchanged: **name the routine beside every rate.**

## Kernel contract

| Rung | Signature |
|---|---|
| R1, R1h | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

```
byte 0..4    nstr   u32 LE     -- number of NUL-terminated strings to process
data_start = 4 ;  avail = len - 4
strings follow, each NUL-terminated, packed
DST_CAP = 32             -- a compile-time constant in every rung
```

```
if len < 4:                        return 0
nstr from the header
if nstr == 0:                      return 0

dst: [u8; DST_CAP] ;  acc = 0
p = data_start
for s in 0 .. nstr:
    q = p ; while q < len && buf[off + q] != 0 { q += 1 }    # p11's bounded scan
    slen = q - p

    # --- the copy: EXACT strncpy semantics, spelled out, in every rung ---
    n = min(slen, DST_CAP)
    copy buf[off+p .. off+p+n] into dst[0 .. n]
    for i in n .. DST_CAP:  dst[i] = 0        # strncpy's zero-fill
    # >>> THE TERMINATION. R1 omits exactly this line and nothing else. <<<
    dst[DST_CAP - 1] = 0

    # --- the CONSUMER: the site where the harm lands ---
    d = 0 ; while dst[d] != 0 { d += 1 }      # UNBOUNDED in C. See below.
    acc = acc *64 31 +64 (d as u64)
    acc = acc *64 31 +64 (dst[0] as u64)      # so truncated CONTENT moves the answer

    p = q + 1
    if p >= len { break }
return acc *64 31 +64 (nstr as u64)
```

Load-bearing, do not "improve":

- **`dst` is written in FULL on every iteration** — by the copy when
  `slen >= DST_CAP`, by the copy plus the zero-fill otherwise. That is real
  `strncpy` semantics and it is what keeps this pattern free of an uninitialised
  read and free of any dependence on the previous iteration's contents. **Do not
  "optimise" the zero-fill away in any rung**; it is the thing being measured.
- **The consumer scan is unbounded in C and bounded in Rust**, and that asymmetry
  is the pattern, not a rigged comparison. Spell Rust's as
  `dst.iter().position(|&b| b == 0)` and **report the difference as a semantics
  difference, not a safety cost** (`.memory/01-ladder.md` finding 9's rule).
  Say in `NOTES.md` what safe Rust returns where C runs away.
- **`d` and `dst[0]` are both folded**, so a rung that truncates differently
  cannot produce the same checksum — p12's lesson applied deliberately.
- Wrapping arithmetic throughout.

```
requires:  off + len <= buf_len
ensures:   result == strncpy_fold(buf, off, len)
```

## What to measure

1. **The termination store's cost, and whether it is measurable at all.** `R1h −
   R1` is **one unconditional store per string** — the first safety tax here that
   is not a compare-and-branch. Predict before measuring. The case that can carry
   a cost is `slen >= DST_CAP`, where the zero-fill does not run; where it does
   run, the store may be dead-store-eliminated into it. **Report per what** — per
   string, per *truncated* string, or zero.
2. **The library axis, four ways**: hand loop, `strncpy`, `strlcpy`, `snprintf`.
   Name the routine beside every rate. The prediction to test is that
   **`strncpy`'s cost is flat in the source length and linear in `DST_CAP`** —
   i.e. copying a 3-byte string into a 32-byte buffer costs the same as copying a
   31-byte one. If that holds, sweep it against `DST_CAP = 256` (one edit,
   `controls/`, p04's `RING_CAP = 60` is the model) and it is the pattern's
   largest single effect.
3. **The two harms, separated per rung.** Truncation is memory-safe and every
   rung has it; the missing NUL is an OOB read only C has. **Give them separate
   adversarial rows** and separate table columns — a single "R1 differs" row
   would merge a memory-safe wrong answer with a memory-safety failure, which is
   exactly the distinction p17 exists to make.
4. **The full protocol before any `ns` claim** — `common/layout/order.py` for the
   identical-copy floor (⚠ pass `--input small`, **not** `small.bin`; it appends
   the suffix — p04 §11), and **subtract `t(n_iters = 1)`**; the ±9-point bar
   lives in the correction, so quote the raw level where you can.

## Inputs

| stem | shape | purpose |
|---|---|---|
| `small` | L1-resident, **every string shorter than `DST_CAP`** | perf row; the zero-fill dominates |
| `large` | past L2, **different truncation ratio** | perf row |
| `sweep-n*` | `nstr` band | the swept laws |
| `sweep-l*` | **source-length band CROSSING `DST_CAP`** | separates "per source byte" from "per `DST_CAP` byte" — the axis item 2 lives on |
| `sweep-t*` | **truncation-ratio band** at fixed `nstr` | the fraction of strings that truncate |
| `adversarial-nonul-dst` | one window, every string ≥ `DST_CAP` with no NUL in its first `DST_CAP` bytes | **the OOB read**: R1's consumer runs off `dst` |
| `adversarial-truncate` | truncation that changes the answer while **every rung stays memory-safe** | the p17 harm, isolated |
| `adversarial-nonul-src` | last source string unterminated | p11's bug, as a second way to overrun |

Adversarial rows are **exactly one window** (`n_blob == stride`); **window 0 must
serve something**. Name sweep bands `sweep-*`, appended **last**.

⚠ **Report the rank of your pooled design.** p04 measured that **no pair of its
four bands identified its four regressors** — only the pooled design did, and
the two bands its task file named were rank 4/5. Yours has at least four
regressors (`nstr`, source bytes scanned, truncated strings, `DST_CAP` bytes
filled) and **three named bands**. Check the rank *before* measuring seven cells
across a hundred blobs, and add a band if it does not identify.

## Done when

The p12 checklist, plus §"What to measure" 1–4. Complete green `check.py p13`;
checksums against an independent `model.py`; the adversarial table **per rung**,
with the two harms in separate columns; the `idiom` block written **before** the
cells, **every entry backticked** (a bare-string entry is audited zero times —
`check.py:929`), shared paragraph byte-identical; a shipped sweep with its
**fitter committed under `controls/`** (p04's precedent — the laws must be
re-derivable from the committed tree); an in-contract **R3-side span**
("cheapest found", **name the input** — on p03 and p16 the cheapest spelling
changes with it); two proof mutants failing the gate; **the declared TCB equal to
the gate's own `tcb_items` total**.

**Run `./verus_run.py` on an R5 twin BEFORE differencing any unsafe-side
variant** — this one check would have caught five published figures across two
patterns — and **check every control against `check.py::spelling_matches` before
quoting it**.

**Budget: one session for R5.** A stalled proof reported with its exact Verus
error IS the deliverable. Expect the work to be the **two-site** obligation:
the consumer's `d < DST_CAP` discharged from a NUL-presence fact established by
the writer, carried across a loop boundary.

## Constraints

No root; no `/tmp` (scratch `.temp/p13/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`; **do not touch `harness/` or `common/` — if p13
seems to need a change there, stop and report it**. Do not edit any existing
pattern's sources. Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`,
valgrind `~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on
PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**; no
self-matching `pgrep` wait-loops. **Measurements in the FOREGROUND, interleaved
by cell.** `harness/measure.py --check-stale` after measuring. Delete binaries
and blobs once the gate is green; **keep every generator**.

Notes to `.temp/p13/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Fifty-five
agents have contradicted the manager and all fifty-five were right — p04's
engineer refuted three of my prescriptions in one task. **Settle these two before
building five rungs on them**, the way p04's §0 did:

- **Whether `dst[DST_CAP - 1] = 0` is measurable at all.** If LLVM sinks it into
  the zero-fill or dead-store-eliminates it on every path, `R1h − R1` is exactly
  0 on every input and p13 has **no** safety-tax axis — only the library one.
  That is a publishable result and not a failure, but I need to know **early**,
  because it changes which inputs are worth generating.
- **Whether C's runaway consumer actually leaves the frame.** `dst` is a 32-byte
  local and the scan will meet *some* zero byte within a few bytes of stack
  almost always, so the read may go a handful of bytes past, never fault, and be
  **stably** wrong rather than ASLR-derived. p03's equivalent was *not*
  reproducible across runs and that is one of its sharper findings. **Measure it
  — run the binary repeatedly and under `valgrind --tool=memcheck` — do not
  reason about it.** If p13's is stable, that is the *more* alarming result
  (silently and repeatably wrong) and the adversarial table should say so.
