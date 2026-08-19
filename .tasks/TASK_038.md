# TASK_038 — p09, bitset: two bugs in one kernel, and only one of them is a memory error

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then `.memory/01-ladder.md` (findings 5 = p17, 6 = p05, 9 = p11, 10 = p03, and the
"R4 is defined by permission" paragraph), `.memory/02-bench-rules.md`,
`.memory/03-measurement.md`, `.memory/04-verus.md`, `.memory/05-layout.md`, then
**`patterns/p03-bounded-stack/` in full** — p03 is the template you clone. Where
this spec is silent, **do what p03 did.**

## Why this pattern

**1. Its safety check is not a bounds check.** Every pattern so far guards a
*range*. p09's guard is `q < nbits` while the *access* is `words[q >> 6]` — so
the bound LLVM must establish is **derived through a shift**. Does it connect
`q < nbits` to `q >> 6 < nbits.div_ceil(64)`? That is p05's question
(`.memory/01-ladder.md` finding 6) on a **different operator**, and p03 just
showed the same class of failure is **not Rust-specific** and is analysis
*seeding* rather than an inability to prove. p09 is the third data point and the
first where the relation is a shift.

**2. It carries two bugs, and only one is a memory error.** That is the point of
the pattern:

- **the spatial bug** — omit `q < nbits` and `q >> 6` walks off the word array;
- **the arithmetic bug** — spell the shift `q >> 5` (or the mask `q & 31`). The
  index stays *in bounds*, every rung including R5 returns the same **wrong**
  answer, and no sanitiser, no bounds check and no proof of memory safety says
  anything. p17 established that a memory-safe program can be wrong; **p09 makes
  the wrongness a one-character edit in the same kernel that also has a real
  overrun**, so the two can be measured side by side.

Report explicitly: **which rungs catch which bug, and with what.** I expect the
answer to be "every rung catches the first, no rung catches the second, and the
`ensures` catches the second only because `model.py` disagrees" — say so if that
is what you find, and say what that costs the reader.

**3. First bit-level kernel.** `u64::count_ones()` vs `__builtin_popcountll`
vs `popcnt` — a same-backend intrinsic comparison, and the first time this project
measures anything that is not a byte or a word load.

## Kernel contract

| Rung | Signature |
|---|---|
| R1, R1h | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

```
byte 0..4    nbits  u32 LE
byte 4..8    nq     u32 LE
data_start = 8 ;  nwords = ceil(nbits / 64)
words:   nwords * 8 bytes at data_start          (u64 LE)
queries: nq * 4 bytes after them                 (u32 LE bit indices)
```

```
if len < 8:                                   return 0
nbits, nq from the header
if nbits == 0 || nq == 0:                     return 0
if 8*nwords + 4*nq > avail:                   return 0     # in u64/size_t

acc = 0 ; hits = 0
for k in 0 .. nq:
    q = load_u32(queries + 4*k)
    # >>> THE GUARD. R1 omits exactly this line and nothing else. <<<
    if q < nbits:
        w = load_u64(words + 8*(q >> 6))       # SHIFT, not divide -- pin it
        if w & (1u64 << (q & 63)) != 0:  hits += 1
        acc = acc *64 31 +64 w
acc = acc *64 31 +64 hits
for i in 0 .. nwords:                          # the popcount pass
    acc = acc *64 31 +64 popcount(load_u64(words + 8*i))
return acc *64 31 +64 nbits *64 31 +64 nq
```

Load-bearing, do not "improve":

- **`q >> 6` and `q & 63`, spelled as shift and mask in every rung**, pinned in
  `idiom.required`. `/64` and `%64` are the `forbidden` spelling — they are the
  same function on unsigned values and *may* give LLVM a different relation, which
  is exactly the thing being measured. If they compile identically, that is a
  finding; report it, do not use it to justify changing the source.
- **`hits` and the popcount pass are both folded**, so a rung that tests the wrong
  bit or reads the wrong word cannot produce the same checksum.
- **The popcount pass is separate from the query loop** — it is the intrinsic
  comparison and must not be fused into a data-dependent loop.
- Wrapping arithmetic throughout.

```
requires:  off + len <= buf_len
ensures:   result == bitset_fold(buf, off, len)
```

## What to measure

