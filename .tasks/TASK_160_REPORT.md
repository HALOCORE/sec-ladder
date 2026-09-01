# TASK_160 report — the two admitted CVEs, re-adjudicated BY RUNNING THEM

**Role: research engineer.** Scratch and all evidence: `.temp/t160/`
(`NOTES.md` is the long form; this file is the report).

---

## 0. THE TASK'S OWN HEADLINE PREMISE IS FALSE — first refutation, before any new measurement

`TASK_160` opens: ⚠⚠⚠ **"NEITHER CVE HAS EVER BEEN RUN BY THIS PROJECT"**, on the
strength of `TASK_143_REPORT.md`'s *"`CVE-2021-3518`, `CVE-2022-40304`: **Not
touched.**"*

**The quote is misread.** That cell is in `TASK_143_REPORT.md` **§8**, whose
table is headed *"What the Rust and Verus rungs look like — ⚠⚠ INFORMATION, NOT
A CRITERION"* and whose two columns are **`safe Rust (R2/R3)`** and **`R4 / R5`**.
It says the **Rust and Verus rungs** were not touched. **The C WAS run** — in §6
of the same report, and `RECAP.md` finding 54 quotes the result as
manager-verified:

```
.temp/t143/cve/classify.log
POSITIVE CONTROL: FIRED  -> ERROR: AddressSanitizer: heap-use-after-free
CVE-2022-40304     silent                     attempting double-free
CVE-2021-3518      silent                     heap-use-after-free on
```

`.temp/t143/cve/fetch_and_run.sh` builds both `server.c` plain and
`-fsanitize=address` at gcc `-O1` and runs `normal.py` and `exploit.py` against
both. It exists, it ran, and it is committed.

**Deliverable 1 is still real, because of what that run LACKED**, and the gaps
are the ones this project's own rules name:

1. ⚠⚠ **No fixed/hardened arm at all.** The ports ship only the vulnerable
   program. So the `p28d` lesson — *the detector was never run on the arm the
   safety line touches* — was wholly unaddressed, and admission question 1 is a
   question about exactly that arm.
2. Reproducibility was **2 runs** of an md5 of whole stdout, not 20 of an answer.
3. **UBSan never run. clang never run.** gcc `-O1` only.
4. The positive control was **ASan-shaped only**. Nothing licensed the
   **glibc-allocator** column — and that is the column `CVE-2022-40304`'s *plain*
   build actually trips (`free(): double free detected in tcache 2`).

---

## 1. VERDICTS

| CVE | verdict |
|---|---|
| **`CVE-2021-3518`** | ⚠⚠ **REFUSE ON C-SIDE DUPLICATION OF `p28`** |
| **`CVE-2022-40304`** | ✅✅ **BUILD** |

⚠⚠⚠ **THIS INVERTS THE MANAGER'S CALL AND `TASK_143`'s RANKING.** The task file
names `CVE-2022-40304` as *"the likelier REFUSAL of the two"*; `TASK_143` ranked
it **5th** and `CVE-2021-3518` **7th** (i.e. 3518 closest to the tree). Measured,
the ordering reverses: **40304 is the row, 3518 is the duplicate.**

Neither verdict uses a Rust, Verus, Miri, cost-gradient or ladder-side reason.
The refusal is question 3 and nothing else, with the C quoted from both sides.

---

## 2. WHAT WAS BUILT AND RUN

| file | what |
|---|---|
| `.temp/t160/build_all.sh` | 60 binaries: 2 CVEs × 5 arms × {gcc, clang} × {plain, ASan, UBSan}, `-O1` |
| `.temp/t160/mkharden.py` | the **four hardened arms the ports do not ship**; every substitution count asserted |
| `.temp/t160/mkprobe.py` | the `nodf` diagnostic arm (count asserted) |
| `.temp/t160/matrix.py` | 120 cells × **20 runs** = 2400 launches, 2 m 32 s |
| `.temp/t160/difflines.sh` | each safety line in **preprocessed** lines |
| `.temp/t160/controls.sh` | four positive controls per compiler |
| `.temp/t160/dedup_probe.py` | 40304's emergent harm, isolated |
| `.temp/t160/red/` | both CVEs **reduced to the pinned kernel signature**, built and run |

`gcc 13.3`; `clang` from `~/tools/llvm/bin` (not on PATH). `env -u LD_PRELOAD`
on every child. No sanitizer log truncated.

