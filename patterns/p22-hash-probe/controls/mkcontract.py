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

    python3 patterns/p22-hash-probe/controls/mkcontract.py           # write
    python3 patterns/p22-hash-probe/controls/mkcontract.py --check   # diff only
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
DONOR = os.path.join(REPO, "patterns", "p38-alias-pun", "spec.md")
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
    "ON p22 THE PINNED SPELLING IS A CONJUNCT THAT NO LANGUAGE SUPPLIES. "
    "`nfill < TABCAP` is not a bounds check and no compiler, checker or "
    "sanitizer emits it: every table access in every rung is `tab[i]` with `i` "
    "reduced modulo TABCAP, so the accesses are in bounds in the BUGGY rung "
    "too. What the conjunct buys is TERMINATION, and safety in the Rust sense "
    "says nothing about that. Measured (../NOTES.md 0): the safe-Rust rung with "
    "the conjunct deleted hangs at -O0 and at -O3 with Miri silent, and "
    "c/kernel.c hangs under gcc and clang at both levels with ASan+UBSan "
    "silent. THAT IS WHY THE ENTRY IS SCOPED TO ALL EIGHT RUNGS RATHER THAN TO "
    "THE HARDENED C ONE: on ten other patterns here the buggy rung omits a "
    "check its language would have supplied, and pinning it in the safe rungs "
    "would be pinning something they cannot avoid. Here every rung writes it by "
    "hand or hangs. "
    "WHY THE PROBE LOOP IS UNBOUNDED IN ALL EIGHT RUNGS -- ⚠ **TWO REASONS, "
    "BECAUSE ONE OF THEM IS FALSE OF HALF OF WHAT IS EXCLUDED** "
    "(TASK_070_REVIEW F3, which measured it; until then this paragraph gave "
    "only reason (1) and gave it for both). "
    "(1) THE BOUND WRITTEN *INSTEAD OF* THE CONJUNCT IS A DIFFERENT FUNCTION. "
    "A bounded trip count also makes the loop terminate and it is idiomatic "
    "safe Rust, but put in place of `nfill < TABCAP` it finds a key that is "
    "present in a full table, where the shipped semantics rejects every "
    "operation once the table is full and folds SENT. That is measured and not "
    "asserted: the control `r3_bounded` prints `8190810770250110748` on "
    "adversarial-full.bin against the shipped `8190810770250117165`, and "
    "agrees on the other seven matrix inputs. Shipping it in one rung would "
    "put a semantic difference inside p22's safety column. "
    "(2) THE BOUND WRITTEN *IN ADDITION TO* THE CONJUNCT IS THE SAME FUNCTION, "
    "AND IS EXCLUDED ON DIFFERENT GROUND. The control `r3_bounded_kept` agrees "
    "with the shipped R3 on ALL EIGHT matrix inputs, so calling it a different "
    "function is false. What excludes it is the PROBE-LOOP `required` entry -- "
    "`required[2]` in the gate record -- and its *no "
    "trip count anywhere* -- and the ground is the same one that forbids "
    "`probes < TABCAP` two sentences below: a trip count in the OBJECT CODE is "
    "the fix wearing the proof's clothes. p22 IS an unbounded probe loop whose "
    "termination follows from a global invariant; a bounded one is a different "
    "pattern. The two spellings are the same edit on opposite sides of the "
    "safety axis, so admitting it in R3 while forbidding it in R5 would be "
    "incoherent, and admitting it in R5 would let the `decreases` be "
    "discharged from the trip count and delete the pattern's result. "
    "⚠ **THE PRICE OF EXCLUSION (2) IS PUBLISHED RATHER THAN HIDDEN.** The "
    "in-contract R3 span is 4401.6100 ... 4411.6100, width 10.00; admitting "
    "`r3_bounded_kept` would take it to 4401.6100 ... 4569.2600 -- width "
    "167.65 on small and 1235.96 on large, 16.8x wider. ⚠ **The direction does "
    "NOT flatter**: `r3_bounded_kept` is DEARER, so `R3ship` remains the "
    "cheapest in-contract R3 found and `R3 - R4 = +2.00` is unaffected. A "
    "16.8x span movement reads like a retraction and is not one. "
    "⚠ **AND NO GREP SETTLES (2).** The two backticked entries below, `for _ "
    "in 0..TABCAP` and `(0..TABCAP)`, exclude the two ITERATOR spellings "
    "literally -- they are the ones measured in `.temp/p22/probe/probe_rs.rs` "
    "-- but `r3_bounded_kept` writes `while n < TABCAP` with its own counter "
    "and matches NEITHER. It is out of contract by the English of "
    "`required[2]` and by nothing a token test decides, which is the same "
    "class as "
    "the polarity and rung-scope readings the shared paragraph below already "
    "records under WHAT NO GREP SETTLES. Both controls are measured "
    "(../NOTES.md 8b), and what they price is exactly *what the proof buys "
    "over the bound*. "
    "WHY `probes < TABCAP` IS FORBIDDEN: an exec-side probe counter is the "
    "other way to satisfy Verus's `decreases`, and it is the one that would "
    "make the proof CIRCULAR WITH THE FIX -- the loop would be bounded in the "
    "object code and the termination measure would be proving something the "
    "loop no longer needed proved. verus.rs carries a GHOST unwrapped cursor "
    "and a GHOST witness for an EMPTY slot instead, so R4 and R5 stay "
    "byte-identical at O3 and the exec code gains nothing. "
    "WHY `#[verifier::exec_allows_no_decreases_clause]` IS FORBIDDEN: it is "
    "Verus's own opt-out from the termination obligation, printed in the error "
    "text when the clause is missing, and it is the one edit that would let R5 "
    "ship p22's bug. Forbidding it is what makes *only R5 catches it* a "
    "statement about this tree rather than about Verus's defaults. "
    "WHY THE HASH IS SPELLED `* 2654435761 / 16777216 % TABCAP` AND NEVER "
    "`* 2654435761 >> 24 & 63`: the two are the same function on unsigned "
    "values and lower to the same instructions, but only the first is linear "
    "arithmetic, so verus.rs carries no `by (bit_vector)` anywhere "
    "(.memory/04-verus.md). The same reason puts `256 *` in the header decode "
    "rather than `<< 8`. "
    "WHY THE TABLE IS A FIXED-CAPACITY ARRAY AND `HashMap` IS FORBIDDEN: p22 is "
    "about the probe loop, and a library hash table would move the whole "
    "question inside std -- where the load-factor invariant is maintained by "
    "code no rung wrote and no rung can omit. "
    "WHAT IS DELIBERATELY NOT PINNED is how the WINDOW and the TABLE are "
    "ADDRESSED -- R2 indexes both, R3 reslices the window once and iterates the "
    "keys, R4 and R5 use `get_unchecked` on both -- because that is the SAFETY "
    "axis and it is the axis the R3-side span is measured along (../NOTES.md "
    "8). It is also why the insert, the EMPTY test and the probe loop's own "
    "condition are described in prose in the entries below rather than "
    "backticked on the Rust side: those three spellings are exactly where the "
    "safety axis lives, and a backtick there would pin the axis flat. "
)

