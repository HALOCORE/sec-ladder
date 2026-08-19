#!/usr/bin/env python3
"""Generate p11's controls into `.temp/p11/controls/`.

    python3 patterns/p11-nul-scan/controls/gen_controls.py

**Why this file exists.** `.memory/05-layout.md` item 11: a Verus source that
does not verify cleanly, and any rung variant that is not a shipped cell, cannot
live in the pattern directory — `check.py` requires every `.rs` beside the rungs
to be a pinned, cleanly-verifying cell and `build.py`'s `--cell` list is closed.
`.memory/02-bench-rules.md` additionally records the failure this shape prevents:
p16's §10a.2 laws were measured on sources that existed only in a gitignored
`.temp/` directory, so they were not reproducible from the tree at all.
`patterns/*/controls/*.py` is inside `source_sha256`, so this file is hashed.

**Derived, never transcribed.** Every control is a shipped rung with a small
number of *exact-string* substitutions, each asserted to hit exactly once. A
control therefore cannot silently drift from the rung it is a respelling of: if
someone edits `unsafe.rs`, either the substitution still applies and the control
moves with it, or the assertion fires and this script fails loudly.

**`#[path]` is rewritten** to `../../../common/driver.rs`, which from
`.temp/p11/controls/` resolves to the real, hashed `common/driver.rs`. p08's
generator originally left the shipped path in place, where it resolved to a
gitignored *copy* under `.temp/common/` and only compiled by luck
(`.memory/02-bench-rules.md`, closed at TASK_022).

Nothing here is built by `harness/build.py`, nothing here is a p11 cell, and no
number in `results/` comes from any of it.

--------------------------------------------------------------------------
WHAT EACH CONTROL IS
--------------------------------------------------------------------------

**The R3 spelling spread — four in-contract respellings.**
`.memory/01-ladder.md` finding 3: never publish a safety-cost claim without R3,
and never without the *best* in-contract R3 anyone can find — this project has
published a spelling's cost as safety's cost three times. On p11 the spread is
not a detail, it *is* the pattern: the scan is deliberately **not** pinned (each
rung reaches its own library), so the declaration leaves the largest single term
free on purpose.

  * `r3_position`  — `rest.iter().position(|&b| b == 0)` instead of
                     `CStr::from_bytes_until_nul`. A scalar byte loop rather than
                     `core::slice::memchr`. NOTES.md §2 has both rates.
  * `r3_takewhile` — `rest.iter().take_while(|&&b| b != 0).count()`, a third
                     spelling of the same thing.
  * `r3_idxfold`   — the shipped scan with an **indexed** fold loop, so the two
                     loops can be changed one at a time
                     (`.memory/01-ladder.md` finding 4's rule: a whole-kernel
                     delta attributes nothing).
  * `r3_nowin`     — the shipped rung without the once-per-call window reslice,
                     indexing `buf[off + p .. off + len]` instead.

**The one-loop-at-a-time decomposition, on the unsafe side.** R2 − R4 is a
whole-kernel delta and attributes nothing. These two change exactly one loop of
R4 to R2's spelling and nothing else:

  * `u_safescan`   — R4's fold, R2's **scan** (`buf[off + q]`).
  * `u_safefold`   — R4's scan, R2's **fold** (`buf[off + i]`).

**The fused control, OUT OF CONTRACT, which prices the split.** `u_fused` and
`k_fused.c` put the fold inside the scan. They are what ../spec.md's
`idiom.required[0]` forbids, they delete `slen` as a value, and they exist to
answer "what does keeping the two loops separate cost?" with a number instead of
an assertion. They are also the falsifier for §1: they have *fewer* backward
branches than every shipped rung, which is how "the split survives -O3" is
checked rather than assumed.

**The C variants.**

  * `k_byteloop.c` — R1 with the scan written out as a byte loop instead of
                     `strlen`. It exists to show that R1's libcall is **not**
                     something the rung was handed by being spelled a special
                     way: clang's loop-idiom recognition rewrites this file's
                     hand-written loop back into `call strlen@plt`, and gcc does
                     not. NOTES.md §1.
  * `k_fused.c`    — the fused scan+fold in C, out of contract, for the same
                     reason as `u_fused`.

**The R4 side, and the rule that governs it.** `.memory/01-ladder.md`: *a rung
covered by an `identity` pin is chained to the prover*, and TASK_026 §0 item 3
makes running `verus_run.py` on an R5 twin a **precondition** of differencing any
unsafe-side variant. So every R4 candidate here ships with a twin, including the
one expected to pass — TASK_026_REVIEW measured that p07's "both candidates were
put through Verus" was false for exactly this reason.

  * `r4_forfold` + `r4_forfold_twin` — the fold loop as `for i in p..q`. In
    contract (the declaration pins the Horner *operation*, not the loop form).
    Expected to be ACCEPTED.
  * `r4_ptr` + `r4_ptr_twin` — `as_ptr()` / `add()`. Expected to be REJECTED:
    both are `is not supported` at the pinned vstd on p05 and p16, and NOTES.md
    §10b re-measures it on p11's own twin rather than inheriting the verdict.
  * `r4_cstr` + `r4_cstr_twin` — **the important one on this pattern.** R4 is
    defined by *permission*, so an R4 may use `CStr::from_bytes_until_nul` for
    the scan exactly as R3 does, and it would then be half the instructions. The
    twin is what decides whether it is a rung. NOTES.md §10b: this is
    `.memory/01-ladder.md`'s "a rung covered by an `identity` pin is chained to
    the prover" with the largest gap the project has measured behind it.

**The proof mutants — three, and each must FAIL.** A green Verus run proves
nothing on its own (`.memory/04-verus.md`).

  * `m1_weak_requires` — `i < v@.len()` weakened to `i <= v@.len()` in the
    trusted item **and** its twin. Verus alone still passes it; the **twin**
    config is what fails, which is the one thing the twin uniquely catches.
  * `m2_unbounded_scan` — the `q >= len` arm deleted from the **spec** function
    `scan_end`, i.e. `strlen`'s definition. It fails on `decreases`, which is
    the sharpest statement of what R1's bug is: *a scan with no bound is a
    recursion with no termination argument.*
  * `m3_exec_offbyone` — the exec scan bound `while q < len` widened to
    `while q < len + 1`, i.e. R1's bug written into R5. It fails on
    `get_unchecked`'s precondition.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p11", "controls")

SHIPPED_PATH = '#[path = "../../common/driver.rs"]'
CONTROL_PATH = '#[path = "../../../common/driver.rs"]'


def sub(text, pairs, label):
    """Exact-string substitution with an asserted hit count per pair."""
    for old, new, want in pairs:
        got = text.count(old)
        if got != want:
            raise SystemExit(
                f"gen_controls.py: {label}: expected {want} occurrence(s) of\n"
                f"---\n{old}\n---\nbut found {got}. The shipped rung has been "
                f"edited; fix this substitution rather than the assertion.")
        text = text.replace(old, new)
    return text


def rust(name, base, pairs, banner):
    src = open(os.path.join(PDIR, base)).read()
    src = sub(src, [(SHIPPED_PATH, CONTROL_PATH, 1)] + pairs, name)
    body = f"//! p11 CONTROL `{name}` -- derived from `{base}` by\n" \
           f"//! `controls/gen_controls.py`. NOT a p11 rung.\n//!\n" \
           + "".join(f"//! {l}\n" for l in banner.strip().split("\n")) + "\n" \
           + "#![allow(unused_imports)]\n" + src
    path = os.path.join(OUT, name + ".rs")
    open(path, "w").write(body)
    return path


def c(name, base, pairs, banner):
    src = open(os.path.join(PDIR, "c", base)).read()
    src = sub(src, pairs, name)
    body = (f"/* p11 CONTROL {name} -- derived from c/{base} by\n"
            f" * controls/gen_controls.py. NOT a p11 rung.\n *\n"
            + "".join(f" * {l}\n" for l in banner.strip().split("\n"))
            + " */\n" + src)
    path = os.path.join(OUT, name + ".c")
    open(path, "w").write(body)
    return path


# ---- verbatim spans of the shipped rungs ------------------------------------
R3_SCAN = """        let q: usize = p + match CStr::from_bytes_until_nul(rest) {
            Ok(c) => c.to_bytes().len(),
            Err(_) => rest.len(),
        };"""
R3_FOLD = """        let h: u64 = w[p..q]
            .iter()
            .fold(0u64, |h, &b| h.wrapping_mul(31).wrapping_add(b as u64));"""

R4_SCAN = """        while q < len {
            if unsafe { *buf.get_unchecked(off + q) } == 0 {
                break;
            }
            q = q + 1;
        }"""
R4_FOLD = """        while i < q {
            h = h.wrapping_mul(31).wrapping_add(unsafe { *buf.get_unchecked(off + i) } as u64);
            i = i + 1;
        }"""
R2_SCAN = """        while q < len {
            if buf[off + q] == 0 {
                break;
            }
            q = q + 1;
        }"""
R2_FOLD = """        while i < q {
            h = h.wrapping_mul(31).wrapping_add(buf[off + i] as u64);
            i = i + 1;
        }"""

C_SCAN_FOLD = """        q = p + strlen((const char *)(buf + off + p));
        slen = q - p;
        for (i = p; i < q; i++)
            h = h * 31 + (uint64_t)buf[off + i];"""


def main():
    os.makedirs(OUT, exist_ok=True)
    made = []

    # -------------------------------------------------- R3 respellings ------
    made.append(rust(
        "r3_position", "safe_tuned.rs",
        [(R3_SCAN,
          """        let q: usize = p + match rest.iter().position(|&b| b == 0) {
            Some(k) => k,
            None => rest.len(),
        };""", 1)],
        "IN CONTRACT. The scan as `iter().position`, which does NOT reach\n"
        "core::slice::memchr: it is a 5-instruction scalar byte loop. This is\n"
        "the control behind NOTES.md 2's claim that the R1-vs-R3 gap is a\n"
        "library difference -- two safe spellings of one rung, 5.3x apart."))
    made.append(rust(
        "r3_takewhile", "safe_tuned.rs",
        [(R3_SCAN,
          "        let q: usize = p + rest.iter().take_while(|&&b| b != 0).count();", 1)],
        "IN CONTRACT. A third spelling of the same scan."))
    made.append(rust(
        "r3_idxfold", "safe_tuned.rs",
        [(R3_FOLD,
          """        let mut h: u64 = 0;
        let mut i: usize = p;
        while i < q {
            h = h.wrapping_mul(31).wrapping_add(w[i] as u64);
            i = i + 1;
        }""", 1)],
        "IN CONTRACT. The shipped SCAN with an indexed FOLD, so the two loops\n"
        "can be changed one at a time -- `.memory/01-ladder.md` finding 4: a\n"
        "whole-kernel delta attributes nothing."))
    made.append(rust(
        "r3_nowin", "safe_tuned.rs",
        [("    let w: &[u8] = &buf[off..off + len];", "", 1),
         ("    let nstr: usize = w[0] as usize + 256 * (w[1] as usize)\n"
          "        + 65536 * (w[2] as usize) + 16777216 * (w[3] as usize);",
          "    let nstr: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)\n"
          "        + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);", 1),
         ("        let rest: &[u8] = &w[p..];",
          "        let rest: &[u8] = &buf[off + p..off + len];", 1),
         (R3_FOLD,
          """        let h: u64 = buf[off + p..off + q]
            .iter()
            .fold(0u64, |h, &b| h.wrapping_mul(31).wrapping_add(b as u64));""", 1)],
        "IN CONTRACT. The shipped rung without the once-per-call window\n"
        "reslice: every span is taken out of `buf` at `off + ..` instead."))

    # ------------------------------- one loop at a time, R4 -> R2 -----------
    made.append(rust(
        "u_safescan", "unsafe.rs", [(R4_SCAN, R2_SCAN, 1)],
        "DECOMPOSITION CONTROL, not a rung. R4 with ONLY the scan loop's read\n"
        "made checked. u_safescan - unsafe is the scan's share of R2 - R4."))
    made.append(rust(
        "u_safefold", "unsafe.rs", [(R4_FOLD, R2_FOLD, 1)],
        "DECOMPOSITION CONTROL, not a rung. R4 with ONLY the fold loop's read\n"
        "made checked. The two controls must sum to R2 - R4 or there is an\n"
        "interaction term, which is the check `.memory/01-ladder.md` finding 4\n"
        "requires and p16's and p02's decompositions both passed."))

    # ------------------------------------------- the fused control ----------
    made.append(rust(
        "u_fused", "unsafe.rs",
        [(R4_SCAN + """
        let slen: usize = q - p;
        let mut h: u64 = 0;
        let mut i: usize = p;
