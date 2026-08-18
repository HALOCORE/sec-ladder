# TASK_014_REVIEW — report

**The one line asked for.** Finding 7 should say: *on glibc 2.39/x86-64 `memcpy`
**is** `memmove` — one address, for the plain **and** the `_chk` pair — so p08's
UB executes on every `adversarial-overlap` call and is unobservable (R1 ≡ R1h,
0.00 Ir/call, same checksum in all 32 builds); the only tools that see it are
ASan on an **unfortified** build and Miri on the Rust mutant, and
`_FORTIFY_SOURCE` blinds ASan under **gcc and clang alike** by rewriting the call
to `__memcpy_chk`.* It must **not** say that R5 rules the bug out (swapping the
trusted body to `copy_nonoverlapping` gives `11 verified, 0 errors`), that
"memmove is free" (0.00 is a libc aliasing property, not a cost), or that p08
"restores the R3-free streak" — p05's break of that streak is itself refuted
below.

**Ordering note.** Part 3 and Part 4 were run first as instructed. Part 4's
suspected blast radius **does not exist** (clean negative, §7). Part 3's
suspicion that p08 undermines p05 **is wrong, and I have the disassembly** — but
chasing it turned up a *different* and larger problem with the same finding, and
that is blocker 1.

---

## Blocker

### B1 — p05's headline is refuted by a third safe spelling: `chunks_exact` is **cheaper than the unsafe rung**

