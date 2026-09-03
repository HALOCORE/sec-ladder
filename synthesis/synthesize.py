#!/usr/bin/env python3
"""The cross-pattern synthesis: `results/synthesis.md`.

`CLAUDE.md` describes this project as patterns *"compared on assembly,
instruction count, timing, proof burden and trusted-base size"*.  Until now
there were 22 per-pattern tables under `results/tables/` and nothing that
compared them (RECAP "Owed" 13).  This is that comparison.

    synthesis/synthesize.py                 # -> results/synthesis.md
    synthesis/synthesize.py --stdout        # to the terminal instead

WHY THIS DIRECTORY.  `harness/check.py::main` hashes
`harness/*.py`, `common/*.py`, `common/layout/*.py`, `patterns/pNN/*.md`,
`patterns/pNN/model.py`, `patterns/pNN/controls/*.py`, `patterns/pNN/inputs/gen.py`,
`common/driver.*` and `verus_run.py` into every gate record's `source_sha256`;
`harness/measure.py::provenance` hashes a subset of the same list into every
MEASUREMENT record.  A file in any of those places stales 22 gate records (and,
for `build/asm/measure.py`, 22 measurement records, which forces a re-measure
that re-takes the wall-clock block).  `synthesis/` is in neither glob, and so is
`results/synthesis.md` -- verified by evaluating both globs literally, not by
reading the docstring that describes them.

WHAT IT READS.  Committed records: `results/pNN-*.json` (measurement) and
`results/gate/pNN-*.json` (gate).  It never builds, never runs a compiled
binary and never writes a record.

⚠ **THE CALLEE CORRECTION IS DERIVED FROM COMMITTED RECORDS** -- see
`CALLEE_NOTE`.  An earlier version of this file printed *"the licence is not in
the committed records and cannot be derived from them"*, which was false:
`results/gate/pNN.json::marginal_ir_per_call` is whole-program and therefore
symbol-independent, so `(marg[A]-marg[B]) - (kex[A]-kex[B])` is the callee
correction, from files already in `git` (TASK_075_REVIEW B1;
`.memory/03-measurement.md`, which prescribed exactly this test).

Three things here are NOT derived from a record, each declared where it prints:

  * the LICENCE TAG (`synthesis/licence.json`) -- a disassembly property, a
    different question from the magnitude, and pinned to the gate
    `source_sha256` it was taken against;
  * the CALIBRATION of the derived column against a callgrind sweep
    (`synthesis/outward_ir.json`) -- evidence for the floor, not a column;
  * the REVIEWED SEARCH VERDICT (`SEARCH_REVIEWED`), beside a *derived* control
    census this file computes by running each pattern's `controls/*.py --list`.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(REPO, "results")
GATE = os.path.join(RESULTS, "gate")
HERE = os.path.dirname(os.path.abspath(__file__))
LICENCE = os.path.join(HERE, "licence.json")
OUTWARD = os.path.join(HERE, "outward_ir.json")

RUNGS = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]
PAIRS = [("safe_naive", "unsafe", "R2-R4"),
         ("safe_tuned", "unsafe", "R3-R4"),
         ("verus", "unsafe", "R5-R4"),
         ("c-gcc", "c-clang", "gcc-clang")]
# The gate records one `identity` entry per compared pair; p01 ships two at
# `-O3`.  Anything about "the proof costs zero instructions" is about this one.
R5_PAIR = "unsafe vs verus"

# ⚠ **THE SAME PATTERN'S TWO-NESS BITES A SECOND COLUMN, AND THIS PIN IS THE
# DISCLOSURE.**  `§3`'s proof-burden row reads ONE Verus source per pattern.
# The line below used to be a bare `.get("verus.rs")` inline, with no comment,
# no constant and nothing that would notice a second source appearing —
# exactly the shape `R5_PAIR` was introduced for one column earlier
# (TASK_075_REVIEW m6).
#
# **p01 pins TWO Verus sources** and is the only pattern that does (checked
# across all 22 gate records, TASK_084):
#
#     safe_naive_verus.rs   7 verified   TCB ['load_input', 'emit']
#     verus.rs              7 verified   TCB ['get_unchecked', 'load_input', 'emit']
#
# **Reading only `verus.rs` is CORRECT and summing would be wrong**, so this is
# a disclosure, not a repair: `safe_naive_verus.rs` is the R2v control that
# proves the *safe naive* rung panic-free (`.memory/01-ladder.md` finding 2,
# *"a proof alone buys nothing"*).  Its trusted base is not R5's, and adding
# the two would publish a trusted-base size that describes no rung on the
# ladder.  The column is R5's, and `TCB_SRC` says so.
#
# ⚠ **What the silence already cost, measured at TASK_084:** with two
# candidate totals in the tree — 90 over `verus.rs` and 92 over every source —
# four documents quote **92** *as the published total* (`RECAP.md:1798`,
# `.tasks/TASK_082.md:195`, `.tasks/TASK_083.md:26` and
# `.tasks/TASK_083_REVIEW_REPORT.md:268`, the last of them naming this very
# table), while this file has published **90** since it was written.  So the
# table now also emits a DERIVED footnote naming every additional Verus source
# it did not read, per pattern — which is the part that will still work when a
# second pattern grows a second source.
TCB_SRC = "verus.rs"

# --------------------------------------------------------------------------
# The search state.  TWO columns, because neither alone is honest.
#
# `R3 - R4` differences two rungs whose spellings have been searched to wildly
# different depths.  A table that puts a well-searched pattern beside an
# unsearched one and differences both is partly measuring SEARCH EFFORT, and
# the tree has three measured instances of the difference moving a long way
# when a side was finally searched.
#
# ⚠ TASK_075_REVIEW M6 prescribed DELETING the declared table and deriving the
# lever count from `controls/*.py --list` for "the 10 patterns that expose one".
# **MEASURED (`.temp/p76/list_parse_probe.py`): that cannot be done.**  Ten
# patterns expose a `--list` and only FIVE of them print a source file at all:
#
#     from <file>.rs   p10 p47          <- <file>.rs   p03 p04 p12
#     NO source column p06 p09 p22 p36 p38
#
# and p36 -- the pattern the review cited as the worked example -- is in the
# second group: its `--list` prints `r3_hdr4  rust`, the LANGUAGE, not the file.
# Deriving p36's split from the `r3_`/`r4_` NAME PREFIX instead gives 4 R3 and
# **2** R4, while `.memory/01-ladder.md` finding 23 says **3** R4 -- i.e. the
# derivation-by-convention rots in the same direction the hand table does, and
# less visibly.  So: DERIVE what is derivable (`control_census`, below, which
# degrades to "no source attribution" and can never print a wrong count), and
# keep the reviewed verdict beside it with every entry cited to a REVIEWED
# artefact.  A pattern with no entry prints `undeclared`, which is its true
# state and not a default.
#
# ⚠⚠ AND `undeclared` HAS NEVER MEANT "NOBODY SEARCHED" -- it means nobody
# wrote an entry, and at TASK_112 four patterns with REVIEWED search results in
# `.memory/01-ladder.md` were printing `undeclared` (TASK_111 adjacent work 1,
# which named p22, p17 and p06; p12 was found while landing it).  Two of the
# four were being quoted in `results/SYNTHESIS.md` §2 inside a bucket labelled
# "flat in the size of the data" -- one of them (p22) at a value this project's
# retraction record puts 510x off.  So: when a pattern's `.memory/` entry gains
# a searched R3 or R4 spelling, ADD IT HERE IN THE SAME PASS.
#
# One entry, `p06`, is marked ⊘ because the authoritative layer marks it ⊘: it
# landed at TASK_048 and has not been through a second review.  Label, do not
# omit and do not silently promote.
# --------------------------------------------------------------------------
SEARCH_REVIEWED = {
    "p01": ("R3 span OWED",
            "RECAP 'Owed' 3: p01 and p08 owe an in-contract R3-side span"),
    "p03": ("R3 span 1 unreviewed measurement; the +5 constant NEVER searched",
            "RECAP 'Owed' 2"),
    "p06": ("⊘ PROVISIONAL -- R3 searched at review: `c_idx` is 0.00000 "
            "Ir/BYTE, and on `small` it is +80.00 against a shipped +334.00. "
            "⚠ On `large` the SHIPPED R3 (+172) is the CHEAPER of the two",
            ".memory/01-ladder.md p06, where this bullet is marked ⊘ -- it "
            "landed at TASK_048 and HAS NOT been through a second review, so "
            "it is the one entry in this table that is not twice-checked. The "
            "measurement is TASK_047_REVIEW_REPORT.md B2: `c_idx` (R3's "
            "two-step reslice and iterator fold with R2's indexed swap) is in "
            "contract, contains no `unsafe`, agrees with the model on four "
            "inputs, and its `c_idx - unsafe` is 105.00 at BOTH ends of band M "
            "(sum_m 64 and 384) -- 0.00000 Ir per byte against the shipped "
            "R3's 2.00000. ⚠ `105 flat` is a BAND-M figure and not a shipped-"
            "blob one: out of sample the parameter-free law predicts +80.00 "
            "(small) and +187.00 (large), both measured exactly, and p06's "
            "cheapest-found in-contract R3 therefore DIFFERS BY BLOB. None of "
            "the shipped R3's 2.00 Ir/byte is a bounds check -- it is the "
            "zip/Rev adaptor's two exhaustion tests per item, and `pads.py` "
            "gives both spellings identical 11 panic pads at identical "
            "line:col"),
    "p08": ("R3 span OWED",
            "RECAP 'Owed' 3"),
    "p10": ("R4 searched at review: -323/-603 becomes -129/-241",
            ".memory/01-ladder.md finding 18 (p10): the rejected R4 candidate "
            "`u_win` verifies 10/0; `R3ship - u_win` is -129.00/-241.00, i.e. "
            "60% of the published margin was R4 SPELLING"),
    "p11": ("R4 chained to the prover; `r4_cstr` inadmissible",
            ".memory/01-ladder.md finding 9 (p11): `r4_cstr` would be "
            "-17 526 Ir/call and its twin is rejected with four "
            "`is not supported`"),
    "p12": ("R4 searched at review: the SIGN FLIPS on `large` to +66.00",
            ".memory/01-ladder.md p12: p12 called its pair interval degenerate "
            "on an INFERENCE; TASK_040_REVIEW BUILT the cheaper R4 (route A), "
            "which verifies 15/0, twin 18/0, holds `R4 = R5 exact` and is "
            "17.00/92.00 cheaper -- so the shipped R3 is +66.00 DEARER than "
            "the cheapest-found verifying R4 on `large`, and the published "
            "-26.00 is a fixed-R4 figure. ⚠ Added at TASK_112: this row printed "
            "`undeclared` although the search is reviewed and moved the sign"),
    "p13": ("R4 searched: the SIGN FLIPS to +44/+77",
            ".memory/01-ladder.md finding 14 (p13): a bounded unchecked "
            "consumer verifies 19/0 with no new trusted item and is excluded "
            "by nothing but spec.md's English"),
    "p17": ("R3 searched: an in-contract respelling is -19.00 flat; "
            "`+32` is NOT a law (swept 18...63)",
            ".memory/01-ladder.md p17 (TASK_018, reviewed at "
            "TASK_018_REVIEW): an in-contract respelling keeping `let start: "
            "i64`, `let end: i64` and the literal `if start < end && start >= "
            "0` measures -19.00 flat against the shipped R4 on both bands and "
            "is BYTE-IDENTICAL (md5_fn 532201c70eeb.., 135 instructions) to a "
            "row an earlier task had declared out of contract. ⚠ It is an "
            "R3-SIDE bound with R4 held by fiat, emphatically not 'safe beats "
            "unsafe'. And the published `+32 flat` is retracted AS A LAW: both "
            "shipped bands sit at nsuf = 3, and swept over nsuf 1-8 "
            "`R3ship - R4` runs 18...63. p17 ships no sweep inputs"),
    "p22": ("R4 searched: `+2.00` is a fixed-R4 bound; against `r4_reslice` "
            "the gap is +125/+1021 -- 510x on `large`",
            ".memory/01-ladder.md finding 22 (p22), reviewed at "
            "TASK_070_REVIEW which re-measured it end to end: `r4_reslice` is "
            "R4 plus R3's one reslice, in contract, same checksum on all 8 "
            "inputs, `20 verified, 0 errors`, and its R4/R5 pair is "
            "byte-identical at -O3 (md5_fn ea06db04c435 both sides, built and "
            "diffed). It is 1*nkw - 5 cheaper than the shipped R4, so "
            "`R3ship - r4_reslice = 1*nkw - 3` = +125.00 / +1021.00. The R4 "
            "was NOT re-shipped (.memory/02-bench-rules.md), so both numbers "
            "publish. ⚠ Added at TASK_112: this row printed `undeclared` while "
            "§6 of results/SYNTHESIS.md reported the 510x retraction"),
    "p36": ("BOTH sides searched (4 R3 levers, 3 R4)",
            ".memory/01-ladder.md finding 23 (p36): publishes +7.00 flat "
            "(fixed-R4 bound, cheapest R3 found) and +10.00 flat (matched "
            "pair), never a single number, and NO pair interval"),
    # ---------------------------------------------------------------------
    # ⚠⚠ TASK_166 item E. THE SEVEN ROWS ADDED AFTER TASK_112 ALL PRINTED
    # `undeclared`, and the growth `14 of 26 -> 21 of 33` was ENTIRELY those
    # seven -- the 14 old undeclared rows are exactly the published 14. Four
    # of the seven had a REVIEWED search and no entry (`p25 p28 p34 p35`);
    # three had a REVIEWED DECLARATION OF NO SEARCH (`p29 p32 p49`, listed in
    # `SEARCH_NONE` below), which `undeclared` also fails to distinguish from
    # "nobody wrote an entry". ⚠ **`p49` ships `controls/spellings.py` and it
    # is NOT a rung-spelling search** -- it is the `cow`-vs-`provenance` REPAIR
    # SITE control on the C kernel -- so inferring an entry from the presence
    # of that filename would have produced a WRONG entry here.
    "p25": ("the repair SITE searched (three); one respelling lever per READ "
            "site measured EQUAL to the hundredth. R3/R4 rung spellings and "
            "the GROWTH-site repair spelling still unsearched",
            "`patterns/p25-realloc-growth/NOTES.md` §3c, REVIEWED at "
            "TASK_158 §4b, which built a ternary spelling of R1h and a "
            "`*(toks + curi)` spelling of `rederive` and found both equal to "
            "their originals **to the hundredth at every cell** — so neither "
            "shipped figure is a spelling artefact on that lever. ⚠ The file "
            "names the weaker-searched endpoint itself: the spelling of the "
            "GROWTH-site repair (`fixup2`) was not searched"),
    "p28": ("R2-vs-R3 searched at review: the WALK HOIST is 72% of the gap, "
            "and it is a FOURTH lever `safe_tuned.rs`'s own header omits",
            "`patterns/p28-intrusive-lists/NOTES.md` §8, `TASK_149` "
            "deliverable 4 (`.temp/t149/lever/`), resolved at TASK_150: three "
            "variants, identical checksum on every probe, and un-hoisting the "
            "walk recovers **72%** of the `R3 − R2` gap on `small.bin` and "
            "57% on the GET-miss probe; on the TRIM path R3 is genuinely 5% "
            "cheaper. ⚠ p28 publishes NO rung-to-rung cost (§8) and the "
            "absence is declared, so this is a search result without a "
            "published figure attached to it"),
    "p34": ("BOTH sides searched, and the control caught a flattering-"
            "direction headline BEFORE any review: the `-O0` shipped-pair gap "
            "was 2.88×/3.36× too large",
            "`patterns/p34-refcount-stack/NOTES.md` §5 and "
            "`patterns/p34-refcount-stack/controls/spellings.py`, REVIEWED at "
            "TASK_155: `r3_cursor`, `r4_checked` and `r4_readdirect` are "
            "built by text substitution from the shipped rungs. `r4_readdirect` "
            "ties the shipped R4 exactly at `-O3` and beats it by "
            "116.13 / 611.10 at `-O0` **and verifies at the pinned obligation "
            "count**, so p34 is the first pattern with more than one R4 "
            "spelling SHOWN admissible and a measured R4-side width "
            "(53.02 / 267.42 at `-O3`). The weaker-searched endpoint is named: "
            "the C side, which had no spelling search at all"),
    "p35": ("R4 searched at review: the SIGN REVERSES — matched on the "
            "op-walk R4 WINS by 203.05 `Ir`/call (6.63%) on `large`",
            "`patterns/p35-tagged-union/NOTES.md` §1(iii), TASK_152 M1 "
            "(the first flattering-direction headline caught by a review "
            "pointed at it on purpose) and the four-arm rig re-run at "
            "TASK_153 (`.temp/t153/rig/measure_rig.py`) with both shipped "
            "rungs as controls that reproduce `results/gate/` exactly. The "
            "published `R3 − R4 = −170.56` is withdrawn; what the pin costs "
            "R4 is **373.61 `Ir`/call (11.56%)**. ⚠ And the same pair of "
            "levers is **−373.61 at `-O3` and +6035.46 at `-O0`**"),
    "p29": ("⊘ NO SEARCH, declared — NEITHER side searched, and the row "
            "publishes no rung-to-rung cost at all",
            "`patterns/p29-bst-delete/NOTES.md` §8, REVIEWED at TASK_140: "
            "*\"No cost axis is published … Neither side was searched. The "
            "measurement record exists and the numbers are in it; nothing "
            "here reads them.\"* ⚠ Three R4 spellings WERE built and counted "
            "for the `-O0` **identity** question (§5) and none matches — that "
            "is an identity search, not a cost search, and it licenses no "
            "figure"),
    "p32": ("⊘ NO SEARCH, declared — NEITHER side searched, no cost axis, and "
            "the four unmeasured R2/R3 levers are named for the next task",
            "`patterns/p32-free-list-pool/NOTES.md` §7, REVIEWED at TASK_145 "
            "(verdict STANDS): *\"p32 SHIPS WITH NO COST AXIS. THE ABSENCE IS "
            "DECLARED, NOT A MEASURED ZERO … That search was not done, on "
            "either side.\"* The four levers left open are the flat "
            "`[u8; 32]` pool vs `[[u8; 4]; 8]`, the NIL-sentinel register "
            "pair vs `Option<(u8, u32)>`, re-widening `h as usize` per use, "
            "and an `if` chain vs a `match`"),
    "p49": ("⊘ NO R3-SIDE SPREAD — only ONE in-contract R3 spelling built, so "
            "there is not even a second point to bound a spread with",
            "`patterns/p49-interned-pool/NOTES.md` §5 and §10, REVIEWED at "
            "TASK_162: the R2/R3 sign REVERSES with the level (R3 +27.05% at "
            "`-O0`, −5.81%/−9.18% at `-O3`), and the file states that no "
            "R3-side spread is published because a second spelling was never "
            "built. ⚠⚠ **`patterns/p49-interned-pool/controls/spellings.py` "
            "is NOT a rung-spelling search** — it is the `cow`-vs-"
            "`provenance` REPAIR-SITE control on `c/kernel.c`, which is why "
            "this entry does not claim one"),
    "p47": ("R4 searched, six levers",
            "`patterns/p47-ct-compare/NOTES.md` §8e, REVIEWED — \"Six R4 "
            "levers were built, each measured and put through "
            "`./verus_run.py`\" — and §8e's table has six rows: `unsafe` "
            "shipped, `u_base`, `u_winu`, `u_end`, `u_win`, `u_ptr`. "
            "`gen_controls.py --list` registers five `from unsafe.rs`; the "
            "sixth is the shipped rung. ⚠ TASK_075_REVIEW M6.3 read this as "
            "four and called the number unsupported; it is supported, and the "
            "citation — not the figure — was what was wrong"),
    # ---------------------------------------------------------------------
    # ⚠⚠⚠ TASK_170 item B / RECAP queue item 35. THE FOURTEEN ROWS THAT HAD
    # PRINTED `undeclared` SINCE 26 PATTERNS WERE READ AGAINST THIS DICT --
    # every `NOTES.md` in full, every `.memory/01-ladder.md` section, every
    # `controls/` header, and the reviewing task report -- and
    # **ALL FOURTEEN HAD A REVIEWED SEARCH.** Zero were a reviewed declaration
    # of NO search; zero were genuinely undeclared. So `undeclared` falls
    # 14 -> 0 and the column is fully declared at 33.
    #
    # ⚠⚠ THAT IS THE STRONG FORM OF TASK_112's AND TASK_166's FINDING, NOT A
    # NEW ONE: this column has NEVER been a measure of search effort. Its
    # `undeclared` was 100% bookkeeping, on both audits, at every size.
    #
    # ⚠ AND THE FILENAME DETECTOR WOULD HAVE MISSED ALMOST ALL OF THEM.
    # Only p42 of the fourteen ships a `controls/spellings.py`; p14, p16, p18,
    # p07, p09 and p38 put the rung search inside `controls/gen_controls.py` or
    # `controls/span.py`, and **p19 and p23 ship no committed spelling probe at
    # all** (their levers were built in gitignored scratch and are recorded only
    # in prose). Meanwhile p23's `controls/guard_variants.c` and p38's
    # `controls/gen_controls.py` C-side family are repair-site controls, the
    # `p49` false-positive shape. **Reading, not grepping**, is what this cost.
    # ---------------------------------------------------------------------
    "p02": ("R3 searched and SWEPT over 16 consecutive lengths: the fixed-R4 "
            "bound falls +10 → **+6** on both shipped blobs. ⚠ The R4 side is "
            "explicitly UNsearched, so +6 is an R3-side bound",
            "`patterns/p02-buffer-copy/NOTES.md` §10a (TASK_019, forced by "
            "TASK_018_REVIEW M1), REVIEWED at TASK_023_REVIEW minor 10, which "
            "works the figure and confirms the file states it correctly — and "
            "whose own *\"what I did not do\"* names p02's R4 side as the next "
            "target. Five variants, three in contract; the cheapest "
            "(`r3_hdrslice`, the `u16` header read out of a 2-byte reslice) is "
            "−4/−3 against the shipped R3 with ZERO residual on all 16 swept "
            "lengths. ⚠⚠ And it BEATS the forbidden additive guard at 14 of 16 "
            "lengths and ties at 2, so **p02's exclusion costs its published "
            "floor nothing** — the opposite of p16, where the exclusion made "
            "the tax 4.5× larger"),
    "p04": ("BOTH sides searched — 16 R3 candidates, 3 R4 with Verus twins: "
            "the tightest in-contract bound is **+4.00**, not the shipped "
            "+5.00, so 20% of the whole published tax was R3 SPELLING",
            "`patterns/p04-ring-buffer/NOTES.md` §10a/§10b/§13c, REVIEWED at "
            "TASK_042_REVIEW blocker 1 (16 candidates, each verdicted by "
            "`check.py::spelling_matches` AND by `model.py` on all five matrix "
            "inputs), landed at TASK_044 and recorded in "
            "`.memory/01-ladder.md` finding 13. Six in-contract spellings "
            "across FIVE distinct machine codes measure 3367/11666 against the "
            "shipped 3368/11667; the mechanism is REGISTER ALLOCATION, not "
            "bounds-check removal. Both numbers publish — `+5.00` fixed-R4, "
            "`+4.00` cheapest-found — and §13c records the decision NOT to "
            "re-ship. R4: `r4_forloop` and `m_clamp_unsafe` are both "
            "`9 verified, 0 errors` and BYTE-IDENTICAL to the shipped R4, so "
            "the R4 endpoint has zero measured width. ⚠ The cheaper R3 has "
            "MORE panic pads (2 vs 1) — pad count is not the tax"),
    "p05": ("BOTH sides searched hardest in the project (11 R3 spellings, 46 "
            "R4 over three rounds): R3-side span 101…127 / 331…403 against a "
            "published 123/399, and the R4 side has NEVER moved by an "
            "admissible instruction",
            "`patterns/p05-index-flatten/NOTES.md` §13, §14 and §14f, REVIEWED "
            "at TASK_021_REVIEW (blocker B1), re-searched at TASK_022, and the "
            "R4 half WITHDRAWN at TASK_027_REVIEW/TASK_028 on seven Verus "
            "twins; `.memory/01-ladder.md` finding 6 uses p05 as its canonical "
            "worked example of the three quantities. ⚠⚠ THREE successive "
            "published *minima* (`5·nrow+6` → `5·nrow+11` → `5·nrow+13`) were "
            "each overturned by the next agent's FIRST lever, and each had "
            "been reached by several independent `md5_fn` bodies — *\"reached "
            "by many spellings\"* is not evidence of a floor. ⚠ Every R4 "
            "spelling that moves respells the header read and needs "
            "`read_unaligned`/`as_ptr`/`from_raw_parts`/`TryFromSliceError`/"
            "`from_le_bytes`, each `is not supported` at the pinned vstd, so "
            "those rows are NOT MADE OF RUNGS"),
    "p07": ("BOTH sides searched: the cheapest in-contract R3 is +2554.45 / "
            "+8412.35 against a shipped +3017.14 / +10019.42 — a span of "
            "EXACTLY 1.0000 `Ir` per probe. R4 degenerate; its one admissible "
            "respelling is DEARER",
            "`patterns/p07-binary-search/NOTES.md` §10a/§10b, built by "
            "`controls/gen_controls.py` (`r3_getunwrap`, `r3_prefix`, "
            "`r3_splitat`, `r3_win`, `r4_for`, `r4_ptr`), REVIEWED at "
            "TASK_026_REVIEW — *\"reproduces §10a/§10b/§11a to the "
            "instruction\"* — whose minor 4 caught that `r4_for`'s "
            "admissibility was an INSPECTION standing beside somebody else's "
            "Verus run and BUILT the missing twin (`10 verified, 0 errors`); "
            "landed at TASK_029, recorded in `.memory/01-ladder.md` finding 8. "
            "The admissible `r4_for` is +58/+92 DEARER and `r4_ptr` dies on "
            "*\"dereferencing a raw pointer\"*. ⚠ The one OUT-of-contract R3 "
            "(`r3_win`) is dearer than the cheapest in-contract one, so unlike "
            "p05 and p16 **p07's declaration is demonstrably not protecting a "
            "number**"),
    "p09": ("R3 searched: a **65×** R3-side span (+263…+16992 / +854…+58953) "
            "against a published +13756 / +48885 — the SPELLING axis alone is "
            "+13493 `Ir`/call on `small`. R4 searched and degenerate",
            "`patterns/p09-bitset/NOTES.md` §10a and §3's three-factor table, "
            "built by `controls/gen_controls.py` family 3 and verdicted in "
            "contract by `check.py::spelling_matches`, REVIEWED at "
            "TASK_038_REVIEW: *\"Every marginal `Ir` in NOTES 3/6b/8/8a/10a "
            "reproduced to 0.01\"* and *\"`spelling_matches` on every control: "
            "all seeding and R3-span controls in contract; `r3_wordchunks` "
            "out, as NOTES says\"*. ⚠⚠ The 65× span is the WIDEST in-contract "
            "R3 spread on this project, and p09 prices the SPELLING factor "
            "(+13493) beside the LIBRARY one (+29.00 `Ir`/word) so neither is "
            "mistaken for the safety one. ⚠ `r3_best`'s cheapness comes from "
            "`chunks_exact(4)`, `is not supported` at the pinned vstd — so "
            "+263 is a number no R4 could answer with (R4-by-permission "
            "again). ⚠ The R4 half is the weaker one: `m_clamp_u` (+241) and "
            "`m_clampb_u` (+721) both RAISE R4 and every route to a wider load "
            "is unsupported AND `idiom.forbidden`, but neither candidate had a "
            "Verus twin BUILT the way p04's and p07's did, and the review "
            "names its own limit: *\"did not attempt an in-contract R3 cheaper "
            "than `r3_best`, nor re-search R4\"*"),
    "p14": ("R3 searched (3 in-contract spellings): on `large` the shipped "
            "cell **OVERSTATES the safe-side figure by 88.9%** — +425.00 "
            "becomes +225.00. ⚠ The R4 side was never searched",
            "`patterns/p14-field-split/NOTES.md` §8a/§8a′, a commissioned "
            "TASK_049 deliverable (*\"two in-contract R3 spellings, and quote "
            "the cheaper\"*), REVIEWED at TASK_049_REVIEW, whose clean "
            "negative 7 re-measured 8 cells × 10 blobs independently and "
            "reproduced `R3 − R4 = +638.00/+425.00`, and whose clean negative "
            "11 direction-tested both out-of-contract fiats and found both "
            "against p14's interest. In-contract span `4291.99…4488.99` "
            "(small) / `2406.99…2607.99` (large). ⚠ THE CHEAPEST SPELLING IS "
            "NOT THE SAME ONE ON BOTH INPUTS — `t_idxfold` wins on `large`, "
            "the shipped iterator fold on `small`. ⚠ The only `u_*` control is "
            "`u_nocap`, a delete-the-check row, so the R4 endpoint is fiat"),
    "p16": ("BOTH sides searched and the SIGN FLIPS: a published `R3 − R4` of "
            "+27/+77 becomes **−199 (small) / −2545 (large)** against the "
            "cheapest-found in-contract R3. The R4 side was searched and its "
            "one mover DISQUALIFIED",
            "`.memory/01-ladder.md` finding 4 (p16) and "
            "`patterns/p16-tlv-walk/NOTES.md` §10a (TASK_018, promoted to a "
            "SWEPT law at TASK_018_REVIEW — 11 `nrec` values × 2 residue "
            "classes, 110 marginals, zero residual), §10a.1 (TASK_023, the R4 "
            "side) and §10a.2 (corrected at TASK_025_REVIEW / TASK_027). The "
            "in-contract R3 spread is 42 `Ir`/call at `large` (−32 … +10) "
            "against a published 77 — 55% of the tax. ⚠ THE R4 MOVER IS NOT A "
            "RUNG: `r4_hdr` needs `read_unaligned`, `is not supported` at the "
            "pinned vstd, withdrawn at TASK_028 — *\"neither pattern's R4 side "
            "has moved by a single admissible instruction\"*. ⚠ NO SINGLE "
            "SPELLING IS CHEAPEST ON BOTH BLOBS: `chunks_exact(64)` is 72 "
            "dearer at `small` and 180 cheaper at `large`"),
    "p18": ("R3 searched, 3 in-contract spellings, and the SHIPPED one is the "
            "cheapest — span width **1.00 `Ir`/call, the narrowest published**, "
            "so nothing moves. ⊘ The R4 side is NOT searched, declared",
            "`patterns/p18-varint-shift/NOTES.md` §8d, REVIEWED at "
            "TASK_051_REVIEW clean negative 11, which reproduced every cell: "
            "shipped R3 2307.00/890.00, `t_1step` +1.00, `t_chain` 0.00, and "
            "the out-of-contract `t_iter` −101.00 on `small` but DEARER on "
            "short varints. ⚠ This is a searched NULL, not an absence — which "
            "is why it is not in `SEARCH_NONE`. The R4 half IS a declared "
            "absence, in `.memory/01-ladder.md` finding 17 and in RECAP's "
            "*Owed*: *\"p18 publishes no pair interval and its R4 side is "
            "unsearched in contract\"*. ⚠ Every price in §8d is a "
            "`cut == 0, brk == 0` law — the controls were never re-swept over "
            "band `t` (§8d, §12, RECAP *Owed*) — so the span is stated on the "
            "benign fully-terminating domain only"),
    "p19": ("BOTH sides searched, 3 levers a side, and ALL THREE SIDES ARE "
            "DEGENERATE — spreads 12 / 11 / 13 `Ir`/call at m = 4096, so "
            "neither published `R3 − R4` (+4094) nor `R2 − R4` (+25592) "
            "depends on which spelling ships",
            "`patterns/p19-state-machine/NOTES.md` §10 (*\"Spelling spread — "
            "and BOTH sides were searched\"*), REVIEWED at TASK_087_REVIEW, "
            "which built TWO MORE in-contract R2 spellings that measure "
            "exactly the shipped R2's numbers (one byte-identical) — *\"five "
            "R2 spellings now, all degenerate\"* — and rebuilt R4 WITHOUT the "
            "identity pin's sub-slice to a byte-identical kernel at an "
            "identical marginal 41516.3000, so **the pin costs R4 nothing at "
            "the measured level**. §10 also prices the in-contract-and-DEARER "
            "levers (R3 branch clamp +8.25 `Ir`/byte; absolute indexing +2.25 "
            "R4 and +10.87 R3, the latter because the check comes back), and "
            "the rejected absolute-indexing R4 went through Verus FIRST "
            "(`8 verified, 0 errors`) — rejected on cost with admissibility "
            "established. ⚠ p19 ships no `controls/`, so the levers are "
            "scratch and only the review re-measured them; and §10's absolutes "
            "are a probe binary's, which §12 says and keeps"),
    "p23": ("BOTH sides searched and the two spans OVERLAP: the in-contract R3 "
            "floor fell 150.00 `Ir`/call to 2991.00 — **59.00 BELOW an "
            "in-contract R4** — and the headline ratio went 3.11× → 1.3148×",
            "`patterns/p23-partition/NOTES.md` §9b/§9b′, `.memory/"
            "06-catalogue.md`'s p23 row and RECAP finding 38. ⚠⚠ The floor was "
            "found BY THE REVIEW (TASK_105 M5, *\"the published R3-side span's "
            "FLOOR is wrong by 150 `Ir`/call\"*) and settled AGAINST the "
            "headline at TASK_106: `k_u5` restores the pinned conjunct as a "
            "TAUTOLOGY, matches all 8 `required` including the English, and "
            "compiles to the SAME OBJECT CODE as the out-of-contract `k_u1` "
            "(`md5_norm da08af26d9b1`, 249 instructions both). Corrected span "
            "2991.00 … 3719.00 over twelve in-contract spellings against an R4 "
            "span 2876.00 … 3050.00, so **at least 150 of the published "
            "safe-side figure is SPELLING, not SAFETY**. ⚠ The span's TOP "
            "endpoint was wrong too — 4208.00 was `r3b`, which is "
            "`forbidden`. ⚠ The correction is rank-dependent: 338.00 at rank "
            "0, 150.00 at rank 50, 46.00 the other way at rank 100. ⚠ The "
            "probes are gitignored scratch; `controls/` holds only the C-side "
            "guard controls and the sweep fitter"),
    "p27": ("R4 searched at review and THE SHIPPED RUNG MOVED: a dead store "
            "deleted, +223.26/+782.25 → **+230.07/+792.75** — i.e. AGAINST "
            "interest. R3 searched twice; R2 never",
            "`patterns/p27-handle-table/NOTES.md` §8 and §8a, REVIEWED at "
            "TASK_060_REVIEW major 2 — *\"an admissible, verifying, "
            "byte-identical R4/R5 pair exists that is 6.81 / 10.50 `Ir`/call "
            "cheaper, so 'the R4 endpoint is degenerate as far as this task "
            "searched' is now false\"* — and SHIPPED at TASK_061. The deleted "
            "line is the epilogue's `arr_set_unchecked(&mut live, j, 0u8)`, "
            "dead because `live` is a kernel local and `j` only increases; R5 "
            "still verifies 15/0, twin 20/0, `R4 = R5 exact`, checksums "
            "identical on all 7 inputs. `.memory/01-ladder.md` finding 19 "
            "publishes the POST-correction figure. R3 side: two in-contract "
            "spellings, and the cheapest found IS the shipped one "
            "(+9.52/+32.00). ⚠ §11 names the unsearched endpoints itself — the "
            "R2 side, the fold's spelling, the cursor arithmetic and the table "
            "layout"),
    "p38": ("R4 searched and it is NOT degenerate: `r4_slice` is −3.00/−7.00 "
            "below R4ship, so `R3 − inf(R4 found)` is +24.00/+32.00 against a "
            "published +21.00/+25.00 — 14%/28% of the headline, and it "
            "FLATTERS SAFE",
            "`patterns/p38-alias-pun/NOTES.md` §8a/§8b and "
            "`patterns/p38-alias-pun/controls/span.py`, whose own header gives "
            "the motive: *\"'degenerate as far as this task searched' was "
            "false on two consecutive patterns (p10, p27) and both times it "
            "flattered the safe rung\"*. REVIEWED at TASK_066_REVIEW P1, which "
            "re-ran the control and reproduced every number (R3ship "
            "1391.30/3350.00, R4ship 1370.30/3325.00, `r4_slice` −3.00/−7.00, "
            "`r4_end` +79.00/+303.00); recorded at `.memory/01-ladder.md` "
            "finding 21 as *\"the R4 side is disclosed but NOT established, "
            "and it flatters SAFE\"*. `r4_slice`'s twin was NOT built (it "
            "needs an unchecked reslice AND an element accessor — two new "
            "trusted items on a pattern with three), so what ships is the "
            "fixed-R4 bound plus an R3-side span of 1391.30…1597.30 / "
            "3350.00…3972.00, and no pair interval. ⚠⚠ "
            "`controls/gen_controls.py` is NOT this search — it is the C-side "
            "`c_pun`-vs-neighbours repair control of §8c"),
    "p42": ("BOTH sides searched TWICE and the SIGN FLIPPED: a fifth R4 "
            "spelling beat every R3 measured, −36.00/−2036.00 → "
            "**+12.00/+11.00**, and it was SHIPPED as the R4 rung. The R3 span "
            "was separately 4.5× too wide",
            "`patterns/p42-goto-cleanup/NOTES.md` §9/§9a/§11b and "
            "`patterns/p42-goto-cleanup/controls/spellings.py` (five R4, four "
            "R3, each substituted from a shipped rung). REVIEWED at TASK_109 "
            "blocker 2, which searched ONE spelling past TASK_104's "
            "four-per-side and found a do-while fold over a descending cursor "
            "— `15 verified, 0 errors`, `identity exact`, agreeing on all 12 "
            "inputs — BELOW every R3 spelling p42 had measured; shipped at "
            "TASK_110. REVIEWED AGAIN at TASK_116 §B4 and corrected at "
            "TASK_118: `r3_zeroed` matches `required`'s **R2** clause and "
            "`r3_push` has no `extend`, so the in-contract R3 span is "
            "1419…1627 / 51138…59845, not 1419…2634 / 51138…102846. ⚠⚠ The R3 "
            "and R4 spans OVERLAP at both ends, so p42 publishes NO "
            "rung-to-rung difference — only `R3ship − R4ship` as a fixed-R4 "
            "bound. ⚠ The lesson is about the SEARCH, not the number: the "
            "first four R4 spellings were four ways of writing ONE shape"),
    "p46": ("BOTH sides searched (3 R4 levers, 3 R3), and BOTH ARE DEGENERATE "
            "— R4's span is 2.00 `Ir`/call, R3's is 0.00, every lever flat in "
            "`n` and in `m`. ⚠ Those widths are TASK_092's UNREVIEWED "
            "re-measure; the reviewed pair was 3 and 2",
            "`patterns/p46-bignum-mac/NOTES.md` §8b (*\"searching one side is "
            "not searching\"*) and §0c, levers generated by "
            "`controls/mkvariants.py` from the shipped rungs by substitutions "
            "that assert their own count and FAIL CLOSED. REVIEWED at "
            "TASK_089_REVIEW M1, which caught `spec.md`'s hashed `why` "
            "claiming *\"three R3 spellings span 9490 … three R4 spellings "
            "span 2750; NEITHER SIDE IS DEGENERATE\"* — figures that appear "
            "NOWHERE in `NOTES.md` and came from the retracted pre-build "
            "probe. ⚠⚠ The CHEAPEST unsafe spelling found is not a rung and "
            "not degenerate: `r4_mutreslice` is −695…−2595 `Ir`/call below "
            "R4ship and below EVERY safe spelling, its full R5 verifies "
            "`21 verified, 0 errors`, and it is excluded on two MEASURED "
            "grounds — two new trusted items (TCB 5/3 → 7/5) and an R4/R5 pair "
            "that is `differ` at `-O3` by `15n + 1`. **Relax either and the "
            "headline inverts.** ⚠ The corrected widths come from TASK_092's "
            "one-sided `-C codegen-units=1` fix, which `RECAP.md`'s START HERE "
            "box still marks PROVISIONAL and unreviewed; it moved the "
            "conclusion in the STRENGTHENING direction"),
}

# ⚠ The entries above that record a REVIEWED DECLARATION OF *NO* SEARCH rather
# than a search result.  `undeclared` cannot express the difference -- it means
# "nobody wrote an entry" -- and three of the seven rows added at TASK_166 are
# in this class, so the aggregate below is split rather than quoted as one
# number.  Keeping it as an explicit set rather than sniffing the entry text is
# deliberate: a prefix test is a hand-maintained convention inside a
# hand-maintained dict, which is the defect this whole block exists to record.
SEARCH_NONE = {"p29", "p32", "p49"}

# --- TASK_172 item C: two counts that were TYPED under a computed list ------
#
# ⚠⚠ **THIS FILE'S MOST-REPEATED DEFECT IS A HAND-TYPED COUNT UNDER A COMPUTED
# LIST, AND `RECAP` RECORDS IT AT LEAST THREE TIMES.** TASK_170 fixed one
# instance (`n_undecl`, difference-of-lengths -> set difference) and TASK_171
# found two more **in the same block, one paragraph below that fix**:
#
#   * *"every entry cited to a **reviewed** artefact -- except one, `p06`"* was
#     **false on three**: `p01`, `p03` and `p08` cite `RECAP`'s ***Owed***
#     queue, i.e. the OPEN BACKLOG, and their own verdict text says the span is
#     OWED or NEVER searched. Worse, `n_found` is a RESIDUAL
#     (`len(SEARCH_REVIEWED & meas) - len(SEARCH_NONE)`), so all three were
#     counted inside the published *"N report a SEARCH RESULT"*.
#   * *"Seven of the fourteen name their own weaker endpoint"* **listed SIX**,
#     omitting `p18` and `p38` -- the two most explicit -- so the typed word,
#     the printed list and the truth were three different numbers.
#
# ✅ **Both are now DATA, and both counts are `len()` of the thing that is
# printed.** A count and a list that come from one object cannot disagree.
# ⚠ **And the membership quotes are checked** -- `weaker_endpoint_rows` FAILS
# CLOSED if an entry's own words move away from the quote anchoring it, which
# is the only way this kind of set rots.

#: The rows that printed `undeclared` at 26 patterns and that TASK_170 read
#: against their own artefacts. Data, not a typed string: *"fourteen"* below is
#: `len(UNDECLARED_AT_26)`.
UNDECLARED_AT_26 = ("p02 p04 p05 p07 p09 p14 p16 p18 p19 p23 p27 p38 p42 p46"
                    .split())

#: Of those, the entries that name an endpoint of their OWN which is
#: unsearched, fiat, or resting on a measurement nobody reviewed -- keyed to a
#: VERBATIM substring of that pattern's own `SEARCH_REVIEWED` entry, so a
#: reader can check the membership against the words rather than trusting a
#: count. ⚠ Deliberately NOT included: `p04`, `p05`, `p07`, `p16`, `p42`, whose
#: entries report a SEARCHED-AND-DEGENERATE endpoint (a result, not a gap), and
#: `p23`, whose one disclosure is about probe durability and whose floor
#: correction was found and settled BY a review.
WEAKER_ENDPOINT = {
    "p02": "The R4 side is explicitly UNsearched",
    "p09": "The R4 half is the weaker one",
    "p14": "The R4 side was never searched",
    "p18": "⊘ The R4 side is NOT searched, declared",
    "p19": "only the review re-measured them",
    "p27": "R3 searched twice; R2 never",
    "p38": "the R4 side is disclosed but NOT established, and it flatters SAFE",
    "p46": "Those widths are TASK_092's UNREVIEWED re-measure",
}


def weaker_endpoint_rows(reviewed=None, quotes=None, population=None):
    """`[(pat, quote)]` for the rows whose own entry names a weaker endpoint.

    **FAILS CLOSED.** Every key must be in the population, must have an entry,
    and its quote must still occur verbatim in that entry's verdict-or-citation
    text. A quote that has drifted raises rather than silently dropping the row
    -- silently dropping is the flattering direction and is how the sentence
    this replaces came to say `Seven` over a list of six."""
    reviewed = SEARCH_REVIEWED if reviewed is None else reviewed
    quotes = WEAKER_ENDPOINT if quotes is None else quotes
    population = UNDECLARED_AT_26 if population is None else population
    out, bad = [], []
    for pat in sorted(quotes):
        if pat not in population:
            bad.append(f"{pat}: not in the population {sorted(population)}")
            continue
        e = reviewed.get(pat)
        if not e:
            bad.append(f"{pat}: no SEARCH_REVIEWED entry")
            continue
        if quotes[pat] not in (e[0] + " " + e[1]):
            bad.append(f"{pat}: the anchoring quote {quotes[pat]!r} is no "
                       f"longer in its entry")
            continue
        out.append((pat, quotes[pat]))
    if bad:
        raise ValueError("WEAKER_ENDPOINT has rotted away from the entries it "
                         "describes: " + "; ".join(bad))
    return out


def backlog_cited(reviewed=None):
    """Entries whose PRIMARY cited artefact is `RECAP`'s ***Owed*** queue --
    outstanding work, not a reviewed measurement.

    `(primary, mentions)`. `primary` is the citation that *starts* with
    `RECAP`; `mentions` is every entry whose citation names the queue anywhere.
    **Both are printed**, because the difference between them is the boundary
    of the rule and a reader must be able to see it: `p18` cites a `NOTES.md`
    and a review AND names the queue for its R4 half, which is a different
    state from citing the queue and nothing else."""
    reviewed = SEARCH_REVIEWED if reviewed is None else reviewed
    primary = sorted(p for p, (_, c) in reviewed.items()
                     if c.lstrip().startswith("RECAP"))
    mentions = sorted(p for p, (_, c) in reviewed.items()
                      if "Owed" in c or "owed" in c)
    return primary, mentions

# The two bands of the derived column, MEASURED rather than asserted.
#
# ⚠⚠⚠ THE HEADLINE JUSTIFICATION FOR `FLOOR` -- *"2.00 is THE ONLY THRESHOLD
# THAT MISSES NOTHING"* -- IS FALSE AGAINST THE COMMITTED TREE AND WAS FALSE
# BEFORE THE SEVEN NEW ROWS LANDED.  Re-scored at TASK_166 (`.temp/t166/
# bands33.py`, `.temp/t166/bands_subset.py`) with today's records and a
# 33-pattern oracle, truth = `|moves_by| >= 5e-3`:
#
#   population        2.00 Ir            3.00 Ir            5.00 Ir
#   TASK_076's 22     156 / 4 / 16       158 / 6 / 12       159 / 6 / 11
#   SYNTHESIS's 26    188 / 4 / 16       190 / 6 / 12       191 / 6 / 11
#   all 33            236 / 5 / 23       240 / 7 / 17       245 / 7 / 12
#   published (22)    162 / 0 / 14       164 / 2 / 10       165 / 2 / 9
#
# The four misses present at EVERY population and EVERY threshold are `p03` and
# `p04` `R3-R4` on both blobs: callgrind measures `-7.00` (the glibc `memset`
# alignment tail) where the derived route computes EXACTLY `+0.00`, so no
# positive floor can catch them.  The 33-population adds one more, `p34 large
# R5-R4` (truth `+0.0065`, derived `-0.10`).  ⚠ The ORACLE did not move: the
# committed 26-pattern sidecar and the TASK_166 re-emit agree on **0 of 208**
# pair rows and **0 of 824** cell figures.  What moved is the DERIVED side --
# the committed `marginal_ir_per_call` records -- and the table was never
# re-scored after it did.
#
# ✅ NEITHER CONSTANT MOVES, and that is measured rather than assumed:
#   * `FLOOR = 2.00` still MINIMISES misses (5 at 33) and has the fewest false
#     alarms of every threshold that does (1.50 -> 5/24, 2.00 -> 5/23,
#     2.50 -> 7/20).  Only a threshold at or below 0.10 catches `p34`, at
#     98 false alarms.  The VALUE stands; the SENTENCE does not.
#   * `CONFIDENT = 16.00`: the `>= CONFIDENT` band is **57 rows, 57 real, 0
#     spurious, smallest |correction| 17.0027** -- the same 17.00 the 22-row
#     fit found, with 23 more rows in it.
#
# The band populations at 33 (`.temp/t166/bands33.py`), against 22 published:
#   |correction| <  FLOOR      175 rows, 5 REAL / 170 spurious   (was 120, 0 real)
#   FLOOR .. CONFIDENT          32 rows, 9 real / 23 spurious    (was 22, 8/14)
#   |correction| >= CONFIDENT   57 rows, ALL real, smallest 17.00 (was 34)
# ⚠⚠ **THE LOW BAND IS NO LONGER EMPTY OF REAL CORRECTIONS** -- *"nothing real
# hides here"* is now false on 5 rows, and `classify` returns `low` BEFORE it
# consults the null, so those five are dropped silently rather than refused.
FLOOR = 2.00
CONFIDENT = 16.00

# ---- the ENVIRONMENT-PHASE census, pinned ------------------------------------
# `marginal_ir_per_call` at `-O3 isolated` is not a constant on p03 and p04: a
# per-call `memset` of a stack scratch buffer takes an alignment-dependent tail
# in `__memset_avx2_unaligned_erms`, and the initial stack pointer moves with the
# length of the environment block.  The effect is BISTABLE with a period of 32
# bytes and a window exactly 16 wide, and the phase differs per binary, so a PAIR
# can swing by 14 (`check.py::check_marginal_ir`).
#
# Below: the derived correction `(marg[A]-marg[B]) - (kex[A]-kex[B])` over 32
# consecutive environment lengths -- one full period -- as `value: pads`.
# Instrument `.temp/r98/sweep.py`, data `.temp/r98/{p03,p04}_sweep.json`
# (TASK_098, reviewed; re-derived at TASK_099).  Identical on both blobs.
#
# ⚠ This is a PIN, not a derivation: nothing in `results/` carries a sweep, and
# re-taking it costs ~2 min/pattern -- the instrument is `.temp/r98/sweep.py`,
# and `.memory/03-measurement.md`'s RESOLVED block is the reviewed write-up.
# ⚠ `common/layout/` is the WRONG instrument and fails in the dangerous
# direction: it varies the PROGRAM and measures `ns`, and callgrind is
# layout-blind, so it returns ~0 on a term worth 7.
PHASE_SWEEP = {
    ("p03", "R2-R4"): {0.00: 16, 7.00: 16},
    ("p03", "R3-R4"): {-7.00: 8, 0.00: 16, 7.00: 8},
    ("p03", "R5-R4"): {-8.00: 14, -1.00: 4, 6.00: 14},
    ("p04", "R2-R4"): {0.00: 16, 7.00: 16},
    ("p04", "R3-R4"): {-7.00: 8, 0.00: 16, 7.00: 8},
    ("p04", "R5-R4"): {-8.00: 14, -1.00: 4, 6.00: 14},
}

# ⚠⚠ WITHDRAWN: the pairs where the correction IS the whole published figure.
# R4 and R5 are byte-identical binaries, so the kernel column is exactly 0.00 and
# the printed cell is the correction alone -- there is no large true difference
# for a 7-Ir term to be a rounding error of.  `value` is the part that
# reproduces: `R5-R4 = kernel 0 + memset {-7,0,+7} + main (-1)`, attributed
# symbol by symbol at TASK_098 (`.temp/mgr98/`), so `main`'s -1.00 is all that
# survives the phase.  ⚠ It is the OPPOSITE SIGN to the `+6.00` this file
# published for five tasks.
WITHDRAWN = {
    ("p03", "R5-R4"): (-1.00, "`main` 14 vs 13"),
    ("p04", "R5-R4"): (-1.00, "`main` 14 vs 13"),
}


# ⚠ The SEVENTH exposed cell, and it is neither p03 nor p04.  A 2-pad screen
# over the whole tree (24 patterns x 6 cells x 2 blobs, pad 0 against pad 16,
# `.temp/r98/treescan_{small,large}.json`) moved 14 of 288 triples: p03's and
# p04's three Rust rungs each, AND p46's `c-clang`.  No full period was taken
# for it, so it is marked and not quantified.  ⚠ **"2 patterns, 7 of 144 cells"
# -- in `.memory/03-measurement.md`'s RESOLVED block, `TASK_098_REPORT.md`
# MAJOR 3 and `TASK_099.md` §C -- is arithmetically impossible for that reason:
# the count is THREE patterns.**
PHASE_SCREEN = {
    ("p46", "gcc-clang"):
        "`c-clang`'s marginal moves `6216.00 → 6209.00` (`small`) and "
        "`23230.66 → 23223.66` (`large`) between pad 0 and pad 16, so the "
        "correction carries the same ±7.00 — **2-pad screen only, no full "
        "period taken**. It is 8% of the `-87.00` correction and 0.34% of the "
        "`+2076.00` figure, so nothing here is withdrawn",
}


# ⚠⚠ WHY EACH `R5-R4` ROW THAT CLEARS THE FLOOR DOES NOT MEAN "THE PROOF COSTS
# INSTRUCTIONS".  This dict exists because the paragraph under §5 claim 1's
# COMPUTED list was TYPED, and it was false: it asserted *"every one of those
# rows is in the uncertain 2.00-16.00 band"* over a list whose `p42 large
# -31.00` is >= CONFIDENT and prints in bold two sections earlier, then
# resolved *"all six"* of seven (TASK_158 M4; PROTOCOL rule 13's class, in a
# generator).  ⚠ A row with NO entry here prints as **UNRESOLVED**, loudly --
# the failure mode being repaired is a summary sentence that covers a row
# nobody looked at.  Key `(pattern, blob)`; `(pattern, None)` covers both.
R5_ROW_WHY = {
    ("p02", None):
        "the sweep measures **0.00**: the derived `−2.00` is the driver "
        "residual and nothing else (`CALLEE_NOTE` — gcc's PLT thunk is the "
        "only true-but-small correction in the tree, and this is not it)",
    ("p03", None):
        "a **real** term — glibc `memset`'s alignment-dependent path length "
        "between two byte-identical kernels — that **has no value**: over 32 "
        "environment phases it takes `{−8.00, −1.00, +6.00}` with support "
        "14 / 4 / 14, so the `+6.00` this file used to print was one draw "
        "**tied with its own sign-reverse**. Withdrawn in §2 (`‡`); the part "
        "that reproduces is `main`'s **−1.00**",
    ("p04", None):
        "identical to p03's, on the same 32-phase sweep and both blobs — "
        "withdrawn in §2 (`‡`), reproducible content `main`'s **−1.00**",
    ("p25", "large.bin"):
        "**decomposed over every function** at pads 0 and 16, identical "
        "(TASK_158 §1g): `verus::kernel − unsafe::kernel = 0.00` (4152.71 "
        "each) and `verus::main − unsafe::main = 0.00` (14.00 each), with "
        "**six glibc malloc-internal symbols summing to +268.88 = 100.0 %** "
        "of the delta. Symbol names are unavailable (`libc6-dbg` absent); the "
        "caller edges identify them as reached from `malloc`, `free` and "
        "`realloc`. ⚠ It is **not** the environment phase",
    ("p42", "large.bin"):
        "**decomposed over every function**, same instrument, pads 0 and 16 "
        "identical (TASK_158 §1h): kernels `0.00` (50734.00 each), `main`s "
        "`0.00` (13.00 each), and a single symbol `0xab170` (`_int_free`) at "
        "**−31.00 = 100.0 %** of the delta",
}


def _phase_note(pat, lab):
    """`{-8.00: 14, ...}` -> `−8.00 on 14 pads, −1.00 on 4, +6.00 on 14`."""
    if (pat, lab) in PHASE_SCREEN:
        return PHASE_SCREEN[(pat, lab)]
    sup = PHASE_SWEEP[(pat, lab)]
    return ", ".join(f"`{v:+.2f}` on {n}"
                     for v, n in sorted(sup.items())) + " of 32"

BULK_CALLS_NOTE = """\
⚠ **`static.bulk_calls` is a WHITELIST, and on three patterns the record it
produces is wrong about what the cell calls.** This is the one genuinely new
defect the licence work turned up, it is in `harness/`, and it is **not fixed
here** -- reported for the owed `harness/` batch:

