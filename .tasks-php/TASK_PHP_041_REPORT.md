# TASK_PHP_041 — REPORT · `ph53-iface-tail-uninit` BUILT · row 7 and the first `T3` row

**Role:** research engineer, alone. **Brackets:** `66/0` and `14/0` first,
`66/0` and `16/0` last (§10). **Spec:** `TASK_PHP_040_REPORT.md` §5.

---

## §0 THE ANSWER IN ONE TABLE

| | |
|---|---|
| row | `patterns-php/ph53-iface-tail-uninit/` — complete: `spec.md`, `model.py`, `inputs/gen.py` + 7 blobs, `c/{kernel,kernel_hardened,main}.c` + `kernel.h` + the shim symlink, `safe_naive.rs`, `safe_tuned.rs`, `unsafe.rs`, `verus.rs`, **8 `controls/` files** (6 code + both fix patches), `NOTES.md`, `README.md` |
| gate | ⭐ **`PASS-WITH-BLOCKED-ROWS`**, `failures []`, `complete_run True`, `verus 27 verified / 0 errors / 27 pinned`, `miri ran`, `sanitizer_hardened fired False on all 7 inputs`. ⚠ **`verus_checked` is absent from the record** — on this row and on `ph45`/`ph64` — so §1 quotes what is actually there instead |
| tier | **`narrowed`** as §2.2 directed, against the catalogue's `verbatim`. ⚠ Kernel overlap **9 %** against a 25 % expectation, and `NOTES.md` §2 gives my view, including the argument for `modelled` that I did **not** take |
| R1h | `d09cdd9f71f3` (2005-06-08), **not** the corpus column's `be8daf1f47fa` (2008); **both cited in `spec.md`, both patches under `controls/`** |
| ⭐⭐ §2.1's central claim | **MEASURED AND CONFIRMED, PER CONSUMER.** R1 → `member access within misaligned address 0xbebebebebebebebe` → SEGV; R1h → `member access within null pointer` → `SEGV on unknown address 0x000000000000`; `QUERY_CMP` exit 0 and the same `u64` on both arms |
| ⭐⭐⭐ §2.5's predictions | **THREE OF FOUR REFUTED** (R2, R3, R4); R5 **HALF refuted**; and the row found a fifth thing neither prediction anticipated — §3 |
| ⭐⭐ the row's own result | **a faithful R4 CANNOT BE VERIFIED AT ALL**, and the cheapest witness that makes it provable costs **+21.8 %**. §3.5, §4 |
| §2.6 | headline in **A1**, cross-language in **B1** labelled + PROVISIONAL, and ⭐ the optional F93 probe was **reached and answers NO** — §7 |
| §2.4 | §B1a's precondition **HOLDS** (O(1) allocations/call), declared in `spec.md`, and the cross-language column carries no allocator caveat |

---

## §1 THE GATE, QUOTED

*(quoted rather than summarised, per §4.2 of the task file.)*

**`results-php/gate/ph53-iface-tail-uninit.json`, quoted field by field:**

```
verdict           = PASS-WITH-BLOCKED-ROWS
failures          = []
complete_run      = True
verus_checked     = None
problems          = <KEY ABSENT from the record; the preflight's `problems` is []>
contract_sha256   = 7013be6f7c1cb70da7568716e7eef71908fd109332f64cf76cf769ba063a9d97
loud              = 6 entries
```

⚠ **`verus_checked` and `problems` are BOTH ABSENT FROM THE RECORD**, and I am
quoting the absence rather than rounding it up: neither key exists on this row,
on `ph45`'s or on `ph64`'s, so the task file's *"`verus_checked` and `problems`
quoted"* asks for two fields this harness does not write into a gate record.
(`problems` **is** a field of the **preflight** record, and it is `[]`.) ▶ **What the record does carry, and it is the thing the
field was standing in for:**

```
verus["verus.rs"]      = {"verified": 27, "errors": 0, "pinned": 27,
                          "tcb_items": [win_get_unchecked, slot_read_unchecked,
                                        slot_set_unchecked, pool_get_unchecked,
                                        load_input, emit],
                          "axiom_decls": [], "global_decls": []}
verified_twins         = 3 twins for 6 trusted items (win_get_unchecked,
                         slot_set_unchecked, pool_get_unchecked), signature_identical
                         true on all three
identity               O0 differ (expected differ) 888/888 vs 789/789
                       O3 differ (expected differ) 764/758 vs 746/741
                       md5_raw_equal false at both levels
miri                   ran = True, blocked = 0
sanitizer              7 inputs, all clean as declared
sanitizer_hardened     fired = False on ALL SEVEN inputs
idiom_audit            spellings 15, rungs 6, pairs 46, present 20,
                       forbidden_spellings 6, forbidden_hits 0,
                       required_pins_nothing 0, required_absent 8,
                       forbidden_unaudited_entries 1, no_rung_entries 0
```

**`results-php/preflight/ph53-iface-tail-uninit.preflight.json`, newest run:**

```
shim_ok              = True
c_digest_ok          = True
allocator_symlink_ok = True     (ph53: c/emalloc_shim.h OK -- symlink, in BOTH digests)
provenance_checked   = True
problems             = []
```

`harness-php/gate.py --audit` → **`preflight coverage: complete`**.

⭐ **`sanitizer_hardened.fired == False` on all seven inputs is stage 7h being
SATISFIED, not bypassed** — and §4 is why that is the row's result rather than
a gap: the input on which R1h *would* fire cannot be in `inputs/`.

**The one `!!` BLOCKED line, quoted because it is the row's finding and not a
gap to skim:**

```
!!  BLOCKED [twin] verus.rs `slot_read_unchecked` (strength unchecked):
    trusted item `slot_read_unchecked` has NO verified twin
    `slb_twin_slot_read_unchecked`, so its `requires`
    ['i < v@.len()', 'v@[i as int].mem_contents().is_init()'] was never tested
    for STRENGTH -- only for triviality (5c-req) and parameter mention (5a),
    both of which `i <= v@.len()` passes. spec.md justifies it: ...
```

### 1a. ⭐⭐ THE FIRST GATE RUN FAILED, AND IT FOUND THE ROW'S SHARPEST INFRASTRUCTURE FINDING

`.temp/php41/14-gate1.log`, verdict `FAIL`, four failures — two `tables`
(expected: the first gate on a new row must fail on them, `PROTOCOL_PHP.md` §E)
and **two that were not expected and were right**:

```
tcb-unsafe  verus.rs:533 an `unsafe` token sits outside every trusted item's
            body, so no `requires` rule and no verified twin governs it.
tcb-unsafe  verus.rs:582 (the same, in the other consumer)
```

`check.py::_scan_unsafe_sites` requires every `unsafe` token in a pinned Verus
source to sit inside an `external_body` item's body, with **no justification
hatch** — and the row as first written put `unsafe { slot_get_unchecked(slots,
i).assume_init() }` in ordinary exec code, which is exactly the shape §3.4's
probe verifies and exactly the shape that makes `assume_init` free.

