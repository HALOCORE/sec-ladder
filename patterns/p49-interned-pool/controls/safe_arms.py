#!/usr/bin/env python3
"""p49 CONTROLS: **three safe-Rust ports of one kernel, and which one you get is
a choice of CONTAINER.**

    python3 patterns/p49-interned-pool/controls/safe_arms.py

WHY THIS EXISTS
---------------
`CLAUDE.md` rule 6 names *"safe Rust reproduces the bug bit-identically"* as a
FINDING and never a kill. **On p49 it is the finding**, and it is the exact
opposite of `p34`, where `Rc::clone` is the only way to publish a second
reference so the bug cannot be written in safe Rust at all.

  A. **the INDEX ARENA** -- `../safe_naive.rs`, the shipped R2. Content lives in
     one `[u8; MEM]` and a record names a byte OFFSET into it. **The alias is an
     integer, so the borrow checker has nothing to say**, and the same
     representation expresses the safe semantics (shipped) and the buggy one
     (`controls/rust_bug.py`) with equal ease.
  B. **`Rc<RefCell<Buf>>`** (`arm_rc_refcell.rs`) -- the idiomatic safe spelling
     of *shared and mutable*. **Reproduces `c/kernel.c` bit for bit**, with no
     `unsafe` anywhere and no panic: the dynamic borrow check passes because
     there is only ever one borrow outstanding.
  C. **`Rc<Buf>` with `Rc::make_mut`** (`arm_rc_makemut.rs`) -- the same program
     with `RefCell` removed. `make_mut` IS copy-on-write, so **the safety line is
     the standard library's** and the bug is not expressible. Reproduces
     `c/kernel_hardened.c` bit for bit.

✅ **B and C differ in ONE TYPE.** That is the result: safe Rust rules the bug
out here by an API choice, not by the type system.

THE rustc-ERROR ARM, AND ITS NEGATIVE CONTROL
---------------------------------------------
⚠ **A rustc error code is not distinguishing unless something shows it is**, and
this project has read one as distinguishing when it was not FOUR times (p25's
E0502, p28's E0382/E0499, p34's E0507). So the arm that writes through a shared
`Rc<Buf>` without `make_mut` is compiled and its error recorded -- **and so is a
NEGATIVE CONTROL that cannot have p49's bug** (no pool, no dedup, no second
referent: one `Rc<i32>` assigned through). If the two produce the same code, the
code says nothing about this pattern, and this control says so in its output
rather than leaving a reader to assume otherwise.

WHAT IT ASSERTS
---------------
  * arm A prints `c/kernel_hardened.c`'s answer on every input;
  * arm B prints `c/kernel.c`'s answer on every input -- **the bug, in safe
    Rust**;
  * arm C prints `c/kernel_hardened.c`'s answer on every input -- **the repair,
    from the standard library**;
  * the `Rc<Buf>` write-through does not compile, and the error code is reported
    beside the negative control's so a reader can see whether it distinguishes.
"""

import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
COMMON = os.path.join(REPO, "common")
CDIR = os.path.join(PDIR, "c")
SCRATCH = os.path.join(REPO, ".temp", "p49ctl", "safe_arms")
sys.path.insert(0, os.path.join(REPO, "harness"))
import build as buildmod  # noqa: E402

RUSTC = os.environ.get("SLB_RUSTC", os.path.expanduser("~/.cargo/bin/rustc"))
GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")

ARMS = {"A_index_arena": os.path.join(PDIR, "safe_naive.rs"),
        "B_rc_refcell": os.path.join(HERE, "arm_rc_refcell.rs"),
        "C_rc_makemut": os.path.join(HERE, "arm_rc_makemut.rs")}
EXPECT = {"A_index_arena": "R1h", "B_rc_refcell": "R1", "C_rc_makemut": "R1h"}

ECODE = re.compile(r"error\[(E\d+)\]")

#: The write-through arm: `Rc<Buf>` without `make_mut`. Written out here rather
#: than shipped as a file, because it does not compile and a source file that
#: cannot be built is a trap for the next reader.
BAD_ARM = """
use std::rc::Rc;
#[derive(Clone)]
pub struct Buf { pub len: u8, pub data: [u8; 6] }
fn main() {
    let b = Rc::new(Buf { len: 2, data: [0u8; 6] });
    let mut recs: Vec<Rc<Buf>> = Vec::new();
    recs.push(Rc::clone(&b));
    recs.push(Rc::clone(&b));
    // p49's write, through a buffer two records name.
    recs[0].data[0] = 0;
    println!("{}", recs[1].data[0]);
}
"""

#: THE NEGATIVE CONTROL. No pool, no dedup, no second referent, no aliasing of
#: any kind -- one `Rc<i32>` assigned through. If rustc gives this the SAME code
#: as the arm above, the code is not about p49.
NEG_ARM = """
use std::rc::Rc;
fn main() {
    let r = Rc::new(5i32);
    *r = 6;
    println!("{}", r);
}
"""


def env():
    e = dict(os.environ)
    e.pop("LD_PRELOAD", None)
    return e


def build_rust(src, out):
    cmd = ([RUSTC] + buildmod.rust_flags("O3", "isolated", "unwind")
           + [src, "-o", out])
    return subprocess.run(cmd, capture_output=True, text=True, timeout=900)


