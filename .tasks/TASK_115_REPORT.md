# TASK_115 — `p26` and `p37` settled, and the six adjudications in landable form

**Role: research engineer (probe only).** No pattern built, no
`patterns/p26-*/` or `patterns/p37-*/` created, no `.memory/`, `RECAP.md`,
`results/`, `synthesis/`, `harness/`, `pilot/` or `patterns/*/` file touched, no
`git add`/`commit`. `harness/check.py`, `build.py` and `measure.py` were **not**
run. Everything under `.temp/t115/`. `TASK_113` and `TASK_114` were live
throughout; every number below is callgrind `Ir`, which is deterministic — **no
wall-clock measurement was taken at all**, so nothing here can be load-sensitive.

**PROTOCOL rule 2 running count: 414 + 12 on this branch.** Launched from 414,
concurrently with `TASK_113` and `TASK_114`. **Reconciliation is the manager's
job, not mine; I have not added anything to the other branches' deltas.**

## HEADLINE

1. ⚠⚠ **§A.1: the manager is RIGHT, but for a sharper reason than the one
   stated, and `TASK_092`'s stated mechanism is not the cause.** The 8387 is not
   a safety price. It is **not** the `memset`-vs-vector idiom split either — that
   split is worth **+1170** in the *safe-costs-more* direction. **The whole
   inversion lives in the CHECKSUM FOLD**, where the *unsafe* rung pays a
   surviving bounds check of **2.99 Ir per output byte** because deleting the
   fill's check destroyed the range fact `o <= OUTCAP` that the fold needed.
2. ⚠⚠ **It is p13's finding, second instance, INCLUDING p13's own retraction.**
   Give the unsafe rung the bound in one line and `safe − unsafe` is **positive
   at 253 of 254 run lengths**; the published `−8387` becomes `+1173`.
   **→ REFUSE `p26`.**
3. ⚠ **`TASK_092`'s "NEITHER HAS A PANIC EDGE" is FALSE. Both rungs have one**,
   and the unsafe rung's is the one that decides the number. The cause is an
   instrument defect worth recording: these are PIE binaries and the panic call
   is GOT-indirect, so objdump prints `_DYNAMIC+0x2c8` and a panic-edge test read
   off disassembly text is a **false negative**.
4. **§A.2: the inversion threshold does not exist.** `S−U` changes sign **four
   times** in `r ∈ [1,254]`, and `ship_safe` is **discontinuous**, dropping
   `−2804.00 Ir` at every `r ≡ 1 (mod 32)` — the SIMD width of its fill. The
   sign is a property of `r mod 32`.
5. **§B: REFUSE `p37`.** Its stated refusal reason stays refuted, but the row
   still dies, on three measurements: the R5 obligation is **p08-shaped
   (unrepresentable, not checked)**, the cost axis is **+2.00 Ir/record**, and
   the harm is silent in 8 of 8 plain cells.
