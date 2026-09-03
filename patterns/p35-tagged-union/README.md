# p35 — tagged union / discriminated dispatch

**The TYPE axis, second row.** CWE-843, access of a resource using an
incompatible type. `results/tables/p35-tagged-union.md` has the numbers;
`NOTES.md` has the findings; `spec.md` has the contract the gate enforces.

## The program, in one paragraph

A cell is a **tag** plus a **union** — `uint8_t tag` beside
`union { uint64_t i; double d; uint8_t *p; }`. An op stream from the file
writes cells at three types and reads them back through the tag. Storing a
pointer or a double takes a byte out of a budget of four, so **the store has a
failure path** — and `c/kernel.c` publishes the tag *before* the payload lands.
When the budget is exhausted the cell claims to hold a pointer (or a double)
while the union still holds the integer a previous `SET_INT` put there, and the
dispatcher reads it **at the claimed type**.

## The safety line

`c/kernel_hardened.c` moves **two statements** — `cells[idx].tag = P35_T_PTR;`
and `cells[idx].tag = P35_T_DBL;` — from before the `if (navail > 0)` to inside
it, after the payload store. Nothing is added, nothing is deleted, no test is
introduced. `controls/safety_line.py` preprocesses both shipped files and
measures it: **same line multiset, `+2 / −2`, a pure reorder at both sites**,
with a must-fire arm that shows the positional half of the check catching a swap
the line-count half is blind to.

⚠ **A sequencing constraint is a third SHAPE of safety line for this tree.**
`p27`'s is a conjunct; `p13`'s is a store; `p35`'s is an order.

## Two harms, one ordering, chosen by the input

| input | what R1 does | what any detector says |
|---|---|---|
| `adversarial-ptr-confusion`, `-ptr-deep` | dereferences an attacker-derived integer | **SIGSEGV**; ASan reports it (gcc and clang) |
| `adversarial-dbl-confusion`, `-exhaust` | compares a garbage double | **nothing at all** |

`controls/detectors.py` runs both shipped kernels under five build lines and
ships **one positive control per detector** — `ctl_asan.c` and `ctl_ubsan.c` —
because a control that fires only in ASan cannot license a UBSan column. The
ASan control's *failure* to fire under UBSan is recorded as a measured row: it
is the evidence for the rule.

## What each rung does with it

* **R2/R3 (safe Rust)** hold a `Cell` **enum**. The mismatch is
  **unrepresentable**: the discriminant and the payload are one value written by
  one assignment, so those rungs have no site for a safety line at all. The
  boundary is compile time — `p08`'s shape.
* **R4 (unsafe Rust)** holds C's shape, a tag array beside a `[Pay; 8]` of
  unions, so the ordering constraint is back and is written by hand.
* **R5 (Verus)** proves it, as the loop invariant `wf_cells`.

⚠⚠ **Verus supports the Rust `union` natively** — a wrong-variant read is
`error: requirement not met: to access this field, the union must be in the
correct variant`. It is a **language builtin, not a vstd spec**, so a
`std_specs/` grep misses it. `controls/union_oracle.py` measures both
configurations of the read, each with a must-fail arm, and shows that the one
the gate **refuses** is the stronger one. `NOTES.md` 6 is the finding.

⚠⚠⚠ **AND THE SHARP FORM OF IT.** Delete the correct-variant `requires` from
the three trusted readers and the shipped proof **still verifies at its pinned
obligation count** (`controls/proof_mutants.py` arm `X1`); the refused
configuration **fails at the read** on the same deletion (`union_oracle.py` arm
`B2`). **So the gate does not merely force the weaker of two available proofs —
it forces the one whose central obligation can be deleted without the gate
noticing**, and the stage that would have judged clause strength, `5c-twin`, is
one of this row's three blocked rows. `NOTES.md` 6b.

## Can Rust reproduce the bug?

`controls/rust_bug.py`, three cells:

* **unsafe Rust with a real union** reproduces the SILENT harm **bit for bit**,
  and **Miri says nothing** — a wrong-variant union read is not undefined
  behaviour in Rust when the bytes are a valid value of the field's type **and
  were all written**. ⚠⚠ **That last clause was added at `TASK_153` and it is
  load-bearing**: `Pay` has a 4-byte `o: u32` in an 8-byte union, so the
  *widening* confusion `adversarial-exhaust.bin` reaches reads uninitialised
  memory and **Miri DOES report it**. That confusion exists only in the Rust
  rungs — C's three members are all 8 bytes — so it is another consequence of
  the offset-for-pointer substitution below. `NOTES.md` 7;
* **safe Rust with `f64::from_bits`** reproduces it too, under
  `#![forbid(unsafe_code)]`. That is why `from_bits`/`to_bits` are forbidden in
  a *rung*;
* the shipped safe rungs' `enum` cannot express it at all.

Neither Rust arm reproduces the loud harm's **class**, and the reason is the one
asymmetry this pattern discloses: the Rust union carries the arena **offset**
where C's carries a **pointer**, so what follows a confused read is an
out-of-bounds index rather than a wild dereference. ⚠ **Both still crash** — the
unsafe arm dies on a SIGNAL and the safe arm panics at `rc=101` — so what the
substitution changes is **which instrument reports it**: Miri reports the
out-of-bounds index and says nothing about the union read.

⚠⚠ **AND THE UNSAFE ARM'S SIGNAL IS A DRAW, NOT A CONSTANT** (TASK_170; the
sentence here used to read *"SIGSEGVs at `rc=-11` exactly as C does"*).
Measured over **40 runs per input** by `controls/rust_bug.py`, which now
asserts it:

| input | C R1 | unsafe arm |
|---|---|---|
| `adversarial-ptr-confusion` | **40/40 SIGSEGV** | 33 SIGSEGV (`-11`) / 7 SIGBUS (`-7`) |
| `adversarial-ptr-deep` | **40/40 SIGSEGV** | 38 SIGSEGV / 2 SIGBUS |

**The stochasticity is a consequence of the same substitution, not noise**:
C's wild pointer is an attacker-derived *integer* and lands in the same place
every run, while the Rust arm's is an arena-relative *offset* whose faulting
address moves with ASLR. So `unsafe_reproduces_c` is `false` on any draw that
comes up SIGBUS, and that is **not** a defect — what is invariant is that the
arm dies loudly, and that is what is asserted.

## Reproducing

```sh
python3 patterns/p35-tagged-union/inputs/gen.py     # the .bin files are gitignored
harness/build.py p35
harness/measure.py p35        # ⚠ BEFORE report.py: report.py loads results/p35-*.json first
harness/report.py p35
harness/check.py p35
harness/report.py p35 && harness/check.py p35   # ⚠ stage 9c's one-run lag, on a NEW pattern only
python3 patterns/p35-tagged-union/controls/safety_line.py            # and --selftest
python3 patterns/p35-tagged-union/controls/detectors.py
python3 patterns/p35-tagged-union/controls/union_oracle.py
python3 patterns/p35-tagged-union/controls/proof_mutants.py
python3 patterns/p35-tagged-union/controls/rust_bug.py
```
