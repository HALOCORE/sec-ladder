# TASK_103 — review of `TASK_099`. **C7's conclusion survives; its mechanism is refuted, and the retraction landed in `.memory/` struck a TRUE sentence.**

**Role: research reviewer. Nothing was fixed.** Scratch `.temp/r103/`, notes in
`.temp/r103/NOTES.md`. No `.memory/`, `RECAP.md`, `harness/`, `synthesis/`,
`results/`, `patterns/*/`, `pilot/` file was edited. No `git add`/`git commit`.
`harness/check.py p03` was run 8 times for §A; the record was snapshotted and
restored byte-identically by the probe, **and I then ran
`git checkout -- results/gate/` as instructed** (`git status --porcelain` on
`results/` is empty; the whole tree is clean outside `.temp/`).
`harness/measure.py` and `harness/build.py` were **not** run.

**Running count I was launched from: 319** (`.tasks/TASK_103.md`'s closing
paragraph). Reconciliation is the manager's job; I carry nothing forward.

---

## THE THREE CALLS, FIRST

**Call 2 — "is C7's mechanism right, or only its conclusion?" Your instinct was
right and the mechanism is wrong.** The axis is **the environment block**, exactly
as `.memory/` said before you struck it. The launcher matters only because
`bash -c "cd REPO && …"` **exports `OLDPWD=REPO`** while
`subprocess.run(cwd=REPO)` leaves `OLDPWD` at the inherited value — an **11-byte**
difference on this box. Crossed design, 8 whole-gate runs, below: **A == A2 and
B == B2.** The launcher is inert once the environment is held equal.

**Call 1 — landing the retraction before this review was the WRONG call, and the
harm is concrete rather than hypothetical.** `.memory/03-measurement.md:2412-2415`
now carries `~~It is not a property of the launching method; it is a property of
the environment block's LENGTH.~~` struck through, replaced at `:2417-2422` by
*"how the gate was launched selects which side of the bistability you land on."*
**The struck sentence is true and the replacement is false.** Rule 9 would have
caught this exactly. ⚠ But the failure is finer than "you broke rule 9": C7 is
**two claims welded together**, and only one of them needed to land. The
consequence — *"re-run the gate and compare is not a reproduction test"* — is
**true, important, and independent of the mechanism**, and leaving it out of
`.memory/` for a cycle would also have had a cost. **The available third option
was to land the consequence and mark the mechanism OPEN**, which is what the
engineer's own text asked for (*"The correction the authoritative layer needs is
the scope, not a mechanism… I am deliberately not naming one"*) — and the
`.memory/` write-up then named one anyway, in a strikethrough that reads as
settled. **That is the same defect rule 9 documents: the manager wrote the
finding from the report rather than from the measurement, and made it sharper
than the engineer had.**

**Call 3 — `kernel_exclusive_ir` upheld on the axis I could test, with two
caveats you should publish beside it.** Measured directly: kernel-exclusive
`Ir`/call moves **`0.00` on 4 of 4 p03 cells** across both the 11-byte launcher
difference and a 16-byte pad, while the marginal moves `±7` in the same runs.
Caveats: (a) **the column is not in the gate record at all** — it lives in
`results/pNN-*.json`, which only `harness/measure.py` writes, so "reproduce
against it" is not a `check.py` re-run; (b) `.memory/03-measurement.md:2013`
already says `kernel_exclusive_ir` is `None` in **302 of 318** `-O3 whole` pairs,
so the advice is `isolated`-only. It is the right column to **quote**. It is not,
by itself, a reproduction test for the gate.

---

## BLOCKER 1 — C7's mechanism is false. The launcher is inert; the environment block decides. (`.memory/03-measurement.md:2411-2422`, `.tasks/TASK_099_REPORT.md` C7)

### The instrument C7 rests on measured the wrong thing

C7 kills the environment mechanism on `.temp/t99/a3_launcher.py`: *"the env block
is **3672 bytes / 48 vars** down every launch path."* Two defects:

