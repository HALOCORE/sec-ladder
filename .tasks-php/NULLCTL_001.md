# NULLCTL_001 — the R4/R5 null control's premise, checked per row for the first time

> ⛔⛔⛔ **WHY THIS FILE IS COMMITTED, AND IT IS NOT TIDINESS.** It was written as
> `.temp/mgr172/NOTES.md`, which is **gitignored and auto-`rm`-able**, and it is
> the evidence record cited by **five published findings — `F82`, `F83`, `F84`,
> `F85`, `F86`** — from **seven** citations in `RECAP_PHP.md` and
> `.memory-php/02-ladder.md`.
> ⛔⛔ **THIS LINE SAID *"six … F82–F87"* WHEN THE FILE WAS WRITTEN, AND `F87` IS
> EVIDENCED BY NONE OF THE SIX PROBES.** Its tokens `get_unchecked` /
> `a1_spread_pp` appear in zero of them, and F87's own section cites
> `TASK_PHP_037` and `results-php/gate/ph45-….json` — **all committed, so its
> law-11 debt was discharged before the promotion began.** ▶ I read the range off
> `.memory-php/02-ladder.md:612`'s citation line and **took a RANGE for a
> MEMBERSHIP**; the census in `F147` had already printed the correct set.
> Caught by the promotion engineer. See `F147`(c′).
> `.memory-php/04-process.md` **law 11**: *a
> published finding whose only evidence is a gitignored probe is a finding that
> will not survive a clean checkout.* Promoted **2026-09-17** under `F147`.
>
> ✅ **THE FIVE PROBES IT CITES WERE PROMOTED IN THE SAME PASS** and are now
> `.tasks-php/probes/{identity_null,inclusive_ir,bc_sweep,flip_exact,null_control}.py`
> plus `probes/sweep_cg.sh`, all registered in `.tasks-php/checkers.py`.
> ⚠⚠ **Two of them CRASHED rather than degraded when their callgrind cache was
> absent** — `inclusive_ir.py` with a `TypeError`, `bc_sweep.py` with a
> `KeyError` — which is law 11's prediction tested for the first time, **with a
> mechanism**. Guarded on promotion; see `F147`(f).
>
> ⚠ **WHAT IT STILL DEPENDS ON THAT IS NOT COMMITTED, stated rather than
> discovered:** the cached callgrind profiles under `.temp/mgr172/cg/`. Those
> are **re-derivable artefacts with a committed generator**
> (`probes/sweep_cg.sh`, `inclusive_ir.py --regen`), which is `CLAUDE.md`
> Don't #1 being **followed**, not broken. ▶ **Do not commit them.**
>
> ⚠⚠ **TWO SECTIONS OF THIS FILE ARE PUBLISHED NOWHERE ELSE, and they are why
> the whole document was kept rather than just the probes:** **§8**, a rule-11
> slip of mine recorded because it is the kind that looks harmless, and
> **§10**, *a `grep` that returns 0 is not evidence of absence unless the
> pattern cannot wrap.* ⓘ §10's other half — `report.py::shout_section`'s
> mechanism — **is** published (`RECAP_PHP.md`), so only the `grep` lesson is
> unique here.
>
> ⚠⚠⚠ **UNREVIEWED** (`PROTOCOL.md` rule 9), as it was when it was scratch.
> **Promotion changes where this lives, not what it has earned.** The parts that
> reached `.memory-php/02-ladder.md` went in as **FLAGS**, and they are still
> flags.
>
> ⓘ **Two `.temp/` citations below were repointed at the promoted probes; every
> other `.temp/` reference in this file is HISTORICAL — it says where work
> happened — and is correct as written.**

---

**Manager's own work. ⚠ UNREVIEWED (`PROTOCOL.md` rule 9) — this goes into
`RECAP_PHP.md` as a finding and into `.memory-php/` only as a FLAG.**

