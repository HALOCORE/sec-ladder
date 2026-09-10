#!/usr/bin/env python3
"""Survey every catalogued row's upstream fix ONCE, so no row engineer repeats it.

Motivated by RECAP_PHP.md F34/F38: `ph07`'s fix took a whole task and a manager
bisect to find, and the answer was that the fix lives in the CALLER, in another
file -- which is invisible to anyone searching by the defect's function name.
This asks that question for every row, mechanically:

    does the fix_commit touch the same FILE as the defect's c_file_line?

Output: .temp/mgr/batch/fixsurvey.json  (+ a markdown table on stdout)
Patches cached under .temp/mgr/batch/patches/ so re-runs cost no network.

    python3 .tasks-php/fixsurvey.py             # fetch what is missing, report
    python3 .tasks-php/fixsurvey.py --offline   # report from cache only
    python3 .tasks-php/fixsurvey.py --selftest  # §H negatives; no network

⚠ This answers "same file?", NOT "is this the commit that removes the 5.0.0
defect?" -- F38 half 2 showed 2 of 4 checked commits are LATER fixes, and only a
tag comparison settles that. Treat a `same-file` verdict as a starting point.
"""
import csv, json, os, re, subprocess, sys, time

ROOT = "/home/apt/repos_common/sec-ladder"
CSV = "/home/apt/repos_common/php-in-safe-rust/paper/evaluation/security/vuln-corpus-5.0/index.csv"
OUT = os.path.join(ROOT, ".temp/mgr/batch")
PAT = os.path.join(OUT, "patches")
DELAY = 0.7          # be polite; ~142 fetches
OFFLINE = "--offline" in sys.argv


def load_corpus(with_merged=True):
    """`with_merged=False` is NOT a mode anyone should run -- it exists only so
    --selftest can rebuild the blind index and show the answer moves (§H)."""
    rows = list(csv.DictReader(open(CSV, encoding="utf-8", errors="replace")))
    idx = {}
    for r in rows:
        for k in ("root_cause_id", "v5c_id", "input_id"):
            v = (r.get(k) or "").strip()
            if v:
                idx.setdefault(v, r)
        # ⚠ THE THIRD NAMESPACE. 22 corpus ids -- every one a V5C -- appear
        # ONLY inside `merged_members`, semicolon-separated, and are absent
        # from all three columns above. Indexing only those three made ph94
        # and ph95 vanish from this survey with `unmapped: 0` still printed.
        # Same blindness previously found and fixed in coverage.py; this is
        # the THIRD instance of it, so treat the column list as a known trap.
        if with_merged:
            for v in re.split(r"[;,\s]+", (r.get("merged_members") or "").strip()):
                if v:
                    idx.setdefault(v, r)
    return idx


def selftest():
    """§H: this file is a VALIDATOR, so it ships with a must-fire and a
    must-NOT-fire case. The must-fire REBUILDS THE BLIND INDEX -- it changes the
    setup's one arbitrary constant (the column list) and checks the answer
    moves, which is the F52 discipline. A test that only ran the fixed path
    would pass just as happily against a no-op patch."""
    cat, seen = catalogue_rows()
    ok = True

    blind, sighted = load_corpus(with_merged=False), load_corpus()
    lost = sorted((ph for ph in cat if not any(blind.get(c) for c in cat[ph])
                   and any(sighted.get(c) for c in cat[ph])),
                  key=lambda s: int(s[2:]))
    print("MUST-FIRE   index without `merged_members` loses these rows entirely:")
    print(f"            {lost}")
    if lost:
        print("            ✅ fires -- the blind index drops rows, so the fix is load-bearing")
    else:
        print("            ❌ DID NOT FIRE: no row depends on `merged_members`, so either")
        print("               the corpus changed or this test no longer tests anything")
        ok = False

    orphan = sorted((ph for ph in cat if not any(sighted.get(c) for c in cat[ph])),
                    key=lambda s: int(s[2:]))
    print("MUST-NOT-FIRE  with the full index, rows whose ids resolve to nothing:")
    print(f"            {orphan}")
    if orphan:
        print("            ❌ FIRED: a row is still unreachable -- a FOURTH namespace?")
        ok = False
    else:
        print("            ✅ silent -- every catalogued row reaches the corpus index")

    missing = [ph for ph in seen if ph not in cat]
    print(f"MUST-NOT-FIRE  catalogue rows carrying no id at all: {missing}")
    if missing:
        print("            ❌ FIRED")
        ok = False
    else:
        print("            ✅ silent")

    print(f"\nselftest: {'PASS' if ok else 'FAIL'}   "
          f"({len(seen)} catalogue rows, {len(cat)} with an id)")
    return 0 if ok else 1


def catalogue_rows():
    """phNN -> [corpus ids], from Part A. Rows whose id cell does not parse are
    reported rather than dropped (F38's coverage note)."""
    cat = open(os.path.join(ROOT, "patterns-php/CATALOGUE.md"), encoding="utf-8").read()
    out, seen = {}, []
    for line in cat.splitlines():
        m = re.match(r"\| (ph\d+) \|", line)
        if not m:
            continue
        seen.append(m.group(1))
        ids = re.findall(r"\b(?:CRASH|V5C|LOGIC)-\d+\b", line)
        if ids:
            out[m.group(1)] = ids
    return out, seen


