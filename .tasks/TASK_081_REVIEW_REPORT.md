# TASK_081 — REVIEW REPORT

**Role:** research reviewer. Targets: TASK_080 item 6 (`is not supported` escapable
at +1 trusted item, `.memory/04-verus.md` final section), the **p45 refusal**, and
the **LADDER TEST** (`.memory/06-catalogue.md:954`, one commit old, unreviewed).
Two of the three are the manager's own designs; PROTOCOL rule 3 was flagged
against both.

All probes, logs and generators: **`.temp/r81/`** (`ls .temp/r81` was absent before
this task). Nothing under `patterns/`, `harness/`, `common/`, `pilot/`, `.memory/`
or `results/` was written. No git history was mutated.

---

## VERDICT IN THREE LINES

1. **The escape is real and reaches every one of finding 14's items that is
   reachable at all** — but the shape TASK_080 measured (`+1 trusted item, and
   Verus prints the fix`) is **vacuous for the memory operations**, and the honest
   price for p05/p16's header read is **6 author-written axioms**, one of which is
   an unchecked cross-type representation axiom.
2. **The gate counts NONE of it.** `assume_specification`, `broadcast axiom fn`
   and `uninterp spec fn` are all invisible to `harness/vparse.py`, so the
   **published TCB column, the pinned obligation count, the `identity` pin, the
   Miri policy and stages 5c / 5c-req / 5c-twin are all blind.** Demonstrated on
   p01's real `verus.rs` with two deliberately false axioms.
3. **The LADDER TEST's first half is wrong in both directions and contradicts the
   p48 row inside its own block.** It is satisfied by **p08** (which the block
   treats as the failure mode) and violated by **p47** (which shipped). The
   manager's own worry was right about the conclusion and wrong about which half.

---

## Findings, ranked

### BLOCKER 1 — `harness/vparse.py:429`, `harness/vparse.py:465`, `harness/check.py:3215`, `harness/check.py:6198`
**The gate cannot see an `assume_specification` at all, so TCB — a published
column — is silently gameable by exactly the mechanism TASK_080 just found.**

`vparse.parse` recognises items with `re.finditer(r"\bfn\s+(IDENT)")`
(`vparse.py:429`) and then **drops every body-less item**:

```python
        if body_open is None:
            continue                      # harness/vparse.py:465
```

`assume_specification`, `broadcast axiom fn` and `uninterp spec fn` are all
body-less. `check.py::_is_trusted` (`:3215`) additionally requires
`item.external == "verifier::external_body"`, and `_trusted_items` (`:6198`) sums
over `_is_trusted`.

**Demonstrated on a real pattern.** `.temp/r81/p01_axiom.rs` is
`patterns/p01-array-sum/verus.rs` plus **two deliberately FALSE axioms on SAFE std
functions** (`u32::rotate_left` given *rotate-right* semantics;
`<[T]>::starts_with` given `b == (p.len() <= s.len())`):

```
patterns/p01-array-sum/verus.rs
   n_items 7 tcb [('get_unchecked','verifier::external_body'), ('load_input',...), ('emit',...)] _is_trusted ['get_unchecked']
.temp/r81/p01_axiom.rs
   n_items 7 tcb [('get_unchecked','verifier::external_body'), ('load_input',...), ('emit',...)] _is_trusted ['get_unchecked']
```

```
$ ./verus_run.py .temp/r81/p01_axiom.rs
verification results:: 7 verified, 0 errors        # the pinned count, unmoved
```

and the emitted code is byte-identical, so the `identity` pin does not see it
either:

```
.temp/r81/p01_base    _RNvCscsbQa3ackwl_8p01_base6kernel    size= 141 md5=e3e4441313c93057730ab568fb000846
.temp/r81/p01_axiom   _RNvCs71Uhsiywr8A_9p01_axiom6kernel   size= 141 md5=e3e4441313c93057730ab568fb000846
```
(both `verus_run.py --compile … -C codegen-units=1 -C opt-level=3 -C debug-assertions=off --cfg slb_isolated`, both `7 verified, 0 errors`.)

**Everything that is blind, and why each one misses:**

| mechanism | why it misses |
|---|---|
| `results/synthesis.md:396` **TCB items** column | built from `tcb_items`, which is `[i for i in item_list if i.external]` (`check.py:3653`) — a vparse item list |
| pinned obligation count (`check.py:3688`) | an `assume_specification` adds **0** verified functions; measured on every probe in `.temp/r81/` |
| `identity` pin R4 ≡ R5 | ghost-only declaration, **0 instructions** — the md5s above |
| `check_miri` (`check.py:6317-6345`) | `n_trusted == 0` ⇒ *"this pattern has NO trusted item … Miri not required"* |
| 5c / 5c-req / 5c-twin | all iterate trusted items; the axiom gets **no conjunct deletion, no requires-strength probe, no verified twin** |
| `_scan_unsafe_sites` (`check.py:3295`) | fires only on an `unsafe` **token**. An axiom on a **safe** std fn has none |
| `spec.md` item-set pin | the item set is vparse-derived |

