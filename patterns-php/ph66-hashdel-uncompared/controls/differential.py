#!/usr/bin/env python3
"""ph66 control -- the SHIPPED C against `model.py`'s three implementations, on
windows no input file contains.

    python3 patterns-php/ph66-hashdel-uncompared/controls/differential.py
    python3 patterns-php/ph66-hashdel-uncompared/controls/differential.py --selftest

============================================================================
WHAT IT CLOSES, AND WHY NEITHER `model.py::selfcheck` NOR THE GATE CLOSES IT
============================================================================
`model.py::selfcheck` drives its three Python implementations against each
other. The gate drives every built CELL against `model.py` -- but only on the
six files in `inputs/`, and only on the windows the checksum-derived index
actually selects. Neither of those is the edge this file measures:

  ⭐ **the SHIPPED `c/kernel.c` and `c/kernel_hardened.c` against the model, on
  windows chosen HERE.**

Three claims rest on that edge and are otherwise assertions:

  1. ⚠⚠ **THE KEY PACKING.** C carries `char arKey[1]` and compares with
     `memcmp(p->arKey, arKey, nKeyLength)`; all four Rust rungs and the model
     carry the key as ONE `u64`, zero-filled past `nKeyLength`, and compare with
     `==`. `PROTOCOL_PHP.md` §A1 clause (c) requires a substitution inside a
     `verbatim` tier to be **DEMONSTRATED behaviour-preserving over the
     reachable domain by a differential with a must-fire control -- not
     asserted.** This is that differential.
  2. **THE HASH UNROLLING.** `zend_inline_hash_func` is unrolled eight times
     with a `switch` tail; every other rung writes the rolled loop. Key lengths
     here span `nKeyLength` 2..8, which straddles the `>= 8` arm.
  3. **THE ALLOCATOR TALLY.** The C links `common-php/emalloc_shim.h`; the Rust
     rungs and the model reproduce `php_shim_tally()` ARITHMETICALLY. If the
     size-class cache model drifted, the u64 would move and this is where it
     shows.

⛔ **AND THE MUST-FIRE CONTROL IS THE HALF THAT MAKES IT EVIDENCE** (`§H`). A
differential that always agrees proves nothing until it has been shown able to
disagree, so `--selftest` runs four MUTATIONS of the model -- one per claim plus
the defect itself -- and requires each to be caught. They are applied to a COPY
of the model's functions, never to `model.py`.
"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
sys.path.insert(0, ROW)
sys.path.insert(0, HERE)
import model  # noqa: E402
import _pin   # noqa: E402

WORK = os.path.join(REPO, ".temp", "ph66-controls")

#: The scratch driver: read a window as hex from argv, print `kernel()`.
DRIVER_C = r"""
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
uint64_t kernel(const uint8_t *buf, size_t off, size_t len);
static int hexv(int c){ if(c>='0'&&c<='9')return c-'0';
  if(c>='a'&&c<='f')return c-'a'+10; if(c>='A'&&c<='F')return c-'A'+10; return -1; }
int main(int argc, char **argv){ static uint8_t b[1<<20]; size_t n=0; const char*h;
  if(argc<2) return 2; h=argv[1];
  while(h[0]&&h[1]){ int a=hexv(h[0]),c=hexv(h[1]); if(a<0||c<0) return 3;
    b[n++]=(uint8_t)((a<<4)|c); h+=2; }
  printf("%llu\n",(unsigned long long)kernel(b,0,n)); return 0; }
