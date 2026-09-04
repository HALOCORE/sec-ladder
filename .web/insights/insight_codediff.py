#!/usr/bin/env python3
"""insight_codediff.py — script-guarded notes for the rung-to-rung diffs.

    python3 insights/insight_codediff.py            # write data/insights/codediff.json
    python3 insights/insight_codediff.py --print    # show every guard's verdict
    python3 insights/insight_codediff.py --check    # verify only; write nothing

THE MECHANISM, which is the point of this file.

A note about a diff is an interpretation, and interpretations rot.  The research
tree above this directory is under active work, and a sentence that was true when
written can be quietly falsified by the next pattern that lands.  So no note here
is a free-standing string: each is ATTACHED TO ASSERTIONS about the live
evidence, and is emitted only if every one of its guards still holds.

When a guard fails, the note is withheld and this script exits non-zero, naming
the note and the reason.  `build_data.py` runs it on every rebuild and turns that
into a warning, which the Method tab renders — so a stale claim announces itself
on the site instead of sitting there being wrong.

That is deliberately the opposite of the usual failure mode.  A hard-coded
sentence stays confidently wrong forever; a guarded one stops being displayed the
moment its evidence moves, and tells you which sentence to go and rewrite.

WHAT A GUARD SHOULD ASSERT: the specific fact the note's claim rests on, read
from `results/`, `results/gate/` or the pattern's own source.  `data/code/` is
allowed because it is the exact text the page renders and the claim is often
about that text — but never read a number from `.web/data/` and call it
evidence, because build_data.py derived it from the same place the note did.

A guard is `f(ev, pid) -> (ok: bool, why: str)`.  `why` is reported either way,
so `--print` doubles as a description of what is currently believed and why.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
REPO = os.path.dirname(WEB)


# --------------------------------------------------------------- evidence ---

class Evidence:
    """Read-only accessors over the research tree. Nothing here writes."""

    def __init__(self):
        self._gate, self._code = {}, {}

    def gate(self, pid):
        if pid not in self._gate:
            p = os.path.join(REPO, "results", "gate", pid + ".json")
            self._gate[pid] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
        return self._gate[pid]

    def code(self, pid):
        """The sliced kernel text per cell — exactly what the page renders."""
        if pid not in self._code:
            p = os.path.join(WEB, "data", "code", pid + ".json")
            self._code[pid] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
        return self._code[pid]

    def source(self, rel):
        p = os.path.join(REPO, rel)
        return open(p, encoding="utf-8").read() if os.path.exists(p) else None

    def patterns(self):
        d = os.path.join(WEB, "data", "code")
        return sorted(f[:-5] for f in os.listdir(d) if f.endswith(".json")) if os.path.isdir(d) else []


# ------------------------------------------------------------------ guards ---

def kernels_identical(*cells):
    """Every named cell's kernel slice is byte-identical."""
    def g(ev, pid):
        c = ev.code(pid)
        if not c:
            return False, f"no code data for {pid}"
        texts = []
        for cell in cells:
            if cell not in c:
                return False, f"{pid} has no {cell} rung"
            texts.append(c[cell]["text"])
        if len(set(texts)) != 1:
            return False, f"{' / '.join(cells)} kernel slices are NO LONGER identical"
        return True, f"{len(cells)} cells share one {len(texts[0])}-byte kernel slice"
    return g


def cell_absent(cell):
    def g(ev, pid):
        c = ev.code(pid)
        if not c:
            return False, f"no code data for {pid}"
        if cell in c:
            return False, f"{pid} now HAS a {cell} rung — the note saying it does not is stale"
        return True, f"no {cell} rung, as the note says"
    return g


def identity_exact_at_o3():
    """The gate measured R4 and R5 as byte-identical kernels at -O3."""
    def g(ev, pid):
        rec = ev.gate(pid)
        if not rec:
            return False, f"no gate record for {pid}"
        rows = [r for r in (rec.get("identity") or [])
                if r.get("opt") == "O3" and "unsafe" in str(r.get("pair", ""))]
        if not rows:
            return False, "gate record has no O3 unsafe-vs-verus identity row"
        bad = [r for r in rows if r.get("md5_fn_a") != r.get("md5_fn_b")]
        if bad:
            return False, ("R4 and R5 kernels are NOT byte-identical at O3 "
                           f"({str(bad[0].get('md5_fn_a'))[:8]} vs {str(bad[0].get('md5_fn_b'))[:8]})"
                           " — the zero-cost claim does not hold for this pattern")
        return True, f"R4/R5 kernel md5 equal at O3 ({rows[0]['md5_fn_a'][:8]})"
    return g


def source_contains(rel, needle):
    def g(ev, pid):
        path = rel.replace("{pid}", pid)
        txt = ev.source(path)
        if txt is None:
            return False, f"{path} does not exist"
        if needle not in txt:
            return False, f"{path} no longer contains {needle!r}"
        return True, f"{os.path.basename(path)} still says {needle!r}"
    return g


