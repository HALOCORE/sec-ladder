# TASK_146 — build `p28`: intrusive doubly linked list, two link sets, incomplete destroy

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You may use
`harness/check.py` and `harness/measure.py`.

## The bar, because it governs everything here

`CLAUDE.md` **rule 6** and `.memory/02-bench-rules.md`'s *THE ADMISSION BAR IS
C-SIDE ONLY*. **This row is ALREADY ADMITTED** (`TASK_143`, finding 54).

> ⚠⚠⚠ **NOTHING the Rust or Verus rungs do can shrink, weaken or retire this
> row. Whatever they land on IS THE RESULT.** *"Safe Rust's answer is an arena
> that never frees"*, *"it is `p27`'s mechanism"*, *"no cost gradient"*, *"the R5
> cannot state the obligation"*, *"Miri does not see it"* — **all are findings to
> REPORT.** ⚠ **`TASK_093` refused this row on exactly the first of those, and
> its OTHER stated reason (`E0382`/`E0499`) was measured FALSE by its own
> review. Do not re-derive either.**

## What already exists — promote it, do not re-derive it

- `.temp/t143/p28/{body.inc,k.c,matrix.json}` — the admitted demonstration, and
  `.temp/t143/{build.sh,difflines.sh,matrix.py,common/}` that drive it.
- ⚠⚠ **`.temp/mgr146/` — the MANAGER's re-verification, and it CHANGES WHICH
  SPELLING YOU BUILD. Read `.temp/mgr146/NOTES.md` first.** It carries
  `p28d/{body.inc,k.c}` (the spelling to promote), `aslr/k.c` (a negative
  control), `repro.sh`, `ppcount.sh`.

✅ **Keep the include-twice construction** (`body.inc` included with
`SLB_HARDEN` 0 and 1) — it makes the *"R1 and R1h differ by the safety line and
nothing else"* claim mechanical rather than asserted. `p32` ships it.

## ⚠⚠ BUILD `p28d`, NOT `p28` — measured, not argued

`TASK_143` called the 15-line safety line *"the one honest weakness"* of this row
and said it *"shortens to 4 if the hash chain is doubly linked too, which is also
the MORE intrusive spelling"*. **It did not build that.** The manager did:

| | `p28` singly linked chain | `p28d` doubly linked chain |
|---|---|---|
| safety line, preprocessed | `+15 / −0` | **`+9 / −0`** |
| R1 body, preprocessed | 127 lines | **127 lines** |
| all four inputs × both arms | — | **bit-identical checksums** |
| reproducibility, 20 runs | 1 distinct every row | **1 distinct every row** |
| ASan `ctl`/`bug`/`bug`(write) | fires | **fires** |

**The number is 9, not 4** — braces and the `vb` binding the `else bucket[vb]`
branch still needs. ⚠⚠ **But the SHARED cost is ZERO: the three lines `hp` adds
to PUT are exactly cancelled by the three the `prevn` cursor no longer needs in
DEL, so both R1 bodies preprocess to 127 lines.** A 40% shorter safety line,
free, at bit-identical behaviour. **Take it — and re-derive the table above
rather than quoting it.**

## The C mechanism, and why it is not `p27`, `p29` or `p32`

An LRU cache whose objects carry **TWO intrusive link sets**: a doubly linked LRU
list (`lp`/`ln`) and a doubly linked hash chain (`hn`/`hp`). **The object is
ALIASED BY TWO LISTS AT ONCE and MEMBERSHIP IS NOT OWNERSHIP.** `TRIM` reaches
its victim through the **LRU list**, so it holds no hash-chain cursor; R1 frees
the victim without leaving the hash chain.

- **The READ path is CORRECT. The DESTROY path is INCOMPLETE.** That is the
  **inversion** of `p27` and `p29`, which both keep a correct free discipline and
  put the missing check on the read.
- **The dangling pointer lives INSIDE ANOTHER HEAP OBJECT's `hn` field** (or in
  `bucket[]`) — not in a stack table (`p27`), not in a stack local (`p29`), not
  in a program-owned pool (`p32`).
- **There is no `live[]` bit, no slot number and nothing the input can index.**
  The input names an object only by KEY and the program finds it by walking.
  `p27`'s `h < ntab && live[h] == 1` has no analogue **because there is no `h`**.

⚠ **A reviewer will attack this first. State it in `spec.md` and make it
checkable**, not a paragraph of adjectives.

## ⚠⚠⚠ A COMMITTED SENTENCE ABOUT THIS ROW IS OVERSTATED. Settle it as deliverable 0.

`.memory/06-catalogue.md`'s `p28` cell and `TASK_143_REPORT.md` §2.2 both say:

> ~~its R1 is reproducible **"so it is GATABLE against `model.py` on its
> adversarial inputs where `p27` and `p29` are NOT"`**~~

