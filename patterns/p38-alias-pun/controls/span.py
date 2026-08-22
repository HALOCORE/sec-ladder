#!/usr/bin/env python3
"""p38's R3-side span and R4-side search, both in contract.

`.memory/01-ladder.md` finding 14 and RECAP: `R3ship - R4ship` bounds
`inf(in-contract R3) - R4ship` **and nothing else**, and it is a bound only
because R4 is held fixed BY FIAT. *"Degenerate as far as this task searched"*
was false on two consecutive patterns (p10, p27) and both times it flattered the
safe rung, so the R4 side is searched here even though p38 expects it to be
degenerate -- and **every R4 candidate is put through Verus before its number is
quoted**, because a rung covered by the `identity` pin is chained to the prover
(TASK_026 §0 item 3). Read the ERROR TEXT: `is not supported` disqualifies;
`postcondition not satisfied` does not.

    python3 patterns/p38-alias-pun/controls/span.py            # all
    python3 patterns/p38-alias-pun/controls/span.py --only r4_end
"""

import argparse
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p38", "span")
assert OUT.endswith(os.path.join("p38", "span")), OUT
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
VERUS_RUN = os.path.join(REPO, "verus_run.py")
INPUTS = os.path.join(PDIR, "inputs")

R3 = os.path.join(PDIR, "safe_tuned.rs")
R4 = os.path.join(PDIR, "unsafe.rs")
R5 = os.path.join(PDIR, "verus.rs")

# ---- the fold loop, in each rung's shipped spelling -------------------------
R3_FOLD = """        let seg: &[u16] = &sc[i + 2..i + 2 + 2 * n];
        let mut k: usize = 0;
        while k < seg.len() {
            acc = acc.wrapping_mul(31).wrapping_add(seg[k] as u64);
            k = k + 1;
        }"""

R4_FOLD = """        let mut k: usize = 0;
        while k < 2 * n {
            acc = acc.wrapping_mul(31).wrapping_add(unsafe {
                *sc.get_unchecked(i + 2 + k) as u64
            });
            k = k + 1;
        }"""

R5_FOLD_HEAD = """        let mut k: usize = 0;"""

VARIANTS = {
    # ---------------- R3 side ------------------------------------------------
    "r3_iter": ("safe_tuned.rs", [(R3_FOLD, """        let seg: &[u16] = &sc[i + 2..i + 2 + 2 * n];
        let mut it = seg.iter();
        while let Some(x) = it.next() {
            acc = acc.wrapping_mul(31).wrapping_add(*x as u64);
        }""")], "fold the reslice with an iterator instead of an index"),

    "r3_noreslice": ("safe_tuned.rs", [(R3_FOLD, """        let mut k: usize = 0;
        while k < 2 * n {
            acc = acc.wrapping_mul(31).wrapping_add(sc[i + 2 + k] as u64);
            k = k + 1;
        }""")], "index `sc` directly -- R2's fold with R3's decode"),

    "r3_wholeslice": ("safe_tuned.rs", [(R3_FOLD, """        let seg: &[u16] = &sc[i + 2..i + 2 + 2 * n];
        let mut k: usize = 0;
        while k < seg.len() {
            acc = acc.wrapping_mul(31).wrapping_add(seg[k] as u64);
            k = k + 1;
        }
        let _ = &sc[..nw];""")], "reslice plus a hoisted whole-window assertion"),

    # ---------------- R4 side ------------------------------------------------
    "r4_end": ("unsafe.rs", [(R4_FOLD, """        let end: usize = i + 2 + 2 * n;
        let mut k: usize = i + 2;
        while k < end {
            acc = acc.wrapping_mul(31).wrapping_add(unsafe {
                *sc.get_unchecked(k) as u64
            });
            k = k + 1;
        }""")], "walk the payload with an absolute cursor and a precomputed end"),

    "r4_slice": ("unsafe.rs", [(R4_FOLD, """        let seg: &[u16] = unsafe { sc.get_unchecked(i + 2..i + 2 + 2 * n) };
        let mut k: usize = 0;
        while k < seg.len() {
            acc = acc.wrapping_mul(31).wrapping_add(unsafe {
                *seg.get_unchecked(k) as u64
            });
            k = k + 1;
        }""")], "unchecked RESLICE, then unchecked indexing inside it"),
}

