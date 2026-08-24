# TASK_084 — finish "Owed" 0: the three trusted forms the gate still cannot see, the flat directory walk, and the published column

**Role: research engineer.** Read `.tasks/PROTOCOL.md` first, then this file,
then `.memory/05-layout.md` (the `vparse.parse()` section) and
`.memory/04-verus.md`. Scratch goes in `.temp/t84/` — that directory is free,
I checked. ⚠ `.temp/p84` and `.temp/r84` are also free; **`.temp/pNN` in this
tree is ambiguous between pattern NN and task NN, so use `t84`.**

---

## 0. Why this task exists, in one paragraph

`TASK_082` added a gate stage that counts body-less trusted declarations
(`assume_specification`, `broadcast axiom fn`, `uninterp spec fn`). It works,
and its acceptance test was good. **`TASK_083_REVIEW` then found that it closed
one of at least four routes**, and that the manager's own verification of it —
*"`results/synthesis.md` regenerates byte-identical, therefore no published
number moved"* — **passed for the wrong reason**: the published column reads
`tcb_items`, and the word *"axiom"* appears **zero times** in `synthesis/`. The
check could not have failed. That is the shape of mistake this task must not
repeat, so §6 below is written as a set of limbs each of which has a stated way
to fail.

**Everything in §1 is manager-verified — I ran each command below before writing
this file.** Do not take that as licence to skip re-running them; take it as
meaning that if your run disagrees with mine, **your run is the evidence and you
should say so loudly.**

---

## 1. The four routes, with the command that shows each one open

### B1 — `#[verifier::external_trait_specification]`

```
$ grep -rho 'external_trait_specification' ~/tools/verus/vstd/ | wc -l
54
$ grep -c 'external_trait_specification\|external_fn_specification' harness/*.py
asm.py:0  fixture.py:0  build.py:0  limbs.py:0  measure.py:0
report.py:0  dloop.py:0  vparse.py:0  check.py:0
```

54 uses in the **pinned** vstd, zero mentions in any of the nine harness
modules. The attribute sits on a **`trait` or `struct`**, not on a `fn`, so
`vparse.parse()` — which keys on `fn NAME` with a body — never produces an item
that could carry `.external`, and the trait's method declarations are body-less
and dropped. TASK_083_REVIEW's probe: Verus proves `r == 0`, the compiled
program prints **7**, `axiom_decls` returns `[]`, the TCB inventory is empty,
and 5c-twin shouts *"no trusted item"*. Its evidence is in `.temp/r83/a1/`;
**re-run it rather than trusting the summary.**

⚠ **And Verus PRINTS the `external_type_specification` line for you to paste** —
the identical accident vector as the original item. This clears rule 5's *"could
this happen by accident?"* test on evidence, not on an argument.

### B2 — `#[verifier::external_fn_specification]`

`harness/vparse.py:477` is `re.search(r"\bverifier::external\b", a)`. The next
character in `verifier::external_fn_specification` is `_`, which is a word
character, so **there is no word boundary and the regex does not match** — and
the same is true of `external_trait_specification`. The item therefore has
`.external is None` and, in `verus.items`, is **indistinguishable from an
ordinary verified function**.

⚠ **B2 is a different shape from B1 and must not be fixed the same way.** An
`external_fn_specification` function *has a body* (it calls the function it is
specifying), so `parse()` **does** see it — the defect is purely that the
attribute is not recognised. B1's item is not seen at all. **Confirm this
distinction yourself before writing either fix**; if I have it backwards, say
so, that is exactly the kind of correction this project runs on.

### B3 — an axiom in a `#[path]`-included subdirectory

`harness/check.py:3615` is `for f in sorted(os.listdir(pdir))`, and
**`os.listdir` is flat**. The axiom scan at `check.py:3759` runs only over
`verus.obligations`. Meanwhile `_path_includes(pdir, srcs)` at `check.py:3275`
already exists and `_scan_unsafe_sites` already uses it (`check.py:3364`) for
exactly this threat.