* **`asm.is_bulk_symbol('bcmp')` is `False`** (measured), so
  `results/p47-ct-compare.json` records `c-gcc: ['memcmp@plt']`, `c-clang: []`
  and `safe_naive: []` for three cells that call **the same glibc entry point**
  -- both names resolve to address `0x188320`, and p47's own reviewed
  `NOTES.md` says clang rewrites `memcmp(...) == 0` into `bcmp`.
* **`__popcountdi2` is not a bulk name either**, so all eight of p09's cells
  record `[]` while `c-gcc` calls libgcc's software popcount at
  **378.00 / 2625.00 `Ir` per call**.
* **p11's four plain C cells record `[]` while calling `strlen@plt`**, which
  `is_bulk_symbol` *does* recognise -- the record predates `asm.py`'s
  `_BULK_STR_WORDS` and only the two `-h` cells are populated. (RECAP "Owed"
  6's follow-up sentence says p11's `bulk_calls` *are* populated; it is wrong
  as written.)

**And the four "adjacent findings" this work reported are, three of them,
already published by the patterns they name** (TASK_075_REVIEW M5) -- so they
are citation fixes and cost no gate re-run:

| finding | disclosed where |
|---|---|
| p27 `R2-R4`/`R3-R4` understated by `+120.33 / +130.95` | `p27/NOTES.md` §5e, as a **closed** decomposition summing to `+230.0694 / +792.7458` |
| p09's gcc column carries `__popcountdi2`, `378 / 2625` | `p09/NOTES.md` §2: *"Quote `marginal_ir_per_call` for anything involving a gcc cell"* |
| p47's `R2-R4` moves (`bcmp`) | `p47/NOTES.md` §1, "The call targets, resolved by GOT relocation and `nm`" |
| p11's `R3-R4` reverses | `p11/NOTES.md:143`, and the boilerplate in 22 of 22 `results/tables/*.md` |
| **p27's `gcc-clang` reverses on `small`, `-25.02 -> +15.00`** | **new** |

