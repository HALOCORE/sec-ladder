# p17 — findings, adversarial behaviour, TCB tally, sticking points

> **Read §0 first.** p17's headline is **not** a performance claim. It is a
> *negative* result about memory safety, and §1a, §1c and §7 are the measurements
> that earn it. §2 and §3 are the cost columns and they are the smaller half.

**The one-line result.** **Safe Rust does not fix this bug. Neither does a proof
of memory safety.** One missing `start >= 0` produces two harms; safe Rust and
the trusted accessor's `requires` each eliminate exactly one of them, and the
one they do not eliminate is a **legal read of the wrong bytes**. Making the
index provably in bounds — which is precisely what safe Rust forces on you and
precisely what `get_unchecked`'s `requires i < v@.len()` demands — discharges
every memory-safety obligation in the file and leaves the wrong read in place.

**Which wrong bytes you get depends on the guard, and that is the measurement.**
Four programs, one token apart, all built from `verus.rs` by substituting the
guard and nothing else. "Verus (MS-only)" is the same file with the functional
specification stripped, which is `.memory/04-verus.md` item 2b's probe: it asks
whether the *memory-safety* half discharges on its own.

| guard | Verus | Verus (MS-only) | memory safety | reads a **neighbouring window**? |
|---|---|---|---|---|
| none — `if (start < end)`, R1 / `verus_nocheck` | 9 verified, 1 errors, **two** error blocks | **9 verified, 1 errors** — `0 <= base` | **no** | yes on `crosswin`, and on `oob` it reads *before* the blob |
| `start >= -(body_start as i64)` — **window**-relative, §7 M4 | 9 verified, 1 errors, functional only | **10 verified, 0 errors** | yes | **no** — it serves the attacker its *own* request header |
| `start >= -((off + body_start) as i64)` — **slice**-relative | 9 verified, 1 errors, functional only | **10 verified, 0 errors** | yes | **YES** — §1c, measured |
| `start >= 0` — shipped R1h/R2/R3/R4/R5 | **10 verified, 0 errors** | 10 verified, 0 errors | yes | no, and correct |

**Rows 2 and 3 are the whole point.** Identical Verus verdicts in both columns,
one token apart, opposite security outcomes. Row 2 is what p17 shipped as its
demonstration and it discloses nothing — its excess bytes are the attacker's own
`nsuf` word and suffix table. Row 3 is the artefact the headline needs: a program
with **no `unsafe` outside the one trusted accessor, every obligation
discharged, no panic and no sanitizer report**, whose output is a function of a
*different* caller's bytes. Row 1 is the positive control that makes the MS-only
column mean something: strip the functional spec from the *unguarded* mutant and
Verus still reports an error, and it is `0 <= base`.

Why row 3 and not row 2 is what a bounds check licenses: p17's driver hands the
kernel `bytes.as_slice()`, **the whole blob**, so the index a bounds check —
and `get_unchecked`'s `requires` — actually constrains is the *slice*-relative
one. The window-relative guard of row 2 is **strictly stronger** than memory
safety, and §1b used to call it "exactly what a bounds check buys you", which was
wrong in the direction that flattered the pattern.

The three earlier rows of the old headline, for the record:

| | on `adversarial-oob.bin` (`s > len`) | on `adversarial-leak.bin` (`content_len < s <= len`) |
|---|---|---|
| C (R1, shipped) | wrong answer, exit 0; **ASan: 6 bytes *before* a 64-byte region** | wrong answer, exit 0; **ASan silent** |
| safe Rust, check deleted | **panics**, exit 101 | **prints C's wrong value**, exit 0, no diagnostic |
| Verus, check deleted | memory-safety obligation fails | — (see §7: Verus quantifies over inputs, not over files) |

Cost, for completeness and because the project's other patterns are about cost:
**R3 safe-tuned is +32 instructions per call on both shipped inputs — 0.61% /
0.08% — and it is flat in the bytes served, not flat per call.** Both shipped
bands have `nsuf = 3`, and §2's own bullet says the +32 splits as roughly 9–10
per call plus 7–8 per *range request*; §3b's 34-point sweep holds the request
count at 1 and so establishes the per-byte rate and nothing about the constant.
On that reading R3 is still the fifth
pattern in a row where idiomatic safe Rust is free **per byte**.
⚠ **And `+32` bounds `inf(in-contract R3) − R4ship` and nothing else
(TASK_018, §10a).** An
alternate R3 that is *inside* p17's declared idiom — same `i64` `start`/`end`,
same literal conjunctive guard, only the suffix-table walk and the byte fold
respelled — measures **51 `Ir`/call cheaper on both bands**, i.e. **−19 against
the shipped R4**. Do not quote `+32` as what safety costs on this kernel — and do
not quote it as an upper bound on p17's in-contract safety tax either: that
would need the **R4** side searched, and it has not been. ~~Where it has been
searched the unsafe rung moved too (p05 by 7 flat at TASK_022, p16 by `4·nrec`
at TASK_023) and the shipped pair's difference stopped bounding anything.~~
**Withdrawn at TASK_028**: both of those levers are respellings of a header read
that vstd cannot verify at the pin, so neither is a rung, and **no pattern's R4
side has moved by an admissible instruction**. p17's `−19` is an **R3-side**
figure and is untouched by any of it (TASK_027_REVIEW Q2, clean negative).

⚠ **This paragraph said "+32 instructions per call, flat" until TASK_016, and
"flat" there was read as flat per call, which the two shipped points cannot
establish** — they differ 8× in body size and not at all in `nsuf`.
TASK_015_REVIEW M2 varied `nsuf` 1…8 on generated inputs and measured
`R3ship − R4` running 18…63, i.e. ≈ `7·nsuf + 9`, with `R3ship − R3′` exactly
`17·nsuf` over eight points and zero residual. Those absolute figures are **not**
p17's, because the inputs are not the shipped ones (at `nsuf = 3` they give
+30/−21 against the shipped +32/−19); what is established is the **`nsuf`
dependence**. The reason it could not be checked against shipped inputs is that
**p17 ships no sweep at all** — `inputs/gen.py` has no `--sweep` mode, unlike
p16's (68 blobs) and p05's (144) — and §3b's sweep lives in `.temp/p17/sweep/`,
regenerated by hand. **A shipped `nsuf` sweep is owed and is its own task**; it
was deliberately not done at TASK_016, which changed no cell source and no
input. R2's naive spelling pays
**4.2500 Ir per folded byte**, which is p16's swept constant **exactly**, on a
completely different kernel — as are the two rates it is the difference of,
10.0000 and 5.7500, once the driver's per-input `println!` term is removed
(§3b) — and §3 shows it is the byte fold and
**not** the signed arithmetic: the entire signed↔unsigned round trip costs
**4 instructions per call, flat**.

## 0. What p17 is for, and what its numbers are of

Every perf result on this project so far is about **cost**. p17 is the first one
about a **limit**.

