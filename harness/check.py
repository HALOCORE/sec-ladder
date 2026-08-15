#!/usr/bin/env python3
"""The correctness gate. A pattern is not done until this is green.

What it enforces, in order:

  0  harness/asm.py still reproduces the pilot numbers recorded in `.memory/`
  1  every cell of the matrix builds
  2  every cell prints the same checksum on `small` and `large`, and that
     checksum matches an independent Python model of the driver + kernel
  3  no cell collapsed: the kernel's disassembly has a real backward branch,
     a memory load inside the loop, and a body above a plausible floor
  4  the `adversarial-*` inputs are *recorded* per rung (exit code, stdout,
     stderr, signal) rather than required to agree -- that divergence is the
     security half of the result (`.memory/02-bench-rules.md`)
  5  the four "Proof domain must cover the measured domain" rules:
       1. every measured input satisfies the R5 kernel's `requires`
       2. R5 has a *verified* call site -- `main` inside `verus!` and not
          `external_body`, calling the kernel
       3. the `ensures` holds on every measured output
       4. this check fails the cell rather than narrowing the table
  6  the driver loop is byte-identical across the Rust rungs and carries the
     same arithmetic in C
  7  the C rung is clean under ASan + UBSan on every input

Exit code is non-zero if anything above fails.

  harness/check.py p01
  harness/check.py p01 --no-build          # reuse .temp/build/pNN
  harness/check.py p01 --skip large        # for a fast edit/check loop
"""

import argparse
import difflib
import itertools
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "common"))
sys.path.insert(0, os.path.join(REPO, "harness"))
import slb  # noqa: E402
import asm  # noqa: E402
import build as buildmod  # noqa: E402

MASK = (1 << 64) - 1
RUN_TIMEOUT = 900
ENSURES_SAMPLE = 128  # calls re-checked with an independent (naive) sum


# ==========================================================================
# reference model -- an independent implementation of ../spec.md
# ==========================================================================

class Model:
    """Simulates the driver loop and the kernel in Python, from the file alone.

    Two separate sum implementations on purpose: the simulation uses prefix
    sums (fast enough for 1.5M elements), and `naive_sum` re-derives a sample of
    the same answers by literally adding the elements. If those two ever
    disagree the model is broken, and the `ensures` check would be circular
    without it."""

    def __init__(self, path):
        f = slb.read(path)
        self.path = path
        self.n_iters = f.n_iters
        self.declared_len = f.declared_len
        self.truncated = f.truncated
        # The drivers read exactly `payload_len` bytes and reject a short file.
        self.payload = f.payload[: f.declared_len]
        self.head, self.vals = slb.head_u64_body(self.payload)
        self.v_len = len(self.vals)
        self.calls = []       # (off, len, result) for every kernel call
        self.checksum = None
        self.entered = False
        if not self.truncated:
            self._run()

    def _run(self):
        head, n_vals = self.head, self.v_len
        acc = 0
        if 0 < head <= n_vals:
            self.entered = True
            win = int(head)
            nwin = n_vals - win + 1
            prefix = [0]
            prefix.extend(itertools.accumulate(self.vals,
                                               lambda a, b: (a + b) & MASK))
            for _ in range(self.n_iters):
                off = acc % nwin
                r = (prefix[off + win] - prefix[off]) & MASK
                self.calls.append((off, win, r))
                acc = (acc * 31 + r) & MASK
        self.checksum = acc

    def naive_sum(self, off, ln):
        acc = 0
        for x in self.vals[off:off + ln]:
            acc = (acc + x) & MASK
        return acc

    @property
    def expected_exit(self):
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.truncated else f"{self.checksum}\n"


# ==========================================================================
# helpers
# ==========================================================================

class Report:
    def __init__(self):
        self.failures = []
        self.notes = []

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