1. it computes `sum(len("k=v")+1) + 8*(n+1)` from `os.environ`, a Python dict,
   instead of reading `/proc/self/environ`;
2. ⚠⚠ **its arm A is not the arm whose phase differs.** `a5_gate_phase.py:49-51`
   runs `bash -c "cd {REPO} && timeout 3000 harness/check.py p03 > log 2>&1"`;
   `a3_launcher.py:38-40` runs `bash -c "timeout 60 <py> a3_launcher.py --child"`
   — **no `cd`, no `cwd=`**. `cd` exports `OLDPWD`. Without it, a3's arm A is
   byte-identical to its arm B.

Measured (`.temp/r103/a1_env_by_launcher.py`, raw `/proc/self/environ`, a5's own
command shapes):

```
arm                                  BYTES NVARS  CWD
A bash+cd, a5 shape                   3269    48  /home/apt/repos_common/sec-ladder
B subprocess cwd=, a5 shape           3280    48  /home/apt/repos_common/sec-ladder
C bash+cd repeat                      3269    48
Z A + SLB_R103_Z=abcde (must fire)    3286    49
D a3 arm-A shape (no cd, no cwd)      3280    48   <-- equals arm B, not arm A

B  only in this arm : ['OLDPWD=/home/apt/repos_common/Agentic/_lproc/.ccneo']
   only in arm A    : ['OLDPWD=/home/apt/repos_common/sec-ladder']
   delta bytes vs A = +11
MUST-FIRE ARM Z: delta=+17, predicted +17 -> FIRED
```

`3280 + 8*(48+1) = 3672` — **a3's own number, reproduced, and it is arm B's.**
Arm A is `3661`, and a3 never produced it.

### The crossed experiment: 8 whole `harness/check.py p03` runs

`.temp/r103/a2_arms.py` + `.temp/r103/a3_gate_crossed.py`. Each arm's environment
is verified from `/proc/self/environ` **before** its gate run. `A2` = **B's
launcher with A's environment**; `B2` = **A's launcher with B's environment**.
If the launcher is the axis, `A == B2` and `B == A2`. If the environment is the
axis, `A == A2` and `B == B2`.

```
run                                 envB   safe_naive safe_tuned    unsafe     verus
committed                              -      8176.00   3418.00   3059.00   3065.00
00 A  bash+cd    file   env=short   3269      8176.00   3418.00   3059.00   3065.00
01 B  subproc    pipe   env=long    3280      8176.00   3425.00   3066.00   3058.00
02 A2 subproc    pipe   env=SHORT   3269      8176.00   3418.00   3059.00   3065.00
03 B2 bash+cd    file   env=LONG    3280      8176.00   3425.00   3066.00   3058.00
04 Z0 bash+cd    file   short+pad0  3283      8176.00   3425.00   3059.00   3065.00
05 Z16 bash+cd   file   short+pad16 3299      8176.00   3418.00   3066.00   3058.00
06 A  (repeat)                      3269      8176.00   3418.00   3059.00   3065.00
07 B  (repeat)                      3280      8176.00   3425.00   3066.00   3058.00
record restored byte-identical: True
```

**`A == A2` and `B == B2`, on all 8 keys, with `A` and `B` each run twice.**
The gate's number is a function of the environment block and of nothing else that
distinguishes these arms — not the launching program, not `stdout`-to-pipe vs
`stdout`-to-file, not the parent process. This also reproduces C7's own
`A = C ≠ B` table to the instruction (`8176 / 3418 / 3059 / 3065` against
`8176 / 3425 / 3066 / 3058`) — **C7 measured a real effect and misattributed it.**

**The must-fire pair fired, and it says something extra.** `Z0` (3283) and `Z16`
(3299) differ by exactly 16 bytes and are in opposite states — but they flip
*different cells*: `Z0` moves `safe_tuned` only, `Z16` moves `unsafe` and `verus`
only. That is C4's *"period 32, window 16, phase per binary"* reproduced in a
third session **through a different knob** (an `OLDPWD`/pad length rather than
`SLBPAD`). C4 is independently confirmed.

