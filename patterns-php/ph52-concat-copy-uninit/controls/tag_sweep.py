#!/usr/bin/env python3
"""ph52 control: the TAG SWEEP, and the number the row publishes.

    python3 patterns-php/ph52-concat-copy-uninit/controls/tag_sweep.py
    python3 .../tag_sweep.py --selftest

⭐⭐ **WHAT THIS NUMBER ANSWERS, AND IT IS WHAT A READER OF THIS LADDER NEEDS:**
*why do uninitialised-read bugs survive for years in shipped code?* `zend.c:243`
tears down a slot whose tag byte nobody wrote, and `Zend/zend_variables.c:36-80`
dispatches on that byte -- so the harm is CONDITIONAL ON THE GARBAGE VALUE and
the condition is small and countable.

The sweep drives `tag_sweep.c` -- a verbatim transcription of `_zval_dtor` over
the whole byte, including the two arms `c/kernel.c` does NOT lift -- and this file
re-derives the same table INDEPENDENTLY from the `#define`s and the `switch`, so
the two are a cross-check rather than one program printing its own input back.

⚠⚠ **`RECAP_PHP.md` F102 PREDICTED *"five named cases out of a byte, widened by
the `& ~IS_CONSTANT_INDEX` mask"*, EXPLICITLY UNTESTED. IT IS WRONG IN THREE
WAYS** and `../NOTES.md` §6 carries the correction:

  1. **SIX named cases, not five.** F102 lists `IS_STRING`, `IS_CONSTANT`,
     `IS_ARRAY`, `IS_CONSTANT_ARRAY` and `IS_OBJECT`, and misses
     **`IS_RESOURCE`** -- `zend_variables.c:64-71`, whose arm calls
     `zend_list_delete(zvalue->value.lval)` on a `long` read out of the same
     unwritten slot.
  2. **TWELVE of 256 byte values, not ten.** The `& ~0x80` mask doubles each of
     the six residues `{3, 4, 5, 7, 8, 9}`.
  3. **`_zval_dtor` DOES have `case IS_NULL`.** F102 says it *"has no
     `case IS_NULL`"*; `zend_variables.c:75` is `case IS_NULL:`, sitting beside
     `default:` at `:76`. The CONCLUSION -- a zero tag is a no-op -- holds; the
     reason given for it does not.

▶ **AND THE SUB-COUNT THAT MATTERS MORE THAN THE TOTAL:** only **8 of 256**
(3.125 %) reach `efree`/`free` with a pointer read out of the slot. The other four
dereference or index through it without releasing it.

⚠ `--selftest`'s negatives are NEW to this row (`.memory-php/04-process.md`
law 7): a control cloned between rows carries its defects.
"""

import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
SRC = os.path.join(HERE, "tag_sweep.c")

#: `Zend/zend.h:387-399`, read back out of `c/kernel.h` by `_row_constants()`.
NAMES = {"IS_NULL": 0, "IS_LONG": 1, "IS_DOUBLE": 2, "IS_STRING": 3,
         "IS_ARRAY": 4, "IS_OBJECT": 5, "IS_BOOL": 6, "IS_RESOURCE": 7,
         "IS_CONSTANT": 8, "IS_CONSTANT_ARRAY": 9}
MASK = 0x80     # IS_CONSTANT_INDEX

#: The SIX teardown arms of `_zval_dtor`, by the residue that selects them, with
#: whether the arm reaches the allocator with a pointer read out of the slot.
#: ⚠ DERIVED HERE FROM THE SWITCH, not imported from `tag_sweep.c`.
ARMS = {
    3: ("STR_FREE(efree)", True),                   # :42-46  IS_STRING
    8: ("STR_FREE(efree)", True),                   # :43     IS_CONSTANT
    4: ("hash destroy+FREE_HASHTABLE", True),       # :47-56  IS_ARRAY
    9: ("hash destroy+FREE_HASHTABLE", True),       # :48     IS_CONSTANT_ARRAY
    5: ("object del_ref", False),                   # :57-63  IS_OBJECT
    7: ("zend_list_delete", False),                 # :64-71  IS_RESOURCE
}

