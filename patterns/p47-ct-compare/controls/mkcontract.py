#!/usr/bin/env python3
"""Splice p47's `slb-contract` block into ../spec.md.

⚠ **THE SHARED NAMED-SPELLING PARAGRAPH IS READ FROM A DONOR `spec.md` AND IS
NOT IN THIS FILE.** `patterns/p27-handle-table/controls/mkspec.py` embedded its
own copy, and re-running it silently deleted the paragraph from p27's contract;
only `harness/check.py`'s new `named_spelling_problem` stage caught that
(`.memory/05-layout.md`, TASK_062). So this generator:

  * reads the donor's `idiom.why`, cuts the span between
    `NAMED-SPELLING STANDARD` and `p01 and p08 neither` inclusive, and appends
    it to p47's own pattern-specific `why` prose;
  * **verifies the cut against `harness/check.py`'s own pin** before writing,
    by importing `named_spelling_problem` rather than re-implementing it;
  * refuses to write anything if the donor is missing, if the paragraph is not
    found, or if the resulting `why` does not satisfy that check.

There is no code path in this file that can produce a `spec.md` without the
paragraph.

Usage:

    python3 patterns/p47-ct-compare/controls/mkcontract.py            # write
    python3 patterns/p47-ct-compare/controls/mkcontract.py --check    # diff only
    python3 patterns/p47-ct-compare/controls/mkcontract.py --donor p10-fir-stencil
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(PDIR, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "harness"))
import check as gate  # noqa: E402

SPEC = os.path.join(PDIR, "spec.md")
FENCE = "```slb-contract"


def donor_paragraph(donor):
    """The shared paragraph, cut out of the donor's *parsed* `idiom.why`.

    Parsed, not grepped: `named_spelling_problem`'s whole point is that a copy
    living outside the hashed block does not count, so the donor's copy is
    taken from inside its block too."""
    dspec = os.path.join(REPO, "patterns", donor, "spec.md")
    if not os.path.exists(dspec):
        raise SystemExit(f"mkcontract: no donor spec at {dspec}")
    txt = open(dspec).read()
    m = re.search(r"```slb-contract\n(.*?)\n```", txt, re.S)
    if not m:
        raise SystemExit(f"mkcontract: donor {donor} has no slb-contract block")
    why = json.loads(m.group(1))["idiom"]["why"]
    i = why.find(gate.NAMED_SPELLING_BEGIN)
    j = why.find(gate.NAMED_SPELLING_END)
    if i < 0 or j < 0:
        raise SystemExit(f"mkcontract: donor {donor}'s why has no shared "
                         f"paragraph -- pick another donor")
    return why[i:j + len(gate.NAMED_SPELLING_END)]


# --------------------------------------------------------------------------
# p47's own prose. Everything the pattern says about ITS spellings lives here;
# the shared standard is appended from the donor and never written out here.
P47_WHY = (
    "POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a "
    "published spread cannot carry a safety number, so what ships is a "
    "named-spelling standard -- the tokens above must appear literally, "
    "uniform across all eight rungs, with ONE measured clause: a rung spells "
    "the same operands the way its language forces. "
    "ON p47 THE PINNED SPELLING IS THE SECURITY PROPERTY ITSELF, WHICH IS NEW. "
    "Every other pattern here pins spellings so that a COST comparison is "
    "between comparable programs; p47 pins them because the difference between "
    "`memcmp(a, b, tlen) == 0` and an or-accumulate over every byte IS the "
    "pattern, and it is invisible to every other check in the gate -- both "
    "expressions compute the same predicate, return the same value on every "
    "input, are memory-safe, are ASan/UBSan/Miri clean, and satisfy the same "
    "`ensures`. THE PIN IS THEREFORE THE ONLY THING IN THIS TREE THAT RECORDS "
    "WHICH RUNGS LEAK. "
    "WHY THE ACCUMULATOR IS NOT `volatile`, AND WHY `volatile` IS FORBIDDEN "
    "RATHER THAN MERELY UNUSED: the received advice for this idiom is to force "
    "the accumulator into memory. Measured on this toolchain it is unnecessary "
    "-- the plain accumulate is already constant in the first-mismatch "
    "position, to the instruction, at every optimisation level tested -- and it "
    "costs 6.35x, because it defeats vectorisation entirely in both gcc and "
    "clang. A cell that reached for it would be 6.35x dearer for no security "
    "gain and would make the R1-vs-R1h column mean something else; "
    "controls/gen_controls.py ships it as `h_vol` so the figure is checkable. "
    "WHY `fold(0u8` IS PINNED AND NOT MERELY `fold`: the identical algorithm "
    "with a `u64` accumulator lowers to a `movzwl/punpcklbw/punpcklwd/"
    "punpckldq` widening loop moving 4 bytes per iteration instead of 32, "
    "because LLVM vectorises the zero-extension rather than the xor. It is "
    "still constant-time; it is five times the work, and a rung that reached "
    "for it would put a codegen accident into the safety column. "
    "WHAT IS DELIBERATELY NOT PINNED is how the two tags are ADDRESSED -- R2 "
    "and R3 reslice with `&buf[a..b]` and R4/R5 index `buf` directly with "
    "`get_unchecked` -- because that is the SAFETY axis and it is the axis the "
    "R3-side span is measured along (../NOTES.md 8). R2 and R3 are pinned to "
    "the SAME addressing on purpose: they carry the identical panic-path "
    "structure on the shipped binaries (two `slice_index_fail` and eight "
    "`panic_bounds_check` call sites each), so `R2 - R3` differences the "
    "comparison idiom with the safety term cancelled exactly, and it is the "
    "only pair in this pattern that isolates the leak from everything else. "
    "WHY THE FOLD MAY NOT MIX IN A TAG BYTE: `acc = acc*31 + (MATCH|MISS)` "
    "folds the VERDICT and the number of comparisons performed and nothing "
    "else, so two windows with the same verdict sequence and different "
    "first-mismatch positions produce the SAME CHECKSUM in every rung. That is "
    "what makes `adversarial-k000.bin` and `adversarial-klast.bin` a timing "
    "row rather than a correctness row; a fold that could see a tag byte would "
    "turn p47 into a different pattern. "
    "WHY `memcmp` IS REQUIRED IN c/kernel.c AND FORBIDDEN EVERYWHERE ELSE: it "
    "is the bug. clang -O3 rewrites `memcmp(a,b,n) == 0` into a call to `bcmp`, "
    "which is the identical symbol rustc emits for `a == b` on slices, so the "
    "c-clang cell and the safe_naive cell enter one glibc routine and any "
    "difference between them is a LIBRARY difference (`.memory/"
    "03-measurement.md`, name the routine). ")


def block(donor):
    para = donor_paragraph(donor)
    why = P47_WHY + para
    obj = {
        "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
        "model": "model.py",
        "requires": ["off + len <= buf_len"],
        "ensures": ["result == tag_fold(buf, off, len)"],
        "note": (
            "requires/ensures above are DERIVED by check.py from verus.rs's own "
            "clause text through verus.translate, and the copy here must equal "
            "the derivation exactly. They are evaluated in Python against the "
            "bindings model.py yields per call (buf/off/len/buf_len/result) plus "
            "the helper it supplies (tag_fold). p47's bindings are the READ-ONLY "
            "set p03, p06, p10, p11, p12, p14, p16, p17, p05, p07 and p27 use: "
            "the kernel writes nothing and allocates nothing. "
            "**THE `ensures` IS THE FUNCTIONAL ONE AND IT IS SATISFIED BY THE "
            "LEAKING RUNG TOO.** That is not an oversight and it cannot be "
            "repaired by strengthening it: `tag_fold` is a statement about the "
            "VALUE the kernel returns, p47's defect does not change the value, "
            "and a timing property is a statement about the TRACE -- which "
            "instructions ran, and how many -- for which Verus's assertion "
            "language has no term at all. It also is not a property of this "
            "program: it is a property of the machine code LLVM chooses after "
            "Verus has finished. controls/proof_mutants.py's `m_leak` "
            "substitutes an early-exiting comparison into verus.rs and it "
            "VERIFIES, at the same obligation count, with this same `ensures`. "
            "**So the top rung of this ladder certifies a leaking kernel, and "
            "that is p47's deliverable rather than its gap** -- p17 (provably "
            "memory-safe and still leaking) one level up. "
            "What the `ensures` deliberately does NOT say is that `ntag` or "
            "`tlen` is honest: a precondition about the contents of a file is "
            "one no honest loader can discharge (`.memory/02-bench-rules.md`), "
            "and `twalk`'s own window guard is what stops the walk instead, so "
            "degenerate.bin and every adversarial row are INSIDE the verified "
            "domain and every rung agrees with model.py on all of them."),
        "idiom": {
            "required": [
                {
                    "c": "THE TIMING LINE, and the whole of what c/kernel.c does "
                         "differently: `memcmp(buf + off + p, buf + off + p + tlen, tlen) == 0`. "
                         "c/kernel_hardened.c writes the or-accumulate instead and is "
                         "otherwise character-identical, so the scoped-absent audit pair this "
                         "entry reports is on that rung and is correct.",
                    "rust": "THE TIMING LINE at R2, the idiomatic safe-Rust comparison and the "
                            "LEAKING one: `if a == b {` in safe_naive.rs. It lowers to a `bcmp` "
                            "call -- one R_X86_64_GLOB_DAT bcmp relocation reached from the kernel symbol "
                            "on the shipped binary -- which is the same glibc routine c-clang "
                            "enters. safe_tuned.rs, unsafe.rs and verus.rs write the "
                            "or-accumulate instead."
                },
                {
                    "c": "THE CONSTANT-TIME LINE, present in c/kernel_hardened.c and ABSENT from "
                         "c/kernel.c: `d |= (uint8_t)(buf[off + p + i] ^ buf[off + p + tlen + i]);`. "
                         "Every byte of the tag is read on every call whatever the data says.",
                    "rust": "THE CONSTANT-TIME LINE. In safe_tuned.rs it is the fold, spelled with "
                            "the `u8` accumulator the why key argues for: "
                            "`fold(0u8, |acc, (x, y)| acc | (x ^ y))`. In unsafe.rs and verus.rs "
                            "the language forces the other spelling -- there is no iterator over "
                            "`get_unchecked` -- so those two write the same accumulation as an "
                            "indexed loop and the entry scopes to R3. safe_naive.rs does NOT "
                            "have it, and that is the pattern."
                },
                {
                    "c": "the WINDOW GUARD, present in BOTH C rungs including the buggy one, so "
                         "p47 models no spatial bug: `while (o < ntag && len - p >= 2 * tlen) {`. "
                         "Subtraction-first, because p <= len is maintained by the guard itself "
                         "so the subtraction cannot wrap, while the additive form can overflow "
                         "and Verus rejects it.",
                    "rust": "the window guard, subtraction-first, in all four Rust rungs: "
                            "`while o < ntag && len - p >= 2 * tlen {`."
                },
                {
                    "c": "the VERDICT FOLD, and it may not see a tag byte -- see the why key: "
                         "`acc = acc * 31 + MATCH;` and `acc = acc * 31 + MISS;` in both C rungs.",
                    "rust": "the verdict fold in all four Rust rungs, spelled with the literal "
                            "multiplier: `.wrapping_mul(31).wrapping_add(MATCH)` and "
                            "`.wrapping_mul(31).wrapping_add(MISS)`."
                },
                {
                    "c": "the CURSOR ADVANCE is by a whole record, so a rung that compared "
                         "overlapping or misaligned tags cannot produce the same verdicts: "
                         "`p += 2 * tlen;` in both C rungs.",
                    "rust": "the cursor advance in all four Rust rungs: `p = p + 2 * tlen;`."
                },
                {
                    "c": "the header is decoded with + and * and never with | and <<, so "
                         "the whole specification stays inside linear arithmetic "
                         "(.memory/04-verus.md): `256 * (size_t)buf[off + 1]` in both C rungs.",
                    "rust": "the header decode, in all four Rust rungs: `256 *`."
                },
                "the number of comparisons actually performed is folded LAST, so a rung that "
                "stopped at a different point cannot produce the same checksum: `o` appears in "
                "the return expression of all eight rungs.",
                "the two header fields are rejected together and before any read of a tag, so no "
                "rung can divide by or index with zero: `ntag == 0` appears in all eight rungs."
            ],
            "forbidden": [
                "`volatile`",
                "`black_box`",
                "`fold(0u64`",
                # `memcmp` is REQUIRED in c/kernel.c -- it is the bug -- so it
                # cannot be forbidden universally, and a universal entry is
                # what `forbidden` means (harness/check.py::idiom_audit: "no
                # rung may spell it, in any language it declares"). A
                # rust-only entry is the correct shape and the audit scopes it
                # to the four Rust rungs.
                {"rust": "`memcmp`"},
                {"rust": "`bcmp`"},
                {"rust": "`libc`"},
                "`starts_with`",
                "`iter().eq(`",
                "`subtle`",
                "`chunks_exact`",
                "`from_le_bytes`",
                "`copy_from_slice`",
                "`position(`"
            ],
            "why": why
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
                "12 = MATCH 1 + MISS 1 + xacc 1 + twalk 1 + kernel 3 + main 5, "
                "each term MEASURED with `./verus_run.py verus.rs "
                "--verify-function <name> --verify-root` and not predicted. The "
                "zero terms are checkable the same way: u32_at and tag_fold are "
                "NON-RECURSIVE spec fns and report 0, while xacc and twalk are "
                "RECURSIVE and carry one termination query each; "
                "buf_get_unchecked, load_input and emit are external_body and "
                "report 0. TWO `const`s carry one query each "
                "(`.memory/04-verus.md`: a `const` inside verus! is its own "
                "obligation). kernel's 3 = body + TWO loop bodies (the "
                "comparison walk and the tag loop). ⚠ **main's term is 5 here, "
                "not the 4 that p03, p05, p06, p07, p10, p11, p12, p14, p17 and "
                "p27 record for the identical driver** -- measured both ways; "
                "the sum 1+1+1+1+3+5 is 12 and the pinned total is 12, so it is "
                "the per-item measurement that governs and the shared off-by-one "
                "note does not transfer to p47."),
            "twin_obligations_note": (
                "The obligation count in the OTHER configuration -- `verus.rs "
                "--cfg slb_twin`, which is where step 5c-twin checks the twins. "
                "12 shipped + 1, the single trusted item inside the twin regime "
                "being slb_twin_buf_get_unchecked. `load_input` and `emit` are "
                "outside the regime (external_body with no `ensures` and no "
                "`unsafe` body) and have no twins."),
            "unsafe_justifications": {},
            # Hand-transcribed from verus.rs, NOT derived from it: a pin
            # generated out of the artefact it pins certifies nothing, which is
            # the p27 lesson this whole file is written around.
            "items": {
                "verus.rs": {
                    "u32_at": {"external": None, "requires": [], "ensures": []},
                    "xacc": {"external": None, "requires": [], "ensures": []},
                    "twalk": {"external": None, "requires": [], "ensures": []},
                    "tag_fold": {"external": None, "requires": [], "ensures": []},
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
                    "load_input": {"external": "verifier::external_body",
                                   "requires": [], "ensures": []},
                    "emit": {"external": "verifier::external_body",
                             "requires": [], "ensures": []},
                    "kernel": {
                        "external": None,
                        "requires": ["off + len <= buf@.len()"],
                        "ensures": ["r == tag_fold(buf@, off as int, len as int)"]
                    },
                    "main": {"external": None, "requires": [], "ensures": []}
                }
            }
        },
        "driver": {
            "statements": 12,
            "c_source": "c/main.c",
            "regions": ["safe_naive.rs", "safe_tuned.rs", "unsafe.rs",
                        "verus.rs", "c/main.c"],
            "aliases": {
                "c": {"n_body": "bytes.len()", "bytes": "bytes.as_slice()",
                      "inp.n_iters": "n_iters"}
            },
            "call_args": {"c": {"kernel": [0, 2, 3]}},
            "canonical": [
                "n_blob = bytes . len ( ) ;",
                "buf = bytes . as_slice ( ) ;",
                "acc = 0 ;",
                "if stride_w >= 8 && stride_w <= n_blob",
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
                "work_per_call is **bytes of the window** -- `stride`, 200 on "
                "small and 1032 on large -- which is p16's, p05's, p11's, p12's, "
                "p06's, p14's, p10's and p27's denomination. WHICH WAY THE "
                "ESTIMATE ERRS, and p47 is the first pattern here where THE "
                "DIRECTION DEPENDS ON THE RUNG: the constant-time rungs read "
                "every one of the `2*tlen*ntag` tag bytes, so `stride` "
                "over-counts only by the 8 header bytes and any window padding; "
                "the LEAKING rungs read FEWER bytes than the window contains -- "
                "that is the bug -- so on a blob whose comparisons all mismatch "
                "early they touch 32 bytes per `2*tlen` and the per-byte rate "
                "falls with `tlen`. Both probe inputs are chosen so that every "
                "rung clears the harness default of 0.25 Ir per byte with room "
                "(../NOTES.md 3): `small` mismatches at k = 5 with tlen 24, so "
                "even `bcmp` reads a whole 32-byte block per comparison, and "
                "`large` has two of its eight comparisons EQUAL, which forces a "
                "full scan of those two in every rung. model.py declares no "
                "min_ir_per_work, so the harness default applies unchanged. What "
                "the floor still catches is the failure it exists to catch -- a "
                "kernel the optimiser collapsed to nothing. The two probe inputs "
                "differ in work_per_call (200 vs 1032) precisely so check.py's "
                "d(Ir)/d(work) assertion has two shapes and can run at all.")
        },
        "identity": [
            {
                "a": "unsafe",
                "b": "verus",
                "O0": "norel",
                "O3": "exact",
                "why": (
                    "R4 == R5: the proof licenses unsafe code at zero cost. On "
                    "p47 the pin carries a second job no other pattern's does -- "
                    "it is what makes the sentence *the proved rung leaks* a "
                    "statement about a BINARY rather than about a source file. "
                    "`.memory/06-catalogue.md` hazard 2 is that a text pin binds "
                    "the source and not the object; here R5's object is R4's "
                    "object byte for byte, R4's object is disassembled in "
                    "../NOTES.md 1 and contains a vectorised `pxor/por` loop with "
                    "no data-dependent branch, and the leak that R5 fails to "
                    "exclude is therefore demonstrated on the shipped machine "
                    "code rather than argued from the text. At O0 the crate names "
                    "differ in length so call displacements differ, which is link "
                    "layout and not codegen, hence `norel` there and `exact` at "
                    "O3.")
            }
        ],
        "miri": {
            "pair": ["unsafe", "verus"],
            "sources": ["unsafe.rs"],
            "required": True,
            "reason": (
                "R4 and R5 ARE byte-identical at O3. Since TASK_010 "
                "`.memory/02-bench-rules.md` makes Miri mandatory for any "
                "pattern with a trusted item, which check.py DERIVES from "
                "verus.rs rather than reading from this flag. **On p47 Miri is "
                "expected to be, and is, entirely silent about the pattern's "
                "bug** -- it checks the unchecked reads, which are the thing "
                "p47's C rung gets RIGHT. It is listed here because the trusted "
                "item is real and a wrong `buf_get_unchecked` would still be "
                "invisible to Verus; it is not evidence about the timing "
                "property and ../NOTES.md 7 says so."),
            "blocked_reason": (
                "miri is installed on the nightly toolchain beside the pinned "
                "one (TOOLCHAIN.md). If it is missing, this row is blocked "
                "rather than failed.")
        }
    }
    return obj


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--donor", default="p10-fir-stencil")
    ap.add_argument("--check", action="store_true",
                    help="print the block, do not write spec.md")
    a = ap.parse_args()

    obj = block(a.donor)

    # The refusal that p27's generator did not have. `named_spelling_problem`
    # is imported from the gate, not re-implemented, so this cannot drift.
    prob = gate.named_spelling_problem(obj)
    if prob:
        raise SystemExit("mkcontract: REFUSING to write -- " + prob.split("\n")[0])
    para_len = len(gate.NAMED_SPELLING_BEGIN)  # touched so the import is used
    del para_len

    body = json.dumps(obj, indent=2, ensure_ascii=False)
    if a.check:
        print(body)
        return 0
    if not os.path.exists(SPEC):
        raise SystemExit(f"mkcontract: {SPEC} does not exist -- write the prose "
                         f"half first; this generator only replaces the fenced "
                         f"block")
    txt = open(SPEC).read()
    m = re.search(r"```slb-contract\n.*?\n```", txt, re.S)
    new = FENCE + "\n" + body + "\n```"
    if m:
        txt = txt[:m.start()] + new + txt[m.end():]
    else:
        txt = txt.rstrip() + "\n\n" + new + "\n"
    open(SPEC, "w").write(txt)
    print(f"mkcontract: wrote {len(body)} bytes of contract into {SPEC} "
          f"(donor {a.donor}, shared paragraph "
          f"{len(gate.NAMED_SPELLING_SHA256)}-char pin verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
