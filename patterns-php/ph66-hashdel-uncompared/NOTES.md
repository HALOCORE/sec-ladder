# ph66-hashdel-uncompared — notes

Measurements, and the arguments that are not in `spec.md`'s hashed block.
`README.md` is the reader's entry point; this file is the evidence.

⚠ **Every figure here is an EVENT**: it was produced by the named command on the
named date against the tree at that moment. `PROTOCOL.md` rule 6's addendum says
to re-run rather than to trust the prose.

---

## 1. The mechanism, in one paragraph

`Zend/zend_hash.c:464-465`, `zend_hash_del_key_or_index`'s chain walk:

```c
464  if ((p->h == h) && ((p->nKeyLength == 0) || /* Numeric index */
465      ((p->nKeyLength == nKeyLength) && (!memcmp(p->arKey, arKey, nKeyLength))))) {
```

A numeric bucket is marked by `nKeyLength == 0` — upstream says so itself at
`:387` — so for a numeric bucket the **left disjunct fires and the key is never
compared at all**. Hash equality alone stands in for key identity.

The trigger needs **no preimage**. `_zend_hash_index_update_or_next_insert`
stores `p->h = h` with `h` the *raw user-chosen index* (`:388`), so running
DJBX33A **forwards** on any string key gives the integer index that key will
destroy. `zend_inline_hash_func("abc", 4) == 6385036779`.

---

## 2. §A3a — reachability, EXECUTED on a real PHP 5.0.0 CLI

**Run 2026-09-16**, `sh .tasks-php/probes/ph66_key_identity.sh`, on
`/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/bin/php-5.0.0-mysql-webext`.

| cell | fixture | rc | survivors |
|---|---|---|---|
| A | victim alone | **0** | `'other'` |
| B | **a reference still holds the victim** | **0** | `'other'` |
| C | victim is an array | **0** | `'other'` |
| ⭐ **D** | `"abc"` inserted **before** the numeric index | **0** | **`'abc'`** |
| E | benign — every key really present | **0** | `6385036779,'other'` |

Re-run of the manager's premise C and it reproduces exactly. **Cell D is the
headline**: `unset($a["abc"])` leaves `'abc'` in the array and destroys the
unrelated live element instead — *the key you named survives, the key you never
named dies, PHP exits 0 with a clean stderr.*

⚠⚠ **THE TWO CAUTIONS §A3a REQUIRES, REPEATED HERE.**

1. **Say which build.** That binary is php-in-safe-rust's **oracle build**
   (mysql + webext) and **not** a museum-default 5.0.0. ⛔ **Its flags are NOT
   recorded in a `.buildinfo`** — only the `-O3lto`/`-maxlto` siblings carry
   one — so this note deliberately **does not name flags** (`F139`: the caution
   whose whole point is *say which build* once named the wrong one).
2. **A clean run is not evidence of absence** (`F3`). Every cell above exits 0,
   and that is this row's *result*, not a failed reproduction — but it remains
   true that a different build, a different `-O` or a sanitizer could show
   something this one does not.

⭐ **REPRODUCIBILITY (§A3a obligation 4):** the probe was run **three times** on
the same binary, into three separate workdirs, and gave byte-identical output
every time (the only textual difference is the workdir path the probe echoes). This row has the *third* of
§A3a's three categories and a fourth the list does not name: **a stable, silent,
value-only result** — no signal to be stable or flaky about, and no `si_addr` to
vary under ASLR. `probes/segaddr.c` was **not** run and there is nothing for it
to catch.

---

## 3. ⛔⛔ Every free in this kernel is a correct free — and how that is checked

`spec.md`'s §2.7 constraint is the row's whole research value, so it is checked
three ways rather than asserted:

1. **By construction, from the C.** `:466-489` unlinks the bucket from the
   bucket chain, from the global list **and** from `ht->pInternalPointer` before
   `pefree(p, ...)`. The payload is a non-zero tagged integer, so
   `if (!p->pDataPtr) pefree(p->pData, ...)` is never taken and the interior
   pointer `&p->pDataPtr` is never freed — the one way this kernel *could* have
   introduced UB the C original does not have, and the divergence ledger's
   `pData is a non-zero tagged integer` entry is there for exactly that reason.
2. **ASan + UBSan, gate stages 7 and 7h**, on every input including every
   adversarial one. `model.py::sanitizer_expect` returns `clean` unconditionally
   and derives it rather than tabulating it.
3. **Miri, gate stage 6**, on `unsafe.rs`. See §7, prediction P2.

⚠ In the Rust rungs "free" is "unlink and stop being reachable" — the arena slot
survives. **On `ph64` that substitution was observable** (its cursor read a link
out of a freed block, so the arena changed what the read returned); **here it is
not**, because nothing ever reads a freed bucket. `controls/differential.py`
measures the two computing the same function over 94 off-corpus windows.

---

## 4. §A3a obligation 5 — the R1h post-image, and ⛔ WHERE THE TASK BRIEF IS WRONG

**Run 2026-09-16**,
`bash .tasks-php/probes/rebuild_hardened_php.sh --label ph66 --patch controls/b73349dbe4e9.patch --trigger <cell D>`:
cold build **30 s**, incremental rebuild after the patch **617 ms**, 60 MB, no
sudo, no network. The artefact is deleted; the script rebuilds it.

| trigger | pre-image (pristine 5.0.0) | post-image (R1h `b73349dbe4e9`) |
|---|---|---|
| **cell D** | `rc=0  count=1 survivors='abc'` | `rc=0  count=1 survivors=6385036779` |
| **cell A** | `rc=0  count=1 survivors='other'` | `rc=0  count=2 survivors=6385036779,'other'` |
| **benign** | `rc=0  count=2 survivors=6385036779,'other'` | **identical** |

✅ The patch applies to the pristine tarball **verbatim**, `-p1`, rc 0, no fuzz,
one file, no backport. `controls/r1h_apply.py` re-derives that on every run.

> ### ⛔⛔ `TASK_PHP_062` §2.5 AND `ROW13_001` §7 ATTRIBUTE `count=1 → count=2` TO **CELL D'S SCRIPT**, AND IT IS **CELL A'S**
>
> Both documents print the table as
> *"adversarial — `$a[6385036779]` live, `unset($a["abc"])` … `count=1`, victim
> destroyed → `count=2`, victim survives"* and label the row **cell D's script**.
> Measured above: **on cell D the count is 1 on BOTH sides.** It has to be — cell
> D's array holds two elements and one delete removes one of them either way;
> what the repair changes is **which** one. The `count=1 → count=2` reading
> belongs to **cell A**, where the named key is absent so the repaired delete
> removes nothing.
>
> ⭐ **This is not a typo, it is the row's own hazard one level up.** A row that
> had quoted `count` alone on cell D would have reported *"no change across the
> repair"* about a run that flips the answer completely — which is precisely the
> failure `rebuild_hardened_php.sh`'s own header warns about when it says an
> rc-only report *"reads 'no change' across a repair that in fact flips the
> observable"*. The script was repaired for `rc`; the **brief's table repeated
> the same mistake one column over, with `count`.** ▶ **The observable on this
> row is the SURVIVOR LIST. Not `rc`, and not `count`.**

### 4a. ⭐⭐ Obligation 5 was DISCHARGED ON A ROW THE PROTOCOL EXCUSES — and `F141` is right

§A3a obligation 5 is *"REQUIRED, GATED ON 'the pre-image run faulted'. If the
row's trigger did not fault, this is vacuous and you skip it."* **This row's
pre-image run does not fault — `rc=0` on both sides, forever — so the protocol
as written excused it. It was run anyway, and it produced the table above.**

▶ **On the substance I agree with `F141`, and I would put it more strongly than
the manager did.** The gate is stated on the wrong predicate *and the predicate
it is stated on is not even a proxy for the right one.* The obligation's own
rationale box says what it buys: *"it makes the upstream fix's efficacy
measurable on real PHP."* Efficacy is a question about **the observable moving
across the repair**, and `rc` is one observable among several. On `ph97` the
observable happened to be `rc` (139 → 0); on `ph66` `rc` is constant and the
survivor list moves. **Gating on `rc` gates on the instrument, not on the
question.**

