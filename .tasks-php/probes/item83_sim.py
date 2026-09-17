#!/usr/bin/env python3
# =============================================================================
# item83_sim.py -- **F100**'s SIMULATION HARNESS, AND THE PROMOTION THAT FOUND
# TWO OF ITS FOUR ARMS HAD GONE VACUOUS UNDER A REBUILT ROW
#
# ⛔⛔ WHY IT IS COMMITTED. Written under `.temp/php43/`, which is GITIGNORED.
# **F100** cites it BY PATH at `RECAP_PHP.md:5648` (landed 2026-09-13, commit
# 691b2cf): *"✅ **The degeneracy was SIMULATED, not inherited** --
# `.temp/php43/item83_sim.py` (`--selftest` PASS, 4 negatives) drives the row's
# **own** verdict functions. ✅ **All six published A1 percentages re-derive to
# the digit.**"* `.memory-php/04-process.md` LAW 11. Promoted by
# `TASK_PHP_064`, 2026-09-17, repo at commit f4bda71.
#
# ⭐ WHAT STILL HOLDS, re-run 2026-09-17: **`N1` -- the load-bearing arm -- is
# green.** The harness reproduces the committed `controls/spellings.json` on all
# five verdict fields (`r4_endpoint_degenerate` True, `r3_endpoint_degenerate`
# False, cheapest R3 `r3_chunks_mask`, cheapest R4 `v0_shipped`, dearest R3
# `r3_slice_param`), and the bare run reproduces `a1_spread_pp` `{R3: 39.899657,
# R4: 45.313019}` exactly. **F100's arithmetic survives its own row's rebuild.**
#
# ⛔⛔⛔ AND WHAT DID NOT -- THE PROBE ARRIVED **RED**, AND IT WAS NOT A CACHE.
# `--selftest` exited **1** before promotion, on two arms, for two different
# reasons, both caused by `TASK_PHP_042` re-searching `ph53`:
#
#   N4 REPORTED A MOVE THAT HAD NOT HAPPENED. It asserted the reading-(a)
#      exclusion set equalled a three-name LIST. After the rebuild each bitmask
#      variant matches `required[4]` TWICE (`wrote[i]` AND `[bool; MAXD]`), so
#      the list held **six** entries with duplicates and the arm said *"R4
#      exclusion set moved"* about a set that had not moved. ▶ **A membership
#      question asked of a multiset.** Repaired to compare the SET.
#   N2/N3 WENT VACUOUS. Both perturb the **R4** endpoint, and `ph53`'s R4
#      endpoint is now DEGENERATE as committed (`r4_beaters: []`). N2 is then
#      trivially satisfied by a state that was already degenerate; N3 asserts a
#      non-degenerate state that no longer exists, and fired. ▶ **An arm that
#      cannot discriminate is NOT PASSING, and an arm reporting that its subject
#      moved is not FAILING.** They now print `VACUOUS -- NOT A PASS`, the
#      discriminating pair is rebuilt on the **R3** side (`N2r`/`N3r`, live: six
#      beaters), and **`N5` MEASURES THE VACUITY'S CAUSE** so it is a reading of
#      the row rather than an assertion about it.
#   ⚠ `N3r` names the dearest R3 variant by DERIVING it from the row's own
#     `dearest_in_contract`, never as a literal -- which is the defect N4 had.
#
# ⚠⚠ THE GENERAL LESSON, AND IT IS WORTH MORE THAN THE REPAIR: **the two ways a
# promoted probe fails to run are a MISSING CACHE and A MOVED SUBJECT**, and
# only the first is guarded by the item-149 rule. `probes/ph29_predict.py`
# crashed on the same class in this same batch, from the opposite direction --
# its prediction came TRUE. **A one-shot probe cited by a finding acquires a
# maintenance cost the moment it is committed, and nothing in this tree prices
# that.**
#
# RUN IT:  python3 .tasks-php/probes/item83_sim.py --selftest   # 6 arms + 2 vacuous
#          python3 .tasks-php/probes/item83_sim.py              # the three readings
#
# ✅ WHAT IT NEEDS THAT IS NOT COMMITTED: NOTHING. It reads
# `patterns-php/ph53-iface-tail-uninit/controls/spellings.json` and imports that
# row's `controls/spellings.py` WITHOUT running its `main`; both committed. It
# re-runs no control, builds nothing, WRITES NOTHING. 0.3 s, 2026-09-17.
# ⚠ `ROOT` is a HARDCODED ABSOLUTE PATH to this checkout, not derived from
# `__file__` -- reported, not repaired, because `probes/sweep_cg.sh` and
# `probes/rebuild_hardened_php.sh` carry the same shape, ▶ which makes it a
# CLASS to adjudicate rather than a typo (`PROMOTE_001`'s call, kept).
#
# ⛔ WHAT IS STILL OWED. (1) **F100 has been REVIEWED AND NARROWED -- its R4 half
# is WITHDRAWN** (read the section heading before quoting anything). This
# promotion preserves the harness, not the withdrawn ruling. (2) *"All six
# published A1 percentages"* is `_043`'s check, and what re-derives here today is
# the FIVE verdict fields plus `a1_spread_pp`; nothing in this file enumerates
# the six percentages by name. (3) The R4 arms are vacuous and nothing will
# un-vacuum them except another R4 endpoint search on `ph53`.
# =============================================================================

