#!/usr/bin/env python3
"""contract_audit.py -- three open items that were all marked "cheap to COUNT,
and counting costs nothing".  This is the counting, with its negatives.

  ITEM 91  `idiom.required` / `forbidden` entries whose ONLY language key is
           `rust` -- an entry that pins a RUNG's own invented artefact inside a
           block whose name says *idiom* (the idiom extracted from the C).
  ITEM 98  `c/*` comments carrying provenance prose that can AGE.  `c/*` is in
           the MEASUREMENT digest, so repairing one costs a 32-cell re-measure
           (F98, ph53/c/kernel_hardened.c:8-9).
  ITEM 103 whether `results-php/preflight/*` is in any digest -- the bracket
           obligation WRITES that file, so if it is in a digest there is no way
           to take the required reading without staling something.

READ-ONLY.  This script counts and rules; it repairs nothing.

-- WHY EACH COUNT IS NARROWER THAN ITS ITEM ----------------------------------

ITEM 91 conflates two fields.  A `forbidden` entry with only a `rust` key is the
ONLY sensible shape: there is nothing in the C to forbid, because the construct
does not exist in C (`HashMap`, `transmute`, `ManuallyDrop`, `Box::leak`).  The
narrowed concern is about `required`, and the count is reported split.

ITEM 98 conflates POINTERS with VERDICTS.  A comment saying "`NOTES.md` §7 says
so in terms" points at where an argument lives; if that argument changes, the
pointer is stale but the C file has asserted nothing false.  A comment saying
"`preimage_screen.py` labels it NOT-THE-REPAIR independently" asserts another
artefact's VERDICT, and that is what aged.  Only the second class is at risk.

-- SECTION H (PROTOCOL_PHP.md) ------------------------------------------------
The negatives live INSIDE this file and run on every invocation, feeding
`problems`.  Emptying a constant is therefore a FAILING RUN, not a tidier
number.  Item 97: a validator whose negatives are gitignored ships without the
evidence that it can fail.
"""
import os, re, sys, json, glob, hashlib, argparse


def _repo_root(start=None):
    """Find the root by MARKER, not by counting `..`.

    F20 ("one `..` too few") bit the first draft of this very script: two
    dirname() calls from `.temp/mgr177/` land on `.temp`, and the import of
    `harness/check.py` failed with a message that named the module, not the
    path.  `width.py::_repo_root` carries the same fix for the same reason."""
    d = os.path.dirname(os.path.abspath(start or __file__))
    while True:
        if os.path.isdir(os.path.join(d, "harness")) and \
           os.path.isfile(os.path.join(d, "CLAUDE.md")):
            return d
        nd = os.path.dirname(d)
        if nd == d:
            raise SystemExit("REFUSED: no repo root above " + os.path.abspath(__file__))
        d = nd


ROOT = _repo_root()
sys.path.insert(0, os.path.join(ROOT, "harness"))
import check as _check          # the GATE's own parser, not a second one (F10)

problems = []

# ---------------------------------------------------------------- item 91 ----

#: Keys that are prose ABOUT the entry rather than a per-language spelling.
NON_LANG = ("why", "note", "comment")


def idiom_entries():
    """(programme, row, field, index, langs, text) for every idiom entry.

    ⚠ 343 of 648 entries are PLAIN STRINGS, not per-language dicts, so the
    schema is heterogeneous and any tool reading `idiom` must handle both.
    That is item 107's hazard one layer down: a validator that assumes dicts
    silently skips more than half the corpus."""
    for prog in ("patterns", "patterns-php"):
        for spec in sorted(glob.glob(os.path.join(ROOT, prog, "*", "spec.md"))):
            pdir = os.path.dirname(spec)
            row = os.path.basename(pdir)
            try:
                contract = _check.read_contract(pdir)[0]
            except Exception as e:                       # noqa: BLE001
                problems.append(f"item91: {prog}/{row}: contract unreadable: {e}")
                continue
            idiom = contract.get("idiom") or {}
            for field in ("required", "forbidden"):
                for i, ent in enumerate(idiom.get(field) or []):
                    if not isinstance(ent, dict):
                        yield (prog, row, field, i, ("__plain__",), str(ent))
                        continue
                    langs = tuple(sorted(k for k in ent if k not in NON_LANG))
                    yield (prog, row, field, i, langs, str(ent.get("rust") or ""))


