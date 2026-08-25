# TASK_096 — report

**Role: research engineer.** Scratch: `.temp/t96/` (a generator for every claim).
No `git add`/`git commit`. No `.memory/` edit. `harness/build.py` and
`harness/asm.py` untouched. `pilot/` untouched. Verus only via `./verus_run.py`,
single-file.

**PROTOCOL rule 2 running count: 274 → 279.** Five measured contradictions,
itemised at the end. Two are against premises written into `TASK_096.md` itself.

---

## Did

### §A — investigated `_scan_unsafe_sites`; **RECOMMEND: narrow it, but only behind a DECLARED hatch with three enforced consequences.** The case for leaving it alone is stated at full strength and is not weak.

| artefact | what it is |
|---|---|
| `.temp/t96/a1_union.rs` (+ `_norequires`, `_mutant`) | the p35 shape at the pin, with two negative controls |
| `.temp/t96/a2_twin_unwritable.rs` | the comply route's `#[cfg(slb_twin)]` twin |
| `.temp/t96/a3_plant.py` | plants into `patterns/p03-bounded-stack/` and runs the **real gate**; bytes AND mtimes snapshotted, restored in `finally:` |
| `.temp/t96/a4_probe_battery.py`, `a5_probe_battery2.py` | 18 `unsafe` constructs through Verus, each also with its guard removed |
| `.temp/t96/a6_narrow_rule.py` | the narrowed predicate, re-implemented against the gate's own `vparse` + `check._is_trusted`, over 9 planted cases and all 24 shipped `verus.rs`. **Does not edit `check.py`.** |
| `.temp/t96/a7_source_to_published.py` | §A.4's missing acceptance test: **one command, planted source → `results/synthesis.md`** |
| `.temp/t96/b1_verus_exit_census.py` | 25 pinned Verus sources × 2 configurations, return codes |

### §C — landed in the tree

- `harness/check.py::check_marginal_ir` — the ±7 bistable docstring weakened to
  what four patterns show (RECAP "Owed" 30).
- `harness/check.py::_callgrind_total` — "three patterns" → four, with p46's
  `2 × 7`.
- `harness/check.py::check_miri` — the `if not why_required` branch
  (TASK_084_REVIEW major 3): the sentence now scopes itself to PATTERN-LOCAL
  declarations and the branch `rep.shout`s the sixth route. **No verdict moves:
  no pattern reaches the branch.**