The CVE (2017-7529, nginx's range filter): `Range: bytes=-N` makes
`start = content_length - N` **negative** in signed arithmetic, and the only
validation, `if (start < end)`, passes for a negative `start`. The negative start
is then added to a base offset. The identity `abs = body_start + start = len - s`
means the served range is always `[len - s, len)` — the read never runs *past*
the window, it runs **backwards**, and how far back is one attacker-controlled
`u16`. `inputs/gen.py` builds two 64-byte windows that differ in exactly that one
`u16`.

Three things this file is careful about:

- the perf claim in §2 **names a loop**, and §3 is the decomposition that earns
  it — five variants, one loop changed at a time, built under `.temp/p17/decomp/`
  and never shipped as rungs, plus a 34-point sweep. p02's headline was retracted
  and p16's was corrected for exactly this;
- **R3 leads**, per `.memory/01-ladder.md` finding 3, whose author broke the rule
  on p16;
- the `Ir` numbers are **marginal per kernel call** — two callgrind runs of one
  binary on one input with only `n_iters` changed, differenced — never a
  whole-program total, which moves with the size of the environment block.

## 1. The adversarial behaviour table

Recorded, not required to agree — `.memory/02-bench-rules.md` makes the
adversarial rows a *behaviour* table. Every row below was produced by
`harness/check.py p17` (stage 4 for the plain builds, stage 7 for ASan+UBSan)
over all 32 cells; where the opt/mode variants of a rung differed the gate says
so, and it did not on any row here.

| input | shape | R1 (c-gcc, c-clang) | R1h + R2 + R3 + R4 + R5 | ASan+UBSan on R1 |
|---|---|---|---|---|
| `adversarial-leak.bin` | **one window**, `n_blob == stride == 64`, `nsuf=3`, suffixes `10, 56, 64`. The third asks for 64 bytes of a 56-byte body: `start = −8`, `abs = 0` | exit 0, **`1395842226496950656`** — a wrong answer, no crash, no diagnostic | exit 0, `13350769809739249920` | **clean, exit 0.** No ASan report, no UBSan report |
| `adversarial-oob.bin` | the same 64 bytes with **one `u16` changed**: suffixes `10, 56, 70`. `start = −14`, `abs = −6` | exit 0, **`7837465949650580608`** — also a wrong answer, also no crash | exit 0, `13350769809739249920` — *identical to the leak row* | **fires**: `heap-buffer-overflow`, `READ of size 1`, ***"6 bytes before 64-byte region"***, allocated in `slb_head1_u64_bytes`, at `c/kernel.c:81`, exit 1 |
| `adversarial-crosswin-lo.bin` | **two** windows, `n_blob = 128`, `stride = 64`. Window 0 is the victim (`nsuf=1`, suffix `32`, secret `buf[4..32)` filled `0x00`); window 1 is the attacker (`nsuf=3`, suffixes `10, 56, 122`), and `s = 122` gives `start = −66`, `abs = 6` — **six bytes into the victim's window** | exit 0, **`16140351554550698128`** | exit 0, `15118011540968580209` | **clean, exit 0.** No ASan report, no UBSan report |
| `adversarial-crosswin-hi.bin` | the same 128 bytes with **only the victim's secret changed** to `0xff` | exit 0, **`16701685314320143948`** — *different from the `-lo` row*, so window 0's bytes reached the output | exit 0, `15118011540968580209` — *identical to the `-lo` row* | **clean, exit 0** |
| `adversarial-nsuf.bin` | `nsuf = 100` declared in a 34-byte window, so `2 + 2*nsuf > len` | exit 0, `0` | the same, everywhere | clean, exit 0 |
| `adversarial-stride1.bin` | `stride_w == 1`, below the driver guard; zero kernel calls | exit 0, `0` | the same, everywhere | clean, exit 0 |
| `small.bin`, `large.bin` | well-formed | exit 0, agree with `model.py` | the same | clean, exit 0 |

**The crosswin pair is a differential and the two R1 cells are the result.** One
byte-for-byte identical pair of files except the victim's 28 secret bytes; R1's
checksum moves and every checked rung's does not. That is *disclosure of another
window's data*, with ASan silent and no panic — and it is what `inputs/gen.py`
already predicted in prose ("a backward read from a middle window stays inside
the allocation, which is a silent wrong answer with no ASan") and treated as a
hazard to be avoided. It is in fact the genuine leak; §1c builds the memory-safe
Rust and Verus programs that do the same thing.

Five things in that table are worth reading twice.

**The two adversarial files differ in one `u16`, and every rung that keeps the
check prints the same checksum on both.** The first two suffix requests are
shared and the body bytes are drawn from the same rng state, so the *only*
variable is the third request. That is what makes the comparison worth
something: the leak and the OOB are not two inputs, they are one input and one
number.

**ASan is silent on the leak and that silence is the result, not a gap.** The
read starts at window byte 0 and runs to byte 64 — inside the allocation, inside
the window, inside anything a bounds check can express. `model.py` declares that
input `"clean"`, derived from `off + len - s < 0` rather than from `start < 0`,
so if a sanitizer *had* fired the gate would have failed it. It did not.

**R1 does not crash on either input.** Contrast p16, where the same class of
omission made `end - p` underflow `size_t` and the walk never terminated
(SIGSEGV, all 8 builds). Here `n = end - start = s <= 65535`, so every served
range is bounded and every loop ends: R1 prints a plausible wrong number and
exits 0 on both adversarial files. **A signed underflow in an *index* is quieter
than an unsigned underflow in a *bound*** — which is why this one shipped in
nginx and was exploited rather than crashing in testing.

**`adversarial-nsuf.bin` is the control**, declared `clean` on purpose. It is the
same "the header lied" shape with the suffix *values* innocent: the walk is
rejected by `2 + 2*nsuf > len`, the test **R1 keeps**, so all eight cells agree.
Without it, "ASan fires on the adversarial input" would not distinguish *a suffix
value was trusted* from *the header did not fit*.

### 1a. The two controls — safe Rust with the check deleted

`.temp/p17/mut/patterns/p17-http-range/safe_naive_nocheck.rs` is `safe_naive.rs` with `&& start >= 0`
deleted and **nothing else changed**, built `-O3 -C debug-assertions=off
--cfg slb_isolated`, never shipped as a rung.

| input | C R1 (shipped) | safe Rust, same omission |
|---|---|---|
| `adversarial-leak.bin` | exit 0, `1395842226496950656` | **exit 0, `1395842226496950656`** |
| `adversarial-oob.bin` | exit 0, `7837465949650580608` (ASan: 6 bytes before) | **exit 101**, `index out of bounds: the len is 64 but the index is 18446744073709551610` |
| `small.bin` | `18416420189787787870` | `18416420189787787870` |
| `large.bin` | `10613012665269285418` | `10613012665269285418` |

**The first row is the project's first measured limit of memory safety.** Safe
Rust, with no `unsafe` anywhere, reproduces C's wrong value bit for bit, exits
0, and says nothing. The bounds check is present and *passes*, because index 0 is
a perfectly good index into a 64-byte slice. (What those extra bytes *are* is
§1b: on this one-window input they are the attacker's own header. Add a second
window and the same omission reads the neighbour — §1c.) The second row is the
usual win, and
the mechanism is visible in the panic message: `(base + j) as usize` on
`base = −6` is `18446744073709551610`, which is what a bounds check is for.

Both rows are the same one-conjunct omission. One language feature catches one of
them.

### 1b. And the version that *is* bounds-safe still serves the wrong bytes

The obvious "fix" for someone reasoning about memory rather than about the
protocol is to guard the **absolute index** instead of the logical start —
`start >= -(body_start as i64)`, i.e. "clamp the read to the front of the
window". `.temp/p17/mut/patterns/p17-http-range/safe_naive_absguard.rs`:

| input | result |
|---|---|
| `adversarial-leak.bin` | exit 0, **`1395842226496950656`** — C's wrong value again |
| `adversarial-oob.bin` | exit 0, `13350769809739249920` — **correct** |
| `adversarial-crosswin-{lo,hi}.bin` | exit 0, `15118011540968580209` on **both** — no cross-window disclosure |
| `small.bin` / `large.bin` | correct |

Memory-safe on every input, correct on the OOB input, and it still serves the
suffix table to the attacker. §7's M4 is the same mutation in Verus, and it
verifies every memory-safety obligation in the file.

**This paragraph used to say that guarding the window-relative index is "exactly
what a bounds check buys you". That was wrong, and wrong in the direction that
flattered the pattern** (TASK_011_REVIEW, blocker 1b). It is *strictly stronger*
than a bounds check. The driver hands the kernel `bytes.as_slice()` — the whole
blob, `safe_naive.rs:71`, `verus.rs:367` — so what a bounds check, and what
`get_unchecked`'s `requires i < v@.len()`, actually demand is that the
**slice**-relative index be in range, not the window-relative one. Guard exactly
that and the program still verifies and does something worse. §1c.

Two consequences of the same correction, both of which cost this pattern its
first headline:

- what §1b and §7 M4 disclose on a **one-window** input is `[0, body_start)` of
  the attacker's *own* window — its `nsuf` word and its own suffix table, eight
  bytes it wrote itself. "Leak" was the wrong word for it; **memory-safe and
  functionally wrong** is the right one, and §5's second table already said so
  one paragraph below the claim it contradicted;
- the maximum disclosure in that regime is `2 + 2*nsuf` attacker-written bytes
  and no input can change that, because the caller is entitled to every body byte
  (it can ask `s = content_len`) so the excess over entitlement is always a
  suffix of the header. It is structural, not an accident of the chosen input.

### 1c. The artefact: memory-safe, verified, and it reads a *neighbouring window*

**This is the claim `.memory/01-ladder.md` finding 5 needs and the one p17
originally shipped without.** One token, on the shipped `verus.rs`:

```rust
-        if start < end && start >= 0 {
+        if start < end && start >= -((off + body_start) as i64) {
```

`adversarial-crosswin-lo.bin` / `-hi.bin` are the pair that reads it out: two
64-byte windows, identical in every byte except window 0's 28 secret bytes
(`0x00` vs `0xff`), and window 1's third suffix `s = 122` puts the read at
absolute index 6 — inside the victim. `spec.md` has the layout and the reason
this input is exempt from the one-window rule.

Every binary below was built from the shipped sources, `-O3
-C debug-assertions=off --cfg slb_isolated`, Verus through `./verus_run.py`:

| binary | `crosswin-lo` | `crosswin-hi` | reads window 0? |
|---|---|---|---|
| `c-gcc` (R1) | `16140351554550698128` | `16701685314320143948` | **yes** |
| `safe_naive` (R2, shipped) | `15118011540968580209` | same | no |
| `safe_naive_absguard` (window-relative) | `15118011540968580209` | same | no |
| **`safe_naive_sliceguard`** (slice-relative, **zero `unsafe`**) | `16140351554550698128` | `16701685314320143948` | **yes** |
| `verus` (R5 shipped, 10 verified / 0 errors) | `15118011540968580209` | same | no |
| `verus_msonly` (shipped guard, spec stripped, 10/0) | `15118011540968580209` | same | no |
| `verus_absguard_msonly` (window-relative, 10/0) | `15118011540968580209` | same | no |
| **`verus_sliceguard_msonly`** (slice-relative, **10 verified, 0 errors**) | `16140351554550698128` | `16701685314320143948` | **yes** |

All exit 0. No panic, no sanitizer report (`gcc -O1
-fsanitize=address,undefined -static-libasan -static-libubsan` on R1 prints
**nothing** on either file and exits 0 on both, while printing the two different
checksums). Three rows of that table are the argument:

1. **`verus_sliceguard_msonly` is a program every one of whose obligations Verus
   discharges — `10 verified, 0 errors` — and whose output is a function of bytes
   another caller owns.** That is a provably memory-safe program that leaks. Be
   exact about the two edits it carries and why each is there: the **guard** is
   the one token, and it is what makes it read the neighbour; the **functional
   specification is stripped**, and that is not a second bug but the *probe* —
   it is how you ask Verus whether the memory-safety half stands on its own, and
   `verus_msonly` (row 6, same strip, shipped guard, no disclosure) and
   `nocheck_msonly` (still fails, on `0 <= base`) are its two controls. With the
   functional specification left in, the same one-token file is `9 verified,
   1 errors` and the single error is the functional invariant — i.e. Verus's
   objection to it is that it computes the wrong number, never that it reads the
   wrong memory.
2. **`verus_msonly` is the control that says the *guard* did it, not the spec
   stripping.** Same deletion of the functional specification, shipped guard, no
   disclosure.
3. **`safe_naive_sliceguard` is the control that says the *trusted accessor* did
   not do it.** Zero `unsafe`, plain safe Rust, indexing `buf[...]` with a bounds
   check on every access — same disclosure. Rust's bounds check permits it for
   exactly the reason Verus's `requires` does: the index it constrains is the
   slice's, and the slice is the whole blob.

Verus verdicts, my own runs, on mutants generated from `verus.rs` by exact-string
substitution (`--multiple-errors 20` changes nothing anywhere):

| mutant | shipped spec | functional spec stripped |
|---|---|---|
| `verus.rs` | **10 verified, 0 errors** | 10 verified, 0 errors |
| window-relative (`§7` M4) | 9 verified, 1 errors — `range_walk` invariant :311 | **10 verified, 0 errors** |
| **slice-relative** | 9 verified, 1 errors — `range_walk` invariant :311 | **10 verified, 0 errors** |
| guard deleted (`§7` M3) | 9 verified, 1 errors, **two** blocks: :311 **and** `0 <= base` :342, plus `note: while loop: not all errors may have been reported` | 9 verified, 1 errors — **`0 <= base`**, i.e. a memory-safety obligation |

The last row is the positive control `.memory/04-verus.md` item 2b asks for: with
the functional specification stripped, the probe can still see a memory-safety
failure, so `10 verified, 0 errors` on the slice-relative mutant is a real
positive and not an artefact of having deleted the specs.

#### Reproducing it — and why the control is not a file in this directory

`verus_leak.rs` is **not** shipped in `patterns/p17-http-range/`, and that is a
harness constraint rather than a choice:

- `.memory/05-layout.md`: *"Rung file stems are fixed … Do not invent variants;
  add an axis to `harness/build.py` instead."* `harness/build.py`'s
  `CONTROL_CELLS` / `RUST_SRC` / `ALL_CELLS` are closed lists used as argparse
  `choices`, so a new control cell is a harness change;
- **`check_verus_contract`** (`harness/check.py:2770`) requires every `.rs` in the pattern directory that
  opens a `verus!` block to be pinned in `spec.md`'s `verus.obligations`, and
  the same function at `:2880` fails the gate for any pinned file Verus reports errors
  on. The mutant as such is `9 verified, 1 errors`, so pinning it turns the gate
  **red**;
- the only 0-error form with the guard swapped and nothing else touched is the
  spec-stripped one, whose kernel `ensures` is `r == r` — which stage 5c
  (clause deletion) fails by design, because that is exactly §7's M2.

So it lives where §1a's and §7's other mutants live: generated into `.temp/`.
The generation is an exact-string substitution with a hit-count assertion, so it
cannot silently drift from `verus.rs`:

```sh
mkdir -p .temp/p17b/mirror/common .temp/p17b/mirror/patterns/p17-http-range
cp common/driver.rs .temp/p17b/mirror/common/
python3 - <<'PY'
src = "patterns/p17-http-range/verus.rs"
out = ".temp/p17b/mirror/patterns/p17-http-range/verus_leak.rs"
t = open(src).read()
old = "if start < end && start >= 0 {"
new = "if start < end && start >= -((off + body_start) as i64) {"
assert t.count(old) == 1
open(out, "w").write(t.replace(old, new))
PY
./verus_run.py .temp/p17b/mirror/patterns/p17-http-range/verus_leak.rs
#   -> 9 verified, 1 errors   (only the range_walk invariant, verus_leak.rs:311)
```

`.temp/p17b/mkvariants.py` does that plus the spec-stripped and safe-Rust
variants; `.temp/p17b/demo.sh` builds them and prints the table above.

**If the disclosure claim is ever to be gate-certified rather than reproduced by
hand, the way to do it is not to relax any of the three rules above.** It is to
ship the mutant with its *specification* moved to match its guard — replace
`start >= 0` with `start >= -(off + body_start)` in `range_walk` as well as in
the exec code — which verifies `10 verified, 0 errors` **with** a load-bearing
functional postcondition, and to pin it in `spec.md` as a second obligations
entry with its own twin, its own `SLB-TRUSTED-ARGUMENT` block and its own
`driver.regions` entry. That is a different and arguably sharper artefact — *a
program proved to meet its specification, whose specification is the bug* — and
it costs a full second Verus file in stages 5a/5c/5c-req/5c-twin on every gate
run. It was not done here because TASK_012 is scoped to one control, one input
and one table, and because it is a design decision rather than an engineering
one.

## 2. Performance

`-O3`, `isolated`, marginal `Ir` per kernel call (two callgrind runs at
`n_iters` 100/200, differenced — the recipe `harness/check.py` step 3b uses;
reproduced independently here and equal to the gate's own numbers in
`results/gate/p17-http-range.json`). `small` is a 506-byte window serving
`498+251+122 = 871` bytes across 3 requests; `large` is a 4093-byte window
serving `4085+2041+1019 = 7145`. Strides, all three suffix values and the totals
differ mod 4, 8 and 16 — `inputs/gen.py` asserts it before writing a byte.

| rung | small | large | Δ vs R4 (small) | Δ vs R4 (large) |
|---|---:|---:|---:|---:|
| R1 `c-gcc` | 7065.28 | 57257.28 | +1856.6 | +15977.6 |
| R1h `c-gcc-h` | 7074.28 | 57266.28 | +1865.6 | +15986.6 |
| R1 `c-clang` | **5163.28** | **41234.28** | −45.4 | −45.4 |
| R1h `c-clang-h` | 5182.28 | 41253.28 | −26.4 | −26.4 |
| **R2 safe-naive** | **8832.70** | **71572.70** | **+3624.0 (+69.6%)** | **+30293.0 (+73.4%)** |
| **R3 safe-tuned** | **5240.70** | **41311.70** | **+32.0 (+0.61%)** | **+32.0 (+0.08%)** |
| R4 unsafe | 5208.70 | 41279.70 | — | — |
| R5 verus | 5207.70 | 41278.70 | −1.0 | −1.0 |

Read per unit of the thing each rung is doing — and the units are *measured*,
not fitted, from a 34-point sweep (§3b) rather than from these two points:

- **R3 costs zero per byte.** Its marginal rate is **5.7500 Ir per folded byte**
  and R4's is **5.7500** — equal, exactly, over 34 consecutive served lengths
  (§3b). Its whole cost is O(1) in the bytes: **+32 per call** on
  the shipped inputs, which serve three ranges, and **+16 (served length ≡ 0 mod
  4) or +18** on the sweep's one-range windows. Those two points interpolate to
  roughly *9–10 per call plus 7–8 per range request* — an interpolation from two
  shapes, not a fit, and p16's `7 + 7·nrec` is the same order. Either way it
  *shrinks* as a fraction of the call: 0.61% on `small`, 0.08% on `large`. That
  is the **fifth pattern in a row** where idiomatic safe Rust is free
  (`.memory/01-ladder.md` findings 3 and 9).

  **The shipped R3 is not the cheapest admissible spelling, and it is
  deliberately not swapped.** ⚠ **Corrected at TASK_018.** This paragraph used
  to say that `.temp/p05r3/v17/tuned_suffix.rs` (§10 row 3) *"satisfies **all
  four** of p17's `required` entries: `i64` endpoints, the one conjunctive `if
  start < end && start >= 0`, `nserved` folded, no `Range:` text parsing"*.
  **That was false of the file** (TASK_017_REVIEW B1): `tuned_suffix.rs` has no
  `end` binding anywhere in its code — the only two occurrences of the word are
  in doc comments — and writes `start < content_len`. Under the
  **named-spelling standard** (`spec.md`'s `idiom.why`; policy adopted at
  TASK_018 for all six patterns, after measuring) row 3 is **out of contract on
  two entries**, `required[0]` and `required[1]`.

  **The correction changes the attribution and not the number.**
  `.temp/p18/v17/r3_incontract.rs` keeps `let start: i64`, `let end: i64`, the
  literal `if start < end && start >= 0` and `n = end - start`, and respells
  only the suffix-table walk and the byte fold — the two things `spec.md` says
  are *not* restricted. It is **in contract**, and it compiles to
  **byte-identical machine code** to `tuned_suffix.rs`: `md5_fn
  532201c70eeb5fea…`, `md5_raw 12fd8faca909d0e0…`, `n_fn 135`, both `-O3
  isolated`. It measures **5189.70 / 41260.70**, i.e. **51.00 below the shipped
  R3 on both inputs** (`17·nsuf` exactly over eight generated `nsuf` points,
  §10), so `+32` is the cost of *this* R3's spelling and is **not** what safety
  costs on this kernel. See §10a.

  Three reasons it is not swapped in, adjudicated at TASK_016_REVIEW Part 5 and
  not a preference:

  1. **the cheaper R3 beats its own R4 too** — `R3′ − R4 = −19.00` on both
     shipped inputs. Swapping R3 alone would publish "safe Rust beats unsafe
     Rust" from an **unmatched pair**, which is exactly the TASK_014/TASK_015
     defect, this time committed as a shipped cell;
  2. **an honest swap has to move R4 as well**, and the matched pair does not
     hold still: TASK_015_REVIEW's `nsuf` sweep has `R3′ − R4` running +1 … −73
     across `nsuf` 1…8, so the swap produces a *different* number, not a stable
     one;
  3. **no swap terminates.** R4 is defined by *permission*, so
     `inf(R4) ≤ inf(R3)` by construction (`.memory/01-ladder.md` finding 14) and
     chasing the cheapest admissible R3 chases a quantity with no fixed point.

  What p17 publishes is therefore a **matched pair by declaration, not an
  optimum** — and that sentence, not the `+32`, is what a reader should carry
  away from this row.
- **R2 is O(bytes served):** **10.0000** Ir per folded byte against R3/R4's
  **5.7500**, i.e. **+4.2500 per byte**. `.memory/01-ladder.md` records p16's
  swept value as exactly 4.2500 on a completely different kernel, and p16's own
  10.00 / 5.75 pair; p17 reproduces **all three exactly**, not to four decimals
  with an offset (§3b). That is a strong sign the constant is a property of
  *rustc's checked indexed byte fold*, not of either pattern.
- **R5 is free**, as on every pattern: byte-identical to R4 at `-O3`
  (`md5_fn 45064db24a5b` both, `md5_raw` equal, padding 9/9 B), `norel` at `O0`
  where the crate names differ in length. The −1.00 Ir is driver-side, outside
  the kernel symbol, exactly as p02's ±2 was.
- **R1h − R1, the cost of the check inside C: gcc +9.00, clang +19.00, on both
  inputs.** Three requests are served per call on both, so that is **+3.0 (gcc)
  and +6.3 (clang) instructions per range request, flat in the size of the
  range**. The check that decides between "serve the body" and "serve the cache
  metadata" costs **0.13% (gcc) / 0.37% (clang)** of the call on `small` and
  0.02% / 0.05% on `large`.
- **clang beats gcc by 27% here** (5163 vs 7065 on `small`). p16 found gcc's
  deficit there was a *flag default* rather than a codegen limit —
  `-funroll-loops` closed it — and §2a checks the same thing here rather than
  assuming either way.

### 2a. gcc's deficit is a flag default, not a codegen limit

`.memory/01-ladder.md` finding 9: *before reporting any gcc-vs-clang gap,
establish whether it is a default or a capability.* Rebuilt with
`-funroll-loops` and nothing else changed (both cells still print
`18416420189787787870`):

| build | small | large | Ir per folded byte † |
|---|---:|---:|---:|
| `c-gcc -O3` (shipped) | 7065.28 | 57257.28 | **8.0000** |
| `c-gcc -O3 -funroll-loops` | **4813.28** | **38541.28** | 5.3758 |
| `c-clang -O3` (shipped) | 5163.28 | 41234.28 | 5.7493 |
| `c-clang -O3 -funroll-loops` | 5163.28 | 41234.28 | 5.7493 — the same numbers to the instruction; clang already unrolls |

† these four rates are **two-point** estimates from the two columns to their
left, not swept — the C cells were not put through §3b's 34-length sweep. Their
*differences* are exact (both points share the residue mix); the absolute values
carry a residue term of the same order as §3b's 8-instruction sawtooth, i.e.
about ±0.002 Ir/byte at these lengths.

So gcc is 37% behind by default and **6.8% ahead when told to unroll**, exactly
as on p16. Two things worth keeping:

- gcc's default fold runs at **exactly 8.0000 Ir per folded byte**, which is
  `.memory/01-ladder.md`'s independently measured constant for a **rolled,
  unchecked** byte-Horner loop (p16 §3.4, four sightings). Two patterns, two
  compilers, same number — it is a property of the loop body, not of either
  pattern;
- `-funroll-loops` is a no-op on clang here, bit for bit, so the flag is
  isolating gcc's unroller and nothing else.

**Do not quote the shipped gcc column as "C's cost".** The same-backend
comparison is `c-clang`, and it is what §2 uses for every C-vs-Rust statement.

### 2b. Wall clock: the +73% instruction tax costs 0.0% of the time

`results/p17-http-range.json`, min of 30 interleaved repetitions pinned to
CPU 3, `-O3 isolated`:

| rung | small min (ms) | large min (ms) |
|---|---:|---:|
| R1 c-gcc | 20.17 | 76.91 |
| R1h c-gcc-h | 20.16 | 76.43 |
| R1 c-clang | 20.11 | 77.22 |
| R1h c-clang-h | 20.15 | 77.29 |
| R2 safe-naive | 20.30 | 77.18 |
| R3 safe-tuned | 20.24 | 77.45 |
| R4 unsafe | 20.34 | 77.29 |
| R5 verus | 20.26 | 77.84 |

All eight fall in 20.11…20.34 ms and 76.43…77.84 ms — spreads of **1.1% and
1.8%** — and R2, which executes **73% more instructions than R4**, is 0.04 ms
*faster* on `small` and 0.11 ms faster on `large`.

Totals are the wrong instrument here (13–26% of them is fixed startup), so the
per-call figure below is **differenced over `n_iters`** — `.memory/01-ladder.md`
finding 9 records that dividing a total wall time by a byte count is how p16's
first cycle arithmetic went wrong. `large.bin` at `n_iters` 2000 and 12000, min
of 15 each, pinned to CPU 3, 7145 bytes folded per call:

| rung | t @ 2000 | t @ 12000 | Δ per call | ns per folded byte |
|---|---:|---:|---:|---:|
| R1 c-clang | 20.92 ms | 76.94 ms | 5.60 µs | **0.7841** |
| R2 safe-naive | 20.79 ms | 77.32 ms | 5.65 µs | **0.7912** |
| R3 safe-tuned | 20.87 ms | 76.96 ms | 5.61 µs | **0.7851** |
| R4 unsafe | 20.81 ms | 77.33 ms | 5.65 µs | **0.7911** |
| R5 verus | 20.89 ms | 77.12 ms | 5.62 µs | **0.7870** |

**Every rung folds a byte in 0.784–0.791 ns — a 0.9% spread across a 73% `Ir`
gap.** The mechanism is p16's and is not mysterious: the fold is
`acc = acc*31 + b`, a **serial dependence chain**, so the loop is latency-bound
and the extra bounds-check instructions issue into slots that were idle anyway.

*Frequency caveat, and it is why no cycles/byte figure is quoted as a
measurement.* **The reason first given here was wrong** — it read
`scaling_cur_freq` "ramping 800 MHz → 902 MHz" as evidence about the clock, and
that file is unusable on this box: it reports **800 MHz while a pinned core is
demonstrably retiring ~2.8 G dependent `addq`s per second**, measured twice
(TASK_011_REVIEW: `800000` for a six-second sample; TASK_012: five consecutive
samples, all `800000`±20, taken while the probe below was running on that core).
`.memory/00-environment.md` carries the durable form: never derive a clock from
that file; time a 1-cycle-latency dependent chain instead.

**The conclusion survives the correction, for a better reason.** The dependent-add
probe, same source and same pinning, does not give the same answer in different
sessions:

| session | CPU 3 | CPU 5 |
|---|---|---|
| TASK_011_REVIEW | 3801–3888 MHz | 3771–3874 MHz |
| TASK_012 | 2764–2861 MHz | 2551–2719 MHz |

That spread is not noise, it is the part number: a Xeon Gold 6230 is 2.1 GHz
base, **3.9 GHz single-core turbo and ~2.8 GHz all-core**, and this is a *shared,
containerised* box, so the clock during any measurement is set by what other
tenants are doing. 0.784–0.791 ns per folded byte is therefore **2.2 cycles/byte
at the all-core clock and 3.1 at the one-core clock** — an interval a third of
its own width, not a figure. p17 does not claim a cycles/byte measurement, and a
quotation of 3.02–3.05 (p16's interval) would be a *new* overclaim of exactly the
species this file has just had to correct: a number lifted from a clock that was
measured in a different session from the wall time it divides.

**What would earn it** is measuring the clock in the same session as, or
interleaved with, the wall-clock reps — the probe is `.temp/review011/clock.c`
and it costs 300 ms. That was not done here, and until it is the wall table
above should be read as it is written: as *ratios between rungs*, which the
30-interleaved-rep / min protocol makes robust to a clock that moves, and not as
absolute times.

So the honest headline for the cost half is **two sentences**: *safe-naive Rust
pays a real 4.25 Ir per byte on an indexed byte fold LLVM cannot hoist — and on
this kernel it buys back nothing, because the kernel was never throughput-bound.*
`.memory/01-ladder.md` already records `Ir` and wall clock disagreeing in
*direction* on p02 and in *magnitude* on p16; p17 is the third instance and the
cleanest, because the per-call time is differenced rather than divided.

**And the null was bracketed at 30 code layouts, where it SURVIVES**
(TASK_030_REVIEW / TASK_031). Code layout moves wall clock by up to 27% at an
unchanged instruction stream and it withdrew two patterns' `ns` rows (p01
`small`, p07 R2 — `.memory/03-measurement.md`, "Code layout: the 32-byte fetch
grid"). p17 has **no mode**: rebuilt at 30 layouts per rung with `md5_fn_norel`,
`n_fn` and stdout invariant at every one, the rung-to-rung gaps are

```
                    published   pooled    mode0    mode16
small  R2 vs R4        -0.22%   -0.09%   -0.12%   -0.18%
small  R3 vs R4        -0.50%   -0.15%   -0.13%   -0.27%
large  R2 vs R4        -0.15%   +0.03%   -0.02%   +0.05%
large  R3 vs R4        +0.20%   -0.04%   -0.06%   +0.13%
```

— under 0.5% everywhere, in both modes, on both inputs; no address bit separates
the population (best ratio ×0.9989, never a perfect split); and the *whole*
30-layout band is 0.84 … 1.40% on `small` and 1.05 … 1.37% on `large`, i.e. the
same size as the 1.1% / 1.8% eight-cell spread quoted above. A null measured at
one layout could be luck; this one is measured at thirty.

The negative comes with the mechanism, not just the number. p17's loops **do**
change 32-byte geometry with layout, on four of them at once, and nothing moves:

```
safe_naive loop2 [kernel+0xb0, +0xcf)   31 B  win32[1,2]   small x0.9992  large x0.9987
safe_tuned loop3 [kernel+0x1b0,+0x1ca)  26 B  win32[1,2]   small x0.9999  large x0.9975
safe_tuned loop2 [kernel+0x130,+0x180)  80 B  jcc32[0,1]   small x0.9999  large x0.9975
unsafe     loop0 [kernel+0x60, +0x17f) 287 B  win32[9,10]  small x1.0015  large x1.0006
```

**The geometry flip is universal; being front-end-bound is not**, and 2b has
already established that this kernel is latency-bound on a serial Horner chain
with idle issue slots — which is exactly a kernel that cannot pay for an extra
fetch window. p17's layout negative and its instruction-tax null have one cause.

⚠ The C cells are **unbracketed**: both levers are rustc / rust-lld side, so
`c-gcc`, `c-clang` and the `-h` twins were built at one layout only. The
conclusion above is an R2/R3-vs-R4 statement and does not rest on them, but the
`ns` column's four C rows have no band of their own.

### 2c. Static counts, and why they are not a proxy

`-O3 isolated`, `nm --print-size` extent, `n_fn` / padding-excluded:

| cell | static | marginal Ir/call (small) |
|---|---:|---:|
| c-gcc | 64 / 61 | 7065.3 |
| c-gcc-h | 67 / 63 | 7074.3 |
| c-clang | 105 / 101 | 5163.3 |
| c-clang-h | 114 / 110 | 5182.3 |
| **R2 safe-naive** | **90 / 88** | **8832.7** — the *smallest* Rust cell and the dearest |
| **R3 safe-tuned** | **152 / 148** | **5240.7** — the *largest* cell in the ladder and near the cheapest |
| R4 unsafe | 120 / 116 | 5208.7 |
| R5 verus | 120 / 116 | 5207.7 |

That inversion is `.memory/01-ladder.md` finding 3's sharpest form, reproduced:
**R3 is statically the largest cell in the whole ladder and dynamically within
0.6% of unsafe**, while R2 is the smallest Rust cell and 70% dearer. A static
instruction count is not a proxy for anything here.

`binary_text_bytes`: ~2.0–2.1 KB for the four C cells, ~259 KB for the four Rust
ones. That is the Rust standard library and it is not a kernel property; it is
recorded because `results/*.json` carries it and it must not be misread.

### 2d. Vectorisation is not a confound

`vector_regs` over all 32 cells: **10 have `['xmm']` and 22 have none**, and all
ten are `whole`-mode cells where the measured symbol is `main` — the driver and
the payload `to_vec`, not the fold. The **fold is scalar in every rung at
`-O3 isolated`**, so every number in §2 and §3 is a scalar loop compared with a
scalar loop. (p16's figure was 9 of 32, the same shape.)

### 2e. `whole` mode

Comparing like with like — `isolated` against `whole` (the kernel having been
inlined into `main`), marginal `Ir` per call, from `results/gate/*.json`:

| rung | small isolated → whole | large isolated → whole |
|---|---|---|
| R2 safe-naive | 8832.7 → 9699.7 (**+867**) | 71572.7 → 78713.7 (**+7141**) |
| R3 safe-tuned | 5240.7 → 5167.7 (−73) | 41311.7 → 41238.7 (−73) |
| R4 unsafe | 5208.7 → 5376.7 (**+168**) | 41279.7 → 43014.7 (**+1735**) |
| R5 verus | 5207.7 → 5406.7 (+199) | 41278.7 → 43044.7 (+1766) |
| R1 c-gcc | 7065.3 → 7057.3 (−8) | 57257.3 → 57249.3 (−8) |
| R1 c-clang | 5163.3 → 5135.3 (−28) | 41234.3 → 41206.3 (−28) |

R2's +10% amplification when inlined is the third pattern to show it (p01's
`large`, p16 on both inputs), so it is now a reproducible effect rather than an
observation. **What is new here is that R4 and R5 get *worse* when inlined too**
— +0.24 Ir per folded byte, which p16's R4 did not — while R3 improves. Recorded
as an observation, not explained; it is a difference of two builds and nothing in
§1–§3 rests on it.

### 2f. `O0`, recorded and never quoted as a perf claim

`.memory/02-bench-rules.md`: never report a perf number from an `O0` row. For the
record, `small`, marginal Ir/call: c-clang 12398, c-gcc 16783, safe-tuned 20681,
unsafe/verus 30854, safe-naive 53583. The *ordering* inverts against `-O3` —
safe-tuned is the **cheapest Rust cell** unoptimised and unsafe is 49% dearer
than it, because `get_unchecked` is a real call until it is inlined, where at
`-O3` unsafe is the cheapest and safe-tuned is 0.6% behind it. That inversion is
exactly why the rule exists.

## 3. The decomposition

**This section comes before the claim in §2, not after it.** Every variant below
is built under `.temp/p17/decomp/` from `safe_naive.rs` with **only the kernel
body swapped** — same driver, same inputs, and all five print
`18416420189787787870` and `10613012665269285418`, so they are semantically
equivalent on well-formed input and only the codegen differs.

`-O3 isolated`, marginal Ir per call. R4 = 5208.70 / 41279.70; the gap R2 must
explain is **+3624.00 / +30293.00**.

| # | variant | small | large | Δ vs R4 small | Δ vs R4 large | % of R2's gap removed |
|---|---|---:|---:|---:|---:|---|
| — | **R2 as shipped** | 8832.70 | 71572.70 | +3624.0 | +30293.0 | — |
| v1 | inner byte fold → slice + iterator `fold` | 5262.70 | 41333.70 | **+54.0** | **+54.0** | **98.51% / 99.82%** |
| v2 | suffix-table walk → reslice (`&buf[off+2..]`, `&tab[2i..2i+2]`) | 8804.70 | 71544.70 | +3596.0 | +30265.0 | 0.77% / 0.09% |
| v3 | both (this is R3's algorithm) | 5240.70 | 41311.70 | +32.0 | +32.0 | 99.12% / 99.89% |
| v4 | the signed arithmetic widened to **`i128`** | 12329.70 | 100165.70 | +7121.0 | +58886.0 | −96% (much worse) |
| v5 | **all-unsigned**: no `i64`, no `as usize`, semantically identical | 8826.70 | 71566.70 | +3618.0 | +30287.0 | **0.17% / 0.02%** |
| — | R3 `safe_tuned` as shipped | 5240.70 | 41311.70 | +32.0 | +32.0 | |

**The delta lives entirely in the inner byte fold.** Changing only the fold
removes 98.5% / 99.8%; changing only the walk removes 0.8% / 0.1%. The two
removals sum to 3570 + 28 = 3598 against the 3592 that changing **both** removes,
so the interaction term is −6 instructions — there is essentially none. Same
shape as p16, on a kernel with a different loop structure.

**v5 is the row the task predicted and it came out the other way.** TASK_011
predicted that the signed↔unsigned conversions would cost something in the safe
rungs specifically — *"the cost of the check is not the comparison, it is the
conversion"*. Measured: rewriting the kernel with **no signed arithmetic at all**
(the guard `start < end && start >= 0` is exactly `0 < s && s <= content_len` in
unsigned terms, so this is a semantics-preserving rewrite) moves the number by
**4 instructions per call, flat, zero per byte** — 0.17% of the gap on `small`
and 0.02% on `large`. **The prediction is contradicted.** The tax is the checked
indexed byte fold, and it is the same 4.25 Ir/byte p16 measured on a kernel with
no signed arithmetic in it at all.

**What the width *does* cost, since v4 measures it:** `i128` index arithmetic
costs **exactly +4.0000 Ir per folded byte** over `i64` — a 40% increase in the
whole kernel — because the index arithmetic is inside the inner loop and doubles
in width there. So width is expensive and *signedness* is free, which is the
opposite of the shape the prediction assumed.

### 3b. The sweep: is it a line, or one residue wearing the label of a constant?

Two points cannot distinguish a slope from a residue, and this project has
stepped in that trap three times. 34 consecutive served lengths (200…233 — two
full mod-16 cycles plus the endpoints), one request per window serving the whole
body, so **folded bytes per call is exactly the swept length** and the outer loop
is held at one iteration. `.temp/p17/sweep/`, 340 callgrind runs.

Least squares over all 34 points:

| rung | Ir/call | max │residual│ |
|---|---|---:|
| R2 safe_naive | `9.9994 · folded + 75.20` | **0.48** |
| R3 safe_tuned | `5.7648 · folded + 113.24` | 8.97 |
| R4 unsafe | `5.7621 · folded + 96.36` | 7.48 |
| v4 i128 | `13.9994 · folded + 80.20` | **0.48** |
| v5 unsigned | `9.9994 · folded + 71.20` | **0.48** |

R2, v4 and v5 are **exactly linear** — residual under half an instruction over 34
points. R3 and R4 are not, and their residual is the same 8.97/7.48 sawtooth,
because both use LLVM's 4×-unrolled fold with a scalar epilogue. Differencing at
**lag 4** (same length mod 4) removes it and gives the true rates:

| rung | Ir per folded byte (lag-4, **zero-residue pair** sw228 → sw232) | (lag-4, mean of 30 — **contaminated**, see below) |
|---|---:|---:|
| R2 safe_naive | **10.0000** | 9.9991 |
| R3 safe_tuned | **5.7500** | 5.7491 |
| R4 unsafe | **5.7500** | 5.7491 |
| R5 verus | **5.7500** | — |
| v4 i128 | **14.0000** | 13.9991 |
| v5 unsigned | **10.0000** | 9.9991 |

**The right-hand column was published first and it is 0.0009 low for a reason
that has nothing to do with the kernel** (TASK_011_REVIEW, minor 3; re-measured
independently at TASK_012 with `.temp/p17b/lag4.py` — four rungs × three lag-4
pairs, plus v4 and v5 at the zero-residue pair, all fresh callgrind runs, so
**every cell in the left-hand column is measured and none is derived from the
differences**). Marginal `Ir` per call carries a **fractional** part that depends
on the *input*, identical across every Rust binary, and it is the cost of
`println!`-formatting a final `acc` with a different number of decimal digits.
It cancels in a same-input difference and biases a cross-input *rate*:

| lag-4 pair | fractional residue | R2 | R3 | R4 | R5 |
|---|---|---:|---:|---:|---:|
| sw200 → sw204 | 0.70 / 0.41 | 10.1775 | 5.9275 | 5.9275 | 5.9275 |
| sw201 → sw205 | 0.30 / 0.11 | 9.9525 | 5.7025 | 5.7025 | 5.7025 |
| **sw228 → sw232** | **0.00 / 0.00** | **10.0000** | **5.7500** | **5.7500** | **5.7500** |

So the honest statement is *stronger* than the published one: at the pair where
the driver term is exactly zero on both sides, p17 reproduces **p16's constants
exactly** — 10.00 for the checked indexed fold, 5.75 for the unchecked one, and
4.2500 for the difference — rather than to four decimals with an offset. Quote
differences, or the zero-residue pair; never a mean of contaminated rates.

and the differences, which are exact because both sides see the same residue:

| difference | per folded byte | per call |
|---|---:|---:|
| **R2 − R4** | **+4.2500** | — |
| **R3 − R4** | **0.0000** | **+16 (len ≡ 0 mod 4) / +18 otherwise** ‡ |
| v5 − R2 (the whole signed↔unsigned round trip) | **0.0000** | **−4.00, every row** |
| v4 − R2 (`i64` → `i128`) | **+4.0000** | — |

`R3 − R4 ∈ {16, 18}` on all 34 lengths and `v5 − R2 = −4.00` on all 34; neither
takes any other value. **The residue modulus that matters here is 4** — the
unroll factor — as on p16 and p01; p02's was 16.

‡ these sweep windows serve **one** range each, where the shipped inputs serve
three and R3 − R4 is +32. So the 16/18 is a per-call *plus* per-request constant
that this sweep cannot separate — it holds the request count at 1 and varies only
the bytes, which is exactly what is needed to establish the **per-byte** rate and
is not enough to split the constant. See the R3 bullet in §2.

## 4. TCB tally

**TCB: 6 lines across 3 items**, counted per `.memory/04-verus.md` — *every*
`external_body` item individually, not just the interesting one, because
under-counting is how the pilot's fatal defect hid in plain sight.

| # | item | lines | `requires` | `ensures` | in the regime? | why it is trusted |
|---|---|---:|---|---|---|---|
| 1 | `get_unchecked` | 1 | `i < v@.len()` | `r == v@[i as int]` | **yes** (`external_body` + `unsafe` + non-empty `ensures`) | vstd ships no spec for `<[T]>::get_unchecked`. It is **half** of p17's security argument — see §5 |
| 2 | `load_input` | 4 | — | — | no (`external_body`, no `ensures`, no `unsafe`) | argv, file I/O, little-endian decoding, delegated to `common/driver.rs` |
| 3 | `emit` | 1 | — | — | no | `println!` is not verifiable |

Zero `assume(...)`, zero `assume_specification`, zero `external_fn_specification`,
and exactly **one `unsafe` token in the whole file**, inside item 1's body — the
gate reports *"scanned for `unsafe` outside a trusted body: ['verus.rs'] +
['common/driver.rs'] (1 token(s) inside a trusted body)"*.

Identical in size to p16's and p01's, and §6(b) records the one place where it
was tempting to grow it and was not: `load_input` could have carried
`ensures r.2@.len() <= i64::MAX` and saved the driver a run-time check. That
would have been an axiom about a `Vec` the verifier never sees constructed, on an
item with no possible twin, and it was rejected.

Obligations: **10** shipped, **11** under `--cfg slb_twin`. Both pinned in
`spec.md` with the arithmetic beside them, and every term measured rather than
asserted — `./verus_run.py patterns/p17-http-range/verus.rs --verify-function
<name> --verify-root`:

| item | queries | why |
|---|---:|---|
| `nsuf_at`, `suf_at`, `range_fold` | 0 each | non-recursive `spec fn` |
| `fold_bytes` | 1 | recursive → a termination query |
| `range_walk` | 1 | recursive → a termination query |
| `get_unchecked`, `load_input`, `emit` | 0 each | `external_body` — trusted, not verified |
| `kernel` | 3 | the body + one per loop body, and there are two loops |
| `main` | 5 | the body + the driver loop + one per `by (nonlinear_arith)` / `by { .. }` sub-proof in the two ghost blocks |
| **total** | **10** | |
| `slb_twin_get_unchecked` (`--cfg slb_twin`) | +1 | one function, no loop, no `by`-block → **11** |

p16's total is also 10, with the same 1+1+3+5 decomposition. That is a
coincidence of skeleton — two spec fns, two kernel loops, the same driver — and
is **not** evidence that the two proofs are equally strong. `.memory/04-verus.md`
already says an unchanged obligation count is evidence of nothing; two patterns
landing on the same number is the same statement from the other side.

### What `work_per_call` is, and how much slack the floor leaves

`work_per_call` is the **window in bytes** (`stride`): 506 on `small`, 4093 on
`large`, deliberately different so `check.py`'s `d(Ir)/d(work)` assertion has two
probe shapes. `model.py` declares **no** `min_ir_per_work`, so the harness
default of 0.25 Ir/byte applies unchanged.

**One honest difference from p16, and it goes the wrong way.** p16 could say the
window is a strict *over*-estimate of the bytes folded, so its derived floor
erred strict. p17's is an **under**-estimate: every suffix serves a slice of the
*same* body, so `nsuf` requests can each serve nearly all of it — the shipped
inputs fold 871 bytes per 506-byte window (**1.72×**) and 7145 per 4093-byte
window (**1.75×**). The floor is therefore looser here than the work actually
done.

The gate reports: *64 cell/probe pairs, marginal Ir per call 5135…436297, all
above the derived floor, tightest margin **40.3×**; d(Ir)/d(work) 10.06…106.69.*
So this stage tolerates a ~97.5% loss of work before it objects, and — as
`.memory/02-bench-rules.md` insists — it is a **NOT-COLLAPSED smoke test**, not
an anti-collapse gate. What certifies that the ranges were served is step 2, the
model checksum, which folds every served byte *and* the served count.

## 5. Why the `ensures` IS the security property here — the opposite of p16

**This is the structural result and it is the reason p17 was worth building.**

p16's `spec.md` argues, correctly for p16, that a read-only kernel's security
property cannot be an `ensures`: "no byte outside the window was read" is not a
property of the return value, because a kernel could read out of bounds and
discard the byte. So for p16 the whole memory-safety claim is the trusted
accessor's discharged `requires i < v@.len()`.

**p17 has two harms and that argument covers only one of them.**

| harm | the index it reads from | `i < v@.len()` | `r == range_fold(..)` |
|---|---|---|---|
| `s > len` — reads before the allocation | negative | **excludes it** | excludes it |
| `content_len < s <= len` — reads the window's own `nsuf` word and suffix table | small, non-negative, **inside `buf`** | **holds** | **excludes it** |

The second harm is a defect that is **memory-safe**. There is no precondition on
any accessor that rejects it, because the access it makes is legal — that is what
"in bounds" means. The only thing in `verus.rs` that rejects it is
`r == range_fold(buf@, off as int, len as int)`, because `range_fold`, unlike any
bounds property, *says which bytes* the result is a fold of.

**Demonstrated, not asserted, in §7 M4:** replace `start >= 0` with
`start >= -(body_start as i64)` — guard the window-relative index instead of the
logical start — and Verus reports **9 verified, 1 error**, the one error being
the functional loop invariant. Every `get_unchecked` precondition discharges.
Every memory-safety obligation in the file is met, and the program serves the
attacker its own metadata. Strip the functional specification from that mutant
and it is `10 verified, 0 errors`: the memory-safety half discharges on its own.

**And the version that is memory-safe by exactly the standard a bounds check
sets — no more — reads *another caller's* bytes.** `start >= -(off + body_start)`
is what `requires i < v@.len()` actually demands of a kernel handed the whole
blob; it also verifies `10 verified, 0 errors` with the functional specification
stripped, and on `adversarial-crosswin-{lo,hi}.bin` its output moves with the
victim window's secret. §1c has the numbers. So the row of the table below is not
"the functional `ensures` is the only thing that rejects the harm" as a nicety:
it is the only thing standing between this program and a cross-tenant read.

So p16 and p17 bracket the question this project has been asserting since
finding 2:

| | what rules the harm out |
|---|---|
| p16, unsigned underflow, walks forward off the end | the trusted accessor's `requires`; **no** `ensures` states it |
| p17 harm 2 (`s > len`), signed underflow, indexes before the buffer | the same `requires` |
| **p17 harm 1 (`content_len < s <= len`), indexes inside the buffer** | **the functional `ensures`, and nothing else** |

Three consequences worth stating plainly.

1. **"Verified memory-safe" is a strictly weaker statement than "verified
   correct", and p17 puts a program between them.** Not a hypothetical program:
   a one-token edit of the shipped one, which discharges every safety obligation
   (`10 verified, 0 errors` with the functional spec stripped) and whose checksum
   is a function of a neighbouring window's bytes (§1c). The distinction has been
   in `.memory/` since finding 2 with no measurement behind it; this is the
   measurement.
2. **The same gap exists in the language, not just in the verifier.** §1a: safe
   Rust with the same conjunct deleted prints C's wrong value on the leak input
   and panics on the OOB input; §1c: safe Rust with the *slice*-relative guard,
   zero `unsafe`, a bounds check on every access, discloses the neighbour. Rust's
   bounds check and Verus's accessor precondition are the *same* property, and
   they draw the *same* line — and that line is the **slice**, which on this
   pattern is the whole blob.
3. **What is machine-judged and what is a human reading.** Of p17's trusted
   clauses:

   | clause | judged by | what that judgement is worth |
   |---|---|---|
   | `get_unchecked` `requires i < v@.len()` | 5a (mentions every parameter its body uses), 5c-req (not a tautology), 5c-twin (strong enough to license `v[i]`) | 5c-twin is the only one that judges *strength*. And on p17 even a perfect judgement of it certifies only the *third* row of §5's first table. |
   | `get_unchecked` `ensures r == v@[i as int]` | 5c (deleting it must break the file — measured, 7 verified / 3 errors), identity, Miri | **Completeness** of this `ensures` w.r.t. the body's operations is judged by **no oracle at all** — §6 (b). |
   | `kernel` `ensures r == range_fold(..)` | 5c (deleting it must break the file — measured, 9 verified / 1 error), and `model.py` re-deriving it on the gate's sampled calls across every input | **This is the clause the pattern's security rests on**, which is new: on p01, p02 and p16 the kernel `ensures` was the value and the accessor's `requires` was the security. |

## 6. Trusted items — the arguments no oracle can make

SLB-TRUSTED-ARGUMENT verus.rs get_unchecked

(a) **Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*v.get_unchecked(i)`; the twin's body is `v[i]`. The standard
library documents `get_unchecked(i)` as `index(i)` with the bounds check
removed, so `v[i]` is the same operation on the same slice at the same index,
and Verus checks the bound that `v[i]` needs against the same `requires`. It is
not a different operation, not a copy of the slice, and not defensive — a
defensive twin `if i < v.len() { v[i] } else { 0 }` cannot satisfy the `ensures`
and fails the stage rather than passing it.

(b) **Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes *as the body stands*. The body is a single expression
performing exactly one unchecked read, at index `i` of slice `v`. `ensures r ==
v@[i as int]` names that index and that slice, so a twin cannot satisfy the
postcondition without performing the same read, and the `requires` is therefore
forced to be strong enough for it. It is complete **only because the body is one
line**, and *nothing mechanical enforces that*: a second unchecked read the
`ensures` never mentions — the classic `let _peek = *v.get_unchecked(i + 1);` —
is invisible to 5a, 5c, 5c-req and 5c-twin alike, because the twin only has to
satisfy the `ensures` and the `ensures` does not mention it. Two backstops exist
and both are tests rather than proofs (`.memory/02-bench-rules.md`, measured at
TASK_010): stage 3c identity catches the case where the extra read is added to
`verus.rs` alone, because R5's machine code then differs from R4's and the pin
here is `exact`; and step 8 Miri catches the case where the same read is added to
`unsafe.rs` too, but **only on inputs that actually reach the boundary**. On p17
they do. Measured (`.temp/p17b/readspan.py` — every window the driver selects,
every byte the *checked* kernel folds plus the header bytes it reads):

| input | `n_blob` | min read idx | max read idx | last valid |
|---|---:|---:|---:|---:|
| `small` | 16192 | **0** | **16191** | 16191 |
| `large` | 8390650 | **0** | **8390649** | 8390649 |
| `adversarial-leak` | 64 | **0** | **63** | 63 |
| `adversarial-oob` | 64 | **0** | **63** | 63 |
| `adversarial-crosswin-lo`/`-hi` | 128 | **0** | **127** | 127 |

R4's own reads touch *both* ends of the blob exactly on **every input that serves
a range at all** (`adversarial-nsuf` reads indices 0–1 and rejects;
`adversarial-stride1` makes no call — both by design), so p17's boundary coverage
is **better** than p16's, whose shipped window ended three bytes short — the
opposite of what this paragraph claimed before
TASK_012 (TASK_011_REVIEW, minor 2). One real caveat remains and it is about the
clamp, not about the inputs: `check.py` rewrites `n_iters` to 4 for Miri, and at
four iterations `large.bin` reaches index 0 but only 6 319 591 of 8 390 649, so
the *far* boundary on `large` is covered by the gate's own runs and not by Miri's.
Every other input covers both ends at four iterations too. Read the body, every
time.

**And there is a p17-specific limit on what this item can be asked to do, which
is the whole pattern.** `i < v@.len()` is a *memory-safety* precondition and p17
has a harm it structurally cannot address: a suffix with `content_len < s <=
len` makes the kernel read the window's own suffix table, at an index that is
small, non-negative and entirely inside `v`. `i < v@.len()` holds. The twin
verifies. Miri is silent. That harm is excluded by `kernel`'s `ensures` and by
nothing else in the trusted base, so **do not read a green 5c/5c-req/5c-twin on
p17 as evidence that the kernel is right** — it is evidence that the kernel does
not read out of bounds, which on this pattern is a strictly weaker statement.

(c) **Does the clause mean the same in both configurations?** Yes. `i < v@.len()`
mentions only `i`, `v` and vstd's `@`/`len()`; there is no pattern-defined name
in it that a `#[cfg]` could redefine, and `v: &[u8]` / `i: usize` are concrete
types with no generic or associated item that could differ. Since TASK_010 the
gate also forbids the token `slb_twin` anywhere in the file except the twin's own
`#[cfg(slb_twin)]` attribute, so no item — `const`, `use`, `type` or `fn` — can
differ between the shipped compilation and the twin's. That rule exists because
`#[cfg(slb_twin)] const SLACK: usize = 0;` / `#[cfg(not(slb_twin))] … = 1;`
behind a shared `spec fn in_bounds` passed the whole gate while shipping
`i < v@.len() + 1`.

SLB-TRUSTED-ARGUMENT verus.rs load_input

(a) **Is the twin's body the right checked stand-in?** There is no twin and none
is required: `load_input` is `external_body` with **no `ensures` and no
`unsafe`**, so it falls outside the trusted-item regime, which
`.memory/04-verus.md` keys on `external_body` + (a non-empty `ensures` **or**
`unsafe`). That is the correct boundary rather than a loophole: an item that
asserts nothing cannot axiomatise a falsehood, and there would be nothing for a
twin's body to be forced to do.

(b) **Is the `ensures` complete with respect to every unchecked operation the
body performs?** Vacuously, because there is no `ensures` — and on p17 that was a
live decision rather than an inherited one. The kernel needs
`buf@.len() <= i64::MAX` for its signed index arithmetic and vstd cannot supply
it (`vstd::slice::axiom_spec_len` gives `<= usize::MAX` and nothing more), so the
obvious shortcut was to add `ensures r.2@.len() <= 9223372036854775807` here.
**It was rejected**: it is an axiom about the length of a `Vec` the verifier never
sees constructed, it would pull `load_input` into the twin regime with no twin
possible (there is no checked stand-in for `read_to_end`), and it would then have
had to be excused through `verus.twin_justifications`, which the gate shouts on
every run. The driver **checks** the bound at run time instead — one conjunct,
outside the measured loop, costing nothing per call. See §9. The body performs no
unsafe operation at all (argv handling, `fopen`, `read_to_end`, a `to_vec`), so
there is no unchecked operation for an `ensures` to be incomplete about, and the
proof knows nothing whatever about the payload, which is exactly right for a
benchmark whose adversarial inputs are the point.

(c) **Does the clause mean the same in both configurations?** No clauses, so
trivially yes, and the `slb_twin` token scan (which covers the file and
everything it `#[path]`-includes, `common/driver.rs` among them) is what makes
that statement checkable rather than assumed.

SLB-TRUSTED-ARGUMENT verus.rs emit

(a) **Is the twin's body the right checked stand-in?** No twin, for the same
reason as `load_input`: `external_body`, no `ensures`, no `unsafe`, therefore
outside the regime. `println!` is not verifiable in Verus and there is no
checked stand-in for writing to a file descriptor.

(b) **Is the `ensures` complete with respect to every unchecked operation the
body performs?** There is no `ensures` and no unchecked operation. The body is
one `println!`. It is counted as TCB anyway, and listed individually in §4,
because `.memory/04-verus.md` records that the pilot was published as "TCB: one
3-line `get_unchecked` wrapper" when the true tally was three items — and the one
that mattered was the *driver*, whose `external_body` deleted every call-site
obligation in the file. Under-counting the boring items is how the interesting
one hides.

(c) **Does the clause mean the same in both configurations?** No clauses. The
item is identical under `--cfg slb_twin`, and the token scan enforces that
nothing in this file varies with that cfg except the twin itself.

## 7. Mutation testing — I broke my own proof, twice on purpose and three times to measure

`.memory/05-layout.md` step 5: *a pattern whose `spec.md` pins are copied without
being re-derived is a pattern whose gate certifies the pattern it was copied
from.* Five mutants, built as full repo-layout mirrors under `.temp/p17/mut/`
(M1–M4) and `.temp/p17b/mirror/` (M3–M5, regenerated at TASK_012 from the
shipped `verus.rs` by an exact-string substitution that asserts its own hit
count), and never in `patterns/` — §1c has the reason that is not a choice.

### M1 — the trusted accessor's `requires` weakened by one character

`i < v@.len()` → **`i <= v@.len()`**, in the item, in the twin (so the signature
comparison still passes) *and* in `spec.md`'s pin, all in one edit.

| oracle | verdict |
|---|---|
| Verus alone | `10 verified, 0 errors` — **no diagnostic at all** |
| stage 5a (structural) | **PASSES, approvingly**: *"trusted item `get_unchecked` demands `['i <= v@.len()']` of every caller, constraining every parameter its body uses (['v', 'i'])"* |
| stage 5c-req (tautology probe) | **PASSES**: *"`i <= v@.len()` is not a tautology"* — and it is not |
| **stage 5c-twin (verified twin)** | **FAILS**: `with --cfg slb_twin Verus reports 10 verified, 1 errors` … `error: precondition not met: index in bounds for this access --> verus.rs:230:5` |

And the mutant's trusted base really does axiomatise a one-byte OOB read: adding
`fn slb_probe_offbyone(v: &[u8]) -> (r: u8) { get_unchecked(v, v.len()) }` to the
mutated file gives **`11 verified, 0 errors`**. In the shipped file the same
probe cannot verify.

### M2 — the kernel's `ensures` made trivial

`r == range_fold(buf@, off, len)` → **`r == r`**, with the driver's consuming
`assert` deleted (otherwise Verus itself objects, and the point is to test the
gate) and both `spec.md` pins moved to match.

| oracle | verdict |
|---|---|
| Verus alone | `10 verified, 0 errors` |
| stage 5a (contract pin) | **PASSES** — the pin was moved in the same commit, which is precisely TASK_003_REVIEW's self-certification finding |
| **stage 5c (clause deletion)** | **FAILS**: *"`verus.rs` kernel ensures[0] is NOT load-bearing: deleting `r == r` still gives 10 verified, 0 errors. Nothing consumes this postcondition, so it is decoration."* |

**On p17 this mutant is not hygiene, it is the security property.** M2 deletes
the only clause in the file that excludes the in-bounds leak (§5); every
memory-safety obligation still discharges and Verus is silent. The derived check
is what catches it, not the pin.

### M3 — the check deleted from R5 (the control TASK_011 asked for)

`&& start >= 0` removed from `verus.rs` and nothing else
(`.temp/p17/mut/patterns/p17-http-range/verus_nocheck.rs`):

```
error: invariant not satisfied at end of loop body
   --> .../verus_nocheck.rs:311:13
    |
311 | /             range_walk(buf@, off as int, len as int, i as int, acc, nserved) == range_walk(
    | |_____________^

error: invariant not satisfied before loop
   --> .../verus_nocheck.rs:342:21
    |
342 |                     0 <= base,
    |                     ^^^^^^^^^
verification results:: 9 verified, 1 errors
```

**TASK_011 predicted that only the functional obligation would fail. It is
contradicted, and for a structural reason worth writing down.** Both fail: the
`range_walk` invariant (functional) *and* `0 <= base` (memory safety — it is what
makes `(base + j) as usize` a real index and discharges `get_unchecked`'s
`requires`). The prediction's phrasing was *"only the second, on the leak input's
shape"*, and **"on the leak input's shape" is a run-time notion that a proof does
not have**: Verus quantifies over every `buf`, `off`, `len` satisfying the
`requires`, the mutation admits *both* harms, so both obligations fail. There is
no mutation of this program that admits the leak and nothing else *by choosing an
input*. To separate the two you have to change the *program* so the OOB is
impossible — which is M4.

### M4 — the mutation the prediction was actually about: bounds-safe and still wrong

`start >= 0` → **`start >= -(body_start as i64)`**. Guard the *window*-relative
index instead of the logical start — "clamp the read to the front of the
window". **This is *stronger* than a bounds check, not equal to one**; the
version that is exactly as strong as a bounds check is M5 below, and it is worse.
`.temp/p17/mut/patterns/p17-http-range/verus_absguard.rs`:

```
error: invariant not satisfied at end of loop body
   --> .../verus_absguard.rs:311:13
    |
311 | /             range_walk(buf@, off as int, len as int, i as int, acc, nserved) == range_walk(
    | |_____________^
verification results:: 9 verified, 1 errors
```

**One error, and it is the functional one.** `0 <= base` is proved. Every
`get_unchecked` precondition is proved. The trusted accessor is satisfied at
every one of the four call sites. And the program serves the attacker the
window's own suffix table — §1b runs the same mutation as plain safe Rust and it
prints C's wrong value.

*That* is the measurement TASK_011 asked for, arrived at by a different route
than the one it prescribed: **a proof of memory safety is not a proof of the
security property, and here is a program that has the first and not the second.**

What M4 does **not** establish, and was published as if it did, is *disclosure*:
what this mutant reads beyond its entitlement is `[0, body_start)` of the
attacker's own window. See §1b.

### M5 — exactly as strong as a bounds check, and it reads the neighbour

`start >= 0` → **`start >= -((off + body_start) as i64)`**. The driver hands the
kernel the whole blob, so this — *the slice-relative index is in range* — is
precisely and only what `get_unchecked`'s `requires i < v@.len()`, and what safe
Rust's bounds check, demand.

```
error: invariant not satisfied at end of loop body
   --> .../verus_sliceguard.rs:311:13
    |
311 | /             range_walk(buf@, off as int, len as int, i as int, acc, nserved) == range_walk(
    | |_____________^
verification results:: 9 verified, 1 errors
```

Identical to M4's verdict — one error, the functional one, `--multiple-errors 20`
unchanged — and with the functional specification stripped, **`10 verified, 0
errors`**, as M4 also gives. The two mutants are indistinguishable to Verus and
differ by one token; on `adversarial-crosswin-{lo,hi}.bin` M4 prints the same
checksum on both files and M5 prints two different ones. §1c is the table, the
positive control (`nocheck` with the spec stripped still fails, on `0 <= base`)
and the reproduction command.

**M5 is the mutant that earns the sentence M4 was published under.** It is a
program whose every Verus obligation about memory discharges, which contains no
`unsafe` outside the one trusted accessor — the safe-Rust twin of it contains
none at all — and whose output is a function of bytes belonging to a different
caller's window.

## 8. Is the verified twin still idle? Yes.

`.memory/04-verus.md` records the honest caveat that the verified twin is idle on
p16 — "its value accrues from p17 on", because what it uniquely catches is a
*missing conjunct* in a multi-clause trusted `requires`.

**It does not accrue on p17, and reporting that is the honest outcome.** p17's
trusted accessor is the same single-clause `i < v@.len()` p01, p02 and p16 ship,
and it is single-clause for a *reason* rather than by inheritance: p17's
interesting harm is not a memory error, so it cannot be expressed as a conjunct
of any accessor precondition at all. Adding a second clause to `get_unchecked`
solely to exercise 5c-twin would be manufacturing work for the mechanism —
gaming the gate — so it was not done.

What p17 does contribute to that mechanism is the same *negative control* p16
supplied, on its own accessor: §7 M1 shows the twin failing on `i <= v@.len()`
while 5a and 5c-req pass it approvingly, and shows the mutant's trusted base
proving `get_unchecked(v, v.len())` defined. A green 5c-twin on p17 remains
evidence of nothing in particular. **The prediction in `.memory/04-verus.md`
should be corrected: the twin's value accrues from the first pattern that needs a
*multi-clause trusted accessor*, which is a property of the wrapped intrinsic
(p27+'s raw pointers, `copy_nonoverlapping`-shaped items with three documented
preconditions), not of the pattern number.**

One thing p17 *does* newly exercise: the kernel's `requires` is the project's
first with **two** clauses, and stage 5c-req deletes each independently — both
give `9 verified, 1 errors`, so both are load-bearing. That is the deletion probe
working per-conjunct on a verified item, which until now had only one conjunct to
work on.

## 9. Proof sticking points

R5 verified on the **second** attempt, `10 verified, 0 errors`, in about 8
minutes of engineer time. The one-session budget went almost entirely unused, as
on p16. Five things are worth carrying forward.

1. **`for` + `continue` does not exist in Verus, and that decided the shape of
   every rung.** TASK_011's pseudocode skips a request with `continue`. Verus:

   ```
   error: for-loops do not yet support continue
   ```

   `while` + `continue` *does* verify (probed, `.temp/p17/probe/whilecont.rs`, 4
   verified / 0 errors), but only if the loop counter is incremented **above** the
   guard, which is unidiomatic in all six rungs and would have made R2 a
   deliberately odd port. The conjunctive spelling
   `if start < end && start >= 0 { ... }` has identical semantics, is what nginx
   actually wrote (`ngx_http_range_filter_module.c:371`), and gives R1-vs-R1h a
   one-conjunct diff. **A prescription that cannot be expressed in the verifier is
   worth reporting; this is the second time a Verus loop form has driven a
   pattern's exec shape** (p16's was `invariant_except_break`).

2. **Signed index arithmetic needs a bound vstd does not have, and it is a real
   gap.** `(len - body_start) as i64` and `(off + body_start) as i64` are lossless
   only if the operands fit in an `i64`, and the strongest fact available is
   `vstd::slice::axiom_spec_len`, i.e. `spec_slice_len(s) == s@.len()` and hence
   `<= usize::MAX`. There is **no axiom that a slice or `Vec` is at most
   `isize::MAX` bytes**, although Rust guarantees it. Worse, Verus models `usize`
   as *possibly 32-bit*, so `x <= i64::MAX` does **not** imply `x <= usize::MAX`
   either — both bounds have to appear in the loop invariants, and a literal
   `9223372036854775807` written as a `usize` is rejected outright:

   ```
   error: integer literal out of range USize
   ```

   Three ways out were considered. An `ensures` on `load_input` (rejected — §6b,
   an axiom about a `Vec` the verifier never sees built, on an untwinnable item).
   A spec that models the truncation (rejected — it puts an unreachable branch in
   the specification *and* in `model.py`). A **run-time check in the driver**,
   which is what shipped: `n_blob <= 9223372036854775807` as a third conjunct of
   the guard, outside the measured loop, costing nothing per call, and honest —
   `stride_w` is a `u64` read straight out of the file.

3. **The invariant shape p16 found transfers unchanged.** *"The walk from here,
   with what we have accumulated, is the whole walk"* —
   `range_walk(buf@, off, len, i, acc, nserved) == range_walk(buf@, off, len, 0,
   0, 0)` — is the outer invariant, and the inner one is
   `acc == fold_bytes(buf@, base, j, a1)` with one ghost snapshot `a1`. p17 is
   *easier* than p16 in one respect: there is no `break`, so a plain `invariant`
   suffices where p16 needed `invariant_except_break` + a loop `ensures`. The trip
   count is still attacker data (`nsuf` is a `u16` from the buffer) but it does not
   move during the walk, where p16's position was recomputed from the data at
   every step.

4. **Two errors, both linear-arithmetic bookkeeping, both fixed by naming the
   sum.** The first attempt failed on `off + 2 + 2 * i` ("possible arithmetic
   underflow/overflow") and on the inner fold's invariant (via a "value may be out
   of range of the target type" recommendation on `(base + j) as usize`). Both
   were the same missing link: `buf@.len() <= usize::MAX` was established *before*
   the loop by the `spec_slice_len` assert but was not **in the invariant**, and a
   loop invariant cuts the context. Adding it to both invariants, plus one ghost
   line `assert(off + 3 + 2 * i < off + len);` to point Z3 at which sum to bound,
   took the file to 0 errors. Carry the rule: **every `<= usize::MAX` /
   `<= i64::MAX` fact a loop body needs must be restated in that loop's
   invariant**, however obvious it looks outside.

5. **Ghost erasure survives signed arithmetic.** R4 and R5 are byte-identical at
   `-O3` (`md5_fn 45064db24a5b`, `md5_raw` equal, padding 9/9 B) with two
   `proof {}` blocks, a `let ghost`, three ghost `assert`s and a consuming
   `assert` in the measured driver loop. Nine obligations of nonlinear arithmetic
   and a recursive spec function over attacker-chosen indices, and the machine
   code is the same 120 instructions.

The two ghost blocks in the driver (`k < nwin` and `k * stride + stride <=
n_blob`) are p16's, which were p02's, lifted **verbatim** — `lemma_div_non_zero`,
`lemma_fundamental_div_mod`, `lemma_mul_inequality` and one
`by (nonlinear_arith)`. Three patterns now share them unchanged; they are the
Family-C driver boilerplate.

Total Verus wall time for the shipped file: ~4 s.

## 10. The spelling spread — three spellings, and the one thing p17 can say

> **Read §10a with this section.** Row 3 below is **out of contract** under the
> named-spelling standard (corrected at TASK_018); §10a is the in-contract
> spread, and it reaches row 3's number with row 3's exact machine code.

**Not the headline.** A result about *method*, required for every pattern by
TASK_016 for every pattern that has spellings. p17's number is the matched pair under
the idiom `spec.md` declares — **R3 `safe_tuned.rs` − R4 `unsafe.rs` = +32
Ir/call on both shipped inputs, 0 per byte** — and the row below it is a kernel
p17 does not ship.

Marginal `Ir`/call, `-O3 isolated`, §2's convention and §2's probe; the three
shipped rows are the gate's own numbers (`results/gate/p17-http-range.json`'s
`marginal_ir_per_call`: 8832.7 / 5240.7 / 5208.7 and 71572.7 / 41311.7 /
41279.7).
`small` and `large` both serve **`nsuf = 3`** requests; that is the whole
weakness of this section and it is stated up front.

| # | rung | spelling | file | small | large | − R4 shipped |
|---|---|---|---|---:|---:|---|
| 1 | R2 | indexed `buf[base+j]`, table indexed `tab[2*i..2*i+2]` | **`safe_naive.rs` (SHIPPED CELL)** | 8832.70 | 71572.70 | +3624 / +30293 — the O(n) row, 4.25 Ir per folded byte (§3b) |
| 2 | R3 | reslice table once, index it 2 bytes at a time; two-endpoint reslice of the served range | **`safe_tuned.rs` (SHIPPED CELL)** | **5240.70** | **41311.70** | **+32 / +32** |
| 3 | R3 | `chunks_exact(2)` over the table; body resliced once, served range as the **suffix** `body[start..]` | `v17-tuned_suffix.rs` | 5189.70 | 41260.70 | −19 / −19 |
| 4 | R4 | `get_unchecked`, flat indices | **`unsafe.rs` (SHIPPED CELL)** | **5208.70** | **41279.70** | **0** |

⚠ **This paragraph was wrong and is corrected at TASK_018.** It used to read:
*"All four rows satisfy p17's declared idiom … Row 3 keeps `start` and `end`
`i64`, keeps the one conjunctive guard, and folds the same bytes; it is an
admissible p17 R3 that nobody has landed."* **Row 3 has no `end` binding
anywhere in its code** (`.temp/p05r3/v17/tuned_suffix.rs`; the only two
occurrences of the word are in doc comments) and it writes `start <
content_len` where `required[1]` names `start < end`. Under the
**named-spelling standard** — `spec.md`'s `idiom.why`, a **policy adopted at
TASK_018 for all six patterns, after the alternate spellings had been
measured** — row 3 is **out of contract on `required[0]` and `required[1]`**.
The claim it satisfied all four was written into this file by TASK_017, in the
same commit that ruled the analogous p16 spelling out (TASK_017_REVIEW B1). The
marking is therefore *shipped* (rows 1, 2, 4) versus *out of contract* (row 3),
and §10a supplies the in-contract alternates row 3 cannot be.

Row 3 is the whole *measured* spread of TASK_015/TASK_016: p17 had **one**
alternate spelling measured, against p05's ten and p16's four. It changes two things at once — a constant-size
`chunks_exact(2)`, which is a mask and not the runtime `div` that made p05's
`chunks_exact` a special case, and a one-endpoint suffix reslice so `s` is never
re-derived as `end - start`. It is identical on every input.

**What the two shipped points cannot establish, and what a generated sweep says.**
`+32` and `−19` are each *two measurements at the same `nsuf`*, 8× apart in body
size. That establishes the **per-byte** rate (0, exactly: §3b) and nothing about
the per-call constant. TASK_015_REVIEW M2 generated inputs varying `nsuf` 1…8 at
a fixed body (`.temp/review015/gen17.py`, `in17/`; all four rungs print identical
checksums on all eight):

| `nsuf` | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R3ship − R3′ | 17 | 34 | **51** | 68 | 85 | 102 | 119 | 136 |
| R3′ − R4 | +1 | −11 | **−21** | −31 | −41 | −53 | −63 | −73 |
| R3ship − R4 | 18 | 23 | **30** | 37 | 44 | 49 | 56 | 63 |

`R3ship − R3′ = 17·nsuf` **exactly**, zero intercept, zero residual over eight
points. `R3ship − R4 ≈ 7·nsuf + 9`. **Both are per-request, not per-call**, so
"+32 flat" is flat in *bytes* and rising in *requests* — a reader applying it to
a request with 20 ranges gets ≈ +150.

Two caveats that bound this, both load-bearing:

- **the eight inputs are generated, not shipped**, so the absolute figures are
  not p17's: at `nsuf = 3` they give +30 / −21 against the shipped +32 / −19.
  What is established is the **`nsuf` dependence**, and that is unambiguous;
- **p17 ships no sweep at all.** `inputs/gen.py` has no `--sweep` mode, unlike
  p16's (68 blobs) and p05's (144), and §3b's 34-point sweep lives in
  `.temp/p17/sweep/`. That is precisely how a two-point constant got published as
  a law, in a project whose own rule is *sweep two full cycles, never sample two
  points*. **A shipped `nsuf` sweep is owed and is its own task** — TASK_016
  changed no cell source and no input.

And the same structural point as p05 and p16, restated correctly at TASK_018:
the cheapest safe spelling measured is **below the unsafe rung** on both shipped
inputs, and although row 3 as written is out of contract, **an in-contract
spelling reaches the identical machine code and the identical number** (§10a).
The pair in rows 2 and 4 is what p17 publishes; it is a matched pair by
declaration, not by optimality — and §10a shows the declaration does not narrow
it to one.

## 10a. The **in-contract** spelling spread (TASK_018)

§10 row 3 is out of contract under the named-spelling standard, so it cannot
answer "is the shipped R3 the cheapest admissible one?". This section answers
it. **The answer is no — and the exclusion of row 3 costs nothing, because the
compiler erases the distinction the standard draws.**

Two alternate R3 spellings, under `.temp/p18/v17/`, **neither a p17 cell**. Both
keep `let start: i64`, `let end: i64`, the literal
`if start < end && start >= 0`, `n = end - start`, `nserved` folded, no `Range:`
parsing, zero `unsafe`. Only the suffix-table walk and the byte fold — the two
things `spec.md`'s `idiom.why` says are deliberately *not* restricted — are
respelled. Both print byte-identical stdout and exit status to shipped R3 on
**8/8** committed inputs.

Marginal `Ir`/call, `-O3 isolated`, §10's convention and probe:

| variant | what changed | small | large | − R4 ship | − R3 ship |
|---|---|---:|---:|---:|---:|
| `r3_tabonly.rs` | table walk only: `chunks_exact(2)` for `tab[2*i..2*i+2]` | 5234.70 | 41305.70 | +26 / +26 | −6 / −6 |
| `r3_incontract.rs` | table walk **and** the served range as a suffix reslice of `body` | **5189.70** | **41260.70** | **−19 / −19** | **−51 / −51** |
| *(shipped R3)* | — | 5240.70 | 41311.70 | +32 / +32 | 0 |

**The identity, which is the finding.** `r3_incontract.rs` and the *excluded*
`.temp/p05r3/v17/tuned_suffix.rs` compile to the **same machine code**:

```
.temp/p18/bin17-r3_incontract-O3-isolated  n_fn=135  md5_fn=532201c70eeb5fea622c8199d94edd99  md5_raw=12fd8faca909d0e087c517a0f1142d25
.temp/p05r3/bin/v17-tuned_suffix-O3-isolated  n_fn=135  md5_fn=532201c70eeb5fea622c8199d94edd99  md5_raw=12fd8faca909d0e087c517a0f1142d25
```

The two sources differ in *exactly* the tokens `required[0]` and `required[1]`
name — `let end: i64 = content_len;` + `start < end` + `n = end - start` against
`start < content_len` + an open-ended suffix reslice — and rustc emits the same
478 bytes for both. `harness/asm.py` is the oracle
(`.memory/03-measurement.md`: identity claims cite raw bytes). The *symbol
names* differ (`…13r3_incontract6kernel` vs `…12tuned_suffix6kernel`) — these
digests are of the function's bytes, not of its symbol, which is exactly what
`md5_fn`/`md5_raw` are for.

**What this establishes.**

1. **"The shipped R3 is the cheapest admissible one" is FALSE for p17**, not
   unestablished: an admissible spelling is **51.00 `Ir`/call cheaper on both
   bands**. And this is a **swept law, not a two-point constant** — which is
   worth spelling out because §10's own caveat is that both shipped inputs sit
   at `nsuf = 3`. Because `r3_incontract` and `tuned_suffix.rs` are *the same
   machine code*, §10's eight-point measurement `R3ship − R3′ = 17·nsuf`
   (`nsuf` 1…8, `.temp/review015/in17/`, zero residual) **is** the in-contract
   law, transferred without re-measuring. A request with 20 ranges pays ≈ 340
   `Ir`/call for the shipped spelling that an admissible one does not.
2. **p17's published `R3 − R4 = +32` is an upper bound on
   `inf(in-contract R3) − R4ship`, and on nothing else.** It is a bound only
   because R4 is held fixed by fiat; it is **not** an upper bound on p17's
   in-contract safety tax, which would need the R4 side searched (p05 and p16
   have been, ~~and both moved~~ — **and at TASK_028 neither moved
   admissibly**: every spelling that moved on either pattern needs a vstd
   feature that is `is not supported` at the pin, so it is not a rung. Searching
   p17's R4 side means running `./verus_run.py` on each candidate's twin first).
   The measured in-contract minimum is **−19.00** against the
   shipped R4, on both bands, and it is an **R3-side** figure — TASK_027_REVIEW
   Q2 checked it specifically and it is a clean negative. Per
   `.memory/01-ladder.md` finding 14 that is
   **not** "safe Rust beats unsafe Rust" — R4 is a spelling too and its
   in-contract space has not been searched — it is "the shipped pair is not on
   the floor of its own contract". (Finding 14's *other* half, `inf(R4) ≤
   inf(R3)` by construction, is refuted; the half cited here is the surviving
   one.)
3. **On p17 the token pin has zero effect on any measured quantity.** It
   excludes a source-level difference the compiler erases. Whatever a
   declaration that pins tokens buys, on this pattern it is not attributability
   of `R3 − R4`: the number the pin was used to exclude is reachable inside the
   pin.
4. All of §10's caveats still stand: both shipped inputs have `nsuf = 3`, p17
   ships **no sweep**, and a shipped `nsuf` sweep is still owed.

**Method.** `.temp/p18/measure2.py` → `.temp/p05r3/mir.py` (= `check.py`'s
`_probe_input` plus a whole-program `Ir` difference). Binaries built with
`harness/build.py`'s exact `-O3 isolated` rustc flags. **No pattern source was
edited.**
