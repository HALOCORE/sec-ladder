# TASK_062 — p27 shipped without the named-spelling standard, and nothing caught it

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md` (**rule 5 — the accident test**), then
`.memory/01-ladder.md`'s **finding 3** (the named-spelling standard: what it is
and what it does and does not buy), then `patterns/p27-handle-table/spec.md` and
any other pattern's `spec.md` for comparison.

## What is wrong

**`patterns/p27-handle-table/spec.md` does not contain the shared named-spelling
paragraph at all.** Every other pattern's `idiom.why` carries it, byte-identical:

```bash
python3 -c "import hashlib,glob;print({hashlib.sha256(open(f).read()[open(f).read().find('NAMED-SPELLING STANDARD'):open(f).read().find('p01 and p08 neither')+19].encode()).hexdigest()[:12] for f in glob.glob('patterns/*/spec.md')})"
# -> {'59748cce2db5', 'e3b0c44298fc'}      <- set size 2; e3b0… is sha256("")
```

p27's `why` is **2607 bytes of its own text** and the shared paragraph is
**~11 003**. `grep -c 'NAMED-SPELLING STANDARD' patterns/p27-handle-table/spec.md`
returns **0**.

**This is not cosmetic. p27 pins backticked spellings** — the review's own
finding touched `idiom.required[2].rust` — **and the shared paragraph is what
DEFINES what a backticked pin means**: that it pins *that spelling*, not merely
the property the expression has, and the three-part matching rule
(whitespace-insensitive, comments and string literals blanked, ghost clauses
blanked) that `check.py::spelling_matches` implements. **Without it p27's pins
are undefined by p27's own contract**, and every argument the other patterns
rest on that paragraph for does not apply to p27 in writing.

**Three tasks and two adversarial reviews did not catch this.** It was found by
the manager's own standing verification command, after p27 was fully landed.

## Deliverable 1 — restore the invariant

Copy the paragraph into p27's `idiom.why`, **byte-identical**, positioned as the
other patterns position it. **Verify with the command above: the set must have
size 1 and the value must be `59748cce2db5`.**

⚠ **Copy it VERBATIM, including the phrase "this paragraph is byte-identical in
all six patterns' `why`".** That "six" is **historical** — there are eighteen
now — and it sits **inside the hashed contract block**, so "fixing" it would
move **eighteen** `contract_sha256` values and require eighteen gate re-runs to
change one adjective. **Do not touch it.** Add a note in `NOTES.md` saying the
count is historical and why it is deliberately not corrected.

**Expect `contract_sha256` to move**, and disclose it the way TASK_061 did:
record the before and after, and **show that undoing only this edit reproduces
the previous hash byte for byte**. **Run the direction test in writing** — it
should pass trivially (this edit moves no published figure; it *adds*
constraints), but say so rather than assuming it.

⚠ **Then check whether the added paragraph moves stage `0b`'s audit** — a
backtick in the wrong place changed `spellings 62→63` and `pins_nothing 3→4` on
TASK_061. Report `spellings`, `pairs`, `present`, `forbidden_hits`,
`required_pins_nothing`, `required_absent` before and after. **If the audit
moves, say which entry moved and why**; the paragraph is prose inside `why` and
should move nothing.

## Deliverable 2 — the gate check, which has a demonstrated accident

PROTOCOL rule 5: *a new gate check needs the "could this happen by accident?"
test first.* **This one has an instance rather than an argument** — p27 is the
accident, it is committed, and it survived three tasks and two reviews.

Add to `check.py` stage `0b`: **if the pattern's `idiom.why` does not contain the
shared paragraph, FAIL**, naming the invariant and the one-liner above. Keep it
small — the shared text can be located from any other pattern, or pinned as a
sha256 constant with a comment saying which patterns it was measured over and on
what date. **Choose, and justify the choice in a comment**; a constant is
tamper-evident and rots, a cross-pattern read is self-maintaining and couples
patterns to each other.

⚠ **`check.py` is hashed into EVERY gate record**, so this costs a full 17-pattern
sweep (~30 min measured). **Do the `spec.md` edit and the `check.py` edit
together, then sweep once.** `.temp/t60-sweep.sh` is the script the manager used
and it works.

⚠ **Predict the blast radius before you sweep, then check your prediction.** It
should be: p27 fails without deliverable 1 and passes with it; every other
pattern is unaffected except for the `check.py` hash. **If any other pattern
moves, stop and report** — that would mean the invariant is not what this task
says it is.

## Done when

The one-liner returns a set of size 1; `check.py` fails a pattern missing the
paragraph (**demonstrate it** — temporarily remove it, capture the failure, put
it back); **all 18 gates green**; `measure.py --check-stale` clean. **Paste the
actual output of the sweep and of the demonstration.**

## Constraints

No root; no `/tmp` (scratch `.temp/t62/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. **You MAY edit `harness/check.py` and
`patterns/p27-handle-table/spec.md` — those two are the task.** Do not edit any
other pattern. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**.
**You are the only agent running.** Tools not on PATH: clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc`; Verus only via `./verus_run.py`.

**If a prescription here is wrong, say so with the measurement.** The running
count is **115**.

**What I am least sure of is deliverable 2's shape** — whether the check should
pin a hash or read a sibling pattern, and whether stage `0b` is even the right
stage. **And whether it should be a gate check at all**: the counter-argument is
that `check.py` is already ~5 300 lines against 18 patterns, and the manager's
one-line command found this in under a second. **If you think the one-liner
belongs in `PROTOCOL.md`'s definition of done instead of in the gate, argue for
it with the ratio** — that argument has won twice on this project.
