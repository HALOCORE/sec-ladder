# TASK_089_REVIEW — report

**Role: research reviewer.** Attacked `p46` at `591fcec`. Ran `check.py p46`
(**PASS**) and `measure.py --check-stale` (**48 records, 0 STALE**). Independent
work in `.temp/r89/`: rebuilt `.temp/t86/{cost.rs,probe2.rs}` **with and without
`black_box`**; a `shape.rs` control putting p46's **shipped** kernel body inside
the probe harness; the rolled-vs-rolled control under **two** flag sets; six
Verus probes; a **second** disassembly pipeline (not `harness/asm.py`); and an
independent re-measure of the whole sweep band. Tree clean.

**PROTOCOL rule 2 running count: 257 → 259.**

⚠⚠ **TWO BLOCKERS, AND THE MANAGER HAD ALREADY COMMITTED BOTH INTO `.memory/`.**
✅ **Both retracted at `350b8a2`, and the root cause fixed in `CLAUDE.md`.**

---

## B1 — blocker. *"A mutable sub-slice at this pin is SOUND but VALUELESS"* is FALSE — the `copy_from_slice` failure mode recurring

`~/tools/verus/vstd/std_specs/slice.rs` ships

```rust
pub assume_specification<T>[ <Range<usize> as SliceIndex<[T]>>::index_mut ]
    (i: Range<usize>, slice: &mut [T]) -> (r: &mut [T])
    ensures  r@ == old(slice)@.subrange(i.start as int, i.end as int),
             final(r)@ == final(slice)@.subrange(i.start as int, i.end as int),
             forall|j: int| !(i.start <= j < i.end) ==> final(slice)@[j] == old(slice)@[j],
```

— **a full VALUE-LEVEL mutable sub-slice specification.** ✅ **MANAGER-VERIFIED
by reading the pinned file.** Plus `<[T]>::split_at_mut` and
`ref_mut_array_unsizing_coercion`.

⚠ **The engineer read `vstd/slice.rs`'s `ExSliceIndex` TRAIT DECLARATION** —
which does carry a `requires` and no `ensures` — **and mistook it for the
specification.** The probe `controls/census.py` labels *"THE FINDING: the written
VALUE cannot be related back to the array"* verifies **`2 verified, 0 errors`**
with **one added line**:

```rust
proof { vstd::seq::lemma_seq_subrange_index(out@, i as int, (i+m+1) as int, 0); }
```

**Blast radius:** `NOTES.md` 0c; `unsafe.rs:29–44`; `safe_tuned.rs:17–33`;
`README.md` result 4; **`spec.md`'s HASHED `why`**; `.memory/06-catalogue.md`'s
p46 row (**was landed, now retracted**); and the report's queued Memory update 2.
⚠ **`controls/census.py --mutsub` exits non-zero UNLESS probe 4 FAILS, so the
committed control now enforces the wrong verdict.**

⚠⚠ **It also breaks A1 limb 1.** *"Both spans degenerate"* holds **only because
`r4_mutreslice` is excluded**. It beats the shipped R4 **and every safe
spelling** by **697…2597 `Ir`/call**, so if admissible **the R4 span is ~2600,
not 3, and the pair does not collapse.**

⚠ **The reviewer refuted the stated REASON, not the conclusion:** whether
`r4_mutreslice`'s **full R5** closes is **now open**, and **p46's central framing
depends on it.**

## B2 — blocker. The `black_box` mechanism is FALSE, and it was already in `.memory/`

Every `.temp/t86/probe2.rs` kernel is `#[no_mangle] #[inline(never)] pub fn` —
**external linkage, so a caller-side `black_box` cannot reach the callee's
codegen.** Measured on the **linked** binaries:

```
k46_checked    296 B  a73eda77…   <- IDENTICAL with and without black_box
k46_unchecked  126 B  daca171e…   <- IDENTICAL
k23_*, k24_*, k26_* : all byte-identical
k35_enum/union/tagged : mnemonic-identical after rip-relative normalisation
```

