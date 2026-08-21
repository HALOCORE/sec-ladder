# TASK_053_REPORT — sweeping every gate stage for the "skips a comparison in one branch" defect

**Role:** research reviewer, adversarial, against `harness/check.py` itself.
**Scope:** audit only. Nothing outside `.temp/p53/` was written. `harness/check.py`
was never invoked as a program; every reproduction imports it as a module, calls
one stage function, and rebinds `check.REPO` to a symlink farm under
`.temp/p53/<pid>/repo/` so that every write the stage makes lands there. **No gate
JSON was rewritten** — `git status` shows only other agents' concurrent work
(p12, TASK_054) and nothing of mine.

---

## Verdict on the manager's own uncertainty

> *"What I am least sure of is whether this sweep is worth its cost at all …
> If the sweep comes back with nothing that passes the accident test, say so
> plainly and say the rule was right."*

**The sweep does not come back clean, and rule 5 was not right here.** Six
candidates survive the accident test; **three are live on the shipped tree
today, measured, in the committed gate records** — one of them across all 16
patterns and 51 of 52 rows. That said, **two of the three prescriptions this
audit implies are the opposite of the obvious fix**, and both corrections are
measured, not argued (F2 and F3 below). Batching blindly would red-line all 16
patterns on F2 and false-fail 37 rows on 14 patterns on F3.

**None of the six is a `blocker`.** No published number moves; no cell's
verdict flips. What moves is what the gate *records* and what its transcript
*claims*.

---

## 1. The stage table — what each stage COULD compare vs what it DOES

`.memory/05-layout.md:268-271` names **16** stages; the file actually has **18**
`head()`-bearing gate stages. The list omits `idiom` (0b) and `derive_contract`
(5d0). One-line correction for `.memory/`.

| # | stage (fn) | line | could compare | does compare | gap |
|---|---|---|---|---|---|
| 0 | `check_selftests` | 539 | 3 module selftest rcs + 3 case tables | all six, each `got != want` | — |
| 0b | `check_idiom` / `idiom_audit` | 993 / 837 | `forbidden_hits` (decidable), `pins_nothing`, `absent` | prints all three; **fails/shouts on none** | **F6** |
| 1 | `check_build` | 1212 | build rc per cell; source mtime under `--no-build` | both | — |
| 2 | `check_checksums` | 1249 | exit, stdout vs `model.checksum`, cross-cell agreement | all three (stderr recorded only, by design) | ok-string count, m1 |
| 3a | `check_no_collapse` | 1285 | loop presence, body floor, memory operand, digests | all four | — |
| 3b | `check_marginal_ir` | 1365 | slope vs derived floor; `d(Ir)/d(work)`; rate/unit/bound consistency | all, with explicit shouts when a probe shape is missing | — |
| 3c | `check_identity` | 1752 | measured level vs `spec.md` pin, per pair per opt | yes; stronger-than-pinned reported not failed | — |
| 4 | `check_adversarial` | 1807 | exit, stdout, stderr, signal per (input, cell, opt, mode) vs model | prints every variant; **records exactly one** | **F1** |
| 5a | `check_verus_contract` | 2140 | item set, per-item `requires`/`ensures` vs pin, `external`, `in_verus`, `cfg`, obligation count, `unsafe` siting, parameter coverage | all of them; **parameter coverage reads comments as clause text** | **F4**, m2 |
| 5b | `check_call_site` | 2295 | `in_verus`, `external`, call presence, `--verify-function` verified/errors/resolved | all four | — |
| 5c | `check_clause_deletion` | 2493 | control verdict, `assert(false)` probe verdict, one mutant per `ensures` conjunct | control + conjuncts fully (incl. `mv is None`); **probe has no `pv is None` arm** | **F5a** |
| 5c-req | `check_requires_strength` | 2804 | control, tautology battery over 3 tactics, deletion for verified items | control, bare-Z3 arm fully (`nocompile`/`perturbed`/`tautology`), deletion fully; **tactic arms have no `pv is None` case** | **F2** |
| 5c-twin | `check_trusted_twins` | 3199 | cfg hygiene, twin shape (6 rules), `--cfg` verdict vs `twin_obligations`, per-conjunct vacuity probe, NOTES.md argument | all except: **vacuity probe has no `dv is None` arm** | **F5b** |
| 5d0 | `derive_contract` | 3616 | derived Python vs declared `contract.requires/ensures`, and Python-compilability | both | — |
| 5d | `check_proof_domain` | 3688 | `requires` on every call, `ensures` on sampled calls, per input incl. adversarial; vacuity at 3 levels | all | — |
| 6 | `check_driver_identity` (+`_check_region_executes`, `_check_region_runs`) | 4249 | region set vs pin, token sequence vs canonical, statement count, one-call-in-region, enclosing-fn exclusive Ir, kernel caller set | all; explicit n==0 failure arms on both dynamic limbs | — |
| 7 | `check_sanitizers` | 4364 | `fired`, exit vs model, **stdout vs model**, diagnostic | `fired` + exit (clean rows only); **stdout bound and dropped** | **F3** |
| 8 | `check_miri` | 4467 | UB, exit vs model, stdout vs model | all three, unconditionally (fixed at TASK_052) | — |

---

## 2. Findings

### F2 — `major` — 5c-req's `by (bit_vector)` arm has aborted on 51 of 52 shipped conjuncts, and the stage's `ok` line names it anyway

