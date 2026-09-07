# TASK_PHP_012_REPORT — adversarial review of `CATALOGUE.md`, and what we build first

**Role:** research **reviewer**. **Status: delivered, NOT REVIEWED.**
**Under review:** `patterns-php/CATALOGUE.md` (91 rows), the five reversals and
three settled rows in `TASK_PHP_011_REPORT.md`, `RECAP_PHP.md` F21–F24.
**Scratch:** `.temp/php12/` — every probe, log and generator named below.

> ✅ marks something I **RAN**, with the output pasted. Everything else is a
> reading of the pinned tarball.
> ⚠ I edited nothing under `harness/`, `common/`, `patterns/`, `results/`,
> `pilot/`, `.web/` or `RECAP_PHP.md`. No `git add` / `git commit`.
> ⚠ Every citation below resolves against the **pinned tarball**
> (`5783e0c0…d6919`) through `.temp/php11/pristine.py`, which sha256-checks each
> file against `patterns-php/php-5.0.0.manifest` before serving a line. I reused
> it; I did not rewrite it.

---

## §0 The bracket, open

```
$ python3 harness/measure.py --check-stale
FRESH       results/p49-interned-pool.json             18 source(s) + 9 input(s)
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
preflight
  ok   shim /home/apt/repos_common/sec-ladder/.temp/php-root
  ok   common-php/ digest bridge
  ok   every patterns-php/*/c/ file has a digest key
  ok   <row>/c/emalloc_shim.h symlink, UNCONDITIONAL
  ok   provenance.py overlap self-test (9 cases)
  ok   patterns-php/MANIFEST.sha256
  ok   every php record has a CERTIFYING preflight record beside it
FRESH       results/gate/ph00-smoke.json               29 source(s)
FRESH       results/ph00-smoke.json                    19 source(s) + 8 input(s)
2 record(s) examined, 0 STALE
```

`git status --porcelain` at open: **clean** (the five `.web/` files
`TASK_PHP_011` reported dirty are no longer dirty — someone landed them; I never
opened `.web/`).

**Toolchain, for the runs below:** glibc `2.39-0ubuntu8.7`, gcc `13.3.0`,
rustc `1.97.1`, valgrind at `~/tools/valgrind/bin/valgrind`.

---

## §1 ⚠⚠ VERDICT, AND THE ONE SENTENCE THAT MATTERS

**The catalogue is good work and I am not asking for it to be redone.** Its
coverage claim survives an independent re-derivation, its citations survive a
sample check, two of its three settled rows survive re-reading at source, and
`F21`/`F22`/`F23` all hold.

⚠⚠ **But `F22` — *a kill written as a set hides its members* — is violated by
the catalogue's own Part C, in the same document that discovered it.** Four
LOGIC rows die in one sentence into `ph47`, and the catalogue's **own stated
discriminator** refutes that merge for at least three of them. And `C.1`'s
closing sentence — *"every one of them is a **merge** — the row survives inside
another row's `corpus rows`"* — is **false for 6 of the 12**, which makes them
the silent drops the task file says a merge must never be.

⚠ **And the manager's prior for the first row, `ph11`, is the wrong pick, for a
reason sharper than the one stated.** ✅ Measured: at `-O3` safe Rust and unsafe
Rust emit **byte-identical** kernel-exclusive `Ir`, and **both beat C**. There is
no bounds check to price. §7 gives the mechanism and names `ph03` instead.

| # | sev | finding | evidence |
|---|---|---|---|
| **B1** | **blocker** | `ph15`'s stated mechanism is **false**; a kernel built to its own `▸ blob` spec exhibits nothing | ✅ `.temp/php12/10-ph15-probe.log` |
| **M1** | **major** | `C.1`: 6 of 12 "merges" are **silent drops** — the target row does not carry the id | ✅ `.temp/php12/07-c1-merge.log` |
| **M2** | **major** | the four-LOGIC set kill into `ph47` is `F22`'s own shape, and the catalogue's own rule refutes 3 of 4 | `.temp/php12/05-logicset.log`, `06-logic003-008.log` |
| **M3** | **major** | `C.2`'s soft kill of **CRASH-021 REVERSES** on the run the catalogue declined to take | ✅ `.temp/php12/04-crash021.log` |
| **M4** | **major** | **12 of 41** `verbatim` tiers are mis-declared; the tier is the only surviving fidelity signal | ✅ `.temp/php12/17-tier.log` |
| **M5** | **major** | CRASH-061 and CRASH-126 are merged into the **wrong family**; CRASH-126's call does not fail at all | `.temp/php12/01-sixrows.log`, `02-callmethod.log` |
| **M6** | **major** | `ph11` cannot price a bounds check — R2 ≡ R4 to the instruction, and both beat R1 | ✅ `.temp/php12/ph11m/`, §7.2 |
| **M7** | **major** | **no `fix_commit` is resolvable on this box** — `PROTOCOL_PHP.md` §F5 cannot be met as written | ✅ §7.5 |
| **m1** | minor | `ph68`'s bare `:87-89` inherits the wrong file — the exact class `TASK_PHP_011` §2.2 claims to have swept | ✅ `.temp/php12/14-ph68-ph85.log` |
| **m2** | minor | `ph85`'s mechanism overstates the harm: the arm requires `str.len == 0` | ✅ same log |
| **m3** | minor | `C.3`'s *"the ONLY criterion-3 kill"* — CRASH-017 does not fail criterion 3 | §4.3 |
| **m4** | minor | `ph11`'s *"sibling at `:4028`"* — `:4028` performs **no dereference at all** | ✅ `15-ph11.log` |
| **m5** | minor | `ph28`'s *"the only row that needs a memory budget"* understates `ph19`/`ph21`/`ph22` | §6.3 |
| **m6** | minor | `ph03` carries a **third, unrecorded limb** (`:158` makes `:160`/`:162` dead code) | ✅ `18-ph03.log` |
| **m7** | minor | `ph66`'s *"the DJBX33A preimage … was never computed"* frames a one-line computation as open work | ✅ `20-djb-preimage.log` |
| **m8** | minor | a **fourth** suspect corpus label, on the row I recommend building first | ✅ §7.4 |

**Clean negatives are in §8. They are not padding — five named attacks did not
land, and one of them is the catalogue's headline claim.**

---

## §2 ⚠⚠ TASK §1 — the six "mechanism quality" rows, one by one

**The manager asks: does *"this is an ordinary null-deref"* mean *"mechanically
identical to another row"* (a merge) or *"uninteresting"* (a forbidden kill)?**

✅ **The manager's §5 call #1 is RIGHT and `ADJUDICATION_001.md` §3b is wrong:
mechanism *quality* is not in the bar.** `PLAN_PHP.md` §3 has four criteria and
the only comparative one is distinctness. I re-derived that and found nothing to
put against it.

⚠⚠ **But the engineer's remedy is also wrong, in a way nobody has said yet: the
six are NOT one family. They are five different C mechanisms, and the catalogue
merged three of them into `ph60` on a sentence that does not survive the
source.** All six read at `.temp/php12/01-sixrows.log`.

| id | site | what the C actually does | distinct? |
|---|---|---|---|
| **CRASH-088** | `ftp_fopen_wrapper.c:649→:652` | `stream = php_ftp_fopen_connect(...)` — a **return value** that can be NULL, used unconditionally | this **is** ph60 |
| **CRASH-021** | `datetime.c:1029→:1033` | `ta = php_localtime_r(...)` — a **return value** that can be NULL, used unconditionally | ⚠ **the same as CRASH-088.** Should be a **ph60 merge**, not a criterion-2 kill — see M3 |
| **CRASH-082** | `array.c:4085` | `!f(x) == SUCCESS` — a **precedence** defect; the guard runs and tests the negation | ✅ distinct — correctly `ph59` |
| **CRASH-126** | `mbstring.c:3215-3219` | ⚠ **nothing fails.** `"\|s"` makes the argument optional, `zend_parse_parameters` returns **SUCCESS**, and `:3215` **does** test it. `char *typ = NULL` at `:3211` simply survives to `strcasecmp("all", typ)` | ⚠ **distinct.** The guard that is missing is `if (typ)`, not `if (rc == FAILURE)` |
| **CRASH-163** | `zend.c:1075→:1083` | ⚠ the failure **is** tested at `:1078`. `EG(exception) = NULL` is set by **the caller itself** at `:1075`, and the failure arm then passes it to `zend_exception_error` | ⚠ **distinct.** Save-and-clear-a-global, then use it in the error path |
| **CRASH-061** | `zend_object_handlers.c:509→:513` | `zval *retval;` **uninitialised** at `:509`; `zend_call_method_with_1_params(…, &retval, …)`; `zval_ptr_dtor(&retval)`. ✅ `zend_interfaces.c:81-94` shows `zend_call_method` **discards `result`** into a `zend_error` and returns `*retval_ptr_ptr` — and `:512` discards *that* too | ⚠ **distinct, and in the wrong family.** This is a **destructor on an out-parameter a failing call left unwritten** — i.e. **`ph90`**'s mechanism (guard absent instead of wrong) and **`ph50`**'s (discarded status → unassigned automatic). It is not "a return value used unchecked" |

