# TASK_021_REVIEW — the R4 side is not flat, so the two-sided floor does not stand

**Should the retracted sentence go back into `.memory/`? Yes — restricted to the
row-scaled term, and with a different number.** Exactly these words:

> **"On p05, the `O(nrow)` part of the in-contract safety tax is the price of the
> optimiser failing the lemma the proof proves."** True of *this kernel*, *this
> declaration* and *this toolchain*, and of the row-scaled term **only**: the
> in-contract respelling removes exactly one instruction per row (`add %rsi,%rax`,
> the `add` that makes the row base buffer-absolute) and the five that survive are
> the reslice's bounds check, whose deletion needs `(i+1)·ncol <= nrow·ncol` —
> the nonlinear fact R5 discharges with `lemma_mul_inequality`. It is **not** true
> of the constants, which move in *both* rungs and by *different* amounts, and it
> is not a statement about safety in general.

What must **not** go in: "two-sided", "zero R4 spread", and `5·nrow + 6`. The
best-found in-contract floor is **`5·nrow + 11`** (106 at `small`, 336 at `large`
against a published 123 / 399), measured with zero residual on all 179 points.

---

## Findings

### blocker B1 — "the R4 side has **zero** in-contract spread" is false; the floor is `5·nrow + 11`, not `5·nrow + 6`

