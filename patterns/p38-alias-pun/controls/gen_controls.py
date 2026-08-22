#!/usr/bin/env python3
"""p38 controls: every variant that is NOT a rung, generated from the shipped
sources and measured rather than asserted.

Scratch lands in `.temp/p38/controls/` -- **this pattern's own subdirectory**.
p27's copy of a sibling's clayout still said `.temp/p14/` and overwrote p14's
`meta.json` (`915bb8a`); the constant below is the fix and it is checked at
import time.

    python3 patterns/p38-alias-pun/controls/gen_controls.py --list
    python3 patterns/p38-alias-pun/controls/gen_controls.py --run c_memcpy c_union
    python3 patterns/p38-alias-pun/controls/gen_controls.py --run all --ir

Every control is derived from `c/kernel.c`, `c/kernel_hardened.c` or
`unsafe.rs` by an exact-string substitution recorded here, so a reader can see
what changed without a diff, and a substitution that stops matching is a hard
error rather than a silent no-op.
"""

import argparse
import hashlib
import os
import re
import shutil
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p38", "controls")     # <-- p38's OWN dir
assert OUT.endswith(os.path.join("p38", "controls")), OUT

GCC = "/usr/bin/gcc"
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
VERUS_RUN = os.path.join(REPO, "verus_run.py")
INPUTS = os.path.join(PDIR, "inputs")

sys.path.insert(0, os.path.join(REPO, "harness"))
import asm as asmmod        # noqa: E402

CK = os.path.join(PDIR, "c", "kernel.c")
CH = os.path.join(PDIR, "c", "kernel_hardened.c")
RU = os.path.join(PDIR, "unsafe.rs")

PUN = """static uint32_t rec_len(const uint16_t *r)
{
    return *(const uint32_t *)r;
}"""

HALVES = """static uint32_t rec_len(const uint16_t *r)
{
    return (uint32_t)r[0] + 65536 * (uint32_t)r[1];
}"""

MEMCPY = """static uint32_t rec_len(const uint16_t *r)
{
    uint32_t v;
    memcpy(&v, r, 4);
    return v;
}"""

UNION = """union rec_u {
    uint16_t h[2];
    uint32_t w;
};

static uint32_t rec_len(const uint16_t *r)
{
    return ((const union rec_u *)r)->w;
}"""

TWICE = """        if (rec_len(&sc[i]) > room)
            rec_set_len(&sc[i], (uint32_t)room);
        n = (size_t)rec_len(&sc[i]);"""

ONCE = """        n = (size_t)rec_len(&sc[i]);
        if (n > room) {
            rec_set_len(&sc[i], (uint32_t)room);
            n = room;
        }"""

NOBACK = """        n = (size_t)rec_len(&sc[i]);
        if (n > room)
            n = room;
        (void)rec_set_len;"""

SETTER_HALVES = """static void rec_set_len(uint16_t *r, uint32_t v)
{
    r[0] = (uint16_t)(v % 65536);
    r[1] = (uint16_t)(v / 65536);
}"""

SETTER_PUN = """static void rec_set_len(uint16_t *r, uint32_t v)
{
    *(uint32_t *)r = v;
}"""


def sub(text, old, new, what):
    if old not in text:
        raise SystemExit(f"gen_controls.py: {what}: substitution no longer "
                         f"matches the shipped source -- the control is stale")
    return text.replace(old, new, 1)


def with_string_h(text):
    return sub(text, '#include "kernel.h"', '#include <string.h>\n\n#include "kernel.h"',
               "add string.h")