**Answer to the task's question: the six got BOTH.** CRASH-088 and CRASH-021 are
a genuine merge; CRASH-082, CRASH-126, CRASH-163 and CRASH-061 were killed on
*quality* and then **re-killed on a distinctness claim that does not hold**. The
catalogue traded a forbidden kill for a wrong merge on three of the six.

⚠ **`ph60` as shipped is one row over four sites of which only one is its own
mechanism.** `PLAN_PHP.md` §3.1 admits *slight variations as separate rows* in
this corpus, so the cost of splitting is zero and the cost of not splitting is a
row whose `spec.md` cannot state one invariant.

### 2.1 ✅ M3 — CRASH-021 reverses, MEASURED

`C.2` is the catalogue's only criterion-2 kill and it discloses itself as *"a
soft kill: it is criterion 2 **pending a measurement I did not take**… If someone
runs it and it faults, it is admissible and the kernel is ten lines."*

**I took the measurement.** `.temp/php12/crash021_probe.c`, the C lifted from
`datetime.c:993/1029/1032-1033`:

```
$ env -u LD_PRELOAD ./crash021_probe
sizeof(time_t)=8  glibc strftime probe
Q1  timestamp                    0 -> localtime_r = non-NULL
Q1  timestamp           2147483647 -> localtime_r = non-NULL
Q1  timestamp  9223372036854775807 -> localtime_r = *** NULL ***
Q1  timestamp -9223372036854775808 -> localtime_r = *** NULL ***
Q1  timestamp    67768036191676800 -> localtime_r = *** NULL ***
Q1 VERDICT: localtime_r returns NULL for at least one PHP-reachable timestamp: YES
Q2  strftime(buf,64,"%Y",NULL) *** FAULTED, signal 11 ***
```

`datetime.c:1009 timestamp = Z_LVAL_PP(timestamp_arg);` is a **`long`**, so
`gmstrftime($f, PHP_INT_MAX)` reaches `localtime_r` with `LONG_MAX`, gets NULL,
and `:1033` passes it to `strftime`. **Both halves fire on this box.**
`crashes_pristine_5_0_0 = True` in the CSV, and the fault is real.

⚠ **The kill also priced the wrong frame** — it asked *"does glibc's `strftime`
fault?"* when the mechanism is PHP's missing NULL test at `:1029`. That is
`F21`/CRASH-097's error (*"the kill priced the wrong operand"*) **repeated one
round later, by the task that named it.**

**→ CRASH-021 is admissible. `C.2` becomes empty.**

---

## §3 ⚠⚠ TASK §2.1 + §2.2 — Part C, and the set-shaped kill inside it

### 3.1 M1 — six of the twelve "merges" are silent drops ✅ MEASURED

The task file is explicit: *"mechanically identical to another row → that is
distinctness, a legitimate **merge** (never a silent drop)"*. `CATALOGUE.md:933`
claims exactly that has been done:

> *"⚠ These are the only kills in this catalogue that rest on §3.1, and every one
> of them is a **merge** — the row survives inside another row's `corpus rows`."*

`.temp/php12/c1_merge_check.py` parses Part A's `corpus rows` column and asks,
per killed id, whether the row `C.1` names actually lists it:

```
$ python3 .temp/php12/c1_merge_check.py
  CRASH-106   -> ph19          carried in Part A `corpus rows`: *** NO ***
  CRASH-109   -> ph19/ph20     carried in Part A `corpus rows`: *** NO ***
  CRASH-090   -> ph32          carried in Part A `corpus rows`: YES (ph32)
  V5C-116     -> ph03          carried in Part A `corpus rows`: YES (ph03)
  V5C-173     -> ph11          carried in Part A `corpus rows`: YES (ph11)
  V5C-015     -> ph22          carried in Part A `corpus rows`: YES (ph22)
  CRASH-037   -> ph39          carried in Part A `corpus rows`: YES (ph39)
  CRASH-101   -> ph39          carried in Part A `corpus rows`: YES (ph39)
  CRASH-061   -> ph60          carried in Part A `corpus rows`: YES (ph60)
  CRASH-126   -> ph60          carried in Part A `corpus rows`: YES (ph60)
  CRASH-163   -> ph60          carried in Part A `corpus rows`: YES (ph60)
  LOGIC-003   -> ph47          carried in Part A `corpus rows`: *** NO ***
  LOGIC-008   -> ph47          carried in Part A `corpus rows`: *** NO ***
  LOGIC-014   -> ph47          carried in Part A `corpus rows`: *** NO ***
  LOGIC-018   -> ph47          carried in Part A `corpus rows`: *** NO ***

C.1 ids NOT carried by the row they were merged into: 6
```

**`C.7`'s summary carries the same false sentence** — *"each survives inside a
catalogued row's `corpus rows` and is named in Part C so the merge is
auditable"*, over a list of twelve of which six do not.

**Concrete failure scenario.** An engineer builds `ph47`. Its `provenance` block
gets `root_cause_ids: ["CRASH-104","CRASH-058"]`, because that is what Part A
says. LOGIC-003/008/014/018 now appear in **no** row's provenance and in **no**
row's `spec.md`. The next coverage check — the one `F22` says is the only thing
that finds set-shaped kills — runs against Part A + Part C, finds them in Part C,
and reports 166/166. **The drop is invisible to the exact check invented to
catch it**, because `coverage.py` counts a kill-table mention as coverage.

### 3.2 M2 — the four-LOGIC set kill is `F22`'s own shape ✅ read at source

`C.1` disposes of four rows in one sentence:

> *"LOGIC-003, LOGIC-008, LOGIC-014, LOGIC-018 | **ph47** | all family E —
> `is_ref` stamped on, or not separated from, a live shared slot; LOGIC-017 was
> **kept** as ph48 because it forces the flag rather than failing to clear it"*

That sentence supplies its own discriminator — *forces the flag* vs *fails to
clear it* — and then does not apply it. All four sites, plus the three
`SEPARATE_*` macros at `Zend/zend.h:554-577`, read at
`.temp/php12/05-logicset.log` and `06-logic003-008.log`:

| row | site | the C | against the sentence's own rule |
|---|---|---|---|
| **LOGIC-014** | `zend_builtin_functions.c:1420` | `SEPARATE_ZVAL_TO_MAKE_IS_REF(arg);` — ⚠ **a THIRD macro** (`zend.h:573-577`): `if (!PZVAL_IS_REF) { SEPARATE_ZVAL; is_ref = 1; }`, and `SEPARATE_ZVAL` is itself a **no-op at refcount 1**, so the stamp lands on the caller's live arg-stack slot | ⚠ **it FORCES the flag.** This is `ph48`'s mechanism delivered by one macro instead of two lines — the catalogue's own reason for keeping `ph48` |
| **LOGIC-018** | `zend_compile.c:1967-1971` | `static void inherit_static_prop(zval **p) { (*p)->refcount++; (*p)->is_ref = 1; }` — ⚠ **no separator anywhere**, a bare unconditional stamp | ⚠ **it FORCES the flag**, and it is not even `ph48`: `ph48` separates first |
| **LOGIC-008** | `zend_execute_API.c:430`, `:458` | `SEPARATE_ZVAL(pp);` **unconditional**, and `zend.h:564` makes `SEPARATE_ZVAL` set `is_ref = 0` — so it **severs** an inherited `is_ref` binding | ⚠ **the OPPOSITE of `ph47`.** `ph47` is a separator that no-ops when it should act; this is a separator that acts when it should not. A third direction the sentence does not have a slot for |
| **LOGIC-003** | `zend_object_handlers.c:296-300`, consumer `zend_execute.c:1277-1279` | `rv = zend_std_call_getter(...); if (rv) retval = &rv;` → `return *retval;` — the value comes back **unseparated and unincremented**, and `:1279 incdec_op(z)` mutates it in place | ⚠ **no separator is called at all.** Closest to `ph47`, and still not the same C |

**Three of four contradict the sentence that killed them, using the sentence's
own test.** ⚠ And `PLAN_PHP.md` §3.1 is explicit that in *this* corpus only
**exact** C-side duplication is a kill and *"a slight variation is ADMITTED as
its own row"* — none of these four is exact.

