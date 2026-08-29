#!/usr/bin/env python3
"""Regenerate `patterns/p29-bst-delete/spec.md`.

p27's `controls/mkspec.py` shape and for its reason: `spec.md` carries a hashed
`slb-contract` fence whose `verus.items` block must equal what
`harness/vparse.py` reads out of `verus.rs`, and whose `idiom.why` must end with
the 11003-byte named-spelling paragraph BYTE-IDENTICALLY
(`harness/check.py::named_spelling_problem`, sha256 `59748cce2db5...`). Both are
mechanical, and hand-maintaining either is how a `contract_sha256` drifts.

    python3 patterns/p29-bst-delete/controls/mkspec.py            # write
    python3 patterns/p29-bst-delete/controls/mkspec.py --check    # diff only

⚠ **`.tasks/PROTOCOL.md`'s artefact-vs-generator rule**: if you edit `spec.md`
by hand, edit THIS FILE too, or the next run silently reverts you.
"""

import argparse
import difflib
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, os.path.join(REPO, "harness"))
import vparse  # noqa: E402

SPEC = os.path.join(PDIR, "spec.md")
P27 = os.path.join(REPO, "patterns", "p27-handle-table", "spec.md")

NS_BEGIN = "NAMED-SPELLING STANDARD"
NS_END = "p01 and p08 neither"
NS_SHA = "59748cce2db5c57258677242cd59ff7e9766817bb659e7a874038d21f7150a7d"


def named_spelling():
    """The shared paragraph, lifted from p27 rather than retyped."""
    t = open(P27).read()
    i = t.find(NS_BEGIN)
    j = t.find(NS_END) + len(NS_END)
    if i < 0 or j <= i:
        raise SystemExit("mkspec: cannot find the named-spelling paragraph in p27")
    ns = t[i:j]
    h = hashlib.sha256(ns.encode()).hexdigest()
    if h != NS_SHA:
        raise SystemExit(f"mkspec: named-spelling paragraph is {h[:12]}..., "
                         f"expected {NS_SHA[:12]}...")
    return ns


def verus_items():
    out = {}
    for it in vparse.parse(open(os.path.join(PDIR, "verus.rs")).read()):
        out[it.name] = {"external": it.external,
                        "requires": list(it.clauses.get("requires", [])),
                        "ensures": list(it.clauses.get("ensures", []))}
    return {"verus.rs": out}


