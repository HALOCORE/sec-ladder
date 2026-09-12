# ph53 — NOTES

⚠ **`PROTOCOL.md` definition-of-done rule 6, recorded BEFORE ANY CELL WAS BUILT.**

> The `slb-contract` block's sha256 **as first written, before any measurement**:
> `c9b666d39db483dc386e23a4ab2f511f094855dbcdbc841c9ba33a01abe333bd`
>
> ⚠ The `git show HEAD:… | diff -` test rule 6 describes is **VACUOUS ON A NEW
> PATTERN** — a pattern lands in one commit, so on a clean tree it always prints
> nothing and always looks like it passed (`TASK_070_REVIEW`). The recorded hash
> above is the only evidence, which is why it is written here first.
>
> ⚠⚠ **IT MOVED ONCE, BEFORE ANY NUMBER WAS PUBLISHED, AND HERE IS WHY —
> rule 6's *"if the hash changes later, say so and say why"*.**
>
> | | |
> |---|---|
> | as first written | `c9b666d39db483dc386e23a4ab2f511f094855dbcdbc841c9ba33a01abe333bd` |
> | after the gate's `tcb-unsafe` repair | `e42a9b92247fe2db003caa2ed308d7faebb50353f65a478288fd557078b92b1f` |
> | **as shipped** | `7013be6f7c1cb70da7568716e7eef71908fd109332f64cf76cf769ba063a9d97` |
>
> **The first gate run FAILED with two `tcb-unsafe` blockers** and they were
> right: `check.py::_scan_unsafe_sites` requires every `unsafe` token in a
> pinned Verus source to sit inside an `external_body` item's body, and
> `unsafe { slot_get_unchecked(slots, i).assume_init() }` put one in ordinary
> exec code. §11.5 is the finding that came out of it. What moved in the fence:
> `slot_get_unchecked` (returning `MaybeUninit<u32>`) became
> `slot_read_unchecked` (returning `u32`, folding the `assume_init` in),
> `twin_obligations` went **31 → 30** because that item's twin cannot exist, a
> `twin_justifications` entry was added for it, and one
> `unsafe_justifications` entry was rewritten. ⚠ **`verus.obligations` did NOT
> move (27), the `identity` pin did NOT move (`differ`/`differ`), and no
> `requires`, `ensures`, `idiom` entry, `provenance` field or `why` moved** —
> the ladder and every number in §8 are unaffected, and §8's figures were
> re-measured after the change rather than carried over.
>
> ⚠⚠ **AND IT MOVED A SECOND TIME, FOR A DEFECT I HAD PUT THERE MYSELF.** The
> `e42a9b92…` block cited **`.temp/php41/probe_wrap.rs`** — twice, in
> `twin_justifications` and `unsafe_justifications` — as the evidence that
> `slot_read_unchecked`'s hand-asserted `requires` is the one vstd demands.
> ⛔ **That is `RECAP_PHP.md` open item 65's defect inside the HASHED block**:
> a committed claim resting on a gitignored path, and the probe is exactly the
> kind of file `CLAUDE.md` constraint 6 deletes. ✅ **Repaired by shipping the
> probe as `controls/mu_unwrapped.rs`** (7 verified / 0 errors), retargeting
> both citations at it, and adding it to `controls/negatives.py --verus` as
> must-NOT-fire arm **N2**, so it is *run* on every invocation rather than
> merely cited. Nothing else in the fence moved.
>
> ⚠⚠ **AND RULE 6 IS NECESSARY AND NOT SUFFICIENT** (`TASK_089_REVIEW`, on
> `p46`): a matching hash proves nothing was edited *after* measuring and
> nothing about a declaration measurement has since FALSIFIED. §12 is the
> re-read of the hashed `why` against the numbers actually obtained, and it
> names the one thing it would have struck if it had been in there.

---

## 1. What the row is

PHP 5.0.0 advances `ce->num_interfaces` once per `implements` clause **at
compile time** and writes no slot:

    opline->extended_value = CG(active_class_entry)->num_interfaces++;   :2591

and then grows the storage to that count and leaves it indeterminate:

    if (ce->num_interfaces > 0) {                                        :2570
        ce->interfaces = (zend_class_entry **) erealloc(ce->interfaces,
                         sizeof(zend_class_entry *)*ce->num_interfaces);  :2571
    }

`:3747-3748` set `num_interfaces = 0` and `interfaces = NULL`, so the
`erealloc` is a plain `malloc` and the **whole** array is indeterminate. A
consumer that runs before every `ZEND_ADD_INTERFACE` has executed reads a slot
nobody wrote.

⚠⚠⚠ **The read is IN BOUNDS.** Inside the reallocated block, nothing freed:
**CWE-824**, not CWE-125. `ph32` is the cross-reference, not the duplicate —
same C shape, sized to the *literal*, so its excess is past the end.

---

## 2. Tier, and the kernel-overlap number (`PROTOCOL_PHP.md` §F9)

**`tier: narrowed`.** `CATALOGUE.md` says `verbatim` and is wrong; the reason
is `TASK_PHP_040_REPORT.md` §5.1 and it is restated in the hashed `why`.

⚠ **`provenance.py` reports the kernel overlap at `9 %` against a `25 %`
expectation for `narrowed`, and §F9 asks what I think of it. Three things, and
the first is the largest:**

1. **The number is measuring identifier renaming, not extraction fidelity.**
   The defect span (`span0`) scores **1 of 2 lines**, and the line it misses
   differs from the tarball's in exactly three tokens: `zend_class_entry` →
   `ph53_iface` (the type is narrowed to its one relevant member),
   `erealloc` → `php_shim_erealloc` (which `PROTOCOL_PHP.md` §B *requires*),
   and the line break. ⭐ I moved `ce` from a local struct to a **pointer**
   specifically so the span would be spelled `ce->interfaces` as upstream
   spells it, and that alone took the span from 0 % to 50 % and the union from
   4 % to 9 %. There is no further honest move available: the remaining
   difference is two names the row is obliged to change.
2. **Five of the seven spans are CONTEXT and drag the denominator hard.**
   `span6` is `zend.h`'s 41-line `struct _zend_class_entry` and scores
   **0 of 32**, because the row lifts two of its 24 members and the divergence
   ledger says so. A row that cited fewer spans would score higher and tell a
   reader less. **The union denominator is 75 lines of which perhaps 15 are the
   mechanism**, so I read 9 % as ~45 % of the lines that could lift.
3. ⚠ **A reviewer could reasonably prefer `modelled`, and here is the argument
   I did not take.** §A2 says a divergence that CHANGES BEHAVIOUR is a
   `modelled` tier, and the faulting consumer's narrowing does change the
   answer: `instanceof_function`'s recursive parent-chain walk becomes a single
   identity test, so transitive interface implementation is not reported. What
   it does **not** change is the number of slot dereferences, which is the
   quantity the row measures. I kept `narrowed` because that is
   `TASK_PHP_040_REPORT` §5.1's assessment and `TASK_PHP_041.md` §2.2's
   decision, and because **a tier is a cost and never a filter** — nothing in
   the row turns on it. **But it is a judgement, not a measurement, and it is
   the call on this row I am least sure of.**

ⓘ `unevaluable_conditionals` is **1** (`#ifndef PH53_KERNEL_H`, the header
guard), so the residual the heuristic cannot see is one include guard.

---

## 3. Both shas, and which is which (`PROTOCOL_PHP.md` §F5(iii))