# --------------------------------------------------------------- controls ----
def c_controls():
    """name -> (source text, extra cc flags, one-line why)."""
    k, h = open(CK).read(), open(CH).read()
    return {
        # THE FREE DEFINED SPELLINGS. Both are legal C; both compile to the
        # UB spelling's own machine code on clang.
        "c_memcpy": (with_string_h(sub(h, HALVES, MEMCPY, "memcpy rec_len")), [],
                     "memcpy(&v, r, 4) -- the C FAQ's answer to strict aliasing"),
        "c_union": (sub(h, HALVES, UNION, "union rec_len"), [],
                    "union punning -- the other legal spelling"),
        # THE RE-READ IS LOAD-BEARING. Fold the two rec_len calls into one and
        # the compiler has nothing to forward past.  -- condition (ii)
        "c_once": (sub(k, TWICE, ONCE, "single rec_len call"), [],
                   "the pun, but rec_len called ONCE -- no re-read to answer stale"),
        # THE ACCESSOR PAIR AGREES ABOUT THE TYPE. Both getter and setter pun,
        # so there is no incompatible pair for the type rule to separate.
        #                                                   -- condition (i)
        "c_symset": (sub(k, SETTER_HALVES, SETTER_PUN, "punning rec_set_len"), [],
                     "SYMMETRIC accessor pair -- rec_set_len puns too"),
        # THE CLAMP IS NEVER WRITTEN BACK. The store whose only consumer is the
        # re-read three lines later simply does not happen. -- condition (iii)
        "c_noback": (sub(k, TWICE, NOBACK, "no write-back"), [],
                     "the pun, clamped into a local, NO write-back at all"),
        # THE FLAG PRICE. Same source as the shipped R1, one build flag.
        "c_nosa": (k, ["-fno-strict-aliasing"],
                   "the shipped R1 built -fno-strict-aliasing (what Linux does)"),
        "c_pun": (k, [], "the shipped R1, for a same-run baseline"),
        "c_halves": (h, [], "the shipped R1h, for a same-run baseline"),
    }


R4_PUN_OLD = """        let d: usize = unsafe {
            *sc.get_unchecked(i) as usize + 65536 * (*sc.get_unchecked(i + 1) as usize)
        };"""
R4_PUN_NEW = """        let d: usize = unsafe {
            core::ptr::read_unaligned(sc.as_ptr().add(i) as *const u32) as usize
        };"""
R4_PUN_OLD2 = """        let n: usize = unsafe {
            *sc.get_unchecked(i) as usize + 65536 * (*sc.get_unchecked(i + 1) as usize)
        };"""
R4_PUN_NEW2 = """        let n: usize = unsafe {
            core::ptr::read_unaligned(sc.as_ptr().add(i) as *const u32) as usize
        };"""


def r4_pun_source():
    """R4 with the DIRECT analogue of the C pun: a u32 `read_unaligned` out of
    the u16 scratch, store through u16 and load through u32, at opt-level 3.

    **In Rust this is DEFINED**, and that is p38's headline. It is not a rung
    only because ../spec.md pins `identity: unsafe == verus, O3 exact` and the
    pinned vstd cannot express it -- see `--verus`."""
    s = open(RU).read()
    s = sub(s, R4_PUN_OLD, R4_PUN_NEW, "r4_pun d")
    s = sub(s, R4_PUN_OLD2, R4_PUN_NEW2, "r4_pun n")
    return s


# ------------------------------------------------------------------- build ---
def build_c(name, text, flags, cc, opt="O3", mode="isolated"):
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(OUT, f"{name}_kernel.c")
    open(src, "w").write(text)
    exe = os.path.join(OUT, f"{name}-{os.path.basename(cc)}-{opt}-{mode}")
    cmd = [cc, "-std=c99", "-Wall", "-Wextra", f"-{opt}"]
    cmd += ["-DSLB_ISOLATED"] if mode == "isolated" else ["-flto"]
    cmd += flags + ["-I", os.path.join(REPO, "common"),
                    "-I", os.path.join(PDIR, "c"),
                    os.path.join(REPO, "common", "driver.c"), src,
                    os.path.join(PDIR, "c", "main.c"), "-o", exe]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"gen_controls.py: {name} on {cc} failed:\n{r.stderr[-800:]}")
    return exe


def build_rust(name, text, opt="3"):
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(OUT, f"{name}.rs")
    open(src, "w").write(text)
    exe = os.path.join(OUT, f"{name}-O{opt}")
    r = subprocess.run([RUSTC, "--edition", "2021", "-C", "codegen-units=1",
                        "-C", f"opt-level={opt}", "-C", "debug-assertions=off",
                        "--cfg", "slb_isolated", src, "-o", exe],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"gen_controls.py: {name} failed:\n{r.stderr[-800:]}")
    return exe


