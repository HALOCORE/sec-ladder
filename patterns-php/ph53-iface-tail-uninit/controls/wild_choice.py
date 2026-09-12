#!/usr/bin/env python3
"""ph53 control driver: build and drive `controls/wild_choice.c`, with the
negatives that make it a check rather than a printout.

    python3 patterns-php/ph53-iface-tail-uninit/controls/wild_choice.py
    python3 .../wild_choice.py --selftest --reps 5

Read `controls/wild_choice.c`'s header first: it CHOOSES the value the
unwritten interface slot holds, by priming PHP 5.0.0's own size-class cache
(`zend_alloc.c:150-168`, `:263-279`) with a known payload and letting
`zend_compile.c:2571`'s `erealloc` pick the block straight back up.
`PROTOCOL_PHP.md` §H and `TASK_PHP_041.md` §3.5: *a control needs a chosen
value.*

⭐⭐ **THE RESULT, AND IT IS SHARPER THAN "R1h GIVES A CORRECT NO-MATCH".**
With the value chosen rather than observed, `d09cdd9f71f3` is **COMPLETE on the
comparing consumer and USELESS on the dereferencing one** — and on the
dereferencing one it makes things *differently* bad rather than better: R1 with
a plausible wild pointer returns a **silent wrong answer**, and R1h **always
dies**. An integrity bug becomes a guaranteed availability bug.

The negatives:

    C1 MUST-FIRE     R1 primed with &pool[3], target pool[3]: the COMPARE-ONLY
                     consumer must MATCH AN UNWRITTEN SLOT (stop == 1). That is
                     a silent wrong answer from the consumer that does not
                     dereference, and `controls/r1h_consumers.py` cannot show
                     it because there the unprimed garbage happened not to match
    C2 MUST-FIRE     changing the priming to &pool[5] must CHANGE the answer.
                     Without this the value could still be observed rather than
                     chosen, and C1 would be an accident
    C3 MUST-NOT-FIRE R1h must answer CORRECTLY (stop == 2) under BOTH primings
                     -- the memset makes the block's history irrelevant, which
                     is the whole of what the fix buys
    C4 MUST-FIRE     R1h's dereferencing consumer must DIE with SIGSEGV under
                     both primings. Silence here would mean the fix removed the
                     fault, which is the claim this row exists to refute
    C5 MUST-NOT-FIRE R1's dereferencing consumer, given a chosen VALID pool
                     address, must NOT die -- a wild dereference that lands on
                     live memory is a wrong answer and not a crash, and that
                     asymmetry is why the row ships two consumers
    C6 MUST-NOT-FIRE every line must be byte-identical across `--reps` runs.
                     A "chosen" value that moves between runs was observed
"""

import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
OUT = os.path.join(REPO, ".temp", "php41", "controls")
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")

ROW_RE = re.compile(
    r"primed with &pool\[(\d)\]\s+cmp_scan=(\d+) \((.*?)\)\s+"
    r"deref (?:hit=(\d) id=([0-9a-f]+)|DIED signal=(\d+))")


def build():
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "wild_choice")
    cmd = [CLANG, "-std=c99", "-O1", "-Wall", "-Wextra",
           "-I", os.path.join(REPO, "common-php"),
           "-o", out, os.path.join(HERE, "wild_choice.c")]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"BUILD FAILED:\n{r.stdout}{r.stderr}")
    if r.stderr.strip():
        print("  (compiler diagnostics)")
        print("    " + r.stderr.strip().replace("\n", "\n    "))
    return out