✅ **THE REAL CAUSE IS THE PROBE KERNEL'S SIGNATURE**, isolated by
`.temp/r89/a2/shape.rs`, which compiles p46's **shipped** body beside
`k46_checked` in one binary, **both called through `black_box`**: `k46_checked`
keeps **10 conditional branches**; the shipped body **loses every bounds check**.

⚠ **The retraction has teeth:** the next probe author dropping `black_box` *"so
as not to hide range facts"* would **re-enable the constant folding it exists to
prevent**, while the real cause went unfixed.

**Exposure, RANKED from the probe sources:** **p24 HIGH** (same linear shape —
expect the same sign flip), **p26 HIGH**, **p35 MEDIUM**, **p23 LOW and
structurally robust** (`while v[i] < pivot { i += 1 }` has no upper guard — the
bounds check **IS** the termination bound), **p28 not in `cost.rs` at all**.
✅ *"p28 is the control"* is right for a second reason.

---

## M1 — major. Three shipped cell sources and the HASHED contract still describe the retracted pre-build world

The report claims *"neither probe is quoted as a p46 number anywhere"*; true of
`NOTES.md` only.

- **`c/kernel.c:13–22`** — *"**THE HARM IS LOUD HERE** … five of six plain builds
  abort or fault, and only one is silent (../NOTES.md 0a)"*. **`NOTES.md` 0a says
  the opposite** and the reviewer reproduced it: **6 of 8 exit 0 with a wrong
  answer.** ⚠ **The citation points at the section that retracts it.**
- **`safe_naive.rs:5–25`** — the retracted `7.00`/MAC; *"the checks are NOT
  hoistable"*, *"LLVM still cannot remove them"*; and *"**186** instructions
  against the unsafe rung's **111**"* — the gate says **179/150**, no-pad
  174/147, objdump 184/155. ⚠ **No pipeline yields 111.**
- **`safe_tuned.rs:17–33`** — cites a *"2×2 `(n,m)` grid"* that is **not in
  `NOTES.md`**, and calls `−1.5`/MAC *"cheaper than this rung"* when the
  coefficient is against **R4** (against R3 it is `−1.0`).
- ⚠⚠ **`spec.md` line 253, INSIDE the hashed `why`:** *"Three R3 spellings span
  **9490** … three R4 spellings span **2750**; **NEITHER SIDE IS DEGENERATE**"* —
  `NOTES.md` 8b says **both ARE degenerate**, spans of 2 and 3, and
  `grep -c '9490\|2750' NOTES.md` = **0**.

**The C-source fix costs a re-measure by design; the other three do not.**

## M2 — major. R3's *"one reslice check per ROW, `O(n)`"* does not exist in the machine code

`safe_tuned`'s kernel has an **identical conditional-branch multiset** to
`safe_naive`'s (`je:6 jne:5 jae:2 ja:2 jb:1 jbe:1`). The measured
`R3 − R2 = 2n − 2 (m even) / −2 (m odd)` is **address arithmetic** — `lea` + `add
$0x8`, the row base computed once per row — and `safe_naive` computes the same
base in its odd-`m` remainder block, **which is exactly why the law has two
branches.** ✅ **The mechanism is confirmed from both sides.**

