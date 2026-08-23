#!/usr/bin/env python3
"""p22 controls: every variant that is NOT a rung, generated from the shipped
sources and measured rather than asserted.

Scratch lands in `.temp/p22/controls/` -- **this pattern's own subdirectory**.
p27's copy of a sibling's clayout still said `.temp/p14/` and overwrote p14's
`meta.json` (`915bb8a`); the constant below is the fix and it is checked at
import time.

    python3 patterns/p22-hash-probe/controls/gen_controls.py --list
    python3 patterns/p22-hash-probe/controls/gen_controls.py --run r2_noguard
    python3 patterns/p22-hash-probe/controls/gen_controls.py --run all --ir

⚠ **Several of these controls DO NOT TERMINATE by design.** Every run here is
under an explicit `timeout=`; nothing is backgrounded and nothing is killed by
name (`.memory/00-environment.md`).

Every control is derived from a shipped source by exact-string substitutions
recorded here, so a reader can see what changed without a diff, and a
substitution that stops matching is a hard error rather than a silent no-op.
Every control but the three isolation mutants is ONE substitution.

⚠ **Verus is always run with `--multiple-errors 20`** -- see `VERUS_FLAGS`.
"""

import argparse
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p22", "controls")     # <-- p22's OWN dir
assert OUT.endswith(os.path.join("p22", "controls")), OUT

GCC = "/usr/bin/gcc"
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
NIGHTLY = "nightly-x86_64-unknown-linux-gnu"
MIRI = os.path.expanduser(f"~/.rustup/toolchains/{NIGHTLY}/bin/miri")
MIRI_SYSROOT = os.path.expanduser("~/.cache/miri")
VERUS_RUN = os.path.join(REPO, "verus_run.py")
INPUTS = os.path.join(PDIR, "inputs")

sys.path.insert(0, os.path.join(REPO, "harness"))
import asm as asmmod        # noqa: E402

R2 = os.path.join(PDIR, "safe_naive.rs")
R3 = os.path.join(PDIR, "safe_tuned.rs")
R4 = os.path.join(PDIR, "unsafe.rs")
R5 = os.path.join(PDIR, "verus.rs")
CK = os.path.join(PDIR, "c", "kernel.c")


def sub(text, old, new, tag):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"gen_controls.py: {tag}: pattern occurs {n} times, "
                         f"want exactly 1:\n{old[:200]}")
    return text.replace(old, new)


# ------------------------------------------------------- the substitutions ---
GUARD_RS = "if k != EMPTY && nfill < TABCAP {"
NOGUARD_RS = "if k != EMPTY {"

PROBE_R2 = """            while tab[i] != EMPTY && tab[i] != k {
                i = (i + 1) % TABCAP;
            }"""
PROBE_R3 = """            while tab[i] != EMPTY && tab[i] != k {
                i = (i + 1) % TABCAP;
            }
            if tab[i] == EMPTY {
                tab[i] = k;
                nfill = nfill + 1;
            }
            acc = acc.wrapping_mul(31).wrapping_add(i as u64);"""
BOUNDED_R3 = """            let mut found: bool = false;
            let mut n: usize = 0;
            while n < TABCAP {
                if tab[i] == EMPTY || tab[i] == k {
                    found = true;
                    break;
                }
                i = (i + 1) % TABCAP;
                n = n + 1;
            }
            if found && tab[i] == EMPTY {
                tab[i] = k;
                nfill = nfill + 1;
            }
            acc = acc.wrapping_mul(31).wrapping_add(i as u64);"""

PROBE_R4 = """            while arr_get_unchecked(&tab, i) != EMPTY && arr_get_unchecked(&tab, i) != k {
                i = (i + 1) % TABCAP;
            }"""
PROBE_R4_ONECMP = """            loop {
                let s: u8 = arr_get_unchecked(&tab, i);
                if s == EMPTY || s == k {
                    break;
                }
                i = (i + 1) % TABCAP;
            }"""
STEP_R4 = "                i = (i + 1) % TABCAP;\n            }"
STEP_R4_NOMOD = """                i = i + 1;
                if i == TABCAP {
                    i = 0;
                }
            }"""

