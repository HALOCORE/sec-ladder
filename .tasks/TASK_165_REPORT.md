# TASK_165 — review of `TASK_164`: the DEVIATION's REASON 1 is TRUE and does not
# settle the question it was asked; entry 23 is now wrong a FIFTH time

**Role: research reviewer. I edited nothing.** No `git add`, no `git commit`, no
`.memory/`, no `RECAP.md`, no `harness/`. `git status --short` is empty. Scratch
is `.temp/t165/` only; `.temp/t164/`'s four Verus probes were **copied out**
(`globalprobe/re_*.rs`) before being re-run, and nothing under `.temp/t164/` or
`.temp/mgr164/` was written to.

**Per-item verdicts**

| item | verdict |
|---|---|
| 1. the `global` DEVIATION | **SURVIVES, NARROWED** — REASON 1's *empirical* half is true and is **stronger than TASK_164 measured** (7 routes, incl. `align`, generics, aliases, `#[path]` modules). Its *inferential* half does not reach the `verus.axioms` count. **Major 1.** |
| 2. stage 9b's verdict read | **SURVIVES** on shape. Every candidate the manager could not rule out behaves; a truncated sidecar FAILS. ⚠ But *"four bespoke shapes"* is **7 files / ≥8 spellings** — **Major 3.** |
| 3. item C's docstring | **SURVIVES.** Every tree-wide count re-derives **exactly**; the shipped nine is the DERIVED list, not the asserted one. ⚠ Length — **Minor 2.** |
| 4. item D's twin | **SURVIVES, STRENGTHENED.** All three arms fire on **both** twins; the bulk twin is as strong an oracle, not merely shorter, and the 12→11 is mechanical. |
| 5. what the manager overstated | **FALLS. Major 2** (entry 23, fifth error, marked ✅ manager-re-derived) and **Minor 1** (`TASK_165.md`'s own `summary: null` claim). |
| 6. the process disclosures | **SURVIVE**, all four, re-derived against `git`, not against the engineer's snapshot. |

---

## Did

- Attacked the deviation's REASON 1 with **8 new Verus probes** it did not try
  (`.temp/t165/globalprobe/`, generators kept), plus a re-derivation of
  TASK_164's four from copies.
- Attacked `control_json_verdict` with **28 document shapes** and drove stage 9b
  itself over a truncated file, a valid-but-partial file and a bespoke-verdict
  file (`.temp/t165/verdict_attack.py`).
- Re-derived every tree-wide figure in `check_marginal_ir`'s new docstring
  **independently** of `.temp/t164/r45_null.py` (`.temp/t165/r45_null_check.py`).
- Re-ran the twin oracle with **three** weakening attacks × **both** twins
  (`.temp/t165/twinprobe/`), not the one arm the report ran.
- Re-ran both `.memory/05-layout.md` harness-pin recipes, the 30-of-30 generator
  premise, and the p35 sidecar leaf diff **against `git show fb7cdb0^:`**.
- Read `.temp/mgr164/` and checked four of its load-bearing claims.

**No sweep was run and none is needed.** Every arm above is a pure function, a
`_selftest()` cell, or a single-file `./verus_run.py` run.

---

## Problems

### MAJOR 1 — the deviation: REASON 1 is TRUE, and it answers a **soundness** question the `verus.axioms` count is not asking. `results/synthesis.md` publishes **"0 axioms"** on 10 rows that carry one.

`harness/check.py:4586-4588`, `harness/vparse.py:679` (`GLOBAL_KINDS`),
`results/synthesis.md:615`.

**First, the empirical half, which I could not break and which is stronger than
the report claims.** TASK_164 tried three routes; I tried seven more. `E0080`
fires on every one, verify-only, `./verus_run.py <file>` with **no `--compile`**
(confirmed by reading `verus_run.py::main` — single-file mode forwards the file
and nothing else):

```
rc=1 align_false           2 verified, 0 errors  error[E0080]: does not have the expected ALIGNMENT
rc=0 align_true            2 verified, 0 errors
rc=1 generic_false         2 verified, 0 errors  error[E0080]  (global layout W<u8>, a generic instantiation)
rc=1 alias_false           2 verified, 0 errors  error[E0080]  (global size_of A, where `type A = u8`)
rc=1 ghostonly_false       2 verified, 0 errors  error[E0080]  (the lie used ONLY in a proof fn)
rc=1 mod_host2             1 verified, 0 errors  error[E0080]  <- the lie in a #[path]-INCLUDED module
rc=1 re_layout_false       2 verified, 0 errors  error[E0080]  (TASK_164's, re-derived)
rc=1 re_sizeof_false       2 verified, 0 errors  error[E0080]  (TASK_164's, re-derived)
rc=1 re_layout_false_unused  1 verified, 0 errors  error[E0080]  (never-constructed)
rc=1 re_layout_false_lib     1 verified, 0 errors  error[E0080]  (--crate-type=lib)
rc=1 outside_verus         error: expected one of `!` or `::`, found `layout`
```

Three of these matter:

* ⚠ **`align` was never measured by TASK_164** — its diagnostic quotes *"does
  not have the expected **size**"* only, and both halves of `global layout` are
  hand-written. rustc checks the alignment too, with its own message. **The
  report's argument was one conjunct short and the missing conjunct holds.**
* ⚠⚠ **The `#[path]`-included module is the vector with blast radius 33** —
  every pattern's `verus.rs` `#[path]`-includes `common/driver.rs`, and
  `_check_axiom_decls` explicitly walks those files (`check.py:5197`). A false
  `global` there still fires `E0080`, at `mod_lie.rs:3`, with `1 verified, 0
  errors` printed first. **Nobody had tested this and it is the one that would
  have mattered.**
* **`global` outside `verus!` is a syntax error**, so `in_verus: False` cannot
  occur in a file that compiles.

**The `--cfg` attack does not land, for a reason worth recording.** `global
layout` **refuses a type declared outside the `verus!` macro** (`error: cannot
use type cfg_false::S which is ignored because it is either declared outside the
verus! macro`), so the cfg'd-field shape is not expressible. Respelled with the
declaration itself under `#[cfg]`, the twin run reports `1 verified, **1
errors**` — **Verus itself** rejects it, because the function's own `ensures`
stops following from the changed axiom. Either way there is no configuration the
gate verifies that `build.py` compiles differently.

**And the stage-5e joint holds, by name.** `_verus` (`check.py:5341`) records the
anomaly whenever *the summary parsed and `errors == 0` and `rc != 0`*; every
probe above satisfies it. The certificate site is `check.py:5125`, inside
`check_verus_contract`'s loop over **every** pinned `verus.obligations` source,
and `check_verus_exit_codes(rep)` is called **unconditionally** at
`check.py:9597`. Checked against every flag: `--no-build` skips only
`build.py::build_verus` (the *second* net); `--no-verus-mutants` skips 5c/5c-req/
5c-twin and *"the run then FAILS, by design"*; `--skip` takes **input stems**, not
stages; `--cells` selects cells. **No flag reaches a PASS with the primary
`_verus` skipped.** Blocked rows do not touch it either — all five `blocked`
entries in the tree are `section: "miri"` (p01, p42) or `section: "twin"` (p35),
never the verification. When a `global` lie coexists with a real verification
error the anomaly condition is false — measured (`mod_host`, `cfg2_twin`: `1
verified, 1 errors`) — **and the run fails for the other reason, which is the
right outcome.**

**⚠⚠ NOW THE HALF THAT DOES NOT SURVIVE.** REASON 1 concludes: *"putting them in
a list captioned 'axioms that NOTHING checks' would be false."* That caption is
real — it is the **`tcb-axiom` SHOUT** at `check.py:4631` — and for the shout the
argument is **correct**. But `_check_axiom_decls` partitions `global` out of
**three** things, and the argument only covers one. The **declared-count**
comparison's own caption is a different sentence (`check.py:4616-4620`):

> *"An `assume_specification` / `axiom fn` / `uninterp spec fn` is an AXIOM about
> real Rust semantics: **Verus does not prove it**, it adds **NO verified
> function** so the obligation count does not move, it **emits no instructions**
> so the `identity` pin does not move, and it carries **no
> `#[verifier::external_body]`** so the TCB tally above does not move either."*

**Every one of those four clauses is true of a `global` directive, verbatim.**
Verus does not prove it — the Verus guide says so in terms: *"the `global`
directive **exports the axioms** `size_of::<T>() == n` and `align_of::<T> == m`
for use in Verus proofs"* — and for `usize` it does strictly more, **narrowing
the SMT integer range** (`usize::MAX`), which is proof power far beyond a size
fact. rustc's `E0080` makes the **program** sound; it does not make the
**declaration** proved, and it does not make it visible.

**The measurable consequence, and it is published.** `results/synthesis.md:615`:

```
**Trusted base, all 33 rows: 152 items (333 lines) and 0 axioms.**
   Quote both numbers; there is no single one.
```

and every one of the 33 rows prints `0` in the `axioms` column — including
`p10 p19 p22 p28 p29 p34 p36 p38 p46 p47`, the 10 the gate now records a `global`
on. Section 3's own prose (`synthesize.py:1519`) says a `0` means *"**this
pattern's author wrote none of their own**"*. **Ten authors wrote one of their
own.** `CLAUDE.md`'s first paragraph lists **trusted-base size** as one of the
five axes this benchmark compares, so this is not a hygiene point: it is a
published figure on a measured axis that is understated on 30% of the tree.

⚠ The report's own defence of the partition is *"folding `global` into that key
would have moved a published column and changed what it says."* **That is the
argument for moving it, stated as the argument against.** A published column that
has stopped saying what its prose says is exactly what should move.

**RECOMMENDATION — reverse it, but not the expensive way.** Three options, priced:

| | what | cost | moves `contract_sha256`? |
|---|---|---|---|
| **A** | count `global` in `verus.axioms`, so 10 patterns must DECLARE | 10 `contract_sha256` moves, 10 stale `results/tables/*.md`, 10 `report.py`, **a second full sweep** | yes |
| **B** ✅ | leave the gate alone; make the **publication** honest — `synthesize.py` already has `global_decls` in every gate record, so add the column/total and rewrite the *"0 axioms"* sentence | **`synthesize.py` edit + one `python3 synthesis/synthesize.py`. NO gate run, NO re-measure** | **no** |
| **C** | both | A's cost | yes |

**B is nearly free and it is verified free:** `main`'s `srcs` list
(`check.py:9666-9677`) globs `harness/*.py`, `common/*.py`, `common/layout/*.py`
and `verus_run.py` — **`synthesis/*.py` is in none of them** — and
`measure.py --check-stale` globs `results/*.json` and `results/gate/p*.json`
only, so `results/synthesis.md` has no staleness gate either. **Take B now.** If
the manager also wants A, ⚠ **it can ride the Results task's sweep** — but only
if the Results task is going to re-gate anyway, and `.temp/mgr164/` does not say
it will. **Do not spend a sweep on A alone.**

### MAJOR 2 — `.memory/03-measurement.md` entry 23 is now wrong a **FIFTH** time, in the commit whose message announces the fourth — and RECAP finding 63 marks the wrong sentence **✅ manager-re-derived**

`.memory/03-measurement.md`, the paragraph added by `8273bfd`:

> ⚠⚠ **THE INPUT AXIS IS NOT COSMETIC — ON THREE OF THE FIVE ROWS ONE INPUT IS
> EXACTLY `0.00`.** *"`p25`'s and `p42`'s `small.bin` nulls are `0.00` in **all
> four** cells"*

**`p42`'s `small.bin` null is `−2.00` at `-O3 whole`.** Re-derived from
`results/gate/p42-goto-cleanup.json`:

```
p42 O0/isolated/small.bin  unsafe=7052.0   verus=7052.0    null=0.0
p42 O0/whole/small.bin     unsafe=7052.0   verus=7052.0    null=0.0
p42 O3/isolated/small.bin  unsafe=1407.0   verus=1407.0    null=0.0
p42 O3/whole/small.bin     unsafe=1444.0   verus=1442.0    null=-2.0   <-- NOT 0.00
```

⚠⚠ **And the four-axis table printed EIGHT LINES ABOVE that sentence, in the same
entry, already prints `-2.00` in that cell.** This is PROTOCOL rule 13's
header-rots-away-from-body shape, at one-paragraph distance, in the authoritative
layer.

**It propagated through three artefacts:**

1. `.tasks/TASK_164_REPORT.md` §4's table — *"| `p42` `31.00` | `large.bin` |
   `small.bin` is **`0.00`** in all four |"* (the engineer's original error);
2. `.memory/03-measurement.md` entry 23 (landed by the manager);
3. commit `8273bfd`'s message — *"p25 and p42 are 0.00 on small in all four
   cells"*;
4. **`RECAP.md` finding 63(c), where the clause sits under a `✅
   **Manager-re-derived.**` marker.**

⚠⚠⚠ **Item 5 asked me to check that the ✅/⊘ separation is honest. This is the
place it is not.** The manager re-derived the *table* (I confirm: all 40 cells
reproduce exactly) and **copied the engineer's prose** — which is rule 9's
original cause, and it landed inside a `✅` claiming the opposite. The 8/35/23
and 10-of-66 and 37/15-of-66 distributions in the same paragraph **all reproduce
exactly** (below); it is only this sentence.

⚠ Second, smaller: *"three of the five rows have `0.00` on the other input"* is
loose. Counting `small.bin` cells that are exactly `0.00`: p25 4/4, p42 **3**/4,
p11 2/4, p28 1/4, p29 1/4. Every row has at least one.

**Fix:** *"`p25`'s `small.bin` null is `0.00` in all four cells and `p42`'s in
three of four (`-2.00` at `-O3 whole`)."*

### MAJOR 3 — *"four bespoke verdict shapes"* is **7 sidecars and ≥8 spellings**, and the proposed generator-side repair covers **2 of 7**

`RECAP.md` finding 63(a) (marked ⊘, correctly) and `TASK_164_REPORT.md` §1
name four: `arms_as_designed`, `cells_ok`, `hardened_kernel_broke`,
`unstable_cells`. Re-derived over all 46 tracked sidecars
(`.temp/t165/sidecar_audit.py`), the 11 `NO-VERDICT` files split:

| sidecar | top-level field that IS a verdict | read by 9b? |
|---|---|---|
| `p35/proof_mutants.json` | `arms_as_designed` 9 / `arms_total` 9 | ❌ |
| `p35/union_oracle.json` | `cells_ok` 9 / `cells_total` 9 | ❌ |
| `p32/forgeable.json` | `hardened_kernel_broke: true` (+ `exit_code`) | ❌ |
| `p28/repro.json` | `unstable_cells: []` **and** `negative_control.fired: true` | ❌ |
| `p32/repro.json` | `unstable_cells: []` **and** `negative_control.fired: true` | ❌ |
| **`p29/arms.json`** | **`asan_positive_control {rc:1, hits:2}`** and **`compiler_warnings: []`** | ❌ **not named anywhere** |
| **`p32/storage_arms.json`** | **`positive_control[].fired`** and **`positive_control_dead_builds: []`** | ❌ **not named anywhere** |
| `p23/controls_pin.json`, `p23/sweep_fit.json`, `p29/miri_arms.json`, `p29/repro.json` | genuinely none — pins, fits, rows | n/a (correct) |

`compiler_warnings` and `positive_control_dead_builds` are `problems`-shaped
lists under other names; `asan_positive_control.rc` and `negative_control.fired`
are must-fire controls whose regression is precisely the *"regenerated at 7/9"*
hazard item A exists for. **So the unread surface is 7 of 46, not 4 of 5, and
`p29` and `p32` each have a file nobody has named.**

**Is the generator-side repair right?** ✅ **Yes in principle, and no as scoped.**
Emitting `summary: {n, as_expected}` from `p35`'s two generators is exactly the
right shape (it reuses a convention the tree already has, it is a `controls/*.py`
edit → gate re-run, **no re-measure**). But it fixes **2 of 7**. The other five
need `p28/repro.py`, `p29/arms.py`, `p32/{forgeable,repro,storage_arms}.py` to do
the same: roll up their own pass condition into `summary: {n, as_expected}` or
`problems: []`. ⚠ **Scoped at "p35's two", the repair leaves `p32/forgeable.json`
— whose whole content is one boolean verdict — unread.**

⚠ Also worth knowing: `p29/repro.json` carries **neither** `unstable_cells` nor
`negative_control`, while `p28`'s and `p32`'s do. Same generator family, three
different verdict surfaces.

### MINOR 1 — `TASK_165.md` re-introduced a claim `TASK_164_REPORT.md` had already corrected

`.tasks/TASK_165.md` item 2: *"`summary` present but `null` (**two shipped
sidecars do exactly this** — `p25`'s and `p35`'s `proof_mutants.json`)"*.