### It closes TASK_099's own loose end, too

`.temp/t99/d1_sweep.sh:8` opens with `cd /home/apt/repos_common/sec-ladder`;
`.temp/t99/b2_source_to_published.py:186-187` uses
`subprocess.run(..., cwd=REPO, capture_output=True)` and no `cd`. **That is
exactly the arm-A / arm-B pair.** The `b2 none` control failed, and the §D sweep
did not, because of an 11-byte `OLDPWD` — i.e. **because of the environment
block's length**, the mechanism C7 declared dead.

### What `.memory/` should say instead

Not the struck sentence, and not the retraction. Both are too coarse:

> The ±7 is selected by the **length of the environment block the measured
> process receives**. **The launching method matters exactly and only through the
> bytes it puts there** — `bash -c "cd repo && …"` exports `OLDPWD=repo` and
> `subprocess.run(cwd=repo)` does not, an 11-byte difference on this box, enough
> to cross a 16-wide window in a 32-byte period. **The launcher itself is inert:
> the same environment through either launcher gives the same number
> (`.temp/r103/a3_gate_crossed.py`, 8 whole-gate runs, `A == A2`, `B == B2`).**
> ⚠ **The consequence stands unchanged and is the point: *"re-run the gate and
> compare"* is not a reproduction test for an `-O3 isolated` marginal**, because
> two equally natural ways of invoking the gate hand it different environments
> and nothing in the artefact records which one you got.

---

## §A's deliverable — what IS a valid reproduction test for an `-O3 isolated` marginal?

**Pick: record the environment-block length in the gate record, and define
reproduction relative to it.** One integer,
`len(open("/proc/self/environ","rb").read())`, written beside
`marginal_ir_per_call`. Then:

- **same recorded length ⇒ the marginal must match exactly**, and a mismatch is a
  real change. (Demonstrated: arms 00/02/06 agree to `0.00` across three runs and
  two launchers; 01/03/07 likewise.)
- **different length ⇒ the marginal is not comparable.** Quote
  `kernel_exclusive_ir`, or re-run at the recorded length.

**Why this and not the alternatives.**

- It is **not** the forbidden pin (`.memory/03-measurement.md:2543`). It does not
  force an environment and cannot make the number *reproducible-and-wrong*; it
  records which draw you took, so a disagreement becomes **diagnosable** instead
  of mysterious. `check.py` is not measurement-hashed, so the cost is a gate
  re-run.
- **"Declare the column unreproducible"** overstates the finding: the column *is*
  reproducible, on a variable nobody was recording. Saying otherwise throws away
  120 rows that never move.
- **"Reproduce only `kernel_exclusive_ir`"** is right about which number to
  *quote* and wrong as a *test*: that column is not in `results/gate/` at all, so
  it cannot be checked by re-running the gate, and it is `None` for 302 of 318
  `-O3 whole` pairs.
- **Complement, for the exposed cells only:** publish the **pair**, by re-running
  at recorded length `L` and `L+16`. C4's window-16-in-period-32 argument makes
  that two-point screen complete, and it is ≈2 min/pattern on the two patterns
  that need it. That turns the four withdrawn cells' `‡` footnote from
  *"unresolvable"* into *"two-state, and this record is in state X"*.

⚠ Scope I did **not** establish: that the axis is length *alone* rather than
length-plus-content. `A` and `A2` have byte-identical environments, so the design
separates *launcher* from *environment* cleanly; it does not separate *length*
from *content*. The 32-pad sweeps (`.temp/r98/p03_sweep.json`) are the evidence
for length, and I did not re-derive them.

---

## MAJOR 2 — `a3_launcher.py` is entry SEVEN for the controls-that-could-not-have-fired list

`.memory/03-measurement.md:2549-2590`. This one is the same shape as entry 5 and
entry 6: **both of its arms were the same arm.** Arm A had no `cd` and no `cwd=`,
so the one variable it existed to vary — the environment the two *gate* arms
receive — was held constant by construction. It could only ever print
"identical", and it did, and a blocker was built on it.

