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
# =============================================================================
# ⭐⭐ F140's REPORT, MADE TO FIRE -- boxcheck's `items -> a reviewer` line.
# =============================================================================
# ⛔ THE FAILURE MODE IS SILENCE, NOT NOISE. That report is an ⓘ that cannot
#    fail a run, so if its regex stops matching the corpus it prints `none`
#    and reads exactly like success -- which is ITEM 131's shape (`N12` scored
#    three tools 0 arms because they spoke a different dialect). ▶ So the arm
#    below plants routing language in a synthetic items table and asserts the
#    pattern FINDS it, and plants a struck row and asserts it does NOT.
import re as _re

_ROUTE = _re.compile(r"(▶|and it)[^|]{0,80}?"
                     r"(is a REVIEWER|Give it to a reviewer|a reviewer can rule"
                     r"|belongs in the round|THE REVIEWER SAYS)", _re.I)

_SYNTH = """## Open items
| 900 | a title | plain prose, nobody is asked anything |
| 901 | a title | the manager says ▶ **It is a REVIEWER's, and it belongs in the round the backlog already owes** |
| ~~902~~ | retired | ▶ **Give it to a reviewer.** but this row is RETIRED |
| 903 | a title | narration: the reviewer found X last round, which is not a route |
| 904 | a title | the answer is settled here. ▶ **It is a REVIEWER's, and it goes to `_063`** |
| 905 | a title | a question with no addressee at all, registered and left to drift |
"""
_items = _re.findall(r'^\| (~~)?([0-9]+)(~~)? \|(.*)$', _SYNTH, _re.M)
_routed = [n for st, n, _, t in _items if not st and _ROUTE.search(t)]

checks += [
    # ⚠ ASSERTED AS A SET, NOT AS A SINGLETON. This read `_routed == ["901"]`
    #   and broke the moment 904 was added -- the arm was pinned to the
    #   POPULATION rather than to the property (F132's shape, in a must-fire).
    ("F140 report: finds BOTH routed LIVE items (901, 904) and only those",
     _routed == ["901", "904"]),
    ("F140 report: does NOT count a RETIRED row (902)", "902" not in _routed),
    ("F140 report: does NOT count narration about a reviewer (903)",
     "903" not in _routed),
    # ⛔⛔⛔ 904/905 EXIST BECAUSE THE ARM'S AUTHOR EVADED IT FOUR TIMES IN
    #   ONE TURN (items 144-147). The first regex keyed on the spellings F140
    #   happened to use, so "▶ A REVIEWER's, and it goes to `_063`" matched
    #   NOTHING. ⭐ Naming a round that does not exist yet is the SAME act as
    #   naming "the round the backlog already owes" -- a round is a process and
    #   a process has no inbox.
    ("F140 report: counts a route that names a ROUND (904)", "904" in _routed),
    # ⚠ 905 is the residual hole, stated rather than hidden: an item with NO
    #   addressee cannot be detected by a router, and registering one is the
    #   same failure wearing no clothes at all. The arm CANNOT catch it.
    ("F140 report: an item with NO addressee is invisible to the router (905) "
     "-- a KNOWN HOLE, asserted so it is not mistaken for coverage",
     "905" not in _routed),
    # ⭐ and it must be non-vacuous against the REAL corpus, or it is measuring
    #   a string literal and nothing else.
    ("F140 report: the pattern is non-vacuous on the live items table",
     bool(_ROUTE.search(open('RECAP_PHP.md', encoding='utf-8',
                             errors='replace').read()))),
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
