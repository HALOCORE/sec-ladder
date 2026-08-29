# TASK_134 — four non-spatial candidates, probed before any row is written

**Role: research engineer. No pattern was built and no `patterns/pNN-*/`
directory was created.** All work is under `.temp/t134/`; measurements,
commands and full logs are in `.temp/t134/NOTES.md`, which this report
summarises rather than repeats.

---

## ⚠⚠ THE HEADLINE

> **None of the four candidates survives. The non-spatial candidates are
> exhausted, and I did not find a survivor to recommend.**

I am reporting that plainly because the task asked for it plainly. Three of the
four die on measurements, not on judgement; the fourth (`p35`) dies on a
structural gate property I confirmed by running Verus six times.

⚠ **But the task is not empty, and the most valuable thing in it is not a
verdict on a row.** It is that **`.memory/01-ladder.md`'s OPEN scope note now
has a two-directional answer** (§C below), and that answer is what kills the
"safe Rust cannot EXPRESS the bug" pitch shared by candidates 1, 2 and 3.

---

## A. Candidate 1 — `p25`, `realloc` growth. REFUSE.

**Expressible: yes.** `.temp/t134/p25/p25_probe.c` runs the pinned signature
with the vector inside the kernel and a `PUSH`/`MARK`/`READ` opcode stream out
of the blob — `p27`'s construction exactly. Nothing engages `dloop.py:361`.

**The addressing mode, settled first, by a run** (`#![forbid(unsafe_code)]`,
rustc 1.97.1). Three different answers, as the task predicted:

```
&u8 held across push      error[E0502]      r2_ref.rs
as_ptr() + deref          error[E0133]      r2_asptr.rs
index                     COMPILES          r2_idx.rs   -- and has NO BUG AT ALL
```

The index port is not "the bug in `p04`'s class"; `realloc` **copies**, so `v[k]`
is simply correct afterwards. So `p25` is a row only if pointer-addressed.

**⚠⚠ Then the kill, and it is a measurement I did not expect: in `p25`'s
shipped heap topology `realloc` never moves.** The driver `malloc`s the blob
first, so the kernel's vector is the newest allocation and glibc extends it in
place. `.temp/t134/p25/realloc_move.c`, doubling from cap 4:

```
A  vector alone at the top of the heap    gcc moved=0/12   clang moved=0/12
B  a pin malloc'd after it                gcc moved=2/12   clang moved=0/12   <- compiler-dependent
C  two vectors grown alternately          moved=9/12 and 10/12, both
D  alone, past the 128 KiB mmap threshold moved=8/20, both
```

Regime A is the shipped shape, and there `k_ptr`'s answer **equals** `k_idx`'s
exactly (`10649415700415720425`), in 6 of 6 compiler × `-O` cells, stable across
two full re-runs. ASan fires only because **ASan's allocator moves on every
`realloc`** (`moved=4` where the shipped build reports `moved=0`).

> So in the shipped link mode **the UB executes and is unobservable** — which is
> `p08`'s published sentence verbatim, and `p08` is built.

Three further findings, each independently sufficient:

- **There is no safety conjunct to omit.** C cannot ask "did my block move"
  without comparing the base pointer, and a rung that saves `(base, k)` and
  re-derives on mismatch *is* the index port. My epoch-checking "hardened" rung
  is over-conservative and diverges from the correct answer even at `moved=0`.
  `p27`'s shape (*"R1 omits exactly `&& live[h] == 1`"*) has **no analogue
  here**; the safety line is an addressing mode, not a check.
- **The gradient prices register allocation.** callgrind, 3000 reads:
  `k_ptr 359 682 Ir` / `k_idx 362 734 Ir` = **`+1.00 Ir` per read, one
  instruction** (122 → 123 in the symbol). The delta reproduced **exactly**
  (`+3052`) across two runs while the absolute level moved by 34.
- **R1 has no stable checksum to publish.** On a moving topology the stale read
  returns freed-chunk contents: same binary, same input, `bug=3196606969367904911`
  then `bug=4868875711876342483`. The hardened rung is stable; the buggy one is
  not.

**The growth-overflow half is spatial and is `p05`/`p17`'s class** — measured,
not asserted: `heap-buffer-overflow`, `WRITE of size 1`. Refused on sight.

**Limb:** would have to be limb 4, and it lands on `p08`'s existing result.
**Duplication:** `p27` (same ASan class, `heap-use-after-free`), `p08` (the
unobservable-UB result), `p04` (the recycle variant), `p05`/`p17` (the overflow
half). I concede all four; I could not find the escape.

## B. Candidate 2 — stack lifetime. REFUSE, and it is weaker, so I killed it.

Expressible inside one kernel call (`.temp/t134/stack/stack_probe.c` runs). But:

1. **Both compilers refuse it at DEFAULT flags, no `-Wall` needed** —
   `-Wreturn-local-addr` (gcc), `-Wreturn-stack-address` (clang). The ladder's
   premise is that C is *silently* wrong. Here C is not silent.
2. **The bug is not adversarial-only — it fires on `benign.bin` too.** A pointer
   to a dead frame is dead unconditionally. This is exactly the constraint that
   made `p27` retract its original shape.
