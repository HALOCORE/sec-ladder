#!/usr/bin/env python3
"""ph53 control: **THE PROOF'S MUTANTS, MIRI, AND THE WITNESS-FREE R4.**

    python3 patterns-php/ph53-iface-tail-uninit/controls/negatives.py --selftest
    python3 .../negatives.py --verus      # the four mutants only
    python3 .../negatives.py --miri       # the Miri arms only
    python3 .../negatives.py --emit M1    # write a mutant and stop

⚠⚠ **`PROTOCOL_PHP.md` §H: a change to a validator lands with its must-fire
negatives, or it does not land — and a GATE RUN EXERCISES A PROOF ON THE
PROGRAM THAT PASSES, IT DOES NOT ATTACK IT.** `verus.rs` verifying 27/0 says
nothing about what Verus does to a program that should be refused. This file
is what says it.

============================================================================
WHAT IS MUTATED, AND WHY EACH ONE IS THE RIGHT MUTANT
============================================================================
Every mutant is a TEXTUAL deletion from the shipped `verus.rs`, so it is the
shipped proof minus one thing and cannot drift from it.

    M1  nowitness   delete the two `if wrote[i]` guards from the query loops.
                    ⭐⭐ THE ROW'S CENTRAL NEGATIVE. That program is the
                    FAITHFUL unsafe port -- `zend_operators.c:1534-1535` with
                    nothing between the loop and the read -- and Verus must
                    refuse it at `slot_read_unchecked`'s second `requires`
                    conjunct, `v@[i as int].mem_contents().is_init()`, which is
                    `MaybeUninit::assume_init`'s own precondition folded into
                    the trusted item (NOTES.md 11.5 is why it had to be). **It is refused for a reason
                    that is not about Verus being weak**: coverage is a
                    property of the op stream, i.e. of attacker data, and the
                    pinned driver loop offers no call site at which to
                    establish it. `controls/r4_nowitness.rs` is that program as
                    plain Rust, measured and Miri'd below.
    M2  norange     delete the `value() < n_pool` conjunct from the op loop's
                    invariant. Verus must refuse `pool_get_unchecked`'s
                    `i < MAXP`. ⚠ THIS IS THE CONJUNCT THAT IS *NOT* PART OF
                    THE C's OBLIGATION -- the C stores a pointer and needs only
                    that it designate a class -- so M1 and M2 together show
                    that the Rust representation's obligation really is two
                    facts and not one, rather than the row asserting it.
    M3  vacuous     replace the kernel's body with `0u64`. Must fail
                    `postcondition not satisfied`. Without it, every bounds
                    obligation in the file would be satisfied by a kernel that
                    computes nothing (`.memory/04-verus.md`).
    M4  noidx       delete the `idx@[j] == j` conjunct from the op loop's
                    invariant. Must refuse `slot_set_unchecked`'s
                    `i < old(v)@.len()`. It is the window-side half of the
                    proof and it comes from the harness's structural
                    precondition rather than from PHP.

    N1  MUST-NOT-FIRE: the SHIPPED `verus.rs` verifies, plain and twin.
                    A suite of four refusals proves nothing if the unmutated
                    file is also refused.
    N2  MUST-NOT-FIRE: ⭐ `controls/mu_unwrapped.rs` verifies at 7/0. It drives
                    the same `MaybeUninit` operations with **no trusted item at
                    all**, letting vstd's own `assume_specification` carry the
                    obligation -- so it is what keeps `slot_read_unchecked`'s
                    HAND-ASSERTED `requires` checkable against what vstd
                    actually says. That item has no verified twin and cannot
                    (NOTES.md 11.5), so this is the substitute, and it is a
                    stronger object than a twin: a twin re-states the contract,
                    this one derives it.

============================================================================
MIRI, AND WHY IT MATTERS MORE ON THIS ROW THAN THE RULE ANTICIPATES
============================================================================
The defect is an **uninitialised read of an IN-BOUNDS slot** — CWE-824, not
CWE-125 — and **ASan cannot see that class at all**: it is MSan's, and what the
ASan build reports on the C rung is the SEGV that follows the dereference.
⭐ **Miri is the only detector in this tree that sees the read itself.** Four
arms:

    A1 MUST-FIRE     `controls/r4_nowitness.rs` on an UNCOVERED blob -- Miri
                     must report uninitialised memory
    A2 MUST-NOT-FIRE `controls/r4_nowitness.rs` on `inputs/small.bin` -- the
                     measured corpus covers every slot before any query, so
                     even the witness-free program is clean there. Without this
                     arm A1 could be a claim about the program rather than
                     about the coverage
    A3 MUST-NOT-FIRE the SHIPPED `unsafe.rs` on the SAME uncovered blob -- the
                     witness works, which is the whole reason it is there
    A4 MUST-NOT-FIRE the SHIPPED `unsafe.rs` on `inputs/small.bin`, which is
                     what `check.py` stage 8 also runs

============================================================================
WHAT THE WITNESS COSTS
============================================================================
`--selftest` also callgrinds `r4_nowitness.rs` against the shipped `unsafe.rs`
on `inputs/small.bin`, so the row can say what the witness costs instead of
asserting that it is cheap. ⚠ The two programs are not equivalent on an
uncovered blob, so this is a cost comparison on the MEASURED corpus only and
the report says so.

============================================================================
⚠ THE FINGERPRINT'S TWO INHERITED DEFECTS ARE FIXED HERE, AND NOT INHERITED
============================================================================
`RECAP_PHP.md` open items **57** and **63**: the shared `spellings.py`
machinery's `kernel_fingerprint` returns `(0, md5(""))` for a binary that does
not exist -- because `disasm` ignores `objdump`'s return code -- **so two
missing binaries compare EQUAL on the one function whose job is to decide
byte-identity** -- and its symbol needle is a bare substring, so a crate named
`nokernel` fingerprints its own `main`. Both are latent on `ph16` and `ph29`
and `_035`/`_037` correctly declined to widen their scope into another row's
control.

▶ **This file does not clone that code. `kernel_fingerprint` below checks
`objdump`'s return code, refuses an empty disassembly, anchors the needle on
`::kernel` at the end of the demangled symbol, and refuses more than one
match** -- and F1/F2/F3 below are the must-fire negatives for exactly those
three, driven on a path that does not exist, on a stripped binary and on a
synthetic two-match table. ⭐ **The general shape open items 57 and 63 record
is that a control cloned between rows carries its defects and only the row
that writes NEW negatives finds them; the cheaper move is not to clone.**
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
OUT = os.path.join(REPO, ".temp", "php41", "negatives")

VERUS_RUN = os.path.join(REPO, "verus_run.py")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
CARGO = os.path.expanduser("~/.cargo/bin/cargo")
NIGHTLY = "nightly-x86_64-unknown-linux-gnu"
MIRI_BIN = os.path.expanduser(f"~/.rustup/toolchains/{NIGHTLY}/bin/miri")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")

sys.path.insert(0, os.path.join(REPO, "common-php"))
sys.path.insert(0, ROW)
import slb  # noqa: E402
from model import Model, OP_FILL, OP_QD  # noqa: E402

STRIDE = 221
POOL_IDS = tuple(0x0C1A55_000000_01 + j for j in range(8))

# --------------------------------------------------------------------------
# the mutations. Each is (needle, replacement) pairs applied to verus.rs, with
# `n` the number of sites each pair must hit -- so a mutation that stops
# applying because the source moved is a LOUD failure and not a silent pass.
# --------------------------------------------------------------------------
MUTANTS = {
    "M1": ("nowitness -- the two `if wrote[i]` guards deleted: the FAITHFUL "
           "unsafe port, which is zend_operators.c:1534-1535 with nothing "
           "between the loop and the read",
           [("""        if wrote[i] {
            let p: u32 = slot_read_unchecked(slots, i);
            let id: u64 = pool_get_unchecked(pool, p as usize);
            assert(a[i as int] == Some(p));
            if id == target_id {
                assert(scan_d(a, pool@, i as int, n as int, target_id) == (1u64, id, (i + 1)
                    as u64));
                return (1, id, examined);
            }
        } else {
            assert(a[i as int] is None);
        }""",
             """        {
            let p: u32 = slot_read_unchecked(slots, i);
            let id: u64 = pool_get_unchecked(pool, p as usize);
            if id == target_id {
                return (1, id, examined);
            }
        }""", 1),
            ("""        if wrote[i] {
            let p: u32 = slot_read_unchecked(slots, i);
            assert(a[i as int] == Some(p));
            if p == target {
                assert(scan_c(a, i as int, n as int, target) == i as u64);
                return i;
            }
        } else {
            assert(a[i as int] is None);
        }""",
             """        {
            let p: u32 = slot_read_unchecked(slots, i);
            if p == target {
                return i;
            }
        }""", 1)],
           "mem_contents"),
    "M2": ("norange -- the `value() < n_pool` conjunct deleted from the op "
           "loop's invariant: the obligation that is the PRICE OF THE "
           "REPRESENTATION and not part of the C's",
           [("""                0 <= j < n_decl ==> (#[trigger] wrote@[j] ==> slots@[j].mem_contents().is_init()
                    && slots@[j].mem_contents().value() < n_pool),""",
             """                0 <= j < n_decl ==> (#[trigger] wrote@[j] ==> slots@[j].mem_contents().is_init()),""",
             1)],
           None),
    "M3": ("vacuous -- the kernel's body replaced by `0u64`: without this "
           "negative every bounds obligation in the file is satisfied by a "
           "kernel that computes nothing",
           [("""    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    let win: &[u8] = &buf[off..off + len];""",
             """    return 0u64;
    #[allow(unreachable_code)] let _unused: () = ();
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    let win: &[u8] = &buf[off..off + len];""", 1)],
           "postcondition not satisfied"),
    "M4": ("noidx -- the `idx@[j] == j` conjunct deleted from the op loop's "
           "invariant: the window-side half of the proof, which comes from the "
           "harness's structural precondition rather than from PHP",
           [("""            forall|j: int| 0 <= j < n_decl ==> #[trigger] idx@[j] == j,
            slots@.len() == n_decl,""",
             """            slots@.len() == n_decl,""", 1)],
           None),
}


