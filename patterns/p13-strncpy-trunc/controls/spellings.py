#!/usr/bin/env python3
"""p13 control: the IN-CONTRACT SPAN ON BOTH SIDES, with every variant audited.

`.memory/02-bench-rules.md`, "NEVER re-ship a rung": the shipped rung is chosen
by idiom, before measurement, and it stays. What a cheaper in-contract spelling
moves is the **published bound**, and two numbers ship, labelled:

    fixed-R4 bound                 R3ship - R4ship        (both held by fiat)
    cheapest-found in-contract     inf(found) - R4ship    (name the spelling
                                                           AND the input)

and TASK_026 §0 item 4: no pair interval.

**TASK_046 ADDS THE R4 SIDE, and it had to.** Until TASK_046 ../spec.md pinned
the byte-loop copy and fill in safe_naive.rs, unsafe.rs and verus.rs and
exempted safe_tuned.rs BY NAME, so only the SAFE side of the published
`R3 - R4` headline was permitted the bulk spelling, and this file said "the R4
side is not searched" and blamed the prover. **The prover does not bind here**
-- an admissible bulk R4/R5 pair verifies (`controls/gen_bulk_r5.py`) -- so the
entries were relaxed symmetrically and the R4 side is searched below. R4ship is
NOT re-spelled; what moves is the published bound.

Every variant here is checked against `harness/check.py::spelling_matches` for
every backticked entry in ../spec.md's `idiom` **before** its number is quoted --
TASK_043 asks for exactly that, and p05's lesson is that a variant nobody audited
is a number about a different benchmark. And the token audit is not the whole
admission test: `admissible` is three-valued, because ../spec.md's per-entry
ENGLISH decides polarity and scope and no gate stage reproduces it.

    python3 patterns/p13-strncpy-trunc/controls/spellings.py
    python3 patterns/p13-strncpy-trunc/controls/spellings.py --audit-only
    python3 patterns/p13-strncpy-trunc/controls/spellings.py --verus

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
     "contract. Neither is available to an R4/R5 pair: both are iterator "
     "methods and `position` is not supported at the pinned vstd "
     "(controls/gen_bulk_r5.py)",
     [("        let d: usize = dst.iter().position(|&b| b == 0).unwrap_or(DST_CAP);\n",
       "        let d: usize = dst.iter().take_while(|&&b| b != 0).count();\n", 1)]),
    ("v3_byteloop_copy",
     "the copy and the fill spelled as R2's byte loops instead of "
     "`copy_from_slice`/`fill` -- in contract because since TASK_046 the "
     "copy and fill entries pin no Rust loop form at all, in either "
     "direction",
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

# ---------------------------------------------------------------------------
# THE R4-SIDE SPAN (TASK_046). Until TASK_046 ../spec.md pinned the byte-loop
# copy and fill in safe_naive.rs, unsafe.rs and verus.rs and exempted
# safe_tuned.rs BY NAME, so only the SAFE side of the published `R3 - R4`
# comparison was permitted the bulk spelling. TASK_045_REVIEW measured the
# direction and the entries were relaxed symmetrically; this is the search that
# relaxation makes meaningful. Applied to the SHIPPED unsafe.rs, same asserted
# hit counts.
#
# `admissible` is a THREE-valued field and the third value is the point:
#   "yes"   in contract on tokens AND reachable by an R5 (run --verus)
#   "no"    a `forbidden` spelling is present
#   "fiat"  in contract on tokens, but excluded by the entry's ENGLISH, which
#           no gate stage reproduces. Priced rather than asserted.
U4_COPY_OLD = """        let mut i: usize = 0;
        while i < n {
            let b: u8 = unsafe { *buf.get_unchecked(off + p + i) };
            unsafe { *dst.get_unchecked_mut(i) = b; }
            i = i + 1;
        }
"""
U4_COPY_NEW = """        unsafe {
            core::ptr::copy_nonoverlapping(buf.as_ptr().add(off + p),
                                           dst.as_mut_ptr(), n);
        }
"""
U4_FILL_OLD = """        let mut j: usize = n;
        while j < DST_CAP {
            unsafe { *dst.get_unchecked_mut(j) = 0; }
            j = j + 1;
        }
