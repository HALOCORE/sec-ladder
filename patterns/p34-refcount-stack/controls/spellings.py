#!/usr/bin/env python3
"""p34 CONTROLS: **the IN-CONTRACT SPELLING SEARCH, on BOTH sides, because six
patterns have published a headline wrong in the FLATTERING direction.**

    python3 patterns/p34-refcount-stack/controls/spellings.py

WHY
---
`TASK_154` deliverable 4, and it is not a style rule: `p10`, `p27`, `p38`,
`p22`, `p36` and `p35` all published a rung-to-rung cost figure taken with one
endpoint searched and the other left at whatever the author wrote first, and
**`p35`'s R4 side WINS by 6.63% once given R3's own two levers**. So a pattern
that publishes a rung-to-rung number owes a search on BOTH endpoints and a
sentence naming the weaker-searched one.

⚠ **`p34` therefore publishes the marginal table as DATA and one rung-to-rung
figure with this file beside it**, and `NOTES.md` 5 states the span rather than
the point. What it does NOT need a search for is the R1-vs-R1h figure, which is
`0.00` on all sixteen cells: that number supports the statement *the safety line
is never executed*, and no respelling of anything can move a statement about a
statement that does not run.

THE VARIANTS, all produced by TEXT SUBSTITUTION from the shipped rungs so that
they cannot drift from what ships
-----------------------------------------------------------------------------
  `r3_cursor`      R3 with R2's CURSOR WALK instead of
                   `chunks_exact(2).take(nops)`, and R3's `match` kept. The
                   op-stream walk is the R3 lever `../spec.md`'s why key
                   deliberately leaves unpinned, and this isolates it.
  `r4_checked`     R4 with `arr_get_unchecked` / `arr_set_unchecked` on the
                   POINTER STACK replaced by plain indexing. ⚠ This is the p27
                   control re-derived on p34 rather than inherited: p27's
                   41.62 Ir/call figure is about p27's table, not this stack.
  `r4_readdirect`  R4 with the payload read spelled `r.data[0]` instead of
                   `arr_get_unchecked(&r.data, 0)`. The index is the literal 0
                   into a `[u8; 8]`, so rustc should elide the check -- and if
                   it does, this spelling is FREE and removes one use of a
                   trusted item, which is a strictly better R4 if the number
                   agrees.

⚠⚠ **THE R4 SIDE IS THE WEAKER-SEARCHED ENDPOINT AND THE REASON IS STRUCTURAL,
NOT LAZINESS.** `../spec.md` pins `identity: unsafe == verus`, so an R4 is not
merely a program that MAY use `unsafe`: it is a program that must have a
machine-code-identical R5 that Verus verifies. Every R4 candidate therefore has
to be put through Verus before it is a rung at all, and this script does that --
it applies the SAME substitution to `verus.rs` and records whether the result
verifies. A variant that does not is a control and not a rung, which is p16's
`r4_hdr` and p05's `c4_hu16_nz` precedent.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * every variant builds and returns the model's checksum on every input --
    a respelling that changed the answer would not be a respelling;
  * the marginal Ir of each variant is measured at BOTH optimisation levels on
    BOTH probe inputs, exactly as `harness/check.py` measures the shipped cells
    (a difference of two runs of the same binary at 100 and 200 iterations);
  * each R4 variant's Verus admissibility is recorded, so the published span is
    over spellings that could actually occupy the rung.
"""

import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
INPUTS = os.path.join(PDIR, "inputs")
OUT = os.path.join(REPO, ".temp", "p34ctl")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
RUSTC = os.environ.get("SLB_RUSTC", os.path.expanduser("~/.cargo/bin/rustc"))
VERUS_RUN = os.path.join(REPO, "verus_run.py")

PROBE_INPUTS = ("small.bin", "large.bin")
PROBE_ITERS = (100, 200)

# ---- the substitutions -----------------------------------------------------
R3_CHUNKS = """    for op in buf[off + 4..off + len].chunks_exact(2).take(nops) {
        let c: u8 = op[0];
        let a: u8 = op[1];
        match c % 4 {"""
R3_CURSOR = """    let mut p: usize = 4;
    let mut o: usize = 0;
    while o < nops {
        if len - p < 2 {
            break;
        }
        let c: u8 = buf[off + p];
        let a: u8 = buf[off + p + 1];
        p = p + 2;
        o = o + 1;
        match c % 4 {"""

