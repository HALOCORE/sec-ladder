# TASK_123 — the enumeration nobody has run: 20 worked CVEs against the reviewed bar

**Role: research engineer. Deliverable: a TRIAGE.** No pattern built, no
catalogue row written. Nothing under `patterns/`, `.memory/`, `RECAP.md`,
`results/`, `synthesis/`, `harness/` or `pilot/` was touched; `git status` shows
52 modified files and **all 52 are `TASK_119`'s** (`harness/`, `results/`,
`synthesis/`). `../LearnVeri/` was read only — every kernel here is a copy under
`.temp/t123/`.

---

## HEADLINE

> ### **1 candidate survives. `CVE-2021-23017`. The other 19 die, each on a `grep`, a run, or a load-bearing citation.**

And the divergence the task was written to settle is settled **against the
manager**: the manager's census mapped `CVE-2021-23017` onto `p12-strcat-fixed`;
that mapping is **refuted by a mechanical test over all 26 built kernels**, whose
must-fire arm fires. The manager had flagged the mapping itself as *"the weakest
part of this file… listed so that somebody can attack it."*

**The second-order result is at least as important, and it is a clean negative:**
the domain **does** look largely worked out — 19 of 20 die, and the two big
families (logical 7, temporal 8) die for structural reasons that will recur — but
*"largely"* is not *"entirely"*, and the one row that survives survives on a
measurement rather than on a reading.

---

## §A — the logical seven. PROBE 1 RUN, NOT ASSUMED. ALL SEVEN DIE.

Probed `CVE-2021-3450` (the `ret` clobber) and `CVE-2023-0465` (the policy loop
that starts at index 1), each at C-gcc / C-clang / safe-naive / safe-tuned /
unsafe. Generator: `.temp/t123/A/build.sh`.

### A1 — behaviour matrix (`.temp/t123/A/matrix.sh`)

The bug fires **identically at all five arms** and the fix works **identically at
all five arms**:

```
logical    rs-naive  attack   R=1 err=1 depth=1   rc=0
logical    rs-tuned  attack   R=1 err=1 depth=1   rc=0
logical    rs-unsafe attack   R=1 err=1 depth=1   rc=0
logical    c_gcc     attack   R=1 err=1 depth=1   rc=0
logical    c_clang   attack   R=1 err=1 depth=1   rc=0
```

(`R=1` = the forged non-CA chain authenticates, with the CA failure recorded in
`err=1` and then ignored — the CVE.) Guarding the strict branch with `ret > 0`
gives `R=0` at every arm, C and Rust alike. `CVE-2023-0465` behaves the same way:
`R=1` at every rung with the leaf's policy malformed, `R=0` at every rung once
the loop starts at 0.

**MUST-FIRE ARM — a gathered sum `buf[idx[i]]` with an index off the end.** It
fires, and it separates and prices the rungs:

```
control  rs-naive  attack   rc=134   "index out of bounds: the len is 64 but the index is 100"
control  rs-tuned  attack   rc=134
control  rs-unsafe attack   rc=0     R=2481614971
control  c_gcc     attack   rc=0     R=2481615210
control  c_clang   attack   rc=0     R=2481614956

CONTROL R2 naive   175.00 Ir/call     CONTROL R4 unsafe  131.00 Ir/call    -> +44.00
```

So the instrument can see a rung boundary and can charge for one. It sees neither
on the CVE.

### A2 — the ISOLATION, and it is the decisive measurement

The **full** kernels do separate — `k_logical_naive` 959 B, `_tuned` 1036 B,
`_unsafe` 237 B, three distinct md5s — **but that separation is `chain.certs[i]`,
an incidental `index >= len`,** which twelve-plus built patterns already carry.
Remove the array index and run the DECISION alone (`.temp/t123/A/dec.{c,rs}`):

```
dec_rs   k_dec_naive    size=108  md5=2a7cb02dabc6005b2bbd8004cc2140a8
dec_rs   k_dec_tuned    size=108  md5=2a7cb02dabc6005b2bbd8004cc2140a8   <- IDENTICAL
dec_rs   k_dec_unsafe   size=108  md5=2a7cb02dabc6005b2bbd8004cc2140a8   <- IDENTICAL
dec_rs   k_dec_fixed    size= 96  md5=a357c4037024109467a659435565b0c3   <- must-fire arm, DIFFERS

3450dec R2 naive    37.00000 Ir/call
3450dec R3 tuned    37.00000 Ir/call
3450dec R4 unsafe   37.00000 Ir/call
3450dec R  fixed    18.00000 Ir/call   <- the arm that must differ, differs
```