### 2a. Positive controls — and one could not fire on its first spelling

Four columns are reported, so four controls, each built with the same compiler
and flags as the binaries it licenses: ASan/UAF, ASan/double-free,
**glibc `free(): double free detected`** (the plain-build column), UBSan.

⚠ **The first `ctl_df.c` DID NOT FIRE under gcc `-O1`.** `objdump`
(`.temp/t160/log/ctl_df_gcc_elided.txt`) shows `main()` as a single `puts` — gcc
deleted the whole `malloc`/`free`/`free` sequence. That is the p31
malloc-elision artefact, **in gcc this time**, and *a control that cannot fire
proves nothing*. Recorded rather than quietly fixed; the second spelling
launders the pointer through a non-static `volatile` global and sizes it from
`argc`.

```
== gcc ==                                   == clang ==
asan/uaf         : FIRED                    asan/uaf         : FIRED
asan/double-free : FIRED                    asan/double-free : FIRED
glibc/double-free: FIRED                    glibc/double-free: FIRED
ubsan/signed-ovf : FIRED                    ubsan/signed-ovf : FIRED
controls: 8 fired, 0 did not
```

### 2b. The matrix — **`n_distinct = 1` in all 120 cells**

Every arm under every detector, hardened arms included. Every answer is
**20/20 reproducible** on both compilers at plain, ASan and UBSan.

**`CVE-2021-3518`**

| arm | benign (`normal.py`) | adversarial (`exploit.py`) |
|---|---|---|
| `bug` ≡ `read0` ≡ `destroy0` | `10 passed, 0 failed`, silent | plain & UBSan: **`API_SECRET=sk_live_9x8w7v6u5t4s3r2q`**, *silent*; ASan: **`heap-use-after-free`** |
| `read` (upstream fix) | `10 passed, 0 failed`, silent | `User content here`, **silent in every detector** |
| `destroy` (p28-shaped fix) | `10 passed, 0 failed`, silent | `User content here`, **silent in every detector** |

⚠ **UBSan is silent on the adversarial input on both compilers** — the UB is
purely temporal. `p34`'s shape.
✅ **Both hardened arms are sanitizer-clean on every input** (stage `7h`).

ASan report, untruncated (`log/asan.3518.exploit.txt`): `READ of size 4` at
`render_content lib.c:321`; `freed by` `clear_declarations lib.c:127`;
`previously allocated by` `xmlNewNode lib.c:58`.

**`CVE-2022-40304`**

| arm | benign | adversarial |
|---|---|---|
| `bug` ≡ `intern0` ≡ `cow0` | `10 passed, 0 failed`, silent | plain & UBSan: **`free(): double free detected in tcache 2`**, rc `-6`; ASan: **`attempting double-free`** |
| `intern` (upstream 644a89e) | ⚠ **`9 passed, 1 failed`** | repaired, silent |
| `cow` (un-share before write) | `10 passed, 0 failed`, **byte-identical to `bug`** | repaired, silent |

⚠ **The upstream fix is OBSERVABLE ON BENIGN INPUT in this port.** Its only
benign difference is `"interned":true` → `"interned":false` in
`GET /doc/0/entities`; the content is right in both, but the port's API exposes
the interning decision. **`cow` is benign-invisible, so `cow` is the safety line
a build should use — measured, not preferred.**

The four `*0` arms (the generated trees compiled at `-DSLB_HARDEN=0`) match
`bug` in **every one of their cells**, which is the check that the `#else`
branch is the original program and the generator changed nothing else.

**Detector census over all 120 cells** (`log/matrix.json`; each cell is 20 runs):

```
CVE-2021-3518   bug/read0/destroy0   asan:heap-use-after-free   2 cells   silent 10
CVE-2021-3518   read                 silent 12                  destroy   silent 12
CVE-2022-40304  bug/intern0/cow0     asan:attempting-double-free 2 cells
                                     glibc:free(): double free   4 cells   silent 6
CVE-2022-40304  intern               silent 12                  cow       silent 12
```

✅ **Every hardened arm is silent in 12 of 12 cells — 240 runs each — benign and
adversarial, both compilers, plain/ASan/UBSan.** That is stage `7h` met by
measurement on all four repairs.

---

## 3. THE SAFETY LINES (deliverable 2), in preprocessed lines

