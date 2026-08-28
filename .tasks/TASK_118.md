# TASK_118 — `p42`: try the repair FIRST, then retract what does not survive it

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
**`.tasks/TASK_116_REPORT.md` in full** (it is the review you are landing), then
`patterns/p42-goto-cleanup/{spec.md,verus.rs,unsafe.rs,NOTES.md,README.md}` and
`patterns/p42-goto-cleanup/controls/`.

Scratch in **`.temp/t118/`**.

⚠ **DO NOT START THIS UNTIL THE MANAGER SAYS THE TREE IS FREE.** It runs the gate
and a re-measure, and concurrent agents read `results/gate/`.

---

## The situation

**`p42`'s R5 has now had TWO published headlines retracted.** `TASK_116` produced
a **leaking program that satisfies the ghost ledger's leak-freedom `ensures`** —
one line, `proof { let tracked _dl = led.tracked_remove(0int); }` in place of the
error path's `led_free`:

```
shipped          18 verified, 0 errors   /  21 verified, 0 errors (--cfg slb_twin)
leaking variant  18 verified, 0 errors   /  21 verified, 0 errors     <- identical
obligations, twin count, axioms          UNCHANGED
bytes leaked     n_err x win_len = model.py::leak_bytes exactly
-O3 kernel       md5_fn d3f1194cb10bce2057e0e1f3e28c1e21, n_fn 128
                 == the shipped R4 WITH p42's BUG PLANTED IN IT
```

✅ **Manager re-ran all four numbers. `.temp/mgr115/p42/REBUILD.sh` regenerates
them; the variant is `.temp/r116/ledger/atk_remove_err.rs`.**

**Mechanism:** `Map::tracked_remove` is the call `led_free` itself makes.
**Wrapping an affine resource in a map does not make it linear — it makes the
drop take one more line.**

⚠ **The manager has already landed the retraction in `RECAP.md`,
`.memory/04-verus.md`, `.memory/06-catalogue.md` and `results/SYNTHESIS.md`.
Those are manager-only and are DONE. The PATTERN still asserts the false claim
in ~12 places, and that is your job — but do §A and §B first, because they can
change what the retraction says.**

## §A — ⚠⚠ BLOCKER 2, AND IT IS UNCONDITIONAL. DO IT FIRST.

**`spec.md::miri.reason`'s `TASK_110` amendment STRUCK A TRUE SENTENCE AND
REPLACED IT WITH A FALSE ONE — INSIDE `contract_sha256`.** The struck sentence
was:

> *"Verus does NOT prove that `dig_free` is reached on every path."*

⚠⚠ **THAT SENTENCE WAS RIGHT, AND `TASK_116` HAS NOW PROVED IT RIGHT WITH A
VERIFYING LEAKER.** **Restore it.** ⚠ **This is PROTOCOL rule 9's `TASK_099`
shape for the second time** — a true sentence struck on the strength of an
unreviewed mechanism — **and this time it happened inside a hashed block.**
**Say so in `NOTES.md`, because the recurrence is the finding.**

## §B — the repair, time-boxed. ⚠ TRY IT BEFORE YOU WRITE THE RETRACTION.

`TASK_116` measured a live lead and did not build it:

- a **module-local** `Tracked<Freed>` receipt is **FORGEABLE** in proof mode —
  `3 verified, 0 errors` for a forged receipt;
- a **PRIVACY-SCOPED** one is **NOT** — rustc rejects the forgery.

⚠ **The general rule it implies, and it is the reusable part: a `Tracked<T>`
obligation is only as strong as the SMALLEST SCOPE THAT CAN CONSTRUCT A `T`.**
**Both failed encodings missed exactly this.**

**Build it against the real kernel.** ⚠⚠ **AND ATTACK YOUR OWN REPAIR WITH THE
SAME TWO ATTACKS THAT KILLED THE LEDGER, PLUS A THIRD:**

1. `tracked_remove`-style: drop the obligation token directly.
2. `tracked_empty`-style: overwrite the whole structure.
3. **Construct the receipt without freeing** — the forgery, from *inside* the
   privacy boundary and from *outside* it. **Both arms must be run and reported.**

✅ **If it survives all three: `p42`'s R5 covers its own bug class and that is a
real result** — ⚠ **and check the `identity` pin still holds, because ghost code
must erase to nothing. A repair that moves the machine code is not admissible
here and would be a finding in itself.**
⚠⚠ **If it does NOT survive, SAY SO AND STOP — the retraction stands as written
and that is a perfectly good outcome.** **Do not iterate more than three
encodings; report what failed and how.** ⚠ **This axis has now produced two
confident published claims that were false. A third would be worse than an open
question.**