# --------------------------------------------------------------- the pins ----
IDIOM_REQUIRED = [
    {
        "c": "THE SAFETY LINE, and the only thing c/kernel.c omits: the "
             "capacity conjunct, `if (k != SLB_P22_EMPTY && nfill < "
             "SLB_P22_TABCAP) {` in c/kernel_hardened.c. c/kernel.c writes "
             "`if (k != SLB_P22_EMPTY) {` there and is otherwise "
             "character-identical, so the scoped-absent audit pair this entry "
             "reports is on that rung and is correct.",
        "rust": "THE SAFETY LINE, present in ALL FOUR Rust rungs and written "
                "by hand in every one of them: `if k != EMPTY && nfill < "
                "TABCAP {`. Unlike every other pattern in this tree, no Rust "
                "rung gets this from the language -- see the why key.",
    },
    {
        "c": "THE PROBE STEP, in both C rungs, and the reason the probe cursor "
             "cannot leave the table: `i = (i + 1) % SLB_P22_TABCAP;`.",
        "rust": "THE PROBE STEP, in all four Rust rungs: "
                "`i = (i + 1) % TABCAP;`.",
    },
    {
        "c": "THE PROBE LOOP, and it is UNBOUNDED in both C rungs -- the "
             "hardened rung does not add a trip count, it adds the capacity "
             "conjunct above: `while (tab[i] != SLB_P22_EMPTY && tab[i] != k)`.",
        "rust": "The probe loop is unbounded in all four Rust rungs too, and "
                "its condition is the one place the SAFETY AXIS shows: the safe "
                "rungs index the table and the unsafe rungs read it through "
                "arr_get_unchecked, so this entry pins the property in prose "
                "and pins the STEP, in backticks, in the entry above. What all "
                "four spell is a test of the slot against EMPTY and against the "
                "key, WITH NO TRIP COUNT ANYWHERE. ⚠ It is this clause, in "
                "prose, that excludes a bounded probe -- not the two backticked "
                "entries in the forbidden list, which exclude the two ITERATOR "
                "spellings literally and match no hand-rolled counter at all: "
                "the control r3_bounded_kept writes a while loop against its "
                "own counter and matches neither of them. TASK_070_REVIEW F3; "
                "the why key gives the two separate reasons and prices what "
                "the exclusion costs. ⚠ NOTHING IN THIS SENTENCE IS "
                "BACKTICKED, deliberately: a backtick in a required entry PINS "
                "A SPELLING, and an earlier draft of this correction "
                "accidentally added three spellings no rung writes -- the same "
                "defect the take(nkey) entry below records and the gate "
                "reported it the same way, as required_pins_nothing.",
    },
    {
        "c": "THE HASH, in both C rungs, spelled with / and % and never with "
             ">> and &: `* 2654435761u / 16777216u % SLB_P22_TABCAP`.",
        "rust": "THE HASH, in all four Rust rungs: "
                "`* 2654435761 / 16777216 % TABCAP`.",
    },
    {
        "c": "THE TABLE IS CLEARED at the start of every call, so a call's "
             "answer does not depend on the previous call's table: "
             "`tab[j] = SLB_P22_EMPTY;` in both C rungs.",
        "rust": "the same, in all four Rust rungs, written the way the language "
                "supplies it: `[EMPTY; TABCAP]`.",
    },
    {
        "c": "THE INSERT happens only into a slot the probe found EMPTY, so a "
             "key never overwrites a different key: `if (tab[i] == "
             "SLB_P22_EMPTY) {` in both C rungs, followed by `tab[i] = k;`.",
        "rust": "the same test and the same store in all four Rust rungs, "
                "spelled along the safety axis: an index in safe_naive.rs and "
                "safe_tuned.rs, arr_get_unchecked / arr_set_unchecked in "
                "unsafe.rs and verus.rs. Prose rather than a backtick for the "
                "reason the why key gives.",
    },
    {
        "c": "the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and the "
             "additive form's overflow never arises: `if (len - p < 1)` in both "
             "C rungs.",
        "rust": "the walk stops at the window in all four Rust rungs. "
                "safe_naive.rs, unsafe.rs and verus.rs write the same "
                "subtraction-first guard as C; safe_tuned.rs reaches the same "
                "set of keys with take(nkey) over a reslice, which is the "
                "R3-side lever and is exactly what this entry declines to pin. "
                "Prose, therefore, and not a backtick -- an earlier draft "
                "backticked take(nkey) here and the audit correctly reported it "
                "scoped-absent on the other three Rust rungs.",
    },
    {
        "c": "a rejected key folds the SENTINEL rather than being skipped, so "
             "the fold's length is a function of the key count alone: "
             "`acc = acc * 31 + SLB_P22_SENT;` in both C rungs.",
        "rust": "the sentinel fold, in all four Rust rungs: "
                "`.wrapping_add(SENT)`.",
    },
    {
        "c": "the fold is a serial Horner chain over `acc`, spelled with the "
             "literal multiplier: `acc = acc * 31 +` in both C rungs.",
        "rust": "the fold, in all four Rust rungs, spelled with the literal "
                "multiplier: `.wrapping_mul(31)`.",
    },
    {
        "c": "the header is decoded with + and * and never with | and <<, so "
             "the whole specification stays inside linear arithmetic "
             "(.memory/04-verus.md): `256 *` in both C rungs.",
        "rust": "the same decode in all four Rust rungs: `256 *`.",
    },
    "the declared key count is rejected before any key is read, so no rung can "
    "walk a header it has not validated: `nkey == 0` appears in all eight "
    "rungs.",
    "the number of slots filled is folded LAST, so a rung that inserted a "
    "different number of keys cannot produce the same checksum: `nfill` appears "
    "in the return expression of all eight rungs.",
]