| | |
|---|---|
| **R1h** | `d09cdd9f71f34deab4b99f4e63523fb94164a724` — Dmitry Stogov, 2005-06-08, *"Fixed valgrind errors"*, 1 file, 1 hunk, **2 insertions, 1 deletion**, first shipped in **php-5.0.5**. `controls/d09cdd9f71f3.patch`, sha256 `4f97b625fc9772d6…`, 1 026 B |
| ⛔ **the corpus column** | `be8daf1f47fa` — Dmitry Stogov, 2008-03-12, *"Optimized ZEND_FETCH_CLASS + ZEND_ADD_INTERFACE into single ZEND_ADD_INTERFACE opcode"*. `controls/be8daf1f47fa.patch`, sha256 `42190b44ad8068c3…`, 7 397 B. **EXCLUDED, twice independently** |

Both excluded for reasons that do not depend on each other:

* `.tasks-php/preimage_screen.py` labels it `NOT-THE-REPAIR` — neither cited
  5.0.0 line is in the pre-image of its `Zend/zend_compile.c` hunk;
* the release-tag walk is decisive on its own: the cited `erealloc` line is
  present at `php-5.0.0` … `php-5.0.4` and **gone at `php-5.0.5`**, two years
  and nine months before that commit.

The 2005 commit's removed line is **byte-identical to 5.0.0's `:2571`**, and
`patch -p1 --dry-run` on the pristine tarball gives `Hunk #1 succeeded at 2568
(offset -14 lines)`, exit 0. `memset` is already used three times in 5.0.0's
`zend_compile.c` (`:250`, `:2190`, `:2191`), so the backport needs no new
include. **`diff c/kernel.c c/kernel_hardened.c` is that commit, the header
comment, and nothing else.**

⚠ The 2008 patch's bytes are kept *because* it is refuted: a later reader who
finds the column should not have to re-fetch it to re-refute it.

---

## 4. Reachability, settled in writing before any rung (`PROTOCOL_PHP.md` §A3)

Every cited site was read out of the pristine tarball
(`sha256 5783e0c0ba94f165633a…`) with `tar -xzOf … | sed -n 'a,bp'`, never from
an extracted tree, and every span is pinned by its own `extract_sha256` in
`spec.md`. All seven hold verbatim, including the two `TASK_PHP_040_REPORT` §3
had inferred rather than quoted:

| site | what it is |
|---|---|
| `zend_compile.c:2569-2572` | the defect. 174 B, `617c5c8532f0d9e4` |
| `zend_compile.c:2591` | `opline->extended_value = CG(active_class_entry)->num_interfaces++;` |
| `zend_compile.c:3747-3748` | `ce->num_interfaces = 0;` **and** `ce->interfaces = NULL;` — which is what makes the *whole* array indeterminate and not merely its tail |
| `zend_operators.c:1534-1535` | the faulting consumer, and the corpus's own `c_file_line` |
| `zend_compile.c:1951` | the compare-only consumer, `if (ce->interfaces[i] == entry)` |
| `zend_opcode.c:161-162` | `destroy_zend_class`'s `efree(ce->interfaces)` — the teardown the kernel carries |
| `zend.h:334-335` | `zend_class_entry **interfaces; zend_uint num_interfaces;` |

---

## 5. ⭐⭐ WHAT `d09cdd9f71f3` ACTUALLY BUYS — MEASURED, PER CONSUMER

This is the row's headline and it is measured in two controls, because the gate
**structurally cannot carry it**: `check.py` stage 7h requires the hardened C
rung clean under ASan+UBSan on **every** input in `inputs/`, in terms, and the
2005 fix adds **no consumer guard** — so every blob on which R1 dereferences an
unwritten slot is a blob on which R1h dereferences NULL. ▶ **The row whose
result is that the fix is incomplete cannot ship the input that shows it.**
That is `.memory-php/02-ladder.md` **F31**'s standing limitation binding on a
real row for the first time, and `controls/` is the resolution F31 prescribes.

### 5a. `controls/r1h_consumers.py --selftest` — `SELFTEST PASS`

Both C kernels, built with `check.py::_san_build`'s line character for
character (`gcc -std=c99 -Wall -Wextra -O1 -g -fsanitize=address,undefined
-fstrict-aliasing -static-libasan -static-libubsan -DSLB_ISOLATED`) and again
plain at `-O2`:

| blob | arm | rung | rc | u64 | diagnostic |
|---|---|---|---|---|---|
| `deref` | san | **R1** | 1 | — | `kernel.c:139:30: runtime error: member access within misaligned address 0xbebebebebebebebe for type 'struct ph53_iface'` → `SEGV on unknown address`, **caused by a READ** |
| `deref` | san | **R1h** | 1 | — | `kernel_hardened.c:178:30: runtime error: member access within null pointer of type 'struct ph53_iface'` → `SEGV on unknown address 0x000000000000` |
| `deref` | plain | R1 / R1h | −11 / −11 | — | SIGSEGV, both |
| `deref-nofill` | san | R1 / R1h | 1 / 1 | — | identical to the above |
| `cmp` | san | R1 / R1h | 0 / 0 | `454892050351138816` **both** | silent, both |
| `cmp` | plain | R1 / R1h | 0 / 0 | `454892050351138816` **both** | silent, both |
| `covered` | both | R1 / R1h | 0 / 0 | `16975370263282301184` **both** | silent — the must-NOT-fire control |

▶ **ONE HUNK, TWO SEVERITIES.** The 2005 fix turns a **wild-pointer
dereference into a deterministic NULL dereference** at
`zend_operators.c:1535`, and the process still dies; at `zend_compile.c:1951`
it turns an indeterminate comparison into a defined one. §A4's fidelity anchor
is met: `index.csv` records `crashes_pristine_5_0_0 = True`, `build = asan`,
`wild-pointer-deref`, CWE-824, and that is exactly what the `san` R1 row is.

⚠ **ASan does not see the uninitialised read.** The read is of an in-bounds
slot of a live allocation, which is MSan's class; what ASan reports is the
*dereference of the value that came out*, and it is deterministic only because
ASan fills fresh allocations with `0xbe`. **§9 is the Miri arm that sees the
read itself.**

### 5b. ⭐⭐ `controls/wild_choice.py --selftest --reps 5` — `SELFTEST PASS`, and it says something 5a cannot

5a *observes* the wild value. This control **chooses** it, by priming PHP
5.0.0's own size-class cache (`zend_alloc.c:150-168`, `:263-279`) with a known
payload and letting `:2571`'s `erealloc` pick the block straight back up —
`TASK_PHP_041.md` §3.5's recipe, and the reason it works is that `_efree` on a
cached class does **not** return the block to `malloc`, so the payload
survives.

```
R1  (erealloc, no memset):
  primed with &pool[3]     cmp_scan=1 (MATCHED UNWRITTEN SLOT)  deref hit=1 id=000c1a5500000004
  primed with &pool[5]     cmp_scan=2 (no match, CORRECT)       deref hit=0 id=0000000000000000
R1h (emalloc + memset):
  primed with &pool[3]     cmp_scan=2 (no match, CORRECT)       deref DIED signal=11
  primed with &pool[5]     cmp_scan=2 (no match, CORRECT)       deref DIED signal=11
```

Byte-identical over five runs, and the answer **moves with the priming** — so
the value really is chosen and not observed.

▶ **Two things this adds to 5a, and the second is the sharper:**

