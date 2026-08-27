# TASK_109 — review of `p42-goto-cleanup`, the 26th pattern

**Role: research reviewer.** Scratch: `.temp/r109/` (568 KB, no binaries, one
`rebuild-all.sh` that regenerates every artefact I deleted).
**No `git add`, no `git commit`, no repo file edited** — `git status --porcelain
-uall` is empty apart from this report. **I did not run `harness/check.py`,
`harness/measure.py` or `harness/build.py`**, so `results/gate/` was never
rewritten and no `git checkout -- results/gate/` was needed. I read
`build.py`'s flag functions and reproduced the compile lines by hand.

---

## HEADLINE

**Two blockers, and they are the two the manager named.**

1. ⚠⚠ **`p42`'s central claim — "Verus at the pinned version CANNOT state
   leak-freedom" — IS FALSE.** A ghost ledger states it, catches exactly p42's
   bug, and costs **zero new trusted items, zero object code, and zero change to
   the pinned kernel signature or driver region.** Built, verified, and given an
   arm that fires, on the **real** p42 kernel, not a toy.
2. ⚠⚠ **`p42`'s R4 endpoint moves, and further than `p23`'s did.** `r4_endptr`
   is genuinely inadmissible — I found the precise reason and it is not the one
   disclosed. But a spelling nobody tried, `r4_foldonly`, **is** admissible
   (verifies 15/0, TCB unchanged, identity `exact`), and at **1407.00 / 51127.00**
   it is cheaper than **every R3 spelling p42 found**. The published claim
   *"safe-tuned Rust beats unsafe Rust here"* **is refuted, and it is refuted by
   the exact construction p42's own hashed `why` retracts.**

**Does p42 earn its slot? YES — but not for the three reasons the report gives,
and it needs a re-write rather than a re-build.** Detail in §3.

**Running count: 379 → 389** (+10, itemised at the end).

---

# §A — THE HEADLINE. Verus CAN state leak-freedom. **BLOCKER.**

## A0. The committed control re-runs, both arms. ✅ Clean.

```
$ timeout 300 ./verus_run.py patterns/p42-goto-cleanup/controls/affine_leak.rs
verification results:: 2 verified, 0 errors

$ ... --cfg p42_control_must_fail
error[E0382]: use of moved value: `pt`  ... `PointsToRaw` ... does not implement `Copy`
error[E0382]: use of moved value: `dl`  ... `Dealloc` ...
error: aborting due to 2 previous errors
```

`Tracked<Dealloc>` **is** affine. That half of the finding is sound and
reproduces exactly. What does not follow is the conclusion built on it.

## A1. ✅ CLEAN NEGATIVE — there is no linear tracked mode at the pin.

Verus `0.2026.08.09.92f466f`.

- `strings ~/tools/verus/rust_verify | grep -oE 'verifier::[a-z_0-9]+'` → **23
  attributes**, none of them a linear / must-consume / no-drop mode
  (`.temp/r109/verus_strings.txt`).
- `grep -rn affine ~/tools/verus/vstd/ -i` → **0 hits**. `grep -rn linear` →
  only `logatom.rs`'s *linearizability* and `nonlinear` arithmetic.
- The guide's *"linear ghost state"* (`state_machines/src/intro.md:41`) is a
  name, not a drop check.

**The engineer's second named route genuinely does not exist**, and that is now
measured rather than "does not appear to have". Nobody needs to re-run it.

## A2. ⚠⚠ THE GHOST LEDGER WORKS. `.temp/r109/ledger/`

**Encoding.** Never hold a bare `Tracked<Dealloc>`. `led_alloc` escrows it into
a tracked `Map<int, Dealloc>`; `led_free` withdraws it; the function's `ensures`
says **the ledger's domain comes back empty**, which Verus checks on *every*
exit, early returns included.