3. **The gate's gcc-only ASan is blind to the escape form:** `k_escape` under
   gcc ASan is **0 hits**, even with `--param asan-use-after-return=1`; gcc's own
   positive control degrades to `SEGV on unknown address 0x0` rather than
   `stack-use-after-return`. Only clang sees it, and stage 7 is gcc.

The task asked me to say so and kill it if it is weaker. It is weaker. Killed.

## C. Candidate 3 — iterator invalidation. REFUSE as a row; ⚠ **but this is where the value is.**

**The C rung's bug is one of exactly three things, and the detector says which**
(`.temp/t134/iter/iter_probe.c`, both positive controls firing first):

```
ptr    heap-use-after-free      pointer cursor + realloc  -> candidate 1
bound  heap-buffer-overflow     hoisted length + shrink   -> SPATIAL, refused on sight
list   heap-use-after-free      free(node); node->next    -> p27, built
```

That is the honest answer to the task's question. There is no fourth spelling.

### ⚠⚠ The law's OPEN scope note, answered in both directions

`.memory/01-ladder.md` records as OPEN: *"The BORROW CHECKER is a SECOND
temporal mechanism … this law does not contain it. Nobody has tested it."*

**Direction 1 — it rejects programs that cannot have the bug.** Seven controls,
all `#![forbid(unsafe_code)]`, all reproducing the safe rungs' diagnostics:

| control | contains | diagnostic |
|---|---|---|
| `ctl1_nostruct` | `struct S{v:u32}` — no heap, no container | **E0502**, message identical to `p25`'s safe rung |
| `ctl2_array` | `[u8;16]` on the stack — nothing can move | E0506 |
| `ctl3_vec_nomove` | `v[1]=7`, provably no reallocation | **E0502** |
| `ctl4_reserved` | `push` with capacity 64 reserved, len 1 | **E0502** |
| `ctl_iter_nomut` | iterate a stack array | E0506 |
| `ctl_iter_reserved` | iterate a `Vec` with 1024 reserved | **E0502** |
| `ctl_stack_nostruct` / `ctl_stack_return` | **one integer local** | E0597 / E0515 |

**Direction 2 — it accepts a real temporal bug in the same data structure.**
`iter/rs/accept_recycle.rs`, `forbid(unsafe_code)`, **0 `unsafe {` blocks**:
`pop` ends the element's lifetime, `push` recycles the slot, the read gets the
new occupant — `v[2] = 9999` where 30 was marked, `buffer moved: false`, and
**Miri reports 0 UB**.

> **The borrow checker is NOT a temporal mechanism. It is an ALIASING mechanism,
> and it is neither sound nor complete for the temporal property.**

**Two consequences I would ask the manager to weigh:**

- **The law is not incomplete in the way the note supposes.** The borrow checker
  is a fifth mechanism but not a temporal one, so the four runtime outcomes
  stand. And **outcome 3 (*"the type system is SILENT"*) extends verbatim from
  pointer-backed structures to flat growable buffers** — the scope note's own
  first exclusion, and `p25`'s data structure.
- **It retires "safe Rust cannot EXPRESS the bug" as a distinguishing claim for
  all three of candidates 1, 2 and 3.** This is the **third** instance of the
  failure mode `.memory/01-ladder.md`'s method rule was written for
  (`TASK_093`'s `E0382`, `TASK_094`'s `E0502`, now these). The rule is what
  caught it, and it cost about ten minutes.

## D. Candidate 4 — `p35`. STAYS BLOCKED, ⚠ but two record corrections.

Six Verus runs, single-file, never `--cargo`:

```
a_verified.rs      unsafe{v.i} in a VERIFIED fn, requires v is i    3 verified, 0 errors
b_no_requires.rs   requires deleted                     MUST-FAIL:  1 verified, 1 errors
c_extbody.rs       unsafe{v.i} in #[verifier::external_body]        2 verified, 0 errors
d_extbody_mustfail caller not establishing the tag      MUST-FAIL:  precondition not satisfied
e_ensures.rs       + full functional ensures                        2 verified, 0 errors
f_twin.rs          the twin, with `unsafe` removed                  error[E0133]
```

**Correction 1 — `.memory/06-catalogue.md:414`'s *"no configuration in which its
safety obligation is CHECKED"* is too strong for the `external_body` route.**
Verus **does** check the correct-variant obligation at the call site, and the
wrapper **can** carry a full functional `ensures`. The spelling is
`get_union_field::<U, u32>(v, "i")` — which the compiler itself names in the
error for `v.i`. ⚠ Per `CLAUDE.md` I grepped `~/tools/verus/vstd/std_specs/`
specifically: `union` has no entry there because union support is a **language
builtin** (`~/tools/verus/builtin/src/lib.rs:296-298`), not a vstd spec. Probe
4's grep misses it for that reason, not because it is absent.

