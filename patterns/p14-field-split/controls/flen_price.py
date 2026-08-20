#!/usr/bin/env python3
"""PRICE the `flen = i - s;` idiom entry, on ALL EIGHT CELLS.

WHY THIS FILE EXISTS. `../spec.md`'s `required` list pins the field length to a
local, `flen = i - s;`, in all seven rungs -- and that entry is **the one entry
in p14's declaration that was added in response to a gate measurement**
(`identity: unsafe vs verus O0 differ`), which `spec.md`'s `why` discloses by
name. p13's rule is that a fiat is legitimate but its price must be published
beside the number it protects, and TASK_049 published the price for R4/R5 only.
TASK_049_REVIEW m4 measured the rest; this script is what re-derives all of it,
because `.memory/05-layout.md` item 11 says a control that lives only in
gitignored scratch is the self-certifying trap one level down.

    python3 patterns/p14-field-split/controls/flen_price.py

Every variant here is a function of the COMMITTED rung sources plus the exact
substitutions below -- the same discipline as `gen_controls.py`, and the script
fails loudly if a substitution stops matching, rather than pricing a stale copy.

WHAT IT MEASURES. `harness/asm.py`'s own kernel report (`n_fn`, `md5_fn_norel`)
for each of the eight cells at `-O0` and `-O3`, with and without the entry.
`../NOTES.md` 6a' publishes the table. The two facts that matter:

  * at `-O3` the entry is worth EXACTLY ZERO on every cell -- identical
    `md5_fn_norel` -- so it moves no published p14 figure, every one of which is
    an `-O3` marginal. That is the direction test, and it reads 0.0000.
  * at `-O0` it is NOT zero and NOT sign-neutral: it makes three Rust cells
    cheaper by 3 and the four C cells dearer by 1 or 2. No p14 claim rests on an
    `-O0` row and none may, but the disclosure belongs beside the entry.

Scratch is per-PID.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "harness"))
import asm  # noqa: E402

PDIR = os.path.join(REPO, "patterns", "p14-field-split")
COMMON = os.path.join(REPO, "common")
OUT = os.path.join(REPO, ".temp", "p14", f"flen.{os.getpid()}")
GCC = "/usr/bin/gcc"
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VERUS_RUN = os.path.join(REPO, "verus_run.py")

# (cell, source, the substitution that DELETES the entry)
RUST = {
    "safe_naive": ("safe_naive.rs",
                   "                let flen: usize = i - s;\n"
                   "                tl[nt] = flen;",
                   "                tl[nt] = i - s;"),
    "safe_tuned": ("safe_tuned.rs",
                   "                let flen: usize = i - s;\n"
                   "                tl[nt] = flen;",
                   "                tl[nt] = i - s;"),
    "unsafe": ("unsafe.rs",
               "                let flen: usize = i - s;\n"
               "                unsafe { *tl.get_unchecked_mut(nt) = flen; }",
               "                unsafe { *tl.get_unchecked_mut(nt) = i - s; }"),
    "verus": ("verus.rs",
              "                let flen: usize = i - s;\n"
              "                tl_set_unchecked(&mut tl, nt, flen);",
              "                tl_set_unchecked(&mut tl, nt, i - s);"),
}
C = {
    "c-gcc": (GCC, "kernel.c"),
    "c-gcc-h": (GCC, "kernel_hardened.c"),
    "c-clang": (CLANG, "kernel.c"),
    "c-clang-h": (CLANG, "kernel_hardened.c"),
}
C_SUB = ("                flen = i - s;\n                tl[nt] = flen;",
         "                tl[nt] = i - s;")


def sub(text, old, new, tag):
    got = text.count(old)
    if got != 1:
        raise SystemExit(f"flen_price.py: {tag}: expected 1 occurrence of\n"
                         f"---\n{old}\n---\ngot {got}. The shipped source "
                         f"moved; fix the substitution, not the control.")
    return text.replace(old, new)


def rust_flags(opt):
    return ["-C", "codegen-units=1", "--cfg", "slb_isolated",
            "-C", f"opt-level={'0' if opt == 'O0' else '3'}",
            "-C", "debug-assertions=off"]


def build_rust(cell, src, opt, out):
    if cell == "verus":
        cmd = [sys.executable, VERUS_RUN, "--compile", src, "-o", out] + \
            rust_flags(opt)
    else:
        cmd = [RUSTC, "--edition", "2021"] + rust_flags(opt) + [src, "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    return out if not r.returncode and os.path.exists(out) else \
        _fail(cell, opt, r)


def build_c(cell, ksrc, incdir, opt, out):
    cc = C[cell][0]
    cmd = [cc, "-std=c99", "-Wall", "-Wextra", "-" + opt, "-DSLB_ISOLATED",
           "-I", COMMON, "-I", incdir, os.path.join(COMMON, "driver.c"),
           ksrc, os.path.join(PDIR, "c", "main.c"), "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    return out if not r.returncode else _fail(cell, opt, r)


def _fail(cell, opt, r):
    raise SystemExit(f"flen_price.py: build failed {cell} {opt}: "
                     f"{(r.stdout + r.stderr)[-400:]}")


def main():
    os.makedirs(os.path.join(OUT, "c"), exist_ok=True)
    print(f"# scratch {OUT}")
    # the no-flen variants, derived from the committed sources
    for cell, (name, old, new) in RUST.items():
        text = open(os.path.join(PDIR, name)).read()
        open(os.path.join(OUT, name), "w").write(sub(text, old, new, cell))
    for name in ("kernel.c", "kernel_hardened.c", "kernel.h"):
        text = open(os.path.join(PDIR, "c", name)).read()
        if name.endswith(".c"):
            text = sub(text, C_SUB[0], C_SUB[1], name)
        open(os.path.join(OUT, "c", name), "w").write(text)

    rows = {}
    for opt in ("O0", "O3"):
        for cell, (name, _, _) in RUST.items():
            for variant, src in (("shipped", os.path.join(PDIR, name)),
                                 ("noflen", os.path.join(OUT, name))):
                b = build_rust(cell, src, opt,
                               os.path.join(OUT, f"{cell}.{opt}.{variant}"))
                k = asm.kernel(b, "kernel")
                rows[(cell, opt, variant)] = (k.n_fn, k.md5_fn_norel)
        for cell, (_, ksrc) in C.items():
            for variant, path, inc in (
                    ("shipped", os.path.join(PDIR, "c", ksrc),
                     os.path.join(PDIR, "c")),
                    ("noflen", os.path.join(OUT, "c", ksrc),
                     os.path.join(OUT, "c"))):
                b = build_c(cell, path, inc, opt,
                            os.path.join(OUT, f"{cell}.{opt}.{variant}"))
                k = asm.kernel(b, "kernel")
                rows[(cell, opt, variant)] = (k.n_fn, k.md5_fn_norel)

    cells = list(C) + list(RUST)
    print(f"\n{'cell':12s} {'-O0 without':>11s} {'-O0 with':>9s} "
          f"{'-O0 price':>9s}   {'-O3 identical?':>14s}  -O3 md5_fn_norel")
    for cell in cells:
        n_no, _ = rows[(cell, "O0", "noflen")]
        n_sh, _ = rows[(cell, "O0", "shipped")]
        _, m_no = rows[(cell, "O3", "noflen")]
        _, m_sh = rows[(cell, "O3", "shipped")]
        print(f"{cell:12s} {n_no:11d} {n_sh:9d} {n_sh - n_no:+9d}   "
              f"{str(m_no == m_sh):>14s}  {m_sh[:12]}")
    same = all(rows[(c, 'O3', 'noflen')][1] == rows[(c, 'O3', 'shipped')][1]
               for c in cells)
    print(f"\nDIRECTION TEST at -O3 (the level every published p14 figure uses): "
          f"identical on all {len(cells)} cells: {same}")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