Neither carries a `summary` key at all:

```
p25/controls/proof_mutants.json  top keys: baseline derived_from_sha256 invariant
                                 measured_utc mutants pin PROBLEMS   -> reads CLEAN
p35/controls/proof_mutants.json  top keys: arms arms_as_designed arms_total
                                 derived_from_sha256 invariant measured_utc pin
                                 shipped_obligations                 -> reads NO-VERDICT
```

`TASK_164_REPORT.md` §1 says so explicitly (*"they carry **no `summary` key at
all**"*), and `TASK_164.md` had the same error. ⚠ **A correction that lands in a
report and not in the next task file is the failure mode item 3 of this very task
file warns about.** Harmless here (the shape is handled: `summary: null` →
`NO-VERDICT`), but it is the third appearance of one wrong sentence.

### MINOR 2 — `check_marginal_ir`'s docstring is now **250 lines**, 1.5× the next longest in the file, and the operative rule is at the 87% mark

```
check_marginal_ir docstring:  before 147 lines / 9281 chars
                              after  250 lines / 15739 chars   (+70%)
top-8 longest function docstrings in check.py, after:
  (249 check_marginal_ir) (164 idiom_audit) (151 _path_includes)
  (124 check_trusted_twins) (121 check_table_render) (104 _env_block)
  (95 _check_axiom_decls) (93 check_control_json_pins)
```

Positions inside it (relative line / 250):

```
 63  the ±7 census header (mechanism ONE)
150  ⚠⚠⚠ EVERYTHING ABOVE IS ONE MECHANISM AND THERE ARE TWO   <- 60% down
176  ⚠⚠⚠ A NULL IS A PROPERTY OF A CELL
217  ✅ THE OPERATIVE RULE ... use `kernel_exclusive_ir`        <- 87% down
```

**The second mechanism is larger than the first by ~250× and it is announced
three-fifths of the way down the first mechanism's essay; the sentence a reader
actually needs — *cross-RUNG comparisons use `kernel_exclusive_ir`* — is the
last thing before the floor derivation.** The task asked whether it is findable
by someone who opens the function to change it. **It is findable by someone who
reads to the end, which is not the same thing.** ✅ Cheap repair, and it costs a
gate re-run and no re-measure: hoist a **four-line** header to the top of the
docstring naming both mechanisms and the operative rule, and leave the essays
below it. ⚠ **Do not do it on its own** — batch it with the next `check.py` edit,
and remember MAJOR 4 below.

### MINOR 3 — `vparse`'s unclassified-`global` fallback is invisible on a same-line directive, and the arm is written to that limitation

`harness/vparse.py:845-853`. The `layout` and `size_of` branches are **not**
line-anchored; the fallback **is**:

```
A same-line unknown `global` form   verus!{ global align_of u8 == 1; }   -> []
B the same, on its own line         verus!{\nglobal align_of u8 == 1;\n} -> [('global','?',2,True)]
D layout NOT at line start          verus!{ global layout X is size == 1; } -> [('global layout','X',1,True)]
```

The `_selftest` cell (`vparse.py:2205`) uses spelling **B**, so the arm passes
and the gap is unpinned. The docstring's *"Never invisible -- same rule as the
`?` above"* is false for A. ⚠ **Prospective, not live** — the engineer measured
zero code-level `global` tokens outside the two forms across all 161 tracked
`.rs`, and I confirm the two live forms (D) are matched anywhere on a line. The
false-positive controls all hold: comments, string literals and an identifier
named `global` are all correctly `[]`.

### MINOR 4 — both must-fire arms sit **behind** `check_selftests`' fixture guard

`harness/check.py:857-861`. `check_selftests` returns early if
`fixture.ensure()` fails, and that `return` precedes `vparse._selftest()`,
`_ASSUME_CASES` and `_CONTROL_VERDICT_CASES`. **Not a false-green** — the guard
`rep.fail`s, so the run is red — but three pure in-process arms are coupled to a
`.temp/build/docrepro` compile they do not need, and they cannot be used as a
toolchain-free smoke test. Pre-existing; TASK_164 inherited it.

### MINOR 5 — item D's bulk twin is presented as new; `p02/verus.rs` has recorded the measurement since **TASK_048**

`patterns/p02-buffer-copy/verus.rs:211-217`, unchanged by `fb7cdb0`:

> *"Measured at TASK_048: with the body respelled `let (a, b) =
> dst.split_at_mut(n); a.copy_from_slice(&src[from..from + n]);` the item above
> needs no `external_body` at all and the file verifies `10 verified, 0 errors`
> (twin `13 verified, 0 errors`)."*

The commit message says *"a bulk-copy twin was **BUILT rather than argued
about**"*. It was built at TASK_048, in a different configuration, and the
comment recording it is the one an engineer reads at the site. **The TASK_164
measurement is still worth having** (it is the first with the shipped
`external_body` retained, and the first with a weakening arm) — but *"argued
about"* under-credits an existing measurement in the file being edited.

---

## Evidence

### Item 1 — the probes (`.temp/t165/globalprobe/`, generators kept, `verus_run.py` single-file, never `--cargo`)

```
$ bash .temp/t165/globalprobe/run.sh
rc=1 align_false            2 verified, 0 errors   error[E0080]: evaluation panicked: does not have the expected alignment
rc=0 align_true             2 verified, 0 errors
rc=1 generic_false          2 verified, 0 errors   error[E0080]: ... does not have the expected size
rc=1 alias_false            2 verified, 0 errors   error[E0080]
rc=1 cfg_plain              (no summary)           error: cannot use type `cfg_false::S` which is ignored because
                                                   it is either declared outside the verus! macro
rc=1 cfg_twin               (same)
rc=1 mod_host               1 verified, 1 errors   error: postcondition not satisfied
rc=1 ghostonly_false        2 verified, 0 errors   error[E0080]
rc=1 re_layout_false        2 verified, 0 errors   error[E0080]
rc=1 re_sizeof_false        2 verified, 0 errors   error[E0080]
rc=1 re_layout_false_unused 1 verified, 0 errors   error[E0080]
rc=1 re_layout_false_lib    1 verified, 0 errors   error[E0080]   (--crate-type=lib)

$ bash .temp/t165/globalprobe/run2.sh
rc=1 mod_host2              1 verified, 0 errors   error[E0080]  --> mod_lie.rs:3  "evaluation of `lie::_` failed here"
rc=0 cfg2_plain             2 verified, 0 errors                 (the cfg'd-in TRUE declaration)
rc=1 cfg2_twin              1 verified, 1 errors   error: postcondition not satisfied
rc=1 outside_verus          error: expected one of `!` or `::`, found `layout`
```

`verus_run.py::main` forwards only the resolved file and the flags given; there
is no implicit `--compile`. So *"the pinned Verus is stricter than its own
guide"* **re-derives**, on ten files.

The Verus guide (`../LearnVeri/_VERUS_DOC_/guide/src/reference-global.md`,
read-only) is also the authority for the *proof power* of the construct:

> *"The global directive both: **Exports the axioms** `size_of::<T>() == n` and
> `align_of::<T> == m` **for use in Verus proofs** · Creates a "static" check …"*
> and, for `usize`, *"Tells Verus that `usize::BITS == 8 * n` … the integer range
> for `usize` is `0 ..= 2^(8n) - 1`"*.

⚠ The guide documents only the `global layout T is size == n, align == m;`
spelling. **`global size_of T == n;` — the form 7 of the 10 patterns use — is
undocumented there** and is accepted by the pinned Verus. Not a defect; worth
knowing before anyone "corrects" a pattern to the documented spelling.

### The published column (MAJOR 1's operative evidence)

```
$ awk 'NR>=578 && NR<=614' results/synthesis.md | grep -E '^\| p(10|19|22|28|29|34|36|38|46|47) '
| p10-fir-stencil     | 10 | 0 | 3 | 6  | 0 | exact | PASS |
| p19-state-machine   | 12 | 0 | 3 | 6  | 0 | exact | PASS |
| p22-hash-probe      | 20 | 0 | 5 | 10 | 0 | exact | PASS |
| p28-intrusive-lists | 23 | 0 | 7 | 20 | 0 | norel | PASS |
| p29-bst-delete      | 25 | 0 | 7 | 20 | 0 | norel | PASS |
| p34-refcount-stack  | 24 | 0 | 7 | 20 | 0 | norel | PASS |
| p36-vtable-dispatch | 12 | 0 | 4 | 7  | 0 | norel | PASS |
| p38-alias-pun       | 13 | 0 | 5 | 10 | 0 | exact | PASS |
| p46-bignum-mac      | 21 | 0 | 5 | 10 | 0 | exact | PASS |
| p47-ct-compare      | 12 | 0 | 3 | 6  | 0 | exact | PASS |
$ sed -n 615p results/synthesis.md
**Trusted base, all 33 rows: 152 items (333 lines) and 0 axioms.** ...
```

### Item 2 — 28 shapes against `control_json_verdict`, plus stage 9b itself

```
$ python3 .temp/t165/verdict_attack.py
`problems` as a DICT                           FAILED      1
`problems` as an EMPTY dict                    FAILED      1
`problems` list of EMPTY STRINGS               FAILED      1
`problems` list containing null                FAILED      1
`summary` as_expected > n                      FAILED      1
`summary` missing n                            FAILED      1
`summary` present but NULL                     NO-VERDICT  0
`summary` = {} (empty object)                  NO-VERDICT  0
`summary` = false                              FAILED      1
`summary` = 0                                  FAILED      1
`summary` counts as BOOLS                      FAILED      1
both keys DISAGREE (clean+regressed)           FAILED      1
both keys disagree the OTHER way               FAILED      1
top-level LIST / STRING / NUMBER               FAILED      1  (each)
EMPTY object (generator wrote {})              NO-VERDICT  0
`problems` NESTED one level down               NO-VERDICT  0   <- top-level read only, by design
bespoke: arms_as_designed 7 of 9               NO-VERDICT  0   <- MAJOR 3
bespoke: unstable_cells NON-EMPTY              NO-VERDICT  0   <- MAJOR 3
bespoke: compiler_warnings NON-EMPTY           NO-VERDICT  0   <- MAJOR 3, unnamed
bespoke: positive_control_dead_builds          NO-VERDICT  0   <- MAJOR 3, unnamed

=== stage 9b's own path (the "generator crashed half-way" question) ===
verdicts: {'truncated.json': 'UNREADABLE', 'valid_partial.json': 'FRESH',
           'bespoke.json': 'FRESH'}
fails:   [('tables', 'controls/truncated.json: not readable as JSON
           (Expecting value: line 1 column 42 ...)')]
printed: "no verdict field ... in 1 of 3 sidecar(s): ['bespoke.json']"
```

✅ **A truncated sidecar FAILS, it does not read CLEAN.** ✅ **A doc missing the
keys entirely is `NO-VERDICT` and is printed, not silently fine.** ⚠ **The one
residual:** a *valid* JSON whose `problems: []` was serialised before the loop
that would fill it reads `CLEAN`. **Not live** — all 30 generators build the list
in memory and `json.dump` once, so a mid-run crash leaves the OLD file, which the
pin then catches as `STALE`. Worth one sentence in the docstring; not worth code.

### Item 2's load-bearing premise, re-derived

```
$ python3 .temp/t165/gen_exit_audit.py
sidecars with a top-level `problems` key: 30
  exits non-zero on non-empty `problems`: 30
  NO exit tied to `problems`            : 0
  generator not located                 : 0
  sample: patterns/p25-realloc-growth/controls/detectors.py
          ['return 1 if problems else 0', 'sys.exit(main())']
```

✅ **30 of 30 confirmed** — so `rep.fail` on a non-empty `problems` is the right
disposition and not a judgement call.

### Item 3 — every tree-wide count, re-derived independently

```
$ python3 .temp/t165/r45_null_check.py
== -O3 isolated: 66 cells over 33 patterns
   |null| >= 2.00 :   8   p25 large 269.52 · p42 large -31.0 · p03 6.0 (both)
                          · p04 6.0 (both) · p02 -2.0 (both)
   1.00<=|n|<2.00 :  35   (exactly 1.00: 34; other: p28 large 1.01)
   |null| <  1.00 :  23
== -O0 isolated
   |null| >= 2.00 :  10   p28 large 1732.73 · p29 large 425.8 · p28 small 281.28
                          · p25 large 269.52 · p29 small 113.76 · p42 large -31.0
                          · p19 -6.0 (both) · p46 -3.0 (both)
== -O3 whole
   |null| >= 2.00 :  37       |null| >= 20.00:  15
   the 15: p11 -494.0/-166.0 · p29 465.55/101.77 · p25 269.52 · p28 211.87/46.02
           · p49 55.57 · p35 36.47 · p14 34.0 · p42 -33.0 · p17 30.0 (both)
           · p18 -25.0 · p13 22.0

           O0/iso           O3/iso           O0/whole         O3/whole
        small    large   small    large   small    large   small    large
p25      0.00   269.52    0.00   269.52    0.00   269.52    0.00   269.52
p28    281.28  1732.73    0.00     1.01  281.28  1732.73   46.02   211.87
p29    113.76   425.80    0.00    -0.02  113.76   425.80  101.77   465.55
p42      0.00   -31.00    0.00   -31.00    0.00   -31.00   -2.00   -33.00
p11      0.00     0.00   -1.00    -1.00    0.00     0.00 -494.00  -166.00
```

**All 8 / 35 / 34 / 23, 10-of-66, 37-of-66, 15-of-66 and the named 15 reproduce
exactly, as does every cell of the five-row table.** ✅

**The shipped list is the DERIVED one, not the asserted one** —
`harness/check.py:2874-2876` reads `NOT in it (9) p23 p25 p28 p29 p32 p34 p35
p42 p49`, and re-deriving from the artefact gives the same:

```
$ python3 -c "... .temp/r98/treescan_large.json ..."
census patterns: 24  [p01..p14 p16 p17 p18 p19 p22 p27 p36 p38 p46 p47]
tree: 33   NOT in census: ['p23','p25','p28','p29','p32','p34','p35','p42','p49']
in census not tree: []
```

✅ **Census denominator and tree size both confirmed: 24 and 33.** The
`2026-08-22` date and the `.temp/r98/treescan.py` citation both **pre-date**
TASK_164 (`git show fb7cdb0^:harness/check.py:2851` carries the same line);
`treescan.py` exists. ⚠ One loose end nobody needs to chase: the artefact's
mtime is `2026-08-25 16:31`, three days after the stated census date. `.temp/`
mtimes are not evidence and the figure was not re-taken by TASK_164, so I did
not pursue it — **naming it so the next agent does not either.**

### Item 4 — the twin, with three attacks × both twins

```
$ bash .temp/t165/twinprobe/run.sh ; bash .temp/t165/twinprobe/run2.sh
                            INDEXED (shipped)              BULK (probe)
baseline            rc=0  12 verified, 0 errors     rc=0  11 verified, 0 errors
W1 `from+n <= src@.len()` +1
                    rc=1  10 verified, 2 errors     rc=1  10 verified, 1 errors
                    postcondition not satisfied     precondition not satisfied
                    + precondition: index in bounds + possible arithmetic overflow
W2 `n <= old(dst)@.len()` +1
                    rc=1  11 verified, 1 errors     rc=1  10 verified, 1 errors
                    invariant not satisfied         precondition not satisfied (x2)
                      before loop
W3 body copies the WRONG source offset
                    rc=1  11 verified, 1 errors     rc=1  10 verified, 1 errors
                    invariant not satisfied         postcondition not satisfied
                      at end of loop body
```

Substitution counts asserted on every arm (1, 2, 3, 2, 2, 1, 1 —
`.temp/t165/twinprobe/mk.py`). Every diagnostic points inside
`slb_twin_copy_bytes`.

**Answers to item 4's three questions:**

1. **TASK_164's three numbers re-run exactly**: shipped `12 verified, 0 errors`,
   bulk `11 verified, 0 errors`, weakened bulk `10 verified, 1 errors` with
   *"precondition not satisfied"*.
2. ⚠⚠ **WHY ONE FEWER: it is mechanical, not weakness.** `check.py:5148` states
   the rule the whole project pins obligations by — *"one Verus query per
   function **plus one per loop body**"*. The bulk body deletes the `while`, so
   it deletes exactly one query. **12 − 1 = 11.** The engineer's *"a count of SMT
   query units"* is right and this is the one-line derivation it did not give.
3. ✅ **THE BULK TWIN IS AS STRONG AN ORACLE, NOT MERELY SHORTER.** All three
   attacks fire on both. ⚠ **And on two of the three the bulk twin's diagnostic
   is BETTER**: it fails at the *contract* (`precondition` / `postcondition`)
   where the indexed twin fails at a *proof-internal loop invariant*. A twin
   exists to certify a contract; an error that names the contract is the one a
   reader can act on. ⚠ **One weakening arm was NOT enough to answer this** — W1
   alone leaves open whether the bulk twin can catch a `dst`-side or a
   body-side error, and W2/W3 are what close it.

   ⚠ **The one real argument for keeping the indexed loop stands and the report
   states it:** the bulk twin discharges its obligation through **one more vstd
   `assume_specification`** (`std_specs/slice.rs:205`), where the indexed loop
   re-derives the copy element by element. That is independence, not strength,
   and it is a judgement — as the report says. **I agree with keeping the
   indexed one, on that ground and not on strength.**

**The five stale `.memory/04-verus.md:133 / :813` citations — confirmed and
priced.**

```
$ sed -n '131,135p;811,815p' .memory/04-verus.md
:133  **An `external_body` item need not contain `unsafe`.** p08's `copy_in` ...
:813  ... a redundant second conjunct on both item and twin ...
$ python3 -c "... p06 fence ..."
p06 fence spans lines 361 .. 707     line 446 inside fence: True
```

Five sites: `p02/NOTES.md:691`, `p06/README.md:108`, `p06/NOTES.md:904`,
`p06/verus.rs:436`, **`p06/spec.md:446` — inside the `slb-contract` fence.**
Price: three are gate-only (`NOTES.md` ×2, `README.md`), **`p06/verus.rs` is in
`measurement_sources` so it costs a RE-MEASURE**, and `p06/spec.md:446` costs a
`contract_sha256` move + `report.py` + a gate. **The report's pricing is right.**

### Item 5 — the manager's own artefacts

**`.memory/05-layout.md`'s confession is ACCURATE and the replacement is RIGHT.**
Both re-run:

```
$ grep -l '"harness/' patterns/*/controls/*.json        # the WRONG recipe
patterns/p23-partition/controls/sweep_fit.json
patterns/p23-partition/controls/controls_pin.json     <-- the false positive
patterns/p35-tagged-union/controls/proof_mutants.json
patterns/p35-tagged-union/controls/union_oracle.json     -> FOUR

$ python3 -c "...reads derived_from_sha256's KEYS..."   # the file's recipe
patterns/p23-partition/controls/sweep_fit.json      ['harness/asm.py','harness/build.py','harness/measure.py']
patterns/p35-tagged-union/controls/proof_mutants.json ['harness/check.py']
patterns/p35-tagged-union/controls/union_oracle.json  ['harness/check.py','harness/vparse.py']
                                                         -> THREE

$ python3 -c "...p23/controls_pin.json['pin']..."
  "read_by": "harness/check.py::check_control_json_pins (gate stage 9b)"   <- prose, not a pin
```

✅ **The confession is exact, the false positive is the file and the field it
names, and the replacement command is correct.** A wrong correction would have
been worse than the error; this one is right.

**Finding 63, ✅/⊘ audit.** (a) *"30 of 30 generators exit non-zero"* ✅ re-derived
(above). (a) *"0 of 46 pin themselves"* ✅ re-derived. (a) *"35 CLEAN / 11
NO-VERDICT / 0 FAILED"* ✅ re-derived. (b) the whole `global` half ✅ re-derived
and strengthened. (b) *"3 + 7 = 10 of 33, p32 has none"* ✅. (d) ✅ re-derived.
**(c) contains MAJOR 2 under a `✅` mark.** ⊘ items are correctly marked ⊘, and
one of them (*"four bespoke shapes"*) is MAJOR 3.

**Queue item 26's closure — accurate.** The `check.py` sentence is gone, the
retraction quotes `std_specs/slice.rs:205`, the dangling-`.memory/` half is real,
the five adjacent citations are real and correctly priced. ⚠ *"a bulk-copy twin
was BUILT rather than argued about"* — see MINOR 5.

**Queue item 30's closure — the withdrawal is RIGHT, and it is slightly harsh on
the original.** The struck sentence (*"leads with ±0.20 and warns of ±7 against a
measured 269.52 at `-O3 isolated`"*) genuinely conflates a between-runs drift
term with a within-run R4/R5 gap, so *"conflated two mechanisms"* is the right
reading. ⚠ **But its number and its cell were both CORRECT** — `p25 large` at
`-O3 isolated` is `+269.52` — and its *instinct* (the docstring's uncertainty
budget is orders of magnitude below a measured figure it does not explain) is
exactly what item C then landed. **Withdraw the framing, keep the observation.**
⚠ **Second point: item 30's ORIGINAL complaint was already fixed before
TASK_164.** `git show fb7cdb0^:harness/check.py:2869` already carried *"⚠ `-O3
isolated` IS NOT INVARIANT"* and `:2921` already named `p03/p04/p38/p46`. So
*"CLOSED at TASK_164"* is true of the item's *body* only because TASK_164 did
different and larger work; the thing the item asked for had been done earlier.
Cosmetic, but it is the same header-vs-body class rule 13 governs.

**The commit messages.** `fb7cdb0` and `8273bfd` are accurate against the tree
except for the `p42 ... 0.00 on small in all four cells` clause in `8273bfd`
(MAJOR 2). Two clauses I checked and confirm: *"`results/synthesis.md` moved 4
lines, all p08, all hundredths"* and *"section 3's `axioms` column did NOT move
on any of the 33 rows"* — the latter is true and is exactly what MAJOR 1 is
about.

**The sentence the manager is least sure of — finding 63's *"stage 5e already
fails on"* a `global` lie, refuting `TASK_156` minor 2 — SURVIVES.** Ten probes,
the anomaly condition read out of `_verus`'s source, the call site named, the
stage's call site named as unconditional, and every flag checked. ⚠ **State it
precisely, though**: what stage 5e fails on is *"Verus reported `N verified, 0
errors` and the process exited non-zero"*. That is a rustc-rejection detector, not
a `global` detector; it catches a `global` lie **because rustc rejects the file**,
and it would not catch a `global` that rustc accepts. Since rustc accepts none of
the eleven false spellings I could construct, the conclusion holds — but the
mechanism is one step longer than the sentence implies.

### Item 6 — the process disclosures, all four

```
$ git show fb7cdb0 --stat --name-only | grep -E 'spec\.md|results/tables|^results/p[0-9]'
(nothing)                                                                  rc=1
```
✅ *"wall clock only: no `contract_sha256` moved, no published table went stale,
no `report.py` ran and no re-measure was needed"* — **confirmed from `git`.** The
commit touches `.tasks/`, `harness/{check,vparse}.py`, p35's two sidecars, 37
`results/gate/*.json`, `results/synthesis.md` and `synthesis/licence.json`.

```
$ python3 .temp/t165/sidecar_diff165.py      # against `git show fb7cdb0^:`, not the snapshot
proof_mutants.json: leaves before=53 after=53 added=[] removed=[] MOVED=2
    .derived_from_sha256.harness/check.py  703f0aa2… -> 60aba3e5…
    .measured_utc  2026-08-31T09:30:56Z -> 2026-09-02T02:45:58Z
union_oracle.json:  leaves before=38 after=38 added=[] removed=[] MOVED=3
    .derived_from_sha256.harness/check.py  703f0aa2… -> 60aba3e5…
    .derived_from_sha256.harness/vparse.py de1f4db8… -> 0922b5ad…
    .measured_utc  2026-08-31T09:31:05Z -> 2026-09-02T02:45:36Z
```
✅ **ZERO substantive leaves moved**, independently confirmed against the
committed pre-state rather than against the engineer's `.temp/t164/p35sidecar/`.

```
$ grep -rn 'p01\.log' .tasks/TASK_164_REPORT.md RECAP.md .memory/
.tasks/TASK_164_REPORT.md:838:   ...is not usable evidence...
```
✅ **The only mention is the disclosure itself. No number is read from it.**

**`temp_citations.py` — not running `--update` was the RIGHT call, and there is a
reason the report did not give.** rc=0, `new=0 unclassified=0 resolved=4`. The
baseline is a committed artefact and subagents cannot commit, so deferring is
correct. ⚠ **But the manager should not simply run `--update` either.** The
tool's own failure condition is `bad = bool(new) or bool(unclassified)`
(`temp_citations.py:360`) and the four RESOLVED entries are `.temp/p49ctl/*` —
**gitignored scratch that `CLAUDE.md` constraint 1 tells agents to delete once
their gates are green.** Prune them and the next agent who cleans `.temp/p49ctl/`
turns a benign note into `new=4` and **rc=1**. **What the manager owes: either
keep them and say why in the baseline's `kind`, or prune them and simultaneously
promote the four scratch dirs out of `.temp/`.** Do not prune in isolation.

### `.temp/mgr164/` — read, four claims checked, no error found

The task said an error there is worth more than most. I checked its four
load-bearing derivations and **all four hold**:

```
R4/R5 identity at -O3, all 33:  exact 28, norel 5 = p25 p28 p29 p34 p36   ✅ exact match
composition --check temporal  :  p25 p27 p28 p29 p32 p34 (six)            ✅ so norel∩temporal = 4 of 6
`global layout` on p28 p29 p34 and NOT p25                                ✅ matches my census
set relations: norel ⊂ NOT-LIC (5/5); big-null ⊂ NOT-LIC (5/5);
  norel\null = {p34,p36}; null\norel = {p11,p42}                          ✅ all four
```

⚠ **One thing to fix before it becomes a task file:** `.temp/mgr164/NOTES.md`
§8's middle table row quotes the **superseded, input-maxed** null set —
*"p25 269.52 · p28 1732.73 · p29 425.80 · p42 31.00 · p11 494.00"* — which is the
table `8273bfd` replaced four and a half hours later. The **set** is unchanged so
§8's set algebra is unaffected, but the numbers in it are the ones entry 23 now
withdraws (and `p11`'s is `−494.00` on **small**). **Re-quote from the four-axis
table when the task file is written.**

---

## Unsure / not done

1. **I did not run a 33-pattern sweep and none is needed.** Every claim above is
   a pure function, a `_selftest()` cell, a single-file `./verus_run.py` run, a
   read of a committed record, or a read-only `git` command.
2. **MAJOR 1 is a recommendation, not a measurement.** The measurement
   (rustc checks every `global` I could write) went the engineer's way. The
   disagreement is about **what `verus.axioms` and the published `axioms` column
   are for**, and reasonable people can read `check.py:4616`'s caption either
   way. ⚠ **What is not a judgement call is `results/synthesis.md:615`**: it
   publishes `0 axioms` for 33 rows and the prose under it says that means the
   author wrote none of their own. That sentence is false on 10 rows whichever
   way the gate question is settled.
3. **I did not price option A by running it.** The 10 `contract_sha256` moves are
   the engineer's arithmetic (10 patterns × one declaration each); I confirmed
   the 10-pattern set and that `verus.axioms` lives inside the fence, not that
   each edit lands cleanly.
4. **I did not test `global` against a 32-bit target** — there is no 32-bit
   toolchain on this box (`.memory/00-environment.md`). The `global size_of usize
   == 8` rows would be false there and the E0080 would fire; that is inference,
   not measurement.
5. **I did not verify the TASK_082 `parse()`-widening measurement** (p36 → six
   FAILs). Same as the engineer: taken as read.
6. **I did not re-derive `.temp/mgr164/`'s items 0a, 1, 4, 5, 7a** (the section
   mention counts, the R2/R3 median, the pointer-cursor census, the pearson, the
   `undeclared` column). Out of scope; they belong to the Results task's review.
7. **MINOR 5 is a credit question, not a correctness one.** Both measurements
   are real and they are of different configurations.
8. **PROTOCOL rule 2 running count: launched from 926. With this report, 929** —
   three manager claims refuted here: `.memory/03-measurement.md` entry 23's
   *"p42 is 0.00 on small in all four cells"* (measured `−2.00` at `-O3 whole`),
   `RECAP` finding 63(a)'s *"four bespoke verdict shapes"* (measured 7 sidecars,
   ≥8 spellings), and `TASK_165.md`'s own *"p25's and p35's proof_mutants.json
   carry `summary: null`"* (neither has the key). ⚠ **Reconciliation across
   branches is the manager's job; I have carried it forward by three and named
   what each counts.**

---

## Clean negatives — named attacks that did NOT land, so nobody re-runs them

1. **A false `global` cannot reach a running binary by any route I could build.**
   Seven new ones on top of TASK_164's three: a **false `align`** (checked, with
   its own diagnostic), a **generic instantiation** (`W<u8>`), a **type alias**,
   a lie used **only in ghost code**, a lie in a **`#[path]`-included module**, a
   **`#[cfg]`-dependent** declaration (both configurations), and a `global`
   **outside `verus!`** (a syntax error). **Stop trying; the net holds.**
2. **`verus_run.py` does not pass `--compile` in single-file mode.** I read
   `main()` to check whether the E0080 was an artefact of the driver. It is not.
3. **No gate flag reaches a PASS with the primary `_verus` skipped.**
   `--no-build`, `--no-callgrind`, `--no-verus-mutants`, `--skip`, `--cells` all
   checked; `--skip` takes input stems, not stages. Blocked rows are `miri` and
   `twin` only, on p01/p35/p42.
4. **`control_json_verdict` handles every shape the manager listed** — `problems`
   as a dict, `as_expected > n`, `summary` missing `n`, `summary: null`, both
   keys disagreeing, a top-level list, a list of empty strings — **plus** a
   top-level string, a top-level number, `summary: false`, `summary: 0`, boolean
   counts and `problems: [None]`. **28 shapes, zero misbehaviours.**
5. **A truncated sidecar does NOT read CLEAN** — stage 9b's `UNREADABLE` path
   catches it with a `rep.fail`, and I drove the stage to prove it.
6. **No shipped sidecar hides a verdict at depth.** I walked all 46 documents to
   any depth looking for a `problems`/`summary` the top-level read would miss.
   Every nested hit (`.mutants[i].ok`, `.arms.M1.errors`, …) is per-row detail
   whose roll-up is at top level. **The top-level-only read is not the gap;
   MAJOR 3 is.**
7. **Every tree-wide number in item C's docstring reproduces exactly**, derived
   from `results/gate/p*.json` by a script that shares no code with
   `.temp/t164/r45_null.py`. I went looking for a sixth entry-23 error in the
   distributions and found none.
8. **The shipped nine is the DERIVED list, not the asserted one.** The correction
   landed in the code, not only in the report.
9. **`vparse`'s false-positive direction is sound** — comments, string literals,
   an identifier named `global`, and a two-directive line all behave; the two
   LIVE forms are matched anywhere on a line, not only at line start.
10. **The `.memory/05-layout.md` confession is exactly accurate** and its
    replacement recipe is right. Both re-run.
11. **`30 of 30` generators exit non-zero on a non-empty `problems`** — the
    premise `rep.fail` rests on, re-derived from the generators themselves.
12. **p35's two sidecars moved nothing substantive**, confirmed against
    `git show fb7cdb0^:` rather than against the engineer's snapshot.
13. **`.temp/mgr164/`'s four load-bearing derivations all hold** (the `norel`
    census, the temporal intersection, the `global layout` set, the set algebra).

---

## Is `TASK_164` FINISHED?

**Nearly. Two things a reader needs that no artefact carries:**

1. ⚠⚠ **Nothing tells a reader of `results/synthesis.md` that ten rows carry a
   hand-written `global` directive.** The gate records `global_decls` per file,
   the docstrings explain it at length, and **the one artefact a reader actually
   reads publishes `0 axioms` and a prose sentence that contradicts it.** That is
   PROTOCOL rule 1's fourth step — *a result is finished when a reader can find
   it, not when its gate is green* — applied to a finding rather than a pattern.
   MAJOR 1, option **B**, costs a `synthesize.py` edit and one run.
2. **The MAJOR 2 sentence must come out of `.memory/` and out of finding 63's
   `✅` half** before anyone quotes entry 23 again.

Everything else is carried: the arms exist and have been seen to fail, the census
is in the code, the deviation is disclosed in three places, and the two process
overruns are disclosed and verified.

---

## Memory updates

**None. I wrote nothing into `.memory/` or `RECAP.md`** (reviewer; forbidden).
What the manager should land, in priority order:

| file | what |
|---|---|
| `.memory/03-measurement.md` **entry 23** | ⚠⚠ **MAJOR 2** — *"`p25`'s and `p42`'s `small.bin` nulls are `0.00` in all four cells"* is FALSE for `p42` (`−2.00` at `-O3 whole`) and contradicts the table eight lines above it. Replace with *"`p25` in all four; `p42` in three of four"*. |
| `RECAP.md` **finding 63(c)** | the same clause, and it sits under a **`✅ Manager-re-derived`** mark. **Move it to `⊘`, or fix it and keep the ✅.** |
| `RECAP.md` **finding 63(a)** | *"four bespoke verdict shapes"* → **7 sidecars, ≥8 spellings**, and name `p29/arms.json` and `p32/storage_arms.json`, which nothing has named. The generator-side repair as scoped covers **2 of 7**. |
| `results/synthesis.md` §3 (via `synthesize.py`) | ⚠⚠ **MAJOR 1** — publish `global_decls` beside `axioms`, and rewrite *"0 axioms"* and *"the author wrote none of their own"*. **No gate, no re-measure**: `synthesis/*.py` is in neither digest. |
| `.memory/04-verus.md` | the `global` measurement is **stronger** than TASK_164 recorded: `align` is const-checked too (its own diagnostic), and the check fires on a **generic instantiation**, a **type alias**, a **ghost-only** use and a **`#[path]`-included module** — the last being the vector with blast radius 33. Also: `global` **outside `verus!` is a syntax error**, and the Verus guide documents only the `global layout` spelling, not the `global size_of` one that 7 patterns use. |
| `.memory/04-verus.md` **or** `02` | stage 5e is a **rustc-rejection detector**, not a `global` detector. It catches a `global` lie *because rustc rejects the file*. State the mechanism, not just the outcome (rule 12). |
| `RECAP.md` **queue** | ⚠ **new item**: `check_marginal_ir`'s docstring is 250 lines, 1.5× the next longest, with the second mechanism at 60% and the operative rule at 87%. Hoist a four-line header. **Batch with the next `check.py` edit** — which now also owes the two p35 generator re-runs (`.memory/05-layout.md`, correct as landed). |
| `RECAP.md` **queue** | ⚠ `temp_citations.py --update` is **not** a free prune: dropping the four `.temp/p49ctl/*` entries makes them `new=4` and `rc=1` the moment that gitignored scratch is cleaned. Decide, do not default. |
| `.temp/mgr164/NOTES.md` §8 | before it becomes a task file: its null table quotes the **superseded input-maxed** figures (`p11 494.00` is `−494.00` on **small**). The set algebra is unaffected. |

**PROTOCOL rule 2 running count: 926 → 929** (three manager claims refuted, named
in *Unsure / not done* 8). Reconciliation across branches is the manager's job.
