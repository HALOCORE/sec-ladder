#!/usr/bin/env python3
"""p42 control 2 -- the R3-side and R4-side SPELLING SPANS, both sides searched.

`.memory/01-ladder.md` asks every pattern for an in-contract spread beside its
headline, and `.memory/06-catalogue.md`'s probe-3 note asks that when the
flattering direction shows up -- safe Rust beating unsafe Rust -- BOTH sides are
searched and the lever count on each is stated.  p42 is in the flattering
direction, so this script exists to make the search reproducible rather than
asserted.

**Four spellings per side.**  Each variant is derived from a SHIPPED rung by
textual substitution, here, in this file: nothing is a hand-copied fork, so a
variant cannot silently drift away from the rung it is a variant of.

R4 side (all four release the digest on both paths, all four are `unsafe`):
  ship      the shipped rung: index `i`, address via `dig_at` -> `with_addr`
  add       `p.add(i)` instead of `p.with_addr(base + i)`
  movptr    a moving cursor plus the counter, `w.add(1)` / `q.sub(1)`
  endptr    a cursor compared against an end pointer, `with_addr` only,
            i.e. ONE induction variable per loop

R3 side (all four are safe, all four keep the pinned allocation-before-test
order):
  ship      `Vec::with_capacity` + `extend` + `iter().rev().fold`
  revidx    `extend`, then the fold by reverse INDEX
  zeroed    `vec![0u8; len]` + `clear` + `extend` + `rev().fold`
  push      `Vec::with_capacity` + `push` per element + index fold

⚠ **ADMISSIBILITY IS NOT THE SAME AS BEING CHEAPEST, and two of the R4 variants
are NOT admissible rungs.**  R4 must have a byte-identical R5 twin that Verus
verifies, and the pinned vstd specifies `<*mut T>::addr` and `<*mut T>::with_addr`
and NOT `<*mut T>::add`/`offset` (`grep -n assume_specification
~/tools/verus/vstd/raw_ptr.rs`).  So `add` and `movptr` cannot be rungs at all;
`endptr` uses only `with_addr` and `<*mut T as PartialEq>::eq`, both specified,
so it is admissible IN PRINCIPLE and nobody has built its R5.  p42 therefore
holds its R4 endpoint FIXED BY FIAT at the shipped, verified spelling and
publishes the span, which is what `.memory/01-ladder.md` asks for instead of a
pair interval.

Every variant is checked to print the shipped checksum before it is measured; a
variant that computes something else is not a spelling of this kernel.

  python3 patterns/p42-goto-cleanup/controls/spellings.py            # build+check
  python3 patterns/p42-goto-cleanup/controls/spellings.py --measure  # + callgrind

Sources and binaries land in .temp/t104/spell/ and are re-derivable from here.
"""

import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "t104", "spell")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
RFLAGS = ["--edition", "2021", "-C", "codegen-units=1", "-C", "opt-level=3",
          "-C", "debug-assertions=off", "--cfg", "slb_isolated"]

# The two loops of the shipped R4, anchored on their FIRST and LAST statements
# so the doc comment between them does not have to be duplicated here. `sub`
# asserts the anchor is present, which is what stopped this control from
# silently measuring a stale variant when unsafe.rs grew a comment.
U_LOOPS_HEAD = "    let mut run: u64 = 0;\n    let mut i: usize = 0;\n    while i < len {"
U_LOOPS_TAIL = """        i = i + 1;
    }
    let mut acc: u64 = 0;
    let mut j: usize = 0;
    while j < len {
        let idx: usize = len - 1 - j;
        let q: *mut u8 = dig_at(p, base, idx);
        let b: u8 = dig_read(q);
        acc = acc.wrapping_mul(31).wrapping_add(b as u64);
        j = j + 1;
    }"""

U_MOVPTR = """    let mut run: u64 = 0;
    let mut i: usize = 0;
    let mut w: *mut u8 = p;
    while i < len {
        run = run.wrapping_add(v_get_unchecked(v, off + i) ^ MIX);
        dig_write(w, (run >> 24) as u8);
        w = unsafe { w.add(1) };
        i = i + 1;
    }
    let mut acc: u64 = 0;
    let mut j: usize = 0;
    let mut q: *mut u8 = unsafe { p.add(len) };
    while j < len {
        q = unsafe { q.sub(1) };
        acc = acc.wrapping_mul(31).wrapping_add(dig_read(q) as u64);
        j = j + 1;
    }"""

U_ENDPTR = """    let mut run: u64 = 0;
    let mut i: usize = 0;
    let mut w: *mut u8 = p;
    let wend: *mut u8 = dig_at(p, base, len);
    while w != wend {
        run = run.wrapping_add(v_get_unchecked(v, off + i) ^ MIX);
        dig_write(w, (run >> 24) as u8);
        w = w.with_addr(w.addr() + 1);
        i = i + 1;
    }
    let mut acc: u64 = 0;
    let mut q: *mut u8 = wend;
    while q != p {
        q = q.with_addr(q.addr() - 1);
        acc = acc.wrapping_mul(31).wrapping_add(dig_read(q) as u64);
    }"""

