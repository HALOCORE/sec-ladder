# TASK_096_REVIEW — report

**Role: research reviewer.** Scratch `.temp/r96/` only. **No `git add`/`git
commit`.** No edit to `.memory/`, `pilot/`, `harness/build.py`,
`harness/asm.py` — or to **any** tracked file. `harness/measure.py` not run.
Verus only via `./verus_run.py`, single-file.

⚠ **I did NOT run `harness/check.py` at all.** Every gate stage I exercised, I
exercised by importing `harness/check.py` and calling the stage function
directly against a **synthetic pattern dir under `.temp/r96/`**, with a
hand-built contract dict. So `results/gate/` was never rewritten, **no
`git checkout -- results/gate/` was needed**, and `git status --porcelain` is
empty at the end exactly as it was at the start. **No plant into `patterns/`
was made.**

**PROTOCOL rule 2 running count: 279 → 286.** Seven measured contradictions,
itemised at the end. Four are of the report; two are of durable facts the
report queued for `.memory/`; one is of a premise in `TASK_096_REVIEW.md`
itself.

---

## THE DECISION, FIRST

> *Should `_scan_unsafe_sites` be narrowed so a Verus-discharged `unsafe` may
> live in a verified body?*

**Not as specified. The narrowed predicate in `.temp/t96/a6_narrow_rule.py` is
UNSOUND, and I have an executed end-to-end demonstration: a file that Verus
certifies `2 verified, 0 errors`, that has ZERO `_is_trusted` items, that the
narrowed rule ADMITS and the shipped rule REFUSES, and whose compiled binary
performs an out-of-bounds read.** The defect is one word wide — the predicate
hosts an `unsafe` token in **any** enclosing verified item instead of the
**innermost** enclosing item — and I verified that the one-word fix repairs it
while preserving all nine of the report's own cases and both target rows.

With that fixed, the narrowing is *defensible* but still under-specified: its
vstd-polarity discriminator (p15 refuse / p35 admit) is **not enforceable by
any gate check**, and the human-judgement backstop the TCB policy depends on
(`_check_trusted_arguments`) **silently owes nothing** on exactly the shape the
hatch creates. Those need a fourth consequence, not a `why` string.

**"Leave it alone" remains a complete answer and it now costs exactly ONE
buildable row** — `p35` — because §C's `n_twins == 0` limb reproduces
(executed, below) and p15 is refused on grounds this hatch does not touch.

---

## Findings

### BLOCKER 1 — the narrowed predicate admits an `unsafe` operation Verus never looks at, and the binary reads out of bounds

`.temp/t96/a6_narrow_rule.py::hosts_narrowed` adds, as a host,
**every** item with `external is None and in_verus`, and `scan` then accepts a
token if *any* host span contains it. `harness/check.py::_scan_unsafe_sites`
does the same span test today, but only over `_is_trusted` items, so nesting
cannot help an attacker there.

`vparse.parse` **does** see items nested inside a `fn` body (measured — see
clean negative CN-1), and Verus **admits** `#[verifier::external]` on such a
nested item. So:

`.temp/r96/probe/n3_composite.rs`

```rust
verus! {
pub fn kernel(v: &[u8], i: usize) -> (r: u8)
    requires i < v@.len(),
{
    #[verifier::external]
    fn raw(v: &[u8], i: usize) -> u8 { unsafe { *v.get_unchecked(i + 1000) } }
    #[verifier::external_body]
    fn wrap(v: &[u8], i: usize) -> u8 { raw(v, i) }
    wrap(v, i)
}
```

Measured:

```
$ ./verus_run.py .temp/r96/probe/n3_composite.rs
verus exit=0
verification results:: 2 verified, 0 errors

  'kernel' external=None                         trusted=False
  'raw'    external='verifier::external'         trusted=False
  'wrap'   external='verifier::external_body'    trusted=False
  'main'   external=None                         trusted=False
shipped : [(12, [])]          <- host NONE  -> rep.fail(tcb-unsafe)
narrowed: [(12, ['kernel'])]  <- host kernel -> ADMIT
```

and the compiled artefact:

```
$ ./verus_run.py --compile .temp/r96/probe/n3_composite.rs -o .temp/r96/probe/n3_bin
verification results:: 2 verified, 0 errors      (compile exit=0)
$ .temp/r96/probe/n3_bin
thread 'main' panicked at .../n3_composite.rs:12:52:
unsafe precondition(s) violated: slice::get_unchecked requires that the index
is within the slice
...
Aborted                              run exit=134
```

**Why every backstop misses it, checked one at a time in `harness/check.py`:**

- `_is_trusted` is **False for both** helpers: `raw` is `verifier::external`
  (fails the `item.external != "verifier::external_body"` guard); `wrap` is
  `external_body` with **no `ensures`** and **no `unsafe` token in its own
  body**, so it fails the disjunct too.
