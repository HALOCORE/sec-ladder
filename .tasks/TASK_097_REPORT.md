# TASK_097 — report (research engineer)

## THE §A ANSWER, FIRST

> **No. `_TWIN_BANNED` is NOT the blocker, and repairing it does not ship `p35`.**
> **The catalogue closes at 24 built patterns plus an optional `p23`.**

⚠⚠ **And the reason is not the one the task file, `.memory/02-bench-rules.md`
and the `p35` catalogue row all give.** All three say the twin rule *"is what
produces"* the illegal spelling and that fixing it *"might ship `p35` the comply
way with no soundness loosening at all"*. **Measured, on the gate's own
functions: it cannot.** `check.py::_scan_unsafe_sites` — the rule the manager
has decided **stays as it is** — refuses **every** route that puts an `unsafe`
token in a twin, and it refuses them *before* `_TWIN_BANNED` is consulted:

| route for a `p35` twin | `_scan_unsafe_sites` | `_TWIN_BANNED` |
|---|---|---|
| twin body holds `unsafe { v.i }` | **FAIL** `verus.rs:13` | FAIL |
| twin calls a **verified** helper holding it | **FAIL** `verus.rs:12` | clean |
| helper is itself `#[cfg(slb_twin)]` | **FAIL** `verus.rs:13` | clean |
| `macro_rules!` helper (TASK_009_REVIEW x1's shape) | **FAIL** `verus.rs:2` | clean |
| twin body is `v.i`, no `unsafe` token | clean | clean — **and rustc refuses it, `E0133`** |

**The mechanism, and it is structural, not a bug in one predicate.**
`check.py::_is_trusted` returns `False` unless
`item.external == "verifier::external_body"`. A twin may not be `external_body`
— **three separate rules say so**: `_TWIN_BANNED` lists `external_body`,
`_TWIN_BANNED` lists `external`, and `check_trusted_twins` has an explicit
`if twin.external:` limb. **So a twin is NEVER `_is_trusted`, so no `unsafe`
token can ever sit inside a trusted body in a twin configuration, so
`_scan_unsafe_sites` hard-fails.** `_TWIN_BANNED` is *downstream* of a rule that
already refuses the same thing.

**`_TWIN_BANNED` would have to be repaired *and* `_scan_unsafe_sites` narrowed,
and the second is the landed refusal.** Executed, not read
(`.temp/t97/a2_gate_limbs.py`): with `unsafe` removed from `_TWIN_BANNED` and
nothing else changed, stage 5c-twin goes **fully green** — and
`FAIL [tcb-unsafe] verus.rs:15` is **unchanged**.

✅ **What is worth keeping from the probe, because it is a genuine positive
result and it is the thing a future revisit turns on:** a repaired twin for
`p35` would have **real teeth**, not decoration. Measured
(`.temp/t97/a1_twin_shapes.py`): the twin `unsafe { v.i }` under `requires
v is i` gives **`2 verified, 0 errors`**, and with that single conjunct deleted
it gives **`1 verified, 1 errors` — *"requirement not met: to access this
field, the union must be in the correct variant"***. The per-conjunct deletion
oracle fires. **So the ban is over-broad *in principle* — Verus really does
check this `unsafe`, which is exactly what the ban assumes it does not — and
that is still not enough to ship the row.**

---

## Did

**§A — the `_TWIN_BANNED` probe (the deliverable).** Four executed probes, no
edits to `harness/` for this half:

- `.temp/t97/a1_twin_shapes.py` — five candidate twin bodies × two cfgs through
  `./verus_run.py`, recording summary **and** return code **and** rustc error
  codes.
- `.temp/t97/a2_gate_limbs.py` — drives `check.py::_scan_unsafe_sites` and
  `check.py::check_trusted_twins` **themselves** against a synthetic pdir under
  `.temp/t97/fakep/`, including a run with `_TWIN_BANNED` monkeypatched to drop
  `unsafe`, to isolate which rule refuses what. Nothing planted into
  `patterns/`.
- `.temp/t97/a3_twin_attacks.py` — if the ban dropped `unsafe`, are the other
  five banned words enough? Six twin bodies through Verus.
- `.temp/t97/a4_helper_route.py` — the four "put the `unsafe` somewhere else"
  routes, refuted **statically** (`_scan_unsafe_sites` is pure text analysis, no
  subprocess).

**§B — the `_verus` return-code hole. Fixed, in four edits.**

- `harness/check.py::_verus` — flags `rc != 0` **only when the summary parsed
  AND `errors == 0`**, records the run in a new module-level
  `_VERUS_RC_ANOMALIES`, and returns `(None, None, out + reason)`. The reason is
  **appended**, not prepended, because every caller prints `out[-300:]`.
- `harness/check.py::check_verus_contract` — the inline byte-for-byte duplicate
  of `_verus` (TASK_096_REVIEW MAJOR 2's *"primary certificate site"*) now
  **calls `_verus`**. The duplicate is deleted; one edit fixes and dedups.
- `harness/check.py::check_verus_exit_codes` — **new stage 5e**, called last in
  `main()`, hard-fails on any recorded anomaly and writes
  `verus_exit_anomalies` into the gate record.
- `harness/limbs.py::verus` — the third copy of the same body, same predicate.

**Acceptance test:** `.temp/t97/b3_source_to_published.py`, source → published
number in ONE command, two arms.

**§C — the sweep**, in the mandatory order (`.temp/t97/c1_sweep.sh`).

**§D — four doc repairs**, all four of the items named:
`patterns/p09-bitset/NOTES.md`, `patterns/p09-bitset/spec.md` (⚠ **inside the
hashed contract — `contract_sha256` moves; disclosed below**),
`patterns/p12-strcat-fixed/NOTES.md`, `patterns/p06-rotate/NOTES.md`.

---

## Evidence

### §A.1 — what the twin is FOR, restated before proposing anything

A trusted item is `#[verifier::external_body]`: **Verus never looks at its
body.** The body performs an unchecked operation, and the only thing between
that operation and UB is the item's `requires`. **Nothing else in the project
can judge whether that `requires` is strong enough:**

- deleting a trusted `requires` **cannot fail Verus** — measured at TASK_008, it
  only removes obligations from callers — so no verify/fail oracle sees it;
- stage 5a checks only that every parameter is *mentioned*;
- stage 5c-req checks only **triviality**, and `i <= v@.len()` is not a
  tautology and is still one byte past the end;
- ⚠ **Miri never opens `verus.rs`.** R5 is not a Miri target, so the runtime
  backstop that covers R4 is not a *partial* backstop here — it is **none**.
  That is the exact ground T009 / TASK_010_REVIEW adjudicated the twin *"worth
  keeping"* on, against the manager's own design, with "delete it" offered as a
  welcome answer.

The twin closes precisely that gap by being **verified code Verus does look
at**: the same signature, a *checked* body, under `#[cfg(slb_twin)]` so it costs
zero instructions structurally. If the trusted `requires` is too weak to license
a checked implementation of the same contract, Verus refuses the twin. And the
**per-conjunct deletion probe** forces the checked body to actually *need* each
conjunct, which is what stops an empty-bodied twin from certifying nothing.

**So: the twin is the sole oracle for the STRENGTH of a trusted precondition,
and it works by being code Verus checks.** Any repair has to preserve that.

### §A.2 — why `_TWIN_BANNED` forbids `unsafe`, and the manager's guess

Landed at **`f1229af`** (TASK_009, *"a verified twin judges the strength of a
trusted precondition"* — the commit that created the twin). It has never been
touched since. The recorded reason is the comment directly above it:

```python
# Anything that would let a twin pass without Verus actually checking the
# operation. `unsafe` and `external_body` would make the twin a second copy of
# the axiom; `assume`/`admit` would let the author write the precondition they
# wish they had; calling the trusted item itself is the degenerate cheat.
_TWIN_BANNED = ("unsafe", "assume", "admit", "assume_specification",
                "external_body", "external")
```

⚠ **The manager's guess in §A.2 is CORRECT and is the recorded reason**: *"the
ban exists so a twin cannot re-introduce the very operation it is supposed to be
an independent check on."* That is the comment's *"a second copy of the axiom"*,
word for word in intent.

**And the guess's consequence — *"then a twin for `p35` is not obviously safe
just because the pattern needs one"* — is where it gets interesting.** For
`get_unchecked` or a raw-pointer deref, the assumption behind the ban is true:
Verus imposes no obligation, so an `unsafe` twin re-states the axiom. **For a
union read it is FALSE.** Verus makes the correct-variant obligation **first
class in its type system** — no vstd spec is involved — so the twin is not a
second copy of the axiom, it is the operation being *checked*. The `unsafe`
keyword there is **rustc's demand, not an escape from Verus's checking**.

### §A.3 — is there a legal `p35` under a repaired twin rule? Runs.

`.temp/t97/a1_twin_shapes.py` — `./verus_run.py`, single-file, both cfgs:

```
case                 cfg              summary                 rc  rustc_errors
no_twin              shipped          1 verified, 0 errors     0  []
no_twin              --cfg slb_twin   1 verified, 0 errors     0  []
twin_unsafe          shipped          1 verified, 0 errors     0  []
twin_unsafe          --cfg slb_twin   2 verified, 0 errors     0  []
twin_unsafe_noreq    shipped          1 verified, 0 errors     0  []
twin_unsafe_noreq    --cfg slb_twin   1 verified, 1 errors     1  []
twin_safe_read       shipped          1 verified, 0 errors     0  []
twin_safe_read       --cfg slb_twin   2 verified, 0 errors     1  ['E0133']
twin_empty           shipped          1 verified, 0 errors     0  []
twin_empty           --cfg slb_twin   1 verified, 1 errors     1  []
```

- `twin_unsafe` is the twin `p35` needs. It **verifies**.
- `twin_unsafe_noreq` deletes the twin's `requires v is i`:
  `error: requirement not met: to access this field, the union must be in the
  correct variant`. **The conjunct is load-bearing — the deletion oracle has
  teeth.**
- `twin_safe_read` is **the only body `_TWIN_BANNED` permits**, and it is
  `2 verified, 0 errors` with `error[E0133]: access to union field is unsafe`
  and **exit 1**. That is MAJOR 3, reproduced end to end.
- `twin_empty` (`0u64`) fails on the `ensures` — so a vacuous twin is already
  refused here.

`.temp/t97/a2_gate_limbs.py` — the gate's own functions on a synthetic pdir
(`SLB-TRUSTED-ARGUMENT` failures in every arm are an artefact of the synthetic
dir having no `NOTES.md`; ignore them):

```
===== U_unsafe_twin =============================================
  -- tcb-unsafe/_scan_unsafe_sites: failures=1
     FAIL[tcb-unsafe] verus.rs:15 an `unsafe` token sits outside every trusted item's body...
  -- 5c-twin/check_trusted_twins: failures=2
     FAIL[twin] verus.rs:11 `slb_twin_read_i` is not a usable twin for `read_i`:
                its body contains `unsafe`, which would let it inherit the very
                axiom it exists to check

===== S_safe_twin ===============================================
  -- tcb-unsafe/_scan_unsafe_sites: failures=0
    verus.rs: `slb_twin_read_i` verifies against `read_i`'s own contract (requires=['v is i']) in 1 lines of checked code
    verus.rs: 2 verified, 0 errors with `--cfg slb_twin` -- matches the pinned verus.twin_obligations
    verus.rs: `slb_twin_read_i` fails when the conjunct `v is i` alone is deleted ... genuinely needs it
  -- 5c-twin/check_trusted_twins: failures=1   (the NOTES.md artefact only)

===== J_justified ===============================================
    !!   [twin] BLOCKED verus.rs `read_i` (strength unchecked)
     FAIL[twin] every trusted item in this pattern (['verus.rs:read_i']) is excused ... off switch
===== J2_justified ==============================================
     BLOCK verus.rs `read_i` (strength unchecked)          (no n_twins fail)

===== U_unsafe_twin  [_TWIN_BANNED without 'unsafe'] ============
  -- tcb-unsafe/_scan_unsafe_sites: failures=1     <-- UNCHANGED
     FAIL[tcb-unsafe] verus.rs:15 an `unsafe` token sits outside every trusted item's body...
    verus.rs: 2 verified, 0 errors with `--cfg slb_twin` -- matches the pinned verus.twin_obligations
    verus.rs: `slb_twin_read_i` fails when the conjunct `v is i` alone is deleted ... genuinely needs it
  -- 5c-twin/check_trusted_twins: failures=1   (the NOTES.md artefact only)
```

**CN-5's limbs B and C reproduce exactly** — `J_justified` hard-fails on
`n_twins == 0`, `J2_justified` only blocks. And the last block is the whole
answer: **repairing `_TWIN_BANNED` turns 5c-twin green and moves `tcb-unsafe`
not at all.**

`.temp/t97/a4_helper_route.py` — the four workarounds, static:

```
route                   tcb-unsafe fails  first message
twin_holds_unsafe                      1  verus.rs:13 an `unsafe` token sits outside...
verified_helper                        1  verus.rs:12 an `unsafe` token sits outside...
cfg_gated_helper                       1  verus.rs:13 an `unsafe` token sits outside...
macro_helper                           1  verus.rs:2  an `unsafe` token sits outside...
safe_spelling_E0133                    0  -- clean --
```

**Every route that lets the twin compute the value is refused by
`_scan_unsafe_sites`; the one route it admits is the one rustc refuses.**

### §A.4 — could the ban be dropped safely, if the other rule were narrowed?

Moot, and I say so rather than pretending it is not: `_scan_unsafe_sites` is
landed. But the decision block's **reason 1** is a claim about exactly this
shape, so I ran it (`.temp/t97/a3_twin_attacks.py`, twin bodies containing
`unsafe` and none of the other five banned words, `--cfg slb_twin`):

```
honest_union_read    2 verified, 0 errors     0
transmute            NO SUMMARY               1   `core::intrinsics::transmute` is not supported
unreachable_unchkd   1 verified, 1 errors     1   precondition not satisfied
wrong_field          1 verified, 1 errors     1   union must be in the correct variant
ptr_read             NO SUMMARY               1   does not yet support dereferencing a pointer
assume_control       2 verified, 0 errors     0   <- `proof { assume(false); } 0u64`
```

Two things worth keeping. **(1)** The `assume` control verifies vacuously at
`2 verified, 0 errors`, which is the measured demonstration that the *other
five* banned words are load-bearing and should not be touched. **(2)** None of
the five `unsafe` bodies verified without an obligation — Verus either
discharged it or refused the construct. ⚠ **That is a FIVE-case enumeration, and
the 26+8-case enumeration it echoes was defeated by one construct at
TASK_096_REVIEW BLOCKER 1. Do not read it as a soundness argument.** I did not
attempt to break a hypothetically-narrowed `_TWIN_BANNED`, because the row does
not turn on it.

### §A.5 — what a `p35` twin would have to contain, and the two options I am NOT recommending

**It would have to contain the token `unsafe`.** There is no safe union read in
Rust — `error[E0133]`, measured above — no vstd spec (`union` is absent from
vstd entirely), and no macro, helper or cfg trick moves the token anywhere the
gate accepts. **That is not acceptable under the landed decision**, for the
decision block's own reason 1: a textual span rule cannot distinguish `unsafe`
Verus discharges from `unsafe` Verus ignores, and `_scan_unsafe_sites` is the
rule that would have to make that distinction.

Two routes exist that do **not** need the ban repaired. **I am reporting them,
not recommending them**, and the task file's *"do not invent a fix to keep a row
alive"* is the right instruction:

1. **Two trusted items, one justified away** (CN-5 limb C, reproduced above).
   Legal, and the verdict is `PASS-WITH-BLOCKED-ROWS` — but the blocked row **is
   the pattern**, so `p35` would publish a type-confusion result whose central
   trusted precondition nothing checked, plus a second trusted item invented
   purely to keep the hatch from being an off switch. That is worse than not
   shipping the row.
2. **A `p35` with no `union` in `verus.rs` at all** — payload as `[u8; 8]`,
   decoded with `u64::from_le_bytes` / `f64::from_bits`, so R5 is entirely safe
   and has **zero trusted items**. The gate accepts that shape (it shouts *"no
   trusted item ... NOTHING in this stage checked this file"* and sets the
   record). ⚠ **But it would be the first `verus.rs` in the tree with zero
   trusted items — measured, all 24 have ≥1; only p01's control cell
   `safe_naive_verus.rs` has none** — and it deletes the pointer arm (the
   SIGSEGV), which is half of what makes `p35`'s harm interesting. **It is a
   different pattern wearing `p35`'s name.**

### §B.1 — the call-site partition, DERIVED

`.temp/t97/b1_verus_sites.py` finds the sites with `ast`, so a docstring mention
and `region_in_verus` cannot be miscounted:

```
AST `_verus(...)` CALL sites: 11
   4195  _verify_function             nv, ne, out = _verus(path, *extra)
   4380  check_clause_deletion        base_v, base_e, base_out = _verus(mpath)
   4398  check_clause_deletion        pv, pe, po = _verus(mpath)
   4446  check_clause_deletion        mv, me, mo = _verus(mpath)
   4619  _run_taut_battery            rv, re_, ro = _verus(mpath)
   4733  check_requires_strength      base_v, base_e, base_out = _verus(mpath)
   4827  check_requires_strength      mv, me, mo = _verus(mpath)
   5298  check_trusted_twins          base_v, base_e, _ = _verus(path)
   5299  check_trusted_twins          tv, te, to = _verus(path, "--cfg", TWIN_CFG)
   5407  check_trusted_twins          dv, de, do = _verus(mpath, "--cfg", TWIN_CFG)
   7481  _probe_selftest              base_v, base_e, base_out = _verus(base)

textual `grep -n '_verus('` hits: 14
non-calls: [4126, 4909, 5820]
```

Classified by reading each **consumer**, not by name:

| site | function | kind | why |
|---|---|---|---|
| 4195 | `_verify_function` | **success** | both callers `rep.fail` on `nv is None` |
| 4380 | `check_clause_deletion` | **success** | `if base_v is None or base_e: rep.fail` |
| 4398 | `check_clause_deletion` | mutant | `assert(false)` probe — healthy answer is `pe != 0` |
| 4446 | `check_clause_deletion` | mutant | `if mv is not None and me == 0: rep.fail` |
| 4619 | `_run_taut_battery` | probe | `pe == 0` ⇒ `"tautology"` ⇒ caller fails |
| 4733 | `check_requires_strength` | **success** | control |
| 4827 | `check_requires_strength` | mutant | `me == 0` ⇒ `rep.fail` |
| 5298 | `check_trusted_twins` | **success** | base, shipped cfg |
| 5299 | `check_trusted_twins` | **success** | `if tv is None or te: rep.fail` |
| 5407 | `check_trusted_twins` | mutant | `dv is not None and de == 0` ⇒ `rep.fail` |
| 7481 | `_probe_selftest` | **success** | `if base_v is None or base_e: bad += 1` |

**6 success-expecting, 5 mutants/probes. ✅ TASK_096_REVIEW's 11 / 6 / 5 is
right; TASK_096's 12 / 4 was wrong.** Derived, not taken on trust — the task
file asked me not to trust either number.

**Why a bare returncode check would be worse:** at all five mutant sites
`errors == 0` is *already* the failure condition, so a bare `rc != 0` check
turns the mutant battery green for the wrong reason. The narrow predicate
(**summary parsed AND `errors == 0` AND `rc != 0`**) is unreachable at a mutant
site by construction.

### §B.2 — the two other rc-blind readers: decided, and why

- **`check.py::check_verus_contract` — FIXED.** It was a byte-for-byte duplicate
  of `_verus`'s body (same command, same regex, same `cwd=REPO`, same
  `RUN_TIMEOUT`) and it is the run that fills every gate record's `verified`,
  `errors` and `tcb_items`. Replacing the duplicate with a call to `_verus` both
  fixes it and deletes the duplicate, so the two cannot drift again. It *is*
  backstopped by `build.py::build_verus --compile`, but that backstop is stage
  `[build]`, which `--no-build` skips — and a diagnostic pointing at the wrong
  stage is how this stayed invisible for 96 tasks. **Cost: zero.** `check.py` is
  in the gate record's `source_sha256` and the sweep rewrites it anyway; it is
  **not** in `measure.py::measurement_sources`, which is `build.py`, `asm.py`,
  `measure.py`, `verus_run.py`, `common/`, and the pattern's own sources.
- **`harness/limbs.py::verus` — FIXED**, same predicate. Its own header says the
  file exists to **re-derive** `check.py`'s comparison and that *"if `check.py`'s
  comparison moves and this does not, every sentence citing it silently becomes
  wrong"* — six patterns' `NOTES.md` sentences rest on it. Editing it is **free
  at the margin** for the same reason. Not a gate stage, so it gets no anomaly
  stage; it suppresses the summary and says why.

### §B.3 — the acceptance test: source → published number, ONE command, an arm that FAILS

`.temp/t97/b3_source_to_published.py e0133` plants into `p03` a union + an
`external_body` accessor + a `#[cfg(slb_twin)]` twin whose body is `v.i`, then
runs the full three-command chain and diffs `results/synthesis.md`.

⚠ **The plant carries NO `ensures`**, deliberately: the natural one is
`r == get_union_field::<Slot, u64>(v, "i")` and `vparse` splits clauses on
top-level commas, so the turbofish becomes two pinned fragments and
`check_clause_deletion`'s mutants stop parsing (TASK_096_REVIEW MINOR 7, which
is why `.temp/t96/a3_gate_comply.log` carries two unrelated `[clause-mut]`
failures). `_is_trusted` is `external_body AND (ensures OR unsafe-in-body)` and
the body has `unsafe`, so the item is still trusted and the whole twin regime
still governs it. Verified standalone first
(`.temp/t97/b2/probe_noensures.rs`): shipped `rc=0`; `--cfg slb_twin`
`2 verified, 0 errors` `rc=1` `E0133`; twin `requires` deleted →
`1 verified, 1 errors`.

```
+ harness/check.py p03
    rc=1  check.py: FAIL
+ /usr/bin/python3 synthesis/licence.py --emit synthesis/licence.json
    rc=0  wrote synthesis/licence.json: 24 patterns, 96 pair verdicts (LICENSED, NOT-LIC, UNDEC)
+ /usr/bin/python3 synthesis/synthesize.py
    rc=0  wrote results/synthesis.md  (60600 bytes, 504 lines)

[verus-exit] lines in the gate transcript: 3
    == 5e. every Verus run's EXIT CODE, not just its summary =============
    FAIL [verus-exit] patterns/p03-bounded-stack/verus.rs ['--cfg', 'slb_twin']:
         verus_run.py exited 1 while reporting `13 verified, 0 errors`. ...

results/synthesis.md MOVED: 9 line(s) differ (+0 lines)
  line 421
    -| p03-bounded-stack | 9 | 0 | 5 | 10 | 0 | exact | PASS |
    +| p03-bounded-stack | 9 | 0 | 6 | 11 | 0 | exact | FAIL |
  line 443
    -| **total** | **316** | | **98** | **204** | **0** | | |
    +| **total** | **316** | | **99** | **205** | **0** | | |
  line 445
    -**Trusted base, all 24 rows: 98 items (204 lines) and 0 axioms.**
    +**Trusted base, all 24 rows: 99 items (205 lines) and 0 axioms.**
  ... (6 more: the calibration paragraph, the two ±-floor bucket rows, p03's
       two derived-correction cells)
git status --porcelain, NEW entries vs the pre-run baseline:
  (none)

b3[e0133] exit 0   log -> .temp/t97/b3_e0133.log
```

⚠⚠ **`13 verified, 0 errors` is the SAME NUMBER `.temp/t96/a3_gate_comply.log`
line 425 printed as GREEN on TASK_096's real gate run** — *"verus.rs: 13
verified, 0 errors with `--cfg slb_twin` -- matches the pinned
verus.twin_obligations"*, about source rustc refuses. Same plant, same number,
opposite verdict. **That is the before/after, and the "before" is a committed
log rather than a claim.**

---
### §C — the sweep

`.temp/t97/c1_sweep.sh`, mandatory order, nothing under `harness/` or
`patterns/` touched after it started.

```
p01   rc=0    337s  check.py: PASS-WITH-BLOCKED-ROWS
p02   rc=0    109s  check.py: PASS      p14   rc=0    120s  check.py: PASS
p03   rc=0     92s  check.py: PASS      p16   rc=0     87s  check.py: PASS
p04   rc=0     94s  check.py: PASS      p17   rc=0    100s  check.py: PASS
p05   rc=0     83s  check.py: PASS      p18   rc=0     76s  check.py: PASS
p06   rc=0    124s  check.py: PASS      p19   rc=0     89s  check.py: PASS
p07   rc=0     86s  check.py: PASS      p22   rc=0    300s  check.py: PASS
p08   rc=0    129s  check.py: PASS      p27   rc=0    205s  check.py: PASS
p09   rc=0     94s  check.py: PASS      p36   rc=0     93s  check.py: PASS
p10   rc=0     80s  check.py: PASS      p38   rc=0     95s  check.py: PASS
p11   rc=0     84s  check.py: PASS      p46   rc=0    104s  check.py: PASS
p12   rc=0    102s  check.py: PASS      p47   rc=0     79s  check.py: PASS
p13   rc=0    106s  check.py: PASS
=== licence.py --emit ===
wrote synthesis/licence.json: 24 patterns, 96 pair verdicts (LICENSED, NOT-LIC, UNDEC)
=== synthesize.py ===
wrote results/synthesis.md  (60660 bytes, 504 lines)
=== measure.py --check-stale ===
48 record(s) examined, 0 STALE
```

**23 `PASS` + 1 `PASS-WITH-BLOCKED-ROWS`, 0 failures, 48 records 0 STALE —
exactly the expected result.** `results/synthesis.md` is **byte-identical to
HEAD**; `synthesis/licence.json` moves in **52 leaves and every one is a
`gate_source_sha256`** entry for the six files I edited — no verdict, no number.

**The 24 gate records, leaf by leaf** (`.temp/t97/c2_record_diff.py`, walking
`.temp/t97/gate.HEAD/` — copied before the sweep — against `results/gate/`):

```
leaf values: HEAD 24179, sweep 24179     MOVED: 181
top-level key                 moved
adversarial                      87   list ORDER + garbage stdout on adversarial-allpop.bin
source_sha256                    52   check.py x24, limbs.py x24, p06/p09/p12 NOTES, p09 spec
sanitizer                        40   ASan/UBSan diagnostic text (addresses, frame offsets)
contract_sha256                   1   p09 -- disclosed, §D
idiom                             1   p09 idiom.why -- disclosed, §D
```

⚠ **`marginal_ir_per_call` moved on ZERO of the 24 in this sweep**, which is why
`results/synthesis.md` reproduced. **That is not the same as it being
reproducible** — see the blocker below. The 87 `adversarial` and 40 `sanitizer`
leaves are the expected nondeterminism of UB inputs (a rung reading
uninitialised stack prints different garbage each run, and rows are grouped by
identical stdout, so the grouping order shuffles). Worth knowing before anyone
diffs gate records again: **a green sweep of an unchanged tree moves ~127 leaves
that mean nothing.**

### §D — the four doc repairs

1. **`patterns/p09-bitset/NOTES.md`** — *"re-cited by FUNCTION **with the line as
   a hint**"* described hints the same sweep had deleted; rewritten as a
   two-stage history (TASK_068 re-cited by function; TASK_096 `9f8fa9d` deleted
   the hints, the "line as a hint" compromise having been **retracted at
   TASK_071**). **The digest table gains the two missing rows** — it named
   `c391270c673f…` while the record has carried `0a37c0cd1418…` since `9f8fa9d`.
   ⚠ **`RECAP.md` carries the same stale digest — reported, not fixed.**
2. **`patterns/p09-bitset/spec.md`** — ⚠⚠ **INSIDE THE HASHED CONTRACT.**
   `idiom.why` asserted `check.py::exec_code` *"does NOT blank a `spec fn`
   BODY"*. **False since TASK_069** — `exec_code` calls `_blank_ghost_items` and
   its own docstring lists `spec fn` / `proof fn` as layer 3 of five. Marked as
   history with the correction beside it. `verus.rs` is untouched: the
   `q as int / 64` contortion is now belt-and-braces, and every rung `.rs` is
   measurement-hashed.

   **DISCLOSURE — and unlike a new pattern, this diff is REAL and I ran it.**

   ```
   $ git show HEAD:patterns/p09-bitset/spec.md   (fenced block, opcode diff)
   edit opcodes inside the fence: 5
     insert : +'WHEN THIS BLOCK WAS WRITTEN '
     replace: -'s'    +'ed'
     replace: -'oes'  +'id'
     replace: -'fire' +'have fired'
     insert : +'. THAT SENTENCE IS NO LONGER TRUE OF THE GATE AND IS CORRECTED HERE AT TASK_097 ...'
   required identical: True
   forbidden identical: True
   everything except idiom.why identical: True
   ```

       contract_sha256  0a37c0cd1418ae4d5e665c090365cb456dafbf8d1085149ce174a27ff2de9130
                     -> ea0295eaea6ae199c6520c93855cfb80f0399d72a31312fd3154243163f375b7

   Both digests are now in `NOTES.md`, with the TASK_068 pair. Stage 0b
   re-checked the shared paragraph — `ok named-spelling standard present in
   idiom.why, verbatim (11003 bytes, sha256 59748cce2db5...)` — and the audit is
   unchanged: `forbidden: 10 spelling(s), 0 hit(s)`. p09 is `PASS`.
3. **`patterns/p12-strcat-fixed/NOTES.md`** — the stray `)`. `9f8fa9d`'s
   citation sweep turned ``**`inputs_of`** (`check.py:495`) and `measure.py:64`
   (`SKIP_INPUT_PREFIX`) both drop`` into ``**`check.py::inputs_of`** and
   `measure.py`'s `SKIP_INPUT_PREFIX`) both drop``, deleting the opener and
   keeping the closer. Removed; whole file re-checked, **0 unmatched parens**
   with comment and code spans blanked.
4. **`patterns/p06-rotate/NOTES.md`** — cited `check_verus_contract` as
   *"`vparse.by_name` + `norm_clause`"*. Measured: it calls `vparse.parse` →
   `duplicate_names(qualified=True)` → `unique_names` + `norm_clause` and
   **never `by_name`**. ⚠ **And the parenthetical *"(`.temp/p48/pinsim.py`, which
   is that code and nothing else)"* is false in a second way the task file did
   not name: `pinsim.py:25` really does call `vparse.by_name`.** `by_name`
   *raises* on a duplicate bare name where `unique_names` qualifies it, so the
   two agree on p06's tables (p06 has no duplicate) and would diverge on a
   pattern that did. Both corrected; the table stands.

