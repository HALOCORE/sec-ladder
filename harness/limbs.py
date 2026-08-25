#!/usr/bin/env python3
"""Which `check.py` limb fires on a Verus MUTANT that is not in the tree?

**Not a gate stage.** `check.py` never imports this and must never be made to:
it is a reporting / reproduction tool, the way `common/layout/*.py` and each
pattern's `controls/*.py` are. It exists here rather than in `.temp/` because
six patterns' published `NOTES.md` sentences now rest on what it reports, and a
committed sentence may not cite a gitignored scratch file -- the trap
`patterns/p06-rotate/controls/clayout.py` exists to avoid. Landed at TASK_056
from `.temp/p54/limbs.py` (TASK_054, which measured the sole-catcher claim on
all 16 patterns with it).

⚠ **It is inside `source_sha256`.** `harness/*.py` is hashed into every gate
record, so editing this file makes all 16 records stale even though it decides
nothing. That coupling is deliberate: this file RE-DERIVES `check.py`'s own pin
comparison, so if `check.py`'s comparison moves and this does not, every
sentence citing it silently becomes wrong. The staleness is the alarm.

The eight limbs a `verus.rs` edit can trip, each named with the `check.py`
FUNCTION it re-derives. ⚠ **This table carried `check.py:<line>` ranges
"as of TASK_056" until TASK_096, and every one of them had rotted** -- the
range that opened it now lands inside `check_build`, not inside the pin
comparison it names. `.memory/02-bench-rules.md`'s convention is the FUNCTION
NAME and NO LINE NUMBER AT ALL; the "line as a hint" compromise was tried at
TASK_066 and retracted at TASK_071 after every hint rotted inside one session.

  5a-items   item set added/removed vs `verus.items`
                                          check.py::check_verus_contract
  5a-clause  per-item external/requires/ensures vs the pin
                                          check.py::check_verus_contract
  5a-obl     shipped-config `N verified` vs `verus.obligations`
                                          check.py::check_verus_contract
  5a-verify  shipped-config errors > 0    check.py::check_verus_contract
  5ct-sig    5c-twin LIMB (i): twin signature == the trusted item's
                                          check.py::check_trusted_twins
  5ct-cfg    twin `#[cfg(slb_twin)]` / in_verus / external / banned-word
             hygiene                      check.py::_check_twin_cfg_hygiene
                                          and check.py::check_trusted_twins
  5ct-run    5c-twin LIMB (ii): `--cfg slb_twin` errors > 0
                                          check.py::check_trusted_twins
  5ct-obl    `--cfg slb_twin` `N verified` vs `verus.twin_obligations`
                                          check.py::check_trusted_twins

**What it is FOR, and the rule it exists to make checkable.** TASK_054 measured
that every pattern's `spec.md` pins the clause text of the verified TWIN in
`verus.items` alongside the trusted item's, so the canonical weakening --
`i < v@.len()` -> `i <= v@.len()` in the item *and* its twin -- moves TWO pinned
clauses and fails stage 5a, which runs BEFORE 5c-twin. So:

  > "the twin is the sole catcher" is a claim about the MUTANT'S CONSTRUCTION,
  > not about the gate. The twin is the sole catcher only of a mutant that edits
  > `spec.md` in the same commit. Do not write "the pin does not move" -- run
  > this and check, because on every pattern on this project it does.

Usage:

    harness/limbs.py <pattern-dir> <verus-src-key> <mutant.rs> [...] [--no-verus]

`<verus-src-key>` is the key under `verus.items` in `spec.md` (normally
`verus.rs`). The two Verus runs per file are the slow part; `--no-verus` skips
them and reports the static limbs only.
"""
import json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'harness'))
import vparse

TWIN_PREFIX = "slb_twin_"
TWIN_CFG = "slb_twin"
TWIN_BANNED = ("unsafe", "assume", "admit", "assume_specification", "external")


def contract(pdir):
    txt = open(os.path.join(pdir, "spec.md")).read()
    m = re.search(r"```slb-contract\n(.*?)\n```", txt, re.S)
    return json.loads(m.group(1))


def clauses(it, kw):
    return [vparse.norm_clause(c) for c in (it.clauses.get(kw, []) if it else [])]


def is_trusted(it):
    """`check.py::_is_trusted`, imported rather than copied."""
    import check as _c
    return _c._is_trusted(it)


