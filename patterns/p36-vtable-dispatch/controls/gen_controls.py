#!/usr/bin/env python3
"""p36 controls: derive every variant from a SHIPPED rung by exact-string
substitution, build it, run it, and report `Ir` per call.

⚠ **Every control is DERIVED, never hand-copied**, and every substitution
asserts its own hit count, so a control cannot silently drift from the rung it
is a variant of (`.memory/05-layout.md` item 11). Sources land under
`.temp/p36/controls/`, binaries under `.temp/p36/controls/bin/`, and the
binaries are deletable -- this file rebuilds them.

    python3 patterns/p36-vtable-dispatch/controls/gen_controls.py --list
    python3 patterns/p36-vtable-dispatch/controls/gen_controls.py --write
    python3 patterns/p36-vtable-dispatch/controls/gen_controls.py --run r_fnptr
    python3 patterns/p36-vtable-dispatch/controls/gen_controls.py --run all

The controls, and what each answers:

  r_fnptr     R4 with a bare `[fn(u64) -> u64; NOPS]` table -- C's own
              mechanism. **Not an admissible rung** (`--verus` prints the
              error), so its number is the price of the prover, not a rung.
  r_match     R3 with `match op { .. }` -- the IDIOMATIC safe-Rust spelling.
              Not a rung either: it devirtualises AND inlines, so it is a
              different program with a different cost model.
  c_switch    the same edit on the C side.
  r4_cursor   R4 with the per-record cursor test restored -- the R2-shaped
              unsafe rung every other pattern here ships. An R4-SIDE lever, and
              the one that decided what p36 ships: it verifies, and it is
              1022 / 8190 Ir/call DEARER.
  r4_reslice  R4 plus R3's single reslice, so it and R3 differ in NOTHING but
              the bounds checks -- the matched-spelling pair, +10.00 flat, and
              since TASK_073 a VERIFIED R4 (`--verus`, `v_r4_reslice`).
  r3_idx      R3 with R2's per-record cursor test -- R3-SIDE lever 1, dear.
  r3_window   R3 with the WINDOW resliced once at the top -- R3-SIDE lever 2,
              and **cheaper than the shipped R3** (1702 / 13350 against
              1710 / 13358), in contract and with zero `unsafe`. Landed at
              TASK_073 on TASK_072_REVIEW B1, which found that p36 had searched
              the R4 side and not the R3 side.
  r3_hdr4     the header alone resliced -- R3-SIDE lever 3, 1704 / 13352.
  r3_iter     r3_window plus `chunks_exact(2)` -- R3-SIDE lever 4, 1705 / 13353,
              i.e. the iterator spelling buys nothing here.
  r2_nodead   R2 with the (dead) table bounds check removed by `get_unchecked`
              ONLY on the table, so the two halves of R4's win separate.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p36", "controls")
BIN = os.path.join(OUT, "bin")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
GCC = "/usr/bin/gcc"
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CG_ANN = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")
VERUS_RUN = os.path.join(REPO, "verus_run.py")

sys.path.insert(0, os.path.join(REPO, "harness"))
import asm  # noqa: E402
import measure as measuremod  # noqa: E402

RUST_FLAGS = ["-C", "opt-level=3", "-C", "debug-assertions=off",
              "-C", "codegen-units=1", "--cfg", "slb_isolated"]
C_FLAGS = ["-std=c99", "-Wall", "-Wextra", "-O3", "-DSLB_ISOLATED"]


def sub(text, old, new, n=1):
    """Exact-string substitution that asserts its own hit count."""
    got = text.count(old)
    if got != n:
        raise SystemExit(f"gen_controls.py: expected {n} occurrence(s) of\n"
                         f"  {old!r}\nfound {got}. A shipped rung moved; fix "
                         f"this generator rather than the control.")
    return text.replace(old, new)


# ------------------------------------------------------------------ rungs ----
def rung(name):
    return open(os.path.join(PDIR, name)).read()


# --------------------------------------------------------------- controls ----
FN_TABLE = """pub trait Op {
    fn apply(&self, x: u64) -> u64;
}

