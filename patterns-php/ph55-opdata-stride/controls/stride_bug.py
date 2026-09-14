#!/usr/bin/env python3
"""ph55 control -- **THE TWO ADVERSARIAL CASES, PRICED SEPARATELY, IN BOTH
LANGUAGES. ONE BYTE APART, AND ONE OF THEM NOTHING SEES.**

    python3 patterns-php/ph55-opdata-stride/controls/stride_bug.py
    python3 patterns-php/ph55-opdata-stride/controls/stride_bug.py --selftest

⭐⭐⭐ **THE QUESTION THIS ROW EXISTS TO ANSWER, AND IT IS SHARPER THAN "safe
Rust catches it".** The defect is a CONTROL-FLOW error -- a wrong program
counter. The NULL call is only how it MANIFESTS. So the question is *does the
dispatch representation catch the wrong PC, and what does the catch cost?* --
and the answer has two halves that a single adversarial input cannot separate:

  `inputs/adversarial-nullcall.bin`      the mis-strided PC lands on a word
                                         whose handler is NULL. C calls address
                                         zero; a Rust port carrying the SAME BUG
                                         panics on the `Option`.
  `inputs/adversarial-opdatalive.bin`    the mis-strided PC lands on a word that
                                         DOES have a handler. C executes it; a
                                         Rust port carrying the same bug executes
                                         it too, **bit for bit**, and nothing
                                         anywhere notices.

**The two blobs differ in ONE BYTE** -- the opcode field of the trailing data
word -- and `inputs/gen.py` asserts that rather than describing it. So the
`Option` catches the NULL; it does not catch the wrong PC.

⚠⚠ **THE RUST ROWS ARE MUTANTS, NOT RUNGS.** Every shipped Rust rung implements
R1h and never mis-strides, so a table built from the shipped binaries would be
all-green and say nothing. This file MATERIALISES the bug into each Rust rung by
exact-string substitution -- deleting `4f68f3774c34`'s three lines from the error
exit -- and **asserts the hit count**, so a mutant cannot silently fail to be a
mutant. That is the whole reason the numbers below are comparable to `c/kernel.c`
at all: it is the same defect in four languages' worth of rungs.

⚠ It also answers stage 7h's question as a by-product: on every BENIGN input R1
and R1h agree, which is what makes `4f68f3774c34` a COMPLETE fix for this defect
rather than a behaviour change. That half is `fix_scope()` and it runs every time.

§H (`PROTOCOL_PHP.md`): the verdict functions are functions so they can be
attacked, and `--selftest` drives them over synthetic rows -- five must-FIRE and
four must-NOT-fire -- because the shipped tree's `problems` is empty and a green
run is no evidence that any arm CAN fire.
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PDIR))

sys.path.insert(0, HERE)
import _pin  # noqa: E402

SCRATCH = os.path.join(ROOT, ".temp", "php55-stride")

#: `rustc` is not on a subprocess's PATH unless rustup's bin dir is put there.
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
CC = "gcc"

#: The three lines `4f68f3774c34` adds, as each Rust rung spells them. Deleting
#: them turns that rung into R1. ⚠ THE HIT COUNT IS ASSERTED: a substitution
#: that matched zero times, or twice, would produce a "mutant" that is not one.
FIX_SUBS = {
    "safe_naive.rs": ("""                if increment_opline {
                    pc = pc + 1;
                }
                pc = pc + 1; // NEXT_OPCODE(), :1769""",
                      """                pc = pc + 1; // :1769 -- R1: STRIDE 1, unconditionally"""),
    "safe_tuned.rs": ("""                if increment_opline {
                    pc = pc + 1;
                }
                pc = pc + 1; // NEXT_OPCODE(), :1769""",
                      """                pc = pc + 1; // :1769 -- R1: STRIDE 1, unconditionally"""),
    "unsafe.rs": ("""                if increment_opline {
                    pc = pc + 1; // 4f68f3774c34
                }
                pc = pc + 1; // :1769""",
                  """                pc = pc + 1; // :1769 -- R1: STRIDE 1, unconditionally"""),
    # ⚠ The control has TWO `if increment_opline { ex.pc += 1; } ex.pc += 1;`
    # blocks -- the error exit and the normal one -- so the anchor has to carry
    # the line ABOVE it. The hit-count assertion is what caught that: the first
    # draft of this table matched twice and the run REFUSED the mutant rather
    # than silently deleting the fix from BOTH exits, which would have made the
    # "mutant" a rung that strides 1 everywhere and measured a different bug.
    "controls/fnptr_dispatch.rs": ("""        ex.ts[t2] = UNINIT;
        if increment_opline {
            ex.pc += 1;
        }
        ex.pc += 1;""",
                                   """        ex.ts[t2] = UNINIT;
        ex.pc += 1;"""),
}