TAB_GET = "arr_get_unchecked(&tab, i)"
TAB_GET_CHECKED = "tab[i]"
TAB_SET = "arr_set_unchecked(&mut tab, i, k);"
TAB_SET_CHECKED = "tab[i] = k;"

# route (b): the exec-side probe counter. `../spec.md` FORBIDS `probes <
# TABCAP` in a rung; this is the control that prices what forbidding it buys.
R5_GHOST = """            let ghost e: int = choose|j: int| 0 <= j < TABCAP as int && tab@[j] == EMPTY;"""


def r2_noguard():
    return sub(open(R2).read(), GUARD_RS, NOGUARD_RS, "r2_noguard")


def r3_noguard():
    return sub(open(R3).read(), GUARD_RS, NOGUARD_RS, "r3_noguard")


def r4_noguard():
    return sub(open(R4).read(), GUARD_RS, NOGUARD_RS, "r4_noguard")


def r3_bounded():
    """R3 with a BOUNDED trip count instead of the capacity conjunct: the
    spelling a careful safe-Rust programmer writes. It terminates on a full
    table WITHOUT the guard -- and it is a DIFFERENT FUNCTION there (it finds a
    key that is present in a full table), measured: it disagrees with the
    shipped R3 on adversarial-full.bin and agrees on the other seven.

    ⚠ **It is out of contract, but NOT by a backticked `forbidden` entry.**
    ../spec.md forbids `for _ in 0..TABCAP` and `(0..TABCAP)` literally; the
    loop below is a while against its own counter and matches neither. What
    puts both bounded controls out of contract is `required` entry 3's prose,
    *no trip count anywhere*. TASK_070_REVIEW F3, and ../NOTES.md 0c."""
    s = sub(open(R3).read(), GUARD_RS, NOGUARD_RS, "r3_bounded guard")
    return sub(s, PROBE_R3, BOUNDED_R3, "r3_bounded probe")


def r3_bounded_kept():
    """The same bounded probe with the capacity conjunct KEPT, so the function
    is identical to the shipped R3 on every input and the Ir difference is
    purely the cost of the trip count.

    ⚠ **This control is why ../spec.md's `why` had to be SPLIT.** The single
    reason the contract used to give for excluding a bounded probe -- *it is a
    different function* -- is TRUE of `r3_bounded` and **FALSE of this one**,
    which agrees with the shipped R3 on all eight matrix inputs (this
    docstring said so from the start; TASK_070_REVIEW F3 measured it and found
    the contract contradicting it). It is excluded on IDIOM grounds instead,
    and it is 167.65 / 1235.96 Ir/call DEARER -- so the exclusion does not
    flatter. ../NOTES.md 8b publishes what admitting it would do to the span."""
    return sub(open(R3).read(), PROBE_R3, BOUNDED_R3, "r3_bounded_kept")


def r4_checked_tab():
    """R4 with the TABLE indexed checked (the window stays unchecked). Prices
    `arr_get_unchecked`/`arr_set_unchecked` on this pattern, where `i % TABCAP`
    may already have deleted rustc's check."""
    s = open(R4).read()
    s = s.replace(TAB_GET, TAB_GET_CHECKED)
    s = sub(s, TAB_SET, TAB_SET_CHECKED, "r4_checked_tab set")
    return s


def r4_onecmp():
    """R4 reading the slot ONCE per probe step instead of twice. An R4-side
    lever with no safety content at all."""
    return sub(open(R4).read(), PROBE_R4, PROBE_R4_ONECMP, "r4_onecmp")


def r4_nomod():
    """R4 with the probe step written `i + 1; if i == TABCAP { i = 0 }` instead
    of `% TABCAP`. Out of contract (../spec.md pins the `%` spelling) and
    measured anyway, because *"degenerate as far as this task searched"* has
    been false on four consecutive patterns."""
    return sub(open(R4).read(), STEP_R4, STEP_R4_NOMOD, "r4_nomod")