WHY = (
    "POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a "
    "published spread cannot carry a safety number, so what ships is a "
    "named-spelling standard -- the tokens above must appear literally, uniform "
    "across all seven rungs, with ONE measured clause: a rung spells the same "
    "operands the way its language forces. "
    "THE SAFETY LINE HAS TWO CONJUNCTS AND p27's HAS ONE, AND THAT IS THE ROW. "
    "p27's READ path asks one question -- is the ALLOCATION still there? -- and "
    "`live[h] == 1` answers it. p29's USE path has to ask two: `live[g_slot] == "
    "1` (the same conjunct, the same array, the same meaning) and `tab[g_slot]"
    "[0] == g_key` (is the OCCUPANT still the one FIND returned?). The second "
    "exists because deleting a node with two children copies the in-order "
    "successor's key and val INTO the victim's record and frees the SUCCESSOR, "
    "so the victim's allocation stays live at the same address holding somebody "
    "else's data -- and no allocation-shaped mechanism can see that. "
    "AND THE ORDER IS LOAD-BEARING, WHICH IS WHY THE TWO ARE NOT "
    "INTERCHANGEABLE: `tab[g_slot]` is never reset, so `tab[g_slot][0]` is the "
    "same load from the same address as `g_saved[0]`; C's `&&` short-circuits, "
    "so with the liveness conjunct in front the identity test is not evaluated "
    "on exactly the inputs where the record has been freed, and without it the "
    "identity test is ITSELF a heap-use-after-free (measured: zero ASan lines "
    "against a hit on every use-after-free window; the counts live in "
    "../NOTES.md 2b and ../controls/arms.json and are deliberately NOT "
    "transcribed into this hashed fence). At R5 the ordering "
    "is not even a choice: `perms.tracked_borrow(g_slot)` has "
    "`dom().contains(g_slot)` as a precondition and `live[g_slot] == 1` is the "
    "only thing that discharges it, so the identity test cannot be written "
    "first. "
    "WHY `tab[h]` IS NOT NULLED ON THE FREE, and it is p27's reason with a "
    "measurement behind it: nulling the table slot would turn a stale read into "
    "a NULL dereference -- a crash, not a use-after-free, and a different bug "
    "class. Measured on this kernel: with `tab[cur] = NULL` added, the "
    "one-conjunct control stops reporting `heap-use-after-free` and starts "
    "reporting `SEGV` (../NOTES.md 2c). It also keeps `tab[]` WRITE-ONCE PER "
    "SLOT, which is what lets R5 know `g_saved` is slot `g_slot`'s record "
    "through an invariant that no operation has to re-establish. "
    "WHY EVERY WALK CARRIES `live[cur] == 1` AND A `steps` BOUND, IN EVERY RUNG "
    "INCLUDING R1: they never fire -- a correct tree never links to a retired "
    "slot and no path is longer than TABCAP -- and they are pinned because R5 "
    "needs them. The liveness conjunct licenses the record read through "
    "`live[i] == 1 <==> perms.dom().contains(i)`, a PER-SLOT fact; the "
    "alternative is proving the link structure IS A TREE (unique parents, "
    "acyclicity), which no per-slot invariant gives you. The step bound is the "
    "`decreases` measure. They are in EVERY rung so that no rung-to-rung "
    "comparison is confounded by them, and the safe rungs would need the "
    "liveness half anyway -- `Option::unwrap` on a `None` slot is a panic. "
    "THE FREE MUST BE A REAL `free`: if the records were one slab and the "
    "release were a freelist push, the stale read would be IN BOUNDS OF A LIVE "
    "ALLOCATION -- Miri would not flag it, `PointsTo` would license it, and the "
    "bug would be LOGICAL, which is p17's class and the tree already has one. "
    "That is what `Box::into_raw`, `ManuallyDrop`, `mem::forget` and `Box::leak` "
    "are forbidden for. `realloc`/`calloc`/`Vec::with_capacity` are forbidden "
    "because they change the allocator traffic and the fairness argument is that "
    "every rung makes exactly one allocation and one free per record; "
    "`Rc`/`RefCell` because they would move the liveness decision to run time "
    "inside the library and delete the comparison. "
    "SLOTS ARE NEVER RECYCLED, AND THAT IS NOT A PRESENTATIONAL CHOICE. It is "
    "p27's convention (`ntab` only grows, which is what reduces the generation "
    "counter to one bit) and it is what keeps the safe rung's answer a function "
    "of the operations rather than of the allocator. `TASK_137` measured the "
    "third spelling -- an arena in which the release does NOT destroy the "
    "record -- and it is wrong on BOTH bug classes and BIT-IDENTICAL to buggy C, "
    "which is verbatim p32/p33's already-refused result; choosing it would "
    "retire this row rather than present it differently. "
    "WHAT IS DELIBERATELY NOT PINNED is how the liveness half is SPELLED in the "
    "safe rungs -- `is_some()` + `unwrap()` in R2, a `match` arm in R3 -- "
    "exactly as p14 leaves its fold loop unpinned: those are the R3-side levers, "
    "they cost zero TCB, and the pattern reports the cheapest one FOUND on a "
    "named input rather than a minimum. "
)