def _run(cmd, timeout=1800, env=None, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                       env=env, cwd=cwd)
    return r.returncode, (r.stdout + r.stderr)


def emit(tag):
    """Write one mutant of verus.rs into `.temp/` and return its path."""
    desc, edits, _ = MUTANTS[tag]
    src = open(os.path.join(ROW, "verus.rs")).read()
    for needle, repl, n in edits:
        got = src.count(needle)
        if got != n:
            raise SystemExit(
                f"MUTANT {tag} DOES NOT APPLY: its needle occurs {got} times, "
                f"expected {n}. verus.rs has moved and this mutant is no "
                f"longer the shipped proof minus one thing -- which is exactly "
                f"the state in which a must-fire negative silently stops "
                f"firing. Repair the needle, do not relax the count.")
        src = src.replace(needle, repl)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"verus-{tag}.rs")
    open(p, "w").write(src)
    return p, desc


# --------------------------------------------------------------------------
# the guarded kernel fingerprint -- open items 57 and 63, fixed rather than
# inherited
# --------------------------------------------------------------------------
_SYM = re.compile(r"^[0-9a-f]+ <(\S+)>:$")


def kernel_fingerprint(path, sym_suffix="kernel"):
    """(n_insn, md5) of the kernel function's padding-free instruction text.

    Raises on anything ambiguous. ⚠ THE THREE GUARDS ARE THE POINT and each has
    a must-fire negative below:

      (a) `objdump`'s RETURN CODE is checked. The inherited version ignored it,
          so a MISSING binary disassembled to "" and fingerprinted as
          `(0, d41d8cd98f00...)` -- and two missing binaries then compared
          EQUAL on the one function whose job is to decide byte-identity
          (open items 57(a) and 63).
      (b) an EMPTY disassembly is refused even when objdump succeeds, because
          a stripped or section-less binary is not a byte-identity answer.
      (c) the symbol needle is ANCHORED: the demangled name must END in
          `::kernel` (or be exactly `kernel`, which is the C spelling), and
          MORE THAN ONE match is refused. The inherited version used a bare
          substring, so a crate named `nokernel` fingerprinted its own `main`
          (open item 57(b)).
    """
    if not os.path.exists(path):
        raise ValueError(f"kernel_fingerprint: {path} does not exist. A "
                         f"missing binary has no fingerprint; returning one "
                         f"is how two absent cells come to compare equal "
                         f"(RECAP_PHP.md open items 57, 63).")
    rc, out = _run(["objdump", "-d", "-C", "--no-show-raw-insn", "-j", ".text",
                    path], timeout=300)
    if rc != 0:
        raise ValueError(f"kernel_fingerprint: objdump exited {rc} on {path}")
    if not out.strip():
        raise ValueError(f"kernel_fingerprint: objdump produced NOTHING for "
                         f"{path} -- stripped, or no .text")
    funcs, cur = {}, None
    for line in out.split("\n"):
        m = _SYM.match(line.strip())
        if m:
            cur = m.group(1)
            funcs[cur] = []
            continue
        if cur is not None and "\t" in line:
            funcs[cur].append(line.split("\t", 1)[1].strip())
    hits = [k for k in funcs
            if k == sym_suffix or k.endswith("::" + sym_suffix)]
    if not hits:
        raise ValueError(f"kernel_fingerprint: no symbol ending in "
                         f"`::{sym_suffix}` in {path}. Candidates: "
                         f"{sorted(funcs)[:8]}")
    if len(hits) > 1:
        raise ValueError(f"kernel_fingerprint: {len(hits)} symbols end in "
                         f"`::{sym_suffix}` in {path} ({hits}) -- ambiguous, "
                         f"and picking one is how a bare substring needle "
                         f"fingerprints the wrong function")
    ins = [i for i in funcs[hits[0]]
           if not i.startswith(("nop", "xchg %ax", "data16", "cs nop"))]
    if not ins:
        raise ValueError(f"kernel_fingerprint: {hits[0]} in {path} has no "
                         f"non-padding instruction")
    return len(ins), hashlib.md5("\n".join(ins).encode()).hexdigest()[:12]


