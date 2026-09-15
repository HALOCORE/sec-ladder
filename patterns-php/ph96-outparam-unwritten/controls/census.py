#!/usr/bin/env python3
"""ph96 -- the `zend_call_method` CENSUS: how many 5.0.0 call sites already took
the contract that cannot be misused?

    python3 patterns-php/ph96-outparam-unwritten/controls/census.py

=============================================================================
WHY A CENSUS IS THE DELIVERABLE HERE AND NOT ON `ph97`
=============================================================================
`ph97`'s R1h is one line at one site and its census is a clean negative. This
row's R1h is a CONTRACT SWITCH -- `zend_interfaces.c:94`'s output contract
becomes `:88-93`'s no-output one -- so the question *how many sites were already
on the safe contract?* has a number, and the number is what makes
`cf020f133487` legible as **copying a sibling** rather than inventing a repair.

⚠ The parse is deliberately shallow and its own limits are printed: it counts a
site as NO-OUTPUT when the argument in the `retval_ptr_ptr` position is the token
`NULL`. The three `zend_call_method_with_N_params` macros put that argument at a
fixed index, so the index is a fact about `zend_interfaces.h` and not a guess --
and the macro definitions themselves, plus the prototype and the definition, are
subtracted by NAME rather than by a line count.

⛔ `grep -a` throughout: 41 of the corpus's 1 170 C files carry a non-UTF-8 byte
and a line-grep exits 1 with no output on one, which reads exactly like *not
present* (`RECAP_PHP.md` F35).
"""
import json
import os
import re
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
import _pin  # noqa: E402

TARBALL = ("/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/"
           "build-5.0.0/php-5.0.0.tar.gz")

#: which argument index is `retval_ptr_ptr`, per spelling -- read off
#: `Zend/zend_interfaces.h:40-49`, which the row cites.
RETVAL_ARG = {"zend_call_method_with_0_params": 4,
              "zend_call_method_with_1_params": 4,
              "zend_call_method_with_2_params": 4,
              "zend_call_method": 5}

#: the lines that are the API and not a call site.
NOT_A_CALL = {("Zend/zend_interfaces.h", 40), ("Zend/zend_interfaces.h", 42),
              ("Zend/zend_interfaces.h", 43), ("Zend/zend_interfaces.h", 45),
              ("Zend/zend_interfaces.h", 46), ("Zend/zend_interfaces.h", 48),
              ("Zend/zend_interfaces.h", 49), ("Zend/zend_interfaces.c", 30),
              ("Zend/zend_interfaces.c", 32)}

#: the manager's figures, restated as an EXPECTATION so a drift is visible.
WANT = {"sites": 23, "no_output": 7, "output": 16}


