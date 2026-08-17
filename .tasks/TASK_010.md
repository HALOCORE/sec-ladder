# TASK_010 — fix the twin's perimeter, and tie the driver region to code that runs

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_009_REVIEW.md` — **every
finding below is demonstrated there with a built mirror and real gate output**,
and the reviewer left rigs and mirrors in `.temp/review009/` (`mkmir.sh` copies
`common/` instead of symlinking; `x1 x2 x3 x4 a9 hc b4chk x2probe bv/`). **Reuse
them.** Then `.memory/04-verus.md` and `.memory/02-bench-rules.md`, which the
manager has already corrected — do not re-apply those edits.

Useful, and not obvious: `python3 harness/check.py ../.temp/review009/x1/patterns/p02x1-buffer-copy`
runs the **whole** gate on a mirror. `build.pattern_dir` accepts a `..`-relative
path, so no symlink into `patterns/` is needed.

TASK_009 built the verified twin. It does judge strength on the two off-by-one
forms it was built for. But its **perimeter** is wrong in three ways and it has one
blind spot, and the driver-region decoy now has a confirmed C-side twin. p16 is
blocked on this task.

## Part A (blocker) — one `macro_rules!` deletes the whole trusted-item regime

`harness/check.py:1044` `_UNSAFE_RE = \bunsafe\b` is searched against `item.body`
only, at `:1092` (5a's "a trusted `unsafe` item must demand something") and
`:2107-2109` (5c-twin's `trusted` list). `harness/vparse.py:383` parses **`fn`
items only**, so a `macro_rules!` is invisible.

Mirror `.temp/review009/x1`: `macro_rules! slb_raw_get { … unsafe { *$v.get_unchecked($i) } }`
outside `verus! {}`, `get_unchecked`'s body becomes `slb_raw_get!(v, i)`, its
`requires` deleted and its twin deleted, pins moved in the same commit:

```
verus.rs: no trusted `unsafe` item, so no twin is required
ok  1 verified twin(s): every trusted `unsafe` item's `requires` is strong enough …
check.py: PASS   complete_run True   failures 0
```

R5's trusted base axiomatises that reading any index of any slice is defined —
TASK_003_REVIEW's blocker, fully re-opened. `unsafe` in a `common/driver.rs`
helper is the same hole without a macro, because the gate never parses that file.

**Fix: key the trusted-item rules on `external_body` + a non-empty `ensures`,
not on `unsafe`.** That is precisely the shape that can axiomatise a falsehood
(`.memory/04-verus.md`: "a trusted item that asserts nothing cannot axiomatise a
falsehood"), it catches x1, and it leaves `load_input`/`emit` alone. Additionally
scan the whole file — and `common/` — for `unsafe`, not one body at a time.

Note the consequence and state it in your report: this makes "prefer trusted
wrappers with no `ensures`" and "a trusted item needs an `ensures` to be checked"
pull the same way. `.memory/04-verus.md` records the tension; your fix decides it.

## Part B (blocker) — the twin is verified in a configuration that need not be the shipped one

`check.py:2188` runs `_verus(path, "--cfg", TWIN_CFG)`. That cfg changes the
meaning of the **whole file**, and `check.py:1238-1241` ("only a verified twin may
be `#[cfg]`-gated") is enforced over `vparse` items, i.e. `fn`s — so a cfg'd
`const`, `use`, `type` or `static` is invisible.

Mirror `.temp/review009/x2`: `#[cfg(slb_twin)] pub const SLACK: usize = 0;` with
`#[cfg(not(slb_twin))] … = 1;`, and `spec fn in_bounds(v, i) { i < v@.len() + SLACK }`
used as the `requires` of **both** the item and its twin — so the signature
comparison matches character for character.

```
`slb_twin_get_unchecked` verifies against `get_unchecked`'s own contract (requires=['in_bounds(v, i)'])
`slb_twin_get_unchecked` fails when `get_unchecked`'s `requires` is deleted (12 verified, 1 errors)
FAILURES: 0   SHOUTS: 0        check.py: PASS
```

The twin was checked against `i < v@.len() + 0`; R5 ships `i < v@.len() + 1`.
Proof (`.temp/review009/x2probe`): `get_unchecked(v, v.len())` gives **11 verified,
0 errors in the shipped config** and fails only under `--cfg slb_twin`.

**Fix the reviewer proposes and I endorse:** the token `slb_twin` may appear in a
pinned Verus file **only** inside a twin item's own `#[cfg(slb_twin)]` attribute —
any other occurrence is a hard failure. Also **pin the `--cfg slb_twin` obligation
count**, not merely `tv > base_v`. If you can do better than a token scan — a real
check that the two configurations agree on everything except twin items — do that
instead and say why.

## Part C (major) — the justification hatch, and a green line that is false at n = 0

`check.py:2117-2140` shouts rather than fails, on uncapped free text nobody reads;
`check.py:2267-2274` then prints the `rep.ok`. With both twins deleted, both
known too-weak forms shipped, and two `twin_justifications` entries reading
`"see NOTES.md"`:

```
ok  0 verified twin(s): every trusted `unsafe` item's `requires` is strong enough …
check.py: PASS   failures 0   loud 3
```