1. **The compare-only consumer is not harmless, it is merely non-fatal.** With
   the value chosen, `zend_do_inherit_interfaces` reports a duplicate that is
   not there — `cmp_scan=1` names an interface the class never implemented. In
   5a it happened to answer correctly, and *"correct"* could have been luck.
   **So `d09cdd9f71f3` is COMPLETE on this consumer**: NULL can never equal a
   pool address.
2. ⚠⚠ **And on the other consumer the fix does not merely fail to help — it
   trades one class of harm for another.** R1 with a plausible wild pointer
   returns a **silent wrong answer** (`hit=1`, the chosen id, no crash); R1h
   **always dies**. An integrity/confidentiality bug becomes a guaranteed
   availability bug. ⓘ I am stating that as what the two rows show and **not**
   as a claim about what upstream intended or about which is worse; the
   severity ordering depends on the deployment and the row does not have one.

---

## 6. The corpus, and what it is forbidden to contain

`inputs/gen.py` re-derives its coverage from the bytes it just wrote
(`PROTOCOL_PHP.md` §A2a rule 1) and `model.py::selfcheck` check 2 re-asserts
the same table over **the calls the driver actually makes**, which is the
sharper half. Arms reached: both arms of `:2570` (`n_decl` 0 and 6), all three
op codes with the `% 3` taken past one wrap, both consumers, all five arms of
the scan loop (zero iterations, first, last, middle, no match), all three head
words' `%` exercised.

⚠ **And, negatively, no measured window runs a QUERY with a slot unwritten.**
That is what makes R1 and R1h bit-identical on the measured path and therefore
what makes the R1-vs-R1h number a comparison between two runs of one program.
`gen.py` refuses a corpus that violates it and so does `selfcheck`.

⚠⚠ **The per-window work is NOT uniform and the row declares it rather than
eliding it**: one window in sixteen has `n_decl == 0`, because both arms of the
defect's own branch must be in the *measured* corpus and the two arms cannot
cost the same. That is exactly the regime `RECAP_PHP.md` **F88** warns about —
`probe_iters [100, 200]` is ONE DRAW of a sampling distribution — so every
family-B figure below is labelled as one draw and marked PROVISIONAL.

`model.py` carries **three** implementations (an imperative transcription of
the hardened C, a recursive mirror of `verus.rs`'s spec functions, and a
deliberately dumb snapshot-per-op spelling) and its `selfcheck` drives the
first two over **90 synthetic windows it builds itself** — `n_decl_w` 0..32,
`n_pool_w` 0..15, seven op orderings × four counts including every
uninitialised-slot shape the corpus may not contain, the four scan arms,
duplicate pool ids and an empty op stream.

⭐ **And the sweep carries its own controls, because a sweep that cannot fail
is not a check.** Three must-fire mutants of `iface_fold` and one must-NOT-fire
equivalent rewrite; the interesting one is **M3 — an unwritten slot reads as
pool index 0 — which the measured corpus CANNOT catch**, by construction, and
which the synthetic sweep does. That is `PROTOCOL_PHP.md` §A2a rule 2's
argument turned into a measurement rather than repeated.

---

## 7. ⭐ The `u64`, and the two things it does for free

⛔ `CATALOGUE.md`'s `▸ benign` line says the checksum is *"a fold of the
interface pointers read"*. **It cannot be**: a pointer is an address, so that
fold differs between rungs and between runs for reasons no rung chose — which
is precisely what a cross-rung checksum exists to rule out
(`TASK_PHP_041.md` §2.3, `RECAP_PHP.md` open item 74). Every term of the
shipped fold is an **index, an id or a count**:

    FILL         the decl index d
    QUERY_DEREF  the return value, the matched pool id (0 if none), the count
                 of slots examined
    QUERY_CMP    whether it matched, then the decl INDEX it stopped at
    finally      xor php_shim_tally()

⭐ **The `||` disjunct `ce->interfaces[i] == target` is deliberately absent
from the faulting consumer, and that is the one place an address could have
leaked into a control-flow decision every rung has to agree on.** It is
redundant (`p == q` implies `p->id == q->id`) and its only effect would be to
skip the dereference on the matching slot, which is written by construction.

⭐⭐ **AND THE TALLY MAKES BOTH ARMS OF THE DEFECT'S OWN BRANCH VISIBLE IN THE
CHECKSUM, FOR FREE.** `php_shim_tally()` is `0` when `n_decl == 0` (no
allocation at all) and `1000003 ^ 1000033 ^ (8·n_decl · 1000039)` otherwise.
`PROTOCOL_PHP.md` §B1.2 asks for the fold so that *the defect* lands in the
number; on this row it also lands `:2570`'s branch there, which is a property
of this row and not of the rule. The four Rust rungs reproduce it
arithmetically (§B forbids them the shim) and **the reproduction is exact
because the allocation count is O(1)** — verified: all six rungs agree bit for
bit on both measured inputs.

⚠ `PHP_SHIM_REAL_SIZE`'s `(size + 7) & ~7` rounding is written as `8 * n_decl`
in the four Rust rungs, because `8 · n_decl` is already 8-aligned so the
rounding is the identity on every value this row can produce, and because a
bitwise `&` on a spec-mode `int` has no type in Verus while R4 and R5 must be
the same program. `model.py::_real_size` keeps the rounding and applies it, so
the two spellings are checked against each other on every call.

### 7a. §B1a — the precondition HOLDS, and this row is its exception

**One `php_shim_erealloc` per call when `n_decl > 0`, none at all when
`n_decl == 0`, plus one `php_shim_efree` in the teardown. `FILL` and `QUERY`
allocate nothing and the interface pool is not allocated** (at `:2571` every
interface an `implements` clause names is an existing `zend_class_entry`). So
the count is **O(1) in the input**, `PROTOCOL_PHP.md` §B1a's precondition
holds, and **this row's cross-language column needs no allocator caveat** —
unlike `ph64`, which allocates `2n+2` per call with 60 % of its C rung's
instructions in libc `malloc`/`free`. §B1a.2's instruction to declare the order
anyway is discharged in `spec.md`'s `idiom.required` last entry.

---

## 8. The numbers, and the mechanism for each

⚠ **THE HEADLINE STATISTIC IS `A1` = `kernel_exclusive_ir / n_iters`,
`isolated`, and it is named as family A beside every figure** — `RECAP_PHP.md`
F91: on cells where two rungs' kernels differ by 1–2 instructions, `|B/A|` is
**49.6–393.9×**, so no callee-inclusive statistic can resolve a small code
difference, and that is the regime a `fixed-R4 bound` operates in.
⚠ **For the CROSS-LANGUAGE column A is the wrong statistic** (F85: 29 of 38
sign flips live there), so those figures are published in family `B1` below,
labelled, and **marked PROVISIONAL pending open item 62 (family C)**.

### 8a. Family A1 — `Ir(kernel)/call`, `O3 / isolated`

| rung | small.bin | large.bin | vs R1 (`c-gcc`), small | vs R1, large |
|---|---:|---:|---:|---:|
| **R1** `c-gcc` | 1 376.538 | 2 899.523 | — | — |
| **R1h** `c-gcc-h` | 1 379.721 | 2 878.640 | **+0.231 %** | **−0.720 %** |
| `c-clang` | 964.165 | 2 326.230 | −29.957 % | −19.772 % |
| `c-clang-h` | 972.676 | 2 334.721 | −29.339 % | −19.479 % |
| **R2** `safe_naive` | 1 472.435 | 3 635.131 | +6.967 % | +25.370 % |
| **R3** `safe_tuned` | 1 387.675 | 3 308.595 | +0.809 % | +14.108 % |
| **R4** `unsafe` | 1 116.947 | 2 835.952 | −18.858 % | −2.192 % |
| **R5** `verus` | 1 102.947 | 2 821.952 | −19.875 % | −2.675 % |

