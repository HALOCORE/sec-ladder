# TASK_080 — p45, signed-overflow UB: §0 settles the bug class, then the cost, then build

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then **`.tasks/TASK_079.md`'s Outcome block** (this task exists because of it),
then `.memory/06-catalogue.md`'s **`p45` row** (Family H) and the **closed axis
programme** note, then `.memory/03-measurement.md` (**the two `Ir` conventions,
the INLINE-MODE rule, the DOMAIN rule, the RESIDUE-CLASS rule, the
OUTWARD-DISPATCHED-WORK rule**) and `.memory/01-ladder.md` **findings 17 (p18),
21 (p38) and 20 (p47)** — those three are p45's nearest neighbours and two of
them are the reason it might not be worth building. Templates:
`patterns/p38-alias-pun/` (**the donor** — same *"what UB actually does"* family,
same demonstration-kernel question) and `patterns/p36-vtable-dispatch/` (newest;
its conventions are the ones this file forwards).

⚠ **YOU PROPOSED THIS ROW.** p45 was recommended by TASK_079's engineer with its
kill-risk probe already run, and the manager took it **because** it arrived
measured — TASK_074's third option was declined for being labelled unmeasured.
**It is the first catalogue row an agent has argued for.** That does not make it
safe: it makes rule 3 point the **other** way for once, so **the manager's job
this time is to attack it**, and the objections below are that attack.
**"Do not build it" remains a legitimate §0 outcome.**

⚠ **State novelty claims as questions to be measured.** *"The first termination
proof in the project"* was the manager's sentence in `TASK_070.md`; it was false
and shipped into eight places, two inside `contract_sha256`. **Treat any sentence
in this file that is not a question as a bug in this file.**

## What is already measured, and what you may NOT inherit

`.temp/p31pat/` is **readable** and holds `so_probe.c`, `so_rs.rs` and
`signed_overflow_matrix.log`. ✅ **Four things are manager-verified** and you may
build on them without re-running:

- `guard_add(INT_MAX-1, 5)` — the classic self-referential check — returns the
  defined `0` at `-O0` on **both** compilers and **`-2147483645` at `-O2` on
  both**.
- `(a*2)/2 == a` is exploited by **gcc at `-O0` as well**, clang from `-O1`.
- **`-fwrapv` restores the defined answer in every flagged cell** on both
  compilers. **This is the control `p31` did not have and it is why p45 is here.**
- The gate's own stage-7 line — **`gcc -O1 -fsanitize=address,undefined`** —
  fires on **both** sites with file:line and the values. **The catcher is inside
  the matrix**, where p36's `cfi-icall`, p48's MSan and p31's were all outside.

⚠ **Everything else in that directory is a probe, not a rung.** Nothing there was
built through `harness/build.py`, nothing is in contract, and none of its numbers
may reach a `results/` record or a published figure. **Re-derive anything you
publish.**

## §0 — three questions, in this order. The first two can end the task.

### §0a — WHAT IS THE BUG CLASS, AND IS IT NEW? Settle it FIRST.

⚠ **The catalogue's bug-class guesses have been overturned on four patterns and
upheld on two, and two rows were refused outright.** `.memory/06-catalogue.md`
says *"signed overflow UB"*; that is a **UB class**, not a **harm**, and the harm
is what the ladder measures. Three objections, none answered:

**1. ⚠ IS THE HARM JUST THE THIRTEENTH `index >= len`, ARRIVING BY A NEW ROUTE?**
The CVE shape is: `if (len + n < len) return ERR;` is **deleted** because signed
overflow cannot happen, the overflowing length passes, and the subsequent
allocation under-allocates → **heap overflow**. **That harm is a bounds bug**,
and the tree has twelve. ⚠ **This is exactly the objection that killed `p31`'s
exhaustion sub-case one task ago** — *"not the thirteenth `index >= len` but
p12's mechanism and p04's harm"*. **Find p45's answer to it or refuse the
pattern.**