# ------------------------------------------------------------------- notes ---
# `pattern=None` broadcasts the note to every pattern whose guards pass — that is
# how the R4->R5 note covers all 23 without being restated 23 times.  A note with
# a named pattern MUST hold: if its guards fail, that is drift and the script
# exits 1.  A broadcast note simply does not apply where its guards fail, which
# is not an error — it is the note correctly declining to make a claim.

NOTES = [
    dict(
        pattern="p08-overlap-move", diff="r2-r3",
        title="On p08 the safe and tuned rungs are one kernel.",
        body=[
            "The kernel slices for **safe Rust naive** and **safe Rust tuned** are byte-identical here, so this diff is empty by measurement rather than by omission. The same holds one rung further up — see the R3 → R4 diff.",
            "p08's README gives the reason there is no Rust spelling to vary: the bug this pattern models is an overlapping copy, and *\"`&[u8]` and `&mut [u8]` into one buffer at once is `E0502`\"*. Safe Rust cannot express it, so there is no check to hoist and no idiom to trade.",
        ],
        guards=[
            kernels_identical("safe_naive", "safe_tuned"),
            source_contains("patterns/{pid}/README.md", "E0502"),
        ],
    ),
    dict(
        pattern="p08-overlap-move", diff="r3-r4",
        title="And the unsafe rung is that same kernel again.",
        body=[
            "All three Rust rungs on p08 — naive, tuned and unsafe — ship one byte-identical kernel. It is the only pattern in the tree where the ladder's Rust half collapses to a single program.",
            "That is p08's result rather than a hole in it. The pattern exists to show a bug **safe Rust cannot express at all**, at a cost its README records as *\"zero: the program does not compile\"*. Where every other pattern prices a runtime check, this one prices a compile-time refusal — so the Rust rungs have nothing to differ about, and the diff worth reading on p08 is the C one.",
        ],
        guards=[
            kernels_identical("safe_naive", "safe_tuned", "unsafe"),
            source_contains("patterns/{pid}/README.md", "the program does not compile"),
        ],
    ),
    dict(
        pattern="p01-array-sum", diff="c-check",
        title="p01 has no hardened C rung, so there is no check to diff.",
        body=[
            "p01 is the calibration pattern: it **models no bug**. Its job is to prove the harness, the driver, the input format and all five rungs work, and to give every later pattern a baseline to be compared against. With no modelled bug there is no missing check, and so no hardened C cell to compare against.",
            "Every other pattern in the tree has one.",
        ],
        guards=[cell_absent("c-gcc-h")],
    ),
    dict(
        pattern=None, diff="r4-r5",
        title="Every line added here compiles to nothing.",
        body=[
            "The gate measured this pattern's **R4 and R5 kernels as byte-identical machine code at `-O3`** — one md5 over the raw bytes of the kernel symbol, not over a normalised disassembly. So the whole of this diff is ghost: `requires`, `ensures`, `invariant`, `decreases`, every `proof` block and lemma, all erased before codegen.",
            "That is this project's finding 1, and it is why the proof's cost is not measured in instructions. What it costs instead is a **trusted base** — the `external_body` bodies highlighted in the R5 source, whose bodies are taken on faith and counted per pattern on the proof tab.",
        ],
        guards=[identity_exact_at_o3()],
    ),
]


# ------------------------------------------------------------------- build ---

def build(ev):
    out, passes, failures = {}, [], []
    for note in NOTES:
        broadcast = note["pattern"] is None
        targets = ev.patterns() if broadcast else [note["pattern"]]
        for pid in targets:
            reasons, ok = [], True
            for guard in note["guards"]:
                try:
                    good, why = guard(ev, pid)
                except Exception as exc:               # a broken guard is a failed guard
                    good, why = False, f"guard raised: {exc}"
                reasons.append((good, why))
                ok = ok and good
            label = f"{pid}/{note['diff']}"
            if ok:
                # a list, not a single note: a broadcast caveat and a
                # pattern-specific finding can both apply to the same diff, and
                # the specific one must not silently replace the general one
                out.setdefault(pid, {}).setdefault(note["diff"], []).append({
                    "title": note["title"], "body": note["body"],
                })
                passes.append((label, [w for _, w in reasons]))
            elif not broadcast:
                failures.append((label, [w for g, w in reasons if not g]))
            else:
                pass                                   # broadcast note declining to apply
    return out, passes, failures


def main():
    argv = sys.argv[1:]
    verbose = "--print" in argv or "--check" in argv
    ev = Evidence()
    out, passes, failures = build(ev)

    if verbose:
        for label, whys in passes:
            print(f"  ok    {label}")
            for w in whys:
                print(f"          {w}")
    for label, whys in failures:
        print(f"  STALE {label}", file=sys.stderr)
        for w in whys:
            print(f"          {w}", file=sys.stderr)

    if "--check" not in argv and "--print" not in argv:
        dest = os.path.join(WEB, "data", "insights")
        os.makedirs(dest, exist_ok=True)
        with open(os.path.join(dest, "codediff.json"), "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)

    n = sum(len(x) for v in out.values() for x in v.values())
    msg = f"insight_codediff: {n} note(s) over {len(out)} pattern(s)"
    if failures:
        msg += f", {len(failures)} STALE"
    print(msg, file=sys.stderr if failures else sys.stdout)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
