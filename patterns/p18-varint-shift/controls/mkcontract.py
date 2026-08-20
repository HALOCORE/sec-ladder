#!/usr/bin/env python3
"""Splice p18's `slb-contract` block into `../spec.md`.

Two jobs, both of which a hand-written block gets wrong:

  1. the **shared paragraph** of `idiom.why` -- the named-spelling standard,
     from `NAMED-SPELLING STANDARD` to the end -- must be **byte-identical in
     every pattern**, and `.memory/05-layout.md` says to diff them. Copying it by
     hand into a fifteenth pattern is how a copy drifts, so this script reads it
     out of `patterns/p14-field-split/spec.md` and asserts it is byte-identical
     in the thirteen patterns that already agree;
  2. the block is JSON inside markdown, so a hand edit can produce a file the
     gate cannot parse at all.

    python3 patterns/p18-varint-shift/controls/mkcontract.py          # write
    python3 patterns/p18-varint-shift/controls/mkcontract.py --check  # verify

`--check` re-derives the block and compares it against what is in `spec.md`, so
the committed file and this generator cannot drift apart silently. Run it after
any edit to the block.
"""

import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
SPEC = os.path.join(PDIR, "spec.md")
SHARED_FROM = os.path.join(REPO, "patterns", "p14-field-split", "spec.md")
MARK = "NAMED-SPELLING STANDARD"


def contract_of(path):
    t = open(path).read()
    m = re.search(r"```slb-contract\n(.*?)\n```", t, re.S)
    if not m:
        raise SystemExit(f"{path}: no slb-contract block")
    return json.loads(m.group(1))


def shared_why():
    """The named-spelling-standard paragraph, read from p14 and cross-checked
    against every other pattern that carries it."""
    w = contract_of(SHARED_FROM)["idiom"]["why"]
    i = w.find(MARK)
    if i < 0:
        raise SystemExit(f"{SHARED_FROM}: no {MARK!r} paragraph")
    tail = w[i:]
    agree, differ = [], []
    for p in sorted(glob.glob(os.path.join(REPO, "patterns", "p*", "spec.md"))):
        if os.path.abspath(p) == os.path.abspath(SPEC):
            continue
        try:
            o = contract_of(p)["idiom"]["why"]
        except Exception:
            continue
        j = o.find(MARK)
        (agree if j >= 0 and o[j:] == tail else differ).append(
            os.path.basename(os.path.dirname(p)))
    print(f"  shared paragraph: {len(tail)} chars, byte-identical in "
          f"{len(agree)} pattern(s); differing/absent in {differ}")
    return tail