""" + R4_FOLD,
          """        let mut h: u64 = 0;
        while q < len {
            let b: u8 = unsafe { *buf.get_unchecked(off + q) };
            if b == 0 {
                break;
            }
            h = h.wrapping_mul(31).wrapping_add(b as u64);
            q = q + 1;
        }
        let slen: usize = q - p;""", 1)],
        "OUT OF CONTRACT, and here to price the declaration. The fold is moved\n"
        "INSIDE the scan, which is what idiom.required[0] forbids: `slen` stops\n"
        "being a value the kernel computes and the strlen/memchr idiom is\n"
        "foreclosed. It is also the falsifier for NOTES.md 1 -- it has FEWER\n"
        "backward branches than every shipped rung, which is how the claim\n"
        "'the split survives -O3' is checked rather than asserted."))

    # ---------------------------------------------------- C variants --------
    made.append(c(
        "k_byteloop", "kernel.c",
        [(C_SCAN_FOLD,
          """        q = p;
        while (buf[off + q] != 0)
            q++;
        slen = q - p;
        for (i = p; i < q; i++)
            h = h * 31 + (uint64_t)buf[off + i];""", 1),
         ("#include <string.h>\n\n", "", 1)],
        "R1 with the scan written out as a byte loop and no libcall anywhere in\n"
        "the source. CLANG REWRITES IT BACK INTO `call strlen@plt` by\n"
        "loop-idiom recognition; gcc keeps the byte loop at 3 Ir/byte. So R1's\n"
        "libcall is not an advantage handed to it by spelling. NOTES.md 1."))
    made.append(c(
        "k_fused", "kernel.c",
        [(C_SCAN_FOLD,
          """        q = p;
        while (buf[off + q] != 0) {
            h = h * 31 + (uint64_t)buf[off + q];
            q++;
        }
        slen = q - p;""", 1),
         ("#include <string.h>\n\n", "", 1)],
        "OUT OF CONTRACT. The C fused scan+fold, the counterpart of u_fused."))

    # ------------------------------------------------- R4 candidates --------
    R4_FORFOLD = """        let mut i: usize = p;
