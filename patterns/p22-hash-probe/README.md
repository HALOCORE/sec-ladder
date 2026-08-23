# p22 — open-addressing hash probe

**The first pattern here whose bug is not a memory-safety bug — and the first
where safe Rust does not help.**

`spec.md` is the contract. `NOTES.md` has every measurement. This file is the
summary.

> ⚠ **The gate verdict for p22 is `PASS-WITH-BLOCKED-ROWS`, not `PASS`.** One
> input is declared non-terminating, and a declared-hang input is a blocked Miri
> row by construction. p01 is the only other pattern in the tree that lands
> there. Nothing is broken; see `NOTES.md` §11.

## What it is

A fixed-capacity open-addressed hash table with linear probing. Each window
declares `nkey` keys; each key is one byte; the kernel inserts or finds each key
and folds the slot it lands in.

```c
if (k != SLB_P22_EMPTY)                                      /* R1  — the bug */
if (k != SLB_P22_EMPTY && nfill < SLB_P22_TABCAP)            /* R1h — the fix */
{
    i = (size_t)k * 2654435761u / 16777216u % SLB_P22_TABCAP;
    while (tab[i] != SLB_P22_EMPTY && tab[i] != k)      /* THE PROBE LOOP */
        i = (i + 1) % SLB_P22_TABCAP;
    if (tab[i] == SLB_P22_EMPTY) { tab[i] = k; nfill++; }
    acc = acc * 31 + (uint64_t)i;
}
```

The probe loop is **unbounded in every rung, including the hardened one**. It
terminates because some slot is EMPTY, and `nfill < TABCAP` is the statement that
one is. Take the conjunct away and a key absent from a full table walks the ring
for ever: a denial of service with no memory error anywhere in it.

## What is different about it

| | every other pattern | p22 |
|---|---|---|
| what `c/kernel.c` omits | a bounds check | a **capacity** check |
| the harm | out-of-bounds read/write, UAF, UB | **the function never returns** |
| undefined behaviour? | yes | **no.** Every access is `tab[i % 64]` |
| ASan + UBSan | 15 of the 20 patterns before p22 declare at least one `"fires"` row | **silent** on every row — measured |
| Miri on the Rust port of the bug | reports UB | **silent** — measured, it just spins |
| safe Rust | prevents it by construction | **does not.** The safe port hangs |
| what R5 adds | a spatial or temporal obligation | **a TERMINATION obligation** — see the retraction below |