#: Which input is which, and what each is FOR. Order is the reading order.
ADV = [
    ("adversarial-nullcall.bin",
     "the mis-strided PC lands on ZEND_OP_DATA -- handler NULL (zend_execute.c:4427)"),
    ("adversarial-opdatalive.bin",
     "the mis-strided PC lands on a word that HAS a handler -- one byte different"),
]


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def build_c(kernel, out):
    r = sh([CC, "-std=c99", "-O2", "-Wall", "-Wextra", "-DSLB_ISOLATED",
            "-I", os.path.join(ROOT, "common"),
            "-I", os.path.join(ROOT, "common-php"),
            "-I", os.path.join(PDIR, "c"),
            os.path.join(ROOT, "common", "driver.c"),
            os.path.join(PDIR, "c", kernel),
            os.path.join(PDIR, "c", "main.c"), "-o", out])
    return (out if r.returncode == 0 else None,
            (r.stdout + r.stderr)[-300:] if r.returncode else "")


def build_rs(src, out):
    r = sh([RUSTC, "--edition", "2021", "-C", "opt-level=3", "--cfg", "slb_isolated",
            "-A", "warnings", "-o", out, src])
    return (out if r.returncode == 0 else None,
            (r.stdout + r.stderr)[-400:] if r.returncode else "")


def materialise(rel, name):
    """One Rust rung with `4f68f3774c34` deleted. Returns the mutant's path.

    ⚠ The hit count is asserted here and not in a comment: `ph53`'s own
    substitution lists caught three ordering mistakes that way."""
    src = os.path.join(PDIR, rel)
    txt = open(src, encoding="utf-8").read()
    old, new = FIX_SUBS[rel]
    n = txt.count(old)
    if n != 1:
        raise AssertionError(
            f"{rel}: the 4f68f3774c34 deletion matched {n} times, want exactly 1 -- "
            f"the rung has been respelled and this mutant is not the mutant it "
            f"claims to be")
    # `#[path = "../../common/driver.rs"]` is relative to the SOURCE FILE, so a
    # mutant must sit at the same depth or the module does not resolve. The
    # scratch dir is two levels below the repo root for exactly that reason, and
    # a mutant of a `controls/` file needs one more.
    depth = os.path.join(SCRATCH, "c") if rel.startswith("controls/") else SCRATCH
    os.makedirs(depth, exist_ok=True)
    out = os.path.join(depth, name + ".rs")
    open(out, "w", encoding="utf-8").write(txt.replace(old, new))
    return out


def run(exe, inp):
    """(exit, signal, stdout, first stderr line). A SIGNAL is a behaviour and is
    recorded, never treated as a failure of this script."""
    r = sh([exe, inp])
    rc = r.returncode
    return {"exit": rc, "signal": -rc if rc < 0 else None,
            "stdout": r.stdout.strip(),
            "stderr": re.sub(r"\s+", " ", r.stderr.strip())[:140]}


# ---- the verdicts, factored so they can be ATTACKED --------------------------
# PROTOCOL_PHP.md §H: a validator lands with its must-fire negatives, and the
# negatives live INSIDE it feeding `problems`, not in gitignored scratch.

def classify(row):
    """What one (binary, input) cell DID, in the row's own vocabulary."""
    if row["signal"] is not None:
        return "SIGNAL-%d" % row["signal"]
    if row["exit"] == 101:
        return "PANIC"
    if row["exit"] != 0:
        return "EXIT-%d" % row["exit"]
    return "ANSWERED"