**`harness/check.py:2799-2801`** (`_run_taut_battery`), with the `ok` line at
**`check.py:2998-3009`** and the per-clause print at **`check.py:2950-2956`**.

```python
        if tac is None:
            if pv is None:
                return "nocompile", pv, pe, po, tac      # <-- the arm that exists
            ...
        elif pv is not None and pe == 0:                 # <-- and the one that does not
            return "tautology", pv, pe, po, tac
    return "not a tautology", pv, pe, po, used
```

`by (bit_vector)` cannot take an assertion mentioning `v@.len()`; Verus aborts
with *"error: aborting due to 1 previous error"* and **no `N verified, M errors`
line at all**, so `_verus` returns `(None, None)`. The tactic arm has no case
for that, so control falls to `return "not a tautology"` — carrying the aborted
run's `pv=None, pe=None, used="bit_vector"` into the record.

**Measured, not reasoned.** Real Verus, `.temp/p53/probe_taut.py`:

```
### p01-array-sum get_unchecked  clause 'i < v@.len()'
control: 7 verified, 0 errors
  tactic None            : verified=7    errors=1
  tactic 'nonlinear_arith': verified=8   errors=1
  tactic 'bit_vector'    : verified=None errors=None
      --> ... assert(i < v@.len()) by (bit_vector); ... error: aborting due to 1 previous error
verdict from _run_taut_battery: ('not a tautology', None)
```
Same result on `p08-overlap-move copy_in` and `p09-bitset kernel`.

**Blast radius — live, in the committed records, on every pattern.** Across the
16 full-run gate JSONs there are 52 `test:"tautology"` rows. **51 carry
`"verified": null, "errors": null, "tactic": "bit_vector", "verdict": "not a
tautology"`.** The single exception is `p08 move_right`'s `0 < dr <= m`, the
only conjunct in the project with no `@` in it (12 verified, 2 errors — the arm
ran). Every one of the 16 gate transcripts prints
`… is not a tautology (bare Z3, \`by (nonlinear_arith)\`, \`by (bit_vector)\`)`
and the `ok` line asserts *"no `requires` conjunct is a tautology under bare Z3
or `by (nonlinear_arith)` or `by (bit_vector)`"*.

**Accident test: PASSES.** The `tac is None` branch three lines up has the
`nocompile` return; whoever added the tactic loop did not carry it into the
`elif`. Nothing adversarial is required.

**⚠ The obvious fix is wrong, and this is the measurement that says so.** A
`return "nocompile"` in the tactic arm would hard-fail **all 16 patterns
immediately**, because `by (bit_vector)` is *genuinely inapplicable* to a clause
mentioning a slice length — that is Verus behaving correctly. And there is **no
false negative to recover**: a tactic that aborts cannot prove anything, so a
clause that aborts `bit_vector` could never have been caught by it. **The
soundness of 5c-req is intact; what is wrong is the claim.** The fix is to
record the tactic as *inapplicable* and stop naming it.

```diff
--- a/harness/check.py
+++ b/harness/check.py
@@ def _run_taut_battery(txt, item, a, b, tag, mpath, base_v):
-    """(verdict, verified, errors, output, tactic) for one `requires` conjunct.
+    """(verdict, verified, errors, output, tactic, inapplicable) for one
+    `requires` conjunct.
@@
     pv = pe = None
     po, used = "", None
+    inapplicable = []
     for tac in _TAUT_TACTICS:
         probe, whynot = _taut_probe(txt, item, a, b, tag, tac)
         if probe is None:
-            return "unsynthesisable", None, None, whynot, tac
+            return "unsynthesisable", None, None, whynot, tac, inapplicable
         open(mpath, "w").write(probe)
         pv, pe, po = _verus(mpath)
         used = tac
         if tac is None:
             if pv is None:
-                return "nocompile", pv, pe, po, tac
+                return "nocompile", pv, pe, po, tac, inapplicable
             if pe == 0:
-                return "tautology", pv, pe, po, tac
+                return "tautology", pv, pe, po, tac, inapplicable
             if pe != 1 or pv != base_v:
-                return "perturbed", pv, pe, po, tac
+                return "perturbed", pv, pe, po, tac, inapplicable
+        elif pv is None:
+            # The tactic could not be APPLIED: `by (bit_vector)` aborts on any
+            # assertion mentioning `v@.len()`, and Verus then emits no
+            # `N verified, M errors` line at all. That is not a negative
+            # result, and it is not a failure either -- a tactic that aborts
+            # could not have proved the clause. TASK_053: 51 of the project's
+            # 52 shipped conjuncts land here, and the `ok` line below used to
+            # name `by (bit_vector)` as a tactic that had judged them.
+            inapplicable.append(tac)
+            continue
         elif pv is not None and pe == 0:
-            return "tautology", pv, pe, po, tac
-    return "not a tautology", pv, pe, po, used
+            return "tautology", pv, pe, po, tac, inapplicable
+    return "not a tautology", pv, pe, po, used, inapplicable
@@ def check_requires_strength(...)
-                    verdict, pv, pe, po, used = _run_taut_battery(
+                    verdict, pv, pe, po, used, inapp = _run_taut_battery(
                         txt, it, a, b, f"{it.name}_{idx}_{jdx}", mpath, base_v)
                     rows.append(dict(item=it.name, kind=why, clause=ctext,
                                      test="tautology", tactic=used,
+                                     tactics_tried=[t for t in _TAUT_TACTICS
+                                                    if t not in inapp],
+                                     tactics_inapplicable=inapp,
                                      verified=pv, errors=pe, verdict=verdict))
@@
                         print(f"    {src}: {it.name} requires[{idx}]"
                               + (f".conjunct[{jdx}]" if len(cj["spans"]) > 1
                                  else "")
                               + f" is not a tautology (bare Z3, "
                               + ", ".join(f"`by ({t})`" for t in _TAUT_TACTICS
-                                          if t)
+                                          if t and t not in inapp)
+                              + ("; INAPPLICABLE here: "
+                                 + ", ".join(f"`by ({t})`" for t in inapp)
+                                 if inapp else "")
                               + f") -- {ctext[:52]}")
```
…and the same `t not in inapp` filter in the `rep.ok` at `check.py:3001`, plus
one clause naming how many conjuncts had a tactic go inapplicable.

