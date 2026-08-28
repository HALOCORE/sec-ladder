# TASK_114 — review of TASK_107, the task that changed the INSTRUMENT

**Role: reviewer.** Nothing was fixed. Probes, logs and JSON: `.temp/r114/`
(`NOTES.md` there is the index and says how to re-derive each one).

⚠ **`TASK_113` was running concurrently throughout.** Every `Ir` figure below is
callgrind and deterministic. Every wall-clock figure is repeated, and the two
that decide anything (§B) are 4.6× apart on an 80-CPU box at load ≈2.

**Bottom line, against the manager's first named doubt:** ⚠⚠ **this task did
need reviewing, and it is §B — not §A — that carries the worst of it.**
TASK_107 is as good a report as the task file says; three of the four findings
below are in places its own self-criticism pointed at, and the fourth is a
measurement that **reverses** one of its headline numbers.

---

## Severity summary

| # | § | severity | one line |
|---|---|---|---|
| B1 | A | **blocker** | the `tuning_vars` rule is FALSE, and the incomplete half is **`bytes`**, not `tuning_vars` |
| B2 | B | **blocker** | the `miri` driver never reads `MIRIFLAGS`; p42's fast/slow assignment **reverses**, and `MIRI_FLAGS = ()` selects the SLOW state in this shell |
| M3 | B | major | TASK_107's family-2 seed result is **confounded** by the same variable |
| M4 | C | major | **four** routes the UNION misses, all compositions of TASK_107's own two failure families |
| m5 | C | minor | 7 source shapes write no `.d` → a `tcb-unsafe` gate FAIL; the docstring's claim is unqualified |
| m6 | C | minor | `.temp/check/depinfo/dep.<pid>.d` is never removed (82 accumulated) |
| m7 | D | minor | both TASK_107 item-7 corrections are **still unlanded**; `.memory/` contradicts itself on the `<2.00` band |
| m8 | E | minor | stage 9 `MISSING`'s stated fix **cannot work** on the case it names |
| m9 | E | minor | `limbs.py` still COPIES two more `check.py` constants, two lines above the comment saying not to |

✅ **Clean negatives** (named attacks that did not land) are in their own section
at the end — **seven** of them, so the next agent need not re-run them.

---

## B1 (blocker) — §A. `same bytes AND same tuning_vars ⇒ the marginal must match EXACTLY` is FALSE