---

## Problems

### ⚠⚠⚠ BLOCKER — `-O3 isolated` marginals are NOT invariant, and a published number flips SIGN

**How I got here: the acceptance test's NEGATIVE CONTROL ARM FAILED.** `b3 none`
plants nothing, runs the same three commands, and should leave
`results/synthesis.md` byte-identical. **It moved 6 lines**, including

```
  line 323  | p03-bounded-stack | 0.00 | 0.00 | LICENSED | small +6.00 (+6.00) **?** / large +6.00 (+6.00) **?** |
            | p03-bounded-stack | 0.00 | 0.00 | LICENSED | small -8.00 (-8.00) **?** / large -8.00 (-8.00) **?** |
  line 178  | `< 2.00`       | 120 | ...   ->   | `< 2.00`       | 122 | ...
  line 179  | `2.00 … 16.00` |  22 | ...   ->   | `2.00 … 16.00` |  20 | ...
```

**Bounded first, so the finding is not read as bigger than it is.** The publish
chain is deterministic: `synthesize.py` and `licence.py --emit` re-run on the
**committed** records both reproduce byte-identical output. The measurement
records (`results/pNN.json`) did not move. **The p03 binaries are byte
reproducible** — two independent `build.py` runs give `unsafe
e7ea55fa488df703` and `verus 75a48f319f14e689`, identical sizes both times.
**p03 is `PASS` in every run and no pin failed.**

