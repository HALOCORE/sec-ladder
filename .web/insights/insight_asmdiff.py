#!/usr/bin/env python3
"""insight_asmdiff.py — script-guarded notes for the ASSEMBLY diffs.

    python3 insights/insight_asmdiff.py            # write data/insights/asmdiff.json
    python3 insights/insight_asmdiff.py --print    # every guard's verdict
    python3 insights/insight_asmdiff.py --check    # verify only, write nothing

Same mechanism as insight_codediff.py: a note is emitted only while its
assertions hold, a failure withholds it and exits non-zero, and build_data.py
turns that into a warning the Method tab renders.  See CLAUDE.md.

ON GUARDING AGAINST `asmcache/`: it is derived, which normally disqualifies a
source of evidence here.  It is allowed for these notes because the claims ARE
claims about the cached diff, and because the cache is itself digest-checked
against `results/` before anything is published — build_data.py drops any diff
whose `md5_fn` no longer matches the measured cell.  A note about the assembly
therefore rests on the same digests the gate does.  Numbers that are not about
the diff still come from `results/`.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
REPO = os.path.dirname(WEB)


class Evidence:
    def __init__(self):
        self._asm, self._gate = {}, {}

    def asm(self, pid):
        if pid not in self._asm:
            p = os.path.join(WEB, "asmcache", pid + ".json")
            self._asm[pid] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
        return self._asm[pid]

    def gate(self, pid):
        if pid not in self._gate:
            p = os.path.join(REPO, "results", "gate", pid + ".json")
            self._gate[pid] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
        return self._gate[pid]

    def source(self, rel):
        p = os.path.join(REPO, rel)
        return open(p, encoding="utf-8").read() if os.path.exists(p) else None

    def patterns(self):
        d = os.path.join(WEB, "asmcache")
        return sorted(f[:-5] for f in os.listdir(d) if f.endswith(".json")) if os.path.isdir(d) else []

    def pair(self, pid, pair_id, opt="O3"):
        a = self.asm(pid)
        return ((a or {}).get("pairs", {}).get(pair_id) or {}).get(opt)


# ------------------------------------------------------------------ guards ---

def asm_removed_spread(pair_id, min_ratio):
    """Across every pattern, the instructions removed by this transition vary by
    at least `min_ratio`x. This is what makes 'the diff is the check' false."""
    def g(ev, pid):
        vals = []
        for p in ev.patterns():
            d = ev.pair(p, pair_id)
            if d:
                vals.append((d["removed"], p))
        if len(vals) < 5:
            return False, f"only {len(vals)} patterns have a {pair_id} assembly diff"
        lo, hi = min(vals), max(vals)
        if lo[0] == 0:
            return False, f"{lo[1]} removes 0 instructions — ratio undefined"
        ratio = hi[0] / lo[0]
        if ratio < min_ratio:
            return False, (f"removed-instruction spread is only {ratio:.1f}x "
                           f"({lo[0]} on {lo[1]} to {hi[0]} on {hi[1]}) — the note claims "
                           f"at least {min_ratio}x and should be rewritten")
        return True, (f"spread {ratio:.0f}x: {lo[0]} instructions on {lo[1]}, "
                      f"{hi[0]} on {hi[1]}, over {len(vals)} patterns")
    return g


def asm_identical(pair_id, opt="O3"):
    def g(ev, pid):
        d = ev.pair(pid, pair_id, opt)
        if not d:
            return False, f"no {pair_id} assembly diff at {opt}"
        if d["added"] or d["removed"]:
            return False, (f"{pair_id} at {opt} now differs by +{d['added']}/-{d['removed']} "
                           "instructions — the zero-cost claim does not hold here")
        if d.get("identity_level") != "exact":
            return False, f"{pair_id} at {opt} is level={d.get('identity_level')}, not exact"
        return True, f"{pair_id} at {opt}: 0 instructions differ, level=exact"
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


def insn_counts(pair_id, a_min, b_max, opt="O3"):
    """This pattern's two kernels are the sizes the note quotes."""
    def g(ev, pid):
        d = ev.pair(pid, pair_id, opt)
        if not d:
            return False, f"no {pair_id} diff at {opt}"
        na, nb = d["a"]["n_fn"], d["b"]["n_fn"]
        if na < a_min or nb > b_max:
            return False, f"kernel sizes moved: {na} -> {nb} (note assumes >={a_min} -> <={b_max})"
        return True, f"{na} -> {nb} instructions"
    return g