- **43 `check.py:<line>` references removed across 24 files** — 31 of the
  `check.py:NNN` form, plus **12 bare `:NNNN` continuations** (8 in
  `harness/limbs.py`'s limb table, and 4 more in p05, p08, p16, p17) that a
  `check\.py:[0-9]` grep **does not see**. ⚠ **Three of those four sat one
  clause after a citation I had already fixed** — *"…and the same function at
  `:2880` fails the gate…"* — so a `check.py:NNN`-only pass leaves half a rotted
  citation behind. Found with `git grep -nE '\`:[0-9]{3,4}'`.
  Generator `.temp/t96/c4_fix_citations.py` (idempotent), audit
  `.temp/t96/c4_rot_audit.py`.

### §D — the sweep (`.temp/t96/d_sweep.sh`), in the mandatory order, then the repair pass (`d2_resweep.sh`).

---

## §D — sweep results

**Part 1, all 24 patterns, ~44 minutes, `rc=0` on every one:**

```
p01 337s PASS-WITH-BLOCKED-ROWS      p16  87s PASS
p02 109s PASS                        p17 100s PASS
p03  92s PASS                        p18  77s PASS
p04  94s PASS                        p19  87s PASS
p05  83s PASS                        p22 301s PASS
p06 125s PASS                        p27 204s PASS
p07  87s PASS                        p36  93s PASS
p08 129s PASS                        p38  96s PASS
p09  94s PASS                        p46 105s PASS
p10  80s PASS                        p47  78s PASS
p11  83s PASS
p12 103s PASS      == 23 PASS + 1 PASS-WITH-BLOCKED-ROWS, 0 failures ==
p13 106s PASS
p14 120s PASS
```

then, **in the mandatory order**:

```
== 2. licence.py --emit  (BEFORE synthesize.py) ==
wrote synthesis/licence.json: 24 patterns, 96 pair verdicts (LICENSED, NOT-LIC, UNDEC)
== 3. synthesize.py ==
wrote results/synthesis.md  (60660 bytes, 504 lines)
== 4. measure.py --check-stale ==
48 record(s) examined, 8 STALE
```

⚠ **The 8 STALE are RED, and they are MY doing, not the tree's.** Every one is a
**gate** record for **p01–p08**, stale on **`harness/check.py`** — exactly the
mid-sweep edit disclosed under "Problems", and nothing else:

```
STALE   results/gate/p01-array-sum.json      harness/check.py
...     (p02..p08 identically)
STALE   results/gate/p05-index-flatten.json  patterns/p05-index-flatten/NOTES.md
STALE   results/gate/p08-overlap-move.json   patterns/p08-overlap-move/controls/gen_controls.py
```

`.temp/t96/d2_gate_stale.py` names **the same eight independently**
(`be5ecafbb68c -> 96f51a28a93b`), which is the cross-check I wanted before
trusting either.
✅ **p12's `NOTES.md` edit did NOT stale p12** — the edit landed before p12's
record was written. Measured, not assumed.
ⓘ **`GEN-ONLY results/p18-varint-shift.json` is PRE-EXISTING** — I did not touch
`p18/inputs/gen.py` (`git status` confirms), and `GEN-ONLY` is not counted in
the 8.

**Part 2 — the repair pass, `.temp/t96/d2_resweep.sh` — ALL GREEN:**

```
8 stale gate record(s): p01 p02 p03 p04 p05 p06 p07 p08
re-gating: p01 p02 p03 p04 p05 p06 p07 p08
p01 rc=0 337s :: PASS-WITH-BLOCKED-ROWS      p05 rc=0  84s :: PASS
p02 rc=0 109s :: PASS                        p06 rc=0 125s :: PASS
p03 rc=0  93s :: PASS                        p07 rc=0  87s :: PASS
p04 rc=0  93s :: PASS                        p08 rc=0 129s :: PASS
== 2. licence.py --emit  (BEFORE synthesize.py) ==
wrote synthesis/licence.json: 24 patterns, 96 pair verdicts (LICENSED, NOT-LIC, UNDEC)
== 3. synthesize.py ==
wrote results/synthesis.md  (60660 bytes, 504 lines)
== 4. measure.py --check-stale ==
48 record(s) examined, 0 STALE
== 5. gate records stale against the live tree? (must be 0) ==
0 stale gate record(s)
== 6. one check.py hash across all 24 gate records? ==
live harness/check.py: 96f51a28a93bdc16
  96f51a28a93bdc16  24 record(s)  MATCHES LIVE
verdicts: Counter({'PASS': 23, 'PASS-WITH-BLOCKED-ROWS': 1})
failures: 0
```

**Final state, re-derived after the acceptance test as well:**
`verdicts {'PASS': 23, 'PASS-WITH-BLOCKED-ROWS': 1}`, **total failures 0**,
**24 records**, `48 record(s) examined, 0 STALE`, `0 stale gate record(s)`.

### What the sweep moved in the published artefacts

- **`results/synthesis.md` is BYTE-IDENTICAL to HEAD.** ⚠ RECAP warns that a
  byte-identical regeneration is *"evidence about the check"* — so I made it
  evidence about the tree instead: **§A.4's acceptance test moves 8 lines of the
  same file from a source plant** (below), so the pipeline demonstrably *can*
  move it and this zero is a real negative.
- **`synthesis/licence.json` moved: 1857 leaves, key sets identical, 91 changed
  — every one a file-hash leaf (74 `.py`, 17 `.md`). Zero verdicts, zero cells.**
  Same shape TASK_084_REVIEW measured for a harness edit.
- **`results/tables/`** — see below; two moved, and only one of them is mine.

### ⚠ `results/tables/p46-bignum-mac.md` HAS BEEN STALE SINCE TASK_092, AND NOTHING WOULD HAVE SAID SO

`bash .temp/t96/d3_tables.sh` regenerates all 24 tables and reports which move.
**Two did:**

| table | moved | mine? |
|---|---|---|
| `p09-bitset.md` | 4 lines — the two citations inside the `why`, and the contract digest `c391270c673f → 0a37c0cd1418` | **yes**, expected |
| `p46-bignum-mac.md` | **60 lines** — the record timestamp/git rev (`06:27:53Z / 9c8fd27a766c → 08:22:25Z / 3203dbbc6158`), the contract digest `bddd7e032a72 → 43925b2955e0`, a `why` line, and **the whole wall-clock table** | ⚠ **NO** |

**`results/tables/` is regenerated by nothing** — not `check.py`, not the sweep,
not `synthesize.py`, and `measure.py --check-stale` does not look at it. So
p46's table has been quoting a **pre-TASK_092 contract digest and pre-re-measure
wall-clock numbers** in the committed tree since TASK_092, and the only reason
it surfaced is that I regenerated all 24 rather than just p09. The other 22 were
current. **Worth a `harness/` one-liner or a line in the sweep recipe.**

### §A.4 — THE ACCEPTANCE TEST WAS RUN, AND IT FIRED

`python3 .temp/t96/a7_source_to_published.py verified` — one command, planted
source → `results/synthesis.md`:

```
$ harness/check.py p03                     rc=1   [tcb-unsafe] verus.rs:525
$ synthesis/licence.py --emit synthesis/licence.json
$ synthesis/synthesize.py                  wrote results/synthesis.md (60601 bytes, 504 lines)

published sha256 cab76f8feaf13c67… -> d92055203a75f618…
results/synthesis.md MOVED: 8 line(s) differ (+0 lines)
  line 178  | `< 2.00` … | 120 | 0 | 120 |   ->  | 122 | 0 | 122 |
  line 179  | `2.00 … 16.00` … | 22 | 8 | 14 |  ->  | 20 | 8 | 12 |
  line 243  | p03-bounded-stack | 5110.00 | 17237.00 | LICENSED | small +5117.00 (+7.00) **?** …  ->  (emptied)
  line 323  | p03-bounded-stack | 0.00 | 0.00 | LICENSED | small +6.00 …  ->  small -8.00 …
  line 421  | p03-bounded-stack | 9 | 0 | 5 | 10 | 0 | exact | PASS |
        ->  | p03-bounded-stack | 10 | 0 | 5 | 10 | 0 | exact | FAIL |
```

**Line 421 is §3's proof-burden table — the obligations column and the verdict a
reader quotes — and it moved from a `union` declaration in `verus.rs`.** The
test exits 1 on a byte-identical file; it exited 0 because the file moved.
Everything is restored in a `finally:` and `results/synthesis.md` is back to
`cab76f8feaf13c67…`, byte-identical to HEAD.

---

## Evidence

### §A.1 — the block REPRODUCES on an EXECUTED gate. It was a code read; it is not any more.

`.temp/t96/a3_plant.py verified` adds to `patterns/p03-bounded-stack/verus.rs`,
inside `verus! {}`, a Rust `union` and a **verified** (not `external_body`)
accessor, and moves the obligation pins to match:

```rust
pub union T96Slot { pub i: u64, pub f: u64 }

pub fn t96_read_i(v: T96Slot) -> (r: u64)
    requires v is i,
    ensures  r == get_union_field::<T96Slot, u64>(v, "i"),
{ unsafe { v.i } }
```

`harness/check.py p03 --no-build`:

```
    ok   verus.rs: 10 verified, 0 errors -- matches the pinned obligation count;
         5 TCB items, all contracts identical to spec.md
    FAIL [tcb-unsafe] verus.rs:525 an `unsafe` token sits outside every trusted
         item's body, so no `requires` rule and no verified twin governs it. ...
    2 FAILURE(S)
check.py: FAIL
```

**Control, same command, UNPLANTED** (`.temp/t96/a3_gate_baseline.log`):
`1 FAILURE(S)` — `[build] --no-build: 32 binaries older than the newest source
file`, an artefact of `--no-build` on this tree present in *both* runs. **The
plant adds exactly one failure and it is `[tcb-unsafe]`.**

Restoration verified every run:

```
restored patterns/p03-bounded-stack/verus.rs: 06d8f71f7e9b4de8 -> 06d8f71f7e9b4de8 OK
restored patterns/p03-bounded-stack/spec.md:  3d0d445a5c032011 -> 3d0d445a5c032011 OK
git status --porcelain: ''
```

Verus side, standalone at the pin (`.temp/t96/a1_union*.rs`):

| file | Verus |
|---|---|
| as written, with a real call site | **`2 verified, 0 errors`** |
| `requires v is i` → `requires true` | `1 verified, 1 errors` — *"requirement not met: to access this field, the union must be in the correct variant"* |
| body `v.i` → `v.f` (both fields are `u64`) | `1 verified, 1 errors`, same error |

So the correct-variant obligation is real, load-bearing, and catches reading the
wrong field of the **same type**. TASK_086's `p35` claim is upheld at the pin.

### §A.1b — ⚠ p35 has **NO legal configuration**, not "one blocked route". The comply route is unwritable in *Rust*.

`_scan_unsafe_sites`' own failure message prescribes: *"Put the unchecked
operation inside an `#[verifier::external_body]` item with a `requires`, an
`ensures` and a `#[cfg(slb_twin)]` twin."* That route dies three times over:

1. `check.py::check_trusted_twins`' `_TWIN_BANNED` = `("unsafe", "assume",
   "admit", "assume_specification", "external_body", "external")` — **a twin may
   not contain `unsafe`.**
2. **There is no safe union read in Rust.** `.temp/t96/a2_twin_unwritable.rs`
   with the twin body `v.i`:
   `error[E0133]: access to union field is unsafe and requires unsafe function or block`.
3. So there is no twin, and both branches of `check_trusted_twins` are hard
   failures when the union read is the pattern's **only** `_is_trusted` item:
   with no `verus.twin_justifications` entry it is
   `rep.fail("twin", "... has no verified twin")`; with one it is
   `if justified: if n_twins == 0: rep.fail(...)` — *"a hatch that can be applied
   to the whole of its own stage is an off switch"*. With a **second** trusted
   item (say a `buf_get_unchecked` for the input blob) it degrades to
   `PASS-WITH-BLOCKED-ROWS` **on the row that IS the pattern** — the p15 refusal
   block's own sentence, arriving at p35 by a different door.

This is stronger than the catalogue's *"blocked on one gate rule"*: **two
independent rules block it, and rustc blocks the escape.**

### §A.1c — ⚠⚠ NEW FINDING, and it is why I could see 3 above: **`check.py::_verus` discards the return code, so the gate CERTIFIED a twin rustc refuses to compile.**

```python
def _verus(path, *extra):
    r = subprocess.run([... verus_run.py, path, *extra], ...)
    res = (r.stdout + r.stderr).strip()
    m = re.search(r"(\d+) verified, (\d+) errors", res)
    ...                          # r.returncode is never read
