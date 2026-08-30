# TASK_148 — build `p35`: tagged union / discriminated dispatch (the TYPE axis)

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You may use
`harness/check.py` and `harness/measure.py`.

⚠ **Run AFTER `TASK_146`/its review.** ⚠ **NOT A TEMPORAL ROW.** `p35` is the
**TYPE** axis (CWE-843), and the tree's type axis still has **ONE** built row
(`p38`) — `results/SYNTHESIS.md` §7 says in terms that *"every claim this
document makes about the type axis rests on ONE pattern."* **This row is the
second.**

## The bar, because it is the whole reason this row exists again

`CLAUDE.md` **rule 6** and `.memory/02-bench-rules.md`'s *THE ADMISSION BAR IS
C-SIDE ONLY*. **ADMITTED at `TASK_143`, and RANKED FIRST OF SEVEN by distance
from `p27`/`p29`.**

> ⚠⚠⚠ **THIS ROW WAS REFUSED THREE TIMES AND EVERY REFUSAL WAS VERUS-SIDE OR
> GATE-SIDE.** *"A trusted item owes a twin and a union read has no safe twin"*;
> *"`p35` has no legal configuration"*; *"such a `p35` has a precondition checked
> by NOTHING"*. **All three are now FINDINGS TO REPORT, and none may shrink,
> weaken or retire this row.** Whatever the Rust and Verus rungs land on **is the
> result.**

## What already exists — promote it, do not re-derive it

- `.temp/t143/p35/{body.inc,k.c,matrix.json}` and `.temp/t143/{build.sh,
  difflines.sh,matrix.py,common/}` — the admitted demonstration.
- ⚠⚠ **`.temp/mgr147/NOTES.md` — the MANAGER's re-verification, and it carries a
  CONTROL THE DEMONSTRATION DID NOT HAVE. Read it first.** Also
  `.temp/mgr147/{repro.sh,ubctl/k.c}`.

✅ **Keep the include-twice construction** (`body.inc` with `SLB_HARDEN` 0 and 1).
⚠ **But see `p32`: applying it to the RUNGS removes the C kernel bodies from
`forbidden_verdict`'s text scan, so `p32` put it in `controls/` and measured the
shipped preprocessed files instead. Do that.**

## The C mechanism, and why it duplicates nothing

A cell is a **tag plus a union**. Storing a pointer takes a resource from a
budget that can run out, so the store has a **FAILURE PATH** — and R1 publishes
the **tag before the payload lands**. When the budget is exhausted the cell
claims to hold a pointer (or a double) while the union still holds the integer a
previous store put there. The dispatcher then reads it **at the claimed type**.

⚠⚠ **THE SAFETY LINE IS A STATEMENT ORDERING, AND THAT IS A THIRD SHAPE FOR THIS
TREE**: `p27`'s is a **conjunct**, `p13`'s is a **store**, `p35`'s is a
**sequencing constraint**. ✅ **Manager-re-run: `+2 / −2` preprocessed lines, and
the diff is a PURE REORDER at both sites** — `cells[idx].tag` moves from before
the `if (navail > 0)` to inside it, after the payload store.

**Two bug classes, one ordering, selected by the input:**

| input | harm | detector |
|---|---|---|
| `adv-ptr-confusion` | dereferences an **attacker-derived integer** | SIGSEGV; ASan reports |
| `adv-dbl-confusion` | compares a **garbage double** → silent wrong value | ⚠ **NOTHING, anywhere** |

**No free, no lifetime, no aliasing — nothing to duplicate.** The nearest built
rows are `p19` (state machine: no union, no reinterpretation of one object's
bytes at a second type) and `p16` (TLV: its selector bounds a **LENGTH**, it does
not choose a **TYPE**). ✅ Manager-re-run: benign identical on all five builds,
`n = 1` in 20 runs on every row, SIGSEGV included.

## ⚠⚠ THE CONTROL THE DEMONSTRATION LACKED — ship the repair

`p35`'s `k_ctl` dereferences an attacker-derived integer. **ASan reports that;
UBSan does not** (`-fsanitize=undefined` has no wild-pointer check), so on the
`ubsan` build the control **SIGSEGVs at `rc=139` with 0 diagnostics**:

```
asan        rc=1    hits=4   AddressSanitizer     <- fires
asan_clang  rc=1    hits=4   AddressSanitizer     <- fires
ubsan       rc=139  hits=0   (SIGSEGV, no diagnostic)   <- DID NOT FIRE
```

⚠ **So the `ubsan` column's silence was UNINTERPRETABLE as shipped** — a UBSan
build that says nothing looks exactly like one that is not linked in (RECAP trap
5; `.memory/03-measurement.md` entry 14). ✅ **Closed at `.temp/mgr147/ubctl/k.c`
with a UBSan-specific control — signed integer overflow — which fires
`runtime error: signed integer overflow` on the same build line while the plain
build is silent.** **The premise stands and now has evidence. Ship a control of
that shape.**

> ⚠ **THE RULE: A POSITIVE CONTROL LICENSES ONLY THE DETECTOR IT FIRES IN.**
> A table with a per-detector column owes a per-detector control.

✅ **You do NOT need to widen this to the tree** — the manager checked: `check.py`
stage 7 builds **one** binary with `-fsanitize=address,undefined` and sets
`fired` if either speaks, and every committed silence claim in
`patterns/*/NOTES.md` is written **jointly** (*"ASan + UBSan clean"*). The gap
was in the scratch demonstration only.

## ⚠⚠⚠ THE GATE RISK — READ THIS BEFORE YOU DESIGN THE R5, AND DO NOT GAME IT

`harness/check.py`'s `_scan_unsafe_sites` / `_TWIN_BANNED` interaction is the
reason this row was refused twice. **Manager-verified facts, do not re-derive:**

- **Verus supports the Rust `union` NATIVELY** — the correct-variant obligation
  is **first class in the type system**. Declared inside `verus!`, a wrong-variant
  read is `error: requirement not met: to access this field, the union must be in
  the correct variant`, and `requires v is i` gives **`2 verified, 0 errors`**.
  ⚠ **It is a LANGUAGE BUILTIN, not a vstd spec, so a `std_specs/` grep MISSES
  it.**
- **There is no safe union read** (`error[E0133]`), and `_TWIN_BANNED` forbids
  the `unsafe` keyword in a twin, so a twin must be justified away →
  `n_twins == 0` → hard FAIL. ✅ **`_is_trusted` returns `False` unless the item
  is `#[verifier::external_body]`, and a twin may not be `external_body`, so a
  twin is STRUCTURALLY never `_is_trusted`.**
- ⚠⚠ **`TASK_098` §4A found a GATE-CLEAN configuration: `include!("h.rs")`
  OUTSIDE `verus!{}` verifies `1 verified, 0 errors` with `_scan_unsafe_sites` at
  0 failures, because `include!` is a MACRO and the walk never sees the file.**

⚠⚠⚠ **DO NOT SHIP THE `include!` CONFIGURATION TO MAKE THE GATE GREEN.** It
passes precisely because the gate cannot see the file, which makes the row's
safety obligation **checked by NOTHING** — the opposite of what a pattern here is
for, and it would be gaming the instrument rather than measuring with it.
**Report it as a live `_path_includes` hole (`TASK_009_REVIEW` blocker x1,
re-opened by a different spelling) and let the manager decide separately.**

✅ **SHIP THE HONEST CONFIGURATION AND MAKE THE GAP THE FINDING.** `p42` is the
standing precedent and it is a good one: it ships with the expressibility
question **OPEN**, keeps both the struck original and the struck replacement
visible, and says plainly *"what stands behind leak-freedom is Miri plus this
pin"* and **"THE PIN PROTECTED THE PATTERN; THE PROOF DID NOT."** ⚠ **A row whose
R5 cannot state its obligation STILL SHIPS, with the gap as the result.**
⚠ **If the gate hard-FAILS, STOP AND REPORT the exact stage and predicate rather
than working around it** — a `check.py` change is a 28-pattern re-gate and is the
manager's call, not a build-task edit.

## Deliverables

1. **Build `patterns/p35-...`** to `patterns/p01-array-sum/`'s structure and
   `p32-free-list-pool/`'s recent example: seven rungs, `spec.md` with the
   machine-readable `slb-contract` pins, `model.py`, `inputs/gen.py`,
   `NOTES.md`, `README.md`, `controls/`.
   **`harness/check.py p35` must PASS and `measure.py` must record it** — or the
   gate must fail for a reason you have isolated and reported.