▶ **Two sound gate rules are jointly unsatisfiable for a `MaybeUninit` read**,
and §11.5 of `NOTES.md` is the write-up. The short version: wrapping the read
in an `external_body` item makes 5c-twin demand a **verified twin**, whose body
must get a `u32` out of a `MaybeUninit<u32>` — for which the pinned vstd offers
`assume_init`, `assume_init_ref` and `assume_init_mut` and **all three are
`unsafe fn`**. There is no safe exec expression from `MaybeUninit<T>` to `T`;
that is what the type means. So the twin's body would contain an `unsafe` token
outside a trusted body, which the first rule refuses.

**What shipped:** `slot_read_unchecked` folds `get_unchecked` and `assume_init`
into **one** trusted item with one `requires` conjunct for each, and its twin is
justified away in `verus.twin_justifications` with that argument. **The TCB item
count is unchanged** (one item either way); what is lost is that
`assume_init`'s precondition is now asserted by the contract rather than taken
from vstd, and `.temp/php41/probe_wrap.rs` (6 verified / 0 errors on the
unwrapped shape) is what keeps the asserted contract checkable against vstd's.

⚠ **It cost a `contract_sha256` move and a re-measure**, both disclosed:
`c9b666d39db483dc…` → `e42a9b92247fe2db…`, in `NOTES.md`'s first box with what
moved and what did not. `verus.obligations` stayed 27, `twin_obligations` went
31 → 30, the `identity` pin did not move, and **every `O3` figure is
byte-identical before and after** because the folded helper is
`#[inline(always)]`; the two `O0` `Ir` figures that did move are named in
`NOTES.md` §12.3.