The rule is written at `harness/check.py:8199–8206`, beside `marginal_ir_env`,
and is now in **all 26 committed gate records**. It restates
`.memory/03-measurement.md:2456–2457` (TASK_103's reproduction protocol) and is
refined at `.memory/03-measurement.md:2773–2793` (TASK_107).

**Must-fire arm first** (`.temp/r114/a1_tuning_complete.py pad`), p03 `unsafe`
`-O3 isolated` `small.bin`, the report's own cell. It reproduces TASK_107's
ladder to the instruction:

```
  pad=  0   bytes=3290  marginal=3066.00
  pad=  8   bytes=3298  marginal=3059.00
  pad= 16   bytes=3306  marginal=3059.00
  pad= 24   bytes=3314  marginal=3066.00      MUST-FIRE: FIRED
```

**The counterexample** (`a1_tuning_complete.py count`) — four environments with a
**byte-identical recorded `bytes`** and **identical (empty) `tuning_vars`**,
differing only in how many variables that byte budget is spread over:

```
  1 filler var(s)   bytes=3520  nvars=49  marginal=3059.00
  2 filler var(s)   bytes=3520  nvars=50  marginal=3059.00
  3 filler var(s)   bytes=3520  nvars=51  marginal=3066.00
  4 filler var(s)   bytes=3520  nvars=52  marginal=3066.00
  recorded bytes: [3520]   tuning_vars identical: True     *** RULE FALSIFIED ***
```

**And the mechanism, measured rather than argued** (`a2_envp_period.py`), nine
rungs at a constant `bytes=3680`:

```
  marginal by filler-count 1..9:
      3059, 3059, 3066, 3066, 3059, 3059, 3066, 3066, 3059
  recorded bytes across the sweep: [3680] (CONSTANT)
  period-4 in the variable count: True
```

**Period 4 in the variable count = the ±7's 32-byte period ÷ 8 bytes per envp
POINTER SLOT.** `_env_block` records
`len(open('/proc/self/environ','rb').read())`, which is the concatenation of
`NAME=VALUE\0` and **contains no envp pointer array at all**.

⚠⚠ **That is the exact term `.memory/03-measurement.md:2580` calls *"the part
the manager forgot entirely"*** in the 87-vs-64 decomposition that corrected
TASK_099:

```
  envp pointer slot        8      <-- the part the manager forgot entirely
  name "SLB_ALIGN_PAD"    13
  "="                      1
  pad z*64                64
  NUL                      1
```

**The pin repeats the arithmetic error it was written to prevent.** `bytes`
captures terms 2–5 and drops term 1.

**⚠ The diagnosis is the opposite of the one TASK_107's item 4 offers.** Its
open item is *"`tuning_vars` is a chosen prefix set … I have not shown it is
complete."* Two clean negatives say the prefix set is **not** where this breaks
(see the clean-negatives section: pure permutation and value-content both hold
exactly). **It is `bytes` that is lossy, and it is lossy in a way one integer
fixes.**

**What the manager can land, and it is one line** — record the count too, or
record the stack-relevant total:

```python
"bytes": n, "nvars": <count>,          # or:  "envp_stack_bytes": n + 8*nvars
```

⚠ **This does not invalidate any published `Ir`.** It invalidates the
**comparison rule** that licenses reading two records against each other, and
that rule is now in 26 records. Two runs can satisfy it and still differ by ±7
per rung / ±14 per pair.

### §A.3 — the `argv` domain lives in ONE prose file and nowhere else

TASK_107 states the pin is *"valid within one clone location"* because `argv` is
the other half of the axis. Where that restriction is written:

* `grep -n argv harness/check.py` outside `sys.argv` → **0 hits**
* `grep -rn "clone location" harness/ .memory/` → **0 hits**
* `results/gate/*.json` `marginal_ir_env` carries `bytes` and `tuning_vars`, **nothing else**
* it appears in `.tasks/TASK_107_REPORT.md` only

Measured, so the gap is not argued (`.temp/r114/a3_argv.py`) — environment held
byte-identical, only the `argv[1]` path length varied:

```
  argv[1] len= 57   marginal=3066.00
  argv[1] len= 58   marginal=3066.00
  argv[1] len= 59   marginal=3059.00        <- +2 characters, -7.00 Ir/call
  argv[1] len= 61/65/73   marginal=3059.00
```

This is the `p05` failure mode the task file names: **a pin whose domain lives
only in prose**, and here it is weaker than `p05` — the prose is a task report,
not even a docstring.

---

## B2 (blocker) — §B. `MIRIFLAGS` is not the variable, and the fast/slow assignment REVERSES

### B2.1 — the `miri` driver does not read `MIRIFLAGS` at all

`check.py:7871` invokes the `miri` **rustc driver** directly, not `cargo miri`.
`.temp/r114/b1_miriflags_mech.py read`:

```
  MIRIFLAGS=<bogus>            rc=  0 rejected=False  ''
  cli <bogus> (MUST FIRE)      rc=  1 rejected=True  'error: unknown unstable option: `miri-r114-not-a-real-flag`'
  nothing (must NOT fire)      rc=  0 rejected=False  ''
```

`MIRIFLAGS` is `cargo-miri`'s variable. The driver ignores it. **So the 4.6×
was never a flag being parsed, and no content-vs-presence framing applies: the
variable is inert as a flag channel in every one of TASK_107's seven settings.**

This also answers the task file's rebuild question **structurally and by
measurement**: there is no cargo, no fingerprint and no target dir in the loop,
and on a synthetic Vec-heavy program (`b1 scale`) the cost is neither
multiplicative nor additive — it is nothing:

```
  n=     1  unset=0.10s  MIRIFLAGS=''=0.09s  ratio=0.91x  diff=-0.01s
  n=  2000  unset=0.47s  MIRIFLAGS=''=0.49s  ratio=1.04x  diff=+0.02s
  n=  8000  unset=1.62s  MIRIFLAGS=''=1.64s  ratio=1.01x  diff=+0.02s
  n= 32000  unset=6.26s  MIRIFLAGS=''=6.21s  ratio=0.99x  diff=-0.05s
```

### B2.2 — ⚠⚠ on p42 the direction is REVERSED, and a decoy variable behaves identically

`.temp/r114/b2_p42_trigger.py`, p42 `unsafe.rs` on `adversarial-wincap.bin`, the
gate's own probe file, `cwd=pdir`, the exact `check_miri` command line — i.e.
TASK_107 §C's setup:

```
  A  MIRIFLAGS unset (baseline)         338.1s   envbytes=3280 nvars=48
  B  MIRIFLAGS='' (author's arm)         75.1s   envbytes=3291 nvars=49
  C  SLB_R114_DECOY='' (NOT miriflags)   74.4s   envbytes=3296 nvars=49
  A' MIRIFLAGS unset, repeat            347.4s
  B' MIRIFLAGS='' , repeat               75.4s
  C' SLB_R114_DECOY='' , repeat          75.9s
  D  removed $OLDPWD                     75.3s   envbytes=3228 nvars=47
```

**TASK_107 measured `unset` = 74.6/73.4/74.0/73.8/73.2 s and `MIRIFLAGS=""` =
339.8 s. I measure the two the other way round, three times each way.**

⚠ **The magnitude reproduces exactly — 4.6× — and the ASSIGNMENT does not.**
A decoy variable that is not `MIRIFLAGS` is indistinguishable from `MIRIFLAGS`;
so is *removing* a variable. **`MIRIFLAGS` is not the trigger. The environment
block is.**

**And the state is a two-valued function of the environment block**
(`.temp/r114/b5_p42_ladder.py`, one variable `SLB_R114_P` padded 0–9 so the
variable COUNT is held at 49 and only the block length moves):

```
  MUST-FIRE ambient (no var added)  nvars=48 bytes=3280  addr=0x22123   345.4s
  pad= 0  nvars=49 bytes=3292  addr=0x22161    74.9s  fast
  pad= 1  nvars=49 bytes=3293  addr=0x22161    76.1s  fast
  pad= 2..9  nvars=49 bytes=3294..3301  addr=0x22169   75.5..77.5s  all fast

  MUST-FIRE (ambient reproduces ~340 s): True  (345.4s)
  states: 1 slow / 10 fast out of 11
```

So the ambient environment is the third independent measurement of the slow
state (338.1 / 347.4 / 345.4 s, taken tens of minutes apart while the other
agent ran) and **every perturbation tried — add a variable, add a longer
variable, remove a variable, add `MIRIFLAGS` — lands in the fast state.** The
slow state is rare in the neighbourhood and is exactly where the gate sits
today.

### B2.3 — the consequence, and it is the blocker

`MIRI_TIMEOUT` is **180 s** and the two states are ≈75 s and ≈340 s.
`results/gate/p42-goto-cleanup.json` records `unsafe.rs adversarial-wincap.bin`
as **green** (`ub=False`, not blocked), with `miri.miriflags: null`.

> ⚠⚠ **Re-running `check.py p42` from THIS shell, with the shipped
> `MIRI_FLAGS = ()`, puts that row in the 340 s state and it would be
> BLOCKED.** The landed fix does not control the state; **it changes it**, and
> in the shell I am in it selects the slow one.

**So `MIRI_FLAGS = ()` was chosen to un-block a row that a re-measure of the
same configuration now blocks.** TASK_107's sweep-2 result (*"p42 is back to one
blocked row"*) is one draw of the same two-state variable that produced sweep 1,
and nothing in the record distinguishes them: `miriflags`, `miriflags_removed_ambient`
and `miri_version` are all identical in the slow and fast states.

⚠ **This is the same class as TASK_107's own item 2** (*"one of my own earlier
measurements does not reproduce and I cannot explain it"* — 72.8/73.8/73.6 s
against three later repeats). **That non-reproduction was the effect, not
noise.** It was the environment moving between his runs.

