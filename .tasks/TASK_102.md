# TASK_102 — propose NEW catalogue rows, and probe every novelty claim BEFORE writing one

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
`.memory/06-catalogue.md`'s **THE THREE PROBES + probe 4 + probe 5**, then
`RECAP.md`'s **time-waster 4** (*"run a proposed axis's novelty claim before you
write the row"*), then the **refusal block** in `.memory/06-catalogue.md`.

Scratch in **`.temp/t102/`**.

---

## Why this task exists

The 48-row catalogue was **written before the project started**. It is now
**24 built + 15 refused + 9 remaining**, and of the 9 only **`p23`** is a live
build candidate (`p24`'s cost axis measured `0.00`, `p26` needs an input band
designed, `p20`/`p21`/`p25` are deferred with measured reasons, `p40`/`p41` were
adjudicated REFUSE at `TASK_086` with measurements that never reached the
catalogue, `p42` is blocked on a leak-detector question under review right now).

**The standing user mandate is "as many realistic C patterns as possible."** With
the original list measured out, breadth now has to come from **new rows** rather
than from the leftovers. **That is what you are producing.**

⚠⚠ **AND THE MANAGER IS 0 FOR 2 AT PROPOSING ROWS.** Both axes the manager
proposed — `p48` (*"no pattern exercises `is_init`"*) and `p31` (*"provenance,
the property Miri checks and nothing else does"*) — **were refused, and both died
on their own distinguishing justification being FALSE.** `p27` exercises
`is_init` in four places including its core invariant; Miri **warns** on the
provenance round-trip and **errors only on aliasing**, which is p08's shipped
class. **Both justifications were written from source reads and `vstd` greps with
NOTHING RUN. The probe is one command and would have cost two tasks less than the
two refusals did.**

**So the deliverable is not a list of ideas. It is a list of ideas WITH THE PROBE
ALREADY RUN.**

---

## §A — the deliverable

**Return 4–6 candidate rows, ranked, each with its novelty claim MEASURED.** For
each candidate, all of:

1. **The C pattern**, in one sentence, and **why a working C programmer writes
   it** — with a real precedent (a CVE, or code in a real project you can name
   and quote). ⚠ **Fetch and read the precedent; do not cite from memory.** p19's
   apparmor citation and p46's OpenSSL `BN_mul` citation are the standard.
2. **The bug class**, and ⚠⚠ **whether the tree already has it.** The tree's
   classes today: **fourteen `index >= len`** (p01 p02 p03 p05 p07 p11 p12 p13
   p14 p16 p17 p19 p36 p46), **temporal** (p27), **non-termination** (p22),
   **UB-that-is-not-memory-unsafety** (p18), **aliasing/pun miscompile** (p38),
   **timing side channel** (p47), **overlap** (p08), **truncation** (p13),
   **in-bounds-and-invisible-to-a-safety-proof** (p04, p09), **integer overflow
   into a check** (p07, p17). ⚠ **"Another `index >= len`" is not automatically a
   refusal — the tree has fourteen — but it IS a much higher bar, and the row
   must say what it adds beyond the fourteenth.**
3. ⚠⚠ **THE NOVELTY CLAIM, STATED AS A SENTENCE THAT COULD BE FALSE, AND THEN
   RUN.** Whatever distinguishes your row — *"safe Rust cannot express this"*,
   *"Verus has no spec for this"*, *"no detector catches this"*, *"this is the
   first X in the tree"* — **is a claim about the tree or the toolchain, and
   every one of them is settleable by a `grep` plus a run.** Settle it. **A
   candidate whose novelty claim you did not run is not a candidate.**
   ⚠ **`grep ~/tools/verus/vstd/std_specs/` SPECIFICALLY** — a `vstd/<mod>.rs`
   trait declaration is **not** the specification, and that exact confusion has
   produced a false *"no spec exists"* claim **twice** (`copy_from_slice`, and
   `index_mut` at TASK_089).
4. **THE THREE PROBES + probe 4 + probe 5**, actually run:
   - **Probe 1 — does a rung boundary EXIST?** ⚠⚠ **This is the one that kills
     rows**, and it killed `p31` and `p32`/`p33`: if the bug compiles identically
     at C, safe-naive, safe-tuned and unsafe, **there is no ladder and no row.**
   - **Probe 2 — do the checked and unchecked kernels differ?** ⚠ **Use
     NORMALISED DISASSEMBLY TEXT.** The md5 forms are **broken in both
     directions**: object-file md5 **false-positives on relocations**, linked md5
     **false-negatives on any kernel with a branch or a global.**
   - **Probe 3 — what does the check cost?** ⚠ **Hoist any setup out of the
     measured loop** (a `Vec` built inside the loop once produced a spurious
     2.12×), and ⚠⚠ **a probe's SLOPE need not transfer, not just its intercept**
     — p46's probe was wrong **in sign** because its kernel signature differed
     from the shipped one and lost the range facts. **Say what your probe's
     signature does not model.**
   - **Probe 4 — is there a `vstd` spec for what R4/R5 would need?** ⚠ The grep
     is **necessary, not sufficient** (p35).
   - **Probe 5 — measure at SHIPPED SHAPE, not probe shape.** `p24` published
     `≈7.9 Ir`/element and the shipped shape is **`0.00`, byte-identical rungs**.
5. **The harm, RUN**, with ⚠ **a positive control that must fire**, ⚠ **`env -u
   LD_PRELOAD`**, and ⚠ **`grep` on the log, NEVER `head`** — a `head -4` hid
   ASan's banner for four rows of `TASK_086`'s harm table and it took two tasks
   to notice. **Report ASan and UBSan separately, and both `-O0` and `-O2`.**
6. **Can the shipped driver host it?** ⚠ **22 of 24 patterns take their payload
   from a file blob, so the kernel cannot hold a pointer** — that is what shapes
   `p27`'s handle table and what kills a naive `p29`. **A row whose bug needs a
   saved raw pointer across calls needs a design answer here, not a hope.**

## §B — starting candidates, and ⚠ THESE ARE UNPROBED MANAGER GUESSES

**Treat every sentence below as a hypothesis with a 0-for-2 track record behind
it.** Discard any of them freely; a well-argued replacement is worth more than a
dutiful probe of a bad idea. **The justifications are the parts most likely to be
false.**

- **Format-string (`printf(user_controlled)`).** *Guess: safe Rust cannot express
  it at all — `format!` takes a literal — so the rung structure is unusual: the
  safe rung is not "checked", it is "impossible".* ⚠ **Is that actually a rung
  ladder or is it a category error?** A row where R2/R3 cannot be written may be
  a **degenerate ladder**, which is a reason to refuse. **Settle that first.**
- **VLA / `alloca` with an attacker-derived size (stack clash).** Real precedent
  exists (systemd, CVE-2018-16864 family). *Guess: safe Rust has no VLA, so the
  safe rung must heap-allocate — a rung difference in ALLOCATION STRATEGY rather
  than in a check, which the tree does not have.* ⚠ **Does the harm reproduce on
  this box at all?** Guard pages and `-fstack-clash-protection` may make it
  unobservable, and **an unobservable harm is `p08`'s situation** — which shipped,
  so that is not fatal, but it must be stated.
- **Recursion-depth / stack exhaustion on nested input** (JSON/XML-shaped).
  *Guess: this is a SECOND instance of `p22`'s class — the one where SAFE RUST
  DOES NOT HELP, because safe Rust overflows the stack too.* ⚠ **The tree has
  exactly one such pattern and it is the project's most surprising finding, so a
  second instance is worth real effort** — but ⚠ **`p22`'s row also shows how
  easily this class is overclaimed** (*"R2/R3/R4 all hang"* was true of a
  **modified** kernel). **And can Verus even state a depth bound?**
- **TOCTOU on a length field read twice from a shared buffer.** *Guess: adjacent
  to `p38` but temporal rather than aliasing.* ⚠ **Most likely to collapse into
  `p38` — check that first and refuse it quickly if so.**
- ⚠ **Two more of your own.** The list above is the manager's, and the manager's
  list is the part with the measured failure rate.

## §C — what a good answer looks like

⚠⚠ **REFUSING ALL SIX IS A PERFECTLY GOOD OUTCOME AND YOU SHOULD SAY SO IF IT IS
TRUE.** Fifteen rows have been refused and **every refusal was the right call**;
several left more reusable measurement behind than a build would have. **What is
NOT acceptable is a row proposed on an unrun justification** — that is the exact
failure this task exists to stop.

⚠ **A refusal's REASON gets reused on the next row, so it needs the same scrutiny
as a finding.** `TASK_093`'s refusal reason was **rejected by its own review**
(right verdict, wrong reason). **Write reasons you would defend under review.**

---

## Constraints

- **`.temp/t102/` only. No `/tmp`.** Keep the generator, delete the artefact.
  **Notes in `.temp/t102/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- **`.memory/` and `RECAP.md` are manager-only.** Propose rows in your report;
  the manager writes them after review.
- ⚠⚠ **Create NO pattern directory and touch NO existing one.** This task
  proposes and probes; it does not build.
- ⚠ **Do not run `harness/measure.py` or `harness/build.py`**, and do not edit
  `harness/check.py`. Throwaway kernels in your own scratch only.
- Verus via `./verus_run.py`, single-file mode. Do not bump the pin.
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_102_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is `MANAGER-FILLS-AT-LAUNCH`.** The calls I
am least sure of:

1. ⚠⚠ **That new rows are needed at all.** The alternative is to stop at 25
   patterns and spend the remaining effort on the cross-pattern synthesis, which
   **has never been scheduled** and is arguably worth more than pattern 26.
   **If your probing says the remaining realistic C patterns are all duplicates
   of what the tree has, SAY THAT** — it is the finding that settles the
   project's endgame, and it is worth more than a sixth candidate.
2. **That §B's four guesses are worth probing.** They are mine, and mine are 0
   for 2. **Replacing them is encouraged, not tolerated.**
3. **That "the tree has fourteen `index >= len`" makes a fifteenth a high bar.**
   ⚠ **It may be the opposite** — that the class dominates because it is what
   real C bugs actually ARE, and a catalogue that keeps refusing it is
   over-fitting to novelty rather than to realism. **If you think the bar is
   wrong, argue it with the CVE distribution, not with taste.**

Carry that count forward, incremented by what you find.
