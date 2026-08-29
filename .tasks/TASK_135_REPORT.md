# TASK_135 — adjudicating the PROVISIONAL debt. Report.

**Role: research reviewer. Nothing was fixed.** Nothing under `.memory/`,
`RECAP.md`, `results/`, `patterns/`, `harness/`, `synthesis/` or `pilot/` was
written. No `git add`, no `git commit`. All scratch is `.temp/t135/`;
`.temp/t135/NOTES.md` lists every file with the command that rebuilds it. I did
**not** run `check.py`, `build.py` or `measure.py` — only
`measure.py --check-stale` (**52 records, 0 STALE**), which is read-only.
`blocked` was read out of `results/gate/*.json`'s `blocked` list, never grepped:
**p01 = 1, p42 = 1, every other pattern 0; 24 `PASS` + 2
`PASS-WITH-BLOCKED-ROWS`** — the committed state RECAP records.

---

## VERDICT TABLE

| # | RECAP line | rests on | manager's triage | **my verdict** |
|---|---|---|---|---|
| 1 | 1588 | `TASK_088` | LIVE | **STANDS** — level half attacked and survives; residue half not attackable from any record |
| 2 | 1704 | `TASK_092` | LIVE | **STANDS** — 3 of 6 components attacked and survive; and rule 3 blocks the manager here for a reason nobody has named |
| 3 | 1883 | `TASK_106` | STALE | **STALE AS WORDED — DO NOT DELETE.** The debt migrated to `TASK_117`. Re-word it |
| 4 | 2108 | `TASK_118` | LIVE, NARROW | **STANDS, AND NARROWER THAN IT IS WRITTEN** — the rule is the shape of **two** of the three failures, not three |
| 5 | 2139 | `TASK_116` | STANDS BY INSTRUCTION | **STANDS.** The instruction is right; **its stated reason is spent** and the live reason is a different one |
| 6 | 2422 | finding 41 | PROBABLY NOT DEBT | **NOT A MARKER** — past-tense narrative. Retraction verified complete. Take it out of the nine → **eight** |
| 7 | 3772 | `TASK_111` | LIVE | **STANDS.** Components falsifiable and one attacked (did not land); **the aggregate claim is not falsifiable as stated** |
| 8 | 4265 | `p17` §10b | LIVE | **STALE — the named ground is gone.** §10b was reviewed twice. ⚠⚠ **And the paragraph the marker sits in is WRONG** |
| 9 | 4490 | three claims | LIVE ×3 | **(i) CLEARED · (ii) CLEARED · (iii) CLEARED**, all three re-derived; the *interpretation* of (ii) has narrowed twice |

**Net: of nine, one is not a marker, two are stale as worded (and neither should
be deleted — one needs re-wording, one needs its paragraph replaced), three are
cleared, and five stand.** Two new blocker/major-class defects fell out, both at
site 8 and site 4.

---

## THE COUNT — it is **thirteen lines / fifteen occurrences**, not nine and not twelve

`grep -n PROVISIONAL RECAP.md` → **13 lines**. `grep -o` → **15 occurrences**
(lines 11 and 12 carry two each).

| where | lines | occ |
|---|---|---|
| START HERE box (11, 12) | 2 | 4 |
| rules/traps prose (96) | 1 | 1 |
| **finding level** (1588, 1704, 1883, 2108, 2139, 2422, 3772, 4265, 4490) | **9** | **9** |
| ⚠ **owed-queue history block, line 3945 — the one the manager missed** | 1 | 1 |

**Line 3945** sits inside *"CLOSED at TASK_053–056 — history, not work"* and reads
*"`forbidden_hits` (F6) was **declined** and is now **RE-OPENED** … `TASK_063`
settled the defect and recommends **fail, batched** — `.memory/02-bench-rules.md`,
PROVISIONAL)"*. It is neither box, nor rules prose, nor a finding: it is a
**pointer at a live PROVISIONAL recommendation in the authoritative layer**
(`.memory/02-bench-rules.md:154, :184`), for a `check.py` change that is still
owed and that would stale every gate record. It is real debt and it was
uncounted.

⚠ **And the box's *"clear the 12 PROVISIONALs"* is off by more than three, in the
other direction, if it means the project's debt rather than RECAP's:**

```
.memory/06-catalogue.md   24      results/SYNTHESIS.md          3
.memory/03-measurement.md 18      results/synthesis.md (gen)    3
RECAP.md                  15      synthesis/{synthesize,census}.py  2
.memory/02-bench-rules.md  8      patterns/p16-tlv-walk/{spec,NOTES}.md  2
.memory/04-verus.md        6      patterns/p09-bitset/spec.md   1
.memory/01-ladder.md       6      results/gate/{p09,p16}*.json  2   (propagated)
.memory/00-environment.md  3      results/tables/{p09,p16}*.md  2   (propagated)
.memory/05-layout.md       1
                                  .memory/ total: 65
```

### ⚠⚠ The two the manager should care about are **inside hashed contract fences**, and they are already false

`patterns/p09-bitset/spec.md` and `patterns/p16-tlv-walk/spec.md` each carry a
PROVISIONAL **inside the `slb-contract` fence** (verified by parsing the fence,
not by grepping the file). Both point at the same thing — `.memory/01-ladder.md`'s
**direction test**, whose repair is marked *"PROVISIONAL — proposed by the manager
at TASK_026, **not yet attacked by anyone**"* (`.memory/01-ladder.md:262`). p16's
fence says it verbatim: *"a repair marked PROVISIONAL and unattacked, and **must
not be cited here again until a reviewer has attacked it**."*

