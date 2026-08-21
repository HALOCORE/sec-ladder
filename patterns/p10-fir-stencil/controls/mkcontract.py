#!/usr/bin/env python3
"""p10's `slb-contract` block generator.

The block in ../spec.md is machine-readable and is hashed into
`contract_sha256`, so it is generated from this file rather than hand-edited:
that keeps the byte-identical shared paragraph of `idiom.why` genuinely
byte-identical (it is read out of p18's spec.md at build time and appended
verbatim, so a drift is impossible by construction rather than by diffing), and
it makes every later edit a diff of THIS file.

    python3 patterns/p10-fir-stencil/controls/mkcontract.py            # print
    python3 patterns/p10-fir-stencil/controls/mkcontract.py --write     # splice

`--write` replaces the text between the ```slb-contract fences in ../spec.md and
prints the new sha256 of the block. `--sha` prints the sha256 without writing.
"""
import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
SPEC = os.path.join(PDIR, "spec.md")
FENCE = re.compile(r"(```slb-contract\s*\n)(.*?)(```)", re.S)

# The paragraph every pattern's `why` ends with, verbatim. Read out of a shipped
# pattern rather than pasted, so "byte-identical" is a property of the build and
# not of a diff somebody remembered to run. p18, p14, p06 and p03 all end with
# it; p16 does not (it predates the repair) and is not used as the source.
SHARED_SOURCE = os.path.join(REPO, "patterns", "p18-varint-shift", "spec.md")
SHARED_HEAD = ". NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018"


def shared_paragraph():
    txt = open(SHARED_SOURCE).read()
    m = FENCE.search(txt)
    why = json.loads(m.group(2))["idiom"]["why"]
    i = why.index(SHARED_HEAD)
    return why[i:]