**Reproduction:** `.temp/p53/probe_taut.py <pattern> <item> <clause-index>`.

---

### F3 — `major` — stage 7 binds the ASan+UBSan build's stdout and drops it; it differs from the model on 37 of 114 rows today

**`harness/check.py:4405`** (`rc, so, se = run_bin(...)` — `so` occurs exactly
once in the function), record at **`4411-4412`**, comparison chain at
**`4413-4431`**. Reported at TASK_051_REVIEW; **no reproduction had been built
and the reachability argument had not been verified.** Both are done here.

**Reachability argument — verified.** `build.py:67` sets `OPTS = ["O0", "O3"]`.
Stage 7 compiles its own binary at **`-O1 -fsanitize=address,undefined
-static-libasan -static-libubsan -DSLB_ISOLATED`** into
`.temp/build/<pat>/c-gcc-asan` and **never puts it in `built`**, so
`check_checksums` (which iterates `built`) cannot reach it. It is the only C
configuration in the whole gate at `-O1`, the only one with sanitizer redzones
and a shifted allocator layout, and **its output is compared to nothing and
recorded nowhere.**

**Reproduction with the real function** (`.temp/p53/repro_san.py`): p01's
`c/kernel.c` with one character changed (`i < len` → `i + 1 < len`, an
off-by-one — the honest-mistake shape), fed to the unmodified
`check.check_sanitizers`:

```
== 7. C rung under ASan + UBSan (per-input expectation) ==============
    ok   adversarial.bin              clean, exit=0 (model 0)
    ok   small.bin                    clean, exit=0 (model 0)
rep.failures from stage 7: NONE  <-- stage 7 is GREEN
=== what the ASan binary actually printed ===
  small.bin   rc=0 stdout='2507258345488692275' model_stdout='17245669606222259694'  *** MISMATCH -- never compared ***
```

**⚠ The obvious fix — "compare it, like Miri now does" — is wrong, and this is
the measurement.** I ran stage 7's build for **all 16 patterns** and compared
the stdout it drops (`.temp/p53/san_sweep.py`):

```
TOTAL: 114 (input, pattern) rows; 37 where the ASan build's stdout differs
from model.py and stage 7 never looked
```

**All 37 are `adversarial-*` inputs. Zero non-adversarial rows differ.** On an
adversarial input the C rung diverging from the model *is the pattern's result*
(`.memory/02-bench-rules.md`, and `check_adversarial` exists precisely to record
rather than require it), so an unconditional comparison would false-fail **37
rows across 14 patterns** — including 6 declared `sanitizer_expect: "clean"`
(p04 `adversarial-overwrite`, p06 `adversarial-inarray`, p09 `adversarial-edge`,
p17 `adversarial-crosswin-hi`/`-lo`/`-leak`), which are the silent-wrong-answer
rows those patterns are *about*.

**Accident test: PASSES**, but narrowly and honestly stated: I could not
construct a live case where `-O1 + fsanitize` diverges from O0/O3 on a
well-formed input, and none exists on the shipped tree (77 of 77 non-adversarial
rows match). What passes the test is the *class*: the only C build in the gate
at an unmeasured optimisation level, with a different allocator layout, running
kernels whose whole subject is out-of-range memory, with its output compared to
nothing and **absent from the gate JSON so a reviewer cannot check it either**.

