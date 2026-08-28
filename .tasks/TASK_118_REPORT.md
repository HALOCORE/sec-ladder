# TASK_118 — `p42`: the third encoding fails too. The retraction stands, and the question is OPEN.

**Role: research engineer. ATTEMPT 2** — attempt 1 died to an account session
limit having landed nothing. Scratch: `.temp/t118/`, notes appended as I went
under a clearly marked *"ATTEMPT 2"* divider, leaving the manager's
reconstruction above it untouched. No `git add`, no `git commit`. `.memory/`,
`RECAP.md` and `results/SYNTHESIS.md` untouched; `results/synthesis.md`
regenerated, never hand-edited.

---

## HEADLINE

⚠⚠ **THE PRIVACY-SCOPED REPAIR DOES NOT SURVIVE, AND ATTEMPT 1'S OWN ARTEFACTS
ALREADY SAID SO.** The manager's reconstruction listed one arm as
`atk_decoy | 19/0 | PURPOSE UNKNOWN — establish before citing`. **That arm is a
verifying leaker**, its purpose is documented in `repair.py`'s own docstring, and
attempt 1 had already measured it leaking (`.temp/t118/b/leakprobe.out`, which
nothing in the reconstruction cites). **The one row the reconstruction could not
place is the row that decides the task.**

I sharpened it, because `atk_decoy` leaks a *superset* of p42's bug (it deletes
both releases; `small.bin` leaks 5 820 000 where the model says 0) and a reader
could dismiss that as *"you deleted the whole cleanup"*. `.temp/t118/decoy_err.py`
narrows it to p42's bug **exactly** — success path frees, error path does not —
and pairs it with the arm that differs in **one** respect: *which ledger the
block is escrowed in.*

```
=== verification (privacy-scoped repair, base = 19 verified, 0 errors) ===
  mustfire_err2        rc=1  18 verified, 1 errors   want FAIL    OK   <- escrowed in the ledger kbody WAS HANDED
      error: postcondition not satisfied
  atk_decoy_err        rc=0  19 verified, 0 errors   want VERIFY  OK   <- escrowed in a ledger kbody MINTS ITSELF
  atk_decoy_err_freed  rc=0  19 verified, 0 errors   want VERIFY  OK   <- same local ledger, BOTH paths free (control)

=== run time (counting global allocator; floor 1028, constant on all four inputs) ===
  atk_decoy_err  adversarial-notag.bin  leaked=1284  model=256   == model.py::leak_bytes
  atk_decoy_err  adversarial-mixed.bin  leaked=1652  model=624   == model.py::leak_bytes
  atk_decoy_err  small.bin              leaked=1028  model=0     == model.py::leak_bytes
  atk_decoy_err  adversarial-win1.bin   leaked=1044  model=16    == model.py::leak_bytes

=== what it compiles to (.temp/t118/identity2.sh -> id-run2.log) ===
-O3  r4          n_fn=128  md5_fn=28432cb848832a692454c3bcc2aee83e
     r5brk       n_fn=128  md5_fn=d3f1194cb10bce2057e0e1f3e28c1e21   R5, release deleted (does NOT verify)
     r5decoyerr  n_fn=128  md5_fn=d3f1194cb10bce2057e0e1f3e28c1e21   *** VERIFIES 19/0 -- IDENTICAL ***
     r5decoyok   n_fn=128  md5_fn=28432cb848832a692454c3bcc2aee83e   the honest twin == R4, pin holds
```

**So encoding 3 reproduces `TASK_116`'s headline line for line:** a program that
**verifies** is byte-identical to R4 with p42's bug planted in it, and leaks
exactly `n_err × win_len`.

**The mechanism is NOT the one that killed encoding 2, and it is the reusable
part.** Privacy did exactly what `TASK_116` predicted — it made the ledger's
**contents** unforgeable, and by **rustc** rather than by Verus
(`error[E0616]: field m of struct res::Ledger is private`; `atk_assign` and
`atk_forge_out` rejected too). ⚠ **What privacy cannot do is make the ledger
UNIQUE.** `res::led_new()` must be public because `kernel` calls it, and
`dig_alloc` sits at crate root beside `kbody`, so the body always has a second
place to put a block. **The obligation binds what you escrow in the ledger you
were handed; nothing binds you to escrow anything there.**

