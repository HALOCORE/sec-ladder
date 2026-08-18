# TASK_014 — p08, overlapping move: the bug safe Rust cannot express

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, `.memory/01-ladder.md` (findings 3, 4, 9–12),
`.memory/02-bench-rules.md`, `.memory/04-verus.md`, `.memory/05-layout.md`
("Adding a pattern" **and** "The five demands steps 1–5 predate"), then
**`patterns/p05-index-flatten/` in full** — p05 is the template you clone. p08
reuses its payload head, its window/Lemire driver, its `work_per_call = stride`
convention, its exit codes and its trusted-accessor shape.

The template is mature. Where this spec is silent, **do what p05 did.**

## Why this pattern

**Every result in this project so far is about a bounds check.** p01/p02/p16/p05
price one; p17 shows one cannot save you. The programme therefore says "Rust
costs a check" and "Rust does not help here" and has **nothing** that says
*"Rust wins structurally, for a reason that is not a runtime check at all."*
That asymmetry will read as bias in a writeup, and it is the largest gap in the
result set.

p08 is that case. Overlapping `memcpy` is UB in C; **safe Rust cannot express
it** — you cannot hold `&[u8]` and `&mut [u8]` into one buffer at once, so the
borrow checker rejects the program *at compile time*, with no runtime cost to
measure because there is no runtime check. The only safe spelling is
`copy_within`, which is `memmove` semantics, i.e. correct by construction.

Three further things make it worth doing now, and the third is the one I care
about most:

1. **Unsafe Rust re-opens the bug**, exactly and only via
   `ptr::copy_nonoverlapping`, whose entire safety contract is the
   non-overlap. So p08 has the full arc — expressible in C, inexpressible in
   safe Rust, expressible again under `unsafe`, and *ruled out by a `requires`*
   at R5. No prior pattern has that shape.
2. **It is UB with no out-of-bounds access.** Every harm this project has
   measured is spatial. Here nothing leaves the allocation; the harm is silent
   corruption. That tests the tooling as much as the ladder.
3. **It should produce the first multi-clause trusted accessor.** Five patterns
   in, every trusted item has been a single-clause `get_unchecked`, so the
   verified twin — a mechanism I designed and `TASK_010_REVIEW` adjudicated as
   worth keeping — **has never once been exercised on the case it was built
   for**. A move's `ensures` needs four clauses (the moved range, the two
   untouched ranges, the length). If the twin is going to earn its keep it will
   be here, and if it stalls, *that* is the measurement.

## The bug class

CWE-1341-adjacent, and in practice the plain one: **`memcpy` where `memmove` is
required.** A fixed read buffer is shifted right to make room at the front —
the nested-encapsulation idiom, where each layer prepends its own framing
header. `memmove(scr + d, scr, m - d)` is correct; `memcpy` is UB, and on a
forward-copying implementation it replicates instead of shifting.

This is **not** another bounds bug. Every rung, R1 included, carries the same
bounds guard. **R1 and R1h differ by exactly one token: `memcpy` vs `memmove`.**

## Kernel contract

| Rung | Signature |
|---|---|
| R1 C, R1h | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Identical to p05's, deliberately — see "The scratch buffer" below for why the
scratch is *not* an argument.

### Window layout and semantics

```
byte 0..2   d_w      u16 LE      # shift distance (the header length)
byte 2..4   nrep_w   u16 LE      # how many framing layers
data_start = 4 ;  avail = len - 4
```

```
SCR = 4096                                  # capacity, a compile-time constant
if len < 4:                        return 0
d, nrep_w from the header
m    = min(avail, SCR)
nrep = 1 + (nrep_w & 3)                     # 1..=4, a mask, not a check

# The bounds guard. EVERY rung has this, R1 included.
if m < 2 || d == 0 || d + nrep > m:  return 0

scr[0..SCR] = 0                             # see "The scratch buffer"
scr[0..m]   = buf[off+4 .. off+4+m]

for r in 0 .. nrep:
    dr = d + r
    # >>> THE OPERATION. R1 spells this memcpy; every other rung memmove. <<<
    move_right(scr, dr, m)                  # scr[dr..m] <- scr[0..m-dr]

acc = 0
for j in 0 .. m: acc = acc *64 31 +64 scr[j]
return acc *64 31 +64 (m as u64)
```

Load-bearing, do not "improve":

- **`dr = d + r`, not a fixed `d`.** With a fixed `d` and `d >= m/2` the rounds
  after the first are *no-ops* — the checksum would stop depending on `nrep`,
  a rung that skipped rounds 2..n would still pass, and LLVM would be free to
  eliminate them. Varying `dr` makes every round change the buffer. The
  realistic reading is nested framing headers of different lengths.
