# TASK_009 — judge the *strength* of a trusted precondition

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_008_REVIEW.md` (every
finding below is demonstrated there, with the mirror and the command output),
then `.memory/04-verus.md` and `.memory/02-bench-rules.md`, which the manager has
already corrected. **Do not re-apply the `.memory/` edits.**

The reviewer left reusable rigs in `.temp/review008/` — `mkmirror.sh`,
`stage.py`, `cert.py`, `probe.py`, and 11 built mirrors. **Reuse them.**

## Part A (blocker) — two characters reopen the `&&` hole

`harness/vparse.py:533-554` (`top_level_ops`) reports operators at bracket depth
0 only, and `:576` treats "no operators found" as *atomic with `refused=None`*.
So a clause wrapped entirely in `( … )` is neither split nor refused — no shout,
no failure. Wrapping p02's `copy_bytes` `ensures` as
`( <security clause> && final(dst)@.len() == old(dst)@.len() )` gives:

```
5c: copy_bytes ensures[0] load-bearing (8 verified, 1 errors)
    FAILURES: 0   SHOUTS: 0        full gate: PASS
```

and deleting only that conjunct reproduces the shipped file at 9 verified, 0
errors — so it was never load-bearing. The redundant trusted axiom is back and
the TCB tally undercounts it.

Fix: strip redundant outer brackets before deciding a clause is atomic, and treat
**"atomic" as a claim that must be justified, not a default** — an unsplittable
clause that was not *recognised* as one of the refused forms should shout at
minimum. Note the `==>` refusal path is loud and correct; the bug is that the
parenthesised case escapes *both* branches.

**p02 as shipped exercises neither path (`SHOUTS: 0`), so the refusal branch is
untested by the tree.** Add fixtures that exercise it.

## Part B (blocker) — a trusted `requires` that is too weak by one passes everything

This is the important part of the task. Everything else here is hygiene beside it.

`get_unchecked`'s `requires i < v@.len()` → **`i <= v@.len()`**, pin moved in the
same edit:

```
5a    : ok  trusted `unsafe` item `get_unchecked` demands ['i <= v@.len()'] of every
            caller, constraining every parameter its body uses (['v', 'i'])
5c-req:     get_unchecked requires[0] is not a tautology (9 verified, 1 errors)
full gate: PASS, complete_run True, 0 failures
```

R5's trusted base now axiomatises that **reading one byte past the end of a slice
is defined and equals `v@[i]`**. The same shape on the copy is
`from + n <= src@.len() + 1`.

All three existing checks are structurally blind to it: the tautology probe
because it is not a tautology, parameter coverage because both parameters appear,
deletion because it is not applied to trusted items (and cannot be — TASK_008
measured that). **They judge triviality and mention. Neither is strength.**

### What is needed

A mechanism that shows the declared `requires` actually **licenses the operation
the body performs**. My leading candidate, but *measure before adopting it*:

**A verified twin.** For each trusted `unsafe` item, `verus.rs` carries a second
item with the *same* pinned `requires`/`ensures`, implemented in verified
safe/checked code rather than `unsafe` — `get_unchecked`'s twin is
`{ v[i] }`, `copy_bytes`'s is an indexed copy loop. The gate asserts the twin
verifies against the same contract. A `requires` too weak to license the real
operation is too weak to license the checked one, so `i <= v@.len()` fails the
twin with an index-out-of-range error. The twin is never called from exec code,
so it costs no instructions and cannot perturb R4≡R5 — **verify that claim, do
not assume it.**

Why I prefer this: the author writes *code Verus checks*, not a number they
assert. A wrong twin that nonetheless verifies under a too-weak contract is much
harder to produce than a wrong pin. It is the same move as `model.py` — an
independent implementation — applied to the trusted base instead of the kernel.

Known wrinkle you must handle: **there is no vstd spec for `copy_from_slice`**
(`.memory/04-verus.md`), so `copy_bytes`'s twin cannot be a bulk copy and must be
an indexed loop. If a twin fails for lack of a spec rather than for weakness,
that is a false failure and the mechanism is worse than useless — distinguish the
two cases explicitly.

Two alternatives, if the twin does not work out:

- **Declared safe-equivalent precondition.** `spec.md` declares, per trusted
  item, the precondition of the safe operation the body stands in for
  (`get_unchecked` ↔ `v[i]` ↔ `i < v@.len()`), and the gate machine-checks that
  the wrapper's `requires` **implies** it. Declared, but small and judgeable from
  `spec.md` alone, which `.memory/02-bench-rules.md` permits — and the
  implication being checked stops the two from drifting.
- **A Miri boundary probe.** For each numeric parameter, take the extremal value
  the declared `requires` admits, generate an exec harness calling the wrapper
  there, and run it under Miri. `i <= v@.len()` admits `i == len`, which is UB,
  and Miri says so. Fully *derived* — the strongest shape, and the same
  "declared value tested against a measured one" as the existing Miri
  cross-check — but the most machinery.

**Demonstrate on both measured forms**: `i <= v@.len()` and
`from + n <= src@.len() + 1` must fail, and the shipped tree must stay green.

If all three approaches are wrong, say so with what you measured. That is a more
valuable outcome than a mechanism that appears to work.

## Part C (major) — the tautology probe cannot judge whole shapes of item

`check.py:1545-1559` synthesises from `vparse.params_text` (`vparse.py:445`),
which copies the parameter list and nothing else. Each of these is a hard
failure — fail-closed and therefore *correct*, but the consequence is that a
pattern with a generic or method-shaped trusted accessor **cannot be greened at
all**:

```
<T: Copy>  /  where T: Copy   -> E0425 cannot find type `T`
&self                         -> `self` parameter is only allowed in associated functions
<'a>                          -> E0261 use of undeclared lifetime name `'a`
forall|j| … without #[trigger] -> "Could not automatically infer triggers"
```