P10_WHY = (
    "each deletes something this pattern IS, and a rung that does it is a "
    "different benchmark whose numbers are not comparable (../spec.md's second "
    "sentence). "

    "THE ONLY THING R1 GETS WRONG IS ONE CHARACTER, AND IT IS IN A COMPARISON "
    "BOTH C RUNGS ALREADY PERFORM. `last` is the window offset of the LAST "
    "sample byte the kernel will read, so the test that keeps it inside the "
    "window is `last >= len`; c/kernel.c writes `last > len`, which admits "
    "`last == len` -- EXACTLY ONE BYTE past the window and not a byte more. "
    "Every other line of the two C cells is character for character identical, "
    "so `c-gcc-h` minus `c-gcc` is the price of that one character and of "
    "nothing else. THAT IS A DIFFERENT SHAPE FROM EVERY EARLIER PATTERN HERE: "
    "p02's, p07's, p16's, p17's and p18's R1 OMITS A LINE, so hardening adds "
    "instructions (+5 gcc / +12 clang on p02, +2.00 per executed pop on p03, "
    "per input byte on p18). p10's R1 already executes the comparison and "
    "merely relates its two operands wrongly, so the hardened cell is the same "
    "instruction stream with one opcode byte changed (`ja` -> `jae`) and the "
    "hardening cost is expected to be ZERO. ../NOTES.md 4 measures it rather "
    "than assuming it. "

    "THE BUG IS CONDITIONAL ON ATTACKER DATA AND THAT IS FORCED BY THE GATE, "
    "not chosen for elegance: `harness/check.py` stage 2 requires every cell "
    "including R1 to print `model.py`'s checksum on every non-`adversarial-*` "
    "input, so a bug that fires on a well-formed window could not be shipped at "
    "all. `inputs/gen.py` packs every benign window exactly full "
    "(`stride == 8 + taps + n`, so `last == len - 1`), and the two rungs are "
    "then behaviourally identical on every benign input -- which is also what "
    "makes the R1-vs-R1h COST comparison legal here where "
    "`.memory/02-bench-rules.md`'s first rule forbids it on p12 and p13: on "
    "every input the cost is measured on, the unhardened rung commits no "
    "undefined behaviour and refuses no work. "

    "THE HARM IS EXACTLY ONE BYTE OF OVERREAD, WHICH IS THE POINT AND NOT A "
    "WEAKNESS. An off-by-one at a boundary cannot reach further than one "
    "element by definition, and `adversarial-farover.bin` is the row that says "
    "so: a window declaring `n` far beyond what it holds is rejected by R1 and "
    "R1h ALIKE, so R1's defect buys an attacker one byte and nothing more. "
    "Whether that byte is observable is a property of the ALLOCATION and not of "
    "the program, which is p02's result on the read side: "
    "`adversarial-fencepost.bin` puts the window at the very end of the payload "
    "so the read leaves the allocation and ASan fires, and "
    "`adversarial-fenceslack.bin` is the SAME window with three trailing "
    "payload bytes that do not form a further window, where the identical "
    "off-by-one reads a byte that is merely the wrong one -- ASan clean, "
    "UBSan clean, exit 0, and a wrong answer. "

    "THE ALGORITHM IS A WEIGHTED FIR AND NOT A BOX FILTER, AND THAT IS A "
    "CORRECTNESS REQUIREMENT ON THE COMPARISON RATHER THAN A TASTE. A box "
    "filter (all weights equal) has an O(n) running-accumulator form -- add the "
    "entering sample, subtract the leaving one -- and an O(n*r) tap-loop form, "
    "and a ladder in which any rung reached for the first while the others used "
    "the second would be comparing two different algorithms with different "
    "complexities. A per-tap coefficient `w[j]` makes the incremental form "
    "impossible for every rung in every language at once, so O(nout * taps) is "
    "honest by construction and the `you pessimised C` objection has no "
    "purchase. It is also the shape real DSP and image code has. "
    "../NOTES.md 0 records the rejected candidates. "

    "THERE IS NO DIVISION ANYWHERE ON THE OUTPUT PATH, DELIBERATELY. A FIR is "
    "normally normalised by the coefficient sum, and a per-output `div` would "
    "cost ONE `Ir` to callgrind (`.memory/03-measurement.md`, the `div` pricing "
    "section) and tens of variable cycles to the machine -- so it would be "
    "nearly free in the column this project publishes and expensive in the one "
    "it cannot measure well, and it would sit inside every per-tap law p10 "
    "fits. The kernel sums into a `u32` and folds the raw sums; the "
    "disassembly of all eight cells is checked for `div`/`idiv` and contains "
    "none (../NOTES.md 1). "

    "ALL ARITHMETIC IS WRAPPING, SO THERE IS NO OVERFLOW OBLIGATION TO "
    "DISCHARGE AND NO PRECONDITION ON VALUES. `s` is a `u32` accumulated with "
    "`wrapping_add`/`wrapping_mul` in Rust and with C's unsigned arithmetic "
    "(6.2.5p9) in C, and the fold is the project's usual wrapping Horner chain. "
    "`.sum(` is forbidden for exactly this reason: `Sum for u32` uses `+`, "
    "which panics under `-C debug-assertions=on` and under Miri, so a rung "
    "using it would behave differently in two of the gate's own "
    "configurations while looking identical in the twenty-four measured cells. "

    "WHAT IS PINNED IS THE OPERATIONS AND THE TWO GUARDS; WHAT IS DELIBERATELY "
    "LEFT FREE IS THE SPELLING OF THE TAP LOOP, AND THAT FREEDOM IS THE "
    "EXPERIMENT. p10 exists to ask whether safe Rust's tax is proportional to "
    "the NUMBER OF INDEXING OPERATIONS or flat, and the three spellings that "
    "answer it -- index every tap (`sam[i + j]`), slice the window once and "
    "reduce it (`sam.windows(taps)`), and `get_unchecked` -- differ in nothing "
    "but that. Pinning a loop form would delete the question. What is pinned "
    "instead is that every rung computes the same `2r+1` products of the same "
    "operands in the same order into the same wrapping `u32`, that both guards "
    "are present in every rung, and that the header is decoded the same way. "
    "`windows(` is NOT forbidden and NOT required: it is the R3 idiom this "
    "project has never used, `grep -rn 'windows(' patterns/*/*.rs` returned "
    "nothing before p10, and it takes a RUNTIME size -- verified by compiling "
    "`sam.windows(taps)` where `taps` is read out of the file (../NOTES.md 0.1) "
    "-- so it needs no compile-time radius and costs no `div`, which "
    "`chunks_exact` with a runtime size does (`.memory/03-measurement.md`). "

    "`chunks_exact` is forbidden because a RUNTIME chunk size computes "
    "`len - len % chunk_size` and lowers to a hardware `div`, which callgrind "
    "prices at 1 `Ir` and the machine at tens of cycles -- it would sit inside "
    "p10's per-tap law and be invisible in the column that law is fitted on -- "
    "and because p16 measured that the chunk width alone moves that pattern's "
    "per-byte rate over a 31% range. `from_le_bytes` deletes the written-out "
    "little-endian header decode every rung shares AND is not available to an "
    "R4 at all at the pinned vstd (`from_le_bytes` and the "
    "`try_into`/`TryFromSliceError` route to it are both `is not supported`, "
    "measured on p05 and p16 at TASK_027_REVIEW and again on p06, p14 and "
    "p18), so a rung using it would compare a safe cell against an unsafe cell "
    "that cannot exist. `.sum(` is forbidden for the wrapping reason above. "
    "`step_by(` is forbidden because it would let a rung visit a subset of the "
    "taps and still satisfy every other entry here. `copy_from_slice` is "
    "forbidden because p10's kernel WRITES NOTHING ANYWHERE -- it has no "
    "destination buffer, no scratch and no table -- and a rung that materialised "
    "the window would be measuring an allocation this pattern does not have. "

    "EVERY EXCLUSION HERE IS WHOLE-PATTERN AND NOT SCOPED TO SOME RUNGS, which "
    "is deliberate: `.memory/01-ladder.md`'s direction test fired on p13 "
    "exactly because three of its entries named some rungs and exempted "
    "`safe_tuned.rs`, so R3 was permitted a spelling R4 was forbidden and "
    "48%/17% of the published margin was the pin. A whole-pattern exclusion "
    "keeps the two sides of the comparison equal. Nothing in `required` is "
    "scoped to a subset of rungs either; the per-language keys on entries 0 and "
    "5..8 exist because C and Rust spell the same operation differently, not "
    "because some rungs are exempt. "

    "THE FOLD IS OVER THE FULL RECORDED EXTENT AND ORDER-SENSITIVE, and p10's "
    "reason is TASK_004_REVIEW's ELISION reason plus one that is p10's own. "
    "Elision: a fold that read only part of the output would let the optimiser "
    "delete the rest of the tap loop, which is the entire kernel. p10's own: "
    "the bug changes WHETHER THE KERNEL RUNS AT ALL on the input that triggers "
    "it -- R1h returns 0 where R1 returns a fold -- so the fold sees it "
    "structurally and not only through the value of the one stolen byte, and "
    "`nout` is folded at the end so a rung computing a different number of "
    "outputs cannot produce the same checksum either. That matters because the "
    "stolen byte MAY be zero, and its coefficient may be small: p06's lesson is "
    "that a sum-fold cannot observe a permutation, and the analogue here would "
    "have been a fold that could not observe a single extra tap. Checked in "
    "../NOTES.md 2 rather than asserted."
)