def item91():
    ents = list(idiom_entries())
    rust_only = [e for e in ents if e[4] == ("rust",)]
    census = {}
    for e in ents:
        census[e[4]] = census.get(e[4], 0) + 1
    req = [e for e in rust_only if e[2] == "required"]
    forb = [e for e in rust_only if e[2] == "forbidden"]
    return ents, rust_only, req, forb, census


# ---------------------------------------------------------------- item 98 ----

#: A named artefact that the MEASUREMENT digest does not cover.
_TOOL = re.compile(r'\b(?:controls/|harness/|\.tasks-php/|\.temp/)?[\w]+'
                   r'\.(?:py|md|json|phpt)\b')
#: A verb asserting what that artefact CONCLUDED (not merely that it exists).
_VERDICT_VERB = re.compile(r'\b(labels?|proves?|confirms?|settles?|shows?)\b', re.I)
#: A verb merely POINTING at where an argument lives.
_POINTER_VERB = re.compile(r'\b(says?|measures?|re-?derives?|reports?|'
                           r'records?|holds?|iterates?)\b', re.I)
#: The word that made F98's claim a claim.
_INDEP = re.compile(r'\bindependent(ly)?\b|\bconfirmed by\b|\bcorroborat\w*|'
                    r'\bboth routes\b', re.I)


