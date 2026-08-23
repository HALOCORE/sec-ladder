#!/usr/bin/env python3
"""Write ../spec.md: the prose contract and the fenced `slb-contract` block.

⚠ **THE SHARED NAMED-SPELLING PARAGRAPH IS READ OUT OF A DONOR PATTERN'S
`spec.md` AND NEVER EMBEDDED HERE** (`.memory/05-layout.md`). Embedding it is
the defect `patterns/p27-handle-table/controls/mkspec.py` shipped: a second copy
drifts, and `harness/check.py::named_spelling_problem` then fails one pattern
while the standard says every copy is byte-identical. This generator refuses to
write anything if the assembled contract does not satisfy `idiom_problems` and
`named_spelling_problem`.

⚠ **`spec.md` IS GENERATED, SO EDIT THIS FILE AND RE-RUN IT** -- three tasks in
a row shipped a `spec.md` edit a generator would have silently reverted, and one
of them was the task that fixed that defect (`.memory/05-layout.md`).

    python3 patterns/p36-vtable-dispatch/controls/mkcontract.py           # write
    python3 patterns/p36-vtable-dispatch/controls/mkcontract.py --check   # diff only
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
DONOR = os.path.join(REPO, "patterns", "p22-hash-probe", "spec.md")
OUT = os.path.join(PDIR, "spec.md")

sys.path.insert(0, os.path.join(REPO, "harness"))
import check as checkmod   # noqa: E402


def donor_paragraph(path=DONOR):
    """The shared named-spelling paragraph, out of a sibling's hashed block."""
    txt = open(path).read()
    m = re.search(r"```slb-contract\s*\n(.*?)```", txt, re.S)
    if not m:
        raise SystemExit(f"mkcontract.py: {path} has no slb-contract block")
    why = json.loads(m.group(1))["idiom"]["why"]
    i = why.find(checkmod.NAMED_SPELLING_BEGIN)
    j = why.find(checkmod.NAMED_SPELLING_END)
    if i < 0 or j < 0:
        raise SystemExit(f"mkcontract.py: donor {path} carries no shared "
                         f"paragraph -- pick another donor")
    return why[i:j + len(checkmod.NAMED_SPELLING_END)]


