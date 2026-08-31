#!/usr/bin/env python3
"""p35 CONTROLS: **the two configurations of the union read, measured side by
side -- the one the gate accepts and the one it refuses.**

    python3 patterns/p35-tagged-union/controls/union_oracle.py

⚠⚠⚠ THIS IS THE ROW'S R5 RESULT AND IT IS AN EXPERIMENT, NOT A COMPLAINT
------------------------------------------------------------------------
Verus supports the Rust `union` **natively**: the correct-variant obligation is
first class in the type system, checked at the operation, with the diagnostic

    error: requirement not met: to access this field, the union must be in the
           correct variant

⚠ It is a LANGUAGE BUILTIN, not a vstd specification, so a `std_specs/` grep
misses it entirely -- which matters, because *"no spec exists"* has been the
wrong reading twice on this project already (`CLAUDE.md`).

But a union read is spelled `unsafe { p.i }` in Rust whether or not Verus checks
it, and `harness/check.py::_scan_unsafe_sites` requires every `unsafe` TOKEN to
sit inside a `#[verifier::external_body]` item's body. Wrapping the read is
exactly what moves it OUT of the region Verus checks and INTO an axiom -- and
the wrapper, being trusted, then owes a verified twin that **cannot be written,
because Rust has no safe spelling of a union read at all**.

So there are two configurations, and this script runs both:

    A  SHIPPED   the read inside `#[verifier::external_body]`. Verifies. The
                 correct-variant obligation survives as the wrapper's
                 `requires` and is checked AT EVERY CALL SITE. What is
                 axiomatised is BOTH unchecked operations in
                 `unsafe { v.get_unchecked(i).i }`: that the body reads the
                 member its name says, AND that `i < v@.len()` licenses the
                 index. (⚠ CORRECTED AT TASK_153 -- this line read ~~what is
                 axiomatised is that the body reads the member its name says~~,
                 which describes one of two. TASK_152 M5.)
                 The gate accepts it and BLOCKS the missing twin, out loud.
    B  REFUSED   the read in VERIFIED code. Verifies, and Verus checks the
                 variant AT THE READ -- a strictly stronger statement, with no
                 axiom at all. `_scan_unsafe_sites` FAILS it.

⚠⚠ **AND THE TWO CONFIGURATIONS DIFFER IN A SECOND WAY THAT IS SHARPER THAN
AXIOM-VERSUS-CHECK (TASK_152 M3, landed TASK_153).** Delete the correct-variant
conjunct itself. In **A** the file still verifies at the shipped obligation
count (`../controls/proof_mutants.py` arm `X1`) and only `spec.md`'s item pin
notices. In **B** the same deletion **FAILS AT THE READ** -- that is arm `B2`
below, and it is the same mutation. **So the gate forces the configuration whose
central obligation can be deleted without the gate noticing.**

**p35 ships A and makes the gap the finding** -- `p42`'s standing precedent.
⚠ This script does NOT propose a `check.py` change: a `check.py` edit is a
29-pattern re-gate and is the manager's call.

FOUR CELLS, AND EVERY ONE HAS A MUST-FAIL ARM
---------------------------------------------
  A1  configuration A verifies                                    (must PASS)
  A2  ...and deleting the tag test at the CALL SITE fails with
      `precondition not satisfied`                                (must FAIL)
  B1  configuration B verifies                                    (must PASS)
  B2  ...and deleting `requires p is i` fails with
      `requirement not met: ... correct variant`                  (must FAIL)

plus two facts about the gate and the language, each measured rather than
quoted:

  G   `check._scan_unsafe_sites`, THE REAL FUNCTION, run against a synthetic
      pattern directory holding each configuration: 0 failures on A, >=1 on B.
  E   `rustc` on the twin that would discharge A's obligation: `error[E0133]`.
      Three spellings are tried, so the result is about the LANGUAGE and not
      about one way of writing it.

⚠ A cell that RAISES is reported as a failed cell with its exception text and
never allowed to crash the script.
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
OUT = os.path.join(REPO, ".temp", "p35ctl", "oracle")
VERUS_RUN = os.path.join(REPO, "verus_run.py")
RUSTC = os.environ.get("SLB_RUSTC", os.path.expanduser("~/.cargo/bin/rustc"))

sys.path.insert(0, os.path.join(REPO, "harness"))

PRELUDE = """use vstd::prelude::*;
use vstd::pervasive::print_u64;