▶ **The repair I would propose** (and it is a manager decision, not mine to
land): re-word the gate as *"REQUIRED whenever the row can name an observable
that the repair is expected to move — which is every row, because a row that
cannot name one has no R1h claim to make."* That is unconditional in practice
and says why. ⓘ §1's own number is the scale: **61.3 % of temporal rows do not
fault**, so the current wording is vacuous on the majority of the axis that owes
15 of the 25 remaining rows.

---

## 5. The predicate census (item 139), and what I think the two-column reading is worth

`python3 .tasks-php/probes/ph66_djbx33a_collide.py`, re-run 2026-09-16, selftest
**PASS** (N1–N8):

| kind | n | lines |
|---|---|---|
| `string` (conjunct) | 5 | 215, 280, 854, 881, 906, 932 → *see below* |
| `numeric` (conjunct) | 3 | 356, 955, 976 |
| ⛔ `dual` (disjunct) | **1** | **464 — the defect** |

⚠ **The table's own count**: the probe reports 6 `string` and 3 `numeric`, i.e.
**9 of 10 already spell the R1h's required-conjunct form**. `ROW13_001` §6
predicted `ph66` would be `F133`(i)'s **counterexample** and it is `F133`(i)'s
**strongest positive** — a higher ratio than `ph96`'s 7-of-23.

▶ **Does the manager's two-column reading — *"the repair's SPELLING was present
nine times; the repair's PROBLEM was present nowhere"* — hold up from inside the
row?** **Yes, and building the row sharpened it in one place and weakened it in
another.**

* ✅ **Sharpened.** The nine are not merely *single-kind*; they are **structurally
  unable to face `:464`'s choice**, and the kernel makes that concrete.
  `_zend_hash_add_or_update` takes `arKey`/`nKeyLength` and nothing else;
  `_zend_hash_index_update_or_next_insert` takes `h` and nothing else. **Neither
  has a parameter that could express the other kind.** `zend_hash_del_key_or_index`
  has `flag`, and `flag` is the whole difference. So the split is not a
  statistical observation about nine siblings — it is a **type-level** fact about
  one signature, and it is visible in the extraction without any census at all.
* ⚠ **Weakened.** The row also shows that the nine are **not evidence of
  intent**. `_zend_hash_add_or_update`'s conjunct is there because a string
  lookup *has* to compare lengths before `memcmp`; it would be a bug without it.
  So *"nine already knew"* over-reads: nine did the only thing their signature
  allowed. ▶ **`F133`(i) as worded — *an R1h is evidence about what was CHOSEN,
  not about what was KNOWN* — survives, but this row is a weak instance of it,
  not the strong one the 9-of-10 ratio suggests.** The ratio counts sites that
  had no choice.

⭐ **And one thing the census does not say, which the row does.** There is a
TENTH place PHP 5.0.0 decides a key's kind and it is not in the census at all:
`HANDLE_NUMERIC` (`zend_hash.h:283-317`), which `zend_symtable_del` applies
*before* hashing. `spec.md`'s `idiom.forbidden[0]` pins it absent on every rung,
because a rung that acquired it would settle the kind upstream of the predicate
and delete part of the row.

---

## 6. ⭐⭐ R5's obligation, and the corpus labeller's own note

`CATALOGUE.md` carries `I7/O2 + I7/O3` and **this row does not edit it**. But
`I7/O2` and `I7/O3` are *refcount* obligations, and a Verus proof about
refcounts is not the proof this row needs: the defect never miscounts a holder,
it picks the wrong bucket.

⭐ The corpus's own labeller reached the same conclusion from the other
direction. `paper/_old_story/invariants-166.json`, `cases[98]`, `notes`, quoted
in full because it is a **corpus artefact and not a manager opinion**:

> *The true primary is arguably a NEW entry:* **`NEW:container-key-identity`** —
> *"a hash-table operation acts on the bucket whose key equals the requested key
> in both key kind and key bytes, and on no other bucket"* — *which by the
> restatement test is **T1-universal** (no PHP noun) and **construct-bound** (a
> single defective predicate at `zend_hash.c:464`; every sibling lookup in the
> same file is correct). I did not file it as the label because the rule says
> NEW only if genuinely nothing fits.*

The same notes record that the labeller's `T3`-honesty sub-rule **fires here and
has nowhere to send the case** — *"this case's counts are not the sharing
oracle, they are pure lifetime"* — which the labeller offers as evidence against
`I7` being a single entry.

▶ **So R5's obligation is stated as the labeller's property**, and
`controls/key_identity.py` builds it in Verus rather than arguing it:

```
r != NIL ==> a[r].nkl == nkl && (nkl == 0 || a[r].k == k)
```

*the bucket the walk selects has the requested key KIND, and — when a key was
named at all — the requested key BYTES.*

⚠ **And the corpus's `CWE-416` does not survive contact with the measurement
either.** `index.csv` files LOGIC-001 as a use-after-free in the `refcount-logic`
family; §2 above shows five cells, one of them holding a live reference to the
victim, all exiting 0 with nothing read after it is freed. The corpus's own
`crashes_pristine_5_0_0` column agrees — it reads `n/a (non-crash class)`.
`PROTOCOL_PHP.md` §A4: reproducing a different category is **a finding to state,
not a failure to hide**. The `cwe` field carries `CWE-416` unchanged because the
corpus's columns are carried across by design.

---

## 7. ⭐⭐⭐ The five registered predictions, scored

### P1 — *R1, R2, R3 and R4 all reproduce the defect, and their benign `u64` values agree exactly.*
### ✅ **SURVIVES, AND MORE STRONGLY THAN IT WAS STATED.** R5 too, and on the ADVERSARIAL inputs as well as the benign ones.

`python3 controls/ladder.py --selftest`, O3/isolated, 2026-09-16 — **every value
is `rc=0`**:

| rung | cella | celld | deep | many | nowin | orderctl | large | small |
|---|---|---|---|---|---|---|---|---|
| R1 `c/kernel.c` gcc | 5553442908994609152 | 3677079714565854208 | 14964600241287891968 | 930842079897528320 | 0 | 10574059460825272320 | 11734148439434793093 | 7365650064901814160 |
| R1 `c/kernel.c` clang | *same* | *same* | *same* | *same* | *same* | *same* | *same* | *same* |
| R2 `safe_naive.rs` | *same* | *same* | *same* | *same* | *same* | *same* | *same* | *same* |
| R3 `safe_tuned.rs` | *same* | *same* | *same* | *same* | *same* | *same* | *same* | *same* |
| R4 `unsafe.rs` | *same* | *same* | *same* | *same* | *same* | *same* | *same* | *same* |
| R5 `verus.rs` | *same* | *same* | *same* | *same* | *same* | *same* | *same* | *same* |
| **R1h** gcc | **16310587633836665856** | **10574059460825272320** | **17954956657160630272** | **4226173720395463680** | 0 | 10574059460825272320 | 11734148439434793093 | 7365650064901814160 |
| **R1h** clang | *same as R1h gcc* | | | | | | | |

**Six defective cells across three languages agree on 8 of 8 inputs. The
hardened cell separates on 4 of the 6 adversarial inputs and agrees on both
measured ones.** The prediction's falsifier — *any rung below R5 whose
adversarial fold differs from R1's* — did not occur, on any input, at either
optimisation level.

⭐ **This is the row's reason for existing, and `CLAUDE.md` Don't 6 is what makes
it publishable**: *the first defect in this corpus that the entire safety stack
is blind to.* Safe Rust, `unsafe` Rust and Verus all express a wrong boolean
exactly, and none of them has any reason to refuse it. A ladder whose every rung
buys safety is a ladder that has never measured a defect the rungs do not
address.

⭐ One datum worth reading twice: **`adversarial-celld` under R1h equals
`adversarial-orderctl` under every rung** (`10574059460825272320`). The repaired
delete, given cell D's insertion order, returns exactly what the *correct* order
returns — which is the sharpest statement of what the repair buys.

### P2 — *Miri reports nothing on the adversarial input.*
### ✅ **SURVIVES.** See §7a for the gate's own line.

There is no UB to detect: every free is a correct free (§3). The falsifier — any
Miri diagnostic — would have meant the kernel introduced UB the C does not have,
and it did not occur.

### P3 — *R5 is the only rung that can refuse it, and its obligation is §2.6's key-identity property.*
### ⚠⚠ **SPLIT: THE SECOND HALF SURVIVES, THE FIRST IS TRUE ONLY UNDER A CONDITION THE PREDICTION DID NOT STATE — AND ITS OWN FALSIFIER IS SATISFIED BY THE SHIPPED `verus.rs`.**