`.memory/01-ladder.md:439-513` (finding 6, the task's "finding 12") and
`patterns/p05-index-flatten/NOTES.md:19-36` claim

> "**R3 is *not* free here.** +16.7% at 496×8, +4.7% at shipped `large` — an
> `O(nrow)` cost. **The 'R3 free' streak ends at five patterns, not six.**"
> … "**The `29 + 3r` Ir per row is the price of the optimiser failing the lemma
> the proof proves.**"

Both are false. p05's R3 replaced by one idiomatic safe expression —
`data.chunks_exact(ncol)`, a spelling `.memory/01-ladder.md:11` **names in the R3
definition itself** — is *negative* cost against R4. Zero `unsafe`, no proof, no
lemma.

Source: `.temp/review014/p05lin/safe_tuned_chunks.rs` (p05's `safe_tuned.rs`,
one substitution). Marginal Ir/call, `-O3 isolated`, my own callgrind, n_iters
100→200:

| input (nrow×ncol) | R2 | R3 shipped | **R4 unsafe** | **chunks_exact** | chunks − R4 |
|---|---:|---:|---:|---:|---:|
| `small` 19×26 | 2081.00 | 1504.00 | **1381.00** | **1369.00** | **−12.00** |
| `large` 65×61 | 11330.70 | 8834.70 | **8435.70** | **8377.70** | **−58.00** |
| `sweep-r19c24` (≡0 mod 8) | 2784.30 | 1276.30 | 1153.30 | 1141.30 | −12.00 |
| `sweep-r19c25` | 1929.30 | 1409.30 | 1286.30 | 1274.30 | −12.00 |
| `sweep-r41c32` | 6359.41 | 3135.41 | 2880.41 | 2846.41 | −34.00 |
| `sweep-r65c64` | 12891.00 | 7795.00 | 7396.00 | 7338.00 | −58.00 |
| `sweep-r65c65` | 9966.30 | 8250.30 | 7851.30 | 7793.30 | −58.00 |

`chunks − R4 = −(nrow − 7)` **exactly**, on every point, both residue classes —
safe Rust is **one instruction per row cheaper than unsafe Rust**. R3 − R4 is
`6·nrow + 9` (123 / 255 / 399 at nrow 19 / 41 / 65), so `chunks_exact` removes
100% of R3's `O(nrow)` cost and then some.

Equivalence: **identical stdout and exit code against R4 on all 150 committed
p05 inputs** (`small`, `large`, 4 adversarial, 144 sweep). Wall clock, `large`,
15 interleaved reps, `taskset -c 3`, differenced n_iters 12000→36000: R2 +31.2%,
R3 +2.22%, chunks +1.78% vs R4 — chunks is not paying in time either.

**The mechanism**, from the listing (`harness/asm.py show`): `chunks_exact` hands
each row a slice whose length **is** `ncol` by construction, so

- the vector/scalar split (`ncol & 7`, `ncol − (ncol&7)`) is computed **once per
  call**, not once per row — there is no `cmov` anywhere in the kernel, against
  five in R2;
- the scalar epilogue is `movzbl / add / inc / cmp / jne`, R4's **unchecked**
  5-instruction body, not R2's checked 8;
- no `cmp $0x9` vector guard and no `movl $8 ; cmove` forcing a zero remainder to
  a full vector width — the two mechanisms `.memory/01-ladder.md:465-470`
  attributes the `f(0)=84` peak to;
- 105 static instructions against R2's 171 and R4's 97.

**Failure scenario.** The writeup states "safe Rust pays an O(nrow) tax on a
vectorised 2-D index, and that tax is the price of a lemma only a verifier can
prove." A reader spends ten minutes writing `chunks_exact` and beats the unsafe
rung. This is the *third* time this project has priced a spelling and called it
a safety cost — p02 (lost `memcpy` idiom, retracted) and p16 ("only the naive
indexed spelling is O(n)") are the precedents, and `.memory/01-ladder.md:116`
already carries the rule that was violated: *"Never publish a safety-cost claim
without R3."* The rule needs a corollary: **without the *best* R3.**

What must change: p05's `NOTES.md` headline and `.memory/01-ladder.md` finding 6.
The `1.375000` steady-state number, the `29 + 3r` per-row model for R2, the AVX2
result and the `f(0)=84` mechanism all survive as descriptions of **R2 and of
p05's shipped R3**; what does not survive is "safe Rust pays this" and "this is
the price of the missing lemma".

---

## Major

### M1 — `README.md:31` claims Verus rules the bug out. It does not, and the measurement is one substitution

`patterns/p08-overlap-move/README.md:26-31`, the "full arc" table, under the
column *"can it express the bug?"*:

| Verus | the bug is not even *expressible* in the spec logic | — |

Measured. `verus.rs:242-244`, `core::ptr::copy` → `core::ptr::copy_nonoverlapping`,
nothing else touched (`.temp/review014/verus/nonovl.rs`):

```
$ ./verus_run.py .temp/review014/verus/nonovl.rs
verification results:: 11 verified, 0 errors
$ ./verus_run.py .temp/review014/verus/nonovl.rs --cfg slb_twin
verification results:: 15 verified, 0 errors
```

The bug is not only expressible at R5, it is **invisible to the verifier, to the
verified twin, to the `spec.md` contract pin, and to gate stages 5c/5c-req**
(the contract is textually unchanged). Step 2 passes too, because on this libc
the mutant prints the right answer. What would catch it is the `O3` identity pin
against R4 (`memcpy` vs `memmove` call target) and Miri — and Miri's
`miri.sources` is `["unsafe.rs"]` (`spec.md:393`), i.e. not R5.

`NOTES.md:965-969` (SLB-TRUSTED-ARGUMENT (b)) says the correct thing —
*"Swapping the body for `copy_nonoverlapping` would make the contract unsound
with no textual change to it"*. So the README's front-page table contradicts the
pattern's own NOTES on the pattern's central claim. The task file inherited the
same error (*"ruled out by a `requires` at R5"*) — there is no non-overlap
`requires`, and there cannot be one, because `ptr::copy` legitimately permits
overlap.

### M2 — the three-clause trusted `ensures` does **not** partition the buffer, and the `&mut [u8]` widening cost exactly that

`verus.rs:233-241`; the claim is `NOTES.md:955-958`:

> "The postcondition names `[dr, m)`, `[0, dr)` and `[m, old(v)@.len())`, which
> together are **every index of the slice**, so there is no index whose final
> value the contract leaves unconstrained."

The three regions partition `old(v)@.len()`. Nothing pins `final(v)@.len()`.
Measured with a caller holding a genuine `&mut [u8]`
(`.temp/review014/verus/lentest.rs`):

```
error: assertion failed
  --> lentest.rs:20:12
   |
20 |     assert(v@.len() == n);      // <-- does the 3-clause contract give this?
verification results:: 1 verified, 1 errors
```

The same file with the **array** signature the engineer abandoned
(`&mut [u8; SCR]`, `.temp/review014/verus/lentest_arr.rs`) gives `3 verified, 0
errors` — the length comes free from the type.

So `NOTES.md:696-710`'s conclusion is backwards. It says widening to `&mut [u8]`
*"is a fix rather than a workaround because the slice contract is the more
general one"*. The generality is exactly what loses the fact: the array contract
carries the length, the slice contract does not, and p08's kernel only verifies
because its single call site passes `&mut scr` with `scr: [u8; SCR]`. **The
trusted item's contract is complete only relative to one caller.**

*Concrete failure scenario, and it is the project's stated practice:* the next
pattern that wraps a bulk-memory primitive clones `move_right`'s contract (p08 is
being written up as the template for the multi-clause case) for a caller that
holds a real `&mut [u8]` — a subslice, a `Vec` — and the kernel's `=~=` step
fails with no diagnostic pointing at the missing length. The natural repair is
the fourth clause, and gate stage 5c will delete it again.

Note what this is **not**: I could not construct a wrong trusted *body* that the
three-clause contract admits and the four would catch — Rust has no way to change
a `&mut [u8]`'s length from inside the callee, so clause 4 is unfalsifiable and
5c's "not load-bearing" verdict is right on its own ground. The defect is the
NOTES claim of completeness, not the deletion.

### M3 — the committed gate record carries no trace of the sanitiser blindness

`results/gate/p08-overlap-move.json` records

```
adversarial-overlap.bin   expect=clean  fired=False  exit=0  diagnostic=""
```

with `"notes": []`, `"blocked": []`, and no `loud` entry on the subject (the three
`loud` entries are all `clause-mut` `forall` warnings). `results/` is the
published artefact. Read from there, p08's row is **indistinguishable from
p17's `adversarial-leak`**, which is genuinely ASan-clean because the read is in
bounds — and that distinction is the whole difference between "memory-safe and
wrong" and "UB the tool could not see". The reason lives only in `model.py:290`'s
docstring, which no consumer of `results/` reads.

I do **not** rank the `sanitizer_expect = "clean"` decision itself as a defect —
see §"Part 1 adjudication". This is about the record, and the fix is one
`rep.loud(...)` or a `notes` entry, not a policy change.

---

## Minor

### m1 — over-precision in the `Ir`/ns direction disagreement

`NOTES.md:432-435`: *"wall clock says c-gcc (452.75 ns) is **2.9% dearer** than
c-clang (440.01 ns)"*. My independent interleaved re-measurement (21 reps,
`taskset -c 3`, differenced n_iters 25 000→75 000, `small`):