""" + R4_FOLD
    made.append(rust(
        "r4_forfold", "unsafe.rs",
        [(R4_FORFOLD,
          """        for i in p..q {
            h = h.wrapping_mul(31).wrapping_add(unsafe { *buf.get_unchecked(off + i) } as u64);
        }""", 1)],
        "IN CONTRACT R4 CANDIDATE. The fold loop as a range `for`, which is the\n"
        "loop form R3 writes -- the declaration pins the Horner OPERATION, not\n"
        "the loop shape. Its twin is r4_forfold_twin and it must verify before\n"
        "this number may be differenced (TASK_026 SS0 item 3)."))
    made.append(rust(
        "r4_ptr", "unsafe.rs",
        [(R4_SCAN,
          """        let bp: *const u8 = buf.as_ptr();
        while q < len {
            if unsafe { *bp.add(off + q) } == 0 {
                break;
            }
            q = q + 1;
        }""", 1)],
        "EXISTS TO BE REJECTED. `as_ptr` and `add` are `is not supported` at\n"
        "the pinned vstd on p05, p16 and p07; NOTES.md 10b re-measures that on\n"
        "p11's own twin rather than inheriting it, because an R4 with no\n"
        "verifying R5 twin is not a rung (`.memory/01-ladder.md`)."))

    CSTR_SCAN = """        let rest: &[u8] = &buf[off + p..off + len];
        let q: usize = p + match std::ffi::CStr::from_bytes_until_nul(rest) {
            Ok(c) => c.to_bytes().len(),
            Err(_) => rest.len(),
        };"""
    made.append(rust(
        "r4_cstr", "unsafe.rs",
        [("""        let mut q: usize = p;
