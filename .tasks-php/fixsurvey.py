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

    # ⚠ Regression guard for the `break` that reported one fix per fat row. A
    # test that only counted rows would pass with the break still in, because
    # the break never lost a ROW -- it lost the 2nd..nth ID of a row.
    fat = sorted((ph for ph in cat
                  if len([c for c in cat[ph] if sighted.get(c)]) > 1),
                 key=lambda s: int(s[2:]))
    n_ids = sum(len([c for c in cat[ph] if sighted.get(c)]) for ph in fat)
    print(f"MUST-FIRE   rows with >1 resolvable id (the `break` reported 1 each):")
    print(f"            {len(fat)} rows, {n_ids} ids, "
          f"{n_ids - len(fat)} of them formerly unexamined")
    if fat:
        print(f"            e.g. {fat[:6]}  ✅ fires -- fat rows exist, so the")
        print("               per-id walk is load-bearing and must not regress")
    else:
        print("            ❌ DID NOT FIRE: no fat rows, so this guard is inert")
        ok = False

    # -----------------------------------------------------------------------
    # §H -- THE SHA-BINDING ARMS (TASK_PHP_054). The verdict is a PURE function
    # of (header bytes, requested sha) so these drive it on synthetic input and
    # do not depend on the cache's current contents.
    # -----------------------------------------------------------------------
    real = b"From 4f68f3774c34948ac651344d73c9d9e0a08801e6 Mon Sep 17 00:00"
    cases = [
        ("B1 MUST-NOT-FIRE  a patch carrying the sha it is filed under",
         binding_verdict(real, "4f68f3774c34") == "OK", True),
        ("B2 MUST-FIRE      a patch carrying a DIFFERENT sha",
         binding_verdict(real, "49bd45a2c175").startswith("BOUND-TO-OTHER:"),
         True),
        ("B3 MUST-FIRE      an HTML error page / truncated file has no header",
         binding_verdict(b"<!DOCTYPE html><html>", "deadbeefdead") == "NO-HEADER",
         True),
        ("B4 MUST-FIRE      `From ` present but not followed by 40 hex -- the "
         "exact hole the old startswith(b'From ') check left open",
         binding_verdict(b"From the desk of nobody at all, 2026", "abc123abc123")
         == "NO-HEADER", True),
        ("B5 MUST-NOT-FIRE  a 40-hex sha matched by a 12-hex request PREFIX",
         binding_verdict(real, "4f68f3774c34948a") == "OK", True),
        ("B6 MUST-FIRE      empty bytes are NOT silently OK",
         binding_verdict(b"", "4f68f3774c34") == "NO-HEADER", True),
    ]
    for label, got, want in cases:
        print(f"{label}")
        if got == want:
            print("            ✅")
        else:
            print("            ❌ arm did not behave as stated")
            ok = False

    # B7 ⭐ THE RATCHET. It is DERIVED from the cache, never a literal -- five
    #    hardcoded figures in .tasks-php/ validators have gone stale
    #    (04-process.md law 6), and `EMPTY_FAMILIES` proved that A BOUND IS NOT
    #    A DERIVATION. A change here is a FINDING to adjudicate by hand, not a
    #    number to update.
    live = scan_bindings()
    print(f"B7 ⓘ  cached patches whose binding does not hold: {len(live)}")
    for f, v in live:
        print(f"            {f[:-len('.patch')]}  {v}")
    if not live:
        print("            ⚠ ZERO today. If this was non-zero yesterday, the "
              "cache was re-fetched and the evidence is GONE -- say so.")

    print(f"\nselftest: {'PASS' if ok else 'FAIL'}   "
          f"({len(seen)} catalogue rows, {len(cat)} with an id)")
    return 0 if ok else 1