#: ⭐ ADJUDICATED VERDICT HITS -- a RATCHET, not a regex tuning.
#:
#: The classifier is a grep and greps have spellings (F10).  Rather than tune it
#: until the number looks right -- the exact anti-pattern this programme keeps
#: catching -- every VERDICT hit is adjudicated BY HAND here with its reason,
#: and N8 fails on any hit that is not in this table.  So the count can only be
#: wrong in the direction that FAILS THE RUN.
#:
#: key = "row/file:line" -> (REAL | FALSE-POSITIVE, why)
ADJUDICATED = {
    "ph53-iface-tail-uninit/kernel_hardened.c:8": (
        "REAL", "F98's own instance: asserts `preimage_screen.py`'s VERDICT, and "
                "F95's repair withdrew that route.  Frozen at re-measure price."),
    "ph53-iface-tail-uninit/kernel_hardened.c:9": (
        "REAL", "the second line of the same sentence -- one claim, two lines."),
    "ph03-uudecode-bound/kernel.c:38": (
        "FALSE-POSITIVE", "`labels` is a plural NOUN here (\"labels are right "
                          "about a different buffer\"), not the verb \"X labels it\"."),
    "ph07-strcut-cursor/kernel_hardened.c:134": (
        "FALSE-POSITIVE", "\"`diff` proves it\" -- `diff` is a deterministic "
                          "operation over files that are THEMSELVES in the "
                          "measurement digest, so the claim cannot age out of "
                          "step with the file asserting it."),
    "ph29-recvfrom-alloc/kernel_hardened.c:23": (
        "FALSE-POSITIVE", "\"the manager's independently cached copy\" -- "
                          "`independently` qualifies a CACHE, not a corroboration."),
    # ---- row 9 (ph55), adjudicated 2026-09-14 when the ratchet fired on it ----
    "ph55-opdata-stride/kernel_hardened.c:9": (
        "REAL", "\u26d4\u26d4 states ANOTHER TOOL'S VERDICT verbatim -- "
                "\"`preimage_screen.py`'s own verdict is `CANDIDATE` and is NOT one "
                "of them\" -- which is F98's shape exactly.  \u2b50 AND IT IS HERE "
                "BECAUSE TASK_PHP_048 \u00a72.3 TOLD THE ENGINEER TO RECORD THAT THE "
                "SCREEN IS WEAK RATHER THAN QUOTE IT AS CONFIRMATION.  The "
                "INSTRUCTION WAS RIGHT AND THE PLACEMENT WAS WRONG: that belongs in "
                "NOTES.md (gate-only, one re-gate) and not in c/* (MEASUREMENT "
                "digest, 32 cells).  \u26d4 NOT REPAIRED -- repairing it costs the "
                "re-measure item 98 exists to avoid; recorded as known, exactly as "
                "ph53's was."),
    "ph55-opdata-stride/kernel.c:473": (
        "FALSE-POSITIVE", "\"../NOTES.md \u00a74 proves it\" -- POINTER class; it "
                "says WHERE the argument lives.  The classifier fired on the strong "
                "verb `proves`, not on a stated verdict.  \u26a0 It is the strongest "
                "verb the pointer class should carry; `shows`/`says` are safer."),
    "ph55-opdata-stride/kernel_hardened.c:496": (
        "FALSE-POSITIVE", "the same sentence as kernel.c:473 -- kernel_hardened.c "
                "is c/kernel.c plus the three-line backport, so its comments are "
                "duplicated by construction.  \u2b50 EVERY ph* row will therefore "
                "double-count c/kernel.c comments; that is structural, not a defect."),
    "ph55-opdata-stride/kernel_hardened.c:326": (
        "FALSE-POSITIVE", "\"../NOTES.md \u00a75 shows why `git apply` refuses it\" -- "
                "POINTER class, same as kernel.c:473."),
    # ---- row 11 (ph97), adjudicated 2026-09-15 when the ratchet fired on it ----
    # ⚠ THE ROW'S FIRST HIT WAS REAL AND WAS REPAIRED BEFORE MEASURING, WHICH IS
    # THE WHOLE POINT OF FIRING EARLY.  The comment as first written ended
    # "A kernel that derived one from the other would have deleted the
    # mechanism" -- a VERDICT on a design argument that lives in ph96's
    # catalogue `risk` note and in TASK_PHP_056 §2.5, i.e. F98's shape.  It was
    # moved to NOTES.md §14 (gate-only) and the c/* comment now POINTS at it.
    # What is left is the classifier's adjective spelling, below.
    "ph97-optarg-unwritten/kernel.c:323": (
        "FALSE-POSITIVE", "\"TWO INDEPENDENT BYTES: `num_args` is read from b[0] "
                "and `arg.type` from b[1], and neither is computed from the other\" "
                "-- `independent` describes TWO BYTES OF THIS RECORD, decoded on "
                "the two lines immediately below, and the claim is checkable FROM "
                "THIS FILE.  It cannot age out of step with the file asserting it, "
                "which is the property the VERDICT class lacks.  It is not a "
                "corroboration between two artefacts, which is what `_INDEP` "
                "exists to catch.  ⭐ THIRD INSTANCE OF THE SAME SPELLING DEFECT "
                "-- ph29:23 (`independently cached`) and emalloc_shim.h:640 "
                "(`order-independent`) are the other two -- so the adjective/adverb "
                "false positive is a RECURRING class, absorbed correctly by the "
                "ratchet at one hand-adjudication each.  ⚠ Deliberately NOT "
                "reworded to dodge the grep: rewording to make a checker quiet is "
                "the anti-pattern this table exists instead of."),
    "ph97-optarg-unwritten/kernel_hardened.c:356": (
        "FALSE-POSITIVE", "the same sentence as kernel.c:323 -- kernel_hardened.c "
                "is c/kernel.c plus the one-line backport, so its comments are "
                "duplicated by construction, exactly as ph55's are."),
    "ph96-outparam-unwritten/kernel.h:112": (
        "FALSE-POSITIVE", "\"`shape_raw` is a third independent byte\" -- "
                "`independent` describes A BYTE OF THIS RECORD, whose decode is "
                "written out in the table on the eight lines immediately above, "
                "and the claim is checkable FROM THIS FILE.  It cannot age out of "
                "step with the file asserting it, which is the property the "
                "VERDICT class lacks, and it is not a corroboration between two "
                "artefacts, which is what `_INDEP` exists to catch.  "
                "\u26d4\u26d4 FOURTH INSTANCE OF THE SAME SPELLING DEFECT -- "
                "ph29:23 (`independently cached`), emalloc_shim.h:640 "
                "(`order-independent`) and ph97 kernel.c:323 / "
                "kernel_hardened.c:356 (`TWO INDEPENDENT BYTES`) are the others.  "
                "\u2b50 TASK_PHP_056 called the class RECURRING at three; at four "
                "it is the ratchet's single largest entry class, and every one of "
                "them is an ADJECTIVE.  A reviewer may want to decide whether that "
                "is the intended steady state.  \u26d4 NO REGEX CHANGE IS "
                "PROPOSED: \u00a7F6a and the ratchet rule both forbid it, and the "
                "false-positive direction is the safe one.  \u26a0 Deliberately "
                "NOT reworded to dodge the grep -- and on this row rewording would "
                "also cost a 32-cell re-measure, which is the second reason not "
                "to."),
    "(SHARED)/emalloc_shim.h:640": (
        "FALSE-POSITIVE", "\"order-independent per field\" -- `independent` inside "
                          "a COMPOUND ADJECTIVE describing the tally's mixing "
                          "function.  Same spelling defect as ph29:23; a substring "
                          "match cannot tell an adverb of corroboration from half "
                          "a hyphenated adjective."),
}