⚠ **The one non-obvious step, and it is why this is worth writing down:**
**keying the map by ADDRESS does not work.** vstd's `allocate` does not promise
the returned address is not already escrowed, so `dom.insert(a).remove(a) ==
dom` is unprovable and the postcondition fails on **both** exits. Keying by a
**ghost `int`** with `requires !old(led).dom().contains(k)` is discharged by the
caller for free. My first attempt failed on exactly this; the second worked.

⚠ **Neither wrapper is `external_body`.** Both are ordinary verified functions
over the pattern's own trusted `dig_alloc`/`dig_free`.

Three files, each with an arm that **must fail**:

```
$ ./verus_run.py .temp/r109/ledger/led1.rs                      -> 4 verified, 0 errors
$ ./verus_run.py .temp/r109/ledger/led1.rs --cfg p42_ledger_leak-> 3 verified, 1 errors

$ ./verus_run.py .temp/r109/ledger/verus_ledger.rs              -> 17 verified, 0 errors
$ ...                          --cfg p42_ledger_leak            -> 16 verified, 1 errors

$ ./verus_run.py .temp/r109/ledger/verus_ledger_nosig.rs        -> 18 verified, 0 errors
$ ...                          --cfg p42_ledger_leak            -> 17 verified, 1 errors

error: postcondition not satisfied
   --> .../verus_ledger_nosig.rs:457:9
457 |         final(led).dom() =~= Set::<int>::empty(),
    |         ^^^^ failed this postcondition
473 |         return 0;
    |         -------- at this exit
```

`verus_ledger.rs` and `verus_ledger_nosig.rs` are **`patterns/p42-goto-cleanup/
verus.rs` itself**, transformed by a script (`.temp/r109/ledger/`, every anchor
asserted), not a hand-written miniature. The `--cfg p42_ledger_leak` arm deletes
**exactly** the error path's release — the same edit `affine_leak.rs` shows the
default encoding accepts `2 verified, 0 errors`. Verus now points at
`return 0;`, which is p42's bug, by file and line.

**`verus_ledger_nosig.rs` is the one that matters**: it keeps the ledger as a
*local* inside `kernel` and pushes the obligation onto an `#[inline(always)]`
`kbody`. **The pinned kernel signature does not change. The driver region does
not change. `driver.canonical` does not change.** NOTES 6's stated obstacle —
*"it changes the kernel's signature, and the kernel signature is pinned across
all six rungs"* — is avoidable in three lines.

## A3. What the ledger costs: **nothing that is measured.**

Built with `build.py::build_verus`'s own flags (`--compile -C codegen-units=1
-C opt-level=3 -C debug-assertions=off --cfg slb_isolated`):

| | shipped R5 | ledger R5 |
|---|---|---|
| verification | `15 verified, 0 errors` | **`18 verified, 0 errors`** |
| `^#\[verifier::external_body\]` | 5 | **5** |
| hand-written axioms | 0 | **0** |
| kernel `n_fn` | 122 | **122** |
| `md5_fn` | `1ab63fde449d56dfab76adbba02d16fb` | **identical** |
| `md5_raw` | `26e2a07b0e29eb767890a4d7a9234b4c` | **identical** |
| `asm.identity_level` | — | **`exact`, `md5_raw_equal: True`** |

`1ab63fde449d` is the hash TASK_104_REPORT itself quotes for the R4/R5 pair, so
the ledger R5 is byte-identical to the **shipped R4** as well. **The only pin
that moves is `verus.obligations` 15 → 18.**

## A4. Where the false claim is written

It is not one sentence. It is inside the **hashed `slb-contract` block twice**
and in five more places:

| file | what it says |
|---|---|
| `spec.md` `idiom.why` (**hashed**) | *"Verus at the pinned version CANNOT state `this allocation is released on every path`"* |
| `spec.md` `identity[0].why` (**hashed**) | *"Verus cannot state leak-freedom at the pinned version"* |
| `verus.rs:8-26` module comment | *"the proof rung of this ladder cannot state the property the row prices"* |
| `unsafe.rs:44-49` SAFETY (5) | *"THIS IS THE PATTERN'S OWN OBLIGATION AND VERUS DOES NOT DISCHARGE IT"* |
| `NOTES.md` 6 | *"Not built. OPEN"* — for the route that works |
| `NOTES.md` `dig_free` trusted argument | *"no clause of it could be strengthened to say otherwise"* |
| `README.md`, `controls/affine_leak.rs:1` | the headline |

