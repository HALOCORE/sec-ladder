#!/usr/bin/env python3
"""ph55 control -- **THE IN-CONTRACT RESPELLING SEARCH, AND §2.8 PREDICTION 1
SCORED AGAINST IT RATHER THAN THE OTHER WAY ROUND.**

    python3 patterns-php/ph55-opdata-stride/controls/spellings.py --audit-only
    python3 patterns-php/ph55-opdata-stride/controls/spellings.py
    python3 patterns-php/ph55-opdata-stride/controls/spellings.py --verus

⚠⚠⚠ **RUN IT WITH `--verus` OR ITS R4 COLUMN MEANS NOTHING.** An R4 respelling
is a RUNG CANDIDATE only if a Verus twin VERIFIES: an R4 is a program whose
obligations a prover can discharge, and without that an R4 candidate is a
control and not a rung. Without the flag this file refuses to certify and says so
in `problems`.

⚠ **THE BAR ON THIS ROW IS *THE TWIN VERIFIES* AND NOT BYTE-IDENTITY.**
`../spec.md` pins `identity: unsafe vs verus = differ` at BOTH levels and
`results-php/gate/ph55-opdata-stride.json` MEASURES `differ` at both (876/872 at
O3). `identity_premise()` reads the pin AND the record, so if this row were ever
re-pinned to `exact` the rule tightens with it instead of silently staying loose.

WHAT IS SEARCHED, AND IT IS A DECOMPOSITION RATHER THAN A HUNT
--------------------------------------------------------------
**R3 side** -- `safe_tuned.rs`'s three levers, reverted ONE AT A TIME. That
prices each lever separately instead of reporting `R2 -> R3` as one number, and
it is the only search that answers *which of the three did the work*.

**R4 side** -- the trusted surface, reduced ONE CLASS AT A TIME, by promoting a
trusted item's own VERIFIED TWIN to be the item. ⭐ `r4_safe_hunwrap` is the
interesting one: it makes **only** the handler `unwrap` checked and leaves every
index unchecked, so it prices *this row's own `unsafe`* and nothing else.
`r4_safe_all` is the degenerate endpoint -- zero unchecked operations, i.e. R3
with a proof attached -- and is labelled NOT A RUNG CANDIDATE.

⚠⚠ **NOTHING HERE IS A HAND-COPIED FORK.** Every variant is the shipped `.rs`
with exact-string substitutions applied and **the hit count asserted**, so a
variant cannot drift away from the rung it claims to be a respelling of.

⛔ **AND IT STILL DOES NOT RE-SHIP EITHER RUNG.** `.memory/02-bench-rules.md`
holds the shipped rungs fixed by fiat -- chosen by IDIOM, before measurement --
and that fiat is what makes `R3ship - R4ship` a BOUND. Two labelled quantities
ship, never three, and **NO PAIR INTERVAL**: `min(R3 found) - min(R4 found)`
differences two upper bounds and bounds nothing in either direction.

⚠ **R4 SEARCHED IS NOT R4 EXHAUSTED.** Seven variants are what was tried.

§H (`PROTOCOL_PHP.md`): the verdict functions are functions so they can be
attacked, and `--audit-only` runs a selftest over synthetic rows -- seven
must-FIRE and four must-NOT-fire -- because the shipped tree's `problems` is
empty and a green run is no evidence that any arm CAN fire.
"""

import argparse
import glob
import importlib.util
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

#: ⚠ TWO LEVELS BELOW THE REPO ROOT: `#[path = "../../common/driver.rs"]`
#: resolves relative to the SOURCE FILE, so a variant at another depth does not
#: compile and the failure would be this file's.
SCRATCH = os.path.join(ROOT, ".temp", "php55sp")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
VERUS_RUN = os.path.join(ROOT, "verus_run.py")
_TOTAL = re.compile(r"^([\d,]+)\s.*PROGRAM TOTALS")

INPUTS = ["small.bin", "large.bin"]
#: Below this, a difference is a TIE and not a win.
TIE_PCT = 0.5