1. **Does the guard's bound survive the shift?** The safety cost per *guarded
   query*, swept — and if a check survives, the `m_clamp`-shaped control from p03
   (hand LLVM the derived fact as a dead test) to see whether it is the same
   seeding failure. **If it is, that is the third instance and it generalises;
   if it is not, say why this operator differs.**
2. **The arithmetic bug's cost: zero.** Build the `>> 5` variant as a control and
   show it is the *same* machine code shape at a different constant, that every
   rung agrees with every other rung, and that only `model.py` catches it. Quote
   what the sanitisers say (nothing).
3. **`count_ones()` vs `__builtin_popcountll`.** Report the emitted instruction
   per rung and whether `-mpopcnt` is implied by this box's default `-march`. If
   any rung emits a software popcount while another emits `popcnt`, the comparison
   is a **library/ISA** difference and must be separated from the safety number —
   p11's rule (`.memory/03-measurement.md`).
4. **The full wall-clock protocol** — `common/layout/order.py` for the
   identical-copy floor *first*. ⚠ **This box has been in a noisy regime**; if
   your spreads trip the 10% rule, say the column is unresolved rather than
   forcing it.

## Inputs

| stem | shape | purpose |
|---|---|---|
| `small` | L1-resident | perf row |
| `large` | past L2, **different hit density** from `small` | perf row |
| `sweep-n*` | `nq` band | the swept laws |
| `sweep-d*` | **hit-density** band (fraction of queries with `q < nbits`) at fixed `nq` | the guard's cost is per *guarded* query, so this is the second axis |
| `adversarial-oob` | one window, `q` far beyond `nbits` | **the spatial bug**: `q >> 6` off the word array; ASan must fire on R1 |
| `adversarial-edge` | `q == nbits`, `q == nbits-1`, `nbits` not a multiple of 64 | the off-by-one and the partial last word |
| `adversarial-count` | `8*nwords + 4*nq` exceeding `avail` | the omitted length check |

Adversarial rows are **exactly one window** (`n_blob == stride`); **window 0 must
serve something** or the driver's Lemire index has an absorbing state at 0. Name
the sweep bands `sweep-*`, appended **last** to `gen.py`.

⚠ **Rank-deficiency, from p03**: a band that holds one regressor constant cannot
identify it, and a per-band fit can return garbage **at zero residual**. Check the
rank of your pooled design and say what it is.

## Done when

The p03 checklist, plus §"What to measure" 1–4. Complete green `check.py p09`;
checksums against an independent `model.py`; the adversarial table **per rung**;
the `idiom` block written **before** the cells with its shared paragraph verified
byte-identical against p03's; a shipped sweep; an in-contract **R3-side span**
(never "minimum" — "cheapest found", and name the input); two proof mutants
failing the gate; the TCB tally; the twin with its arithmetic written out.

**Run `./verus_run.py` on an R5 twin BEFORE differencing any unsafe-side
variant.** Read the error text, not the exit code. **And check any control against
`check.py::spelling_matches` before quoting it** — p03 shipped two controls that
were out of contract and one of them reached a published mechanism.

**Budget: one session for R5.** A stalled proof reported with its exact Verus
error IS the deliverable for that row. Expect the work to be relating `q < nbits`
to `q >> 6 < nwords`; `.memory/04-verus.md` has the shift lemmas.

## Constraints

No root; no `/tmp` (scratch `.temp/p09/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`; **do not touch `harness/` or `common/` — if p09 seems
to need a change there, stop and report it**. Do not edit any existing pattern's
sources. Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; confirm an exact PID's full command
line before any kill, **and no monitor wait-loops with self-matching `pgrep`
patterns**. **Measurements in the FOREGROUND, interleaved by cell.** Run
`harness/measure.py --check-stale` after measuring. Delete your binaries and blobs
once the gate is green.

Notes to `.temp/p09/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Forty-eight
agents have contradicted the manager and all forty-eight were right. Two things I
am least sure of:

- **whether the arithmetic bug is really invisible to R5.** The `ensures` says
  `result == bitset_fold(...)`, and if `bitset_fold`'s spec is written from the
  same wrong shift, the proof passes and the pattern's whole second axis
  evaporates. **Check that first**, on the spec, before building rungs — and if
  R5 *does* catch it, that is a *better* result than the one I designed for and it
  should lead the pattern.
- **whether `q >> 6` and `q / 64` actually differ to LLVM.** If they are the same
  IR immediately, the `forbidden` entry pins nothing and should say so rather than
  implying a distinction the compiler does not make.