# ---------------------------------------------------------------- the why ----
WHY_HEAD = (
    "POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a "
    "published spread cannot carry a safety number, so what ships is a "
    "named-spelling standard -- the tokens above must appear literally, uniform "
    "across all eight rungs, with ONE measured clause: a rung spells the same "
    "operands the way its language forces. "
    "ON p36 THAT CLAUSE DOES REAL WORK FOR THE FIRST TIME, AND THE REASON IS "
    "THE PINNED VERUS. C dispatches through a bare function-pointer table -- "
    "`static uint64_t (*const TABLE[8])(uint64_t)`, the textbook bytecode "
    "interpreter -- and the four Rust rungs CANNOT: `const TABLE: [fn(u64) -> "
    "u64; N]` is `error: The verifier does not yet support the following Rust "
    "feature: function pointer types`, on the DECLARATION, at the pinned Verus "
    "0.2026.08.09.92f466f. The `identity` pin below makes an R4 a program that "
    "must have a verifying R5 twin, so a bare `fn`-pointer table is not an "
    "admissible rung at all. The Rust rungs therefore dispatch through "
    "`[&'static dyn Op; NOPS]` -- a single-trait object, which is a REAL vtable "
    "and a REAL computed-target indirect call, but two dependent loads where C "
    "has one. THAT DIFFERENCE IS MEASURED AND PUBLISHED, NOT WAVED AT: it is "
    "EXACTLY 3.00000 Ir PER DISPATCH -- the `fn`-pointer Rust control `r_fnptr` "
    "is `10.00000*nrw + 31` and the shipped `dyn` rung is `13.00000*nrw + 31`, "
    "same intercept, zero residual over twelve swept points and confirmed out "
    "of sample at nrw = 1024 (../NOTES.md 8a). 0a gives the probe "
    "matrix behind the claim (a `static` of `&dyn Op` fails twice over -- rustc "
    "wants `Sync`, and Verus then reports `dyn with more that one trait` -- so "
    "the Rust table is a `const` where C's is a `static`). "
    "WHY THE DISPATCH SPELLING IS PINNED ACROSS ALL FOUR RUST RUNGS: p36's cost "
    "column is about the INDIRECT CALL, and the safety column is about bounds "
    "checking. If R2 dispatched one way and R4 another, the R2-R4 difference "
    "would carry both and attribute neither. So `.apply(acc ^ arg)` and "
    "`[&'static dyn Op; NOPS]` are required of all four, and what is left free "
    "is how the WINDOW and the TABLE are ADDRESSED -- R2 indexes both, R3 "
    "hoists the record count and reslices the window once, R4 and R5 hoist the "
    "record count and use `get_unchecked` on both. That is the safety axis and "
    "it is the axis the R3-side span is measured along (../NOTES.md 8). "
    "\u26a0 **AND THE R4 SIDE WAS SEARCHED BEFORE ANY DIFFERENCE WAS "
    "PUBLISHED, WHICH CHANGED WHAT SHIPS.** The R2-shaped unsafe rung -- the "
    "one that keeps the per-record cursor test, i.e. what every other pattern "
    "in this tree ships as its R4 -- VERIFIES as an R5 twin (`12 verified, 0 "
    "errors`, no new trusted item) and is 1022 / 8190 Ir per call DEARER than "
    "the shipped R4. Shipping it would have made p36 publish *safe Rust beats "
    "unsafe Rust by 1007 / 8175 Ir per call*, all of it loop structure and "
    "none of it safety -- "
    "RECAP's *trap that keeps firing*, on its fifth pattern. So the shipped R4 "
    "is R3's loop structure with the checks removed, `R3 - R4` is a "
    "MATCHED-SPELLING difference of `+15.00 flat`, and both numbers plus the "
    "admissible R4-side span 1695...2717 / 13343...21533 are published "
    "(../NOTES.md 8b). "
    "WHY `match op { .. }` IS FORBIDDEN, AND IT IS THE MOST IMPORTANT ENTRY IN "
    "THE LIST: it is the IDIOMATIC safe-Rust spelling of this kernel and it is "
    "NOT A DISPATCH TABLE. Measured on the shipped op set at -O3 (../NOTES.md "
    "6b): the `match` lowers to `movslq (%r10,%r14,4),%r14 ; add %r10,%r14 ; "
    "jmp *%r14` -- a jump table with ALL EIGHT ARMS INLINED and no call at all. "
    "It is a different program with a different cost model, and shipping it as "
    "a rung would put a devirtualisation inside p36's safety column. It ships "
    "as the control `r_match` instead, measured -- and it is DEARER, which was "
    "not the expected direction: 2035.7726 / 15923 against the shipped R3's "
    "1710 / 13358. \u26a0 Its `Ir` is NOT AN INTEGER, and that is itself the "
    "finding: a jump table's arms have different lengths, so the executed "
    "instruction count becomes OPCODE-DEPENDENT where the table spelling's is "
    "exactly constant -- shipping it would have destroyed the `sweep-t*` "
    "control as well as the comparison (../NOTES.md 6b, 7). THE SAME GOES FOR "
    "`switch (op)` ON THE C SIDE, measured at 2411.5795 / 19099 against "
    "c-gcc-h's 1574 / 12326. "
    "WHY A MASK IS FORBIDDEN (`op & 7`, `op % 8`): masking the opcode into "
    "range is a THIRD program -- it makes every byte a legal opcode, so the "
    "out-of-table input stops being adversarial and the pattern's whole "
    "security half evaporates. It is also the fix a reader will reach for, "
    "which is exactly why it is named. "
    "WHY THE OP SET IS EIGHT ONE-OPERATION FUNCTIONS: the finding is the CALL, "
    "not the callee. An expensive callee would drown the dispatch cost in its "
    "own work. Measured rather than asserted -- all eight C ops are 0x12 = 18 "
    "bytes and all eight monomorphised Rust `apply`s are 0x0e = 14 bytes, from "
    "`nm --print-size` on the shipped -O3 binaries (../NOTES.md 6). That "
    "uniformity is also what makes the swept branch bands possible: `sweep-mix*` "
    "holds the OPCODE MULTISET fixed and varies only its ORDER, and `sweep-t*` "
    "varies the number of distinct TARGETS. Measured, `Ir` is identical to the "
    "instruction across both bands in ALL EIGHT CELLS while wall clock moves "
    "3.17x (Rust) and 3.16x (C) against a 4.19% noise floor -- p36's strongest "
    "half and the reason the op set may not be respelled (../NOTES.md 7). "
    "WHY THE HEADER IS DECODED WITH `+` AND `*` AND NEVER `|` AND `<<`: the two "
    "are the same function on unsigned values and lower to the same "
    "instructions, but only the first is linear arithmetic, so verus.rs carries "
    "no `by (bit_vector)` anywhere (`.memory/04-verus.md`). The same reason "
    "keeps every shift, mask and `%` out of the fold. "
    "WHY `#[verifier::external_body]` ON THE DISPATCH IS FORBIDDEN: hiding the "
    "table read behind a wrapper whose `ensures` is `r == op_spec(i, x)` also "
    "verifies -- it is the OTHER route past the function-pointer limitation, "
    "and it was probed and works (../NOTES.md 0a, probe a6) -- but it "
    "axiomatises all eight function bodies, i.e. it puts the thing the pattern "
    "measures inside the TCB. The shipped `tab_get_unchecked` claims only the "
    "SLOT'S IDENTITY (`r == TABLE@[i as int]`); what calling it does comes from "
    "`Op::apply`'s own VERIFIED `ensures`. The alternative is measured as the "
    "control in ../NOTES.md 8c, where its TCB cost is published beside the "
    "3.00000 Ir per dispatch the shipped design pays instead. "
)