IDIOM_FORBIDDEN = [
    {"rust": "`for _ in 0..TABCAP`"},
    {"rust": "`(0..TABCAP)`"},
    {"rust": "`probes < TABCAP`"},
    {"rust": "`#[verifier::exec_allows_no_decreases_clause]`"},
    {"rust": "`HashMap`"},
    {"rust": "`HashSet`"},
    {"c": "`probes < SLB_P22_TABCAP`"},
    "`>> 24`",
    "`& 63`",
    "`black_box`",
    "`volatile`",
]

# --------------------------------------------------------------- the note ----
CONTRACT_NOTE = (
    "requires/ensures above are DERIVED by check.py from verus.rs's own clause "
    "text through verus.translate, and the copy here must equal the derivation "
    "exactly. They are evaluated in Python against the bindings model.py yields "
    "per call (buf/off/len/buf_len/result) plus the helper it supplies "
    "(key_fold). p22's bindings are the READ-ONLY set p03, p06, p10, p11, p12, "
    "p14, p16, p17, p05, p07, p27, p38 and p47 use: the kernel writes only its "
    "own local table, which nothing outside the call can observe. "
    "**THE `ensures` IS A FUNCTIONAL POSTCONDITION AND IT IS NOT WHERE p22'S "
    "BUG LIVES.** `run` is an abstract machine over (table, nfill, acc) and the "
    "`ensures` says the accumulator is what that machine computes, so a rung "
    "that probed differently, inserted into a different slot or truncated at a "
    "different TABCAP is rejected. c/kernel.c would satisfy it too -- on every "
    "input on which it RETURNS. What excludes c/kernel.c's bug is not any "
    "clause here: it is the `decreases` on verus.rs's probe loop, an obligation "
    "Verus imposes on every exec loop by default and whose absence is reported "
    "as `error: loop must have a decreases clause` before any postcondition is "
    "considered. ⚠ **THAT IS NOT THE FIRST TERMINATION OBLIGATION IN THIS "
    "PROJECT AND THE SENTENCE THAT SAID SO IS RETRACTED** (TASK_070_REVIEW F1, "
    "which counted it; the claim came from TASK_070.md and shipped in eight "
    "places, TWO OF THEM INSIDE THIS HASHED BLOCK). Verus imposes a "
    "`decreases` on EVERY exec loop by default, so this tree carries 73 "
    "exec-loop measures across 21 verus.rs files and 72 of them are not p22's "
    "probe loop. What IS p22's own is counted rather than argued: of those 73, "
    "the probe loop's is the ONLY measure that is not expressible in the "
    "loop's own exec variables. It is `i0 as int + d - u` -- a ghost cursor "
    "and a ghost witness handed over by a counting lemma, with the loop's own "
    "control variable `i` absent from it entirely, because `i` WRAPS. The "
    "other 72 are `B - c` for a loop-invariant bound and a monotone exec "
    "cursor, or a bare monotone exec variable (../NOTES.md 0e, 9). "
    "What the `ensures` deliberately does NOT say is that `nkey` is honest, "
    "that the key stream is well formed, or that the window has fewer than "
    "TABCAP distinct keys: a precondition about the contents of a file is one "
    "no honest loader can discharge (`.memory/02-bench-rules.md`), and it would "
    "delete every row this pattern exists for. `nfill < TABCAP` is a fact the "
    "kernel MAINTAINS -- `count_ne(tab, TABCAP) == nfill` is the loop invariant "
    "that says so -- and not one it assumes. degenerate.bin and all five "
    "adversarial rows are therefore INSIDE the verified domain, and every rung "
    "except c/kernel.c agrees with model.py on all of them."
)