⚠⚠ **DO NOT WRITE THAT VERUS CANNOT STATE LEAK-FREEDOM.** Three encodings, three
verifying leakers, is three data points and not an impossibility proof — and
that exact sentence has already been retracted once. **The governing sentence is
that expressibility at this pin is OPEN.**

### THE HONEST FINAL STATEMENT ABOUT `p42`'s R5

> **`p42`'s R5 does not cover `p42`'s own bug class, and no encoding tried does.**
> The shipped ghost ledger costs **+3 obligations, 0 trusted items, 0
> instructions** — **the price was always accurate and it is the PRODUCT that was
> wrong.** What the postcondition certifies is that the proof author wrote
> *something* on every exit that empties a map the proof author controls; the gap
> to leak-freedom is **one proof line** wide, in three separate places (empty the
> map, overwrite the map, use a different map). **What stands behind
> leak-freedom on BOTH top rungs is Miri plus the `identity` pin — which is
> exactly where it stood before `TASK_110`.** The ledger buys a reader a named,
> greppable discipline; it buys the verifier nothing. ⚠ **The pin protected the
> pattern; the proof did not** — every planted leak moves `md5_fn` at `-O3` and
> `n_fn`/`md5_raw_norel` at `-O0`. ⚠ **Its blind spot: a leak planted in BOTH
> rungs is byte-identical, passes every pin and every obligation count, and is
> caught only by Miri.**

### DID I LAND THE REPAIR? NO — and §B's own instruction is why

> *"If it does NOT survive, SAY SO AND STOP — the retraction stands as written
> and that is a perfectly good outcome."*

It survives the three attacks §B **named** and fails a fourth that reproduces
p42's bug class exactly. §B's criterion was never those three attacks for their
own sake; it was *"`p42`'s R5 covers its own bug class"*. It does not. Landing it
would have moved `verus.obligations` 18 → 19, added ~100 lines of unreviewed
proof to a pattern whose proof has been wrong twice, and bought a claim I would
have had to retract a leaker against in the same breath. **The encoding, its ten
arms and its measurements are recorded in `NOTES.md` 6d and in `.temp/t118/`.**

⚠ **I therefore did NOT run `harness/check.py` on the repaired file, and that was
the manager's blocker #1.** It is moot once the encoding is not seeking
admission. **Stated as a gap, not hidden.**

⚠ **THE LEAD I DID NOT BUILD, so nobody re-derives it:** close both acquisition
routes by moving `dig_alloc` **and** `led_new` inside `mod res` (private) and
exporting a `res::run(...)` that mints the one ledger, calls `kbody`, and drops
it. Then `kbody`'s only acquisition is `led_alloc` on the `&mut Ledger` it was
handed. **UNBUILT AND OPEN, deliberately** — the three-encoding budget, and the
value of a fourth attempt on this axis is lower than the value of an honest
OPEN. It moves the trusted items into a child module (`_is_trusted` and the twin
naming both key on them) and it would still prove nothing about the *program*,
only about `kbody`.

---

## §A — the struck sentence, RE-DERIVED, then RESTORED VERBATIM

The task's call #2 asked me not to un-strike it on the strength of one review.
`.temp/t118/rederive_a.py`, re-run by me:

```
  base               18 verified,  0 errors  (want 18/0)  err-path releases=1  OK   MUST verify
  mustfire_err       17 verified,  1 errors  (want 17/1)  err-path releases=0  OK   MUST FAIL
  mustfire_ok        17 verified,  1 errors  (want 17/1)  err-path releases=1  OK   MUST FAIL
  atk_remove_err     18 verified,  0 errors  (want 18/0)  err-path releases=0  OK   ATTACK
  => SENTENCE IS TRUE
```

I checked the **shape** as well as the truth. *"Verus does NOT prove that
`dig_free` is reached on every path"* is a claim about what **verification**
establishes, so it is established by **one** accepted program that does not, and
refuted only by showing there is none. `atk_remove_err` is that program — **zero
release calls between the tag test and that exit, counted on comment- and
string-blanked code by `harness/vparse.py::blank_noncode` so a comment cannot
fake it** — and the two must-fail arms fire, which is what says the harness can
see a broken exit at all. `led_free` is `dig_free`'s only caller, so the narrow
and wide spellings stand together. ✅ **Restored verbatim.**