⚠⚠ **I am NOT naming a mechanism for the 4.6× itself.** I have the effect across
21 timed runs and the trigger localised to the environment block rather than to
`MIRIFLAGS`; I have no explanation. `.memory/`'s standing rule applies and
TASK_107 was right to state it in bold: **mechanism OPEN.**

✅ **And I killed the one correlation I had, rather than reporting it.** The only
slow environment was also the only one drawing a Miri base address `≡ 3 (mod 4)`
— one point, worth nothing, so `.temp/r114/b6_addr_search.py` searched 43
environments for a *second* `% 4 == 3` draw and timed it:

```
  base % 4 == 0: 8 environments      base % 4 == 1: 14      base % 4 == 3: 15
  MUST-FIRE ambient (expect SLOW)  addr=0x22123 (mod4=3)   343.1s  SLOW
  drop $AI_AGENT                   addr=0x2212b (mod4=3)    75.0s  fast
  add pad 0                        addr=0x22161 (mod4=1)    74.7s  fast
  -> the residue is a COINCIDENCE; correlation DEAD
```

**Four independent slow measurements of the ambient environment (338.1 / 347.4 /
345.4 / 343.1 s) and every one of ~15 perturbations fast** — including one that
merely *drops* a variable. ⚠ **Not a cold-cache artefact either: `b2`'s arm `A'`
was the FOURTH run of its sequence and still took 347.4 s.**

### B2.4 — item 6's blast radius: the question has changed shape

TASK_107 lists *"§C's blast radius outside p42 is not measured … I did not test
the other 20."* ⚠ **With `MIRIFLAGS` out of the picture the question is no longer
"do the other 20 patterns react to `MIRIFLAGS`" — it is "which patterns' Miri
cost is a two-state function of the environment block".** The ~0% he measured on
38 rows across p03/p38/p46/p14/p02 is still evidence, and it covers 5 of 26.
**Twenty-one patterns are unprobed on the axis that actually exists.** I did not
run them: at ≈75–345 s per row that is a task, not a review arm.

---

## M3 (major) — §B.4. TASK_107's family-2 measurement is CONFOUNDED, and `miri_version` is not sufficient

**Is `base % 4` a good witness?** No, and the full address is a better one
(`.temp/r114/b3_miri_addr.py`):

```
  == 6 launches, byte-identical environment ==
    0x22123 0x235e8   (x6, identical)      -> full address CONSTANT: True
  == same program, environment padded ==
    pad=  0: 0x22161    pad=  2: 0x22169    pad= 16: 0x22171    pad= 32: 0x22181
                                            -> the address MOVES with the environment