**Concrete failure scenario.** `ph47`'s `spec.md` must pin one invariant. It
cannot pin *"the separator no-ops"* (LOGIC-008 is the separator **firing**),
*"is_ref is not set"* (LOGIC-014/018 **set** it) and *"CoW is broken"* (that is
the outcome, not the mechanism) at once. The row ships one obligation and four
corpus ids, and the report built from it says the corpus has one CoW defect
where it has at least three.

### 3.3 Are there other set-shaped Part C entries? ⚠ yes, two more

Enumerated **against `index.csv`**, not against the prose, as `F22` requires:

- **`CRASH-061, CRASH-126, CRASH-163 → ph60`** — three rows, one sentence
  (*"same 'fallible call's failure not tested'"*). ⚠ §2 shows the sentence is
  false for all three.
- **`CRASH-037, CRASH-101 → ph39`** — two rows, one sentence. ✅ This one holds:
  `zend_exceptions.c:339` and `streamsfuncs.c:817` are both an unguarded
  `Z_*_PP` read, and both **are** carried in `ph39`'s `corpus rows`. **Clean
  negative.**

### 3.4 m3 — `C.3`'s headline overstates itself

`C.3` says *"**Exactly one row in 166**"* and *"⚠ That is the ONLY criterion-3
kill."* ⚠ **CRASH-017 does not fail criterion 3.** A kernel over a blob of
`size` values computing `unsigned int real_size = REAL_SIZE(size)` and folding
the outcome into a `u64` **is** a computation over a flat blob producing a `u64`
— which is all criterion 3 asks. What actually retires the row is
`PLAN_PHP.md` §4.3's standing decision (*"a multiplier on every sizing defect in
the engine, not a pattern of its own … do not re-propose it as a row"*), which is
binding and correct.

⚠ **`C.0` warns against precisely this** — *"tier assignments wearing a kill's
clothes"*. This is a **design decision wearing criterion 3's clothes**, in the
section written to stop that. **The honest statement is: zero criterion-3 kills;
one kill on a standing design decision.** The outcome does not change.

---

## §4 TASK §2.3 — citations, checked independently

⚠ `TASK_PHP_011`'s 222/222 checks **existence and line-in-range**. That check
**cannot fail on a transposed line inside a long file**, which is the failure
mode `PLAN_PHP.md` §6 records. I checked **content**.

### 4.1 ✅ A 12-row random sample, resolved and printed

`.temp/php12/cite_dump.py` (seed 12) →
`ph02 ph19 ph35 ph36 ph45 ph48 ph49 ph61 ph62 ph68 ph85 ph86`,
**46 citations resolved**, full output at `.temp/php12/13-cite-sample.log`. Every
one lands on the C the catalogue claims — e.g.

```
   php_pcre.c:448     name_idx = 0xff * name_table[0] + name_table[1];
   zend_language_parser.c:3518     if (yycheck[yyx + yyn] == yyx)
   zend_execute_API.c:608     SEPARATE_ZVAL_IF_NOT_REF(tmp_object_ptr);
   zend_execute_API.c:610     (*fci->object_pp)->is_ref = 1;
   zend_hash.c:490     ht->pDestructor(p->pData);
   zend_hash.c:497     ht->nNumOfElements--;
```

✅ **Citation quality is high.** Two defects only:

### 4.2 m1 — `ph68`'s bare `:87-89` names the wrong file

`ph68`'s block opens `Zend/zend_execute_API.c:617-626` and then writes
*"`zend_objects_store_put` pops it back at `:87-89`"*. By the catalogue's own
reading convention the bare span inherits `zend_execute_API.c`, where `:87-89` is

```
    89  static void zend_extension_deactivator(zend_extension *extension TSRMLS_DC)
```

✅ **`zend_objects_store_put` does not exist in that file at all**
(`pristine.py --grep Zend/zend_execute_API.c "zend_objects_store_put"` → no
hits). The intended file is `Zend/zend_objects_API.c`, whose `:87-89` is the
free-list pop exactly as claimed:

```
    87  	if (EG(objects_store).free_list_head != -1) {
    88  		handle = EG(objects_store).free_list_head;
    89  		EG(objects_store).free_list_head = …object_buckets[handle].bucket.free_list.next;
```

⚠ **This is the exact class `TASK_PHP_011` §2.2 says it found twice (`ph09`,
`ph77`) and fixed**, and it survived because `zend_execute_API.c:87-89` exists
and is in range — **the 222/222 checker is structurally blind to it.**

### 4.3 m2 — `ph85`'s mechanism overstates the harm

`ph85` says *"`array_init` is called straight over a live `IS_STRING` payload …
the string's buffer becomes unreachable."* At `zend_execute.c:914-926` the arm is
guarded by

```
   916  		|| (container->type==IS_STRING && container->value.str.len==0)) {
   920  			if (!PZVAL_IS_REF(container)) {
   921  				SEPARATE_ZVAL(container_ptr);
   924  			array_init(container);
```

⚠ The retype only happens for a **zero-length** string, whose `str.val` is
either the shared `empty_string` global (nothing to leak) or a one-byte
`emalloc`. So the leak is **0 or 1 byte per event**, not a live payload. The
row's `▸ benign + u64 = (allocs, frees)` still sees it, so criterion 2 holds —
but a builder reading Part B expects a payload leak and will size the fixture
wrongly.

### 4.4 ✅ Every citation on every row I recommend in §7 was resolved by hand

`ph03` (`.temp/php12/18-ph03.log`), `ph07` + `ph29`
(`22-ph29-ph07.log`), `ph11` (`15-ph11.log`), `ph12` + `ph31`
(`16-ph12-ph31.log`), `ph16` (`15-ph11.log`), `ph66`
(`19-hashfunc.log`). All exact.

---

## §5 TASK §2.4 — the three settled rows

### 5.1 ⚠⚠⚠ B1 — `ph15` / CRASH-096: the third reading is wrong too, and I measured it

The task file said: *"two prior readings were wrong, so a third being right is
not the way to bet."* **It was right not to bet.**

✅ **The conclusion survives.** `zend_operators.h:128-151` is verbatim as quoted;
`end -= needle_len` is at `:134`; the defect really is a 24-line `static inline`
in a Zend header and **not** in the stream layer. `TASK_PHP_011` §3.3 wins that
argument outright.

⚠⚠ **The MECHANISM is false, and it is the cell the row is built from.**
Part A and Part B both say:

> *"`end -= needle_len` underflows below a **zero-length haystack**"* … *"For a
> zero-length haystack `end` underflows below `haystack`, `while (p <= end)` at
> `:136` is **true under unsigned pointer comparison**"*

`.temp/php12/ph15_probe.c` lifts `zend_memnstr` verbatim and instruments the loop:

```
$ env -u LD_PRELOAD ./ph15_probe
CASE A  real haystack, hlen=0  (the CATALOGUE's blob: 'haystack bytes + a length field + needle bytes')
   loop test `p <= end-nlen`  =>  0x56048ed442a0 <= 0x56048ed4429e  =>  FALSE
   RESULT: returned (nil), loop body entered = 0  --  no fault, correct NULL answer

CASE A2 real haystack, hlen=1 < needle_len=2
   loop test `p <= end-nlen`  =>  0x56048ed442a0 <= 0x56048ed4429f  =>  FALSE
   RESULT: returned (nil), loop body entered = 0  --  no fault, correct NULL answer

CASE B  NULL haystack, hlen=0  (what main/streams/streams.c:844 passes when readbuf is NULL)
   end      = (nil)   end-needle_len = 0xfffffffffffffffe
   loop test `p <= end-nlen`  =>  (nil) <= 0xfffffffffffffffe  =>  TRUE
   RESULT: *** FAULTED, signal 11 ***, loop body entered = 1
```

**A zero-length haystack at an ordinary address gives `end < p`, the loop is
skipped, and `zend_memnstr` returns the correct `NULL`.** The defect fires only
because `haystack == NULL`, so the subtraction wraps **through zero** rather than
merely below the haystack. `streams.c:844` supplies that NULL — the catalogue's
own `▸ trigger` field describes it correctly (*"`readbuf` stays NULL"*) and then
its mechanism and `▸ blob` fields describe something else.

**Concrete failure scenario, and this is why it is a blocker.** An engineer
builds `ph15` from Part B. `▸ blob: haystack bytes + a length field + needle
bytes` gives a kernel that does
`zend_memnstr(buf, needle, nlen, buf + hlen)` over an allocated `buf`. It is
**correct on benign inputs** (criterion 1 passes), it is **correct on the
adversarial input too**, `harness/check.py` compares five rungs that all agree,
and the gate goes **green on a row that models nothing**. The row's `⚠ risk`
field — the field the catalogue says exists to stop exactly this — warns about
the stream layer instead.