```

Measured:

```
$ ./verus_run.py .temp/t96/a2_twin_unwritable.rs      # twin body is `v.i`
verification results:: 1 verified, 0 errors
error[E0133]: access to union field is unsafe and requires unsafe function or block
verus_run.py exit=1

check.py::_verus would return: (1, 0) | subprocess returncode (IGNORED by _verus): 1
```

On a **real gate run** (`.temp/t96/a3_gate_comply.log`, the `comply` plant):

```
verus.rs: `slb_twin_t96_read_i` verifies against `t96_read_i`'s own contract
          (requires=['v is i']) in 1 lines of checked code
verus.rs: 13 verified, 0 errors with `--cfg slb_twin` -- matches the pinned
          verus.twin_obligations
verus.rs: `slb_twin_t96_read_i` fails when the conjunct `v is i` alone is
          deleted ... -- the checked implementation genuinely needs it
```

— a full twin certificate over source that **does not compile**. This matters
because **`--cfg slb_twin` is compiled by nothing else in the project**, so the
return code is the only signal.

✅ **Clean negative that bounds it — LATENT, NOT LIVE.**
`.temp/t96/b1_verus_exit_census.py`: 25 pinned Verus sources × 2 configurations
= **50 rows, every one `rc=0` and `0 errors`; `rows with rc!=0 or errors!=0: 0`.**

⚠ **I did not fix it**, because the naive fix breaks the mutant batteries (they
*expect* a non-zero exit) and choosing which call sites must assert `rc == 0` is
a gate design decision — PROTOCOL rule 3 territory. **Recommended, not done.**
The narrow fix is **four of the twelve `_verus(...)` call sites** — the ones
whose run is supposed to *succeed*: `check_clause_deletion`'s and
`check_requires_strength`'s unmutated controls, and `check_trusted_twins`'
`base_v = _verus(path)` / `tv = _verus(path, "--cfg", TWIN_CFG)` pair. The other
eight are mutants and deliberately exit non-zero.

### §A.2 — *what honest mistake does the rule prevent, and does a narrower rule prevent the same one?*

The rule's own docstring and TASK_009_REVIEW blocker x1 name the mistake: **an
unchecked operation escaping both the 5a `requires` rule and the 5c-twin
strength rule, because the `unsafe` is somewhere the item-level rules cannot
see** — a `macro_rules!`, a `const` initialiser, an `unsafe impl`, a closure
outside a `fn`, a `common/driver.rs` helper.

That is not the same population as *"`unsafe` inside a verified fn"*. So I
measured whether the second population is safe to admit — i.e. whether Verus
emits an obligation for **every** `unsafe` operation it admits inside a verified
body. **26 distinct constructs across three batteries**, each run with its guard
and again without it:

**ADMITTED, OBLIGATION PRESENT** (removing the guard breaks the file) — 5:

| construct | as written | guard removed |
|---|---|---|
| union field read | `1v/0e` | `0v/1e` *requirement not met … correct variant* |
| union read inside a **closure** | `1v/0e` | `0v/1e` same |
| `str::from_utf8_unchecked` (vstd `assume_specification`) | `1v/0e` | `0v/1e` *precondition not satisfied* |
| `core::hint::unreachable_unchecked` | `1v/0e` | `0v/1e` *precondition not satisfied* |
| `MaybeUninit::assume_init` | — | `0v/1e` *precondition not satisfied* |

**REFUSED BY VERUS OUTRIGHT — cannot ship at all** — 15:
`<[T]>::get_unchecked` (two spellings), `get_unchecked_mut`, `core::ptr::read`,
`core::mem::transmute`, `core::slice::from_raw_parts`, `from_raw_parts_mut`,
`Vec::set_len`, `Box::from_raw`, `NonNull::new_unchecked`,
`u64::unchecked_add` (all `is not supported`); bare `*raw_ptr` and `asm!`
(*"does not yet support …"*); `static mut` read (*"does not yet support"*);
`unsafe impl Send`/`Sync` **inside** `verus!{}` (*"unsafe impl for `Send` is not
allowed"*); `extern "C"` FFI (*"cannot use function … declared outside the
verus! macro"*).

**ADMITTED WITH NO OBLIGATION — exactly one class, and it is x1's own class:**
`unsafe impl Send` **outside** `verus!{}` → `1 verified, 0 errors`. (`unsafe fn`
with a safe body and `unsafe {}` around safe arithmetic are also
obligation-free, but perform no unchecked operation.) **The narrowed rule
refuses it anyway**, because a top-level `impl` is not inside any fn body.

⚠ **A trap I stepped in and am reporting because the project has now hit it
three times:** battery 1 spelled it `core::str::from_utf8_unchecked` → `is not
supported`, and I read that as "Verus refuses it". `.memory` says in so many
words to grep the **inherent** spelling; `str::from_utf8_unchecked` is what
`vstd/string.rs:136` specs. Battery 2 corrects it.

**The narrowed rule, probed** (`.temp/t96/a6_narrow_rule.py`) — *"…or inside the
body of a VERIFIED item: `in_verus`, `external is None`"*:

```
case                               shipped    narrowed    expected
x1_macro_bypass                    REFUSE [2] REFUSE [2]  ok
x1b_macro_called_from_verified     REFUSE [2] REFUSE [2]  ok
unsafe_impl_outside_verus          REFUSE [3] REFUSE [3]  ok
unsafe_in_const_init               REFUSE [2] REFUSE [2]  ok
unsafe_in_external_fn              REFUSE [4] REFUSE [4]  ok
unsafe_outside_any_item            REFUSE [3] REFUSE [3]  ok
p35_union_read                     REFUSE [6] admit       ok
p15_from_utf8                      REFUSE [5] admit       ok
shipped_wrapper                    admit      admit       ok