def _fingerprint_negatives():
    bad = []
    # F1: a path that does not exist must RAISE, not return (0, md5("")).
    try:
        kernel_fingerprint(os.path.join(OUT, "does-not-exist"))
        bad.append("F1: kernel_fingerprint returned a value for a MISSING "
                   "binary -- open items 57(a)/63's defect, reproduced")
    except ValueError:
        print("  ok   F1 MUST-FIRE: a missing binary raises (open item 57a/63)")
    # F2: a binary with no such symbol must RAISE.
    os.makedirs(OUT, exist_ok=True)
    tiny = os.path.join(OUT, "tiny.c")
    open(tiny, "w").write("int notkernel(int x){return x+1;}\nint main(void){return notkernel(1);}\n")
    tinyb = os.path.join(OUT, "tiny")
    rc, log = _run(["gcc", "-O0", "-o", tinyb, tiny])
    if rc != 0:
        bad.append(f"F2: could not build the probe binary: {log[:200]}")
    else:
        try:
            n, h = kernel_fingerprint(tinyb)
            bad.append(f"F2: kernel_fingerprint matched `notkernel` -- "
                       f"({n}, {h}) -- so the needle is still a BARE "
                       f"SUBSTRING (open item 57b's defect, reproduced)")
        except ValueError:
            print("  ok   F2 MUST-FIRE: `notkernel` does not match the anchored "
                  "needle (open item 57b)")
    # F3: two matching symbols must RAISE rather than silently pick one.
    two = os.path.join(OUT, "two.c")
    open(two, "w").write("int kernel(int x){return x+1;}\n"
                         "int a_kernel(int x){return x+2;}\n"
                         "int main(void){return kernel(1)+a_kernel(2);}\n")
    twob = os.path.join(OUT, "two")
    rc, log = _run(["gcc", "-O0", "-o", twob, two])
    if rc == 0:
        try:
            n, h = kernel_fingerprint(twob, sym_suffix="kernel")
            print(f"  ok   F3 MUST-NOT-FIRE: `a_kernel` does NOT end in "
                  f"`::kernel` and is not a second match, so the exact `kernel` "
                  f"is picked unambiguously ({n} insn, {h})")
        except ValueError as e:
            bad.append(f"F3: the unambiguous C symbol `kernel` was refused "
                       f"beside `a_kernel`: {e}")
    return bad


