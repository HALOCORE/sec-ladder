# TASK_022 — land the p05 corrections, and say "best found" where we said "floor"

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_021_REVIEW_REPORT.md`
**in full** — this task is its blocker, its major and its five minors — and
`.memory/01-ladder.md` finding 6, which the manager has already corrected and
which is the wording to follow rather than re-invent.

This is repair. Nothing in it is open, and the numbers are all measured.

## Part 1 — the blocker: there is no two-sided floor

TASK_021 reported one, on the ground that six in-contract R4 spellings gave a
single instruction count. **All eight of its R4 spellings decoded the header the
shipped way**, so the flatness measured the *header*, not the rung. Respelling
that too gives **13 in-contract R4 spellings, 11 distinct `md5_fn` bodies, every
one cheaper than shipped R4** — the cheapest being two unaligned `*const u16`
header reads.

Corrections, everywhere they appear in `patterns/p05-index-flatten/`:

- **`5·nrow + 6` → `5·nrow + 11`**, i.e. **106 / 336**, not 101 / 331.
- The published `6·nrow + 9` is high by `nrow − 2` = **14% / 16%**, not 18%/17%.
- **Delete "two-sided" and "zero R4 spread"** wherever they occur.
- §14h.4's *"the whole in-contract interval's lower end"* presupposes R4 is a
  point. It is not. p05 needs p16's and p17's **interval** treatment.

Sites the review names: §14's opening, §14f, §14h.2, §14h.4, §2a's qualification
(ii), §12d, and `README.md:139-152`.

**And change the word.** Two "floors" have now been broken on this pattern, by
the same move each time — respell one more thing. The review says plainly that a
third search will probably find a twelfth spelling. So write **"best found"**,
never "floor", and say how many spellings were searched to find it (29 R3 + 13
R4). `inf(R4) <= inf(R3)` holds by construction; a best-found value is a
measurement, an infimum is not available.

## Part 2 — the reading-dependence, which was stated unconditionally

`required[1]` has two readings and **the number depends on which**: p16's reading
gives `5·nrow + 11` (106/336), the strict reading
`min(6·nrow + 11, 5·nrow + 17)` (112/342). §14b and §14e get this right; §14's
opening, `README.md:139-142` and (already fixed) `.memory/`+`RECAP.md` did not.
State both, and state that the *qualitative* claim survives either — that is what
makes the ambiguity tolerable rather than load-bearing for the conclusion, even
though it is load-bearing for the figure.

## Part 3 — the mechanism, which survives and should be stated in the reviewed words

The reinstated sentence is in `.memory/01-ladder.md` finding 6 verbatim. Put the
same wording in p05's `NOTES.md` and `README.md`, restricted the same way:
**the `O(nrow)` part only**, this kernel, this declaration, this toolchain; not
the constants, which move in both rungs by different amounts; not a statement
about safety in general.

## Part 4 — five minors from the review

1. §14e:1396 — the R3 best-found set has **five** distinct `md5_fn`, not four.
2. §14a:1299-1300 — "greppable, true of all 37" **fails on `r3_ds_cells`**
   (`cells > avail`, `cells as u64`).
3. §14h — *"cannot be removed by any spelling"* is unmeasured; the
   out-of-contract `t4_idx` removes **2 of the 5**. Say measured-or-not.
4. "179 points" is **177 distinct dimensions** — `small`/`large` duplicate
   `sweep-r19c26`/`sweep-r65c61`.
5. §12c:1085 is the one un-amended `6·nrow + 9`.

## Part 5 — p08's control generator

`patterns/p08-overlap-move/controls/gen_controls.py` leaves the shipped
`#[path = "../../common/driver.rs"]` in its output, which from
`.temp/p08/controls/` resolves to **`.temp/common/driver.rs`** — a gitignored
copy. Byte-identical today, so it works **by luck**; on a fresh clone p08's
controls do not compile. p16's new generator already rewrites the path to the
real, hashed file. Do the same for p08.

## Done when

Every site listed is corrected; "best found" replaces "floor" with its search
size; the reinstated sentence appears in p05's files in the reviewed wording;
p08's generator points at the hashed `common/driver.rs`; p05 and p08 gates green;
`md5_fn` unchanged. **No cell source may change** — this is prose and one
generator.

Prose first, gates last.

## Constraints

No root; no `/tmp` (scratch `.temp/p22/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. You may edit `patterns/p08-overlap-move/controls/gen_controls.py`
and prose; **nothing in `harness/`** and no cell source. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; confirm an exact PID's full command
line before any kill. Check `git status` before finishing.

Notes to `.temp/p22/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Twenty-seven
agents have contradicted the manager's written instructions and all twenty-seven
were right; the last one refuted a "floor" that had been measured over 179
points, by respelling one more thing. What I am least sure of is **whether
"best found (29 R3 + 13 R4 spellings searched)" is honest enough**, given that
the same sentence was written about 8 R4 spellings a task ago and was wrong. If
you think the only defensible statement is an interval with no lower end, say so
and write that instead.
