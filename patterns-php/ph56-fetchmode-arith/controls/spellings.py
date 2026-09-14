#!/usr/bin/env python3
"""ph56 control -- **THE CONTRACT AUDIT: every backticked spelling in
`../spec.md`'s `idiom`, against every rung, with `harness/check.py`'s OWN
semantics.**

    python3 patterns-php/ph56-fetchmode-arith/controls/spellings.py --audit-only
    python3 patterns-php/ph56-fetchmode-arith/controls/spellings.py

⛔⛔ **WHAT THIS FILE IS FOR, AND IT IS NARROWER THAN `ph55`'s FILE OF THE SAME
NAME.** `ph55/controls/spellings.py` is an in-contract RESPELLING SEARCH -- it
builds R3 and R4 variants, verifies the R4 ones, and prices each lever in Ir.
**This file does NOT do that, and the row does not claim it.** What it does is
the half that has to happen BEFORE a contract lands:

> **A backtick in an `idiom.required` or `idiom.forbidden` entry IS A PIN.**
> `required` names a spelling every rung it scopes to must CARRY; `forbidden`
> names one no rung may carry, and a `forbidden` hit is a HARD GATE FAILURE
> (`check.py::idiom_audit`, since TASK_068). So a backtick dropped into
> EXPLANATORY PROSE silently creates an obligation nobody meant -- item 100,
> **three instances in three consecutive tasks, one of them inside a
> validator.**

⭐ **IT EARNED ITS KEEP ON THIS ROW BEFORE THE CONTRACT LANDED.** Run against
the first draft of `../spec.md`, it reported **24 `required` spellings ABSENT**
out of 40 -- every one of them a backtick in a sentence explaining the pin
rather than stating it: `BP_VAR_IS`, `:753`, `new_zval->refcount++`,
`EG(uninitialized_zval)`, `$a[] = 1`, `zend_fetch_dim_is_handler`,
`inputs/adversarial-chain.bin` and seventeen more. The draft was rewritten to
de-backtick all of them, and the shipped contract audits **0 absent, 0
forbidden-present**.

⚠ **WHAT NO GREP SETTLES, and this file says so rather than pretending
otherwise**: the POLARITY of a quoted span and the SET OF RUNGS a `required`
entry scopes to live in the entry's ENGLISH. `spelling_matches` decides ONE
spelling against ONE rung; which spelling and which rung is a reading. Per-
language entries (`{"c": ..., "rust": ...}`) narrow the scope mechanically and
this file honours them; a plain-string entry applies to every rung.

§H (`PROTOCOL_PHP.md`): the verdict function is a function so it can be
attacked, and `--audit-only` runs a selftest over synthetic contracts --
**five must-FIRE and four must-NOT-fire** -- because the shipped tree audits
clean and a green run is no evidence that any arm CAN fire.
"""

import argparse
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PDIR))

sys.path.insert(0, HERE)
import _pin  # noqa: E402

#: Every rung the gate builds a cell from, with the language `spelling_matches`
#: must be told. ⚠ `c/kernel_hardened.c` is R1h and `c/kernel.c` is R1: a
#: `required` entry that held only in the hardened one would be describing the
#: fix rather than the idiom.
RUNGS = [("c/kernel.c", "c"), ("c/kernel_hardened.c", "c"),
         ("safe_naive.rs", "rust"), ("safe_tuned.rs", "rust"),
         ("unsafe.rs", "rust"), ("verus.rs", "rust")]

_CHK = None


def load_check():
    """`harness/check.py`, IMPORTED, for `spelling_matches` -- the ONE definition
    of what it means for a rung to carry a declared spelling. Transcribing it
    would be a second, drifting parser; reading under `harness/` is what the
    shim exists to do and `PLAN_PHP.md` §2.1 forbids only WRITING there."""
    global _CHK
    if _CHK is None:
        spec = importlib.util.spec_from_file_location(
            "slb_check", os.path.join(ROOT, "harness", "check.py"))
        _CHK = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_CHK)
    return _CHK