⚠ **The correct finding is BETTER than the retracted one**, exactly as the task
file predicted: *"the natural encoding does not state leak-freedom, and here is
one that does — at zero TCB and zero object code, for the price of an escrow
discipline the reader has to trust nobody bypasses."* That last clause is the
honest limit: the ledger binds allocations that go through `led_alloc`; a direct
call to `vstd::raw_ptr::allocate` still leaks silently. **That is a module-level
discipline, not a global guarantee — and it is a far more interesting sentence
than "Verus cannot".**

---

# §B — THE R4 ENDPOINT. **BLOCKER.** `.temp/r109/endptr/`

## B1. Is `r4_endptr` in contract? **Yes — identically to the shipped rung.**

Drove the real `check.py::spelling_matches` over every backticked spelling in
`idiom.required`/`.forbidden`, rust scope, against all eight `spellings.py`
variants:

```
spelling                     r4_ship  r4_endptr  r4_add  r4_movptr  r3_ship ...
required[3] 'dig[len-1]'        .        .          .       .          .
required[4] 'vec![0u8; len]'    .        .          .       .          .
required[4] 'Vec::with_capacity'.        .          .       .          Y
required[4] 'extend'            .        .          .       .          Y
required[4] 'std::alloc::alloc' Y        Y          Y       Y          .
required[4] 'std::alloc::dealloc'Y       Y          Y       Y          .
forbidden[4..7]                 .        .          .       .          .
```

`r4_endptr` matches exactly what `r4_ship` matches and hits no `forbidden`.
**No tautological conjunct is needed — p23's lever does not apply here**,
because there is no out-of-contract spelling to rescue.

## B2. Does its R5 close? **NO — and not for the reason disclosed.**

`.temp/r109/endptr/probe_end.rs`, with a control that verifies so the probe
cannot be vacuous:

```
control_in_range   dig_at(p, base, len - 1)  ->  verifies
end_pointer        dig_at(p, base, len)      ->  precondition not satisfied
                                                 `base + i <= usize::MAX`
verification results:: 3 verified, 1 errors
```

