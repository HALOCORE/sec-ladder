#!/usr/bin/env python3
"""Leaf-by-leaf diff of two gate JSONs -- ../NOTES.md 11a's churn scope.

    cp results/gate/p27-handle-table.json /tmp-less/A.json   # .temp/, not /tmp
    harness/check.py p27
    python3 patterns/p27-handle-table/controls/gatediff.py A.json \
            results/gate/p27-handle-table.json

Nothing here is p27-specific; it lives in this pattern's controls/ because
../NOTES.md 11a quotes its output and a quoted number needs a generator. p27
needs it because TWO of its adversarial inputs are deliberately
non-reproducible (7), so its gate record churns on every run and a reviewer
diffing two runs has to be able to tell that churn from a tree that moved.
"""
import json, sys, collections
def leaves(o, p="", out=None):
    if out is None: out = {}
    if isinstance(o, dict):
        for k, v in o.items(): leaves(v, f"{p}/{k}", out)
    elif isinstance(o, list):
        for i, v in enumerate(o): leaves(v, f"{p}[{i}]", out)
    else: out[p] = o
    return out
a, b = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
la, lb = leaves(a), leaves(b)
keys = set(la) | set(lb)
ch = [k for k in sorted(keys) if la.get(k, "<absent>") != lb.get(k, "<absent>")]
print(f"verdict: {a.get('verdict')} -> {b.get('verdict')} | "
      f"failures: {len(a.get('failures',[]))} -> {len(b.get('failures',[]))} | "
      f"contract_sha256 {'unchanged' if a.get('contract_sha256')==b.get('contract_sha256') else 'CHANGED'}")
print(f"changed leaves: {len(ch)} of {len(keys)}")
# The three benign categories, named rather than lumped: an "adversarial" bucket
# large enough to hide one real change is not a scope note. Anything that is not
# one of the three prints its own path and is a finding.
cat, per_input = collections.Counter(), collections.Counter()
for k in ch:
    tail = k.rsplit("/", 1)[-1]
    if "==" in str(la.get(k)):
        cat["ASan ==<pid>== in the recorded diagnostic"] += 1
    elif "adversarial" in k and ("stdout" in k or tail in ("checksum", "value")):
        cat["adversarial stdout value"] += 1
    elif "adversarial" in k and "cells" in k:
        cat["adversarial cells[] group permutation"] += 1
    else:
        cat["OTHER -- NOT CHURN: " + k] += 1
    for part in k.split("/"):
        if part.endswith(".bin"):
            per_input[part] += 1
            break
for k, v in cat.most_common():
    print(f"  {v:4d}  {k}")
print("  by input: " + ", ".join(f"{k[:-4]} {v}" for k, v in sorted(per_input.items())))
