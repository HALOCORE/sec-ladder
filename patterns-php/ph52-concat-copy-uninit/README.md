# ph52 — an unconstructed caller slot destructed on an early exit

**PHP 5.0.0 · `Zend/zend.c:242-247` · corpus row LOGIC-007 · CWE-457 (CWE-824 as
the consequence) · tier `narrowed` · the second `T3` row (*initialised before
read*), and the one that CLOSES the family.**

`Zend/zend_operators.c:1148` declares **`zval op1_copy, op2_copy;`** — bare stack
locals, no `= {0}`, no `INIT_ZVAL`, no `memset` — and hands their addresses to
`zend_make_printable_zval`, which writes `expr_copy->value.str.*` on every arm and
`expr_copy->type` **once, at `:263`, after the switch**. The `EG(exception)` early
exit at `:243` tears the slot down first, and `_zval_dtor` dispatches on the
unwritten tag byte and **frees a pointer read out of the same slot**.

⚠⚠⚠ **The harm is a TAG-DISPATCHED FREE, not a read.** A kernel whose teardown
merely *branched* would have built a weaker row.

## Read these four things, in this order

1. **`NOTES.md` §4 — DELIVERABLE #0, and the five things it broke.** ph52's
   uninitialised datum is on the **stack**, where every mechanism this tree has is
   an *allocator* shim, so determinism was settled before any rung existed.
   `controls/d0_stack.py` drives 16 cells. ⭐ The offset **is** reused exactly — so
   the trigger is a **call history** — and without a `noinline` on the lifted
   callees **2 of the 16 answer differently**, because at `-O3` a compiler that can
   see the unwritten tag treats it as `undef` and folds the teardown away. ⛔ Five
   of the manager's registered statements are refuted there, including *"a clean
   stack slot reads ZERO"* (an **ASan** property) and the registered prediction that
   the harness's `isolated`/`whole` axis would decide it (it decides **nothing**).
2. **`NOTES.md` §6 — the tag sweep, which is the row's publishable number.**
   `controls/tag_sweep.py` drives the whole tag byte through `_zval_dtor` and
   measures **12 of 256 values (4.688 %) tearing anything down and 8 of 256
   (3.125 %) reaching `efree`**. ⭐⭐ So **95.3 % of byte values make `zend.c:243` a
   no-op**, and `IS_NULL` is `0` — which is the answer to *why do
   uninitialised-read bugs survive for years in shipped code*, and why LOGIC-007 is
   recorded `uninit-read-silent`. ⚠ `RECAP_PHP.md` F102's untested *"five named
   cases"* is wrong in three ways and §6a itemises them.
3. **`NOTES.md` §5 — the defect is in the published u64**, which `ph53`
   structurally could not manage. `inputs/adversarial-dblfree.bin` and
   `inputs/adversarial-safe.bin` differ in **one op byte**, and R1 and R1h differ on
   one of the pair and agree on the other. ⭐⭐⭐ **And §7 is the row's most surprising
   measurement: ASan fires on the two BENIGN inputs and is SILENT on the adversarial
   one.** Its fake stack hands out a zeroed frame on 282 of 283 `:243`-reaching calls
   and a **recycled** one on the 283rd — so **the detector manufactures the defect it
   was asked to find**, on an input the real stack keeps clean. F102's `0xbe`
   correction with the sign reversed.
4. **`NOTES.md` §11 — the Verus side, and the first two-row law on the `T3` axis.**
   `controls/negatives.py --verus` mutant **V1** deletes the witness test — which is
   `zend.c:243` exactly — and Verus refuses with `precondition not satisfied`. ⭐⭐
   And `controls/r4_nowitness.rs` **reproduces the C's defect bit for bit**: it
   prints R1's answer, not R1h's, where ph53's witness-free control answered
   *correctly*. §11c is the witness-cost comparison against ph53's `+21.775 %`.

## The ladder, in one table

Four answers to one question — *has this slot been constructed?*