verus!{

pub union Pay { pub i: u64, pub d: f64, pub o: u32 }

pub open spec fn pay_int(p: Pay) -> u64 { get_union_field::<Pay, u64>(p, "i") }
"""

#: A -- SHIPPED. The read is wrapped. `{REQ}` is the wrapper's variant clause
#: and `{TAG}` is the call site's tag test; the must-fail arm deletes the tag
#: test, which is what a rung with p35's bug would look like at R5.
CONF_A = PRELUDE + """
#[verifier::external_body]
fn pay_i(p: &Pay) -> (r: u64)
    requires *p is i,
    ensures r == pay_int(*p),
{ unsafe { p.i } }

fn read_cell(t: u8, p: &Pay) -> (r: u64)
    requires t == 1u8 ==> *p is i,
{
    if t == 1u8 {TAG}
}

fn main() {
    let p = Pay { i: 7 };
    print_u64(read_cell(1u8, &p));
}

}
"""

#: B -- REFUSED by `_scan_unsafe_sites`. The read stays in verified code and
#: Verus checks the variant AT THE READ. The must-fail arm deletes the
#: `requires`.
CONF_B = PRELUDE + """
fn pay_i(p: &Pay) -> (r: u64)
{REQ}
    ensures r == pay_int(*p),
{
    unsafe { p.i }
}