def _defect_file(cell):
    """The file a `c_file_line` cell is really about.

    ⚠ This was `cell.split(":")[0]`, and TASK_PHP_030 found the one cell that
    defeats it: CRASH-112 (row ph72) is

        ext/standard/uuencode.c:0|ext/standard/user_filters.c:140

    -- two files, `|`-separated, and the FIRST one carries the line-number
    SENTINEL `:0`. The naive split returned `uuencode.c`, so the row looked like
    the ph07 shape (fix in a different file) when it is nothing of the kind.
    Exactly one corpus cell has each of `:0` and `|` today, and it is this one --
    but a sentinel that silently mis-files a row is worth handling by rule, not
    by luck."""
    parts = [p.strip() for p in cell.split("|") if p.strip()]
    real = [p for p in parts
            if not re.search(r":0\s*$", p)]        # drop line-number sentinels
    chosen = (real or parts or [""])[0]
    return chosen.split(":")[0].strip()


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


# ---------------------------------------------------------------------------
# ⛔⛔ THE SHA BINDING -- TASK_PHP_054, 2026-09-15
#
# `fetch()` above validated a cached patch by `startswith(b"From ")` ALONE. That
# is a check on the SHAPE of the header and not on its CONTENT -- `RECAP_PHP.md`
# F10's class, *a guard that is a string search is a guard with a spelling*.
#
# MEASURED: 3 of the 163 cached patches carry a `From <sha>` that is NOT the sha
# they were requested under. Reproduced live, three ways:
#
#     a made-up sha            -> HTTP 404          (GitHub does not substitute)
#     a known-good corpus sha  -> From <same sha>   (4f68f3774c34, ph55's R1h)
#     these three              -> HTTP 200, NO redirect, From <a DIFFERENT sha>
#
#   49bd45a2c175  (ph79/LOGIC-025) -> bc9f2fb8dfadc1dba4264695ded28f673c54dc75
#   abb09693ac4d  (ph78/CRASH-159) -> 6a6c273893178bb9b59c117e31761fe0193d0c9f
#   ed4c0245c7ca  (ph75/CRASH-161) -> 9dfa843a386b65b18353c510f032e322004d0bb7
#
# ⭐ AND THE CONTENT IS THE RIGHT COMMIT ANYWAY: for all three the `Subject:`
# and the file count match what this survey records for that row. Agent B's
# narrowing, independently reached: both of its two carry the correct BUG NUMBER
# in the subject. ▶ So this looks like a BINDING ERROR OVER AN MFH / CHERRY-PICK
# TWIN, not an unrelated patch.
#
# ⚠⚠ THE MECHANISM IS UNEXPLAINED AND THIS CODE DOES NOT GUESS AT IT. It
# REPORTS the class and changes no verdict, because the mismatch is a fact about
# the corpus's sha and upstream's history, NOT a corruption of the cache -- and
# deleting or re-fetching the file would destroy the evidence for it.
# ---------------------------------------------------------------------------
_FROM_SHA = re.compile(rb"\AFrom ([0-9a-f]{40}) ")


def binding_verdict(head, requested):
    """Pure. `head` = first bytes of a patch file, `requested` = the sha it was
    cached under. Returns "OK" | "BOUND-TO-OTHER:<sha>" | "NO-HEADER"."""
    m = _FROM_SHA.match(head or b"")
    if not m:
        return "NO-HEADER"
    carried = m.group(1).decode()
    return "OK" if carried.startswith(requested) else "BOUND-TO-OTHER:" + carried


