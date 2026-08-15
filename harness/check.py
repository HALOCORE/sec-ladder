#!/usr/bin/env python3
"""The correctness gate. A pattern is not done until this is green.

Rewritten at TASK_003, because the version before it reported 28/28 PASS on p01
while a reviewer walked six distinct defects past it -- including the pilot's own
fatal defect, an `#[verifier::external_body] fn main` hidden by a single blank
line. Forty-seven patterns will clone this file, so the rule it now follows is:

    where a check was textual, replace it with something semantic; where that is
    impossible, pin the expected value in `spec.md` and diff mechanically.

What it enforces, in order:

  0  the extractor still reproduces the pilot numbers in `.memory/` (both digest
     conventions), and the structural parsers pass their own selftests
  1  every cell of the matrix builds
  2  every cell prints the checksum the pattern's own `model.py` predicts
  3  no cell collapsed: structurally (a real backward branch, a memory operand,
     a body above a floor) *and* dynamically -- marginal executed instructions
     per kernel call, measured as a difference of two callgrind runs, above the
     floor `spec.md` declares
  3b structural identity R4-vs-R5 is measured and **recorded as a result**. Only
     a drop below the level `spec.md` pins fails the gate: a proof that
     legitimately costs an instruction is a finding, not a harness error
  4  `adversarial-*` behaviour is recorded per rung and compared to the model's
     expected exit/stdout
  5  the four "Proof domain must cover the measured domain" rules:
       - the Verus obligation count equals the number pinned in `spec.md`
       - every item's `external` attribute, `requires` and `ensures` match
         `spec.md` exactly, and the item set matches too
       - Verus itself confirms the call site verifies (`--verify-function`),
         rather than a regex confirming it looks like it might
       - `requires`/`ensures` are evaluated on **every measured input**,
         adversarial included
  6  every rung's driver loop, C included, normalises to the token sequence
     pinned in `spec.md`
  7  the C rung is clean under ASan + UBSan and exits as the model says
  8  the Miri policy: mandatory wherever R4 and R5 are not byte-identical

Results are written to `results/gate/<pattern>.json`. Exit code is non-zero if
anything above fails.

  harness/check.py p01
  harness/check.py p01 --no-build          # reuse .temp/build/pNN
  harness/check.py p01 --skip large        # for a fast edit/check loop
  harness/check.py p01 --no-callgrind      # skip step 3's dynamic half
"""

import argparse
import difflib
import importlib.util
import json
import os
import re
import struct
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "common"))
sys.path.insert(0, os.path.join(REPO, "harness"))
import asm  # noqa: E402
import build as buildmod  # noqa: E402
import vparse  # noqa: E402
import dloop  # noqa: E402
import fixture  # noqa: E402

RUN_TIMEOUT = 900
ENSURES_SAMPLE = 128  # calls re-checked with the model's independent summation
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")


# ==========================================================================
# helpers
# ==========================================================================

class Report:
    def __init__(self):
        self.failures = []
        self.notes = []
        self.results = {}

    def fail(self, section, msg):
        self.failures.append((section, msg))
        print(f"    FAIL [{section}] {msg}")

    def ok(self, msg):
        print(f"    ok   {msg}")

    def note(self, msg):
        self.notes.append(msg)
        print(f"    --   {msg}")


def head(title):
    print(f"\n== {title} " + "=" * max(0, 66 - len(title)))


def run_bin(path, arg):
    try:
        r = subprocess.run([path, arg], capture_output=True, text=True,
                           timeout=RUN_TIMEOUT)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return None, "", f"<timeout after {RUN_TIMEOUT}s>"


def inputs_of(pdir, skip=()):
    d = os.path.join(pdir, "inputs")
    # `sweep-*` files are diagnostic (a per-call cost measured at one window
    # length is a coincidence, not a number -- see inputs/gen.py). They are not
    # part of the matrix and would multiply the gate's runtime for nothing.
    names = sorted(f for f in os.listdir(d)
                   if f.endswith(".bin") and not f.startswith("sweep-"))
    names = [n for n in names if n[:-4] not in skip]
    good = [n for n in names if not n.startswith("adversarial")]
    adv = [n for n in names if n.startswith("adversarial")]
    return d, good, adv


def read_contract(pdir):
    """Pull the ```slb-contract block out of spec.md."""
    txt = open(os.path.join(pdir, "spec.md")).read()
    m = re.search(r"```slb-contract\s*\n(.*?)```", txt, re.S)
    if not m:
        raise SystemExit("check.py: spec.md has no ```slb-contract block")
    return json.loads(m.group(1))


