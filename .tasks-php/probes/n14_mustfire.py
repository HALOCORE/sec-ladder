"""Show that task_cost.py's N14 CAN FAIL -- PROTOCOL_PHP §H / F10.

An arm that passes is not an arm that works. N14 exists for ONE state that no
other arm can see, and this reproduces it:

  (a) ⭐ THE STATE N14 IS FOR: a row is GATED, its build tasks ARE classified
      (as PENDING, which is what an in-flight build is), and `ROWS` was never
      extended when the row landed. `N1` sees every task classified and passes.
      `spread()` raises no KeyError because PENDING charges no row. So every
      published rate silently divides by too small a denominator -- in the
      FORGIVING direction.
  (b) ROWS phantom -- a row in `ROWS` with no gate record (item 114's shape:
      a directory, or a name, that is not a built row).

  ⓘ The variant "ROWS stale AND the row's tasks charge to it by name" is NOT
    modelled, because it does not need an arm: `spread()` raises `KeyError` and
    the tool stops. A crash is already a must-fire negative.

    python3 .tasks-php/probes/n14_mustfire.py

================================================================================
⛔⛔ THIS PROBE WAS ABSOLUTE AND IT HAD TO BECOME DIFFERENTIAL. READ THIS BEFORE
EDITING IT.
================================================================================

The first version asserted **`control PASSES, (a) FAILS, (b) FAILS`** -- verdicts
in absolute terms. That works only while the tree is CLEAN, and the very first
time a real `N14` defect went live it broke:

    control                      FAIL  ... missing ['ph97']
    (a) ROWS STALE, ph56 removed FAIL  ... missing ['ph56', 'ph97']
    (b) ROWS PHANTOM             FAIL  ... missing ['ph97'], phantom ['ph99']

⭐⭐ Every arm "failed", so the probe reported `FAIL` and **could no longer
distinguish its own planted defect from the real one** -- in (a) the two appear
in a single sorted list. **A must-fire demonstration that only works when nothing
is wrong is useless exactly when it matters**, which is `RECAP_PHP.md` F49's
shape and item 114's: *it agreed with the truth for as long as the state that
would separate them had never occurred.* ⓘ Found by `TASK_PHP_056`'s engineer,
not by the manager who wrote it, within hours of it landing.

▶ **THE REPAIR IS THE ONE F73's DETECTOR USES: ask whether the MUTATION CHANGES
THE ANSWER, not what the answer is.** Each arm now asserts the mutation moves
`N14`'s own reported sets by EXACTLY the planted row, relative to whatever the
baseline happens to be. ⭐ That is strictly stronger than the absolute form --
it proves the arm RESPONDS to the defect rather than merely being red near one
-- and it holds with a real defect live, which is when a probe earns its keep.
"""
import io, re, sys, contextlib, importlib.util, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location(
    "tc", os.path.join(ROOT, ".tasks-php", "task_cost.py"))
tc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tc)
os.chdir(ROOT)

BASE_ROWS, BASE_CLASS = list(tc.ROWS), dict(tc.CLASS)

# N14's ⓘ line, which reports the two sets whatever its verdict is. Parsing that
# rather than the PASS/FAIL word is what makes this differential.
_INFO = re.compile(r"missing from ROWS = (.+?) · in ROWS but not gated = (.+?)$")


def _parse(tok):
    """`['ph56', 'ph97']` or `none` -> a set."""
    tok = tok.strip()
    return set() if tok == "none" else set(re.findall(r"ph\d+", tok))


def run(label, rows, cls):
    """-> (missing, phantom, verdict_word). Prints what N14 said."""
    tc.ROWS, tc.CLASS = rows, cls
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            tc.selftest()
        except Exception as e:
            buf.write(f"\n(raised {type(e).__name__}: {e})\n")
    out = buf.getvalue()
    info = [l for l in out.splitlines() if "N14:" in l and l.lstrip().startswith("ⓘ")]
    hits = [l for l in out.splitlines()
            if "N14" in l and l.strip().startswith(("PASS", "FAIL"))]
    print(f"--- {label} ---")
    print("\n".join(hits) or "  (N14 did not run -- an earlier arm raised)")
    if not info:
        return None, None, None
    m = _INFO.search(info[0])
    word = hits[0].strip().split()[0] if hits else None
    return _parse(m.group(1)), _parse(m.group(2)), word


base_missing, base_phantom, base_word = run(
    "baseline: ROWS and CLASS as shipped", BASE_ROWS, BASE_CLASS)

# (a) ph56 is gated; pretend ROWS was never extended and its two build tasks are
#     still carried as PENDING, the way _056 was carried for ph97 in flight.
a_missing, a_phantom, a_word = run(
    "(a) ROWS STALE -- ph56 gated, tasks PENDING, ROWS not extended",
    [r for r in BASE_ROWS if r != "ph56"],
    dict(BASE_CLASS, **{"051": "PENDING", "052": "PENDING"}))

b_missing, b_phantom, b_word = run(
    "(b) ROWS PHANTOM -- ph99 in ROWS with no gate record",
    BASE_ROWS + ["ph99"], BASE_CLASS)

print()
if base_missing is None or a_missing is None or b_missing is None:
    print("N14 MUST-FIRE DEMONSTRATION: FAIL (N14 did not run in some arm)")
    sys.exit(1)

checks = [
    # ⭐ The differential assertions. Each says the MUTATION moved N14's own sets
    #   by exactly the planted row, whatever the baseline was.
    ("(a) adds exactly ph56 to `missing`",
     a_missing - base_missing == {"ph56"}),
    ("(a) disturbs no phantom",
     a_phantom == base_phantom),
    ("(b) adds exactly ph99 to `phantom`",
     b_phantom - base_phantom == {"ph99"}),
    ("(b) disturbs no missing",
     b_missing == base_missing),
    # ⛔ And the arm must still be capable of the VERDICT word, or a differential
    #   probe would pass over an N14 that computes correctly and never fails.
    ("both mutations produce a FAIL verdict",
     a_word == "FAIL" and b_word == "FAIL"),
]
for label, ok in checks:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}")

if base_word != "PASS":
    print(f"\n  ⓘ BASELINE IS CURRENTLY **{base_word}** -- there is a REAL N14 "
          f"defect live (missing={sorted(base_missing) or 'none'}, "
          f"phantom={sorted(base_phantom) or 'none'}). ⭐ This probe is "
          f"DIFFERENTIAL, so it still means something; the absolute version it "
          f"replaced did not. Fix the real defect separately -- this probe is "
          f"not the place, and going green here is not going green there.")

good = all(ok for _, ok in checks)
print()
print("N14 MUST-FIRE DEMONSTRATION:", "PASS" if good else "FAIL")
sys.exit(0 if good else 1)
