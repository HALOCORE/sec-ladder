# TASK_066_REVIEW — p38-alias-pun, reviewer report

**Verdict: no blocker. 3 majors, 8 minors, 35 clean negatives.** The gate
re-runs PASS, every number in `NOTES.md` §1/§2/§4a/§4b/§8/§9/§10 that I re-derived
reproduced exactly, and the six refutations the engineer landed on the manager
all hold. What does not hold is **three of the replacement claims**, and one of
them is the A3 headline.

Scratch: `.temp/p38rev/` (probes and generators kept, binaries deleted).
Tree left clean — `results/gate/p38-alias-pun.json` was rewritten by my gate
re-run and restored with `git checkout --`.

---

## Premises in the task file that are wrong, with the measurement

**P1 — A5's direction is inverted.** TASK_066_REVIEW:120 says *"a cheaper R4
makes `R3 − R4` larger, so the unsearched side flatters **unsafe**, not safe."*
It flatters **safe**, exactly as on p10 and p27. `r4_slice` is −3.00 / −7.00
against `R4ship` (reproduced, §8b table below), so the true `R3 − inf(R4 found)`
is **+24 / +32** and what ships is **+21 / +25**. Publishing the smaller number
makes the safe rung look *closer* to unsafe, which is `.memory/01-ladder.md`
finding 18's defect direction verbatim (*"an unsearched R4 side flatters the
safe rung"*). p38 therefore has p10's defect in kind, at 14 % / 28 % of the
headline; it is disclosed in `NOTES.md` §8b/§10d and **not** in `README.md`.

**P2 — A3's proposed test does not settle it, and `nw` is the wrong column.**
TASK_066_REVIEW:88 says *"Settle it by adding `nw` and refitting."* I did.
Adding a linear `nw` column makes the out-of-sample residual **worse**:

```
R2-R4  D1 [1,nrec,nrec*rlen]      coef 61.20016 -6.66160 6.42278            in 27.41364  OOS  86.66080
       D2 [1,nrec,nrec*rlen,nw]   coef 1643.81910 -8.22576 6.55644 -6.52008 in 16.80680  OOS 102.74096
```

(D1 reproduces the engineer's published figures to the digit, including
`sweep-x09u03 = 88` measured.) See major M1 for what the columns actually are.

**P3 — A4's *"any UB class that exists only at `-O2` and above"* is false.**
The class is not level-gated, it is flag-gated, and `-O1` is enough:

```
gcc -O1 (default)            8516071857945885891   OK
gcc -O1 -fstrict-aliasing   13195311868066990464   *** WRONG
gcc -O1 -fno-strict-aliasing 8516071857945885891   OK
gcc -O1 -fstrict-aliasing -fsanitize=address:
  ERROR: AddressSanitizer: stack-buffer-overflow ... READ of size 2 ... kernel.c:84
```

**P4 — the engineer's stated cause for A3 is measured false.** `NOTES.md`:319
says *"R2 also pays a bounds check per window byte in the decode loop, and `nw`
is a third structural parameter that neither band varies."* `R2 − R4` is
**exactly constant in `nw`**: holding `(nrec, rlen) = (2, 4)` it is `115.00` at
`nw` = 128, 160, 200, 240, 248 **and** 256, and `88.00` at every one of those for
`(9, 3)`. The only `nw` that moves it is one whose residue mod 8 is non-zero.

---

## MAJOR

### M1 — the additivity failure is real, its published cause is false, and the law is exactly repairable — `NOTES.md`:309-324, `README.md`:66-72

