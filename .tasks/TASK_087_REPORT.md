# TASK_087 — build `p19`: report

**Role: research engineer.** **UNREVIEWED** — `TASK_087_REVIEW` attacks it next;
per PROTOCOL rule 9 nothing here enters `.memory/` until then, except where
marked manager-verified.

**`patterns/p19-state-machine/` is built, gated `PASS`, measured, `0 STALE`
tree-wide.** 13 committed files plus `results/p19-state-machine.json`,
`results/gate/p19-state-machine.json`, `results/tables/p19-state-machine.md`.

**PROTOCOL rule 2 running count: 241 → 245.** ⚠⚠ **All four contradictions are
of numbers the MANAGER wrote into `.memory/06-catalogue.md`'s p19 row from
`TASK_086`'s probe. Three of them were wrong.**

---

## §0 — the kill risk: the row is BUILT, and the framing is CONDITIONAL with the condition PINNED

A protocol decoder's state index is attacker-reachable out of range **iff**
(1) the transition table is **loaded data** and (2) dispatch is by **indexing**,
not `switch`. **Both settled by runs before any cell existed**
(`.temp/t87/s0_bugclass.c`, 5 runs), and **both are now `forbidden` entries in
the hashed block** — ⚠ **the only entries in the tree that forbid a spelling for
being *safe*.**

**Real precedent, source fetched:** Linux `security/apparmor/match.c` —
`aa_dfa_match_until()` indexes four tables with **no test at all**, licensed by
`verify_dfa()` walking every entry once at policy load. ✅ **Manager-verified
that the fetch is real**: `.temp/t87/apparmor_match.c`, 21 467 bytes, genuine
`SPDX-License-Identifier: GPL-2.0-only` AppArmor header, 5 hits for the two
named functions. **Validate-once-then-index-unchecked *is* p19's R4/R5 rung.**

⚠ **The two CVE IDs the pattern cites — `CVE-2026-23407` and `CVE-2026-23269` —
are NOT manager-verified.** They cannot be checked offline. **The source-code
precedent stands without them; the IDs must be confirmed or struck before
anything cites them outward.** Reviewer: this is a named task.

**Bug class stated up front, as asked:** the tree's **THIRTEENTH `index >= len`**,
nearest sibling **p36**, said in `spec.md`, `README.md`, `NOTES.md` **and**
`c/kernel.h`.

---

## Gate, proof, identity

- `check.py: PASS`, **failures / loud / blocked = 0 0 0**, `complete_run: true`.
- `contract_sha256 db6e6c51…`, recomputed from the shipped file and equal.
- `measure.py --check-stale` → **46 records examined, 0 STALE**.
- **Verus `12 verified, 0 errors`**; `--cfg slb_twin` → **`13 verified, 0
  errors`**. **3 TCB items**, 1 with a contract, twin verified, **both `ensures`
  conjuncts load-bearing, neither `requires` conjunct a tautology**.
