# TASK_100 — the leak-detector claim, and the NINE refusals nobody reviewed

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read `.tasks/PROTOCOL.md`, then this file, then **`.temp/mgr99/NOTES.md`**
(the manager's own probe, written for you to attack), then
`.memory/00-environment.md`'s section *"THERE IS NO WORKING LEAK DETECTOR FOR
THE C RUNGS ON THIS BOX"*, then `.memory/06-catalogue.md`'s rows for
`p29 p30 p32 p33 p34 p37 p39 p43 p44`, then `.memory/01-ladder.md`'s
allocator-guarantee section.

Scratch in **`.temp/r100/`** — free, I checked.

⚠⚠ **`TASK_099` IS RUNNING CONCURRENTLY.** It edits `harness/check.py` and
`synthesis/synthesize.py` and runs a full 24-pattern sweep. **You are barred
from `harness/check.py`, `harness/measure.py`, `harness/build.py`,
`synthesis/`, `results/` and every `patterns/*/` file — do not run them, do not
edit them.** Reading `check.py` is fine. Everything you build goes in
`.temp/r100/`. If you need a gate behaviour, **drive the limb on a synthetic
pdir in your own scratch**, the way `TASK_097` drove `check_trusted_twins`.

---

## §A — ⚠⚠ A `.memory/` SECTION LOOKS FALSE, AND IT IS A NAMED KILL FOR TWO ROWS

`.memory/00-environment.md` publishes, *"at the gate's exact stage-7 flags"*:

```
  -O0  leak=1 -> exit=1  reports=1
  -O1  leak=1 -> exit=0  reports=0
  -O2  leak=1 -> exit=0  reports=0
```

**and concludes there is no working leak detector for the C rungs.** That
sentence is the **NAMED KILL** on catalogue row `p34` and the named blocker on
`p42`.

**The manager re-ran it at the flags read out of `check.py::check_sanitizers`
and got `exit=1 reports=1` at ALL THREE levels**, with a negative arm at
`exit=0 reports=0`. Full detail and rebuild lines: `.temp/mgr99/NOTES.md`.

⚠⚠ **DO NOT TAKE THAT AT FACE VALUE. THE MANAGER'S PROBE IS THE THING YOU ARE
REVIEWING.** Named ways it could be wrong, and there will be others:

1. **The manager's leaked list may not be the one `.memory/` measured.** A leak
   still pointed to by a **global** or a **static** is *"still reachable"* and
   LSan will not report it — by design, at every `-O`. If TASK_093's probe held
   its head in a global and the manager's held it in a local, **both results are
   right and the disagreement is about the program.** ⚠ **Establish what was
   actually measured before calling anything false.** `.temp/` may still hold it.
2. **`__lsan_do_recoverable_leak_check()` mid-program returns 0 by design** when
   the pointer is still in scope. `.memory/` cites it as corroboration. **If the
   original checked mid-program, the table is a probe artefact** — the manager
   flagged this hypothesis and did **not** test it. **Test it.**
3. **The `-O` dependence the manager found is an ACCOUNTING one** — 80→16 bytes,
   5→1 object at `-O1`. ⚠ **Is there a leak SHAPE where the accounting
   degradation becomes a detection failure — i.e. where the last reported object
   also drops out and the count goes to zero?** If yes, `.memory/` is right in
   substance and wrong only in generality, **and that shape is what a leak row
   would have to avoid.** This is the most useful thing in §A.
4. **The `--wrap=malloc` counter** (result 3) is a second instrument. **Attack
   it**: what does it miss? It counts calls, not reachability, so a program that
   frees a block and leaks a *different* one nets to zero. **Does that matter for
   a leak-on-error-path row, where the whole point is an unbalanced path?**
   ⚠ **And does adding it perturb the measured cell?** If it does, it cannot ride
   in the measured build and must live in a harm probe only. **Say which.**

**Then answer the question that turns on it, with runs:**

> ⚠⚠ **Are `p34` and `p42` UNBLOCKED?**

- `p34` is *reference counting*, and `.memory/01-ladder.md` outcome 4 says its
  safe rung is **WORSE than C** (`Rc` cycle leaks, `Weak` does not; manager-re-run
  `miri cycle` → 5 `memory leaked`, `miri weak` → 0). ⚠⚠ **That inversion — safe
  Rust losing on SAFETY, not on speed — DOES NOT EXIST ANYWHERE IN THE 24-PATTERN
  TREE.** If the C side can be instrumented, this is the most valuable row left
  in the catalogue. **If it still cannot, say so plainly and close it for good.**
- `p42` is *`goto cleanup`, leak on error path* — a genuinely idiomatic C shape.
  ⚠ **Its triage named *"Miri's leak check or valgrind"* and `.memory/` says one
  of those two is unavailable. Is the OTHER one enough?**
- ⚠ **A row is not unblocked just because a detector exists.** It also needs a
  bug class the tree does not have, a boundary that moves between rungs, and a
  kernel shape the 22-of-24 file-blob driver can host. **Apply THE THREE PROBES
  + probe 4 from `.memory/06-catalogue.md` before saying yes**, and remember
  **`p33` died on probe 1** (the bug compiles identically at every rung).

---

## §B — NINE REFUSALS REST ON REASONING NOBODY REVIEWED

`grep -c PROVISIONAL .memory/06-catalogue.md` finds **eleven** rows; **nine are
refusals**: `p29 p30 p32 p33 p34 p37 p39 p43 p44`. They came out of `TASK_094`
and `TASK_095`, and **neither was ever reviewed.**

⚠⚠ **This matters because of what happened the last time a refusal was
reviewed.** `TASK_093` refused `p28` and its **stated reason was REJECTED by its
own review** — *"safe Rust has no owned intrusive DLL (`E0382` + `E0499`)"* was
false three ways, including a control containing **no data structure at all**
that printed the identical error. **Right verdict, wrong reason.** RECAP's
lesson: ⚠ **"a refusal's REASON is what gets reused on the next row, so it needs
the same scrutiny as a finding."** Nine rows are now carrying exactly that risk.

**You are not required to overturn any of them, and I expect most to stand.**
What I want is the **reason** audited. For each of the nine:

1. **Is the stated reason a MEASUREMENT or an ARGUMENT?** Measurements are cheap
   to re-run — re-run the load-bearing ones. Arguments are where `p28` failed.
2. ⚠ **Is the reason GENERIC?** `p28`'s died because a borrow-checker diagnostic
   was attributed to a data structure when a struct with one `u32` field
   reproduced it. `.memory/01-ladder.md` states the rule: **"a borrow-checker
   diagnostic is not evidence about a data structure until a control with no
   data structure has been compiled."** **Apply that rule to every refusal that
   cites a compiler error.**
3. **Does the verdict survive if the reason dies?** Say so per row — that is the
   `p28` outcome and it is a perfectly good one.

**Prioritise. Do not spend equal time on nine rows.** My ranking of where a
defect is most likely, and I may be wrong about it:

- ⚠⚠ **`p34` — it is §A's row and its kill is an environment claim under active
  contradiction.** Highest value by a distance.
- **`p30`** — refused on *"a chained table CANNOT FILL"*, measured
  `maxchain=4096 of 4096 keys in 1024 buckets`. The measurement looks sound.
  ⚠ **But the refusal then reduces p30 to "p27's half alone" — is that the only
  bug class a chained table offers?** An unreduced bucket index, or the resize
  path, are different classes. **One `grep` of the built tree settles whether
  either is novel; RECAP's rule 4 says run it before writing a row, and the
  same rule should apply before REFUSING one.**
- **`p43`/`p44`/`p39`** — all three refuse on *"it is another pattern's shape
  with one immediate/one operand moved"*. ⚠ **That is a similarity judgement.
  Is it backed by a normalised-disassembly comparison, or by reading?** ⚠ **And
  note probe 2 is known BROKEN IN BOTH DIRECTIONS** (object-file md5
  false-positives on relocations; linked md5 false-negatives on any kernel with
  a branch or a global) — **the only form that works is normalised-disassembly
  text.** If these three were refused on a broken probe, say so.
- **`p29`** — the verdict looks strong and its artefact is already banked.
  ⚠ **Its declared cost zero was FALSE and caught (`−0.00024` per lookup vs
  `+48.01` per key with the alloc/free in the pair). Is any OTHER number in
  these two reports scoped to the wrong denominator the same way?**
- **`p32`/`p33`/`p37`** — I expect these to stand; `p33` died on probe 1, which
  is the strongest kill available. **Confirm briefly and move on.**

---

## Constraints

- **`.temp/r100/` only. No `/tmp`.** Keep the generator, delete the artefact.
  **Notes in `.temp/r100/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠⚠ **Do not edit `.memory/`, `RECAP.md`, `pilot/`, `harness/`, `synthesis/`,
  `results/` or any `patterns/*/` file.** You are a reviewer: **do not fix
  anything**, and `TASK_099` is concurrently writing three of those trees.
- ⚠ **`env -u LD_PRELOAD` for every hand-run sanitizer** (RECAP time-waster 5:
  this shell's `LD_PRELOAD` silently blinds a *shared* ASan build, and both arms
  exit 1 so the exit code cannot tell them apart). **`grep` sanitizer logs,
  never `head` them** — `TASK_086` lost a round to `head -4`.
- ⚠ **Every harm probe needs a positive control that must fire.** Five controls
  in this project could not have failed; the most recent was `64 mod 32 == 0`.
- Verus via `./verus_run.py` only, single-file mode. Do not bump the pin.
- `timeout <N> <cmd>`; never `pkill`/`killall`.
- **Give clean negatives.** A named attack that did not land is worth as much as
  a finding — the manager's own valgrind hypothesis in `.temp/mgr99/NOTES.md` is
  one, and it is written up as a result.

Write your report to `.tasks/TASK_100_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 299**, plus **2** from the manager probe
in `.temp/mgr99/NOTES.md` (the `-O1` and `-O2` rows of the LSan table) = **301**.
⚠ **`TASK_099` is in flight and carries its own increment; the manager
reconciles the two at the commit — do not try to.** The calls I am least sure of:

1. ⚠⚠ **That my leak probe contradicts `.memory/` at all.** §A.1 is the way it
   is wrong: if TASK_093 measured a *different program*, both results stand and
   I have manufactured a contradiction out of two correct measurements. **That
   would be the fourth time a manager claim died to "you measured a different
   thing", and I would rather find it here than in `.memory/`.**
2. **That the nine refusals are mostly sound.** I am ranking by intuition; §B's
   priority order is a guess and **the defect may well be in the three I told
   you to confirm briefly and move on.** If your reading says otherwise, spend
   the time where the evidence points and say I ranked it wrong.
3. **That `p34` is worth reopening even if §A clears it.** It is one row, it is
   `research-grade`, and the catalogue was declared closed two tasks ago. ⚠ **If
   the honest answer is "the detector exists and the row is still not worth it",
   that is a fine outcome — `.memory/` gets corrected either way, which is
   most of the value here.**

Carry **301** forward, incremented by what you find.
