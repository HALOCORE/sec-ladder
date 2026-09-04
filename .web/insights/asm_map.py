#!/usr/bin/env python3
"""asm_map.py — attach a source line to every instruction in the assembly diffs.

    python3 insights/asm_map.py            # every pattern already in asmcache/
    python3 insights/asm_map.py p03 p17    # just these
    python3 insights/asm_map.py --stats    # coverage report, writes nothing

THE PROBLEM.

The measured binaries carry no line information for this project's code.
`safe_tuned.rs` appears in ZERO rows of their DWARF line table and the C kernels
resolve to `??:?`; the `.debug_line` that is present belongs to the precompiled
stdlib.  `harness/build.py` passes no `-g`, and it should not start — adding a
flag to it would stale every measurement record that hashes it.

THE ANSWER, AND HOW MUCH EACH LINE IS WORTH.

Build a throwaway TWIN with debug info and take the mapping from that.  The
assembly the page SHOWS still comes from the measured binary; only the line
numbers come from the twin.

`-g` is meant to be codegen-neutral, and for C it is — every C cell tested has an
identical `md5_fn` with and without it.  For Rust it is not: at `-O0` debug info
changes the instruction stream outright, and even at `-O3` register allocation
can shift.  So the twin is aligned against the measured kernel instruction by
instruction and every line carries a confidence — see `align()`:

    CERTAIN  the twin's whole stream matches; index N is index N
    LIKELY   the streams differ somewhere, but this instruction is inside an
             equal run of the alignment
    APPROX   inside a changed run; positionally anchored and no more

An earlier version refused the whole pair whenever the streams differed at all.
That was wrong by a wide margin: the WORST such case still aligns 97% of its
measured instructions into equal runs, so refusing threw away nearly everything
in order to avoid being wrong about nearly nothing.  What is refused now is only
a twin sharing less than half its instruction stream, which is a different
program rather than a variant.

⚠ THE MAPPING IS PARTIAL AT -O3 AND THE UI MUST SAY SO.  On p03's 82-instruction
tuned kernel: 60 map to `safe_tuned.rs` (9 of those with a file but no line), 22
to *inlined stdlib*, 0 to nothing — about 62% get a real line.  Scheduling also
scatters one source line's instructions through the function, so a line maps to
a set of ranges and never a single block.

Flags come from `harness/build.py`'s own `c_flags`/`rust_flags` plus the debug
flag, rather than being retyped here.  The twin is scratch and is deleted.
"""

import difflib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
REPO = os.path.dirname(WEB)
CACHE = os.path.join(WEB, "asmcache")
BUILD = os.path.join(REPO, ".temp", "build")
TWINS = os.path.join(WEB, ".temp", "dbgtwins")

sys.path.insert(0, os.path.join(REPO, "harness"))
import asm      # noqa: E402 — the one sanctioned objdump pipeline
import build    # noqa: E402 — reuse its flags rather than retyping them

MODE = "isolated"

# cell -> (language, source). C cells differ only by compiler and kernel file.
C_CELLS = {
    "c-gcc":     (build.GCC, "kernel.c"),
    "c-gcc-h":   (build.GCC, "kernel_hardened.c"),
    "c-clang":   (build.CLANG, "kernel.c"),
    "c-clang-h": (build.CLANG, "kernel_hardened.c"),
}


def twin_path(pid, cell, opt):
    os.makedirs(TWINS, exist_ok=True)
    return os.path.join(TWINS, f"{pid}-{cell}-{opt}")


def build_twin(pid, cell, opt):
    """Same build as the measured one, plus debug info. Returns a path or None."""
    pdir = os.path.join(build.PATTERNS, pid)
    out = twin_path(pid, cell, opt)
    if os.path.exists(out):
        return out

    if cell in C_CELLS:
        cc, kern = C_CELLS[cell]
        if not os.path.exists(os.path.join(pdir, "c", kern)):
            return None
        flags = build.c_flags(opt, MODE, "unwind") + ["-g"]
        cmd = [cc] + flags + ["-I", build.COMMON, "-I", os.path.join(pdir, "c")] + [
            os.path.join(build.COMMON, "driver.c"),
            os.path.join(pdir, "c", kern),
            os.path.join(pdir, "c", "main.c"),
        ] + ["-o", out]
    elif cell in build.RUST_SRC:
        src = os.path.join(pdir, build.RUST_SRC[cell])
        if not os.path.exists(src):
            return None
        flags = build.rust_flags(opt, MODE, "unwind") + ["-C", "debuginfo=2"]
        if cell in ("verus", "safe_naive_verus"):
            flags = [f for f in flags if f not in ("--edition", "2021")]
            cmd = [sys.executable, build.VERUS_RUN, "--compile", src, "-o", out] + flags
        else:
            cmd = [build.RUSTC] + flags + [src, "-o", out]
    else:
        return None

    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    except Exception:
        return None
    return out if (p.returncode == 0 and os.path.exists(out)) else None


