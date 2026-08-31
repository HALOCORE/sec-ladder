# p25 — a dynamic array grown with `realloc`, and an interior pointer held across the growth

The kernel parses an op stream into two growable byte vectors. It saves an
**interior pointer** into the token vector, `cur = &toks[curi]`, keeps parsing,
and a later push grows the token vector with `realloc`. When the block relocates
the old one is retired — **the program never calls `free` on it, `realloc` does**
— and the next `READ` dereferences a pointer into storage the allocator has taken
back. `c/kernel.c` omits the conjunct `curbase == toks` that would ask.

⚠⚠⚠ **This row was REFUSED at `TASK_134` and every limb of that refusal was
driver-artefact or ladder-side.** *"In p25's shipped heap topology `realloc`
never moves"* — a fact about **that driver**. *"There is no safety conjunct to
omit"* — refuted by the shipped `c/kernel_hardened.c`. *"Safe Rust makes the bug
a compile error"* — a **finding**, and a weak one, because the error code is not
distinguishing. It was re-admitted at `TASK_143` on the C-side bar
(`CLAUDE.md` rule 6) and built at `TASK_157`.

| | |
|---|---|
| **Bug** | CWE-416 use-after-free reached through CWE-825 expired-pointer dereference. The retirement is `realloc`'s, not a `free` the program calls, and the stale reference is an **interior** pointer into the middle of a container. |
| **Safety line** | the conjunct `} else if (curbase == toks) {` on the READ path, with a **re-derive** `v = (uint64_t)toks[curi];` in the `else` it guards. `controls/safety_line.py` measures it on the two shipped files at **`+3 / −1` preprocessed lines, net `+2`** — not a pure addition, because the read *moves* into the guarded branch — and checks that the include-twice body in `controls/arm_body.inc` reproduces both files exactly. |
| **Rungs** | R1 `c/kernel.c` · R1h `c/kernel_hardened.c` · R2 `safe_naive.rs` · R3 `safe_tuned.rs` · R4 `unsafe.rs` · R5 `verus.rs` |
| **R5** | `10 verified, 0 errors` (twin config `12 / 0`), TCB **4 `external_body` items**, of which **2 are inside the twin regime** — both twinned, `blocked` is `[]`. **Three fewer trusted items than p27's and p34's seven**, because this rung allocates through `Vec` and vstd owns the allocation. |
| **Headline 1** | ⚠⚠ **The hardened cell's `else` branch RE-DERIVES, and that is forced.** The obvious `else { v = SENT; }` would make the kernel's **answer a function of the allocator**, so `model.py` could not derive the checksum and the Rust rungs — whose `Vec` grows on a different schedule — could not agree with the C ones. Re-deriving is allocator-independent because **`realloc` copies**. So **the conjunct buys memory safety and buys nothing else**: both branches compute the same value. |
| **Headline 2** | ⚠⚠ **The conjunct is NOT the standard-clean repair, and the standard-clean one is CHEAPER.** DR 400 makes `cur` indeterminate after *any* `realloc`, moved or not. The unconditional re-derive is the only C rung DR 400 cannot reach — and `controls/rederive.py` prices it at **roughly half** the shipped conjunct's cost, on both compilers at both optimisation levels. **On the C side this row has no trade-off: the safer repair dominates.** |
| **Headline 3** | ⚠⚠ **The ladder DELETES the bug above R1 rather than making it provable.** Safe Rust cannot hold `&toks[curi]` across a `push`, so the port saves an index — and then it has **no bug at all**, because `realloc` copies. At R4/R5 the pointer *could* be held (`controls/arm_unsafe_ptr.rs` does, and Miri reports it) but must not be: Verus cannot license `*cur`, because address equality does not imply provenance equality. **p25's R5 obligation is SMALLER than p27's, p29's, p32's or p34's, and saying so is the result.** |

## The C-mechanism distinction, stated first because a reviewer will attack it first

```
p27  individually malloc'd records; an explicit free(); the READ does not ask.
p29  an explicit free() of a whole record and a stale ADDRESS held across it.
p32  nothing is allocated at all; a handle is not revalidated.
p34  an explicit free() a refcount selected; the read path is correct.
p25  NO free() ANYWHERE EXCEPT THE EPILOGUE.  `realloc` retires the block as a
     SIDE EFFECT OF GROWTH, and what is stale is an INTERIOR pointer.
```

