# p42-goto-cleanup — working notes

## 0. Rule 6 disclosure (`.tasks/PROTOCOL.md`)

`slb-contract` block sha256 **as first written, before any measurement**:

```
50697e33b2971fc4c965a710fc1d6fad19000d81ecb7744fa8ddc07471e9fb8d
```

**As shipped**, after the three edits below:

```
4a252569067081a55c55c8e6177bc8f6a4f897a57cd59a00c7c000a3da8d29a4
```

⚠ **The hash MOVED TWICE, and here is exactly what moved it. All three edits are
the gate's own findings, none weakens anything, and the intermediate value was
`22cced7d398a9837624615e11f53fdecc967fb35c18c01590a50e6d8d8e6a5b6`. Edits 1 and
2 were made BEFORE any `harness/measure.py` run; edit 3 was made AFTER, and it
touches `idiom` only -- no `requires`, no `ensures`, no `identity`, no
`driver`, no `collapse` -- so no measured number depends on it and none moved
(`results/p42-goto-cleanup.json` does not hash `spec.md` at all: its
`source_sha256` covers the rung sources, `model.py`, `inputs/gen.py`,
`c/kernel.*`, `c/main.c` and the harness).**

1. **`verus.items["verus.rs"]["dig_alloc"].ensures` lost one conjunct** —
   `pt.0.addr() as int % align as int == 0`. Stage 5c (`clause-mut`) deletes
   every `ensures` conjunct of every trusted item in turn and requires the file
   to fail; deleting this one still gave `15 verified, 0 errors`, so it was a
   trusted claim nothing depended on. p42 allocates with `align == 1` and
   `into_typed::<u8>` needs `start % align_of::<u8>() == 0`, which
   `vstd::layout::align_of_u8` discharges. **Direction: strictly weaker than
   vstd's original**, which is the direction `.memory/01-ladder.md`'s direction
   test allows.
2. **`dig_free`'s `pt` parameter stopped being destructured** —
   `Tracked(pt): Tracked<PointsToRaw>` became `pt: Tracked<PointsToRaw>`, and
   the four clauses that mention it moved from `pt.…` to `pt@.…`. This is not a
   semantic change; it is `harness/vparse.py`'s parameter parser, which raises
   *"parameter pattern 'Tracked(pt)' is not a plain identifier"* and thereby
   turned off stage 5c-req for all six of `dig_free`'s `requires` **and** made
   `_scan_unsafe_sites` fail the TCB stage. p27's `rec_free` uses the
   un-destructured spelling for the same reason.
3. **The four Rust `forbidden` entries gained BACKTICKS** —
   `{"rust": "ManuallyDrop"}` became `{"rust": "`ManuallyDrop`"}`, and the same
   for `mem::forget`, `Box::leak` and `Box::into_raw`. Stage 0b shouted that
   each entry *"has NOT ONE backticked spelling, so the enforced audit never
   ranges over it and its share of the 0 hits above is vacuous"*. It was right:
   unbackticked, those four were prose. Backticked, `spelling_matches` really
   runs over all four Rust rungs — verified to be 0 hits before the edit was
   made, so this **turns an enforcement ON** rather than accommodating the tree.
   The `why` also gained a paragraph saying, in the gate's own terms, that the
   first four entries forbid a STRUCTURE rather than a token and that their
   shout is permanent and correct.

⚠ **The `git show HEAD:… | diff -` command PROTOCOL rule 6 quotes is VACUOUS on
a new pattern** and is deliberately not run here: p42 lands in one commit, so on
a clean tree it always prints nothing and always looks like it passed. The two
hashes above are the only evidence.

**Honest scope of the claim.** The block was first written *after* the six rungs
existed and after the exploratory probes in `.temp/t104/`, and *before* any
`harness/measure.py` run and before any `results/` record. No number in
`.temp/t104/`'s probe output is quoted as a p42 number; every figure below that
is called a p42 number came from the shipped tree.

---

## 1. The bug class, and the real defect it is modelled on

**A 25-pattern census of the built tree finds ZERO leak rows.** Taking each
built pattern's bug class from `.memory/06-catalogue.md`'s own table: none
(p01), spatial OOB write (p02), index underflow (p03), an in-bounds wrap (p04),
dimension/overflow (p05), an unreduced rotate amount (p06), unsigned underflow
(p07), overlap UB (p08), a missing bitset guard (p09), boundary off-by-one
(p10), missing terminator (p11), stack overflow (p12), truncation (p13),
unbounded field count (p14), TLV length (p16), integer overflow (p17),
unbounded shift (p18), state confusion (p19), non-termination (p22),
`index >= len` (p23), use-after-free (p27), index out of table (p36),
strict-aliasing UB (p38), limb bound/carry (p46), timing side channel (p47).
**Memory leak appears nowhere.**

`p27` is the row most likely to collide and it does not. It is the tree's only
other *temporal* pattern and it does ship `allocate`/`deallocate` — but it is
built **not to leak by contract**: its `spec.md` says the epilogue frees every
record still alive *"so neither C rung leaks"*, and its `forbidden` list
excludes `ManuallyDrop`, `mem::forget`, `Box::leak` and `Box::into_raw`. **What
p42 adds is exactly the path p27 forbids itself: p27 frees on every path by
construction, and p42's whole subject is the path where it does not.**

