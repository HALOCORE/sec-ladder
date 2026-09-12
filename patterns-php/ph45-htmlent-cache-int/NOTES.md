# ph45-htmlent-cache-int — NOTES

## 0. Rule 6 disclosure

`spec.md`'s `slb-contract` block:

```
as first written   d45a9142d17cd103f0272dab829bd29d065fd7c00a2fd539d6e035a3b04d6c80
after the measure  2c878709c17c3569f657dcaa4092e50b85214e76ed602043a365be55fe123f93
as shipped         d3cb3219ef3ef5c84a7a82601adbca76dcc70fef090c9c8dd5fef9114ff1186f
```

⚠⚠ **THE HASH MOVED TWICE AND HERE IS THE WHOLE DIFF, FIELD BY FIELD.**

1. **`identity: []` → one entry** (`unsafe` vs `verus`, `differ` at O0 and at
   O3, with the measured instruction counts in its `why`). `check.py` stage 8
   REQUIRES an `unsafe`-vs-`verus` identity row at O3 before it will evaluate
   the Miri policy (`check.py::check_miri`), so an empty list could not ship; and a pin
   is a claim about a MEASUREMENT, so it could not honestly be written before
   one existed.
2. **`verus.axioms` and `verus.unsafe_justifications['verus.rs']['ent_table']`
   added**, both because the FIRST GATE RUN ASKED FOR THEM by name —
   `[proof-axiom]` counted one body-less trusted declaration against a declared
   zero, and `[tcb-unsafe]` refused an `external_body` item with no `requires`
   and no justification. Both are declarations of things that were already true
   of `verus.rs`; neither changed a line of code.
3. **`verus.items` re-derived** after `verus.rs`'s free `emit` was renamed to
   `emit_result`. ⚠ That rename was ALSO the first gate run's doing and it took
   out FIVE stages at once — `proof-rule2`, `clause-mut`, `req-mut`, `twin` and
   `contract-source` all failed with `vparse: duplicate item name(s): emit at
   lines [911, 1258]`, because `Ctx::emit` and a free `emit` share a name that
   no scope distinguishes and `vparse.unique_names` RAISES rather than picking
   one. The item set is otherwise unchanged: 46 items before and after.
4. **`idiom.forbidden` rewritten and `verus.twin_justifications` added**, both
   demanded by the SECOND gate run. ⚠⚠ **The `forbidden` rewrite is the one
   worth reading and it is a mistake this row made and the gate caught**: the
   entries used backticks freely in their explanatory prose, and
   `harness/check.py::spelling_matches` treats **every** backticked span in a
   `forbidden` entry as a spelling that must be ABSENT FROM EVERY RUNG OF THAT
   LANGUAGE. So `` `int` ``, `` `size_t` ``, `` `cache` ``,
   `` `mbfl_filt_conv_html_dec` `` and `` `filter->status` `` — all of them
   quoted only to be talked about — became nineteen refusals across six files,
   and `` `void *opaque` `` refused `c/kernel_hardened.c` for containing its own
   fix. The rewrite backticks **only** tokens checked absent from all six rungs
   by grep beforehand (`intptr_t`, `i64`, `memcpy`, `memmove`, `copy_within`)
   and puts everything else in plain prose. ⭐ **The lesson is the
   named-spelling standard's own, arriving from the other side**: it says the
   POLARITY and the SCOPE of a quoted span live in the entry's English — and
   what this row learned is that so does *everything you did not mean to pin*.