- `_check_trusted_unsafe` (5a) opens `for i in tcb: if not _is_trusted(i):
  continue` — **skips both**.
- `check_trusted_twins` reaches `if not trusted:` and `rep.shout(...)` +
  `continue` — no failure, no twin required.
- `_check_trusted_arguments` iterates `trusted_by_src`, which is only populated
  *after* that `continue` — **no written argument is owed**.
- `_check_axiom_decls` sees no `assume`/`admit`/`assume_specification`.

So under the narrowed rule this ships with `_is_trusted = 0`, `axioms = 0`, a
green Verus certificate, and an out-of-bounds read that rustc's own UB check
catches at run time. **That is TASK_009_REVIEW blocker x1 and
TASK_003_REVIEW's blocker, re-opened by the narrowing itself** — and the
report's battery cannot see it, because none of its nine cases contains a
nested item.

**Honest-mistake plausibility:** moderate-to-high. Nesting a helper inside the
function that uses it is ordinary Rust; marking a helper Verus cannot handle
`#[verifier::external]` is the project's own idiom (`common/driver.rs` is
exactly that); and the hatch would already have been *declared* for `kernel`,
so the nested token rides along for free.

**The fix, verified** (`.temp/r96/r3_innermost.py`) — host on the **innermost**
enclosing parsed item:

```
case                               shipped        any-encl (report)    innermost
x1_macro_bypass                    REFUSE [2]     REFUSE [2]           REFUSE [2]
x1b_macro_called_from_verified     REFUSE [2]     REFUSE [2]           REFUSE [2]
unsafe_impl_outside_verus          REFUSE [3]     REFUSE [3]           REFUSE [3]
unsafe_in_const_init               REFUSE [2]     REFUSE [2]           REFUSE [2]
unsafe_in_external_fn              REFUSE [4]     REFUSE [4]           REFUSE [4]
unsafe_outside_any_item            REFUSE [3]     REFUSE [3]           REFUSE [3]
p35_union_read                     REFUSE [6]     admit                admit
p15_from_utf8                      REFUSE [5]     admit                admit
shipped_wrapper                    admit          admit                admit
r96_nested_external_fn             REFUSE [8]     admit                REFUSE [8]   <-
r96_composite_oob                  REFUSE [12]    admit                REFUSE [12]  <-
r96_nested_extbody                 admit          admit                admit
r96_macro_in_verified              REFUSE [8]     admit                admit
```

### MAJOR 2 — the recommended `_verus` fix is scoped wrong, and it leaves a byte-for-byte duplicate of the same bug in the same file

Report §A.1c: *"The narrow fix is **four of the twelve** `_verus(...)` call
sites."* Both numbers are wrong and the omission matters.

```
$ grep -c "_verus(" harness/check.py
14
```
of which `def _verus` (4126), a docstring mention (4909) and `region_in_verus`
(5820) are not calls — **11 call sites, not 12.** Enclosing functions, computed:

| site | function | kind |
|---|---|---|
| 4195 | `_verify_function` | **expects success** — the report omits it |
| 4380 | `check_clause_deletion` | control (report names it) |
| 4398, 4446 | `check_clause_deletion` | probe / mutant |
| 4619 | `_run_taut_battery` | probe |
| 4733 | `check_requires_strength` | control (report names it) |
| 4827 | `check_requires_strength` | mutant |
| 5298, 5299 | `check_trusted_twins` | controls (report names them) |
| 5407 | `check_trusted_twins` | mutant |
| 7481 | `_probe_selftest` | **expects success** — the report omits it |

That is **6 success-expecting sites, not 4**, and 5 probes/mutants, not 8.

⚠ **And `_verus` is not the only return-code-blind reader of `verus_run.py`.**
`harness/check.py::check_verus_contract` runs it **inline** with the identical
regex and never reads `r.returncode` — and that is the run that produces every
gate record's `verified`, `errors` and `tcb_items`. `harness/limbs.py::verus`
is a third copy. **A manager who implements the recommendation verbatim fixes
`_verus` and leaves the primary certificate site untouched.**

**Bound, in the report's favour:** `harness/build.py::build_verus` invokes
`verus_run.py --compile` and *does* check `rc`, and all 24 patterns' pinned
obligation sources are exactly `verus.rs` / `safe_naive_verus.rs`, both of
which are built cells (measured across all 24 `slb-contract` blocks). So the
inline site is backstopped by stage `[build]` — the diagnostic points at the
wrong stage, but the gate does fail. **`--cfg slb_twin` is compiled by nothing,
so the report is right that the twin run is the unbackstopped one.** The review
task's hypothesis *"if there is a second site, that is a bigger finding than
the first"* **does not land**: the second and third sites exist, but they are
smaller, not bigger.

⚠ **The line numbers in the table above are HEAD-relative and WILL rot** —
they are there only as a key into a `grep`, per `.memory/02-bench-rules.md` the
function names are the citation. Re-derive with
`grep -n "_verus(" harness/check.py`.

