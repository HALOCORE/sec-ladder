# TASK_010_REVIEW_REPORT — the gate is not obstructive to p16, and one of its green lines is vacuous

**Role:** research reviewer. Everything below was run; no claim rests on reading
alone. Logs and rigs: `.temp/review010/` (`gate-p01.log`, `gate-p02.log`,
`mir-{x1,x2,x3,hc}.log`, `pc-gate.log`, `cgvac.py`, `miribench/`, `NOTES.md`).

---

## Part 1 — will this gate accept p16?

| # | TASK_010 check family | verdict | reason (measured) |
|---|---|---|---|
| 1 | exactly-one-kernel-call, inside the region (Part E structural) | **PASS** | p16's driver is p02's shape minus one argument. `_kernel_calls` scores `fn kernel(`, `uint64_t kernel(` and the `kernel.h` prototype as 0, and `= kernel(...)` as 1, in both languages; it is unaffected by `match`, nested blocks, `#[cfg]`-gated lines, comments and string literals. R1h needs no special handling: `build.py:204` links the *same* `c/main.c` against `c/kernel_hardened.c`, so R1h carries no region of its own and is checked against `main.c`'s. Measured on p02: 5 region files, one call each, and all 8 C cells (2 compilers × plain/hardened) pass. |
| 2 | non-zero exclusive `Ir` + kernel's-only-caller (Part E dynamic) | **PASS**, with F1 | The premise in the task file cannot arise: the stage reads **one** profile, `collapse.probe_inputs[0]` at the high `n_iters` (`check.py:971`), so no adversarial input reaches it; and it `continue`s on `m != "isolated"` (`check.py:3419`), so `-O3` `whole`-mode inlining never reaches it either. In `isolated` mode the symbol survives — measured in `.temp/cg/p02/`: `kernel`, `unsafe::kernel`, `verus::kernel`, `safe_tuned::kernel`. p01/p02 do **not** pass by accident. **But** the "only caller" half is vacuous when no symbol matches — F1. |
| 3 | twin regime, per-conjunct probe, `MAX_TWIN_JUSTIFICATIONS` | **PASS**, with F2 | The probe **is** per-conjunct, verified by construction (mirror `.temp/review010/pc`): a redundant second conjunct `i <= v@.len()` on `get_unchecked` *and* its twin, pins moved, gives `FAIL … still verifies with the single conjunct `i <= v@.len()` DELETED (12 verified, 0 errors)` while `i < v@.len()` alone gives 11/1. p02's two `copy_bytes` conjuncts each give 11/1, i.e. both load-bearing. p16 needs **one** trusted item (a read-only kernel has one accessor), so the cap is not reached. |
| 4 | mandatory Miri, 180 s budget | **PASS**, needs one line changed in TASK_007 (F5) | Measured: p02's 8.38 MB `large.bin` finishes Miri in **1.5 s**; p01's blocks because `common/driver.rs::head_u64_body` decodes the payload *element by element* (1.5 M `le64` + `push`), which p16 does not use — `head1_u64_bytes` is a `to_vec()`, like p02's `head2_`. Miri fold throughput on this box, measured directly: **5.91e-5 s per folded byte (~16 900 B/s)**, so 180 s ≈ 3.05 M folded bytes ≈ **stride ≤ ~760 KiB per call** at `MIRI_PROBE_ITERS=4`. p16's `small`/`large` strides are window sizes (a few KiB) → ~1–2 s. The one input at risk is `adversarial-overrun`, where TASK_007 *requires* `n_blob == stride`. |

### Three premises in `TASK_010_REVIEW.md` that the measurements contradict

1. **Item 2's failure mode cannot occur.** The dynamic half never sees an
   adversarial input and never sees `whole` mode (evidence above). "p16's kernel
   `break`s early on `adversarial-overrun`" is irrelevant to it. The thing that
   *does* go quiet is different and is F1.
2. **Item 3's premise is wrong twice.** p16's accessor is single-clause. TASK_007
   itself prescribes `fn get_unchecked(v: &[u8], i: usize) -> u8`, whose
   `requires` is `i < v@.len()`; `off + len <= buf_len` is the **kernel's**
   `requires`, and the kernel is a *verified* item, outside the trusted regime
   entirely. (And, per your own mid-task correction, p02's `copy_bytes` is
   already a two-clause trusted item.)
