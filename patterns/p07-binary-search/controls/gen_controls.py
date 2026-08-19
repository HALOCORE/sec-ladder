#!/usr/bin/env python3
"""Generate p07's controls into `.temp/p07/controls/`.

    python3 patterns/p07-binary-search/controls/gen_controls.py

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
`.temp/p07/controls/` resolves to the real, hashed `common/driver.rs`. p08's
generator originally left the shipped path in place, where it resolved to a
gitignored *copy* under `.temp/common/` and only compiled by luck
(`.memory/02-bench-rules.md`, closed at TASK_022).

Nothing here is built by `harness/build.py`, nothing here is a p07 cell, and no
number in `results/` comes from any of it.

--------------------------------------------------------------------------
WHAT EACH CONTROL IS
--------------------------------------------------------------------------

**The branchless pair — MANDATORY, not optional.** This box has
`perf_event_paranoid = 3` and therefore no branch-miss counter
(`.memory/00-environment.md`), so the only way to say anything about branch
misprediction is to build the counterfactual. `u_cmov.rs` and `s_cmov.rs` are
`unsafe.rs` and `safe_tuned.rs` with the *ordering* test — the unpredictable one
— replaced by a `cmov`-shaped select, and with the `v == key` early exit kept
identical. The equality test is predictable-not-taken (it fires once per hit,
i.e. once per ~9 or ~18 probes); the ordering test is a coin flip at every
level. So the pair differs in exactly the branch the pattern is about.
`NOTES.md` §11 confirms `cmov` in the disassembly rather than assuming it, and
states what the inference rests on.

**The R3 spelling spread.** `.memory/01-ladder.md` finding 3: never publish a
safety-cost claim without R3, and never without the *best* in-contract R3
anyone can find — this project has published a spelling's cost as safety's cost
three times. `r3_getunwrap`, `r3_prefix` and `r3_splitat` are three further
in-contract ways to move the four per-byte checks of a u32 read into one; they
keep `let ep: usize = off + 8 + 4 * mid;`, both `if v` comparisons, the midpoint,
the half-open bounds and the written-out decode, i.e. every `idiom.required`
entry. `r3_win` is **out of contract** and is here to show what the declaration
is worth: it hoists `&buf[off..off + len]` once per call and indexes
window-relative, which deletes the `off + 8 + 4 * mid` the declaration pins.

**The R4 side.** `.memory/01-ladder.md`: *a rung covered by an `identity` pin is
chained to the prover*, and TASK_026 §0 item 3 makes running `verus_run.py` on
an R5 twin a precondition of differencing any unsafe-side variant. `r4_for`
swaps the query `while` for a `for`, which is what R2/R3 write and is in
contract. `r4_ptr` uses `as_ptr()`/`add()`/`read()` and exists to be *rejected*:
`NOTES.md` §10b runs its twin through Verus and quotes the error text, because
`is not supported` is what disqualifies and `postcondition not satisfied` is not.

**The C variants for §6, which are the pattern's two other bugs.**

  * `k_incl.c` — the textbook INCLUSIVE binary search: `hi = n - 1`,
    `while (lo <= hi)`, `hi = mid - 1`. This is the spelling `idiom.required`
    excludes, and the reason is that it underflows `size_t` at `mid == 0`, which
    any key below element 0 reaches **on well-formed input**. It is built from
    `c/kernel_hardened.c` — i.e. it has the length check — so what it does on
    `small.bin` is not about the missing check at all.
  * `k_incl_nozero.c` — the same, with the `n == 0` guard removed, which is the
    OTHER underflow site TASK_026 named (`hi = n - 1` at `n == 0`). Run on
    `adversarial-zero.bin`.
  * `k_u32.c` — the length check written in **unsigned 32-bit**:
    `if ((uint32_t)(4 * n + 4 * nq) > (uint32_t)avail)`. p07's `n`/`nq` are u32
    fields, so `4*n + 4*nq` needs 36 bits and this wraps. Contrast p05, whose
    u16 dimensions keep `nrow*ncol` inside `uint32_t` so that only its *signed*
    spelling breaks.
  * `k_i32.c` — the same check in **signed 32-bit**, which is p05's bug shape,
    for the side-by-side table in `NOTES.md` §6.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p07", "controls")

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
    body = f"//! p07 CONTROL `{name}` -- derived from `{base}` by\n" \
           f"//! `controls/gen_controls.py`. NOT a p07 rung.\n//!\n" \
           + "".join(f"//! {l}\n" for l in banner.strip().split("\n")) + "\n" + src
    path = os.path.join(OUT, name + ".rs")
    open(path, "w").write(body)
    return path


def c(name, base, pairs, banner):
    src = open(os.path.join(PDIR, "c", base)).read()
    src = sub(src, pairs, name)
    body = (f"/* p07 CONTROL {name} -- derived from c/{base} by\n"
            f" * controls/gen_controls.py. NOT a p07 rung.\n *\n"
            + "".join(f" * {l}\n" for l in banner.strip().split("\n"))
            + " */\n" + src)
    path = os.path.join(OUT, name + ".c")
    open(path, "w").write(body)
    return path


# ---- the branchy ordering test, verbatim from unsafe.rs / safe_tuned.rs -----
BRANCHY = """            if v < key {
                lo = mid + 1;
            } else {
                hi = mid;
            }"""

# ...and the branchless replacement. Written as two `if`-expressions rather than
# as arithmetic (`lo += (v < key) as usize * (mid + 1 - lo)`) because a select is
# what LLVM lowers to `cmov`; NOTES.md 11 confirms it in the disassembly instead
# of assuming it, which is what `.memory/00-environment.md` requires on a box
# with no branch-miss counter.
BRANCHLESS = """            let lt: bool = v < key;
            lo = if lt { mid + 1 } else { lo };
            hi = if lt { hi } else { mid };"""

# ...and a second branchless spelling that is branchless BY CONSTRUCTION rather
# than by asking for a select: two's-complement masking, which has no `if` for
# LLVM to re-materialise. It measures exactly the shipped rung too, which is
# what makes NOTES.md 11a a claim about the PASS and not about one spelling.
BRANCHLESS_MASK = """            let m: usize = ((v < key) as usize).wrapping_neg();
            lo = (lo & !m) | ((mid + 1) & m);
            hi = (hi & m) | (mid & !m);"""


def main():
    os.makedirs(OUT, exist_ok=True)
    made = []

    # ---------------------------------------------------------- branchless --
    made.append(rust(
        "u_cmov", "unsafe.rs", [(BRANCHY, BRANCHLESS, 1)],
        "R4 with the UNPREDICTABLE branch replaced by a select. The `v == key`\n"
        "early exit is untouched, so the two differ in exactly the coin-flip\n"
        "test. The branch-misprediction control this box cannot measure\n"
        "directly (perf_event_paranoid = 3, no counters)."))
    made.append(rust(
        "u_mask", "unsafe.rs", [(BRANCHY, BRANCHLESS_MASK, 1)],
        "R4 with the ordering test made branchless by MASKING rather than by a\n"
        "select -- no `if` at all, so there is nothing for LLVM to convert back.\n"
        "It converts it back anyway: 0 cmov, and exactly R4's Ir. NOTES.md 11a."))
    made.append(rust(
        "s_cmov", "safe_tuned.rs", [(BRANCHY, BRANCHLESS, 1)],
        "R3 with the same substitution, so the branchless comparison exists on\n"
        "the safe side too and the inference is not a statement about `unsafe`."))

    # ------------------------------------------------------- R3 respellings --
    R3_RESLICE = "            let ew: &[u8] = &buf[ep..ep + 4];"
    made.append(rust(
        "r3_getunwrap", "safe_tuned.rs",
        [(R3_RESLICE, "            let ew: &[u8] = buf.get(ep..ep + 4).unwrap();", 1)],
        "In contract. The same one-check-per-probe reslice through `get`."))
    made.append(rust(
        "r3_prefix", "safe_tuned.rs",
        [(R3_RESLICE, "            let ew: &[u8] = &buf[ep..][..4];", 1)],
        "In contract. Two reslices instead of one range."))
    made.append(rust(
        "r3_splitat", "safe_tuned.rs",
        [(R3_RESLICE, "            let (ew, _rest): (&[u8], &[u8]) = buf[ep..].split_at(4);", 1)],
        "In contract. `split_at` consumes the slice; `.memory/01-ladder.md`\n"
        "records that the consuming forms keep winning on other patterns."))
    made.append(rust(
        "r3_win", "safe_tuned.rs",
        [("    let hdr: &[u8] = &buf[off..off + 8];",
          "    let win: &[u8] = &buf[off..off + len];\n"
          "    let hdr: &[u8] = &win[0..8];", 1),
         ("        let kp: usize = off + 8 + 4 * n + 4 * q;\n"
          "        let kw: &[u8] = &buf[kp..kp + 4];",
          "        let kp: usize = 8 + 4 * n + 4 * q;\n"
          "        let kw: &[u8] = &win[kp..kp + 4];", 1),
         ("            let ep: usize = off + 8 + 4 * mid;\n" + R3_RESLICE,
          "            let ep: usize = 8 + 4 * mid;\n"
          "            let ew: &[u8] = &win[ep..ep + 4];", 1)],
        "OUT OF CONTRACT, and it is here to price the declaration. The window\n"
        "is resliced once per call and every index is window-relative, which\n"
        "deletes the `off + 8 + 4 * mid` that idiom.required[7] pins."))

    # -------------------------------------------------------- R4 variants ---
    made.append(rust(
        "r4_for", "unsafe.rs",
        [("    let mut q: usize = 0;\n    while q < nq {", "    for q in 0..nq {", 1),
         ("        acc = acc.wrapping_mul(31).wrapping_add(found.wrapping_add(1));\n"
          "        q = q + 1;\n    }",
          "        acc = acc.wrapping_mul(31).wrapping_add(found.wrapping_add(1));\n"
          "    }", 1)],
        "In contract. The query loop as a `for`, which is what R2 and R3 write.\n"
        "The only degree of freedom the declaration leaves on the R4 side that\n"
        "does not need a vstd feature."))
    made.append(rust(
        "r4_ptr", "unsafe.rs",
        [("            let v: u32 = unsafe { *buf.get_unchecked(ep) } as u32\n"
          "                + 256 * (unsafe { *buf.get_unchecked(ep + 1) } as u32)\n"
          "                + 65536 * (unsafe { *buf.get_unchecked(ep + 2) } as u32)\n"
          "                + 16777216 * (unsafe { *buf.get_unchecked(ep + 3) } as u32);",
          "            let p: *const u8 = buf.as_ptr();\n"
          "            let v: u32 = unsafe { *p.add(ep) } as u32\n"
          "                + 256 * (unsafe { *p.add(ep + 1) } as u32)\n"
          "                + 65536 * (unsafe { *p.add(ep + 2) } as u32)\n"
          "                + 16777216 * (unsafe { *p.add(ep + 3) } as u32);", 1)],
        "EXISTS TO BE REJECTED. `as_ptr` and `add` are `is not supported` at the\n"
        "pinned vstd on p05 and p16; NOTES.md 10b re-measures that on p07's own\n"
        "twin rather than inheriting it, because an R4 with no verifying R5\n"
        "twin is not a rung (`.memory/01-ladder.md`)."))

    # ------------------------------------------- the R5 twin of an R4 --------
    # `.memory/01-ladder.md`: a rung covered by an `identity` pin is chained to
    # the prover, so an R4 candidate is not a rung until its R5 twin verifies.
    # This is the twin for `r4_ptr`, and NOTES.md 10b quotes what Verus says
    # about it. Derived from the SHIPPED verus.rs, same substitution discipline.
    PTR_OLD = """            let v: u32 = get_unchecked(buf, ep) as u32 + 256 * (get_unchecked(
                buf,
                ep + 1,
            ) as u32) + 65536 * (get_unchecked(buf, ep + 2) as u32) + 16777216 * (
            get_unchecked(buf, ep + 3) as u32);"""
    PTR_NEW = """            let p: *const u8 = buf.as_ptr();
            let v: u32 = unsafe { *p.add(ep) } as u32 + 256 * (unsafe { *p.add(ep + 1) } as u32)
                + 65536 * (unsafe { *p.add(ep + 2) } as u32)
                + 16777216 * (unsafe { *p.add(ep + 3) } as u32);"""
    made.append(rust(
        "r4_ptr_twin", "verus.rs", [(PTR_OLD, PTR_NEW, 1)],
        "THE R5 TWIN OF r4_ptr, and it exists to be REJECTED. Run it with\n"
        "`./verus_run.py .temp/p07/controls/r4_ptr_twin.rs`; NOTES.md 10b quotes\n"
        "the error. `is not supported` disqualifies an R4 candidate because it\n"
        "forces a NEW TRUSTED ITEM; `postcondition not satisfied` would not."))

    # ---------------------------------------------------------- C variants --
    INCL_BRANCHY = """        size_t lo = 0;
        size_t hi = n;
        uint64_t found = UINT64_MAX;
        while (lo < hi) {
            size_t mid = lo + (hi - lo) / 2;"""
    INCL_NEW = """        size_t lo = 0;
        size_t hi = n - 1;
        uint64_t found = UINT64_MAX;
        while (lo <= hi) {
            size_t mid = lo + (hi - lo) / 2;"""
    INCL_TAIL = """            if (v < key)
                lo = mid + 1;
            else
                hi = mid;"""
    INCL_TAIL_NEW = """            if (v < key)
                lo = mid + 1;
            else
                hi = mid - 1;"""
    made.append(c(
        "k_incl", "kernel_hardened.c",
        [(INCL_BRANCHY, INCL_NEW, 1), (INCL_TAIL, INCL_TAIL_NEW, 1)],
        "The TEXTBOOK INCLUSIVE spelling, built from the HARDENED kernel so the\n"
        "length check is present and nothing here is about the missing check.\n"
        "`hi = mid - 1` underflows size_t at mid == 0, which any key below\n"
        "element 0 reaches. Run it on small.bin -- well-formed input, no\n"
        "attacker."))
    made.append(c(
        "k_incl_nozero", "kernel_hardened.c",
        [(INCL_BRANCHY, INCL_NEW, 1), (INCL_TAIL, INCL_TAIL_NEW, 1),
         ("    if (n == 0 || nq == 0)\n        return 0;\n", "", 1)],
        "The same, with the zero guard removed: the OTHER underflow site,\n"
        "`hi = n - 1` at n == 0. Run it on adversarial-zero.bin."))
    made.append(c(
        "k_u32", "kernel_hardened.c",
        [("    if (4 * n + 4 * nq > avail)",
          "    if ((uint32_t)(4 * n + 4 * nq) > (uint32_t)avail)", 1)],
        "The length check in UNSIGNED 32-bit. 4*n + 4*nq needs 36 bits because\n"
        "n and nq are u32 fields, so this wraps -- and p05's does NOT, because\n"
        "its dimensions are u16. Run it on adversarial-width.bin."))
    made.append(c(
        "k_i32", "kernel_hardened.c",
        [("    if (4 * n + 4 * nq > avail)",
          "    if ((int)(4 * n + 4 * nq) > (int)avail)", 1)],
        "The same in SIGNED 32-bit, which is p05's bug shape. Undefined\n"
        "behaviour rather than merely wrong; here for the side-by-side table."))

    for p in made:
        print("  wrote", os.path.relpath(p, REPO))
    print(f"\n{len(made)} control(s) in {os.path.relpath(OUT, REPO)}/")
    print("\nbuild and measure them with .temp/p07/build_controls.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
