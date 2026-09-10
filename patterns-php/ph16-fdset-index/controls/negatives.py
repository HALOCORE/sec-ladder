#!/usr/bin/env python3
"""ph16 -- the Verus mutants, and every one of them MUST FAIL to verify.

    python3 patterns-php/ph16-fdset-index/controls/negatives.py
    python3 patterns-php/ph16-fdset-index/controls/negatives.py --emit noguard

`../verus.rs` verifies `15 verified, 0 errors`, and `.memory/04-verus.md`'s
standing warning is that a green count says nothing on its own: a tautological
`ensures`, a deleted `requires` on an `external_body` wrapper and a kernel whose
body is `0u64` all verify. **The only defence is mutation.**

Six mutants, each a one-edit change to `../verus.rs` written into
`.temp/php25/negatives/` and run through Verus. Five MUST FAIL; one MUST PASS
and is the must-NOT-fire control.

    noguard      delete `if w < NW` -- i.e. delete `99e290f882c9` guard (b),
                 which is the ONE line every unchecked store in this row rests
                 on. ⭐ THIS IS THE ROW: with it gone `aset_unchecked` has no
                 precondition and the rung IS `c/kernel.c:541`.
    nomaxfd      delete the `if max_fd >= FD_SETSIZE` clamp -- guard (c). The
                 memory-safety obligations are untouched, so if this one
                 verified the postcondition would not be watching `max_fd` at
                 all and a third of R1h would be undefended by the proof.
    weakreq      weaken `aset_unchecked`'s `requires i < NW` to `true`. It is
                 the shape `.memory/04-verus.md` names: a trusted item whose
                 precondition is gone verifies with the SAME count and every
                 caller's obligation silently disappears. ⚠ So the mutant is
                 detected NOT by the kernel failing but by the twin --
                 `slb_twin_aset_unchecked`, which must meet the same contract
                 with a SAFE body -- and that is what this row's three twins are
                 for. If Verus reports no error, this control reports FAIL.
    wrongwalk    `walk` steps `i + 2` instead of `i + 1`, i.e. the spec skips
                 every other entry. The exec code is untouched. A proof that
                 still verified would mean the postcondition is not pinning what
                 the loop does.
    tautology    replace the kernel's `ensures` with `r == r`. ⭐ IT MUST
                 **FAIL**, AND THE FIRST DRAFT OF THIS FILE PREDICTED THE
                 OPPOSITE. `.memory/04-verus.md` warns that a tautological
                 `ensures` verifies with the same green count and no
                 diagnostic; on THIS row it does not, because `main`'s
                 `assert(r == fdset_fold(...))` CONSUMES the postcondition and
                 has nothing left to discharge it with. Measured: `14 verified,
                 1 errors`, and the error is in the driver's `while` loop, not
                 in the kernel. **So the consuming assert is load-bearing here
                 and is not decoration** -- which is the claim its own comment
                 makes, now with a number.
    tautology-un the same edit PLUS deleting `main`'s consuming assert. THIS is
                 the vacuity baseline and it MUST VERIFY: it is what
                 `.memory/04-verus.md` says a green count is worth on its own.
                 ⚠ Reported as the must-NOT-fire case of this file, not as a
                 pass to be proud of.
    zerobody     the kernel returns `0u64` and nothing else, with the shipped
                 `ensures` kept. MUST FAIL -- if it verified, the postcondition
                 would be satisfiable without computing anything.

⚠ `--emit <name>` writes one mutant and does not run it, for a human to read.

A run that cannot evaluate says so and exits non-zero.
"""

import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
SCRATCH = os.path.join(REPO, ".temp", "php25", "negatives")
VERUS_RUN = os.path.join(REPO, "verus_run.py")
ENV = {k: v for k, v in os.environ.items() if k != "LD_PRELOAD"}


def _sub(src, old, new, label):
    if old not in src:
        raise KeyError(f"{label}: the text this mutant edits is not in "
                       f"verus.rs any more:\n    {old[:80]}...")
    return src.replace(old, new, 1)


MUTANTS = {}


def mutant(name, must_verify=False):
    def deco(fn):
        MUTANTS[name] = (fn, must_verify)
        return fn
    return deco


@mutant("noguard")
def m_noguard(src):
    return _sub(src,
        """                if w < NW {             // 99e290f882c9 guard (b)
                    aset_unchecked(fds, w, aget_unchecked(fds, w) | (1u64 << (this_fd % 64)));
                }""",
        """                {
                    aset_unchecked(fds, w, aget_unchecked(fds, w) | (1u64 << (this_fd % 64)));
                }""",
        "noguard")


@mutant("nomaxfd")
def m_nomaxfd(src):
    return _sub(src,
        """    if max_fd >= FD_SETSIZE {
        max_fd = FD_SETSIZE - 1;
    }""",
        """    if false {
        max_fd = FD_SETSIZE - 1;
    }""",
        "nomaxfd")


