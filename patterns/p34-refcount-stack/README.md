# p34 — manual reference counting over a stack of heap objects

Every object carries its own count in its own first word. `NEW` allocates one
with `rc = 1` and pushes it; **`DUP` publishes a SECOND reference to the object
on top of the stack**; `POP` releases one reference and frees at zero; the
epilogue releases whatever the window left behind. `c/kernel.c` omits the `rc++`
that `DUP` owes.

⚠⚠⚠ **This row was REFUSED TWICE and both refusals were LADDER-SIDE.**
*"There is no working leak detector for the C rungs on this box"* — dead, and
never the binding constraint. *"The safe rung leaks only in the `Rc`-both-ways
spelling"* — about a **different bug class**, the `Rc` cycle leak, which
`.memory/01-ladder.md` scopes to the statically-asymmetric doubly-linked-list
case. **`p34` as built is the PREMATURE-FREE class only**, and it was admitted at
`TASK_143` on the C-side bar (`CLAUDE.md` rule 6). Nothing the Rust or Verus
rungs do can shrink it.

| | |
|---|---|
| **Bug** | CWE-911 improper reference count update reaching CWE-416 use-after-free. The acquire path publishes a reference and does not count it, so a later release frees an object a live stack entry still names. |
| **Safety line** | `t->rc = t->rc + 1;` on the `DUP` path — **`+1 / −0` preprocessed lines, the smallest in this tree.** `controls/safety_line.py` measures it on the shipped files AND checks that the include-twice body in `controls/arm_body.inc` reproduces both of them exactly. |
| **Rungs** | R1 `c/kernel.c` · R1h `c/kernel_hardened.c` · R2 `safe_naive.rs` · R3 `safe_tuned.rs` · R4 `unsafe.rs` · R5 `verus.rs` |
| **R5** | `24 verified, 0 errors` (twin config `29 / 0`), TCB **7 `external_body` items**, of which **5 are inside the twin regime** (`_is_trusted`: `external_body` + an `ensures`, or `unsafe` in the body) — **all 5 twinned, `blocked` is `[]`**. The other two, `load_input` and `emit`, carry no `ensures` and no `unsafe`, so they are outside the regime and owe no twin. Full functional refinement plus the temporal invariant `perms[k].value().rc == cnt(ids, k)`. |
| **Headline 1** | **The benign cost gradient across the safety line is `0.00` BY CONSTRUCTION, and it is proved rather than searched** — and then measured anyway: `+0.00` Ir/call on all sixteen cells. |
| **Headline 2** | **Two bug classes separated by WHICH INSTRUMENT SEES THEM.** On two of the four adversarial inputs the two rungs' checksums are **bit-identical** and ASan is the only discriminator. |
| **Headline 3** | **BOTH branches of `.memory/01-ladder.md`'s temporal law, in ONE row, selected by the PORT.** The `Rc` port cannot express the bug at all; a safe index-arena port reproduces `c/kernel.c` **bit for bit**. |

## The distinction, stated first because a reviewer will attack it first

```
p27  the free discipline is correct; the READ does not ask.          Fix the READ.
p29  the free discipline is correct; the READ does not revalidate.   Fix the READ.
p32  nothing is allocated; the handle is not revalidated.            Fix the READ.
p34  THE READ IS CORRECT AND ASKS NOTHING WRONG.                     Fix the ACQUIRE.
```

A refcounted pointer is valid **by construction**, so no test the read path could
grow would repair this program without becoming a liveness table. **The free
happens EARLY rather than the read happening LATE** — a different C program with
a different repair site, and the harm lands an unbounded distance from the
omission.

## Headline 1 — `0.00`, proved, then measured

`t->rc = t->rc + 1` is the **only increment in the kernel**, so in R1 every
object's `rc` is permanently `1`. Any executed `DUP` therefore leaves **two stack
entries naming a one-reference object**, and the two releases that must follow go
`1 → 0` (*free*) and then `0 → underflow`, reading `o->rc` out of a freed block.
**There is no input on which the safety line executes and R1 stays memory-safe.**

So no measured input may contain a `DUP`, and that is checked in three
independent places rather than assumed: `inputs/gen.py` cannot emit one and
re-checks the bytes it wrote, `model.py::no_dup_problems` re-derives it from the
shipped blob on every gate invocation, and `controls/no_dup.py` censuses the
directory — **0 executed DUPs on every matrix input, 48 across the adversarial
ones.**

⚠ **And `0.00` is a PREDICTION until it is measured**, because R1h is a different
compiled function. Measured: **`R1h − R1 = +0.00` Ir/call on all sixteen cells**
(2 inputs × 2 opt levels × 2 inline modes × 2 compilers), while the **static**
instruction count moves by **+1 at `-O3` and +5 at `-O0`** on both compilers.
`NOTES.md` 4.

## Headline 2 — two bug classes, and the checksum sees only one

| input | what R1 touches | checksum vs R1h | ASan | UBSan |
|---|---|---|---|---|
| `adversarial-blind` | `o->rc` of a freed block (release path) | **identical** | fires | silent |
| `adversarial-blindread` | `o->data[0]` of a freed block | **identical** | fires | silent |
| `adversarial-recycle` | `o->data[0]` of a **recycled** block | diverges | fires | silent |
| `adversarial-many` | all three, 36 times | diverges | fires | silent |