⚠ **Whatever happens, the honest state is: two encodings tried, both admit a
verifying leaker, INEXPRESSIBILITY IS NOT PROVEN.** **Do not write that Verus
cannot state leak-freedom** — that exact sentence has already been retracted once.

## §C — the retraction sites in the pattern, once §B has decided the wording

`TASK_116` lists them. **Budget them against `PROTOCOL.md`'s table:**

| site | hashed into | cost |
|---|---|---|
| **4 `spec.md` fields inside the fence** | contract + gate | **`contract_sha256` moves** |
| `spec.md` prose, `NOTES.md`, `README.md` | gate | gate re-run |
| ⚠ **`verus.rs`, `unsafe.rs`** | ⚠ **MEASUREMENT** | ⚠ **a re-measure** |
| `controls/*` (3 files) | gate | gate re-run |
| **`results/tables/p42-*.md`** | — | ⚠⚠ **GENERATED — fix `harness/report.py`'s input, never the file** |

⚠ **You are paying for a re-measure anyway, so batch EVERY prose fix into the
same pass** — `PROTOCOL.md` rule 6's note says the re-measure is cheap and moves
nothing published (p19: 1 m 17 s; p46: 111 of 1371 leaves, **zero `Ir`, zero
md5, zero identity**). ⚠ **Record the `slb-contract` sha256 BEFORE and AFTER and
disclose the move**, per rule 6.

⚠⚠ **AND RE-READ THE HASHED `why` AGAINST THE MEASUREMENTS.** `idiom.why`
currently asserts *"a proof cannot drop the MAP that holds it"* — **`TASK_116`
refuted that in its own words** (`Map::tracked_empty()` assigned over the ledger
verifies). **Rule 6 is necessary and not sufficient: a frozen declaration is
evidence about WHEN it was written, not about whether it is still true.**

## §D — the three smaller ones, all confirmed by the review

1. ⚠ **The published R3 span `1419…2634` is 4.5× too wide.** `r3_zeroed` and
   `r3_push` are **outside `required[4]`'s R3 idiom**, so the in-contract span is
   **`1419…1627`**. ⚠ **This is `p23`'s span lesson for the third time — an
   endpoint is what someone thought to write, not what the declaration permits.**
   ⚠ **`TASK_116` notes its scoping rests on `required[4]`'s PROSE, which no gate
   stage reproduces. Say whether the pin can be made to carry it.**
2. **`controls/sweep.py:27`** — docstring says *"the six measured ones"*, `CELLS`
   lists **seven** (it includes `c-gcc-h`). One word.