⛔ **I did not propose a `harness/` change.** `harness/` is frozen for this
programme and both rules earned their place — x1 deleted a whole regime and the
twin rule is the only stage that judges *strength* rather than triviality. A
`spec.md`-side declaration plus a probe is the cheaper answer, and if a second
row ever needs it the shape of a repair (*"a `twin_justifications` entry whose
text names a type with no safe reader"*) is a proposal for the manager rather
than something to assume.

### 1a2. ⚠ AND THE HASHED BLOCK THEN CITED A GITIGNORED PATH — MY DEFECT, FOUND BY MY OWN CITATION CHECK, AND REPAIRED

The `e42a9b92…` block cited **`.temp/php41/probe_wrap.rs`** — twice, in
`twin_justifications` and `unsafe_justifications` — as the evidence that
`slot_read_unchecked`'s hand-asserted `requires` is the one vstd demands.
⛔ **That is `RECAP_PHP.md` open item 65's defect inside the HASHED block**: a
committed claim resting on a gitignored path, and the probe is exactly the kind
of file `CLAUDE.md` constraint 6 deletes once the gates are green. ⓘ
`.tasks-php/citecheck.py` does not scan per-row `NOTES.md` or `spec.md`, so it
reported `0 unresolved in a LIVE doc` and did not catch this; I found it
reading my own §9 while writing the evidence table.

✅ **Repaired properly rather than annotated away:** the probe is now
**`controls/mu_unwrapped.rs`**, a committed control that verifies at **7
verified / 0 errors** driving the same `MaybeUninit` operations with **no
trusted item at all** — vstd's own `assume_specification` carrying the
obligation — both citations point at it, and `controls/negatives.py --verus`
runs it as must-NOT-fire arm **N2** so it is *executed* on every invocation
rather than merely cited. ⭐ **That makes it a stronger object than the twin it
replaces: a twin re-states a contract, this one derives it** — if the trusted
`requires` ever drifts from what vstd says, one command reports it.

⚠ **Third `contract_sha256`, disclosed:** `e42a9b92247fe2db…` →
`7013be6f7c1cb70da7568716e7eef71908fd109332f64cf76cf769ba063a9d97`. Nothing else in the fence moved, and no measured number moved
(`spec.md` is in the gate digest, not the measurement one).

### 1b. The other loud lines, carried deliberately

* `[idiom-forbidden] idiom.forbidden[2] has NOT ONE backticked spelling` — the
  entry forbids a **structure** (a NULL or emptiness guard inside either C
  consumer's scan loop) and cannot be backticked, because `spelling_matches`
  decides one spelling against **every** rung of a language and all four Rust
  rungs legitimately carry such a guard. The entry says so at length. The shout
  asks for it in `why` too, which costs a `contract_sha256` move and a re-gate
  **for a pointer**, so I carried the shout; `ph45` ships 1 of these and `ph29`
  2. §6.4.
* `provenance` reports the kernel overlap at **9 %** against a 25 % expectation
  for `narrowed` — §6.3 and `NOTES.md` §2.

---

## §2 ⚠ WHERE I DISAGREED WITH THE BRIEF, AND WHAT I DID

`TASK_PHP_041.md` §0 asks for any disagreement between it and
`TASK_PHP_040_REPORT.md` §5. **There is one substantive one and two smaller
ones, and all three are in §5.**

### 2.1 §5.4's blob format cannot be used as written — a FIXED STRIDE is a harness requirement

§5.4 gives `u32 n_decl; u32 n_pool; u32 n_ops; n_pool × {u64 id}; n_ops × {u8
op; u32 a; u32 b}`, which is **variable-length**. The driver loop is pinned
canonical (`nwin = n_blob / stride`, `kernel(buf, k * stride, stride)`), so a
window must be a **fixed stride**. Every field §5.4 names survives; what
changed is how the counts are bounded:

* `n_pool` is capped at `MAXP = 8` and **all eight entries are read on every
  call**, so the pool term is a constant and no rung reads an uninitialised
  pool slot (a second uninitialised read would be a different row);
* `n_ops` is bounded by the window LENGTH — `cap = (len - 76) / 9` — and the
  declared `n_ops_w` is reduced `mod (cap + 1)`, so the header is still read
  from the blob and the `%` is still exercised, but a window can never claim
  more ops than it carries;
* `n_decl` is `n_decl_w mod (MAXD + 1)` with `MAXD = 16`.

⚠ **`MAXD = 16` is a real restriction on the row and I am naming it**: a PHP
class can implement more than 16 interfaces. 16 is what keeps the fixed-size
`idx[]` and `wrote[]` arrays small and what makes the `u32` bitmask the named
candidate for a cheaper witness; nothing about the mechanism depends on the
bound.

### 2.2 §5.3's `QUERY_DEREF` has a redundant disjunct and I dropped it

§5.3 writes `if (ce->interfaces[i] == target || ce->interfaces[i]->id ==
target->id)`. The first disjunct is **redundant** — `p == q` implies
`p->id == q->id` — and its only effect is to skip the dereference on the
matching slot, which is written by construction. I dropped it, and the reason
is §2.3's: it is the one place an **address** could have entered a control-flow
decision every rung has to agree on. Declared in `provenance.divergences` with
that argument. **No behaviour moves on any input.**

### 2.3 §5.5's benign definition needs one more clause, and R3 is why

§5.5 says benign = *"every `FILL` precedes every `QUERY`, and `n_decl` `FILL`s
cover `0..n_decl-1` exactly once"*. **That is not enough to make all six rungs
agree**: R3 is php-5.2.0's append-and-count repair, so its slot order is the
**arrival** order of the fills. The shipped definition adds **in increasing
order**, which is also what real PHP does (the `ZEND_ADD_INTERFACE` opcodes run
in source order and `extended_value` was assigned in that order one pass
earlier). `inputs/gen.py::_check_arms` asserts it and refuses a corpus that
violates it.

---

## §3 ⭐⭐⭐ EVERY §2.5 PREDICTION, BY NAME

⚠ **A refuted prediction is a better result than a confirmed one, and this row
refutes three of four outright, half-refutes the fourth, and turns up a fifth
thing neither prediction anticipated.** Numbers are A1
(`kernel_exclusive_ir / n_iters`, `O3 / isolated`), `small.bin` then
`large.bin`, against R1 = `c-gcc`. `NOTES.md` §8 has the full table and the
mechanism for each.

### 3.1 **R2** — *"PHP 5.2.0's upstream repair reinvented by the type system, and ≈ R1h in cost"* — ⛔ **REFUTED on the cost half, and CORRECTED on the other half**

**Cost: REFUTED.** R2 is **+6.967 % / +25.370 %** over R1 where R1h is
**+0.231 % / −0.720 %** — i.e. R2 is ~6.7 pp dearer than the upstream fix on
`small` and ~26 pp on `large`, not ≈.

**Mechanism, which the prediction's own arithmetic missed.** `Option<u32>` is
**8 bytes** on this platform (a `u32` has no niche), so R2's `None`-fill moves
exactly as many bytes as R1h's `memset` — the prediction was right about that —
but R2 then pays **a discriminant load and a branch on every slot READ**, and
the query loops outnumber the fill by `n_ops : 1` (16 : 1 on `small`, 40 : 1 on
`large`). ⭐ **That ratio is why the gap is four times larger on `large`, which
is what makes the mechanism a measurement rather than a story.**

⭐⭐ **And the OTHER half of the prediction is not so much wrong as too modest,
which is the more interesting correction.** R2 is *not* "php-5.0.5's repair
reinvented": 5.0.5 zeroes the storage and leaves both consumers unguarded.
`Option` reinvents that `memset` **plus the consumer guard upstream never
added**, because `if let Some(p)` is the only expression in safe Rust that
reaches the value at all. ▶ **The type system does not reproduce the historical
fix; it reproduces the fix that would have worked.**

### 3.2 **R3** — *"push-as-you-go, no window at all, the cheapest rung on the row — which would be the headline"* — ⛔ **REFUTED**

R3 is **+24.238 % / +16.666 %** over R4 and **+0.809 % / +14.108 %** over R1.
It is the **cheapest SAFE rung** (5.8 pp under R2 on `small`, 9.0 pp on
`large`) and not the cheapest rung.

**Mechanism.** R3's `Vec<u32>` scan loops **vectorise** — 352 padding-excluded
static instructions, `xmm` present — and R4's do not, because the per-slot
`if wrote[i]` is a data-dependent branch inside the loop (758 static). So R4
executes *more* static code and *fewer* dynamic instructions, and what wins for
R4 is the absent `Option` discriminant and the elided uninit stores, not the
scan.

⚠ At `O0` R3 **is** the cheapest Rust rung (−24.732 % against R4), the
direction the prediction expected — and **no claim rests on an `O0` row**
(`.memory/02-bench-rules.md`). I mention it because it is the only support the
prediction has.

⭐ **The narrower claim that survives is still worth publishing**: the
restructuring that makes R3 safe also deletes the compile-time `idx[]` array
and the `Option` discriminant, and it is the cheapest thing in the row that
needs no `unsafe`.

### 3.3 **R4** — *"LLVM elides the `MaybeUninit::uninit()` fill and R4's inner loop is byte-identical to R1's; if it does not, R4 is DEARER than the C it models"* — ⛔ **BOTH HALVES REFUTED**

Measured against a control that is `unsafe.rs` with `MaybeUninit::uninit()`
replaced by `MaybeUninit::new(0u32)` — a real zero fill, everything else
identical:

| | kernel insns | whole-program `Ir`, `small.bin` |
|---|---:|---:|
| `MaybeUninit::uninit()` (shipped) | 762 | 31 997 125 |
| `MaybeUninit::new(0u32)` | 764 | 32 137 956 |
| difference | **+2** | **+140 831 (+0.440 %) = +5.63 Ir/call** |

* **Not elided entirely.** LLVM elides the **value stores** and keeps the
  **loop**: the uninit version still pays the `Vec` length bookkeeping and
  saves ~5.6 `Ir`/call, about one store per slot at `n_decl = 6`.
* **And R4 is not dearer than the C it models — it is 18.9 % CHEAPER**
  (`small`/`O3`), and 2.2 % cheaper on `large`. R4's inner loop is **not**
  byte-identical to R1's either: 758 against 858 padding-excluded instructions,
  different `md5_fn`.

⭐ **The honest summary is that the fill was never the interesting term on this
row.** The witness (§3.5) is **fifty times larger**.

### 3.4 **R5** — *"needs no hand-rolled ghost state — the obligation is literally `forall|i| … ==> v[i].mem_contents().is_init()`"* — ⚠ **HALF CONFIRMED, HALF REFUTED**

**Confirmed, and exactly as spelled.** `verus.rs` verifies **27 / 0** and
**31 / 0** under `--cfg slb_twin`. The query loops' invariant is

    forall|j| 0 <= j < n_decl ==> (wrote@[j]
        ==> slots@[j].mem_contents().is_init()
            && slots@[j].mem_contents().value() < n_pool)

and its first conjunct **is** `MaybeUninit::assume_init`'s own `requires`
(`~/tools/verus/vstd/std_specs/maybe_uninit.rs`). ⭐ **So `assume_init` costs
NO trusted item** — and the `get_unchecked` on the same line costs one, because
**0 files under `~/tools/verus/vstd/` mention `get_unchecked` at all** against
four that mention `assume_init`. Two unsafe operations, one line, and only one
enlarges the trusted base. ⓘ I re-verified both greps myself rather than
taking `_040`'s word, per `CLAUDE.md`'s standing `std_specs/` warning, and both
hold.

**Refuted, on the value postcondition.** `run_ops` has to say what the kernel
*returns*, and **a spec function cannot construct a `MaybeUninit`** —
`mem_contents` is `uninterp` and there is no spec-mode constructor — so the
spec-level slot array is a `Seq<Option<u32>>` and `abst()` is the abstraction
function from `(slots@, wrote@)` onto it. **One hand-rolled ghost `Seq`, just
not the `Seq<bool>` the prediction ruled out.**

**And the residual risk `_040` §5.6 left open is SETTLED, in the helpful
direction.** *"Whether the `FILL` assignment through `Vec`'s `index_mut`
carries a value-level `ensures`"* — **it does, and the whole of it**:
`std_specs/vec.rs:67-78`'s `vec_index_mut` ensures `*element ==
old(vec)@.index(i)`, `final(vec)@ == old(vec)@.update(i, *final(element))`
**and** `*final(element) == final(vec)@.index(i)`. Confirmed by probe
(`.temp/php41/probe_mu.rs`, 5 verified / 0 errors) **before any rung was
written**. ⚠ The shipped rung does not use it — the C's write is unchecked, so
it goes through `slot_set_unchecked` — but the answer is now recorded so nobody
greps for it a third time.

### 3.5 ⭐⭐⭐ AND THE FIFTH THING, WHICH NO PREDICTION ANTICIPATED: A FAITHFUL R4 CANNOT BE VERIFIED AT ALL

The faithful unsafe port scans `0..num_interfaces` and `assume_init()`s every
slot — `zend_operators.c:1534-1535` with nothing between the loop and the read.
**That program cannot be verified, and not because Verus is weak:**

* `assume_init`'s precondition is `m.mem_contents().is_init()`;
* whether slot `i` was written is a property of the **op stream**, i.e. of
  attacker data;
* the driver loop is pinned canonical and calls `kernel(buf, k * stride,
  stride)` with **no test**, so there is no call site at which coverage could
  be established and no `requires` that could carry it.

▶ **A rung that reproduces the defect cannot be verified and a rung that
verifies does not reproduce it.**

**Measured, not argued.** `controls/negatives.py` mutant **M1** deletes the two
`if wrote[i]` guards from the shipped proof and Verus refuses it at
`vstd/std_specs/maybe_uninit.rs:40:13`, `failed precondition`, 25 verified /
2 errors. The same program as plain Rust is `controls/r4_nowitness.rs`:
**Miri reports it** (`error: Undefined Behavior: constructing invalid value of
type u32: encountered uninitialized memory, but expected an integer`) on an
uncovered blob and is silent on `inputs/small.bin`, while the shipped
`unsafe.rs` is silent on both.

**So the shipped R4/R5 carry a one-byte-per-slot witness the C does not have,
and here is what it costs** (`controls/negatives.py --cost`, `O3`,
`inputs/small.bin`, whole-program `Ir`):

| | whole-program `Ir` | kernel insns |
|---|---:|---:|
| R4 as shipped | 31 997 489 | 760 |
| `r4_nowitness` | 26 275 913 | 260 |
| **the witness** | **+5 721 576 = +21.775 %** | **+500** |

⚠ **Measured corpus only** — the two programs are not equivalent on an
uncovered blob, which is what the witness is for.
**Mechanism:** 260 → 760 static instructions is not one byte per slot. The
witness-free scan loops are branch-free over a `Vec<MaybeUninit<u32>>` and LLVM
vectorises and unrolls them; `if wrote[i]` puts a data-dependent branch inside
the loop and both disappear. ▶ **The cost is lost vectorisation, not the byte.**
ⓘ The named candidate for a cheaper witness is a **`u32` bitmask** (`n_decl ≤
16` fits one word) and it is **not built** — see §6's debt.

⛔ **This is `CLAUDE.md` rule 6's case and I am filing it as a FINDING.** *"The
R5 can't state the obligation"*, *"the program had to change"* and *"Miri
doesn't see it"* are findings, never kills — and here the obligation IS
statable, the program DID have to change, and Miri DOES see it. Nothing about
this refuses the row; it is the row.

---

## §4 ⭐⭐ §2.1's SECOND HALF: R1h's PER-CONSUMER BEHAVIOUR ON THE ADVERSARIAL BLOB (DoD 5)

**Two controls, because the gate structurally cannot carry this.**
`check.py` stage 7h requires R1h clean under ASan+UBSan on **every** input in
`inputs/`, in terms — *"a per-input declaration here would let a pattern
declare its way out of the only thing this stage asks"* — and `d09cdd9f71f3`
adds **no consumer guard**, so **every blob on which R1 dereferences an
unwritten slot is a blob on which R1h dereferences NULL.** ▶ **The row whose
result is that the fix is incomplete cannot ship the input that shows it.**

⭐ **That is `.memory-php/02-ladder.md` F31's standing limitation binding on a
real row for the first time** — F31 was written as a general caveat about
`check_sanitizers_hardened`; `ph03`'s and `ph07`'s R1h do not fault, so it had
never bitten. The resolution F31 itself prescribes (*"that evidence lives in
the row's `controls/`"*) is the one taken, and `inputs/gen.py`'s docstring and
`model.py::sanitizer_expect` both say so where a reader meets them.

### 4.1 `controls/r1h_consumers.py --selftest` → **SELFTEST PASS**

Built with `check.py::_san_build`'s line character for character.

| blob | arm | rung | rc | `u64` | diagnostic |
|---|---|---|---:|---|---|
| `deref` | san | **R1** | 1 | — | `kernel.c:139:30: runtime error: member access within misaligned address 0xbebebebebebebebe for type 'struct ph53_iface'` → `ERROR: UndefinedBehaviorSanitizer: SEGV on unknown address`, **caused by a READ** |
| `deref` | san | **R1h** | 1 | — | `kernel_hardened.c:178:30: runtime error: member access within null pointer of type 'struct ph53_iface'` → `SEGV on unknown address 0x000000000000` |
| `deref` | plain `-O2` | R1 / R1h | −11 / −11 | — | SIGSEGV both |
| `deref-nofill` | san | R1 / R1h | 1 / 1 | — | identical to the two rows above |
| `cmp` | san + plain | R1 / R1h | 0 / 0 | `454892050351138816` **both** | silent both |
| `covered` | san + plain | R1 / R1h | 0 / 0 | `16975370263282301184` **both** | silent both — must-NOT-fire |

Five negatives, all as declared: N1 (R1's fault address is **not** NULL, so the
control is not measuring one program twice), N2 (R1h's **is** NULL), N3 (the
comparing consumer is silent on both arms and both print the same `u64`),
N4 (`covered` is clean on all four arm × kernel cells), N5 (the four blobs are
distinct and each re-decodes to the coverage the docstring claims).

▶ **ONE HUNK, TWO SEVERITIES, and the UBSan text names both:** *misaligned
address `0xbebebebebebebebe`* against *null pointer*. §A4's fidelity anchor is
met — `index.csv` records `crashes_pristine_5_0_0 = True`, `build = asan`,
`wild-pointer-deref`, CWE-824, and the `san` R1 row **is** that.

⚠ **ASan does not see the uninitialised read.** The read is of an in-bounds
slot of a live allocation, which is MSan's class; what ASan reports is the
dereference of the value that came out, and it is deterministic only because
ASan fills fresh allocations with `0xbe`. **Miri is the only detector in this
tree that sees the read itself** (§3.5).

### 4.2 ⭐⭐ `controls/wild_choice.py --selftest --reps 5` → **SELFTEST PASS**, and it says two things §4.1 cannot

§3.5 of the task file asks for a **chosen** wild pointer, not an observed one.
The mechanism is PHP 5.0.0's own size-class cache: `_efree` on a cached class
does not return the block to `malloc`, so a primed payload survives into
`:2571`'s `erealloc`.

```
R1  (erealloc, no memset):
  primed with &pool[3]     cmp_scan=1 (MATCHED UNWRITTEN SLOT)  deref hit=1 id=000c1a5500000004
  primed with &pool[5]     cmp_scan=2 (no match, CORRECT)       deref hit=0 id=0000000000000000
R1h (emalloc + memset):
  primed with &pool[3]     cmp_scan=2 (no match, CORRECT)       deref DIED signal=11
  primed with &pool[5]     cmp_scan=2 (no match, CORRECT)       deref DIED signal=11
```

Byte-identical over five runs, and **the answer moves with the priming** — so
the value really is chosen. Six negatives, all as declared.

**1. The compare-only consumer is not harmless, it is merely non-fatal.** With
the value chosen, `zend_do_inherit_interfaces` reports a duplicate that is not
there (`cmp_scan=1` names an interface the class never implemented). In §4.1 it
answered correctly and *"correct"* could have been luck. ▶ **So
`d09cdd9f71f3` is COMPLETE on this consumer** — NULL can never equal a pool
address — **and useless on the other.**

**2. ⚠⚠ And on the dereferencing consumer the fix does not merely fail to help
— it trades one class of harm for another.** R1 with a plausible wild pointer
returns a **silent wrong answer** (`hit=1`, the chosen id, no crash); R1h
**always dies**. ⓘ I state that as what the four rows show and **not** as a
claim about which is worse or about what upstream intended: the severity
ordering depends on a deployment the row does not have.

---

## §5 WHAT ELSE THE ROW MEASURED

### 5.1 The upstream fix's cost on the benign path — attributable, tiny, and its SIGN DEPENDS ON THE INPUT

`_040` §2.5(2) predicted *"an O(n) `memset` on every benign class declaration —
a real, attributable number"*, against `ph52`'s predicted 0.00 %. **It is
attributable, and it is `+0.231 %` on `small`, `−0.720 %` on `large` and
`+0.364 %` on `small`/`O0`.** ⚠ **Both quoted; neither maxed over input**,
which is `check.py`'s own *DO NOT MAX IT OVER INPUT* rule and the thing F82 was
corrected for.

**Mechanism.** At `O3` both gcc arms have **exactly 858** padding-excluded
kernel instructions with different `md5_fn` (`fa205ef2` vs `d96f5500`): the
`memset` of `8·n_decl ≤ 128` bytes is inlined to `xmm` stores and **replaces**
the `erealloc` cache-lookup path, so the static size does not move and only the
dynamic mix does. On clang the static count moves **+4** (399 → 403). ▶ **So
the 2005 fix is not "an O(n) memset added to the same code" — it is a
malloc-arm swap plus a vectorised fill, and at `n_decl ≤ 16` the fill is one or
two stores.** That is why the number is fractions of a percent and why it can
go either way.

### 5.2 R1 == R1h bit for bit on the measured corpus — a THIRD row

The benign corpus writes every slot before any query, so the published `u64`
carries **no evidence whatever** that the defect exists. That is stage 7h's
requirement being *satisfied*, and it is `ph64`'s and `ph45`'s lesson arriving
on a **third** row. The evidence is in `controls/`.

### 5.3 ⭐ The proved rung is CHEAPER than the unsafe one, at both levels — a THIRD row

A1 `−1.253 %` (`small`/`O3`) and `−0.494 %` (`large`/`O3`); `O0` −16.870 %.
`identity` is pinned **`differ` / `differ`**, measured **before the first gate
run**, and the record agrees on the verdict (`md5_fn`, `md5_fn_norel`,
`md5_raw` all `no`). ⚠⚠ **Not a cost of proof in either direction**: every
`let ghost`, `assert` and `proof {}` erases before codegen and R5's exec code
is R4's; what differs is that rustc sees a larger module and allocates
registers differently (`mov %rdx,%r15` where R4 keeps the value in `%rcx`, from
the first basic block). `NOTES.md` §10 states it and does not attribute it.
⭐ This makes F82's observation **3 of 3 rows on which it has been looked for**,
and by the largest margin of the three.

### 5.4 ⭐ The tally makes both arms of the defect's own branch visible in the checksum, for free

`php_shim_tally()` is `0` when `n_decl == 0` (no allocation at all) and
`1000003 ^ 1000033 ^ (8·n_decl · 1000039)` otherwise. §B1.2 asks for the fold
so that *the defect* lands in the number; on this row it also lands `:2570`'s
branch there. That is a property of this row rather than of the rule, and it is
why `_check_arms` can assert both arms are reached without a second oracle.

### 5.5 §2.3's `u64` — the catalogue's is unusable and the shipped one is address-free

`CATALOGUE.md`'s `▸ benign` line (*"a fold of the interface pointers read"*) is
address-dependent and cannot be used. Every term of the shipped fold is an
index, an id or a count, plus `php_shim_tally()`. ⭐ **And the one place an
address could still have leaked into a decision every rung must agree on is
§5.3's `||` disjunct in the faulting consumer, which is why I dropped it**
(§2.2) rather than only keeping addresses out of the arithmetic.

---

## §6 ⚠ WHAT THE ROW DOES NOT HAVE, AND THE DEBTS IT DECLARES

1. ⚠⚠ **No `controls/spellings.py`. The R3 and R4 endpoints are UNSEARCHED**,
   so every figure in §3 is a `fixed-R4 bound` over an unsearched endpoint and
   must be quoted as one. `ph03`, `ph45` and `ph64` carry the same debt; this
   row makes it **4 of 7**. Declared in `README.md`, `NOTES.md` §8c and here.
   ⭐ **The named candidate for a cheaper R4 is a `u32` bitmask witness** and
   §3.5's +21.8 % is the number it has to beat. ⓘ The row's own `idiom` audit
   reads `14 backticked spellings over 6 rungs → 42 pairs, 18 present,
   0 pin nothing, 6 scoped-absent`, so a `spellings.py` written here would not
   be vacuous the way a clone into `ph29` would have been (open item 51).
2. ⚠ **No `adversarial-deref.bin`, and there cannot be one** — §4.
3. ⚠ **The tier is a judgement, not a measurement.** `provenance.py` reports
   the kernel overlap at **9 %** against a 25 % expectation for `narrowed`, and
   `NOTES.md` §2 gives three reasons and the argument for `modelled` I did not
   take. ⭐ I raised the number from 4 % to 9 % by making the C kernel use
   `ce->` as upstream does (the defect span went 0 % → 50 %); the residual is
   two identifiers the row is obliged to change (`zend_class_entry` →
   `ph53_iface`, `erealloc` → `php_shim_erealloc`) and five context spans that
   are deliberately narrowed, one of which (`zend.h`'s 41-line struct) scores
   0/32 by design. **This is the call on the row I am least sure of** (§8).
4. ⚠ **`idiom.forbidden[2]` has no backticked spelling and the gate shouts
   about it on every run** (`forbidden_unaudited_entries: 1`; the final audit
   reads `spellings 15, rungs 6, pairs 46, present 20, forbidden_spellings 6,
   forbidden_hits 0, required_pins_nothing 0, required_absent 8`).** The entry forbids a *structure* — a NULL or
   emptiness guard inside either C consumer's scan loop — and it cannot be
   backticked, because `spelling_matches` decides one spelling against **every**
   rung of a language and all four Rust rungs legitimately carry such a guard.
   The entry says so at length; the shout asks for it in `why` as well, which
   would cost a `contract_sha256` move and a re-gate **for a pointer**, so I
   carried the shout instead. `ph45` ships 1 and `ph29` 2 of these. ⓘ If a
   reviewer wants it in `why`, it is one sentence and one re-gate.
5. ⚠ **No `O0` claim.** `O0` rows are in the published table and §3.2/§3.3 name
   the two places where `O0` is the only support a prediction has.

---

## §7 ⭐ §2.6's OPTIONAL PROBE — REACHED, AND THE ANSWER IS **NO**

§2.6 offered F93's question as adjacent and optional: *does `ph53`'s
`[100, 200]` span sit on a start-of-run transient?* **It was reached, and this
is a third data point on open item 69.** Method: the marginal slope
`(Ir(b) − Ir(a)) / (b − a)` at six spans of equal width over the existing
`O3/isolated` binaries, `small.bin`, whole-program `Ir` under callgrind
(deterministic, so it ran beside the gate):

| cell | 100→200 | 200→300 | 1000→1100 | 5000→5100 | 10000→10100 | 20000→20100 | `[100,200]` vs mean(far four) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `c-gcc` | 1510.090 | 1523.540 | 1501.650 | 1531.840 | 1501.110 | 1529.580 | **−0.393 %** |
| `c-gcc-h` | 1512.890 | 1527.140 | 1504.330 | 1535.590 | 1503.760 | 1533.370 | **−0.419 %** |
| `safe_naive` | 1739.890 | 1767.640 | 1727.140 | 1779.490 | 1728.310 | 1776.590 | **−0.741 %** |
| `safe_tuned` | 1527.200 | 1545.660 | 1517.100 | 1554.800 | 1518.240 | 1552.120 | **−0.545 %** |
| `unsafe` | 1253.450 | 1277.520 | 1242.990 | 1288.000 | 1243.440 | 1285.660 | **−0.915 %** |
| `verus` | 1239.450 | 1263.520 | 1228.990 | 1274.000 | 1229.440 | 1271.660 | **−0.925 %** |

▶ **`ph53`'s `[100, 200]` does NOT sit on a transient.** It is within
**0.39–0.93 %** of the mean of the four far spans on all six cells — and the
far spans differ from *each other* by about as much (`c-gcc` reads 1501.11 at
10000→10100 and 1529.58 at 20000→20100). ⭐ **So what this row has is not a
start-of-run effect but a ±1 % WINDOW-SELECTION oscillation that is the same at
`[100, 200]` as anywhere else**, and it alternates with the span's parity in a
way that is visible in the table: the odd-numbered spans are all ~1.8 %
above the even ones, which is the pseudo-random window index cycling.

⚠ **This does not close item 69 and I am not claiming it does.** It says that
`ph29`'s 32 % draw instability (F93) is **not** a property of the harness's
`[100, 200]` choice as such, and it is consistent with F88's own control —
*"`ph03` reads 0.03 % because its per-window work is uniform"*. ▶ **The three
points now read: uniform work 0.03 % (`ph03`), nearly uniform ~1 % (`ph53`,
one window in sixteen differing), heterogeneous 32 % (`ph29`)** — i.e. the
draw's instability tracks per-window work heterogeneity, which is a
*hypothesis* with three supporting points and not a measurement of a mechanism.
⚠ `ph53`'s heterogeneity is *forced*: both arms of `:2570` must be in the
measured corpus and they cannot cost the same.

---

## §7a ⭐ CANDIDATE FINDINGS, FOR THE MANAGER TO LAND OR REFUSE

⚠ **These are the engineer's claims and none has been reviewed** — `PROTOCOL.md`
rule 9. Ordered by what I think they are worth, with what each rests on.

| | claim | rests on |
|---|---|---|
| **A** | ⭐⭐⭐ **A row whose upstream fix does not remove the fault cannot ship the input that shows it**, because stage 7h requires R1h clean on every input in `inputs/` and says so in terms. `.memory-php/02-ladder.md` **F31** binding on a real row for the first time; the resolution F31 prescribes (`controls/`) is the one taken | §4, `controls/r1h_consumers.py`, the gate's own `sanitizer_hardened.fired = False ×7` |
| **B** | ⭐⭐⭐ **A rung that reproduces this defect cannot be verified and a rung that verifies does not reproduce it** — coverage is a property of attacker data and the pinned driver loop offers no call site at which to establish it. So the shipped R4/R5 carry a witness the C does not, and it costs **+21.8 %** | §3.5, M1's refusal, the four Miri arms, `controls/negatives.py --cost` |
| **C** | ⭐⭐⭐ **Two sound gate rules are jointly unsatisfiable for a `MaybeUninit` read**: every `unsafe` token must sit in an `external_body` body, and every trusted item needs a verified twin — and there is no safe exec route from `MaybeUninit<T>` to `T`. Found by the gate, on the first run | §1a, `.temp/php41/14-gate1.log`, `controls/mu_unwrapped.rs` |
| **D** | ⭐⭐ **THREE of `_040` §5.6's FOUR predictions are refuted and the fourth is half refuted**, each with a mechanism read off the disassembly | §3 |
| **E** | ⭐⭐ **The comparing consumer is not harmless, it is merely non-fatal** — with the wild value CHOSEN it reports an interface the class never implemented, and `d09cdd9f71f3` really does remove that. So the fix is **complete on one consumer and useless on the other** | §4.2, `controls/wild_choice.py`, 6 negatives |
| **F** | ⭐ **The proved rung is cheaper than the unsafe one** — F82's observation on a **third** row and by the largest margin of the three (A1 −1.253 %) | §5.3, the record's `identity` rows |
| **G** | ⭐ **`[100, 200]` does NOT sit on a transient on this row** (0.39–0.93 %), a third data point on open item 69, and the three points track per-window work heterogeneity | §7 |
| **H** | ⭐ **A and B agree in sign and closely in magnitude on every cross-language cell of this row**, which is the opposite of F85's regime — and the reason is §B1a's precondition holding, so there is no allocator term for B to include and A to miss. ⚠ Evidence about this row, not about A | `NOTES.md` §8h |
| **I** | **The catalogue's `ph53` tier and `u64` were both wrong**, as §2.2/§2.3 said. ⓘ Open item **75** asks whether the tiers are *systematically* optimistic; **I did not survey** and §6.3 says what I saw on this one row | `NOTES.md` §2 |
| **J** | ⚠ **Neither `verus_checked` nor `problems` is a field this harness writes into a GATE record.** The task file's definition of done asks for both quoted; both are absent from `ph53`'s, `ph45`'s and `ph64`'s. `problems` **is** a preflight field and it is `[]`; what stands in for `verus_checked` is `verus["verus.rs"] = {verified 27, errors 0, pinned 27}` | §1 |
| **K** | ⚠ **`citecheck.py` does not scan per-row `spec.md` or `NOTES.md`**, so it reported `0 unresolved` while my hashed block cited a gitignored path. Open item 65's own checker has a blind spot exactly where the hashed layer is | §1a2 |

---

## §8 WHAT I AM UNSURE OF (`PROTOCOL.md` DoD 5)

⭐ `UNTESTED` and *I could not tell* are the intended answers here.

1. ⚠⚠ **THE TIER. This is the call I am least sure of.** `narrowed` is what
   §2.2 directed and what `_040` §5.1 assessed, and the overlap heuristic
   reports 9 % against 25 %. My three reasons are in `NOTES.md` §2, and the
   counter-argument I did not take is real: §A2 says a divergence that CHANGES
   BEHAVIOUR is a `modelled` tier, and the faulting consumer's narrowing **does**
   change the answer (no transitive interface implementation). What it does not
   change is the number of slot dereferences, which is what the row measures.
   **I could not settle it and a reviewer may prefer `modelled`.** Nothing in
   the row turns on it (a tier is a cost, never a filter), but it is inside the
   hashed block, so changing it costs a `contract_sha256` move.
2. ⚠ **`MAXD = 16` is a real restriction and I do not know whether it matters.**
   A PHP class can implement more than 16 interfaces. 16 keeps `idx[]` and
   `wrote[]` small and makes a `u32` bitmask the obvious cheaper witness.
   **UNTESTED:** whether the ladder's ordering survives at, say,
   `MAXD = 64` — where R2's `Option` fill grows linearly and R4's witness stays
   one byte per slot, so I would *expect* the R2–R4 gap to widen, but I did not
   measure it.
3. ⚠ **§3.5's +21.8 % is a cost comparison and NOT a rung comparison**, because
   `r4_nowitness` answers differently on an uncovered blob. I believe it is the
   right number to publish for *what the witness costs*, but it is not a
   `fixed-R4 bound` and must not be read as one.
4. ⚠ **The `wrote[]` witness is indexed SAFELY** and I did not measure the
   unchecked spelling. The argument for safe indexing is that reaching a rung's
   own safety witness with `get_unchecked` would make the witness rest on the
   thing it exists to establish — but LLVM very likely elides the check anyway
   (`i < n_decl ≤ 16`, a fixed-size array), so the choice is probably free and
   **I did not verify that**.
5. ⚠ **I did not build `controls/spellings.py`** (§6.1), so no endpoint on this
   row is searched and the `fixed-R4 bound` figures are over unsearched
   endpoints in both directions.
6. ⚠ **R3's `Vec::with_capacity(n_decl)` is not php-5.2.0's allocation
   schedule.** 5.2.0 `erealloc`s per interface, i.e. O(n) allocations; R3
   reserves once. I chose the one allocation so §B1a's precondition holds of
   the whole row, declared it in the ledger, and **did not measure what the
   5.2.0 schedule would cost** — which would be the honest way to price
   *upstream's* restructuring rather than a Rust-idiomatic version of it.
7. ⚠ **The `instanceof_function` narrowing's reachable-domain argument is an
   argument, not a differential.** §A1 asks for substitutions to be
   *demonstrated* behaviour-preserving; this one is declared `narrowed` rather
   than `substitution` precisely because it is not behaviour-preserving, so no
   differential is owed — but a reviewer who thinks the tier should be
   `modelled` is really disagreeing with that classification and item 1 is
   where that lands.
8. ⚠ **§4.2's "an integrity bug becomes a guaranteed availability bug"** is my
   reading of four measured rows and **not** a claim about severity ordering or
   about upstream's intent. I could not tell which is worse and the row has no
   deployment to decide it.
9. ⚠ **§7's three-point trend is a hypothesis.** Three rows, one of them mine,
   and the "per-window work heterogeneity" variable is not something I
   manipulated — I observed it. It is not a measurement of a mechanism.
10. ⚠ **`model.py` cannot express the defect**, by construction (there is no
    Python spelling of *read a slot nobody wrote*), so its unwritten slot is
    `None` and is skipped. That makes it a genuinely independent second opinion
    **and** means it cannot check the C's behaviour on a blob where the defect
    is reached. Stage 4 records those rows instead. I think this is the right
    trade and it is stated in `model.py`'s docstring and in `spec.md`'s `note`,
    but it is a real limitation of the oracle.
11. ⚠ **I did not identify the php-5.2.0 restructuring's commit** — `_040` §6.3
    left the same gap. R3 implements its *shape*, cited to the code at the tag
    rather than to a commit. It is not R1h and the row does not need it.
12. ⚠⚠ **I DID NOT SHIP THE `MaybeUninit<&Iface>` REPRESENTATION, AND IT
    VERIFIES — this is the design alternative I am least comfortable having
    rejected.** `.temp/php41/probe_mu_ref.rs` puts a genuine `&Iface`
    REFERENCE in the slot (`Vec<MaybeUninit<&'a Iface>>`, filled with
    `MaybeUninit::new(&pool[j])`, read with `unsafe { m.assume_init() }.id`)
    and verifies at **5 verified / 0 errors with ZERO `external_body` items**.
    On that representation the Rust rung's slot holds a POINTER exactly as the
    C's does, the uninitialised read is a genuine wild-pointer dereference, and
    §11.5's fourth obligation (`p < MAXP`, the price of the index
    representation) **disappears**.
    ▶ **I rejected it for one reason and I believe the reason is right**: the
    COMPARE-ONLY consumer must read the slot and NOT dereference it — that
    asymmetry is the row's headline — and in Rust `a == b` on two `&Iface`
    delegates to `Iface: PartialEq`, i.e. it **reads the pointee**. Comparing
    without dereferencing needs `core::ptr::eq`, which is address-dependent
    (§2.3 forbids that reaching the checksum) and which the pinned vstd does
    not specify. So the reference representation can express the faulting
    consumer and **not** the comparing one, and a row with one consumer cannot
    show that one hunk lands at two severities.
    ⚠ **What I did not do is measure it.** I did not build a two-consumer
    reference variant to see whether `ptr::eq` could be made to work, and I did
    not price the representation. **UNTESTED**, and it is the first thing I
    would look at if a reviewer disagreed with the index choice.
