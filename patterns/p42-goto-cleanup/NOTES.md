# p42-goto-cleanup — working notes

## 0. Rule 6 disclosure (`.tasks/PROTOCOL.md`)

`slb-contract` block sha256 **as first written, before any measurement**:

```
50697e33b2971fc4c965a710fc1d6fad19000d81ecb7744fa8ddc07471e9fb8d
```

**As TASK_104 shipped it**, after the three edits below:

```
4a252569067081a55c55c8e6177bc8f6a4f897a57cd59a00c7c000a3da8d29a4
```

**As TASK_110 shipped it**, after its edits 4-9:

```
437ae31512cf250acac91e64e289b8cd200dfd83b78797aa3467945b86718d76
```

**As shipped now**, after TASK_118's retraction:

```
1af5c4568295ebb2547069e714df5205ca2fcbf8b3e7f289f792b1e1b8a997fe
```

⚠ **TASK_118 moved it ONCE, and everything that moved it is a RETRACTION or a
correction — nothing was strengthened, nothing was added, and no measured
number depends on any of it.** Five fields inside the fence changed:

| field | what moved |
|---|---|
| `idiom.why` | the TASK_110 clause claiming the ghost ledger states leak-freedom is **withdrawn in full**; the sentence TASK_110 struck is **not restored** (section 6) |
| `identity[0].why` | same withdrawal in its closing sentence, plus what the pin **did** do — it catches every planted leak at both levels |
| `verus.twin_obligations_note` | *"the GHOST LEDGER that states leak-freedom"* → *"the GHOST LEDGER, WHICH DOES NOT STATE LEAK-FREEDOM"* |
| `miri.reason` | ⚠ **the TASK_110 amendment is REVERSED and the struck sentence RESTORED VERBATIM** — *"Verus does NOT prove that `dig_free` is reached on every path"* — re-derived at TASK_118 rather than taken from the review |
| `miri.blocked_reason` | the OWED item from TASK_107 and TASK_114: `check.py` now **removes** an ambient `MIRIFLAGS` and records it, and the seed-dependence premise does not reproduce |

⚠⚠ **`miri.reason` is the one to read twice. A TRUE sentence was struck inside
this hashed block at TASK_110 and replaced with a FALSE one** — `PROTOCOL.md`
rule 9's `TASK_099` shape, second occurrence, and the first time inside a hash.
✅ **The hash matching is evidence about WHEN a sentence was written, not about
whether it is true**, and this is the pattern that demonstrates it: TASK_110's
`437ae315…` verified perfectly for eight tasks while carrying two false claims.

⚠ **What did NOT move:** every `requires`, every `ensures`, `obligations` (18),
`twin_obligations` (21), `axioms` (0), `identity`'s levels, `driver`,
`collapse`, and every `required`/`forbidden` entry. **The measured numbers are
untouched by this task** — it retracts prose about what a measurement means,
not a measurement.

⚠ **The hash moved TWICE inside TASK_110, and the second move is disclosed
rather than smoothed over.** Edits 4-8 took it to
`2be2bf3f04df0d95890cb59c85c78edc4b98082f5efaecb64a9cffb94438dd6c`, and that
value was gate-green with 0 failures. **Edit 9 then landed on top of it**,
because re-deriving TASK_109 A1's attribute count for `idiom.why` gave **22**
where the review had written 23 (section 6d) — a wrong number inside the hashed
block is worse than a second hash move, and this pattern has now been corrected
twice for exactly that class of thing.

⚠ **AND THERE WAS A THIRD MEASURE AND A THIRD GATE, WHICH MOVED NO HASH IN THIS
SECTION AND IS DISCLOSED ANYWAY.** A final sweep of the rung sources against the
measured numbers — `.tasks/PROTOCOL.md` rule 6's added step — found two more
stale comments, both in **measurement-hashed** files and neither inside the
fence: trusted item 2's *"still gave `15 verified, 0 errors`"* (a TASK_104-era
base count that now reads as current), and `unsafe.rs`'s SAFETY (3) and (4),
which described the fold as an index after the do-while replaced it.
`contract_sha256` did not move; `source_sha256` did, and the record was
regenerated. ⚠ **The transferable part: there is NO comment-only escape in a
rung source (`measure.py::measurement_sources` globs `pdir/*.rs`), so the sweep
belongs BEFORE the first measurement. TASK_110 paid for it twice.**

⚠ **The hash MOVED TWICE BEFORE TASK_104 SHIPPED, and here is exactly what moved
it. All three edits are the gate's own findings, none weakens anything, and the
intermediate value was
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

### ⚠⚠ TASK_110's edits, 4-9, and they MOVE the hash to `437ae31512cf`

**All six are corrections, five of them TASK_109's findings and the sixth a
correction to TASK_109 itself. Every one either STRENGTHENS a pin or retracts a
false claim. None weakens anything.**

4. **`verus.obligations` 15 → 18 and `twin_obligations` 18 → 21**, with three
   items added to the item set: `led_alloc`, `led_free`, `kbody` — the ghost
   ledger (section 6b). ⚠ **A pin going UP is the direction
   `.memory/01-ladder.md`'s direction test permits**; the three items are pinned
   with every clause, `kbody`'s ledger-emptiness `ensures` included, because
   deleting that clause costs nothing any count would notice (section 6c).
   ⚠ **TASK_118: that clause was called the *leak-freedom* `ensures` here and is
   not one** — section 6. The pin still earns its line for the reason given.
5. **`required[1]` and `required[2]` gained BACKTICKS, and `required[3]` gained
   one on the C side.** TASK_109 M3: the two per-language entries carried no
   backticks at all, so `check.py::_TICK` yielded **zero** spellings from them —
   *the idiom this pattern is named for was pinned by nothing* — and
   `required[3]`'s `dig[len-1]` matched **0 of 6** rungs. Measured before and
   after, by driving the real `check.py::idiom_audit`:

   | | before | after |
   |---|---|---|
   | backticked spellings | 16 | **18** |
   | (spelling, rung) pairs | 52 | **56** |
   | **pairs PRESENT** | **7** | **17** |
   | `required_pins_nothing` | 7 | **5** — and all five are now the correct C-side scoping of a Rust-only entry |

   ⚠ **This is a STRENGTHENING and it is measured as one**: `goto cleanup` now
   pins both C rungs, `(uint8_t)(run >> 24)` / `(run >> 24) as u8` pins all six,
   and `dig[len - 1 - i]` pins both C rungs. The Rust half of `required[3]`
   quotes no spelling deliberately — the four Rust rungs spell the backwards
   fold four different ways and a per-language key cannot name a rung — and the
   entry says so and names what enforces it instead, exactly as
   `forbidden[0..3]` do. ⚠ **A trap worth recording: the first draft of these
   entries put file names and the retracted span in backticks inside the
   explanatory prose, and the audit dutifully pinned all of them** — 27
   spellings, 11 pinning nothing. **Every backtick in an entry is a pin.**
6. **`idiom.why`'s *"WHAT THIS DECLARATION DOES NOT CLAIM"* clause is RETRACTED
   and replaced** (section 6). The shared NAMED-SPELLING STANDARD paragraph is
   **untouched** — `check.py::named_spelling_problem` returns `None`, so its
   sha256 still matches the constant in all patterns.
7. **`identity[0].why`'s closing sentence is RETRACTED** (it said Verus cannot
   state leak-freedom) and its `O3` instruction counts are **re-measured**.
   ⚠⚠ **THE REPLACEMENT IS ITSELF RETRACTED AT TASK_118 and the original is
   NOT restored — expressibility is OPEN (section 6).** The counts stand:
   `127` against `128`, in `%r9`, where the pre-TASK_110 fold gave `120` against
   `122` in `%r8` (section 8).
8. **`miri.reason`'s *"Verus does NOT prove that `dig_free` is reached on every
   path"* is amended** — it does, on R5. Miri's role on R4 is unchanged and the
   `required: true` flag does not move.
9. ⚠ **`idiom.why`'s attribute count 23 → 22**, and this one is a correction to
   TASK_109 rather than to TASK_104: the review's clean negative (section 6d)
   quoted *"23 `verifier::` attributes"*, and
   `strings … | grep -oE 'verifier::[a-z_0-9]+' | sort -u` returns **22**. The
   negative itself is unaffected — none of the 22 is a linear mode — but a
   published count belongs to whoever re-runs it. **This edit landed AFTER the
   first `measure.py`/`check.py` pass**, which cost a second re-measure and a
   second gate run; both were re-run and the disclosure above says so.

