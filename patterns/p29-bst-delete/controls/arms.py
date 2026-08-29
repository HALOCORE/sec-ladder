#!/usr/bin/env python3
"""p29 CONTROLS: the safety-line arms that were measured and NOT shipped.

`TASK_137` established that p29 had **two** exact candidates for the safety
line, not one, and `TASK_139` chose between them on a stated criterion. This
script is the committed form of that measurement: it derives every arm from the
SHIPPED `c/kernel.c` by textual substitution, so an arm can never drift away
from the rung it is a variant of, builds them all, and scores them against the
pattern's own checked semantics.

    python3 patterns/p29-bst-delete/controls/arms.py            # measure, write JSON
    python3 patterns/p29-bst-delete/controls/arms.py --windows 800

The arms:

    R1          the shipped bug: `if (g_saved != NULL)`
    R1h         the shipped safety line: both conjuncts        <- SHIPPED
    liveonly    R1h minus the OCCUPANT-IDENTITY conjunct
    keyonly     R1h minus the LIVENESS conjunct
    deref       `keyonly` spelled through the saved POINTER (TASK_136's `H4`)
    H2          the WRITE-PATH alternative: `if (tab[cur] == g_saved)
                g_saved = NULL;` at the top of the deletion loop, one site,
                with R1's USE line unchanged                   <- the loser,
                                                                 kept measured
and each of them again under `-DNULLTAB`, which restores `tab[cur] = NULL;`
after the free -- the deviation from `p27`'s convention that ../spec.md refuses.

⚠ **`rm` the binaries when you are done**; `.memory/00-environment.md`
constraint 6. This script deletes its own `.b/` directory on success.
"""

import argparse
import hashlib
import json
import os
import random
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, os.path.join(PDIR, "inputs"))
import gen as G  # noqa: E402  -- the generator's Sim is the checked semantics

GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")
BDIR = os.path.join(REPO, ".temp", "p29ctl")

ENV = dict(os.environ)
ENV.pop("LD_PRELOAD", None)          # ASan fails to start under LD_PRELOAD
ENV["ASAN_OPTIONS"] = "detect_leaks=0"

R1_LINE = "            if (g_saved != NULL) {"
R1H_LINE = ("            if (g_saved != NULL && live[g_slot] == 1 "
            "&& tab[g_slot][0] == g_key) {")
FREE_LINE = "                        free(tab[cur]);"
GUARD_LINE = "                    guard++;"

ARMS = {
    "R1": R1_LINE,
    "R1h": R1H_LINE,
    "liveonly": "            if (g_saved != NULL && live[g_slot] == 1) {",
    "keyonly": "            if (g_saved != NULL && tab[g_slot][0] == g_key) {",
    "deref": "            if (g_saved != NULL && g_saved[0] == g_key) {",
    "H2": R1_LINE,          # + the write-path line, spliced below
}


def source(arm, nulltab):
    """The shipped R1 kernel with ONE line substituted. Nothing else moves."""
    src = open(os.path.join(PDIR, "c", "kernel.c")).read()
    if R1_LINE not in src:
        raise SystemExit("arms.py: c/kernel.c no longer contains the R1 USE "
                         "line this script substitutes; update R1_LINE")
    src = src.replace(R1_LINE, ARMS[arm], 1)
    if arm == "H2":
        if GUARD_LINE not in src:
            raise SystemExit("arms.py: cannot find the deletion loop's guard "
                             "increment; update GUARD_LINE")
        src = src.replace(
            GUARD_LINE,
            GUARD_LINE + "\n"
            "                    if (tab[cur] == g_saved)\n"
            "                        g_saved = NULL;", 1)
    if nulltab:
        if FREE_LINE not in src:
            raise SystemExit("arms.py: cannot find the free; update FREE_LINE")
        src = src.replace(FREE_LINE, FREE_LINE + "\n"
                          "                        tab[cur] = NULL;", 1)
    return src


