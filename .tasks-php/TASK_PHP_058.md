# TASK_PHP_058 — **MEASURE `inside_share` ON `ph03`, `ph16`, `ph29`.** ⭐⭐⭐ `TASK_PHP_057`'s BINDING resume priority: five built rows never measured it, three of those publish an `A1` headline, and the one at the centre of the programme's largest open thread has its only figures in a **docstring that disclaims the comparison we publish from it**

> ⚠ **Item 127.** The reviewer wrote that this is *"more important than any
> finding in this round, including the one it came out of."* `_057` §9 installed
> the rule that a reviewer's stated resume priority BINDS the manager, and F123
> is the record of what happens when one is quietly re-ranked. **This task is
> that rule being obeyed, and if it is not the next thing done, say so in writing
> with a reason — do not just do something else.**

## §0 ⛔ READ FIRST, IN THIS ORDER

1. `RECAP_PHP.md` — the START HERE box, then the ⭐ **which statistic** cell, then
   findings **F108**, **F109**, **F119**, **F125**, **F127**, then items **127** and **128**.
2. `.memory-php/03-numbers.md` — it treats `inside_share` as a live per-cell
   discipline. ⛔ **On 5 of 11 rows it is aspirational.** That gap is this task.
3. `patterns-php/ph97-optarg-unwritten/controls/inside_share.py` — **the template.**
   Read its whole docstring; it is the argument, not just the code.
4. `patterns-php/ph29-recvfrom-alloc/controls/spellings.py` lines 39–55 — the
   docstring §2.3 takes apart.
5. `.tasks/PROTOCOL.md` and `.tasks-php/PROTOCOL_PHP.md` §H (validators land with
   their must-fire negatives INSIDE them).

## §1 What is true, measured by the manager at `6bff271`, so you need not re-derive it

⚠ **These are the premises. `PROTOCOL.md` rule 14: a premise in a task file is one
you have no reason to doubt — so every one below carries the command that produced
it, and if any is false that is a finding worth more than the task.**

| premise | how it was measured | value |
|---|---|---|
| the three rows have **no** `inside_share` anywhere | `grep -rlan inside_share patterns-php/` | `ph03`, `ph16`: absent. `ph29`: one **docstring** in `controls/spellings.py`, no `.json` |
| all four rows share `ph97`'s cell/input shape **exactly** | `marginal_ir_per_call` keys in each `results-php/gate/*.json` | 8 cells × {`small.bin`, `large.bin`}, 96 entries each |
| the `kernel` symbol **survives** at `O3/isolated` | one `callgrind_annotate` on `ph03/safe_naive-O3-isolated`/`large.bin` | `safe_naive::kernel` = **95.03 %** of PROGRAM TOTALS |
| one callgrind run is **cheap even on the 8.4 MB input** | `time valgrind --tool=callgrind` on the heaviest-looking cell | **6.6 s** (1,444,434,324 Ir) |
| one re-gate costs | `time python3 harness-php/gate.py ph03-uudecode-bound` | **2 m 29 s**, `check.py: PASS` |
| `_pin.py` exists in **three** rows only | `ls patterns-php/*/controls/_pin.py` | `ph55`, `ph56`, `ph97`. **Not in the three rows you are editing** |
| `n_iters` is **readable**, not guessable | `common-php/slb.py::read(path).n_iters` | `ph03` 25000/20000 · `ph16` 25000/12000 · `ph29` 25000/12000 · `ph97` 20000/3000 |

⭐ **So the row-level cost is ~2 min of callgrind + 2 m 29 s of gate, and the
budget is dominated by the gate, not the measurement.** ⛔ **I asserted *"~20 min
+ 3 re-gates"* in item 127 before measuring any of it.** It happens to be about
right. **That it happens to be right is luck, and F123 is the finding about
exactly this** — a cost asserted, then inherited, then acted on.

## §2 THE WORK

### 2.1 Write ONE control and port it three times — but **derive what `ph97` hardcoded**