# --------------------------------------------------------------------------
def verus_arms():
    bad = []
    print("-- Verus mutants " + "-" * 60)
    for tag in ("M1", "M2", "M3", "M4"):
        p, desc = emit(tag)
        rc, log = _run([sys.executable, VERUS_RUN, p, "--multiple-errors", "8"])
        errs = re.findall(r"^error(?:\[[^\]]*\])?: (.*)$", log, re.M)
        res = re.search(r"verification results:: (\d+) verified, (\d+) errors",
                        log)
        want = MUTANTS[tag][2]
        ok = rc != 0 and (res is None or int(res.group(2)) > 0)
        txt = " | ".join(errs[:3])[:200]
        print(f"  {tag} {desc[:62]}")
        print(f"     rc={rc} results={res.group(0) if res else 'none'}")
        print(f"     errors: {txt}")
        if not ok:
            bad.append(f"{tag}: MUST-FIRE mutant VERIFIED ({log[-300:]}). The "
                       f"obligation it deletes is therefore not being checked.")
        elif want and want not in log:
            bad.append(f"{tag}: refused, but the error text does not mention "
                       f"{want!r} -- it may be failing for the wrong reason, "
                       f"which is not evidence about this obligation")
        else:
            print(f"     ok   MUST-FIRE: refused"
                  + (f", and the text names {want!r}" if want else ""))
    # N2 MUST-NOT-FIRE: the committed unwrapped control. ⭐ It is what stands
    # in for `slot_read_unchecked`'s missing twin, so it runs in the same arm.
    ctl = os.path.join(ROW, "controls", "mu_unwrapped.rs")
    rc, log = _run([sys.executable, VERUS_RUN, ctl])
    res = re.search(r"verification results:: (\d+) verified, (\d+) errors", log)
    if rc != 0 or not res or int(res.group(2)) != 0:
        bad.append(f"N2: controls/mu_unwrapped.rs did NOT verify ({log[-400:]}). "
                   f"That file is the ONLY thing checking that "
                   f"`slot_read_unchecked`'s hand-asserted `requires` is the "
                   f"one vstd actually demands -- the item has no twin and "
                   f"cannot have one (NOTES.md 11.5) -- so its failure means "
                   f"the trusted contract may have drifted from vstd.")
    elif int(res.group(1)) != 7:
        bad.append(f"N2: controls/mu_unwrapped.rs verifies {res.group(1)} "
                   f"obligations, its own docstring says 7. Update the "
                   f"docstring; do not relax this check.")
    else:
        print(f"  ok   N2 MUST-NOT-FIRE: controls/mu_unwrapped.rs {res.group(1)}/0 "
              f"-- the obligation verifies UNWRAPPED, against vstd's own "
              f"`assume_init` spec and with no trusted item")

    # N1 MUST-NOT-FIRE: the shipped file, plain and twin.
    for cfg, want in ((None, 27), ("slb_twin", 30)):
        cmd = [sys.executable, VERUS_RUN, os.path.join(ROW, "verus.rs")]
        if cfg:
            cmd += ["--cfg", cfg]
        rc, log = _run(cmd)
        res = re.search(r"verification results:: (\d+) verified, (\d+) errors",
                        log)
        label = cfg or "plain"
        if rc != 0 or not res or int(res.group(2)) != 0:
            bad.append(f"N1 {label}: the SHIPPED verus.rs did not verify "
                       f"({log[-300:]}). Four refusals prove nothing if the "
                       f"unmutated file is refused too.")
        elif int(res.group(1)) != want:
            bad.append(f"N1 {label}: {res.group(1)} obligations, spec.md pins "
                       f"{want}")
        else:
            print(f"  ok   N1 MUST-NOT-FIRE: shipped verus.rs {label} "
                  f"{res.group(1)}/0, matching spec.md")
    return bad