```diff
--- a/harness/check.py
+++ b/harness/check.py
@@ def check_sanitizers(pdir, rep, indir, models):
     for name, mod in sorted(models.items()):
         rc, so, se = run_bin(out, os.path.join(indir, name))
+        got = so.strip()
         expect = sbg(mod, "sanitizer_expect")
         m_exit = sbg(mod, "expected_exit")
+        want_out = (sbg(mod, "expected_stdout") or "").strip()
         fired = ("runtime error" in se or "AddressSanitizer" in se
                  or "UndefinedBehaviorSanitizer" in se or "ERROR:" in se)
         diag = re.sub(r"\s+", " ", se.strip())[:300]
         res[name] = {"exit": rc, "expected_exit": m_exit,
-                     "expect": expect, "fired": fired, "diagnostic": diag}
+                     "expect": expect, "fired": fired, "diagnostic": diag,
+                     # TASK_053: bound and dropped since the stage was written.
+                     # Recorded unconditionally, compared only where a
+                     # comparison is meaningful -- see below.
+                     "stdout": got, "model_stdout": want_out}
@@
         elif rc != m_exit:
             # the old version printed the exit code and ignored it entirely
             rep.fail("sanitizer", f"{name}: exit {rc}, model expects {m_exit}")
+        elif not name.startswith("adversarial") and got != want_out:
+            # This is the ONLY C configuration in the gate at -O1 and the only
+            # one built with -fsanitize, so step 2 (OPTS = ["O0", "O3"], and
+            # this binary is not in `built` at all) never runs it. Scoped to
+            # non-adversarial inputs deliberately: on the shipped tree 37 of
+            # 114 rows diverge and every one of them is adversarial, where
+            # divergence from the model IS the result (TASK_053).
+            rep.fail("sanitizer",
+                     f"{name}: the ASan+UBSan build printed {got!r}, model says "
+                     f"{want_out!r}. Nothing else in the gate runs a C binary "
+                     f"at -O1 or under -fsanitize, so no other stage can see "
+                     f"this.")
         else:
-            print(f"    ok   {name:28s} clean, exit={rc} (model {m_exit})")
+            print(f"    ok   {name:28s} clean, exit={rc} (model {m_exit}), "
+                  f"stdout {got!r}"
+                  + ("  [adversarial: recorded, not required to agree]"
+                     if name.startswith("adversarial")
+                     else " matches the model"))
```
**Cost on the shipped tree: zero new failures** (all 77 non-adversarial rows
already match), and 114 rows gain a `stdout`/`model_stdout` pair a reviewer can
diff. The `expect == "fires"` branch keeps recording only — that is the
documented decision at `check.py:4380-4384` and it is correct.

**Minor, same function:** stage 7 does not `os.makedirs` its output directory
(`check.py:4387`); it works only because `build.py` created it earlier in the
run. Under `--no-build` on a fresh clone it fails with a raw `ld: cannot open
output file` (hit during this audit). One line.

**Reproduction:** `.temp/p53/repro_san.py` and `.temp/p53/san_sweep.py`.

---

### F1 — `major` — stage 4 records **one** adversarial behaviour per (input, cell) and prints N; live on 7 patterns, up to 4 dropped per row

**`harness/check.py:1822-1825`.**

```python
            for rc, out, err, sig in sorted(seen, key=str):
                table[f"{name}/{c}"] = dict(exit=rc, stdout=out, stderr=err,
                                            signal=sig, model_exit=m_exit,
                                            model_stdout=m_out.strip())
```
The assignment is *inside* the loop, so the last element of
`sorted(seen, key=str)` wins — an ordering by the `str()` of the tuple, i.e.
lexicographic on the stdout string. The row carries **no `opt`/`mode` key**, so
the record does not say which of the four cells it came from, and `rep.note`
one line later says only *how many* were dropped.

**Live today**, from the committed records: 22 `opt/mode variants of this rung
disagree` notes across **p02 (2 rows × 2), p03 (4 × 4), p05 (2 × 4), p06 (2×2 +
2×4), p12 (2), p13 (8), p14 (4)**.

**Reproduction with the real function** (`.temp/p53/repro_adv.py p03-bounded-stack`,
driving `check.check_adversarial` over the already-built p03 binaries):

```
  adversarial-allpop.bin/c-gcc: 4 distinct
      ('O0', 'isolated')  -> (0, '15194360732743077888', '')
      ('O0', 'whole')     -> (0, '9462787543073015552', '')
      ('O3', 'isolated')  -> (0, '13268475638711343872', '')
      ('O3', 'whole')     -> (0, '8620288420891183616', '')
      RECORDED -> exit=0 stdout='6651391795963020928'
```
(p03's values are ASLR-dependent and that *is* documented — `p03/spec.md:94`,
`README.md:49`. The finding is the 4→1 collapse, not the nondeterminism.)

**Accident test: PASSES.** Assignment-in-loop instead of accumulate-in-loop.
Nothing adversarial. And it defeats a check the project's own reviewer
checklist demands: *"Adversarial behaviour recorded per rung rather than swept
up?"* (`PROTOCOL.md`) — this is the sweeping-up.

```diff
--- a/harness/check.py
+++ b/harness/check.py
@@ def check_adversarial(built, rep, adv_models, indir, cells):
         for c in cells:
-            seen = set()
+            seen = {}
             for (cc, o, m), path in sorted(built.items()):
                 if cc != c or not path:
                     continue
                 rc, out, err = run_bin(path, os.path.join(indir, name))
                 sig = -rc if rc is not None and rc < 0 else None
-                seen.add((rc, out.strip(), err.strip()[:120], sig))
-            for rc, out, err, sig in sorted(seen, key=str):
-                table[f"{name}/{c}"] = dict(exit=rc, stdout=out, stderr=err,
-                                            signal=sig, model_exit=m_exit,
-                                            model_stdout=m_out.strip())
+                seen.setdefault((rc, out.strip(), err.strip()[:120], sig),
+                                []).append(f"{o}/{m}")
+            # A LIST, always. This used to be a single assignment inside the
+            # loop, so a rung whose opt/mode variants disagree had N-1 of its
+            # behaviours dropped and the survivor was whichever sorted last by
+            # `str()` -- with no opt/mode label saying which cell it was
+            # (TASK_053: live on 7 patterns, up to 4 behaviours per row).
+            rows = []
+            for (rc, out, err, sig), where in sorted(seen.items(), key=str):
+                rows.append(dict(exit=rc, stdout=out, stderr=err, signal=sig,
+                                 cells=sorted(where), model_exit=m_exit,
+                                 model_stdout=m_out.strip(),
+                                 diverges=(rc != m_exit or out != m_out.strip())))
+            table[f"{name}/{c}"] = rows
+            for r in rows:
+                flag = "  <-- diverges from model" if r["diverges"] else ""
                 print(f"       {c:18s} exit={rc!s:5s} stdout={out!r:24s}"
                       f" stderr={err!r:60s}{flag}")
```
(the `flag` computation at `1826-1828` folds into `diverges`, which is also now
*recorded* rather than only printed.)

