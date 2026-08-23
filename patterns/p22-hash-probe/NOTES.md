# p22 — open-addressing hash probe: findings

Contract: `spec.md`. Summary: `README.md`. This file is the evidence.

> ⚠ **p22's gate verdict is `PASS-WITH-BLOCKED-ROWS`, not `PASS`, and that is
> correct.** `model.py` declares `adversarial-full.bin` non-terminating, and
> `harness/check.py` blocks a declared-hang input's Miri row up front rather than
> waiting out `MIRI_TIMEOUT`. p01 is the only other pattern in the tree that
> lands there. §11 has the disclosure and a harness finding that goes with it.

> **`slb-contract` sha256, as first written:**
> `1f29b02eac0bf442d646cdcc03b83ced321a25b3f0c74109dc1c1028831c1d71`
> — written by `controls/mkcontract.py` before any measurement was published.
> **It changed once, to
> `044f02cded64694e54484df7b69cda3154019e0d350cf049e55dac07199bd5da`**, and §11c
> says exactly what moved and why. The final value is in
> `results/gate/p22-hash-probe.json`.

## 0. §0 — the bug class and the harm, settled before any rung was written

`.memory/06-catalogue.md` predicted: *"the bug is a probe loop that never
terminates on a full table: memory-safe, a real DoS, and safe Rust does not
prevent it either — R2, R3 and R4 all hang, and only R5 catches it, as a
`decreases` obligation."* **Four claims. All four were measured before any rung
existed**, on standalone probes in `.temp/p22/probe/` (`probe.c`,
`probe_rs.rs`). Verdict: **two upheld, one reframed, one upheld with a
qualification the catalogue did not have.**

### 0a. The hang is real, deterministic, and survives `-O3` on both compilers

C11 6.8.5p6 lets a compiler assume a loop with a non-constant controlling
expression terminates, so *"the C rung hangs at `-O3`"* is not obvious and had to
be measured. `probe.c`, TABCAP 64, distinct keys `1,2,3,…`, `timeout 5`:

| build | `n = 64` (fills the table) | `n = 65` (first absent key) | `n = 200` |
|---|---|---|---|
| gcc `-O0` / `-O3` | exit 0, `10975232390226517432` | **rc 124** | **rc 124** |
| clang `-O0` / `-O3` | exit 0, same | **rc 124** | **rc 124** |
| all four **with the guard** | exit 0, same | exit 0, `8190810770250117165` | exit 0 |

**4 of 4 hang.** `i`'s final value is used after the loop, so neither LLVM's
`mustprogress`-driven loop deletion nor gcc's touches it. On the shipped tree the
same holds: **8 of the 32 built cells do not terminate on
`adversarial-full.bin`** — `c-gcc` and `c-clang` × {O0, O3} × {isolated, whole}
— and the gate records all eight (§5).

### 0b. Safe Rust does not help — measured on the shipped rungs, three ways

`controls/gen_controls.py --run hang --miri` derives `r2_noguard`, `r3_noguard`
and `r4_noguard` from the shipped `safe_naive.rs`, `safe_tuned.rs` and
`unsafe.rs` by **one exact-string substitution**, asserted to hit exactly once:

```
'if k != EMPTY && nfill < TABCAP {'   ->   'if k != EMPTY {'
```

| control | `small.bin` | `adversarial-nearfull.bin` | `adversarial-full.bin` |
|---|---|---|---|
| `r2_noguard` `-O0` / `-O3` | `12413078541623012263` | `1685533861422832768` | **rc None, `<timeout after 8s>`** |
| `r3_noguard` `-O0` / `-O3` | same | same | **rc None** |
| `r4_noguard` `-O0` / `-O3` | same | same | **rc None** |
| `c_asan` (gcc `-O1 -fsanitize=address,undefined`) | clean, exit 0 | clean, exit 0 | **rc None, stderr EMPTY** |
| Miri on `r2_noguard` | — | exit 0, **no UB** | **did not terminate in 90 s, no diagnostic, no output** |

Six safe-Rust cells hang, at both optimisation levels, with **zero** `unsafe`
anywhere in them. ASan + UBSan on the C rung is **silent**; Miri on the safe-Rust
port is **silent**. Every access is `tab[i]` with `i` reduced modulo TABCAP, so
there is no memory error for either instrument to find.

**This is the pattern's spine, and it is a measurement rather than an argument.**

### 0c. …but the catalogue's headline is a claim about a SPELLING, and it is stated that way

The manager named this as the call least likely to survive §0, and the worry is
**half right**. A probe written with a bounded trip count —

```rust
for _ in 0..TABCAP { if tab[i] == EMPTY || tab[i] == k { break } i = (i + 1) % TABCAP }
(0..TABCAP).map(|j| (start + j) % TABCAP).find(|&i| tab[i] == EMPTY || tab[i] == k)
```

— **does terminate**, at `-O0` and `-O3`, and both spellings are idiomatic safe
Rust (measured in `.temp/p22/probe/probe_rs.rs`; both give the guarded answer on
every input tried). So *"safe Rust does not help"* is **not** *"every safe Rust
programmer hangs"*. What survives, and what p22 publishes, is narrower and
checkable:

> **Nothing on this ladder EMITS the capacity check.** In p02, p05, p16 and p17
> the safety line is a bounds check the language inserts for you and charges you
> for. Here the safety line is `nfill < TABCAP`, and `c/kernel_hardened.c`,
> `safe_naive.rs`, `safe_tuned.rs`, `unsafe.rs` and `verus.rs` each write it out
> **by hand** — five times, once per rung that has it. The rung that omits it
> hangs whatever language it is written in.

The bounded spelling is **forbidden by `spec.md`** for a reason that is semantic
and not stylistic: on a full table it is a **different function** — it finds a
key that is present, where the shipped semantics rejects every operation once
`nfill == TABCAP` and folds `SENT`. Shipping it in one rung would put a semantic
difference inside p22's cost column. It is measured as a control instead
(`r3_bounded` and `r3_bounded_kept`, §8), and what p22 therefore publishes is
**what the proof buys over the bound**, which is the smaller, honest result.