✅ **Measured, not asserted** (`controls/no_reloc.py`, re-derived every run, with
comments and string literals blanked first): `realloc` is called by **exactly one
pattern's `c/` and it is this one — 1 of 32** — and only **5 of 32** call
`malloc` at all. ⚠ `free` is called by **32 of 32**, because every `c/main.c`
frees the driver payload, so *"calls `free`"* is not a distinguishing token and
the distinction is stated about the **kernel**.

## The harm window is ONE GROWTH wide

`controls/reloc_probe.py` compiles the **shipped** kernel and the **shipped**
driver unmodified, interposes on `realloc` by a command-line `-D`, and counts:

```
adversarial-move      realloc sizes [4, 4, 8, 16, 32]        MOVED only at 32
adversarial-many      realloc sizes [4, 4, 8, 16, 32, 64, 8] MOVED only at 32
adversarial-nogrow    realloc sizes [4, 4, 8]                MOVED nowhere
small                 realloc sizes [4, 4, 8, 8]             MOVED nowhere
gcc and clang identical on all four.
```

glibc's minimum chunk gives a 4-byte `malloc` 24 usable bytes, so `4 → 8` and
`8 → 16` are satisfied in place; it is `16 → 32` that has to move, and only
because the string vector was allocated after the token vector and is still live.
**The adversarial windows are TUNED to that growth.** ⚠ Even `32 → 64` does not
move — by then the token block is at the top of the heap with room — so
*"`realloc` moves"* is not a general property of this kernel, and `inputs/gen.py`
carried the opposite prediction until this control refuted it.

## ⚠ ASan is a BIASED instrument here, and the row does not rest on it

ASan's allocator moves on **every** `realloc`, so its column would fire even
under a topology in which glibc never relocated. The **unbiased** evidence is the
plain-build divergence between R1 and R1h. Both are in `NOTES.md` 2, separately.
It is also why `model.py` derives `sanitizer_expect` from *"the token vector was
reallocated while a saved pointer was live"* — that is ASan's condition, it is
what makes the column checkable against an ASan build, and it is the conservative
direction, because every read it calls stale is a read C already calls undefined.

`controls/detectors.py` ships **one positive control per detector** and runs
**both** C arms under both, because a UBSan build that says nothing looks exactly
like one that was never linked in — the gap `.temp/mgr155/NOTES.md` §3 found in
this row's own pre-build demonstration.

## Safe Rust: what is established, and what `E0502` does not say

`controls/safe_arms.py`, four arms:

| arm | what | result |
|---|---|---|
| A `arm_safe_ptr.rs` | `&toks[curi]` held across `toks.push(a)` | **does not compile**, `E0502` |
| B `arm_safe_ptr_nopush.rs` | A with the ONE push replaced by the SENT fold | **compiles** — so the diagnostic is attributable to the two edited lines |
| C `arm_safe_negctl.rs` | **NEGATIVE CONTROL**: no container, no growth, no saved reference — 12 lines with a struct and a `&mut` | **does not compile, same `E0502`** |
| D `arm_safe_index.rs` | the index port | **compiles**, and agrees with `model.py::parse_fold` on all four adversarial windows |

⚠⚠ **Arm C is the finding.** `E0502` carries **no information** about interior
pointers or about `realloc` — **the fourth time this project has read a rustc
code as distinguishing when it was not** (p25's own, p28's `E0382`/`E0499`,
p34's `E0507`). What p25's safe rungs actually establish is stronger and
different: **the port that DOES compile has no bug**, so safe Rust's answer here
is `c/kernel_hardened.c`'s at zero cost.

## Reproducing

```sh
python3 patterns/p25-realloc-growth/inputs/gen.py     # the .bin files are gitignored
harness/build.py p25
harness/measure.py p25
harness/report.py p25
harness/check.py p25
python3 patterns/p25-realloc-growth/controls/safety_line.py
python3 patterns/p25-realloc-growth/controls/no_stale.py
python3 patterns/p25-realloc-growth/controls/no_reloc.py
python3 patterns/p25-realloc-growth/controls/reloc_probe.py
python3 patterns/p25-realloc-growth/controls/detectors.py
python3 patterns/p25-realloc-growth/controls/safe_arms.py
python3 patterns/p25-realloc-growth/controls/rederive.py
python3 patterns/p25-realloc-growth/controls/rust_bug.py
python3 patterns/p25-realloc-growth/controls/proof_mutants.py
```

`spec.md` carries the machine-readable contract and the reasoning; `NOTES.md`
carries every number and what it does and does not support; `c/kernel.h` carries
the kernel contract in pseudocode.