**A better fix than the one recommended, and it is safe at all 12 sites:** flag
`returncode != 0` **only when the summary parsed AND `errors == 0`**. At every
mutant site, `errors == 0` already triggers `rep.fail` —
`check.py::check_clause_deletion`, `check.py::check_requires_strength` and
`check.py::check_trusted_twins` each read `if mv is not None and me == 0:
rep.fail(...)` (and `dv`/`de` in the twin case) — so a mutant can never be
turned red by this; and at `check.py::_verify_function` the
"unnameable"/"ambiguous" answers return `nv is None`, which the condition
excludes.

### MAJOR 3 — "latent, not live" understates it: the shape is NOT union-specific, and the gate's own `_TWIN_BANNED` rule is what produces it

The report exhibits one instance and calls it *"a verified-but-uncompilable
twin is exactly the shape"*. Measured (`.temp/r96/r6_rc_shapes.py`):

```
case                         cfg              summary                rc  rustc_errors
union_read_no_unsafe         shipped cfg      2 verified, 0 errors   0   []
union_read_no_unsafe         --cfg slb_twin   3 verified, 0 errors   1   ['E0133']
user_unsafe_fn_called_bare   shipped cfg      3 verified, 0 errors   0   []
user_unsafe_fn_called_bare   --cfg slb_twin   4 verified, 0 errors   1   ['E0133']
warning_only                 shipped cfg      2 verified, 0 errors   0   []
warning_only                 --cfg slb_twin   2 verified, 0 errors   0   []
```

`user_unsafe_fn_called_bare` has **no union in it**: a pattern declares its own
`unsafe fn`, and the twin calls it. **`_TWIN_BANNED` forbids the token
`unsafe` inside a twin body**, so an author whose checked stand-in touches any
unsafe operation *cannot legally write the keyword* — the only spelling the
gate permits is the one rustc rejects with `E0133`, and the gate then certifies
it. That is an honest mistake **induced by the gate's own rule**, which is the
strongest form of the threat model in `.memory/02-bench-rules.md`. The finding
is still latent (see CN-4), but its reach is general, not p35-shaped.

### MAJOR 4 — TASK_055_REVIEW's TCB policy is "one number **plus prose**", and the prose half is unenforced exactly on the shape the hatch creates

The report's §A.3 answer (`tcb_items = 2`, both infra, do not reinstate the
second column) is **right on the number and right to refuse the second
column** — I did not find an argument that beats the 402-site census, and I do
not propose one. But the decided policy has two halves, and the second one
evaporates here.

`harness/check.py::_check_trusted_arguments` is what makes the prose exist: it
demands a `SLB-TRUSTED-ARGUMENT <src> <name>` block in `NOTES.md`, with labels
(a)/(b)/(c) and a minimum length, **per trusted item**. It iterates
`trusted_by_src`, which `check_trusted_twins` fills only after its
`if not trusted: … continue`. **A pattern with zero `_is_trusted` items owes no
written argument at all** — measured in my synthetic runs, where the block
fires once per trusted item and not at all when there are none.

So a `p35` built on the hatch publishes `tcb_items = 2` with **no enforced
prose beside it**, which is precisely the configuration TASK_055_REVIEW
rejected `tcb_reach` *in favour of*. Consequence 1's one-line
`verus.verified_unsafe[...] = "<why>"` is not that: it is a shouted string with
no structure and no length floor.

⚠ **The report's own defence of (b) — "a verified body's operations all carry
obligations, so completeness is the verifier's job" — is exactly the claim
BLOCKER 1 refutes.** The two findings compound: the prose backstop disappears
*because* the enumeration is trusted, and the enumeration is false.

**A fourth consequence is needed**: extend `_check_trusted_arguments` to
`verus.verified_unsafe` hosts.

### MAJOR 5 — the polarity discriminator is not gate-enforceable, and the report's own battery encodes its violation as "ok"

`.temp/t96/a6_narrow_rule.py`'s docstring:

> *"Case `p15_from_utf8` below is admitted by the narrowed rule and **MUST NOT
> BE** …"*

and its case table two hundred lines later:

```python
    # ⚠ ADMITTED BY THE NARROWED RULE AND IT SHOULD NOT BE -- the sixth route.
    "p15_from_utf8": (""" … """, True, False),      # want_narrow = False = admit
```

so the battery **asserts the behaviour its own docstring forbids** and prints
`ALL AS EXPECTED`; the report's §A.2 table reproduces the row with `ok` in the
expected column. A reader of the report sees a green battery over a case the
report elsewhere says must be refused.

The substantive point: **none of the three enforced consequences enforces the
discriminator.** Consequence 1 shouts a `why`; 2 adds a mutation target; 3
forces Miri. Nothing asks "does the pinned vstd carry a spec for this
operation?" — so the outcome claim *"p35 becomes buildable … p15 stays refused,
on its own named condition"* is an author-honesty claim, not a gate property.
Under the honest-mistake threat model that may be acceptable; it must be said
out loud rather than filed under "three enforced consequences".