def _classify(line):
    """POINTER | VERDICT | None.  VERDICT is the class that can age."""
    named = bool(_TOOL.search(line))
    if not named and not _INDEP.search(line):
        return None
    if _INDEP.search(line) or (named and _VERDICT_VERB.search(line)):
        return "VERDICT"
    if named and _POINTER_VERB.search(line):
        return "POINTER"
    return None


def _is_section_header(stripped):
    """`/* ===== basic_functions.c:2102-2137  foo ===== */` and friends.

    NOT at risk: it cites a span in the PINNED tarball, which cannot age."""
    return bool(re.match(r'^[/*= ]*[\w./]+\.(c|h):\d', stripped)) or stripped.count("=") > 10


def item98():
    """Returns (rows, shared) -- shared-shim hits are deduped and reported once."""
    rows, shared, seen = {}, [], set()
    for f in sorted(glob.glob(os.path.join(ROOT, "patterns-php", "*", "c", "*"))):
        if not f.endswith((".c", ".h")):
            continue
        row, base = f.split(os.sep)[-3], os.path.basename(f)
        incomment = False
        for i, ln in enumerate(open(f, errors="replace").read().splitlines(), 1):
            s = ln.strip()
            if s.startswith("/*"):
                incomment = True
            is_comment = incomment or s.startswith("//") or s.startswith("*")
            if "*/" in s:
                incomment = False
            if not is_comment or _is_section_header(s):
                continue
            cls = _classify(ln)
            if not cls:
                continue
            if base == "emalloc_shim.h":                  # identical in every row
                k = hashlib.sha256(s.encode()).hexdigest()[:12]
                if k in seen:
                    continue
                seen.add(k)
                shared.append((base, i, cls, s[:110]))
            else:
                rows.setdefault(row, []).append((base, i, cls, s[:110]))
    return rows, shared


# --------------------------------------------------------------- item 103 ----

def item103():
    """Is any `preflight` path named inside a committed gate/measurement digest?"""
    named, mentioned = [], 0
    recs = sorted(glob.glob(os.path.join(ROOT, "results-php", "gate", "*.json"))) + \
           sorted(glob.glob(os.path.join(ROOT, "results-php", "*.json")))
    for rec in recs:
        try:
            d = json.load(open(rec))
        except Exception as e:                            # noqa: BLE001
            problems.append(f"item103: {rec} unreadable: {e}")
            continue
        if "preflight" in json.dumps(d):
            mentioned += 1
        for key in ("source_sha256", "measurement_sha256", "sources"):
            m = d.get(key)
            if isinstance(m, dict):
                for p in m:
                    if "preflight" in p:
                        named.append((os.path.relpath(rec, ROOT), key, p))
    return len(recs), mentioned, named


# ------------------------------------------------------------- negatives -----