The only trace is `check.py:3663`:

```python
        for kw in ("assume(", "assume_specification", "admit("):
            n = len(re.findall(re.escape(kw), vparse.blank_noncode(txt)))
            if n:
                rep.note(f"{src}: {kw} appears {n}x -- must be justified in NOTES.md")
```

`rep.note` is informational (`check.py:468`) and does not fail the gate.

**Concrete failure scenario.** p11 ships `r4_cstr` under the escape. Its four
axioms (see R2 below — all on **safe** functions, **no `unsafe` token anywhere**)
verify `2 verified, 0 errors`. `results/synthesis.md` still reads
`p11-nul-scan | 12 | 0 | 3 | 6 | exact | PASS` — obligations 12, **TCB items 3** —
while the proof now rests on **seven** trusted items, four of them hand-written
and never checked by anything. RECAP's settled answers already say the column is
*"prospectively gameable"*; this is the mechanism, and it arrives at the moment
someone has a reason to want it.

⚠ **Scope, stated honestly, because it changes the priority.** The hole is
specific to axioms on **safe** functions. For an **unsafe** std function
(`unchecked_add`, `read_unaligned`) the call site is still an `unsafe` token
sitting outside every trusted body, and `_scan_unsafe_sites` hard-fails it — so
the author is pushed back to an `external_body` wrapper, which **is** counted.
(Read from `check.py:3295-3348`; **not run against a live pattern** — see
*Unsure*.) The uncounted set is exactly finding 14's *safe* items:
p16's `chunks_exact` / `ChunksExact` / `by_ref` / `TryFromSliceError`, p11's four
`CStr` items, and `from_le_bytes`.

**I do not fix. Rule 5's default applies** — a `check.py` change owes the *"could
this happen by accident?"* test first. My reading: **yes, easily.** Verus prints
the declaration in its own help text and invites you to paste it, and nothing in
`spec.md`, `NOTES.md` or the verdict currently asks for it to be tallied. The
cheapest honest repair is a `NOTES.md`/`spec.md` **declared** count plus turning
`check.py:3663`'s `rep.note` into a `rep.shout` (it survives to the verdict), not
a new parser.

---

### BLOCKER 2 — `.memory/06-catalogue.md:961-963`
**The LADDER TEST's first half is wrong in both directions, and it contradicts
the `p48` row four lines below it.** It is currently in RECAP's START HERE box as
guidance for the next agent.

The rule:

> **A PATTERN NEEDS A BUG THAT R4 CAN REINTRODUCE AND R3 CANNOT, AND A COST THAT
> DIFFERS BETWEEN THEM.**