- **`identity: unsafe vs verus — O0 `norel` / O3 `exact`**, established **before
  either rung was written**: plain-rustc `&w[0..TBL]` against Verus
  `slice_subrange`, both **235 B `ac3fb207cd05963419d722adcd8b9da2`**, extracted
  from **LINKED** binaries per `TASK_086` #238.

## The cost

Disassembly rates (`body_len / K`), `-O3`, **inline mode `isolated`**:

| | R2 | R3 | R4/R5 | c-gcc | c-clang |
|---|---|---|---|---|---|
| fold instrs / bytes-per-iter | 15 / 1 | 39 / 4 | 35 / 4 | 11 / 1 | 35 / 4 |
| **`Ir` per message byte** | **15.00000** | **9.75000** | **8.75000** | 11.00000 | 8.75000 |

The gate's **independent** marginals reproduce all of it:
`d(Ir)/d(work)` = `15.0000781 / 9.7500781 / 8.7500781 / 11.0001875 / 8.7501875`.
Two-point slopes exact: `(25594−1594)/3840 = 6.25000`,
`(4100−260)/3840 = 1.00000`.

## The manager's three named calls, all measured

- **(a) the framing is not contrived — UPHELD, CONDITIONALLY.** Unconditional it
  is not; the two conditions are now contract pins (§0).
- **(b) `st*256+b` vs `(st&7)*256+b` is a rung distinction — UPHELD, and the
  PROOF is the reason.** After the validation pass, `st < NST` on every path
  reaching the fold, so **`st & 7 == st` identically on every input including
  adversarial ones** — and that equality *is* R5's loop invariant. R2 and R3
  agree on all 8 inputs, gate-checked. **Delete the pass and they become two
  programs.**
- **(c) `+0.999` is the one `and` — CONFIRMED TWICE, and it is exactly
  `1.00000`.** A rolled-vs-rolled control (`-unroll-count=1`) gives R2 15, R3 13,
  R4 12 — **`R3 − R4 = 1.00` rolled *and* unrolled**, so not an unrolling
  artefact. And adding the mask to the **unsafe** rung costs `+1.00024` with a
  39-instruction body, identical to R3's.

## The mechanism, which is worth more than the numbers

`R2 − R4 = 6.25 = 3.00 check + 3.25 foreclosed 4× unroll`. The three rolled
instructions are `cmp $0x8` + `jae` **plus one `mov %rdx,%rax`** — **the checked
spelling must keep `st` live for the compare and cannot destroy it with the
shift.**

⚠ **And the finding to defend: LLVM lowers the bounds check to `cmp $0x8`, a
STATE-RANGE check. Safe Rust's automatic check and the validation pass C omits
are THE SAME PREDICATE — enforced once per access versus once per call.**

## A second result, and it is not about Rust

Validation is **`O(table)` once** (`c-gcc-h − c-gcc = +10242`,
`c-clang-h − c-clang = +5637`, **identical at both inputs** — that is what
*"constant, not slope"* means); the bounds check is **`O(message)`**.
Consequence: **the buggy C rung is 5071 `Ir`/call CHEAPER than unsafe Rust at
`small` and 3569 DEARER at `large`** — difference `2.25·m − 5647`, zero at
m ≈ 2510. **A sign flip that is not about safety.**
✅ **`c-clang-h` and `unsafe` are within 5 `Ir`/call at both inputs** (0.06 % /
0.011 %) — **finding 7 again, now on a data-dependent loop.**

## Both sides searched — §3's trap

**R2 3 levers (spread 12 `Ir`/call), R3 3 (11), R4 3 (13)** at m=4096 —
**comparable counts, and all three DEGENERATE**, so the headline does not depend
on which is shipped. In contract and *dearer*: R3 branch-clamp **+8.25/byte**
(dearer than the check it replaces), R4 absolute indexing **+2.25/byte**, R3
absolute indexing **+10.87/byte**. ✅ **The rejected R4 was put through Verus
FIRST (`8 verified, 0 errors`) and rejected on cost, not admissibility.**

## Harm — three inputs one byte apart

`gen.py` asserts the distance; `model.py` **computes** `sanitizer_expect`.

| table entry | behaviour |
|---|---|
| **8** | in-bounds, exit 0, **ASan clean** |
| **10** | **`heap-buffer-overflow`, "5 bytes after 2560-byte region"**, names `slb_head1_u64_bytes driver.c:157` |
| **255** | **`SEGV on unknown address`**, *"can not provide additional info"* |

**All three silent at plain `-O2` on 8/8 C cells.**

## PROTOCOL rule 6

First hash `177d47841871d90c589d083111f84cf0f94f714a6d3a83588a77edd8a10e5c35`,
**recorded before `build.py` was ever invoked**; shipped `db6e6c51…`. **It moved
once**: `forbidden[2]`'s explanation had stray backticks around `` `off` `` and
`` `buf.len()` ``, **which `idiom_audit` reads as forbidden spellings** — 4 gate
failures. The edit removed those two pairs and added one sentence; **no
`required` entry, no forbidden spelling, no obligation count, no identity level
and no driver token moved.** ⚠ `git show HEAD: | diff` is **vacuous on a new
pattern** and is **not cited**; NOTES §2 says so.

---

## ⚠⚠ Four contradictions, all of the manager's catalogue row

1. ⚠⚠ **THE HARM IS SILENT, NOT `exit 139 SIGSEGV`.** That was a **storage-class
   artefact** of `TASK_086`'s `harms.c`, which used `static uint8_t TBL[8][256]`
   in `.bss`. **The same read from the heap exits 0.** Run E reproduces both.
   **Do not quote `exit 139` for p19.**
2. **The naive slope is `+6.25 Ir/byte`, not `+5.25`** — the probe's fold was
   `wrapping_add`; p19's is `acc*31 + st`, which needs `st` in a register the
   check also needs.
3. **The *"2-D rows +4.25"* spelling DOES NOT EXIST IN CONTRACT.** `TASK_086`'s
   `k19_rows` got its `&[[u8;256];8]` from an `unsafe` cast **in its driver**;
   with the table arriving as payload bytes the reachable safe reslice measures
   **the same as naive** (67129 vs 67134).
4. **The three-way rung matrix (panic / silent-remap / OOB) is NOT shippable as
   rungs.** It needs three rungs computing three functions on a bad table, which
   costs the R3-vs-R4 boundary — R4 has no sound spelling without the pass, and
   masking to make it sound **collapses R4 onto R3, which is p41's death.**
   Shipped instead as **three inputs one byte apart**, which is strictly more
   informative and costs no boundary.

## Problems

- **First gate run failed 16 rows.** Four `[idiom-forbidden]` (the stray
  backticks above). Nine checksum/agreement rows plus the sanitizer row because
  `degenerate.bin` carried an invalid-table window — ⚠ **the REJ path cannot
  live in a non-adversarial blob**, since an out-of-table entry is exactly what
  makes R1 diverge. Fixed by moving REJ coverage to the adversarial rows;
  `gen.py` carries the reason. One `[identity]` row: R4 written with the inline
  `&buf[off..off+len]` lands at `differ` against R5's `slice_subrange` at O0.
  **Fixed by writing R4's sub-slicing as `fn subrange(…)`; disclosed in NOTES §5
  as "R4's spelling was chosen to match R5's".**
- A stray empty file `=` at the repo root and an unused
  `patterns/p19-state-machine/controls/` — ✅ **both removed by the manager.**

## Unsure / not done

- ⚠⚠ **`results/synthesis.md` and `synthesis/licence.json` were NOT regenerated,
  so p19 is missing from the published aggregate.** Deliberate:
  `.memory/05-layout.md` says the sidecar must be re-emitted **before** the
  artefact or 22 `LICENCE STALE` verdicts publish. ✅ **Done by the manager.**
- ⚠⚠ **`vstd::slice::slice_subrange` is an `#[verifier::external_body]` EXEC
  item and is NOT in the TCB tally.** Measured: **p19 is the only pattern in the
  tree that calls a vstd *exec* trusted function from its kernel** — every other
  hit is a broadcast axiom group or a ghost `spec_slice_len`. ✅
  **MANAGER-VERIFIED both halves**: `grep -l slice_subrange patterns/*/verus.rs`
  returns **p19 alone**, `vstd/slice.rs:107-108` is
  `#[verifier::external_body] pub exec fn slice_subrange`, and p19's gate record
  shows `tcb_items ['buf_get_unchecked','load_input','emit']` — **three, none of
  them vstd's.** ⚠ **So RECAP "Owed" 0's sixth route is no longer hypothetical:
  a published TCB of 3 omits a trusted exec body this kernel actually calls.**
  It does not settle what the column *should* say.