> The manager's candidate answer, offered as a question: **is the class here the
> *deletion of the programmer's own check by the optimiser*, rather than the
> overflow?** That would put p45 with **p38** (the optimiser weaponises UB), not
> with the twelve bounds patterns — and it would make the interesting figure the
> **presence or absence of the check in the disassembly**, not the harm. ⚠ **If
> that is the claim, it owes a disassembly, not a checksum.**

**2. ⚠ p38 ALREADY OWNS *"the first bug class unsafe Rust does not
reintroduce"*, AND RUST HAS NO SIGNED-OVERFLOW UB AT ALL.** In Rust, signed
overflow is **defined**: it panics with `-C debug-assertions=on` and wraps
without. So the naive ladder gives **R2 = R3 = R4** on the UB question and p45
becomes a second p38 on that axis.

> ⚠ **The route out, and it is the pattern's whole R4 story, so settle it before
> anything else: `i32::unchecked_add` and friends ARE unsafe intrinsics whose
> safety precondition is no-overflow, and violating it IS UB in Rust.** **Three
> questions, all measurable in an afternoon:** does the **pinned rustc 1.97.1**
> have them; does the **pinned vstd** support them, or is it `is not supported`
> the way `read_unaligned`, `as_ptr`, `from_raw_parts` and `dereferencing a raw
> pointer` were on p05/p07/p11; and **does Miri catch a violated
> `unchecked_add`?**
> ⚠⚠ **If `unchecked_add` is unsupported at the pin, R4 CANNOT EXPRESS THE BUG,
> and p45 collapses to p08's shape — which is the third finding that killed p48
> and part of what killed p31.** **That is the single fastest way to kill this
> pattern. Run it first.**

**3. WHAT IS `R1h`?** ⚠ **This may be p45's best story and no other pattern has
one this good**, so do not let it go unmeasured. There are at least three
hardened-C answers, and they are not equivalent: **`__builtin_add_overflow`**
(the correct idiom, both compilers, no flag), **`-fwrapv`** (a whole-TU flag that
defines the UB away), and **`-ftrapv`** (traps at run time). **Which is `R1h`,
what do the other two cost, and do they agree?** ⚠ **A flag-based `R1h` is a
`build.py` change and `build.py` is measurement-hashed — a FULL re-measure**
(RECAP settled answer 4). **If `R1h` needs a flag, say so and STOP** rather than
reaching for it; `__builtin_add_overflow` is source and costs nothing.

### §0b — THE KILL-RISK THE PROPOSAL NAMED: is there a cost axis at all?

⚠ **You named this yourself and the manager is forwarding it unchanged: the cost
may be 1–2 `Ir` (a `seto`/`jo`), i.e. a pattern whose behaviour axis is rich and
whose performance axis is ~0.** That is **p47's** situation, and **p47 was worth
building** — its finding is *"the proof certifies a leaking kernel"*, which needs
no cost gap. **But p47 knew that going in.**

**Measure it before writing a rung, and say which pattern p45 is:**

- if the gap is real → an ordinary cost pattern, and the six-lever search applies;
- if the gap is ~0 → **say so in `§0b` and make the finding the behaviour
  matrix**, the way p47 did. ⚠ **Do not discover it after building five rungs.**

⚠ **And `Ir` may not be the right instrument here.** A `jo` that never jumps is
one instruction and **may cost nothing in time**, while a `checked_add` that
returns `Option` may change **inlining and branch layout** far beyond its own
bytes. **Name the inline mode at every figure**, and remember **p07's result**:
the same binary can execute **+7.84% more instructions in 71.75% less time**.

### §0c — WHERE DOES THE WORK LIVE, AND WHAT DOES THE KERNEL COLUMN SEE?

⚠ **The outward-dispatch rule is NOT *"check the `@plt` calls match"*** — it is
**any** outward-dispatched work, including project-local callees, which is how
p36 walked past it. Arithmetic helpers are the case where this is easy to get
right and easy to forget: **does any rung dispatch to a libgcc/compiler-rt helper
the others do not?** (p09's gcc column carries **378.00 / 2625.00 `Ir` per call**
of `__popcountdi2` while `asm.py` records `[]` — the same shape.)
⚠ **gcc defaults to `-fcf-protection=full`**, so every gcc cell carries `endbr64`
landing pads the others do not. **Name it before attributing a gcc-vs-clang gap
to codegen.**