⚠⚠ **The recurrence is the finding, and it is sharper than "rule 9 again".**
`p42` is the demonstration that **a matching `contract_sha256` is evidence about
WHEN a sentence was written, not about whether it is true**: `437ae315…`
verified perfectly for eight tasks while carrying **two** false claims inside
the fence. `PROTOCOL` rule 6's own added step (*"re-read the hashed `why`
against your measured numbers"*) is the only thing that catches this, and it did
not fire here because nothing between `TASK_110` and `TASK_116` re-measured.

---

## §C / §C2 — the contract move, disclosed

```
BEFORE  437ae31512cf250acac91e64e289b8cd200dfd83b78797aa3467945b86718d76
AFTER   1af5c4568295ebb2547069e714df5205ca2fcbf8b3e7f289f792b1e1b8a997fe
```

✅ **`git show HEAD:patterns/p42-goto-cleanup/spec.md` still hashes to
`437ae315…`** — `p42` is an existing pattern (landed `TASK_104`, edited
`TASK_110`), so rule 6's diff is **NOT vacuous here** and the disclosure is
checkable rather than asserted.

**ONE move, five in-fence fields, every one a retraction or a correction:**

| field | what moved |
|---|---|
| `idiom.why` | `TASK_110`'s clause that the ghost ledger states leak-freedom — **withdrawn in full**; the sentence `TASK_110` struck is **not restored**; the third encoding recorded so it is not retried |
| `identity[0].why` | same withdrawal in its closing sentence, plus what the pin **did** do (catches every planted leak at both levels) and its blind spot |
| `verus.twin_obligations_note` | *"the GHOST LEDGER that states leak-freedom"* → *"…WHICH DOES NOT STATE LEAK-FREEDOM"*, plus *price right / product wrong* |
| `miri.reason` | **§A** — the `TASK_110` amendment reversed, the struck sentence restored verbatim, with the derivation |
| `miri.blocked_reason` | **§C2**, the owed item from `TASK_107` and `TASK_114`: `check.py` now **removes** an ambient `MIRIFLAGS` and records it; the seed-dependence premise does not reproduce; the mechanism is **OPEN** and belongs to `TASK_119` |

⚠ **NOT moved:** every `requires`, every `ensures`, `obligations` **18**,
`twin_obligations` **21**, `axioms` **0**, `identity` levels, `driver`,
`collapse`, every `required`/`forbidden` entry. **This task retracts prose about
what a measurement means; it moves no measurement.**

**Also edited (gate-hashed, not contract-hashed):** `spec.md`'s pin-table row
for `verus.items kbody`; `verus.rs` module comment, ledger block, `kbody`'s
`ensures` comment and the error-path comment; `unsafe.rs` SAFETY (5);
`NOTES.md` 0/4/6/6b/6c/6d/7/10/10a/11b; `README.md`;
`controls/{affine_leak.rs, miri_seeds.sh, sweep.py, ledger_leak.py}`.

---

## §D

### D.1 — the R3 span was 4.5× too wide. Confirmed **through the gate's own predicate**.

Not read off by eye: `check.py::spelling_matches` imported and driven over
`controls/spellings.py::variants()`.

```
variant       vec![0u8; len]   Vec::with_capacity   extend
r3_ship       no               YES                  YES     <- in contract
r3_revidx     no               YES                  YES     <- in contract
r3_zeroed     YES              no                   YES     <- matches required[4]'s R2 clause
r3_push       no               YES                  no      <- no `extend`
SHIPPED R3    no               YES                  YES     <- the control that says the probe is right
```

✅ **In-contract R3 span `1419 … 1627` (small), `51138 … 59845` (large)**;
published was `1419 … 2634` / `51138 … 102846`. ⚠ **`r3_zeroed` is not a
near-miss — it matches the entry's *R2* acquisition**, so it is a mislabelled
rung, not a variant. ✅ **The overlap conclusion survives**: `1419 ∈ [1407,1617]`
and `1617 ∈ [1419,1627]`.

