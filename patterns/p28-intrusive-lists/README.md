# p28 — intrusive doubly linked lists, two link sets, incomplete destroy

**The bug in one sentence.** A bounded object cache puts every object on TWO
intrusive lists — a doubly linked eviction list and a doubly linked hash chain —
and its TRIM path, which reaches its victim through the *eviction* list, frees the
object without leaving the *chain*.

```c
struct p28_obj { struct p28_obj *lp, *ln;   /* the eviction list  */
                 struct p28_obj *hn, *hp;   /* the hash chain     */
                 uint8_t key, val; };
```

`c/kernel.c` is the bug and `c/kernel_hardened.c` is the same file plus nine
preprocessed lines — the chain splice — and nothing else
(`controls/safety_line.py` measures the `+9 / −0`).

## Why it is a row, and not one of the three temporal rows already here

|  | where the stale reference lives | what forgets |
|---|---|---|
| `p27` | a HANDLE in a stack table, and the input supplies the slot number | the READ path |
| `p29` | an ADDRESS in a stack local | the READ path |
| `p32` | a handle into a pool that is never allocated and never freed | the READ path |
| **`p28`** | **a POINTER INSIDE ANOTHER HEAP OBJECT** (`hn`), or in `bucket[]` | **the DESTROY path** |

Two things follow, and both are checkable rather than adjectival.

* **The read path is correct.** Nothing in PUT, GET or DEL is missing a test:
  they walk a chain and use the object they reach, which is what a hash chain is
  for. There is no guard to add there. That inverts all three built temporal rows.
* **There is nothing the input can index.** The input names an object only by
  KEY and the program finds it by walking, so neither C rung contains a slot
  number, a liveness bit or a generation. `p27`'s `h < ntab && live[h] == 1` has
  **no analogue, because there is no `h`**.

`controls/harm_sites.py` ships one adversarial window for each of the two sites
and reports which is which, with ASan firing on the buggy arm at both and a
positive control firing on both compilers.

## What the row measured, in four lines

1. **R1 reads freed heap and its checksum is STABLE** — 1 distinct value in 20
   runs, in all four (compiler × opt) cells, on every adversarial input, against
   a negative control that gives 20/20. The links come first in the struct, so
   glibc's tcache clobbers `lp` and `ln` and leaves what the stale walk reads.
   p28 is the first temporal row whose adversarial evidence carries a *figure*.
   ⚠ It does **not** make the row gatable against `model.py`; nothing is
   (`NOTES.md` 2c).
2. **Safe Rust cannot reproduce the bug at all.** It cannot express an object on
   two intrusive lists, so every Rust rung stores slot numbers instead of
   pointers — and with the safety line deleted the safe rung either gives the
   CORRECT answer or panics, never a silently wrong one and never UB
   (`NOTES.md` 4b). That is the *opposite* of `p32`, whose safe rung reproduces
   its buggy C bit for bit.
3. **The R5 proof does not force the safety line; the SPECIFICATION does.**
   Delete the splice from the exec code → fail. From the abstract machine only →
   fail. From **both** → verifies. p28 has the linear resources `p32` lacked —
   a real `PointsTo` and a real `Dealloc`, consumed by a real `free` — and they
   still do not reach a destroy-path omission, because the linear argument only
   ever bites at a READ (`NOTES.md` 6).
4. **And the proof does not force the epilogue either.** Kill it and everything
   leaks; the proof verifies. `Tracked<Dealloc>` is affine, so dropping a token is
   legal — `.memory/04-verus.md`'s `p42` result, reproduced on a fourth pattern
   (`NOTES.md` 6a).

## Layout

```
c/kernel.h              the contract, in pseudocode, with the LAYOUT NOTE
c/kernel.c              R1  -- TRIM frees without leaving the chain. THE BUG.
c/kernel_hardened.c     R1h -- the same file plus the nine-line splice
c/main.c                the driver; the marked region is the shared loop
safe_naive.rs           R2  -- `Option<Box<Obj>>` over a slot table, u8 links
safe_tuned.rs           R3  -- the same, indexed once per object per step
unsafe.rs               R4  -- raw pointers per object, slot-number links
verus.rs                R5  -- R4's exec code with the proof
model.py                the reference: a dict cache with NO LINKS, plus the
                        Verus machine, plus the released-object detector
inputs/gen.py           the generator; the blobs are gitignored
spec.md                 the reasoning and the machine-readable pins
NOTES.md                what was measured, including three retracted predictions
controls/               safety_line, harm_sites, repro, proof_mutants, rust_arms
```

## Reproducing

```sh
python3 patterns/p28-intrusive-lists/inputs/gen.py
harness/check.py p28
python3 patterns/p28-intrusive-lists/controls/safety_line.py
python3 patterns/p28-intrusive-lists/controls/harm_sites.py
python3 patterns/p28-intrusive-lists/controls/repro.py
python3 patterns/p28-intrusive-lists/controls/rust_arms.py
python3 patterns/p28-intrusive-lists/controls/proof_mutants.py     # SLOW: ~40 min
```

⚠ Hand-run sanitisers need `env -u LD_PRELOAD` on this box or ASan does not
start and says nothing while exiting 1 (`.memory/00-environment.md`). Every
control here does it for you.

⚠ `proof_mutants.py` is the slow one and most of its time is ONE arm:
`A3-spec-only-weaken` fails for a real reason (`assertion failed`) **and** then
exhausts the solver budget, so it burns the whole `--rlimit 400`. The other six
arms are a minute or two each.
