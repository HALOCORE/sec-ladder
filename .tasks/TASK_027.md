# TASK_027 — land TASK_025_REVIEW's corrections in p16, and ship the reproduction path

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_025_REVIEW_REPORT.md`
in full** — blocker 1 and majors 2–5 are this task — then
`patterns/p16-tlv-walk/NOTES.md` §10a.1 and §10a.2 (what you are correcting), and
`.memory/01-ladder.md`'s p16 entry and its R4-by-permission paragraph, **both
already corrected by the manager and the wording to follow rather than
re-invent**.

`.memory/` and `RECAP.md` are done. **`patterns/p16-tlv-walk/` currently
disagrees with `.memory/`, and `.memory/` is the one to believe** until you land
this.

## What was measured, and what it costs p16

A reviewer attacked TASK_024 and found one blocker and four majors. All five are
reproduced with command output in the report; do not re-derive them, land them.
The short version:

1. **`u_c32` is not a p16 R4 rung.** `spec.md`'s `identity: unsafe ≡ verus, O3
   exact` means every R4 needs a byte-identical R5 that Verus verifies, and vstd
   supports none of `chunks_exact`, `ChunksExact`, `by_ref`, `TryFromSliceError`,
   `get_unchecked`. Five new trusted items would be needed, against the one
   trusted `requires` p16's whole claim rests on.
2. **`−0.5625` → `−0.65625`.** It was the K=16 number left pointing at the K=32
   rung. `5.09375 − 5.75 = −0.65625`, confirmed independently by
   `(115 − 31)/(4·32)`.
3. **`−199 / −2365` is not the minimum.** `chunks_exact(64)` gives
   **`−127 / −2545`**. Fifth published minimum overturned by the next search.
4. **"`chunks_exact(4)` is dearer" is a `try_into` artefact.** Drop `try_into` and
   K=4 measures 5.37500 and is **1509 Ir/call cheaper** than shipped R4 at
   `large`.
5. **The direction test is stated with its sign inverted** relative to its own
   cited precedent, and the exclusion it was used to forbid would not have
   restored `+19` anyway (manual unrolling is licensed by name; manual 32× is
   5.18750 < 5.75).

## What to land

**Prose first, gates last** — `source_sha256` globs `patterns/*.md`.

1. **§10a.2's three numbered statements are the centre of this.** Statement 2
   ("at matched spelling the unsafe rung is cheaper … as `inf(R4) ≤ inf(R3)`
   predicts by construction", `NOTES.md:1586-1598`) must go, and what replaces it
   is **stronger, not weaker**: the six `u_c*` probes are not admissible R4s at
   all, so the comparison was never between two rungs. Say what the measurement
   *does* support — that the safe class reaches spellings the unsafe class cannot,
   because the unsafe class is chained by the `identity` pin to what vstd can
   verify — and say plainly that whether `inf(admissible R4) > inf(admissible R3)`
   on p16 is **open**, because a hand-unrolled 32× fold with explicit indices was
   never tried.
2. **Every site carrying `−0.5625`, `−199 / −2365` or `+19 / +45`.** The review
   names them: `NOTES.md:1605,1607` and `203-204,1390,1559`; `README.md:58-59`;
   hashed `spec.md:297`; `results/tables/p16-tlv-walk.md:37` is *generated*, so
   regenerate it rather than editing it. Grep for the numbers rather than trusting
   that list. **Write "cheapest found", never "minimum"** — the value has moved
   three times.
3. **The null, upgraded.** §10a.2 claims it from three pairs at one residue offset
   (56, 88, 2040, 2072, 2168, 2296 are all ≡ 24 mod 32). The review swept 127
   consecutive `vlen` and got a *single integer per call* at every point, slope
   `0.0000000`, max residual 0.00. That is a better result than the one shipped —
   state it as the swept one and say what the earlier evidence actually was.
   Mnemonic identity also holds at **K = 4 and 8**, which §10a.2 hedges away from.
4. **The `try_into` control (major 4).** It is the first control ever run for that
   mechanism and it confirms the mechanism while refuting the argument built on
   it. Both halves go in.
5. **`minor 6`, and do not soften it.** The published 5-decimal rates are exact as
   *disassembly* quantities (`body/K`) and **not** as measured slopes: measured,
   they carry ±0.01 Ir/byte from the driver's `println` digit-count term, which is
   20× the gap between two published rates in that table and does not cancel
   within a binary. Any table of rates in p16 must say which kind of number it is.
6. **The withdrawn direction-test argument** (`NOTES.md:1619-1638`). The
   *conclusion* — do not pin the unroll factor — stands. **Every stated reason for
   it is withdrawn**, and the honest replacement is the one the review supplied:
   pinning would not have worked, because the declaration licenses manual
   unrolling by name and manual 32× is already below the shipped rate. Do not
   restate the direction test here; `.memory/01-ladder.md` now carries it flagged
   as broken with a PROVISIONAL repair, and citing it again before that repair is
   reviewed is the thing that went wrong last time.
7. **`spec.md`'s hashed `why`** should say what blocker 1 measured, because it is
   a fact about the *contract* and not about one experiment: **an R4-side variant
   must be expressible in what vstd can verify, or it is not a rung** — the
   `identity` pin makes that a contract property, and it is why the safe-side and
   unsafe-side levers are not "the same category of edit". `gen_controls.py:69-71`
   already says the p16-specific half about `r4_hdr`; this is the general form.

## The reproduction path — the part that is not prose

§10a.2's twelve probes and every number in it live in gitignored `.temp/p24/*.py`.
`controls/*.py` is inside `source_sha256` **precisely so a control's reproduction
path ships**. The review costed it:

- **(a)** `controls/gen_controls.py` takes a third dict of the fold variants;
  `.temp/p24/gen_matched.py`'s `chunks(k, slice_expr)` is already the exact
  `sub()` shape it wants. Its hardcoded `REPO = "/home/apt/repos_common/sec-ladder"`
  must become the `__file__`-derived path `gen_controls.py` already uses;
  `measure.py`, `equiv.py` and `miri.py` carry the same absolute-path constant.
- **(b)** The K=64 row and the "323 insns" figure need either a fourth
  `inputs/gen.py` band **appended last** (TASK_020's argument: the 95 existing
  blobs stay byte-identical) or an explicit "scratch-only, not reproducible from
  the tree" marker. The review's own 128-blob consecutive sweep needed no mod-64
  triple, so a consecutive band is the better shape. **Before you choose, measure
  the cost**: if appending leaves all 95 existing blobs byte-identical, does the
  gate need only a re-run (hash moved) or a full re-measure? Report the answer —
  it decides this and it is not written down anywhere.
- **(c)** `.temp/p24/foldbody.py` **must not ship as-is.** Re-run as committed it
  prints `identical=False` at every `K` — it compares full instruction text
  including registers, and finds no body at K=4/8 — which is the *opposite* of the
  verdict `NOTES.md:1665` cites it for. Ship the reviewer's working version, or a
  repaired one, and make sure the artefact a claim names actually prints that
  claim.

## Explicitly NOT this task

The review proposes a **mechanical backstop** — `spec.md` pins the shipped fold's
chunk-body instruction count and `check.py` asserts `body_len / K` equals the
published rate, ~90 lines, `.temp/r25/foldcmp.py` is a working prototype. **Do not
build it.** It is real and the accident it prevents has happened twice, which is
the standard `.memory/02-bench-rules.md` sets — but gate work competes with
patterns, six of 47 exist, and eleven consecutive tasks have now gone to the
spelling problem. It goes in the queue with its cost, and the manager decides.
**Say in your report whether you think that is the wrong call**, because you will
have just spent a session on exactly the defect it would catch.

## Done when

All seven prose items and (a)(b)(c) land; `check.py p16` green; `md5_fn`
unchanged; `results/tables/p16-tlv-walk.md` regenerated rather than hand-edited.
Re-run p05 and p02 only if you touch them. Expect gate-record churn on an
unchanged tree — ASan PIDs and p05's nondeterministic `adversarial-dims` stdouts;
`.memory/03-measurement.md` has the inventory. Subtract before attributing.

## Constraints

No root; no `/tmp` (scratch `.temp/p27/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. Prose, `controls/*.py` and `inputs/gen.py` only —
**nothing in `harness/`, no cell source**. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never
`pkill`/`killall`; confirm an exact PID's full command line before any kill.

**Run measurements in the FOREGROUND.** Background `nohup` jobs on this box get
reported "completed" while still running; that is how two concurrent runs shared a
scratch path and corrupted a data point during the review, caught only because the
column was otherwise constant. Give any scratch file a per-PID path.

Per `.memory/00-environment.md` constraint 6, **delete your binaries and generated
blobs when the gate is green and keep your scripts, notes and results.**

Notes to `.temp/p27/NOTES.md` as you go, so you can be resumed if you die to a
transient API error — three agents on this arc have.

**If a prescription here is wrong, say so with the measurement.** Thirty-two
agents have contradicted the manager's written instructions and all thirty-two
were right; the last one refuted a headline I had committed the night before and
overturned a claim I had been writing into three files for six patterns. What I am
least sure of here is **item 7** — whether "an R4 must be Verus-expressible"
belongs in the hashed contract at all, or whether stating it there quietly
narrows the R4 class after the fact, which is the self-certification move this
project has a rule against. It is a *consequence* of a pin that has been there
since the pattern shipped, not a new restriction — but that is exactly what
someone making the bad version of this move would also say.
