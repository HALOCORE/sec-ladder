# TASK_036 — p03, bounded stack: the first kernel whose control flow is attacker-chosen

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**
(the distilled methodology — it is why p11 needed only prose corrections and no
re-measurement), then `.memory/01-ladder.md` (findings 3–5, 8, 9 and the "R4 is
defined by permission" paragraph), `.memory/02-bench-rules.md`,
`.memory/03-measurement.md`, `.memory/04-verus.md`, `.memory/05-layout.md`, then
**`patterns/p11-nul-scan/` in full** — p11 is the template you clone. Where this
spec is silent, **do what p11 did.**

## Why this pattern

**1. Every kernel so far has a straight-line shape.** p01/p02/p05/p16/p17 fold,
p07 searches, p11 scans — in all eight the *sequence of operations* is fixed by
the code and only the data varies. **p03's operation sequence is in the file.**
An opcode stream decides, per step, whether the kernel pushes or pops. That is
the first kernel where the attacker chooses the control flow, and it is what a
protocol state machine or a bytecode interpreter actually looks like.

**2. The bug is a stack underflow, which is a different failure from all eight.**
p16 walks one step past a length; p17 computes a wrong-but-in-bounds index; p07
underflows an *inclusive bound*; p11's loop does not stop. **Here the index goes
negative** — `sp - 1` at `sp == 0` — and on `usize` that is `SIZE_MAX`. The read
is wildly out of bounds, so a sanitiser should catch it every time. p11 predicted
the same and it held; predict it again and say whether it does.

**3. It is the first pattern where safe Rust's check is not on a slice.** The
stack is a fixed-size local array and the guard is `sp > 0` — an *emptiness* test,
not a bounds test. Expect the R2/R3/R4 story to be different in kind from every
per-byte constant this project has measured, and say what it is rather than
assuming it is another `2.00`/`3.00`.

## Kernel contract

| Rung | Signature |
|---|---|
| R1, R1h | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

### Window layout and semantics

```
byte 0..4    nops   u32 LE    -- number of operations
data_start = 4 ;  avail = len - 4
operations follow, 5 bytes each:  op u8 (0 = PUSH, else POP), val u32 LE
STACK_CAP = 64          -- a compile-time constant in every rung
```

```
if len < 4:                               return 0
nops from the header
if nops == 0:                             return 0
if 5*nops > avail:                        return 0     # computed in u64/size_t

stack: [u64; STACK_CAP] ;  sp = 0 ;  acc = 0
for k in 0 .. nops:
    op  = buf[off + 4 + 5*k]
    val = load_u32(off + 5 + 5*k)
    if op == 0:
        # >>> THE PUSH GUARD. Present in EVERY rung. <<<
        if sp < STACK_CAP: stack[sp] = val ; sp += 1
    else:
        # >>> THE POP GUARD. R1 omits exactly this line and nothing else. <<<
        if sp > 0:
            sp -= 1
            acc = acc *64 31 +64 stack[sp]
return acc *64 31 +64 (sp as u64) *64 31 +64 nops
```

Load-bearing, do not "improve":

- **The push guard is in every rung, the pop guard is not.** Overflow is not the
  bug being modelled and letting R1 overflow too would confound them. Pin both in
  `idiom.required`, and say in `NOTES.md` that only one is the variable.
- **`sp` and `nops` are folded into the result**, so a rung that ends with a
  different stack depth or runs a different number of ops cannot produce the same
  checksum.
- **`stack` is a local fixed array, not a `Vec`.** A `Vec` moves the pattern to
  allocator behaviour, which is p02's axis and not this one.
- **Do not hoist the branch.** If a rung converts the per-op `if op == 0` into a
  branchless select, that is a *finding to report* — p07 measured LLVM's
  `X86CmovConverterPass` doing the opposite — not a licence to change the source.
- Wrapping arithmetic throughout.

### Contract

```
requires:  off + len <= buf_len
ensures:   result == stack_fold(buf, off, len)
```

## What to measure

1. **The safety cost of an emptiness check, and what it is a function of.** It is
   per *pop*, not per byte. Sweep the pop density (the fraction of ops that are
   POP) as well as `nops`, and report the law in whatever variable it is actually
   linear in. **Do not assume it is another per-byte constant.**
2. **Branch predictability, which p07 gave you the tools for.** The op stream is
   attacker-chosen, so you can generate a *predictable* stream (alternating,
   blocked) and an *unpredictable* one (random) **with the same op counts and the
   same checksum-relevant work**. That is a cleaner branch lever than p07's
   compiler flag, and this box has `callgrind --branch-sim=yes`
   (`.memory/00-environment.md`). Report `Bcm` per op for both.
3. **Whether the R5 proof needs an invariant nobody has written yet.** `sp` is
   bounded by both guards, so the obligation is `sp < STACK_CAP` on write and
   `sp > 0` on read, both maintained across an attacker-chosen branch. Budget one
   session; a documented failure with the exact Verus error **is** the deliverable
   for that row.
4. **The full `.memory/03-measurement.md` protocol before any `ns` claim** —
   `common/layout/order.py` for the identical-copy floor first, then
   `layout_gen.py` + `loopfit.py` if a mode shows.

## Inputs

| stem | shape | purpose |
|---|---|---|
| `small` | L1-resident, balanced push/pop | perf row |
| `large` | past L2, **different pop density** from `small` | perf row |
| `sweep-n*` | `nops` band | the swept laws |
| `sweep-d*` | **pop-density** band at fixed `nops` | item 1's second axis |
| `adversarial-underflow` | **one window**, POP as the first op | **the bug**: `sp − 1` at 0; ASan must fire on R1 |
| `adversarial-allpop` | every op a POP | the sustained-underflow case; R1 walks far |
| `adversarial-overflow` | more than `STACK_CAP` consecutive pushes | the guard that *is* in every rung — all rungs agree |
| `adversarial-count` | `5*nops` exceeding `avail` | the omitted length check |

Adversarial rows are **exactly one window** (`n_blob == stride`). **Window 0 must
serve something**, or `acc` pins at 0 and the driver's Lemire index has an
absorbing state. Name the sweep bands `sweep-*` and nothing else, appended
**last** to `gen.py`.

## Done when

The p11 checklist, unchanged, plus §"What to measure" 1–4: complete green
`check.py p03`; checksums against an independent `model.py`; the adversarial table
**per rung** with `adversarial-underflow` firing ASan on R1; the `idiom` block
written **before** the cells and its shared paragraph verified byte-identical
against p11's; a shipped sweep from day one; an in-contract **R3-side span** with
R4 held by fiat (**no pair interval**); two proof mutants failing the gate; the
TCB tally; the twin with its arithmetic written out; an `SLB-TRUSTED-ARGUMENT`
block.

**Run `./verus_run.py` on an R5 twin BEFORE differencing any unsafe-side
variant.** Read the error text, not the exit code.

## Constraints

No root; no `/tmp` (scratch `.temp/p03/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`; **do not touch `harness/` or `common/` — if p03 seems
to need a change there, stop and report it**. Do not edit any existing pattern's
sources. Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; confirm an exact PID's full command
line before any kill, **and no monitor wait-loops with self-matching `pgrep`
patterns**. **Measurements in the FOREGROUND, interleaved by cell.** Delete your
binaries and blobs once the gate is green.

Notes to `.temp/p03/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Forty-five
agents have contradicted the manager and all forty-five were right. Two things I
am least sure of:

- **whether `STACK_CAP = 64` and a 5-byte op are the right sizes.** The stack must
  fit in registers badly enough that the array is real, and the op stream must
  dominate the per-call constant. Check both before building five rungs, the way
  p11 checked its two premises on the disassembly first.
- **whether the underflow actually reads out of the allocation.** `stack` is a
  *local* array, so `stack[SIZE_MAX]` is a wild address rather than a heap
  overread — it may segfault rather than produce ASan's clean diagnostic, and it
  may be caught at compile time by a sufficiently smart optimiser. If R1's bug
  cannot be made to *execute*, that changes the pattern and I would rather hear it
  early. p08's whole result is that a bug which executes and is unobservable is
  still a finding.
