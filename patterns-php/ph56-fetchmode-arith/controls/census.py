#!/usr/bin/env python3
"""ph56 control -- **THE SIBLING CENSUS: SIX ARMS, TWO GUARDS, ONE DEFECT.**

    python3 patterns-php/ph56-fetchmode-arith/controls/census.py
    python3 patterns-php/ph56-fetchmode-arith/controls/census.py --selftest

`zend_do_end_variable_parse`'s `switch (type)` has SIX arms
(`Zend/zend_compile.c:751-776`). TWO carry the append-dim guard. FOUR do not.
`1e708a5aeb30` added it to exactly ONE of the four.

⛔⛔ **WHICH ONE, AND WHY ONLY THAT ONE, IS NOT DEDUCIBLE FROM THE SHAPE.** This
file answers it by RUNNING all six, three ways:

  **A. THE SOURCE**, parsed out of the pinned tarball -- which arms carry the
     guard, and at which lines.
  **B. THE ROW'S OWN LADDER** -- the same six arms driven through `model.py` in
     both configurations, so that *"R1h moves this arm"* is a number.
  **C. ⭐ PRISTINE PHP 5.0.0 ITSELF**, if a CLI built from the pinned tarball is
     on this box: six one-line scripts, six exit codes. This is the half that
     settles it, because four of the six arms behave in ways no reading of
     `:751-776` predicts.

**THE ANSWER, and every cell of it is measured below:**

    arm              guard?  PHP 5.0.0 behaviour on `[]`        1e708a5aeb30?
    BP_VAR_R         YES     Fatal: Cannot use [] for reading   (already)
    BP_VAR_W         no      ✅ LEGAL -- `$a[] = 1` is the POINT  no
    BP_VAR_RW        no      ✅ works, exit 0, appends int(1)     no
    BP_VAR_IS        no      ⛔ SEGV                              ADDS IT
    BP_VAR_FUNC_ARG  no      ⚠ runs, exit 0, SILENT append       no
    BP_VAR_UNSET     YES     Fatal: Cannot use [] for unsetting  (already)

▶ **So three of the four unguarded arms are not defects: two are deliberate
features and the third is a defect upstream closed ELSEWHERE.** `BP_VAR_FUNC_ARG`
was fixed **11 1/2 months later, at RUNTIME, in a different file, by a different
author** -- `9183f91b506a` / `779e6d203e4f` (Dmitry Stogov, 2005-08-10, bug
#34064), which added the test to `zend_fetch_dim_func_arg_handler` in
`Zend/zend_execute.c` and left `zend_compile.c` untouched. The same patch
WIDENED the opcode specs (`+UNUSED` on `ZEND_FETCH_DIM_RW` and
`ZEND_FETCH_DIM_FUNC_ARG`), i.e. upstream's settled position is that the RW
append is a FEATURE.
⭐⭐ **THE COMPILE-TIME ASYMMETRY IS THEREFORE PERMANENT AND DELIBERATE, NOT AN
OVERSIGHT AWAITING REPAIR** -- the same three arms still carry the guard and the
same three still do not in `zend_compile.c` at php-8.3 and at master.

⚠⚠ **PART A IS A PARSE, WHICH MEANS IT HAS A SPELLING** (`RECAP_PHP.md` F10,
`PROTOCOL_PHP.md` trap 4). It is therefore written to REPORT the arm bodies it
found and to fail on a body it cannot split, rather than to be tuned until it
returns the expected answer. `--selftest` attacks it with five mutated switch
bodies.
"""

import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
sys.path.insert(0, PDIR)
import _pin   # noqa: E402
import model  # noqa: E402

M = model
TARBALL_SHA = "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919"

ARMS = ["BP_VAR_R", "BP_VAR_W", "BP_VAR_RW", "BP_VAR_IS", "BP_VAR_FUNC_ARG",
        "BP_VAR_UNSET"]

# The PHP each arm is reached by. ⚠ `f($a[])` appears TWICE and the two differ
# only in WHERE `function f` is written, which is the whole FUNC_ARG finding:
# `zend_do_pass_param` (zend_compile.c:1411-1427) asks for BP_VAR_R when the
# callee is already declared and BP_VAR_FUNC_ARG when it is not.
SNIPPETS = [
    ("BP_VAR_R", "$a=array(1,2,3); $x=$a[]; echo \"ran\";"),
    ("BP_VAR_W", "$a=array(1,2,3); $a[]=1; echo count($a);"),
    ("BP_VAR_RW", "$a=array(1,2,3); $a[]+=1; echo count($a);"),
    ("BP_VAR_IS", "$a=array(1,2,3); $r=isset($a[]); echo \"ran\";"),
    ("BP_VAR_FUNC_ARG",
     "$a=array(1,2,3); f($a[]); echo count($a); function f($z){}"),
    ("BP_VAR_UNSET", "$a=array(1,2,3); unset($a[]); echo \"ran\";"),
    # the control that shows FUNC_ARG's reachability is DECLARATION ORDER and
    # nothing else: the same call, with `function f` moved above it.
    ("BP_VAR_R (via a DECLARED callee)",
     "function f($z){} $a=array(1,2,3); f($a[]); echo count($a);"),
]