def verus(path, *extra):
    """`check.py::_verus`, re-derived -- INCLUDING its return-code rule.

    TASK_097. This was the third copy of a body that read the `N verified, M
    errors` summary and never read `subprocess.CompletedProcess.returncode`
    (TASK_096_REVIEW MAJOR 2 named all three). A file Verus verifies and rustc
    rejects -- `#[cfg(slb_twin)] fn slb_twin_read_i(..) { v.i }`, `2 verified,
    0 errors`, `error[E0133]`, exit 1 -- read as clean here too, so the
    `5ct-run` / `5a-verify` limbs this tool reports would have said the mutant
    passed them.

    Same narrow predicate as `check.py::_verus`, and for the same reason: this
    tool exists to run MUTANTS, most of which are supposed to exit non-zero, so
    only `summary parsed AND errors == 0 AND rc != 0` is an anomaly."""
    r = subprocess.run([sys.executable, os.path.join(REPO, "verus_run.py"), path,
                        *extra], capture_output=True, text=True, cwd=REPO,
                       timeout=1800)
    out = (r.stdout + r.stderr)
    m = re.search(r"(\d+) verified, (\d+) errors", out)
    if not m:
        return None, None, out
    nv, ne = int(m.group(1)), int(m.group(2))
    if ne == 0 and r.returncode != 0:
        return None, None, out + (
            f"\n\n[limbs.py::verus] SUMMARY SUPPRESSED: verus_run.py exited "
            f"{r.returncode} while reporting `{nv} verified, 0 errors` for "
            f"{os.path.relpath(path, REPO)} {list(extra)} -- Verus was "
            f"satisfied and the compiler was not, so no limb may be reported "
            f"as passing from this run.\n")
    return nv, ne, out


def main():
    pdir, src = sys.argv[1], sys.argv[2]
    files = [a for a in sys.argv[3:] if not a.startswith("-")]
    do_verus = "--no-verus" not in sys.argv
    c = contract(pdir)["verus"]
    want = c["items"][src]
    pin_obl = c["obligations"][src]
    pin_twin = (c.get("twin_obligations") or {}).get(src)

    for path in files:
        txt = open(path).read()
        items = vparse.by_name(txt)
        fired = {}

        got, wantset = set(items), set(want)
        if got != wantset:
            fired["5a-items"] = [f"added={sorted(got-wantset)} removed={sorted(wantset-got)}"]
        cd = []
        for name in sorted(got & wantset):
            w, it = want[name], items[name]
            if (it.external or None) != (w.get("external") or None):
                cd.append(f"{name}.external {it.external!r} != {w.get('external')!r}")
            for kw in ("requires", "ensures"):
                g, wc = clauses(it, kw), [vparse.norm_clause(x) for x in w.get(kw, [])]
                if g != wc:
                    cd.append(f"{name}.{kw} {g!r} != pinned {wc!r}")
        if cd:
            fired["5a-clause"] = cd

        # ---- 5c-twin limb (i) and the twin hygiene rules --------------------
        trusted = [i for i in items.values() if is_trusted(i)]
        sig, cfg = [], []
        for t in trusted:
            tw = items.get(TWIN_PREFIX + t.name)
            if tw is None:
                cfg.append(f"{t.name}: NO TWIN")
                continue
            gs, ts = vparse.norm_clause(tw.sig), vparse.norm_clause(t.sig)
            if gs != ts:
                sig.append(f"{tw.name} sig != {t.name} sig\n           twin:    {gs}\n           trusted: {ts}")
            if tw.external:
                cfg.append(f"{tw.name} is {tw.external}")
            if not tw.in_verus:
                cfg.append(f"{tw.name} outside verus!{{}}")
            if not any(re.fullmatch(r"#!?\[\s*cfg\s*\(\s*" + TWIN_CFG + r"\s*\)\s*\]",
                                    a.strip()) for a in tw.attrs):
                cfg.append(f"{tw.name} not #[cfg({TWIN_CFG})]")
            b = vparse.blank_noncode(tw.body or "")
            for w_ in TWIN_BANNED:
                if re.search(r"\b" + w_ + r"\b", b):
                    cfg.append(f"{tw.name} body contains `{w_}`")
        if sig:
            fired["5ct-sig"] = sig
        if cfg:
            fired["5ct-cfg"] = cfg

        nv = ne = tv = te = None
        if do_verus:
            nv, ne, o1 = verus(path)
            if ne:
                fired["5a-verify"] = [f"{nv} verified, {ne} errors",
                                      *[l for l in o1.splitlines() if l.startswith("error")][:3]]
            elif nv != pin_obl:
                fired["5a-obl"] = [f"{nv} verified, pinned {pin_obl}"]
            tv, te, o2 = verus(path, "--cfg", TWIN_CFG)
            if te:
                fired["5ct-run"] = [f"--cfg {TWIN_CFG}: {tv} verified, {te} errors",
                                    *[l for l in o2.splitlines() if l.startswith("error")][:3]]
            elif pin_twin is not None and tv != pin_twin:
                fired["5ct-obl"] = [f"--cfg {TWIN_CFG}: {tv} verified, pinned {pin_twin}"]

        print(f"=== {os.path.basename(path)}   shipped {nv}/{ne}   twin {tv}/{te}")
        if not fired:
            print("      NO LIMB FIRES")
        for k in ("5a-items", "5a-clause", "5a-obl", "5a-verify",
                  "5ct-sig", "5ct-cfg", "5ct-run", "5ct-obl"):
            for d in fired.get(k, []):
                print(f"      [{k}] {d}")
        print()


if __name__ == "__main__":
    main()
