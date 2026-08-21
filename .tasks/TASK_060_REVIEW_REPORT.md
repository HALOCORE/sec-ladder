# TASK_060_REVIEW_REPORT — p27, handle table

**Verdict: no blocker.** Every load-bearing number in `patterns/p27-handle-table/NOTES.md`
reproduced, several of them to the last digit, and the two attacks the task file
called blocker candidates both came back clean. **A1 is a strong clean negative:
the twin regime is not circular here and I broke it four ways to prove it.**
**A3 reproduces exactly and is now closed rather than merely consistent.**
Three `major`s and eight `minor`s follow, plus one refuted premise in the task
file itself and one new result (the clang sweep).

Probes, logs and a regenerator for every `.rs` I built: `.temp/p27rev/`
(`gen_review_probes.py`, `fndelta.py`, `noise.py`, `argvlen.py`, `batch.log`,
`sweep-clang.json`, `sweep-clang.log`, `gate-rerun.log`). Binaries deleted;
generators kept. **Nothing under `patterns/`, `.memory/`, `harness/`, `common/`
or `pilot/` was edited, and `git status` is clean** (I backed up
`results/gate/p27-handle-table.json`, re-ran the gate, diffed, and restored it).

---

## A1 — the twin regime. CLEAN NEGATIVE, and it is the strongest one available.

The task's worry: `slb_twin_rec_alloc`'s body **is** `vstd::raw_ptr::allocate`,
so the twin may re-state the axiom instead of re-deriving it. **It does not.** I
weakened the contract four ways — editing the trusted item *and* its twin
together, which is the only way past the gate's signature-identity rule — and
every one is caught, with the shipped configuration staying green throughout:

| mutant (`.temp/p27rev/a1_*.rs`) | shipped cfg | `--cfg slb_twin` |
|---|---|---|
| baseline (`verus.rs` verbatim) | **15 verified, 0 errors** | **20 verified, 0 errors** |
| `rec_alloc`: drop `size != 0` (both sides) | 15 verified, 0 errors | **19 verified, 1 error** |
| `rec_alloc`: `valid_layout(size, align)` → `align != 0` (both sides) | 15 verified, 0 errors | **19 verified, 1 error** |
| `rec_free`: `dealloc@.size() == size` → `>= size` (both sides) | 15 verified, 0 errors | **19 verified, 1 error** |
| `rec_free`: delete `p@.provenance == dealloc@.provenance()` (both sides) | 15 verified, 0 errors | **19 verified, 1 error** |
| `rec_alloc`: drop `size != 0` from the **trusted item only** | 15 verified, 0 errors | 20 verified, 0 errors — *Verus does not catch it* |

The diagnostic names the right site:

```
error: precondition not satisfied
   --> .temp/p27rev/a1_alloc_dropsizene0.rs:475:5
    |
475 |     allocate(size, align)
    |     ^^^^^^^^^^^^^^^^^^^^^
   --> vstd/raw_ptr.rs:915:8
```

`raw_ptr.rs:915` is vstd's `size != 0`. The last row is the important one: a
one-sided weakening verifies 20/0, exactly as `check.py:3513-3521` predicts, and
is caught by the **structural** rule instead — I ran the gate's own comparison
directly and `vparse.norm_clause(twin.sig) == norm_clause(trusted.sig)` is
`True` on the shipped file and `False` on that mutant. **Both legs of the regime
are load-bearing on p27**, and the gate's own per-conjunct vacuity probe already
records 11 of 11 conjuncts across the five twins as load-bearing at 19/1 each —
the same shape my hand-built mutants produce.

**What the twin does establish**: `rec_alloc`'s contract is *no stronger* than
`vstd::raw_ptr::allocate`'s, `rec_free`'s no stronger than `deallocate`'s. That
is a genuine refinement check against a **different** axiom, not the item's own,
so `_TWIN_BANNED` and the "body calls the trusted item" rule are not being
side-stepped — vstd's `allocate` is not in the file's `ext_names`.

**What it does not establish, and what closes it on p27**: the twin cannot see
`rec_alloc`'s *body*, which is a **copy** of vstd's rather than a call, so body
drift is invisible to Verus (TASK_009_REVIEW x4). On this pattern two backstops
actually close it and they should be stated together:
1. both `rec_alloc` and `rec_free` are `#[inline(always)]` and inline into
   `kernel`, and `md5_fn` of `unsafe::kernel` and `verus::kernel` are both
   `87ced1532a93396575bfc00f716f550d` at `-O3 isolated` — so R5's inlined body
   *is* R4's, byte for byte;
2. Miri runs over `unsafe.rs`, which contains that body.
Note the shape: the `identity` pin certifies the two items whose reason for
existing is to make the `identity` pin `exact`. That is not vicious — Miri is
the independent leg — but it is worth saying out loud, because it is the only
place in the tree where the pin and the trusted item justify each other.