def driver_region(src_path):
    """The text between SLB-DRIVER-BEGIN and SLB-DRIVER-END, normalised:
    comments gone, whitespace collapsed, and Verus-only clauses
    (`invariant ...`, `decreases ...`) removed so R5's copy can be compared to
    the plain-Rust ones."""
    txt = open(src_path).read()
    m = re.search(r"SLB-DRIVER-BEGIN\s*(?:\*/)?\n(.*?)\n\s*(?://\s*|/\*\s*)?SLB-DRIVER-END",
                  txt, re.S)
    if not m:
        return None
    body = m.group(1)
    out, skipping = [], False
    for line in body.splitlines():
        s = line.strip()
        s = re.sub(r"//.*$", "", s).strip()
        if not s:
            continue
        if re.match(r"^(invariant|decreases)\b", s):
            # a clause block runs until the line that opens the loop body
            skipping = not s.endswith("{")
            if s.endswith("{"):
                out.append("{")
            continue
        if skipping:
            if s.endswith("{"):
                skipping = False
                out.append("{")
            continue
        out.append(s)
    text = "\n".join(out)
    # A Verus loop writes `while c` / clauses / `{`; a plain Rust loop writes
    # `while c {`. Once the clauses are gone the only difference left is where
    # the brace sits, so pull a lone `{` back onto the previous line.
    return re.sub(r"\n\{", " {", text)


# ==========================================================================
# checks
# ==========================================================================

def check_asm_selftest(rep):
    head("0. asm.py reproduces the pilot numbers in .memory/")
    rc = asm.selftest()
    if rc == 77:
        rep.note("pilot fixture .temp/build/docrepro missing -- selftest skipped")
    elif rc != 0:
        rep.fail("asm-selftest", "harness/asm.py no longer matches .memory/")


def check_build(pdir, rep, cells, opts, modes):
    head("1. build the matrix")
    built = {}
    for c in cells:
        for o in opts:
            for m in modes:
                ok, out, log = build_cell_quiet(pdir, c, o, m)
                built[(c, o, m)] = out if ok else None
                if not ok:
                    rep.fail("build", f"{c} {o} {m}\n{log}")
    n_ok = sum(1 for v in built.values() if v)
    print(f"    {n_ok}/{len(built)} cells built")
    return built


def build_cell_quiet(pdir, c, o, m):
    return buildmod.build_cell(pdir, c, o, m, quiet=True)


def check_checksums(pdir, built, rep, good_inputs, indir):
    head("2. checksum agreement across every cell")
    models = {}
    for name in good_inputs:
        models[name] = Model(os.path.join(indir, name))
    for name, mod in models.items():
        # sanity: the two independent sums inside the model agree
        for off, ln, r in mod.calls[:8]:
            if mod.naive_sum(off, ln) != r:
                rep.fail("model", f"{name}: prefix-sum model disagrees with naive sum "
                                  f"at off={off} len={ln}")
                break
        print(f"    {name}: n_iters={mod.n_iters} v_len={mod.v_len} win={mod.head} "
              f"calls={len(mod.calls)} expected={mod.checksum}")
    results = {}
    for (c, o, m), path in sorted(built.items()):
        if not path:
            continue
        for name, mod in models.items():
            rc, out, err = run_bin(path, os.path.join(indir, name))
            results[(c, o, m, name)] = (rc, out.strip(), err.strip())
            if rc != 0:
                rep.fail("run", f"{c} {o} {m} on {name}: exit {rc} stderr={err.strip()[:200]}")
            elif out.strip() != str(mod.checksum):
                rep.fail("checksum", f"{c} {o} {m} on {name}: got {out.strip()}, "
                                     f"model says {mod.checksum}")
    for name in models:
        vals = {v[1] for k, v in results.items() if k[3] == name and v[0] == 0}
        if len(vals) == 1:
            rep.ok(f"{name}: all {sum(1 for k in results if k[3] == name)} cells agree "
                   f"-> {vals.pop()}")
        elif vals:
            rep.fail("checksum", f"{name}: cells disagree: {sorted(vals)}")
    return models, results


