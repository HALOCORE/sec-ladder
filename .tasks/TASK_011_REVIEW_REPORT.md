# TASK_011_REVIEW — report

**`.memory/01-ladder.md` finding 5 OVERCLAIMS.** The "provably memory-safe" half
is solid and I strengthened it; the "**and still leaks**" half is not supported by
the artefact that was shipped — every byte the leak discloses is a byte the
attacker wrote. (One separate, smaller *underclaim*: the frequency caveat in
finding 5 is wrong and p17 may quote cycles/byte after all — §5 below.)

---

## Did

Re-ran, from scratch and in my own mirror (`.temp/review011/`), every claim
TASK_011_REVIEW names: the Verus mutants, the two safe-Rust controls, the C
rungs, ASan, the full marginal-`Ir` table, the `4.2500` and `8.0000` constants,
the obligation decomposition, the `abs = len - s` identity, the anti-collapse
margin, and the CPU clock. Built **five new artefacts** the delivery does not
have: a byte-level disclosure model, a memory-safety-only build of the absguard
mutant, a *slice*-relative guard mutant (Verus + safe Rust), a two-window
disclosure probe, and a direct clock measurement.

Nothing under `patterns/`, `.memory/`, `harness/`, `pilot/` was touched.
`git status` is clean apart from the manager's own untracked
`.tasks/TASK_011_REVIEW.md`; nothing was written into `results/gate/`.

---

## Findings

### BLOCKER 1 — the "leak" discloses only the attacker's own bytes

`.memory/01-ladder.md:313,322,331,344` · `patterns/p17-http-range/NOTES.md:7-10,
16,127-143,541,771` · `README.md:34` · `RECAP.md:70-78` · `spec.md:92-106` ·
`c/kernel.c:26-31` · `verus.rs:17-22`

`adversarial-leak.bin` is one 64-byte window:

```
window bytes: 03000a0038004000 284311c559d747ef ... (56 random body bytes)
nsuf=3 body_start=8 content_len=56 suffixes=[10, 56, 64]
```

R1 (unchecked) folds 130 bytes over window indices `[0,63]`.
R1h/R2/R3/R4/R5 fold 66 bytes over `[8,63]`.
**The excess is exactly indices `{0..7}` = `03 00 0a 00 38 00 40 00` = the `nsuf`
word and the three suffix `u16`s — the attacker's own request table, byte for
byte.** (`.temp/review011/disclose.py`, output pasted in Evidence.)

This is structural, not an artefact of the chosen input. The leak regime is
`content_len < s <= len`, whose read is `[len-s, len)` with
`len-s ∈ [0, body_start)`; a caller is *entitled* to every body byte (ask
`s = content_len`); therefore the excess over entitlement is **always** a suffix
of `[0, body_start)`, and `[0, body_start)` is by construction the header the
attacker supplied — `inputs/gen.py:15` labels it `ATTACKER DATA` in so many
words. No input to this kernel can make the in-bounds regime disclose anything
else. The maximum possible disclosure is `2 + 2*nsuf` attacker-written bytes.

So what p17 actually demonstrates is: **a program that is provably memory-safe
and functionally wrong** — it serves a range it should have rejected and returns
a checksum ≠ `range_fold`. That is real, valuable, and puts the promised
measurement under finding 2. It is **not** an information disclosure, and the
words "leak", "information leak the CVE is famous for", "Heartbleed's shape" and
"still leaks" are not earned by this artefact. `NOTES.md:541` and `:771` state
the true thing ("serves the attacker **its own** metadata") one paragraph below
the headline that contradicts it.

Concrete failure scenario: the project cites p17 as "a provably memory-safe
program that leaks"; a reader asks *what was disclosed*; the answer is eight
bytes the attacker sent in the same request. The claim collapses under the first
question anyone would ask.

**The fix is one token, and I built and verified it — see BLOCKER 1b.**

### BLOCKER 1b (constructive) — the artefact finding 5 describes does exist, one token away