**CAN THE PIN CARRY THE SCOPING? NO — and the gate's own record proves it rather
than an argument.** `spelling_matches` keys on **language**, never on rung, which
is why `required[4]` states its per-rung scoping in English. The audit applies
all five spellings to all six rungs and files the misses:
`idiom_audit.required_absent` = **13**, `required_pins_nothing` = **5**, and
those 13 rows *are* the scoping the prose describes. **The record already holds
the evidence; nothing compares it to a pin.** Two repairs exist — a per-**rung**
key alongside `c`/`rust`, or pinning the `absent` set — **both are gate changes**
and neither passes `.memory/02-bench-rules.md`'s *"could this happen by
accident?"* test well: no shipped rung is at risk, only an **analysis** that
quotes a variant. **Reported, not wired up** (`PROTOCOL` rule 5).

### D.2 — `controls/sweep.py:27`. Fixed, and it is three lines rather than one word

The docstring now names `CELLS` as the source of truth and records that it said
*six* until `TASK_118` while `CELLS` has always held **seven**.

### D.3 — `controls/ledger_leak.py`. **FIXED, not deleted** — and the task's description of the defect is half right

⚠ **The wording matters.** §D.3 says *"`ERR_ARM`'s anchor fires on the attack,
`OK_ARM`'s does not … a control arm that cannot fire is a named failure class"*.
**Both ARMS fire** (17/1 each, exit named). What did not fire is `OK_ARM`'s
**anchor assert** under an error-path attack, because each substitution asserted
only its own anchor. `check_anchors` now asserts **both** releases, exactly once
each, **before any arm runs**.

⚠⚠ **And the bigger defect, which §D.3 does not name: the script's own printed
headline was FALSE.** It ended with *"the shipped R5 states leak-freedom"* — off
two arms that fired. It now runs **five**, and the two new ones are
**ACCEPTANCE** arms, so the hole is pinned rather than merely described:

```
  base             18 verified,  0 errors  OK   must verify
  leak_err         17 verified,  1 errors  OK   DELETION -- must fail, naming the exit
                  Verus names the exit: return 0; [at this exit]
  leak_ok          17 verified,  1 errors  OK   DELETION -- must fail, naming the exit
                  Verus names the exit: acc [at the end of the function body]
  atk_remove_err   18 verified,  0 errors  OK   ATTACK -- must VERIFY (the hole, pinned)
  atk_assign_err   18 verified,  0 errors  OK   ATTACK -- must VERIFY (the hole, pinned)
```

If a future encoding rejects one, the script FAILS and prints *"the encoding has
CHANGED … do not just edit the expected numbers"*.

⚠⚠ **FOR `.memory/03-measurement.md`'s LIST — A NEW SHAPE, and it is the
manager's to land.** Every existing entry is *a control that could not have
fired*. This one is **a control that FIRED and whose firing did not support the
sentence it printed**: two deletion arms distinguish *no exit-emptying
statement* from *some exit-emptying statement*, and the script concluded
*"states leak-freedom"*. **Asking "what would make this FAIL?" is not enough on
its own — you must also ask "and would its FAILING mean what the script says its
PASSING means?"**

---

## §E — MEASURED, FIXED, AND DELIBERATELY WITHDRAWN. ⚠ THE TASK FILE'S BUDGET IS WRONG BY 25 GATE RUNS.

> §E: *"✅ `check.py` is not measurement-hashed — **this costs the gate run you
> are already paying for**."*

**First half TRUE. Second half FALSE.** `measure.py::measurement_sources` really
does not list `check.py`. **But `check.py::main` hashes `harness/*.py` into every
GATE record's `source_sha256`, and `measure.py --check-stale` examines gate
records too.** Measured, with the one-line edit applied:

```
52 record(s) examined, 25 STALE
STALE  results/gate/p01-array-sum.json   harness/check.py      <- x25, ONE reason each
                                                                  and ZERO results/pNN-*.json stale
```

I started paying it (`.temp/t118/regate.py`, which re-gates each stale pattern
**and diffs its verdict/failures/blocked against `git show HEAD:`**). `p01` came
back `PASS-WITH-BLOCKED-ROWS` in 338.1 s, **SAME as HEAD** — so the edit is
verdict-neutral on at least one other pattern.