⚠ `O0` / `small.bin`, for the lowering only: R1 1 545.574, R1h 1 551.207,
`c-clang` 1 231.553, R2 5 043.128, R3 4 732.640, **R4 6 287.746**, R5
5 226.986 — at `-O0` every Rust rung is 3–4× the C and R4 is the dearest of the
six. **No performance claim rests on that row**; it is here because §8c's sign
flip is read off it.

⚠ `O0` figures are in `results-php/tables/ph53-iface-tail-uninit.md` and **no
performance claim rests on one** (`.memory/02-bench-rules.md`).

### 8b. What the upstream fix costs on the benign path

`TASK_PHP_040_REPORT` §2.5(2) predicted *"an O(n) `memset` on every class
declaration — a real, attributable number"*, against `ph52`'s predicted
0.00 %. **It is attributable and it is tiny, and its SIGN DEPENDS ON THE
INPUT**: `+0.231 %` on `small`, `−0.720 %` on `large`, `+0.364 %` on
`small`/`O0`. ⚠ **Both figures are quoted; neither is maxed over input**, which
is `check.py`'s own *"DO NOT MAX IT OVER INPUT"* rule and the thing `F82` was
corrected for.

**Mechanism** (§F8 — a cost with no mechanism is an incomplete row): at `O3`
both gcc arms have **exactly 858 padding-excluded kernel instructions** and
different `md5_fn` (`fa205ef2` vs `d96f5500`). The `memset` of `8·n_decl ≤ 128`
bytes is inlined to `xmm` stores and **replaces** the `erealloc` cache-lookup
path, so the *static* size is unchanged and only the dynamic mix moves. On
`clang` the static count moves by **+4** (399 → 403). ▶ **So the 2005 fix is
not "an O(n) memset added to the same code" — it is a `malloc`-arm swap plus a
vectorised fill, and at `n_decl ≤ 16` the fill is 1–2 stores.** That is why the
number is fractions of a percent and why it can go either way.

### 8c. The `fixed-R4 bound`, and it is NOT what was predicted

⚠ **`PROTOCOL_PHP.md`/`.memory-php/02-ladder.md`'s rule: a bound ships
LABELLED, beside a cheapest-found counterpart — and `controls/spellings.py`
was NOT built on this row, so the R3 and R4 endpoints are UNSEARCHED and every
figure here is a `fixed-R4 bound` over an unsearched endpoint.** The debt is
declared here, in `README.md` and in the task report; `ph03`, `ph64` and `ph45`
carry the same one and this row makes it **4 of 7**.

| | A1, small.bin, O3 | A1, large.bin, O3 | A1, small.bin, O0 |
|---|---:|---:|---:|
| `fixed-R4 bound` R3ship − R4ship | **+24.238 %** | **+16.666 %** | **−24.732 %** |
| R2ship − R4ship | +31.827 % | +28.180 % | −19.794 % |
| R5ship − R4ship | −1.253 % | −0.494 % | −16.870 % |

⚠⚠ **THE SIGN OF THE BOUND FLIPS BETWEEN `O0` AND `O3`, AND NO CLAIM RESTS ON
THE `O0` ROW.** At `O3` the bound is POSITIVE and large, which makes this row
**3 positive, 2 negative** over the five rows with a figure (`ph03` +12.19,
`ph64` +17.08, `ph53` +24.24 / +16.67 positive; `ph16` −1.22, `ph29` −6.06
negative). ⓘ `ph45` publishes A1 `+0.37 %` and whole-program `−3.06 %` and
belongs to neither list cleanly.

**Mechanism.** R3's `Vec<u32>` scan loops **vectorise** (352 static
instructions, `xmm`); R4's do not, because the per-slot `if wrote[i]` is a
branch inside the loop (758 static instructions). So R4 executes *more* static
code and *fewer* dynamic instructions — it is the **uninit fill and the absent
`Option` discriminant** that win, not the scan. §8e measures the witness
directly.

### 8d. R2 vs R1h — the R2 prediction, refuted in a measurable direction

`TASK_PHP_040_REPORT` §5.6 predicted *"R2 ≈ R1h and cheaper than a naive
bounds-checked scan"*. **R2 is +6.967 % over R1 where R1h is +0.231 %**
(small/O3), i.e. R2 is ~6.7 pp DEARER than the upstream fix, and on `large` the
gap is 25.370 % against −0.720 %, ~26 pp. ▶ **REFUTED**, and the mechanism is
the one the prediction's own arithmetic missed: `Option<u32>` is **8 bytes** on
this platform (a `u32` has no niche), so R2's `None`-fill moves the same bytes
as R1h's `memset` — but R2 then pays **a discriminant load and a branch on
every slot READ**, and the query loops outnumber the fill by `n_ops : 1`
(16 : 1 on `small`, 40 : 1 on `large`), which is exactly why the gap is four
times larger on `large`.

### 8e. ⭐⭐ What the R4/R5 witness costs — and it is the row's largest single number

`controls/negatives.py --cost`, `O3`, `inputs/small.bin`, whole-program `Ir`
under callgrind, against `controls/r4_nowitness.rs` (the same program with the
`wrote[]` witness deleted):

| | whole-program Ir | kernel insns | `md5_fn` |
|---|---:|---:|---|
| R4 as shipped | 31 997 489 | 760 | `fa5a36f96e02` |
| `r4_nowitness` | 26 275 913 | 260 | `03aca617e8f8` |
| **the witness** | **+5 721 576 (+21.775 %)** | **+500** | — |

⚠ **MEASURED CORPUS ONLY**: the two programs are not equivalent on an
uncovered blob — that is what the witness is for — so this is a cost
comparison and not a ladder rung.

**Mechanism.** 260 → 760 static instructions is not a byte per slot: the
witness-free scan loops are branch-free over a `Vec<MaybeUninit<u32>>` and LLVM
**vectorises and unrolls** them; `if wrote[i]` puts a data-dependent branch
inside the loop and both disappear. ▶ **So the cheapest witness that makes R4
provable costs 21.8 % of the whole run, and the reason is lost vectorisation
rather than the byte.** ⓘ A bitmask witness (`n_decl ≤ 16` fits one `u32`) is
the obvious candidate for a cheaper spelling and **is not built** — it is the
first thing a `controls/spellings.py` on this row should price.

### 8f. R4's prediction — the fill is PARTLY elided, and the number is small

§5.6 predicted *"LLVM elides the `MaybeUninit::uninit()` fill entirely and R4's
inner loop is byte-identical to R1's; if it does NOT elide, R4 pays an O(n)
write pass the C rung skips and lands near R1h."* Measured against a control
that pushes `MaybeUninit::new(0u32)` instead — a real zero fill, everything
else identical:

| | kernel insns | whole-program Ir, small.bin |
|---|---:|---:|
| `MaybeUninit::uninit()` (shipped) | 762 | 31 997 125 |
| `MaybeUninit::new(0u32)` | 764 | 32 137 956 |
| **difference** | **+2** | **+140 831 (+0.440 %), i.e. +5.63 Ir/call** |

