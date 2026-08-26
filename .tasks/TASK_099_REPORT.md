# TASK_099 — four cells withdrawn, the `include!` hole closed (and a sixth spelling found), the docstring corrected

**Role: research engineer.** Scratch `.temp/t99/`, notes in `.temp/t99/NOTES.md`.
Nothing under `.memory/` or `RECAP.md` touched; no `git add`/`git commit`.

## THE ANSWER TO THE THREE CALLS, FIRST

**1. Blank vs. range — I chose NEITHER of your two, and the reason is inside
your own §A2.** The cells now print **`**WITHDRAWN — not a quantity.**` + the
measured support + the reproducible term**, and no `**?**`.

> *Blanking is wrong specifically because BLANK ALREADY MEANS SOMETHING ELSE in
> this table*: `|correction| < 2.00`, which is the `< 2.00` band whose own claim
> §A2 asks me to withdraw as false. Blanking p03/p04's `R5−R4` would move them
> into the band that says *"nothing real hides below the floor"* — the sentence
> the same task proves wrong — and it would make them indistinguishable from
> the 120 rows that really are inside the floor. Publishing `−1.00` alone
> (option 2) re-creates the false precision in the opposite direction: a reader
> quotes *"the proof costs −1 instruction"*, which is `main`'s residue, not an
> answer to the question the column asks. The range **with its support** is the
> only form that carries the reason not to quote it.

**2. Is `include!` the only macro route? NO — and the sixth spelling is not a
macro at all.** `#[path]`-of-`#[path]` — a **transitive** module chain — was
live at HEAD, is reachable **by accident**, needs no macro, and nothing in
`.memory/`, `TASK_098_REPORT.md` or `TASK_099.md` names it. `_path_includes`
read `srcs` and never re-read what it returned, so `verus.rs → common/x.rs →
h.rs` left `h.rs` unscanned. Verus: `1 verified, 0 errors`. Full route table in
§B2. **This is worth more than the fifth, exactly as you said it would be.**

**3. Does `0 hits across 24 patterns` bound it? No, and it is weaker than you
wrote.** It bounds *today's tree against the spellings someone thought to
grep for*. The transitive route needs **zero** new tokens, so a `grep -c
'include!'` returning 0 says nothing about it — and `0` is what it returns on
this tree today. The honest bound is: *the walk's file set is byte-identical on
all 24 patterns before and after this change* (`.temp/t99/b1_pathincludes_diff.py`,
`24 patterns compared, 0 file-set difference(s)`), which is a statement about
**the fix being latent**, not about the tree being safe.

**Running count: 299 → 307.** Eight, in §CONTRA. Three are against sentences the
manager wrote in `TASK_099.md` itself; three are also committed in `.memory/`;
the sharpest (C7) is against `.memory/03-measurement.md`'s framing of the ±7
and is the one I would most want a reviewer to attack.

---

## Did

| file | change |
|---|---|
| `harness/check.py::_path_includes` | sees `include!("…")` (any bracket, raw strings, subdirectories) **and is now a transitive fixed point**, resolving each include against the **including file's** directory |
| `harness/check.py::_check_opaque_includes` | **new**, called from `check_verus_contract` beside `_scan_unsafe_sites` (which I did not touch): refuses an `include!` whose argument is not a resolvable literal, and an `include!` naming a file that does not exist |
| `harness/check.py::check_marginal_ir` | docstring: the four-pattern list, the `-O3 isolated is invariant` line, *"the only cell class no probe has moved"*, and the *"presence, not size"* bullet — all four corrected against measurement |
| `synthesis/synthesize.py` | `PHASE_SWEEP` / `PHASE_SCREEN` / `WITHDRAWN` pins + `derived()` withdrawal and `‡` marking; band-table `reading`; the `64-byte` control paragraphs; §5 claim 1's row list |
| `synthesis/licence.py`, `synthesis/outward_ir.py` | docstrings: `64-byte-longer environment block` → the measured **+87 bytes**, and the bistable/period-32 shape |
| `.temp/t99/` | `NOTES.md`, `a2_phase.py`, `b1_pathincludes_diff.py`, `b2_source_to_published.py`, `b3_routes.py`, `d1_sweep.sh`, logs |

**Not touched:** `harness/build.py`, `harness/asm.py`, `check.py::_scan_unsafe_sites`,
any rung `.rs`, `c/kernel.{c,h}`, `model.py`, `inputs/gen.py`, `pilot/`, the
Verus pin, `.memory/`, `RECAP.md`, `results/synthesis.md` by hand.

⚠ **DISCLOSURE — three edits landed after the §D sweep began, all in
`synthesis/`, none of them hashed by anything.** With the sweep at `p01` I
(a) prefixed the withdrawn cell with `‡` so the marker its own footnote is named
after is present, and (b) replaced `50.02 → 43.02` with the exact
`129 + 50.00×6000` form in `synthesize.py`, `licence.py` and `outward_ir.py`.
**`synthesis/` is in NEITHER hash** — verified by reading `check.py`'s glob
(`patterns/pNN/*`, `common/driver.*`, `harness/*.py`, `common/*.py`,
`common/layout/*.py`, `verus_run.py`) and `measure.py::measurement_sources` —
and `synthesize.py` runs **once, at the end** of the sweep, after all 24 gates.
So neither edit can stale a record or make the artefact disagree with its
generator. **`harness/check.py` was NOT touched after the sweep started**, which
is the thing TASK_096 got wrong.

---

## §CONTRA — eight contradictions, six of them against the task file or `.memory/`