""" + R4_SCAN, CSTR_SCAN, 1)],
        "R4 CANDIDATE, and the one that matters. R4 is defined by PERMISSION,\n"
        "so an unsafe rung may use the standard library's bounded NUL search for\n"
        "the scan exactly as R3 does and keep `get_unchecked` for the fold. It is\n"
        "the cheapest unsafe-side spelling anybody has written on this pattern.\n"
        "Whether it is a RUNG is decided by r4_cstr_twin, not by this number."))

    # ------------------------------------------------- the R5 twins ---------
    V_SCAN = """        while q < len
            invariant_except_break
                p <= q <= len,
                4 <= len,
                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                scan_end(buf@, off as int, len as int, q as int) == scan_end(
                    buf@,
                    off as int,
                    len as int,
                    p as int,
                ),
            ensures
                p <= q <= len,
                q as int == scan_end(buf@, off as int, len as int, p as int),
            decreases len - q,
        {
            if get_unchecked(buf, off + q) == 0 {
                break;
            }
            q = q + 1;
        }"""
    V_FOLD_HEAD = """        let mut i: usize = p;
        // "The fold from here is the whole fold."
        while i < q
            invariant
                p <= i <= q,"""
    made.append(rust(
        "r4_forfold_twin", "verus.rs",
        [(V_FOLD_HEAD,
          """        // TASK_033: the fold loop as a range `for`, i.e. r4_forfold's spelling.
        // Verus derives `p <= i` and the `decreases` for a range `for`, so both
        // go; `i <= q` stays because the invariant references it.
        for i in p..q
            invariant""", 1),
         ("""                fold_str(buf@, off as int, i as int, q as int, h) == fold_str(
                    buf@,
                    off as int,
                    p as int,
                    q as int,
                    0,
                ),
            decreases q - i,
        {
            h = h.wrapping_mul(31).wrapping_add(get_unchecked(buf, off + i) as u64);
            i = i + 1;
        }""",
          """                fold_str(buf@, off as int, i as int, q as int, h) == fold_str(
                    buf@,
                    off as int,
                    p as int,
                    q as int,
                    0,
                ),
        {
            h = h.wrapping_mul(31).wrapping_add(get_unchecked(buf, off + i) as u64);
        }""", 1)],
        "THE R5 TWIN OF r4_forfold, and unlike r4_ptr_twin it exists to be\n"
        "ACCEPTED. `./verus_run.py .temp/p11/controls/r4_forfold_twin.rs`;\n"
        "NOTES.md 10b quotes the count."))
    made.append(rust(
        "r4_ptr_twin", "verus.rs",
        [(V_SCAN,
          """        let bp: *const u8 = buf.as_ptr();
        while q < len
            invariant_except_break
                p <= q <= len,
                4 <= len,
                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                scan_end(buf@, off as int, len as int, q as int) == scan_end(
                    buf@,
                    off as int,
                    len as int,
                    p as int,
                ),
            ensures
                p <= q <= len,
                q as int == scan_end(buf@, off as int, len as int, p as int),
            decreases len - q,
        {
            if unsafe { *bp.add(off + q) } == 0 {
                break;
            }
            q = q + 1;
        }""", 1)],
        "THE R5 TWIN OF r4_ptr, and it exists to be REJECTED. Run it with\n"
        "`./verus_run.py .temp/p11/controls/r4_ptr_twin.rs`; NOTES.md 10b\n"
        "quotes the error. `is not supported` disqualifies an R4 candidate\n"
        "because it forces a NEW TRUSTED ITEM; `postcondition not satisfied`\n"
        "would not."))

    made.append(rust(
        "r4_cstr_twin", "verus.rs",
        [("""        let mut q: usize = p;
        // "The scan from here is the whole scan." There is no closed form for
        // where a NUL scan stops -- the path is the data -- so this is the only
        // shape the invariant can take, and it is p16's.