**The repair is one clause, not a re-adjudication:** the blob must carry a
"buffer present?" bit and the kernel must pass `hlen ? buf : NULL`, which is
faithful to `php_stream_get_record` (`streams.c:836` fills nothing at
`maxlen == 0`, so `readbuf` stays NULL). ⚠ Say so, because *"pass NULL"* is
exactly what a tidying extraction removes.

⚠ `PROTOCOL.md` rule 9's split applies: **land the conclusion (defect site =
`zend_operators.h:134`, blob-pure, admitted as `ph15`); mark the mechanism
CORRECTED, not merely open** — I measured it.

### 5.2 ✅ `ph09` / CRASH-033 — holds exactly. Clean negative.

`zend_compile.c:2611-2621` read verbatim (`.temp/php12/11-ph09-ph46.log`):
`:2613` nulls both out-params, `:2615 if (mangled_property[0]!=0)` returns early
for an *ordinary* name, so an **empty** name (first byte = its own terminator)
falls through to `:2620 *class_name = mangled_property+1` and
`:2621 strlen(*class_name)`. ✅ The corpus's `c_file_line` does name both frames,
as §3.1 of the 011 report says.

⚠ **m4 (minor):** `ph09`'s `⚠ risk` line says *"the corpus's `c_file_line` points
at a frame 400 lines away in another file. Cite `zend_compile.c`."* — which
contradicts its own body two lines above (*"the corpus **also** names it"*) and
re-asserts the claim `TASK_PHP_011` §3.1 retracted. `.tasks/PROTOCOL.md` rule 13:
the body got maintained, the summary line did not.

### 5.3 ✅ CRASH-053 / `ph46` — the 011 report's correction is exactly right. Clean negative.

`zend_execute.c:138-151`: the NULL test **is** at `:141` and is used correctly for
the unlock; the bug is `:147 return T(node->u.var).var.ptr_ptr;` handing back the
NULL it just detected. `make_real_object` (`:280-292`) is a correct 12-line
function and `:283` is its first dereference — a NULL deref, as the corpus says.
`temp_variable` (`zend_execute.h:30-43`) is confirmed tagless, and
`zend_switch_free` (`:196-217`) discriminates on the same sibling member.
**`ADJUDICATION_001.md` §7b is wrong and `TASK_PHP_011` §3.2 is right.** I tried
to break this and could not.

---

## §6 TASK §2.5 — duplication within the 91

### 6.1 ✅ `ph03` vs `ph07` — NOT one kernel. Clean negative.

- `ph03` (`uuencode.c:141`): a bound **is** computed — `ee = s + (len == 45 ? 60
  : (int)floor(len*1.33))` — and is wrong, while the true end `e` sits unused
  three lines above.
- `ph07` (`mbfilter.c:1202-1210`): ✅ read at source — `for (;;) { m = mbtab[*p];
  n += m; p += m; if (n > from) break; start = n; }`. **There is no bound at
  all**; `string->len` never appears in the loop.

*A wrong bound* and *no bound* are different obligations and different R5s. Also
different tiers (`verbatim` pure-C vs `narrowed`). **Keep both.**

### 6.2 ✅ `ph16` vs `ph17` — a legitimate §3.1 variation, with a build-order caveat

`FD_SET` into a caller-frame `fd_set` vs `BITSET_SET_BIT` into a heap
`cc->bs`. Different macros, different storage class, and the catalogue's own
measurement shows the *detector* differs (ASan blind on the stack one). §3.1
admits it. ⚠ **But the Rust and Verus halves are the same row twice** — "index a
fixed-size bitset with an unvalidated integer" is one obligation. Building both
early buys one ladder result and pays for it twice; §7.3 defers `ph17`.

### 6.3 ✅ `ph19`–`ph22` — four distinct C shapes. Clean negative, with two riders.

Read at `.temp/php12/08-nl2br-wordwrap.log` and `16-ph12-ph31.log`:
`ph19` a product of two attacker values wrapping in an expression; `ph20` the
wrap collapsed **inside `safe_emalloc`'s first argument** so the wrapper is
present and bypassed; `ph21` a 64-bit product narrowed **by the store** with a
provably dead guard disjunct; `ph22` an **accumulation** across two passes of one
format string. Four different things.

⚠ **Rider m8 — the kill bar is applied inconsistently.** `ph19` and `ph20` are
kept apart on a fine distinction (is the wrapper present?), while `CRASH-106`
(nl2br `len + repl_cnt*6`, a **constant** multiplier) and `CRASH-109` (wordwrap
`textlen*(breakcharlen+1)+1`, plus a second `erealloc` growth path at `:692-694`)
are killed as *exact* duplicates on a coarse one. In a corpus where
`PLAN_PHP.md` §3.1 makes only **exact** duplication a kill, *"distinct only in
needing a ~358 MB input, which is a worse kernel"* is a **cost** judgement, and
`C.0` forbids exactly that. Combined with M1 (neither id is carried by `ph19`
or `ph20`), these two are the most likely place the catalogue lost a real row.

⚠ **Rider m5 — `ph28`'s resource claim.** `ph28` says *"it is **the only row in
the catalogue** that [needs a memory budget stated up front]"*. An `int` sizing
wrap needs the product ≥ 2³¹, so `ph19`, `ph21` and `ph22` all have emit loops
that **attempt** ≥ 2 GiB of sequential writes. They fault early under ASan (the
write starts at the head of a small block) so the *input* stays small and the row
is cheap — but an un-sanitised R1/R1h cell walks the heap until it hits an
unmapped page. ✅ `ph28` remains unique in needing 2 GiB **resident**; the claim
should be narrowed to that word, and the other three should carry a one-line
"the emit loop is unbounded; run the adversarial cell under a detector" note.

---

## §7 ⚠⚠ HALF TWO — WHAT WE BUILD FIRST

### 7.1 ⚠ M4 — first, a correction that changes how the picks are scored

The manager's derisking criteria lead with `verbatim`. **12 of the 41 rows that
declare `verbatim` are mis-tiered.** `.temp/php12/tier_check.py` walks back from
each `verbatim` row's defect site to its enclosing function in the pinned tarball
and asks whether that frame is a `PHP_FUNCTION` / VM opcode handler /
argument-parsing frame — all of which `PLAN_PHP.md` §4.1 and `PROTOCOL_PHP.md`
§A1 define as `narrowed` (*"a wrapper comes off (zval unpacking, **argument
parsing**)"*):

```
$ python3 .temp/php12/tier_check.py
   ph05  string.c:240      enclosing: static void php_spn_common_handler(INTERNAL_FUNCTION…  <-- MIS-TIERED
   ph11  zend_execute.c:4033 enclosing: …zend_isset_isempty_dim_prop_obj_handler(  VM-handler <-- MIS-TIERED
   ph12  string.c:4786     enclosing: PHP_FUNCTION(substr_compare)                          <-- MIS-TIERED
   ph21  string.c:4120     enclosing: PHP_FUNCTION(str_repeat)                              <-- MIS-TIERED
   ph22  pack.c:247        enclosing: PHP_FUNCTION(pack)                                    <-- MIS-TIERED
   ph24  datetime.c:358    enclosing: static void php_date(INTERNAL_FUNCTION_PARAMETERS…    <-- MIS-TIERED
   ph35  php_pcre.c:448    enclosing: static void php_pcre_match(INTERNAL_FUNCTION_PARAM…   <-- MIS-TIERED
   ph50  array.c:1893      enclosing: static void _phpi_pop(INTERNAL_FUNCTION_PARAMETERS…   <-- MIS-TIERED
   ph55  zend_execute.c:1761 enclosing: …zend_binary_assign_op_helper( ZEND_OPCODE_HANDLER  <-- MIS-TIERED
   ph59  array.c:4085      enclosing: PHP_FUNCTION(array_map)                               <-- MIS-TIERED
   ph76  array.c:2058      enclosing: PHP_FUNCTION(array_splice)                            <-- MIS-TIERED
   ph80  basic_functions.c:1325 enclosing: PHP_FUNCTION(putenv)                             <-- MIS-TIERED

verbatim rows whose defect site needs a wrapper removed: 12  ph05 ph11 ph12 ph21 ph22 ph24 ph35 ph50 ph55 ph59 ph76 ph80
```

All twelve verified by eye. ⚠ **Three false negatives in my own tool, disclosed:**
it walks back from `line-1`, so a row whose cited line **is** its function header
(`ph09`, `ph15`, `ph61`) reports the *preceding* function. Those three are
genuine `verbatim` — I checked each by hand.