OBLIGATIONS_NOTE = (
    "20 = TABCAP 1 + EMPTY 1 + SENT 1 + count_ne 1 + probe 1 + run 1 + "
    "lemma_count_zero 1 + lemma_all_ne 1 + lemma_exists_empty 1 + "
    "lemma_count_congr 1 + lemma_count_update 1 + kernel 4 + main 5, each term "
    "MEASURED with `./verus_run.py verus.rs --verify-function <name> "
    "--verify-root` and not predicted, and the terms SUM to the pinned total "
    "(p27's did not, in a spec.md the gate had passed nineteen times -- "
    "`.memory/04-verus.md`). The zero terms are checkable the same way: u32_at, "
    "nkey_at, hash_s, empty_tab and key_fold are NON-RECURSIVE spec fns and "
    "report 0, while count_ne, probe and run are RECURSIVE and carry one "
    "termination query each; buf_get_unchecked, arr_get_unchecked, "
    "arr_set_unchecked, load_input and emit are external_body and report 0. "
    "THREE `const`s carry one query each (`.memory/04-verus.md`: a `const` "
    "inside verus! is its own obligation). The five proof fns carry one each. "
    "kernel's 4 = body + TWO loop bodies (the key walk and THE PROBE LOOP) + "
    "the one `assert ... by` block that places the empty slot, which is its own "
    "query. main's term is 5, which is what every other pattern in this tree "
    "that records the term also records for the byte-identical driver loop."
)

TWIN_NOTE = (
    "The obligation count in the OTHER configuration -- `verus.rs --cfg "
    "slb_twin`, which is where step 5c-twin checks the twins. 20 shipped + 3, "
    "the three trusted items inside the twin regime being "
    "slb_twin_buf_get_unchecked, slb_twin_arr_get_unchecked and "
    "slb_twin_arr_set_unchecked. `load_input` and `emit` are outside the regime "
    "(external_body with no `ensures` and no `unsafe` body) and have no twins."
)

COLLAPSE_NOTE = (
    "work_per_call is `stride` -- WINDOW BYTES, the denomination p16, p05, p11, "
    "p12, p06, p14, p27, p10, p38 and p47 use -- and it is strict here for a "
    "structural reason: on every shipped matrix blob `nkey` equals the number "
    "of key bytes present, so the kernel reads all `stride - 4` of them and "
    "then clears 64 table bytes besides, and the count cannot exceed the bytes "
    "touched. It over-counts only where a window declares fewer keys than it "
    "carries, which degenerate.bin's fourth window does and which is not a "
    "collapse.probe_input. The two probe inputs differ in work_per_call (132 vs "
    "1028) precisely so check.py's d(Ir)/d(work) assertion has two shapes and "
    "can run at all, and they differ in ALPHABET too (32 keys against 40), "
    "because the probe loop's trip count is a function of the load factor and "
    "not of the window length. model.py declares no min_ir_per_work, so the "
    "harness default of 0.25 applies unchanged; ../NOTES.md 3 has the per-cell "
    "margins."
)

IDENTITY_WHY = (
    "R4 == R5: the proof licenses unsafe code at zero cost. On p22 the pin "
    "carries a second job, and it is the one the whole Verus section turns on: "
    "**the termination proof adds NOTHING to the object code.** The `decreases` "
    "measure is built from a ghost unwrapped cursor `u`, a ghost witness `e` "
    "for an EMPTY slot and a ghost distance `d`, none of which survives "
    "erasure; the alternative route -- an exec-side probe counter -- would have "
    "put a bound in the binary and is forbidden by the idiom. So `exact` at O3 "
    "is what says p22's termination proof cost zero instructions. ⚠ It is NOT "
    "what says *the first* termination proof in this tree cost zero: that "
    "sentence stood here until TASK_070_REVIEW F1 counted 73 exec-loop "
    "`decreases` measures across 21 verus.rs files and retracted it. Every R5 "
    "here has discharged termination obligations since p01, because Verus "
    "demands a measure on every exec loop by default. p22's is the only one of "
    "the 73 built from GHOST state rather than from the loop's own exec "
    "variables, and that is what `exact` prices at zero. At O0 the crate names "
    "differ in length so call displacements differ, which is link layout and "
    "not codegen, hence `norel` there."
)