**Verdict: A1 does not land. The two extra trusted items are checked, and the
shape is licensed.**

---

## A2 — TCB 7 vs TCB 5. The trade is not p27's to make, and the number checks out.

Confirmed by measurement:
* `r5_vstdpure` verifies **15 verified, 0 errors** and publishes **5**
  `external_body` items (`vparse`: `arr_get_unchecked`, `arr_set_unchecked`,
  `buf_get_unchecked`, `emit`, `load_input`); the shipped file publishes **7**
  and the gate's own `tcb_items` list agrees.
* **The `+130.11` is in the convention it claims.** Whole-program marginal,
  `-O3 isolated`: `verus` 2464.6514 → `r5_vstdpure` 2594.7618 = **+130.1104** on
  `small`; 9140.9250 → 9556.9250 = **+416.0000** on `large`. And it decomposes
  exactly: **−30.0255** (work leaves the `kernel` symbol) **+150.1275**
  (`vstd::raw_ptr::allocate`, now its own symbol) **+10.0085**
  (`vstd::raw_ptr::deallocate`) = +130.1105. NOTES 5d's sign-flip warning is
  correct and its numbers are right.
* NOTES 5a's **unshown half is true**: I built the vstd-pure control at `-O0`
  too, and the pair is `differ` there as well — `md5_raw` **False** and
  `md5_raw_norel` **False** at *both* opt levels, against the shipped pair's
  `norel` at `-O0` and `exact` at `-O3`.

**Arguing it both ways.**

*For 5:* `tcb_items` is a published trust metric; two of p27's seven are pure
measurement apparatus and a reader comparing p01's 3 with p27's 7 is misled.
The relocation argument is only as good as the twin, and the twin proves
contract refinement, not body equivalence (above).

*For 7, and this is decisive:* **the choice is not between two identity levels,
because there is only one.** I read the `identity` pin out of all 18 shipped
`spec.md` files: **18 of 18 pin `O0: norel, O3: exact`.** Shipping
`r5_vstdpure` would make p27 the only pattern in the tree whose R4/R5 pair is
not byte-identical, i.e. the only one that cannot contribute to
`.memory/01-ladder.md` finding 1 — on the kernel where "the proof erases" is
*least* a priori plausible, because p27 carries the largest ghost state in the
project (two tracked `Map`s threaded through two loops with `tracked_remove` in
both). Buying that with two items whose contracts the gate re-derives every run
as no stronger than vstd's, and which cost **zero** in the dimension the pattern
is about (the temporal property costs 0 trusted items in *both* configurations —
`r5_vstdpure`'s five are the same three spatial accessors plus the same two
infra items), is the right trade. The alternative also costs +130.11 / +416.00
Ir/call, which would silently make R5 the dearest Rust rung.

**Verdict: A2 does not land. Ship 7. NOTES 6a's framing is right; the one thing
it under-sells is that `identity: exact` is a project-wide invariant, not a
per-pattern preference.**

---

## A3 — the headline. Verified on the shipped binary, and the decomposition is CLOSED.

### (a) The niche optimisation, on `.temp/build/p27/safe_tuned-O3-isolated`

```
sub    $0x138,%rsp
xorps  %xmm0,%xmm0
movaps %xmm0,0x120(%rsp)  ... movaps %xmm0,0x30(%rsp)      <- 16 x 16B = 256 bytes
```

Sixteen `movaps` covering `0x30..0x12f` — **256 bytes for 32 slots = one pointer
word per slot**, and the fill is zeros, so `None` *is* the null pointer. The
table is addressed `0x30(%rsp,%r14,8)`, stride 8. The CLOSE path is the
pattern's whole sentence in three instructions:

```
mov    0x30(%rsp,%r14,8),%rdi        ; tab[h]
movq   $0x0,0x30(%rsp,%r14,8)        ; tab[h] = None      -- the invalidation
test   %rdi,%rdi                     ; .take().is_some()  -- the asking
```

and the READ path's discriminant test is `test %rcx,%rcx` on the same word.
R4's prologue is **18** `movaps` (256 bytes of `tab` + 32 of `live`), so the
safe rung zeroes 32 fewer bytes per call. ✔ verified.

One precision point: NOTES 0a / README say the safe table is "byte-for-byte the
hardened C rung's `tab[]` minus `live[]`". The **layout** is; the **contents**
are not — after a CLOSE, C's `tab[h]` still holds the dangling pointer and
Rust's holds 0. That difference is the finding, not a counterexample to it.

### (b) The decomposition — reproduced, and shown to be complete

`.temp/p27rev/fndelta.py` parses the whole `callgrind_annotate` table rather
than four needles, so it can answer the question NOTES cannot: *is anything else
moving?* `-O3 isolated`, `small.bin`, marginal 20000 → 40000:

| function | `safe_tuned` | `unsafe` | delta |
|---|---:|---:|---:|
| `kernel` | 1031.1904 | 928.3500 | **+102.8404** |
| `drop_glue::<[Option<Box<u8>>; 32]>` | 120.4218 | — | **+120.4218** |
| `malloc` | 421.1211 | 421.1211 | **0.0000** |
| `free` | 310.2635 | 310.2635 | **0.0000** |
| `_int_malloc` (`libc+0xab170`) | 587.8332 | 587.8332 | 0.0000 |
| `_int_free` (`libc+0xab570`) | 72.9715 | 72.9715 | 0.0000 |
| `std::sys::alloc::unix` | 80.0680 | 80.0680 | 0.0000 |
| `__rust_alloc` / `__rust_dealloc` / `__rust_no_alloc_shim` | 10.0085 ea | 10.0085 ea | 0.0000 |
| **SUM over every function** | | | **223.2621** |
| whole-program | 2687.9135 | 2464.6514 | **223.2621** |

**The sum of the per-function deltas equals the whole-program delta exactly**, so
`+223.2621 = +102.8404 + 120.4218 + 0.0000` is not three cherry-picked terms —
nothing else moved. NOTES 5e is right and can be stated more strongly: the
**entire** allocator stack, not just `malloc`/`free`, is equal to the last digit.
`120.4218 / 223.2621 = 53.94%`, so "54%" is right.

### (c) The mechanism for the other 46%, which NOTES does not give

PROTOCOL asks for the mechanism, and the +102.84 is left as "inside the kernel".
I resolved every call target in the two kernels by GOT relocation + `nm`:

```
safe_tuned::kernel : 5x core::panicking::panic_bounds_check, 2x __rust_dealloc,
                     2x drop_glue, 1x __rust_alloc, 1x handle_alloc_error,
                     1x _Unwind_Resume
unsafe::kernel     : 1x __rust_alloc, 1x __rust_dealloc, 1x __rust_no_alloc_shim,
                     1x indirect, 1x std::process::abort      -- ZERO panic sites
```

Then I built the missing controls (`.temp/p27rev/controls/`, all three print the
shipped checksums on `small` and `large`), kernel-exclusive marginal on `small`:

| | kernel Ir/call | vs shipped R4 |
|---|---:|---:|
| `unsafe` (shipped R4, 3 U-license items) | 928.3500 | — |
| `r4_tabchecked` (pattern's own control) | 969.9715 | +41.6215 |
| **`r4_bufchecked`** (window read checked) | 1040.2407 | **+111.8907** |
| **`r4_allchecked`** (both checked, zero U-license items) | 1081.8622 | **+153.5122** |
| `safe_tuned` (R3) | 1031.1904 | +102.8404 |

The two levers are exactly additive (`111.8907 + 41.6215 = 153.5122`). **So an
R4 that kept the bounds checks R3 keeps costs +153.51, and R3's kernel is +102.84
— i.e. R3's in-kernel excess is entirely the spatial bounds-check tax, and R3
pays 50.67 Ir/call *less* of it than a checked R4 would.** The headline is
therefore stronger than NOTES states: **not one instruction of the R3−R4 gap is
the lifetime guarantee.** It is (i) three trusted items' worth of *spatial*
checks and (ii) an epilogue asymmetry.

I also priced the epilogue asymmetry's own mechanism: in `r2_epilogue` (which
sets every slot to `None` by hand before the drop) `drop_glue` falls from
120.4218 to **100.0000**, so ~100 Ir of the 120.42 is the unconditional 32-slot
walk itself and ~20 is the frees — exactly the `TABCAP`-vs-`ntab` story NOTES 5e
asserts, now measured. (`r2_epilogue` reproduces at **+115.4983**, the published
figure to four decimals.)

**Verdict: A3 does not land. Both halves verified; the decomposition is closed.**

---

## Findings

### major 1 — `verus.rs`'s module doc still carries the claim the pattern retracted, and cites the refutation as its evidence

`patterns/p27-handle-table/verus.rs:37-41`:

> **The table is indexed CHECKED, in this rung and in unsafe.rs**, and that is a
> measured decision rather than a concession: `h < ntab` and `ntab <= TABCAP`
> together already delete rustc's bounds check on `tab[h]`, so a
> `get_unchecked` accessor here would buy zero instructions and cost two trusted
> items. ../NOTES.md 4 has the disassembly and the control.