ITEMS = {'u32_at': {'external': None, 'requires': [], 'ensures': []}, 'dotp': {'external': None, 'requires': [], 'ensures': []}, 'fwalk': {'external': None, 'requires': [], 'ensures': []}, 'fir_fold': {'external': None, 'requires': [], 'ensures': []}, 'buf_get_unchecked': {'external': 'verifier::external_body', 'requires': ['i < v@.len()'], 'ensures': ['r == v@[i as int]']}, 'slb_twin_buf_get_unchecked': {'external': None, 'requires': ['i < v@.len()'], 'ensures': ['r == v@[i as int]']}, 'load_input': {'external': 'verifier::external_body', 'requires': [], 'ensures': []}, 'emit': {'external': 'verifier::external_body', 'requires': [], 'ensures': []}, 'kernel': {'external': None, 'requires': ['off + len <= buf@.len()'], 'ensures': ['r == fir_fold(buf@, off as int, len as int)']}, 'main': {'external': None, 'requires': [], 'ensures': []}}

OBL_NOTE = "10 = u32_at 0 + dotp 1 + fwalk 1 + fir_fold 0 + kernel 3 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained, and the zero terms are checkable the same way: u32_at and fir_fold are NON-RECURSIVE spec fns and report 0, while dotp and fwalk are RECURSIVE and carry one termination query each; buf_get_unchecked, load_input and emit are external_body and report 0. kernel's 3 = body + TWO loop bodies (the output walk and the tap loop), and BOTH loops exit exactly one way, so neither needs `invariant_except_break` -- which is a difference from p18, whose two loops both exit early. There is no `by (bit_vector)` and no `|` or `<<` anywhere in this file: the header decode is written with + and * and the kernel performs no other bit operation at all, so the whole proof stays in linear arithmetic. p10 declares NO `const`, so there is no const query -- unlike p03, p06, p08 and p18 -- and `global size_of usize == 8;` carries none either, which is checkable by the arithmetic above summing to exactly 10. **That declaration is p10's one genuinely new Verus fact and it was MEASURED, not guessed**: Verus treats `usize` as architecture-independent, so `2 * r + 1` on a `usize` built from four header bytes is `possible arithmetic underflow/overflow` without it (exact error text in ../NOTES.md 6), and p07 dodged the identical obligation by computing its length check in `u64` -- a route p10 cannot take, because ../spec.md pins the spelling `2 * r + 1` in all seven rungs. It is CHECKED against the compilation target rather than assumed, so it adds nothing to the TCB. main's 5 is quoted AS MEASURED and does not decompose from the command line: body + driver loop + one per by-block would predict 6 and Verus reports 5, the identical off-by-one p03's, p05's, p06's, p07's, p11's, p12's, p14's, p17's and p18's spec.md record for the identical driver. `.memory/04-verus.md`'s one-query-per-function-plus-one-per-loop rule of thumb gives 8 here and is therefore not the derivation."

