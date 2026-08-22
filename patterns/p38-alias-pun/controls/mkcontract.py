#!/usr/bin/env python3
"""Write ../spec.md: the prose contract and the fenced `slb-contract` block.

⚠ **THE SHARED NAMED-SPELLING PARAGRAPH IS READ OUT OF A DONOR PATTERN'S
`spec.md` AND NEVER EMBEDDED HERE** (`.memory/05-layout.md`). Embedding it is
the defect `patterns/p27-handle-table/controls/mkspec.py` shipped: a second copy
drifts, and `harness/check.py::named_spelling_problem` then fails one pattern
while the standard says every copy is byte-identical. This generator refuses to
write anything if the assembled contract does not satisfy `idiom_problems` and
`named_spelling_problem`.

⚠ **`spec.md` IS GENERATED, SO EDIT THIS FILE AND RE-RUN IT** -- three tasks in
a row shipped a `spec.md` edit a generator would have silently reverted, and one
of them was the task that fixed that defect (`.memory/05-layout.md`).

    python3 patterns/p38-alias-pun/controls/mkcontract.py           # write
    python3 patterns/p38-alias-pun/controls/mkcontract.py --check   # diff only
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
DONOR = os.path.join(REPO, "patterns", "p47-ct-compare", "spec.md")
OUT = os.path.join(PDIR, "spec.md")

sys.path.insert(0, os.path.join(REPO, "harness"))
import check as checkmod   # noqa: E402


def donor_paragraph(path=DONOR):
    """The shared named-spelling paragraph, out of a sibling's hashed block."""
    txt = open(path).read()
    m = re.search(r"```slb-contract\s*\n(.*?)```", txt, re.S)
    if not m:
        raise SystemExit(f"mkcontract.py: {path} has no slb-contract block")
    why = json.loads(m.group(1))["idiom"]["why"]
    i = why.find(checkmod.NAMED_SPELLING_BEGIN)
    j = why.find(checkmod.NAMED_SPELLING_END)
    if i < 0 or j < 0:
        raise SystemExit(f"mkcontract.py: donor {path} carries no shared "
                         f"paragraph -- pick another donor")
    return why[i:j + len(checkmod.NAMED_SPELLING_END)]


# ---------------------------------------------------------------- the why ----
WHY_HEAD = (
    "POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a "
    "published spread cannot carry a safety number, so what ships is a "
    "named-spelling standard -- the tokens above must appear literally, uniform "
    "across all eight rungs, with ONE measured clause: a rung spells the same "
    "operands the way its language forces. "
    "ON p38 THE PINNED SPELLING IS THE UNDEFINED BEHAVIOUR ITSELF. "
    "`*(const uint32_t *)r` in c/kernel.c and "
    "`(uint32_t)r[0] + 65536 * (uint32_t)r[1]` in c/kernel_hardened.c compute "
    "the same function of the same two bytes on this target and differ only in "
    "that the first is undefined by C99 6.5p7. THEY ARE NOT THE SAME MACHINE "
    "CODE, AND THAT IS MEASURED RATHER THAN ASSUMED: the defined spelling costs "
    "6 static instructions on gcc and 10 on clang, by two different routes -- "
    "clang and rustc MERGE the two 16-bit loads back into one 32-bit load and "
    "then fail to simplify `(x & 0xffff) + 65536 * (x >> 16)` back to `x`, "
    "while gcc does not merge at all and pays for two movzwl plus a shift and "
    "an add. rustc pays clang's 10 in every Rust rung (../NOTES.md 1). The "
    "defined spellings that ARE "
    "free are `memcpy(&v, r, 4)` and the union: on clang both are BYTE-IDENTICAL "
    "to c/kernel.c and on gcc one instruction from it. Neither is the shipped "
    "R1h, because neither is a spelling any Rust rung can write, and a C rung "
    "spelling the length read a way no Rust rung can would put a codegen "
    "difference into p38's safety column; they ship as the controls `c_memcpy` "
    "and `c_union`. Every other check in this gate "
    "is blind to that difference: both cells agree with model.py on every "
    "non-adversarial input, both are ASan- and UBSan-clean in the gate's own "
    "-O1 sanitizer build, and Miri never sees a C rung at all. THE PIN IS "
    "THEREFORE THE ONLY THING IN THIS TREE THAT RECORDS WHICH C RUNG HAS THE "
    "BUG. "
    "WHY THE CLAMP IS `required` IN BOTH C RUNGS AND NOT ABSENT FROM ONE: p38 "
    "is not a pattern with a missing bounds check -- ten of the twenty patterns "
    "here already are. The check is WRITTEN in c/kernel.c, character for "
    "character as in c/kernel_hardened.c, and the type rule licenses the "
    "compiler to ignore it. A `required` entry that scoped the clamp to the "
    "hardened rung only would have described a different pattern. "
    "WHY THE ACCESSOR PAIR IS SPLIT INTO A GETTER AND A SETTER, AND WHY THE "
    "GETTER IS CALLED TWICE: the clamp writes through `uint16_t` lvalues and "
    "the re-read loads through a `uint32_t` lvalue, and a compiler is entitled "
    "to answer the second call from the value the first returned. Fold the two "
    "calls into one local and the question cannot be asked; that variant is "
    "shipped as the control `c_once` in controls/gen_controls.py and it is "
    "measured, not asserted. "
    "WHY `rlen` COUNTS 32-BIT UNITS: every record header then sits at an even "
    "word index, so the punning load is ALIGNED. Misalignment is a second, "
    "different undefined behaviour, and UBSan's `alignment` check would "
    "otherwise take credit for catching p38's bug when it cannot see it at all "
    "(../NOTES.md 6). "
    "WHY THE DECODE LOOP IS WORD-AT-A-TIME AND NOT `memcpy`/`copy_from_slice`: "
    "a bulk copy in the C rungs against an indexed loop in the Rust rungs would "
    "put p12's lost-bulk-lowering finding inside p38's cost column. All eight "
    "rungs read two bytes and combine them with `+` and `*`. "
    "WHAT IS DELIBERATELY NOT PINNED is how the scratch and the window are "
    "ADDRESSED -- R2 indexes, R3 reslices once per record, R4 and R5 use "
    "`get_unchecked` -- because that is the SAFETY axis and it is the axis the "
    "R3-side span is measured along (../NOTES.md 8). "
    "WHY `read_unaligned` IS FORBIDDEN IN THE RUST RUNGS: it is the DIRECT "
    "analogue of the C pun and it is DEFINED in Rust, which is p38's headline "
    "-- but ../spec.md pins `identity: unsafe == verus, O3 exact`, and at the "
    "pinned vstd `as_ptr`, `add` and `read_unaligned` are each `is not "
    "supported`, so a rung that spelled it would have no verifying twin and "
    "would not be a rung (`.memory/01-ladder.md` finding 14). It ships as the "
    "control `r4_pun`, measured and run through Verus, and ../NOTES.md 8 "
    "records both numbers. "
)