5. **`idiom.required` rewritten for the same reason**, and this half the gate
   did NOT catch — `required` cannot fail the gate by design
   (`.memory-php/02-ladder.md`). As first written it made **34** (spelling ×
   rung) obligations of which most were prose tokens like `` `why` ``,
   `` `:161` `` and `` `controls/warnings.py` ``, satisfied by nothing and
   meaning nothing. Rewritten it makes **21**, of which **15 are satisfied** and
   the six that are not are exactly the three C spellings against `c/kernel.h`
   (a declaration header with no code in it) and against `c/kernel_hardened.c`
   (which must NOT contain them — removing those three casts is the whole of
   `e8901dc17087`, and the entries' English says so). ⭐ **Every number in the
   declaration is now explainable**, which is the state `ph29`'s open item 51
   was about from the other direction.

**Nothing else moved across either step**: no `required`, no `forbidden`, no
`why`, no `requires`, no `ensures`, no `provenance`, no `driver`, no `collapse`.
⚠ All three fields that did move are ones the GATE supplies or demands, and
writing any of them earlier would have been a guess dressed as a declaration.

⚠ **Computed the way the gate computes it** — `check.py::read_contract`'s
``re.search(r"```slb-contract\s*\n(.*?)```", txt, re.S)``, whose capture **keeps
the newline before the closing fence**. The obvious spelling hashes one byte
less and gives a different number for every pattern in the tree
(`PROTOCOL_PHP.md` §E).

⚠⚠ **AND THE DISCLOSURE IS WEAKER THAN THE RULE ASKS FOR, SO HERE IS EXACTLY
WHAT IT COVERS.** `PROTOCOL.md`'s definition of done rule 6 says *"record it the
moment you first write it, before building any cell"*. `spec.md` was written
**after** the six rungs existed and after they had been built by hand in
`.temp/php36/bin/` and driven against `model.py` — it could not have been
written earlier, because its `verus.items` block is 46 items derived from
`verus.rs` by `vparse` and its `obligations` figure is a measurement. What the
hash above does pin is that **no `required`, `forbidden` or `why` moved after
the first `harness-php/gate.py` run**, and that the one field that did move is
the one named above. ⚠ **The `git show HEAD:` form of the check is
VACUOUS on a new row** — a row lands in one commit, so on a clean tree it always
prints nothing and always looks like it passed (`PROTOCOL.md` rule 6's own
warning). The hash above is the only evidence, and it is weaker evidence than it
would be on an existing row. Said here rather than elsewhere because a false
disclosure is worse than the stale thing it describes.

---

## 0a. The gate verdict, read out of the record

```
$ python3 -c "import json; d=json.load(open('results-php/gate/ph45-htmlent-cache-int.json')); \
              print(d['verdict'], d['failures'])"
PASS-WITH-BLOCKED-ROWS []
contract_sha256  d3cb3219ef3ef5c84a7a82601adbca76dcc70fef090c9c8dd5fef9114ff1186f
```

⚠ **`PASS-WITH-BLOCKED-ROWS` and not bare `PASS`, and the one blocked row is
named**: stage 5c-twin certified **2 twins for 3 trusted items**, with
`verus.rs:ent_table` justified away. The gate prints that justification in
every verdict, which is the point of the mechanism. ⓘ It is the same verdict
`p01-array-sum` (the PAT template), `p35-tagged-union` and `ph00-smoke` carry.

⭐ **One alternative was considered and does not work**, recorded so nobody
re-derives it: making `ent_table` an ordinary verified function and threading
the table through every spec function as a `Seq<Ent>` parameter would remove
BOTH the trusted item and the axiom — but `kernel`'s `ensures` would then have
to read `r == html_fold(ent_table()@, …)`, and a Verus `ensures` **cannot call
an exec function**. The uninterpreted `tbl()` is the way round that, and the
trusted item is its price.

⚠ **One other gate note, resolved rather than suppressed**: at `O0 / isolated`
the `verus` cell's `kernel` symbol has no back edge, because `kernel` is split
from `run` (§11) and at `-O0` nothing is inlined. The gate says so itself —
*"the loop is one DIRECT CALL away … structural anti-collapse is satisfied by
the callee"* — and stage 3b is what establishes the work happened. No
performance claim in this file rests on an `O0` row.

## 0b. ⚠ One committed file outside the row moved, and it is not mine to want

`results-php/preflight/_norow.preflight.json` gained **188 lines**. That is
`PROTOCOL_PHP.md` §E's *"a FAILING run grows a COMMITTED file"* firing exactly
as documented: the mid-task `gate.py --tool measure --check-stale` that reported
`2 STALE` (my own `model.py` citation fix) is a failing run, and `gate.py`
appends its preflight record before running the tool. **Nothing in `harness/`,
`common/`, `patterns/`, `results/` or `pilot/` was touched**, and the only other
paths that moved are this row and its four `results-php/` records.

---

## 1. What the row is

`int cache;` (`ext/mbstring/libmbfl/mbfl/mbfl_convert.h:49`) is a 32-bit field.
`ext/mbstring/libmbfl/filters/mbfilter_htmlent.c:161` puts a heap pointer in it.
`:178` and `:249` take it back out through `(char*)`, which sign-extends; `:169`
hands it to the deallocator; and ten lines dereference it.

⚠ **The catalogue says "five lines, two functions". It is fifteen tarball lines
across four**, and the enumeration is `TASK_PHP_034_REPORT` §2.1, re-derived
here: `:49` the declaration, `:161` the store, `:169` the free, `:178` and
`:249` the two casts back, and `:183 :189 :190 :193 :202 :215 :216 :223 :230
:236 :253` the dereferences. **`:249` is cited by nobody** — not `index.csv`,
not `CATALOGUE.md`, not `ADJUDICATION_001.md` — and it is one of the four sites
`e8901dc17087` rewrites, so a row built to the catalogue's five lines would not
be a faithful pre-image for its own R1h.

---

## 2. Why the row places its work buffer

**Read `c/arena.h`'s header first; this is the summary.**

`:167`'s `if (filter->cache)` rejects only the value zero, so `:169`'s free runs
on **every** filter destruction, for **any** input. On a 2026 PIE process the
heap is at `0x55…` and `(int)p` loses 16 bits on every allocation. Measured:

```
$ python3 patterns-php/ph45-htmlent-cache-int/controls/native.py
  hello, world       -> SIGNAL 11        <- NO `&` IN IT AT ALL
  &#20013;           -> SIGNAL 11
  &amp;              -> SIGNAL 11
  x&amp;y &#65; z    -> SIGNAL 11
-> 60 of 60 runs faulted
```

⭐ **So the forcing mechanism this row needs is one that makes the BENIGN case
work, not the adversarial one** — which is the opposite of what a forcing
mechanism usually does, and it is the finding that decided the row's design
(`TASK_PHP_034_REPORT` §5.4, reproduced above rather than transcribed).
Without it there is no benign corpus, `check.py` stage 2's checksum agreement
can never be reached, and the row cannot be measured at all.

`c/arena.h` maps `LO` with `MAP_32BIT` and `HI = LO + 2³²` with
`MAP_FIXED_NOREPLACE`, **once, from `main.c`, outside the measured loop**.
Verified under all eight `{gcc, clang} × {-O0, -O3} × {-DSLB_ISOLATED, -flto}`
combinations (`.temp/php36/logs-02-placement.log`): `LO` always lands in
`[0x40000000, 0x42000000)` and `(int)HI == (int)LO` exactly.

⭐ **`LO` is not a convenience; it is 2004.** A non-PIE `php` binary's `brk`
heap sat below 2³², `(char*)(int)p == p` **exactly**, the implementation-defined
conversion is the identity, and that is precisely why this shipped and was
filed as *a compiler warning*.

---

## 3. Tier — `narrowed`, and the argument is in `spec.md` where it can be attacked

`provenance.divergences_note` carries it in full. The short form:

* **not `verbatim`**, because §A1 clause (b) wants a `why` ending in *"no
  semantics"* and the allocator substitution's cannot — the address it returns
  **is** the mechanism;
* **not `modelled`**, because the mechanism is *lifted*, character for
  character, along with all four decode functions at `[155,258]`; what is
  substituted is the allocator **behind** it, and upstream that is a
  **function-pointer table entry** which PHP itself rebinds at
  `mbstring.c:764`;
* **`narrowed`**, because two wrappers come off — `mbfl_buffer_converter_feed`'s
  memory device and `mbfl_convert_filter_new`'s vtable dispatch — which is
  §A1's own definition.

⚠⚠ **The strongest argument against, stated because a reviewer should weigh
it**: the window's `place` word has **no pre-image in PHP at all**. No input
chooses where `emalloc` puts a block, so R1's behaviour at `place != 0` is not
PHP's behaviour on any input — it is PHP's behaviour on a *different platform*.
The counter is that every **measured** window is `place == 0`, that this is the
platform the code shipped on, and that the other placements live in
`adversarial-*.bin` where the gate **records** rather than requires.
⚠ **A tier is a cost, never a filter**: if a reviewer reads this as
precedent-stretching, the row is `modelled` and nothing else about it changes.

---

## 4. §F9 — the kernel-overlap number, and what I think of it

```
$ python3 harness-php/provenance.py ph45-htmlent-cache-int
  per-span overlap: span0 91% (42/46), span1 86% (12/14), span2 0% (0/4),
                    span3 0% (0/253), span4 0% (0/10), span5 0% (0/22),
                    span6 0% (0/2), span7 23% (6/26), span8 40% (2/5),
                    span9 12% (2/17), span10 0% (0/7), span11 0% (0/17)
  kernel overlap 15% (61/419 excerpt lines in kernel.c, kernel.h,
                      kernel_hardened.c)  tier=narrowed is expected to clear 25%
  ⚠⚠ THE OVERLAP IS BELOW WHAT tier=narrowed LEADS A READER TO EXPECT
  ⚠ 1 preprocessor condition(s) this heuristic CANNOT evaluate:
    ['#ifndef PH45_KERNEL_H']
```

**What I think of it, since §F9 moves that judgement to a person:** ⭐ **the
number is 15 % and the row's C is a near-verbatim lift, and both are true.**
The decomposition says why, and it is the whole answer:

| | |
|---|---|
| **span0** — `mbfilter_htmlent.c:155-258`, the four decode functions | **91 %** (42/46) |
| **span1** — `mbfl_convert.h:40-54`, the struct with the defect | **86 %** (12/14) |
| **span3** — `html_entities.c:37-290`, the 251-entity table | **0 % (0/253)** |

**253 of the 419 excerpt lines are the entity table, and the heuristic cannot
see it**, because it reads `c/kernel*.{c,h}` and the table is in
`c/mbfl__html_entities.h` — flattened under `PROTOCOL_PHP.md` §B3's spelling 1,
which is what the audit wants. Drop the two `html_entities` spans and the number
is **61/162 = 38 %**, comfortably over the 25 % a `narrowed` row is expected to
clear.

⚠ **I did not rename the file to `c/kernel_entities.h` to make the number go
up**, although `kernel*` is the glob and the table genuinely is a kernel source.
The honest name records the table's provenance, and a number moved by a file
name is not a number about the code. ⚠ **And the number's own caveat applies
here with force**: it measures TEXT IN A FILE, not code in the benchmark
(`TASK_PHP_005` F-4), so 91 % on span0 is not evidence that those lines are
compiled either. What says they are compiled is `controls/warnings.py` —
`-Wpointer-to-int-cast` fires at `kernel.c:191`, which is `:161`, in every one
of the eight cells gcc and clang build.

---

## 5. ⚠⚠ The measured `u64` carries no evidence that the defect exists

At `place == 0` the truncation is the identity, so **R1 and R1h are
bit-identical** on every measured window:

```
$ python3 patterns-php/ph45-htmlent-cache-int/controls/oracle.py
A. small.bin: R1 == R1h on 32 of 32 windows
```

**That is `check.py` stage 7h's requirement being SATISFIED, not a defect** —
and it means the catalogue's proposed oracle, `u64 = decoded bytes + (allocs,
frees)`, **measures nothing on this row**.

⭐⭐ **This is `ph64`'s lesson arriving on a second row, and that is now twice.**
`ph64`'s catalogue oracle was a fold of the ids its walk invoked, and a freed
39-byte element goes into `AG(cache)[5]` with its payload intact, so the fold was
bit-identical between its two rungs too. Two rows, two different mechanisms, the
same failure of the catalogue's proposed oracle — **a catalogue entry's `benign`
line is a proposal and not a measurement, and the first thing a build task
should do with one is try to falsify it.**

---

## 6. The oracle, and the row at BOTH placements

`controls/oracle.py`, on one text — filter A gets `x&amp;y`, filter B gets
` &#65; `, interleaved byte by byte:

| `place` | regions | R1 vs R1h | alloc/free/dfree/wfree/leak (R1) |
|---|---|---|---|
| **0** | LO / LO | **identical** — the must-**not**-fire control | 2/2/0/0/0 |
| **2** | LO / HI | `&amp;` → **65** where R1h gives **38**; u64 differs | 2/**1**/**1**/0/**1** |
| **1** | HI / LO | the mirror: the same u64, the same 65 | 2/**1**/**1**/0/**1** |
| **3** | HI / HI | **decode CORRECT**, u64 differs on the allocator only | 2/**0**/0/**2**/**2** |

R1h is 2/2/0/0/0 at all four.

⭐⭐ **The mechanism, because `PROTOCOL.md` rule 12 wants the mechanism and not
the number.** Under truncation A's and B's work buffers are the same 17 bytes.
A writes `&` at index 0 and `a` at index 1; B then writes `&` at 0 and `#` at 1,
overwriting A's `a`; B writes `6` and `5` at 2 and 3, overwriting A's `m` and
`p`. When A's `;` arrives, `:190`'s `buffer[1]=='#'` is now **true**, so the
*named* entity `&amp;` takes the **numeric** arm, `:193` reads `6` and `5`, and
A emits **65**. **`&amp;` decodes to `A`.** No crash, no sanitizer diagnostic,
no allocator damage — filter B's answer delivered to filter A, silently.

⚠ **The must-NOT-fire control is the load-bearing half.** `place 0` and `place
2` carry byte-for-byte the same text and the same interleaving; the only thing
that moves is where B's buffer lives. Without it the divergence could be the
interleaving, and nothing in the number would say which. It ships as an input —
`inputs/adversarial-noalias.bin` — so the gate records it beside the others.

⚠ **`TASK_PHP_034_REPORT` §6.4 measured this as `&amp;` → 674 with ITS
interleaving.** §2.4 of the build task says to re-derive it, and re-deriving it
gives **65**: the value is a property of which bytes the other filter happens to
have written, and 674 came from `('m'-'0')*10 + ('p'-'0')` where 65 comes from
`('6'-'0')*10 + ('5'-'0')`. The *mechanism* is identical and the *number* is not
transferable; that is worth knowing before quoting either.