`difflines.sh` preprocesses the same source twice with `SLB_HARDEN` 0 and 1 and
diffs, the way `.temp/t143`, `.temp/mgr149` and `.temp/mgr155` do.

| CVE | arm | site | **safety line** |
|---|---|---|---|
| 3518 | `read` | `lib.c::render_content` | **+2 / −5** — a REPLACEMENT (`p35`'s shape). ⚠ **NET NEGATIVE: the repair is three lines SHORTER than the bug** |
| 3518 | `destroy` | `server.c::apply_content_policy` | **+14 / −0** — a pure ADDITION |
| 40304 | `intern` | `lib.c::entity_create` | **+3 / −10** |
| 40304 | `cow` | `lib.c::validate_reference_graph` | **+12 / −2** |

⚠ **Neither CVE has a one-line safety line, and that refuses nothing** — `p28`'s
is a nine-line splice, `p35`'s a reordering. What matters here is the
comparison: **`p28`'s own SINGLY-LINKED spelling measures 15 preprocessed lines;
`CVE-2021-3518`'s destroy-path repair measures 14.**

---

## 4. THE SIGNATURE QUESTION — answered with two reductions, not an opinion

`.temp/t160/red/k3518.c` and `k40304.c` implement each mechanism behind
`kernel(buf, buf_len, off, len) -> u64` driven by a byte-stream opcode loop, at
`SLB_HARDEN` 0/1/2 × {gcc, clang} × {plain, ASan}. Positive control fires on
both compilers. **Both mechanisms survive the reduction.**

⚠ **The task's specific worry does not happen.** *"If reducing `CVE-2022-40304`
to a kernel loses the shared dict, it loses the deduplication."* It does not:
the dict is a bump arena plus a hash table **living inside the kernel**, which is
`p27`'s stated precedent (*"a file cannot name a pointer, but it CAN name an
operation that saves one"*) and `p32`'s pool restated.

```
k3518   benign  191303283128738         H=0 = H=1 = H=2, both compilers
k3518   adv     H=0  117576099934009    [ASan heap-use-after-free]
                H=1  6414870147         [clean]   <- read-path repair
                H=2  6414870147         [clean]   <- destroy-path repair (p28's)

k40304  benign  6472294297349180934     H=0 = H=1 = H=2
k40304  adv     H=0  17113680355010809990   [ASan SILENT]
                H=1  1156967019954588610    [clean]   <- copy-on-write
                H=2  1156967019954588610    [clean]   <- provenance (upstream)
```

⚠ **A divergence alone only proves the walk went somewhere else.**
`red/leaktest.sh` varies the OFF-TREE secret node's value and nothing else:

```
gcc   H=0 bug          117576099934009   117576099963831   SECRET REACHES ANSWER
gcc   H=1 fix/read     6414870147        6414870147        secret invisible
gcc   H=2 fix/destroy  6414870147        6414870147        secret invisible
      (clang identical)
```

So the buggy kernel really folds the value of an object that is **not in the
tree** — the port's information disclosure, preserved by the reduction.
**All 24 reduction cells: 1 distinct answer in 20 runs.**

### ✅ A CLEAN NEGATIVE — an attack on the `read` repair that did NOT land

The upstream `read` fix is a **narrowing**, not a guard addition: it stops
descending into an entity-ref's children *unconditionally*, where the blacklist
descended whenever the child was not a declaration. So the obvious attack is:
**find a benign input where the aliased pointer is still LIVE, and the two arms
must disagree.**

**It does not land, and for a reason rather than by luck.** `k3518.benign.bin`
is exactly that input — three WALKs with **live** declarations and live
ref→decl links, no DROP anywhere — and H=0, H=1 and H=2 all return
`191303283128738` on both compilers. The reason: the blacklist's excluded set
*contains* `XML_ENTITY_DECL`, so the buggy arm **already** declines to descend
into a live declaration; the arms can differ only once the child is no longer a
declaration, i.e. once it has been freed and reused. **Do not re-run this
attack.**

---

## 5. ⚠⚠ SECOND REFUTATION: `CVE-2022-40304`'s DOUBLE FREE IS **WRITTEN**, NOT EMERGENT

`TASK_143`'s admission (quoted in `RECAP.md` finding 54 and in `TASK_160` itself)
says *"the double free is **emergent, never written**"*.

`src/CVE-2022-40304/lib.c` 229–236:

```c
if (e->owner_id == owner && e->in_use) {
    *pp_iter = e->next;
    free(e);
    p->num_entries--;
    p->total_released++;
    free(e);                 /* <-- the same pointer, three lines later */
    continue;
}
```

**gcc diagnoses it at compile time, with no input at all:**

```
lib.c:234:17: warning: pointer 'e' used after 'free' [-Wuse-after-free]
lib.c:231:17: note: call to 'free' here
```

and the ASan report puts both frees in `pool_reclaim_owner` at `lib.c:231` and
`lib.c:234`. ⚠ **Both hardened arms still contain that statement and still emit
that warning** — the safety lines only make it unreachable.

### So what does the mechanism produce on its own?

`mkprobe.py` builds `nodf` = the pristine port with the second `free(e)` deleted
and nothing else. `dedup_probe.py` then drives the sequence the mechanism
actually needs — **two documents sharing one interned buffer**:

```
nodf   [0] VICTIM   POST /doc  keep=<&b;>       -> 201
           VICTIM   GET  /doc/0 BEFORE          -> 200 b'keep\t&b;\t\n'
       [1] ATTACKER POST /doc  a=<&b;> b=<&a;>  -> 400 'cycle detected'
       [2] VICTIM   GET  /doc/0 AFTER           -> 200 b'keep\t\t\n'
           server exit=0
VERDICT: CROSS-DOCUMENT CORRUPTION ... no free, no dangling pointer, no UB
intern / cow -> VERDICT: doc 0 unchanged
```

⚠ **ASan is clean in the `nodf` cells**: HTTP 200, wrong content, exit 0.

✅✅ **THE MECHANISM'S OWN HARM IS A WRONG VALUE CROSSING AN OWNERSHIP BOUNDARY,
WITH NO FREE ANYWHERE AND EVERY DETECTOR SILENT.** The port's `abort()` is a
hand-written duplicate statement layered on top of it. **This strengthens the
row and weakens the port**: a build must implement `pool_reclaim_owner` without
the duplicated statement.

---

## 6. `CVE-2021-3518` — REFUSE, C-SIDE DUPLICATION OF `p28`

### The C, from both

**`p28`** (`patterns/p28-intrusive-lists/c/kernel.c`) — the free site, TRIM:

```c
/* TRIM. Reclaim the oldest object. It arrives here
 * through the EVICTION LIST and therefore holds no hash-chain cursor. */
if (tail != NULL) {
    victim = tail;
    if (victim->lp != NULL) victim->lp->ln = NULL; else head = NULL;
    tail = victim->lp;
    free(victim);
```

— and the use site, GET (its own shipped comment: *"In R1 the chain can still
contain a FREED object, and `n->key` / `n->val` is then a use-after-free READ"*):

```c
n = bucket[b];
while (n != NULL && steps < P28_SLOTS) {
    steps++;
    if (n->key == a) { found = 1; break; }
    n = n->hn;
}
```

**`CVE-2021-3518`** (`../LearnVeri/microbench/CVE-2021-3518/lib.c`) — the free
site:

```c
static void clear_declarations(XmlNode **entities, int entity_count) {
    for (int i = 0; i < entity_count; i++) {
        if (entities[i]) {
            free(entities[i]->name);
            free(entities[i]->content);
            free(entities[i]);
            entities[i] = NULL;
        }
    }
}
```

— and the use site, `render_content`:

```c
if (cur->children != NULL) {
    int child_type = cur->children->type;
    if (child_type != XML_ENTITY_DECL &&
        child_type != XML_XINCLUDE_START &&
        child_type != XML_XINCLUDE_END) {
        cur = cur->children;
        continue;
    }
}
```

### The shared mechanism, limb for limb

| limb | `p28` | `CVE-2021-3518` |
|---|---|---|
| object registered twice | eviction list **and** hash chain | `doc->entities[]` **and** the entity-ref's `children` |
| destroy reaches it through | the eviction list | `entities[]` |
| destroy clears | the eviction list **only** | `entities[i]` **only** |
| stale pointer lives in | another heap object's `hn`, or `bucket[]` | another heap object's `children` |
| use | a chain walk dereferences it | a tree walk dereferences it |
| repair (as built here) | 9-line splice (doubly linked) / **15 lines** (singly linked) | **14 lines** (singly linked — measured) |

`p28`'s own `kernel.c` states the CVE's mechanism in the CVE's own terms: *"the
whole of the bug is that one of the two lists is left holding a pointer to
storage the program has returned to the allocator."*

### The admission's sole distinguisher, refuted twice

`TASK_143` admitted it as *"same family as `p28` … distinguished by ONE sharp
property: **the guard IS the UB**, so the check cannot be written at the point of
use."*

1. ⚠⚠ **A check CAN be written at the point of use — I BUILT IT AND RAN IT.**
   The `read` arm repairs the adversarial input at **+2 / −5 preprocessed lines,
   at the point of use**, is benign-identical, is ASan-clean, and is 20/20
   reproducible on both compilers. It is not a *validity conjunct* — it is a
   whitelist on the traversal's own owned, live state — but *"the check cannot be
   written at the point of use"* is the operative clause, and it can.
2. ⚠⚠ **The property is not unique to it.** `p28`'s GET dereferences a
   possibly-freed `n` inside `if (n->key == a)` and again at `n = n->hn`, before
   anything about `n` has been decided. Reading through the pointer whose
   validity is in question is `p28`'s read path too.

And the **p28-shaped destroy repair also works here**, at p28's site and p28's
size (14 against p28's measured 15). The row would land on `p28`'s mechanism,
`p28`'s harm and `p28`'s repair site.

⚠ Not `p34` either: `p34`'s read path is correct by construction and its repair
is on the ACQUIRE. Nothing here is refcounted.

### ✅ What the refusal should NOT lose — a finding for `p28`'s row

**A program with `p28`'s mechanism can additionally admit a READ-PATH repair,
and here that repair is SMALLER THAN THE BUG (`+2 / −5`, net −3 preprocessed
lines), because the traversal has an owned, live alternative source for the same
decision (`cur->type` instead of `cur->children->type`).** `p28`'s own kernel
says *"There is no test to add on this rung's read path"*, and for `p28` that is
true; this CVE shows it is a property of `p28`'s particular structure and not of
the mechanism. **Two repair sites, one of them free and one of them p28's** —
that belongs in `p28`'s row, not in a row of its own.

---

## 7. `CVE-2022-40304` — BUILD

### The C mechanism

Content shorter than `INLINE_THRESHOLD` is **INTERNED** in a shared,
bump-allocated arena and **DEDUPLICATED**, so two independent records
legitimately hold one buffer — correctly, intentionally, benignly. A later
cycle-breaker then **WRITES through that borrowed pointer**.

```c
/* the alias is CREATED here -- and it is CORRECT */
if (ent->byte_length < INLINE_THRESHOLD) {
    ent->content = (char *)pool_intern(pool, content, (int)ent->byte_length, owner);
    ent->content_interned = 1;
    ...
/* the harm is HERE -- a WRITE through storage this record does not own */
if (ent->content_interned) ent->content[0] = '\0';
```

Nothing is ever freed. Every index is in bounds. There is no dangling pointer
and no stale handle.

### Distinct from all six temporal rows, and from `p08` and `p38`

| built row | its C | why this is not it |
|---|---|---|
| `p27` | handle table, missing liveness test on the READ | a real `free`; here **nothing is ever freed** |
| `p28` | object on two lists, destroy leaves one behind | a real `free`; here no dangling pointer exists at all |
| `p29` | save a stack pointer, free, read through it | same |
| `p34` | missing retain on publish → early `free` | same; and there is no refcount here |
| `p25` | `realloc` relocates; interior pointer goes stale | the arena never moves and never relinquishes |
| **`p32`** | stale handle double-pushed → free-list self-loop → two handles alias one block | ⚠⚠ **the closest call, and it INVERTS.** `p32`'s alias is *created by the bug*, its block has been **recycled**, and its safety line asks a **lifetime** question about the block (`gen[h] != g`). Here the alias is created **by design**, nothing is stale or recycled, and the safety line asks an **ownership** question about the *writer*: *is this buffer mine to write?* `p32`'s alias IS the harm; here the alias is the CONTRACT and the WRITE is the harm. By `composition.py`'s own stated test — *what does the safety line ASK?* — they ask different questions. |
| `p08` | `memmove`/`memcpy` with overlapping regions | one call, no shared-ownership structure, no dedup, no table |
| `p38` | strict-aliasing pun: two incompatible **types** over one object; harm is a **miscompile** | same type, same object, two **owners**; harm is a wrong value at `-O1` on both compilers |

### A fourth repair-site position

`harness/tools/composition.py`'s `CAVEATS` records three: `p27`/`p29`/`p32` fix
the **READ**, `p28` fixes the **DESTROY**, `p34` fixes the **ACQUIRE**. This
row's two working spellings are the **PROVENANCE** (never borrow) and the
**MUTATION** (un-share before writing). Neither is any of the three.

### And a harm class the tree does not have

**A wrong value crossing an ownership boundary with no free, no dangling
pointer, every index in bounds, and every detector silent.** The *silence* is
`p32`'s shipped shape — arrived at from a completely different C program, which
is what makes it worth a second row rather than a duplicate.

---

## 8. WHAT A BUILD OF `CVE-2022-40304` WOULD OWE (deliverable 5)

1. ⚠⚠ **Stage `7h`** — hardened arm sanitizer-CLEAN on EVERY input. ✅ Met by
   `cow` in this task's evidence (240 port runs: 2 phases × 2 compilers × 3
   detectors × 20, all silent; plus the reduction's H=1/H=2 ASan-clean on both
   blobs). ⚠ **But it is met only because the safety line makes the port's
   duplicated `free(e)` UNREACHABLE, not because it is gone.** A pattern must
   implement `pool_reclaim_owner` **without** the duplicated statement —
   otherwise `c/kernel_hardened.c` carries a latent double free that `-Wall`
   complains about, and admission question 1 is a question about exactly that
   arm (`p28d`'s lesson, in the row that produced it).
2. **`verus.assumptions`** if any rung uses `assume(`/`admit(`. ⚠ **I did not run
   Verus and I claim nothing.** The reduction's shape *suggests* it may not be
   needed: `k40304.c` has no raw pointers and no `free`, and the borrowed pointer
   is naturally modelled as an INDEX into a kernel-owned array — `p32`'s
   already-proved shape (`15 verified, 0 errors`, TCB 5). The new obligation
   would be a **disjointness / provenance** one — *no record's content range
   aliases another's at a write* — which nothing in the tree states. Unmeasured.
3. **The safety line is `cow`, not the upstream `intern`.** Measured in §2b.
4. The adversarial input must contain a **deduplicating pair**;
   `red/run.sh`'s `k40304.adv.bin` is the shape (`a` and `a+7` collide by
   construction).
5. Usual pattern furniture: `spec.md` pins, `model.py` written FROM THE CONTRACT
   (not transliterated from `kernel.c` — `p23`/`p29`'s hazard), `inputs/gen.py`,
   `c/main.c`, separate `c/kernel.c` and `c/kernel_hardened.c` translation units.

---

## 9. THE PROCESS GAP (deliverable 6)

```
$ grep -c '^| p[0-9]' .memory/06-catalogue.md
48
$ grep -n 'CVE-2021-3518\|CVE-2022-40304' .memory/06-catalogue.md
(nothing)
```

⚠⚠ **Neither CVE has a catalogue row.** Their entire status lives in `RECAP.md`
prose and in task reports — while `RECAP.md`'s own START HERE box instructs
*"READ THE CATALOGUE CELL, NOT `TASK_143_REPORT.md`"*. For these two there is no
cell to read, and the one artefact the project calls authoritative has never
mentioned them. **This is the same class as PROTOCOL rule 1's missing-finding
loop: a row is only findable where a reader looks.**

**Proposed cells — written out in `.temp/t160/NOTES.md` §9, NOT written into
`.memory/`.** One `p49`-shaped row for `CVE-2022-40304` (ADMITTED, upheld,
`cow` safety line, fourth repair site, and the *written-not-emergent* correction),
and one refusal note for `CVE-2021-3518` naming `p28` and quoting both sides.

---

## 10. Problems, and what I did NOT do

- **Everything is at `-O1`.** No `-O0`/`-O2`/`-O3` sweep, no `Ir`, no wall
  clock, no `harness/` — `check.py`/`measure.py` are forbidden by the task and
  the bar forbids a cost number from deciding anything.
- **No Verus run.** §8 item 2 is explicitly a suggestion, marked unmeasured.
- **No Rust rung of any kind.** The corpus's `rust/` and `rust-formal2/` were not
  even copied. What they can and cannot inherit is unchanged and untested.
- **My reductions are DEMONSTRATIONS, not patterns.** One file each; no
  `spec.md`, no `model.py`, no `inputs/gen.py`, no split translation units, no
  `contract_sha256`. PROTOCOL definition-of-done rule 6 does not apply — no
  `slb-contract` block was written.
- **`matrix.py`'s first answer regex for 40304 was wrong** and reported
  `n_distinct=1` for a crashing and a non-crashing cell alike, because it matched
  the warmup `Status: 201` line present in every arm. Recorded in the file
  itself, not silently fixed. *A "reproducible" answer that cannot distinguish
  the arms is not an answer.*
- **`red/demo.h`'s first version did not compile** — a `patterns/*/c/main.c` in a
  block comment closed the comment early. Fixed with an asserted substitution.
- I read both `root-cause.md` files, both `lib.c` end to end, both `server.c`'s
  relevant handlers, and the drivers. I did **not** read `orig-detailed-chain.md`
  (789 lines) end to end.
- The `intern` arm's benign failure is a failure of **the port's own test**, not
  a proof that the upstream fix is wrong; a kernel returning a `u64` would not
  expose the `interned` flag. I report it because it is what the port measures.
- I did **not** attempt a spelling of `CVE-2021-3518` that escapes `p28`. If a
  manager wants one, the burden is a C mechanism that is not
  *register-twice / clear-one / dereference-the-other*, and I did not find one.

---

## 11. Deliverable checklist

| # | deliverable | status |
|---|---|---|
| 1 | run both, per (arm × input × build), 20 runs, detectors, positive controls | ✅ 120 cells × 20; 8/8 controls; every arm under every detector |
| 2 | name and count each safety line in preprocessed lines | ✅ four measured; neither is one line, and that refuses nothing |
| 3 | a verdict per CVE, `BUILD` or `REFUSE ON C-SIDE DUPLICATION` | ✅ REFUSE (`p28`) / BUILD, C quoted from both |
| 4 | reproducibility and environment stated honestly | ✅ 1 distinct in 20, all 144 cells (120 port + 24 reduction) |
| 5 | what a `BUILD` owes — `7h`, `verus.assumptions` | ✅ §8, with the `7h` caveat that matters |
| 6 | the process gap; propose cells, do not write them | ✅ §9 + `NOTES.md` §9 |
| — | the signature question, with a reduction | ✅ §4, both reductions built and run |

---

**PROTOCOL rule 2 running count: launched from 911, +3 = 914.**
The three: *(1)* the task file's headline *"neither CVE has ever been run"* —
false, `TASK_143` §6 ran both and `RECAP` 54 quotes it; *(2)* `TASK_143`'s
*"the double free is emergent, never written"* — false, it is a literal
duplicated `free(e)` that gcc diagnoses with no input; *(3)* the manager's call
that `CVE-2022-40304` is the likelier refusal — inverted by measurement, and
`TASK_143`'s 5th-vs-7th ranking with it.
⚠ **Reconciliation across branches is the manager's job, not mine.**

---

## 12. Housekeeping, checked rather than assumed

- **Artefacts deleted, generators kept.** `bin/` (54 MB), `red/bin/` (22 MB) and
  `red/blob/` are gone. `.temp/t160/run_all.sh` regenerates every binary, blob
  **and log**, and was verified end to end on an emptied tree
  (`log/run_all_smoke.log`, `rc=0`) *before* the deletion.
- **`../LearnVeri/` was never written.** `git status` there shows
  ` M PITFALLS.md`; it is **not mine** — mtime `2026-08-17 18:44:40`, two weeks
  before this session, and the diff is sec-ladder `TASK_008` Verus material.
  Checked, not assumed.
- **`git status` in sec-ladder: `?? .tasks/TASK_160_REPORT.md` and nothing
  else.** No `.memory/`, `RECAP.md`, `results/`, `harness/`, `synthesis/`,
  `patterns/` or `pilot/` file touched; no earlier `.temp/t*/` or `.temp/mgr*/`
  directory written. `harness/check.py` and `harness/measure.py` never run.
  No `git add`, no `git commit`.
- **No waiter left running.** Every background wait used a `.done` sentinel, not
  `pgrep -f`. The one surviving `until [ -f … ]` process on the box belongs to a
  DIFFERENT session (`…-sec-ladder--web`) and was neither started nor touched by
  me.