# --------------------------------------------------------------- the pins ----
IDIOM_REQUIRED = [
    {
        "c": "THE PUN, and the whole of what c/kernel.c does differently: "
             "`return *(const uint32_t *)r;` in `rec_len`. The object is an "
             "array of `uint16_t` and the lvalue has type `uint32_t`; neither "
             "is a character type, so C99 6.5p7 does not permit the access. "
             "c/kernel_hardened.c writes the two-half spelling instead and is "
             "otherwise character-identical, so the scoped-absent audit pair "
             "this entry reports is on that rung and is correct.",
        "rust": "There is no Rust analogue of this entry and that is p38's "
                "result, so the entry pins the Rust rungs to the ABSENCE of "
                "the only spelling that could be one -- read_unaligned "
                "appears in no rung and is forbidden below.",
    },
    {
        "c": "THE DEFINED READ, present in c/kernel_hardened.c and ABSENT from "
             "c/kernel.c: `return (uint32_t)r[0] + 65536 * (uint32_t)r[1];`. "
             "It reads the two 16-bit halves the wire format is defined in "
             "terms of and combines them, and it needs no build flag. It is "
             "NOT free -- see the why key -- and it is here rather than the "
             "free memcpy spelling because it is the one every Rust rung is "
             "forced into, so R1h stays idiom-matched to R2..R5.",
        "rust": "THE DEFINED READ, in all four Rust rungs and spelled the way "
                "the language forces (`sc` is a `[u16; 256]`, so there is no "
                "cast to make): `65536 *` combines the two halves. It is the "
                "only spelling any Rust rung has, which is the pattern.",
    },
    {
        "c": "THE CLAMP, present in BOTH C rungs including the buggy one -- "
             "p38 models no MISSING check: `if (rec_len(&sc[i]) > room)`.",
        "rust": "the clamp, in all four Rust rungs, written through `u16` "
                "lvalues exactly as the C rungs write it: `> room`.",
    },
    {
        "c": "the WINDOW/SCRATCH GUARD, in both C rungs: "
             "`while (o < nrec && i + 2 <= nw) {`. Additive rather than "
             "subtraction-first on purpose: i is the one quantity a "
             "miscompiled clamp can push PAST nw, and the subtraction-first "
             "form would then underflow into a second, unbounded walk. The "
             "loop invariant i <= nw keeps the addition from overflowing in "
             "the verified rungs.",
        "rust": "the same guard in all four Rust rungs: "
                "`while o < nrec && i + 2 <= nw`.",
    },
    {
        "c": "the CURSOR ADVANCE is by a whole record including its length "
             "field, so a rung that walked overlapping or misaligned records "
             "cannot produce the same fold: `i = i + 2 + 2 * n;` in both C "
             "rungs.",
        "rust": "the cursor advance in all four Rust rungs: "
                "`i = i + 2 + 2 * n;`.",
    },
    {
        "c": "the PAYLOAD FOLD, spelled with the literal multiplier: "
             "`acc = acc * 31 + (uint64_t)sc[i + 2 + k];` in both C rungs.",
        "rust": "the payload fold in all four Rust rungs: "
                "`.wrapping_mul(31).wrapping_add(`.",
    },
    {
        "c": "the header and every word are decoded with + and * and never "
             "with | and <<, so the whole specification stays inside linear "
             "arithmetic (.memory/04-verus.md): `256 *` in both C rungs.",
        "rust": "the same decode in all four Rust rungs: `256 *`.",
    },
    "the number of records actually walked is folded LAST, so a rung that "
    "stopped at a different point cannot produce the same checksum: `o` "
    "appears in the return expression of all eight rungs.",
    "the declared record count is rejected before any record is read, so no "
    "rung can walk a header it has not validated: `nrec == 0` appears in all "
    "eight rungs.",
]