⚠ **And p27's mechanism, as this file first stated it, was wrong.** It said
*"p27's `unsafe` dispatches through `call *%r12`"* was the cause of the
`+120.33`. Measured outward `Ir` on `small`: `unsafe` pays `dealloc 917.33`;
`safe_naive` pays `dealloc 280.93 + drop_glue 756.73`. **The cost is the SAFE
side's out-of-line `drop_glue::<[Option<Box<u8>>; 32]>`**, not the unsafe
side's indirect call -- which is a second call to `__rust_dealloc` already
inside p27's decomposition. `.memory/01-ladder.md` finding 19 had this right
before this file was written and was re-confirmed against it.
*A right answer with a wrong justification propagates exactly like a wrong
answer* (`.memory/03-measurement.md`).
"""

CALLEE_NOTE = """\
**The callee correction below is DERIVED FROM COMMITTED RECORDS.**
`results/gate/pNN.json` carries **`marginal_ir_per_call`** for every
`(cell, opt, mode, input)`. That figure is whole-program -- the `n_iters`
200-minus-100 construction -- and therefore *symbol-independent*, so it already
contains exactly the callee work the kernel-exclusive column drops. For two
cells whose driver is compiled the same way the driver term cancels, and

```
(marg[A] - marg[B]) - (kex[A] - kex[B])   =   the callee correction
```

is computable from files already in `git`. This is `.memory/03-measurement.md`'s
own *"author-checkable test, which needs no disassembly"*, and the same
arithmetic is the generated boilerplate in 22 of 22 `results/tables/*.md`.

⚠ **An earlier version of this file said the opposite** -- *"the licence is not
in the committed records and cannot be derived from them"* -- and scheduled two
sidecars on the strength of it (TASK_075_REVIEW B1). Nothing in the tables moved;
the provenance sentence was the defect.

⚠ **ITS FLOOR IS 2.00 `Ir` AND THAT IS THE ONLY THRESHOLD AT WHICH IT MISSES
NOTHING.** TASK_075_REVIEW B1 and `.memory/03-measurement.md` report *"zero
misses at every threshold (2.0 -> 14 false alarms, 3.0 -> 10, 5.0 -> 9)"*.
Re-measured (`.temp/p76/derived_probe.py`), scoring the oracle at 5e-3 rather
than at the same threshold as the estimate:

| threshold | hit | **miss (false OK)** | false alarm |
|---|---:|---:|---:|
| **2.00 Ir** | 162 | **0** | 14 |
| 3.00 Ir | 164 | **2** | 10 |
| 5.00 Ir | 165 | **2** | 9 |

The review's version scores `truth = |correction| >= threshold`, which excuses
the estimator from finding exactly the corrections it is too coarse to find.
Both misses are `p02 gcc-clang`, both worth exactly **+2.00** -- one libc call
per kernel call through gcc's PLT thunk, and the only true-but-small correction
in the tree. **So this file uses 2.00, and the smallest real correction sits
exactly on it.**

**What the derived column cannot do.** It does not name a callee, and it cannot
resolve the +-7.00 `memset` term or the +2.00 PLT thunk. **Its residual is
structured, not noise**: exactly **+1.00 on 26 of 44 `gcc-clang` rows** and
exactly **-1.00 on 28 of 44 `R5-R4` rows** -- the driver-codegen term, which is
what puts the floor at 2.00 rather than at 0. It is **not** subtracted here; a
fitted correction is not a measurement.

**Where the mechanism comes from instead**: the licence column, which is a
disassembly property with zero run noise and answers a *different* question --
*may this row be differenced at all* -- and names the callee when the answer is
no. The two disagree on p03/p04 `R2-R4` (`LICENSED`, derived +7.00) and that
disagreement **is** the `memset` finding, not a defect in either.

⚠ **And that `+7.00` is one draw of a two-state variable, not a constant**: the
same cell derives `0.00` at half of the 32 environment phases (`‡` below). The
disagreement is real at every phase -- the licence says "differenceable", the
sweep says the callee moves -- but its MAGNITUDE is a phase, so quote the
support, never the draw.
"""



def _n_named(name):
    """How many published `verus.rs` TCB items carry this name. COMPUTED, because
    a hardcoded count in a generated file goes stale the moment a pattern lands
    (TASK_088: the prose said 22 with 23 patterns in the tree)."""
    import json as _j, glob as _g
    n = 0
    for f in _g.glob(os.path.join(REPO, "results", "gate", "*.json")):
        if ".partial" in f:
            continue
        vb = (_j.load(open(f)).get("verus") or {}).get("verus.rs") or {}
        n += sum(1 for i in (vb.get("tcb_items") or []) if i.get("name") == name)
    return n


def _n_verus_rs():
    import glob as _g
    return len(_g.glob(os.path.join(REPO, "patterns", "*", "verus.rs")))


def _n_broadcast():
    import glob as _g
    return sum(1 for f in _g.glob(os.path.join(REPO, "patterns", "*", "verus.rs"))
               if "broadcast use" in open(f).read())

def load_measurements():
    out = {}
    for f in sorted(glob.glob(os.path.join(RESULTS, "p*.json"))):
        d = json.load(open(f))
        if "cells" not in d or not isinstance(d.get("inputs"), dict):
            continue                     # side record (p02-residue-sweep)
        out[d["pattern"].split("-")[0]] = d
    return out


def load_gates():
    out = {}
    for f in sorted(glob.glob(os.path.join(GATE, "p*.json"))):
        if f.endswith(".partial.json"):
            continue
        d = json.load(open(f))
        out[d["pattern"].split("-")[0]] = d
    return out


def ir_per_call(d, cell, opt, mode, inp):
    n = d["inputs"].get(inp, {}).get("n_iters")
    for c in d["cells"]:
        if (c["cell"], c["opt"], c["mode"]) != (cell, opt, mode):
            continue
        v = (c.get("ir") or {}).get(inp) or {}
        ke = v.get("kernel_exclusive_ir")
        if ke is None or not n:
            return None
        return ke / n
    return None


def fmt(x, w=11, p=2):
    return f"{x:{w}.{p}f}" if x is not None else f"{'-':>{w}}"


def marginal(gates, pat, cell, inp, opt="O3", mode="isolated"):
    """`results/gate/pNN.json::marginal_ir_per_call` -- whole-program, so it
    carries the callee work the kernel-exclusive column drops."""
    m = (gates.get(pat) or {}).get("marginal_ir_per_call") or {}
    return m.get(f"{cell}/{opt}/{mode}/{inp}")


def derived_correction(meas, gates, pat, a_, b_, inp):
    """The callee correction for one pair on one blob, FROM COMMITTED RECORDS.

    `(marg[A] - marg[B]) - (kex[A] - kex[B])`.  Returns `None` when either
    record is missing rather than guessing."""
    ka = ir_per_call(meas[pat], a_, "O3", "isolated", inp) if pat in meas else None
    kb = ir_per_call(meas[pat], b_, "O3", "isolated", inp) if pat in meas else None
    ma, mb = marginal(gates, pat, a_, inp), marginal(gates, pat, b_, inp)
    if None in (ka, kb, ma, mb):
        return None
    return (ma - mb) - (ka - kb)


# ------------------------------------------- the PER-PATTERN null, and the rule
#
# `NULL_PAIR` is the pair the `identity` pin forces to agree.
# `check.py::check_identity` compares the two rungs' `-O3 isolated` kernel
# digests, so on THIS column -- `-O3 isolated`, the only one this file
# publishes -- the pair's
# derived correction is a MEASURED NULL: a number that ought to be zero and is
# not.  Anything a pattern reads there is that pattern's own noise on this
# column, and a correction no larger than it is not resolvable HERE, whatever
# the tree-wide bands say.
#
# ⚠ TASK_170 item A: this comment and the published sentence in `emit_bands`
# both carried `(check.py:3303)` beside the function name.  That line had
# ROTTED -- it is a data line inside `check_marginal_ir`'s docstring, not
# `check_identity` at all -- and the belt-and-braces spelling (function name
# AND line) is exactly the shape `.memory/02-bench-rules.md` retracts:
# *"name the FUNCTION and give NO LINE NUMBER AT ALL"*.  `.memory/` recorded
# this same coordinate as rotted and repaired it IN ITS OWN COPY ONLY, which
# is why the generator kept re-emitting it into a PUBLISHED artefact.
# **Do not put a line number back.**
#
# ⚠ MODE AND LEVEL ARE PART OF THE STATEMENT, and getting either wrong has
# already produced two wrong tables (TASK_158 M1/M2, and this file's third
# correction of the same derivation -- see `NULL_NOTE`).
NULL_PAIR = ("verus", "unsafe")


def r5_null(meas, gates, pat, inp):
    """This pattern's own `R5 - R4` derived correction on this blob."""
    return derived_correction(meas, gates, pat, *NULL_PAIR, inp)


def null_for(meas, gates, pat, a_, b_, inp):
    """The null to score `(a_, b_)` against -- `None` on the pair that IS the
    null.  A control cannot be its own control: scored against itself the
    `R5-R4` column refuses every row it prints, at a ratio of exactly 1.00x."""
    if (a_, b_) == NULL_PAIR:
        return None
    return r5_null(meas, gates, pat, inp)


def classify(c, null):
    """The band a derived correction prints in.  PURE -- `(correction, null)`
    in, band out -- so it can be exercised on PLANTED values, which is what
    `null_rule_selftest` does.  Returns `low` / `mid` / `high` / `refused`.

    `refused` means *this pattern's own null on this column is at least as big
    as the figure*, so the figure is not promoted to a band; the null prints
    beside it instead.  A null inside the global floor is not a null at all --
    it is what every pattern reads -- so it never refuses anything."""
    if c is None:
        return None
    if abs(c) < FLOOR:
        return "low"
    if null is not None and abs(null) >= FLOOR and abs(c) <= abs(null):
        return "refused"
    return "high" if abs(c) >= CONFIDENT else "mid"


def null_rule_selftest(meas, gates):
    """MUST-FIRE and SILENT arms for `classify`, run on every invocation.

    ⚠ `.memory/03-measurement.md`: *every harm probe owes a positive control
    that must fire, in the detector whose column it licenses.*  The planted
    arms are pure and cannot fail to run; the live arms are derived from the
    records and name the rows the rule actually moved.  Raises `SystemExit` on
    any disagreement -- a rule whose own control is broken must not publish."""
    planted = [
        # (name, got, want) -- MUST-FIRE first
        ("MUST-FIRE  a CONFIDENT-sized figure under a bigger null",
         classify(100.00, 500.00), "refused"),
        # ⚠ no raw `|` in an arm name -- these print inside a markdown table.
        ("MUST-FIRE  equality is refusal (correction == null in magnitude)",
         classify(19.42, -19.42), "refused"),
        ("MUST-FIRE  a mid-band figure under a bigger null",
         classify(5.00, -31.00), "refused"),
        # ⚠ `want` here is `high`, not `mid`: 19.43 >= CONFIDENT, so "promotes
        # normally" IS the confident band.  This arm was written with `mid` and
        # the selftest refused to publish -- which is the control working.
        ("silent     one Ir over its null promotes normally",
         classify(19.43, -19.42), "high"),
        ("silent     a big figure with a floor-sized null is untouched",
         classify(100.00, 1.00), "high"),
        ("silent     a big figure with NO null is untouched",
         classify(100.00, None), "high"),
        ("silent     a big figure with a null of exactly the floor",
         classify(100.00, 2.00), "high"),
        ("silent     the rule never MANUFACTURES a figure below the floor",
         classify(1.00, 500.00), "low"),
        ("silent     mid stays mid when the null is small",
         classify(3.00, 1.00), "mid"),
    ]
    fails = [p for p in planted if p[1] != p[2]]
    live = []
    for a_, b_, lab in PAIRS:
        for pat in sorted(meas):
            for inp in ("small.bin", "large.bin"):
                c = derived_correction(meas, gates, pat, a_, b_, inp)
                n = null_for(meas, gates, pat, a_, b_, inp)
                if classify(c, n) == "refused":
                    live.append((pat, inp[:-4], lab, c, n))
    # The live must-fire arm, named so that its ABSENCE is loud.  It is
    # conditional on the row existing, and it says so when it does not.
    want = ("p25", "large", "gcc-clang")
    if "p25" in meas and "p25" in gates:
        if not any(r[:3] == want for r in live):
            fails.append(("MUST-FIRE (live)  p25 large gcc-clang is refused",
                          "absent", "present"))
        live_note = ("live must-fire arm **`p25 large gcc-clang` FIRED**"
                     if any(r[:3] == want for r in live) else "**DID NOT FIRE**")
    else:
        live_note = ("live must-fire arm **NOT RUN** -- `p25` is not in the "
                     "records this run read")
    if fails:
        raise SystemExit("null_rule_selftest FAILED: "
                         + "; ".join(f"{n}: got {g!r} want {w!r}"
                                     for n, g, w in fails))
    return planted, live, live_note