```
c-gcc   448.16 ns/call   c-clang 442.44 ns/call   -> gcc +1.29%
R4      442.76           R5      444.40           -> noise floor +0.37%
```

The **direction reproduces** (gcc dearer in ns, 33.3% cheaper in Ir) and 1.29% is
3.5× my floor, so the finding stands. The magnitude is 2.2× overstated. Quote a
band or quote the floor beside it.

### m2 — four dangling section cross-references

- `verus.rs:39`, `:49`, `:76` all say "NOTES.md 4"; §4 is *"Wall clock, and the
  memset's share"*. The intended targets are §6a (the clause-count decision) and
  §8 (the TCB tally).
- `model.py:257` says "NOTES.md 7 reports the measured margin" for the `Ir`
  floor; §7 is the manifestation table, the floor is §9.
- Adjacent, as the task flagged: `patterns/p05-index-flatten/NOTES.md:13`
  references §12; that file's last section is §11. Confirmed dangling.

### m3 — the finding numbering the task uses does not exist

`.memory/01-ladder.md` numbers its structural findings **1–6**; p05 is finding
**6**, and p08 would be **7**. `TASK_014_REVIEW.md:6,79,89` say "finding 12" and
`RECAP.md:32,138` say "finding 9" / "finding 10". Whatever numbering those refer
to is not in the file. Land finding 7 and fix the references in the same commit,
or the next agent will grep for finding 12 and find p05 under a different number.