⚠⚠ **This vector is live in all 22 patterns**: every `verus.rs` `#[path]`-
includes `common/driver.rs`, so `common/` is inside every pattern's token
stream. Nothing there declares an axiom today — which is why the fix should be
**inert on the current tree**, and if it is not, that is a finding and you
should stop and report it rather than editing 22 `spec.md` files.

### B4 — the published column cannot see any of it

```
$ grep -rc 'axiom' synthesis/*.py results/synthesis.md
synthesis/outward_ir.py:0  synthesis/licence.py:0
synthesis/synthesize.py:0  results/synthesis.md:0
$ grep -n 'tcb_items' synthesis/synthesize.py
854:        items = vb.get("tcb_items") or []
```

✅ **Good news that changes the cost of this limb:** `axiom_decls` is **already
in every gate record** (`check.py:3775` per Verus source and `check.py:6439` in
the Miri block). So the published-column fix is a **`synthesize.py`-only**
change and does not, by itself, stale anything.

---

## 2. The fifth route, which I found while writing this file — verify it before you fix it

`synthesis/synthesize.py:853` reads

```python
vb = (g.get("verus") or {}).get("verus.rs") or {}
```

— a hardcoded single key with no comment. **p01 pins two Verus sources**, and
the published table silently drops one of them:

```
$ python3 -c "import json; d=json.load(open('results/gate/p01-array-sum.json'));
  [print(k, v.get('verified'), [i['name'] for i in v['tcb_items']]) for k,v in d['verus'].items()]"
safe_naive_verus.rs 7 ['load_input', 'emit']
verus.rs            7 ['get_unchecked', 'load_input', 'emit']
```

p01 is the **only** pattern with two (I checked all 22). So the published row for
p01 reports 7 obligations / 3 TCB items / 6 TCB lines and omits a second
verified source with 7 more obligations, 2 more items and 5 more lines.