`ph97`'s template hardcodes

```
CALLS = {"small.bin": 20000, "large.bin": 3000}
```

with a comment saying the numbers came *"from the payload header, not guessed"*.
✅ **Both literals are correct today** — I checked them against `slb.read`. ⛔ **And
they are still literals, and the three rows you are porting to have three
*different* pairs.** Copying the pattern would add six more hand-maintained
numbers to a programme in which **a count in prose or in a tool has now rotted
nine times** (item 73).

▶ **Read `n_iters` from the input file** via `common-php/slb.py`, which is already
the reader `inputs/gen.py` and `harness/check.py` share. **A derived number cannot
go stale when the input is regenerated; a copied one silently can.**

⚠ **Fix it in `ph97` too**, in the same edit. Leaving the template carrying the
defect its own copies were told to avoid is how the *"fixed one limb"* class
(F122, F127) keeps recurring. **`ph97` must be re-gated for that change** — so
this task is **four** re-gates, not three. ⭐ **That is the honest cost and it is
the reason to state it up front rather than discover it at the end.**

### 2.2 The pin

The three rows have no `controls/_pin.py`. ⛔ **Do not skip the pin.** A sidecar
with no `derived_from_sha256` is one `check.py` stage 9b cannot call `STALE`, and
an unpinnable number is the thing this whole task exists to stop being.

▶ **Copy `ph97/controls/_pin.py` into each row and change the one `ROW` constant.**
⚠ Read its docstring first: **paths are written in the SHIM's view**
(`patterns/<row>/…`, not `patterns-php/<row>/…`) because `check.py` re-hashes them
relative to the root `gate.py` runs it under. ⚠⚠ **A pin written the other way
hashes nothing and the stage reports every path ABSENT — which it SHOUTS rather
than FAILS, so it is the quietest possible way to have no pin at all.** Check the
gate output says `FRESH` for your new sidecar and not something else.

### 2.3 ⭐⭐⭐ `ph29` IS THE POINT OF THE TASK. The other two are the control.

`ph29/controls/spellings.py` says, of this row:

> *"A1 is the headline only where the two compared cells have comparable callee
> share, which R3-vs-R4 on this row does (`inside_share` 0.655 vs 0.669); it is
> **NOT right for this row's C-vs-Rust column (0.927 vs 0.655) and that comparison
> is not made here**."*

⛔⛔ **And `RECAP_PHP.md`'s *which statistic* cell makes exactly that comparison
from exactly this row** — *"on `ph29/large` A says C is **+33 %** dearer than naive
safe Rust"* — **the single most-cited number in the programme's largest open
thread.** Item 127 currently rules it **UNDER-QUALIFIED, not wrong**: nobody has
shown it false and nobody has shown it admissible.

**Four questions, and each is a publishable answer either way:**

**(a) Do the docstring's four numbers reproduce?** `0.655` / `0.669` / `0.927` /
`0.655`. They are **fractions**, i.e. 65.5 % / 66.9 % / 92.7 %. Your matrix is in
percent; convert once and say which way.

**(b) ⭐ WHICH CELL ARE THEY?** ⛔ **The docstring names no input, no `-O`, and no
mode.** `inside_share` is **per-CELL** (F109 / `.memory-php/03-numbers.md`) — on
`ph52` it is 22.24 % on the C rungs and ≈98.6 % on the Rust ones. **So the
disclaimer that the programme's biggest caveat rests on is itself missing three of
F108's five things.** ▶ If your matrix has a cell that reproduces all four, name
it. **If more than one does, or none does, that is the finding.**

**(c) ⭐⭐ WHICH C?** The docstring says C is `0.927`. **F108's fifth thing is
WHICH COMPILER, with both columns.** There are two C columns here and the
docstring names neither. ▶ Report `c-gcc` **and** `c-clang`. **If they differ
materially, the disclaimer is not merely under-specified — it is a one-compiler
claim standing in for both.**