NOTE = (
    "requires/ensures above are DERIVED by check.py from verus.rs's own clause "
    "text through verus.translate, and the copy here must equal the derivation "
    "exactly. They are evaluated in Python against the bindings model.py yields "
    "per call (buf/off/len/buf_len/result) plus the helper it supplies "
    "(bst_fold). p29's bindings are the READ-ONLY set p03, p06, p11, p12, p14, "
    "p16, p17, p05, p07 and p27 use and NOT p02's before/after set: p29's "
    "records are allocated AND FREED inside the kernel, so no buffer crosses the "
    "signature and there is nothing for an `after` binding to name. "
    "**The security property is carried by TWO conjuncts on the USE path** -- "
    "`live[g_slot] == 1 && tab[g_slot][0] == g_key` in C and in the unsafe "
    "rungs, `tab[g_slot].is_some() && rec.key == g_key` in the safe rungs -- and "
    "at R5 the FIRST becomes `perms.dom().contains(g_slot)`, the precondition "
    "`tracked_borrow` cannot be called without, while the SECOND is an ordinary "
    "value equality that linearity has nothing to say about. That split is the "
    "row: `p27` needs only the first. "
    "**The `ensures` is the FUNCTIONAL one**: `run` is an abstract machine "
    "carrying five parallel slot sequences (`ky`, `vl`, `lt`, `rt`, `lv`), a "
    "root link and the cached lookup result, and it says the accumulator is what "
    "that machine computes -- so a kernel that folded a freed record's value, or "
    "a re-occupied record's, or that truncated at a different TABCAP, is "
    "rejected. **What the `ensures` deliberately does NOT say is that `nops` is "
    "honest, that the op stream is well formed, or that a cached record is still "
    "itself.** `run` specifies what the PROGRAM does -- stop when the window runs "
    "out, reject an INSERT past TABCAP, reject a FIND or REMOVE of an absent "
    "key, fold SENT for a USE whose cached record is gone or re-occupied -- so "
    "degenerate.bin and all four adversarial op-stream files are INSIDE the "
    "verified domain and every checked rung agrees with model.py on all of them. "
    "A `requires` that the op stream never staled a cached record would be a "
    "precondition about the contents of a file that no honest loader can "
    "discharge (`.memory/02-bench-rules.md`), and it would delete every row the "
    "pattern exists for."
)

OBLIG_NOTE = (
    "25 = TABCAP 1 + RECSZ 1 + NIL 1 + SENT 1 + **struct Rec 1** + descend 1 + "
    "succ_walk 1 + del_walk 1 + run 1 + rec_open 1 + rec_close 1 + rec_read 1 + "
    "rec_write 1 + walk 2 + kernel 5 + main 5. Every FUNCTION term was measured "
    "with `./verus_run.py verus.rs --verify-function <name> --verify-root` "
    "(controls/../.temp is not needed: the loop is in "
    "`.temp/t139/verus/obligations.sh` in TASK_139's scratch and the log is "
    "`.temp/t139/logs/obligations.log`). The zero terms are checkable the same "
    "way: u32_at, nops_at, val_of, alive, ins_new, step, st0, bst_fold, rec_ok, "
    "dal_ok, base and wf are NON-RECURSIVE spec fns and report 0, while descend, "
    "succ_walk, del_walk and run are RECURSIVE and carry one termination query "
    "each; buf_get_unchecked, arr_get_unchecked, arr_set_unchecked, rec_alloc, "
    "rec_free, load_input and emit are external_body and report 0. FOUR `const`s "
    "carry one query each (`.memory/04-verus.md`: a const inside verus! is its "
    "own obligation). ⚠ **AND SO DOES A `struct`, WHICH IS NEW HERE AND WAS "
    "MEASURED, NOT ASSUMED**: the per-function census sums to 24 against a "
    "measured total of 25, and adding one further bare `#[repr(C)] struct Rec2 "
    "{ a: u8 }` to a copy of this file takes the total to 26 "
    "(`.temp/t139/verus/probe_ob.rs`). The `global layout Rec` directive "
    "therefore carries ZERO. kernel's 5 = body + FOUR loop bodies (the op walk, "
    "the deletion guard loop, the successor descent and the epilogue); walk's "
    "2 = body + its one loop. main's 5 is quoted AS MEASURED."
)

TWIN_NOTE = (
    "The obligation count in the OTHER configuration -- `verus.rs --cfg "
    "slb_twin`, which is where step 5c-twin checks the twins. 25 shipped + 5, "
    "one per trusted item that is inside the twin regime: "
    "slb_twin_buf_get_unchecked, slb_twin_arr_get_unchecked, "
    "slb_twin_arr_set_unchecked, slb_twin_rec_alloc and slb_twin_rec_free. "
    "**The last two are the point of the pattern's TCB section**: their checked "
    "implementations are `vstd::raw_ptr::allocate` and "
    "`vstd::raw_ptr::deallocate` themselves, so what the twin stage proves is "
    "that this crate's copies are no stronger than vstd's originals -- a "
    "relocation of trust for a codegen reason, not new trust. `load_input` and "
    "`emit` are outside the regime (external_body with no `ensures` and no "
    "`unsafe` body) and have no twins."
)