---

## 7. Size — the mechanism, the extraction, and the table

| | |
|---|---|
| the **mechanism** | **15 tarball lines**, four functions (§1). The catalogue says five and two. |
| the **extraction** | **548 raw / 504 code lines** over twelve spans |
| of which the **table** | **254**, and it is `const` data with no control flow |
| **LOGIC** (extraction − table) | **294 raw / 250 code** |

⭐ `ph64` was billed at 8 lines and measured ~140; this one is billed at 5 and
measures **~250 lines of logic plus a table**. The table is the cheap part, so
the real cost is closer to `ph64`'s than the raw number suggests — and it is
what makes §4's overlap number unreadable without its decomposition.

---

## 8. The measurement

### 8a. ⚠⚠⚠ READ THIS BEFORE ANY NUMBER BELOW: `kernel_exclusive_ir` SEES ONE TENTH OF THIS ROW

`measure.py` sums only symbols matching `(^|::)kernel($|[^A-Za-z0-9_])`. On this
row **the filter body is a separate symbol in every rung**, because the C
reaches `mbfl_filt_conv_html_dec` through `filter->filter_function` — a call
through a POINTER, which neither gcc nor clang inlines — and the four Rust rungs
carry `#[cfg_attr(slb_isolated, inline(never))]` on `dec` so that they attribute
the same way (`unsafe.rs`'s header says why; left to LLVM, R5 inlined it and
R2/R3/R4 did not, which made R5's `kernel_exclusive_ir` read **76.2 M against
R4's 7.8 M** — a 10× number that was not a cost at all, only a different
denominator).

⚠⚠ **AND 44 % OF THE C's INSTRUCTIONS ARE IN glibc, WHICH LANDS IN NO COLUMN OF
THE PUBLISHED TABLE AT ALL.** Whole-program callgrind on `c-gcc-O3-isolated`,
`small.bin` (`.temp/php36/logs-05-cgbreakdown.log`), with the two hot addresses
resolved by symbol arithmetic and confirmed from their disassembly (AVX2
`vpcmpeqb` / `tzcnt`, and the binary's only libc string imports are `strchr` and
`strcmp`):

```
164,971,274 (100.0%)  PROGRAM TOTAL
 72,365,420 ( 43.9%)  glibc __strcmp_avx2   <- mbfilter_htmlent.c:202, the 251-entity scan
 58,234,254 ( 35.3%)  mbfl_filt_conv_html_dec
  9,516,720 (  5.8%)  kernel                <- THE ONLY ONE THE TABLE COUNTS
  9,405,003 (  5.7%)  glibc __strchr_avx2   <- mbfilter_htmlent.c:225
  6,287,105 (  3.8%)  ph45_output
```

**The published table's own prose already says this can happen** — *"whatever a
rung calls out to … lands in no column of this table at all"*, and *"only the
marginal is comparable across rungs"*. ⭐ This row is a worked example of it, and
the numbers below are given in **three** families, labelled, because on this row
two of them disagree on SIGN.

### 8b. The two families, `O3 / isolated`, `small.bin`

| rung | whole-program `Ir` | `kernel_exclusive_ir` | share inside `kernel` |
|---|---:|---:|---:|
| R1 `c-gcc` | 164,971,274 | 9,516,720 | 5.8 % |
| R1 `c-clang` | 163,071,853 | 8,573,224 | 5.3 % |
| R1h `c-gcc-h` | **164,902,661** | 9,516,720 | 5.8 % |
| R1h `c-clang-h` | 163,071,867 | 8,573,224 | 5.3 % |
| R2 `safe_naive` | 98,055,906 | 7,851,998 | 8.0 % |
| R3 `safe_tuned` | **79,512,064** | 7,851,998 | 9.9 % |
| R4 `unsafe` | 82,019,981 | 7,823,432 | 9.5 % |
| R5 `verus` | 82,190,705 | 7,820,432 | 9.5 % |

| comparison | **A1** (`Ir(kernel)`/call, `small`) | whole-program |
|---|---:|---:|
| **`fixed-R4 bound` = R3ship − R4ship** | **+0.37 %** | **−3.06 %** |
| R2 − R4 | +0.37 % | +19.55 % |
| R2 − R3 (what the tuning buys) | 0.00 % | +23.32 % |
| **R5 − R4 — the NULL control, true value 0** | **−0.04 %** | +0.21 % |
| R1h − R1 (the upstream fix) | 0.00 % | **−0.042 %** |
| `c-clang` − `c-gcc` (NOT a safety effect) | −9.91 % | −1.15 % |
| R3 − R1 (C vs safe Rust) | −17.49 % | −51.80 % |