**The movement is in `results/gate/p03-bounded-stack.json::marginal_ir_per_call`,
and it is BISTABLE, not noise.** Four records of the same source:

```
p03 marginal_ir_per_call: 96 entries, 22 moved between
  {HEAD == TASK_096 sweep == TASK_097 sweep}  and  {run2 == run3, standalone}
  every delta is exactly +-7.0: [-7.0, 7.0]

opt/mode          moved / total
O0/isolated           8 / 24
O0/whole              4 / 24
O3/isolated           6 / 24        <-- the class the docstring calls INVARIANT
O3/whole              4 / 24
```

⚠⚠ **`check.py::check_marginal_ir`'s docstring states the rule**

```
      -O3 isolated  invariant (0.00 across every probe to date)
      -O3 whole     moves by 7 per per-call stack `memset`
      -O0           moves in BOTH modes
```

**and closes: *"quote the `-O3 isolated` one, which is what
`synthesis/synthesize.py::marginal` already defaults to, and which is the only
cell class no probe has moved."* THAT IS FALSE.** Every moved `-O3 isolated`
key:

```
   safe_tuned/O3/isolated/large.bin             9067.3 ->     9074.3   (+7.0)
   safe_tuned/O3/isolated/small.bin             3418.0 ->     3425.0   (+7.0)
   unsafe/O3/isolated/large.bin                 8441.3 ->     8448.3   (+7.0)
   unsafe/O3/isolated/small.bin                 3059.0 ->     3066.0   (+7.0)
   verus/O3/isolated/large.bin                  8447.3 ->     8440.3   (-7.0)
   verus/O3/isolated/small.bin                  3065.0 ->     3058.0   (-7.0)
```

