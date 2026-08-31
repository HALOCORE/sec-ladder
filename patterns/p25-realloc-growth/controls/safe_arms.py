#!/usr/bin/env python3
"""p25 CONTROLS: **what safe Rust does with p25's bug, measured in four arms.**

    python3 patterns/p25-realloc-growth/controls/safe_arms.py

⚠⚠ **`TASK_157` deliverable 4 asks for exactly this, by name:** *"If you claim
safe Rust cannot express this bug, you owe a NEGATIVE CONTROL that cannot have
the bug and must not print the same error."* **It DOES print the same error**, so
the claim this file supports is the narrower and truer one.

  A `arm_safe_ptr.rs`         `&toks[curi]` held across `toks.push(a)`.
                              MUST NOT COMPILE. The error code is recorded.
  B `arm_safe_ptr_nopush.rs`  ATTRIBUTION: A with the ONE push replaced by the
                              SENT fold the same file already writes. MUST
                              COMPILE -- so the diagnostic is caused by the two
                              edited lines and not by the program's shape.
  C `arm_safe_negctl.rs`      **THE NEGATIVE CONTROL.** No container, no growth,
                              no reallocation, no saved interior pointer: twelve
                              lines with a struct and a `&mut`. **It must NOT
                              compile either, and it must print the SAME code.**
                              That is the finding: the code carries no
                              information about interior pointers.
  D `arm_safe_index.rs`       The INDEX port. MUST COMPILE, and on every SHIPPED
                              adversarial window its answer must equal
                              `../model.py::parse_fold` -- i.e. **the safe port
                              does not merely avoid the bug, it does not have
                              one**, because `realloc` copies.

⚠ **What this establishes, stated precisely so nobody can quote it wider.** Safe
Rust cannot spell `c/kernel.c`'s READ, and the port it forces is
`c/kernel_hardened.c`'s answer at zero cost -- **that** is p25's safe-Rust
result. What it does NOT establish, and what arm C exists to stop anybody
claiming, is that `E0502` says anything about this bug class. **Fourth instance
in this project of a rustc code read as distinguishing when it was not** (p25's
own, p28's `E0382`/`E0499`, p34's `E0507`).
"""

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
INDIR = os.path.join(PDIR, "inputs")
TMP = os.path.join(REPO, ".temp", "p25ctl")

RUSTC = os.environ.get("SLB_RUSTC", os.path.expanduser("~/.cargo/bin/rustc"))

sys.path.insert(0, PDIR)
sys.path.insert(0, os.path.join(REPO, "common"))
import model as m25  # noqa: E402
import slb  # noqa: E402

ARMS = [
    ("A", "arm_safe_ptr.rs", False, "the interior pointer across the push"),
    ("B", "arm_safe_ptr_nopush.rs", True, "the same file with the push deleted"),
    ("C", "arm_safe_negctl.rs", False, "THE NEGATIVE CONTROL: no container"),
    ("D", "arm_safe_index.rs", True, "the index port"),
]

ADV = ["adversarial-move.bin", "adversarial-lateread.bin",
       "adversarial-many.bin", "adversarial-nogrow.bin"]

_CODE = re.compile(r"error\[(E\d+)\]")


def compile_arm(src, tag):
    out = os.path.join(TMP, f"safe_{tag}")
    r = subprocess.run([RUSTC, "--edition", "2021", "-C", "opt-level=0",
                        "-C", "debug-assertions=off",
                        os.path.join(HERE, src), "-o", out],
                       capture_output=True, text=True, timeout=900, cwd=REPO)
    codes = sorted(set(_CODE.findall(r.stderr)))
    msg = " ".join(r.stderr.split())
    return r.returncode == 0, codes, msg, out


def window_hex(name):
    """The FIRST window of a shipped blob, as hex. Read from the blob rather
    than re-derived, so arm D is fed the bytes the C rungs were fed."""
    f = slb.read(os.path.join(INDIR, name))
    payload = f.payload[: f.declared_len]
    stride, buf = slb.head1_u64_bytes(payload)
    return buf[:stride].hex(), buf, stride