def pair_problems(table, ref):
    """The claims this control makes, as a function of the measured table, so
    that a run which stopped supporting them says so instead of printing the
    claim anyway.

    `table[(name, inp)]` is a classified row; `ref[inp]` is R1h's answer.

      1. on `adversarial-nullcall.bin` the C R1 must DIE OF A SIGNAL. If it
         answers, the NULL dispatch is not being reached and the row's headline
         is unsupported.
      2. on the same input every SAFE Rust mutant must PANIC -- not answer, not
         signal. That is the difference the `Option` buys and it is the only
         place in this row where safe Rust does something C cannot.
      3. on `adversarial-opdatalive.bin` the C R1 must ANSWER, and its answer
         must DIFFER from R1h's. A crash there would mean the two inputs are not
         isolating what they claim to.
      4. ⭐ on that input every safe Rust mutant must ANSWER **the same value as
         the C R1**. That is the finding: safe Rust reproduces the bug bit for
         bit, and it is a claim that can fail.
      5. no mutant may agree with R1h on either adversarial input -- a "mutant"
         that does is one the substitution did not reach.
    """
    p = []
    NC, OL = ADV[0][0], ADV[1][0]
    c1 = table.get(("c-R1", NC))
    if c1 and c1["class"] != "SIGNAL-11":
        p.append(f"1. c/kernel.c on {NC} is {c1['class']}, want SIGNAL-11: the "
                 f"NULL dispatch is this row's recorded crash category "
                 f"(CWE-476) and if it is not reached the headline is "
                 f"unsupported")
    for (nm, inp), row in sorted(table.items()):
        if inp != NC or not nm.endswith("-bug") or "unsafe" in nm:
            continue
        if row["class"] != "PANIC":
            p.append(f"2. {nm} on {NC} is {row['class']}, want PANIC: a SAFE "
                     f"Rust port carrying this bug cannot call through a `None`, "
                     f"and that is the whole of what the Option buys")
    c2 = table.get(("c-R1", OL))
    if c2:
        if c2["class"] != "ANSWERED":
            p.append(f"3. c/kernel.c on {OL} is {c2['class']}, want ANSWERED: "
                     f"the two adversarial inputs differ in ONE BYTE and this "
                     f"one is the case no detector sees")
        elif c2["stdout"] == ref.get(OL):
            p.append(f"3. c/kernel.c on {OL} answers {c2['stdout']}, which is "
                     f"R1h's own answer -- so the mis-stride changed nothing and "
                     f"the input is not adversarial")
    for (nm, inp), row in sorted(table.items()):
        if inp != OL or not nm.endswith("-bug") or "unsafe" in nm:
            continue
        if row["class"] != "ANSWERED" or (c2 and row["stdout"] != c2["stdout"]):
            p.append(f"4. {nm} on {OL} is {row['class']} {row['stdout']!r}, want "
                     f"ANSWERED {c2['stdout'] if c2 else '?'!r} -- the claim is "
                     f"that safe Rust reproduces this half BIT FOR BIT")
    for (nm, inp), row in sorted(table.items()):
        if not nm.endswith("-bug"):
            continue
        if row["class"] == "ANSWERED" and row["stdout"] == ref.get(inp):
            p.append(f"5. {nm} on {inp} agrees with R1h ({ref.get(inp)}), so the "
                     f"4f68f3774c34 deletion did not reach the path this input "
                     f"takes -- it is not a mutant")
    return p


def scope_problems(benign):
    """`check.py` stage 7h's question, measured: R1h must agree with R1 on every
    NON-adversarial input, or the 'fix' is a behaviour change."""
    p = []
    for inp, (r1, r1h) in sorted(benign.items()):
        if r1["class"] != "ANSWERED" or r1h["class"] != "ANSWERED":
            p.append(f"fix_scope: {inp} -- R1 is {r1['class']} and R1h is "
                     f"{r1h['class']}; a benign input must leave both answering")
        elif r1["stdout"] != r1h["stdout"]:
            p.append(f"fix_scope: {inp} -- R1 says {r1['stdout']} and R1h says "
                     f"{r1h['stdout']}. 4f68f3774c34 CHANGES A BENIGN ANSWER, so "
                     f"it is not a complete fix in this row's sense and "
                     f"PROTOCOL_PHP.md C's ph07 case applies")
    return p