6. **§C: no later task supersedes any of the six adjudications.** One is
   corrected (`TASK_090`'s harm re-run covers `p21`, `p26`, `p41`), one is
   *strengthened* (`p20`'s duplication reason now also names `p17`).

---

# §A — `p26`

## A.0 — the reproduction is exact

`.temp/t115/build.sh` regenerates `TASK_092` Part B's shipped-shape sources from
the same template (`.temp/t92/partB/mkpartb.py`), same flags
(`rustc -O -C codegen-units=1 --cfg slb_isolated`), same marginal convention
(`(Ir@200 − Ir@100)/100`).

```
input                            safe         unsafe        S-U
p26-np016r016.bin             7570.30        6837.30    + 733.00
p26-np016r200.bin            24450.30       32837.30    -8387.00
p26-np200r020.bin            55794.00       44381.00   +11413.00
```

Identical to `TASK_092` PART B to the last decimal. `TASK_086`'s probe pair was
**not** reused (its two halves are not the same function).

## A.1 — ⚠⚠ THE ANSWER: it is not a safety price, and it is not the idiom either

### A.1a — `TASK_092`'s "neither has a panic edge" is false, and here is why nobody saw it

`.temp/t115/resolve_calls.py`. rustc calls internal functions through the GOT in
a PIE, and objdump resolves the **slot** address, not the callee:

```
p26_safe    15737 -> memset@GLIBC   1591b -> slice_index_fail
            1592d -> core::panicking::panic_bounds_check
            15944 -> core::panicking::panic_bounds_check
p26_unsafe  1572b -> memset@GLIBC   1577d -> memset@GLIBC
            15845 -> slice_index_fail
            1585c -> core::panicking::panic_bounds_check
```

Read off the disassembly text those four calls all print as
`call *0x…(%rip)  # <_DYNAMIC+0x2c8>`. **A panic-edge test built on the
disassembly is a false negative**, and that is the most likely way the claim was
made.

The two live checks are in *different loops*:

| rung | live compare-and-branch | where |
|---|---|---|
| `p26_safe` | `cmp $0xfff,%rdi ; ja <panic_bounds_check>` @ `0x15810` | the **scalar epilogue of the vectorised fill**, plus a hoisted `min(OUTCAP−o, n−1)` trip count from two `cmovae` |
| `p26_unsafe` | `cmp $0x1000,%rcx ; je <panic_bounds_check>` @ `0x157a0` | the **checksum fold**, once per 4 elements |

So finding 37's condition is satisfied — a compare-and-branch one rung emits and
the other omits — **with the rungs' roles reversed from what the row assumes.**

### A.1b — the factorial: the 8387 is in the FOLD, not the FILL

`.temp/t115/gen_src2.py` crosses the fill spelling with the fold spelling.
`p26-np016r200.bin`, marginal Ir/call:

```
fill \ fold          fold=safe    fold=unchecked     Δfold
esafe   out[o]=b      24450.30        24447.30          -3
eunsafe get_unchk     32837.30        23277.30       -9560
bsafe   .fill(b)      32789.30        23213.30       -9576
bunsafe write_bytes   32789.30        23213.30       -9576
guard   unchk + if    38872.30        38869.30          -3
```

With the fold unchecked on both sides the inversion **disappears**:
`esafe − eunsafe = +1170` at r=200 and `+1458` at r=16 — safe dearer at both.

Instruction accounting closes: the safe build's fold is 23 insns per 4 elements
(**5.75/element**), the unsafe build's is 35 per 4 (**8.75/element**) because it
must also test `q < 4096` and therefore cannot peel the remainder.
`3.00 × 3200 = 9600` against a measured `9560`.

### A.1c — the null control: two SAFE spellings differ by the whole 8387

```
p26-np016r200.bin    safe 24450.30    safe_fill 32789.30    Δ = +8339
```

`safe_fill` is `out[o..o+n].fill(b)` — safe Rust, same capacity line, same
function — and it is **byte-identical machine code to `unsafe_wb`**
(`ptr::write_bytes`): normalised-disassembly md5 `5917bd8eec3f`, 114 insns, both
(`.temp/t115/kasm.py`, `<SELF+0xNN>` kept per `.temp/t104/probe2.py`), identical
Ir on all three inputs. **One rung wearing two names.** Likewise
`safe == safe_for` and `unsafe == unsafe_for` are byte-identical.

**A difference of the published magnitude is reachable with no safety difference
at all.**

### A.1d — the symmetric control, BOTH directions

*Direction 1 — delete the check from the safe rung.* `safe_nocap` (capacity line
removed): `24450.30 → 24396.30` (r=200), `7570.30 → 7532.30` (r=16),
`55794 → 55388` (np200r020). **The safety line costs +38…+406 Ir/call, never
more than 0.7%.** The unsafe rung moves by the same order (`−51`, `−51`, `−787`).

*Direction 2 — add a check to the unsafe rung.* Two spellings, two answers:
- `unsafe_guard` (redundant `if o < OUTCAP` per write) does **not** restore the
  safe codegen; it makes a third one, `38872.30`, dearer than both. **So the
  fill strategy is not selected by "is there a check".**
- ⚠⚠ the unsafe fill **plus one line before the fold** —
  `if o > OUTCAP { unreachable_unchecked() }` — erases the inversion (below).

### A.1e — instrument check on `memset` (a clean negative, plus one live hazard)

`.temp/t115/memset_ir.c`: callgrind does **not** redirect glibc `memset` to a
byte loop — 36…152 Ir/call for 8…2000 bytes, so the vector-vs-memset comparison
at r=200 is not a valgrind artefact. ⚠ **But at n=4000 it is 4042 Ir/call =
1.011 Ir/byte** — the `rep stosb` ERMS path charged ~1 Ir/byte, the same
instrument effect the catalogue already records for `memcpy`/`rep movsb` at 8192
bytes (p24's row). **Threshold for `memset` is between 2000 and 4000 bytes.**
Any future row that fills more than ~2 KB per call is measuring glibc, not code.

## A.2 — the inversion threshold DOES NOT EXIST; the sign is periodic

Dense sweep, **every** run length 1..254 at np=16 — no stride, so p38's and
p23's residue-class trap cannot apply. 254 × 4 cells, **0 checksum
disagreements** (`.temp/t115/sweep_runlen.json`).

- `ship_safe − ship_unsafe` **changes sign four times**: at **r = 4, 33, 59, 65**.
- `ship_safe` is **discontinuous**: it *drops* by **exactly −2804.00 Ir** at
  r = 33, 65, 97, 129, 161, 193, 225 — every `r ≡ 1 (mod 32)`. 32 is the vector
  width of its fill (`movdqu %xmm0` ×2 = 32 B/iteration); the scalar epilogue
  handles `(r−1) mod 32` bytes at ≈5.5 Ir each and resets. `2804/16 runs =
  175.25` per run ≈ 31 × 5.5.
- `ship_unsafe` has **no** such cliff — two `+252` steps at r=65 and r=129, which
  are glibc `memset`'s own size-class boundaries.
- The linear term is the fold's bounds check: **2.6875 Ir/output byte at r=8
  rising monotonically to 2.9902 at r=254** — asymptotically 3.00.

So `S−U(r) ≈ sawtooth(r mod 32) − 3.00·16·r`. **`TASK_092`'s "the sign is a
property of the RUN LENGTH" is right and understated: it is a property of
`r mod 32`.** Designing an input band for this row would be designing a band that
picks its own answer — which is `p38`'s out-of-sample failure by construction.

## A.3 — ⚠⚠ IT IS p13's FINDING, AND p13's OWN RETRACTION KILLS IT

**Question 1 — is `p26` `p13` again? YES.** RECAP finding 25:

> *"a bound the optimiser can SEE is worth more than the check costs … **the
> discriminator is the BOUND, not the check** … a consumer whose bound LLVM can
> see fully unrolls to 2 Ir/byte; an unbounded walk stays a 4-instruction loop at
> 4 — **+2.00000 Ir per consumed byte at matched spelling**"*, and *"**the sign
> does not survive**: allow R4 a bounded consumer and `R3ship − R4` is +44 / +77."*

`p26` is that, item for item: the thing paid for is the **consumer** (the
checksum fold); the discriminator is the **bound** `o <= OUTCAP`, which the safe
fill's per-element check supplies as a side effect; the price is **+2.99 Ir per
consumed byte at matched spelling**; and the sign does not survive.

⚠⚠ **The sign does not survive, measured over all 254 run lengths**
(`.temp/t115/sweep_hinted.json`): `ship_safe` against the unsafe fill plus one
line, `if o > OUTCAP { unreachable_unchecked() }` — a pure hint, no runtime
check:

```
   r    ship_safe   unsafe+bound   S-U(hinted)   S-U(t92 pair)
   1      4750.30        4825.30      -75.00        -83.00
  16      7570.30        6109.30    +1461.00       +733.00
  33      8014.00        7689.00     +325.00      -1219.00
 100     14626.30       13965.30     +661.00      -4099.00
 200     24450.30       23277.30    +1173.00      -8387.00
 254     31610.00       28245.00    +3365.00      -8787.00
```

**Positive at 253 of 254 run lengths** (only r=1, at −75). The published −8387
becomes **+1173**. `assert!(o <= OUTCAP)` — safe Rust, a real runtime check —
gives the same numbers to within 2 Ir, and costs the *safe* rung nothing
(`24449.30` vs `24450.30`).

⚠ **A `spec.md` that pinned the unsafe rung to the un-hinted spelling would be
p13's contract defect verbatim — the DIRECTION TEST's first fire, repeated.**

**Question 2 — is the inversion `p19`'s (finding 35)? NO, and the difference is
worth recording.** `p19` crosses **once**, because two *rates* cross (O(table)
validation against O(message) checking, at m ≈ 2509). `p26` crosses **four
times**, because a **sawtooth whose period is the SIMD width** is added to a
linear term. Same phenomenology, genuinely different mechanism. ⚠ **But the
sawtooth is not about safety**: it is present with the safety difference removed
(`safe == safe_for` byte-identical; `safe_fill == unsafe_wb` byte-identical), and
it is a property of LLVM's vectoriser epilogue.

## A.4 — the §A.1 question, answered as asked

> *Is `p26`'s 8387 a counterexample to finding 37's "only if" half, or the best
> illustration of it?*

**The best illustration of it, and finding 37 is not contradicted.** There *is* a
compare-and-branch that one rung emits and the other omits — `cmp $0x1000,%rcx ;
je <panic_bounds_check>` in the fold — so the "only if" half is satisfied, not
violated. What `p26` shows is the *other* trap: **the compare-and-branch was in a
loop nobody was looking at, on the rung nobody expected, and a naive reading
would have published an idiom sawtooth plus a misattributed check as a
−2.62 Ir/byte "safe is cheaper" result.** Finding 37 says the instrument can
price a property only when a branch appears; `p26` adds that **finding the branch
is not optional — the sign of the headline depends on which loop it is in.**

## A.5 — VERDICT: ⚠ **REFUSE `p26`**

The deciding measurement: **`safe − unsafe(+bound)` is positive at 253 of 254 run
lengths; the published −8387 is +1173 once the unsafe rung is allowed the bound
the safe rung got for free.** The residual finding is *"a bound the optimiser can
see outweighs the check that supplies it"* — **p13's, second instance**, which is
`TASK_086`'s own kill criterion firing. Under RECAP finding 37's replacement bar
(*a new mechanism — a new operator, a new source of the bound, or a new reason
the check is or is not elided*): the operator is `index >= len` again, the source
of the bound is the capacity test again, and the elision reason is p13's again.
**Nothing new. Refuse, and say the catalogue really is measured out — with this
evidence rather than by assumption.**

The one thing worth keeping is **not a row**: the `memset`/`rep stosb` ~1 Ir/byte
instrument threshold at 2000–4000 bytes, and the GOT-indirect panic-edge false
negative. Both belong in `.memory/03-measurement.md`.

---

# §B — `p37`

## B.1 — the open question the catalogue names: UNREPRESENTABLE, not CHECKED

`.temp/t115/v37/v37_confuse.rs`, at the pin, with a positive control that must
fire:

```
verification results:: 2 verified, 1 errors
```

`good()` — allocate, write a `u64`, read it back as a `u64` — **verifies**.
`confuse()` — the same allocation, re-viewed as an `i64` — fails **three**
preconditions:

```
 line 45  ptu.into_raw()                  -> precondition not satisfied   (requires self.is_uninit())
 line 46  raw.into_typed::<i64>(addr)     -> precondition not satisfied
 line 48  ptr_ref(pi, Tracked(&pti))      -> precondition not satisfied   (requires perm.is_init())
```

The structural one is the third. `~/tools/verus/vstd/raw_ptr.rs:832` —
`into_typed` **ensures `points_to.is_uninit()`**, and `into_raw` (line 849)
**requires `self.is_uninit()`**. **There is no route at this pin from an
initialised `PointsTo<A>` to a readable `PointsTo<B>`.** Second route closed
too: `.temp/t115/v37/v37_transmute.rs` →
`error: core::intrinsics::transmute is not supported`.

⚠ **So `p37`'s R5 is `p08`'s shape** — the bug the language cannot express —
**which the catalogue itself calls the weaker reason to build.** What
`TASK_100`'s `v37_sub2.rs` checks non-vacuously (`pt.ptr() == ud`,
`pt.is_init()`) is **provenance and initialisation, not type identity** — and a
checked validity conjunct on an erased handle is **`p27`'s shape, already built**
(`p27` omits `&& live[h] == 1` on the read path).

## B.2 — cost axis (the probe the row was missing)

`.temp/t115/v37/gen_cost37.py` + `measure37.py`, sec-ladder shipped shape,
benign input, **checksums agree across all three cells**:

```
input                     rs_safe   rs_checked   rs_unsafe
p37-n016-benign.bin        399.00       381.00      343.00
p37-n064-benign.bin       1406.70      1340.70     1206.70
p37-n200-benign.bin       4263.00      4061.00     3655.00
slope, Ir per record        21.00        20.00       18.00
```

**The tag check costs +2.00 Ir/record; the typed-enum spelling costs +3.00.**
The branch multiset confirms the mechanism: `rs_checked` has one more `je` than
`rs_unsafe`, `rs_safe` one more `je` (the discriminant match). That is the same
order as `p36`'s already-published **3.00000 Ir/dispatch**, on the same
mechanism (a table dispatch), in an already-built pattern.

⚠ **A trap for whoever measures this next: my first cut had the tag as a
compile-time constant, and the CHECKED cell came out CHEAPER (15.00 vs 18.00)**
because LLVM proved the opcode and folded the indirect call away. **Do not
measure this row with a constant tag.** Fixed by reading the tag from the window
header.

## B.3 — harm matrix (`env -u LD_PRELOAD`, `grep` not `head`, control that must fire)

`.temp/t115/v37/harm37.sh`, `harm37.c`. modes: 0 = buggy, 1 = hardened,
2 = positive control (unconditional 1-byte heap overread), 3 = buggy with a
neighbour allocated.

| build | mode 0, op=1 (the confusion) | mode 2 (control) |
|---|---|---|
| gcc `-O0`/`-O2`, clang `-O0`/`-O2` | **rc=0, silent, plausible answer** (4 of 4) | silent (expected: malloc slack) |
| gcc `-O1 -fsanitize=address,undefined` | **rc=1, ASan** | **rc=1, ASAN+UBSAN** |
| clang `-O1 -fsanitize=address,undefined` | **rc=1, ASan** | **rc=1, ASAN+UBSAN** |

**The control fires in 4 of 4 sanitiser cells.** The bug is a real 12-byte heap
overread that ASan reports on both compilers and that **is silent with exit 0 in
all 8 plain cells** — and worse, the wrong-typed read returns the *same* value as
the correct one, because glibc's 32-byte minimum chunk absorbs the overread.
With a neighbour allocated (mode 3) **clang `-O2` SIGSEGVs (rc=139) while gcc
`-O2` stays silent**; ⚠ **I did not establish that mechanism** and the planted
`0x53…` secret is still not reached. **Leak magnitude is allocation-dependent —
`p20`/`p48`'s lesson, again.**

## B.4 — the bug-class census (a census, not a whitelist grep)

All **26** built patterns, bug class read off `.memory/06-catalogue.md`'s own
column, one row at a time:

`p01` none · `p02` spatial OOB write · `p03` index underflow · `p04` in-bounds
wrap · `p05` dimension overflow→OOB · `p06` unreduced rotate · `p07` unsigned
underflow + 32-bit overflow · `p08` overlap UB · `p09` missing guard + mask ·
`p10` off-by-one · `p11` missing terminator · `p12` stack overflow · `p13`
truncation semantics · `p14` unbounded field count · `p16` length vs remaining ·
`p17` int overflow→OOB · `p18` unbounded shift · `p19` state confusion · `p22`
non-termination · `p23` `index >= len` · `p27` use-after-free · `p36` index out
of table · `p38` strict-aliasing UB · `p42` leak on error path · `p46` limb
bound/carry · `p47` timing side channel.

**No built row is type confusion** — `p35`'s row is right. ⚠ **But say it with
the qualifier `p35`'s row does not:** `p38` **is** a type pun (`*(const
uint32_t*)r` on a `uint16_t` array); what makes it not `p37` is that its **harm
is a MISCOMPILE, not a wrong-typed read of live data.**

## B.5 — VERDICT: ⚠ **REFUSE `p37`, on new grounds**

`TASK_100`'s finding stands: limb (ii) of the old refusal is measurably false and
must not be re-quoted. **But the row still dies, and now on measurements rather
than an argument:**

1. **R5 is `p08`'s shape.** `2 verified, 1 errors` with a firing positive
   control; `into_typed` ensures `is_uninit()`, `transmute` is unsupported. The
   confusion is unrepresentable, not checked.
2. **The checkable residue is `p27`'s.** `pt.ptr() == ud` + `pt.is_init()` is a
   validity conjunct on an erased handle, which `p27` already ships.
3. **The cost axis is +2.00 Ir/record**, the same order and the same mechanism as
   `p36`'s published 3.00000 Ir/dispatch.

⚠ **And the manager's least-sure call #3 is CORRECT:** the row's distinguishing
feature is `void*` erasure, a C idiom; the Rust side cannot express the
confusion, so the row is `p08`-shaped and should be refused on that ground
rather than kept open. **The catalogue cell should stop saying `NEEDS
RE-TRIAGE`.**

---

# §C — the six `planned` rows, in landable form

**No later task supersedes any of the six.** `TASK_090` *corrects* one harm cell
that covers three of them; `TASK_094` and `TASK_100` *cite* them as precedent
without moving them; `TASK_093` reuses `p25`'s detector standard elsewhere.
Suggested status-cell text, measurements quoted verbatim:

### `p26` — RLE decode expansion → **REFUSE** *(this task; supersedes TASK_086's BUILD)*
> ⚠⚠ **REFUSED at TASK_115 — and `TASK_086`'s third-tier BUILD is withdrawn by
> its own kill criterion.** `TASK_086`'s `5.33×` is invalid (the pair is not the
> same function). `TASK_092`'s matched shipped pair reproduces exactly
> (`7570.30/6837.30`, `24450.30/32837.30`, `55794/44381`) **but its stated
> mechanism is not the cause and its "neither has a panic edge" is FALSE — both
> rungs have one, and the GOT-indirect call is why nobody saw it.** Factorial:
> with the checksum fold unchecked on both sides the inversion vanishes
> (`+1170` at r=200). ⚠ **The `−8387` is the FOLD's bounds check surviving in the
> UNSAFE rung at `2.99 Ir/output byte`, because deleting the fill's check
> destroyed `o <= OUTCAP`.** Null control: `safe` vs `safe_fill` — **two SAFE
> spellings, `Δ = +8339`** — and `safe_fill` is **byte-identical to
> `ptr::write_bytes`** (`5917bd8eec3f`, 114 insns). ⚠⚠ **It is `p13`'s finding
> INCLUDING p13's retraction: give the unsafe rung the bound in one line and
> `S−U` is POSITIVE at 253 of 254 run lengths (published `−8387` → `+1173`).**
> Sweep of every `r ∈ [1,254]`: **four sign changes** (r=4,33,59,65) and
> `ship_safe` drops `−2804.00 Ir` at every `r ≡ 1 (mod 32)`, the SIMD width —
> **so there is no threshold to design a band around.** Evidence:
> `.tasks/TASK_115_REPORT.md`, `.temp/t115/`.

### `p37` — callback with `void*` userdata → **REFUSE** *(this task; closes the re-triage)*
> ⚠⚠ **RE-TRIAGED AND REFUSED at TASK_115.** `TASK_100`'s correction stands —
> limb (ii) is false and must not be re-quoted. The row dies on three new
> measurements instead. **(1) The confusion is UNREPRESENTABLE, `p08`'s shape:**
> `into_typed` **ensures** `is_uninit()` and `into_raw` **requires** it, so there
> is no route from an initialised `PointsTo<A>` to a readable `PointsTo<B>`
> (`2 verified, 1 errors`, positive control `good()` verifies); `transmute` is
> `is not supported` at the pin. What `TASK_100`'s R5 checks is provenance +
> init, i.e. **`p27`'s validity conjunct**, not type identity. **(2) Cost axis:
> `21.00 / 20.00 / 18.00` Ir per record for typed-enum / erased+tag-check /
> erased-unchecked — the tag check is `+2.00`**, the same order as `p36`'s
> published `3.00000` Ir/dispatch. ⚠ Measure it only with a RUNTIME tag: with a
> constant tag the checked cell comes out **cheaper** (15.00) because LLVM folds
> the dispatch. **(3) Harm: silent, exit 0, plausible answer in 8 of 8 plain
> cells**; ASan fires 2/2, control 4/4; clang `-O2` SIGSEGVs only when a
> neighbour is allocated. Type confusion **is** absent from the built tree
> (census of all 26), nearest `p38` — ⚠ but `p38` **is** a pun; what differs is
> that its harm is a MISCOMPILE. Evidence: `.tasks/TASK_115_REPORT.md`.

### `p20` — length/offset pair (Heartbleed) → **DEFER**, and the reason is now STRONGER
> **DEFERRED at TASK_086, with a measurement, and the deferral reason is
> stronger than that report states.** Probe 3: `k20_checked 22070.00` vs
> `k20_unchecked 22060.00` = **`+10.00` Ir/call, FLAT — `0.0024` Ir/byte at
> n=4096 and falling**; the whole check is six instructions at the top
> (`add;setb;cmp;seta;or;jne`) and the loop body is the identical 8×-unrolled
> fold. **A length/offset check is O(1) and does not scale.** Probe 2 clean
> (`251 B 056e9912…` vs `235 B e6f559dc…`); probe 4 clean
> (`slice::from_raw_parts` 0 hits). ⚠⚠ **Kill risk, MEASURED: with `secret`
> malloc'd BEFORE `buf` the identical run leaked 0 bytes** — `p48`'s lesson.
> ⚠ **`TASK_086`'s own disclosure: `leaked_secret_bytes=1616` counts coincidental
> `0x53` bytes and is not an oracle — do not quote that figure.**
> ⚠ **TASK_115: the duplication reason names too few patterns.** `TASK_086` said
> *"p16's and p02's"*; **`p17` is built, reviewed, and IS a trusted-length-field
> OOB (`int overflow → OOB`, cf. CVE-2017-7529), with the leaking slice-guard
> variant reproduced at TASK_012.** So `p20` duplicates **three** built rows,
> not two, and the deferral holds a fortiori.

### `p21` — CSV/field splitter with escapes → **DEFER**
> **DEFERRED at TASK_086, with a measurement.** Probe 3:
> `26862.00` vs `26788.00` = **`+74.00` Ir/call**, and the tax is **per FIELD,
> not per byte** — the `buf[i]` check is hoisted and what remains is `nf < 64` on
> ~74 commas. Probe 2 clean (`210 B fb463072…` vs `213 B 9c45103b…`); probe 4
> `::get_unchecked` 0 hits. ⚠ **Kill risk: the quote-state adds a data-dependent
> branch but NO NEW BOUND — the row is `p14` with a different delimiter rule, and
> `p14`'s row already says its bug class is the unbounded field count.**
> ⚠ **Harm cell corrected at TASK_090: `p21` fires BOTH ASan and UBSan; the
> `head -4` in `.temp/t86/harms.sh` showed only the UBSan half.**

### `p25` — dynamic array `realloc` growth → **DEFER stands (never probed)**
> **NOT PROBED at TASK_086 — out of scope per its task file, which recorded
> "nothing found that disturbs p25's defer".** ⚠ **This row has no measurement
> of its own and should not be quoted as if it did.** Later corroboration only:
> `TASK_093` §0.1 reuses *"`p25`'s standard"* — the detector test — to refuse a
> different row, and `TASK_100` §B5 confirms *"the resize path is `p25`'s row,
> still `planned`; verdict unchanged"*.

### `p40` — SoA vs AoS → **REFUSE, with the measurement**
> **REFUSED at TASK_086, with the measurement.** N=1048576, 3 iterations,
> `callgrind --cache-sim=yes`: `k40_aos` **360,114,293** Ir / 3,481,161 D1 misses
> / 1,912,884 LLd read misses; `k40_soa` **360,114,314** / 2,301,516 / 454,953.
> **21 Ir out of 360 million (5.8e-8) while LLd read misses differ 4.20× —
> the row's own axis is invisible in the project's primary metric.** And the
> safety axis is zero too: `k40_soa_idx 360,114,467` vs `k40_soa_unchecked
> 360,114,274` = **`+193` Ir in 360M** for a bounds check over 3M elements =
> `6.4e-5` Ir/element. **Wall clock cannot rescue it:** best-of-7 spreads
> **2.8%–32.7%**, over the project's own 10% discard threshold on **3 of 4**
> rungs. The catalogue's own bug column is *"none — pure perf axis"*. **`p01`'s
> axis with `p31`'s problem.**

### `p41` — flexible array member → **REFUSE, with the measurement**
> **REFUSED at TASK_086, with the measurement.** Probe 3 kills it:
> `k41_checked 23614.00`, `k41_tuned` **`2387.00`**, `k41_unchecked 2404.00` —
> **the tuned SAFE rung BEATS the unsafe rung by `17.00` Ir/call**, and the
> apparent 9.6× was **100% R3 spelling** (byte-at-a-time
> `from_le_bytes([buf[o],…])` against a `chunks_exact(4)` walk). **That is
> `p10`'s error exactly, and here it is 100%.** ⚠ **The bug class is unreachable
> in the natural spelling:** `sizeof(hdr) + n*sizeof(uint32_t)` in `size_t` does
> not wrap for any `n` a wire format can express; the harm only fires with the
> product cast to `uint32_t`, **which is `p07`'s finding verbatim and `p07`
> already ships the reachable 32-bit-check version as `adversarial-width.bin`**.
> Probes 1, 2 and 4 **pass** (285 B / 244 B / 175 B, all distinct) — **the row
> dies on probe 3 and on duplication, not on the ladder test.**
> ⚠ **Harm cell corrected at TASK_090: `p41` fires BOTH detectors.**

---

## Clean negatives — named attacks that did NOT land. Do not re-run these.

1. **"callgrind redirects `memset` to a byte loop, so the whole 8387 is a
   valgrind artefact."** ✗ It does not: 36…152 Ir/call for 8…2000 bytes
   (`memset_ir.c`). *(But `rep stosb` above ~2–4 KB IS charged ~1 Ir/byte — see
   §A.1e; that hazard is real and separate.)*
2. **"`p26`'s divergence is the `memset`-vs-vector fill idiom."** ✗ That axis is
   worth **+1170 in the opposite direction** (factorial, §A.1b).
3. **"Adding a check to the unsafe rung recovers the safe rung's codegen."**
   ✗ `unsafe_guard` produces a *third* codegen, dearer than both (38872.30).
4. **"`p37`'s R5 obligation is new."** ✗ It is provenance + init, which `p27`
   already checks; the type half is unrepresentable.
5. **"`p37` can be costed with a constant tag."** ✗ LLVM folds the dispatch and
   the checked rung comes out cheaper.
6. **`.temp/t104/probe2.py`'s truncation rule on these kernels.** ✗ It cuts at
   the **last `ret`**, and LLVM puts the single `ret` epilogue in the *middle* —
   31 of 177 instructions. Strip trailing padding instead
   (`.temp/t115/kasm.py`). This is a **false negative on a kill criterion** in
   the tool the catalogue currently recommends.

## Problems / worked around

- `.temp/t104/probe2.py` truncation defect (above) — worked around in
  `.temp/t115/kasm.py`, not fixed in place (I do not edit others' probes).
- The `p37` mode-3 clang `-O2` SIGSEGV is **not explained**. Cite it, do not
  explain it.
- `measure.py`'s first draft asserted checksum equality across `n_iters`, which
  is wrong (the fold accumulates). Corrected; the cross-check is across
  *variants* at fixed `n_iters`, as `.temp/t92/partB/measure.py` does it.

## Unsure / not done

- **No pattern was built and nothing went through `harness/check.py`**, by
  instruction. Every number is from throwaway kernels.
- The `p26` kernels are `TASK_092`'s reading of "shipped shape". **A real `p26`
  might differ**, and in particular a `p26` whose checksum fold did not index the
  same scratch would not show this effect at all. That is an argument for
  refusing the row, not for trusting the number.
- **I did not build a C rung for `p26`**, and no C-vs-Rust claim is made here.
- `p37`'s C rung exists only as a harm probe (`harm37.c`), not as a costed
  sec-ladder rung; the cost axis is Rust-only. **A `c-gcc`/`c-clang` column for
  `p37` is not established.**
- The `p26` sweep holds `np = 16`. A second axis (`np` at fixed `r`) was
  generated but **not measured** — the run-length axis is where `TASK_092` put
  the question and the budget went there.
- **I did not attempt a `p37` R5 with a `PointsToRaw` userdata passed by value
  through the trait**; `into_typed` consumes `tracked self`, so only one callback
  could ever hold it, but I did not run that.
- No `.memory/` edit, no `RECAP.md` edit, no `git add`/`commit`.

## Memory updates owed (manager applies, after review)

1. `.memory/03-measurement.md`: ⚠ **GOT-indirect calls make a panic-edge test
   read off disassembly text a FALSE NEGATIVE** in a PIE — objdump prints
   `_DYNAMIC+0xNN` for the slot. Resolve through `.rela.dyn`
   (`.temp/t115/resolve_calls.py`). **This produced a false claim in
   `TASK_092` PART B.**
2. `.memory/03-measurement.md`: **glibc `memset` crosses to `rep stosb` between
   2000 and 4000 bytes and callgrind then charges ~1.011 Ir/byte** — the same
   effect the catalogue records for `memcpy` at 8192. Below that it is
   36…152 Ir/call.
3. `.memory/06-catalogue.md`: ⚠ `.temp/t104/probe2.py` truncates at the **last
   `ret`** and that is wrong whenever LLVM sinks the epilogue — 31 of 177
   instructions on these kernels. The catalogue recommends this tool.
4. `.memory/06-catalogue.md`: the six status cells above.
5. `.memory/01-ladder.md` finding 25 (p13): **second instance, in `p26`, with the
   retraction reproducing** — +2.99 Ir/consumed byte, sign gone once the unsafe
   rung is allowed the bound.