The prediction's falsifier reads *"an R5 that verifies with the defective
predicate in place."* **`verus.rs` is exactly that: 49 verified, 0 errors, with
`:464`'s disjunct in the exec code.** It has to be — the shipped `ensures` is
`r == hash_fold(...)` and `hash_fold` is a spec function that *carries* the
defect, which is what makes R1…R5 comparable at all.

▶ So the honest scoring is:

* ⛔ **P3 as worded is REFUTED.** Verus verifies the defective rung.
* ✅ **P3's SUBSTANCE survives, and is measured.** `controls/key_identity.py`,
  three arms, 2026-09-16:

  | arm | predicate | obligation | result |
  |---|---|---|---|
  | N1 | `b73349dbe4e9`'s | key-identity | **VERIFIES** |
  | N2 | PHP 5.0.0's | key-identity | **FAILS — `postcondition not satisfied`** |
  | N3 | PHP 5.0.0's | vacuous | **VERIFIES** |

  N3 is the arm that makes N1-vs-N2 attributable to the **predicate** and not to
  the file, and without it the pair proves nothing.

⭐⭐ **What that actually shows, and it is a sharper claim than the prediction
was.** Verus is not *"the rung that refuses the defect"*. Verus is **the rung
that can be ASKED**. R2, R3 and R4 have no place to put the question; R5 does,
and the answer depends entirely on which obligation is written. ▶ **The thing
this row measures is not that a proof catches the bug — it is that the proof
obligation is where the bug becomes sayable, and that choosing the obligation is
a human act the toolchain does not perform.** That is why §6 quotes the corpus
labeller: *somebody had to decide that `I7/O2` was the wrong property*, and no
gate stage in this repository does that.

⚠ **Which part resists, precisely** (the prediction asked): nothing resists at
the Verus level — the obligation is eleven tokens and verifies in one recursive
proof with no lemmas. **What resists is attaching it to the shipped rung.** To
make `verus.rs` itself refuse, its `ensures` would have to be stated against a
*correct* specification of delete rather than against `hash_fold`, and then R5
would no longer compute the same function as R1…R4 and the row's cross-rung
checksum would be comparing two programs. **That is a real tension in the
ladder's design and this row is where it shows.**

### P4 — *the R1h is NOT free at `O0` and is within noise at `O3`.*
### ⚠⚠ **SPLIT: the first half SURVIVES but only in family B, the second half is REFUTED — and getting this right required correcting my own first reading.**

Full figures, both statistics, both C columns, both levels: §9.4 and §9.5.

* ✅ **First half — *not free at `O0`* — SURVIVES, in family B.**
  `marginal_ir_per_call`, O0/isolated: gcc **`+4.00`** (`small`) and **`+6.12`**
  (`large`); clang **`+5.00`** and **`+9.69`**. The extra conjunct costs at `O0`.
  ⚠ **But it is INVISIBLE to `A1` on all four cells**, because neither compiler
  inlines `zend_hash_del_key_or_index` into `kernel` at `-O0`, so the whole
  defect is in a callee: `c-gcc` and `c-gcc-h` report the same `33,968,756` Ir
  and the same `md5_fn 0123a7ac`. ⛔ And `O0` figures are **lowering readings and
  not performance claims** (`.memory/02-bench-rules.md`), which is also why
  `php50_align_sweep.py` hard-codes `OPT = "O3"` — **so no `O0` magnitude here is
  swept and none is published.**
* ⛔ **Second half — *within noise at `O3`* — REFUTED. The sign is stable,
  negative, and the same on both compilers: the repair is CHEAPER.** Family B,
  O3/isolated, all four **SIGN-STABLE** over a full 32-residue pad sweep: gcc
  `−3.20` / `−19.83`, clang `−2.03` / `−12.00`. **One magnitude clears §B5 and
  it is `c-gcc → c-gcc-h` on `large.bin`, `−19.83 Ir/call`**; the other three are
  published as signs only.

> ⛔⛔ **AND MY OWN FIRST READING OF THIS WAS WRONG, WHICH IS WHY §9.3 EXISTS.**
> `A1` reads **exactly `+0.0000`** for `c-clang` at O3, and I first wrote that up
> as *"R1 and R1h compile to the byte-identical kernel — a 0.00 that is identity
> and not noise."* **The `kernel` symbols ARE byte-identical. The programs are
> not.** `nm` says why in one line: clang keeps `zend_hash_del_key_or_index`
> **out of line** (`t zend_hash_del_key_or_index`, 0x3a5 bytes in R1 against
> 0x3a2 in R1h) where gcc inlines it, so the entire repair sits in a symbol `A1`
> does not count — and family B, which is whole-program, separates the two by
> `−2.03` and `−12.00 Ir/call`.
> ⭐ **`c-clang`'s `inside_share_W` on those cells is 65.31 % and 51.31 %.** A
> healthy share did not predict it, and could not: **what decides whether `A1`
> resolves a difference is whether THE DIFFERENCE lands inside the symbol, not
> how much of the cell does.**

▶ **The mechanism, since a cost with no mechanism is an incomplete row**
(`PLAN_PHP.md` §7 rule 12). R1 tests `p->nKeyLength == 0` first and
`p->nKeyLength == nKeyLength` second; R1h swaps them. For a *string* bucket both
orders cost two length comparisons and nothing moves. For an **index** delete
meeting a *string* bucket — which the benign corpus does constantly, because the
prologue's `del_idx` walks past a same-hash string bucket by construction — R1
costs two length tests and R1h one, so **R1h skips work**. At `-O0` that saving
is swamped by the extra comparison being evaluated per chain step before the
short-circuit is scheduled; at `-O3` the scheduler keeps the saving.

### P5 — *the `verbatim` tier does NOT survive the narrowing.*
### ⛔ **REFUTED. The tier survives, and `provenance.py` scores it 84 %.** See §10.

---

## 7a. Gate lines, quoted from the record

From `results-php/gate/ph66-hashdel-uncompared.json` (first full run,
2026-09-16), the two stages that score P2:

* **Miri, stage 6** — `unsafe.rs`, **all eight inputs**, `n_iters` rewritten to
  4 by `check.py`: every entry reads `"exit": 0, "ub": false, "leak": false`,
  `stderr` empty, and `stdout == model_stdout` on every one. ⭐ **Including
  `adversarial-celld`, `adversarial-cella`, `adversarial-deep` and
  `adversarial-many` — the four inputs on which the defect fires.** Miri sees
  nothing because there is nothing to see.
* **ASan + UBSan, stages 7 and 7h** — `"expect": "clean"`, `"fired": false`,
  `"exit": 0` on **every input for both the R1 and the R1h C rungs**. Stage 7h
  additionally records, on each of the four defect-firing inputs,
  `"adversarial": true` with R1h's `stdout` differing from the model's — which
  is the gate printing this row's whole result as a side effect of a sanitizer
  check.

⚠ **`F3` still applies**: a clean sanitizer run is not evidence of absence. What
makes the absence *derivable* here is §3's first argument, not these two lines.

---

## 8. ⚠⚠ WHAT THIS FIXTURE CANNOT DO — the `memcmp` is not a discriminator

**`controls/differential.py`'s first draft mutated the key comparison to one
byte and DID NOT FIRE ON A SINGLE WINDOW.** That is recorded rather than
repaired away, because it is a property of the construct and not of the probe.

On this kernel's domain **`memcmp(p->arKey, arKey, nKeyLength)` never decides
anything.** Every site that compares key bytes — `:215`, `:465`, and the
hardened `:463` — has already required `p->h == h` **and**
`p->nKeyLength == nKeyLength`, and the 64 keys have pairwise distinct 64-bit
DJBX33A hashes (`inputs/gen.py::_check_keys` asserts it). So the comparison is
**executed on every match and always returns 0**.

⛔ **And it cannot be fixed by widening the fixture.** Making `memcmp` decide
needs two *distinct* keys with an *equal* 64-bit DJBX33A hash — which is exactly
the object `CATALOGUE.md`'s *"compute the preimage"* instruction asked for and
which `.tasks-php/probes/ph66_djbx33a_collide.py` shows is not constructible:
every `33^k` is odd, hence a unit mod 2^64, so there is no digit structure to
lift, and a birthday search is ~2^32 work. ⭐ **The same fact that makes this row
cheap to trigger makes this one arm of it unreachable.**