fn main() {
    let p = Pay { i: 7 };
    print_u64(pay_i(&p));
}

}
"""

#: E -- the twin that cannot exist. Three spellings, plain rustc, no Verus.
TWIN_SPELLINGS = {
    "index": "pub fn t(v: &[Pay; 8], i: usize) -> u64 { v[i].i }",
    "get_unchecked": "pub fn t(v: &[Pay; 8], i: usize) -> u64 "
                     "{ v.get_unchecked(i).i }",
    "deref": "pub fn t(p: &Pay) -> u64 { p.i }",
}
TWIN_FILE = """#![allow(dead_code)]
pub union Pay { pub i: u64, pub d: f64, pub o: u32 }
%s
fn main() {}
"""



def mask(txt):
    """Strip everything from a diagnostic that is not evidence.

    ⚠ A committed file that cites an absolute `.temp/` path costs the manager a
    `harness/tools/temp_citations.py` baseline entry for a file a fresh clone
    will not have, and that tool reads `git ls-files`, so the cost only shows
    up after the commit. ASan pids and pointer values are pure churn for the
    same reason `p23`'s `controls.log` is declared un-hashable
    (`.memory/05-layout.md`). The DIAGNOSTIC TEXT is what this control is
    evidence for; the path, the pid and the address are not."""
    txt = re.sub(re.escape(REPO) + r"/\.temp/\S*", "<scratch>", txt)
    txt = txt.replace(REPO + "/", "")
    txt = re.sub(r"==\d+==", "==<pid>==", txt)
    txt = re.sub(r"0x[0-9a-f]{6,}", "0x<addr>", txt)
    return txt

def sh(cmd):
    env = dict(os.environ)
    env.pop("LD_PRELOAD", None)
    return subprocess.run(cmd, capture_output=True, text=True, env=env,
                          timeout=1800, cwd=REPO)


def verus(src_text, name):
    path = os.path.join(OUT, name)
    open(path, "w").write(src_text)
    r = sh([sys.executable, VERUS_RUN, path])
    txt = r.stdout + r.stderr
    m = re.search(r"(\d+) verified, (\d+) errors", txt)
    return {"file": os.path.relpath(path, REPO),
            "verified": int(m.group(1)) if m else None,
            "errors": int(m.group(2)) if m else None,
            "diagnostic": mask(re.sub(r"\s+", " ", txt.strip()))[:400]}


def scan_unsafe(src_text, name):
    """Run **the real `check._scan_unsafe_sites`** against a synthetic pattern
    directory holding one `.rs` file. TASK_096/097's method: execute the
    predicate, do not read it."""
    import check
    d = os.path.join(OUT, "pdir-" + name)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "verus.rs"), "w").write(src_text)
    rep = check.Report()
    contract = {"verus": {"obligations": {"verus.rs": 1}}}
    check._scan_unsafe_sites(rep, d, contract)
    return {"failures": len(rep.failures),
            "messages": [mask(m) for _s, m in rep.failures][:2]}


def derived_from():
    out = {}
    for rel in ("patterns/p35-tagged-union/verus.rs",
                "patterns/p35-tagged-union/controls/union_oracle.py",
                "harness/check.py", "harness/vparse.py", "verus_run.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    cells, results = [], {}

    def cell(label, fn, want):
        try:
            got = fn()
        except Exception as e:                              # noqa: BLE001
            got = {"RAISED": f"{type(e).__name__}: {e}"}
        ok = want(got)
        cells.append((label, ok, got))
        return got

    # --- A: the SHIPPED configuration ----------------------------------
    a1 = cell("A1  SHIPPED: read wrapped in external_body VERIFIES",
              lambda: verus(CONF_A.replace("{TAG}", "{ pay_i(p) } else { 0 }"),
                            "conf_a.rs"),
              lambda r: r.get("errors") == 0 and r.get("verified"))
    a2 = cell("A2  ...delete the CALL SITE's tag test -> must FAIL",
              lambda: verus(CONF_A.replace("{TAG}", "{ pay_i(p) } else "
                                                    "{ pay_i(p) }"),
                            "conf_a_mut.rs"),
              lambda r: (r.get("errors") or 0) > 0
              and "precondition not satisfied" in (r.get("diagnostic") or ""))

    # --- B: the configuration the gate refuses -------------------------
    b1 = cell("B1  REFUSED: read left in VERIFIED code VERIFIES",
              lambda: verus(CONF_B.replace("{REQ}", "    requires *p is i,"),
                            "conf_b.rs"),
              lambda r: r.get("errors") == 0 and r.get("verified"))
    b2 = cell("B2  ...delete `requires *p is i` -> must FAIL at the READ",
              lambda: verus(CONF_B.replace("{REQ}", ""), "conf_b_mut.rs"),
              lambda r: (r.get("errors") or 0) > 0
              and "correct variant" in (r.get("diagnostic") or ""))

    # --- G: the gate's own predicate, executed --------------------------
    ga = cell("G-A `check._scan_unsafe_sites` on A -> 0 failures",
              lambda: scan_unsafe(
                  CONF_A.replace("{TAG}", "{ pay_i(p) } else { 0 }"), "a"),
              lambda r: r.get("failures") == 0)
    gb = cell("G-B `check._scan_unsafe_sites` on B -> >= 1 failure",
              lambda: scan_unsafe(
                  CONF_B.replace("{REQ}", "    requires *p is i,"), "b"),
              lambda r: (r.get("failures") or 0) >= 1)

    # --- E: the twin that cannot exist ----------------------------------
    def try_twin(name, body):
        path = os.path.join(OUT, f"twin_{name}.rs")
        open(path, "w").write(TWIN_FILE % body)
        r = sh([RUSTC, "--edition", "2021", "--emit", "metadata",
                "-o", os.path.join(OUT, f"twin_{name}.meta"), path])
        txt = r.stdout + r.stderr
        return {"rc": r.returncode, "E0133": "E0133" in txt,
                "diagnostic": mask(re.sub(r"\s+", " ", txt.strip()))[:200]}

    twins = {}
    for name, body in TWIN_SPELLINGS.items():
        twins[name] = cell(f"E-{name:13s} safe union read -> must be E0133",
                           lambda n=name, b=body: try_twin(n, b),
                           lambda r: r.get("E0133") is True)

    print("p35 union oracle -- the two configurations of the union read\n")
    nok = 0
    for label, ok, got in cells:
        nok += bool(ok)
        ev = {k: v for k, v in got.items() if k != "diagnostic"}
        print(f"  {'ok  ' if ok else 'FAIL'} {label:56s} {ev}")
        if got.get("diagnostic"):
            print(f"         | {got['diagnostic'][:150]}")
    print(f"\n{nok}/{len(cells)} cell(s) as designed")

    results = {"A1_shipped_verifies": a1, "A2_call_site_mutant": a2,
               "B1_refused_verifies": b1, "B2_requires_mutant": b2,
               "G_scan_unsafe_sites_A": ga, "G_scan_unsafe_sites_B": gb,
               "E_safe_twin_spellings": twins}
    doc = {
        "pin": {"regenerate": "python3 patterns/p35-tagged-union/controls/"
                              "union_oracle.py"},
        "derived_from_sha256": derived_from(),
        "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cells_ok": nok,
        "cells_total": len(cells),
        "results": results,
        "invariant": "Both configurations of the union read VERIFY, and each "
                     "has a must-fail arm that fires with the diagnostic named "
                     "above. The configuration the gate REFUSES is the one in "
                     "which Verus checks the correct-variant obligation AT THE "
                     "READ rather than assuming it; the configuration p35 SHIPS "
                     "keeps the obligation as a wrapper precondition that is "
                     "checked at every call site, and axiomatises BOTH "
                     "unchecked operations in the body -- the union field read "
                     "AND the unchecked index. No safe Rust spelling of a union "
                     "read exists, in any of three forms, so the twin the gate "
                     "asks for cannot be written. ⚠⚠ The same `requires` "
                     "deletion that arm B2 makes FAIL AT THE READ in "
                     "configuration B leaves configuration A verifying at its "
                     "shipped obligation count (proof_mutants.py arm X1), so "
                     "the refused configuration is stronger in resistance as "
                     "well as in what it assumes.",
    }
    out = os.path.join(HERE, "union_oracle.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    return 0 if nok == len(cells) else 1


if __name__ == "__main__":
    sys.exit(main())
