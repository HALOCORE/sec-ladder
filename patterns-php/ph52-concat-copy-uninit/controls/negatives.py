#!/usr/bin/env python3
"""ph52 controls: the must-fire / must-NOT-fire suite for the row's two claims
that no gate stage checks.

    python3 patterns-php/ph52-concat-copy-uninit/controls/negatives.py --verus
    python3 .../negatives.py --miri
    python3 .../negatives.py --firstcall
    python3 .../negatives.py --all

⚠⚠ **WHY EACH ARM EXISTS, because a suite whose arms are not justified is a suite
nobody will maintain** (`PROTOCOL_PHP.md` §H).

`--verus`  The row's Verus-side claim is *a rung that REPRODUCES this defect
           cannot be VERIFIED*. A green `verus.rs` is not evidence for that: it is
           evidence that the rung WITH the witness verifies. ▶ So this arm (a)
           re-verifies `mu_unwrapped.rs`, which is the same obligation with NO
           trusted item, and (b) generates FIVE MUTANTS of `../verus.rs` -- four
           must-fire and one must-NOT-fire -- the witness test deleted, each
           `requires` conjunct that carries initialisedness deleted in turn, the
           tag written on a path that did not write the value, and one cosmetic
           rewrite that must STILL verify.
           ⭐ **Mutant V1 is the whole finding: deleting `if *constructed` is
           `Zend/zend.c:243` exactly, and Verus refuses it at
           `std_specs/maybe_uninit.rs`.**

`--miri`   The shipped `unsafe.rs` must be SILENT and `r4_nowitness.rs` must be
           LOUD. ⚠⚠ **AND THE BLOB THAT MAKES IT LOUD IS ONE `inputs/` CANNOT
           CARRY**, because a window whose op 0 is the faulting arm reads whatever
           the previous frame left -- which for `MaybeUninit` is Rust-level UB and
           for the C is build-dependent (`../inputs/gen.py` rule R1). This arm
           generates it. ⭐ Miri is the ONLY detector in this tree that sees this
           read: `model.py::sanitizer_expect` is `clean` on every input and §7 of
           `../NOTES.md` measures the two independent reasons why.

`--firstcall`
           ⚠⚠ **THE NONDETERMINISM `inputs/` IS NOT ALLOWED TO CONTAIN, MEASURED
           RATHER THAN ASSERTED.** Builds the faulting-arm-at-op-0 blob and runs
           the four C cells on it, reporting the spread. It is what justifies
           `gen.py`'s rule R1 -- and it is `.memory-php/02-ladder.md` F31's
           prescription taken for ONE input rather than for the row.

⚠ Every arm's negatives are NEW to this row and none is inherited
(`.memory-php/04-process.md` law 7: a control cloned between rows carries its
defects, and only the row that writes new negatives finds them).
"""

import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
VERUS_RUN = os.path.join(REPO, "verus_run.py")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
GCC = "/usr/bin/gcc"
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")
TMP = os.path.join(REPO, ".temp", "php45", "neg")

sys.path.insert(0, os.path.join(REPO, "common-php"))
sys.path.insert(0, ROW)
import slb  # noqa: E402
import model  # noqa: E402

# ---------------------------------------------------------------------------
# the blob `inputs/` is not allowed to carry
# ---------------------------------------------------------------------------
STRIDE = 74


def faulting_at_op0(path):
    """A window whose op 0 carries the FAULTING arm on BOTH sides.

    ⛔ `../inputs/gen.py` rule R1 forbids exactly this: `zend.c:243` then reads
    whatever the previous frame left at that stack offset, which is the C
    runtime's own startup residue on the program's first kernel call. That makes
    the u64 not a function of the blob, so it cannot be an `inputs/` file in a
    tree whose gate compares six rungs' checksums."""
    A_OBJ = model.ARM_OBJECT
    body = bytearray()
    body += model._u32(2)                    # n_ops
    body += model._u32(0x5A5A1234)           # fold_w
    body += bytes((A_OBJ, 1, A_OBJ, 1))      # op 0: the FAULTING arm, both sides
    body += bytes((model.ARM_NULL, 0, model.ARM_NULL, 0))
    body += bytes(STRIDE - len(body))
    payload = slb.pack_head1_bytes(STRIDE, bytes(body))
    slb.write(path, 1, payload)
    return path