REQUIRED = [
    {
        "c": "THE SAFETY LINE, and the only thing c/kernel.c omits: TWO "
             "conjuncts on the USE path, `if (g_saved != NULL && live[g_slot] "
             "== 1 && tab[g_slot][0] == g_key) {` in c/kernel_hardened.c. "
             "c/kernel.c writes `if (g_saved != NULL) {` there and is otherwise "
             "character-identical, so the scoped-absent audit pair this entry "
             "reports is on that rung and is correct.",
        "rust": "THE SAFETY LINE. In the unsafe rungs it is `if g_has && "
                "arr_get_unchecked(&live, g_slot as usize) == 1u8 {` followed "
                "by `if rr.key == g_key {`, and the NESTING is forced rather "
                "than chosen: at R5 the record read needs "
                "`perms.tracked_borrow(g_slot)`, whose precondition only the "
                "liveness test discharges. In the safe rungs the first conjunct "
                "is the `Option` discriminant -- `tab[g_slot].is_some()` in "
                "safe_naive.rs and the `Some(rec)` arm in safe_tuned.rs -- "
                "because safe Rust has no separate liveness array to test, "
                "**and the second conjunct has to be written out in full there "
                "too**: `rec.key == g_key`. That asymmetry is the pattern's "
                "whole subject; see the why key."
    },
    {
        "c": "THE LINE THE C RUNG MUST NOT FORGET, present in BOTH C rungs: "
             "`live[cur] = 0;` immediately after the `free`. R1's bug is NOT "
             "that it skips this -- it does not -- it is that its USE path "
             "never asks. Splitting the free from the invalidation is what makes "
             "forgetting possible at all.",
        "rust": "the same line in the unsafe rungs, `arr_set_unchecked(&mut "
                "live, cur as usize, 0u8);` -- and at R5 the proof FORCES it: "
                "without it the loop invariant cannot be re-established, because "
                "`rec_free` has consumed slot `cur`'s permission while the "
                "liveness array would still claim it exists. In the safe rungs "
                "there is no such line, because `tab[cur] = None` frees the "
                "record and invalidates the slot in ONE operation."
    },
    {
        "c": "THE SUBSTITUTION, in both C rungs, and it is the SECOND bug "
             "class's whole mechanism: `tab[cur][0] = tab[s][0];` copies the "
             "in-order successor's key INTO the victim's record. The victim's "
             "ALLOCATION is not freed, so nothing temporal happens and no "
             "allocation-shaped detector fires.",
        "rust": "the substitution in the unsafe rungs, `Rec { key: srec.key, "
                "val: srec.val, l: co.l, r: co.r }` written back through "
                "`rec_write`; in the safe rungs the same two fields are assigned "
                "to the live `Box`'s contents. Nothing is dropped in any rung."
    },
    {
        "c": "THE REAL `free`, in both C rungs: `free(tab[cur]);`. Not a "
             "freelist push into a slab -- see the why key.",
        "rust": "THE REAL free, in all four Rust rungs: `std::alloc::dealloc(p, "
                "layout);` inside rec_free in unsafe.rs and verus.rs "
                "(`vstd::raw_ptr::deallocate`'s six preconditions and its body, "
                "respelled but not weakened, whose verified twin in verus.rs is "
                "vstd's own `deallocate`), and the drop of `Option<Box<Rec>>` in "
                "safe_naive.rs and safe_tuned.rs."
    },
    {
        "c": "ONE ALLOCATION PER RECORD, in both C rungs: `malloc(RECSZ)`.",
        "rust": "ONE ALLOCATION PER RECORD, in all four Rust rungs: "
                "`std::alloc::alloc(layout)` inside rec_alloc in unsafe.rs and "
                "verus.rs, and `Box::new(Rec {` in safe_naive.rs and "
                "safe_tuned.rs. Rust's default global allocator calls `malloc` "
                "for `align <= 8`, so all seven rungs hit the same glibc, in the "
                "same size class, once per record."
    },
    {
        "c": "THE WALK'S LIVENESS CONJUNCT AND ITS STEP BOUND, in every rung "
             "including R1: `while (cur != NIL && live[cur] == 1 && steps < "
             "TABCAP)`. Neither ever fires; both are what R5 needs. See the why "
             "key.",
        "rust": "the same walk guard in the unsafe rungs, `while cur != NIL && "
                "arr_get_unchecked(live, cur as usize) == 1u8 && steps < "
                "TABCAP`, and in the safe rungs the `Option` discriminant plays "
                "the liveness role -- `tab[cur].is_some()` in safe_naive.rs and "
                "a `match tab[cur].as_ref()` whose `None` arm breaks in "
                "safe_tuned.rs."
    },
    {
        "c": "the table's extent is a COMPILE-TIME CONSTANT and the capacity "
             "guard is in every rung including R1: `if (ntab < TABCAP)` in both "
             "C rungs.",
        "rust": "the capacity guard, in all four Rust rungs: `if ntab < TABCAP "
                "{`."
    },
    {
        "c": "the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and the "
             "additive form's overflow never arises: `if (len - p < 2)` in both "
             "C rungs.",
        "rust": "the cursor guard, subtraction-first, in all four Rust rungs: "
                "`if len - p < 2 {`."
    },
    {
        "c": "the opcode is `c % 4`, so EVERY byte value is a legal opcode and "
             "no input is rejected for being malformed: `c % 4 == 0` in both C "
             "rungs.",
        "rust": "the opcode, in all four Rust rungs: `c % 4 == 0`."
    },
    {
        "c": "a rejected operation folds the SENTINEL rather than being skipped, "
             "so the fold's length is a function of the op count alone: `acc = "
             "acc * 31 + SENT;` in both C rungs.",
        "rust": "the sentinel fold, in all four Rust rungs: "
                "`.wrapping_add(SENT)`."
    },
    {
        "c": "the fold is a serial Horner chain over `acc`, spelled with the "
             "literal multiplier: `acc = acc * 31 +` in both C rungs.",
        "rust": "the fold, in all four Rust rungs, spelled with the literal "
                "multiplier: `.wrapping_mul(31)`."
    },
    "the slot count is folded last so that a rung which allocated a different "
    "number of records cannot produce the same checksum: `ntab` appears in the "
    "return expression of all seven rungs.",
]