**This is a cost error, never a filter** (`§0.2`). But it is not cosmetic:
`provenance.py` prints the kernel-overlap number **against the declared tier's
expectation** (`verbatim` 50 %, `narrowed` 25 %) and `TASK_PHP_008` §2 demoted
that from a floor to a **report**, moving the judgement to a person
(`PROTOCOL_PHP.md` §F.9). ⚠ **The tier is now the only surviving link between a
row's C and its citation**, and a `verbatim` row landing at 30 % overlap gives
the reviewer a scary number with no way to tell a mis-declared tier from a bad
extraction. `PROTOCOL_PHP.md` §F.9 says *"the first `verbatim` row is where that
stops being true"* — **so this must be fixed before the first row, not after.**

### 7.2 ⚠⚠ M6 — `ph11` is the wrong first row, and the reason is worse than the stated risk

The manager named the risk: *"at `-O2` the compiler may hoist or vectorise the
whole loop and a bounds check may be free — which is a finding, but a poor
property for the row that is supposed to prove the pipeline **measures**
anything."* ✅ **I ran it rather than argued it.** `.temp/php12/ph11m/`: the
`:4033` compare in the kernel shape, driven by 2²⁰ benign offsets read from a
file at run time, at three rungs.

```
$ for b in c_O3 rs_safe_O3 rs_unsafe_O3; do ./$b off.bin; done
C   u64=3013236481096652130 n=1048576
R2  u64=3013236481096652130 n=1048576
R4  u64=3013236481096652130 n=1048576         <- all three agree

=== kernel-exclusive Ir (callgrind) ===
c_O3           11,534,345   ???:kernel
rs_safe_O3     11,010,064   ???:safe::kernel
rs_unsafe_O3   11,010,064   ???:unsafe::kernel

=== the same three at O0 ===
c_O0           32,505,618
rs_safe_O0     51,379,741
rs_unsafe_O0   46,137,116
```

**At `-O3`, safe Rust and unsafe Rust are byte-identical: 11,010,064 both. Both
are 524,281 instructions CHEAPER than C.** Per element: C 11.00, both Rust rungs
**10.50**. The safety column moves by **exactly zero**, and the C↔Rust column
moves the *wrong* way by 0.5 Ir/element.

**The mechanism** (`PROTOCOL.md` rule 12 — *"it vanished" is not a mechanism*),
read off `objdump`:

- C's loop keeps a genuine **signed** compare against a runtime `long`:
  `mov (%rdx),%rcx ; cmp %rsi,%rcx ; jg` then `cmpb $0x30,(%r9,%rcx,1)`.
- Safe Rust's `o <= len as i64` **plus** `usize::try_from(o)` **plus**
  `s.get(u)` collapse to the single **unsigned** compare
  `cmp $0x1000,%rsi ; jb` — the standard `0 ≤ o < len` fold. **Rust's check is
  strictly stronger than C's and costs one instruction fewer**, because C's
  one-sided signed test cannot be folded that way.
- LLVM then **unrolls 2×** (`and $0xfffffffffffffffe,%r9`, two bodies per
  iteration), amortising the loop control that C pays every element.

So the manager's instinct was right and the cause is not vectorisation: the
bounds check is not *elided*, it is **cheaper than the defect it replaces**.

⚠ **What this means for `ph11` as a ROW:** *"no column moves"* is a **finding,
never a kill** (`CLAUDE.md` rule 6, `PLAN_PHP.md` §3). `ph11` stays admitted and
is worth building — the O0↔O3 inversion (safe costs +11 % at O0 and 0 % at O3) is
exactly `PLAN_PHP.md` §5.3's warning demonstrated on real PHP code. ⚠ **But four
of its five rungs will publish the same number, its `verbatim` tier is wrong
(§7.1), and its `u64` on the adversarial input is a fold of whatever byte lives
at `s[-4096]` — a checksum that is a read of foreign memory.** As the row that
must prove the pipeline measures something, it is the worst pick in the shortlist.

⚠ **Honest limit (`PLAN_PHP.md` §5.3):** I searched **one spelling per side**. A
better safe spelling could only widen safe-Rust's win; a better unsafe spelling
cannot help, because safe already equals unsafe **exactly**. The claim *"there is
no safety cost here to price"* is robust to the search I did not do.

⚠ **m4:** `ph11`'s *"Sibling at `:4028`"* is wrong. `zend_execute.c:4028` is the
`ZEND_ISSET` arm — `if (offset->value.lval <= Z_STRLEN_PP(container)) result = 1;`
— which **performs no dereference at all**. It is a wrong-answer bug, not a
memory-safety one. A builder pinning both as OOB reads pins a non-defect.

### 7.3 ⭐ (a) THE SINGLE FIRST ROW: **`ph03` — `php_uudecode`, CRASH-115**

**I ran the admission bar on it rather than arguing it.**
`.temp/php12/ph03_probe.c` lifts `php_uudecode` **verbatim** from
`ext/standard/uuencode.c:126-171` plus `PHP_UU_DEC` (`:66`) and `PHP_UU_ENC`
(`:62`), built with ASan and a **positive control**:

```
===== control =====   (the detector must be live)
CONTROL  writing b[8] of an 8-byte malloc
==1405401==ERROR: AddressSanitizer: heap-buffer-overflow … WRITE of size 1
    #0 … in main .../ph03_probe.c:132

===== benign =====    (PLAN_PHP.md §3 criterion 1)
BENIGN   decoded 45 bytes, round-trip == input: YES
BENIGN   u64 = 12846101660872805163

===== adv =====       (criterion 2)
ADV      src_len=9, declared line length=45 (ee = s+60)
==1405408==ERROR: AddressSanitizer: heap-buffer-overflow … WRITE of size 1
    #0 … in php_uudecode .../ph03_probe.c:41      <- ext/standard/uuencode.c:144
    allocated by thread T0 here: … in php_uudecode .../ph03_probe.c:26   <- :131
```

✅ **Control fires. Benign round-trips with a deterministic `u64`. Adversarial
fires at `uuencode.c:144`, a WRITE.** All four `PLAN_PHP.md` §3 criteria met with
a detector firing and a must-fire control, which is what §3 criterion 2 demands
and what no other candidate has been given.

**Against the manager's own criteria:**

| criterion | `ph03` |
|---|---|
| `verbatim` | ✅ **and it survives §7.1's check** — `PHPAPI int php_uudecode(char *src, int src_len, char **dest)` is a **pure C signature**: no zval, no `TSRMLS`, no `INTERNAL_FUNCTION_PARAMETERS`. 46 lines, `:126-171`. It is the cleanest genuine `verbatim` in the catalogue |
| no allocator | ⚠ **it allocates — deliberately, and this is a feature.** One `emalloc(ceil(src_len*0.75)+1)`, an ordinary small request: **none of T1/T2/T3 fires.** So the shim is *linked, symlinked, digested and executed* without its semantics being the finding. That is the right first exercise of `emalloc_shim.h` — it proves the §B2 machinery works before a row's result depends on it |
| no cursor | ⚠ **it is a cursor row, deliberately.** `s`, `e`, `p`, `ee`, `*p++`, `*(s+1..3)`, `s += 4`. That is `DP-07` — the idiom the census found in **all 22** corpus programs and **zero** of the 33 PAT kernels. Row 1 attacks the project's largest documented coverage gap instead of deferring it |
| `crashes_pristine_5_0_0` | ✅ **True**, `requires` **empty** |
| one-line reproducer | ✅ `convert_uudecode("M" . str_repeat("A", 3))`. `input/crash/CRASH-115.php` is shipped, **and** the corpus's history layer ships a second one at `history/ext/stdext-finds/GIT-f95c1df58349.php` |
| an `echoes` PAT row | ✅ `p16` (TLV walk) — the closest PAT analogue, a length-driven walk |
| an obviously-right `u64` | ✅ **the best in the shortlist.** `u64` = FNV over the decoded bytes + `total_len`. It is a *round-trip*: encode 45 bytes, decode, compare. It cannot be right by accident and it does not read foreign memory |

**Three more things `ph03` buys that nothing else on the shortlist does:**

1. ⭐ **It exercises R1h properly on the very first row, and is set up to deliver
   `PROTOCOL_PHP.md` §C's strongest result.** The corpus's own history layer
   (`history/ext/stdext-verdicts-all.json`, `stdext-canonical.json`) records a
   **second, distinct** uudecode defect — `1e2818b14376`,
   *"uudecode-inner-loop-decodes-past-src-end-oob-read"* at `uuencode.c:145`,
   *"DISTINCT from f95c1df58349 … different crash line, different corruption
   direction"*, fixed only in **2014**. So `kernel_hardened.c` = the real 2004
   `fix_commit` **fixes the write and leaves the source-side over-read
   reachable.** `PROTOCOL_PHP.md` §C: *"An upstream fix is not automatically
   correct … That is a result, and one of the strongest a row can carry. Report
   it; do not repair it."* ⚠ **`1e2818b14376` is not in `index.csv`** (checked),
   so this is outside the catalogue's scope and is a genuine bonus.