The manager asked whether this is *a real non-additivity* or *a domain error*.
**It is both, and neither is `nw`.** Measured with the engineer's own estimator
(`controls/fit.py`'s marginal-Ir difference), on the engineer's own blobs, plus
two designs nobody had run: an `nw`-only sweep at fixed `(nrec, rlen)`, and a
7 × 7 `(nrec, rlen)` grid at fixed `nw = 256`.

**(a) A genuine `nrec × rlen` interaction, through the parity of `rlen`.**
At `nw = 256`, `R2 − R4 = 79 + s(rlen)·nrec` with

```
rlen     2     3     4     5     6     7    10
s(rlen)  5     1    18    14    31    27    57
         s = 6.5*rlen - 8     (rlen even)
         s = 6.5*rlen - 18.5  (rlen odd)     -> odd records cost 10.5 LESS each
```

No function of `nw` can remove that; it is an interaction, so the additivity
test failed for a real reason. It is also invisible to the shipped band design,
because band `r` fixes `rlen = 4` (even).

**(b) A band-design defect, and the column is `nw mod 8`, not `nw`.**
Fine sweep at `(nrec, rlen) = (2, 4)`:

```
nw     238  239  240  241  242  243  244  245  246  247  248  250  252  254  255  256
R2-R4  105  111  115   75   81   87   93   99  105  111  115   81   93  105  111  115
nw%8     6    7    0    1    2    3    4    5    6    7    0    2    4    6    7    0
```

Band `r` sits at `nw = 240` (`0 mod 8`), band `x` at `256` (`0 mod 8`), and
**band `w` sits entirely at `244` (`4 mod 8`)** — worth a flat `−22`. That is a
missing column, and it is the manager's "DOMAIN is a missing column" rule
landing — on a column nobody named.

**(c) The repaired law, exact everywhere including out of sample.**

```
R2 - R4 = A(nw mod 8) - 8*nrec + 6.5*nrec*rlen - 10.5*nrec*(rlen mod 2)
          A(0) = 79 ;  A(m) = 33 + 6m  for m = 1..7
```

| set | rows | max abs residual |
|---|---:|---:|
| sweep bands `r` + `w` (in sample) | 22 | **0.00000** (except `sweep-w01`, the already-disclosed `rlen = 1` blob, 12.00) |
| sweep band `x` (**out of sample**) | 6 | **0.00000** |
| independent `(nrec, rlen)` grid at `nw = 256`, never measured before | 49 | **0.00000** |
| the measured matrix, kernel-exclusive `Ir`/call | `small` 257, `large` 711 | **0.00** and **0.00** |

So *"the first failure of this project's additivity test"* survives as an event
but **not as written**: the failure is 100 % attributable, half of it to a
genuine interaction and half to a band placed on an anomalous `nw` residue, and
the model the engineer says is "missing a regressor" is missing **two**, neither
of which is the one named. `README.md`:66-72 and `NOTES.md` §4c must not go into
`.memory/` in their present form — this is precisely the "much larger claim than
the evidence supports" the task file warned about, with the mechanism now
supplied (PROTOCOL rule 12).

Note also that `NOTES.md` §4c publishes the misspecified fit
(`61.20 − 6.66·nrec + 6.42·nrec·rlen`) as an equation. Those three coefficients
are artefacts of the misspecification and none of them is a p38 result.

### M2 — "structurally blind" is wrong, and it misdirects the queued gate fix — `NOTES.md`:371, `model.py`:228-248, `README.md`:78-79

`NOTES.md`:371: *"gcc enables `-fstrict-aliasing` at `-O2`; the gate's stage 7
builds at `-O1`, so the gate's own sanitizer stage is **structurally blind** to
p38"*. The hole is real and the engineer was right to report it — but it is
**one flag wide, not one optimisation level wide**. `harness/check.py`:4738
builds `-O1 -fsanitize=address,undefined`; add `-fstrict-aliasing` and stage 7
sees p38 at `-O1`:

```
gcc -O1 -fstrict-aliasing -fsanitize=address -static-libasan
  ERROR: AddressSanitizer: stack-buffer-overflow ... READ of size 2
  SUMMARY: ... kernel.c:84 in kernel
gcc -O1 -fstrict-aliasing -fsanitize=address,undefined
  kernel.c:84:42: runtime error: index 256 out of bounds for type 'uint16_t [256]'
```

Read literally, `NOTES.md` says the repair is to raise stage 7's optimisation
level — which would perturb 20 patterns' sanitizer rows. The repair that works
is one token and changes nothing else. `RECAP` "Owed" 12 and
`.memory/02-bench-rules.md` will inherit whichever sentence lands.

**Blast radius, which the task asked for and nobody had measured: exactly one
pattern.** Across all 20 gate records, 16 patterns declare at least one
`sanitizer_expect: "fires"` input and every one of them fires at `-O1`
(p18-varint-shift, the other UB pattern, fires on all four of its rows). The
four that declare none are p01, p08, p47 and p38. p01 and p08 model no
memory-safety bug; p47's is a timing property outside every sanitizer; **p38 is
the only pattern in the tree whose declared-clean adversarial row is clean
*because of the gate's build flags rather than because of the kernel*.** So this
is a p38 note plus a one-line gate fix, not a `major` about the gate's history.

**Is p38's security half adequately evidenced by a control?** Yes, but not by
the control it names — see minor m7: `s_asan_O3` does not exist. The evidence
that does exist and that I reproduced is the `-O3` ASan run above and the
disassembly in §2.

### M3 — the idiomaticity claim is asserted, not evidenced, and the harm needs FOUR conjunctive conditions that are nowhere stated — `c/kernel.c`:7, :19-23

`c/kernel.c`:7 — *"Both are ordinary C and the pair is written this way in real
parsers."* No citation. `:19-23` — *"it is not a straw man. Replace
`*(const uint32_t *)r` with the two-half spelling ... That single expression is
the whole of p38."* True, but it is one of **four** single-edit counterfactuals
that each remove the harm, and the write-up names only the one that flatters the
framing. All measured on the shipped `c/kernel.c`, gcc 13.3.0 `-O3
-DSLB_ISOLATED`, `adversarial-oob.bin` (defined answer `8516071857945885891`):

| one-line variant of the shipped R1 | gcc `-O3` result | `Ir`/call vs shipped R1 |
|---|---|---:|
| **shipped** (pun getter, two-half setter, getter called twice) | **wrong, non-deterministic** | — |
| `rec_set_len` also puns (`*(uint32_t *)r = v`) — a *symmetric* accessor pair | **correct** | **−6.00** |
| `rec_len` called once, clamp into a local (`c_once`) | **correct** | **−6.00** |
| same, and no write-back at all | **correct** | −2.00 |
| `-fno-strict-aliasing` on the identical source | **correct** | **−6.00** |
| two-pass parser: sanitise loop, then walk loop (the realistic reason to write a clamp *back*) | **correct** | — |
| `rec_set_len` in its own TU, no LTO (accessor in a `.c` rather than a header) | **correct** (fires again under `-flto`) | — |
| shipped R1h (two-half getter) | correct | +12.00 |

So the harm requires **(i)** the getter and setter to disagree about the access
type, **(ii)** the getter to be called a *second* time after the setter, **(iii)**
the write-back to have no consumer other than that second read, and **(iv)** both
accessors visible in one optimisable region. `sc[i]`/`sc[i+1]` are read by
nothing else in the kernel and the cursor never revisits them, so condition (iii)
is structural: **the clamp store exists only to be re-read three lines later**,
which is not why real parsers write a value back into a buffer — and the shape
that *is* (a sanitise pass followed by a parse pass) is the one the engineer's
own `harm4.c` found does not reproduce, which I have now confirmed on p38's own
kernel.

This does not make p38 fake — the bug class is real, ASan-confirmed, and the
Linux kernel builds `-fno-strict-aliasing` for exactly it. It makes the *claim*
"this is what real parsers write" unsupported, and it leaves the pattern's
strongest honest sentence unwritten: **on gcc the undefined spelling is the
dearest of the five neighbouring spellings — three independent one-line fixes
each save exactly 6.00 `Ir`/call, and the UB is not even a speed win against the
natural single-read spelling.** `NOTES.md` §8c currently frames that 6.00 as a
property of the *flag*; it is a property of *not doing the double read*, and
`c_once` and the symmetric accessor pair buy the identical 6.00.

Recommended severity if corrected: state the conjunction, drop or cite
":7", and promote the "dearest of five" sentence. The finding survives as a
security result at the lower severity the task file anticipated.

---

## MINOR

**m1 — `README.md` publishes `R3 − R4 = +21.0 / +25.0` with no R4-side
disclosure** (`README.md`:97-98; also `NOTES.md`:306, *"p38's safety tax is
`O(1)` per record"*). The disclosure exists in `NOTES.md` §8b/§10d and is
correct; the summary file a reader reaches first carries the fixed-R4 bound as
if it were the tax. See P1 for the direction.

**m2 — `NOTES.md`:328 says "6 of 32 O3 wall cells" were discarded; the data and
the file it cites both say 4.** `results/tables/p38-alias-pun.md`:194 says
"**4 of 32**" and lists exactly four; recounted from
`results/p38-alias-pun.json`, four O3 wall cells exceed 10 % (`c-clang/isolated`
11.09, `safe_naive/isolated` 11.66, `unsafe/isolated` 10.92, `c-clang-h/whole`
10.25). No claim rests on it, but it is a number in the file the manager copies
from.

**m3 — the run-to-run variation on `adversarial-oob` is NOT ASLR**
(`NOTES.md`:211-218, `README.md`:52). Measured:

```
adversarial-stale, ASLR on      : 4 runs, 4 different checksums
adversarial-stale, setarch -R env -i : 4 runs, IDENTICAL (17682374070775870151)
adversarial-oob,   setarch -R env -i : 4 runs, 4 different checksums
adversarial-oob,   setarch -R env -i, -fno-stack-protector : 3 runs, 3 different
```

So the ASLR attribution is right for `-stale` (the read that stays inside `sc`)
and wrong for `-oob` (the read that leaves it) — and `-oob` is the row both the
README headline and the gate record use. The residue past the frame varies for a
reason that is not address randomisation and that I did not pin down; the
shipped build does carry a stack canary (`mov %fs:,%rax` in `kernel`), so at
least one leaked word is `AT_RANDOM`-derived, but removing the canary does not
make it deterministic.

**m4 — the "clang declines" mechanism is narrower than the mechanism**
(`NOTES.md`:89-94, `c/kernel.h`:60-65). Stated: *"LLVM does not apply TBAA when
BasicAA has already proved the two accesses are the **same address**"*. Two new
controls (`.temp/p38rev/a4/mustalias2.c`, `mustalias3.c`):

```
                                   gcc O1/O2/O3   clang O1/O2/O3
one_base        (full overlap)         4000            16      declines
one_base_partial(only w[0] written)    4000            16      declines  <- NOT MustAlias
two_params      (unrelatable ptrs)     4000          4000      exploits
known_off  (ONE base, offset known)    4000            16      declines
opaque_off (ONE base, offset opaque)   4000          4000      exploits  <- decisive
```

`one_base_partial` is never MustAlias, and clang still declines; `opaque_off`
keeps the single base and only hides the offset, and clang exploits. The
discriminator is **whether BasicAA can compute the offset**, not "the same
address" and not "one base pointer" — and p38's own kernel is the *partial*
case (each 2-byte store against the 4-byte load), which the stated wording does
not cover. Separately, the shipped `c-clang-O3-isolated` listing shows clang
**merging the two `uint16_t` clamp stores into one 32-bit store**
(`mov %ebx,-(%rsp,%r11,2)`, instruction 103) where gcc emits two 16-bit stores —
a second reason the forwarded value is type-consistent on clang, omitted from
the one-line mechanism. The conclusion (*"clang is safe" is false*) is upheld.

**m5 — TySan §6a: "promotion" is right for the object and incomplete for the
report count** (`NOTES.md`:377-418). The engineer's whole table reproduced
exactly on my rebuild (two-TU 2/2/2/2, one-TU 2/0/0/0, M1 2/2/2/2, M2 2/2/1/1,
M3 2/2/2/2), and I added the discriminator they did not run: **M4 — one TU,
fully inlined, stack object, address does *not* escape, only dynamically indexed
so SROA cannot promote it — fires 2 at every level.** That isolates
promotability from inlining, from escape and from the heap, and **upholds the
replacement claim**. What is incomplete is the count: M2's `2 → 1` at `-O2` is
not promotion — the IR shows the type-establishing `store i32` dead-stored away,
after which the report *changes direction*
(`READ of size 4 with type int accesses an existing object of type short`). The
same halving happens on p38's own kernel (160000 → 80000 violations at `-O2`,
both inline modes), on a 512-byte in-memory array that is never promoted. The
accurate general statement is *"TySan checks only the accesses that survive to
the end of the pipeline; promotion is the case that removes all of them."*

**m6 — `c/kernel.h` documents two spellings the pattern's own contract rejects.**
`:22` — *"`c/kernel_hardened.c` writes `(uint32_t)r[0] | ((uint32_t)r[1] << 16)`
instead"*. It does not; it writes `+ 65536 *`, and the contract's `why` says the
decode is written *"with + and * and never with | and <<"* to stay in linear
arithmetic. `:36` — the header's pseudo-code writes the guard as
`while o < nrec && nw - i >= 2`, the subtraction-first form `required[3]` exists
to forbid and explains at length. Comments are blanked before `spelling_matches`,
so no gate stage can see either.

**m7 — `s_asan_O3` is cited in three committed files and does not exist.**
`NOTES.md`:371, `model.py`:242 and `spec.md`:200 (hence `mkcontract.py`:635) all
say *"`controls/gen_controls.py` ships that build as `s_asan_O3`"*.
`gen_controls.py --list` ships `c_memcpy, c_union, c_once, c_nosa, c_pun,
c_halves, r4_pun, sanitizers, mustalias`. The `-O3` ASan build exists but is
anonymous inside `do_sanitizers()` under the tag `"gcc -O3 asan+ubsan"` and
cannot be selected by name. This is PROTOCOL rule 10's failure class inside
`spec.md`, the hashed layer, and the fix has to go in the **generator** too.

**m8 — `NOTES.md` §10a's third row is not self-consistent, and it is the only
snapshot there is** (`NOTES.md`:653). It says **six** backticked spans were
de-backticked *"because `idiom_audit` reported them as `pins nothing`"* and that
`required_pins_nothing` went **"4 → 0"**. Six spans that each pin nothing move
that counter by six, not four. And one of the six, `nw - i >= 2`, is **not
present in the shipped contract block at all** (`grep` finds it only in
`spec.md`:95 prose, still backticked, and in `c/kernel.h`:36) — so that entry was
rewritten, not de-backticked. The final sha256 checks out
(`9a413347f3336869c2f7c0add48b6f760d9a50ce7791c8dcc4cf0f4c287adccd`, recomputed
from the block plus its trailing newline), the shipped block has 9 `required`
and 10 `forbidden` entries, `required_pins_nothing` is 0 and `forbidden_hits` is
0 — but the *narrative* of the third edit is the one part of the disclosure I
cannot make add up, and PROTOCOL rule 6 is explicit that a wrong disclosure
removes the check it was meant to enable.

Related, and the same class the engineer fixed six times: `required[1].rust`
still pins `` `[u16; 256]` `` while its own English says *"in all four Rust
rungs"*. It occurs only in `verus.rs` (6×); `safe_naive.rs`, `safe_tuned.rs` and
`unsafe.rs` all write `[u16; SCRATCH_W]`. The gate reports it as three
`required_absent` pairs and nobody reads them.

**m9 — §4b and §4c name neither the inline mode nor the `Ir` convention**
(`NOTES.md`:274-324). `.memory/03-measurement.md` has an explicit INLINE-MODE
rule (*"a law fitted in one INLINE MODE is not the law in the other — the
regressors can SWAP"*, p10) and two `Ir` conventions; TASK_066 repeated *"NAME
THE INLINE MODE at every figure"*. §4a is kernel-exclusive `Ir`, §4b/§4c are
whole-program marginals from `-O3 isolated` cells (`controls/fit.py`'s `PAIRS`),
and nothing in the text says so. It happens not to matter here — I verified the
repaired M1 law predicts the kernel-exclusive matrix figures exactly as well —
but that is luck, not disclosure.

---

## Clean negatives — 35 attacks that did NOT land

Every one of these is a thing I tried to break and could not; do not re-run them.

**A1 — the miscompile**

1. `-fno-strict-aliasing` on the shipped gcc `-O3` kernel: harm **vanishes**,
   defined answer, 236 vs 237 instructions. The decisive control lands.
2. clang, 15 cells (`O0/O1/O2/O3/Os` × default / `-fstrict-aliasing` /
   `-fno-strict-aliasing`): **defined answer in 15 of 15**. "clang does not
   exploit it here" holds without exception.
3. gcc `-O0`, all three flag settings: correct. The overflow is **not**
   reachable-but-silent at `-O0`.
4. Is the clamp store dead? **No.** `v_ship` (237 insns, `096a44a91938…`) is not
   `v_noclamp` (224, `0f5d8690bd43…`); the stores are emitted and executed.
   Deleting only the *store* gives an object **byte-identical** to deleting the
   whole clamp, on both compilers — the store is inert only because nothing
   observes it, which is the claim.
5. `NOTES.md` §2's gcc listing reproduces instruction for instruction
   (`asm.py` normalised indices 197-207, quoted as "198-209"): one 32-bit load,
   `lea (%r12,%r12,1),%rdi` from the pre-clamp value, then both clamp stores.
6. …and there is **no second load of the length field** anywhere in the shipped
   gcc kernel; index 213's `movzwl (%rsi,%rdx,2),%eax` is the payload fold.
7. `NOTES.md` §2's hardened listing reproduces: the two `movzwl`, the two clamp
   stores at 209/210, and **the re-read at 211** (`movzwl (%rsp,%rcx,2),%esi`)
   followed by `add %rsi,%rsi`.
8. §1's static table reproduces exactly — gcc 237 / 243, clang 175 / 185, and
   `md5_fn 366e3be50428933dee85aae05655e7ff` shared by the pun, `c_memcpy`,
   `c_union` and `c_nosa` on clang.
9. §8c's flag price reproduces to the digit: gcc 1043.72 → 1037.72 = **−6.00**,
   clang 1274.72 → 1274.72 = **0.00 and byte-identical**.
10. `c_once` reproduces at **−6.00** `Ir`/call on gcc and correct on every cell.
11. Heap-allocated scratch still miscompiles on gcc — the harm does not depend on
    `sc` being a stack array.
12. ASan at gcc `-O3` gives exactly `stack-buffer-overflow READ of size 2` at
    `kernel.c:84`, as claimed.
13. `adversarial-stale` **is** deterministic with ASLR off (4/4 identical) — the
    ASLR attribution holds for that row even though it fails for `-oob` (m3).

**A2 — TySan**

14. The engineer's whole probe-4 table reproduces on a fresh build: two-TU
    2/2/2/2, one-TU-static 2/0/0/0, M1 2/2/2/2, M2 2/2/1/1, M3 2/2/2/2.
15. New probe M4 (one TU, inlined, stack object, no escape, dynamic index ⇒
    unpromotable) fires **2 at every level** — promotability isolated from
    inlining, escape and the heap. **The replacement claim is upheld and
    strengthened.**
16. p38's own kernel fires under TySan in **both** inline modes at every level
    (`-DSLB_ISOLATED` and `-flto`, `O0..O3`, 8 of 8 cells). The prediction that
    could have failed does not.
17. `-fsanitize=undefined` alone has no strict-aliasing check; it fires only as
    `array-bounds` and only where the index leaves a statically typed array —
    reproduced.

**A3 — the laws**

18. `R1h − R1 = 3.00000·nrec` (gcc) and `8.00000·nrec` (clang), **max residual
    0.00000 in and out of sample**, re-derived with my own fitter on the shipped
    blobs.
19. …and it predicts the measured matrix: gcc 1040−1028 = 12 = 3·4, 2582−2558 =
    24 = 3·8; clang 32 = 8·4 and 64 = 8·8.
20. `R3 − R4 = 17 + 1.00·nrec`, exact on **27 of 28** sweep blobs with
    `sweep-w01` (rlen 1) the sole exception at 21 vs 19 — exactly as disclosed —
    and exact on both matrix blobs (21 / 25).
21. …and exact on all **49** cells of an independent `(nrec, rlen)` grid at
    `nw = 256` that had never been measured.
22. …and exactly **independent of `nw`**: 19.00 at `nw` = 128/160/200/240/244/256
    for `nrec = 2`. The `nw mod 8` anomaly that wrecks `R2 − R4` does not touch
    the safety law.
23. §4a's eight kernel-exclusive `Ir`/call rows all re-derive from
    `results/p38-alias-pun.json` (1028.0/2558.0 … 1306.0/3261.0).

**A5 — the R4 side, and the ladder claim**

24. `r4_pun`'s Verus twin fails with **exactly three** `is not supported`
    diagnostics — `core::ptr::read_unaligned`, `core::ptr::const_ptr::…::add`,
    `core::slice::…::as_ptr`. Reproduced verbatim.
25. The pinned vstd (`~/tools/verus/vstd/`) contains **no `get_unchecked` spec at
    all**, so `r4_slice` genuinely needs two new trusted items (an unchecked
    reslice and a `&[u16]` element accessor). The disclosure is honest.
26. `controls/span.py` reproduces every number: R3ship 1391.30/3350.00,
    R4ship 1370.30/3325.00, `r4_slice` **−3.00 / −7.00**, `r4_end` +79.00/+303.00
    (twin 11 verified / 2 errors, no `is not supported`), `r3_wholeslice`
    +0.00/+0.00, `r3_iter` +122.00/+390.00, `r3_noreslice` +206.00/+622.00, all
    with the shipped checksum.

**Verus, TCB, gate**

27. `verus.rs` = **13 verified, 0 errors**; `--cfg slb_twin` = **16 / 0**.
28. Both proof mutants reproduce at 12 verified / 1 error and both fail on
    `invariant not satisfied before loop` — the spatial fact, not a ghost
    assertion. Not vacuous.
29. TCB recount: exactly **5** `#[verifier::external_body]` items
    (`buf_get_unchecked`, `sc_get_unchecked`, `sc_set_unchecked`, `load_input`,
    `emit`), 3 twins, and **no `assume`, `assume_specification`, `admit` or bare
    `external`** anywhere in `verus.rs`. The gate's `tcb_items` is 5.
30. The gate's own `requires_strength` stage proves all four probed clauses are
    "not a tautology" and `verified_call_site` is non-vacuous (`main` 5,
    `kernel` 5).
31. `R4 ≡ R5`: `exact` at O3 (`md5_fn 59ee6732b504cd73ba0debfa08772b86` on both)
    and `norel` at O0 — from the gate record, matching the pin.
32. **`harness/check.py p38` re-run: PASS, 0 failures, 0 blocked, complete run.**
    The only diff against the committed record is the three ASLR-dependent
    `c-gcc` adversarial checksums; the three `notes` lines (2 / 3 / 3 distinct
    behaviours) are byte-identical, so no genuine non-determinism is hiding in
    the structure of the adversarial table.
33. `harness/measure.py p38 --check-stale`: 2 records examined, **0 STALE**.
34. `controls/mkcontract.py --check`: *"spec.md is up to date"* — no
    artefact-vs-generator skew, the defect three tasks in a row shipped.
35. The shipped `slb-contract` sha256 recomputes to
    `9a413347f3336869c2f7c0add48b6f760d9a50ce7791c8dcc4cf0f4c287adccd`, matching
    §10a's "final (shipped)" row; `forbidden_hits` 0 and
    `required_pins_nothing` 0 in the gate record; the anti-collapse verdict line
    quoted in §3 reproduces verbatim.

---

## What I did not do

- I did not pin down **why** `adversarial-oob` varies with ASLR disabled (m3).
  I established that the stated cause does not explain it; I did not find the
  one that does.
- I did not identify the compiler transform behind the `nw mod 8` step or the
  `rlen` parity step in `R2 − R4` (M1). Both are exact and reproducible over
  103 measured points; the shapes are consistent with an unroll-by-8 decode loop
  and a fold trip count of `2·rlen mod 4`, but I did not read the vector
  epilogue to confirm, and the finding does not rest on it.
- I did not build `r4_slice`'s Verus twin (out of scope: reviewers do not fix,
  and it needs two new trusted items).
- I did not re-run `harness/check.py` for any pattern other than p38.
- I did not attack `c_memcpy` / `c_union` beyond re-deriving their digests, nor
  the `harm*.c` §0 probe ladder beyond the two negatives that bear on M3
  (two-pass and the byte-buffer direction).