"""TASK_PHP_043 §1 -- SIMULATE READING (a) THROUGH `ph53`'s OWN VERDICT FUNCTIONS.

Reading (a) of item 83 says a `required` entry's backticked span binds inside
the rungs its English scopes to, so the three bitmask variants (which record
`required_absent: ["required[4] `wrote[i]`"]`) are OUT OF CONTRACT.

⚠⚠ THIS SCRIPT DOES NOT RE-RUN THE CONTROL AND BUILDS NOTHING. It reads the
COMMITTED `controls/spellings.json`, rebuilds the `rows` dict the control's own
verdict functions consume, flips `in_contract` on exactly the variants reading
(a) excludes, and calls `cheaper_than_shipped` / `cheapest_in_contract` /
`dearest_in_contract` FROM THE ROW'S OWN MODULE. So the degeneracy verdict is
computed by the same code that published `r4_endpoint_degenerate: false`, not by
a reimplementation here.

⚠ `--selftest` drove three controls as written, and now drives six arms plus a
vacuity report -- see the promotion header above for what moved and why.
The original description: the UNMODIFIED rows must reproduce the
committed `r4_endpoint_degenerate` / `r3_endpoint_degenerate` / cheapest /
dearest fields exactly (otherwise this harness is not reading the same thing the
control wrote), a must-FIRE case (excluding every R4 variant makes the endpoint
degenerate), and a must-NOT-FIRE case (excluding a DEARER R4 variant leaves it
non-degenerate).
"""
import importlib.util
import json
import os
import sys

ROOT = "/home/apt/repos_common/sec-ladder"
PDIR = os.path.join(ROOT, "patterns-php/ph53-iface-tail-uninit")
SJSON = os.path.join(PDIR, "controls/spellings.json")