# Confidence in one instruction's source line, and what earns it.
CERTAIN, LIKELY, APPROX = 2, 1, 0

# Below this the twin is not a variant of the measured kernel, it is a different
# program, and aligning them would be arithmetic rather than evidence.
MIN_RATIO = 0.5


def align(measured, twin):
    """Line up the measured kernel against its debug twin, instruction by
    instruction, and say how much each pairing is worth.

    `-g` is meant to be codegen-neutral.  For C it is — every C cell tested
    comes out with an identical `md5_fn`.  For Rust it is not: at `-O0` debug
    info changes the instruction stream outright (271 against 415 on p27's
    verus rung) and even at `-O3` register allocation can shift.

    Refusing those outright was the first design and it was wrong: the WORST
    refused case still aligns 97% of its measured instructions into equal runs,
    so it threw away almost everything to avoid being wrong about almost
    nothing.  What it should do instead is grade:

      CERTAIN  the twin's whole instruction stream matches the measured one, so
               index N is index N by construction
      LIKELY   the streams differ somewhere, but THIS instruction sits inside an
               equal run of the alignment — same text at a corresponding
               position.  Almost always the same source construct; not
               guaranteed, which is why it is not called certain
      APPROX   inside a changed run.  Positionally anchored, and no more

    Returns (level, idx, conf, why) where idx[i] is the twin index for measured
    instruction i (or None) and conf[i] is one of the three above.
    """
    try:
        km, kt = asm.try_kernel(measured), asm.try_kernel(twin)
    except Exception as exc:
        return None, None, None, f"disassembly failed: {exc}"
    if km is None or kt is None:
        return None, None, None, "no kernel symbol in one of the two"

    nm = [asm.normalise_text(i.text) for i in km.insns_fn]
    nt = [asm.normalise_text(i.text) for i in kt.insns_fn]

    if nm == nt and km.md5_fn_norel == kt.md5_fn_norel:
        why = ("identical to the measured kernel" if km.md5_fn == kt.md5_fn
               else "identical instruction stream; addresses relocated")
        return "exact", list(range(len(nm))), [CERTAIN] * len(nm), why

    sm = difflib.SequenceMatcher(None, nm, nt, autojunk=False)
    ratio = sm.ratio()
    if ratio < MIN_RATIO:
        return None, None, None, (f"twin shares only {ratio:.0%} of the measured "
                                  "instruction stream — too different to align")

    idx, conf = [None] * len(nm), [APPROX] * len(nm)
    equal = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        for k in range(i2 - i1):
            j = j1 + k
            if tag == "equal":
                idx[i1 + k] = j
                conf[i1 + k] = LIKELY
                equal += 1
            elif j < j2:                       # positional anchor inside the run
                idx[i1 + k] = j
    return "partial", idx, conf, (f"{equal}/{len(nm)} instructions in matching runs "
                                  f"({km.n_fn} against {kt.n_fn} in the twin)")


def resolve_lines(twin, kernel, own_basename):
    """One addr2line call for the whole kernel. Returns a list, one per
    instruction: a positive int (a line in the rung's own source), -1 (inlined
    from another file) or 0 (no information)."""
    addrs = [hex(i.addr) for i in kernel.insns_fn]
    if not addrs:
        return [], {}
    try:
        p = subprocess.run(["addr2line", "-e", twin] + addrs,
                           capture_output=True, text=True, timeout=180)
    except Exception:
        return [0] * len(addrs), {}
    out = p.stdout.splitlines()
    lines, foreign = [], {}
    for idx, raw in enumerate(out[:len(addrs)]):
        raw = raw.strip()
        base = raw.rsplit("/", 1)[-1]
        fname, _, lno = base.rpartition(":")
        if not fname or raw.startswith("??"):
            lines.append(0); continue
        if fname == own_basename:
            lines.append(int(lno) if lno.isdigit() else 0)
        else:
            lines.append(-1)
            foreign[str(idx)] = f"{fname}:{lno}" if lno.isdigit() else fname
    lines += [0] * (len(addrs) - len(lines))
    return lines, foreign