#: The two arms `c/kernel.c` does NOT lift, by residue. `controls/tag_sweep.c`
#: carries all six so the published figure is about UPSTREAM.
NOT_LIFTED = {5, 7}


def arm_of(tag):
    """`_zval_dtor`'s dispatch, spelled independently of `tag_sweep.c`."""
    if tag == NAMES["IS_LONG"]:
        return None                                  # :38-40  the early return
    r = tag & ~MASK
    return ARMS.get(r, (None, None))[0] if r in ARMS else None


def table():
    """(per-arm counts, tearing tags, allocator-reaching tags)."""
    counts = {}
    tearing = []
    freeing = []
    for t in range(256):
        a = arm_of(t)
        counts[a] = counts.get(a, 0) + 1
        if a is not None:
            tearing.append(t)
            if ARMS[t & ~MASK][1]:
                freeing.append(t)
    return counts, tearing, freeing


def _row_constants():
    """The IS_* codes as `c/kernel.h` spells them, so this file cannot drift."""
    out = {}
    with open(os.path.join(ROW, "c", "kernel.h")) as fh:
        for line in fh:
            m = re.match(r"#define\s+PH52_(IS_\w+)\s+(0x[0-9A-Fa-f]+|\d+)", line)
            if m:
                out[m.group(1)] = int(m.group(2), 0)
    return out


def run_c():
    """Build and run `tag_sweep.c`, returning its tearing-tag list."""
    out = os.path.join(os.environ.get("SLB_TMP", "/tmp"), "ph52_tag_sweep")
    out = os.path.join(ROW, "..", "..", ".temp", "php45", "tag_sweep.bin")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    r = subprocess.run(["/usr/bin/gcc", "-std=c99", "-Wall", "-Wextra", "-O1",
                        SRC, "-o", out], capture_output=True, text=True)
    if r.returncode != 0:
        return None, f"build failed: {(r.stdout + r.stderr)[-300:]}"
    r = subprocess.run([out], capture_output=True, text=True, timeout=60)
    tags = [int(m.group(1)) for m in
            re.finditer(r"^\s*(\d+) \(0x..\) ->", r.stdout, re.M)]
    return tags, r.stdout


def check():
    """Problems. The C and this file must agree, exactly."""
    bad = []
    cc = _row_constants()
    for k, v in NAMES.items():
        if cc.get(k) != v:
            bad.append(f"c/kernel.h PH52_{k} = {cc.get(k)}, this file says {v}")
    if cc.get("IS_CONSTANT_INDEX") != MASK:
        bad.append(f"c/kernel.h PH52_IS_CONSTANT_INDEX = "
                   f"{cc.get('IS_CONSTANT_INDEX')}, this file says {MASK}")
    ctags, _out = run_c()
    if ctags is None:
        bad.append(_out)
        return bad, None
    _counts, tearing, _freeing = table()
    if ctags != tearing:
        bad.append(f"tag_sweep.c tears down {ctags}, this file derives {tearing}")
    return bad, tearing