**⚠ This changes the shape of the `adversarial` key in all 16 gate JSONs** from
`{key: object}` to `{key: [object, …]}`. I grepped: **nothing reads it
programmatically** (`harness/report.py` has no reference; `measure.py` reads
`results/gate/*.json` for staleness only). Prose citations exist —
`patterns/p06-rotate/spec.md:738` and `.tasks/TASK_048.md:143` — and both cite
the row by key, which survives. If the manager prefers the shape not to move,
`rows if len(rows) > 1 else rows[0]` keeps the common case identical, at the
cost of a union type.

---

### F4 — `major` — a comment inside a trusted item's `requires` satisfies the parameter-coverage rule, which is the rule that catches `requires n >= 0`

**`harness/check.py:2089`** (`_check_trusted_unsafe`).

```python
            body_ids = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", i.body or ""))
            req_ids  = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", " ".join(reqs)))
            used = [p for p in pars if p in body_ids]
            bare = [p for p in used if p not in req_ids]
```
`vparse` returns a comment inside a `requires` list **as clause text** — as its
own clause when it trails, or glued onto the front of the clause when it
precedes. `req_ids` is a bag of every identifier-shaped token in the joined
text, so a parameter name that appears **only in a comment** counts as
constrained and `bare` comes back empty.

This is the rule `.memory/04-verus.md` and TASK_006_REVIEW built specifically
because *no verify/fail oracle can catch a too-weak trusted precondition*
(deleting one only removes obligations from callers). 5c-req's own docstring
lists it as the check that "Catches M1, M2 and M3".

**Reproduction** (`.temp/p53/repro_comment_clause.py`, real Verus):

```
### A trailing // comment after the last clause
  vparse requires  = ['i + n < v@.len()', '// `n` is bounded by the caller']
  5a param coverage: used=['v','i','n'] bare=[] -> PASS (rule satisfied)
  control verify   : 2 verified, 0 errors
  5c-req requires[0].0 'i + n < v@.len()'  -> not a tautology
### B // comment line BEFORE the clause
  vparse requires  = ['// `n` is bounded by the caller i < v@.len()']
  5a param coverage: used=['v','i','n'] bare=[] -> PASS
### C /* block */ comment after the last clause
  vparse requires  = ['i < v@.len()', '/* `n` is bounded by the caller */']
  5a param coverage: used=['v','i','n'] bare=[] -> PASS
### Z control: identical item, comment removed
  5a param coverage: used=['v','i','n'] bare=['n'] -> FAIL (caught)
```
The item's body is
`unsafe { let _ = *v.get_unchecked(i + n); *v.get_unchecked(i) }` — an unchecked
read at `i + n` with **nothing in the real `requires` constraining `n`** — and
in A, B and C the gate does not object. `vparse.conjunct_spans` drops the
comment-only clause, so **5c-req never tries to compile it and never fires
`nocompile`**: no other stage catches it. (Checked: for the *kernel*'s clauses
`derive_contract` would catch it, because `compile('// …', '<d>', 'eval')` is a
SyntaxError — but trusted items are not translated.)

**Accident test: PASSES, and this is the strongest of the six.** The defect the
rule exists to catch is "you knew the constraint and forgot to write the
clause". The bypass is "you wrote the constraint *in the comment* and forgot to
write the clause" — the same mistake, one line apart. And `req_ids` matches any
identifier-shaped token, so ordinary English in a comment (`n`, `len`, `src`,
`dst`, `off`) suffices; a comment reading *"`dst` is written, never read as an
address"* — which is exactly what `verus.unsafe_justifications` exists for —
makes `dst` look constrained and turns a shouted hatch into a silent pass.

**Blast radius: latent, zero live instances.** I recomputed `bare` for every
`external_body` item in all 16 `verus.rs` with and without comment blanking:
**0 comment-bearing clauses on the shipped tree, 0 items where the two answers
differ.** So the fix moves no gate record.

```diff
--- a/harness/check.py
+++ b/harness/check.py
@@ def _check_trusted_unsafe(rep, src, tcb, justifications):
             body_ids = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", i.body or ""))
-            req_ids = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", " ".join(reqs)))
+            # A COMMENT IS NOT CLAUSE TEXT. `vparse` hands back a `//` or
+            # `/* */` inside a `requires` list as clause text -- as its own
+            # clause when it trails, glued to the front of the clause when it
+            # precedes -- and this rule is a bag of identifiers, so a
+            # parameter named only in a comment used to count as constrained.
+            # `requires i < v@.len(),  // n is bounded by the caller` on an
+            # item whose body reads `i + n` passed this rule, 5c-req and 5a
+            # alike (TASK_053). The same item with the comment deleted fails.
+            req_ids = set(re.findall(
+                r"[A-Za-z_][A-Za-z0-9_]*",
+                " ".join(vparse.blank_noncode(c) for c in reqs)))
```

**Two things the manager must know before batching this.**
1. It closes A and C cleanly. For **B** (comment *before* the clause) `vparse`
   has already collapsed the newline, so blanking the `//` erases the real
   clause too and the item hard-fails naming *every* parameter — loud and
   safe, but the message will read as nonsense. The complete repair belongs in
   `vparse`: drop comment-only clauses and strip a leading comment from a
   clause's text. That is outside this audit's scope and outside `check.py`.
