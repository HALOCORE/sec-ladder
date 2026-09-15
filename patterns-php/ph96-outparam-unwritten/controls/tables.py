#!/usr/bin/env python3
"""ph96 -- do the C rungs, the four Rust rungs and `model.py` carry the SAME
constants?

    python3 patterns-php/ph96-outparam-unwritten/controls/tables.py

Three transcriptions of two small tables, and a typo in any one of them would be
a silent disagreement the gate's cross-rung checksum would blame on a RUNG:

  * `Z_TYPE_P`'s four reachable tags, in **upstream's own numbering**
    (`Zend/zend.h:302-309`) -- C `ph96_tytab`, Rust `TYTAB`, model `TYTAB`;
  * the six fold tags, which decide what each of the four handlers contributes
    to the `u64`.

⭐ The type table is also what `verus.rs`'s `s_tytab` is DEFINED AS THE VIEW OF,
so nothing about its four bytes is in the TCB -- this file is where they are
checked instead.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, PDIR)
import _pin  # noqa: E402
import model  # noqa: E402

TAGS = ("READ", "UNDEF", "WRITE", "EXISTS", "UNSET", "CORE")


def c_defines(path):
    s = open(path).read()
    return {m.group(1): int(m.group(2).rstrip("uU"), 0)
            for m in re.finditer(r"^#define PH96_(\w+)\s+(0x[0-9A-Fa-f]+[uU]?|\d+)",
                                 s, re.M)}


def c_tytab(path):
    s = open(path).read()
    m = re.search(r"ph96_tytab\[4\]\s*=\s*\{(.*?)\}", s, re.S)
    names = [x.strip().replace("PH96_", "") for x in m.group(1).split(",")]
    d = c_defines(os.path.join(os.path.dirname(path), "kernel.h"))
    d.update(c_defines(path))
    return [d[n] for n in names]


def rust_consts(path):
    s = open(path).read()
    out = {}
    for m in re.finditer(r"^(?:pub )?const (\w+): u(?:8|64) = (0x[0-9A-Fa-f]+|\d+);",
                         s, re.M):
        out[m.group(1)] = int(m.group(2), 0)
    m = re.search(r"TYTAB: \[u8; 4\] = \[(.*?)\]", s, re.S)
    out["_TYTAB"] = [out[x.strip()] for x in m.group(1).split(",")]
    return out


def main():
    problems = []
    rec = {"problems": problems}
    cdef = c_defines(os.path.join(PDIR, "c", "kernel.h"))
    cdef.update(c_defines(os.path.join(PDIR, "c", "kernel.c")))
    rows = {"c/kernel.c": {"tytab": c_tytab(os.path.join(PDIR, "c", "kernel.c"))},
            "model.py": {"tytab": list(model.TYTAB)}}
    for r in ("safe_naive.rs", "safe_tuned.rs", "unsafe.rs", "verus.rs"):
        rows[r] = {"tytab": rust_consts(os.path.join(PDIR, r))["_TYTAB"]}
    rec["tytab"] = {k: v["tytab"] for k, v in rows.items()}
    base = rows["c/kernel.c"]["tytab"]
    print(f"{'source':18s} Z_TYPE_P table")
    for k, v in rows.items():
        ok = v["tytab"] == base
        print(f"{k:18s} {v['tytab']}  {'ok' if ok else 'DIFFERS'}")
        if not ok:
            problems.append(f"{k}'s type table {v['tytab']} differs from "
                            f"c/kernel.c's {base}")
    # upstream's own numbering -- Zend/zend.h:302-309
    want = [0, 1, 3, 6]
    rec["upstream_numbering"] = want
    if base != want:
        problems.append(f"the type table is {base}, not upstream's IS_NULL=0, "
                        f"IS_LONG=1, IS_BOOL=3, IS_STRING=6 -- the switch in "
                        f"i_zend_is_true is supposed to be upstream's switch")

    # ---- the six fold tags, three transcriptions -------------------------
    rec["tags"] = {}
    print(f"\n{'source':18s} " + " ".join(f"{t:7s}" for t in TAGS))
    ctags = [cdef["TAG_" + t] for t in TAGS]
    rec["tags"]["c/kernel.c"] = ctags
    print(f"{'c/kernel.c':18s} " + " ".join(f"{v:#7x}" for v in ctags))
    mtags = [getattr(model, "TAG_" + t) for t in TAGS]
    rec["tags"]["model.py"] = mtags
    print(f"{'model.py':18s} " + " ".join(f"{v:#7x}" for v in mtags))
    if mtags != ctags:
        problems.append(f"model.py's tags {mtags} differ from c/kernel.c's "
                        f"{ctags}")
    for r in ("safe_naive.rs", "safe_tuned.rs", "unsafe.rs", "verus.rs"):
        rc = rust_consts(os.path.join(PDIR, r))
        rt = [rc["TAG_" + t] for t in TAGS]
        rec["tags"][r] = rt
        print(f"{r:18s} " + " ".join(f"{v:#7x}" for v in rt))
        if rt != ctags:
            problems.append(f"{r}'s tags {rt} differ from c/kernel.c's {ctags}")

    # ---- the record geometry ---------------------------------------------
    rec["geometry"] = {"REC": cdef["REC"], "STRMAX": cdef["STRMAX"]}
    print(f"\nrecord geometry: REC={cdef['REC']} STRMAX={cdef['STRMAX']}")
    if cdef["REC"] != model.REC or cdef["STRMAX"] != model.STRMAX:
        problems.append("model.py's REC/STRMAX differ from c/kernel.h's")
    if cdef["REC"] != 6 + cdef["STRMAX"]:
        problems.append(f"REC ({cdef['REC']}) is not SOFF + STRMAX (6 + "
                        f"{cdef['STRMAX']}), so the record's value field does "
                        f"not reach the end of the record and every rung's "
                        f"bound is arbitrary rather than structural")

    # ---- §H: must-fire, so a comparator that stopped comparing fails ------
    n1 = (c_tytab(os.path.join(PDIR, "c", "kernel.c")) != [0, 1, 3, 7])
    print(f"\nN1 MUST-FIRE  a planted wrong table differs -> "
          f"{'ok' if n1 else 'BAD'}")
    if not n1:
        problems.append("N1: the comparator cannot tell [0,1,3,6] from "
                        "[0,1,3,7], so every `ok` above means nothing")
    n2 = TAGS and len(set(ctags)) == len(ctags)
    print(f"N2 MUST-NOT-FIRE  the six fold tags are pairwise distinct -> "
          f"{'ok' if n2 else 'BAD'}")
    if not n2:
        problems.append("N2: two fold tags are equal, so two of the four "
                        "handlers' answers are indistinguishable in the u64")

    rec.update(_pin.pin(["c/kernel.h", "c/kernel.c", "model.py",
                         "safe_naive.rs", "safe_tuned.rs", "unsafe.rs",
                         "verus.rs"],
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
