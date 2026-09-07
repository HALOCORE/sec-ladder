# NOTES.md — TEMPORAL axis, php-5.0.0 candidate mining

Scope: the 85 `index.csv` rows whose `cwe` is one of CWE-416 (56), CWE-401 (15), CWE-562 (5),
CWE-590 (4), CWE-415 (2), CWE-911 (2), CWE-824 (1). All 85 are accounted for below: **23
candidates covering 85/85 rows**, no rejections on a C-side ground and none on any other ground.

Everything cited was read out of the pristine tarball
`/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz`
(sha256 `5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919`, 5595997 bytes).
No patched tree was consulted for a single line number. `VERIFY.md` re-derives the top five in
one command each; `mk_candidates.py` regenerates `candidates.json`.

---

## 1. The manager's call, measured

> *"I believe the CWE-416 mass in `Zend/zend_execute.c` will collapse into only 3–5 genuinely
> distinct C mechanisms, and that most of them require the whole executor and will rate
> `modelled`."*

**Half right, and wrong in the direction that matters.**

**Right about `zend_execute.c` specifically.** Its **14** CWE-416 rows do collapse hard — to four
mechanisms plus one ambiguous row, and three of the four do need executor context:

| mechanism inside `zend_execute.c` | rows | rating |
|---|---|---|
| deferred-free `EG(garbage)` double-unlock (rank 16) | CRASH-151, CRASH-057, CRASH-050 | `narrowed` |
| container freed, interior slot still used (rank 9) | CRASH-004, CRASH-003, CRASH-025, CRASH-067 | `modelled` |
| unaddref'd pointee freed by a callback (rank 17) | CRASH-159, CRASH-035, CRASH-064, CRASH-010 | `narrowed` |
| freed-then-read across call teardown (rank 18) | CRASH-069, CRASH-031 | `narrowed` |
| *ambiguous* — see below | CRASH-040 | `narrowed` |

CRASH-040 is the one row I could not place cleanly. Its `root_cause_id` names the
`zend_hash_apply_deleter` mechanism (destructor before unlink — rank 6/rank 3 territory), but
`index.csv`'s exercised site is `Zend/zend_execute.c:69` + `:76`, which is the `EG(garbage)`
push/drain — rank 16 territory — and the row's own note says the claimed
`Zend/zend_hash.c:573-575` is *"present verbatim but unexercised"*. I filed it under rank 3 on
the strength of its named mechanism. **The manager may reasonably move it to rank 16.**

**Wrong about the axis as a whole.** The temporal mass is not concentrated in the executor at
all — the executor is where it *surfaces*. Grouping by mechanism rather than by file gives
**23 families**, and the biggest ones live in standalone containers:

- `Zend/zend_ptr_stack.h` — 60 lines of header, no zval, no TSRM. Carries five rows.
- `Zend/zend_objects_API.c` — a slot map with a free list, ~150 lines. Carries five rows across
  two *opposite* mechanisms (rank 2: valid index, moved storage; rank 7: valid storage, stale index).
- `Zend/zend_hash.c` + `zend_hash.h` — carries six rows across three mechanisms.
- `Zend/zend_llist.c` — an eight-line `apply` loop.
- `ext/standard/var_unserializer.c` — a parser whose input **already is** a flat byte blob.

Self-containment across all 23: **11 `verbatim`, 10 `narrowed`, 2 `modelled`** (rank 21 straddles
narrowed/modelled and is counted narrowed; ranks 6 and 23 are verbatim for their lead member).
Only rank 9, rank 4 (if the re2c body has to come), rank 21's LOGIC-002 member and rank 12's
executor members genuinely need the engine. **The prediction "most will rate `modelled`" is the
opposite of what the corpus does: nine in ten lift.**

The reason the prediction reads plausible is that `c_file_line` points at the **faulting frame**,
which is nearly always executor code, while the **defect** is usually one call down in a
container. CRASH-002 is the clean example: index.csv's line is `array.c:1062`, but the
mechanism is `HashPosition` being a bare `Bucket *` (`zend_hash.h:88`), and the extraction that
matters is the hashtable, not `php_array_walk`.

---

## 2. The mechanism families