**(d) The verdict on the `+33 %`.** With the matrix in hand, does the
`C`-vs-`safe_naive` comparison on `ph29/large` meet the comparable-callee-share
bar the docstring sets, or not? ⛔⛔ **DO NOT SOFTEN THIS EITHER WAY.** If it does
not, the programme has been publishing a headline its own row disclaims and
`RECAP_PHP.md` must say so. If it does, the docstring's disclaimer is too strong
and should be narrowed. ⚠ **A third outcome is live and is the most likely: the
bar is not a threshold anybody ever wrote down, and *"comparable"* has no
definition.** ▶ **Then say that, and do not invent one** — report the numbers and
route the definition to the manager as an open item.

### 2.4 ⛔ A HIGH SHARE IS NOT A CERTIFICATE, AND THE MATRIX MUST SAY SO

**F109**: `ph55`'s C cells sit at 74–83 % and A1 still read `0.000 %` on that
row's own defect site, because the defect lived in an **uninlinable callee**.
▶ What decides a statistic is whether **the DIFFERENCE** lands inside the symbol,
not the level. ⚠ **Your control prints the level.** Carry `ph97`'s warning line
into every copy, and do not let a high number in your report become a claim that
A1 is safe on that row.

### 2.5 The `whole` cells are deliberately absent

At `O3` in `whole` mode the kernel is inlined into `main` and there is no `kernel`
symbol to be exclusive of, so the ratio is **undefined, not 100 %**. `ph97`'s
template already says this. ⚠ **Keep the sentence; a reader who finds only
`isolated` in the matrix will otherwise assume it was an oversight.**

## §3 ⭐⭐ A FREE MEASUREMENT I MADE WHILE TIMING THE GATE, AND IT BELONGS TO ITEM 128

⚠ **Quoted as an EVENT, not a state** (F119 / M2). I ran
`python3 harness-php/gate.py ph03-uudecode-bound` at `6bff271` with no source
change, and diffed the resulting record against the committed one:

* `marginal_ir_env.envp_stack_bytes` moved **3695 → 3698** (`bytes` 3303 → 3306,
  `nvars` 49 both times) — an **accidental** draw, not a constructed one.
* The record's `domain` field declares two records with different
  `envp_stack_bytes` **incomparable**.
* **All 96 `marginal_ir_per_call` cells were byte-identical** — including the
  `whole` column, which A1's structural immunity cannot protect.
* The only lines that moved were **4 ASan PIDs/ASLR addresses and 2 wall-clock
  timings**. `check.py: PASS`, 2 m 29 s.

⭐ **This is a second row, on an accidental draw, showing what item 128 says
`ph53` showed on three deliberate ones: the `domain` guard is more conservative
than these rows need.** ⛔ **It does NOT show the ±7 term is absent** — `TASK_114`
measured it firing. And a **+3-byte** draw may simply land in the same stack
alignment bucket, which nobody here has tested.

▶ **NOT your task. Do not chase it.** It is written down because the alternative
was losing it, and because a measurement that contradicts a guard is worth more
than the ten minutes it took. ⓘ **If you want one line of it:** your own gate runs
will each append a preflight record and move those same 6 noise lines. **Say so in
your report if a reviewer might otherwise read them as a result.**

## §4 TRAPS

1. ⛔ **`grep -a` ALWAYS** (F35). Gate records and callgrind output both contain
   bytes that make `grep` call a file binary and print nothing — **which looks
   exactly like a clean result.**
2. ⛔ **`rc=$?` after a pipeline reads the pipe's LAST element, not the command.**
   This has bitten this programme repeatedly. Use `${PIPESTATUS[0]}`.
3. ⛔ **No `/tmp`.** Use `.temp/`, a subdir per category, gitignored. **Keep the
   generator, delete the artefact** — the `.py` and the `.json` stay, callgrind
   `.out` files go.