TWIN_NOTE = "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. 10 shipped + 1, and the term is measured the same way: `--cfg slb_twin --verify-function slb_twin_buf_get_unchecked --verify-root` reports `1 verified`. It is +1 rather than +3 because load_input and emit state NO `ensures` and contain NO `unsafe`, so they are outside the twin regime (`.memory/04-verus.md`: the regime is keyed on `external_body` + a non-empty `ensures` OR `unsafe`). p10 has the same three-item trusted base as p18, one item with a `requires`, and for the same structural reason: its kernel performs exactly ONE kind of memory access, a byte read of the input window, so there is exactly one accessor to trust. There is no scratch, no output buffer, no bulk copy and no write of any kind. **What differs from p18 is that on p10 that one `requires` IS the pattern's bug** -- `i < v@.len()` is exactly what `c/kernel.c`'s `last > len` fails to establish -- where p18's accessor precondition had nothing to do with its arithmetic defect. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg."

COLLAPSE_NOTE = "work_per_call is **taps** -- one multiply-accumulate -- i.e. `nout * taps`, and NOT bytes of the window. p10's kernel reads every sample byte `taps` times and every coefficient byte `nout` times, so a floor denominated in window bytes would understate the work by a factor of `taps` and would be cleared on every input without testing anything -- exactly the 'skipping walker denominated in buffer bytes' shape harness/check.py names. WHICH WAY THE ESTIMATE ERRS: it is EXACT on both probe inputs and LOW elsewhere. model.py takes the MINIMUM over the blob's windows, because the driver's `k` is pseudo-random and the model cannot know which windows a given `n_iters` visits; inputs/gen.py emits small.bin and large.bin with every window carrying the same `(n, r)`, so the minimum IS the value for every call. small is 96 windows of (n=72, r=4): taps 9, nout 64, 576 taps/call. large is 32768 windows of (n=136, r=8): taps 17, nout 120, 2040 taps/call. The two shapes differ in BOTH structural parameters, which is what check.py's d(Ir)/d(work) assertion across two probe shapes needs. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per tap applies unchanged, and the margin is stated as a MEASUREMENT rather than as an argument that the loop cannot vectorise: **p10's tap loop DOES vectorise** at -O3 to an SSE2 body of 17 instructions per 8 samples, i.e. 2.125 Ir/tap, which is the smallest per-tap figure any p10 cell reaches and is 8.5x the floor (../NOTES.md 8). That is the opposite of p18's argument for the same default and is the honest form of it here. work_unit_bits is 16 -- one sample byte and one coefficient byte are consumed per tap -- so the effective absolute bound under min_ir_per_work would be 0.001953125 x 16 = 0.03125 if p10 declared one, which it does not."

