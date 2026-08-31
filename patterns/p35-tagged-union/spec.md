# p35 — tagged union / discriminated dispatch (the TYPE axis)

**CWE-843, access of a resource using an incompatible type.** A cell is a TAG
plus a UNION. Storing a pointer or a double takes a byte out of a budget that
can run out, so the store has a **failure path** — and `c/kernel.c` publishes
the tag **before the payload lands**. When the budget is exhausted the cell
claims to hold a pointer (or a double) while the union still holds the integer a
previous `SET_INT` put there, and the dispatcher reads it **at the claimed
type**.

⚠ **NOT A TEMPORAL ROW.** Nothing here is allocated, freed, recycled or aliased.
`p35` was carried in `TASK_143`'s temporal re-adjudication list only because its
old refusal was Verus-side; the axis is **TYPE**, and this is the tree's
**second** type row after `p38`.

## The kernel

```
window = buf[off .. off+len)
nops       = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
data_start = 4
op         = 2 bytes: c = opcode byte, a = operand byte   ALL ATTACKER DATA

CELLS  = 8     tagged cells                 a compile-time constant
BUDGET = 4     arena bytes; how many        a compile-time constant
               pointer/double payloads can
               be issued before the store
               starts FAILING
SENT   = 251   what a rejected op folds     a compile-time constant
T_UNSET/T_INT/T_PTR/T_DBL = 0/1/2/3         the tag alphabet

cells[CELLS] all (T_UNSET, 0) ; arena[j] = (j*11+5) & 255 ; navail = BUDGET
acc = 0 ; p = 4
for o in 0 .. nops:
    if len - p < 2: break
    c = buf[off+p] ; a = buf[off+p+1] ; p += 2 ; idx = a % CELLS
    switch c % 4:
      0 SET_INT: payload = a * 2654435761 (u64) ; tag = T_INT
                 acc = acc*31 + a
      1 SET_PTR: if navail > 0: payload = &arena[BUDGET-navail]   (C)
                                        = BUDGET-navail  (u32)    (Rust)
                                THEN tag = T_PTR ; navail -= 1 ; acc = acc*31 + 1
                 else:          acc = acc*31 + SENT
      2 SET_DBL: if navail > 0: payload = (a % 2 == 0) ? 0.25 : 2.5
                                THEN tag = T_DBL ; navail -= 1 ; acc = acc*31 + 2
                 else:          acc = acc*31 + SENT
      3 GET:     T_INT   -> acc = acc*31 + (payload & 0xFF)
                 T_PTR   -> acc = acc*31 + *payload   (C)  /  arena[payload]  (Rust)
                 T_DBL   -> acc = acc*31 + (payload > 1.0 ? 1 : 0)
                 T_UNSET -> acc = acc*31 + SENT
return acc*31 + navail
```

**THE SAFETY LINE is the word `THEN`.** `c/kernel_hardened.c` publishes the tag
inside the `navail > 0` test, after the payload store; `c/kernel.c` publishes it
before the test. **Nothing is added and nothing is deleted** — the preprocessed
diff is `+2 / −2` lines and a pure reorder at both sites
(`controls/safety_line.py`).

⚠ **That is a third SHAPE of safety line for this tree.** `p27`'s is a
**conjunct**, `p13`'s is a **store**, `p35`'s is a **sequencing constraint**.

## Two bug classes, one ordering, selected by the input

| input | harm | what any detector says |
|---|---|---|
| `adversarial-ptr-confusion`, `adversarial-ptr-deep` | `GET` dereferences an **attacker-derived integer** | **SIGSEGV**, `exit 139`; ASan reports `SEGV on unknown address` |
| `adversarial-dbl-confusion`, `adversarial-exhaust` | `GET` compares a **garbage double** → a silent wrong value | **NOTHING**, anywhere: ASan, UBSan, gcc and clang at `-Wall -Wextra`, and Miri on the Rust reproduction |

⚠ **The asymmetry is the row's result.** One ordering, two harms, and the
detector coverage differs by the TYPE the tag happens to name. Reading a union
member other than the one last stored is **defined** in C99 (6.2.6.1p7,
6.5.2.3): the DBL arm executes no undefined behaviour at all and is simply
wrong. The PTR arm's undefined behaviour is the **dereference**, not the union
read that produced the pointer.