def fetch(sha):
    p = os.path.join(PAT, f"{sha}.patch")
    if os.path.exists(p) and os.path.getsize(p) > 0:
        return p
    if OFFLINE:
        return None
    os.makedirs(PAT, exist_ok=True)
    rc = subprocess.run(
        ["curl", "-sSL", "--max-time", "45", "-o", p,
         f"https://github.com/php/php-src/commit/{sha}.patch"],
        capture_output=True)
    time.sleep(DELAY)
    if rc.returncode != 0 or not os.path.exists(p) or os.path.getsize(p) == 0:
        return None
    # GitHub serves an HTML error page for a bad sha; a patch starts with "From "
    with open(p, "rb") as fh:
        if not fh.read(5).startswith(b"From "):
            os.remove(p)
            return None
    return p


def parse(p):
    txt = open(p, encoding="utf-8", errors="replace").read()
    subj = re.search(r"^Subject: \[PATCH\] (.*)$", txt, re.M)
    date = re.search(r"^Date: (.*)$", txt, re.M)
    auth = re.search(r"^From: (.*?) <", txt, re.M)
    files = re.findall(r"^diff --git a/(\S+) b/", txt, re.M)
    return {
        "subject": (subj.group(1).strip() if subj else "?")[:90],
        "date": (date.group(1).strip()[:16] if date else "?"),
        "author": (auth.group(1).strip() if auth else "?"),
        "files": files,
        "n_files": len(files),
        "bytes": len(txt),
    }


def main():
    idx = load_corpus()
    cat, seen = catalogue_rows()
    os.makedirs(OUT, exist_ok=True)
    res, unmapped, unfetched = {}, [r for r in seen if r not in cat], []

    for ph in sorted(cat, key=lambda s: int(s[2:])):
        # ⚠ A row whose ids ALL fail to resolve used to `continue` silently and
        # never enter `res` -- so the headline counted the survivors as if they
        # were the population, while `unmapped` (which measures something else
        # entirely: no id ON THE CATALOGUE LINE) still read 0. A dropped row now
        # ships as an UNRESOLVED verdict, because the whole point of this survey
        # is that "no fix found" and "never looked" must not print the same.
        if not any(idx.get(c) for c in cat[ph]):
            res.setdefault(ph, []).append(
                {"row": ph, "id": "+".join(cat[ph]), "sha": "", "defect_file": "",
                 "history_status": "", "verdict": "UNRESOLVED"})
            continue
        for cid in cat[ph]:
            r = idx.get(cid)
            if not r:
                continue
            sha = (r.get("fix_commit") or "").strip()
            defect_file = (r.get("c_file_line") or "").split(":")[0].strip()
            rec = {"row": ph, "id": cid, "sha": sha, "defect_file": defect_file,
                   "history_status": (r.get("history_status") or "").strip()}
            if not re.fullmatch(r"[0-9a-f]{11,40}", sha):
                rec["verdict"] = "NO-SHA"
                res.setdefault(ph, []).append(rec)
                continue
            p = fetch(sha)
            if not p:
                rec["verdict"] = "UNFETCHED"
                unfetched.append((ph, cid, sha))
                res.setdefault(ph, []).append(rec)
                continue
            rec.update(parse(p))
            rec["verdict"] = ("same-file" if defect_file in rec["files"]
                              else "OTHER-FILE")
            res.setdefault(ph, []).append(rec)
            break        # one id per row is enough

    json.dump({"rows": res, "unmapped_rows": unmapped,
               "unfetched": unfetched}, open(os.path.join(OUT, "fixsurvey.json"), "w"),
              indent=1)

    flat = [x for v in res.values() for x in v]
    same = [x for x in flat if x.get("verdict") == "same-file"]
    other = [x for x in flat if x.get("verdict") == "OTHER-FILE"]
    unres = [x for x in flat if x.get("verdict") == "UNRESOLVED"]
    # ⚠ Three DIFFERENT populations, printed apart on purpose. `seen` is every
    # phNN in the catalogue; `unmapped` is those with no id on the line at all;
    # UNRESOLVED is those with an id that the corpus index cannot find.
    print(f"catalogue rows: {len(seen)}   with an id on the line: {len(cat)}   "
          f"unmapped (no id): {len(unmapped)} {unmapped}")
    print(f"resolved: {len(same) + len(other)}   same-file: {len(same)}   "
          f"OTHER-FILE: {len(other)}   unfetched: {len(unfetched)}   "
          f"no-sha: {len([x for x in flat if x.get('verdict') == 'NO-SHA'])}   "
          f"UNRESOLVED: {len(unres)}")
    if unres:
        print("\n⚠⚠ ROWS WHOSE IDS THE CORPUS INDEX CANNOT FIND -- these are NOT "
              "rows without a fix, they are rows NOBODY LOOKED UP:")
        for x in sorted(unres, key=lambda r: int(r["row"][2:])):
            print(f"   {x['row']:6} {x['id']}")
    print("\n⚠ ROWS WHOSE FIX IS IN A DIFFERENT FILE FROM THE DEFECT "
          "(the ph07 shape -- a function-name search cannot find these):\n")
    print("| row | id | sha | defect file | fix touches | subject |")
    print("|---|---|---|---|---|---|")
    for x in sorted(other, key=lambda r: int(r["row"][2:])):
        f = ", ".join(x["files"][:3]) + ("…" if x["n_files"] > 3 else "")
        print(f"| {x['row']} | {x['id']} | `{x['sha'][:12]}` | `{x['defect_file']}` "
              f"| `{f}` | {x['subject'][:52]} |")
    big = [x for x in flat if x.get("n_files", 0) >= 5]
    print(f"\n⚠ fixes touching >= 5 files (F34's 'inside a rewrite' shape): {len(big)}")
    for x in sorted(big, key=lambda r: -r["n_files"])[:12]:
        print(f"   {x['row']:6} {x['sha'][:12]}  {x['n_files']:3} files  {x['subject'][:60]}")


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