```

✅ **The determinism half of TASK_107's claim is upheld and strengthened** — not
two bits, the whole address, six launches.
⚠ **The reproducibility half is not.** The draw is a function of the
environment block (`-Zmiri-disable-isolation` is on the gate's command line, so
Miri materialises the host environment inside the interpreted process), and
`base % 4` reproduced as `3` because the environment was held fixed.

**And that confounds TASK_107's own family-2 table** — the one that produced
*"the live variable is unseeded-vs-seeded, not seed-vs-seed."*
`.temp/r114/b4_family2_confound.py`, `Vec<u8>` + `ptr::read::<u32>` at byte
offset 1, both must-fire controls run in **every** arm:

```
  A nothing added            envbytes=3280  family2 UB=False  base=0x22123 (mod4=3)  [ctl clean-UB=False ub-UB=True]
  B MIRIFLAGS=''             envbytes=3291  family2 UB=True   base=0x22161 (mod4=1)  [ctl clean-UB=False ub-UB=True]
  C MIRIFLAGS=-Zmiri-seed=0  envbytes=3304  family2 UB=True   base=0x22171 (mod4=1)  [ctl clean-UB=False ub-UB=True]
  D SLB_R114_DECOY=''        envbytes=3296  family2 UB=True   base=0x22169 (mod4=1)  [ctl clean-UB=False ub-UB=True]
  E SLB_R114_DECOY_LONGER='' envbytes=3303  family2 UB=True   base=0x22171 (mod4=1)  [ctl clean-UB=False ub-UB=True]

  MUST-FIRE controls held in every arm: True
```

**A decoy variable flips the UB verdict exactly as `-Zmiri-seed=0` does.** The
seeded arms in TASK_107's family 2 differed from the unseeded arm by **one
environment variable**, and the driver never read the seed (B2.1). ⚠ **So the
sentence *"the live variable is unseeded-vs-seeded"* is not established; the
live variable is the environment block.**

✅ **The CONCLUSION TASK_107 drew from family 2 survives and is now stronger:**
*"a green Miri row was a claim about a configuration nobody had written down."*
⚠ **But the configuration the record now writes down is the wrong one.**
`miri_version` pins the interpreter; nothing pins the draw. A green Miri row is
**still** a claim about an unrecorded draw, and `check.py` strips only
`MIRIFLAGS` — every other ambient variable is inherited and moves it.

⚠ **`.memory/00-environment.md:609`'s advice — *"read it as 'no UB at whatever
seed the unpinned default chose'"* — is wrong in kind, not only in detail.
There is no seed. Read it as *"no UB at whatever address draw the invoking
shell's environment selected"*.**

---

## M4 (major) — §C. FOUR routes the UNION misses

TASK_107's table has two failure families: the **regex** loses on attribute
spellings (R7a `cfg_attr`, R7b raw string, R7c `mod x { mod m; }`), and
**dep-info** loses on anything inside `verus!{}` (N1, N2). Each was measured
separately. ⚠ **The composition was never run**, and the union's 13/13 says
nothing about that cell because no row of the table occupies it.

`.temp/r114/c1_route14.py`, same instrument shape as `a1_routes.py` (Verus
poison test for "did Verus read the leaf"), every module named `m` and every
leaf `h.rs` so TASK_107's own probe artefact cannot recur:

```
CONTROL-R5     verus=1/0  verus-reads-leaf=True  dep=True  union=True   union_files=['h.rs']
CONTROL-plain  verus=1/0  verus-reads-leaf=False dep=False union=False  union_files=[]
N7aV           verus=1/0  verus-reads-leaf=True  dep=False union=False  *** UNION MISSES ***
N7bV           verus=1/0  verus-reads-leaf=True  dep=False union=False  *** UNION MISSES ***
N7cV           verus=1/0  verus-reads-leaf=True  dep=False union=False  *** UNION MISSES ***
N8             verus=1/0  verus-reads-leaf=True  dep=True  union=True   union_files=['h.rs']
N8V            verus=1/0  verus-reads-leaf=True  dep=False union=False  *** UNION MISSES ***
N9-symlink     verus=1/0  verus-reads-leaf=True  dep=True  union=True   union_files=['link.rs']

ROUTES THE UNION MISSES: ['N7aV', 'N7bV', 'N7cV', 'N8V']
MUST-FIRE control (CONTROL-R5 found by the union): True
Negative control (CONTROL-plain seen by nobody): True
```

* **N7aV** `#[cfg_attr(all(), path = "h.rs")] mod m;` **inside `verus!{}`**
* **N7bV** `#[path = r"h.rs"] mod m;` **inside `verus!{}`**
* **N7cV** `mod x { mod m; }` **inside `verus!{}`** (leaf `x/m.rs`)
* **N8V** a `macro_rules!` taking the path as an **argument** (`#[path = $p]`,
  so no literal ever sits next to `path` in the raw text), **inside `verus!{}`**.
  ⚠ **N8 — the same macro OUTSIDE `verus!{}` — is caught**, by dep-info, which
  is exactly the division of labour TASK_107 describes working.