Every clause is false of the shipped file. The table is indexed **unchecked**
(`verus.rs:689,690,711,719,723,746,750,769,777`); the accessor buys **41.62
Ir/call** (I reproduced it, and resolved the three surviving
`core::panicking::panic_bounds_check` sites by symbol); the two trusted items it
says would be spent *are* spent, and the same doc comment lists them as items 2
and 3 twenty lines above (`verus.rs:19-21`), and again at `verus.rs:340-350`
where the comment says the opposite ("it is here because it is worth 41.70
Ir/call"). And `NOTES.md` §4 is the section that **refutes** the quoted
sentence. `unsafe.rs:13-18` was corrected when the claim was retracted;
`verus.rs` was not.

*Failure scenario:* a reader auditing the TCB from the R5 file alone — which is
the file `spec.md` pins and the one `.memory/04-verus.md` sends people to —
concludes the two array accessors are absent, that p27's trusted base is five,
and that `NOTES.md` §4 supports a claim it demolishes. This is
`.memory/01-ladder.md` finding 14's exact shape ("plausible, written in a comment
as though it had been measured, wrong on the first thing that could check it")
surviving into the shipped rung of the pattern that *documents* finding 14.

### major 2 — an admissible, verifying, byte-identical R4/R5 pair exists that is 6.81 / 10.50 Ir/call cheaper, so "the R4 endpoint is degenerate as far as this task searched" is now false

`NOTES.md` §8: *"the R4 side was searched once (`r4_tabchecked`, which is dearer
and inadmissible) and no admissible cheaper R4 was found, so the R4 endpoint is
**degenerate as far as this task searched**"*. This is p10's blocker verbatim,
and it falls to one deletion. **The epilogue's `arr_set_unchecked(&mut live, j,
0u8)` (`unsafe.rs:200`, `verus.rs:778`) is a dead store** — `live` is a kernel
local and is never read after the epilogue. Deleting it:

```
                        whole small   whole large   kernel small   kernel large
unsafe (shipped)          2464.6514     9140.9230       928.3500      3879.6750
r4_noepiclear             2457.8441     9130.4220       921.5427      3869.1756
                          -6.8073      -10.4994         -6.8073      -10.4994