---

## Part 3 adjudication — finding 12 is **not** refuted by p08, and here is the disassembly

**The 26.00 is real.** Reproduced independently (my own callgrind, n_iters
100→200): `small` R3 7334.22 − R4 7308.22 = **26.00**; `large` 29079.56 −
29053.56 = **26.00**. Flat in `m` and in bytes moved, as claimed. Every other
number in NOTES §2b/§3b reproduced to ±0.06 Ir, and `R1h − R1 = 0.00` in all four
C cells on both bands.

**The retained check is genuinely linear.** From the listing, not the prose. The
`for r in 0..nrep` loop is **fully unrolled into four `memmove` call sites** in
both R3 and R4 (`asm.py stat` → 4 × `memmove@GLIBC_2.2.5`), and each R3 site
carries six instructions R4 does not:

```
mov  %rbx,%rdx        # rdx = m
sub  %rbp,%rdx        # rdx = m - dr        (the count)
cmp  $0x1000,%rdx     # count > SCR ?  -> slice_end_index_len_fail
ja   ...
mov  $0x1000,%eax
sub  %edx,%eax        # eax = SCR - count
cmp  %eax,%ebp        # dr > SCR - count ?  -> "dest is out of bounds"
ja   ...
```

4 rounds × 6 = 24, +2 from register-pressure differences = 26.00. Both tests are
`dr + (m − dr) = m <= SCR` rearranged: **linear**, and dead given the kernel's
guard `d + nrep <= m` and `m = min(avail, SCR)`.

**But the blocker is not linearity, and it is not "LLVM never eliminates dead
checks" either** — `.temp/review014/lin/probe3.rs`, four ten-line functions,
`rustc -C opt-level=3 -C debug-assertions=off`:

| function | panic refs | insns |
|---|---:|---:|
| `p08_shipped` — guard `d+nrep<=m` outside, `dr = d+r` inside | **3** | 60 |
| `p08_local` — same, relation **restated inside the loop** | **0** | 47 |
| `p08_reslice` — `scr[..m].copy_within(..)` | 1 | 52 |
| `p08_unsafe` — `ptr::copy` | 0 | 92 |

Restating the relation locally deletes the check outright. So p08's blocker is a
**relational deduction over `{d, nrep, m, r}` across the loop induction
variable** — LLVM's value-range machinery is per-value, not relational — which is
a *different* blocker from p05's, not a counterexample to it.

**And p05's blocker really is the nonlinearity, when nothing else interferes.**
`.temp/review014/lin/probe2.rs` compiles p05's kernel verbatim (`e_p05`) and
reproduces TASK_013_REVIEW's mechanism exactly and independently: the
22-instruction per-row `cmova`/`cmovb` min-max chain, the `cmpq $9` vector guard
against R4's `>= 8`, the `movl $8,%r10d ; cmoveq` that forces a zero remainder to
a full vector width, and a **live** `cmpq %rsi,%rdi ; jae panic_bounds_check` in
the scalar epilogue. The same kernel with **only the guard's arithmetic
linearised** (`f_p05_lin`: running `base`, per-row `base.checked_add(ncol) <=
buf.len()`) compiles to **zero `cmov`, no `cmp $9`, no residue `cmove`, and an
unchecked 5-instruction epilogue** — 166 → 125 instructions, 5 → 4 panic refs
(the 4 are the header decode). That is the counterfactual the manager asked for,
and it goes the manager's way.