def r5_of(rs_transform, tag):
    """Apply the same exec-side substitution to verus.rs, so a candidate R4 can
    be put through Verus rather than assumed admissible (`.memory/01-ladder.md`:
    a rung covered by an `identity` pin is chained to the prover)."""
    s = open(R5).read()
    return rs_transform(s, tag)


def v_onecmp(s, tag):
    old = """            while arr_get_unchecked(&tab, i) != EMPTY && arr_get_unchecked(&tab, i) != k
                invariant"""
    new = """            loop
                invariant"""
    s = sub(s, old, new, tag + " head")
    old2 = """                decreases i0 as int + d - u,
            {
                i = (i + 1) % TABCAP;"""
    new2 = """                decreases i0 as int + d - u,
            {
                let s: u8 = arr_get_unchecked(&tab, i);
                if s == EMPTY || s == k {
                    break;
                }
                i = (i + 1) % TABCAP;"""
    return sub(s, old2, new2, tag + " body")


def v_nomod(s, tag):
    old = """            {
                i = (i + 1) % TABCAP;
                proof {
                    u = u + 1;
                }
            }"""
    new = """            {
                i = i + 1;
                if i == TABCAP {
                    i = 0;
                }
                proof {
                    u = u + 1;
                }
            }"""
    return sub(s, old, new, tag)


# ------------------------------------------------------------------- build ---
def build_rust(name, text, opt="3", mode="isolated"):
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(OUT, f"{name}.rs")
    open(src, "w").write(text)
    exe = os.path.join(OUT, f"{name}-O{opt}-{mode}")
    cmd = [RUSTC, "--edition", "2021", "-C", "codegen-units=1",
           "-C", f"opt-level={opt}", "-C", "debug-assertions=off"]
    if mode == "isolated":
        cmd += ["--cfg", "slb_isolated"]
    cmd += [src, "-o", exe]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"gen_controls.py: {name} failed:\n{r.stderr[-800:]}")
    return exe


def build_c_asan(name, src_path):
    os.makedirs(OUT, exist_ok=True)
    exe = os.path.join(OUT, name)
    cmd = [GCC, "-std=c99", "-Wall", "-Wextra", "-O1", "-g",
           "-fsanitize=address,undefined", "-static-libasan", "-static-libubsan",
           "-DSLB_ISOLATED", "-I", os.path.join(REPO, "common"),
           "-I", os.path.join(PDIR, "c"),
           os.path.join(REPO, "common", "driver.c"), src_path,
           os.path.join(PDIR, "c", "main.c"), "-o", exe]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"gen_controls.py: {name} failed:\n{r.stderr[-800:]}")
    return exe