```

The mechanism is exact: the deleted line is **one store per record still alive
at scope exit**, and `nopen − nclose` per call is 6.75 on `small` and 10.50 on
`large` — so 6.8073/6.75 and 10.4994/10.50, i.e. ≈1.00 instruction per surviving
record.

It is **admissible**, and I checked every leg the gate checks:
* checksums identical to the shipped rungs on **all seven inputs**, benign and
  adversarial;
* **R5 verifies: `15 verified, 0 errors`** — same as the pinned
  `verus.obligations`. The proof needs one change, and it is the ordinary one:
  weaken the epilogue's loop invariant from `wf(..)` over `[0, ntab)` to the same
  two conjuncts over `[j, ntab)`, after which neither `live[j]` nor the ghost
  `lv` needs updating. Source: `.temp/p27rev/controls/r5_noepiclear.rs`.
* **`R4 ≡ R5` `exact` at `-O3 isolated`**: `harness/asm.py diff` reports
  `identical by raw machine-code bytes : True`;
* **in contract**: I extracted every backticked token from the gate's own
  `idiom.required` and counted occurrences in the variant against the shipped
  rungs — **every count is identical**, including
  `arr_set_unchecked(&mut live, h, 0u8);` (the pinned CLOSE-path line, which
  stays) and `while j < ntab {`. No `idiom.forbidden` token appears.

*Failure scenario:* `NOTES.md` §8's fixed-R4 bound `R3ship − R4ship = +223.26 /
+782.25` is quoted as bounding `inf(in-contract R3) − R4ship`. The R4 endpoint is
now known not to be at its infimum, so the pair interval is at least 6.81 / 10.50
wider than the pattern implies, and the sentence a future agent will cite is
false as written. (I have *not* run the full gate on the variant — I cannot
create a pattern directory — so treat "admissible" as "passes every check I could
run outside `check.py`".)

### major 3 — `adversarial-many` is exactly as non-reproducible as `adversarial-noreuse`, and only the latter is disclosed. **This is the wrong premise in the task file.**

`NOTES.md` §7 and §11 and `README.md:51-58` all name `adversarial-noreuse`
alone; TASK_060_REVIEW.md inherits it as *"`adversarial-noreuse`'s **two C
cells** are deliberately non-reproducible across runs, so p27's gate JSON churns
on every run"*. Measured, three runs per cell, all four `(opt, mode)` cells of
both C rungs:

```
adversarial-many  c-gcc  O3-isolated 14140989823541798491 8617323831642039604 10494148422824245386
adversarial-many  c-clang O3-isolated 14642513528799798278 1329542131860295442 14368955144113616576
   ... all 8 C cells, all 24 values distinct
adversarial-uaf   every C cell, every run: 1402190519230396416      <- deterministic, as claimed
```

`adversarial-many` is 24 stale reads in one window; most of them read a chunk
still in the tcache, so like `noreuse` they return glibc's safe-linked `next`
word, which is ASLR-dependent. **The gate already prints this** — the re-run log
shows four notes, not two:

```
note: adversarial-many.bin/c-gcc:     opt/mode variants of this rung disagree (4 distinct behaviours)
note: adversarial-many.bin/c-clang:   opt/mode variants of this rung disagree (4 distinct behaviours)
note: adversarial-noreuse.bin/c-gcc:  opt/mode variants of this rung disagree (4 distinct behaviours)
note: adversarial-noreuse.bin/c-clang:opt/mode variants of this rung disagree (4 distinct behaviours)
```

I re-ran `check.py p27` and diffed the two gate JSONs leaf by leaf:

```
verdict: PASS -> PASS | failures: 0 -> 0 | contract_sha256 unchanged
changed leaves: 31 of 1290
  adversarial 28  (16 stdout values + 12 `cells[]` group-ordering permutations,
                   split 14 / 14 between adversarial-many and adversarial-noreuse)
  sanitizer    3  (the ASan `==<pid>==` in the recorded diagnostic)
```

*Failure scenario:* `NOTES.md` §11 exists precisely so *"a reviewer diffing two
gate runs will see it and should not read it as churn"*. A reviewer told to
expect two cells of one input, who then finds 28 changed leaves across two
inputs plus a permuted group list, has to re-derive the whole thing to decide
whether the tree moved. **Is the churn acceptable?** Yes, and I checked the three
things that could make it not: `--check-stale` hashes `measurement_sources` and
`matrix_inputs` only and never touches stdout (`measure.py:225-262`);
`results/p27-handle-table.json` records checksums for `small.bin` and `large.bin`
only, so the *measurement* record does not churn at all; and `source_sha256`
hashes files, not outputs. The only cost is the gate-JSON diff, and it needs an
accurate scope note.

### minor 1 — `spec.md` and `verus.rs` both still say `rec_alloc` carries vstd's contract "character for character" / "five `ensures` clauses"

`spec.md`'s `verus.unsafe_justifications["verus.rs"]["rec_alloc"]` — the text the
gate shouts every run — says *"the returned pointer is constrained by **five**
`ensures` clauses copied from vstd verbatim"*, and `verus.rs:407-410` says *"its
`requires`, its `ensures` and its body, character for character"*. Three
`ensures` are shipped; the other two were dropped when stage 5c found them not
load-bearing, and `NOTES.md` discloses that in two places. The machine-readable
`verus.items` pin is correct (3 clauses); only the prose is stale. Also
"character for character" is loose about the body: vstd writes
`alloc::alloc::Layout::…` / `::alloc::alloc::alloc`, p27 writes `std::alloc::…`
— same items, different paths.

### minor 2 — `R5 − R4` whole-program on `large` `= +0.0132` does not reproduce; it is a function of the scratch path, not of the code

`NOTES.md` §3b quotes `+0.0132` Ir/call and glosses it *"132 instructions over a
5000-call increment"*. Two problems. (i) The arithmetic: `0.0132 × 5000 = 66`,
not 132. (ii) It does not reproduce. On rebuilt binaries I measure **+0.0020**,
deterministically — three repeats gave byte-identical raw callgrind totals
(`u: 46082384, 91786999`; `v: 46083837, 91788462`). Handing the *same* binaries
the *same* input under a longer scratch path moves both marginals and gives
**+0.0104**:

```
unsafe   argv-short pathlen= 63  marginal=9140.9154     argv-long pathlen=102  marginal=9140.9154
   ...but with the other scratch prefix: unsafe 9140.9230 / verus 9140.9250
```

Mechanism: p27 is the only kernel here that calls `malloc`, so the initial break
— which depends on the size of `argv`/`envp` — decides at which iteration glibc
extends the heap, and that lands in or out of the marginal window. NOTES already
says the figure is "below the resolution of the marginal"; it should say **±0.02
and not a property of the code**, and drop the instruction count. The conclusion
(`R5 ≡ R4`, kernel-exclusive `0.0000` on both inputs — I re-measured, both
kernels 928.3500 / 3879.6750) is untouched.

### minor 3 — NOTES 3d's `c-clang-h` inversion holds only on the padded count and reverses on the unpadded one

`NOTES.md` §3d: *"⚠ `c-clang-h` has one FEWER static instruction than `c-clang`
(146 vs 147, 142 vs 141 unpadded) while executing more"*. I reproduced the whole
table exactly. But the two pairs point opposite ways: `n_fn` 146 < 147 (one
fewer), `n_fn_nopad` **142 > 141** (one *more*). `harness/asm.py`'s own docstring
and `.memory/03-measurement.md` say to prefer the unpadded count, on which the
inversion does not exist. Both numbers are printed, so the table is honest; the
sentence draws the arrow from the convention the project says not to use, over a
one-instruction difference.

### minor 4 — `adversarial-stride3` executes ZERO kernel calls, so "clean on all four benign ones" is three

`stride = 3` and the driver's guard is `stride_w >= 4`, so the loop never runs
and every rung prints 0. `inputs/gen.py:76-78` states this exactly right (*"every
rung prints 0 after ZERO kernel calls"*) and the gate's `proof_domain` records
`"calls": 0, "ensures_checked": 0`. `NOTES.md` §7a's *"clean on all four benign
ones"* is the one place that reads sanitiser evidence into a row where ASan had
no kernel to be clean about. The real ASan evidence is 3 firing / 3 clean.

### minor 5 — NOTES 5c's identity table has three rows and does not say why the fourth is absent

`O3/whole` is missing. The reason is good and should be one line: at `-O3` in
`whole` mode the kernel is inlined into `main` and **there is no `kernel` symbol
at all** — `asm.py syms` finds none in either binary and `asm.py diff --sym
kernel` raises. (NOTES §1's dead-argument table already shows the same effect as
"(inlined away)".) Reviewer checklist: "any cell missing from the table without a
documented reason".

### minor 6 — the +102.84 half of the pattern's most load-bearing number is left unattributed, and the pattern already owns the control that attributes it

`NOTES.md` §3b's ⚠ correctly refuses to call `R3 − R4` a safety number and
attributes 54% of it. The other 46% is labelled only "inside the kernel", which
invites the reading that *that* part is the safety cost. Section A3(c) above
attributes all of it, using `r4_tabchecked` (which the pattern already ships) plus
two one-line siblings.

### minor 7 — `.tasks/TASK_060_REPORT.md` does not exist

TASK_060_REVIEW.md instructs the reviewer to gatekeep *"three candidates named at
the end of the engineer's report"*. There is no such file in `.tasks/`. PROTOCOL
rule 10's own check is **clean** (nothing cites it by path — the only real miss
it reports is `.tasks/TASK_060_REVIEW_REPORT.md`, which this file now is), so
this is not the TASK_027 dangling-citation defect; it is the same cause one step
earlier. I gatekept the candidates I could reconstruct from `NOTES.md` and
`README.md`. TASK_052, TASK_056 and TASK_059 have no report file either.

### minor 8 — gate-JSON churn from ASan PIDs (harness-wide, adjacent work)

`check.py:4575` records the sanitiser diagnostic verbatim, including
`==<pid>==`, so **every** pattern with a firing sanitiser row rewrites one leaf
per row on every gate run — 3 leaves on p27, independent of the adversarial
non-determinism. Stripping `==\d+==` would make the sanitiser block
byte-stable. Reported, not fixed; it is a `harness/` change and I am a reviewer.

---

## New result: the clang sweep, which the engineer named as the first thing to attack

`NOTES.md` §9c: *"**Not measured in this sweep: `c-clang` and `c-clang-h`.** … A
four-fold and twenty-four-fold compiler disagreement on one added conjunct
deserves the band and did not get it."* `sweep_ir.py` already takes `--cells` and
already carries `("c-clang-h", "c-clang", "R1h - R1 (clang)")` in its fit pairs,
so it cost one command over the existing 80 blobs. `.temp/p27rev/sweep-clang.json`:

```
c-clang        nopen= 207.1276  nclose= 10.5693  nread= 23.4968  nrej= 28.9165  const=-116.5077  max|resid| 152.6409  n=80
c-clang-h      nopen= 207.1377  nclose= 10.6064  nread= 24.7203  nrej= 27.9647  const=-116.1939  max|resid| 153.9943  n=80

R1h - R1 (clang)   nopen= 0.0100  nclose= 0.0370  nread= 1.2235  nrej= -0.9519  const= 0.3138  max|resid| 5.9706
R1h - R1 (gcc)     nopen=-0.0601  nclose= 1.8017  nread= 1.9408  nrej= -0.0350  const=-0.6564  max|resid| 6.4487
```

Both fits predict the matrix-input totals inside their own residual:

| | predicted | measured |
|---|---:|---:|
| gcc, `small` | +19.29 | +19.83 |
| gcc, `large` | +91.34 | +91.01 |
| clang, `small` | +6.89 | +4.95 |
| clang, `large` | +1.45 | +3.76 |

**Three things this settles.**
1. **The one term with a listing-level mechanism, `nread`, differs by 1.59×, not
   4× or 24×.** The conjunct costs gcc 1.9408 Ir per READ and clang 1.2235. The
   "4× / 24×" is a property of the two blobs' op mixes, not of the conjunct.
2. **NOTES 9c item 3's hedge is now confirmed by an independent control.** The
   engineer flagged gcc's `1.8017·nclose` as having no mechanism ("gcc's codegen
   shifting elsewhere in the function"). Clang's is **0.0370** — the same source
   change costs clang nothing on CLOSE. On `large` that term alone is
   `21.5 × 1.8017 = +38.7` of gcc's +91.
3. **Clang's `nrej = −0.9519` is what collapses its `large` total.** With 37.39
   rejected ops per call the hardened clang build *saves* ~35.6 Ir/call on the
   reject path, which is why more work gives a *smaller* hardening cost
   (+3.76 on `large` vs +4.95 on `small`) — the paradox NOTES flags and does not
   explain.
Level residuals are 152.6 / 154.0 on levels of 6000–10000, i.e. the same ~2% as
the four cells NOTES swept, so §9a's "2% is not a law" reproduces on two more.

---

## Clean negatives — every attack I ran, with its outcome

1. **A1, weaken `rec_alloc`'s `requires` (drop `size != 0`, both sides)** — caught: 19/1 at the twin's `allocate` call; shipped 15/0.
2. **A1, weaken `valid_layout(size, align)` → `align != 0` (both sides)** — caught: 19/1.
3. **A1, weaken `rec_free`'s `dealloc@.size() == size` → `>=` (both sides)** — caught: 19/1.
4. **A1, delete `rec_free`'s provenance conjunct (both sides)** — caught: 19/1.
5. **A1, weaken the trusted item only** — Verus does *not* catch it (20/0), and the gate's signature-identity rule does (`norm_clause` differs). Both legs load-bearing.
6. **A1, is the twin re-stating the axiom?** No — vstd's `allocate` is not in the file's `external_body` set, so the "body calls the trusted item" rule is not being dodged; and the gate's own vacuity probe records 11/11 conjuncts load-bearing across five twins.
7. **A1, does anything cover `rec_alloc`'s *body*?** Yes, uniquely on p27: `#[inline(always)]` + `md5_fn(unsafe::kernel) == md5_fn(verus::kernel) == 87ced153…`, plus Miri over `unsafe.rs`.
8. **A3, niche optimisation on the shipped binary** — verified: 16 `movaps` = 256 B / 32 slots, stride 8, `None` = `movq $0x0`, `is_some()` = `test %rdi,%rdi`.
9. **A3, is the decomposition complete?** Yes — the sum of *every* per-function delta equals the whole-program delta, 223.2621. `malloc`, `free`, `_int_malloc`, `_int_free`, the `unix` shim and all three `__rust_*` symbols are equal to the last digit.
10. **A2, is `+130.11` whole-program?** Yes: 2594.7618 − 2464.6514 = 130.1104; `large` +416.0000. Decomposes as −30.0255 + 150.1275 + 10.0085.
11. **A2, does `r5_vstdpure` really publish 5?** Yes — `vparse` counts 5 `external_body` items against the shipped 7, and the gate's `tcb_items` agrees.
12. **NOTES 5a's unmeasured half: is the vstd-pure pair `differ` at `-O0` too?** Yes — built it; `md5_raw` False *and* `md5_raw_norel` False at both levels. Shipped pair: `norel` / `exact`, as pinned.
13. **§4's "three `panic_bounds_check` sites survive"** — verified by *symbol*, not by call count: `r4_tabchecked`'s kernel has three `call *…(%rip)` through GOT `0x56dc0`, whose `R_X86_64_RELATIVE` addend `0x50eef` is `core::panicking::panic_bounds_check`. Shipped `unsafe` kernel: zero. Cost reproduces at +41.6215 / +165.6456.
14. **§8's `r3_issome` ≡ `safe_naive`** — to the last digit: kernel 1040.7062 both, whole 2697.4293 both. Shipped R3 cheaper by 9.5158 / 32.0000.
15. **§5e's `r2_epilogue` bracket** — +115.4983 on `small`, the published figure to four decimals.
16. **§3b's `R1h − R1`** — +19.8267 / +91.0132 (gcc) and +4.9532 / +3.7578 (clang), all four reproduce.
17. **§3's kernel-exclusive table** — all 16 numbers reproduce exactly from `results/p27-handle-table.json`.
18. **§3d's panic-pad table** — all eight rows reproduce exactly; `bulk_calls` empty on all eight kernels.
19. **Is the bug temporal or logical?** Temporal, proven: ASan reports `heap-use-after-free`, *"0 bytes inside of 1-byte region [0x502000000010,0x502000000011)"*, shadow byte **`fd` = Freed heap region**, freed at `c/kernel.c:92` (`free(tab[h])`), allocated at `:79` (`malloc(RECSZ)`), read at `:104`. The address is inside **no live allocation**. Not p17's class.
20. **Is R1 vs R1h one program and its guard?** Yes — comment-stripped, the two C files are 69 lines each and differ in **exactly one**: `if (h < ntab)` → `if (h < ntab && live[h] == 1)`.
21. **§7's determinism claims** — `adversarial-uaf` = 1402190519230396416 on gcc *and* clang, all four cells, three runs each; the six checked rungs all print 4295919549966416896 / 3390747988282288128. Reproduced.
22. **Is R2 a straw man?** No. `safe_naive` is `is_some()` + `unwrap()` and `is_some()` + `= None` — the honest naive spelling — and `R2 − R3` is 9.52 / 32.00, i.e. 0.35% / 0.32% of the level. It also documents its own bounds checks (`safe_naive.rs:22-24`).
23. **Is `model.py` independent?** Yes — two implementations in one file (an `Optional[int]` simulation and an iterative `op_fold` mirroring the Verus `run`), no `subprocess`, no import of any rung.
24. **Is the driver loop really identical across rungs?** Yes — gate `driver_loops`: 12 statements, `matches_pin: true`, for all five sources.
25. **The direction test, verified byte-exactly.** Reconstructing the pre-build contract block from the *two disclosed edits alone* — restore `rec_alloc`/`slb_twin_rec_alloc`'s two `ensures` in vstd's positions, restore `rec_free`/`slb_twin_rec_free`'s six `requires` to the destructured `dealloc.`/`pt.` spelling — and re-serialising with `json.dumps(indent=2)` reproduces **`b1f2dbb3e48542af…`** exactly. Neither edit alone does (`6d176cdf…`, `26a8ef39…`). So **no `required` or `forbidden` entry moved, and neither did `obligations`, `twin_obligations`, `identity`, `miri`, the `note` or the `why`** — the engineer's claim is now byte-provable rather than asserted. Both edits are weakenings of a trusted contract (fewer `ensures`) or make more conjuncts judgeable, and the gate's `requires_strength` record confirms all six `rec_free` conjuncts are now judged ("not a tautology"). **Direction: toward a stricter gate, as claimed.**
26. **Does the gate reproduce?** Yes — PASS, 0 failures, `contract_sha256` unchanged, 31 of 1290 leaves changed and every one of the 31 is the adversarial/sanitiser non-determinism.
27. **Is `identity: exact` a free choice?** No — 18 of 18 shipped `spec.md` files pin `O0: norel, O3: exact`.
28. **Is the whole-program marginal otherwise stable?** Yes — three repeats gave byte-identical raw callgrind totals; the only instability is the scratch-path effect in minor 2.

---

## Premises in the task file that are wrong

1. **"`adversarial-noreuse`'s two C cells are deliberately non-reproducible across
   runs, so p27's gate JSON churns on every run."** Two *inputs*, not one:
   `adversarial-many` is equally non-reproducible (24 of 24 measured values
   distinct across 8 C cells × 3 runs), and the churn is **28 leaves**, split
   14/14, plus 3 more from ASan PIDs. The task inherited the scope from
   `NOTES.md` §11 without re-measuring — the same mechanism PROTOCOL rule 9 was
   written for. **This is the "one more error of that kind" the task predicted.**
2. **PROTOCOL rule miscited, twice.** A3 and the "Also in scope" list both say
   *"the mechanism question (PROTOCOL rule 11)"*. Rule 11 is "Never `git add -A`
   while a subagent is working"; the mechanism rule is **rule 12**. Worth fixing
   given commit `d653fa4` ("the reciprocal numbering warning, in the file being
   miscited").
3. **A2's framing** — *"p27 chose the LARGER TCB … is it gaming in the other
   direction?"* — presupposes a choice p27 does not have. See A2: 18 of 18
   patterns pin `O3: exact`, so the alternative is not "5 instead of 7" but "p27
   leaves the ladder's central result".

## Not done / unsure

* **I could not run `check.py` on the cheaper R4/R5 pair**, because that needs a
  directory under `patterns/`. "Admissible" in major 2 means: verifies 15/0,
  byte-identical at `-O3`, checksums match on all seven inputs, every
  `idiom.required` token present at the shipped count, no `idiom.forbidden`
  token. It has not been through stages 2, 4, 5c, 7 or 8.
* **No `ns` work.** `controls/clayout.py` is still unrun; `NOTES.md` §3c's
  refusal to publish a wall-clock claim stands and I did not test it.
* **The R2 side is still unsearched for a *cheaper* R2.** I checked only that R2
  is not pessimised (clean negative 22). A genuinely cheaper in-contract R2 would
  be R3, so I judged the search uninteresting; if the manager disagrees, say so.
* **I did not sweep `safe_naive`, `verus` or any `whole`-mode cell.** The clang
  sweep is `-O3 isolated` only, matching `sweep_ir.py`'s defaults and the four
  cells NOTES swept.
* **I did not re-derive the tcache hit/miss split of §9b.** I reproduced the
  claim's shape only through the level residuals.
* **`.temp/build/p27` was rebuilt and then deleted again**, so re-running any of
  my numbers needs `harness/build.py p27` and
  `sh patterns/p27-handle-table/controls/build_controls.sh <dir>` first, plus
  `python3 .temp/p27rev/gen_review_probes.py` for my four extra rungs.

## Memory updates

None — reviewers do not write `.memory/`. What I believe is ready for it, after
the manager applies the corrections above: **the epilogue-asymmetry decomposition
(closed, `223.2621 = 102.8404 + 120.4218 + 0.0000`, nothing else moved)**; **the
twin-regime result (a twin whose body is another crate's `external_body` API is a
valid strength oracle, measured four ways, and the signature rule carries the
one-sided case)**; and **the `identity`-vs-TCB tension, stated with the 18-of-18
fact that makes it a non-choice**. The `R5 − R4` `large` `+0.0132` should **not**
go in — it is a scratch-path artefact.