IDIOM_FORBIDDEN = [
    {"rust": "`read_unaligned`"},
    {"rust": "`transmute`"},
    {"rust": "`align_to`"},
    {"rust": "`from_le_bytes`"},
    {"c": "`union`"},
    {"c": "`memcpy`"},
    "`copy_from_slice`",
    "`chunks_exact`",
    "`black_box`",
    "`volatile`",
]

# --------------------------------------------------------------- the note ----
CONTRACT_NOTE = (
    "requires/ensures above are DERIVED by check.py from verus.rs's own clause "
    "text through verus.translate, and the copy here must equal the derivation "
    "exactly. They are evaluated in Python against the bindings model.py yields "
    "per call (buf/off/len/buf_len/result) plus the helper it supplies "
    "(rec_fold). p38's bindings are the READ-ONLY set p03, p06, p10, p11, p12, "
    "p14, p16, p17, p05, p07, p27 and p47 use: the kernel writes only its own "
    "local scratch, which nothing outside the call can observe. "
    "**THE `ensures` IS SATISFIED BY THE C RUNG'S SOURCE AND VIOLATED BY ITS "
    "OBJECT, AND THAT IS p38'S SUBJECT.** `rec_fold` denotes the value the "
    "kernel returns under the C abstract machine's rules; c/kernel.c computes "
    "exactly that, on paper. What gcc 13.3.0 at -O2/-O3 emits does not, because "
    "the type rule lets it answer the re-read from before the clamp. No clause "
    "here can exclude that: a strict-aliasing violation is a property of the C "
    "abstract machine, this specification is about a RUST program, and Rust has "
    "no type-based aliasing rule for the specification to be about. "
    "controls/proof_mutants.py ships two mutants that DO fail, both SPATIAL -- "
    "which is the honest statement of what R5 buys here (../NOTES.md 9). "
    "What the `ensures` deliberately does NOT say is that `nrec` or any record "
    "length is honest: a precondition about the contents of a file is one no "
    "honest loader can discharge (`.memory/02-bench-rules.md`), and the CLAMP "
    "inside `rwalk` is what stops the walk instead, so degenerate.bin and every "
    "adversarial row are INSIDE the verified domain and every RUST rung agrees "
    "with model.py on all of them."
)

OBLIGATIONS_NOTE = (
    "13 = SCRATCH_W 1 + wfold 1 + rwalk 1 + kernel 5 + main 5, each term "
    "MEASURED with `./verus_run.py verus.rs --verify-function <name> "
    "--verify-root` and not predicted. The zero terms are checkable the same "
    "way: u32_at, nw_of, dec and rec_fold are NON-RECURSIVE spec fns and report "
    "0, while wfold and rwalk are RECURSIVE and carry one termination query "
    "each; buf_get_unchecked, sc_get_unchecked, sc_set_unchecked, load_input "
    "and emit are external_body and report 0. The `const` carries one query "
    "(`.memory/04-verus.md`: a `const` inside verus! is its own obligation). "
    "kernel's 5 = body + THREE loop bodies (the decode loop, the record walk "
    "and the payload fold) + the one `assert ... by (nonlinear_arith)`, which "
    "is its own query. main's term is 5, which is what every other pattern in "
    "this tree that records the term also records for the byte-identical "
    "driver loop."
)