2. **The independent agreement is already on record.** The corpus's own note for
   this sha reads *"run5.py: heap-buffer-overflow at uuencode.c:144 in
   php_uudecode, faults_5.0.0=true"*. ✅ **My probe hit the same line by the same
   route.** For a first row, an oracle that two independent efforts agree on is
   worth more than any other property.
3. ✅ **The catalogue's `⚠ risk` field for `ph03` is correct and I confirmed it**
   — *"the row's `cwe` is CWE-125 but the **write** fires first under ASan on
   most inputs"*. Credit where due; that field earned its keep.

⚠ **m8 — a FOURTH suspect corpus label, on this row.** `index.csv` gives
CRASH-115 `cwe = CWE-125, category = out-of-bounds-read` while its **own**
`root_cause_id` is `uudecode-decode-loop-**WRITES**-past-emalloc-on-short-line`
and its **own** history layer says `asan_kind: heap-buffer-overflow`. ✅ My run
says WRITE. **`provenance.cwe` for `ph03` should be CWE-787, and the row should
record the disagreement** — that is corpus-quality evidence and `§0.1` says to
keep it. (The catalogue found three such labels: CRASH-053, CRASH-009,
CRASH-071. This is the fourth.)

⚠ **m6 — a third limb the catalogue does not record, and a builder must not
"tidy" it.** `uuencode.c:158`:

```c
   158  	if ((len = total_len > (p - *dest))) {
   160  		if (len > 1) {
   162  			if (len > 2) {
```

`>` binds tighter than `=`, so `len` receives **0 or 1** and `:160`/`:162` are
**provably dead**. The tail block can only ever emit one byte, and it reads
`*s`, `*(s+1)` at a point where `s` may be at or past `e`. This is `ph59`'s
precedence family living inside `ph03`. It must be lifted **as written**; an R2
port that "fixes" it to `len = total_len - (p - *dest)` has built a different
program. Put it in `spec.md`'s pins.

**Cost: `PROTOCOL_PHP.md` §E — six commands, ~28 min, and the order is
load-bearing.**

### 7.4 ⭐ (b) THE FIRST BATCH — six rows, spatial, chosen to SPAN

Ordered by when to build, not by rank. Every one is spatial per
`PLAN_PHP.md` §8.

| # | row | why it is in the batch | what it is the first test of |
|---|---|---|---|
| 1 | **`ph03`** uudecode | §7.3 | the whole pipeline, `verbatim`, R1h, `DP-07` |
| 2 | **`ph29`** `stream_socket_recvfrom` (CRASH-097) | ✅ verified at source: `long to_read` from `zend_parse_parameters` at `:309`, `emalloc(to_read+1)` at `:321`, `read_buf[recvd]='\0'` at `:332`. `crashes_pristine = True` | ⚠ **the allocator, load-bearing for the first time.** One of only two rows where the T1 truncation *is* the defect. Under plain `malloc` the row **vanishes**, which makes it the only real test of `emalloc_shim.h`'s semantics. Its declared tier `narrowed` is ✅ **correct** |
| 3 | **`ph07`** `mbfl_strcut` (CRASH-124) | ✅ verified: `mbfilter.c:1202-1210`, `for(;;)` with `m = mbtab[*p]` and no consultation of `string->len`. `mbfl_string` reduces to `{val,len}`; `mblen_table` is a static array | ⚠ **the first `narrowed` extraction**, so the first real test of the tiers **and** of `provenance.py`'s overlap report at the 25 % expectation. Also the second `DP-07` cursor, and one of `F22`'s three recoveries — building it validates the recovery |
| 4 | **`ph21`** `str_repeat` (CRASH-107) | `crashes_pristine = True`, one-line reproducer, `echoes p13`, `u64` = a result checksum that is deterministic. ⚠ retier to `narrowed` (§7.1) | **the integer-narrowing family**, and the crispest R5 obligation in the shortlist: `:4145 if (result_len < 1 \|\| result_len > 2147483647)` has a **provably dead second disjunct**, which Verus can state and discharge |
| 5 | **`ph16`** `FD_SET` (CRASH-098) | `verbatim`, `crashes_pristine = True`, `echoes p02`, blob = a list of 16-bit indices | ⚠ **the ORACLE.** The catalogue measured that stock ASan is **silent** at 384 bytes past and that `_FORTIFY_SOURCE` catches it. Build it early *because* it forces a canary/checksum oracle — the machinery every later stack row needs, learned once, on a row whose C is one macro |
| 6 | **`ph12`** `substr_compare` (CRASH-108) | ✅ verified: `:4786 if (len && offset >= s1_len)` — the first conjunct disables the guard; `:4794 s1 + offset` with `offset` an unclamped `long`. `crashes_pristine = True`, `echoes p02` | **the row `ph11` was supposed to be.** Same "no lower bound on a signed index" family, but the consumer is `zend_binary_strncmp` — a real `memcmp` loop, so there is work to measure and the safe/unsafe delta is not one instruction. ⚠ retier to `narrowed` |

**How the batch spans, against the manager's three musts:**
✅ pointer-cursor (`DP-07`): **`ph03`, `ph07`** — two, from the axis PAT has zero of.
✅ allocator-dependent: **`ph29`**, where the shim is load-bearing.
✅ `narrowed`: **`ph07`** (and `ph29`, `ph21`, `ph12` once retiered) — the first
real exercise of the extraction tiers and of `provenance.py`'s overlap report.
Plus mechanism spread: unbounded walk (`ph03`, `ph07`) · sizing/truncation
(`ph29`, `ph21`) · unvalidated index (`ph16`, `ph12`) · stack (`ph16`) vs heap
(`ph03`, `ph21`) vs allocator (`ph29`) storage · two `echoes p02`, one `p13`, one
`p16`, and **two rows with no PAT analogue at all**.

### 7.5 ⚠⚠ M7 — A BLOCKER FOR THE BATCH THAT IS NOT ABOUT ANY ROW

`PROTOCOL_PHP.md` §F item 5 and §C, and `PLAN_PHP.md` §4.4, make
`c/kernel_hardened.c` **the real `fix_commit`, backported and sha-pinned**, and
call that the programme's structural advantage over PAT (*"here we do not
[have to argue our hardening is fair]"*).

✅ **Measured: there is no `php-src` clone on this box.**

```
$ find /home/apt/repos_common -maxdepth 6 -type d \( -name php-src -o -name php-src.git \)
(nothing)
$ python3 -c "…index.csv…"
distinct fix_commit values: 166   lengths: [11, 12, 38, 40]
```

166 distinct 12-hex prefixes and **no repository to resolve them against**.

⚠ **Also: `ph00-smoke` ships no `c/kernel_hardened.c`** (`find patterns-php/ph00-smoke`),
and `harness/build.py:96 has_hardened()` makes the R1h cells conditional — **so
R1h has never been built on the php side at all.** The first row is the first
time both the R1h *cells* and the R1h *provenance claim* are exercised.

**What is available instead**, and it is genuinely useful but weaker: the
corpus's `history/ext/stdext-verdicts-all.json` carries, per sha, a prose
description of the fix — for `ph03`: *"5.0.0 `php_uudecode` has no
`len>src_len` / `ee>e` guards"*.

**The manager owes a decision before row 1 lands, and both options are fine —
what is not fine is shipping `spec.md` text that says "sha-pinned" when nothing
is pinned:**
(a) obtain the patches (a php-src clone, or the 166 diffs extracted once into
`patterns-php/`), and keep §F5 as written; or
(b) re-scope §F5 to *"the fix as the corpus's history layer records it, cited to
`history/ext/…` and to `fix_commit` as an unresolved identifier"* — and then
`PLAN_PHP.md` §4.4's *"here we do not [have to argue]"* must be softened, because
we would be arguing.

⚠ **I recommend (a), and `ph03` is the cheapest place to find out what (a)
costs**: its fix is two guards.

### 7.6 (c) WHAT I WOULD **NOT** BUILD EARLY, AND WHY

⚠ Rows whose **cost or risk the catalogue understates**. None of these is a kill.