`vstd::raw_ptr::allocate` ensures only `addr + size <= usize::MAX + 1`
(`grep -n 'usize::MAX' ~/tools/verus/vstd/raw_ptr.rs` → **one hit, that one**),
and `PointsToRaw::is_range` carries no address bound. So **the one-past-the-end
pointer `r4_endptr` needs is not computable in verified exec code.** Building it
would cost a *strengthened* trusted `ensures` on `dig_alloc` — which p42's own
trusted argument forbids (*"Every difference from vstd is a WEAKENING or a
respelling, never a strengthening"*) and which is precisely what disqualified
p16's `r4_hdr`. ✅ **The disclosed open question is now answered: inadmissible.**

## B3. ⚠⚠ BUT A CHEAPER ADMISSIBLE R4 EXISTS AND WAS NEVER TRIED.

The end pointer is only needed because the fold loop walks *down*. A do-while
shape never leaves the allocation:

```rust
let mut q: *mut u8 = dig_at(p, base, len - 1);
loop {
    acc = acc.wrapping_mul(31).wrapping_add(dig_read(q) as u64);
    if q == p { break; }
    q = q.with_addr(q.addr() - 1);
}
```

Operations used: `with_addr`, `addr`, `ptr_ref`, and `<*mut T as PartialEq>::eq`
— **all four specified at the pin** (`vstd/raw_ptr.rs:198`, `ensures res <==>
x@.addr == y@.addr && x@.metadata == y@.metadata`). `r4_foldonly` keeps the
shipped WRITE loop untouched, so it changes one loop only.

| | result |
|---|---|
| R5 (`.temp/r109/endptr/r5_foldonly.rs`) | **`15 verified, 0 errors`** — same count as shipped |
| `^#\[verifier::external_body\]` | **5**, unchanged; **0** new axioms |
| identity R4 ≡ R5 at `-O3` | **`exact`**, `md5_raw_equal: True`, `n_fn=128`, `md5_fn=28432cb848832a69…` |
| checksums | agree with the shipped rung on **all 12 committed inputs**, exit codes included |
| in contract | same spelling profile as `r4_ship`; keeps `required[0]`, `[3]`, `[4]` |

**Same-session marginals** (`.temp/r109/endptr/compare.py`, all six built and
measured back to back, because comparing across sessions is what this project
distrusts):

```
variant            small        large
r4_ship          1617.00     59834.00   <- TASK_104's published figures,
r3_ship          1419.00     51138.00   <- reproduced EXACTLY, to the
r3_zeroed        1572.00     55298.00   <- hundredth, all four
r4_endptr        1455.00     53174.00   <-
r4_dowhile       1409.00     51131.00   <- NEW
r4_foldonly      1407.00     51127.00   <- NEW, cheapest

cheapest R3 - cheapest R4 (TASK_104): -36.00  -2036.00
cheapest R3 - r4_foldonly      (NEW): +12.00    +11.00   <- THE SIGN FLIPS
```

## B4. What the overlap means, plainly

> **NOTES.md 11b's headline is refuted.** *"cheapest R3 found (1419.00 /
> 51138.00) is below cheapest R4 found (1455.00 / 53174.00) … so 'safe-tuned
> Rust beats unsafe Rust here' is not an artefact of an unsearched R4 side"* —
> **the R4 side WAS unsearched.** One more spelling, using nothing the pin does
> not already specify, puts R4 **below** every R3 spelling p42 measured.

⚠ **And the failure is one p42's own hashed declaration predicts, in its own
words.** The shared named-spelling paragraph — byte-identical in six patterns,
inside the sha256 — says:

> *"And `min(R3 found) - min(R4 found)` is **NOT the repair** — two upper bounds
> differenced bound nothing in either direction."*

NOTES 11b is that construction, and it calls the two minima **"the two
INFIMA"**, which they are not: they are upper bounds on the infima over four
spellings each. `r4_foldonly` is the counterexample the paragraph warned about.

**What survives, and should be what ships:** `R3ship − R4ship` = `−198.00 /
−8696.00` kernel-exclusive — a statement about **two shipped cells**, which is
the only form the same paragraph licenses. Plus an R4-side span that now runs
**1407 … 1617** on `small` and **51127 … 59834** on `large`, overlapping the R3
span at both ends. **A difference whose endpoints overlap is not a difference,
and p42 should say so rather than narrow the claim a second time.**

---

# §C — THE NUMBERS

## C1. ✅ The two gcc C rungs ARE two rungs. Confirmed by hand.

Rebuilt with `build.py::c_flags`' own string. `.temp/t104/probe2.py` (the form
that keeps `<SELF+0xNN>`):

```
gcc-kernel             insns= 49 norm=ddfee5f4896e alloc=1 free=1
gcc-kernel_hardened    insns= 49 norm=e9ec52dfc42e alloc=1 free=1
clang-kernel           insns=119 norm=33a81fa90e15
clang-kernel_hardened  insns=121 norm=49fc5210b34c        all six pairs !=
```

Hand `objdump` diff of the gcc pair — **exactly one field, nothing else**:

```
-    197b:	jne    19e1 <kernel+0x91>
+    197b:	jne    19dc <kernel+0x8c>
```

**The C side of this pattern does have a boundary. It is one branch-target field
wide, and that is what `R1 − R1h = 0.00` means.** F1's probe-2 defect
(discarding the self-relative offset) is real and its consequence here is
exactly as reported: `knorm.py`/`b4_norm.py` collapse these two into one rung.

## C2. ⚠ MAJOR — the clang mechanism is WINDOW PARITY, not window size, and the report names one of three terms.