## What p45 must have, if §0 says build it

- **Record the `slb-contract` sha256 in `NOTES.md` before building any cell**
  (definition-of-done 6), and ⚠ **say that the `git show HEAD:` diff is
  UNAVAILABLE on a new pattern and why** — it compares working tree to HEAD, not
  first-written to shipped, so on a clean tree it always looks like it passed.
  **The recorded first hash is the only evidence.**
- **If `spec.md` is generated, fix the GENERATOR and re-run it.** Read the shared
  named-spelling paragraph from a donor `spec.md`; never embed a copy.
- ⚠ **`WHY_HEAD` NAMES the finding, never a bare number** — *"every rung is a
  spelling"*, not *"finding 14"*, which is a **live collision** (ladder 14 is
  p13). **Follow p36, not p22/p27/p38.**
- ⚠ **SEARCH BOTH SIDES AND COUNT THE LEVERS ON EACH.** *A difference is only as
  honest as its WEAKER-searched endpoint.* **p36 searched R4 first and correctly
  — and then published against an R3 side with ONE lever, which moved R3 the
  wrong way; `+15.00` was `+7`.** Publish the **fixed-R4 bound**, the **span**,
  the words **"cheapest found"**, the **input named**, and **the lever count per
  side**. **No pair interval** unless you built an admissible R4 that moves.
  ⚠ **On this pattern R3 has at least four levers by construction** —
  `checked_`, `saturating_`, `wrapping_`, plain `+` — **so an unsearched R3 side
  has no excuse here.**
- ⚠ **A fitted law owes its DOMAIN, and check the RESIDUE CLASS of any parameter
  your bands hold constant.** p38's additivity failure was 100% attributable to
  three missing columns, two of its bands sitting at `nw ≡ 0 (mod 8)`.
- **No `ns` claim without a layout population**; port `controls/clayout.py` and
  ⚠ **point `OUT` and its scratch default at your own scratch dir** — p27's copy
  still said `.temp/p14/` and overwrote p14's `meta.json`.
- **Adversarial rows per rung**, **TCB as one number plus the U-license / V-gap /
  infra classification**, and **two proof mutants that FAIL** — ⚠ **run the
  battery with `--multiple-errors`**; p22 skipped it and the review found a
  mutant failing on a different obligation than claimed.
- ⚠ **`forbidden_hits` HARD-FAILS**, and **backtick every entry you want
  enforced** — an unbackticked entry is audited **zero** times. Recompute the
  denominator rather than quoting one:
  ```
  python3 -c "import glob,json;print(sum(json.load(open(f))['idiom_audit']['forbidden_spellings'] for f in glob.glob('results/gate/p*.json')))"
  ```

## Secondary, and only if §0 refuses p45: RECAP "Owed" 4

**p17 ships no `sweep-*` inputs**, so its published *"+32 `Ir`/call flat"* was
fitted from two bands that **both had `nsuf = 3`** — the same residue-class
failure that broke p38's additivity, sitting inside a published law. A `sweep-*`
band appended last costs **one gate re-run, not a re-measure**. You proposed this
as the cheaper alternative; it stands.

## Done when

§0a's and §0b's decisions are written with their arguments — **and if either is
"do not build", that plus the measurements IS the deliverable.** Otherwise: the
checklist above; complete `harness/check.py p45` (**say up front which verdict
you expect and why**); checksums against an independent `model.py`; two failing
proof mutants with `--multiple-errors` output; `measure.py --check-stale` clean.
**Paste actual output.** ⚠ Doc edits make a gate record STALE — re-run after.

⚠ **Expect `PASS`.** A blocked Miri row is **no longer** a by-design outcome:
`check_miri` reads stage 4's **measured** per-rung `hung` column. **If a row
blocks, that is a finding, not a shrug.**