4. ⛔ **You do not run `git add` or `git commit`.** Report; the manager lands it.
5. ⚠ **Do not spell a rooted path with a shell variable or a glob in prose.**
   `citecheck.py` reads it as a path citation and reports rot — **six instances so
   far, two of them created by a document warning about it.** Describe the path.
6. ⚠ **The control must build nothing.** It measures the binaries
   `gate.py --tool build` already produced, in the shim's build root, so the
   numbers describe the cells the measurement record describes. ⚠ If a binary is
   missing it must **fail loudly naming the build command**, not silently skip.
7. ⚠ **`PROTOCOL_PHP.md` §H: land the must-fire negatives INSIDE the validator.**
   A control that cannot fail is not a control. At minimum: a missing binary, and
   a cell where no `kernel` symbol is found.

## §5 THE MANAGER'S PREDICTIONS, REGISTERED BEFORE YOU RUN

⚠ **Registered so they can be refuted. Seven consecutive review rounds have
refuted manager claims; in `_055` ZERO of four reasons survived and in `_057` only
three of sixteen entries had both conclusion and reason upheld. Assume these are
wrong and check.**

* **P1** — `ph29`'s four docstring numbers **reproduce in at least one cell**, and
  that cell is `small.bin` / `O3` / `isolated`, because A1 on this row is defined
  on `small.bin` by the same docstring.
* **P2** — ⭐ **No cell reproduces all four**, because the docstring's C figure
  names no compiler and `c-gcc` and `c-clang` will differ. **P1 and P2 are
  deliberately contradictory; at most one survives, and I do not know which.**
* **P3** — `ph03` and `ph16` will read **high** (> 90 %) on every cell, like the
  95.03 % I measured on `ph03/safe_naive`, so their A1 headlines will look
  well-founded. ⛔ **And that will be worth exactly as much as F109 says it is:
  nothing, until somebody checks where the DIFFERENCE lands.**
* **P4** — the `+33 %` will turn out **under-qualified rather than false**, i.e.
  item 127's current ruling stands and the honest fix is a label, not a retraction.
* **P5** — ⭐ **the *"comparable callee share"* bar has no written definition
  anywhere in this repo**, and §2.3(d)'s third outcome is the one that happens.

## §6 DEFINITION OF DONE

1. An `inside_share.py` and its `.json` sidecar in the `controls/` directory of
   **each of the three rows**, each pinned, each with its must-fire negatives,
   each deriving `n_iters` rather than hardcoding it.

   > ⛔ **That sentence names the three rows in words because spelling the path
   > with a brace expansion is a citation `citecheck.py` reports as ROT — and it
   > did, in the first draft of this file, which is the SEVENTH instance of the
   > class and the THIRD created by a document that warns about it four sections
   > earlier (§4 trap 5).** ⭐ **Repaired by applying the rule, not by exempting
   > the file.** ⚠ It is left written down because the rate is the finding: the
   > warning is read, agreed with, and then not applied by the same author in the
   > same document — which is why item 115's class keeps being reported closed.
2. `ph97`'s template updated to derive `n_iters` too, and re-gated.
3. **Four** rows re-gated PASS, with the `check.py: PASS` line quoted per row and
   `controls_json` showing your new sidecar as `FRESH`.
4. Each row's `NOTES.md` carries its `inside_share` matrix, or says where it is.
5. §2.3's four questions answered **with numbers**, and the `+33 %` given a
   verdict in the words of §2.3(d) — including the third outcome if that is what
   you find.
6. Each of P1–P5 marked upheld / refuted / untested, **with the evidence**.
7. A `WHAT I AM UNSURE OF` section. ⚠⚠ **Item 129 is a census of exactly these
   sections and the rate at which the next task quietly demotes what they say.
   Write it for a reader who will audit it, and if you estimate a COST in it,
   MEASURE the cost or label it an estimate** — F123 is the finding about a check
   demoted on a cost nobody measured, and it cost this programme four documents
   and two rounds.
8. `.tasks-php/TASK_PHP_058_REPORT.md` written **before** anything cites it
   (`PROTOCOL.md` rule 10).