CONTRACT_NOTE = (
    "requires/ensures above are DERIVED by check.py from verus.rs's own clause "
    "text through verus.translate, and the copy here must equal the derivation "
    "exactly. They are evaluated in Python against the bindings model.py yields "
    "per call (buf/off/len/buf_len/result) plus the helper it supplies "
    "(op_fold). p36's bindings are the READ-ONLY set p03, p06, p10, p11, p12, "
    "p14, p16, p17, p05, p07, p22, p27, p38 and p47 use: the kernel writes "
    "nothing at all. "
    "**THE `ensures` IS A FUNCTIONAL POSTCONDITION AND IT IS EXACTLY WHERE "
    "p36'S BUG LIVES -- unlike p22's.** `run` is an abstract machine over "
    "(t, p, acc) whose step function is `op_spec(op, acc ^ arg)` for `op < 8` "
    "and the sentinel fold otherwise, so a rung that dispatched to a DIFFERENT "
    "function, or dispatched at all on an out-of-table opcode, cannot produce "
    "the same checksum. c/kernel.c does not satisfy it: on every input carrying "
    "an opcode >= NOPS it loads a code pointer from past the end of TABLE and "
    "calls it. What makes that an obligation rather than a hope is "
    "`tab_get_unchecked`'s `requires i < NOPS`, which the verifier discharges "
    "at the one call site from the exec test `op < NOPS` -- delete that test "
    "and Verus reports `precondition not satisfied` before any postcondition is "
    "considered (../NOTES.md 10, mutant m1). "
    "⚠ **AND THE OBLIGATION IT DISCHARGES IS A BOUNDS OBLIGATION, WHICH IS THE "
    "UNFLATTERING HALF OF THIS PATTERN AND IS SAID HERE RATHER THAN BURIED.** "
    "p36's BUG CLASS is this tree's twelfth `index >= len`; what is new is the "
    "HARM (a control transfer, the only one here), the CHECKER SET's blindness "
    "to it (every diagnostic on this box names the array read, and the one "
    "checker that names a control transfer is not in gcc at all), the COST "
    "MECHANISM (0 of 534 built kernels in the other 21 patterns contains a "
    "computed-target call -- counted, ../NOTES.md 0d), and the fact that the "
    "pinned verifier cannot type C's declaration. None of those is the bug "
    "class. "
    "What the `ensures` deliberately does NOT say is that `nrec` is honest or "
    "that the opcode stream is well formed: a precondition about the contents "
    "of a file is one no honest loader can discharge "
    "(`.memory/02-bench-rules.md`), and it would delete every row this pattern "
    "exists for. degenerate.bin and all four adversarial rows are INSIDE the "
    "verified domain, and every rung except c/kernel.c agrees with model.py on "
    "all of them."
)

OBLIGATIONS_NOTE = (
    "12 = NOPS 1 + SENT 1 + TABLE 1 + OpTag::apply 1 + run 1 + kernel 2 + "
    "main 5, each term MEASURED with `./verus_run.py verus.rs "
    "--verify-function <name> --verify-root` and not predicted, and the terms "
    "SUM to the pinned total (p27's did not, in a spec.md the gate had passed "
    "nineteen times -- `.memory/04-verus.md`). The zero terms are checkable the "
    "same way: u32_at, nrec_at, op_spec and op_fold are NON-RECURSIVE spec fns "
    "and report 0, while run is RECURSIVE and carries one termination query; "
    "Op::apply and Op::spec_apply are TRAIT DECLARATIONS with no body and "
    "report 0, and OpTag::spec_apply is a non-recursive spec fn and reports 0; "
    "buf_get_unchecked, tab_get_unchecked, load_input and emit are "
    "external_body and report 0. THREE `const`s carry one query each "
    "(`.memory/04-verus.md`: a `const` inside verus! is its own obligation) -- "
    "NOPS, SENT and TABLE, and TABLE being one of them is worth noting because "
    "it is a `const` ARRAY OF TRAIT OBJECTS and nothing else in this tree has "
    "one. kernel's 2 = body + the one loop body. main's term is 5, which is "
    "what every other pattern in this tree that records the term also records "
    "for the byte-identical driver loop."
)