# --------------------------------------------------------------------------
# `§` -- A CORRECTION THAT CROSSES A LIBC BULK-ROUTINE THRESHOLD (TASK_170 E)
#
# `Ir` counts instructions, and a bulk fill/copy changes INSTRUCTIONS PER BYTE
# by ~10x across a size threshold while the hardware cost goes the other way:
# `rep stosb` is what the CPU runs BECAUSE it is fast, so `Ir` reports the cost
# RISING at exactly the size the real cost falls (`.memory/03-measurement.md`).
# A difference taken across that threshold is real work, priced in a regime no
# other row in this column is in -- so it is not comparable with them.
#
# ⚠⚠ WHAT MUST NOT BE PUBLISHED HERE IS A DISCOUNT FACTOR. The *"~90% of the
# term is counter, not code"* gloss is WITHDRAWN: its `≈426 Ir` counterfactual
# was glibc **`memcpy`**'s 4092-byte figure (`0.104 Ir`/byte) re-badged as a
# **`memset`** counterfactual (TASK_169 §3b). There is no measured vector-path
# counterfactual for p42's zeroing, so no percentage may be quoted. One rung
# zeroes 4096 bytes and the other does not; the work is REAL and belongs
# entirely to one rung. What `Ir` gets wrong is the PRICE, not the presence.
#
# THE TEST IS THE `Ir`/BYTE SIGNATURE, and the sidecar gives `Ir` PER CALL of
# the routine without a byte count -- so the byte count is inferred from the
# two possible rates and checked against the routine's own measured crossover:
#
#   vector 0.10 Ir/byte  =>  bytes = 10 * C  =>  C < lo forces VECTOR
#   byte-wise ~1.00      =>  bytes = C       =>  C > hi forces BYTE-WISE
#
# ⚠ AND THE FIRST SPELLING OF THIS CENSUS FOUND ONLY p42, WHICH IS THE
# FLATTERING ANSWER. In this sidecar the glibc routines have NO SYMBOL -- they
# are bare addresses -- so a name regex misses every one of them and reports
# the one Rust-named callee. `0x189480` and `0x188a80` are resolved in
# `.memory/03-measurement.md`.
#
# ⚠⚠ **AND THIS DICT IS A WHITELIST. IT WAS PUBLISHED AS *"DERIVED rather than
# listed"* AND THAT MARK WAS NOT EARNED** (TASK_171 §1a(ii)/§5, RECAP finding
# 67(d)). The marked ROWS are derived; the ROUTINE SET is three keys somebody
# typed, two of them bare glibc load addresses that a glibc bump would silently
# retire -- returning `{}`, the flattering answer again. What makes it a
# whitelist is **not** the names: it is the pair `(lo, hi)`, the routine's own
# byte-count crossover, which the sidecar cannot supply because it carries `Ir`
# per call and no byte count. A signature rule with routine-independent
# thresholds is therefore NOT available from this sidecar, and saying so is the
# honest form.
# ✅ **What IS available, and is now derived on every run:
# `unclassified_bulk_candidates` prints what the whitelist does not decide** --
# every callee NOT in this dict that contributes asymmetrically above the floor
# on a published pair, scored against the smallest `lo` and `hi` any classified
# routine has. On today's tree it settles TASK_171's open question with a
# measurement instead of a name: `__memchr_avx2` and `__strlen_avx2` peak at
# 41.51 and 33.06 `Ir` per callee-call over the WHOLE sidecar, 7x and 9x below
# the smallest `lo` (300.0) -- **forced VECTOR on every cell they appear in, so
# they cannot trigger the mark, and adding them would change nothing.**
BULK_REGIME = {
    "0x0000000000189480":
        ("glibc `memset` (`__memset_avx2_unaligned_erms`)", 300.0, 4000.0),
    "0x0000000000188a80":
        ("glibc `memmove` (`__memmove_avx_unaligned_erms`)", 852.0, 8192.0),
    "__rustc::__rust_alloc_zeroed":
        ("`__rust_alloc_zeroed`'s fill", 300.0, 4000.0),
}


def bulk_regime(callee, ir_per_callee_call):
    """`(name, "VECTOR"|"BYTE-WISE"|"?")`, or `None` if not a bulk routine."""
    if callee not in BULK_REGIME:
        return None
    name, lo, hi = BULK_REGIME[callee]
    c = ir_per_callee_call
    return (name, "VECTOR" if c < lo else "BYTE-WISE" if c > hi else "?")


def regime_crossing(outw, floor=None):
    """`{(pat, inp, lab): [evidence]}` -- published rows the `§` marker applies to.

    A row qualifies when a bulk routine's contribution is ASYMMETRIC across the
    pair by at least the floor AND at least one side is in the BYTE-WISE
    regime. Symmetric terms cancel out of the difference and are not marked --
    p08's `memset` is 4113.00 `Ir` in all four RUST cells, so `R2-R4`, `R3-R4`
    and `R5-R4` are clean and only `gcc-clang` is not (gcc inlines the same
    4096-byte fill as a 512-`Ir` `rep stos %rax`)."""
    floor = FLOOR if floor is None else floor
    out = {}
    for pat, d in sorted(outw.items()):
        if not isinstance(d, dict):
            continue
        for inp in ("small.bin", "large.bin"):
            side = d.get(inp)
            if not isinstance(side, dict):
                continue
            cells = side.get("cells") or {}
            for a_, b_, lab in PAIRS:
                if a_ not in cells or b_ not in cells:
                    continue
                ev = []
                for k in sorted(set(BULK_REGIME)):
                    ia = (cells[a_].get("outward_by_callee_per_call") or {}).get(k, 0.0)
                    ib = (cells[b_].get("outward_by_callee_per_call") or {}).get(k, 0.0)
                    if abs(ia - ib) < floor:
                        continue
                    regs = []
                    for cell in (a_, b_):
                        c = (cells[cell].get("outward_ir_per_callee_call")
                             or {}).get(k)
                        if c is None:
                            continue
                        nm, r = bulk_regime(k, c)
                        regs.append((cell, nm, c, r))
                    if any(r == "BYTE-WISE" for _, _, _, r in regs):
                        # ⚠ THE REASON STRING USED TO END *"while the other
                        # side does not call it at all"* AND THAT IS TRUE BY
                        # CONSTRUCTION, not by measurement (TASK_171 §1a(iii),
                        # RECAP 67(d)). `regs` has one entry when the OTHER
                        # side reports no entry under THIS KEY -- and on a
                        # `gcc-clang` pair the key space is compiler-dependent:
                        # gcc cells spell their libc callees as the client's
                        # own PLT address. Re-derived here at TASK_172, on the
                        # marked pattern itself: `p08 c-gcc` carries the SAME
                        # `memmove` at 39.0 `Ir`/callee-call under key
                        # `0x0004001160` against `c-clang`'s 39.4 under
                        # `0x188a80` -- the delta is the extra thunk. So the
                        # honest clause names the KEY, not the call.
                        ev.append(
                            f"{regs[0][1]} contributes {ia - ib:+.2f} `Ir` to "
                            "this difference and is priced BYTE-WISE on "
                            + " and ".join(
                                f"`{cell}` ({c:.2f} `Ir`/call)"
                                for cell, _, c, r in regs if r == "BYTE-WISE")
                            + (f" while `{b_ if regs[0][0] == a_ else a_}` "
                               "reports NO CALLEE EDGE UNDER THIS KEY"
                               + (" — which on a `gcc-clang` pair is NOT the "
                                  "same as not calling it, because the key "
                                  "space is compiler-dependent: see the "
                                  "caption below the table"
                                  if lab == "gcc-clang" else
                                  " — and both cells here are rustc-built, so "
                                  "the key space is common and this one does "
                                  "mean no call")
                               if len(regs) == 1 else ""))
                if ev:
                    out[(pat, inp, lab)] = ev
    return out


def unclassified_bulk_candidates(outw, floor=None):
    """What `BULK_REGIME`'s whitelist does NOT decide, derived.

    `{callee_key: {"rows": n, "max_ir_per_callee_call": x, "pats": [...]}}` over
    every callee **not** in `BULK_REGIME` that contributes asymmetrically by at
    least the floor on a published pair -- i.e. exactly the population a
    complete census would have to rule on.

    ⚠ **The scoring is against `BULK_REGIME`'s OWN thresholds and that is its
    limit**, stated rather than hidden: a callee under `min(lo)` is forced into
    the VECTOR regime by every crossover this project has resolved, and one over
    `min(hi)` would be forced BYTE-WISE. A routine whose own crossover is far
    below every resolved one would sit under `min(lo)` and still be byte-wise --
    that case cannot be settled from a sidecar with no byte count, and no row on
    this tree is near it (the largest unclassified figure is 3246.60, a Rust
    `drop_glue` over a 32-element array, which has no size regime at all)."""
    floor = FLOOR if floor is None else floor
    out = {}
    for pat, d in sorted(outw.items()):
        if not isinstance(d, dict):
            continue
        for inp in ("small.bin", "large.bin"):
            side = d.get(inp)
            if not isinstance(side, dict):
                continue
            cells = side.get("cells") or {}
            for a_, b_, lab in PAIRS:
                if a_ not in cells or b_ not in cells:
                    continue
                ka = cells[a_].get("outward_by_callee_per_call") or {}
                kb = cells[b_].get("outward_by_callee_per_call") or {}
                for k in sorted(set(ka) | set(kb)):
                    if k in BULK_REGIME:
                        continue
                    if abs(ka.get(k, 0.0) - kb.get(k, 0.0)) < floor:
                        continue
                    per = [(cells[c].get("outward_ir_per_callee_call")
                            or {}).get(k) for c in (a_, b_)]
                    m = max([v for v in per if v is not None] or [0.0])
                    e = out.setdefault(k, {"rows": 0,
                                           "max_ir_per_callee_call": 0.0,
                                           "pats": set()})
                    e["rows"] += 1
                    e["max_ir_per_callee_call"] = max(
                        e["max_ir_per_callee_call"], m)
                    e["pats"].add(pat)
    for e in out.values():
        e["pats"] = sorted(e["pats"])
    return out


def sidecar_callee_peak(outw, key):
    """Peak `Ir` per callee-call for one callee key over the WHOLE sidecar --
    every pattern, blob and cell, not only the published pairs. `(peak, where,
    n_cells)`, `(None, None, 0)` if the key never appears."""
    best, where, n = None, None, 0
    for pat, d in sorted(outw.items()):
        if not isinstance(d, dict):
            continue
        for inp in ("small.bin", "large.bin"):
            side = d.get(inp)
            if not isinstance(side, dict):
                continue
            for cell, c in sorted((side.get("cells") or {}).items()):
                v = (c.get("outward_ir_per_callee_call") or {}).get(key)
                if v is None:
                    continue
                n += 1
                if best is None or v > best:
                    best, where = v, f"{pat}/{inp[:-4]}/{cell}"
    return best, where, n


#: Callees TASK_171 §1a(ii) found unclassified in the sidecar and named as the
#: whitelist's silence.  They are resolved by address in the pinned glibc, and
#: they are here so the caption can print a MEASURED verdict on them rather
#: than leaving them unmentioned -- `unclassified_bulk_candidates` finds them
#: on its own; this dict only supplies the human name.
NAMED_UNCLASSIFIED = {
    "0x0000000000188080": "glibc `__memchr_avx2`",
    "0x000000000018b7c0": "glibc `__strlen_avx2`",
    "0x0000000000015220": "`ld.so`'s `_dl_runtime_resolve_xsavec`",
}


def derived(meas, gates, pat, a_, b_, lab=None, cross=None):
    """The `corrected (derived)` cell: the corrected difference with the
    correction in parentheses, on both blobs.  A dash means the derived
    correction is inside the +-2.00 Ir floor, where this route cannot tell it
    from zero -- NOT that the row was not computed.

    ⚠ **Two pairs print no figure at all.**  `WITHDRAWN` above names the cells
    where the correction is a phase of the environment block rather than a
    property of the code, and where it is also the entire published figure.
    They print the measured support and the reproducible term, and they do
    **not** print `**?**`: that marker means *look further*, and there is
    nothing further to look at -- the quantity has no value.  Blanking them was
    the cheaper option and is the wrong one, because in this table BLANK ALREADY
    MEANS SOMETHING ELSE (`|correction| < 2.00`), which is the band this file
    used to call *"safe: nothing real hides below the floor"*."""
    if (pat, lab) in WITHDRAWN:
        val, prov = WITHDRAWN[(pat, lab)]
        return (f"‡ **WITHDRAWN — not a quantity.** Over 32 environment phases "
                f"the correction takes {_phase_note(pat, lab)}, identically on "
                f"both blobs; the published `+6.00` was one draw and is tied "
                f"with its own sign-reverse. Reproducible content "
                f"**{val:+.2f}** ({prov}); the `memset` term "
                f"`{{−7, 0, +7}}` is unresolvable here.")
    out, any_move, any_row = [], False, False
    for inp, nm in (("small.bin", "small"), ("large.bin", "large")):
        c = derived_correction(meas, gates, pat, a_, b_, inp)
        k = ir_per_call(meas[pat], a_, "O3", "isolated", inp)
        k2 = ir_per_call(meas[pat], b_, "O3", "isolated", inp)
        if c is None or k is None or k2 is None:
            out.append(f"{nm} no record")
            continue
        any_row = True
        nul = null_for(meas, gates, pat, a_, b_, inp)
        band = classify(c, nul)
        if band == "low":
            out.append(f"{nm} <{FLOOR:.2f}")
        elif band == "refused":
            any_move = True
            out.append(f"{nm} {k - k2 + c:+.2f} ({c:+.2f}) **†** "
                       f"(own null {nul:+.2f})")
        elif band == "mid":
            any_move = True
            out.append(f"{nm} {k - k2 + c:+.2f} ({c:+.2f}) **?**")
        else:
            any_move = True
            out.append(f"**{nm} {k - k2 + c:+.2f}** ({c:+.2f})")
        # `§` is PER BLOB, not per row: p42's zeroing is BYTE-WISE at
        # n = 4096 (`large`) and VECTOR at n = 168 (`small`), which is the
        # whole point -- the same code, the same rung pair, two regimes.
        if cross and (pat, inp, lab) in cross and band != "low":
            out[-1] += " **§**"
    if not any_row:
        return "no record"
    s = " / ".join(out) if any_move else ""
    # ...and the same term on a pair where it is NOT the whole figure: mark it,
    # do not withdraw it.  On p03/p04 `R2-R4` the 7.00 rides on a difference of
    # 5110.00, i.e. 0.14% -- but the MARKER is still one draw, since the same
    # cell prints blank at half the phases.
    if (pat, lab) in PHASE_SWEEP or (pat, lab) in PHASE_SCREEN:
        s = (s + " ‡") if s else "‡"
    return s


# --------------------------------------------------------------------- census
_CTL_SRC = re.compile(r"^\s*(\w[\w.]*)\s+(?:from|<-)\s+(\S+)")
_RUNG_OF = {"safe_naive.rs": "R2", "safe_tuned.rs": "R3", "unsafe.rs": "R4",
            "verus.rs": "R5"}


def control_census(pat_dir, timeout=60):
    """DERIVED control census: run every `controls/*.py` that advertises a
    `--list` and count the entries it attributes to each rung's source file.

    It can print three things and never a wrong count: the attribution, or
    `--list, no source attribution`, or `no --list`.  ⚠ Five of the ten
    patterns with a `--list` are in the middle case (p06 p09 p22 p36 p38) --
    which is why this does not replace `SEARCH_REVIEWED`."""
    scripts = [s for s in sorted(glob.glob(os.path.join(pat_dir, "controls",
                                                        "*.py")))
               if "--list" in open(s, errors="replace").read()]
    if not scripts:
        return "no `--list`"
    counts, entries = {}, 0
    for s in scripts:
        try:
            r = subprocess.run([sys.executable, s, "--list"], timeout=timeout,
                               capture_output=True, text=True, cwd=REPO)
        except (subprocess.TimeoutExpired, OSError) as e:
            return f"`--list` failed: {type(e).__name__}"
        if r.returncode != 0:
            return f"`--list` exit {r.returncode}"
        for line in r.stdout.splitlines():
            m = _CTL_SRC.match(line)
            if not m:
                continue
            entries += 1
            k = _RUNG_OF.get(os.path.basename(m.group(2)),
                             os.path.basename(m.group(2)))
            counts[k] = counts.get(k, 0) + 1
    if not counts:
        return "`--list`, **no source attribution**"
    return ", ".join(f"{k} {counts[k]}" for k in sorted(counts))


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def outward_pin_status(outw, meas, read=None):
    """`{pattern: [reason, ...]}` -- empty list means FRESH. TASK_170 item D.

    Three comparisons, because the sidecar has three kinds of determinant:

      * `derived_from_sha256` -- the BUILD determinants, written by
        `outward_ir.py::repin`, which owns the definition and arms it;
      * `input_sha256` -- the blob, which no source hash can stand in for;
      * `n_iters` -- the per-call DIVISOR, which lives in the measurement
        record and is a VALUE, not a file.

    ⚠ A MISSING blob is *not* staleness, exactly as
    `measure.py::matrix_inputs`' docstring insists: the blobs are gitignored
    and running `inputs/gen.py` is the documented way to get them back. A
    checker that shouts STALE on a fresh clone is a checker that gets
    switched off, which is this whole item's argument.

    `read` is an injection point for the must-fire arms: `(relpath) -> sha256
    or None`. Nothing else passes it."""
    if read is None:
        def read(rel):
            p = os.path.join(REPO, rel)
            return _sha256_file(p) if os.path.isfile(p) else None
    out = {}
    for pat, d in sorted(outw.items()):
        if not isinstance(d, dict):
            continue
        why = []
        for rel, want in sorted((d.get("derived_from_sha256") or {}).items()):
            got = read(rel)
            if got is None:
                why.append(f"{rel} is GONE")
            elif got != want:
                why.append(f"{rel} moved")
        for rel, want in sorted((d.get("input_sha256") or {}).items()):
            got = read(rel)
            if got is not None and got != want:
                why.append(f"{rel} (blob) moved")
        for inp in ("small.bin", "large.bin"):
            side = d.get(inp)
            rec = (meas.get(pat) or {}).get("inputs") or {}
            if isinstance(side, dict) and inp in rec:
                if side.get("n_iters") != rec[inp].get("n_iters"):
                    why.append(f"{inp} n_iters {side.get('n_iters')} != "
                               f"record {rec[inp].get('n_iters')}")
        out[pat] = why
    return out


#: Must-fire arms for the pin comparison. Driven from `main`, printed into the
#: artefact, and each was SEEN TO FAIL under the regression its label names
#: (TASK_170, `.temp/t170/pin_status_break.py`).
_PIN_H = "a" * 64
_PIN_G = "b" * 64
_PIN_DOC = {"p90": {"derived_from_sha256": {"harness/build.py": _PIN_H},
                    "input_sha256": {"patterns/p90-x/inputs/small.bin": _PIN_H},
                    "small.bin": {"n_iters": 100}}}
_PIN_MEAS = {"p90": {"inputs": {"small.bin": {"n_iters": 100}}}}


def _pin_arm(reader):
    try:
        return outward_pin_status(_PIN_DOC, _PIN_MEAS, reader)["p90"]
    except Exception as e:                                    # noqa: BLE001
        return ["RAISED " + repr(e)]


PIN_STATUS_CASES = [
    ("everything matches -> FRESH",
     _pin_arm(lambda rel: _PIN_H), []),
    ("a BUILD determinant moved -> stale",
     _pin_arm(lambda rel: _PIN_G if rel.endswith("build.py") else _PIN_H),
     ["harness/build.py moved"]),
    ("a build determinant DELETED -> stale, and it says so differently",
     _pin_arm(lambda rel: None if rel.endswith("build.py") else _PIN_H),
     ["harness/build.py is GONE"]),
    ("the BLOB moved -> stale (no source hash can see this)",
     _pin_arm(lambda rel: _PIN_G if rel.endswith(".bin") else _PIN_H),
     ["patterns/p90-x/inputs/small.bin (blob) moved"]),
    ("⚠ a MISSING blob is NOT staleness -- a fresh clone has none",
     _pin_arm(lambda rel: None if rel.endswith(".bin") else _PIN_H), []),
    ("the n_iters DIVISOR moved -> stale",
     outward_pin_status(_PIN_DOC,
                        {"p90": {"inputs": {"small.bin": {"n_iters": 101}}}},
                        lambda rel: _PIN_H)["p90"],
     ["small.bin n_iters 100 != record 101"]),
    ("⚠ an UNPINNED entry is not reported STALE here -- `unpinned` is a "
     "separate list, and conflating them is how 33 false STALEs happened",
     outward_pin_status({"p90": {"small.bin": {"n_iters": 100}}}, _PIN_MEAS,
                        lambda rel: _PIN_G)["p90"], []),
]