### C1 (blocker-grade, against `TASK_099.md` §A2 bullet 2 and `TASK_098_REPORT.md` BLOCKER 2) — **the "vacuous control" is not vacuous. The control fired, and I reproduced the exact published movement.**

The claim: *"`results/synthesis.md:50` and `:188` rest on a second sweep taken
under a **64-byte-longer environment block** — which is the SAME alignment phase
as pad 0, because the period is 32. It is the FIFTH control in this project that
could not have fired."*

**The sweep does not lengthen a variable. It ADDS one.** `.temp/p75rev/envsweep.py:93-95`:

```python
envA = dict(os.environ)
envC = dict(os.environ)
envC["SLB_ALIGN_PAD"] = "z" * 64
```

so the block grows by `8 (envp slot) + len("SLB_ALIGN_PAD=") + 64 + 1 (NUL)`
= **87** bytes, and `87 mod 32 = 23`. Measured, not computed
(`.temp/t99/a2_phase.py`, one callgrind run per environment, p03 `-O3 isolated`,
`small.bin`, per-function **exclusive** Ir of the glibc `memset`):

```
# case                                                    envblk B d(envblk)    memset       kernel
  A  inherited env (sweep A)                                  3672        +0    300129     20166000
  C  + SLB_ALIGN_PAD=z*64  (sweep C, the published control)    3759       +87    258129     20166000
  C0 + SLBPAD=      (empty)                                    3688       +16    258129     20166000
  D  + SLBPAD=x*64                                             3752       +80    258129     20166000
  P16  SLBPAD length 16                                        3704       +32    300129     20166000
```

**These reproduce the published figure exactly, not approximately.** p03
`small.bin` runs `n_iters = 6000` with one `memset` call per kernel call
(`synthesis/outward_ir.json`: `outward_calls_per_kernel_call = 1.0`), so

```
   300129  =  129 + 50.00 x 6000        <- sweep A, the committed phase
   258129  =  129 + 43.00 x 6000        <- sweep C, the "vacuous" control
   difference 42000 = 7.00 x 6000
```

with the same 129 `Ir` of startup `memset` outside the kernel in both. That is
**the very `50.00 → 43.00`** those two lines are about, to the instruction,
reproduced in a different session under the exact knob that was declared unable
to fire. The `kernel` column reads `20166000` in every row, so the immunity
claim reproduces in the same runs.

**Corroboration the reviewer had and did not use:** the sweep it called vacuous
**moved 11 of 348 triples** (`TASK_075_REVIEW_REPORT.md:136-144`). A control that
cannot fire does not move 11 triples. `.temp/p75rev/perturb.py`'s `C0` row shows
the same on an *empty* added variable (`+16` bytes): `50.00 → 43.00`.

**So the "fifth control that could not have fired" is itself a control that
could not have failed** — it was an arithmetic reading of a phrase, never a
measurement. I corrected the description in all three places that carry it
(`synthesize.py`, `licence.py`, `outward_ir.py`) rather than withdrawing a true
sentence.

### C2 (major, against `TASK_099.md` §C's opening sentence) — **TASK_097 did not fix the `-O3 isolated is exactly invariant` claim. It is still in `check.py` at HEAD.**

§C opens *"TASK_097 fixed the `-O3 isolated` is exactly invariant claim. Its
four-pattern exposed list is ALSO wrong"* — i.e. one fix remained. Two did.

```
$ git show 711d9c7 --stat | grep check.py     # the TASK_097 commit
 harness/check.py | 136 +++++-
$ git show 711d9c7 -- harness/check.py | grep -c check_marginal_ir
0
$ git show HEAD:harness/check.py | sed -n '2571,2573p'
              -O3 isolated  invariant (0.00 across every probe to date)
              -O3 whole     moves by 7 per per-call stack `memset`
              -O0           moves in BOTH modes
$ git show HEAD:harness/check.py | grep -n "only cell class no probe has moved"
2597:    only cell class no probe has moved. And if p08's 12 cells move by a few
```

`.memory/03-measurement.md:2413` agrees with `git`, not with the task file:
*"**What is owed, and none of it is done:** the docstring's scope…"*. Both are
fixed here.

### C3 (major, against `.memory/03-measurement.md`'s RESOLVED block, `TASK_098_REPORT.md` MAJOR 3 and `TASK_099.md` §C) — **"2 patterns, 7 of 144 cells" is arithmetically impossible. It is THREE patterns.**

Recounted from the reviewer's own artefacts (`.temp/r98/treescan_{small,large}.json`,
pad 0 vs pad 16, 24 patterns × 6 cells × 2 blobs):

```
(pattern,input,cell) triples: 288;  marginal moved: 14;  kernel-exclusive compared 288 moved 0
    p03/small safe_tuned 3418.0 -> 3425.0      p03/large safe_tuned  9067.3 ->  9074.3
    p03/small unsafe     3059.0 -> 3066.0      p03/large unsafe      8441.3 ->  8448.3
    p03/small verus      3065.0 -> 3058.0      p03/large verus       8447.3 ->  8440.3
    p04/small safe_tuned 3425.0 -> 3432.0      p04/large safe_tuned 11724.0 -> 11731.0
    p04/small unsafe     3420.0 -> 3427.0      p04/large unsafe     11719.0 -> 11726.0
    p04/small verus      3426.0 -> 3419.0      p04/large verus      11725.0 -> 11718.0
    p46/small c-clang    6216.0 -> 6209.0      p46/large c-clang    23230.66 -> 23223.66
```