"""


def build():
    """Compile R1 and R1h against the scratch driver. Returns the two paths."""
    os.makedirs(WORK, exist_ok=True)
    drv = os.path.join(WORK, "diffdrv.c")
    with open(drv, "w") as f:
        f.write(DRIVER_C)
    out = []
    for k in ("kernel", "kernel_hardened"):
        exe = os.path.join(WORK, "diff_" + k)
        cmd = ["gcc", "-std=c99", "-Wall", "-Wextra", "-O1", "-DSLB_ISOLATED",
               "-I", os.path.join(REPO, "common-php"),
               "-I", os.path.join(REPO, "common"),
               "-I", os.path.join(ROW, "c"),
               drv, os.path.join(ROW, "c", k + ".c"), "-o", exe]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f"build failed for {k}:\n{r.stderr}")
        out.append(exe)
    return out


def run_c(exe, win):
    r = subprocess.run([exe, win.hex()], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"{exe} exited {r.returncode}: {r.stderr}")
    return int(r.stdout.strip())


def windows():
    """Windows chosen HERE. The shipped `inputs/` are deliberately excluded --
    the gate already drives those -- so every window below is off-corpus."""
    out = list(model.Model._synthetic_windows())
    # a long deterministic stream per (nrec) shape, so several table sizes and
    # therefore several chain-depth regimes are exercised
    for nrec in (1, 2, 3, 5, 8, 9, 16, 17, 31, 32, 64, 127):
        st = 0x243F6A8885A308D3 + nrec
        w = bytearray()
        for _ in range(nrec):
            st = (st * 6364136223846793005 + 1442695040888963407) & model.MASK
            w += bytes([(st >> 11) & 0xFF, (st >> 19) & 0xFF,
                        (st >> 27) & 0xFF, (st >> 35) & 0xFF])
        out.append(bytes(w))
    # every (op, kind, coll) triple against every one of the 64 selectors, in
    # pairs, so `nKeyLength` 2..8 is swept against both insert functions
    for sel in range(model.NKEY):
        out.append(model.Model._rec(0, 0, 0, sel, 0x55)
                   + model.Model._rec(0, 1, 1, sel, 0x66)
                   + model.Model._rec(1, 0, 0, sel)
                   + model.Model._rec(1, 1, 1, sel))
    return out


def compare(r1, r1h, wins, sim=None, rec=None, dumb=None, hard=None):
    """-> (n, [disagreements]). The four implementations are parameters so the
    selftest can pass MUTATED copies without touching `model.py`."""
    sim = sim or (lambda w: model.simulate(w, hardened=False))
    hard = hard or (lambda w: model.simulate(w, hardened=True))
    rec = rec or (lambda w: model.Model.hash_fold(model.Model, w, 0, len(w)))
    dumb = dumb or (lambda w: model._dumb(w, hardened=False))
    bad = []
    for w in wins:
        if len(w) < model.REC:
            continue
        c1 = run_c(r1, w)
        c1h = run_c(r1h, w)
        a, b, c, h = sim(w), rec(w), dumb(w), hard(w)
        if not (c1 == a == b == c):
            bad.append(f"R1 {w.hex()[:40]}: C={c1} sim={a} recursive={b} dumb={c}")
        if c1h != h:
            bad.append(f"R1h {w.hex()[:40]}: C={c1h} sim={h}")
    return len(wins), bad


# ==========================================================================
# the must-fire controls -- §H: a checker lands with its negatives INSIDE it
# ==========================================================================
def _mut_fold_prefix(w):
    """MUTATION 1 -- fold only the FIRST byte of each surviving key instead of
    all `nKeyLength` of them.

    ⭐⭐ THIS IS THE MUTATION THE PACKING CLAIM ACTUALLY NEEDS, AND THE ONE IT
    NEEDS IS NOT THE ONE THIS FILE FIRST TRIED. The first attempt mutated the
    key COMPARISON -- `memcmp` shortened to one byte -- and it **did not fire on
    a single window**, which is a result rather than a broken control: on this
    kernel's domain `memcmp` NEVER DECIDES ANYTHING. Every site that compares
    keys has already required `p->h == h` AND `p->nKeyLength == nKeyLength`, the
    64 keys have pairwise distinct 64-bit DJBX33A hashes
    (`inputs/gen.py::_check_keys` asserts it), and two DISTINCT keys with an
    equal 64-bit hash are exactly the object `patterns-php/CATALOGUE.md` asked
    for and `.tasks-php/probes/ph66_djbx33a_collide.py` shows is not
    constructible. ▶ So the byte comparison is EXECUTED on every match and
    always returns 0; the test that discriminates is the LENGTH one. `N2b`
    below mutates THAT. ../NOTES.md section 8 states it as a limitation of the
    fixture rather than leaving it in a control's comment.

    What this mutation does establish is the half that is not vacuous: the
    packed word's bytes are all OBSERVABLE, because the surviving-key fold reads
    every one of them."""
    nrec = len(w) // model.REC
    t = model._Table(nrec)
    for r in range(nrec):
        b = w[r * model.REC:(r + 1) * model.REC]
        op, kind, coll, sel, val = model.decode(b)
        key = model.key_of(sel)
        idx = model.djbx33a(key) if coll else model.plain_index(b)
        data = 0x10000 | val
        if op == 0 and kind == 0:
            t.ins_str(key, data)
        elif op == 0:
            t.ins_idx(idx, data)
        elif kind == 0:
            t.delete(key, len(key), 0, False)
        else:
            t.delete(None, 0, idx, False)
    return _fold_prefix(t)


def _fold_prefix(t):
    acc = 0
    p = t.lhead
    while p != model.NIL:
        n = t.a[p]
        acc = (acc * 31 + n.nkl) & model.MASK
        acc = (acc * 31 + n.h) & model.MASK
        for i in range(min(1, n.nkl)):      # <- ONE byte, not n.nkl of them
            acc = (acc * 31 + n.key[i]) & model.MASK
        acc = (acc * 31 + (n.data & 0xFFFF)) & model.MASK
        p = n.lnxt
    acc = (acc * 31 + t.nelem) & model.MASK
    acc = (acc * 31 + t.nnext) & model.MASK
    acc = (acc * 31 + t.ndtor) & model.MASK
    acc = (acc * 31 + t.dfold) & model.MASK
    acc = (acc * 31 + t.ndok) & model.MASK
    acc = (acc * 31 + t.ndfail) & model.MASK
    return (acc ^ t.al.tally()) & model.MASK


def _mut_nkl_dropped(w):
    """MUTATION 2b -- drop `p->nKeyLength == nKeyLength` from the STRING-KEY
    INSERT predicate (`zend_hash.c:215`).

    ⭐ That is the conjunct `b73349dbe4e9` HOISTS into the delete, and this
    mutation is what shows it is load-bearing: without it a string insert
    matches a NUMERIC bucket of the same `h`, which is the defect one function
    over."""
    nrec = len(w) // model.REC
    t = model._Table(nrec)
    for r in range(nrec):
        b = w[r * model.REC:(r + 1) * model.REC]
        op, kind, coll, sel, val = model.decode(b)
        key = model.key_of(sel)
        idx = model.djbx33a(key) if coll else model.plain_index(b)
        data = 0x10000 | val
        if op == 0 and kind == 0:
            _ins_str_nolen(t, key, data)
        elif op == 0:
            t.ins_idx(idx, data)
        elif kind == 0:
            t.delete(key, len(key), 0, False)
        else:
            t.delete(None, 0, idx, False)
    return t.fold()


def _ins_str_nolen(t, key, data):
    h = model.djbx33a(key)
    n_index = h & t.mask
    p = t.ar[n_index]
    while p != model.NIL:
        n = t.a[p]
        if n.h == h:                      # <- `p->nKeyLength == nKeyLength` GONE
            t._dtor(n.data)
            n.data = data
            return
        p = n.nxt
    req = model.BUCKET_BASE + len(key)
    t.al.alloc(req)
    t.a.append(model._Node(h, len(key), key, data, req))
    t._connect(len(t.a) - 1, n_index)


def _mut_hash_rolled_wrong(w):
    """MUTATION 2 -- hash only the first 7 bytes, i.e. drop `zend_inline_hash_
    func`'s unrolled `>= 8` arm. Invisible unless some key reaches
    `nKeyLength == 8`."""
    old = model.djbx33a
    try:
        model.djbx33a = lambda k: old(k[:7])
        return model.simulate(w, hardened=False)
    finally:
        model.djbx33a = old


def _mut_no_cache(w):
    """MUTATION 3 -- drop the size-class cache, so `n_cache_hit` stays 0 and
    `bytes_mallocked` counts every request. The tally then differs from the C's."""
    old = model.Alloc.alloc

    def noc(self, size):
        rsz = (size + 7) & ~7
        self.n_alloc += 1
        self.bytes += rsz
    try:
        model.Alloc.alloc = noc
        return model.simulate(w, hardened=False)
    finally:
        model.Alloc.alloc = old