def selftest():
    """⛔ The arms above, driven over SYNTHETIC rows. Five must FIRE and four
    must NOT, because the shipped tree's `problems` is empty and a green run is
    not evidence that any of this CAN fire (check.py's own argument for
    `_CONTROL_VERDICT_CASES`)."""
    NC, OL = ADV[0][0], ADV[1][0]

    def row(cls, out=""):
        return {"class": cls, "stdout": out, "exit": 0, "signal": None, "stderr": ""}

    ref = {NC: "R1H", OL: "R1H"}
    good = {
        ("c-R1", NC): row("SIGNAL-11"),
        ("c-R1", OL): row("ANSWERED", "GARBAGE"),
        ("safe_naive-bug", NC): row("PANIC"),
        ("safe_naive-bug", OL): row("ANSWERED", "GARBAGE"),
    }
    cases = [
        # (label, table, must_fire, which arm)
        ("N1 C does not crash on the NULL case",
         {**good, ("c-R1", NC): row("ANSWERED", "X")}, True, "1."),
        ("N2 safe Rust answers where it must panic",
         {**good, ("safe_naive-bug", NC): row("ANSWERED", "X")}, True, "2."),
        ("N3 safe Rust SIGNALs where it must panic",
         {**good, ("safe_naive-bug", NC): row("SIGNAL-11")}, True, "2."),
        ("N4 C crashes on the silent case too",
         {**good, ("c-R1", OL): row("SIGNAL-11")}, True, "3."),
        ("N5 safe Rust does NOT reproduce the silent case bit for bit",
         {**good, ("safe_naive-bug", OL): row("ANSWERED", "OTHER")}, True, "4."),
        ("N6 a mutant that agrees with R1h is not a mutant",
         {**good, ("safe_naive-bug", OL): row("ANSWERED", "R1H"),
          ("c-R1", OL): row("ANSWERED", "R1H")}, True, "5."),
        ("P1 the shipped shape",
         good, False, None),
        ("P2 a different but still-wrong C answer",
         {**good, ("c-R1", OL): row("ANSWERED", "OTHER"),
          ("safe_naive-bug", OL): row("ANSWERED", "OTHER")}, False, None),
        ("P3 an UNSAFE mutant may do anything on the NULL case",
         {**good, ("unsafe-bug", NC): row("SIGNAL-11"),
          ("unsafe-bug", OL): row("ANSWERED", "GARBAGE")}, False, None),
    ]
    bad = []
    for label, tbl, must_fire, arm in cases:
        got = pair_problems(tbl, ref)
        fired = bool(got)
        if fired != must_fire:
            bad.append(f"selftest {label}: fired={fired}, want {must_fire} "
                       f"({got})")
        elif must_fire and arm and not any(g.startswith(arm) for g in got):
            bad.append(f"selftest {label}: fired, but on arm {[g[:2] for g in got]} "
                       f"rather than {arm}")
    # the scope arm, both directions
    ok = {"small.bin": ({"class": "ANSWERED", "stdout": "7"},
                        {"class": "ANSWERED", "stdout": "7"})}
    ko = {"small.bin": ({"class": "ANSWERED", "stdout": "7"},
                        {"class": "ANSWERED", "stdout": "8"})}
    kc = {"small.bin": ({"class": "SIGNAL-11", "stdout": ""},
                        {"class": "ANSWERED", "stdout": "7"})}
    if scope_problems(ok):
        bad.append("selftest N7: fix_scope fires on two agreeing rungs")
    if not scope_problems(ko):
        bad.append("selftest N8: fix_scope does NOT fire on a changed benign answer")
    if not scope_problems(kc):
        bad.append("selftest N9: fix_scope does NOT fire on a benign input that crashes")
    return bad


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true",
                    help="drive the verdict functions over synthetic rows only")
    args = ap.parse_args()

    problems = list(selftest())
    print("0. §H -- THE VERDICT ARMS, ATTACKED OVER SYNTHETIC ROWS")
    print(f"   selftest {'PASS' if not problems else 'FAIL'}   "
          f"9 arms (6 must-FIRE, 3 must-NOT-fire)")
    for p in problems:
        print(f"     *** {p}")
    if args.selftest:
        return 1 if problems else 0

    os.makedirs(SCRATCH, exist_ok=True)
    inputs = {os.path.basename(p): p
              for p in glob.glob(os.path.join(PDIR, "inputs", "*.bin"))}
    if not inputs:
        print("stride_bug.py: no .bin -- run inputs/gen.py first", file=sys.stderr)
        return 1

    # ---- build ----------------------------------------------------------
    print("\n1. BUILD -- the shipped C pair, plus one R1 MUTANT per Rust rung")
    bins, errs = {}, []
    for tag, kern in (("c-R1", "kernel.c"), ("c-R1h", "kernel_hardened.c")):
        exe, e = build_c(kern, os.path.join(SCRATCH, tag))
        bins[tag] = exe
        if e:
            errs.append(f"{tag}: {e}")
        print(f"   {tag:22s} c/{kern:22s} {'ok' if exe else 'BUILD FAILED'}")
    for rel in FIX_SUBS:
        tag = os.path.basename(rel)[:-3] + "-bug"
        try:
            mut = materialise(rel, tag)
        except AssertionError as e:
            problems.append(str(e))
            print(f"   {tag:22s} {rel:24s} MUTANT REFUSED")
            continue
        exe, e = build_rs(mut, os.path.join(SCRATCH, tag))
        bins[tag] = exe
        if e:
            errs.append(f"{tag}: {e}")
        print(f"   {tag:22s} {rel:24s} {'ok' if exe else 'BUILD FAILED'}"
              f"   (4f68f3774c34 deleted, 1 hit asserted)")
    problems.extend(errs)

    # ---- stage 7h's question, and it is a precondition for the rest -------
    print("\n2. fix_scope -- DOES 4f68f3774c34 CHANGE A BENIGN ANSWER?\n"
          "   (check.py stage 7h's question; a fix that changes benign output is\n"
          "   PROTOCOL_PHP.md C's ph07 case and would have to be split)")
    benign = {}
    for nm, path in sorted(inputs.items()):
        if nm.startswith("adversarial"):
            continue
        r1, r1h = run(bins["c-R1"], path), run(bins["c-R1h"], path)
        for r in (r1, r1h):
            r["class"] = classify(r)
        benign[nm] = (r1, r1h)
        print(f"   {nm:28s} R1 {r1['class']:10s} {r1['stdout']:22s}"
              f"  R1h {r1h['class']:10s} {r1h['stdout']}")
    sp = scope_problems(benign)
    problems.extend(sp)
    print("   -> " + ("4f68f3774c34 changes NO benign answer: it is a COMPLETE "
                      "fix for this defect" if not sp else "SEE PROBLEMS"))

    # ---- the pair ---------------------------------------------------------
    print("\n3. ⭐⭐⭐ THE TWO ADVERSARIAL CASES, PRICED SEPARATELY")
    ref = {}
    for nm, _why in ADV:
        r = run(bins["c-R1h"], inputs[nm])
        r["class"] = classify(r)
        ref[nm] = r["stdout"]
    table = {}
    order = ["c-R1"] + [os.path.basename(r)[:-3] + "-bug" for r in FIX_SUBS]
    for nm, why in ADV:
        print(f"\n   {nm}\n   {why}\n   R1h (no bug) answers {ref[nm]}")
        for tag in order:
            if not bins.get(tag):
                continue
            row = run(bins[tag], inputs[nm])
            row["class"] = classify(row)
            table[(tag, nm)] = row
            same = ("== C R1" if (tag != "c-R1"
                                  and row["stdout"]
                                  and row["stdout"] == table.get(("c-R1", nm), {}).get("stdout"))
                    else "")
            print(f"     {tag:22s} {row['class']:10s} {row['stdout']:22s} "
                  f"{same:8s} {row['stderr'][:64]}")
    problems.extend(pair_problems(table, ref))

    # ---- the sentence ------------------------------------------------------
    NC, OL = ADV[0][0], ADV[1][0]
    print("\n4. WHAT SAFE RUST DOES, IN EACH CASE, IN ONE LINE EACH")
    print(f"   {NC:30s} C dies of a signal; a SAFE Rust port carrying the same\n"
          f"   {'':30s} bug PANICS on the `Option`. A real difference, and it is\n"
          f"   {'':30s} a FINDING, not the row's purpose.")
    print(f"   {OL:30s} C answers {table.get(('c-R1', OL), {}).get('stdout', '?')}\n"
          f"   {'':30s} and a SAFE Rust port carrying the same bug answers the\n"
          f"   {'':30s} SAME VALUE. The `Option` caught the NULL, not the wrong\n"
          f"   {'':30s} PC. Nothing in either language notices.")

    pin = _pin.pin(

        ['c/kernel.c', 'c/kernel_hardened.c', 'c/main.c', 'safe_naive.rs', 'safe_tuned.rs', 'unsafe.rs', 'inputs/gen.py', 'controls/fnptr_dispatch.rs', 'controls/stride_bug.py'],

        'python3 patterns-php/ph55-opdata-stride/controls/stride_bug.py',

        "the two C kernels and the driver (the shipped R1/R1h pair), the three Rust rungs this file MUTATES plus the fnptr control it also mutates, inputs/gen.py (the corpus every row is run over) and this script. It does NOT pin verus.rs: R5's exec code is unsafe.rs's and this file mutates the latter.")

    out = {"problems": problems,
           "benign": {k: [v[0], v[1]] for k, v in benign.items()},
           "r1h_reference": ref,
           "adversarial": {f"{t}/{i}": r for (t, i), r in table.items()}}
    out.update(pin)
    dst = os.path.join(HERE, "stride_bug.json")
    json.dump(out, open(dst, "w"), indent=2, sort_keys=True)
    print(f"\nwrote {os.path.relpath(dst, ROOT)}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