FORBIDDEN = [
    "`realloc(`",
    "`calloc(`",
    "`Vec::with_capacity`",
    "`Rc<`",
    "`RefCell`",
    "`ManuallyDrop`",
    "`mem::forget`",
    "`Box::leak`",
    "`Box::into_raw`",
]

UNSAFE_JUST = {
    "verus.rs": {
        "arr_set_unchecked":
            "`x` is a pure VALUE parameter: it is stored into the array and is "
            "never used as an address, an index or a length, so there is no "
            "precondition a caller could usefully be asked for -- every `T` is a "
            "legal thing to store in a `T` slot. The two parameters that DO "
            "decide whether the unchecked store is defined, `v` and `i`, are "
            "both constrained by `i < old(v)@.len()`, which for a `&mut [T; N]` "
            "reads `i < N`. This is the parameter-coverage false positive "
            "`.memory/04-verus.md` names; p03 was the first pattern to exercise "
            "it, p12 the second, p06 the third, p14 the fourth, p27 the fifth "
            "and p29 the sixth.",
        "rec_alloc":
            "`size` and `align` are constrained by `valid_layout(size, align)` "
            "and `size != 0`, which is vstd's own precondition for the identical "
            "body, and the returned pointer is constrained by THREE `ensures` "
            "clauses copied from vstd verbatim -- vstd states five, and the "
            "other two (`pt.0.addr() + size <= usize::MAX + 1` and "
            "`pt.0.addr() as int % align as int == 0`) are dropped here as p27 "
            "drops them, at `align == 1` where neither is used. Dropping them "
            "makes the item strictly WEAKER, and the twin -- vstd's own "
            "`allocate` -- still verifies, which is what a weakening has to do. "
            "There is no unconstrained parameter. The reason this item exists at "
            "all is CODEGEN and not trust: vstd carries no `#[inline]` on "
            "`allocate`, so an R5 that called it directly emits a GOT-indirect "
            "cross-crate `call` that unsafe.rs cannot produce.",
        "rec_free":
            "Every parameter is constrained: `p`, `size` and `align` by the four "
            "`dealloc.*` equalities, and the two tracked permissions by "
            "`pt.is_range(..)` and the provenance equalities -- vstd's own six "
            "preconditions for the identical body, all six shipped, RESPELLED "
            "through `dealloc@.` / `pt@.` because vstd destructures its tracked "
            "parameters and this item takes plain ones; the destructured form "
            "made the gate's tautology probe unsynthesisable and left all six "
            "conjuncts unjudged. Its verified twin is vstd's `deallocate`. Same "
            "codegen reason as `rec_alloc`.",
    }
}