⚠ **So there are THREE hardening strategies, not four:** `0` (proof), `O(1)`
(C's pre-loop compare), `0` (the language's checks, deleted). **R3's `2n` is a
spelling cost.** Falsifies `NOTES.md` §1 and §8e (*"the pattern's cleanest
positive result"*), `README.md`'s rung table and *"four different asymptotics"*,
`safe_tuned.rs`'s *"that asymptotic change is the whole lever"*, and `spec.md`'s
`why`.

## M3 — major. `verus.rs:39` says the safety-line-deleted control gives `14 verified, 1 errors`; it is `20 verified, 1 errors`

`NOTES.md` 6a, `controls/mkvariants.py` and the reviewer's own run all say **20**.
⚠ **The report says a `verus.rs` doc-comment edit already forced a re-measure;
this number survived it.**

## minors

- **m1 — A4 resolves the OTHER way: neither prose nor tool is wrong; the
  REPORT'S FRAMING is.** Under §8's declared convention (whole-program marginal)
  there is exactly **one** `+3.00` exception. §8d's second is real under the
  **kernel-exclusive** convention (`8275−8271 = +4` on `small`,
  `28869−28866 = +3` on `large`). **The defect is §8's summary line sitting under
  a header declaring the section's convention.**
- **m2 — the committed gate record is not bit-reproducible.** `check.py p46`
  moved **33 numbers**, all stage-3b whole-program marginals on `-O0`/`whole`
  cells (±7 `Ir`/call, **identical shift on both inputs so every
  `d_ir_d_work` is unchanged**) plus two ASan addresses. ✅ **No `-O3 isolated`
  figure moved — nothing p46 publishes is affected.** Unexplained.
- **m3** — `.temp/t89/unrollctl.sh` omits `-C codegen-units=1`, which
  `build.py` passes. **Verified harmless** (adding it moves both sides by exactly
  `+3.00` and leaves every difference unchanged).

---

## ⚠⚠ THE PROTOCOL FINDING, and it is the sharpest thing in this review

> **"The Rule 6 verification and M1/B1 are the same fact seen twice. The `why`
> really WAS frozen before any cell was built — which is WHY it still describes
> the pre-build probe's world. Rule 6 protects against a declaration edited
> AFTER measuring; it does NOTHING about a declaration that measurement has
> since FALSIFIED."**

✅ **Rule 6's disclosure VERIFIED by exact hash reconstruction** — deleting the
`unsafe_justifications` block and one trailing comma reproduces the recorded
pre-build sha256 **exactly**, so no `required`/`forbidden`/`identity`/`why`
moved. **p46 is the first pattern where that gap is demonstrated with a matching
hash.**

## Clean negatives, by name

**A1 limb 2 — the `0.00000` per-MAC tax is REAL and holds RUNG-WIDE, not just in
the MAC loop**: `safe_naive` 184 insns / 17 cond, `unsafe` 155 / 15; the MAC loop
is 19 insns with **one** conditional branch (its own `jne`); **no bounds branch
anywhere in R2's kernel.** **A1 limb 3 — the rolled control reproduces to the
instruction, is symmetric, and holds under both flag sets**, `R2 − R4 rolled =
+2.00000·n·m` on all five shapes. **The four cost laws** — independent
re-measure, zero residual. **A3a's harm mechanism** — re-derived on the shipped
binaries: gcc `-O3` `bl` at `0x3a0(%rsp)`, `out` at `0xa0(%rsp)`, Δ `0x300` = 96
limbs, canary above both; all 32 cells reproduce. **Rule 6** — verified by exact
hash reconstruction. **`by (bit_vector)` / `by (compute)` first in tree** — all
10 non-p46 hits are inside comments. **TCB tally** (5 `external_body`, 3 twins,
no `assume`/`admit`). **R4 ≡ R5** (`O3 exact`, 0 `Ir` on all 49 blobs
re-measured). **`model.py::_fold_bigint` is genuinely independent** — one Python
big-int multiply, sharing only `_ld64`/`_guards`. **Rung semantic equivalence**
— 32/32 cells agree on all three non-adversarial inputs. **No constant folding.**
**R2 is a fair naive port.**

## Unsure / not done

- ⚠ **Did NOT establish that `r4_mutreslice` is admissible** — only that the
  stated obstacle is not one. **The full nested-loop R5 through a mutable
  sub-slice was not attempted, and p46's framing depends on it.**
- The ±7 `Ir` gate-record drift has **no mechanism**.
- Exposure ranking for p23/p24/p26/p35 is from the probe sources plus p46's
  measured mechanism; **no shipped-shape kernel was built for any of the four.**
- No wall-clock work.