**The REPRODUCIBILITY half is confirmed** (manager-re-run, 1 distinct value in
20 runs on every row, **with a negative control that gives 20 distinct values**,
so the test is not blind). ⚠ **The CONSEQUENCE half looks wrong to the manager
and the manager may be wrong — measure it and say so either way:**

- `check.py`'s `inputs_of` splits on the `adversarial-` prefix; **stage 2**
  requires agreement on **non-adversarial** cells only. An adversarial input is
  one on which R1 and R1h **must** disagree, so it could never join the agreement
  set however reproducible it is.
- **Stage 4** *records* per-rung adversarial behaviour and computes `diverges`
  against the model's `expected_exit`/`expected_stdout`. **It records; it does
  not require agreement.**

✅ **What the manager believes it actually buys, and it is still new:** the
**recorded** adversarial row and any **control** checksum are **stable across
runs, so they can be pinned to an exact number.** `p29` cannot — its
`controls/repro.json` publishes an invariant and no pinned count because the
use-after-**free** half is not reproducible. **`p28` would be the first temporal
row whose adversarial evidence carries a pinned figure.** ⚠ And note the split
*within* `p28`: `adv-uaf-read` is a stable wrong **value**, `adv-uaf-write` is a
stable **SIGSEGV** — only the first can carry a checksum pin.

**⚠ I think this; prove me wrong.** If stage 2 or stage 4 can in fact gate an
adversarial cell against `model.py`, say so with the run and I will correct the
catalogue in the other direction.

## Deliverables

0. **The overstated sentence above, settled with a run.** First, because it
   decides what `controls/` can pin.
1. **Build `patterns/p28-...`** to `patterns/p01-array-sum/`'s structure and
   `p32-free-list-pool/`'s recent example: seven rungs, `spec.md` with the
   machine-readable `slb-contract` pins, `model.py`, `inputs/gen.py`,
   `NOTES.md`, `README.md`, `controls/`.
   **`harness/check.py p28` must PASS and `measure.py` must record it.**
2. ⚠⚠⚠ **`model.py` MUST BE WRITTEN FROM THE CONTRACT, NOT TRANSLITERATED.**
   `TASK_136`'s was a line-by-line copy of its own kernel — same variable names,
   same guard — which satisfies the model-sandbox rule mechanically and defeats
   it in substance, and is exactly how its delete bug went undetected.
   ✅ **`p29`'s model is the good example (a reachability walk). Say in
   `NOTES.md` how yours differs structurally** — the obvious independent
   formulation here is a **dict cache with an explicit recency order**, carrying
   no links at all.

   ⚠⚠⚠ **AND THERE IS A SECOND `model.py` FAILURE MODE, FOUND ON `p32` ONE TASK
   AGO (`TASK_145` M1), THAT INDEPENDENCE DOES NOT PROTECT YOU FROM: A CHECK
   THAT IS A TAUTOLOGY OF THE MODEL'S OWN REPRESENTATION.** `p32`'s `model.py`
   claimed — in six places, two inside `contract_sha256` — to **DERIVE** its
   `sanitizer_expect` by computing *"every index the buggy rung would compute"*.
   Its guard was `0 <= s < SLOTS` over a slot drawn from a successor map over
   `0..SLOTS-1`: **structurally incapable of firing. 0 firings in 20 000 fuzzed
   buggy windows**, and the one input that would have tripped it **crashed the
   model** before the field was read. The conclusion was true and the evidence
   claim was false.
   ⚠⚠ **So: whatever your `model.py` DERIVES rather than declares, SHOW IT
   FIRING.** A derived `sanitizer_expect` owes an input or a planted mutation on
   which it returns `"fires"`. **If it cannot fire, declare it and say so** —
   declaring is honest, a derivation that cannot fire is not.
   ⚠ **`p28` is more exposed to this than `p32` was**, because its whole harm is
   a pointer left in another object's `hn` field, which a Python dict model does
   not have. **Decide early whether your model can represent the stale link at
   all, and write the answer down rather than discovering it at gate time.**
3. **The R5 owes an ATTACK ARM THAT MUST FAIL TO VERIFY, plus a VACUITY arm.**
   ⚠⚠ **You have a ready-made one from `TASK_091`: delete the ADDRESS
   INJECTIVITY conjunct and `fake3` passes — ONE node with `prev = next =
   itself`, declared `len = 3`, `ptrs@ = [p,p,p]`, discharging `unlink`'s ENTIRE
   precondition.** ⚠ **`p42`'s ghost ledger verified `18/0` while leaking and
   `TASK_136`'s ARM_C was discharged by `fn arm_c() -> u8 { 9 }`. Both are in
   this project's history; do not repeat them.**