COLLAPSE_NOTE = (
    "work_per_call is **bytes of the window** -- `stride`, 52 on small and 244 "
    "on large -- which is p27's, p16's, p05's, p11's, p12's, p06's and p14's "
    "denomination. WHICH WAY THE ESTIMATE ERRS: STRICT, and by more than an "
    "order of magnitude. It OVER-counts by the 4 window-header bytes, which are "
    "decoded as a u32 and are not operations. It UNDER-counts by everything "
    "else: each 2 window bytes is one OPERATION, and an operation here is a TREE "
    "WALK -- up to TABCAP steps, each a table index, a liveness test and a "
    "record load -- plus, for two of the four opcodes, a `malloc` or a `free`. "
    "model.py declares NO min_ir_per_work, so the harness default applies "
    "unchanged; it is not a tight floor here and is not meant to be, because a "
    "kernel that walks a tree and calls the allocator cannot be denominated like "
    "a fold. What it still catches is the failure it exists to catch -- a kernel "
    "the optimiser collapsed to nothing. The two probe inputs differ in "
    "work_per_call (52 vs 244) precisely so check.py's d(Ir)/d(work) assertion "
    "has two shapes and can run at all."
)

IDENTITY_WHY = (
    "R4 == R5 at `-O3` up to pc-relative displacement fields, and NOT at `-O0`. "
    "⚠⚠ **THIS IS THE FIRST `identity: differ` ROW IN THE TREE AND IT IS A "
    "MEASURED RESULT, NOT A CONCESSION** -- `.memory/02-bench-rules.md` records "
    "that `differ` is a legal pin value that no pattern had yet exercised, so "
    "p29 is the run that was owed. **What differs and why.** p27 bought `O0: "
    "norel` with one line: writing `*base = v` rather than "
    "`core::ptr::write(base, v)`, because vstd's `ptr_mut_write` is "
    "`#[inline(always)]` over a precompiled vstd and inlines to a bare store "
    "while `core::ptr::write` is only `#[inline]` and survives as a call. **That "
    "trick does not transfer once the record is a four-byte struct rather than a "
    "byte**: at `-O0` R4's `*p = v` emits 870 kernel instructions and R5's "
    "`ptr_mut_write` emits 900, thirty more, in six-instruction groups at five "
    "write sites; `core::ptr::write` in R4 measures 886, closer and still not "
    "equal. All three were built and counted (../NOTES.md 5). At `-O3` the "
    "normalised text is IDENTICAL and only pc-relative fields differ -- the "
    "crate names differ in length, so the GOT displacements for "
    "`__rust_alloc`/`__rust_dealloc` differ -- which is link layout and not "
    "codegen, hence `norel`, p36's level. **The consequence the gate draws is "
    "the right one**: `check_miri` treats R4 != R5 as a reason Miri is REQUIRED "
    "rather than as an error, and Miri is required here anyway."
)

MIRI_REASON = (
    "Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any "
    "pattern with a trusted item, which check.py DERIVES from verus.rs rather "
    "than reading from this flag. **On p29 Miri is doing what it does on p27 and "
    "one thing more**: it is the only tool in the matrix that checks the "
    "TEMPORAL property on the unsafe rung, and because R4 and R5 are NOT "
    "byte-identical at `-O0` it is also the only tool that checks R4's own "
    "`-O0` shape at all. ASan checks the temporal half on the C rungs; the "
    "proof covers R5. ⚠ **And note what Miri CANNOT see here, which is the "
    "pattern's headline**: the two-child splice frees nothing, so Miri is "
    "silent on `adversarial-recycle.bin` in every rung -- the second conjunct's "
    "bug class is invisible to every allocation-shaped instrument. Cost: "
    "check.py rewrites n_iters to 4, so each row performs at most 4 x nops "
    "allocator operations."
)