"""
U4_FILL_NEW = """        unsafe {
            core::ptr::write_bytes(dst.as_mut_ptr().add(n), 0u8, DST_CAP - n);
        }
"""
U4_CONS_OLD = """        let mut d: usize = 0;
        while unsafe { *dst.get_unchecked(d) } != 0 {
            d = d + 1;
        }
"""
U4_CONS_NEW = """        let mut d: usize = 0;
        while d < DST_CAP && unsafe { *dst.get_unchecked(d) } != 0 {
            d = d + 1;
        }
"""

U_VARIANTS = [
    ("u0_shipped", "the shipped R4, unmodified", "yes", []),
    ("u1_bulk_copyfill",
     "the copy and the fill spelled `copy_nonoverlapping` and `write_bytes` -- "
     "the unsafe-side analogue of what R3 does with `copy_from_slice`/`fill`. "
     "In contract since TASK_046 relaxed the byte-loop entries symmetrically, "
     "and REACHABLE BY AN R5: it verifies at 17/0 shipped and 24/0 under "
     "--cfg slb_twin, at a cost of TWO new trusted items (TCB 5 -> 7) -- run "
     "--verus",
     "yes", [(U4_COPY_OLD, U4_COPY_NEW, 1), (U4_FILL_OLD, U4_FILL_NEW, 1)]),
    ("u2_bulk_copy", "the copy only, fill left as a byte loop",
     "yes", [(U4_COPY_OLD, U4_COPY_NEW, 1)]),
    ("u3_bulk_fill", "the fill only, copy left as a byte loop",
     "yes", [(U4_FILL_OLD, U4_FILL_NEW, 1)]),
    ("u4_bounded_consumer",
     "the consumer BOUNDED -- `while d < DST_CAP && ...` instead of the "
     "unbounded scan. It matches every backticked spelling, including the "
     "consumer entry's `d = d + 1;`, and it VERIFIES (19/0 and 22/0, the "
     "SHIPPED counts unmoved, with no new trusted item), so neither the token "
     "audit nor the prover excludes it. What "
     "excludes it is the consumer entry's ENGLISH -- 'an unbounded scan' -- "
     "and the pattern's subject: a bounded consumer turns p13's two-site "
     "obligation into a loop bound and stops R4/R5 being a matched spelling "
     "against R1's runaway scan. Held by FIAT, and this is its price",
     "fiat", [(U4_CONS_OLD, U4_CONS_NEW, 1)]),
    ("u5_bulk_and_bounded",
     "everything at once: bulk copy, bulk fill AND a bounded consumer. Not an "
     "endpoint either -- it inherits u4's fiat -- but it is the cheapest R4 "
     "anybody on this project has built, so `R3ship - u5` is the strongest "
     "form of the headline's sign test: if R3 is still cheaper than THIS, the "
     "sign does not rest on any pin, any fiat or any prover limitation",
     "fiat", [(U4_COPY_OLD, U4_COPY_NEW, 1), (U4_FILL_OLD, U4_FILL_NEW, 1),
              (U4_CONS_OLD, U4_CONS_NEW, 1)]),
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


def build_variant(base, name, subs):
    """Apply the substitutions, assert each hit count, write the source."""
    txt = base
    for old, new, hits in subs:
        if txt.count(old) != hits:
            raise SystemExit(f"{name}: substitution matched "
                             f"{txt.count(old)}, expected {hits}")
        txt = txt.replace(old, new)
    path = os.path.join(SCRATCH, f"{name}.rs")
    with open(path, "w") as f:
        f.write(txt)
    return txt, path


def r4_side(c, names, audit_only, run_verus):
    """THE R4-SIDE SPAN. See `U_VARIANTS`."""
    base = open(os.path.join(PDIR, "unsafe.rs")).read()
    rows = []
    for name, why, adm, subs in U_VARIANTS:
        txt, path = build_variant(base, name, subs)
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
        row = {"name": name, "why": why, "admissible": "no" if hit else adm,
               "required_present": sum(1 for _, ok in req if ok),
               "required_total": len(req), "required_absent": miss,
               "forbidden_present": hit}
        rows.append(row)
        if audit_only:
            continue
        binary = os.path.join(SCRATCH, f"{name}.bin")
        rc, o, e = sh([RUSTC, "--edition", "2021", "-C", "codegen-units=1",
                       "-C", "opt-level=3", "-C", "debug-assertions=off",
                       "--cfg", "slb_isolated", path, "-o", binary])
        if rc != 0:
            print((o + e)[:2000])
            raise SystemExit(f"{name}: build failed")
        row["ir"] = {}
        for nm in names:
            row.setdefault("checksum", {})[nm] = sh(
                [binary, os.path.join(PDIR, "inputs", nm)])[1].strip()
            row["ir"][nm] = marginal(binary, nm)
        os.remove(binary)
    if run_verus:
        verus_side()
    return rows


def verus_side():
    """Is the cheapest R4 candidate REACHABLE BY AN R5? `identity: exact` binds
    R4 to a byte-identical R5, so an R4 spelling with no admissible R5 is a
    control and not a rung (../spec.md's `why`, and p05/p16's precedent). This
    builds the R5 twin of `u1_bulk_copyfill` and runs Verus on it in both
    configurations, and it also runs the bounded-consumer R5 -- the one held by
    FIAT -- so that "the prover does not exclude it" is a measurement."""
    import gen_bulk_r5
    for label, path in gen_bulk_r5.emit(SCRATCH):
        for cfg in ([], ["--cfg", "slb_twin"]):
            rc, o, e = sh([sys.executable, os.path.join(REPO, "verus_run.py"),
                           path] + cfg)
            last = [l for l in (o + e).splitlines() if "verification results" in l]
            print(f"  verus {label:22s} {' '.join(cfg) or '(shipped cfg)':16s} "
                  f"{last[-1].split('::')[-1].strip() if last else (o + e)[-200:]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit-only", action="store_true")
    ap.add_argument("--inputs", default="small.bin,large.bin")
    ap.add_argument("--verus", action="store_true",
                    help="also put the R4-side candidates' R5 twins through "
                         "Verus (adds ~4 minutes)")
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

    urows = r4_side(c, names, a.audit_only, a.verus)
    print("\n" + "=" * 74)
    print("R4-SIDE SPAN (Ir per call, O3 isolated) -- TASK_046")
    print("=" * 74)
    print(f"  {'variant':24s} " + " ".join(f"{nm:>14s}" for nm in names)
          + "   admissible")
    for r in urows:
        print(f"  {r['name']:24s} "
              + " ".join(f"{r['ir'][nm]:14.2f}" for nm in names)
              + f"   {r['admissible']}")
    ubad = [r["name"] for r in urows
            if any(r["checksum"][nm] != urows[0]["checksum"][nm] for nm in names)]
    print(f"\n  checksum agreement across R4 variants: "
          f"{'ALL AGREE' if not ubad else 'DISAGREE: ' + str(ubad)}")
    for nm in names:
        adm = {r["name"]: r["ir"][nm] for r in urows if r["admissible"] == "yes"}
        fiat = {r["name"]: r["ir"][nm] for r in urows if r["admissible"] == "fiat"}
        u_lo = min(adm, key=adm.get)
        r3ship = rows[0]["ir"][nm]
        print(f"\n  --- {nm} ---")
        print(f"    fixed-R4 bound          R3ship - R4ship = "
              f"{r3ship - r4ir[nm]:+.2f} Ir/call "
              f"({100 * (r3ship - r4ir[nm]) / r4ir[nm]:+.2f}%)")
        print(f"    cheapest-found PAIR     R3ship - inf(in-contract R4) = "
              f"{r3ship - adm[u_lo]:+.2f} Ir/call "
              f"({100 * (r3ship - adm[u_lo]) / adm[u_lo]:+.2f}%)   [{u_lo}]")
        print(f"    R4-side span            {adm[u_lo]:.2f} .. "
              f"{max(adm.values()):.2f} = width "
              f"{max(adm.values()) - adm[u_lo]:.2f}")
        for k, v in fiat.items():
            print(f"    held by FIAT            {k} = {v:.2f} "
                  f"({v - r4ir[nm]:+.2f} vs R4ship) -- NOT an endpoint, "
                  f"R3ship - it = {r3ship - v:+.2f}")

    out = os.path.join(SCRATCH, "spellings.json")
    with open(out, "w") as f:
        json.dump({"variants": rows, "r4": r4ir, "r4_variants": urows}, f,
                  indent=1)
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