def parse(text):
    """[(arm, chosen, stop, verdict, hit, id, signal)] in file order, where
    `arm` is 'R1' before the R1h header and 'R1h' after it."""
    rows, arm = [], "R1"
    for line in text.split("\n"):
        if line.startswith("R1h "):
            arm = "R1h"
            continue
        m = ROW_RE.search(line)
        if m:
            rows.append((arm, int(m.group(1)), int(m.group(2)), m.group(3),
                         None if m.group(4) is None else int(m.group(4)),
                         m.group(5),
                         None if m.group(6) is None else int(m.group(6))))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--reps", type=int, default=5)
    a = ap.parse_args()

    binary = build()
    outs = []
    for _ in range(max(1, a.reps)):
        r = subprocess.run([binary], capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            raise SystemExit(f"probe exited {r.returncode}:\n{r.stdout}{r.stderr}")
        outs.append(r.stdout)
    print(outs[0], end="")

    if not a.selftest:
        return 0

    print("-- negatives (PROTOCOL_PHP.md H) " + "-" * 46)
    bad = []
    rows = parse(outs[0])
    if len(rows) != 4:
        raise SystemExit(f"expected 4 rows, parsed {len(rows)}: {rows}")
    by = {(arm, ch): r for r in rows for arm, ch in [(r[0], r[1])]}

    # C1
    r = by[("R1", 3)]
    if r[2] != 1:
        bad.append(f"C1: R1 primed with &pool[3] gave cmp_scan={r[2]}, want 1 "
                   f"(a MATCH on the unwritten slot). Without it the "
                   f"compare-only consumer looks harmless, and the row's claim "
                   f"that d09cdd9f71f3 buys something REAL there has no "
                   f"evidence")
    else:
        print("  ok   C1 MUST-FIRE: R1 matches an UNWRITTEN slot -- a silent "
              "wrong answer from the consumer that does not dereference")

    # C2
    if by[("R1", 3)][2] == by[("R1", 5)][2]:
        bad.append(f"C2: both primings gave cmp_scan={by[('R1', 3)][2]}, so the "
                   f"value is not demonstrably CHOSEN. The whole point of this "
                   f"probe over controls/r1h_consumers.py is that changing the "
                   f"priming changes the answer")
    else:
        print(f"  ok   C2 MUST-FIRE: the answer moves with the priming "
              f"({by[('R1', 3)][2]} vs {by[('R1', 5)][2]}) -- the value is "
              f"CHOSEN, not observed")

    # C3
    for ch in (3, 5):
        if by[("R1h", ch)][2] != 2:
            bad.append(f"C3: R1h primed with &pool[{ch}] gave "
                       f"cmp_scan={by[('R1h', ch)][2]}, want 2 (no match). The "
                       f"memset is supposed to make the block's history "
                       f"irrelevant")
    if not any(b.startswith("C3") for b in bad):
        print("  ok   C3 MUST-NOT-FIRE: R1h answers correctly under BOTH "
              "primings -- history is irrelevant once the block is zeroed")

    # C4
    for ch in (3, 5):
        if by[("R1h", ch)][6] != 11:
            bad.append(f"C4: R1h primed with &pool[{ch}]: the dereferencing "
                       f"consumer did NOT die with SIGSEGV (signal="
                       f"{by[('R1h', ch)][6]!r}, hit={by[('R1h', ch)][4]!r}). "
                       f"The row's headline is that the fix does NOT remove "
                       f"the fault, and this is where that is measured")
    if not any(b.startswith("C4") for b in bad):
        print("  ok   C4 MUST-FIRE: R1h's dereferencing consumer dies with "
              "SIGSEGV under both primings -- the NULL is deterministic and "
              "the fault survives the fix")

    # C5
    r = by[("R1", 3)]
    if r[6] is not None:
        bad.append(f"C5: R1's dereferencing consumer died (signal={r[6]}) on a "
                   f"CHOSEN VALID pool address. It should return a wrong "
                   f"ANSWER, not a crash -- that asymmetry between the two "
                   f"consumers is why the kernel ships both")
    elif r[4] != 1:
        bad.append(f"C5: R1's dereferencing consumer returned hit={r[4]}, want "
                   f"1 -- the chosen pointer names pool[3] and the target IS "
                   f"pool[3]")
    else:
        print(f"  ok   C5 MUST-NOT-FIRE: R1's wild dereference lands on live "
              f"memory and returns a WRONG ANSWER (id={r[5]}), not a crash")

    # C6
    if len(set(outs)) != 1:
        bad.append(f"C6: {len(set(outs))} distinct outputs over {a.reps} runs. "
                   f"A CHOSEN value does not move between runs; this one did, "
                   f"so the probe is observing something")
    else:
        print(f"  ok   C6 MUST-NOT-FIRE: byte-identical over {a.reps} runs")

    print()
    if bad:
        print("SELFTEST FAIL")
        for b in bad:
            print(f"    {b}")
        return 1
    print("SELFTEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