`.temp/r109/crungs/clangdelta.py`:

```
  window  parity      buggy   hardened   R1-R1h
      64    even    1151.44    1156.44    -5.00
      65     odd    1169.72    1173.72    -4.00
      66    even    1186.72    1191.72    -5.00
      67     odd    1200.72    1204.72    -4.00
     512    even    7870.00    7875.00    -5.00
     513     odd    7889.72    7893.72    -4.00
     514    even    7906.00    7911.00    -5.00
     515     odd    7920.00    7924.00    -4.00
```

`small` is win **97 (odd → −4)**; `large` is **4096 (even → −5)**. The report
and `NOTES.md` 5 present `−4.00`/`−5.00` as a `small`-vs-`large` pair. **The
variable is parity and the size term is exactly zero over a 32× range.**

Isolated from my own disassembly — **three** terms, of which the report names
one:

1. **+3** — the `setne`/`sete`/`or` prologue merge. The report's mechanism, and
   it is real: I reproduced the exact instruction sequence it quotes.
2. **+1** — an alignment `nopw 0x0(%rax,%rax,1)` at `16ea` in the **hardened**
   scan-loop preheader, executed once per call. Not padding after a `ret`;
   fall-through.
3. **+1 on EVEN windows only** — the odd-remainder guard changes from
   `test $1,%bl; je <skip>` to `test $1,%bl; jne <do>; jmp <skip>`, costing one
   extra instruction when the remainder is absent.

`3+1 = 4` (odd), `3+1+1 = 5` (even). Exact, both bands, both parities.
RECAP finding 37's companion rule — *a limb claiming a new REASON owes an
isolation* — is satisfied by the report only in part.

## C3. ✅ The "two points and no rate" restraint HELD.

`grep` over `NOTES.md`, `README.md`, `spec.md`: the only fits are NOTES 11d's
band-A fits, published **as the evidence they do not transfer**. The
`Ir/element` columns are ratios at the two measured points and differ from each
other (19.309 vs 19.007), i.e. they display the non-constancy rather than hide
it. No slope is offered for extrapolation anywhere. Nothing sneaked back in.

## C4. ✅ The allocator-size-class REFUTATION reproduces exactly.

Re-ran `.temp/t104/allocclass/iso.py` after reconstructing the two build lines
it needs (see m2):

```
var  malloc(len)     fit = 184.177 + 18.91424*w  in-sample 1.356  band-B +37.61 .. +39.23
fixed malloc(4096)   fit = 377.177 + 18.91424*w  in-sample 1.356  band-B +37.61 .. +39.23
```

Identical slope, identical in-sample residual, identical band-B residuals; only
the intercept moves **+193**. Checksums agree between the two binaries on
`small.bin` and `sweep-w512.bin`, so the fixed arm really is the same
computation. **This is a real refutation** — had the size class been the cause,
the fixed arm's residuals would have collapsed, and they did not. "OPEN, do not
attribute" is the right verdict and I have nothing to add to it.

## C5. ✅ `controls/leak.sh` HAS TEETH — ⚠ but its point count is wrong.

I ran the **byte-identical shipped script** (md5 `a5140870a5fa81a4e01be82955b6d17a`
both copies) inside a scratch replica at `.temp/r109/leak/fakerepo` — symlinks
to the real `common/`, `inputs/` and `model.py`, `c/` copied. **No repo file was
touched and nothing was planted in the tree.**

```
unplanted : exit=0,  352 rows,  0 flagged
planted   : exit=1,             12 rows flagged  *** WRONG (want YES) ***
```

The plant restores the missing `goto cleanup` in `c/kernel.c`, i.e. a non-leak.
The script fails, on 3 inputs × 4 optimisation levels. **Teeth confirmed.**