def derived_from():
    out = {}
    for rel in ["patterns/p25-realloc-growth/model.py",
                "patterns/p25-realloc-growth/inputs/gen.py",
                "patterns/p25-realloc-growth/safe_naive.rs",
                "patterns/p25-realloc-growth/controls/safe_arms.py"] + \
               [f"patterns/p25-realloc-growth/controls/{s}"
                for _, s, _, _ in ARMS]:
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    os.makedirs(TMP, exist_ok=True)
    problems, rows = [], []
    built = {}
    for tag, src, want_ok, what in ARMS:
        ok, codes, msg, out = compile_arm(src, tag)
        built[tag] = out if ok else None
        rows.append({"arm": tag, "source": src, "compiles": ok,
                     "error_codes": codes, "what": what,
                     "diagnostic": msg[:400]})
        print(f"  {tag}  {src:26s} compiles={ok!s:6s} codes={codes} -- {what}")
        if ok != want_ok:
            problems.append(
                f"arm {tag} ({src}): compiles={ok}, expected {want_ok}. "
                + ("A must-fail arm that compiles means safe Rust CAN spell "
                   "this and ../spec.md's safe-Rust paragraph is wrong."
                   if want_ok is False else
                   "A must-compile arm that fails means the attribution or the "
                   "index-port claim is not measurable from this file.")
                + f" rustc said: {msg[:300]}")

    a_codes = set(rows[0]["error_codes"])
    c_codes = set(rows[2]["error_codes"])
    shared = sorted(a_codes & c_codes)
    print(f"\n  arm A codes {sorted(a_codes)} | arm C codes {sorted(c_codes)} "
          f"| SHARED {shared}")
    if not shared:
        problems.append(
            "the negative control (arm C) and the real arm (arm A) print "
            "DISJOINT error codes. That would make the code DISTINGUISHING "
            "after all -- which contradicts ../spec.md, the catalogue and three "
            "earlier instances, and is a finding either way. Do not leave it "
            "unreported: re-read the codes and re-argue the paragraph.")
    else:
        print(f"  => the code(s) {shared} are printed by BOTH, so E0502 carries "
              f"no information about interior pointers. NEGATIVE CONTROL HOLDS.")

    print("\n  arm D vs model.py::parse_fold on the shipped adversarial windows")
    dvals = []
    if built["D"]:
        for name in ADV:
            hexw, buf, stride = window_hex(name)
            r = subprocess.run([built["D"], hexw], capture_output=True,
                               text=True, timeout=600)
            got = r.stdout.strip()
            mod = m25.build(os.path.join(INDIR, name))
            want = str(mod.parse_fold(buf, 0, stride))
            dvals.append({"input": name, "arm_d": got, "parse_fold": want,
                          "agree": got == want})
            print(f"     {name:26s} arm D {got:24s} parse_fold {want:24s} "
                  f"{'AGREE' if got == want else 'DIFFER'}")
            if got != want:
                problems.append(
                    f"{name}: the safe index port printed {got}, model.py's "
                    f"parse_fold says {want}. The index port is supposed to "
                    f"have NO BUG on exactly the windows where R1 reads retired "
                    f"storage -- that is the row's safe-Rust result")
    else:
        problems.append("arm D did not compile, so the index-port claim was "
                        "checked against nothing")

    doc = {"pin": {"regenerate": "python3 patterns/p25-realloc-growth/controls/"
                                 "safe_arms.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "arms": rows,
           "shared_error_codes_A_and_C": shared,
           "index_port_vs_model": dvals,
           "problems": problems,
           "invariant": "The interior-pointer arm does not compile; the same "
                        "file with the push deleted DOES, so the diagnostic is "
                        "attributable; the NEGATIVE CONTROL -- no container, no "
                        "growth, no saved reference -- does not compile either "
                        "and prints the SAME code, so the code carries no "
                        "information; and the index port compiles and agrees "
                        "with model.py::parse_fold on every shipped adversarial "
                        "window, i.e. the safe port has NO BUG rather than a "
                        "prevented one."}
    out = os.path.join(HERE, "safe_arms.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    for b in built.values():
        if b and os.path.exists(b):
            os.unlink(b)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