51 `unsafe` token(s) across the tree's `verus.rs`; 0 file(s) refused by either rule
ALL AS EXPECTED
```

✅ **And the 25th pinned source is covered too**: p01 is the only pattern whose
`verus.obligations` names a second file, and `safe_naive_verus.rs` has **0
`unsafe` tokens**, so both rules pass it (`[] / []`).

So: **the narrowed rule prevents the same honest mistake, at zero cost to the 24
shipped patterns.** (⚠ **51 tokens across 24 `verus.rs`**, not the catalogue's
`47 across 22` — that count predates p19 and p46.)

⚠ **Scope note:** `_scan_unsafe_sites` has a *second* limb — the `seen_common`
loop over `#[path]`-included files — which fails on **any** `unsafe` token with
no host concept at all. Narrowing would touch only the pinned-source limb; the
included-file limb stays absolute, which is right (`common/driver.rs` is
`#[verifier::external]` for R5, so Verus emits no obligation for anything in
it). `a6_narrow_rule.py` models the pinned-source limb only, and says so.

### §A.2b — ⚠ AND THE NARROWED RULE ALONE WOULD DELETE THE STRENGTH CHECK ON THE ROW THAT IS THE PATTERN

`check.py::_mutation_targets` returns `trusted` = every `external_body` item
(derived, nothing can drop out) and `verified` = **`spec.md`'s
`verus.clause_deletion_extra_items`, default `[kernel_item]`**. Measured on the
two plants:

| plant | 5c-req | was the union read's `requires v is i` probed? |
|---|---|---|
| baseline (unplanted) | `4 requires conjunct(s) probed … 1 deleted` | n/a |
| **verified** (`unsafe` in a verified fn) | **`4 … 1 deleted` — IDENTICAL** | **NO. `read_i` appears nowhere in the whole gate log.** |
| **comply** (`external_body` wrapper) | `5 … 1 deleted` | yes, plus 5c-twin's per-conjunct deletion oracle |

So stages 5a, 5c, 5c-req and 5c-twin would all check **nothing** about a
verified `unsafe` host, unless it happens to be the kernel item. That is the
missing companion, and it is one line.

### §A.3 — THE HARD QUESTION: what counts as the TCB?

**Answer: `tcb_items = 2` (`load_input`, `emit`), `_is_trusted = 0`,
`axioms = 0` — and that is TRUE by the closed definition, ALREADY DECIDED, and
NOT a new hole. Do not reinstate the second column.**

**Measured on the two plants, which is the accounting difference in miniature.**
Stage 8's own line, from the three real gate runs:

```
baseline  Miri is REQUIRED because: this pattern has 3 trusted item(s)
          {'verus.rs': ['buf_get_unchecked','stack_get_unchecked','stack_set_unchecked']}
VERIFIED  ... 3 trusted item(s)  {the same three}      <- the union read adds NOTHING
COMPLY    ... 4 trusted item(s)  {... , 't96_read_i'}  <- the wrapper adds ONE
```

So the choice between the two routes **is** the choice of what the TCB column
says, and the gate already prints it.

The published column is `tcb = [i for i in item_list if i.external]`, so it
counts infra too: the p03 plant printed *"5 TCB items"* for 5 `external_body`
items. A pattern whose only `external_body` items are `load_input`/`emit`
publishes **2** — and `.memory/04-verus.md` **predicted exactly this number**:
*"a verified `raw_ptr` kernel needs zero project-local trusted items, so it would
publish `tcb_items = 2` — fewer than p01's array sum … Decide how such a pattern
is counted BEFORE building one."* TASK_055_REVIEW already decided it: **one
number + prose + the U-license / V-gap / infra classification, and `tcb_reach`
was rejected as undecidable for the same reason the 402-site census killed the
two-number proposal.** Applied here: `2`, both **infra**, zero U-license, zero
V-gap, with prose saying how the rung reaches the payload.

**But the two rows are NOT the same case, and they differ exactly here.** This
is the sharpest thing I found:

| | **p35** — `unsafe { v.i }` | **p15** — `str::from_utf8_unchecked` |
|---|---|---|
| who licenses the operation | **Verus's own type-system encoding**. `union` is *not in vstd at all* (318 `union` hits are all `Set::union`) | **a vstd `assume_specification`** — `vstd/string.rs:136`, `requires valid_utf8(v@) ensures res.spec_bytes() =~= v@` |
| is a hand-written `ensures` about real Rust semantics in the chain? | **no** — no more than for `v[i]` | **yes**, and it is verbatim what a local wrapper would write |
| honest TCB | **2, both infra** — the same *kind* of zero all 24 patterns already publish for Verus's encoding of `v[i]` | 2 by the letter, **and one relocated axiom the column cannot see** |
| Miri backstop | not derived-required; the pattern can pin `miri.required` | **required**, and `check_miri` would say it is not |

> ⚠ **THE DISCRIMINATOR IS CATALOGUE PROBE 4's GREP WITH THE OPPOSITE POLARITY,
> AND NOBODY HAS STATED IT: a vstd spec for the operation is a REASON TO REFUSE,
> not a reason to admit.** If vstd specs it, the licence is an upstream axiom
> `_axiom_items` structurally cannot see (the sixth route). If vstd does *not*
> spec it and Verus admits it anyway, the licence is the verifier's own
> encoding, and `tcb_items` is honest.