### 0d. The catalogue's "R2, R3 and R4 all hang" is REFRAMED, not upheld

It is **true of a mechanical port** (§0b, measured) and **false of the shipped
ladder**, and the shipped ladder is right:

* `.memory/01-ladder.md`'s rung table puts the bug in **R1 only** — *"written the
  way a competent systems programmer writes it, **including** the bug class the
  pattern is about"*. Only R1's definition mentions the bug. Every other pattern
  in this tree follows it (p27: R1 omits the liveness conjunct, all four Rust
  rungs have it).
* A hanging R3 beside a terminating R4 would (i) make the rungs semantically
  unequal, which is `PROTOCOL.md`'s own reviewer-checklist blocker, and (ii)
  force `identity: differ`, breaking an **18-of-18** invariant
  (`.memory/04-verus.md`) and with it ladder finding 1 — on the one pattern
  whose whole Verus result is that the proof costs nothing.
* It would also read as *"unsafe Rust is safer than safe Rust"*, which is not the
  finding and is not true.

So: **R1 omits the conjunct and hangs; R1h and R2–R5 carry it; the "safe Rust
does not help" half is carried by three shipped, measured controls.** That is a
stronger form of the claim than a single hanging rung would have been, because it
does not depend on which safe spelling is chosen: R2's indexed loop, R3's
iterator and R4's unchecked walk all hang when the conjunct goes.

**Consequence for the harness: 8 hung cells, not the 12–20 the task file
predicted.** The prediction assumed R2/R3/R4 hang as rungs.

### 0e. The Verus route: (a′) — a GHOST measure, not a set and not an exec counter

The task named two routes and asked which worked. **Neither.** What ships is a
third, and it has route (a)'s faithfulness at route (b)'s proof cost:

* **(a) a ghost `Set` of visited slots, `decreases cap - |visited|`** — faithful,
  needs set-cardinality reasoning in the invariant. Not taken.
* **(b) a probe counter in the EXEC code, `decreases cap - probes`** — trivial to
  prove, and it would make the proof *circular with the fix*: the loop would be
  bounded in the object code and the measure would be proving something the loop
  no longer needed proved. **Not taken, and priced** (§8c).
* **(a′) what ships:** a ghost **unwrapped cursor** `u` with the invariant
  `i == u % TABCAP`, plus a ghost **witness** `e` for an EMPTY slot obtained from
  `nfill < TABCAP` through a counting lemma, and `d` the distance from the start
  slot to `e`. `decreases i0 + d - u`. Progress: the guard says `tab[i] != EMPTY`
  and `tab@[e] == EMPTY`, so `i != e`, so `u != i0 + d`, so `u < i0 + d`.

`u`, `e` and `d` are **all ghost**, so the exec code is byte-identical to
`unsafe.rs` and the `identity` pin holds `exact` at O3 (§4). **The proof consumes
the guard `c/kernel_hardened.c` needs anyway; it adds nothing to the program.**

⚠ **And the obligation is not optional, which is the part the catalogue did not
say.** Deleting the `decreases` clause:

```text
error: loop must have a decreases clause
    = help: to disable this check, use #[verifier::exec_allows_no_decreases_clause]
```

**Verus requires a termination measure on every exec loop by default.** The
opt-out is a named attribute — which is why `spec.md` forbids it: without that
entry, *"only R5 catches it"* would be a statement about Verus's defaults rather
than about this tree. `.memory/04-verus.md`'s warning that `decreases b - a`
fails on two-cursor loops is **upheld in its purest form**: a ring cursor
`i = (i + 1) % TABCAP` does not decrease in any direction at all.

## 1. The safety line, and what no language supplies

`c/kernel.c` and `c/kernel_hardened.c` are character-identical apart from the
header comment and:

```c
        if (k != SLB_P22_EMPTY) {                                 /* R1  */
        if (k != SLB_P22_EMPTY && nfill < SLB_P22_TABCAP) {       /* R1h */
```

`nfill < TABCAP` is exactly *"some slot is still EMPTY"*, and an EMPTY slot is
the only thing that stops the probe. It is **not a bounds check**: `i` is reduced
modulo `TABCAP` on entry (`% SLB_P22_TABCAP`) and on every step
(`i = (i + 1) % SLB_P22_TABCAP`), so `tab[i]` is in bounds unconditionally, in
the buggy rung as much as in the hardened one. rustc's check on the safe rungs'
`tab[i]` is dead code that LLVM removes — measured in §4d: `r4_checked_tab`, the
R4 variant with the table indexed *checked*, is **byte-identical to the shipped
R4 at O3** (`md5_fn 4ac4bd132a50`).

That is the whole of why this pattern exists. Ten of the twenty patterns before
it model *"an index or length is not checked against a buffer"*, and on every one
of them safe Rust supplies the missing check. Here it supplies nothing.

## 2. The hang on the shipped binary

