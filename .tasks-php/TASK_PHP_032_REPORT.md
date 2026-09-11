# TASK_PHP_032_REPORT — `ph64-callback-frees-cursor`, the first temporal row

**Role: research engineer. One agent, alone.** The row is built at all five
rungs plus R1h, with `spec.md`, `model.py`, nine controls and `results-php/`
records. §0 is the headline, §1–§12 the detail, §13 what I did not do.

---

## §0 Headline, before the detail

| | |
|---|---|
| **the row** | `patterns-php/ph64-callback-frees-cursor/` — **the slug is the MECHANISM**: a list walk whose cursor is advanced *after* a callback that is allowed to free the element it points at. Not `zend_llist`, not `apply` |
| ⭐ **the falsifiable prediction held** | **`check.py` stage 7h was GREEN ON THE FIRST ATTEMPT.** `sanitizer_hardened` is clean on **all eight** inputs, adversarial included, and `sanitizer` fires on exactly the four the model declares. `_031` §6.4 predicted it and the task file staked the brief on it |
| ⭐⭐ **the catalogue's oracle measures nothing, confirmed at scale** | `controls/oracle.py` E2a: on **213 of 213** corpus-trigger windows the visit fold is **bit-identical** between R1 and R1h. `CATALOGUE.md:795`'s proposed `u64` would have gated green while measuring nothing. The row folds `l->count`, the dtor count, the refusal count and `php_shim_tally()`'s four fields as well, and those move on all 213 |
| ⭐⭐ **§A4 fidelity: the recorded category IS reproducible, with the allocator swapped** | `controls/asan_fidelity.sh`: on plain `malloc`/`free` the row gives **`heap-use-after-free`, `WRITE of size 4`, frame #0 `user_tick_function_call` (SITE C), frame #1 `zend_llist_apply` (SITE L)** — exactly `index.csv`'s category and exactly its cited line. On the faithful cached allocator the same window is **SILENT**, which is §B1 rule 1 measured rather than quoted |
| ⭐⭐ **the counterfactual hardening is NOT weaker — it is INCOMPARABLE** | `controls/next_cache.py`: caching `next` (the idiom `zend_llist_apply_with_del:177` uses fifteen lines above) removes 189/189 wild walks, leaves SITE C writing into the recycled block 189/189, fails to restore the answer 189/189, **and ADDS a use-after-free of the cursor's SUCCESSOR on 196/196 windows that the plain walk does not have.** ⚠ **I predicted the opposite and the control caught me** |
| ⭐ **`562f886ecb14` is one word from being a no-op** | `controls/predicate.py`: reading `tick_fe2->calling` (the search key, which PHP never sets) instead of `tick_fe1->calling` makes the guard dead — **189/189 trigger windows revert to R1's exact `u64`** and 189/189 reuse windows still go wild |
| ⭐ **what the fix costs** | **+15.98 Ir/call (gcc) / +18.34 (clang), FLAT in list length** across a 7.6× change in `n`. That is the one clean like-for-like number this row has |
| ⚠⚠ **and it is INVISIBLE in the published table's own column** | `kernel_exclusive_ir` is **identical to the instruction** for `c-gcc` and `c-gcc-h`, because gcc keeps `ph64_unregister_tick_function` out of line and that is the symbol the guard lives in. **Reading the table's `Ir` column alone supports "R1h costs zero", which is false** |
| ⚠⚠⚠ **the C-vs-Rust column on this row is NOT a safety comparison** | `PROTOCOL_PHP.md` §B forbids a Rust rung from linking the shim, so **the C rung allocates and the Rust rungs count.** On `ph07` that was one `emalloc` per call and it was noise; here it is `2n + 2` with `n` up to 1014, and **60 % of the C's instructions are in libc `malloc`/`free`.** §5 is the general form and it is the report's most transferable finding |
| ⭐ **the `fixed-R4 bound` is POSITIVE and breaks the `ph16`/`ph29` pair** | **+17.08 % (small) / +15.37 % (large)**, where `ph16` is −1.22 % and `ph29` is −6.06 %. ⚠ Unsearched on both sides — `controls/spellings.py` was not built and the debt is declared, not carried |
| ⭐⭐ **the ladder finding** | **Safe Rust does not turn this defect into a panic. It turns it into a WRONG ANSWER**, because the faithful safe port of an intrusive pointer list is an index arena and a dangling index is an in-bounds read. `verus.rs`'s `wf` — the invariant that licenses all eight unchecked accessors and every `decreases` — **holds with `562f886ecb14` DELETED.** Memory safety and the upstream fix are **orthogonal** on this row |
| **the proof** | **39 verified / 0 errors**, 47 under `--cfg slb_twin`, with the **full value postcondition** `r == llist_fold(buf@, off, len)`. ⭐ **And NO `#[verifier::rlimit]` anywhere**: `kernel` would not verify at `rlimit(600)` as one function and verifies at the DEFAULT 10 once `run_spec` was made `#[verifier::opaque]` and two functions were split out. **Raising the budget was tried first and did nothing** |
| **the gate** | **`check.py: PASS`, 0 failures**, over three rounds (19 → 3 → 2 → 0). Every failure in every round was the gate being right about the row — including 8 `idiom-forbidden` hits caused by my own `forbidden` prose quoting tokens the C rungs contain |
| ⚠ **the open item, NOT measured** | `_031` §4.3's incompleteness candidate is **not resolved** and I did not try before the row gated. The static reading is verified at source and is in `spec.md`'s `divergences[5]` and `NOTES.md` §4d as an OPEN ITEM, not a finding |

