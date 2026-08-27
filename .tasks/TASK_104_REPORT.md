# TASK_104 — `p42-goto-cleanup` built. Report.

**`ls -d patterns/p*/ | wc -l` was 25 when I started, so p42 is the 26th
pattern; `p23` had landed.**

---

## HEADLINE

**`p42-goto-cleanup` ships, gate `PASS-WITH-BLOCKED-ROWS`** (one blocked row:
Miri on `large.bin` at the 180 s `MIRI_TIMEOUT`, which `spec.md` declares in
`miri.blocked_reason`). Verus **15 verified, 0 errors**, twin **18/0**, hand-
written axioms **0**, `identity unsafe ≡ verus` **`exact` at `-O3`**, `norel` at
`-O0`.

**Three results, and they are different kinds of thing.**

1. ⚠⚠ **VERUS AT THE PINNED VERSION CANNOT STATE LEAK-FREEDOM, AND `TASK_104`
   §2'S PREMISE IS REFUTED.** `Tracked<Dealloc>` is **affine**, not linear: a
   proof may drop it. An R5 that forgot the error path's `deallocate` reports
   `0 errors`. **p42 is the first pattern in this tree whose R5 proof does not
   cover the pattern's own bug class.**
2. **The leak costs `0.00` on the success path under gcc — exactly — and
   `−4.00`/`−5.00` under clang**, and clang's number has an isolated mechanism
   that is not about memory safety (a branchless merge of two early exits).
3. ⚠⚠ **A per-element rate for this row would have been WRONG, and I have the
   out-of-band test that shows it.** Fit on windows 64..79, predict 512..527:
   every rung's out-of-band residual is 3×–25× its in-sample residual, and the
   cheapest rung mispredicts its own shipped `large.bin` by **−2545 `Ir`/call**
   off an in-sample residual of 12.57. **p42 publishes two measured points per
   rung and no rate.**

---

## §0, settled BEFORE the rungs existed

### The census: `leak` really is absent, and what p42 adds that `p27` does not

Re-run rather than trusted. Taking each of the 25 built patterns' bug class from
`.memory/06-catalogue.md`'s own column: none (p01), spatial OOB write (p02),
index underflow (p03), in-bounds wrap (p04), dimension/overflow (p05),
unreduced rotate (p06), unsigned underflow (p07), overlap UB (p08), bitset guard
(p09), boundary off-by-one (p10), missing terminator (p11), stack overflow
(p12), truncation (p13), unbounded field count (p14), TLV length (p16), integer
overflow (p17), unbounded shift (p18), state confusion (p19), non-termination
(p22), `index >= len` (p23), use-after-free (p27), index out of table (p36),
strict-aliasing UB (p38), limb bound/carry (p46), timing side channel (p47).
**Zero leak rows.**

**What p42 adds that `p27` does not, exactly as the task file predicted:** p27
frees on every path **by contract** — its `spec.md` says the epilogue frees
every record still alive *"so neither C rung leaks"* and its `forbidden` list
excludes `ManuallyDrop`/`mem::forget`/`Box::leak`/`Box::into_raw`. **p42's whole
subject is the path where it does not.**

### The framing is conditional and the conditions are `forbidden` entries