def _uncovered_blob():
    """n_decl 2, one FILL, one QUERY_DEREF -- slot 1 is read and dereferenced.
    Generated here: `.temp/` is gitignored and a committed file must not rest a
    claim on a `.temp/` path (RECAP_PHP.md open item 65)."""
    os.makedirs(OUT, exist_ok=True)
    ops = [(OP_FILL, 0, 0), (OP_QD, 1, 0)]
    win = Model._mkwin(STRIDE, 2, 7, len(ops), POOL_IDS, ops)
    p = os.path.join(OUT, "uncovered.bin")
    slb.write(p, 4, slb.pack_head1_bytes(STRIDE, win))
    return p


def _miri_sysroot():
    rc, out = _run([CARGO, f"+{NIGHTLY}", "miri", "setup", "--print-sysroot"],
                   timeout=1800)
    return out.strip().split("\n")[-1] if rc == 0 else None


def _small_probe():
    """`inputs/small.bin` with `n_iters` clamped to 4, exactly as check.py's
    Miri stage does."""
    f = slb.read(os.path.join(ROW, "inputs", "small.bin"))
    p = os.path.join(OUT, "small-4.bin")
    slb.write(p, 4, f.payload[: f.declared_len])
    return p


def miri_arms():
    bad = []
    print("-- Miri " + "-" * 69)
    if not os.path.exists(MIRI_BIN):
        print(f"  BLOCKED: no miri at {MIRI_BIN} (TOOLCHAIN.md). Recorded as "
              f"blocked, never as a pass.")
        return ["miri BLOCKED -- the four arms were not run"]
    sysroot = _miri_sysroot()
    if not sysroot:
        return ["miri sysroot could not be built -- the four arms were not run"]
    unc, small = _uncovered_blob(), _small_probe()
    env = dict(os.environ)
    env.pop("MIRIFLAGS", None)
    arms = [
        ("A1", "controls/r4_nowitness.rs", unc, True,
         "the WITNESS-FREE R4 on an uncovered blob"),
        ("A2", "controls/r4_nowitness.rs", small, False,
         "the witness-free R4 on the MEASURED corpus (covered, so clean)"),
        ("A3", "unsafe.rs", unc, False,
         "the SHIPPED R4 on the same uncovered blob (the witness works)"),
        ("A4", "unsafe.rs", small, False,
         "the shipped R4 on the measured corpus"),
    ]
    for tag, src, blob, must_fire, what in arms:
        spath = os.path.join(ROW, src)
        try:
            rc, log = _run([MIRI_BIN, "--sysroot", sysroot, "--edition", "2021",
                            "-Zmiri-disable-isolation", spath, "--", blob],
                           timeout=600, env=env, cwd=ROW)
        except subprocess.TimeoutExpired:
            bad.append(f"{tag}: miri did not finish in 600s on {src}")
            continue
        ub = "Undefined Behavior" in log or "error: unsupported operation" in log
        first = next((l.strip() for l in log.split("\n")
                      if "Undefined Behavior" in l or l.startswith("error")), "")
        print(f"  {tag} {what}")
        print(f"     rc={rc} ub={ub}  {first[:160]}")
        if must_fire and not ub:
            bad.append(f"{tag}: MUST-FIRE and Miri reported nothing. The "
                       f"uninitialised read is the whole defect, and Miri is "
                       f"the only detector in this tree that sees it -- ASan "
                       f"sees only the dereference that follows.")
        elif must_fire:
            print(f"     ok   MUST-FIRE: Miri reports it")
        elif ub:
            bad.append(f"{tag}: MUST-NOT-FIRE and Miri reported UB: "
                       f"{first[:200]}")
        else:
            print(f"     ok   MUST-NOT-FIRE: silent")
    return bad