13. ⓘ **One `required` spelling arrived by ACCIDENT and I am keeping it, and
    saying so.** `required[2]`'s Rust key contains the word `unsafe` in
    backticks — I wrote it as prose while retargeting the citation in §1a2 — so
    the audit now pins `unsafe` as a spelling (15 rather than 14, and two more
    `required_absent` pairs). It is harmless and in fact true: `unsafe` is
    present in `unsafe.rs` and `verus.rs` and absent from the two safe rungs,
    which is what the entry is about. **But it was not deliberate**, and the
    reason to name it is that it is the same mechanism that WOULD have failed
    the gate in a `forbidden` entry — six such incidental spellings would have,
    before the first gate run, which is why `forbidden[0]`'s own text now warns
    about it.
14. ⚠ **`.temp/php41/` is gitignored**, so every number this report rests on is
    **in this report and in `NOTES.md`**, not behind a `.temp/` path (open item
    65). The paths are for re-derivation only; §9 lists them with what each
    proves and which are regenerable by a committed script.

---

## §9 EVIDENCE

⚠ **`.temp/php41/` is gitignored**, so every number this report rests on is in
this report and in `patterns-php/ph53-iface-tail-uninit/NOTES.md`; the paths
below are for re-derivation, not for citation (open item 65). **Keep the
generator, delete the artefact** (`CLAUDE.md` constraint 6): the `.bin` blobs,
binaries, `.o` and `__pycache__` under `.temp/php41/` were deleted once the
gates were green, and everything left is a generator, a source or a log.