R4_CHECKED = [
    ("arr_set_unchecked(&mut stk, ntop, q);", "stk[ntop] = q;"),
    ("let t = arr_get_unchecked(&stk, ntop - 1);", "let t = stk[ntop - 1];"),
    ("arr_set_unchecked(&mut stk, ntop, t);", "stk[ntop] = t;"),
    ("let q = arr_get_unchecked(&stk, ntop);", "let q = stk[ntop];"),
    ("obj_read(arr_get_unchecked(&stk, (a as usize) % ntop))",
     "obj_read(stk[(a as usize) % ntop])"),
    # verus.rs binds the READ index first, so it has its own spelling.
    ("obj_read(arr_get_unchecked(&stk, j), Tracked(tp))",
     "obj_read(stk[j], Tracked(tp))"),
]
R4_READDIRECT = [
    ("arr_get_unchecked(&r.data, 0)", "r.data[0]"),
    ("arr_get_unchecked(&ptr_ref(p, Tracked(pt)).data, 0)",
     "ptr_ref(p, Tracked(pt)).data[0]"),
]

#: name -> (rung file, [(find, replace)], verify_with_verus)
VARIANTS = {
    "r3_cursor": ("safe_tuned.rs", [(R3_CHUNKS, R3_CURSOR)], False),
    "r4_checked": ("unsafe.rs", R4_CHECKED, True),
    "r4_readdirect": ("unsafe.rs", R4_READDIRECT, True),
}
SHIPPED = {"safe_naive": "safe_naive.rs", "safe_tuned": "safe_tuned.rs",
           "unsafe": "unsafe.rs"}


def sh(cmd, **kw):
    env = dict(os.environ)
    env.pop("LD_PRELOAD", None)
    return subprocess.run(cmd, capture_output=True, text=True, env=env,
                          timeout=3600, **kw)


def substitute(src_path, subs, out_path, depth_fix=True):
    txt = open(src_path).read()
    for find, repl in subs:
        if find not in txt:
            # A substitution that does not apply to THIS file is fine only when
            # it is the other file's spelling of the same edit; every variant
            # below has at least one that does apply, and `applied` records it.
            continue
        txt = txt.replace(find, repl)
    if depth_fix:
        txt = txt.replace('#[path = "../../common/driver.rs"]',
                          '#[path = "' + os.path.join(REPO, "common",
                                                      "driver.rs") + '"]')
    open(out_path, "w").write(txt)
    return txt


def applied(src_path, subs):
    txt = open(src_path).read()
    return sum(1 for find, _ in subs if find in txt)


def build(src, out, opt):
    r = sh([RUSTC, "-C", f"opt-level={opt}", "-C", "debug-assertions=off",
            "-C", "codegen-units=1", "--cfg", "slb_isolated", src, "-o", out])
    if r.returncode != 0:
        raise SystemExit(f"spellings.py: build failed on {src} at O{opt}:\n"
                         f"{(r.stdout + r.stderr)[-2000:]}")
    return out


def probe(src, n_iters, out):
    blob = open(src, "rb").read()
    with open(out, "wb") as f:
        f.write(struct.pack("<Q", n_iters) + blob[8:])
    return out


def cg_total(binary, arg, outfile):
    r = sh([VALGRIND, "--tool=callgrind", f"--callgrind-out-file={outfile}",
            binary, arg])
    if r.returncode != 0:
        return None
    for line in open(outfile):
        if line.startswith("summary:") or line.startswith("totals:"):
            return int(line.split()[1])
    return None


def marginal(binary, inp):
    a = cg_total(binary, probe(os.path.join(INPUTS, inp), PROBE_ITERS[0],
                               os.path.join(OUT, f"sp-i100-{inp}")),
                 os.path.join(OUT, "sp-a.out"))
    b = cg_total(binary, probe(os.path.join(INPUTS, inp), PROBE_ITERS[1],
                               os.path.join(OUT, f"sp-i200-{inp}")),
                 os.path.join(OUT, "sp-b.out"))
    if a is None or b is None:
        return None
    return (b - a) / float(PROBE_ITERS[1] - PROBE_ITERS[0])


def run(path, arg):
    return sh([path, arg]).stdout.strip()


def verus_ok(path):
    r = sh([sys.executable, VERUS_RUN, path], cwd=REPO)
    txt = r.stdout + r.stderr
    m = re.search(r"verification results:: (\d+) verified, (\d+) errors", txt)
    kinds = sorted({ln.split("error:")[1].strip().split("\n")[0][:70]
                    for ln in txt.splitlines() if ln.startswith("error:")})
    return {"verified": int(m.group(1)) if m else None,
            "errors": int(m.group(2)) if m else None,
            "rc": r.returncode, "error_kinds": kinds[:3]}