@mutant("weakreq")
def m_weakreq(src):
    src = _sub(src,
        """fn aset_unchecked(a: &mut [u64; NW], i: usize, x: u64)
    requires
        i < NW,""",
        """fn aset_unchecked(a: &mut [u64; NW], i: usize, x: u64)
    requires
        true,""",
        "weakreq (trusted item)")
    return _sub(src,
        """fn slb_twin_aset_unchecked(a: &mut [u64; NW], i: usize, x: u64)
    requires
        i < NW,""",
        """fn slb_twin_aset_unchecked(a: &mut [u64; NW], i: usize, x: u64)
    requires
        true,""",
        "weakreq (twin)")


@mutant("wrongwalk")
def m_wrongwalk(src):
    src = _sub(src, "walk(win, base, i + 1, n, fds2, mx2)",
               "walk(win, base, i + 2, n, fds2, mx2)", "wrongwalk a")
    return _sub(src, "walk(win, base, i + 1, n, fds, mx)",
                "walk(win, base, i + 2, n, fds, mx)", "wrongwalk b")


def _tautologise(src):
    return _sub(src,
        """    ensures
        r == fdset_fold(buf@, off as int, len as int),
{""",
        """    ensures
        r == r,
{""",
        "tautology")


@mutant("tautology")
def m_tautology(src):
    return _tautologise(src)


@mutant("tautology-un", must_verify=True)
def m_tautology_un(src):
    src = _tautologise(src)
    return _sub(src,
        "            assert(r == fdset_fold(buf@, (k * stride) as int, stride as int));\n",
        "",
        "tautology-un (drop the consuming assert)")


@mutant("zerobody")
def m_zerobody(src):
    i = src.index("pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)")
    j = src.index("\n// ------", i)
    head = src[i:src.index("{", src.index("ensures", i))]
    return src[:i] + head + "{\n    0u64\n}\n" + src[j:]


def run_verus(path, twin=False):
    cmd = [sys.executable, VERUS_RUN, path] + (["--cfg", "slb_twin"] if twin else [])
    r = subprocess.run(cmd, capture_output=True, text=True, env=ENV, cwd=REPO,
                       timeout=3600)
    out = r.stdout + r.stderr
    m = re.search(r"(\d+) verified, (\d+) errors", out)
    if not m:
        return None, out.strip()[-400:]
    return (int(m.group(1)), int(m.group(2))), out.strip()[-400:]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--emit", choices=sorted(MUTANTS))
    ap.add_argument("--only", choices=sorted(MUTANTS))
    args = ap.parse_args()

    if not os.path.exists(VERUS_RUN):
        print(f"CANNOT EVALUATE: no verus_run.py at {VERUS_RUN}")
        return 2
    os.makedirs(SCRATCH, exist_ok=True)
    src = open(os.path.join(ROW, "verus.rs")).read()

    # ⚠ `#[path = "../../common/driver.rs"]` is resolved relative to the FILE,
    # so a mutant written three levels deeper cannot find the driver. Rewrite
    # the path to an absolute one; it is outside `verus!` and unverified either
    # way, so nothing about the proof moves.
    drv = os.path.join(REPO, "common", "driver.rs")
    src = src.replace('#[path = "../../common/driver.rs"]', f'#[path = "{drv}"]')

    if args.emit:
        p = os.path.join(SCRATCH, f"{args.emit}.rs")
        open(p, "w").write(MUTANTS[args.emit][0](src))
        print(f"wrote {p} -- NOT run")
        return 0

    # must-NOT-fire, first: the UNMUTATED source, path-rewritten, still
    # verifies. Without it a mutant that failed for a path error would read as
    # a pass.
    base = os.path.join(SCRATCH, "baseline.rs")
    open(base, "w").write(src)
    got, log = run_verus(base)
    print(f"  must-NOT-fire  {'baseline':11s} {got}  "
          f"{'PASS' if got and got[1] == 0 else 'FAIL'}")
    if not (got and got[1] == 0):
        print(f"CANNOT EVALUATE: the unmutated copy does not verify:\n{log}")
        return 2

    bad = 0
    names = [args.only] if args.only else list(MUTANTS)
    for name in names:
        fn, must_verify = MUTANTS[name]
        p = os.path.join(SCRATCH, f"{name}.rs")
        try:
            open(p, "w").write(fn(src))
        except KeyError as e:
            print(f"  CANNOT EVALUATE  {name}: {e}")
            bad += 1
            continue
        # `weakreq` is detected by the TWIN, so it is run in twin mode.
        twin = (name == "weakreq")
        got, log = run_verus(p, twin=twin)
        if got is None:
            print(f"  CANNOT EVALUATE  {name}: verus printed no verdict\n{log}")
            bad += 1
            continue
        v, e = got
        if must_verify:
            okd = (e == 0)
            tag = "must-VERIFY"
        else:
            okd = (e > 0)
            tag = "must-FAIL"
        print(f"  {tag:14s} {name:11s} {v} verified, {e} errors"
              + ("  [--cfg slb_twin]" if twin else "")
              + f"  {'PASS' if okd else 'FAIL'}")
        if not okd:
            bad += 1
            print(f"      {log[-300:]}")

    print("\nRESULT:", "FAIL" if bad else "PASS", f"({bad} problem(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
