# TASK_042 — p04, ring buffer: the first kernel whose index is modular, and the first with two live cursors

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then `.memory/01-ladder.md` (findings 8 = p07, 10 = p03, 11 = p09, 12 = p12, and
the "R4 is defined by permission" paragraph), `.memory/02-bench-rules.md`
(**including the new "A WRITE bug forces the adversarial row" section — p04's
guard is a live length below capacity, so read the inheritance table before
designing the adversarial rows**), `.memory/03-measurement.md`,
`.memory/04-verus.md`, `.memory/05-layout.md`, then **`patterns/p03-bounded-stack/`
in full** — p03 is the template you clone (same shape: an opcode stream driving a
bounded container). Where this spec is silent, **do what p03 did.**

## Why this pattern

**1. The index is modular, and that is a new relation for the optimiser.** p09
asked whether LLVM carries a bound through a **shift**; p05 asked through a
**multiply**; p04 asks through **`% CAP`**. With `CAP` a power of two the compiler
sees a mask; with `CAP` *not* a power of two it sees a division. **Ship the
power-of-two `CAP` and build the non-power-of-two as a control** — that one edit
is the whole question, and it is the third operator in a series this project has
been building without meaning to.

**2. It is the first kernel with two live cursors.** `head` and `tail` are both
state, both attacker-influenced through the opcode stream, and the emptiness and
fullness conditions are *relations between them* (`head == tail` is empty,
`(tail + 1) % CAP == head` is full) rather than a comparison against a constant.
p03's guard was `sp > 0` against a constant; p04's is a relation, and
`.memory/01-ladder.md` finding 6 records that p05's blocker was a *relational*
deduction. **Expect the R5 invariant to be the interesting part** and budget for it.

**3. Its bug is a wrap that stays in bounds.** Drop the fullness check and a push
onto a full ring overwrites the oldest element — **no OOB access at all**. Every
index remains `< CAP`; ASan, UBSan and Miri see nothing; safe Rust's bounds check
sees nothing; the proof of memory safety discharges. It is p09's `q & 31` shape on
a *container* rather than an index, and it is the second instance of the project's
sharpest claim: **memory safety is not the property that catches this.**

## Kernel contract

| Rung | Signature |
|---|---|
| R1, R1h | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

```
byte 0..4    nops   u32 LE
data_start = 4 ;  avail = len - 4
operations follow, 5 bytes each:  op u8 (0 = PUSH, else POP), val u32 LE
RING_CAP = 64            -- a compile-time constant, a POWER OF TWO, in every rung
```

```
if len < 4:                               return 0
nops from the header
if nops == 0:                             return 0
if 5*nops > avail:                        return 0     # in u64/size_t

ring: [u64; RING_CAP] ;  head = 0 ;  tail = 0 ;  acc = 0
for k in 0 .. nops:
    op  = buf[off + 4 + 5*k]
    val = load_u32(off + 5 + 5*k)
    if op == 0:
        # >>> THE FULLNESS CHECK. R1 omits exactly this line and nothing else. <<<
        if (tail + 1) % RING_CAP != head:
            ring[tail] = val ; tail = (tail + 1) % RING_CAP
    else:
        if head != tail:                  # the emptiness check, in EVERY rung
            acc = acc *64 31 +64 ring[head] ; head = (head + 1) % RING_CAP
return acc *64 31 +64 (head as u64) *64 31 +64 (tail as u64) *64 31 +64 nops
```

Load-bearing, do not "improve":

- **`% RING_CAP`, spelled as `%` in every rung**, pinned in `idiom.required`;
  `& (RING_CAP - 1)` is the `forbidden` spelling. **Backtick both** — a
  bare-string entry is audited zero times (`check.py:929`; p09 shipped five that
  audited nothing).
- **The emptiness check is in every rung; the fullness check is not.** Only one
  is the variable, exactly as p03 did with push/pop. Say so in `NOTES.md`.
- **`head` and `tail` are both folded into the result**, so a rung that wraps
  differently cannot produce the same checksum. This is what makes the bug
  *visible to the model* while remaining invisible to every safety mechanism —
  and it is the p12 lesson applied deliberately rather than stumbled into.
- Wrapping arithmetic throughout.

```
requires:  off + len <= buf_len
ensures:   result == ring_fold(buf, off, len)
```