⚠⚠ **A POSITIVE CONTROL LICENSES ONLY THE DETECTOR IT FIRES IN**, so the silence
in the second row needs a **UBSan-specific** control and not merely an ASan one:
`.temp/mgr147/NOTES.md` found `TASK_143`'s demonstration failing exactly that
test (its control SIGSEGVed at `rc=139` under `ubsan` with **0** diagnostics,
which is indistinguishable from a UBSan that is not linked in — RECAP trap 5,
`.memory/03-measurement.md` entry 14). `controls/detectors.py` ships one control
per detector.

## What each rung spells

| rung | the cell | the safety line |
|---|---|---|
| **R1** `c/kernel.c` | `uint8_t tag` + `union { uint64_t i; double d; uint8_t *p; }` | **absent** — the tag is published before the payload lands |
| **R1h** `c/kernel_hardened.c` | the same | present: the tag store moves inside the `if` |
| **R2** `safe_naive.rs` | `enum Cell { Unset, Int(u64), Ptr(u32), Dbl(f64) }` | **it has no site** — tag and payload are ONE value written by ONE assignment |
| **R3** `safe_tuned.rs` | the same `enum` | the same: none |
| **R4** `unsafe.rs` | `[u8; CELLS]` of tags beside `[Pay; CELLS]` of unions | **back, and written by hand**, at two sites |
| **R5** `verus.rs` | the same, plus `wf_cells` | the same, and it is the invariant the proof maintains |

⚠⚠ **The gradient is in OBLIGATION, not in instructions.** Safe Rust does not
"pay" for the type discipline — it gets it from the `enum` at zero run-time cost
— and `unsafe` does not "buy" speed with it, it buys bounds checks and *acquires*
the correct-variant obligation as a side effect of the representation it needs to
match C. `NOTES.md` 3 has the numbers.

## ⚠⚠ The one place the rungs are not isomorphic, disclosed

**The C union holds a POINTER; the four Rust rungs hold the ARENA OFFSET.**
`.memory/01-ladder.md`'s own rule decides this: *a rung covered by an `identity`
pin is chained to the prover.* This pattern pins `identity: unsafe ≡ verus`, and
R5 cannot hold a `*const u8` and dereference it without `vstd::raw_ptr`'s
`PointsTo` machinery — which is `p27`'s and `p29`'s row, and would put an
allocation proof inside a type-confusion pattern. So R4 inherits the constraint
and R2/R3 follow R4 so that all four Rust rungs are one algorithm.

`*p` and `arena[o]` name the same byte, so **every checksum agrees on every
input**, adversarial ones included. What the substitution changes is the
addressing mode and — the part that matters — **the CLASS of the loud harm, and
therefore which instrument reports it**: an offset read at the wrong type is a
wrong index, not a wild pointer, so the unsafe arm still SIGSEGVs (`rc=-11`,
like C) but does so through an out-of-bounds `get_unchecked` that **Miri
reports**, and the safe arm panics. ⚠ **An earlier draft of this paragraph said
the substitution *"removes the LOUD harm from the Rust side entirely"*, and
`controls/rust_bug.py` refutes the natural reading of that.** `NOTES.md` 5
measures it.

## The proof domain, and why every adversarial input is inside it

The kernel's only precondition is `off + len <= buf_len`, which the driver
establishes structurally. **Everything the file can say is inside the domain**:
`nops` may be any `u32` and bounds nothing (the cursor guard stops the walk),
every opcode byte is legal (`c % 4`), every operand byte names a cell
(`a % CELLS`), and a store the budget cannot serve folds `SENT`. So the
adversarial inputs are not out-of-domain calls — they are ordinary calls whose
answer `c/kernel.c` gets wrong.

## The pins, and the arithmetic behind two of them