def _mut_hardened(w):
    """MUTATION 4 -- the DEFECT itself: drive the model's HARDENED predicate
    against the SHIPPED `c/kernel.c`. If this did not fire, the row's whole
    R1-vs-R1h separation would be unmeasured."""
    return model.simulate(w, hardened=True)


def selftest(r1, r1h, wins):
    bad = []

    def ck(name, cond, why):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}: {why}")
        if not cond:
            bad.append(name)

    n, clean = compare(r1, r1h, wins)
    ck("N1", clean == [],
       f"the SHIPPED C agrees with all three model implementations on {n} "
       f"off-corpus windows, on BOTH rungs"
       + ("" if clean == [] else f" -- got {clean[:3]}"))

    for name, fn, why in (
        ("N2a", _mut_fold_prefix,
         "folding only the FIRST byte of each surviving key is CAUGHT, so every "
         "byte of the packed word is observable in the u64 -- the half of the "
         "packing substitution that is not vacuous (PROTOCOL_PHP.md A1 (c))"),
        ("N2b", _mut_nkl_dropped,
         "dropping `p->nKeyLength == nKeyLength` from the string-key INSERT is "
         "CAUGHT -- that conjunct is the one b73349dbe4e9 hoists into the "
         "delete, and this is it being load-bearing one function over"),
        ("N3", _mut_hash_rolled_wrong,
         "dropping zend_inline_hash_func's unrolled `>= 8` arm is CAUGHT, so "
         "the corpus really does reach nKeyLength 8"),
        ("N4", _mut_no_cache,
         "dropping zend_alloc.c's size-class cache is CAUGHT, so the Rust and "
         "Python tallies are checked against the SHIPPED shim and not against "
         "each other"),
        ("N5", _mut_hardened,
         "driving the HARDENED predicate against the SHIPPED c/kernel.c is "
         "CAUGHT -- the row's own R1-vs-R1h separation, measured"),
    ):
        _, hits = compare(r1, r1h, wins, sim=fn)
        ck(name, hits != [], why + f" ({len(hits)} disagreement(s))")

    print("\nSELFTEST " + ("FAIL: " + " ".join(bad) if bad else "PASS"))
    return 1 if bad else 0