T_SHIP_BODY = """    let mut run: u64 = 0;
    dig.extend(v[off..off + len].iter().map(|&x| {
        run = run.wrapping_add(x ^ MIX);
        (run >> 24) as u8
    }));
    dig.iter()
        .rev()
        .fold(0u64, |a, &b| a.wrapping_mul(31).wrapping_add(b as u64))"""

T_REVFOLD = """    dig.iter()
        .rev()
        .fold(0u64, |a, &b| a.wrapping_mul(31).wrapping_add(b as u64))"""

T_IDXFOLD = """    let mut acc: u64 = 0;
    for i in 0..len {
        acc = acc.wrapping_mul(31).wrapping_add(dig[len - 1 - i] as u64);
    }
    acc"""

T_PUSH = """    let mut run: u64 = 0;
    for i in 0..len {
        run = run.wrapping_add(v[off + i] ^ MIX);
        dig.push((run >> 24) as u8);
    }
    let mut acc: u64 = 0;
    for i in 0..len {
        acc = acc.wrapping_mul(31).wrapping_add(dig[len - 1 - i] as u64);
    }
    acc"""


def sub(src, old, new, tag):
    assert old in src, (f"{tag}: the shipped rung no longer contains the text this "
                        f"variant substitutes -- fix the anchor rather than the assert")
    return src.replace(old, new)


def replace_loops(src, new, tag):
    """Swap out both of the shipped R4's loops, from the first statement of the
    write loop to the last statement of the fold loop."""
    i = src.find(U_LOOPS_HEAD)
    j = src.find(U_LOOPS_TAIL)
    assert i >= 0 and j > i, f"{tag}: cannot find the shipped R4's two loops"
    return src[:i] + new + src[j + len(U_LOOPS_TAIL):]


def variants():
    u = open(os.path.join(PDIR, "unsafe.rs")).read()
    t = open(os.path.join(PDIR, "safe_tuned.rs")).read()
    yield "r4_ship", u
    yield "r4_add", sub(u, "    p.with_addr(base + i)", "    unsafe { p.add(i) }", "r4_add")
    yield "r4_movptr", replace_loops(u, U_MOVPTR, "r4_movptr")
    yield "r4_endptr", replace_loops(u, U_ENDPTR, "r4_endptr")
    yield "r3_ship", t
    yield "r3_revidx", sub(t, T_REVFOLD, T_IDXFOLD, "r3_revidx")
    yield "r3_zeroed", sub(sub(t, "let mut dig: Vec<u8> = Vec::with_capacity(len);",
                               "let mut dig: Vec<u8> = vec![0u8; len];", "r3_zeroed"),
                           "    dig.extend(", "    dig.clear();\n    dig.extend(", "r3_zeroed")
    yield "r3_push", sub(t, T_SHIP_BODY, T_PUSH, "r3_push")


def reiter(src, n, dst):
    b = bytearray(open(src, "rb").read())
    struct.pack_into("<Q", b, 0, n)
    open(dst, "wb").write(bytes(b))


def marginal(binary, inp):
    """(Ir at 200 iterations - Ir at 100 iterations) / 100, the project's
    convention. Whole-program, so it is symbol-independent."""
    tot = []
    for n in (100, 200):
        f = os.path.join(OUT, f"it{n}.bin")
        reiter(inp, n, f)
        cg = os.path.join(OUT, "cg.out")
        subprocess.run([VALGRIND, "--tool=callgrind", f"--callgrind-out-file={cg}",
                        binary, f], capture_output=True, timeout=3600)
        s = [l for l in open(cg) if l.startswith("summary:")]
        tot.append(int(s[0].split()[1]))
        os.remove(cg)
    return (tot[1] - tot[0]) / 100.0


def main():
    os.makedirs(OUT, exist_ok=True)
    inputs = [("small", os.path.join(PDIR, "inputs", "small.bin")),
              ("large", os.path.join(PDIR, "inputs", "large.bin"))]
    ref = {}
    rows = []
    for name, src in variants():
        p = os.path.join(OUT, f"{name}.rs")
        open(p, "w").write(src)
        b = os.path.join(OUT, name)
        r = subprocess.run([RUSTC] + RFLAGS + [p, "-o", b],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name:12s} BUILD FAILED\n{r.stderr[-800:]}")
            return 1
        ok = True
        for label, f in inputs:
            out = subprocess.run([b, f], capture_output=True, text=True).stdout.strip()
            ref.setdefault(label, out)
            if out != ref[label]:
                print(f"{name:12s} {label}: checksum {out} != shipped {ref[label]}")
                ok = False
        if not ok:
            return 1
        rows.append((name, b))
        print(f"{name:12s} built, checksums agree with the shipped rungs")

    if "--measure" not in sys.argv:
        print("\n(pass --measure for the callgrind marginals)")
        return 0
    print("\nmarginal Ir/call, -O3, inline mode `isolated`, whole-program")
    print(f"{'variant':12s} {'small (win=97)':>16s} {'large (win=4096)':>18s}")
    for name, b in rows:
        vals = [marginal(b, f) for _, f in inputs]
        print(f"{name:12s} {vals[0]:16.2f} {vals[1]:18.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