# ---------------------------------------------------------------------------
# --verus
# ---------------------------------------------------------------------------
#: (name, edits, must_fire, wanted text, why)
#: ⚠⚠ EACH `wanted` IS A SPECIFIC VERUS DIAGNOSTIC AND NOT THE WORD "error".
#: The first draft of this suite used `"error"` for two arms and they PASSED on a
#: `#[path]` resolution failure -- a must-fire arm firing for a reason that has
#: nothing to do with the mutation. That is §H's own target and it is recorded here
#: rather than quietly fixed.
VERUS_MUTANTS = [
    ("V1 witness test deleted", [
        ("    if *constructed {\n        let p: Pr = slot_read_unchecked(slot);",
         "    {\n        let p: Pr = slot_read_unchecked(slot);")],
     True, "precondition not satisfied",
     "deleting `if *constructed` IS `Zend/zend.c:243`. Verus must refuse the "
     "faithful port, and THAT is the row's Verus-side result"),

    ("V2 caller's is_init requires deleted", [
        ("        *old(constructed) ==> old(expr_copy).mem_contents().is_init()\n"
         "            && old(expr_copy).mem_contents().value().req == sl.req,\n",
         "")],
     True, "precondition not satisfied",
     "`make_printable_zval` is where the slot's initialisedness ENTERS the proof; "
     "without that conjunct its own `:243` call cannot discharge `zval_dtor`'s"),

    ("V3 zval_dtor's witness-agreement requires deleted", [
        ("    requires\n        sl.c == *old(constructed),\n",
         "    requires\n")],
     True, "postcondition not satisfied",
     "the ghost slot and the runtime witness must agree, or `s_dtor`'s own "
     "transition is not what the code performs"),

    ("V4 tag written without the value", [
        ("    *expr_copy = MaybeUninit::new(pr);\n    *constructed = true;",
         "    if pr.req != 0 {\n        *expr_copy = MaybeUninit::new(pr);\n    }\n"
         "    *constructed = true;")],
     True, "postcondition not satisfied",
     "⭐ THE WRITE ORDER, AS A MUTANT. Setting the witness on a path that did not "
     "write the slot is the defect one level up, and the proof must not survive it"),

    ("V5 equivalent rewrite of the witness test", [
        ("    if *constructed {\n        let p: Pr = slot_read_unchecked(slot);",
         "    if *constructed == true {\n        let p: Pr = slot_read_unchecked(slot);")],
     False, "",
     "MUST-NOT-FIRE: the suite must be keyed on the FUNCTION and not on the "
     "spelling, or a cosmetic edit would look like a defect"),
]


def verus_run(src, extra=()):
    cmd = [sys.executable, VERUS_RUN, src] + list(extra)
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO, timeout=2400)
    return r.returncode, (r.stdout + r.stderr)


def arm_verus():
    os.makedirs(TMP, exist_ok=True)
    fails = []
    print("  --verus")

    # N1 MUST-NOT-FIRE: the shipped rung verifies
    rc, out = verus_run(os.path.join(ROW, "verus.rs"))
    m = re.search(r"(\d+) verified, (\d+) error", out)
    print(f"    N1 verus.rs                        {m.group(0) if m else out[-120:]}")
    if rc != 0 or not m or m.group(2) != "0":
        fails.append("N1: the shipped verus.rs must verify")

    # N2 MUST-NOT-FIRE: the same obligation, unwrapped, with NO trusted item
    rc, out = verus_run(os.path.join(HERE, "mu_unwrapped.rs"))
    m2 = re.search(r"(\d+) verified, (\d+) error", out)
    print(f"    N2 mu_unwrapped.rs                 {m2.group(0) if m2 else out[-120:]}")
    if rc != 0 or not m2 or m2.group(2) != "0":
        fails.append("N2: mu_unwrapped.rs must verify -- it is what keeps the "
                     "hand-asserted contract checkable against vstd's")

    # the mutants: each MUST FIRE
    base = open(os.path.join(ROW, "verus.rs")).read()
    for name, edits, must_fire, want, why in VERUS_MUTANTS:
        txt = base
        applied = True
        for old, new in edits:
            if old not in txt:
                applied = False
                break
            txt = txt.replace(old, new, 1)
        if not applied:
            fails.append(f"{name}: the mutation target is GONE from verus.rs, so "
                         f"this negative checks nothing [{why}]")
            print(f"    {name:34s} TARGET MISSING")
            continue
        p = os.path.join(TMP, "mut_" + name.split()[0] + ".rs")
        # ⚠ `.temp/php45/neg/` is THREE levels below the repo root where the row is
        # TWO, so the `#[path]` has to be re-based or the mutant fails to RESOLVE
        # and a must-fire arm passes for the wrong reason.
        open(p, "w").write(txt.replace('#[path = "../../common/driver.rs"]',
                                       '#[path = "../../../common/driver.rs"]'))
        rc, out = verus_run(p)
        vr = re.search(r"(\d+) verified, (\d+) error", out)
        clean = bool(vr) and vr.group(2) == "0" and rc == 0
        fired = (not clean) and (want in out) if must_fire else (not clean)
        tail = (vr.group(0) if vr else "") + "  " + re.sub(r"\s+", " ", out)[-110:]
        ok = fired if must_fire else clean
        print(f"    {name:42s} rc={rc} clean={clean} ok={ok}  {tail}")
        if not ok:
            if must_fire:
                fails.append(f"{name}: MUST FIRE with {want!r}, got rc={rc} "
                             f"clean={clean} [{why}]")
            else:
                fails.append(f"{name}: MUST NOT FIRE, got rc={rc} [{why}]")
    return fails