**The precedent, fetched and quoted rather than remembered.** Linux commit
`505d9dcb0f7ddf9d075e729523a33d38642ae680`, *"crypto: ccp - fix resource leaks
in `ccp_run_aes_gcm_cmd()`"*, `drivers/crypto/ccp/ccp-ops.c`:

```
 		if (ret)
-			goto e_ctx;
+			goto e_aad;
```

That is **CVE-2021-3764** — *"A memory leak flaw was found in the Linux kernel's
`ccp_run_aes_gcm_cmd()` function that allows an attacker to cause a denial of
service"*, CVSS 3.1 base **5.5**, vector `AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`
(suse.com/security/cve/CVE-2021-3764.html; the patch text above is from
github.com/torvalds/linux, fetched, not paraphrased). The same commit fixes two
further links of the same chain. The generic form is SEI CERT **MEM12-C**,
*"Consider using a goto chain when leaving a function on error when using and
releasing resources"* — p42's C rung follows the rule and breaks it in one
branch, which is the shape the rule exists to name.

⚠ **What is NOT verified: nothing here claims p42's kernel is a port of that
function.** It is the same defect shape at 25 lines instead of 200.

---

## 2. Can the gate express a leak expectation at all? (Answered before the rungs existed.)

`sanitizer_expect` had never been used for a leak anywhere in this tree, so this
was settled first, against the **real** `harness/check.py::check_sanitizers`
driven on a synthetic pdir — not against a hand-written copy of it.
`.temp/t104/gp_drive.py` imports `check.py` and calls the function. Four arms,
**two of them positive controls that must fail**:

```
arm A  buggy kernel    + sanitizer_expect="fires"   failures=0   want PASS   OK
arm B  hardened kernel + sanitizer_expect="fires"   failures=2   want FAIL   OK  <- CONTROL
arm C  buggy kernel    + sanitizer_expect="clean"   failures=2   want FAIL   OK
arm D  hardened kernel + sanitizer_expect="clean"   failures=0   want PASS   OK
```

**Answer: yes.** `check_sanitizers`'s `fired` predicate matches LSan's report on
two independent substrings — the report carries both `ERROR: LeakSanitizer:
detected memory leaks` and `SUMMARY: AddressSanitizer: N byte(s) leaked in M
allocation(s)`.

⚠ **AND THE GATE LIMITATION IT EXPOSES, WHICH IS REAL AND SHOULD BE REPORTED
UPWARD.** `fired` is a four-way substring OR:

```python
fired = ("runtime error" in se or "AddressSanitizer" in se
         or "UndefinedBehaviorSanitizer" in se or "ERROR:" in se)
```

so **it cannot tell a leak from a heap-buffer-overflow**. p42's `"fires"`
obligation would be discharged by any diagnostic at all. This is a coarsening,
not a blocker, and `controls/leak.sh` carries the finer check the gate cannot:
it greps for `LeakSanitizer` **specifically**, requires that no *other*
sanitizer fired, and compares the leaked byte count against the model's derived
invariant.

⚠ **A control this probe wrote for itself was ONE-POINTED and it was caught
before it shipped.** The first `adversarial-mixed` input leaked 64 objects on 64
iterations — i.e. *every* call took the error path, because the error path
returns 0, `acc` never leaves 0, `off` never leaves 0, and the same malformed
word is read every time. A "mixed" input that is in fact all-error is a control
with one point. `inputs/gen.py` now forces word 0 well-formed and **asserts**
both call counts are non-zero; `model.py::selfcheck` re-asserts it at gate time.
The shipped `adversarial-mixed.bin` runs **38 success calls and 26 error calls**.

---

## 3. The detector, and why this pattern needs no `__lsan_default_options` hook

`.memory/00-environment.md` records a leak shape that LSan sees at `-O0` and
misses at `-O1`/`-O2` because gcc inlines the allocating callee and the stale
root stays live in `main`'s frame, and it offers
`__lsan_default_options() -> "use_stacks=0"` as a zero-`Ir` fix. **p42 does not
need it, and `c/main.c` deliberately defines no hook.**

`controls/leak.sh` is the evidence and it is **88 points, not one**: 2 kernels ×
4 optimisation levels × 11 inputs, at the gate's own stage-7 flag string except
for `-O`, which it sweeps. Verbatim tail:

```
ALL 88 POINTS AS DECLARED: the buggy rung reports a LeakSanitizer leak of
exactly n_err * win_len bytes on every input that reaches the error path
and is silent on every input that does not; the hardened rung is silent on
all of them, at every optimisation level.  No other sanitizer fired.
```

The three rows that fire, at every one of `-O0`/`-O1`/`-O2`/`-O3`:

| input | LSan | leaked bytes | why that number |
|---|---|---|---|
| `adversarial-notag.bin` | YES, exit 1 | `n_err × win_len` | 8 erroring calls × a 32-byte digest |
| `adversarial-mixed.bin` | YES, exit 1 | `n_err × win_len` | 26 of 64 calls × 24 bytes |
| `adversarial-win1.bin` | YES, exit 1 | `n_err × win_len` | 16 calls × **one** byte |

⚠ **The byte count is published as an INVARIANT, not as a transcript.**
`.tasks/PROTOCOL.md` rule 6's newest lesson is that a number only a rebuild can
produce must not be written into a file the rebuild re-hashes — `p23` got `7, 7,
8, 8` from four runs of the same thing. `model.py::leak_bytes` **derives**
`n_err * win_len` from the file bytes alone and the control asserts LSan against
it, so the number in this table is a property of the input, not of the run.
✅ **Checked rather than assumed: it is identical across all four optimisation
levels and across repeated runs.**