# ---------------------------------------------------------------------------
# p18's own half of `why`. Everything above the shared paragraph.
WHY_P18 = """each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (../spec.md's second sentence). THE ONLY THING R1 OMITS IS THE SHIFT BOUND: the scan bound `p < len` is present in every rung, so every read of `buf` is in bounds in every rung and p18 has NO out-of-bounds access to model on any input; the outer cursor guard `p == len` is present in every rung, so a dishonest `nv` cannot spin; `val`, `shift` and `nb` are reset at the top of every varint in every rung. R1-vs-R1h is therefore the cost of `if (shift < VBITS)` and nothing else. THE BOUND IS A SHIFT COUNT AND THAT IS WHY THIS PATTERN EXISTS: every earlier bound in this project is SPATIAL -- p02's, p16's and p17's compare a declared length against a buffer extent, p11's and p13's are about a terminator, p14's is a count of a byte value against a table's extent, p09's is a bit index against a word count -- and all of them decide whether an ADDRESS is inside an ALLOCATION. p18's decides whether an ARITHMETIC OPERATION IS DEFINED AT ALL. `shift` is `7 * nb` and `nb` is decided by the attacker's continue bits, not by any declared length: the canonical encoding of a `uint64_t` is at most TEN bytes and its last shift is exactly 63, in range, and the ELEVENTH byte is the first one that is not. So the guard cannot be hoisted out of the scan, folded into a length check or derived from the header, and it runs ONCE PER INPUT BYTE rather than once per call or once per record -- which is why p18's hardening cost does not amortise as the input grows and every earlier pattern's does. THE BUG TOUCHES NO MEMORY, AND THE CONSEQUENCE FOR THE TOOLKIT IS THE RESULT: ASan is silent on every rung and every input of p18, rustc's bounds checks are silent, and a memory-safety-only specification is VACUOUSLY TRUE OF R1. What catches it is UBSan on the C side (`-fsanitize=undefined` implies `-fsanitize=shift`, measured at harness/check.py's own flags), `-C debug-assertions=on` and Miri on the Rust side, and Verus (`possible bit shift underflow/overflow`). All four are outside the 24-cell matrix; ../NOTES.md 0.2 and 7 have the measurements. THE CHECKSUM IS NOT AN ORACLE FOR THIS BUG CLASS, AND THAT IS A PROPERTY OF THE BUG RATHER THAN OF THE FOLD: `|=` is idempotent, so a payload wrapped round into a bit that is ALREADY SET changes nothing, and `adversarial-sat.bin` is a twenty-byte varint of `0x7f` payloads on which ten undefined shifts execute, UBSan fires, and R1 and R1h return the SAME value. No choice of fold could repair that, which is why the fold entries below are justified by what they DO catch and not by a claim to catch everything. TRUNCATION AT VBITS IS THE SPECIFIED ANSWER, not an evasion, and it is ALSO THE SECOND BUG: once `shift` reaches VBITS the hardened rung keeps consuming the varint's bytes -- so `nb` and the cursor are unchanged -- and stops accumulating, which is what the Linux kernel's uleb128 reader and most hand-written protobuf readers do, and it is p13's shape one level up (the hardened cell is memory-safe, well-defined, and LOSES DATA). Rejecting instead was built and rejected in ../NOTES.md 0b for a measured reason: it needs a second live variable and a second test, so R1-vs-R1h would stop being a one-line difference. And a TEN-byte varint whose last payload is `0x7f` ends at shift 63 -- in range, no undefined behaviour, guard never fires -- and six bits of the encoded integer are discarded by the shift itself; `truncating.bin` is that input, every rung agrees on it, ASan, UBSan, `debug-assertions=on` and Miri are all clean and R5's proof discharges, because `varint_fold` specifies what the PROGRAM does. That is p17's limit arriving on arithmetic instead of on a range and it is stated in the `ensures` section of ../spec.md rather than left to be discovered. THE CURSOR GUARDS ARE DIRECT COMPARISONS AND NOT SUBTRACTION-FIRST, and the absence of a pin that p07, p14 and three other patterns carry is deliberate rather than an oversight: their cursors advance by a DECLARED length, so the additive form `p + 4 > len` can overflow `usize` and Verus rejects it. p18's cursor advances by ONE, so `p < len` and `p == len` involve no arithmetic at all, there is nothing to overflow, and the kernel's `requires` stays at ONE clause without needing the idiom. `wrapping_shl`, `checked_shl`, `overflowing_shl` and `unchecked_shl` are forbidden because each REPLACES the safety line with a library call and each does so in a different and separately interesting way, so a rung using one would be measuring a different question: `wrapping_shl` makes the oversized shift DEFINED with exactly x86's masking semantics, i.e. it writes R1's realised behaviour on purpose and would be silent under debug-assertions, under Miri and under Verus while still returning the wrong number; `checked_shl` IS the guard, in library form, so a rung using it would price `Option` codegen rather than the branch this pattern is about; `unchecked_shl` is the Rust spelling of C's undefined behaviour and would put the UB inside an `unsafe` block, which is a DIFFERENT experiment (it would make R4 and R1 commit the same UB and make the safe rungs incomparable to both). All four are built and priced in controls/gen_controls.py and ../NOTES.md 9, and their prover disposition is MEASURED there rather than asserted. `from_le_bytes` deletes the written-out little-endian header decode every rung shares AND is NOT AVAILABLE TO AN R4 AT ALL at the pinned vstd (`from_le_bytes` and the `try_into`/`TryFromSliceError` route to it are both `is not supported`, measured on p05 and p16 at TASK_027_REVIEW and again on p06 and p14), so a rung using it would compare a safe cell against an unsafe cell that cannot exist. `chunks_exact` is forbidden because p16 measured that the chunk width moves that pattern's per-byte rate over a 31% range (5.04688...6.62500, `.memory/01-ladder.md`), and p18's published decomposition is into a per-varint-byte and a per-varint term. `take_while` and `.position(` are forbidden because each turns the scan into a LIBRARY iterator whose exit condition is the continue bit: `position` in particular computes the varint's LENGTH in one pass and would then decode in a second, which is a different program with a different cost model, and this pattern's whole per-byte law is a statement about a single-pass explicit cursor. EVERY EXCLUSION HERE IS WHOLE-PATTERN AND NOT SCOPED TO SOME RUNGS, which is deliberate: `.memory/01-ladder.md`'s direction test fired on p13 exactly because three of its entries named some rungs and exempted `safe_tuned.rs`, so R3 was permitted a spelling R4 was forbidden and 48%/17% of the published margin was the pin. A whole-pattern exclusion keeps the two sides of the comparison equal. NOTHING IN `required` IS SCOPED TO A SUBSET OF RUNGS ON p18, which is a difference from p06 and p14 worth naming: both of those scope their bulk load's RECEIVER 2-and-2 because `RangeTo` has no `SliceIndexSpecImpl` at the pinned vstd, and p18 has no bulk load and no receiver -- its kernel performs exactly one kind of memory access, a byte read of the input window, so there is nothing to scope. WHAT IS AND IS NOT PINNED ABOUT THE SCAN LOOP, STATED PRECISELY BECAUSE AN EARLIER DRAFT OF ../spec.md's PROSE GOT IT WRONG AND THE BLOCK IS WHAT DECIDES: the scan's BOUND is pinned -- `while p < len` in all four Rust rungs and `while (p < len)` in both C rungs, entry `required[2]` -- because that bound is the whole of what keeps p18 out of p11's territory, and a rung whose scan is bounded by the continue bit instead is a DIFFERENT PATTERN with a different harm (../NOTES.md 0b builds it and rejects it). So an iterator-driven scan such as `w[p..].iter()` is OUT of contract on every rung including R3, and ../NOTES.md 8d prices it as such rather than pretending it is admissible. What the declaration DOES leave free on R3 is the WINDOW RESLICE -- named nowhere here, so the two-step `split_at` form that ships, the one-step `&buf[off..off + len]` form and no reslice at all are all admissible -- and the STATEMENT STRUCTURE OF THE FOLD, since only its operations are pinned; those are p18's two in-contract R3 spellings besides the shipped one and ../NOTES.md 8d publishes all three with the input named. What IS pinned instead of the loop form is the OPERATIONS and the BOUND -- the payload mask, the continue test, the wrapping shift step, the guard, the scan bound and the cursor guard. THE FOLD IS OVER THE FULL RECORDED EXTENT AND ORDER-SENSITIVE, AND p18 SUPPLIES NO FOURTH INDEPENDENT REASON FOR THAT RULE -- saying so is more useful than inventing one. TASK_004_REVIEW's reason is ELISION: a fold that reads only part of the result lets the optimiser delete the rest. p06's is INVARIANCE: three reverses compose to a permutation, so a sum- or xor-fold could not tell the buggy scratch from the correct one. p14's is PARTITION-BLINDNESS: tokenising moves no byte, so a fold over the concatenated content is identical for every possible set of field boundaries. p18's bug corrupts the DECODED VALUE, which the fold reads directly, so elision alone justifies the rule here. What p18 adds is the COUNTER-observation above -- that on `adversarial-sat.bin` no fold whatsoever can see the bug. The two folded quantities each catch a different mutation and ../NOTES.md 2 tabulates them: the VALUE catches a rung that shifted by the wrong amount or masked the wrong bits, and the BYTE COUNT catches a rung that consumed a different number of bytes -- a ten-byte cap instead of a shift guard, or a scan that stopped on the wrong bit. `nv` is folded once at the end so a rung that decoded a different number of varints cannot produce the same checksum either. THE SHIFT STEP IS WRAPPING IN ALL SEVEN RUNGS AND THAT IS NOT STYLISTIC: `shift += 7` on C's `unsigned` wraps by 6.2.5p9 and Rust spells it `shift.wrapping_add(7)`, and the effect is that the SHIFT ITSELF and the two cursor increments are the ONLY arithmetic in this kernel that a Rust `-C debug-assertions=on` build can fire on. p18 is the first pattern in this project to measure the `O0d` axis at all, and that axis is only attributable because of this entry. ../NOTES.md 5 decomposes the O0d-minus-O0 delta mnemonic by mnemonic and reports what fraction of it is the shift check rather than the increments. WHEN THIS DECLARATION WAS WRITTEN, STATED EXACTLY BECAUSE p18 HAS A PRE-FLIGHT: it was written after the seven rungs, the R5 proof (12/0 on the second attempt, twin 13/0) and the checksums existed and BEFORE any p18 CELL had been measured for perf -- `harness/measure.py p18` had not been run and no `Ir` or `ns` figure for any of the eight cells existed. What DID exist is ../NOTES.md 0: `Ir`, sanitizer behaviour and checksums for a standalone SIX-KERNEL C PROBE with no driver and no pattern, which settled the bug class TASK_051 asked to be settled before five rungs were built on it, plus the three-premise `O0d` probe of ../NOTES.md 0.1. Neither is a cell and no number from either is published as p18's, but they are not nothing either, and saying 'no number existed' would be false. What the probe DID influence is the CHOICE OF BUG CLASS, the choice of TRUNCATION over rejection as the hardened answer, and the wire format that expresses both; what it did not influence is any entry of `required` or `forbidden`, every one of which names a line the contract in ../spec.md's Semantics block already had. NO ENTRY OF `required` OR `forbidden` WAS ADDED IN RESPONSE TO A MEASUREMENT ON p18, and that is stated as a fact about this pattern rather than as a general claim: p14 had to disclose one (`flen = i - s;`, added after an `identity` failure) and p18 had no such repair -- its `-O0` identity came out `norel` and its `-O3` identity `exact` on the first build of the pair, before any entry of this declaration was edited. ONE EDIT TO THIS `why` KEY WAS HOWEVER MADE AFTER THE CONTROLS WERE BUILT, AND IT IS NAMED HERE RATHER THAN LEFT TO BE INFERRED: the paragraph above about the scan loop originally read `WHAT IS DELIBERATELY NOT PINNED is the SPELLING OF THE SCAN LOOP: ... and the second in-contract R3 spelling drives it from w[p..].iter()`, which CONTRADICTED this block's own `required[2]` (`while p < len`). Building `t_iter` is what surfaced the contradiction. NO ENTRY of `required` or `forbidden` moved -- `required[2]` is exactly what it was, and `t_iter` is out of contract now as it was then; what changed is that the prose now says so. The corresponding sentence in ../spec.md's prose and in safe_tuned.rs's header was wrong the same way and was corrected in the same commit (../NOTES.md 12). """