**Two caveats, both measured.** (i) That counterfactual does **not** survive the
shipped binary configuration: built as a full p05 cell
(`.temp/review014/p05lin/safe_naive_lin.rs`, same rustc flags as `build.py`),
LLVM's induction-variable simplification re-derives `i*ncol` (an `imul` per row),
the whole chain returns, and the linearised R2 measures **2366.00 Ir/call against
R2's 2081.00** — *worse*. Same checksum. So "linearise the guard and the cost
goes away" is true of the kernel in isolation and false of the shipped build.
(ii) B1 makes the question moot: a spelling with no lemma at all beats R4.

**Verdict.** Finding 12 survives as a statement about the *obligation*; it must
not survive as a general law; and its cost half is refuted by B1. Proposed
replacement for `.memory/01-ladder.md:493-504`:

> **Why the check cannot be eliminated — and what that is worth.** R2's panic is
> dead on every execution, and LLVM keeps it: `nrow*ncol <= avail ⟹ i*ncol + j <
> avail` is nonlinear, which is exactly the obligation R5 discharges with
> `lemma_mul_inequality` and one `by (nonlinear_arith)`. Linearising that guard
> in an isolated compilation deletes the entire per-row apparatus
> (TASK_014_REVIEW), so nonlinearity is the blocker *for this kernel*. It is
> **not necessary in general**: p08 keeps a provably-dead `copy_within` range
> check whose implication is purely linear, at 26.00 Ir/call, because the fact
> needed is *relational* rather than nonlinear. **And the cost is not intrinsic
> to safe Rust.** `data.chunks_exact(ncol)` — zero `unsafe`, no proof — is
> `nrow − 7` instructions per call **cheaper than R4** on every p05 input. What
> the `29 + 3r` per row prices is the *indexed and the manually-resliced
> spelling*, not the missing lemma.

**Decisive experiment, if the two ever need reconciling from scratch:** build the
linearised guard as a real p05 cell *and* defeat IndVarSimplify's
re-derivation (carry the row base in a slice that is consumed, i.e. `split_at`
or `chunks_exact`, so there is no `i*ncol` for it to reconstruct), then sweep
`ncol` over two full residue cycles. `chunks_exact` is that experiment and it has
now been run.

---

## Part 4 adjudication — the counting behaviour is real, the blast radius is empty

**Verified directly**, `.temp/review014/rep/rep.c`, gcc `-O2`, marginal Ir/call
(callgrind at n=200 minus n=100, over 100):

| body, 4096 bytes | marginal Ir | Ir/byte |
|---|---:|---:|
| `rep stosb` | **4110.00** | **1.0034** |
| `rep stosq` (512 iterations) | 527.00 | 0.1287 |
| `rep movsb` | 4106.00 | 1.0025 |
| explicit `volatile` byte loop | 10252.00 | 2.503 |
| empty | 5.00 | — |

Callgrind counts a `rep`-string instruction **once per repetition**, exactly as
`NOTES.md:420` says. gcc's inlined `rep stos %rax` at 0.126 Ir/byte and glibc's
`rep stosb` at 1.006 are both explained by this one rule.

**Blast radius — nothing is contaminated.** Two independent checks.

1. *Explicit `rep` in a measured kernel.* Scanned every `-O3` build of every
   pattern, symbol `kernel` **and** symbol `main` (`harness/asm.py`): the only
   hits in the whole tree are p08's four gcc cells (`rep stos %rax`,
   `rep movsq`). p01, p02, p05, p16, p17 have none.
