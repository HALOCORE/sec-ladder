#!/usr/bin/env python3
"""p47's control variants: the in-contract R3 and R4 respellings, the `volatile`
control, the leaking-Rust control, and the proof mutants.

    python3 patterns/p47-ct-compare/controls/gen_controls.py            # write
    python3 patterns/p47-ct-compare/controls/gen_controls.py --build     # + build
    python3 patterns/p47-ct-compare/controls/gen_controls.py --verus     # + verify
    python3 patterns/p47-ct-compare/controls/gen_controls.py --list

Each variant is generated from a SHIPPED rung by exact-string substitution, so
"differs from the shipped cell in exactly this and nothing else" is a property
of this file rather than a claim about a hand-edit. Output goes to
`.temp/p47/ctl/` (sources) and `.temp/p47/ctlbin/` (binaries); both are
re-derivable and neither is committed (`.memory/00-environment.md` constraint 6).

WHAT ../spec.md's `idiom` BLOCK LEAVES FREE, and therefore what may vary:
the ADDRESSING of the two tags. It pins the comparison expression in every rung
(that is the security property), the window guard, the verdict fold, the cursor
advance and the header decode. It says in its `why` that addressing is the
SAFETY axis and is deliberately unpinned.

IN-CONTRACT R3 SPELLINGS -- `.memory/01-ladder.md` finding 3 asks every pattern
for at least two, and for the CHEAPEST FOUND to be quoted with the INPUT named:

    t_split     the two tag slices come from `split_at` rather than `&buf[a..b]`
                -- finding 3's two-step-reslice lever
    t_win       the WINDOW is resliced once, outside the loop, and the two tags
                are subslices of it, so the per-comparison index is `p` rather
                than `off + p`
    t_iter      the two tags are reached with `.iter().skip(..).take(..)`
                instead of a subslice, so there is no reslice bounds check at
                all in the loop -- the fold's operands are iterators either way

IN-CONTRACT R4 SPELLINGS -- `.memory/01-ladder.md` finding 14 and findings 18
and 19: **an unsearched R4 side has flattered the safe rung on two consecutive
patterns.** An R4 candidate is NOT a rung unless a byte-identical R5 twin
VERIFIES at the pinned vstd (`.tasks/TASK_026.md` §0 item 3), so every one of
these is put through `./verus_run.py` and the ERROR TEXT is read rather than the
exit code.

    u_base      hoist `off + p` and `off + p + tlen` into two loop-invariant
                bases, so the tag loop indexes `ba + i` and `bb + i` rather
                than `off + p + i` and `off + p + tlen + i`. THE ONE INSTRUCTION
                the shipped R4 pays over R3 is a second induction variable, so
                this is the lever aimed at it.
    u_win       reslice the window once and `get_unchecked` INTO the window
    u_ptr       raw pointers (`buf.as_ptr().add(..)`) -- expected `is not
                supported` at the pinned vstd, and reported as a clean negative

THE `volatile` CONTROL, which is the reason ../spec.md forbids it:

    h_vol       c/kernel_hardened.c with `uint8_t d` -> `volatile uint8_t d`.
                Same semantics, same verdicts, and the received advice for this
                idiom. Measured cost in ../NOTES.md 8c.

THE LEAKING-RUST CONTROL:

    n_early     safe_naive with `a == b` replaced by a hand-written early-exit
                loop, so the leak can be priced at BYTE granularity rather than
                glibc's 32-byte one. Out of contract (the comparison expression
                is pinned) and priced anyway, because the price of a declaration
                is what it excludes.

MUTANTS -- ../NOTES.md 10:

    m_noguard   verus.rs with the window guard `len - p >= 2 * tlen` deleted.
                MUST fail to verify.
    m_hdr       verus.rs with the tag loop's read shifted by one byte
                (`off + p + tlen + i` -> `off + p + tlen + i + 1`).
                MUST fail to verify, on the trusted accessor's `requires`.
    m_leak      ⚠ **THE MUTANT THAT MUST *PASS*.** verus.rs with the
                constant-time tag loop replaced by an early-exiting one that
                computes the same verdict. It is `c/kernel.c`'s bug, promoted
                into the proved rung. **Verus verifies it**, at the same
                obligation count, against the same `ensures` -- which is p47's
                whole result and the one place in this tree where a mutant
                passing is the deliverable. `--build` COMPILES IT (see
                `VERUS_BUILD`), because ../NOTES.md 6 publishes an Ir figure
                measured on its object and a published blob owes a generator.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p47", "ctl")
BIN = os.path.join(REPO, ".temp", "p47", "ctlbin")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")
GCC = "/usr/bin/gcc"
VERUS = os.path.join(REPO, "verus_run.py")

TUNED = os.path.join(PDIR, "safe_tuned.rs")
NAIVE = os.path.join(PDIR, "safe_naive.rs")
UNSAFE = os.path.join(PDIR, "unsafe.rs")
VERUS_RS = os.path.join(PDIR, "verus.rs")
HARD_C = os.path.join(PDIR, "c", "kernel_hardened.c")

SHIP_TAGS_TUNED = """        let a: &[u8] = &buf[off + p..off + p + tlen];
        let b: &[u8] = &buf[off + p + tlen..off + p + 2 * tlen];"""
SHIP_TAGS_NAIVE = SHIP_TAGS_TUNED
SHIP_FOLD = ("        let d: u8 = a.iter().zip(b.iter())"
             ".fold(0u8, |acc, (x, y)| acc | (x ^ y));")
SHIP_U4 = """        let mut d: u8 = 0;
        let mut i: usize = 0;
        while i < tlen {
            d = d
                | (unsafe { *buf.get_unchecked(off + p + i) }
                    ^ unsafe { *buf.get_unchecked(off + p + tlen + i) });
            i = i + 1;
        }"""
SHIP_V5 = """        let mut d: u8 = 0;
        let mut i: usize = 0;"""

#: `verus`-kind variants whose BINARY is measured, and therefore whose binary
#: `--build` must produce. ⚠ **This set exists because TASK_064_REVIEW major 1
#: found `--build` skipping every `verus` variant**, which left `m_leak`'s
#: binary -- the object ../NOTES.md 6 and ../README.md quote `+7088.000` from --
#: with **no generator**, in violation of `CLAUDE.md` "Don't" #1 (*if a blob has
#: no script that rebuilds it, write one before finishing*).
#:
#: It is a NAMED SET rather than "all of them" for two measured reasons, and
#: `build()` prints the reason for every variant it skips so the skip is visible
#: rather than silent:
#:   * `m_noguard` and `m_hdr` MUST FAIL to verify (that is their job), and
#:     `verus_run.py --compile` refuses to emit an object for a file that does
#:     not verify -- so a binary for them cannot exist and is not wanted;
#:   * `u_*_verus` are the byte-identical R5 TWINS of the `u_*` Rust variants.
#:     Their job is to answer *does this R4 candidate have a verifying twin?*,
#:     which `--verus` does; the Ir figures in ../NOTES.md 8e come from the
#:     `u_*` builds, which `--build` already produces in both inline modes.
VERUS_BUILD = {"m_leak"}

# (name, source rung, [(find, replace), ...], kind)  kind: rs | verus | c
VARIANTS = [
    # ---------------- in-contract R3 spellings --------------------------
    ("t_split", TUNED, [(SHIP_TAGS_TUNED, """        let a: &[u8] = buf.split_at(off + p).1.split_at(tlen).0;
        let b: &[u8] = buf.split_at(off + p + tlen).1.split_at(tlen).0;""")],
     "rs"),
    ("t_win", TUNED, [
        ("    let mut acc: u64 = 0;\n    let mut p: usize = 8;",
         "    let w: &[u8] = &buf[off..off + len];\n"
         "    let mut acc: u64 = 0;\n    let mut p: usize = 8;"),
        (SHIP_TAGS_TUNED, """        let a: &[u8] = &w[p..p + tlen];
        let b: &[u8] = &w[p + tlen..p + 2 * tlen];""")], "rs"),
    ("t_iter", TUNED, [
        (SHIP_TAGS_TUNED + "\n" + SHIP_FOLD,
         """        let d: u8 = buf.iter().skip(off + p).take(tlen)
            .zip(buf.iter().skip(off + p + tlen).take(tlen))
            .fold(0u8, |acc, (x, y)| acc | (x ^ y));""")], "rs"),
    # ---------------- in-contract R4 spellings --------------------------
    ("u_base", UNSAFE, [(SHIP_U4, """        let ba: usize = off + p;
        let bb: usize = off + p + tlen;
        let mut d: u8 = 0;
        let mut i: usize = 0;
        while i < tlen {
            d = d
                | (unsafe { *buf.get_unchecked(ba + i) }
                    ^ unsafe { *buf.get_unchecked(bb + i) });
            i = i + 1;
        }""")], "rs"),
    ("u_win", UNSAFE, [
        ("    let mut acc: u64 = 0;\n    let mut p: usize = 8;",
         "    let w: &[u8] = buf.split_at(off).1.split_at(len).0;\n"
         "    let mut acc: u64 = 0;\n    let mut p: usize = 8;"),
        (SHIP_U4, """        let mut d: u8 = 0;
        let mut i: usize = 0;
        while i < tlen {
            d = d
                | (unsafe { *w.get_unchecked(p + i) }
                    ^ unsafe { *w.get_unchecked(p + tlen + i) });
            i = i + 1;
        }""")], "rs"),
    ("u_ptr", UNSAFE, [(SHIP_U4, """        let mut d: u8 = 0;
        let mut i: usize = 0;
        let pa = unsafe { buf.as_ptr().add(off + p) };
        let pb = unsafe { buf.as_ptr().add(off + p + tlen) };
        while i < tlen {
            d = d | unsafe { *pa.add(i) ^ *pb.add(i) };
            i = i + 1;
        }""")], "rs"),
    ("u_winu", UNSAFE, [
        ("    let mut acc: u64 = 0;\n    let mut p: usize = 8;",
         "    let w: &[u8] = unsafe { buf.get_unchecked(off..off + len) };\n"
         "    let mut acc: u64 = 0;\n    let mut p: usize = 8;"),
        (SHIP_U4, """        let mut d: u8 = 0;
        let mut i: usize = 0;
        while i < tlen {
            d = d
                | (unsafe { *w.get_unchecked(p + i) }
                    ^ unsafe { *w.get_unchecked(p + tlen + i) });
            i = i + 1;
        }""")], "rs"),
    ("u_end", UNSAFE, [(SHIP_U4, """        let ba: usize = off + p;
        let ea: usize = off + p + tlen;
        let mut d: u8 = 0;
        let mut i: usize = ba;
        while i < ea {
            d = d
                | (unsafe { *buf.get_unchecked(i) }
                    ^ unsafe { *buf.get_unchecked(i + tlen) });
            i = i + 1;
        }""")], "rs"),
    # ---------------- the `volatile` control ----------------------------
    ("h_vol", HARD_C, [("    uint8_t d;", "    volatile uint8_t d;")], "c"),
    # ---------------- the leaking-Rust control --------------------------
    ("n_early", NAIVE, [
        (SHIP_TAGS_NAIVE + """
        acc = if a == b {""",
         SHIP_TAGS_NAIVE + """
        let mut eq: bool = true;
        let mut i: usize = 0;
        while i < tlen {
            if a[i] != b[i] {
                eq = false;
                break;
            }
            i = i + 1;
        }
        acc = if eq {""")], "rs"),
    # ---------------- R4-side twins (must verify to be rungs) -----------
    ("u_base_verus", VERUS_RS, [
        ("""        let mut d: u8 = 0;
        let mut i: usize = 0;""",
         """        let ba: usize = off + p;
        let bb: usize = off + p + tlen;
        let mut d: u8 = 0;
        let mut i: usize = 0;"""),
        ("""            d = d | (buf_get_unchecked(buf, off + p + i) ^ buf_get_unchecked(
                buf,
                off + p + tlen + i,
            ));""",
         """            d = d | (buf_get_unchecked(buf, ba + i) ^ buf_get_unchecked(
                buf,
                bb + i,
            ));"""),
        ("""                i <= tlen,
                o < ntag,""",
         """                i <= tlen,
                ba == off + p,
                bb == off + p + tlen,
                o < ntag,""")], "verus"),
    ("u_ptr_verus", VERUS_RS, [
        ("""            d = d | (buf_get_unchecked(buf, off + p + i) ^ buf_get_unchecked(
                buf,
                off + p + tlen + i,
            ));""",
         """            d = d | unsafe { *buf.as_ptr().add(off + p + i)
                ^ *buf.as_ptr().add(off + p + tlen + i) };""")], "verus"),
    ("u_win_verus", VERUS_RS, [
        ("    let mut acc: u64 = 0;\n    let mut p: usize = 8;",
         "    let w: &[u8] = buf.split_at(off).1.split_at(len).0;\n"
         "    assert(w@ == buf@.subrange(off as int, off + len as int));\n"
         "    let mut acc: u64 = 0;\n    let mut p: usize = 8;"),
        ("""            d = d | (buf_get_unchecked(buf, off + p + i) ^ buf_get_unchecked(
                buf,
                off + p + tlen + i,
            ));""",
         """            d = d | (buf_get_unchecked(w, p + i) ^ buf_get_unchecked(
                w,
                p + tlen + i,
            ));"""),
        # THE CLAUSE THAT CLOSES IT, in BOTH loops. p10's `u_win_verus` needed
        # exactly this and TASK_057 shipped `w@.len() == len` instead, which
        # constrains the window's LENGTH and never relates its CONTENTS to
        # `buf@` -- so the `xacc` invariant, written over `buf@`, has nothing to
        # rewrite `w@[k]` into. vstd ships a spec for `<[T]>::split_at`
        # (~/tools/verus/vstd/std_specs/slice.rs) giving the subrange directly.
        ("""            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            twalk(""",
         """            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            w@ == buf@.subrange(off as int, off + len as int),
            twalk("""),
        ("""                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                xacc(""",
         """                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                w@ == buf@.subrange(off as int, off + len as int),
                xacc(""")], "verus"),
    ("u_end_verus", VERUS_RS, [
        ("""        let mut d: u8 = 0;
        let mut i: usize = 0;""",
         """        let ba: usize = off + p;
        let ea: usize = off + p + tlen;
        let mut d: u8 = 0;
        let mut i: usize = ba;"""),
        ("        while i < tlen\n            invariant\n                i <= tlen,",
         "        while i < ea\n            invariant\n                ba <= i <= ea,\n"
         "                ba == off + p,\n                ea == off + p + tlen,"),
        ("""            d = d | (buf_get_unchecked(buf, off + p + i) ^ buf_get_unchecked(
                buf,
                off + p + tlen + i,
            ));""",
         """            d = d | (buf_get_unchecked(buf, i) ^ buf_get_unchecked(
                buf,
                i + tlen,
            ));"""),
        ("""                xacc(buf@, (off + p) as int, tlen as int, i as int, d) == xacc(""",
         """                xacc(buf@, (off + p) as int, tlen as int, i as int - ba as int, d) == xacc("""),
        ("            decreases tlen - i,\n        {", "            decreases ea - i,\n        {"),
    ], "verus"),
    ("u_winu_verus", VERUS_RS, [
        ("    let mut acc: u64 = 0;\n    let mut p: usize = 8;",
         "    let w: &[u8] = slice_unchecked(buf, off, len);\n"
         "    let mut acc: u64 = 0;\n    let mut p: usize = 8;"),
        ("""            d = d | (buf_get_unchecked(buf, off + p + i) ^ buf_get_unchecked(
                buf,
                off + p + tlen + i,
            ));""",
         """            d = d | (buf_get_unchecked(w, p + i) ^ buf_get_unchecked(
                w,
                p + tlen + i,
            ));"""),
        ("""            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            twalk(""",
         """            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            w@ == buf@.subrange(off as int, off + len as int),
            twalk("""),
        ("""                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                xacc(""",
         """                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                w@ == buf@.subrange(off as int, off + len as int),
                xacc("""),
        # A FOURTH TRUSTED ITEM would be needed for this one -- that is the
        # point of building it. vstd ships no spec for `<[T]>::get_unchecked`
        # on a Range, so the panic-pad-free window reslice costs a new axiom.
        ("#[inline(always)]\n#[verifier::external_body]\nfn buf_get_unchecked",
         """#[inline(always)]
#[verifier::external_body]
fn slice_unchecked(v: &[u8], off: usize, len: usize) -> (r: &[u8])
    requires
        off + len <= v@.len(),
    ensures
        r@ == v@.subrange(off as int, off + len as int),
{
    unsafe { v.get_unchecked(off..off + len) }
}

#[inline(always)]
#[verifier::external_body]
fn buf_get_unchecked"""),
    ], "verus"),
    # ---------------- mutants that MUST fail ----------------------------
    ("m_noguard", VERUS_RS, [
        ("    while o < ntag && len - p >= 2 * tlen",
         "    while o < ntag")], "verus"),
    ("m_hdr", VERUS_RS, [
        ("""            d = d | (buf_get_unchecked(buf, off + p + i) ^ buf_get_unchecked(
                buf,
                off + p + tlen + i,
            ));""",
         """            d = d | (buf_get_unchecked(buf, off + p + i) ^ buf_get_unchecked(
                buf,
                off + p + tlen + i + 1,
            ));""")], "verus"),
    # ---------------- THE MUTANT THAT MUST PASS -------------------------
    ("m_leak", VERUS_RS, [
        # (1) the early exit itself: stop as soon as the accumulator is
        #     non-zero. This IS `c/kernel.c`'s bug, in the proved rung.
        ("        while i < tlen\n            invariant",
         "        while i < tlen && d == 0\n            invariant"),
        # (2) the base-case assert has to split on WHY the loop stopped.
        ("""        // Ghost only: `i == tlen`, so `xacc` at `i` is its own base case, and
        // the loop invariant therefore identifies `d` with the spec's verdict.
        assert(xacc(buf@, (off + p) as int, tlen as int, tlen as int, d) == d);""",
         """        // The loop now stops for EITHER reason, so the base case splits.
        proof {
            if d == 0 {
                assert(xacc(buf@, (off + p) as int, tlen as int, tlen as int, d) == d);
            } else {
                lemma_xacc_sticky(buf@, (off + p) as int, tlen as int, i as int, d);
            }
        }
        assert(d == 0 <==> xacc(buf@, (off + p) as int, tlen as int, 0, 0) == 0);"""),
        # (3) the sticky lemma: once `d` is non-zero it stays non-zero, so the
        #     early exit computes the same VERDICT as the full fold. Pure ghost.
        ("/// THE MACHINE: comparisons `o .. ntag`",
         """/// Once `d` is non-zero it stays non-zero, so an early exit computes the same
/// VERDICT as the full fold. **This lemma is the whole of what makes the
/// LEAKING implementation satisfy the CONSTANT-TIME specification**, and it is
/// why no strengthening of the `ensures` can exclude the leak: the two programs
/// are the same function.
pub proof fn lemma_xacc_sticky(buf: Seq<u8>, base: int, tlen: int, i: int, d: u8)
    requires
        d != 0,
    ensures
        xacc(buf, base, tlen, i, d) != 0,
    decreases tlen - i,
{
    if i >= tlen {
    } else {
        let x: u8 = buf[base + i] ^ buf[base + tlen + i];
        assert(d | x != 0) by (bit_vector)
            requires
                d != 0,
        ;
        lemma_xacc_sticky(buf, base, tlen, i + 1, d | x);
    }
}

/// THE MACHINE: comparisons `o .. ntag`""")], "verus"),
]


def write():
    os.makedirs(OUT, exist_ok=True)
    made = []
    for name, src, subs, kind in VARIANTS:
        txt = open(src).read()
        for find, rep in subs:
            if find not in txt:
                raise SystemExit(f"gen_controls.py: {name}: substitution not "
                                 f"found in {os.path.basename(src)}:\n"
                                 f"{find[:200]}")
            txt = txt.replace(find, rep, 1)
        ext = ".c" if kind == "c" else ".rs"
        p = os.path.join(OUT, name + ext)
        open(p, "w").write(txt)
        made.append((name, p, kind, os.path.basename(src)))
    return made


def build(made):
    os.makedirs(BIN, exist_ok=True)
    common = os.path.join(REPO, "common")
    cdir = os.path.join(PDIR, "c")
    lld = os.path.expanduser("~/tools/llvm/bin/ld.lld")
    for name, p, kind, _src in made:
        if kind == "verus":
            # THE BRANCH TASK_064_REVIEW major 1 FOUND MISSING. The flags below
            # are `harness/build.py::build_verus` + `rust_flags` verbatim for
            # (O3, <mode>, unwind), minus `--edition`, which Verus fixes itself
            # -- so a control binary is built the same way the shipped `verus`
            # cell is and the two are comparable.
            if name not in VERUS_BUILD:
                print(f"  --   {name:14s} verus-kind, no binary wanted "
                      f"(see VERUS_BUILD)")
                continue
            for mode in ("isolated", "whole"):
                out = os.path.join(BIN, f"{name}-O3-{mode}")
                cmd = [sys.executable, VERUS, "--compile", p, "-o", out,
                       "-C", "codegen-units=1", "-C", "opt-level=3",
                       "-C", "debug-assertions=off"]
                if mode == "isolated":
                    cmd += ["--cfg", "slb_isolated"]
                r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
                ok = r.returncode == 0 and os.path.exists(out)
                vr = [ln for ln in (r.stdout + r.stderr).splitlines()
                      if "verification results" in ln]
                print(f"  {'ok ' if ok else 'FAIL'} "
                      f"{name:14s} {mode:9s} {out}"
                      + (f"   [{vr[0].strip()}]" if vr else ""))
                if not ok:
                    print((r.stdout + r.stderr)[-800:])
            continue
        if kind == "c":
            # BOTH inline modes, mirroring harness/build.py::c_flags: isolated
            # is -DSLB_ISOLATED and whole is -flto (+ lld under clang). Before
            # TASK_065 only `isolated` was built, and ir_table.py::binary()
            # silently served the isolated object under `--mode whole`.
            for cc, tag in ((GCC, "gcc"), (CLANG, "clang")):
                for mode in ("isolated", "whole"):
                    out = os.path.join(BIN, f"{name}-{tag}-O3-{mode}")
                    cmd = [cc, "-std=c99", "-O3", "-Wall", "-Wextra"]
                    if mode == "isolated":
                        cmd.append("-DSLB_ISOLATED")
                    else:
                        cmd.append("-flto")
                        if tag == "clang" and os.path.exists(lld):
                            cmd.append("-fuse-ld=lld")
                    cmd += ["-I", common, "-I", cdir,
                            os.path.join(common, "driver.c"), p,
                            os.path.join(cdir, "main.c"), "-o", out]
                    r = subprocess.run(cmd, capture_output=True, text=True,
                                       cwd=REPO)
                    print(f"  {'ok ' if r.returncode == 0 else 'FAIL'} "
                          f"{name}-{tag:6s} {mode:9s} {out}")
                    if r.returncode:
                        print((r.stdout + r.stderr)[-800:])
            continue
        for mode in ("isolated", "whole"):
            out = os.path.join(BIN, f"{name}-O3-{mode}")
            cmd = [RUSTC, "--edition", "2021", "-C", "codegen-units=1",
                   "-C", "opt-level=3", "-C", "debug-assertions=off"]
            if mode == "isolated":
                cmd += ["--cfg", "slb_isolated"]
            cmd += [p, "-o", out]
            r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
            print(f"  {'ok ' if r.returncode == 0 else 'FAIL'} "
                  f"{name:14s} {mode:9s} {out}")
            if r.returncode:
                print((r.stdout + r.stderr)[-800:])


def verus(made, only=None):
    for name, p, kind, _src in made:
        if kind != "verus" or (only and name not in only):
            continue
        r = subprocess.run([sys.executable, VERUS, p], capture_output=True,
                           text=True, cwd=REPO)
        txt = r.stdout + r.stderr
        tail = [ln for ln in txt.splitlines()
                if "verification results" in ln or ln.startswith("error")
                or "is not supported" in ln]
        print(f"  {name:14s} rc={r.returncode}  " + " | ".join(tail[:4]))


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--verus", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        for name, src, _s, k in VARIANTS:
            print(f"  {name:14s} from {os.path.basename(src):20s} ({k})")
        return 0
    made = write()
    print(f"wrote {len(made)} variant(s) to {OUT}")
    if a.build:
        build(made)
    if a.verus:
        verus(made, set(a.only.split(",")) if a.only else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