**Measured on all twelve build lines** — plain/ASan/UBSan × gcc/clang × `-O0`/`-O3`
(`controls/detectors.py`) — with **one positive control per detector**, because a
detector that says nothing looks exactly like a detector that is not running.
The refcount header comes first and `data` starts at offset 16, clear of glibc's
tcache `next`/`key` words, so the stale read returns the *right* byte. **Layout
disclosed**, the way `p28` discloses its own.

## Headline 3 — both branches of the temporal law, in one row

`controls/safe_arms.py`, one pattern, the PORT as the only variable:

| port | the bug | evidence |
|---|---|---|
| **`Rc`** (the shipped R2/R3) | **not expressible** | `arm_safe_rc_move.rs` → `error[E0507]`, `arm_safe_rc_borrow.rs` → `error[E0502]`; `safe_naive.rs` compiles on the same command line |
| **index arena** (`arm_safe_arena.rs`, `#![forbid(unsafe_code)]`) | **reproduces `c/kernel.c` BIT FOR BIT on all 8 inputs**, the recycle-divergent one included | and with `--cfg slb_arm_retain` it equals `model.py` on all 8 |

`.memory/01-ladder.md`'s law is *safe Rust's temporal guarantee is a guarantee
about the ALLOCATOR; a structure that recycles its own storage gets no guarantee
at all.* `p28` is one branch and `p32` is the other; **`p34` has both, and the
selector is the port rather than the pattern.** Miri is silent on the arena arm
on every input — it is `forbid(unsafe_code)` and nothing is allocated in the
kernel — which is the `p32` half of the coverage result.

## The R5, and the obligation that is new to this tree

A `PointsTo` is **linear** and p34's subject is **aliasing**, so the permission
cannot be held per stack entry the way `p27` holds one per slot. It is keyed by
OBJECT, and the proof carries the bridge:

> **`perms[k].value().rc == cnt(ids, k)`** — the count in the object's own first
> word equals the NUMBER OF STACK ENTRIES naming it.

`cnt` is an occurrence count over a `Seq<int>` with five supporting lemmas: the
first multiset-flavoured obligation in this project. **Leak-freedom falls out as
a corollary** — `obj_ok` requires `cnt(ids, k) > 0` for every key and the
epilogue empties the stack, so the permission map is empty when the kernel
returns.

`controls/proof_mutants.py`, six arms, all as expected:

| arm | expect | got | where it fails |
|---|---|---|---|
| `M0-control` | verify | `24 / 0` | — |
| `M1-delete-retain` (**the attack**) | fail | `23 / 1` | `assertion failed` — the loop invariant |
| `M2-constant-body` (vacuity) | fail | `21 / 1` | `postcondition not satisfied` |
| `X1-delete-rc-conjunct` | fail | `22 / 2` | **`precondition not satisfied`** |
| `X2-exec-and-spec` | fail | `22 / 2` | **`precondition not satisfied`** |
| `M3-delete-epilogue` | fail | `23 / 1` | `assertion failed` — leak-freedom |

⚠⚠ **`X2` is the arm to read.** It weakens the exec code AND the invariant so
they agree again — the arm `p32` publishes as **VERIFYING**, because p32
allocates nothing and its safety line is load-bearing against the specification
alone. **On `p34` it FAILS, on a memory-safety precondition.** That is the
sharpest difference between the two rows' R5 results.

## What the pinned vstd does not have, reported as a result

`~/tools/verus/vstd/std_specs/smart_ptrs.rs` is **78 lines** with no
`strong_count`, no `Rc::clone`, no `into_raw`/`from_raw` and no
`increment_strong_count`, so an R5 must model the counter itself in a raw-pointer
rung — which is what the C rung does anyway. ⚠ And the layout fact the rung needs
is a **`global layout` directive, not an axiom**: `size_of` is uninterpreted for
a user struct at the pinned vstd, and `global layout Obj is size == 24,
align == 8;` is **checked by rustc at codegen** (measured: a wrong value verifies
and then fails to compile). `NOTES.md` 6 and 6a.

## Cost

⚠ **The rung-to-rung axis is published as a TABLE with a two-sided spelling
search beside it** (`controls/spellings.py`), never as a bare point — six
patterns in this project have published a rung-to-rung headline wrong in the
flattering direction. `NOTES.md` 5 gives both optimisation levels, names the
weaker-searched endpoint, and records the one comparison that **REVERSES between
optimisation levels**. The `0.00` safety-line figure above needs no such search:
nothing can move a statement about a statement that does not run.

## Reproducing

```sh
python3 patterns/p34-refcount-stack/inputs/gen.py     # the .bin files are gitignored
harness/build.py p34
harness/measure.py p34        # BEFORE report.py
harness/report.py p34
harness/check.py p34
python3 patterns/p34-refcount-stack/controls/safety_line.py
python3 patterns/p34-refcount-stack/controls/no_dup.py
python3 patterns/p34-refcount-stack/controls/detectors.py
python3 patterns/p34-refcount-stack/controls/safe_arms.py
python3 patterns/p34-refcount-stack/controls/rust_bug.py
python3 patterns/p34-refcount-stack/controls/spellings.py
python3 patterns/p34-refcount-stack/controls/proof_mutants.py
```
