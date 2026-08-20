#!/usr/bin/env python3
"""p13 control: the IN-CONTRACT R3-SIDE SPAN, with every variant audited.

`.memory/02-bench-rules.md`, "NEVER re-ship a rung": the shipped rung is chosen
by idiom, before measurement, and it stays. What a cheaper in-contract spelling
moves is the **published bound**, and two numbers ship, labelled:

    fixed-R4 bound                 R3ship - R4ship        (both held by fiat)
    cheapest-found in-contract     inf(found) - R4ship    (name the spelling
                                                           AND the input)

and TASK_026 §0 item 4: no pair interval. If the R4 side does not move, say
**degenerate**, which is falsifiable.

Every variant here is checked against `harness/check.py::spelling_matches` for
every backticked entry in ../spec.md's `idiom` **before** its number is quoted --
TASK_043 asks for exactly that, and p05's lesson is that a variant nobody audited
is a number about a different benchmark.

    python3 patterns/p13-strncpy-trunc/controls/spellings.py
    python3 patterns/p13-strncpy-trunc/controls/spellings.py --audit-only

Scratch under `.temp/p13/spellings/`.
"""

import argparse
import json
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, os.path.join(REPO, "harness"))
SCRATCH = os.path.join(REPO, ".temp", "p13", "spellings")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
BUILD = os.path.join(REPO, ".temp", "build", "p13")
LO, HI = 100, 200

# Each variant is (name, why, [(old, new, hits)]) applied to the SHIPPED
# safe_tuned.rs by exact-string substitution with an asserted hit count, so a
# variant cannot drift away from the rung it claims to be a respelling of.
VARIANTS = [
    ("v0_shipped", "the shipped R3, unmodified", []),
    ("v1_onestep_reslice",
     "the reslice spelled `&buf[off..off + len]` instead of the two-step "
     "`split_at` -- `.memory/01-ladder.md` finding 3 measured the two-step form "
     "at -1 Ir/call on p04, from REGISTER ALLOCATION and not from a deleted "
     "bounds check. p13 spelled it the cheap way from the start; this variant "
     "is the expensive one, measured rather than inherited",
     [("    let w: &[u8] = buf.split_at(off).1.split_at(len).0;\n",
       "    let w: &[u8] = &buf[off..off + len];\n", 1)]),
    ("v2_takewhile_consumer",
     "the consumer spelled `dst.iter().take_while(|&&b| b != 0).count()` "
     "instead of `position(...).unwrap_or(DST_CAP)` -- both are total, both "
     "return DST_CAP on a destination with no NUL, and the `idiom` entry that "
     "pins the consumer scopes to the OTHER three Rust rungs, so both are in "
     "contract",
     [("        let d: usize = dst.iter().position(|&b| b == 0).unwrap_or(DST_CAP);\n",
       "        let d: usize = dst.iter().take_while(|&&b| b != 0).count();\n", 1)]),
    ("v3_byteloop_copy",
     "the copy and the fill spelled as R2's byte loops instead of "
     "`copy_from_slice`/`fill` -- in contract because the byte-loop entry "
     "scopes to safe_naive/unsafe/verus and nothing forbids R3 from agreeing "
     "with them",
     [("""        dst[..n].copy_from_slice(&w[p..p + n]);
        dst[n..].fill(0);
""",
       """        let mut i: usize = 0;
        while i < n {
            dst[i] = w[p + i];
            i = i + 1;
        }
        let mut j: usize = n;
        while j < DST_CAP {
            dst[j] = 0;
            j = j + 1;
        }
""", 1)]),
    ("v4_fill_explicit_end",
     "the zero-fill spelled `dst[n..DST_CAP].fill(0)` instead of "
     "`dst[n..].fill(0)` -- the same operation with the end named",
     [("        dst[n..].fill(0);\n", "        dst[n..DST_CAP].fill(0);\n", 1)]),
]


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def contract():
    t = open(os.path.join(PDIR, "spec.md")).read()
    return json.loads(re.search(r"```slb-contract\s*\n(.*?)```", t, re.S).group(1))


def backticked(entry, lang):
    txt = entry if isinstance(entry, str) else entry.get(lang, "")
    return re.findall(r"`([^`]+)`", txt)


def audit(src_text, c):
    """Every backticked spelling of every `required`/`forbidden` rust entry,
    against this variant, using check.py's own `spelling_matches`."""
    import check
    req, forb = [], []
    for e in c["idiom"]["required"]:
        for sp in backticked(e, "rust"):
            req.append((sp, check.spelling_matches(sp, src_text)))
    for e in c["idiom"]["forbidden"]:
        for sp in backticked(e, "rust"):
            forb.append((sp, check.spelling_matches(sp, src_text)))
    return req, forb


def probe(src, n_iters, out):
    blob = open(src, "rb").read()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(struct.pack("<Q", n_iters) + blob[8:])
    return out


def cg_ir(binary, arg, tag):
    out = os.path.join(SCRATCH, f"cg.{tag}.out")
    rc, o, e = sh([VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + out,
                   "-q", binary, arg])
    if rc != 0:
        raise SystemExit(f"callgrind rc={rc}: {e[:300]}")
    tot = None
    with open(out) as f:
        for ln in f:
            if ln.startswith(("summary:", "totals:")):
                tot = int(ln.split()[1])
    os.remove(out)
    return tot


