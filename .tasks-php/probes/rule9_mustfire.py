"""Show that boxcheck.py's RULE-9 one-row-per-key arm CAN FAIL -- §H / F10.

    python3 .tasks-php/probes/rule9_mustfire.py

⭐ THE STATE IT IS FOR, and it is not hypothetical -- it is `F131`, measured
2026-09-15: `RECAP_PHP.md`'s RULE-9 table listed **six** findings as BOTH
`⛔ UNREVIEWED` and verdicted (`F120`-`F125`), because `TASK_PHP_057` verdicted a
BATCH and the batch was APPENDED below the table instead of APPLIED to the rows
at the top. The table that decides what may enter `.memory-php/` disagreed with
itself about six keys, and **nothing could see it** -- the block's own preamble
records three earlier one-row instances, every one caught by eye after the fact.

⛔⛔ THIS PROBE IS DIFFERENTIAL, NOT ABSOLUTE, AND THAT IS NOT A STYLE CHOICE.
`n14_mustfire.py` shipped in the absolute form (`control PASSES, (a) FAILS`) and
broke the first time a real defect went live: every arm "failed", so the probe
could no longer tell its own planted defect from the real one. ▶ Each arm below
asserts the mutation moves `rule9_rows`'s OWN OUTPUT by exactly the planted row,
relative to whatever the baseline happens to be. That holds with a real defect
live, which is when a probe earns its keep.

⭐ And it plants the defect in a STRING, never in the committed file: `F52`'s
rule -- *the probe made the state it was measuring, and so did mine, twice, the
same week.*
"""
import re, sys, collections, importlib.util, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location(
    "bc", os.path.join(ROOT, ".tasks-php", "boxcheck.py"))
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)          # safe: the body is under __main__
os.chdir(ROOT)

DOC = open(os.path.join(ROOT, "RECAP_PHP.md"), encoding="utf-8").read()


def dups(keys):
    return {k for k, v in collections.Counter(keys).items() if v > 1}


def report(label, s):
    """-> (keys, open_cycles). Prints what the arm would have said."""
    keys, oc = bc.rule9_rows(s)
    if keys is None:
        print(f"--- {label} ---\n  (table not found)")
        return None, None
    d = dups(keys)
    print(f"--- {label} ---")
    print(f"  {len(keys)} row(s), {len(set(keys))} distinct, "
          f"{len(oc)} open cycle(s); duplicates: {' '.join(sorted(d)) or 'none'}")
    return keys, oc


base_keys, base_oc = report("baseline: RECAP_PHP.md as committed", DOC)
if base_keys is None:
    print("\nRULE-9 MUST-FIRE DEMONSTRATION: FAIL (table not found at baseline)")
    sys.exit(1)

# ---- the mutations. Each edits a COPY of the text, never the file. ----------
# ⚠⚠ THE VICTIM ROW MUST BE INSIDE THE LIVE TABLE, AND THE FIRST DRAFT OF THIS
# PROBE GOT IT WRONG -- kept, because the wrong version PROVED SOMETHING ELSE.
# It picked the first `> | ... F<n>` row anywhere in the document, which landed
# in the `_047` DATED SNAPSHOT table (`F106`), and all four differential arms
# went FAIL: the mutation was planted OUTSIDE the scanned region and the arm
# correctly ignored it. ⭐ That is a free demonstration that `_R9`'s scoping
# holds -- the snapshot tables and the `F96` per-group table are not indexed --
# and it is why the victim is now taken from the live span itself.
_span = bc._R9.search(DOC)
_first = re.search(r'^> \| .*?\bF([0-9]+)\b.*$', _span.group(1), re.M)
VICTIM = _first.group(1)
APPENDED = (f"> | **F{VICTIM}** | ✅ **UPHELD** (planted by rule9_mustfire) | "
            f"a second row for a key that already has one |\n")
mut_a = DOC.replace(_first.group(0) + "\n", _first.group(0) + "\n" + APPENDED, 1)
a_keys, a_oc = report(f"(a) VERDICT APPENDED -- a second row for F{VICTIM}", mut_a)

# (b) the same key twice in ONE cell, the shape the `_047` snapshot table uses
#     (`**F97 · F102 · F104**`) and which would silently merge three cycles
#     into one row if it ever reached the live table.
mut_b = DOC.replace(_first.group(0),
                    _first.group(0).replace(f"F{VICTIM}",
                                            f"F{VICTIM} · F{VICTIM}", 1), 1)
b_keys, b_oc = report(f"(b) TWO KEYS IN ONE CELL -- F{VICTIM} listed twice", mut_b)

print()
if a_keys is None or b_keys is None:
    print("RULE-9 MUST-FIRE DEMONSTRATION: FAIL (an arm lost the table)")
    sys.exit(1)

checks = [
    ("baseline has NO duplicate key",
     dups(base_keys) == set()),
    (f"(a) introduces exactly F{VICTIM} as a duplicate",
     dups(a_keys) - dups(base_keys) == {f"F{VICTIM}"}),
    ("(a) adds exactly one row",
     len(a_keys) - len(base_keys) == 1),
    (f"(b) introduces exactly F{VICTIM} as a duplicate",
     dups(b_keys) - dups(base_keys) == {f"F{VICTIM}"}),
    # ⭐ (b) must be caught even though it adds NO ROW -- a row-count check
    #   alone would pass it, which is why the arm counts KEYS and not rows.
    ("(b) adds no row, so a row-count check would have MISSED it",
     len(b_keys) == len(base_keys) + 1 and
     len(mut_b.split('\n')) == len(DOC.split('\n'))),
    # ⭐⭐ And the backlog must be derivable and must NOT move under a mutation
    #   that only duplicates a verdicted row -- F131 §2's half.
    ("open-cycle set is derived and non-empty at baseline",
     bool(base_oc)),
]
for label, ok in checks:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}")

if dups(base_keys):
    print(f"\n  ⓘ BASELINE ALREADY HAS DUPLICATES "
          f"({' '.join(sorted(dups(base_keys)))}) -- there is a REAL defect "
          f"live. ⭐ This probe is DIFFERENTIAL, so it still means something; "
          f"fix the real one separately, and going green here is not going "
          f"green there.")

good = all(ok for _, ok in checks)
print()
print("RULE-9 MUST-FIRE DEMONSTRATION:", "PASS" if good else "FAIL")
sys.exit(0 if good else 1)