⚠⚠ **THEN I READ THE QUEUE, AND WITHDREW IT.** `RECAP.md` item (2) and
`.tasks/TASK_119.md`'s own opening:

> **`TASK_119` … Must run AFTER `TASK_118`** (*it edits `check.py`, which stales
> every gate record*). **One 26-pattern sweep, no re-measure.**
>
> *"⚠ **EVERY ITEM HERE EDITS `harness/check.py` … NONE OF WHICH IS
> MEASUREMENT-HASHED.** ✅ **So the whole task costs ONE 26-pattern gate sweep
> and NO re-measure.** **That is why they are batched.**"*

**`TASK_118` §E asks for a `check.py` edit that `TASK_119` — already written,
already queued to run immediately after me — exists to batch.** Landing it here
buys a **second** 26-pattern sweep and nothing else, since `TASK_119` must sweep
for its own edits regardless. ✅ **So: sweep stopped, `harness/check.py` and
`results/gate/p01-array-sum.json` restored from `git show HEAD:` (read-only git
plus a plain write — no history-mutating command), and the control moved out of
the pattern.**

**§E is delivered as a TESTED RIDER for `TASK_119`:**

| artefact | what to do with it |
|---|---|
| `.temp/t118/E-check-py.diff` | 58 lines; `git apply` it. Records `leak` on every Miri row and gives it a failure branch above the exit-code branch |
| `.temp/t118/miri_leak_key.py` | move to `patterns/p42-goto-cleanup/controls/`; it is the regression control, in `p18-varint-shift/controls/miri_exit_hole.py`'s shape |

**Both ran green before withdrawal**, and the arm that matters is the fourth —
the old `check.py` loaded out of `git` and run on the same mutant:

```
  MUTANT-A   exit=1  ub=False  leak=True       <- error-path dig_free deleted
  CONTROL-B  exit=0  ub=False  leak=False      <- shipped rung
  ok    the RECORD says leak=True on the leaking rung
  ok    ub=False on the same row, so the `leak` key is NEEDED and not redundant with `ub`
  ok    the gate FAILS the mutant: ... Miri reports a MEMORY LEAK at process exit
  ok    the shipped rung passes with leak=False ...
  OLD-CODE   exit=1  ub=False  leak=<KEY ABSENT>
  ok    the old record has NO leak key and ub=False: a reader auditing results/gate/*.json by `ub` saw nothing
  ok    ...and the old gate still FAILED, on the exit code
```

⚠ **`ub=False` on the mutant is asserted deliberately** — without it the control
would show only that the new key works, not that it was **needed**.
⚠ **It also closes a small hole**, and it is a trap for the next pattern rather
than a repair of this one: on an input whose model declares a **non-zero**
`expected_exit`, a leaking rung whose exit happened to equal that code used to
pass. **No committed row is in that position** (186 Miri rows expect 0, five
expect 5, one expects 7; no committed stderr contains `memory leaked`), **so no
shipped verdict changes.**

**`NOTES.md` 10a documents the defect, the measurement and the fact that the fix
is HELD and why** — so the finding is landed even though the code is not.

---

## §F — the gate, the re-measure, and the Miri landmine

### ✅ FINAL STATE

```
harness/check.py p42              PASS-WITH-BLOCKED-ROWS, 0 failures
                                  blocked: ['unsafe.rs on large.bin']  (declared in miri.blocked_reason)
                                  contract_sha256 1af5c4568295...
harness/measure.py --check-stale  52 record(s) examined, 0 STALE
results/synthesis.md              BYTE-IDENTICAL to HEAD (`git diff` empty)
```

### ⚠ §F's MIRI LANDMINE DID NOT FIRE, and the record says which state I got

The task warned `p42` might come back with **two** blocked Miri rows for
environment reasons. **It came back with ONE**, on every one of the four gate
runs. `adversarial-wincap.bin` was GREEN, as at HEAD.

```
marginal_ir_env   NEW  {"bytes": 3269, "tuning_vars": {"LD_PRELOAD": "/usr/libexec/coreutils/libstdbuf.so"}}
                 HEAD  {"bytes": 3269, "tuning_vars": {"LD_PRELOAD": "/usr/libexec/coreutils/libstdbuf.so"}}  <- IDENTICAL
```