⚠ **"the first termination obligation in this project" was FALSE and is
retracted** (TASK_070_REVIEW F1, the manager's premise from `TASK_070.md`,
shipped in eight places and two of them inside `spec.md`'s hashed contract).
Verus demands a `decreases` on **every** exec loop by default, so every R5 here
has discharged termination obligations since p01 — **73 exec-loop measures
across 21 `verus.rs` files**, 70 of them in the other twenty patterns and 72 of
them not p22's probe loop. What is p22's own is counted, not argued:

> **Of those 73, p22's probe loop carries the only measure that is not
> expressible in the loop's own exec variables.** The rest are `B − c` for a
> loop-invariant bound and a monotone exec cursor, or a bare monotone exec
> variable. p22's is `i0 as int + d - u` — a ghost cursor and a ghost witness,
> with the loop's own control variable `i` nowhere in it, because `i` wraps.

`NOTES.md` §0e-i has the census.

## The measured core, in one table

`adversarial-full.bin` — 64 distinct keys fill the table, then a 65th that is
absent. `timeout` in seconds; every other input agrees across all eight rungs.

| build | `small.bin` | `adversarial-nearfull.bin` (63 keys) | `adversarial-full.bin` (64 + 1) |
|---|---|---|---|
| `c-gcc`, `c-clang` (R1) — O0 and O3 | agrees | agrees | **does not terminate** |
| `c-gcc-h`, `c-clang-h` (R1h) | agrees | agrees | agrees |
| `safe_naive`, `safe_tuned`, `unsafe`, `verus` | agrees | agrees | agrees |
| **`r2_noguard`** — R2 minus the conjunct, O0 and O3 | agrees | agrees | **does not terminate** |
| **`r3_noguard`**, **`r4_noguard`** — likewise | agrees | agrees | **does not terminate** |
| `c_asan` — gcc `-O1 -fsanitize=address,undefined` | clean | clean | **spins, stderr empty** |
| Miri on `r2_noguard` | — | no UB | **spins, no diagnostic** |
| Verus on `verus.rs` minus the conjunct | — | — | **3 errors** (`--multiple-errors 20`; the default reported 2) |

The `*_noguard` rows are one exact-string substitution away from the shipped
rungs (`controls/gen_controls.py --run hang --miri`, which asserts the
substitution hit exactly once).

## Why R2–R5 carry the fix rather than the bug

`.memory/06-catalogue.md` predicted *"R2, R3 and R4 all hang"*. That is **true of
a mechanical port and false of the shipped ladder**, and the reframing is a
deliverable of the task that built p22 (`NOTES.md` §0d):

* `.memory/01-ladder.md` puts the bug in **R1 only** — "written the way a
  competent systems programmer writes it, *including* the bug class the pattern
  is about". Every other pattern in the tree follows it.
* A hanging R3 beside a terminating R4 would make the rungs semantically unequal
  (the reviewer checklist's own blocker) and would force `identity: differ`,
  breaking an 18-of-18 invariant and with it ladder finding 1.

So the "safe Rust does not help" half is carried by **controls that are measured
and shipped**, not by a hanging rung. It is a stronger claim that way, because
`r2_noguard`, `r3_noguard` and `r4_noguard` are all measured and all hang: the
result does not depend on which safe spelling you pick.

⚠ **And the counterweight is stated rather than buried.** A bounded trip count
(`for _ in 0..TABCAP`) also terminates and is idiomatic safe Rust. It is out of
contract — but for **two different reasons**, and the single reason p22 shipped
first was false of half of what it excluded (TASK_070_REVIEW F3):

* the bound written **instead of** the conjunct (`r3_bounded`) is a *different
  function* — it disagrees with the shipped R3 on `adversarial-full.bin`;
* the bound written **in addition to** the conjunct (`r3_bounded_kept`) is the
  *same function*, agreeing on all eight matrix inputs. It is excluded by
  `spec.md`'s probe-loop `required` entry (`required[2]`), *no trip count anywhere* — the same ground
  that forbids `probes < TABCAP` in R4/R5, because a bound in the object code is
  the fix wearing the proof's clothes.

⚠ **What that second exclusion costs is published, not hidden.** The in-contract
R3 span is width **10.00**; with `r3_bounded_kept` admitted it would be
**167.65 / 1235.96 — 16.8× wider**. The direction does **not** flatter:
`r3_bounded_kept` is *dearer*, so `R3ship` is still the cheapest in-contract R3
found and `R3 − R4 = +2.00` does not move. `NOTES.md` §0c and §8b.

So what p22 publishes is *what the proof buys over the bound*, not a claim that
no safe programmer would write the bound.

## The cost column, and the caveat that comes with it

Kernel-exclusive `Ir`/call, `-O3 isolated` (`NOTES.md` §4). `nkw` is the number
of key bytes walked per call.

| difference | small (nkw 128) | large (nkw 1024) | law |
|---|---:|---:|---|
| R2 − R3 | +273.00 | +2065.00 | **`2·nkw + 17`**, residual 0.00 on 30/30 sweep blobs |
| R3 − R4 | **+2.00** | **+2.00** | **flat**, 32/32 blobs |
| R4 − R5 | 0.00 | 0.00 | byte-identical |
| `c-gcc-h` − `c-gcc` | +128.00 | +1024.00 | exactly **1.00 per key** |
| `c-clang-h` − `c-clang` | +640.00 | +5120.00 | exactly **5.00 per key** |

⚠ **`R3 − R4 = +2.00` is a FIXED-R4 bound and it is not "the cost of safety".**
The R4 side is **not degenerate**: `r4_reslice` — the shipped R4 with the one
reslice R3 already has — is in contract, verifies `20 verified, 0 errors`, has a
byte-identical R5 twin (built and diffed), and is **`1·nkw − 5` cheaper**
(123.00 / 1019.00). Against it the same difference is **+125.00 / +1021.00**,
i.e. 510× the shipped figure on the large band. The shipped R4 is kept
(`.memory/02-bench-rules.md`: never re-ship a rung because a cheaper in-contract
spelling was found) and the span is published instead. `NOTES.md` §4d.

⚠ **And the bounded probe straddles the shipped R3 — one side is FASTER.**
`r3_bounded` runs 440.84 / 3844.04 `Ir`/call **below** the shipped R3 because the
trip count lets LLVM restructure the loop, so "the careful programmer pays for
the bound" is false here. `r3_bounded_kept` runs 167.65 / 1235.96 **above** it.
Neither figure is a safety cost. `NOTES.md` §8b, §8c.

⚠ **The C column's 1× / 5× split is a DERIVATION, not a guess.** An earlier
version of `NOTES.md` §4e said clang "presumably" restructured the key loop; it
does not. Counted per instruction with callgrind (`controls/dyn_ir.py`): clang
**refuses to short-circuit** the `&&` and pays `+setne +setb +and +2·cmp +jne
−je` = **+5.00/key**; gcc does short-circuit (`+cmp +ja`) and recovers a `lea`
by re-associating the Horner shift, = **+1.00/key**. TASK_070_REVIEW F7.

## What R5 adds, precisely

Verus **requires a `decreases` clause on every exec loop by default** — on every
R5 in this tree, since p01, which is why the "first termination obligation"
claim above is retracted:

```text
error: loop must have a decreases clause
    = help: to disable this check, use #[verifier::exec_allows_no_decreases_clause]
```

Discharging **p22's** needs the EMPTY witness that `nfill < TABCAP` supplies
through a counting lemma. The measure is a **ghost** unwrapped cursor `u` with
`i == u % TABCAP` plus a **ghost** witness `e` for an EMPTY slot — so **the
termination proof costs zero instructions** and R4 ≡ R5 stays `exact` at O3. The
alternative, an exec-side probe counter, would have put the bound in the binary
and made the proof circular with the fix; it is forbidden by the contract and
priced as a control.

⚠ **What the mutant battery does and does not show** (`NOTES.md` §10, re-run with
`--multiple-errors 20`, which `.memory/04-verus.md` §2b prescribes and the first
version omitted). It **does** show the measure is checked: `m3_noempty` fails
*first* with `decreases not satisfied at end of loop` **at the probe loop**. It
**does not** show the conjunct is required *only* for termination — deleting it
also breaks the arithmetic invariant `nfill <= TABCAP`, and once that is deleted
too, the overflow check on `nfill + 1`. The defensible claim is the narrower one:
*the termination obligation is real, is checked, and cannot be discharged without
the conjunct.*

## Layout

```
c/kernel.c              R1  — omits `&& nfill < SLB_P22_TABCAP`
c/kernel_hardened.c     R1h — otherwise character-identical
c/main.c  c/kernel.h
safe_naive.rs  safe_tuned.rs  unsafe.rs  verus.rs
model.py                the independent Python reference
inputs/gen.py           deterministic blobs; audits every window by SIMULATING
                        the unguarded rung and refuses to ship an undeclared hang
controls/mkcontract.py  writes spec.md (edit the generator, not spec.md)
controls/gen_controls.py  every non-rung variant, measured. Verus always with
                        --multiple-errors 20 (VERUS_FLAGS)
controls/sweep_ir.py    the sweep-band marginals and the additivity test
controls/dyn_ir.py      per-INSTRUCTION dynamic Ir for two cells, and the diff
                        — what a static asm.py diff cannot settle (NOTES.md 4e)
controls/clayout.py     the code-layout population behind any `ns` figure
                        (ported, NOT run — p22 publishes no `ns` figure)
```