def negatives():
    """§H: must-fire and must-NOT-fire arms, INSIDE the validator, every run."""
    print("\n" + "=" * 72)
    print("§H NEGATIVES -- they run on every invocation and feed `problems`")
    print("=" * 72)

    # -- N1 MUST-FIRE: a rust-only `required` entry is the item-91 subject.
    got = _classify_entry_langs({"rust": "`foo`"})
    ok = got == ("rust",)
    print(f"  N1 MUST-FIRE  rust-only entry -> langs {got} (want ('rust',))  "
          f"{'OK' if ok else 'FAIL'}")
    if not ok:
        problems.append("N1: a rust-only idiom entry no longer classifies as rust-only")

    # -- N2 MUST-NOT-FIRE: a c+rust entry is the NORMAL shape and is not counted.
    got = _classify_entry_langs({"c": "x", "rust": "y", "why": "prose"})
    ok = got == ("c", "rust")
    print(f"  N2 MUST-NOT-FIRE  c+rust(+why) -> langs {got} (want ('c','rust'))  "
          f"{'OK' if ok else 'FAIL'}")
    if not ok:
        problems.append("N2: `why` is leaking into the language-key set")

    # -- N3 MUST-FIRE: the F98 shape is VERDICT, not POINTER.
    f98 = "* 2 years before that commit, and `preimage_screen.py` labels it " \
          "`NOT-THE-REPAIR` independently."
    ok = _classify(f98) == "VERDICT"
    print(f"  N3 MUST-FIRE  F98's own sentence -> {_classify(f98)!r} (want 'VERDICT')  "
          f"{'OK' if ok else 'FAIL'}")
    if not ok:
        problems.append("N3: the sentence item 98 exists for no longer classifies as VERDICT")

    # -- N4 MUST-NOT-FIRE: a pointer is not a verdict, or the count is meaningless.
    ptr = "* `controls/fortify.py` measures both configurations. */"
    ok = _classify(ptr) == "POINTER"
    print(f"  N4 MUST-NOT-FIRE  a pointer sentence -> {_classify(ptr)!r} (want 'POINTER')  "
          f"{'OK' if ok else 'FAIL'}")
    if not ok:
        problems.append("N4: POINTER and VERDICT have collapsed; the item-98 split is void")

    # -- N5 MUST-NOT-FIRE: a section header must never be scanned at all.
    hdr = "/* ============ basic_functions.c:2102-2137  user_tick_function_call ===="
    ok = _is_section_header(hdr)
    print(f"  N5 MUST-NOT-FIRE  section header excluded -> {ok} (want True)  "
          f"{'OK' if ok else 'FAIL'}")
    if not ok:
        problems.append("N5: span citations into the pinned tarball are being counted as risk")

    # -- N6 LIVE REACH: the known ph53 instance must still be found.
    #    If it vanishes, EITHER someone repaired it (update this arm and say so)
    #    OR the scanner broke silently -- which is F10's defect, and the whole
    #    point of a live-reach arm is that those two look identical otherwise.
    rows, _ = item98()
    ph53 = [h for h in rows.get("ph53-iface-tail-uninit", []) if h[2] == "VERDICT"]
    ok = len(ph53) >= 1
    print(f"  N6 LIVE REACH  ph53 VERDICT hits = {len(ph53)} (want >= 1)  "
          f"{'OK' if ok else 'FAIL'}")
    if not ok:
        problems.append("N6: the ph53 instance F98 found is no longer reachable -- "
                        "repaired, or the scanner is blind")

    # -- N7 MUST-NOT-FIRE: item 103's ruling is void if a preflight path is hashed.
    _, _, named = item103()
    ok = not named
    print(f"  N7 MUST-NOT-FIRE  preflight paths inside a digest = {len(named)} (want 0)  "
          f"{'OK' if ok else 'FAIL'}")
    if not ok:
        problems.append(f"N7: item 103's ruling is VOID -- preflight is hashed: {named[:3]}")

    # -- N8 THE RATCHET: every VERDICT hit must be adjudicated by hand.
    #    A NEW hit is not allowed to slip in under a count that "looks about
    #    right"; it must be read and filed as REAL or FALSE-POSITIVE.  ⭐ And a
    #    STALE adjudication is caught too: an entry naming a line that no longer
    #    hits means someone repaired it (say so) or the scanner went blind (F10).
    live = set()
    for row, hits in item98()[0].items():
        live |= {f"{row}/{b}:{i}" for b, i, c, _s in hits if c == "VERDICT"}
    live |= {f"(SHARED)/{b}:{i}" for b, i, c, _s in item98()[1] if c == "VERDICT"}
    unfiled = sorted(live - set(ADJUDICATED))
    stale = sorted(set(ADJUDICATED) - live)
    real = [k for k, (v, _w) in ADJUDICATED.items() if v == "REAL" and k in live]
    print(f"  N8 RATCHET    VERDICT hits {len(live)}; unfiled {len(unfiled)} (want 0); "
          f"stale adjudications {len(stale)} (want 0); ⭐ REAL {len(real)}  "
          f"{'OK' if not unfiled and not stale else 'FAIL'}")
    for k in unfiled:
        problems.append(f"N8: UNFILED VERDICT hit {k} -- read it and adjudicate it "
                        f"in ADJUDICATED; do not tune the regex")
    for k in stale:
        problems.append(f"N8: STALE adjudication {k} no longer hits -- either it was "
                        f"repaired (drop the entry and say so) or the scanner is blind")