# --------------------------------------------------------------- variants ---
# `(name, side, why, [(old, new, hits), ...])`, applied to the side's base file.
# `verus_subs` is applied to `verus.rs` in the same run so an R4 candidate can be
# put through the prover.

R3_BASE = "safe_tuned.rs"
R4_BASE = "unsafe.rs"

_L1_OLD = """        // ⭐ LEVER 1: ONE load, ONE bounds check, for the whole dispatch.
        let o: Op = ops[pc];
"""

R3_VARIANTS = [
    ("r3_nobind", "LEVER 1 REVERTED: re-index `ops[pc]` per field, as R2 does. "
     "This is the lever about the row -- a dispatch loop reads its current "
     "instruction four or five times.",
     # ⚠ `o.opcode` ALSO occurs in `two_word` and in `emit_from`, where the
     # local is a DIFFERENT `o` indexed by `p` and not by `pc`. The first draft
     # of this variant replaced the bare token and produced eight `cannot find
     # value pc in this scope` errors -- so the anchors below are the DISPATCH
     # LOOP's spellings and nothing else, and the hit counts are asserted.
     [(_L1_OLD, "", 1),
      ("acc.wrapping_mul(31).wrapping_add(o.opcode as u64)",
       "acc.wrapping_mul(31).wrapping_add(ops[pc].opcode as u64)", 1),
      ("o.handler.unwrap()", "ops[pc].handler.unwrap()", 1),
      ("o.op1", "ops[pc].op1", None), ("o.op2", "ops[pc].op2", None),
      ("if o.ext == X_DIM {", "if ops[pc].ext == X_DIM {", 1),
      ("o.result", "ops[pc].result", None)]),
    ("r3_noodbind", "LEVER 2 REVERTED: re-index `ops[pc + 1]` per field in the "
     "two two-word arms.",
     [("            let od: Op = ops[pc + 1]; // LEVER 2\n", "", 1),
      ("                let od: Op = ops[pc + 1]; // LEVER 2.  op_data = opline + 1, :1742\n", "", 1),
      ("od.op1", "ops[pc + 1].op1", None), ("od.op2", "ops[pc + 1].op2", None)]),
    ("r3_noslice", "LEVER 3 REVERTED: eight independent index expressions in the "
     "decoder instead of one slice bind.",
     [("""        let b: &[u8] = &win[8 * i..8 * i + 8]; // LEVER 3
        ops[i] = Op {
            opcode: b[0] % N_OPCODES,
            ext: b[1],
            op1: (b[2] as u16) | ((b[3] as u16) << 8),
            op2: (b[4] as u16) | ((b[5] as u16) << 8),
            result: (b[6] as u16) | ((b[7] as u16) << 8),
            handler: None,
        };""",
       """        ops[i] = Op {
            opcode: win[8 * i] % N_OPCODES,
            ext: win[8 * i + 1],
            op1: (win[8 * i + 2] as u16) | ((win[8 * i + 3] as u16) << 8),
            op2: (win[8 * i + 4] as u16) | ((win[8 * i + 5] as u16) << 8),
            result: (win[8 * i + 6] as u16) | ((win[8 * i + 7] as u16) << 8),
            handler: None,
        };""", 1)]),
]