3. **`controls/ledger_leak.py`** — `ERR_ARM`'s anchor fires on the attack,
   **`OK_ARM`'s does not.** ⚠ **A control arm that cannot fire is a named failure
   class here** (`.memory/03-measurement.md`'s list). **Fix or delete it, and say
   which.**

## §E — one harness item, and it is NOT measurement-hashed

**`check.py`'s Miri `ub` key reads `False` for a leak.** The gate still FAILS
(on the exit code), so nothing shipped is wrong — ⚠ **but the RECORD shows
nothing, so a reader of `results/gate/p42-*.json` cannot see that Miri caught a
leak.** ✅ **`check.py` is not measurement-hashed — this costs the gate run you
are already paying for.** ⚠ **Give it an arm that MUST FIRE.**

## §F — the gate, last

⚠⚠⚠ **READ THIS BEFORE YOU RUN THE GATE — `TASK_114` FOUND A LANDMINE THAT WILL
LOOK LIKE A REGRESSION YOU CAUSED, AND IT IS NOT.**

**`MIRIFLAGS` was never the variable.** The `miri` **driver** does not parse it
at all — it is `cargo-miri`'s variable, and the gate invokes the driver. **The
4.6× is an ENVIRONMENT-BLOCK effect**, the same axis as `TASK_107`'s ±7:

```
MIRIFLAGS unset          338.1 / 347.4 / 345.4 / 343.1 s     <- SLOW
MIRIFLAGS=""              75.1 / 75.4 s                      <- fast
SLB_R114_DECOY=""  (a DECOY, nothing to do with Miri)  74.4 / 75.9 s
$OLDPWD removed           75.3 s
                          10-rung ladder: 1 slow, 10 fast
```

⚠⚠ **`MIRI_TIMEOUT` is 180 s, and `results/gate/p42-goto-cleanup.json` currently
records `adversarial-wincap.bin` as GREEN. In the shipped `MIRI_FLAGS = ()`
configuration, from a shell like this one, that row lands in the 340 s state and
goes BLOCKED.** **`TASK_107`'s landed fix does not CONTROL the state — it
CHANGES it, and here it selects the slow one.**

**So `p42` may come out with TWO blocked Miri rows instead of one.**
⚠ **THAT IS NOT A REGRESSION YOU INTRODUCED. Do not "fix" it, do not chase it,
and do NOT let it stop your gate.** ✅ **Report which rows blocked and what
`marginal_ir_env` recorded, and move on** — the fix is `TASK_119`'s and the
mechanism is OPEN. ⚠ **`miriflags`, `miriflags_removed_ambient` and
`miri_version` are IDENTICAL in both states, so the record cannot currently tell
you which one you got.**

⚠ **If a Miri row you need blocks, you may re-run that one row by hand** and say
so explicitly, rather than editing anything to make it pass.

Full `harness/check.py p42`, then a re-measure of `p42` only, then
`synthesis/licence.py --emit` **BEFORE** `synthesis/synthesize.py`, then
`synthesis/outward_ir.py`, then **`synthesize.py` AGAIN** (its sidecar pin makes
the second run mandatory), then `harness/measure.py --check-stale`.

**Expect `PASS-WITH-BLOCKED-ROWS` for `p42`** (Miri on `large.bin`, declared).
⚠ **If anything else turns red, STOP AND REPORT.** ⚠ **Diff
`results/synthesis.md` and state exactly which lines moved and why.**

---

## Constraints

- **`.temp/t118/` only. No `/tmp`.** **Notes in `.temp/t118/NOTES.md` as you go.**
  Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- **`.memory/` and `RECAP.md` are manager-only — the manager has landed its half
  already. `results/SYNTHESIS.md` is manager-only too.** ⚠⚠ **`results/synthesis.md`
  (lower case) is GENERATED — never edit it.**
- ⚠ **Do not touch any other pattern**, and do not touch
  `harness/{build,asm,measure}.py` — all three are measurement-hashed.
- ⚠ **Every probe needs an arm that MUST FIRE.** The list at the end of
  `.memory/03-measurement.md` holds **six live entries numbered 1–7** (entry 5 is
  retracted). ⚠ **Do not quote its ordinal.** ⚠ **§D.3 is about ADDING to that
  list, so read it first.**
- Verus via `./verus_run.py` only, **single-file mode, never `--cargo`**. Do not
  bump the pin.
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_118_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 466, reconciled by the manager across
five concurrent branches.** Derivation, stated so it can be checked rather than
trusted: base **414**; `TASK_113` **+11** (→425); then `TASK_114` **+6** and
`TASK_115` **+12** off the 414 branch, and `TASK_116` **+9** and `TASK_117`
**+14** off the 425 branch. ⚠ **PROTOCOL rule 1 says this is a RIGOUR SIGNAL AND
NOT A LEDGER — do not re-add it, and do not treat 466 as an audited total.**
**Carry it forward; increment it by what you find.**

The calls I am least sure of:

1. ⚠⚠ **That the repair is worth attempting at all (§B).** ⚠ **This axis has
   produced two confident published claims that were both false.** **The
   strongest argument for trying is that `TASK_116` has already measured the
   discriminating fact — forgeable module-local, unforgeable privacy-scoped — so
   this is building a measured lead, not guessing.** ⚠ **The strongest argument
   against is that a third encoding invites a third retraction. If you think the
   honest move is to leave the question OPEN and just retract, SAY SO AND DO
   THAT.**
2. **That §A's restored sentence is exactly right.** ⚠ **I am asking you to
   un-strike a sentence inside a hashed block on the strength of one review.
   Re-derive it yourself from the leaking variant before you restore it** — if
   the sentence is subtly wrong in some other way, restoring it verbatim repeats
   the original error in the opposite direction.
3. ⚠ **That `p42` should keep shipping at all.** **It is the only pattern in the
   tree whose R5 does not cover its own bug class, its proof has been wrong
   twice, and it is one of the two `PASS-WITH-BLOCKED-ROWS` rows.** ⚠⚠ **I think
   it SHOULD ship — a pattern that documents two failed encodings and an open
   question is more useful than one that quietly works — but that is a judgement
   and I want it challenged.**