TWIN_NOTE = (
    "The obligation count in the OTHER configuration -- `verus.rs --cfg "
    "slb_twin`, which is where step 5c-twin checks the twins. 12 shipped + 2, "
    "the two trusted items inside the twin regime being "
    "slb_twin_buf_get_unchecked and slb_twin_tab_get_unchecked. `load_input` "
    "and `emit` are outside the regime (external_body with no `ensures` and no "
    "`unsafe` body) and have no twins."
)

COLLAPSE_NOTE = (
    "work_per_call is `stride` -- WINDOW BYTES, the denomination p16, p05, p11, "
    "p12, p06, p14, p27, p10, p38, p47 and p22 use. On small.bin and large.bin "
    "the window's declared `nrec` equals the number of records present, so the "
    "kernel reads the 4-byte header and all `stride - 4` record bytes, i.e. "
    "exactly `stride`, and the estimate is neither strict nor loose there. It "
    "OVER-counts only where a window declares fewer records than it carries, "
    "which degenerate.bin's fourth window does and which is not a "
    "collapse.probe_input. The two probe inputs differ in work_per_call (260 "
    "vs 2052) precisely so check.py's d(Ir)/d(work) assertion has two shapes "
    "and can run at all. model.py declares no min_ir_per_work, so the harness "
    "default of 0.25 applies unchanged; ../NOTES.md 3 has the per-cell margins."
)

IDENTITY_WHY = (
    "R4 == R5: the proof licenses unsafe code at zero cost. ⚠ **AND p36 IS THE "
    "FIRST PATTERN IN THIS TREE WHOSE O3 LEVEL IS `norel` RATHER THAN `exact`, "
    "WHICH IS A DISCLOSURE AND NOT A WEAKENING.** Measured: the two kernels are "
    "60 instructions and 193 bytes each, their normalised text is identical, "
    "`md5_fn_norel` is EQUAL, and EXACTLY ONE INSTRUCTION of the sixty differs "
    "-- `lea 0x3f6ad(%rip),%rsi` against `lea 0x3f7ed(%rip),%rsi`, the "
    "pc-relative address of TABLE. p36 is the first pattern here whose kernel "
    "REFERENCES A GLOBAL OBJECT at all, and the displacement to it depends on "
    "where the linker put a `const` in each binary, which is the "
    "source-path/crate-name layout artefact RECAP's settled answer 1 already "
    "names. `exact` is unavailable for a reason that has nothing to do with the "
    "proof, and `norel` is what says so precisely; every other pattern's O0 "
    "level is `norel` for the same class of reason. "
    "⚠ **A SECOND THING THIS PIN CAUGHT, AND IT IS A DURABLE VERUS FACT: A "
    "`spec fn` DECLARED IN A TRAIT OCCUPIES A VTABLE SLOT IN THE ERASED "
    "BUILD.** With `spec_apply` declared BEFORE `apply` in `trait Op`, R5's "
    "dispatch is `call *0x20(%rcx)` where R4's is `call *0x18(%rcx)` -- same "
    "instruction count, same byte count, same normalised text, and NOT equal "
    "even under `md5_fn_norel`. Declaring the exec method first is the whole "
    "fix and it is what this file's trait does; ../NOTES.md 5 has both "
    "listings. Ghost code still costs zero INSTRUCTIONS here, which is what "
    "`.memory/01-ladder.md` finding 1 actually claims -- but it is the first "
    "time in this project that a ghost declaration moved a byte of the object "
    "code, and the mechanism is trait-item ORDER."
)

MIRI_REASON = (
    "R4 and R5 are byte-identical under `md5_fn_norel` at O3 and their "
    "normalised text is identical, so Miri is checking the same program either "
    "way. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for "
    "any pattern with a trusted item, which check.py DERIVES from verus.rs "
    "rather than reading from this flag. **On p36 Miri is expected to be, and "
    "is, the only checker that sees the Rust-side analogue of the bug from "
    "inside the language**: `tab_get_unchecked` is `*TABLE.get_unchecked(i)`, "
    "and an unsafe rung with `op < NOPS` deleted reads a fat pointer out of "
    "bounds -- but note that rung is not shipped, because deleting the test "
    "also changes the ANSWER (the hardened semantics folds SENT). What IS "
    "shipped is measured: Miri on unsafe.rs over every non-hang input, "
    "including both out-of-table rows, on which the Rust rungs are perfectly "
    "well defined because they never dispatch. ../NOTES.md 2 has the wall "
    "times."
)