| rung | how it answers | note |
|---|---|---|
| **R1** `c/kernel.c` | it does not ask | the defect (LOGIC-007) |
| **R1h** `c/kernel_hardened.c` | ⭐ it **deletes the question** — `7412202c43e7` removes the one line that asks | and the deletion is **COMPLETE**, unlike `ph53`'s fix |
| **R2** `safe_naive.rs` | `Option<Pr>` + `take()` | the C's **fourth** slot state becomes unrepresentable |
| **R3** `safe_tuned.rs` | ⭐ **a port of R1h, made structural** — the printable is returned, so the deleted line cannot be written | available only *because* the fix is complete |
| **R4/R5** `unsafe.rs` / `verus.rs` | **one bit per slot** — `constructed: bool`, two for the whole kernel | against ph53's `[bool; MAXD]` |

⭐ **R4 and R5 are the same machine code at `-O3`** (`identity: norel`, 433
instructions each, equal `md5_raw_norel`), which no other php row reports — and they
are **bit-identical in `marginal_ir_per_call` too**, at `1975.16` Ir/call.

## What is here

| | |
|---|---|
| `spec.md` | the hashed contract: the pins, the divergence ledger, the provenance, the Verus obligations |
| `NOTES.md` | every measurement, each with its mechanism |
| `model.py` | **three** independent implementations, a 69-window synthetic sweep, four must-fire mutants and one must-NOT-fire |
| `inputs/gen.py` | the corpus, with the **three call-history rules** re-derived from the bytes it wrote |
| `c/kernel.c` · `c/kernel_hardened.c` | R1 and R1h, differing by **one statement** |
| `controls/d0_stack.{c,py}` | Deliverable #0's 16-cell table, **committed** (§F6) |
| `controls/tag_sweep.{c,py}` | the 12-of-256 figure, with 15 assertions |
| `controls/r1h_onelinedel.py` | §C's owed argument **as a check**, 11 cases |
| `controls/negatives.py` | `--verus` (7 arms), `--miri` (8 arms), `--firstcall` (the blob `inputs/` cannot carry) |
| `NOTES.md` §12 | ⚠ **four citation defects the row found in its own committed files**, and why writing the named controls was cheaper than correcting the pointers |
| `controls/mu_unwrapped.rs` | the obligation with **no trusted item**, 6/0 |
| `controls/r4_nowitness.rs` | the faithful witness-free R4 — **it reproduces the defect** |
| `controls/digest.py` | the three content-digest constants and **all 256 object handles**, 10 assertions |
| `controls/dblfree.py` | the escalation from *the defect is in the u64* to **`SIGABRT`**, 4 iteration counts × 4 cells |
| `controls/tu_boundary.sh` · `controls/firstcall.py` | the entry points `c/kernel.c` and `inputs/gen.py` name — both in the **measurement** digest, so the files were written rather than the comments corrected (`NOTES.md` §13) |
| `controls/7412202c43e7.patch` | the upstream commit, committed so the citation survives without network |

## Running it

```sh
python3 harness-php/gate.py --tool build   ph52-concat-copy-uninit --all
python3 harness-php/gate.py --tool measure ph52-concat-copy-uninit
python3 harness-php/gate.py --tool report  ph52-concat-copy-uninit
python3 harness-php/gate.py               ph52-concat-copy-uninit

python3 patterns-php/ph52-concat-copy-uninit/controls/d0_stack.py --selftest
python3 patterns-php/ph52-concat-copy-uninit/controls/tag_sweep.py --selftest
python3 patterns-php/ph52-concat-copy-uninit/controls/r1h_onelinedel.py --selftest
python3 patterns-php/ph52-concat-copy-uninit/controls/negatives.py --all
python3 patterns-php/ph52-concat-copy-uninit/controls/digest.py --selftest
python3 patterns-php/ph52-concat-copy-uninit/controls/dblfree.py --selftest
sh      patterns-php/ph52-concat-copy-uninit/controls/tu_boundary.sh --selftest
```

⚠ **Never run `harness/check.py` directly on a php row** — everything goes through
`harness-php/gate.py`, which builds the shim, verifies the digest bridge and checks
provenance first (`PROTOCOL_PHP.md` §E).