DRIVER = {
    "statements": 12,
    "c_source": "c/main.c",
    "regions": ["safe_naive.rs", "safe_tuned.rs", "unsafe.rs", "verus.rs",
                "c/main.c"],
    "aliases": {"c": {"n_body": "bytes.len()", "bytes": "bytes.as_slice()",
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
}

PROSE = """# p29 -- binary search tree delete, with a cached lookup result

**The SECOND temporal row in this project, and it is `p27`'s row with one term
added to the safety line.** `c/kernel.h` carries the kernel contract in
pseudocode; this file carries the reasoning and the machine-readable pins.

## The bug, in one paragraph

A `FIND` saves the address of the record it found. A later `USE` reads through
that address and asks only whether a `FIND` ever succeeded. Deleting a key from
a binary search tree does one of two things to the record that held it, and
**which one is chosen by the DEGREE of the victim**:

| victim | what the splice does | what R1's cached read is |
|---|---|---|
| 0 or 1 child | unlinks it and **frees** it | a genuine `heap-use-after-free`; ASan aborts; the value read is **not reproducible** |
| 2 children | copies the in-order successor's key and val **into it** and frees the **successor** | an in-bounds read of a **live** allocation whose occupant changed; ASan is silent; the wrong answer is **stable** |

One omitted line, two bug classes, selected by the input.

## Why the safety line needs TWO conjuncts, and `p27`'s needs one

```
p27   if (h < ntab && live[h] == 1)                                  ONE conjunct
p29   if (g_saved != NULL && live[g_slot] == 1 && tab[g_slot][0] == g_key)   TWO
                             ^^^^^^^^^^^^^^^^^    ^^^^^^^^^^^^^^^^^^^^^^^
                             is the ALLOCATION     is the OCCUPANT still the
                             still there?          one FIND returned?
                             (p27's whole line)    (p27 has no analogue)
```

The second conjunct exists because **`p29`'s second bug class never touches the
allocation.** A liveness bit cannot see it, and neither can ASan, safe Rust's
`Option` discriminant, Miri, or a linear `PointsTo` -- all four are mechanisms
about the ALLOCATION. `../NOTES.md` 2 measures all of them.

**Neither conjunct subsumes the other, and they fail in different currencies.**
Measured on one 500-window corpus (`../NOTES.md` 2b, `controls/arms.json`): drop
the liveness conjunct and the harm is memory-unsafety and usually *not* a wrong
answer — the freed bytes still hold the old record often enough that the
checksum survives; drop the identity conjunct and the harm is a wrong answer,
**every** recycle window, and *never* a memory error. ⚠ The counts are in
`NOTES.md` and in the control's JSON, not here: a number only a rebuild can
produce must not sit inside a fence the rebuild re-hashes.

**The order is load-bearing.** `tab[g_slot]` is never reset, so `tab[g_slot][0]`
is the same load from the same address as `g_saved[0]`. `&&` short-circuits, so
the identity test is not evaluated on the inputs where the record has been
freed. At R5 the ordering is not even a choice: the record read needs
`perms.tracked_borrow(g_slot)` and only the liveness test discharges its
precondition.

## What every rung carries that a textbook BST would not

Every walk is `while (cur != NIL && live[cur] == 1 && steps < TABCAP)`, and the
two-child test asks liveness of both children: **six liveness conjuncts and five
step bounds, eleven terms, and not one of them can fire** — in every rung
including R1. They are the price of *not* proving the link
structure is a tree: with them, the licence for a record read is `p27`'s own
per-slot `live[i] == 1 <==> perms.dom().contains(i)`; without them it is unique
parents and acyclicity. They are in **every** rung so that no rung-to-rung
comparison is confounded by them, and the safe rungs would need the liveness
half anyway (`unwrap` on a `None` slot is a panic). `../NOTES.md` 4 counts them.

## Why `tab[h]` is not nulled on the free

`p27`'s `c/kernel.c` argues it by name: nulling the table slot turns a stale
read into a NULL dereference, *a crash, not a use-after-free, and a different
bug class*. p29 keeps the convention and now has a measurement for it -- with
`tab[cur] = NULL` added, the one-conjunct control stops reporting
`heap-use-after-free` and starts reporting `SEGV` (`../NOTES.md` 2c). It also
keeps `tab[]` **write-once per slot**, which is what lets R5 know `g_saved` is
slot `g_slot`'s record through an invariant no operation has to re-establish.

## Why every benign window must USE only a record that is still itself

`inputs/gen.py` checks it, by running a copy of the checked kernel over every
window of every blob it emits, and `harness/check.py` stage 2 requires every
non-adversarial cell to agree with `model.py` and with every other cell. Both
bug classes therefore live on the `adversarial-*` rows alone, whose behaviour
the gate **records** per cell instead of requiring agreement.

## The C/Rust arity gap, and `driver.call_args`

The C loop calls `kernel(buf, n_blob, k * stride, stride)` and the Rust loop
calls `kernel(buf, k * stride, stride)`. `driver.call_args` declares which
argument *positions* of a named call are the canonical ones. **This is p14's pin
unchanged**, inherited through p27; p29 adds no new declaration surface.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. p01's `spec.md` explains what each pin closes;
what is worth saying here is the arithmetic behind the two obligation counts and
the price of the identity pin.

| pin | why |
|---|---|
| `verus.obligations` = 25 | **4 consts + 1 struct + 4 recursive spec fns + 4 record ops + walk 2 + kernel 5 + main 5.** Every function term was measured with `--verify-function <name> --verify-root`; the `struct` term was measured too, and it is a fact this tree did not have -- see `obligations_note`. |
| `verus.twin_obligations` = 30 | the count under `--cfg slb_twin`. **25 shipped + 5**, one per trusted item inside the twin regime. Two of the five are `vstd::raw_ptr::allocate` and `deallocate` themselves. |
| `identity` `O3: norel`, `O0: differ` | ⚠ **the first `differ` row in the tree**, and it is measured rather than conceded: p27's one-line `-O0` fix does not transfer once the record is a struct. See the pin's `why`. |
| `miri.required: true` | on p29 Miri is the only instrument that checks the temporal property on the unsafe rung **and** the only one that sees R4's `-O0` shape at all, because R4 and R5 are not byte-identical there. ⚠ And it is **silent on the recycle half**, which is the row's point. |
"""


def build():
    contract = {
        "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
        "model": "model.py",
        "requires": ["off + len <= buf_len"],
        "ensures": ["result == bst_fold(buf, off, len)"],
        "note": NOTE,
        "idiom": {
            "required": REQUIRED,
            "forbidden": FORBIDDEN,
            "why": WHY + named_spelling(),
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
            "obligations": {"verus.rs": 25},
            "twin_obligations": {"verus.rs": 30},
            "obligations_note": OBLIG_NOTE,
            "twin_obligations_note": TWIN_NOTE,
            "unsafe_justifications": UNSAFE_JUST,
            "items": verus_items(),
        },
        "driver": DRIVER,
        "collapse": {
            "probe_inputs": ["small.bin", "large.bin"],
            "probe_iters": [100, 200],
            "note": COLLAPSE_NOTE,
        },
        "identity": [
            {"a": "unsafe", "b": "verus", "O0": "differ", "O3": "norel",
             "why": IDENTITY_WHY}
        ],
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
    return (PROSE + "\n```slb-contract\n"
            + json.dumps(contract, indent=2, ensure_ascii=False)
            + "\n```\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    text = build()
    if a.check:
        cur = open(SPEC).read() if os.path.exists(SPEC) else ""
        if cur == text:
            print("OK: spec.md matches the generator")
            return 0
        sys.stdout.writelines(difflib.unified_diff(
            cur.splitlines(True), text.splitlines(True),
            "spec.md", "mkspec.py"))
        return 1
    open(SPEC, "w").write(text)
    print(f"wrote {SPEC} ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