TWIN_NOTE = (
    "The obligation count in the OTHER configuration -- `verus.rs --cfg "
    "slb_twin`, which is where step 5c-twin checks the twins. 13 shipped + 3, "
    "the three trusted items inside the twin regime being "
    "slb_twin_buf_get_unchecked, slb_twin_sc_get_unchecked and "
    "slb_twin_sc_set_unchecked. `load_input` and `emit` are outside the regime "
    "(external_body with no `ensures` and no `unsafe` body) and have no twins."
)

COLLAPSE_NOTE = (
    "work_per_call is `stride` -- WINDOW BYTES, the denomination p16, p05, p11, "
    "p12, p06, p14, p27 and p10 use -- and it is strict here for a reason that "
    "is structural rather than lucky: p38's kernel touches every window byte "
    "from data_start ONCE in the decode loop before it walks a single record, "
    "so the count cannot exceed the bytes read. It undercounts by the 4 header "
    "bytes and by every payload word the fold reads a second time. The two "
    "probe inputs differ in work_per_call (200 vs 516) precisely so check.py's "
    "d(Ir)/d(work) assertion has two shapes and can run at all; `large.bin`'s "
    "stride is chosen so that nw is EXACTLY SCRATCH_W, which puts the "
    "truncation branch on its boundary rather than leaving it untested. "
    "model.py declares no min_ir_per_work, so the harness default of 0.25 "
    "applies unchanged; ../NOTES.md 3 has the per-cell margins."
)

IDENTITY_WHY = (
    "R4 == R5: the proof licenses unsafe code at zero cost. On p38 the pin "
    "carries a second job -- it is what makes *the R4 rung is immune* a "
    "statement about a BINARY. `.memory/06-catalogue.md` hazard 2 is that a "
    "text pin binds the source and not the object, and p38 is the pattern where "
    "that hazard is the whole subject: the C rung's source is correct and its "
    "object is not. R5's object is R4's object byte for byte, and R4's object "
    "is disassembled in ../NOTES.md 1. At O0 the crate names differ in length "
    "so call displacements differ, which is link layout and not codegen, hence "
    "`norel` there and `exact` at O3."
)

MIRI_REASON = (
    "R4 and R5 ARE byte-identical at O3. Since TASK_010 "
    "`.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a "
    "trusted item, which check.py DERIVES from verus.rs rather than reading "
    "from this flag. **On p38 Miri is expected to be, and is, entirely silent "
    "about the pattern's bug** -- it checks the unchecked reads and the "
    "unchecked store, which are the things the Rust rungs get right, and it "
    "never sees a C rung. It is listed here because the three contract-bearing "
    "trusted items are real and a wrong `sc_set_unchecked` would still be "
    "invisible to Verus. ../NOTES.md 7 says so. ⚠ Miri is ALSO the instrument "
    "that would catch the Rust analogue of p38's bug if Rust had one: "
    "controls/gen_controls.py's `r4_pun` reads a u32 out of the u16 scratch "
    "with `read_unaligned` and Miri reports NOTHING, because there is nothing "
    "to report."
)

UNSAFE_JUSTIFICATIONS = {
  "verus.rs": {
    "sc_set_unchecked": (
        "`x` is a pure VALUE parameter -- written into the scratch, never used "
        "as an address or a length -- so it needs no precondition. This is the "
        "false positive of the parameter-coverage rule that "
        "`.memory/04-verus.md` names and that p03 was the first pattern to "
        "exercise; p38 is the second."
    ),
  },
}