⚠ **The generalisable reflex, and it is not the one already on the list:** entry
5's lesson is *"compute the alignment from the bytes, not from the prose."*
This one's is **"a control must reproduce the COMMAND, not the idea of the
command."** a3 modelled *"bash versus python"*; the arms that differed were
*"`bash -c "cd X && cmd"` versus `subprocess.run(cmd, cwd=X)"`*, and the `cd` was
the whole effect.

Every probe in this review carries an arm that must fire, and each one did:
`a1` arm Z (`+17` predicted, `+17` measured); `a3` arms `Z0/Z16`; `a4` arm Z;
`b1` `CONTROL-plain`; `b2` `real`; `b2b` the `verus.rs` arm; `c1 --selfdiff`
(24 179 leaves, 0 moved); `c2` pad0-vs-pad0 (288 triples, 0 movers).

---

## MAJOR 3 — a SEVENTH, EIGHTH and NINTH route past `_path_includes`, all `1 verified, 0 errors`

`.temp/r103/b1_routes7.py --verus`. TASK_099's route table varied the *`include!`
spelling* and the *depth*; it never varied the spelling of the **`#[path]`
attribute itself**, which `check.py:3421` matches with
`re.findall(r"#\[\s*path\s*=\s*\"([^\"]+)\"\s*\]", txt)`.

```
route                      walk returns   needs         verdict
CONTROL-plain (must fire)  ['h.rs']       h.rs          scanned
R7a cfg_attr-gated path    []             h.rs          *** UNSCANNED -- HOLE ***
R7b raw-string path        []             h.rs          *** UNSCANNED -- HOLE ***
R7c nested inline mod      []             x/m.rs        *** UNSCANNED -- HOLE ***

Does Verus/rustc actually ACCEPT each route? (./verus_run.py)
  CONTROL-plain              rc=0  verification results:: 1 verified, 0 errors
  R7a cfg_attr-gated path    rc=0  verification results:: 1 verified, 0 errors
  R7b raw-string path        rc=0  verification results:: 1 verified, 0 errors
  R7c nested inline mod      rc=0  verification results:: 1 verified, 0 errors
```

- **R7a `#[cfg_attr(all(), path = "h.rs")] mod m;`** — the attribute does not
  *start* with `path`, so `#\[\s*path` cannot match. ⚠ This is **the** standard
  Rust idiom for platform-selected module files
  (`#[cfg_attr(unix, path = "unix.rs")] mod imp;`).
- **R7b `#[path = r"h.rs"] mod m;`** — a raw string is a legal attribute value
  and `\s*\"` cannot match the leading `r`. TASK_099 tested the raw-string
  spelling of `include!` and not of `#[path]`.
- **R7c `mod x { mod m; }`** — rustc resolves this to `x/m.rs` (its own `E0583`
  help says so); the `mod m;` fallback at `check.py:3428-3430` looks for `m.rs`
  and `m/mod.rs` **beside the including file**. ⚠ **No attribute and no macro at
  all** — this is the most accident-reachable of the three, and it is the same
  shape as TASK_099's own route 5.

In all three the `unsafe` in the target file is unscanned by
`_scan_unsafe_sites`, `_check_twin_cfg_hygiene` and the three Verus-side
detectors, and the gate is otherwise green.

**The real finding is the method, not the three spellings.** TASK_099 wrote the
right sentence — *"`0 hits` bounds today's tree against the spellings someone
thought to grep for"* — and then shipped another spelling table. `_path_includes`
is a regex approximation of rustc's module resolution and will not converge.
**The compiler will hand over the exact file set for one flag**, on a compiler
this project already invokes directly (`harness/build.py:54`, `verus_run.py`):

```
$ .temp/r103/b3_depinfo.sh          # rustc --edition 2021 --emit=dep-info main.rs
--- main.d ---
main.d: main.rs h.rs x/y.rs
```