⚠ **The `git show HEAD:… | diff -` command PROTOCOL rule 6 quotes was VACUOUS on
this pattern when it landed** — p42 landed in one commit, so on a clean tree it
always printed nothing and always looked like it passed. ✅ **It is NOT vacuous
any more, and it is the check to run from here on**, because p42 now has a
shipped commit to diff against:

```
git show 096d870:patterns/p42-goto-cleanup/spec.md | diff - patterns/p42-goto-cleanup/spec.md
```

`096d870` is the commit p42 landed in. Before TASK_110 that diff was empty. It
is now **eleven hunks**, and here is every one of them, so that a reviewer can
read the disclosure instead of re-deriving it:

| hunk (old line) | what | inside the fence? |
|---|---|---|
| 13, 21 | the `0.00`-on-the-success-path prose now names gcc, and the three-results table's middle row names the clang parity effect | no |
| 63 | *"three things … are pinned in the block below"* → the table that says which of the three is pinned by a spelling and which is prose (TASK_109 M3) | no |
| 147 | one row added to the pin table, for `kbody`'s ledger-emptiness `ensures` (called the *leak-freedom* one until TASK_118) | no |
| 161, 162, 163 | **edit 5** — the three `required` entries | **yes** |
| 176 | **edits 6 and 9** — `idiom.why`'s retraction, and the 23 → 22 attribute recount inside it | **yes** |
| 190, 191, 192 | **edit 4** — `obligations`, `twin_obligations` and its note | **yes** |
| 248, 251 | **edit 4** — `led_alloc`, `led_free`, `kbody` added to `verus.items` | **yes** |
| 294 | **edit 7** — `identity[0].why` | **yes** |
| 301 | **edit 8** — `miri.reason` | **yes** |

**Four** of the eleven hunks (old lines 13, 14, 21, 63, 147 — the first table row
covers three of them) are prose **above** the fence and therefore move the gate's
`source_sha256` and not `contract_sha256`; the other **seven** are inside it and
are what `4a252569…` → `2be2bf3f…` is made of.

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

`controls/leak.sh` is the evidence and it is **352 points, not one**: 2 kernels ×
4 optimisation levels × **44 inputs**, at the gate's own stage-7 flag string
except for `-O`, which it sweeps.

⚠ **CORRECTED AT TASK_110, from TASK_109 C5. The number used to read `88`
here, in the script's header comment, in the script's own success message and
in `README.md`, and 88 was never right for any input set.** The glob is
`"$PDIR"/inputs/*.bin`, which takes the 32 `sweep-w*.bin` as well as the 12
matrix inputs: `2 × 4 × 44 = 352`. Excluding the sweeps it would be `2 × 4 × 12
= 96`. The review ran the byte-identical shipped script and counted **352 rows**
while it printed *"ALL 88 POINTS"*. ✅ **The count is now DERIVED from the loop
that prints the rows, so it cannot go stale again.**

✅ **THE TEETH WERE NEVER IN QUESTION AND WERE RE-MEASURED AT TASK_110, both
arms, on a scratch replica so that no repo file was touched**
(`.temp/t110/leakteeth.sh`; the copied script's md5 is checked against the
shipped one first):

```
ARM 1  unplanted                                   exit=0   352 rows, 0 flagged
ARM 2  the missing `goto cleanup` PLANTED BACK     exit=1   12 rows flagged
       -- i.e. the buggy rung made NOT to leak
```

The twelve are `kernel` × {`-O0`,`-O1`,`-O2`,`-O3`} × the three inputs that
reach the error path (`-notag`, `-mixed`, `-win1`) — **exactly the rows the
model says must leak** — and the hardened rung stays silent throughout. Verbatim
tail of arm 1, as it now reads:

```
ALL 352 POINTS AS DECLARED: the buggy rung reports a LeakSanitizer leak of
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
| R1 c-clang | 1506.00 | 61487.00 | 15.526 | 15.011 |
| R1h c-clang-h | 1510.00 | 61492.00 | 15.567 | 15.013 |
| R2 safe_naive | 1850.00 | 75826.00 | 19.072 | 18.512 |
| R3 safe_tuned | 1263.00 | 50745.00 | 13.021 | 12.389 |
| R4 unsafe | **1251.00** | **50734.00** | 12.897 | 12.386 |
| R5 verus | **1251.00** | **50734.00** | 12.897 | 12.386 |

⚠⚠ **THE R4/R5 ROWS MOVED AT TASK_110 AND THE BOLD MOVED WITH THEM.** They read
`1461.00 / 59441.00` while the fold loop was an index loop; the shipped R4 is
now a do-while over a descending cursor, which is one induction variable instead
of two. **The cheapest rung in the table is no longer `safe_tuned`.** Section 9
has the search that found it and section 11b has what survives of the claim it
refutes.

**What each difference is, and what kind of thing it is:**

| | small | large | |
|---|---|---|---|
| **R1 − R1h, gcc** | **+0.00** | **+0.00** | the leak is FREE on the success path, exactly |
| **R1 − R1h, clang** | **−4.00** | **−5.00** | ⚠ the LEAKING rung is CHEAPER; it is a PARITY effect, mechanism below |
| **R3 − R4** | **+12.00** | **+11.00** | ⚠⚠ **the sign FLIPPED at TASK_110**; it read `−198.00 / −8696.00` |
| R2 − R4 | +599.00 | +25092.00 | `vec![0u8; len]` + indexing against raw |
| **R5 − R4** | **+0.00** | **+0.00** | the `identity` pin's tautology, kernel-exclusive |
| R1(gcc) − R4 | +622.00 | +27120.00 | |
| R1(clang) − R4 | +255.00 | +10753.00 | same backend, and it shows |

### ⚠ R1 − R1h is `0.00` on gcc and NOT on clang, and on clang the variable is PARITY

⚠⚠ **CORRECTED AT TASK_110, from TASK_109 C2. This section used to present
`−4.00` and `−5.00` as a `small`-vs-`large` pair, i.e. as a size effect. It is
not one. The variable is the WINDOW'S PARITY, the size term is exactly zero over
a 32× range, and the shipped inputs happen to be 97 (odd) and 4096 (even) —
which is how a parity effect got read as a size effect off two points.**

Both rungs execute the same success path, so a difference there is a code-layout
effect and not work. Measured on `harness/build.py`'s own binaries, whole-program
marginal, `.temp/t110/parity.py`:

```
  window  parity        buggy     hardened    R1-R1h   parity model
      64    even      1151.44      1156.44     -5.00     -5.00 OK
      65     odd      1169.72      1173.72     -4.00     -4.00 OK
      66    even      1186.72      1191.72     -5.00     -5.00 OK
      67     odd      1200.72      1204.72     -4.00     -4.00 OK
      78    even      1366.00      1371.00     -5.00     -5.00 OK
      79     odd      1379.28      1383.28     -4.00     -4.00 OK
     512    even      7870.00      7875.00     -5.00     -5.00 OK
     513     odd      7889.72      7893.72     -4.00     -4.00 OK
     526    even      8086.00      8091.00     -5.00     -5.00 OK
     527     odd      8100.00      8104.00     -4.00     -4.00 OK
 small.bin win=   97   odd      1649.00      1653.00     -4.00 predicted -4.00 OK
 large.bin win= 4096  even     61867.00     61872.00     -5.00 predicted -5.00 OK
```

⚠ **The arm that must fire here is the SIZE arm**, and it is refutable by its own
measurement: a size term would have made the 64..79 band and the 512..527 band
disagree, and would have shown up as a miss on one of the twelve rows. It did
not, over a 32× range, and the two shipped windows are then PREDICTED from
parity alone rather than fitted.

### ⚠ FOUR terms, not one, and they are attributed by callgrind rather than read

`.temp/t110/terms.py` runs callgrind with `--dump-instr=yes` and takes the
per-instruction marginal inside the `kernel` symbol, so every `Ir` is attributed
to an address and a register rename cancels. `R1h − R1` decomposes exactly:

| term | even | odd |
|---|---|---|
| the tag test goes BRANCHLESS: `setne` + `sete` + `or` replace one `jne` and one `cmp` | **+1** | **+1** |
| one extra **alignment NOP** executed once per call (`data16 cs nopw` → `nopw` + `nopl`) | +1 | +1 |
| the fold-loop preheader's address arithmetic respelled: one `lea` becomes two `mov` and one `add` | +2 | +2 |
| the **odd-remainder guard**: `je <skip>` becomes `jne <do>; jmp <skip>`, so the extra `jmp` runs only when the remainder is ABSENT — **even windows only** | **+1** | **0** |
| **total `R1h − R1`** | **+5** | **+4** |

The merge itself is the instruction sequence TASK_104 quoted, and it is real:

```
   buggy                          hardened
   cmpb   $0xa7,(%r15,%r14,8)     cmpb   $0xa7,(%r15,%r14,8)
   jne    <kernel+0x3b>           setne  %cl
   test   %rbx,%rbx               test   %rbx,%rbx
   je     <kernel+0x33>           sete   %dl
                                  or     %cl,%dl
                                  je     <kernel+0x35>