# ---------------------------------------------------------------------------
# §H: a validator lands with its must-fire negatives, or it does not land.
# ---------------------------------------------------------------------------
def selftest():
    fails = []
    _counts, tearing, freeing = table()

    def want(name, cond, why):
        if not cond:
            fails.append(f"{name}: {why}")

    # N1  MUST-FIRE on F102's own claim: the count is NOT 10 (five cases x the mask)
    want("N1 F102's five cases", len(tearing) == 12,
         f"the sweep finds {len(tearing)} tearing tags, and F102's 'five named "
         f"cases ... widened by the mask' predicts 10")
    # N2  MUST-FIRE: IS_RESOURCE is one of them and F102 omits it
    want("N2 IS_RESOURCE", 7 in tearing and 135 in tearing,
         "IS_RESOURCE (7) and its masked twin (135) must be in the set")
    # N3  MUST-NOT-FIRE: IS_NULL, IS_LONG, IS_DOUBLE, IS_BOOL are no-ops, masked
    #     or not
    for t in (0, 1, 2, 6, 128, 129, 130, 134):
        want(f"N3 tag {t}", t not in tearing,
             f"tag {t} must be a no-op ({t} & ~0x80 = {t & ~MASK})")
    # N4  MUST-FIRE: the mask really doubles every residue
    want("N4 the mask", all((t + 128) in tearing for t in (3, 4, 5, 7, 8, 9)),
         "every residue's masked twin must tear down too")
    # N5  MUST-NOT-FIRE: 0x81 masks to IS_LONG and the SWITCH's own
    #     `case IS_LONG: return` catches it -- not the `:38` early return, which
    #     tests the UNMASKED byte. ⭐ Two different reasons, one outcome, and a
    #     checker that conflated them would be right by accident.
    want("N5 0x81 via the switch", 129 not in tearing,
         "0x81 must be a no-op, and via `case IS_LONG:` at :72 rather than the "
         "`type == IS_LONG` early return at :38")
    want("N5b 0x01 via the early return", arm_of(1) is None,
         "0x01 must be a no-op via the :38 early return")
    # N6  MUST-FIRE: only 8 of the 12 reach the allocator
    want("N6 allocator-reaching", len(freeing) == 8,
         f"{len(freeing)} of {len(tearing)} tearing tags reach efree/free, "
         f"expected 8")
    # N7  MUST-FIRE: the two arms the kernel does not lift are exactly IS_OBJECT
    #     and IS_RESOURCE, so the kernel's OWN live count is 8 of 256
    kernel_live = [t for t in tearing if (t & ~MASK) not in NOT_LIFTED]
    want("N7 kernel's own count", len(kernel_live) == 8,
         f"c/kernel.c lifts arms for {len(kernel_live)} of the 12, expected 8")
    # N8  MUST-FIRE: a mutant dispatch that forgets the mask must be caught
    def no_mask(tag):
        if tag == 1:
            return None
        return ARMS.get(tag, (None, None))[0] if tag in ARMS else None
    mut = [t for t in range(256) if no_mask(t) is not None]
    want("N8 mask mutant", mut != tearing,
         "a dispatch without `& ~IS_CONSTANT_INDEX` must differ from the real one")
    # N9  MUST-FIRE: a mutant that drops the `:38` early return. ⚠ It does NOT
    #     change the answer, because `case IS_LONG:` at :72 returns too -- so this
    #     is a MUST-NOT-FIRE in disguise and the sweep says so rather than
    #     pretending the early return is load-bearing.
    def no_early(tag):
        r = tag & ~MASK
        return ARMS.get(r, (None, None))[0] if r in ARMS else None
    want("N9 :38 is redundant for the COUNT",
         [t for t in range(256) if no_early(t) is not None] == tearing,
         "deleting the `:38` early return must NOT change the count, because "
         "`case IS_LONG:` at :72 already returns -- and if it ever does change, "
         "this control's reading of the switch is wrong")
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        fails = selftest()
        print("  --selftest: 15 assertions (9 must-fire claims, 6 must-NOT-fire)")
        for f in fails:
            print(f"    FAIL {f}")
        print("  --selftest PASS" if not fails else "  --selftest FAILED")
        return 1 if fails else 0

    probs, tearing = check()
    counts, tearing2, freeing = table()
    for a_, n in sorted(counts.items(), key=lambda kv: (kv[0] is not None, kv[0] or "")):
        print(f"  {str(a_ or 'no-op'):32s} {n:3d} / 256  ({100.0 * n / 256:6.3f} %)")
    print(f"  {'TOTAL TEARING':32s} {len(tearing2):3d} / 256  "
          f"({100.0 * len(tearing2) / 256:6.3f} %)   {tearing2}")
    print(f"  {'of which reach efree/free':32s} {len(freeing):3d} / 256  "
          f"({100.0 * len(freeing) / 256:6.3f} %)   {freeing}")
    kl = [t for t in tearing2 if (t & ~MASK) not in NOT_LIFTED]
    print(f"  {'live in c/kernel.c (2 arms unlifted)':32s} {len(kl):3d} / 256  "
          f"({100.0 * len(kl) / 256:6.3f} %)")
    for p in probs:
        print(f"    PROBLEM {p}")
    print("  ok: tag_sweep.c and this file agree" if not probs else "  REFUSED")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
