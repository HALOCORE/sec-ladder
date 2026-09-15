#!/usr/bin/env python3
"""ph96 -- is `c/kernel_hardened.c` really `cf020f133487`, and does the patch apply?

    python3 patterns-php/ph96-outparam-unwritten/controls/r1h_backport.py

=============================================================================
THE THREE QUESTIONS, AND THE THIRD IS WHY THIS ROW SAYS **BACKPORT**
=============================================================================
1. **Does the cached patch BIND?** Its `From` sha must match its filename
   (`RECAP_PHP.md` F115: three cached patches in this corpus do not).
2. **Does `git apply` place it on pristine 5.0.0?** ⛔ **It does NOT**, at any
   context width, because the pre-image carries `SEPARATE_ARG_IF_REF(offset);`
   and `zval_ptr_dtor(&offset);` -- two lines an unrelated later change added.
3. **Does the hand backport reproduce upstream's own diffstat?** ✅ It does:
   `1 file changed, 1 insertion(+), 3 deletions(-)` against the commit header's
   `Zend/zend_object_handlers.c | 4 +---`. **That is the evidence the SEMANTIC
   change is upstream's and only the CONTEXT is not.**

⚠⚠ **THE VERDICT IS TAKEN FROM THE BYTES, NEVER FROM AN EXIT STATUS.** `ph55`
NOTES §5: `git apply --check` has lied on this project when the scratch path was
gitignored, and the manager's own first run of question 2 printed `EXIT=0`, which
was `head`'s status rather than `git apply`'s. Every verdict below reads a file.

⚠ The scratch `git init` repo lives under `.temp/php96/` and its toplevel is
asserted, so the outer repository's gitignore cannot reach it.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
import _pin  # noqa: E402

SHA = "cf020f133487d36a8b1d9cfd16ec456f7f07952e"
PATCH = os.path.join(HERE, "cf020f133487.patch")
TARBALL = ("/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/"
           "build-5.0.0/php-5.0.0.tar.gz")
SCRATCH = os.path.join(REPO, ".temp", "php96", "r1hctl")
SRC = "Zend/zend_object_handlers.c"

#: upstream's own diffstat, from the commit header in the cached patch.
WANT_STAT = "1 file changed, 1 insertion(+), 3 deletions(-)"


def _git(*a, cwd):
    return subprocess.run(["git"] + list(a), cwd=cwd, capture_output=True,
                          text=True)


def main():
    problems = []
    rec = {"commit": SHA, "problems": problems}

    # ---- 1. does the patch BIND? (F115) ---------------------------------
    txt = open(PATCH).read()
    m = re.match(r"From ([0-9a-f]{40}) ", txt)
    rec["from_sha"] = m.group(1) if m else None
    rec["filename_prefix"] = os.path.basename(PATCH).split(".")[0]
    binds = bool(m) and m.group(1).startswith(rec["filename_prefix"])
    rec["binds"] = binds
    print(f"1. BINDS?   From {rec['from_sha']}  filename "
          f"{rec['filename_prefix']}  -> {'YES' if binds else 'NO'}")
    if not binds:
        problems.append("the cached patch does not bind: its `From` sha does "
                        "not match its filename, which is F115's class and "
                        "means the bytes are some other commit's")

    # ---- stage the pristine file in its own git repo ---------------------
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "Zend"))
    with tarfile.open(TARBALL) as t:
        data = t.extractfile("php-5.0.0/" + SRC).read()
    open(os.path.join(SCRATCH, SRC), "wb").write(data)
    _git("init", "-q", ".", cwd=SCRATCH)
    top = _git("rev-parse", "--show-toplevel", cwd=SCRATCH).stdout.strip()
    rec["scratch_toplevel"] = top
    if os.path.realpath(top) != os.path.realpath(SCRATCH):
        problems.append(f"the scratch repo's toplevel is {top}, not {SCRATCH} "
                        f"-- `git init` did not take, so every verdict below "
                        f"is about the WRONG repository")
        return _finish(rec, problems)
    _git("-c", "user.email=a@b", "-c", "user.name=c", "add", "-A", cwd=SCRATCH)
    _git("-c", "user.email=a@b", "-c", "user.name=c", "commit", "-qm", "base",
         cwd=SCRATCH)

    # ---- 2. does `git apply` place it? ----------------------------------
    rec["apply_check"] = {}
    for flags in ([], ["-C1"], ["-C0"], ["-3"]):
        r = _git("apply", "--check", *flags, PATCH, cwd=SCRATCH)
        rec["apply_check"][" ".join(flags) or "(default)"] = r.returncode
        print(f"2. APPLY?   git apply --check {' '.join(flags) or '':10s} "
              f"rc={r.returncode}")
    applies = any(v == 0 for v in rec["apply_check"].values())
    rec["applies"] = applies
    # The pre-image lines 5.0.0 does not have -- read out of the patch, not
    # asserted, so a different cached patch would change this list.
    # ⚠ Only the lines BELOW the `@@` hunk header are context; the commit
    # header's own diffstat lines also begin with a space and are not.
    body = txt.split("@@", 2)[-1] if "@@" in txt else ""
    absent = [ln[1:].strip() for ln in body.splitlines()
              if ln.startswith(" ") and ln[1:].strip()
              and ln[1:].strip().encode("latin-1") not in data]
    rec["context_lines_absent_from_5_0_0"] = absent
    print(f"   context lines the patch expects and 5.0.0 does not have: {absent}")
    if applies:
        problems.append("the cached patch APPLIES to pristine 5.0.0, so this "
                        "row's `spec.md` is wrong to call R1h a BACKPORT and "
                        "should say it applies")
    if not absent:
        problems.append("the patch's pre-image context is entirely present in "
                        "5.0.0, so there is no explanation for the refusal and "
                        "the refusal itself needs re-checking")

    # ---- 3. does the hand backport reproduce upstream's diffstat? --------
    lines = data.decode("latin-1").split("\n")
    i509 = 508
    ok = (lines[i509].strip() == "zval *retval;"
          and "offsetunset" in lines[i509 + 3] and "&retval" in lines[i509 + 3]
          and lines[i509 + 4].strip() == "zval_ptr_dtor(&retval);")
    rec["preimage_shape_ok"] = ok
    if not ok:
        problems.append("the pristine file no longer has the three lines the "
                        "backport edits at :509/:512/:513; the citation has "
                        "drifted from the tarball")
        return _finish(rec, problems)
    lines[i509 + 3] = lines[i509 + 3].replace('"offsetunset", &retval, offset',
                                              '"offsetunset", NULL, offset')
    post = [l for k, l in enumerate(lines) if k not in (i509, i509 + 4)]
    open(os.path.join(SCRATCH, SRC), "w", encoding="latin-1").write(
        "\n".join(post))
    stat = _git("--no-pager", "diff", "--stat", cwd=SCRATCH).stdout.strip()
    rec["backport_diffstat"] = stat
    got = stat.splitlines()[-1].strip() if stat else ""
    rec["backport_diffstat_summary"] = got
    rec["upstream_diffstat_summary"] = WANT_STAT
    print(f"3. BACKPORT diffstat: {got!r}")
    print(f"   upstream's own:    {WANT_STAT!r}")
    if got != WANT_STAT:
        problems.append(f"the hand backport's diffstat {got!r} is not "
                        f"upstream's {WANT_STAT!r}, so the row cannot claim the "
                        f"semantic change is upstream's")

    # ---- 4. and is that what c/kernel_hardened.c actually does? ----------
    # FROM THE BYTES: the two C rungs must differ at the unset site and nowhere
    # else in their code.
    def body_of(path, fn):
        """The code lines of one function, comments stripped."""
        s = open(path).read()
        s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
        i = re.search(r"^(?:static|SLB_NOINLINE)[A-Za-z_ *0-9]*\b"
                      + fn + r"\(", s, re.M).start()
        j = s.index("\n}\n", i)
        return [" ".join(l.split()) for l in s[i:j].splitlines() if l.strip()]

    kc = os.path.join(PDIR, "c", "kernel.c")  # noqa: E501
    kh = os.path.join(PDIR, "c", "kernel_hardened.c")
    rec["site_diff"] = {}
    for fn in ("ph96_read_dimension", "ph96_write_dimension",
               "ph96_has_dimension", "ph96_unset_dimension",
               "ph96_call_method", "ph96_zval_ptr_dtor", "ph96_is_true",
               "ph96_call_function", "ph96_fold_zval", "kernel"):
        a, b = body_of(kc, fn), body_of(kh, fn)
        rec["site_diff"][fn] = {"r1_only": [l for l in a if l not in b],
                                "r1h_only": [l for l in b if l not in a]}
        same = a == b
        print(f"4. {fn:22s} {'IDENTICAL' if same else 'DIFFERS'}")
        if fn != "ph96_unset_dimension" and not same:
            problems.append(f"{fn} differs between the two C rungs; "
                            f"cf020f133487 touches the offsetunset site ONLY")
    d = rec["site_diff"]["ph96_unset_dimension"]
    print(f"   R1-only at the unset site:  {d['r1_only']}")
    print(f"   R1h-only at the unset site: {d['r1h_only']}")
    want_r1 = ["ph96_zval *retval;",
               "ph96_call_method(b, slot, &retval, n_rel, &core);",
               "ph96_zval_ptr_dtor(&retval, n_rel);"]
    if d["r1_only"] != want_r1:
        problems.append(f"the unset site's R1-only lines are {d['r1_only']}, "
                        f"want {want_r1} -- the local, the call and the dtor, "
                        f"which is the whole of cf020f133487")
    if d["r1h_only"] != ["ph96_call_method(b, slot, (ph96_zval **) 0, n_rel, &core);"]:
        problems.append(f"R1h's only added line at the unset site should be the "
                        f"NULL-passing call; it is {d['r1h_only']}")
    return _finish(rec, problems)


def _finish(rec, problems):
    rec.update(_pin.pin(["c/kernel.c", "c/kernel_hardened.c",
                         "controls/cf020f133487.patch"],
                        "python3 controls/r1h_backport.py",
                        "one tar extract, one git init, seconds"))
    with open(os.path.join(HERE, "r1h_backport.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/r1h_backport.json -- {len(problems)} problem(s)")
    for p in problems:
        print("  ⛔ " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