▶ **What follows, and it is the useful half.** The test that *does* discriminate
on this domain is the **length** test, `p->nKeyLength == nKeyLength` — and that
is precisely the conjunct `b73349dbe4e9` hoists. So the row's defect turns on
the *kind* comparison and not on the *bytes* comparison, and the labeller's
phrase *"in both key kind and key bytes"* is, on this construct, carried
entirely by its first half. `controls/differential.py`'s `N2b` mutates the length
test and is caught in 5 windows; `N2a` mutates the *fold* over the key bytes and
is caught in 82, which is what keeps the packed-`u64` substitution demonstrated
rather than asserted.

⚠ **This narrows what the row can claim about real PHP.** In real PHP two
distinct strings *can* share a DJBX33A hash — that is the 2011 hash-collision
DoS — and there `memcmp` is the discriminator. This kernel cannot reach that
state, and no fixture of this shape can.

---

## 9. The numbers

### 9.1 The two statistics, named, and the one that is not published

* **`A1` = `kernel_exclusive_ir`** — callgrind per-function exclusive for the
  `kernel` symbol, from `results-php/ph66-hashdel-uncompared.json`.
* **Family B = `marginal_ir_per_call`** — `(Ir at 200 iterations − Ir at 100) / 100`,
  a WHOLE-PROGRAM slope, from `results-php/gate/ph66-hashdel-uncompared.json`.
* **`W1` (whole-program level) is NOT published** on this row at all.

⚠ **Every figure below names five things**: statistic · input · opt/mode · base ·
and **both C columns**, never one (`F108`).

### 9.2 `inside_share` per cell, as a matrix, BEFORE the statistic is chosen

`python3 controls/inside_share.py`, **32 (cell × opt × input) triples, both C
columns, BOTH optimisation levels**. ⛔⛔ **WHICH `inside_share`:** this is the
**`W`** one, `100 × A1 / callgrind's own summary total` — **not** `F74`'s
`(A1/n_iters) / marginal_ir_per_call`, which is arithmetic over two committed
records. Both are printed side by side (`F129`).

| cell | O3 small | O3 large | O0 small | O0 large |
|---|---|---|---|---|
| `c-gcc` | 75.95 % | 58.02 % | 17.97 % | 16.42 % |
| `c-gcc-h` | 75.94 % | 58.02 % | 17.96 % | 16.42 % |
| `c-clang` | 65.31 % | 51.31 % | 19.02 % | 17.26 % |
| `c-clang-h` | 65.34 % | 51.32 % | 19.01 % | 17.26 % |
| `safe_naive` | 62.97 % | 71.81 % | 11.02 % | 13.13 % |
| `safe_tuned` | 65.70 % | 76.40 % | 14.30 % | 16.05 % |
| `unsafe` | 65.20 % | 81.78 % | 8.15 % | 9.29 % |
| `verus` | 64.92 % | 79.20 % | 8.48 % | 9.25 % |

**32 independent per-cell ratios, NOT a comparison. W range 8.15 % .. 81.78 %.**
⛔ **`F74`'s two-condition bar is NOT A GATE** (settled at `_059`) and nothing
below is withheld on the strength of a share.

### 9.3 ⭐⭐⭐ AND THE MATRIX IS USED TO EXPLAIN A DISAGREEMENT — WHICH IS EXACTLY WHAT IT IS FOR

**`A1` and family B disagree on `c-clang`, and the share does not predict it.**

| | `A1` (R1h − R1) | family B (R1h − R1) |
|---|---|---|
| `c-clang`, O3/isolated, `small.bin` | **`+0.0000`** | **`−2.03` Ir/call** |
| `c-clang`, O3/isolated, `large.bin` | **`+0.0000`** | **`−12.00` Ir/call** |

`c-clang`'s `inside_share_W` on those two cells is **65.31 %** and **51.31 %** —
perfectly healthy numbers, and the reading *"A1 sees most of the cell, so A1 can
resolve this difference"* is **false**.

⭐ **The reason is one `nm` line.** At `-O3` **clang keeps
`zend_hash_del_key_or_index` OUT OF LINE** — `t zend_hash_del_key_or_index`,
**0x3a5 bytes in R1 against 0x3a2 in R1h** — so the `kernel` symbols are
byte-identical (`md5_fn 8e090858` on both) and **the entire repair sits in a
symbol `A1` does not count.** **gcc inlines it** (`kernel` 0x166a against
0x168e) and `A1` does see it.