def _write(rec):
    rec.update(_pin.pin(["c/kernel.c", "c/kernel_hardened.c", "c/kernel.h",
                         "model.py"],
                        "python3 controls/differential.py --selftest",
                        "builds two C binaries and drives them over 94 "
                        "off-corpus windows; seconds"))
    with open(os.path.join(HERE, "differential.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"wrote controls/differential.json -- "
          f"{len(rec['problems'])} problem(s)")
    return 1 if rec["problems"] else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    r1, r1h = build()
    wins = windows()
    if a.selftest:
        rc = selftest(r1, r1h, wins)
        n, bad = compare(r1, r1h, wins)
        return _write({"windows": n, "selftest_rc": rc, "arms": 6,
                       "problems": (bad + ([f"selftest rc={rc}"] if rc else []))})
    n, bad = compare(r1, r1h, wins)
    print(f"  windows: {n}")
    if bad:
        print("  ⛔ DISAGREEMENTS:")
        for b in bad[:20]:
            print(f"    {b}")
    else:
        print("  ✅ the shipped C agrees with model.py's simulation, its "
              "recursive spelling and its link-free spelling on every window, "
              "on BOTH rungs.")
        print("  ⓘ run with --selftest for the five must-fire mutations, which "
              "is what makes the agreement evidence.")
    return _write({"windows": n, "selftest_rc": None, "arms": 6,
                   "problems": bad})


if __name__ == "__main__":
    raise SystemExit(main())