A sentence asserting the property at **n = 0**. Fix: `rep.ok` must not fire when
any item was justified away; cap the number of justified items (1 per pattern is
my suggestion — argue if you disagree); and make every count-bearing `rep.ok` in
the harness state its `n`. **Audit the other stages for the same shape** — this is
a class of bug, not one line, and a green line that is vacuous at zero is exactly
what four reviews have been finding.

## Part D (major) — a trusted `ensures` need not cover every unchecked operation

Mirror `.temp/review009/x4`: `get_unchecked`'s body becomes
`unsafe { let _peek = *v.get_unchecked(i + 1); *v.get_unchecked(i) }`, contract,
twin and pins unchanged → `FAILURES: 0  SHOUTS: 0`. Nothing licenses the `i + 1`
read; the twin cannot see it because the twin only has to satisfy the `ensures`.

This is the deepest finding of the review and **I do not expect you to close it
mechanically.** What I want:

1. **Make Miri the backstop it has to be.** `.memory/02-bench-rules.md` now
   records why the current policy is wrong: Miri is mandatory only when R4 ≠ R5,
   i.e. optional exactly when byte-identity holds, which is the case the project
   reports as its headline. Miri over all inputs costs ~1 minute. Run it whenever
   a pattern has **any** trusted `unsafe` item, keeping the identity rule only as
   the reason it can never be skipped when R4 ≠ R5. Then **confirm Miri actually
   catches x4** — if it does not, say so loudly, because then the class has no
   backstop at all.
2. **Require the per-item argument** in `NOTES.md`: for each trusted item, is the
   twin body the right checked stand-in, and is the `ensures` *complete* with
   respect to every unchecked operation the body performs? The gate can require
   the text exists and print it; only a human can judge it. That is honest, and it
   is what `.memory/04-verus.md` now asks for.
3. Fix the related code-evident weakness at `check.py:2233-2243`: the deletion
   probe deletes **all** of a twin's `requires` and needs one failure, so a twin
   needing 1 of N clauses still reports the implementation "genuinely needs it".
   Make it per-conjunct. p02 does not exhibit it; a multi-clause accessor will.

## Part E (blocker) — tie the driver region to code that executes

The decoy region works against **C as well as Rust — one mechanism, not two**
(mirror `.temp/review009/hc`, `c/main.c` only): markers moved into a dead
`static void slb_decoy(void)` whose body is the canonical region, the real loop in
`main` unmarked and carrying `__builtin_prefetch`. Gate PASS, region reported
matching, `prefetch` present in three C cells, **all 32 C cells moved +1…+6
Ir/call while all four Rust rungs stayed put** — a pure cross-language asymmetry.

Two derived fixes, both using machinery that exists. Implement at least one;
implement both if the cost is small:

1. **Structural, catches both demonstrations**: the pinned kernel item may be
   called **exactly once** per rung source, and that call must be inside the
   region. A decoy whose body is the canonical loop necessarily contains a second
   kernel call; a real measured loop cannot avoid containing one.
2. **Dynamic**: callgrind already runs twice per cell for the marginal-`Ir` probe
   and records caller→callee edges. Assert that the kernel symbol's callers in the
   `isolated` build are exactly the region's enclosing function, and that that
   function has non-zero `Ir`. A dead decoy has zero. That is an operational
   definition of "executed" — measured, not declared.

For Rust, `_verus_verified_files` already resolves the region's enclosing item, so
requiring it to equal `driver.call_site` closes that half cheaply — but it says
nothing about C, so it is not sufficient alone.

## Part F (minor) — the floor's three composing knobs

`check.py:757-760`: bound = `MIN_DECLARABLE_IR_PER_BIT × model.work_unit_bits`,
then `/64` with a hatch. `work_unit_bits` is checked only for `>= 1`, so
`work_unit_bits = 1` + hatch gives an absolute bound of **3.05e-5, 512× below the
pre-TASK_009 bound**, from two numbers in the same author-written file that
supplies `min_ir_per_work` and `work_per_call`. Nothing checks `work_per_call` is
denominated in the unit `work_unit_bits` names. Bound the composition, or bound
the product, and print what the effective absolute floor came out as.

## Done when

- Parts A, B, C, E are fixed, each demonstrated by re-running the reviewer's own
  mirror and showing it now **fails** (`x1`, `x2`, `x3`, `hc`).
- Part D items 1–3 are done, with an explicit statement of whether Miri catches
  `x4` (mirror `.temp/review009/x4`).
- `check.py p01` and `check.py p02` green on **complete** runs, and R4≡R5
  unchanged: p02 O3 `md5_fn 0e5b59364bb6`. If the Miri policy change makes a row
  blocked, that is a documented row, not a failure.
- Part F bounded.

## Constraints

No root; no `/tmp` (scratch `.temp/p010/`, reuse `.temp/review009/`); **no
`git add`/`git commit`**; do not edit `pilot/` or `.memory/`. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N>`; a Verus run on p02 is ~2 s, a full gate ~90–120 s.
**A gate run on a mirror writes into the tracked `results/gate/` — move it out.**

Save notes to `.temp/p010/NOTES.md` as you go: five agents in this project have
died to transient API errors mid-task, and notes make a resume cheap.

**If a prescription here is wrong, say so with the measurement.** Six engineers
have contradicted my instructions and all six were right. Part B's token-scan fix
and Part C's cap-at-1 are my calls and the least certain things in this file.