#: `(exec old, exec new, verus old, verus new)` per accessor class. ⭐ The
#: replacement is the accessor's OWN VERIFIED TWIN, promoted to be the item --
#: which is why every one of these is admissible by construction and why the
#: Verus run is a check rather than a hope.
_SAFE = {
    "hunwrap": [("""fn hunwrap(t: Option<u8>) -> u8 {
    unsafe { t.unwrap_unchecked() }
}""", """fn hunwrap(t: Option<u8>) -> u8 {
    t.unwrap()
}""", """#[verifier::external_body]
fn hunwrap(t: Option<u8>) -> (r: u8)""", """fn hunwrap(t: Option<u8>) -> (r: u8)"""),
                ("", "", """    unsafe { t.unwrap_unchecked() }
}

#[cfg(slb_twin)]
fn slb_twin_hunwrap""", """    t.unwrap()
}

#[cfg(slb_twin)]
fn slb_twin_hunwrap""")],
    "ops": [("""fn oget(a: &[Op; MAX_OPS], i: usize) -> Op {
    unsafe { *a.get_unchecked(i) }
}""", """fn oget(a: &[Op; MAX_OPS], i: usize) -> Op {
    a[i]
}""", """#[verifier::external_body]
fn oget(""", """fn oget("""),
            ("""fn oset(a: &mut [Op; MAX_OPS], i: usize, x: Op) {
    unsafe { *a.get_unchecked_mut(i) = x };
}""", """fn oset(a: &mut [Op; MAX_OPS], i: usize, x: Op) {
    a[i] = x;
}""", """#[verifier::external_body]
fn oset(""", """fn oset("""),
            ("", "", """    unsafe { *a.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_oget""", """    a[i]
}

#[cfg(slb_twin)]
fn slb_twin_oget"""),
            ("", "", """    unsafe { *a.get_unchecked_mut(i) = x };
}

#[cfg(slb_twin)]
fn slb_twin_oset""", """    a[i] = x;
}

#[cfg(slb_twin)]
fn slb_twin_oset""")],
    "slots": [("""fn kget(a: &[u8; NSLOT], i: usize) -> u8 {
    unsafe { *a.get_unchecked(i) }
}""", """fn kget(a: &[u8; NSLOT], i: usize) -> u8 {
    a[i]
}""", """#[verifier::external_body]
fn kget(""", """fn kget("""),
              ("""fn kset(a: &mut [u8; NSLOT], i: usize, x: u8) {
    unsafe { *a.get_unchecked_mut(i) = x };
}""", """fn kset(a: &mut [u8; NSLOT], i: usize, x: u8) {
    a[i] = x;
}""", """#[verifier::external_body]
fn kset(""", """fn kset("""),
              ("""fn vget(a: &[u64; NSLOT], i: usize) -> u64 {
    unsafe { *a.get_unchecked(i) }
}""", """fn vget(a: &[u64; NSLOT], i: usize) -> u64 {
    a[i]
}""", """#[verifier::external_body]
fn vget(""", """fn vget("""),
              ("""fn vset(a: &mut [u64; NSLOT], i: usize, x: u64) {
    unsafe { *a.get_unchecked_mut(i) = x };
}""", """fn vset(a: &mut [u64; NSLOT], i: usize, x: u64) {
    a[i] = x;
}""", """#[verifier::external_body]
fn vset(""", """fn vset("""),
              ("", "", """    unsafe { *a.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_kget""", """    a[i]
}

#[cfg(slb_twin)]
fn slb_twin_kget"""),
              ("", "", """    unsafe { *a.get_unchecked_mut(i) = x };
}

#[cfg(slb_twin)]
fn slb_twin_kset""", """    a[i] = x;
}

#[cfg(slb_twin)]
fn slb_twin_kset"""),
              ("", "", """    unsafe { *a.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_vget""", """    a[i]
}

#[cfg(slb_twin)]
fn slb_twin_vget"""),
              ("", "", """    unsafe { *a.get_unchecked_mut(i) = x };
}

#[cfg(slb_twin)]
fn slb_twin_vset""", """    a[i] = x;
}

#[cfg(slb_twin)]
fn slb_twin_vset""")],
    "win": [("""fn bget(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}""", """fn bget(v: &[u8], i: usize) -> u8 {
    v[i]
}""", """#[verifier::external_body]
fn bget(""", """fn bget("""),
            ("", "", """    unsafe { *v.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_bget""", """    v[i]
}

#[cfg(slb_twin)]
fn slb_twin_bget""")],
}