def load_module():
    """Import `ph53/controls/spellings.py` WITHOUT running its `main`."""
    path = os.path.join(PDIR, "controls/spellings.py")
    spec = importlib.util.spec_from_file_location("ph53_spellings", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ph53_spellings"] = mod
    spec.loader.exec_module(mod)
    return mod


def rows_from_json():
    d = json.load(open(SJSON))
    rows = {}
    for r in d["variants"]:
        rows[(r["side"], r["name"])] = dict(r)
    return d, rows


def verdicts(mod, rows):
    beat = mod.cheaper_than_shipped(rows, "R4")
    beat3 = mod.cheaper_than_shipped(rows, "R3")
    c3 = mod.cheapest_in_contract(rows, "R3")
    c4 = mod.cheapest_in_contract(rows, "R4")
    d3 = mod.dearest_in_contract(rows, "R3")
    return {
        "r4_endpoint_degenerate": not beat,
        "r3_endpoint_degenerate": not beat3,
        "cheapest_r3_in_contract": (c3 or {}).get("name"),
        "cheapest_r4_in_contract": (c4 or {}).get("name"),
        "dearest_r3_in_contract": (d3 or {}).get("name"),
        "r4_beaters": [r["name"] for r in beat],
        "r3_beaters": [r["name"] for r in beat3],
    }


# Variants whose `required_absent` names `required[4]` AND which are on a RUNG
# side. Computed, not hardcoded -- so if the committed file changes, so does the
# exclusion set.
def reading_a_exclusions(rows, entry="required[4]"):
    out = []
    for (side, name), r in rows.items():
        if side not in ("R3", "R4"):
            continue
        for m in (r.get("required_absent") or []):
            if m.startswith(entry + " "):
                out.append((side, name, m))
    return out


def main():
    mod = load_module()
    committed, rows = rows_from_json()

    if "--selftest" in sys.argv:
        fails, vacuous = [], []
        # N1 -- the harness reproduces the committed verdicts from the committed
        # rows. If this fails, nothing else this script prints means anything.
        base = verdicts(mod, rows)
        for k in ("r4_endpoint_degenerate", "r3_endpoint_degenerate",
                  "cheapest_r3_in_contract", "cheapest_r4_in_contract",
                  "dearest_r3_in_contract"):
            if base[k] != committed.get(k):
                fails.append(f"N1 {k}: harness {base[k]!r} != committed "
                             f"{committed.get(k)!r}")

        # ⛔⛔ N2/N3 WERE WRITTEN ON THE **R4** SIDE AND `ph53` HAS MOVED UNDER
        # THEM (`TASK_PHP_042`). The committed record now reads
        # `r4_endpoint_degenerate: true` with `r4_beaters: []`, so the R4
        # endpoint has nothing to perturb: N2 ("excluding all R4 challengers
        # degenerates it") is trivially satisfied by a state that was already
        # degenerate, and N3 ("excluding a DEARER R4 variant leaves it
        # non-degenerate") asserts a state that no longer exists and fired.
        # ▶ **AN ARM THAT CANNOT DISCRIMINATE IS NOT PASSING**, and one that
        # reports its own subject moving is not FAILING either. They are
        # reported VACUOUS -- `checkers.py`'s own dialect for this -- and the
        # discriminating pair is rebuilt on the **R3** side, which is live
        # (six beaters). N5 pins the CAUSE so the vacuity is measured, not
        # assumed.
        r4_live = bool(base["r4_beaters"])

        # N2 -- MUST FIRE: exclude every non-shipped R4 variant and the R4
        # endpoint must go degenerate.
        r2 = {k: dict(v) for k, v in rows.items()}
        for (s, n) in list(r2):
            if s == "R4" and n != "v0_shipped":
                r2[(s, n)]["in_contract"] = False
        if not r4_live:
            vacuous.append("N2 (R4 must-fire): the R4 endpoint is ALREADY "
                           "degenerate, so this arm cannot discriminate")
        elif verdicts(mod, r2)["r4_endpoint_degenerate"] is not True:
            fails.append("N2 did NOT fire: excluding all R4 challengers left "
                         "the endpoint non-degenerate")
        # N3 -- MUST NOT FIRE: exclude only a DEARER R4 variant.
        if not r4_live:
            vacuous.append("N3 (R4 must-NOT-fire): no R4 variant beats the "
                           "shipped rung, so there is no non-degenerate state "
                           "to preserve")
        else:
            r3 = {k: dict(v) for k, v in rows.items()}
            r3[("R4", "r4_win_checked")]["in_contract"] = False
            if verdicts(mod, r3)["r4_endpoint_degenerate"] is not False:
                fails.append("N3 FIRED: excluding a dearer variant should not "
                             "degenerate the endpoint")

        # N2r -- MUST FIRE, R3 side: exclude every non-shipped R3 variant and
        # the R3 endpoint must go degenerate.
        r2r = {k: dict(v) for k, v in rows.items()}
        for (s, n) in list(r2r):
            if s == "R3" and n != "v0_shipped":
                r2r[(s, n)]["in_contract"] = False
        if verdicts(mod, r2r)["r3_endpoint_degenerate"] is not True:
            fails.append("N2r did NOT fire: excluding all R3 challengers left "
                         "the endpoint non-degenerate")
        # N3r -- MUST NOT FIRE, R3 side: exclude only the DEAREST in-contract R3
        # variant. ⭐ DERIVED from the row's own `dearest_in_contract`, never
        # named as a literal -- which is the defect N4 carried.
        dear = (mod.dearest_in_contract(rows, "R3") or {}).get("name")
        if not dear:
            vacuous.append("N3r: no dearest in-contract R3 variant resolves")
        else:
            r3r = {k: dict(v) for k, v in rows.items()}
            r3r[("R3", dear)]["in_contract"] = False
            if verdicts(mod, r3r)["r3_endpoint_degenerate"] is not False:
                fails.append(f"N3r FIRED: excluding the DEAREST R3 variant "
                             f"({dear}) should not degenerate the endpoint")

        # N4 -- the reading-(a) exclusion set is exactly the three bitmask
        # variants and nothing else on the R4 side.
        # ⛔⛔ REPAIRED AT PROMOTION: this compared a LIST, and since `ph53` was
        # rebuilt each bitmask variant matches `required[4]` TWICE (`wrote[i]`
        # AND `[bool; MAXD]`), so the list held six entries with duplicates and
        # the arm reported "exclusion set moved" about a set that had not moved.
        # A membership question asked of a multiset. The SET is the question.
        exc = reading_a_exclusions(rows)
        r4exc = sorted({n for s, n, _ in exc if s == "R4"})
        if r4exc != ["r4_bitmask", "r4_bitmask_min", "r4_bitmask_pool"]:
            fails.append(f"N4 R4 exclusion set moved: {r4exc}")

        # N5 -- ⭐ THE VACUITY'S OWN CAUSE, MEASURED. Without this, "N2/N3 are
        # vacuous" is an assertion about the row rather than a reading of it.
        if bool(committed.get("r4_endpoint_degenerate")) == r4_live:
            fails.append(
                f"N5: the committed record says r4_endpoint_degenerate="
                f"{committed.get('r4_endpoint_degenerate')!r} while the "
                f"harness computes {len(base['r4_beaters'])} R4 beater(s) -- "
                f"the two disagree, so the vacuity above is not explained")

        print("SELFTEST:", "FAIL" if fails else "PASS", end="")
        print(f"  ({len(vacuous)} arm(s) VACUOUS)" if vacuous else "")
        for f in fails:
            print("  ", f)
        for v in vacuous:
            print("   ⓘ VACUOUS -- NOT A PASS:", v)
        if vacuous:
            print("   ▶ `ph53` was re-searched (TASK_PHP_042) and its R4 "
                  "endpoint is degenerate as committed. The R4 arms report on "
                  "the ROW, not on this harness; N2r/N3r are the live pair.")
        return 1 if fails else 0

    print("=== COMMITTED (reading (b): required is presence-only) ===")
    base = verdicts(mod, rows)
    for k, v in base.items():
        print(f"  {k:28s} {v}")
    print(f"  [cross-check vs committed json] "
          f"r4_endpoint_degenerate={committed['r4_endpoint_degenerate']} "
          f"r3={committed['r3_endpoint_degenerate']} "
          f"cheapest_r4={committed['cheapest_r4_in_contract']}")

    print("\n=== READING (a): required[4]'s backticks bind inside its English "
          "scope ===")
    exc = reading_a_exclusions(rows)
    rows_a = {k: dict(v) for k, v in rows.items()}
    for s, n, m in exc:
        print(f"  excluding {s} {n:18s} on {m}")
        rows_a[(s, n)]["in_contract"] = False
    va = verdicts(mod, rows_a)
    for k, v in va.items():
        print(f"  {k:28s} {v}")

    print("\n=== READING (a) applied to EVERY required entry, not just [4] ===")
    rows_all = {k: dict(v) for k, v in rows.items()}
    # An entry binds only inside the rungs its English scopes to. The English
    # scopes, transcribed by hand from spec.md and stated here so the reading is
    # auditable:
    scope = {
        "required[0]": {"R3", "R4"},   # "safe_tuned.rs, unsafe.rs and verus.rs"
        "required[1]": {"R4"},         # "safe_naive.rs, unsafe.rs and verus.rs"
        "required[2]": {"R4"},         # "unsafe.rs and verus.rs"
        "required[4]": {"R4"},         # "unsafe.rs and verus.rs"
    }
    for (side, name), r in rows_all.items():
        if side not in ("R3", "R4"):
            continue
        for m in (r.get("required_absent") or []):
            tag = m.split(" ")[0]
            if side in scope.get(tag, set()):
                print(f"  excluding {side} {name:18s} on {m}")
                r["in_contract"] = False
    vall = verdicts(mod, rows_all)
    for k, v in vall.items():
        print(f"  {k:28s} {v}")

    print("\n=== a1_spread_pp UNDER READING (a) -- recomputed the control's "
          "own way (max-min of pct_vs_r4ship_a1) ===")
    for label, rr, filt in (("committed (all variants)", rows, False),
                            ("reading (a) scoped, in-contract", rows_all, True)):
        for side in ("R3", "R4"):
            vals = [r["pct_vs_r4ship_a1"] for (s, n), r in rr.items()
                    if s == side and r.get("pct_vs_r4ship_a1") is not None
                    and (not filt or r.get("in_contract"))]
            if not vals:
                print(f"  {label:32s} {side} spread = NONE (no variants left)")
                continue
            print(f"  {label:32s} {side} spread = "
                  f"{round(max(vals) - min(vals), 6)} pp over {len(vals)}")
    print(f"  committed json a1_spread_pp = {committed['a1_spread_pp']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