# ------------------------------------------------------------ A. the source --
def _tarball():
    p = os.environ.get("PHP500_TARBALL")
    if p and os.path.exists(p):
        return p
    for c in ("/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/"
              "build-5.0.0/php-5.0.0.tar.gz",
              "/home/apt/repos_common/php-in-safe-rust/.temp/san_tests/oracle/"
              "build-5.0.0/php-5.0.0.tar.gz"):
        if os.path.exists(c):
            return c
    return None


def _pristine(path):
    t = _tarball()
    if not t:
        return None
    if subprocess.run(["sha256sum", t], capture_output=True,
                      text=True).stdout.split()[0] != TARBALL_SHA:
        return None
    r = subprocess.run(["tar", "-xzOf", t, f"php-5.0.0/{path}"],
                       capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def split_arms(src):
    """Split `zend_do_end_variable_parse`'s switch into its six arm BODIES.

    ⚠ Returns `(arms, problems)`. A body it cannot find is a PROBLEM, never a
    silent absence -- the failure mode of every grep-shaped checker is to
    report *"not present"* when it means *"I did not look correctly"*."""
    m = re.search(r"void zend_do_end_variable_parse\(.*?\n\}", src, re.S)
    if not m:
        return {}, ["zend_do_end_variable_parse not found"]
    body = m.group(0)
    sw = re.search(r"switch \(type\) \{(.*?)\n\t\t\}", body, re.S)
    if not sw:
        return {}, ["the `switch (type)` body could not be delimited"]
    txt = sw.group(1)
    starts = [(mm.group(1), mm.start())
              for mm in re.finditer(r"case (BP_VAR_\w+):", txt)]
    probs = []
    found = [n for n, _ in starts]
    for a in ARMS:
        if a not in found:
            probs.append(f"arm {a} not found in the switch body")
    arms = {}
    for i, (name, pos) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(txt)
        arms[name] = txt[pos:end]
    return arms, probs


def guard_table(src):
    """Which arms carry the append-dim guard, by reading each ARM BODY --
    not by grepping the file, which would find the other arm's copy."""
    arms, probs = split_arms(src)
    out = {}
    for a in ARMS:
        b = arms.get(a, "")
        out[a] = {
            "present": bool(b),
            "guard": ("ZEND_FETCH_DIM_W" in b and "IS_UNUSED" in b
                      and "E_COMPILE_ERROR" in b),
            "delta": (re.search(r"opline->opcode ([-+]= \d+)", b).group(1)
                      if re.search(r"opline->opcode ([-+]= \d+)", b) else None),
        }
    return out, probs


# -------------------------------------------------- B. the row's own ladder --
def ladder_table():
    """Drive the six arms through `model.py` in BOTH configurations and report
    whether R1h moves each one. ⭐ This is the census as a NUMBER."""
    def rec(mode, o2t, chain=0):
        mode_i = {M.BP_R: 0, M.BP_W: 1, M.BP_RW: 2, M.BP_IS: 3,
                  M.BP_FUNC_ARG: 4, M.BP_UNSET: 5}[mode]
        o2t_i = {M.T_UNUSED: 0, M.T_CONST: 1, M.T_VAR: 2}[o2t]
        return bytes([mode_i, 1 | (0x80 if chain else 0), o2t_i, 0,
                      0, 0, 0, 0])

    out = {}
    for name, mode in zip(ARMS, (M.BP_R, M.BP_W, M.BP_RW, M.BP_IS,
                                 M.BP_FUNC_ARG, M.BP_UNSET)):
        win = rec(mode, M.T_UNUSED) + rec(M.BP_W, M.T_CONST)
        r1h = M.ph56_run(win, 0, len(win), fixed=True)
        try:
            r1 = M.ph56_run(win, 0, len(win), fixed=False)
            null = False
        except M.NullOperand:
            r1, null = None, True
        out[name] = {"r1h": r1h, "r1": r1, "null_operand": null,
                     "r1h_moves_it": null or r1 != r1h}
    # the chain variant of BP_VAR_IS -- the SILENT harm
    win = rec(M.BP_IS, M.T_CONST, chain=1) + rec(M.BP_W, M.T_CONST)
    r1h = M.ph56_run(win, 0, len(win), fixed=True)
    try:
        r1 = M.ph56_run(win, 0, len(win), fixed=False)
        null = False
    except M.NullOperand:
        r1, null = None, True
    out["BP_VAR_IS (chained)"] = {"r1h": r1h, "r1": r1, "null_operand": null,
                                  "r1h_moves_it": null or r1 != r1h}
    return out


# ------------------------------------------------ C. pristine PHP 5.0.0 CLI --
def find_cli():
    """A php-5.0.0 CLI whose `zend_compile.c` AND `zend_execute.c` are
    BYTE-IDENTICAL to the pinned tarball's.

    ⚠⚠ `patterns-php/SOURCES.md` §3 forbids CITING a build tree, and this does
    not cite one: every `file:line` in this row resolves against the tarball.
    What a build tree is used for here is an EXPERIMENT -- what the program
    DOES -- and the two source files that decide this row's behaviour are
    verified identical before it is trusted."""
    want = {}
    for f in ("Zend/zend_compile.c", "Zend/zend_execute.c"):
        s = _pristine(f)
        if s is None:
            return None, "no pinned tarball"
        import hashlib
        want[f] = hashlib.sha256(s.encode()).hexdigest()
    roots = ["/home/apt/repos_common/php-in-safe-rust"]
    for root in roots:
        if not os.path.isdir(root):
            continue
        r = subprocess.run(
            ["find", root, "-maxdepth", "7", "-type", "f", "-name", "php",
             "-path", "*sapi/cli*"], capture_output=True, text=True, timeout=180)
        for cli in r.stdout.split():
            tree = os.path.dirname(os.path.dirname(os.path.dirname(cli)))
            ok = True
            for f, h in want.items():
                p = os.path.join(tree, f)
                if not os.path.exists(p):
                    ok = False
                    break
                import hashlib
                if hashlib.sha256(open(p, "rb").read()).hexdigest() != h:
                    ok = False
                    break
            if not ok or not os.access(cli, os.X_OK):
                continue
            # ⚠⚠ AND IT MUST ACTUALLY RUN. Several of the trees on this box are
            # `-mysql-webext` builds whose CLI exits 127 with `error while
            # loading shared libraries: libmysqlclient`. A binary that cannot
            # start answers every question with the same exit code, which is
            # indistinguishable from `every arm behaves identically` -- the
            # quietest possible way to get a census wrong. SMOKE IT FIRST.
            try:
                sm = subprocess.run([cli, "-n", "-r", "echo 42;"],
                                    capture_output=True, text=True, timeout=60)
            except Exception:  # noqa: BLE001
                continue
            if sm.returncode == 0 and sm.stdout.strip() == "42":
                return cli, tree
    return None, "no pristine-sourced 5.0.0 CLI on this box that starts"


def php_table(cli):
    out = {}
    for name, code in SNIPPETS:
        try:
            r = subprocess.run([cli, "-n", "-r", code], capture_output=True,
                               text=True, timeout=60)
            txt = (r.stdout + r.stderr).strip().replace("\n", " ")[:160]
            out[name] = {"rc": r.returncode, "out": txt,
                         "segv": r.returncode in (-11, 139),
                         "fatal": "Fatal error" in txt}
        except Exception as e:  # noqa: BLE001
            out[name] = {"rc": None, "out": f"{type(e).__name__}", "segv": False,
                         "fatal": False}
    return out


# ------------------------------------------------------------- the verdict --
def verdict(ev):
    """⚠ A FUNCTION so `--selftest` can attack it. Returns `problems`."""
    p = list(ev.get("parse_problems", []))
    g = ev.get("guards")
    if g:
        want = {"BP_VAR_R": True, "BP_VAR_W": False, "BP_VAR_RW": False,
                "BP_VAR_IS": False, "BP_VAR_FUNC_ARG": False,
                "BP_VAR_UNSET": True}
        for a, w in want.items():
            if a not in g or not g[a]["present"]:
                p.append(f"arm {a} missing from the parsed switch")
            elif g[a]["guard"] != w:
                p.append(f"arm {a}: guard={g[a]['guard']}, 5.0.0 has {w}")
        deltas = {"BP_VAR_R": "-= 3", "BP_VAR_W": None, "BP_VAR_RW": "+= 3",
                  "BP_VAR_IS": "+= 6", "BP_VAR_FUNC_ARG": "+= 9",
                  "BP_VAR_UNSET": "+= 12"}
        for a, d in deltas.items():
            if a in g and g[a]["delta"] != d:
                p.append(f"arm {a}: delta {g[a]['delta']!r}, want {d!r}")
    lad = ev.get("ladder")
    if lad:
        want_move = {"BP_VAR_R": False, "BP_VAR_W": False, "BP_VAR_RW": False,
                     "BP_VAR_IS": True, "BP_VAR_FUNC_ARG": False,
                     "BP_VAR_UNSET": False, "BP_VAR_IS (chained)": True}
        for a, w in want_move.items():
            if a not in lad:
                p.append(f"ladder: {a} not driven")
            elif lad[a]["r1h_moves_it"] != w:
                p.append(f"ladder: R1h moves {a} = {lad[a]['r1h_moves_it']}, "
                         f"want {w}. The census is that 1e708a5aeb30 fixes "
                         f"BP_VAR_IS and leaves the other three standing")
        if lad.get("BP_VAR_IS", {}).get("null_operand") is not True:
            p.append("ladder: BP_VAR_IS does not dereference a NULL operand "
                     "under R1; that IS CRASH-041")
        if lad.get("BP_VAR_IS (chained)", {}).get("null_operand") is not False:
            p.append("ladder: the CHAINED BP_VAR_IS should NOT null-deref -- "
                     "its whole point is that it silently APPENDS")
    php = ev.get("php")
    if php:
        if not php.get("BP_VAR_IS", {}).get("segv"):
            p.append("pristine PHP 5.0.0 did NOT segfault on isset($a[]); "
                     "that is the corpus's recorded crash and the row's §A4 "
                     "fidelity evidence")
        for a in ("BP_VAR_R", "BP_VAR_UNSET", "BP_VAR_R (via a DECLARED callee)"):
            if not php.get(a, {}).get("fatal"):
                p.append(f"pristine PHP did not raise a fatal error on {a}; "
                         f"the guard is supposed to fire there")
        for a in ("BP_VAR_W", "BP_VAR_RW", "BP_VAR_FUNC_ARG"):
            d = php.get(a, {})
            if d.get("rc") != 0 or d.get("fatal"):
                p.append(f"pristine PHP did not run {a} cleanly ({d}); the "
                         f"census says these three arms are unguarded AND "
                         f"benign at 5.0.0")
    return p


def gather():
    src = _pristine("Zend/zend_compile.c")
    ev = {"ladder": ladder_table()}
    if src is None:
        ev["guards"] = None
        ev["parse_problems"] = ["no pinned tarball; parts A and C UNMEASURED"]
        ev["php"] = None
        return ev
    g, probs = guard_table(src)
    ev["guards"], ev["parse_problems"] = g, probs
    cli, why = find_cli()
    ev["cli"] = cli or why
    ev["php"] = php_table(cli) if cli else None
    if cli is None:
        ev.setdefault("parse_problems", []).append(
            f"part C UNMEASURED: {why}")
    return ev


# -------------------------------------------------------------- --selftest --
_SW = """
			case BP_VAR_R:
				if (opline->opcode == ZEND_FETCH_DIM_W && opline->op2.op_type == IS_UNUSED) {
					zend_error(E_COMPILE_ERROR, "Cannot use [] for reading");
				}
				opline->opcode -= 3;
				break;
			case BP_VAR_W:
				break;
			case BP_VAR_RW:
				opline->opcode += 3;
				break;
			case BP_VAR_IS:
				opline->opcode += 6; /* 3+3 */
				break;
			case BP_VAR_FUNC_ARG:
				opline->opcode += 9; /* 3+3+3 */
				opline->extended_value = arg_offset;
				break;
			case BP_VAR_UNSET:
				if (opline->opcode == ZEND_FETCH_DIM_W && opline->op2.op_type == IS_UNUSED) {
					zend_error(E_COMPILE_ERROR, "Cannot use [] for unsetting");
				}
				opline->opcode += 12; /* 3+3+3+3 */
				break;
"""


def _fake(sw):
    return ("void zend_do_end_variable_parse(int type, int arg_offset TSRMLS_DC)\n"
            "{\n\t\tswitch (type) {" + sw + "\n\t\t}\n}")


def _selftest():
    """⚠⚠ §H: the PARSE is the part with a spelling, so it is what gets
    attacked -- FIVE must-FIRE mutations and TWO must-NOT-fire."""
    bad = 0
    base, probs = guard_table(_fake(_SW))
    ok = (not probs and base["BP_VAR_IS"]["guard"] is False
          and base["BP_VAR_R"]["guard"] is True
          and base["BP_VAR_IS"]["delta"] == "+= 6")
    print(f"  must-NOT-fire {'OK ' if ok else 'FAIL'}  the real 5.0.0 switch parses")
    bad += 0 if ok else 1

    fixed = _SW.replace(
        "			case BP_VAR_IS:\n				opline->opcode += 6;",
        "			case BP_VAR_IS:\n"
        "				if (opline->opcode == ZEND_FETCH_DIM_W && opline->op2.op_type == IS_UNUSED) {\n"
        "					zend_error(E_COMPILE_ERROR, \"Cannot use [] for reading\");\n"
        "				}\n				opline->opcode += 6;")
    g2, _ = guard_table(_fake(fixed))
    ok = g2["BP_VAR_IS"]["guard"] is True
    print(f"  must-NOT-fire {'OK ' if ok else 'FAIL'}  the POST-FIX switch reads "
          f"BP_VAR_IS as guarded")
    bad += 0 if ok else 1

    mutations = [
        ("a transposed delta on BP_VAR_IS",
         _SW.replace("opline->opcode += 6", "opline->opcode += 9", 1),
         lambda g, p: g["BP_VAR_IS"]["delta"] == "+= 6"),
        ("BP_VAR_R's guard deleted",
         _SW.replace('zend_error(E_COMPILE_ERROR, "Cannot use [] for reading");',
                     "", 1),
         lambda g, p: g["BP_VAR_R"]["guard"] is True),
        ("an arm removed entirely",
         _SW.replace("			case BP_VAR_FUNC_ARG:\n"
                     "				opline->opcode += 9; /* 3+3+3 */\n"
                     "				opline->extended_value = arg_offset;\n"
                     "				break;\n", ""),
         # ⚠ the checker NOTICES this one by REPORTING A PARSE PROBLEM, so
         # "still says 5.0.0" means BOTH no problems AND the arm present.
         lambda g, p: (not p) and g["BP_VAR_FUNC_ARG"]["present"]),
        ("the guard moved OUT of any arm, to the top of the switch",
         "\n\t\t\tif (opline->opcode == ZEND_FETCH_DIM_W && opline->op2.op_type "
         "== IS_UNUSED) { zend_error(E_COMPILE_ERROR, \"x\"); }\n"
         + _SW.replace(
             'zend_error(E_COMPILE_ERROR, "Cannot use [] for reading");', "", 1),
         lambda g, p: g["BP_VAR_R"]["guard"] is True),
        ("BP_VAR_W given a delta it does not have",
         _SW.replace("			case BP_VAR_W:\n				break;",
                     "			case BP_VAR_W:\n				opline->opcode += 1;\n				break;"),
         lambda g, p: g["BP_VAR_W"]["delta"] is None),
    ]
    for name, sw, still_says_5_0_0 in mutations:
        g, p = guard_table(_fake(sw))
        try:
            unchanged = still_says_5_0_0(g, p)
        except KeyError:
            unchanged = False
        fired = not unchanged
        print(f"  must-FIRE     {'OK ' if fired else 'MISS'}  {name}")
        bad += 0 if fired else 1

    print(f"\n--selftest: {bad} problem(s)")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(_selftest())

    ev = gather()
    probs = verdict(ev)
    out = {"control": "census", "row": "ph56-fetchmode-arith",
           "question": "six arms, two guards -- why did 1e708a5aeb30 fix only "
                       "BP_VAR_IS?",
           "evidence": ev, "problems": probs}
    out.update(_pin.pin(["model.py", "c/kernel.c", "c/kernel_hardened.c"],
                        "python3 controls/census.py",
                        "re-parses the pinned tarball's switch, re-drives the "
                        "six arms through model.py, and re-runs the six PHP "
                        "snippets on a pristine-sourced 5.0.0 CLI"))
    with open(os.path.join(HERE, "census.json"), "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")

    if ev.get("guards"):
        print("A. the pinned tarball's switch")
        for a_ in ARMS:
            d = ev["guards"][a_]
            print(f"   {a_:<18} guard={str(d['guard']):<5} "
                  f"delta={str(d['delta']):<6}")
    print("\nB. the row's own ladder -- does R1h move this arm?")
    for k, v in ev["ladder"].items():
        print(f"   {k:<22} moves={str(v['r1h_moves_it']):<5} "
              f"null_operand={v['null_operand']}")
    if ev.get("php"):
        print(f"\nC. pristine PHP 5.0.0 CLI  ({ev['cli']})")
        for name, _ in SNIPPETS:
            d = ev["php"][name]
            print(f"   {name:<34} rc={str(d['rc']):<5} {d['out'][:70]}")
    else:
        print(f"\nC. UNMEASURED -- {ev.get('cli')}")
    print(f"\nproblems: {probs if probs else 'none'}")
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()