- **The sweep band's laws are not re-fitted from the committed blobs.**
  `R2−R4 = 6.25·m − 8` and `R3−R4 = 1.00·m − 2` come from the probe at 5 lengths
  (zero residual); the band **ships** (19 lengths, all residues mod 4 and mod 8)
  so they *can* be re-derived from a hashed generator, **and nobody has.**
- **No wall-clock analysis.** The fold is a serial dependent-load chain, so `Ir`
  should **understate** the safe rungs' penalty — **a prediction, not a
  measurement.**
- **`spec.md` is hand-maintained, not generated.** `.temp/t87/mkspec.py` is a
  one-shot; re-running it would revert later edits (**the p27 accident**). The
  file says so at the top.
- **Three `required` "pins nothing" rows are stray backticks in prose**, left
  deliberately and documented in NOTES §4 — fixing them would move
  `contract_sha256` a **second** time to remove three benign report rows.
- Did **not** touch `harness/build.py`, `harness/asm.py`, `.memory/`, `pilot/`,
  or any other pattern; ran `check.py p19` only, **never a sweep**; no `git
  add`/`commit`.

## Memory updates owed (manager applies, AFTER review)

1. **The catalogue's p19 harm row**: `exit 139` → **silent**, plus the
   three-input family. ✅ **Landed immediately** — it was a wrong number the
   manager had written.
2. `.memory/03-measurement.md`: **an OOB read's loudness is set by the object's
   STORAGE CLASS** — `.bss` array vs heap, same read, `SIGSEGV` vs exit 0.
3. `.memory/02-bench-rules.md`: ⚠ **a stray backtick in an `idiom` entry's
   PROSE is audited as a pinned spelling.** It failed 4 rows here and **is a
   live trap for every future pattern.**
4. The `#[trigger]` paren trap and the other three Verus sticking points
   (NOTES §6).
