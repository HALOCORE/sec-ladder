#!/usr/bin/env python3
"""TASK_PHP_050 §1.1 -- render the item-112 sweep table from the JSONs that
`php50_align_sweep.py` wrote under `.temp/php50/`.

    python3 .tasks-php/php50_table.py

⚠ Pure rendering. It measures nothing and decides nothing; every figure it
prints came out of a `sw_*.json` / `ph64_full.json` produced by the sweep, and
the column names say which field. **`|d|/step` is `|median delta| / (the sweep
range of that same delta)`** -- the pair's OWN observed step, never `ph55`'s
borrowed.
"""

import glob
import importlib.util
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, ".temp", "php50")

#: ⭐ Verdicts are RECOMPUTED from each record's raw `sweep` arrays rather than
#: read out of its stored `verdicts` block, so a correction to the verdict
#: function (the `SIGN-ZERO` arm `ph52` forced) applies to data already
#: collected WITHOUT re-running 10 000 callgrind invocations. The stored block
#: is left in the JSON as the as-measured record.
_spec = importlib.util.spec_from_file_location(
    "php50_sweep", os.path.join(ROOT, ".tasks-php", "php50_align_sweep.py"))
SW = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SW)

#: which rows PUBLISH a family-B difference in their NOTES.md (grep for
#: `marginal_ir_per_call` / `family B`), so the table can mark them.
PUBLISHES_B = {"ph52", "ph53", "ph55", "ph64"}


def load():
    out = {}
    for f in sorted(glob.glob(os.path.join(D, "sw_*.json"))) + \
            sorted(glob.glob(os.path.join(D, "ph64_full.json"))):
        out.update(json.load(open(f)))
    return out


def main():
    data = load()
    print("#### Per-CELL measured step (Ir/call), -O3 isolated, 32 pads = a full "
          "32-byte period\n")
    cells = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
             "safe_naive", "safe_tuned", "unsafe", "verus"]
    print("| row / input | pub B? | " + " | ".join(cells) + " |")
    print("|---|---|" + "---|" * len(cells))
    for k in sorted(data):
        row = k.split("/")[0].split("-")[0]
        s = data[k]["steps"]
        mark = "**yes**" if row in PUBLISHES_B else "no"
        print(f"| `{k}` | {mark} | " +
              " | ".join(("**%.2f**" % s[c]) if s.get(c) else
                         ("%.2f" % s[c] if c in s else "n/a") for c in cells) +
              " |")
    print("\n#### Every family-B difference, against its OWN measured step\n")
    print("| row / input | pair | median Ir/call | sweep range | `|d|/step` | "
          "magnitude | sign |")
    print("|---|---|---:|---:|---:|---|---|")
    flagged = []
    for k in sorted(data):
        fresh = SW.verdicts(data[k]["sweep"])
        for pair, v in sorted(fresh.items()):
            mid, rng, mag, sign, ratio = v
            if mid is None:
                continue
            r = "n/a (step 0)" if ratio is None else f"{ratio:.2f}"
            flag = ""
            if ratio is not None and ratio < 3.0:
                flag = " ⛔"
                flagged.append((k, pair, mid, rng, ratio, mag, sign))
            print(f"| `{k}` | `{pair}` | {mid:.2f} | {rng:.2f} | {r}{flag} | "
                  f"{mag} | {sign} |")
    print(f"\n#### ⛔ FLAGGED: `|d|/step` under 3x -- {len(flagged)} of "
          f"{sum(len(data[k]['verdicts']) for k in data)} pairs\n")
    for k, pair, mid, rng, ratio, mag, sign in flagged:
        print(f"* `{k}` `{pair}` -- median **{mid:.2f}** Ir/call against a "
              f"**{rng:.2f}** Ir/call step, ratio **{ratio:.2f}x** -- "
              f"**{mag} / {sign}**")
    if not flagged:
        print("*(none)*")
    print("\n#### Rows where NO cell moved at all (step 0 everywhere)\n")
    for k in sorted(data):
        if all((v or 0) == 0 for v in data[k]["steps"].values()):
            print(f"* `{k}`")


if __name__ == "__main__":
    main()