7 (pattern, cell) pairs = p03 ×3 + p04 ×3 + **p46 `c-clang` ×1**. TASK_098's own
prose says so one paragraph later (*"exactly one in p46 — `c-clang`"*) and its
headline still says two patterns; `.memory/` and this task file inherited the
headline.

**The mechanism of the slip is worth keeping**: the 32-pad sweeps
(`.temp/r98/p*_sweep.json`) cover **Rust rungs only**, so "p38 and p46 swing
0.00" is true *of the Rust rungs* and was generalised to the pattern. Verified:

```
p01 {safe_naive: 0.0, safe_tuned: 0.0, unsafe: 0.0, verus: 0.0}
p16 {…all 0.0}   p38 {…all 0.0}   p46 {…all 0.0}
```

The correct sentence is *"p38's and p46's **Rust rungs** swing 0.00 over 32 pads,
which kills the four-pattern list; the exposed set is p03, p04 and p46 `c-clang`
— 7 of 144 cells over three patterns."* p46's `gcc-clang` row is now marked `‡`
in the artefact.

### C4 (major, against `check.py::check_marginal_ir`'s own docstring, HEAD) — **"the discriminator is the PRESENCE of a variable, not its size" is false at `-O3 isolated`.**

Recomputed from `.temp/r98/p03_sweep.json` — `marginal_ir_per_call`, pads 0…31:

```
unsafe      3066 for pads  6..21, else 3059
verus       3058 for pads  8..23, else 3065
safe_tuned  3425 for pads 14..29, else 3418
safe_naive  8176 flat
```

Pad 1 and pad 7 disagree on the same binary. The shape is **period 32, window
exactly 16, phase per binary**, and my own pads 0/8/16/24 reproduce it exactly in
a different session. Two things fall out that nobody had stated:

* **the pair swing is 14 because the two rungs have different phases** — that is
  the mechanism behind TASK_097's `+6.00 → −8.00` sign flip, and it is now in
  the docstring;
* **a two-pad screen 16 apart is a COMPLETE detector, not a lower bound**,
  because a 16-wide window in a 32-period puts `p` and `p+16` in opposite states
  always. That is why `treescan.py`'s two pads were enough — a fact its own
  report treats as a sampling compromise. ⚠ It rests on the 16-wide window,
  which is verified on p03's and p04's six Rust cells only.

### C5 (major, against `.memory/02-bench-rules.md`'s own §`include!()` section) — **the `include!` hole was not new at TASK_098. The same file has listed it as a DELIBERATELY-ACCEPTED residual since 2026-08-17.**

`.memory/02-bench-rules.md:273`, under *"Known residuals we are deliberately
**not** closing, all measured"*:

> `include!()` of a file outside the module graph escapes the `unsafe` scan.

```
$ git log -S 'include!()` of a file outside the module graph' --oneline -- .memory/02-bench-rules.md
4abffbf docs: settle the gate's threat model, the manager's rules, and the priority   (2026-08-17)
```

That is **365 commits and eight days before** TASK_098 §4A, which presents it as
found. This matters twice over:

* it is the project's own recurring failure mode — the correction was already in
  the authoritative layer, one list above the section that re-announces it;
* **by that file's settled threat model, `include!` alone did not warrant a gate
  change.** *"Before hardening the gate again, ask: could this defect happen by
  accident? If not, record it as a known residual, name it here, and move on."*
  It was recorded. TASK_098's own severity note reaches the same conclusion
  (*"no honest author reaches for `include!`"*).

**So the fix earns its keep on route 5, not on route 1.** A transitive
`#[path]` chain is exactly what an honest author writes — one shared helper
pulling in another — and it was never named anywhere. I would not have argued
for this change on `include!` alone.

### C6 (major, against `TASK_098_REPORT.md` MAJOR 4's "a gate-clean `p35` therefore EXISTS") — **demonstrated at `_scan_unsafe_sites`, not at `check.py`. The whole gate goes RED on the sibling spelling — with a diagnostic that names the wrong thing.**

Measured (`.temp/t99/b2_include.log`, the first run, before I moved the plant):
`include!("t99_helper.rs")` in p03's `verus.rs`, HEAD's `_path_includes`
semantics → the gate fails **5 times**, none of them `[tcb-unsafe]`:

```
FAIL [clause-mut] verus.rs: the UNMUTATED copy at .temp/clausemut/p03/patterns/p03-bounded-stack/verus.rs
     does not verify (None verified, None errors). Every mutant would then 'fail' for the wrong reason…
FAIL [req-mut]  … (same cause)
FAIL [twin] verus.rs:223  … Verus produced no result for the mutant …
FAIL [twin] verus.rs:263  …
FAIL [twin] verus.rs:306  …
```

**Cause:** `check.py::_mutant_path` mirrors *only* the pattern directory plus a
`common` symlink, so a sibling `include!` cannot resolve in the mutant copy and
the unmutated control fails to verify. This is an **incidental** detector: it
would not fire for an `include!` that resolves through `common/` (which is
symlinked into the mirror), and it says nothing about `unsafe`. It is why my
primary acceptance arm routes the plant through `common/` — one cause, one
message.

So the accurate statement is: *`_scan_unsafe_sites` is blind to `include!`, and
on a pattern with clause-deletion and twin stages the gate still turns red for
an unrelated reason.* A pattern **without** those stages, or with the include
under `common/`, was genuinely gate-clean.

### C7 (blocker-grade, against `.memory/03-measurement.md`'s RESOLVED block) — **the ±7's axis is NOT "the environment block's length". The gate's own number changes with HOW THE GATE WAS LAUNCHED.**