2. *`rep` reached through libc.* Only p02 and p08 call a bulk routine from the
   measured kernel at all (p01/p05/p16/p17 call nothing). glibc's thresholds,
   measured (`.temp/review014/rep/glibc.c`, marginal Ir/call vs size):

   | size | `memcpy`/`memmove` Ir/byte | `memset` Ir/byte |
   |---:|---:|---:|
   | 2044 / 2048 | 0.1140 / 0.1138 | 0.0700 / 0.0698 |
   | 3072 | 0.1071 | **1.0107** ← `rep stosb` |
   | **4092** | **0.1039** | 1.0081 |
   | 8192 | 0.0988 | 1.0040 |
   | 16384 | **0.9989** ← `rep movsb` | 1.0020 |

   p02's two sizes are **61 B (26.00 Ir) and 4092 B (425.00 Ir)** — squarely on
   the vector path, four thousand bytes below the `rep movsb` threshold. p02's
   `Ir` comparisons are clean.

So the suspected blocker does not exist. p08's own `rep` exposure is confined to
its gcc cells and is documented in §4a with both currencies.

---

## Part 1 adjudication — the isolation reproduces, and it is stronger than reported

Four ASan+UBSan builds of p08's C rung, stage 7's exact flags plus one change
each (`.temp/review014/san/`), run on `adversarial-overlap.bin`:

| build | the move lowers to | result |
|---|---|---|
| gcc, default (`_FORTIFY_SOURCE=3`) — **the gate's build** | `__memcpy_chk@plt` | **silent, exit 0** |
| gcc `-D_FORTIFY_SOURCE=0` | `__interceptor_memcpy` | `memcpy-param-overlap`, exit 1 |
| clang, default (no fortify) | `__asan_memcpy` | `memcpy-param-overlap`, exit 1 |
| **clang `-D_FORTIFY_SOURCE=3`** | `__memcpy_chk@plt` | **silent, exit 0** |

The fourth row is mine and it closes the attribution: the discriminator is
`__memcpy_chk`, **not gcc**. "gcc is fortified and clang is not" is the local
cause; "fortification hides overlap from ASan" is the transferable one, and it is
the sentence a reader needs.

**Is `"clean"` right?** Yes, and I tried to break it. The alternatives:
`"fires"` makes the gate red on an *environment* property, which is how gates get
switched off (`check.py:3643` says so in its own docstring); a documented blocked
row is not available — `check.py:566` accepts only `"clean"` or `"fires"`, so
p08 would have needed a `harness/` change the task forbade, and the engineer did
the right thing by reporting it instead. `"clean"` is also *true of the build the
gate makes*, and the predicate that would drive the honest value is computed and
kept (`model.py:278-289`, `any_overlap`) so the flip is one line when stage 7
grows a clang column. My only complaint is M3: the record does not carry the
caveat.

**Generalisation — p02 is not blind.** Calls inside the `kernel` symbol of each
pattern's stage-7 binary (`.temp/build/pNN/c-gcc-asan`):

| pattern | `mem*`/`str*` in the kernel |
|---|---|
| **p02** | **`__interceptor_memcpy`** — intercepted, and ASan fires on 3 of its inputs |
| **p08** | `__memcpy_chk@plt` (the move) + `__interceptor_memcpy` + `__interceptor_memset` |
| p01, p05, p16, p17 | none at all |

p02 escapes because its destination is a bare `uint8_t *dst` parameter
(`p02/c/kernel.c:22`) with no computable `__builtin_dynamic_object_size`; p08 is
caught because its destination is `scr + dr` on a fixed 4096-byte local. **No
existing published sanitiser row is blind.**

---

## Part 2 — does p08 still support the claim it was commissioned for?

Mostly yes, with M1 as the exception.

- The *"UB is real and a tool sees it"* vs *"the program computes the wrong
  answer"* distinction is held consistently in `NOTES.md` §1c, §5d and §7 —
  §7's four-pattern comparison table ("p08 | overlapping memcpy | **nothing. The
  right answer, everywhere.**") is the clearest statement of it in the project.
  §5c is the honest counterweight and it reproduces exactly (below). Where it
  slips is `README.md:31` — M1.