MIRI_REASON = (
    "R4 and R5 ARE byte-identical at O3. Since TASK_010 "
    "`.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a "
    "trusted item, which check.py DERIVES from verus.rs rather than reading "
    "from this flag. **On p22 Miri is expected to be, and is, entirely silent "
    "about the pattern's bug**, and measuring that is half the result: a "
    "non-terminating loop is not undefined behaviour, so an interpreter that "
    "checks for UB has nothing to say about it. Run the safe-Rust rung with the "
    "capacity conjunct deleted under Miri and it spins until the timeout kills "
    "it, with no diagnostic and no output "
    "(`controls/gen_controls.py --run r2_noguard`, ../NOTES.md 0b). Miri is "
    "listed here because the three contract-bearing trusted items are real and "
    "a wrong `arr_set_unchecked` would still be invisible to Verus. "
    "⚠ **`adversarial-full.bin` is a BLOCKED Miri row**, not a passing one: "
    "model.py declares `expected_hang` on it and check.py blocks the row up "
    "front rather than waiting out MIRI_TIMEOUT. p22 therefore lands "
    "PASS-WITH-BLOCKED-ROWS and not PASS. ⚠ On p22 the block's stated reason -- "
    "*R4 does not return under Miri either* -- is FALSE: it is the C rung that "
    "hangs and unsafe.rs returns. ../NOTES.md 11 reports that as a harness "
    "finding rather than working around it."
)

RUN_WHY = (
    "c/kernel.c's probe loop does not terminate on `adversarial-full.bin`: its "
    "single window carries the 64 distinct keys that fill the table and then a "
    "65th that is absent from it, so the loop has no EMPTY slot to stop at and "
    "no matching key to find. 8 of the 32 built cells hang on it -- c-gcc and "
    "c-clang at both optimisation levels and in both link modes -- and without "
    "a budget each would be waited on for RUN_TIMEOUT (900 s), i.e. two hours "
    "per gate run. **2.0 s is the pin**, and the argument for the number is a "
    "measurement rather than a round figure: the same input on the cells that "
    "DO terminate is 1-3 ms wall (n_iters is 1 and the window is 132 bytes), "
    "bare process startup on this box is 1-2 ms, and the slowest shipped O0 "
    "cell anywhere in this tree on `large.bin` is 198 ms -- so 2.0 s is about "
    "10x the slowest honest cell in the project and roughly 1000x the slowest "
    "honest cell on THIS input. It is also 2x RUN_BUDGET_FLOOR, so it is not "
    "sitting on the floor. `_confirm_hang` re-runs one hung cell at 20 s and "
    "the pattern FAILS if it terminates, which is what stops this pin from "
    "being self-certifying. Total added cost of the declaration: about 36 s per "
    "gate run against about two hours without it. "
    "⚠ **`adversarial-nearfull.bin` deliberately carries NO budget**: 63 "
    "distinct keys and then 64 more from the same 63, so `nfill` stops one "
    "short of TABCAP and every cell including c/kernel.c terminates. It is the "
    "negative control for this declaration, and if it ever needed a budget the "
    "declaration above would be measuring something other than a full table."
)

UNSAFE_JUSTIFICATIONS = {
    "verus.rs": {
        "arr_set_unchecked": (
            "`x` is a pure VALUE parameter: it is stored into the table and is "
            "never used as an address, an index or a length, so there is no "
            "precondition a caller could usefully be asked for -- every `T` is "
            "a legal thing to store in a `T` slot. The two parameters that DO "
            "decide whether the unchecked store is defined, `v` and `i`, are "
            "both constrained by `i < old(v)@.len()`, which for a `&mut [T; N]` "
            "reads `i < N`. This is the parameter-coverage false positive "
            "`.memory/04-verus.md` names; p03 was the first pattern to exercise "
            "it, p12 the second, p06 the third, p14 the fourth, p27 the fifth "
            "and p38 the sixth."
        ),
    },
}

ITEM_UNCHECKED_GET = {
    "external": "verifier::external_body",
    "requires": ["i < v@.len()"],
    "ensures": ["r == v@[i as int]"],
}
ITEM_TWIN_GET = {
    "external": None,
    "requires": ["i < v@.len()"],
    "ensures": ["r == v@[i as int]"],
}
ITEM_SET = {
    "external": "verifier::external_body",
    "requires": ["i < old(v)@.len()"],
    "ensures": ["final(v)@ == old(v)@.update(i as int, x)"],
}
ITEM_TWIN_SET = {
    "external": None,
    "requires": ["i < old(v)@.len()"],
    "ensures": ["final(v)@ == old(v)@.update(i as int, x)"],
}
SPEC_ITEM = {"external": None, "requires": [], "ensures": []}
EXT_ITEM = {"external": "verifier::external_body",
            "requires": [], "ensures": []}