def cost_arm():
    """What the witness costs, on the MEASURED corpus."""
    print("-- what the witness costs (Ir, small.bin, O3/isolated) " + "-" * 22)
    if not os.path.exists(VALGRIND):
        print(f"  BLOCKED: no valgrind at {VALGRIND}")
        return []
    os.makedirs(OUT, exist_ok=True)
    small = os.path.join(ROW, "inputs", "small.bin")
    outs = {}
    for tag, src in (("R4ship", "unsafe.rs"),
                     ("R4nowitness", "controls/r4_nowitness.rs")):
        b = os.path.join(OUT, tag)
        rc, log = _run([RUSTC, "--edition", "2021", "-C", "codegen-units=1",
                        "-C", "opt-level=3", "-C", "debug-assertions=off",
                        "--cfg", "slb_isolated", os.path.join(ROW, src),
                        "-o", b])
        if rc != 0:
            print(f"  BUILD FAILED {tag}: {log[:300]}")
            return [f"cost arm: {tag} did not build"]
        cg = os.path.join(OUT, f"cg.{tag}")
        rc, log = _run([VALGRIND, "--tool=callgrind", f"--callgrind-out-file={cg}",
                        "--", b, small], timeout=1800)
        tot = re.search(r"refs:\s+([\d,]+)", log)
        n, h = kernel_fingerprint(b)
        outs[tag] = (int(tot.group(1).replace(",", "")) if tot else None, n, h)
        print(f"  {tag:12s} whole-program Ir={outs[tag][0]:,}  "
              f"kernel {n} insn  md5 {h}")
    a, b = outs["R4ship"][0], outs["R4nowitness"][0]
    if a and b:
        print(f"  ⭐ the witness costs {a - b:+,} Ir over the whole run "
              f"({100.0 * (a - b) / b:+.4f} %), and "
              f"{outs['R4ship'][1] - outs['R4nowitness'][1]:+d} kernel "
              f"instructions")
        print(f"  ⚠ MEASURED CORPUS ONLY: the two programs are NOT equivalent "
              f"on an uncovered blob -- that is what the witness is for.")
    return []


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true", help="all arms")
    ap.add_argument("--verus", action="store_true")
    ap.add_argument("--miri", action="store_true")
    ap.add_argument("--cost", action="store_true")
    ap.add_argument("--emit", metavar="TAG", help="write one mutant and stop")
    a = ap.parse_args()
    if a.emit:
        p, desc = emit(a.emit)
        print(f"{a.emit}: {desc}\n  -> {p}")
        return 0
    allof = a.selftest or not (a.verus or a.miri or a.cost)
    bad = []
    if allof or a.verus:
        bad += _fingerprint_negatives()
        bad += verus_arms()
    if allof or a.miri:
        bad += miri_arms()
    if allof or a.cost:
        bad += cost_arm()
    print()
    if bad:
        print("SELFTEST FAIL")
        for b in bad:
            print(f"    {b}")
        return 1
    print("SELFTEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