def derived_from():
    out = {}
    for rel in ("patterns/p34-refcount-stack/safe_naive.rs",
                "patterns/p34-refcount-stack/safe_tuned.rs",
                "patterns/p34-refcount-stack/unsafe.rs",
                "patterns/p34-refcount-stack/verus.rs",
                "patterns/p34-refcount-stack/controls/spellings.py",
                "patterns/p34-refcount-stack/inputs/gen.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    sys.path.insert(0, PDIR)
    import model as M  # noqa: E402

    names = sorted(f for f in os.listdir(INPUTS)
                   if f.endswith(".bin") and not f.startswith("sweep-"))
    expect = {n: str(M.build(os.path.join(INPUTS, n)).checksum) for n in names}
    problems, rows = [], {}

    # ---- the shipped cells, re-measured here so the span is self-contained --
    todo = [(k, v, [], False) for k, v in SHIPPED.items()]
    todo += [(k, v[0], v[1], v[2]) for k, v in VARIANTS.items()]

    for name, rung, subs, verify in todo:
        src = os.path.join(PDIR, rung)
        vpath = os.path.join(OUT, f"sp-{name}.rs")
        substitute(src, subs, vpath)
        n_applied = applied(src, subs)
        if subs and n_applied == 0:
            problems.append(f"{name}: no substitution applied to {rung} -- the "
                            f"rung moved under this script and the variant is "
                            f"a copy of the shipped cell")
        row = {"rung": rung, "substitutions_applied": n_applied,
               "checksums": {}, "marginal": {}}
        for opt in ("0", "3"):
            b = build(vpath, os.path.join(OUT, f"sp-{name}-O{opt}"), opt)
            if opt == "3":
                for n in names:
                    got = run(b, os.path.join(INPUTS, n))
                    row["checksums"][n] = got
                    if got != expect[n]:
                        problems.append(
                            f"{name}/{n}: checksum {got} != model {expect[n]} "
                            f"-- a respelling that changes the answer is not a "
                            f"respelling")
            for inp in PROBE_INPUTS:
                m = marginal(b, inp)
                row["marginal"][f"O{opt}/{inp}"] = m
                print(f"  {name:14s} O{opt} {inp:10s} marginal={m:12.2f}")
                sys.stdout.flush()
        if verify:
            vsrc = os.path.join(OUT, f"sp-{name}-verus.rs")
            substitute(os.path.join(PDIR, "verus.rs"), subs, vsrc,
                       depth_fix=False)
            # `.temp/p34ctl/` is two levels below the repo root, so the rung's
            # own `#[path = "../../common/driver.rs"]` still resolves.
            row["verus"] = verus_ok(vsrc)
            print(f"  {name:14s} verus: {row['verus']['verified']}/"
                  f"{row['verus']['errors']} {row['verus']['error_kinds']}")
        rows[name] = row

    # ---- the span, per side -------------------------------------------------
    def span(names_, key):
        vals = [(n, rows[n]["marginal"][key]) for n in names_
                if rows[n]["marginal"].get(key) is not None]
        vals.sort(key=lambda t: t[1])
        return {"cheapest": vals[0], "dearest": vals[-1],
                "width": vals[-1][1] - vals[0][1]}

    spans = {}
    for key in [f"O{o}/{i}" for o in ("0", "3") for i in PROBE_INPUTS]:
        spans[key] = {
            "R3_side": span(["safe_tuned", "r3_cursor"], key),
            "R4_side": span(["unsafe", "r4_checked", "r4_readdirect"], key),
            "R2_shipped": rows["safe_naive"]["marginal"][key],
        }
        s = spans[key]
        print(f"\n{key}:  R3 side {s['R3_side']['cheapest'][1]:.2f} .. "
              f"{s['R3_side']['dearest'][1]:.2f} (width "
              f"{s['R3_side']['width']:.2f})   "
              f"R4 side {s['R4_side']['cheapest'][1]:.2f} .. "
              f"{s['R4_side']['dearest'][1]:.2f} (width "
              f"{s['R4_side']['width']:.2f})")

    doc = {"pin": {"regenerate": "python3 patterns/p34-refcount-stack/controls/"
                                 "spellings.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "probe_iters": list(PROBE_ITERS),
           "variants": rows,
           "spans": spans,
           "problems": problems,
           "weaker_searched_endpoint": (
               "THE R4 SIDE. spec.md pins `identity: unsafe == verus`, so every "
               "R4 candidate must also verify before it is a rung, and this "
               "file measures two candidates and records their Verus verdicts. "
               "The R3 side is free of that constraint and therefore cheaper to "
               "search, so a published R3-minus-R4 figure is an UPPER BOUND on "
               "the R3 side and a POINT on the R4 side. `.memory/01-ladder.md` "
               "finding 14: cheapest FOUND, never minimum."),
           "invariant": "Every variant returns the model's checksum on every "
                        "input; the marginal Ir of each is measured at both "
                        "optimisation levels on both probe inputs; and each R4 "
                        "variant's Verus verdict is recorded, because the "
                        "identity pin makes an unverified R4 a control rather "
                        "than a rung."}
    out = os.path.join(HERE, "spellings.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"\nwrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
