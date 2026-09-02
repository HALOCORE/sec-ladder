# TASK_169 REPORT — review of `TASK_168` and of the manager's fold at `0678b2d`

**Role: research reviewer. I did not fix anything.** No `git add`, no `git commit`,
no history-mutating git. No sweep, no re-measure, no `outward_ir.json` re-emit —
**none was needed**; every arm in items 1 and 2 is a pure function or a selftest
cell and was driven in process, and every number in items 3, 5 and 6 came out of
a committed record, a committed source, or the already-warm `.temp/build/`.
Scratch: `.temp/t169/`. No earlier `.temp/t*/` or `.temp/mgr*/` was modified.

---

## HEADLINE

**Both new stages fire. Neither fails open. The parser widening is real. The
whitelist-grep attack on the `rep` census does not land.** The defects are one
level out from where the task file pointed them — and **three of them are in the
`✅` marks of finding 65(b)**:

0. ⚠⚠⚠ **THREE `✅`-MARKED CLAIMS IN FINDING 65(b) ARE FALSE.**
   (a) *"all 34 instructions are the WORD-wise form (`rep stos %rax`, ≈0.126
   `Ir`/byte)"* — **16 of 34 are `rep stos %eax` at 0.25 `Ir`/byte and 2 are
   `rep movsq`**. (b) The old sentence's conclusion, *"no previously published
   `Ir` comparison is contaminated"*, **falls on a LICENSED published row**:
   `p27 gcc-clang` (`−25.02 / −201.73`) carries gcc's 32-`Ir` `rep stos` against
   clang's 19-`Ir` vector spelling — over half its magnitude. (c) *"gcc's `Ir`
   UNDERSTATES its work … on nine patterns instead of one"* — **p08's direction
   needs a transfer over the 2048-byte threshold; it zeroes 4096 and the other
   five zero 128–768, where gcc is DEARER than clang.** The report itself was
   more careful than the fold on (a) and explicitly declined (b).
1. ⚠⚠⚠ **The manager's scoping call SURVIVES for the gate and FALLS as a
   statement of exposure.** `.memory/`'s six are **not** the remaining set.
   **`RECAP.md` — the handoff document — carries SIX of its own, at least four
   rotten**, and **`results/synthesis.md`, a PUBLISHED artefact, carries a
   `check.py:3303` emitted by `synthesize.py`** — a coordinate `.memory/` itself
   already records as rotted, and repaired **in its own copy of the same
   sentence** and not in the generator. Nothing in the report, finding 65, queue
   item 38 or the commit message mentions RECAP.md or `synthesis/` at all.
2. ⚠⚠⚠ **`.memory/03-measurement.md` STILL ASSERTS THE FALSE SENTENCE, at
   `:502–504`, un-annotated**, sixty lines below the correction the fold
   inserted at `:439`. A reader who finds the sentence gets *"so no previously
   published `Ir` comparison is contaminated"* with no signal. This is
   `PROTOCOL` rule 13 exactly — and rule 9's *"annotate as DISPUTED, do not
   leave it standing"*.