⚠ **The count is not 88, it is 352.** The glob is `"$PDIR"/inputs/*.bin`, which
takes the 32 `sweep-*.bin` as well: `2 × 4 × 44 = 352`. Excluding sweeps it
would be `2 × 4 × 12 = 96`. **`88` was never a correct number for any input
set**, and it is a literal in four places: the script's header comment
(*"2 kernels x 4 levels x 11 inputs"*), the script's own success message
(*"ALL 88 POINTS AS DECLARED"* — which it printed on my 352-row run), `NOTES.md`
3, and `README.md`'s table.

## C6. ✅ `sanitizer_expect` — the disclosure is accurate.

`"fires"` is discharged by any of `fired`'s four substrings, so a stray
heap-buffer-overflow or a UBSan `runtime error` would satisfy p42's obligation.
`"clean"` is strong. The gate record *stores* the diagnostic text (I can read
`ERROR: LeakSanitizer: detected memory leaks Direct leak of 624 byte(s) in 26
object(s)` in `results/gate/p42-goto-cleanup.json`) but nothing **checks** it.
`controls/leak.sh` carries the real check, and it works. Reported upward as
asked; not a p42 defect.

---

# §D — THE DISCLOSED SELF-CORRECTIONS. **All four fixes are real.**

| fix | verified how | result |
|---|---|---|
| (a) prose `forbidden` backticks stripped | `idiom_audit` in the gate record | `forbidden_spellings: 4`, `forbidden_unaudited_entries: 4` — the four prose entries carry no spelling. Permanent and correct. |
| (b) `vparse` 5c-req silently off | `results/gate/p42-goto-cleanup.json` → `requires_strength["verus.rs"]["mutants"]` | **six `dig_free` rows**, each `verdict: not a tautology`, `verified=16 errors=1`. **5c-req is RUNNING, not suppressed.** |
| (c) one `dig_alloc` `ensures` deleted | deleted each of the four survivors in turn (`.temp/r109/clausemut/`) | **all four give `14 verified, 1 errors`.** Every remaining conjunct is load-bearing. |
| (d) three `SLB-TRUSTED-ARGUMENT` sections | read | present, NOTES 7, one per `_is_trusted` item |

## D2. `contract_sha256` — no pin moved, but rule 6's hole is open again.

```
spec.md slb-contract sha256 : 4a252569067081a55c55c8e6177bc8f6a4f897a57cd59a00c7c000a3da8d29a4
gate record contract_sha256 : 4a252569067081a55c55c8e6177bc8f6a4f897a57cd59a00c7c000a3da8d29a4
NOTES.md "as shipped"       : 4a252569067081a55c55c8e6177bc8f6a4f897a57cd59a00c7c000a3da8d29a4
37 source_sha256 entries in the gate record, 0 stale -> the record is current
```

⚠ The disclosure is honest and the intermediate value cannot be reconstructed
(new pattern; NOTES 0 says so, correctly, rather than citing the vacuous
`git show HEAD:` command). **But rule 6 protects the wrong thing here, exactly
as `p46` demonstrated: two hashed `why` clauses are now FALSIFIED by
measurement** — `idiom.why`'s *"Verus at the pinned version CANNOT state …"* and
`identity[0].why`'s *"Verus cannot state leak-freedom at the pinned version"*.
The hash proves when they were written, not that they are still true. **A third
is self-contradictory rather than falsified**: NOTES 11b's "two INFIMA" against
the hashed paragraph's own retraction of `min − min` (§B4).

---

# OTHER FINDINGS

## M3 — `spec.md`'s pin table over-claims. **Major.**

`spec.md:63` says *"Three things in that are load-bearing and are pinned in the
block below"*. **None of the three is enforced by a spelling.**

- item 1 (allocation before the tag test) is prose — correctly unenforceable,
  and `forbidden`'s prose entries say so.
- item 2 — `required[2]` is `{"c": "(uint8_t)(run >> 24)", "rust": "(run >> 24)
  as u8"}` with **NO BACKTICKS**, so `check.py::_TICK` yields zero spellings and
  the entry pins **nothing**. Same for `required[1]` `{"c": "goto cleanup"}` —
  **the idiom the pattern is named for, and the CERT rule it models, is
  unenforced.** `p02` writes its per-language entries *with* backticks inside
  the prose, so this is a p42 slip, not a convention.