⚠⚠ **`unsafe` moves `+7` and `verus` moves `-7`, so their DIFFERENCE moves by
14** — and `synthesize.py::derived_correction` is `(ma - mb) - (ka - kb)` with
`ma`/`mb` read straight out of this key at `O3/isolated`.
`3065.0 - 3059.0 = +6.0` becomes `3058.0 - 3066.0 = -8.0`. **That is the
published sign flip, derived arithmetically rather than guessed.** 14 is **7x
the ±2.00 floor** the same table uses to separate "safe" from "coin flip".

**The mechanism is already in that docstring — only its SCOPE is wrong.** It is
the environment-block effect: the initial stack pointer shifts, a per-call stack
scratch array changes alignment, and `__memset_avx2_unaligned_erms` takes a
different tail (±7 Ir/call; p03, p04, p38 and p46 are the four patterns with a
per-call stack `memset`). The docstring already says it is **bistable** and that
*"the discriminator is the presence of a single environment variable, not its
size"*. **Consistent with what I saw:** the two runs launched from the sweep's
`nohup`'d shell script agree with HEAD, and the two launched directly from an
interactive tool shell agree with each other and differ by exactly ±7.

> **Two green gate runs of an unchanged tree, differing only in the shell that
> launched them, publish a different SIGN for p03's `R5 - R4`. The
> `-O3 isolated` rule that was supposed to make this safe does not hold, and
> `synthesize.py::marginal` defaults to `O3/isolated` *because of* that rule.**