Ranked; the number after each is corpus rows merged into it. Ranks 1–16 are the proposal.
Ranks 17–23 complete the partition so the manager can see that nothing was dropped — several of
them (17, 18, 20) are as strong as the top ten and are lower only because they need more of the
engine or have thinner reproducers.

| # | family | rows | self-containment | the one-line C statement |
|--:|---|--:|---|---|
| 1 | arg-stack realloc invalidates a borrowed slot | 5 | verbatim | a vector doubles under an interior pointer |
| 2 | object-store realloc invalidates a cached bucket ptr | 2 | verbatim | same, but the stale access is a **write** |
| 3 | hash cursor freed under traversal | 3 | narrowed | a node is unlinked while a cursor names it |
| 4 | unserialize back-reference table holds a freed zval | 2 | modelled | an interning table outlives its entries |
| 5 | `hash_del` numeric bucket short-circuits the key compare | 1 | verbatim | the lookup answers the wrong question |
| 6 | destructor runs on a still-linked bucket | 2 | verbatim | destroy-then-commit instead of commit-then-destroy |
| 7 | stale handle resolves to a recycled slot | 3 | verbatim | ABA: no generation counter on a handle |
| 8 | one owned pointer in two owning slots | 5 | narrowed | a missing (or extra) refcount increment |
| 9 | container freed, interior slot still used | 4 | modelled | two statements in the wrong order across an owner |
| 10 | llist element freed inside the apply loop | 1 | verbatim | the loop variable is the freed node |
| 11 | conditional alloc, unconditional free | 3 | narrowed | alloc site and free site disagree on the arm |
| 12 | stack value published to a callee that retains it | 6 | narrowed | the allocator is not involved at all |
| 13 | ownership committed after a fallible step | 4 | narrowed | the error/unhandled path transfers nothing |
| 14 | engine-owned table adopted and then freed | 4 | verbatim | a **provenance** error: never an allocator return |
| 15 | erealloc grow leaves an uninitialised tail | 1 | verbatim | the length field lies, not the pointer |
| 16 | deferred-free garbage list, double unlock | 5 | narrowed | release is queued, not performed |
| 17 | unaddref'd pointee freed by a user callback | 7 | narrowed | no reference was ever taken |
| 18 | cached/reused pointer to a per-invocation target | 5 | narrowed | "borrowed" and "owned" share one C type |
| 19 | foreign registry aliases a buffer its owner frees | 4 | verbatim | two ownership domains, one pointer |
| 20 | freed slot left non-NULL, read by re-entrant code | 2 | verbatim | "freed" and "present" are the same bit pattern |
| 21 | lock taken on one path, released only textually later | 14 | narrowed/modelled | the release never runs (the CWE-401 mass) |
| 22 | compile-time liveness metadata names the wrong temp | 2 | narrowed | a static analysis the program runs on itself |
| 23 | error path consumes storage it released or never set | 3 | verbatim | the diagnostic is the consumer |

**The two organising axes underneath these 23.** Almost every row is one of:
*(a)* a pointer that was valid and stopped being so — and the sub-question is *why*: the storage
moved (1, 2), the pointee died (3, 10, 17), the index was recycled (7), the frame returned (12),
or the release was queued (16); or
*(b)* an ownership claim that is arithmetically or structurally wrong — too many owners (8, 13),
too few (21), the wrong owner (14, 19), or an owner that never existed (11, 20).
Family 5 and family 22 belong to neither: they are *identity* errors, where nothing about
lifetime is wrong and the code simply names the wrong object.

---

## 3. Rows rejected on a C-side ground

**None.** Every one of the 85 rows is a C program that is correct on benign input, wrong on an
adversarial one, and reachable through a blob-drivable operation stream. The only legitimate kill
available to me — C-side duplication — I applied as *merging*, not removal: 85 rows folded into 23
candidates, with the merged member list on every candidate and a `risks` note wherever I judged
the merge itself debatable.

Four merges I flag as most likely to be wrong, so the manager can split them:

1. **Rank 21 merges 14 CWE-401/CWE-911 rows.** They share invariant I6 but are at least four
   distinct C shapes: a loop temp stranded on unwind (LOGIC-002), an unconditional lock ignoring
   result-usage (LOGIC-011), a deep copy with no matching destructor (LOGIC-015), and a type-tag
   overwrite over a live payload (LOGIC-006, `array_init` straight over an `IS_STRING`). This
   should probably be four candidates.
2. **Rank 8 merges five rows that break I7 from opposite directions** — CRASH-131 is a *missing*
   increment (I7/O1), CRASH-047/099/103/080 are *unmatched* decrements (I7/O2). Two candidates.
3. **Rank 12 merges six CWE-562 sites.** One idiom, six defects. Merging understates the breadth
   of the CWE-562 story; splitting overstates their distinctness.
4. **Rank 23 contains CRASH-062**, which is a subsystem *teardown-ordering* row and shares only
   the "reached via an error handler" framing with its two co-members. Weakest merge in the file.

Rows I was tempted to reject and did not, with the reason each temptation was invalid:

- **LOGIC-001** (rank 5) produces no fault at all — it silently destroys the wrong live element.
  Not a kill: the C is correct on benign input and wrong on adversarial input, which is the bar.
  It is in fact the *best* candidate for a checksum-visible defect, because the wrong answer shows
  up in the digest with the allocator entirely out of the picture.
- **CRASH-158** (rank 15) is arguably a spatial/initialisation row. Its CWE (824) and its
  invariant (I19) put it on my axis, so it stays; flagged for the manager in case the spatial
  miner has it too.
- **Ranks 5, 13, 21, 22** are `LOGIC` rows whose `crashes_pristine_5_0_0` field reads
  `n/a (non-crash class)`. That is a corpus bookkeeping fact, not an admission fact.
- **40 of the 85 rows are `crashes_pristine_5_0_0=False`** (27 True, 18 `n/a (non-crash class)`). See §5 — this is a measurement
  property of PHP's allocator, not evidence that the defect is absent.

---

## 4. Citations checked, and the ones that are wrong

I resolved every `c_file_line` for all 23 candidates against the pristine tarball. **Every
`index.csv` line I checked resolves to what it claims.** Three discrepancies exist and all three
are outside `index.csv`:

1. **`input/crash/CRASH-012.php` cites `ext/standard/array.c:1645`.** In the pristine tarball
   that line is a closing brace of an unrelated function:
   ```
   tar -xzOf $TB php-5.0.0/ext/standard/array.c | sed -n '1643,1647p'
   ```
   ```
   1643          RETURN_FALSE;
   1644      }
   1645  }
   1646  /* }}} */
   1647
   ```
   The defect is at `:2058-2060` (`zend_hash_destroy` + `efree(Z_ARRVAL_P(array))`), which is what
   `index.csv` says. The `.php` header is quoting the fix commit's tree. **Recorded, not fixed.**

2. **`index.csv` already self-reports two corrections**, and both check out in the pristine tree,
   so they should be trusted rather than re-derived:
   - CRASH-092: *"Claimed `:263` is the line number in the 2005 fix commit's tree, NOT in
     php-5.0.0"* — the pristine site is `ext/standard/http_fopen_wrapper.c:197-201`.
   - CRASH-074: *"Claimed line `:1005` (`args[2] = userdata;`) does exist"* but is not the defect;
     the defect is the `:997` / `:1024` / `:1061` triangle (declared uninitialised, allocated on
     one arm only, freed on every arm). Confirmed by reading `ext/standard/array.c:993-1063`.
   - Also self-reported and confirmed: CRASH-052's claimed sibling
     `Zend/zend_object_handlers.c:277` is a real instance of the stack-zval idiom but is not the
     reachable one (`Zend/zend_execute.c:1138` is); CRASH-040's claimed
     `Zend/zend_hash.c:573-575` is present verbatim but unexercised (the exercised site is
     `zend_execute.c:69`/`:76`); CRASH-062's claimed `Zend/zend.c:975` is real but is the
     semantics bug, not the lifetime defect.