def contract(path=None):
    txt = open(path or os.path.join(PDIR, "spec.md"), encoding="utf-8").read()
    return json.loads(re.search(r"```slb-contract\s*\n(.*?)```", txt, re.S).group(1))


def sources():
    return {f: open(os.path.join(PDIR, f), encoding="utf-8").read()
            for f, _ in RUNGS}


def spellings(idiom):
    """`[(key, index, lang_or_None, spelling)]` -- every backticked span in
    `required` and `forbidden`, with the scope the entry's SHAPE gives it.

    `lang_or_None` is `None` for a plain-string entry, which applies to every
    rung; 343 of the corpus's 648 `idiom` entries are plain strings with no
    language key (item 91), so this is the common shape and not the odd one."""
    out = []
    for key in ("required", "forbidden"):
        for i, e in enumerate(idiom.get(key) or []):
            if isinstance(e, dict):
                for lang in ("c", "rust"):
                    t = e.get(lang)
                    if isinstance(t, str):
                        for tok in re.findall(r"`([^`]+)`", t):
                            out.append((key, i, lang, tok))
            elif isinstance(e, str):
                for tok in re.findall(r"`([^`]+)`", e):
                    out.append((key, i, None, tok))
    return out


def audit(idiom, src):
    """`(rows, absent, present)`.

    `rows` is one entry per (spelling, rung) obligation with its verdict;
    `absent` are `required` misses and `present` are `forbidden` hits."""
    chk = load_check()
    rows, absent, present = [], [], []
    for key, i, lang, tok in spellings(idiom):
        for f, l in RUNGS:
            if lang is not None and l != lang:
                continue
            hit = chk.spelling_matches(tok, src[f], lang=l)
            rows.append({"key": key, "index": i, "lang": lang, "spelling": tok,
                         "rung": f, "hit": hit})
            if key == "required" and not hit:
                absent.append((i, lang, tok, f))
            if key == "forbidden" and hit:
                present.append((i, lang, tok, f))
    return rows, absent, present


# ---- the verdict, factored so it can be ATTACKED ----------------------------

def audit_problems(absent, present, n_obligations):
    """1. ⛔ a `forbidden` spelling PRESENT in any rung is a HARD GATE FAILURE
          and this file must say so before the gate does.
       2. ⛔ a `required` spelling ABSENT from a rung it scopes to means the
          contract pins something the tree does not carry -- item 100's shape,
          and on this row it fired 24 times on the first draft.
       3. a contract that pins NOTHING is not clean, it is unaudited: p01 and
          p05 backtick nothing at all and their rungs are matched by prose only
          (`check.py`'s own note). This row does pin, so zero obligations would
          mean the extractor has stopped seeing the entries."""
    p = []
    for (i, lang, tok, f) in present:
        p.append(f"1. forbidden[{i}] `{tok}` is PRESENT in {f} -- "
                 f"check.py::idiom_audit HARD-FAILS on this")
    for (i, lang, tok, f) in absent:
        p.append(f"2. required[{i}]{'' if lang is None else '.' + lang} "
                 f"`{tok}` is ABSENT from {f} -- the contract pins a spelling "
                 f"the tree does not carry")
    if n_obligations == 0:
        p.append("3. the contract yields ZERO (spelling x rung) obligations. "
                 "That is unaudited, not clean -- either `idiom` backticks "
                 "nothing or the extractor has stopped seeing it")
    return p