```

⚠ **But it is worth `+1`, not `+3`**, because the two branchless instructions it
adds pay for a `jne` and a `cmp` they delete — TASK_109 C2 counted the three
`setcc`/`or` without the two they replace, and the totals agreed only because
its third term was mis-signed by the same amount. Statically, clang's hardened
kernel is **121** instructions to the buggy one's **119**; dynamically, on the
success path, the difference is the table above.

gcc merges nothing and pays nothing. **So "what the leak costs" is `0.00` on one
compiler and `−4.00`/`−5.00` on the other, the leaking rung being the CHEAPER
one, and neither number is about memory safety.** This is why the axis was
declared as a behaviour matrix in `spec.md` before anything was measured.

### ⚠ `R5 − R4 = 0.00` is convention-dependent, and the two conventions disagree

Kernel-exclusive `Ir` gives **exactly `+0.00` on both inputs**, which is the
tautology the `identity` pin forces. The **whole-program marginal** — the other
convention this project uses — gives `1407.00 / 51127.00` for R4 and
`1407.00 / 51096.00` for R5: **`0.00` on `small` and `−31.00` on `large`**, from
two binaries whose kernels are byte-identical (`md5_fn 28432cb84883` both,
`n_fn 128`). The 31 instructions are outside the kernel symbol; they are the
binary-layout term `patterns/p01-array-sum/spec.md`'s `collapse.note` documents
(p02's `0.02` from a differently-aligned destination buffer). **Quote `R5 − R4`
in the kernel-exclusive convention, or say which one you meant.**

⚠ **Re-measured at TASK_110 (`.temp/t110/wpmarg.py`), and the `−31.00` did not
move even though both rungs did** — it read `1617.00 / 59834.00` against
`1617.00 / 59803.00` on the pre-TASK_110 fold, i.e. the same 31 instructions
outside the same symbol. That is what "binary-layout term" means, and it is a
better piece of evidence for the claim than the original pair was.

---

## 6. ⚠⚠ THREE ENCODINGS, THREE VERIFYING LEAKERS. p42's R5 DOES NOT COVER ITS OWN BUG CLASS, AND WHETHER SOME ENCODING COULD IS **OPEN**.

> ⚠⚠⚠ **THIS SECTION HAS NOW BEEN RETRACTED TWICE, IN OPPOSITE DIRECTIONS, AND
> THE SECOND RETRACTION IS THE ONE THAT LANDS. TASK_118.**
>
> | task | this section's headline | status |
> |---|---|---|
> | TASK_104→109 | *"VERUS AT THE PINNED VERSION CANNOT STATE LEAK-FREEDOM"* | struck at TASK_110 |
> | TASK_110→118 | *"THE NATURAL ENCODING CANNOT STATE LEAK-FREEDOM. ESCROWING THE TOKEN CAN."* | **FALSE — struck at TASK_118** |
> | now | *three encodings admit a verifying leaker; expressibility is **OPEN*** | measured, and stated as an open question on purpose |
>
> **What killed the second headline.** `TASK_116` substituted **one line** into
> the shipped `verus.rs`, in place of the error path's `led_free`:
>
> ```rust
>         proof { let tracked _dl = led.tracked_remove(0int); }
>         return 0;
> ```
>
> `18 verified, 0 errors`. `21 verified, 0 errors` under `--cfg slb_twin`. Every
> obligation count, axiom count and `spec.md` clause pin **unmoved**. And it
> leaks **exactly `model.py::leak_bytes`** — `n_err × win_len`, the same quantity
> `controls/leak.sh` asserts against LeakSanitizer for the buggy C rung.
> `Map::tracked_remove` is **the call `led_free` itself makes**. ⚠ **Wrapping an
> affine resource in a map does not make it linear — it makes the drop take one
> more line.** `TASK_118` re-derived the whole thing independently
> (`.tasks/TASK_118_REPORT.md`) rather than take it on report.
>
> ⚠ **AND THE FIRST HEADLINE IS NOT RESTORED.** *"Verus cannot state
> leak-freedom"* is **not re-established** by any of this — only **no longer
> refuted**. Three refuted encodings are three data points, not an impossibility
> proof. **The governing sentence is that expressibility at this pin is OPEN**,
> and writing anything stronger would be the third confident false claim on this
> axis.
>
> ⚠ **The shape of the mistake is the durable part, and it is the same shape
> twice.** In 2026-08 this section published *the property is unstateable* off a
> measurement of *one encoding fails*. TASK_110 then published *escrowing states
> it* off a measurement of *this encoding rejects the two edits I tried*. **Both
> are the same generalisation error with the sign flipped.** `PROTOCOL.md` rule
> 9's refinement covers it: a conclusion and a mechanism carry different
> evidence. **An `ensures` is a claim about a formula; that it MEANS the English
> beside it is a claim about the encoding, and nothing in the gate checks it.**

`.tasks/TASK_104.md` §2 asked *"Can Verus state 'this allocation is released on
every path, including the error path'?"* and offered `p27`'s `Tracked<Dealloc>`
as a precedent. **After three attempts the answer is: not by any route tried, and
the question is open.** What ships is a ledger that costs +3 obligations, 0
trusted items and 0 instructions, and that buys **a named, greppable discipline
for a reader** rather than a guarantee from the verifier.

### 6a. What is true about the bare token, and it is what was measured

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
epilogue, not on its proof. **All of that is still true, and none of it implies
that leak-freedom is unstateable** — nor, after three failed encodings, that it
is stateable. ⚠ **p27 is untouched by any of this**: a spelling pin plus a
reader is exactly what p42 is left with too, which if anything makes the two
rungs the same kind of claim rather than different kinds.

### 6b. ⚠⚠ THE GHOST LEDGER, WHICH IS WHAT SHIPS — AND WHAT IT DOES NOT DO

⚠⚠ **THE SECOND SENTENCE OF THIS SUBSECTION READ *"A proof may drop an affine
token; it may not drop a MAP whose contents a postcondition names"* FROM
TASK_110 TO TASK_118. IT IS FALSE, TWICE OVER, AND THE REFUTATION WAS ALREADY
WRITTEN ONE PARAGRAPH BELOW IT IN 6c** (*"a tracked `Map` is as droppable as the
token inside it"* — written about deleting the *clause*, and it licenses
emptying the *map* just as much). **The price table below is accurate; the
product claim above it was not.**

**Never hold a bare `Tracked<Dealloc>`.** So `verus.rs` carries
two ordinary verified wrappers:

- `led_alloc` calls the trusted `dig_alloc` and **escrows** the returned
  `Dealloc` into a tracked `Map<int, Dealloc>` under a ghost key, handing back
  only the pointer and the `PointsToRaw`;
- `led_free` **withdraws** the token from the map and spends it on the trusted
  `dig_free`;
- `kbody` — the `#[inline(always)]` body of `kernel` — `ensures` that the map's
  domain comes back `Set::<int>::empty()`.

Verus checks a postcondition on **every** exit, so the early `return 0` on the
error path is checked too, and that path is p42's whole subject. ⚠ **What is
checked on that exit is that the LEDGER IS EMPTY, which is not the same as
"the block was freed", and the gap is one proof line wide** — section 6c's
attack table.

**The price, measured rather than argued** (⚠ **the price is right and the
PRODUCT is not** — three verification conditions bought at zero cost still buy
nothing if the property they state is weaker than the one claimed)**:**

| | shipped R5 before | shipped R5 now |
|---|---|---|
| verification | `15 verified, 0 errors` | **`18 verified, 0 errors`** |
| `--cfg slb_twin` | `18 verified, 0 errors` | **`21 verified, 0 errors`** |
| `#[verifier::external_body]` items | 5 | **5** |
| items `check.py::_is_trusted` calls trusted | 3 | **3** |
| hand-written axioms | 0 | **0** |
| kernel `n_fn` at `-O3` | 122 | 128 (the fold loop moved too, section 9) |
| `identity unsafe ≡ verus` at `-O3` | `exact` | **`exact`, `md5_raw_equal: True`** |
| pinned kernel signature, `driver.canonical` | — | **unchanged** |