**I did NOT fix it**, and I do not think it should be fixed by editing the
docstring: the real question is whether the derived callee-corrected column can
be published at a ±2.00 floor when its transport is ±14. That is a
measurement-policy call for the manager plus a reviewer, not an engineer's edit
late in a task whose sweep has already run. ⚠ It also lands squarely on
`.memory/03-measurement.md` and on `patterns/p03-bounded-stack/NOTES.md` 3b,
which names the same 7 Ir.

**What I left in the tree, and it is a CHOICE:** the **sweep's**
`p03-bounded-stack.json` (kept at `.temp/t97/p03.sweep.json`, restored after the
two diagnostic re-runs), because the sweep is the mandated artefact and runs 2
and 3 were diagnostics. ⚠ **It is also the record that reproduces HEAD's
`results/synthesis.md`, so do not read that byte-identity as evidence about the
tree.** `--check-stale` re-run afterwards: **48 records, 0 STALE**, and
`licence.py`/`synthesize.py` re-run from it.

### P2 — nothing else failed

No gate failure, no Verus failure, no other red arm. `check.py` and `limbs.py`
both re-parse and re-import cleanly; p09's stage 0b and idiom audit were run
standalone before the sweep and again inside it.

---

## Unsure / not done

- **I did NOT touch `check.py::_scan_unsafe_sites`.** The decision is landed.
- **I did NOT edit `.memory/`, `RECAP.md` or `pilot/`.** ⚠ `RECAP.md` carries
  p09's stale `c391270c673f…` digest — **reported, not fixed**, per the task.