IDENT_WHY = "R4 == R5: the proof licenses unsafe code at zero cost, on a kernel whose load-bearing obligation is the SPATIAL one `c/kernel.c` gets wrong by a single character. The byte-identity result now covers a nested loop over a RUNTIME radius whose safety rests on `8 + taps + n - 1 < len` -- an index bound, not a length bound -- and it holds with no lemma in the kernel at all: the only ghost lines in `kernel` are two `assert`s unfolding a recursive spec fn at its base case, plus the `spec_slice_len` mention. **The pin has no measured price on p10**, which is worth recording because p06's and p14's did: both had to bind a value to a local before a store, because R5's store is a CALL and R4's is an assignment. p10 has no store at all -- it writes nothing anywhere -- so the argument-evaluation-order problem that broke their -O0 identity has nothing to act on here. At O0 the crate names differ in length so call displacements differ -- link layout, not codegen -- which is why O0 is pinned `norel` and O3 `exact`."


def contract():
    return {
        "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
        "model": "model.py",
        "requires": ["off + len <= buf_len"],
        "ensures": ["result == fir_fold(buf, off, len)"],
        "note": (
            "requires/ensures above are DERIVED by check.py from verus.rs's own "
            "clause text through verus.translate, and the copy here must equal "
            "the derivation exactly. They are evaluated in Python against the "
            "bindings model.py yields per call (buf/off/len/buf_len/result) plus "
            "the helper it supplies (fir_fold). p10's bindings are the READ-ONLY "
            "set p03, p06, p11, p12, p14, p16, p17, p05, p07 and p18 use and NOT "
            "p02's before/after set: p10's kernel WRITES NOTHING ANYWHERE -- no "
            "destination buffer, no scratch, no table; `s`, `acc`, `i` and `j` "
            "are scalars -- so there is no buffer for an `after` binding to name. "
            "THE SECURITY PROPERTY HERE IS SPATIAL AND IS CARRIED BY THE TRUSTED "
            "ACCESSOR'S `requires` (`i < v@.len()`), which is p10's difference "
            "from p18: p18's bug is an out-of-range SHIFT that no accessor "
            "precondition can exclude, while p10's is an out-of-bounds READ, "
            "exactly what that precondition excludes. The `ensures` is "
            "nevertheless the FUNCTIONAL one and not a memory-safety-only one, "
            "for the reason p09 established: a memory-safety-only specification "
            "is blind to every functional change, and p10 has a functional "
            "mutant class -- a rung that folds `nout + 1` outputs, or that "
            "applies the coefficients in reverse -- that stays in bounds. What "
            "the `ensures` deliberately does NOT say is that `n` or `r` is "
            "honest, or that the coefficients sum to anything in particular: "
            "every adversarial input is INSIDE the verified domain and the "
            "proof is silent about whether the answer is the one the encoder "
            "meant, which is p17's limit."
        ),
        "idiom": {
            "required": [
                {
                    "c": "THE SAFETY LINE, and it is ONE CHARACTER rather than a whole line: `if (last >= len)` in c/kernel_hardened.c. c/kernel.c writes `if (last > len)` -- the same comparison between the same two operands, with the wrong relation -- and that single character is the whole difference between the two cells. `last` is an INDEX (the window offset of the last sample byte the kernel reads), so last == len is already one past the window.",
                    "rust": "THE SAFETY LINE: `if last >= len {` in all four Rust rungs. In Rust it is not the only thing standing between the program and the overread -- the bounds check is -- but it is what makes the four Rust rungs return 0 where c/kernel.c returns a fold, so it is what keeps the checksum comparable across all seven rungs on the benign inputs."
                },
                {
                    "c": "THE WINDOW GUARD, present in every rung including R1, so that `nout = n - 2*r` cannot underflow and p10 has NO wild index to model on any input: `if (n < taps)` in both C rungs. p10's bug is an off-by-one and its harm is one byte; an underflowed `nout` would be a different and much larger bug, and excluding it in every rung is what keeps the two cells one character apart.",
                    "rust": "THE WINDOW GUARD, present in every rung including R1: `if n < taps {` in all four Rust rungs."
                },
                "THE TAP COUNT IS TWICE THE RADIUS PLUS ONE AND IS COMPUTED AT 64 BITS IN EVERY RUNG, so a declared radius near 2^32 cannot wrap it into a small one: `2 * r + 1` in all seven rungs.",
                "THE LAST-SAMPLE OFFSET IS COMPUTED AS AN INDEX AND GIVEN A NAME, because that is where the fencepost lives and naming it is what makes the one-character difference legible: `+ taps + n - 1` in all seven rungs.",
                "THE COEFFICIENTS COME FIRST IN THE WINDOW AND THE SAMPLES LAST, so the sample array ends at the window's end and an off-by-one leaves the window rather than landing on a neighbouring field: `8 + taps` is the sample base in all seven rungs.",
                {
                    "c": "EVERY TAP IS A PRODUCT OF ONE SAMPLE AND ONE COEFFICIENT, ACCUMULATED INTO A 32-BIT WRAPPING SUM, and the tap loop's SPELLING is deliberately not pinned because comparing spellings is what p10 is for: `s = s + (uint32_t)` in both C rungs (unsigned, 6.2.5p9).",
                    "rust": "EVERY TAP IS A PRODUCT OF ONE SAMPLE AND ONE COEFFICIENT, ACCUMULATED INTO A 32-BIT WRAPPING SUM: `s = s.wrapping_add(` in all four Rust rungs, and the product is `.wrapping_mul(`. The tap loop's SPELLING is not pinned -- indexed, windows() and get_unchecked are all in contract -- and that freedom is the experiment."
                },
                {
                    "c": "...and the multiplication is the one operation the loop performs. Rust spells it wrapping_mul; C has no such spelling and writes the operator: `* (uint32_t)` in both C rungs.",
                    "rust": "...and the product: `.wrapping_mul(` in all four Rust rungs."
                },
                {
                    "c": "THE OUTPUT VALUE IS FOLDED, in order, so a rung that applied the coefficients in the wrong order or dropped a tap cannot produce the same checksum: `acc = acc * 31 + (uint64_t)s;` in both C rungs.",
                    "rust": "THE OUTPUT VALUE IS FOLDED, in order: `.wrapping_add(s as u64)` in all four Rust rungs."
                },
                {
                    "c": "...and the OUTPUT COUNT is folded once at the end, so a rung that computed a different number of outputs -- which is exactly what an off-by-one does -- cannot produce the same checksum either: `* 31 + (uint64_t)nout` in both C rungs.",
                    "rust": "...and the OUTPUT COUNT is folded once at the end: `.wrapping_add(nout as u64)` in all four Rust rungs."
                },
                "the little-endian u32 header fields are decoded with + and * rather than | and <<, so the header decode is linear arithmetic and stays out of the way of the tap loop this pattern measures: `+ 65536 *` in all seven rungs.",
                "...and their top bytes: `+ 16777216 *` in all seven rungs."
            ],
            "forbidden": [
                "`chunks_exact`",
                "`from_le_bytes`",
                "`.sum(`",
                "`step_by(`",
                "`copy_from_slice`"
            ],
            "why": P10_WHY + shared_paragraph(),
        },
        "verus": {
            "call_site": "main",
            "kernel_item": "kernel",
            "translate": {
                "buf@.len()": "buf_len",
                "buf@": "buf",
                " as int": "",
                "r": "result",
            },
            "obligations": {"verus.rs": 10},
            "twin_obligations": {"verus.rs": 11},
            "obligations_note": OBL_NOTE,
            "twin_obligations_note": TWIN_NOTE,
            "unsafe_justifications": {},
            "items": {"verus.rs": ITEMS},
        },
        "driver": {
            "statements": 12,
            "c_source": "c/main.c",
            "regions": ["safe_naive.rs", "safe_tuned.rs", "unsafe.rs",
                        "verus.rs", "c/main.c"],
            "aliases": {"c": {"n_body": "bytes.len()",
                              "bytes": "bytes.as_slice()",
                              "inp.n_iters": "n_iters"}},
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
                "}",
            ],
        },
        "collapse": {
            "probe_inputs": ["small.bin", "large.bin"],
            "probe_iters": [100, 200],
            "note": COLLAPSE_NOTE,
        },
        "identity": [
            {
                "a": "unsafe",
                "b": "verus",
                "O0": "norel",
                "O3": "exact",
                "why": IDENT_WHY,
            }
        ],
        "miri": {
            "pair": ["unsafe", "verus"],
            "sources": ["unsafe.rs"],
            "required": True,
            "reason": "R4 and R5 ARE byte-identical at O3, and since TASK_010 that does not make Miri optional: it is mandatory for any pattern with a trusted item.",
            "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed.",
        },
    }