def map_pair(pid, pair_id, opt, d, log):
    """Attach per-side source lines, with a confidence, to one cached diff."""
    sides = {}
    for side in ("a", "b"):
        cell = d[side]["cell"]
        measured = os.path.join(BUILD, pid.split("-")[0], f"{cell}-{opt}-{MODE}")
        if not os.path.exists(measured):
            log.append(f"{pair_id}/{opt}/{side}: measured binary gone")
            return False
        twin = build_twin(pid, cell, opt)
        if not twin:
            log.append(f"{pair_id}/{opt}/{side}: twin build failed ({cell})")
            return False
        level, idx, conf, why = align(measured, twin)
        if level is None:
            log.append(f"{pair_id}/{opt}/{side}: {why}")
            return False

        kt = asm.kernel(twin)
        own = os.path.basename(
            C_CELLS[cell][1] if cell in C_CELLS else build.RUST_SRC.get(cell, ""))
        # resolve_lines is indexed by TWIN instruction; the diff is indexed by
        # MEASURED instruction, so carry it across via the alignment
        tlines, tforeign = resolve_lines(twin, kt, own)
        lines, foreign = [], {}
        for i, j in enumerate(idx):
            if j is None or j >= len(tlines):
                lines.append(0)
                continue
            lines.append(tlines[j])
            if str(j) in tforeign:
                foreign[str(i)] = tforeign[str(j)]
        sides[side] = (lines, conf, foreign, level, why)

    # Walk the ops, consuming each side's instruction stream in step. `-` ops
    # advance only A, `+` only B, ` ` both — the same order the diff was built
    # in, so index N of each list lands on the op it came from.
    al, bl, ac, bc, fx = [], [], [], [], {}
    ia = ib = 0
    la, ca, fa, _la, _wa = sides["a"]
    lb, cb, fb, _lb, _wb = sides["b"]
    for n, op in enumerate(d["ops"]):
        k = op[0]
        if k == "@":
            skip = int(op[1:])
            ia += skip; ib += skip
            al.append(0); bl.append(0); ac.append(0); bc.append(0); continue
        a_line = b_line = 0
        a_conf = b_conf = 0
        if k in (" ", "-"):
            if ia < len(la):
                a_line, a_conf = la[ia], ca[ia]
                if a_line == -1 and str(ia) in fa:
                    fx[str(n)] = fa[str(ia)]
            ia += 1
        if k in (" ", "+"):
            if ib < len(lb):
                b_line, b_conf = lb[ib], cb[ib]
                if b_line == -1 and str(ib) in fb and str(n) not in fx:
                    fx[str(n)] = fb[str(ib)]
            ib += 1
        al.append(a_line); bl.append(b_line)
        ac.append(a_conf); bc.append(b_conf)

    d["map"] = {"al": al, "bl": bl, "ac": ac, "bc": bc, "fx": fx}
    # the weaker of the two sides is what the pair as a whole is worth
    d["map_level"] = "exact" if sides["a"][3] == sides["b"][3] == "exact" else "partial"
    d["map_note"] = {"a": sides["a"][4], "b": sides["b"][4]}
    return True


def stats(m):
    """(own-source, inlined, total, certain, likely, approx) over both sides."""
    own = foreign = total = 0
    tiers = [0, 0, 0]
    for lines, confs in ((m["al"], m["ac"]), (m["bl"], m["bc"])):
        for x, c in zip(lines, confs):
            if x == 0:
                continue
            total += 1
            if x > 0:
                own += 1
                tiers[c] += 1
            else:
                foreign += 1
    return own, foreign, total, tiers[CERTAIN], tiers[LIKELY], tiers[APPROX]


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    stats_only = "--stats" in sys.argv

    pids = sorted(f[:-5] for f in os.listdir(CACHE) if f.endswith(".json")) \
        if os.path.isdir(CACHE) else []
    if argv:
        pids = [p for p in pids if any(p.startswith(a) or p == a for a in argv)]

    mapped = skipped = 0
    tot_own = tot_foreign = tot_all = 0
    tier = [0, 0, 0]
    levels = {"exact": 0, "partial": 0}
    for pid in pids:
        path = os.path.join(CACHE, pid + ".json")
        data = json.load(open(path, encoding="utf-8"))
        log, n = [], 0
        for pair_id, by_opt in (data.get("pairs") or {}).items():
            for opt, d in by_opt.items():
                if stats_only:
                    if "map" in d:
                        o, f, t, c, l, a = stats(d["map"])
                        tot_own += o; tot_foreign += f; tot_all += t
                        tier[0] += a; tier[1] += l; tier[2] += c
                        levels[d.get("map_level", "partial")] += 1
                    continue
                if map_pair(pid, pair_id, opt, d, log):
                    n += 1
                    o, f, t, c, l, a = stats(d["map"])
                    tot_own += o; tot_foreign += f; tot_all += t
                    tier[0] += a; tier[1] += l; tier[2] += c
                    levels[d.get("map_level", "partial")] += 1
        if stats_only:
            continue
        if n:
            data["mapped"] = True
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, separators=(",", ":"), sort_keys=True)
            mapped += 1
        else:
            skipped += 1
        print(f"  {pid:22} {n} diff(s) mapped" + (f"   ** {len(log)} refused" if log else ""))
        for m in log:
            print(f"      {m}", file=sys.stderr)

    if tot_all:
        print(f"\ncoverage: {tot_own}/{tot_all} instructions map to their own source "
              f"({100*tot_own/tot_all:.0f}%), {tot_foreign} inlined from elsewhere")
        print(f"confidence: {tier[2]} certain · {tier[1]} likely · {tier[0]} approximate")
        print(f"diffs: {levels['exact']} exact-twin, {levels['partial']} partial-twin")
    if not stats_only:
        print(f"asm_map: {mapped} pattern(s) mapped, {skipped} without any")
        shutil.rmtree(TWINS, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
