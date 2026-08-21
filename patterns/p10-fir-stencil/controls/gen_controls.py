#!/usr/bin/env python3
"""p10's control variants: the in-contract R3 and R4 respellings, and the
proof/behaviour mutants.

    python3 patterns/p10-fir-stencil/controls/gen_controls.py            # write
    python3 patterns/p10-fir-stencil/controls/gen_controls.py --build     # + build
    python3 patterns/p10-fir-stencil/controls/gen_controls.py --list

Each variant is generated from a SHIPPED rung by exact-string substitution, so
"differs from the shipped cell in exactly this and nothing else" is a property
of this file rather than a claim about a hand-edit. Output goes to
`.temp/p10/ctl/` (sources) and `.temp/p10/ctlbin/` (binaries); both are
re-derivable and neither is committed, which is `.memory/00-environment.md`
constraint 6.

IN-CONTRACT R3 SPELLINGS -- `.memory/01-ladder.md` finding 3 asks every pattern
for at least two, and for the CHEAPER to be quoted with the input named. What
../spec.md's `idiom` block leaves free on R3 is the WINDOW RESLICE (named
nowhere) and the SPELLING OF THE TAP LOOP (deliberately, since comparing tap-loop
spellings is what p10 is for):

    t_winidx    the tap loop INDEXES the window `windows()` already handed it
                (`win[j] * coef[j]`) instead of zipping two iterators
    t_1step     the window reslice is the ONE-STEP `&buf[off..off + len]`
                instead of the shipped two-step `split_at`.
                **This is `.memory/01-ladder.md` finding 3's two-step reslice
                lever, backlog priority 1, worth -1.00 Ir/call on six patterns.**
                p10's R3 opens with a window reslice, which is why the task
                asked for it here; the measurement is in ../NOTES.md 8d either
                way, and a clean negative retires the item.
    t_fold      the tap loop is `.fold()` rather than a `for` with a mutable
                accumulator

OUT OF CONTRACT, priced anyway because the price of a declaration is what it
excludes:

    x_chunks    `coef.chunks_exact(1)`-driven -- FORBIDDEN (`chunks_exact`)
    x_sum       `.map(..).sum()` -- FORBIDDEN (`.sum(`)

R4-SIDE LEVERS -- `.memory/01-ladder.md` finding 14: an R4 candidate is not a
rung unless a byte-identical R5 twin VERIFIES at the pinned vstd, so every one
of these is run through `./verus_run.py` before its number is quoted, and the
ERROR TEXT is read rather than the exit code.

    u_win       reslice the window once, then `get_unchecked` INTO THE WINDOW,
                so the per-tap index is `sb + i + j` rather than
                `off + sb + i + j`. 3397.00 / 8349.00 Ir/call against R4ship's
                3591.00 / 8711.00 at `-O3 isolated`.
                ⚠ **Its twin VERIFIES -- 10 verified, 0 errors, the same
                obligation count as the shipped `verus.rs`, no new trusted item
                and no lemma.** TASK_057 reported that it does not and called
                the R4 side degenerate; that is retracted at ../NOTES.md 8e and
                14, and 60% of p10's published margin was R4 spelling. What
                excludes `u_win` from shipping is the IDENTITY PIN and not the
                proof: its surviving `split_at` panic pad holds a pc-relative
                `&core::panic::Location`, so the pair is `norel` and not
                `exact`. ../NOTES.md 8e2 has the general consequence, which
                bounds the R4 search space of every pattern here.

MUTANTS -- ../NOTES.md 10:

    m_fence     verus.rs with `last >= len` weakened to `last > len`: the C
                bug, in the proof. MUST fail to verify.
    m_fence3    m_fence AND BOTH copies of the loop invariant
                `8 + taps + n - 1 < len` weakened to `<=`, so that the
                rejection cannot land on an invariant and has to land on the
                TRUSTED ACCESSOR's `requires i < v@.len()` -- which is the
                obligation the pattern is about. Reported because m_fence alone
                fails one level too early to prove that, and because weakening
                only ONE of the two copies (tried, and recorded in ../NOTES.md
                10) still lands on the other.
    m_nowin     verus.rs with the window guard `n < taps` deleted. MUST fail.
    u_win_verus the R5 twin of `u_win`; an R4 candidate is not a rung until
                this verifies (`.memory/01-ladder.md` finding 14). **It does:
                10 verified, 0 errors.** The closing repair is ONE invariant
                clause, `w@ == buf@.subrange(off as int, off + len as int)`, in
                BOTH loops -- vstd's `<[T]>::split_at` spec gives the subrange
                directly. Both clauses are load-bearing and the accompanying
                `assert` is dead; `.temp/p10c/minimality.py` derives the three
                probes that show it. TASK_057's repair round added
                `w@.len() == len`, which constrains the window's LENGTH and
                never relates its CONTENTS to `buf@`, so the `dotp` invariant --
                written over `buf@` -- could not close.
    b_fence     unsafe.rs with `last >= len` weakened to `last > len`: the C
                bug promoted into a Rust rung with no bounds check. MUST be
                caught by Miri.
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p10", "ctl")
BIN = os.path.join(REPO, ".temp", "p10", "ctlbin")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VERUS = os.path.join(REPO, "verus_run.py")

TUNED = os.path.join(PDIR, "safe_tuned.rs")
NAIVE = os.path.join(PDIR, "safe_naive.rs")
UNSAFE = os.path.join(PDIR, "unsafe.rs")
VERUS_RS = os.path.join(PDIR, "verus.rs")

# Each entry: (name, source rung, [(find, replace), ...], verus?)
VARIANTS = [
    ("t_winidx", TUNED, [(
        """        for (a, b) in win.iter().zip(coef.iter()) {
            s = s.wrapping_add((*a as u32).wrapping_mul(*b as u32));
        }""",
        """        let mut j: usize = 0;
        while j < taps {
            s = s.wrapping_add((win[j] as u32).wrapping_mul(coef[j] as u32));
            j = j + 1;
        }""")], False),
    ("t_1step", TUNED, [(
        "    let w: &[u8] = buf.split_at(off).1.split_at(len).0;",
        "    let w: &[u8] = &buf[off..off + len];")], False),
    ("t_fold", TUNED, [(
        """        let mut s: u32 = 0;
        for (a, b) in win.iter().zip(coef.iter()) {
            s = s.wrapping_add((*a as u32).wrapping_mul(*b as u32));
        }""",
        """        let s: u32 = win.iter().zip(coef.iter()).fold(0u32, |q, (a, b)| {
            q.wrapping_add((*a as u32).wrapping_mul(*b as u32))
        });""")], False),
    ("x_sum", TUNED, [(
        """        let mut s: u32 = 0;
        for (a, b) in win.iter().zip(coef.iter()) {
            s = s.wrapping_add((*a as u32).wrapping_mul(*b as u32));
        }""",
        """        let s: u32 = win.iter().zip(coef.iter())
            .map(|(a, b)| (*a as u32).wrapping_mul(*b as u32)).sum();""")], False),
    ("n_2step", NAIVE, [(
        """    let n: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);
    let r: usize = buf[off + 4] as usize + 256 * (buf[off + 5] as usize)
        + 65536 * (buf[off + 6] as usize) + 16777216 * (buf[off + 7] as usize);""",
        """    let w: &[u8] = buf.split_at(off).1.split_at(len).0;
    let n: usize = w[0] as usize + 256 * (w[1] as usize)
        + 65536 * (w[2] as usize) + 16777216 * (w[3] as usize);
    let r: usize = w[4] as usize + 256 * (w[5] as usize)
        + 65536 * (w[6] as usize) + 16777216 * (w[7] as usize);"""),
        ("""                (buf[off + sb + i + j] as u32).wrapping_mul(buf[off + 8 + j] as u32));""",
         """                (w[sb + i + j] as u32).wrapping_mul(w[8 + j] as u32));""")], False),
    ("u_win", UNSAFE, [(
        """            s = s.wrapping_add(
                (unsafe { *buf.get_unchecked(off + sb + i + j) } as u32)
                    .wrapping_mul(unsafe { *buf.get_unchecked(off + 8 + j) } as u32));""",
        """            s = s.wrapping_add(
                (unsafe { *w.get_unchecked(sb + i + j) } as u32)
                    .wrapping_mul(unsafe { *w.get_unchecked(8 + j) } as u32));"""),
        ("""    let nout: usize = n - 2 * r;
    let sb: usize = 8 + taps;""",
         """    let nout: usize = n - 2 * r;
    let sb: usize = 8 + taps;
    let w: &[u8] = buf.split_at(off).1.split_at(len).0;""")], False),
    ("b_fence", UNSAFE, [("    if last >= len {", "    if last > len {")], False),
    ("m_fence", VERUS_RS, [("    if last >= len {", "    if last > len {")], True),
    ("m_fence3", VERUS_RS, [("    if last >= len {", "    if last > len {"),
                            ("8 + taps + n - 1 < len,",
                             "8 + taps + n - 1 <= len,")], True),
    ("u_win_verus", VERUS_RS, [(
        """            s = s.wrapping_add(
                (buf_get_unchecked(buf, off + sb + i + j) as u32).wrapping_mul(
                    buf_get_unchecked(buf, off + 8 + j) as u32,
                ),
            );""",
        """            s = s.wrapping_add(
                (buf_get_unchecked(w, sb + i + j) as u32).wrapping_mul(
                    buf_get_unchecked(w, 8 + j) as u32,
                ),
            );"""),
        ("""    let nout: usize = n - 2 * r;
    let sb: usize = 8 + taps;""",
         """    let nout: usize = n - 2 * r;
    let sb: usize = 8 + taps;
    let w: &[u8] = buf.split_at(off).1.split_at(len).0;
    assert(w@ == buf@.subrange(off as int, off + len as int));"""),
        # THE CLAUSE THAT CLOSES IT, and the whole of TASK_057_REVIEW's B1.
        # TASK_057 shipped this variant with `w@.len() == len` alone and reported
        # the R4 side "degenerate"; that constrained the window's LENGTH but
        # never related its CONTENTS to `buf@`, so the `dotp` invariant -- which
        # is written over `buf@` -- had nothing to rewrite `w@[k]` into. vstd
        # ships a spec for `<[T]>::split_at` (~/tools/verus/vstd/std_specs/slice.rs)
        # and it gives the subrange directly, so this needs NO lemma, NO new
        # trusted item and NO `by (nonlinear_arith)`: 10 verified, 0 errors,
        # the same obligation count as the shipped `verus.rs`.
        ("""            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            fwalk(""",
         """            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            w@ == buf@.subrange(off as int, off + len as int),
            fwalk("""),
        ("""                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                dotp(""",
         """                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                w@ == buf@.subrange(off as int, off + len as int),
                dotp(""")], True),
    ("m_nowin", VERUS_RS, [(
        """    if n < taps {
        return 0;
    }""", "")], True),
]


def write():
    os.makedirs(OUT, exist_ok=True)
    made = []
    for name, src, subs, is_verus in VARIANTS:
        txt = open(src).read()
        for find, rep in subs:
            if find not in txt:
                raise SystemExit(f"gen_controls.py: {name}: substitution not "
                                 f"found in {os.path.basename(src)}:\n{find[:120]}")
            txt = txt.replace(find, rep, 1)
        p = os.path.join(OUT, name + ".rs")
        open(p, "w").write(txt)
        made.append((name, p, is_verus, os.path.basename(src)))
    return made


def build(made):
    os.makedirs(BIN, exist_ok=True)
    for name, p, is_verus, _src in made:
        out = os.path.join(BIN, name + "-O3-isolated")
        if is_verus:
            continue
        cmd = [RUSTC, "--edition", "2021", "-C", "codegen-units=1",
               "-C", "opt-level=3", "-C", "debug-assertions=off",
               "--cfg", "slb_isolated", p, "-o", out]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
        print(f"  {'ok ' if r.returncode == 0 else 'FAIL'} {name:12s} {out}")
        if r.returncode:
            print((r.stdout + r.stderr)[-800:])


def verus(made):
    for name, p, is_verus, _src in made:
        if not is_verus:
            continue
        r = subprocess.run([sys.executable, VERUS, p], capture_output=True,
                           text=True, cwd=REPO)
        tail = [l for l in (r.stdout + r.stderr).splitlines()
                if "verification results" in l or l.startswith("error")]
        print(f"  {name:12s} rc={r.returncode}  " + " | ".join(tail[:3]))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--verus", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        for name, src, _s, v in VARIANTS:
            print(f"  {name:12s} from {os.path.basename(src):16s} "
                  f"{'(verus)' if v else ''}")
        return 0
    made = write()
    print(f"wrote {len(made)} variant(s) to {OUT}")
    if a.build:
        build(made)
    if a.verus:
        verus(made)
    return 0


if __name__ == "__main__":
    sys.exit(main())