The `-O` dependence `.memory/00-environment.md` warns about is genuinely absent
here, and the reason is the shape: the digest pointer is a kernel local that is
dead by the time the kernel returns, and with more than one erroring call every
leaked block but at most the last is unreachable from any frame. `win_len = 1`
is the sharpest row — a **one-byte** block, reported.

---

## 4. Two things the kernel would have got wrong, both caught by a control

**(a) The digest byte must come from `run >> 24`, not from `run`.** The first
`c/kernel.c` wrote `dig[i] = (uint8_t)run`. `run` is a wrapping sum, so its bits
0..7 are a function of the inputs' bits 0..7 alone — and those carry the record
tag, which is `0xA7` on every well-formed window. The digest would have been the
constant sequence `((i+1) * 0xB2) & 0xff` and **the kernel would not have read
its input at all**. It was caught because `model.py` was written with the shift
and the C rung without it, so the two disagreed on the very first comparison.
`inputs/gen.py::_check_data_dependent` now makes that a standing control: two
payloads of the same shape and different contents must not produce the same
checksum. On the shipped generator it prints

```
data-dependence control: two payloads, same shape ->
    16882046685265576958 != 7036701885568957162  OK
```

**(b) The scratch must be input-sized and the fold must run backwards, or the
compiler deletes the allocation — and one compiler does.** `.temp/t104/elide/`,
LINKED binaries (a `.o` hides the call behind a relocation), counting
`call <malloc>`/`call <free>` inside the kernel symbol:

```
                                   gcc O0..O3     clang O0    clang O1..O3
k_arr   malloc(len*8), two passes       2 2 2 2           2          2 2 2
k_one   malloc(8), store then load      2 2 2 2           2          0 0 0
k_cap   malloc(CAP*8) fixed, chunked    2 2 2 2           2          2 2 2
CONTROL k_dead: written, never read     2 2 2 (O1..O3)               0 0 0
```

**clang deletes a heap allocation whose stores it can forward, at `-O1` and
above; gcc deletes none, not even the dead one.** The control (`k_dead`) fires
on clang, so the instrument is live. Since clang's backend is rustc's backend at
the same version (TOOLCHAIN.md), a one-word context is **not a viable p42
kernel** — the Rust rungs would lose the allocation and the leak with it. The
shipped shape is `k_arr`: input-sized, written forward, read backward.

---

## 5. What the scratch costs, per rung

Kernel-**exclusive** `Ir` per call, `-O3`, inline mode **`isolated`**, from
`results/p42-goto-cleanup.json` (60 000 calls on `small`, 1 500 on `large`):

| rung | small, win 97 | large, win 4096 | Ir/element small | Ir/element large |
|---|---|---|---|---|
| R1 c-gcc | 1873.00 | 77854.00 | 19.309 | 19.007 |
| R1h c-gcc-h | **1873.00** | **77854.00** | 19.309 | 19.007 |
| R1 c-clang | 1506.00 | 61487.00 | 15.526 | 15.012 |
| R1h c-clang-h | 1510.00 | 61492.00 | 15.567 | 15.013 |
| R2 safe_naive | 1850.00 | 75826.00 | 19.072 | 18.512 |
| R3 safe_tuned | **1263.00** | **50745.00** | 13.021 | 12.389 |
| R4 unsafe | 1461.00 | 59441.00 | 15.062 | 14.512 |
| R5 verus | 1461.00 | 59441.00 | 15.062 | 14.512 |

**What each difference is, and what kind of thing it is:**

| | small | large | |
|---|---|---|---|
| **R1 − R1h, gcc** | **+0.00** | **+0.00** | the leak is FREE on the success path, exactly |
| **R1 − R1h, clang** | **−4.00** | **−5.00** | ⚠ the LEAKING rung is CHEAPER; mechanism below |
| R3 − R4 | −198.00 | −8696.00 | safe-tuned beats unsafe -- the flattering direction, section 9 |
| R2 − R4 | +389.00 | +16385.00 | `vec![0u8; len]` + indexing against raw |
| **R5 − R4** | **+0.00** | **+0.00** | the `identity` pin's tautology, kernel-exclusive |
| R1(gcc) − R4 | +412.00 | +18413.00 | |
| R1(clang) − R4 | +45.00 | +2046.00 | same backend, and it shows |

### ⚠ R1 − R1h is `0.00` on gcc and NOT on clang, and the mechanism is a branch merge

Both rungs execute the same success path, so a difference there is a code-layout
effect and not work. It is: at `-O3` clang's **hardened** kernel is 121
instructions to the buggy one's 119, because once the tag test's failure branch
targets the same label as the `len == 0` early exit, clang **merges the two
conditions branchlessly**:

```
   buggy                          hardened
   cmpb   $0xa7,(%r15,%r14,8)     cmpb   $0xa7,(%r15,%r14,8)
   jne    <kernel+0x3b>           setne  %cl
   test   %rbx,%rbx               test   %rbx,%rbx
   je     <kernel+0x33>           sete   %dl
                                  or     %cl,%dl
                                  je     <kernel+0x35>
```

