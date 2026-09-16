# TASK_PHP_062 — REPORT: row 13, `ph66-hashdel-uncompared`

**Role:** research engineer, one agent. **Date:** 2026-09-16.
**Row directory:** `patterns-php/ph66-hashdel-uncompared/` (23 characters, the
same length class as `ph96-outparam-unwritten` — §3 trap 3).

---

## §0 ⭐ HEADLINE, AND THE ONE QUESTION ROUTED TO THE MANAGER

**The row is built at all six cells and the ladder result is the one the brief
predicted, measured rather than argued:**

> **R1 (gcc), R1 (clang), R2, R3, R4 and R5 return the SAME `u64` on all eight
> inputs — every adversarial input included — and only `c/kernel_hardened.c`
> moves.** `rc=0` everywhere. The entire safety stack is blind to this defect.

**One of the five registered predictions fell outright** (P5), **two split** (P3,
whose own falsifier the shipped `verus.rs` satisfies; and P4, whose `O0` half
survives only in a statistic that can see it), **two survive** (P1, P2). **Two of the task brief's own premises are wrong** and are named in §3.

⚠ **ONE QUESTION IS ROUTED TO THE MANAGER (you), by name, and it is in §8.** It
is about `PROTOCOL_PHP.md` §A3a obligation 5's wording and it is a protocol
decision I may not land. **It is not routed to "a reviewer" or "the next round".**

---

## §1 STATUS — what gated

**THE ROW GATED. `verdict: PASS`, `failures: []`, `complete_run: true`,
`contract_sha256 ff4868908deb…`** — quoted from
`results-php/gate/ph66-hashdel-uncompared.json`, and `check.py`'s own last line
is **`check.py: PASS`**.

All six cells are built at both optimisation levels and both modes (32 binaries),
measured, reported and gated. `verus.rs` is **49 verified / 0 errors** shipped and
**59 / 0** under `--cfg slb_twin`. Six controls ship with their must-fire
negatives and all six are green.

The six-command sequence took exactly the shape `PROTOCOL_PHP.md` §E predicts:
build → measure → report → **gate (FAIL: the table cites no `contract_sha256`
yet)** → report → **gate (PASS)**.

⚠ **It took THREE gate runs, not two, and the extra one was mine.** The first
full run failed on four real things — a `model.py` arm-census rule that refused
this row's own must-NOT-fire adversarial input, a stale `verus.items` pin after I
inlined a helper, and **ten missing `SLB-TRUSTED-ARGUMENT` sections in `NOTES.md`,
one per trusted accessor, which I had simply not known were required.** The
second run I stopped deliberately: I had edited `spec.md` mid-chain and was
therefore paying an extra cycle anyway, which made two other repairs free (§7.7,
§7.8). ▶ **Recorded because "it gated" is not the same claim as "it gated
first time", and the three things the first run caught are the ones a reader
should assume the next row will also miss.**

### 1.1 Brackets, first and last

| bracket | at the start | at the end |
|---|---|---|
| `harness/measure.py --check-stale` | **66 record(s), 0 STALE** | **66 record(s), 0 STALE** |
| `harness-php/gate.py --tool measure --check-stale` | **26 record(s), 0 STALE** | **28 record(s), 0 STALE** |

⭐ The PAT bracket **did not move** — nothing under `harness/`, `common/`,
`patterns/`, `results/` or `pilot/` was touched. The php bracket moved 26 → 28,
which is this row's own two records.

### 1.2 The other checkers, at the end

| | |
|---|---|
| `cbaseline_check.py --ratchet` | **77 hits, ratchet 77** — unmoved; ph66 contributes **0** to the no-C-baseline list and **0** to the one-column list |
| `citecheck.py` | **0** `.temp/` citations from anything in `patterns-php/ph66-hashdel-uncompared/` |
| `contract_audit.py` | **✅ no problems** — `VERDICT hits 13; unfiled 0; stale 0; REAL 3`, i.e. back to its committed numbers (§7.7) |
| `coverage.py` | **✅ PASS** — 0 unrecorded duplicates, 0 stale adjudications |
| `checkers.py` | **CHECKERS PASS** (after two repairs it forced — §1.3) |
| `provenance.py ph66` | 0 FAILED, **kernel overlap 84 %** over ten cited spans |

### 1.3 ⚠ Two manager-ledger repairs this row's gating FORCED, both done and both self-checked

