# TASK_040 — p12, `strcat` into a fixed buffer: the first kernel that WRITES past a bound

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then `.memory/01-ladder.md` (findings 2 = p02, 9 = p11, 10 = p03, 11 = p09, and
the "R4 is defined by permission" paragraph), `.memory/02-bench-rules.md`,
`.memory/03-measurement.md`, `.memory/04-verus.md`, `.memory/05-layout.md`, then
**`patterns/p11-nul-scan/` in full** — p11 is the template you clone (same family,
same NUL machinery). Where this spec is silent, **do what p11 did.**

## Why this pattern

**1. Every bug in this project so far is a READ.** p02 is the only write, and it
is a bulk `memcpy`. p12 is the classic **stack** buffer overflow — `strcat` into a
fixed local array — which is the single most-cited memory-safety bug in C and the
one this project's audience will look for first. It is currently absent.

**2. It is the first pattern where the safe rung cannot express the bug at all.**
p08 established that shape for aliasing; here it is length. `String::push_str`
grows; a fixed `[u8; N]` in safe Rust cannot be written past its end. So R2/R3
must be written with an **explicit capacity check**, and the interesting question
is what that check costs against C's `strcat`, which has none — and against
`strncat`/`snprintf`, which have one.

**3. The C rung's bug lands in the same frame as the return address.** p03 showed
a stack *under*-read is ASLR-derived and non-deterministic; a stack **over-write**
of a fixed local is the canonical smash. Report what actually happens at the gate's
own flags: does the canary fire, does ASan report `stack-buffer-overflow`, and is
the wrong answer stable or ASLR-derived? p03's answer was "not reproducible across
runs"; predict and check.

## Kernel contract

| Rung | Signature |
|---|---|
| R1, R1h | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

```
byte 0..4    nstr   u32 LE     -- number of NUL-terminated strings to concatenate
data_start = 4 ;  avail = len - 4
strings follow, each NUL-terminated, packed
DST_CAP = 128            -- a compile-time constant in every rung
```

```
if len < 4:                        return 0
nstr from the header
if nstr == 0:                      return 0

dst: [u8; DST_CAP] ;  dlen = 0 ;  acc = 0
p = data_start
for s in 0 .. nstr:
    q = p ; while buf[off + q] != 0 { q += 1 }   # the p11 scan, bounded by len
    slen = q - p
    # >>> THE CAPACITY CHECK. R1 omits exactly this line and nothing else. <<<
    if dlen + slen <= DST_CAP:
        copy buf[off+p .. off+q] into dst[dlen ..]
        dlen += slen
    acc = acc *64 31 +64 (slen as u64)
    p = q + 1
    if p >= len { break }
for i in 0 .. dlen:                              # fold the destination
    acc = acc *64 31 +64 dst[i]
return acc *64 31 +64 (dlen as u64) *64 31 +64 nstr
```

Load-bearing, do not "improve":