def check_no_collapse(built, rep):
    head("3. anti-collapse: the kernel loop survived optimisation")
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
        if k.n_nopad < floor:
            problems.append(f"body {k.n_nopad} < floor {floor}")
        if not loads:
            problems.append("no memory operand anywhere")
        rows.append((c, o, m, k.symbol, k.n_raw, k.n_nopad,
                     len(k.backward_branches), k.md5_raw[:8], k.md5_raw_norel[:8]))
        digests[(c, o, m)] = k
        if problems:
            bad += 1
            rep.fail("collapse", f"{c} {o} {m}: " + ", ".join(problems))
    print(f"    {'cell':18s} {'opt':4s} {'mode':9s} {'raw':>4s} {'nopad':>6s} "
          f"{'loops':>6s}  {'md5_raw':8s} md5_norel")
    for c, o, m, sym, raw, nopad, nloop, md5, md5n in rows:
        print(f"    {c:18s} {o:4s} {m:9s} {raw:4d} {nopad:6d} {nloop:6d}  "
              f"{md5}  {md5n}")
    if rows and not bad:
        rep.ok(f"{len(rows)} cells: real loop, real memory operand, body above floor")
    return digests


# `.memory/01-ladder.md` structural findings 1 and 2, restated as a gate: a
# proof must cost nothing. Checked in `isolated` mode only -- that is where the
# kernel is its own symbol. In `whole` mode `main` also swallows the loader,
# which legitimately differs between a rung that calls driver::load directly and
# one that calls it through an external_body wrapper.
IDENTITY_PAIRS = [
    ("unsafe", "verus", "R4 == R5: the proof licenses unsafe code at zero cost"),
    ("safe_naive", "safe_naive_verus", "R2 == R2v: proving safe code buys nothing"),
]


def check_identity(digests, rep):
    head("3b. structural identity: a Verus proof costs zero instructions")
    for a, b, why in IDENTITY_PAIRS:
        for o in buildmod.OPTS:
            ka, kb = digests.get((a, o, "isolated")), digests.get((b, o, "isolated"))
            if not ka or not kb:
                rep.note(f"{a}/{b} {o}: one side missing, skipped")
                continue
            exact = ka.md5_raw == kb.md5_raw
            norel = ka.md5_raw_norel == kb.md5_raw_norel
            counts = (ka.n_raw, ka.n_nopad) == (kb.n_raw, kb.n_nopad)
            if not (norel and counts):
                _, _, d = asm.diff(ka.binary, kb.binary)
                rep.fail("identity", f"{a} != {b} at {o} isolated "
                                     f"({ka.n_raw}/{ka.n_nopad} vs "
                                     f"{kb.n_raw}/{kb.n_nopad})\n{d}")
            elif exact:
                rep.ok(f"{o}: {a} == {b} by raw machine-code bytes "
                       f"({ka.md5_raw}) -- {why}")
            else:
                rep.ok(f"{o}: {a} == {b} with pc-rel fields masked "
                       f"({ka.md5_raw_norel}); md5_raw differs "
                       f"({ka.md5_raw[:8]} vs {kb.md5_raw[:8]}) because the two "
                       f"binaries link the kernel's callees at different "
                       f"addresses -- {why}")