**(a) It contradicts its own table.** `:970` records p48's failure as
*"**R3 cannot express it** → so R4-vs-R3 is p08's 'compile-time, nothing to
measure'"*. The rule **requires** R3 to be unable to reintroduce the bug; the
table cites exactly that as the failure. The two readings differ in what *"it"*
is — the **bug** (which the rule means) versus the **kernel** (which p48's real
problem was: *"safe Rust needs `set_len`, i.e. `unsafe`, to reach the residue at
all"*). The rule states the first and the table diagnoses the second.

**(b) p08 satisfies the rule and the block treats p08's shape as the failure
mode.** p08's bug is an overlapping `memcpy`; R4 reintroduces it via
`copy_nonoverlapping`, and **safe Rust cannot express it — the borrow checker
rejects it at compile time** (`.memory/01-ladder.md:1302-1306`). That is the
rule's first half, met exactly. p08 shipped and is finding 7.

**(c) p47 violates the rule and shipped.** The manager's stated worry was that
p47 would fail the *cost* half. **It does not** — measured from
`results/gate/p47-ct-compare.json`, `O3/isolated`:

```
safe_tuned/O3/isolated/small.bin 524.0     unsafe/O3/isolated/small.bin 434.0
safe_tuned/O3/isolated/large.bin 747.7     unsafe/O3/isolated/large.bin 605.7
```

R3 − R4 = **+90.0 / +142.0 Ir per call**. p47 passes the second half comfortably.
It fails the **first**: the timing leak is reintroducible in **safe Rust** —
`safe_naive` *is* one of the leaking rungs (`.memory/01-ladder.md:2270`,
`spread 184.000 in k  LEAKS`). So "R3 cannot" is false for p47.

**So the rule as written misclassifies both of the project's own reference
cases, in opposite directions.**

**(d) The second half never says which of the two `Ir` conventions it means**, and
`.memory/03-measurement.md` defines both. On p08:

```
safe_tuned/O3/isolated 7334.16 / 29079.56   d_ir_d_work 6.055527708
unsafe/O3/isolated     7308.14 / 29053.56   d_ir_d_work 6.055533278
```

level difference **+26.02 / +26.00** (differs); slope difference **5.6e-6**
(does not). The rule gives opposite verdicts on p08 depending on an unstated
choice.

**(e) The block's own exemplar does not meet its own trigger.** `:1002` says
*"Run them on any pattern that reports a rung difference of 0.00"* and then cites
p16 as *"the shipped instance of a genuine zero"*. p16's rung difference is
**+27.0 / +77.0** at level (`3051.3` vs `3024.3`; `23889.3` vs `23812.3`); only
the per-**byte** rate is 0. Same unstated-convention defect.

**(f) The `readelf` half cannot fire on a shipped pattern.** `:998` prescribes
*"two rung symbols on ONE section index?"*. In this project **every rung is its
own binary** (`.temp/build/<pNN>/<cell>-<opt>-<mode>`, `build.py:33`), so no
binary ever contains two rungs' kernels. p45's `k_plain`/`k_wrapping` were two
kernels in **one probe object file**. Only the `md5sum` half transfers across
binaries, and as written (`md5sum <each rung's extracted kernel bytes>`) it is
not a runnable command — it needs the extraction procedure (symbol size from
`readelf -sW`, section file offset from `readelf -SW`).

**(g) `:1006`'s *"the bodies are mnemonic-identical"* is not true of p16's shipped
kernels.** Measured (below): 410 bytes vs 324 bytes, different md5. p16's
mnemonic-identity claim is about the **chunk-loop body at matched fold
spellings** in `controls/foldcmp.py`, and p16's own `NOTES.md:1797-1800` says the
shipped pair is *"23 instructions on each side, the same multiset, a different
order"* — i.e. explicitly **not** identical.

#### R5 verdict and restatement

**The first half must be retracted. The second half must be re-scoped. The
`md5sum` half is the good part and should be kept and made runnable.**

Proposed restatement — three probes, all cheap, all run **before the row is
written**:

> **1. A rung boundary must exist somewhere, and the row must name it.** Not
> necessarily R3-vs-R4: p08's runs at compile time (R2/R3 *cannot express the
> bug*, R4 can), p47's runs *inside* the safe class (idiom vs idiom), p16's is a
> slope. What is fatal is **no boundary anywhere** — p31's arena carve is correct
> C, so no rung differs.
>
> **2. The rungs must differ as machine code, and this is checked, not argued.**
> For each rung's binary take the kernel symbol's `Ndx`/`Size` from
> `readelf -sW`, the section's file offset from `readelf -SW`, and `md5sum` the
> extracted bytes. **If two rungs collide, the pattern is one rung** — that is
> what would have caught p45 (`.text.k_plain` and `.text.k_unchecked`, 155 bytes
> each, both `85bd268b3def0d5e386f1498706a6b2b`; re-derived below). The
> "two symbols on one section index" form applies to a **probe object file**, not
> to this project's per-rung binaries.
>
> **3. Any published 0.00 must name its axis and its convention IN ADVANCE.**
> Which axis carries the finding when the cost gap is zero (behaviour matrix,
> TCB, compile-time expressiveness, or a slope rather than a level), and which
> `Ir` convention the zero is stated in. p47 *"knew that going in"*; p45 did not,
> and could have shipped `R3 − R4 = 0.00` as *"safety is free"*.

The manager's own draft — *"either the ladder separates the rungs or the pattern
states in advance which single axis carries it"* — is the right shape and holds
on all six rows I checked (p05, p08, p16, p31, p45, p47, p48). Probes 2 and 3
are what make *"states in advance"* checkable rather than a promise.

---

### MAJOR 3 — `.memory/04-verus.md` (final section) — the escape as recorded is VACUOUS for the memory items
The section's usable summary is *"`is not supported` is a TCB price for simple
arithmetic intrinsics"* plus *"Verus itself prints the fix"*. Both halves fail on
the memory operations.

**(a) The printed fix does not parse for the pointer methods.**
`.temp/r81/c_ru_verbatim.rs` is the help line pasted verbatim:

```
error: expected identifier
 --> .temp/r81/c_ru_verbatim.rs:8:57
  |
8 | pub assume_specification<T> [std::ptr::const_ptr::<impl *const T>::read_unaligned] (_0: *const T) -> T;
  |                                                         ^
```

`<*const T>::read_unaligned` does parse (`1 verified, 0 errors`,
`.temp/r81/c_ru_alt.log`), but you have to know that.

**(b) The declaration shaped like the printed one is VACUOUS.**
`.temp/r81/d_mem_escape.rs` declares `as_ptr`, `add` and `read_unaligned` with the
printed signatures and no `requires`:

```
verification results:: 4 verified, 0 errors
```

The four are `main`, a correct 8-byte header read, `hdr_oob` — `.add(131072)`
(1 MiB) off a slice with **no length precondition at all** — and `hdr_null`,
`core::ptr::null::<u64>().read_unaligned()`. **A heap over-read and a null deref
both verify.** The reviewer checklist's *"a wrong one axiomatises a falsehood"*
is realised here as *"a missing one axiomatises everything"*.