Probe: `identity_null.py`, `--selftest` **PASS, 9 must-fire negatives**.
Re-derives everything from `results*/gate/*.json` and `results*/<row>.json`.
No artefact; the script is the evidence.

## Why I ran it

I was about to dispatch item 58 (search `ph45`'s R4 endpoint) and noticed while
reading `ph45`'s gate record that its `identity` entry for `unsafe vs verus`
reads **`differ` at both O0 and O3** — not `exact`.

F74 settled item 52 by a **null control**: *"`identity` pins R4 and R5
byte-identical, so `verus − unsafe` has a known true value of 0."* If `ph45`
is not pinned byte-identical, that premise is not true of `ph45`. And
`.tasks-php/probes/null_control.py` — my own probe, the one F74 rests on — **never
checked the premise on any row.** It asserted it for all 39.

## §1 The premise is false on 7 of 40 rows

Measured level of `unsafe vs verus` at **O3**:

| | `exact` | not `exact` |
|---|---|---|
| PHP (7 incl. `ph00`) | `ph00` `ph03` `ph16` `ph29` | **`ph07` norel · `ph45` differ · `ph64` differ** |
| PAT (33) | 28 | **`p25` `p28` `p29` `p34` `p36`, all norel** |

## §2 ⚠⚠ BUT THE LEVEL IS THE WRONG PREDICATE — AND RESTRICTING ON IT WOULD HAVE LOOKED RIGHT

`exact` is **byte**-identity. A count statistic needs only the **executed
instruction count** to agree, and `norel` covers two different situations:

* same instructions at different rip-relative displacements, and
* genuinely different code.

Only the second breaks the null. The rows say which they are, **in their own
`identity` notes**:

* `p25`: *"every intra-function branch displacement and the rip-relative `lea`
  … differ by exactly that — `lea -0xde51(%rip)` against `lea -0xde31(%rip)`,
  **both resolving to the same absolute address `0x7910`** — while `md5_norm`,
  the instruction count (189 non-pad at `-O3`) and the byte count are all
  identical."*
* `ph07`: *"R4 == R5 at O3 **UP TO RELOCATIONS**, and `norel` is the honest
  level rather than `exact`. … **251 instructions and 953 bytes in BOTH
  cells**."*

So the predicate is **`Δnopad == 0 and Δbytes == 0`**, read out of the identity
entry's own `counts_a`/`counts_b`. Under it:

| | true null | rescued by Δnopad (level said no) | **genuinely NOT a null** |
|---|---|---|---|
| PHP | 4 | 1 — `ph07` | **2 — `ph45`, `ph64`** |
| PAT | 28 | 5 — `p25` `p28` `p29` `p34` `p36` | **0** |

⭐⭐ **ALL 33 PAT ROWS ARE TRUE NULLS.** F74's numbers are **intact**:

| | over all rows | over `level == exact` only | correct (Δnopad) |
|---|---|---|---|
| PHP B worst | **+3.6522 %** `ph03 small` | +3.6522 % | **+3.6522 %** |
| PAT B worst | **+5.0102 %** `p25 large` | −0.8734 % `p02 small` | **+5.0102 %** |
| PHP / PAT A worst | 0.0000 % | 0.0000 % | **0.0000 %** |

⚠⚠ **The middle column is the trap.** A level-based restriction drops PAT's
family-B worst null by **5.7×**, to a number that looks perfectly plausible, by
discarding **five valid cells**. I would have published it. The `--selftest`
negative that stops this is **N6**: `p25`'s `spec.md` contains the literal
string `identity: unsafe == verus, O3 exact` — **shared-block boilerplate** —
while its real pin, in a table row, is `` `O0: norel`, `O3: norel` ``. A script
that grepped `spec.md` for the level would call `p25` a null for the wrong
reason and get the right answer. **Read the record, not the spec.**

## §3 ⭐⭐ THE REAL GAP: F74 ARGUED FROM A NULL CONTROL ALONE, AND A NULL CONTROL IS ONE-SIDED

**A statistic hard-wired to `0` would ace every null in this tree.** F74
published family A on the strength of the null and nothing else, and that
argument is exactly as persuasive for a constant. The **sensitivity** half was
never measured. It now is, and the rows that are *not* nulls supply it free:
there the kernels differ by a **known** static count, so family A has a
**predicted nonzero** value.

    predicted Δ(kernel_exclusive_ir) = Δnopad × (calls on which it executes)

| row | input | Δnopad | Δ(A) | `n_iters` | `exec_rate` |
|---|---|---|---|---|---|
| `ph45` | `large.bin` | −2 | **−400** | 200 | **1.0000** |
| `ph45` | `small.bin` | −2 | **−3000** | 1500 | **1.0000** |
| `ph64` | `large.bin` | −1 | −102 | 200 | 0.5100 |
| `ph64` | `small.bin` | −1 | −764 | 1500 | 0.5093 |

⭐ **Family A resolves a 2-instruction static difference to the instruction**,
independently on two inputs 7.5× apart in call count.

⚠ **`exec_rate` of exactly `1.0000` is "too clean", and too-clean is the only
warning F52 gives** — so `ph64` is the control on `ph45`. If the arithmetic
were feeding itself, **every** row would read `1.0`. `ph64`'s does not: its one
instruction sits on a **conditional** path, and the two inputs agree on its
rate to **0.0007** — a quantity nobody designed to agree. Three fields, two
files (`Δ` from `results-php/<row>.json`, `Δnopad` from
`results-php/gate/<row>.json`, `n_iters` from a third key), no fitting.
Negatives **N8** (both `1.0` and `<1.0` cells must exist, or §3 proves nothing)
and **N9** (multi-input rates agree < 0.02) guard it.

## §4 ⭐ AND THE SIGN: ON `ph45` AND `ph64`, **R5 IS CHEAPER THAN R4**

`counts_a` is `unsafe`, `counts_b` is `verus`. Δnopad is **−2** and **−1**: the
**proved** rung's kernel is *smaller* than the hand-written `unsafe` one, and
family A measures it — **−0.0383 %** (`ph45 small`), **−0.0067 %** (`ph64
small`). Nothing is violated; both rows pin `differ`. But the **direction** is
F77's shape from a new angle: F77 found an admissible R4 *cheaper than the
shipped one*; this is the **shipped R5** cheaper than the shipped R4, on two of
six rows, with no search at all.

## §5 ⚠ FOR ROUTING ONLY — `harness/check.py` HAS THE SAME UNCHECKED PREMISE

`harness/check.py`'s null docstring is far more careful than my probe was: it
corrects its table for **mode** (*"a null control is only a null in the MODE
ITS IDENTITY PIN COVERS"*), for **opt level** (`p28 1732.73` and `p29 425.80`
were `-O0` cells printed under an `-O3` heading) and for **input** (*"on
`small.bin` p25's and p42's nulls are `0.00`"*), and it warns **⚠⚠⚠ A NULL IS A
PROPERTY OF A CELL. DO NOT MAX IT OVER MODE, OVER LEVEL, OR OVER INPUT.**

It does **not** correct for the **identity level**, and its worst quoted cell —
**`p25 large +269.52`** — is on the row whose own pin is `` `O3: norel` ``,
while the docstring justifies the table by *"`identity` forces R4's and R5's
kernels to agree byte for byte."*

✅ **The number is right and the justification is wrong.** p25 rescues it by the
Δnopad route its own identity note records. ⚠ **`harness/` is FROZEN** — editing
that docstring costs a 33-pattern re-gate for a sentence. **Reported for
routing, not fixed.** ⚠ And `results/SYNTHESIS.md` is the authority on the PAT
side, not me.

## §6 ⚠⚠ WHAT THIS CHANGES ABOUT ITEM 58, WHICH IS WHY IT WAS WORTH THE DETOUR

The shared `why` block — byte-identical in all six PHP rows and all 33 PAT rows
— argues R4 admissibility **from the identity pin**:

> *"All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not
> merely a program that MAY use `unsafe`: it is a program that must have a
> byte-identical R5 twin that Verus verifies."*

⚠⚠⚠ **THAT ANTECEDENT IS FALSE ON THREE OF SIX PHP ROWS** — `ph07` `norel`,
`ph45` `differ`, `ph64` `differ`. The sentence is PAT-side boilerplate carried
into a programme where it does not hold.

▶ **So an R4 candidate on `ph45` does NOT have to be byte-identical to its R5
twin.** `ph45`'s R4 search is **wider** than `ph29`'s was, and F77's method —
hunt for a spelling whose Verus twin compiles byte-identically — is **not the
binding constraint there**. The binding constraint is only that the candidate
**verify**. This goes into the item-58 task file as a stated premise, with the
instruction to re-derive it.

## §7 ⭐⭐⭐ AND THEN THE SECOND PROBE OVERTURNED F74's MECHANISM — `inclusive_ir.py`

**F82 above asks whether the null's PREMISE held. It does not ask the obvious
next question: WHETHER THE NONZERO READING IS REAL.** It is.

Probe `inclusive_ir.py`, `--selftest` **PASS, 6 must-fire negatives**. Adds a
**third statistic**, computable from the same profiles and **without touching
frozen code**, because the pinned valgrind 3.27.1 ships
`callgrind_annotate --inclusive=yes`:

| | scope | runs |
|---|---|---|
| **A** `kernel_exclusive_ir` | inside the kernel symbol; callees in no column | 1 |
| **C** `kernel` **INCLUSIVE** `Ir` | the kernel's whole **call tree** | 1 |
| **B** `marginal_ir_per_call` | whole program, a **slope** | 2, differenced |

`harness/measure.py::callgrind_ir` records exclusive only, for two needles.

### The PHP headline null is REAL WORK

`ph03-uudecode-bound`, `unsafe` vs `verus`, O3/isolated — **and the two kernels
have the same `md5_fn` `338505795ee18db952aafcdaec522df4`, so they are
byte-identical, not merely equal in count:**

| input | A | C | B |
|---|---|---|---|
| `small.bin` | **0** | **+265.924/call** `+3.6581 %` | **+266.000/call** `+3.6522 %` |
| `large.bin` | **0** | **−31.000/call** | **−31.000/call** |

⭐⭐⭐ **B AND C AGREE TO 0.03 % ON `small` AND EXACTLY ON `large`, BY TWO
INDEPENDENT METHODS.** So B's `+3.65 %` — *the number F74 calls the PHP
programme's worst null* — **is not noise. It is real work, measured twice.**

⚠ **The environment is ruled out, and it had to be**, because `check.py`
documents a mechanism that would explain it away: *"the environment block shifts
the stack pointer → a per-call stack array's alignment → a different tail in
`__memset_avx2_unaligned_erms`"*, ±7, **between two runs of the SAME build**.
Measured on **one** binary at **three** environment sizes spanning 4 000 bytes:
kernel inclusive is **181,733,873 at every one**, spread **0**. (Negative N6.)

⚠ **And the work is LOCATED, not inferred**: **+205.94/call** in one unnamed
libc function and **+56.98** in a second, both in `libc.so.6`, both **local**
functions the dynamic symbol table does not name — nearest exported symbols
`__default_morecore` (+2912) and `timer_settime` (+3488), offsets far too large
to be those functions. `__default_morecore` is in `malloc.c`, which places the
cost in the **allocator**. ⚠ **Stated as a region, not a function name: without
libc debug symbols this cannot be named and the probe does not pretend to.**

### ⭐⭐ SO THE DEFECT IN FAMILY B IS NOT NOISE, IT IS ATTRIBUTION

**The two kernels are byte-identical, so neither rung's code can have caused a
3.66 % difference in allocator work.** B charges the rung for work the rung did
not do. ⚠⚠ **That is a CONFOUND, and unlike noise a confound does not shrink
with more measurement** — which is exactly why calling it noise mattered.

✅ **F74's practical advice — headline family A, name the statistic — SURVIVES.
Its stated reason is replaced by a stronger one.**

### ⚠ AND THE PAT CELL SPLITS THE DIFFERENCE, SO BOTH READINGS WERE PARTLY RIGHT

`p25-realloc-growth`, `large.bin`: **C +167.872/call** against **B
+269.520/call** — they agree to only **37.71 %**. So of the worst null in either
programme, roughly **62 % is real call-tree work** and **≈ +101.65/call is a
method artefact of the slope**. ⚠⚠ **I have NOT identified what the residual is,
and I am not going to invent a mechanism for it** — that is exactly F72, where
my stated cause turned out to be a story and `_033` produced git evidence
against it. ⓘ `p25/small` reads **0 on all three**, which is the control.

### ⚠ SCOPE — WHAT THIS DOES NOT SAY

**Attribution is a property of the COMPARISON, not of the statistic.** On a
**C-vs-Rust** comparison callee work often **is** rung-attributable: `ph64`'s C
rung really does call `malloc` `2n+2` times per call and **60 %** of its
instructions are in libc (F71, open item **54**). The confound is specific to
comparisons where the two rungs' own code is identical or nearly so — which is
**precisely why the R4/R5 pair was picked as a null**, and precisely where the
confound is largest relative to the signal.

### ⭐ THE META-OBSERVATION, AND IT IS THE PART WORTH KEEPING

**F74 has now been corrected three times in three rounds:**

| | what was wrong | found by |
|---|---|---|
| **F80** | the **rule** (one condition) | `ph45`, the very next row built |
| **F82** | the **premise** (never checked per row) | reading a gate record for another purpose |
| **F83** | the **mechanism** (“noise”) | a second, independent measurement |

⚠⚠ **F74 was published from ONE script reading ONE field, and every one of its
three errors was found by bringing a SECOND METHOD to bear on the same
quantity.** Not one was an arithmetic error. ▶ **A statistic's own null is not
enough evidence about a statistic.**

### ▶ WHAT FAMILY C ACTUALLY BUYS — and I got this wrong on the first pass

⚠⚠ **MY FIRST DRAFT OF THIS SECTION SAID C HAS "A's ATTRIBUTABILITY AND B's
COVERAGE", MAKING IT THE STATISTIC THE PROJECT WANTS. THAT IS FALSE, AND IT IS
THE VERY ERROR §7 IS ABOUT — one reading, no second method.** On `ph03/small` C
reads **+265.924**, essentially B's **+266.000**. The allocator work **is** in
the kernel's call tree, so **C includes it too**. Scoping to the call tree does
not make work attributable; the work is genuinely there, it is just **caused by
binary layout rather than by either rung's logic**.

Corrected:

| | coverage | slope artefact | **attributable** |
|---|---|---|---|
| **A** | ⚠ kernel only — misses 91–94 % on `ph45` | none | ✅ yes |
| **C** | ✅ whole call tree | ✅ **none** — one run | ❌ **no** |
| **B** | ✅ whole program | ⚠ **yes** — `+101.65/call` on `p25/large` | ❌ no |

▶ **So C strictly DOMINATES B — same coverage, one fewer error source — and it
does NOT solve attribution.** ⭐⭐ **NO STATISTIC HERE SOLVES ATTRIBUTION**,
because it is not a property of the statistic: it is a property of the
comparison. Two rungs whose callee usage differs for reasons unrelated to
safety cannot be separated by choosing a better column. **That is what
`inside_share` and the corrected F74 rule are groping at, and it is why `ph45`
publishing "both families, labelled" is the right answer rather than a
compromise.**

⚠⚠ **NOT BUILT, and deliberately.** `TASK_PHP_037` is running and one agent
works at a time. It is buildable as a **php-side control** with no frozen-file
change — six PAT patterns' `controls/` already call `objdump` directly, so one
calling `callgrind_annotate` is the same shape. ▶ **Open item 62.**

## §9 ⭐⭐⭐ AND THE SWEEP REFINED F83 — WHICH I HAD ALSO PUBLISHED OFF TWO ROWS

**F83 says *"B is measuring real work"*. Across 12 cells that is TRUE ON 6 AND
FALSE ON 6.** Probe `bc_sweep.py`, `--selftest` **PASS, 7 must-fire negatives**;
profiles from `sweep_cg.sh`, every binary md5-checked against its published
record. ⛔ **`ph45` excluded — `TASK_PHP_037` is rebuilding it.**

| row | inp | level | A | **C** | **B** | disagree |
|---|---|---|---|---|---|---|
| `ph00` | small | exact | 0 | **0.000** | **−1.000** | 100 % |
| `ph00` | large | exact | 0 | **0.000** | **−1.000** | 100 % |
| `ph03` | small | exact | 0 | +265.924 | +266.000 | 0.03 % |
| `ph03` | large | exact | 0 | −31.000 | −31.000 | 0.00 % |
| `ph07` | small | norel | 0 | +17.624 | **+37.340** | 52.80 % |
| `ph07` | large | norel | 0 | 0.000 | 0.000 | — |
| `ph16` | small/large | exact | 0 | 0.000 | 0.000 | — |
| `ph29` | small | exact | 0 | **+0.061** | **+8.830** | **99.31 %** |
| `ph29` | large | exact | 0 | **+2.383** | **+0.000** | **100 %** |
| `ph64` | small | differ | −0.509 | +214.970 | +193.360 | 10.05 % |
| `ph64` | large | differ | −0.510 | −28.255 | −28.770 | 1.79 % |

**6 agree under 5 %; 4 where B is larger; 2 where C is larger.**
The decomposition the numbers force:

> **B = C + work OUTSIDE the kernel's call tree + slope-method effects**

### Three results a two-row sample could not reach

1. ⭐⭐ **THE UBIQUITOUS `−1.00` IS A SLOPE ARTEFACT.** `harness/check.py`'s PAT
   null table records *"1.00 ≤ |null| < 2 in 35 cells (**34 of them exactly
   −1.00**)"* and offers **no mechanism**. `ph00` reads **B `−1.000` on both
   inputs while C reads `0.000` on both.** ▶ **A whole documented class of that
   table is the slope, not the program.** ⚠ PAT-side; **reported for routing**,
   and it belongs with item 60.

2. ⚠⚠ **B CAN MISS REAL WORK, NOT ONLY INVENT IT.** `ph29/large`: **C
   `+2.383`/call, B `+0.000`.** **B reports a clean null over a real call-tree
   difference.** Every prior treatment of B — F74's and F83's included —
   assumed the error was one-directional. ⭐ **A two-directional error is not
   correctable by any constant**, which is why this matters more than its size.

3. **The disagreement is not one odd row**: `ph29/small` **99.31 %**,
   `ph07/small` **52.80 %**, while `ph03`, `ph16` and `ph64` agree closely.
   ⚠ **`ph29` is the row publishing F77's `−5.63 pp` R4 result**, and its R4/R5
   B reading is **99.31 % artefact**. ⓘ F77 is quoted in **A1**, so F77 is not
   affected — but that is luck, not design.

### ✅ And family A's null is re-derived through a DIFFERENT code path

**`max |A| = 0.000000` over all 8 true-null cells**, computed here off the
**callgrind profiles** rather than off `results-php/` as F82 did. Two code paths,
same answer. ⚠ And A reads `−0.509`/`−0.510` on `ph64`, matching F82's
`exec_rate` of 0.5093/0.5100 — **the conditional path, from the other direction.**

### ⚠ What C is not

C is **not "the truth"** — it is the kernel's **call tree**, which is the right
unit for *"what does one call cost"* only because `main` here is the **harness**
rather than the program. And **C does not fix attribution**: on `ph03` the two
kernels are **byte-identical** and C still reads `+265.924`.

## §10 ⚠⚠ A LINE-BASED `grep` CANNOT FIND A PHRASE THAT WRAPS — AND I ASSERTED AN ABSENCE FROM ONE

I told `TASK_PHP_037` its F72 hedge was **absent**, citing
`grep -a -c 'DO NOT QUOTE IT AS A RESULT' …/NOTES.md` → **0**. **The hedge was
already there.** The phrase **wraps across a line break** in the prose, and
`grep` matches within a line, so it returns 0 whether the text is present or
not — **the check cannot distinguish presence from absence and I read it as
absence.**

⚠⚠⚠ **A grep that returns 0 is not evidence of absence unless the pattern
CANNOT wrap.** This is F35's family (`grep` dispatching to `ugrep` and exiting 1
on 41 corpus files) at a different joint: **the tool answered a narrower
question than the one I asked it.** ▶ **For prose, match a short unwrappable
token, or read the section.** Everything in this project's prose is
hard-wrapped at ~76 columns, so **any phrase over ~8 words is a coin flip.**