### §A.4 — the acceptance test, and the answer to *"which single command?"* is **THERE ISN'T ONE**

The chain a reader's number comes down is **four** commands:

```
harness/check.py pNN                 -> results/gate/pNN-*.json
synthesis/licence.py --emit synthesis/licence.json
synthesis/synthesize.py              -> results/synthesis.md
```

and every acceptance test written so far has covered a **prefix**. That is the
test that was missing, so I built it:
**`.temp/t96/a7_source_to_published.py <verified|comply>`** — snapshots the
pattern's sources *and* every `results/gate/*.json`, `synthesis/licence.json`
and `results/synthesis.md` by bytes; plants; runs the **full** gate (no
`--no-build`, so a real record is written), then `licence.py --emit`, then
`synthesize.py`, in that order; diffs the published file; **exits 1 if it is
byte-identical** (the plant did not reach the number a reader quotes); restores
everything in a `finally:` and re-derives the published file from the restored
records; then asserts `git status --porcelain` is empty.

**It was RUN and it fired** — see "§D — sweep results", *THE ACCEPTANCE TEST WAS
RUN*: the plant moves **8 lines** of `results/synthesis.md`, including §3's
`obligations` column (`9 → 10`) and the verdict (`PASS → FAIL`).

### §A — THE RECOMMENDATION, in the form a reviewer can attack

**Narrow `_scan_unsafe_sites` — but only behind a DECLARED hatch, and the
declaration must force three things the gate can enforce.** Undeclared `unsafe`
outside a trusted body keeps failing **exactly as today**, so the false-positive
surface is zero and no shipped pattern moves (measured: 0 of 24).

1. **`verus.verified_unsafe[<src>][<fn>] = "<why>"`** in the `slb-contract`
   block; the gate `rep.shout`s the `why` every run (the expensive-hatch pattern
   the project already uses twice).
2. **The declared host is added to `_mutation_targets`' `verified` list**, so 5c
   and 5c-req probe its clauses. Without this the row that *is* the pattern is
   probed **zero** times (§A.2b, measured).
3. **The declaration forces `miri.required` derived-true**, so `check_miri`'s
   no-trusted-item branch cannot fire on it. This does not *close* the sixth
   route — nothing decidable can, and the "vstd relied upon" column was refuted
   by census — but it removes the route's operative harm, which is a skipped
   Miri over a proof resting on an upstream axiom.

The `why` must answer the polarity question above: **does vstd spec this
operation?** If it does (p15), the licence is upstream and the row should stay
refused. If it does not and Verus admits it anyway (p35), the licence is the
verifier's own encoding and the TCB number is honest.

**Outcome if adopted: p35 becomes buildable (type confusion — the only bug class
absent from the tree). p15 stays refused, on its own named condition.**

**THE CASE FOR LEAVING IT ALONE, AT FULL STRENGTH — a reviewer should weigh
these before my recommendation:**

- ⚠⚠ **RECAP's own condition is not met.** *"Softening that rule is admissible
  only AFTER this route is closed."* My proposal neutralises the route's harm;
  it does not close it. If the manager reads that sentence literally, **the rule
  stands and p15 and p35 stay refused.**
- ⚠ **TASK_055_REVIEW's named residual gets its first real instance** — *"a
  legitimate zero-trusted-item pattern and the known macro bypass produce the
  same gate output."* No legitimate one exists today; narrowing creates the
  first. ⚠ **But I have to weaken my own bullet here, because the probe says so:
  the residual is about stage 5c-twin's *shout*, and the two cases are still
  distinguishable at the VERDICT level** — the macro bypass keeps failing
  `[tcb-unsafe]` under the narrowed rule (`x1_macro_bypass`, `REFUSE [2]` in
  both columns), while a legitimate pattern would pass. So this argument is
  softer than it first looks, and I am not going to pretend otherwise.
- ⚠ **The twin regime goes idle on the interesting row.** p35 would have
  `_is_trusted = 0`, so 5a, 5c-req and 5c-twin certify nothing about the union
  read; only 5c's clause deletion would, and only because of consequence 2.
- ⚠ **My "Verus always emits an obligation" result is ENUMERATIVE, not
  structural** — 26 constructs, and I could not find a 27th that breaks it.
  `unsafe impl Send` outside `verus!{}` is one obligation-free `unsafe`, and the
  narrowed rule refuses it *because a top-level `impl` is not inside a fn body*,
  which is an accident of where Rust puts the construct rather than a property
  of the rule. A future Verus that supports raw-pointer deref, `asm!` or FFI
  inside `verus!{}` would have to be re-probed.
- ✅ **And the honest cost of doing nothing is exactly two rows**, one of which
  (p15) is refused on other grounds anyway. **"Leave it alone" is a complete
  answer and I would not argue against it hard.**

### §B — "Owed" 0's sixth route: **it is live in 24 of 24 and MATTERS in none of them. Clean negative.**

Census over all 24 gate records:

```
p01..p47   miri.required=True  ran=True  n_trusted in [1..5]  n_axioms=0
```

**No pattern reaches `check_miri`'s `if not why_required` branch.** `why_required`
is non-empty in every row because `n_trusted >= 1`.

The *literal* route is live everywhere, and more widely than RECAP records:
`Vec::<T,A>::len` (`std_specs/vec.rs:93`), `Vec::as_slice` (`:236`) and — the
one nobody has named — **`<usize as SliceIndex<[T]>>::index`
(`std_specs/slice.rs:20`), which is what licenses `v[i]`, i.e. the body of every
`slb_twin_*get_unchecked` in the tree** — are all vstd `assume_specification`s.

Counted through **`check.py::exec_code`** (comments, `#[cfg]`-excluded items,
`spec fn`/`proof fn`, ghost clauses and ghost statements all blanked), and
excluding `@.len()`, which is `Seq::len` and *not* a vstd
`assume_specification`: **24 of 24 `verus.rs` make an EXEC `.len()`/`.as_slice()`
call — 52 sites, 2 per pattern except p02 and p14 at 4.** RECAP says
*"22 of 23"*; it is **24 of 24**. ⚠ A naive `\.len\(\)` grep gives 13–50 per
file and is wrong — most of those are ghost `v@.len()`.