def run(exe, blob, timeout=60):
    """ALWAYS with a timeout: several controls here never return."""
    try:
        r = subprocess.run([exe, os.path.join(INPUTS, blob)],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "", f"<timeout after {timeout}s>"
    return r.returncode, r.stdout.strip(), r.stderr.strip()[:200]


def probe_input(blob, n_iters):
    src = os.path.join(INPUTS, blob)
    out = os.path.join(OUT, f"probe-{n_iters}-{blob}")
    b = open(src, "rb").read()
    os.makedirs(OUT, exist_ok=True)
    open(out, "wb").write(struct.pack("<Q", n_iters) + b[8:])
    return out


def ir(exe, arg):
    o = os.path.join(OUT, "cg.out." + str(os.getpid()))
    r = subprocess.run([VALGRIND, "--tool=callgrind", f"--callgrind-out-file={o}",
                        exe, arg], capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        return None
    for line in open(o):
        if line.startswith(("summary:", "totals:")):
            return int(line.split()[1])
    return None


def marginal_ir(exe, blob, lo=100, hi=200):
    """Ir per kernel call, as a DIFFERENCE -- the per-process constant cancels
    (`.memory/03-measurement.md`). WHOLE-PROGRAM convention, named here so no
    figure derived from it is quoted as kernel-exclusive."""
    a, b = ir(exe, probe_input(blob, lo)), ir(exe, probe_input(blob, hi))
    return None if a is None or b is None else (b - a) / (hi - lo)


def kstat(exe):
    try:
        return asmmod.kernel(exe, "kernel")
    except KeyError:
        return None


# ⚠ **ALWAYS `--multiple-errors`.** `.memory/04-verus.md` 2b: Verus reports the
# FIRST failure per query by default -- and prints `not all errors may have been
# reported` when it does -- so a mutant that reports one error may be concealing
# others. p22's whole result is a claim about WHICH obligation fires, which is
# the case that file calls fatal, and TASK_070_REVIEW F2 measured that the
# default had hidden an error on two of the four failing mutants (m1 had three,
# not two; m3's FIRST error is the `decreases` and NOT an invariant). The flag
# is not optional here and is therefore a module constant, not a call site.
VERUS_FLAGS = ["--multiple-errors", "20"]


def verus(text, name, flags=VERUS_FLAGS):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"{name}.rs")
    open(p, "w").write(text)
    r = subprocess.run([sys.executable, VERUS_RUN, p] + list(flags),
                       capture_output=True, text=True, timeout=1800)
    txt = r.stdout + r.stderr
    out, want_site = [], False
    for l in txt.splitlines():
        s = l.strip()
        if "is not supported" in s or "verification results" in s:
            out.append(s[:160])
            want_site = False
        elif s.startswith("error:"):
            out.append(s[:160])
            # `aborting due to N previous errors` carries no site of its own
            want_site = not s.startswith("error: aborting")
        elif want_site and s.startswith("-->"):
            # THE SITE. Which obligation fired is the whole point of the flag,
            # so the location is reported next to the message rather than left
            # in a log nobody keeps.
            out.append("     " + s.replace(OUT + os.sep, "")[:160])
            want_site = False
    return out or ["(no verus output)"]


# ----------------------------------------------------------------- reports ---
def do_hang(want_miri):
    """The pattern's central control: the SAME omission in safe Rust."""
    print("\n== the omission, ported to safe Rust (r2_noguard) and to R3/R4 ==")
    print("   the shipped rungs differ from these by exactly "
          f"{GUARD_RS!r} -> {NOGUARD_RS!r}\n")
    for name, src in (("r2_noguard", r2_noguard()),
                      ("r3_noguard", r3_noguard()),
                      ("r4_noguard", r4_noguard())):
        for opt in ("0", "3"):
            exe = build_rust(name, src, opt=opt)
            for blob in ("small.bin", "adversarial-nearfull.bin",
                         "adversarial-full.bin"):
                rc, so, se = run(exe, blob, timeout=8)
                print(f"    {name:12s} -O{opt} {blob:26s} rc={rc} "
                      f"out={so!r} {se}")
    print("\n== the same omission in C, under ASan + UBSan ==")
    exe = build_c_asan("c_asan", CK)
    for blob in ("small.bin", "adversarial-nearfull.bin",
                 "adversarial-full.bin"):
        rc, so, se = run(exe, blob, timeout=15)
        print(f"    c_asan (gcc -O1 -fsanitize=address,undefined) {blob:26s} "
              f"rc={rc} out={so!r} stderr={se!r}")
    if want_miri:
        print("\n== Miri ==")
        for name, src in (("r2_noguard", r2_noguard()),):
            p = os.path.join(OUT, f"{name}.rs")
            open(p, "w").write(src)
            for blob in ("adversarial-nearfull.bin", "adversarial-full.bin"):
                b = probe_input(blob, 4)
                try:
                    r = subprocess.run(
                        [MIRI, "--sysroot", MIRI_SYSROOT, "--edition", "2021",
                         "-Zmiri-disable-isolation", p, "--", b],
                        capture_output=True, text=True, timeout=90)
                    ub = "Undefined Behavior" in r.stderr
                    print(f"    miri {name} {blob:26s} rc={r.returncode} "
                          f"UB={ub} out={r.stdout.strip()!r}")
                except subprocess.TimeoutExpired:
                    print(f"    miri {name} {blob:26s} DID NOT TERMINATE in 90s"
                          f" -- no diagnostic, no output")
        # The row the gate BLOCKS. unsafe.rs is the shipped R4 and it has the
        # guard, so Miri runs it fine on the declared-hang input; the block is
        # a consequence of the declaration being per-INPUT.
        for blob in ("adversarial-full.bin",):
            b = probe_input(blob, 4)
            try:
                r = subprocess.run(
                    [MIRI, "--sysroot", MIRI_SYSROOT, "--edition", "2021",
                     "-Zmiri-disable-isolation", R4, "--", b],
                    capture_output=True, text=True, timeout=180, cwd=PDIR)
                print(f"    miri SHIPPED unsafe.rs {blob:20s} rc={r.returncode} "
                      f"UB={'Undefined Behavior' in r.stderr} "
                      f"out={r.stdout.strip()!r}   <-- the row check.py BLOCKS")
            except subprocess.TimeoutExpired:
                print(f"    miri SHIPPED unsafe.rs {blob:20s} timed out")


def do_spread(want_ir, want_verus):
    print("\n== spelling spread (whole-program marginal Ir/call, isolated) ==")
    rows = [
        ("R3ship  ", R3, open(R3).read(), None),
        ("r3_bounded_kept", None, r3_bounded_kept(),
         "R3 + a bounded trip count, capacity conjunct KEPT: same function, "
         "so the delta is the price of the bound alone"),
        ("r3_bounded", None, r3_bounded(),
         "R3 with the bound INSTEAD of the conjunct: terminates, but a "
         "different function on a full table"),
        ("R4ship  ", R4, open(R4).read(), None),
        ("r4_checked_tab", None, r4_checked_tab(),
         "R4 with the TABLE indexed checked"),
        ("r4_onecmp", None, r4_onecmp(),
         "R4 reading the slot once per probe step instead of twice"),
        ("r4_nomod", None, r4_nomod(),
         "R4 with `i + 1; if i == TABCAP { i = 0 }` instead of `% TABCAP` "
         "(OUT OF CONTRACT -- spec.md pins the `%` spelling)"),
    ]
    print(f"{'spelling':16s} {'opt':4s} {'n_fn_nopad':>10s} {'md5_fn':34s} "
          f"{'small Ir/call':>13s} {'large Ir/call':>13s}")
    for name, path, src, why in rows:
        for opt in ("0", "3"):
            exe = build_rust(name.strip(), src, opt=opt)
            k = kstat(exe)
            ms = marginal_ir(exe, "small.bin") if want_ir else None
            ml = marginal_ir(exe, "large.bin") if want_ir else None
            print(f"{name:16s} O{opt:3s} "
                  f"{(k.n_fn_nopad if k else 0):10d} {(k.md5_fn if k else '-'):34s} "
                  f"{('%.4f' % ms) if ms is not None else '-':>13s} "
                  f"{('%.4f' % ml) if ml is not None else '-':>13s}")
        rc, so, _ = run(build_rust(name.strip(), src, opt="3"), "small.bin")
        print(f"                 small.bin checksum {so}   {why or ''}")
    if want_verus:
        print("\n== the R4-side candidates through Verus (`.memory/01-ladder.md`: "
              "a rung covered by an `identity` pin is chained to the prover) ==")
        for name, tf in (("v_onecmp", v_onecmp), ("v_nomod", v_nomod)):
            for line in verus(r5_of(tf, name), name):
                print(f"    {name:10s} {line}")


def do_routeb(want_ir, want_verus):
    """Route (b): what an EXEC-side probe counter would have cost."""
    print("\n== route (b): the exec-side probe counter ../spec.md forbids ==")
    s = open(R4).read()
    s = sub(s, """            let mut i: usize = (k as usize) * 2654435761 / 16777216 % TABCAP;""",
            """            let mut i: usize = (k as usize) * 2654435761 / 16777216 % TABCAP;
            let mut probes: usize = 0;""", "routeb init")
    s = sub(s, PROBE_R4,
            """            while probes < TABCAP && arr_get_unchecked(&tab, i) != EMPTY
                && arr_get_unchecked(&tab, i) != k {
                i = (i + 1) % TABCAP;
                probes = probes + 1;
            }""", "routeb loop")
    for opt in ("0", "3"):
        exe = build_rust("r4_execbound", s, opt=opt)
        k = kstat(exe)
        ms = marginal_ir(exe, "small.bin") if want_ir else None
        ml = marginal_ir(exe, "large.bin") if want_ir else None
        rc, so, _ = run(exe, "small.bin")
        print(f"    r4_execbound O{opt} n_fn_nopad={(k.n_fn_nopad if k else 0):5d} "
              f"md5_fn={(k.md5_fn if k else '-')} "
              f"small Ir/call={('%.4f' % ms) if ms is not None else '-':>10s} "
              f"large Ir/call={('%.4f' % ml) if ml is not None else '-':>10s} "
              f"checksum={so}")


def r4_reslice():
    """R4 with R3's ONE reslice added and nothing else changed: the window is
    bounds-checked once per call and the keys are still read through
    `buf_get_unchecked`. This is the MECHANISM control for `R3 - R4 = 2.00 flat`
    -- if the reslice is what the 2.00 is, this variant lands on R3's number."""
    s = open(R4).read()
    s = sub(s, """    let nkey: usize = buf_get_unchecked(buf, off) as usize
        + 256 * (buf_get_unchecked(buf, off + 1) as usize)
        + 65536 * (buf_get_unchecked(buf, off + 2) as usize)
        + 16777216 * (buf_get_unchecked(buf, off + 3) as usize);""",
            """    let w: &[u8] = &buf[off..off + len];
    let nkey: usize = buf_get_unchecked(w, 0) as usize
        + 256 * (buf_get_unchecked(w, 1) as usize)
        + 65536 * (buf_get_unchecked(w, 2) as usize)
        + 16777216 * (buf_get_unchecked(w, 3) as usize);""", "r4_reslice hdr")
    return sub(s, "        let k: u8 = buf_get_unchecked(buf, off + p);",
               "        let k: u8 = buf_get_unchecked(w, p);", "r4_reslice key")


# The GHOST side of `r4_reslice`. The exec code changes, so the loop invariant
# has to relate `w@` to `buf@.subrange(off, off+len)`; all three additions are
# ghost and erase, which is why the pair below is still byte-identical.
V_RESLICE_HDR_OLD = """    let nkey: usize = buf_get_unchecked(buf, off) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 2) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 3) as usize);"""
V_RESLICE_HDR_NEW = """    let w: &[u8] = &buf[off..off + len];
    assert(w@ =~= buf@.subrange(off as int, off + len as int));
    let nkey: usize = buf_get_unchecked(w, 0) as usize + 256 * (buf_get_unchecked(
        w,
        1,
    ) as usize) + 65536 * (buf_get_unchecked(w, 2) as usize) + 16777216 * (
    buf_get_unchecked(w, 3) as usize);"""
V_RESLICE_KEY_OLD = "        let k: u8 = buf_get_unchecked(buf, off + p);"
V_RESLICE_KEY_NEW = """        assert(w@[p as int] == buf@[off + p as int]);
        let k: u8 = buf_get_unchecked(w, p);"""
V_RESLICE_INV_OLD = """            buf@.len() <= usize::MAX,
            tab@.len() == TABCAP as int,"""
V_RESLICE_INV_NEW = """            buf@.len() <= usize::MAX,
            w@.len() == len,
            w@ =~= buf@.subrange(off as int, off + len as int),
            tab@.len() == TABCAP as int,"""


def r5_reslice():
    s = open(R5).read()
    s = sub(s, V_RESLICE_HDR_OLD, V_RESLICE_HDR_NEW, "r5_reslice hdr")
    s = sub(s, V_RESLICE_KEY_OLD, V_RESLICE_KEY_NEW, "r5_reslice key")
    return sub(s, V_RESLICE_INV_OLD, V_RESLICE_INV_NEW, "r5_reslice inv")


def build_verus(name, text, opt="3"):
    """Compile an R5 candidate with `harness/build.py`'s own verus flags, so the
    binary is comparable to a shipped cell."""
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(OUT, f"{name}.rs")
    open(src, "w").write(text)
    exe = os.path.join(OUT, f"{name}-O{opt}-isolated")
    cmd = [sys.executable, VERUS_RUN, "--compile", src, "-o", exe,
           "-C", "codegen-units=1", "-C", f"opt-level={opt}",
           "-C", "debug-assertions=off", "--cfg", "slb_isolated"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        raise SystemExit(f"gen_controls.py: {name} verus build failed:\n"
                         f"{(r.stdout + r.stderr)[-800:]}")
    return exe


def do_mech(want_ir):
    """Where `R3 - R4` comes from, measured rather than counted."""
    print("\n== mechanism: is `R3 - R4 = 2.00 flat` the RESLICE? ==")
    for name, src in (("R3ship", open(R3).read()),
                      ("R4ship", open(R4).read()),
                      ("r4_reslice", r4_reslice())):
        exe = build_rust(name, src, opt="3")
        k = kstat(exe)
        ms = marginal_ir(exe, "small.bin") if want_ir else None
        ml = marginal_ir(exe, "large.bin") if want_ir else None
        rc, so, _ = run(exe, "small.bin")
        print(f"    {name:12s} O3 n_fn_nopad={(k.n_fn_nopad if k else 0):4d} "
              f"md5_fn={(k.md5_fn if k else '-')} "
              f"small={('%.4f' % ms) if ms is not None else '-':>11s} "
              f"large={('%.4f' % ml) if ml is not None else '-':>11s} "
              f"cksum={so}")
    # ⚠ `r4_reslice` is an ADMISSIBLE R4 candidate, not just a mechanism probe,
    # so it is put through Verus AND its R4/R5 pair is built and diffed --
    # `.memory/01-ladder.md`: a rung covered by an `identity` pin is chained to
    # the prover, and "the ghost additions erase" is a claim about a BINARY.
    src5 = r5_reslice()
    print("    r4_reslice through Verus:")
    for line in verus(src5, "r5_reslice"):
        print(f"        {line}")
    a = build_rust("pair_r4", r4_reslice(), opt="3")
    b = build_verus("pair_r5", src5, opt="3")
    ka, kb = kstat(a), kstat(b)
    print(f"    r4_reslice R4/R5 pair at O3: md5_fn {ka.md5_fn} vs {kb.md5_fn} "
          f"-> {'IDENTICAL' if ka.md5_fn == kb.md5_fn else 'DIFFER'}; "
          f"md5_raw {'equal' if ka.md5_raw == kb.md5_raw else 'differ'}")


# The exec-side guard is GUARD_RS; the SPEC function `run` carries the same
# conjunct over `int`, and m6/m7 need both so the functional obligation stops
# being the thing that fails.
GUARD_SPEC = "if k != EMPTY && nfill < TABCAP as int {"
INV_NFILL_CAP = "            nfill <= TABCAP,\n"
LEMMA_CALL = """            proof {
                lemma_exists_empty(tab@);
            }
"""

# name -> ([(old, new), ...], why). ⚠ m1..m5 are ONE substitution each, which
# is what makes them readable without a diff. m6..m8 are the ISOLATION battery
# TASK_070_REVIEW F2 asked for and they need more than one by construction --
# each removes a *further* obligation in order to ask whether anything is left
# but termination. The answer is no, and ../NOTES.md 10 says why it cannot be.
PROOF_MUTANTS = {
    "m1_noguard": ([(GUARD_RS, NOGUARD_RS)],
                   "delete the capacity conjunct -- c/kernel.c's bug, in R5"),
    "m2_nodecreases": ([("                decreases i0 as int + d - u,\n", "")],
                       "delete the probe loop's `decreases` clause"),
    "m3_noempty": ([("                    tab@[e] == EMPTY,\n", "")],
                   "forget that the witness slot is EMPTY"),
    "m4_nofill": ([("            count_ne(tab@, TABCAP as int) == nfill as int,\n", "")],
                  "drop the fullness invariant, so `nfill` stops meaning "
                  "`the number of non-EMPTY slots`"),
    "m5_wronghash": ([("(k as int * 2654435761) / 16777216 % (TABCAP as int)",
                       "(k as int * 2654435761) / 16777216 % (TABCAP as int) + 0")],
                     "a NO-OP edit to the spec hash: the control that says the "
                     "battery is not just breaking the file"),
    "m6_specmatched": ([(GUARD_RS, NOGUARD_RS), (GUARD_SPEC, NOGUARD_RS)],
                       "m1 PLUS the same conjunct deleted from the SPEC fn "
                       "`run`, so the functional obligation becomes satisfiable "
                       "and cannot mask what else the conjunct was carrying"),
    "m7_isolate": ([(GUARD_RS, NOGUARD_RS), (GUARD_SPEC, NOGUARD_RS),
                    (INV_NFILL_CAP, "")],
                   "m6 PLUS the outer invariant `nfill <= TABCAP` deleted -- "
                   "the attempt to leave termination as the ONLY failure"),
    "m8_nolemma": ([(LEMMA_CALL, "")],
                   "delete the `lemma_exists_empty` CALL, keeping the guard: "
                   "the mechanism control for why deleting the guard can never "
                   "report `decreases not satisfied`"),
}


def do_mutants():
    print("\n== proof mutants (m1-m5 are ONE exact-string substitution of "
          "verus.rs each; m6-m8 are the isolation battery) ==")
    print("   ⚠ every run below is with --multiple-errors 20 "
          "(`.memory/04-verus.md` 2b): the DEFAULT reports only the first "
          "failure per query,\n     and on this pattern the claim IS which "
          "obligation fires. TASK_070_REVIEW F2.\n")
    base = open(R5).read()
    for name, (subs, why) in PROOF_MUTANTS.items():
        src = base
        for i, (old, new) in enumerate(subs):
            src = sub(src, old, new, f"{name}[{i}]")
        print(f"    {name:16s} {why}")
        for line in verus(src, name):
            print(f"        {line}")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", nargs="*", default=["all"])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--ir", action="store_true")
    ap.add_argument("--verus", action="store_true")
    ap.add_argument("--miri", action="store_true")
    a = ap.parse_args()
    groups = {"hang": lambda: do_hang(a.miri),
              "spread": lambda: do_spread(a.ir, a.verus),
              "routeb": lambda: do_routeb(a.ir, a.verus),
              "mech": lambda: do_mech(a.ir),
              "mutants": do_mutants}
    # Every control has a NAME as well as a group, and `--run <name>` works.
    # ⚠ Committed files cite controls by name -- c/kernel.c, safe_naive.rs,
    # safe_tuned.rs and model.py each say `--run <name>` -- and on p38 exactly
    # this drifted: three committed files cited a build called `s_asan_O3` that
    # `--list` did not ship (TASK_066_REVIEW m7). The alias table is what keeps
    # those citations executable, and `--list` prints it.
    alias = {
        "r2_noguard": "hang", "r3_noguard": "hang", "r4_noguard": "hang",
        "c_asan": "hang", "miri_full": "hang",
        "r3_bounded": "spread", "r3_bounded_kept": "spread",
        "r4_checked_tab": "spread", "r4_onecmp": "spread",
        "r4_nomod": "spread", "R2ship": "spread", "R3ship": "spread",
        "R4ship": "spread",
        "r4_execbound": "routeb",
        "r4_reslice": "mech",
    }
    alias.update({m: "mutants" for m in PROOF_MUTANTS})
    if a.list:
        print("groups:")
        for g in groups:
            print("   ", g)
        print("control names (each runs its whole group):")
        for n, g in sorted(alias.items()):
            print(f"    {n:18s} -> {g}")
        return 0
    want = []
    for g in (list(groups) if a.run == ["all"] else a.run):
        g = alias.get(g, g)
        if g not in groups:
            raise SystemExit(f"gen_controls.py: unknown group or control {g!r}; "
                             f"one of {sorted(groups)} or "
                             f"{sorted(alias)}")
        if g not in want:
            want.append(g)
    for g in want:
        groups[g]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