▶ **BOTH HALVES OF THE PREDICTION ARE REFUTED.** The fill is **not elided
entirely** — LLVM elides the *value stores* and keeps the *loop*, so the
uninit version still pays the `Vec` length bookkeeping and saves ~5.6 Ir/call,
about one store per slot. And R4 does **not** land near R1h: it is **18.9 %
CHEAPER than R1** at `O3`/`small`. ⓘ The honest summary is that the fill was
never the interesting term on this row; the witness (§8e) is 50× larger.

### 8g. R3's prediction — refuted, and the corrected statement is narrower

§5.6 predicted *"R3 is the cheapest rung on the row"* and called it the
headline if it held. ▶ **REFUTED at `O3` on both inputs**: R3 is +24.238 % /
+16.666 % over R4 and +0.809 % / +14.108 % over R1. What holds is the **narrower
and still interesting** claim that **R3 is the cheapest SAFE rung** — 5.8 pp
cheaper than R2 on `small` and 9.0 pp on `large` — and that the restructuring
which makes it safe also deletes the `idx[]` array and the `Option`
discriminant. ⚠ At `O0` R3 IS the cheapest Rust rung (−25.201 % against R4),
which is the direction the prediction expected, and **no claim rests on an
`O0` row**.

### 8h. The cross-language column — family `B1`, LABELLED and PROVISIONAL

⚠⚠ **PUBLISHED IN FAMILY `B1`, `marginal_ir_per_call`, ONE DRAW at
`probe_iters [100, 200]`, AND MARKED PROVISIONAL PENDING OPEN ITEM 62 (FAMILY
C).** F85: 29 of the 38 sign flips in the corpus are cross-language, so A is
the wrong statistic here; F88: family B is one draw of a sampling distribution
and this row's per-window work is deliberately heterogeneous (§6), which is
exactly where the draw bites. ⛔ **No bare C-vs-Rust number is published.**

| rung | B1 `small.bin` | vs R1 | B1 `large.bin` | vs R1 |
|---|---:|---:|---:|---:|
| **R1** `c-gcc` | 1 510.090 | — | 3 081.720 | — |
| **R1h** `c-gcc-h` | 1 512.890 | +0.185 % | 3 061.610 | −0.653 % |
| `c-clang` | 1 104.560 | −26.855 % | 2 525.140 | −18.061 % |
| `c-clang-h` | 1 123.960 | −25.570 % | 2 545.740 | −17.392 % |
| **R2** `safe_naive` | 1 739.890 | **+15.218 %** | 3 993.770 | **+29.595 %** |
| **R3** `safe_tuned` | 1 527.200 | **+1.133 %** | 3 511.860 | **+13.958 %** |
| **R4** `unsafe` | 1 253.450 | **−16.995 %** | 3 062.750 | **−0.616 %** |
| **R5** `verus` | 1 239.450 | **−17.922 %** | 3 048.750 | **−1.070 %** |

⚠⚠ **FAMILY `B1`, `marginal_ir_per_call`, ONE DRAW at `probe_iters [100, 200]`,
PROVISIONAL pending open item 62.** ⭐ **A AND B AGREE IN SIGN AND CLOSELY IN
MAGNITUDE ON EVERY CROSS-LANGUAGE CELL OF THIS ROW** — the largest
disagreement is R2 on `small` (A +6.967 %, B +15.218 %, 8.3 pp) and the R3,
R4 and R5 cells agree to within 2–3 pp. That is the *opposite* of F85's regime,
and the reason is §7a: the allocation count is O(1) per call, so there is no
allocator term for B to include and A to miss. ⚠ **It is not evidence that A is
safe cross-language in general** — F86 shows no function of the shares can
certify A at any threshold — it is evidence about this row.

### 8i. ⭐ Does `[100, 200]` sit on a start-of-run transient? NO — a third data point on open item 69

F93 found that `ph29`'s does. Method: the marginal slope over six spans of
equal width, `O3 / isolated`, `small.bin`, whole-program `Ir` (deterministic
under callgrind, so it ran beside the gate):

| cell | 100→200 | 200→300 | 1000→1100 | 5000→5100 | 10000→10100 | 20000→20100 | `[100,200]` vs mean(far four) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `c-gcc` | 1510.090 | 1523.540 | 1501.650 | 1531.840 | 1501.110 | 1529.580 | **−0.393 %** |
| `c-gcc-h` | 1512.890 | 1527.140 | 1504.330 | 1535.590 | 1503.760 | 1533.370 | **−0.419 %** |
| `safe_naive` | 1739.890 | 1767.640 | 1727.140 | 1779.490 | 1728.310 | 1776.590 | **−0.741 %** |
| `safe_tuned` | 1527.200 | 1545.660 | 1517.100 | 1554.800 | 1518.240 | 1552.120 | **−0.545 %** |
| `unsafe` | 1253.450 | 1277.520 | 1242.990 | 1288.000 | 1243.440 | 1285.660 | **−0.915 %** |
| `verus` | 1239.450 | 1263.520 | 1228.990 | 1274.000 | 1229.440 | 1271.660 | **−0.925 %** |

▶ Within **0.39–0.93 %** on all six cells, and the far spans differ from *each
other* by about as much (`c-gcc` 1501.11 at 10000→10100 against 1529.58 at
20000→20100). ⭐ **So this row has no start-of-run effect — what it has is a
±1 % window-selection oscillation that is the same at `[100, 200]` as anywhere
else**, visible as the odd-numbered spans sitting ~1.8 % above the even ones.
⚠ It does not close item 69: it says `ph29`'s 32 % is not a property of the
`[100, 200]` choice as such, and it is consistent with F88's own control
(*"`ph03` reads 0.03 % because its per-window work is uniform"*). **Three
points now read: uniform 0.03 % (`ph03`), nearly uniform ~1 % (`ph53`, one
window in sixteen differing), heterogeneous 32 % (`ph29`)** — a hypothesis with
three supporting points, not a measured mechanism.

---

## 9. Miri — and on this row it is the only detector that sees the defect

`controls/negatives.py --miri`, four arms, all as declared:

| arm | | result |
|---|---|---|
| **A1** MUST-FIRE | `controls/r4_nowitness.rs` on an uncovered blob | ✅ `error: Undefined Behavior: constructing invalid value of type u32: encountered uninitialized memory, but expected an integer` |
| **A2** MUST-NOT-FIRE | `r4_nowitness.rs` on `inputs/small.bin` | ✅ silent — the measured corpus covers every slot, so even the witness-free program is clean there |
| **A3** MUST-NOT-FIRE | the shipped `unsafe.rs` on the same uncovered blob | ✅ silent — the witness works |
| **A4** MUST-NOT-FIRE | the shipped `unsafe.rs` on `inputs/small.bin` | ✅ silent |

⭐ **A1 is the only place in this tree where the DEFECT ITSELF is detected
rather than its consequence.** An uninitialised read of an in-bounds slot is
CWE-824; ASan's class is CWE-125, and what ASan reports on the C rung is the
SEGV after the dereference (§5a). A2 is what makes A1 a statement about the
COVERAGE rather than about the program.

---

## 10. The ladder, in one paragraph, and the `identity` pin

Four answers to one question — *was this slot written?*

| rung | how it answers | what it costs |
|---|---|---|
| R1 | it does not; the tail is indeterminate | — |
| R1h | zeroes the storage and **still faults** | ±0.2–0.7 % (§8b) |
| R2 | `Option<u32>` — 8 bytes per slot, a discriminant load and a branch per read | +6.97 % / +25.37 % over R1 |
| R3 | it does not need to: `Vec::len()` carries it, which is php-5.2.0's own repair | +0.81 % / +14.11 % over R1 |
| R4/R5 | one byte per slot in a stack array | −18.86 % / −2.19 % vs R1, and +21.8 % over a witness-free port (§8e) |