⚠ **This is NOT obviously a bug, and I am not asking you to sum them.**
`safe_naive_verus.rs` proves the **R2 rung** panic-free (finding 2: *"a proof
alone buys nothing"*); its TCB is not R5's TCB, and adding them would publish a
number that describes no rung. **The defect I am confident about is that the
choice is silent** — there is no comment, no disclosure in the table's prose,
and no gate check that would notice if a second pattern grew a second source
tomorrow.

⚠ **There is direct precedent one paragraph above the offending line.** The same
file already documents that *"p01 ships **two** `-O3` identity pairs and an
earlier version of this file took whichever came first (TASK_075\_REVIEW m6)"*,
and fixed it by pinning `R5_PAIR`. **p01's two-ness has bitten this file once
already, on a different column, and the Verus-source case was never audited.**

**Your call, and I want your reasoning:** disclose-and-pin (a comment plus an
explicit constant, mirroring `R5_PAIR`), or something better. **If you conclude
the current behaviour is correct and only needs a comment, say that** — that is
a legitimate outcome and cheaper than the alternatives.

---

## 3. What to build

**D1 — B1.** `vparse.axiom_decls()` sees `#[verifier::external_trait_specification]`
and the body-less trusted method declarations it introduces.

**D2 — B2.** The attribute matcher recognises `external_fn_specification` (and
`external_trait_specification`) so the item is classified trusted rather than
verified.

**D3 — B3.** The axiom scan follows `#[path]` includes, reusing
`_path_includes`. Pick and **document** a key convention for declaring an axiom
that lives outside `pdir` (the `verus.axioms` key is currently keyed by the
`verus.obligations` source name).

**D4 — B4.** The published TCB column sees axioms. See §5 for the design
question I am least sure about.

**D5 — the fifth route.** Whatever §2 concludes, plus the comment that was
missing.

**D6 — p17 `NOTES.md` §10b.** It is PROVISIONAL and rule 9 has kept it out of
`.memory/`; its review has now landed and found the **mechanism wrong** and the
**rate band-specific**. Replace it with TASK_083_REVIEW's law:

```
R3ship − R4  =  11 + 7·nsuf − 2 · #{ i < nsuf : s_i ≡ 0 (mod 4) }
```

Zero free parameters, exact on **49 measured points**, and it predicts both
shipped inputs at **+32**. The sawtooth is the **inner byte fold keyed on served
length**, *not* a 4×-unrolled table walk — neither rung's table walk is unrolled
at all, and `inputs/gen.py`'s own `SWEEP_NSUFS` comment already said so. ⚠ **Do
not carry `6.50 per request` forward**: it is the mean of a band that samples
each residue once per four, both shipped inputs pay **7.00**, and quoting 6.50
makes a 20-range extrapolation **11 low**. Full derivation, disassembly and the
four step-bands: `.tasks/TASK_083_REVIEW_REPORT.md` A2, majors 6 and 7.

**D7 — `patterns/p01-array-sum/spec.md:82`.** It says structural identity is
*"recorded as a result"*, and `check.py:2943` and `check.py:67-72` say a drop
below the pinned level calls `rep.fail` and the verdict is **FAIL**. p01's spec
states the opposite of what the gate does. It is the only `patterns/*/spec.md`
carrying the phrase. ⚠ **This is inside the hashed block, so it moves p01's
`contract_sha256`** — which is why it was queued for a task that re-gates
anyway. **Follow PROTOCOL "definition of done" rule 6: record the before and
after hashes in `NOTES.md` and say in one line that the edit is a prose
correction with no `required`/`forbidden` entry moved.**

**D8 — re-gate and re-publish.** Full 22-pattern `harness/check.py` sweep and
`synthesis/synthesize.py` regeneration. ⚠ **Budget ~45 min for the sweep** —
measured at 2593 s and 2672 s on the last two runs, *not* the 13 min an older
note claimed. Use `timeout`. Keep notes in `.temp/t84/NOTES.md` **as you go**,
because agents on this project die to transient API errors and the ones that
kept incremental notes lost nothing.

---

## 4. The trap that this exact item already sprang once — do not spring it again

⚠⚠ **DO NOT "SIMPLIFY" ANY OF THIS BY WIDENING `vparse.parse()` TO KEEP
BODY-LESS ITEMS.** That is what "Owed" 0 originally implied, the manager wrote
it into `TASK_082` as the prescribed repair, and **it turns p36 red in six
stages**: a **trait method declaration is body-less**, p36 declares `fn apply` /
`spec fn spec_apply` in a trait and defines them in the impl, so keeping
body-less items makes `by_name` raise `duplicate item name(s)`. **And
`assume_specification` has no `fn` token at all**, so the widening would have
paid p36's price *and still missed the target*. `axiom_decls` is a **separate
keyword-keyed matcher** for this reason. Full write-up in `.memory/05-layout.md`.

⚠ **B1 makes this trap sharper, not weaker.** An `external_trait_specification`
trait's methods are *exactly* the body-less declarations p36 also has. **Your
B1 matcher must distinguish "body-less method inside a trait carrying the
external-trait attribute" from "body-less method inside an ordinary trait", and
p36 is the live negative control.** If you cannot separate them, **stop and
report that** rather than shipping something that turns p36 red — a refused
deliverable with a measurement behind it is a good outcome here.

---

## 5. The call I am least sure of — attack this one first

**How the published column should represent an axiom.** Two candidates:

- **(a) fold** axioms into `tcb_items`, so `TCB items` rises and `TCB lines`
  gains 0;
- **(b) break out** a separate `axioms` column beside `TCB items`.

**I lean (b), and my reason is that (a) equates two unlike things:** a 7-line
`external_body` wrapper whose `ensures` a reviewer has read against real Rust
semantics, and a zero-line hand-written axiom that is **strictly stronger** and
whose printed-by-Verus form carries no `requires` and no `ensures` at all
(`.memory/04-verus.md` — that form verifies a 1 MiB out-of-bounds read and a
null dereference at `4 verified, 0 errors`). A single count would let one be
traded for the other at par.

⚠ **But I have not measured anything here and the counter-argument is real:** a
column that reads `0` in all 22 rows is column real-estate spent on a hypothetical,
and the TCB *total* — the number a reader actually quotes — would still be an
undercount under (b) unless the prose says so.

**Tell me which, and why, with the regenerated table in front of you.** ⚠ **And
whichever you pick, the acceptance test must include a run where the number
MOVES** — see §6 limb 3. Every agent that has contradicted me with a measurement
has been right; this is the call to do it on.

---

## 6. Acceptance — every limb states how it could fail

The manager's last self-check was a tautology. **Each limb below names the
failure it is capable of detecting; if you add a limb, add its failure mode
too.**

1. **22 verdicts unchanged.** Expect **21 `PASS` + 1
   `PASS-WITH-BLOCKED-ROWS` (p01, the Miri timeout), 0 failures.**
   *Fails if:* any fix is over-broad and refuses a legal construct — this is the
   limb p36 would trip.
2. **The current tree is inert.** TCB total **92 → 92**, `axiom_decls` empty in
   all 22, and `common/driver.rs` contributes nothing.
   *Fails if:* the `#[path]` walk finds an axiom in shared code, which would be
   a genuine finding — report it, do not paper over it.
3. ⚠⚠ **THE LIMB THAT MUST BE ABLE TO FAIL — four planted axioms, one per
   route, each caught, and the published column MOVES.** Under `.temp/t84/`,
   build four throwaway copies of a real pattern's `verus.rs`, one per route:
   B1 an `external_trait_specification`; B2 an `external_fn_specification`; B3
   an axiom in a `#[path]`-included subdir; B4 anything, checked at
   `results/synthesis.md` rather than at the gate. For **each**, record: Verus's
   own `N verified, 0 errors`, what the gate said **before** the fix, what it
   says **after**, and **the diff of the regenerated `synthesis.md` row**.
   *Fails if:* the fix is cosmetic. **A byte-identical `synthesis.md` under a
   planted axiom is exactly the failure this limb exists to catch** — it is the
   result the manager got and misread. Do not delete the plants; commit the
   generators under `.temp/t84/` per `CLAUDE.md` "Don't" 1, delete the binaries.
4. **p01's `contract_sha256` moves and nothing else's does.** D7 is the only
   contract edit in this task.
   *Fails if:* a `spec.md` was touched incidentally — `git status --porcelain
   patterns/` is the check.
5. **`harness/measure.py --check-stale` after the sweep.** ⚠ **Expect
   `0 STALE`.** `check.py` and `vparse.py` are gate-hashed, `build.py` and
   `asm.py` are **measurement**-hashed and you are not touching them.
   *Fails if:* you touched a measurement-hashed file, which costs a full
   43-minute re-measure of 17 records and churns published timing prose. **If
   `--check-stale` reports anything, stop and report — do not re-measure.**

---

## 7. Constraints

- `.memory/` is **manager-only**. Put durable facts in your report; I land them.
- **No `git add` / `git commit`.** Read-only git is fine and you will need
  `git show HEAD:` for D7.
- Scratch under `.temp/t84/` only. **No `/tmp`.** Keep the generator, delete the
  artefact.
- **Do not edit `pilot/`.**
- Do not widen scope. If you see adjacent work — and you will, this is the
  harness — **report it, do not do it.**
- `timeout <N> <cmd>` on every long run. Never `pkill`/`killall`.

---

⚠ **PROTOCOL rule 2's running count is 235** (unchanged since TASK_083; this
file adds no new agent contradictions yet). **Every agent that has contradicted
the manager with a measurement has been right — 235 times.** §5 is where I am
least sure and §2 is a route I found myself and have not had attacked; §1's B2
paragraph makes a structural claim about `external_fn_specification` having a
body that I reasoned out rather than ran. **Prove me wrong on any of the three
and say so in your report.** Carry **235** forward, incremented by whatever you
find.