**`R3 − R4 = 0.00` AND PROBE 2 COLLIDES.** By the catalogue's own surviving line
— *"a zero because two rungs compiled to the same bytes is an ARTEFACT"* — this
is an artefact, not a finding. It is `p45`'s and `p44`'s death exactly: **there
is one rung.** ⚠ Note what I did **not** use: I did not refuse anything on
*"the ladder has nothing to price"* (finding 41, dead). The kill is probe 1 plus
byte-identical machine code.

### A3 — the argument that retires the other five

All 20 corpus ports are `#![forbid(unsafe_code)]` and
`grep -rn '\bunsafe\b' */rust/src/` over the whole corpus returns **0**. For the
logical seven that is structural: the "check" whose absence is the bug is a
**policy predicate the programmer writes**, not a bound the compiler inserts — so
R4 has nothing to elide and R3 has nothing to pay. Each unprobed one is strictly
simpler than one I probed: `CVE-2022-1343` and `CVE-2026-31790` are
`CVE-2021-3450`'s `ret`-clobber verbatim; `CVE-2015-1793` is a counter,
`CVE-2019-20372` a cursor update, `CVE-2016-4449` / `CVE-2017-7375` missing
boolean guards. And each root-cause doc's own §6 *"When would Rust prevent
this?"* answers **"It would not"** — seven for seven, e.g. `CVE-2015-1793`:
*"every index used is in bounds, every value initialized."*

---

## §B — the temporal eight. CLOSED ON A CITATION, AND THE CITATION IS LOAD-BEARING.

Confirmed verbatim in three places; **no measurement spent**, as instructed.

1. `patterns/p27-handle-table/verus.rs:511-514` (on `rec_free`) and `:589-594`
   (on `rec_close`): *"A freelist push into a slab would consume nothing, the
   stale read would be in bounds of a live allocation, and the bug would be
   p17's LOGICAL class instead of this one."*
2. `.tasks/TASK_055_REPORT.md` §2.8 caveat 1: *"If the slab is one allocation and
   'free' is a freelist push, the stale read is in bounds of a live allocation.
   Miri does not flag it, `PointsTo` licenses it, and the bug is logical, not a
   lifetime bug — the same class as p17, which the tree already has."*
3. `.memory/06-catalogue.md`'s `p33` cell carries the **measurement** of that
   shape: *"use-after-recycle reads the recycled node's value … a slot
   double-free yields two ALIASED handles, both silently wrong and Miri-clean
   (0 UB in all three modes), manager-re-run"*, and *"PROBE 1 KILLS BOTH
   INDEPENDENTLY: the bug compiles identically at C, safe naive, safe tuned and
   unsafe."*

The corpus's own tracker ports **every one of the eight** as a *generational
index into a `Vec`/arena with slot reuse* — exactly the freelist-into-a-slab
shape those three kill. So the citation decides the row: **load-bearing.**

> ⚠ **CORRECTION OWED TO `TASK_123.md` AND TO `.temp/mgr121/NOTES.md` — the same
> misquote in both.** Both say `TASK_055` §2.8 *"records that the manager offered
> the `(slot, gen)` formulation and the engineer REJECTED it."* **It does not.**
> §2.8's own recommended shape **uses** `(slot, gen)` — *"the handle is a POINTER
> at R4/R5 and a `(slot, generation)` pair at R1h/R2/R3"*, and *"R2/R3 (safe
> Rust) cannot hold the pointer at all, so the `(slot, gen)` representation is
> FORCED."* What §2.8 rejects is `(slot, gen)` **as the R4/R5 representation**:
> *"Only a real `deallocate` makes it the missing class."* **The verdict is
> unaffected; the reason is wrong in two files.**

---

## §C — the spatial five, and the candidate. NOVELTY CLAIM RUN BEFORE ANYTHING WAS WRITTEN DOWN.

### C0 — `TASK_123`'s own §C premise is false, and I checked it first