**`identity: unsafe vs verus, O0 differ, O3 differ`** — pinned `differ` because
that is what was measured **before the first gate run**: `O3` 762 (R4) vs 755
(R5) padding-excluded kernel instructions, `O0` 899 vs 803. The shipped record
reads 758 vs 741 at `O3` — the same verdict on `md5_fn`, `md5_fn_norel` and
`md5_raw`, all three `no`, at both levels.

⭐ **So the proved rung is CHEAPER than the unsafe one at both levels, with no
search at all** — A1 `−1.253 %` (small/O3), `−0.494 %` (large/O3) and
`−16.870 %` (small/O0, which supports nothing on its own). That is
`RECAP_PHP.md` **F82**'s observation on `ph45` and `ph64` arriving on a **third
row**, and by some margin the largest of the three.
⚠⚠ **DO NOT READ IT AS A COST OF PROOF IN EITHER DIRECTION.** Nothing about
the proof is in the binary: every `let ghost`, `assert` and `proof {}` erases
before codegen, and R5's exec code is R4's. What differs is that rustc sees a
larger module and allocates registers differently — `mov %rdx,%r15` where R4
keeps the value in `%rcx`, from the very first basic block. The row states the
difference and does not attribute it.

---

## 11. ⭐⭐⭐ THE VERUS-SIDE RESULT: THE OBLIGATION IS NOT DISCHARGEABLE OVER A FAITHFUL R4

**`verus.rs`: 27 verified / 0 errors; 30 / 0 under `--cfg slb_twin`.**
**Six trusted items, THREE twins** — the fourth cannot have one and §11.5 is
why.
`#[verifier::rlimit(60)]` on `kernel`, disclosed in `spec.md` with its reason.

`TASK_PHP_040_REPORT` §5.6 predicted *"R5 needs NO hand-rolled ghost state —
the obligation is literally `forall|i| … ==> v[i].mem_contents().is_init()`"*.
**Half right, and the half that is wrong is the more interesting one.**

**1. ✅ The memory obligation needs no hand-rolled ghost state, and it is
literally vstd's own `requires`.** `~/tools/verus/vstd/std_specs/maybe_uninit.rs`
ships `assume_specification` for `MaybeUninit::{new, uninit, assume_init,
assume_init_ref, assume_init_mut}`; `uninit()` ensures `MemContents::Uninit`
and every `assume_init*` carries `requires m.mem_contents().is_init()`. The
query loops' invariant is

    forall|j| 0 <= j < n_decl ==> (wrote@[j]
        ==> slots@[j].mem_contents().is_init()
            && slots@[j].mem_contents().value() < n_pool)

and its first conjunct *is* that `requires`. ⭐ **So in ordinary exec code
`assume_init` costs NO trusted item** — verified at **6 verified / 0 errors** in
`controls/mu_unwrapped.rs` — 7 verified / 0 errors, and it is COMMITTED — which
is the shape `unsafe { m.assume_init() }` sitting in a plain `fn` with vstd's
own precondition carrying it and no trusted item anywhere — while the
`get_unchecked` on the same line costs one: **0 files under
`~/tools/verus/vstd/` mention `get_unchecked` at all**, against four that
mention `assume_init`. ⓘ I re-verified both greps myself rather than taking
`_040`'s word, per `CLAUDE.md`'s standing warning about `std_specs/`.

⛔⛔ **AND THE SHIPPED ROW CANNOT USE THAT, FOR A REASON THAT IS THE ROW'S
SHARPEST INFRASTRUCTURE FINDING — §11.5.**

**2. ⛔ The VALUE postcondition does need one ghost `Seq`, and it is not a
`Seq<bool>`.** `run_ops` has to say what the kernel *returns*, and a spec
function cannot construct a `MaybeUninit` — `mem_contents` is `uninterp` and
there is no spec-mode constructor — so the spec-level slot array is a
`Seq<Option<u32>>` and `abst()` is the abstraction function from
`(slots@, wrote@)` onto it. **One ghost `Seq`, just not the one predicted
absent.**

**3. ⭐⭐⭐ And the residual risk `_040` named is SETTLED, in the direction that
helps.** `_040` §5.6 left open *"whether the `FILL` assignment through `Vec`'s
`index_mut` carries a value-level `ensures`"*. **It does**, and the whole of
it: `~/tools/verus/vstd/std_specs/vec.rs:67-78`'s `vec_index_mut` ensures
`*element == old(vec)@.index(i)`, `final(vec)@ == old(vec)@.update(i, *final(element))`
**and** `*final(element) == final(vec)@.index(i)`. A probe
(`.temp/php41/probe_mu.rs`, 5 verified / 0 errors) confirmed it before any rung
was written, and `controls/mu_unwrapped.rs`'s `fill` is that assignment,
committed and re-run by `controls/negatives.py`. ⚠ The shipped rung does not use it — it goes through
`slot_set_unchecked` because the C's write is unchecked — but the answer is now
recorded so nobody greps for it a third time.

**4. ⚠⚠⚠ AND THE THING NEITHER PREDICTION ANTICIPATED: A FAITHFUL R4 CANNOT BE
VERIFIED AT ALL.** The faithful unsafe port scans `0..num_interfaces` and
`assume_init()`s every slot — `zend_operators.c:1534-1535` with nothing between
the loop and the read. Whether slot `i` was written is a property of the **op
stream**, i.e. of attacker data; `spec.md`'s driver loop is pinned canonical
and calls `kernel(buf, k * stride, stride)` with no test, so **there is no call
site at which coverage could be established and no `requires` that could carry
it.** ▶ **A rung that reproduces the defect cannot be verified and a rung that
verifies does not reproduce it.** Measured, not argued:
`controls/negatives.py --verus` mutant **M1** deletes the two `if wrote[i]`
guards from the shipped proof and Verus refuses it at
`vstd/std_specs/maybe_uninit.rs:40:13`, `failed precondition`, 25 verified /
2 errors. ⛔ **That is the reason the shipped R4/R5 carry a witness the C does
not have, and it is a FINDING rather than a problem with the row**
(`CLAUDE.md` rule 6).