- **I did NOT edit `harness/build.py`, `harness/asm.py`, any rung `.rs`, any
  `c/kernel.{c,h}`, any `model.py` or any `inputs/gen.py`.** Nothing
  measurement-hashed moved; `harness/measure.py` is untouched.
- **I did NOT attempt to break a hypothetically-narrowed `_TWIN_BANNED`.** It is
  moot under the landed decision, and the five-case enumeration in §A.4 is not a
  soundness argument.
- **`.temp/t97/a3_twin_attacks.py` is five cases.** Read it as "the ban's other
  five words are load-bearing", not as "an `unsafe` twin would be safe".
- **The blocker's mechanism is INFERRED, not proved by construction.** I proved
  the *effect* (bistable, ±7.0, four records, run2 == run3, binaries byte
  identical, the arithmetic of the sign flip) and I matched it to the mechanism
  `check_marginal_ir`'s own docstring already documents. ⚠ **I did NOT run the
  discriminating experiment** — vary one environment variable, hold everything
  else, and show the `-O3 isolated` cell flip — because it belongs in a task
  that can also decide what to do about the published column, and because the
  sweep had already run and I was not going to touch `harness/` again.
- **I measured the blocker on p03 only.** p04, p38 and p46 are the other three
  patterns with a per-call stack `memset` and are the obvious next probes; I did
  not run them. The 24-pattern sweep moved **zero** `marginal_ir_per_call`
  leaves, which says the sweep is internally consistent, **not** that the other
  three are invariant.