**+3 obligations, 0 trusted items, 0 instructions.** The ledger is ghost and is
erased before codegen; R5's kernel is byte-identical to R4's.

⚠ **THE ONE NON-OBVIOUS STEP, so nobody rediscovers it: key the map by a ghost
`int`, NOT by the address.** `dig_alloc` promises nothing about the returned
address being absent from the ledger, so `dom.insert(a).remove(a) =~= dom` is
unprovable and the postcondition fails on **both** exits — the arms then fire
for the wrong reason and the base does not verify at all. A ghost key with
`requires !old(led).dom().contains(k)` is discharged by the caller for free.
Measured both ways at TASK_109 A2.

### 6c. `controls/ledger_leak.py` — FIVE arms since TASK_118: two deletions that FAIL and two attacks that VERIFY

An obligation nobody has seen fail is indistinguishable from a decoration —
and, it turns out, **an obligation whose failures you have seen is still not the
obligation you think it is**. The control deletes each of the two `led_free`
calls in turn, and then **replaces the error path's release with each of two
proof lines**, from the shipped `verus.rs`, by substitution. Actual output:

```
  base             18 verified,  0 errors  OK           must verify
  leak_err         17 verified,  1 errors  OK           DELETION -- must fail, naming the exit
                  Verus names the exit: return 0; [at this exit]
  leak_ok          17 verified,  1 errors  OK           DELETION -- must fail, naming the exit
                  Verus names the exit: acc [at the end of the function body]
  atk_remove_err   18 verified,  0 errors  OK           ATTACK -- must VERIFY (the hole, pinned)
  atk_assign_err   18 verified,  0 errors  OK           ATTACK -- must VERIFY (the hole, pinned)
```

**The two deletion arms are what the ledger really buys.** The failing clause is
`final(led).dom() =~= Set::<int>::empty()` in both, and Verus names the exit.

⚠⚠ **The two attack arms are what it does not.** They replace the SAME release
`leak_err` deletes — so they are p42's own bug class, not a contrived leak — and
they verify:

```rust
        proof { let tracked _dl = led.tracked_remove(0int); }   // 18 verified, 0 errors
        proof { *led = Map::<int, Dealloc>::tracked_empty(); }  // 18 verified, 0 errors
```

`Map::tracked_remove` is **the call `led_free` itself makes**. The second
discards the whole map **without mentioning the key**, which is precisely what
`spec.md`'s `idiom.why` asserted was impossible. Both leak
`model.py::leak_bytes` exactly, and both compile at `-O3` to `md5_fn
d3f1194cb10bce2057e0e1f3e28c1e21` — **byte-identical to R4 with p42's bug
planted in it.**

⚠ **They are pinned as ACCEPTANCE arms deliberately.** If a future encoding
rejects one, the control FAILS and prints *"the encoding has CHANGED … do not
just edit the expected numbers"*. **A hole that nothing measures rots back into
a claim; this one cannot.**

⚠ **The anchor asserts used to be half a tripwire** (TASK_116 MINOR 7): each
substitution asserted only its own anchor, so a tree whose *error*-path release
had already been tampered with tripped `leak_err`'s assert and sailed past
`leak_ok`'s. `check_anchors` now asserts **both** releases are present, exactly
once each, **before any arm runs**.

⚠ **AND THE OTHER DIRECTION, WHICH IS WHY THE CLAUSE IS PINNED IN `spec.md`
RATHER THAN MERELY WRITTEN.** Deleting the *clause* instead of the *release*
gives **`18 verified, 0 errors`** — the same count as the shipped file, because
a tracked `Map` is as droppable as the token inside it. **The obligation
vanishes and no number moves.** That is `spec.md`'s `verus.items[*].ensures` pin
doing the job it exists for: only a textual diff against the declaration catches
it, and `contract_sha256` is where that diff shows up. ⚠⚠ **AND THAT SENTENCE —
*"a tracked `Map` is as droppable as the token inside it"* — WAS ALREADY THE
REFUTATION OF 6b's HEADLINE, ONE PARAGRAPH BELOW IT, FROM THE DAY BOTH WERE
WRITTEN.** It was written about deleting the clause; it licenses emptying the
map just as much. **The counterexample to a pattern's central claim sat inside
the pattern for six tasks.** That is `PROTOCOL.md` rule 9's documented shape and
it is the single most useful thing in this section.

### 6d. ⚠ THE RESIDUAL TRUST — THREE ROUTES, NOT ONE — AND A CLEAN NEGATIVE

⚠⚠ **THIS SUBSECTION USED TO NAME ONE ROUTE AND CALL IT *"the honest form of the
claim"*: *p42's R5 states leak-freedom for the allocations its own wrapper
makes, and the residual trust is that nothing bypasses the wrapper.* RETRACTED
AT TASK_118 — THERE ARE THREE ROUTES AND THE MIDDLE ONE GOES THROUGH THE
WRAPPER.**

| # | route | closed by the shipped ledger? | measured |
|---|---|---|---|
| 1 | acquire outside the wrapper — `dig_alloc`, `vstd::raw_ptr::allocate` — and drop the token | ❌ no | disclosed since TASK_110 |
| 2 | acquire through `led_alloc`, then **empty the ledger without freeing** | ❌ no | 6c's two attack arms, `18 verified, 0 errors` |
| 3 | acquire through `led_alloc` **into a ledger the body mints for itself** | ❌ no | TASK_118, on the privacy-scoped encoding |

**Route 2 is the one that killed the claim**, because the disclosure implied the
guarantee *held* for allocations that do go through `led_alloc`. It does not.

**Route 3 is what killed the repair.** TASK_118 built the encoding that closes
route 2 — the map in a **private** field of a `pub tracked struct Ledger` in a
child `mod res`, plus an opaque `closed` tag the kernel must preserve — and it
works as designed: reaching into the map becomes `error[E0616]: field m of
struct res::Ledger is private`, **from rustc, not from Verus**; overwriting the
ledger fails the tag conjunct; forging a `Ledger` from outside the module is
`error: disallowed: constructor for an opaque datatype`. **And then the body
mints its own ledger and leaks anyway:**

```
mustfire_err2        18 verified, 1 errors   escrow in the ledger kbody WAS HANDED, release deleted -> REJECTED
atk_decoy_err        19 verified, 0 errors   escrow in a ledger kbody MINTS ITSELF, release deleted -> ACCEPTED
atk_decoy_err_freed  19 verified, 0 errors   the same local ledger, both paths free -> ACCEPTED, leaks 0
```

The two top rows differ in **one respect only — which ledger the block goes
into** — and `atk_decoy_err` leaks `256 / 624 / 0 / 16` bytes on
`adversarial-notag` / `adversarial-mixed` / `small` / `adversarial-win1`, which
is `model.py::leak_bytes` **exactly**, against a constant instrument floor of
1028 on all four. At `-O3` it is `md5_fn d3f1194c…`, byte-identical to R4 with
p42's bug planted; `atk_decoy_err_freed` is `28432cb8…`, byte-identical to
shipped R4. ⚠ **So the `identity` pin still catches it and the proof still does
not.**

⚠⚠ **THE GENERAL RULE, AND IT IS THE REUSABLE PART OF ALL THIS:** a
`Tracked<T>` obligation is only as strong as the smallest scope that can
construct a `T` — **and privacy fixes the CONTENTS of a ledger, not the
UNIQUENESS of the ledger.** `res::led_new()` has to be public because `kernel`
calls it, and `dig_alloc` sits at crate root beside `kbody`, so the body always
has a second place to put a block. **Nothing at this pin makes a ledger unique;
that is what a linear mode would be for, and there isn't one.**

⚠ **NOT BUILT, and recorded so nobody re-derives it:** close both routes by
moving `dig_alloc` **and** `led_new` inside `mod res` (private) and exporting a
`res::run(...)` that mints the one ledger, calls `kbody`, and drops it. Then
`kbody`'s only acquisition is `led_alloc` on the `&mut Ledger` it was handed.
**UNBUILT AND OPEN.** It moves the trusted items into a child module, which
`_is_trusted` and the twin naming both key on, and it would still prove nothing
about the *program* — only about `kbody`.