- **R1 vs R1h = 0.00 is written as a libc property**, not as "memmove is free":
  `NOTES.md:161-164` says *"because the callee is the same function … a property
  of glibc rather than of the ladder"*. This is **not** the p02 mistake in a new
  costume; clean negative. I did find one gap and closed it: §1b measured
  `dlsym("memcpy") == dlsym("memmove")`, but the **gcc cells call the `_chk`
  forms**, which were never checked. They alias too —
  `__memcpy_chk == __memmove_chk == libc+0x198910` (`.temp/review014/rep/which.c`)
  — so the mechanism covers all four C cells.
- **Is p08 carrying its weight?** Yes, but as a *tooling and expressiveness*
  result, not a performance one. Its performance content is one number (26.00
  Ir/call, 0.09%) and a null (0.00). Its real content is: the compile-time
  rejection with rustc's own `split_at_mut` suggestion; the first multi-clause
  trusted contract; the first demonstration that the twin's unique catch is real;
  the fortify-blinds-ASan mechanism; and a *negative* manifestation table that is
  worth as much as p02's positive one. A second platform would add the
  corruption row and nothing else — it is not needed for any claim p08 actually
  makes, provided finding 7 is phrased as the one-liner at the top.

---

## Part 5 — proof, twin, and the two errors

- **M2 reproduces exactly.** `.temp/review014/verus/m2.rs` (`0 < dr <= m` →
  `<= m + 1`, item **and** twin): shipped `11 verified, 0 errors`; `--cfg
  slb_twin` `14 verified, 1 errors`, *invariant not satisfied before loop* at
  `dr <= j <= m` (verus.rs:284). Control: `11` / `15`. **The twin is the only
  semantic mechanism that catches it**, and this is the first time in six
  patterns that has been demonstrated rather than argued. Keep the twin.
- **Four clauses vs three** — see M2 in the Major list. No wrong body exists;
  the *completeness claim* is what is wrong.
- **Stage 5a's `&mut [u8; SCR]` rejection is a genuine false positive** of a
  syntactic rule (does the `requires` mention `v`?), because an array type leaves
  nothing about `v` to constrain — the real safety fact, `m <= SCR`, *is* stated
  and *is* about `v`'s length, just not syntactically. And the widening **did**
  cost the contract something: the length fact (M2). `NOTES.md:706-710` calls
  that "a fix rather than a workaround"; it is a workaround, and the more general
  contract is the weaker one.
- **TCB tally is exact.** `grep -n 'assume\|external_body\|external\b\|assume_specification'`
  → four `#[verifier::external_body]` sites (verus.rs:232, 316, 372, 384), no
  `assume`, no `assume_specification`, no bare `external`. Body lines 4/1/4/1 =
  **10**, as §8 says. Obligation decomposition spot-checked and exact: `SCR` → `1
  verified` (the `const`-carries-an-obligation claim is real), `kernel` → `3`,
  `main` → `5`, `move_right` → `0`.
- **R5's exec code matches R4's**: `md5_fn 9259612a652d…` for both at `-O3
  isolated` per the gate record, and my own `asm.py stat` confirms 168/166.

---

## Part 6 — standard validity

- **The manifestation table reproduces in full, not on one cell.** I ran all
  **32** builds (8 cells × O0/O3 × isolated/whole) on `adversarial-overlap.bin`:
  every one printed `17006177784580028288`, exit 0.
- **Control 1** — `rustc --crate-type=lib --edition 2021 borrow_reject.rs` →
  **three `E0502`s**, exit 1, with rustc's `split_at_mut` suggestion. Reproduced.
- **Control 2** — `nonoverlap.rs` native prints `17006177784580028288` (correct);
  under Miri: `error: Undefined Behavior: 'copy_nonoverlapping' called on
  overlapping ranges` at line 71, backtrace `move_right → kernel → main`. The
  shipped `unsafe.rs` on the same input is clean. **Miri has teeth on aliasing
  UB**, confirmed.