- **`harness/limbs.py::TWIN_BANNED` diverges from `check.py::_TWIN_BANNED`**: it
  is missing `"external_body"`, and `\bexternal\b` does **not** match
  `external_body` (`_` is a word character). So `limbs.py`'s `5ct-cfg` limb
  under-reports an `external_body` twin. **Found, reported, NOT fixed** — it is
  outside the task and the file is the one whose header says the staleness is
  the alarm. One-token fix if the manager wants it.
- **`.temp/p48/pinsim.py` really does call `vparse.by_name`** (see §D), so
  p06's parenthetical was wrong in a second way the task file did not name.

---

## Memory updates

`.memory/` is manager-only, so **none written**. The durable facts to land, in
priority order:

### 1. ⚠⚠⚠ `.memory/03-measurement.md` + `check.py::check_marginal_ir` — the `-O3 isolated` invariance rule is FALSE

`check_marginal_ir`'s docstring rule table says `-O3 isolated  invariant (0.00
across every probe to date)` and closes *"quote the `-O3 isolated` one … the
only cell class no probe has moved"*. **Refuted on p03: six `-O3 isolated`
cells move by exactly ±7.0 between two green runs of an unchanged tree**, and
because `unsafe` moves `+7` while `verus` moves `−7`, the **difference** moves
by **14** — 7× the ±2.00 floor. `synthesize.py::derived_correction` reads that
key, so p03's published `R5 − R4` goes **`+6.00` → `−8.00`**. Bistable, not
scatter: `HEAD == TASK_096 sweep == TASK_097 sweep` on one side,
`run2 == run3` on the other, launched from a `nohup`'d script and an
interactive shell respectively — which is the docstring's own *"presence of a
single environment variable"* discriminator. Binaries are byte reproducible
(two `build.py` runs: `unsafe e7ea55fa488df703`, `verus 75a48f319f14e689`).
Evidence: `.temp/t97/c3_marginal_bistable.log`, `.temp/t97/c2_record_diff.py`.
**The open question is not the docstring: it is whether the derived
callee-corrected column can be published at a ±2.00 floor when its transport is
±14.** p04, p38 and p46 are the other three per-call-stack-`memset` patterns and
were not probed.

⚠ Corollary for `9f8fa9d`'s *"results/synthesis.md byte-identical to HEAD — that
zero is MEANINGFUL"*: **the zero is conditional on the launching shell, not on
the tree.**

### 2. `.memory/02-bench-rules.md` — replace the `_TWIN_BANNED` paragraph

*"ONE THING IS NOT CLOSED … fixing that might ship `p35` the comply way with no
soundness loosening at all"* — **it cannot.** `check.py::_is_trusted` returns
`False` unless the item is `#[verifier::external_body]`, and a twin may not be
`external_body` (**three rules**: `_TWIN_BANNED` lists `external_body`;
`_TWIN_BANNED` lists `external`; `check_trusted_twins` has an explicit
`if twin.external:` limb). **So a twin is structurally never `_is_trusted` and
`_scan_unsafe_sites` hard-fails any `unsafe` token in one** — including when it
is moved into a verified helper, a `#[cfg(slb_twin)]` helper or a
`macro_rules!` (four routes executed, `.temp/t97/a4_helper_route.py`). With
`unsafe` deleted from `_TWIN_BANNED` and nothing else changed, 5c-twin goes
**fully green** and `FAIL [tcb-unsafe] verus.rs:15` is **unchanged**
(`.temp/t97/a2_gate_limbs.py`). **`_TWIN_BANNED` is the SECOND rule. The
catalogue closes.**

✅ Two things survive. **(a) The ban's premise is FALSE for a union read.** It
exists because *"`unsafe` … would make the twin a second copy of the axiom"*
(`f1229af`, TASK_009 — **the manager's §A.2 guess is correct and is the recorded
reason**). True for `get_unchecked` and raw pointers; for a union read Verus
imposes the obligation itself. **Measured:** twin `unsafe { v.i }` under
`requires v is i` is `2 verified, 0 errors`; delete the conjunct →
`1 verified, 1 errors`, *"requirement not met: to access this field, the union
must be in the correct variant"*. **A repaired twin would have teeth.**
**(b) The other five banned words ARE load-bearing:** `proof { assume(false); }
0u64` as a twin body verifies **vacuously at `2 verified, 0 errors`**.