| row | the catalogue says | why not early |
|---|---|---|
| **`ph11`** | the manager's prior for row 1 | ✅ §7.2 **measured**: R2 ≡ R4 exactly, both beat R1, four rungs publish one number, tier is wrong, and the adversarial `u64` is a read of foreign memory. Build it as a **finding** row (the O0↔O3 inversion is real and publishable), not as the row that proves the pipeline measures |
| **`ph15`** | *"settled"*, `verbatim`, blob-pure | ✅ §5.1 **measured**: built to its own spec it exhibits **nothing** and the gate goes green. Fix the mechanism and the blob spec first |
| **`ph28`** `concat_function` | *"~2 GiB resident, twice over … a resource cost, not a shape failure"* | ✅ correct, and it is the one row where that is truly irreducible (both operand strings must exist). ⚠ Under `harness/measure.py` this is **28 cells × two 2 GiB allocations**, and `results/` timing prose is taken on a shared box. It is a *scheduling* problem the catalogue prices as a *row* problem. Late, alone, and with the wall-clock column explicitly disclaimed |
| **`ph13`** exif | *"✅ the defect completes at `:3079`, **before** the recursive call"* — reversed out of a cost kill, correctly | ⚠ its `requires` is a **binary fixture** (`bug48378.jpeg`, present) and its blob is a JPEG/TIFF header. That makes it the **only** shortlisted row whose `inputs/gen.py` must reproduce a real file format bit-exactly — a `.memory/03` input-provenance problem on top of the row. Second wave |
| **`ph27`** `php_ereg_replace` | `modelled`, *"a POSIX engine must come along or be replaced by a blob-supplied offset list, **and the substitution is what decides reachability**"* | ✅ the catalogue is right and it is the sharpest `modelled` warning in the file. **The first `modelled` row should not be one where the substitution decides the verdict** — that is `PLAN_PHP.md` §4.3's failure mode (a substituted primitive changing the answer) on the extraction rather than the allocator. Do `ph65` or `ph71` first if a `modelled` row is wanted |
| **`ph17`** | *"ph16's shape on a heap object … its own row"* | ✅ admissible, but §6.2: the Rust and Verus halves are `ph16` again. Build after `ph16` so the second one is nearly free and the pair reads as a storage-class comparison |
| **`ph31`** calendar (CRASH-135) | one of `F21`'s five reversals; *"46 self-contained lines … **there is no library**"* — ✅ **verified verbatim, the claim is exactly right** | ⚠ **its safety delta is `sprintf` vs `format!`.** The memory-safety limb is `calendar.c:280 sprintf(date,"%i/%i/%i",…)` into `char date[16]`, so the R1↔R2 column measures glibc's formatter against Rust's `core::fmt` — a **library** comparison, which is `PLAN_PHP.md` §7 rules 2 and 12's trap. Also `crashes_pristine = False`. Excellent row, wrong job for a first batch |
| **`ph66`** `zend_hash` (LOGIC-001) | *"the **best checksum-visible row in the corpus**, with the allocator entirely out of the picture"* | ✅ I agree with the assessment and it is a strong **wave 2** pick. ⚠ **m7:** the stated blocker — *"the DJBX33A preimage the fixture needs was never computed; compute it before building"* — frames a **one-line computation** as open work. The *integer* key is attacker-chosen, so no search is needed. ✅ Computed, `.temp/php12/20-djb-preimage.log`, from `Zend/zend_hash.h:243-269` with `nKeyLength = strlen+1` and a **signed** `char` accumulator: `$a[5863440] = 'victim'; $a['k'] = 'other'; unset($a['k']);` destroys `'victim'`. Kernel form: insert `(h=5863440, nKeyLength=0)`, then delete with `arKey="k", nKeyLength=2` |
| **`ph91`** | `unresolved` | correctly parked. Needs the reproducer run nobody has taken |

---

## §8 ⚠ CLEAN NEGATIVES — named attacks that did NOT land

`PROTOCOL.md` rule 6. Each of these is an attack I ran and lost; do not re-run
them.

1. ✅ **The coverage claim survives an independent re-derivation.**
   `.temp/php12/indep_coverage.py`, written straight off `index.csv` without
   reading `.temp/php11/coverage.py`:
   ```
   corpus ids in index.csv          : 166
   Part A rows                      : 91   {'spatial': 38, 'type': 22, 'temporal': 31}
   Part B blocks                    : 91
   Part A rows with no Part B block : []
   accounted for                    : 166 / 166
   MISSING (in corpus, in NEITHER)  : []
   named but not in the corpus      : ['V5C-015', 'V5C-116', 'V5C-173']
   ids claimed by >1 Part A row     : {'CRASH-153': ['ph49','ph50'], 'LOGIC-011': ['ph77','ph83'], 'LOGIC-022': ['ph77','ph83']}
   ```
   Every number matches `C.7` exactly. ⚠ **M1 is about the *narrative* of the
   merges, not the arithmetic** — the arithmetic is right.
2. ✅ **`F21`'s central claim — the criterion-3-vs-tier distinction is crisp — I
   could not break.** I looked for a row where "how much C comes along" and "can
   the harmful step be a computation over a blob" genuinely blur, and the closest
   I found (`ph27`, where the substitution decides reachability) is a `modelled`
   *cost* with a `u64` that still exists. The distinction held everywhere I
   pushed.
3. ✅ **`ph09`/CRASH-033 and CRASH-053/`ph46` both survive re-reading at source**
   (§5.2, §5.3). Two of the three settled rows are settled correctly, and the 011
   report's `§7b` correction is exactly right.
4. ✅ **`ph03` vs `ph07` are not one kernel** (§6.1); **`ph19`–`ph22` are four
   distinct C shapes** (§6.3); **`ph16`/`ph17` is a legitimate §3.1 variation**
   (§6.2). The task's three suspected duplication pairs all survive.
5. ✅ **`CRASH-037 / CRASH-101 → ph39` is a real merge, correctly carried** — the
   one set-shaped Part C entry that holds (§3.3).
6. ✅ **A 12-row random citation sample resolves to the claimed C at content
   level**, not merely in range (§4.1) — 46 citations, one defect (`ph68`).
7. ✅ **`ph31`'s *"there is no library"* is exactly true** — `SdnToJulian` is
   `julian.c:154-199`, 46 lines, `#include "sdncal.h"` only, three `#define`s,
   pure integer arithmetic. `F21`'s reversal of CRASH-135 is sound.
8. ✅ **`ph16`'s reversal is sound** — I re-read `streamsfuncs.c:520-547`; the
   `requires RLIMIT_NOFILE` really is a property of the PHP reproducer, not of
   `FD_SET(this_fd, fds)`.
9. ✅ **`§6`'s format judgement is right and I am not asking for it to change.**
   The manager's least-sure call #2 was whether 91 rows at ~100 words is
   readable. It is: Part A is a scannable 113-line table and the six-field
   micro-schema is the reason I could audit 91 rows in one task. ⚠ **The `⚠ risk`
   field is the highest-value field in the file** — it caught `ph03`'s
   write-before-read, which my run confirmed. **Do not move it to `NOTES.md`.**
   The prose that should go is `⚠ trigger`'s duplication with `▸ blob` on the
   ~20 rows where they say the same thing.

---

## §9 Everything I refute, in one list

⚠ `PROTOCOL.md` rule 2. **Reconciliation is the MANAGER's job, not mine** — I am
not carrying a running count forward. **Launched from 45.**

