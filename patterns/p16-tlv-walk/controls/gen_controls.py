#!/usr/bin/env python3
"""Generate p16's three in-contract R3 respellings into `.temp/p16/controls/`.

    python3 patterns/p16-tlv-walk/controls/gen_controls.py

**Why this file exists (TASK_021).** `../NOTES.md` §10a states four swept laws,
and three of them — `R3ship − r3_endslice = 2·nrec − 2`,
`R3ship − r3_window = 4·nrec − 8`, `r3_hdrarray − R3ship = nrec` — rest on
binaries built from sources that lived only in gitignored `.temp/p18/v16/`.
TASK_020 shipped the *input* axis (`inputs/gen.py`'s third band); the
**variants** did not ship, so §10a's own ⚠ said rows 2–4 were "reproducible only
by rebuilding `.temp/p18/v16/`" — i.e. not reproducible from the tree at all.
`patterns/p08-overlap-move/controls/gen_controls.py` is the prescribed shape for
a source that must not live in the pattern dir (`.memory/05-layout.md` demand
11: `check.py` requires every `.rs` beside the rungs to be a pinned, cleanly
verifying cell, and `build.py`'s `--cell` list is closed), and this is the same
shape.

**Derived, never transcribed.** Each control is the shipped `safe_tuned.rs` with
one or two *exact-string* substitutions, each asserted to hit exactly once. A
variant therefore cannot silently drift from the rung it is a respelling of: if
someone edits `safe_tuned.rs`, either the substitution still applies and the
control moves with it, or the assertion fires and this script fails loudly. That
is the property the `.temp/p18/v16/` copies did not have.

**What each control is, and why it is in contract.** p16's `idiom.required[0]`
pins two *tokens* — `end - p >= 3` and `vlen > end - (p + 3)` — and its `why`
says the header read and the value fold's *indexing base* are deliberately not
restricted. All three keep both tokens literally, keep `p`/`end` as the
cursor-and-end pair, keep `p = p + 3 + vlen`, fold `nrec`, and contain zero
`unsafe`.

  1. `r3_endslice.rs` — one added line: both reslices come out of `&buf[..end]`
     instead of out of `buf`. `p` stays absolute, `end` stays `off + len`. In
     contract on the tokens *and* on `why` ground (ii)'s gloss ("`p` indexing
     the whole blob"). **2·nrec − 2 cheaper than shipped R3.**
  2. `r3_window.rs` — the window is resliced once before the loop and `p` is
     window-relative, `end = len`. In contract on the tokens; ground (ii)'s
     gloss arguably excludes it, which is why §10a reports it separately.
     **4·nrec − 8 cheaper.**
  3. `r3_hdrarray.rs` — the 3-byte header is read as `[u8; 3]` via `try_into()`
     rather than as a runtime-length reslice. In contract. **`nrec` DEARER**,
     and it is here because a control that goes the wrong way is what shows the
     other two are not an artefact of the measurement.

Nothing here is built by `harness/build.py`, nothing here is a p16 cell, and no
number in `results/` comes from any of it. The commands to build and measure are
printed at the end.

**One difference from p08's generator, and it is a fix.** p08's controls keep
the shipped `#[path = "../../common/driver.rs"]`, which from `.temp/p08/controls/`
resolves to `.temp/common/driver.rs` — a *copy* of `common/` that happens to
exist on this box and is gitignored, so on a fresh clone those controls do not
compile. This script rewrites the path to `../../../common/driver.rs`, which
resolves to the real, hashed `common/driver.rs`. Reported rather than fixed for
p08 (TASK_021).
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p16", "controls")

#: shipped -> generated. The generated file sits three levels under the repo
#: root, the shipped one two, so the relative `#[path]` needs one more `..`.
#: Applied to every control; asserted like any other substitution.
PATH_FIX = ('#[path = "../../common/driver.rs"]',
            '#[path = "../../../common/driver.rs"]')

BANNER = ("//! p16 CONTROL -- an IN-CONTRACT alternate spelling of R3.\n"
          "//! NOT a p16 cell. Generated from `safe_tuned.rs` by\n"
          "//! `patterns/p16-tlv-walk/controls/gen_controls.py`; every\n"
          "//! substitution is asserted to hit exactly once, so this file\n"
          "//! cannot drift from the rung it respells. See ../NOTES.md 10a.\n"
          "//!\n")

CONTROLS = {
    # (1) both reslices out of `&buf[..end]`; `p` still absolute.
    "r3_endslice.rs": (
        "//! `r3_endslice` -- the MINIMAL in-contract edit: one added line.\n"
        "//! Both reslices come out of `&buf[..end]` instead of out of `buf`.\n"
        "//! `p` is still the absolute whole-blob offset, `end` is still\n"
        "//! `off + len`, both named comparisons are literal and unchanged, and\n"
        "//! `p = p + 3 + vlen` is unchanged. Measured: `R3ship - this =\n"
        "//! 2*nrec - 2`, zero residual over 22 committed sweep blobs.\n"
        "//!\n"
        "//! The one thing to attack, answered in ../NOTES.md 10a: `&buf[..end]`\n"
        "//! moves a bounds check EARLIER than shipped R3's first `&buf[p..p+3]`.\n"
        "//! Under the kernel's `requires off + len <= buf_len` -- structural,\n"
        "//! true on every input this benchmark runs -- the two are the same\n"
        "//! function. That is what `.memory/01-ladder.md`'s R3 definition means\n"
        "//! by \"hoisted length assertions\".\n",
        [PATH_FIX,
         ("    let end: usize = off + len;\n",
          "    let end: usize = off + len;\n    let w: &[u8] = &buf[..end];\n"),
         ("let h: &[u8] = &buf[p..p + 3];", "let h: &[u8] = &w[p..p + 3];"),
         ("acc = buf[p + 3..p + 3 + vlen]", "acc = w[p + 3..p + 3 + vlen]")]),

    # (2) the window resliced once; `p` window-relative.
    "r3_window.rs": (
        "//! `r3_window` -- the window is resliced ONCE before the loop and `p`\n"
        "//! is window-relative, `end = len`. Both named comparisons appear\n"
        "//! literally and unchanged; the cursor-and-end pair is still `p`/`end`,\n"
        "//! still `usize`, still advanced by `p = p + 3 + vlen`. The only change\n"
        "//! is which slice the header read and the value fold index into, which\n"
        "//! p16's own `why` says is deliberately NOT restricted.\n"
        "//! Measured: `R3ship - this = 4*nrec - 8`, zero residual.\n"
        "//!\n"
        "//! Reported SEPARATELY in ../NOTES.md 10a because `why` ground (ii)'s\n"
        "//! gloss (\"`p` indexing the whole blob\") arguably excludes it, and\n"
        "//! the in-contract minimum should not rest on the contested reading.\n",
        [PATH_FIX,
         ("    let mut p: usize = off;\n    let end: usize = off + len;\n",
          "    let w: &[u8] = &buf[off..off + len];\n"
          "    let mut p: usize = 0;\n    let end: usize = len;\n"),
         ("let h: &[u8] = &buf[p..p + 3];", "let h: &[u8] = &w[p..p + 3];"),
         ("acc = buf[p + 3..p + 3 + vlen]", "acc = w[p + 3..p + 3 + vlen]")]),

    # (3) the header as a fixed-size array. DEARER, and that is the point.
    "r3_hdrarray.rs": (
        "//! `r3_hdrarray` -- shipped R3 with ONLY the three-byte header read\n"
        "//! respelled: a fixed-size array via `try_into()` instead of a\n"
        "//! runtime-length reslice, so the header length is a type-level\n"
        "//! constant. Both named comparisons literal, cursor and end unchanged,\n"
        "//! whole-blob indexing unchanged, value fold unchanged.\n"
        "//!\n"
        "//! Measured: `this - R3ship = nrec`, i.e. **DEARER**. It is kept as a\n"
        "//! control precisely for that: a respelling that goes the wrong way is\n"
        "//! what shows the other two are a property of the code and not of the\n"
        "//! measurement. The `Err(_) => break` arm is unreachable -- the slice\n"
        "//! is always three bytes -- and exists only because `try_into()` is\n"
        "//! fallible in the type system.\n",
        [PATH_FIX,
         ("        let h: &[u8] = &buf[p..p + 3];\n",
          "        let h: [u8; 3] = match buf[p..p + 3].try_into() {\n"
          "            Ok(a) => a,\n"
          "            Err(_) => break,\n"
          "        };\n")]),
}

RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
#: `harness/build.py::rust_flags("O3", "isolated")`, verbatim. Quoted here so
#: the controls are built exactly the way the cells they are compared against
#: are -- a marginal is only exact within one build (../NOTES.md 10b).
FLAGS = ["--edition", "2021", "-C", "codegen-units=1", "-C", "opt-level=3",
         "-C", "debug-assertions=off", "--cfg", "slb_isolated"]


def sub(src_name, out_name, header, pairs):
    s = open(os.path.join(PDIR, src_name)).read()
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{out_name}: {n} hits (want 1) for {old!r}"
        s = s.replace(old, new)
    open(os.path.join(OUT, out_name), "w").write(BANNER + header + "\n" + s)
    print(f"  {out_name:18s} <- {src_name} ({len(pairs)} substitution(s))")


def main():
    build = "--build" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    print("p16 controls ->", os.path.relpath(OUT, os.getcwd()))
    for name, (header, pairs) in sorted(CONTROLS.items()):
        sub("safe_tuned.rs", name, header, pairs)

    if build:
        print("\nbuilding (harness/build.py's exact -O3 isolated flags):")
        for name in sorted(CONTROLS):
            src = os.path.join(OUT, name)
            out = os.path.join(OUT, name[:-3])
            r = subprocess.run([RUSTC] + FLAGS + [src, "-o", out],
                               capture_output=True, text=True)
            print(f"  {name:18s} {'ok' if r.returncode == 0 else 'FAILED'}")
            if r.returncode != 0:
                print(r.stderr[-2000:])
                return 1

    print(f"""
build them:
  python3 patterns/p16-tlv-walk/controls/gen_controls.py --build

...or by hand, with harness/build.py's exact -O3 isolated flags:
  {RUSTC} \\
      {' '.join(FLAGS)} \\
      .temp/p16/controls/r3_endslice.rs -o .temp/p16/controls/r3_endslice

check equivalence (all three must print the shipped R3 binary's checksum and
exit code on every committed input, sweep blobs included):
  python3 patterns/p16-tlv-walk/inputs/gen.py --sweep
  for f in patterns/p16-tlv-walk/inputs/*.bin; do ... done

re-derive NOTES.md 10a's laws (marginal Ir/call, n_iters 100 -> 200, the same
probe harness/check.py step 3b uses):
  R3ship - r3_endslice = 2*nrec - 2
  R3ship - r3_window   = 4*nrec - 8
  r3_hdrarray - R3ship = nrec
on the 22 `sweep-n{{nrec}}v{{vlen}}.bin` blobs inputs/gen.py's third band emits.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