- **`dlen + slen <= DST_CAP` in `usize`.** Note in `NOTES.md` whether the same
  check in a narrower type can overflow and wave the attack through, and **build
  that as the R1h-gets-it-wrong control** — it is one line and it is what makes
  R1h meaningful (p05's precedent).
- **The copy is a loop, not `memcpy`/`copy_from_slice`, in R1 and R2.** p02's
  retraction is the precedent: one operator flips `bulk_calls` and 100% of the
  delta. R3 and R4 may use the bulk idiom — that is the *measurement*, and it must
  be reported as a spelling difference, not a safety one (p11's rule).
- **`dlen` and `nstr` are folded**, so a rung that truncates differently cannot
  produce the same checksum.
- Wrapping arithmetic throughout.

```
requires:  off + len <= buf_len
ensures:   result == strcat_fold(buf, off, len)
```

## What to measure

1. **The capacity check's cost, per what?** Per string, per byte copied, or per
   *accepted* string. p03's law was per *executed* operation and p09's per
   *guarded* query; predict before measuring and say whether you were right.
2. **R1 vs R1h vs `strncat` vs `snprintf`.** All four are what a C programmer
   actually writes. The last two carry the check *inside libc*, so this is p11's
   library-vs-safety separation again — **name the routine beside every rate**.
3. **What safe Rust cannot express**, stated precisely and measured where
   possible: `dst[dlen..dlen+slen].copy_from_slice(..)` panics rather than
   overflowing, so the *control* is deleting the check from R2/R3 and showing it
   panics where C corrupts. p02's control is the model.
4. **The full protocol before any `ns` claim** — `common/layout/order.py` for the
   identical-copy floor, and ⚠ **subtract `t(n_iters = 1)`** before quoting any
   ratio (`.memory/03-measurement.md`; the per-process constant was 55–73% on
   p09 and it killed a published mechanism).

## Inputs

| stem | shape | purpose |
|---|---|---|
| `small` | L1-resident, total well under `DST_CAP` | perf row |
| `large` | past L2, **different acceptance ratio** | perf row |
| `sweep-n*` | `nstr` band | the swept laws |
| `sweep-a*` | **acceptance-ratio** band at fixed `nstr` | item 1's second axis |
| `adversarial-overflow` | one window, strings totalling well past `DST_CAP` | **the bug**: R1 smashes the frame; ASan must fire |
| `adversarial-exact` | total exactly `DST_CAP`, and `DST_CAP + 1` | the off-by-one |
| `adversarial-nonul` | last string unterminated | p11's bug, here as a *second* way to overrun |

Adversarial rows are **exactly one window** (`n_blob == stride`); **window 0 must
serve something**. Name sweep bands `sweep-*`, appended **last**.

⚠ **Rank-deficiency (p03, p09)**: a band holding one regressor constant cannot
identify it and a per-band fit can return garbage **at zero residual**. Report the
rank of your pooled design.

## Done when

The p11 checklist, plus §"What to measure" 1–4. Complete green `check.py p12`;
checksums against an independent `model.py`; the adversarial table **per rung**;
the `idiom` block written **before** the cells, **every `required` and `forbidden`
entry BACKTICKED** (a bare-string entry is audited zero times — `check.py:929`,
and p09 shipped five that audited nothing), shared paragraph byte-identical; a
shipped sweep; an in-contract **R3-side span** ("cheapest found", name the input);
two proof mutants failing the gate; the TCB tally **equal to the gate's own
`tcb_items` total** (p09 declared 12 where the gate said 7).

**Run `./verus_run.py` on an R5 twin BEFORE differencing any unsafe-side
variant**, and **check every control against `check.py::spelling_matches` before
quoting it.**

**Budget: one session for R5.** A stalled proof reported with its exact Verus
error IS the deliverable for that row. Expect the work to be the write
obligation — `dlen + slen <= DST_CAP` maintained across a loop that also advances
`p` — which is the first *write* precondition in this project.

## Constraints

No root; no `/tmp` (scratch `.temp/p12/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`; **do not touch `harness/` or `common/` — if p12 seems
to need a change there, stop and report it**. Do not edit any existing pattern's
sources. Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`. **No `nohup … &` background jobs** —
one reported exit 0 after 1 of 8 cells. **Measurements in the FOREGROUND,
interleaved by cell.** `harness/measure.py --check-stale` after measuring. Delete
binaries and blobs once the gate is green.

Notes to `.temp/p12/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Fifty-one agents
have contradicted the manager and all fifty-one were right. Two things I am least
sure of:

- **whether the C rung's overflow is observable at all at the gate's flags.**
  `dst` is a fixed local, so `-fstack-protector` (this box's default) may abort
  before the checksum is printed, which would make R1's row an abort rather than
  the silent corruption p02 made its name on. **If R1 aborts on every input, the
  pattern measures something different from what I designed** — tell me early, and
  say whether an `-fno-stack-protector` cell is the honest control or a thumb on
  the scale.
- **whether `DST_CAP = 128` and the accept/reject mix leave anything to measure.**
  If almost every string is accepted, the check is never exercised on the reject
  path; if almost none, the copy loop vanishes. Check the balance before building
  five rungs on it.