# ---------------------------------------------------------------------------
# --miri
# ---------------------------------------------------------------------------
#: `harness/check.py's `MIRI_BIN``, `:9949` -- the SAME command line the gate's Miri stage
#: uses, so a verdict here and a verdict there mean the same thing. ⚠ `MIRIFLAGS`
#: is deliberately NOT set: it is `cargo-miri`'s variable and the rustc driver
#: never parses it (`check.py`'s own note at `:422-425`).
NIGHTLY = "nightly-x86_64-unknown-linux-gnu"   # harness/check.py's `NIGHTLY`
MIRI_BIN = os.path.expanduser(f"~/.rustup/toolchains/{NIGHTLY}/bin/miri")
CARGO = os.path.expanduser("~/.cargo/bin/cargo")


def miri_sysroot():
    r = subprocess.run([CARGO, f"+{NIGHTLY}", "miri", "setup", "--print-sysroot"],
                       capture_output=True, text=True, timeout=1800)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def miri_run(src, blob, sysroot):
    env = dict(os.environ)
    env.pop("MIRIFLAGS", None)
    cmd = [MIRI_BIN, "--sysroot", sysroot, "--edition", "2021",
           "-Zmiri-disable-isolation", src, "--", blob]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800,
                           cwd=os.path.dirname(src), env=env)
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT"
    return r.returncode, (r.stdout + r.stderr)


def arm_miri():
    os.makedirs(TMP, exist_ok=True)
    fails = []
    print("  --miri")
    sysroot = miri_sysroot()
    if not sysroot:
        fails.append("miri sysroot unavailable -- the arm did not run")
        print("    miri sysroot unavailable; BLOCKED, not passed")
        return fails
    loud_blob = faulting_at_op0(os.path.join(TMP, "op0-faulting.bin"))
    shipped = [os.path.join(ROW, "inputs", n) for n in
               ("small.bin", "adversarial-dblfree.bin", "adversarial-safe.bin")]

    def say(name, rc, out, want_loud, why):
        loud = ("Undefined Behavior" in out) or ("uninitialized" in out)
        tail = re.sub(r"\s+", " ", out)[:200]
        print(f"    {name:46s} rc={rc} loud={loud}  {tail[:110]}")
        if loud != want_loud:
            fails.append(f"{name}: expected loud={want_loud} [{why}]")

    # M1 MUST-NOT-FIRE: the shipped rung, on every input
    for b in shipped:
        rc, out = miri_run(os.path.join(ROW, "unsafe.rs"), b, sysroot)
        say(f"M1 unsafe.rs on {os.path.basename(b)}", rc, out, False,
            "the shipped R4's witness is what makes the read defined")
    # M2 MUST-NOT-FIRE: the witness-free control on the SHIPPED inputs.
    #    ⭐ It is silent, and that is a measured fact with a reason: `gen.py`'s
    #    rules R1-R3 mean no `:243` in the measured corpus ever sees a slot that
    #    was never constructed, so even the faithful port reads only INITIALISED
    #    memory -- it reproduces the DOUBLE FREE without an uninitialised read.
    for b in shipped:
        rc, out = miri_run(os.path.join(HERE, "r4_nowitness.rs"), b, sysroot)
        say(f"M2 r4_nowitness.rs on {os.path.basename(b)}", rc, out, False,
            "gen.py's R1-R3 keep the measured corpus clear of the uninitialised "
            "read; the control's divergence on adversarial-dblfree is the DOUBLE "
            "FREE and not the read")
    # M3 MUST-FIRE: the witness-free control on the blob `inputs/` cannot carry
    rc, out = miri_run(os.path.join(HERE, "r4_nowitness.rs"), loud_blob, sysroot)
    say("M3 r4_nowitness.rs on op0-faulting", rc, out, True,
        "THE READ ITSELF. `zend.c:243` on a slot nothing wrote, and Miri is the "
        "only detector in this tree that sees it")
    # M4 MUST-NOT-FIRE: the shipped rung on the SAME blob
    rc, out = miri_run(os.path.join(ROW, "unsafe.rs"), loud_blob, sysroot)
    say("M4 unsafe.rs on op0-faulting", rc, out, False,
        "the witness is exactly what turns M3 into M4, which is the whole point "
        "of the one bit")
    return fails