## What to measure

1. **Does the bound survive `%`?** The access is `ring[tail]` with `tail < CAP`
   maintained by the modular update. Is the check elided, and if not, does p03's
   `m_clamp` control (hand LLVM the invariant as a dead test) delete it? **That is
   the third operator** — shift (p09: composition through the multiply failed),
   multiply (p05), now modulus. Report where `%` falls.
2. **The power-of-two lever.** Build `RING_CAP = 60` as a control. If the mask
   becomes a division the cost story changes completely; if LLVM strength-reduces
   it, say so. This is one edit and it may be the pattern's largest single effect.
3. **What sees the wrap bug.** Run it against every rung, both sanitisers, Miri,
   and the R5 proof with the functional spec **stripped** (p09's `_msonly`
   construction, *with* a positive control so the probe is not blind — `assert(false)`
   in three places and guard deletion). **If memory safety discharges it, that is
   the second instance of p09's result and it belongs in the headline.**
4. **The full protocol before any `ns` claim** — `common/layout/order.py` for the
   identical-copy floor, and **subtract `t(n_iters = 1)`**; the ±9-point bar lives
   in the correction, not the level, so quote the raw level where you can.

## Inputs

| stem | shape | purpose |
|---|---|---|
| `small` | L1-resident, balanced push/pop, ring never full | perf row |
| `large` | past L2, **different fill ratio** | perf row |
| `sweep-n*` | `nops` band | the swept laws |
| `sweep-f*` | **fill-ratio** band at fixed `nops` — the fraction of pushes that hit a full ring | the check's cost is per *rejected* push |
| `adversarial-overwrite` | one window, sustained pushes onto a full ring | **the bug**: R1 overwrites live elements, **stays in bounds** |
| `adversarial-wrap` | `head`/`tail` crossing the wrap point repeatedly | the modular arithmetic itself |
| `adversarial-count` | `5*nops` exceeding `avail` | the omitted length check |

Adversarial rows are **exactly one window** (`n_blob == stride`); **window 0 must
serve something**. Name sweep bands `sweep-*`, appended **last**. ⚠ **Report the
rank of your pooled design** — a band holding one regressor constant cannot
identify it and a per-band fit can return garbage at zero residual (p03, p09, p12).

## Done when

The p03 checklist, plus §"What to measure" 1–4. Complete green `check.py p04`;
checksums against an independent `model.py`; the adversarial table **per rung**;
the `idiom` block written **before** the cells, **every entry backticked**, shared
paragraph byte-identical; a shipped sweep; an in-contract **R3-side span**
("cheapest found", name the input); two proof mutants failing the gate; **the
declared TCB equal to the gate's own `tcb_items` total**.

**Run `./verus_run.py` on an R5 twin BEFORE differencing any unsafe-side
variant**, and **check every control against `check.py::spelling_matches` before
quoting it**.

**Budget: one session for R5.** A stalled proof reported with its exact Verus
error IS the deliverable. Expect the work to be the two-cursor invariant:
`head < CAP && tail < CAP` plus whatever relates them, maintained across an
attacker-chosen branch.

## Constraints

No root; no `/tmp` (scratch `.temp/p04/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`; **do not touch `harness/` or `common/` — if p04 seems
to need a change there, stop and report it**. Do not edit any existing pattern's
sources. Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**; no self-matching
`pgrep` wait-loops. **Measurements in the FOREGROUND, interleaved by cell.**
`harness/measure.py --check-stale` after measuring. Delete binaries and blobs once
the gate is green.

Notes to `.temp/p04/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Fifty-four
agents have contradicted the manager and all fifty-four were right. Two things I
am least sure of:

- **whether the wrap bug is really invisible to a memory-safety proof.** It is the
  whole reason for the pattern. If `ring_fold`'s spec is written from the same
  wrong wrap, the proof passes for the *wrong* reason and the axis evaporates —
  check that on the spec first, the way p09 did. And if R5 *does* catch it, say so
  early: that is a different and also-publishable result.
- **whether `head`/`tail` both being folded is enough to make the bug visible to
  `model.py` without making it visible to the checksum in a way that breaks the
  perf rows.** p12 learned this the hard way in the other direction. Check the
  interaction before building five rungs.