| pin | why |
|---|---|
| `verus.obligations` = 16 | **7 consts + 1 recursive spec fn (`run`) + kernel 3 + main 5.** Every function term was measured with `--verify-function <name> --verify-root`; `.temp/t148/verus/obligations.log` is the census. The eleven non-recursive `spec fn`s carry ZERO, and so does the `union` declaration — there is no datatype term. |
| `verus.twin_obligations` = 20 | the count under `--cfg slb_twin`. **16 shipped + 4**, one per trusted item that HAS a twin. ⚠ **Three trusted items have none and cannot**, which is the row's R5 result — see `verus.twin_justifications`. |
| `identity` `O3: exact`, `O0: norel` | R4 ≡ R5 by raw machine-code bytes at `-O3`. Same as `p32` and `p38`: there is no vstd call and no pointer write in this kernel, so R4 and R5 have nothing to spell differently. |
| `miri.required: true` | derived from the trusted items. ⚠ **What Miri finds is NOTHING**, on every input including all four adversarial ones — and it finds nothing on `controls/arm_unsafe_bug.rs` either, which is the buggy ordering written in unsafe Rust. **Reading a union member other than the one last stored is not UB in Rust when the bytes are a valid value of the field's type**, and every bit pattern is valid for `u32`, `u64` and `f64`. That is the row's detector-coverage result, not a gap in the run. |

⚠⚠ **`verus.twin_justifications` is not decoration here and it is the thing to
read first.** The three union readers `pay_i`, `pay_o` and `pay_d_gt1` are
`#[verifier::external_body]` because `harness/check.py`'s `_scan_unsafe_sites`
requires every `unsafe` token to sit inside a trusted item's body, and a union
read is spelled `unsafe { p.i }` in Rust whether or not Verus checks it. Being
trusted, each owes a **verified twin** — and **Rust has no safe spelling of a
union read at all** (`error[E0133]`), while `_TWIN_BANNED` forbids `unsafe` in a
twin. So the gate **BLOCKS** all three, out loud, on every run.

**The configuration the gate refuses is the STRONGER one.** Verus supports the
Rust `union` natively: the correct-variant obligation is first class in the type
system, and a wrong-variant read inside a verified function is
`error: requirement not met: to access this field, the union must be in the
correct variant`. `controls/union_oracle.py` measures both configurations side
by side with a must-fail arm on each. **This row ships the honest configuration
and makes the gap the finding** — `p42`'s precedent, *"THE PIN PROTECTED THE
PATTERN; THE PROOF DID NOT"*, in a different currency. `NOTES.md` 6.

