#!/usr/bin/env python3
"""Survey every catalogued row's upstream fix ONCE, so no row engineer repeats it.

Motivated by RECAP_PHP.md F34/F38: `ph07`'s fix took a whole task and a manager
bisect to find, and the answer was that the fix lives in the CALLER, in another
file -- which is invisible to anyone searching by the defect's function name.
This asks that question for every row, mechanically:

    does the fix_commit touch the same FILE as the defect's c_file_line?

Output: .temp/mgr/batch/fixsurvey.json  (+ a markdown table on stdout)
Patches cached under .temp/mgr/batch/patches/ so re-runs cost no network.

    python3 .temp/mgr/fixsurvey.py            # fetch what is missing, report
    python3 .temp/mgr/fixsurvey.py --offline  # report from cache only

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


def load_corpus():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8", errors="replace")))
    idx = {}
    for r in rows:
        for k in ("root_cause_id", "v5c_id", "input_id"):
            v = (r.get(k) or "").strip()
            if v:
                idx.setdefault(v, r)
    return idx


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
    print(f"catalogued rows with a corpus id: {len(res)}   "
          f"unmapped: {len(unmapped)} {unmapped}")
    print(f"resolved: {len(same) + len(other)}   same-file: {len(same)}   "
          f"OTHER-FILE: {len(other)}   unfetched: {len(unfetched)}   "
          f"no-sha: {len([x for x in flat if x.get('verdict') == 'NO-SHA'])}")
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
    main()