`spec.md`'s `idiom.forbidden` carries four structural conditions, not style
rules: **heap not stack** (the allocation size is the window length, from the
file; a stack array cannot leak and would delete the row), **a real allocator
release not a freelist** (p33's refusal is the precedent: *"did the rung
release its heap blocks?"* reads zero on both sides for an allocator), **an
error path a committed input reaches** (p31's death), and **no measured input
that reaches it** (those cells would be timing a leaking program).

⚠ **The last two are MECHANICAL, not prose.** `inputs/gen.py` replays the driver
loop through `model.py` before writing each file and asserts the (ok, err) call
counts the case declares; `model.py::selfcheck` re-asserts both at gate time.
Four `forbidden` entries backtick no spelling (the gate shouts about that, and
its shout is permanent and correct — they forbid a structure, p05's precedent);
four more do and the audit ranges over all four Rust rungs.

### Precedent, fetched and quoted — not from memory

Linux commit `505d9dcb0f7ddf9d075e729523a33d38642ae680`, *"crypto: ccp - fix
resource leaks in `ccp_run_aes_gcm_cmd()`"*, `drivers/crypto/ccp/ccp-ops.c`,
fetched as raw patch text:

```
 		if (ret)
-			goto e_ctx;
+			goto e_aad;
```

`e_ctx` sits below `e_aad` in the chain, so the wrong label skipped the AAD work
area's release. **CVE-2021-3764**, description verified independently at
suse.com/security/cve/CVE-2021-3764.html: *"A memory leak flaw was found in the
Linux kernel's `ccp_run_aes_gcm_cmd()` function that allows an attacker to cause
a denial of service"*, CVSS 3.1 base **5.5**,
`AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`. Generic form: SEI CERT **MEM12-C**.
⚠ **Nothing claims p42's kernel is a port of that function** — it is the same
defect shape at 25 lines.

---

## THE THREE CALLS THE MANAGER WAS LEAST SURE OF

### 1. *"That `model.py` and the gate can express a leak expectation at all."* — **YES, and I drove the REAL gate.**

`.temp/t104/gp_drive.py` imports `harness/check.py` and calls
`check_sanitizers` on a synthetic pdir. Four arms, **two of them positive
controls that must fail**:

```
arm A  buggy kernel    + sanitizer_expect="fires"   failures=0   want PASS   OK
arm B  hardened kernel + sanitizer_expect="fires"   failures=2   want FAIL   OK  <- CONTROL
arm C  buggy kernel    + sanitizer_expect="clean"   failures=2   want FAIL   OK
arm D  hardened kernel + sanitizer_expect="clean"   failures=0   want PASS   OK
```

And it is now real, in the shipped gate:

```
ok   adversarial-mixed.bin   sanitizer fired as declared (exit=1): ...
         ERROR: LeakSanitizer: detected memory leaks Direct leak of 624
ok   adversarial-notag.bin   ... Direct leak of 256
ok   adversarial-win1.bin    ... Direct leak of 16 b
ok   large.bin / small.bin   clean, exit=0, stdout matches the model
```

⚠ **THE GATE LIMITATION IS REAL AND SHOULD BE REPORTED UPWARD.**
`check_sanitizers`'s `fired` is a four-way substring OR (`"runtime error"`,
`"AddressSanitizer"`, `"UndefinedBehaviorSanitizer"`, `"ERROR:"`), so **it
cannot tell a leak from a heap-buffer-overflow.** p42's `"fires"` obligation
would be discharged by any diagnostic. It is a coarsening, not a blocker;
`controls/leak.sh` carries the finer check — greps `LeakSanitizer`
specifically, requires no *other* sanitizer fired, and asserts the byte count
against `model.py::leak_bytes` = `n_err × win_len`. **88 points, all as
declared**, at `-O0`/`-O1`/`-O2`/`-O3` with `c/kernel_hardened.c` as the
positive control.

### 2. *"That the behaviour matrix is enough of an axis."* — **It is a FINDING, and it is not the only axis: there is a real cost axis too.**

The manager asked to be told if p42 ends up as *"the rungs are byte-identical
and the difference is entirely in whether a `free` exists"*. **It does not.**

- **R1 vs R1h at `-O3` gcc: byte-identical except ONE branch target**, so the
  leak costs `+0.00 / +0.00`. That is the byte-identical result, and `p24` is
  the precedent for publishing it.
- **But the RUNGS are not byte-identical**, and the scratch has a real price:
  R2 1850/75826, R3 1263/50745, R4 1461/59441, c-gcc 1873/77854, c-clang
  1506/61487 kernel-exclusive `Ir`/call at `-O3 isolated`.
- **And R1 vs R1h is NOT zero on clang: `−4.00`/`−5.00`**, with an isolated
  mechanism (clang merges the tag test with the `len == 0` early exit into
  `setne/sete/or` once both branch to the same label; gcc does not).

**So: a finding, on both counts.** The zero has a named axis declared in
`spec.md` before it was measured, and it is not *"safety is free"* — it is
*"this particular safety property has no instruction cost on one compiler and a
four-instruction cost on the other, and neither number is about memory
safety."*

### 3. *"That the error path can be driven from a file blob."* — **YES; nothing needs a failed allocation or an I/O error.**

The error path is a **malformed record tag** in the payload: `(v[off] & 0xff) !=
0xA7`. Three committed inputs reach it (`-notag` all calls, `-mixed` 26 of 64,
`-win1` all 16), and `inputs/gen.py` proves reachability by simulation before
writing each file. The `malloc`-failure path exists and is jumped into the
cleanup chain, but no committed input exercises it and nothing claims otherwise.

---

## WHAT I MEASURED

### The ladder — kernel-exclusive `Ir`/call, `-O3`, inline mode `isolated`

| rung | small (win 97) | large (win 4096) | Ir/element small | Ir/element large |
|---|---|---|---|---|
| R1 c-gcc | 1873.00 | 77854.00 | 19.309 | 19.007 |
| R1h c-gcc-h | **1873.00** | **77854.00** | 19.309 | 19.007 |
| R1 c-clang | 1506.00 | 61487.00 | 15.526 | 15.012 |
| R1h c-clang-h | 1510.00 | 61492.00 | 15.567 | 15.013 |
| R2 safe_naive | 1850.00 | 75826.00 | 19.072 | 18.512 |
| R3 safe_tuned | **1263.00** | **50745.00** | 13.021 | 12.389 |
| R4 unsafe | 1461.00 | 59441.00 | 15.062 | 14.512 |
| R5 verus | 1461.00 | 59441.00 | 15.062 | 14.512 |

`R1 − R1h` gcc **+0.00 / +0.00**; clang **−4.00 / −5.00**.
`R3 − R4` **−198.00 / −8696.00`**; `R2 − R4` **+389.00 / +16385.00**;
`R5 − R4` **+0.00 / +0.00**.

⚠ **`R5 − R4 = 0.00` is convention-dependent and the two conventions disagree.**
Kernel-exclusive gives `+0.00` on both. The **whole-program marginal** gives
`0.00` on `small` and **`−31.00` on `large`** for two binaries whose kernels are
byte-identical (`md5_fn 1ab63fde449d` both) — the binary-layout term p01's
`collapse.note` documents. `results/synthesis.md` scopes `R5 − R4 = 0.00` as a
tautology; **in the whole-program convention it is not one.**

### Both sides searched — four R3 spellings and four R4 spellings

Whole-program marginal `Ir`/call, `-O3 isolated`, all generated from the shipped
rungs by `controls/spellings.py`:

| variant | small | large | admissible as a rung? |
|---|---|---|---|
| **r4_ship** | **1617.00** | **59834.00** | ✅ shipped, verified |
| r4_add (`p.add(i)`) | 1617.00 | 59834.00 | ❌ no vstd spec for `<*mut T>::add` |
| r4_movptr | 1491.00 | 54710.00 | ❌ same |
| **r4_endptr** | **1455.00** | **53174.00** | ⚠ in principle yes; **R5 unbuilt — OPEN** |
| **r3_ship** | **1419.00** | **51138.00** | ✅ shipped |
| r3_revidx | 1627.00 | 59845.00 | ✅ |
| r3_zeroed | 1572.00 | 55298.00 | ✅ |
| r3_push | 2634.00 | 102846.00 | ✅ |

⚠⚠ **THE TWO SPANS OVERLAP** — `r3_revidx` (1627.00) is dearer than every R4
spelling measured. What survives is the narrower claim: **cheapest R3 found
(1419.00 / 51138.00) is below cheapest R4 found (1455.00 / 53174.00) by 36.00
and 2036.00**, so *"safe-tuned Rust beats unsafe Rust here"* is not an artefact
of an unsearched R4 side. R4's endpoint is held **fixed by fiat** at the shipped
verified spelling, per `.memory/01-ladder.md`.

✅ **Clean negative: `with_addr` is not the pessimisation.** `r4_add` measures
identically to the shipped rung. The R3/R4 gap is induction-variable count.

---

## FINDINGS THAT ARE NOT ABOUT p42

### F1. ⚠⚠ PROBE 2'S NORMALISER HAS A FOURTH DEFECT, IN THE KILL DIRECTION

`.temp/t102/b4_norm.py` — *the* corrected form — and `.temp/t94/knorm.py` both
rewrite a self-relative branch target `<kernel+0x91>` to `<SELF>` and **discard
the offset**. So **two kernels that differ only in which of their OWN labels a
branch targets normalise identically.**

Run on p42's two C rungs it reports them as **one rung** (`norm=45d32052d67e`
for both). They are not: one leaks. The complete difference between them is:

```
-    193b:	jne    19a1 <kernel+0x91>      # skips `call free@plt`
+    193b:	jne    199c <kernel+0x8c>      # lands on it
```

**The fix is one character class: keep `<SELF+0xNN>`.** The offset is measured
from the symbol's own start, so it is layout-independent; dropping it buys
nothing and loses exactly the class of bug whose whole expression is a branch
target. With it kept, p42's five kernels read `49 / 49 / 108 / 139 / 120`
instructions and five distinct texts. `.temp/t104/probe2.py` is the corrected
form.

**Probe 2 is a KILL criterion, so a false negative manufactures a refusal.**
Every probe-2 result taken on a pair whose difference is a branch target is
suspect until re-run.

### F2. `harness/vparse.py` cannot parse a destructured `Tracked(pt)` parameter, and the failure is SILENT in one direction

`vparse.params` raises *"parameter pattern 'Tracked(pt)' is not a plain
identifier"*. Consequences on the real gate, both observed:

- `[tcb-unsafe]` **fails the run** — loud, fine;
- `[req-mut]` reports *"the tautology probe could not be synthesised, so this
  conjunct was not judged at all"* for **all six** of the item's `requires`.

The second is the dangerous one. p27 avoids it by spelling the parameter
`pt: Tracked<PointsToRaw>` and writing `pt@.…`, which is a convention nothing
records; I hit it and had to look at p27 to find out. **Worth either fixing
`vparse.params` or writing the convention into `.memory/04-verus.md`.**

### F3. ⚠ The pinned vstd, two facts, both checked against `std_specs/` as CLAUDE.md demands

- **`grep -rn 'from_raw_parts' ~/tools/verus/vstd/` → 0 hits.** There is no route
  from a raw allocation to a `&mut [T]`, so a heap array must be reasoned about
  through `PointsToRaw`/`PointsTo` — p27's route, no slice shortcut.
- **There is no axiom for `size_of::<[T; N]>()`** (`grep -rn 'size_of::<\[' →
  0 hits; `vstd::array`'s broadcast group has no layout axiom). So
  `allocate(size_of::<[u64;CAP]>(), …)` cannot discharge `size != 0` and the
  whole *"one `PointsTo<[u64; CAP]>` and ordinary array reasoning"* route is
  **unavailable without a hand-written axiom.** That is why p42's R5 splits the
  block one byte at a time.
- ✅ `<*mut T>::addr` and `<*mut T>::with_addr` **do** have `assume_specification`s
  (`raw_ptr.rs`'s `pointer_specs!`); `<*mut T>::add`/`offset` do not.

### F4. A compiler-elision fact with a control that fires

Linked binaries, counting `call <malloc>`/`call <free>` inside the kernel symbol
(`.o` hides the call behind a relocation — the documented trap):

```
                                   gcc O0..O3   clang O0   clang O1..O3
k_arr   malloc(len*8), two passes       2            2         2
k_one   malloc(8), store then load      2            2         0
k_cap   malloc(CAP*8) fixed, chunked    2            2         2
CONTROL k_dead: written, never read     2 (O1..O3)             0
```

**clang deletes a heap allocation whose stores it can forward, at `-O1` and
above; gcc deletes none, not even the dead one.** clang's backend is rustc's
backend at the same version, so **a one-word heap context is not a viable
kernel for any leak-shaped row** — the Rust rungs lose the allocation and the
leak with it. This shaped p42's kernel and is worth keeping for any successor.

### F5. `.tasks/TASK_104.md`'s own running count contradicts itself

The closing section says *"PROTOCOL rule 2's running count is **368**"* and then
the last line says *"Carry **324** forward"*. I have carried **368**.

---

## PROBLEMS AND THINGS I WORKED AROUND

1. **The gate's first run FAILED and every failure was mine, not the gate's.**
   (a) Four prose `forbidden` entries backticked words the rungs legitimately
   write (`len`, `free`, `dealloc`, `n_iters`) — **a backticked span in a
   `forbidden` entry is a forbidden SPELLING and a hit hard-fails**; stripped.
   (b) `dig_free`'s destructured parameter (F2). (c) One `dig_alloc` `ensures`
   conjunct was not load-bearing; deleted (a weakening, direction-test-clean).
   (d) Three `SLB-TRUSTED-ARGUMENT` sections missing from `NOTES.md`; written.
2. **`contract_sha256` moved twice and both moves are disclosed in `NOTES.md` 0**,
   with what moved them and in which direction. First written
   `50697e33b2971fc4c…`; shipped `4a252569067081a55…`. The third edit came after
   `measure.py`, touches `idiom` only, and **`results/p42-goto-cleanup.json`
   does not hash `spec.md` at all** — checked, its `source_sha256` covers the
   rung sources, `model.py`, `inputs/gen.py`, `c/*` and the harness.
3. **I reproduced p27's `identity` finding by writing it BACKWARDS.** p27 records
   that `*base = v` is the spelling to use *because* `core::ptr::write` is
   `#[inline]` and survives as a call at `-O0`. p42's first `unsafe.rs` asserted
   the opposite in a doc comment and the code followed the comment; `-O0`
   identity read `differ` until it was swapped. **A correction that names two
   spellings can be applied with the names swapped.**
4. **My own gate probe shipped a one-pointed control and I caught it before the
   pattern existed.** The first `adversarial-mixed` leaked 64 objects on 64
   iterations — every call errored, because the error path returns 0, so `acc`
   never moves and `off` never moves. `inputs/gen.py` now forces word 0
   well-formed and asserts both counts non-zero; the shipped file runs 38 ok /
   26 err.
5. **The first `c/kernel.c` did not read its input.** `dig[i] = (uint8_t)run`
   takes bits 0..7 of a wrapping sum, which depend only on bits 0..7 of the
   inputs — and those carry the constant tag. The digest would have been a
   function of `len` alone. Caught because `model.py` was written with the shift
   and the C without it; `inputs/gen.py::_check_data_dependent` is now a
   standing control.
6. **`controls/spellings.py` refused to run once, correctly.** Its anchor assert
   fired when `unsafe.rs` grew a doc comment — the control refusing to measure a
   stale variant is the behaviour I wanted; the anchor was re-cut.
7. **The Miri seed sweep initially read `rc != 0` as UB.** `adversarial-
   shortlen.bin` exits **5** by design, so every seed looked like a failure. It
   now reads Miri's **stderr**. Second version swept the 32 `sweep-*.bin` files
   too, which cost 40 minutes for nothing; it now skips them, as `check.py` and
   `measure.py` do.
8. **`§3`'s "six controls that could not have failed" is "seven" in my
   instructions** — `.memory/03-measurement.md` should be checked for which.

## THE HARNESS DEFECTS I WAS WARNED ABOUT AND WHETHER THEY BIT

- `_check_opaque_includes` on `include!` in a comment — **did not bite**.
- `_path_includes` missing `cfg_attr`/raw-string/nested `mod` — **did not bite**.
- **`check.py` sets no `MIRIFLAGS` and Miri's alignment check is
  seed-dependent** — **did not bite, and I swept it rather than assuming**:
  `controls/miri_seeds.sh`, seeds **0..7** over the nine small inputs, **no UB
  and no leak at every seed**. `NOTES.md` does not write *"Miri: N of N, no
  UB"*.
- ⚠ `.temp/t94/knorm.py`'s padding defect — **did not bite** (I used
  `.temp/t102/b4_norm.py`'s extents), **but its OTHER defect did — see F1.**

## UNSURE / NOT DONE

1. ⚠ **The MECHANISM of the band-local rate is OPEN.** I measured the
   phenomenon precisely and refuted one candidate: fixing the allocation size
   (`malloc(4096)` instead of `malloc(len)`) leaves the band-B residual
   **identical** (`+37.61 … +39.23` both ways) and moves only the intercept
   (+193 `Ir`, which *is* the size class). A second isolation shows it is smooth
   curvature, not a step: residual `+2.06 → +563.74` monotone over
   `w = 96 … 2048`. **Do not attribute it.**
2. ⚠ **`r4_endptr` is admissible in principle and its R5 was never built.** It
   uses only `with_addr` and `<*mut T as PartialEq>::eq`, both specified by the
   pinned vstd, and it is **162 `Ir`/call cheaper on `small`** than the shipped
   R4. If it verifies, p42's R4 endpoint moves and the R3−R4 gap narrows to
   36.00 / 2036.00. **This is p42's open question and it is stated as one.**
3. ⚠ **The claim "Verus cannot express leak-freedom" is a CONCLUSION about the
   default encoding, not an exhaustive search.** Two routes were considered and
   not built: a **ghost conservation ledger** threaded as a `Tracked(&mut …)`
   parameter (a real obligation, but it changes the kernel signature, which is
   pinned across all six rungs), and a **linear tracked mode**, which the pinned
   Verus does not appear to have. Both are named in `verus.rs` and `NOTES.md` 6
   so nobody re-derives them.
4. **Miri on `large.bin` is BLOCKED** at 180 s. That input is unchecked by Miri;
   the other eleven are not.
5. **No `whole`-mode kernel symbol exists** (the kernel inlines into `main`), so
   the identity pin and the per-symbol numbers are `isolated`-mode only, as they
   are for every pattern.
6. **I did not touch `.memory/` or `RECAP.md`.** The catalogue's `p42` row, the
   findings list and the pattern count are the manager's to land. The catalogue
   still says 48 rows and `p42` PROVISIONAL/UNBLOCKED.
7. **I did not re-run the other 25 patterns' gates.** Nothing in `harness/` was
   modified, so nothing should have moved, but that is an inference.

## MEMORY UPDATES

**None written — `.memory/` and `RECAP.md` are manager-only.** The durable facts
this task produced are F1–F5 above plus:

- `check.py::check_sanitizers` **can** host a leak row, with no
  `__lsan_default_options` hook, at its own stage-7 flags — now demonstrated on
  a real pattern rather than a synthetic pdir, and its `fired` predicate's
  inability to name the sanitizer is a limitation worth recording beside it.
- **`Tracked<Dealloc>` is affine at the pinned Verus** — with a control that
  fires, committed at `patterns/p42-goto-cleanup/controls/affine_leak.rs`.
  `.memory/06-catalogue.md`'s p42 row currently says *"Probe 4's `dealloc` route
  is precedented by `p27`'s `Tracked<Dealloc>`"*; that is true of the
  MACHINERY and false of the OBLIGATION, and the row should say which.

---

## FINAL STATE, VERIFIED

```
$ harness/check.py p42
check.py: PASS-WITH-BLOCKED-ROWS          (exit 0, failures: 0, blocked: 1)
contract_sha256 4a252569067081a55c55c8e6177bc8f6a4f897a57cd59a00c7c000a3da8d29a4

$ harness/measure.py --check-stale
FRESH  results/gate/p42-goto-cleanup.json      37 source(s)
FRESH  results/p42-goto-cleanup.json           18 source(s) + 12 input(s)
52 record(s) examined, 0 STALE
```

Five shouts, all expected: four are stage 0b on `idiom.forbidden[0..3]` having
no backticked spelling (**correct and permanent** — they forbid a STRUCTURE, and
the `why` says so in the gate's own words), and one is the Miri block.

**18 files to commit** (`git status --porcelain -uall patterns/p42-goto-cleanup/`),
**zero `.bin`** — `.gitignore:7` covers `patterns/*/inputs/*.bin` — and no
`__pycache__`. Plus `results/p42-goto-cleanup.json`,
`results/gate/p42-goto-cleanup.json` and this report.

`.temp/t104/` holds 47 files, **356 KB, no binaries**: generators, sources and
logs only, with a manifest at `.temp/t104/NOTES.md` saying what rebuilds what.

⚠ **I ran no `git add` and no `git commit`.**

---

## RUNNING COUNT

⚠ **`TASK_104.md` states two different numbers** — *"the running count is 368"*
in the closing paragraph and *"Carry 324 forward"* on the last line (F5).
**I carry 368.**

I claim **+11**, → **379**, itemised so the manager can discount any of them:

1. §2's premise *"the route is precedented — p27 already proves a deallocation
   obligation"* — **refuted**, with a control that fires.
2. Probe 2's normaliser drops the self-relative offset — **fourth probe-2
   defect, kill direction** (F1).
3. `check_sanitizers::fired` cannot name the sanitizer — gate limitation.
4. `vparse.params` silently disables 5c-req on a destructured `Tracked(…)`
   parameter (F2).
5. The pinned vstd has no `from_raw_parts` (F3).
6. The pinned vstd has no `size_of::<[T; N]>()` axiom, which closes the cheap
   R5 route (F3).
7. clang deletes a forwardable heap allocation at `-O1`+; gcc deletes none
   (F4), with a positive control.
8. The per-element rate is band-local — a new instance of the out-of-band
   lesson, on a new row, with the numbers.
9. The allocator size class is **refuted** as its mechanism.
10. `R1 − R1h` is `0.00` on gcc and `−4.00`/`−5.00` on clang, with the branch
    merge isolated.
11. `R5 − R4 = 0.00` is convention-dependent: `+0.00` kernel-exclusive,
    `−31.00` whole-program marginal on `large`, from byte-identical kernels.