### 3. `.memory/02-bench-rules.md` — the `_verus` rc section, marked FIXED

- ✅ **Landed at TASK_097.** `_verus` flags `rc != 0` **only when the summary
  parsed and `errors == 0`**, records the run in `_VERUS_RC_ANOMALIES` and
  returns `(None, None, out + reason)` — reason **appended**, because callers
  print `out[-300:]`. New stage **5e `check_verus_exit_codes`** turns any
  anomaly into a `[verus-exit]` failure and writes `verus_exit_anomalies` into
  the gate record; it exists because `_run_taut_battery` reads `(None, None)` as
  *"tactic inapplicable"* and would swallow it.
- ✅ **11 / 6 / 5 CONFIRMED**, derived with `ast` (`.temp/t97/b1_verus_sites.py`).
  TASK_096's 12 / 4 was wrong.
- ✅ **`check_verus_contract`'s inline duplicate FIXED BY DELETION** — it calls
  `_verus` now, so the two cannot drift again. `harness/limbs.py::verus` fixed
  the same way. Both **free at the margin**: `harness/*.py` is in the gate
  record's `source_sha256`, **not** in `measure.py::measurement_sources`
  (`build.py`, `asm.py`, `measure.py`, `verus_run.py`, `common/`, pattern
  sources).
- ✅ **Acceptance test with a failing arm exists.**
  `.temp/t97/b3_source_to_published.py e0133`: one command, source → published,
  `results/synthesis.md` moves 9 lines including p03 `PASS → FAIL`, and the
  number the fix catches (**`13 verified, 0 errors`**) is **the same number
  `.temp/t96/a3_gate_comply.log:425` printed as green.**

### 4. `.memory/06-catalogue.md` — `p35` closes

Replace *"THE ONE THING STILL OPEN IS `_TWIN_BANNED` … Probe it before treating
this row as dead"* with **REFUSED**, citing fact 2. Two routes that do not need
the ban repaired exist and are both worse than not shipping: (a) invent a second
trusted item so CN-5's limb C yields `PASS-WITH-BLOCKED-ROWS` — the blocked row
**is** the pattern; (b) drop `union` from `verus.rs` and decode a `[u8; 8]`
payload safely — legal, but it would be the **first `verus.rs` in the tree with
zero trusted items** (measured: 24/24 have ≥1; only p01's control cell
`safe_naive_verus.rs` has none) and it deletes the SIGSEGV arm.

### 5. `.memory/02-bench-rules.md` citation-rot table — two more, and one is a tool

- `patterns/p06-rotate/NOTES.md` cited `check_verus_contract` as
  *"`vparse.by_name` + `norm_clause`"*. It calls **`vparse.parse` →
  `duplicate_names(qualified=True)` → `unique_names` + `norm_clause`** and never
  `by_name`. ⚠ **The parenthetical *"(`.temp/p48/pinsim.py`, which is that code
  and nothing else)"* is false too: `pinsim.py:25` really does call
  `vparse.by_name`.** Both corrected in the file.
- **`harness/limbs.py::TWIN_BANNED` is missing `"external_body"`** relative to
  `check.py::_TWIN_BANNED`, and `\bexternal\b` does **not** match
  `external_body` (`_` is a word character — verified). So the tool that exists
  to re-derive `check.py`'s limbs **under-reports `5ct-cfg`**. **NOT fixed**;
  one token.

### 6. `.memory/03-measurement.md` — record-diff noise

A green sweep of an unchanged tree moves **127 gate-record leaves that mean
nothing**: 87 `adversarial` (list order + garbage stdout on
`adversarial-allpop.bin`, which is UB by construction) and 40 `sanitizer`
(diagnostic text carrying addresses and frame offsets). Anyone diffing gate
records should exclude those two keys first.

---

## Contradictions, counted (286 → 291)

1. **287 — the task file's own title and premise, and two `.memory/` sentences.**
   *"`_TWIN_BANNED` is the real blocker"* / *"fixing that might ship `p35` the
   comply way"* / *"THE ONE THING STILL OPEN IS `_TWIN_BANNED`"* (task file,
   `.memory/02-bench-rules.md`, `.memory/06-catalogue.md`'s `p35` row).
   **Refuted, executed on four routes**: `_scan_unsafe_sites` is the binding
   constraint and refuses all of them; repairing `_TWIN_BANNED` moves `tcb-unsafe`
   not at all.
2. **288 — `check.py::check_marginal_ir`'s rule table.** `-O3 isolated
   invariant (0.00 across every probe to date)` and *"the only cell class no
   probe has moved"* are **false**; six p03 `-O3 isolated` cells move by ±7 and
   the `unsafe`/`verus` difference by 14, flipping a published sign.
3. **289 — `9f8fa9d`'s *"results/synthesis.md byte-identical to HEAD … that zero
   is MEANINGFUL"*.** The zero is conditional on the launching shell's
   environment, not on the tree. (Same cause as 288; a distinct written claim in
   a distinct place, so counted separately — collapse to one if you prefer.)
4. **290 — `patterns/p06-rotate/NOTES.md`'s *"(`.temp/p48/pinsim.py`, which is
   that code and nothing else)"*.** False in a second way the task file did not
   name: `pinsim.py:25` calls `vparse.by_name`, which `check_verus_contract`
   does not.
5. **291 — `harness/limbs.py::TWIN_BANNED` is missing `"external_body"`** and
   `\bexternal\b` does not match it, so the re-derivation tool under-reports the
   limb it exists to re-derive.

**Upheld rather than contradicted, and worth saying so:** the manager's §A.2
guess about *why* the ban exists is **correct and is the recorded reason**;
TASK_096_REVIEW's 11 / 6 / 5 partition is **right**, derived independently; the
`_verus` rc hole is real and reachable; §D's prediction that p09's `exec_code`
claim is false today is **correct**; and CN-5's limbs B and C **both reproduce**.