— on a `main.rs` containing **both** R7a and R7c. That is the complete set, from
the authority, with no regex. **Reported as adjacent work; I did not implement
it.** By `.memory/02-bench-rules.md`'s own threat model these three are otherwise
"known residuals" (R7a is accident-reachable, R7b is not, R7c is borderline), and
"prefer producing a pattern over hardening the gate" applies — **but the residual
list should name them, because TASK_099's route table currently reads as
exhaustive and is not.**

---

## MAJOR 4 — `_check_opaque_includes` false-positives on every comment shape, and its one unusable diagnostic

`.temp/r103/b2_opaque_fp.py`. It reads the **raw** text (`check.py:3466`).
`_path_includes` reads raw text deliberately, because over-approximating a
*file set* is the safe direction; `_check_opaque_includes` **turns the whole gate
RED**, where over-approximation is the unsafe direction.

```
real   opaque include! in live code (must fire)      -> gate FAIL   [must fire: FIRED]
FP-1   line comment quoting the idiom                -> gate FAIL
FP-2   //! doc comment quoting the idiom             -> gate FAIL
FP-3   block comment quoting the idiom               -> gate FAIL
FP-4   the idiom inside a STRING literal             -> gate FAIL
FP-5   a commented-out include! of a REAL literal    -> gate FAIL
clean  no include! at all                            -> gate pass
```

The accident route is specific and near: `include!(concat!(env!("OUT_DIR"),
"/gen.rs"))` is now the canonical example sentence in `check.py`'s own docstring,
in `.memory/02-bench-rules.md` and in two reports. **The first author who quotes
it in a rung-source doc comment fails the gate**, and this tree's `.rs` files are
heavily doc-commented. FP-5 is the sharpest: a *commented-out*
`include!("does_not_exist.rs")` produces
`Point it at a real file or delete it.` — advice about a line the compiler never
sees. Cheap fix (not applied): run the scan on `vparse.blank_noncode(txt)` for
*this* check while `_path_includes` keeps the raw text.

**Answering §B's question directly — "is a legitimate use now impossible, and is
the message good enough?"** The refusal is correct (the gate genuinely cannot
scan a computed path) but **the remedy it prints is not actionable for the case
it names**: for the build-script idiom there *is* no literal path, so
*"Use a literal path"* tells the author to do the one thing that cannot be done.
It bites the day someone adds a codegen step; today `build.py` invokes `rustc`
directly with no `OUT_DIR`, so nothing is lost. The message should say the shape
is unsupported and name the alternative (generate at author time, commit the
file).

**Scope gap in the same check** (`.temp/r103/b2b_opaque_scope.py`):
`_check_opaque_includes`'s file list is *obligation sources* + *what
`_path_includes` returns*, and `_path_includes` returns the includes, never the
roots. So an opaque `include!` in `safe_tuned.rs` — a rung the ladder asserts is
`unsafe`-free — is **not refused**, `_path_includes` returns `[]`, and
`_scan_unsafe_sites` sees nothing:

```
opaque include! in safe_tuned.rs             opaque-check=pass  unsafe-scan=pass  walk=[]
opaque include! in verus.rs  (must fire)     opaque-check=FAIL  unsafe-scan=pass  walk=[]
```

Severity is capped at **minor** because I could find no stage that scans the safe
rungs for an `unsafe` token at all (no `forbid(unsafe_code)` in any rung source,
no such check in `check.py`), so this is a pre-existing scope, not a regression.
⚠ It is worth a sentence in `.memory/` all the same: the new check covers the
Verus obligation graph, not the ladder.

---

## §B — the two disclosed weaknesses, measured

**The fixed point TERMINATES on a cycle.** Clean negative — do not re-run it.
`a.rs` `include!`s `b.rs` `include!`s `a.rs`, under a 60 s wall clock:

```
CYC  rc=0  ['…/CYC-cycle/a.rs', '…/CYC-cycle/b.rs']
```

`walked` is a set of `realpath`s and every file is enqueued at most once
(`check.py:3439-3441`), so the queue is bounded by the file count. A self-include
terminates for the same reason. **The gate does not hang.**