PROSE = """# p36 — function-pointer table dispatch: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

⚠ **This file is GENERATED by `controls/mkcontract.py`. Edit the generator and
re-run it** — three tasks in a row shipped a `spec.md` edit a generator would
have silently reverted (`.memory/05-layout.md`). The generator reads the shared
named-spelling paragraph out of a DONOR pattern's `spec.md` and refuses to write
anything if the result does not satisfy `harness/check.py::named_spelling_problem`.

## What p36 is, and what it is NOT

p36 is a one-byte bytecode interpreter. Each record is an (opcode, operand)
pair; the opcode indexes a table of eight callables and the interpreter
**calls** the entry it finds:

```c
acc = TABLE[op](acc ^ arg);          /* c/kernel.c — no `op < NOPS` */
```

⚠ **THE UNFLATTERING SENTENCE COMES FIRST. p36's BUG CLASS IS THIS TREE'S
TWELFTH `index >= len`.** p01, p02, p03, p05, p07, p11, p12, p13, p14, p16 and
p17 are all *"an index or a length is not checked against a buffer"*, and so is
this. Four things are new, and none of them is the bug class:

| | measured in |
|---|---|
| **the HARM is a control transfer**, not a value — the only one in this tree | `../NOTES.md` 0c |
| **no checker on this box can see that.** Every diagnostic names the *array read*; clang's `-fsanitize=function` names a control transfer and gcc 13.3.0 does not implement it, and even under clang it is defeated because the loaded garbage is not a function | `../NOTES.md` 0b |
| **the indirect call is a cost mechanism nothing here has had.** 0 computed-target `call` instructions in 534 built kernel symbols across the other 21 patterns, counted | `../NOTES.md` 0d |
| **the pinned Verus cannot type C's declaration.** `[fn(u64) -> u64; N]` is `does not yet support ... function pointer types`, so the Rust rungs use a trait object | `../NOTES.md` 0a, 8 |

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, carrying the same information: `&[u8]`
is a pointer and a length and C spells the pair out. C is handed the blob length
and *both* C rungs ignore it — p22's, p47's, p06's, p10's, p12's, p14's, p27's
and p38's shape. (The arity mismatch is why `spec.md` carries a
`driver.call_args` pin: no alias can turn a four-argument call into a
three-argument one.)

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..4     nrec   u32 LE    DECLARED record count           ATTACKER DATA
byte 4..      (opcode, operand) byte pairs                     ATTACKER DATA
data_start = 4
NOPS  = 8                     the table's extent
SENT  = 251                   what a rejected opcode folds
```

`NOPS` and `SENT` are compile-time constants in every rung. They are properties
of the *program* — a bytecode interpreter has a fixed number of opcodes — and
not of the input: `n_iters`, `stride`, `n_blob`, `nrec` and every opcode and
operand byte come from the file.

**248 of 256 byte values are out of table**, so the bug is one byte away from
every conforming input.

## Semantics

```
if len < 4:                                   return 0
nrec from the header
if nrec == 0:                                 return 0

acc = 0 ; p = 4 ; t = 0
for t in 0 .. nrec:
    if len - p < 2:   break                            # subtraction-first
    op = buf[off+p] ; arg = buf[off+p+1] ; p += 2
    # >>> THE SAFETY LINE. c/kernel.c omits exactly `op < NOPS`. <<<
    if op < NOPS:
        acc = TABLE[op](acc ^ arg)                     # THE DISPATCH
    else:
        acc = acc *64 31 +64 SENT
    t += 1

return acc *64 31 +64 t
```

`*64` and `+64` are wrapping `u64` operations.

⚠ **`safe_tuned.rs`, `unsafe.rs` and `verus.rs` HOIST the loop bound** to
`nw = min(nrec, (len - 4) / 2)` and drop the per-record `len - p < 2` test. It
is the same set of records — record `t` is read iff `t < nrec` and
`len - (4 + 2t) >= 2`, i.e. iff `t < min(nrec, (len - 4) / 2)` — and Verus
proves it: `verus.rs` verifies `12 verified, 0 errors` against the `run`
machine above, which is written with the per-record guard. Both C rungs and
`safe_naive.rs` write the guard. The `idiom` entry declines to pin either
spelling, because that is the safety axis.

**The eight ops, identical constant for constant in all eight rungs and in
`model.py`:**

```
op0(x) = x ^ 0x9e3779b97f4a7c15      op4(x) = x -64 0x61c8864680b583eb
op1(x) = x ^ 0xff51afd7ed558ccd      op5(x) = x -64 0xbf58476d1ce4e5b9
op2(x) = x +64 0x2545f4914f6cdd1d    op6(x) = x ^ 0x94d049bb133111eb
op3(x) = x +64 0xc4ceb9fe1a85ec53    op7(x) = x +64 0x9e6c63d0676a9a99
```

One 64-bit constant and one operation each, and that is load-bearing twice:
the finding is the **call**, not the callee, and equal-cost ops are what let the
`sweep-mix*` band hold the opcode multiset fixed while varying only its order.
Measured: all eight C ops are **18 bytes** and all eight monomorphised Rust
`apply`s are **14 bytes** (`nm --print-size`, shipped `-O3` binaries).

## The table, and the one place C and Rust differ

```c
static uint64_t (*const TABLE[SLB_P36_NOPS])(uint64_t) = { op0, ..., op7 };
```

```rust
const TABLE: [&'static dyn Op; NOPS] = [&OpTag::<0>, ..., &OpTag::<7>];
```

Both are runtime-indexed indirect calls. C's is one load and a `call
*(%r13,%rax,8)`; Rust's is an index scale, a vtable load and a `call
*0x18(%rcx)`. **The difference is forced, not chosen** — see `idiom.why` — and
it is measured rather than waved at.

⚠ **Eight `impl Op for OpN` blocks were written first and VERIFIED (19/0). The
GATE refuses them**: `harness/vparse.py::duplicate_names` fails any pinned file
that defines a name more than once, and eight impls define `apply` eight times.
The const-generic `OpTag<K>` shape is what makes p36 expressible inside the
existing gate with **no `harness/` change**; `OpTag<0>` .. `OpTag<7>` are eight
distinct types with eight distinct vtables and eight distinct code addresses.

## The adversarial rows

| input | shape | R1's behaviour |
|---|---|---|
| `adversarial-oob` | one opcode byte set to 8, the NEAREST out-of-table value | **SIGSEGV on 8 of 8 plain cells**; under ASan+UBSan the diagnostic names the *array read* |
| `adversarial-oobmax` | one opcode byte set to 255, 1976 bytes past the table | SIGSEGV on 8 of 8 plain cells; a separate row because the two do **not** behave alike under the sanitizer build |
| `adversarial-nrecbig` | `nrec` saturated at `0xFFFFFFFF`; only the cursor guard stops the walk | terminates, agrees |
| `adversarial-stride5` | a 5-byte window | none: the driver guard `stride_w >= 6` skips the loop and every rung prints 0 |

⚠ **What "adversarial behaviour per rung" means when the harm is a segfault in
one build and a wrong answer in another.** Stage 4 records the exit status and
signal per cell and computes `diverges` against the model's CONFORMING answer,
so the eight R1 cells read `diverges=True` and the twenty-four others read
`diverges=False`. Stage 7 is a *different* build (gcc -O1 `-fsanitize=...`), and
there the redzones move what is adjacent to `TABLE`: on `adversarial-oobmax` the
sanitized binary returns a wrong answer and exits 0 while still reporting. That
is why `sanitizer_expect` is **"fires"** — *a sanitizer reports, deterministically*
— and never *"the harm is identical"*.

## Contract

"""