- item 3 — `required[3]`'s `` `dig[len-1]` `` matches **0 of 4 rungs in either
  language**, landing in `required_pins_nothing` (no rung writes it; R4/R5 have
  no `dig` binding at all).

The gate record confirms the arithmetic: `spellings: 16`, all of them from
`required[3]`, `required[4]` and `forbidden[4..7]`. `required[0..2]` contribute
**zero**. The `required` half of the audit is data, not a verdict, so the gate
prints this and stays green — which is by design, but the prose above the block
should not claim otherwise.

## m1 — `controls/spellings.py` cannot run in a fresh clone. **Minor.**

The variants it writes keep `#[path = "../../common/driver.rs"]`, which from
`.temp/t104/spell/` resolves to **`.temp/common/driver.rs`** — a gitignored copy
that happens to exist on this box (identical to `common/driver.rs`; I checked).
In a fresh clone the control dies with *"couldn't read …: No such file"*. My own
port hit it. One `cp` in the script fixes it.

## m2 — `.temp/t104/allocclass/iso.py` has no rebuild script. **Minor.**

It consumes `.temp/t104/build/p42c` and `p42c_fixed`, both correctly deleted as
artefacts, and **nothing in `.temp/t104/` rebuilds them** — CLAUDE.md constraint
6's *"if a blob has no script that rebuilds it, write one before finishing"*.
I reconstructed the two `gcc` lines; they are in `.temp/r109/rebuild-all.sh` §5.
`.temp/t104/allocclass/main_shim.c` is a **0-byte file**.

## m3 — one over-reach in the `dig_free` trusted argument. **Minor.**

*"no clause of it could be strengthened to say otherwise"* is defensible about
`dig_free` **itself**. The sentence it supports — *"p42's leak claim on the Rust
side rests on Miri and not on this contract"* — is now wrong: a **verified
wrapper** over that same trusted item states the obligation at zero TCB (§A2).

---

# THE THREE CALLS THE MANAGER WAS LEAST SURE OF

### 1. *"That 'Verus cannot state leak-freedom' survives an actual attempt at a better encoding."* — **IT DOES NOT.**

The ghost ledger works, on the real kernel, with an arm that fires, at **zero
new trusted items, zero object code and zero interface change**. You were right
to want to know now. The linear-mode half of the caveat is a clean negative and
can be closed permanently. **The replacement claim is stronger and more
interesting than the one it retracts** — write it as *"the natural encoding does
not; escrowing the token in a tracked map does, and the residual trust is that
nobody bypasses the wrapper."*

### 2. *"That `r4_endptr` being left unbuilt is acceptable."* — **IT IS NOT, and this is worse than p23's.**

On p23 the cheaper spelling turned out admissible and moved the floor. Here
`r4_endptr` itself turns out **inadmissible** — for a reason nobody had
identified (the one-past-the-end pointer) — but the search that stopped at four
spellings missed one that **is** admissible and is cheaper than everything on
either side. The floor moves **210 / 8707 `Ir`/call**, and the pattern's
comparative headline reverses. **You called it: this was the most likely place
for a real defect.**

### 3. *"That `p42` is worth its slot at all."* — **YES, and I would not refuse it — but two of your three negatives do not survive.**

- ~~"its R5 does not cover its bug class"~~ → **it can, and cheaply.** That is a
  *better* row, not a lost one: it is now the only pattern in the tree that
  prices what a leak-freedom obligation costs, and the answer is **0 `Ir`, 0
  TCB, +3 obligations**.
- ~~"its rate is unpublishable"~~ → **this one stands** and is well done. The
  out-of-band test, the refuted candidate and the explicit OPEN are exemplary.
- ~~"its gcc rungs differ by 0.00"~~ → **stands, and is sharper than reported**:
  the two rungs differ in *one branch-target field*, and the clang side is a
  parity effect with a fully isolated three-term mechanism (§C2).