⚠⚠ **A reviewer has. It was attacked at `TASK_045_REVIEW` blocker 1, on p13, on
shipped code, and IT FIRED** — 48% (small) and 17% (large) of p13's published
margin was the pin. That is written **forty lines below the header that says it
is unattacked**, in the same file (`.memory/01-ladder.md:288-300`). This is
PROTOCOL rule 13's exact shape — *the body gets maintained and the header rots* —
and here the rot has propagated into **two hashed contract declarations** and
from there into two gate records and two published tables.

- **Cost:** `.memory/01-ladder.md:262` is free (`.memory/` is in neither
  `check.py::main`'s glob list nor `measure.py::measurement_sources` — verified).
  The two fences cost **two `contract_sha256` moves plus a gate re-run each**, and
  **no re-measure** (`spec.md` is not in `measurement_sources`). Batch them.

**Answer to deliverable 3: nine at finding level is right; the manager's "plus
three" is "plus four"; the total is thirteen lines and fifteen occurrences in
RECAP; and the interesting missed ones are not in RECAP at all.**

---

## SITE 1 — RECAP:1588, `TASK_088` (p19). **STANDS.**

**No `TASK_088_REVIEW*.md` exists.** The only closure is task-level, at
`TASK_113_REPORT.md:322-325`: *"both are corrections-landing tasks for patterns
that already had a review; the reviewed content is the reviewer's."* **That reason
does not cover the marker**, and I checked why rather than inheriting it: every
one of the four things the marker names is **new at TASK_088**, not the reviewer's
— the re-fit was re-derived independently (`.temp/t88/refit.py`), the two-cause
decomposition **contradicted the manager's own task file** (contradiction #253),
the CVE correction took route (i) after showing route (ii) *"CANNOT EXIST AS
WRITTEN"* (#250), and the harness changes are new code in `check.py`/`vparse.py`.
So RECAP:11's *"the closure reason may not cover what the markers flag"* is
**correct**, and *"the markers are stale"* is **wrong** on this site.

**ATTACKED, AND IT SURVIVES (the level half).** From
`results/p19-state-machine.json` alone, `-O3 isolated`, kernel-exclusive
`Ir`/call:

```
small.bin  R2−R4 = 1594.00   R3−R4 =  260.00        (m = 256)
large.bin  R2−R4 = 25594.00  R3−R4 = 4100.00        (m = 4096)

re-fitted   6.25m − 6  = 1594 / 25594      1.00m + 4 =  260 / 4100    ALL FOUR EXACT
retracted   6.25m − 8  = 1592 / 25592      1.00m − 2 =  254 / 4094    off by 2 / 6
```

The re-fit is right at both record-pinned points and the retracted law is wrong at
both. Clean positive.

**NOT ATTACKABLE FROM ANY COMMITTED RECORD — and this is the soft spot.** The
distinctive half of the re-fit is the `m mod 4` residue terms, and **both pinned
lengths are `≡ 0 (mod 4)`, so both terms vanish at every point the record holds.**
The 19 `sweep-m*.bin` blobs the residue term was fitted on are gitignored
(`.gitignore:7`) and appear in **no** record: `results/p19-state-machine.json`'s
`input_sha256` has exactly **8 keys, none a sweep blob** (verified). The
two-cause decomposition, the CVE correction and the harness changes are likewise
untouched by me.

**Cost to clear: 45–60 min.** Regenerate the sweep band from the hashed `gen.py`,
re-run `.temp/t88/refit.py` (its per-length table and both fits are already in
`.temp/t88/refit.log`, so the arithmetic can be audited in ~5 min without
re-running), then one `grep -rn '23269\|23407' patterns/p19-state-machine/` for
the CVE half.

---

## SITE 2 — RECAP:1704, `TASK_092` (p46). **STANDS. Three of six components attacked; all three survive.**

**Attacked today, single-file `./verus_run.py`, never `--cargo`:**

```
python3 patterns/p46-bignum-mac/controls/mkvariants.py --check   -> 8 substitutions, each applying exactly once
python3 patterns/p46-bignum-mac/controls/mkvariants.py --write .temp/t135/p46var

./verus_run.py .temp/t135/p46var/v46_mutreslice.rs   -> 21 verified, 0 errors     THE CLAIM
./verus_run.py .temp/t135/p46var/v46_nosafety.rs     -> 20 verified, 1 errors     MUST-FIRE ARM
./verus_run.py patterns/p46-bignum-mac/verus.rs      -> 21 verified, 0 errors     SHIPPED BASELINE

grep -cE '^\s*assume\(|^\s*admit\(|assume_specification'  v46_mutreslice.rs  -> 0
grep -c 'verifier::external_body'  v46_mutreslice.rs / verus.rs              -> 7 / 5   (= the "+2 trusted items")
grep -rn get_unchecked ~/tools/verus/vstd/ | wc -l                           -> 0
grep -rn get_unchecked ~/tools/verus/vstd/std_specs/ | wc -l                 -> 0
```

and the exclusion-reason refutation itself, at `~/tools/verus/vstd/std_specs/slice.rs:43-48`:

```rust
pub assume_specification<T>[ <Range<usize> as SliceIndex<[T]>>::index_mut ](i: Range<usize>, slice: &mut [T]) -> (r: &mut [T])
    ensures r@ == old(slice)@.subrange(i.start as int, i.end as int),
            final(r)@ == final(slice)@.subrange(i.start as int, i.end as int),
            forall|j: int| !(i.start <= j < i.end) ==> final(slice)@[j] == old(slice)@[j],
```

Value-level, as claimed. The `21 verified, 0 errors` is not vacuous (the
must-fire arm fires), matches the shipped `verus.obligations` pin of 21, and
carries no `assume`/`admit`/`assume_specification`. **Every component I could
reach reproduces exactly.**

**NOT ATTACKED:** `R5 − R4 = 15n + 1`, the `differ` verdict at `-O3`, and the
`5923 / 6284` vs `6453 / 6499` ordering at (24,24) — all three need a build plus
callgrind (~30–45 min; `mkvariants.py`'s docstring gives the exact `rustc` line,
including the `-C codegen-units=1` that is the point of the flag-mismatch
finding). **The marker's headline consequence — *"the headline is now contingent
on the IDENTITY PIN and the TCB … relax either and it inverts"* — rests on
precisely the half I did not measure.** So: STANDS.

### ⚠⚠ And there is a reason to clear this one *last*, which nobody has stated

`.tasks/TASK_092_REPORT.md:4-7` says, in its own second paragraph: *"**This file
was written by the MANAGER after the fact** — PROTOCOL rule 10 says write the
report BEFORE citing it, and the manager landed `.memory/` entries attributing
findings to `TASK_092` while this file did not exist. The content is the
engineer's; the lateness is the manager's defect."*

**Every number in `TASK_092_REPORT.md` is manager-transcribed, not
engineer-written.** Under rule 3 the manager cannot clear a marker on a report it
authored — so this site is *doubly* blocked, and the block is on the report, not
on the finding. Whoever clears it must re-measure, not re-read.

**Partial prior attack that does exist and should not be re-spent:**
`TASK_115_REPORT.md:17-31` reproduced TASK_092's Part B to the last decimal and
then **refuted two of its claims** (the stated mechanism, and *"NEITHER HAS A
PANIC EDGE"*, which is false — both rungs have one, and a disassembly-text test
is a false negative under PIE + GOT-indirect panic calls). Part B is covered;
Part A0 and the flag mismatch are not.

---

## SITE 3 — RECAP:1883, `TASK_106` (p23, finding 38). **STALE AS WORDED. DO NOT DELETE — RE-WORD.**

The marker says *"PROVISIONAL where it rests on `TASK_106`, **which is
unreviewed**"*. That sentence is false today, and I checked the review rather
than the title.

**`TASK_117` is an adequate review**, on the reviewer's own standard: **1 blocker,
4 majors, 3 minors, 5 named clean negatives**, a must-fire reproduction arm that
re-derives all seven published band-K rows to `±0.00` from a script that reads
`safe_tuned.rs` read-only, and — the test that matters — **it contradicted the
manager's written direction and won**: the task file predicted the ratio would go
to ≈7.2×; the reviewer measured **1.3148** and said so in its first line. It also
declined to over-correct, keeping the shape axis alive (`up + dn == mbytes` at all
109 points). That is not a rubber stamp.

**But the debt did not go away — it migrated.** `TASK_117_REPORT.md`'s own verdict
row reads *"finding 38's PROVISIONAL marker: ⚠ **do NOT clear it. Correct the
headline first.**"* The headline **was** corrected (RECAP:1886-1900, struck
`3.11×`, new table, manager-re-measured), so that condition is met — **and the
correction is itself unreviewed reviewer work that RECAP now publishes as the
headline.** Deleting the marker would remove the flag from the *newer* unreviewed
claim, which is strictly worse than leaving a stale one.