1. **`task_cost.py`'s `CLASS["062"]` flipped from `PENDING:ph66` to
   `{"ph66": 1.0}`, in the same edit that added `ph66` to `ROWS`.** The entry's
   own text asked for exactly that (*"FLIP IT the moment the row gates … neither
   half of the flip can be forgotten silently"*) and `N14` fired until both
   halves landed. ⚠ The comment keeps the PENDING text's own caveat: **1.00
   understates this row** — the scoping that preceded it (`ROW13_001.md`, the two
   `ph66` probes, the `rebuild_hardened_php.sh` generalisation) was manager work
   inside `_061`'s session and is charged nowhere.
   ⓘ The published projection moves with it: **`~57 .. ~72, middle ~58`**
   (was `~63 .. ~79, middle ~64`), marginal **2.38** tasks/row.
2. ⭐ **`task_cost.py`'s `N8d` arm had `unbuilt = "ph66"` HARD-CODED** — a
   must-fire control whose "definitely not built" example **this row falsified by
   being built.** It went red for a reason that has nothing to do with what it
   checks. ▶ **Repaired by DERIVATION, not by a new literal**: `unbuilt` is now
   the first `phNN` in catalogue order that `ROWS` does not contain, so it is
   unbuilt by construction and cannot go stale. ⚠ **That is `F101`/item 109's
   class one level up — a check whose correctness depended on a literal the work
   moved — and the repair is the same shape: compute the operand, do not spell
   it.** Both edits are validated by the file's own arms (`N8b`/`N8d`/`N14`);
   `--selftest` is **PASS**.

---

## §2 THE FIVE PREDICTIONS, SCORED BY NAME

Full evidence in `patterns-php/ph66-hashdel-uncompared/NOTES.md` §7.

| | prediction | verdict |
|---|---|---|
| **P1** | R1–R4 all reproduce the defect and their folds agree | ✅ **SURVIVES, and more strongly than stated** — R5 too, and on the adversarial inputs as well as the benign ones |
| **P2** | Miri reports nothing | ✅ **SURVIVES** |
| **P3** | R5 is the only rung that can refuse it, obligation = key-identity | ⚠⚠ **SPLIT** — the obligation half survives and is measured; the *"only rung that can refuse it"* half is **refuted by its own falsifier**, which the shipped `verus.rs` satisfies |
| **P4** | R1h not free at `O0`, within noise at `O3` | ⚠⚠ **SPLIT** — the `O0` half survives **in family B only** (`A1` is blind there); the `O3` half is **refuted** — the repair is consistently *cheaper*, sign-stable on both compilers |
| **P5** | the `verbatim` tier does not survive the narrowing | ⛔ **REFUTED** — it survives, at 84 % kernel overlap |

### P1 ✅ — and it is the row's reason for existing

`controls/ladder.py --selftest`, O3/isolated, the gate's own binaries:

| rung | cella | celld | deep | many | nowin | orderctl | large | small |
|---|---|---|---|---|---|---|---|---|
| R1 gcc | 5553442908994609152 | 3677079714565854208 | 14964600241287891968 | 930842079897528320 | 0 | 10574059460825272320 | 11734148439434793093 | 7365650064901814160 |
| R1 clang, R2, R3, R4, R5 | *identical on every column* | | | | | | | |
| **R1h** (gcc **and** clang) | **16310587633836665856** | **10574059460825272320** | **17954956657160630272** | **4226173720395463680** | 0 | *same* | *same* | *same* |

Six defective cells across three languages agree on **8 of 8** inputs. The
falsifier — *any rung below R5 whose adversarial fold differs from R1's* — did
not occur, at either optimisation level.

⭐ A datum worth reading twice: **`adversarial-celld` under R1h equals
`adversarial-orderctl` under every rung.** The repaired delete, given cell D's
insertion order, returns exactly what the *correct* insertion order returns.

### P3 ⚠⚠ — the split, and why it is the more interesting answer

The prediction's falsifier reads *"an R5 that verifies with the defective
predicate in place."* **`verus.rs` is exactly that** — 49 verified, 0 errors,
with `:464`'s disjunct in the exec code. It has to be: the shipped `ensures` is
`r == hash_fold(...)` and `hash_fold` is a spec function that *carries* the
defect, which is what makes R1…R5 comparable at all.

So: **P3 as worded is refuted; P3's substance is confirmed and measured.**
`controls/key_identity.py`, three arms:

| arm | predicate | obligation | result |
|---|---|---|---|
| N1 | `b73349dbe4e9`'s | `NEW:container-key-identity` | **VERIFIES** |
| N2 | PHP 5.0.0's | same | **FAILS — `postcondition not satisfied`** |
| N3 | PHP 5.0.0's | vacuous | **VERIFIES** |

N3 is what makes N1-vs-N2 attributable to the **predicate** and not to the file.

⭐⭐ **The sharper claim the row actually supports:** Verus is not *the rung that
refuses the defect*. Verus is **the rung that can be ASKED**. R2, R3 and R4 have
nowhere to put the question; R5 does, and the answer depends entirely on which
obligation is written. ▶ **What this row measures is not that a proof catches
the bug — it is that the proof obligation is where the bug becomes sayable, and
that choosing the obligation is a human act no gate stage in this repository
performs.**

⚠ **Which part resists** (the prediction asked): *nothing* resists at the Verus
level — the obligation is eleven tokens and verifies by one recursive proof with
no lemmas. **What resists is attaching it to the shipped rung.** Making
`verus.rs` itself refuse would mean stating its `ensures` against a *correct*
delete rather than against `hash_fold`, and then R5 would no longer compute the
same function as R1–R4 and the cross-rung checksum would be comparing two
programs. **That is a real tension in the ladder's design and this row is where
it shows.**

### P4 ⚠⚠ — SPLIT, and correcting my own first reading of it is the useful part

Full figures in `NOTES.md` §9.4/§9.5. Both statistics, both C columns, both levels.

* ✅ **First half — *not free at `O0`* — SURVIVES in family B**: `+4.00` / `+6.12`
  (gcc) and `+5.00` / `+9.69` (clang) Ir/call. ⚠ **Invisible to `A1`**, because at
  `-O0` neither compiler inlines `zend_hash_del_key_or_index` into `kernel` — the
  whole defect is in a callee and `c-gcc`/`c-gcc-h` report the same
  `33,968,756` Ir and the same `md5_fn`. ⛔ `O0` figures are lowering readings,
  not performance claims, and `php50_align_sweep.py` hard-codes `OPT = "O3"`, so
  **no `O0` magnitude is swept or published**.
* ⛔ **Second half — *within noise at `O3`* — REFUTED.** The sign is stable,
  negative and the same on both compilers: **the repair is CHEAPER.** Family B,
  O3/isolated, all four **SIGN-STABLE** over a full 32-residue pad sweep: gcc
  `−3.20` / `−19.83`, clang `−2.03` / `−12.00`. Exactly one magnitude clears
  §B5 — `c-gcc → c-gcc-h` on `large.bin`, `−19.83 Ir/call`.

> ⛔⛔ **AND I GOT THIS WRONG ONCE BEFORE GETTING IT RIGHT, WHICH IS THE PART
> WORTH CARRYING.** `A1` reads **exactly `+0.0000`** for `c-clang` at O3, and I
> first wrote that up as *"R1 and R1h compile to the byte-identical kernel — a
> 0.00 that is identity and not noise."* **The `kernel` symbols ARE
> byte-identical; the programs are not.** One `nm` line explains it: clang keeps
> `zend_hash_del_key_or_index` **out of line** (`t zend_hash_del_key_or_index`,
> 0x3a5 bytes in R1 against 0x3a2 in R1h) where gcc inlines it, so **the entire
> repair sits in a symbol `A1` does not count**, and the whole-program slope
> separates the two by `−2.03` and `−12.00 Ir/call`.
>
> ⭐⭐ **`c-clang`'s `inside_share_W` on those cells is 65.31 % and 51.31 %.** A
> perfectly healthy share did not predict it and **could not**: what decides
> whether `A1` resolves a difference is **whether THE DIFFERENCE lands inside the
> symbol**, not how much of the cell does. That is `F74`'s failure mode in a new
> place, and `_061`'s refutation of `ph96` happening to me, on the row whose brief
> told me it would. **§2.8's instruction to show the matrix at more than one
> optimisation level is what caught it.**

⭐ **Mechanism**: R1 tests `p->nKeyLength == 0` first and
`p->nKeyLength == nKeyLength` second; R1h swaps them. For a *string* bucket both
orders cost two length comparisons. For an **index** delete meeting a *string*
bucket — which the benign corpus does constantly, by the prologue's construction
— R1 costs two length tests and R1h one, so R1h **skips work**. At `-O0` the
saving is swamped by the extra comparison being evaluated before the
short-circuit is scheduled; at `-O3` the scheduler keeps it.

### P5 ⛔ — the tier survives

`provenance.py` reports **kernel overlap 84 % (144/171)** against a `verbatim`
expectation of 50 %, over the union of **ten** cited spans. Every function is
lifted **whole**. The one narrowing that could have cost the tier — the resize
path — is a narrowing of the **domain** (the kernel sizes its table from the
record count, a real PHP spelling) and not an edit to any lifted body.
`NOTES.md` §10.

---

## §3 ⛔⛔ WHERE THE BRIEF IS WRONG

§4 item 13 asked for this. **Two things.**

### 3.1 §2.5's table attributes `count=1 → count=2` to **cell D's script**. It is **cell A's**.

`TASK_PHP_062` §2.5 and `ROW13_001` §7 both print

> | adversarial (cell D's script) | `count=1`, victim destroyed | `count=2`, **victim survives** |

**Measured, 2026-09-16, obligation 5 run end to end:**

| trigger | pre-image | post-image |
|---|---|---|
| **cell D** | `rc=0  count=1 survivors='abc'` | `rc=0  **count=1** survivors=6385036779` |
| **cell A** | `rc=0  count=1 survivors='other'` | `rc=0  **count=2** survivors=6385036779,'other'` |

**On cell D the count is 1 on both sides.** It has to be: cell D's array holds
two elements and one delete removes one of them either way — what the repair
changes is **which**. The `count=1 → count=2` reading belongs to cell A, where
the named key is absent so the repaired delete removes nothing.

⭐⭐ **This is not a typo; it is the row's own hazard one level up.** A row that
quoted `count` alone on cell D would have reported *"no change across the
repair"* about a run that flips the answer completely — which is **precisely**
the failure `rebuild_hardened_php.sh`'s own header warns about when it says an
rc-only report *"reads 'no change' across a repair that in fact flips the
observable"*. ▶ **The script was repaired for `rc`; the brief's table then
repeated the same mistake one column over, with `count`.** The observable on
this row is the **survivor list**. Not `rc`, and not `count`.

### 3.2 The catalogue's `⚠ risk` note and the brief agree — but the catalogue is *also* wrong about the preimage, and the brief is right

§3 trap: *"Where this brief and `CATALOGUE.md` disagree, say so in the report
rather than picking one."* **They do not disagree on anything I found.** The
catalogue's `⚠ risk` note (*"it produces no fault — a silent wrong answer"*) is
confirmed by §2 of `NOTES.md`; the brief's §2.2 refutation of the catalogue's
closing sentence (*"compute the preimage"*) is confirmed by
`ph66_djbx33a_collide.py`, whose N4 arm checks the *reason* (33 is a unit mod
2^64) rather than asserting it.

⭐ **But the catalogue's superlative is worth qualifying.** It calls this *"the
best checksum-visible row in the corpus, with the allocator entirely out of the
picture."* The first half is right. The second is right only about the
**observable**, exactly as `ROW13_001` §6 warned — and this row's kernel makes
**one `ecalloc` plus one `pemalloc` per bucket inserted and one `pefree` per
bucket deleted**, i.e. **O(nrec) allocations per call**. §B1a's precondition
does **not** hold here, the row declares that, and every cross-language figure
is labelled. See §6.

---

## §4 §2.3's FIVE-CELL MATRIX, RE-RUN AND RECORDED AS AN EVENT

`sh .tasks-php/probes/ph66_key_identity.sh`, **2026-09-16**, on
`/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/bin/php-5.0.0-mysql-webext`
— **exit 0, all five cells ok, reproducing premise C exactly**:

| cell | rc | survivors |
|---|---|---|
| A victim alone | 0 | `'other'` |
| B reference-held | 0 | `'other'` |
| C victim-is-array | 0 | `'other'` |
| ⭐ D named-key-survives | 0 | **`'abc'`** |
| E benign control | 0 | `6385036779,'other'` |

⚠⚠ **BOTH §A3a CAUTIONS, REPEATED** (and repeated again in `NOTES.md` §2):

1. **Which build**: php-in-safe-rust's **oracle** build (mysql + webext), **not**
   a museum-default 5.0.0, and **its flags are not recorded in a `.buildinfo`**
   — only the `-O3lto`/`-maxlto` siblings carry one — so **no flags are named**
   (`F139`).
2. **A clean run is not evidence of absence** (`F3`). Every cell exits 0 and that
   is the *result*, not a failed reproduction; a different build, a different
   `-O` or a sanitizer could still show something this one does not.

⭐ **Obligation 4 (reproducibility):** run **three times** into three separate
workdirs, byte-identical output every time. This row has a category §A3a's list of three does not name: **a stable,
silent, value-only result** — no signal to be stable or flaky about and no
`si_addr` to vary. `probes/segaddr.c` was **not** run and has nothing to catch.

**It reproduced, so the task did not stop here.**

---

## §5 OBLIGATION 5 DISCHARGED ON A ROW THE PROTOCOL EXCUSES — and the gate defect, in one sentence

`bash .tasks-php/probes/rebuild_hardened_php.sh --label ph66 --patch <row>/controls/b73349dbe4e9.patch --trigger <cell D>`,
**2026-09-16**: cold build **30 s**, incremental rebuild after the patch
**617 ms**, 60 MB, no sudo, no network. Table in §3.1 and `NOTES.md` §4.

**This row's pre-image run does not fault, so §A3a obligation 5 as written
excused it. It was run anyway.**

> ⭐ **The gate defect, in one sentence:** obligation 5 is gated on *"the
> pre-image run faulted"*, but what it buys is *"the upstream fix's efficacy
> measurable on real PHP"* — and efficacy is a question about **the observable
> moving across the repair**, of which `rc` is one instance. **The gate is
> stated on the instrument and not on the question.**

▶ **I agree with `F141` and would put it more strongly.** See §8 for the
question this raises, which is routed to you.

---

## §6 THE NUMBERS, AND THE FIVE THINGS EACH PERCENTAGE OWES

Full tables in `NOTES.md` §9. Summary of what was done and what is published:

* **Both statistics named and separated**: `A1` = `kernel_exclusive_ir`;
  family B = `marginal_ir_per_call` (whole-program slope). **`W1` is not
  published on this row at all.**
* **`inside_share` per cell as a MATRIX, BEFORE the statistic was chosen** —
  `controls/inside_share.py`, **32 (cell × opt × input) triples, both C columns,
  BOTH optimisation levels.** ⛔ **Which `inside_share`: the `W` one**
  (`A1 / callgrind summary total`), not `F74`'s; both are printed side by side
  (`F129`). W range **8.15 % .. 81.78 %**.
* ⭐⭐ **The matrix was used to EXPLAIN a disagreement, never to withhold a
  column** — see §2's P4 and `NOTES.md` §9.3.
* **Both C columns on every cross-language figure**, and the row publishes no
  bare C-vs-Rust headline without the allocator label §B1a requires.
* **More than one optimisation level, measured** — and it is what caught my own
  error.
* **Every family-B figure cleared through §B5 with TWO verdicts**, from a full
  32-residue pad sweep. **Exactly one magnitude is publishable**
  (`c-gcc → c-gcc-h`, `large.bin`, `−19.83 Ir/call`); the other three R1/R1h
  pairs are published as **signs only**, all four sign-stable and negative at O3.

### 6.1 ⛔ One figure is WITHHELD by §B5's own named rule, and it confirms that rule on a second row

*"Never publish a family-B figure for an `unsafe → verus` pair on a row whose
kernel allocates."* **This kernel allocates `O(nrec)` per call** (§B1a's
precondition does not hold, declared in `spec.md`'s `uses_allocator_why`), and
the pair behaves exactly as `ph64`'s did: family B measures **`−25.97` on
`small` and `+792.42` on `large` — it flips sign between the two inputs** — while
`A1` is `−0.96 %` and `−0.53 %`, both negative. ⭐ **That is the rule's second
measured instance, on an independent row, and it confirms it.**
(`safe_tuned → unsafe` flips too: `+104.11` / `−1789.32`.)

### 6.2 ⭐ The ladder's own reading, and the one that is worth stopping on

`A1`, O3/isolated, **same-language ratios** — where the allocator term cancels
and the figure is clean (§B1a decision 4):

| ratio | `small` | `large` | what it prices |
|---|---|---|---|
| **R2 → R3** | **−6.88 %** | **−7.40 %** | the three declared tunings |
| **R3 → R4** | **+1.37 %** | **+0.86 %** | ⛔ removing the bounds checks made it **DEARER** |
| **R4 → R5** | **−0.96 %** | **−0.53 %** | the proof, and it is **negative** |

⛔ **R3 → R4 is the one to stop on.** Removing every bounds check from the bucket
arena cost 1.37 % / 0.86 %, it did not save. ▶ **Mechanism**: R3 binds
`let n = &self.a[p as usize];` once and LLVM hoists the single check out of the
inner comparison and keeps `n` in registers; R4's `nref` returns a reference
through an opaque `get_unchecked` the same alias analysis cannot see through.
**The bound was already free; what `unsafe` removed was an analysis, not a
branch.** Static counts agree — R3 750 instructions against R4 791.

## §7 OTHER FINDINGS WORTH CARRYING

### 7.1 ⭐⭐ `memcmp` is not a discriminator on this construct — and cannot be made one

`controls/differential.py`'s first draft mutated the key comparison to one byte
and **did not fire on a single window**. That is a property of the construct,
not of the probe: every site that compares key bytes has already required
`p->h == h` **and** `p->nKeyLength == nKeyLength`, and the 64 keys have pairwise
distinct 64-bit DJBX33A hashes. **The comparison runs on every match and always
returns 0.**

⛔ **And it cannot be fixed by widening the fixture.** Making `memcmp` decide
needs two distinct keys with an equal 64-bit DJBX33A hash — **exactly the object
the catalogue's "compute the preimage" instruction asked for, and which is not
constructible.** ⭐ *The same fact that makes this row cheap to trigger makes
this one arm of it unreachable.*

▶ **The useful half**: the test that *does* discriminate is the **length** test,
which is precisely the conjunct `b73349dbe4e9` hoists. So the defect turns on
the *kind* comparison and not on the *bytes* comparison, and the labeller's
phrase *"in both key kind and key bytes"* is, on this construct, carried
entirely by its first half.

⚠ **This narrows what the row can claim about real PHP**, where two distinct
strings *can* share a DJBX33A hash — that is the 2011 hash-collision DoS — and
there `memcmp` is the discriminator. No fixture of this shape can reach it.

### 7.2 Item 139 — the two-column reading holds, sharpened in one place and weakened in another

The census reproduces: **9 of 10 `p->h == h` predicates already spell the R1h's
required-conjunct form; `:464` is the only `dual`.** `ROW13_001` §6's own
prediction (that `ph66` would be `F133`(i)'s counterexample) stays refuted.

* ✅ **Sharpened.** The nine are not merely *single-kind*; they are
  **structurally unable to face `:464`'s choice**, and the extraction makes that
  concrete: `_zend_hash_add_or_update` takes `arKey`/`nKeyLength` and nothing
  else, `_zend_hash_index_update_or_next_insert` takes `h` and nothing else.
  **Neither has a parameter that could express the other kind.**
  `zend_hash_del_key_or_index` has `flag`. **The split is a type-level fact
  about one signature, not a statistic about nine siblings.**
* ⚠ **Weakened.** The nine are **not evidence of intent**.
  `_zend_hash_add_or_update`'s conjunct is there because a string lookup *has* to
  compare lengths before `memcmp`; it would be a bug without it. ▶ `F133`(i) as
  worded survives, **but this row is a weak instance of it, not the strong one
  the 9-of-10 ratio suggests. The ratio counts sites that had no choice.**

⭐ **And there is a TENTH place PHP decides a key's kind that the census does not
see**: `HANDLE_NUMERIC` (`zend_hash.h:283-317`), which `zend_symtable_del`
applies *before* hashing. `spec.md`'s `idiom.forbidden[0]` pins it absent on
every rung.

### 7.3 The `E2` fit — asked for in §1, answered plainly

**The `E2` fit is NOT real, and I would not have filed it there.** `E2` is
*"released, then still named"*. On this row **nothing is still named**: the
delete unlinks the bucket from the bucket chain, from the global list and from
`ht->pInternalPointer` *before* freeing it, and the payload's destructor frees
only at refcount 0. There is no surviving name, which is why five oracle cells —
including one holding a live reference to the victim — are silent.

▶ **What this row actually is**: *the wrong thing released*. The harm is in the
**selection**, not in the **lifetime**. ⚠ **That matters for `QUOTA_001`'s
within-family control argument, which depends on the members sharing a
mechanism**: a family control that pairs this row with a genuine
released-then-named row is pairing two different mechanisms under one heading.

⭐ **The corpus agrees with me from two independent directions.** `index.csv`
files LOGIC-001 as `CWE-416` / `refcount-logic`, and its own
`crashes_pristine_5_0_0` column reads **`n/a (non-crash class)`**; and
`invariants-166.json` `cases[98]`'s labeller proposes
**`NEW:container-key-identity`** and files `I7` only because a freeze rule
forbids new entries, adding that the `T3`-honesty sub-rule fires here and has
nowhere to send the case.

⚠ **As instructed, the axis and family are carried across UNMODIFIED and
`CATALOGUE.md`'s `inv/obl` column is NOT edited.** The disagreement is stated in
`spec.md`'s `provenance.obligation_note` and `cwe_note` and in `NOTES.md` §6.

### 7.4 ⚠ The spellings audit caught six `forbidden` HITS *before* the gate saw them

First run: **228 (spelling × rung) obligations, 83 unsatisfied, and SIX DISTINCT
`forbidden` SPELLINGS HIT — which FAIL the gate.** They were `arKey`,
`key_of(sel)`, `_zend_hash_add_or_update`, `zend_hash_del`,
`zend_hash_del_key_or_index` and `_zend_hash_init` — each a real identifier in
the row's own kernels, each quoted **inside the sentence explaining a `forbidden`
entry rather than as the forbidden spelling itself.** Every one had the same cause:
**backticks inside the explanatory English of an entry are pins.** After the
repair (a `forbidden` entry carries exactly one backticked span, the spelling
itself): **32 obligations, 0 unsatisfied.**

ⓘ This is item 100's fourth instance and the **first caught before landing**.
§3 trap 4 is the reason it was caught, and it earned its place.

### 7.5 The `identity` entry was measured, and the first measurement was about the wrong thing

As first built, `verus.rs` split the record loop into a `run` helper (Verus
wants the window bound stated once) and `unsafe.rs` did not. At `O0` the
measured `kernel` symbol was then a **14-instruction wrapper** on one side and
the whole loop on the other, and `identity_level` said `differ` about a
difference that was **entirely the split**. ⭐ It would also very likely have
failed gate stage 3a, whose third disjunct wants a backward branch or a
bulk-memory call inside the `kernel` window. Both rungs now carry the loop in
`kernel`.

Measured after that: `differ` at both levels; at O3 **791 / 3231 (R4) against
770 / 3125 (R5)** — the proof rung is the **smaller** one by 21 instructions and
**0.96 % cheaper** in `Ir(kernel)` on `small`. ⚠ A codegen coin flip, quoted so
nobody reads `differ` as *the proof costs something*.

---

### 7.9 ⚠ A row that QUOTES its own gate verdict owes a seventh and eighth command

`NOTES.md` is in the gate record's `source_sha256`. `NOTES.md` §13a quotes the
gate's verdict. **So writing the verdict down stales the record that produced
it**, and `--check-stale` says so immediately.

▶ The resolution is one more `report` + `gate` after the notes are final, which
is what this row did. ⭐ **`PROTOCOL_PHP.md` §E's six commands get a row from
nothing to a green gate; they do not get it from a green gate to a green gate
*with the verdict written down*.** ⓘ I am **not** proposing a seventh rule: the
cheaper alternative — never quote the verdict, only cite the record path — is
defensible and is what most of the corpus does. It is named because the cost is
real (one extra ~75-minute gate run) and a row that does not expect it will
either re-gate in surprise or ship a stale record.

### 7.8 ⭐ The `rlimit` count was six and the measurement said one

`verus.rs` shipped a first draft with **six** `#[verifier::rlimit(120)]`
attributes, added together before the file verified. Measured afterwards, on the
shipped file: deleting all six gives **`48 verified, 1 errors`** and the single
error is on **`del` and nothing else**; keeping only `del`'s gives **`49
verified, 0 errors`**. ▶ **Five were decoration and were removed.**

⚠ **An unnecessary `rlimit` is not a false claim** — it is a budget that is never
reached and it changes no verdict. **What it is, is an unearned suggestion that
five functions were hard**, and a reader taking the count as a difficulty signal
would have been wrong by a factor of six. ⭐ I first wrote it up as a disclosed
blemish owed at the next re-gate; then noticed I was paying a gate cycle anyway
for an unrelated `spec.md` edit, which made the repair free. **`.memory-php`'s
"a figure a document asserts is computed from the tree" applies to counts in a
source file as much as to numbers in prose.**

### 7.6 ⚠ I built a clause-mutation pre-check and it over-approximated the gate — usefully

The gate's stage 5c takes ~90 minutes on this file (one Verus run per mutated
clause), so I built `.temp/php66/clausetest.py` to run the same mutations 4-way
parallel and find failures an hour earlier. **It reported 21 non-load-bearing
`ensures` conjuncts. The gate reported ZERO.**

▶ **Both are right, and the difference is what the gate actually checks.**
`check.py` mutates **12** clauses on this row — the trusted items' `ensures`, plus
the `assert(false)` call-site probe — and does **not** deletion-test a *verified*
item's `ensures` at all. My script mutated all **59**. Ten of my 21 were also an
artefact of running without `--cfg slb_twin`, where the twins are compiled out
entirely and deleting their `ensures` trivially changes nothing.

⚠ **The lesson is the one this programme keeps re-learning in other places: a
re-implementation of a check is a check of a DIFFERENT THING until it has been
shown to agree.** I did not lose anything by it — the pre-check cost CPU, not a
decision — but I did spend an hour believing eleven repairs were owed that were
not. ⭐ **The cheap version of that hour would have been to read
`check.py:6620`'s `if why != "verified": continue` first**, which is one line and
says exactly which items are in scope.

### 7.7 A `c/*` comment was REWORDED rather than adjudicated, because a re-measure was owed anyway

`contract_audit.py`'s `N8` flagged `kernel.c:468` / `kernel_hardened.c:466` —
*"the record decode … is re-derived **independently** by model.py"* — as a
VERDICT hit, the same word and class as the already-filed
`ph29-recvfrom-alloc/kernel_hardened.c:23`.

I first filed both as `FALSE-POSITIVE`. ⭐ **Then the gate's first run forced a
re-measure for an unrelated reason (a `model.py` fix), which made the reword
FREE — so I reworded the comment and WITHDREW both adjudication entries.**
`.tasks-php/contract_audit.py` is back to its committed bytes; `N8` reads
`VERDICT hits 13; unfiled 0; stale 0; REAL 3`, exactly as before this task.

▶ **The general point, which §F6a's own table does not make:** whether a `c/*`
comment is worth repairing is not only a question about the comment, it is a
question about **whether a re-measure is already owed**. The rule prices the
repair at 32 cells; inside a task that is re-measuring anyway it costs nothing,
and a row that knows that will reword where a row that does not will file.

---

## §8 ⭐ WHAT I AM UNSURE OF — and the question routed to the manager

### 8.1 ⚠⚠ THE QUESTION, ROUTED TO YOU (the manager of `TASK_PHP_062`), BY NAME

> **§A3a obligation 5's gate is stated on `rc`. I discharged it anyway and it
> produced this row's best evidence. But I cannot land a protocol change, and
> the wording I would propose changes the cost model for every future row.
> Which do you want?**
>
> **(a)** Leave the gate as written and treat "discharge it anyway" as a
> convention. ⛔ My objection: a convention that the protocol's own text
> contradicts is what `F123` is about — an obligation demoted to *"nice to
> have"* and then to *"impossible"* in three steps.
> **(b)** Re-word it as *"REQUIRED whenever the row can name an observable the
> repair is expected to move — which is every row, because a row that cannot
> name one has no R1h claim to make."* That is unconditional in practice and
> says why. ⓘ Cost: 30 s cold build + ~600 ms per row, measured twice now.
> **(c)** Something narrower I have not thought of.
>
> ⓘ **The number that decides it is already in the brief**: §1 says **61.3 % of
> temporal rows do not fault**, so the current wording is vacuous on the
> majority of the axis that owes 15 of the 25 remaining rows.

### 8.2 What I could not tell

* ⚠ **`UNTESTED`: whether the `E2` re-filing I argue against in §7.3 would
  change any published number.** I did not run `quota.py`'s family arithmetic
  under a different assignment, and I did not look at what `QUOTA_001`'s
  within-family control claims for `E2` specifically. **§7.3 is an argument
  about the mechanism, not a costing of the move.**
* ⚠ **`UNTESTED`: whether a 64-bit DJBX33A collision is reachable with lattice
  work.** §7.1 says it is *not constructible*; what I actually checked is that
  **digit-lifting cannot work** (the probe's N4 arm) and that a birthday search
  is ~2^32. **I did not try CVP/LLL and I do not know that it fails.** If it
  succeeds, the `memcmp` arm becomes reachable and §7.1's limitation goes away.
* ⚠ **`UNTESTED`: whether `clang`'s R1 ≡ R1h identity at `O3` is stable across
  clang versions.** It is one compiler at one version (22.1.6). P4's refutation
  does not rest on it — the gcc half is independent — but the *"0.00 is identity
  and not noise"* sentence does.
* ⚠ **I could not tell whether `spec.md`'s `obligation_note` is the right home
  for §7.3's disagreement.** It is inside the hashed contract, so it costs a
  re-gate to repair and is *not* in the measurement digest. `NOTES.md` would
  have been cheaper. I put it in both because the contract is where a reader
  looking at `invariant: I7` will be.
* ⚠ **`controls/inside_share.py` sweeps two optimisation levels where `ph96`'s
  swept one.** I have not checked whether the extra 16 callgrind runs make it
  too slow to be re-run routinely; on this row it is minutes, but this row's
  binaries are small.
* ⚠ **A `c/*` comment I chose to keep rather than reword.** `contract_audit.py`'s
  N8 flagged `kernel.c:468` / `kernel_hardened.c:466` — *"the record decode … is
  re-derived **independently** by model.py"* — as a VERDICT hit. I adjudicated
  both **FALSE-POSITIVE** (the same word and the same class as the already-filed
  `ph29-recvfrom-alloc/kernel_hardened.c:23`) because the sentence asserts that a
  second *derivation exists*, not another artefact's *conclusion*. **A reviewer
  may reasonably prefer the reword.** It costs a 32-cell re-measure today and
  nothing if batched with this row's next one; the adjudication entry says so.

* ⚠ **`UNTESTED`: whether flipping `task_cost.py`'s `CLASS["062"]` to `1.00` is
  the classification YOU want.** The entry's own text told the gating agent to
  flip it and `N14` fired until I did, so the flip is what the ledger asked for
  — **but "this row cost one task" is a judgement, not an arithmetic fact**, and
  I am the interested party. The published projection moved `~63..~79/~64` to
  `~57..~72/~58` on the strength of it. ▶ **If you think row 13 cost more than
  one task, change the weight; the comment already records that the manager-side
  scoping is charged nowhere.**
* ⚠ **`UNTESTED`: whether `php50_align_sweep.py` being `O3`-only is a gap.** It
  hard-codes `OPT = "O3"` and cites `.memory-php/03-numbers.md`'s rule against
  quoting an `O0` figure as a performance figure, so I treated the `O0` family-B
  numbers as lowering readings and published none of them. **That is the
  conservative reading and it may be the wrong one**: this row's `O0` family-B
  sign (`+`, the repair costs) is the opposite of its `O3` sign (`−`, the repair
  saves), and a row that could publish both would be saying something the
  corpus currently cannot.
* ⚠ **I did not re-run `.tasks-php/probes/ph66_djbx33a_collide.py --selftest`
  after the key alphabet changed.** I did re-run it at the start (N1–N8 PASS),
  but the probe's arms are about the *algorithm* and the *tarball census*, not
  about this row's alphabet, so nothing in it depends on `kl = 1 + (sel % 7)`.
  **I believe that is right and I did not verify it by mutation.**
* ⚠ **`controls/inside_share.py`'s `F74` column is `n/a` on every `O0/large`
  cell** and I did not chase why. `marginal_ir_per_call` has the key, so the
  most likely cause is a `large.bin` `A1` that the record does not carry at `O0`
  — but **I did not confirm it**, and a `n/a` I have not explained is a hole in
  a matrix I called complete.

### 8.3 Things I deliberately did NOT do

* **I did not edit `CATALOGUE.md`**, `RECAP_PHP.md` or `.memory-php/`.
* **I did not add any `.py` or `.sh` under `.tasks-php/`**, so
  `.tasks-php/checkers.py` needs no new filing; it reports **PASS** and its
  arm-count claims still match. I *edited* `.tasks-php/contract_audit.py` — two
  entries in its `ADJUDICATED` table, which its own N8 arm validates.
* **I did not run `probes/segaddr.c`** — there is no fault to take the address
  of, and §4 says so rather than reporting a `(nil)` that means nothing.
* **I did not leave scratch behind.** `.temp/php66/` is down to 476 KB: the two
  `.py` probes, `probe_main.c`/`probe.sh`, the four `.log` files, the three
  `.php` triggers and the two probe transcripts — **the evidence** — plus
  `REGEN.sh`, which rebuilds every deleted artefact (the 60 MB PHP tree, the
  clause mutants, the scratch binaries, the extracted tarball member) in one
  command. `CLAUDE.md` "Don't" rule 1.
* **I did not re-file the row's axis or family**, per §1's instruction, and §7.3
  is the report the brief asked for instead.

---

## §9 WHAT IS IN THE TREE

| path | |
|---|---|
| `patterns-php/ph66-hashdel-uncompared/` | the row: 6 rungs, `model.py` (three implementations), `inputs/gen.py`, 6 controls, `spec.md`, `NOTES.md`, `README.md` |
| `results-php/ph66-hashdel-uncompared.json` | the measurement record — 32 cells |
| `results-php/gate/ph66-hashdel-uncompared.json` | the gate record — **`verdict: PASS`** |
| `results-php/tables/ph66-hashdel-uncompared.md` | the rendered table |
| `results-php/preflight/ph66-hashdel-uncompared.preflight.json` | the php-side preflight certificate |
| `.tasks-php/task_cost.py` | **modified** — §1.3's two repairs |
| `results-php/preflight/_norow.preflight.json` | **modified** — expected, and in no digest (§F6b) |

⛔ **Nothing else in the tree is touched.** `git status` shows exactly those,
`.tasks-php/contract_audit.py` is back to its committed bytes (§7.7), and the PAT
bracket is unmoved at `66/0`.

**No `git add` or `git commit` was run.**

### 9.1 The controls, and what each one would catch

| control | arms | what a green line means |
|---|---|---|
| `ladder.py` | 3 | the six cells' folds, side by side, on all eight inputs — **P1** |
| `key_identity.py` | 3 | the key-identity obligation VERIFIES against the R1h predicate and FAILS on the POSTCONDITION against 5.0.0's, with a vacuous-obligation control — **P3** |
| `differential.py` | 6 | the shipped C against all three `model.py` spellings over 94 off-corpus windows, with five must-fire mutations |
| `r1h_apply.py` | 7 | the R1h binding re-derived from the tarball BYTES, with three must-fire mutations |
| `inside_share.py` | — | 32 (cell × opt × input) triples, both C columns, **both** optimisation levels |
| `spellings.py` | 5 | every backticked span in `spec.md` pins what it claims to — 32 obligations, 0 unsatisfied |