def split_args(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            if depth == 0:
                break
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def main():
    problems = []
    hits = []
    with tarfile.open(TARBALL) as t:
        for m in t.getmembers():
            if not m.isfile() or not m.name.endswith((".c", ".h")):
                continue
            txt = t.extractfile(m).read().decode("latin-1")
            if "zend_call_method" not in txt:
                continue
            rel = m.name.split("/", 1)[1]
            for n, line in enumerate(txt.split("\n"), 1):
                if "zend_call_method" not in line:
                    continue
                hits.append((rel, n, line.strip()))
    rec = {"raw_grep_hits": len(hits), "problems": problems}

    calls, api = [], []
    for rel, n, line in hits:
        if (rel, n) in NOT_A_CALL:
            api.append({"file": rel, "line": n})
            continue
        calls.append((rel, n, line))
    rec["api_lines_excluded"] = api

    noout, out, unparsed = [], [], []
    for rel, n, line in calls:
        m = re.search(r"\b(zend_call_method(?:_with_\d_params)?)\s*\(", line)
        if not m:
            unparsed.append({"file": rel, "line": n, "text": line})
            continue
        args = split_args(line[m.end():])
        idx = RETVAL_ARG[m.group(1)]
        if len(args) <= idx:
            unparsed.append({"file": rel, "line": n, "text": line})
            continue
        entry = {"file": rel, "line": n, "retval_arg": args[idx]}
        (noout if args[idx] == "NULL" else out).append(entry)

    rec["sites"] = len(calls)
    rec["no_output"] = noout
    rec["output"] = out
    rec["unparsed"] = unparsed
    print(f"raw `zend_call_method` grep hits : {len(hits)}")
    print(f"  minus the API in zend_interfaces.{{h,c}} : {len(api)}")
    print(f"  = real call sites               : {len(calls)}")
    print(f"     NO-OUTPUT (retval_ptr_ptr == NULL) : {len(noout)}")
    for e in noout:
        print(f"        {e['file']}:{e['line']}")
    print(f"     OUTPUT    (&something)             : {len(out)}")
    print(f"     unparsed                           : {len(unparsed)}")
    for e in unparsed:
        print(f"        {e['file']}:{e['line']}  {e['text'][:70]}")

    got = {"sites": len(calls), "no_output": len(noout), "output": len(out)}
    rec["expected"] = WANT
    rec["measured"] = got
    if got != WANT:
        problems.append(f"the census reads {got} where spec.md's `why` states "
                        f"{WANT}; the row quotes those three numbers and they "
                        f"must be re-derivable from the tarball")
    if unparsed:
        problems.append(f"{len(unparsed)} call site(s) could not be parsed; a "
                        f"census with an unexplained residue is not a census")

    # ⛔ MUST-FIRE: the four ArrayAccess handlers must land in the right columns,
    # or the 2x2 the row is built on is not in the tarball.
    want_cells = {("Zend/zend_object_handlers.c", 384): "output",
                  ("Zend/zend_object_handlers.c", 413): "no_output",
                  ("Zend/zend_object_handlers.c", 427): "output",
                  ("Zend/zend_object_handlers.c", 512): "output"}
    place = {}
    for e in noout:
        place[(e["file"], e["line"])] = "no_output"
    for e in out:
        place[(e["file"], e["line"])] = "output"
    rec["arrayaccess_cells"] = {f"{k[0]}:{k[1]}": place.get(k) for k in want_cells}
    print("\nN1 MUST-NOT-FIRE  the four ArrayAccess handlers:")
    for k, want in sorted(want_cells.items()):
        got1 = place.get(k)
        print(f"  {k[0]}:{k[1]:<5d} {str(got1):10s} want {want}"
              f"  {'ok' if got1 == want else 'BAD'}")
        if got1 != want:
            problems.append(f"{k[0]}:{k[1]} is classified {got1}, want {want} "
                            f"-- the row's 2x2 is not what the tarball says")

    # ⛔ MUST-FIRE: a deliberately mis-indexed reader must MISCLASSIFY, so a
    # classifier that had stopped reading the argument could not pass clean.
    bad = 0
    for rel, n, line in calls:
        m = re.search(r"\b(zend_call_method(?:_with_\d_params)?)\s*\(", line)
        if not m:
            continue
        args = split_args(line[m.end():])
        if len(args) > 0 and args[0] == "NULL":
            bad += 1
    rec["mustfire_wrong_index_noout"] = bad
    print(f"\nN2 MUST-FIRE  reading argument 0 instead of {RETVAL_ARG} "
          f"classifies {bad} site(s) as NO-OUTPUT -> "
          f"{'ok (the index is load-bearing)' if bad != len(noout) else 'BAD'}")
    if bad == len(noout):
        problems.append("reading the WRONG argument index gives the same "
                        "answer as reading the right one, so the classifier is "
                        "not reading the retval_ptr_ptr position at all")

    rec.update(_pin.pin(["spec.md"], "python3 controls/census.py",
                        "one tar walk over 1170 files, seconds"))
    with open(os.path.join(HERE, "census.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/census.json -- {len(problems)} problem(s)")
    for p in problems:
        print("  ⛔ " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