def build_c(kernel, out):
    cmd = [GCC, "-std=c99", "-O3", "-DSLB_ISOLATED", "-I", COMMON, "-I", CDIR,
           os.path.join(COMMON, "driver.c"), os.path.join(CDIR, kernel),
           os.path.join(CDIR, "main.c"), "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise SystemExit(f"safe_arms.py: C build failed:\n{r.stderr}")
    return out


def run(exe, path):
    r = subprocess.run([exe, path], capture_output=True, text=True,
                       timeout=900, env=env())
    return r.stdout.strip()


def derived_from():
    out = {}
    for rel in ("patterns/p49-interned-pool/safe_naive.rs",
                "patterns/p49-interned-pool/c/kernel.c",
                "patterns/p49-interned-pool/c/kernel_hardened.c",
                "patterns/p49-interned-pool/inputs/gen.py",
                "patterns/p49-interned-pool/controls/arm_rc_refcell.rs",
                "patterns/p49-interned-pool/controls/arm_rc_makemut.rs",
                "patterns/p49-interned-pool/controls/safe_arms.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    problems = []
    inputs = sorted(glob.glob(os.path.join(PDIR, "inputs", "*.bin")))
    if not inputs:
        print("safe_arms.py: no .bin files -- run inputs/gen.py first",
              file=sys.stderr)
        return 1

    ref = {"R1": build_c("kernel.c", os.path.join(SCRATCH, "R1")),
           "R1h": build_c("kernel_hardened.c", os.path.join(SCRATCH, "R1h"))}
    exes = {}
    for name, src in ARMS.items():
        out = os.path.join(SCRATCH, name)
        r = build_rust(src, out)
        if r.returncode != 0:
            raise SystemExit(f"safe_arms.py: {name} failed to build:\n"
                             f"{r.stderr[-3000:]}")
        exes[name] = out
        print(f"  built {name:16s} <- {os.path.relpath(src, REPO)}")

    print(f"\n{'input':32s} {'R1 (bug)':>21s} {'R1h (cow)':>21s}  "
          + "  ".join(f"{k:>14s}" for k in ARMS))
    rows = []
    for path in inputs:
        name = os.path.basename(path)
        a = {k: run(ref[k], path) for k in ref}
        b = {k: run(exes[k], path) for k in ARMS}
        rows.append({"input": name, **{f"c_{k}": v for k, v in a.items()},
                     **b})
        print(f"{name:32s} {a['R1']:>21s} {a['R1h']:>21s}  "
              + "  ".join(f"{'==' + EXPECT[k] if b[k] == a[EXPECT[k]] else b[k]:>14s}"
                          for k in ARMS))
        for k in ARMS:
            if b[k] != a[EXPECT[k]]:
                problems.append(
                    f"{name}: arm {k} printed {b[k]} but {EXPECT[k]} printed "
                    f"{a[EXPECT[k]]}. The arm is claimed to reproduce that C "
                    f"rung EXACTLY, and a port that lands somewhere else "
                    f"measures nothing")

    # ---- the rustc-error arm and its negative control ---------------------
    print("\nthe `Rc<Buf>` write-through, and a NEGATIVE CONTROL that cannot "
          "have p49's bug")
    codes = {}
    for label, text in (("Rc<Buf> write-through", BAD_ARM),
                        ("NEGATIVE CONTROL (Rc<i32>)", NEG_ARM)):
        src = os.path.join(SCRATCH, label.split()[0].replace("<", "_")
                           .replace(">", "_") + ".rs")
        open(src, "w").write(text)
        r = build_rust(src, os.path.join(SCRATCH, "bad"))
        m = ECODE.search(r.stderr)
        codes[label] = {"rc": r.returncode, "code": m.group(1) if m else None,
                        "first_line": next((l for l in r.stderr.splitlines()
                                            if l.startswith("error")), "")}
        print(f"    {label:28s} rc={r.returncode} code={codes[label]['code']}")
        print(f"        {codes[label]['first_line']}")
        if r.returncode == 0:
            problems.append(f"{label} COMPILED, which the arm is here to show "
                            f"it does not")
    same = (codes["Rc<Buf> write-through"]["code"]
            == codes["NEGATIVE CONTROL (Rc<i32>)"]["code"])
    print(f"\n  the two error codes are {'THE SAME' if same else 'DIFFERENT'}"
          + ("  <-- so the code is NOT distinguishing, and must not be quoted "
             "as if it were" if same else ""))

    doc = {"pin": {"regenerate": "python3 patterns/p49-interned-pool/controls/"
                                 "safe_arms.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "expect": EXPECT,
           "rows": rows,
           "rustc_errors": codes,
           "error_code_distinguishes": not same,
           "problems": problems,
           "invariant": "Three safe-Rust ports of one kernel: the index arena "
                        "(shipped R2) and `Rc<Buf>` + `Rc::make_mut` both "
                        "reproduce c/kernel_hardened.c exactly, and "
                        "`Rc<RefCell<Buf>>` reproduces c/kernel.c exactly -- so "
                        "SAFE RUST EXPRESSES BOTH THE BUG AND THE REPAIR, and "
                        "the difference between the last two is ONE TYPE. The "
                        "rustc error for a write through a shared `Rc<Buf>` is "
                        "recorded beside a negative control's, because a code "
                        "that both produce says nothing about this pattern."}
    out = os.path.join(HERE, "safe_arms.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