def check_adversarial(built, rep, adv_inputs, indir, cells):
    head("4. adversarial inputs -- behaviour recorded, not required to agree")
    table = {}
    # One representative build per cell keeps this readable; behaviour is an
    # attribute of the rung, and O0/O3 are re-run below to confirm that.
    for name in adv_inputs:
        mod = Model(os.path.join(indir, name))
        print(f"    -- {name}: n_iters={mod.n_iters} declared_len={mod.declared_len} "
              f"present={len(slb.read(os.path.join(indir, name)).payload)} "
              f"truncated={mod.truncated} -> model expects exit "
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
                table[(name, c)] = dict(exit=rc, stdout=out, stderr=err, signal=sig)
                flag = ""
                if rc != mod.expected_exit or out != mod.expected_stdout.strip():
                    flag = "  <-- diverges from model"
                print(f"       {c:18s} exit={rc!s:5s} stdout={out!r:24s}"
                      f" stderr={err!r:60s}{flag}")
            if len(seen) > 1:
                rep.note(f"{name}/{c}: opt/mode variants of this rung disagree "
                         f"({len(seen)} distinct behaviours)")
    return table


def check_proof_domain(pdir, rep, models, contract):
    head("5. proof domain must cover the measured domain")
    verus_src = os.path.join(pdir, "verus.rs")
    if not os.path.exists(verus_src):
        rep.fail("proof", "no verus.rs")
        return {}
    txt = open(verus_src).read()

    # --- rule 2: a *verified* call site -----------------------------------
    vm = re.search(r"^verus!\s*\{", txt, re.M)
    if not vm:
        rep.fail("proof-rule2", "verus.rs has no `verus! {` block")
        return {}
    verus_body = txt[vm.end():]
    items = parse_items(txt)
    main_item = next((i for i in items if i["name"] == "main"), None)
    if main_item is None:
        rep.fail("proof-rule2", "verus.rs has no `fn main`")
    else:
        bad = False
        if not main_item["in_verus"]:
            bad = True
            rep.fail("proof-rule2", "`fn main` is outside `verus! {}` -- the kernel "
                                    "call site is unverified (this is the pilot's bug)")
        if main_item["external"]:
            bad = True
            rep.fail("proof-rule2", f"`fn main` is {main_item['external']} -- no "
                                    f"precondition is ever discharged")
        if "kernel(" not in main_item["body"]:
            bad = True
            rep.fail("proof-rule2", "`fn main` does not call kernel(); the verified "
                                    "call site does not exist")
        if not bad:
            rep.ok("R5 call site: `fn main` is inside verus!, is not external_body, "
                   "and calls kernel()")
    kern = next((i for i in items if i["name"] == "kernel"), None)
    if kern is None or not kern["in_verus"]:
        rep.fail("proof-rule2", "kernel is not a verified item")
    elif kern["external"]:
        rep.fail("proof-rule2", f"kernel is {kern['external']}")
    elif "requires" not in kern["sig"]:
        rep.fail("proof-rule2", "kernel has no `requires` -- nothing to discharge")
    elif "ensures" not in kern["sig"]:
        rep.fail("proof-rule2", "kernel has no `ensures`")

    # TCB inventory -- reported so NOTES.md can be recounted against it
    tcb = [i for i in items if i["external"]]
    print(f"    TCB items in verus.rs ({len(tcb)}):")
    for i in tcb:
        print(f"       {i['external']:32s} {i['name']}  ({i['body_lines']} body lines)")
    for kw in ("assume(", "assume_specification", "admit("):
        n = len(re.findall(re.escape(kw), verus_body))
        if n:
            rep.note(f"{kw} appears {n}x in verus.rs -- must be justified in NOTES.md")

    # --- run the verifier -------------------------------------------------
    r = subprocess.run([sys.executable, os.path.join(REPO, "verus_run.py"), verus_src],
                       capture_output=True, text=True, cwd=REPO, timeout=RUN_TIMEOUT)
    out = (r.stdout + r.stderr).strip()
    m = re.search(r"(\d+) verified, (\d+) errors", out)
    if not m or int(m.group(2)) != 0 or int(m.group(1)) < 1:
        rep.fail("proof-verify", f"verus.rs did not verify cleanly: {out[-500:]}")
    else:
        rep.ok(f"verus.rs: {m.group(1)} verified, {m.group(2)} errors")

    # --- rules 1 and 3: evaluate the contract over the measured domain ----
    ns_base = {"wrapping_sum": None}
    stats = {}
    for name, mod in models.items():
        if not mod.calls:
            print(f"    {name}: 0 kernel calls (degenerate shape) -- vacuously inside "
                  f"the domain")
            stats[name] = dict(calls=0, requires_ok=True, ensures_checked=0)
            continue
        bad_req = None
        for off, ln, _ in mod.calls:
            env = {"off": off, "len": ln, "v_len": mod.v_len}
            for expr in contract["requires"]:
                if not eval(expr, {"__builtins__": {}}, env):
                    bad_req = (expr, off, ln, mod.v_len)
                    break
            if bad_req:
                break
        if bad_req:
            rep.fail("proof-rule1", f"{name}: requires {bad_req[0]!r} violated at "
                                    f"off={bad_req[1]} len={bad_req[2]} "
                                    f"v_len={bad_req[3]}")
        else:
            rep.ok(f"{name}: `requires` holds on all {len(mod.calls)} kernel calls "
                   f"(off range {min(c[0] for c in mod.calls)}.."
                   f"{max(c[0] for c in mod.calls)}, len={mod.calls[0][1]}, "
                   f"v_len={mod.v_len})")
        # ensures, re-derived with the independent naive sum on a sample
        step = max(1, len(mod.calls) // ENSURES_SAMPLE)
        sample = mod.calls[::step][:ENSURES_SAMPLE]
        bad_ens = None
        for off, ln, res in sample:
            env = dict(ns_base)
            env.update({"off": off, "len": ln, "v_len": mod.v_len, "result": res,
                        "v": mod.vals, "wrapping_sum": lambda v, o, l: mod.naive_sum(o, l)})
            for expr in contract["ensures"]:
                if not eval(expr, {"__builtins__": {}}, env):
                    bad_ens = (expr, off, ln, res)
                    break
            if bad_ens:
                break
        if bad_ens:
            rep.fail("proof-rule3", f"{name}: ensures {bad_ens[0]!r} violated at "
                                    f"off={bad_ens[1]} len={bad_ens[2]} "
                                    f"result={bad_ens[3]}")
        else:
            rep.ok(f"{name}: `ensures` re-derived independently on {len(sample)} "
                   f"sampled calls")
        stats[name] = dict(calls=len(mod.calls), requires_ok=bad_req is None,
                           ensures_checked=len(sample))
    return stats


def parse_items(txt):
    """Crude but adequate Rust item scanner: name, whether it sits inside the
    `verus! {}` block, which external attribute (if any) precedes it, its
    signature and its body. Good enough to answer `.memory/02-bench-rules.md`
    rule 2, which is a structural question."""
    verus_start = None
    m = re.search(r"^verus!\s*\{", txt, re.M)
    if m:
        verus_start = m.end()
    verus_end = len(txt)
    m2 = re.search(r"^\}\s*//\s*verus!", txt, re.M)
    if m2:
        verus_end = m2.start()
    items = []
    for m in re.finditer(r"^(?:pub\s+)?(?:exec\s+|open\s+|closed\s+)?"
                         r"(fn|spec fn|proof fn)\s+([A-Za-z_][A-Za-z0-9_]*)",
                         txt, re.M):
        pos = m.start()
        name = m.group(2)
        # attributes immediately above
        prefix = txt[max(0, pos - 400):pos]
        attrs = re.findall(r"#\[(verifier::[a-z_]+)\]", prefix.split("\n\n")[-1])
        external = next((a for a in attrs if a in
                         ("verifier::external_body", "verifier::external")), None)
        # body: from the first `{` after the signature to its matching `}`
        brace = txt.find("{", m.end())
        sig = txt[m.end():brace] if brace > 0 else ""
        body, depth, i = "", 0, brace
        while i < len(txt) and brace > 0:
            if txt[i] == "{":
                depth += 1
            elif txt[i] == "}":
                depth -= 1
                if depth == 0:
                    body = txt[brace + 1:i]
                    break
            i += 1
        items.append(dict(name=name, kind=m.group(1), sig=sig, body=body,
                          body_lines=len([l for l in body.splitlines() if l.strip()]),
                          external=external,
                          in_verus=verus_start is not None and
                          verus_start < pos < verus_end))
    return items


def check_driver_identity(pdir, rep):
    head("6. the driver loop is the same loop in every rung")
    rust = {}
    for f in sorted(os.listdir(pdir)):
        if f.endswith(".rs"):
            r = driver_region(os.path.join(pdir, f))
            if r is not None:
                rust[f] = r
    if len(rust) < 2:
        rep.fail("driver", "fewer than two Rust driver regions found")
        return
    ref_name, ref = sorted(rust.items())[0]
    for name, body in sorted(rust.items()):
        if body != ref:
            d = "\n".join(difflib.unified_diff(ref.splitlines(), body.splitlines(),
                                               ref_name, name, lineterm=""))
            rep.fail("driver", f"{name} driver loop differs from {ref_name}:\n{d}")
    if not any(f[0] == "driver" for f in rep.failures):
        rep.ok(f"{len(rust)} Rust rungs share a byte-identical driver loop "
               f"({len(ref.splitlines())} lines, Verus clauses excluded)")
    # C is compared by the arithmetic it must contain: a mechanical diff across
    # languages is not possible, so the equivalence argument lives in spec.md and
    # this is the guard against it silently drifting.
    cmain = os.path.join(pdir, "c", "main.c")
    creg = driver_region(cmain)
    if creg is None:
        rep.fail("driver", "c/main.c has no SLB-DRIVER region")
        return
    required = ["win_len_w > 0", "win_len_w <= (uint64_t)n_vals",
                "n_vals - win_len + 1", "acc % nwin",
                "kernel(vs, off, win_len)", "acc * 31 + r", "it < inp.n_iters"]
    missing = [s for s in required if s not in creg]
    if missing:
        rep.fail("driver", f"c/main.c driver loop is missing: {missing}")
    else:
        rep.ok("c/main.c driver loop carries the same arithmetic "
               f"({len(creg.splitlines())} lines, {len(required)} markers matched)")


def check_sanitizers(pdir, rep, indir, good, adv):
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
        return
    for name in list(good) + list(adv):
        rc, so, se = run_bin(out, os.path.join(indir, name))
        if "runtime error" in se or "AddressSanitizer" in se or "ERROR:" in se:
            rep.fail("sanitizer", f"{name}: {se.strip()[:300]}")
        else:
            print(f"    ok   {name:28s} exit={rc}")


# ==========================================================================

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pattern")
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--skip", action="append", default=[],
                    help="input stem to skip, e.g. --skip large")
    ap.add_argument("--cells", default="all", choices=["all", "measured"])
    a = ap.parse_args()

    pdir = buildmod.pattern_dir(a.pattern)
    cells = (buildmod.ALL_CELLS if a.cells == "all" else buildmod.MEASURED_CELLS)
    opts, modes = buildmod.OPTS, buildmod.MODES
    indir, good, adv = inputs_of(pdir, skip=a.skip)
    contract = read_contract(pdir)

    print(f"check.py: {os.path.basename(pdir)}")
    print(f"  cells   {cells}")
    print(f"  opts    {opts}   modes {modes}")
    print(f"  inputs  good={good} adversarial={adv}")
    print(f"  contract requires={contract['requires']} ensures={contract['ensures']}")

    rep = Report()
    check_asm_selftest(rep)

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

    models, _ = check_checksums(pdir, built, rep, good, indir)
    digests = check_no_collapse(built, rep)
    check_identity(digests, rep)
    check_adversarial(built, rep, adv, indir, cells)
    check_proof_domain(pdir, rep, models, contract)
    check_driver_identity(pdir, rep)
    check_sanitizers(pdir, rep, indir, good, adv)

    head("verdict")
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