CONTRACT = {
    "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
    "model": "model.py",
    "requires": ["off + len <= buf_len"],
    "ensures": ["result == varint_fold(buf, off, len)"],
    "note": (
        "requires/ensures above are DERIVED by check.py from verus.rs's own "
        "clause text through verus.translate, and the copy here must equal the "
        "derivation exactly. They are evaluated in Python against the bindings "
        "model.py yields per call (buf/off/len/buf_len/result) plus the helper "
        "it supplies (varint_fold). p18's bindings are the READ-ONLY set p03, "
        "p06, p11, p12, p14, p16, p17, p05 and p07 use and NOT p02's "
        "before/after set, and the reason is stronger here than on any of them: "
        "p18's kernel WRITES NOTHING ANYWHERE. It has no scratch, no output "
        "buffer and no table -- `val`, `shift`, `nb`, `p` and `acc` are "
        "scalars -- so there is no buffer for an `after` binding to name and no "
        "store of any kind to exclude. **THE SECURITY PROPERTY IS THEREFORE NOT "
        "CARRIED BY A TRUSTED ACCESSOR'S `requires` AT ALL**, which is a first "
        "for this project and is the thing to read this pin for. "
        "`buf_get_unchecked`'s `i < v@.len()` excludes an out-of-bounds READ; "
        "R1's defect is an out-of-range SHIFT, and the two are about different "
        "facts. Weakening or deleting that `requires` neither admits nor "
        "excludes R1's bug (measured, ../NOTES.md 10), and a memory-safety-only "
        "specification of this kernel is VACUOUSLY TRUE OF R1. What rejects the "
        "deletion of the safety line is Verus's own arithmetic obligation on "
        "`<<`, `possible bit shift underflow/overflow`, raised on the operator "
        "with no accessor and no `ensures` involved. **The `ensures` is the "
        "FUNCTIONAL one and on p18 that is not a preference but the only option "
        "that says anything**: it states that the accumulator is the fold of "
        "the values the window's varints decode to and of the bytes each "
        "consumed, through `vdec`, `vbytes` and `vwalk`. **What the `ensures` "
        "deliberately does NOT say** is that `nv` is honest, that a varint "
        "terminates inside the window, or -- and this is the honest limit -- "
        "that the decoded value is the integer the ENCODER wrote. "
        "`varint_fold` specifies the TRUNCATING decode because that is what the "
        "program does, so adversarial-shift11.bin, adversarial-shift20.bin, "
        "adversarial-many.bin, adversarial-sat.bin, truncating.bin and "
        "degenerate.bin are all INSIDE the verified domain, every checked rung "
        "agrees with model.py on all six, and the proof is SILENT on "
        "truncating.bin's wrong answer. A `requires` that a varint fitted in "
        "sixty-four bits would be a precondition about the contents of a file "
        "that no honest loader can discharge (`.memory/02-bench-rules.md`), and "
        "it would delete every row the pattern exists for."),
    "idiom": {
        "required": [
            {
                "c": "THE SAFETY LINE, and the only line c/kernel.c omits: `if (shift < VBITS)` in c/kernel_hardened.c. c/kernel.c omits exactly this and nothing else.",
                "rust": "THE SAFETY LINE: `if shift < VBITS {` in all four Rust rungs. In Rust at the flags this benchmark measures (-C debug-assertions=off, all 24 cells) it is NOT a safety line -- deleting it produces no panic and no bounds-check failure, only the same silently wrong integer C produces, because `<<` MASKS the count. It becomes a safety line only under -C debug-assertions=on, under Miri and under Verus. ../NOTES.md 7."
            },
            {
                "c": "the shift is applied with `<<` and combined with `|`, spelled out rather than through a library helper, so that the operator carrying the undefined behaviour is visible in the source of the rung that commits it: `val |= (uint64_t)(c & 0x7f) << shift;` in both C rungs.",
                "rust": "the shift is applied with `<<` and combined with `|`, spelled out rather than through the wrapping_shl / checked_shl / unchecked_shl family, all of which are forbidden and priced: `val = val | (((c & 0x7f) as u64) << shift);` in all four Rust rungs."
            },
            {
                "c": "THE SCAN IS BOUNDED BY THE WINDOW IN EVERY RUNG, R1 included -- p18 is NOT p11 and NOT p16, and this entry is what says so by grep: `while (p < len)` in both C rungs.",
                "rust": "THE SCAN IS BOUNDED BY THE WINDOW IN EVERY RUNG, R1 included: `while p < len` in all four Rust rungs. The opening brace is deliberately NOT part of the quoted spelling: verus.rs puts its invariant block between the loop condition and the brace, so a pin that included the brace would put R5 out of its own pattern's declaration.."
            },
            {
                "c": "...and the OUTER CURSOR GUARD, present in every rung, so a dishonest `nv` cannot spin over an exhausted window: `if (p == len)` in both C rungs.",
                "rust": "...and the OUTER CURSOR GUARD, present in every rung, so a dishonest `nv` cannot spin over an exhausted window: `if p == len {` in all four Rust rungs."
            },
            "the payload is the low SEVEN bits, so no rung can be decoding a different wire format: `c & 0x7f` in all seven rungs.",
            {
                "c": "...and the CONTINUE BIT is bit 7, which is what decides a varint's length and therefore what decides the shift count: `if (!(c & 0x80))` in both C rungs.",
                "rust": "...and the CONTINUE BIT is bit 7, which is what decides a varint's length and therefore what decides the shift count: `if c & 0x80 == 0 {` in all four Rust rungs."
            },
            {
                "c": "THE SHIFT STEP IS WRAPPING in every rung, which is what leaves the shift itself and the two cursor increments as the only arithmetic a debug-assertions=on build can fire on: `shift += 7;` in both C rungs (unsigned, 6.2.5p9).",
                "rust": "THE SHIFT STEP IS WRAPPING in every rung, which is what leaves the shift itself and the two cursor increments as the only arithmetic a debug-assertions=on build can fire on: `shift = shift.wrapping_add(7);` in all four Rust rungs."
            },
            {
                "c": "`val`, `shift` and `nb` are RESET AT THE TOP OF EVERY VARINT in every rung, so no state crosses a varint boundary and none crosses a call boundary: `shift = 0;` in both C rungs.",
                "rust": "`val`, `shift` and `nb` are RESET AT THE TOP OF EVERY VARINT in every rung, so no state crosses a varint boundary and none crosses a call boundary: `let mut shift: u32 = 0;` in all four Rust rungs."
            },
            {
                "c": "the DECODED VALUE is folded, so a rung that shifted by the wrong amount or masked the wrong bits cannot produce the same checksum: `acc = acc * 31 + val;` in both C rungs.",
                "rust": "the DECODED VALUE is folded, so a rung that shifted by the wrong amount or masked the wrong bits cannot produce the same checksum: `.wrapping_add(val)` in all four Rust rungs."
            },
            {
                "c": "...and the BYTE COUNT is folded, in order, so a rung that consumed a different number of bytes -- a ten-byte cap instead of a shift guard, or a scan that stopped on the wrong bit -- cannot either: `acc = acc * 31 + (uint64_t)nb;` in both C rungs.",
                "rust": "...and the BYTE COUNT is folded, in order, so a rung that consumed a different number of bytes cannot either: `.wrapping_add(nb as u64)` in all four Rust rungs."
            },
            {
                "c": "the declared varint count is folded, so a rung that decoded a different number of varints cannot produce the same checksum either: `* 31 + (uint64_t)nv` in both C rungs.",
                "rust": "the declared varint count is folded, so a rung that decoded a different number of varints cannot produce the same checksum either: `.wrapping_add(nv as u64)` in all four Rust rungs."
            },
            "the little-endian u32 header decode is written out with + and * rather than | and <<, so it stays linear arithmetic and the ONLY `<<` in the kernel is the one the pattern is about: `+ 65536 *` in all seven rungs.",
            "...and its top byte: `+ 16777216 *` in all seven rungs."
        ],
        "forbidden": [
            "`wrapping_shl`",
            "`checked_shl`",
            "`overflowing_shl`",
            "`unchecked_shl`",
            "`from_le_bytes`",
            "`chunks_exact`",
            "`take_while`",
            "`.position(`"
        ],
        "why": WHY_P18 + "@@SHARED@@"
    },
    "verus": {
        "call_site": "main",
        "kernel_item": "kernel",
        "translate": {
            "buf@.len()": "buf_len",
            "buf@": "buf",
            " as int": "",
            "r": "result"
        },
        "obligations": {"verus.rs": 12},
        "twin_obligations": {"verus.rs": 13},
        "obligations_note": (
            "12 = VBITS 1 + vdec 1 + vbytes 1 + vwalk 1 + kernel 3 + main 5, "
            "each term measured with `./verus_run.py verus.rs "
            "--verify-function <name> --verify-root`, which is how they were "
            "obtained, and the zero terms are checkable the same way: u32_at, "
            "nv_at and varint_fold are NON-RECURSIVE spec fns and report 0, "
            "while vdec, vbytes and vwalk are RECURSIVE and carry one "
            "termination query each; buf_get_unchecked, load_input and emit are "
            "external_body and report 0. ONE `const` carries one query, VBITS "
            "-- `.memory/04-verus.md` records that a `const` inside verus! is "
            "its own obligation (measured on p08's SCR and p03's STACK_CAP), "
            "and p18 has the single-constant shape p03, p06 and p08 have "
            "rather than p14's three. kernel's 3 = body + TWO loop bodies (the "
            "varint walk and the byte scan), and there is no `by "
            "(nonlinear_arith)` and no `by (bit_vector)` anywhere in the kernel "
            "-- the spec is written with the SAME `&`/`|`/`<<` the exec code "
            "uses, which is what keeps the solver in the fragment it is good "
            "at, and the only multiplications are by literals. main's 5 is "
            "quoted AS MEASURED and does not decompose from the command line: "
            "body + driver loop + one per by-block would predict 6 and Verus "
            "reports 5, the identical off-by-one p03's, p05's, p06's, p07's, "
            "p11's, p12's, p14's and p17's spec.md record for the identical "
            "driver. `.memory/04-verus.md`'s one-query-per-function-plus-one-"
            "per-loop rule of thumb gives 9 here and is therefore not the "
            "derivation."),
        "twin_obligations_note": (
            "The obligation count in the OTHER configuration -- `verus.rs "
            "--cfg slb_twin`, which is where step 5c-twin checks the twins. 12 "
            "shipped + 1, and the term is measured the same way: `--cfg "
            "slb_twin --verify-function slb_twin_buf_get_unchecked "
            "--verify-root` reports `1 verified`. It is +1 rather than +3 "
            "because load_input and emit state NO `ensures` and contain NO "
            "`unsafe`, so they are outside the twin regime "
            "(`.memory/04-verus.md`: the regime is keyed on `external_body` + "
            "a non-empty `ensures` OR `unsafe`). **p18 has the smallest "
            "trusted base of any pattern in this project -- 3 items, 1 with a "
            "`requires` -- and for a structural reason rather than by "
            "cleverness**: its kernel performs exactly ONE kind of memory "
            "access, a byte read of the input window, so there is exactly one "
            "accessor to trust. There is no scratch, no output buffer, no bulk "
            "copy and no write of any kind. Pinning the number rather than "
            "requiring `tw > base` is what catches a twin that quietly lost "
            "its body, or an item that exists only under the cfg."),
        "unsafe_justifications": {},
        "items": {
            "verus.rs": {
                "u32_at": {"external": None, "requires": [], "ensures": []},
                "nv_at": {"external": None, "requires": [], "ensures": []},
                "vdec": {"external": None, "requires": [], "ensures": []},
                "vbytes": {"external": None, "requires": [], "ensures": []},
                "vwalk": {"external": None, "requires": [], "ensures": []},
                "varint_fold": {"external": None, "requires": [], "ensures": []},
                "buf_get_unchecked": {
                    "external": "verifier::external_body",
                    "requires": ["i < v@.len()"],
                    "ensures": ["r == v@[i as int]"]
                },
                "slb_twin_buf_get_unchecked": {
                    "external": None,
                    "requires": ["i < v@.len()"],
                    "ensures": ["r == v@[i as int]"]
                },
                "load_input": {
                    "external": "verifier::external_body",
                    "requires": [], "ensures": []
                },
                "emit": {
                    "external": "verifier::external_body",
                    "requires": [], "ensures": []
                },
                "kernel": {
                    "external": None,
                    "requires": ["off + len <= buf@.len()"],
                    "ensures": ["r == varint_fold(buf@, off as int, len as int)"]
                },
                "main": {"external": None, "requires": [], "ensures": []}
            }
        }
    },
    "driver": {
        "statements": 12,
        "c_source": "c/main.c",
        "regions": ["safe_naive.rs", "safe_tuned.rs", "unsafe.rs", "verus.rs",
                    "c/main.c"],
        "aliases": {
            "c": {
                "n_body": "bytes.len()",
                "bytes": "bytes.as_slice()",
                "inp.n_iters": "n_iters"
            }
        },
        "call_args": {"c": {"kernel": [0, 2, 3]}},
        "canonical": [
            "n_blob = bytes . len ( ) ;",
            "buf = bytes . as_slice ( ) ;",
            "acc = 0 ;",
            "if stride_w >= 4 && stride_w <= n_blob",
            "{",
            "stride = stride_w ;",
            "nwin = n_blob / stride ;",
            "it = 0 ;",
            "while it < n_iters",
            "{",
            "k = acc * nwin >> 64 ;",
            "r = kernel ( buf , k * stride , stride ) ;",
            "acc = acc * 31 + r ;",
            "it = it + 1 ;",
            "}",
            "}"
        ]
    },
    "collapse": {
        "probe_inputs": ["small.bin", "large.bin"],
        "probe_iters": [100, 200],
        "note": (
            "work_per_call is **bytes of the window** -- `stride`, 116 on small "
            "and 45 on large -- which is p16's, p05's, p11's, p12's, p14's and "
            "p06's denomination. WHICH WAY THE ESTIMATE ERRS: HIGH, BY EXACTLY "
            "FOUR BYTES, and it is stated in the direction it really goes "
            "rather than in the comfortable one. The 4 window-header bytes are "
            "decoded as a u32 and are never scanned; every other window byte is "
            "visited EXACTLY ONCE, because `nv` is honest on small, large, "
            "truncating and every sweep blob, so the cursor reaches `len`. "
            "There is no second pass and no third: p18's kernel does not copy "
            "and does not re-read, so unlike p14 there is no under-count to set "
            "against the over-count. The derived floor is therefore 1.00 Ir/call "
            "too high out of 29.00 on small and 11.25 on large -- against a "
            "kernel that executes about eleven instructions per scanned byte, "
            "so it is cleared by roughly 40x either way (../NOTES.md 3). A "
            "floor that errs HIGH can produce a false FAILURE and never a false "
            "pass, which is the safe direction for this check, and the margin "
            "above says by how much. work_unit_bits is 8, one window byte, so "
            "the effective absolute bound under min_ir_per_work is 0.001953125 "
            "x 8 = 0.015625. model.py declares NO min_ir_per_work, so the "
            "harness default of 0.25 Ir per byte applies unchanged, and the "
            "argument is p18-specific and stronger than any earlier pattern's: "
            "**a varint's length is not known until its last byte has been "
            "read**, so the scan is not merely un-vectorised, it is "
            "unvectorisABLE at any -march -- the loop-carried dependence is the "
            "continue bit of the byte just loaded -- and the fold on top of it "
            "is a serial Horner chain `acc = acc*31 + x`. No compiler emitted a "
            "vector instruction in any of the eight cells (measured on the "
            "disassembly, ../NOTES.md 1). The two probe inputs differ in "
            "work_per_call (116 vs 45) precisely so check.py's d(Ir)/d(work) "
            "assertion has two shapes and can run at all.")
    },
    "identity": [
        {
            "a": "unsafe",
            "b": "verus",
            "O0": "norel",
            "O3": "exact",
            "why": (
                "R4 == R5: the proof licenses unsafe code at zero cost, on the "
                "first kernel in this project whose load-bearing obligation is "
                "ARITHMETIC rather than spatial. The byte-identity result now "
                "covers a kernel whose postcondition is a recursive fold "
                "written with `&`, `|` and `<<` -- the operators this project "
                "has kept out of its specs on eleven previous patterns -- and "
                "it holds with no `by (bit_vector)` anywhere in the file. **The "
                "pin has NO measured price on p18**, which is worth recording "
                "because p06's and p14's did: both had to bind a value to a "
                "local before a store, because R5's store is a CALL and R4's is "
                "an assignment. p18 has no store at all, so the argument "
                "evaluation order that broke their -O0 identity has nothing to "
                "act on here, and `norel`/`exact` came out on the FIRST build "
                "of the pair with no edit to any rung. At O0 the crate names "
                "differ in length so call displacements differ -- link layout, "
                "not codegen.")
        }
    ],
    "miri": {
        "pair": ["unsafe", "verus"],
        "sources": ["unsafe.rs"],
        "required": True,
        "reason": (
            "R4 and R5 ARE byte-identical at O3. Since TASK_010 "
            "`.memory/02-bench-rules.md` makes Miri mandatory for any pattern "
            "with a trusted item, which check.py DERIVES from verus.rs rather "
            "than reading from this flag -- because R4 inherits R5's proof and "
            "R5's proof is only as good as its trusted `ensures`, which need "
            "not be complete with respect to the operations the trusted body "
            "performs. **On p18 there is a second reason, specific to this "
            "pattern and to nothing else in the project: Miri runs with "
            "`debug-assertions` ON.** So the Miri row is simultaneously the "
            "only place inside the gate where an oversized shift in a RUST rung "
            "would be caught -- it panics with `attempt to shift left with "
            "overflow` rather than reporting `Undefined Behavior`, so "
            "check.py's `ub` flag stays false and the row fails on the exit "
            "code instead (measured, ../NOTES.md 0.2). It is silent on every "
            "p18 input precisely because all four Rust rungs carry the safety "
            "line, and ../NOTES.md 7 shows what it does when they do not. Cost: "
            "check.py rewrites n_iters to 4, so each row scans at most 4 x "
            "stride bytes -- 464 on small and 180 on large, five orders of "
            "magnitude inside `.memory`'s measured 3.05 M budget. The only real "
            "cost is the 5.2 MB payload to_vec, and p07's 12 MB one passes."),
        "blocked_reason": (
            "miri is installed on the nightly toolchain beside the pinned one "
            "(TOOLCHAIN.md). If it is missing, this row is blocked rather than "
            "failed.")
    }
}


def build():
    tail = shared_why()
    c = json.loads(json.dumps(CONTRACT))          # deep copy
    c["idiom"]["why"] = c["idiom"]["why"].replace("@@SHARED@@", tail)
    return json.dumps(c, indent=2, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="verify spec.md matches this generator, do not write")
    a = ap.parse_args()
    want = build()
    text = open(SPEC).read()
    m = re.search(r"```slb-contract\n(.*?)\n```", text, re.S)
    if a.check:
        if m is None:
            print("spec.md has no slb-contract block", file=sys.stderr)
            return 1
        if m.group(1) != want:
            print("spec.md's slb-contract block DIFFERS from this generator",
                  file=sys.stderr)
            return 1
        print("  spec.md matches the generator")
        return 0
    if m is not None:
        text = text[:m.start(1)] + want + text[m.end(1):]
    else:
        text = text.replace("@@CONTRACT@@", want)
    open(SPEC, "w").write(text)
    print(f"  wrote {len(want)} chars into {os.path.relpath(SPEC, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