R4_VARIANTS = [
    ("r4_safe_hunwrap", ["hunwrap"],
     "⭐ ONLY the handler `unwrap` is checked; every index stays unchecked. This "
     "prices THE ROW'S OWN `unsafe` and nothing else.", True),
    ("r4_safe_ops", ["ops"],
     "the op_array accessors are checked: trusted surface 8 -> 6.", True),
    ("r4_safe_slots", ["slots"],
     "the zval-store accessors are checked: trusted surface 8 -> 4.", True),
    ("r4_safe_all", ["hunwrap", "ops", "slots", "win"],
     "the DEGENERATE ENDPOINT -- every unchecked operation removed, i.e. R3 with "
     "a proof attached. ⛔ NOT A RUNG CANDIDATE: an R4 with no `unsafe` is an R3.",
     False),
]

_M = None


def load_measure():
    global _M
    if _M is None:
        spec = importlib.util.spec_from_file_location(
            "slb_measure", os.path.join(ROOT, "harness", "measure.py"))
        _M = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_M)
    return _M


def load_check():
    """`harness/check.py`, IMPORTED, for `spelling_matches` -- the ONE definition
    of what it means for a rung to carry a declared spelling."""
    spec = importlib.util.spec_from_file_location(
        "slb_check", os.path.join(ROOT, "harness", "check.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def contract():
    txt = open(os.path.join(PDIR, "spec.md"), encoding="utf-8").read()
    return json.loads(re.search(r"```slb-contract\s*\n(.*?)```", txt, re.S).group(1))


def identity_premise():
    """The `identity` pin AND the measured record -- both, because F82's N6 found
    a PAT row carrying `identity: unsafe == verus, O3 exact` as shared-block
    BOILERPLATE while its real pin was `norel`."""
    pinned = {}
    for e in contract().get("identity") or []:
        if e.get("a") == "unsafe" and e.get("b") == "verus":
            pinned = {"O0": e.get("O0"), "O3": e.get("O3")}
    measured = {}
    rec = os.path.join(ROOT, "results-php", "gate", "ph55-opdata-stride.json")
    if os.path.exists(rec):
        for r in json.load(open(rec)).get("identity") or []:
            if r.get("pair") == "unsafe vs verus":
                measured[r["opt"]] = r["level"]
    return pinned, measured


def admissibility(pinned, measured):
    if pinned.get("O3") == "exact" or measured.get("O3") == "exact":
        return True, ("`identity` is `exact` at O3, so an R4 candidate must have "
                      "a BYTE-IDENTICAL verified twin")
    return False, ("`identity` is `differ` at O3 (pinned and measured), so the "
                   "bar for an R4 candidate is THAT THE TWIN VERIFIES, not "
                   "byte-identity -- ph53's ruling, and this row measures the "
                   "same thing")


def materialise(name, base, subs, out_dir=None):
    src = os.path.join(PDIR, base)
    txt = open(src, encoding="utf-8").read()
    for old, new, want in subs:
        if not old:
            continue
        n = txt.count(old)
        if want is not None and n != want:
            raise AssertionError(
                f"{name}: substitution {old[:44]!r} matched {n}x, want {want} -- "
                f"{base} has been respelled and this variant is not the "
                f"respelling it claims to be")
        if want is None and n == 0:
            raise AssertionError(
                f"{name}: substitution {old[:44]!r} matched 0x in {base}")
        txt = txt.replace(old, new)
    d = out_dir or SCRATCH
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{name}.rs")
    open(p, "w", encoding="utf-8").write(txt)
    return p


def materialise_r4(name, classes):
    """The exec variant AND its Verus analogue, from the SAME class list."""
    ex = [(a, b, None) for cls in classes for (a, b, _c, _d) in _SAFE[cls] if a]
    vr = [(c, d, None) for cls in classes for (_a, _b, c, d) in _SAFE[cls] if c]
    return (materialise(name, R4_BASE, ex),
            materialise(name + "_verus", "verus.rs", vr))


def unsafe_tokens(src):
    txt = re.sub(r"//[^\n]*", "", src)
    return len(re.findall(r"\bunsafe\b", txt))


def external_bodies(src):
    return len(re.findall(r"#\[verifier::external_body\]", src))


def audit(chk, decl, src, lang="rust"):
    """Every backticked spelling in `../spec.md`'s `idiom`, against one variant,
    with `harness/check.py`'s OWN semantics.

    A `forbidden` hit DISQUALIFIES -- `check.py` has hard-failed on one since
    TASK_068 and its scope is universal by the key's own meaning. A `required`
    miss is REPORTED and does not, because which rungs a `required` entry scopes
    to lives in the entry's ENGLISH and no gate stage reproduces it."""
    forb, miss = [], []
    for key, sink in (("required", miss), ("forbidden", forb)):
        for i, e in enumerate(decl.get(key) or []):
            txt = e.get(lang) if isinstance(e, dict) else e
            if not isinstance(txt, str):
                continue
            for tok in re.findall(r"`([^`]+)`", txt):
                hit = chk.spelling_matches(tok, src, lang=lang)
                if key == "forbidden" and hit:
                    sink.append(f"forbidden[{i}] `{tok}` PRESENT")
                elif key == "required" and not hit:
                    sink.append(f"required[{i}] `{tok}`")
    return forb, miss


def build(src, out):
    r = subprocess.run([RUSTC, "--edition", "2021", "-C", "opt-level=3",
                        "--cfg", "slb_isolated", "-A", "warnings", "-o", out, src],
                       capture_output=True, text=True)
    return (out if r.returncode == 0 else None,
            (r.stdout + r.stderr)[-400:] if r.returncode else "")


def checksums(exe):
    out = {}
    for p in sorted(glob.glob(os.path.join(PDIR, "inputs", "*.bin"))):
        r = subprocess.run([exe, p], capture_output=True, text=True)
        out[os.path.basename(p)] = (r.returncode, r.stdout.strip())
    return out


def families(exe, inp, tag):
    M = load_measure()
    o = os.path.join(SCRATCH, f"cg.{tag}")
    r = subprocess.run([VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + o,
                        exe, os.path.join(PDIR, "inputs", inp)],
                       capture_output=True, text=True, timeout=7200)
    if r.returncode != 0 or not os.path.exists(o):
        return None, None, f"callgrind failed on {tag} (rc {r.returncode})"
    a = subprocess.run([M.CG_ANNOTATE, "--threshold=100", o],
                       capture_output=True, text=True)
    txt = a.stdout + a.stderr
    os.unlink(o)
    k, _ = M._sum_rows(txt, "kernel")
    wp = None
    for ln in txt.splitlines():
        m = _TOTAL.match(ln.strip())
        if m:
            wp = int(m.group(1).replace(",", ""))
            break
    if k is None or wp is None:
        return None, None, f"{tag}: annotate gave kernel={k} totals={wp}"
    sys.path.insert(0, os.path.join(ROOT, "common"))
    import slb
    n = slb.read(os.path.join(PDIR, "inputs", inp)).n_iters
    return k / n, wp / n, None


def run_verus(path, extra=()):
    r = subprocess.run([sys.executable, VERUS_RUN, path, *extra],
                       capture_output=True, text=True, timeout=3600)
    txt = r.stdout + r.stderr
    m = re.search(r"verification results:: (\d+) verified, (\d+) errors", txt)
    return {"rc": r.returncode,
            "verified": int(m.group(1)) if m else None,
            "errors": int(m.group(2)) if m else None,
            "unsupported": "is not supported" in txt or
                           "does not yet support" in txt,
            "text": txt[-800:]}


#: The `problems` entry a run WITHOUT `--verus` carries. A module constant so a
#: negative can hand it to the verdict function and prove the refusal is real.
NO_VERUS_PROBLEM = (
    "R4 ADMISSIBILITY WAS NOT CHECKED (no --verus), so every R4 variant's "
    "`in_contract` above is unverified: an R4 is a program whose obligations a "
    "prover can discharge, and without a twin that VERIFIES an R4 candidate is "
    "a control and not a rung. Regenerate with `--verus`.")


# ---- the verdicts, factored so they can be ATTACKED -------------------------

def spelling_problems(rows, verus_ran):
    """1. ⛔ a FORBIDDEN hit disqualifies a variant, decidably and with no
          English involved;
       2. a variant that did not BUILD cannot be quoted;
       3. ⛔ a variant whose checksums differ from the shipped rung's is not a
          respelling -- it is a different program;
       4. an R4 RUNG CANDIDATE with no verifying twin may not be called one;
       5. ⚠ without `--verus` the R4 column is uncertified and the run says so.
    """
    p = []
    if not verus_ran and any(r.get("rung_candidate") for r in rows.values()):
        p.append("5. " + NO_VERUS_PROBLEM)
    for key, r in sorted(rows.items()):
        if r.get("forbidden_hits"):
            p.append(f"1. {key}: FORBIDDEN spelling present -- "
                     f"{'; '.join(r['forbidden_hits'])}")
        if r.get("built") is False:
            p.append(f"2. {key}: did not build -- {str(r.get('build_error'))[:160]}")
            continue
        if r.get("checksum_mismatch"):
            p.append(f"3. {key}: checksums differ from the shipped rung on "
                     f"{r['checksum_mismatch']} -- it is a different program, "
                     f"not a respelling")
        if verus_ran and r.get("rung_candidate") and r.get("twin_errors") not in (0,):
            p.append(f"4. {key}: called an R4 rung candidate but its Verus "
                     f"analogue reports errors={r.get('twin_errors')} "
                     f"unsupported={r.get('twin_unsupported')} -- an R4 whose "
                     f"obligations no prover discharges is a control, not a rung")
    return p


def selftest():
    ok = {"forbidden_hits": [], "built": True, "checksum_mismatch": None,
          "rung_candidate": False, "twin_errors": 0}
    r4 = dict(ok, rung_candidate=True)
    bad = []
    cases = [
        ("P1 the shipped shape", {"a": dict(ok), "b": dict(r4)}, True, False, None),
        ("N1 a forbidden spelling appears",
         {"a": dict(ok, forbidden_hits=["forbidden[1] `% MAX_OPS` PRESENT"])},
         True, True, "1."),
        ("N2 a variant does not build",
         {"a": dict(ok, built=False, build_error="E0502")}, True, True, "2."),
        ("N3 a variant answers differently",
         {"a": dict(ok, checksum_mismatch="small.bin")}, True, True, "3."),
        ("N4 an R4 candidate whose twin errors",
         {"a": dict(r4, twin_errors=2)}, True, True, "4."),
        ("N5 an R4 candidate Verus REFUSES as unsupported",
         {"a": dict(r4, twin_errors=None, twin_unsupported=True)}, True, True, "4."),
        ("N6 no --verus at all, with an R4 candidate present",
         {"a": dict(r4)}, False, True, "5."),
        ("N7 a build failure hides a checksum mismatch (arm 2 wins, arm 3 must "
         "not also fire on an unbuilt variant)",
         {"a": dict(ok, built=False, build_error="x", checksum_mismatch="y")},
         True, True, "2."),
        ("P2 no --verus and NO R4 candidates", {"a": dict(ok)}, False, False, None),
        ("P3 an R3 variant with a required miss is fine",
         {"a": dict(ok, required_absent=["required[2] `x`"])}, True, False, None),
        ("P4 an R4 candidate whose twin verifies", {"a": dict(r4)}, True, False, None),
    ]
    for label, rows, vr, must_fire, arm in cases:
        got = spelling_problems(rows, vr)
        if bool(got) != must_fire:
            bad.append(f"selftest {label}: fired={bool(got)}, want {must_fire} ({got})")
        elif must_fire and arm and not any(g.startswith(arm) for g in got):
            bad.append(f"selftest {label}: fired on {[g[:2] for g in got]}, want {arm}")
    # arm 2 must SHORT-CIRCUIT arm 3: an unbuilt variant has no checksums
    got = spelling_problems({"a": dict(ok, built=False, build_error="x",
                                       checksum_mismatch="y")}, True)
    if any(g.startswith("3.") for g in got):
        bad.append("selftest N7b: arm 3 fires on a variant that did not build, "
                   "so it is reporting a checksum that does not exist")
    return bad


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit-only", action="store_true",
                    help="the spelling audit; no build, no callgrind")
    ap.add_argument("--verus", action="store_true",
                    help="put every R4 variant's Verus analogue through the prover")
    args = ap.parse_args()

    problems = list(selftest())
    print("0. §H -- THE VERDICT ARMS, ATTACKED OVER SYNTHETIC ROWS")
    print(f"   selftest {'PASS' if not problems else 'FAIL'}   "
          f"12 arms (7 must-FIRE, 4 must-NOT-fire, 1 short-circuit)")
    for p in problems:
        print(f"     *** {p}")

    pinned, measured = identity_premise()
    need_ident, why = admissibility(pinned, measured)
    print("\n0a. THE `identity` PREMISE, FROM BOTH THE PIN AND THE RECORD")
    print(f"    ../spec.md               pinned   {pinned}")
    print(f"    results-php/gate/...json measured {measured}")
    print(f"    -> {why}")
    if pinned.get("O3") != measured.get("O3"):
        problems.append(
            f"the `identity` pin (O3 {pinned.get('O3')!r}) and the gate record "
            f"(O3 {measured.get('O3')!r}) DISAGREE, so this file cannot tell "
            f"which admissibility rule applies")

    chk = load_check()
    decl = contract()["idiom"]
    rows = {}

    print("\n0b. THE SPELLING AUDIT -- every backticked idiom entry, through "
          "harness/check.py::spelling_matches")
    variants = ([(n, "R3", w, s, R3_BASE, False) for n, w, s in R3_VARIANTS]
                + [(n, "R4", w, c, R4_BASE, cand) for n, c, w, cand in R4_VARIANTS])
    shipped = {"R3": R3_BASE, "R4": R4_BASE}
    for base_label, base in shipped.items():
        src = open(os.path.join(PDIR, base), encoding="utf-8").read()
        forb, miss = audit(chk, decl, src)
        rows[f"{base_label}/SHIPPED"] = {
            "side": base_label, "name": "SHIPPED", "why": base,
            "rs": os.path.join(PDIR, base), "verus_rs": None,
            "rung_candidate": False, "forbidden_hits": forb,
            "required_absent": miss, "in_contract": not forb,
            "unsafe_tokens": unsafe_tokens(src)}
    for name, side, why, subs, base, cand in variants:
        try:
            if side == "R4":
                rs, vp = materialise_r4(name, subs)
            else:
                rs, vp = materialise(name, base, subs), None
        except AssertionError as e:
            problems.append(str(e))
            print(f"   {side} {name:18s} VARIANT REFUSED -- {e}")
            continue
        src = open(rs, encoding="utf-8").read()
        forb, miss = audit(chk, decl, src)
        rows[f"{side}/{name}"] = {
            "side": side, "name": name, "why": why, "rs": rs, "verus_rs": vp,
            "rung_candidate": cand, "forbidden_hits": forb,
            "required_absent": miss, "in_contract": not forb,
            "unsafe_tokens": unsafe_tokens(src)}
    for key, r in sorted(rows.items()):
        print(f"   {key:26s} "
              + ("IN CONTRACT" if r["in_contract"] else "OUT: " + "; ".join(r["forbidden_hits"]))
              + f"   unsafe={r['unsafe_tokens']:2d}"
              + "   required absent: "
              + (", ".join(m.split("`")[1] for m in r["required_absent"]) or "none"))

    if args.audit_only:
        problems.extend(spelling_problems(rows, args.verus))
        for p in problems:
            print(f"  *** {p}", file=sys.stderr)
        return 1 if problems else 0

    os.makedirs(SCRATCH, exist_ok=True)
    print("\n1. BUILD + CHECKSUM -- a variant that answers differently is not a "
          "respelling")
    ref = {}
    for key, r in sorted(rows.items()):
        exe, err = build(r["rs"], os.path.join(SCRATCH, key.replace("/", "_")))
        r["built"] = exe is not None
        r["build_error"] = err
        r["exe"] = exe
        if not exe:
            print(f"   {key:26s} BUILD FAILED")
            continue
        cs = checksums(exe)
        if r["name"] == "SHIPPED":
            ref[r["side"]] = cs
        bad = [k for k, v in cs.items() if ref.get(r["side"], cs).get(k) != v]
        r["checksum_mismatch"] = bad[0] if bad else None
        print(f"   {key:26s} ok   checksums "
              + ("identical to the shipped rung" if not bad else f"DIFFER on {bad}"))

    print("\n2. A1 AND W1, O3/isolated -- ⚠ this file's OWN build "
          "(`rustc -C opt-level=3`),\n   NOT harness/build.py's, so LEVELS are "
          "not comparable with ../NOTES.md §8;\n   only the columns here are "
          "comparable with each other.")
    for inp in INPUTS:
        print(f"   -- {inp}")
        for key, r in sorted(rows.items()):
            if not r.get("exe"):
                continue
            a, w, e = families(r["exe"], inp, key.replace("/", "_") + inp)
            if e:
                problems.append(e)
                continue
            r.setdefault("A1", {})[inp] = a
            r.setdefault("W1", {})[inp] = w
        base = {s: rows[f"{s}/SHIPPED"] for s in ("R3", "R4")}
        for key, r in sorted(rows.items()):
            if "A1" not in r or inp not in r["A1"]:
                continue
            b = base[r["side"]]
            da = (r["A1"][inp] - b["A1"][inp]) / b["A1"][inp] * 100
            dw = (r["W1"][inp] - b["W1"][inp]) / b["W1"][inp] * 100
            tie = "  (TIE)" if abs(da) < TIE_PCT else ""
            print(f"      {key:26s} A1 {r['A1'][inp]:9.3f} {da:+7.2f} %   "
                  f"W1 {r['W1'][inp]:9.3f} {dw:+7.2f} %{tie}")

    if args.verus:
        print("\n3. ⚠ R4 ADMISSIBILITY -- the Verus analogue of every R4 variant")
        for key, r in sorted(rows.items()):
            if r["side"] != "R4" or not r.get("verus_rs"):
                continue
            v = run_verus(r["verus_rs"])
            r["twin_errors"] = v["errors"]
            r["twin_verified"] = v["verified"]
            r["twin_unsupported"] = v["unsupported"]
            print(f"   {key:26s} {str(v['verified']):>4s} verified / "
                  f"{str(v['errors']):>3s} errors"
                  + ("   ⛔ is-not-supported" if v["unsupported"] else "")
                  + ("   ADMISSIBLE" if v["errors"] == 0 and r["rung_candidate"]
                     else ""))

    problems.extend(spelling_problems(rows, args.verus))
    out = {"identity_pinned": pinned, "identity_measured": measured,
           "rows": {k: {kk: vv for kk, vv in v.items() if kk != "exe"}
                    for k, v in rows.items()},
           "verus_ran": args.verus, "problems": problems}
    dst = os.path.join(HERE, "spellings.json")
    out.update(_pin.pin(
        ['safe_tuned.rs', 'unsafe.rs', 'verus.rs', 'spec.md', 'inputs/gen.py', 'controls/spellings.py'],
        'python3 patterns-php/ph55-opdata-stride/controls/spellings.py --verus',
        'the two rung sources the variants are derived from, verus.rs (the R4 admissibility half), spec.md (the declaration the audit runs against AND the `identity` pin the admissibility rule reads), inputs/gen.py and this script.'))
    json.dump(out, open(dst, "w"), indent=2, sort_keys=True, default=str)
    print(f"\nwrote {os.path.relpath(dst, ROOT)}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