| path | what it is, and what rebuilds it |
|---|---|
| `00-EXPECTATIONS.md` | my predictions, written **before any rung was compiled** — including the named bias *"I want prediction 5 (R5 refuted) to be true"* and the guard I set against it |
| `01-pre-build-state.log` | `git status` and `ls patterns-php/` at that moment: the row did not exist |
| `probe_mu.rs`, `probe_mu_ref.rs`, `probe_wrap.rs` | the three Verus probes run **before any rung was written**: the `MaybeUninit`+`Vec` shape (5/0), the `MaybeUninit<&Iface>` alternative (5/0 — see §8.13), and the four trusted accessors with their twins and the witness invariant (6/0). ⭐ `probe_wrap.rs` is what keeps §11.5's asserted contract checkable against vstd's |
| `10-build.log`, `11-measure.log`, `20-chain.log` | the six-command chain, both times |
| `12-negatives.log`, `21-negatives-verus.log`, `22-negatives-miri.log`, `24-cost.log` | `controls/negatives.py`'s four arms. ⚠ `12-` is the FIRST run and it records the one genuine self-catch: M1's needle stopped applying after §11.5's fold and the mutant **refused to run** rather than silently passing |
| `23-r1h.log` | `controls/r1h_consumers.py --selftest`, `SELFTEST PASS` — §4.1's table |
| `14-gate1.log` | ⭐ **the gate run that found §1a's collision.** Two `tcb-unsafe` blockers, quoted there |
| `25-chain2.log`, `30-final.log` | the two remaining `gate → report → gate` chains. `30-final.log` ends `check.py: PASS-WITH-BLOCKED-ROWS` |
| `26-regen.log` | `inputs/gen.py` re-run at the end; the seven blobs come out byte-identical to the record's `input_sha256` |
| `31-negatives-final.log`, `32-r1h-final.log`, `33-wild-final.log` | **the whole control suite re-run against the shipped tree**: 4 must-fire Verus mutants + 2 must-NOT-fire + 3 fingerprint negatives, 4 Miri arms, the cost arm, 5 `r1h_consumers` negatives, 6 `wild_choice` negatives. **All three `SELFTEST PASS`** |
| `15-transient.log`, `transient.py` | §7's probe. **Generator kept, blobs deleted** |
| `16-marginal-large.log` | §8h's family-B figures on both inputs |
| `elide/r4_realfill.rs` | §3.3's control — `unsafe.rs` with `MaybeUninit::uninit()` replaced by `MaybeUninit::new(0u32)`, produced by one `sed` recorded in the log |
| `negatives/verus-M{1,2,3,4}.rs` | the four Verus mutants as emitted. Re-derivable with `controls/negatives.py --emit M1`; kept because each one *is* the statement of what it deletes |
| `gen_spec.py` | the generator that wrote `spec.md`, so the JSON and the 11 003-byte shared `why` tail are exact rather than hand-assembled. ⚠ **`.memory/05-layout.md`'s artefact-vs-generator rule**: `spec.md` is generated, so a later edit must go through this file and re-run it, or it will be silently reverted. It is under `.temp/`, which is the weaker half of that rule and is named here rather than left to be discovered |
| `named_spelling_tail.txt`, `verus_items.json` | the shared `why` tail lifted from `ph16` (11 003 B, sha256 `59748cce2db5…`, byte-identical to `ph45`'s) and `vparse`'s item dump that `gen_spec.py` embeds |
| (deleted) | every `.bin`, binary, `.o`, `__pycache__` and callgrind output — `CLAUDE.md` constraint 6. `.temp/php41/` is **492 KB** and every file left is a generator, a source or a log. Both `controls/*.py` regenerate their own blobs and binaries |

**Committed, and this is where a reader should go:**

| path | |
|---|---|
| `patterns-php/ph53-iface-tail-uninit/NOTES.md` | every number, with its mechanism, and the four trusted-item arguments |
| `patterns-php/ph53-iface-tail-uninit/README.md` | the reader's entry point and the row's declared debts |
| `patterns-php/ph53-iface-tail-uninit/controls/` | `r1h_consumers.py`, `wild_choice.{c,py}`, `negatives.py`, `r4_nowitness.rs`, and **both** fix patches |
| `results-php/gate/ph53-iface-tail-uninit.json` | the verdict |
| `results-php/ph53-iface-tail-uninit.json` | the measurement record |
| `results-php/tables/ph53-iface-tail-uninit.md` | the published table |
| `results-php/preflight/ph53-iface-tail-uninit.preflight.json` | the php-specific certification |

---

## §10 BRACKET AND SCOPE

```
FIRST   python3 harness/measure.py --check-stale                -> 66 record(s) examined, 0 STALE
        python3 harness-php/gate.py --tool measure --check-stale -> 14 record(s) examined, 0 STALE
LAST    python3 harness/measure.py --check-stale                -> 66 record(s) examined, 0 STALE
        python3 harness-php/gate.py --tool measure --check-stale -> 16 record(s) examined, 0 STALE   <- +2, exactly as §0 predicted
```

`git status --porcelain`:

```
 M results-php/preflight/_norow.preflight.json
?? .tasks-php/TASK_PHP_041_REPORT.md
?? patterns-php/ph53-iface-tail-uninit/
?? results-php/gate/ph53-iface-tail-uninit.json
?? results-php/ph53-iface-tail-uninit.json
?? results-php/preflight/ph53-iface-tail-uninit.preflight.json
?? results-php/tables/ph53-iface-tail-uninit.md
```

⚠ **The one MODIFIED tracked file is `results-php/preflight/_norow.preflight.json`,
+101 lines, and it is `PROTOCOL_PHP.md` §E's documented second-order effect**:
the preflight *"is not read-only — a run grows a COMMITTED file"*, and every
`gate.py --tool measure --check-stale` and `gate.py --audit` appends a
row-less entry to it. §E names this exactly (`TASK_PHP_009` m5, *"one failed
`gate.py --tool measure --check-stale` added 52 lines"*) and asks an agent to
print `git status` rather than only the sha256 of what it meant to touch. **I
did not edit that file**; the bracket commands did. `harness-php/gate.py
--audit` reports `preflight coverage: complete`.

`harness-php/gate.py --audit` → **`preflight coverage: complete`**.

**Nothing else was touched.** Nothing under `harness/`, `common/`,
`common-php/`, `patterns/`, `results/`, `pilot/`, `.web/`, `RECAP_PHP.md`,
`.memory-php/`, `patterns-php/CATALOGUE.md`, `patterns-php/MANIFEST.sha256`,
`patterns-php/php-5.0.0.manifest` or any **existing** `patterns-php/` row.
No `git add`, no `git commit`, no history-mutating git command. No `/tmp` file
— all scratch is under `.temp/php41/`. Every corpus and tarball `grep` used
`-a`. `inputs/gen.py` re-run at the end produces the seven blobs
**byte-identically** (their sha256s match `results-php/ph53-iface-tail-uninit.json`'s
`input_sha256`), so the gitignored artefacts are regenerable from the committed
generator.