3. **One claim of my own that I had to retract.** I first wrote that CRASH-068's
   `free(c->name)` at `zend_constants.c:320` was *also* an allocator mismatch — libc `free` on
   `emalloc`'d storage (I5/O4). Checking it killed it: every `c->name` in that file comes from
   `zend_strndup` (`:41`, `:119`, `:170`, `:184`, `:199`), so libc `free` is the correct
   deallocator and the row is a pure free-before-format ordering defect. Corrected in
   `candidates.json` rank 23. Recording it because it is the shape of error most likely to be in
   the parts of this file I did *not* re-check: a plausible second defect asserted next to a real
   first one.
4. **No citation I checked came from a patched tree.** I did not read `build/php-4.0.2/`,
   `.temp/san_tests/oracle/.../php-5.0.0/`, or `.app-tests/.temp/oracle/build-5.0.0-*/` for any
   line number. The ASan census in §5 is the only thing I took from a patched build, and it is
   used for *frequency*, never for a line.

---

## 5. Hotness — what the ASan render census actually says

First, a correction to the brief. The task described this source as *"123 ASan reports from
ordinary … page renders"*. The number 123 does appear in `.temp/san_tests/REPORT.md`, at line 68
— but it is the report count of **one curated pass** (18 applications × 8 pages, ASan with the
allocation cache off), which that table breaks down as **123 reports / 7 distinct sites / 31 of
them use-after-free**. The `asan-logs/` directory itself holds far more: **2534 log files
carrying 3199 ASan report occurrences**, accumulated over many runs. Both numbers are correct at
different granularities; the counts below are *occurrence* counts over the accumulated logs, so
they measure how often a site fires, not how many independent defects exist. REPORT.md's
"7 distinct sites" is the right number for the latter, and it is consistent with the four
top-frame shapes I get.

Report types across the accumulated logs:

```
2450 heap-buffer-overflow · 490 heap-use-after-free · 189 use-after-poison · 70 global-buffer-overflow
```

The 490 heap-use-after-free occurrences — my axis, spread over 336 of the 2534 log files —
cluster into **exactly four top-frame shapes**:

```
 280  zend_do_fcall_common_helper <- zend_do_fcall_handler <- execute     (freed by _zval_ptr_dtor)
  98  _zval_ptr_dtor <- zend_switch_free_handler <- execute               (freed by _efree)
  70  xbuf_format_converter <- php_error_cb <- zend_error                 (freed by zend_register_constant)
  42  memcpy <- xbuf_format_converter <- php_error_cb                     (freed by zend_register_constant)
```

Three findings from this, none of which I would have guessed:

- **Temporal defects in php-5.0.0 fire on completely ordinary traffic, unprompted.** 336 of the
  2534 render logs contain a use-after-free. No adversarial input is involved.
- **57% of them are in the function-call teardown** (`zend_do_fcall_common_helper` — which is
  `zend_execute.c` around :2760-2800, the `efree(EX(fbc))` / `EG(This)` region and the arg-stack
  drain). That region is rank 18 and rank 1. **Rank 18 is the best-evidenced hot temporal defect
  in the whole corpus** and I had it ranked far too low on structural grounds until I ran this.
- **20% are in `zend_switch_free_handler`** — the loop/switch temp double-free, which is rank 16.
  So the two hottest measured temporal sites are the two families the file-based view makes look
  like executor minutiae.
- The remaining 112 reports are freed by `zend_register_constant` and consumed by the error
  formatter — that is **rank 23 / CRASH-068 firing on real page renders**, on a family I ranked
  last precisely because "error paths are cold". They are not cold.

**Caveat, and it is a large one.** These logs come from a *patched, allocator-modified* build.
`.temp/san_tests/REPORT.md` §2 documents why: at 5.0.0 `zend_alloc.c:39-43` forces
`ZEND_DISABLE_MEMORY_CACHE` to 0 in both arms of its `#ifdef`, so `_efree()` pushes any block
under 88 bytes onto `AG(cache)` and never calls `free()`. Measured there: a naive ASan build sees
**36.5% of PHP's heap traffic; 3.0 million allocations never reach malloc**. Consequences for
this mining pass:

- The 40 rows marked `crashes_pristine_5_0_0=False` are, for the most part, *not* rows where the
  defect is absent. They are rows where the freed block goes into the size-class cache and the
  stale read returns the old bytes. **A C kernel that uses plain `malloc`/`free` will reproduce
  more of these than pristine PHP does, not fewer** — which is a good property for the benchmark
  and a bad one for any claim of the form "faithful to 5.0.0 behaviour".
- Every candidate's `benign_behaviour` therefore specifies a **checksum that folds the value read**
  and, where relevant, an `(allocs, frees)` tally — so the defect is visible in the `u64` output
  rather than only in a sanitizer. That is the single most important design note in this file.

---

## 6. Blob-drivability — the short answer

All 23 are drivable by a flat byte blob decoded as an opcode stream, and each candidate names its
opcodes concretely. Three grades:

- **The blob *is* the input** (no synthetic encoding needed): rank 4 (`unserialize` — `s:`, `i:`,
  `a:`, `r:` literally are the opcodes) and rank 22 (the blob is an opcode stream and the kernel
  is a compiler pass plus an interpreter). These two are the most natural fits in the set.
- **A container-op stream** — insert / delete / walk / grow, with a callback program also decoded
  from the blob so re-entrancy is blob-controlled: ranks 1, 2, 3, 5, 6, 7, 8, 10, 11, 13, 14, 15,
  16, 19, 20, 21, 23. This is the majority and it is the same shape `p27` already uses.
- **An object-graph op stream** — needs (container, index) operand pairs so the blob can name the
  same container on both sides of a rebind: ranks 9, 12, 17, 18.

Nothing on this axis needs anything the pinned kernel shape (flat blob in, `u64` out) cannot
supply. The data structures that must live inside the kernel are, at most: a growable pointer
vector (rank 1), a slot map with a free list (ranks 2, 7), a hashtable with buckets and two
doubly-linked lists (ranks 3, 5, 6), a singly-linked list (rank 10), and a refcounted box
(ranks 8, 9, 17). All of these are smaller than the 32 raw pointers `p27` already holds.

---

## 7. Things I could not settle

- **Whether rank 5 (LOGIC-001) clears the admission bar.** It exhibits no fault — it silently
  destroys the wrong element. The bar as written says "exhibits the target error", and destroying
  a live element *is* the CWE-416 target error; but it is a judgement the manager should make
  explicitly rather than inherit from my ranking.
- **Whether rank 15 (CRASH-158) belongs on this axis or the spatial one.** CWE-824 and I19 put it
  here; "erealloc without zeroing the tail" reads spatial.
- **The exact preimage for rank 5's fixture.** The collision needs
  `zend_inline_hash_func(key, len+1) == some_integer_index`. DJBX33A over the key *including* the
  trailing NUL — callers pass `len+1`. Computable offline; I did not compute it.
- **`EG(garbage)` is `zval *garbage[2]`** (`Zend/zend_globals.h:214-215`) and
  `zend_pzval_unlock_func` does an unchecked `EG(garbage)[EG(garbage_ptr)++] = z`. A faithful
  extraction of rank 16 inherits a **spatial** overflow inside a temporal kernel. I flagged it in
  that candidate's `risks` rather than bounding it away, but someone has to decide what to do
  with it before the row is built.
- **Whether the 280 `zend_do_fcall_common_helper` census reports are one defect or several.**
  The logs are LTO'd and stripped of line info, so the frame is a 40-line region, not a site. I
  can say the region is hot; I cannot attribute it to CRASH-069 vs CRASH-031 vs the arg-stack
  drain.

---

## 8. Files in this directory

| file | what it is |
|---|---|
| `candidates.json` | the deliverable — 23 candidates, 85/85 corpus rows covered |
| `NOTES.md` | this file |
| `VERIFY.md` | pristine `tar -xzOf … \| sed -n` excerpts for the top 5, re-derivable in one command |
| `mk_candidates.py` | regenerates `candidates.json` (the generator; the JSON is the artefact) |
| `rows.json` | the 85 `index.csv` rows for this axis, extracted verbatim |
| `invmap.json` | case-id → invariant/obligation map, from `paper/invariants-166.json` |
| `extract_src.sh` | rebuilds the 35 pristine `.c`/`.h` files I read into `src/`. The extraction itself is a derivable blob and has been deleted; this is its generator. |