`.memory/` says: *"It is not a property of the launching method; it is a
property of the environment block's LENGTH."* **Both halves are wrong on this
box.** Three full `harness/check.py p03` runs, byte-identical tree
(`.temp/t99/a5_gate_phase.py`; the record is snapshotted and restored):

```
run                               safe_naive  safe_tuned      unsafe       verus
committed / post-sweep               8176.00     3418.00     3059.00     3065.00
A  bash, stdout -> FILE              8176.00     3418.00     3059.00     3065.00
B  python, stdout -> PIPE            8176.00     3425.00     3066.00     3058.00
C  bash, stdout -> FILE (repeat)     8176.00     3418.00     3059.00     3065.00
```

`A = C ≠ B`, deterministic and repeatable, 3 of 4 cells, `unsafe +7` against
`verus −7` — i.e. **p03's `R5−R4` goes `+6.00 → −8.00` with no environment
variable set and nothing in the tree changed.** And the two obvious mechanisms
are dead by measurement: the env block is **3672 B / 48 vars down every launch
path** (`a3_launcher.py`), and the measured program's stdio is **inert**
(`a4_stdio_phase.py`: pipe / file / devnull all `3066.00 / 3058.00`).

I did **not** isolate what does it, and I am not naming one. The correction the
authoritative layer needs is the scope, not a mechanism:

> The ±7 is selected by something in the **process image of the gate run**, of
> which the environment block's length is one instance and the launcher is
> another. ⚠ **"Re-run the gate and compare" is therefore not a reproduction
> test for these cells unless the launcher is held fixed** — which is exactly
> how TASK_097 saw it first (a `nohup`'d script against an interactive shell)
> and attributed it to environment size.

### C8 (minor, process) — **the running count is now in three files while its owner is mid-task.** `.tasks/TASK_100.md` (written 11:35, during this task) closes with *"Carry **301** forward"*, pre-committing TASK_099's result at `+2` before it existed; `.tasks/TASK_101.md` and `.tasks/TASK_102.md` followed. `RECAP.md` and `.tasks/PROTOCOL.md` were also being modified concurrently (mtimes 11:54/11:55, mid-sweep-prep). I touched none of them. PROTOCOL rule 2's *"ONE place: the closing paragraph of the newest `TASK_NNN*.md`"* no longer identifies a unique file while more than one task is open, which is the same drift that put `RECAP.md` 48 out.

---

## §A — the four cells, and what replaced them

`results/synthesis.md` §2 `R5−R4`, the two rows §A quotes, now read:

```
| p03-bounded-stack | 0.00 | 0.00 | LICENSED | **WITHDRAWN — not a quantity.** Over 32 environment
phases the correction takes `-8.00` on 14, `-1.00` on 4, `+6.00` on 14 of 32, identically on both
blobs; the published `+6.00` was one draw and is tied with its own sign-reverse. Reproducible
content **-1.00** (`main` 14 vs 13); the `memset` term `{−7, 0, +7}` is unresolvable here. |
| p04-ring-buffer | … identical text … |
```

and no `**?**` on either. The support is re-derived, not copied — recomputed
from `.temp/r98/{p03,p04}_sweep.json` with `(marg[A]−marg[B]) − (kex[A]−kex[B])`:

```
p03/p04  R2-R4: {0.00: 16, 7.00: 16}
p03/p04  R3-R4: {-7.00: 8, 0.00: 16, 7.00: 8}     <- BLANK at 16 of 32 phases
p03/p04  R5-R4: {-8.00: 14, -1.00: 4, 6.00: 14}   <- the four withdrawn cells
```

**Scope, and why exactly four and not twelve.** The same ±7 rides on p03/p04's
`R2−R4` (`+5117.00`, so 0.14%) and `R3−R4` (blank at this phase). Those are not
withdrawn — the correction is a rounding error of a large true difference there.
On `R5−R4` the two binaries are **byte-identical**, the kernel column is exactly
`0.00`, and **the correction IS the entire published figure**; that is the
discriminator, and it is stated in `WITHDRAWN`'s comment. The other eight cells
carry a new `‡` marker instead, with the support printed under each table.

**§A2 (a) — the band's claim.** `| < 2.00 … | **safe**: nothing real hides below
the floor |` → `| **not safe — this is one environment phase.** ⚠ See `‡` |`,
plus a paragraph naming the falsifier (p03/p04 `R3−R4`: `0.00` at 16 of 32
phases, `±7.00` at the other 16 — 3.5× the floor).

**§A2 (b) — the control.** Re-taken rather than withdrawn: see **C1**.

**One internal contradiction I had to fix to make the withdrawal honest**: §5
claim 1 printed the withdrawn numbers again, 280 lines later
(*"clears the ±2.00 floor on 6 rows — … p03 small +6.00, p03 large +6.00, p04
small +6.00, p04 large +6.00"*). It now prints `p03 small **WITHDRAWN** ‡` and
the follow-up paragraph no longer says *"the derived `+6.00` has the right
existence and the wrong sign"*.

---

## §B — the hole, and six routes

### B1 — the fix is latent on the shipped tree

```
$ python3 .temp/t99/b1_pathincludes_diff.py
24 patterns compared, 0 file-set difference(s)
exit=0
```

Both argument shapes (`verus.obligations`, and `+ pdir/*.rs` as
`_scan_unsafe_sites` passes them) compared against a **verbatim copy of HEAD's
`_path_includes`**. And `_check_opaque_includes` over all 24: `0 failure(s)`.
So no shipped pattern's file set, and no shipped verdict, moves because of §B.

⚠ **The first version of this fix returned `[]` for TASK_098's exact route** and
b2 caught it: I had seeded the `seen` set with the roots, and an `include!`d
**sibling** is in `pdir/*.rs`, hence a root. Emitted-vs-walked are now two sets,
and the docstring says why.

### B2 — the route table (`.temp/t99/b3_routes.py`)

Each route is real files, put through the **actual** detector twice — HEAD's
`_path_includes` and the new one — and through `./verus_run.py`:

| route | HEAD sees | now | Verus |
|---|---|---|---|
| 1 `include!("h.rs")` | `[]` | `['h.rs']` | `1 verified, 0 errors` |
| 2 `include!("sub/h.rs")` | `[]` | `['sub/h.rs']` | `1 verified, 0 errors` |
| 3 `include!(r#"h.rs"#)` | `[]` | `['h.rs']` | `1 verified, 0 errors` |
| 4 `macro_rules!` emitting `#[path] mod` | `['h.rs']` | `['h.rs']` | `1 verified, 0 errors` |
| **5 `#[path]` of `#[path]`** | **`['mid/mid.rs']` — LEAF UNSCANNED** | `['mid/h.rs','mid/mid.rs']` | `1 verified, 0 errors` |
| 6 `include!` of `include!` | `[]` | `['h.rs','mid.rs']` | `1 verified, 0 errors` |
| 7 `include_str!` | `[]` | `[]` | n/a — data, no `unsafe` **token** enters the token stream |
| 8 `include!(concat!(…))` | `[]` | `literals=[] opaque=1` → **refused** | `1 verified, 0 errors` |

**Route 4 was already closed** and nobody had said so: `_path_includes` matches
`#[path]` in the **raw** text, so a `#[path]` inside a `macro_rules!` body is
found. That is a clean negative — do not re-run it.

**Route 5 is the answer to your question 2.** It is not a macro, it needs no
unusual spelling, and an honest author reaches it by having one shared helper
pull in another.

**Build-script route: not reachable here.** `harness/build.py:54` invokes
`~/.cargo/bin/rustc` directly — no cargo, no `build.rs`, no `OUT_DIR` — and
`verus_run.py --cargo` is forbidden by this task. `include!(env!("OUT_DIR"))`
would be refused by `_check_opaque_includes` in any case.

### B3 — the acceptance test: source → published, ONE command, arms that FAIL

`.temp/t99/b2_source_to_published.py <arm>` runs
`harness/check.py p03` → `synthesis/licence.py --emit` → `synthesis/synthesize.py`,
after snapshotting every file it can touch **by bytes** and restoring in a
`finally:`. It also runs the detectors in-process under a monkeypatched HEAD
`_path_includes`, so the "without the fix" arm needs no second checkout —
and because `_verus_file_list` calls `_path_includes`, that one patch reaches
all three Verus-side detectors as well.

**Arm `include`** (helper under `common/`, so the mutant mirror resolves it and
the only cause is the scan) — **exit 0**:

```
== the SAME planted tree, under HEAD's `_path_includes` ==
    [HEAD] _path_includes -> ['common/driver.rs']
    [HEAD] scan failures: 0
== and under TASK_099's ==
    [TASK_099] _verus_file_list keys -> ['verus.rs', 'common/driver.rs', 'common/t99_helper.rs']
    [TASK_099] scan failures: 1
        FAIL [tcb-unsafe] common/t99_helper.rs:5 `unsafe` in a shared driver file …
+ harness/check.py p03                       rc=1  check.py: FAIL
+ synthesis/licence.py --emit                rc=0  24 patterns, 96 pair verdicts
+ synthesis/synthesize.py                    rc=0  wrote results/synthesis.md
[tcb-unsafe] lines in the gate transcript: 4
results/synthesis.md MOVED: 6 line(s) differ
  line 458   -| p03-bounded-stack | 9 | 0 | 5 | 10 | 0 | exact | PASS |
             +| p03-bounded-stack | 9 | 0 | 5 | 10 | 0 | exact | FAIL |
git status --porcelain, NEW entries vs the pre-run baseline:  (none)
b2[include] exit 0
```

**Arm `opaque`** (`include!(concat!("t99_helper", ".rs"))`) — **exit 0**:

```
FAIL [tcb-unsafe] verus.rs: 1 `include!` whose argument is not a string literal. …
line 458  PASS -> FAIL
b2[opaque] exit 0
```

**Arm `deep`** (`verus.rs` → `#[path] t99_mid/mid.rs` → `#[path] h.rs`, `unsafe`
in the leaf, **no `include!` anywhere**) — **exit 0**:

```
FAIL [tcb-unsafe] patterns/p03-bounded-stack/t99_mid/h.rs:5 `unsafe` in a shared driver file …
line 458  PASS -> FAIL
b2[deep] exit 0
```

**Arm `sibling`** (TASK_098 §4A's exact spelling, helper beside `verus.rs`) —
**exit 0**, and now with the *right* message:

```
FAIL [tcb-unsafe] patterns/p03-bounded-stack/t99_helper.rs:5 `unsafe` in a shared driver file …
line 458  PASS -> FAIL
b2[sibling] exit 0
```

**Arm `none`** — ⚠ **the control FAILED, and the cause is §A's own finding.**
See the box below.

Summary, all five arms:

| arm | HEAD scan | after | gate | `results/synthesis.md` | exit |
|---|---|---|---|---|---|
| `include` | 0 failures | `FAIL common/t99_helper.rs:5` | FAIL | p03 `PASS → FAIL` | **0** |
| `deep` | 0 failures | `FAIL …/t99_mid/h.rs:5` | FAIL | p03 `PASS → FAIL` | **0** |
| `opaque` | 0 failures | `FAIL verus.rs: 1 include! not a literal` | FAIL | p03 `PASS → FAIL` | **0** |
| `sibling` | 0 failures | `FAIL …/t99_helper.rs:5` | FAIL | p03 `PASS → FAIL` | **0** |
| `none` | — | — | **PASS** | ⚠ moved 4 lines with no plant | 2 |

Every arm restored the tree byte-for-byte
(`git status --porcelain, NEW entries vs the pre-run baseline: (none)`).

---

## ⚠⚠ THE NEGATIVE CONTROL FAILED, AND IT IS THE STRONGEST RESULT IN THIS TASK

`b2[none]`: **no plant at all**, `harness/check.py p03` **PASS**, and
`results/synthesis.md` still moved **4 lines**:

```
| `< 2.00` (blank / `<2.00`)   | 120 -> 122 rows
| `2.00 … 16.00` (marked **?**)|  22 ->  20 rows
| p03 R2-R4 | small +5117.00 (+7.00) **?** / large +17244.00 (+7.00) **?**  ->  (blank, ‡)
```

**A gate re-run on a byte-identical tree moved the published table.** The
committed record holds `unsafe/O3/isolated/small.bin = 3059.0` — the LOW state —
and this shell's environment block sits in the **other** phase, where
`a2_phase.py` case A measures p03 `unsafe` HIGH. `safe_naive` is flat at
`8176.0`, so the `R2−R4` correction moves by exactly ∓7 and crosses the 2.00
floor, taking two band counts with it.

Three consequences:

1. **The ±7 is not a hypothetical about other shells. It reaches
   `results/synthesis.md` through a plain `harness/check.py` re-run**, with
   nothing in the tree changed and no environment variable set by hand.
2. **`9f8fa9d`'s already-retracted *"that zero is MEANINGFUL"* is wrong a second
   way**: a byte-identical `synthesis.md` is not reproducible even across a gate
   re-run on an unchanged tree, let alone across shells.
3. **I predicted §D would move p03/p04 and the band counts. IT DID NOT** — the
   sweep's 24 records reproduce `marginal_ir_per_call` on **0 moved keys**. So
   I chased the disagreement, and it turned into the sharpest result here.

---

## ⚠⚠⚠ THE GATE'S PUBLISHED NUMBER DEPENDS ON HOW THE GATE WAS INVOKED — REPRODUCIBLY

`.temp/t99/a5_gate_phase.py`: three full `harness/check.py p03` runs on a
**byte-identical tree**, reading `results/gate/p03-bounded-stack.json`'s
`marginal_ir_per_call` after each (record snapshotted and restored by bytes;
`git status` clean afterwards):

```
run                               safe_naive  safe_tuned      unsafe       verus
committed / post-sweep               8176.00     3418.00     3059.00     3065.00
A  bash, stdout -> FILE              8176.00     3418.00     3059.00     3065.00
B  python, stdout -> PIPE            8176.00     3425.00     3066.00     3058.00
C  bash, stdout -> FILE (repeat)     8176.00     3418.00     3059.00     3065.00
  A moved on 0 of 4 cells
  B moved on 3 of 4 cells: safe_tuned, unsafe, verus
  C moved on 0 of 4 cells
```

**A = C ≠ B: deterministic, repeatable, and it is the launcher.** `unsafe` goes
`+7` and `verus` goes `−7`, so **p03's `R5−R4` pair difference goes
`+6.00 → −8.00`** — TASK_097's sign flip, reached with **no environment variable
set by hand and nothing in the tree changed**.

**Two candidate mechanisms are dead, both measured:**

* **the launcher's environment block — INERT.** `.temp/t99/a3_launcher.py`:
  `bash → timeout → child`, `python subprocess.run → timeout → child` and the
  parent itself all hand the child **3672 bytes / 48 variables**, identical.
* **the client's stdio — INERT.** `.temp/t99/a4_stdio_phase.py` reproduces
  `check.py::_callgrind_total`'s construction with the measured binary's stdout
  on a pipe, a file and `/dev/null`:

  ```
  # cell               pipe         file      devnull
    unsafe          3066.00      3066.00      3066.00
    verus           3058.00      3058.00      3058.00
  ```

**So the axis is inside `check.py`'s own process, not inside the measured
program's environment, and I have NOT isolated it.** I am deliberately not
naming a mechanism — this project's own rule. What is established:

> **`.memory/03-measurement.md`'s framing — *"it is a property of the
> environment block's LENGTH"* — is too narrow.** The gate's own
> `marginal_ir_per_call`, and therefore four cells of `results/synthesis.md`,
> **change with how `harness/check.py` was started**, which is a variable no
> reader of the artefact can see, and which is *not* the environment block.
> ⚠ **It also means "re-run the gate and compare" is not a valid reproduction
> test for these cells unless the launcher is held fixed.**

This is why the `b2 none` control failed (b2 uses `capture_output=True`, arm B)
and why the sweep did not (`d1_sweep.sh` redirects to a file, arm A). It also
means the `MOVED` line counts in the four failing arms include those p03 rows —
harmless, because each arm asserts on `PASS → FAIL`, which is unambiguous.

---

---

## §C — the docstring, in a form that cannot go stale

`check.py::check_marginal_ir` now states the **census with its instrument, its
date and its denominator** instead of a pattern list — 24 × 6 × 2 = 288 triples,
14 marginal movers, 0 kernel-exclusive, 7 of 144 (pattern, cell) pairs over
three patterns — plus the corrected mode table, the period-32/window-16 shape,
the pair-swing-of-14 mechanism, the completeness argument for the two-pad screen,
and the standing "do not pin the environment" warning. Every earlier version's
error is named in place (*three* until TASK_096, *four* until TASK_099,
*invariant* until TASK_097-should-have).

---

## §D — the sweep

`.temp/t99/d1_sweep.sh` (a copy of `.temp/t97/c1_sweep.sh` with the log path
changed), mandatory order, nothing under `harness/` touched after it started.
Full log `.temp/t99/d1/_sweep.log`, per-pattern `.temp/t99/d1/pNN.log`.

```
p01   rc=0    338s  check.py: PASS-WITH-BLOCKED-ROWS
p02   rc=0    109s  check.py: PASS     p22   rc=0    301s  check.py: PASS
p03   rc=0     92s  check.py: PASS     p27   rc=0    205s  check.py: PASS
p04   rc=0     94s  check.py: PASS     p36   rc=0     94s  check.py: PASS
p05   rc=0     83s  check.py: PASS     p38   rc=0     95s  check.py: PASS
p06   rc=0    125s  check.py: PASS     p46   rc=0    105s  check.py: PASS
p07   rc=0     87s  check.py: PASS     p47   rc=0     78s  check.py: PASS
p08…p19  rc=0  75-129s each  check.py: PASS
=== licence.py --emit ===
wrote synthesis/licence.json: 24 patterns, 96 pair verdicts (LICENSED, NOT-LIC, UNDEC)
=== synthesize.py ===
wrote results/synthesis.md  (69428 bytes, 535 lines)
=== measure.py --check-stale ===
48 record(s) examined, 0 STALE
SWEEP DONE
```

**23 `PASS` + 1 `PASS-WITH-BLOCKED-ROWS`, 0 failures, 48 records 0 STALE — exactly
as specified.** Elapsed ≈ 47 min for the 24 gates.

### Exactly which lines of `results/synthesis.md` moved, and why

**20 hunks; 605 lines → 642.** Every one is generator text. Diff
`.temp/t99/synth_diff_FINAL.txt`, baseline `.temp/t99/synthesis.HEAD.md`
(`git show HEAD:results/synthesis.md`).

| HEAD line(s) | new | what | why |
|---|---|---|---|
| 50 | 50 | limit 2's sweep description | `one 64-byte environment variable` → `one added variable (SLB_ALIGN_PAD=z*64, i.e. **+87 bytes**…)` — **C1** |
| 52 | 52 | limit 2's knob paragraph | strikes *"it is scatter, not a trend"* for p03/p04 and states the period-32 / window-16 shape |
| — | 171-176 | +6 lines in `CALLEE_NOTE` | the `+7.00` on p03/p04 `R2-R4` is one draw of a two-state variable |
| 178 | 184 | band table, `< 2.00` row | **`**safe**: nothing real hides below the floor` → `**not safe — this is one environment phase.** ⚠ See `‡`** — §A2(a). ⚠ The row's *numbers* (`120 / 0 / 120 / 0.00`) are **unchanged** |
| 182 | 188-190 | the paragraph under the band table | now says the `< 2.00` claim was false and names the falsifier; the `?`-band paragraph rewritten around the withdrawal |
| 188 | 196-198 | licence calibration | `64-byte-longer` → `longer`, plus a new paragraph with the measured `+87` and `50.00 → 43.00` — **C1** |
| 235, 278, 317, 353 | 245, 295, 341, 384 | the four table legends | the `**?**` legend gains the `‡` marker |
| **243-244** | **253-254** | **p03/p04 `R2-R4`** | ` ‡` appended. Figures **unchanged** (`+5117.00 (+7.00) **?**` …) |
| — | 276-282 | new `‡` footnote under `R2-R4` | support `+0.00` on 16, `+7.00` on 16 of 32 |
| **286-287** | **303-304** | **p03/p04 `R3-R4`** | blank → `‡`. This is the cell that falsifies the `< 2.00` band |
| — | 326-332 | new `‡` footnote under `R3-R4` | support `-7.00` on 8, `0.00` on 16, `+7.00` on 8 of 32 |
| **323-324** | **347-348** | **p03/p04 `R5-R4` — THE FOUR WITHDRAWN CELLS** | `small +6.00 (+6.00) **?** / large +6.00 (+6.00) **?**` → `‡ **WITHDRAWN — not a quantity.** …` |
| — | 370-376 | new `‡` footnote under `R5-R4` | the two withdrawn rows, marked `⟵ WITHDRAWN above` |
| 379 | 410 | p46 `gcc-clang` | ` ‡` appended; figures unchanged — **C3**, the seventh exposed cell |
| — | 412-417 | new `‡` footnote under `gcc-clang` | p46 `c-clang` `6216.00 → 6209.00`, *2-pad screen only* |
| 498 | 535 | §5 claim 1's row list | `p03 small +6.00 …` → `p03 small **WITHDRAWN** `‡`` — the withdrawn figure was being reprinted 175 lines later |
| 500 | 537 | §5 claim 1's follow-up | *"the derived `+6.00` has the right existence and the wrong sign"* → the support and the reproducible `-1.00` |

### ⚠ ZERO measured numbers moved — and I predicted the opposite

I wrote, before the sweep, *"p03's and p04's rows WILL move and so will the band
counts; that is the finding arriving."* **Refuted by the sweep.** Recounted leaf
by leaf over all 24 gate records (24 179 leaves):

```
      95  adversarial      <- p03 28, p27 32, p05 14, p13 8, p38 6, p06 7
      40  sanitizer        <- ASan's own PID inside `diagnostic` strings
      24  source_sha256    <- one per pattern: `harness/check.py` changed
  marginal_ir_per_call keys moved: 0
```

**0 `Ir`, 0 md5, 0 identity, 0 checksum, 0 verdict.** `synthesis/licence.json`:
1857 leaves, **24 moved, all of them the per-pattern `harness/check.py` entry
inside `gate_source_sha256`** — no licence verdict moved. The `adversarial` and
`sanitizer` movers are pre-existing run-to-run nondeterminism (UB cells print a
different value each run; ASan prints its PID), not caused by anything here, and
the gate records them rather than requiring them to agree.

**So the b2 `none` control's movement is NOT reproduced by the sweep.** Chased
and settled: the difference is the **launcher**, reproducibly — see the boxed
result above (`.temp/t99/a5_gate_phase.py`).

---

## Problems

* The `none` control fails for a real reason (above). The acceptance test cannot
  currently distinguish *"the plant moved the published number"* from *"the
  environment phase moved it"* by line count alone — it distinguishes them by
  the `PASS → FAIL` assertion, which is unambiguous. I did **not** pin the
  environment to make the control quiet: that is the forbidden repair, and here
  it would have hidden the finding.
* `RECAP.md`, `.tasks/PROTOCOL.md` and three new `TASK_10N.md` task files were
  being written **while this task ran** (C7). Nothing I did touches them, and
  none of them is gate-hashed, but a concurrent editor is a hazard for a sweep.

## Unsure / not done

* **I did not re-emit `synthesis/outward_ir.json`** (352 callgrind runs). The
  `152 / 14 / 0 / 10` second-sweep figure is TASK_075_REVIEW's; I verified its
  **mechanism** directly (C1) and corrected its **description**, not its digits.
* **The 16-wide window is verified on six cells** (p03/p04 Rust rungs). The
  completeness argument for the two-pad screen inherits that scope. p46
  `c-clang` has a 2-pad screen only and is marked, not quantified.
* **`PHASE_SWEEP` is a PIN, not a derivation.** Nothing in `results/` carries a
  sweep, so a future measurement can contradict it silently. The comment says
  so and names the instrument. A generated form would need a sweep artefact in
  `results/`, which is a bigger change than this task.
* **`_check_opaque_includes` is a new failure mode** — the only one this task
  adds. Justified by the accident test (0 `include!` of any spelling in 24
  patterns; no build script in the build path) and by refusing rather than
  silently returning `[]`. A reviewer should attack it: it fires on the raw
  text, so an `include!(concat!(…))` inside a comment or a string literal would
  fail the gate.
* **I did not add a `check.py` selftest case for `_include_literals`.** The
  battery in `check_selftests` has no `_path_includes` cases at all; adding one
  is adjacent work, reported not done.
* **`_path_includes` still tests `os.path.exists`, not `os.path.isfile`.** A
  `#[path = "sub"]` naming a **directory** would be walked and `open()`ed, which
  raises. This is HEAD's behaviour too (HEAD returned it and `_scan_unsafe_sites`
  would have `open()`ed it), so the fix does not introduce it — but the walk
  touches it twice now. **I found it after the §D sweep had started and did NOT
  edit `check.py` mid-sweep** (that is TASK_096's 8-STALE mistake). One-word fix
  for the next `harness/` batch.
* **`patterns/p03-bounded-stack/NOTES.md:156`** prints `50` as a property of the
  R2 cell in its `Ir` table — the same one-draw figure as TASK_098 MINOR 5's
  §3b table. A pattern `.md` is gate-hashed, so fixing it costs a gate re-run;
  not done here, reported.
* **`.memory/02-bench-rules.md:273`'s known-residual line is now false** and is
  manager-only to fix (C5).

## Memory updates

**None** — `.memory/` and `RECAP.md` are manager-only. Durable facts to land, in
priority order:

1. **C1** — the "vacuous control" is not vacuous (`.memory/03-measurement.md`'s
   RESOLVED block asserts it; so does `TASK_098_REPORT.md` BLOCKER 2).
2. **C3** — "2 patterns, 7 of 144 cells" → **three** patterns; the seventh cell
   is p46 `c-clang`. Same block.
3. **C4** — period 32, window 16, phase per binary; "presence not size" is false
   at `-O3 isolated`; the two-pad screen is complete, not a sample.
4. **C5** — `.memory/02-bench-rules.md:273`'s residual is closed, and the
   §`include!()` section should say the residual had been recorded since
   `4abffbf`.
5. **C6** — MAJOR 4's "gate-clean `p35`" is a `_scan_unsafe_sites` statement;
   the whole gate reddens on the sibling spelling for an unrelated reason
   (`_mutant_path`).
6. **C7 — THE HIGHEST-VALUE ONE.** The ±7 is selected by the gate run's process
   image, of which the environment block is one instance and the **launcher** is
   another; `.memory/`'s *"not a property of the launching method"* is false,
   measured `A = C ≠ B` on three whole-gate runs. And **"re-run the gate and
   compare" is not a reproduction test for these cells** unless the launcher is
   held fixed.
7. **Route 5** — the transitive `#[path]` hole, closed here, previously unnamed;
   and `.memory/02-bench-rules.md:273`'s residual line is now stale.
8. **The clean negatives, so nobody re-runs them**: `macro_rules!` emitting
   `#[path] mod` was ALREADY caught (raw-text regex); `include_str!` cannot
   carry an `unsafe` token; no build script exists in the build path
   (`build.py` invokes `rustc` directly); the launcher's env block is identical
   down all three paths; the measured program's stdio is inert; and p01, p16,
   p38, p46's Rust rungs swing `0.00` over all 32 pads.