`.memory/01-ladder.md:338` and `NOTES.md:130-133,755-757` say the absolute-index
guard `start >= -(body_start as i64)` is "**exactly what a bounds check buys
you**". It is not — it is **strictly stronger**. p17's driver hands the kernel
`bytes.as_slice()`, the *whole blob* (`safe_naive.rs:71`, `verus.rs:367`), so the
bound a bounds check (and `get_unchecked`'s `requires i < v@.len()`) actually
enforces is *slice* index ≥ 0, not *window* index ≥ 0. The guard that expresses
that is

```rust
if start < end && start >= -((off + body_start) as i64) {   // sliceguard
```

Measured (all in `.temp/review011/mirror/`, my copies, Verus via `./verus_run.py`):

| file | result |
|---|---|
| `verus.rs` (shipped) | `10 verified, 0 errors` |
| `verus_absguard.rs` (p17's M4) | `9 verified, 1 errors` — functional invariant only, **also under `--multiple-errors 20`** |
| `verus_absguard_msonly.rs` (M4 with the functional spec stripped) | **`10 verified, 0 errors`** |
| `verus_sliceguard.rs` (**new**) | `9 verified, 1 errors` — functional invariant only |
| `verus_sliceguard_msonly.rs` (**new**) | **`10 verified, 0 errors`** |

Both guards are fully memory-safe. The difference is what they disclose.
`.temp/review011/leakprobe.rs` puts two 64-byte windows in one allocation
(window 0's body = a secret, window 1 = the attacker's) and calls the kernel on
window 1 with the secret set to `0x00` and to `0xff`:

| guard | `s` | secret=0x00 | secret=0xff | discloses window 0? |
|---|---:|---|---|---|
| shipped | 64 / 70 | `10964111326756502081` | same | no |
| **absguard (p17's artefact)** | 64 | `6538821468947553451` | **same** | **no** — wrong answer, zero information |
| absguard | 70 | `10964111326756502081` | same | no (guard rejects) |
| **sliceguard** | 70 | `14940305438379539953` | `10930790086150322769` | **YES — real disclosure** |

The output of the sliceguard kernel is a function of bytes belonging to another
window. No panic, no `unsafe`, and Verus proves every access in bounds. **That**
is a provably memory-safe program that leaks. The irony worth writing down: the
*stronger-than-a-bounds-check* guard p17 chose is precisely the one that confines
the disclosure to the attacker's own bytes.

Recommended restatement of finding 5: keep "provably memory-safe and
functionally wrong" for the shipped artefact; if the information-disclosure claim
is wanted, ship the sliceguard variant and a multi-window adversarial input
(note `inputs/gen.py:51-58` already identifies the multi-window backward read as
"a silent wrong answer with no ASan" — it was treated as a hazard to gate
determinism and is in fact the genuine leak).

### MINOR 2 — `NOTES.md:598-605`'s Miri-coverage caveat is factually wrong

> "R4 keeps the `start >= 0` conjunct, so R4's own reads never come within a byte
> of either end of the blob on any shipped input … so Miri's coverage here is
> thinner than it was on p16"

Measured over every window the driver actually visits:

| input | n_blob | min read idx | max read idx | last valid |
|---|---:|---:|---:|---:|
| small | 16192 | **0** | **16191** | 16191 |
| large | 8390650 | **0** | **8390649** | 8390649 |
| adversarial-leak | 64 | **0** | **63** | 63 |
| adversarial-oob | 64 | **0** | **63** | 63 |

R4 touches *both* blob boundaries exactly on all four. Miri's boundary coverage
on p17 is better than p16's (whose window ended three bytes short), not thinner.
This is an SLB-TRUSTED-ARGUMENT block, i.e. text a future reader is meant to rely
on; it should be corrected rather than left as a conservative-sounding error.

### MINOR 3 — `NOTES.md:418-426`'s absolute swept rates are over-precise

`§3b` quotes R2 `9.9991` and R3/R4 `5.7491` Ir/byte and `§2` says "R3's marginal
rate is 5.7491 and R4's is 5.7491 — equal to four decimal places". The *equality*
and the *differences* are exact and reproduce; the absolute values do not. Three
independent lag-4 pairs I measured:

| pair | R2 | R4 | R2 − R4 |
|---|---:|---:|---:|
| sw200 → sw204 | 10.1775 | 5.9275 | **4.2500** |
| sw201 → sw205 | 9.9525 | 5.7025 | **4.2500** |
| **sw228 → sw232** | **10.0000** | **5.7500** | **4.2500** |

The wobble is a *driver* term: marginal `Ir`/call carries a fractional part that
depends on the input (`.70/.41/.00/.30/.11`, identical across all three Rust
binaries), which is the cost of formatting the final `println!` of a different
`acc`. It cancels in same-input differences and contaminates cross-input rates.
The sw228→232 pair has zero residue on both sides and gives **exactly 10.0000 and
5.7500 — p16's constants, not 0.0009 below them**. So the honest statement is
*stronger* than the one in `NOTES.md`: p17 reproduces p16's rates exactly, not to
four decimals with a 0.0009 offset.

### MINOR 4 (underclaim) — the frequency caveat is based on an unusable sysfs value

`.memory/01-ladder.md:363-367` and `NOTES.md:271-280` decline to quote
cycles/byte because CPU 3's `scaling_cur_freq` "was seen ramping 800 → 902 MHz".
That reading is meaningless on this box. `.temp/review011/clock.c` times a
dependent `addq` chain (exactly 1 cycle latency), pinned:

```
CPU 3: window 0: 1190 MHz | window 1: 2773 MHz | windows 2-10: 3801-3888 MHz
CPU 5: 3771-3874 MHz
```

and **while that load runs, `/sys/.../cpu3/cpufreq/scaling_cur_freq` reports
`800000` for the entire six-second sample**. So:

- p16's "CPU 5 turbos to a measured 3.85 GHz" (`p16/NOTES.md:193`) is correct and
  its **3.027–3.055 cycles/byte stands**; the two patterns were measured on
  CPUs with identical governors (`powersave`/`intel_pstate`, 800 MHz–3.9 GHz).
- p17 *can* quote cycles/byte: 0.784–0.791 ns/byte × 3.85 GHz = **3.02–3.05
  cycles/byte**, which is p16's interval, not merely an upper bound of 3.09.
- There is a ~45 ms ramp from idle. p17's wall protocol (30 interleaved reps,
  min) and p16's survive it; a single cold run would not.

Durable fact for `.memory/00-environment.md`: **`scaling_cur_freq` reads 800 MHz
under full load on this box — never use it to reason about the clock during a
measurement; time a dependent-add chain instead.**

---

## Evidence

Disclosure model (`.temp/review011/disclose.py`):
```
=== adversarial-leak.bin: n_iters=8 stride=64 n_blob=64 nwin=1
    window bytes: 03000a0038004000284311c559d747ef0a0b8ab6693d47a9daca29062a6263b0...
    nsuf=3 body_start=8 content_len=56   suffixes: [10, 56, 64]
    R1  (unchecked): checksum=6710369658547213763 nserved=3 bytes_folded=130 distinct_idx=[0,63]
        indices outside the allocation: []
        indices inside the window HEADER (metadata): [0, 1, 2, 3, 4, 5, 6, 7]
        those bytes = 03000a0038004000
    R1h (checked):   checksum=11081456374647857074 nserved=2 bytes_folded=66  distinct_idx=[8,63]
        indices inside the window HEADER (metadata): []
```
Folding those kernel results through the driver (8 iterations) reproduces all
three published stdout values independently: `1395842226496950656` (R1 leak),
`13350769809739249920` (checked), `7837465949650580608` (R1 oob).

Verus (my mirror, `./verus_run.py`):
```
verus.rs                     -> 10 verified, 0 errors
verus_absguard.rs            -> 9 verified, 1 errors   (only: invariant not satisfied
                                at end of loop body, verus_absguard.rs:311 range_walk)
verus_absguard.rs --multiple-errors 20 -> 9 verified, 1 errors   (unchanged)
verus_nocheck.rs             -> 9 verified, 1 errors, TWO error blocks
                                (range_walk:311 AND `0 <= base`:342) and the default run
                                prints "note: while loop: not all errors may have been
                                reported" — which absguard does NOT print
verus_absguard_msonly.rs     -> 10 verified, 0 errors
verus_sliceguard.rs          -> 9 verified, 1 errors   (functional only)
verus_sliceguard_msonly.rs   -> 10 verified, 0 errors
```
The `nocheck` run is the control that proves the `--multiple-errors` probe would
have shown a second, memory-safety obligation if one existed.

Safe-Rust controls (`rustc -C opt-level=3 -C debug-assertions=off --cfg slb_isolated`):
```
safe_naive           leak 13350769809739249920 | oob 13350769809739249920 | small/large agree
safe_naive_nocheck   leak 1395842226496950656  | oob exit=101             | small/large agree
safe_naive_absguard  leak 1395842226496950656  | oob 13350769809739249920 | small/large agree
c-gcc / c-clang O3   leak 1395842226496950656  | oob 7837465949650580608
c-gcc-h / c-clang-h  both 13350769809739249920
```

Marginal `Ir` per call, my own two-run callgrind differencing
(`.temp/review011/marginal.py`, `n_iters` 100/200) — **every cell equals
`results/gate/p17-http-range.json` and `NOTES.md §2` to the hundredth**:
```
c-gcc      7065.28 / 57257.28     safe_naive  8832.70 / 71572.70
c-gcc-h    7074.28 / 57266.28     safe_tuned  5240.70 / 41311.70
c-clang    5163.28 / 41234.28     unsafe      5208.70 / 41279.70
c-clang-h  5182.28 / 41253.28     verus       5207.70 / 41278.70
```
Derived: gcc rolled fold `50192/6274 = 8.00000` **exactly**; R2
`62740/6274 = 10.00000` **exactly** (both loops rolled, so the two-point estimate
is unbiased); R4 `5.74928` (two-point, carries the unroll residue — the true swept
value is 5.7500); R1h−R1 = +9.00 gcc, +19.00 clang; R3−R4 = +32.00; R5−R4 = −1.00.

ASan+UBSan, my own build (gcc -O1 -fsanitize=address,undefined -static-lib*):
```
adversarial-leak  exit=0 stdout=1395842226496950656  stderr EMPTY
adversarial-oob   exit=1  ERROR: AddressSanitizer: heap-buffer-overflow
                          READ of size 1 ... in kernel patterns/p17-http-range/c/kernel.c:81
                          located 6 bytes before 64-byte region
adversarial-nsuf  exit=0 stdout=0  clean      small exit=0 clean
```

Obligation decomposition, recounted with `--verify-function X --verify-root`:
`kernel 3`, `main 5`, `fold_bytes 1`, `range_walk 1`, `range_fold 0` → **10**,
exactly as `spec.md:307` pins it.

`abs = len - s` identity: an independent model written in the *identity form*
(serve iff `0 < s <= content_len`, read `[off+len-s, off+len)`, `n = s`)
reproduces the checked checksum of **both** the shipped C (`c-gcc-h`) and the
shipped Rust (`safe_naive`) on all six inputs. The identity is implemented, not
just asserted.

R1 vs R1h, comments stripped — one conjunct, nothing else:
```
-        if (start < end) {
+        if (start < end && start >= 0) {
```

Anti-collapse floor: tightest ratio **40.27×** at `c-clang/O3/whole/large.bin`
(41206.28 Ir vs a derived floor of 0.25 × 4093), i.e. 97.52% of the work could
vanish before the stage objects; **23.07×** even if denominated in the honest
871/7145 folded bytes. `NOTES.md:507`'s 40.3× and its "this stage is a smoke
test, not a gate" caveat are right; the floor does nothing on this pattern.

---

## Clean negatives — attacks that did not land

1. **"The `1 error` is hiding a memory-safety obligation."** It is not.
   `--multiple-errors 20` changes nothing on `verus_absguard.rs`, the
   "not all errors may have been reported" note appears on `verus_nocheck.rs`
   and not on `verus_absguard.rs`, and stripping the functional spec entirely
   from the absguard mutant gives `10 verified, 0 errors`.
2. **"R2 is a pessimised straw man."** Four alternative naive spellings, all
   agreeing on `small`/`large` checksums: `usize`-hoisted index **8832.70 /
   71572.70**, incrementing index **8832.70 / 71572.70**, `while` + `i64`
   **8832.70 / 71572.70** — identical to R2 as shipped to the hundredth — and a
   `for j in base..base+n` range loop at **8841.70 / 71581.70**, i.e. +9 *worse*.
   R2 is tied-cheapest of five. The +69.6% is fair.
3. **"The C/safe-Rust bit-identity is a coincidence."** It is not: my byte-level
   model shows both fold the identical 130-byte index sequence
   (`[54,64) ++ [8,64) ++ [0,64)`), and the model derives `1395842226496950656`
   from the bytes alone.
4. **"Rust's bound is the slice, C's is the allocation, so the comparison is
   unsound."** Here they coincide (the driver passes the whole blob), *and* the
   leak-regime result is robust to that choice anyway: `len - s ∈ [0, body_start)`
   is in bounds of the **window** too, so an idiomatic `&buf[off..off+len]` API
   would panic on neither. (The choice does matter for the OOB regime — that is
   BLOCKER 1b.)
5. **"The `buf@.len() <= i64::MAX` requires is bureaucracy / the driver's third
   guard conjunct is vacuous."** Both load-bearing: deleting the driver conjunct
   gives `9 verified, 1 errors` (`invariant not satisfied before loop`, :384);
   deleting either kernel `requires` clause gives `9 verified, 1 errors` with
   `precondition not satisfied` / `possible arithmetic underflow/overflow`.
6. **"`for` + `continue` really works and the engineer restructured for
   convenience."** No: a minimal probe gives
   `error: for-loops do not yet support continue`.
7. **"The TCB tally is under-counted."** Recounted: 3 `external_body` items
   (verus.rs:192, :242, :254), 6 lines of body, exactly **1** `unsafe` token in
   exec position (:199), zero `assume` / `assume_specification` /
   `external_fn_specification`, zero `unsafe` in `common/driver.rs`. Matches
   `NOTES.md §4`.
8. **"R4 ≢ R5."** Gate JSON: O3 `md5_fn 45064db24a5be1cd9be7c5fc9c2a5ef5` both
   sides, `md5_raw_equal true`, counts 120/116, padding 9/9.
9. **p02 Part 0 re-quoting** (scope-limited check only): `9200.74` / `10204.74` /
   `10200.84` are in `results/gate/p02-buffer-copy.json` at the stated keys;
   `c-gcc` small wall `0.0075607 s → 7.56 ms` and `binary_text_bytes 2545` are in
   `results/p02-buffer-copy.json`. The diff matches the JSONs, and it flags its
   own remaining half-fix honestly.

---

## Problems

- **BLOCKER 1 requires a restatement of `.memory/01-ladder.md` finding 5,
  `RECAP.md:70-78`, `patterns/p17-http-range/NOTES.md` §0/§1b/§5/§7-M4,
  `README.md:28-40`, `spec.md:92-106`, `c/kernel.c:26-31` and `verus.rs:17-22`.**
  Every one of those says or implies "leak"/"information disclosure"/"Heartbleed"
  about a read that discloses attacker-supplied bytes only.
- The manager's commit message (`a58ca64`) carries the same overclaim
  ("provably memory-safe program that still leaks"). It is already in history;
  the correction belongs in `.memory/`.
- I did **not** run the full gate. A gate run was unnecessary for every question
  asked and would have written into the tracked `results/gate/`.

---

## Unsure / not done

- I did not rebuild or re-measure the §3 decomposition variants v1–v5, the
  `whole`-mode and `O0` rows, the wall-clock table, or the 34-point sweep in
  full; I sampled the sweep at three lag-4 pairs and took the rest from the gate
  JSON, which I did verify against my own callgrind runs on the shipped inputs.
- `verus_sliceguard.rs` and `leakprobe.rs` are *reviewer* artefacts under
  `.temp/review011/`. They are not gate-checked, have no `spec.md` pins and no
  `model.py`; if the manager wants the disclosure claim, they need to be built
  properly as a pattern control, not lifted from my scratch dir.
- My "entitlement" definition — the caller is entitled to every body byte because
  it can ask for `s = content_len` — is a judgement, though I think an
  unavoidable one for a *suffix-range* server. If someone argues the caller is
  only entitled to the bytes of the range it actually asked for, then p17's
  in-bounds regime still discloses only header bytes it also wrote, so the
  conclusion does not move.
- The 1-cycle-latency assumption for `addq` in the clock probe is textbook but
  unverified on this exact part; if it were wrong the measured GHz would be an
  *under*-estimate, which only strengthens MINOR 4.

---

## Memory updates

None written — reviewers do not edit `.memory/`. Four things belong there and
the manager should land them:

1. `.memory/01-ladder.md` finding 5 — restate per BLOCKER 1 and 1b.
2. `.memory/00-environment.md` — `scaling_cur_freq` reads 800 MHz under full load
   on this box; measure the clock with a dependent-add chain (3.80–3.89 GHz on
   CPUs 3 and 5, ~45 ms ramp from idle).
3. `.memory/03-measurement.md` — marginal `Ir`/call carries a per-input
   fractional term from the final `println!`; it cancels in same-input
   differences and biases cross-input rate estimates by ~±0.2 Ir/byte at
   200-byte scales. Quote differences, or sweep, or use a byte span wide enough
   to drown it.
4. `.memory/04-verus.md` — `--multiple-errors N` is the probe that distinguishes
   "one obligation failed" from "one was reported"; the tell that more are hiding
   is Verus's own `note: while loop: not all errors may have been reported`.
   Stripping the functional spec and re-verifying is the stronger form.