**(c) And the same hazard is one omitted line away on the arithmetic case
TASK_080 verified.** `.temp/r81/a_unsound.rs` — TASK_080's declaration with the
`requires` deleted and the `ensures r == a + b` kept:

```
verification results:: 2 verified, 0 errors      # `assert(false)` VERIFIES
```

Compiled (`.temp/r81/a_unsound_exec.rs`, `1 verified, 0 errors`), a function with
`ensures r == false` that returns `true`:

```
thread 'main' (41476) panicked at .temp/r81/a_unsound_exec.rs:18:31:
unsafe precondition(s) violated: i32::unchecked_add cannot overflow
...
thread caused non-unwinding panic. aborting.
```

Verus verified a program that hits real UB on its first call. Nothing checks an
`assume_specification` against anything.

**(d) The reason (c) cannot be repaired the vstd way.** vstd's sound reads take a
permission (`~/tools/verus/vstd/raw_ptr.rs:602`, `:620`:
`ptr_mut_read(ptr, Tracked(perm): Tracked<&mut PointsTo<T>>)`), and
`assume_specification` must match the real Rust signature
(`.temp/r81/e_ru_perm2.log`):

```
error[E0061]: this function takes 1 argument but 2 arguments were supplied
11 |     Tracked(perm): Tracked<&PointsTo<T>>,
   |     ------------- unexpected argument #2 of type `Tracked<&PointsTo<T>>`
```

**(e) A non-vacuous version exists — at 4 items for safety and 6 for safety +
value.** `.temp/r81/f_mm.rs` (1 `uninterp spec fn readable_at` + 3
`assume_specification`) makes the bad call bite:

```
error: precondition not satisfied  --> .temp/r81/f_mm.rs:66:14   (add's address bound)
error: precondition not satisfied  --> .temp/r81/f_mm.rs:66:14   (read_unaligned's readable_at forall)
verification results:: 2 verified, 1 errors
```

but its `read_unaligned` has an **empty `ensures`**, so the value read is
unconstrained — useless for a kernel with a functional postcondition. Carrying
the value needs a **generic** model, because monomorphising is refused
(`.temp/r81/g_value.log`):

```
error: assume_specification requires function type signature to match
       `core::ptr::const_ptr::impl&%0::read_unaligned` exactly
             assume_specification provided: `(*const u64) -> u64`
             expected:                      `for<T> (*const T) -> T`
```

so relating a `u64` read to `u8` slice bytes needs a **cross-type little-endian
decomposition axiom**. Built: `.temp/r81/h_full.rs`, **6 author-written trusted
items** (2 `uninterp spec fn`, 3 `assume_specification`, 1 `broadcast axiom fn`):

```
verification results:: 2 verified, 1 errors
# hdr_val: ensures v == spec_u64_from_le_bytes(s@.subrange(0,8))  -- VERIFIES
# hdr_oob: FAILS on both add's bound and read_unaligned's readable_at
```

Proof cost inside the kernel: two `broadcast use`, one `assert forall … by`, one
`=~=`. **The trusted item that carries the real risk (`ax_u64_le`, a
representation axiom about real Rust memory) is unavoidable**, because (e)'s
monomorphisation is refused.

**So the honest sentence for `.memory/04-verus.md` is not "+1 trusted item and
Verus prints the fix". It is: `+1` for a safe or arithmetic intrinsic whose
contract is one line; `+4` for memory safety alone on a pointer read; `+6` for
memory safety and value; and the printed declaration is a trap for three of the
six items.**

---

### MAJOR 4 — RECAP finding 14 (`RECAP.md:455-458`): *"every route to respelling a header read needs a new trusted item"* is REFUTED
The sentence lists six `is not supported` items and concludes that every route
needs a new trusted item. Two things are wrong with the inference.

**(a) The pinned vstd already ships the route, at ZERO author-written trusted
items.** `~/tools/verus/vstd/bytes.rs` has
`u64_from_le_bytes(s: &[u8]) -> u64  requires s@.len()==8  ensures x == spec_u64_from_le_bytes(s@)`
and `~/tools/verus/vstd/slice.rs:108` has `slice_subrange`. `.temp/r81/k_vstdbytes.rs`:

```rust
pub fn hdr_at(s: &[u8], off: usize) -> (v: u64)
    requires off <= usize::MAX - 8, off + 8 <= s@.len(),
    ensures  v == spec_u64_from_le_bytes(s@.subrange(off as int, off + 8)),
{ let w = slice_subrange(s, off, off + 8); u64_from_le_bytes(w) }
```

```
verification results:: 2 verified, 0 errors
```

An arbitrary-offset little-endian `u64` header read, with its value, at **zero**
new trusted items. Whether it is *in contract* for p05/p16 and what it costs in
`Ir` are open — but *"every route needs a new trusted item"* is false as stated,
and it is the sentence that carries finding 14's *"neither pattern's R4 side has
ever moved by a single admissible instruction"*.