⚠ **One data point for `TASK_119`, and it is a NEGATIVE one:** this shell landed
in the same environment state as the committed run, across a session boundary
and four separate gate invocations. **That does not identify the mechanism and I
am not naming one.**

### ✅ THE RE-MEASURE MOVED NOTHING PUBLISHED — 103 of 1391 leaves

`git show HEAD:results/p42-goto-cleanup.json` diffed leaf by leaf against the
new record:

```
leaves total 1391   MOVED 103
     98  wall clock
      2  source hash        <- unsafe.rs and verus.rs, the two rung sources I edited
      2  run metadata
      1  .generated_utc
```

✅ **ZERO `Ir`, zero md5, zero identity, zero static counts, zero checksums.**
Third reproduction of `PROTOCOL` rule 6's note (p19, p46, now p42).

### ✅ AND THE SIDECARS REPRODUCED TOO

`outward_ir.py --emit` is **352 callgrind runs**; re-emitted three times here.

```
synthesis/licence.json     26 -> 26 patterns, 2029 leaves, 7 moved, 0 of them NOT a gate hash
synthesis/outward_ir.json  26 -> 26 patterns, 4208 leaves, 7 moved, 0 of them NOT a gate hash
```

**Every moved leaf is p42's own `gate_source_sha256`. Zero `Ir` values moved
across 4208 leaves**, which is an independent reproduction of the whole outward
sidecar. ⚠ **I backed both files up to `.temp/t118/backup/` before re-emitting,
because `outward_ir.py --emit` writes a fresh `doc` and a pattern whose
`.temp/build/` is incomplete would silently lose its rows.** None did.

**Chain run, in the mandatory order:** `build.py p42` → `measure.py p42` →
`check.py p42` → `report.py p42` → `check.py p42` →
`licence.py --emit` → `synthesize.py` → `outward_ir.py --emit` →
`synthesize.py` → `measure.py --check-stale`.

---

## Problems

1. ⚠ **I paid for four `p42` gate runs (7.5 min each) and two re-measures**,
   because I edited `verus.rs` (measurement-hashed) and `controls/sweep.py`
   (gate-hashed) *after* running the chain, and because §E's withdrawal
   invalidated one gate record. **All self-inflicted sequencing, all disclosed.**
   The transferable version: **finish every edit to `*.rs`, `c/*` and
   `controls/*.py` before the first `measure.py`, and every edit to any pattern
   file before the first `check.py`.**
2. ⚠ **A `SyntaxWarning` I introduced and then removed**: `/!\ ` inside a Python
   docstring is an invalid escape sequence. Caught with
   `python3 -W error::SyntaxWarning`. `.rs`/`.sh` comments are unaffected; only
   `controls/*.py` docstrings need the `⚠` spelling.
3. **`atk_forge_in` verifies at `20/0`** — forging a `Ledger` from *inside*
   `mod res` still works. That is expected (the module is the boundary) and is
   not why the encoding fails; `atk_decoy_err` is.

## Unsure / not done

1. **I did not run the gate on the repaired `verus.rs`.** It was the manager's
   blocker #1 and it is moot once the encoding is not seeking admission, but it
   means `_scan_unsafe_sites` on a real pdir and obligation counting against the
   pin remain **unrun for that file**. The three things the manager cleared by
   importing the harness (vparse, `_is_trusted`, the `unsafe` surface) stand.
2. **I did not build the fourth encoding** (`dig_alloc` + `led_new` private to
   `mod res`, `res::run` as the entry). Deliberate. **OPEN.**
3. **My leak instrument is a counting `#[global_allocator]`, not LeakSanitizer** —
   attempt 1's, which is `TASK_116`'s, reused unchanged so the three sets of
   numbers are comparable. valgrind memcheck cannot start on this box. It is
   validated by a constant floor (1028 on all four inputs) and by agreement with
   `model.py::leak_bytes` on all four.
4. **`spec.md`'s prose asserts a TCB of "5 / 3"; `_is_trusted` counts 3.** Both
   are right (5 `external_body`, 3 trusted) and I left the wording alone, but the
   manager's reconstruction flagged the mismatch and I am not certain the "5" is
   never read as a trusted count.