3. ⚠⚠ **The `≈426 Ir` counterfactual — the load-bearing input to the published
   *"~90% is COUNTER, not code"* — applies the `memcpy` vector-path constant
   (`0.104 Ir`/byte) to a `memset`-class zeroing.** That is the *exact* error
   finding 65(a) exists to name (*"two libc routines, two thresholds, and the
   manager quoted one at the other"*), committed one level down. **And
   `.memory/03-measurement.md:483–489` already carries the right instrument:**
   a `vec![0; n]`-against-`MaybeUninit` probe whose **n = 4096 row is
   `4154.94 Ir`** — p42's `+4160.00` to **0.12%** — four lines below the block
   the fold inserted. The headline survives (88.5% instead of 89.8%); the
   derivation does not, and the manager marked it **✅**.
4. ⚠⚠ **The `vparse` comment's stated direction argument is FALSE**, and the
   widening adds false positives in the direction it claims to protect.
5. ⚠ **Queue item 37 is wrong about its own cost before it becomes a task:**
   **4 of the 33 stale pins move files that ARE in `measurement_sources`**, so
   the proposed replacement pin **still reports 4 of 33 STALE** on the same
   evidence.

**Per-item verdicts** (§1–6), then **fourteen clean negatives, none repeated
from `TASK_166` or `TASK_167`**, then the two deliverable answers.

---

## Did

* Loaded `harness/check.py` from source in process (`__file__` pinned to the real
  path so `REPO` and the sibling imports resolve) and **drove all twelve
  must-fire arms of stages `0c`/`0d`, then broke each one** with a plausible
  regression — `.temp/t169/arm_break.py`.
* Attacked `0c`'s **regex** over fourteen citation spellings and its
  **`patterns/`-only scope** over every tracked text file in the repo, using
  `check.py`'s own `citation_verdict` — `.temp/t169/cite_scope.py`.
* Confirmed stage placement above `fixture.ensure()` by driving `check_selftests`
  with `fixture.ensure` forced `False` and the arms planted broken —
  `.temp/t169/placement.py`.
* Re-derived the `vparse` widening against the **actual pre-change file**
  (`git show 0678b2d~1:harness/vparse.py`), not by string substitution, and ran
  28 break cases — `.temp/t169/vparse_probe.py`, `.temp/t169/vparse_OLD.py`.
* Re-derived `outward_ir.json`'s 33-of-33 staleness **and which files cause it**,
  which is what tests queue item 37.
* Re-derived the `≈426` counterfactual from `.memory/`'s own zero-fill probe.
* Re-ran the four closing checks individually, each read from its own `rc`.
* Re-ran the `rep` census from an unmodified copy of `.temp/t168/rep_scan.py`
  (`.temp/t169/rep_scan_copy.py`, `rc=0`) and drove `asm.try_kernel` directly
  over p08's full 16-cell `-O3` matrix to test the whitelist-grep hypothesis.
* Re-derived `p42`'s `+4160.00` myself out of `synthesis/outward_ir.json`, and
  the `≈426` counterfactual out of `.memory/`'s own zero-fill probe.
* Delegated three independent re-derivations (item A's numbers and the window
  census, the eight citation rewrites, the two overruns + the prediction); their
  output is folded in below and attributed. Scratch for those sits under
  `.temp/t169/itemA/`, `.temp/t169/cites/`, `.temp/t169/overruns/`.

---

## §1. THE TWO NEW STAGES — **SURVIVES, NARROWED**

### 1a. All twelve arms fire. Eleven of twelve are armed against the property they name.

`.temp/t169/arm_break.py` loads a **fresh** module per mutation so mutations do
not compose, drives each arm's own input, and reports whether the arm's `got`
moves away from its `want`:

```
[C1] ARM FIRES  CITE_FATAL_MODULE = "checker.py"        base ('FAIL',[(1,'check.py',1249)],[])  mutated ('OK',[],[(1,'check.py',1249)])
[C2] ARM FIRES  line_citations widened to `mod.py::fn`  base ('OK',[],[])                       mutated ('FAIL',[(1,'check.py',0)],[])
[C3] ARM FIRES  _CITE_RE gains \b(?!-) so a RANGE stops base ('FAIL',[(1,'check.py',1249)],[])  mutated ('OK',[],[])
[C4] ARM FIRES  line_citations ignores `names`          base ('OK',[],[])                       mutated ('OK',[],[(1,'model.py',50),(1,'gen.py',30)])
[C5] ARM FIRES  citation_verdict makes EVERYTHING fatal base ('OK',[],[(1,'measure.py',64)])    mutated ('FAIL',[(1,'measure.py',64)],[])
[C6] !! DID NOT FIRE  _CITE_RE loses its leading \b     base ('FAIL',[(1,'check.py',1)],[])     mutated ('FAIL',[(1,'check.py',1)],[])

[D1] ARM FIRES  codegen_cfg_verdict stops comparing     ('FAIL',['slb_bogus'],0) -> ('OK',[],0)
[D2] ARM FIRES  build_cfg_flags forgets `--cfg=NAME`    ('FAIL',['slb_bogus'],0) -> ('OK',[],0)
[D3] ARM FIRES  CODEGEN_CFGS loses `slb_isolated`       ('OK',[],0) -> ('FAIL',['slb_isolated'],0)
[D4] ARM FIRES  build_cfg_flags replaced by a GREP      ('OK',[],0) -> ('FAIL',['slb_bogus'],0)
[D5] ARM FIRES  the `unresolved` counter is dropped     ('OK',[],1) -> ('OK',[],0)
[D6] ARM FIRES  the `unresolved` counter is dropped     ('OK',[],1) -> ('OK',[],0)
```

**Eleven of twelve are genuine arms.** `D4` in particular is the good one: it
fires precisely under the grep the docstring says the tokeniser exists to beat.

### 1b. `minor` — **arm C6's `\b` clause is UNARMED. `_CITE_RE`'s `\b` is blind to all six arms.**

`_CITE_RE`'s leading `\b` (`harness/check.py:972`) is not distinguished by **any**
of the six 0c arms. `.temp/t169/cite_scope.py` §B, running all six under a regex
with the `\b` removed:

```
  arm C1: with \b -> ('FAIL', [(1, 'check.py', 1249)], [])
           no \b -> ('FAIL', [(1, 'check.py', 1249)], [])   SAME (arm blind to \b)
  ... C2 C3 C4 C5 C6 all SAME ...
  arms that distinguish the `\b` anchor: 0 of 6
```

The reason is that `xcheck.py:1` is already rejected by the **greedy** name match
plus the `names` whitelist, not by `\b`: `finditer` consumes `xcheck.py` whole,
`'xcheck.py' not in names`, done. The case that *does* distinguish it is a
digit-glued prefix, where the greedy match cannot start:

```
    'see `12check.py:5`'
      shipped: ('OK', [], [])
      no \b  : ('FAIL', [(1, 'check.py', 5)], [])
```

**Failure scenario:** someone simplifies `_CITE_RE` by dropping `\b` (it looks
redundant, and against the shipped arms it *is*); `12check.py:5` and
`p2check.py:9` then hard-fail a pattern. Nothing in the arm set notices.
`harness/check.py:1262–1265`'s label — *"`checkNpy:1` and `xcheck.py:1` do not
match"* — describes a property the regex has for a different reason than the
label implies. Two of its three clauses are controls; only *"`harness/check.py:1`
does"* is load-bearing.

### 1c. `major` — **`0c`/`0d`'s arms are the only ones in `check.py` with NO `RAISED` guard, and a throw takes the gate down at IMPORT.**

`_CITE_VERDICT_CASES` (`:1244`) and `_CFG_VERDICT_CASES` (`:1268`) call
`citation_verdict` / `codegen_cfg_verdict` **bare at module scope**. The two most
recent precedents both wrap:

```
  _ASSUME_CASES (TASK_151): helper `_ak` has try/except -> YES
  _CONTROL_VERDICT_CASES (TASK_164): helper `_cv` has try/except -> YES
  _CITE_VERDICT_CASES / _CFG_VERDICT_CASES: call the function BARE at module scope -> NO guard
```

and both say so in their own docstrings (`:913–914`, `:923–924`:
*"`got[0] == "RAISED"` means … it threw — reported, not crashed
(`.memory/03-measurement.md` entry 19)"*). Demonstrated, by planting a raise into
`citation_verdict` in a copy of the source and importing it:

```
=== the RAISED-guard gap: what happens if citation_verdict throws? ===
  !! harness/check.py FAILS TO IMPORT: RuntimeError: a plausible regression, ...
     -> every stage on every pattern dies with a traceback,
        no verdict, no results/gate/*.json.
```

**Failure scenario:** a future widening of `_CITE_RE` that makes
`int(m.group(2))` see a non-digit — the shape of C2's own mutation — turns a
designed one-line gate failure into a repo-wide import traceback with no
`results/gate/*.json` written for **any** pattern. `check.py:9836–9840` already
carries this exact lesson for `run_budgets` (*"indexing here turned a clean gate
failure into a Python traceback with no verdict"*, TASK_068_REVIEW M5).

### 1d. The regex: what it catches, what it misses, and where it draws the line

`.temp/t169/cite_scope.py` §A, all fourteen spellings through `citation_verdict`:

```
  FAIL  a plain citation                   | 'see `check.py:1249`'
  FAIL  a RANGE (the tree had one)         | 'see `check.py:1249-1278`'
  FAIL  with a path prefix                 | 'see `harness/check.py:1249`'
  FAIL  an emdash range                    | 'see `check.py:1249–1278`'
  FAIL  inside a python string literal     | 'MSG = "cited from check.py:1249"'
  FAIL  inside a docstring                 | '"""derived at check.py:1249."""'
  OK    prose: backticked file, bare line  | 'see `check.py` line 1249'
  OK    prose: comma form                  | 'see check.py, line 1249'
  OK    a Python traceback                 | '  File "harness/check.py", line 1249, in main'
  OK    a github-style anchor              | 'see harness/check.py#L1249'
  OK    an L-prefixed line                 | 'see `check.py:L1249`'
  OK    a colon-space form                 | 'see check.py: 1249'
  OK    the FUNCTION convention            | 'see `check.py::check_checksums`'
  OK    a digit-glued lookalike            | 'see `12check.py:5`'
```

✅ Range, path prefix and `.md` are all caught (`_pattern_text_files` walks every
file whose extension is not in `_CITE_SKIP_EXT`, so `.md`, `.py`, `.json`, `.sh`
are all read — **659 files across the 33 patterns**, walk time `0.00 s`, no file
over 2 MB). ✅ The em-dash range is caught too, which no arm covers.
✅ **The line between citation and mention is drawn at "raw text, no code
parsing"**, so a string literal or docstring is flagged — which is the right
side to err on given the *no escape hatch* design (`line_citations`' docstring),
and the documented workaround (*"spell it without the colon"*) works.

**The prose forms are the miss, and it is unrealised.** Hunted across the tree:

```
=== forms 0c MISSES, hunted under patterns/ ===
check\.py`? line [0-9]             : 0
check\.py", line [0-9]             : 0
check\.py#L[0-9]                   : 0
check\.py:L[0-9]                   : 0
check\.py at line                  : 0
line [0-9]+ of .?check\.py         : 0
```

and the **only** occurrence anywhere in the tracked tree is `.tasks/TASK_169.md:48`
— the task file's own example. **Clean negative.**

### 1e. ⚠⚠⚠ THE CALL NAMED FOR ATTACK — `0c` scans `patterns/` ONLY

**Verdict: the GATE scoping decision SURVIVES. The claim of remaining exposure
that came with it FALLS.**

**The scoping is right, for two reasons the fold does not state:**

1. **A per-pattern stage is the wrong instrument for a repo-wide convention.**
   `0c` runs 33 times; scanning `.memory/` from it would report the same six
   failures 33 times and couple every pattern's verdict to manager-owned files
   nobody edits during a build.
2. **`line_citations` has, deliberately, no escape hatch — and `.memory/` needs
   one.** Three of `.memory/`'s six citations are **deliberate quotations of a
   rotted citation, as evidence**, and the stage would hard-fail all three:

   ```
   .memory/03-measurement.md:3355  '⚠ **This sentence carried `check.py:3303` until `TASK_164`, by which time'
   .memory/06-catalogue.md:842     '> - **`check.py:1249` is not the checksum rule** — it is a selftest for'
   .memory/06-catalogue.md:414     '... MANAGER-VERIFIED AT `harness/check.py:3941` — ⚠ the line has since moved to `3972`; cite the predicate, not the number'
   ```

   The documented workaround (*"spell it without the colon"*) **destroys the
   evidence** in each case: the sentence's whole subject is the coordinate.

✅ **The right home already exists and the report names its precedent without
using it: `harness/tools/temp_citations.py`** — repo-wide, out of both digests,
with a curated baseline and an `--update` path, and its own header explains
exactly why a hygiene checker belongs there rather than in `harness/*.py`. That
is a repo-wide `check.py:NNNN` scan for ~40 lines, with the escape hatch the
`.memory/` cases need, and **no sweep**.

**And the exposure claim is wrong. Scanned with `check.py`'s own
`citation_verdict` over every tracked text file** (`.temp/t169/cite_scope.py` §C):

```
  (root)        fatal(check.py:NNNN)=   6   other harness modules=   8
      RECAP.md :3823 -> check.py:4178 · :3842 -> check.py:3941 · :4649 -> check.py:2387
               :5179 -> check.py:3941 · :5439 -> check.py:3303 · :5458 -> check.py:2805
  .memory       fatal=   6   other=   7      (03-measurement.md ×3, 06-catalogue.md ×3)
  harness       fatal=   6   other=   6      (check.py's own 0c docstring + arm literals)
  patterns      fatal=   0   other=  13
  results       fatal=   1   other=  13      results/synthesis.md:224 -> check.py:3303
  synthesis     fatal=   2   other=   0      synthesize.py:659 and :1400 -> check.py:3303
  .tasks        fatal= 372   other= 124      (history — correctly out of scope)
```

Three things follow, none of them in the report, in finding 65, in queue item 38
or in the commit message:

* ⚠⚠ **`RECAP.md` has SIX of its own and at least four are rotten now.** Resolved
  against the current `check.py`:

  ```
  RECAP.md:3823 -> check.py:4178   now '    for c in cfgs:'                          in def _dep_info_files
      ctx: "`#[verifier::external_body]` body (`check.py:4178-4180` is the ONE allowed"
  RECAP.md:3842 -> check.py:3941   now '    longer = min(RUN_BUDGET_CONFIRM * ...'   in def _confirm_hang
      ctx: "`harness/check.py:3941`: `cand += _include_literals(txt)[0]`, so"
  RECAP.md:4649 -> check.py:2387   now '                  f"does not have.")'        in def forbidden_verdict
  RECAP.md:5439 -> check.py:3303   now '        WHOLE tree, 66 (pattern, input)...'  in def check_marginal_ir
  ```

  `RECAP.md` is the file `CLAUDE.md` says to *"Read first, always"*. It is a
  strictly worse place for a rotted pointer than a pattern's `inputs/gen.py`.
* ⚠⚠⚠ **`results/synthesis.md:224` — a PUBLISHED artefact — carries
  `check.py:3303`, emitted by `synthesis/synthesize.py:1400`**, and the citation
  is **belt-and-braces**: it names the function *and* the line.

  ```
  synthesize.py:1400   "`check.py::check_identity` compares their "
                       "`-O3 isolated` digests (`check.py:3303`) — so on **this column** ..."
  ```

  `check_identity` is at `harness/check.py:3719`; `:3303` is a data line inside
  `check_marginal_ir`'s docstring. **And `.memory/03-measurement.md:3355–3359`
  already records this exact coordinate as rotted and says the repair —
  *"Fixed by deleting the number, not by updating it"* — was applied.** It was
  applied to `.memory/`'s copy of the sentence and **not** to the generator that
  re-emits the other copy into the published file on every run. That is
  `PROTOCOL` rule 6's own *artefact-vs-generator skew* (*"Three tasks in a row
  shipped an edit the generator would have silently reverted"*), on the
  citation-rot class the whole item is about.
* `harness/check.py` itself carries six (`:942` quoting the historical
  `check.py:8841`, plus the arm literals at `:1246/:1252/:1254/:1262/:1263`).
  Correct as fixtures — but they mean the stage **cannot be widened to
  `harness/` without an escape hatch either.**

**What enforcement in `.memory/`+`RECAP.md` would cost:** nothing measurable —
neither is in the gate digest for `.memory/` (`RECAP.md` and `.memory/*.md` are
absent from `check.py`'s `srcs` glob at `:9985–9995`) and neither is in
`measurement_sources` (`measure.py:224–235`). **A scan is free; the cost is
entirely the three evidence-quotations, which need an opt-out.**

### 1f. `0d` reads `build.py` LIVE. **Not a second hand-maintained list** — for the direction it checks.

`check_codegen_cfgs` (`:1133–1139`) opens `buildmod.__file__` and **tokenises**
it. That is the live file; `CODEGEN_CFGS` is only the *allowed* set. The
direction is the one queue item 16(b) named: a **new** `--cfg` in `build.py` that
`CODEGEN_CFGS` lacks → `_cfg_reaches_codegen` answers *"no"* → `_blank_unbuilt_cfg`
deletes the item → the idiom audit stops seeing it. `0d` fails on exactly that.
Verified against all 33 records:

```
codegen verdicts   : Counter({'OK': 33})
build_py_cfgs      : Counter({"['slb_isolated']": 33})
unresolved         : Counter({0: 33})
```

⚠ **Three narrowings, all `minor`:**

* **The reverse direction is unchecked.** 17 of `CODEGEN_CFGS`' 18 names are
  never cross-checked against anything — `miri` is set by the stage-8
  interpreter, not by `build.py`, and the other 16 are rustc built-ins. `0d`'s
  `ok` line, *"all in CODEGEN_CFGS (18 names)"*, reads as if 18 were covered.
* ⚠ **`harness/limbs.py:208` is a SECOND `--cfg` producer inside `harness/` and
  `0d` does not read it:** `verus(path, "--cfg", TWIN_CFG)` with
  `TWIN_CFG = "slb_twin"` (`check.py:3982`), which is **not** in `CODEGEN_CFGS`.
  This is **correct today** — `slb_twin` gates verify-only twin bodies that
  `build.py` never compiles, and blanking them is deliberate
  (`check.py`'s header, TASK_069) — but the stage's scope is `build.py`, not
  *"every `--cfg` the harness passes"*, and its docstring does not say so.
* **A cfg passed through a constant degrades to a shout.** Pointed at
  `limbs.py`, `build_cfg_flags` returns `([], 1)` — one `unresolved`, no name.
  If `build.py` ever spells `f += ["--cfg", ISOLATED_CFG]`, `0d` shouts instead
  of failing. Documented in the docstring; worth knowing it is the live shape
  one directory over.

### 1g. Placement above `fixture.ensure()` — **CONFIRMED, and it cannot make a fixture-less run look green.**

`.temp/t169/placement.py` drives `check_selftests` with `fixture.ensure` forced
`False` and a wrong `want` planted on the first arm of each new set:

```
fixture.ensure -> True  | arms planted broken: False   rep: clean
fixture.ensure -> True  | arms planted broken: True    doc-citation-selftest, codegen-cfg-selftest
fixture.ensure -> FALSE | arms planted broken: False   fixture
fixture.ensure -> FALSE | arms planted broken: True    doc-citation-selftest, codegen-cfg-selftest, fixture
```

Both new arm sets fire with no fixture; the `fixture` failure is still raised, so
the run is red either way. And `check_doc_citations`/`check_codegen_cfgs`
themselves are called from `main` at `:9831–9832`, outside `check_selftests`, so
they run regardless of the early return. ✅ **The report's claim is exactly true.**

---

## §2. THE PARSER WIDENING — **SURVIVES, NARROWED. One `major`.**

### 2a. The three arms genuinely fail against the old matcher — re-derived independently.

I did **not** rebuild the old predicate by substitution (the engineer's method).
I loaded `git show 0678b2d~1:harness/vparse.py` as a module and ran both.
`.temp/t169/vparse_probe.py`:

```
  arm 1: unknown `global` after `}` ON THE SAME LINE      old=[] new=[('global','?')]  ARM FIRES
  arm 2: unknown `global` after `;` ON THE SAME LINE      old=[] new=[('global','?')]  ARM FIRES
  arm 3: unknown `global` after an ATTRIBUTE              old=[] new=[('global','?')]  ARM FIRES
  CONTROL: a KNOWN `global size_of` sharing a line        old==new                      (correctly labelled)
  NEGATIVE: a LOCAL named `global`                        old==new==[]
  the PRE-EXISTING own-line arm                           old==new
```

✅ **All three confirmed.** ✅ **And the engineer's relabelling of the fourth cell
from "arm" to "CONTROL" is correct** — it passes under both, exactly as the
comment now says.

### 2b. `minor` — the census is **161**, not 152, and `vparse.py` says so nine lines from the change.

```
git ls-files '*.rs'             : 161
  under patterns/               : 151
  under pilot/                  :   4
  common/ + .tasks/TASK_134_ART :   6
```

`harness/vparse.py:857` — inside the very comment block `TASK_168` rewrote —
says *"across all 161 tracked `.rs`"*. The report (`:280`) and **`RECAP.md:6112`**
say **152**. Re-derived over all **161**:

```
  tracked .rs scanned            : 161
  files whose axiom_decls MOVED  : 0
  total `global*` declarations seen by the NEW matcher: 10
  {'global size_of usize': 7, 'global layout Obj': 2, 'global layout Rec': 1}
```

✅ **The 0-of-N conclusion is stronger than claimed** (0 of 161), and the census
of 10 reproduces `.memory/`'s TASK_164 figure exactly. Only the denominator in
`RECAP.md` is wrong.

### 2c. `major` — **the comment's stated direction argument is FALSE, and the widening adds false positives in that very direction.**

`harness/vparse.py:872–876` asserts:

> *"It still rejects `let global`, `= global`, `(global`, `, global` and
> `.global`, **which is every shape a local named `global` can appear in**.
> Direction: **a false POSITIVE shouts and can turn a green pattern red**, a
> false NEGATIVE hides a trusted declaration — so the anchor is TIGHTENED rather
> than dropped."*

**Both halves are wrong.**

**(i) It is not every shape.** A local named `global` also appears bare as a
block-final expression and as a bare statement, and both are preceded by `{` or
`;` — which the new anchor accepts:

```
  old=[]  new=[('global','?')]  | `if c { global } else { 0 }`
  old=[]  new=[('global','?')]  | a closure body `|| { global }`
  old=[]  new=[('global','?')]  | a block-final expression `fn f(global: u8) -> u8 { global }`
  old=[]  new=[('global','?')]  | a statement-position local after `;`
  old=[]  new=[('global','?')]  | a struct FIELD named `global`  (`struct S { global: u8 }`)
  old=[]  new=[('global','?')]  | an ENUM VARIANT named `global`
  old=[]  new=[('global','?')]  | inside a `macro_rules!` body
```

⚠ **And the `_selftest` negative added alongside the widening** — *"`global`
after `=`, `(`, `,` and `.` is still not a directive"*, `vparse.py:2255–2260` —
**covers exactly the five shapes the comment enumerates and none of the six the
widening actually admits.** The negative control was written from the comment's
list rather than from the language. That is item 33's own defect one level
further down, for the second time in the same edit — the engineer caught the
first instance (the mislabelled control) and not this one.

⚠ The pre-existing line-anchored matcher was already wrong on four of them
(idiomatic multi-line spellings put `global` alone on a line):

```
  old=[('global','?')] new=[('global','?')]  | fn f(global: u8) -> u8 {\n    global\n}
  old=[('global','?')] new=[('global','?')]  | struct S {\n    global: u8,\n}
```

so the widening does not *create* the class — it **enlarges** it from
own-line-only to own-line-plus-`{`/`;`/`]`.

**(ii) A false positive does NOT shout and CANNOT turn a pattern red.** Traced:
`check_verus_contract` (`check.py:4899–4907`) splits `axiom_decls` on
`vparse.GLOBAL_KINDS`, and `"global"` **is** in `GLOBAL_KINDS`
(`vparse.py:678`), so an unclassified `global` is excluded from the **pinned**
`axioms` count, is only `print`ed, and is written to the record as
`global_decls` (`:5454`). No `rep.fail`, no `rep.shout`. What it *does* do is
move a **published** column: `synthesis/synthesize.py:1835` prints
`len(v.get('global_decls'))` as its own column in `results/synthesis.md` §3, and
`:1695–1700` publishes `n_glob_rows` in prose.

**So the real direction is the opposite of the one stated:** a false positive
silently inflates a published count, a false negative silently deflates it, and
neither is loud. The design choice may still be right; **the argument written
into the file to justify it is not.**

⚠ Prospective, as the comment says: no shipped `.rs` has a local named `global`
(0 of 161 moved). Severity `major` because the sentence is a *checkable* claim
about the code that is false, and it is the sentence the next agent will read
before touching the anchor.

### 2d. Clean negatives on the new matcher

`blank_noncode` handles all of them correctly — a `global` in a raw string
(`r#"…"#`), a nested-hash raw string (`r##"…"##`), a byte string, a `//` comment
after a `}`, and a `/* … */` block comment **all score `[]` under both
matchers**. A `global` split across lines, a `global size_of` split across
lines, and a `global layout` split across lines are all classified correctly
under both — the anchor is about the *preceding* character, so line splits after
the keyword never mattered. `crate::global::f()`, `x\n.global()` and
`_ => global,` are all correctly rejected.

---

## §3. ITEM A's ANSWER — **`+4160.00` SURVIVES (stronger). `≈426` FALLS. The `rep` census SURVIVES the attack.**

### 3a. `+4160.00` and `1.0156 Ir`/byte — re-derived from `synthesis/outward_ir.json`, independently.

```
===== large.bin (n_iters 1500) =====
  safe_naive  out_ir/call=  4540.00
      __rustc::__rust_alloc_zeroed           4342.00 Ir/call  n=1.0000/kernel call
      __rustc::__rust_dealloc                 197.00 Ir/call  n=1.0000/kernel call
  unsafe      out_ir/call=   380.00
      __rustc::__rust_alloc                   182.00 Ir/call  n=1.0000/kernel call
      __rustc::__rust_dealloc                 197.00 Ir/call  n=1.0000/kernel call
  DELTA alloc_zeroed - alloc = 4342.00 - 182.00 = 4160.00
```

`4160 / 4096 = 1.015625`. ✅ **Confirmed exactly**, at `n = 1.0` call per kernel
call, on the `-O3 isolated` quadrant `outward_ir.py::run_pattern` defaults to.
`safe_tuned` and `verus` both spell `__rust_alloc` at `182.00`, so the term is
`safe_naive` alone. The rung spellings are as reported —
`safe_naive.rs:52` `vec![0u8; len]`, `safe_tuned.rs:46` `Vec::with_capacity(len)`.

⚠ `minor` — **the report's `small.bin` figure is the wrong quantity.** It says
*"On `small.bin` … the term is +189.01"*. `189.01` is `alloc_zeroed`'s **absolute
cost**, not the term:

```
===== small.bin =====
  safe_naive  out_ir/call=296.01   alloc_zeroed 189.01 · dealloc 106.00
  unsafe      out_ir/call=143.00   alloc         55.00 · dealloc  87.00
  DELTA alloc_zeroed - alloc = 134.01      total outward delta = 153.01
```

The published correction is `+153.00` (`results/synthesis.md:345`), of which
`+134.01` is the alloc delta and `+19.00` is a dealloc difference the report does
not mention. On `large` the dealloc terms are equal (197 = 197), which is *why*
`+4160.00` there happens to be exactly the alloc delta.

⚠ `minor` — **`unsafe` does not spell `with_capacity`.**
`patterns/p42-goto-cleanup/unsafe.rs:106–108` uses
`Layout::from_size_align_unchecked` + `std::alloc::alloc`; `safe_tuned.rs:46` is
the `Vec::with_capacity` rung. Both lower to `__rust_alloc` so no number moves,
but `.memory/03-measurement.md:452–453`, `RECAP` 65(a) and the commit message all
say *"`unsafe`'s `with_capacity`"* — a factual error about a rung source, in the
authoritative layer.

### 3b. ⚠⚠ `≈426 Ir` — **FALLS.** The `~90%` headline **SURVIVES**, from both replacements.

`426 = 0.104 × 4096`, and `0.104 Ir`/byte is not a rate someone derived — it is
`.memory/03-measurement.md:387`'s **measurement itself**:

```
| **glibc `memcpy`, 4092 bytes** | **425.7 = 0.104 Ir per byte** |
```

i.e. **glibc `memcpy`'s own 4092-byte figure, re-badged as a `memset`
counterfactual and rounded to 426.** Applying it to a `memset`-class zeroing
repeats finding 65(a)'s own error one level down, in the paragraph that names it.
The two glibc routines are different loops on this box: `0x189480`
(`__memset_avx2_unaligned_erms`) steady state is **7 insns / 128 B = 0.055
Ir/byte**; `0x188a80` (`__memmove_avx_unaligned_erms`) is **~12 / 128 = 0.094**.

**Two better-anchored counterfactuals, from two different instruments, bracket
it — and both are BELOW 426, so the headline gets stronger, not weaker:**

| counterfactual for the `+4160.00` term at n = 4096 | `Ir` | inflation | "is counter" |
|---|---:|---:|---:|
| report's `426` (glibc **memcpy** at 4092 B) | 425.98 | 9.8× | 89.8% |
| `.memory/:483–489`'s `vec![0;n]`-vs-`MaybeUninit` probe, extrapolated from its own sub-threshold rows (fixed 275.64 + 0.04947/B) | **478.3** | 8.7× | 88.5% |
| the pure-memset route: p03/p04's measured **43.00 Ir for a 512-byte** `0x189480` call + that loop's own 7-insn/128 B slope, ⇒ ≈239, + 47 `calloc`-vs-`malloc` bookkeeping | **≈286** | **14.5×** | **93.1%** |

✅ **So *"roughly 90% is COUNTER"* SURVIVES and is conservative** (88.5–93.1%),
⚠ ***"inflated ~10×"* sits at the bottom of an 8.7×–14.5× bracket**, and
⚠ **the `≈426` figure itself FALLS** — it should not be in `.memory/` or in the
commit message.

✅ **And `+4160.00` gets a corroboration the manager did not take**:
`.memory/03-measurement.md:483–489`'s TASK_074 probe of the *same mechanism at
the same n* reads **4154.94** — `+5.06`, **0.12%**.

### 3c. The task's own question — *"divide by ten"* or *"two different programs"*?

**Neither alone, and the tree already answers it.** `patterns/p42-goto-cleanup/safe_naive.rs:21–24`,
a **measurement-hashed** rung source:

> *"`vec![0u8; len]` zeroes what it allocates and the C rung does not, because
> safe Rust has no way to hand out uninitialised bytes. **That cost is real, it
> is R2's to pay**, and R3 is where it is avoided without leaving the safe
> subset."*

So the row is **not** "comparing two different programs" in any illegitimate
sense — R2 doing more work than R3/R4 *is the ladder's subject*. And it is not
"divide by ten" either, because the work is not one tenth of what is claimed.
**The single defect is that `Ir` prices this real, one-sided work in a regime no
other row in that column is in.** Full verdict in **Deliverable 2**.

### 3d. The `rep` census — ⚠⚠ **THE NAMED ATTACK DOES NOT LAND. It is a real census, not a whitelist grep.**

The attack was: does `rep_scan.py` see Rust cells at all? `asm.try_kernel(p, needle)`
is called with `needle = "kernel"` (isolated) / `"main"` (whole), and Rust symbols
are mangled — so a plausible failure is that every Rust window comes back `None`
or empty and *"zero Rust windows"* means *"nobody looked"*. **Driven directly over
p08's full 16-cell `-O3` matrix:**

```
  c-gcc         O3 isolated  sym=<kernel>                                   insns=  118  rep=2
  c-gcc         O3 whole     sym=<main>                                     insns=  229  rep=0
  c-clang       O3 isolated  sym=<kernel>                                   insns=  131  rep=0
  safe_naive    O3 isolated  sym=<_RNvCsaBH6GJeUSWJ_10safe_naive6kernel>    insns=  269  rep=0
  safe_naive    O3 whole     sym=<_RNvCsaBH6GJeUSWJ_10safe_naive4main>      insns=  878  rep=0
  safe_tuned    O3 isolated  sym=<_RNvCs86OlWC8CPt8_10safe_tuned6kernel>    insns=  205  rep=0
  unsafe        O3 isolated  sym=<_RNvCsbJ183vTuGGA_6unsafe6kernel>         insns=  168  rep=0
  verus         O3 isolated  sym=<_RNvCs5wP2qveqZnT_5verus6kernel>          insns=  168  rep=0
  c-gcc-h       O3 isolated  sym=<kernel>                                   insns=  118  rep=2
  c-clang-h     O3 isolated  sym=<kernel>                                   insns=  131  rep=0
```

✅ **`try_kernel` resolves the Rust `v0` mangling**, and the **Rust windows are
LARGER than the C ones** (269 / 878 against 118 / 229). *"Zero clang or Rust
windows"* is a statement about instructions that were actually examined.
**Clean negative: this is NOT `check_miri`'s whitelist-grep, third instance.**

Corroborated across the whole tree: **all 1052 windows were disassembled** —
0 missing binaries, 0 null symbols, 0 empty windows, 0 missing `nm` extents — and
Rust windows carry **193,912** examined instructions against C's **101,434**.
The positive control settles it: every Rust binary carries **48 `rep`
instructions elsewhere** (in `std::backtrace`/`gimli`/`alloc`, never executed)
and **0 inside the window**. The scan looked, in the right place, at more Rust
code than C code.

⚠ **New scope gap (mine, and it is a floor not a census).** In `whole` mode the
symbol is `main`, and gcc's partial inlining leaves executed kernel code
*outside* it:

```
p08 c-gcc/-h  O3 whole  scanned=<main> in_window=0   OUTSIDE: <kernel.part.0> rep stos %rax ×2
p46 c-gcc/-h  O3 whole  scanned=<main> in_window=0   OUTSIDE: <kernel>        rep stos %rax ×1
```

So **26 windows / 34 instructions is a lower bound**; over executed kernel code
it is 30 / 40. The pattern *set* is unchanged (p08 and p46 are already in it),
and excluding callees is **correct** for `kernel_exclusive_ir` — but the census
answers *"is there a `rep` in the counted window"*, not *"in this binary"*.

### 3d(ii). ⚠⚠ `major` — **the `✅`-marked *"all 34 instructions are the WORD-wise form"* is FALSE on 18 of 34.**

`RECAP` finding 65(b) marks **✅ manager-re-derived**:
*"**All 34 instructions are the WORD-wise form (`rep stos %rax`, ≈`0.126`
`Ir`/byte)**, so the direction is that gcc's `Ir` UNDERSTATES its work"*, and the
same sentence is in `.memory/03-measurement.md:468–471` and in the commit
message. Re-run of the census, full instruction text:

```
   16  rep stos %eax,%es:(%rdi)          <- DWORD: 4 bytes/rep = 0.25 Ir/byte
   16  rep stos %rax,%es:(%rdi)          <- QWORD: 8 bytes/rep = 0.125 Ir/byte
    2  rep movsq %ds:(%rsi),%es:(%rdi)   <- a MOVE, not a store
```

**Half are `%eax` at double the quoted rate, and two are not `stos` at all.**
The engineer's own report was more careful — §A4 wrote *"(`%rax`/`%eax`)"* — and
priced both at 0.126; the fold dropped the `%eax` and kept the rate. This is the
`✅` the manager had not earned, third review running.

✅ **Narrowing that partly rescues it, and it is what the fold should say
instead:** split by mode, **every one of the 16 `%eax` is in `whole` mode**, and
`results/synthesis.md:11` states *"Every number below is `-O3 isolated`"*. The
published quadrant's hits are **12 windows, 6 patterns — p08, p14, p27, p29,
p35, p46 — all `rep stos %rax`**, plus p08's two `rep movsq`. So `≈0.126
Ir`/byte is right *for what is published* and wrong *as stated over the 34*.

### 3e. `p08` and *widen*-vs-*contradict* — **it is CONTRADICT, and the old CONCLUSION falls on a LICENSED published row.**

The old sentence is `.memory/03-measurement.md:502–504`:

> *"p01, p05, p16 and p17 call no bulk routine at all. **Only p08's gcc kernels
> contain a `rep` instruction**, so no previously published `Ir` comparison is
> contaminated."*

* **p08 is still in the set** ✓, and the **premise is contradicted on its own
  words**: it says *kernels*, and in `isolated` mode the window **is** `kernel` —
  **six** patterns' gcc kernels hit (p08, p14, p27, p29, p35, p46).
  *"Widen"* describes the phenomenon and is the wrong word for the sentence.
* ⚠⚠ **The CONCLUSION falls, and here is the quantification the report
  explicitly declined to do.** `%rcx` is loaded immediately before every isolated
  `rep stos %rax`, so each is priced exactly:

  | pattern | `%rcx` | bytes | `Ir` charged | published `gcc-clang` small / large | licence |
  |---|---|---:|---:|---:|---|
  | p08 | `$0x200` | 4096 | **512** | 1725.00 / 10256.00 | NOT-LIC |
  | p14 | `$0x10` | 128 | 16 | 965.00 / 331.00 | NOT-LIC |
  | **p27** | `$0x20` | 256 | **32** | **−25.02 / −201.73** | **LICENSED** |
  | p29 | `$0x20` | 256 | 32 | −101.91 / −779.53 | NOT-LIC |
  | p35 | `$0x10` | 128 | 16 | −59.46 / −470.43 | NOT-LIC |
  | p46 | `$0x60` | 768 | **96** | 2163.00 / 5778.00 | NOT-LIC |

  ✅ `gcc-clang` **is** published (`results/synthesis.md:492`), and the 14
  `whole`-mode hits (p06, p23, p32) touch **nothing** published. ⚠ **The one
  genuinely exposed published row is `p27 gcc-clang`, the only LICENSED one:**
  clang's kernel spells the same zeroing as **18 `movaps` + 1 `xorps` = 19 Ir**
  against gcc's **32**, so **≈13–17 `Ir` of a published −25.02 — over half its
  magnitude — is the `rep`-vs-vector spelling in a row the file licenses.**
* ⚠⚠ **AND THE DIRECTION CLAIM FALLS.** *"gcc's `Ir` UNDERSTATES its work …
  on nine patterns instead of one"* (`.memory/`, `RECAP` 65(b), commit message)
  requires clang's counterpart to be **glibc `memset` on the byte-wise path**,
  which needs the transfer to clear `__x86_rep_stosb_threshold` — measured at
  **2048** in `.memory/`. **p08 zeroes 4096 bytes; the other five zero 128–768.**
  Below the threshold clang's side is inline vector stores at **0.066 Ir/byte**
  (p27, measured) — so on those five the `Ir` column charges **gcc MORE**, not
  less, for identical work. **p08 remains the only pattern where the documented
  direction holds, and for a reason none of the other eight share.**
* ⚠ `minor` — a supporting sentence also falls. The report: *"`memset(scr, 0,
  4096)` runs once per kernel call in **all eight cells** at 4113.00 `Ir` … so it
  drops out of every rung pair."* The `0x189480` edge is in **six** cells and is
  **absent from `c-gcc` and `c-gcc-h`**, where gcc inlines it as the 512-`Ir`
  `rep stos %rax`. The **conclusion** (no p08 *rung-pair* number moves) survives —
  R2–R5 are all rustc and all carry 4113.00 — but *"all eight cells"* is false,
  and the gcc/clang asymmetry it papers over **is the finding**.

### 3f. ⚠⚠ OUT OF SCOPE BUT LIVE AND PUBLISHED — `asm.py`'s `main` needle mis-resolves 31 committed records.

Found by the window census, not by anything in `TASK_168`.
`asm.py::find_symbol(needle, pick="largest")` matches by **substring**, so at
`-O0 whole` the `verus` cell's window resolves to

```
_RINvNtNtNtCs4NRVxsYgnAr_4core5slice4sort6stable14driftsort_main…addr2line…LineSequence…gimli…
```

— `core::slice::sort::stable::driftsort_main`, a std backtrace-machinery sort —
because the mangled name **contains** `main` and is 4 instructions larger than
the crate's real `_RNvCs…5verus4main`. **31 of the 33 committed measurement
records carry it** (`grep -lc driftsort results/p*.json` → 31), and it is
**rendered** into `results/tables/pNN-*.md`'s `O0 / whole` block, whose header
says *"static counts are for the `main` symbol"*. The apparent *"the proof
shrinks `main` by 27 instructions and loses the vector registers"* is a symbol
mis-resolution. ✅ **`-O3 isolated` — the only level `results/synthesis.md`
publishes — is unaffected: all 526 `isolated` windows resolve correctly.**
**Reported, not fixed; it predates `TASK_168`.**

### 3g. What survives of finding 65(b), in one line

✅ **`gcc-clang` is published** (`results/synthesis.md:492`, 44 rows) and **is
NOT in `results/SYNTHESIS.md`** — the exposure is bounded to the generated file.
✅ **26 / 1052 / nine patterns / all `c-gcc`-`c-gcc-h` / all `-O3`** reproduces
byte-for-byte. ⚠ *"gcc's `Ir` UNDERSTATES"* and *"all 34 are word-wise"* both
fall; *"every rung pair is untouched because every hit is a C cell"* stands, and
is narrower than stated — **6 of the 9 patterns are in the published quadrant at
all, and exactly one of those (`p27`) is LICENSED.**

---

## §4. THE CITATION REWRITES — **SURVIVES. Zero wrong functions.** Two `major`s beside them.

**All eight name a symbol that exists, and in every case it is the symbol the
surrounding sentence is actually about.** Both quoted strings are byte-exact.

| # | file | now | verdict |
|---|---|---|---|
| 1 | `patterns/p12-strcat-fixed/inputs/gen.py:30,32` | `check_checksums`, `inputs_of` | VERIFIED |
| 2 | `patterns/p13-strncpy-trunc/inputs/gen.py:30,32` | same | VERIFIED |
| 3 | `patterns/p13-strncpy-trunc/model.py:50,52` | `check_checksums`; `inputs_of` + quote | VERIFIED, quote byte-exact |
| 4 | `patterns/p16-tlv-walk/model.py:19` | `check_marginal_ir` | VERIFIED |
| 5 | `patterns/p16-tlv-walk/model.py:182` | `check_marginal_ir` + `rep.fail("collapse-ir",…)` | VERIFIED, quote byte-exact |
| 6 | `patterns/p35-tagged-union/controls/rust_bug.py:163` | `check_miri` | VERIFIED |
| 7 | `patterns/p38-alias-pun/inputs/gen.py:28` | `inputs_of`, `measure.py::SKIP_INPUT_PREFIX` | VERIFIED |

Resolved: `check_checksums` `:2825`, `inputs_of` `:655`, `check_marginal_ir`
`:3112` (next top-level `def` is `check_identity` `:3719`, so the whole cited
machinery is inside it, including the `work <= 0` guard at `:3433–3438`),
`check_miri` `:9255` (prints `head("8. Miri policy")` at `:9296`, and the argv
at `:9621–9622` matches `rust_bug.py:169–171` item for item),
`measure.py::SKIP_INPUT_PREFIX` `:64`.

✅ **Three were rotten AT BIRTH and the rewrite silently repaired them** — which
is a stronger result than "the line numbers decayed":
* `p16`'s `check.py:625`: at `c623b22` (the commit that created p16) `:625` was
  inside **`check_no_collapse`**, and `check_marginal_ir` was at `:690`. The
  original citation named the wrong *function* from day one.
* `p38`'s `check.py:459-460`: at `51de7e1` those were a blank line and
  `def head(title)`; `inputs_of` was at `:473`. And `measure.py:60` was
  mis-typed for `:64` — that region of `measure.py` **has not moved a line since
  TASK_066**, so it never decayed either.
* Conversely `p35`'s `check.py:8841` was **exactly** the `MIRI_BIN` argv at
  `e7c2e67` and decayed in ~20 tasks. That one citation is the whole evidentiary
  case for the convention.

**Bonus:** all **41** distinct `<module>.py::<symbol>` citations under
`patterns/` were resolved; every one lands on a real `def`/`class`/constant.
**Zero dangling function-name citations tree-wide.**

### 4a. `minor` — the report and the new stage-0c comment miscount the residue

```
$ grep -rn 'check\.py:[0-9]' patterns/ | wc -l
0                                        <- headline CONFIRMED
measure.py: 7   build.py: 3   dloop.py: 3   = 13   <- count CONFIRMED
```

* ⚠ **"13 line citations … across 6 patterns" is 7 patterns**, not 6 — p12, p14,
  p18, p19, p22, p27, p36. Confirmed independently from the 33 gate records'
  `doc_citations.other`. The report's own listing block names all seven; only
  its summary sentence says six. `RECAP.md` queue item 38 repeats "13" without a
  pattern count, so only the report is wrong.
* ⚠ **"exactly TWO are rotten" is ONE.** `build.py:66` **is** mis-aimed (p18
  quotes `ALL_OPTS` and cites the line holding `ALL_CELLS`) — but it was an
  authoring error at `18f7a28`, not decay: `build.py` has not moved.
  `measure.py:238` **is not rotten**: at `05ec7da`, where p27 wrote it, `:238`
  was `def matrix_inputs(indir):`, byte-identical to today, and it is the apt
  landing — `matrix_inputs`' own docstring states, verbatim, the two-hash
  property p27's sentence is describing. The report's proposed `:229` is a
  re-reading, not a decay finding. **This wrong number is now inside
  `harness/check.py:955–966`'s stage-0c comment and inside `RECAP.md` queue
  item 38.**

### 4b. `minor`, and the irony is the point — **stage 0c's own comment mis-dates its own evidence, and two of its five coordinate descriptions are false at the date it names.**

`harness/check.py:944–948` says *"**At TASK_168-time** all EIGHT surviving
citations … pointed at the wrong code (`:1249` a blank line, `:625` a `Report`
method, `:8841` a `MIRI_BIN` argument list, `:469` `#`, `:459` a comment about
row counts)"*. Read out of the two trees:

```
=== at 0678b2d^  ("TASK_168-time") ===        === at a832768^ (pre-TASK_164) ===
  1249 :     code = vparse.blank_noncode(src)   1249 :  (blank)
   625 :         self.blocked.append(...)        625 :      self.blocked.append(...)
  8841 :     for f in blobs:                    8841 :   [MIRI_BIN, "--sysroot", sysroot, ...
   469 : #                                       469 : #
   459 : #   * `0 of 40` p01 rows ...            459 : #   * `0 of 40` p01 rows ...
```

The five descriptions are the manager's, and they are **all correct for
pre-TASK_164** — which is exactly what `.tasks/TASK_168.md:96–99` said, together
with *"⚠ `check.py` grew again, so they are now rotten in a NEW way — do not
'verify' one by reading the current line."* The engineer copied them and
**re-dated them to TASK_168-time**, where two are false. A comment in the stage
built to stop coordinate rot, rotted by four tasks on the way in.

### 4c. `major` — **the surrounding sentences: p13 ships two mutually contradictory statements about the same measurement, one in each of the two files `TASK_168` edited.**

* `patterns/p13-strncpy-trunc/model.py:56`, in the very paragraph the rewrite
  touched: *"under `gcc -O3` the value it reads is not even stable across runs
  (`../NOTES.md` 0)"*. `NOTES.md:77–78` forbids exactly that reading — *"the
  probe's pattern does NOT transfer to the shipped cells. **Do not quote the
  table above as a compiler property.**"* — and `NOTES.md:857` (§7a, shipped
  cells, 60 and 300 runs) records **`c-gcc` (all four): stable | stable | stable
  | stable**. It is `c-clang` that is unstable. The pointer `(../NOTES.md 0)`
  should be §0b.
* `patterns/p13-strncpy-trunc/inputs/gen.py:42–44`, immediately below the
  rewritten hunk: *"3 of `c-clang`'s 4 builds give two different answers"* — the
  **pre-TASK_046** figure. The current tree measures 1 of 4 at 60 runs and 2 of 4
  at 300, and §7a's own conclusion is *"**Quote the mechanism, never the
  counts.**"*

Both are **rung-adjacent doc text in measurement-hashed files**, so fixing them
is a re-measure — which is why they are reported and not fixed, and why they
should be batched with anything else p13 owes.

### 4d. `major` — **the `p35` `rc=-11` contradiction is LIVE IN THE COMMITTED TREE at `HEAD`, in five documents including a `contract_sha256`-hashed `why`.**

The committed `patterns/p35-tagged-union/controls/rust_bug.json` now says:

```
"adversarial-ptr-confusion.bin": { "c_r1": {"rc": -11}, "unsafe_arm": {"rc": -7},
                                   "unsafe_reproduces_c": false }
"adversarial-ptr-deep.bin":      { "c_r1": {"rc": -11}, "unsafe_arm": {"rc": -11},
                                   "unsafe_reproduces_c": true }
"problems": []
```

while the tree still publishes, in five places:

```
patterns/p35-tagged-union/README.md:92        "unsafe arm SIGSEGVs at `rc=-11` exactly as C does"
patterns/p35-tagged-union/NOTES.md:369,370    "| `rc=-11` SIGSEGV | `rc=-11` SIGSEGV |"
patterns/p35-tagged-union/NOTES.md:1027       "the unsafe arm **SIGSEGVs**, `rc=-11`, exactly as C does"
patterns/p35-tagged-union/spec.md:116         "the unsafe arm still SIGSEGVs (`rc=-11`"
patterns/p35-tagged-union/spec.md:264 (`why`, INSIDE the hashed fence)
                                              "the unsafe arm SIGSEGVs on adversarial-ptr-confusion
                                               and adversarial-ptr-deep, rc=-11, exactly as c/kernel.c does"
```

⚠ **The gate is green over this**, because stage 9b checks the sidecar's
*freshness* and `rust_bug.py::main` asserts `unsafe_reproduces_c` only on the
three SILENT inputs. ⚠ **`README.md` is the reader-facing file.** RECAP finding
65(d) and queue item 39 record the *mechanism* (a two-state draw) and mark it
`⊘`; **neither says that the tree currently ships a self-contradiction**, and
`.memory/` says nothing at all. This is not a to-do — it is a live defect in a
committed pattern, and it landed *because of* `TASK_168`'s docstring edit.

---

## §5. WHAT THE MANAGER OVERSTATED — mandatory

### 5a. `blocker`-class for the doc layer — **`.memory/03-measurement.md` still asserts the retracted sentence, un-annotated, at `:502–504`.**

```
.memory/03-measurement.md:502   p01, p05, p16 and p17 call no bulk routine at all. **Only p08's gcc kernels
                        :503   contain a `rep` instruction**, so no previously published `Ir` comparison is
                        :504   contaminated. Re-check this before denominating any future pattern in bytes
                        :505   moved rather than bytes folded.
```

The fold's correction went in at `:439–479`, **sixty-three lines above**, and
says *"`.memory/`'s own *'only `p08`'s gcc kernels contain a `rep`
instruction'* is FALSE at 33"* — quoting the sentence without naming where it is
and without touching it. `CLAUDE.md` calls `.memory/` *"the authoritative layer,
and it supersedes any task report it contradicts"*; a reader who greps
`rep instruction` lands on `:503` and gets the false claim **plus its false
conclusion** with no signal at all.

⚠ This is `PROTOCOL` rule 13 in its sharpest published form — *"item 27's header
asserted the opposite of the body underneath it"* — and rule 9's *"ANNOTATE the
sentence as DISPUTED and name the evidence on both sides. Do not delete, and do
not replace."* **Neither annotate nor replace happened; the sentence was left
standing.**

### 5b. `major` — **`.memory/`, `PROTOCOL` and `05-layout.md` carry the fold with NO `PROVISIONAL` marker, against rule 9's explicit text.**

`RECAP.md` finding 65 opens *"⚠ **UNREVIEWED — ✅ = manager re-derived, ⊘ =
engineer's alone.**"* — good. **None of the three other landing sites carries any
such marker:**

* `.memory/03-measurement.md:439–479` — flat assertion, including
  *"roughly 90% of the term is COUNTER, not code"*.
* `.memory/05-layout.md:485–516` — three costs, flat.
* `.tasks/PROTOCOL.md` rule 6, two new paragraphs — flat, and one of them is now
  a **rule** (*"✅ Budget `re-measure → report.py → gate` per pattern"*).

Rule 9: *"If a finding must be recorded before review, mark it **PROVISIONAL —
not yet reviewed** in the text itself."* The block immediately below the new
`03-measurement.md` text does exactly that for TASK_074's threshold
(*"⚠ **PROVISIONAL — measured at TASK_074, NOT YET REVIEWED**"*), so the
convention is live on the same page and was not applied to the new material.

### 5c. `major` — **the `✅` on *"the magnitude is inflated ~10×"* rests entirely on a `⊘`, and the `⊘` figure is derived the wrong way.**

RECAP finding 65(a) marks `⊘` on *"…costing `+4160.00` at `1.0156 Ir`/byte … On
the vector path the same zeroing prices at **≈426 `Ir`**, so ~90% of the term is
COUNTER, not code"*, then marks **`✅`** on *"the magnitude is inflated ~10×"* —
which **is** the ⊘ sentence, restated. The engineer's own report says so
explicitly: *"I have **not** verified the `≈426 Ir` vector-path counterfactual …
it is derived from `.memory/`'s 0.104 `Ir`/byte."*

⚠⚠ **And `0.104 Ir`/byte is the `memcpy`/`memmove` constant.**
`.memory/03-measurement.md:426–427`: *"`memcpy`/`memmove` stay on the vector path
at **0.104 Ir/byte** up to somewhere between 8 KiB and 16 KiB, `memset` flips at
3 KiB"*. `426 = 0.104 × 4096`. **So the counterfactual applies the `memcpy`
constant to a `memset`-class zeroing — the exact error finding 65(a) exists to
name** (*"Two libc routines, two thresholds, and the manager quoted one at the
other"*), committed one level down and marked `✅`.

✅ **`.memory/` already has the right instrument, and it is FOUR LINES BELOW the
block the fold inserted.** `.memory/03-measurement.md:483–489`, TASK_074:

> Probing a zero-fill cost axis (**`vec![0; n]` against `MaybeUninit`**), rustc
> 1.97.1 `-C opt-level=3`, whole-program `Ir`:
>
> | `n` | 512 | 1024 | **2048** | 4096 | 65536 |
> | (safe − unsafe) / call | 300.97 | 326.30 | **2106.94** | **4154.94** | 65595.01 |

Re-derived:

```
sub-threshold marginal cost of vec![0;n] vs MaybeUninit : 0.04947 Ir/byte
fixed term                                              : 275.64 Ir
vector-path counterfactual at n=4096                    : 478.28 Ir
report's figure (0.104 Ir/byte x 4096, the MEMCPY rate) : 425.98 Ir

p42 measured delta at 4096                              : 4160.00 Ir
.memory/ TASK_074 probe, SAME mechanism, n=4096         : 4154.94 Ir  (+5.06, +0.122%)

  counterfactual  425.98 -> inflation  9.77x -> "89.8% is counter"   [report's 426, memcpy rate]
  counterfactual  478.28 -> inflation  8.70x -> "88.5% is counter"   [.memory/'s own memset probe]
```

**Two consequences, opposite in sign:**

1. ✅ **`+4160.00` is stronger than the manager claimed.** It is corroborated to
   **0.12%** by an independent, four-tasks-older `.memory/` probe of the *same
   mechanism at the same n* — a `✅` that was available and was not taken. The
   ⊘ should be an ✅ for a better reason than the one given.
2. ⚠ **The published `~90%` survives numerically (88.5% vs 89.8%) and its
   derivation does not.** The number in `.memory/` and in the commit message
   should be **≈478**, from the zero-fill probe, not ≈426 from the memcpy rate.

### 5d. `major` — ***"roughly 90% of the term is COUNTER, not code"* is the wrong sentence, and it contradicts the sentence beside it.**

The task asks whether the honest correction is *"divide by ten"* or *"this row
is comparing two different programs"*. **It is neither alone, and the fold picked
the one that is false on its own terms.**

* `safe_naive` spells `vec![0u8; 4096]`; `unsafe` spells `Vec::with_capacity`.
  **One program zeroes 4096 bytes and the other does not.** The work is real,
  it is entirely in one rung, and it is not an artefact of anything.
* What `Ir` gets wrong is the **price**, and only above the crossover: the *same*
  zeroing costs ≈0.05 `Ir`/byte marginal at n ≤ 1024 and ≈1.00 at n = 4096.
  `.memory/`'s own words, three lines under that table: *"**`rep stosb` is what
  the hardware runs BECAUSE it is fast, so `Ir` reports the cost rising 6.5× at
  exactly the size the real cost falls.**"*
* So *"~90% of the term is COUNTER, not code"* **asserts the work is not there**,
  which is false; and the very next sentence in the same `.memory/` block —
  *"✅ The behavioural difference IS real — one rung zeroes and the other does
  not"* — walks it back. **Only the first half reached the commit message and
  RECAP's START HERE box.**
* ✅ The defensible statement: **the difference is real work done by exactly one
  rung, and `Ir` prices it in a regime no other row in that column is in.** The
  number is not inflated *relative to the truth*; it is **non-comparable** with
  the rest of the column.

### 5e. `major` — **queue item 37 is wrong about its own cost, and I checked it the way `TASK_167` checked `QUEUE_TRIAGE.md`.**

Item 37 (and `.memory/05-layout.md`, and finding 65(c)) says: *"A `check.py`
docstring edit cannot move a callgrind number, so **all 33 STALEs are FALSE**.
✅ The repair is `synthesis/`-only … and costs **no sweep and no re-measure**:
pin `derived_from_sha256` over … `measure.py::measurement_sources`."*

Re-derived — 33 of 33 confirmed stale, **and which files cause it**:

```
patterns with a stale gate_source_sha256 pin: 33 of 33

files responsible, and on how many patterns:
    33  harness/check.py
    33  harness/vparse.py
     1  patterns/p12-strcat-fixed/inputs/gen.py
     1  patterns/p13-strncpy-trunc/inputs/gen.py
     1  patterns/p13-strncpy-trunc/model.py
     1  patterns/p16-tlv-walk/model.py
     1  patterns/p35-tagged-union/controls/rust_bug.py
     1  patterns/p38-alias-pun/inputs/gen.py

would the proposed `measurement_sources` pin still be stale?
   movers that ARE in measurement_sources:
     p12/inputs/gen.py, p13/inputs/gen.py, p13/model.py, p16/model.py, p38/inputs/gen.py
   movers that are NOT: harness/check.py, harness/vparse.py, p35/controls/rust_bug.py
```

⚠⚠ **So item 37's repair does NOT make the pin quiet: it would report 4 of 33
STALE the moment it lands** (p12, p13, p16, p38), on files that are in
`measurement_sources` by design. **Item 37's own rationale — *"a pin whose STALE
does not mean 'the numbers are wrong' is a pin that gets switched off"* —
therefore applies to its own replacement**, because those four moves were also
comment-only. The repair is a large improvement (33 → 4) and it is not the
elimination the item claims.

⚠ **What the item must say before it becomes a task:** the re-pin has to be
performed at emit time, or those four patterns must be re-emitted, or the
re-pinner has to *assert* freshness it cannot check for four patterns. Any of the
three is fine; none is "costs no sweep and no re-measure, done".

✅ **The *placement* half of the item is verified correct:** `synthesis/*.py` is
in neither digest — `check.py:9985–9995`'s `srcs` glob covers
`harness/*.py`, `common/*.py`, `common/layout/*.py`, `verus_run.py`, the
pattern's own files; `measure.py:224–235`'s `measurement_sources` covers the
pattern's sources plus `build.py`/`asm.py`/`measure.py`/`verus_run.py`/`common`.
**Neither reaches `synthesis/`.**

⚠ `.memory/05-layout.md`'s headline *"ANY `harness/*.py` edit stales the whole
sidecar"* is narrower than the mechanism: the pin covers the **gate digest**,
which also includes `patterns/*/*.md`, `common/*.py`, `verus_run.py` and
`patterns/*/controls/*` — as its own quoted 9b docstring says two lines below.
Empirically only `check.py`+`vparse.py` moved this time, so the headline
described this instance and not the rule.

### 5f. `minor` — the `✅` on *"three lines above"* and the quoted range

The commit message and `.memory/03-measurement.md:444` say *"`memset` flips at
**2–4 KiB** — which this very entry says **three lines above**"*. What
`:427` actually says is **`memset` flips at 3 KiB** (a single value), **two**
lines above `:429`'s 8192 figure. The **2000–4000** range comes from the
*"`memset` CROSSES TO `rep stosb`"* section at `:2708–2711`, ~2280 lines below.
The engineer's report said *"2–3 KiB"*; the manager widened it to *"2–4 KiB"*
without saying so. The substance is right (4096 > 4000, both sources agree it is
byte-wise); the `✅` on *"states it three lines above"* describes a sentence that
says something narrower.

### 5g. `minor` — `RECAP.md` disagrees with itself on the `undeclared` count

The START HERE box, rewritten at `0678b2d`, says *"`results/SYNTHESIS.md` §7
publishes the count: **14 of 33** print `undeclared`"* — **correct**, verified
(`results/SYNTHESIS.md:532`, `:1481`; 14 rows in `synthesis.md` §2's R2−R4
table). But `RECAP.md`'s `.temp/mgr164` paragraph, four lines up and untouched by
the fold, still says *"§7 says '14 of 26 print `undeclared`'; **it is 21 of 33**
and at least `p34` is WRONG"* — a pre-TASK_166 statement the box now contradicts.
`.tasks/TASK_169.md` scopes queue item 35 as *"auditing the **14** `undeclared`
rows"*, which is the right number; the stale `21` is what a reader arriving at
the mgr164 paragraph gets. Rule 13 again.

---

## §6. THE TWO OVERRUNS AND THE PREDICTION — **SURVIVES, NARROWED ×3**

### 6a. The re-measure→table→re-gate chain: mechanism **CONFIRMED**; the render count is **6, not 5**.

Mechanism, read from source: `check_table_render` (`harness/check.py:8625`)
loads `results/pNN-<slug>.json` via `report.py::load`, re-renders, and on
mismatch calls **`rep.fail("tables", …STALE IN ITS CONTENT…")` — a hard fail,
not a shout.** Confirmed live in `.temp/t168/sweep/p35_regate.log`.
`git show 0678b2d --stat` lists exactly four moved tables (p12/p13/p16/p38, 36 /
36 / 45 / 55 lines); `results/tables/p35-tagged-union.md` is **absent** from the
stat, so the report's *"ends byte-identical"* is true.

⚠ **The artefacts price it at six renders and six gate runs, not five and six.**
`.temp/t168/` holds **six** `report_*.log` (p12, p13, p16, p35 at `09:56:19`,
p38, **and `report_p35b` at `10:05:39`**) and **six** regate logs
(`p12 p13 p16 p38 p35 p35_regate2`). The sixth render is a *wasted* one: p35's
real loop was **fix → report → gate (rc=1) → report → gate (PASS)**, not the
*"fix → gate → report → gate"* the report's §P1 describes, because the first
render ran against a gate record still carrying the stale sidecar verdicts.
⚠ `.temp/t168/regate_rc.txt` records **5** rcs for **6** gate runs.
**So `.memory/05-layout.md`'s and `PROTOCOL` rule 6's `+5 renders` should read
`+6`** — and the extra one *strengthens* the cost argument.

⚠ `minor`: `PROTOCOL` rule 6's new paragraph attributes the whole `+5/+6` to
re-measured patterns, but `p35` was **not** re-measured — its cost came from a
`controls/*.json` move. A reader budgeting from the rule's general form gets
4 renders / 4 gates.

### 6b. `p35`'s three sidecars: **the general form is TRUE and can be stated STRONGER — with one correction and one important narrowing.**

Over all **46** `patterns/*/controls/*.json`:

```
sidecars pinning their OWN GENERATOR:  46/46
sidecars pinning ANY harness/ file:     3/46
    p23/controls/sweep_fit.json     -> asm.py, build.py, measure.py
    p35/controls/proof_mutants.json -> check.py
    p35/controls/union_oracle.json  -> check.py, vparse.py
```

* ⚠ **Correction to the spelling:** `.memory/05-layout.md` says *"a
  `controls/*.py` edit"*. **45 of 46 generators are `.py`; `p23`'s
  `controls_pin.json` is emitted by `controls/run.sh` and pins that.** The
  invariant is *"its own generator"*, not *"its own `.py`"*.
* ⚠⚠ **The narrowing that matters: this is a property of each GENERATOR, not of
  the GATE.** Stage 9b (`harness/check.py:9142`) re-hashes **whatever paths it
  finds** in `derived_from_sha256` and enforces nothing about which paths must be
  there; the absent-pin branch only `rep.shout`s. Each generator hand-writes its
  own list. **So the sentence should read *"46 of 46 do, and nothing makes
  them"*** — as landed it reads as a law, and a new generator that omits its own
  hash would print `FRESH` forever with no stage objecting.
* ✅ p35's arithmetic is exactly right: 2 harness-pinning sidecars + `rust_bug`
  = **3**, and the commit stat corroborates all four p35 files.

### 6c. The prediction lesson: **SURVIVES** on 3(a)/3(b), **NARROWED** on the bigger question, plus one **new** finding.

* ✅ `harness/measure.py:429–430`: `--reps` default **30**, `--cpu` default **3**;
  recorded at `:464` as `timing_cpu` and interpolated into `protocol.wall` at
  `:469`. ✅ The commit diff shows `"reps": 31 → 30` on p12/p13 and
  `"timing_cpu": 5 → 3` plus the `protocol.wall` string on p16.
* ⚠ **YES — four published records are STILL at non-default values today**, read
  as JSON out of all 33 measurement records:

  ```
  timing_cpu distribution: {3: 31, 5: 2}
  reps-set distribution:   {(30,): 30, (31,): 3}

  p04-ring-buffer     cpu=3  reps=31
  p05-index-flatten   cpu=5  reps=31     <- both non-default
  p11-nul-scan        cpu=3  reps=31
  p14-field-split     cpu=5  reps=30
  ```

  **But the rule is NOT bigger than a prediction lesson, and the reason is
  already published.** `.memory/03-measurement.md:1315–1320` specifies the
  protocol as *"pin to a single core with `taskset -c N`; use the same core for a
  whole comparison set; record which"* and *"≥30 reps"* — it pins **neither a
  core number nor a rep count**, so `cpu 5 / reps 31` is *in* protocol. Each
  table self-discloses (`results/tables/p05-index-flatten.md:137`). And
  `--reps`/`--cpu` feed only `wall(...)` (`measure.py:402`); `callgrind_ir(...)`
  (`:375`) takes neither, so **no `Ir` is affected**. Decisively,
  `results/synthesis.md:56` already says *"**There is no wall-clock column here
  at all**: this box's `ns` floor is a session property, so cross-pattern timing
  … is not a measurement."* **No published cross-pattern claim rests on a wall
  number.** ✅ **Clean negative on the escalation.**
* ⚠ **The real residue is narrower and unpriced:** nothing in the tree records
  whether any of those four choices was deliberate, and **no gate stage reads
  `reps` or `timing_cpu` at all**. Any future re-measure of p04/p05/p11/p14 will
  silently retire them exactly as `TASK_168` retired p12/p13/p16 — and nothing
  will notice.
* ⚠⚠ **NEW — `PROTOCOL` rule 6's lesson names the two visible arguments and
  misses three INVISIBLE ones, which are strictly worse.** `measure.py`'s full
  argparse list against the record's keys:

  | argument | default | recorded? | effect |
  |---|---|---|---|
  | `--reps` | 30 | **yes** | the `TASK_168` case |
  | `--cpu` | 3 | **yes** | the `TASK_168` case |
  | `--no-callgrind` | off | ⚠ **NO** | omits every `ir` leaf |
  | `--no-wall` | off | ⚠ **NO** | omits every wall leaf |
  | `--cells {all,measured}` | `all` | ⚠ **NO** | drops the control cells |

  `reps`/`timing_cpu` are the *benign* case precisely because they leave a trace —
  which is how `TASK_168` diagnosed them after the fact. The other three **delete
  data and record nothing**, so such a record is indistinguishable from a full one
  minus the missing rows. ✅ **No shipped record was taken with any of the three**
  — all 33 are `32 rows / 8 cells / 32 with-ir / 16 with-wall`, except
  `p01-array-sum` at `28 / 7`, correct because p01 ships no `kernel_hardened.c`.
  **The hazard is unpriced, not realised.**
* ✅ **The prediction was genuinely ex ante.** `.temp/t168/PREDICTION.md` mtime
  `07:44:02`; p12's own record `generated_utc = 2026-09-02T07:44:40Z` — **38 s
  later** — and the first measure log at `07:47:19`. Its wall row states *"`reps`
  stays 31"*, which is precisely the half that was wrong: **self-falsifying in the
  right direction.** The report's table reproduces `PREDICTION_OUTCOME.md`
  faithfully; two rows are merged for width with identical values.
* ⚠ Noticed while reading all 33 records, out of scope: **five lack
  `source_sha256` AND `input_sha256` entirely** — `p02`, `p05`, `p07`, `p11`,
  `p17`, all `generated_utc ≤ 2026-08-19`, predating TASK_035's provenance
  block. `measure.py --check-stale` cannot date any of them, yet reports
  `66 record(s) examined, 0 STALE`.

---

## DELIVERABLE 2 — the verdict on `p42`'s `+4160.00`

**Do not retract it, do not "divide it by ten", and do not move it out of the
band. Mark it as regime-crossing, in the file's own existing idiom.**

The number appears in exactly **one** place —
`results/synthesis.md:345`, and `grep '29252\|4160\.00' results/` returns that
line and nothing else. **`results/SYNTHESIS.md` does not quote it**; its ten p42
mentions are all about the affine-token Result. So the repair is one generated
line.

1. **`+4160.00` stands.** Independently corroborated to **0.12%** by
   `.memory/03-measurement.md:483–489`'s TASK_074 zero-fill probe at the same
   `n`. Retracting a correctly measured `Ir` delta would be wrong.
2. **The `≥ 16.00` band's legend is not wrong either.** *"every one is real"* is
   a claim about **noise**, and `+4160.00` is not noise. **The row does not need
   demoting.**
3. **What is missing is a comparability marker, and `results/synthesis.md`
   already has the idiom for exactly this.** It ships `†` (*"at or below its own
   pattern's `R5 − R4` null"*) and `‡` (*"a phase of the environment block rather
   than a property of the code"*). **Add a third**, e.g.:

   > **`§` marks a correction that crosses a libc bulk-routine threshold.** The
   > work is real and belongs to one rung, but `Ir` prices it at ≈1.00/byte above
   > the crossover and ≈0.05/byte below, so the magnitude is **regime-dependent
   > and not comparable with any sub-threshold row in this column**. See
   > `.memory/03-measurement.md`'s zero-fill probe: 326.30 `Ir` at n = 1024,
   > 2106.94 at n = 2048.

   and mark **p42 `large` only**. `TASK_168` checked all **614** callee edges and
   found exactly one asymmetric crossing; p08's is symmetric and cancels.
4. **What must NOT be written is *"~90% is counter artefact, not code"*.** One
   rung zeroes 4096 bytes and the other does not. Say *"real work, in one rung,
   priced in a regime nothing else in this column is in"*.
5. **Cost: zero gate runs, zero re-measures.** `synthesis/*.py` is in neither
   digest (verified above), so it is a `synthesize.py` edit plus one
   regeneration of `results/synthesis.md`. ⚠ **Do it in the same pass as queue
   item 37**, since both are `synthesis/`-only and both touch the file's
   staleness prose.

---

## DELIVERABLE 4 — is the GATE finished?

**No — and not because a stage is missing.** Three answers:

1. ✅ **No stage has an arm that could not fire.** All twelve new arms were driven
   and eleven were broken by a regression that the arm caught. `0c` and `0d` sit
   above `fixture.ensure()` and fire on a fixture-less run. `0d` reads
   `build.py` live and tokenises it; it is not a second copy.
2. ⚠ **One arm is under-armed and one guard is missing** — `_CITE_RE`'s `\b` is
   invisible to all six 0c arms (§1b), and `0c`/`0d` are the only arm sets in
   `check.py` with no `RAISED` wrapper, so a throw is an import-time traceback
   with no gate record for any pattern (§1c).
3. ⚠⚠ **The gate states a convention it enforces on one thirteenth of it.**
   `harness_module_names()` derives **13** harness modules; `CITE_FATAL_MODULE`
   is **one** of them, and the other 12 are reported. That is a defensible
   staging — but combined with the `patterns/`-only scope, the convention *"name
   the FUNCTION and give NO LINE NUMBER"* is enforced over
   **`check.py` ∩ `patterns/`** and stated everywhere. Outside that intersection
   the tree currently carries **6 in `RECAP.md`** (≥4 rotten), **6 in
   `.memory/`**, **1 in a PUBLISHED `results/synthesis.md`**, **2 in the
   generator that emits it**, and **13 non-`check.py` line citations under
   `patterns/`** (1 rotten). ✅ **The instrument for the repo-wide half already
   exists and needs ~40 lines: `harness/tools/temp_citations.py` — repo-wide,
   out of both digests, with a curated baseline for the three `.memory/`
   quotations that must keep their colons.** Queue item 38 proposes widening
   `0c`'s *regex*; the bigger and cheaper win is widening its *scope*, and it
   cannot be done inside `0c` without an escape hatch.

---

## CLEAN NEGATIVES — twenty-one, named, none from `TASK_166` or `TASK_167`

1. **Stage `0c`/`0d` placement does not fail open.** `fixture.ensure() → False`
   with the arms planted broken raises `doc-citation-selftest`,
   `codegen-cfg-selftest` **and** `fixture`. A fixture-less run cannot look green.
2. **`0c` reads `.md`, `.py`, `.json` and `.sh` alike** — 659 files across 33
   patterns, walk time `0.00 s`, no file above 2 MB. The `.md` case the task
   asked about is covered by construction, not by a whitelist.
3. **`0c` catches the em-dash range `check.py:1249–1278`** as well as the ASCII
   one. No arm covers it; it works.
4. **The six prose spellings `0c` misses are unrealised.** `` `check.py` line N ``,
   `check.py, line N`, a Python traceback, `#L`, `:L`, `check.py: N` — **0 hits
   under `patterns/`**, and the only occurrence in the whole tracked tree is
   `.tasks/TASK_169.md:48`, the task file's own example.
5. **`0d` is not a cross-check against a second hand-maintained list.** It opens
   `buildmod.__file__` and tokenises the live file; `CODEGEN_CFGS` is only the
   allowed set. All 33 records agree: `build_py_cfgs = ['slb_isolated']`,
   `unresolved = 0`, verdict `OK`.
6. **The `--cfg` grep really would get it wrong.** Arm D4 fires under a
   `re.findall(r"--cfg[= ]+…")` replacement, on `build.py`'s own comment. The
   tokeniser earns its place.
7. **`build_cfg_flags` degrades safely on a non-literal.** Pointed at
   `harness/limbs.py` (a live second `--cfg` producer) it returns `([], 1)` — one
   `unresolved`, shouted, never dropped.
8. **`slb_twin`'s absence from `CODEGEN_CFGS` is correct, not a hole.**
   `build.py` never passes it; `limbs.py` passes it only to a verify-only Verus
   run, so blanking `#[cfg(slb_twin)]` in the idiom audit is right and is
   documented (TASK_069).
9. **All 33 gate records carry the new keys.** `doc_citations` 33/33,
   `codegen_cfgs` 33/33, `fatal` total **0**, `other` total **13**,
   `harness_modules` length **13** on every one.
10. **`blank_noncode` holds under the widened `global` anchor.** A `global` in a
    raw string, a nested-hash raw string (`r##"…"##`), a byte string, a `//`
    comment after a `}`, and a `/* … */` block comment **all score `[]` under
    both matchers**.
11. **A `global` split across lines was never the issue.** `global\n align_of`,
    `global size_of\n usize` and `global layout\n S` are all classified
    identically by both matchers — the anchor is about the *preceding* character.
12. **The `vparse` widening moves nothing shipped, at a WIDER denominator than
    claimed.** 0 of **161** tracked `.rs` (not 152), and the census of 10
    (`global size_of` ×7, `global layout` ×3) reproduces `.memory/`'s TASK_164
    figure exactly.
13. **The four closing checks re-run green, each read from its own `rc`:**
    `composition.py --check` `rc=0` (*"33 patterns, 10 classes"*),
    `temp_citations.py` `rc=0` (*"new=0 unclassified=0 resolved=4"*),
    `measure.py --check-stale` `rc=0` (*"66 record(s) examined, 0 STALE"*), and
    `PROTOCOL` rule 10's dangling-citation loop reports only the three documented
    `TASK_NNN*` placeholders plus this report, which now exists.
14. **All 41 `<module>.py::<symbol>` citations under `patterns/` resolve** to a
    real `def`, `class` or module constant. The convention the rewrites moved to
    has **zero** dangling instances tree-wide.
15. **`rep_scan.py`'s *"0 not built"* is literally true.** Over all **1052**
    windows: 0 missing binaries, 0 `symbol is None`, 0 empty windows, 0 missing
    `nm --print-size` extents. The count is not hiding skipped cells.
16. **The `rep` census reproduces byte-for-byte on a re-run** — 26 windows,
    1052 scanned, nine patterns `{p06 p08 p14 p23 p27 p29 p32 p35 p46}`,
    `{'rep stos': 32, 'rep movsq': 2}`, 34 instructions in 26 windows (14 carry
    two). The **26/34 arithmetic checks out.**
17. **`+4160.00` is corroborated by a second, independent, four-tasks-older
    instrument** — `.memory/03-measurement.md:483–489`'s `vec![0;n]`-vs-
    `MaybeUninit` probe reads **4154.94** at the same `n`, `+0.12%`.
18. **The re-measure prediction was genuinely ex ante.**
    `.temp/t168/PREDICTION.md` mtime `07:44:02`; p12's own record
    `generated_utc = 07:44:40Z` — 38 s later. Its wall row states *"`reps` stays
    31"*, which is exactly the half that was wrong: **self-falsifying in the
    right direction**, and the report reproduces `PREDICTION_OUTCOME.md`
    faithfully.
19. **The `reps`/`cpu` escalation does not land.** `--reps`/`--cpu` feed only
    `wall(...)` (`measure.py:402`); `callgrind_ir(...)` (`:375`) takes neither,
    `.memory/03-measurement.md:1315–1320` pins neither value, each table
    self-discloses its protocol line, and `results/synthesis.md:56` publishes
    **no wall-clock column at all**. **No cross-pattern claim is affected.**
20. **No shipped record was taken with `--no-callgrind`, `--no-wall` or
    `--cells measured`.** All 33 are `32 rows / 8 cells / 32 with-ir / 16
    with-wall`, except `p01-array-sum` at `28 / 7` — correct, because p01 ships
    no `kernel_hardened.c`. The hazard is unpriced, not realised.
21. **`46 of 46` `controls/*.json` pin their own generator**, so `p35`'s three
    sidecars are the rule and not an exception; and `3 of 46` pin a `harness/`
    file, reproducing `.memory/05-layout.md:468`'s published census exactly.

---

## Problems

Ranked. `file:line` and the failure scenario are in the sections above.

| # | severity | finding | § |
|---|---|---|---|
| 0a | **blocker** | ***"all 34 instructions are the WORD-wise form (`rep stos %rax`, ≈0.126 `Ir`/byte)"* is FALSE on 18 of 34** — 16 are `rep stos %eax` (0.25 `Ir`/byte, double) and 2 are `rep movsq`. It is in `.memory/03-measurement.md:468–471`, in the commit message, and in `RECAP` 65(b) marked **`✅` manager-re-derived**. ✅ True of the *published* `-O3 isolated` quadrant (12 windows, all `%rax`); false as stated. | 3d(ii) |
| 0b | **blocker** | **The old conclusion *"so no previously published `Ir` comparison is contaminated"* FALLS on a LICENSED row.** `p27 gcc-clang` (published, `−25.02 / −201.73`, **LICENSED**) carries gcc's 32-`Ir` `rep stos %rax` against clang's 19-`Ir` vector spelling — **over half its magnitude**. Nobody quantified this; the report says so in *Unsure* and the fold marked the direction `✅`. | 3e |
| 0c | **blocker** | ***"gcc's `Ir` UNDERSTATES its work … on nine patterns instead of one"* FALLS.** p08's direction needs a transfer over `__x86_rep_stosb_threshold` (2048); it zeroes **4096**, the other five zero **128–768**, where clang's counterpart is inline vector stores at 0.066 `Ir`/byte and gcc's 0.125–0.25 is **dearer**. p08 is still the only pattern the direction holds on. | 3e |
| 1 | **major** | `.memory/03-measurement.md:502–504` still asserts the retracted *"Only p08's gcc kernels contain a `rep` instruction, so no previously published `Ir` comparison is contaminated"*, un-annotated, 63 lines below its own correction. `PROTOCOL` rule 9 requires DISPUTED, rule 13 names the shape. | 5a |
| 2 | **major** | `p35` ships a live self-contradiction at `HEAD`: `controls/rust_bug.json` says `rc=-7 / unsafe_reproduces_c=false` on `adversarial-ptr-confusion`; `README.md:92`, `NOTES.md:369/370/1027`, `spec.md:116` and `spec.md`'s **hashed `why`** all say `rc=-11`, *"exactly as C does"*. Gate green — 9b checks freshness, `rust_bug.py` asserts only on the silent inputs. | 4d |
| 3 | **major** | The `✅` on *"the magnitude is inflated ~10×"* rests on a `⊘`, and the `⊘`'s `≈426 Ir` applies the **`memcpy`** vector constant (`0.104 Ir`/byte) to a **`memset`** — the exact error finding 65(a) exists to name. `.memory/`'s own zero-fill probe, 4 lines below the insertion, gives **≈478** and corroborates `+4160.00` to 0.12%. | 5c |
| 4 | **major** | *"roughly 90% of the term is COUNTER, not code"* asserts the work is absent. One rung zeroes 4096 bytes and the other does not; what `Ir` mis-prices is the **regime**. The correcting sentence beside it did not reach the commit message or the START HERE box. | 5d |
| 5 | **major** | Queue item 37's *"costs no sweep and no re-measure"* is wrong: the proposed `measurement_sources` pin **still reports 4 of 33 STALE** (p12, p13, p16, p38), on files that are in it by design. Verify before it becomes a task. | 5e |
| 6 | **major** | `.memory/`, `.memory/05-layout.md` and `PROTOCOL` rule 6 carry the fold with **no `PROVISIONAL` marker**, against rule 9's explicit text — while the block directly below the new `03-measurement.md` text uses that marker for TASK_074. | 5b |
| 7 | **major** | The `patterns/`-only scope leaves **`RECAP.md` with six** (≥4 rotten) and a **PUBLISHED `results/synthesis.md:224`** carrying `check.py:3303`, emitted by `synthesize.py:1400` — a coordinate `.memory/03-measurement.md:3355` already records as rotted and repaired **in its own copy only**. Artefact-vs-generator skew, on the citation-rot class itself. | 1e |
| 8 | **major** | `vparse.py:872–876`'s direction argument is false in both halves: the enumerated shapes are not *"every shape a local named `global` can appear in"* (six more are admitted), and a false positive **neither shouts nor fails** — it silently moves a **published** column (`synthesize.py:1835`). The new `_selftest` negative was written from the comment's list, not from the language. | 2c |
| 9 | **major** | `p13` ships two mutually contradictory statements about the same measurement, one in each of the two files `TASK_168` edited (`model.py:56` vs `NOTES.md:77/857`; `inputs/gen.py:42–44` vs `NOTES.md:858`). Both are in measurement-hashed files. | 4c |
| 10 | **major** | `0c`/`0d`'s arms are the only ones in `check.py` with no `RAISED` guard: a throw is an import-time traceback with **no `results/gate/*.json` for any pattern**, which is `check.py:9836–9840`'s own recorded lesson. | 1c |
| 11 | **minor** | `+5 renders` should be `+6` in `.memory/05-layout.md` and `PROTOCOL` rule 6; the sixth is `report_p35b` at `10:05:39`, a render wasted against a stale gate record. And rule 6 attributes p35's cost to a re-measure it did not have. | 6a |
| 12 | **minor** | *"exactly TWO are rotten"* is **ONE** (`measure.py:238` resolves correctly to `def matrix_inputs`, unmoved since `05ec7da`), and *"across 6 patterns"* is **7**. Both wrong numbers are now inside `check.py:955–966` and `RECAP.md` queue item 38. | 4a |
| 13 | **minor** | Stage `0c`'s own comment (`check.py:944–948`) mis-dates its evidence to *"TASK_168-time"*; two of its five coordinate descriptions are false at that date and correct only pre-`TASK_164`. | 4b |
| 14 | **minor** | `_CITE_RE`'s `\b` is invisible to all six `0c` arms; `12check.py:5` is the case that distinguishes it, and no arm carries it. Arm C6's label describes a property the regex has for a different reason. | 1b |
| 15 | **minor** | `0 of 152` should be `0 of 161`; `harness/vparse.py:857`, inside the comment block the same commit rewrote, says **161**. `RECAP.md:6112` carries the 152. | 2b |
| 16 | **minor** | `.memory/05-layout.md`'s *"a `controls/*.py` edit"* is 45 of 46 (p23's generator is `run.sh`), and *"a sidecar pins its own generator"* is a **generator** convention, not gate-enforced — 9b hashes whatever it is handed and only shouts on an absent pin. | 6b |
| 17 | **minor** | `PROTOCOL` rule 6's prediction lesson names the two argparse arguments that **are** record fields and misses three that are not — `--no-callgrind`, `--no-wall`, `--cells` — which delete data and record nothing. Unrealised across all 33. | 6c |
| 18 | **minor** | Four published records are still at non-default `reps`/`cpu` (p04, p05, p11, p14); nothing marks them deliberate and no gate stage reads either field. The escalation does **not** land — no cross-pattern claim uses wall clock. | 6c |
| 19 | **minor** | *"three lines above"* / *"2–4 KiB"*: `:427` says **3 KiB**, two lines above; 2000–4000 comes from `:2711`. The engineer wrote 2–3 KiB. | 5f |
| 20 | **minor** | `RECAP.md`'s START HERE box says **14 of 33** `undeclared` (correct); its mgr164 paragraph four lines up still says *"it is **21 of 33**"* (pre-TASK_166). | 5g |
| 21 | **minor** | `0d`'s scope is `build.py`, not *"every `--cfg` the harness passes"* — `harness/limbs.py:208` is a second producer — and its `ok` line reads as if all 18 `CODEGEN_CFGS` names were cross-checked when one is. | 1f |
| 22 | **minor** | Five measurement records lack `source_sha256` and `input_sha256` entirely (`p02 p05 p07 p11 p17`, all pre-2026-08-19); `--check-stale` cannot date them yet prints `0 STALE`. Out of `TASK_168`'s scope; noted. | 6c |
| 23 | **major**, out of scope | **`asm.py::find_symbol(needle="main", pick="largest")` mis-resolves 31 of 33 committed measurement records** — the `verus` cell at `-O0 whole` records `core::slice::sort::stable::driftsort_main<…addr2line…gimli…>` because the mangled name *contains* `main` and is 4 instructions larger than the crate's real `main`. It is **rendered** into `results/tables/pNN-*.md`'s `O0/whole` block. ✅ `-O3 isolated`, the only published level, is unaffected (526/526 correct). **Predates `TASK_168`.** | 3f |
| 24 | **minor** | `.memory/03-measurement.md:452–453`, `RECAP` 65(a) and the commit message say `+4160.00` is measured against ***`unsafe`'s `with_capacity`***. `unsafe.rs:106–108` uses `std::alloc::alloc`; `safe_tuned.rs:46` is the `with_capacity` rung. Both lower to `__rust_alloc`, so no number moves. | 3a |
| 25 | **minor** | The report's *"on `small.bin` the term is +189.01"* is neither figure: the alloc-edge delta is **134.01** and the published parenthetical is **+153.00** (it also picks up a dealloc difference, 106.00 vs 87.00). `189.01` is `alloc_zeroed`'s absolute cost. | 3a |
| 26 | **minor** | The report's *"`memset(scr,0,4096)` runs … in **all eight cells**"* is false — the `0x189480` edge is in **six**, absent from `c-gcc`/`c-gcc-h` where gcc inlines it. The rung-pair conclusion survives; the sentence papers over the gcc/clang asymmetry that *is* the finding. | 3e |
| 27 | **minor** | *"inflated ~10×"* sits at the **bottom** of an 8.7×–14.5× bracket once the counterfactual is anchored on a `memset` rather than a `memcpy`, and the `≈426` figure itself should not be in `.memory/` or the commit message. The `~90%` headline survives (88.5–93.1%) and is conservative. | 3b |
| 28 | **minor** | The `rep` census is a **floor**, not a census of executed kernel code: `-O3 whole` gcc partial inlining leaves `<kernel.part.0>` (p08 ×2) and `<kernel>` (p46 ×2) outside the scanned `main`, +6 instructions. Pattern set unchanged; scoping to the counted window is correct for `kernel_exclusive_ir`. | 3d |

---

## Unsure / not done

* **I did not run a sweep, a re-measure, or `outward_ir.py --emit`**, and none
  was needed. Every claim above came from a pure function driven in process, a
  committed record read as JSON, a committed source, or `git show`.
* **I re-ran the 26-of-1052 `rep` census myself** from an unmodified copy
  (`.temp/t169/rep_scan_copy.py`, `rc=0`, output `.temp/t169/itemA/`) and
  verified the `%eax`/`%rax`/`movsq` histogram directly. The **window census**
  (per-window instruction counts, the Rust positive control, the
  `kernel.part.0` gap) and the **p27 clang-side 19-`Ir` counterfactual** are from
  the delegated re-derivation, `.temp/t169/itemA/window_census.{py,json}`; I
  verified the p27/p08/p14/p29/p35/p46 licence-and-magnitude column against
  `results/synthesis.md:492–527` myself.
* **The `Ir` cost of each `rep` window is now bounded but not fully priced.**
  The `%rcx` immediate gives an upper bound per call (512 / 96 / 32 / 32 / 16 /
  16 `Ir`); what has **not** been done is the corresponding clang-side figure for
  the five patterns other than `p27`, so the *net* `gcc-clang` contamination is
  quantified on p27 and p08 only.
* **The `≈286` and `≈478` counterfactuals disagree by 1.7×** and I did not run a
  `GLIBC_TUNABLES=glibc.cpu.x86_rep_stosb_threshold` control to settle which is
  right. Both are below 426, so the direction of the correction is not in doubt;
  the exact fraction (88.5% vs 93.1%) is.
* **I did not check whether `p35`'s two-state signal draw is machine-specific**
  or whether it moves under ASLR settings; §4d reports the contradiction, not its
  cause.
* **`.temp/build/` (2.4 GB) is left in place**, as `TASK_168` disclosed —
  removing it would cost the next `outward_ir` re-emit a full rebuild.
* **No tracked file was modified. `git status` is clean.** No `git add`, no
  `git commit`.

## Memory updates

**None written — `.memory/` is the manager's, and a reviewer does not fix.**
The corrections this report asks for, in priority order, are Problems 0a–10
above. The four that should not wait for a task file:

* **0a / 0c** — two `✅`-marked sentences in `.memory/03-measurement.md:468–471`
  and in `RECAP` 65(b) are false as stated (`%eax`, and the direction claim).
* **0b** — `p27 gcc-clang` is a **LICENSED published row** with over half its
  magnitude in a `rep`-vs-vector spelling; the old *"nothing published is
  contaminated"* conclusion has to go.
* **#1** — a retracted sentence still standing un-annotated in the authoritative
  layer (`03-measurement.md:502–504`).
* **#2** — a live self-contradiction in a shipped pattern's `README.md` and its
  `contract_sha256`-hashed `why` (`p35`, `rc=-11` vs `rc=-7`).

**PROTOCOL rule 2 running count: launched from 948.** This review refutes the
manager on: *"all 34 instructions are the WORD-wise form"* (`✅`);
*"gcc's `Ir` UNDERSTATES its work on nine patterns"* (`✅`);
*"no previously published `Ir` comparison is contaminated"* / the `widen`
framing; *"the vector path prices it at ≈426 `Ir`"*; *"`unsafe`'s
`with_capacity`"*; *"`.memory/`'s six are what is left"* (RECAP.md has six,
`results/synthesis.md` publishes one, `synthesize.py` emits it); *"exactly TWO
[of the 13] are rotten"* and *"across 6 patterns"*; *"+5 renders"*;
*"a `controls/*.py` edit"* (45 of 46) and *"a sidecar pins its own generator"*
stated as a law rather than a census; *"0 of 152 shipped `.rs`"* (161);
`vparse.py`'s *"every shape a local named `global` can appear in"* and its
*"a false POSITIVE shouts"*; and **queue item 37's *"costs no sweep and no
re-measure"***. ⚠ **Reconciliation is the manager's job, not mine.**