def run(exe, blob):
    r = subprocess.run([exe, os.path.join(INPUTS, blob)],
                       capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout.strip(), r.stderr.strip()[:200]


def probe_input(blob, n_iters):
    src = os.path.join(INPUTS, blob)
    out = os.path.join(OUT, f"probe-{n_iters}-{blob}")
    b = open(src, "rb").read()
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
    (`.memory/03-measurement.md`)."""
    a, b = ir(exe, probe_input(blob, lo)), ir(exe, probe_input(blob, hi))
    return None if a is None or b is None else (b - a) / (hi - lo)


def kstat(exe):
    try:
        k = asmmod.kernel(exe, "kernel")
    except KeyError:
        return None
    return k


# ------------------------------------------------------------------ report ---
def do_c(names, want_ir):
    ctl = c_controls()
    print(f"{'control':10s} {'cc':6s} {'n_fn_nopad':>10s} {'md5_fn':34s} "
          f"{'small Ir/call':>13s}  behaviour on adversarial-oob.bin")
    for name in names:
        text, flags, why = ctl[name]
        for cc in (GCC, CLANG):
            exe = build_c(name, text, flags, cc)
            k = kstat(exe)
            m = marginal_ir(exe, "small.bin") if want_ir else None
            rc, so, se = run(exe, "adversarial-oob.bin")
            tag = "gcc" if cc == GCC else "clang"
            print(f"{name:10s} {tag:6s} {k.n_fn_nopad:10d} {k.md5_fn:34s} "
                  f"{('%.2f' % m) if m is not None else '-':>13s}  "
                  f"rc={rc} out={so!r}")
        print(f"           why: {why}")


def do_r4_pun(want_ir, want_verus):
    src = r4_pun_source()
    exe = build_rust("r4_pun", src)
    print("\nr4_pun -- the DIRECT Rust analogue of the C pun "
          "(read_unaligned::<u32> on a *const u16)")
    for blob in ("small.bin", "adversarial-oob.bin"):
        rc, so, se = run(exe, blob)
        print(f"    {blob:24s} rc={rc} out={so}")
    k = kstat(exe)
    if k:
        print(f"    n_fn_nopad={k.n_fn_nopad} md5_fn={k.md5_fn}")
    if want_ir:
        print(f"    small Ir/call = {marginal_ir(exe, 'small.bin')}")
    if want_verus:
        vs = open(os.path.join(PDIR, "verus.rs")).read()
        vs = sub(vs, """        let d: usize = sc_get_unchecked(&sc, i) as usize + 65536 * (sc_get_unchecked(
            &sc,
            i + 1,
        ) as usize);""", R4_PUN_NEW, "verus twin of r4_pun")
        p = os.path.join(OUT, "r4_pun_verus.rs")
        open(p, "w").write(vs)
        r = subprocess.run([sys.executable, VERUS_RUN, p],
                           capture_output=True, text=True, timeout=1800)
        txt = r.stdout + r.stderr
        print("    Verus on the R5 twin of this spelling:")
        for line in txt.splitlines():
            if "is not supported" in line or "verification results" in line:
                print("      " + line.strip()[:150])


# Every sanitizer build has a NAME, so a claim about one can be re-run rather
# than re-derived. Until TASK_067 this table was anonymous and three committed
# files -- ../NOTES.md, ../model.py and ../spec.md, the hashed layer -- cited a
# build called `s_asan_O3` that `--list` did not ship (TASK_066_REVIEW m7).
SAN_BUILDS = {
    "s_asan_O1_gate": ("gcc -O1 asan+ubsan (WHAT THE GATE BUILDS)", GCC,
                       ["-O1", "-fsanitize=address,undefined",
                        "-static-libasan", "-static-libubsan"]),
    "s_asan_O1_sa": ("gcc -O1 -fstrict-aliasing asan+ubsan (THE ONE-FLAG "
                     "REPAIR: the hole is FLAG-gated, not LEVEL-gated)", GCC,
                     ["-O1", "-fstrict-aliasing",
                      "-fsanitize=address,undefined",
                      "-static-libasan", "-static-libubsan"]),
    "s_asan_O3": ("gcc -O3 asan+ubsan", GCC,
                  ["-O3", "-fsanitize=address,undefined", "-static-libasan",
                   "-static-libubsan"]),
    "s_ubsan_O3": ("gcc -O3 ubsan only", GCC, ["-O3", "-fsanitize=undefined"]),
    "s_tysan_iso": ("clang -O3 tysan (isolated)", CLANG,
                    ["-O3", "-fsanitize=type", "-DSLB_ISOLATED"]),
    "s_tysan_lto": ("clang -O3 tysan (whole/-flto)", CLANG,
                    ["-O3", "-fsanitize=type", "-flto"]),
}


def do_sanitizers(names=None):
    """The two catchers that CAN see p38, and the one that cannot."""
    k = open(CK).read()
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(OUT, "san_kernel.c")
    open(src, "w").write(k)
    print("\nsanitizers on c/kernel.c, adversarial-oob.bin")
    for name in (names or list(SAN_BUILDS)):
        tag, cc, flags = SAN_BUILDS[name]
        exe = os.path.join(OUT, "san-" + name)
        cmd = [cc, "-std=c99", "-g"] + flags
        if "-flto" in flags and "clang" in cc:
            lld = os.path.expanduser("~/tools/llvm/bin/ld.lld")
            if os.path.exists(lld):
                cmd.insert(1, "-fuse-ld=lld")
        if "-DSLB_ISOLATED" not in flags and "-flto" not in flags:
            cmd.append("-DSLB_ISOLATED")
        cmd += ["-I", os.path.join(REPO, "common"), "-I", os.path.join(PDIR, "c"),
                os.path.join(REPO, "common", "driver.c"), src,
                os.path.join(PDIR, "c", "main.c"), "-o", exe]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"    {name:14s} {tag} BUILD FAILED: {r.stderr[-200:]}")
            continue
        rc, so, se = run(exe, "adversarial-oob.bin")
        hits = [ln for ln in se.splitlines()
                if "runtime error" in ln or "ERROR:" in ln
                or "type-aliasing-violation" in ln]
        print(f"    {name:14s} {tag}\n        rc={rc} out={so!r}")
        for hh in hits[:2]:
            print(f"        | {hh.strip()[:150]}")
        if not hits:
            print("        | (silent)")


MUSTALIAS = r"""/* p38 control x_mustalias: WHY clang declines the shipped kernel's violation
   and gcc takes it. Same violation, same address at run time in every variant;
   what varies is what BasicAA can work out about the two accesses.

   The two-variant version of this control (TASK_066) concluded "LLVM declines
   TBAA when BasicAA has proved the two accesses are the SAME ADDRESS". That is
   sufficient but NOT NECESSARY and it does not cover p38's own kernel, which
   is the PARTIAL case -- two 2-byte stores against one 4-byte load, never
   MustAlias. The three variants added at TASK_067 (TASK_066_REVIEW m4) settle
   it: the discriminator is whether BasicAA can COMPUTE THE OFFSET.

     one_base         one base, full overlap                    declined
     one_base_partial one base, only w[0] written -- NOT MustAlias, declined
     known_off        one base, constant offset                 declined
     opaque_off       one base, offset opaque -- DECISIVE,      exploited
     two_params       two pointers the compiler cannot relate,  exploited

   ⚠ It is the offset BETWEEN the store and the load that has to be opaque,
   not the offset itself. A first draft of `opaque_off` applied the same
   opaque `k` to both accesses; their difference is then 0 symbolically,
   BasicAA still answers MustAlias, and clang still declines (measured, 16 at
   every level). What makes it exploit is an opaque offset on ONE side only.

   gcc applies TBAA in all five. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#define CAP 16u
static volatile size_t g_zero = 0;      /* 0 at run time, opaque at compile time */
__attribute__((noinline))
static uint32_t one_base(uint32_t *lenp)
{
    uint16_t *w = (uint16_t *)lenp;
    if (*lenp > CAP) { w[0] = (uint16_t)CAP; w[1] = 0; }
    return *lenp;
}
__attribute__((noinline))
static uint32_t one_base_partial(uint32_t *lenp)
{
    /* Only the LOW half is written, so the 2-byte store and the 4-byte load
       PARTIALLY overlap and BasicAA can never answer MustAlias. This is p38's
       own kernel's shape. */
    uint16_t *w = (uint16_t *)lenp;
    if (*lenp > CAP) { w[0] = (uint16_t)CAP; }
    return *lenp;
}
__attribute__((noinline))
static uint32_t known_off(uint32_t *base)
{
    uint16_t *w = (uint16_t *)(base + 1);
    if (base[1] > CAP) { w[0] = (uint16_t)CAP; w[1] = 0; }
    return base[1];
}
__attribute__((noinline))
static uint32_t opaque_off(uint32_t *lenp)
{
    /* ONE base pointer, exactly as in one_base -- only the OFFSET FROM THE
       LOAD TO THE STORE is hidden. `g_zero` is 0, so this is the same address
       at run time as one_base's. */
    uint16_t *w = (uint16_t *)lenp + g_zero;
    if (*lenp > CAP) { w[0] = (uint16_t)CAP; w[1] = 0; }
    return *lenp;
}
__attribute__((noinline))
static uint32_t two_params(uint32_t *lenp, uint16_t *w)
{
    if (*lenp > CAP) { w[0] = (uint16_t)CAP; w[1] = 0; }
    return *lenp;
}
int main(int argc, char **argv)
{
    uint32_t a = (argc > 1) ? (uint32_t)strtoul(argv[1], NULL, 0) : 4000;
    uint32_t l1 = a, l2 = a, l3 = a, l4 = a;
    uint32_t arr1[2] = { 0, a };
    printf("one_base=%u one_base_partial=%u known_off=%u opaque_off=%u "
           "two_params=%u   (defined answer: 16 everywhere)\n",
           one_base(&l1), one_base_partial(&l3), known_off(arr1),
           opaque_off(&l4), two_params(&l2, (uint16_t *)&l2));
    return 0;
}
"""


def do_mustalias():
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(OUT, "x_mustalias.c")
    open(src, "w").write(MUSTALIAS)
    print("\nx_mustalias -- the mechanism behind 'gcc exploits it, clang does not'")
    for cc, tag in ((GCC, "gcc"), (CLANG, "clang")):
        for o in ("O1", "O2", "O3"):
            for fl in ("-fstrict-aliasing", "-fno-strict-aliasing"):
                exe = os.path.join(OUT, f"x_mustalias-{tag}-{o}-{fl[1:6]}")
                r = subprocess.run([cc, f"-{o}", fl, "-o", exe, src],
                                   capture_output=True, text=True)
                if r.returncode:
                    continue
                out = subprocess.run([exe, "4000"], capture_output=True,
                                     text=True).stdout.strip()
                print(f"    {tag:6s} {o:3s} {fl:21s} {out}")


ALL = ["c_pun", "c_halves", "c_memcpy", "c_union", "c_once", "c_symset",
       "c_noback", "c_nosa"]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", nargs="*", default=None)
    ap.add_argument("--ir", action="store_true", help="measure marginal Ir (slow)")
    ap.add_argument("--verus", action="store_true", help="run r4_pun's R5 twin")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--clean", action="store_true")
    ap.add_argument("--out", default=OUT,
                    help="scratch dir (must be under .temp/; default "
                         ".temp/p38/controls -- this pattern's OWN dir)")
    a = ap.parse_args()
    globals()["OUT"] = os.path.abspath(a.out)
    assert OUT.startswith(os.path.join(REPO, ".temp") + os.sep), OUT
    if a.clean:
        shutil.rmtree(OUT, ignore_errors=True)
        print(f"removed {OUT}")
        return 0
    if a.list:
        for n, (_t, f, why) in c_controls().items():
            print(f"  {n:14s} {'flags=' + ' '.join(f) if f else '':26s} {why}")
        print(f"  {'r4_pun':14s} {'':26s} "
              "the Rust read_unaligned analogue (+ --verus)")
        for n, (tag, _cc, _f) in SAN_BUILDS.items():
            print(f"  {n:14s} {'':26s} {tag}")
        print(f"  {'sanitizers':14s} {'':26s} all six s_* builds at once")
        print(f"  {'mustalias':14s} {'':26s} "
              "why clang declines and gcc does not (5 variants)")
        return 0
    names = a.run or ALL
    if names == ["all"]:
        names = ALL + list(SAN_BUILDS) + ["r4_pun", "mustalias"]
    unknown = [n for n in names if n not in c_controls() and n not in SAN_BUILDS
               and n not in ("r4_pun", "sanitizers", "mustalias")]
    if unknown:
        raise SystemExit(f"gen_controls.py: no such control: {', '.join(unknown)}"
                         f" (try --list)")
    os.makedirs(OUT, exist_ok=True)
    cs = [n for n in names if n in c_controls()]
    if cs:
        do_c(cs, a.ir)
    if not a.run or "r4_pun" in names:
        do_r4_pun(a.ir, a.verus)
    sans = [n for n in names if n in SAN_BUILDS]
    if not a.run or "sanitizers" in names:
        sans = list(SAN_BUILDS)
    if sans:
        do_sanitizers(sans)
    if not a.run or "mustalias" in names:
        do_mustalias()
    return 0


if __name__ == "__main__":
    sys.exit(main())