**Correction 2 — the `include!` escape route is CLOSED at HEAD and the catalogue
still advertises it.** The cell says *"a GATE-CLEAN `p35` DOES EXIST … `include!`
is a macro … so the walk never sees the file"*. `harness/check.py:3941` now reads
`cand += _include_literals(txt)[0]`, so `_path_includes` **does** resolve
`include!`, and `_scan_unsafe_sites`' second loop (4201-4212) fails any `unsafe`
in an include target with **no exemption branch at all**.

**What actually blocks it is one thing, and it is structural.**
`_scan_unsafe_sites` has exactly one allowed branch (`check.py:4178-4180`): the
`unsafe` must sit inside an `#[verifier::external_body]` body. That makes it a
trusted item, which **owes a twin** — and the twin must be a **safe spelling of
the same operation**. `p01`'s twin for `get_unchecked` is literally `v[i]`
(`patterns/p01-array-sum/verus.rs:84-90`). **Rust has a safe spelling for
indexing and none for a union read**, so `f_twin.rs` is `error[E0133]`.

The remaining hatch, `verus.twin_justifications`, appears in **0 of 26 shipped
`spec.md` contracts**; its only occurrence under `patterns/` is
`p17-http-range/NOTES.md:1050-1058` **rejecting** an axiom for this very reason
(*"no twin possible … it would then have had to be excused through
`verus.twin_justifications` … It was rejected"*). `p35` would be asking for the
same hatch, for the same reason, on the item the row exists to check.

**So: no, there is no unblocked spelling.** The row dies for a stated reason, and
the reason is now sharper than the one on file — *the twin mechanism cannot check
an axiom for an operation with no safe spelling* — which is a clean
instrument-boundary finding.

---

## Ranking, and the recommendation

**No survivor. I recommend building none of the four.** Ranked by how close they
came:

1. **`p25`** — the front-runner, and the only one that was close. It fails on the
   shipped-topology `moved=0` measurement plus the absence of any safety
   conjunct. If the manager wants to overturn this, the single thing to attack is
   my claim that `TOPO=0` is the shipped topology.
2. **`p35`** — blocked, correctly, but its record needs the two corrections above.
3. **Candidate 3** — no independent bug exists; it resolves to 1, to spatial, or
   to `p27`. Its *by-product* is the most valuable result in the task.
4. **Candidate 2** — weakest; killed on three independent grounds.

## What I did NOT do, and what I am unsure about

- **I did not run `harness/check.py` or `harness/measure.py`** (forbidden — a
  concurrent agent). So **no claim here is gate-certified**, and my `p35`
  conclusion rests on reading `check.py`'s predicates plus running Verus, not on
  executing the gate against a synthetic pdir the way `TASK_096`/`097` did.
  ⚠ **That is the weakest link in this report** and the twin/`n_twins`
  interaction in particular deserves an executed check before the correction is
  landed in `.memory/`.
- **I did not write anything to `.memory/`, `RECAP.md` or `results/SYNTHESIS.md`.**
  The two `p35` corrections in §D are proposals for the manager.
- **`TOPO=0` is my inference about the shipped heap topology**, argued from the
  driver `malloc`ing the blob before the kernel runs. I verified the *allocator*
  behaviour by measurement, but I did not build a real pattern driver to confirm
  the ordering, because building a pattern was forbidden.
- **I did not attempt a Verus R5 for `p25`.** Given the row fails on the C side
  first, it seemed the wrong place to spend the budget. If `p25` is revived, an
  R5 attack arm that must fail to verify is still owed
  (`.memory/02-bench-rules.md`).
- I did not explore whether a *deliberately two-vector* kernel (`TOPO=2`) could
  be argued as idiomatic. It reliably moves, so it is the one way `p25` could be
  revived — but it is a kernel designed to produce its own bug, and I judged that
  contrived rather than measuring it further.

## Files

`.temp/t134/NOTES.md` (all measurements and commands) · `p25/` `stack/` `iter/`
`p35/` (sources, controls, logs) · runners `p25/run.sh`, `p25/rs/run.sh`,
`stack/run.sh`, `stack/rs/run.sh`, `iter/run.sh`, `iter/rs/run.sh`,
`p35/run.sh`, and `p25/gen.py`. All were re-run end to end after cleanup.
Binaries and `.bin` blobs deleted (25 M → 388 K); every one is regenerated by a
script in the tree.

---

**Running count.** I was launched carrying **634**. My branch delta is **+4**:
the four manager premises this task's own measurements moved —
(i) *"safe Rust's `Vec` makes a stale `&T` across a `push` a compile error, so
the safe rung may be unable to EXPRESS the bug"* is true but **not
distinguishing**, refuted by seven controls; (ii) *"a stale INDEX is not a stale
POINTER — if the port uses indices the bug vanishes into `p04`'s class"* — the
index port has **no bug at all**, not a `p04`-class one; (iii) the catalogue's
*"`p35` has no configuration in which its safety obligation is CHECKED"* is too
strong for the `external_body` route (measured `precondition not satisfied`);
(iv) the catalogue's *"a GATE-CLEAN `p35` DOES EXIST"* via `include!` is stale —
that route is closed at HEAD. **Sum: 638.** ⚠ A concurrent branch also carries
634; **reconciliation is the manager's job, not mine**, and this figure must not
be added to the other branch's.