def scan_bindings(patdir=None):
    """Every cached patch, checked against the sha it is filed under."""
    patdir = patdir or PAT
    out = []
    if not os.path.isdir(patdir):
        return out
    for f in sorted(os.listdir(patdir)):
        p = os.path.join(patdir, f)
        if not os.path.isfile(p) or not f.endswith(".patch"):
            continue
        with open(p, "rb") as fh:
            v = binding_verdict(fh.read(64), f[:-len(".patch")])
        if v != "OK":
            out.append((f, v))
    return out


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
            defect_file = _defect_file(r.get("c_file_line") or "")
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
            # ⚠⚠ THERE WAS A `break` HERE -- "one id per row is enough". It was
            # not. A FAT ROW CARRIES ONE fix_commit PER ID, and stopping at the
            # first reported one fix and hid the rest: 68 ids across 31 rows were
            # never looked at, and 30 of those rows have ids naming DIFFERENT
            # commits (ph82 is 9 ids -> 9 commits).
            #
            # This is what made open item 45 look like "ph73's fix_commit does
            # not touch ph73's function". TASK_PHP_029 showed the column is
            # RIGHT: 3d7b0bab28e7 is the exact fix for CRASH-052, while the
            # catalogue's cited span is CRASH-051's, fixed by 235e6c0afe1d. The
            # catalogue was right and the single-record output was what looked
            # wrong -- a tool defect that spent a manager's open item.

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

    # ---- ID SPREAD -------------------------------------------------------
    # ⚠ Counts above are per RECORD, and a fat row now contributes several. This
    # section is per ROW, and it is the useful selector: a row whose ids name
    # DIFFERENT commits has no single "the fix", so §F5's "kernel_hardened.c =
    # the real fix_commit, sha-pinned" has no spelling for it until someone
    # decides which. TASK_PHP_029 measured this as nearly ORTHOGONAL to the
    # fix-date selector (date 31, id-spread 30, overlap only 10).
    spread = []
    for ph, recs in res.items():
        shas = {r["sha"] for r in recs if r.get("sha")}
        if len(shas) > 1:
            spread.append((ph, len(recs), len(shas)))
    print(f"\n⚠ ROWS WHOSE IDS NAME DIFFERENT fix_commits: {len(spread)} of {len(res)}")
    print("  (these owe an R1h decision BEFORE a build task, not inside one)")
    for ph, n, s in sorted(spread, key=lambda t: (-t[2], int(t[0][2:])))[:12]:
        print(f"   {ph:6} {n} ids -> {s} distinct fix commits")

    # ⚠ This survey answers "same file?" and RANKS. It never excludes anything.
    # The decisive test lives next door and is deliberately NOT run here: it has
    # to sha256+gunzip the 5.6 MB tarball (2.2 s vs this file's 0.1 s) and would
    # make a dependency-free lookup fail on a box where that tarball was cleaned.
    print("\n⚠ NONE of the above EXCLUDES a commit -- it only ranks. For the "
          "decisive test\n  (is the 5.0.0 text even in the commit's PRE-IMAGE?) "
          "run:\n      python3 .tasks-php/preimage_screen.py")
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

    # ⛔⛔ THE SHA BINDING -- reported, never acted on. See the block above fetch().
    bad = scan_bindings()
    print(f"\n⛔ CACHED PATCHES WHOSE `From <sha>` IS NOT THE SHA THEY ARE FILED "
          f"UNDER: {len(bad)}")
    if bad:
        by_sha = {}
        for x in flat:
            by_sha.setdefault(x["sha"][:12], []).append(f"{x['row']}/{x['id']}")
        for f, v in bad:
            who = ", ".join(by_sha.get(f[:-len('.patch')], ["(no corpus row)"]))
            print(f"   {f[:-len('.patch')]}  {v}")
            print(f"      cited by: {who}")
        print("   ⚠⚠ THE CONTENT IS STILL THE RIGHT COMMIT on every instance "
              "measured so far -- subject, bug number and file count all match "
              "the row. Treat this as a BINDING question over an MFH/cherry-pick "
              "twin, NOT as a corrupt cache, and NEVER re-fetch or delete: that "
              "destroys the only evidence there is.")
        print("   ▶ A row whose R1h is named by one of these owes an R1h "
              "DECISION before a build task (PROTOCOL_PHP.md §C), the same as a "
              "row whose ids name several commits.")


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