So the answer to *"does it MATTER"* is: **not today, and it cannot until a
pattern has zero `_is_trusted` items — which today requires either narrowing
`_scan_unsafe_sites` (§A) or a fully-vstd-specified R5.** The two items are the
same item. The reachability half is already demonstrated and reviewed
(TASK_084_REVIEW major 3, route G: `TCB items (2)`, the sentence printed
verbatim, published TCB total 90 → 89), so I did not re-run it.

**What I did instead** is make the branch stop overclaiming — §C below.

### §C — the smaller items

**Major 2 (`synthesize.py` §3 prose) — ⚠ ALREADY LANDED. The task file's premise
is false.** `TASK_096.md` says *"the `22` → computed `_n_named` fix landed; the
overclaim did not."* All three of TASK_084_REVIEW major 2's overclaims are
corrected in `synthesis/synthesize.py` **and published in
`results/synthesis.md`** at HEAD:

- *"A TCB item is **usually** an `external_body` wrapper … since TASK_084 a
  bodied `#[verifier::external_fn_specification]` also counts"*;
- *"the twin-and-`(a)/(b)/(c)` requirement does NOT cover every published item:
  `load_input` and `emit` (24 and 24 …) are `external_body` with no `ensures`"*;
- *"reading `0` does NOT mean this tree rests on no hand-written axiom — an
  earlier version of this paragraph claimed exactly that and it is FALSE"*, plus
  *"A USED vstd `assume_specification` declares nothing locally and is invisible
  here too (RECAP 'Owed' 0, sixth route)."*

`git log -L 903,950:synthesis/synthesize.py` puts it at **`6e36f31`** —
*"TASK_088: p19's corrections, and the `#[path]` walk now feeds all three
detectors"*. **Nothing to do; I changed nothing here.**