**Confirmed, not a substring accident** (`c2_confirm_n7av.py`):

```
N7aV  Verus, unpoisoned: 1 verified, 0 errors
      Verus, leaf POISONED -- lines naming h.rs:
         --> /home/apt/repos_common/sec-ladder/.temp/r114/c1/N7aV/h.rs:5:6
      _path_includes(main.rs) = []
      `unsafe` tokens visible to a scan over that set: []

CONTROL-R5 (identical leaf, `#[path]` at top level)
      _path_includes(main.rs) = ['h.rs']
      `unsafe` tokens visible to a scan over that set: [('h.rs', 1), ('h.rs', 3)]
```

**This is TASK_098 §4A's shape — `1 verified, 0 errors` with the leaf's `unsafe`
unscanned — reached by a fourteenth, fifteenth, sixteenth and seventeenth
spelling.** It reaches everything `_path_includes` feeds: `_verus_file_list` →
`_trusted_items` / `_axiom_items` / `check_call_site`, plus `_scan_unsafe_sites`
and `_check_twin_cfg_hygiene`.

⚠ **It is not a regression and it is not a reason to undo the union.** Both
limbs were blind to these before TASK_107 too; the union closed R7a/R7b/R7c at
top level and left them open one construct deeper. **The prior the task file
states — *"nine routes found by three tasks, each after the previous table read
as exhaustive"* — held again, and the productive move is the one TASK_107 half
made: `verus!{}` is where the regex has to stand alone, so any spelling the
regex misses is automatically a hole the moment it is written inside it.**

### §C.2 — "blast radius zero" is the observation that the new limb does nothing yet

Re-derived independently (`.temp/r114/c4_census.py`, my own census, not
`a2_census.py`):

```
  distinct union results across 26 patterns: {('common/driver.rs',)}
  roots that produced NO `.d`: none
  files dep-info ADDS beyond the union: none
```

✅ TASK_107's number reproduces exactly. ⚠ **Read it as the second thing, not the
first: every end-to-end acceptance arm ran on a planted tree, and no shipped
pattern exercises any route at all.** The limb is inert; its value is entirely
prospective.

---

## m5 (minor) — §C.3. Seven shapes write no `.d`, and the docstring's claim is unqualified

`_dep_info_files`'s docstring says, without qualification: *"rustc emits the
`.d` even when compilation FAILS."* `.temp/r114/c3_failclosed.py`:

```
  ok-plain / ok-verus / empty / no_std / unknown-inner-attr /
  missing-mod / lex-bad-char                       dep-info written=True   <- MUST-FIRE controls hold
  unterminated-string                              dep-info written=False
  unterminated-comment                             dep-info written=False
  unbalanced-brace                                 dep-info written=False
  unclosed-raw-string                              dep-info written=False
  bad-utf8                                         dep-info written=False
  shebang-ish (binary content)                     dep-info written=False
  unreadable (mode 000)                            dep-info written=False