def selftest():
    cases = [
        ("P1 nothing absent, nothing present, obligations > 0",
         [], [], 40, False, None),
        ("N1 one forbidden spelling present",
         [], [(0, None, "offset != NULL", "c/kernel.c")], 40, True, "1."),
        ("N2 a forbidden spelling present in a Rust rung",
         [], [(2, "rust", "o.op2_type != T_UNUSED", "verus.rs")], 40, True, "1."),
        ("N3 one required spelling absent",
         [(0, "c", "opline->opcode += 6", "c/kernel.c")], [], 40, True, "2."),
        ("N4 a required spelling absent from ONE rung only",
         [(4, "rust", "UNINIT as usize", "safe_naive.rs")], [], 40, True, "2."),
        ("N5 the contract pins nothing at all", [], [], 0, True, "3."),
        ("P2 many obligations, all clean", [], [], 200, False, None),
        ("P3 exactly one obligation, clean", [], [], 1, False, None),
        ("P4 clean at the corpus median", [], [], 82, False, None),
    ]
    bad = []
    for label, absent, present, n, must_fire, arm in cases:
        got = audit_problems(absent, present, n)
        if bool(got) != must_fire:
            bad.append(f"selftest {label}: fired={bool(got)}, want {must_fire} ({got})")
        elif must_fire and arm and not any(g.startswith(arm) for g in got):
            bad.append(f"selftest {label}: fired on {[g[:2] for g in got]}, want {arm}")
    return bad


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit-only", action="store_true",
                    help="run the selftest and the audit; write no sidecar")
    ap.add_argument("--spec", help="audit a DRAFT spec.md instead of the shipped "
                                   "one -- which is the whole point of running "
                                   "this before a contract lands")
    args = ap.parse_args()

    problems = list(selftest())
    print("0. §H -- THE VERDICT ARM, ATTACKED OVER SYNTHETIC CONTRACTS")
    print(f"   selftest {'PASS' if not problems else 'FAIL'}   "
          f"9 arms (5 must-FIRE, 4 must-NOT-fire)")
    for p in problems:
        print(f"     *** {p}")

    c = contract(args.spec)
    src = sources()
    rows, absent, present = audit(c["idiom"], src)

    print(f"\n1. EVERY BACKTICKED SPELLING x EVERY RUNG IT SCOPES TO "
          f"({len(rows)} obligations)")
    hdr = "".join(f"{os.path.basename(f)[:9]:>11s}" for f, _ in RUNGS)
    print(f"   {'entry':<14s}{'spelling':<44s}{hdr}")
    seen = set()
    for r in rows:
        k = (r["key"], r["index"], r["lang"], r["spelling"])
        if k in seen:
            continue
        seen.add(k)
        cells = ""
        for f, l in RUNGS:
            if r["lang"] is not None and l != r["lang"]:
                cells += f"{'-':>11s}"
            else:
                hit = next(x["hit"] for x in rows
                           if (x["key"], x["index"], x["lang"], x["spelling"]) == k
                           and x["rung"] == f)
                cells += f"{('YES' if hit else 'no'):>11s}"
        tag = f"{r['key'][:4]}[{r['index']}]{'' if r['lang'] is None else '.' + r['lang'][0]}"
        print(f"   {tag:<14s}{r['spelling'][:43]:<44s}{cells}")

    problems.extend(audit_problems(absent, present, len(rows)))
    print(f"\n   required ABSENT: {len(absent)}    forbidden PRESENT: {len(present)}")

    if not args.audit_only:
        out = {"rows": rows, "absent": absent, "present": present,
               "n_obligations": len(rows), "problems": problems}
        out.update(_pin.pin(
            ['spec.md', 'c/kernel.c', 'c/kernel_hardened.c', 'safe_naive.rs',
             'safe_tuned.rs', 'unsafe.rs', 'verus.rs', 'controls/spellings.py'],
            'python3 patterns-php/ph56-fetchmode-arith/controls/spellings.py',
            'spec.md (the pins) and all six rungs (the text matched against '
            'them), plus this script. NOT inputs/ and NOT NOTES.md: no number '
            'here is derived from either.'))
        dst = os.path.join(HERE, "spellings.json")
        json.dump(out, open(dst, "w"), indent=2, sort_keys=True)
        print(f"\nwrote {os.path.relpath(dst, ROOT)}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