**Attack I could run on the replacement, and it did not land (clean negative).**
The published figures are internally consistent to the digit: the spelling term is
`0.00` at `nlow = 31`, where the shipped and cheap-R3 taxes must coincide — and
they do, both `227.00`; at `nlow = 1` the shipped `706.37` less the spelling term
`480.00` gives `226.37`, correctly *inside* the stated `[172.64, 227.00]` band and
not at its endpoint; and `227.00 / 172.64 = 1.31488`, the published `1.3148`. I
could not break the arithmetic. Re-measuring the `2·dn − 2·recs` law itself needs
`.temp/r117/mk_rungs.py` plus 31 blobs of callgrind (~45–60 min).

**Recommended re-wording** (manager's edit; `.memory/`/RECAP only, so free):
> *PROVISIONAL where it rests on `TASK_117`'s re-measured replacement, which is
> unreviewed. `TASK_106` itself was reviewed at `TASK_117`.*

### ⚠ Three more `TASK_106` markers live outside RECAP, and one has the same rot

`.memory/02-bench-rules.md:1660`, `:1708` and `.memory/03-measurement.md:2940` all
carry *"TASK_106, PROVISIONAL (unreviewed)"*. **`03-measurement.md:2940`'s header
is contradicted by its own body 52 lines below**, which says *"RETRACTED AT
`TASK_117`, MANAGER-RE-MEASURED"* and prints the replacement. Rule 13 again.

---

## SITE 4 — RECAP:2108, `TASK_118`'s RULE. **STANDS, AND IT IS NARROWER THAN IT IS WRITTEN.**

The manager's triage is right that only the *rule* is in debt — the conclusion
(encoding 3 fails) is three-armed with one differing variable, four leak
measurements agreeing with `model.py::leak_bytes` against a constant floor, an
`md5_fn` identity check, and a manager re-run. That half is as well evidenced as
anything in the repo.

**The rule is not, and I found two concrete defects in it by reading the
authoritative layer.**

**(a) ⚠⚠ *"the shape of all three failures"* is false. It is the shape of TWO.**
The rule is *"privacy makes a ledger's **contents** unforgeable and cannot make
the ledger **unique**"*, and *"the postcondition certifies only that the author
wrote something on each exit that **empties a map** the author controls."*
`.memory/04-verus.md:1730-1745` is explicit that **encoding 1 is holding a bare
`Tracked<Dealloc>`** — *"NEVER HOLD A BARE `Tracked<Dealloc>`"* is the sentence
that introduces the ledger as encoding 2. Encoding 1 has **no ledger, no map and
no privacy**; its failure is that an affine token is simply dropped. **Neither
clause of the rule can be instantiated on it.** The generalisation reaches
encodings 2 and 3 and stops.

**(b) *"the gap is one proof line wide, in three places"* aggregates two different
programs.** Places 1 and 2 (empty the map, overwrite the map) are measured against
**encoding 2** (`atk_remove_err`, `atk_assign_err`, both `18/0`); place 3 (a
different map) against **encoding 3** (`atk_decoy_err`, `19/0`). Encoding 3
*blocks* places 1 and 2 — by rustc, `error[E0616]`. **In no single program are all
three holes open**, which is what the sentence reads as.

**(c) The load-bearing premise is asserted, not measured.** *"`res::led_new()`
must be public because `kernel` calls it"* has no arm behind it, and
`TASK_118_REPORT.md:102-110` names the counter-design it deliberately did not
build (`dig_alloc` + `led_new` private to `mod res`, entry `res::run(...)`). That
unbuilt encoding is the direct test of *"cannot make the ledger unique"*.

**Cost to clear: 60–90 min** (build the fourth encoding as a `.temp/` review probe,
not a repair — it exceeds `TASK_118`'s own three-encoding budget). **Cost to fix
(a) and (b) right now: free** — they are wording, in `RECAP.md:2103-2110` and
`.memory/04-verus.md:1838-1844`, and neither file is hashed into anything.

---

## SITE 5 — RECAP:2139, `TASK_116`. **STANDS. The instruction is right; its stated reason is spent.**

**The instruction exists, verbatim**: `TASK_116_REPORT.md`, answer to call 3 —
*"⚠ **Do not clear finding 39's PROVISIONAL marker.** The pattern's gate is green,
its record reproduces, its corrections landed — **and its central positive claim
is false.**"*

**I do not think the instruction is wrong. I do think its reason no longer holds,
and that matters, because a marker kept on a spent reason is how the next session
gets it wrong.** The central positive claim TASK_116 was protecting against —
*"leak-freedom on R5 is stated by the GHOST LEDGER"* — **has since been
retracted** (finding 39's own title now reads *"TWO HEADLINES PUBLISHED AND
RETRACTED"*). There is no longer a published false claim for the marker to guard.

**It stands on fresher ground instead, and the ground is genuinely live:**
(i) `TASK_118`'s rule is new, unreviewed and defective in two ways (site 4) — and
it landed on this same finding *after* TASK_116 wrote its instruction;
(ii) TASK_116's **own** running-count items 5 and 6 — *a module-local
`Tracked<Freed>` receipt is FORGEABLE in proof mode (`3 verified, 0 errors`); a
privacy-scoped one is NOT* — are reviewer-produced measurements, now quoted in
RECAP:2082-2084 as *"the live repair lead"*, and **no agent has ever attacked
them**. A reviewer's own new measurements are exactly what rule 9 exists for.

**I attacked the paragraph the marker is attached to — the clean negative — and it
survives, reproduced today:**

```
strings ~/tools/verus/rust_verify | grep -oE 'verifier::[a-z_0-9]+' | sort -u   -> 22, and none is a linear/must-consume mode
grep -rni affine ~/tools/verus/vstd/          -> 0
grep -rni affine ~/tools/verus/vstd/std_specs/ -> 0
```

The 22 are `accept_recursive_types, allow, allow_complex_invariants,
assume_termination, decreases_by, deprecated_postcondition_mut_ref_style, exec,
exec_allows_no_decreases_clause, external_body, external_trait_specification,
external_type_specification, internal_trait, loop_isolation, nonlinear,
prophetic, recommends_by, reject_recursive_types,
reject_recursive_types_in_ground_variants, spinoff_prover, truncate,
type_invariant, verify`. **Not one is a linearity mode.** The corrected `22` (not
`23`) is what `.memory/04-verus.md:1807` says today, so TASK_116's item 4 has
landed. ⚠ One scope note the negative does not carry and should: `strings` on the
binary finds attribute names that appear as **literal strings**; it is a good
census of the *attribute* surface and says nothing about a non-attribute
mechanism. The `affine` grep is what closes that, and it is `0`.

---

## SITE 6 — RECAP:2422, finding 41. **NOT A MARKER. Retraction verified complete.**

Read as written, the sentence is **past tense and about a marker, not one**:
*"This finding was landed as `TASK_120`'s replacement for finding 40, marked
PROVISIONAL, explicitly so it could be attacked. `TASK_122` attacked it AND IT DID
NOT SURVIVE."* A `grep` counts it; a reader does not. **The manager's "PROBABLY
NOT DEBT" is right, and it should come out of the nine — leaving eight live
finding-level markers.**

**Retraction completeness — checked before agreeing, three ways:**
1. `grep -rn "nothing to price\|7 of 22\|LADDER.*COST" .memory/` → **0 hits.** The
   claim never reached the authoritative layer. Rule 9's ordering held.
2. RECAP:2427 carries it **struck through**; `results/SYNTHESIS.md:1068-1074`
   records it as dead with the control-arm blocker restated. Those are the only
   two occurrences in the corpus.
3. RECAP:2478 carries a **forward prohibition** — *"do NOT reuse 'the ladder has
   nothing to price' as a kill criterion … `p46` is the counter-example already in
   the tree"* — and no `.memory/06-catalogue.md` refusal row uses it.

**Complete.**

### ⚠ The inverse defect, in the same finding, with no marker at all

Finding 41's **second half** — TASK_122's settlement of the 18.9 M `Ir` drift
(RECAP:2484-2520) — is new reviewer-produced measurement, published as
*"SUFFICIENCY, NOT ACTUALITY"*, and it carries **no PROVISIONAL marker**. Its
`.memory/` counterpart is worse: `.memory/03-measurement.md:3077-3079` reads
*"**PROVISIONAL AND UNREVIEWED** — `TASK_120`'s own result … **`TASK_122` §A/§B is
its review.**"* Those two sentences cannot both be operative. A reader deciding
whether to trust the `<100 Ir` noise-floor rule gets no answer from that header.

---

## SITE 7 — RECAP:3772, `TASK_111`. **STANDS. The aggregate claim is not falsifiable as stated; its components are.**

**No review exists.** `TASK_112` is a *landing*
(`TASK_112_REPORT.md:1-3`, *"Role: research writer/engineer"*), and `TASK_113`
was offered the review and **declined it**, checking the landing instead:
*"reviewing a review, twice; not worth it, and I checked the landing instead of
asserting it"* (`TASK_113_REPORT.md:338-342`). **That is the `TASK_113` closure
gap in its purest form** — landing ≠ attack — and it is the site where the
manager's triage and mine agree most cleanly.

**The task asks me to say whether it is unfalsifiable as stated. It is, in one
half and not the other.**

- **Falsifiable and cheap: the component absence claims.** *"Finding N is absent
  from the document"* is refuted by one grep. B1 (finding 4) is the model of it
  and runs a positive grep and a negative grep.
- **Not falsifiable: the aggregate.** *"What compression cut was the pro-safety
  half of the ledger, four to six times running."* Three reasons, each sufficient:
  **(i) no denominator** — 12 findings are named as dropped out of 39, and nothing
  is said about the other 27, so no drop-rate by direction can be computed;
  **(ii) the `direction` column is a label the reviewer assigns**, not a property
  in the record — RECAP does not classify findings by direction, and the report's
  *second* dropped list (findings 35, 34, 23, 21, 5, 22) carries **no direction
  labels at all**, so the reviewer's own enumeration is 6 labelled and 6
  unlabelled; **(iii) "four to six" is elastic by construction** — the same
  evidence supports either count depending on whether findings 17 and 8 are
  included, and no rule is given.
  The report concedes part of this itself: *"The §C.1 finding walk is a
  judgement."*

**Attack I ran, and it did NOT land — a clean negative worth recording so nobody
re-runs it.** Falsify-by-presence against the document the review actually read:
`git show 49e3828:results/SYNTHESIS.md` → **636 lines, matching the reviewer's
stated line count exactly**. Greps for `143 740 000`, `sawtooth`, `next_pow2`,
`incomparable`, `not nested`, `chained to the prover`, `one-byte`, `heap corrupt`,
`both ends` → **0 hits each**. The only two hits in that neighbourhood —
`_FORTIFY_SOURCE=3` at `:87` and *"seven of eight multiples of four"* at `:498` —
are **both disclosed and correctly annotated as unrelated in the report itself**
(`TASK_111_REPORT.md:54-57`). **The absence half of B1 is honest and reproduces.**

- ⚠ *minor:* the command as printed is `grep -in 'fortify|heap corrupt|silent|one-byte|seven of eight'` — a BRE, which matches **nothing at all**. The reviewer's parenthetical shows the true result, so the finding is sound and the *citation* is not runnable. Same class as the `check.py:NNNN` rot the project already has a rule for.
- ⚠ *a live correction already exists and has not reached RECAP:3776-3784:* `TASK_112_REPORT.md:177-184` corrects finding 32's price half — it is **five** spellings at `6.00` and one (`c_noback`) at `2.00`, and the only defined spelling that costs *more*, `c_halves` at `+12.00` gcc / `+32.00` clang, is **the two-half read the Rust rungs are forced into**, i.e. it runs *against* safety. **A mixed-direction row inside a table whose whole thesis is that the direction is uniform.** RECAP still quotes the unqualified *"the undefined spelling is the DEAREST of its six neighbours"*.

**Where this leaves it.** The finding is a **plausible, unfalsified hypothesis**
with two strong measured components (findings 4 and 14 — both were acted on and
are in today's document) and four unmeasured ones. It is currently published in
RECAP's **"The recurring traps"** section, which is a register reserved for things
the project has established. **That register is stronger than the evidence.** The
marker is what stops a reader from noticing, so it stands.

**The one measurement that would settle it (~60–90 min):** classify all 39 RECAP
findings by direction, grep each against `49e3828:results/SYNTHESIS.md` — **not**
today's 975-line file, which is the wrong artefact — and publish the drop rate by
direction. That is the census §C.1 asked for and the report did not run.

---

## SITE 8 — RECAP:4265, p17 §10b. **STALE — and ⚠⚠ THE PARAGRAPH IT MARKS IS WRONG. This is the finding of the task.**

**The stated ground is gone.** The marker reads *"PROVISIONAL — in
`patterns/p17-http-range/NOTES.md` §10b per rule 9, **awaiting review**."* §10b
has been reviewed **twice**:

1. **`TASK_083_REVIEW` majors 6 and 7 attacked it and WON** — §10b says so in its
   own text: *"⚠⚠ **RETRACTED, TASK_083_REVIEW majors 6 and 7 … BOTH HALVES ARE
   WRONG.**"*
2. Its **replacement** landed at `TASK_084` (`git log -S "11 + 7·nsuf"` → commit
   `bce8aa8`, *"TASK_084: …"*) and was verified at **`TASK_084_REVIEW` item 12**,
   which upheld it *and re-derived the mechanism independently* from the
   reviewer's own `asm.py show --raw`: *"the level law predicts 32 for both
   shipped inputs and the measured `R3ship − R4` is 32.00 / 32.00; … `6.50/request`
   survives only as an explicit retraction. Mechanism re-derived …: the outer
   per-request loop is scalar, the 4× unroll is the **inner byte fold**."*

### ⚠⚠ And RECAP:4255-4260 still publishes both retracted halves

> *"lag-4 differencing gives 26, 26, 26, 26 with ZERO residual **= 6.50 `Ir` per
> request** — a mod-4 sawtooth **from the 4×-unrolled table walk**, the same
> device p17 §3b already uses on the byte axis."*

Against p17's own §10b, which the marker points at:

> *"⚠⚠ **DO NOT CARRY `6.50 per request` FORWARD.** It is `7 − 2/4` … For a
> 20-range request … the level law gives **151**; `7·nsuf + 9` gives 149 and is
> nearly right; **`6.50/request` gives ≈140 and is 11 low**. The 'correction'
> moved the reader away from the answer."*
> *"⚠ **Neither rung's suffix-table walk is unrolled at all.** … The 4× unroll is
> the **inner byte fold**, and it is keyed on the **served length**."*
> *"⚠ `inputs/gen.py` said so itself, in a hashed comment."*

`grep -n "6\.50" RECAP.md` → **line 4259 is the only occurrence** outside
finding 8's unrelated p02 range. **The correction never propagated, and the
paragraph carrying the PROVISIONAL marker is the one place it needed to.**

**The replacement law RECAP does not carry**, zero free parameters, zero residual
over **49** points (12 sweep + 32 across four step-bands + 5 predicted before
measured):

```
R3ship − R4  =  11 + 7·nsuf − 2 · #{ i < nsuf : s_i ≡ 0 (mod 4) }
```

It also converts RECAP's *"this band gives 30 there, and §10 already discloses
that"* from a caveat into a **mechanism**: `sweep-nsuf-03`'s suffixes 497/460/423
have residues 1, **0**, 3 → one `≡ 0 (mod 4)` → `32 − 2 = 30`; both shipped inputs
have **no** served length `≡ 0 (mod 4)` and so pay `32`. **The period is the
generator's**, not the kernel's — re-emitting the band at suffix step 36 or 38
makes the sawtooth vanish entirely.

**I verified every figure in RECAP's sentence independently, and they are all
arithmetically correct** — steps `+5,+7,+7,+7,+5,+7,+7`; OLS slope `272/42 =
6.47619`, intercept `40 − 6.47619·4.5 = 10.857143`, max |residual| `0.8095` at
`nsuf = 2`; lag-4 `26,26,26,26`. **It is the conclusion drawn from them that is
retracted**, which is exactly why this survived: the numbers check out, so nobody
re-read the sentence around them.

⚠ *Minor, same paragraph:* the marker says *"in `patterns/p17-http-range/NOTES.md`
§10b"*, which reads as a citation to a marker. There is none there —
`grep -ni 'provisional\|awaiting review\|not yet reviewed\|unreviewed\|rule 9'
patterns/p17-http-range/NOTES.md` → **0 hits**.

**Action: this is not a marker to clear. It is a paragraph to replace.** Cost:
**free** — `RECAP.md` only, no gate, no re-measure.

---

## SITE 9 — RECAP:4490, three claims. **ALL THREE ATTACKED. ALL THREE REPRODUCE.**

Re-derived today on a `0 STALE` tree from committed records only, with two
committed tools that read nothing else: `python3 .temp/synth/aggregate.py` and
`python3 synthesis/census.py`.

### (i) `R5 − R4 = 0.00` on all 40 rows → **CLEARED, and it is a tautology on every one of today's 52**

`census.py`: *"`R5-R4 == 0` on every row: **True** (26 patterns × 2 blobs)"*.

⚠ **It is not a measurement anywhere, and I checked the one place it might have
been.** Parsing every `slb-contract` fence: **25 of 26 patterns pin `unsafe ==
verus` at `O3: exact`. `p36` alone pins `O3: norel`** — and `norel` still forces
`Ir` equality, because p36's own `why` records *55 instructions, 54 non-padding,
170 bytes each, normalised text identical, exactly one `lea` displacement
differing*. **There is no row in the 52 where a zero could have come out
non-zero.** RECAP:4466-4468 already scopes this as a tautology; the marker 24
lines below does not, which is why it reads as a result.

⚠ **Three denominators in one item:** the marker says **40 rows**, the newer text
above it says **44**, and today it is **52**.

### (ii) `R3 − R4` NEGATIVE on 5 of 20 → **CLEARED as arithmetic. The interpretation has narrowed twice.**

**All five named figures reproduce to the cent**, and a sixth has joined:

```
p10-fir-stencil   -323.00 / -603.00        p13-strncpy-trunc  -177.00 / -1054.00
p11-nul-scan     -5768.00 / -24503.00      p18-varint-shift    -25.00 /   -12.00
p12-strcat-fixed    +3.00 /   -26.00       p46-bignum-mac     -119.00 /  -815.00   <- NEW since the marker
```

**6 of 26 patterns, 11 of 52 rows.** But the project's own instruments have
already narrowed the *claim built on it* twice, and both narrowings post-date the
marker:

- **`p11` is `NOT-LIC`** — `census.py`: *"22 LICENSED, not licensed: p11 p27 p36
  p42"*. A `NOT-LIC` row is *known to be wrong* as a kernel-exclusive difference
  (p11: *"R4 chained to the prover; `r4_cstr` inadmissible"*). The published count
  is **4 of 22 negative on both blobs** — p10, p13, p18, p46.
- **Against the searched in-contract R4s the project has already measured, two of
  the five sign-flip**: `p13 −177/−1054 → +44.00/+77.00` (a bounded unchecked
  consumer, `19 verified, 0 errors`, no new trusted item) and `p12 +3/−26 →
  +20.00/+66.00` (route A, `15/0`, twin `18/0`, `identity exact`). `census.py`
  arm C: the distribution at searched values is **`7 / 3 / 10`**, i.e. **3 of 22**.

**So the figure runs `6/26 → 4/22 → 3/22` (23% → 18% → 14%) depending on which of
the project's own corrections you apply — and the marker's own hedge, *"the sign
may be an artefact of R4's spelling"*, has been vindicated for two of the five
patterns it named.**

### (iii) *"a cross-pattern `Ir` comparison is available in `isolated` mode ONLY"* → **CLEARED**

Re-derived: of **414** `whole`-mode `-O3` cell/input pairs, **394** have
`kernel_exclusive_ir = None`. The **20** survivors are all `c-gcc` / `c-gcc-h` on
p03, p04, p08, p38, p46 — **not one Rust rung, and therefore not one row that
could carry an `R3 − R4`**. (Marker: 318/302. §1 text: 350/334. Today: 414/394.
Shape intact; the denominator grows with the tree.)

---

## DELIVERABLE 4 — is the project's prose consistent with `R3 − R4 < 0` on a quarter of the tree?

**Yes, and the published prose is more careful than the marker.** Three checks:

1. `results/SYNTHESIS.md:143-145` publishes the negative bucket **by name and by
   count** (*"4 of 22 are negative on both blobs — p10, p13, p18, p46: safe Rust
   is cheaper than the unsafe rung"*), with the licence rule stated first;
   `:158-171` publishes both sign flips in a table; `:171` gives `7/3/10` at
   searched values; and `:151-153` even discloses that **`9 + 4 + 9 = 22` is a
   coincidence and not a partition** (p18 in two buckets, p16 in none), which
   `census.py` re-derives with its own warning. Nothing is hidden.
2. ⚠⚠ **The sentence the marker says it contradicts is not one this project
   says.** `grep -rn "safe tuned Rust is dearer than unsafe" .memory/ RECAP.md
   results/SYNTHESIS.md` returns **exactly one hit: `RECAP.md:4496`, inside the
   marker itself, where it is being denied.** The task file's framing — *"`R3 − R4
   < 0` on a quarter of the tree contradicts a sentence this project says
   often"* — **does not hold.** The project's habit runs the *other* way:
   *"safe beats unsafe"* occurs **14 times** (RECAP ×7, `.memory/01-ladder.md` ×5,
   `06-catalogue.md` ×1, `SYNTHESIS.md` ×1) and is **retracted or hedged at every
   one**.
3. The only near-universal I found — `.memory/03-measurement.md:1186`, *"`R3−R4` is
   `+1.2…+6.9%`, **always positive**"* — is scoped to **p05's `small` wall-clock
   cell across 17 measurements**, not to the tree, and that cell is withdrawn
   two lines above.

**So it is not a footnote the project is hiding, and it is not a result waiting to
be published. It is already published, twice, with both corrections attached.**
What is *not* published anywhere and is the honest headline available here:
**the tree's negative-`R3 − R4` count is not a fact about safety at all — it is a
fact about which side was searched.** Every one of the four R4-side levers the
project has found moves the number **against** safe Rust; the two R3-side levers
move it the other way and are not applied. That asymmetry is stated in
`SYNTHESIS.md:181-186` and is the only thing in this area that survives every
correction.

---

## Clean negatives — attacks that were named and did NOT land

1. **Falsify-by-presence against `TASK_111`'s B1** — the pre-`TASK_112`
   `SYNTHESIS.md` really does lack all nine tokens; both incidental hits are
   disclosed in the report. B1 is honest. (site 7)
2. **`TASK_117`'s replacement arithmetic** — the `1.3148`, the `227.00`
   coincidence at `nlow = 31`, and `706.37 − 480.00` all check out. (site 3)
3. **`TASK_116`'s clean negative** — 22 `verifier::` attributes, none linear;
   `affine` 0 hits in the pinned vstd *and* in `std_specs/`. Reproduced. (site 5)
4. **`v46_mutreslice` vacuity** — the must-fire arm fires (`20 verified, 1
   errors`), so `21 verified, 0 errors` is not a vacuous verdict. (site 2)
5. **p17 §10b's arithmetic** — every number in RECAP's retracted sentence is
   correct; only the conclusion is wrong. That is *why* it survived. (site 8)

## What I did NOT do

1. **No re-measurement of anything.** Sites 1 (residue half), 2 (`15n + 1` and the
   ordering), 3 (`2·dn − 2·recs`) and 8 (the 49-point law) all need callgrind and
   are costed above, not run — two agents are live and the task forbade
   `check.py`/`measure.py`.
2. **I did not build `TASK_118`'s fourth encoding**, which is the only thing that
   can move *"cannot make the ledger unique"* from assertion to result (60–90 min).
3. **I did not run the direction-by-finding census** that would settle site 7.
4. **I did not audit the 65 `.memory/` markers individually** — I counted them,
   located the two inside hashed fences, and verified that those two are false.
   The other 63 are unexamined.
5. **I did not check whether `results/gate/{p09,p16}*.json` and
   `results/tables/{p09,p16}*.md` would need regenerating** after the fence fix —
   they carry the PROVISIONAL text by propagation, and the gate re-run that the
   `spec.md` edit forces should refresh them, but I did not confirm the table
   render path.

## Memory updates

**None.** `.memory/` and `RECAP.md` are manager-only. Everything durable is in
this report and in `.temp/t135/NOTES.md`.

---

## RUNNING COUNT — **634 + 11 on this branch = 645**

⚠ **Branch delta only. `TASK_133` and `TASK_134` also carry 634;
reconciliation is the manager's job, not mine.**

1. **RECAP carries thirteen PROVISIONAL lines / fifteen occurrences, not twelve** — the manager missed `RECAP.md:3945`, a live pointer at `.memory/02-bench-rules.md`'s owed `forbidden_hits` change.
2. **`patterns/p09-bitset/spec.md` and `patterns/p16-tlv-walk/spec.md` carry PROVISIONAL markers INSIDE the hashed `slb-contract` fence**, uncounted by anyone, and propagated into two gate records and two published tables.
3. **Both of those markers are FALSE**: they say `.memory/01-ladder.md`'s direction-test repair is *"unattacked"*, and p16's forbids citing it until a reviewer attacks it — **`TASK_045_REVIEW` blocker 1 attacked it and it FIRED, on p13, forty lines below the header that denies it.**
4. **RECAP:4255-4260 publishes two claims that p17's own §10b retracts** — `6.50 Ir per request` and *"the 4×-unrolled table walk"*, both killed at `TASK_083_REVIEW` majors 6 and 7 and confirmed dead at `TASK_084_REVIEW` item 12. RECAP:4259 is the only surviving copy in the corpus.
5. **Site 8's marker is stale for the opposite of the assumed reason**: §10b is reviewed *twice*, and the thing that needs fixing is the paragraph carrying the marker, not the marker.
6. **`TASK_118`'s rule is the shape of TWO of the three failures, not three** — encoding 1 holds a bare `Tracked<Dealloc>`, with no ledger, no map and no privacy, so neither clause of the rule can be instantiated on it.
7. **"the gap is one proof line wide, in three places" aggregates two different programs** — places 1/2 are encoding 2's and are *blocked by rustc* in encoding 3, where place 3 lives.
8. **`TASK_116`'s "do not clear" instruction is right and its stated reason is spent** — the false claim it guarded has been retracted; the live grounds are `TASK_118`'s rule and TASK_116's own unattacked items 5 and 6.
9. **The sentence site 9 says it contradicts occurs exactly once in the corpus — inside the marker denying it.** *"Safe tuned Rust is dearer than unsafe"* is not something this project says; *"safe beats unsafe"* occurs 14 times and is hedged or retracted every time.
10. **`R3 − R4 < 0` runs `6/26 → 4/22 → 3/22` under the project's own licence rule and its own searched R4s** — p11 is `NOT-LIC`, and p12 and p13 sign-flip. The marker's own hedge is vindicated, not merely prudent.
11. **`TASK_092_REPORT.md` was written by the manager after the fact and says so** — so under rule 3 the manager cannot clear site 2 even if every number checks. That constraint is on the report, not the finding, and no triage has noticed it.

Items 1–5 and 11 are corrections to the project's record; 6–8 are corrections to
landed findings; 9–10 are measurements. **If you prefer to count only the ones
that change what a file says, the figure is 634 + 7** (items 1, 2, 3, 4, 6, 7, 11).