5. **I did not re-run `controls/{spellings,sweep,leak,miri_seeds}.py/sh`
   end-to-end.** `spellings.py`'s variants were exercised through
   `spelling_matches` (§D.1) and `affine_leak.rs` was re-verified both arms;
   `sweep.py` and `miri_seeds.sh` had comment-only edits and were syntax-checked,
   not run.
6. **I did not touch any other pattern**, `harness/{build,asm,measure}.py`,
   `.memory/`, `RECAP.md` or `results/SYNTHESIS.md`.

## Memory updates

**None — `.memory/` and `RECAP.md` are manager-only.** Everything durable is in
this report, in `patterns/p42-goto-cleanup/NOTES.md` (sections 0, 6, 6b, 6c, 6d,
10, 10a, 11b) and in `.temp/t118/NOTES.md`.

⚠ **Two things the manager owes `.memory/` once this is reviewed:**
(a) `.memory/03-measurement.md`'s controls list gains a **new shape** (§D.3 —
a control that fired and whose firing did not support its printed sentence);
(b) `.memory/04-verus.md`'s ledger section needs the **third** encoding recorded
with its residual, and the *"a `Tracked<T>` obligation is only as strong as the
smallest scope that can construct a `T`"* rule needs its second half:
**privacy fixes the contents, not the uniqueness of the container.**

---

## RUNNING COUNT — **466 + 14 on this branch**

⚠ **Branch delta only. `PROTOCOL` rule 1 says the count is a rigour signal and
not a ledger; reconciliation is the manager's job, not mine, and I have not
re-added 466.**

1. **The privacy-scoped encoding admits a verifying leaker of p42's exact bug
   class** — `19 verified, 0 errors`, `model.py::leak_bytes` on all four inputs,
   against a control differing in one respect and REJECTED at `18/1`.
2. **That leaker is byte-identical at `-O3` to R4 with p42's bug planted**
   (`md5_fn d3f1194c…`), and its honest twin is byte-identical to shipped R4 —
   so the `identity` pin catches it and the proof does not, exactly as for
   encoding 2.
3. **The mechanism is new and general: privacy makes a ledger's CONTENTS
   unforgeable and cannot make the ledger UNIQUE.** Three encodings, three
   leakers, one residual.
4. **Attempt 1's `atk_decoy` was already a verifying leaker with a run-time
   measurement**, recorded in the handoff as *"PURPOSE UNKNOWN"*. **The row that
   decided the task was the one row the reconstruction could not place** — a
   reconstruction that reads the summary table and not the generator.
5. **§A's sentence re-derived independently and confirmed TRUE**, with the
   release count taken from comment-blanked code and two must-fail arms firing.
6. **`p42` is the proof that a matching `contract_sha256` is evidence about WHEN,
   not about TRUTH** — `437ae315…` verified perfectly for eight tasks while
   carrying two false in-fence claims.
7. **The published R3 span is 4.5× too wide, confirmed through the gate's own
   `spelling_matches`** rather than by reading; `1419 … 2634` → `1419 … 1627`.
8. **`r3_zeroed` is not a near-miss — it matches `required[4]`'s R2 clause**, so
   it is a mislabelled rung and not an out-of-contract variant.
9. **The pin cannot carry `required[4]`'s per-rung scoping, and the gate record
   already shows the scoping**: `required_absent` 13, `required_pins_nothing` 5.
10. **`controls/ledger_leak.py` printed a false headline off two arms that
    FIRED** — a new shape for the controls list, distinct from every entry in it.
11. **`check.py` is NOT measurement-hashed but IS gate-record-hashed**:
    `--check-stale` goes 0 → **25 STALE**, all gate records, one reason. **§E's
    stated budget is wrong by 25 gate runs.**
12. **`TASK_118` §E and `TASK_119` collide** — `TASK_119` is written and queued
    to batch exactly this `check.py` edit into one sweep. §E withdrawn as a
    tested rider; a second 26-pattern sweep avoided.
13. **The re-measure moved 103 of 1391 leaves, none of them published** (98 wall
    clock); **and `outward_ir.json`'s 352 callgrind runs moved 0 of 4208
    non-hash leaves.** Two independent reproductions.
14. **§F's Miri landmine did not fire on any of four gate runs**, with
    `marginal_ir_env` byte-identical to HEAD — a clean negative for `TASK_119`.