⚠ **What the shipped configuration still gets.** The wrappers' `requires`
include `v@[i as int] is i` / `is o` / `is d`, and **Verus checks those at every
call site**: delete the tag test in front of a `pay_*` call and the proof fails
with `precondition not satisfied` (`controls/proof_mutants.py`, arm
`M1-drop-tag-test`). The tag/variant agreement IS proved. What is axiomatised is
only that each wrapper's body reads the member its name says.

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == cell_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (cell_fold). p35's bindings are the READ-ONLY set p03, p06, p11, p12, p14, p16, p17, p05, p07, p27, p29, p32 and p38 use and NOT p02's before/after set: p35's cells and arena are LOCALS of the kernel, so no buffer crosses the signature and there is nothing for an `after` binding to name. **The security property is carried by a STATEMENT ORDERING at TWO sites** -- the tag store moves inside the `navail > 0` test, after the payload store -- and at R5 it is discharged as the loop invariant `wf_cells`, which says a cell's tag names the union member its payload actually is. ⚠⚠ **That invariant is what the `requires` of every `pay_*` call needs**, so unlike p32's conjunct it is not merely a functional obligation: deleting the tag test in front of a union read fails with `precondition not satisfied` rather than with a wrong postcondition (controls/proof_mutants.py, M1). ⚠ **But the READ ITSELF is an axiom in the shipped configuration and that is the row's R5 result**: the gate requires every `unsafe` token to live in an `#[verifier::external_body]` body, which moves the union read out of the region Verus checks -- and Verus checks union reads NATIVELY, so the refused configuration is the stronger one. controls/union_oracle.py measures both. The `ensures` is the FUNCTIONAL one: `run` is an abstract machine carrying the tag sequence, the payload sequence and the budget, and it says the accumulator is what that machine computes -- so a kernel that folded a wrongly-typed read could not satisfy it. ⚠ `f64` is OPAQUE at the pinned vstd (its arithmetic carries an undischargeable `add_req` and `u8 as f64` is a possibly-non-deterministic cast), so the DBL payload is built from LITERALS and the exec comparison `d > 1.0` is axiomatised against the spec function `dbl_gt1` inside `pay_d_gt1`. The proof establishes that the kernel folds `dbl_gt1(dbl_of(a))` consistently with the spec; it does not establish what that boolean is. NOTES.md 6c.",
  "idiom": {
    "required": [
      {
        "c": "THE CELL IS A TAG PLUS A UNION, in both C rungs and in c/kernel.h: `uint8_t tag;` beside `union {`, `uint64_t i;`, `double d;`, `uint8_t *p;`. This is the representation the whole pattern is about -- eight bytes with no record of which member was last stored, and a tag that is the only claim about them.",
        "rust": "the same representation in R4 and R5: `union Pay {` with `i: u64`, `d: f64` and `o: u32`; and the SAFE ANSWER to it in R2 and R3, `enum Cell {` with `Int(u64)`, `Ptr(u32)` and `Dbl(f64)`. ⚠ The union's third member is the arena OFFSET where C's is a POINTER -- see the why key, which is where that substitution is argued and measured."
      },
      {
        "c": "THE SAFETY LINE. In c/kernel_hardened.c the tag store sits INSIDE the budget test, after the payload store: `cells[idx].u.p = &arena[P35_BUDGET - navail];` immediately followed by `cells[idx].tag = P35_T_PTR;`. c/kernel.c spells the SAME two statements in the OTHER ORDER and differs in nothing else. ⚠ **A text pin cannot express an ORDERING**, so both rungs contain both tokens and this entry pins the STATEMENTS, not the sequence; ../controls/safety_line.py preprocesses the two shipped files and measures the sequence (`+2 / -2` lines, a pure reorder at both sites). That division of labour is stated rather than left implicit.",
        "rust": "the same ordering, written by hand, in R4 and R5 only: `pay_set_unchecked(&mut pays, idx, Pay { o: (BUDGET - navail) as u32 });` immediately followed by `arr_set_unchecked(&mut tags, idx, T_PTR);`, inside `if navail > 0 {`. ⚠⚠ **R2 and R3 have NO SITE for this line and that is the row's safe-Rust result, not an omission**: `cells[idx] = Cell::Ptr((BUDGET - navail) as u32);` writes the discriminant and the payload as ONE value, so the two cannot come apart. See the why key."
      },
      {
        "c": "THE TAG IS PUBLISHED ONLY BY A STORE, NEVER CLEARED, in both C rungs. Nothing writes `cells[idx].tag` except the three SET arms, and a cell nothing has written keeps tag 0 and folds `P35_SENT`. That is what keeps p35's bug from being `read uninitialised` -- see the why key.",
        "rust": "the same in all four Rust rungs: the `T_UNSET` / `Cell::Unset` arm folds `SENT`."
      },
      {
        "c": "A FAILED STORE IS STILL ACCOUNTED FOR: the `else` arm folds `P35_SENT` in both C rungs, so the fold's length is a function of the op count alone and the bug is never `the fold lost an operation`.",
        "rust": "the same `SENT` arm in all four Rust rungs."
      },
      {
        "c": "THE BUDGET IS DECREMENTED ONLY BY A STORE THAT HAPPENED: `navail--;` inside the `if (navail > 0)` in both C rungs, so both return the same trailing term.",
        "rust": "the same, in all four Rust rungs: `navail = navail - 1;`."
      },
      {
        "c": "the cell index is `a % P35_CELLS`, so EVERY operand byte names a cell and no input is rejected for being malformed: `idx = (size_t)(a % P35_CELLS);` in both C rungs.",
        "rust": "the same, in all four Rust rungs: `(a % CELLS as u8) as usize`."
      },
      {
        "c": "the opcode is `c % 4`, so EVERY byte value is a legal opcode: `c % 4 == 0` in both C rungs.",
        "rust": "the opcode, in all four Rust rungs. ⚠ R3 spells it `match c % 4 {` rather than as a chain of `if`s, which is the R3 lever and is deliberately not pinned to one spelling -- see the why key."
      },
      {
        "c": "the fold is a serial Horner chain over `acc`, spelled with the literal multiplier, ONCE per operation: `acc = acc * 31 + ` in both C rungs.",
        "rust": "the fold, in all four Rust rungs, spelled with the literal multiplier: `acc.wrapping_mul(31).wrapping_add(`."
      },
      {
        "c": "the remaining budget is folded last, so a rung that served a different number of stores cannot produce the same checksum: `return acc * 31 + (uint64_t)navail;` in both C rungs.",
        "rust": "the same, in all four Rust rungs: `acc.wrapping_mul(31).wrapping_add(navail as u64)`."
      },
      {
        "c": "THE DBL PAYLOAD IS TWO LITERALS AND NOT `(double)a + 0.5`, in both C rungs: `(a % 2 == 0) ? 0.25 : 2.5`. This is a MEASUREMENT and not a preference -- see the why key.",
        "rust": "the same two literals in all four Rust rungs: `if a % 2 == 0 { 0.25 } else { 2.5 }` in R2/R3 and `Pay { d: 0.25 }` / `Pay { d: 2.5 }` in R4/R5."
      }
    ],
    "forbidden": [
      "`transmute`",
      "`from_bits`",
      "`to_bits`",
      "`read_unaligned`",
      "`align_to`",
      "`memcpy(`",
      "`malloc(`",
      "`calloc(`",
      "`realloc(`",
      "`free(`",
      "`std::alloc::`",
      "`vstd::raw_ptr::`",
      "`Box::new`",
      "`Box::into_raw`",
      "`ManuallyDrop`",
      "`mem::forget`",
      "`Rc<`",
      "`RefCell`",
      "`Vec::with_capacity`"
    ],
    "why": "POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ONE STATEMENT ORDERING CARRIES TWO BUG CLASSES SELECTED BY THE INPUT, AND THAT IS THE ROW. When the budget is exhausted, `c/kernel.c` publishes a tag whose payload never landed; a GET then reads the union AT THE CLAIMED TYPE. tag PTR over an int payload DEREFERENCES AN ATTACKER-DERIVED INTEGER -- SIGSEGV, exit 139, and ASan reports it. tag DBL over an int payload compares a GARBAGE DOUBLE and produces a SILENT WRONG VALUE that NOTHING reports: not ASan, not UBSan, not gcc or clang at -Wall -Wextra, and not Miri on the Rust reproduction. Which harm the input gets is chosen by which opcode the failing store carries, and the ordering is the same one. THE SAFETY LINE IS A SEQUENCING CONSTRAINT AND THAT IS A THIRD SHAPE FOR THIS TREE: p27's is a CONJUNCT, p13's is a STORE, p35's is an ORDER. The preprocessed diff between the two shipped C files is `+2 / -2` lines and a PURE REORDER at both sites, measured by controls/safety_line.py rather than asserted -- nothing is added, no test is introduced, no load and no branch. \u26a0\u26a0 THIS SENTENCE IS CORRECTED AFTER MEASURING AND THE ORIGINAL IS STRUCK RATHER THAN QUIETLY REPLACED (PROTOCOL rule 6's added step; p46's defect, caught here by the author before shipping). It read: ~~the R1-vs-R1h cost of this pattern's safety is a SCHEDULING difference and nothing more, which is why NOTES.md 4 reports it as a per-call figure with its own noise floor rather than as a headline~~. MEASURED, R1h is CHEAPER than R1 on both compilers and both inputs -- -13.71 to -215.86 Ir/call, four figures, every one of them outside the coin-flip band results/synthesis.md publishes -- and the candidate mechanism is NOT scheduling: c/kernel.c performs the tag store on the FAILURE path too, 32.76 times per call on large.bin and 3.67 on small.bin (.temp/t148/failed_stores.py). So the safety line is BETTER THAN FREE, NOTES.md 4 does report that as a headline, and what NOTES.md 4 marks OPEN is the MECHANISM, because the implied per-store cost is 2.62 Ir on gcc/large against 3.74 on gcc/small and is therefore not stable. NOTHING IS ALLOCATED, FREED, RECYCLED OR ALIASED IN ANY RUNG, AND THE ROW IS NOT TEMPORAL. The cells and the arena are locals whose extent is a compile-time constant. p35 was carried in TASK_143's temporal re-adjudication list only because its old refusal was VERUS-side; the axis is TYPE, and this is the tree's second type row. THE NEAREST BUILT ROWS AND WHY THIS DUPLICATES NEITHER: p19 is a state machine with no union and no reinterpretation of one object's bytes at a second type; p16's variant selector bounds a LENGTH rather than choosing a TYPE; and p38 -- the other TYPE row -- turns on C99 6.5p7 EFFECTIVE TYPE and its harm is a MISCOMPILE, while p35 executes NO aliasing violation at all. Reading a union member other than the one last stored is DEFINED in C99 6.2.6.1p7 and 6.5.2.3, and the shipped kernels are built `-fstrict-aliasing` in the sanitizer stage without a word from either compiler. p38's answer was that Rust has NO type-based aliasing rule for `unsafe` to unlock; p35's is the opposite and that is why it is a row -- Rust DOES have a correct-variant rule for unions, `unsafe` IS required to break it, and Verus checks it NATIVELY. THE C UNION HOLDS A POINTER AND THE FOUR RUST RUNGS HOLD THE ARENA OFFSET, DISCLOSED HERE BECAUSE IT IS THE ONE PLACE THE RUNGS ARE NOT ISOMORPHIC. `.memory/01-ladder.md`'s own rule decides it: a rung covered by an `identity` pin is CHAINED TO THE PROVER, this pattern pins `identity: unsafe == verus`, and R5 cannot hold a `*const u8` and dereference it without `vstd::raw_ptr`'s `PointsTo` machinery -- which is p27's and p29's row and would put an allocation proof inside a type-confusion pattern. `*p` and `arena[o]` name the same byte, so every checksum agrees on every input including the adversarial ones; what the substitution changes is the addressing mode, and -- the part that matters and is stated rather than buried -- IT CHANGES THE CLASS OF THE LOUD HARM AND THEREFORE WHICH INSTRUMENT REPORTS IT. \u26a0\u26a0 THIS SENTENCE IS ALSO CORRECTED AFTER MEASURING, ORIGINAL LEFT VISIBLE: it read ~~IT REMOVES THE LOUD HARM FROM THE RUST SIDE ENTIRELY~~, and controls/rust_bug.py refutes the natural reading of that -- the unsafe arm SIGSEGVs on adversarial-ptr-confusion and adversarial-ptr-deep, rc=-11, exactly as c/kernel.c does. What changes is the CLASS: an offset read at the wrong type is a WRONG INDEX and not a WILD POINTER, so the Rust arm's crash is an out-of-bounds `get_unchecked` that MIRI REPORTS as Undefined Behaviour -- where Miri says nothing at all about the union read itself -- and the safe arm turns the same step into a PANIC. The CWE-822 dereference-of-an-attacker-derived-integer does not survive into any Rust rung; a crash does. That is why `vstd::raw_ptr::`, `malloc(`, `free(`, `std::alloc::` and `Box::new` are forbidden: a rung that allocated would be measuring a different pattern. THE DBL PAYLOAD IS TWO LITERALS RATHER THAN `(double)a + 0.5`, AND THAT IS A MEASUREMENT. At the pinned Verus/vstd, `f64` ARITHMETIC carries an `add_req` precondition nothing discharges (vstd/std_specs/ops.rs) and `u8 as f64` is specified as a *(possibly) non-deterministic Rust cast* (vstd/float.rs), while an `f64` LITERAL verifies -- four probes, .temp/t148/verus/probe3.rs and probe4.rs, NOTES.md 6c. Every rung spells the same conditional, so no rung is disadvantaged, and the confusion is still detectable: the correct value is `2.5 > 1.0` for an odd operand and the confused one is a subnormal that is not. `from_bits` AND `to_bits` ARE FORBIDDEN FOR A SHARPER REASON THAN TIDINESS: they are safe Rust's TOTAL reinterpretation -- every bit pattern is a valid `f64` -- so a rung spelling them would delete the correct-variant obligation altogether and the pattern with it, while looking like the same algorithm. `transmute`, `read_unaligned` and `align_to` are forbidden as the other routes to the same deletion, and `memcpy(` because copying the payload out is a third. WHAT IS DELIBERATELY NOT PINNED is how R3 walks the op stream -- `chunks_exact(2).take(nops)` against R2's cursor -- exactly as p32 leaves its handle-register spelling unpinned and p14 leaves its fold loop. That is the R3 lever, it costs zero TCB, and NOTES.md 3 reports what it moves. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 16
    },
    "twin_obligations": {
      "verus.rs": 20
    },
    "obligations_note": "16 = SEVEN consts (CELLS, BUDGET, SENT, T_UNSET, T_INT, T_PTR, T_DBL) 1 each + run 1 + kernel 3 + main 5. Every FUNCTION term was measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, not predicted; the census is .temp/t148/verus/obligations.log. ⚠ The ELEVEN non-recursive `spec fn`s carry ZERO, and so does the `union Pay` declaration -- there is no datatype term, which is the same result p32 recorded for its bare `struct`.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. **16 shipped + 4**, one per trusted item that HAS a twin: buf_get_unchecked, arr_get_unchecked, arr_set_unchecked and pay_set_unchecked. ⚠⚠ **THREE trusted items have no twin and CANNOT** -- pay_i, pay_o and pay_d_gt1 -- so this number is 4 and not 7, and the difference is the row's R5 result rather than an oversight. See verus.twin_justifications.",
    "twin_justifications": {
      "verus.rs": {
        "pay_i": "THERE IS NO SAFE RUST SPELLING OF A UNION READ. `v.get_unchecked(i).i` and `v[i].i` are BOTH `error[E0133]: access to union field is unsafe`, and `_TWIN_BANNED` forbids `unsafe` in a twin, so no `slb_twin_pay_i` can exist -- this is a fact about the LANGUAGE, not about this pattern's spelling. ⚠⚠ AND THE CONFIGURATION THAT WOULD NOT NEED A TWIN IS THE STRONGER ONE AND THE GATE REFUSES IT: Verus supports `union` NATIVELY, so the same read left in VERIFIED code is checked at the operation (`requirement not met: to access this field, the union must be in the correct variant`) -- but `_scan_unsafe_sites` requires every `unsafe` token to sit inside an `#[verifier::external_body]` body, which is exactly what turns the checked read into an axiom. controls/union_oracle.py runs both configurations with a must-fail arm on each. ⚠ What is NOT unchecked here: the `requires` `v@[i as int] is i` is verified AT EVERY CALL SITE, so the tag/variant agreement is proved; controls/proof_mutants.py arm M1 deletes the tag test and Verus reports `precondition not satisfied`. What the axiom asserts is only that this body reads the member its name says.",
        "pay_o": "Same as pay_i, for the `o: u32` member. `error[E0133]` for every safe spelling; the `requires` `v@[i as int] is o` is checked at every call site; controls/union_oracle.py measures the refused configuration.",
        "pay_d_gt1": "Same as pay_i, for the `d: f64` member, PLUS a second axiom this one alone carries: that the exec comparison `d > 1.0f64` agrees with the spec function `dbl_gt1`. ⚠ At the pinned vstd that link cannot be proved -- `f64` comparison is specified through `partial_cmp`'s existential and its arithmetic through an undischargeable `add_req` (.temp/t148/verus/probe3.rs). A twin would fail on the SECOND axiom even if the union read were safe, so this item is doubly untwinnable and the two reasons are independent. NOTES.md 6c."
      }
    },
    "unsafe_justifications": {
      "verus.rs": {
        "arr_set_unchecked": "`x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for. The `requires` constrains `i`, which is the only parameter the unchecked operation depends on. This is the false positive of the parameter-coverage rule and it is the same one p32 and p38 declare.",
        "pay_set_unchecked": "`x` is a pure VALUE parameter, exactly as for arr_set_unchecked -- a whole `Pay` value moved into the slot. ⚠ Note what is NOT unsafe here: WRITING a union member is safe Rust, so the only unchecked operation in this body is the INDEX, and `i < old(v)@.len()` is the whole of what licenses it. That is why this item, unlike the three readers, HAS a verified twin."
      }
    },
    "items": {
      "verus.rs": {
        "u32_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "nops_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "int_payload": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "arena_byte": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "dbl_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "dbl_gt1": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "pay_int": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "pay_off": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "pay_dbl": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "wf_cell": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "wf_cells": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "step": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "st0": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "run": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "cell_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "buf_get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_buf_get_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "arr_get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_arr_get_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "arr_set_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "slb_twin_arr_set_unchecked": {
          "external": null,
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "pay_set_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "slb_twin_pay_set_unchecked": {
          "external": null,
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "pay_i": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()",
            "v@[i as int] is i"
          ],
          "ensures": [
            "r == pay_int(v@[i as int])"
          ]
        },
        "pay_o": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()",
            "v@[i as int] is o"
          ],
          "ensures": [
            "r == pay_off(v@[i as int])"
          ]
        },
        "pay_d_gt1": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()",
            "v@[i as int] is d"
          ],
          "ensures": [
            "r == dbl_gt1(pay_dbl(v@[i as int]))"
          ]
        },
        "load_input": {
          "external": "verifier::external_body",
          "requires": [],
          "ensures": []
        },
        "emit": {
          "external": "verifier::external_body",
          "requires": [],
          "ensures": []
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()"
          ],
          "ensures": [
            "r == cell_fold(buf@, off as int, len as int)"
          ]
        },
        "main": {
          "external": null,
          "requires": [],
          "ensures": []
        }
      }
    }
  },
  "driver": {
    "statements": 12,
    "c_source": "c/main.c",
    "regions": [
      "safe_naive.rs",
      "safe_tuned.rs",
      "unsafe.rs",
      "verus.rs",
      "c/main.c"
    ],
    "aliases": {
      "c": {
        "n_body": "bytes.len()",
        "bytes": "bytes.as_slice()",
        "inp.n_iters": "n_iters"
      }
    },
    "call_args": {
      "c": {
        "kernel": [
          0,
          2,
          3
        ]
      }
    },
    "canonical": [
      "n_blob = bytes . len ( ) ;",
      "buf = bytes . as_slice ( ) ;",
      "acc = 0 ;",
      "if stride_w >= 4 && stride_w <= n_blob",
      "{",
      "stride = stride_w ;",
      "nwin = n_blob / stride ;",
      "it = 0 ;",
      "while it < n_iters",
      "{",
      "k = acc * nwin >> 64 ;",
      "r = kernel ( buf , k * stride , stride ) ;",
      "acc = acc * 31 + r ;",
      "it = it + 1 ;",
      "}",
      "}"
    ]
  },
  "collapse": {
    "probe_inputs": [
      "small.bin",
      "large.bin"
    ],
    "probe_iters": [
      100,
      200
    ],
    "note": "work_per_call is **bytes of the window** -- `stride`, 52 on small and 244 on large -- which is p27's, p29's, p32's, p38's, p16's, p05's, p11's, p12's, p06's and p14's denominator. marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary, so the one-shot loader terms cancel. ⚠ The estimate is STRICT: it over-counts the 4 window-header bytes, which are decoded as a u32 and are not operations, and under-counts every 2-byte operation, each of which does a modulo, a tag load, a compare chain and a multiply-add. No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per byte applies and what it catches is the failure it exists to catch -- a kernel the optimiser collapsed to nothing."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5 by raw machine-code bytes at `-O3`, and identical up to pc-relative displacement at `-O0`. The proof licenses the unsafe code at zero instruction cost, which is this project's standing R4/R5 result and holds here for the same reason it holds on p32 and p38: there is no vstd call, no pointer write and no allocation in this kernel, so R4 and R5 have nothing to spell differently. ⚠ The pin is also what CHAINS R4 TO THE PROVER, and on p35 that is load-bearing rather than incidental -- it is why the Rust union carries an arena OFFSET where C's carries a POINTER (see idiom.why). At `-O0` the two differ only in pc-relative displacements, which is `norel`; the four twins are `#[cfg(slb_twin)]` and no build compiles them, so they cost zero instructions structurally."
    }
  ],
  "miri": {
    "pair": [
      "unsafe",
      "verus"
    ],
    "sources": [
      "unsafe.rs"
    ],
    "required": true,
    "reason": "Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from here -- and p35 has nine, three of them union reads that no verified twin can check, so the Miri row is the only INDEPENDENT instrument on this pattern's R4 at all. ⚠⚠ What it finds is NOTHING, on every input including the four adversarial ones, and controls/arm_unsafe_bug.rs shows that it finds nothing on the BUGGY ordering either: reading a union member other than the one last stored is NOT undefined behaviour in Rust when the bytes are a valid value of the field's type, and every bit pattern is valid for u32, u64 and f64. **That is the row's detector-coverage result and it is the same shape as the C side's silent arm.**",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed."
  }
}
```

## Reproducing

```sh
python3 patterns/p35-tagged-union/inputs/gen.py     # the .bin files are gitignored
harness/build.py p35
harness/measure.py p35        # ⚠ BEFORE report.py: report.py loads results/p35-*.json first
harness/report.py p35
harness/check.py p35
harness/report.py p35 && harness/check.py p35   # ⚠ stage 9c's one-run lag, on a NEW pattern only
python3 patterns/p35-tagged-union/controls/safety_line.py            # and --selftest
python3 patterns/p35-tagged-union/controls/detectors.py
python3 patterns/p35-tagged-union/controls/union_oracle.py
python3 patterns/p35-tagged-union/controls/proof_mutants.py
python3 patterns/p35-tagged-union/controls/rust_bug.py
```