def contract():
    return {
        "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
        "model": "model.py",
        "requires": ["off + len <= buf_len"],
        "ensures": ["result == op_fold(buf, off, len)"],
        "note": CONTRACT_NOTE,
        "idiom": {
            "required": [
                {
                    "c": "THE SAFETY LINE, and the only thing c/kernel.c omits: "
                         "`op < SLB_P36_NOPS` in c/kernel_hardened.c. c/kernel.c "
                         "dispatches unconditionally and is otherwise "
                         "character-identical, so the scoped-absent audit pair this "
                         "entry reports is on that rung and is correct.",
                    "rust": "THE SAFETY LINE, present in ALL FOUR Rust rungs and "
                            "written by hand in every one of them: `op < NOPS`. It is "
                            "not a bounds check in any Rust rung -- it is the "
                            "kernel's SEMANTICS, because the hardened C cell folds "
                            "SENT on an out-of-table opcode -- which is why deleting "
                            "it from a Rust rung would change the answer and not "
                            "merely the safety.",
                },
                {
                    "c": "THE DISPATCH, in both C rungs, and the reason p36 exists: "
                         "`TABLE[op](acc ^ (uint64_t)arg)`.",
                    "rust": "THE DISPATCH, in all four Rust rungs: "
                            "`.apply(acc ^ arg)`. What precedes it is the SAFETY AXIS "
                            "and is deliberately NOT pinned -- R2 and R3 index the "
                            "table, R4 and R5 read it through the unchecked accessor "
                            "-- so this entry backticks only the part all four share, "
                            "and neither of those two spellings appears in backticks "
                            "anywhere in this declaration, because a backtick in a "
                            "required entry PINS a spelling and these two are the "
                            "axis this entry exists to leave free. (That sentence "
                            "is written without backticks around the word required "
                            "for exactly the reason it states: the gate audited the "
                            "backticked version as a spelling, and reported it "
                            "pinning nothing across all four Rust rungs.)",
                },
                {
                    "c": "THE TABLE IS A RUNTIME-INDEXED ARRAY OF CODE POINTERS, in "
                         "both C rungs: `(*const TABLE[SLB_P36_NOPS])(uint64_t)`.",
                    "rust": "THE TABLE IS A RUNTIME-INDEXED ARRAY OF TRAIT OBJECTS, "
                            "in all four Rust rungs: `[&'static dyn Op; NOPS]`. It is "
                            "a `const` and not a `static`, and it is a trait object "
                            "and not a function pointer, for the two reasons the why "
                            "key gives -- both of them measured Verus errors.",
                },
                {
                    "c": "the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and "
                         "the additive form's overflow never arises: `len - p < 2` in "
                         "both C rungs.",
                    "rust": "the walk stops at the window in all four Rust rungs. "
                            "safe_naive.rs writes the same subtraction-first guard as "
                            "C; safe_tuned.rs, unsafe.rs and verus.rs reach the same "
                            "set of records by hoisting the minimum of the "
                            "declared count and the room the window leaves out of the "
                            "loop, which is the R3-side lever and is exactly what this "
                            "entry declines to pin. Prose throughout, therefore, and "
                            "not a backtick -- an earlier draft backticked the hoisted "
                            "expression and the gate's audit correctly reported it as "
                            "pinning nothing, because no rung spells it that way.",
                },
                {
                    "c": "a rejected opcode folds the SENTINEL rather than being "
                         "skipped, so the fold's length is a function of the record "
                         "count alone: `acc * 31 + SLB_P36_SENT;` in "
                         "c/kernel_hardened.c. c/kernel.c has no such arm at all, "
                         "which is the same scoped absence as the safety line.",
                    "rust": "the sentinel fold, in all four Rust rungs: "
                            "`.wrapping_add(SENT)`.",
                },
                {
                    "c": "the fold is a serial Horner chain over `acc`, spelled with "
                         "the literal multiplier: `acc * 31` in both C rungs.",
                    "rust": "the fold, in all four Rust rungs, spelled with the "
                            "literal multiplier: `.wrapping_mul(31)`.",
                },
                {
                    "c": "the header is decoded with + and * and never with | and <<, "
                         "so the whole specification stays inside linear arithmetic "
                         "(.memory/04-verus.md): `256 *` in both C rungs.",
                    "rust": "the same decode in all four Rust rungs: `256 *`.",
                },
                "THE OP SET is eight one-operation functions and is identical "
                "constant for constant in all eight rungs; the first constant, "
                "`0x9e3779b97f4a7c15`, appears in every one of them. The finding "
                "is the CALL and not the callee, so no op may be dear enough to "
                "drown the dispatch -- measured at 18 bytes (C) and 14 bytes "
                "(Rust) per op.",
                "the declared record count is rejected before any record is read, "
                "so no rung can walk a header it has not validated: `nrec == 0` "
                "appears in all eight rungs.",
                "the number of records walked is folded LAST, so a rung that "
                "dispatched a different number of times cannot produce the same "
                "checksum: `t` appears in the return expression of all eight rungs.",
            ],
            "forbidden": [
                {"rust": "`match op {`"},
                {"rust": "`fn(u64) -> u64`"},
                {"rust": "`op & 7`"},
                {"rust": "`op % 8`"},
                {"c": "`switch (op)`"},
                {"c": "`op & 7`"},
                {"c": "`op % 8`"},
                "`black_box`",
                "`volatile`",
            ],
            "why": WHY_HEAD + donor_paragraph(),
        },
        "verus": {
            "call_site": "main",
            "kernel_item": "kernel",
            "translate": {
                "buf@.len()": "buf_len",
                "buf@": "buf",
                " as int": "",
                "r": "result",
            },
            "obligations": {"verus.rs": 12},
            "twin_obligations": {"verus.rs": 14},
            "obligations_note": OBLIGATIONS_NOTE,
            "twin_obligations_note": TWIN_NOTE,
            "unsafe_justifications": {},
            "items": {
                "verus.rs": {
                    "apply": {"external": None, "requires": [], "ensures": []},
                    "spec_apply": {"external": None, "requires": [], "ensures": []},
                    "u32_at": {"external": None, "requires": [], "ensures": []},
                    "nrec_at": {"external": None, "requires": [], "ensures": []},
                    "op_spec": {"external": None, "requires": [], "ensures": []},
                    "run": {"external": None, "requires": [], "ensures": []},
                    "op_fold": {"external": None, "requires": [], "ensures": []},
                    "buf_get_unchecked": {
                        "external": "verifier::external_body",
                        "requires": ["i < v@.len()"],
                        "ensures": ["r == v@[i as int]"],
                    },
                    "slb_twin_buf_get_unchecked": {
                        "external": None,
                        "requires": ["i < v@.len()"],
                        "ensures": ["r == v@[i as int]"],
                    },
                    "tab_get_unchecked": {
                        "external": "verifier::external_body",
                        "requires": ["i < NOPS"],
                        "ensures": ["r == TABLE@[i as int]"],
                    },
                    "slb_twin_tab_get_unchecked": {
                        "external": None,
                        "requires": ["i < NOPS"],
                        "ensures": ["r == TABLE@[i as int]"],
                    },
                    "load_input": {"external": "verifier::external_body",
                                   "requires": [], "ensures": []},
                    "emit": {"external": "verifier::external_body",
                             "requires": [], "ensures": []},
                    "kernel": {
                        "external": None,
                        "requires": ["off + len <= buf@.len()"],
                        "ensures": ["r == op_fold(buf@, off as int, len as int)"],
                    },
                    "main": {"external": None, "requires": [], "ensures": []},
                }
            },
        },
        "driver": {
            "statements": 12,
            "c_source": "c/main.c",
            "regions": [
                "safe_naive.rs",
                "safe_tuned.rs",
                "unsafe.rs",
                "verus.rs",
                "c/main.c",
            ],
            "aliases": {
                "c": {
                    "n_body": "bytes.len()",
                    "bytes": "bytes.as_slice()",
                    "inp.n_iters": "n_iters",
                }
            },
            "call_args": {"c": {"kernel": [0, 2, 3]}},
            "canonical": [
                "n_blob = bytes . len ( ) ;",
                "buf = bytes . as_slice ( ) ;",
                "acc = 0 ;",
                "if stride_w >= 6 && stride_w <= n_blob",
                "{",
                "stride = stride_w ;",
                "nwin = n_blob / stride ;",
                "it = 0 ;",
                "while it < n_iters",
                "{",
                "k = acc * nwin >> 64 ;",
                "r = kernel ( buf , k * stride , stride ) ;",
                "acc = acc * 31 + r ;",
                "it = it + 1 ;",
                "}",
                "}",
            ],
        },
        "collapse": {
            "probe_inputs": ["small.bin", "large.bin"],
            "probe_iters": [100, 200],
            "note": COLLAPSE_NOTE,
        },
        "identity": [
            {
                "a": "unsafe",
                "b": "verus",
                "O0": "norel",
                "O3": "norel",
                "why": IDENTITY_WHY,
            }
        ],
        "miri": {
            "pair": ["unsafe", "verus"],
            "sources": ["unsafe.rs"],
            "required": True,
            "reason": MIRI_REASON,
            "blocked_reason": "miri is installed on the nightly toolchain beside "
                              "the pinned one (TOOLCHAIN.md). If it is missing, "
                              "this row is blocked rather than failed.",
        },
    }


def render(c):
    return PROSE + "```slb-contract\n" + json.dumps(c, indent=2) + "\n```\n"


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="do not write; report whether spec.md matches")
    a = ap.parse_args()
    c = contract()

    # Fail closed: the generator refuses to write a contract the gate would
    # reject for a reason it can see itself.
    probs = checkmod.idiom_problems(c) or []
    nsp = checkmod.named_spelling_problem(c)
    if nsp:
        probs.append(nsp)
    if probs:
        for p in probs:
            print("REFUSING:", p, file=sys.stderr)
        return 1

    txt = render(c)
    para = donor_paragraph()
    print(f"shared named-spelling paragraph: {len(para)} chars, read from "
          f"{os.path.relpath(DONOR, REPO)}")
    if a.check:
        cur = open(OUT).read() if os.path.exists(OUT) else ""
        if cur == txt:
            print("spec.md matches the generator")
            return 0
        print("spec.md DIFFERS from the generator", file=sys.stderr)
        return 1
    with open(OUT, "w") as f:
        f.write(txt)
    print(f"wrote {os.path.relpath(OUT, REPO)} ({len(txt)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