- **Control 3 is genuinely wrong**, exactly as tabled: `fwd_loop` prints
  `4507432511443086080` on `adversarial-overlap` against the model's
  `17006177784580028288`, and agrees on `small` (`5963384295905503290`) and
  `large` (`16961355432730674521`). Safe, no panic, exit 0, wrong answer.
- **R2 is a fair naive port.** `for j in (0..m-dr).rev() { v[j+dr] = v[j] }` is
  what a programmer writes when `memcpy` will not compile; the two live bounds
  checks per byte are what that spelling costs, not a pessimisation. Its 11.26
  Ir/moved byte is correctly *not* rounded to the project's 10.0000 constant
  (§3b item 3), which is the right call — it is a checked read *and* a checked
  write.
- **`model.py` is genuinely independent**: two implementations (a `bytearray`
  slice-assignment simulation and a recursive walk mirroring the Verus spec
  functions element by element), cross-checked in `selfcheck()`. Not a
  transliteration of any rung.

---

## Part 7 — clean negatives (attacks that did not land; do not re-run these)

1. **"A `rep`-string instruction contaminates a published `Ir` number."** No.
   Only p08's gcc cells contain one; p02's memcpy sizes are 4 000 bytes below
   glibc's `rep movsb` threshold. Thresholds measured and tabulated above.
2. **"p02's stage-7 row is blind like p08's."** No — `__interceptor_memcpy`, and
   ASan fires on three of its inputs. The `_chk` rewrite needs a computable
   destination size; a `uint8_t *` parameter does not have one.
3. **"p08 undermines p05's nonlinearity claim."** No. p08's blocker is
   relational, p05's is nonlinear, and linearising p05's guard in isolation
   deletes the entire apparatus. (The finding still needs narrowing — but for the
   generality of its wording, not because p08 contradicts it.)
4. **"R1h − R1 = 0.00 is a mislabelled gcc-only measurement (the p02 mistake)."**
   No — it is written as a libc property, and I closed the one gap by checking the
   `_chk` pair, which also aliases.
5. **"The four-clause `ensures` would have caught a wrong body."** No such body
   exists: a `&mut [u8]` callee cannot change the slice's length in Rust. Gate 5c
   is right to delete it. (The *completeness claim* is still wrong — M2.)
6. **"Verus verifies M2 because the twin is vacuous / the proof is vacuous."**
   No. Obligation counts reproduce item by item; `main` verifies at a real call
   site (`5 verified`); M2's twin failure is a specific loop-invariant error.
7. **"`sanitizer_expect = 'clean'` is a green gate bought by pointing the gate at
   a blind build."** Argued and rejected: the alternatives are a red gate on an
   environment property or a harness change the task forbade, the predicate for
   the honest value is already computed, and the docstring carries the isolating
   experiment. The defect is the *record* (M3), not the declaration.
8. **"The `chunks_exact` variant changes the algorithm / skips work / breaks on
   some residue."** No: identical stdout and exit on all 150 committed p05
   inputs, and the −(nrow−7) law holds at ncol ≡ 0 and ≢ 0 (mod 8) alike.
9. **"Miri on p08 is vacuous because everything is in bounds."** No — the
   one-token mutant is caught and only on the overlapping input.
10. **"R2's 11.26 Ir/byte should be the project's 10.0000 constant."** No; §3b
    already says why and it is right.

---

## What I did not do

- Did **not** re-run `harness/check.py` on any pattern (nothing was written to
  `results/`; `git status` clean at exit).
- Did **not** re-measure p16 or p17, per scope.
- Did **not** chase *why* the linearised p05 kernel behaves differently as a lib
  and as a binary (IndVarSimplify re-deriving `i*ncol` is the observation, not a
  confirmed cause). B1 makes it moot.
- Did **not** measure the `chunks_exact` variant's static identity against R4 or
  build it at `O0`/`whole`, and did not run it through the gate — it lives in
  `.temp/review014/p05lin/` and needs an engineer task to land.
- Did **not** test whether p16's or p17's R3 has a better spelling too. Given B1
  is the third instance of this failure mode, somebody should.