**`exists` vs `isfile` — the failure moved, and it got slightly worse.** The
disclosure says HEAD *"returned it and `_scan_unsafe_sites` would have `open()`ed
it"*. Now the walk itself opens it:

```
DIR  a DIRECTORY named h.rs, reached through `#[path]`:
   *** IsADirectoryError: [Errno 21] Is a directory: …/DIR-directory/h.rs ***
```

The exception is raised **inside `_path_includes`** (`check.py:3420`), so it now
also kills `_check_opaque_includes` and `_verus_file_list` — three call sites
instead of one, and as an uncaught traceback rather than a stage failure.
Reachability is genuinely contrived (a directory whose name ends `.rs`), so this
stays **minor**; the engineer's "one-word fix for the next `harness/` batch" is
the right call, and `isfile` should also guard the `queue.append`.

---

## §C — the accounting, verified rather than the headline

**24 179 leaves and `0` `marginal_ir_per_call` movers: CONFIRMED**
(`.temp/r103/c1_leafdiff.py`, every `results/gate/*.json` leaf at `032bfd3^`
against `032bfd3`; must-fire arm `--selfdiff` = 0 moved of the same 24 179).

```
before=032bfd3^  after=032bfd3   files 24 -> 24
leaves at `after`: 24179
moved 155   added 2   removed 2
     91  adversarial      <- p03 28, p05 14, p06 7, p13 4, p27 32, p38 6
     40  sanitizer
     24  source_sha256
marginal_ir_per_call keys moved: 0
```

**Minor correction to the report's classification.** It prints
`95 adversarial <- … p13 8`. The truth is **91 moved + 2 added + 2 removed**, and
the four extra are all `p13-strncpy-trunc.json`'s `c-clang` adversarial cells
changing **list index**, not value:

```
ADDED:   adversarial/adversarial-nonul-dst.bin/c-clang/[0]/cells/[1]
         adversarial/adversarial-truncate.bin/c-clang/[2]/cells/[1]
REMOVED: adversarial/adversarial-nonul-dst.bin/c-clang/[1]/cells/[1]
         adversarial/adversarial-truncate.bin/c-clang/[0]/cells/[1]
```

The headline arithmetic (95+40+24 = 159 = 155+4) is internally consistent and the
conclusion is unaffected — `0 Ir, 0 md5, 0 identity, 0 checksum, 0 verdict`
reproduces exactly. ⚠ Worth recording as a durable fact: **a p13 gate re-run
reorders the `c-clang` adversarial list**, so a naive JSON diff of that record
overstates change by four leaves.

**The `synthesis/`-is-in-neither-hash argument HOLDS.** Read, not taken on trust:
`check.py:7513-7523`'s `srcs` glob is `pdir/*.rs`, `pdir/c/*`, `pdir/*.md`,
`pdir/model.py`, `common/driver.*`, `harness/*.py`, `pdir/inputs/gen.py`,
`pdir/controls/*.py`, `common/*.py`, `common/layout/*.py`, `verus_run.py`;
`measure.py:224-235`'s `measurement_sources` is `pdir/*.rs`, `pdir/c/*`,
`model.py`, `inputs/gen.py`, `common/driver.*`, `common/slb.py`,
`harness/{build,asm,measure}.py`, `verus_run.py`. **No `synthesis/` entry in
either.** `d1_sweep.sh` runs `licence.py --emit` and `synthesize.py` after all 24
gates, and nothing in `results/` records a hash of `synthesis/*`. Unlike
TASK_096, `harness/check.py` was not touched after the sweep began — the 24
`source_sha256` movers above are the *pre-sweep* `check.py` change, one per
pattern, exactly as claimed. **Clean negative.**

**C3's seven, NAMED** (`.temp/r103/c2_seven.py`; must-fire arm pad0-vs-pad0 =
288 triples, 0 movers). `7 of 144` = 24 patterns × 6 cells; `288` = × 2 blobs:

| # | pattern | cell | small.bin | large.bin |
|---|---|---|---|---|
| 1 | p03 | `safe_tuned` | 3418.00 → 3425.00 | 9067.30 → 9074.30 |
| 2 | p03 | `unsafe` | 3059.00 → 3066.00 | 8441.30 → 8448.30 |
| 3 | p03 | `verus` | 3065.00 → 3058.00 | 8447.30 → 8440.30 |
| 4 | p04 | `safe_tuned` | 3425.00 → 3432.00 | 11724.00 → 11731.00 |
| 5 | p04 | `unsafe` | 3420.00 → 3427.00 | 11719.00 → 11726.00 |
| 6 | p04 | `verus` | 3426.00 → 3419.00 | 11725.00 → 11718.00 |
| 7 | **p46** | **`c-clang`** | 6216.00 → 6209.00 | 23230.66 → 23223.66 |

`kernel_exclusive` moved on **0 of 288** in the same scan. **C3 confirmed
exactly**, including that it is three patterns and that p46's is the seventh.

---

## MINOR — a pasted evidence line in C2 does not reproduce (the conclusion does)

C2 pastes:

```
$ git show 711d9c7 -- harness/check.py | grep -c check_marginal_ir
0
```

I get **1** — `git show <rev> -- <path>` prints the commit message first, and
`711d9c7`'s message contains *"check_marginal_ir's docstring says -O3 isolated
is 'not merely inferred'"*. **C2's conclusion is right and I confirmed it a
different way**: `711d9c7`'s hunks in `check.py` are at `@@ -3968`, `-4123`,
`-4132`, `-7195`, `-7301` — none of them inside `check_marginal_ir`
(≈2513-2680), and `git show 9b138b5:harness/check.py` still carries
*"only cell class no probe has moved"* at `:2597`. **A pasted command whose
output cannot be re-obtained is exactly what a disclosure is supposed to prevent
(PROTOCOL "definition of done" 6's `git show` amendment); flagging it so the
citation is not inherited as-is.**

Also verified, **clean negatives, do not re-run**:
`.memory/02-bench-rules.md:273`'s residual line and its provenance
(`4abffbf`, 2026-08-17) are exactly as C5 states, and the line is now correctly
struck through in the file.

---

## Clean negatives — named attacks that did NOT land

1. **"C7 is just RECAP settled answer 1 (source-path-length) seen from another
   angle."** No. The `cwd` is `/home/apt/repos_common/sec-ladder` in *every* arm
   (printed by `a1_env_by_launcher.py`), the binary and probe paths are identical
   across arms, and `A2` differs from `A` in launcher/stdio/parent while agreeing
   to `0.00`. It is `OLDPWD`'s **value length inside the environment block**, not
   the path the tree lives at.
2. **"The fixed point hangs on a cycle."** It terminates; `walked` is a realpath
   set (above).
3. **"`kernel_exclusive_ir` has a hole on the launcher axis."** It does not:
   `0.00` on 4 of 4 p03 cells across an 11-byte and a 16-byte perturbation, with
   the marginal moving `±7` in the same runs.
4. **"The client's stdio selects the phase."** Independently confirmed inert by
   the crossed design (`A` file-redirect vs `A2` pipe, identical).
5. **"A mid-sweep `synthesis/` edit could stale a record."** It could not; the
   two hash globs read and quoted above contain no `synthesis/` path.
6. **"The `0 marginal keys moved` headline hides a real move."** It does not —
   leaf-by-leaf over 24 179 leaves, with a self-diff must-fire arm.
7. **"C3's 7-of-144 is another loose count."** It is exact; the seven are named.
8. **`include_str!`, `macro_rules!`-emitting-`#[path]`, and the build-script
   route** were already settled by TASK_099 and I did not re-run them.

---

## Severity summary

| # | severity | finding |
|---|---|---|
| 1 | **blocker** | C7's mechanism is false; `.memory/03-measurement.md:2412-2422` struck a true sentence and replaced it with a wrong one. The launcher is inert; the environment block decides. Landing it pre-review was the wrong call. |
| 2 | **major** | `.temp/t99/a3_launcher.py` is a control that could not have fired — entry **7**. Both its arms were the same arm. |
| 3 | **major** | Three new `_path_includes` routes (`#[cfg_attr(…, path=…)]`, `#[path = r"…"]`, `mod x { mod m; }`), all `1 verified, 0 errors`. The route table reads exhaustive and is not; `rustc --emit=dep-info` closes the class. |
| 4 | **major** | `_check_opaque_includes` fails the gate on `include!` inside comments and string literals (5 of 5 shapes), and its diagnostic prescribes the one thing the named case cannot do. |
| 5 | minor | C2's pasted `git show … | grep -c` line returns `1`, not `0`. Conclusion independently confirmed. |
| 6 | minor | §D's `95 adversarial … p13 8` is 91 moved + 2 added + 2 removed; p13's `c-clang` adversarial list **reorders** between runs. |
| 7 | minor | `exists`-not-`isfile` now raises `IsADirectoryError` **inside** `_path_includes`, reaching three call sites instead of one. |
| 8 | minor | `_check_opaque_includes` does not cover non-obligation rung sources (`safe_tuned.rs` et al.). Pre-existing scope, worth stating. |

**What TASK_099 got right and should be kept:** C1 (already manager-verified),
C3 (exact, and now enumerated), C4 (independently reproduced here in a third
session through a different knob), C5, C6, the withdrawal's *form* (`WITHDRAWN`
+ support beats blank or a bare range, and the reason given is correct), the
`b2` acceptance test's five arms, and — above all — **C7's conclusion**, which
is the most important sentence in the report and survives untouched.

## Unsure / not done

- I did **not** separate *environment length* from *environment content*. `A` and
  `A2` have byte-identical environments, so launcher-vs-environment is settled;
  length-vs-content rests on `.temp/r98/p03_sweep.json`, which I did not
  re-derive.
- Everything in §A is **p03 only**. p04, p38 and p46 remain unprobed on the
  launcher axis, as they were before.
- `kernel_exclusive_ir` was measured by hand from `callgrind_annotate` (validated
  against the gate record, which it reproduces exactly), **not** by
  `harness/measure.py`, which this task forbade. The `results/pNN-*.json` column
  itself is unre-measured.
- I did not attack C6's `_mutant_path` analysis or re-run the `b2` arms.
- I did not check whether the three new routes are reachable through
  `harness/build.py`'s `rustc` invocation for the **non-Verus** rungs; only
  `verus_run.py` acceptance was measured.
- Concurrency: `TASK_102` was live in `.temp/t102/` throughout. It is barred from
  `results/`; my 8 gate runs rewrote `results/gate/p03-bounded-stack.json` and
  restored it byte-identically, and `git checkout -- results/gate/` was run
  afterwards. If TASK_102 read that file between 14:44 and 14:59 it saw a
  transient value.

## Memory updates

**None** — `.memory/` is manager-only and reviewers do not fix. Durable facts to
land, in priority order:

1. **The C7 correction above**, replacing *both* the struck sentence and the
   retraction. The consequence sentence stays; the mechanism sentence becomes
   "the environment block, and the launcher only through it."
2. **The process verdict on rule 9**: the exception was not defensible as taken,
   and the reason is that a two-part finding was landed as one. Land the
   consequence, mark the mechanism OPEN.
3. **Entry 7** on the controls-that-could-not-have-fired list, with its own
   lesson: *a control must reproduce the COMMAND, not the idea of the command.*
4. **Routes 7/8/9**, and the `rustc --emit=dep-info` recommendation that retires
   the whole class.
5. **`_check_opaque_includes` false-positives on raw text**, plus its scope
   (obligation graph, not the ladder).
6. **The reproduction protocol**: record the environment-block byte length in the
   gate record; same length ⇒ exact match required; different ⇒ compare
   `kernel_exclusive_ir` or re-run at the recorded length.
7. **p13's `c-clang` adversarial list reorders between gate runs.**
8. `.tasks/TASK_099_REPORT.md` C2's pasted `git` line should be corrected in
   place or annotated, so it is not inherited.