What earns the slot: it is the **only leak row in a 26-pattern tree**; the
`0.00` with a one-field boundary is a real result; the parity anti-result is a
real result; the band-local rate with a refuted mechanism is a real result; and
F1 (probe 2's fourth defect, kill direction) and the `fired`-predicate
limitation are durable harness findings. **p42 needs a re-write of §6, §9 and
§11b — not a re-build.** The rungs, the inputs, the model, the controls and the
gate are all sound.

---

# WHAT I DID NOT DO

1. **I did not build `r4_foldonly` as the shipped R4.** That is the engineer's
   call and would need a `spec.md` `identity`/`obligations` pass, a re-measure
   and a re-gate. I built it far enough to settle admissibility: it verifies, it
   is byte-identical to its R4, its TCB is unchanged and it agrees on all 12
   inputs. I did **not** run Miri on it.
2. **I did not run the gate**, so I have not re-derived
   `PASS-WITH-BLOCKED-ROWS`. I verified instead that all 37 `source_sha256`
   entries in the committed gate record match the tree, so the record is current
   and its `idiom_audit` / `requires_strength` numbers are about this tree.
3. **I did not re-measure the kernel-exclusive ladder table.** §B's numbers are
   whole-program marginals from `spellings.py`'s own convention, measured in one
   session; the four I could compare reproduced to the hundredth, which is my
   evidence that the table is sound.
4. **I did not attempt a ledger for the C or safe-Rust rungs.** Not applicable.
5. **I did not test whether the ledger encoding survives `--cfg slb_twin`**, nor
   whether `check.py::_is_trusted` would classify `led_alloc`/`led_free` (they
   are not `external_body` and contain no `unsafe`, so they should not, but I
   did not drive the function).
6. **I did not chase the superlinearity.** The report leaves it OPEN and I agree
   with that; I only verified the refutation.
7. **I did not sweep Miri seeds** — the report did, and nothing I found bears on
   it.

---

# RUNNING COUNT

⚠ **PROTOCOL rule 2's count was 379**, and the task file states it once and
consistently (the `368`/`324` split that bit `TASK_104` is reconciled — I
re-read the closing paragraph and it says 379 in both places).

I claim **+10 → 389**, itemised so the manager can discount any of them:

1. **`Tracked<Dealloc>` being affine does NOT mean Verus cannot state
   leak-freedom.** Ghost ledger built, verified 18/0 on the real kernel, arm
   fires, zero TCB, zero object code, zero interface change. **BLOCKER.**
2. **There is no linear tracked mode at the pin** — the other named route, now
   a measured clean negative rather than "does not appear to have".
3. **`r4_endptr` is inadmissible, and the reason is the one-past-the-end
   pointer**, not an unbuilt proof: vstd's `allocate` permits
   `addr + size == usize::MAX + 1`.
4. **`r4_foldonly` is an admissible R4 that is cheaper than every R3 spelling
   p42 measured** — R3-beats-R4 refuted, floor moves 210 / 8707. **BLOCKER.**
5. **NOTES 11b's "two INFIMA" is the `min − min` construction p42's own hashed
   `why` retracts**, with `r4_foldonly` as the counterexample.
6. **The clang `−4`/`−5` is window PARITY, not window size**, with three
   mechanisms isolated where the report named one.
7. **`required[1]` and `required[2]` pin nothing** (per-language entries with no
   backticks) and `required[3]` pins nothing on any rung — `spec.md`'s "three
   things … are pinned" claim is enforced zero times.
8. **`controls/leak.sh` says 88 points and runs 352**, and 88 was never right
   for any input set. (Its teeth are real — planted and it fails.)
9. **`controls/spellings.py` is not runnable from a fresh clone** — it depends
   on a gitignored `.temp/common/driver.rs`.
10. **`.temp/t104/allocclass/iso.py` has no rebuild script** for the two
    binaries it consumes; `main_shim.c` is 0 bytes.

Items 1–7 are corrections to measured claims; 8–10 are reproducibility hygiene.
If you prefer to count only the first seven, the figure is **386**.