and the merged form is on the path every successful call takes. gcc does not
merge them and pays nothing. **So "what the leak costs" is `0.00` on one
compiler and `−4.00`/`−5.00` on the other, and neither number is about
memory safety.** This is why the axis was declared as a behaviour matrix in
`spec.md` before anything was measured.

### ⚠ `R5 − R4 = 0.00` is convention-dependent, and the two conventions disagree

Kernel-exclusive `Ir` gives **exactly `+0.00` on both inputs**, which is the
tautology the `identity` pin forces. The **whole-program marginal** — the other
convention this project uses — gives `1617.00 / 59834.00` for R4 and
`1617.00 / 59803.00` for R5: **`0.00` on `small` and `−31.00` on `large`**, from
two binaries whose kernels are byte-identical (`md5_fn 1ab63fde449d` both). The
31 instructions are outside the kernel symbol; they are the binary-layout term
`patterns/p01-array-sum/spec.md`'s `collapse.note` documents (p02's `0.02` from
a differently-aligned destination buffer). **Quote `R5 − R4` in the
kernel-exclusive convention, or say which one you meant.**

---

## 6. ⚠⚠ VERUS AT THE PINNED VERSION CANNOT STATE LEAK-FREEDOM. This is p42's central result.

`.tasks/TASK_104.md` §2 asked *"Can Verus state 'this allocation is released on
every path, including the error path'?"* and offered `p27`'s `Tracked<Dealloc>`
as a precedent. **The answer is no, and the precedent does not transfer.**

`controls/affine_leak.rs` is the experiment, committed so it can be re-run:

```
$ ./verus_run.py patterns/p42-goto-cleanup/controls/affine_leak.rs
verification results:: 2 verified, 0 errors
```

`leaky` allocates 64 bytes and returns on an error path **without deallocating**;
both tracked tokens — the `PointsToRaw` and the `Dealloc` — are dropped. Verus
accepts it.

**THE POSITIVE CONTROL, and it fires:**

```
$ ./verus_run.py patterns/p42-goto-cleanup/controls/affine_leak.rs \
      --cfg p42_control_must_fail
error[E0382]: use of moved value: `pt`
error[E0382]: use of moved value: `dl`
error: aborting due to 2 previous errors
```

The tokens are **move-only** — using one twice is rejected — so the probe is not
vacuous. Move-only plus droppable is exactly **affine**, not linear.

**What p27 actually proves, and what it does not.** `Tracked<Dealloc>` makes a
deallocation *legal* — no double free, no use-after-free, right size and
alignment and provenance. Nothing makes it *happen*. p27's own leak-freedom
claim rests on a `required` **spelling pin** in its `spec.md` and on reading the
epilogue, not on its proof. So:

> **p42 is the first pattern in this tree whose R5 proof does not cover the
> pattern's own bug class.** The `identity` pin certifies that R4 and R5 are the
> same machine code; it does not certify that either is leak-free. What stands
> behind leak-freedom on the Rust side is **Miri** (section 10) and the reader.

⚠ **This is a CONCLUSION, and the MECHANISM is only half-isolated.** What is
measured is that a dropped `Dealloc` verifies. What is *not* established is that
no encoding could express the obligation. Two routes were considered and not
built, and they are named here so nobody re-derives them:

- a **ghost conservation ledger** threaded through the kernel as a
  `Tracked(&mut …)` parameter, with the trusted `dig_alloc`/`dig_free`
  contracts incrementing and decrementing it and the kernel ensuring it is
  balanced. This would be a genuine obligation — a path that skips `dig_free`
  leaves the counter at +1 and the postcondition fails — but it changes the
  kernel's **signature**, and the kernel signature is pinned across all six
  rungs. **Not built. OPEN.**
- **a linear (rather than affine) tracked mode**, which the pinned Verus does
  not appear to have. `../LearnVeri/_VERUS_DOC_/` calls `tracked` *"linear ghost
  state"* in one line of `state_machines/src/intro.md`, and the measurement
  above says that is loose language: it is affine. **Not exhaustively searched.
  OPEN.**

---

## 7. TCB tally

**Five `external_body` items in `verus.rs`.** `check.py::_is_trusted` counts an
item as trusted when it is `external_body` **and** carries either a non-empty
`ensures` or an `unsafe` in its body. Three qualify:

| item | why trusted | twin |
|---|---|---|
| `v_get_unchecked` | `ensures r == v@[i]` over an unchecked read | `v[i]`, checked |
| `dig_alloc` | `ensures` about a real allocation; `unsafe` body | `vstd::raw_ptr::allocate` |
| `dig_free` | no `ensures`, but an `unsafe` body | `vstd::raw_ptr::deallocate` |

The other two — `load_input` and `emit` — are `external_body` with **no**
`ensures` and no `unsafe`, exactly as every pattern's are: an `ensures` on
`load_input` would be an axiom about the contents of a file.

**Hand-written axioms: 0.** `vparse.axiom_decls(verus.rs)` returns `[]`; the
contract declares `verus.axioms = {"verus.rs": 0}` and the gate re-derives it.
p42 uses vstd's `assume_specification`s for `<*mut T>::addr` and
`<*mut T>::with_addr`, but those are vstd's, not this pattern's.

**Verus itself: `15 verified, 0 errors` shipped, `18 verified, 0 errors` under
`--cfg slb_twin`** (15 + the three twins).