**(b) The six-item list is not homogeneous, and one member is not reachable at
all.** `from_le_bytes` cannot be given an `assume_specification` at this pin — the
array length in the real signature is an anonymous associated const with no
writable spelling (`.temp/r81/j_fleb.log`, `.temp/r81/j_fleb2.log`):

```
error: assume_specification requires function type signature to match
       `core::num::impl&%9::from_le_bytes` exactly
             assume_specification provided: `([u8; 8]) -> u64`
             expected:  `([u8; core::::num::{impl#9}::from_le_bytes::{constant#0}]) -> u64`
```

Second attempt with `[u8; core::mem::size_of::<u64>()]` gives the same error.
Verus's own printed suggestion for this item is not valid Rust either.

*(This is a correction to the reach of the claim, not a refutation of finding 14
itself. Finding 14's pricing sentence — every route needs a **new trusted item** —
was already the right shape for the pointer route; it is the word "every" that
does not survive.)*

---

### MAJOR 5 — `.memory/03-measurement.md` (p27 entry): the extracted rule does NOT generalise
The entry closes with *"The distinction to keep: **check whether the symbol is
PRESENT, not whether the difference is zero**."*

**Sufficient on the shape it came from.** `/usr/bin/gcc -O2` on
`.temp/p31pat/cost_c.c`: the elided build has **zero** `malloc`/`free`
references; `-fno-builtin` gives `1 malloc@GLIBC_2.2.5 / 2 malloc@plt /
1 free@GLIBC_2.2.5 / 2 free@plt`.

**Not sufficient in general.** `.temp/r81/p27rule/gen_rule.c` is the same loop with
**one escaping allocation outside it**:

```
objdump:      1 free@GLIBC_2.2.5   2 free@plt   1 malloc@GLIBC_2.2.5   2 malloc@plt
llvm-objdump --disassemble-symbols=main:  the loop's malloc/free calls are GONE
callgrind:    n=10000  I refs: 185,298      n=110000  I refs: 385,520
              marginal = 2.00222 Ir/object
```

`2.00222` is the committed **BUILTIN-ELIDED** rate (`cost_marginal.log`:
`2.00192`). **The symbol is present and the allocator work in the measured region
is entirely elided.** Presence is necessary, not sufficient.

The evidence that actually settled p27 was a **rate** — `malloc` at
**421.1211 `Ir`/call in BOTH rungs** — which is the strong test. The weaker half
is what got written into `.memory/`. Suggested durable form: *"check the
symbol's per-call rate inside the measured region, not its presence in the
binary and not whether the difference is zero."*

---

### MINOR 6 — `.memory/00-environment.md:179-181`: the adjacency refinement is right for the wrong reason
The entry says: *"without ASan, gcc lays `y` SIXTEEN BYTES BEFORE `x` (`-16`) and
clang `+16` … A `y - x == +16` probe reports gcc "notadjacent" **with no
sanitizer at all**."*

Re-run on the original probe (`.temp/p45pat/san_attack.c`, `int x[4]={..};
int y[4]={..};`, no sanitizer):

```
gcc    -O0  delta=+16  ADJACENT
gcc    -O1  delta=-16  notadjacent
gcc    -O2  delta=-16  notadjacent
clang  -O0  delta=+16  ADJACENT
clang  -O1  delta=+16  ADJACENT
clang  -O2  delta=+16  ADJACENT
```

The claim holds **from `-O1` up** and is **false at gcc `-O0`**, where the sign is
`+16` and the naive probe reports ADJACENT. A second variant with `.bss`
declarations (`.temp/r81/adj.c`, `static char x[16]; static char y[16];`) gives
`gcc -O0 +16, gcc -O2 -16, clang -O0 -16, clang -O2 -16` — so the **sign depends
on optimisation level and on section, not on the compiler**. The entry's
conclusion (`|delta| == 16`) is **upheld and is stronger than it states**; its
per-compiler attribution should be deleted and the opt level named.

---

### MINOR 7 — `.tasks/TASK_081.md:8-10` uses RECAP's finding numbers against `.memory/01-ladder.md`
The task file cites *".memory/01-ladder.md **finding 14** … and **finding 17**
(p11)". In `.memory/01-ladder.md`, **14 is p13** (`:1763`) and **17 is p18**
(`:2019`); p11 is **finding 9** (`:1394`). The numbers used are RECAP's.
`.memory/01-ladder.md:385` says this collision is *live, not hypothetical*, and
the same file already records it having propagated once. Cite `RECAP finding N`
explicitly, the way `.memory/01-ladder.md:320` and `:540` do.

### MINOR 8 — `.tasks/TASK_081.md:156` mis-cites the source of `12.30×`
The re-derivation is **correct**: 15,565,615 / 1,265,467 = **12.300293**, and the
marginal 140.00150 / 10.00150 = 13.9979 → **14.00** (`.temp/p31pat/cost_marginal.log`).
But **neither number appears in `.temp/p31pat/cost_functions.log`**, which the
task file names — that file carries only percentages. The exact totals are in
`.temp/p45pat/NOTES.md:198` (`mode=0 n=110000 TOTAL=15565615 main_excl=990034`).
`.memory/03-measurement.md:1488` states the ratio with no file citation at all.

### MINOR 9 — `patterns/p11-nul-scan/NOTES.md` contradicts itself, and the escape makes it matter
`:1021` — *"shipping it would cost **four new trusted items** on a pattern whose
entire memory-safety claim is one trusted `requires`"* — is a **price**.
`:1030` and RECAP finding 17 (`RECAP.md:600`) — *"the unsafe class cannot reach it
at all"* — is an **impossibility**. Both are in p11's own record. The measurement
below shows the price is exact and the impossibility is false. (`.memory/04-verus.md`'s
claim that p11's triage language reads as impossibility is therefore **half
right**: the headline sentence does, the NOTES paragraph beneath it does not.)

---

## R1 — per-item table

Baseline (`.temp/r81/b_baseline.log`, `--multiple-errors 30`): all six confirmed
`is not supported` at the pin.

| # | item | (a) declaration accepted? | (b) correct call verifies? | (c) **bad call FAILS?** | (d) TCB cost |
|---|---|---|---|---|---|
| 0 | `i32::unchecked_add` (TASK_080's) | ✅ help text verbatim | ✅ | ✅ **yes, and directly** — `a_bite.log` `1 verified, 1 errors`, error at the call, citing the *assume_specification's* `requires` | **1** |
| 1 | `read_unaligned` | ⚠ **help text does not parse**; `<*const T>::read_unaligned` does | ✅ | ❌ **NO** as printed (`d_mem_escape.log` `4 verified, 0 errors`, incl. null deref) — ✅ **yes** under a hand-built model (`f_mm.log`) | **4** safety only, **6** with value (`h_full.log`) |
| 2 | `as_ptr` | ⚠ same; `<[T]>::as_ptr` parses | ✅ | ❌ / ✅ as above | shared with #1 |
| 3 | `add` | ⚠ same; `<*const T>::add` parses | ✅ | ❌ / ✅ as above | shared with #1 |
| 4 | `from_raw_parts` | ✅ help-text spelling parses | ✅ | ✅ **yes** — `i_frp.log` `2 verified, 1 errors`, the no-permission call site fails | **1** + the shared model |
| 5 | `TryFromSliceError` | ⚠ **help text rejected** (*"private fields not supported for transparent datatypes (try 'external_body' instead?)"*); accepted with `#[verifier::external_body]` added | ❌ — the `try_into().unwrap()` chain still fails (`m_tfse_use.log`, `vstd/std_specs/result.rs:181`, `unwrap` owes `is_Ok`) | n/a — it is a **type**, no `requires` exists | **1**, and needs a **second** (`TryFrom::try_from`) to be usable |
| 6 | `from_le_bytes` | ❌ **NOT REACHABLE AT ALL** — the array-length const has no writable spelling; help text is malformed Rust | n/a | n/a | **∞** by this route; **0** via `vstd::bytes::u64_from_le_bytes` |

**Answer to R1's question.** The escape **does** reach the memory items — it does
not stop where finding 14's claim lives — but it reaches them in a different
shape from the arithmetic case, and one item (`from_le_bytes`) it does not reach
at all. **The dangerous middle is (c): the declaration a reader gets from
`.memory/04-verus.md` and from Verus's help text has no `requires` and therefore
bites nothing.**

---

## R2 — p11's `r4_cstr`: the four items, named, and the escape run on each

The four (`patterns/p11-nul-scan/NOTES.md:964-975`, reproduced exactly at
`.temp/r81/o_cstr.log`):

| # | item | kind | route |
|---|---|---|---|
| 1 | `core::ffi::c_str::CStr` | **TYPE** | `external_type_specification` + `external_body` |
| 2 | `core::ffi::c_str::FromBytesUntilNulError` | **TYPE** | same |
| 3 | `CStr::from_bytes_until_nul` | fn, **SAFE** | `assume_specification` |
| 4 | `CStr::to_bytes` | fn, **SAFE** | `assume_specification` |

`.temp/r81/p_cstr_escape.rs`, all four written at once:

```
verification results:: 2 verified, 0 errors
```

**First try. Four trusted items, exactly as p11's own `NOTES.md:1021` priced it.**

**But the sentence the measurement supports is not the one the number invites.**

- ⚠ **Two of the four are TYPES.** `assume_specification` does not apply to them;
  `external_type_specification` does, and **Verus's printed form is rejected** for
  both (the `TryFromSliceError` diagnostic above), needing `+ external_body`.
  *"Rejected with four `is not supported` errors"* is therefore not four
  applications of one mechanism.
- ⚠ **Both functions are SAFE, so there is no `requires` to bite.** (c) is not
  *"does a bad call fail"* — it is *"does anything check the `ensures`"*, and
  nothing does. `r4_cstr` at +4 items is four unchecked claims about
  `core::slice::memchr`'s wrapper, with no twin, no conjunct-deletion stage, and
  no Miri (Blocker 1).
- ⚠ **The `identity` pin does NOT stop it.** An `assume_specification` emits zero
  instructions (Blocker 1's md5 evidence), so `r4_cstr`'s R5 twin would be
  byte-identical to its R4 by construction. **The pin is not the obstacle it was
  assumed to be here.**

**The sentence the measurement supports:** *"the unsafe class reaches
`core::slice::memchr` at four hand-written axioms that no gate stage checks, on a
pattern whose whole claim rests on one trusted `requires` that four stages do
check."* **Not** *"cannot reach it at all"* (RECAP finding 17 / p11 NOTES:1030),
and **not** *"p11's finding flips"*. The 35% number does not decide the sentence;
the **asymmetry in what is checked** does, and it is a stronger result than
either.

⚠ **Not done:** I did not build `r4_cstr` or run its twin through `check.py` —
that is engineer work and out of a reviewer's scope. The identity claim above is
derived from the zero-instruction measurement, not from a built twin.

---

## R4 — the p45 refusal

**The `readelf` evidence is load-bearing and it REPRODUCES EXACTLY.**
`~/.cargo/bin/rustc -C opt-level=3 -C debug-assertions=off --crate-type=lib --emit=obj`
on `.temp/p45pat/cost_rs.rs`:

```
 7:  60 FUNC GLOBAL DEFAULT  3 k_checked      12:  60 FUNC GLOBAL DEFAULT  3 k_overflowing
 8: 155 FUNC GLOBAL DEFAULT  4 k_plain        13: 155 FUNC GLOBAL DEFAULT  4 k_wrapping
10: 155 FUNC GLOBAL DEFAULT  6 k_unchecked

[ 3] .text.k_checked        size=  60 md5=cef325780cf71be543f6caddb2795e14
[ 4] .text.k_plain          size= 155 md5=85bd268b3def0d5e386f1498706a6b2b
[ 6] .text.k_unchecked      size= 155 md5=85bd268b3def0d5e386f1498706a6b2b
```

Both halves confirmed: `k_plain`/`k_wrapping` two symbols on section **4**,
`k_checked`/`k_overflowing` two symbols on section **3**, and `k_unchecked`'s own
155-byte section md5-identical to `k_plain`'s — **`85bd268b3def0d5e386f1498706a6b2b`**,
the manager's digest, to the character. **The refusal stands on its evidence
regardless of framing.**

**Fourth framing: ATTEMPTED AND FAILED — clean negative, and it is the second
independent failure, which closes the row.**

What I tried, and why it was the only candidate worth trying: the one place
signed-overflow UB is *measured* to buy anything is the **`int` induction
variable** (`.temp/p45pat/NOTES.md:263-282`: `nsw_2d` gcc `-O3` 75→28 under
`-fwrapv`), while the accumulator gets nothing. So the framing would be *"the
kernel's index arithmetic is the UB site, the harm is the deleted bound, and R4
gets `nsw` for free"*. `.temp/r81/r4_framing.rs`, three spellings of the same 2-D
fold, `rustc -C opt-level=3 -C debug-assertions=off`:

```
k_idx_plain      368 bytes  104 insns   (i32 index, wrapping_add accumulate)
k_idx_unchecked  331 bytes   95 insns   (unchecked_mul/unchecked_add on the index)
k_idx_usize      315 bytes   91 insns   (the SAFE spelling -- no UB available at all)
```

**The safe `usize` spelling is the cheapest of the three**, reproducing the C
result in Rust: `size_t`/`usize` gets same-or-better codegen with no UB, so there
is no framing in which `unchecked_*` gives R4 a job. Generalising the reason,
which the refusal did not: **for every `unchecked_op` there is a safe
`wrapping_op` with the same machine code whenever the precondition holds**, so
the arithmetic-intrinsic family can never separate R3 from R4 by construction.
That is a stronger closing argument than "under two contracts".

**Other framings considered and rejected without a compile, with reasons:**
*(i)* obligation-in-a-`requires`, p11-style — that **is** the *"caller guarantees
no overflow"* contract, and the byte-identity above kills it; *(ii)* a defensive
R3 (`checked_add(..).expect()`) against an `unchecked_add` R4 — the checker is
dead under the contract, so it is a pessimised R3 and the reviewer checklist's
*"deliberately pessimised?"* test refuses it, and TASK_080 already records the
`checked`-vs-`wrapping` gap as **safe-against-safe**, no rung boundary running
through it; *(iii)* overflow-as-detection — refuted in TASK_080, `unchecked_add`
cannot implement it.

---

## R5 — the p16 half of the ladder test, measured

The block's own two commands, run on `.temp/build/p16/*-O3-isolated`:

```
safe_tuned  Ndx=15  _RNvCs86OlWC8CPt8_10safe_tuned6kernel  size=410  md5=0b8c64b6b08b62fefcbc88d9fdfa18dc
unsafe      Ndx=15  _RNvCsbJ183vTuGGA_6unsafe6kernel       size=324  md5=7952ec0bc154820792edcab6eb7484f4
verus       Ndx=15  _RNvCs5wP2qveqZnT_5verus6kernel        size=324  md5=7952ec0bc154820792edcab6eb7484f4
```

**The distinction the block claims is REAL: p16's R3 and R4 differ in size and in
md5, where p45's collide.** ✅ Clean negative — *"is it a rationalisation
available after the fact?"* is answered **no**, on the block's own instrument.
(Note also `unsafe` ≡ `verus` exactly, which is the `identity` pin.) The defects
in the block are the ones listed under Blocker 2 (f) and (g), not this one.

---

## Clean negatives — named attacks that did NOT land

1. **"TASK_080 only tested the wrapper's `requires`, not the axiom's."** Refuted.
   `.temp/r81/a_bite.rs` calls `a.unchecked_add(b)` from a function with **no**
   precondition: `1 verified, 1 errors`, the error at the call site citing the
   *assume_specification's* own `requires` as the failed precondition. **Item 6's
   "the requires bites" survives.**
2. **"p45's `readelf` evidence is soft."** Refuted — reproduced to the digest.
3. **"There is a fourth framing for p45."** I could not find one either; the
   `nsw`/induction-variable route is measured dead in Rust (above). **Two
   independent failures.**
4. **"p16's genuine-zero story is a post-hoc rationalisation."** Refuted by the
   block's own commands (above).
5. **"p47 fails the ladder test's cost half."** Refuted — R3 − R4 is
   **+90.0 / +142.0 Ir/call**. (p47 fails the *other* half.)
6. **"`8.6×` reconstructs from something in the committed log."** Refuted. A
   pairwise scan of every number in `cost_functions.log`, `cost_marginal.log` and
   `prov_matrix.log` for a ratio in [8.55, 8.65] returns four hits, all spurious
   (a truncated percentage `86.0/10.0`; two from hex addresses parsed as
   decimal). **`.memory/03-measurement.md:1493`'s "reconstructs from nothing" is
   upheld**, and so is `12.30×` (12.300293) and `14.00×` (13.9979).
7. **"The p27 symbol-presence rule is wrong on the case it came from."** Refuted —
   on `.temp/p31pat/cost_c.c` the elided build has **zero** `malloc`/`free`
   references. It is only the *generalisation* that fails (Major 5).
8. **"You can quietly re-axiomatise something vstd already specifies."** Refuted —
   `assume_specification [<[T]>::len]` gives
   *"specification declared via `assume_specification` → vstd/slice.rs:83"*.
   Verus rejects duplicates.
9. **"You can monomorphise an `assume_specification` to give a per-type value
   spec."** Refuted — *"requires function type signature to match … exactly"*
   (`g_value.log`). This is what forces the extra representation axiom.
10. **"The escape lets `unsafe` into a pattern without a trusted wrapper."**
    Does not land: `_scan_unsafe_sites` (`check.py:3295`) hard-fails any `unsafe`
    token outside a trusted body, so an unsafe intrinsic still needs an
    `external_body` wrapper, which **is** counted. Blocker 1's hole is specific to
    axioms on **safe** functions. *(Read from source; not run against a live
    pattern.)*
11. **PROTOCOL rule 10 check** — `grep -rho '\.tasks/TASK_[A-Za-z0-9_]*\.md' .memory/ .tasks/ RECAP.md`
    reports only the two documented placeholders (`TASK_NNN.md`,
    `TASK_NNN_REVIEW_REPORT.md`). This report exists.

---

## Not done / limits

- **I did not build `r4_cstr`, `r4_hdr` or any rung**, and did not run
  `harness/check.py` on anything. Reviewer scope.
- **The `Ir` cost of the zero-TCB `slice_subrange` + `u64_from_le_bytes` route is
  unmeasured.** `u64_from_le_bytes` is `u64::from_le_bytes(s.try_into().unwrap())`
  under the hood, so it carries a length check and a panic path and may well be
  *dearer* than the shipped spelling. Major 4 refutes finding 14's stated
  **reason**; whether R4 actually *moves* is a separate, cheap measurement that
  nobody has run.
- **Clean negative 10 is read from `check.py` source, not executed.** Confirming
  it needs a live pattern with an `unsafe` block outside a trusted body, which
  means editing a pattern — out of scope here.
- **The `readable_at` / `val_at` model in `f_mm.rs` / `h_full.rs` is mine and is
  unaudited.** It exists to answer *"can (c) be made to bite, and at what
  count?"*, not as a design to adopt. Its `ax_u64_le` is exactly the kind of axiom
  this report says nothing checks.
- **`.memory/04-verus.md`'s claim that "four patterns (p05, p07, p11, p18) triaged
  R4 candidates in that language"** — I checked p11 in detail and p05/p16 through
  RECAP finding 14. p07 and p18 I did not re-read.