*"`p16` (TLV walk) and `p14` (field split) are the two most likeliest to already
do this."* **Neither does.** `p16` is a **single-pass** walk whose bound is the
attacker's `vlen` field (`patterns/p16-tlv-walk/c/kernel.c`, one `while` over the
window). `p14` **counts delimiters and appends descriptors in the same pass**
(`while (i <= m)`), bounded by `#define MAXTOK`.

### C1 — the mechanical test the standing rule demands (`.temp/t123/C/bound_census.py`)

It walks every built `patterns/*/c/kernel.c` and classifies every destination
buffer's size expression as FIXED (`#define`/literal), INPUT EXTENT (a
parameter), or **PRIOR-PASS COUNT** (a variable accumulated inside a loop):

```
p03 stack[STACK_CAP]   p04 ring[RING_CAP]   p06 scr[SCR]   p08 scr[P08_SCR]
p12 dst[DST_CAP]       p13 dst[DST_CAP]     p14 scr[SCR] + tl[MAXTOK]
p22 tab[SLB_P22_TABCAP]  p23 scr[SCR]  p27 live[TABCAP] + q[RECSZ]
p38 sc[SLB_P38_SCRATCH_W]   p42 dig = malloc(len)   p46 out[..OUTCAP] + bl[..BCAP]

BUILT TREE: destination buffers sized by a PRIOR-PASS COUNT = 0

=== MUST-FIRE ARM: the candidate's own kernel ===
  dst   size=(size_t)len   PRIOR-PASS COUNT (`(size_t)len`; `len` accumulated in a loop)
CANDIDATE: prior-pass-count buffers = 1   ARM FIRED (scanner works)
```