def _classify_entry_langs(ent):
    return tuple(sorted(k for k in ent if k not in NON_LANG))


# ------------------------------------------------------------------ main -----

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true",
                    help="run the §H negatives only")
    args = ap.parse_args()

    if args.selftest:
        negatives()
        return _exit()

    ents, rust_only, req, forb, census = item91()
    print("=" * 72)
    print("ITEM 91 -- idiom entries whose ONLY language key is `rust`")
    print("=" * 72)
    print(f"  entries scanned            : {len(ents)}")
    print(f"  ONLY-`rust`                : {len(rust_only)}")
    print(f"     in `forbidden`          : {len(forb)}   <- NOT the concern: there is")
    print(f"                                        nothing in the C to forbid when the")
    print(f"                                        construct does not exist in C")
    print(f"  ⭐ in `required`            : {len(req)}   <- the narrowed item-91 subject")
    for e in req:
        print(f"        {e[0]}/{e[1]} {e[2]}[{e[3]}]  {e[5][:78]}")
    print("\n  key-set census (the schema is HETEROGENEOUS -- item 107's hazard):")
    for k, v in sorted(census.items(), key=lambda kv: -kv[1]):
        label = "PLAIN STRING, no language keys" if k == ("__plain__",) else ",".join(k)
        print(f"      {v:5}  {label}")

    rows, shared = item98()
    nv = sum(1 for hs in rows.values() for h in hs if h[2] == "VERDICT")
    np_ = sum(1 for hs in rows.values() for h in hs if h[2] == "POINTER")
    print("\n" + "=" * 72)
    print("ITEM 98 -- `c/*` provenance prose, split POINTER vs VERDICT")
    print("=" * 72)
    print(f"  rows with hits             : {len(rows)}")
    print(f"  POINTER (cannot age)       : {np_}")
    print(f"  ⭐ VERDICT (CAN age)        : {nv}")
    for row in sorted(rows):
        v = [h for h in rows[row] if h[2] == "VERDICT"]
        if v:
            print(f"      {row}:")
            for b, i, _c, s in v:
                print(f"         {b}:{i}  {s}")
    print(f"  (shared emalloc_shim.h, counted once: {len(shared)} line(s), "
          f"{sum(1 for h in shared if h[2] == 'VERDICT')} VERDICT)")

    nrec, mentioned, named = item103()
    print("\n" + "=" * 72)
    print("ITEM 103 -- is `results-php/preflight/*` in any digest?")
    print("=" * 72)
    print(f"  gate + measurement records scanned : {nrec}")
    print(f"  records mentioning 'preflight'     : {mentioned}")
    print(f"  digest entries naming a preflight path : {len(named)}")
    print("  ▶ ANSWER: preflight is in NO digest, so taking the bracket reading")
    print("    cannot stale anything.  Option (a) -- say so in PROTOCOL_PHP.md --")
    print("    is free and correct." if not named else "  ⛔ RULING VOID, see N7.")

    negatives()
    return _exit()


def _exit():
    print()
    if problems:
        print(f"⛔ {len(problems)} PROBLEM(S):")
        for p in problems:
            print("   -", p)
        return 1
    print("✅ no problems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