3. **"It costs a second Verus invocation" understates and overstates at once.**
   5c-twin runs Verus **five** times on p02 (base + `--cfg slb_twin` + one per
   conjunct), not twice — but a p02 Verus run measures **1.7 s** (re-timed this
   run), so the whole stage is ~8.5 s of a ~4-minute gate. Runtime is not the
   cost worth arguing about; maintenance surface is (Part 3).

### What to change in `TASK_007.md` — F5 and F6, verbatim suggestions

**F5 (minor, act on it).** Under "Inputs", `adversarial-overrun` currently says
*"Keep `n_iters` small there."* That is the wrong knob under TASK_010's Miri
policy: `check.py:3819` rewrites `n_iters` to 4 for **every** Miri run, so the
pattern author's `n_iters` is discarded. Because the same row also requires
`n_blob == stride`, Miri's cost there is `4 × n_blob` folded bytes. Replace with:

> Keep the blob small — a few KiB. `check.py` clamps `n_iters` to 4 for the Miri
> stage, so this input's Miri cost is `4 × n_blob` folded bytes; measured
> throughput on this box is ~16 900 B/s, so a blob above ~700 KiB blocks the row
> and p16 is born `PASS-WITH-BLOCKED-ROWS`. The same bound applies to `small`
> and `large` via their **stride**, not their blob size.

**F6 (minor).** "Done when" does not name three artefacts that are now hard
failures and that did not exist when p02 was built. Cloning p02 supplies the
shapes, but an engineer should not meet them for the first time at hour three:

- `#[cfg(slb_twin)] fn slb_twin_get_unchecked` beside the accessor, same
  signature and contract character-for-character (TASK_009);
- `verus.twin_obligations` in the `slb-contract` block — **with the arithmetic
  written out beside it**, as p02 does ("9 shipped + 3: …"). Without that note it
  is a declared pin a reviewer cannot check from `spec.md` alone, which
  `.memory/02-bench-rules.md` forbids;
- an `SLB-TRUSTED-ARGUMENT verus.rs get_unchecked` block in `NOTES.md` carrying
  labels (a)(b)(c), ≥200 chars.

All three appear as failures in my mirror runs (`mir-x1.log`, `mir-x2.log`,
`mir-hc.log`), so they are load-bearing, not advisory.

---

## Findings

### F1 — `major` — stage 6's dynamic half asserts "the only caller" over an empty set

`harness/check.py:3442-3474`.

```python
kids = [i for i, s in names.items() if re.fullmatch(r"(?:.*::)?" + re.escape(kname), s)]
callers_of_k = sorted({names.get(x, x) for k in kids for x in callers.get(k, ())})
bad = [s for s in callers_of_k if not _cg_name_matches(s, fn)]
if not host or ir == 0:   ...fail...
elif bad:                 ...fail...
else:                     checked += 1
```