`patterns/p05-index-flatten/NOTES.md:1407` (§14f title), `:1424` ("one executed
count at every point"), `:1428` ("the shipped R4 is the cheapest in-contract
unsafe spelling found"), `:1486-1490` (§14h.4), `README.md:145-149`,
`RECAP.md:170-172`, `.memory/01-ladder.md:787-789` (the PROVISIONAL block).

All eight of the engineer's R4 spellings decode the header the shipped way —
`movzwl` + two `movzbl` + `shl` + `or` (`asm-r4_ship.txt` lines 1, 5-8). The
**header** is never respelled on the R4 side. On the R3 side it is, and §14g:1450
says so itself: *"The `+3` is the header: shipped decodes `nrow`/`ncol` with
`movzwl` + two `movzbl` + `shl` + `or`; the array form issues one 4-byte load"*.
The write-up names the term as header-side and then leaves it in the difference.

Applying the same respelling to R4, in contract (nothing in `required`/`forbidden`
mentions the header; R4's definition licenses `get_unchecked` and raw pointers,
and the shipped R4 already uses `get_unchecked` for the header):

| review spelling | header | `− R4ship`, 179 pts | `md5_fn` |
|---|---|---:|---|
| `x4_h1u` | `unsafe { buf.get_unchecked(off..off+4) }.try_into()` → two `u16::from_le_bytes` | **−3**, flat | `32a2f792dfdf` |
| `x4_hptr` | `(buf.as_ptr().add(off) as *const u32).read_unaligned()` | **−3**, flat | `c1179a6732d6` |
| `y4_hptr_{for,getrange,dsrow,rowslice,dataptr,cells,dsrow_cells,nozero}`, `w4_hptr_g2` | ditto × 9 bodies | **−3**, flat | 8 more bodies |
| **`w4_hu16`**, `w4_hu16_g2` | two unaligned `*const u16` reads | **−5**, flat | `7110dd6bea56`, `ba3cbd8e2d88` |

**13 in-contract R4 spellings, 11 distinct `md5_fn` bodies, all cheaper than the
shipped R4.** Laws, my own build and my own probe, zero residual on **179/179**:

```
  my r4 rebuild == engineer's r4_ship        179 points, residual 0 on  179
  R3ship - R4ship = 6*nrow + 9  [published]  179 points, residual 0 on  179
  r3_ds_h1 - R4ship = 5*nrow + 6 [NOTES 14]  179 points, residual 0 on  179
  R4ship  - x4_h1u  = 3 (flat)               179 points, residual 0 on  179
  R4ship  - w4_hu16 = 5 (flat)               179 points, residual 0 on  179
  r3_ds_h1 - w4_hu16 = 5*nrow + 11 [FLOOR]   179 points, residual 0 on  179
```

Equivalence: 28 binaries × 183 committed inputs, **0 mismatches** — every one
prints the shipped R4 binary's checksum and exit code.

The in-contract R4 interval is therefore **5 Ir wide, flat in `nrow` and `ncol`**
(1376.00 … 1381.00 on `small`, 8430.70 … 8435.70 on `large`), not zero. So:

* "p05 is the first pattern with a two-sided floor" — **withdrawn**.
* `5·nrow + 6` — **wrong by 5**. Best found is `5·nrow + 11` = 106 / 336.
* "101 at `small` against a published 123, 331 at `large` against 399"
  (`NOTES.md:1474`) → **106 / 336**.
* "the published figure is high by `nrow + 3` — 18% / 17%" (`:1264`) → high by
  `nrow − 2`, i.e. 17 / 63, **14% / 16%**.

**Failure scenario.** `.memory/` records p05's safety number as "nearly a number
rather than a bound". The next agent quotes 101 / 331 as p05's in-contract
minimum tax. The first reader who respells the *header* of the unsafe rung — a
two-line change that touches nothing the declaration mentions, and the exact
change the delivery already made on the safe rung — measures 106 / 336. That is
the fifth time a p05 headline has moved on the first thing someone tried.

**What survives, and it is the important half.** My correction does not touch the
mechanism. The *row-scaled* reduction is still exactly `nrow`, still exactly the
`add %rsi,%rax`, and the five survivors are still the check. What moves is the
**constant** (−3 safe side, −5 unsafe side). Stated about the `O(nrow)` term the
rehabilitation is stronger than the delivery argued, because the constant — which
is where the asymmetry lives — drops out of it.

### major B2 — the headline number is reading-dependent; only the *qualitative* conclusion is not

`NOTES.md:1261-1264` opens §14 with *"The measured in-contract minimum is
`5·nrow + 6`"* unconditionally; `README.md:139-142` says *"the shipped R3 is
beaten under **both** readings of `required[1]`: seven textually independent
in-contract respellings reach `5·nrow + 6`"*, which reads as if the floor held
under both. It does not. §14b:1328-1330 and §14e's `reading` column are correct;
the summary, the README, `RECAP.md` and the `.memory/` PROVISIONAL block are not.

Measured, after correcting the R4 side (all from the engineer's own sweep plus
mine, zero residual on 179 points):

| reading of `required[1]` | cheapest in-contract R3 (rel R4ship) | both rungs tuned (min R3 − min R4) | at `small` / `large` |
|---|---|---|---|
| p16's (hoisted sub-slice) | `5·nrow + 6` | **`5·nrow + 11`** | 106 / 336 |
| strict (`base = off + 4 + i*ncol`) | `min(6·nrow + 6, 5·nrow + 12)` | `min(6·nrow + 11, 5·nrow + 17)` | 112 / 342 |
| — published shipped pair — | `6·nrow + 9` | — | 123 / 399 |

So the ambiguity is **load-bearing for the number** (106 vs 112 at `small`,
336 vs 342 at `large`) and not for the sentence *"the shipped R3 is not the
cheapest admissible spelling"*, which holds under both readings — `r3_hdrarray`
is 3 cheaper than shipped R3, flat, at every `nrow`, and respells nothing but the
header. §14h.1 is therefore correct as written; §14h.2's *number* is not.

**And a definitional point the delivery's framing hides.** §14h.4 calls
`5·nrow + 6` *"the whole in-contract interval's lower end"*. That presupposes the
R4 side is a point. It is not, so "the in-contract safety tax" is only well
defined as an interval or under a stated pairing convention: the min over
in-contract *pairs* is `min R3 − max R4`, and under the strict reading at
`nrow ≤ 6` the "both rungs tuned" pair is actually **dearer** than the shipped
pair (`6·nrow + 11` against `6·nrow + 9`), because tuning R4's header buys 5 and
tuning R3's buys only 3. p05 needs the same interval treatment p16 and p17 got;
"two-sided floor" is not a shape this pattern has.

Note the pleasant robustness that *is* available: the header term cancels between
the two header treatments. If array/packed headers are ruled *out* on both sides,
min R3 = `r3_ds_h0` = `5·nrow + 9` and min R4 = R4ship, giving `5·nrow + 9`;
ruled *in* on both sides it is `5·nrow + 11`. Only the asymmetric treatment gives
`5·nrow + 6`.

### minor m1 — "four distinct machine-code bodies" on the R3 floor is five

`NOTES.md:1393-1397`. The seven ✦ spellings carry `e1d625cc9b0e` (`_h1`, `_h2`,
`_copied`), `d233f48a00ff`, `9e59f98affaa`, `83d5f8bb96a5`, `cf5784a53206` —
**five** distinct `md5_fn`, not four. Under-counts its own evidence.

### minor m2 — §14a's admission table claims a grep it does not pass

`NOTES.md:1299-1300` records `required[2]` and `required[3]` as *"greppable, true
of all 37"*. `r3_ds_cells` — one of the seven spellings that define the floor —
writes `cells > avail` and `.wrapping_add(cells as u64)`. Whitespace-deleted,
`nrow*ncol>avail` **MISS**, `(nrow*ncol)asu64` **MISS**. The *property* holds
(`cells` is bound to `nrow * ncol`); the stated grep does not. Same for my
`y4_hptr_cells`. Harmless to the floor — six other spellings reach it and pass
the literal grep — but it is a claim asserted as measured that was not.

### minor m3 — "they cannot be removed by any spelling" is not measured

`NOTES.md:1455-1459`. §13 row 3 (`t4_idx`, out of contract) is `3·nrow + 8`
against R4ship, i.e. supplying a *linear* induction variable removes **2 of the
5** per-row instructions (the `mov;imul` re-derivation) while `lea;cmp;ja`
survive. The defensible claim is "no in-contract spelling searched removes them",
which is what §14h.4's own hedge says.

### minor m4 — "179 points" contains two duplicate dimensions

`NOTES.md:1366`: *"179 inputs — 14 values of `nrow`, 96 of `ncol`"*. There are
177 sweep blobs plus `small` (19×26) and `large` (65×61); `sweep-r19c26.bin` and
`sweep-r65c61.bin` both exist, so 177 *distinct* `(nrow, ncol)` pairs. The two
repeats carry different bytes, so they are still independent measurements — but
"179 points" reads as 179 distinct points of the model's domain.

### minor m5 — one occurrence of `6·nrow + 9` with no upper-bound pointer

`NOTES.md:1085` (§12c's closing "the sentence that replaces this one"). Every
other occurrence (§2a's ⚠, §12d, §13, README) now carries the amendment.

---

## Clean negatives — attacks that did not land

1. **The R3 floor holds.** Seven further in-contract R3 spellings, none below
   `r3_ds_h1`'s 1482.00 / 8766.70: `.map(..).fold` (1485), `.rev()` (1867 —
   de-vectorises), `assert!(data.len() == nrow*ncol)` (1485), an explicit in-loop
   `base + ncol > n` guard (1489), two separate `u16` `try_into` reads (1487),
   `u16::from_le_bytes([buf[off], buf[off+1]])` direct indexing (1497), and the
   array header re-spelt (1482). Safe Rust cannot reach the unsafe rung's
   two-`u16`-load header, which is *why* the constant does not cancel.
2. **Band D and input identity are exactly as claimed.** Ran `838ccb4^`'s
   generator and the committed one into separate scratch dirs: old emits 150
   blobs, new 183, **0 of 150 differ**, 33 new = `nrow ∈ {1…9,12,16} × ncol ∈
   {30,32,33}`. All 183 on-disk blobs are byte-identical to the committed
   generator's output. The `nrow` axis really is 14 values now.
3. **Provenance is sound.** `harness/build.py p05 --cell {safe_tuned,unsafe} --opt
   O3 --mode isolated` gives `md5_fn 9de0ae49d75a…` / `4a28657ae7e4…`, matching
   the committed tables and the engineer's rebuilds; the gate's committed
   marginals 1504.00 / 8834.70 and 1381.00 / 8435.70 reproduce to the
   instruction. My independently written variant template reproduces
   `4a28657ae7e4` **byte for byte** (`x4_ship`), so the −3 / −5 cannot be a
   template artefact.
4. **The mechanism is exactly as §14g describes.** My own disassembly:
   R4 shipped 12 insns/row, R3 shipped 18, `r3_ds_h1` 17; the removed instruction
   is literally `add %rsi,%rax` (`asm-r3_ship.txt` line 52); the five survivors
   are `mov;imul` · `lea` · `cmp;ja`; `r3_ds_h1`'s vector guard really is
   `cmp $0x80000,%r9d` against the packed header word. Not a coincidence of one
   codegen either — it is corroborated by §12b's `probe2.rs` linearisation
   control and by R5's obligation being `lemma_mul_inequality` itself.
5. **`md5_fn` invariance is stronger than claimed.** Not 28/28 but **188/188**:
   every `md5_fn` cell in all six `results/tables/*.md` is unchanged across
   `838ccb4^..HEAD`, and `git diff` over `patterns/*/*.rs`, `patterns/*/c/*` and
   `common/` is empty — no cell source changed at all.
6. **`marginal_ir_per_call`: 564 cells, exactly 8 moved**, all p08, all
   `|Δ| ≤ 0.04`, all on `O0` or `whole` rows. As claimed.
7. **The hash gap is really closed.** 158 hashed source entries across the six
   records, **0 stale**; the four new keys (`inputs/gen.py`, `common/slb.py`,
   `verus_run.py`, `controls/*.py`) present. The demonstration reproduces: record
   A vs B is 514 leaves with **exactly 2 differing** — the ASan PID and
   `.source_sha256."patterns/p16-tlv-walk/inputs/gen.py"` — and the key is absent
   from `838ccb4^`'s record, so the edit really did move nothing before.
8. **p16's controls generator reproduces §10a byte for byte.** `md5_fn`
   `34a618f837f2` (117), `c7f697a8d9ec` (119), `999fb67758ff` (118), matching
   `NOTES.md:1207-1208`; and all three laws re-derive end to end from the
   committed tree with **zero residual on 22 blobs**: `R3ship − r3_endslice =
   2·nrec − 2`, `R3ship − r3_window = 4·nrec − 8`, `r3_hdrarray − R3ship = nrec`.
9. **The reported p08 adjacent defect is real.** `.temp/p08/controls/{nonoverlap,
   fwd_loop}.rs` carry `#[path = "../../common/driver.rs"]`, which resolves to
   `.temp/common/driver.rs` — present and byte-identical today, gitignored.
10. **Audit selftests and buckets.** `_AUDIT_CASES` 13/13, `_IDIOM_CASES` 13/13,
    `_MATCH_CASES` 10/10 pass when executed directly; `no_rung_entries = 0` and
    `languages = ['c','rust']` in all six records; p05 `spellings = 0`, so the
    machine audit genuinely decides nothing on p05 — §14a is right.
11. **All six gates green**: `failures = 0`, `complete_run = true` on all six;
    p01 `PASS-WITH-BLOCKED-ROWS`, the other five `PASS`.

## Not done

* Did not re-run `harness/check.py` end to end (the committed records verify
  against the tree: 0 stale hashes, 0 failures, and no cell source moved).
* Did not sweep the `y4_*` / `z3_*` probe families over all 179 points — only
  `x4_h1u`, `x4_hptr`, `w4_hu16`, `w4_hu16_g2` and the baselines were swept.
  The `y4_*`/`z3_*` figures are `small`/`large` only and are reported as such.
* Did not check R5/Verus obligations; no `verus.rs` change was in scope.
* `5·nrow + 11` is **best found**, not an infimum — `inf(R4) ≤ inf(R3)` still
  holds by construction (finding 14), and my own search on the R4 header is
  exactly the kind of move that has now beaten two "floors" in a row.

## Artefacts

`.temp/review021/` — `mkvar.py`, `mkvar2.py` (variant sources → `v05/`),
`mir.py` (independently written marginal probe), `laws.py` (residuals),
`equiv.py` (183 inputs × 28 binaries), `sweep*.json`, `asm-*.txt`,
`gen_old/` + `gen_new/` (the two generators' outputs), `NOTES.md`.
