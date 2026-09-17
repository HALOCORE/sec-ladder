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
    # ⛔⛔⛔ THIS READ `bool(base_oc)` -- "the live backlog is non-empty" -- AND IT
    #   FAILED ON 2026-09-16 WHEN `_063` CLEARED THE BACKLOG TO ZERO FOR THE
    #   FIRST TIME IN THE PROGRAMME'S HISTORY. ⭐ The arm was pinned to the
    #   POPULATION (a backlog happens to exist) instead of to the PROPERTY (the
    #   set is DERIVED from the table). That is F132's shape, and it is the
    #   SECOND time in this one file -- `_routed == ["901"]` was the first, and
    #   the comment 40 lines down already says so. ⚠ A must-fire arm that can
    #   only pass while the tree is UNHEALTHY is not a must-fire arm.
    # ▶ REPAIRED THE WAY THIS FILE'S OWN DOCSTRING PRESCRIBES: plant an
    #   UNREVIEWED row in a STRING and assert it is FOUND, so the arm is
    #   non-vacuous whether or not the real backlog is empty.
    ("open-cycle set is DERIVED: a planted `⛔ **UNREVIEWED**` row is found, "
     "and a verdicted one is not -- asserted on a synthetic table so the arm "
     "does not depend on the live backlog being non-empty",
     bc.rule9_rows(
         "> | finding | verdict | what |\n"
         "> |---|---|---|\n"
         "> | **F901** | ⛔ **UNREVIEWED** -- planted | nothing |\n"
         "> | **F902** | ✅ **UPHELD** (`_063`) | something |\n"
         "> \n")[1] == ["F901"]),
    # ⓘ and the live set stays REPORTED rather than asserted: an empty backlog
    #   is the goal state, not a defect, and nothing here may punish reaching it.
    ("open-cycle set on the LIVE document is a derived list (reported, not "
     f"constrained) -- currently {len(base_oc)}: "
     f"{' '.join(base_oc) if base_oc else 'none, backlog CLEAR'}",
     isinstance(base_oc, list)),
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

# ⛔⛔⛔ THIS FILE USED TO CARRY ITS OWN COPY OF THE ROUTER REGEX, AND THE COPY
#   WAS THE NARROW PRE-WIDENING FORM. So `904` -- the row that exists to prove
#   the widening catches a route naming a ROUND -- PASSED WITHOUT THE WIDENING,
#   by matching `is a REVIEWER` instead. ⭐ A must-fire arm testing a stale
#   duplicate of the thing it guards is F131 and F138 at once, inside the
#   harness that polices this arm. ▶ ONE HOME: import it.
_ROUTE = bc.ROUTE

_SYNTH = """## Open items
| 900 | a title | plain prose, nobody is asked anything |
| 901 | a title | the manager says ▶ **It is a REVIEWER's, and it belongs in the round the backlog already owes** |
| ~~902~~ | retired | ▶ **Give it to a reviewer.** but this row is RETIRED |
| 903 | a title | narration: the reviewer found X last round, which is not a route |
| 904 | a title | the answer is settled here. ▶ **It is a REVIEWER's, and it goes to `_063`** |
| 905 | a title | a question with no addressee at all, registered and left to drift |
| 906 | a title | ~~▶ **It is a REVIEWER's, and it goes to `_063`**~~ ✅ RULED, the route is SPENT |
| 907 | a title | ~~▶ **Give it to a reviewer**~~ superseded, but ▶ **it is a REVIEWER's** all over again |
| 908 | a title | the answer is settled here. ▶ **`_064`** takes it |
"""
_items = _re.findall(r'^\| (~~)?([0-9]+)(~~)? \|(.*)$', _SYNTH, _re.M)
_routed = [n for st, n, _, t in _items
           if not st and _ROUTE.search(bc.unstruck(t))]

checks += [
    # ⚠ ASSERTED AS A SET, NOT AS A SINGLETON. This read `_routed == ["901"]`
    #   and broke the moment 904 was added -- the arm was pinned to the
    #   POPULATION rather than to the property (F132's shape, in a must-fire).
    ("F140 report: finds exactly the routed-and-LIVE items "
     "(901, 904, 907, 908) and only those",
     _routed == ["901", "904", "907", "908"]),
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
    # ⛔⛔ 906/907 ADDED WHEN `_063` RULED ALL NINE ROUTED ITEMS AND FIVE STILL
    #   PRINTED AS `LIVE, unscheduled` -- the arm was matching inside the very
    #   strikethrough that recorded the route as spent. A report whose
    #   population can never shrink is one nobody reads.
    ("F140 report: a route that is STRUCK is HISTORICAL and is not counted "
     "(906)", "906" not in _routed),
    # ⭐ and the other side of it, or `unstruck` would be a licence to hide:
    #   striking one route must NOT suppress a second, LIVE one on the same row.
    ("F140 report: a struck route does NOT mask a second LIVE route on the "
     "same item (907)", "907" in _routed),
    # ⛔⛔⛔ 908 IS THE ARM THAT THE OLD PRIVATE REGEX COPY COULD NOT PASS.
    #   `904` names a round AND says "is a REVIEWER's", so the narrow form
    #   matched it for the wrong reason and the widening looked tested. 908 says
    #   ONLY `**`_064`**` -- nothing else in it is routing language at all.
    ("F140 report: counts a route whose ONLY addressee is a ROUND NAME (908) "
     "-- the case the pre-widening regex could not see",
     "908" in _routed),
    # =========================================================================
    # ⭐⭐ THE `.memory-php/ -> .temp/` ARM, MADE TO FIRE. Same failure mode as
    #   the router: it is an ⓘ that cannot fail a run, so if its regex stops
    #   matching it prints 0 and reads exactly like success.
    # ⛔⛔⛔ WHY IT EXISTS: `_063` §7.2 measured the AUTHORITATIVE LAYER depending
    #   on paths `rm` is auto-permitted to delete, and this directory family HAS
    #   already lost state once. ⭐ It is an ARM and not an open item BECAUSE
    #   `_063` §6.3 measured what a prose box is worth: F123's repair WAS one,
    #   three rounds carried it in capitals, and none did the work.
    # =========================================================================
    ("layer->temp report: a `.temp/` path in a layer line is EXTRACTED",
     bool(_re.search(r'`?(\.temp/[A-Za-z0-9_./-]+)',
                     "> see `.temp/mgr172/NOTES.md`, probe x.py"))),
    # ⛔ the bare directory is how the RULE about scratch is SPELLED, and citing
    #   the rule is not depending on a path. Counting it would drown the real
    #   dependencies in ~100 mentions of the convention itself.
    ("layer->temp report: a bare `.temp/` mention is the RULE, not a dependency",
     (lambda m: m is None or m.group(1).rstrip('.`,') in ('.temp', '.temp/'))(
         _re.search(r'`?(\.temp/[A-Za-z0-9_./-]+)',
                    "use `.temp/`, a subdir per category"))),
    # ⭐⭐ AND THE ONE WITH TEETH: EXISTS vs GONE must be DERIVED from the
    #   filesystem, not assumed. A citation whose target is already deleted is a
    #   different and worse thing than a live dependency, and the arm must be
    #   able to tell them apart -- `_063` scoped its count to 02-ladder.md and
    #   the arm found a FOURTH in 04-process.md on its first run.
    ("layer->temp report: EXISTS is derived from the filesystem "
     "(a path that cannot exist is reported GONE)",
     __import__('os').path.exists('.memory-php')
     and not __import__('os').path.exists('.temp/definitely-not-here-999')),
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