## SLB-TRUSTED-ARGUMENT verus.rs v_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The twin is `v[i]` — the
same read with Rust's own bounds check in front of it. A `requires` too weak to
license `*v.get_unchecked(i)` is too weak to license `v[i]`, and Verus *can* see
the second one: weaken the pair to `i <= v@.len()` and the twin fails with
*"index in bounds for this access"*. That is the only mechanism in this project
that judges the STRENGTH of a trusted precondition rather than its triviality —
stages 5a and 5c-req both accept `i <= v@.len()` happily (TASK_008_REVIEW).

**(b) Is the `ensures` complete with respect to what the body does?** The body
performs exactly one operation, a read of `v[i]`, and the single `ensures`
clause states its value. There is no second access and no write, so there is
nothing the contract fails to describe. ⚠ This is the clause TASK_009_REVIEW's
x4 attacks — a body that *also* read `i + 1` would pass the contract pin, the
twin and the `--cfg slb_twin` run unchanged — and the backstop for it is Miri on
`unsafe.rs`, which p42 declares `required: true` (section 10).

**(c) Does each clause mean the same in both configurations?** `v@`, `.len()`
and `[i as int]` are vstd's slice view and do not depend on `slb_twin`; the
token `slb_twin` appears nowhere but on the twin's own `#[cfg]`, which the gate
checks.

## SLB-TRUSTED-ARGUMENT verus.rs dig_alloc

**(a) Is the twin's body the right checked stand-in?** The twin's body is
`allocate(size, align)` — **`vstd::raw_ptr::allocate` itself**. This item is a
copy of vstd's, and the twin run proves the copy is no stronger than the
original: if this crate's `requires` were weakened or its `ensures`
strengthened, the twin would stop verifying against vstd's contract. That is a
stronger check than any hand-written stand-in could be, because the "checked
stand-in" is upstream's own reviewed specification.

**The copy exists for codegen and only for codegen** (p27's finding, NOTES 5a
there): vstd carries no `#[inline]` on `allocate`, so calling vstd's directly
emits a GOT-indirect cross-crate `call` that `unsafe.rs` cannot produce, and the
R4/R5 pair measures `differ` at both optimisation levels. Every difference from
vstd is a **weakening or a respelling**: the body writes `std::alloc::` where
vstd writes `::alloc::alloc::`, and **one `ensures` conjunct is dropped** —
`pt.0.addr() as int % align as int == 0` — because stage 5c measured that
nothing depends on it (section 0, edit 1). Nothing is added.

**(b) Is the `ensures` complete?** The body performs two operations: it builds a
`Layout` with `from_size_align_unchecked(size, align)` and calls
`std::alloc::alloc(layout)`, aborting if the result is null. The `requires`
covers the first — `valid_layout(size, align)` is exactly
`Layout::from_size_align_unchecked`'s documented safety condition — and
`size != 0` is `alloc`'s. The four surviving `ensures` conjuncts describe
everything the caller can observe: the extent of the returned `PointsToRaw`, the
non-overflow of `addr + size`, the `DeallocData` that pairs with it, and the
provenance equality that ties the raw pointer to the permission. The block is
returned **uninitialised**, which `into_typed` requires and which is what
`is_range` on a `PointsToRaw` (rather than a `PointsTo`) says.

**(c) Does each clause mean the same in both configurations?** Every clause is
built from vstd's own spec functions and both configurations are compiled
against the same pinned vstd.

## SLB-TRUSTED-ARGUMENT verus.rs dig_free

**(a) Is the twin's body the right checked stand-in?** The twin's body is
`deallocate(p, size, align, pt, dealloc)` — **`vstd::raw_ptr::deallocate`
itself**, with the same force as `dig_alloc`'s twin and for the same reason.
Same codegen motivation.

**(b) Is the `ensures` complete?** There is no `ensures`, and that is correct
rather than lazy: the item's whole semantic content is that it **consumes** the
`PointsToRaw` and the `Dealloc`. The body performs one operation,
`std::alloc::dealloc(p, layout)`, and the six `requires` conjuncts — vstd's own
— cover every parameter: `p`, `size` and `align` through the four `dealloc@.*`
equalities, and both permissions through `pt@.is_range(..)` and the two
provenance equalities.

⚠⚠ **AND HERE IS THE ONE THING A READER MUST NOT INFER.** Consuming the tokens
means a caller cannot *use* the block afterwards. It does **not** mean the
caller is obliged to call this item at all. `Tracked<Dealloc>` is affine at the
pinned Verus, so a path that simply drops it verifies — measured, with a
control, in section 6. **This item's contract is about the legality of a
release, never about its occurrence, and no clause of it could be strengthened
to say otherwise.** That is why p42's leak claim on the Rust side rests on Miri
and not on this contract.

**(c) Does each clause mean the same in both configurations?** As for
`dig_alloc`: vstd's own spec functions, one pinned vstd, and `slb_twin` appears
nowhere but on the twin's `#[cfg]`.

---

## 8. The `identity` pin, and the two edits it cost

`unsafe ≡ verus`, **`O0: norel`, `O3: exact`**, which is what every other
pattern in the tree pins. It took two edits to `unsafe.rs`, and **both were
found by the pin dropping, not by reading**:

**(1) `O3` read `differ` (120 vs 122 instructions) until `unsafe.rs` bound `q`
and `b` in verus.rs's order.** R4 first wrote `dig_write(dig_at(p, base, i),
(run >> 24) as u8)` as one expression; R5 *must* bind `q` before `run` is
updated, because the permission split that licenses the store happens between
them. The two are the same program and not the same object code — the complete
difference:

```
R4  lea    0x1(%r14),%r8            R5  lea    (%r15,%r14,8),%r8
                                        add    $0x8,%r8
    mov    -0x8(%r15,%r8,8),%r9         mov    -0x8(%r8,%rdx,8),%r9
    mov    (%r15,%r8,8),%rcx            mov    (%r8,%rdx,8),%rcx
    add    $0x2,%r8                     (absent)
```

LLVM strength-reduces the write loop differently: R5 keeps a byte cursor in
`%r8`, R4 keeps an index. Two instructions.

**(2) `O0` read `differ` (106 vs 104) until `dig_write` spelled the store
`*q = b` instead of `core::ptr::write(q, b)`.** The complete difference:

```
R4  mov    %rax,0x48(%rsp)          R5  mov    %rcx,0x48(%rsp)
    mov    0x48(%rsp),%rax              mov    0x48(%rsp),%rcx
    shr    $0x18,%rax                   shr    $0x18,%rcx
    lea    RIP,%rdx                     mov    %cl,(%rax)
    movzbl %al,%esi
    call   <core::ptr::write>
```

`core::ptr::write` is `#[inline]`, not `#[inline(always)]`, and survives as a
CALL at `-O0`; vstd's `ptr_mut_write` is `#[inline(always)]` over an
already-optimised precompiled vstd and becomes a bare store.

⚠ **This is p27's finding and TASK_104 reproduced it by writing it BACKWARDS.**
p27's note says `*base = v` is the spelling to use *because* `core::ptr::write`
leaves a call; p42's first `unsafe.rs` doc comment asserted the opposite
("`core::ptr::write` … are the spellings vstd uses") and the code followed the
comment. **A correction that names two spellings can be applied with the names
swapped, and the gate is what caught it.**

**One clean negative, so nobody re-runs it:** replacing R4's `dig_alloc` return
type with `(*mut u8, (), ())` to mirror R5's erased three-tuple changes
**nothing** — `O0` stayed `differ [106,106,504]` vs `[104,104,488]` and `O3`
stayed `exact`. The tuple was never the difference. Reverted.

### R1 vs R1h: the leak costs `0.00`, and the whole difference is one field

`c/kernel.c` and `c/kernel_hardened.c` compile to the **same 49 instructions at
`-O3`**, and the complete diff of their normalised disassembly is one branch
target:

```
-    193b:	jne    19a1 <kernel+0x91>      # skips `call free@plt`
+    193b:	jne    199c <kernel+0x8c>      # lands on it
```

Same instruction count, same bytes elsewhere, same addresses. So **the leak is
free on the success path, exactly, and it is one displacement field wide.**

⚠⚠ **AND THIS IS A NEW DEFECT IN PROBE 2, IN THE DIRECTION THAT KILLS ROWS.**
`.temp/t102/b4_norm.py` (the "fixed" normaliser) and `.temp/t94/knorm.py` both
rewrite a self-relative target `<kernel+0x91>` to `<SELF>` and **discard the
offset**, so *two kernels that differ only in which of their own labels a branch
targets normalise identically*. Run on p42's two C rungs, that form reports them
as **one rung** (`norm=45d32052d67e` for both). They are not: one leaks.