If `kids` is empty, `callers_of_k == []`, `bad == []`, the cell is **counted as
checked**, and line 3470 prints *"… has non-zero exclusive Ir and is **the only
caller of the `kernel` symbol**"*. There is no `n` and no guard. This is the
fifth instance of the class TASK_010 itself promoted to a rule in
`.memory/02-bench-rules.md` ("a count-bearing `rep.ok` must state its `n` and
must never fire at `n == 0`") — and it is in code TASK_010 added.

**Reproduced**, `.temp/review010/cgvac.py`: a real p02 `c-gcc O3 isolated`
profile, with only the kernel symbol renamed to `kernel.constprop.0` (the shape
of a gcc IPA clone):

```
control (symbol intact):                   failures=0 shouts=0
kernel renamed to `kernel.constprop.0`:    failures=0 shouts=0
```

— identical green line in both.

**Why it matters, concretely.** The `ir == 0` limb catches the *dead* decoy (and
does: see Part 2's `hc`). The caller-set limb is what catches a **live** decoy —
markers in an executed helper whose body is the canonical loop calling `kernel`,
while `main`'s real loop calls a thin wrapper. That variant passes the structural
one-call rule (one `kernel(` token, inside the region) and is caught only by
`bad != []`. Rename or clone the symbol and nothing objects.

**Reachable by honest accident?** Yes, though not on p16: gcc/clang IPA cloning
(`.constprop.N`, `.isra.N`, `.part.N`), an LLVM `.llvm.<hash>` suffix on a
cold-split function, or a pattern whose `verus.kernel_item` is renamed in
`spec.md` without the symbol following. Also `--cells measured`, already
documented as a soft edge.

**Fix:** `if not kids: rep.fail(...)` naming the symbols actually present, and
print `len(callers_of_k)` in the OK line. Three lines.

### F2 — `major` — `MAX_TWIN_JUSTIFICATIONS = 1` is redundant, and it is the one knob that can forbid an honest pattern

`harness/check.py:1131`. You flagged this as your own least-certain call and the
engineer objected in `.memory`; the objection is right and I can now put a
measurement behind it.

**It is redundant for the case it was built for.** Re-running `x3` (both twins
deleted, both known off-by-one weakenings shipped, two `"see NOTES.md"`
justifications) fails on **both** rules independently:

```
[twin] 2 trusted item(s) [...] are excused ... the cap is 1 per pattern.
[twin] every trusted item in this pattern ([...]) is excused by
       verus.twin_justifications, so stage 5c-twin checked the strength of NOTHING.
```

Delete the numeric cap and `x3` still fails, on the second line. The cap only
bites the case the second rule does *not* cover: ≥3 trusted items with 2
justified — where the machinery already delivers 2 `rep.block`s, 2 shouts, a
suppressed `rep.ok` and a `PASS-WITH-BLOCKED-ROWS` verdict. The cap converts
that documented-blocked-row outcome into a hard failure **with no route out**,
which is precisely the shape that made `MIN_DECLARABLE_IR_PER_WORK` forbid p09
and needed a hatch built in a later task.

**Recommendation:** delete the constant; keep "fewer than all" (already
implemented, `check.py:2842`), the per-item `rep.block`, the shout and the
suppressed `rep.ok`.

**One caveat against my own recommendation, and it should be fixed either way.**
`rep.block` is losing its signal value: p01 now ships permanently as
`PASS-WITH-BLOCKED-ROWS` because Miri cannot finish `large.bin`. If a blocked row
is the normal verdict for a healthy pattern, it no longer distinguishes "attend
to this". The verdict header should separate a **pre-declared** blocked row
(`miri.blocked_reason`) from a newly discovered one.

### F3 — `minor` — the `results/gate/` leak is untracked-but-not-ignored, and `check.py` can close it

Confirmed. `.gitignore:19` covers only `results/gate/*.partial.json`. My four
mirror **full** runs left:

```
?? results/gate/p02x1-buffer-copy.json
?? results/gate/p02x2-buffer-copy.json
?? results/gate/p02x3-buffer-copy.json
?? results/gate/p02hc-buffer-copy.json
```

— one per mirror, plus `p02pc-buffer-copy.partial.json` from my two-conjunct
mirror (that one *is* ignored, by the `*.partial.json` line). A `git add -A`
sweeps the four full-run records, which is how two got committed before. All five
are now under `.temp/review010/leaked-gate-records/` and `results/gate/` is back
to its two tracked files.

**Fix, better than a `.gitignore` line:** `check.py` already resolves
`pattern_dir`; when it does not live under `REPO/patterns/`, write the record
beside the mirror instead of into `results/gate/`. A mirror is not evidence about
this repository and should not be filed as if it were.

### F4 — `minor` — `results/gate/*.json` is not reproducible, so `git status` cannot tell a re-run from a result change

My clean re-run of `check.py p02` produced a 3-line diff against the committed
record. All three are ASan **PIDs and ASLR addresses** inside the stored
`diagnostic` strings:

```
-"...==3102721==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x506000000060 at pc 0x55a98e5b0f13..."
+"...==3118043==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x506000000060 at pc 0x5608887c4f13..."
```

Consequence: every gate run dirties the tracked record, so "the record changed"
carries no information, and the `source_sha256`/contract-hash design that exists
precisely so a weakened pin shows up as an artefact diff is diluted by noise.
Fix: `re.sub(r"==\d+==", "==PID==", …)` and `0x[0-9a-f]{6,}` → `0xADDR` before
storing.

### F5, F6 — `minor` — `TASK_007.md` edits, spelled out above. I did not edit that file.

### F7 — `minor`, residual, do **not** close it — `unsafe` in `common/` is a hard failure with no hatch

`harness/check.py:1274-1285`. Every other structural rule in this file has an
escape hatch that the gate then shouts (`verus.unsafe_justifications`,
`verus.twin_justifications`, `min_ir_per_work_why`, `min_ir_per_work_bound_why`).
This one does not: any `unsafe` token anywhere in a `#[path]`-included `common/`
file fails outright. `common/` has none today and p16 adds only
`head1_u64_bytes`, so nothing is blocked now. But the first pattern that wants a
shared raw-pointer or SIMD helper in `common/driver.rs` is stopped with no route
out — same shape as F2, in a file all 47 patterns share. Record it; do not spend
a task on it.

---

## Part 2 — independent verification of the delivery

Re-run by me, not quoted from the commit message.

### The four mirrors now fail, and for the stated reason

`mkmir.sh` copies `common/`; I checked staleness rather than assuming —
`.temp/review009/{x1,x2,x3,hc}/common/` differs from the tree's `common/` **only
in `__pycache__`**, so the mirrors are current and I reused them.

| mirror | verdict | the stated reason, in the run's own words |
|---|---|---|
| `x1` macro bypass | `FAIL`, 5 failures | `[tcb-unsafe] verus.rs:36 an `unsafe` token sits outside every trusted item's body` + `get_unchecked … has **no `requires`**` + `trusted item `get_unchecked` … has no verified twin` |
| `x2` cfg divergence | `FAIL`, 5 failures | `[twin] verus.rs:53` and `:55` — `the token `slb_twin` appears outside any twin item's own `#[cfg(slb_twin)]` attribute`; plus `no verus.twin_obligations` |
| `x3` justification hatch at n=0 | `FAIL`, 4 failures | `the cap is 1 per pattern` **and** `every trusted item in this pattern … is excused … stage 5c-twin checked the strength of NOTHING` |
| `hc` C-side decoy | `FAIL`, 12 failures | `[driver] c/main.c: 2 call(s) to the pinned kernel item `kernel()` at line(s) [41, 74], 1 of them inside the SLB-DRIVER region` **and** 8 × `[driver] c-{gcc,clang}{,-h} O{0,3} isolated on small.bin: `c/main.c`'s SLB-DRIVER region sits in `slb_decoy`, which executed **0 instructions**` |

All four fail on the intended stage. Two caveats, both benign: `x1`, `x2`, `x3`
and `hc` each also fail the new `SLB-TRUSTED-ARGUMENT` rule (the mirrors predate
it), and `hc` also lacks the new `twin_obligations` pin — incidental noise, not
the closure. The primary failures are present and correctly attributed in every
case. Note `hc`'s dynamic message reads *"(no such symbol in the profile)"* —
`slb_decoy` is `static` and dead, so the `not host` limb is what fires. That is
the limb F1 shows has no counterpart on the `kids` side.

### `check.py p01` and `check.py p02`, complete runs

```
check.py p02 -> PASS                     (.temp/review010/gate-p02.log)
  3c: unsafe vs verus O0: norel (md5_fn 5c0d4e0be96b)
  3c: unsafe vs verus O3: exact (md5_fn 0e5b59364bb6)      <- the pin you asked me to confirm
  6:  5 region files, one kernel call each, inside the region
  6:  dynamic: 16 isolated cells, region function is the kernel's only caller
  8:  miri 9/9 inputs clean, incl. large.bin
check.py p01 -> PASS-WITH-BLOCKED-ROWS   (.temp/review010/gate-p01.log)
  8:  !! BLOCKED unsafe.rs on large.bin: miri did not finish within 180s
      (8 of 9 inputs clean)
```

Both as specified. `p02` O3 `md5_fn 0e5b59364bb6` — unchanged.

### `results/gate/` hygiene at hand-back

Checked before finishing, as instructed. All five mirror records
(`p02x1`, `p02x2`, `p02x3`, `p02hc`, and `p02pc-…partial`) moved to
`.temp/review010/leaked-gate-records/`. `results/gate/p01-array-sum.json` and
`p02-buffer-copy.json` were regenerated by my clean re-runs — I restored the
committed copies (`git checkout --`, working tree only) so the tree is clean, and
kept mine at `.temp/review010/gate-record-{p01,p02}-reviewrun.json`. The only
difference is the ASan PID/address noise of F4. Final `git status`:
`?? .tasks/TASK_010_REVIEW_REPORT.md` and nothing else.

---

## Part 3 — is the verified twin worth its weight?

**Keep the mechanism. Delete one piece of it (F2). Say plainly where it is idle.**

I went looking for the argument to remove it and did not find one. Here is what
decided it.

### The cheap alternative does not work, and this is structural rather than a judgement

`check_miri` runs `miri.sources`, which is **R4's `unsafe.rs`**. The trusted
`requires` lives in **R5's `verus.rs`**. Miri never opens the file the
precondition is written in. It is not a weak backstop for this class; it is not a
backstop at all. Corroboration from the record rather than from the code:
`p02/spec.md` has carried `miri.required: true` since `e27eb85` — before
TASK_006 — and TASK_008_REVIEW nevertheless shipped `i <= v@.len()` past a **full
green gate**. Miri ran, on nine inputs, and passed.

The deeper reason is worth writing down, because it will keep coming up: Miri
tests what R4 *executes*; a trusted `requires` says what the proof *licenses*.
When the kernel's own runtime check is what keeps the accessor in bounds — which
is the situation in every pattern in this catalogue — the licensed-but-not-taken
path is exactly the path Miri cannot reach.

### Free text does not work either, and this project has measured that twice

`min_ir_per_work_why = "see NOTES.md"` passed the whole gate (TASK_006_REVIEW).
`twin_justifications` reading `"see NOTES.md"` passed the whole gate
(TASK_009_REVIEW, `x3`). `SLB-TRUSTED-ARGUMENT` is better shaped — mandatory,
per-item, three named labels, printed in full every run — but it is the same
species, and its only enforcement is a 200-character minimum.

There is also direct evidence that *human reading* of these particular contracts
has a nonzero error rate here: TASK_004_REVIEW read `copy_bytes`'s two `ensures`
clauses and reported both redundant; TASK_006 measured that only one is
(`.memory/04-verus.md` carries the correction). Two agents read six lines and
disagreed. The deletion probe settled it in 1.7 s.

### What the twin catches that neither alternative would: a *missing* conjunct

This is the honest mistake, not the adversarial one. A trusted wrapper around an
intrinsic has to enumerate that intrinsic's documented preconditions from
memory. p02's own comment says so out loud: *"`copy_nonoverlapping` has three
documented preconditions and the `requires` below carries two of them"*. Dropping
one of those is the archetypal accident in this file.

Nothing else in the gate sees it. `.memory/04-verus.md` records the measurement:
deleting a trusted precondition **cannot** fail a Verus run — it only removes
obligations from callers. Parameter coverage (5a) passes whenever the omitted
parameter appears in some *other* clause, which `n` does. The tautology probe
(5c-req) passes. Miri, per above, cannot reach it.

The twin does see it. Measured this run on p02:

```
verus.rs: `slb_twin_copy_bytes` fails when the conjunct `n <= old(dst)@.len()`
alone is deleted from `copy_bytes`'s `requires` (11 verified, 1 errors)
```

And the one accidental contract-strength defect this project has actually
recorded — `safe_naive_verus.rs`, which had never had a consuming ghost `assert`
— was found by the *`ensures`-side* deletion probe, not by anyone reading the
file. The twin is that same mechanism applied to the `requires` side.

### Answering your question directly

> Would an honest author actually ship a too-weak trusted `requires`? Is there a
> recorded instance, or is the mechanism defending a hypothetical?

**No recorded instance of that exact defect.** Both known forms (`i <= v@.len()`,
`from + n <= src@.len() + 1`) were constructed by reviewers. So on the narrowest
reading, yes, it defends a hypothetical. But the *neighbouring* defect — a
contract clause that looks load-bearing and is not — has occurred accidentally on
this project and was caught mechanically rather than by reading, and the
missing-conjunct case above is a plain accident with no other detector at all.
Under "honest mistake, not malicious author" the twin still earns its place; it
just earns it for a different reason than the one it was built for.

### Where it is idle, and this should temper the enthusiasm

**On p16 the twin buys almost nothing.** p16's accessor is the same one-clause
`get_unchecked` with `requires i < v@.len()` that p01 and p02 already ship, and
whose twin is `{ v[i] }`. There is no room in one clause for a missing conjunct,
and the off-by-one it does catch is the one form that has now been checked three
times. p16's real proof risk lives in the *kernel's* loop invariants, which are
verified code and which Verus checks properly without help.

The twin's value accrues to patterns with hand-written multi-clause trusted
wrappers — p02's `copy_bytes` today, and the raw-pointer families from p17 on. So
the honest summary is: **the mechanism is worth its weight, but not on the next
pattern.** Do not let a green 5c-twin line on p16 be read as evidence that
anything difficult was checked; the stage's own OK text is already careful about
this, and p16's `NOTES.md` should say the same in its own words.

### Simplify list

1. **Delete `MAX_TWIN_JUSTIFICATIONS`** (F2). Redundant, measured.
2. **Keep** the `slb_twin` token scan and the `--cfg` regime as built; do not
   extend them. They close a construction no honest author would produce, but
   built machinery costs nothing to retain and the engineer's completeness
   argument (cfg predicates must name the flag in the token stream) is sound.
3. **Keep** `verus.twin_obligations`, on condition the per-pattern note explains
   the arithmetic, as p02's does. Without that note it is a declared pin that
   fails `.memory/02-bench-rules.md`'s own "checkable from `spec.md` alone" test.

---

## Part 4 — clean negatives (things I tried that did not land)

1. **`_kernel_calls` evasion.** Call in a `match` arm, in a nested block, on a
   `#[cfg]`-gated line, `self.kernel(`, `inner::kernel(`, `return kernel(` — all
   counted 1. Rust/C definitions, a C prototype, a call in a comment, a call in a
   string literal — all counted 0. Two residuals, neither p16-relevant and both
   fail-closed or harmless: a C `#define CALLK(x) kernel(x,0)` counts the
   *definition* and not the expansion (so a macro-wrapped call fails the stage);
   `static F: fn() = kernel;` counts 0, so a function-pointer indirection is
   invisible.
2. **`slb_twin` token scan false-firing on the twins' own names.**
   `_TWIN_CFG_TOKEN_RE` (`\bslb_twin\b`) does **not** match
   `slb_twin_get_unchecked` — `_` is a word character. No false positive.
3. **`#[cfg_attr(slb_twin, …)]` as a whitelisted spelling.** `_TWIN_CFG_ATTR_RE`
   does not `fullmatch` it, so it lands in `bad` and fails. Fail-closed, correct.
4. **`_is_trusted` boundary drift.** On p02's four `external_body` items:
   `get_unchecked` True, `copy_bytes` True, `load_input` False, `emit` False —
   exactly where the docstring says the regime ends.
5. **Stale mirrors.** `.temp/review009/{x1,x2,x3,hc}/common/` vs `common/`:
   identical but for `__pycache__`. No regeneration needed; the re-runs are valid.
6. **The dynamic check reaching an adversarial input or a `whole`-mode cell.**
   It cannot. `_cg_probe` is `collapse.probe_inputs[0]` only; the loop skips every
   non-`isolated` cell.
7. **Miri blocking p16's `large`.** Measured not to (8.38 MB → 1.5 s on p02).
   p01's block is the element-wise `head_u64_body` decode, which p16 does not use.
8. **p16 needing a second trusted item, and so meeting the cap.** It does not: a
   read-only kernel has one accessor; `load_input`/`emit` are outside the regime.
9. **p02's `copy_bytes` twin passing the per-conjunct probe on one clause.** It
   needs both (11 verified / 1 error each).
10. **A sixth `rep.ok` vacuity.** I checked all 17 `rep.ok` call sites in
    `check.py`. Sixteen are guarded (`if rows and not bad`, `if per and …`, an
    earlier `len(found) < 2` failure, or explicit `n=… > 0` text). Only stage 6's
    dynamic line is not — F1.
11. **A seventh bypass.** Not hunted, per the task. Nothing incidental turned up
    beyond F1 and the two hatch-shaped residuals F2/F7.

---

## What I did not do

- I did not build p16 or any part of it. Item 4's verdict rests on a measured
  Miri throughput curve plus TASK_007's declared input shapes, not on p16's
  actual `gen.py`.
- I did not re-derive the Part F floor work or re-check Parts A/B/D beyond the
  mirrors named above; TASK_010's own rigs (`g1`–`g4`, `d3`, `d4`, `x4`, `x4m`,
  `x1c`) were not re-run.
- I did not test the twin machinery against a *generic* or method-shaped trusted
  accessor. `.memory/04-verus.md` records that `vparse.params_text` hard-fails
  there; p16 does not need one, but p17+ might, and nobody has re-measured that
  since TASK_008_REVIEW.
- F1's honest-accident routes (IPA cloning, `.llvm.` suffixes) are argued from
  compiler behaviour, not observed in this tree. The **vacuity** is observed; its
  *reachability* on a future pattern is an argument.
