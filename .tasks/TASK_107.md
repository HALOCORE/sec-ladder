# TASK_107 — the batched harness work, and ONE sweep

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
`.memory/02-bench-rules.md`'s `include!` section, `.memory/03-measurement.md`'s
±7 sections **and its reproduction protocol**, and `RECAP.md` owed-item 23.

Scratch in **`.temp/t107/`**.

⚠⚠ **EVERY ITEM HERE EDITS `harness/check.py`, WHICH STALES EVERY GATE RECORD.
That is why they are batched. ONE sweep, LAST.** ⚠ **`TASK_096` edited `check.py`
between p08 and p09 and went 8 STALE. Finish every edit before the sweep starts.**

⚠⚠ **AND THE COST ASYMMETRY DECIDES THE DESIGN OF ITEM 5.** `harness/check.py` is
**not** measurement-hashed — an edit costs a gate sweep. **`harness/measure.py`
IS measurement-hashed** (`measure.py::measurement_sources` globs it), so editing
it costs **a full re-measure of every record**, which churns published timing
prose. **Prefer `check.py` wherever a check can live in either.**

---

## §A — `_path_includes` will not converge. Replace it with the compiler.

**Nine routes have now been found by three separate tasks**, each after the
previous table read as exhaustive: four `include!` spellings, transitive
`#[path]`-of-`#[path]`, `macro_rules!`-emitting-`#[path]` (already caught), and
`TASK_103`'s three — **`#[cfg_attr(all(), path = "h.rs")]`** (the standard
platform-selection idiom), a **raw-string `#[path = r"h.rs"]`**, and a bare
**nested inline `mod x { mod m; }`** (rustc resolves it to `x/m.rs`).

⚠ **The finding is the method, not the ninth route: `_path_includes` is a regex
approximation of rustc's module resolution.** The compiler will hand over the
exact set for one flag, on a compiler this project already invokes:

```
$ rustc --edition 2021 --emit=dep-info main.rs
main.d: main.rs h.rs x/y.rs          # on a main.rs containing BOTH R7a and R7c
```

**Replace the walk with `--emit=dep-info`, and feed all three Verus-side
detectors from the one list.** ⚠ **That asymmetry — one detector fed and not the
others — WAS `TASK_084_REVIEW` major 1 and took two tasks to close. Do not
re-open it.**

⚠ **Acceptance must run source → published number in ONE command with an arm
that FAILS.** `.temp/t99/b2_source_to_published.py` and
`.temp/t97/b3_source_to_published.py` are the working models. **Include all nine
routes as arms, and a `CONTROL-plain` arm that must be scanned.**
⚠ **Keep a fallback**: if `--emit=dep-info` fails for a file the gate must still
judge, **fail closed and say so** — silently falling back to the regex would
reproduce the hole under a new name.

## §B — `_check_opaque_includes` fails the gate on comments and strings

**5 of 5 shapes**: a line comment, a `//!` doc comment, a block comment, the
idiom inside a **string literal**, and a **commented-out** `include!` of a real
path all turn the gate **RED**.

⚠ **`_path_includes` reads raw text deliberately** — over-approximating a *file
set* is safe. **For a check that FAILS the gate, over-approximation is the unsafe
direction.** ✅ **Fix: run this check on `vparse.blank_noncode(txt)`.**

⚠ **The accident route is near**: `include!(concat!(env!("OUT_DIR"), "/gen.rs"))`
is now the canonical example sentence in `check.py`'s own docstring, in
`.memory/02-bench-rules.md` and in two reports — **the first author who quotes it
in a rung source's doc comment fails the gate.**
⚠ **And fix the DIAGNOSTIC too**: for the build-script idiom there is no literal
path, so *"Use a literal path"* asks for the one impossible thing. **Say what to
do instead.**
⚠ **Scope gap, decide and state**: the check never covers the roots, so an opaque
`include!` in `safe_tuned.rs` is not refused. **Pre-existing, since no stage
scans the safe rungs for `unsafe` tokens — say whether you extended it.**

## §C — pin `MIRIFLAGS`; Miri's alignment check is seed-dependent

**The same source is clean under `-Zmiri-seed=0` and `2` and reports UB under
`1` and `3`, and `check.py` passes no seed.** So **every *"Miri: N of N, no UB"*
line in this tree is a statement about one unpinned draw**, and a `miri.required`
row can pass or fail on the default.

**Two honest designs — pick one and defend it:** *(a)* **pin a seed** and record
it in the gate record, which is reproducible but tests one draw; *(b)* **sweep a
small fixed set** (e.g. 0–3) and require all to pass, which is stronger and
slower. ⚠ **Whichever you choose, RECORD WHAT RAN in the gate record** — the
current defect is not the seed, it is that nothing says which seed answered.

## §D — record the environment-block length in the gate record

**Decided at `TASK_103` and this is the implementation.** One integer beside
`marginal_ir_per_call`:

```python
env_bytes = len(open("/proc/self/environ", "rb").read())
```