def build(arm, nulltab, san):
    tag = f"{arm}{'-null' if nulltab else ''}{'-asan' if san else ''}"
    os.makedirs(BDIR, exist_ok=True)
    csrc = os.path.join(BDIR, f"k_{arm}{'n' if nulltab else ''}.c")
    open(csrc, "w").write(source(arm, nulltab))
    out = os.path.join(BDIR, tag)
    cmd = [GCC, "-std=c99", "-Wall", "-Wextra", "-O1", "-DSLB_ISOLATED",
           "-I", os.path.join(REPO, "common"), "-I", os.path.join(PDIR, "c")]
    if san:
        cmd += ["-fsanitize=address", "-g"]
    cmd += [os.path.join(REPO, "common", "driver.c"), csrc,
            os.path.join(PDIR, "c", "main.c"), "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True, env=ENV, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit(f"arms.py: build failed for {tag}:\n{r.stderr}")
    warn = [ln for ln in r.stderr.splitlines() if "warning:" in ln]
    return out, warn


def run(binpath, path):
    r = subprocess.run([binpath, path], capture_output=True, text=True,
                       env=ENV, timeout=120)
    txt = r.stdout + r.stderr
    hits = txt.count("AddressSanitizer")
    kind = ""
    for line in txt.splitlines():
        if "ERROR: AddressSanitizer:" in line:
            kind = line.split("ERROR: AddressSanitizer:")[1].strip().split()[0]
            break
    val = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return (val if r.returncode == 0 else f"rc={r.returncode}"), hits, kind


def write_input(path, ops, rng, n_iters=1):
    body = G.encode(rng, ops)
    payload = G.slb.pack_head1_bytes(len(body), body)
    G.slb.write(path, n_iters, payload)
    return body


def expected(body):
    return G._walk(body)[0]


def fuzz_ops(rng, nops):
    """Keys from a SMALL pool, and half the REMOVEs target the key the last
    FIND used, so both bug classes appear. A uniform draw over a wide key range
    produces almost no two-child victims at all."""
    pool = list(range(1, 14))
    ops, last = [], rng.choice(pool)
    for _ in range(nops):
        r = rng.random()
        if r < 0.30:
            ops.append((G.INSERT, rng.choice(pool)))
        elif r < 0.48:
            last = rng.choice(pool)
            ops.append((G.FIND, last))
        elif r < 0.70:
            ops.append((G.REMOVE,
                        last if rng.random() < 0.5 else rng.choice(pool)))
        else:
            ops.append((G.USE, rng.randrange(0, 256)))
    return ops


def derived_from():
    """The staleness pin `harness/check.py` stage 9b reads."""
    out = {}
    for rel in ("patterns/p29-bst-delete/c/kernel.c",
                "patterns/p29-bst-delete/c/kernel.h",
                "patterns/p29-bst-delete/c/main.c",
                "patterns/p29-bst-delete/inputs/gen.py",
                "patterns/p29-bst-delete/controls/arms.py",
                "common/driver.c"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--windows", type=int, default=500)
    ap.add_argument("--seed", type=int, default=20260830)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    names = list(ARMS)
    warns = set()

    plain, asan, nplain, nasan = {}, {}, {}, {}
    for n in names:
        plain[n], w = build(n, False, False)
        warns |= set(w)
        asan[n], _ = build(n, False, True)
        nplain[n], _ = build(n, True, False)
        nasan[n], _ = build(n, True, True)

    inp = os.path.join(BDIR, "in.slb")
    wins = []
    for _ in range(a.windows):
        ops = fuzz_ops(rng, rng.randrange(8, 46))
        wins.append(ops)

    # classify each window by which bug class R1 lands in
    cls, want = [], []
    for ops in wins:
        body = write_input(inp, ops, random.Random(7))
        want.append(str(expected(body)))
        v, _h, _k = run(asan["R1"], inp)
        if v.startswith("rc="):
            cls.append("UAF")
            continue
        v, _h, _k = run(plain["R1"], inp)
        cls.append("RECYCLE" if v != want[-1] else "benign")

    res = {}
    for n in names:
        tot = u = r = lines = ntot = nlines = 0
        kinds, nkinds = set(), set()
        for ops, k, w in zip(wins, cls, want):
            body = write_input(inp, ops, random.Random(7))
            v, _h, _kd = run(plain[n], inp)
            if v != w:
                tot += 1
                u += (k == "UAF")
                r += (k == "RECYCLE")
            _v, h2, kd = run(asan[n], inp)
            lines += h2
            if kd:
                kinds.add(kd)
            v3, _h, _kd = run(nplain[n], inp)
            if v3 != w:
                ntot += 1
            _v, h4, kd2 = run(nasan[n], inp)
            nlines += h4
            if kd2:
                nkinds.add(kd2)
        res[n] = {"wrong_total": tot, "wrong_on_uaf": u, "wrong_on_recycle": r,
                  "asan_lines": lines, "asan_classes": sorted(kinds),
                  "nulltab_wrong_total": ntot, "nulltab_asan_lines": nlines,
                  "nulltab_asan_classes": sorted(nkinds)}

    # ASan positive control: the probe must be able to see a use-after-free.
    pc = os.path.join(BDIR, "posctl")
    open(os.path.join(BDIR, "posctl.c"), "w").write(
        "#include <stdlib.h>\n#include <stdio.h>\n"
        "int main(void){char*p=malloc(8);p[0]=1;free(p);"
        "printf(\"%d\\n\",(int)p[0]);return 0;}\n")
    subprocess.run([GCC, "-std=c99", "-O1", "-g", "-fsanitize=address",
                    os.path.join(BDIR, "posctl.c"), "-o", pc], check=True,
                   env=ENV)
    r = subprocess.run([pc], capture_output=True, text=True, env=ENV)
    txt = r.stdout + r.stderr
    pcinfo = {"rc": r.returncode, "hits": txt.count("AddressSanitizer"),
              "class": next((ln.split("ERROR: AddressSanitizer:")[1].strip()
                             .split()[0] for ln in txt.splitlines()
                             if "ERROR: AddressSanitizer:" in ln), "")}

    doc = {
        "pin": {"regenerate":
                "python3 patterns/p29-bst-delete/controls/arms.py",
                # ⚠⚠ TASK_141, and it is `p23`'s `k_selfpivot` class in this
                # pattern: a green pin does NOT make every cell below
                # reproducible. Four draws of this script over the same corpus
                # and seed, three of them on one tree state:
                #   keyonly / deref  wrong_total, wrong_on_uaf: 7, 8, 7, 7
                #   EVERY OTHER CELL, all six arms:              constant 4/4
                # The reason is structural, not environmental: `keyonly` and
                # `deref` are the two arms that DELETE THE LIVENESS CONJUNCT,
                # so their identity test reads FREED memory by construction and
                # whether the stale bytes still spell the old key is a draw.
                # The arms that do not read freed memory do not move.
                "not_covered": [
                    "keyonly.wrong_total / keyonly.wrong_on_uaf and the same "
                    "two cells of deref: measured 7, 8, 7, 7 over four draws "
                    "(TASK_139 + TASK_141 x3). They are a DRAW, not a figure, "
                    "because both arms read freed memory by construction. "
                    "../NOTES.md 2b publishes the INVARIANT -- deleting the "
                    "liveness conjunct costs ASan lines and few wrong answers, "
                    "deleting the identity conjunct costs every recycle window "
                    "and zero ASan lines -- and marks these two cells as a "
                    "draw. Do not quote either as a fixed number.",
                    "the C toolchain: SLB_GCC defaults to /usr/bin/gcc and is "
                    "not hashed, so a compiler bump moves these counts and "
                    "nothing here fires.",
                ]},
        "derived_from_sha256": derived_from(),
        "windows": a.windows,
        "seed": a.seed,
        "classes": {"UAF": cls.count("UAF"), "RECYCLE": cls.count("RECYCLE"),
                    "benign": cls.count("benign")},
        "arms": res,
        "asan_positive_control": pcinfo,
        "compiler_warnings": sorted(warns),
        "note": "Every arm is c/kernel.c with ONE line substituted; `H2` also "
                "splices the write-path line into the deletion loop. "
                "`wrong_*` is measured on the PLAIN build against the "
                "generator's checked semantics; `asan_lines` on the "
                "`-fsanitize=address` build over the same corpus. "
                "`nulltab_*` is the same source with `tab[cur] = NULL;` "
                "restored after the free -- ../spec.md refuses that spelling "
                "and this is the measurement behind the refusal.",
    }
    out = os.path.join(HERE, "arms.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(json.dumps(doc["classes"], indent=2))
    for n in names:
        print(f"  {n:10s} {res[n]}")
    print(f"ASan positive control: {pcinfo}")
    print(f"wrote {out}")
    # Keep the generator, delete the artefact.
    for f in os.listdir(BDIR):
        os.remove(os.path.join(BDIR, f))
    os.rmdir(BDIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
