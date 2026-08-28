# TASK_122 — the INSTRUMENT: attack finding 41, and characterise an 18.9 M `Ir` drift

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** ⚠ **Except §B, which is a measurement you must actually run.**

Read `.tasks/PROTOCOL.md`, then this file, then **`RECAP.md` findings 40 and 41
in full**, then **`.tasks/TASK_120_REPORT.md` §A1 and §D2**, then
`.memory/03-measurement.md`'s band table and its list of named failure classes.

Scratch in **`.temp/r122/`**.

---

## Why this task exists

**`TASK_120` reviewed the manager's finding 40 and it did not survive as written.
In the course of that review it produced TWO NEW RESULTS OF ITS OWN, and by
PROTOCOL rule 9 neither may become a law without being attacked.** ⚠⚠ **Finding
41 is finding 40's exact shape — ONE READER, ONE REFUSAL SET, ONE CLASSIFICATION
— and finding 40's fate is the reason to be suspicious of it.**

## §A — ⚠⚠ ATTACK FINDING 41. IT IS THE ONE THE PROJECT MAY STOP ON.

> **`LADDER` + `COST` is 7 of 22 as a primary reason, so THE MOST COMMON THING
> WRONG WITH A REMAINING ROW IS THAT THE FIVE-RUNG LADDER HAS NOTHING TO PRICE ON
> IT — a property of the INSTRUMENT, which will keep killing NEW rows too.**

**The whole decision now rests on this.** RECAP says: *if the project stops, stop
on finding 41.* **So it had better hold.**

1. ⚠⚠ **THE CLASSIFICATION IS ONE READER'S, AND IT IS THE SAME METHOD THAT
   PRODUCED THE 7-OF-22 TALLY THAT TURNED OUT TO BE 6-OF-22.**
   **Re-run `.temp/r120/classify22.py` and then RE-CLASSIFY ALL 22 ROWS
   YOURSELF, blind to its buckets if you can.** ⚠ **Where you disagree, say so
   with the cell's own words.** **`LADDER`/`COST` vs `NOVELTY` is exactly the
   boundary most likely to move** — *"the axis is flat"* and *"the row's novelty
   claim was false"* can be the same sentence read two ways.
