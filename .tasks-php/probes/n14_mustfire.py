"""Show that task_cost.py's N14 CAN FAIL -- PROTOCOL_PHP §H / F10.

An arm that passes is not an arm that works. N14 exists for ONE state that no
other arm can see, and this reproduces it:

  (a) ⭐ THE STATE N14 IS FOR: a row is GATED, its build tasks ARE classified
      (as PENDING, which is what an in-flight build is), and `ROWS` was never
      extended when the row landed. `N1` sees every task classified and passes.
      `spread()` raises no KeyError because PENDING charges no row. So every
      published rate silently divides by too small a denominator -- in the
      FORGIVING direction. This is the exact future state of `ph97`/`_056`.
  (b) ROWS phantom -- a row in `ROWS` with no gate record (item 114's shape:
      a directory, or a name, that is not a built row).

  ⓘ The variant "ROWS stale AND the row's tasks charge to it by name" is NOT
    modelled, because it does not need an arm: `spread()` raises `KeyError` and
    the tool stops. A crash is already a must-fire negative.

    python3 .tasks-php/probes/n14_mustfire.py
"""
import io, sys, contextlib, importlib.util, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location(
    "tc", os.path.join(ROOT, ".tasks-php", "task_cost.py"))
tc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tc)
os.chdir(ROOT)

BASE_ROWS, BASE_CLASS = list(tc.ROWS), dict(tc.CLASS)

def run(label, rows, cls):
    tc.ROWS, tc.CLASS = rows, cls
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            tc.selftest()
        except Exception as e:
            buf.write(f"\n(raised {type(e).__name__}: {e})\n")
    out = buf.getvalue()
    hits = [l for l in out.splitlines()
            if "N14" in l and l.strip().startswith(("PASS", "FAIL"))]
    print(f"--- {label} ---")
    print("\n".join(hits) or "  (N14 did not run -- an earlier arm raised)")
    return hits

def verdict(hits, want):
    return any(l.strip().startswith(want) for l in hits)

ok = run("control: ROWS and CLASS as shipped", BASE_ROWS, BASE_CLASS)

# (a) ph56 is gated; pretend ROWS was never extended and its two build tasks are
#     still carried as PENDING, the way _056 is carried for ph97 right now.
stale_cls = dict(BASE_CLASS, **{"051": "PENDING", "052": "PENDING"})
stale = run("(a) ROWS STALE -- ph56 gated, tasks PENDING, ROWS not extended",
            [r for r in BASE_ROWS if r != "ph56"], stale_cls)

phant = run("(b) ROWS PHANTOM -- ph99 in ROWS with no gate record",
            BASE_ROWS + ["ph99"], BASE_CLASS)

good = (verdict(ok, "PASS") and verdict(stale, "FAIL") and verdict(phant, "FAIL"))
print()
print("N14 MUST-FIRE DEMONSTRATION:", "PASS" if good else "FAIL")
sys.exit(0 if good else 1)