**5. The fourth obligation, and it is the price of the representation.**
`pool_get_unchecked`'s `i < MAXP` is **not** part of the C's obligation: the C
stores a `zend_class_entry *` and needs only that the pointer designate a
class, while safe Rust cannot store an address in memory it owns, so all four
Rust rungs store an INDEX (ph45's precedent) — and an index needs a **range**
as well as an initialisedness. ⭐ So where the C has one fact the proof has a
conjunction, and mutant **M2** (delete the `value() < n_pool` conjunct) refuses
independently of M1, which is what makes that a measurement rather than a
story.

**5. ⛔⛔⛔ TWO SOUND GATE RULES ARE JOINTLY UNSATISFIABLE FOR A `MaybeUninit`
READ, AND THE FIRST GATE RUN IS WHERE THAT WAS FOUND.**

The row as first written put `unsafe { slot_get_unchecked(slots, i)
.assume_init() }` in the two query helpers' exec bodies — the shape §11.1's
probe verifies — and kept `assume_init`'s obligation where vstd puts it. **Gate
run 1 refused it, twice:**

```
tcb-unsafe  verus.rs:533 an `unsafe` token sits outside every trusted item's
            body, so no `requires` rule and no verified twin governs it.
tcb-unsafe  verus.rs:582 (the same, in the other consumer)
```

**The rule is right, and it has no justification hatch**
(`check.py::_scan_unsafe_sites`): an `unsafe` token outside a trusted body is
an unchecked operation no `requires` demands and no twin checks, which is
`TASK_009_REVIEW`'s blocker x1. ▶ **But the obvious repair collides with the
OTHER rule.** Wrapping the read in an `external_body` item makes 5c-twin
require a **verified twin** with the same contract — and a twin's body must get
a `u32` out of a `MaybeUninit<u32>`, for which the pinned vstd offers exactly
three routes (`assume_init`, `assume_init_ref`, `assume_init_mut`) and **all
three are `unsafe fn`**. There is no safe exec expression from `MaybeUninit<T>`
to `T`; that is what the type *means*. So the twin's body would contain an
`unsafe` token outside a trusted body, which the first rule refuses.

**What shipped, and what it costs.** `slot_read_unchecked` folds
`get_unchecked` and `assume_init` into **one** trusted item with one conjunct
of `requires` for each, and its twin is justified away in
`verus.twin_justifications` with the argument above.

| | |
|---|---|
| TCB item count | **unchanged** — one item either way |
| twins | **3 of 4** unchecked accessors, so 5c-twin still measures something and its `ok` line correctly does not fire |
| what is lost | `assume_init`'s precondition is now **asserted by this contract** rather than **taken from vstd** |
| what replaces the twin | ⭐ **`controls/mu_unwrapped.rs`, a COMMITTED control**, verifies the UNWRAPPED shape at **7 / 0** with **no trusted item at all** — vstd's own `assume_specification` carrying the obligation — so the asserted contract is demonstrably the one vstd asserts, which is a *stronger* object than a twin (a twin re-states a contract; this derives it). `controls/negatives.py --verus` runs it as must-NOT-fire arm **N2**. Plus M1/M2 (§11a) and the Miri arms (§9) |

⚠ **This is a finding about the infrastructure and not a complaint.** Both
rules earned their place (x1 deleted a whole regime; the twin rule is the only
stage that judges *strength* rather than triviality), and neither is wrong. The
row is simply the first to hold a type for which no safe checked stand-in
exists. ⓘ **I did not propose a harness change**: `harness/` is frozen for this
programme and a `spec.md`-side declaration plus a probe is the cheaper answer.
If a second row ever needs it, the shape of a repair would be *"a
`twin_justifications` entry whose text names a type with no safe reader"*, and
it should be brought to the manager as a proposal rather than assumed.

### 11a. `controls/negatives.py --selftest` — the whole suite

| | | result |
|---|---|---|
| **M1** MUST-FIRE | the two `if wrote[i]` guards deleted | ✅ refused, `vstd/std_specs/maybe_uninit.rs:40:13 failed precondition`, 25/2 |
| **M2** MUST-FIRE | the `value() < n_pool` conjunct deleted | ✅ refused, `precondition not satisfied` ×2, 26/1 |
| **M3** MUST-FIRE | the kernel body replaced by `0u64` | ✅ refused, `postcondition not satisfied`, 21/1 |
| **M4** MUST-FIRE | the `idx@[j] == j` conjunct deleted | ✅ refused, `precondition not satisfied` / `index in bounds`, 26/1 |
| **N1** MUST-NOT-FIRE | the SHIPPED `verus.rs`, plain and twin | ✅ 27/0 and 30/0, matching `spec.md` |
| **F1** MUST-FIRE | `kernel_fingerprint` on a missing binary | ✅ raises |
| **F2** MUST-FIRE | a binary whose only symbol is `notkernel` | ✅ raises |
| **N2** MUST-NOT-FIRE | `controls/mu_unwrapped.rs`, the UNWRAPPED obligation | ✅ 7/0, no trusted item — §11.5's substitute for the missing twin |
| **F3** MUST-NOT-FIRE | `kernel` beside `a_kernel` | ✅ unambiguous, 8 insns |

⭐ **F1–F3 are `RECAP_PHP.md` open items 57 and 63, fixed in this row's copy
and not inherited.** The shared `spellings.py` machinery's `kernel_fingerprint`
returns `(0, md5(""))` for a binary that does not exist — so **two missing
binaries compare EQUAL on the one function whose job is to decide
byte-identity** — and its needle is a bare substring, so a crate named
`nokernel` fingerprints its own `main`. **This row does not clone that code**:
its fingerprint checks `objdump`'s return code, refuses an empty disassembly,
anchors the needle on `::kernel` at the end of the demangled symbol and refuses
more than one match, with the three negatives above. ⓘ Nothing in `ph16`'s or
`ph29`'s tree was touched. **The general shape both items record is that a
control cloned between rows carries its defects and only the row that writes
NEW negatives finds them; the cheaper move is not to clone.**

### 11b. One Verus fact worth the next agent's time

⚠⚠ **A Verus `while` body sees the loop INVARIANTS and the loop condition and
NOTHING from before the loop.** Both query helpers return from *inside* their
loop on a match, and with `target` bound only by a `let ghost` before the loop,
**both early exits fail their postcondition while every assert inside them
passes** — which is a confusing way to be told that a binding is out of scope.
The repair is one invariant clause per helper, pinning the ghost to the
postcondition's own expression. `instanceof_ex`'s comment says so in the file.

---

## 12. Rule 6's second half — the hashed `why` re-read against the numbers

`PROTOCOL.md` DoD 6: *a frozen declaration is evidence about when it was
written, not about whether it is still true.* Re-read in full. **Nothing in the
hashed block is refuted by the measurements**, and the two places it came
closest are worth naming:

1. The `why` says R4/R5 *"answer it with ONE BYTE PER SLOT in a stack array and
   a test/jz"*. That is a statement about the **source** and it is true. ⚠ It
   would have been **false as a cost claim** — the witness costs 21.8 % (§8e),
   because the branch defeats vectorisation — and it does not make one. Had it
   said *"cheaply"*, §8e would have struck it.
2. `identity.why` quotes 762/755 and 899/803 from the pre-gate measurement; the
   shipped record reads 758/741 at `O3`. **The VERDICT is unchanged (`differ`
   at both levels, all three hashes `no`)** and the difference is that the
   pre-gate probe counted the raw objdump grouping while the record counts the
   `nm` symbol extent. §10 gives both, labelled.
3. ⚠ **The `O0` `Ir` figures moved when §11.5's fold landed** — `unsafe`
   158 179 024 → 157 193 640 and `verus` 134 616 174 → 130 674 638 — because at
   `-O0` the extra function-call boundary the fold removes is real. **Every
   `O3` figure is byte-identical before and after** (the helper is
   `#[inline(always)]`), and the `O3` `md5_fn`s agree. §8a and §8c carry the
   re-measured numbers; nothing in this file quotes a pre-fold `O0` figure.

⛔ **What the row does NOT claim, stated because the absence is the finding:**
no rung of this row reproduces the defect except R1, and `controls/` is where
the Rust-side reproduction lives. And no figure here is a search: `README.md`
and §8c carry the unsearched-endpoint debt.

---

SLB-TRUSTED-ARGUMENT verus.rs win_get_unchecked

**(a) Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*v.get_unchecked(i)`; the twin's body is `v[i]`. The standard
library documents `get_unchecked(i)` as `index(i)` with the bounds check
removed, so it is the same operation on the same slice at the same index, and
Verus checks the bound `v[i]` needs against the same `requires`. A defensive
twin — `if i < v.len() { v[i] } else { 0 }` — cannot satisfy the `ensures` and
so fails the stage rather than passing it.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes *as the body stands*: one expression, one unchecked read,
at index `i` of slice `v`, and `ensures r == v@[i as int]` names that index and
that slice. ⚠ **Nothing mechanical enforces it.** A second unchecked read the
`ensures` never mentions — `let _peek = *v.get_unchecked(i + 1);` — is
invisible to 5a, 5c, 5c-req and 5c-twin alike. This row's backstops are Miri
(§9, which exercises this wrapper 12 or 40 times per call at indices up to
`len - 1`) and the fact that an extra read would move `md5_fn` — but
`identity` here is `differ`, so a `verus.rs`-only extra read would NOT be
caught by stage 3c the way it is on a row pinned `exact`. **That asymmetry is
stated rather than elided: on this row (b) rests on Miri and on review.**

**(c) Does each clause mean the same thing in both configurations?** Yes. Both
clauses are over `v@` and `i`, which are the function's own arguments; neither
mentions a `cfg`, a global, or anything the `slb_twin` configuration changes.
`v@` is `vstd`'s slice view in both, and `spec_slice_len`'s axiom is broadcast
at module scope in both.

---

SLB-TRUSTED-ARGUMENT verus.rs slot_read_unchecked

**(a) Is the twin's body the right checked stand-in?** ⛔⛔ **THERE IS NO TWIN,
AND THERE CANNOT BE ONE — see §11.5, which is the row's finding rather than a
concession.** A twin has to be a VERIFIED exec function meeting this contract,
whose `ensures` is `r == v@[i as int].mem_contents().value()`, so its body must
get a `u32` OUT of a `MaybeUninit<u32>`. The pinned vstd offers exactly three
routes — `assume_init`, `assume_init_ref`, `assume_init_mut` — and **all three
are `unsafe fn`**; there is no safe exec expression from `MaybeUninit<T>` to
`T`, which is what the type means. Any twin's body would therefore contain an
`unsafe` token outside a trusted item's body, and
`check.py::_scan_unsafe_sites` refuses exactly that, with no hatch. **Two sound
rules, jointly unsatisfiable for this one operation.** ⚠ **So what is NOT
checked here is precisely what a twin checks: that this `requires` is STRONG
ENOUGH to license a checked implementation.** What replaces it: (i)
`.temp/php41/probe_wrap.rs` verifies the UNWRAPPED shape at 6 verified / 0
errors — superseded by the COMMITTED `controls/mu_unwrapped.rs` at 7 / 0, which
is what `controls/negatives.py --verus` arm N2 runs — i.e. vstd's own
`assume_init` specification carrying the same obligation in ordinary exec code
with no trusted item, so the contract asserted here is demonstrably the one
vstd asserts; (ii) `controls/negatives.py` M1 deletes the
guard that supplies the initialisedness conjunct and Verus refuses at
`vstd/std_specs/maybe_uninit.rs:40:13`; (iii) M2 deletes the range conjunct and
Verus refuses independently; (iv) §9's Miri arms are silent on the shipped rung
and loud on the witness-free control.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** The body is `unsafe { (*v.get_unchecked(i)).assume_init() }` —
**TWO** unchecked operations in one expression — and the `requires` has one
conjunct for each: `i < v@.len()` for the slice access and
`v@[i as int].mem_contents().is_init()` for the `assume_init`. The `ensures`
names the value of that one slot and nothing else, which is complete *as the
body stands*. ⚠⚠ **Nothing mechanical enforces it, and on this item that
matters more than on the other three**, because this is the item whose twin is
missing: a second unchecked read the `ensures` never mentions would be
invisible to 5a, 5c, 5c-req and 5c-twin alike, and `identity` on this row is
`differ`, so stage 3c would not catch a `verus.rs`-only extra read either.
**On this item (b) rests on Miri and on review, and I am saying so rather than
implying a backstop the row does not have.**

**(c) Does each clause mean the same thing in both configurations?** Yes, and
the question is thinner than usual here because there is no twin configuration
to differ from: both clauses are over `v@` and `i`, which are the function's own
arguments; `MaybeUninit<u32>`'s view is the opaque
`external_type_specification` type in every build and `mem_contents()` is
`uninterp` in every build, so nothing about the clauses' meaning can depend on
a `cfg`. The token `slb_twin` appears nowhere but on the three twins' own
`#[cfg]`.

---

SLB-TRUSTED-ARGUMENT verus.rs slot_set_unchecked

**(a) Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*v.get_unchecked_mut(i) = x` and the twin's body is `v[i] = x` —
the same store of the same value at the same index with the bounds check
restored. `Vec`'s `IndexMut` is specified in the pinned vstd
(`std_specs/vec.rs`'s `vec_index_mut`, with a full value-level `ensures`), so
the twin is verified against a real specification and not against another
axiom.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes, and this is the item where completeness does the most
work. The body performs **one** unchecked store, and the `ensures` names the
**whole post-state** — `final(v)@ == old(v)@.update(i as int, x)` — not merely
`final(v)@[i] == x`. So a body that also clobbered `v[i + 1]`, or that
truncated the vector, or that left any other element moved, **could not satisfy
it**. ⚠ That is the completeness class `TASK_009_REVIEW` x4 names, and it is
why `miri.required` is `true` on this row: `x: MaybeUninit<u32>` is a pure
value and needs no precondition of its own, because every one of its
inhabitants is a legal store into a slot of that type, initialised or not — so
the *only* thing between this wrapper and a wild write is `i < old(v)@.len()`.

**(c) Does each clause mean the same thing in both configurations?** Yes. The
`requires` is over `old(v)@.len()` and `i`; the `ensures` is over `old(v)@`,
`final(v)@`, `i` and `x`. All five are the function's own arguments or their
views, none mentions a `cfg` or a global, and `Seq::update` is the same spec
function in both builds.

---

SLB-TRUSTED-ARGUMENT verus.rs pool_get_unchecked

**(a) Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*a.get_unchecked(i)` on a `&[u64; MAXP]` and the twin's body is
`a[i]`; the pinned vstd specifies `<[T; N]>::index` (`std_specs/slice.rs:81`),
so the twin is verified against a real specification. ⚠ The array's length is
in its **type**, so `a@.len() == MAXP` holds for every `a` this signature
admits (vstd's `array_len_matches_n`) and there is nothing left for a
`requires` to say beyond the index — which is why the `requires` is `i < MAXP`
and not `i < a@.len()`.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes as the body stands: one unchecked read, at index `i`, and
`ensures r == a@[i as int]` names it. ⚠⚠ **And the precondition this item
carries is the one that is NOT part of the C's obligation**, which is worth a
reviewer's attention rather than a footnote: the C's slot holds a
`zend_class_entry *` and needs only that the pointer designate a class, while
the four Rust rungs store an index — so `i < MAXP` is the price of the
representation and mutant M2 (`controls/negatives.py`) refuses the proof
independently of M1 when the invariant that supplies it is deleted. Nothing
mechanical enforces completeness here either; Miri and review are the backstop.

**(c) Does each clause mean the same thing in both configurations?** Yes. Both
clauses are over `a@`, `i` and the compile-time constant `MAXP`, which is a
plain `pub const usize` outside any `cfg`. `MAXP` is 8 in both builds and
`a@`'s meaning is vstd's array view in both.