`adversarial-full.bin` is one 132-byte window: `nkey = 65`, keys `1..64` (64
distinct values under the pattern's alphabet, filling all 64 slots) and then a
65th key absent from the table.

```
c-gcc    O0/isolated,O0/whole,O3/isolated,O3/whole  exit=None  stderr='<timeout after 2.0s>'  [DID NOT TERMINATE]
c-clang  O0/isolated,O0/whole,O3/isolated,O3/whole  exit=None  stderr='<timeout after 2.0s>'  [DID NOT TERMINATE]
```

and the gate's own confirmation, at ten times the pinned budget:

```
ok   adversarial-full.bin: confirmed -- c-clang O0/isolated still had not terminated
     at 20.0s (10x the pinned budget), so the 2.0s budget is measuring a hang and not
     a slow cell.
```

**`adversarial-nearfull.bin` is the negative control** and it is what makes the
row mean something: 63 distinct keys and then 64 more drawn from the same 63, so
`nfill` stops one short of `TABCAP` and **all 32 cells terminate and agree**,
`c/kernel.c` included. The hang needs a *full* table, not a busy one — and
`maxprobe` on that window is already 20, so it is not that the probe is short.

## 3. Anti-collapse

Every one of the 32 cells shows a real loop, a real memory operand and a body
above the floor. The gate's own caveat applies and is quoted rather than
paraphrased: the derived floor is **105× below the tightest cell measured**, so
stage 3b rules out total collapse and essentially nothing else. What certifies
that the work happened is stage 2 — **all 32 cells agree with `model.py` on
`small.bin`, `large.bin` and `degenerate.bin`**, and `model.py`'s two internal
implementations (the mutating simulation and the fuel-bounded `key_fold`) agree
with each other on every sampled call.

`collapse.probe_inputs` are `small.bin` (132 window bytes, alphabet 32) and
`large.bin` (1028, alphabet 40). They differ in `work_per_call` — which is what
lets the `d(Ir)/d(work)` assertion run at all — **and in load factor**, because
the probe loop's trip count is a function of the alphabet and not of the window
length.

## 4. The numbers

**Kernel-exclusive `Ir` per call**, `-O3 isolated`, from
`results/p22-hash-probe.json` (`measure.py`'s convention for every pattern in
this tree — `.memory/03-measurement.md`). `small.bin`: 128 keys per window,
alphabet 32. `large.bin`: 1024 keys, alphabet 40. **INLINE MODE: `isolated`**,
i.e. the kernel is behind a real call, and every figure in this section is that
mode. (`whole` has no kernel symbol to attribute at `-O3`; the gate's stage 3a
table shows why.)

| cell | small (nkw = 128) | large (nkw = 1024) |
|---|---:|---:|
| `c-gcc` (R1, **the buggy rung**) | 3446.5497 | 28383.9227 |
| `c-gcc-h` (R1h) | 3574.5497 | 29407.9227 |
| `c-clang` (R1) | 3760.3652 | 31852.7932 |
| `c-clang-h` (R1h) | 4400.3652 | 36972.7932 |
| `safe_naive` (R2) | 4674.3652 | 39038.7932 |
| `safe_tuned` (R3) | 4401.3652 | 36973.7932 |
| `unsafe` (R4) | 4399.3652 | 36971.7932 |
| `verus` (R5) | **4399.3652** | **36971.7932** |

### 4a. R4 ≡ R5, to the instruction and to the byte

`unsafe` and `verus` are **equal to four decimals on both bands** and their
`-O3 isolated` kernels are byte-identical (`md5_fn 4ac4bd132a50`, `md5_raw`
equal, `identity: exact`). ⚠ **On p22 that pin carries an extra job:** the
`decreases` measure is built entirely from ghost state (`u`, `e`, `d`), so
`exact` is the statement that **the first termination proof in this tree cost
zero instructions**. Had route (b) been taken — a probe counter in the exec code
— the pair would still have been `exact` but the *object code* would have moved;
§8c prices that.

### 4b. The safety cost, with the mechanism, not just the number

Two clean laws. Both are **matched-spelling differences** — the same input, the
same convention — so the per-process constant cancels exactly, which is why they
have no error bars. The whole-program and kernel-exclusive conventions give the
identical figures for these differences (checked to four decimals).

| difference | small | large | law | evidence |
|---|---:|---:|---|---|
| **R2 − R3** | +273.00 | +2065.00 | **`2·nkw + 17`** | residual **0.00 on 30 of 30** sweep blobs |
| **R3 − R4** (fixed-R4 bound) | **+2.00** | **+2.00** | **2.00 flat** | **32 of 32** blobs, one distinct value |
| R4 − R5 | 0.00 | 0.00 | 0 | byte-identical |

`nkw` is the number of key bytes the kernel actually walks per call,
`min(nkey, len - 4)`, averaged over exactly the calls the marginal differences
(`controls/sweep_ir.py`). **Not `stride - 4`**: the first draft used that and
reported residuals up to 992 against a law whose residual is 0.

**The mechanism for `2·nkw + 17`, decomposed by measurement rather than by
counting** (`-O3 isolated`, whole-program marginal, `controls/gen_controls.py`):

| spelling | small | large | vs the one above |
|---|---:|---:|---|
| `R2ship` — index `buf[off + p]` per key | 4674.6100 | 39185.9600 | — |
| `r2_reslice` — R2 + one reslice, still indexed | 4407.6100 | 37126.9600 | **−(2·nkw + 11)** — the reslice |
| `R3ship` — reslice + `w[4..].iter().take(nkey)` | 4401.6100 | 37120.9600 | **−6.00 flat** — the iterator |

`2·nkw + 11` and `6` sum to `2·nkw + 17`, which is the measured R2 − R3 exactly.
**So the per-key bounds check is worth 2.00 Ir per key and the reslice is what
removes it; the iterator is worth a flat 6.** That is the mechanism, and it is
three measurements rather than an assertion.

**The `Ir` domain**: `nkw ∈ [16, 1024]` and alphabet `nd ∈ [1, 48]`, 32 blobs.
The law is **independent of `nd`** — band `d` holds `nkw = 256` and sweeps `nd`
from 1 to 48, and R2 − R3 is 529.00 on all eleven, while the *level* moves from
8231 to 9788. So the probe loop's trip count, which is entirely a function of the
load factor, contributes **nothing** to the safety delta.

### 4c. ⚠ The additivity extrapolation PASSED, including off the residue class

`.memory/03-measurement.md`'s only out-of-sample test that can fail. Bands `k`
(sweep `nkw`, hold `nd = 24`) and `d` (sweep `nd`, hold `nkw = 256`) are the fit;
band `x` is six `(nkw, nd)` pairs neither band contains, and band `h` is three
length-**heterogeneous** blobs whose regressor is a weighted mean.

**Residual 0.00 on all 6 of band x and all 3 of band h.**

⚠ **And the residue class was checked, because p38's miss was two-thirds a band
sitting at `nw ≡ 0 (mod 8)`.** Every blob in the fit bands has `nkw ≡ 0 (mod 8)`
(16, 32, 48, 64, 96, 128, 192, 256, 384, 512). Band x deliberately includes
`nkw = 100 (≡ 4)` and `nkw = 150 (≡ 6)`, and band h lands at 98.24 (≡ 2), 183.04
(≡ 7) and 124.00 (≡ 4). **All five off-residue points predict exactly.** That is
a clean negative: on p22 the law does not depend on the residue class, and it was
tested rather than assumed.

### 4d. ⚠ THE R4 SIDE IS NOT DEGENERATE, and the shipped pair FLATTERS safe Rust

*"Degenerate as far as this task searched"* has been false on four consecutive
patterns and it is false here too. **The shipped R4 is missing a lever the
shipped R3 already has.**

| R4 candidate | small | large | in contract? | Verus | R4 ≡ R5 at O3 |
|---|---:|---:|---|---|---|
| `R4ship` (shipped) | 4399.6100 | 37118.9600 | yes | `20 verified, 0 errors` | **exact** |
| **`r4_reslice`** — R4 + R3's one reslice, keys still read through `buf_get_unchecked` | **4276.6100** | **36099.9600** | **yes** | **`20 verified, 0 errors`** | **byte-identical, measured** |
| `r4_checked_tab` — table indexed checked | 4399.6100 | 37118.9600 | yes | (n/a) | `md5_fn` identical to `R4ship` |
| `r4_onecmp` — slot read once per probe step | 4399.6100 | 37118.9600 | yes | `19 verified, 1 errors` (failed transplant, not `is not supported`) | `md5_fn` identical to `R4ship` |
| `r4_nomod` — `i + 1; if i == TABCAP { i = 0 }` | 4389.2800 | 37737.8600 | **NO** — `spec.md` pins the `%` spelling | `20 verified, 0 errors` | — |

**`r4_reslice` is a fully admissible R4**: in contract, same checksum on every
input, its R5 twin verifies `20 verified, 0 errors` (the ghost side needs two
extra invariants relating `w@` to `buf@.subrange(off, off+len)` and one
`assert`; all of it erases), and **its R4/R5 pair is byte-identical at `-O3` —
built and diffed, not assumed** (`md5_fn ea06db04c435` on both sides, `md5_raw`
equal). All of it is one command, `controls/gen_controls.py --run mech --ir`,
which regenerates the R5 source from `verus.rs` by three asserted single-string
substitutions. It is

**`1·nkw − 5` Ir/call cheaper than the shipped R4** (123.00 / 1019.00).

Consequences, stated plainly because this is the direction that flatters:

* **`R3 − R4 = +2.00 flat` is a FIXED-R4 bound, R4 held by fiat**, and it is an
  upper bound on `inf(in-contract R3) − R4ship`. It is **not** "the cost of
  safety on p22".
* Against the cheapest admissible R4 found, the same difference is
  **`R3ship − r4_reslice = 1·nkw − 3`** — +125.00 on `small.bin`, **+1021.00 on
  `large.bin`**. On the large band that is **510× the shipped figure.**
* The lever is the **reslice**, and the asymmetry is the whole story: `R3ship`
  reslices once per call and then addresses keys off `w`; `R4ship` addresses them
  off `buf` with `off + p`, one extra instruction per key. R3 was tuned and R4
  was not.
* **The shipped R4 is NOT re-shipped.** `.memory/02-bench-rules.md`: *never
  re-ship a rung because a cheaper in-contract spelling was found.* p22 follows
  p38's and p47's convention (R2 indexes, R3 reslices, R4 uses `get_unchecked`),
  and the span is published instead.

**R3-side span**, cheapest found to dearest found, in contract, `small.bin`:
`R3ship 4401.6100` … `r3_noresl 4411.6100` (R3 with the reslice removed), width
**10.00**. `R3ship` is the cheapest in-contract R3 found.

### 4d-asm. The disassembly behind "the table check is already dead"

`harness/asm.py show <cell>-O3-isolated --sym kernel`, all four Rust rungs:

| rung | insns in the `kernel` extent (`n_fn_nopad`) | mentions of `panic` |
|---|---:|---:|
| `safe_naive` | 107 | **0** |
| `safe_tuned` | 72 | **0** |
| `unsafe` | 74 | **0** |
| `verus` | 74 | **0** |

**No rung has a `panic_bounds_check` call site at `-O3`**, so rustc's check on
`tab[i]` is not merely cheap in the safe rungs, it is absent. The probe body is
the same instruction sequence in R3 and R4:

```
imul $,%r8,%r10       # the hash: * 2654435761
shr  $,%r10           #           / 16777216   -> a SHIFT, so the `/` spelling is free
mov  %r10d,%r9d
and  $,%r9d           #           % TABCAP     -> a MASK, so the `%` spelling is free
movzbl (%rsp,%r9,1),%r11d      # tab[i], no bounds test anywhere near it
test %r11b,%r11b
```

R4's is the same with `-(%rsp,%rbx,1)` as the base. That is the direct evidence
for two claims made elsewhere in this file: `arr_get_unchecked` buys nothing at
`-O3` (§4d), and the contract's `/` and `%` spellings — chosen so the Verus
specification stays inside linear arithmetic — cost nothing against `>>` and `&`
(`spec.md`'s `why`).

### 4e. The C column — and why the compilers disagree by 5×

| difference | small | large | per key |
|---|---:|---:|---|
| `c-gcc-h` − `c-gcc` | +128.00 | +1024.00 | **exactly 1.00 / key** |
| `c-clang-h` − `c-clang` | +640.00 | +5120.00 | **exactly 5.00 / key** |

**The capacity conjunct costs gcc one instruction per key and clang five.** Both
are exact on both bands. The conjunct is *never taken* on either input (the table
never fills), so this is the cost of evaluating a correctly-predicted branch —
and clang pays 5× for it, presumably by restructuring the key loop around it.
This is a **compiler** result, not a language one, and it is why the C-vs-Rust
row below needs both columns:

| | small | large |
|---|---:|---:|
| `safe_tuned` (R3) − `c-clang-h` | **+1.00** | **+1.00** |
| `safe_tuned` (R3) − `c-gcc-h` | +826.82 | +7565.87 |

**Against clang, all four Rust rungs and the hardened C rung are within 2.00
Ir/call of each other** — R3 is 1.00 dearer than clang's hardened C and R4 is
1.00 cheaper. Against gcc they are 827 / 7566 dearer. ⚠ **Neither figure is a
language result**: `c-gcc-h` and `c-clang-h` are the *same C source*, and they
differ by 826 / 7566 themselves. What p22 measures about C is that **gcc compiles
this kernel much better than clang does**, and the Rust rungs land on clang's
number. Nothing in this pattern licenses "C is faster than Rust" without naming
the compiler.

⚠ **A note on comparing against `c-gcc`/`c-clang` at all.**
`.memory/02-bench-rules.md` forbids comparing cost on an input where the
unhardened rung commits UB. On `small.bin` and `large.bin` the unhardened C
executes no UB and returns the model's answer, so the R1/R1h rows above are a
legitimate comparison; on `adversarial-full.bin` there is no R1 number to compare
because R1 does not return.

### 4f. `-O0`, and what it is not

| cell | small (`-O0 isolated`) |
|---|---:|
| `c-gcc` / `c-gcc-h` | 7668.7240 / 7924.7240 |
| `c-clang` / `c-clang-h` | 8120.1550 / 8376.1550 |
| `safe_naive` / `safe_tuned` | 9108.1486 / 7609.1486 |
| `unsafe` = `verus` | 8721.1486 |

At `-O0` **R3 is cheaper than R4** (7609 vs 8721) because `arr_get_unchecked` and
`buf_get_unchecked` are generic functions rustc does not inline at `-O0`, so R4
pays a real call per access. No perf claim in this file rests on an `-O0` row;
the table is here because `.memory/03-measurement.md` asks for both levels and
because the `-O0` inversion is exactly the artefact that would look like a
finding if it were quoted alone.

### 4g. No `ns` figure is published

`.memory/03-measurement.md` forbids one without a code-layout population, and
this box's R4/R5 offset is a source-path-length artefact that makes the pair a
biased draw of size one. `controls/clayout.py` is shipped so the population can
be built; it has not been run for p22 and **no wall-clock number appears
anywhere in this file**.

## 5. Adversarial rows, per rung

⚠ **What "adversarial behaviour per rung" means when four cells never return.**
`check_adversarial` records `exit=None`, `hung=True` and the cell list, and
computes `diverges` against `model.py`'s `expected_exit` — which keeps describing
the **conforming** behaviour. So the eight hanging cells read `diverges=True` and
the twenty-four that terminate read `diverges=False`. That is the right way
round; the alternative design (`expected_exit = None` meaning "expected not to
terminate") prints the headline upside down, and `harness/check.py` documents why
it was refused.

| input | shape | behaviour |
|---|---|---|
| `adversarial-full` | 64 distinct keys, then a 65th that is absent | **8 cells (both C rungs × 2 opts × 2 modes) do not terminate.** The other 24 agree with the model |
| `adversarial-nearfull` | 63 distinct keys, then 64 more from the same 63 | all 32 agree. `nfill = 63`, `maxprobe = 20` |
| `adversarial-nkeybig` | `nkey = 0xFFFFFFFF`; only the cursor guard stops the walk | all 32 agree |
| `adversarial-allempty` | every key byte is the EMPTY sentinel | all 32 agree, `nfill = 0` |
| `adversarial-stride3` | a 3-byte window | all 32 print 0; the driver guard `stride_w >= 4` skips the loop |

No adversarial row diverges by *value* on any cell. p22 has no silent-wrong-answer
mode: the buggy rung either returns the right answer or does not return.

## 6. The catchers, with their domains

| instrument | domain | on p22's bug |
|---|---|---|
| rustc bounds checks | spatial | **blind.** `i % TABCAP` deletes the check; there is nothing to catch |
| the borrow checker | temporal / aliasing | **blind.** No borrow is involved |
| ASan + UBSan (gcc `-O1`) | spatial, lifetime, arithmetic UB | **blind — measured silent.** No diagnostic, no output; the process spins |
| Miri | UB in the Rust abstract machine | **blind — measured silent.** 90 s, no diagnostic, no output |
| `model.py` checksum agreement | value | **blind by construction.** A cell that never returns produces no checksum to disagree with |
| **Verus `decreases`** | termination | **catches it.** `error: loop must have a decreases clause` before any postcondition is considered, and the clause cannot be discharged without the capacity conjunct (§10) |

**Five of six instruments in this project's own gate are blind to p22's bug, and
that is measured for four of them rather than argued.** The sixth is the one the
pattern exists to exercise.

⚠ **What this does NOT say.** A `timeout` catches it, and so does any watchdog; a
non-terminating loop is trivially *detectable at run time* by anyone who thinks
to look. The claim is about the **static** instruments this project prices — none
of which is in the business of termination except Verus.

## 7. The trusted base

**Five `external_body` items, three of them with contracts.** p27's shape minus
the two allocator items, because p22 allocates nothing.

| item | contract | class |
|---|---|---|
| `buf_get_unchecked` | `i < v@.len()` ⊢ `r == v@[i]` | **U-license** — vstd ships no spec for `<[T]>::get_unchecked` |
| `arr_get_unchecked` | `i < v@.len()` ⊢ `r == v@[i]` | **U-license** — same, for `<[T; N]>::get_unchecked` |
| `arr_set_unchecked` | `i < old(v)@.len()` ⊢ `final(v)@ == old(v)@.update(i, x)` | **U-license** |
| `load_input` | none | **infra** — argv, file I/O, LE decode |
| `emit` | none | **infra** — `println!` |

**One number: `tcb_items = 5`.** Classification: **3 U-license, 0 V-gap, 2
infra.** Nothing here is a V-gap — every fact p22's proof needs about the *table*
is proved, not assumed, and the counting lemmas that carry the termination
argument (`count_ne`, `lemma_all_ne`, `lemma_exists_empty`,
`lemma_count_congr`, `lemma_count_update`) are ordinary verified `proof fn`s with
no `external_body` anywhere near them.

⚠ **`global size_of usize == 8;` is not TCB.** Verus checks it against the actual
compilation target rather than assuming it (`.memory/04-verus.md`).

### SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

(a) *Is the twin's body the right checked stand-in?* The trusted body is
`unsafe { *v.get_unchecked(i) }` and the twin's is `v[i]`. vstd specifies the
checked slice index with the obligation `i < v@.len()`, which is this item's
`requires` verbatim, so a `requires` too weak to license the unchecked read is
too weak to license the checked one and Verus rejects the twin. The gate's
5c-twin per-conjunct deletion confirms the twin *uses* the clause: deleting
`i < v@.len()` gives `22 verified, 1 errors`.

(b) *Is the `ensures` complete with respect to every unchecked operation the body
performs?* The body performs exactly one — a byte read at `i` — and the single
`ensures` `r == v@[i as int]` determines its value. The known blind spot applies
and is not closed here: a body that *also* read `i + 1` would satisfy this
contract, so the argument rests on the body being three tokens long and visible
in the same file. Miri on `unsafe.rs` is the backstop and `miri.required` is
true. ⚠ On p22 that backstop is **weaker than usual on exactly one input**:
`adversarial-full.bin`'s Miri row is BLOCKED by the hang declaration (§11). It
was run by hand anyway and reports no UB — `controls/gen_controls.py --run hang
--miri`, last line.

(c) *Does each clause mean the same in both configurations?* Yes. The signature,
the `requires` and the `ensures` are character-identical between the shipped item
and `slb_twin_buf_get_unchecked`; `#[cfg(slb_twin)]` is a cfg no measured build
sets, so the twin is stripped before codegen and the shipped object is
unaffected. The gate verifies that the token `slb_twin` occurs nowhere but on the
three twin attributes.

⚠ **This item's `requires` has nothing to do with p22's bug.** It bounds a read
of the *input window*, and `c/kernel.c` gets every window read right. It is here
because the R4 rung reads the window unchecked.

### SLB-TRUSTED-ARGUMENT verus.rs arr_get_unchecked

(a) *Is the twin's body the right checked stand-in?* Trusted body
`unsafe { *v.get_unchecked(i) }` on a `&[T; N]`; twin body `v[i]`. vstd's array
index carries the same `0 <= i < N` obligation, and `group_array_axioms` supplies
`v@.len() == N` from the parameter type, so the twin's obligation is this item's
`requires` and nothing else. The `requires` is **one conjunct** and deliberately
not `i < v@.len(), v@.len() == TABCAP`: for a `&[u8; TABCAP]` the second is a
tautology discharged from the parameter type alone and would demand nothing of
any caller — p03 shipped exactly that and the gate's 5c-req tautology probe
refused it. Deleting the one conjunct gives `21 verified, 2 errors`.

(b) *Is the `ensures` complete?* One unchecked operation, one clause determining
its value. Same blind spot, same backstop. ⚠ **On p22 this item is read TWICE per
probe step** (`arr_get_unchecked(&tab, i) != EMPTY && arr_get_unchecked(&tab, i)
!= k`), and both reads are at the same `i`, so completeness is a statement about
one index and not about a range.

(c) *Does each clause mean the same in both configurations?* Yes — same argument
as above, and the item is generic in `T` and `N` in both.

⚠ **This item buys NOTHING at `-O3` on p22, and that is measured rather than
assumed** (§4d): `r4_checked_tab` — the shipped R4 with `arr_get_unchecked` /
`arr_set_unchecked` on the table replaced by `tab[i]` / `tab[i] = k` — is
**byte-identical** to the shipped R4 at `-O3`, `md5_fn 4ac4bd132a50` on both. It
is retained for `-O0`, for uniformity with p27, and because R5 must be
byte-identical to R4 at both levels of spelling, not just of object code. **This
is the opposite of p27's result, where the same item was worth 41.62 Ir/call**;
the difference is `% TABCAP`, which tells LLVM the index is in range.

### SLB-TRUSTED-ARGUMENT verus.rs arr_set_unchecked

(a) *Is the twin's body the right checked stand-in?* Trusted body
`unsafe { *v.get_unchecked_mut(i) = x }`; twin body `v[i] = x`. Same obligation
from vstd for the checked store. Deleting `i < old(v)@.len()` gives
`22 verified, 1 errors`.

(b) *Is the `ensures` complete?* The body performs one store. The `ensures` is a
**whole-sequence equality** — `final(v)@ == old(v)@.update(i as int, x)` — not a
statement about slot `i` alone, so it says both *"slot `i` became `x`"* and
*"nothing else moved"*. ⚠ **The second half is load-bearing on p22 in a way it is
not on p03, p06, p12, p14, p27 or p38**: the outer loop's invariant is
`count_ne(tab@, TABCAP) == nfill`, which quantifies over the **whole** table, so
a store that could disturb any other slot would break the fullness invariant and
with it the termination argument. A weaker `ensures` naming only slot `i` would
leave `lemma_count_update` unusable.

`x` is a pure **value** parameter — stored, never used as an address, an index or
a length — so it has no precondition. That is the parameter-coverage false
positive `.memory/04-verus.md` names; `spec.md`'s
`verus.unsafe_justifications` carries the argument and the gate shouts it every
run. p03 was the first pattern to exercise it, p12 the second, p06 the third,
p14 the fourth, p27 the fifth, p38 the sixth and p22 the seventh.

(c) *Does each clause mean the same in both configurations?* Yes — signature,
`requires` and `ensures` character-identical to `slb_twin_arr_set_unchecked`.

## 8. The spans, and what was searched

**Mandatory spelling spread** (`.memory/05-layout.md` item 13). All figures
`-O3 isolated`, whole-program marginal `Ir`/call, `small.bin` / `large.bin`.
The shipped, contract-conformant cell is marked **SHIPPED**.

### 8a. R2 side

| spelling | small | large | in contract | note |
|---|---:|---:|---|---|
| **`R2ship`** | **4674.6100** | **39185.9600** | yes | **SHIPPED** — index `buf[off + p]` per key |
| `r2_reslice` | 4407.6100 | 37126.9600 | yes | one reslice, still indexed. `−(2·nkw + 11)` |
| `r3_noresl` | 4411.6100 | 37130.9600 | yes | the iterator without the reslice |

⚠ `r2_reslice` is 267.00 / 2059.00 cheaper than the shipped R2 and is in
contract. **R2 is therefore also not at its minimum**, and the R2 − R3 law above
is a difference between two *named* spellings, not between two minima.

### 8b. R3 side

| spelling | small | large | in contract | note |
|---|---:|---:|---|---|
| **`R3ship`** | **4401.6100** | **37120.9600** | yes | **SHIPPED** — cheapest in-contract R3 found |
| `r3_noresl` | 4411.6100 | 37130.9600 | yes | +10.00 flat |
| `r3_bounded_kept` | 4569.2600 | 38356.9200 | **NO** | bounded trip count, conjunct kept |
| `r3_bounded` | 3960.7700 | 33276.9200 | **NO** | bounded trip count *instead of* the conjunct |

**Span (in contract): 4401.6100 … 4411.6100, width 10.00.**

### 8c. ⚠ What the ghost proof buys over the exec bound — and it is NOT instructions

The task that built p22 named route (b) — a probe counter in the exec code — as
the route that would make the proof circular with the fix, and asked what
avoiding it costs. **Measured, and the answer is not the flattering one:**

| spelling | small | large | note |
|---|---:|---:|---|
| **`R4ship`** (route a′, ghost measure) | **4399.6100** | **37118.9600** | **SHIPPED** |
| `r4_execbound` (route b, `probes < TABCAP` in exec code) | 4400.1200 | **36784.8000** | `+0.51` / **`−334.16`** |

**Route (b) is 334.16 Ir/call CHEAPER on `large.bin`.** Reproduced at a second
marginal pair (200/400): `−339.27`. The exec bound gives LLVM a trip count and it
pays for itself on a busy table.

So the honest statement of what route (a′) buys, with the tempting version struck
out:

* ~~"the ghost proof saves N instructions over the exec bound"~~ — **false**, and
  in the direction that would have flattered the result.
* What it buys is that **`unsafe.rs` and `verus.rs` are the same program**: with
  route (b) the R4/R5 pair would still be `exact`, but the *object code of both*
  would move (`md5_fn d0201d1b…` against `4ac4bd13…`, 85 static instructions
  against 74), so the R4 rung would carry a bound that exists only because the
  R5 rung needs to be provable. **That is the circularity, and it is a
  specification defect rather than a performance one.**
* And the `decreases` under route (b) is `TABCAP - probes`, which proves the
  termination of a loop that is bounded in the source. Under route (a′) it proves
  the termination of a loop that is not.

`r3_bounded` (§8b) is the same point on the safe side and it is the sharper one:
the bounded R3 is **440.84 / 3844.04 CHEAPER than the shipped R3**, because the
bound lets LLVM restructure. ⚠ **So "the safe programmer who writes the bounded
loop pays for it" is FALSE on this pattern.** The bounded loop is faster, it
terminates, and the reason `spec.md` forbids it is purely semantic: it computes a
different function on a full table.

### 8d. Sanity: the controls reproduce the shipped cells

`controls/gen_controls.py`'s `R2ship`, `R3ship` and `R4ship` rebuilds have the
same `md5_fn` as the corresponding gate cells (`d086bd6a`, `caf7701f`,
`4ac4bd13` at `-O3 isolated`), so the control harness's flags match
`harness/build.py`'s and every control figure above is comparable to the shipped
column.

## 9. What the proof says, and what it cannot

**The `ensures` is functional and it is NOT where p22's bug lives.** `run` is an
abstract machine over `(tab, nfill, acc)` and the postcondition says the
accumulator is what that machine computes, so a rung that probed differently,
inserted into a different slot, or truncated at a different `TABCAP` is rejected.
**`c/kernel.c` would satisfy it too — on every input on which it returns.**

What excludes the bug is the **`decreases` clause on the probe loop**, and the
relationship between the specification and the implementation is the interesting
part:

> The specification's probe is **bounded** and the implementation's is not.
> `probe(tab, i, k, fuel)` carries `decreases fuel` because a spec function must
> terminate to be a function at all; the exec loop carries no bound. The
> `decreases` on the exec loop is exactly the statement that the two land in the
> same slot — the loop invariant is
> `probe(tab@, i0, k, TABCAP) == probe(tab@, i, k, TABCAP - (u - i0))`, unfolded
> one level per iteration.

Three things the proof does **not** buy, stated because they are the questions a
reader should ask:

1. **It does not prove the C rung terminates.** Nothing here says anything about
   `c/kernel.c`; the ladder's claim is that a rung *written this way and put
   through Verus* cannot omit the conjunct, not that Verus audits C.
2. **It does not prove a bound on the number of probe steps.** `decreases`
   proves *finite*, not *fast*. A table at 63/64 load has `maxprobe = 20` on
   `adversarial-nearfull.bin` and the proof is equally happy.
3. **It says nothing about the wall-clock DoS being survivable.** Termination is
   not liveness under load.

## 10. The proof mutants

`controls/gen_controls.py --run mutants`. Each is **one exact-string
substitution** of `verus.rs`, asserted to hit exactly once.

| mutant | edit | result |
|---|---|---|
| `m1_noguard` | delete `&& nfill < TABCAP` — **`c/kernel.c`'s bug, in R5** | **`19 verified, 1 errors`**: *precondition not satisfied* on `lemma_exists_empty` (its precondition is `count_ne(s, TABCAP) < TABCAP`, i.e. *"some slot is still EMPTY"*) **and** *invariant not satisfied at end of loop body* on the functional invariant |
| `m2_nodecreases` | delete the probe loop's `decreases` clause | **`error: loop must have a decreases clause`** — Verus refuses before verifying anything |
| `m3_noempty` | delete the invariant `tab@[e] == EMPTY` | **`19 verified, 1 errors`**, two *invariant not satisfied* — the witness stops being a witness |
| `m4_nofill` | delete the invariant `count_ne(tab@, TABCAP) == nfill` | **`19 verified, 1 errors`**, *precondition not satisfied* — `nfill < TABCAP` stops meaning "an EMPTY slot exists" |
| `m5_wronghash` | a no-op edit to the spec hash (`… % TABCAP` → `… % TABCAP + 0`) | **`20 verified, 0 errors`** — the CONTROL: the battery is not just breaking the file |

**Two of the four failing mutants fail on the termination argument and not on a
safety clause**, which is what makes p22 a termination result: `m3` and `m4`
delete facts that exist *only* to discharge the `decreases`, and the file stops
verifying. `m2` is the sharpest: it is not a failed proof at all, it is Verus
refusing to accept a program with an unbounded loop and no measure.

⚠ **`m1` is the one to read carefully.** Deleting the exec conjunct fails on the
*lemma's precondition* rather than on the `decreases` line itself, because the
lemma is what supplies the witness the measure is built from. The `decreases`
clause is still there and is still what the failure is about; Verus reports the
first unprovable obligation on the path to it.

## 11. Provenance and disclosures

### 11a. Why the verdict is PASS-WITH-BLOCKED-ROWS

`model.py` declares `expected_hang` on `adversarial-full.bin`;
`harness/check.py::check_miri` blocks a declared-hang input's row up front rather
than waiting out `MIRI_TIMEOUT`. One blocked row, and the verdict is
`PASS-WITH-BLOCKED-ROWS` with **0 failures**. p01 is the only other pattern in
the tree that lands there.

### 11b. ⚠ HARNESS FINDING — the block's stated reason is FALSE on p22, and one Miri row is lost that need not be

`check_miri`'s block text reads:

> *"model.py declares this input non-terminating (expected_hang), so R4 does not
> return under Miri either. n_iters is clamped to MIRI_PROBE_ITERS but the FIRST
> kernel call is the one that hangs."*

**On p22 that is wrong.** The rung that hangs is `c/kernel.c`; `unsafe.rs` — the
only file `miri.sources` names — carries the capacity conjunct and returns
normally. Measured, by running the blocked row by hand:

```
miri SHIPPED unsafe.rs adversarial-full.bin rc=0 UB=False out='15820751917455319872'   <-- the row check.py BLOCKS
```

`expected_hang` is a **per-input** declaration, but its Miri consequence assumes
the hanging rung is the one Miri runs. That is true whenever the bug lives in the
Rust rungs and false whenever it lives only in C — which is the shape of **every
pattern in this tree except a hypothetical one whose R4 has the bug**. The cost
is one unnecessarily blocked row per declared-hang input.

**Reported, not worked around.** `harness/` is not this pattern's to edit
(TASK_070's constraint), and the gate is green either way. The obvious repair is
to condition the block on the Miri source rung actually being one that hangs,
which `model.py` cannot express today: `expected_hang` has no per-rung axis.

### 11c. ⚠ The `slb-contract` sha256 changed once, and this is what moved

| when | sha256 | what |
|---|---|---|
| as first written | `1f29b02eac0b…` | `controls/mkcontract.py`'s first output, before any measurement was published |
| shipped | `044f02cded64…` | two edits, both to `idiom` prose, neither to a pin |

The two edits, in full:

1. `required[6]`'s `rust` value backticked `` `.take(nkey)` `` while its own
   English said *"prose, therefore, and not a backtick"*. The gate's audit
   correctly reported it as three scoped-absent pairs (`safe_naive.rs`,
   `unsafe.rs`, `verus.rs` do not spell it). The backticks were removed so the
   entry pins nothing on the Rust side, as its English always said.
2. A sentence was added to the same entry recording (1).

**No `required` or `forbidden` spelling was added, removed or weakened, and no
`verus`, `driver`, `collapse`, `run`, `identity` or `miri` value moved.** The
direction test (`.memory/01-ladder.md`) is therefore not engaged: the change
*narrows* nothing and *widens* nothing that any measurement depends on. Verify it
against `git` once this lands:

```bash
git show HEAD:patterns/p22-hash-probe/spec.md | diff - patterns/p22-hash-probe/spec.md
```

### 11d. `spec.md` is GENERATED

`controls/mkcontract.py` writes it, reads the 11 003-byte shared named-spelling
paragraph out of `patterns/p38-alias-pun/spec.md` at run time (never embedded —
`.memory/05-layout.md`), and **refuses to write anything** if the assembled
contract fails `check.idiom_problems` or `check.named_spelling_problem`.
`--check` diffs without writing. Edit the generator, never `spec.md`.

### 11e. What was NOT done

* **No `ns` figure is published.** `.memory/03-measurement.md` forbids one
  without a code-layout population, and `controls/clayout.py` is shipped so the
  population can be built — but the p22 numbers here are `Ir` only.
* **`adversarial-full.bin`'s Miri row is blocked** (§11b) and was run by hand
  instead.
* **The hang was not measured under valgrind**, deliberately: a non-terminating
  loop under callgrind is a non-terminating loop.
* **`controls/clayout.py` was ported but NOT RUN.** There is no `ns` figure to
  support, so there is no layout population; run it before quoting one.
* **R4 was not re-shipped** as `r4_reslice` even though that spelling is in
  contract, verifies, and is `1·nkw - 5` cheaper (§4d). That is the standing
  rule, not an oversight.
* **The R2 side was searched only three spellings deep** (§8a) and `r2_reslice`
  is already 267.00 / 2059.00 cheaper than the shipped R2, so `inf(R2)` is not
  known either. Nothing in this file is a claim about a minimum.
* **`r4_onecmp`'s R5 twin was not made to verify.** It reports
  `19 verified, 1 errors` — a failed transplant, **not** `is not supported`
  (`.memory/01-ladder.md`: only the second disqualifies), and its exec code is
  byte-identical to the shipped R4 at `-O3` anyway, so nothing rests on it.