fn fop0(x: u64) -> u64 { x ^ 0x9e3779b97f4a7c15 }
fn fop1(x: u64) -> u64 { x ^ 0xff51afd7ed558ccd }
fn fop2(x: u64) -> u64 { x.wrapping_add(0x2545f4914f6cdd1d) }
fn fop3(x: u64) -> u64 { x.wrapping_add(0xc4ceb9fe1a85ec53) }
fn fop4(x: u64) -> u64 { x.wrapping_sub(0x61c8864680b583eb) }
fn fop5(x: u64) -> u64 { x.wrapping_sub(0xbf58476d1ce4e5b9) }
fn fop6(x: u64) -> u64 { x ^ 0x94d049bb133111eb }
fn fop7(x: u64) -> u64 { x.wrapping_add(0x9e6c63d0676a9a99) }

const TABLE: [fn(u64) -> u64; NOPS] =
    [fop0, fop1, fop2, fop3, fop4, fop5, fop6, fop7];
"""

MATCH_ARM = """        if op < NOPS {
            let x = acc ^ arg;
            acc = match op {
                0 => x ^ 0x9e3779b97f4a7c15,
                1 => x ^ 0xff51afd7ed558ccd,
                2 => x.wrapping_add(0x2545f4914f6cdd1d),
                3 => x.wrapping_add(0xc4ceb9fe1a85ec53),
                4 => x.wrapping_sub(0x61c8864680b583eb),
                5 => x.wrapping_sub(0xbf58476d1ce4e5b9),
                6 => x ^ 0x94d049bb133111eb,
                _ => x.wrapping_add(0x9e6c63d0676a9a99),
            };
        } else {"""

C_SWITCH_ARM = """        if (op < SLB_P36_NOPS) {
            uint64_t x = acc ^ (uint64_t)arg;
            switch (op) {
            case 0: acc = x ^ 0x9e3779b97f4a7c15ULL; break;
            case 1: acc = x ^ 0xff51afd7ed558ccdULL; break;
            case 2: acc = x + 0x2545f4914f6cdd1dULL; break;
            case 3: acc = x + 0xc4ceb9fe1a85ec53ULL; break;
            case 4: acc = x - 0x61c8864680b583ebULL; break;
            case 5: acc = x - 0xbf58476d1ce4e5b9ULL; break;
            case 6: acc = x ^ 0x94d049bb133111ebULL; break;
            default: acc = x + 0x9e6c63d0676a9a99ULL; break;
            }
        } else"""


def _tab_block(src):
    """The whole `pub trait Op { .. } .. const TABLE .. ];` block of a rung."""
    i = src.index("pub trait Op {")
    j = src.index("const TABLE: [&'static dyn Op; NOPS] =")
    j = src.index("];", j) + 3
    return src[i:j]


def c_r_fnptr():
    """R4 with C's own mechanism: a bare `fn(u64) -> u64` table."""
    s = rung("unsafe.rs")
    s = sub(s, _tab_block(s), FN_TABLE)
    s = sub(s, "fn tab_get_unchecked(i: usize) -> &'static dyn Op {\n"
               "    unsafe { *TABLE.get_unchecked(i) }\n}",
               "fn tab_get_unchecked(i: usize) -> fn(u64) -> u64 {\n"
               "    unsafe { *TABLE.get_unchecked(i) }\n}")
    s = sub(s, "acc = tab_get_unchecked(op).apply(acc ^ arg);",
               "acc = (tab_get_unchecked(op))(acc ^ arg);")
    return s


def c_r_match():
    """R3 with the idiomatic `match` spelling. Devirtualises and inlines."""
    s = rung("safe_tuned.rs")
    s = sub(s, _tab_block(s), "")
    s = sub(s, "        if op < NOPS {\n"
               "            acc = TABLE[op].apply(acc ^ arg);\n"
               "        } else {", MATCH_ARM)
    return s


def c_c_switch():
    """c/kernel_hardened.c with `switch (op)` instead of the table."""
    s = open(os.path.join(PDIR, "c", "kernel_hardened.c")).read()
    s = sub(s, "        if (op < SLB_P36_NOPS)\n"
               "            acc = TABLE[op](acc ^ (uint64_t)arg);\n"
               "        else", C_SWITCH_ARM)
    # the table is now unused; keep it alive so the comparison is of the LOOP
    s = sub(s, "SLB_NOINLINE uint64_t kernel(",
               "const void *slb_p36_keep_table(void) { return (const void *)TABLE; }\n\n"
               "SLB_NOINLINE uint64_t kernel(")
    return s


def c_r4_cursor():
    """R4-SIDE LEVER 1, and the one that decided what ships: the R2-shaped
    unsafe rung, i.e. R4 with the per-record `len - p < 2` cursor test restored
    and the hoisted count removed. It is what every other pattern in this tree
    ships as its R4, it VERIFIES as an R5 twin, and it is 1022 / 8190 Ir per
    call DEARER than the shipped R4. Shipping it would have made p36 publish
    *safe Rust beats unsafe Rust* from a loop-structure difference."""
    s = rung("unsafe.rs")
    s = sub(s, """    let room: usize = (len - 4) / 2;
    let nw: usize = if nrec < room { nrec } else { room };
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut t: usize = 0;
    while t < nw {
        let op: usize = buf_get_unchecked(buf, off + p) as usize;""",
        """    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut t: usize = 0;
    while t < nrec {
        if len - p < 2 {
            break;
        }
        let op: usize = buf_get_unchecked(buf, off + p) as usize;""")
    return s


def c_r4_reslice():
    """R4-SIDE LEVER 2: the shipped R4 plus R3's single reslice, so R3 and this
    control differ in NOTHING but the bounds checks. Its difference from R3 is
    the MATCHED-SPELLING safety number (`.tasks/TASK_026.md` §0.1): **+10.00
    flat**, and that is the number ../NOTES.md 8b publishes as such.

    ⚠ **THIS DOCSTRING AND ../NOTES.md 8b USED TO NAME DIFFERENT NUMBERS AS
    "the matched-spelling difference" IN ONE COMMIT** -- this one +10, NOTES.md
    the shipped `R3ship - R4ship` = +15 -- and the headline shipped was the
    larger (TASK_072_REVIEW B1). This one was right and NOTES.md's was wrong:
    the shipped R4 carries a second induction variable `p` and indexes
    `buf[off + p]`, where R3 indexes `rec[2 * t]` into a reslice, so R3ship and
    R4ship are NOT the same loop written twice. `r4_reslice` is. Since TASK_073
    it is also a VERIFIED R4 (`v_r4_reslice`, `12 verified, 0 errors`), so the
    +10 is admissible-to-admissible."""
    s = rung("unsafe.rs")
    s = sub(s, """    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut t: usize = 0;
    while t < nw {
        let op: usize = buf_get_unchecked(buf, off + p) as usize;
        let arg: u64 = buf_get_unchecked(buf, off + p + 1) as u64;
        p = p + 2;""",
        """    let rec: &[u8] = &buf[off + 4..off + 4 + 2 * nw];
    let mut acc: u64 = 0;
    let mut t: usize = 0;
    while t < nw {
        let op: usize = buf_get_unchecked(rec, 2 * t) as usize;
        let arg: u64 = buf_get_unchecked(rec, 2 * t + 1) as u64;""")
    return s


# The header block every R3-side lever below rewrites, quoted once so the three
# substitutions cannot drift apart.
_R3_HDR = """    let nrec: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);
    if nrec == 0 {
        return 0;
    }
    // The hoisted record count: the same records the per-record cursor test
    // would have admitted, computed once.
    let room: usize = (len - 4) / 2;
    let nw: usize = if nrec < room { nrec } else { room };
    let rec: &[u8] = &buf[off + 4..off + 4 + 2 * nw];"""


def c_r3_window():
    """R3-SIDE LEVER 2, **CHEAPER THAN THE SHIPPED R3** (TASK_072_REVIEW B1,
    landed at TASK_073): reslice the WINDOW once at the top and index the header
    inside it, so `w.len() == len >= 4` is visible and LLVM collapses the four
    separate `off + k < buf.len()` header checks into the single reslice test.

    `13.00000*nrw + 38` against the shipped R3's `13.00000*nrw + 46` -- 1702 /
    13350 against 1710 / 13358, **identical checksums on both blobs, zero
    `unsafe`, and in contract**: all 11 required backticked rust spellings match
    exactly as the shipped R3 does and no forbidden spelling is hit
    (`controls/r3_contract.py`, which uses the gate's own
    `check.py::spelling_matches`).

    ⚠ **The SLOPE does not move: 13.00000 in both.** The whole R3-side spread is
    prologue, i.e. per call and zero per record, which is why the shipped rung
    was kept and the SPAN published instead of reshipping -- ../NOTES.md 8b."""
    return sub(rung("safe_tuned.rs"), _R3_HDR,
               """    let w: &[u8] = &buf[off..off + len];
    let nrec: usize = w[0] as usize + 256 * (w[1] as usize)
        + 65536 * (w[2] as usize) + 16777216 * (w[3] as usize);
    if nrec == 0 {
        return 0;
    }
    // The hoisted record count: the same records the per-record cursor test
    // would have admitted, computed once.
    let room: usize = (len - 4) / 2;
    let nw: usize = if nrec < room { nrec } else { room };
    let rec: &[u8] = &w[4..4 + 2 * nw];""")


def c_r3_hdr4():
    """R3-SIDE LEVER 3: reslice ONLY the four header bytes, leaving the record
    reslice exactly as shipped. It isolates the lever `r3_window` pulls -- one
    bounds check on the header instead of four -- and lands at
    `13.00000*nrw + 40` (1704 / 13352), two dearer than `r3_window` because the
    record reslice is still measured against `buf` rather than against `w`."""
    return sub(rung("safe_tuned.rs"), _R3_HDR,
               """    let h: &[u8] = &buf[off..off + 4];
    let nrec: usize = h[0] as usize + 256 * (h[1] as usize)
        + 65536 * (h[2] as usize) + 16777216 * (h[3] as usize);
    if nrec == 0 {
        return 0;
    }
    // The hoisted record count: the same records the per-record cursor test
    // would have admitted, computed once.
    let room: usize = (len - 4) / 2;
    let nw: usize = if nrec < room { nrec } else { room };
    let rec: &[u8] = &buf[off + 4..off + 4 + 2 * nw];""")


def c_r3_iter():
    """R3-SIDE LEVER 4: `r3_window` plus an iterator over the record pairs, so
    the per-record indexing disappears from the source entirely.
    `13.00000*nrw + 41` (1705 / 13353) -- DEARER than `r3_window`, which is the
    useful half of the result: on p36 the iterator spelling buys nothing,
    because R3's loop was already check-free (../NOTES.md 4)."""
    return sub(c_r3_window(), """    let mut acc: u64 = 0;
    let mut t: usize = 0;
    while t < nw {
        let op: usize = rec[2 * t] as usize;
        let arg: u64 = rec[2 * t + 1] as u64;""",
               """    let mut acc: u64 = 0;
    let mut t: usize = 0;
    for c in rec.chunks_exact(2) {
        let op: usize = c[0] as usize;
        let arg: u64 = c[1] as u64;""")


def c_r3_idx():
    """R3-SIDE LEVER 1: R2's per-record cursor test on the tuned rung, i.e. the
    reslice without the hoist. The DEAR end of the R3-side span."""
    s = rung("safe_tuned.rs")
    s = sub(s, """    let room: usize = (len - 4) / 2;
    let nw: usize = if nrec < room { nrec } else { room };
    let rec: &[u8] = &buf[off + 4..off + 4 + 2 * nw];
    let mut acc: u64 = 0;
    let mut t: usize = 0;
    while t < nw {
        let op: usize = rec[2 * t] as usize;
        let arg: u64 = rec[2 * t + 1] as u64;""",
        """    let rec: &[u8] = &buf[off + 4..off + len];
    let mut acc: u64 = 0;
    let mut t: usize = 0;
    while t < nrec {
        if rec.len() < 2 * t + 2 {
            break;
        }
        let op: usize = rec[2 * t] as usize;
        let arg: u64 = rec[2 * t + 1] as u64;""")
    return s


def c_r2_nodead():
    """R2 with ONLY the table access spelled unchecked, so the dead table check
    and the two live window checks separate."""
    s = rung("safe_naive.rs")
    s = sub(s, "acc = TABLE[op].apply(acc ^ arg);",
               "acc = (unsafe { *TABLE.get_unchecked(op) }).apply(acc ^ arg);")
    return s


# ------------------------------------------------- the Verus twins (R4 side) --
# `.tasks/TASK_026.md` §0.3: **run ./verus_run.py on an R5 twin BEFORE
# differencing any unsafe-side variant.** A rung covered by an `identity` pin is
# chained to the prover, so an R4 candidate the pinned vstd/Verus cannot express
# is NOT A RUNG and its number means nothing. Read the ERROR TEXT and not the
# exit code: `is not supported` disqualifies (it forces a new TRUSTED item);
# `postcondition not satisfied` disqualifies nothing.
def v_r4_cursor():
    """The R2-shaped unsafe rung, as an R5 twin. Expected to VERIFY -- it is the
    shape p36 shipped first and it is what makes `r4_cursor` an ADMISSIBLE R4
    rather than a curiosity."""
    s = rung("verus.rs")
    s = sub(s, """    let room: usize = (len - 4) / 2;
    let nw: usize = if nrec < room { nrec } else { room };
    let mut acc: u64 = 0;""", """    let mut acc: u64 = 0;""")
    s = sub(s, "    while t < nw\n        invariant\n",
               "    while t < nrec\n        invariant_except_break\n")
    s = sub(s, """            room == (len - 4) / 2,
            nw <= room,
            nw <= nrec,
""", "")
    s = sub(s, "            t <= nw,\n", "            p <= len,\n            t <= nrec,\n")
    s = sub(s, """        decreases nw - t,
    {
        let op: usize""", """        ensures
            acc.wrapping_mul(31).wrapping_add(t as u64) == run(
                buf@,
                off as int,
                len as int,
                0,
                nrec as int,
                4,
                0,
            ),
        decreases nrec - t,
    {
        if len - p < 2 {
            break;
        }
        let op: usize""")
    return s


def v_r4_reslice():
    """`r4_reslice`, as an R5 twin. **Built at TASK_073, on TASK_072_REVIEW M1.**

    ../NOTES.md 8b and 11c used to say this twin was NOT built -- *"it needs
    `vstd::slice::slice_subrange` and the subrange-indexing proof that goes with
    it, which is real work this task did not do"* -- so `r4_reslice`'s
    1700 / 13348 was reported and NOT counted in the R4-side span. Measured, the
    proof is four `assert` lines and two `invariant` lines and it verifies
    **first try**: `12 verified, 0 errors`, the same obligation count as the
    shipped R5, and **no new `#[verifier::external_body]` item in this
    pattern** -- the reslice's contract comes from `vstd::slice::slice_subrange`,
    which is `external_body` *inside the pinned vstd*, i.e. in the trusted base
    every pattern in this tree already stands on rather than in p36's own tally.

    So `r4_reslice` IS an admissible R4 and the R4-side span has THREE verified
    members. 1700 / 13348 is interior to 1695...2717 / 13343...21533, so the
    endpoints do not move -- what moves is that `R3ship - r4_reslice` is now an
    admissible-to-admissible MATCHED-SPELLING pair at `+10.00 flat`.

    Compiled (`--compile ... -C opt-level=3 --cfg slb_isolated`) it is
    `md5_fn_norel`-identical to the `r4_reslice` control with equal checksums on
    both blobs; ../NOTES.md 8b has the run."""
    s = rung("verus.rs")
    # 1. the reslice, and drop the exec cursor `p`.
    s = sub(s, """    let nw: usize = if nrec < room { nrec } else { room };
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut t: usize = 0;""",
            """    let nw: usize = if nrec < room { nrec } else { room };
    assert(off + 4 + 2 * nw <= buf@.len()) by {
        assert(2 * nw <= len - 4);
    }
    let rec: &[u8] = vstd::slice::slice_subrange(buf, off + 4, off + 4 + 2 * nw);
    let mut acc: u64 = 0;
    let mut t: usize = 0;""")
    # 2. the invariant: `p` becomes `4 + 2*t`, plus the two subrange facts.
    s = sub(s, """            p == 4 + 2 * t,
            t <= nw,
            run(buf@, off as int, len as int, t as int, nrec as int, p as int, acc) == run(""",
            """            t <= nw,
            rec@ == buf@.subrange(off + 4, off + 4 + 2 * nw),
            rec@.len() == 2 * nw,
            run(buf@, off as int, len as int, t as int, nrec as int, 4 + 2 * t, acc) == run(""")
    # 3. the body: index the reslice, no cursor.
    s = sub(s, """        let op: usize = buf_get_unchecked(buf, off + p) as usize;
        let arg: u64 = buf_get_unchecked(buf, off + p + 1) as u64;
        p = p + 2;""",
            """        assert(rec@[2 * t as int] == buf@[off + 4 + 2 * t]);
        assert(rec@[2 * t as int + 1] == buf@[off + 4 + 2 * t + 1]);
        let op: usize = buf_get_unchecked(rec, 2 * t) as usize;
        let arg: u64 = buf_get_unchecked(rec, 2 * t + 1) as u64;""")
    return s


def v_r_fnptr():
    """The bare `fn`-pointer table, as a Verus twin. Expected to be rejected on
    the DECLARATION."""
    s = rung("verus.rs")
    i = s.index("/// THE OP INTERFACE.")
    j = s.index("// ------------------------------------------------------------------ spec ----")
    s = s[:i] + """pub open spec fn op_spec_of(i: int, x: u64) -> u64 {
    op_spec(i, x)
}

fn fop0(x: u64) -> u64 { x ^ 0x9e3779b97f4a7c15 }

pub const TABLE: [fn(u64) -> u64; NOPS] = [fop0, fop0, fop0, fop0, fop0, fop0, fop0, fop0];

""" + s[j:]
    s = sub(s, """fn tab_get_unchecked(i: usize) -> (r: &'static dyn Op)
    requires
        i < NOPS,
    ensures
        r == TABLE@[i as int],
{
    unsafe { *TABLE.get_unchecked(i) }
}""", """fn tab_get_unchecked(i: usize) -> (r: fn(u64) -> u64)
    requires
        i < NOPS,
    ensures
        r == TABLE@[i as int],
{
    unsafe { *TABLE.get_unchecked(i) }
}""")
    s = sub(s, """fn slb_twin_tab_get_unchecked(i: usize) -> (r: &'static dyn Op)
    requires
        i < NOPS,
    ensures
        r == TABLE@[i as int],
{
    TABLE[i]
}""", """fn slb_twin_tab_get_unchecked(i: usize) -> (r: fn(u64) -> u64)
    requires
        i < NOPS,
    ensures
        r == TABLE@[i as int],
{
    TABLE[i]
}""")
    s = sub(s, "acc = tab_get_unchecked(op).apply(acc ^ arg);",
               "acc = (tab_get_unchecked(op))(acc ^ arg);")
    return s


def v_specfirst():
    """THE VTABLE-SLOT CONTROL (../NOTES.md 5): the shipped `verus.rs` with the
    trait's two items SWAPPED, so the ghost `spec_apply` is declared before the
    exec `apply`.

    It verifies identically (`12 verified, 0 errors`) and produces the SAME 55
    instructions and 170 bytes -- and a DIFFERENT `md5_fn_norel`, because the
    ghost item takes vtable slot 0 and `apply` moves to slot 1: `call
    *0x20(%rcx)` where the shipped rung has `call *0x18(%rcx)`. Compile it with
    `./verus_run.py --compile .temp/p36/controls/v_specfirst.rs -o <out> --cfg
    slb_isolated -C opt-level=3 -C debug-assertions=off -C codegen-units=1` and
    diff the kernel against `.temp/build/p36/unsafe-O3-isolated`."""
    s = rung("verus.rs")
    i = s.index("pub trait Op {")
    j = s.index("/// The eight op types.")
    tr = s[i:j]
    new = tr.replace("""    fn apply(&self, x: u64) -> (r: u64)
        ensures
            r == self.spec_apply(x),
    ;

    spec fn spec_apply(&self, x: u64) -> u64;""",
        """    spec fn spec_apply(&self, x: u64) -> u64;

    fn apply(&self, x: u64) -> (r: u64)
        ensures
            r == self.spec_apply(x),
    ;""")
    if new == tr:
        raise SystemExit("gen_controls.py: verus.rs's trait moved; fix this "
                         "generator rather than the control.")
    return s[:i] + new + s[j:]


VERUS_TWINS = {
    "v_r4_cursor": (v_r4_cursor, "the R2-shaped unsafe rung, as an R5 twin"),
    "v_r4_reslice": (v_r4_reslice, "the matched-spelling R4, as an R5 twin "
                                   "-- TASK_073, on TASK_072_REVIEW M1"),
    "v_specfirst": (v_specfirst, "the trait with the GHOST item declared first "
                                 "-- verifies, and moves the vtable slot"),
    "v_r_fnptr": (v_r_fnptr, "C's bare `fn`-pointer table, as an R5 twin"),
}


def run_verus_twins():
    os.makedirs(OUT, exist_ok=True)
    for name, (fn, desc) in sorted(VERUS_TWINS.items()):
        p = os.path.join(OUT, name + ".rs")
        open(p, "w").write(fn())
        print(f"=== {name}: {desc}")
        print(f"    {os.path.relpath(p, REPO)}")
        r = subprocess.run([sys.executable, VERUS_RUN, p, "--multiple-errors", "20"],
                           capture_output=True, text=True)
        for line in (r.stdout + r.stderr).strip().splitlines():
            print(f"    {line}")
        print(f"    [exit {r.returncode}]")


CONTROLS = {
    "r_fnptr": ("rust", c_r_fnptr),
    "r_match": ("rust", c_r_match),
    "c_switch": ("c", c_c_switch),
    "r4_cursor": ("rust", c_r4_cursor),
    "r4_reslice": ("rust", c_r4_reslice),
    "r3_idx": ("rust", c_r3_idx),
    "r3_window": ("rust", c_r3_window),
    "r3_hdr4": ("rust", c_r3_hdr4),
    "r3_iter": ("rust", c_r3_iter),
    "r2_nodead": ("rust", c_r2_nodead),
}


# ---------------------------------------------------------------- driving ----
def write_all():
    os.makedirs(BIN, exist_ok=True)
    for name, (lang, fn) in sorted(CONTROLS.items()):
        ext = ".rs" if lang == "rust" else ".c"
        p = os.path.join(OUT, name + ext)
        open(p, "w").write(fn())
        print(f"wrote {os.path.relpath(p, REPO)}")


def build(name):
    lang, _ = CONTROLS[name]
    out = os.path.join(BIN, name)
    if lang == "rust":
        src = os.path.join(OUT, name + ".rs")
        cmd = [RUSTC, *RUST_FLAGS, src, "-o", out]
    else:
        src = os.path.join(OUT, name + ".c")
        cmd = [GCC, *C_FLAGS, "-I", os.path.join(REPO, "common"),
               "-I", os.path.join(PDIR, "c"),
               os.path.join(REPO, "common", "driver.c"), src,
               os.path.join(PDIR, "c", "main.c"), "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"{name}: build failed\n{r.stdout}{r.stderr}")
    return out


def ir_per_call(binary, blob, n_calls):
    """Per-function exclusive `Ir` for the kernel symbol, per call.

    ⚠ **It uses `measure.py::_sum_rows`, not a first-match grep.**
    `callgrind_annotate` splits one function across several `file:function`
    rows, so taking the first row understates a kernel whose rows are split --
    which it silently did in this script's first version, printing non-integer
    Ir/call for `r_match` and `c_switch` and integers for everything else. The
    number this file prints must be the same quantity `results/p36-*.json`
    carries or the two cannot be compared at all."""
    cg = os.path.join(BIN, "cg.out")
    subprocess.run([VALGRIND, "--tool=callgrind", f"--callgrind-out-file={cg}",
                    binary, blob], capture_output=True, text=True, check=True)
    ann = subprocess.run([CG_ANN, "--threshold=100", cg],
                         capture_output=True, text=True, check=True).stdout
    tot, names = measuremod._sum_rows(ann, "kernel")
    if tot is None:
        raise SystemExit(f"{binary}: no `kernel` row in callgrind output")
    return tot / n_calls, names


def run(name, blobs):
    src_ext = ".rs" if CONTROLS[name][0] == "rust" else ".c"
    b = build(name)
    k = asm.try_kernel(b)
    print(f"-- {name} ({os.path.relpath(os.path.join(OUT, name + src_ext), REPO)})")
    if k:
        print(f"   n_fn={k.n_fn} n_fn_nopad={k.n_fn_nopad} bytes={len(k.fn_bytes)} "
              f"md5_fn_norel={k.md5_fn_norel}")
        ind = [i.text.strip() for i in k.insns_fn
               if re.match(r"^(call|jmp)q?\s+\*", i.text.strip())]
        print(f"   indirect transfers in the kernel: {ind}")
    for blob, ncalls in blobs:
        path = os.path.join(PDIR, "inputs", blob)
        out = subprocess.run([b, path], capture_output=True, text=True).stdout.strip()
        ir, names = ir_per_call(b, path, ncalls)
        print(f"   {blob:12s} checksum={out:22s} "
              f"Ir/call={ir:12.4f}  rows={names}")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--run", default=None)
    ap.add_argument("--verus", action="store_true",
                    help="derive and run the R4-side Verus twins")
    a = ap.parse_args()
    if a.list:
        for n, (lang, _) in sorted(CONTROLS.items()):
            print(f"  {n:12s} {lang}")
        return 0
    if a.verus:
        run_verus_twins()
        return 0
    write_all()
    if a.write:
        return 0
    blobs = [("small.bin", 20000), ("large.bin", 20000)]
    names = sorted(CONTROLS) if a.run in (None, "all") else [a.run]
    for n in names:
        run(n, blobs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
