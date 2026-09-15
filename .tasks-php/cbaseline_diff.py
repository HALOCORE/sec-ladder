"""Which `cbaseline_check` units are NEW vs a git ref?  Diff by UNIT TEXT.

    python3 .tasks-php/cbaseline_diff.py            # vs HEAD
    python3 .tasks-php/cbaseline_diff.py 1cc2c0e    # vs any ref
    python3 .tasks-php/cbaseline_diff.py --selftest

⛔⛔⛔ WHY THIS EXISTS: THE RATCHET COUNT IS NOT A MEASURE OF CORPUS HEALTH.
`units()` splits on BLANK LINES, so a unit is a paragraph -- and an ordinary
prose edit near a hit can move the count with nothing repaired and nothing
broken.  THREE MEASURED INSTANCES (RECAP_PHP.md F132):

  1. TASK_PHP_059 found `RECAP_PHP.md`'s Index unit STOPPED hitting because a
     later finding TITLE added the literal `c-gcc` to it.  The ratchet absorbed
     a real new hit under cover of that accidental departure.
  2. Landing that round, a block inserted into `02-ladder.md`'s FOURTH-FLAG
     BLOCKQUOTE carried `c-gcc`, so BASE matched and the unit stopped hitting.
  3. Same landing: a blank line added to `ph16`'s NOTES SPLIT a unit in two and
     the first half lost the bare `C` that XLANG was matching.

In (2) and (3) the manager was editing the very finding about the ratchet.
Net was +1; THREE had actually arrived.

▶ **ADJUDICATE THE SET, BY UNIT TEXT, NEVER THE NUMBER.**  Line numbers move
under every edit, so a line-keyed diff cannot do this either.

⚠ This READS ONLY.  It writes nothing and runs no build."""
import importlib.util, os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "cb", os.path.join(ROOT, ".tasks-php", "cbaseline_check.py"))
cb = importlib.util.module_from_spec(spec); spec.loader.exec_module(cb)

def hitset(getter):
    out = {}
    for p in cb.SCAN:
        rel = os.path.relpath(p, ROOT)
        txt = getter(rel)
        if txt is None:
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                         encoding="utf-8") as f:
            f.write(txt); tmp = f.name
        for n, u in cb.units(tmp):
            if cb.MAG.search(u) and cb.XLANG.search(u) and not cb.BASE.search(u):
                out.setdefault(rel, []).append(" ".join(u.split())[:160])
        os.unlink(tmp)
    return out

REF = next((a for a in sys.argv[1:] if not a.startswith("-")), "HEAD")


def at_ref(rel):
    r = subprocess.run(["git", "-C", ROOT, "show", f"{REF}:{rel}"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None

def at_work(rel):
    p = os.path.join(ROOT, rel)
    return open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else None

def selftest():
    """MUST-FIRE: the diff must see a unit that gains a BASE spelling, and one
    that is SPLIT by a blank line -- instances (2) and (3) above."""
    base = "A says C is +33.01 % DEARER than safe_naive."
    fails = []

    def arm(name, ok):
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
        if not ok:
            fails.append(name)

    def scores(u):
        return bool(cb.MAG.search(u) and cb.XLANG.search(u)
                    and not cb.BASE.search(u))

    arm("1 the model unit hits at all", scores(base))
    arm("2 MUST-FIRE: adding `c-gcc` to the SAME unit silences it",
        not scores(base + " Measured on c-gcc."))
    arm("3 MUST-FIRE: a blank line SPLITS it and the C half loses MAG",
        not scores(base.split(" is ")[0]) or not scores("+33.01 % DEARER"))
    arm("4 must-NOT-fire: appending an unrelated paragraph-internal line keeps "
        "the hit", scores(base + "\nStill the same unit."))
    print(f"\n{4 - len(fails)} of 4 arms as expected")
    return 1 if fails else 0


if "--selftest" in sys.argv:
    raise SystemExit(selftest())

H, W = hitset(at_ref), hitset(at_work)
for rel in sorted(set(H) | set(W)):
    h, w = H.get(rel, []), W.get(rel, [])
    new = [x for x in w if x not in h]
    gone = [x for x in h if x not in w]
    if new or gone:
        print(f"\n=== {rel}   HEAD {len(h)} -> WORK {len(w)}")
        for x in new:  print("  NEW  |", x)
        for x in gone: print("  GONE |", x)
print(f"\nTOTAL HEAD {sum(len(v) for v in H.values())} -> WORK {sum(len(v) for v in W.values())}")