---

## §1 Where I disagree with the brief, and where I corrected myself

`_031` §6 is a good brief and **everything in it that I measured held**. Three
places where the shipped row differs from it, and one where I was wrong:

1. ⚠ **§6.1's span table is 12 spans; the row cites 14.** I added
   `Zend/zend_llist.c:107-121` (`zend_llist_destroy`, sha256
   `5e38ed5040949606…`) because the kernel lifts it — every call destroys its
   list so that call *N* does not depend on call *N−1* — and I split
   `[73,104]` exactly as §6.1 offers. No span in §6.1 was dropped.
2. ⚠ **§6.4's oracle 2 is in `inputs/`, not only in `controls/`.** §6.4 says *"a
   row cannot measure a faulting cell (the driver loop dies), so oracle 2 belongs
   in `controls/`"*. That is true of the **measured** cells and not of the
   adversarial ones: `check.py::check_adversarial` RECORDS per-rung behaviour and
   does not require agreement, and stage 7's `sanitizer_expect` is per-input. So
   the four reuse windows ship as `inputs/adversarial-reuse-{mid,head,tail,only}.bin`,
   R1 dies on a signal on all four, R1h is clean on all four, and **the fault is
   in the gate record** instead of only in a control. The controls carry it too.
3. ⚠ **The window layout is mine, not §6.3's.** §6.3 specifies the trigger
   ("one entry's callback unregisters itself, plus one same-size-class
   allocation"); the four head words, the 4-byte slot and the
   `[u32 le id][slot]` name are the row's own. **The id half is what makes names
   unique BY CONSTRUCTION**, which closes `_031` §8.8's own probe bug by
   construction rather than by an assertion.
4. ⚠⚠ **I was wrong about the counterfactual hardening and a control caught
   me.** `controls/next_cache.py`'s first version declared "identical wherever
   nothing is freed under the cursor" and missed on **196 of 1958** windows, all
   `mode == AHEAD`. The expectation was wrong, not the measurement. The miss is
   recorded in the control's own header and the finding it produced (§0, row 5)
   is better than the one I expected.

---

## §2 What is built

```
patterns-php/ph64-callback-frees-cursor/
  spec.md          71,800 B   contract_sha256 a45c15891ee66bc8…  (GENERATED, §9)
  NOTES.md         ~47 kB     §0 rule-6 disclosure .. §13, + 8 SLB-TRUSTED-ARGUMENT
  README.md
  model.py         two independent implementations + a 2 592-window selfcheck
  c/kernel.h  c/kernel.c  c/kernel_hardened.c  c/main.c  c/emalloc_shim.h -> symlink
  safe_naive.rs  safe_tuned.rs  unsafe.rs  verus.rs
  inputs/gen.py + 8 .bin
  controls/  562f886ecb14.patch  bug41037.phpt  bug41037.py  oracle.py
             differential.py  next_cache.py  predicate.py
             asan_fidelity.sh  asan_fidelity.py  plain_alloc.h  dump.c
results-php/ph64-callback-frees-cursor.json           (measurement)
results-php/gate/ph64-callback-frees-cursor.json      (gate)
results-php/tables/ph64-callback-frees-cursor.md      (rendered)
results-php/preflight/ph64-callback-frees-cursor.preflight.json
```

⚠ **The faithful chain is ~330 lines of C across five frames, not 8.** `_031`
§5.3 measured ~140 for a probe; the row adds `zend_llist_destroy`,
`register_tick_function`, the layout assertion and the driver wrapper. The
8-line `zend_llist_apply` is the DEFECT, not the extraction, and the manager's
"8 lines, no PHP machinery" (written into `_031`'s task file) remains false.

---

## §3 The evidence, command by command

Every control ships **must-fire and must-NOT-fire** cases and fails on a miss in
either direction (`PROTOCOL_PHP.md` §H). ⚠ `harness-php/gate.py` **hashes
`controls/*.py` and never runs them**, so these are hand-run and the output is
below.

```
$ python3 patterns-php/ph64-callback-frees-cursor/controls/oracle.py
E1  must-NOT-fire  R1 == R1h              : 2166/2166
E2  must-fire      R1 != R1h (latent)     : 213/213
E2a must-fire      visit fold IS EQUAL    : 213/213  <- the catalogue's oracle measures nothing
E3  must-fire      R1 goes WILD on reuse  : 213/213
E4  must-NOT-fire  nothing else goes wild : 2379/2379
E5  must-fire      DEL_LLIST arms reached : ['head', 'mid', 'only', 'tail']
=== ORACLE CONTROL: PASS (0 miss(es)) ===

$ python3 .../controls/differential.py            # the SHIPPED C vs both model implementations
windows: 2592
E1 must-fire      C-R1h == simulated == closed form : 2592/2592
E2 must-fire      C R1 != C R1h (the latent case)   : 213/213
E3 must-NOT-fire  C R1 == C R1h everywhere else     : 2166/2166
E4 must-fire      C R1 SIGNALS on reuse             : 213/213
E5 must-NOT-fire  nothing else signals              : 2379/2379
E6 must-fire      DEL_LLIST_ELEMENT arms reached    : ['head', 'mid', 'only', 'tail']
=== differential CONTROL: PASS (0 miss(es)) ===

$ python3 .../controls/next_cache.py
E1 must-fire      cached `next` removes the wild walk : 189/189   <- SITE L is FIXED
E2 must-fire      ... and SITE C still clobbers       : 189/189   <- SITE C is NOT
E3 must-fire      ... and the u64 still differs       : 189/189   <- and the ANSWER is NOT
E4 must-NOT-fire  identical where nothing dies ahead  : 1762/1762
E5 must-fire      ⚠ cached `next` VISITS A FREED NODE : 196/196   <- the hazard it ADDS
=== next_cache CONTROL: PASS (0 miss(es)) ===

$ python3 .../controls/predicate.py
E1 must-fire      `tick_fe2` guard == R1 (a no-op)   : 189/189
E2 must-fire      `tick_fe2` guard still goes WILD   : 189/189
E3 must-NOT-fire  all three agree where nothing dies : 1958/1958
E4 must-fire      shipped guard refuses exactly once : 2336/2336   <- §4.2's invariant, measured
=== predicate CONTROL: PASS (0 miss(es)) ===

$ python3 .../controls/bug41037.py                 # upstream's own regression test
controls/bug41037.phpt: 3 x `hello`, 3 x the refusal warning  <- upstream's own --EXPECTF--
E1 must-fire      R1h  : {'visits': 3, 'refusals': 3, 'dtors': 0, 'count': 1}
E2 must-fire      R1   : {'visits': 1, 'refusals': 0, 'dtors': 1, 'count': 0}
E3 must-NOT-fire  R1h  : {'visits': 3, 'refusals': 0, 'dtors': 0, 'count': 1}
E3 must-NOT-fire  R1   : {'visits': 3, 'refusals': 0, 'dtors': 0, 'count': 1}
=== bug41037 CONTROL: PASS (0 miss(es)) ===

$ sh .../controls/asan_fidelity.sh                 # §A4, four builds x three windows
shim_plain    trigger-no-reuse   -> returns the u64      trigger-with-reuse -> CRASH 11
shim_asan     trigger-no-reuse   -> SILENT               trigger-with-reuse -> UBSan misaligned
                                                            0x1000000000004 then DEADLYSIGNAL
malloc_plain  trigger-no-reuse   -> CRASH 11             (⭐ §B1 rule 1, measured)
malloc_asan   trigger-no-reuse   -> AddressSanitizer: heap-use-after-free
                                    WRITE of size 4
                                      #0 user_tick_function_call  c/kernel.c:431   <- SITE C
                                      #1 zend_llist_apply         c/kernel.c:265   <- SITE L
              control-no-free    -> silent in all four builds
```

⚠ **Two declared expectations of my own were WRONG and are recorded rather than
rewritten**: `next_cache.py` E5 (§1.4) and `asan_fidelity.sh` E2, where I
predicted `SEGV on unknown address` and got UBSan's misaligned-access
diagnostic. In both cases the *category* claim the expectation existed for held.

---

## §4 ⚠⚠⚠ The measurement problem this row exposes, and it is not this row's

`report.py`'s own preamble already warns that the `isolated` kernel-exclusive
column "is right only when every rung does its own work inside its own symbol",
and names `p08` and `p11` as the two PAT rows where it reverses a real
comparison. **ph64 is a third, and it reverses TWO.** Whole-program attribution,
`O3 / isolated / small.bin`, from `callgrind_annotate`:

```
c-gcc      total 66,070,064   kernel 20,036,795 (30.3%)
                              libc malloc/free & friends 39,803,304 (60.2%)
                              user_tick_function_dtor       2,988,765 (4.5%)
                              ph64_unregister_tick_function   693,416 (1.0%)   <- R1h LIVES HERE
unsafe     total 12,795,571   unsafe::kernel 11,330,956 (88.6%)
safe_naive total 19,759,221   safe_naive::kernel 12,936,157 (65.5%)
                              safe_naive::name_of 3,261,108 (16.5%)
                              realloc               503,412 (2.5%)
```

1. **It hides `562f886ecb14` entirely.** `kernel_exclusive_ir` is identical to
   the instruction for `c-gcc` and `c-gcc-h`, and so is `md5_fn_norel`. The
   marginal (whole-program slope) puts the fix at **+15.98 Ir/call**.
2. **It reverses R2 vs R3.** Kernel-exclusive reads R3 **+2.9 % dearer**; the
   marginal reads R3 **24.6 % cheaper**. The 16.5 % R2 spends in an out-of-line
   `name_of` is in no column of the published table.

**Every figure this row publishes is in `marginal_ir_per_call`**, and `NOTES.md`
§8 states that convention, which is what `report.py` asks a row in this position
to do.

---

## §5 ⚠⚠⚠ THE FINDING I THINK MATTERS MOST, AND IT IS ABOUT `PROTOCOL_PHP.md` §B

> **The C rung allocates; the Rust rungs count. §B2's "the Rust rungs reproduce
> the tally arithmetically" is free only while a row makes O(1) allocations per
> kernel call, and ph64 is the first php row where it is O(n).**

§B forbids a Rust rung from linking `emalloc_shim.h` (three translation units,
frozen `build.py`), so the four Rust rungs model `php_shim_tally()`'s four
counters arithmetically. That is **exactly right for the CHECKSUM** — it is what
makes the six rungs agree on the `u64` — and **exactly wrong for the COST**.

On `ph07` the kernel made one `emalloc` + one `efree` per call and the asymmetry
was noise. Here it makes `2n + 2` with `n` up to 1014, and `php_shim_reset()` at
the top of every call (§B1 rule 3, and NOT optional here because the cache IS the
oracle) means every one of them is a real `malloc`. The result is **60 % of the
C's instructions in libc**, and the 4.3–4.6× "C vs unsafe Rust" ratio is that and
nothing else.

⚠ **A row in this position has two honest options and I took the first**: say so
in the loudest terms available (`NOTES.md` §8c, `spec.md`'s `divergences[10]`,
`README.md`), or give the Rust rungs the same allocation traffic — which for an
index arena would be a design chosen to fit a metric. **The second is what I
think a reviewer should push back on if they disagree with the first.**

⚠ I do not think this changes any published `pNN` or `phNN` figure. It changes
what a reader may conclude from **this** row's C-vs-Rust column, and it is a
condition worth adding to §B2 when a reviewer has looked at it.

---

## §6 The numbers

`marginal_ir_per_call`, `O3 / isolated` — the whole-program slope:

| rung | `small.bin` (552 B, mean n≈73) | `large.bin` (4074 B, mean n≈558) |
|---|---:|---:|
| `c-gcc` (R1) | 42,585.22 | 342,010.56 |
| `c-gcc-h` (R1h) | 42,601.20 | 342,027.51 |
| `c-clang` (R1) | 41,428.27 | 333,033.90 |
| `c-clang-h` (R1h) | 41,446.61 | 333,052.23 |
| `safe_naive` (R2) | 12,407.88 | 88,218.50 |
| `safe_tuned` (R3) | 9,351.56 | 70,330.15 |
| `unsafe` (R4) | 7,987.14 | 60,959.59 |
| `verus` (R5) | 8,180.50 | 60,930.82 |

| | `small` | `large` |
|---|---:|---:|
| **R1h − R1 (gcc)** | **+15.98 Ir/call** (+0.037 %) | **+16.95 Ir/call** (+0.005 %) |
| **R1h − R1 (clang)** | +18.34 (+0.044 %) | +18.33 (+0.006 %) |
| `fixed-R4 bound` R3 − R4 | **+17.08 %** | **+15.37 %** |
| R2 − R4 | +55.35 % | +44.72 % |
| R3 − R2 | **−24.63 %** | **−20.28 %** |
| R5 − R4 | +2.42 % | −0.05 % |

⭐ **R1h's cost is FLAT in `n`** to within 1 Ir across a 7.6× change in list
length, and the mechanism is the source: `ret` is true at most once per
`zend_llist_del_element` call and a window makes at most two such calls. **The
upstream fix for a use-after-free costs sixteen instructions per tick round.**

⭐ **R3 − R2 = −20 to −25 %, mechanism named** (`PROTOCOL_PHP.md` §F8): R2 spends
16.5 % of its whole program in an out-of-line `safe_naive::name_of` (building
`[u8; 8]` byte by byte keeps the helper out of line) and 2.5 % in `realloc`
(`Vec::new()` doubles). R3's `name_of` returns the `u64` the comparison is and
inlines; `Vec::with_capacity(n)` does not reallocate.

⚠ **R5 − R4 flips sign between bands.** Solving the two gives **+227 Ir/call flat
and −0.46 Ir per registered entry**; the per-entry term is the size of the one
scheduling difference in the walk (`incq <mem>` vs `inc %rbx ; mov %rbx,<mem>`)
and **the flat term I did not isolate.** `kernel_exclusive_ir` puts R5 −0.007 %
below R4. The honest summary is that the proof is free at run time and the
direction depends on which statistic and which band you read.

⚠⚠ **The `fixed-R4 bound` is POSITIVE (+15 to +17 %) and breaks the
`ph16`/`ph29` pair.** `.memory-php/02-ladder.md` records `ph16` at −1.22 % and
`ph29` at −6.06 % and calls two rows with the same sign "materially harder to
explain as a per-row spelling artefact". **At n = 3 the signs are +, −, −.**
⚠ It is a bound over an UNSEARCHED R4 endpoint and one R3 spelling (§13).

---

## §7 R1h, and the one thing it is not

`562f886ecb14` (Antony Dovgal, 2007-04-10) ships whole and unmodified: one hunk,
7 added / 2 deleted, in `user_tick_function_compare`. Three artefacts inside the
commit (#41037, the NEWS line, `bug41037.phpt`); the php-5.2.1 → php-5.2.2 diff
of the function IS the hunk line for line; and the backport to pristine 5.0.0
costs **zero**, because 5.0.0's function is byte-identical to php-5.2.1's.
`controls/562f886ecb14.patch` and `controls/bug41037.phpt` carry the bytes.

⚠⚠ **It patches NEITHER SITE** — not `zend_llist.c:190` (never repaired at any
tag: the body's sha256 is identical at twelve tags and differs at php-7.0.0 only
by the `TSRMLS` deletion) and not `basic_functions.c:2135` (`grep -ac 'calling =
0'` over the 86-line patch is 0). It makes the FREE unreachable from a third
function and both dereferences survive verbatim into master.

⚠ **`.tasks-php/preimage_screen.py` calls it `NOT-THE-REPAIR` with
`decisive=False`, and it is right to.** No line-level pre-image screen can find
a fix of this shape; `_031` §7.1 measured the class at 17 of the screen's 43
exclusions, and ph64 is the one member checked by hand.

### §7a The open item — NOT measured, NOT a finding

`_031` §4.3's candidate is unresolved. The static reading is verified at source
at 5.0.0 **and** php-5.2.2: `php_error_docref(E_WARNING)` → `php_verror` →
`php_error` → `zend_error`'s user-handler arm, i.e. **arbitrary userland from
inside `zend_llist_del_element`'s own walk**, which holds `current` and `next`.
**I did not build PHP, did not run the reproducer, and did not check whether
`EG(user_error_handler) = NULL` or `EH_THROW` blocks the nesting.** The
conclusion is in `spec.md`'s `divergences[5]` (the one whose `why` does not end
in "no semantics") and `NOTES.md` §4d as an OPEN ITEM. ⭐ Upstream is a partial
answer: master replaced the warning with `zend_throw_error`.

⚠⚠ **So ph64 is NOT the fifth of five.** On the tick list `562f886ecb14` is
correct and minimal — `controls/predicate.py` E4 measures the invariant at
2 336/2 336 — and the incompleteness question is open, not answered. The tally in
`.memory-php/02-ladder.md` should read **`ph03` not-minimal-and-not-sufficient,
`ph07` the same, `ph16` complete and minimal, `ph29` neither stage removes it,
`ph64` correct on the site it covers with one OPEN candidate next door.** Five
rows, five different answers, and still no run.

---

## §8 The proof

```
requires  off + len <= buf@.len(),  24 <= len,  len <= 268435456
ensures   r == llist_fold(buf@, off as int, len as int)
39 verified / 0 errors           47 verified / 0 errors under --cfg slb_twin
```

`verus.rs`'s `llist_fold` is a **fuel-bounded recursion over the same arena the
exec code mutates**; `model.py`'s is a **closed form** with no list and no
cursor; and `model.py`'s other implementation is a structural list simulation
driven at both rungs. Three spellings, one number, and the gate drives the first
against the third.

⭐⭐ **The row's ladder result is that the guard discharges none of it.** `wf` —
every link is `NIL` or an in-range index, `next` ascends, `prev` descends — is
what licenses all eight unchecked accessors and every `decreases`, and **it holds
with `562f886ecb14` deleted.** Memory safety and the upstream fix are orthogonal
here, and only the value postcondition can see the difference. That is the
sharpest thing the temporal axis has produced so far and it is the opposite of
what the spatial rows say.

⚠ **Eight trusted `external_body` items with `ensures`** (plus `load_input` and
`emit`), which is more than any other row: the arena's element is a STRUCT, so an
unchecked accessor is needed per FIELD, and `DEL_LLIST_ELEMENT`'s unlink is two
different NEIGHBOUR writes. Each has a `SLB-TRUSTED-ARGUMENT` section in
`NOTES.md`, and the three writers' `ensures` name the WHOLE post-state precisely
because a neighbour write is what they do.

### §8a ⚠ One Verus behaviour worth a PITFALLS line

`del_element` originally used `return;` from inside its `while` loop. Its
postcondition **failed at that exit while an `assert` of the identical
proposition immediately before the `return` PASSED.** The repair is the C's own
spelling — `zend_llist_del_element:101` uses `break` — plus
`invariant_except_break` for the clauses that are false at the break, `invariant`
for those true at both exits, and a loop `ensures` for what the exits must agree
on. **An early `return` from inside a `while` in a `&mut self` function is where
to look when a postcondition fails at an exit whose facts are all provable.**

### §8b What made `kernel` verify

The structural fixes came first and the budget second: `register_all` split out;
`kernel` split into decode + `run`; and **`run_spec` marked
`#[verifier::opaque]` and revealed once inside `run`** — without which `kernel`'s
one-line body blew `rlimit(600)`, because Z3 unfolds `llist_fold` into the whole
composition, unfolds four recursive spec functions inside it, and then matches
that tree against itself with differently-spelled arguments. Opaque, it verifies
in seconds.

---

## §9 Process notes

- **`spec.md` is GENERATED** by `.temp/php32/mkspec.py` (rule 6's
  artefact-vs-generator note). The 11 003-byte named-spelling tail is lifted from
  `ph07` rather than retyped and `verus.items` is read with the gate's own
  `harness/vparse.py`.
- **`contract_sha256` moved three times after the pre-build record and all four
  values are in `NOTES.md` §0** with the reason for each. Two of the moves were
  the gate correcting me: the `identity` pin (I wrote `norel`, the measurement
  said `differ`) and the `idiom` block (my `forbidden` prose quoted
  `zend_llist_apply`, `l->count`, `DEL_LLIST_ELEMENT` and `--l->count` in
  backticks, which under the named-spelling standard made the row's own C rungs
  violate the row's own contract — **8 forbidden hits, and the gate failed
  exactly as designed**).
- ⚠ **I used the FULL row directory name on every `harness-php/gate.py`
  invocation** (F55 / open item 42). `results-php/preflight/` gained exactly one
  new file, `ph64-callback-frees-cursor.preflight.json`.
- ⚠ **`grep -a` / `/usr/bin/grep` / the `Grep` tool throughout** (F35), and every
  question about the tarball was asked about a FUNCTION.

---

## §10 Brackets

```
FIRST  python3 harness/measure.py --check-stale                 -> 66 record(s), 0 STALE
FIRST  python3 harness-php/gate.py --tool measure --check-stale -> 10 record(s), 0 STALE
LAST   (see §12)
```

⚠ The first reading was **10/0** exactly as the task file predicted; `_028`'s
landing (`995f5aa`, `89008e3`) is in `git log` before this task and moved nothing.

---

## §11 Reviewer checklist, answered

| question | answer |
|---|---|
| constant-folded? | no — stage 3a/3b green, `has_loop` true in every cell, and `d_ir_d_work` is 15–143 against a floor of 0.25 |
| data from the file at run time? | yes — `n`, `trigger`, `mode`, `reuse`, `post` and every name byte come out of the window; `controls/differential.py` drives 2 592 distinct windows through the shipped C |
| result consumed and printed? | yes — `slb_emit(acc)` |
| five rungs semantically equivalent? | **on the `u64`, yes** — 32 of 32 cells agree on both measured inputs. ⚠ **On MEMORY BEHAVIOUR, no, and §5 is the statement**: the C allocates `2n + 2` blocks per call and the Rust rungs model the counters |
| C rung idiomatic C? | it is transcribed PHP, `TSRMLS` removed; `controls/dump.c` + `plain_alloc.h` build the same kernel against libc `malloc` and reproduce `index.csv`'s recorded category |
| R2 a fair naive port? | yes — `Option<u32>` links, index by index, no adaptors. ⚠ It pays 16.5 % for an out-of-line `name_of`, which is a real cost of the naive spelling and is named |
| R3 check-free or check moved? | neither — R3 is R2 with a smaller `Node`, an inlinable name and `with_capacity`; the bounds checks are all still there |
| perf claim on an `O0` row? | none |
| Verus: `assume` / `external_body`? | 10 `external_body`, 0 `assume`, 0 `assume_specification`; 8 have `ensures` and 8 have verified twins; each argued in `NOTES.md` |
| `requires` satisfiable, call site real? | stage 5b green, and `main` asserts `r == llist_fold(...)` so the postcondition is consumed |
| `ensures` non-trivial? | it is the full value postcondition |
| TCB tally accurate? | 10 items, recounted against `verus.rs` |
| R5 exec matches R4? | to one instruction — §6 and `NOTES.md` §11 |
| numbers reproducible? | the whole chain is six commands and every control is one |
| adversarial behaviour per rung? | recorded — R1 signals on four inputs, every other rung returns |
| does the C exhibit the bug? | `heap-use-after-free`, `WRITE of size 4`, frame #0 SITE C, under ASan on plain `malloc`/`free` |

---

## §12 Verdict, brackets and `git status`

```
$ python3 harness-php/gate.py ph64-callback-frees-cursor
check.py: PASS                       verdict PASS, failures 0
                                     contract_sha256 7ec3fc87b30975c5827e6074b683302d461d1c402459a9983dd0e3cedd822aa6
```

**Three rounds, 19 -> 3 -> 2 -> 0 failures.** ⚠ **Rounds are not failure and
every extra one caught a real defect**, exactly as `TASK_PHP_018`'s eleven did:

| round | failures | what they were |
|---|---|---|
| 1 | **19** | 8 x `idiom-forbidden` (my `forbidden` PROSE quoted `zend_llist_apply`, `l->count`, `DEL_LLIST_ELEMENT`, `--l->count` in backticks, so the row's own C rungs violated the row's own contract); 1 x a trusted item with no verified twin; 8 x a missing `SLB-TRUSTED-ARGUMENT` section; 2 x `[tables]` |
| 2 | **3** | the twin I added was refused too -- `slb_twin_slice_subrange`'s body called `vstd::slice::slice_subrange` and step 5c-twin matches by IDENTIFIER, so it read as re-using the axiom; + 2 x `[tables]` |
| 3 | **2 then 0** | only `[tables]`, which is the irreducible `gate -> report -> gate` chain |

⭐ **Every one of those was the gate being right about the row.** The forbidden
hits in particular: I wrote "NO BACKTICKED SPELLING IN THIS ENTRY, deliberately"
and then used backticks, and the named-spelling standard caught the
contradiction.

**What the green record certifies**

```
verus.rs                     39 verified / 0 errors    47 under --cfg slb_twin
clause deletion              10 mutants, EVERY ONE fails -- no trusted `ensures`
                             conjunct is decoration
requires strength            11 `requires` conjunct(s) probed, none a tautology
                             under bare Z3, `nonlinear_arith` or `bit_vector`
sanitizer (R1)               fires on the 4 reuse inputs, clean on the other 4
sanitizer_hardened (R1h)     CLEAN ON ALL EIGHT, adversarial included
checksums                    32 of 32 cells agree on both measured inputs
identity                     unsafe vs verus `differ` at O0 and O3, as declared
miri                         required and run, `unsafe.rs`, 8 trusted items
```

**Brackets — first and last, both green**

```
FIRST  harness/measure.py --check-stale                  -> 66 record(s), 0 STALE
FIRST  harness-php/gate.py --tool measure --check-stale  -> 10 record(s), 0 STALE
LAST   harness/measure.py --check-stale                  -> 66 record(s), 0 STALE
LAST   harness-php/gate.py --tool measure --check-stale  -> 12 record(s), 0 STALE
```

⭐ **12/0, i.e. 10 + the row's two new records**, exactly as the task file
predicted. The PAT side is untouched at 66/0 both times.

**`git status --porcelain` at the end**

```
 M results-php/preflight/_norow.preflight.json
?? .tasks-php/TASK_PHP_032_REPORT.md
?? patterns-php/ph64-callback-frees-cursor/
?? results-php/gate/ph64-callback-frees-cursor.json
?? results-php/ph64-callback-frees-cursor.json
?? results-php/preflight/ph64-callback-frees-cursor.preflight.json
?? results-php/tables/ph64-callback-frees-cursor.md
```

⚠ **The ONE modified file is not mine in substance and it is disclosed rather
than reverted.** `results-php/preflight/_norow.preflight.json` gained **87
lines** — one appended run entry — because **the closing bracket itself writes
it**: `gate.py --tool measure --check-stale` names no row, so its preflight is
recorded under `_norow`. That is `TASK_PHP_009` m5's documented second-order
effect (*"a FAILING run grows a COMMITTED file"*, and a row-less run does too),
and `results-php/preflight/README.md` documents `_norow`. The diff is purely an
appended entry; nothing else in it moved. **The manager should decide whether to
commit it or restore it**; I have not touched it by hand.

⚠ **I used the FULL row directory name on every `gate.py` invocation** (F55 /
open item 42), so `results-php/preflight/` gained exactly one new file and no
stray short-name record.

**Every control, re-run against the SHIPPED tree after the green gate**

```
oracle.py        PASS (0 miss)     differential.py  PASS (0 miss)
next_cache.py    PASS (0 miss)     predicate.py     PASS (0 miss)
bug41037.py      PASS (0 miss)     asan_fidelity.sh heap-use-after-free reproduced
```

---

## §13 What I did NOT do

1. ⚠⚠ **No `controls/spellings.py`, and the debt is declared rather than
   carried.** §6's `fixed-R4 bound` is over an **unsearched** R4 endpoint and one
   R3 spelling. `TASK_PHP_025` shipped `ph16` the same way and it was right;
   `TASK_PHP_028` exists because three rows carried the debt silently. ⭐ **The
   spellings search on this row needs its own task**, and it is more interesting
   than usual: R3 is 20–25 % cheaper than R2 for two named reasons, so the R3
   side is plainly not at its minimum.
2. ⚠ **§7a is not measured.** No PHP built, no reproducer run.
3. ⚠ **I did not re-derive `_031`'s tag sweep, its patch fetch or its
   `preimage_all` census.** I reused `.temp/php31/` as instructed and re-verified
   only what the row leans on: every span's `extract_sha256` (the gate does this
   on every run) and the one span `_031` did not compute.
4. ⚠ **The `.memory-php/` and `RECAP_PHP.md` writes are the manager's.** I
   touched neither. §5 and §7's tally correction are proposals, not landings.
5. ⚠ **I did not measure a second R3 or R4 spelling, and I did not measure the
   index-scan R3** that `spec.md`'s `forbidden[2]` pins absent — it is named as
   the cheapest R3 candidate there is and left unbuilt on purpose, because
   building it is the spellings task.
6. ⚠ **`.temp/php32/` keeps the generators and the logs; every `.bin`, `.o` and
   `__pycache__` is deleted.** `mkspec.py`, `dump.c`, `dump.sh`,
   `diff_c_model.py` and `smoke.rs` re-derive everything, and every blob has a
   script that rebuilds it.
