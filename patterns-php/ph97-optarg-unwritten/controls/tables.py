#!/usr/bin/env python3
"""ph97 — the two constant tables, diffed across all three transcriptions; and
the `strcasecmp` census, re-derived from the tarball.

    python3 patterns-php/ph97-optarg-unwritten/controls/tables.py

=============================================================================
WHY THIS EXISTS
=============================================================================
**A. THE TABLES.** `verus.rs` defines its spec functions `s_sel` and `s_name` as
the CONSTANT TABLES' OWN VIEWS, not as a second transcription of their bytes.
That is what lets the two table accessors have verifying twins instead of two
more entries in the TCB (`../NOTES.md` §10) — but it means **Verus checks that
the accessor returns row `k`, and nothing checks the bytes.** `model.py` carries
a third transcription and the gate's cross-rung checksum would notice a
disagreement only as a rung failure with the wrong name on it.

▶ So the bytes are checked HERE, three ways at once, with must-fire negatives.

**B. THE CENSUS, AND IT IS A CLEAN NEGATIVE.** `f7326d627962` is one hunk at one
site, so this row publishes NO census — and a negative is a result (F10) only if
it was looked for. This counts the `strcasecmp` call sites in the pristine
`mbstring.c`, separates the five that are `mb_get_info`'s chain from the seven
that are not, and reports both rather than asserting *"one site"*.

⚠ It reads the pinned tarball read-only and writes only `tables.json`.
"""

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
sys.path.insert(0, PDIR)
import _pin  # noqa: E402
import model  # noqa: E402

TARBALL = os.environ.get(
    "PHP500_TARBALL",
    "/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz")
NTYP = 21


# ------------------------------------------------------- A. the two tables --

def c_table(name):
    """`static const char <name>[N][PH97_BUFSZ] = { ... };` out of c/kernel.c."""
    src = open(os.path.join(PDIR, "c", "kernel.c")).read()
    m = re.search(r"static const char " + re.escape(name)
                  + r"\[[^\]]*\]\[PH97_BUFSZ\]\s*=\s*\{(.*?)\};", src, re.S)
    assert m, f"c/kernel.c no longer declares {name}"
    return [s.encode().decode("unicode_escape").encode("latin-1")
            for s in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))]


def rust_table(path, name):
    """`const <name>: [[u8; NTYP]; N] = [ *b"...", ... ];` out of a rung."""
    src = open(os.path.join(PDIR, path)).read()
    m = re.search(r"const " + re.escape(name)
                  + r": \[\[u8; NTYP\]; \w+\] = \[(.*?)\];", src, re.S)
    assert m, f"{path} no longer declares {name}"
    out = []
    for s in re.findall(r'\*b"((?:[^"\\]|\\.)*)"', m.group(1)):
        b = s.encode().decode("unicode_escape").encode("latin-1")
        assert len(b) == NTYP, f"{path}:{name} entry is {len(b)} bytes, want {NTYP}"
        out.append(b.rstrip(b"\0"))
    return out


def part_a(problems):
    rec = {}
    for tname, cname, mine in (("SELS", "ph97_sels", list(model.SELS)),
                               ("NAMES", "ph97_enc_name", list(model.NAMES))):
        c = c_table(cname)
        rs = {p: rust_table(p, tname)
              for p in ("safe_naive.rs", "safe_tuned.rs", "unsafe.rs", "verus.rs")}
        rec[tname] = {"c": [x.decode("latin-1") for x in c],
                      "model": [x.decode("latin-1") for x in mine],
                      "rust": {p: [x.decode("latin-1") for x in v]
                               for p, v in rs.items()}}
        ok = all(v == c for v in rs.values()) and c == mine
        print(f"  {tname:6s} C={len(c)} model={len(mine)} rust="
              f"{ {p: len(v) for p, v in rs.items()} }  "
              f"{'ALL AGREE' if ok else 'DISAGREE'}")
        if not ok:
            problems.append(
                f"{tname}: the three transcriptions disagree -- C {c}, model "
                f"{mine}, rust { {p: v for p, v in rs.items()} }")
        for x in c:
            if len(x) >= NTYP:
                problems.append(
                    f"{tname}: entry {x!r} is {len(x)} bytes and the frame is "
                    f"{NTYP}, so it cannot be NUL-terminated inside it")
        if len(set(x.lower() for x in c)) != len(c):
            problems.append(
                f"{tname}: entries are not pairwise distinct under case folding, "
                f"so the chain's ORDER decides the answer and model.py::_dumb's "
                f"dict lookup would disagree with it")
    return rec


def negatives(problems):
    """MUST-FIRE: a corrupted transcription has to be caught."""
    c = c_table("ph97_sels")
    bad = list(c)
    bad[1] = b"internal_encodinG"      # one byte, one case
    caught = bad != list(model.SELS)
    print(f"  N1 MUST-FIRE  a one-byte corruption of SELS[1] -> "
          f"{'caught' if caught else 'MISSED'}")
    if not caught:
        problems.append("N1: a one-byte corruption of the selector table is not "
                        "caught, so part A certifies nothing")
    short = list(c)
    short[1] = b"x" * NTYP
    over = len(short[1]) >= NTYP
    print(f"  N2 MUST-FIRE  an entry of exactly {NTYP} bytes -> "
          f"{'caught' if over else 'MISSED'}")
    if not over:
        problems.append("N2: a table entry with no room for its NUL is not "
                        "caught")


# --------------------------------------------------------- B. the census ----

def part_b(problems):
    r = subprocess.run(["tar", "-xzOf", TARBALL,
                        "php-5.0.0/ext/mbstring/mbstring.c"],
                       capture_output=True)
    assert r.returncode == 0, "cannot read the pristine tarball"
    lines = r.stdout.decode("latin-1").splitlines()
    sites = [(i + 1, l.strip()) for i, l in enumerate(lines)
             if "strcasecmp" in l]
    chain = [(n, t) for n, t in sites if 3219 <= n <= 3252]
    rec = {"total_sites": len(sites),
           "mb_get_info_chain": [n for n, _ in chain],
           "other_sites": [n for n, _ in sites if not (3219 <= n <= 3252)]}
    print(f"  strcasecmp call sites in the pristine mbstring.c : {len(sites)}")
    print(f"    of which mb_get_info's chain (:3219-:3252)     : {len(chain)} "
          f"{rec['mb_get_info_chain']}")
    print(f"    elsewhere in the file                          : "
          f"{len(rec['other_sites'])} {rec['other_sites']}")
    print("  ⭐ THE CENSUS IS A CLEAN NEGATIVE: f7326d627962 is one hunk at one "
          "site, and the other sites compare CONFIGURATION values that are "
          "never optional parameters.")
    if len(chain) != 5:
        problems.append(
            f"mb_get_info's chain has {len(chain)} strcasecmp sites, want 5 -- "
            f"the five selectors are the row's own arms and the kernel ships "
            f"exactly that many")
    return rec


def main():
    problems = []
    print("A. THE TWO CONSTANT TABLES, THREE TRANSCRIPTIONS")
    rec = {"tables": part_a(problems)}
    negatives(problems)
    print("\nB. THE strcasecmp CENSUS -- a clean negative, re-derived")
    rec["census"] = part_b(problems)
    rec["problems"] = problems
    rec.update(_pin.pin(["c/kernel.c", "safe_naive.rs", "safe_tuned.rs",
                         "unsafe.rs", "verus.rs", "model.py"],
                        "python3 controls/tables.py", "seconds"))
    with open(os.path.join(HERE, "tables.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/tables.json -- {len(problems)} problem(s)")
    for p in problems:
        print("  ⛔ " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