# ---------------------------------------------------------------------------
# --firstcall
# ---------------------------------------------------------------------------
def arm_firstcall():
    os.makedirs(TMP, exist_ok=True)
    fails = []
    print("  --firstcall  (the nondeterminism `inputs/` is not allowed to carry)")
    blob = faulting_at_op0(os.path.join(TMP, "op0-faulting.bin"))
    answers = {}
    for cc, ccname in ((GCC, "gcc"), (CLANG, "clang")):
      for kern in ("kernel.c", "kernel_hardened.c"):
        for opt in ("-O0", "-O3"):
            for mode in ("isolated", "whole"):
                flags = ["-std=c99", "-Wall", "-Wextra", opt]
                flags += ["-DSLB_ISOLATED"] if mode == "isolated" else ["-flto"]
                if ccname == "clang" and mode == "whole":
                    flags = ["-fuse-ld=lld"] + flags
                tag = "R1" if kern == "kernel.c" else "R1h"
                out = os.path.join(TMP, f"fc-{tag}-{ccname}{opt}-{mode}")
                cmd = ([cc] + flags + ["-I", os.path.join(REPO, "common"),
                       "-I", os.path.join(ROW, "c"),
                       os.path.join(REPO, "common", "driver.c"),
                       os.path.join(ROW, "c", kern),
                       os.path.join(ROW, "c", "main.c"), "-o", out])
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                if r.returncode != 0:
                    print(f"    {tag} {ccname}{opt}-{mode:9s} BUILD FAILED")
                    continue
                rr = subprocess.run([out, blob], capture_output=True, text=True,
                                    timeout=300)
                key = f"{tag} {ccname}{opt}-{mode}"
                answers[key] = (rr.returncode, rr.stdout.strip() or
                                re.sub(r"\s+", " ", rr.stderr.strip())[:60])
                print(f"    {key:26s} exit={answers[key][0]} out={answers[key][1]}")
    r1 = {v for k, (_rc, v) in answers.items() if k.startswith("R1 ")}
    r1h = {v for k, (_rc, v) in answers.items() if k.startswith("R1h ")}
    print(f"    DISTINCT R1  ANSWERS ACROSS {len(r1)} value(s): {r1}")
    print(f"    DISTINCT R1h ANSWERS ACROSS {len(r1h)} value(s): {r1h}")
    # ⭐ THE OBSERVABLE THAT SAYS WHETHER THE RESIDUE WAS A FREEING TAG:
    #    R1h has no `:243` at all, so R1 == R1h iff `zval_dtor` no-opped.
    if r1 == r1h:
        print("    ⭐ R1 == R1h on this blob, so the startup residue was NOT one of "
              "the 12 freeing tag values -- which `controls/tag_sweep.py` measures "
              "at 12/256 = 4.688 %, i.e. the 95.3 % outcome. RECORDED, NOT "
              "REQUIRED: it is the C runtime's residue and the corpus may not rest "
              "on it, which is exactly `inputs/gen.py` rule R1.")
    else:
        print("    ⛔ R1 != R1h: the startup residue WAS a freeing tag and the "
              "defect fired on the program's first kernel call.")
    if len(r1h) > 1:
        fails.append(f"R1h must be deterministic on this blob and gave {r1h}")
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verus", action="store_true")
    ap.add_argument("--miri", action="store_true")
    ap.add_argument("--firstcall", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if not (a.verus or a.miri or a.firstcall or a.all):
        ap.print_help()
        return 2
    fails = []
    if a.verus or a.all:
        fails += arm_verus()
    if a.miri or a.all:
        fails += arm_miri()
    if a.firstcall or a.all:
        fails += arm_firstcall()
    for f in fails:
        print(f"  FAIL {f}")
    print("  ALL ARMS AS EXPECTED" if not fails else f"  {len(fails)} FAILURE(S)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