### MAJOR 6 — a durable fact queued for `.memory/` is false, and the report's own §D output refutes it

Report "Problems" and memory update 8(a):

> *"there is no `--check-stale` for `results/gate/`, and this is one"*
> *"once a sweep starts, nothing under `harness/` or `patterns/` may be touched
> until it ends — I broke it twice and **there was no check that would have
> caught either**"*

`harness/measure.py::check_stale`:

```python
    files = sorted(glob.glob(os.path.join(RESULTS, "p*.json"))
                   + glob.glob(os.path.join(RESULTS, "gate", "p*.json")))
```

and its own docstring: *"Covers both record families, because they have the
same failure mode and `.memory/02-bench-rules.md`'s hand-run one-liner only
ever covered one: `results/gate/*.json` … `results/*.json`"*, with a comment at
a comment just above `harness/measure.py::check_stale` dating it to TASK_035
(*"`results/gate/*.json` has carried `source_sha256` since TASK_005"*).

**The check exists, it is step 4 of `TASK_096.md` §D's own mandatory order, and
it is what produced the report's `48 record(s) examined, 8 STALE` naming
`results/gate/p01-array-sum.json harness/check.py`.**
`.temp/t96/d2_gate_stale.py` is a re-implementation, useful as an independent
cross-check and nothing more. ⚠ **PROTOCOL rule 9 exists for exactly this: do
not land 8(a) as written.** The process rule itself ("do not touch `harness/`
mid-sweep") is sound and worth landing; the justification attached to it is not.

*(Memory update 7b — `results/tables/` is regenerated by nothing — is **true**;
see CN-6.)*

### MINOR 7 — `vparse` mis-splits a turbofish in a clause, independently reproduced

The report discloses this under "Unsure / not done". It reproduced verbatim in
my execution of `check_trusted_twins`:

```
ensures=['r == get_union_field::<Slot', 'u64>(v, "i")']
```

`vparse` splits clauses on top-level commas and the generic list splits with
them. Legal Verus, mis-split pin. **It would bite `p35` for real**, and it also
means the obligation-count and contract-pin machinery cannot express p35's own
`ensures` today — an item the hatch decision should price in.

---

## Clean negatives — named attacks that did NOT land

**CN-1. "Nest an `external_body` helper inside a verified fn so `vparse` cannot
see it."** `vparse.parse` **does** parse nested items:
`.temp/r96/probe/n1_nested_extbody.rs` verifies `2 verified, 0 errors` and
`vparse` reports `name='raw' external='verifier::external_body' … trusted=True`.
Both rules admit it, and 5a would then demand its missing `requires`. **The
nesting bypass only works through `#[verifier::external]`, which is BLOCKER 1's
route, not this one.**

**CN-2. The report's own named enumeration gap — `unsafe impl GlobalAlloc` —
closes in the SAFE direction.** `.temp/r96/r1_gap_battery.py`:

```
case                             verus      rc  shipped           narrowed
unsafe_impl_globalalloc          2v/0e      0   REFUSE [4, 5, 6]  REFUSE [4, 5, 6]
unsafe_extern_block              2v/0e      0   REFUSE [2]        REFUSE [2]
unsafe_attribute_no_mangle       2v/0e      0   REFUSE [6]        REFUSE [6]
```

Verus admits all three with no obligation, and **both** rules refuse all three,
because a top-level `impl` / `extern` block / attribute is inside no fn body.
`Allocator` is nightly-only and was not probed.

**CN-3. "The §A.2 enumeration is a sample of 26; find a 27th construct that
Verus admits inside a verified body with no obligation."** I found that four of
the report's *refusals* were caused by the **operation** (`get_unchecked` `is
not supported`) rather than the construct, so I re-ran them with an operation
Verus supports natively (`.temp/r96/r2_union_variants.py`):

```
case                             verus    rc   shipped        narrowed
u_macro_in_verified_body         2v/0e    0    REFUSE [8]     admit
u_macro_no_requires              1v/1e    1    REFUSE [6]     admit
u_trait_default_body             1v/1e    1    REFUSE [5]     admit
u_nested_unsafe_fn_called        2v/1e    1    REFUSE [6, 7]  admit
u_closure_no_requires            1v/1e    1    REFUSE [6]     admit
```

**Every one carries the obligation** — with `requires v is i` it verifies, and
without it Verus reports *"requirement not met: to access this field, the union
must be in the correct variant"*. So the report's central claim survives four
more constructs than it tested, including a `macro_rules!` **defined inside a
verified body**, which is x1's own shape at close range. **The enumeration is
stronger than the report claims; what defeats it is BLOCKER 1's `external`
item, which is not "something Verus admits inside a verified body" at all — it
is something Verus never looks at that a TEXTUAL span rule mistakes for one.**

**CN-4. The `_verus` return-code hole is LATENT on this tree — re-verified.** I
re-ran `.temp/t96/b1_verus_exit_census.py` (the engineer's script, so this is a
reproduction and not an independent implementation): **50 rows, every one
`rc=0`, `rows with rc!=0 or errors!=0: 0`.**

**CN-5. §C's `n_twins == 0` limb was a code read; I EXECUTED it.**
`.temp/r96/r5_twin_limbs.py` calls `check.py::check_trusted_twins` itself
against a synthetic pdir under `.temp/r96/fakep/` with a hand-built contract —
no plant into `patterns/`:

```
A  no twin, no justification
   FAIL [twin] verus.rs:5 trusted item `read_i` … has no verified twin.
B  no twin, justified, ONLY trusted item        <- the limb in question
   !!   [twin] BLOCKED verus.rs `read_i` (strength unchecked)
   FAIL [twin] every trusted item in this pattern (['verus.rs:read_i']) is
        excused by verus.twin_justifications, so stage 5c-twin checked the
        strength of NOTHING. A hatch that can be applied to the whole of its
        own stage is an off switch…
C  no twin, justified, SECOND trusted item present
   !!   [twin] BLOCKED verus.rs `read_i` (strength unchecked)     (no n_twins fail)
```

**§A.1b is upheld exactly as written: `p35` has NO legal comply configuration
— hard FAIL with one trusted item, `PASS-WITH-BLOCKED-ROWS` on the row that IS
the pattern with two.** The review task's premise *"the engineer flags that the
`n_twins == 0` hard-fail limb is a CODE READ"* is correct, and the code read
was correct.

**CN-6. Consequence 2 WORKS — executed, not read.** `.temp/r96/r8_consequence2.py`
drives `check.py::check_requires_strength` against the p35 shape with the union
read in a **verified** fn, twice, changing only
`clause_deletion_extra_items`:

```
## DEFAULT  (clause_deletion_extra_items absent)
    FAIL [req-mut] this stage judged 0 `requires` conjuncts across ['verus.rs'] …

## CONSEQUENCE 2  (extra_items = ['kernel','read_i'])
    verus.rs: read_i requires[0] is not a tautology … -- v is i
    verus.rs: read_i requires[0] is load-bearing when deleted (2 verified, 1 errors)
    ok   1 `requires` conjunct(s) probed (n=1 > 0) and 1 deleted …
    -> req-mut failures=0
```

So the §A.2b defect is real and consequence 2 repairs 5c-req on the row that IS
the pattern. **What consequence 2 does NOT restore is 5c-twin's strength oracle
and `_check_trusted_arguments`' prose (MAJOR 4).**

**CN-7. Probe 4's inverted polarity does NOT retro-refuse any shipped row.**
Census of every `_is_trusted` body across all 24 `patterns/*/verus.rs`: the
distinct unchecked operations are `get_unchecked`, `get_unchecked_mut`,
`copy_nonoverlapping`, `count_ones`, `<*const T>::add`. Against the **pinned**
vstd:

```
  get_unchecked          hits=0     assume_specification=0
  get_unchecked_mut      hits=0     assume_specification=0
  copy_nonoverlapping    hits=0     assume_specification=0
  count_ones             hits=0     assume_specification=0
  <*const T>::add        hits=0     assume_specification=0     (p02/p08; the only
                                    three `::add` specs in the pinned vstd are
                                    `<*mu T>::addr` and `f32`/`f64` `Add::add`)
  from_utf8_unchecked    hits=1     assume_specification=1     <- p15 only
```

**0 of 24 built rows would be retro-refused.** ⚠ One clarification the report
should carry: the *reason* it gives for the polarity ("the licence is an
upstream axiom the TCB column cannot see") is true of the built tree too —
**49 of 52 shipped `slb_twin_*` bodies index a slice**, and `v[i]` is licensed
by `std_specs/slice.rs`'s `assume_specification` for
`<usize as SliceIndex<[T]>>::index`. The discriminator's real content is
narrower than its stated reason: *vstd hand-writes a `requires` that licenses
**UB***, not *vstd is anywhere in the chain*. State it that way or the next
reader will apply it to the twins.

**CN-8. The mid-sweep repair IS complete — recomputed independently of
`d2_gate_stale.py`.** Re-hashing every entry of every gate record's
`source_sha256` against the working tree:

```
24 gate record(s)
live harness/check.py: 96f51a28a93bdc16
distinct check.py hashes across records: {'96f51a28a93bdc16'}
STALE entries: 0
hashed path prefixes: {'patterns': 397, 'harness': 9, 'common': 12, 'verus_run.py': 1}
verdicts Counter({'PASS': 23, 'PASS-WITH-BLOCKED-ROWS': 1})
complete_run: Counter({True: 24})   total failures: 0
```

**CN-9. `results/tables/` is current — all 24, checked without writing.**
`harness/report.py <p> --stdout | diff - results/tables/<p>*.md`, trailing
newline normalised: `24 table(s) examined, 0 stale`. And the report's claim
that p46's had been stale since TASK_092 holds:
`git log --oneline -- results/tables/p46-bignum-mac.md` shows only `591fcec`
(the landing) and `9f8fa9d` (TASK_096) — TASK_092's re-measure never touched it.

⚠ **Answering the review's question "was any published number WRONG, not merely
old": YES, one was.** `results/tables/p46-bignum-mac.md:186` read

```
**5 of 32 wall-clock cells exceed the 10% min-to-median spread threshold and
are DISCARDED**
```

with a five-item list, while the record it declares itself generated from gives
**9**, and only one of the old five survives into the new nine
(`safe_naive/whole` on `large.bin`). The stale table also cited contract
`bddd7e032a72` against the shipped `43925b2955e0`. A reader quoting the discard
list would have quoted the wrong cells. **The report's fix (regenerate, and add
`harness/report.py pNN` to the sweep recipe) is right and worth landing.**

---

## Answers to the questions the task asked by name

**A.1 — is the return-code hole really latent?** Latent on this tree (CN-4),
but the honest-mistake shape is general and gate-induced, not union-specific
(MAJOR 3).

**A.2 — is the fix safe at all 12 call sites?** The partition is wrong (MAJOR
2: 11 sites, 6 success-expecting) and a better predicate exists that is safe at
all of them.

**A.3 — does anything else read a subprocess result the same way?** Yes, two
more (`check_verus_contract` inline, `limbs.py::verus`) — but **smaller**, not
bigger, because `build.py::build_verus` checks `rc` and both pinned-obligation
source names are built cells.

**B.1 — enumerative claim.** Survives eight more constructs (CN-2, CN-3);
defeated by BLOCKER 1, which is not a construct Verus admits but a construct
Verus **ignores** that a textual span rule mistakes for an admitted one.

**B.2 — is the three-consequence design sufficient?** Consequence 2 works
(CN-6). Consequences 1 and 3 do not restore `_check_trusted_arguments` (MAJOR
4) and do not enforce the polarity discriminator (MAJOR 5). **A fourth
consequence is required.**

**B.3 — is `tcb_items = 2` honest?** The number is right and the second column
must stay refused — I did not find an argument that beats the 402-site census
and I am not proposing one. The *policy* is what has the hole: its prose half
is unenforced at zero trusted items (MAJOR 4).

**B.4 — polarity on the 24 built rows.** 0 retro-refusals (CN-7), with one
wording correction.

**C — does `p35` have a legal configuration?** No. Executed (CN-5). **So the
hatch buys exactly one row, and only if BLOCKER 1 is fixed first.**

**D — the four small items.** Tables: confirmed, 1 of 24 was stale and one
published number was wrong (CN-9). Gate `--check-stale`: **it already exists**
(MAJOR 6) — so the "could this happen by accident?" question is moot: the check
was there, it was step 4 of the mandatory order, and it fired. Repair
completeness: confirmed independently (CN-8). Citation audit: all 43 correct,
but the `.memory/` originals of two corrected sentences are still wrong
(MAJOR 8, MAJOR 9, MINOR 10).

---

## D — the 43 citation rewrites, audited in full (not sampled)

All 43 were re-resolved against the current `harness/check.py` with an
AST-based enclosing-`def` resolver (`.temp/r96/agent/encl.py`), and I
independently re-derived the two load-bearing ones below.

**The engineer's core claim HOLDS: 43 removals across 24 files (0 additions),
28 distinct `check.py::<name>` targets, every one resolving to a real `def`,
and — after the two self-reported corrections — ZERO wrong function names.**
Corroborating the stated lesson: **every** old line number had rotted onto a
different function (`:1262` → `idiom_problems`, `:2770` → `check_marginal_ir`,
`:4069` → `check_call_site`, `:2253` → `check_build`, `:411` →
`model_sandbox`), so resolving by line would have produced ~40 wrong answers.

**The residue is not in what was rewritten — it is in what was not.**

### MAJOR 8 — the sweep left the AUTHORITATIVE copy of a corrected sentence wrong, and it is the paragraph that promulgates the convention

```
.memory/02-bench-rules.md:1036   **`check_idiom`** keys on `_TICK.findall`
                                 (in `check.py::spelling_matches`), so
patterns/p04-ring-buffer/spec.md:153   (**`check.py::idiom_audit`** -- `_TICK.findall`)
```

Measured — every `_TICK` site in `harness/check.py`, with its enclosing `def`
computed:

```
  check.py:1470  idiom_lines@1442   _TICK = re.compile(r"`([^`]+)`")
  check.py:1698  idiom_audit@1517   "spellings": _TICK.findall(e[lang])})
  check.py:1701  idiom_audit@1517   for tok in _TICK.findall(per[lang]):
```

`_TICK` appears **nowhere** in `spelling_matches`. So the sweep made the
*derived* copies (p04, p09) correct and left the **`.memory/`** original wrong —
the inverse of the project's own precedence rule, and a reader reconciling the
two now finds a direct contradiction that `.memory/` wins.

⚠ **And the wrong attribution was introduced by `f4d0e63`, the commit whose
entire subject is fixing citation rot** (*".memory/ + RECAP: the 'line as a
hint' citation convention failed inside one session"*):

```
$ git log --oneline -S'in `check.py::spelling_matches`), so' -- .memory/02-bench-rules.md
f4d0e63 .memory/ + RECAP: the "line as a hint" citation convention failed inside one session
```

The same paragraph carries `⚠ **Cite the FUNCTION and give NO line number at
all**`, and its own table two screens below still reads
`` **`check_idiom`**, `:1103-1105` (`_TICK` at `:993`) `` — two more rotted
hints inside the rule against rotted hints. `RECAP.md:848-849` carries the same
error. **Manager-only files; reported, not fixed.**

### MAJOR 9 — the "9 left" residue is right by count and wrong by class: `.memory/` carries 12 more live rotted hints, including demand 11's original

`git grep -nE 'check\.py:[0-9]'` outside `.tasks/` gives **8**, plus one bare
`` `:632` `` continuation in `patterns/p16-tlv-walk/model.py` = **9**, so
43 + 9 = 52 holds exactly, in the 6 files named. **All 9 are rotted**:

```
 1249 -> idiom_problems   (claimed check_checksums, actually 2370-2407)
  469 -> class Report     (claimed the `sweep-` drop, actually inputs_of)
  625 -> run_budgets      (claimed check_marginal_ir)
  632 -> run_budgets      (claimed the `work <= 0` hard fail, actually 2680)
  459/460 -> <module>
```

**But the regex the report used cannot see the `` `check.py`'s X (`:NNNN`) ``
form, and `.memory/` is full of it:**

```
.memory/05-layout.md:215   `check.py`'s stage 5a (`:2197`; this said `:1446`) requires *every* `.rs` …
.memory/05-layout.md:216   … and `:1549` fails the gate
.memory/05-layout.md:328   (`check.py`'s inline `sweep-` test at `:474` …)
.memory/02-bench-rules.md:694  (`MIRI_PROBE_ITERS` is defined at `:311` and applied at
                                `:4769`; this said `:3819` … **cite the SYMBOL,
                                line numbers rot**)
```

resolved against the current file: `:2197` → `<module>`, `:1549` →
`idiom_audit`, `:474` → `Report.ok`, `:311` → `<module>` (the constant is at
`353`), `:4769` → `check_requires_strength` (the use is in `check_miri`).
**`.memory/05-layout.md:215-216` is demand 11 — the SOURCE the three pattern
copies quote** — so the sweep again fixed the copies and left the original
rotted, and `.memory/02-bench-rules.md:694` is self-refuting: it says *"cite
the SYMBOL, line numbers rot"* while carrying two rotted line numbers, one of
them ~2100 lines out and into the wrong function. A further 8 sit in
`.memory/06-catalogue.md`'s p22 blockquote, which is fenced `PROVISIONAL`.

### MINOR 10 — four stale claims the sweep's own method would have caught

- `patterns/p09-bitset/spec.md:408` (**inside the hashed contract**, and its two
  derived copies): *"`check.py::exec_code` … does **NOT** blank a `spec fn`
  BODY"*. The function name is right; the **claim is false today** —
  `exec_code`'s own docstring lists *"3. `spec fn` / `proof fn` items, by
  kind"* and it calls `_blank_ghost_items`, added at TASK_069. `exec_code`'s
  docstring even names p09 as the pattern that documents the trap.
- `patterns/p09-bitset/NOTES.md:16-18` now reads *"re-cited by FUNCTION **with
  the line as a hint**"* — the sweep deleted the hints and left the sentence
  describing them. Its `:12` still records `c391270c673f…` as the
  `contract_sha256`; the record says `0a37c0cd1418…`, moved by `9f8fa9d`
  itself. `RECAP.md:2435` carries the old digest too.
- `patterns/p12-strcat-fixed/NOTES.md:95` — the rewrite deleted an opening
  paren and left the closer: ``**`check.py::inputs_of`** and `measure.py`'s
  `SKIP_INPUT_PREFIX`) both drop …``.
- `patterns/p06-rotate/NOTES.md:1457` — the rewrite touched this line and left
  ``(**`check.py::check_verus_contract`**, `vparse.by_name` + `norm_clause`)``.
  `check_verus_contract` calls `vparse.parse`, `duplicate_names`,
  `unique_names` and `norm_clause` — **never `by_name`**, which mentions it
  only in a comment. `vparse.by_name`'s own docstring enumerates its consumers
  and `check_verus_contract` is not among them.

**One AMBIGUOUS citation, flagged rather than called wrong:**
`patterns/p12-strcat-fixed/NOTES.md:1402`'s *"which rungs an entry scopes to
lives in its English"* is near-verbatim `spelling_matches`, but the same idea
appears in `idiom_audit_lines` and `forbidden_only_sources`. `spelling_matches`
is the best and defensible match — it is the definitional statement — but the
sentence does not uniquely identify one function.

---

## The seven contradictions, counted (279 → 286)

- **#280** — report §A.1c: *"four of the twelve `_verus(...)` call sites"*.
  **11 sites, 6 success-expecting**, and two further return-code-blind
  `verus_run.py` readers (`check_verus_contract` inline, `limbs.py::verus`) are
  never named.
- **#281** — report "Problems" / memory update 8(a): *"there is no
  `--check-stale` for `results/gate/`"*, *"there was no check that would have
  caught either"*. **False** — `measure.py::check_stale` globs
  `results/gate/p*.json` and its docstring says so; it is step 4 of the task's
  own mandatory sweep order and it is what found the 8.
- **#282** — the narrowed predicate is **unsound as implemented**: ANY-enclosing
  admits an `unsafe` inside a nested `#[verifier::external]` item that Verus
  never verifies, demonstrated end to end with an aborting binary. INNERMOST
  repairs it at zero cost to the report's own nine cases.
- **#283** — report §A.1c bound *"a verified-but-uncompilable twin is exactly
  the shape"* / *"latent, not live"*. The shape is **not union-specific**: a
  user-declared `unsafe fn` called from a twin gives `4 verified, 0 errors`,
  `rc=1`, `E0133`, and the gate's own `_TWIN_BANNED` is what forces the illegal
  spelling.
- **#284** — report §A's outcome claim *"p15 stays refused, on its own named
  condition"* is **not gate-enforced by any of the three consequences**, and
  the battery that is offered as evidence encodes `p15_from_utf8 -> admit` as
  **expected**, printing `ALL AS EXPECTED` over the case its own docstring says
  must not be admitted.
- **#285** — report §A.3: *"that is TRUE by the closed definition, ALREADY
  DECIDED, and **NOT a new hole**"*. The closed definition is *one number
  **plus prose***, and `_check_trusted_arguments` owes **nothing** when
  `_is_trusted == 0` — so the hatch creates the first shape that publishes a
  TCB number with no enforced prose beside it.
- **#286** — report "Problems": *"43 removed + 9 left = **52** live `check.py`
  line references at HEAD"*. The residue is **at least 64**: the counting regex
  cannot see the `` `check.py`'s <thing> (`:NNNN`) `` form, and `.memory/`
  carries **12 more** live rotted hints in it — four in
  `.memory/05-layout.md` and `.memory/02-bench-rules.md` (including **demand
  11**, the original the three fixed pattern copies quote), and eight in
  `.memory/06-catalogue.md`'s `PROVISIONAL` p22 block.

---

## Not done / unsure

- **I did not run `harness/check.py`,** so I have no end-to-end gate verdict
  for BLOCKER 1 — only the stage functions, run individually against a
  synthetic pdir, plus the shipped-vs-narrowed predicate over the real source.
  A manager who wants the end-to-end demonstration should plant
  `.temp/r96/probe/n3_composite.rs`'s shape into a pattern with the narrowed
  rule applied; I judged that not worth mutating a tracked file for, given the
  five stage-by-stage misses are each verified.
- **I did not implement the narrowed rule in `harness/check.py`.** The
  innermost predicate lives only in `.temp/r96/r3_innermost.py`, which imports
  `check.py` read-only.
- **`unsafe impl Allocator` was not probed** — it is nightly-only at the pin.
  `asm!` and `extern "C"` inside `verus! {}` I did not re-probe; the report's
  refusals for those are about the construct, not the operation, so I accept
  them.
- **CN-4 is a reproduction, not an independent implementation** — I re-ran the
  engineer's `b1_verus_exit_census.py` rather than writing my own.
- **I did not re-derive the report's "24 of 24 make an EXEC `.len()`/
  `.as_slice()` call — 52 sites" figure.** I did verify the `51 unsafe tokens
  across 24 verus.rs` count independently (and that
  `p01/safe_naive_verus.rs` has 0).
- **`.temp/r96/probe/n3_bin*` are binaries** and are re-derivable from
  `n3_composite.rs` by the one `verus_run.py --compile` line quoted above; they
  are deleted. Every `.rs` probe, `.py` generator and `.log` stays.
- Valgrind is **not on `PATH`** on this box (`~/tools/valgrind/bin/valgrind`
  exists but dies at startup on a `memcmp` redirection in `ld-linux`), so the
  out-of-bounds read is evidenced by rustc's own `assert_unsafe_precondition`
  abort rather than by a memcheck trace.