2. ⚠ **IS `COST` EVEN THE SAME CATEGORY AS `LADDER`?** **Finding 41 ADDS THEM.**
   `LADDER` = *the rungs do not separate* (probe 1, one-rung kills). `COST` =
   *the axis is flat, zero, false, or below the instrument*. ⚠⚠ **A row whose
   cost axis is FALSE (`p41`'s `9.6×` was 100% R3 spelling) died of a BAD CLAIM,
   not of an instrument limit — that is `NOVELTY`'s story, not the ladder's.**
   **If `COST` splits, 7 of 22 splits with it and finding 41 is a list too.**
   ⚠ **This is the attack I would run first.**
3. ⚠ **SELECTION EFFECT, AGAIN, AND IT KILLED THE LAST TWO GENERALISATIONS.**
   Every one of those 22 reasons was written by an agent who **already knew what
   this instrument can price**. *"The ladder has nothing to price here"* is a
   reason that is **always available to somebody holding this ladder**. **Ask
   whether it is the TRUE reason or the reason the instrument makes easiest to
   see** — `TASK_120` caught `p20`'s duplication clause being appended *"a
   fortiori"* with a timestamp. **Look for the same shape in the `LADDER`/`COST`
   cells.**
4. ✅ **A CLEAN NEGATIVE IS A FINE OUTCOME.** **If the classification holds and
   `COST`/`LADDER` really is one family, SAY SO** — the project then has a
   measured reason to stop and that is worth more than another open question.

## §B — ⚠⚠ THE 18.9 M `Ir` DRIFT. THIS ONE IS A MEASUREMENT, NOT A REVIEW.

**`TASK_120` re-ran `TASK_086`'s `p40` probe with its own parameters and got:**

```
whole-program Ir total   360,114,293  (TASK_086)  ->  378,984,676  (TASK_120)
                         = +18,870,383, about +5.2%
rustc  1.97.1 / LLVM 22.1.6   UNCHANGED (pinned)
valgrind 3.27.1                UNCHANGED
D1 miss delta k40_aos - k40_soa    1,179,645  ==  1,179,645   EXACT
```

⚠ **The reviewer could not attribute it and correctly refused to guess.**
⚠⚠ **THIS MATTERS BEYOND `p40`: if whole-program totals on this box have moved
5%, then every published whole-program figure taken before the move is suspect,
and the project has 52 measurement records.**

**What to do, in order, and STOP at the first one that explains it:**

1. ✅ **CHEAPEST FIRST — is it the ENVIRONMENT BLOCK?** **This project has
   already measured that the environment block moves the marginal by ±7 and that
   `bytes` alone is an incomplete pin** (`TASK_114`, and `TASK_119` is fixing
   it). ⚠ **A 5% whole-program move is far too large for the ±7 term** — **but
   `TASK_120` also measured a 60-`Ir` move between `--cache-sim=yes` and plain
   `callgrind` on an identical binary, so the harness's own knobs move totals.
   Check the probe's invocation FIRST**: `--cache-sim`, `--toggle-collect`, the
   iteration count, and whether `TASK_086`'s script and `TASK_120`'s re-run
   allocated the same 67 MB + 16 MB.
2. ⚠ **Is it the BINARY or the BOX?** ✅ **Decisive and cheap: rebuild
   `TASK_086`'s exact kernel, take `md5_fn` and `n_fn` via `harness/asm.py`, and
   compare against whatever `TASK_086` recorded.** **Identical text + different
   total ⇒ the box moved. Different text ⇒ the build moved and the pins did not
   catch it, which is a MUCH bigger finding.**
3. ⚠ **Only if 1 and 2 both come back clean:** widen to one OTHER pattern's
   committed whole-program figure and see whether it moved by a similar
   proportion. **One row is an anecdote; two is a drift.**
4. ⚠⚠ **DO NOT PUBLISH A MECHANISM WITHOUT A MEASUREMENT.** **This axis is
   `MIRIFLAGS` all over again — that one had TWO confident published mechanisms
   before anyone measured that the driver never parsed the variable.** **An open,
   well-characterised question beats a third wrong mechanism.**
5. ✅ **State the BLAST RADIUS either way** — how many published figures are
   whole-program totals rather than differences. ⚠ **`TASK_120` already named
   three (`p40`'s `21`, `p40`'s `193`, `p43`'s `+3.00`) and `p40`'s `21` survives
   because it was re-derived as a DIFFERENCE. Is that the whole list?**

## §C — the small one, and it is owed

**`TASK_120` §C4 found a citation rotted to the wrong `.memory/` file** (the
`4.25 = 2.00 + 2.25` rule) **and a *"third instance"* claim when four earlier
instances exist on BUILT patterns.** **Confirm both, and `grep` for the same rot
elsewhere** — ⚠ **the manager has landed a lot of `.memory/` text this session
and cross-file citations are exactly what rots.**

---

## Constraints

- **`.temp/r122/` only. No `/tmp`.** **Notes in `.temp/r122/NOTES.md` AS YOU GO.**
  Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine — ⚠ **and §B.2 needs
  `git log`/`git show` on the old record, so use it.**
- ⚠ **Do not edit `.memory/`, `RECAP.md`, `results/`, `synthesis/`, `harness/`,
  `pilot/` or any `patterns/*/` file. You are a reviewer.**
- ⚠⚠ **DO NOT RUN `harness/check.py`, `build.py` or `measure.py`**
  (`measure.py --check-stale` is fine) **unless the manager says the tree is
  free.** **Build probes with direct `clang`/`gcc`/`rustc` under `.temp/r122/`.**
- ⚠ **Callgrind `Ir` is deterministic and immune to concurrent load; wall clock
  is not.** ⚠⚠ **§B is precisely a claim that "deterministic" has limits —
  measure them, do not assume them in either direction.**
- ⚠ **Every probe needs an arm that MUST FIRE.** **The list at the end of `.memory/03-measurement.md` is the catalogue of
  named failure classes — ⚠ **READ THE LIST; IT CARRIES NO USABLE COUNT.**
  ⚠⚠ **Its own entry says a count is a cached derivation that goes stale like
  any other cached number, and that count has now rotted THREE times — most
  recently because this manager added an entry after writing the old figure
  into three task files. If you need a number, derive it where you write it.**
- ⚠⚠ **Probe 2 has SIX known defects and `.temp/t104/probe2.py` carries the
  sixth.** **Take the symbol extent from the ELF symbol table.**
- Hand-run ASan needs `env -u LD_PRELOAD`; never truncate a sanitiser log with
  `head`.
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_122_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 502** (`TASK_120` carried 466 → 488, then `TASK_118` added 14 off the same branch → 502;
⚠ **a rigour signal, not a ledger — do not re-add it**). The calls I am least
sure of:

1. ⚠⚠ **That finding 41 should have been landed at all.** **I landed it the same
   session it was written, from one task, marked PROVISIONAL — which is exactly
   what I did with finding 40, and finding 40 lasted one review.** ⚠ **If your
   honest read is that the project should carry the 22-row CLASSIFICATION and NO
   generalisation over it, SAY SO. That is a respectable outcome and it is what I
   should probably have done with finding 40.**
2. ⚠ **That §B is worth a whole section.** **It is one number on one refused row.
   The argument for chasing it is that it is a claim about the BOX and the box
   underwrites 52 records; the argument against is that `p40` is refused, nothing
   ships on it, and this could eat a task for an answer nobody uses.** **If §B.1
   or §B.2 settles it in ten minutes, say so and spend the rest on §A.**
3. ⚠⚠ **That the project should NOT stop.** **I have now written the box to say
   the endgame decision rests on finding 41, and finding 41 is unreviewed. If it
   falls, the project has NO stated reason to stop and the standing user mandate
   is *"as many realistic C patterns as possible"* — which means the enumeration
   in `TASK_123` becomes the main line rather than an option.** **Tell me if I
   have the dependency backwards.**

Carry **502** forward, incremented by what you find.