- **The guard is `d + nrep > m`, checked once**, so every `dr` is in range and
  no rung needs a per-round check. Do not push it into the loop.
- **Nothing is written into the space the move opens.** A real encoder writes
  the header bytes there; that is a second bounded loop and adds nothing to the
  aliasing axis. Say so in `NOTES.md` rather than silently omitting it.
- Wrapping arithmetic throughout, as every prior pattern.

### The perf inputs must NOT overlap, and this is the design

If `dr < m - dr` the source `[0, m-dr)` and destination `[dr, m)` ranges
overlap and a forward copy corrupts. **On `small` and `large`, choose
`d >= m/2` so they do not overlap** — then `memcpy` and `memmove` agree, every
rung produces the same checksum, and the perf rows compare like with like.

This is not dodging the bug, it is the point: the overlap is
**attacker-controlled**, because `d` comes from the file. `adversarial-overlap`
is where `d` is small, the ranges overlap deeply, and R1 is the only rung that
gets it wrong.

It also protects the measurement. The driver's `k = (acc * nwin) >> 64` is
derived from the previous result, so **a rung whose checksum diverges visits
different windows** and stops being comparable. Adversarial inputs are one
window (`nwin == 1`, `k == 0` always), so divergence there is harmless — which
is the existing "exactly one window" rule doing a second job here. Say so.

### The scratch buffer

`scr` is a **fixed `SCR = 4096` byte array local to the kernel**, in all six
rungs (`uint8_t scr[4096]` / `[0u8; 4096]`). It is *not* a driver-owned `&mut`
argument, and that is a harness fact rather than a taste call: `driver.call_args`
refuses to drop anything that is not a single bare identifier, so C's `scr` and
Rust's `&mut scr` cannot be reconciled by the driver diff (`harness/dloop.py`),
and making them so is a `harness/` change this task does not authorise.

**Zero-initialise it in every rung, C included.** Rust cannot do otherwise in
safe code; making C match keeps the memset a uniform per-call constant that
cancels in every rung-to-rung comparison. Do not let C skip it. Report the
memset's share of per-call `Ir` — if it is over ~20% and swamps the move, stop
and tell me, do not redesign it yourself.

Consequence, and state it plainly in `NOTES.md`: **p08 has no cache axis in the
scratch.** The working set is 4 KiB in every cell. `small` and `large` differ in
`m`, in `d`'s residue, and in *blob* size — the copy-in reads a pseudo-random
window out of the blob, so locality lives there and nowhere else.

### Contract

```
requires:  off + len <= buf_len
ensures:   result == shift_fold(buf, off, len)
```

## Part 0 — three probes, before you build anything

Each of these can change the design, and two of them are claims of mine that I
want tested rather than inherited. Timebox: a short session, artefacts under
`.temp/p08/probe/`, ~30 lines of C and Rust each. **Report the answers before
writing `spec.md`.**

1. **Does the overlapping `memcpy` actually corrupt on this box?** glibc 2.39,
   x86-64, `memcpy` and `memmove` share ifunc-selected implementations, so it
   may silently produce the right answer — which would be p02's headline shape
   ("silent, plausible, exit 0") and a fine result, but I need to know before
   the inputs are designed. Sweep `m` across the small / vector / ERMS /
   non-temporal size regimes, both `gcc` and `clang`, `-O0` and `-O3`, and
   report the sizes at which the answer diverges from `memmove`'s. Watch for the
   compiler inlining a bounded `memcpy` as load-all-then-store-all, which is
   overlap-safe by accident — check the disassembly for a real `memcpy@plt` /
   `__memcpy_chk@plt`.
2. **Does ASan catch it?** RECAP and `.memory/06-catalogue.md` both assert
   "overlap UB is not caught by ASan". **I now think that is wrong** — the
   `-param-overlap` interceptor string is present in this box's
   `libclang_rt.asan.a`. Settle it: build the overlapping case under ASan
   (static, per `.memory/00-environment.md`) and paste what it prints, or paste
   the clean exit if it prints nothing. Then do the same under
   `~/tools/valgrind/bin/valgrind` (memcheck reports overlap for `memcpy`).
   **If I am wrong, say so — the catalogue line is mine and I will land the
   correction.**