def render(doc):
    return json.dumps(doc, indent=2, ensure_ascii=True) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--sha", action="store_true")
    a = ap.parse_args()
    doc = contract()
    body = render(doc)
    sha = hashlib.sha256(body.encode()).hexdigest()
    # The `idiom` object hashed on its own. The whole-block hash necessarily
    # moves when the two Verus obligation counts and the `items` map are filled
    # in from `./verus_run.py` (they are MEASUREMENTS and cannot precede the
    # proof), so the whole-block hash alone cannot support "no `required` or
    # `forbidden` entry moved after I measured". This one can: it covers
    # exactly the object `.memory/01-ladder.md`'s direction test governs, and
    # ../NOTES.md 0 records it as first written.
    isha = hashlib.sha256(
        json.dumps(doc["idiom"], indent=2, ensure_ascii=True,
                   sort_keys=True).encode()).hexdigest()
    if a.write:
        txt = open(SPEC).read()
        if not FENCE.search(txt):
            raise SystemExit("mkcontract.py: spec.md has no ```slb-contract fence")
        txt = FENCE.sub(lambda m: m.group(1) + body + m.group(3), txt, count=1)
        open(SPEC, "w").write(txt)
        print("wrote", SPEC)
    elif not a.sha:
        sys.stdout.write(body)
    print("contract_sha256(as rendered):", sha, file=sys.stderr)
    print("idiom_sha256(sorted keys)  :", isha, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