""" + V_SCAN,
          """        let rest: &[u8] = &buf[off + p..off + len];
        let q: usize = p + match std::ffi::CStr::from_bytes_until_nul(rest) {
            Ok(c) => c.to_bytes().len(),
            Err(_) => rest.len(),
        };
        assume(q as int == scan_end(buf@, off as int, len as int, p as int));
        assume(p <= q <= len);""", 1)],
        "THE R5 TWIN OF r4_cstr. Note the two `assume`s: they are there so that\n"
        "the ONLY thing this file can fail on is whether Verus can compile the\n"
        "`CStr` call at all. If it still fails, the failure is a missing vstd\n"
        "feature and not a missing proof -- which is exactly the distinction\n"
        "`.memory/01-ladder.md` says decides admissibility. An `assume` would be\n"
        "unsound in a shipped rung; this is a control that exists to be REJECTED\n"
        "and it is generated into `.temp/`, never into the pattern directory."))

    # ------------------------------------------------- proof mutants --------
    made.append(rust(
        "m1_weak_requires", "verus.rs",
        [("""fn get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),""",
          """fn get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i <= v@.len(),""", 1),
         ("""fn slb_twin_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),""",
          """fn slb_twin_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i <= v@.len(),""", 1)],
        "MUTANT 1, and it MUST FAIL -- but only under `--cfg slb_twin`. The\n"
        "trusted precondition is weakened by one character in BOTH the item and\n"
        "its twin, so the signatures still match and plain Verus is happy: the\n"
        "shipped config verifies. R5's trusted base then axiomatises that\n"
        "reading one byte past the end of a slice is defined, which is CWE-125,\n"
        "the bug class p11 exists to model. The twin is the only mechanism in\n"
        "the project that catches it (`.memory/04-verus.md`)."))
    made.append(rust(
        "m2_unbounded_scan", "verus.rs",
        [("""pub open spec fn scan_end(buf: Seq<u8>, off: int, len: int, q: int) -> int
    decreases len - q,
{
    if q >= len {
        len
    } else if buf[off + q] == 0 {""",
          """pub open spec fn scan_end(buf: Seq<u8>, off: int, len: int, q: int) -> int
    decreases len - q,
{
    if buf[off + q] == 0 {""", 1),
         ("""        q
    } else {
        scan_end(buf, off, len, q + 1)
    }
}""",
          """        q
    } else {
        scan_end(buf, off, len, q + 1)
    }
}
// (the `q >= len` arm is gone: this is `strlen`.)""", 1)],
        "MUTANT 2, and it MUST FAIL. The `q >= len` arm is deleted from the SPEC\n"
        "function, which turns `scan_end` into `strlen` -- R1's scan, exactly.\n"
        "It fails on `decreases`, and that is the sharpest statement of what\n"
        "this pattern's bug is: A SCAN WITH NO BOUND IS A RECURSION WITH NO\n"
        "TERMINATION ARGUMENT. `.memory/04-verus.md` records p16's `decreases`\n"
        "catching a hang with no test run; this is the same mechanism aimed at\n"
        "the specification rather than at the code."))
    made.append(rust(
        "m3_exec_offbyone", "verus.rs",
        [("""        let mut q: usize = p;
        // "The scan from here is the whole scan." There is no closed form for
        // where a NUL scan stops -- the path is the data -- so this is the only
        // shape the invariant can take, and it is p16's.
        while q < len""",
          """        let mut q: usize = p;
        // MUTANT: the scan bound widened by one -- R1's bug, in R5.
        while q < len + 1""", 1)],
        "MUTANT 3, and it MUST FAIL. The exec scan bound is widened by one, i.e.\n"
        "R1's over-read written into the verified rung. It fails on\n"
        "`get_unchecked`'s precondition, which is the obligation that carries\n"
        "p11's whole memory-safety claim."))

    for p in made:
        print("  wrote", os.path.relpath(p, REPO))
    print(f"\n{len(made)} control(s) in {os.path.relpath(OUT, REPO)}/")
    print("\nbuild and measure them with .temp/p11/run_controls.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