# R4 variants need a Verus twin. Same substitution against verus.rs, with the
# trusted accessor in place of `get_unchecked`.
R5_TWINS = {
    "r4_end": ("""        let mut k: usize = 0;
        // THE PAYLOAD FOLD. Single exit, so a plain `invariant` suffices; the
        // clause is one unfolding of `wfold` per step and there is no lemma.
        while k < 2 * n
            invariant
                k <= 2 * n,""", """        let end: usize = i + 2 + 2 * n;
        let mut k: usize = i + 2;
        // THE PAYLOAD FOLD, respelled with an absolute cursor.
        while k < end
            invariant
                i + 2 <= k <= end,
                end == i + 2 + 2 * n,"""),
}


def rewrite(path, subs, name):
    src = open(os.path.join(PDIR, path)).read()
    for old, new in subs:
        if old not in src:
            raise SystemExit(f"span.py: {name}: substitution stale against {path}")
        src = src.replace(old, new, 1)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"{name}.rs")
    open(p, "w").write(src)
    return p


def build(p, name):
    exe = os.path.join(OUT, name)
    r = subprocess.run([RUSTC, "--edition", "2021", "-C", "codegen-units=1",
                        "-C", "opt-level=3", "-C", "debug-assertions=off",
                        "--cfg", "slb_isolated", p, "-o", exe],
                       capture_output=True, text=True)
    if r.returncode:
        return None, r.stderr[-500:]
    return exe, ""


def probe(blob, n):
    b = open(os.path.join(INPUTS, blob), "rb").read()
    o = os.path.join(OUT, f"probe-{n}-{blob}")
    open(o, "wb").write(struct.pack("<Q", n) + b[8:])
    return o


def ir(exe, arg):
    o = os.path.join(OUT, f"cg.{os.getpid()}")
    r = subprocess.run([VALGRIND, "--tool=callgrind", f"--callgrind-out-file={o}",
                        exe, arg], capture_output=True, text=True, timeout=1800)
    if r.returncode:
        return None
    for line in open(o):
        if line.startswith(("summary:", "totals:")):
            return int(line.split()[1])
    return None


def marginal(exe, blob, lo=100, hi=200):
    a, b = ir(exe, probe(blob, lo)), ir(exe, probe(blob, hi))
    return None if a is None or b is None else (b - a) / (hi - lo)


def checksum(exe, blob):
    r = subprocess.run([exe, os.path.join(INPUTS, blob)],
                       capture_output=True, text=True, timeout=600)
    return r.stdout.strip()


def verus_of(name):
    if name not in R5_TWINS:
        return "no twin written"
    old, new = R5_TWINS[name]
    src = open(R5).read()
    if old not in src:
        return "TWIN SUBSTITUTION STALE"
    p = os.path.join(OUT, f"{name}_verus.rs")
    open(p, "w").write(src.replace(old, new, 1))
    r = subprocess.run([sys.executable, VERUS_RUN, p], capture_output=True,
                       text=True, timeout=1800)
    txt = r.stdout + r.stderr
    ns = [ln for ln in txt.splitlines() if "is not supported" in ln]
    m = re.search(r"verification results:: (\d+) verified, (\d+) error", txt)
    tag = m.group(0) if m else "no result line"
    return tag + ("   *** is not supported: " + ns[0][:80] if ns else "")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    names = a.only or list(VARIANTS)
    os.makedirs(OUT, exist_ok=True)

    base = {}
    for tag, path in (("R3ship", "safe_tuned.rs"), ("R4ship", "unsafe.rs"),
                      ("R2ship", "safe_naive.rs")):
        p = os.path.join(PDIR, path)
        exe, err = build(p, tag)
        if not exe:
            raise SystemExit(f"span.py: baseline {tag} failed: {err}")
        base[tag] = (marginal(exe, "small.bin"), marginal(exe, "large.bin"),
                     checksum(exe, "small.bin"))
        print(f"{tag:14s} small={base[tag][0]:9.2f}  large={base[tag][1]:9.2f}   "
              f"checksum {base[tag][2]}")
    print()

    for name in names:
        path, subs, why = VARIANTS[name]
        p = rewrite(path, subs, name)
        exe, err = build(p, name)
        if not exe:
            print(f"{name:14s} BUILD FAILED: {err[:200]}")
            continue
        s, l = marginal(exe, "small.bin"), marginal(exe, "large.bin")
        cs = checksum(exe, "small.bin")
        ref = "R3ship" if path == "safe_tuned.rs" else "R4ship"
        ok = "same checksum" if cs == base[ref][2] else f"CHECKSUM DIFFERS {cs}"
        print(f"{name:14s} small={s:9.2f}  large={l:9.2f}   "
              f"vs {ref}: {s - base[ref][0]:+8.2f} / {l - base[ref][1]:+8.2f}   {ok}")
        print(f"               {why}")
        if path == "unsafe.rs":
            print(f"               Verus twin: {verus_of(name)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