def contract():
    why = WHY_HEAD + donor_paragraph()
    return {
        "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
        "model": "model.py",
        "requires": ["off + len <= buf_len"],
        "ensures": ["result == rec_fold(buf, off, len)"],
        "note": CONTRACT_NOTE,
        "idiom": {
            "required": IDIOM_REQUIRED,
            "forbidden": IDIOM_FORBIDDEN,
            "why": why,
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
            "obligations": {"verus.rs": 13},
            "twin_obligations": {"verus.rs": 16},
            "obligations_note": OBLIGATIONS_NOTE,
            "twin_obligations_note": TWIN_NOTE,
            "unsafe_justifications": UNSAFE_JUSTIFICATIONS,
            "items": {
                "verus.rs": {
                    "u32_at": {"external": None, "requires": [], "ensures": []},
                    "nw_of": {"external": None, "requires": [], "ensures": []},
                    "dec": {"external": None, "requires": [], "ensures": []},
                    "wfold": {"external": None, "requires": [], "ensures": []},
                    "rwalk": {"external": None, "requires": [], "ensures": []},
                    "rec_fold": {"external": None, "requires": [], "ensures": []},
                    "buf_get_unchecked": {
                        "external": "verifier::external_body",
                        "requires": ["i < v@.len()"],
                        "ensures": ["r == v@[i as int]"],
                    },
                    "slb_twin_buf_get_unchecked": {
                        "external": None,
                        "requires": ["i < v@.len()"],
                        "ensures": ["r == v@[i as int]"],
                    },
                    "sc_get_unchecked": {
                        "external": "verifier::external_body",
                        "requires": ["i < v@.len()"],
                        "ensures": ["r == v@[i as int]"],
                    },
                    "slb_twin_sc_get_unchecked": {
                        "external": None,
                        "requires": ["i < v@.len()"],
                        "ensures": ["r == v@[i as int]"],
                    },
                    "sc_set_unchecked": {
                        "external": "verifier::external_body",
                        "requires": ["i < old(v)@.len()"],
                        "ensures": ["final(v)@ == old(v)@.update(i as int, x)"],
                    },
                    "slb_twin_sc_set_unchecked": {
                        "external": None,
                        "requires": ["i < old(v)@.len()"],
                        "ensures": ["final(v)@ == old(v)@.update(i as int, x)"],
                    },
                    "load_input": {"external": "verifier::external_body",
                                   "requires": [], "ensures": []},
                    "emit": {"external": "verifier::external_body",
                             "requires": [], "ensures": []},
                    "kernel": {
                        "external": None,
                        "requires": ["off + len <= buf@.len()"],
                        "ensures": ["r == rec_fold(buf@, off as int, len as int)"],
                    },
                    "main": {"external": None, "requires": [], "ensures": []},
                }
            },
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
        "identity": [{"a": "unsafe", "b": "verus", "O0": "norel",
                      "O3": "exact", "why": IDENTITY_WHY}],
        "miri": {
            "pair": ["unsafe", "verus"],
            "sources": ["unsafe.rs"],
            "required": True,
            "reason": MIRI_REASON,
            "blocked_reason": "miri is installed on the nightly toolchain "
                              "beside the pinned one (TOOLCHAIN.md). If it is "
                              "missing, this row is blocked rather than failed.",
        },
    }


PROSE = r"""# p38 — strict aliasing / type punning: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

⚠ **This file is GENERATED by `controls/mkcontract.py`. Edit the generator and
re-run it** — three tasks in a row shipped a `spec.md` edit a generator would
have silently reverted (`.memory/05-layout.md`). The generator reads the shared
named-spelling paragraph out of a DONOR pattern's `spec.md` and refuses to write
anything if the result does not satisfy `harness/check.py::named_spelling_problem`.

## What makes p38 different from the other nineteen

**Every other pattern here has the shape *C has the bug, safe Rust rejects it,
R4 gets it back*. p38 is the first bug class that unsafe Rust does not
reintroduce.**

| | every other pattern | p38 |
|---|---|---|
| what `c/kernel.c` omits | a bounds check | **nothing — the clamp is written, in full** |
| why it is wrong anyway | the check is absent | **the compiler is entitled to ignore it** |
| R2 is safe because | a bounds check panics | **the language has no type-aliasing rule** |
| R4 gets the bug back | yes, 15 patterns of 19 | **no — there is nothing to get back** |
| R5's `ensures` excludes it | usually | **no, and it cannot be strengthened to** |
| which compilers exhibit it | both | **gcc 13.3.0 only, and the reason is mechanical** |

Rust's `&mut` carries `noalias`, which is *uniqueness* — a provenance property,
not a type one. There is no rule anywhere in Rust that lets an optimiser assume
a `u32` access and a `u16` access do not overlap. `ptr::read_unaligned::<u32>`
on a `*const u16` is defined and returns the bytes that are there; measured at
`-C opt-level=3` in `controls/gen_controls.py`'s `r4_pun`.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, carrying the same information: `&[u8]`
is a pointer and a length and C spells the pair out. C is handed the blob length
and *both* C rungs ignore it — p47's, p06's, p10's, p12's, p14's and p27's shape.
(The arity mismatch is why `spec.md` carries a `driver.call_args` pin.)

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..4     nrec   u32 LE    DECLARED record count           ATTACKER DATA
byte 4..      the record stream, as little-endian 16-bit words
data_start = 4
SCRATCH_W  = 256 words          the decode scratch, in every rung

record at scratch word index i:
  words i, i+1   rlen, a u32 stored as two 16-bit halves, low half first
  words i+2 ..   2*rlen payload words      (`rlen` counts 32-bit units)
```

`rlen` counts **32-bit units**, so `i` is always even and the punning load is
**aligned**. That is load-bearing: misalignment is a *second* undefined
behaviour, and UBSan's `alignment` check would otherwise appear to catch p38's
bug while being blind to the aliasing violation it is actually about.

## Semantics

```
if len < 4:                                   return 0
nrec from the header
if nrec == 0:                                 return 0

nw = min((len - 4) / 2, SCRATCH_W)
sc[j] = LE16(window[4 + 2j])  for j in 0..nw          # THE DECODE LOOP

acc = 0 ; i = 0 ; o = 0
while o < nrec and i + 2 <= nw:                       # THE GUARD, every rung
    room = (nw - i - 2) / 2
    if REC_LEN(sc+i) > room:  REC_SET_LEN(sc+i, room) # THE CLAMP, every rung
    n = REC_LEN(sc+i)                                 # THE RE-READ
    for k in 0 .. 2*n:  acc = acc *64 31 +64 sc[i+2+k]
    i += 2 + 2*n
    o += 1
return acc *64 31 +64 o
```

`*64` and `+64` are wrapping `u64` operations.

Load-bearing, do not "improve":

- **`REC_LEN` is called twice and the second call is the one the pattern is
  about.** Fold them into one local and the question p38 asks cannot be asked;
  `controls/gen_controls.py` ships that variant as `c_once` and measures it.
- **The clamp is in every rung, R1 included.** p38 models no *missing* check.
- **The guard is additive (`i + 2 <= nw`) and not subtraction-first.** `i` is the
  one quantity a miscompiled clamp can push past `nw`, and `nw - i >= 2` would
  then underflow into a second, unbounded walk — which would make the
  adversarial rows non-terminating rather than merely wrong. The verified rungs
  carry `i <= nw` as a loop invariant, so `i + 2` cannot overflow.
- **The fold folds payload words and never a length field**, so a record whose
  length the clamp rewrote still produces the same checksum in every rung that
  observes the clamp.

## The bug

`c/kernel.c` writes

```c
static uint32_t rec_len(const uint16_t *r)
{
    return *(const uint32_t *)r;
}
```

and `c/kernel_hardened.c` writes

```c
static uint32_t rec_len(const uint16_t *r)
{
    return (uint32_t)r[0] + 65536 * (uint32_t)r[1];
}
```

⚠ **The two are not the same machine code, and the difference is not what the
task predicted.** The defined spelling costs **+6 static instructions on gcc and
+10 on clang, by two different routes**: clang (and rustc) merge the two 16-bit
loads back into one 32-bit load and then fail to simplify
`(x & 0xffff) + 65536*(x >> 16)` back to `x`, while gcc does not merge at all
and pays for two `movzwl` plus a shift and an add. **rustc pays clang's 10 in
every Rust rung.** The defined spellings that *are* free —
`memcpy(&v, r, 4)` and the union — are **byte-identical to the UB spelling on
clang** (`md5_fn 366e3be50428933dee85aae05655e7ff`) and one instruction from it
on gcc. So *"the UB buys literally nothing"* is true against the right defined
spelling and false against the one the named-spelling standard forces on every
rung. `NOTES.md` 1 has both listings; the free spellings ship as `c_memcpy` and
`c_union` because no Rust rung can write either.

CWE-843 (access of resource using incompatible type), reaching CWE-125
(out-of-bounds read). The object is an array of `uint16_t`; the lvalue has type
`uint32_t`; neither is a character type; C99 6.5p7 does not permit the access.
The clamp stores through `uint16_t` lvalues, the re-read loads through a
`uint32_t` lvalue, and under the type rule the load need not observe the stores.

**Measured on the shipped binary, not in a probe** (`NOTES.md` 2):

| build | `adversarial-oob.bin` |
|---|---|
| `c-gcc` `-O3`, both inline modes | **the clamp has no effect; the fold reads past `sc`** |
| `c-clang` `-O3`, both inline modes | clamped; no out-of-bounds read |
| either compiler at `-O0`, or `-fno-strict-aliasing` | clamped |
| every Rust rung, every cell | clamped |

### ⚠ The catalogue's stated spelling is OVERTURNED, with the measurement

`.memory/06-catalogue.md` describes p38 as *"endian conversion / type punning
(`memcpy` vs union)"* — reading a `uint32_t` out of an `unsigned char` array.
That is UB by 6.5p7 and **neither compiler exploits it**: 16 of 16 cells
(gcc/clang × `-O0..-O3` × `±-fstrict-aliasing`) return the defined answer,
because a character-typed access may alias anything and the compilers key their
TBAA on the *access* type. A pattern built on that spelling would return a null
result for the wrong reason. p38 is built on the weaponised direction — two
incompatible **non-character** types — and `NOTES.md` 0 has the 16-cell table.
That is the fifth catalogue row this project has overturned.

### ⚠ And the compiler difference has a mechanism, not a version number

clang declines this violation and gcc takes it, from identical source. The
discriminator is **not** the optimisation level and **not** the LLVM version: it
is that LLVM does not apply TBAA when BasicAA has already proved the two
accesses are the *same address*, which is exactly what a single-base accessor
pair creates. Hand clang two pointers it cannot relate — same address at run
time, two parameters — and it exploits the identical violation from `-O1`
upward. `NOTES.md` 0d ships that control. **So "clang is safe here" is false;
"clang's alias analysis answers this particular query before TBAA is consulted"
is true.**

## The adversarial rows, and what one means when the harm is a miscompilation

**A miscompilation has no crash on the rung that is right and no wrong answer on
the rung that is wrong *in source*.** What p38 records is a *ladder of harms*,
all from one attacker field:

| input | declared `rlen` | what it reaches | what sees it |
|---|---|---|---|
| `adversarial-stale` | 60 units | scratch words the decode loop never wrote — **inside** the array | nothing: ASan and UBSan are clean |
| `adversarial-oob` | 200 units | **past the array**, into the frame | ASan `stack-buffer-overflow READ`; UBSan `array-bounds` |
| `adversarial-huge` | 0xFFFFFFF units | off the stack entirely | SIGSEGV |
| `adversarial-nrec` | well formed | the `i + 2 <= nw` guard, with `nrec` saturated | nothing — every rung agrees |
| `adversarial-stride7` | — | the driver's `stride_w >= 8` guard | every rung prints 0 |

`adversarial-stale` is p17's shape: the read stays *inside* the allocation, so
every instrument is silent and the answer is merely wrong. `adversarial-oob` is
the one that leaves it. **Neither is reproducible across runs** — the disclosed
words are stack residue under ASLR — which is p03's pointer-disclosure shape and
is recorded per rung in `NOTES.md` 5 rather than checksummed.

⚠ **The gate's own sanitizer stage cannot see any of this**, and `model.py`
declares `sanitizer_expect: "clean"` on every input because of it:
`harness/check.py` stage 7 builds the C rung at **`-O1`**, and gcc enables
`-fstrict-aliasing` at `-O2` and above. The same source at `-O3` under ASan
reports the overflow; `controls/gen_controls.py` ships that build as `s_asan_O3`.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == rec_fold(buf, off, len)
```

`rec_fold` is the spec function; `model.py` is its independent Python twin — and
independent in the way that matters here: **`model.py`'s simulation slices
`bytes` and clamps with an `int.from_bytes` comparison, and its helper
`rec_fold` builds a word list and mirrors the Verus spec functions term for
term, including the clamp as a *sequence update*.** The gate checks the two
against each other on every call of every input.

The `requires` is **structural** — about the shape of the buffer the driver
built, not about its contents — so it holds on every input this benchmark runs,
`adversarial-*` included. It is **ONE clause**, as on p03, p06, p10, p11, p12,
p14, p27 and p47 and unlike p17.

### ⚠ What the `ensures` cannot say, and why that is the deliverable

The `ensures` is satisfied by `c/kernel.c`'s **source** and violated by its
**object**, and no strengthening repairs that:

- `rec_fold` denotes the value the kernel returns under the abstract machine's
  rules. `c/kernel.c` computes exactly that, on paper.
- The violation is a property of **C's** type rule. This specification is about
  a **Rust** program, and Rust has no type-based aliasing rule for it to be
  about. The obligation does not fail to discharge; **it does not exist**.
- This is p47's shape one axis over, with a different cause. p47's property is
  *inexpressible* (there is no term for a trace). p38's is *vacuous in the
  language the proof is about*.

`controls/proof_mutants.py` ships two mutants that **do** fail, both spatial.
See `NOTES.md` 9 for the full statement of what is and is not proved.

## The trusted base

**Five** `external_body` items, **three** of them with contracts:
`buf_get_unchecked`, `sc_get_unchecked`, `sc_set_unchecked` (all three twinned),
plus `load_input` and `emit` (infra, in every pattern here). The classification
is **3 U-license + 2 infra + 0 V-gap** — p03's shape, and for p03's structural
reason: p38's kernel has *two* buffers and one of them is written.

⚠ **`sc_set_unchecked`'s `ensures` is where the language difference lives.** It
says the store lands and nothing else moves. The corresponding C expression is
`r[0] = (uint16_t)(v % 65536)`, and in C a later read of the same storage
through a `uint32_t` lvalue need not observe it. That the Rust one is observed
is not an axiom about the wrapper — it is Rust's memory model, which has no rule
for the axiom to be wrong about.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p38's payload is p47's, p10's, p27's and eight
others':

```
word 0     u64  stride      # bytes per window; the kernel walks one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes`, reused verbatim,
with **nothing added to `common/` for p38**.

## Driver loop

Identical in all eight rungs, between the `SLB-DRIVER-BEGIN` /
`SLB-DRIVER-END` markers, and byte-for-byte p47's and p10's.
`harness/check.py` normalises every copy — the C one included — and diffs it
against `driver.canonical` in the block below.

```
n_blob := bytes.len()
buf    := bytes
acc    := 0
if stride_w >= 8 and stride_w <= n_blob:
    stride := stride_w as usize
    nwin   := (n_blob / stride) as u64
    it     := 0
    while it < n_iters:
        k   := ((acc as u128 * nwin as u128) >> 64) as usize
        r   := kernel(buf, k * stride, stride)
        acc := acc *64 31 +64 r
        it  := it + 1
emit(acc)
```

`stride_w >= 8` because p38's window is a 4-byte header plus at least one 4-byte
record length field. `adversarial-stride7.bin` attacks it.

`k` is derived from `acc`, and `acc` from the previous call's result, so call
*i+1* cannot begin until call *i* has returned. Nothing to CSE, nothing to
hoist, no `black_box` and no `asm volatile`.

**Every sweep blob is window-homogeneous** except the `sweep-h*` band, which is
deliberately heterogeneous so that a blob's regressor row is not a scalar
multiple of any other band's. `inputs/gen.py` checks that window 0 returns
non-zero, for `.memory/01-ladder.md`'s absorbing-state reason.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. p01's `spec.md` explains what each pin closes;
what is worth saying here is the arithmetic behind the two obligation counts.

| pin | why |
|---|---|
| `verus.obligations` = 13 | **`SCRATCH_W` 1 + `wfold` 1 + `rwalk` 1 + `kernel` 5 + `main` 5 = 13**, every term measured with `--verify-function <name> --verify-root`. `u32_at`, `nw_of`, `dec` and `rec_fold` are non-recursive spec fns and report 0; `wfold` and `rwalk` are recursive and carry one termination query each; the five `external_body` items report 0. `kernel`'s 5 is 1 body + 1 per loop body (**three** loops: decode, record walk, payload fold) + the one `by (nonlinear_arith)` assertion, which is its own query. |
| `verus.twin_obligations` = 16 | the count under `--cfg slb_twin`. **13 shipped + 3**, the three trusted items inside the twin regime. |
| `identity` `O3: exact`, `O0: norel` | and on p38 it carries a second job: it is what makes *"the unsafe rung is immune"* a statement about a **binary** rather than about a source file. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`. **Miri is expected to be, and is, entirely silent about p38's bug** — including on the `r4_pun` control, where it has nothing to report because there is nothing to report. |
| `forbidden: read_unaligned` (rust) | the direct analogue of the C pun, **defined in Rust**, and inadmissible as a rung only because the pinned vstd cannot express it. Shipped as the control `r4_pun`. |
| `forbidden: memcpy` (c) | two reasons, and both are measured. A bulk decode in C against an indexed decode in Rust would put p12's lost-bulk-lowering finding inside p38's cost column; and `memcpy(&v, r, 4)` is the *free* defined spelling of the length read, byte-identical to the UB one on clang, which no Rust rung can write. It ships as the control `c_memcpy`. |
| `forbidden: union` (c) | the other *legal* C spelling of type punning, and also free. Using it in a rung would make R1 defined and delete the pattern; it is measured as the control `c_union` instead. |
"""


def render():
    return PROSE + "\n```slb-contract\n" + \
        json.dumps(contract(), indent=2, ensure_ascii=False) + "\n```\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="do not write; report whether spec.md is up to date")
    a = ap.parse_args()

    c = contract()
    probs = checkmod.idiom_problems({"idiom": c["idiom"]})
    if probs:
        raise SystemExit("mkcontract.py: idiom_problems: " + "; ".join(probs))
    ns = checkmod.named_spelling_problem(c)
    if ns:
        raise SystemExit("mkcontract.py: named_spelling_problem: " + ns)

    text = render()
    if a.check:
        cur = open(OUT).read() if os.path.exists(OUT) else ""
        if cur == text:
            print("spec.md is up to date")
            return 0
        print("spec.md DIFFERS from what this generator would write")
        return 1
    open(OUT, "w").write(text)
    print(f"wrote {OUT} ({len(text)} bytes); idiom ok, named-spelling paragraph "
          f"{len(donor_paragraph())} bytes from {os.path.relpath(DONOR, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