4. ⚠ **If you publish any rung-to-rung cost difference, search BOTH rungs'
   spellings and count the levers on each side.** ⚠⚠ **This row has already
   produced a near miss of exactly that kind, caught before a build:** a `p28`
   with R3 = safe arena and R4 = raw-pointer DLL would have published *"safe Rust
   is 6.02× CHEAPER than unsafe"* with **108.4% of the gap in the ALLOCATOR**,
   the bounds check being 3.0% of the magnitude **and the opposite sign**.
   ⚠ **And 4.0 of the 12.5 R3→R4b gap is INDEX SCALING, not checking**, so an R3
   that is a safe index arena misattributes it. **A row may ship with NO cost
   axis — `p29` does — but say so explicitly so the absence does not read as a
   zero.**
5. **Tell the manager the bug class** for `harness/tools/composition.py`.
   ⚠ **Do not edit that file.** Expect `--check` to FAIL with
   `built but unclassified` until the manager classifies it — **that is the
   check working, not a defect.** ⚠ Note `p28`'s harm has an **aliasing** limb
   (two lists naming one object) as well as a temporal one; `p32`'s cell already
   carries a caveat of that shape — propose the wording, do not apply it.

## Verus groundwork that exists — ⚠ INFORMATION, NOT A CRITERION, and PROVISIONAL

`.tasks/TASK_091_REPORT.md` (**UNREVIEWED**) and `.temp/t91/`:

- ✅ `wf` **PRESERVED** by `unlink` (`4/0`) and **ESTABLISHABLE** (`8/0`, first
  attempt) — `new()` → `push_front`×3 → `unlink` on the **MIDDLE** node, three
  `requires` discharged from `push_front`'s postcondition alone. **Zero TCB.**
- ⚠⚠ **THE TRAP THAT WOULD BURN A SESSION: `is_disjoint` takes `&mut self`, so
  it CANNOT be called inside `assert forall|i| … by`.** Not a hint problem, a
  goal-reformulation problem. The fix was one extra `wf` conjunct (key
  discipline, `m.dom().contains(a) ==> m[a].ptr().addr() == a`), which
  **STRENGTHENS `wf` and made `unlink` HARDER**.
- ⚠ **`Dll` needs EXEC fields (`head`, `len`) it had only in ghost — a CONTRACT
  change. Budget it in `spec.md`.**
- ✅ **The whole-struct read-modify-write Verus forces is FREE** — `raw_ptr` has
  no field-level mutator, so R5 rewrites the whole 24-byte `Node` at **1.00 `Ir`
  per CALL out of 50 232**. So R5 needs no local `external_body` field-store
  wrapper to stay identical to R4.
- ⚠⚠ **THE REAL OPEN RISK, and it is not `unlink`: there is NO `deallocate`.**
  The probe drops `Tracked<Dealloc>` and **leaks**; a shipped `p28` must thread
  it like `p27`'s. **Untested.** ⚠⚠ **AND `TASK_091` PROVED ONE LIST. `p28` HAS
  TWO LINK SETS AND THE BUG IS IN THEIR INTERACTION** — the groundwork does not
  cover the aliasing, and that gap is a RESULT to report, never a reason to
  shrink the row.

## Rules

- `.temp/t146/` for scratch. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`.** No `git add`/`git commit`.
- ⚠ **Do not touch `.temp/t136/ t137/ t139/ t140/ t141/ t142/ t143/ t144/ t145/
  t91/ mgr146/`** — all cited evidence. **Copy from them; do not modify them.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`. ⚠ Grep
  `~/tools/verus/vstd/std_specs/` **specifically** before any "no spec exists" —
  a `vstd/<mod>.rs` trait declaration is NOT the specification, and that exact
  confusion has produced a false claim twice.
- Hand-run sanitisers need `env -u LD_PRELOAD`; **never truncate a sanitiser log
  with `head`**; **every harm probe owes a positive control that must fire.**
  ⚠ **`TASK_143` had clang ELIMINATE one of its positive controls** — a
  malloc-elision artefact `p31` also hit. **Check your controls actually run.**
- ⚠ **Read `blocked` out of the RECORD, never `grep` the log.** Expect
  `p01 = 1`, `p42 = 1`; `p42` may legitimately be 2 (environment-selected Miri
  slowdown) and that is not a regression.
- ⚠⚠ **If the gate fails on `[tables]`, run `harness/report.py pNN` and
  re-gate.** Stage 9c was repaired at `TASK_141` but the ordering still matters.
- ⚠ **Generate control JSONs AFTER the sources are final** — `TASK_139` edited
  doc comments after generating them and paid a re-measure. **`c/*` and `*.rs`
  are MEASUREMENT-HASHED; a comment-only edit stales the record.**
- Keep the generator, delete the artefact (`.memory/00-environment.md`
  constraint 6).
- Report to `.tasks/TASK_146_REPORT.md`. **PROTOCOL rule 2: the count is in
  `TASK_145_REPORT.md`'s closing paragraph if it exists, else
  `TASK_144_REPORT.md`'s — read it there, do not guess.**