## ⚠ Also attack these — TASK_079's PROVISIONAL findings, per rule 9

They are in `.memory/` **marked PROVISIONAL and unreviewed**, and this is the
task that gets to break them. **A named attack that does not land is worth
reporting** (rule 6).

- `.memory/03-measurement.md` — the **kernel-column sign reversal** on the
  allocator pair (`main` 990,034 against 1,100,035 while the whole program is
  8.6× dearer; 89.75% of cost inside libc). **The elision above it is
  manager-verified; this is not.**
- `.memory/03-measurement.md` — the **open question about p27's committed
  `0.00 allocator` term**. It is asked, not asserted. **One `objdump | grep` on a
  committed binary settles it**, and it is a two-minute job if you are already in
  the tree.
- `.memory/00-environment.md` — all three sanitizer items: gcc's
  `-fsanitize=pointer-overflow` **missing** the unsigned-huge offset clang
  catches, ASan's redzones destroying object adjacency, and
  `-fsanitize=alignment` being **in** both default sets. ⚠ **The third one bears
  directly on your own pattern** — you will be relying on
  `-fsanitize=signed-integer-overflow` being in gcc's default set, which the
  manager verified, but the *alignment* claim beside it is unreviewed.
- `.memory/04-verus.md` — the **raw-pointer arena** section. The
  `6 verified, 0 errors` is manager-verified; the readings around it are not.

## Constraints

⚠ **`ls` any scratch path before you name it.** `.temp/pNN/` is a **live
collision between PATTERN and TASK directories** — `.temp/p31/` is TASK_031's
layout evidence and `.temp/p48/` is TASK_048's, and both were nearly destroyed by
a manager prescription. **`.temp/p45/` may or may not exist; check, and if it
does, use `.temp/p45pat/`.** `.temp/p31pat/` is **readable, NOT writable.**

No root; no `/tmp`; **no `git add`/`git commit`**; do not edit `pilot/`,
`.memory/`, `harness/`, `common/`, or any existing pattern. **If p45 seems to
need a `harness/` change, STOP and report it** — PROTOCOL rule 5's default
applies unweakened: the `harness/` batch closed at TASK_078 and the queue of
*measured* gate defects is **empty**, so a new gate check needs the *"could this
happen by accident?"* test first. Verus only via `./verus_run.py`;
`~/tools/verus/vstd/` for vstd source — **never** `../LearnVeri/_VERUS_DOC_/vstd/`,
an older snapshot that caused one false *"no spec exists"* that stood for 44
tasks. clang `~/tools/llvm/bin/clang`, gcc `/usr/bin/gcc`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — **none but gcc on
PATH**. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**;
⚠ **no self-matching `pgrep` wait-loops**. Measurements in the **FOREGROUND**.
**You are the only agent running.**

Notes to your scratch `NOTES.md` as you go, so a transient API death loses
nothing.

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 208** — **+5 from your own last task**, including both calls the manager
named as least certain. **The count is the evidence that this instruction is not
a courtesy.**

**What I am least sure of, by name: §0a objection 1 — whether p45's harm is a
genuinely new class or the tree's THIRTEENTH `index >= len` arriving by a new
route.** I think the answer is that the class is *the optimiser deleting the
programmer's own check*, which puts p45 with p38 rather than with the twelve —
but **I have not measured it, and the equivalent claim about p31's exhaustion
sub-case was mine and was wrong one task ago.** ⚠ **If the honest answer is "the
harm is a buffer overflow", say so** — and then the question becomes whether the
*route* is worth a pattern, which is p36's question and p36 answered it "yes" on
three grounds. **Check p45 against all three before agreeing with me.**

**Second-least sure: §0a objection 2's escape route.** I do not know whether
`unchecked_add` is supported at the pinned vstd, and **the entire R4 rung depends
on it.** Four patterns have had an R4 candidate die on `is not supported` at this
pin. **Run that probe first** — it is the cheapest thing in this file and it can
end the task.