2. ⚠⚠⚠ **`model.py`: TWO failure modes, not one.**
   **(i) NOT TRANSLITERATED** — `TASK_136`'s was a line-by-line copy of its own
   kernel and that is how its bug went undetected. The obvious independent
   formulation here is a **tagged value as a Python `(tag, payload)` pair with an
   explicit "payload not yet written" state**, which is what the ordering bug
   actually creates.
   **(ii) NO CHECK THAT IS A TAUTOLOGY OF THE MODEL'S OWN REPRESENTATION**
   (`.memory/03-measurement.md` entry **19**, found on `p32` at `TASK_145`).
   ⚠⚠ **`p35` IS THE MOST EXPOSED ROW IN THE TREE TO THIS**, because a Python
   model has **no unions** — a `(tag, payload)` pair cannot reinterpret bytes at
   a second type, so the harm may be **unrepresentable** in the model by
   construction. **Decide this FIRST and write the answer down.** ✅ **If the
   model cannot see it, DECLARE `sanitizer_expect` and say so — declaring is
   honest, a derivation that cannot fire is not.**
   ⚠ **If you build a must-fire arm, make it REPORT rather than CRASH when the
   detector is broken.** `p32`'s crashes: loud, but the diagnostic is lost, and
   fixing it there costs a re-measure. **Free to get right here.**
3. **The R5 owes an ATTACK ARM THAT MUST FAIL and a VACUITY arm.** ⚠ `p42`'s
   ghost ledger verified `18/0` while leaking; `TASK_136`'s ARM_C was discharged
   by `fn arm_c() -> u8 { 9 }`; and `p32`'s `assume(false)` verifies `15/0` while
   `check.py` only SHOUTS. ✅ **`p32`'s battery is the shape to copy — it is a
   THREE-cell result: exec-only → fail, spec-only → fail, both → verify.**
4. ⚠ **If you publish any rung-to-rung cost difference, search BOTH rungs'
   spellings and count the levers on each side.** Five patterns published a
   headline wrong in the flattering direction. **A row may ship with NO cost axis
   — `p29` and `p32` do — but say so explicitly so the absence does not read as a
   zero.**
5. **Tell the manager the bug class** for `harness/tools/composition.py`.
   ⚠ **Do not edit that file.** Expect `--check` to FAIL with
   `built but unclassified` until the manager classifies it — **that is the check
   working.** ⚠ Propose the wording; do not apply it. **This should be the
   `type` axis's SECOND row.**

## Rules

- `.temp/t148/` for scratch. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`.** No `git add`/`git commit`.
- ⚠ **Do not touch `.temp/t136/ t137/ t139/ t140/ t141/ t142/ t143/ t144/ t145/
  t146/ t147/ t91/ mgr146/ mgr147/ mgr148/ mgr149/ mgr150/ mgr151/`** — all
  cited evidence. **Copy from them; do not modify them.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`. ⚠ Grep
  `~/tools/verus/vstd/std_specs/` **specifically** before any "no spec exists" —
  ⚠⚠ **and note that for THIS row a `std_specs/` grep is the WRONG instrument
  anyway: union support is a language builtin.**
- Hand-run sanitisers need `env -u LD_PRELOAD`; **never truncate a sanitiser log
  with `head`**; **every harm probe owes a positive control that must fire — in
  the detector whose column it licenses.**
- ⚠ **Read `blocked` out of the RECORD, never `grep` the log.** Expect
  `p01 = 1`, `p42 = 1`; `p42` may legitimately be 2.
- ⚠⚠ **If the gate fails on `[tables]`, run `harness/report.py pNN` and
  re-gate.**
- ⚠ **Generate control JSONs AFTER the sources are final** — `c/*`, `*.rs`,
  `model.py` and `inputs/gen.py` are MEASUREMENT-HASHED; a comment-only edit
  stales the record.
- ⚠ When a `contract_sha256` moves, `python3 harness/tools/contract_diff.py p35`
  says what moved, from `git` alone. Use it for your disclosure.
- Keep the generator, delete the artefact (`.memory/00-environment.md`
  constraint 6).
- Report to `.tasks/TASK_148_REPORT.md`. **PROTOCOL rule 2: the count is in the
  newest `.tasks/TASK_NNN*_REPORT.md`'s closing paragraph — read it there, do not
  guess.**