⚠ **Read it from the MEASURED CHILD, not from the launching shell, and not from
`os.environ`** — `TASK_099`'s probe computed it from a Python dict and became
control entry 7. **Then: same recorded length ⇒ the marginal must match exactly
and a mismatch is a real change; different length ⇒ compare
`kernel_exclusive_ir` or re-run at the recorded length.**

⚠⚠ **This is NOT the forbidden pin.** Do **not** force an environment — that
makes the number reproducible-and-wrong. **Record which draw you took, so a
disagreement becomes diagnosable.**

## §E — `results/tables/` has no staleness detector, and item 23 predicted its own recurrence

It recurred: `results/tables/p09-bitset.md` cited a digest **two contract moves
stale**, and `p23` shipped with **no table at all** and nothing noticed.
⚠ **`harness/measure.py::check_stale` globs `results/*.json` and
`results/gate/p*.json` and NOTHING ELSE.**

⚠⚠ **DO NOT FIX THIS IN `measure.py` — it is measurement-hashed and would cost a
full re-measure for a bookkeeping check. Put it in `check.py` as a gate stage**,
where it costs the sweep you are already paying for.

**It must catch BOTH failure modes**, and the second is the one my own throwaway
script missed: **a table whose cited `contract_sha256` disagrees with the gate
record**, *and* **a pattern with no table at all.** ⚠ **Iterate over PATTERNS,
not over tables** — globbing tables makes an absent one invisible, which is how
`.temp/mgr99/tables_stale.py` reported *"24 checked, 0 STALE"* on a 25-pattern
tree. **That script is the prototype; it is not the answer.**

## §F — two small ones, if §A–§E are done

- **`harness/limbs.py::TWIN_BANNED` is missing `"external_body"`** —
  `\bexternal\b` does not match it, so the re-derivation tool under-reports
  `5ct-cfg`. Reported at `TASK_098`, never fixed. ✅ `limbs.py` is **not**
  measurement-hashed.
- **`synthesis/outward_ir.json` carries no staleness pin** and
  `results/synthesis.md` says so in its own text. It was found **three patterns
  stale** (22 entries against 25). ⚠ **`synthesis/licence.json` is the pattern to
  copy: carry the gate `source_sha256` you were taken against and print `STALE`
  on a mismatch.** **Same rule now applies to `patterns/*/controls/*.json`** —
  `p23` ships one.

## §G — the sweep

Full **26-pattern** (or 25, if `p42` has not landed — **say which**)
`harness/check.py`, then `synthesis/licence.py --emit synthesis/licence.json`
**BEFORE** `synthesis/synthesize.py` — ⚠ **mandatory order or every row publishes
`LICENCE STALE`** — then `synthesis/outward_ir.py`, then
`harness/measure.py --check-stale`.

**Expect all `PASS` except p01's `PASS-WITH-BLOCKED-ROWS`, 0 failures.**
**If anything turns red, STOP AND REPORT.**

⚠ **`results/synthesis.md` will move and that is expected** — §D adds a field.
**Diff it and state exactly which lines moved.**

---

## Constraints

- **`.temp/t107/` only. No `/tmp`.** **Notes in `.temp/t107/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- **`.memory/` and `RECAP.md` are manager-only.**
- ⚠⚠ **Do not touch `harness/build.py`, `harness/asm.py` or `harness/measure.py`**
  — all three are measurement-hashed. ⚠ **Do not touch `check.py::_scan_unsafe_sites`;
  that decision is landed.** ⚠ **Do not touch any `patterns/*/` file** — every
  rung `.rs`, `c/*`, `model.py` and `inputs/gen.py` is measurement-hashed.
- ⚠ **Every acceptance test needs an arm that FAILS.** The list of **seven**
  controls in this project that could not have failed is at the end of
  `.memory/03-measurement.md`. **Do not become the eighth.**
- Verus via `./verus_run.py` only. Do not bump the pin.
- ⚠ **Cite `check.py` by FUNCTION NAME, never a line number.**
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_107_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is `MANAGER-FILLS-AT-LAUNCH`.** The calls I
am least sure of:

1. ⚠⚠ **That `--emit=dep-info` is the right instrument at all.** It is rustc's
   answer for *rustc's* module graph — **Verus is a different front end**, and if
   `verus_run.py` accepts a file rustc's dep-info does not list, §A closes the
   hole for the wrong compiler. **Check that before rewriting the walk.**
2. **That §D's one integer is enough.** `TASK_103` settled launcher-vs-environment
   but explicitly **did not separate environment LENGTH from CONTENT.** ⚠ **If
   content matters too, a length is a lossy pin and will read as reproducible
   when it is not.**
3. **That §E belongs in `check.py`.** It is a *publishing* check, not a
   *correctness* check, and the gate is already 18 stages. ⚠ **If you think it
   belongs in a standalone script that CI-less humans run on request, say so** —
   `CLAUDE.md` forbids wiring up automation but not shipping the script.

Carry that count forward, incremented by what you find.