▶ **This is `F74`'s failure mode in a new place, and the new part is that it is
not about the share at all.** `_059`'s counterexample was a cell whose `A1` read
`+0.0000` against a moving whole-program figure; here the same thing happens
with a *healthy* share, because what decides whether `A1` resolves a difference
is **whether THE DIFFERENCE lands inside the symbol**, not how much of the cell
does. ⚠ **`results/tables/*.md` already says this in general terms** (*"whatever
a rung calls out to lands in no column of this table at all"*); this row is an
instance where it changes a published sign from *nothing moved* to *it moved and
you were looking in the wrong symbol*.

### 9.4 R1 vs R1h — both C columns, both statistics, both levels

| opt | statistic | gcc `small` | gcc `large` | clang `small` | clang `large` |
|---|---|---|---|---|---|
| **O3** | `A1` | **−3.241** | **−18.414** | `+0.000` ⚠ | `+0.000` ⚠ |
| **O3** | family B | **−3.20** | **−19.83** | **−2.03** | **−12.00** |
| O0 | `A1` | `+0.000` ⚠ | `+0.000` ⚠ | `+0.000` ⚠ | `+0.000` ⚠ |
| O0 | family B | +4.00 | +6.12 | +5.00 | +9.69 |

*(base: `c-gcc` and `c-clang` respectively; `isolated`; Ir/call; negative means
R1h is cheaper.)*

⚠⚠ **THE `O0` ROWS ARE LOWERING READINGS AND NOT PERFORMANCE CLAIMS**
(`.memory/02-bench-rules.md`), and that is also why `.tasks-php/php50_align_sweep.py`
hard-codes `OPT = "O3"` — so **no `O0` family-B magnitude on this row is swept,
and none is published.** What the `O0` row is good for is its SIGN: at `O0` the
extra conjunct costs, at `O3` it saves.

⚠ **Every `+0.000` marked ⚠ above means *the difference is not in this symbol*,
not *there is no difference.*** At `O0` neither compiler inlines the delete into
`kernel`, so `A1` is blind on all four cells; `c-gcc` and `c-gcc-h` report the
same `33,968,756` and the same `md5_fn 0123a7ac`.

### 9.5 §B5 — the two verdicts per pair, from a full 32-residue pad sweep

`python3 .tasks-php/php50_align_sweep.py --row ph66-hashdel-uncompared --pads 32`,
O3/isolated:

| pair | input | median | range (step) | \|d\|/step | **magnitude** | **sign** |
|---|---|---|---|---|---|---|
| `c-gcc → c-gcc-h` | small | −3.20 | 1.89 | 1.69 | ⛔ **NOT RESOLVABLE** | ✅ SIGN-STABLE |
| `c-gcc → c-gcc-h` | large | −19.83 | 4.44 | 4.47 | ✅ **RESOLVABLE** | ✅ SIGN-STABLE |
| `c-clang → c-clang-h` | small | −2.03 | 1.89 | 1.07 | ⛔ **NOT RESOLVABLE** | ✅ SIGN-STABLE |
| `c-clang → c-clang-h` | large | −12.00 | 4.56 | 2.63 | ⛔ **NOT RESOLVABLE** | ✅ SIGN-STABLE |

▶ **So exactly ONE family-B magnitude is published on this row:
`c-gcc → c-gcc-h` on `large.bin`, `−19.83 Ir/call`.** The other three R1/R1h
pairs are published as **SIGNS ONLY** — the sign is stable on all four, and it
is **negative at O3**: the repair is cheaper.

⛔⛔ **AND ONE FIGURE IS WITHHELD BY §B5's OWN NAMED RULE.** *"Never publish a
family-B figure for an `unsafe → verus` pair on a row whose kernel allocates."*
**This kernel allocates** (§9.7), and the pair behaves exactly as `ph64`'s did:
`unsafe → verus` measures **`−25.97` on `small` and `+792.42` on `large`** — it
**flips sign between the two inputs** while `A1` is `−0.96 %` and `−0.53 %`, both
negative. ⭐ **That is the rule's second measured instance and it confirms it on
an independent row.** `safe_tuned → unsafe` flips too (`+104.11` / `−1789.32`).

### 9.6 The ladder, `A1`, both C columns — and the allocator label §B1a requires

⚠⚠ **EVERY CROSS-LANGUAGE FIGURE IN THIS TABLE INCLUDES ALLOCATOR WORK ON THE C
SIDE AGAINST ARITHMETIC ON THE RUST SIDE** (§9.7). The row publishes no bare
C-vs-Rust headline without that label.

`A1` Ir/call, **O3/isolated**:

| rung | `small` | vs `c-gcc` | vs `c-clang` | `large` | vs `c-gcc` | vs `c-clang` |
|---|---|---|---|---|---|---|
| R1 `c-gcc` | 3194.49 | — | +11.02 % | 23104.63 | — | +7.31 % |
| R1 `c-clang` | 2877.49 | −9.92 % | — | 21530.50 | −6.81 % | — |
| R2 `safe_naive` | 3383.78 | +5.93 % | +17.59 % | 25506.64 | +10.40 % | +18.47 % |
| R3 `safe_tuned` | 3150.86 | −1.37 % | +9.50 % | 23619.22 | +2.23 % | +9.70 % |
| R4 `unsafe` | 3194.09 | −0.01 % | +11.00 % | 23822.40 | +3.11 % | +10.64 % |
| R5 `verus` | 3163.35 | −0.98 % | +9.93 % | 23696.82 | +2.56 % | +10.06 % |

⭐ **THE SAME-LANGUAGE RATIOS ARE THE CLEAN ONES** — R2/R3 and R4/R5 allocate
identically, so the allocator term **cancels** (§B1a decision 4):

| ratio | `small` | `large` | what it prices |
|---|---|---|---|
| **R2 → R3** | **−6.88 %** | **−7.40 %** | what the three tunings buy: `Option<u32>` → a `NIL` sentinel, one bound-checked index per chain step instead of one per field, and a single-word key compare |
| **R3 → R4** | +1.37 % | +0.86 % | ⚠ the **bounds checks cost NOTHING here and removing them costs a little** — R4 is *dearer* than safe R3 on both inputs |
| **R4 → R5** | −0.96 % | −0.53 % | the proof, and it is **negative**: R5 is cheaper than R4 |

⛔ **R3 → R4 is the reading worth stopping on.** Removing every bounds check from
the bucket arena made the kernel **1.37 % / 0.86 % DEARER** in `A1`, not cheaper.
▶ **The mechanism, from the disassembly** (§F8 wants one): R3's chain walk binds
`let n = &self.a[p as usize];` once and LLVM hoists the single bounds check out
of the inner comparison, then keeps `n` in registers; R4's `nref` returns a
`&Node` the optimiser must re-load through because the `get_unchecked` is opaque
to the same alias analysis. **The bound was already free; what `unsafe` removed
was an analysis, not a branch.** ⚠ The two cells' static counts agree with that
— R3 750 instructions against R4 791 — and the family-B slope agrees in sign
(`safe_tuned → unsafe` is `+104.11` on `small`), **but that family-B pair flips
sign on `large` and is therefore NOT published as a magnitude** (§9.5).

### 9.7 ⚠⚠ §B1a — this row's allocation order, declared

`c/kernel.c` makes **one `ecalloc` for `ht->arBuckets`, one `pemalloc` per
bucket INSERTED and one `pefree` per bucket DELETED, per kernel call**, plus a
`zend_hash_destroy` sweep after the tally is read. **That is `O(nrec)` per call
and §B1a's precondition does NOT hold.**

⛔ **It is a FINDING and never a refusal** (§B1a decision 1, `CLAUDE.md` Don't 6).
What it costs is stated above: cross-language figures are labelled, same-language
ratios are clean. ⭐ **And the allocator is not background here — it is half the
oracle**: the tally is folded into the u64, so a delete that removed a bucket and
a delete that removed nothing differ in `n_free` as well as in the surviving-key
list. The truncations T1/T2/T3 do **not** fire (every request is 73..79 bytes or
the `8 × nTableSize` table), so this row exercises the **cache** half of
`emalloc_shim.h` and none of the overflow half.

### 9.8 What the marginal scales with

`d(Ir)/d(work)` at O3/isolated: `c-gcc` 79.19, `c-gcc-h` 79.15, `c-clang` 83.52,
`c-clang-h` 83.50, `safe_naive` 66.76, `safe_tuned` 57.82, `unsafe` 53.62,
`verus` 55.44 Ir per window byte. ⚠ **The per-record work is not constant** and
the bucket TABLE is sized from the same `nrec`, so chain length — and therefore
walk cost — is itself a function of the denominator. That is why `large`'s
Ir/call is ~7.4× `small`'s while its window is only 7.8× larger and its record
count 8.1×.

---

## 10. The tier, and why `verbatim` survives

`provenance.py` reports **kernel overlap 84 % (144/171 excerpt lines)** against a
`verbatim` expectation of 50 %, over the union of **ten** cited spans. Per-span:
97 / 100 / 93 / 93 / 100 / 36 / 85 / 86 / 79 / 93 %.

⚠ **Read the 36 %.** It is span 5, `UPDATE_DATA` + `INIT_DATA`, and it is low
because the kernel keeps only the `nDataSize == sizeof(void*)` arm of each macro
— which is the arm a PHP array takes, and the only one any call site reaches.
That is declared as a `projection`, not smoothed over.

⚠ **And read the residual the tool prints**: **1 preprocessor condition the
heuristic cannot evaluate** (`#ifndef PH66_KERNEL_H`, the header guard).
Anything inside a dead one of those is counted as live; here the one it cannot
evaluate is a header guard, which is live. **`TASK_PHP_007` M2 measured nine
spellings of "this block is dead" that the normaliser counts in full, so a high
number is not a proof** — but 1 is the size of the residual and the residual is
a header guard.

▶ **P5 asked whether the narrowing costs the tier. It does not, and here is the
argument rather than the number.** Every function this row lifts is lifted
**whole**: `_zend_hash_init`, `_zend_hash_add_or_update`,
`_zend_hash_index_update_or_next_insert`, `zend_hash_del_key_or_index`,
`zend_hash_destroy` and `zend_inline_hash_func` are the tarball's own bodies.
The one narrowing that could have cost the tier is the **resize path**, and it is
a narrowing of the **domain** rather than an edit to any body: the kernel calls
`_zend_hash_init(&ht, nrec, ...)`, which is a real PHP spelling wherever the
size is known, and `nNumOfElements > nTableSize` is then unreachable.
`PROTOCOL_PHP.md` §A1's test is *"does a substitution change behaviour over the
reachable domain"*, and an unreachable branch changes nothing.

⚠ **The honest caveat.** `.tasks-php/TASK_PHP_062` §2.8 warned that *"the whole
of `zend_hash.c` is not the kernel"*, and it is right: the file has 1328 lines
and this row lifts about 300 of them. **`verbatim` is a claim about the lifted
spans, not about the file**, and the ten `extra_spans` are how the row says which
spans it means.

---

## 11. The Verus proof — what it cost, and the rlimit bisection

**49 verified / 0 errors** shipped, **59** under `--cfg slb_twin` (ten trusted
accessors, therefore ten twins). `./verus_run.py patterns-php/ph66-hashdel-uncompared/verus.rs --crate-type=lib`.

### 11a. ⭐ The `rlimit` attribute — ONE, and it is measured

The file carries **exactly one** `#[verifier::rlimit(120)]`, on `del`. That is a
MEASUREMENT and not a guess, and the measurement corrected a first draft that
carried **six**:

| configuration | result |
|---|---|
| all six deleted | **`48 verified, 1 errors`** — `function body check: Resource limit (rlimit) exceeded`, on **`del` and nothing else** |
| only `del`'s kept | **`49 verified, 0 errors`** — what ships |

▶ **So five of the six were decoration and are gone.** They had been added
together, before the file verified, on the reasonable-at-the-time guess that
`connect`, `ins_str`, `ins_idx`, `fold` and `kernel` would need them too; the
measurement was taken afterwards and said they did not. ⚠ **An unnecessary
`rlimit` is not a false claim** — it is a budget that is never reached and it
changes no verdict — **but it is an unearned suggestion that five functions were
hard**, and a reader who took the count as a difficulty signal would have been
wrong by a factor of six.

⭐ **Why `del` is the expensive one, in one sentence**: its lockstep
postcondition rewrites four links, two list heads, the bucket table, the
destructor counters and the allocator, and proves the whole post-state equal to
`s_del`'s output in a single query.

⭐ **What made the proof tractable was structural, not budgetary**, and the order
is worth recording because the tempting order is the wrong one:

1. **The search is PURE.** Unlike `ph64` — whose `s_del` mutates *inside* the
   chain walk and therefore needs a "remaining computation" invariant over a
   changing arena — this row's three walks (`find_str`, `find_idx`, `find_del`)
   only read, and the mutation is straight-line afterwards. The loop invariant is
   then an equality between two applications of one spec function over a
   **constant** `Seq`.
2. **`wf` needs no power-of-two fact.** The bucket index is `h & mask`, and the
   whole bound comes from `wf`'s `ar.len() == mask + 1` plus **one** bit-vector
   lemma, `h & m <= m`, which is universally true. A proof that needed `ts` to be
   a power of two would have needed a symbolic shift in the bit-vector solver.
3. **Both walks have a `decreases` for free**, because `CONNECT_TO_BUCKET_DLLIST`
   prepends and `CONNECT_TO_GLOBAL_DLLIST` appends: chain indices strictly
   descend and global-list indices strictly ascend. **`zend_hash.c` has no
   analogue of either and its walks have no termination measure.**

⚠ **The one thing the twin mechanism caught**, and it is exactly what §H says
twins are for: `slb_twin_wsub` needs a line the trusted item does not —
`assert(v@.len() == vstd::slice::spec_slice_len(v))` — because `o + n <= v@.len()`
alone does not stop `o + n` overflowing a `usize`. The `external_body` item was
getting that precondition **for free**; the twin had to earn it.

### 11a. What the proof costs at run time

`unsafe` vs `verus`, O3/isolated: **791 instructions / 3231 bytes** against
**770 / 3125** — `differ` at both levels, and **the proof rung is the smaller
one by 21 instructions**. `Ir(kernel)` on `small`: 63,881,798 (R4) against
63,266,923 (R5), i.e. **R5 is 614,875 Ir cheaper over 20 000 calls, −0.96 %**.

⚠ **That is a codegen coin flip and NOT a result about verification.** It is
quoted so nobody reads `differ` as *the proof costs something*.

⭐ **And the shape of the two `kernel` functions was made the same before the
`identity` entry was written.** As first built, `verus.rs` split the record loop
into a `run` helper and `unsafe.rs` did not, so at `O0` the measured symbol was a
**14-instruction wrapper** on one side and the whole loop on the other, and
`identity_level` said `differ` about a difference that was entirely the split.
Both rungs now carry the loop in `kernel` — which is also what gate stage 3a
wants, since a `kernel` window with no backward branch is a collapsed cell.

---

## 12. What the spellings audit moved

`python3 controls/spellings.py`, run **on the candidate `idiom` before the gate
saw it** (§3 trap 4; `TASK_PHP_060` §3.4).

**First run: 228 (spelling × rung) obligations, 83 unsatisfied — and SIX DISTINCT
`forbidden` SPELLINGS HIT, which FAIL the gate.** They were `arKey`,
`key_of(sel)`, `_zend_hash_add_or_update`, `zend_hash_del`,
`zend_hash_del_key_or_index` and `_zend_hash_init` — every one of them a real
identifier in the row's own kernels, and every one of them quoted **inside the
sentence explaining a `forbidden` entry rather than as the forbidden spelling
itself.** Every one came from the same
cause: **backticks inside the explanatory English of an entry are pins.** The
prose said things like *"a rung that acquired it would resolve some string-key
deletes to the index path before `zend_hash_del_key_or_index` ever ran"* — and
`zend_hash_del_key_or_index` is in both C rungs, so a `forbidden` entry HIT on
its own explanation.

**After the repair: 32 obligations, 0 unsatisfied.** The rule applied was: a
`forbidden` entry carries **exactly one** backticked span, the spelling itself;
everything else is unquoted prose. ⓘ This is item 100's fourth instance and the
first one caught *before* landing.

⭐⭐ **AND THE REPAIR CHANGED WHAT THE CONTRACT PINS, NOT ONLY HOW IT READS.**
Before it, `forbidden[2]`'s prose quoted `zend_hash_del_key_or_index` and
`_zend_hash_add_or_update` — two functions the kernel really does define — so the
entry **forbade the row's own primary span**. It would have failed the gate, and
the failure would have read as a defect in the kernel rather than in the sentence
explaining the kernel. ▶ **A `forbidden` entry's English is not commentary; it is
part of the declaration.** That is the half `PROTOCOL_PHP.md` §H1 does not say,
because §H1 is about character literals — a narrower case of the same thing.

⚠ `controls/spellings.py` ships five must-fire/must-not-fire arms, and **N2 is
live on this row**: `ph66_key_of` really does write a character literal, and a
pin on it could not fire (`§H1`).

---

## 13. Brackets, quoted first and last

| bracket | at the start | at the end |
|---|---|---|
| `python3 harness/measure.py --check-stale` | **66 record(s) examined, 0 STALE** | **66 record(s) examined, 0 STALE** |
| `python3 harness-php/gate.py --tool measure --check-stale` | **26 record(s) examined, 0 STALE** | **28 record(s) examined, 0 STALE** |

⭐ The PAT bracket **did not move**, which is what it is for: nothing under
`harness/`, `common/`, `patterns/`, `results/` or `pilot/` was touched. The php
bracket moved **26 → 28**, which is this row's own two records landing.

### 13a. The gate verdict, quoted from the record

`results-php/gate/ph66-hashdel-uncompared.json`, 2026-09-16:

> **`"verdict": "PASS"`**, `"failures": []`, `"complete_run": true`,
> `"contract_sha256": "ff4868908deb…"`.

`check.py`'s own last line is **`check.py: PASS`**. The six-command sequence took
the shape `PROTOCOL_PHP.md` §E predicts: build → measure → report → **gate
(FAIL: the table cites no `contract_sha256` yet)** → report → **gate (PASS)**.

⚠ **Two `!!` SHOUTS SURVIVE IN A PASSING RUN and neither is a defect of this
row.** They are printed here rather than left in the log:

1. `[doc-citation-other]` — three line citations into `build.py` from
   `c/emalloc_shim.h`. **That file is the shared `common-php/emalloc_shim.h`
   through this row's mandatory symlink**, so the citations are the corpus's and
   not this row's; re-citing them by function costs a re-measure of every php row
   (`RECAP` queue item 38).
2. `[collapse-ir]` — *"the derived floor is 224× below the tightest cell actually
   measured, so it rules out total collapse and essentially nothing else."*
   That is the stage describing its own strength and it says to read it as a
   smoke test. ⭐ On this row the anti-collapse question is answered elsewhere
   anyway: `controls/ladder.py` shows six cells returning eight distinct
   non-trivial u64s, which no collapsed kernel does.

Four `[tcb-unsafe]` shouts also survive, one per WRITE accessor, each saying that
the `requires` constrains nothing about `x`. **That is correct and intended** —
`x` is a pure value — and §14's per-item arguments are where the gate sends a
reader to judge it.

### 13b. ⚠ THIS SECTION CANNOT BE WRITTEN BEFORE THE GATE AND IS HASHED INTO IT

`NOTES.md` is in the gate record's `source_sha256`, and this section quotes the
gate's verdict. **So writing it stales the record it describes**, and
`gate.py --tool measure --check-stale` reports
`STALE results/gate/ph66-... patterns/ph66-.../NOTES.md` the moment it is
written. ▶ **The resolution is one more `report` + `gate` after the notes are
final**, which is what this row did: the verdict above is the run BEFORE this
file was last edited, and the run AFTER it reproduced the same verdict against
the same `contract_sha256`.

⭐ **It is worth naming because the six-command sequence in `PROTOCOL_PHP.md` §E
does not mention it.** §E's six commands get a row from nothing to a green gate;
they do not get a row from a green gate to a green gate *with the verdict written
down*. **A row that quotes its own verdict owes a seventh and eighth command**,
and a row that does not quote it has a `NOTES.md` a reader cannot check against
the record. ⓘ Not proposed as a rule — it is one row's observation, and the
cheaper alternative (never quote the verdict, only cite the record path) is
defensible and is what most of the corpus does.

---

## 14. SLB-TRUSTED-ARGUMENT — the ten per-item arguments the gate requires

**Ten trusted accessors, ten arguments.** Each answers the three things no stage
of the gate can judge: **(a)** is the twin's body the right checked stand-in for
the unchecked operation; **(b)** is the `ensures` COMPLETE with respect to every
unchecked operation the body performs; **(c)** does each clause mean the same
thing in the shipped configuration as in the twin's.

⚠ **(b) is `TASK_009_REVIEW`'s x4 and it is the one a contract pin cannot
catch:** a body that ALSO read `i + 1` satisfies the contract, the twin and the
`--cfg slb_twin` run unchanged. The defence on every item below is the same two
things — **a body short enough to quote whole**, and **Miri**, which this row
requires and which reported `ub: false, leak: false` on all eight inputs.

⭐⭐ **AND THE SHAPE OF THIS ROW'S TCB IS WORTH ONE PARAGRAPH BEFORE THE LIST.**
All ten items are INDEX ACCESSES and nothing else. There is no trusted item that
reinterprets memory, none that constructs a reference from an integer, none that
asserts anything about a VALUE. ▶ **So the whole trusted surface is one
proposition — *this index is in range* — and `wf` is what discharges it, ten
times.** That is the honest measure of what R5 buys here, and it is also why it
buys nothing against the row's actual defect: `zend_hash.c:464` picks a bucket
that is perfectly in range.

#### SLB-TRUSTED-ARGUMENT verus.rs nref

Body: `unsafe {{ v.get_unchecked(i as usize) }}`. Twin: `&v[i as usize]`.

**(a)** `&v[i]` is the checked form of the same borrow, character for character
otherwise, and it is the only checked spelling of it. **(b)** One unchecked
operation; one quantity can make it undefined — `i` against `v`'s length, a
RUN-TIME fact for a `Vec`, which is why the `requires` names it. The `ensures`
`*r == v@[i as int]` names the WHOLE node, so a body that returned a different
slot, or a modified copy, could not satisfy it. ⭐ **It is the ONLY read
accessor in the file and that is deliberate**: returning `&Node` rather than ten
scalars costs one bound instead of ten and shrinks the trusted surface by nine
items. ⚠ The residue is a body that ALSO read `i + 1` and discarded it; Miri
covers that. **(c)** `v@.len()` and `Seq::index` mean the same in both
configurations. The four call sites bound `i` from `wf`: the three chain walks
carry `p == NIL || p < a@.len()` as a loop invariant, and `fold` carries the
same for the global list.

#### SLB-TRUSTED-ARGUMENT verus.rs set_nxt

Body: `unsafe { v.get_unchecked_mut(i as usize).nxt = x; }`.
Twin: `let n = Node { nxt: x, ..*(&v[i as usize]) }; v.set(i as usize, n);`.

**(a)** The twin performs the same field write through the CHECKED path —
`&v[i]` panics where `get_unchecked_mut` is undefined, and `Vec::set` is vstd's
checked store. It is the same store, one bound-check apart, and there is no
third spelling to choose between. **(b)** The body performs exactly one
unchecked operation and its definedness depends on exactly one thing: `i`
against `v`'s length, which for a `Vec` is a RUN-TIME fact and is therefore what
the `requires` has to name. `x: u32` is a PURE VALUE — every one of the 2^32
values is a legal store into a field `Vec::push` initialised before any link
pointed at it — so it needs no precondition at all. ⚠⚠ **THE `ensures` NAMES
THE WHOLE POST-STATE, `old(v)@.update(i, Node { nxt: x, ..old(v)@[i] })`, AND
ON THIS ROW THAT IS NOT PEDANTRY**: `zend_hash_del_key_or_index` is two pairs of
NEIGHBOUR writes — `p->pLast->pNext` / `p->pNext->pLast` at `:470-475` and
`p->pListLast->pListNext` / `p->pListNext->pListLast` at `:477-484` — so an
`ensures` naming only `v@[i].nxt == x` would license a body that also moved a
neighbour's link, which is exactly the class this construct makes easy to write.
⚠ The residue (b) cannot cover is a body that also WROTE somewhere and then
restored it, or that read out of bounds and discarded the value; **Miri is the
backstop for that class and this row requires it** (`spec.md`'s `miri` block).
**(c)** `v@.len()`, `Seq::update` and the `Node` literal mean the same in the
shipped configuration and under `--cfg slb_twin`; nothing here is
`cfg`-dependent. The call sites bound `i` from `wf`: `connect` writes the node
it just pushed (`i == a@.len() - 1`) and its two neighbours, both of which `wf`
places below the arena length; `del` writes the four neighbours of a bucket the
chain walk returned, and the walk's own `ensures` gives `r < a@.len()`.

#### SLB-TRUSTED-ARGUMENT verus.rs set_lst

Body: `unsafe { v.get_unchecked_mut(i as usize).lst = x; }`.
Twin: `let n = Node { lst: x, ..*(&v[i as usize]) }; v.set(i as usize, n);`.

**(a)** The twin performs the same field write through the CHECKED path —
`&v[i]` panics where `get_unchecked_mut` is undefined, and `Vec::set` is vstd's
checked store. It is the same store, one bound-check apart, and there is no
third spelling to choose between. **(b)** The body performs exactly one
unchecked operation and its definedness depends on exactly one thing: `i`
against `v`'s length, which for a `Vec` is a RUN-TIME fact and is therefore what
the `requires` has to name. `x: u32` is a PURE VALUE — every one of the 2^32
values is a legal store into a field `Vec::push` initialised before any link
pointed at it — so it needs no precondition at all. ⚠⚠ **THE `ensures` NAMES
THE WHOLE POST-STATE, `old(v)@.update(i, Node { lst: x, ..old(v)@[i] })`, AND
ON THIS ROW THAT IS NOT PEDANTRY**: `zend_hash_del_key_or_index` is two pairs of
NEIGHBOUR writes — `p->pLast->pNext` / `p->pNext->pLast` at `:470-475` and
`p->pListLast->pListNext` / `p->pListNext->pListLast` at `:477-484` — so an
`ensures` naming only `v@[i].lst == x` would license a body that also moved a
neighbour's link, which is exactly the class this construct makes easy to write.
⚠ The residue (b) cannot cover is a body that also WROTE somewhere and then
restored it, or that read out of bounds and discarded the value; **Miri is the
backstop for that class and this row requires it** (`spec.md`'s `miri` block).
**(c)** `v@.len()`, `Seq::update` and the `Node` literal mean the same in the
shipped configuration and under `--cfg slb_twin`; nothing here is
`cfg`-dependent. The call sites bound `i` from `wf`: `connect` writes the node
it just pushed (`i == a@.len() - 1`) and its two neighbours, both of which `wf`
places below the arena length; `del` writes the four neighbours of a bucket the
chain walk returned, and the walk's own `ensures` gives `r < a@.len()`.

#### SLB-TRUSTED-ARGUMENT verus.rs set_lnxt

Body: `unsafe { v.get_unchecked_mut(i as usize).lnxt = x; }`.
Twin: `let n = Node { lnxt: x, ..*(&v[i as usize]) }; v.set(i as usize, n);`.

**(a)** The twin performs the same field write through the CHECKED path —
`&v[i]` panics where `get_unchecked_mut` is undefined, and `Vec::set` is vstd's
checked store. It is the same store, one bound-check apart, and there is no
third spelling to choose between. **(b)** The body performs exactly one
unchecked operation and its definedness depends on exactly one thing: `i`
against `v`'s length, which for a `Vec` is a RUN-TIME fact and is therefore what
the `requires` has to name. `x: u32` is a PURE VALUE — every one of the 2^32
values is a legal store into a field `Vec::push` initialised before any link
pointed at it — so it needs no precondition at all. ⚠⚠ **THE `ensures` NAMES
THE WHOLE POST-STATE, `old(v)@.update(i, Node { lnxt: x, ..old(v)@[i] })`, AND
ON THIS ROW THAT IS NOT PEDANTRY**: `zend_hash_del_key_or_index` is two pairs of
NEIGHBOUR writes — `p->pLast->pNext` / `p->pNext->pLast` at `:470-475` and
`p->pListLast->pListNext` / `p->pListNext->pListLast` at `:477-484` — so an
`ensures` naming only `v@[i].lnxt == x` would license a body that also moved a
neighbour's link, which is exactly the class this construct makes easy to write.
⚠ The residue (b) cannot cover is a body that also WROTE somewhere and then
restored it, or that read out of bounds and discarded the value; **Miri is the
backstop for that class and this row requires it** (`spec.md`'s `miri` block).
**(c)** `v@.len()`, `Seq::update` and the `Node` literal mean the same in the
shipped configuration and under `--cfg slb_twin`; nothing here is
`cfg`-dependent. The call sites bound `i` from `wf`: `connect` writes the node
it just pushed (`i == a@.len() - 1`) and its two neighbours, both of which `wf`
places below the arena length; `del` writes the four neighbours of a bucket the
chain walk returned, and the walk's own `ensures` gives `r < a@.len()`.

#### SLB-TRUSTED-ARGUMENT verus.rs set_llst

Body: `unsafe { v.get_unchecked_mut(i as usize).llst = x; }`.
Twin: `let n = Node { llst: x, ..*(&v[i as usize]) }; v.set(i as usize, n);`.

**(a)** The twin performs the same field write through the CHECKED path —
`&v[i]` panics where `get_unchecked_mut` is undefined, and `Vec::set` is vstd's
checked store. It is the same store, one bound-check apart, and there is no
third spelling to choose between. **(b)** The body performs exactly one
unchecked operation and its definedness depends on exactly one thing: `i`
against `v`'s length, which for a `Vec` is a RUN-TIME fact and is therefore what
the `requires` has to name. `x: u32` is a PURE VALUE — every one of the 2^32
values is a legal store into a field `Vec::push` initialised before any link
pointed at it — so it needs no precondition at all. ⚠⚠ **THE `ensures` NAMES
THE WHOLE POST-STATE, `old(v)@.update(i, Node { llst: x, ..old(v)@[i] })`, AND
ON THIS ROW THAT IS NOT PEDANTRY**: `zend_hash_del_key_or_index` is two pairs of
NEIGHBOUR writes — `p->pLast->pNext` / `p->pNext->pLast` at `:470-475` and
`p->pListLast->pListNext` / `p->pListNext->pListLast` at `:477-484` — so an
`ensures` naming only `v@[i].llst == x` would license a body that also moved a
neighbour's link, which is exactly the class this construct makes easy to write.
⚠ The residue (b) cannot cover is a body that also WROTE somewhere and then
restored it, or that read out of bounds and discarded the value; **Miri is the
backstop for that class and this row requires it** (`spec.md`'s `miri` block).
**(c)** `v@.len()`, `Seq::update` and the `Node` literal mean the same in the
shipped configuration and under `--cfg slb_twin`; nothing here is
`cfg`-dependent. The call sites bound `i` from `wf`: `connect` writes the node
it just pushed (`i == a@.len() - 1`) and its two neighbours, both of which `wf`
places below the arena length; `del` writes the four neighbours of a bucket the
chain walk returned, and the walk's own `ensures` gives `r < a@.len()`.

#### SLB-TRUSTED-ARGUMENT verus.rs set_data

Body: `unsafe { v.get_unchecked_mut(i as usize).data = x; }`.
Twin: `let n = Node { data: x, ..*(&v[i as usize]) }; v.set(i as usize, n);`.

**(a)** As the four link setters: the twin is the same store through `&v[i]` and
`Vec::set`. **(b)** One unchecked operation, one quantity — `i` against the
length. `x: u64` is a PURE VALUE: it is the projected `zval *` the bucket stores
and every u64 is a legal payload. ⭐ **It is the only write this kernel makes
that is NOT a link**, and its two call sites are the UPDATE arms of the two
insert functions (`zend_hash.c:232` and `:364`, through `UPDATE_DATA`). ⚠ The
`ensures` is the whole post-state for a reason specific to those sites:
`UPDATE_DATA` writes TWO fields in C — `pDataPtr` and then `pData = &p->pDataPtr`
— and the second is a self-pointer this row projects away, so a partial `ensures`
here would be the one place a reader could not tell the projection from an
omission. **(c)** Nothing `cfg`-dependent; both call sites bound `i` by the
chain walk's own `ensures`, `r != NIL ==> r < a@.len()`.

#### SLB-TRUSTED-ARGUMENT verus.rs aget

Body: `unsafe { *v.get_unchecked(i) }`. Twin: `v[i]`.

**(a)** `v[i]` is the checked form of the same read. **(b)** One unchecked
operation; one quantity — `i` against the length. The `ensures` `r == v@[i as
int]` names the whole result, so a body that read `i + 1` and returned it could
not satisfy it; a body that read `i + 1` and DISCARDED it could, and that residue
is Miri's. **(c)** Nothing `cfg`-dependent. ⭐⭐ **WHERE THE PRECONDITION COMES
FROM IS WORTH THE PARAGRAPH, because it is the one place this proof could have
needed a bit-vector argument and does not.** `aget` serves BOTH `ht->arBuckets`
and the size-class cache counters, which are the same Rust type. For the cache,
`idx < MCM` is tested in the exec code and `wf` carries `cnt.len() == MCM`. For
the bucket table the index is `(h & mask) as usize`, and the bound comes from
`wf`'s `ar.len() == mask + 1` together with `lemma_mask_le` — `h & m <= m`,
universally true and the only `by (bit_vector)` in the file. ▶ **`wf` deliberately
does NOT say that the table size is a power of two**, because a proof that needed
that would have needed a symbolic shift inside the bit-vector solver.

#### SLB-TRUSTED-ARGUMENT verus.rs aset

Body: `unsafe { *v.get_unchecked_mut(i) = x; }`. Twin: `v.set(i, x);`.

**(a)** `Vec::set` is vstd's checked store at the same index. **(b)** One
unchecked operation, one quantity — `i` against the length; `x: u32` is a pure
value. The `ensures` `final(v)@ == old(v)@.update(i as int, x)` names the WHOLE
post-state, so a body that also moved another entry of `arBuckets` could not
satisfy it. ⚠ **That is not hypothetical on this row**: `zend_hash_rehash`
rewrites every entry of exactly this array, and `spec.md`'s `idiom.forbidden[1]`
pins it absent for the same reason. **(c)** Nothing `cfg`-dependent; the bound
is `aget`'s, from the same two places.

#### SLB-TRUSTED-ARGUMENT verus.rs wsub

Body: `unsafe { v.get_unchecked(o..o + n) }`. Twin:
`assert(v@.len() == vstd::slice::spec_slice_len(v)); vstd::slice::slice_subrange(v, o, o + n)`.

**(a)** `slice_subrange` is vstd's CHECKED `&v[i..j]` and is the stand-in for the
unchecked range borrow. **(b)** One unchecked operation; its definedness depends
on `o + n <= v@.len()`, which is the whole `requires` — and on nothing about the
bytes, which is the point: every one of the 256 values is a legal window byte.
The `ensures` `r@ == v@.subrange(o, o + n)` names the whole view, so a body that
returned a shifted window could not satisfy it. **(c)** ⭐⭐ **THIS IS THE ONE
ITEM WHERE THE TWIN NEEDED SOMETHING THE TRUSTED BODY DID NOT, AND IT IS THE
TWIN MECHANISM EARNING ITS PLACE.** `o + n <= v@.len()` does not by itself stop
`o + n` overflowing a `usize`; the broadcast group is what says a slice's length
IS a `usize`, and the twin has to `assert` it where the `external_body` item
simply asserts its way past it. The clause means the same thing in both
configurations — but only one of them has to prove it.

#### SLB-TRUSTED-ARGUMENT verus.rs wb

Body: `unsafe { *v.get_unchecked(i) }`. Twin: `v[i]`.

**(a)** `v[i]` is the checked form of the same read. **(b)** One unchecked
operation, one quantity — `i` against the slice length, a run-time fact. The
`ensures` `r == v@[i as int]` names the whole result. ⭐ **It asserts nothing
about the BYTE, and that is the row**: every one of the 256 values is a legal
record byte and the kernel's job is to be correct on all of them. **(c)** Nothing
`cfg`-dependent. The call site is the record loop, whose invariant carries
`nrec * 4 <= win@.len()` and `r < nrec`; the four reads are at `r*4 .. r*4+3`.

⚠ **It is the only place attacker data enters the kernel.** If `wb`'s contract
were wrong, everything downstream would be about a different window — which is
why its `ensures` names the value rather than a property of it.