def contract():
    why = WHY_HEAD + donor_paragraph()
    return {
        "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
        "model": "model.py",
        "requires": ["off + len <= buf_len"],
        "ensures": ["result == key_fold(buf, off, len)"],
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
            "obligations": {"verus.rs": 20},
            "twin_obligations": {"verus.rs": 23},
            "obligations_note": OBLIGATIONS_NOTE,
            "twin_obligations_note": TWIN_NOTE,
            "unsafe_justifications": UNSAFE_JUSTIFICATIONS,
            "items": {
                "verus.rs": {
                    "u32_at": SPEC_ITEM,
                    "nkey_at": SPEC_ITEM,
                    "hash_s": SPEC_ITEM,
                    "count_ne": SPEC_ITEM,
                    "probe": SPEC_ITEM,
                    "empty_tab": SPEC_ITEM,
                    "run": SPEC_ITEM,
                    "key_fold": SPEC_ITEM,
                    "lemma_count_zero": {
                        "external": None,
                        "requires": [
                            "0 <= n <= s.len()",
                            "forall|j: int| 0 <= j < n ==> s[j] == EMPTY",
                        ],
                        "ensures": ["count_ne(s, n) == 0"],
                    },
                    "lemma_all_ne": {
                        "external": None,
                        "requires": [
                            "0 <= n <= s.len()",
                            "forall|j: int| 0 <= j < n ==> s[j] != EMPTY",
                        ],
                        "ensures": ["count_ne(s, n) == n"],
                    },
                    "lemma_exists_empty": {
                        "external": None,
                        "requires": [
                            "s.len() == TABCAP as int",
                            "count_ne(s, TABCAP as int) < TABCAP as int",
                        ],
                        "ensures": [
                            "exists|j: int| 0 <= j < TABCAP as int && s[j] == EMPTY",
                        ],
                    },
                    "lemma_count_congr": {
                        "external": None,
                        "requires": [
                            "0 <= n <= s.len()",
                            "n <= t.len()",
                            "forall|j: int| 0 <= j < n ==> s[j] == t[j]",
                        ],
                        "ensures": ["count_ne(s, n) == count_ne(t, n)"],
                    },
                    "lemma_count_update": {
                        "external": None,
                        "requires": [
                            "0 <= i < n <= s.len()",
                            "s[i] == EMPTY",
                            "x != EMPTY",
                        ],
                        "ensures": [
                            "count_ne(s.update(i, x), n) == count_ne(s, n) + 1",
                        ],
                    },
                    "buf_get_unchecked": ITEM_UNCHECKED_GET,
                    "slb_twin_buf_get_unchecked": ITEM_TWIN_GET,
                    "arr_get_unchecked": ITEM_UNCHECKED_GET,
                    "slb_twin_arr_get_unchecked": ITEM_TWIN_GET,
                    "arr_set_unchecked": ITEM_SET,
                    "slb_twin_arr_set_unchecked": ITEM_TWIN_SET,
                    "load_input": EXT_ITEM,
                    "emit": EXT_ITEM,
                    "kernel": {
                        "external": None,
                        "requires": ["off + len <= buf@.len()"],
                        "ensures": ["r == key_fold(buf@, off as int, len as int)"],
                    },
                    "main": SPEC_ITEM,
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
                "}",
            ],
        },
        "collapse": {
            "probe_inputs": ["small.bin", "large.bin"],
            "probe_iters": [100, 200],
            "note": COLLAPSE_NOTE,
        },
        "run": {
            "timeout_s": {"adversarial-full": 2.0},
            "why": RUN_WHY,
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


PROSE = r"""# p22 — open-addressing hash probe: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

⚠ **This file is GENERATED by `controls/mkcontract.py`. Edit the generator and
re-run it** — three tasks in a row shipped a `spec.md` edit a generator would
have silently reverted (`.memory/05-layout.md`). The generator reads the shared
named-spelling paragraph out of a DONOR pattern's `spec.md` and refuses to write
anything if the result does not satisfy `harness/check.py::named_spelling_problem`.

⚠ **p22's gate verdict is `PASS-WITH-BLOCKED-ROWS`, not `PASS`.** One input,
`adversarial-full.bin`, is declared non-terminating, and a declared-hang input
is a blocked Miri row by construction. p01 is the only other pattern in the tree
that lands there. Nothing is broken.

## What makes p22 different from the other twenty

**Every other pattern here asks what safety costs. p22 asks what safety does not
buy.**

| | every other pattern | p22 |
|---|---|---|
| what `c/kernel.c` omits | a bounds check | **a capacity check, `nfill < TABCAP`** |
| the harm | an out-of-bounds read or write | **the function never returns** |
| is it undefined behaviour? | yes | **no. Every access is `tab[i % 64]`** |
| does ASan/UBSan see it? | usually | **no — measured silent** |
| does Miri see it? | on the Rust port, yes | **no — measured silent, it just spins** |
| does safe Rust prevent it? | yes, by construction | **no. The safe port hangs identically** |
| what does R5 add? | a spatial or temporal obligation | **a TERMINATION obligation** — see below, it is *not* the first here |

⚠ **"the first termination obligation in this project" was FALSE and is
retracted** (TASK_070_REVIEW F1). Verus demands a `decreases` on every exec
loop by default, so every R5 in this tree has been discharging termination
obligations since p01: **73 exec-loop measures across 21 `verus.rs` files**, of
which 70 are in the other twenty patterns and 72 are not p22's probe loop (p22
carries 3 — the key walk, the probe loop and the driver loop). What is p22's own
is the *shape* of its measure, and it
is counted rather than argued — **of those 73, p22's probe loop carries the only
one that is not expressible in the loop's own exec variables.** The other 72 are
`B - c` for a loop-invariant bound `B` and a monotone exec cursor `c`, or a bare
monotone exec variable. p22's is `i0 as int + d - u`: a ghost cursor and a ghost
witness, with the loop's own control variable `i` nowhere in it, because `i`
wraps.

The line `c/kernel.c` omits is not a check any language emits. It is written by
hand in `c/kernel_hardened.c`, in `safe_naive.rs`, in `safe_tuned.rs`, in
`unsafe.rs` and in `verus.rs` — five times, once per rung that has it — and the
one rung whose *tooling* refuses its absence is R5, where Verus reports

```text
error: loop must have a decreases clause
    = help: to disable this check, use #[verifier::exec_allows_no_decreases_clause]
```

before it looks at a single postcondition.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, carrying the same information: `&[u8]`
is a pointer and a length and C spells the pair out. C is handed the blob length
and *both* C rungs ignore it — p47's, p06's, p10's, p12's, p14's, p27's and
p38's shape. (The arity mismatch is why `spec.md` carries a `driver.call_args`
pin: no alias can turn a four-argument call into a three-argument one.)

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..4     nkey   u32 LE    DECLARED key count              ATTACKER DATA
byte 4..      one key per byte                                 ATTACKER DATA
data_start = 4
TABCAP = 64                   the table's extent, a power of two
EMPTY  = 0                    the sentinel; key 0 is not storable
SENT   = 251                  what a rejected key folds
```

`TABCAP`, `EMPTY` and `SENT` are compile-time constants in every rung. They are
properties of the *program* — a fixed-capacity hash table has a fixed number of
slots — and not of the input: `n_iters`, `stride`, `n_blob`, `nkey` and every
key byte come from the file.

**Every byte value is a legal key.** Byte 0 is the EMPTY sentinel and therefore
folds `SENT` rather than being stored; no input is malformed and no rung rejects
anything for shape.

## Semantics

```
if len < 4:                                   return 0
nkey from the header
if nkey == 0:                                 return 0

tab[TABCAP] = {EMPTY} ; nfill = 0 ; acc = 0 ; p = 4
for t in 0 .. nkey:
    if len - p < 1:   break                            # subtraction-first
    k = buf[off+p] ; p += 1
    # >>> THE SAFETY LINE. c/kernel.c omits exactly `&& nfill < TABCAP`. <<<
    if k != EMPTY and nfill < TABCAP:
        i = k * 2654435761 / 16777216 % TABCAP         # THE HASH
        while tab[i] != EMPTY and tab[i] != k:         # THE PROBE LOOP
            i = (i + 1) % TABCAP                       # THE PROBE STEP
        if tab[i] == EMPTY:
            tab[i] = k ; nfill += 1
        acc = acc *64 31 +64 i
    else:
        acc = acc *64 31 +64 SENT

return acc *64 31 +64 nfill
```

`*64` and `+64` are wrapping `u64` operations.

**Slots are never freed.** `nfill` only grows within a call, and the table is
cleared at the start of every call, so there is no deletion, no tombstone and no
question of a probe chain broken by a removal. That is deliberate: tombstones
are a second bug class and they would put a second mechanism inside one pattern.

**The probe loop is unbounded in every rung, including the hardened one.** The
hardened rung does not add a trip count; it adds the conjunct that makes the
unbounded loop terminate. This distinction is the pattern:

* `nfill < TABCAP` says *some slot is still EMPTY*, and an EMPTY slot is what
  the probe stops at. It is a **global invariant enforced elsewhere in the
  function**, which is how every real open-addressing table argues termination.
* A bounded trip count would also make the loop stop, and it is idiomatic safe
  Rust. It is out of contract, for **two different reasons depending on where
  it goes** (TASK_070_REVIEW F3):
  * written *instead of* the conjunct it is a **different function** — it finds
    a key that is present in a full table, where these semantics reject every
    operation once the table is full. Measured: the control `r3_bounded`
    disagrees with the shipped R3 on `adversarial-full.bin`.
  * written *in addition to* the conjunct it is the **same function** — the
    control `r3_bounded_kept` agrees on all eight matrix inputs — and what
    excludes it is the probe-loop `required` entry's *no trip count anywhere*: a bound in
    the object code is the fix wearing the proof's clothes, which is the same
    ground on which `probes < TABCAP` is forbidden.

  Both are measured as controls, and the `why` key publishes what excluding the
  second one costs the R3-side span.

## The bug, and why it is the one this project has never had

`c/kernel.c` writes `if (k != EMPTY)` where `c/kernel_hardened.c` writes
`if (k != EMPTY && nfill < TABCAP)`. On a full table, a key that is not already
present makes the probe walk the ring for ever.

**Three things make it a new class rather than a lookalike:**

1. **It is memory-safe.** `i` is reduced modulo `TABCAP` before the loop and on
   every step of it, so `tab[i]` is in bounds unconditionally, in the buggy rung
   as much as in the hardened one. There is no unchecked index, no lifetime, no
   aliasing violation and no integer overflow anywhere in `c/kernel.c`.
   ASan + UBSan on it are **silent**; Miri on the equivalent safe Rust is
   **silent**. Both measured — `../NOTES.md` 0.
2. **Safe Rust does not prevent it.** Delete the same conjunct from
   `safe_naive.rs` and it hangs at `-O0` and at `-O3`. That control is shipped
   (`controls/gen_controls.py --run r2_noguard`) and it is the closest thing
   this project has to a direct measurement of what safe Rust buys.
3. **The proof is the only thing that refuses it.** Verus requires a `decreases`
   clause on every exec loop by default, and discharging p22's needs the EMPTY
   witness that `nfill < TABCAP` supplies through a counting lemma.
   ⚠ **It is not the ONLY obligation the conjunct discharges, and no mutant
   here isolates it as such** (TASK_070_REVIEW F2): re-run with
   `--multiple-errors 20`, deleting the conjunct also breaks the outer
   invariant `nfill <= TABCAP` and, once that is weakened too, the overflow
   check on `nfill + 1`. The defensible claim is the narrower one — *the
   termination obligation is real, is checked, and cannot be discharged
   without the conjunct*. `../NOTES.md` 10 has every error list and the
   mechanism that makes the isolation impossible.

## Why the hang lives on ONE adversarial input

`nfill` can never exceed the number of distinct non-zero key bytes in a window,
so a window with fewer than `TABCAP` distinct keys can never fill the table and
the missing conjunct can never be reached. `inputs/gen.py` generates every
matrix and sweep blob from an alphabet of at most 48 distinct keys **and audits
every window by simulating the unguarded rung**, refusing to write a blob that
would hang unless it is declared. `adversarial-full.bin` is the one declared
blob: 64 distinct keys, then a 65th that is absent.

That is why `harness/check.py` stage 2 can see all six rungs at all — on
`small.bin`, `large.bin` and `degenerate.bin` the two C rungs are the same
program.

## The adversarial rows

A non-terminating loop has no magnitude axis. What it has is a **fullness**
axis, and it is a step function:

| input | shape | R1's behaviour |
|---|---|---|
| `adversarial-full` | 64 distinct keys fill the table, then a 65th that is absent | **does not terminate.** 8 of 32 cells — `c-gcc`, `c-clang` × `{O0,O3}` × `{isolated,whole}` |
| `adversarial-nearfull` | 63 distinct keys, then 64 more drawn from the same 63 | terminates, and agrees with every other rung. **The negative control**: the hang needs a FULL table, not a busy one |
| `adversarial-nkeybig` | `nkey` saturated at `0xFFFFFFFF`; only the cursor guard stops the walk | terminates, agrees |
| `adversarial-allempty` | every key byte is the EMPTY sentinel | terminates, agrees; `nfill == 0` |
| `adversarial-stride3` | a 3-byte window | none: the driver guard `stride_w >= 4` skips the loop and every rung prints 0 |

⚠ **What "adversarial behaviour per rung" means when a rung never returns.**
Stage 4 records `exit=None`, `hung=True` and the cell list, and the `diverges`
column is still computed against the model's `expected_exit` — which keeps
describing the CONFORMING behaviour, so the eight hanging cells read
`diverges=True` and the twenty-four that terminate read `diverges=False`. That
is the right way round, and `harness/check.py::check_adversarial` documents why
the alternative prints the headline upside down.

## Contract

"""


def render(c):
    return PROSE + "```slb-contract\n" + json.dumps(c, indent=2) + "\n```\n"


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="do not write; report whether spec.md matches")
    a = ap.parse_args()
    c = contract()

    # Fail closed: the generator refuses to write a contract the gate would
    # reject for a reason it can see itself.
    probs = checkmod.idiom_problems(c) or []
    nsp = checkmod.named_spelling_problem(c)
    if nsp:
        probs.append(nsp)
    if probs:
        for p in probs:
            print("REFUSING:", p, file=sys.stderr)
        return 1

    txt = render(c)
    para = donor_paragraph()
    print(f"shared named-spelling paragraph: {len(para)} chars, read from "
          f"{os.path.relpath(DONOR, REPO)}")
    if a.check:
        cur = open(OUT).read() if os.path.exists(OUT) else ""
        if cur == txt:
            print("spec.md matches the generator")
            return 0
        print("spec.md DIFFERS from the generator", file=sys.stderr)
        return 1
    with open(OUT, "w") as f:
        f.write(txt)
    print(f"wrote {os.path.relpath(OUT, REPO)} ({len(txt)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