```

**The true claim is narrower: rustc emits the `.d` for failures at or after
module resolution, and not for LEXICAL or I/O failures.** Each of those seven
becomes `rep.fail("tcb-unsafe", …)`.

⚠ **The failure branch's own diagnostic (`check.py:3865`) already states this
correctly** — *"the causes that reach here are a root rustc cannot PARSE or
EXPAND"*. **So this is header-rot, `PROTOCOL.md` rule 13's exact shape: the body
is right and the summary above it is not.** Practical risk today is low — a
rung source that Verus accepts and rustc cannot lex would have to exist, and
none of the 26 has one (0 roots without a `.d`, above). Recorded so the next
agent does not re-derive it.

## m6 (minor) — §C.4. The scratch `.d` leaks

It lands at `.temp/check/depinfo/dep.<pid>.d` — **gitignored** (`.gitignore`
line 3, `.temp/`), **never inside `patterns/*/`** (`find patterns -name '*.d'`
→ empty), so neither of the task file's two worries is live. But it is removed
only at the **start** of the next call, never at the end: **82 files are sitting
there**, one per gate-run process, plus one `dep.d` with no pid — the fossil of
TASK_107's mid-task rename (its own item 3, honestly disclosed). 382 bytes each;
hygiene only.

---

## §D — the published claim that moved

### D.1 ✅ TASK_107's attribution is CONFIRMED, and its item 5 is CLOSED

**First, from the artefact alone.** In the shipped `synthesis/outward_ir.json`
the whole of each of the four misses is **one callee**:

```
  p03 small safe_tuned  outward_by_callee {0x189480: 43.0}    kex 3361
  p03 small unsafe      outward_by_callee {0x189480: 50.0}    kex 3002    43-50 = -7.00
  p03 large  "          43.0 / 50.0                                       -7.00
  p04 small  "          43.0 / 50.0                                       -7.00
  p04 large  "          43.0 / 50.0                                       -7.00
  p04 small/large R5-R4  50.0 / 50.0                                       0.00  <- the two that went the other way
```

`0x189480` is `__memset_avx2_unaligned_erms`. Every number in TASK_107's
row-by-row table falls straight out of this, including the two `falseLIC → hit`
flips.

**Second, the 32-pad question item 5 left open.** `.temp/r114/d1_phase_attrib.py`
sweeps the environment and reads the per-call memset term of each rung:

```
  pad=  0 bytes=3290  R3 memset=50.00  R4 memset=50.00   R3-R4 = +0.00
  pad=  4 bytes=3294  R3 memset=50.00  R4 memset=50.00   R3-R4 = +0.00
  pad=  8 bytes=3298  R3 memset=50.00  R4 memset=43.00   R3-R4 = +7.00
  pad= 12 bytes=3302  R3 memset=50.00  R4 memset=43.00   R3-R4 = +7.00
  pad= 16 bytes=3306  R3 memset=43.00  R4 memset=43.00   R3-R4 = +0.00
  pad= 20 bytes=3310  R3 memset=43.00  R4 memset=43.00   R3-R4 = +0.00
  pad= 24 bytes=3314  R3 memset=43.00  R4 memset=50.00   R3-R4 = -7.00
  pad= 28 bytes=3318  R3 memset=43.00  R4 memset=50.00   R3-R4 = -7.00

  MUST-FIRE: a rung's memset term moved: True   R3 [43,50]  R4 [43,50]
  R3-R4 support: [-7.0, 0.0, 7.0]
```

⚠ **The mechanism is visible: each rung's memset term takes {43, 50}
independently, and the two rungs' phase boundaries are offset by 8 bytes**, so
the DIFFERENCE takes `{−7, 0, +7}` with support 2/4/2 over eight pads.

> ✅ **ATTRIBUTION CONFIRMED. The published `4 real / 139 spurious` is ONE DRAW.**
> The same tree re-emitted from a shell 8 bytes different reads `0 real / 143
> spurious`, and from another `4 real` with the opposite sign. ⚠ **The `4` is
> not a standing figure and should not be quoted as one** — `results/synthesis.md`
> already marks the rows `‡` and says so in prose, so the file is honest; **the
> number in the table is still a draw.**

### D.1 second-order — does any published sentence still assert the pre-move version?

`results/synthesis.md`: **no.** Line 194 corrects it explicitly and 22 `‡`
markers carry it.

⚠ **`.memory/03-measurement.md` does, and it contradicts itself.**

* **line 1395** — ```|corr| <  2.00    120 rows    0 real / 120 spurious   <- nothing real hides below the floor```
* **lines 2603–2605** — *"the `< 2.00` band's claim that "nothing real hides below the floor" **is still false**"*

Line 1395 sits inside a block that is honestly dated (*"Against a fixed truth
threshold, 176 rows"*), but the trailing comment is the retracted adjective with
no marker, in the layer `CLAUDE.md` calls authoritative. **Manager-only; one
annotation.**

Two latent copies, both correctly dated and neither published today:
`synthesis/synthesize.py:229` (comment) and `:931` (the **fallback** text that
renders into `synthesis.md` *only when the sidecar is absent*, and would then
print `120 rows, 0 real` where the live line prints `143 | 4 | 139`), plus
`synthesis/outward_ir.py:13` (docstring).

### D.2 ⚠ NEITHER of TASK_107's item-7 corrections has been landed

Checked at `e6a372e`. `.memory/00-environment.md` was touched at `ccf46b1`
(*"The superseded Miri paragraph said 'Owed: pin the seed'"*) — **which struck
the remedy and left the refuted premise.**

**(a) `.memory/00-environment.md:601–604`, verbatim, unannotated:**

> **This is a live gate defect, not a curiosity.** The **same source** is clean
> under `-Zmiri-seed=0` and `-Zmiri-seed=2` and reports **UB** under
> `-Zmiri-seed=1` and `-Zmiri-seed=3`.

TASK_107 measured seeds 0..11 agreeing. ⚠ **My M3 goes further: the seed is not
the variable at all, and this sentence should not be replaced by a
seed-independence claim either — the honest replacement names the ENVIRONMENT.**
Cost: a `.memory/` edit, nothing else.

**(b) `patterns/p42-goto-cleanup/spec.md`, `miri.blocked_reason`, final
sentence:**

> ⚠ AND READ THE MIRI ROW NARROWLY: `harness/check.py` passes no `MIRIFLAGS`
> and no `-Zmiri-seed`, and `.memory/00-environment.md` records that Miri's
> alignment check is SEED-DEPENDENT, so a green row is `no UB at whatever seed
> ran`.

⚠ **Cost, since the task file asks:** that sentence is **inside the
`slb-contract` fence**, so editing it moves `contract_sha256`
(`437ae31512cf250a…`). `results/tables/p42-goto-cleanup.md:67` cites
`contract 437ae31512cf`, so **stage 9 will then report the table STALE and FAIL
the gate.** The loop is **three commands, not one**: edit `spec.md` →
`harness/report.py p42` → `harness/check.py p42`. **No re-measure**
(`spec.md` is not in `measure.py::measurement_sources`).

⚠⚠ **And note B2.3 before doing it:** re-running `check.py p42` from a shell in
the slow state will BLOCK `adversarial-wincap.bin` and change the record's
verdict to PASS-WITH-BLOCKED-ROWS for a reason unrelated to the edit.

---

## §E — the structural questions

### m8 (minor) — stage 9 `MISSING`'s stated fix cannot work on the case it names

The diagnostic (`check.py:7417–7422`) says:

> Fix: `harness/report.py pNN`. **It renders FROM `results/gate/<pattern>.json`**,
> which this run writes even if the verdict is FAIL, so run it after this run
> and gate again.

**`report.py` does not render from the gate record.** `report.py::main` calls
`load(pid)` first, and `load` requires `results/pNN-*.json` — **`measure.py`'s**
record, discriminated by carrying a `cells` list. The gate record is read only
by `read_gate_audit`, for the stage-0b audit section. Measured:

```
$ python3 harness/report.py p99
report.py: p99 matches [] in results/
```

⚠ **So on the case the diagnostic is explicitly about — a brand-new pattern's
FIRST gate run — the two-command loop deadlocks** until `measure.py pNN` has
also run, which is the full matrix the docstring says costs nothing here. On the
`STALE`/`UNPINNED` cases the measurement record already exists and the
two-command claim is correct.

**Is the ergonomic cost correctly judged as small?** In practice yes — it is
zero if no 27th pattern is built, and the two live verdicts are unaffected. **But
the fix instruction is wrong, and a wrong fix instruction is the thing a reader
trusts instead of checking.** One-line edit to the message.

### m8b — is `check_control_json_pins`'s SHOUT visible to a reader?

**No.** `UNPINNED` appears in exactly two places, both inside one JSON file:
`results/gate/p23-partition.json`'s `controls_json` and its `loud[1]`. It is in
**no** human-readable artefact:

```
grep -rn "UNPINNED|controls_json" results/tables/ results/synthesis.md harness/report.py synthesis/*.py
  -> (no output)
```

`harness/report.py` reads neither `loud` nor `controls_json` nor
`published_table`. **33 shouts across the 26 records are rendered nowhere.**

⚠ **So the judgment is: the check CAN fail and DOES fire — it is not a control
that cannot fire — but its output goes to a key nobody renders, which is one
level up from the `results/tables/` gap stage 9 was built to close.** It is
recoverable from a committed file, so `minor`, not `major`. ✅ **Coverage is
complete**: `patterns/*/controls/*.json` is exactly one file tree-wide and the
stage sees it; `find patterns -name '*.json' -not -path '*/controls/*'` is empty.

### m9 (minor) — §E.3. Two more copied `check.py` constants, in the same file

`harness/limbs.py:69–70`:

```python
TWIN_PREFIX = "slb_twin_"
TWIN_CFG = "slb_twin"
# ⚠⚠ **IMPORTED, NOT COPIED -- and it was a COPY, and the copy was WRONG.**
...
import check as _check
TWIN_BANNED = _check._TWIN_BANNED
```

⚠ **The two copies sit immediately ABOVE the comment block explaining why copies
drift**, and duplicate `check.py:3405–3406`. They agree today (verified by
import), so this is latent — but it is the same class as the entry on
`.memory/03-measurement.md`'s controls list that TASK_107 fixed, in the same
file, two lines away, and the fix was applied to one of three. `is_trusted` and
`verus` are already handled correctly (imported / re-derived-with-a-reason).

✅ **The wider sweep is clean**: `limbs.py` is the only module that imports
`check`, and the only other cross-file duplicate I found is `VALGRIND`'s path in
`measure.py:47` and `outward_ir.py:109` — a filesystem path, not a rule, and it
cannot silently under-report.

---

## ✅ Clean negatives — named attacks that did NOT land

Worth as much as the findings, and they stop the next agent re-running them.

1. **`tuning_vars`'s prefix set is NOT where the rule breaks — the ENVP
   PERMUTATION arm holds exactly.** Four envp orders (as-inherited / sorted /
   reversed / rotated), `bytes=3280` in all four, marginal `3059.00` in all
   four. This is the arm the task file called the sharpest, and it is a null.
2. **Nor does value content outside the prefix set.** Six variants
   (`z`-filler vs `Q`-filler, two `LANG`s, two `TZ`s): four `(bytes,
   tuning_vars)` groups, **0 with a split marginal**. `LANG`, `TZ` and value
   bytes do not move p03's marginal at fixed length and fixed count.
3. **A `#[path]` reached through a `macro_rules!` argument at TOP LEVEL is
   caught** (N8), by dep-info. So is a **SYMLINKED** leaf (N9). Both were
   candidate 14th routes and both are closed.
4. **`--emit=dep-info` did NOT fail on any of the 26 patterns' roots**, and
   dep-info adds no file the regex misses on the shipped tree — TASK_107's
   census reproduces exactly under an independently written script.
5. **Miri's unseeded address assignment IS deterministic** across six launches
   at a fixed environment, at the full address rather than two bits. The half
   of TASK_107's claim I attacked hardest is the half that stands.
6. **The Miri base-address RESIDUE does not explain the 4.6×.** 43 environments
   searched, 15 of them drawing `base % 4 == 3`; the second one timed is fast.
   ⚠ **Do not chase the address residue.**
7. **The p42 slow state is not a cold-cache or first-run artefact** — `b2`'s
   fourth run reproduced it at 347.4 s after two fast runs.

---

## What I did NOT do, and what I am unsure about

1. **I did not run `check.py`, `build.py` or `measure.py`** (task constraint;
   `TASK_113` was reading `results/gate/`). Everything is `check.py` imported as
   a module and driven on synthetic trees. **Two things can therefore only be
   settled by a real gate run and are follow-ups, not findings:** whether
   `check.py p42` re-run today actually records the blocked row (B2.3 predicts
   it from the same command line at the same timeout, but the prediction is
   mine); and whether the union's four missing routes produce a green gate
   end-to-end (`c2_confirm_n7av.py` shows the file set is empty and the tokens
   invisible, which is the whole of the mechanism, but the gate itself was not
   run).
2. **No mechanism for the 4.6×.** I have the trigger localised to the
   environment block and away from `MIRIFLAGS`, and the one correlation I found
   is dead by measurement (`b6_addr_search.py`). ⚠ **I also cannot say WHICH
   environments are slow** — one in 15+ probed, and the one that is happens to
   be the ambient one. A characterisation needs a wide sweep, which is a task.
3. **The blast radius across the other 21 patterns is still unmeasured** (B2.4).
   At 75–345 s per row it is a task.
4. **`p04`, `p38` and `p46` are unprobed on the envp-COUNT axis.** I measured
   the count effect on `p03` only; the pad-length effect is documented on the
   same seven cells, so I expect the count effect wherever the length effect
   lives, but I did not measure it.
5. **I did not check whether `bytes + 8*nvars` is a SUFFICIENT pin** — only that
   `bytes` alone is not. `argv` is a third term (§A.3) and there may be others;
   the honest posture is that the record names the draw approximately.
6. **`b1 scale`'s null is on a synthetic Vec-heavy program, not on a pattern.**
   It shows the effect is not universal; it does not bound it.

---

⚠ **PROTOCOL rule 2's running count: 414 + 6 on this branch.** Reconciliation is
the manager's job, not mine; `TASK_113` was launched from the same 414 in
parallel. The six, each with an arm that fired:

1. **§A's rule** — *"same `bytes` and same `tuning_vars` ⇒ the marginal must
   match EXACTLY"* — **falsified**, ±7 at `bytes=3520`, `tuning_vars={}`, with
   the period-4 mechanism measured.
2. **§A's diagnosis** — *"`tuning_vars` is the incomplete half"* — **refuted**;
   two clean negatives say the prefix set holds and `bytes` is the lossy term.
3. **§B's premise** — *"the trigger is the variable's PRESENCE"* — **refuted**;
   the `miri` driver never reads `MIRIFLAGS`, and a decoy variable is
   indistinguishable from it.
4. **§B's landed numbers** — *"unset 74 s, `MIRIFLAGS=''` 340 s"* — **reversed**,
   three repeats each way, plus a third independent slow measurement.
5. **§B's family-2 reading** — *"the live variable is unseeded-vs-seeded"* —
   **confounded**; a decoy variable flips the verdict identically.
6. **§C's `Union 13/13`** — **four routes the union misses**, with both controls
   holding.

**The manager's three named doubts, answered:**

1. ⚠ **It did need reviewing** — two blockers, and one of them (B2) reverses a
   published pair of numbers that changed the gate's Miri configuration
   tree-wide. **This does not make TASK_107 a bad report: it is the report whose
   own disclosures told me exactly where to dig, and four of my six deltas start
   from a sentence it wrote against itself.**
2. ⚠ **§A was a good pick and §B mattered more.** §A's rule is false and the
   correction is one integer. §B's landed decision was taken on a two-state
   variable nobody had identified, and it currently selects the state that
   blocks the row it was chosen to unblock.
3. ⚠⚠ **"The instrument is fine, stop polishing it" is NOT the honest answer.**
   The instrument has a comparison rule that is false in 26 records, a Miri
   configuration whose result is a coin flip on the invoking shell, and four
   open routes. ✅ **But none of that invalidates a published `Ir`** — every
   defect is in the *reproducibility metadata* and the *latent* detectors, not
   in the measurements. **The proportionate response is a small correction task
   (B1's one integer, m7's two sentences, m8's one message, m9's two lines), and
   a decision about B2 that is a genuine research question rather than a fix.**