3. **Does LLVM's loop-idiom recogniser turn a safe reverse copy loop into
   `memmove`?** i.e. does `for j in (0..n).rev() { v[j+dr] = v[j] }` compile to a
   `memmove` call at `-O3`? This decides R2-vs-R3 — and if the answer is yes it
   may also decide R5's shape, because a *verified safe loop* would then reach
   R4's machine code without any trusted item at all. Report it; do not silently
   restructure the ladder around it.

**Carry-over, cheap, do it in Part 0 as well:** `patterns/p17-http-range/spec.md`'s
`obligations_note` is arithmetically wrong — its stated derivation predicts 6 for
`main` and the measured value is 5 (p05's character-identical driver also
measures 5, and p05's own note already says so). Fix the one JSON string to quote
`main`'s 5 as measured, the way p05's does. It is **inside the hashed contract
block**, so re-run `harness/check.py p17` afterwards to refresh the gate record,
and paste the verdict. Do not touch anything else in p17.

## The rungs — what each may and may not use

| Rung | The move |
|---|---|
| R1 | `memcpy(scr + dr, scr, m - dr)` — **the bug** |
| R1h | `memmove(scr + dr, scr, m - dr)` — one token apart |
| R2 safe naive | an explicit **reverse indexed byte loop**, bounds-checked. This is what a programmer porting the C actually writes, and it is the fair naive port — not a pessimisation |
| R3 safe tuned | `scr.copy_within(0 .. m - dr, dr)` |
| R4 unsafe | `ptr::copy(p, p.add(dr), m - dr)` |
| R5 | R4's exec code, with the move behind a trusted `ensures` |

**R2 is where the honesty lives.** Safe Rust prevents the *UB*, it does not
prevent *wrongness*: write the loop forward instead of reverse and you get a
silently replicated buffer, safely. Build that as a control and record it. A
writeup that claims "Rust fixes this" without it is overclaiming, and this
project has done that four times already.

Expect `R3 == R4` byte-identical (both lower to `memmove`). If they are, say so
loudly — "the tuned safe rung *is* the unsafe rung, bit for bit" is a result.

## Controls — three, and they are deliverables not extras

1. **The borrow-check rejection.** The C program transliterated into safe Rust,
   which must fail to compile. Paste the exact `rustc` error and code (`E0499` /
   `E0502`). Per `.memory/05-layout.md` item 11, a source file that does not
   compile **cannot live in the pattern dir** — ship it as a `.temp/p08/`
   artefact with a **committed generator** under `patterns/p08-overlap-move/controls/`.
   If you find the gate tolerates it in-tree, say so and I will reconsider the
   rule.
2. **`copy_nonoverlapping` re-opens it.** R4 with `ptr::copy` swapped for
   `ptr::copy_nonoverlapping`, on the overlapping input, under Miri. Same
   generator arrangement. This is the first time the gate's Miri stage is
   pointed at an **aliasing** UB rather than a bounds one — say whether it has
   teeth.
3. **The forward-loop control** from "R2 is where the honesty lives" above.

## What to measure that no prior pattern could

Beyond the standard table, these are the deliverable:

1. **The `memcpy` → `memmove` cost, isolated.** R1 vs R1h is one token; quote
   marginal `Ir` per call and ns per call, both compilers, both opt levels. I
   predict flat and small (finding 3's family). If it is a percentage rather
   than a constant, that is the result and I am wrong.
2. **R2 vs R3 — the idiom question**, decided by disassembly, not by reading
   two timings. Does the reverse loop become a `memmove` call? At what `m`?
3. **The manifestation table**, p02's shape: for each of the eight builds, on
   `adversarial-overlap`, does R1 print the right answer, the wrong answer, or
   abort? With the checksum, not a verdict word.
4. **The detection table**: ASan, valgrind memcheck, Miri, and plain execution,
   against R1's overlap and against R4's `copy_nonoverlapping` mutant. Which
   tools have teeth on aliasing UB.
5. **ns as primary where the move dominates.** `Ir` cannot see a bulk move
   properly — glibc moves a byte in ~0.104 `Ir` (`harness/check.py`'s own floor
   derivation says so) against ~1.4 for a vectorised fold. Report the move's
   share of per-call `Ir` *and* of per-call ns, and if they disagree in
   direction, that is finding 6 again on a new axis. **No cycles/element unless
   the clock is measured interleaved with the wall reps** — `ns` is a
   measurement on this box and `cycles` is an inference (`.memory/00-environment.md`).

## Inputs

| stem | shape | purpose |
|---|---|---|
| `small` | blob L1/L2-resident, `d >= m/2` (no overlap) | perf row |
| `large` | blob past L3, **different `m` and different `d` residue** | perf row |
| `adversarial-overlap` | **one window**, `d` small, `m` large — deep overlap | R1 corrupts or is caught; the headline row |
| `adversarial-dzero` | `d == 0` | every rung returns 0 |
| `adversarial-dbig` | `d + nrep > m` | every rung returns 0 |
| `adversarial-stride3` | stride below the 4-byte header | driver rejects, zero kernel calls |

Adversarial rows are **exactly one window** (`n_blob == stride`) for p05's
reasons, which here also keep a diverging R1 from wandering into different
windows. **Window 0 must serve something** on the perf inputs — a window
returning 0 pins `acc` at 0 and the Lemire index has an absorbing state there.
Give `small` and `large` different `m` residues mod 16 and mod 32; the fold
vectorises and p05 found residue 0 is the *worst* case, not the neutral one.

Miri: per call it is one 4 KiB memset, one `m` copy, `nrep` moves and an `m`
fold — well under the ~16 900 B/s × 180 s budget at these sizes. Confirm rather
than assume.

## Verus, and the twin

The trusted item is the move, not an element accessor:

```
#[verifier::external_body]
fn move_right(v: &mut [u8; SCR], dr: usize, m: usize)
    requires dr <= m, m <= SCR
    ensures  v@.len() == old(v)@.len(),
             forall|j: int| dr <= j < m       ==> v@[j] == old(v)@[j - dr],
             forall|j: int| 0  <= j < dr      ==> v@[j] == old(v)@[j],
             forall|j: int| m  <= j < SCR     ==> v@[j] == old(v)@[j],
```

Sketch, not gospel — get the clause set right for the code you actually write,
and note that **the third and fourth clauses are the ones that make it a real
trusted `ensures`**: without them the proof cannot know the untouched regions
survived, and with them wrong you have axiomatised a falsehood.

The spec side wants a recursive `shift_rounds(s, d, r)` composing a
non-recursive `shift_round(s, dr) = Seq::new(len, |j| if j < dr { s[j] } else
{ s[j-dr] })`, with the kernel invariant `scr@ == shift_rounds(init@, d, r)`.
The trusted `ensures` above is exactly one `shift_round` step, so the induction
should be short. p05's nested-loop invariants are the model.

**The twin is the interesting part.** `slb_twin_move_right` must implement the
same contract in *safe, verified* Rust — the reverse loop with the in-place
shift invariant (indices `>= j` already moved, indices `< j` still original).
That is a real proof and it is the first one that will actually test the
mechanism. Order: **kernel proof first, twin second.**

**Budget: one session for R5.** If the twin stalls, report the exact Verus
error and the obligation you could not discharge — and note that stage 5c-twin
requires the twin to verify, so a stalled twin is a **red gate**, not a missing
row. If that happens, stop and report; do not weaken the trusted contract to
make the twin easy, because a twin that only checks a weakened `ensures` is the
exact failure mode the twin exists to prevent. I will decide what to do.

## Done when

p05's checklist, unchanged, plus Part 0's three answers and items 1–5 of "What
to measure". In particular: complete green `check.py p08`; checksums against
`model.py` on every non-adversarial input; the adversarial table **per rung**;
the three controls with their actual tool output; the decomposition naming a
loop with **R3 quoted first**; two proof mutants failing the gate; the TCB
tally; the twin with `verus.twin_obligations` **and its arithmetic written
out**; an `SLB-TRUSTED-ARGUMENT` block with labels (a)(b)(c) ≥200 chars; and
`spec.md` + `model.py` complete, `model.py` being an independent reference
implementation rather than a transliteration of one rung.

## Constraints

No root; no `/tmp` (scratch `.temp/p08/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/` (report durable facts; I land them); do not touch
`harness/` or `common/` — if p08 seems to need a change there, **stop and report
it**. Do not edit p01/p02/p05/p16 sources; p17 only per the Part 0 carry-over.
Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Check `git status` before finishing and move anything you
created under `results/gate/` into `.temp/p08/`.

Notes to `.temp/p08/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Thirteen
agents have contradicted my written instructions and all thirteen were right;
two of those prescriptions could not have worked at all, and one proved two of
my deliverables mutually inconsistent. In this file the things I am least sure
of are, in order: **(a)** that the overlapping `memcpy` corrupts at all on
glibc 2.39 — if it never does, p08's security axis is "UB that is invisible
without a sanitiser" and I want that said early rather than dressed up;
**(b)** that ASan does not catch it, which I now believe is my error already;
**(c)** that the twin's proof is a session's work rather than a wall.