> **Probe 2's normaliser must keep the self-relative OFFSET.** The offset is
> measured from the symbol's own start, so it is layout-independent — dropping
> it buys nothing and loses exactly the class of bug whose whole expression is a
> branch target. With `<SELF+0xNN>` kept, p42's five kernels read `49 / 49 / 108
> / 139 / 120` instructions and **five distinct normalised texts**, C-buggy and
> C-hardened included. `.temp/t104/probe2.py` is the corrected form.

**This is the fourth defect found in probe 2** (object-file relocations →
false positive; linked md5 → false negative; `knorm.py`'s padding → false
negative; this one → false negative). It is a **kill criterion**, so a false
negative manufactures a refusal.

---

## 9. Both sides searched: the R3 and R4 spelling spans

⚠ p42 lands in the **flattering direction** — safe-tuned Rust is cheaper than
unsafe Rust here — which is the trap that has caught this project's patterns
repeatedly, so both sides were searched to the same depth and the count is
stated: **four spellings per side**, all generated from a shipped rung by textual
substitution in `controls/spellings.py` so that no variant can drift from the
rung it varies. Every variant is checked to print the shipped checksum before it
is measured. Numbers in section 11.

⚠ **Two of the four R4 variants are NOT admissible rungs**, and the reason is
`.memory/01-ladder.md`'s "R4 is chained to the prover": R4 must have a
byte-identical R5 twin that Verus verifies, and the pinned vstd specifies
`<*mut T>::addr` and `<*mut T>::with_addr` and **not** `<*mut T>::add` or
`offset` (`grep -n assume_specification ~/tools/verus/vstd/raw_ptr.rs` — two
pointer-method entries, both in the `pointer_specs!` macro). So `r4_add` and
`r4_movptr` cannot be p42 rungs at all. `r4_endptr` uses only `with_addr` and
`<*mut T as PartialEq>::eq`, both specified, so it is admissible **in
principle** and **nobody has built its R5** — that is p42's open question and it
is stated as one rather than assumed away. p42 therefore holds its R4 endpoint
**fixed by fiat** at the shipped, verified spelling and publishes the span,
which is what `.memory/01-ladder.md` asks for instead of a pair interval.

**A clean negative worth keeping:** `with_addr` is **not** the pessimisation.
`r4_add` — the same rung with `p.add(i)` instead of `p.with_addr(base + i)` — is
identical to the shipped rung to the instruction on `small`. The gap between R4
and R3 is the number of induction variables per loop, not the addressing
spelling.

---

## 10. Miri, and how narrowly to read the row

⚠ **`harness/check.py` passes no `MIRIFLAGS` and no `-Zmiri-seed`**, and
`.memory/00-environment.md` records that Miri's alignment check is
**seed-dependent** — the same source clean on seeds 0 and 2 and reporting UB on
1 and 3. So a green gate row means *"no UB at whatever seed the default
happened to be"*, and this file does not write "Miri: N of N, no UB" as though
it were seed-independent.

`controls/miri_seeds.sh` sweeps **seeds 0 through 7** over every input with
`n_iters` clamped to 4 (the gate's own `MIRI_PROBE_ITERS`), and it carries a
**positive control that must fire**: the shipped `unsafe.rs` with the ERROR
PATH's `dig_free` deleted, generated by substitution so it cannot drift. Since
Verus cannot state leak-freedom (section 6), **Miri's own leak report is the
only mechanical check p42 has that R4 does not leak** — and an unexercised
checker is indistinguishable from a satisfied one. Results in section 11.

⚠ One trap this control fell into and climbed out of: `adversarial-shortlen.bin`
exits **5** by design, and the first version read `rc != 0` as UB, so every seed
looked like a failure. The script now reads Miri's **stderr**, which is where
`Undefined Behavior` and `memory leaked` are reported, and treats the exit code
as information only.

---

## 11. Measured results

### 11z. What the gate says

**0 failures.** The verdict STRING is `PASS` or `PASS-WITH-BLOCKED-ROWS`
depending on whether Miri finishes `large.bin` inside `check.py`'s 180 s
`MIRI_TIMEOUT` — which is wall-clock and therefore run-dependent, so this file
does not transcribe it (`.tasks/PROTOCOL.md` rule 6's newest lesson: a number
only a rebuild can produce must not live in a file the rebuild re-hashes, and
`NOTES.md` is in the gate record's `source_sha256`). `spec.md`'s
`miri.blocked_reason` declares that row in advance, and a timeout is recorded as
BLOCKED, never as a pattern failure.

**Five shouts, all expected and all permanent:** four are stage 0b saying that
`idiom.forbidden[0..3]` backtick no spelling — correct, they forbid a STRUCTURE,
and the `why` says so in the gate's own words — and one is the Miri block above.

### 11a. The ladder

Section 5 has the table. Wall clock, `-O3 isolated`, min of 30 interleaved reps
on cpu 3, **secondary to `Ir` and quoted only as a sanity check**: `small`
10.86–12.44 ms, `large` 14.05–15.80 ms across the eight cells, with `safe_naive`
slowest and `c-clang`/`c-clang-h` fastest on both — the same ordering the `Ir`
column gives except that `safe_tuned`'s `Ir` win does not show up in wall clock
(10.93 ms against `unsafe`'s 10.91 ms on `small`), which is what a
1.3 %-of-`Ir` difference under a 10 ms process looks like.

### 11b. The spelling spans -- four per side, whole-program marginal `Ir`/call, `-O3 isolated`

| variant | small (97) | large (4096) | admissible as a p42 rung? |
|---|---|---|---|
| **r4_ship** (index + `with_addr`) | **1617.00** | **59834.00** | ✅ shipped, Verus-verified |
| r4_add (`p.add(i)`) | 1617.00 | 59834.00 | ❌ no vstd spec for `<*mut T>::add` |
| r4_movptr (cursor + counter) | 1491.00 | 54710.00 | ❌ same |
| **r4_endptr** (cursor vs end ptr) | **1455.00** | **53174.00** | ⚠ in principle YES; **R5 unbuilt** |
| **r3_ship** (`with_capacity`+`extend`+`rev().fold`) | **1419.00** | **51138.00** | ✅ shipped |
| r3_revidx (`extend` + index fold) | 1627.00 | 59845.00 | ✅ |
| r3_zeroed (`vec![0;len]`+`clear`+`extend`) | 1572.00 | 55298.00 | ✅ |
| r3_push (`with_capacity`+`push`+index fold) | 2634.00 | 102846.00 | ✅ |

**R4 span 1455 … 1617 (small), 53174 … 59834 (large). R3 span 1419 … 2634
(small), 51138 … 102846 (large).**

⚠⚠ **THE TWO SPANS OVERLAP, and saying so is the point.** `r3_revidx` at
1627.00 is *dearer* than every R4 spelling measured, and `r3_push` is dearer by
63 %. What survives the search is the narrower claim:

> **cheapest R3 found (1419.00 / 51138.00) is below cheapest R4 found
> (1455.00 / 53174.00), by 36.00 and 2036.00** — so "safe-tuned Rust beats
> unsafe Rust here" is not an artefact of an unsearched R4 side. It is a
> statement about the two INFIMA, on eight spellings, and it is 2.5 % on `small`
> and 3.8 % on `large`.

✅ **Clean negative: `with_addr` is not the pessimisation.** `r4_add` measures
identically to the shipped rung at both inputs. The gap between R4 and R3 is the
number of induction variables per loop, not the addressing spelling — and the
one R4 spelling that gets to one induction variable per loop (`r4_endptr`)
closes 162 of the shipped 198.

### 11c. Miri

`controls/miri_seeds.sh`. **Seeds 0,1,2,3,4,5,6,7 over the nine small inputs:
no UB, no leak, at every seed.** `adversarial-wincap.bin` (200 000 words) is
clean at the default seed; **`large.bin` is BLOCKED — it exceeds 180 s under
interpretation**, which is `check.py`'s own `MIRI_TIMEOUT`, so that one input is
unchecked and the others are not.

**THE POSITIVE CONTROL FIRES**, and this is the row that matters, because it is
the only mechanical check p42 has that R4 does not leak (section 6):

```
adversarial-notag        rc=1  error: memory leaked: alloc7447  (Rust heap, size: 32, align: 1)   4 leaked
adversarial-mixed        rc=1  error: memory leaked: alloc13213 (Rust heap, size: 24, align: 1)   2 leaked
adversarial-win1         rc=1  error: memory leaked: alloc3233  (Rust heap, size: 1,  align: 1)   4 leaked
small.bin                rc=0  no leak
```

on the shipped `unsafe.rs` **with the error path's `dig_free` deleted**. The
leaked counts are what `n_iters = 4` predicts: 4 of 4 calls error on `-notag`
and `-win1`, 2 of 4 on `-mixed`, 0 of 4 on `small`.

### 11d. ⚠⚠ The per-element rate is BAND-LOCAL. Do not publish it as a law.

`controls/sweep.py` fits `Ir/call = a + b·win_len` on **band A, win 64..79**, and
then predicts band B (512..527) and both shipped inputs. All four residue
classes mod 4 are in each band.

| cell | band-A fit | max in-sample resid | worst band-B resid | `small` (97) | `large` (4096) |
|---|---|---|---|---|---|
| c-gcc | `184.177 + 18.91424·w` | 1.36 | **+39.23** | +2.14 | **+582.12** |
| c-gcc-h | `184.177 + 18.91424·w` | 1.36 | +39.23 | +2.14 | +582.12 |
| c-clang | `192.777 + 15.01424·w` | 3.86 | +10.96 | −0.16 | +175.92 |
| safe_naive | `285.464 + 19.51332·w` | 9.42 | +312.75 | −19.26 | +166.96 |
| safe_tuned | `176.014 + 13.06332·w` | 12.57 | +320.94 | −24.16 | **−2545.39** |
| unsafe | `203.161 + 14.59274·w` | 5.21 | +47.05 | −1.66 | −141.00 |
| verus | `203.161 + 14.59274·w` | 5.21 | +47.05 | −1.66 | −172.00 |

**Every cell's out-of-band residual is 3× to 25× its in-sample residual**, and
`safe_tuned` — the cheapest rung, the one a headline would quote — mispredicts
its own SHIPPED `large.bin` by **−2545 `Ir`/call**. That is p23's lesson
reproduced on a new row: an in-sample residual of 12.57 said nothing at all.
**p42 therefore publishes two measured points per rung and no rate.**

⚠ **`large.bin`'s residual is not comparable to band B's**: it is a different
array (1 000 000 words against 4 096), so it moves the memory system as well as
the window. Band B is the honest out-of-band test and it is the one that
already fails.

### 11e. The MECHANISM of 11d is OPEN, and one candidate is REFUTED

Two isolations were run, and the obvious explanation is **not** the answer.

**Refuted: the allocator's size class.** The kernel calls `malloc(len)` once per
call, so the request size moves with the window; glibc's bins change under the
fit. Isolation: the same C program with `malloc(len)` replaced by
`malloc(4096)` — a constant size, and only `dig[0..len)` is ever touched, so the
checksum is unchanged (checked).

```
var   malloc(len)    fit = 184.177 + 18.91424*w   in-sample 1.356   band-B resid +37.61 .. +39.23
fixed malloc(4096)   fit = 377.177 + 18.91424*w   in-sample 1.356   band-B resid +37.61 .. +39.23
```

**Identical band-B residuals and an identical slope.** Fixing the request size
moves the INTERCEPT by +193 `Ir` (that part *is* the size class: 4 096 bytes is
past glibc's tcache limit and 64..79 is not) and does **nothing** to the
deviation. The size class is not it.

**Second isolation: it is smooth curvature, not a step.** Measured against band
A's fit at twelve window lengths on the shipped `c-gcc`:

```
   w      96    128    160    192    224    256    320    384    448    512   1024   2048
resid  +2.06  +5.52  +7.54  +9.57 +13.03 +15.06 +21.27 +27.47 +31.52 +37.73 +81.64 +563.74
```

Monotone from `w = 96` upward, so `Ir(w)` is mildly **superlinear**, with a
sharper break between 1 024 and 2 048.

⚠ **What causes the superlinearity is NOT ESTABLISHED and is left OPEN.**
`.tasks/PROTOCOL.md`'s rule is that a phenomenon and its cause carry different
evidence: what is measured here is that a band-local fit does not transfer, and
that one plausible cause does not explain it. **Do not attribute it.**