⚠⚠ **THE HEADLINE DISAGREES ON SIGN BETWEEN THE TWO FAMILIES.** `R3ship −
R4ship` is **+0.37 %** in A1 and **−3.06 %** whole-program, and the mechanism is
§8a's: A1 excludes `dec`, and `dec` is where R3's lever and R4's `get_unchecked`
both live. **`R2 − R4` is +0.37 % in A1 and +19.55 % whole-program** — a 19 pp
gap on one comparison. This is `RECAP_PHP.md` open item 52 ("which statistic a
bound is quoted in is UNDECIDED across rows") arriving with a mechanism rather
than as an observation, and it is much larger here than the 0.72 pp `ph16`
showed.

▶ **What this row publishes, per `TASK_PHP_036.md` §3, LABELLED, and it is two
quantities and not three:**

> **`fixed-R4 bound`, family A1 — kernel-exclusive `Ir`, per call, `small.bin`,
> R4 held fixed by fiat: `+0.37 %`.**
> **The same bound, whole-program `Ir`, `small.bin`: `−3.06 %`.**
>
> ⚠ **There is NO pair interval**, and `min(R3 found) − min(R4 found)` is not
> the repair.
>
> ⭐ **AND SINCE `TASK_PHP_037` THERE IS A SECOND QUANTITY BESIDE IT: the
> R3-side span, whole-program, `−20.66 % .. +46.07 %`** (§8g). ⚠⚠ **Both
> endpoints of the bound above are now known to MOVE**, so read §8g before
> quoting either figure in this box as if it were tight.

⚠⚠ **AND `inside_share` CANNOT BE COMPUTED AS §3 SPELLS IT ON THIS ROW.**
§3 defines it as `(kernel_exclusive_ir / n_iters) / marginal_ir_per_call`, and
`marginal_ir_per_call` is a **whole-program slope**. The column above headed
*"share inside `kernel`"* is that ratio computed against the **whole-program
total** rather than against the slope, which is the same quantity one decimal
place coarser and is what the gate record's own numbers reproduce. On the
comparison the rule is about, `|Δ share|` between R3 and R4 is **0.0034**, i.e.
INSIDE §3's 0.02 threshold — **and the two families still disagree on sign.**
⭐ So F74's condition PASSES here and A1 is still the wrong number, which is a
result about the condition and not about this row: a small `Δinside_share` says
the two cells have the same callee *share*, and on this row **both** cells put
90 % of the work in a callee. The rule catches cells that differ; it cannot
catch cells that agree on being mostly outside.

> ⚠⚠⚠ **THE PARAGRAPH THAT USED TO CLOSE HERE SAID *"that is offered as an
> observation on one row, not as a correction to F74 — F74 is a 310-comparison
> result and this is one row with a mechanism."* THAT CAUTION WAS RIGHT WHEN IT
> WAS WRITTEN AND THE OBSERVATION HAS SINCE BECOME THE CORRECTION.**
> `TASK_PHP_037`, from `RECAP_PHP.md` F74/F80/F82.
>
> The manager took the observation up, re-ran the same probe over **366**
> comparisons, and **F74's rule is withdrawn in its published one-condition
> form** — the probe printed its own refutation, and **all six refuting
> comparisons are this row's.** The corrected rule, measured clean at **0 sign
> flips in 151 comparisons**:
>
> > **(i) `min(inside_share)` over the two compared cells must be HIGH — family
> > A must actually SEE both cells — AND (ii) `|Δinside_share| ≤ 0.02`.**
>
> ⚠ The threshold in (i) is **not tuned and six rows cannot pin it**: `> 0.3`,
> `> 0.5` and `> 0.6` all give 0 flips. Read it as *"A sees most of both
> cells"*.
> ⚠⚠ **DO NOT OVERSTATE WHAT THIS ROW DID.** It supplied the counterexample —
> one row, with a mechanism, which is exactly what the withdrawn sentence
> claimed for itself. **The 366-comparison sweep is the manager's, it is
> UNREVIEWED under `PROTOCOL.md` rule 9, and nothing here re-derives it.** What
> this row can still say on its own evidence is the sentence above the box:
> the condition passes and A1 is still wrong.
> ⚠ **Do not quote F74's one-condition form** anywhere.

### 8c. ⭐ The upstream fix is CHEAPER than the defect, and A1 cannot see it

`c-gcc-h` is **68,613 Ir cheaper** than `c-gcc` over 1,500 calls — **−0.042 %**
whole-program — and all 68,613 are inside `mbfl_filt_conv_html_dec`
(58,165,655 against 58,234,254). The mechanism: `(char*)filter->cache` loads a
32-bit field and **sign-extends** it (`movslq`); `(char*)filter->opaque` loads a
64-bit field and does not. `e8901dc17087` removes one instruction per `_dec`
call and it removes the defect in the same edit. ⚠ `kernel_exclusive_ir` is
**identical** for the two rungs (9,516,720), so A1 reports this as `0.00 %`.
⭐ It is `.memory-php/02-ladder.md`'s *"the safety check can be NEGATIVE-cost"*
on a new row and for a new reason: **not a check LLVM can drop, but a type that
needs no conversion.**

### 8d. R2 vs R3 — the tuning is worth 23 %, and A1 reports 0.00 %

`safe_tuned.rs`'s header carries the whole four-candidate search. The shipped
lever — resolving the work buffer to a `&[u8; REQ]` before the 251-entity scan —
is worth **−18.9 %** whole-program against R2, and three other candidates
including the obvious sub-slice hoist were **pessimisations**. ⚠ A1 reports the
tuning as **exactly 0.00 %**, because both rungs have the identical `kernel`
symbol and the lever is inside `dec`.

⭐⭐ **And the shipped R3 is cheaper than R4**, which is `ph16`'s F67 mechanism —
two rungs cheapest under different spellings, R3's minimum under R4's — arriving
on a second row. ⚠⚠ **`.memory-php/02-ladder.md` says F67 is n = 1 and this does
NOT make it n = 2 by itself**: `ph16`'s evidence included a mirror control (R3
given R4's signature, byte-identical to `safe_naive`) and a degenerate R4 side,
and this row has neither, because it ships no `controls/spellings.py`. What it
has is four measured R3 candidates and no R4 search at all. **Read it as a
pointer for whoever discharges this row's spellings debt, not as a second data
point.**

> ⚠⚠⚠ **THE SENTENCE ABOVE IS NOW HISTORY AND SO IS ITS STATED MECHANISM.
> `controls/spellings.py` EXISTS (§8g), AND IT REFUTES THE FIRST PARAGRAPH OF
> THIS SECTION.** `TASK_PHP_037`.
>
> The lever is **not** *"a `&[u8; REQ]` whose length is a compile-time
> constant"*. It is the **HOIST** — resolving the work-buffer base once, outside
> the 251-entity scan, instead of re-deriving it per byte compared. The array
> type contributes essentially nothing, measured **three independent times**:
>
> | measurement | whole-program `Ir`, `small.bin` |
> |---|---:|
> | shipped R3, `&[u8; REQ]` via `try_into` | **53 015.2** /call |
> | `r3_subslice` — the identical hoist as a plain `&[u8]` | **53 008.2** /call |
> | `r4_buf_slice_inline` (`&[u8]`) vs `r4_buf_array` (`&[u8; REQ]`) | **41 851.1** vs **41 844.1** /call |
>
> **Both pairs agree to 0.02 %, i.e. a TIE by this row's own 0.05 % threshold.**
> ⭐ And the third measurement is the sharp one, because the *same* pair of
> spellings is a tie on the unsafe side too: it is not an artefact of one rung.
>
> ⚠⚠ **`safe_tuned.rs`'s header STATES the refuted mechanism** — *"the bound
> LLVM gets free from the TYPE is worth more than the check it removes"* — **and
> it is NOT EDITED HERE.** `.rs` sources are in this row's MEASUREMENT digest,
> so a comment fix costs a **32-cell re-measure**; `RECAP_PHP.md` open item 53 is
> the same situation on `ph16` and its ruling is *batch it, never land it alone,
> and do it the next time the row is re-measured for a substantive reason*. ▶ The
> correction lives here, where it is free, and the `.rs` comment is flagged for
> the manager.
> ⚠ **What the header gets RIGHT and this correction does not touch**: the
> obvious `&mut [u8]` sub-slice hoisted per `dec` call really was **+6.9 %
> worse**, and three of its four candidates really were pessimisations. The
> refutation is about WHY the shipped one wins, not about whether it wins.

### 8e. What is NOT a safety effect on this row

* **`c-clang` beats `c-gcc` by 9.91 % in A1 and by 1.15 % whole-program.** Two
  compilers, one language, no safety.
* **The C spends 49.6 % of its instructions in glibc's AVX2 `strcmp` and
  `strchr`; the Rust rungs spend 0 % there** — they spell `strchr` as a range
  predicate (a declared divergence, demonstrated equal over all 256 byte values
  by `controls/strchr_equiv.c`) and `strcmp` as a byte loop. ⚠⚠ **So the
  C-vs-Rust column on this row is mostly a measurement of glibc**, and
  `R3 − R1 = −51.80 %` must not be read as *"safe Rust is twice as fast as C"*.
  It is *"a scalar range test beats a function call into a vectorised
  `strchr` when the haystack is 63 bytes and the call is made once per input
  byte"*. The row states it rather than publishing the number bare.
* **R5 − R4 = −0.04 % (A1) / +0.21 % (whole-program).** A codegen coin flip; the
  `identity` pin's `why` says so. **The proof costs nothing at run time.**

### 8f. ⭐⭐ THIS ROW IS THE TREE'S SENSITIVITY CALIBRATION FOR FAMILY A, AND IT DID NOT KNOW IT

`TASK_PHP_037`, re-derived from `results-php/ph45-htmlent-cache-int.json` and
`results-php/ph64-callback-frees-cursor.json` alone (`.temp/php37/sens.py`,
`.temp/php37/sens.log`). ⚠ **The reasoning below is the manager's (F82) and is
UNREVIEWED; the arithmetic is re-derived here rather than transcribed.**

F74 settled which statistic this programme should headline **by a null
control** — `identity` pins R4 and R5 byte-identical on most rows, so
`verus − unsafe` has a known true value of 0, and family A reads `0.0000 %`
everywhere. ⚠⚠ **A null control is ONE-SIDED: a statistic hard-wired to `0`
would ace every null in this tree.** Nothing had measured whether family A can
*resolve* a difference it ought to see.

⭐ **This row supplies that half for free, because it pins `differ`.** R4 and R5
here are genuinely different programs whose `kernel` symbols differ by a
**known** static count, so family A has a **predicted nonzero** value:

| row | input | `n_iters` | Δnopad | Δ(A) | `exec_rate` | A1 |
|---|---|---:|---:|---:|---:|---:|
| **`ph45`** | `small.bin` | 1 500 | **−2** | **−3 000** | **1.0000** | **−0.0383 %** |
| **`ph45`** | `large.bin` | 200 | **−2** | **−400** | **1.0000** | **−0.0054 %** |
| `ph64` | `small.bin` | 1 500 | −1 | −764 | 0.5093 | −0.0067 % |
| `ph64` | `large.bin` | 200 | −1 | −102 | 0.5100 | −0.0009 % |

where `exec_rate = Δ(A) / (Δnopad × n_iters)`.

▶ **Family A resolves a two-instruction static difference to the instruction, on
two inputs 7.5× apart in call count.** `−3 000` over 1 500 calls and `−400` over
200 calls are both exactly `2 × n_iters`.

⚠⚠ **`exec_rate` of exactly `1.0000` is *too clean*, and too-clean is the only
warning F52 gives — so `ph64` is the control on `ph45` and it must be read
beside it.** If the arithmetic were feeding itself, every row would read `1.0`.
`ph64`'s extra instruction sits on a **conditional** path, so its rate is
**0.51**, and its two inputs — different sizes, different call counts — agree on
that rate to **0.0007**. Three fields, two files, no fitting.
⚠ **`ph45`'s rate is 1.0 for a reason that is stated rather than assumed**: both
of its two instructions are on the unconditional path through `kernel`, which is
what `exec_rate == 1` means and is why this row is the clean calibration point
and `ph64` is not.

⭐ **AND THE SIGN. The shipped R5's `kernel` is TWO INSTRUCTIONS SMALLER than the
shipped R4's** (306 non-pad against 308), so **the proved rung is cheaper than
the hand-written unsafe one, with no search at all.** ⚠ Nothing is violated:
this row pins `identity: differ` at both levels and the gate measures `differ`.
⚠ And it is not a result about verification — §8e already calls R5 − R4 a
codegen coin flip, and −0.04 % is what a coin flip looks like. **The value here
is the CALIBRATION, not the direction.**
⚠ **F82 and `TASK_PHP_037.md` both quote family A as `−0.0383 %` for this row
without saying which input; that is the `small.bin` figure and `large.bin` is
`−0.0054 %`.** Same for `ph64`'s `−0.0067 %`.

### 8g. ⭐⭐⭐ THE SPELLING SEARCH — `controls/spellings.py`, AND **NEITHER** ENDPOINT IS DEGENERATE

`TASK_PHP_037`. **The debt §13 used to declare is discharged.** Nine variants,
all produced by exact-string substitution from the shipped rungs with the hit
count asserted; every one audited against `spec.md`'s declaration by
`harness/check.py::spelling_matches`; every one returning the shipped checksum on
all eight inputs; every R4 variant's substitution applied to `verus.rs` as well
and put through Verus. Full output and both families per variant:
`controls/spellings.json`.

⚠⚠⚠ **READ THIS FIRST, BECAUSE IT IS THE MOST IMPORTANT THING THE SEARCH FOUND
AND IT IS ABOUT THE ROW'S OWN HEADLINE STATISTIC.** §8a says A1 sees 9.5 % of
this row. Every lever the search found lives in `dec`, which A1 excludes — so

> ## ⚠⚠⚠ **A1 CANNOT RESOLVE THIS ROW AT ALL.**
>
> **A1 reports EVERY ONE of the nine variants as EXACTLY `+0.37 %` (R3 side) or
> EXACTLY `+0.00 %` (R4 side).** Its spread over a side is **`0.000000`
> percentage points**. The whole-program spread over the same nine variants is
> **66.7 pp on R3 and 44.5 pp on R4.**
>
> ▶▶ **SO A CONTROL THAT PRICED THIS ROW IN A1 ALONE WOULD HAVE WRITTEN
> `r4_endpoint_degenerate: true` AND `r3_endpoint_degenerate: true`. BOTH ARE
> FALSE.** That is not a small mis-estimate — it is a **false negative on this
> row's main result**, produced by a statistic that is `0.0000 %` on every null
> in the tree and therefore looks impeccable.
>
> ⭐⭐ **AND THIS IS THE CORRECTED TWO-CONDITION RULE EARNING ITS KEEP ON THE
> FIRST ROW IT WAS APPLIED TO** (§8b). Condition (i) — *family A must actually
> SEE both cells* — is precisely what fails here: `inside_share` is
> **0.055–0.094**, so A1 sees under 10 % of either cell. F74's withdrawn
> one-condition form passes on this comparison (`|Δinside_share| = 0.003`) and
> would have licensed A1 as the headline. **The condition that catches it is the
> one the sweep added.**

⭐ And the `kernel` **fingerprints are NOT identical** — the four R3 variants
carry **3** distinct `kernel` digests and the five R4 variants **4**
(`spellings.json .kernel_digests_distinct`), because `dec_flush` is inlined into
`kernel`. **So A1's blindness here is not *"the symbol did not change"*; it is
*"the symbol's EXECUTED COUNT did not move at all while its code did"*** — a
sharper statement, and the one the A1 column actually rests on.
▶ **A control that priced this row in A1 alone would have reported both
endpoints DEGENERATE, and it would have been wrong for a reason that has nothing
to do with Rust.** That is why `spellings.json`'s `headline_statistic` is the
whole-program family and both are printed for every comparison.

**Both families, `O3 / isolated`, `small.bin`, per kernel call.** A1 =
`kernel_exclusive_ir / n_iters` (`measure.py::_sum_rows`, imported); W1 =
whole-program `Ir / n_iters` (callgrind's own `PROGRAM TOTALS`, which is §8b's
*"whole-program"* column). Stage 3 reproduces the shipped cells to **0.0000 %**
in A1 against `results-php/ph45-htmlent-cache-int.json` and to **0.014 %** in W1
against §8b.

| variant | side | A1 vs R4ship | **W1 vs R4ship** | trusted sites | twin |
|---|---|---:|---:|---:|---|
| `v0_shipped` | R3 | +0.37 % | **−3.06 %** | 0 | — |
| `r3_subslice` | R3 | +0.37 % | −3.07 % | 0 | — |
| `r3_namecmp_fn` | R3 | +0.37 % | **−20.66 %** | 0 | — |
| `r3_arena_index` | R3 | +0.37 % | +46.07 % | 0 | — |
| `v0_shipped` | R4 | +0.00 % | **+0.00 %** | 12 | verifies 41/0 |
| `r4_buf_slice_inline` | R4 | +0.00 % | **−23.47 %** | **10** | **verifies 41/0** |
| `r4_buf_slice` | R4 | +0.00 % | +16.65 % | 10 | verifies 41/0 |
| `r4_mirror_unchecked` | R4 | +0.00 % | +20.97 % | 12 | verifies 41/0 |
| `r4_buf_array` | R4 | +0.00 % | (−23.48 %) | 10 | ⛔ `is not supported` |

**What may be quoted, labelled, and it is two quantities per family and not
three:**

> **`fixed-R4 bound`, R4 held fixed by fiat — A1 `+0.37 %`, W1 `−3.06 %`.**
> **R3-side span, cheapest-found .. dearest-found in contract — W1 `−20.66 %`
> .. `+46.07 %` (`r3_namecmp_fn` .. `r3_arena_index`).** ⚠ **In family A1 the
> span is NOT COMPUTABLE**: all four in-contract R3 variants measure the same
> figure, and a `min` over equal values is the enumeration order, not a
> minimum. The control says so rather than naming a variant.
>
> ⚠⚠ **NO PAIR INTERVAL.** `min(R3 found) − min(R4 found)` differences two
> upper bounds and bounds nothing in either direction.

**1. ⭐⭐⭐ THE R4 ENDPOINT MOVES, AND THE CANDIDATE IS CHEAPER *AND* SMALLER.**
`r4_buf_slice_inline` — `name_eq` taking the work buffer as a hoisted `&[u8]`
and reading it with a **checked** index, forced inline — is **−23.47 %** on W1
against the shipped R4, has a Verus twin that verifies at **41 verified, 0
errors** (the shipped rung's own count) with **no `assume`, no new trusted item
and no `is not supported`**, and its unchecked-dereference surface is **10 call
sites against the shipped rung's 12** (measured, not asserted). So it is cheaper
**and two trusted call sites smaller** — `ph07`'s `r4_index0` shape and `ph29`'s
`r4_fold_iter` shape at once. This row is the **second** in either programme
whose R4 endpoint moves.

**2. ⭐⭐ AND THE R3 ENDPOINT MOVES TOO, WHICH IS THE FIRST TIME BOTH HAVE.**
`r3_namecmp_fn` is **−20.66 %** on W1 against R4ship, i.e. **18.1 % cheaper than
the shipped R3.** ▶ **So NEITHER published endpoint of this row's `fixed-R4
bound` is a searched endpoint**, and that is a fact about the published number
rather than about Rust.

**3. ⚠⚠⚠ AND THE SIGN OF THE BOUND REVERSES UNDER SEARCH.** Shipped, R3 is
cheaper than R4 (`−3.06 %`). Under the cheapest spelling found on each side, R4
is cheaper than R3 — `41 851` against `43 389` `Ir`/call, **3.5 %**. ⚠ **That
3.5 % is the only figure here that is a difference of two minima and it is
therefore NOT a bound**; it is quoted as an ordering, never as an interval.
⚠⚠ **So this row is NOT `ph16`'s F67 mechanism after all**, and §8d's old
paragraph guessed the other way: F67 is *two rungs cheapest under DIFFERENT
spellings with a degenerate R4*, and here the **same** spelling is cheapest on
both sides and R4 is **not** degenerate. **F67 stays n = 1**, exactly as
`ph29`'s search also concluded.

**4. ⭐⭐⭐ THE MIRROR CONTROL, AND IT IS THE SHARPEST LADDER RESULT ON THIS ROW.**
`r4_mirror_unchecked` is `r4_buf_slice_inline`'s shape **exactly** — same
signature, same hoist, same inline hint, same 12 trusted call sites — with the
arena reads left as `get_unchecked`. It measures **+20.97 %**, i.e. **44
percentage points dearer than the checked spelling of the same program.**

> ▶ **WHAT IS MEASURED, and it is the whole of what is measured: on this row, in
> this loop shape, the BOUNDS-CHECKED read is 44 pp cheaper than the unchecked
> one in an otherwise identical program.** So `get_unchecked` is not merely
> free here — it is the expensive spelling. **The two programs differ in the
> read and in nothing else**, which is what makes the 44 pp attributable to the
> read at all.

⚠⚠⚠ **AND THE MECHANISM IS A STORY I HAVE NOT VERIFIED. DO NOT QUOTE IT AS A
RESULT.** The explanation that suggests itself — *"reading through the whole
512-byte arena at a computed offset is what blocks the hoist, and `unsafe` is
what forces that spelling, because an unchecked read has to name the object the
bound was removed from"* — is **plausible and unmeasured**. I did not diff the
two `dec` symbols at the instruction level, and **a disassembly diff is what
would settle it.**
⭐ **This is recorded as open because F72 is exactly this shape**: a stated cause
that read as measured, and `TASK_PHP_033` produced git evidence against it one
round later. `PROTOCOL.md` rule 9's refinement applies — *a result with a
CONCLUSION and a MECHANISM has different evidence for each; land the conclusion,
mark the mechanism OPEN.* **The conclusion (44 pp, attributable to the read) is
measured and stands on its own. The mechanism is a hypothesis for whoever
reviews this row.**

⚠ **And what the conclusion does NOT license.** One loop, one row, one
toolchain; it says nothing about `get_unchecked` in general. What it does say is
that *"remove the bounds check"* and *"make it faster"* **came apart here**, and
the mirror is what separates them.

**5. ⛔ THE R3 LEVER CANNOT BE MOVED TO R4 IN ITS OWN SPELLING, AND THE REASON IS
vstd COVERAGE.** `r4_buf_array` is `safe_tuned.rs`'s own `&[u8; REQ]` /
`try_into` lever put into R4. It builds, it returns the shipped checksum, and it
is **−23.48 %** — but its twin is refused:

```
error: `core::array::TryFromSliceError` is not supported
```

**`is not supported` DISQUALIFIES** (`spec.md`'s own hashed rule): the pinned
vstd ships no `TryFrom<&[T]> for &[T; N]`, and `std_specs/convert.rs`'s only
`TryFromSpecImpl` is a macro over integer types.
⭐⭐ **AND THE SHARED `why` BLOCK ALREADY SAYS SO, WHICH IS WHY IT MATTERS THAT
THIS WAS RE-DERIVED AND NOT INHERITED.** That block — byte-identical across all
six PHP rows — lists the routes that are `is not supported` at the pinned vstd
and **`TryFromSliceError` is one of the six it names**. The control reproduces
the error text from a Verus run on this row's own twin rather than quoting the
declaration, because a control that inherits a claim cannot detect the day the
claim stops being true.
⚠ **Declaring the error type by hand does not rescue it** — measured: with
`#[verifier::external_type_specification]` plus `#[verifier::external_body]` the
error becomes `precondition not satisfied` on `Result::unwrap`, because nothing
establishes the conversion succeeded, and discharging that needs a
`TryFromSpecImpl` this vstd does not have. **Two new trusted declarations and it
still does not close.** ⭐ This is `ph29`'s `r4_head_array` result on a second
row — *the R3-side lever is out of contract on the R4 side for a vstd-coverage
reason* — and it is why the ADMISSIBLE candidate had to be spelled `&[u8]`. ⭐⭐
**That the two spellings are a TIE at run time is what makes it free to comply.**

**6. ⚠⚠⚠ THE HONEST CAVEAT, AND IT IS LARGE.** `r4_buf_slice` and
`r4_buf_slice_inline` differ by **one attribute** and by **40 percentage
points**, and `#[inline(always)]` applied WITHOUT the hoist is a **pessimisation**
(measured, `.temp/php37/explore2.log`). The two levers are not separable and
neither is a property of Rust. **Every number in this section is about
`rustc 1.97.1 / LLVM 22.1.6` on this box**, and inlining is an LLVM heuristic.
⚠ **R4 searched is NOT R4 exhausted**: nine spellings shipped, seven more priced
and dropped (`.temp/php37/explore*.log`): a `for` over the table **+14.21 %**, a
`.position()` **+13.31 %**, the table as a `static` an **exact tie** (identical
whole-program AND identical `dec`), a name-byte iterator and the loop bound
hoisted both **ties**, `#[inline(never)]` **+56.79 %**, `#[inline(always)]`
WITHOUT the hoist **+13.35 %**, and two trusted-surface reductions in `dec_flush`
and the numeric arm at **+4.07 %** and **+7.51 %** — both **dearer**, so neither
is the *"smaller trusted surface at the same price"* result they were proposed
as. **The honest claim is *"an admissible cheaper R4 exists"*, never *"this is
the cheapest"*.**
⚠ **ONE MARGIN ON THE WHOLE-PROGRAM FAMILY ITSELF, quoted rather than
re-measured** (`RECAP_PHP.md` F83, manager, **UNREVIEWED**): a whole-program
statistic on this programme carries an **attribution confound** measured at up
to **~266 `Ir`/call** — work in a callee that neither compared rung's own code
caused — and it runs in **both** directions, missing real work as readily as
charging extra. Against the **−23.47 %** above (≈ 12 800 `Ir`/call) that is about
**2 %** of the effect, and against the **44 pp** mirror it is smaller still.
**Nothing in this section turns on it.** ⚠ It would matter to a sub-percent
claim, and this row makes none.

**7. ⚠ AND THE ADMISSIBILITY BAR ON THIS ROW IS WIDER THAN `ph29`'s, WHICH IS A
PREMISE THE CONTROL READS RATHER THAN ASSUMES.** The shared `why` block argues
R4 admissibility from *"All six patterns pin `identity: unsafe == verus, O3
exact`"*. **That antecedent is FALSE here**: this row pins `differ` at both
levels and the gate record measures `differ` (`RECAP_PHP.md` F82, open item 61).
So an R4 candidate needs only a twin that **VERIFIES**, not one that compiles
byte-identically — and all four admissible twins here are in fact **not**
byte-identical to their exec rungs, as `differ` predicts.
⚠ `controls/spellings.py::identity_premise` reads the pin **and** the gate
record and derives the bar from what it finds, so a row re-pinned to `exact`
tightens the rule instead of silently keeping the loose one. It is also why the
bar reads the RECORD: F82 found a PAT row whose `spec.md` carries
`identity: unsafe == verus, O3 exact` as shared-block boilerplate while its real
pin is `norel`.

---

## 9. Sanitizers — `clean` on every input, and that is the finding

`model.py::sanitizer_expect` returns `"clean"` unconditionally, and the reason
is not that the row failed to build an adversarial input.

**The defect is a TYPE error, and the address it produces is a legitimately
mapped page of the row's own arena.** ASan does not track `mmap`. UBSan has
nothing to say: `(int)ptr` and `(char*)i` are **implementation-defined**
(C99 6.3.2.3p5 and p6), not undefined — what is undefined is the
**dereference**, and no sanitizer has a check for it. ⭐ **So on this row the
detectors are silent and the checksum is the only observer**, which is why
`c/arena.h`'s five counters are folded into it (`PROTOCOL_PHP.md` §B1 rule 2).

⚠ **§A4 fidelity is not lost, it is relocated to `controls/`.** `controls/fatal.c`
is the faithful spelling — `common-php/emalloc_shim.h`, no arena — and under
ASan it reproduces the corpus's recorded category exactly:

```
corpus, php-5.0.0-fullext + ASan, CRASH-123.php
  -> SEGV on unknown address 0x14ba8, WRITE, #0 mbfl_filt_conv_html_dec
     ... mbfilter_htmlent.c:183

controls/fatal.c, `&#20013;`
  -> SEGV on unknown address 0x28, WRITE, #0 dec ... fatal.c:84
     (which IS `buffer[0] = '&'`, i.e. :183)

controls/fatal.c, `hello, world`      <- NO `&` AT ALL
  -> SEGV on unknown address 0x20, READ, #0 php_shim_efree
     ... emalloc_shim.h:414   (PHP's own `_efree` reading the header at p-24,
     reached from the dtor -- i.e. :169's free)
```

⭐ **Signal, access type, function and line all match.** `ph64` had to report a
*different* signal from its corpus row; this one does not.

⚠ **`-static-libasan` is not cosmetic on this box.** Without it every ASan run
prints `ASan runtime does not come first in initial library list` and produces
**no report at all** — which reads exactly like "no fault". `controls/native.py`
says so in a comment.

---

## 10. ⭐⭐⭐ The ladder — what safe Rust does with a pointer in an `int`

**This section is the reason the row exists, and it contradicts the brief the
row was built from.**

### 10a. The brief's claim, and the measurement that refutes it

`TASK_PHP_036.md` §1 and `TASK_PHP_034_REPORT` §6.8 both state:

> *"safe Rust **cannot store a pointer in an `i32` at all**: there is no pointer
> to store and no `as` cast from a reference to an integer."*

⚠⚠ **MEASURED FALSE**, rustc 1.97.1, `.temp/php36/probe/rustcast*.rs`:

```rust
let r: &u8 = &x[0];
let t: i32 = r as *const u8 as i32;      // compiles. ZERO diagnostics.
let back: *const u8 = t as usize as *const u8;
// E1b r=0x7ffe6f584994 t=0x6f584994 back=0x6f584994
```

Pointer-to-integer casts are **safe** in Rust, `as i32` truncates silently, and
`rustc -D warnings -W unused -W future-incompatible` emits **nothing**. The
resulting program SIGSEGVs when the value is dereferenced under `unsafe`.

⭐⭐ **What safe Rust refuses is O2, and only O2.**

```
error[E0133]: dereference of raw pointer is unsafe and requires unsafe
              function or block
```

There is no safe expression that gets from an integer to a place. **So the
immunity is on the DEREFERENCE side, not the storage side** — which is a
sharper and more useful statement than the one the brief made, and it is why
the faithful safe port is *forced to own its memory*.

### 10b. What the four Rust rungs therefore are

⚠⚠ **They carry R1's own idiom, not R1h's.** `cache` is an `i32`; the store is
`idx as i32`; the read-back is `cache as usize`, sign extension included;
`void *opaque` appears in **no** Rust rung. What changes is the **value**: an
index into a 512-byte arena the kernel owns, which round-trips through `i32`
for the same reason an address does not.

⭐ **The 2³² gap has no counterpart, and that is the result stated as
arithmetic rather than as a check**: an arena index space of 2³² entries cannot
exist in a program that owns its arena. The Rust rungs honour `place` — it
selects between two arena regions — and the regions are 256 bytes apart.

⚠ **The arena ledger's `n_dfree`, `n_wfree` and leak arms are written out in
all four Rust rungs and are unreachable in all four.** That is the finding
written as an arm that cannot be taken, not dead code, and a reviewer should
read it that way.

### 10c. ⭐⭐ The three toolchains, on one five-line idiom

| | what it says about `(int)p` … `(char*)i` … `*i` |
|---|---|
| **gcc 13.3 / clang 22.1.6**, `-Wall -Wextra` | **FOUR warnings**: `-Wpointer-to-int-cast` ×1 at the store, `-Wint-to-pointer-cast` ×3 at the free and the two casts back — and they are exactly the four sites `e8901dc17087` rewrites. **This is bug #30573.** Zero on R1h. Measured in all 8 cells of both compilers: `controls/warnings.py`. |
| **rustc 1.97.1**, `-D warnings` | **NOTHING.** The same truncation, the same sign extension, the same fault at run time, and not one diagnostic. |
| **Verus 0.2026.08.09** | **REFUSES.** `(idx as i32) as usize == idx` verifies under `idx < 0x8000_0000` (2 verified, 0 errors) and fails without it — `postcondition not satisfied`, plus `recommendation not met: value may be out of range of the target type` **at both cast sites**. `controls/o1_roundtrip.rs` and `controls/o1_roundtrip_nopre.rs`. |

⭐ **gcc warns, rustc is silent, Verus refuses.** The usual story about C and
Rust runs the other way round, and on the type axis's first row it does not.

---

## 11. R5 — what is proved, and the vacuity measured with five mutants

`41 verified, 0 errors` in ~3 s; `43 verified, 0 errors` under `--cfg slb_twin`.

**Trusted base: three items.** `bget` and `bset` (`get_unchecked` /
`get_unchecked_mut` on `[u8; 512]` — vstd ships no spec for either; grepped
`~/tools/verus/vstd/std_specs/slice.rs`, which has `index`, `index_mut`,
`split_at`, `copy_from_slice` and `copy_within` and no `get_unchecked`, and
`~/tools/verus/vstd/array.rs`, which has `array_index_get` and no unchecked
form), each with a `slb_twin_*` safe body carrying the identical contract; and
`ent_table`, which links the 251-entry literal to an **uninterpreted**
`tbl()` and therefore axiomatises nothing about the contents.

⭐⭐ **What is proved is the corpus invariant itself**, which no other row in
either programme can say, because CRASH-123 is the only one of 166 cases with
its own invariant:

| obligation | where it lives in `verus.rs` |
|---|---|
| **O1** *a pointer must not be stored into an integer field narrower than a pointer* | `alloc`'s `ensures r == 0 \|\| (0 < r && r + BLOCK <= ASZ)` |
| **O2** *a value read back out of such a field must not be dereferenced without re-establishing that it designates the original object* | `wf_ptr(f)`, which discharges `bget`/`bset`'s `i < ASZ` at **all eleven** dereference sites |
| **O3** *a value that is not an address returned by the allocator must not be handed to the deallocator* | `s_free_n`'s ledger — ⚠ **and it is NOT a memory-safety obligation in this representation.** Freeing a wrong index is a wrong **answer**, not a wrong **access**, so O3 lives entirely in the value postcondition. |

### The vacuity, measured (`controls/vacuity.py`)

```
baseline: 41 verified, 0 errors
V1  MUST FAIL  kernel's body -> 0u64                       -> 40 / 1   ok
V2  redundant  alloc's O1 range ensures deleted            -> 41 / 0   ok
V3  MUST FAIL  bset's ensures names only the written slot   -> 40 / 1   ok
V4  MUST FAIL  wf_c's bump[r] <= REGION deleted             -> 40 / 1   ok
V5  MUST FAIL  wf_ptr weakened to `0 <= f.cache`            -> 39 / 2   ok
```

⚠⚠ **V2 IS THE ONE WORTH READING. It did not fire, and I had declared that it
would.** `alloc`'s third `ensures` is the human-readable statement of O1 — and
deleting it still verifies 41/0, because `r == s_alloc_r(old(self).g(), n)` plus
`wf_c`'s bump bound already pin the range. **The clause is REDUNDANT.** It is
kept, and `verus.rs` now says so at the site, because *a declaration that cannot
fail is worth writing only if you have measured that it cannot*. **V4 is what
shows where the fact really lives**: delete `wf_c`'s `bump[r] <= REGION` and the
proof fails with `possible arithmetic underflow/overflow`.

⚠ **`TASK_PHP_034_REPORT` §6.8 predicted a vacuity problem for exactly the
reason that does not apply here**: it expected Verus's raw-pointer API to carry
provenance, making *"the value read back designates the same allocation"* true
by typing. In an **index** representation there is no provenance at all, so
`wf_ptr` has to be established and carried, and V5 measures what happens when it
is not — three unmet preconditions and a failed loop invariant.

⚠ **V3 is the row-specific one.** The arena holds **both** filters' work
buffers, so a `bset` whose `ensures` named only `v@[i] == x` would license a
body that also moved the *other* filter's buffer — which is precisely the defect
R1 has. The shipped `ensures` is the whole post-state.

### The trusted items, one argument each

⚠ `check.py` requires a written `SLB-TRUSTED-ARGUMENT` section per trusted item
and **prints it in every verdict**, because the three questions below are ones
no stage of the gate can judge.

SLB-TRUSTED-ARGUMENT verus.rs bget

(a) **Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `v.get_unchecked(i)` on a `&[u8; ASZ]`; `slb_twin_bget`'s body is
`v[i]`. The standard library documents `get_unchecked(i)` as `index(i)` with the
bounds check removed, so it is the same byte of the same array, and Verus checks
the bound `v[i]` needs against the **same** `requires i < ASZ`. A defensive twin
— `if i < ASZ { v[i] } else { 0 }` — cannot satisfy `r == v@[i as int]` for the
out-of-range case and would fail the stage rather than pass it.

(b) **Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes as the body stands: one expression, one unchecked read, one
byte at index `i`, and `ensures r == v@[i as int]` names that index and that
array. ⚠ Nothing mechanical enforces it — a second unchecked read the `ensures`
never mentions is invisible to stages 5a, 5c, 5c-req and 5c-twin alike
(`TASK_009_REVIEW` x4). What a reviewer checks is the one-line body.

(c) **Does each clause mean the same thing in the shipped configuration as in
the twin's?** Yes: the two items have byte-identical signatures and clause text,
and neither clause mentions anything configuration-dependent. ⚠ **The backstop
is weaker here than on a row with an `exact` identity pin**, and this row says so
rather than borrowing that paragraph: `identity` is `differ` at both levels
(§8), so an extra read in `verus.rs` alone would NOT move an `md5_fn` the pin
compares. What does catch it is Miri, which this row requires, and the
cross-rung checksum.

SLB-TRUSTED-ARGUMENT verus.rs bset

(a) **Yes** — `v.get_unchecked_mut(i) = x` against the twin's `v[i] = x`, the
same argument as `bget`, on the write side. The twin needs one extra line,
`assert(final(v)@ =~= old(v)@.update(i as int, x))`, which is a proof hint and
not a weakening: it asserts exactly the shipped `ensures`.

(b) ⚠⚠ **THIS IS THE ROW WHERE (b) BITES, AND IT IS MEASURED RATHER THAN
ARGUED.** The arena holds **both** filters' work buffers, so an `ensures` naming
only `final(v)@[i] == x` would license a body that ALSO moved the other filter's
buffer — which is precisely the defect R1 has, written into the proof. The
shipped `ensures` is the whole post-state, `old(v)@.update(i as int, x)`, and
mutant **V3** (`controls/vacuity.py`) replaces it with the weaker pair
`final(v)@[i] == x` + `final(v)@.len() == old(v)@.len()` and the file drops to
`40 verified, 1 errors`. `x: u8` is a pure value and needs no precondition:
all 256 inhabitants are a legal store into a byte `[0u8; ASZ]` already
initialised.

(c) **Same as `bget`.** Miri is the backstop for the class regardless, and
`spec.md`'s `miri.reason` says why it matters more here than on a row whose
unchecked writes go to a private scratch buffer.

SLB-TRUSTED-ARGUMENT verus.rs ent_table

(a) ⚠⚠ **THERE IS NO TWIN AND THERE CANNOT BE**, and `spec.md`'s
`verus.twin_justifications` carries the argument: the `ensures` is `r@ ==
tbl()` where `tbl()` is **uninterpreted**, so a checked body would have to prove
an equation about a function with no definition. That is a fact about the shape
of the abstraction, not about this row's spelling of it.

(b) ⭐ **The question does not arise, because there is no unchecked operation.**
The body is `&[ …251 literals… ]` — a reference to a `'static` array. It is
defined for every input, there is no precondition to discharge, and `spec.md`'s
`unsafe_justifications` says so at length. That is also why this item's
`requires` is empty and why that is not a hole.

(c) ⚠ **What this item DOES axiomatise, stated plainly: that the table the exec
code walks is the one the spec functions talk about — and NOTHING about its
contents.** The proof therefore holds for any 251-entity table, and Verus is not
what says the shipped table is PHP's. `controls/entity_table.py` is: all six
shipped copies, byte for byte against `html_entities.c:37-290`, with a must-fire
negative that bumps one entity's code by 1 and is rejected by **6 of 6**. So is
`check.py` stage 2, which makes every rung agree on a `u64` that depends on the
table. ⭐ **The axiom is cheap for exactly the reason it cannot be twinned**, and
those are the same sentence read twice.

### TCB tally

| | |
|---|---|
| `#[verifier::external_body]` items **inside** `verus!` | **3** — `bget`, `bset`, `ent_table` |
| of which have a verified twin | **2** — `slb_twin_bget`, `slb_twin_bset` |
| body-less trusted declarations (`verus.axioms`) | **1** — `uninterp spec fn tbl()` |
| `#[verifier::external_body]` items **outside** the kernel's reach | 2 — `load_input`, `emit_result`, which are the driver bridge every php row has |
| `assume` / `admit` / `assume_specification` | **0** |
| `#[verifier::rlimit]` | **1**, on `run`, value 60 |

⚠ The axiom's width, counted properly: `tbl()` asserts **nothing** — it has no
`requires`, no `ensures` and no definition — so the only thing in the trusted
base because of it is `ent_table`'s `r@ == tbl()`, which is already counted as a
trusted item. That is why the row does not also owe *"a `requires` that makes it
bite and a deliberately bad call site proving that it does"*: **there is no
clause to strengthen.** What the row owes instead is evidence about the
CONTENTS, and that is `controls/entity_table.py`'s must-fire negative.

### Why `run_spec` is opaque and `kernel` is split from `run`

`ph64`'s `twin_obligations_note` records the same thing and it was true again
here: with the composition inline, `run` exceeded the rlimit. Split, with
`run_spec` `#[verifier::opaque]` and revealed once inside `run`, the file
verifies in ~3 s. There is exactly one `#[verifier::rlimit]` in the file, on
`run`, and it is 60.

---

## 12. ⚠ Two adjacent defects found and NOT pursued

`PROTOCOL.md`: *"do not improve scope; if you see adjacent work, report it."*

**12a. `mbfilter_htmlent.c:123` — a stack OOB write in the ENCODE half.**
`:101` declares `int tmp[64]`; `:123` is `int *p = tmp + sizeof(tmp);` — that is
`tmp + 256`, i.e. **192 `int`s past the end** — and `:129` immediately does
`*(--p) = '\0'`, a stack write 768 bytes out of bounds. php-5.0.4 carries
`tmp + sizeof(tmp)/sizeof(tmp[0])`. It is **not** in `e8901dc17087` and **not**
in `index.csv`. ⛔ **It is why this row must not lift `:99-150`**, and
`spec.md`'s `extra_spans_note` says so. Found by `TASK_PHP_034_REPORT` §2.2,
which did not identify its commit; neither did I, and **nobody should act on it
without doing so.**

**12b. `mbfilter_htmlent.c:193` — signed overflow, and it is MINE.**
`ent = ent*10 + (buffer[pos] - '0')` is `int` arithmetic, and `:225`'s
`strchr(html_entity_chars, c)` admits **letters** as well as digits — so
`&#abcdefghijkl;` computes roughly `7.4e12` in an `int`. That is undefined
behaviour reachable from an ordinary `mb_convert_encoding($s, 'UTF-8',
'HTML-ENTITIES')` call, in the same function as the row's own defect, and I did
not find it in `index.csv` either. ⚠ **It is not this row's defect and the row
does not price it**: `inputs/gen.py::_check_span` refuses a corpus whose largest
`|ent|` comes within 100× of `INT_MAX` **on either rung**, so no shipped number
is taken over that path. Reported, not pursued, and not traced to a fix.

**⭐ THE OBSERVED MARGIN, MEASURED OVER THE TWO SHIPPED BENIGN INPUTS.**
`TASK_PHP_037`, discharging `RECAP_PHP.md` open item 59. F46 requires a row's
benign corpus be shown not to evaluate a UB path inside its own scope. The guard
existed and was verified; what was missing is that it only **printed** its number
and nothing kept it. It is kept here:

| | `small.bin` | `large.bin` |
|---|---:|---:|
| windows, all `place = 0` | 32 | 2 050 |
| arms of the nine reached | **9 / 9** | **9 / 9** |
| numeric-arm evaluations | 528 | 251 323 |
| longest numeric body reached | **5 digits** | **5 digits** |
| **max abs ent** | **20 013** | **20 013** |
| margin vs `ENT_CEILING` (= `INT_MAX // 100` = 21 474 836) | **1 073.04×** | **1 073.04×** |
| margin vs `INT_MAX` | **107 304×** | **107 304×** |

⚠ **The guard is NOT vacuous a priori, and that is why the observed number is
worth keeping rather than the ceiling.** The `buffull` arm caps a numeric body at
**13 digits**, i.e. about `7.4e12` — three orders of magnitude ABOVE `INT_MAX`.
What keeps this corpus safe is not the arm bound; it is that no token in
`inputs/gen.py::TOKENS`, and no splice between two of them, ever produces a body
longer than the five digits of the largest numeric entity the grammar contains.

**How it was measured, and it is READ-ONLY.** ⛔ `inputs/gen.py` is in this row's
**measurement** digest *and* it rewrites `inputs/*.bin`, so it must not be run:
either would cost a 32-cell re-measure and a byte change would invalidate every
number this row publishes. `.temp/php37/entmargin.py` instead unpacks the
**shipped** `.bin` files through `common-php/slb.py` and decodes them **twice**:

* **decoder A** — `gen.py`'s own `_arms_of` and `_entities`, imported as a module
  (its `main()` sits behind an `if __name__` guard, and `sys.dont_write_bytecode`
  is set before the import so not even a `__pycache__` entry appears beside a
  file in the measurement digest);
* **decoder B** — an independent re-implementation with its own entity-table
  parser over `c/mbfl__html_entities.h` and its own `html_entity_chars` read from
  **`c/kernel.c`**, so the two decoders share no constant. It tracks the
  accumulator in unbounded integers **and** in wrapped 32-bit at the same time.

✅ **The two agree on both inputs (20 013 / 20 013) and on all nine arms**; the
two entity tables are equal; the two character sets are equal; and the
**wrapped and unbounded accumulators are identical, which is the direct statement
that `:193` never overflowed on a shipped input** rather than an inference from a
margin. The probe re-hashes all eight blobs before and after and confirms none
moved.
⚠ Had the two decoders disagreed, the disagreement would have been the result: a
re-implementation that quietly differs is F52's shape.
⚠ **Still not traced to a fix, and that half is unchanged.** Nothing here is
evidence about whether upstream ever repaired `:193`.

---

## 13. What I did not do

* ~~⚠ **`controls/spellings.py` is NOT built.** ⚠⚠ The R4 endpoint is
  **UNSEARCHED**, so the `fixed-R4 bound` this row publishes is over an
  unsearched endpoint and `.memory-php/02-ladder.md`'s standing debt applies —
  `ph03` and `ph64` carry the same one and this row makes it three.~~
  ✅ **DISCHARGED AT `TASK_PHP_037`: `controls/spellings.py` and
  `controls/spellings.json` ship, both sides are searched, and §8g is the
  result.** ⚠⚠ **And the answer is that NEITHER endpoint is degenerate**, so
  the `fixed-R4 bound` this row publishes is a bound over two numbers that both
  move, which is a stronger statement of the debt than the one struck above.
  `ph03` and `ph64` still carry it, so this row takes the count from 3 of 6 to
  **2 of 6** — ⚠ count it rather than trusting this line.
  ⭐ **The R3-side search that WAS here is not superseded, it is corrected**:
  `safe_tuned.rs`'s header carries four candidates measured whole-program on
  both inputs, three of them pessimisations, one cheaper than R4, and a fifth
  (`c3`) measured and deliberately not shipped. What it does not have is an
  `.idiom_audit`, so nothing checked those candidates against the declaration by
  grep — `spellings.py` does, for nine variants. ⚠ **And §8d records that the
  header's stated MECHANISM for its own lever is refuted**: the array type is a
  tie against a plain sub-slice, measured three ways. The bound ships
  **labelled**, in **both families**, and there is **no pair interval**.
* ⚠ **No PHP was built and no reproducer was run.** The corpus's `n_fault: 3/3`
  is its measurement; mine is `controls/fatal.c`, and the two agree on signal,
  access type, function and line (§9).
* ⚠ **`mbfl_convert_filter_copy`'s aliasing double free is CITED and NOT
  PRICED.** `TASK_PHP_034_REPORT` §4.3 reads it at source and its own §8.4 says
  in terms that it is an inference. The span is in `extra_spans` because the fix
  removes it as a consequence — which makes the fix *larger* than the catalogued
  defect — and that is all this row claims about it.
* ⚠ **`echoes: ["p38"]` was not re-derived**; it is the catalogue's and is
  carried forward.
* ⚠ **The tier is a judgement and §3 is where it is argued.** The manager's
  ruling that the placement is a `projection` rather than a `modelled`
  divergence is accepted here with the counter-argument written down beside it.