def marginal(binary, name):
    indir = os.path.join(PDIR, "inputs")
    lo = probe(os.path.join(indir, name), LO, os.path.join(SCRATCH, f"p.{name}.lo"))
    hi = probe(os.path.join(indir, name), HI, os.path.join(SCRATCH, f"p.{name}.hi"))
    a = cg_ir(binary, lo, f"{os.path.basename(binary)}.{name}.lo")
    z = cg_ir(binary, hi, f"{os.path.basename(binary)}.{name}.hi")
    os.remove(lo)
    os.remove(hi)
    return (z - a) / float(HI - LO)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit-only", action="store_true")
    ap.add_argument("--inputs", default="small.bin,large.bin")
    a = ap.parse_args()
    os.makedirs(SCRATCH, exist_ok=True)
    c = contract()
    base = open(os.path.join(PDIR, "safe_tuned.rs")).read()
    names = a.inputs.split(",")

    r4 = os.path.join(BUILD, "unsafe-O3-isolated")
    rows = []
    for name, why, subs in VARIANTS:
        txt = base
        for old, new, hits in subs:
            if txt.count(old) != hits:
                raise SystemExit(f"{name}: substitution matched "
                                 f"{txt.count(old)}, expected {hits}")
            txt = txt.replace(old, new)
        path = os.path.join(SCRATCH, f"{name}.rs")
        with open(path, "w") as f:
            f.write(txt)
        req, forb = audit(txt, c)
        miss = [s for s, ok in req if not ok]
        hit = [s for s, ok in forb if ok]
        print(f"\n=== {name} ===\n  {why}")
        print(f"  spelling audit: {sum(1 for _, ok in req if ok)}/{len(req)} "
              f"rust `required` spellings present; "
              f"{len(hit)} `forbidden` spelling(s) present")
        if miss:
            print(f"    absent required: {miss}")
        if hit:
            print(f"    !! FORBIDDEN PRESENT: {hit}")
        in_contract = not hit
        rows.append({"name": name, "why": why, "required_present":
                     sum(1 for _, ok in req if ok), "required_total": len(req),
                     "required_absent": miss, "forbidden_present": hit,
                     "in_contract": in_contract})
        if a.audit_only:
            continue
        binary = os.path.join(SCRATCH, f"{name}.bin")
        rc, o, e = sh([RUSTC, "--edition", "2021", "-C", "codegen-units=1",
                       "-C", "opt-level=3", "-C", "debug-assertions=off",
                       "--cfg", "slb_isolated", path, "-o", binary])
        if rc != 0:
            print((o + e)[:2000])
            raise SystemExit(f"{name}: build failed")
        rows[-1]["ir"] = {}
        for nm in names:
            got = sh([binary, os.path.join(PDIR, "inputs", nm)])[1].strip()
            rows[-1]["ir"][nm] = marginal(binary, nm)
            rows[-1].setdefault("checksum", {})[nm] = got
        os.remove(binary)

    if a.audit_only:
        return 0

    r4ir = {nm: marginal(r4, nm) for nm in names}
    print("\n" + "=" * 74)
    print("IN-CONTRACT R3-SIDE SPAN (Ir per call, O3 isolated)")
    print("=" * 74)
    print(f"  {'variant':24s} " + " ".join(f"{nm:>14s}" for nm in names)
          + "   in contract")
    for r in rows:
        print(f"  {r['name']:24s} "
              + " ".join(f"{r['ir'][nm]:14.2f}" for nm in names)
              + f"   {'yes' if r['in_contract'] else 'NO'}")
    print(f"  {'R4 (unsafe, shipped)':24s} "
          + " ".join(f"{r4ir[nm]:14.2f}" for nm in names))
    # checksum sanity: every variant must still print the shipped answer
    bad = [r["name"] for r in rows
           if any(r["checksum"][nm] != rows[0]["checksum"][nm] for nm in names)]
    print(f"\n  checksum agreement across variants: "
          f"{'ALL AGREE' if not bad else 'DISAGREE: ' + str(bad)}")
    for nm in names:
        vals = {r["name"]: r["ir"][nm] for r in rows if r["in_contract"]}
        lo_n = min(vals, key=vals.get)
        hi_n = max(vals, key=vals.get)
        ship = vals["v0_shipped"]
        print(f"\n  --- {nm} ---")
        print(f"    fixed-R4 bound          R3ship - R4ship = "
              f"{ship - r4ir[nm]:+.2f} Ir/call")
        print(f"    cheapest found          {lo_n} = {vals[lo_n]:.2f}, "
              f"so inf(in-contract found) - R4ship = "
              f"{vals[lo_n] - r4ir[nm]:+.2f} Ir/call")
        print(f"    R3-side span            {vals[lo_n]:.2f} .. {vals[hi_n]:.2f} "
              f"= width {vals[hi_n] - vals[lo_n]:.2f}  "
              f"({lo_n} .. {hi_n})")
    out = os.path.join(SCRATCH, "spellings.json")
    with open(out, "w") as f:
        json.dump({"variants": rows, "r4": r4ir}, f, indent=1)
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