⚠⚠ **AND DO NOT WRITE THAT VERUS CANNOT STATE LEAK-FREEDOM.** Three encodings
have admitted a verifying leaker. **That is three data points and not an
impossibility proof**, and that exact sentence has already been retracted once
(section 6's table).

✅ **CLEAN NEGATIVE, so nobody re-runs the search: there is no linear
(must-consume, non-droppable) tracked mode at the pinned Verus.** TASK_109 A1's
finding, **re-derived at TASK_110** on `0.2026.08.09.92f466f`:

- `strings ~/tools/verus/rust_verify | grep -oE 'verifier::[a-z_0-9]+' | sort -u`
  → **22 distinct attribute names** (`.temp/t110/verus_attrs.txt`), none of them
  a linear / must-consume / no-drop mode. **The only one matching `linear` at all
  is `verifier::nonlinear`.** ⚠ **TASK_109 said 23 and it is 22** — the
  conclusion does not depend on the count, but the count is published, so it is
  recounted here rather than copied;
- `grep -rn affine ~/tools/verus/vstd/ -i` → **0 hits**. `grep` for a bare
  `linear` token (excluding `nonlinear*` and `lineariz*`) finds **one** hit in
  the whole of vstd, and it is the phrase *"non-linear arithmetic"* in a doc
  comment (`arithmetic/internals/general_internals.rs:14`);
- `../LearnVeri/_VERUS_DOC_/`'s *"linear ghost state"*
  (`state_machines/src/intro.md:41`) is a **name, not a drop check**.

⚠ **Read the first bullet narrowly and it is still decisive**: `strings` over a
binary is a lower bound on the attribute set, so "22" is *"22 that the binary
spells literally"* and not *"22 that exist"*. What the bullet rules out is a
linear mode among them, and the second bullet rules out any linear/affine
machinery in vstd, which is where such a mode would have to be used.

**This route genuinely does not exist**, and that is now measured rather than
"does not appear to have". The ledger is what stands in for it, and it costs
three verification conditions.

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

⚠ **THE GHOST LEDGER ADDS NOTHING TO THIS TABLE.** ⚠⚠ **That was published as
*the point of it*; after TASK_118 it is better read as the whole of it — the
ledger's PRICE is zero and so is its PRODUCT (section 6).**
`led_alloc` and `led_free` (section 6b) are ordinary verified functions: no
`external_body`, no `unsafe`, so `_is_trusted` returns `False` for both and
`_scan_unsafe_sites` finds every `unsafe` token still inside a trusted body.
Driven for real rather than argued — `check.py` imported and its own predicates
called over the shipped `verus.rs`:

```
led_alloc  fn  external=None  trusted=False
led_free   fn  external=None  trusted=False
kbody      fn  external=None  trusted=False
external_body items: 5     _is_trusted: 3        <- both UNCHANGED
_scan_unsafe_sites -> 0 failures; 5 `unsafe` tokens, all inside a trusted body
```

**Hand-written axioms: 0.** `vparse.axiom_decls(verus.rs)` returns `[]`; the
contract declares `verus.axioms = {"verus.rs": 0}` and the gate re-derives it.
p42 uses vstd's `assume_specification`s for `<*mut T>::addr` and
`<*mut T>::with_addr`, but those are vstd's, not this pattern's.

**Verus itself: `18 verified, 0 errors` shipped, `21 verified, 0 errors` under
`--cfg slb_twin`** (18 + the three twins). ⚠ **Both counts rose by 3 at
TASK_110** — they read 15 and 18 — and the three are `led_alloc`, `led_free` and
`kbody`. **The twin run was the review's own untested item** (TASK_109_REPORT,
"WHAT I DID NOT DO" 5: *"I did not test whether the ledger encoding survives
`--cfg slb_twin`"*) and it passes: the token `slb_twin` still occurs nowhere but
on the three twins' own `#[cfg]` attributes, so the two configurations differ in
nothing but the twin items.

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
control, in section 6a. **This item's contract is about the legality of a
release, never about its occurrence, and no clause of it could be strengthened
to say otherwise.**

⚠ **CORRECTED AT TASK_110, from TASK_109 m3. The sentence that used to close
this paragraph — *"That is why p42's leak claim on the Rust side rests on Miri
and not on this contract"* — is now wrong, and it was wrong in an instructive
way: the statement about `dig_free` ITSELF is still exactly right, and the
inference drawn from it was not.** Nothing this trusted item says can be
strengthened into *"the release happens"*; but a **verified wrapper over this
same item** can say it, at zero addition to the trusted text, and section 6b is
that wrapper. So the correct closing sentence is: **p42's leak claim rests on
Miri for R4 and on `kbody`'s ledger postcondition for R5, and on this contract
for neither** — which is the same thing this paragraph always said about
`dig_free`, with the false corollary removed.

**(c) Does each clause mean the same in both configurations?** As for
`dig_alloc`: vstd's own spec functions, one pinned vstd, and `slb_twin` appears
nowhere but on the twin's `#[cfg]`.

---

## 8. The `identity` pin, and the two edits it cost

`unsafe ≡ verus`, **`O0: norel`, `O3: exact`**, which is what every other
pattern in the tree pins. It took two edits to `unsafe.rs`, and **both were
found by the pin dropping, not by reading**:

⚠ **RE-MEASURED AT TASK_110 AGAINST THE SHIPPED TREE, because the fold loop
moved underneath both of them.** `.tasks/PROTOCOL.md` rule 6's added step says a
frozen declaration is evidence about *when* it was written and not about whether
it is still true, so both edits were put back one at a time and the pin watched
(`.temp/t110/idprobe.py`, three arms, **two of which must fail**):

```
  O0  base  identity=norel  n_fn R4= 104 R5= 104  want=norel   OK
  O0  P2    identity=differ n_fn R4= 106 R5= 104  want=!norel  OK -- FIRED
  O3  base  identity=exact  n_fn R4= 128 R5= 128  want=exact   OK
  O3  P1    identity=differ n_fn R4= 127 R5= 128  want=!exact  OK -- FIRED
```

**Both mechanisms reproduce; one of the two COUNTS moved and is corrected
below.**

**(1) `O3` read `differ` until `unsafe.rs` bound `q` and `b` in verus.rs's
order.** R4 first wrote `dig_write(dig_at(p, base, i), (run >> 24) as u8)` as
one expression; R5 *must* bind `q` before `run` is updated, because the
permission split that licenses the store happens between them. The two are the
same program and not the same object code — the complete difference, on the
shipped tree:

```
R4  lea    0x1(%r14),%r9            R5  lea    (%r15,%r14,8),%r9
                                        add    $0x8,%r9
    mov    -0x8(%r15,%r9,8),%r10        mov    -0x8(%r9,%rdx,8),%r10
    mov    (%r15,%r9,8),%rcx            mov    (%r9,%rdx,8),%rcx
    add    $0x2,%r9                     (absent)
    data16 cs nopw 0x0(%rax,%rax,1)     nopl   0x0(%rax)
```

LLVM strength-reduces the write loop differently: R5 keeps a byte cursor, R4
keeps an index. ⚠ **`127` against `128` — ONE instruction net, in `%r9`.** This
read *"120 vs 122 instructions … in `%r8` … two instructions"* before TASK_110,
which was correct for the index fold and is not correct for the do-while. Both
figures are recorded; only the second is a fact about the shipped tree.

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
already-optimised precompiled vstd and becomes a bare store. ✅ **`106` against
`104` re-measured EXACTLY at TASK_110, count, mechanism and disassembly alike.**

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

## 9. Both sides searched — and ⚠⚠ THE FIRST SEARCH WAS NOT DEEP ENOUGH, WHICH IS THE ROW'S SHARPEST FINDING

⚠⚠ **TASK_104 searched four spellings per side and published a comparative
headline off them. TASK_109 §B searched ONE more on the R4 side and the headline
reversed.** That is the finding, and it is worth more than the number: *an
in-contract spread is only as good as the search behind it, and the number of
spellings is not the measure of the search — whether the search reached the
SHAPE the pin permits is.* p42's first four R4 spellings were four ways of
writing a two-induction-variable fold; the fifth was a different shape.

p42 landed in the **flattering direction** — safe-tuned Rust cheaper than unsafe
Rust — which is the trap that has caught this project's patterns repeatedly, and
the trap sprang anyway. **The R4 side now carries five spellings and the R3 side
four**, all generated from a shipped rung by textual substitution in
`controls/spellings.py` so that no variant can drift from the rung it varies.
Every variant is checked to print the shipped checksum before it is measured.
Numbers in section 11b.

### 9a. Which R4 spellings are admissible, and why the refusals are refusals

`.memory/01-ladder.md`'s "R4 is chained to the prover": R4 must have a
byte-identical R5 twin that Verus verifies.

| spelling | admissible? | why |
|---|---|---|
| **`r4_ship`** — do-while over a descending cursor | ✅ **SHIPPED**, `18 verified, 0 errors`, identity `exact` | `with_addr`, `addr`, `ptr_ref` and `<*mut T as PartialEq>::eq`, all four specified at the pin (`~/tools/verus/vstd/raw_ptr.rs`, `pointer_specs!`) |
| `r4_idxfold` — the fold by reverse INDEX | ✅ yes — **it was the shipped rung until TASK_110** and verified 15/0 | same operations |
| `r4_add` — `p.add(i)` | ❌ | the pinned vstd specifies `<*mut T>::addr` and `<*mut T>::with_addr` and **not** `<*mut T>::add` or `offset` (`grep -n assume_specification ~/tools/verus/vstd/raw_ptr.rs` — two pointer-method entries, both in `pointer_specs!`) |
| `r4_movptr` — cursor plus counter, `w.add(1)`/`q.sub(1)` | ❌ | same |
| `r4_endptr` — cursor against an END pointer | ❌ **and this answer is NEW** | below |

⚠⚠ **`r4_endptr` was p42's disclosed open question — *"admissible in principle,
R5 unbuilt"* — and TASK_109 B2 answered it: it is INADMISSIBLE, for a reason
nobody had identified.** It uses only specified operations, so the refusal is
not about the operation set at all. It needs the **one-past-the-end pointer**
`dig_at(p, base, len)`, whose `requires` is `base + i <= usize::MAX`; and
`vstd::raw_ptr::allocate` ensures only `addr + size <= usize::MAX + 1` (`grep -n
'usize::MAX' ~/tools/verus/vstd/raw_ptr.rs` → **one hit, that one**), while
`PointsToRaw::is_range` carries no address bound. So the pointer is **not
computable in verified exec code**, and building it would cost a *strengthened*
trusted `ensures` on `dig_alloc` — which this pattern's own trusted argument
forbids (*"Every difference from vstd is a WEAKENING or a respelling, never a
strengthening"*, section 7) and which is exactly what disqualified p16's
`r4_hdr`. The probe carried a control that verifies, so it was not vacuous:
`dig_at(p, base, len - 1)` verifies and `dig_at(p, base, len)` does not, in the
same file, `3 verified, 1 errors`.

✅ **The shipped do-while exists precisely because it never forms that pointer**:
it starts at `len - 1` and leaves through `q == p`, so every address it computes
is inside the allocation.

**A clean negative worth keeping:** `with_addr` is **not** the pessimisation.
`r4_add` — the same rung with `p.add(i)` instead of `p.with_addr(base + i)` — is
identical to the shipped rung **to the instruction on both inputs**
(1407.00 / 51127.00, section 11b). The gap between R4 and R3 was the number of
induction variables per loop, not the addressing spelling — and closing that gap
is what moved the row.

---

## 10. Miri, and how narrowly to read the row

⚠⚠ **THIS PARAGRAPH'S PREMISE IS RETRACTED AT TASK_118 — flagged at TASK_107,
flagged again at TASK_114, and it is the same sentence `spec.md`'s
`miri.blocked_reason` carried.** It read: *"`harness/check.py` passes no
`MIRIFLAGS` and no `-Zmiri-seed`, and `.memory/00-environment.md` records that
Miri's alignment check is seed-dependent — the same source clean on seeds 0 and
2 and reporting UB on 1 and 3."*

**Both halves are stale.**

1. Since TASK_107 `check.py` does not merely fail to set `MIRIFLAGS` — it
   **removes an ambient one** and records what it did, in
   `miri.miriflags`, `miri.miriflags_removed_ambient` and `miri.miri_version`.
   ⚠ `MIRIFLAGS=""` is a **different configuration** from `MIRIFLAGS` unset:
   setting it at all costs **4.6×** on this pattern, 74 s → 340 s, past the
   180 s budget.
2. **The seed split does not reproduce.** TASK_107 measured seeds 0..11
   agreeing; TASK_114 measured that **the seed is not the variable at all** —
   the swing is an ENVIRONMENT-BLOCK effect that the mere presence of
   `MIRIFLAGS` selects, and a decoy variable with nothing to do with Miri
   reproduced it. ⚠ **THE MECHANISM IS OPEN** (TASK_119's), and the record
   cannot tell you which state a run landed in, because those three keys are
   **identical in both**.

**So a green gate row means *"no UB at Miri's default seed, in whichever
environment state this run landed in"***, and a p42 run that comes back with a
second BLOCKED Miri row is most likely that state rather than a regression.

`controls/miri_seeds.sh` sweeps **seeds 0 through 7** over every input with
`n_iters` clamped to 4 (the gate's own `MIRI_PROBE_ITERS`), and it carries a
**positive control that must fire**: the shipped `unsafe.rs` with the ERROR
PATH's `dig_free` deleted, generated by substitution so it cannot drift.
**Miri's own leak report is the only mechanical check p42 has that R4 does not
leak** — and an unexercised checker is indistinguishable from a satisfied one.
Results in section 11c.

⚠⚠ **AMENDED AT TASK_110 AND AMENDED BACK AT TASK_118.** This paragraph
originally opened *"Since Verus cannot state leak-freedom (section 6)"*;
TASK_110 struck that on the ground that R5 states it and checks it on every
exit, and **that ground is false** (section 6). **The original is not restored
either — expressibility is OPEN.** What is true, and is what this control rests
on: **Miri is load-bearing for BOTH rungs, not just R4.** The ledger is erased
before codegen, `identity` compares object code, and a leak planted in both
rungs is byte-identical and passes every pin — so Miri's leak report is the only
mechanical check either rung has. ⚠ **TASK_116 re-ran this in the gate's own
post-TASK_107 configuration and it still fires** (`rc=1`, `memory leaked:
alloc… (Rust heap, size: 32)`) with the shipped rung silent. ⚠ **And note the
hole it leaves: `miri.sources` is `["unsafe.rs"]`, so R5 is never Miri-checked
at all** — R5's leak-freedom is inferred from R4's Miri result plus the
`identity` pin, and `large.bin` is outside Miri entirely.

⚠ One trap this control fell into and climbed out of: `adversarial-shortlen.bin`
exits **5** by design, and the first version read `rc != 0` as UB, so every seed
looked like a failure. The script now reads Miri's **stderr**, which is where
`Undefined Behavior` and `memory leaked` are reported, and treats the exit code
as information only.

### 10a. ⚠⚠ AND THE GATE'S OWN RECORD SHOWS NOTHING — MEASURED, FIXED, AND THE FIX DELIBERATELY NOT LANDED HERE

**A Miri LEAK is neither `Undefined Behavior` nor `error: unsupported`**, and
until TASK_118 those two strings were the whole of `check.py`'s `ub` key. So a
leaking rung was recorded with **`ub: False`** and caught only by the next
branch, on the exit code, with the message *"miri exited 1, model expects 0"*.
**The verdict was right; the record was blind** — and a reader auditing
`results/gate/*.json` by the key they would search saw nothing, on the one
pattern in the tree whose entire subject is a leak (TASK_116 MINOR 6).

**The fix is written, tested and HELD.** It records **`leak`** on every Miri row,
unconditionally, with its own failure branch above the exit-code branch, plus a
regression control in the shape `p18-varint-shift/controls/miri_exit_hole.py`
established. ⚠⚠ **It is NOT landed in this task, and the reason is arithmetic:**
`check.py::main` hashes `harness/*.py` into every gate record's
`source_sha256`, so a one-line edit takes `harness/measure.py --check-stale`
from **0 STALE to 25 STALE** — every gate record but this one — and costs a full
26-pattern gate sweep to clear. **`TASK_119` is already written to edit
`check.py` and already budgets exactly that one sweep, and says so in its own
opening: *"EVERY ITEM HERE EDITS `harness/check.py` … the whole task costs ONE
26-pattern gate sweep … That is why they are batched."*** **Landing it here
would have bought a second sweep and nothing else.** The diff and the control
are held as a rider (`.tasks/TASK_118_REPORT.md` §E). ⚠ **`check.py` is not
MEASUREMENT-hashed — that part of the budget was right — but it is
GATE-RECORD-hashed, and `--check-stale` reads gate records too.**

**Measured, on the real `check.py` with the fix applied and on the shipped one
out of `git`, before the edit was withdrawn:**

```
  MUTANT-A   exit=1  ub=False  leak=True      <- error-path dig_free deleted
  CONTROL-B  exit=0  ub=False  leak=False     <- shipped rung
  ok    the RECORD says leak=True on the leaking rung
  ok    ub=False on the same row, so the `leak` key is NEEDED and not redundant with `ub`
  ok    the gate FAILS the mutant: ... Miri reports a MEMORY LEAK at process exit
  ok    the shipped rung passes with leak=False ...
  OLD-CODE   exit=1  ub=False  leak=<KEY ABSENT>
  ok    the old record has NO leak key and ub=False: a reader auditing results/gate/*.json by `ub` saw nothing
  ok    ...and the old gate still FAILED, on the exit code
```

⚠ **`ub=False` on the mutant is asserted deliberately**: without it the script
would only show the new key works, not that it was needed. And the OLD-CODE arm
loads the pre-fix `check.py` out of `git` and runs it on the same mutant, so
*"the record showed nothing"* is measured rather than remembered.

⚠ **It also closes a small hole, and it is a trap for the next pattern rather
than a repair of this one:** on an input whose model declares a **non-zero**
`expected_exit`, a leaking rung whose exit happened to equal that code used to
pass. No committed row is in that position — 186 Miri rows expect 0, five expect
5, one expects 7, and no committed stderr contains `memory leaked` — so **no
shipped verdict changes.**

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

**Four shouts and one BLOCKED row, all expected and all permanent.** The four
shouts are stage 0b saying that `idiom.forbidden[0..3]` backtick no spelling —
correct, they forbid a STRUCTURE, and the `why` says so in the gate's own words.
The blocked row is Miri on `large.bin`, above. ⚠ **This paragraph used to say
*"five shouts … and one is the Miri block"*, which folded a `rep.block` into the
`rep.shout` count**; the gate record keeps them in two different lists
(`loud: 4`, `blocked: 1`) and so does this line now.

⚠ **The four shouts did NOT change when TASK_110 backticked `required[1..3]`,
and that is the right behaviour**: stage 0b's shout is about `forbidden` entries
only, and p42's four prose `forbidden` entries still deliberately quote nothing.
What TASK_110 moved is the `required` audit — 7 present pairs to 17 — which the
gate reports and never fails on.

### 11a. The ladder

Section 5 has the table. Wall clock, `-O3 isolated`, min of 30 interleaved reps
on cpu 3, **secondary to `Ir` and quoted only as a sanity check**: about
**11–13 ms** on `small` and **14–16 ms** on `large` across the eight cells, with
`safe_naive` slowest and the two clang cells fastest on both — the same ordering
the `Ir` column gives **at the ends**.

⚠ **In the MIDDLE it resolves nothing, and TASK_110 has direct evidence rather
than an argument.** `measure.py p42` ran **three times** during TASK_110, on
trees differing only in comments. The `unsafe`-vs-`safe_tuned` order on `large`
came out **unsafe cheaper, safe_tuned cheaper, unsafe cheaper** — it flipped and
flipped back on binaries whose `Ir` never moved. The kernel-exclusive difference
is `11.00 Ir`/call out of ~50 700, **0.02 %**. **So the `+12.00 / +11.00` in
section 5 is an `Ir` result, and wall clock neither corroborates nor contradicts
it.** ⚠ Ranges are quoted to the nearest millisecond here deliberately: a
min-of-30 wall figure is a number only a rebuild can produce, and `NOTES.md` is
inside the gate record's `source_sha256` (the same rule section 3 applies to the
leaked byte count and section 11c to Miri's allocation IDs).

### 11b. The spelling spans -- five R4, four R3, whole-program marginal `Ir`/call, `-O3 isolated`

Measured in ONE session by `controls/spellings.py --measure` at TASK_110, from
the shipped rungs:

| variant | small (97) | large (4096) | admissible as a p42 rung? |
|---|---|---|---|
| **r4_ship** (do-while, descending cursor) | **1407.00** | **51127.00** | ✅ **SHIPPED**, Verus-verified 18/0 |
| r4_idxfold (the fold by reverse INDEX) | 1617.00 | 59834.00 | ✅ — was the shipped rung to TASK_109 |
| r4_add (`p.add(i)`) | 1407.00 | 51127.00 | ❌ no vstd spec for `<*mut T>::add` |
| r4_movptr (cursor + counter) | 1491.00 | 54710.00 | ❌ same |
| r4_endptr (cursor vs end ptr) | 1455.00 | 53174.00 | ❌ needs the one-past-the-end pointer (section 9a) |
| **r3_ship** (`with_capacity`+`extend`+`rev().fold`) | **1419.00** | **51138.00** | ✅ shipped |
| r3_revidx (`extend` + index fold) | 1627.00 | 59845.00 | ✅ |
| r3_zeroed (`vec![0;len]`+`clear`+`extend`) | 1572.00 | 55298.00 | ❌ **NOT R3** — see below |
| r3_push (`with_capacity`+`push`+index fold) | 2634.00 | 102846.00 | ❌ **NOT R3** — see below |

**Both spans are over the ADMISSIBLE spellings only** — the three refusals are
listed for the search's sake and are not endpoints of anything. **R4 span
`1407 … 1617` (small), `51127 … 59834` (large), from `r4_ship` and
`r4_idxfold`.**

⚠⚠ **AND THE PUBLISHED R3 SPAN WAS 4.5× TOO WIDE. CORRECTED AT TASK_118, FROM
TASK_116 §B4.** It read **`1419 … 2634` (small), `51138 … 102846` (large)** and
both top endpoints came from a spelling that is **not an R3 rung**.
`required[4]` reads *"R2 acquires with `vec![0u8; len]` and indexes; R3 acquires
with `Vec::with_capacity` and fills with `extend`"* — and under this pattern's
own named-spelling standard a backticked span in a `required` entry pins THAT
SPELLING. **Driven through the gate's own `check.py::spelling_matches` rather
than read off by eye:**

| variant | `vec![0u8; len]` | `Vec::with_capacity` | `extend` | verdict |
|---|---|---|---|---|
| `r3_ship` | no | **YES** | **YES** | ✅ in contract |
| `r3_revidx` | no | **YES** | **YES** | ✅ in contract |
| `r3_zeroed` | **YES** | no | **YES** | ❌ — it spells **R2's** acquisition |
| `r3_push` | no | **YES** | no | ❌ — no `extend` |
| shipped `safe_tuned.rs` | no | **YES** | **YES** | ✅ (the control that says the probe is right) |

**`r3_zeroed` is not a near-miss: it matches the entry's R2 clause.** ✅ **THE
IN-CONTRACT R3 SPAN IS `1419 … 1627` (small), `51138 … 59845` (large)**, from
`r3_ship` and `r3_revidx`. ✅ **The conclusion below survives unchanged** — the
narrowed span still overlaps R4's `1407 … 1617` at both ends. **Only the
published width was wrong**, and this is `p05`'s two-task detour and `p23`'s
span lesson for the third time: *an endpoint is what someone thought to write,
not what the declaration permits.*

⚠ **CAN THE PIN BE MADE TO CARRY THIS? NO, not today, and the answer is in the
gate's own record.** `spelling_matches` is keyed by **language** (`c` / `rust`),
never by rung, which is why `required[4]` states its per-rung scoping in
English. The audit applies all five of the entry's spellings to all six rungs
and files the misses: `results/gate/p42-goto-cleanup.json`'s
`idiom_audit.required_absent` is **13** and `required_pins_nothing` is **5**, and
those 13 rows are *exactly* the per-rung scoping the prose describes. So the
record already contains the evidence; **nothing compares it to a pin.** Two
repairs exist and both are gate changes — a per-RUNG key alongside `c`/`rust`,
or pinning the `absent` set in the contract — and neither passes
`.memory/02-bench-rules.md`'s *"could this happen by accident?"* test very well:
no shipped rung is at risk, only an ANALYSIS that quotes a variant. **Reported,
not wired up** (`PROTOCOL.md` rule 5).

(The inadmissible `r4_add` happens to tie `r4_ship` to the instruction, so
including it would not move the endpoint — but it is excluded on principle, not
because it is free to exclude.)

### ⚠⚠ THE HEADLINE THIS SECTION USED TO CARRY IS RETRACTED, AND SO IS THE CONSTRUCTION THAT PRODUCED IT

Until TASK_110 this section read:

> ~~*cheapest R3 found (1419.00 / 51138.00) is below cheapest R4 found
> (1455.00 / 53174.00), by 36.00 and 2036.00 — so "safe-tuned Rust beats unsafe
> Rust here" is not an artefact of an unsearched R4 side. It is a statement
> about the two INFIMA, on eight spellings.*~~

**It is refuted twice over.**

1. **On the numbers.** One further R4 spelling — `r4_ship`, using nothing the
   pinned vstd does not already specify — is **below every R3 spelling p42
   measured**. `min(R3 found) − min(R4 found)` goes `−36.00 / −2036.00` →
   **`+12.00 / +11.00`. The sign flips.** The R4 side *was* unsearched, which is
   the very thing the retracted sentence denied.
2. ⚠⚠ **On the form, and this is the part worth keeping.** `min − min` was
   never a licensed construction here, and **p42's own hashed `why` says so, in
   words this pattern carries byte-identically with five others**: *"`min(R3
   found) − min(R4 found)` is **NOT the repair** — two upper bounds differenced
   bound nothing in either direction."* Calling the two minima *"the two
   INFIMA"* is the error in one word: **they are upper bounds on the infima over
   the spellings someone happened to try**, and `r4_ship` is the counterexample
   the paragraph predicted. **A pattern can quote its own declaration's
   retraction and then commit the retracted move four sections later; p42 did.**

### What ships instead

✅ **`R3ship − R4ship` — two SHIPPED cells, which is the only form that
paragraph licenses:** **`+12.00` on `small` and `+11.00` on `large`**,
kernel-exclusive (section 5), and `+12.00 / +11.00` whole-program as well. With
R4 held fixed by fiat at the shipped verified spelling, that bounds
`inf(in-contract R3) − R4ship` from above and nothing else.

✅ **And beside it, both spans — which is what `.memory/01-ladder.md` asks for
instead of a pair interval.** ⚠⚠ **They OVERLAP, at both ends: the R3 span's
lower endpoint (1419) lies inside the R4 span, and the R4 span's upper endpoint
(1617) lies inside the R3 span.** `r3_revidx` at 1627.00 is dearer than every R4
spelling measured; and
`r4_idxfold` at 1617.00 is dearer than two of the four R3 spellings.

> ⚠ **A difference whose endpoints overlap is not a difference.** p42 publishes
> two spans that overlap and one bounded quantity between two named cells. It
> does **not** publish "safe Rust beats unsafe Rust here", and it does not
> publish the mirror claim either — **"unsafe beats safe-tuned by 12"** would be
> the same mistake with the sign turned round, made off a search that has now
> been wrong once. **The row's honest statement is that on this kernel the R3
> and R4 admissible classes are not separated by the measurement.**

✅ **Clean negative: `with_addr` is not the pessimisation.** `r4_add` measures
identically to the shipped rung at both inputs (1407.00 / 51127.00). What moved
the R4 endpoint was the number of induction variables in the fold loop — two
down to one — and not the addressing spelling.

### 11c. Miri

`controls/miri_seeds.sh`, **re-run at TASK_110 on the do-while fold**. **Seeds
0,1,2,3,4,5,6,7 over the nine small inputs: no UB, no leak, at every seed.**
`adversarial-wincap.bin` (200 000 words) is clean at the default seed;
**`large.bin` is BLOCKED — it exceeds 180 s under interpretation**, which is
`check.py`'s own `MIRI_TIMEOUT`, so that one input is unchecked and the others
are not.

⚠ `adversarial-win1.bin` is the sharp input for this rung: `win_len == 1`, so the
do-while executes its body once and breaks on the first `q == p`, with no
address ever computed outside the one-byte allocation.

**THE POSITIVE CONTROL FIRES**, and this is the row that matters, because it is
the only mechanical check p42 has that **R4** does not leak (section 10):

```
adversarial-notag.bin   rc=1  miri-leak=YES want=YES OK  size: 32, align: 1
adversarial-mixed.bin   rc=1  miri-leak=YES want=YES OK  size: 24, align: 1
adversarial-win1.bin    rc=1  miri-leak=YES want=YES OK  size:  1, align: 1
small.bin               rc=0  miri-leak=no  want=no  OK
ALL AS DECLARED
```

on the shipped `unsafe.rs` **with the error path's `dig_free` deleted**. The
leaked block sizes are `win_len` and are a property of the input; the counts are
what `n_iters = 4` predicts — 4 of 4 calls error on `-notag` and `-win1`, 2 of 4
on `-mixed`, 0 of 4 on `small`.

⚠ **CORRECTED AT TASK_110, and it is this file's own rule turned on itself.**
This block used to transcribe Miri's **allocation IDs** — `alloc7447`,
`alloc13213`, `alloc3233` — and on the re-run they came back `alloc7533`,
`alloc13345`, `alloc3279`. An allocation ID is a number only a rebuild can
produce, `NOTES.md` is inside the gate record's `source_sha256`, and section 3
of this very file quotes `.tasks/PROTOCOL.md` rule 6's lesson against doing
exactly that. **Sizes and counts are derived from the input and stay; the IDs are
gone.**

### 11d. ⚠⚠ The per-element rate is BAND-LOCAL. Do not publish it as a law.

`controls/sweep.py` fits `Ir/call = a + b·win_len` on **band A, win 64..79**, and
then predicts band B (512..527) and both shipped inputs. All four residue
classes mod 4 are in each band.

**Re-run in one session at TASK_110, all seven cells.** ⚠ **The five cells whose
rungs did not change reproduced their TASK_104 rows EXACTLY — fit, in-sample
residual, worst band-B residual and both shipped residuals — which is what makes
the two rows that DID move readable as a change in the rung rather than in the
session.**

| cell | band-A fit | max in-sample resid | worst band-B resid | `small` (97) | `large` (4096) |
|---|---|---|---|---|---|
| c-gcc | `184.177 + 18.91424·w` | 1.36 | **+39.23** | +2.14 | **+582.12** |
| c-gcc-h | `184.177 + 18.91424·w` | 1.36 | +39.23 | +2.14 | +582.12 |
| c-clang | `192.777 + 15.01424·w` | 3.86 | +10.96 | −0.16 | +175.92 |
| safe_naive | `285.464 + 19.51332·w` | 9.42 | +312.75 | −19.26 | +166.96 |
| safe_tuned | `176.014 + 13.06332·w` | 12.57 | +320.94 | −24.16 | **−2545.39** |
| **unsafe** | **`165.611 + 13.04274·w`** | **11.69** | **−310.83** | −23.76 | **−2461.65** |
| **verus** | **`165.611 + 13.04274·w`** | **11.69** | **−310.83** | −23.76 | **−2492.65** |

⚠ **The R4/R5 rows read `203.161 + 14.59274·w`, in-sample 5.21, band-B +47.05,
`large` −141.00/−172.00 before TASK_110.** The do-while fold does not merely
make the rung cheaper: it makes it MISPREDICT ITS OWN OUT-OF-BAND POINTS THE WAY
`safe_tuned` does, sign included. **The rung that used to be the best-behaved
under extrapolation is now among the worst**, which is a second reason not to
publish a rate: the residual structure is a property of the loop shape, and the
loop shape is exactly what an in-contract respelling is free to change.

**Every cell's out-of-band residual is 2.8× to 33× its in-sample residual** —
c-clang 2.8×, safe_tuned 25.5×, unsafe 26.6×, c-gcc 28.9×, safe_naive 33.2× —
and `unsafe`, now the cheapest rung and the one a headline would quote,
mispredicts its own SHIPPED `large.bin` by **−2462 `Ir`/call** off an in-sample
residual of 11.69. ⚠ **That range read *"3× to 25×"* before TASK_110 and was
wrong at both ends on its own table's numbers** (c-clang was already 2.8× and
safe_naive already 33.2×); it is recomputed here rather than copied. That is
p23's lesson reproduced on a new row: an in-sample residual of 12 says nothing
at all. **p42 therefore publishes two measured points per rung and no rate.**

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

⚠ **Re-run at TASK_110 and reproduced to the digit** — and it took a repair
first: `.temp/t104/allocclass/iso.py` consumes two binaries that were correctly
deleted as artefacts and **nothing rebuilt them** (TASK_109 m2, CLAUDE.md
constraint 6). `.temp/t104/allocclass/rebuild.sh` is now that script; it carries
the two compile lines and **asserts the two arms agree on the checksum before
fitting**, because a `fixed` arm that computed something else would make the
isolation say nothing. (The zero-byte `main_shim.c` that sat beside it was
referenced by nothing and is deleted.) The C rungs did not change at TASK_110,
so this row is a reproduction and not a re-measurement.

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