**Fourteen destination buffers across twelve built patterns: thirteen are
`#define` fixed capacities, one is the input extent (`p42`'s `malloc(len)`), and
ZERO is a count a prior pass accumulated.**

⚠ **Scanner blind spot, disclosed:** it reads declarations and `malloc`s inside
the kernel TU and does **not** see a caller-supplied buffer passed as a
parameter. That is exactly `p02` — `kernel(…, uint8_t *dst, size_t dst_cap)` —
which I checked by hand: an INPUT EXTENT, and the bound the bug violates is
`len`, an attacker field read from the wire. Still not a prior-pass count.

⚠ **The first draft of this scanner was wrong in the dangerous direction** (`^`
without `re.M` → *"no destination buffer"* for every pattern → the right answer
`0` for the wrong reason). The must-fire arm is what exposed it. Recorded here
rather than quietly fixed, because that is what `.memory/03-measurement.md`'s
seven-entry failure-class list is for.

### C2 — probe 1 on the candidate. It survives, and the matrix is four-way.

Kernel copied from `../LearnVeri/microbench/CVE-2021-23017/lib.c`
(`name_decoded_size` + `name_decode_into`), stripped of the cache
(`.temp/t123/C/d.c`, `d.rs`; `REBUILD.sh` regenerates everything).
Attack packet = a label immediately followed by a compression pointer.

| rung | attack input | detector |
|---|---|---|
| **R1 C gcc/clang** | `reserved=4 produced=5 over=1` | **ASan `heap-buffer-overflow`, `WRITE of size 1`, at `k_decode`** |
| **R1h C** (the nginx fix, `len += 1` in pass 1) | `reserved=5 produced=5 over=0` | ASan silent — must-NOT-fire arm |
| **R2 safe naive** (`vec![0;len]` + `dst[o]`) | **PANIC**, rc `134`, *"index out of bounds: the len is 4 but the index is 4"* | rustc bounds check; Miri agrees |
| **R3 safe tuned** (`Vec::with_capacity` + `push`) | **NO HARM — output equals the FIXED C's** (`acc=5757583`) | Miri clean |
| **R4 unsafe** (`get_unchecked_mut`) | **SILENT 1-byte OOB write — output equals the BUGGY C's** (`acc=185727`) | **Miri: UB**, *"slice::get_unchecked_mut requires that the index is within the slice"* |
| all rungs, **benign** packet | `reserved=8 produced=8 over=0`, identical everywhere | silent — must-NOT-fire arm |

Three independent detectors fire (ASan, the rustc bounds check, Miri); both
must-not-fire arms are silent. **So it is genuinely spatial in this shape — it is
NOT `p04`'s "stays in bounds, invisible to a memory-safety proof" class.**

### C3 — probes 2, 3, 4

- **probe 2** (linked kernels): `k_dec_naive` 602 B `a4b68f02…`, `k_dec_unsafe`
  470 B `2117abed…`, `k_dec_push` 515 B `7e36073e…`. **Three distinct. No
  collision.**
- **probe 3**: `R2 − R4 = 677.00 − 614.00 = +63.00 Ir/call` (marginal,
  differenced over two iteration counts so the setup term cancels).
  C-gcc bug `409.00` → fix `421.00`, i.e. the nginx fix costs **`+12.00 Ir/call`**.
  ⚠ **Confound disclosed:** R2/R4 use `vec![0u8; n]` (zero-filled) and R3 uses
  `Vec::with_capacity` (not filled), so R3's `590.00` is **not** comparable
  without controlling the fill. The `R2 − R4` pair *is* clean — same allocation,
  same fill, differing only in the index check.
- **probe 4**: `grep -rn "get_unchecked" ~/tools/verus/vstd/` → **0 hits**,
  re-derived at the pin, not quoted. The R4 op needs an `external_body` wrapper
  like every other pattern; **no `p15` blocker.**

### C4 — what I am NOT claiming. Attack these.

- **Only limb 2 is met, and it is measured.** Limb 1 is not (the operator is an
  ordinary store through a bumped cursor). **Limb 3 is NOT established** — the
  interesting sentence, *safe Rust's idiomatic escape is `Vec::push`, which
  deletes the bound rather than checking it*, is a phenomenon with no isolation,
  and finding 37's companion rule says **a limb claiming a new REASON owes an
  isolation, not just a measurement**.
- **Do not overclaim the safety line.** The fix is a *counting* correction, not a
  bound check — but it is still a compare (`(pkt[p] & 0xC0) == 0xC0`), against
  the **input** rather than the buffer. And `p13`'s hardened line is already a
  **store** (`dst[DST_CAP-1] = 0`) rather than a compare, so *"the safety line is
  not a comparison"* is not new either.
- ⚠⚠ **The row has TWO shapes and only one is buildable as a spatial row.** With
  a per-name allocation the write leaves the allocation (what I measured). With
  the **shared arena** the corpus's own Rust port uses, the write stays in bounds
  and corrupts the neighbouring `naddrs` field — **that shape IS `p04`'s class**
  and would die. **The buildable shape is chosen by the engineer, not by the
  CVE.** This is the strongest single objection to the candidate.
- **The proof would duplicate `p22` on the termination axis**: the corpus's Verus
  proof carries a `fuel` budget against a compression-pointer cycle, which is
  `p22`'s non-termination class. The novelty is on the **bound**, not the proof.
- **Bug-class duplication is real and is not a valid kill**: a 1-byte heap OOB
  write duplicates `p02`. The reviewed bar says bug-class novelty *"predicts
  neither way"*, and `p37` is the row that got killed for a bug-class-shaped
  reason that turned out backwards.

---

## §D — THE TABLE. 20 rows.

Legend for **limb**: which limb of the reviewed bar the row would meet
(1 new operator · 2 new source of the bound · 3 new elision reason).

| # | CVE | cat | mechanism, one line | maps to | limb | verdict | evidence |
|---|---|---|---|---|---|---|---|
| 1 | CVE-2017-7529 | spatial | range int-overflow bypasses the size guard; suffix underflow | **IS `p17`** | — | **REFUSE — already built** | citation: `.tasks/TASK_011.md:13` names this exact directory; `06-catalogue.md` p17 *"cf. CVE-2017-7529"* |
| 2 | **CVE-2021-23017** | spatial | **a SIZING pass under-counts a separator the WRITING pass emits** | **NONE** | **2** | ⚠ **SURVIVES** | RUN: `bound_census.py` (0/14 built buffers, arm fires) + four-way matrix + ASan + Miri + probe 2 + `+63.00 Ir/call` |
| 3 | CVE-2014-0160 | spatial | Heartbleed: attacker content-length > received payload | **IS `p20`** (catalogue row, DEFERRED with a measurement) | 2 fails | **REFUSE** | citation: p20 cell *"(heartbeat-style) … cf. CVE-2014-0160"*, deferred on *"a length/offset check is O(1) and does not scale"* (`+6.00`/`+7.00 Ir`) |
| 4 | CVE-2014-3508 | spatial | `OBJ_obj2txt` omits the terminating NUL; caller reads past the OID text | **IS `p13`** | 1,2,3 fail | **REFUSE — exact duplication** | citation: p13 cell *"does not terminate on truncation; the harm lands at a different site from the bug (… OOB read later in the consumer)"* — that is this CVE's sentence |
| 5 | CVE-2017-8872 | spatial | `halt()` leaves a stale over-length `fill`; the drain reads the carry | `p19` (state confusion) × `p04`/`p17`-harm-1 (in-bounds residual) | 2 fails | **REFUSE** | citation: corpus's own *"a func invalidates the pointer … the later func doesn't check the validity"* = p19; safe-Rust residual *"in-bounds logical wrong-data leak"* = p04 |
| 6 | CVE-2016-4449 | logical | external SYSTEM entity resolved with no `allow_external` check | — | none | **REFUSE — probe 1** | RUN (§A2) + corpus §6 *"a missing authorization/policy check is a logic property, not a memory property"* |
| 7 | CVE-2017-7375 | logical | external param entity loaded with no `OPT_LOAD_SUBSET` check | — | none | **REFUSE — probe 1** | RUN (§A2) + corpus §6 *"a security-relevant `if` … is simply not written"* |
| 8 | CVE-2021-3450 | logical | CA-check result in `ret` clobbered by the curve check | — | none | **REFUSE — probe 1** | **RUN**: three rungs byte-identical, 108 B `2a7cb02d…`, 37.00 Ir/call each; must-fire arm differs |
| 9 | CVE-2023-0465 | logical | policy scan starts at index 1, leaf never scanned | — | none | **REFUSE — probe 1** | **RUN**: `R=1` at all 5 arms on the attack input, `R=0` at all 5 once fixed |
| 10 | CVE-2015-1793 | logical | `num_untrusted` drifts smaller; alt path never resyncs | — | none | **REFUSE — probe 1** | RUN (§A2) + corpus §6 *"every index used is in bounds, every value initialized"* |
| 11 | CVE-2022-1343 | logical | OCSP `ret` overwritten by a positive X509 error code | **row 8's shape verbatim** | none | **REFUSE — probe 1** | the row-8 measurement + corpus §6 *"no memory unsafety … no undefined behavior anywhere on the path"* |
| 12 | CVE-2019-20372 | logical | redirect emits 302, never consumes the body; cursor not advanced | — | none | **REFUSE — probe 1** | RUN (§A2) + corpus §6 *"perfectly valid, in-bounds `&[u8]` data"* |
| 13 | CVE-2024-25062 | temporal | node dropped mid-traversal, slot compacted+reused, stale cursor | `p27` / `p33` | none | **REFUSE — citation** | §B citations 1–3 |
| 14 | CVE-2016-4658 | temporal | span holds a stale slot index; reuse reads the new occupant | `p27` / `p33` | none | **REFUSE — citation** | §B 1–3 |
| 15 | CVE-2022-23308 | temporal | `deregister` fails silently; map keeps a stale slot | `p27` / `p33` | none | **REFUSE — citation** | §B 1–3 |
| 16 | CVE-2022-40304 | temporal | interned value zeroed w/o key update → double free → free-list duplicate → aliasing | `p33` | none | **REFUSE — citation + measurement** | §B 3: p33 measured *"a slot double-free yields two ALIASED handles … Miri-clean"* |
| 17 | CVE-2021-3518 | temporal | subtree released, entity-ref keeps a stale `children_idx` | `p27` / `p33` | none | **REFUSE — citation** | §B 1–3 |
| 18 | Issue-15143 | temporal | entity removed, entity-use keeps a stale `resolved_entity` | `p27` / `p33` | none | **REFUSE — citation** | §B 1–3 |
| 19 | Issue-15192 | temporal | clone copies `ns_ref` by value; source doc released | `p27` / `p33` | none | **REFUSE — citation** | §B 1–3 |
| 20 | CVE-2026-31790 | *temporal\** | KEM misses `rsa_public_encrypt`'s `-1`, reports success with a stale buffer | **row 8's shape** — the tracker's own asterisk says *"value-flow, not a real UAF"* | none | **REFUSE — probe 1, as a LOGICAL row** | the corpus's own asterisk + the row-8 measurement |

**Tally: 20 enumerated · 19 refused · 1 survives.** Corrected category mix:
**spatial 5 / logical 8 / temporal 7** (the corpus's own tally of 5/7/8 counts
`CVE-2026-31790` as temporal while flagging it as not a UAF).

---

## Where I differ from `.temp/mgr121/NOTES.md`

`census.md` was written **before** I opened the manager's file. We converge on
**18 of 20 verdicts** and on **both decisive citations**. Four differences:

1. ⚠⚠ **`CVE-2021-23017 → p12-strcat-fixed` is REFUTED.** `p12`'s destination is
   `uint8_t dst[DST_CAP]`, a `#define`, and its missing check is
   `dlen + slen <= DST_CAP` against that constant; the candidate's destination is
   sized by a count the program accumulated in a **prior pass over the same
   input**. `bound_census.py` separates them mechanically and its must-fire arm
   fires. **The manager asked to be attacked here and was right to.**
2. ⚠ **`CVE-2017-8872 → p16` is right verdict, wrong reason** (`p28`'s shape, and
   a reason is what the next row gets judged against). `p16`'s bound is an
   attacker length field on the wire; `8872`'s is a **stale cached `fill`** that
   a state transition invalidated — `p19`'s state confusion, with a `p04`-class
   in-bounds residual in safe Rust.
3. ⚠⚠ **I do not adopt *"the honest denominator is 13, not 20"* / *"about seven
   of twenty"*.** Its stated ground is *"there is no rung-to-rung difference to
   price — the ladder would be flat by construction"*, **which is finding 41's
   sentence, and finding 41 is dead.** My kills for the logical seven rest on
   probe 1 **plus probe 2's byte-identical machine code**, i.e. the ARTEFACT side
   of the line probe 3 draws and which survived. Shrinking the denominator is
   also what makes a 0-candidate outcome look inevitable, which this task was
   explicitly warned about.
4. **`CVE-2026-31790` should be counted LOGICAL**, not temporal (see §D row 20).

---

## Answering the task file's three "least sure" calls

1. ⚠⚠ **"Is this corpus the right domain at all?"** — **Partly, and the
   objection you raised is correct and should be recorded.** A CVE corpus selects
   for **exploitability and for reportability**, not for **idiom frequency**, and
   it is doubly selected here because *another* project picked these 20 for
   *provable security invariants*. Two visible consequences: (a) **8 of 20 are
   pure decision bugs with no memory dimension at all** — a distribution no C
   *idiom* census would produce; (b) **temporal bugs are 7 of 20 (35%)** while
   this benchmark has one temporal pattern, because UAF is over-represented in
   CVE feeds relative to how often the idiom appears. **So the corpus is a valid
   instrument for *"is there a mechanism the tree lacks?"* and an invalid one for
   *"what should the tree contain?"*.** ✅ **But it is the first enumeration of
   any domain this project has run, and it did produce exactly what it was
   supposed to: one mechanism the built tree provably lacks, and eighteen it
   provably has.** If the project wants the second question answered, the
   enumeration has to be over **C idioms** — and the natural corpus is
   CWE-frequency data or a `libc`/parser idiom census, not CVEs.
2. ⚠ **"Is `CVE-2021-23017` a real candidate?"** — **Yes on limb 2, measured;
   and you were right to distrust your own mapping away.** The mechanical census
   is the evidence, its must-fire arm fires, and I disclosed the one blind spot
   (`p02`'s parameter buffer) and hand-checked it. **The honest weakness is not
   the bound — it is that the row's spatial character depends on the ALLOCATION
   SHAPE the engineer picks** (§C4), and that limb 3 has no isolation.
3. ⚠⚠ **"Would a 0-candidate outcome be believed?"** — **It would have been the
   easier answer and I nearly wrote it.** Two of my own first-draft probes gave
   me a free refusal and both were **instrument defects**: a `0.00000 Ir/call`
   that came from an argv bug (`atol("f") == 0`, so both arms ran zero
   iterations), and a `bound_census.py` whose missing `re.M` printed *"0
   prior-pass counts"* over a tree it had not actually read. **Both would have
   read as confirmation of the refusal.** That is the reflex you named, caught
   twice in one task by must-fire arms.

---

## Measurement defects I hit and fixed (all three are the failure list's class)

The list at `.memory/03-measurement.md`'s *"THE CONTROLS THAT COULD NOT HAVE
FIRED"* is numbered 1–8 with entry 5 struck — **seven live entries, derived here,
not quoted.** Mine:

1. **A `0.00000 Ir/call` from an argv bug.** `./c_gcc logical attack f <N>` put
   the fixed-arm flag where the iteration count is read; `atol("f") == 0`, so
   both arms ran **zero iterations** at identical whole-program totals.
2. **Per-iteration `match rung.as_str()` dispatch contaminated every Rust arm.**
   The string compare's cost depends on the arm's **position in the match**, so
   byte-identical kernels read `43 / 50 / 37 Ir/call`. Hoisted to a function
   pointer + `black_box`; they then read `37 / 37 / 37`, which is what a
   byte-identical md5 requires. **This changed the sign of the `3450`
   safe-vs-unsafe delta.** Same family as the `println!` name-length trap.
3. **C loop-hoisting.** `ok = k0465_bug(&c)` in a pure loop was hoisted out
   entirely (`n1 == n2` exactly). Fixed with a per-iteration
   `asm volatile("" :: "r"(&c) : "memory")`, identical in every arm.

---

## Problems / not done

- **No Verus run at all.** The corpus ships the proofs and this is a triage.
  So the candidate's R5 feasibility rests on the corpus's `cargo verus verify`,
  which this project cannot reproduce (single-file mode only, never `--cargo`).
  **That is an unrun risk on the candidate, not a measured one.**
- **No wall clock anywhere** — `TASK_119` owns the tree, so `Ir` only. I did not
  run `harness/check.py`, `build.py` or `measure.py`, and I quoted no number from
  `results/`, `synthesis/` or `harness/`.
- **Limb 3 of the candidate has no isolation and is therefore not claimed.**
- `CVE-2014-0160` has no `root-cause.md` in the corpus; I mapped it from the
  tracker line and from `06-catalogue.md`'s `p20` cell, which names it.
- I probed **2 of 7** logical CVEs directly; the other five rest on the stated
  argument plus their own §6 texts. If one is to be spot-checked, make it
  `CVE-2019-20372` — the cursor-advance shape is the only one of the five with a
  cursor, and `p23` is the tree's two-moving-cursor row.
- **Two files carry the `TASK_055` §2.8 misquote** (`.tasks/TASK_123.md`,
  `.temp/mgr121/NOTES.md`). Manager's to fix; I do not edit either.

## Recommendation (a scoping, not a decision)

1. **Land the enumeration itself as the result.** *"20 CVEs enumerated, 19 die
   with a citation or a run, 1 survives"* is the argument the manager asked for
   at `TASK_113` and has now got. It is the first time the domain has been
   enumerated at all.
2. **`CVE-2021-23017` is a candidate for a task file, not for a row.** Anyone who
   writes that task must first settle §C4's objection: **the allocation shape
   decides whether the row is spatial (`p02`'s class, buildable) or in-bounds
   (`p04`'s class, dead)**, and that choice is the engineer's, not the CVE's.
3. **The generalisation to publish, if any, is not about the refusal set.** It is
   about the corpus: **a CVE distribution answers *"which mechanisms are
   missing?"* and does not answer *"which idioms matter?"*.** The bar can be
   argued from the first; `TASK_113`'s request was for the second, and this
   corpus cannot supply it.

---

**PROTOCOL rule 2 running count: launched from 520, carried to 526** (branch
delta **+6**: the `TASK_055` §2.8 misquote in two files · the `p12` mapping ·
the `p16` mapping's reason · the `CVE-2026-31790` category · `TASK_123` §C's
`p16`/`p14` premise · my own two-then-three instrument defects). ⚠ **A rigour
signal, not a ledger — reconciliation across concurrent branches is the
manager's job, not mine.**

Evidence: `.temp/t123/NOTES.md`, `.temp/t123/census.md`,
`.temp/t123/A/build.sh` (+ `matrix.sh`, `ir.py`, `kmd5.py`),
`.temp/t123/C/REBUILD.sh` (+ `bound_census.py`). Binaries deleted; every one is
re-derived by the two generator scripts.