def load_model(pdir, contract):
    """Import the pattern's own reference model (`model.py`).

    Before TASK_003 this was hard-coded into check.py and every one of 47
    patterns would have had to fork the gate to get its own (M8). The API the
    module must expose is documented at the top of `patterns/p01-array-sum/model.py`."""
    name = contract.get("model", "model.py")
    path = os.path.join(pdir, name)
    if not os.path.exists(path):
        raise SystemExit(f"check.py: {path} missing -- every pattern ships a "
                         f"reference model; see patterns/p01-array-sum/model.py "
                         f"for the API")
    spec = importlib.util.spec_from_file_location(
        f"slb_model_{buildmod.pattern_id(pdir)}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "build"):
        raise SystemExit(f"check.py: {path} does not define build(path)")
    return mod


REQUIRED_MODEL_ATTRS = ("n_iters", "truncated", "checksum", "expected_exit",
                        "expected_stdout", "n_calls", "iter_calls",
                        "sample_calls", "helpers", "describe", "selfcheck")


# ==========================================================================
# 0. the extractor and the parsers still do what `.memory/` says
# ==========================================================================

def check_selftests(rep):
    head("0. extractor + parsers reproduce .memory/ and their own selftests")
    if not fixture.ensure():
        rep.fail("fixture", "could not build .temp/build/docrepro "
                            "(harness/fixture.py) -- step 0 cannot run")
        return
    rc = asm.selftest()
    if rc == 77:
        rep.fail("asm-selftest", "pilot fixture still missing after a build "
                                 "attempt")
    elif rc != 0:
        rep.fail("asm-selftest", "harness/asm.py no longer matches .memory/")
    if vparse._selftest() != 0:
        rep.fail("vparse-selftest", "harness/vparse.py fails its own bypass "
                                    "cases -- attribute detection is unsound")


# ==========================================================================
# 1. build
# ==========================================================================

def check_build(pdir, rep, cells, opts, modes):
    head("1. build the matrix")
    built = {}
    for c in cells:
        for o in opts:
            for m in modes:
                ok, out, log = buildmod.build_cell(pdir, c, o, m, quiet=True)
                built[(c, o, m)] = out if ok else None
                if not ok:
                    rep.fail("build", f"{c} {o} {m}\n{log}")
    n_ok = sum(1 for v in built.values() if v)
    print(f"    {n_ok}/{len(built)} cells built")
    return built


# ==========================================================================
# 2. checksums against the pattern's own model
# ==========================================================================

def build_models(modmod, indir, names, rep):
    models = {}
    for name in names:
        m = modmod.build(os.path.join(indir, name))
        missing = [a for a in REQUIRED_MODEL_ATTRS if not hasattr(m, a)]
        if missing:
            rep.fail("model", f"{name}: model.py's Model lacks {missing}")
            continue
        for p in m.selfcheck():
            rep.fail("model", f"{name}: {p}")
        models[name] = m
    return models


def check_checksums(built, rep, models, indir):
    head("2. checksum agreement across every cell (vs the pattern's model.py)")
    if not models:
        rep.fail("coverage", "no non-adversarial input left to check a checksum "
                             "against -- `--skip` removed them all, so this run "
                             "certifies nothing")
        return {}
    for name, mod in models.items():
        print(f"    {name}: {mod.describe()}")
    results = {}
    for (c, o, m), path in sorted(built.items()):
        if not path:
            continue
        for name, mod in models.items():
            rc, out, err = run_bin(path, os.path.join(indir, name))
            results[(c, o, m, name)] = (rc, out.strip(), err.strip())
            if rc != 0:
                rep.fail("run", f"{c} {o} {m} on {name}: exit {rc} "
                                f"stderr={err.strip()[:200]}")
            elif out.strip() != str(mod.checksum):
                rep.fail("checksum", f"{c} {o} {m} on {name}: got {out.strip()}, "
                                     f"model says {mod.checksum}")
    for name in models:
        vals = {v[1] for k, v in results.items() if k[3] == name and v[0] == 0}
        if len(vals) == 1:
            rep.ok(f"{name}: all {sum(1 for k in results if k[3] == name)} cells "
                   f"agree -> {vals.pop()}")
        elif vals:
            rep.fail("checksum", f"{name}: cells disagree: {sorted(vals)}")
    return results


# ==========================================================================
# 3. anti-collapse -- structural AND dynamic
# ==========================================================================

def check_no_collapse(built, rep):
    head("3a. anti-collapse, structural: the kernel loop survived optimisation")
    rows, digests, bad = [], {}, 0
    for (c, o, m), path in sorted(built.items()):
        if not path:
            continue
        # In `isolated` builds the kernel is its own symbol. In `whole` builds it
        # is inlined on purpose, so the loop has to be found in main instead.
        needle = "kernel" if m == "isolated" else "main"
        k = asm.try_kernel(path, needle)
        if k is None:
            bad += 1
            rep.fail("collapse", f"{c} {o} {m}: no symbol containing {needle!r}")
            continue
        floor = 8 if m == "isolated" else 20
        loads = [i for i in k.insns if re.search(r"\(%r[a-z0-9]+", i.text)]
        problems = []
        if not k.has_loop:
            problems.append("no backward branch")
        if k.n_fn_nopad < floor:
            problems.append(f"body {k.n_fn_nopad} < floor {floor}")
        if not loads:
            problems.append("no memory operand anywhere")
        rows.append((c, o, m, k.n_fn, k.n_fn_nopad, k.pad_insns,
                     len(k.backward_branches), k.md5_fn[:8], k.md5_raw[:8]))
        digests[(c, o, m)] = k
        if problems:
            bad += 1
            rep.fail("collapse", f"{c} {o} {m}: " + ", ".join(problems))
    print(f"    {'cell':18s} {'opt':4s} {'mode':9s} {'n_fn':>5s} {'nopad':>6s} "
          f"{'pad':>4s} {'loops':>6s}  {'md5_fn':8s} md5_raw")
    for c, o, m, nfn, nopad, pad, nloop, md5fn, md5raw in rows:
        print(f"    {c:18s} {o:4s} {m:9s} {nfn:5d} {nopad:6d} {pad:4d} {nloop:6d}"
              f"  {md5fn}  {md5raw}")
    if rows and not bad:
        rep.ok(f"{len(rows)} cells: real loop, real memory operand, body above "
               f"floor. Counts/digests are the `nm --print-size` extent; `pad` "
               f"is what objdump's grouping adds on top.")
    return digests


def _probe_input(src, n_iters, out):
    """The same input file with `n_iters` rewritten.

    `n_iters` is at offset 0 of *every* pattern's input file
    (`.memory/02-bench-rules.md`), so this is a format-level operation and needs
    no help from the pattern."""
    blob = open(src, "rb").read()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(struct.pack("<Q", n_iters) + blob[8:])
    return out


def _callgrind_total(binary, arg, outfile):
    """Whole-program Ir for one run. Only ever used as one half of a
    *difference*: `.memory/03-measurement.md` shows the absolute value moves
    with the size of the environment block, and every one of those terms cancels
    when the same binary is run twice in the same shell."""
    r = subprocess.run([VALGRIND, "--tool=callgrind",
                        f"--callgrind-out-file={outfile}", binary, arg],
                       capture_output=True, text=True, timeout=RUN_TIMEOUT)
    if r.returncode != 0:
        return None
    for line in open(outfile):
        if line.startswith("summary:") or line.startswith("totals:"):
            return int(line.split()[1])
    return None


def check_marginal_ir(pdir, built, rep, modmod, contract, indir, enabled):
    """The dynamic half of anti-collapse: does the loop still do work per call?

    A kernel that got constant-folded, hoisted or CSE'd away still has a
    backward branch somewhere in its symbol, so the structural check above
    cannot see it. Executed instructions per kernel call can. Measured as a
    slope -- Ir at N calls minus Ir at N/2 calls, over the difference in calls --
    which is symbol-independent (so it works in `whole` mode, and at O0 where a
    rung's work lives in `core::iter` symbols rather than in `kernel`) and
    cancels the loader and environment terms exactly."""
    head("3b. anti-collapse, dynamic: marginal Ir per kernel call")
    cfg = contract.get("collapse")
    if not cfg:
        rep.fail("collapse-ir", "spec.md declares no `collapse` floor -- "
                                "TASK_003 M4 requires one")
        return {}
    if not enabled:
        rep.fail("collapse-ir", "--no-callgrind given: the dynamic anti-collapse "
                                "assertion did not run, so this gate run does "
                                "not certify that the loop survived")
        return {}
    if not os.path.exists(VALGRIND):
        rep.fail("collapse-ir", f"valgrind missing at {VALGRIND}")
        return {}
    src = os.path.join(indir, cfg["probe_input"])
    if not os.path.exists(src):
        rep.fail("collapse-ir", f"probe input {cfg['probe_input']} not found")
        return {}
    lo, hi = cfg["probe_iters"]
    floor = cfg["min_marginal_ir_per_call"]
    scratch = os.path.join(REPO, ".temp", "check", buildmod.pattern_id(pdir))
    probes = {n: _probe_input(src, n, os.path.join(scratch, f"probe-{n}.bin"))
              for n in (lo, hi)}
    calls = {n: modmod.build(probes[n]).n_calls for n in (lo, hi)}
    dcalls = calls[hi] - calls[lo]
    if dcalls <= 0:
        rep.fail("collapse-ir", f"probe iters {lo}->{hi} produce no extra kernel "
                                f"calls ({calls}) -- pick a different probe_input")
        return {}
    print(f"    probe {cfg['probe_input']} at n_iters {lo}/{hi} "
          f"-> {calls[lo]}/{calls[hi]} kernel calls; floor {floor} Ir/call")
    out, worst = {}, None
    for (c, o, m), path in sorted(built.items()):
        if not path:
            continue
        ir = {}
        for n in (lo, hi):
            ir[n] = _callgrind_total(path, probes[n],
                                     os.path.join(scratch, f"cg.{c}-{o}-{m}.{n}.out"))
            if ir[n] is None:
                rep.fail("collapse-ir", f"{c} {o} {m}: callgrind produced no total")
                break
        else:
            slope = (ir[hi] - ir[lo]) / dcalls
            out[f"{c}/{o}/{m}"] = slope
            worst = slope if worst is None else min(worst, slope)
            if slope < floor:
                rep.fail("collapse-ir",
                         f"{c} {o} {m}: {slope:.0f} Ir per kernel call is below "
                         f"the floor {floor} declared in spec.md -- the loop is "
                         f"not doing the work the benchmark claims to measure "
                         f"(Ir {ir[lo]:,} -> {ir[hi]:,} over {dcalls} calls)")
    if out and worst is not None and not any(f[0] == "collapse-ir"
                                             for f in rep.failures):
        rep.ok(f"{len(out)} cells: marginal Ir per call {worst:.0f}..."
               f"{max(out.values()):.0f}, all above the floor {floor}")
    return out


# ==========================================================================
# 3c. structural identity -- a RESULT, not a gate condition
# ==========================================================================

def check_identity(digests, rep, contract):
    head("3c. structural identity R4-vs-R5 (recorded as a result)")
    pins = contract.get("identity") or []
    if not pins:
        rep.note("spec.md pins no identity expectations")
    recorded = []
    for pin in pins:
        a, b = pin["a"], pin["b"]
        for o in buildmod.OPTS:
            ka, kb = digests.get((a, o, "isolated")), digests.get((b, o, "isolated"))
            if not ka or not kb:
                rep.note(f"{a}/{b} {o}: one side missing, skipped")
                continue
            level, ev = asm.identity_level(ka, kb)
            want = pin.get(o)
            rec = dict(pair=f"{a} vs {b}", opt=o, level=level, expected=want,
                       md5_fn_a=ev["md5_fn_a"], md5_fn_b=ev["md5_fn_b"],
                       md5_raw_equal=ev["md5_raw_equal"],
                       counts_a=ev["counts_a"], counts_b=ev["counts_b"],
                       pad_a=ev["pad_a"], pad_b=ev["pad_b"])
            recorded.append(rec)
            if want is None:
                rep.note(f"{a} vs {b} {o}: measured {level!r}, spec.md pins "
                         f"nothing")
                continue
            if want not in asm.IDENTITY_LEVELS:
                rep.fail("identity", f"{a} vs {b} {o}: spec.md pins {want!r}, "
                                     f"which is not one of "
                                     f"{asm.IDENTITY_LEVELS}")
                continue
            got_i = asm.IDENTITY_LEVELS.index(level)
            want_i = asm.IDENTITY_LEVELS.index(want)
            if got_i < want_i:
                # A *regression* against the pin. Not "the proof cost
                # something" -- that would be a result; this is the tree no
                # longer matching what spec.md says about itself.
                _, _, d = asm.diff(ka.binary, kb.binary)
                rep.fail("identity", f"{a} vs {b} at {o}: identity dropped to "
                                     f"{level!r}, spec.md pins {want!r}\n"
                                     f"      md5_fn {ev['md5_fn_a'][:12]} vs "
                                     f"{ev['md5_fn_b'][:12]}, counts "
                                     f"{ev['counts_a']} vs {ev['counts_b']}\n{d}")
            else:
                extra = "" if got_i == want_i else "  (stronger than pinned)"
                rep.ok(f"{a} vs {b} {o}: {level} "
                       f"(md5_fn {ev['md5_fn_a'][:12]}; md5_raw equal="
                       f"{ev['md5_raw_equal']}, padding "
                       f"{ev['pad_a'][1]}/{ev['pad_b'][1]} B){extra}")
    return recorded


# ==========================================================================
# 4. adversarial behaviour
# ==========================================================================

def check_adversarial(built, rep, adv_models, indir, cells):
    head("4. adversarial inputs -- behaviour recorded, not required to agree")
    table = {}
    for name, mod in adv_models.items():
        print(f"    -- {name}: {mod.describe()} -> model expects exit "
              f"{mod.expected_exit}, stdout {mod.expected_stdout.strip()!r}")
        for c in cells:
            seen = set()
            for (cc, o, m), path in sorted(built.items()):
                if cc != c or not path:
                    continue
                rc, out, err = run_bin(path, os.path.join(indir, name))
                sig = -rc if rc is not None and rc < 0 else None
                seen.add((rc, out.strip(), err.strip()[:120], sig))
            for rc, out, err, sig in sorted(seen, key=str):
                table[f"{name}/{c}"] = dict(exit=rc, stdout=out, stderr=err,
                                            signal=sig,
                                            model_exit=mod.expected_exit,
                                            model_stdout=mod.expected_stdout.strip())
                flag = ""
                if rc != mod.expected_exit or out != mod.expected_stdout.strip():
                    flag = "  <-- diverges from model"
                print(f"       {c:18s} exit={rc!s:5s} stdout={out!r:24s}"
                      f" stderr={err!r:60s}{flag}")
            if len(seen) > 1:
                rep.note(f"{name}/{c}: opt/mode variants of this rung disagree "
                         f"({len(seen)} distinct behaviours)")
    return table


# ==========================================================================
# 5. proof domain must cover the measured domain
# ==========================================================================

def _clauses(item, kw):
    return item.clauses.get(kw, []) if item else []


def check_verus_contract(pdir, rep, contract):
    """B1 + B2: obligation count, item set, and every `requires`/`ensures`
    diffed against the pin in spec.md.

    This is the only mechanical defence against the two failure modes that
    produce `N verified, 0 errors` regardless:
      * a tautological `ensures` (`r == r`) -- same count, no diagnostic;
      * a `requires` deleted from an `external_body` wrapper -- same count, no
        diagnostic, and every caller's obligation silently gone
        (`.memory/04-verus.md`)."""
    head("5a. the Verus contract matches the pin in spec.md")
    vcfg = contract.get("verus") or {}
    pinned_obl = vcfg.get("obligations") or {}
    pinned_items = vcfg.get("items") or {}
    if not pinned_obl or not pinned_items:
        rep.fail("proof-pin", "spec.md pins no `verus.obligations` / "
                              "`verus.items` -- TASK_003 B1/B2 require both")
        return {}
    out = {}
    for src, want_n in sorted(pinned_obl.items()):
        path = os.path.join(pdir, src)
        if not os.path.exists(path):
            rep.fail("proof-pin", f"{src} pinned in spec.md but not in the tree")
            continue
        txt = open(path).read()
        items = {i.name: i for i in vparse.parse(txt)}

        # --- item set -----------------------------------------------------
        want_items = pinned_items.get(src)
        if want_items is None:
            rep.fail("proof-pin", f"{src}: no item pin in spec.md")
            continue
        got, want = set(items), set(want_items)
        if got != want:
            rep.fail("proof-pin", f"{src}: item set differs from spec.md; "
                                  f"added={sorted(got - want)} "
                                  f"removed={sorted(want - got)}")
        # --- per-item attributes and clauses ------------------------------
        for name in sorted(want & got):
            w, it = want_items[name], items[name]
            diffs = []
            if (it.external or None) != (w.get("external") or None):
                diffs.append(f"external: {it.external!r} != {w.get('external')!r}")
            for kw in ("requires", "ensures"):
                gotc = _clauses(it, kw)
                wantc = [vparse.norm_clause(c) for c in w.get(kw, [])]
                if gotc != wantc:
                    diffs.append(f"{kw}: {gotc!r} != pinned {wantc!r}")
            if diffs:
                rep.fail("proof-pin", f"{src}:{it.line} `{name}` drifted from "
                                      f"spec.md -- " + "; ".join(diffs))

        # --- TCB inventory, from the fixed parser -------------------------
        tcb = [i for i in items.values() if i.external]
        print(f"    {src}: TCB items ({len(tcb)}):")
        for i in tcb:
            print(f"       {i.external:32s} {i.name:16s} "
                  f"({i.body_lines} body lines, line {i.line})")
        for kw in ("assume(", "assume_specification", "admit("):
            n = len(re.findall(re.escape(kw), vparse.blank_noncode(txt)))
            if n:
                rep.note(f"{src}: {kw} appears {n}x -- must be justified in NOTES.md")

        # --- obligation count --------------------------------------------
        r = subprocess.run([sys.executable, os.path.join(REPO, "verus_run.py"), path],
                           capture_output=True, text=True, cwd=REPO,
                           timeout=RUN_TIMEOUT)
        res = (r.stdout + r.stderr).strip()
        m = re.search(r"(\d+) verified, (\d+) errors", res)
        if not m:
            rep.fail("proof-verify", f"{src}: no verification result: {res[-500:]}")
            continue
        n_ver, n_err = int(m.group(1)), int(m.group(2))
        out[src] = {"verified": n_ver, "errors": n_err, "pinned": want_n,
                    "tcb_items": [dict(name=i.name, attr=i.external,
                                       body_lines=i.body_lines, line=i.line)
                                  for i in tcb]}
        if n_err:
            rep.fail("proof-verify", f"{src}: {n_ver} verified, {n_err} errors")
        elif n_ver != want_n:
            rep.fail("proof-obligations",
                     f"{src}: {n_ver} verified, spec.md pins {want_n}. A count "
                     f"that MOVED means code stopped being verified, not that "
                     f"the proof got easier (`.memory/04-verus.md`). An "
                     f"`external_body` on a driver drops it exactly this way.")
        else:
            rep.ok(f"{src}: {n_ver} verified, 0 errors -- matches the pinned "
                   f"obligation count; {len(tcb)} TCB items, all contracts "
                   f"identical to spec.md")
    return out


def check_call_site(pdir, rep, contract):
    """Rule 2, asked of Verus rather than of a regex.

    `--verify-function <name> --verify-root` reports how many obligations that
    *one* function contributed. An `#[verifier::external_body] fn main` reports
    `0 verified` -- there is no body to verify, so no call inside it discharges
    anything. That is the pilot's defect, detected semantically."""
    head("5b. rule 2: Verus confirms the call site is a verified call site")
    vcfg = contract.get("verus") or {}
    site = vcfg.get("call_site", "main")
    kname = vcfg.get("kernel_item", "kernel")
    src = os.path.join(pdir, "verus.rs")
    if not os.path.exists(src):
        rep.fail("proof-rule2", "no verus.rs")
        return {}
    items = {i.name: i for i in vparse.parse(open(src).read())}
    out = {}

    it = items.get(site)
    if it is None:
        rep.fail("proof-rule2", f"verus.rs has no `fn {site}`")
    else:
        if not it.in_verus:
            rep.fail("proof-rule2", f"`fn {site}` is outside `verus! {{}}` -- the "
                                    f"kernel call site is unverified (the pilot's bug)")
        if it.external:
            rep.fail("proof-rule2", f"`fn {site}` is {it.external} -- no "
                                    f"precondition is ever discharged")
        if not it.calls(kname):
            rep.fail("proof-rule2", f"`fn {site}` contains no call to {kname}() "
                                    f"(comments and string literals do not count)")

    for name in (site, kname):
        r = subprocess.run([sys.executable, os.path.join(REPO, "verus_run.py"), src,
                            "--verify-function", name, "--verify-root"],
                           capture_output=True, text=True, cwd=REPO,
                           timeout=RUN_TIMEOUT)
        res = (r.stdout + r.stderr).strip()
        m = re.search(r"(\d+) verified, (\d+) errors", res)
        n = int(m.group(1)) if m else 0
        out[name] = n
        if not m or int(m.group(2)) or n < 1:
            rep.fail("proof-rule2",
                     f"`verus --verify-function {name}` reports {n} verified: "
                     f"Verus has no verified body for `{name}`. If it is "
                     f"`external_body`, every obligation inside it -- including "
                     f"the kernel's `requires` at the call site -- is discarded "
                     f"(`.memory/02-bench-rules.md` rule 2).\n      {res[-300:]}")
        else:
            rep.ok(f"verus --verify-function {name}: {n} verified -- `{name}` "
                   f"has a real verified body")
    return out


def check_proof_domain(rep, models, contract):
    """Rules 1 and 3, on **every** measured input.

    The previous version built its model set from the non-adversarial inputs
    only (B3). p01 hides that -- its adversarial inputs make zero kernel calls --
    but for the 47 downstream patterns the adversarial input is by construction
    the one aimed at the precondition, so it is precisely the input on which
    these rules must be evaluated."""
    head("5c. rules 1 and 3 on EVERY measured input, adversarial included")
    stats = {}
    for name, mod in sorted(models.items()):
        if mod.n_calls == 0:
            print(f"    {name}: 0 kernel calls (degenerate shape) -- vacuously "
                  f"inside the domain")
            stats[name] = dict(calls=0, requires_ok=True, ensures_checked=0)
            continue
        bad_req, n = None, 0
        offs = []
        for env in mod.iter_calls():
            n += 1
            if "off" in env:
                offs.append(env["off"])
            for expr in contract["requires"]:
                if not eval(expr, {"__builtins__": {}}, dict(env)):
                    bad_req = (expr, {k: v for k, v in env.items() if k != "v"})
                    break
            if bad_req:
                break
        if bad_req:
            rep.fail("proof-rule1", f"{name}: requires {bad_req[0]!r} violated at "
                                    f"{bad_req[1]}")
        else:
            rng = f", off {min(offs)}..{max(offs)}" if offs else ""
            rep.ok(f"{name}: `requires` holds on all {n} kernel calls{rng}")
        # ensures, re-derived with the model's independent implementation
        sample = mod.sample_calls(ENSURES_SAMPLE)
        bad_ens = None
        for env in sample:
            ns = dict(env)
            ns.update(mod.helpers)
            for expr in contract["ensures"]:
                if not eval(expr, {"__builtins__": {}}, ns):
                    bad_ens = (expr, {k: v for k, v in env.items() if k != "v"})
                    break
            if bad_ens:
                break
        if bad_ens:
            rep.fail("proof-rule3", f"{name}: ensures {bad_ens[0]!r} violated at "
                                    f"{bad_ens[1]}")
        else:
            rep.ok(f"{name}: `ensures` re-derived independently on "
                   f"{len(sample)} sampled calls")
        stats[name] = dict(calls=n, requires_ok=bad_req is None,
                           ensures_checked=len(sample))
    return stats


# ==========================================================================
# 6. the driver loop
# ==========================================================================

def check_driver_identity(pdir, rep, contract):
    head("6. every driver loop matches the token sequence pinned in spec.md")
    cfg = contract.get("driver") or {}
    canon = cfg.get("canonical")
    if not canon:
        rep.fail("driver", "spec.md pins no `driver.canonical` token sequence -- "
                           "generate one with `harness/dloop.py <rung>.rs` and "
                           "paste it into the slb-contract block")
        return {}
    ref = "\n".join(canon)
    aliases = cfg.get("aliases") or {}
    found = {}
    for f in sorted(os.listdir(pdir)):
        if f.endswith(".rs"):
            r = dloop.normalise_file(os.path.join(pdir, f), "rust",
                                     aliases.get("rust"))
            if r is not None:
                found[f] = r
    cmain = cfg.get("c_source", os.path.join("c", "main.c"))
    cpath = os.path.join(pdir, cmain)
    if os.path.exists(cpath):
        r = dloop.normalise_file(cpath, "c", aliases.get("c"))
        if r is None:
            rep.fail("driver", f"{cmain} has no SLB-DRIVER region")
        else:
            found[cmain] = r
    else:
        rep.fail("driver", f"{cmain} not found")
    if len(found) < 2:
        rep.fail("driver", "fewer than two driver regions found")
        return {}
    want_stmts = cfg.get("statements")
    out = {}
    for name, body in sorted(found.items()):
        n = dloop.statement_count(body)
        out[name] = {"statements": n, "matches_pin": body == ref}
        if body != ref:
            d = "\n".join(difflib.unified_diff(
                ref.splitlines(), body.splitlines(),
                "spec.md:driver.canonical", name, lineterm=""))
            rep.fail("driver", f"{name} driver loop differs from the pin in "
                               f"spec.md ({n} statements vs {want_stmts}):\n{d}")
        elif want_stmts is not None and n != want_stmts:
            rep.fail("driver", f"{name}: {n} statements, spec.md pins {want_stmts}")
    if not any(f[0] == "driver" for f in rep.failures):
        rep.ok(f"{len(found)} driver loops ({len(found) - 1} Rust + C) all "
               f"normalise to the pinned {want_stmts}-statement token sequence; "
               f"Verus clauses and ghost statements excluded")
    return out


# ==========================================================================
# 7. sanitizers
# ==========================================================================

def check_sanitizers(pdir, rep, indir, models):
    head("7. C rung under ASan + UBSan")
    out = os.path.join(REPO, ".temp", "build",
                       buildmod.pattern_id(pdir), "c-gcc-asan")
    cmd = [buildmod.GCC, "-std=c99", "-Wall", "-Wextra", "-O1", "-g",
           "-fsanitize=address,undefined",
           # the container has an LD_PRELOAD that breaks the shared ASan
           # runtime's init ordering; static linking sidesteps it
           "-static-libasan", "-static-libubsan",
           "-DSLB_ISOLATED", "-I", os.path.join(REPO, "common"),
           "-I", os.path.join(pdir, "c"),
           os.path.join(REPO, "common", "driver.c"),
           os.path.join(pdir, "c", "kernel.c"),
           os.path.join(pdir, "c", "main.c"), "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        rep.fail("sanitizer", f"asan build failed: {(r.stdout + r.stderr)[-400:]}")
        return {}
    res = {}
    for name, mod in sorted(models.items()):
        rc, so, se = run_bin(out, os.path.join(indir, name))
        res[name] = {"exit": rc, "expected_exit": mod.expected_exit}
        fired = ("runtime error" in se or "AddressSanitizer" in se
                 or "ERROR:" in se)
        if fired:
            rep.fail("sanitizer", f"{name}: {se.strip()[:300]}")
        elif rc != mod.expected_exit:
            # the old version printed the exit code and ignored it entirely
            rep.fail("sanitizer", f"{name}: exit {rc}, model expects "
                                  f"{mod.expected_exit}")
        else:
            print(f"    ok   {name:28s} exit={rc} (model {mod.expected_exit})")
    return res


# ==========================================================================
# 8. Miri policy
# ==========================================================================

def check_miri(pdir, rep, contract, identity):
    """`.memory/02-bench-rules.md`: Miri is mandatory for any pattern whose R4
    and R5 are **not** byte-identical, because that is exactly when R4 stops
    inheriting R5's discharged obligations. Byte-identical R4/R5 is exempt."""
    head("8. Miri policy")
    cfg = contract.get("miri") or {}
    o3 = [r for r in identity if r["pair"] == "unsafe vs verus" and r["opt"] == "O3"]
    byte_identical = bool(o3) and o3[0]["level"] == "exact"
    if byte_identical and not cfg.get("required"):
        rep.ok("R4 and R5 are byte-identical at O3 (identity level 'exact'), so "
               "R4 inherits R5's proof exactly -- Miri not required. "
               f"spec.md: {cfg.get('reason', '(no reason given)')}")
        return {"required": False, "ran": False, "byte_identical": True}
    if not byte_identical and not cfg.get("required"):
        rep.fail("miri", "R4 and R5 are NOT byte-identical at O3, so R4 is "
                         "unverified unsafe code that does not inherit R5's "
                         "proof. `.memory/02-bench-rules.md` makes Miri "
                         "mandatory here; spec.md sets miri.required=false.")
        return {"required": True, "ran": False, "byte_identical": False}
    cargo = os.path.expanduser("~/.cargo/bin/cargo")
    r = subprocess.run([cargo, "miri", "--version"], capture_output=True, text=True)
    if r.returncode != 0:
        rep.fail("miri", "Miri is required for this pattern but the component is "
                         "not installed for this toolchain "
                         f"({(r.stdout + r.stderr).strip()[:160]}). Install it "
                         f"or record the pattern as a documented failure.")
        return {"required": True, "ran": False, "available": False}
    rep.note("Miri required and available -- per-pattern invocation is the "
             "pattern's job; record the run in NOTES.md")
    return {"required": True, "ran": False, "available": True}


# ==========================================================================

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pattern")
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--skip", action="append", default=[],
                    help="input stem to skip, e.g. --skip large")
    ap.add_argument("--cells", default="all", choices=["all", "measured"])
    ap.add_argument("--no-callgrind", action="store_true",
                    help="skip step 3b; the run then FAILS, by design")
    a = ap.parse_args()

    pdir = buildmod.pattern_dir(a.pattern)
    cells = (buildmod.ALL_CELLS if a.cells == "all" else buildmod.MEASURED_CELLS)
    opts, modes = buildmod.OPTS, buildmod.MODES
    indir, good, adv = inputs_of(pdir, skip=a.skip)
    contract = read_contract(pdir)
    modmod = load_model(pdir, contract)

    print(f"check.py: {os.path.basename(pdir)}")
    print(f"  cells   {cells}")
    print(f"  opts    {opts}   modes {modes}")
    print(f"  inputs  good={good} adversarial={adv}")
    print(f"  model   {contract.get('model', 'model.py')}")
    print(f"  contract requires={contract['requires']} ensures={contract['ensures']}")
    if a.skip:
        print(f"  SKIPPED {a.skip} -- this run does not certify those inputs")

    rep = Report()
    check_selftests(rep)

    if a.no_build:
        built = {}
        for c in cells:
            for o in opts:
                for m in modes:
                    p = buildmod.out_path(pdir, c, o, m, "unwind")
                    built[(c, o, m)] = p if os.path.exists(p) else None
        head("1. build the matrix")
        print(f"    --no-build: reusing {sum(1 for v in built.values() if v)}"
              f"/{len(built)} existing binaries")
        for k, v in built.items():
            if v is None:
                rep.fail("build", f"{k} missing and --no-build given")
    else:
        built = check_build(pdir, rep, cells, opts, modes)

    good_models = build_models(modmod, indir, good, rep)
    adv_models = build_models(modmod, indir, adv, rep)
    all_models = dict(good_models)
    all_models.update(adv_models)

    check_checksums(built, rep, good_models, indir)
    digests = check_no_collapse(built, rep)
    slopes = check_marginal_ir(pdir, built, rep, modmod, contract, indir,
                               not a.no_callgrind)
    identity = check_identity(digests, rep, contract)
    advtable = check_adversarial(built, rep, adv_models, indir, cells)
    verus_res = check_verus_contract(pdir, rep, contract)
    callsite = check_call_site(pdir, rep, contract)
    domain = check_proof_domain(rep, all_models, contract)
    drivers = check_driver_identity(pdir, rep, contract)
    san = check_sanitizers(pdir, rep, indir, all_models)
    miri = check_miri(pdir, rep, contract, identity)

    doc = {
        "pattern": os.path.basename(pdir),
        "skipped_inputs": a.skip,
        "inputs_checked": sorted(all_models),
        "identity": identity,
        "marginal_ir_per_call": slopes,
        "verus": verus_res,
        "verified_call_site": callsite,
        "proof_domain": domain,
        "driver_loops": drivers,
        "adversarial": advtable,
        "sanitizer": san,
        "miri": miri,
        "failures": [{"section": s, "message": m} for s, m in rep.failures],
        "notes": rep.notes,
        "verdict": "FAIL" if rep.failures else "PASS",
    }
    outdir = os.path.join(REPO, "results", "gate")
    os.makedirs(outdir, exist_ok=True)
    outp = os.path.join(outdir, f"{os.path.basename(pdir)}.json")
    with open(outp, "w") as fh:
        json.dump(doc, fh, indent=2, sort_keys=False, default=str)

    head("verdict")
    print(f"    results -> {os.path.relpath(outp, REPO)}")
    for n in rep.notes:
        print(f"    note: {n}")
    if rep.failures:
        print(f"    {len(rep.failures)} FAILURE(S):")
        for s, m in rep.failures:
            print(f"      [{s}] {m}")
        print("\ncheck.py: FAIL")
        return 1
    print("\ncheck.py: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