2. The failure message at `check.py:2093-2106` should gain one sentence: *"if
   the constraint is stated in a comment beside the clause, it is not stated."*

---

### F5 — `minor` — two of the four mutant loops have no "Verus produced no result" arm; the other two do

**`harness/check.py:2594-2605`** (5c's `assert(false)` reachability probe) and
**`check.py:3520-3542`** (5c-twin's per-conjunct vacuity probe). The siblings
that *do* have the arm are **`check.py:2645-2647`** and **`check.py:2972-2975`**,
20 and 30 lines away respectively.

```python
# 5c probe, :2594
if pv is not None and pe == 0:  rep.fail(... "assert(false) VERIFIES")
else:                           print("... is unprovable ... the call site's context is satisfiable")

# 5c-twin vacuity, :3520
if dv is not None and de == 0:  rep.fail(... "still verifies with the conjunct DELETED")
else:                           needed += 1; print("... the checked implementation genuinely needs it")
```
`_verus` returns `(None, None)` whenever Verus emits no `N verified, M errors`
line at all. Both `else` arms then report a **successful negative result from a
run that produced none**, and 5c-twin additionally increments the
`vacuity_probe.load_bearing` counter that goes into the gate JSON.

**Reproduction** (`.temp/p53/repro_none_arms.py`, real `_verus`, verbatim
branch chains):
```
_verus on the mangled mutant -> verified=None errors=None
--- check.py:2594-2605, verbatim ---
    verus.rs: assert(false) after `kernel(...)` is unprovable (None verified, None errors) -- the call site's context is satisfiable
--- check.py:3520-3542, verbatim ---
    verus.rs: `slb_twin_get_unchecked` fails when the conjunct `i < v@.len()` alone is deleted from `get_unchecked`'s `requires` (None verified, None errors) -- the checked implementation genuinely needs it
    load_bearing counter -> 1
--- the sibling loops that DO have the arm ---
    FAIL [clause-mut] ...: Verus produced no result for the mutant
    FAIL [req-mut]    ...: Verus produced no result for the deletion mutant
```

**Accident test: PASSES, weakly.** No *source-shaped* accident is available:
I checked the insertion at `_insert_false_probe` and `vparse.delete_conjunct`
(whose own docstring names this exact symptom — *"a parse error, which the gate
reports as 'Verus produced no result for the mutant' — blaming Verus for a
splitter bug"*) and both are robust on the shipped shapes. What is available is
any environmental no-verdict — the `verus_run.py` failure mode `CLAUDE.md`
DON'T #5 and `TOOLCHAIN.md` both warn about. That is honest-mistake territory,
and it is why the other two loops have the arm.

**Blast radius: latent.** All 17 `assert(false)` probe rows in the committed
records carry real numbers (`(6,1)`, `(8,1)`, `(17,1)` …), and no
`vacuity_probe.per_conjunct` row anywhere has a null `verified`. The only null
`verified` values in any gate JSON are F2's 51.

```diff
--- a/harness/check.py
+++ b/harness/check.py
@@ (5c, :2594)
             if pv is not None and pe == 0:
                 rep.fail("clause-mut", ... )
+            elif pv is None:
+                rep.fail("clause-mut",
+                         f"{src}: Verus produced no result for the "
+                         f"`assert(false)` reachability probe, so the call "
+                         f"site's context was never tested for satisfiability. "
+                         f"The clause-mutant loop below has this arm; this one "
+                         f"did not, and printed 'the call site's context is "
+                         f"satisfiable' from a run that produced "
+                         f"nothing.\n      {(po or '')[-300:]}")
             else:
                 print(...)
@@ (5c-twin, :3520)
                         if dv is not None and de == 0:
                             rep.fail("twin", ... )
+                        elif dv is None:
+                            rep.fail("twin",
+                                     f"{src}:{twin.line} Verus produced no "
+                                     f"result for the mutant that deletes "
+                                     f"`{frag}` from `{twin.name}`'s "
+                                     f"`requires`, so that conjunct was not "
+                                     f"tested -- and this arm used to count it "
+                                     f"as load-bearing. `delete_conjunct`'s own "
+                                     f"docstring names this symptom; the 5c and "
+                                     f"5c-req deletion loops both report "
+                                     f"it.\n      {(do or '')[-300:]}")
                         else:
                             needed += 1
```

---

### F6 — `minor` — `forbidden_hits` is the one decidable half of the idiom declaration, and a hit produces a plain print inside a block headed "REPORTING ONLY"

**`harness/check.py:939-942`** (the hit is computed), **`981-983`** (printed with
no `!!`), **`1025-1030`** (the block's own `ok` line says *"REPORTING ONLY. It
cannot fail the gate and does not enter the verdict"*).

`idiom_audit`'s docstring (`check.py:852-860`) says `forbidden`'s scope "is
universal by the key's own meaning … decidable with no English involved — **and
it has teeth**". It has none: a hit prints one line among dozens of audit
lines, does not reach `rep.loud`, and the run is `PASS`.

**Accident test: PASSES, with precedent.** `.memory/01-ladder.md` finding 14:
p05's `spec.md` forbade `chunks_exact` **by name** and two consecutive tasks
measured it anyway and published the result as p05's number. That is the
accident, and it has already happened twice.

**Blast radius: 0 live.** 132 forbidden spellings across the 16 patterns,
`forbidden_hits = 0` in every record. The fix therefore fires nowhere today.

```diff
--- a/harness/check.py
+++ b/harness/check.py
@@ def check_idiom(rep, pdir, contract):
         for ln in idiom_audit_lines(au):
             print(ln)
+    if au["spellings"] and au["forbidden_hits"]:
+        # `required` is not decidable -- an entry's rung scope is its English.
+        # `forbidden` IS: no rung may spell it, in any language it declares.
+        # A shout, not a failure, because the audit is presence-only and the
+        # threat model is honest mistake -- but not a plain print either:
+        # p05's spec.md forbade `chunks_exact` BY NAME and two consecutive
+        # tasks measured it and published the number
+        # (`.memory/01-ladder.md` finding 14). Shipped tree: 0 of 132.
+        rep.shout("idiom",
+                  f"{au['forbidden_hits']} FORBIDDEN spelling hit(s): "
+                  f"{[(h['rung'], h['spelling']) for h in au['hits']]}. A rung "
+                  f"spells something spec.md's `idiom.forbidden` names, which "
+                  f"is the one half of the declaration that is decidable "
+                  f"without reading English.")
     return au
```
If the manager judges this to be gate-hardening under rule 5, **decline it** —
it is the weakest of the six and the only one whose value rests on a
counterfactual.

---

### Minors found in the `ok`-string sweep (task item 4)

All 20 `rep.ok(...)` call sites were read against their guards. Two overclaim,
and **both can only fire on a run that is already FAIL**, which is why neither
is ranked higher: the two known instances were dangerous precisely because they
lied on a *green* run.

- **m1 — `check.py:1274`.** `all {sum(1 for k in results if k[3] == name)} cells
  agree` counts every row for that input, including cells that exited non-zero
  and were therefore excluded from `vals`. Fix: count `len([… if v[0] == 0])`.
- **m2 — `check.py:2289-2291`.** `… matches the pinned obligation count; N TCB
  items, **all contracts identical to spec.md**` is not gated on the per-item
  drift failures raised 50 lines above at `2240`. Fix: track a `drifted` flag
  per source and print the `ok` only when it is clear.

---

## 3. Clean negatives — stages checked and cleared, by name

Each of these was read line by line looking for the three sub-shapes, and each
is clear. **Do not re-run these.**

1. **`check_selftests` (0).** Six comparisons, all `got != want`, all failing.
   `asm.selftest()`'s 77 and non-zero returns are distinguished and both fail.
2. **`check_build` (1).** Fails per cell on `not ok`; the `--no-build` path
   additionally compares every binary's mtime against the newest source and
   fails on staleness.
3. **`check_checksums` (2).** Exit code, stdout-vs-`model.checksum`, and
   cross-cell agreement are all compared. `expected_stdout` is not compared
   here and does not need to be: `model.py` derives it *from* `checksum`
   (`p01/model.py:202`), so the two cannot disagree. `stderr` is recorded and
   only reported, which is right — a rung's stderr is not part of the contract.
4. **`check_no_collapse` (3a).** Four independent structural conditions, each
   appended to `problems`, and the `ok` is gated on `rows and not bad`.
5. **`check_marginal_ir` (3b).** Every derived quantity is compared: the rate
   against the absolute bound, the unit against the composition clamp, the
   slope against the floor, and `d(Ir)/d(work)` against the rate. The three
   cases where an assertion *cannot* run (one probe shape, hatched bound,
   loose margin) are each `rep.shout`, not silence. The `ok` is gated on
   `not any(f[0] == "collapse-ir")`.
6. **`check_identity` (3c).** Level compared to the pin per pair per opt;
   a missing side is a `note` (and the missing binary already failed stage 1);
   an unknown pinned level is a hard failure.
7. **`check_verus_contract` (5a) apart from F4 and m2.** Duplicate names,
   `in_verus`, `cfg_gated`, `external`, and both clause lists are all diffed
   against the pin; the pinned-file list is cross-checked against every `.rs`
   containing a `verus!` span; `_scan_unsafe_sites` covers `#[path]`-included
   files. `assume(`/`assume_specification`/`admit(` are counted on the
   comment-blanked text.
8. **`check_call_site` (5b).** Four conditions, and `resolved` is
   distinguished from "no verified body" — the TASK_008_REVIEW major-E fix is
   intact.
9. **`check_clause_deletion` (5c) apart from F5a.** The relocated control is
   verified before any mutant runs; `_mutation_targets` resolves every
   `clause_deletion_extra_items` name across all pinned files and
   `_unresolved` hard-fails a typo; the conjunct loop handles
   `me == 0`, `mv is None` and the healthy case; refused splits are shouted;
   `n == 0` is a hard failure.
10. **`check_requires_strength` (5c-req) apart from F2.** The bare-Z3 arm
    distinguishes `nocompile`, `tautology`, `perturbed` and the healthy case,
    and `unsynthesisable` is a hard failure rather than a skip. The deletion
    half handles `mv is None`. `n == 0` is a hard failure. The `ok` line's
    explicit "what is NOT claimed" paragraph is accurate.
11. **`check_trusted_twins` (5c-twin) apart from F5b.** Six structural rules
    per twin; `tv is None or te` fails; `tv <= base_v` fails ("the twins were
    not compiled at all"); a missing `twin_obligations` pin fails; the pin is
    compared. The justification hatch `rep.block`s (forcing
    PASS-WITH-BLOCKED-ROWS) as well as shouting, `n_twins == 0` with
    justifications is a hard failure, and the `ok` refuses to fire if anything
    was justified away. `_check_twin_cfg_hygiene` scans `#[path]`-included
    files too.
12. **`derive_contract` (5d0).** Every clause is translated and
    `compile(..., "eval")`-checked, and the derived list is compared to the
    declared one. **This is also what would catch a comment glued into the
    *kernel's* clause text** (F4's shape, for the one item that is translated).
13. **`check_proof_domain` (5d).** `requires` on every call of every input
    including adversarial; `ensures` on the sample; three separate vacuity
    failures (empty `reqs`, empty `enss`, zero total calls, zero sampled
    calls). Both `ok` lines state their `n`.
14. **`check_driver_identity` + `_check_region_executes` + `_check_region_runs`
    (6).** Region *set* compared to the pin (not merely ">= 2"); token
    sequence and statement count compared; exactly-one-call-inside-the-region;
    and the dynamic half has explicit failure arms for `not host or ir == 0`,
    `not kids or not callers_of_k` (the n=0 vacuity TASK_010_REVIEW found) and
    a wrong caller set. `_cg_name_matches` is anchored, not substring.
15. **`check_miri` (8).** TASK_052's fix is correct and complete: exit is
    compared to `want_exit` unconditionally and stdout unconditionally, the
    `ok` line names both, and the derived `why_required` list overrides the
    declared flag in one direction only.
16. **`_verus_verified_files`.** Refuses a harbour certificate on duplicate
    names, unresolvable names and no-verified-body, and the three are
    distinguished. A silent `continue` there costs the file its ghost-strip,
    which then fails stage 6 loudly.
17. **The model sandbox.** `_MODEL_FORBIDDEN` plus an audit hook; a `model.py`
    cannot reach a subprocess, so step 2 cannot be satisfied by running the
    thing under test.
18. **`--skip` / partial-run handling in `main()`.** Adversarial stems cannot be
    skipped, unknown stems are refused, and any of `--skip`/`--no-build`/
    `--no-callgrind`/`--no-verus-mutants`/`--cells measured` writes
    `.partial.json` and never over the full record.

Two attacks I ran that did **not** land and are worth naming so nobody repeats
them:

- **`nonlinear_arith` is not F2's sibling.** I suspected both non-bare tactics
  aborted. Measured on three patterns: `by (nonlinear_arith)` returns a real
  `(N+1, 1)` on every clause tried. Only `bit_vector` aborts.
- **`vparse.delete_conjunct`'s comment bug is closed.** Its docstring warns that
  a comment between `&&` conjuncts produces a parse error the gate blames on
  Verus. The scan runs on the blanked copy (`vparse.py:844`), so the comment is
  swallowed with the operator and the mutant parses. F5 needed a different
  route.

---

## 4. Ranked summary

| rank | id | file:line | accident? | live today | fix moves records? |
|---|---|---|---|---|---|
| major | F2 | `check.py:2799` | **yes** | **51/52 rows, all 16 patterns** | log + JSON keys only, no verdict |
| major | F3 | `check.py:4405` | yes (class) | 37/114 rows differ, 0 wrong | adds `stdout` to 114 rows, 0 failures |
| major | F1 | `check.py:1822` | **yes** | **7 patterns, up to 4→1** | `adversarial` key becomes a list |
| major | F4 | `check.py:2089` | **yes** | 0 (latent) | none — 0 clauses affected |
| minor | F5 | `check.py:2594`, `:3520` | yes, weakly | 0 (latent) | none |
| minor | F6 | `check.py:939`/`1025` | yes, with precedent | 0 of 132 | none |
| minor | m1 | `check.py:1274` | yes | red-run only | none |
| minor | m2 | `check.py:2289` | yes | red-run only | none |
| minor | — | `check.py:4387` | yes | `--no-build` only | none |

**Batching note.** F2, F4, F5, F6, m1, m2 and the `makedirs` line change no gate
record's *content*; F3 adds two keys per stage-7 row; F1 changes the shape of
one key. If the manager wants the ~30-minute re-run to buy the most, F1 and F3
are the two that need it, and they are independent of the other six.

---

## 5. Reproductions

All under `.temp/p53/`, each re-derivable by running the named script; nothing
outside `.temp/p53/` is written and `check.REPO` is rebound so the stage
functions' own scratch lands there too.

| script | finding | what it does |
|---|---|---|
| `probe_taut.py <pat> <item> <ci>` | F2 | builds the exact probe `_taut_probe` builds, runs real Verus per tactic, prints `_run_taut_battery`'s verdict |
| `repro_san.py <pid>` | F3 | calls the real `check_sanitizers` on p01 with a one-character off-by-one in `c/kernel.c` |
| `san_sweep.py <pid>` | F3 | runs stage 7's build for all 16 patterns and compares the dropped stdout to the model |
| `repro_adv.py <pat>` | F1 | calls the real `check_adversarial` over existing binaries and prints per-(opt,mode) behaviour beside the single recorded row |
| `repro_comment_clause.py <pid>` | F4 | three comment shapes plus a control, through the real `_check_trusted_unsafe` arithmetic and real Verus |
| `repro_none_arms.py <pid>` | F5 | forces `_verus` to return `(None, None)` and runs both branch chains verbatim |

`.temp/p53/NOTES.md` carries the working log.