⭐ Caught by the agent, not by me, and it cost it a paragraph of its report to
correct its coordinator. ⓘ It also found the property that explains why gate
round 2 passed stage 9c against its own prediction:
**`report.py::shout_section` emits a table line only for a `controls_json` entry
that is NOT `FRESH`** — so adding a **FRESH** `controls/*.json` to a row needs
**no `report.py` re-render and no extra gate round.** That is a real fact about
the frozen harness and it belongs in the findings.

## §8 ⚠ MY OWN RULE-11 SLIP, RECORDED BECAUSE IT IS THE KIND THAT LOOKS HARMLESS

`PROTOCOL.md` rule 11: **do not edit files a running subagent reads.**
`TASK_PHP_037`'s read list opens with `RECAP_PHP.md` and `.memory-php/` 00–04,
**and I landed F83, item 62, the index line and the box rewrite into
`RECAP_PHP.md` while that agent was running.**

⚠ The `.memory-php/` FLAG went in **before** dispatch, which was fine. The
`RECAP_PHP.md` edits did not.

**Actual risk, assessed rather than waved away:** every edit was **additive** —
a new finding section, a new items row, an index clause, and a box whose
`NOTING RUNNING` line had become false. Nothing the task depends on changed
meaning, and F83 *strengthens* the one claim of its brief that touches this
(*"a null control is one-sided"*, task §3.4, which F83 makes more true rather
than less). The residual risk is a torn read if an edit landed mid-`Read`.

⚠⚠ **The rule is not really about the content, it is about the WINDOW**, and I
had no way to know whether the agent had already read the file — *"almost
certainly by now"* is not knowing. ▶ **Standing correction for the rest of this
round: stage manager edits in `.temp/mgr172/` and land them after the task
reports.** The `ph03`/`p25` callgrind work and this notes file are safe because
they touch nothing the task reads or writes, and `.tasks-php/probes/sweep_cg.sh`
**deliberately excludes `ph45`** — `TASK_PHP_037` is rebuilding it, so its
binaries could move under a sweep mid-run.

## Artefacts

Nothing to delete — `identity_null.py` reads committed JSON and writes no file.
⚠ `.temp/mgr171/ptr_as_i32` and `.temp/mgr171/ptr_as_int` are **compiled
binaries with no rebuild script**; `rebuild.sh` written there to discharge
`CLAUDE.md` constraint 6 before deleting them.