**Major 3 (`check_miri`'s `if not why_required`) — landed.** The `ok` now reads
*"declares NO **PATTERN-LOCAL** trusted item and NO **PATTERN-LOCAL**
hand-written axiom, so there is no trusted `ensures` **OF THIS PATTERN'S OWN**
… Miri not required **by the derived policy**"*, and the branch adds a
`rep.shout` naming the sixth route and telling the author to pin
`miri.required: true`. A 40-line comment records why it is not a failure and why
`_axiom_items` is **not** widened to "vstd specs used" (the refuted column).
`out` gains `local_only: True`. **Zero patterns reach the branch, so zero
verdicts move** — stated as the acceptance argument rather than as a hope.

⚠ **Note for the next reviewer, and it does not enter the running count because
it is a REVIEWER's sentence rather than the manager's.** TASK_084_REVIEW major 3
says *"`miri.required: true` cannot save a future pattern: with
`n_trusted == 0 and n_axioms == 0` the `required is False` FAIL guard cannot
fire, and the branch returns before it."* The second clause is true and
trivially so. **The headline, read as "pinning `miri.required: true` cannot
force Miri on a zero-trusted-item pattern", is FALSE**:

```python
    if cfg.get("required"):
        why_required.append("spec.md sets miri.required")   # runs FIRST
    if not why_required:
        ... return                                         # so this is skipped
```

and `git log -S 'spec.md sets miri.required' -- harness/check.py` puts that line
at **`98da583` (TASK_010)**, i.e. it was already there when the review ran. The
sentence is only true of the FAIL guard. That is why my shout tells the author to
pin the flag — it is the one lever that works. **Sentence claimed only where the
code supports it; a reviewer should re-derive both halves.**

**"Owed" 30 (`check_marginal_ir` docstring) — landed.** The bullet that read
*"The term is `whole`-mode only … `isolated` is not merely small, it is exactly
invariant"* now reads:

```
-O3 isolated  invariant (0.00 across every probe to date)
-O3 whole     moves by 7 per per-call stack `memset`
-O0           moves in BOTH modes
```

with the note that TASK_077's evidence is **all `-O3`**, that p46 is the
**fourth** pattern (p03, p04, p38, p46), and that a pattern's step is
`7 × (per-call stack arrays)` — p46 `memset`s two and moves by `−14`. Three
downstream sentences corrected to match, including *"quote the `-O3 isolated`
one"*.

**The 39 citations.** `.temp/t96/c4_rot_audit.py` re-resolves each cited line
against HEAD's `check.py`. **Every one had rotted.** A sample:

| citation | prose named | HEAD's function at that line |
|---|---|---|
| `check.py:2253-2257` (`limbs.py`, "as of TASK_056") | the 5a pin comparison | `check_build` |
| `check.py:2770` (p05, p08, p17) | `check_verus_contract` | `check_marginal_ir` |
| `check.py:1756` (p10 ×2, p12) | `check_checksums` | `idiom_audit_lines` |
| `check.py:1262` (p04, p09 ×2, p27) | `idiom_audit` | `idiom_problems` |
| `check.py:752` (p09 ×2) | `exec_code` | `check_selftests` |
| `check.py:495` / `:469` (p12 ×3, p13 ×2) | `inputs_of` | `sha256_file` |
| `check.py:1976` / `:2069-2075` (p16, p47) | `check_marginal_ir` | `_fv` |
| `check.py:4069` (p13 ×2) | `check_trusted_twins` | `check_call_site` |
| `check.py:5108` (p18) | `check_sanitizers` | `check_trusted_twins` |

**⚠⚠ AND I GOT TWO OF THE REPLACEMENT NAMES WRONG ON THE FIRST PASS. Both are
corrected, and the lesson is worth more than the fix:**

- `patterns/p12-strcat-fixed/NOTES.md` quotes *"which rungs an entry scopes to
  lives in its English"*. That sentence is **`spelling_matches`' docstring**.
  The prose said `idiom_audit` (wrong) and the rotted line resolved to
  `idiom_problems` (also wrong). **I inherited the second error by resolving the
  line instead of the sentence.** → `check.py::spelling_matches`.
- `patterns/p27-handle-table/NOTES.md`: **both** `idiom_problems` and
  `idiom_audit` iterate `("required", "forbidden")`, so the line does not
  disambiguate — but the surrounding claim is about `spellings`, which only
  `idiom_audit` computes. **The prose was right and the line was not**, and my
  first pass "corrected" it to `idiom_problems`. → `check.py::idiom_audit`.

> ⚠ **Resolving a rotted citation by *what is at that line today* is exactly as
> wrong as trusting the line. Grep for the SENTENCE, or for the code the prose
> describes.** Every other replacement was re-verified this way: the
> *"every `.rs` with a `verus!` block must be pinned"* rule really is inside
> `check_verus_contract`; `_TICK.findall` really is in `idiom_audit`;
> `sorted(hung_cells)[0]` really is in `_confirm_hang`; *"re-denominate
> `work_per_call`"* really is in `check_marginal_ir`;
> `norm_clause(twin.sig)` really is in `check_trusted_twins`.

**⚠⚠ THE `p09` CONTRACT HASH MOVED, AS THE TASK FILE PREDICTED — DISCLOSED
HERE:**

Computed with `check.py::read_contract`'s own regex (⚠ **not** a hand-written
`\n``` ` one — that gives a different digest because the block's trailing
newline is inside the captured group):

```
patterns/p09-bitset/spec.md   contract_sha256
  HEAD    c391270c673f2c322892e863b99747dec4f9f68153f999ae4a047bb9e1e540fd
  working 0a37c0cd1418ae4d5e665c090365cb456dafbf8d1085149ce174a27ff2de9130
```

and `results/gate/p09-bitset.json` now records `0a37c0cd1418…`, i.e. the gate
agrees.

**Structural diff of the parsed contract, HEAD vs working tree: 132 leaves, key
sets identical, exactly ONE leaf changed — `.idiom.why` — and the whole of the
change is the two citations:**

```
  .idiom.why
    - `check.py`'s `exec_code`   (`check.py:752`)   + `check.py::exec_code`
    - `check.py`'s `idiom_audit` (`check.py:1262`)  + `check.py::idiom_audit`
```

**No `required`, no `forbidden` spelling, no `identity`, no obligation count, no
`miri` key moved.**
✅ **I checked the other four spec.md files I touched and their fences are
byte-identical** (`p04 af9ffbb3…→af9ffbb3…`, `p12 d0c15cce…→d0c15cce…`,
`p13 2f89456c…→2f89456c…`, `p16 944bf05b…→944bf05b…`) — those citations all sit
in the prose *outside* the fence.

⚠ **`results/tables/p09-bitset.md` is GENERATED** from `spec.md` by
`harness/report.py`, so the fix went in the generator's input and the table is
regenerated — the artefact-vs-generator skew PROTOCOL rule 6 warns about.

---

## Problems

### ⚠ 9 line references in 6 files are NOT fixed, and 8 of them are in files the task file's own cost model missed

`TASK_096.md` says the measurement-hashed set is *"every rung `.rs` and
`c/kernel.{c,h}`"*. **`harness/measure.py::measurement_sources` also globs
`pdir/model.py` and `pdir/inputs/gen.py`** — verified against a real record:

```
$ python3 -c "...json.load(open('results/p13-strncpy-trunc.json'))['source_sha256']..."
['patterns/p13-strncpy-trunc/inputs/gen.py', 'patterns/p13-strncpy-trunc/model.py']
```

So a **comment-only** citation fix in
`p12/inputs/gen.py` (1), `p13/inputs/gen.py` (1), `p13/model.py` (2),
`p16/model.py` (3 — two `check.py:625` and one bare `:632`),
`p38/inputs/gen.py` (1) costs a **re-measure of p12, p13, p16 and p38**, which
would churn published wall-clock prose. **I left them and am reporting rather
than deciding** — batch them into the next re-measure. The ninth is
`.memory/06-catalogue.md`'s `check.py:1249`, which is **manager-only**;
replacement text is in "Memory updates" 5b.

**Totals, so the arithmetic is checkable:** 43 removed + 9 left = **52 live
`check.py` line references** at HEAD, of which the `check\.py:[0-9]` grep the
task file used sees only 39.

### ⚠ A PROCESS MISTAKE I MADE, REPORTED BEFORE IT COULD BE DISCOVERED

**I edited `harness/check.py` while the sweep was running**, between p08 and p09
— a one-line docstring lead-in (*"three patterns at ±7"* → *"FOUR patterns"*,
which the bullet under it already corrected). `harness/*.py` is hashed into
every gate record's `source_sha256`, so:

```
p01..p08 recorded  harness/check.py be5ecafbb68c06dd
live after the edit                 96f51a28a93bdc16
```

— and the sweep stopped being *"all 24 against ONE `check.py`"*, which is the
whole reason a sweep is paid for. **I then did it a second time**, fixing two
mis-resolved function names in `patterns/p12-strcat-fixed/NOTES.md` after p12
had already been gated.

**Repair, and it is better than the hand-tracking that would have hidden it:**
`.temp/t96/d2_gate_stale.py` **recomputes every gate record's recorded
`source_sha256` against the live tree** and names the patterns to re-gate —
there is no `--check-stale` for `results/gate/`, and this is one.
`.temp/t96/d2_resweep.sh` drives off it, then redoes `licence.py --emit` and
`synthesize.py` in that order, re-runs `measure.py --check-stale`, and asserts
**(a) zero stale gate records and (b) one `check.py` hash across all 24**.
Result below.

**Lesson, and it belongs in `.memory/`: once a sweep starts, nothing under
`harness/` or `patterns/` may be touched until it ends — and there was no check
that would have caught it, which is why `d2_gate_stale.py` exists.**

### The `[build]` failure in the plant logs

`check.py --no-build` fails `[build]` on this tree with or without a plant
(shown in the baseline control). I neutralised the *plant's* contribution by
restoring mtimes after planting; the residual is a property of the tree's
existing binaries and is present in both runs, so the plant's delta is exactly
one failure.

### Not fixed: `_verus`'s return-code blindness

Reported above, latent not live (50/50 rows clean). The fix is a gate design
decision — the mutant batteries deliberately produce non-zero exits — so it
needs the manager, not me.

---

## Unsure / not done

- ⚠ **I did NOT change `_scan_unsafe_sites`.** §A is a recommendation with
  demonstrations; the narrowed predicate lives only in
  `.temp/t96/a6_narrow_rule.py`, which imports `check.py` read-only.
- ⚠ **I did not build a zero-`_is_trusted` pattern end to end.** The evidence
  that such a pattern ships green with *"Miri not required"* is
  TASK_084_REVIEW's route G, which is reviewed; I cite it rather than re-running
  it. My p03 plants both keep p03's three real trusted items, so they do **not**
  demonstrate the `n_twins == 0` hard-fail — that limb of §A.1b is a code read
  of `check_trusted_twins` (`if justified: if n_twins == 0: rep.fail`), and I say
  so.
- **My "Verus emits an obligation for every admitted `unsafe`" result is
  enumerative** (18 constructs). Not probed: `asm!`, `extern "C"` FFI,
  `unsafe impl` of `GlobalAlloc`/`Allocator`/`Sync`, `MaybeUninit::assume_init`,
  `NonNull::new_unchecked`.
- **`get_union_field::<T,U>(v,"i")` in an `ensures` is mis-split by the pin
  machinery.** `vparse` splits clauses on top-level commas and the turbofish
  generic list splits with them: the gate reported
  `['r == get_union_field::<T96Slot', 'u64>(v, "i")'] != pinned [...]`. Legal
  Verus, mis-split pin. Minor, and it would bite p35 for real.
- **I did not re-measure anything.** No `measure.py <pattern>` run; `build.py`
  and `asm.py` are byte-identical to HEAD.
- **`.temp/t96/probe/*.rs` and `.temp/gate-partial/*.partial.json` are left in
  place**; both are regenerated by the committed generators
  (`a4_probe_battery.py`, `a5_probe_battery2.py`, `a3_plant.py`). Binaries: none
  produced outside the gate's own `.temp/build`.

---

## Memory updates

**None written — `.memory/` is manager-only.** Durable facts for the manager to
land, in priority order:

1. **`check.py::_verus` discards the return code** (`.memory/04-verus.md`): a
   file that Verus verifies and rustc then rejects returns `(N, 0)`. Measured on
   a real gate: a `#[cfg(slb_twin)]` twin with `error[E0133]` was **certified**.
   Clean negative: 50/50 shipped rows `rc=0`. **Latent, not live.**
2. **p35 has no legal configuration, for two independent reasons**
   (`.memory/06-catalogue.md`, p35 row): `_scan_unsafe_sites` blocks the verified
   route, and `_TWIN_BANNED` + `E0133` block the comply route, ending in
   `n_twins == 0` (hard fail) or `PASS-WITH-BLOCKED-ROWS` on the row that is the
   pattern.
3. **The polarity of catalogue probe 4** (`.memory/06-catalogue.md`): *a vstd
   spec for the operation is a reason to REFUSE a verified `unsafe`, not a reason
   to admit it* — it means the licence is an upstream axiom the TCB column cannot
   see. This is what separates p35 (verifier-native, `union` absent from vstd)
   from p15 (`vstd/string.rs:136`).
4. **`_mutation_targets` does not reach a verified `unsafe` host**
   (`.memory/04-verus.md`): `verified` is `verus.clause_deletion_extra_items`,
   default `[kernel_item]`. Measured: 4 conjuncts probed with the plant, 4
   without.
5. **`measurement_sources` includes `model.py` and `inputs/gen.py`**
   (`.memory/05-layout.md` / PROTOCOL rule 6's cost table): there is no cheap doc
   fix in those either.
5b. **The one `.memory/` citation, with the replacement text ready.**
   `.memory/06-catalogue.md`'s p36 block reads *"**`check.py:1249` is not the
   checksum rule** — it is a selftest for `idiom_problems`"*. That line now
   resolves to **`idiom_problems` itself**, not to its selftest; the selftest is
   in **`check.py::check_selftests`** (it prints
   `idiom_problems: {label}: got …, want …`). ⚠ **The bullet is a warning ABOUT
   citation rot whose own citation has rotted for the third time** — it says so
   about `:1440-1476` already. Replacement: *"`check.py::check_selftests` carries
   the `idiom_problems` selftest ('a bare string is not a declaration'); the real
   checksum rule is `check.py::check_checksums` (stage 2)"*, **with no line
   number.**
6. **Counts to refresh**: `51` `unsafe` tokens across `24` `verus.rs` (not
   `47`/`22`); the sixth route's literal form is live in **24 of 24** (not
   22 of 23), including via `<usize as SliceIndex<[T]>>::index` at
   `std_specs/slice.rs:20`.
7. **TASK_084_REVIEW major 2 is CLOSED** at `6e36f31`; RECAP and `TASK_096.md`
   both still list it as open.
7b. ⚠ **`results/tables/` is regenerated by nothing, and `p46-bignum-mac.md` has
   been stale since TASK_092** (`.memory/05-layout.md`): 60 lines, including a
   pre-re-measure wall-clock table and a **pre-correction contract digest**
   (`bddd7e032a72`, against the shipped `43925b2955e0`). Not `check.py`, not the
   sweep, not `synthesize.py`, and not `measure.py --check-stale` looks at it.
   **Add `harness/report.py pNN` to the sweep recipe**, or a staleness check.
8. **Two process rules, both earned the hard way in this task**
   (`.memory/00-environment.md` or PROTOCOL):
   *(a)* **once a sweep starts, nothing under `harness/` or `patterns/` may be
   touched until it ends** — I broke it twice and there was **no check that
   would have caught either**; `.temp/t96/d2_gate_stale.py` is the missing one
   (a `--check-stale` for `results/gate/`) and is worth promoting into
   `harness/`.
   *(b)* **when a citation has rotted, resolve it by grepping for the SENTENCE
   or the code the prose describes, never by reading what is at that line
   today.** I got two of 43 wrong by doing the latter, and in one of them the
   original prose had been right all along.

---

## The five contradictions, counted (274 → 279)

- **#275** — `TASK_096.md` §C: *"the `22` → computed `_n_named` fix landed; the
  overclaim did not."* **False.** All three overclaims are corrected in
  `synthesize.py` and published in `results/synthesis.md`; `git log -L` puts the
  fix at `6e36f31` (TASK_088).
- **#276** — `TASK_096.md`'s cost model: *"every rung `.rs` and
  `c/kernel.{c,h}`"* is the measurement-hashed set. **Incomplete** —
  `measurement_sources` also globs `pdir/model.py` and `pdir/inputs/gen.py`,
  which is where **8 of the 52 live line references** sit — the reason they are
  the ones I left alone.
- **#277** — the catalogue's p35 row: *"blocked on the same gate rule as p15 —
  fix `_scan_unsafe_sites` and TWO rows unblock."* **p35 is blocked by TWO
  independent rules**, and the second (`_TWIN_BANNED` + `E0133`) is not a gate
  policy at all — it is Rust. Fixing `_scan_unsafe_sites` alone unblocks p35
  only because it makes the comply route unnecessary.
- **#278** — RECAP: *"the literal sixth route has been live in 22 of 23 patterns
  all along."* **24 of 24**, and it was 23 of 23 when that was written — no
  pattern in the tree has ever lacked an exec `.len()`/`.as_slice()` call. The
  widest instance is `v[i]` itself (`std_specs/slice.rs:20`), not `bytes.len()`.
- **#279** — the catalogue: *"47 `unsafe` tokens in 22 `patterns/*/verus.rs`."*
  **51 across 24**, counted the way the gate counts (`blank_noncode`).