def calibrate(meas, gates, outw):
    """Score the DERIVED column against the callgrind sidecar, live.

    This is the sidecar's only remaining job in this file: it is the evidence
    for the floor, not a published column.  A `miss` is the dangerous
    direction -- the derived route saying `< floor` where callgrind measured a
    real correction."""
    if not outw:
        return None
    s = {"rows": 0, "hit": 0, "miss": 0, "false alarm": 0}
    # TASK_107 §F: the staleness pin `outward_ir.json` did not have. Same
    # comparison `licence.json` already gets 20 lines below -- the sidecar
    # carries the gate `source_sha256` it was taken against, and a mismatch
    # means its rows describe sources that are no longer in the tree. It was
    # found THREE PATTERNS STALE (22 entries against 25) with nothing able to
    # say so, and `results/synthesis.md` printed the ABSENCE of the pin as a
    # caveat in its own text -- a warning is not a detector.
    #
    # ⚠⚠⚠ AND THE KEY IT COMPARED WAS THE WRONG ONE -- TASK_170 item D.
    # `gate_source_sha256` covers `check.py`, `vparse.py`, every `*.md`,
    # `model.py`, `inputs/gen.py` and `common/layout/*`, none of which the
    # sidecar reads, so ONE `check.py` docstring edit printed STALE on all 33
    # (TASK_168 P3) and every one of those STALEs was FALSE. RECAP item 37's
    # proposed replacement, `measure.py::measurement_sources`, was MEASURED at
    # TASK_169 §5e and again at TASK_170 (`.temp/t170/pin_probe.py`) and STILL
    # reports 4 of 33 (`p12 p13 p16 p38`), on `model.py`/`inputs/gen.py`
    # comment edits. The pin is now `derived_from_sha256` -- the BUILD
    # determinants only -- plus the blob and `n_iters`, written by
    # `outward_ir.py::repin`, which documents the set and arms it.
    st = outward_pin_status(outw, meas)
    s["stale"] = sorted(p for p, why in st.items() if why)
    s["stale_why"] = st
    s["unpinned"] = sorted(
        p for p, d in outw.items()
        if isinstance(d, dict) and not d.get("derived_from_sha256"))
    # bands[name] = [rows, real, spurious, smallest |correction| in the band]
    bands = {b: [0, 0, 0, None] for b in ("low", "mid", "high")}
    resid, misses = [], []
    for pat in sorted(meas):
        for inp in ("small.bin", "large.bin"):
            for a_, b_, lab in PAIRS:
                o = (((outw.get(pat) or {}).get(inp) or {})
                     .get("pairs") or {}).get(lab)
                c = derived_correction(meas, gates, pat, a_, b_, inp)
                if o is None or c is None:
                    continue
                s["rows"] += 1
                resid.append(abs(c - o["moves_by"]))
                pred, truth = abs(c) >= FLOOR, abs(o["moves_by"]) >= 5e-3
                if pred == truth:
                    s["hit"] += 1
                elif truth and not pred:
                    s["miss"] += 1
                    misses.append(f"{pat} {inp[:-4]} {lab} "
                                  f"{o['moves_by']:+.2f}")
                else:
                    s["false alarm"] += 1
                b = bands["low" if abs(c) < FLOOR
                          else "mid" if abs(c) < CONFIDENT else "high"]
                b[0] += 1
                b[1 if truth else 2] += 1
                b[3] = abs(c) if b[3] is None else min(b[3], abs(c))
    resid.sort()
    s["max_resid"] = resid[-1] if resid else None
    s["p95_resid"] = resid[int(.95 * len(resid))] if resid else None
    s["median_resid"] = resid[len(resid) // 2] if resid else None
    s["misses"] = misses
    s["bands"] = bands
    return s


def calibrate_licence(meas, lic, outw):
    """Score the LICENCE TAG against the same sidecar, live.

    `LICENSED` is a prediction that including the callees moves the pair
    difference by 0.00.  ⚠ This is recomputed on every run rather than quoted,
    because the score is a property of the sweep AND of the rule, and the rule
    has been corrected once already (TASK_075_REVIEW M4)."""
    if not outw or not lic:
        return None
    s = {"hit": 0, "false LICENSED": 0, "false alarm": 0, "abstain": 0}
    smallest, alarms = None, []
    for pat in sorted(meas):
        for inp in ("small.bin", "large.bin"):
            for _, _, lab in PAIRS:
                e = ((lic.get(pat) or {}).get("pairs") or {}).get(lab)
                o = (((outw.get(pat) or {}).get(inp) or {})
                     .get("pairs") or {}).get(lab)
                if e is None or o is None:
                    continue
                moves = abs(o["moves_by"]) >= 5e-3
                v = e["verdict"]
                if v not in ("LICENSED", "NOT-LIC"):
                    s["abstain"] += 1
                    continue
                if v == "NOT-LIC":
                    smallest = (abs(o["moves_by"]) if smallest is None
                                else min(smallest, abs(o["moves_by"])))
                if (v == "LICENSED") != moves:
                    s["hit"] += 1
                elif v == "LICENSED":
                    s["false LICENSED"] += 1
                else:
                    s["false alarm"] += 1
                    alarms.append(f"{pat} {inp[:-4]} `{lab}`")
    s["smallest_NOT-LIC_move"] = smallest
    s["alarms"] = alarms
    return s


def whole_mode_census(meas):
    """Every -O3 `whole` cell/input pair, and what its kernel column is.

    ⚠ The surviving symbol is NOT uniform, and this file asserted that it was
    until TASK_112 (TASK_111 M3).  It printed the four p46 rows carrying the
    WHOLE `kernel` symbol four lines above a sentence saying all twenty were
    `kernel.part.0` — PROTOCOL rule 13, the summary above the detail.  So the
    breakdown is DERIVED here and the prose is generated from it.
    """
    none_, kept = 0, []
    for pat, d in meas.items():
        for c in d["cells"]:
            if c["opt"] != "O3" or c["mode"] != "whole":
                continue
            for inp, v in (c.get("ir") or {}).items():
                if v.get("kernel_exclusive_ir") is None:
                    none_ += 1
                else:
                    kept.append((pat, c["cell"], inp,
                                 (v.get("kernel_functions") or ["?"])[0]))
    return none_, kept


def whole_mode_symbols(kept):
    """`{symbol: [(pat, cell, input), ...]}` over the surviving rows."""
    by_sym = {}
    for pat, cell, inp, sym in kept:
        by_sym.setdefault(sym, []).append((pat, cell, inp))
    return by_sym


def whole_mode_sentence(kept):
    """One sentence describing the survivors, true whatever the records say."""
    by_sym = whole_mode_symbols(kept)
    if not kept:
        return "there are no survivors at all"
    parts = ", ".join(
        f"{len(v)} are `{s}`"
        for s, v in sorted(by_sym.items(), key=lambda kv: -len(kv[1])))
    if len(by_sym) == 1:
        return (f"all {len(kept)} that DID keep a symbol are "
                f"`{next(iter(by_sym))}`")
    return (f"the {len(kept)} that DID keep a symbol carry "
            f"{len(by_sym)} DIFFERENT symbols — {parts}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--out", default=os.path.join(RESULTS, "synthesis.md"))
    a = ap.parse_args()

    meas, gates = load_measurements(), load_gates()
    lic = json.load(open(LICENCE)) if os.path.exists(LICENCE) else {}
    outw = json.load(open(OUTWARD)) if os.path.exists(OUTWARD) else {}
    L = []
    w = L.append

    w("# Cross-pattern synthesis")
    w("")
    w("Generated by `synthesis/synthesize.py` from **committed records** "
      "(`results/pNN-*.json`, `results/gate/pNN-*.json`). It builds nothing and "
      "measures nothing. Re-run it after any `harness/measure.py --check-stale` "
      "that is not `0 STALE`.")
    w("")
    w("**Both `Ir` columns are derived from those records, including the callee "
      "correction** — see §2. Three things are not, and each says so where it "
      "prints: the **licence tag** (`synthesis/licence.json`, a disassembly "
      "property pinned to the gate `source_sha256`), the **calibration** of the "
      "derived correction against a callgrind sweep "
      "(`synthesis/outward_ir.json`, evidence for a floor rather than a "
      "column), and the **reviewed search verdict**, which prints beside a "
      "control census this file derives by running each pattern's "
      "`controls/*.py --list`.")
    w("")
    w(f"Patterns: **{len(meas)}**. Gate records: **{len(gates)}**.")
    w("")

    # ---------------------------------------------------------------- limits
    w("## Read these four limits BEFORE the first number")
    w("")
    none_, kept = whole_mode_census(meas)
    by_sym = whole_mode_symbols(kept)
    gcc_only = all(c.startswith("c-gcc") for _, c, _, _ in kept)
    w(f"**1. Every number below is `-O3 isolated`, and there is no `whole` "
      f"column to compare it with.** Of the {none_ + len(kept)} `-O3` "
      f"`whole`-mode cell/input pairs in the tree, **{none_} have "
      f"`kernel_exclusive_ir = None`** -- the kernel inlined into `main` and "
      f"left no symbol. That much was already known (RECAP \"Owed\" 13). "
      f"⚠ **What is sharper: {whole_mode_sentence(kept)}**, and every one of "
      f"them is a `c-gcc` or `c-gcc-h` cell"
      f"{'' if gcc_only else ' -- EXCEPT that this run says otherwise, see the listing'}:")
    w("")
    w("```")
    for r in kept:
        w(f"  {r[0]:5s} {r[1]:9s} {r[2]:10s} {r[3]}")
    w("```")
    w("")
    part = by_sym.get("kernel.part.0", [])
    whole = [(s, v) for s, v in sorted(by_sym.items()) if s != "kernel.part.0"]
    w(f"⚠⚠ **THE SURVIVORS ARE NOT UNIFORM, AND THIS FILE ASSERTED THAT THEY "
      f"WERE UNTIL TASK_112** (TASK_111 M3). {len(part)} of the {len(kept)} "
      f"are `kernel.part.0`, gcc's partial-inlining remnant -- an *outlined "
      f"function remainder*, which is genuinely not the thing `isolated`'s "
      f"kernel column measures. But "
      + "; ".join(
          f"**{len(v)} carry the `{s}` symbol** ("
          + ", ".join(sorted({p for p, _, _ in v})) + "; "
          + ", ".join(sorted({c for _, c, _ in v})) + "; both blobs)"
          for s, v in whole)
      + " -- the whole symbol. **So the previous sentence here, *\"there is "
        "not one `whole`-mode row in the tree where the kernel column means "
        "what it means in `isolated`\"*, was FALSE for those rows, and the "
        "listing printed four lines above it said so.** (PROTOCOL rule 13: the "
        "summary line above the detail is not where anyone is looking.)")
    w("")
    w("**The isolated-only decision survives the correction and its "
      "justification changes.** The rows that do keep a whole `kernel` symbol "
      "are one pattern's C cells only, so they license no rung comparison and "
      "no cross-pattern column: there is nothing to compare them with in the "
      "same mode. Since p10 showed regressors SWAP between modes "
      "(`.memory/01-ladder.md` finding 18), everything here speaks for "
      "`isolated` and for nothing else.")
    w("")
    w("**2. The column is kernel-EXCLUSIVE, and its licence is stated per "
      "row.** `.memory/03-measurement.md`: the column is comparable only when "
      "the cells being differenced dispatch the *same* work outside the kernel "
      "symbol. The licence tag answers **only** that question — *may this row "
      "be differenced* — and never *by how much*; the magnitude is §2's derived "
      "column. Five tags, and **each is a distinct condition**:")
    w("")
    w("| tag | means |")
    w("|---|---|")
    w("| `LICENSED` | the two cells' live outward call multisets are **equal** |")
    w("| `NOT-LIC` | they are not: the difference in this table is **known to "
      "be wrong**, and the `why` under the table names what only one side calls |")
    w("| `UNDEC` | **both** sides dispatch through a pointer with no static "
      "target — a genuine limit of the disassembly |")
    w("| `NO-KSYM` | a cell has **no kernel symbol** (inlined away), so there "
      "is no column to license |")
    w("| `NOT-BUILT` | the `-O3 isolated` binary is **absent** — a tooling "
      "state, not a property of the pattern. **It cannot appear in this "
      "table**: `licence.py --emit` refuses to write a sidecar containing one |")
    w("")
    w("⚠ **The last two used to print as `UNDEC` under this legend's first "
      "sentence** (TASK_075_REVIEW M2). `.temp/build/` is gitignored and "
      "`CLAUDE.md` rule 1 tells agents to delete exactly those blobs, so "
      "re-emitting the licence on a cleaned tree turned all 88 verdicts into "
      "`UNDEC` — and this file republished them under a legend asserting all "
      "88 dispatched through an unresolvable pointer, with nothing failing "
      "anywhere because none of it is gate-checked. Now `--emit` exits **2** "
      "and writes nothing, naming the cells.")
    w("")
    w("⚠ **The callee-inclusive figure is LESS reproducible than the "
      "kernel-exclusive one it corrects — measured, not argued.** Two "
      "independent callgrind sweeps of the same binaries on the same blobs, "
      "differing only in **one added environment variable** "
      "(`SLB_ALIGN_PAD=z*64`, i.e. **+87 bytes** of environment block once the "
      "`envp` slot, the name and the NUL are counted — ⚠ **not +64**, and that "
      "difference is what made someone call this control vacuous; see the "
      "calibration section): **kernel-exclusive `Ir`/call moved in 0 of 348 "
      "(pattern, input, cell) triples; outward `Ir`/call moved in 11** — p03 "
      "and p04 `safe_tuned` on both blobs (`50.00 → 43.00`, glibc `memset`'s "
      "alignment-dependent path length, re-measured at TASK_099) and **p08 on "
      "seven cells** (`+0.0627`/`+0.0676` on `small`, `+0.0065` on `large` "
      "`unsafe`). p08's offset cancels within a language and so moves no "
      "verdict today; p03's and p04's does not.")
    w("")
    w("⚠ **The knob that produced the first version of this paragraph was "
      "INERT.** It said the two sweeps *\"differ only in the "
      "`--callgrind-out-file=` path, which is part of valgrind's argv and so "
      "shifts the client's stack\"*. Valgrind **strips its own options before "
      "building the client stack**: replicating the two paths at their exact "
      "lengths (97 and 99 characters) gives identical kernel-exclusive *and* "
      "identical outward figures. The environment block is the knob that works "
      "(`.memory/03-measurement.md`, `check.py::check_marginal_ir`). ⚠ **This "
      "line used to add *\"and it is scatter, not a trend\"*. That is p08's "
      "behaviour, not p03's and p04's**: theirs is **bistable with a 32-byte "
      "period and a 16-wide window** (`‡`, below), which is why a two-pad "
      "screen 16 apart detects all of it and a single contrast can miss "
      "nothing. The published `6 of 348` was a floor and its exposed-pattern "
      "list was short by one (TASK_075_REVIEW M1). "
      "**So the callee correction is an addition to the kernel-exclusive "
      "column and never a replacement for it**, and on p03 and p04 the "
      "kernel-exclusive column is the correct one.")
    w("")
    w("**3. `Ir` is not time, and three named mechanisms make them disagree "
      "in DIRECTION**: `rep`-string instructions counted once per repetition "
      "(p08), a hardware `div` priced at 1 (p05), and a latency-bound chain "
      "(p16). There is no wall-clock column here at all: this box's `ns` floor "
      "is a *session* property, so cross-pattern timing taken across 22 "
      "separate measurement sessions is not a measurement.")
    w("")
    w("**4. gcc's column carries mitigations clang's does not.** gcc defaults "
      "to `-fcf-protection=full`, so every gcc function opens with an "
      "`endbr64` IBT landing pad (`.memory/03-measurement.md`; on p36 that is "
      "`1.00000*nrw + 1` `Ir` per call). **Never attribute a gcc-vs-clang gap "
      "to codegen without naming it.** And two further gcc-only terms this "
      "file found: `__popcountdi2` on p09 (378.00 / 2625.00 `Ir` per call, "
      "libgcc's software popcount, absent from clang) and a 2-instruction PLT "
      "thunk on every gcc libc call (below).")
    w("")
    w("⚠ **And a per-process constant hiding inside a per-call column, which "
      "is why the thunk rows never read as a clean multiple of 2.00.** A "
      "one-off lazy-binding / IFUNC resolver call (**725–794 `Ir` per "
      "process**, present in clang's and rustc's binaries and not gcc's) is "
      "charged to whichever call site triggers it, and it scales as "
      "`1/n_iters` — **0.0065 … 0.5293 `Ir` per call** across this tree. It is "
      "why p11's thunk term reads `+299.87` where `150 × 2.00 = 300.00`, and "
      "it is the shape `.memory/03-measurement.md` already condemns for `ns`. "
      "The `large`-blob rows are quieter than the `small` ones for the same "
      "reason.")
    w("")
    w("Three standing rules govern every figure: **never the word "
      "\"minimum\"** -- write *cheapest found* and name the input, because on "
      "p03 and p16 the cheapest spelling changes with the blob; **no pair "
      "interval** unless the pattern has an admissible R4 that moves (p03 and "
      "p36 do, and both intervals this project published before that were "
      "built from rungs that do not exist); and **a law owes its domain** -- "
      "glibc's `rep stosb` threshold near `n = 2048` makes `Ir` report a cost "
      "rising 6.5x at the size the real cost falls.")
    w("")

    # ------------------------------------------------------------ levels
    w("## 1. Kernel-exclusive `Ir` per call, `-O3 isolated`")
    w("")
    w("*A `-` is a cell the pattern does not ship, not a missing measurement: "
      "the `-h` columns are the hardened C rungs, and p01 ships none.*")
    w("")
    w("| pattern | input | " + " | ".join(RUNGS) + " |")
    w("|---|---|" + "---:|" * len(RUNGS))
    for pat in sorted(meas):
        d = meas[pat]
        for inp in ("small.bin", "large.bin"):
            vals = [ir_per_call(d, r, "O3", "isolated", inp) for r in RUNGS]
            if vals[RUNGS.index("unsafe")] is None:
                continue
            w(f"| {d['pattern']} | {inp[:-4]} | "
              + " | ".join(fmt(v, 1) for v in vals) + " |")
    w("")

    # ------------------------------------------------------------ differences
    w("## 2. The differences the project argues about -- with their licence")
    w("")
    w(CALLEE_NOTE)
    w("")
    cal = calibrate(meas, gates, outw)
    if cal is None:
        w(f"⚠ **`synthesis/outward_ir.json` is absent, so the bands are "
          f"QUOTED and not recomputed.** Every corrected figure below is still "
          f"present — the derived column needs no sidecar at all. As last "
          f"measured (TASK_166, 33 patterns, 264 rows): `<{FLOOR:.2f}` "
          f"**175 rows, 5 REAL / 170 spurious**; "
          f"`{FLOOR:.2f}–{CONFIDENT:.2f}` **32 rows, 9 real / 23 spurious**; "
          f"`≥{CONFIDENT:.2f}` **57 rows, all real, smallest 17.00**. "
          f"⚠ The 22-pattern fit this line used to quote read "
          f"`120 rows, 0 real` in the low band; **it is not 0 any more**. "
          f"Re-emit the sidecar (`synthesis/outward_ir.py --emit "
          f"synthesis/outward_ir.json`, 524 callgrind runs, ~48 min against a "
          f"warm `.temp/build/`) to make this line live again.")
    else:
        w(f"**Calibration, recomputed on every run of this file** — the "
          f"derived column scored against `synthesis/outward_ir.json`, a "
          f"callgrind caller→callee sweep, at the {FLOOR:.2f} `Ir` floor: "
          f"**{cal['rows']} rows, {cal['hit']} hit, {cal['miss']} miss "
          f"(the dangerous direction), {cal['false alarm']} false alarm**; "
          f"residual median **{cal['median_resid']:.2f}**, p95 "
          f"**{cal['p95_resid']:.2f}**, max **{cal['max_resid']:.2f}**."
          + (f" ⚠ Misses: {', '.join(cal['misses'])}." if cal["misses"] else ""))
        w("")
        w("**So the column has three bands, and they are measured on every "
          "run rather than chosen** — each row sorted by `|correction|` "
          "against whether the sweep says the row moves at all:")
        w("")
        w("| band | rows | real | spurious | smallest \\|correction\\| | "
          "reading |")
        w("|---|---:|---:|---:|---:|---|")
        for key, lo, hi, mark, read in (
                ("low", None, FLOOR, "blank / `<2.00`",
                 "**not safe — this is one environment phase.** ⚠ See `‡`"),
                ("mid", FLOOR, CONFIDENT, "marked **?**",
                 "**a coin flip — do not quote alone**"),
                ("high", CONFIDENT, None, "**bold**",
                 "**every one is real**")):
            n, real, spur, small = cal["bands"][key]
            rng = (f"< {hi:.2f}" if lo is None
                   else f"≥ {lo:.2f}" if hi is None
                   else f"{lo:.2f} … {hi:.2f}")
            w(f"| `{rng}` ({mark}) | {n} | {real} | {spur} | "
              + (f"{small:.2f}" if small is not None else "-") + f" | {read} |")
        w("")
        _lo_n, _lo_real, _lo_spur, _ = cal["bands"]["low"]
        w(f"⚠⚠⚠ **THE `< {FLOOR:.2f}` BAND'S OWN CLAIM WAS FALSE, AND IT IS "
          f"NOW FALSE ARITHMETICALLY AND NOT ONLY IN ITS ADJECTIVE.** It read "
          f"*\"safe: nothing real hides below the floor\"*, scored "
          f"`0 real / 120 spurious` over a **22-pattern** fit. **This run "
          f"scores `{_lo_real} REAL / {_lo_spur} spurious`** — the misses "
          f"named in the calibration line above. ⚠ **They are not the seven "
          f"new rows**: re-scored at TASK_166 on the SAME 22 patterns with "
          f"today's records the floor already misses **4**, and the oracle did "
          f"not move to make it so (the committed 26-pattern sidecar and the "
          f"TASK_166 re-emit agree on 0 of 208 pair rows and 0 of 824 cell "
          f"figures). What moved is the DERIVED side, and nothing re-scored "
          f"the table when it did. So *\"{FLOOR:.2f} is the only threshold "
          f"that misses nothing\"* — this file's stated reason for the "
          f"constant — **is retracted**; what survives, and is re-measured, is "
          f"that {FLOOR:.2f} MINIMISES misses and carries the fewest false "
          f"alarms of any threshold that does.")
        w("")
        w("⚠ **The mechanism behind four of the misses was already published "
          "here and is unchanged:** **p03's and p04's `R3-R4` correction is "
          "`0.00` — blank, in this band — at 16 of 32 environment phases and "
          "`±7.00` at the other 16**, three and a half times the floor. A band "
          "scored at one draw cannot certify the absence of a term that is "
          "invisible at that draw. The rows that carry it are marked `‡` "
          "below. ⚠ **And the `‡` note below says the disagreement is on "
          "`R2-R4`; measured today it is on `R2-R4`, `R3-R4` AND `R5-R4` — 8 "
          "of p03/p04's 16 pair/blob rows disagree between the derived route "
          "and the sweep.** The band still means *the derived route cannot "
          "resolve this*; it no longer means *there is nothing here*.")
        w("")
        w("⚠ **The middle band is where p03, p04, p07 and p22 live.** On p03 "
          "and p04 `R5-R4` the derived route was reporting `+6.00`, one draw "
          "from `{−8.00, −1.00, +6.00}` — **tied with its own sign-reverse** — "
          "and those four cells are now **withdrawn** rather than marked "
          "**?**: `?` means *look further*, and there is nothing further to "
          "look at. Treat a surviving **?** as *\"look with the licence or a "
          "callgrind run\"*, never as a figure.")
        w("")
        # TASK_107 §F. This paragraph used to read "⚠ That sidecar is the only
        # thing in this file with no staleness pin", which was true and was a
        # WARNING rather than a DETECTOR -- the sidecar was found three patterns
        # stale (22 entries against 25) with nothing able to report it.
        # ⚠⚠ TASK_170 item D: the pin TASK_107 added was the GATE
        # `source_sha256`, and it was the WRONG KEY -- one `check.py` docstring
        # edit printed STALE on all 33 and every one of those was FALSE. The
        # comparison is now `outward_pin_status`, over the BUILD determinants
        # plus the blob plus the `n_iters` divisor.
        if cal["stale"] or cal["unpinned"]:
            w(f"⚠⚠ **`synthesis/outward_ir.json` IS STALE, so the calibration "
              f"above is scored partly on rows taken against sources that have "
              f"since moved.**"
              + (" **STALE: "
                 + "; ".join(f"{p} ({', '.join(cal['stale_why'][p][:3])})"
                             for p in cal["stale"]) + ".**"
                 if cal["stale"] else "")
              + (f" **No pin at all: {', '.join(cal['unpinned'])}.** Run "
                 f"`synthesis/outward_ir.py --repin synthesis/outward_ir.json`, "
                 f"which needs no callgrind." if cal["unpinned"] else "")
              + f" Re-emit with `synthesis/outward_ir.py --emit "
              f"synthesis/outward_ir.json` against a fully built `.temp/build/` "
              f"(352 callgrind runs), then re-run this file.")
        else:
            npin = sum(len(d.get("derived_from_sha256") or {})
                       for d in outw.values() if isinstance(d, dict))
            w(f"✅ **`synthesis/outward_ir.json` is FRESH** — all "
              f"{len(outw)} entries carry a pin and every one still matches: "
              f"**{npin} build-determinant hashes, {sum(len(d.get('input_sha256') or {}) for d in outw.values() if isinstance(d, dict))} "
              f"input blobs and the `n_iters` divisor**, compared by "
              f"`synthesize.py::outward_pin_status`. It was once found **three "
              f"patterns stale, 22 entries against 25**, and this file's own "
              f"text said the pin did not exist — a warning where a detector "
              f"was wanted. Re-emitting costs 352 callgrind runs against a "
              f"fully built `.temp/build/`, which is why it calibrates a "
              f"column here and no longer **is** one.")
        w("")
        w("⚠⚠ **AND THE PIN IT CARRIED UNTIL TASK_170 WAS THE WRONG KEY — "
          "which matters because a sidecar nobody will re-emit is a sidecar "
          "whose false STALE just gets ignored.** TASK_107 §F pinned the "
          "**gate** `source_sha256`, copied from `licence.json`. That digest "
          "covers `harness/check.py`, `harness/vparse.py`, every "
          "`patterns/*/*.md`, `model.py`, `inputs/gen.py` and "
          "`common/layout/*` — **none of which this sidecar reads, and none "
          "of which can move a callgrind number of an already-built binary.** "
          "One `check.py` docstring edit at TASK_168 therefore printed STALE "
          "on **all 33 entries, every one FALSE**, and stage 9b's own "
          "docstring had already argued against the key in terms: *\"a pin "
          "whose STALE does not mean 'the numbers are wrong' is a pin that "
          "gets switched off.\"* ⚠ **The obvious replacement — "
          "`measure.py::measurement_sources` — was MEASURED TWICE and is not "
          "the repair either: it still reports 4 of 33 STALE (`p12 p13 p16 "
          "p38`), on `model.py`/`inputs/gen.py` comment edits.** What is "
          "pinned now is the BUILD determinants only (the four rung sources, "
          "`c/*`, `common/driver.*`, `build.py`, `verus_run.py`) plus the blob "
          "and the divisor: **0 of 33 stale on the same evidence.** ✅ **And "
          "no callgrind run was needed to land it**: the old key was not one "
          "hash but the whole `path → sha256` map, so `outward_ir.py --repin` "
          "*filters that map* — the values below are still TASK_166's, taken "
          "at commit `6f5674f`. ⚠ **The one determinant that could not be "
          "verified retroactively is the blob for `p02 p05 p07 p11 p17`, "
          "whose measurement records predate TASK_035's provenance block and "
          "carry no `input_sha256`; 56 of 66 blobs were cross-checked and 0 "
          "mismatched.**")
        w("")
        bad_arms = [lab for lab, got, want in PIN_STATUS_CASES if got != want]
        w(f"*The pin comparison's own must-fire arms, run on every emission of "
          f"this file:* **{len(PIN_STATUS_CASES) - len(bad_arms)} of "
          f"{len(PIN_STATUS_CASES)} pass**"
          + ("." if not bad_arms else
             " — ⚠⚠ **FAILING: " + "; ".join(bad_arms) + "**.")
          + " They cover a moved determinant, a deleted one, a moved blob, a "
            "**missing** blob (which is NOT staleness — the blobs are "
            "gitignored and a fresh clone has none), a moved `n_iters`, and an "
            "entry with no pin at all.")
        w("")
        lc = calibrate_licence(meas, lic, outw)
        if lc:
            w(f"**And the LICENCE TAG scored against the same sweep, also "
              f"recomputed here**: **{lc['hit']} hit, "
              f"{lc['false LICENSED']} false `LICENSED` (the dangerous "
              f"direction), {lc['false alarm']} false alarm, "
              f"{lc['abstain']} abstain**. The smallest movement under a "
              f"`NOT-LIC` verdict is "
              f"**{lc['smallest_NOT-LIC_move']:.2f} `Ir`/call**.")
            w("")
            # ⚠⚠ THIS PARAGRAPH WAS TYPED UNDER A COMPUTED TRIPLE AND WENT
            # FALSE UNDERNEATH IT — the SECOND instance of §5 claim 1's defect
            # in this same file, 400 lines earlier, and no review found it
            # (TASK_159).  It asserted `0 false alarms` in three places while
            # the generated figure beside it read `2`.  It is derived now.
            if lc["false alarm"] == 0:
                w("✅ **`0 false alarms` is a statement about this sweep, not "
                  "about the rule** (TASK_075_REVIEW M4) — which is why this "
                  "line is recomputed rather than quoted. It holds on this "
                  "run.")
            else:
                w(f"⚠⚠ **THE `0 false alarms` THIS FILE USED TO ASSERT IS GONE "
                  f"— IT NOW READS `{lc['false alarm']}`, AND THE PARAGRAPH "
                  f"THAT ASSERTED IT WAS TYPED UNDER A COMPUTED TRIPLE.** "
                  f"(Found at TASK_159; it is §5 claim 1's defect a second "
                  f"time, in this same file.) The sentence used to read "
                  f"*\"the smallest movement under a `NOT-LIC` verdict is X, "
                  f"so 0 false alarms is robust to any tolerance below "
                  f"that\"* — and the smallest movement is now "
                  f"**{lc['smallest_NOT-LIC_move']:.2f}**, which is not a "
                  f"margin at all: it IS the false alarms. The rows are "
                  f"**{', '.join(lc['alarms'])}**. ⚠ *A `NOT-LIC` on a row "
                  f"the sweep says does not move is the SAFE direction* — the "
                  f"rule refused to license a difference that would have been "
                  f"fine — so nothing published is wrong because of it; what "
                  f"was wrong is the file saying there were none.")
            w("")
            w("⚠ **The score is a property of the sweep, not of the rule.** "
              "Correcting one thing the rule got right for a contradicted "
              "reason (`kernel.cold`, below) moved it from `156 / 10 / 0 / 10` "
              "to `154 / 12 / 0 / 10` at TASK_076, by converting p27's "
              "`gcc-clang` from a lucky `NOT-LIC` into an honest false "
              "`LICENSED`; a second sweep under a **longer environment block** "
              "read `152 / 14 / 0 / 10`, the excess being p03's and p04's "
              "`memset` term. ⚠⚠ **Those three historical triples are quoted "
              "as history and NOT as the current score** — the live figures "
              "are the ones in the sentence above, and they have moved.")
            w("")
            w("⚠ **That control was called VACUOUS on an arithmetic slip, and "
              "it is not** (TASK_098 BLOCKER 2, TASK_099 §A2; re-measured "
              "here). The reading was *\"a 64-byte pad is `64 mod 32 == 0`, "
              "i.e. the same alignment phase as pad 0, so the second sweep "
              "could not have moved\"*. But the sweep does not lengthen an "
              "existing variable — `.temp/p75rev/envsweep.py` **adds** one, "
              "`SLB_ALIGN_PAD=z*64`, so the block grows by "
              "`8 (envp slot) + 14 (\"SLB_ALIGN_PAD=\") + 64 + 1 (NUL) = 87` "
              "bytes and `87 mod 32 = 23`. **Measured directly at TASK_099** "
              "(`.temp/t99/a2_phase.py`, one callgrind run per environment): "
              "the block grows by exactly **+87 bytes**, and p03 `safe_tuned`'s "
              "glibc `memset` goes **300129 → 258129 Ir** whole-process, "
              "which is `129 + 50.00*6000` against `129 + 43.00*6000` at "
              "`n_iters = 6000` — **exactly the `50.00 → 43.00` per kernel "
              "call** that this "
              "paragraph is about, reproduced in a different session. **The "
              "control fired.** ⚠ It is still ONE contrast rather than a "
              "period, which is what `‡` is for.")
    w("")

    # ---------------------------------------------- the per-pattern null, `†`
    nulls = sorted(((p, i, r5_null(meas, gates, p, i))
                    for p in sorted(meas) for i in ("small.bin", "large.bin")),
                   key=lambda r: -abs(r[2] or 0.0))
    over = [r for r in nulls if r[2] is not None and abs(r[2]) >= FLOOR]
    rest = max((abs(r[2]) for r in nulls if r not in over and r[2] is not None),
               default=0.0)
    planted, live, live_note = null_rule_selftest(meas, gates)
    w("⚠⚠ **`†` — A PATTERN'S OWN NULL, AND IT OUTRANKS THE TREE-WIDE BANDS.** "
      "The bands above are scored across the tree. But `identity` forces R4's "
      "and R5's kernels to agree — `check.py::check_identity` compares their "
      "`-O3 isolated` digests — so on **this column** each "
      "pattern's own `R5 - R4` correction is a **measured null**: a number "
      "that ought to be 0.00 and is not. It is not small everywhere:")
    w("")
    w("| pattern | blob | own `R5 - R4` null |")
    w("|---|---|---:|")
    for p, i, v in over:
        w(f"| {p} | {i[:-4]} | {v:+.2f} |")
    w(f"| *every other row* | | *≤ {rest:.2f}* |")
    w("")
    w(f"**So a correction no bigger than its own pattern's null is not "
      f"resolvable here, and this file no longer promotes one to a band.** "
      f"`†` marks such a row and prints the null beside it. The rule is "
      f"`|correction| <= |null|` with `|null| >= {FLOOR:.2f}` — a null inside "
      f"the global floor is what *every* pattern reads and refuses nothing — "
      f"and it is **not applied to the `R5-R4` column itself**, because a "
      f"control cannot be its own control: scored against itself that column "
      f"refuses every row it prints, at a ratio of exactly 1.00x.")
    w("")
    if live:
        w("**Rows the rule moved on this run** — derived, not listed:")
        w("")
        w("| pattern | blob | pair | correction | band it would have had | "
          "own null | ratio |")
        w("|---|---|---|---:|---|---:|---:|")
        for p, i, lab, c, n in live:
            was = "**bold** (≥ CONFIDENT)" if abs(c) >= CONFIDENT else "`?`"
            w(f"| {p} | {i} | `{lab}` | {c:+.2f} | {was} | {n:+.2f} | "
              f"{abs(n) / abs(c):.2f}x |")
        w("")
    else:
        w("**No row on this run is at or below its own pattern's null.**")
        w("")
    w(f"✅ **The rule's own controls, run on every invocation of this file** "
      f"(`null_rule_selftest`; it raises rather than publishing if any arm "
      f"disagrees). {len(planted)} planted arms — "
      f"{sum(1 for n, _, _ in planted if n.startswith('MUST-FIRE'))} must-fire, "
      f"{sum(1 for n, _, _ in planted if n.startswith('silent'))} silent — plus "
      f"a {live_note}:")
    w("")
    w("| arm | verdict |")
    w("|---|---|")
    for n, got, _ in planted:
        w(f"| {n} | `{got}` |")
    w("")
    w("⚠⚠ **THE NULL TABLE ABOVE IS `-O3 isolated` AND THREE ARTEFACTS "
      "PUBLISH IT WITH TWO `-O0` ROWS IN IT.** `RECAP.md` finding 60, "
      "`.memory/03-measurement.md` entry 23 and `.tasks/TASK_159.md` all print "
      "*\"R4/R5 null, -O3 ISOLATED (the published column): p28 1732.73 · "
      "p29 425.80 · p25 269.52 · p42 31.00 · everything else <= 6.00\"*. "
      "**`p28 1732.73` and `p29 425.80` are `-O0 isolated` cells.** At "
      "`-O3 isolated` — the level this file publishes and the only level the "
      "corrections above are taken at — **p28 reads `+1.01` and p29 reads "
      "`−0.02`**; that quoted list is the max over ISOLATED at *both* levels. "
      "The mode fix (TASK_158 M1, `whole` excluded) was right and the LEVEL "
      "was not fixed with it. ⚠ *\"Real exposure is FOUR patterns\"* is "
      f"likewise `-O0 isolated`'s count: at `-O3 isolated` **{len(over)} rows "
      f"across {len({p for p, _, _ in over})} patterns** clear the "
      f"{FLOOR:.2f} floor and "
      f"**{len({p for p, _, v in over if abs(v) >= CONFIDENT})}** reach "
      f"{CONFIDENT:.2f}. ✅ **The three affected published numbers survive "
      "the correction unchanged** — they are `-O3 isolated` rows scored "
      "against `-O3 isolated` nulls, and p28's and p29's `-O0` figures never "
      "touched them.")
    w("")
    w(BULK_CALLS_NOTE)
    w("")

    # ------------------------------------------------------- `§`, TASK_170 E
    cross = regime_crossing(outw)
    w("⚠⚠ **`§` — A CORRECTION THAT CROSSES A LIBC BULK-ROUTINE THRESHOLD: "
      "REGIME-DEPENDENT, AND NOT COMPARABLE WITH THE REST OF THIS COLUMN.**")
    w("")
    w("`Ir` counts instructions. A bulk fill or copy changes its "
      "**instructions per byte by roughly 10×** across a size threshold — and "
      "in the direction that makes the counter *wrong*: `rep stosb` is what "
      "the hardware runs **because it is fast**, so `Ir` reports the cost "
      "**rising 6.5× at exactly the size the real cost falls** "
      "(`.memory/03-measurement.md`'s zero-fill probe: 326.30 `Ir` at "
      "n = 1024, **2106.94** at n = 2048 — ⚠ that probe is TASK_074's and "
      "`.memory/` marks it **PROVISIONAL, not yet reviewed**, so it is "
      "quoted as the direction and the size of the jump, not as a "
      "constant). A difference taken across that "
      "threshold is **real work**, priced in a regime no other row here is "
      "in — so the number stands, its band stands, and its **magnitude is not "
      "comparable** with a sub-threshold row.")
    w("")
    w("⚠⚠ **NO DISCOUNT FACTOR IS PUBLISHED, AND THE ONE THAT WAS DRAFTED IS "
      "WITHDRAWN.** The gloss *\"~90% of the term is counter, not code\"* "
      "rested on a `≈426 Ir` vector-path counterfactual that was glibc "
      "**`memcpy`**'s own 4092-byte figure (`0.104 Ir`/byte) re-badged as a "
      "**`memset`** counterfactual — two libc routines, two thresholds, one "
      "quoted at the other (TASK_169 §3b). **There is no measured "
      "vector-path counterfactual for these fills, so no percentage may be "
      "quoted**, and *\"the work is not there\"* would be false anyway: on "
      "p42 one rung zeroes 4096 bytes and the other does not.")
    w("")
    if cross:
        w("**The marked ROWS are derived; the ROUTINE SET is a WHITELIST.** "
          "`synthesize.py::regime_crossing` requires a bulk routine's "
          "contribution to be **asymmetric across the pair** by at least "
          f"{FLOOR:.2f} `Ir` **and** at least one side to be in the byte-wise "
          "regime. The regime is read off the routine's own `Ir` per call "
          "against its measured crossover, because the sidecar has no byte "
          "count: below `0.10 Ir`/byte a call of `C` `Ir` implies `10C` "
          "bytes, so a small `C` **forces** the vector path and a large one "
          "**forces** the byte-wise path.")
        w("")
        w("⚠⚠ **This file used to call the marked set *\"DERIVED rather than "
          "listed\"*. That was withdrawn at TASK_171 and it is corrected "
          "here:** `synthesize.py::BULK_REGIME` is "
          f"**{len(BULK_REGIME)} hand-classified keys**, two of them bare "
          "glibc load addresses that a glibc bump would silently retire. What "
          "makes it a whitelist is not the names but the pair `(lo, hi)` — the "
          "routine's own byte-count crossover — which **a sidecar carrying "
          "`Ir` per call and no byte count cannot supply**, so a "
          "routine-independent signature rule is not available here. It is "
          "printed in full rather than described:")
        w("")
        w("| callee key | routine | forced VECTOR below | forced BYTE-WISE "
          "above | cells in the sidecar |")
        w("|---|---|---:|---:|---:|")
        for k_, (nm_, lo_, hi_) in sorted(BULK_REGIME.items()):
            _, _, ncell = sidecar_callee_peak(outw, k_)
            w(f"| `{k_}` | {nm_} | {lo_:.2f} `Ir`/call | {hi_:.2f} `Ir`/call "
              f"| {ncell} |")
        w("")
        w(f"**The {len(cross)} (pattern, blob, pair) row(s) that clear both "
          f"tests, and why:**")
        w("")
        w("| pattern | blob | pair | why |")
        w("|---|---|---|---|")
        for (p_, i_, l_), ev in sorted(cross.items()):
            w(f"| {p_} | {i_[:-4]} | `{l_}` | " + " · ".join(ev) + " |")
        w("")
        w("⚠⚠ **THE *\"no callee edge under this key\"* CLAUSE IS NOT A "
          "MEASUREMENT OF *\"the other side does not call it\"* ON A "
          "`gcc-clang` ROW, AND IT USED TO SAY IT WAS.** This file printed "
          "*\"while the other side does not call it at all\"*, which is **true "
          "by construction** rather than measured (TASK_171 §1a(iii), RECAP "
          "finding 67(d)): on a `gcc-clang` pair the two cells do not share a "
          "key space, because gcc-built cells report their libc callees under "
          "**the client's own PLT address** while clang-built cells report the "
          "**libc** address. Re-derived at TASK_172 on the marked pattern "
          "itself: `p08 c-gcc` carries the SAME `memmove` at **39.0** "
          "`Ir`/callee-call under key `0x0004001160` against `c-clang`'s "
          "**39.4** under `0x188a80` — the delta is the extra thunk. On "
          "`memset` the clause happens to be true (gcc inlines it, as `rep "
          "stos %rax`); on `memmove` the identical sentence would have been "
          "false. **The census got the right answer on `p08` for a reason it "
          "had not established**, and the clause now names the KEY rather "
          "than the call.")
        w("")
        w("⚠ **Two things this census settles that marking `p42` by hand "
          "would not have.** (a) **`p08 gcc-clang` is marked and nobody had "
          "noticed**: gcc inlines the same 4096-byte fill as a 512-`Ir` "
          "`rep stos %rax` while clang calls glibc `memset` at 4113.00 `Ir` "
          "— identical work, 8× apart, inside a published row. (b) **p08's "
          "rung pairs are NOT marked**, correctly: the 4113.00 `Ir` `memset` "
          "is in *all four* Rust cells, so it cancels out of `R2-R4`, "
          "`R3-R4` and `R5-R4` exactly. ⚠ And **`§` is per BLOB**: p42's "
          "`R2-R4` is marked on `large` (the fill is 4342.00 `Ir`) and not "
          "on `small` (189.01 `Ir`, forced vector) — the same code, the same "
          "rung pair, two regimes.")
    else:
        w("**No row qualifies today.**")
    w("")
    w("⚠ **The first spelling of this census found `p42` and nothing else, "
      "which is the flattering answer.** In `synthesis/outward_ir.json` the "
      "glibc routines carry **no symbol at all** — they are bare addresses — "
      "so a name regex misses every one of them and reports only the "
      "Rust-named `__rust_alloc_zeroed`. `0x189480` and `0x188a80` are "
      "resolved in `.memory/03-measurement.md`.")
    w("")

    # ------------------------------------------- what the whitelist misses
    # TASK_172 item B. The whitelist's silence is turned into a printed,
    # derived census, and the two routines TASK_171 named get a MEASURED
    # verdict instead of an absence.
    unc = unclassified_bulk_candidates(outw)
    lo_min = min(lo for _, lo, _ in BULK_REGIME.values())
    hi_min = min(hi for _, _, hi in BULK_REGIME.values())
    over_hi = {k: e for k, e in unc.items()
               if e["max_ir_per_callee_call"] >= hi_min}
    over_lo = {k: e for k, e in unc.items()
               if e["max_ir_per_callee_call"] >= lo_min}
    w(f"⚠⚠ **AND HERE IS WHAT THE WHITELIST DOES NOT DECIDE, DERIVED RATHER "
      f"THAN ASSERTED.** Every callee **not** in `BULK_REGIME` that "
      f"contributes asymmetrically by at least {FLOOR:.2f} `Ir` on a published "
      f"pair is the population a complete census would have to rule on: "
      f"**{len(unc)} distinct callee keys across "
      f"{sum(e['rows'] for e in unc.values())} published rows** "
      f"(`synthesize.py::unclassified_bulk_candidates`). Scored against the "
      f"smallest crossover any *classified* routine has — forced VECTOR below "
      f"**{lo_min:.2f}** `Ir`/callee-call, forced BYTE-WISE above "
      f"**{hi_min:.2f}** — **{len(over_hi)} clear the byte-wise bound** and "
      f"**{len(over_lo)} clear even the vector bound**"
      + (":" if over_lo else "."))
    if over_lo:
        w("")
        w("| unclassified callee | max `Ir`/callee-call | rows | patterns |")
        w("|---|---:|---:|---|")
        for k_, e in sorted(over_lo.items(),
                            key=lambda kv: -kv[1]["max_ir_per_callee_call"]):
            nm_ = NAMED_UNCLASSIFIED.get(k_)
            short = k_ if len(k_) <= 92 else k_[:91] + "…"
            w(f"| `{short}`" + (f" — {nm_}" if nm_ else "")
              + f" | {e['max_ir_per_callee_call']:.2f} | {e['rows']} | "
              + " ".join(e["pats"]) + " |")
    w("")
    named = []
    for k_ in ("0x0000000000188080", "0x000000000018b7c0"):
        pk, where, ncell = sidecar_callee_peak(outw, k_)
        if pk is not None:
            named.append(f"{NAMED_UNCLASSIFIED[k_]} peaks at **{pk:.2f}** "
                         f"`Ir`/callee-call over the whole sidecar "
                         f"({ncell} cells, max at `{where}`), "
                         f"**{lo_min / pk:.0f}×** under the bound")
    if named:
        w("✅ **This settles the two routines TASK_171 named as the "
          "whitelist's silence, and it settles them with a MEASUREMENT rather "
          "than with a name.** " + "; ".join(named)
          + f". The bound is the {lo_min:.2f} `Ir`/callee-call figure that "
            f"**forces** the vector path under every crossover this project "
            f"has resolved, so both routines are in the VECTOR regime on every "
            f"cell they appear in: they cannot trigger the mark, and adding "
            f"them to the whitelist would change **no row**. Their asymmetry "
            f"on six published `gcc-clang` rows is real and is a "
            f"*callee-resolution* asymmetry, not a regime one.")
        w("")
    dl = "0x0000000000015220"
    dlpk, dlwhere, dlcells = sidecar_callee_peak(outw, dl)
    if dlpk is not None and dl not in unc:
        w(f"⚠ **And the single biggest callee in the whole sidecar is excluded "
          f"by the FLOOR rather than by a name**, which is the same point from "
          f"the other side: `{dl}` — {NAMED_UNCLASSIFIED[dl]} — reads "
          f"**{dlpk:.2f}** `Ir` per callee-call ({dlcells} cells, max at "
          f"`{dlwhere}`), the largest figure here and above the byte-wise "
          f"bound, and it appears in the census above **not at all**. It is "
          f"the lazy-binding resolver, invoked once per program rather than "
          f"once per kernel call, so its contribution to every published "
          f"difference is under {FLOOR:.2f} `Ir`. **No rule had to know its "
          f"name.**")
        w("")
    w("⚠ **The limit of that scoring, stated rather than hidden:** it uses "
      "the crossovers of the routines this project has *resolved*. A bulk "
      "routine whose own crossover sat far below every resolved one would be "
      "byte-wise while reading under "
      f"{lo_min:.2f} `Ir`/callee-call, and **a sidecar with no byte count "
      "cannot tell**. Nothing on this tree is near that case: the largest "
      "unclassified figure above is a Rust `drop_glue` over a 32-element "
      "array, which has no size regime at all.")
    w("")
    w("⚠⚠ **AND THE CENSUS IS STRUCTURALLY BLIND TO AN INLINED BULK "
      "INSTRUCTION, WHICH IS A KNOWN PUBLISHED ROW AND NOT A HYPOTHETICAL.** "
      "It reads `outward_by_callee_per_call`, so a bulk fill the compiler "
      "emits *inline* produces **no callee edge and cannot be seen at all**. "
      "`p27 gcc-clang` is exactly that (TASK_169, upheld at TASK_171 §1c): "
      "gcc emits `rep stos` for 32 `Ir` inside `<kernel>` and clang emits "
      "18 `movaps` + 1 `xorps` = 19, both **inline**, and the 13-`Ir` "
      "difference is **52% of that row's published `−25.02`**. It is not "
      "marked, and **non-marking is not evidence the row is clean** — a "
      "census that cannot see a row says nothing about it. ⚠ The same is "
      "true of the marked pattern's own gcc side: `p08 c-gcc` inlines its "
      "4096-byte fill as `rep stos %rax`, so `p08 gcc-clang` is marked **only "
      "because clang calls out**, and a pair where *both* sides inlined would "
      "be silently unmarked.")
    w("")

    for a_, b_, lab in PAIRS:
        show_search = lab in ("R2-R4", "R3-R4")
        w(f"### `{lab}`  (`{a_}` - `{b_}`)")
        w("")
        w(f"*`corrected (derived)` is blank when **both** blobs' derived "
          f"corrections are inside the ±{FLOOR:.2f} `Ir` floor; a cell marked "
          f"**?** is in the {FLOOR:.2f}–{CONFIDENT:.2f} band and means *look "
          f"further*, not a figure; **bold** is ≥{CONFIDENT:.2f}. The three "
          f"bands are scored above. ⚠ **`†` marks a cell at or below its own "
          f"pattern's `R5 - R4` null and is NOT promoted to a band at all** — "
          f"the null prints beside it. ⚠ **`‡` marks a cell whose correction "
          f"is a phase of the environment block rather than a property of the "
          f"code**, and **`§` a cell whose correction crosses a libc "
          f"bulk-routine threshold and is therefore regime-dependent** — see "
          f"the notes above and below the table.*")
        w("")
        if show_search:
            w("⚠ The last column is the **R3/R4 spelling search state**, and it "
              "is the reason this table cannot be read as a per-pattern "
              "property: see claim 2 in §5.")
            w("")
        w("| pattern | small | large | licence | corrected (derived)"
          + (" | R3/R4 search state |" if show_search else " |"))
        w("|---|---:|---:|---|---|" + ("---|" if show_search else ""))
        whys = []
        for pat in sorted(meas):
            d = meas[pat]
            v = [None, None]
            for i, inp in enumerate(("small.bin", "large.bin")):
                x = ir_per_call(d, a_, "O3", "isolated", inp)
                y = ir_per_call(d, b_, "O3", "isolated", inp)
                v[i] = None if x is None or y is None else x - y
            if v[0] is None and v[1] is None:
                continue
            pl = (lic.get(pat) or {})
            entry = (pl.get("pairs") or {}).get(lab) or {}
            verd = entry.get("verdict", "no licence recorded")
            if pl.get("gate_source_sha256") and pat in gates and \
                    pl["gate_source_sha256"] != gates[pat].get("source_sha256"):
                verd = "LICENCE STALE"
            # ⚠ Include LICENSED rows whose `why` carries an UNPRICED warning:
            # p27's `gcc-clang` is exactly the row where a LICENSED verdict is
            # known to be wrong, and dropping its `why` would hide that.
            if entry.get("why") and (verd != "LICENSED"
                                     or "UNPRICED" in entry["why"]):
                whys.append(f"- **{pat}** `{verd}` — {entry['why']}")
            corr = derived(meas, gates, pat, a_, b_, lab, cross)
            s = SEARCH_REVIEWED.get(pat)
            w(f"| {d['pattern']} | {fmt(v[0], 1)} | {fmt(v[1], 1)} | {verd} "
              f"| {corr} |"
              + (f" {s[0] if s else 'undeclared'} |" if show_search else ""))
        w("")
        marked = sorted({p for (p, l) in list(PHASE_SWEEP) + list(PHASE_SCREEN)
                         if l == lab})
        if marked:
            w(f"⚠ **`‡` — the environment-phase term, and it is not noise.** "
              f"The derived correction is a **whole-program** figure, so it "
              f"contains the callees; a per-call `memset` of a **stack** array "
              f"takes an alignment-dependent tail in "
              f"`__memset_avx2_unaligned_erms`, and the initial stack pointer "
              f"moves with the **length of the environment block**. The effect "
              f"is bistable, period **32 bytes**, window exactly **16 wide**, "
              f"and the phase differs per binary — so one rung can sit high "
              f"while another sits low and **a pair swings by 14, not 7**. "
              f"Per row, with its instrument:")
            w("")
            for p in marked:
                src = ("2-pad screen `.temp/r98/treescan_*.json`"
                       if (p, lab) in PHASE_SCREEN
                       else "32-pad sweep `.temp/r98/sweep.py`, one full "
                            "period, both blobs")
                w(f"- **{p}** `{lab}` — {_phase_note(p, lab)} "
                  f"*({src}; TASK_098, reviewed)*"
                  + ("  ⟵ **WITHDRAWN above**"
                     if (p, lab) in WITHDRAWN else ""))
            w("")
            w(f"**The kernel-exclusive columns beside them are immune** — a "
              f"callee is not in a per-function exclusive count, and under the "
              f"same perturbation **0 of 288** (pattern, input, cell) triples "
              f"moved on that column while **14 of 288** marginals did. So "
              f"where the two disagree on "
              f"{', '.join('**' + p + '**' for p in marked)}, **the "
              f"kernel-exclusive column is the one that reproduces** "
              f"(`.memory/03-measurement.md`, "
              f"`check.py::check_marginal_ir`).")
            w("")
        if whys:
            w(f"⚠ **Why each non-`LICENSED` row is not licensed, plus every "
              f"`LICENSED` row carrying an unpriced term** — the `why` string "
              f"`licence.py` recorded. An earlier version of this file printed "
              f"the tag and dropped this, which is how three different "
              f"conditions came to share one tag (limit 2). "
              f"`⚠ UNPRICED` counts **live** `@plt` sites and means the row "
              f"carries gcc's 2-instruction PLT thunk at `+2.00 Ir` per "
              f"*dynamic* libc call — a count no static check can have:")
            w("")
            for x in whys:
                w(x)
            w("")
        if lab == "gcc-clang":
            tags = [((lic.get(p) or {}).get("pairs") or {})
                    .get(lab, {}).get("verdict") for p in sorted(meas)]
            w(f"⚠ **This is the pair in trouble, not `R3-R4`.** "
              f"{tags.count('NOT-LIC')} of {len(meas)} are `NOT-LIC` and "
              f"{tags.count('UNDEC')} more is undecidable — every C-vs-C "
              f"statement in the tree runs through this column. Two gcc-only "
              f"terms, both measured here and neither previously recorded:")
            w("")
            w("* **`__popcountdi2`, p09** — gcc emits a call to libgcc's "
              "software popcount that clang inlines; **378.00 / 2625.00 "
              "`Ir` per call**, against a published gap of 7322 / 25908. It "
              "is not a bulk routine, so it appears in no record.")
            w("* **a 2-instruction PLT thunk on every gcc libc call.** gcc's "
              "`memcpy@plt` is `endbr64 ; jmp *GOT`, which callgrind "
              "attributes as its own function; clang's is a bare `jmp` and is "
              "folded into the callee. Measured: **+2.00 `Ir` per libc call, "
              "gcc's column only** — p02 `+2.00` (1 call/kernel-call), p12 "
              "`+23.99` (6 × 2.00 + resolution), p11 `+299.87` (150 `strlen` "
              "calls × 2.00), with the libc work itself *identical* "
              "(`strlen` inclusive 2105.0288 gcc / 2105.0265 clang). **One of "
              "the two instructions is the `endbr64` of gcc's default "
              "`-fcf-protection=full`**, so the corrected column carries an "
              "IBT term the kernel-exclusive column never had. It is an "
              "argument for publishing both columns, not for replacing one "
              "with the other.")
            w("")
            w("⚠ **Two `gcc-clang` verdicts were right for reasons the "
              "measurement contradicts** (TASK_075_REVIEW M4), and the thunk "
              "is what actually carried both. It is a **dynamic** term — "
              "`2.00 × libc calls per kernel call` — and the licence is a "
              "**static** check, so it cannot see it at all.")
            w("")
            w("* **p27** was `NOT-LIC` because *\"only `c-gcc` calls "
              "`kernel.cold`\"*. `kernel.cold`'s entire body is "
              "`call abort@plt` — it executes **zero** times in any accepted "
              "run — **and it matches `measure.py::_sum_rows`'s own kernel "
              "needle** `(?:^|::)kernel(?:$|[^A-Za-z0-9_])`, so if it ever "
              "executed its cost would land *inside* `kernel_exclusive_ir`, "
              "not outside it. It cannot make the column incomparable in "
              "either state. `licence.py` now filters kernel siblings, and "
              "**p27's `gcc-clang` is `LICENSED` — which is an honest false "
              "`LICENSED`**, because the row does move, by `+40.02` = 20 libc "
              "calls × 2.00, all of it thunk.")
            w("* **p47** is `NOT-LIC` on `memcmp@plt` against `bcmp@plt`. With "
              "call counts those are **literally the same address "
              "`0x188320`** — glibc aliases them and p47's own reviewed "
              "`NOTES.md` says clang rewrites `memcmp(...) == 0` into `bcmp` — "
              "and the entire `+7.96` the row moves by is the thunk (4 calls "
              "× 2.00 − the resolver). The verdict is **kept**: a static check "
              "cannot know that two dynamic names resolve to one address, and "
              "an alias whitelist is the shape this check exists to avoid. "
              "But the `why` no longer stands alone.")
            w("")
            w("The `why` strings above now carry an **`⚠ UNPRICED`** clause "
              "wherever a `gcc-clang` pair has an `@plt` call site, whichever "
              "way the verdict went. The call **sites** are static and "
              "countable; the per-call **count** is not.")
            w("")

    # ------------------------------------------------- proof burden and TCB
    w("## 3. Proof burden and trusted base")
    w("")
    w("From `results/gate/*.json` (`verus`, `identity`, `verdict`). "
      f"`obligations` is what Verus verified for `{TCB_SRC}`; `TCB` counts the "
      "`external_body` / `assume`d items the proof rests on and `TCB lines` "
      "their bodies. **`R4 = R5` identity is the thing the `Ir` column cannot "
      "establish**: quote the digest, not the zero (`.memory/01-ladder.md` "
      "finding 1). The `R4=R5 @O3` column is the entry whose `pair` is "
      f"`{R5_PAIR}` — p01 ships **two** `-O3` identity pairs and an earlier "
      "version of this file took whichever came first (TASK_075_REVIEW m6).")
    w("")
    w("⚠ **`axioms` is a SEPARATE column and is deliberately not folded into "
      "`TCB items`, because the two are not the same kind of thing.** A TCB "
      "item is **usually** an `#[verifier::external_body]` wrapper with a body "
      "a reviewer can read and an `ensures` that can be checked against real "
      "Rust semantics. ⚠ **Two corrections, both measured (TASK_084_REVIEW "
      "major 2), because an earlier version of this paragraph overstated "
      "both:** since TASK_084 a bodied `#[verifier::external_fn_specification]` "
      "*also* counts as a TCB item — and `.memory/05-layout.md` records that it "
      "and `assume_specification` are **one mechanism**, so the split between "
      "these two columns is *has a reviewable body*, not *is a different kind "
      "of trust*. And the twin-and-`(a)/(b)/(c)` requirement does NOT cover "
      "every published item: `load_input` and `emit` "
      f"({_n_named('load_input')} and {_n_named('emit')}, one per pattern) are "
      "`external_body` with **no `ensures`**, so `_is_trusted` is "
      "false and nothing is demanded of them. ⚠ **These counts are COMPUTED "
      "from the records every run — an earlier version hardcoded them and went "
      "stale the moment a pattern was added.** An "
      "**axiom** is a hand-written claim about code Verus never compiles: "
      "`assume_specification`, `axiom fn`, `uninterp spec fn`, "
      "`#[verifier::external_trait_specification]`. It has **no body**, so it "
      "adds **0** to `TCB lines`; it adds no verified function, so "
      "`obligations` does not move; it emits no instructions, so `R4=R5 @O3` "
      "does not move; and the form Verus's own error message prints for you "
      "to paste carries **no `requires` and no `ensures` at all**, which "
      "verifies a 1 MiB out-of-bounds read and a null dereference at "
      "`4 verified, 0 errors` (`.memory/04-verus.md`). One column would let a "
      "7-line reviewed wrapper be traded for a zero-line unconditional axiom "
      "**at par**, and nothing in the table would move.")
    w("")
    w("**So the trusted base of a row is `TCB items` + `axioms`, and the "
      "totals below are reported that way rather than summed.** ⚠⚠ **The "
      "`axioms` column counts PATTERN-LOCAL declarations only, and reading `0` "
      "does NOT mean this tree rests on no hand-written axiom — an earlier "
      "version of this paragraph claimed exactly that and it is FALSE "
      "(TASK_084_REVIEW major 2).** All "
      f"**{_n_broadcast()}** of the **{_n_verus_rs()}** `verus.rs` carry "
      "`broadcast use`, and `vstd::slice::group_slice_axioms` alone is six "
      "`broadcast axiom fn`s in the pinned vstd (`vstd/slice.rs:186`); ten also "
      "import `group_array_axioms`, and `lemma_u128_shr_is_div` appears 23 "
      "times. **Every published number here rests on hand-written axioms. They "
      "are vstd's, they are pinned, and they are outside this column by "
      "construction**. ⚠ **A USED vstd "
      "`assume_specification` declares nothing locally and is invisible here "
      "too** (RECAP \"Owed\" 0, sixth route). The gate has carried "
      "`axiom_decls` per Verus source since TASK_082; nothing published read "
      "it, so a byte-identical regeneration was **not** evidence that nothing "
      "moved (TASK_083_REVIEW major 4).")
    w("")
    # ⚠⚠⚠ TASK_166 item D, from TASK_165 MAJOR 1 (option B). THE SENTENCE THAT
    # USED TO SIT HERE -- *"a `0` says THIS PATTERN'S AUTHOR WROTE NONE OF
    # THEIR OWN"* -- WAS FALSE ON TEN ROWS, and the `0 axioms` total was read
    # with it. `_check_axiom_decls` partitions the `global` directive OUT of
    # `verus.axioms` (TASK_164's deviation, reviewed SURVIVES-NARROWED), so a
    # hand-written `global layout` / `global size_of` is invisible in that
    # column. The count is NOT changed here -- changing it would demand a
    # declaration on 10 patterns, 10 `contract_sha256` moves and a full sweep.
    # ⚠ What is fixed is the REPORTING: `global` is published beside `axioms`
    # as its own column and its own total, and the prose says what a `0` in
    # each column does and does not mean.
    n_glob_rows = sum(1 for g in gates.values()
                      if any((v.get("global_decls") or [])
                             for v in (g.get("verus") or {}).values()))
    w(f"⚠⚠ **AND A `0` IN THE `axioms` COLUMN DOES NOT MEAN THIS PATTERN'S "
      f"AUTHOR WROTE NO HAND-WRITTEN DECLARATION OF THEIR OWN — "
      f"{n_glob_rows} of the {len(gates)} rows below carry a `global` "
      f"directive, and every one of them prints `0 axioms`.** This paragraph "
      f"said the opposite until TASK_166 (TASK_165 MAJOR 1). Verus's `global "
      f"layout` / `global size_of` is hand-written, pattern-local, and the "
      f"Verus guide describes it as *exporting the **axioms** "
      f"`size_of::<T>() == n` and `align_of::<T>() == m`*; for `usize` it also "
      f"narrows the SMT integer range. The gate deliberately partitions it out "
      f"of `verus.axioms` — **rustc const-checks a `global` and rejects a "
      f"false one with `E0080`**, so it is not an unchecked claim the way an "
      f"`assume_specification` is, and stage 5e catches the rejection "
      f"(TASK_164, re-derived and extended at TASK_165). ✅ **So the two "
      f"columns answer different questions and are published side by side: "
      f"`axioms` is *what nothing checks*, `global` is *what the author "
      f"declared and rustc checks*.** ⚠ **Neither is zero for this tree, and "
      f"quoting `0 axioms` alone understates the hand-written declarations on "
      f"{n_glob_rows} rows.**")
    w("")
    w("| pattern | obligations | errors | TCB items | TCB lines | axioms | "
      "global | R4=R5 @O3 | verdict |")
    w("|---|---:|---:|---:|---:|---:|---:|---|---|")
    tot_ob = tot_tcb = tot_lines = tot_ax = tot_glob = 0
    # ⚠ **THE TOTALS DEDUPE THE `#[path]`-INCLUDED ROWS** (`TASK_084_REVIEW`
    # minor 1). `common/driver.rs` is included by all 23 `verus.rs`, so ONE
    # axiom or ONE trusted item there lands in all 23 records. The per-row `1`
    # is right -- every one of those patterns' binaries executes it -- but the
    # column total then reads 23 for one item, and the prose below tells the
    # reader to quote the total. Distinct key: `(source, name, line)`.
    shared_ax, shared_tcb, shared_glob = set(), {}, set()
    extra_srcs = {}
    for pat in sorted(gates):
        g = gates[pat]
        vall = g.get("verus") or {}
        vb = vall.get(TCB_SRC) or {}
        # R5's trusted base: `verus.rs`'s own items and axioms, plus everything
        # in the files it `#[path]`-includes. The gate keys an included file by
        # its path relative to the repo root and flags it `path_included`
        # (`check.py::_verus_file_list`); an axiom or an `external_body` in
        # `common/driver.rs` is licensed by this pattern's proof and executed by
        # this pattern's binary, so it belongs in this row.
        #
        # ⚠ **`tcb_items` on an included row is TASK_088**, and it is what makes
        # a planted `external_body ... ensures r == 0` in an included module
        # MOVE THIS TABLE. Before it, route J of `TASK_084_REVIEW` shipped green
        # with `grep -c <name> gate.log` == 0 and a byte-identical
        # `synthesis.md`: the gate did not look and this column could not see.
        own_ax = list(vb.get("axiom_decls") or [])
        own_items = list(vb.get("tcb_items") or [])
        own_glob = list(vb.get("global_decls") or [])
        inc_ax, inc_items, inc_glob = [], [], []
        for k, v in sorted(vall.items()):
            if v.get("path_included"):
                inc_ax += [dict(d, src=k) for d in (v.get("axiom_decls") or [])]
                inc_items += [dict(d, src=k) for d in (v.get("tcb_items") or [])]
                inc_glob += [dict(d, src=k)
                             for d in (v.get("global_decls") or [])]
        ax = own_ax + inc_ax
        glob = own_glob + inc_glob
        items = own_items + inc_items
        lines = sum(i.get("body_lines", 0) for i in items)
        others = {k: v for k, v in sorted(vall.items())
                  if k != TCB_SRC and not v.get("path_included")}
        if others:
            extra_srcs[g["pattern"]] = others
        lvl = next((e["level"] for e in g.get("identity", [])
                    if e.get("opt") == "O3"
                    and e.get("pair") == R5_PAIR), "-")
        tot_ob += vb.get("verified", 0)
        tot_tcb += len(own_items)
        tot_lines += sum(i.get("body_lines", 0) for i in own_items)
        tot_ax += len(own_ax)
        tot_glob += len(own_glob)
        for d in inc_ax:
            shared_ax.add((d.get("src"), d.get("name"), d.get("line")))
        for d in inc_glob:
            shared_glob.add((d.get("src"), d.get("name"), d.get("line")))
        for d in inc_items:
            shared_tcb[(d.get("src"), d.get("name"), d.get("line"))] = \
                d.get("body_lines", 0)
        w(f"| {g['pattern']} | {vb.get('verified', '-')} | "
          f"{vb.get('errors', '-')} | {len(items)} | {lines} | {len(ax)} | "
          f"{len(glob)} | {lvl} | {g.get('verdict', '-')} |")
    n_shared_ax, n_shared_tcb = len(shared_ax), len(shared_tcb)
    n_shared_glob = len(shared_glob)
    tot_glob += n_shared_glob
    tot_ax += n_shared_ax
    tot_tcb += n_shared_tcb
    tot_lines += sum(shared_tcb.values())
    w(f"| **total** | **{tot_ob}** | | **{tot_tcb}** | **{tot_lines}** | "
      f"**{tot_ax}** | **{tot_glob}** | | |")
    w("")
    w(f"**Trusted base, all {len(gates)} rows: {tot_tcb} items ({tot_lines} "
      f"lines), {tot_ax} axioms and {tot_glob} `global` directives on "
      f"{n_glob_rows} rows.** Quote all three; there is no single one. "
      f"⚠ **`{tot_ax} axioms` on its own is the number this file used to "
      f"print, beside prose saying a `0` meant the author wrote nothing of "
      f"their own — see the warning above the table.**")
    w("")
    w(f"⚠ **The totals are DISTINCT counts, not column sums, and the rows are "
      f"not** (`TASK_084_REVIEW` minor 1, fixed at TASK_088). Every pattern's "
      f"`verus.rs` `#[path]`-includes the same `common/driver.rs`, so one "
      f"trusted item or one axiom there is real in every row and would be "
      f"counted {len(gates)} times in a column sum. The rows above add the "
      f"shared file's items because that row's binary executes them; the "
      f"totals add each `(source, name, line)` **once**. Today the shared file "
      f"contributes **{n_shared_tcb} item(s)**, **{n_shared_ax} axiom(s)** and "
      f"**{n_shared_glob} `global` directive(s)**, "
      f"so the two agree — the dedupe is measured inert and is here for the "
      f"day it is not.")
    w("")
    # ---- the DERIVED disclosure of every Verus source this table skipped ----
    w(f"*This table reads **one** Verus source per pattern, `{TCB_SRC}` — the "
      "R5 rung's. The list below is derived from the records on every run, so "
      "a pattern that grows a second pinned source announces itself here "
      "instead of being silently dropped.*")
    w("")
    if not extra_srcs:
        w(f"*No pattern pins a Verus source other than `{TCB_SRC}`.*")
    else:
        w("| pattern | other pinned Verus source | obligations | TCB items | "
          "axioms | global | why it is not in the row above |")
        w("|---|---|---:|---:|---:|---:|---|")
        for pat in sorted(extra_srcs):
            for src, v in sorted(extra_srcs[pat].items()):
                why = ("the **R2v control**: safe Rust carrying the same "
                       "proof, which holds up `.memory/01-ladder.md` finding "
                       "2 (*a proof alone buys nothing*). It is not a rung "
                       "and is not in the measured 6-cell matrix, so its "
                       "trusted base is not R5's and summing the two would "
                       "publish a number describing no rung."
                       if src == "safe_naive_verus.rs" else
                       "**not a known control — this source is unclassified "
                       "and its trusted base is unaccounted for above.**")
                w(f"| {pat} | `{src}` | {v.get('verified', '-')} | "
                  f"{len(v.get('tcb_items') or [])} | "
                  f"{len(v.get('axiom_decls') or [])} | "
                  f"{len(v.get('global_decls') or [])} | {why} |")
    w("")

    # --------------------------------------------------------- static shape
    w("## 4. Static shape, `-O3 isolated`")
    w("")
    w("`n_fn_nopad` is the padding-excluded instruction count of the kernel "
      "symbol at its declared `nm` extent. **A static count is not a cost "
      "model** (`.memory/03-measurement.md`): on the pilot the 32-instruction "
      "gcc kernel executed 125 019 `Ir` where the 37-instruction LLVM one "
      "executed 87 520. It is here as *assembly*, one of `CLAUDE.md`'s five "
      "axes, not as a proxy for work.")
    w("")
    w("*Each cell is `n_fn_nopad`, then `/` and **the first letter of every "
      "entry in the record's `static.vector_regs`**. Every populated entry in "
      "the tree today is `[\"xmm\"]`, so the only suffix that appears is `/x`; "
      "a `/xy` would be `xmm` and `ymm`. No `/` means the record lists no "
      "vector register. A `-` is a cell the pattern does not ship.*")
    w("")
    w("| pattern | " + " | ".join(f"{r} n/vec" for r in RUNGS) + " |")
    w("|---|" + "---|" * len(RUNGS))
    for pat in sorted(meas):
        d = meas[pat]
        cs = []
        for r in RUNGS:
            hit = [c for c in d["cells"]
                   if (c["cell"], c["opt"], c["mode"]) == (r, "O3", "isolated")]
            st = (hit[0].get("static") or {}) if hit else {}
            if not st:
                cs.append("-")
            else:
                cs.append(f"{st.get('n_fn_nopad', '?')}"
                          + ("/" + "".join(v[0] for v in st.get("vector_regs", []))
                             if st.get("vector_regs") else ""))
        w(f"| {d['pattern']} | " + " | ".join(cs) + " |")
    w("")

    # --------------------------------------------- the three claims, scored
    w("## 5. The three claims the probe exposed, each scored")
    w("")
    w("`.temp/synth/aggregate.py` produced three provisional, unreviewed "
      "claims (RECAP \"Owed\" 13). They are re-derived here from the records.")
    w("")

    # claim 1
    bad, rows_seen = [], 0
    for pat, d in sorted(meas.items()):
        for inp in ("small.bin", "large.bin"):
            x = ir_per_call(d, "verus", "O3", "isolated", inp)
            y = ir_per_call(d, "unsafe", "O3", "isolated", inp)
            if x is None or y is None:
                continue
            rows_seen += 1
            if x != y:
                bad.append((pat, inp, x - y))
    norel = sorted(p for p, g in gates.items()
                   if any(e.get("opt") == "O3" and e.get("pair") == R5_PAIR
                          and e["level"] != "exact"
                          for e in g.get("identity", [])))
    exact = sorted(p for p, g in gates.items()
                   if p not in norel
                   and any(e.get("opt") == "O3" and e.get("pair") == R5_PAIR
                           for e in g.get("identity", [])))
    # where the callee correction breaks the zero, DERIVED from the records
    broke, broke_rows = [], []
    for pat in sorted(meas):
        for inp in ("small.bin", "large.bin"):
            c = derived_correction(meas, gates, pat, "verus", "unsafe", inp)
            k = ir_per_call(meas[pat], "verus", "O3", "isolated", inp)
            k2 = ir_per_call(meas[pat], "unsafe", "O3", "isolated", inp)
            if c is None or k is None or k2 is None or abs(c) < FLOOR:
                continue
            # ⚠ Do NOT reprint a figure §2 withdrew. This list is *which rows
            # clear the floor*, which is still true of them at this phase; the
            # number is what has no value.
            broke.append(f"{pat} {inp[:-4]} "
                         + ("**WITHDRAWN** `‡`" if (pat, "R5-R4") in WITHDRAWN
                            else f"{k - k2 + c:+.2f}"))
            broke_rows.append((pat, inp, c))
    w(f"**Claim 1 -- `R5 - R4 = 0.00` on every row. SCOPED, and it is a "
      f"TAUTOLOGY rather than a result.** Re-derived: **{len(bad)} of "
      f"{rows_seen}** `-O3 isolated` pattern/input rows differ from 0.00. But "
      f"at `-O3` the gate records `identity: exact` for the `{R5_PAIR}` pair "
      f"on {len(exact)} patterns and `norel` for {len(norel)} "
      f"({', '.join(norel)}) -- and *both* levels force `Ir` equality here. "
      f"`exact` means the machine code is byte-identical, so the entailment is "
      f"immediate.")
    w("")
    w("⚠ **`norel` does NOT entail it in general, and this file used to say it "
      "did** (TASK_075_REVIEW m3). `md5_fn_norel` **zeroes branch-displacement "
      "fields**, so `je +0x10` and `je +0x20` normalise to the same digest — a "
      "`norel` pair *can* differ in control flow and therefore in how many "
      "instructions execute. What licenses the claim is a **check on the one "
      f"pattern it applies to**: p36's six differing instruction texts are "
      "five branches at **identical relative offsets** (`+0xa7 +0x64 +0x8d "
      "+0x40 +0x64`) plus one rip-relative `lea` to the dispatch table. So the "
      "zero holds for p36 by inspection, not by entailment.")
    w("")
    w("Two consequences: the evidence for *\"a proof costs zero "
      "instructions\"* is the raw-byte digest, not this column "
      "(`.memory/01-ladder.md` finding 1); and the zero is column-specific -- "
      "on p16's whole-program **marginal** the same pair reads **-1.00**, the "
      "driver's.")
    w("")
    if broke:
        mid = [r for r in broke_rows if abs(r[2]) < CONFIDENT]
        high = [r for r in broke_rows if abs(r[2]) >= CONFIDENT]
        w(f"⚠ **And the zero does NOT survive the callee correction.** On the "
          f"derived callee-corrected column `R5 - R4` clears the "
          f"±{FLOOR:.2f} floor on {len(broke)} rows -- {', '.join(broke)} -- "
          f"i.e. *\"the proof costs instructions\"* between two "
          f"**byte-identical** kernels.")
        w("")
        w(f"⚠⚠ **THIS PARAGRAPH USED TO BE TYPED UNDER A COMPUTED LIST, AND "
          f"IT WAS FALSE.** It read *\"every one of those rows is in the "
          f"uncertain {FLOOR:.2f}–{CONFIDENT:.2f} band\"* and resolved *\"on "
          f"all six\"* over a **seven**-row list containing "
          f"`p42 large −31.00`, which is `≥ {CONFIDENT:.2f}` and prints in "
          f"**bold** in §2 — three internal disagreements in one claim "
          f"(TASK_158 M4). It is now derived from the same list. "
          f"**{len(mid)} of the {len(broke)} rows are in the "
          f"{FLOOR:.2f}–{CONFIDENT:.2f} band and {len(high)} "
          f"{'is' if len(high) == 1 else 'are'} at or above "
          f"{CONFIDENT:.2f}**, and they do not resolve the same way:")
        w("")
        for pat, inp, c in broke_rows:
            why = R5_ROW_WHY.get((pat, inp)) or R5_ROW_WHY.get((pat, None))
            band = "**≥ CONFIDENT**" if abs(c) >= CONFIDENT else "mid"
            if why is None:
                w(f"- ⚠⚠ **{pat} {inp[:-4]} {c:+.2f} — UNRESOLVED.** No "
                  f"decomposition is recorded for this row, so nothing here "
                  f"licenses reading it as zero. *(This bullet is generated: "
                  f"a row with no entry in `R5_ROW_WHY` prints as unresolved "
                  f"rather than being swept into a summary sentence.)*")
            else:
                w(f"- **{pat} {inp[:-4]}** {c:+.2f} ({band}) — {why}")
        w("")
        w(f"**The kernel-exclusive zero is the correct reading on all "
          f"{len(broke)}** — every row above is a difference between two "
          f"kernels the `identity` pin makes agree, and every one that has "
          f"been decomposed puts 100 % of the delta *outside* the kernel "
          f"symbol. ⚠ **What does not follow, and what §2's `†` now enforces, "
          f"is that these rows are harmless to the REST of the table**: a "
          f"pattern that reads `{max((abs(c) for _, _, c in broke_rows), default=0):+.2f}` "
          f"here cannot also resolve a correction smaller than that on any "
          f"other pair.")
        w("")

    # claim 2
    neg = {}
    for pat, d in sorted(meas.items()):
        for inp in ("small.bin", "large.bin"):
            x = ir_per_call(d, "safe_tuned", "O3", "isolated", inp)
            y = ir_per_call(d, "unsafe", "O3", "isolated", inp)
            if x is not None and y is not None and x - y < 0:
                neg.setdefault(pat, []).append((inp[:-4], x - y))
    w(f"**Claim 2 -- `R3 - R4` is negative on {len(neg)} of {len(meas)} "
      f"patterns. CONFIRMED as arithmetic, and the reason it was doubted is "
      f"the WRONG reason.**")
    w("")
    w("| pattern | negative on | licence for `R3-R4` | callee correction "
      "(derived) | search state |")
    w("|---|---|---|---|---|")
    for pat in sorted(neg):
        pl = (lic.get(pat) or {}).get("pairs", {}).get("R3-R4", {})
        s = SEARCH_REVIEWED.get(pat)
        w(f"| {meas[pat]['pattern']} | "
          + ", ".join(f"{i} {v:.2f}" for i, v in neg[pat]) + " | "
          + pl.get("verdict", "-") + " | "
          + (derived(meas, gates, pat, "safe_tuned", "unsafe", "R3-R4",
                      regime_crossing(outw))
             or f"inside the ±{FLOOR:.2f} floor") + " | "
          + (s[0] if s else "undeclared") + " |")
    w("")
    w("The argument that scheduled this work said the claim rests *\"at its "
      "two biggest numbers, on the column the tree has caught reversing a "
      "comparison three times\"*, naming **p11 and p13** as *\"precisely the "
      "two patterns whose `.memory/` entries already say their rungs dispatch "
      "different work outward\"*.")
    w("")
    w("⚠ **The licence is a property of the PAIR, not of the PATTERN, and "
      "that is the whole defect.** `.memory/03-measurement.md` says of p13, "
      "verbatim: *\"`c-gcc` calls `strlen`; `c-clang` calls `strlen` + "
      "`memcpy` + `memset`; `safe_naive` calls `memset` only; **R3/R4/R5 call "
      "`memcpy` + `memset`**\"* -- R3 and R4 are grouped **together** in the "
      "sentence being cited, and the two figures p13's rule moved are "
      "`gcc-vs-clang` and **`R2 - R4`**. Likewise p11's 12.0x library factor "
      "is C-`strlen` against Rust-`memchr`, an **R1-vs-R3** factor.")
    w("")
    w("Derived from committed records, by the arithmetic at the top of this "
      "section — **no disassembly, no callgrind, no sidecar**:")
    w("")
    w("```")
    w(f"{'':5s} {'':6s} {'kernel-excl':>12s} {'correction':>12s} "
      f"{'corrected':>12s}")
    for pat in ("p10", "p11", "p12", "p13", "p18"):
        for inp in ("small.bin", "large.bin"):
            c = derived_correction(meas, gates, pat, "safe_tuned", "unsafe", inp)
            k = ir_per_call(meas[pat], "safe_tuned", "O3", "isolated", inp)
            k2 = ir_per_call(meas[pat], "unsafe", "O3", "isolated", inp)
            if c is None or k is None or k2 is None:
                continue
            w(f"{pat:5s} {inp[:-4]:6s} {k - k2:12.2f} {c:12.2f} "
              f"{k - k2 + c:12.2f}"
              + ("   <- SIGN FLIPS" if (k - k2) * (k - k2 + c) < 0 else ""))
    w("```")
    w("")
    w("**Four of the five named patterns are unaffected, exactly.** Only "
      "**p11** moves, and only its `small` row reverses. The independent "
      "callgrind sweep puts p11's correction at `+9821.15 / +7124.34` against "
      "the derived `+9815.56 / +7116.78` — 0.06% and 0.11% apart, which is the "
      "one-off resolver term (limit 4) that the marginal construction cancels "
      "and the single-run figure does not. **So the defect is real and it is "
      "ONE pattern, not five**, and the pattern the argument called *\"the one "
      "that established the rule\"* (p13) is a clean 0.00 on both blobs by both "
      "routes.")
    w("")
    w("⚠ **What the claim does NOT survive is the SEARCH objection, which "
      "nobody raised.** `R3 - R4` differences two rungs searched to wildly "
      "different depths, and every time a side has been searched the number "
      "moved a long way: p10's -323/-603 becomes **-129/-241** against a "
      "verifying R4 candidate (60% of the margin was R4 spelling); p13's "
      "-177/-1054 becomes **+44/+77** -- *sign flip* -- against a bounded "
      "unchecked consumer that verifies 19/0 with no new trusted item; p12's "
      "-26.00 becomes **+66.00** -- *sign flip* -- against route A, which "
      "verifies 15/0 with twin 18/0 and holds `R4 = R5 exact`; p36 "
      "refuses to publish a single number at all. **THREE of the six negatives "
      "in this table are known to move and every one of the three moves "
      "AGAINST the safe rung; p11's cheaper R4 exists and is inadmissible at "
      + (f"the pin; **{', '.join(sorted(set(neg) - set(SEARCH_REVIEWED)))} "
         f"still ha{'s' if len(set(neg) - set(SEARCH_REVIEWED)) == 1 else 've'}"
         f" an undeclared search state.** "
         if set(neg) - set(SEARCH_REVIEWED) else
         "the pin; and every row in this table now DECLARES its search "
         "state.** ")
      + "So the "
      "honest reading is that the column is partly measuring search effort. "
      "That is what the aggregate genuinely adds: it makes an unsearched R4 "
      "side a *systematic* problem instead of a per-pattern footnote. "
      "⚠ **p12 was in this list printing `undeclared` until TASK_112**, "
      "although TASK_040_REVIEW had built its cheaper R4 and `.memory/` "
      "records it -- so the sentence above understated its own case by one "
      "row for as long as the column existed. ⚠⚠ **AND THE CLAUSE ABOVE WAS "
      "TYPED, NOT DERIVED, FOR THE SAME REASON:** it read *\"only p18 and p46 "
      "have an undeclared search state\"* and stayed in the artefact after "
      "TASK_170 declared both — the identical defect one paragraph below its "
      "own confession. It is now computed from `SEARCH_REVIEWED` and cannot "
      "say a number the dict does not. ⚠ **`declared` still does not mean "
      "`searched deeply enough`** — the three sign flips above are all rows "
      "that were declared at the time.")
    w("")
    w("**Claim 3 -- a cross-pattern `Ir` comparison is available in "
      "`isolated` mode ONLY. CONFIRMED and SHARPENED** -- see limit 1 above. "
      "The count in RECAP (*\"of 318 `-O3` cell/input pairs, `whole` has "
      "`kernel_exclusive_ir = None` in 302\"*) reads as if 318 were the total; "
      f"it is the `whole`-mode subtotal. Today: {none_ + len(kept)} "
      f"`whole`-mode pairs, {none_} `None`, and "
      f"{whole_mode_sentence(kept)} (limit 1).")
    w("")

    # ------------------------------------------------------- provenance
    w("## 6. Where the non-derived columns come from")
    w("")
    w("**Both `Ir` columns above are derived from committed records**, "
      "including the callee correction (§2). Three things are not:")
    w("")
    w("**Licence tag and `why`** — `synthesis/licence.json`, emitted by "
      "`synthesis/licence.py` from the built `-O3 isolated` matrix. Each entry "
      "carries the gate `source_sha256` it was taken against; a mismatch "
      "prints `LICENCE STALE` above instead of a verdict. It answers *may this "
      "row be differenced*, never *by how much* — a different question from "
      "the derived column, not a second route to it.")
    w("")
    w("**Calibration of the derived column** — `synthesis/outward_ir.json`, "
      "emitted by `synthesis/outward_ir.py`, one callgrind run per cell, "
      "parsing the caller→callee edges the annotation discards. It is scored "
      "against the derived column on every run of this file (§2) and supplies "
      "**no published figure**. ⚠ Until TASK_107 it carried **no staleness pin "
      "at all**; it now carries the gate `source_sha256` per pattern, the same "
      "key `licence.json` uses, and §2 prints its status on every run. It "
      "stays a calibration rather than a column because re-emitting it needs "
      "352 callgrind runs against a fully built `.temp/build/`.")
    w("")
    w("**R3/R4 search state** — two things side by side, because neither alone "
      "is honest.")
    w("")
    w("*Derived*, by running each pattern's `controls/*.py --list` (this is "
      "the only place this file executes anything, and it executes committed "
      "Python, never a compiled binary):")
    w("")
    w("| pattern | controls registered, by source file |")
    w("|---|---|")
    for pat in sorted(meas):
        pdir = os.path.join(REPO, "patterns", meas[pat]["pattern"])
        w(f"| {pat} | {control_census(pdir)} |")
    w("")
    w("⚠ **TASK_075_REVIEW M6 prescribed deriving the lever count this way for "
      "\"the 10 patterns that expose a `--list`\" and deleting the declared "
      "table. Measured, that cannot be done.** Ten patterns expose a `--list` "
      "and **five of them print no source file at all** (p06 p09 p22 p36 p38); "
      "the other five split two ways (`from x.rs` on p10 and p47, `<- x.rs` on "
      "p03, p04 and p12). **p36 — the review's own worked example — is in the "
      "first group**: its `--list` prints `r3_hdr4  rust`, the *language*. "
      "Deriving p36's split from the `r3_`/`r4_` **name prefix** instead gives "
      "4 R3 and **2** R4, while `.memory/01-ladder.md` finding 23 says **3** "
      "R4 — so the derivation-by-convention rots in the same direction the "
      "hand table does and less visibly. The census above is therefore built "
      "to degrade to *\"no source attribution\"* rather than to a wrong count.")
    w("")
    # ⚠ SET DIFFERENCE, not a difference of lengths. The old spelling
    # (`len(meas) - len(SEARCH_REVIEWED)`) prints the right number only while
    # every key is also a measured pattern, and prints a SMALLER one -- never a
    # larger -- the moment a key is not. A published count that can only fail
    # in the flattering direction is exactly the shape this section is about.
    undecl = sorted(set(meas) - set(SEARCH_REVIEWED))
    n_undecl = len(undecl)
    # ⚠ TASK_172 item C, and it is the SAME defect as `n_undecl` above one
    # paragraph down: `n_found` was `declared - n_none`, a RESIDUAL, so the
    # three entries whose cited artefact is the OPEN BACKLOG were counted as
    # reporting a search RESULT. The split is three ways, and each way is a set.
    owed_primary, owed_mentions = backlog_cited()
    declared = SEARCH_REVIEWED.keys() & set(meas)
    n_owed = len(set(owed_primary) & declared)
    # ⚠ `n_none` was scored against `SEARCH_REVIEWED` while the denominator
    # is `declared`, so an entry for an unmeasured pattern would have
    # inflated it. All three buckets are now scored on the same set.
    n_none = len(SEARCH_NONE & declared)
    n_found = len(declared) - n_none - n_owed
    w("*Declared*, in `synthesize.py::SEARCH_REVIEWED`, every row has an "
      f"entry, and **{n_owed + 1} of {len(declared)} are NOT cited to a "
      "reviewed measurement** — a count this file used to give as *\"except "
      "one, `p06`\"*, which was false on three (TASK_171 §3d) and is derived "
      "here rather than typed. The exceptions:")
    w("")
    w("- `p06` — marked `⊘` because `.memory/01-ladder.md` marks it `⊘`: it "
      "landed at TASK_048 and has not been through a second review. Labelled "
      "rather than omitted or silently promoted.")
    only_mentions = sorted(set(owed_mentions) - set(owed_primary))
    w(f"- **{', '.join('`%s`' % p for p in owed_primary)}** — the cited "
      "artefact is `RECAP`'s ***Owed*** queue, i.e. **the open backlog**: "
      "outstanding work, not a reviewed measurement, and each entry's own "
      "verdict says so — "
      + "; ".join(f"`{p}` *\"{SEARCH_REVIEWED[p][0]}\"*" for p in owed_primary)
      + ". `synthesize.py::backlog_cited` derives this from the citation "
      f"itself. ⚠ **The boundary is printed too**: {len(owed_mentions)} "
      f"entries *mention* the queue ("
      + ", ".join('`%s`' % p for p in owed_mentions)
      + f") and {len(owed_primary)} cite it and nothing else; "
      + ", ".join('`%s`' % p for p in only_mentions)
      + (" cites" if len(only_mentions) == 1 else " cite")
      + " a `NOTES.md` and a review as well, which is a different state.")
    w("")
    w("A pattern with no entry prints `undeclared`, which is its true state — "
      f"**{n_undecl} of {len(meas)}** today"
      + (f" ({', '.join(undecl)}):" if undecl else "."))
    w("")
    if n_undecl == 0:
        w("⚠⚠⚠ **AND THE HONEST SENTENCE IS NOT *\"EVERY RUNG'S CHEAPEST "
          "SPELLING HAS BEEN SEARCHED\"*. IT IS THIS: every one of the "
          f"{len(meas)} rows now DECLARES its search state, and "
          f"{n_found} of them declare a search that was reviewed.** "
          f"TASK_170 read all {len(UNDECLARED_AT_26)} rows that had printed "
          "`undeclared` since 26 patterns — "
          + " ".join(f"`{p}`" for p in UNDECLARED_AT_26)
          + " — against their own `NOTES.md`, "
          "`.memory/01-ladder.md`, `controls/` and reviewing report, and "
          f"**all {len(UNDECLARED_AT_26)} had a reviewed search**: none was a "
          "reviewed declaration of NO search, and none was genuinely "
          "undeclared. "
          "⚠⚠ **So `undeclared` was 100% bookkeeping at 26 patterns, 100% "
          "bookkeeping at 33, and never once measured search effort — the "
          "same conclusion TASK_112 and TASK_166 reached on smaller "
          "samples, now at the whole tree.** ⚠ **What is still NOT claimed, "
          "and what this column has never been able to say: that the search "
          "was DEEP ENOUGH.**")
        w("")
        # ⚠ TASK_172 item C. This used to read *"Seven of the fourteen"* and
        # then list SIX, omitting `p18` and `p38` -- a hardcoded count inside a
        # generated file, one paragraph below the same defect's own fix, and it
        # undercounted in the flattering direction (TASK_171 §3c). The count is
        # now `len()` of the list that is printed, and each membership is
        # anchored to a VERBATIM quote from the row's own entry.
        wk = weaker_endpoint_rows()
        w(f"**{len(wk)} of the {len(UNDECLARED_AT_26)} name an endpoint of "
          "their OWN that is unsearched, fiat, or resting on a measurement "
          "nobody reviewed** — in their own words, and the count below is "
          "`len()` of this list rather than a word typed above it "
          "(`synthesize.py::WEAKER_ENDPOINT`, which fails closed if a quote "
          "drifts out of its entry):")
        w("")
        for pat, q in wk:
            w(f"- **{pat}** — *\"{q}\"*")
        w("")
        w("⚠⚠ **Read a declared row as *somebody looked and wrote down what "
          "they found*, never as *this is the floor*: on p05 three "
          "successive published minima were each overturned by the next "
          "agent's FIRST lever, and on p42 the fifth R4 spelling reversed "
          "the sign of the published difference.**")
        w("")
    w(f"⚠⚠ **AND THE {len(declared)} DECLARED ROWS SPLIT THREE WAYS — NOT "
      f"TWO, WHICH IS WHAT THIS SENTENCE USED TO SAY — AND "
      f"ONE COUNT CANNOT SAY IT: {n_found} report a SEARCH "
      f"RESULT, {n_none} report a REVIEWED DECLARATION OF *NO* SEARCH "
      f"({', '.join(sorted(SEARCH_NONE & declared))}, marked `⊘` "
      f"in their entry text and listed in `SEARCH_NONE`), and {n_owed} report "
      f"a SEARCH THAT IS STILL OWED "
      f"({', '.join(sorted(set(owed_primary) & declared))}, whose cited "
      f"artefact is the open backlog).** ⚠⚠ **The third bucket is new here "
      f"and it is a correction, not a refinement**: `n_found` used to be a "
      f"RESIDUAL — declared minus `SEARCH_NONE` — so a row that says its span "
      f"is OWED landed in *report a SEARCH RESULT* by arithmetic "
      f"(TASK_171 §3d). It is now a set difference and all three buckets are "
      f"printed. A row that publishes no rung-to-rung figure and says so is "
      f"not in the same state as a row nobody has looked at, nor as a row "
      f"that owes one, and `undeclared` collapses all three. "
      f"⚠ **So do not read `{n_undecl} of {len(meas)}` as *the unsearched "
      f"fraction*** — it is *the fraction with no entry in this dict*, which "
      f"is what it has always been.")
    w("")
    for pat in sorted(SEARCH_REVIEWED):
        w(f"- **{pat}** — {SEARCH_REVIEWED[pat][0]}  \n  "
          f"*{SEARCH_REVIEWED[pat][1]}*")
    w("")
    w("⚠⚠⚠ **THE SAME DEFECT TASK_112 FIXED RECURRED ON THE SEVEN ROWS ADDED "
      "AFTER IT, AND NOTHING FIRED — because a missing entry is "
      "indistinguishable from a true `undeclared`.** Before TASK_166 this "
      "column printed **21 of 33** undeclared against a published **14 of "
      "26**, and ⚠ **the entire growth was the seven new rows**: the 14 rows "
      "undeclared at 26 are still exactly the 14 undeclared among those 26 "
      "today, so `14 → 21` was **100% bookkeeping and 0% a change in search "
      "state**. Of the seven, **four had a REVIEWED SEARCH and no entry** "
      "(`p25 p28 p34 p35` — `p34`'s own `controls/spellings.py` caught a "
      "flattering-direction headline before any review saw it, and `p35`'s "
      "search REVERSED the sign of its published `R3 − R4`) and **three had a "
      "REVIEWED DECLARATION OF NO SEARCH** (`p29 p32 p49`). ✅ **This defect "
      "runs AGAINST the usual flattering direction — it UNDER-reports the "
      "project's own search effort.** ⚠⚠ **And the obvious detector does not "
      "work: `p49` ships `controls/spellings.py` and it is NOT a rung-spelling "
      "search** — it is the `cow`-vs-`provenance` repair-site control on "
      "`c/kernel.c` — so *\"a pattern shipping `controls/spellings.py` with no "
      "entry here\"* would have produced a WRONG entry for `p49`. A check that "
      "could tell a missing entry from a true `undeclared` has to read the "
      "pattern's `NOTES.md`, not its file list.")
    w("")
    w("⚠⚠ **FOUR ENTRIES WERE ADDED AT TASK_112 AND THE COLUMN UNDERSTATED THE "
      "RECORD BY THAT MUCH** (TASK_111, adjacent work 1, which named three of "
      "the four; `p12` was found while landing it). `p22`, `p17`, `p06` and "
      "`p12` each have a **reviewed** search result in "
      "`.memory/01-ladder.md`, and each printed `undeclared` here. ⚠ **The "
      "consequence was not cosmetic**: `results/SYNTHESIS.md` §2 was quoting "
      "p22's `+2.00` and p12's `-26.00` inside a bucket labelled *\"flat in "
      "the size of the data\"* while RECAP finding 33 and "
      "`.memory/01-ladder.md` finding 22 carried the 510× correction for one "
      "of them (⚠ it is recorded there and in RECAP's standing trap box, "
      "**not** on the *\"Retracted -- do not reinstate\"* list, where p17's "
      "`+32 flat` does sit). **An `undeclared` in this "
      "column means *nobody wrote an entry*, and it has never meant *nobody "
      "searched*.**")
    w("")
    w("⚠ **Three corrections to this section's own provenance, and the "
      "paragraph that carried them predicted exactly this rot** "
      "(TASK_075_REVIEW M6, two of whose three items do not survive "
      "re-checking):")
    w("")
    w("1. **`8 of 22` was wrong and is gone.** RECAP records *\"8 of **20** "
      "patterns have a `--list`\"*, from when the tree had 20 patterns; the "
      "synthesis re-based the denominator to 22 and did not recount the "
      "numerator. Measured: `grep -l -- '--list' patterns/*/controls/*.py` is "
      "**11 files across 10 patterns** (p03 p04 p06 p09 p10 p12 p22 p36 p38 "
      "p47). The table above now derives it instead of quoting it.")
    w("2. **The `RECAP \"Owed\" 12` citation was RIGHT and the review's "
      "correction to it is wrong.** RECAP item 12 spans `RECAP.md:1808-1863` "
      "(item 13 opens at `:1864`) and the `--list` census at `:1847-1852` is "
      "inside it. RECAP \"Owed\" **6** is the `source_sha256` item, whose tail "
      "is the p11 `bulk_calls` sentence — which is a *different* citation this "
      "file also makes, correctly. The two were swapped.")
    w("3. **`p47`'s \"six levers\" checks out, and its citation did not.** "
      "The figure was cited to `.tasks/TASK_075.md`, unreviewed manager prose, "
      "and that was the defect. The number is supported by "
      "`patterns/p47-ct-compare/NOTES.md` §8e — *\"Six R4 levers were "
      "built\"*, a six-row table — and `gen_controls.py --list` registers five "
      "`from unsafe.rs`, the sixth being the shipped rung. TASK_075_REVIEW "
      "M6.3 counted the four non-baseline rows and called the figure "
      "unsupported.")
    w("")

    txt = "\n".join(L) + "\n"
    if a.stdout:
        sys.stdout.write(txt)
    else:
        open(a.out, "w").write(txt)
        print(f"wrote {os.path.relpath(a.out, REPO)}  ({len(txt)} bytes, "
              f"{len(L)} lines)")
    # ⚠ TASK_170: this file used to exit 0 whatever happened, so a broken
    # must-fire arm would have been a sentence in the artefact and nothing
    # else. `PROTOCOL`'s closing rule -- CHECK EACH SCRIPT'S OWN EXIT STATUS --
    # needs the script to HAVE one.
    bad = [lab for lab, got, want in PIN_STATUS_CASES if got != want]
    for lab, got, want in PIN_STATUS_CASES:
        if got != want:
            print(f"  ARM FAIL  {lab}\n            got  {got!r}\n"
                  f"            want {want!r}")
    print(f"outward-pin must-fire arms: "
          f"{len(PIN_STATUS_CASES) - len(bad)}/{len(PIN_STATUS_CASES)} pass")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main() or 0)
