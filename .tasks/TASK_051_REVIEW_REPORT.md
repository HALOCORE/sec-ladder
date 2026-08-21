# TASK_051_REVIEW report — p18 (LEB128 varint shift)

**Role:** research reviewer. **Verdict:** the headline survives; **1 blocker, 7
major, 5 minor**. Item 1's *mechanism* reproduces and its *blast radius as the
manager stated it is false* — measured on two other patterns. The single most
consequential finding is not in p18 at all: it is that the R4/R5 alignment offset
already written into `.memory/03-measurement.md` is an artefact of the **length of
the source path on the rustc command line**, which I can move at will.

Everything below was re-measured with my own tools under `.temp/r51/`
(`marg.py`, a from-scratch reimplementation of the differenced-marginal protocol,
so a bug in the pattern's own fitter cannot hide inside the check of the
pattern's own fitter). Working tree untouched apart from `.temp/r51/` and
`.temp/build/p06/unsafe-O3-isolated` (rebuilt by `harness/build.py`, byte-identical
to what was there). No `git add`/`git commit`. `check.py` was **not** run, so no
gate JSON was rewritten.

---

## ITEM 1 — the highest-value item: mechanism CONFIRMED, blast radius REFUTED

### 1a. p18's claim reproduces exactly

`.temp/r51/bin/`, my own build at `build.py`'s flags, my own probe:

```
blob            R2-O3   R2-O3d   R3-O3   R3-O3d   R4-O3   R4-O3d
sweep-b01v08     407     417      299     302      332     417
sweep-b10v08    1703    1785     1523    1526     1484    1785
sweep-v01b04     153.0   159.0    126.0   129.0    121.0   159.0
sweep-v16b04    1623.0  1689.0   1371.0  1374.0   1396.0  1689.0
```

`R4-O3d == R2-O3d` on **all four**, to the last instruction. `NOTES.md` 5d is
right, and the derived laws (`19·b + 26·v + 57` both) check out on every row.

### 1b. It reproduces on p01 — and **fails on p16**

```
p01 (small / w500 / w509):  R2-O3d 925/936/939   R4-O3 914/907/928 -> R4-O3d 925/936/939   EQUAL
p16 (small / k120 / k132):  R2-O3d 5125/2499/2739  R4-O3d 3099/1527/1665                   NOT EQUAL
```

On p16 R4 keeps a **2026 Ir/call (39%)** advantage over R2 at `O3d`. So the
proposed `.memory` sentence — *"R4's advantage over R2 vanishes under them"* — is
**false as a project-wide fact**. The exact collapse needs R2 and R4 to differ
*only* by checked-vs-unchecked indexing, which holds on p01 and p18 and does not
hold on p16 (`p16/safe_naive.rs:37` uses `for j in 0..vlen`, `p16/unsafe.rs:48`
uses `while j < vlen`).

**What does generalise, on 3 of 3 patterns measured: at `-O3` with
`debug-assertions=on`, R4 becomes DEARER than R3, reversing the `-O3` ordering.**

```
            R3-O3  R4-O3     R3-O3d  R4-O3d     ordering
p18 b10v08   1523   1484  ->   1526    1785      R4 cheaper -> R4 +17.0%
p01 w500      912    907  ->    914     936      R4 cheaper -> R4  +2.4%
p16 k120     1499   1482  ->   1518    1527      R4 cheaper -> R4  +0.6%
```

**Blast radius, counted:** 15 of 16 patterns' `unsafe.rs` call `get_unchecked` in
the hot loop (all but `p08-overlap-move`, whose R4 is `core::ptr::copy`,
`p08/unsafe.rs:58` — which carries its own `assert_unsafe_precondition!`, so p08
is affected per call rather than per byte; not measured here). So the *exposure* is near-total;
the *exact collapse* is not.

**Suggested `.memory/01-ladder.md` wording (measured, not inferred):**
> `-C debug-assertions=on` also turns on `assert_unsafe_precondition!` inside
> `get_unchecked`, so an R4 built on it is a **checked** access again. Measured
> at `-O3` on p01, p16 and p18: **R4 becomes dearer than R3 on all three,
> reversing the `-O3` ordering**. R4's law becomes *identical* to R2's only where
> R2 and R4 differ by nothing but the bounds check (p01, p18); on p16 R4 keeps a
> 39% margin over R2. 15 of 16 R4s here rest on `get_unchecked`.

### 1c. The sub-claim that keeps it honest — CONFIRMED, independently

I regenerated the `*_wrapall` controls myself from `safe_naive.rs`/`unsafe.rs`
(`.temp/r51/o0d/`) rather than reusing the pattern's, and re-measured the
per-byte slope over band b:

```
n_plain   O0 42.00  O0d 65.00  Δ 23.00     n_wrapall  O0 42.00  O0d 49.00  Δ  7.00
u_plain   O0 55.00  O0d 93.00  Δ 38.00     u_wrapall  O0 55.00  O0d 76.00  Δ 21.00
```

7.00 of 23.00 / 38.00 is the shift check. Exact. And from **my own** objdump
(`.temp/r51/o0d/n_wrapall-O0{,d}.asm`): the `O0` shift block executes **13**
instructions, the `O0d` one **20** — 8 added (3 spills, `cmp $0x40,%eax`, `jae`,
3 reloads), 1 removed (`mov %ecx,%edx`), net **+7**, of which **2** are the check.
`NOTES.md` 636-643 is correct.

---

## BLOCKER

### B1 — every published per-call `Ir` law has an unstated domain, and a blob in p18's own committed input set falsifies the R3−R4 law's **sign**

`patterns/p18-varint-shift/NOTES.md:362-374` publishes eight laws as *"exact over
34 blobs, max |residual| 0.029"*; `NOTES.md:933-941` publishes
`R3 − R4 = +1.00·bytes − 6.00·varints + 7.00` with *"a crossover at
`bytes/varint ≈ 6`"*. Every blob those laws were fitted on — all 31 of bands
b/v/x and all 3 of band y — has `term == nv`, i.e. **every varint terminates
inside the window**. That is a structural parameter of the kernel and it is never
named.

`inputs/degenerate.bin` is committed, is one of the eight matrix inputs, and has
`term = 4 < nv = 5` (one varint ends on window exhaustion, taking the inner
`while p < len` exit and then the outer `if p == len` break). Measured against
the published laws:

```
cell         predicted   measured    miss
c-gcc            372      374.018    +2.00
c-gcc-h          408      410.018    +2.00
safe_naive       509      511.008    +2.00
safe_tuned       424      432.008    +8.00
unsafe           429      431.008    +2.00
```

and therefore

```
R3 − R4  law predicts  +1·18 − 6·5 + 7 = −5.00   (R3 cheaper)
R3 − R4  MEASURED       432.008 − 431.008 = +1.00 (R3 DEARER)   <- WRONG SIGN
```

Reproduced at a second `(n1,n2)` pair (`--n1 3000 --n2 9000` → 432.0000).

**Negative control that isolates the parameter:** `inputs/truncating.bin`
(`bytes = 30`, `nv = 3`, `term = 3`) is predicted **exactly** — 474 / 673 / 598 /
579 predicted, 474.000 / 673.000 / 598.000 / 579.000 measured. So the miss is not
noise and not the `println!` term; it is the `term < nv` code path.

**Failure scenario.** A reader takes `R3 − R4 = +1·b − 6·v + 7` and the stated
crossover at `b/v ≈ 6` and concludes p18's R3 is cheaper than R4 on any window
with fewer than ~6 bytes per varint. `degenerate.bin` has `b/v = 3.6` and R3 is
**dearer**. The residual that is supposed to bound this reads 0.029 — it is out
by a factor of 275.

**Why the replacement out-of-sample test cannot catch it (item 2's real
weakness).** `.memory/03-measurement.md:1148` says *"hold out a value of a
structural parameter the model is [built on]"*. Band y varies `bytes` and `nv` 4×
each and holds `term == nv` fixed, exactly like bands b/v/x. So the 24
pre-registered predictions were incapable of detecting the one domain limit the
laws actually have. That is the same defect the hold-out had, in a new costume.

**Fix (not mine to make):** publish the laws with `term == nv` as a stated
domain, or add a band in which varints are cut off by the window end and refit.

---

## MAJOR

### M1 — the R4/R5 kernel-address offset is a function of the **source path length**, not of the pattern. `.memory/03-measurement.md:735-740` is wrong as softened.

The manager asked me to confirm or correct the PROVISIONAL wording *"the offset
is FIXED per pattern, not that it is 0x20"*. **Correct it.**

Harness-built binaries, as committed:

```
p06  unsafe 0x156b0   verus 0x15690   offset 0x20
p14  unsafe 0x156b0   verus 0x15690   offset 0x20
p18  unsafe 0x15640   verus 0x15640   offset 0     <- p18's own claim, CONFIRMED
```

Now the same p06 `unsafe.rs`, same rustc, same flags, only the **spelling of the
source path** on the command line changed:

```
src path length   binary size   kernel addr
   (relative, 29)     4370128      0x15690     <- offset 0, same class as verus
              66      4370160      0x156b0     <- what build.py produces
              74      4370160      0x156b0
              82      4370176      0x156c0
              90      4370176      0x156c0
              98      4370192      0x156d0
```

**Mechanism** (PROTOCOL rule 11): `p06/unsafe.rs` contains a panicking site, so
its binary embeds `/home/apt/repos_common/sec-ladder/patterns/p06-rotate/unsafe.rs`
as a panic `Location` (1 hit in `strings`); `build.py:176` builds `src` with
`os.path.join(pdir, ...)` and `pdir` is absolute (`build.py:84`), so rustc is
handed an **absolute** source path, while `verus_run.py` compiles R5 from a copy
under its own scratch dir. The two `.rodata` sizes differ, `.text` shifts, and the "fixed
0x20" appears. `p18/unsafe.rs` has **no** panic site — `strings` finds **zero**
source paths in it — so its address is path-insensitive and happens to land on
verus's. That, and not "a property of those two patterns' symbol sets"
(`NOTES.md:1142-1143`), is why p18 reads 0.

**Failure scenario.** Someone clones the repo two directories deeper. p06's and
p14's R4/R5 pair silently changes alignment class; p14's published **+8.95%**
pair reading is a function of the checkout path. Any `.memory` sentence of the
form "the offset is fixed per pattern" will then be false in the tree it
describes.

**Suggested replacement:** *"The R4/R5 pair samples ONE alignment draw, and which
draw is decided by the length of the source path rustc is handed — `build.py`
passes an absolute path for R4 while `verus_run.py` compiles R5 from a scratch
copy. Measured on p06: the R4 kernel moves 0x15690 → 0x156d0 as the source path
grows from 29 to 98 characters, with R5 fixed. p18 reads offset 0 only because
its `unsafe.rs` has no panic site and so embeds no path at all. The offset is not
a property of the pattern and must never be quoted as one."*

### M2 — `NOTES.md:958-959` quotes a command whose output is the **opposite** of what is printed beside it

```
$ ./verus_run.py .temp/p18/ctl/probe_shl_bare.rs      # `wrapping_shl` alone
verification results:: 2 verified, 0 errors
```

`probe_shl_bare.rs` does not contain `wrapping_shl`. `gen_controls.py:365-371`
writes it as the `<<` probe, and running the exact quoted command gives:

```
error: possible bit shift underflow/overflow  --> probe_shl_bare.rs:4:52
verification results:: 2 verified, 1 errors
```

**The claim is true** — I wrote a one-function `wrapping_shl`-only probe
(`.temp/r51/verus/r51_wshl_only.rs`) and it reads `2 verified, 0 errors`. But
**no committed generator produces that probe**: `gen_controls.py` writes three
probes and `probe_shl_family.rs` (the only one containing `wrapping_shl`) aborts
on `checked_shl`/`overflowing_shl` being `is not supported`, so it prints no
verdict for `wrapping_shl` at all. A reader re-running the cited command
concludes the opposite of the finding it supports — which is p18's problem #2 and
one of the five things the manager plans to put in `.memory`.

Bonus measurement, not in the pattern: `wrapping_shl` is not merely
"unobligated", it has a **real vstd specification** — a probe with
`ensures r == 0u64` fails with *`postcondition not satisfied`*, not
*`is not supported`*.

### M3 — `m_noguard_ms` is **not** a memory-safety-only configuration, which is the exact defect for which `m_wshl_ms` is withdrawn twelve lines below it

`NOTES.md:1091-1097`: *"`m_noguard_ms` is the one that decides p18's headline …
So a memory-safety-only proof of this kernel — one that says nothing about the
answer — still rejects R1's bug."*

`diff` of `.temp/p18/ctl/m_noguard_ms.rs` against `verus.rs` (whitespace-blanked):
only the top-level `ensures` becomes `true`, the guard is deleted, and one
call-site `assert` is removed. **All six loop invariants survive, functional ones
included** (`grep -c invariant` = 6 in both files). That is precisely what
`NOTES.md:1099-1106` says disqualifies `m_wshl_ms` — *"the separation needs a
PROGRAM change, not a SPEC change"* — applied as the "third instance" of the p17
control-2 lesson while the fourth instance sits in the same table.

The **conclusion** survives, but on different evidence: my `r51_shl_bare.rs` has
a one-line function with no `requires`, no `ensures` and no loop at all, and
still errors `possible bit shift underflow/overflow`. Cite that, not the mutant.

### M4 — the hashed pre-registration proves tamper-evidence, not ordering. Re-running `register` **after** the measurement reproduces the identical hash.

`predict.py:23-25`: *"`score` re-hashes it and refuses to run if it has changed,
which is the whole mechanism — a prediction that can be edited after the
measurement is not a prediction."* `NOTES.md:868-886` presents `sha256 ca0bbe26…`
as evidence the predictions predate band y.

I re-ran `predict.py register .temp/p18/sweep_all_O3.json` **today**, long after
band y was measured:

```
sha256 ca0bbe26a2a88a641fdee37e62368268c42e400ee4312b92ad485b952b3dff61
cmp .temp/r51/predict_y_REDERIVED.json .temp/p18/predict_y.json  ->  IDENTICAL
```

`register` is a pure deterministic function of `sweep_all_O3.json` plus shapes
hard-coded from `gen.py`. Anyone can produce that hash at any time. The hash
establishes nothing about ordering.

**What actually makes the test honest — and it is stronger than the hash — is
that `register` has zero free parameters.** Say *that*. (Circumstantial support
does exist: `predict_y.json` mtime 18:58:25 precedes `sweep-y64.bin` 18:58:32 and
`sweep_y_O3.json` 18:58:54.) Also: `predict_y.json` lives under `.temp/`, which
`.gitignore:3` excludes, so the artefact the hash names is **not in the committed
tree** and will not survive `cleanup.sh` + a fresh clone.

**Clean negative on the same item, and it is the strongest evidence p18 has:** I
measured band y myself, with my own binaries and my own probe, and the
extrapolation is exact.

```
        registered   my measurement
y16     3351.01      3351.0075   (safe_naive)
y40     5055.01      5055.0027
y64     7479.01      7479.0000
y64     6443.01      6443.0000   (safe_tuned)
y64     6500.01      6500.0000   (unsafe)
```

4× outside the hull in both regressors, hit to the `println!` digit term. The
convex-hull-vs-row-space distinction `NOTES.md:888-891` draws is correct and is
the right criterion; the objection in the review task ("does the hull mean
anything for a rank-3 design") does **not** land. What the test misses is B1's
structural parameter, not the hull.

### M5 — the proposed "3-column designs make every leave-one-band-out unable to fail" caveat is wrong, and `.memory` already has the right rule

`TASK_051_REPORT.md:165-166` proposes a **column-count** caveat.
`.memory/03-measurement.md:1121-1133` already states the correct one: the test
cannot fail iff the design **keeps full rank after the drop**. Column count is
not the criterion. Counterexample in three columns: bands
`A = {(1,0,1),(2,0,1),(3,0,1)}` (rank 2) and `B = {(0,1,1),(0,2,1),(0,3,1)}`
(rank 2) pool to rank 3, and dropping either band leaves rank 2 — the LOLO fails.

What actually kills p18's LOLO is that **band x alone is rank 3**
(`NOTES.md:848`), because band x was designed to turn on every regressor at once.
p06's pooled design is **rank 5 of 5** (`p06/NOTES.md:1256`) and every band is
rank-deficient alone, which is why its LOLO has teeth. Recording "3 columns" as
the diagnosis would send the next pattern looking at the wrong number.

### M6 — `check.py`'s Miri stage skips the exit-code AND stdout comparison whenever the model expects a non-zero exit, and reports `ok … matches the model` anyway

The review task asked whether the gate keys on the `ub` flag alone. **It does
not** — `check.py:4612` also fires on a non-zero exit, so p18's Miri panic *would*
have failed the gate (all nine p18 inputs have `expected_exit == 0`).
`NOTES.md:806-808` is correct. But the branch chain at `check.py:4602-4620` is:

```python
ub = "Undefined Behavior" in r.stderr or "error: unsupported" in r.stderr
if ub:                                         fail
elif r.returncode != 0 and expected_exit == 0: fail
elif r.returncode == 0 and got != want:        fail
else:                                          rep.ok("... no UB, stdout {got!r} matches the model")
```

When `expected_exit != 0`, **the exit code is never compared to the expected one
and stdout is never compared at all** — and the `ok` line asserts the stdout
matched.

Reachable today: `p01-array-sum/adversarial-shortlen.bin` (`expected_exit 5`),
`p02-buffer-copy/adversarial-capbig.bin` (7) and `adversarial-shortlen.bin` (5)
are all Miri stage inputs.

Measured, not reasoned: I built a mutant driver (`.temp/r51/miriprobe/`) whose
`die()` panics instead of exiting, ran real Miri on p01's R4 over
`adversarial-shortlen.bin`, and got `rc=101`, empty stdout, no `Undefined
Behavior` in stderr. Feeding those exact values through a replica of the branch
chain prints:

```
ok   miri ...: no UB, stdout '' matches the model
```

**Failure scenario.** Exactly p18's bug class: a Rust rung that hits an
arithmetic-overflow panic under Miri (Miri runs with debug-assertions on) on an
input whose model expects exit 5 or 7 is recorded green. That is one of the two
gate stages the project relies on to backstop an incomplete trusted `ensures`.

### M7 — `RECAP.md:14` still asserts, as fact, two claims p18 measured false

*"An oversized shift is UB that touches no memory — ASan, Miri and a
memory-safety proof are all blind. In Rust it is caught by `debug-assertions` and
nothing else"*. p18 measured that **Miri catches it** (as a panic) and that
**Verus catches it** (`NOTES.md` 0.2b, 0.2c), and I reproduced both. `RECAP.md:13`
correctly quarantines the *item-1* claim as unreviewed; the row below it does not
quarantine the refuted one. Same failure mode as PROTOCOL rule 9, one layer out.

---

## MINOR

### m1 — `README.md:20` ships a corrupted line in the pseudocode block

```
        shift +=32 7                    # wrapping, in every rung
```

Should be `shift += 7`. It is in the one code block a first-time reader reads.

### m2 — the amortisation claim rests on the wrong pair

`README.md:38-45` and `NOTES.md:432-435`: *"11.89% of `small`'s kernel `Ir` and
11.11% of `large`'s — i.e. the fraction does not shrink with the input either."*
`large.bin`'s **window is 41 bytes**; `small.bin`'s is **112**. The pair is two
shapes, not two sizes, and the smaller window is the one with the smaller
fraction — so it demonstrates nothing about growth. The pattern already owns the
right evidence and does not use it: on band b, at fixed `nv = 8`, my measurement
gives `(R1h−R1)/R1` = **5.08%** at `bytes = 8` (331 vs 315) and **13.57%** at
`bytes = 80` (1339 vs 1179), rising toward the 2/12 asymptote. Quote band b.

### m3 — `NOTES.md:638-643` says "the other five" and then lists six instructions

The arithmetic in the same sentence (*"adds eight instructions and removes one"*)
is right, and my listing confirms 8 added / 1 removed / net 7. But the
parenthetical enumerates the six **added** spill/reload instructions under the
label "the other five" (the net figure). One of the two numbers has to move.

### m4 — the `wrapping_shl` limit is not co-located with the claim it limits

`README.md:56-64` and `NOTES.md:180-185` both state the four-catcher headline
with no qualifier; the *"Verus's obligation attaches to the OPERATOR SPELLING"*
limit is at `NOTES.md:971-979`, ~790 lines away, and in `spec.md`'s `why`. I ran
the direction test in writing: the `forbidden` entry is **whole-pattern** (all
seven rungs), so it does not tilt any rung-vs-rung comparison; and its measured
price, which I reproduced exactly, is `t_wshl` = 2106.00 on `small` against
shipped R3's 2307.00 (`−2.00·b + 1.00·v − 1.00` — predicted −201, measured
−201.00; on `large` predicted −73, measured −73.00). So the fiat is real,
priced, and directionally neutral between rungs — but it is 8.7% of R3 and it
is the reason the headline says "Verus". Put one clause beside the headline.

### m5 — the `ns` figures in `README.md:44-46` do not name their input

`+7.14% / +12.04%` are `small`'s. The sentence immediately before them names both
`small` and `large`. `large`'s row is the weak one (`P = 0.676 / 0.829`).

---

## Clean negatives — attacks I ran that did NOT land

1. **`unbnd` is identical to guarded on all four probe blobs.** Rebuilt
   `kprobe.c` + `gen_probe.py` from scratch under `.temp/r51/probe/` and ran all
   six kernels × four blobs at gcc-O0, gcc-O3 and clang-O3: **all 24 values
   identical to `NOTES.md` 0**, `unbnd == guard` everywhere. §0's table stands and
   its rejection reasoning (the harm is p11's OOB read, needing a different input)
   is sound.
2. **The `adversarial-sat` row is doing real work, not hiding a gap.** On that
   input R1 and R1h have *identical observable state at every step*: `val` is
   already all-ones so `|=` changes nothing, and `shift`, `nb`, `p` and the
   consumed byte count are equal. So *"no choice of fold could repair that"* is
   literally true for any fold over the kernel's output, and the row is the
   demonstration that a checksum benchmark cannot certify UB-freedom. It is also
   the row on which Miri **does** fire (`NOTES.md:798, 802`). Finding, not gap.
3. **UBSan re-run at the gate's own flags.** Rebuilt `c/kernel.c` with
   `-fsanitize=address,undefined -static-libasan -static-libubsan -O1 -g`: fires
   `shift exponent 70 is too large` on all four adversarial blobs, silent on
   `truncating` / `small` / `degenerate` / `adversarial-stride3`. No ASan
   diagnostic anywhere.
4. **`c_mask` reproduces both halves.** My own `<< (shift & 63)` rebuild is
   identical to `c-gcc` on every marginal I measured (315 / 1179 / 1899 / 753.018,
   exactly `c-gcc`'s) and prints R1's four wrong values under ASan+UBSan with
   **no diagnostic at all**. *"The sanitizer catches the undefinedness, not the
   wrongness"* is exactly right.
5. **`R1h − R1 = 2.00·bytes`, zero intercept, zero per-varint — and I re-derived
   the coefficient from my own listing.** Measured: `b=8` +16, `b=80` +160,
   `b=112` +224, `b=41` +82. From my `objdump` of `c-gcc-O3` vs `c-gcc-h-O3`: the
   per-byte body goes from 10 instructions (`0x19d0..0x19ef`) to 12 — the added
   pair is `cmp $0x3f,%ecx` + `ja`, nothing else, and the `nopl` at `0x19cc` is off
   the back-edge (`jb 0x19d0`). All four C laws reproduce exactly, gcc and clang.
   **This also survives B1**: on `degenerate.bin` the difference is
   410.018 − 374.018 = **36.000 = 2 × 18**, exact.
6. **clang really does move the check past the shift.** My `c-clang-h-O3`
   listing: `shl %cl,%rbp` at `0x1722`, then `cmp $0x40,%ecx` / `cmovae` at
   `0x1728`/`0x172b`. §1a's reading is correct.
7. **Verus mutants all reproduce.** `m_noguard` 11/1 *bit shift
   underflow/overflow*; `m_noguard_ms` 11/1, **same error** (so the headline
   conclusion is right even though M3's artefact is mislabelled); `m_wshl` 11/1 on
   the inner loop's functional invariant. `checked_shl`, `overflowing_shl`,
   `unchecked_shl` all `is not supported`.
8. **TCB recount.** `verus.rs` has exactly **3** `#[verifier::external_body]`
   items and **zero** `assume`, `assume_specification`, `admit` or bare
   `external`. TCB = 3 as published. Kernel `requires off + len <= buf@.len()`,
   `ensures r == varint_fold(...)` — a full functional postcondition, not trivial.
9. **R4/R5 exec code has not drifted.** My own builds: both kernels are 211
   bytes with `md5 8f97546b0bdb6cf3ebac6668e8d71230`, matching `NOTES.md` 3.
   Verus reports 12 verified, 0 errors on my run.
10. **The `.memory/02-bench-rules.md` UB rule is respected.** All 31 fit rows and
    all 3 band-y rows have `over == 0`; `small` and `large` have `over == 0`. No
    cost is compared on an input where R1 commits UB. The four blobs with
    `over > 0` appear only in behaviour tables.
11. **Both R3 numbers, and the in-contract span, reproduce exactly.** shipped R3
    2307.00/890.00; `t_1step` 2308/891 (+1.00); `t_chain` 2307/890 (0.00);
    `t_cshl` 2307/890 (identical, so that `forbidden` entry costs nothing);
    `t_iter` 2206/861 and **326 vs 299 on `sweep-b01v08`** — dearer on short
    varints, exactly as `NOTES.md:931` says.
12. **`m_wshl_ms`'s withdrawal is complete.** `grep -rn m_wshl_ms` over
    `patterns/p18-varint-shift/`, `results/` and `RECAP.md`: the only hits are the
    withdrawal paragraph itself and the two generator scripts. No number derived
    from it survives.
13. **`large`'s weak `ns` row is not leaned on.** `+4.24% P=0.676` /
    `+10.73% P=0.829` appear at exactly one place in the tree, `NOTES.md:490`,
    with their `P` and with the sentence saying `small` is the quotable row.
    Nothing in `README.md`, `results/tables/p18-varint-shift.md` or
    `results/p18-varint-shift.json` quotes them.
14. **Nothing reads as "safe beats unsafe".** `R3 − R4` appears only at
    `NOTES.md:933-941` and `NOTES.md:1169`, both carrying the FIXED-R4 caveat, and
    is absent from `README.md` and the results table. (Its *law* is still wrong on
    `degenerate.bin` — B1 — but the framing is honest.)
15. **The `why`-key self-correction.** `required[2]` is
    `while p < len`, the shipped R3 spells it, `t_iter` does not, and the
    correction *narrowed* the published R3-side in-contract span from a
    hypothetical 0…101 to 0…1.00. I could not falsify "no entry moved" — p18
    landed in a single commit (`18f7a28`) and no pre-edit snapshot exists in the
    tree — so the disclosure is **not independently checkable**; I record that
    rather than either endorsing or disputing it. Direction: excluding `t_iter`
    makes R3 look 101 Ir/call *dearer*, i.e. it works against the R3-vs-R4
    comparison and in favour of the "narrowest span published" remark at
    `NOTES.md:919`. That remark should carry the caveat; nothing else moves.

---

## Not done / limits of this review

- **`harness/check.py p18` was not run.** Deliberate: it rewrites
  `results/gate/p18-varint-shift.json`, and every fact I would have taken from it
  I measured directly instead (checksums, Verus counts, identity, Miri policy,
  sanitizer row). The gate's own PASS is not re-confirmed by me.
- **No `ns` work.** I re-measured nothing in wall clock; `clayout.py` was not
  re-run. The `ns` findings above (m5, clean negative 13) are documentary only.
- **Blast radius measured on 3 patterns, not 16.** p01, p16, p18 at `-O3`/`O3d`.
  The `get_unchecked` census (15/16) is a grep of `unsafe.rs`, not a build.
- **M1 was demonstrated on p06 only.** p14 was not re-built from a varied path; I
  read its harness-built addresses only. The mechanism (panic `Location` string in
  `.rodata`) was confirmed by `strings` on p06 and p18 but not on p14.
- **B1's domain was probed with the two committed blobs that straddle it**
  (`degenerate` fails, `truncating` passes). I did not generate a band of
  `term < nv` blobs to find the corrected law.