# ------------------------------------------------------------------- notes ---

NOTES = [
    dict(
        pattern=None, pair="r3-r4",
        title="This is not a bill for the check.",
        body=[
            "It is tempting to read the deleted instructions as the price of safety. They are not. Removing the bounds check also changes what the optimiser can then do — how it unrolls, how it allocates registers, whether it vectorises — so the diff shows **everything downstream of the check as well as the check itself**.",
            "The evidence is the spread: across the patterns here the same transition removes anywhere from a handful of instructions to a couple of hundred, a range far too wide to be one check. Where a pattern's cost *has* been decomposed properly, the decomposition is on its own page and in the findings — and the honest per-call numbers are the `Ir` columns, not this instruction count.",
        ],
        guards=[asm_removed_spread("r3-r4", 8)],
    ),
    dict(
        pattern=None, pair="r4-r5",
        title="Zero instructions differ.",
        body=[
            "The source diff added the whole proof — every `requires`, `ensures`, `invariant`, `decreases`, every `proof` block and lemma — and **not one machine instruction changed**. The two kernels are byte-identical at `-O3`.",
            "This is the cleanest form of the project's finding 1. Switch to `-O0` and the digests stop matching, but the instruction stream still does not change: what differs there is pc-relative link addresses, which is an artefact of where the linker put things and not a cost.",
        ],
        guards=[asm_identical("r4-r5", "O3")],
    ),
    dict(
        pattern="p03-bounded-stack", pair="r3-r4",
        title="On p03 the removed instructions are recoverable — in safe Rust.",
        body=[
            "The check LLVM emits here is deletable without leaving the safe language. Handing the optimiser the proof's own invariant as a dead clamp removes it, and p03's README records that this is **not a fact about Rust**: give the C rung the same manual check and clang keeps it *\"at 4.00000 Ir per executed pop exactly\"*, hand either the identical clamp and *\"both delete 100% of it, byte-identically\"*.",
            "Two independent middle-ends, and gcc shares none with rustc. So what this diff shows is analysis **seeding** — the optimiser can prove the fact once it is told it — rather than a cost that safety necessarily carries.",
        ],
        guards=[
            source_contains("patterns/{pid}/README.md", "both delete 100% of it"),
            insn_counts("r3-r4", 60, 120),
        ],
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
                except Exception as exc:
                    good, why = False, f"guard raised: {exc}"
                reasons.append((good, why))
                ok = ok and good
            label = f"{pid}/{note['pair']}"
            if ok:
                # a list, not a single note: a broadcast caveat and a
                # pattern-specific finding can both apply to the same diff, and
                # the specific one must not silently replace the general one
                out.setdefault(pid, {}).setdefault(note["pair"], []).append({
                    "title": note["title"], "body": note["body"],
                })
                passes.append((label, [w for _, w in reasons]))
            elif not broadcast:
                failures.append((label, [w for g, w in reasons if not g]))
    return out, passes, failures


def main():
    argv = sys.argv[1:]
    verbose = "--print" in argv or "--check" in argv
    ev = Evidence()
    out, passes, failures = build(ev)

    if verbose:
        seen = set()
        for label, whys in passes:
            # the broadcast notes repeat their reason per pattern; show once
            key = tuple(whys)
            if key in seen:
                continue
            seen.add(key)
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
        with open(os.path.join(dest, "asmdiff.json"), "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)

    n = sum(len(x) for v in out.values() for x in v.values())
    msg = f"insight_asmdiff: {n} note(s) over {len(out)} pattern(s)"
    if failures:
        msg += f", {len(failures)} STALE"
    print(msg, file=sys.stderr if failures else sys.stdout)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