Carry the generic list, the `where` clause and the lifetime parameters into the
probe. For a `self` receiver, either synthesise inside the `impl` or refuse *with
a named reason*. Add a fixture for each of the four.

## Part D (major) — the probe reads "Z3 could not prove it" as "it constrains a caller"

```
off <= (off | 1)        -> "not a tautology"
(off & 0xff) <= 255     -> "not a tautology"
v@.len() <= usize::MAX  -> "not a tautology"     <- our own documented tautology
```

The exploitable subset is narrower than it looks and the reviewer measured why: a
tautology the bare probe cannot discharge usually cannot be discharged at the
*call site* either (`from <= (from|1)` as a real clause gives
`8 verified, 1 errors — precondition not satisfied`). What survives is a clause
the caller *can* prove and the probe cannot — `v@.len() <= usize::MAX` is exactly
one, because the kernel fires the axiom with
`assert(src@.len() == spec_slice_len(src))` and the probe has no such line.

Minimum fix: give the probe the same ambient facts a call site has (the
`spec_slice_len` axiom for every slice parameter, and any file-global
`broadcast use`). Then re-measure all three rows above and report which are
caught. **Do not claim this closes the class** — say what survives.

## Part E (major) — certificate denial misattributes a mod-nested driver

`check.py:1982` runs `--verify-function <name> --verify-root`, which cannot
resolve a function inside a `mod`: *"could not find function drive"* → `(None,
None)` → certificate denied → a message saying *"the item enclosing the region
has no verified body"*, which is false. An `impl` method resolves fine.
Fail-closed but wrong diagnosis, and it bites the first pattern that puts its
driver in a submodule.

Distinguish "Verus says this item has no verified body" from "Verus could not
resolve this item name" and report them differently. Also note for the record:
Verus does **not** object to two items sharing a name (`S::drive` and
`inner::drive` → `--verify-function drive` silently reports `1 verified`), so
`vparse`'s duplicate-name failure is the only thing between the certificate and
the wrong item. Confirm that ordering still holds after your change.

## Part F (major) — `MIN_DECLARABLE_IR_PER_WORK` forbids an honest future pattern

`check.py:707` fires `rep.fail(); return {}` **before** any justification is
consulted, unlike the below-default path which accepts `min_ir_per_work_why`. The
bound's derivation (`check.py:174-187`) is "4 instructions per 256 bytes" — a
statement about *bytes*. `.memory/06-catalogue.md` plans **p09 bit
vector/bitset**: AVX-512 `vpopcntq` does 512 bits in ~3 instructions =
**0.0059 Ir per bit**, below the bound, with no route out. The same shape applies
to any *skipping* walker denominated in buffer bytes.

Either make the bound unit-aware, or give it the same justification hatch the
below-default path has (shouted every run). Your call; say why. Fix it now rather
than when p09 arrives, because arriving at it under deadline is how a bound gets
switched off rather than fixed.

## Part G (minors)

1. `vparse.py:617-628` — `delete_conjunct` swallows only whitespace around the
   connective, but `conjunct_spans` trims through comments (blanked in
   `sig_code`). `ensures a == b /* && c */ && d == e` → deleting conjunct[0]
   leaves a dangling `/* && c */ &&`, a parse error reported as *"Verus produced
   no result for the mutant"* — blaming Verus for a splitter bug.
2. `harness/check.py` is not executable (`./harness/check.py` → Permission
   denied). Either `chmod +x` it or stop documenting it as `./harness/check.py`.
3. `measure.py` cannot record the commit it will be committed *in*, so a fresh
   JSON always names HEAD~1 as dirty. Structural — say so in the schema comment
   rather than chasing it.

## Part H (scoped investigation) — the decoy driver region

The reviewer raised this **from reading only, and did not demonstrate it**:
nothing pins the `SLB-DRIVER` region to the *measured* code path. A region in a
dead decoy `fn` whose body matches the canonical tokens, while the real measured
loop goes unpinned, looks reachable.

**Verify or refute it, with a built mutant and a gate run.** If it lands it is a
blocker in its own right and the sixth distinct bypass of the driver diff. If it
does not, say what stops it — that is equally worth knowing, and this is the
highest-value unexplored attack on the pin.

## Done when

- Parts A–G are fixed, each demonstrated with real gate output, and both
  `check.py p01` / `check.py p02` are green on **complete** runs.
- Part B fails on **both** measured too-weak forms, and you have verified the
  mechanism costs no exec instructions (R4≡R5 identity unchanged on p02).
- Part H is answered either way.
- `.temp/` holds your mutants so the next reviewer can re-run them.

## Not in scope

`measure.py p02` — deliberately deferred. `.memory/06-catalogue.md` records the
ordering: it is re-run *once*, with p16's `common/head1_u64_bytes` already in
place, when p16 is published. Do not do it here and do not do it twice.

## Constraints

No root; no `/tmp` (scratch in `.temp/p009/`, reuse `.temp/review008/`); **no
`git add`/`git commit`**; do not edit `pilot/` or the `.memory/` files. Verus only
via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N>` on long builds; a Verus run on p02 is ~1.7 s, a full gate ~90 s.

**If a prescription here is wrong, say so with the measurement.** Six engineers
have contradicted my instructions and all six were right — most recently on this
exact subject, where my `requires`-deletion oracle could not have worked. Part B
is my design and it is the part most likely to be wrong.