| # | claim | source | verdict |
|---|---|---|---|
| 1 | *"every one of them is a **merge** — the row survives inside another row's `corpus rows`"* | `CATALOGUE.md` C.1, restated in C.7 | ⚠ **false for 6 of 12.** ✅ measured. Those are the silent drops `TASK_PHP_012` §1 forbids |
| 2 | *"LOGIC-003/008/014/018 … all family E … LOGIC-017 was kept because it **forces the flag** rather than failing to clear it"* | `CATALOGUE.md` C.1 | ⚠ **LOGIC-014 and LOGIC-018 also force the flag; LOGIC-008 is the opposite direction.** Three of four refuted by the sentence's own rule |
| 3 | CRASH-021 is a criterion-2 kill *"pending a measurement I did not take"* | `CATALOGUE.md` C.2 | ⚠ **REVERSED.** ✅ `localtime_r(LONG_MAX)` → NULL, `strftime(…,NULL)` → SIGSEGV on this box's glibc 2.39 |
| 4 | CRASH-061 / CRASH-126 / CRASH-163 are *"the same 'fallible call's failure not tested'"* as CRASH-088 | `CATALOGUE.md` C.1, `ph60` | ⚠ **three different mechanisms.** CRASH-126's call **succeeds**; CRASH-163's failure **is** tested; CRASH-061 is `ph90`/`ph50`'s out-parameter shape |
| 5 | *"`end -= needle_len` underflows below a **zero-length haystack** … `while (p <= end)` is **true**"* | `CATALOGUE.md` ph15 (Part A + Part B) | ⚠ **FALSE, measured.** With a real haystack the test is **FALSE** and the function is correct. The trigger is `haystack == NULL` — a wrap **through zero** |
| 6 | 41 rows declared `verbatim` | `CATALOGUE.md` Part A | ⚠ **12 are mis-tiered.** ✅ measured mechanically against the tarball |
| 7 | *"⚠ That is the **ONLY** criterion-3 kill"* (CRASH-017) | `CATALOGUE.md` C.3 | ⚠ **it is not a criterion-3 kill.** It is a `PLAN_PHP.md` §4.3 design decision. Outcome unchanged; the label is `C.0`'s own error class |
| 8 | *"[ph28] is the **only row in the catalogue** that [needs a memory budget]"* | `CATALOGUE.md` ph28 | ⚠ true only of **resident** memory. `ph19`/`ph21`/`ph22` all attempt ≥ 2 GiB of unbounded sequential writes |
| 9 | *"`array_init` … straight over a **live** `IS_STRING` payload"* | `CATALOGUE.md` ph85 | ⚠ the arm requires `str.len == 0`; the leak is **0 or 1 byte** |
| 10 | *"Sibling at `:4028`"* | `CATALOGUE.md` ph11 | ⚠ `zend_execute.c:4028` performs **no dereference**. It is a wrong answer, not an OOB read |
| 11 | *"the corpus's `c_file_line` points at a frame 400 lines away in another file"* | `CATALOGUE.md` ph09 `⚠ risk` | ⚠ contradicts its **own body** and re-asserts what `TASK_PHP_011` §3.1 retracted |
| 12 | *"222/222 citations resolve"* as a citation-quality claim | `TASK_PHP_011` §2.2, `RECAP_PHP.md` F23 | ⚠ **true and insufficient.** ✅ It is structurally blind to `ph68`'s wrong-file inheritance — the very class §2.2 says it swept |
| 13 | *"The DJBX33A preimage the fixture needs was **never computed**; compute it before building"* | `CATALOGUE.md` ph66 | ⚠ it is a **one-line computation**, not a search. ✅ Computed: `$a[5863440]` collides with `'k'` |
| 14 | **`ph11`** as the first row, *"the smallest possible spatial defect"* | `TASK_PHP_012` §3a, spatial miner | ⚠ **the stated risk is real and the mechanism is different.** ✅ Measured: R2 ≡ R4 **byte-identical**, both cheaper than R1, because LLVM folds `0 ≤ o < len` into one **unsigned** compare where C's signed one-sided test cannot fold — and then unrolls 2× |
| 15 | *"`c/kernel_hardened.c` is the `fix_commit` patch backported and **sha-pinned**"* | `PROTOCOL_PHP.md` §C/§F5, `PLAN_PHP.md` §4.4 | ⚠ **unmeetable on this box today.** ✅ No `php-src` clone exists and R1h has never been built on the php side (`ph00-smoke` ships no hardened kernel) |
| 16 | *"the 'ordinary null-deref' set — a mechanism-quality judgement on the C, **which the bar permits**"* | `ADJUDICATION_001.md` §3b | ⚠ **upholding `TASK_PHP_011` §1 against the manager's §5 call #1: the bar does NOT permit it.** The manager's own doubt was correct |

---

## §10 What I did NOT do, and what I am unsure about

1. **I built no row and ran no PHP.** Every probe is a C or Rust lift of the
   pinned tarball's code, not PHP itself. I ran **no reproducer** through a PHP
   binary.
2. ⚠ **I re-derived Part C's criterion for every remaining kill, but I did not
   re-open all 91 Part A rows at source.** I read **~30** at source in full and
   sampled **12** more mechanically. A 91-row source re-derivation is a second
   task. ⚠ Given that M2 and M4 were both found in the parts I *did* open, I
   would expect more in the parts I did not.
3. ⚠ **My `tier_check.py` has a disclosed off-by-one** (§7.1): it walks back from
   `line-1`, so a row whose cited line *is* its function header reports the
   preceding function. That produced three false negatives (`ph09`, `ph15`,
   `ph61`), which I checked by hand. It may therefore **under**-report
   mis-tiering; 12 is a floor, not a ceiling.
4. ⚠ **My `ph11` measurement searched ONE spelling per side** (`PLAN_PHP.md`
   §5.3). See §7.2 for why the conclusion is robust to that and what it would
   take to overturn it.
5. **I did not re-verify `crashes_pristine_5_0_0` for any row** — carried from
   the CSV, exactly as the catalogue's §9.2 discloses.
6. **I did not re-derive one `inv/obl` label or one `echoes` value.** Both remain
   what the catalogue calls them: a hypothesis for the builder.
7. ⚠ **I did not re-run the ASan census.** `CATALOGUE.md` §9.3's *"zero of 2520
   spatial reports fault in `Zend/` or `ext/standard/`"* is still on the
   adjudication's word — `TASK_PHP_011` §8.8 flagged this and it is still owed.
   ⚠ **It matters more now**, because five of my six batch picks are
   `ext/standard/` rows and that number is the reason no `hotness` evidence
   exists for them.
8. ⚠ **`ph03`'s R1h claim in §7.3 rests on the corpus's history layer, not on the
   patch.** I read `stdext-verdicts-all.json` and `stdext-canonical.json`; I did
   not see `f95c1df58349` or `1e2818b14376` themselves (§7.5 — they are not
   obtainable here). The *prediction* that R1h leaves the read reachable is
   therefore a **reading**, stated so a builder can falsify it cheaply on row 1.
9. **The judgement I would most like attacked** is §7.3's trade: I took a row
   that **allocates** and **has a cursor** over the manager's stated "no
   allocator, no cursor". My argument is that the allocation is inert (T1/T2/T3
   never fire) and the cursor is `DP-07`, the reason this programme exists — but
   a manager optimising purely for moving parts would pick `ph31` or `ph12`, and
   that is a defensible different answer.

---

## §11 Memory updates

**None written.** `PROTOCOL.md` rule 9 — nothing here reaches `.memory-php/`
until this report is reviewed. ⚠ **Four things I would propose for it once it
is**, in priority order:

1. ⚠⚠ **`F22` is not a lesson you can learn once.** *A kill written as a set
   hides its members* was discovered **and then re-committed in the same
   document**, with a four-row set whose own discriminating sentence refutes it.
   ✅ **The mechanical form of the rule is what generalises:** a kill covering N
   rows must (a) enumerate the N against `index.csv`, and (b) **be checkable —
   the surviving row must LIST the merged ids**, so that a merge and a drop look
   different to a script. §3.1's checker is nine lines.
2. ⚠ **A coverage check that counts a kill-table mention as coverage cannot see a
   silent drop.** `coverage.py` reported 166/166 over six ids that no row
   carries. The repair is one extra assertion, not a new tool.
3. ⚠ **A citation checker that tests *existence and range* is blind to the
   commonest citation defect this project has** — a bare `:NNN` inheriting the
   wrong file. It passed `ph68` and it passed `ph09`/`ph77` until a human read
   them. ✅ **The content check is cheap** (`.temp/php12/cite_dump.py`): resolve
   the line and **print it**.
4. ⚠ **A `tier` is not free just because it is *"a cost, never a filter"*.** Since
   `TASK_PHP_008` §2 demoted the overlap floor to a report, the declared tier is
   the **only** thing left that says what the printed overlap number should look
   like. A mis-declared tier does not block a row; it silently disarms the last
   fidelity signal the programme has.

---

## §12 The bracket, closed

```
$ python3 harness/measure.py --check-stale
FRESH       results/p49-interned-pool.json             18 source(s) + 9 input(s)
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
FRESH       results/gate/ph00-smoke.json               29 source(s)
FRESH       results/ph00-smoke.json                    19 source(s) + 8 input(s)
2 record(s) examined, 0 STALE
```

✅ **And `git status`, because `PROTOCOL_PHP.md` §E's *"not read-only"* row says a
preflight run can dirty a COMMITTED file as a second-order effect — *"print `git
status` inside every `finally:`, not just the sha256 of what you meant to
touch"*. I ran the preflight twice (open and close):**

```
$ git status --porcelain
?? .tasks-php/TASK_PHP_012_REPORT.md
```

**One untracked file, and it is this report.** `results-php/preflight/` did not
grow — both runs were clean, so they collapsed on content
(`TASK_PHP_008` M3). Nothing under `harness/`, `common/`, `patterns/`,
`results/`, `pilot/`, `.web/` or `RECAP_PHP.md` moved.

**Scratch kept** under `.temp/php12/`: `01`–`22` `.log` (the evidence), the five
`.py` checkers (`c1_merge_check.py`, `cite_dump.py`, `cite_content.py`,
`tier_check.py`, `indep_coverage.py`), the four `.c` probes
(`crash021_probe.c`, `ph15_probe.c`, `ph03_probe.c`), `ph11m/{kernel.c,
safe.rs, unsafe.rs, gen.py}` and `rebuild.sh`. **Binaries, `.bin` blobs and
callgrind output are deleted** — `rebuild.sh` regenerates every one
(`CLAUDE.md` constraint 1).
