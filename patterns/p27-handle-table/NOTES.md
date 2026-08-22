# p27 — handle table over per-record allocations: measurements and arguments

**The one TEMPORAL bug class in this project.** Every other pattern's bug is
spatial (an index outside an allocation) or logical (a wrong answer inside a live
one). p27's read is through a pointer whose record has been `free`d, so the
address is inside **no live allocation at all** — and it is the one class safe
Rust rejects at *compile* time.

Read `spec.md` first; it carries the contract and the pins. This file carries the
measurements, the arguments the gate cannot judge, and the things that turned out
not to be true.

**Contract hash.** The `slb-contract` block's sha256, as first written before any
cell of the shipped matrix was measured, was
`b1f2dbb3e48542af48d444c69f4bbc80402363fcec05a8b4ded37b50da1f8dea`.
**It moved once, to `a0e83e2f2ee2e3bb756b2985a3ca9c718f6c5a13dbf7a91e7b0ebc446e23beb5`,
and the reason is recorded here rather than left to be noticed**: the gate's
clause-mutation stage (5c) found two of `rec_alloc`'s `ensures` clauses **not
load-bearing** — `pt.0.addr() + size <= usize::MAX + 1` and
`pt.0.addr() as int % align as int == 0`, both copied verbatim from
`vstd::raw_ptr::allocate` — and the same run found that `rec_free`'s
`Tracked(pt)` destructuring parameter pattern made the tautology probe
*unsynthesisable*, so six of its `requires` conjuncts were not judged at all. The
clauses were dropped and the parameters made plain identifiers; `verus.items` is
a mechanical dump of `verus.rs` through `harness/vparse`
(`controls/mkspec.py`, which regenerates `spec.md` byte-identically), so the
pin followed. **No `required` or `forbidden`
entry moved**, and the direction of both edits is *toward* a stricter gate.

**And that claim is no longer asserted — it is byte-provable, which is the first
time on this project the recorded hash has actually been used to check a
disclosure end to end.** TASK_060_REVIEW clean negative 25 reconstructed the
pre-build contract block from the *two disclosed edits alone* — restore
`rec_alloc`/`slb_twin_rec_alloc`'s two `ensures` in vstd's positions, restore
`rec_free`/`slb_twin_rec_free`'s six `requires` to the destructured `dealloc.` /
`pt.` spelling — re-serialised, and got **`b1f2dbb3e48542af…` exactly**;
**neither edit alone does** (`6d176cdf…`, `26a8ef39…`). So "no `required`,
`forbidden`, `obligations`, `twin_obligations`, `identity`, `miri`, `note` or
`why` entry moved" is a *checked* statement about the whole block, not a promise
about the parts its author remembered. That is what PROTOCOL definition-of-done 6
was added for, and 12 below records it as a method result.

**⚠ IT MOVED A SECOND TIME, at TASK_061, to
`0c9f0e9784642dd9b6a68c9dee88fb03c15e07dcd7fb97df9bfb3058451524c5`, and the
reason is THREE FACTUAL CORRECTIONS to English prose inside the block** — one
sentence, in three places, each saying that `rec_alloc` / `rec_free` are vstd's
items *"character for character"* or *"verbatim"*. They are not, and this file
already said so one paragraph above, which is the point: **the block contradicted
itself, and the machine-readable `verus.items` pin was right all along.**

| key | said | ships |
|---|---|---|
| `verus.unsafe_justifications.rec_alloc` | "constrained by **five** `ensures` clauses copied from vstd verbatim" | **three**; the other two are the ones dropped above |
| `verus.unsafe_justifications.rec_free` | vstd's preconditions "copied **verbatim**" | all six, **respelled** — vstd destructures its tracked parameters and writes `dealloc.addr()`, this item takes plain ones and writes `dealloc@.addr()` |
| `idiom.required[2].rust` | "**character-for-character** `vstd::raw_ptr::deallocate`" | same respelling, and the body writes `std::alloc::` where vstd writes `::alloc::alloc::` |

(The `rec_alloc` correction also names the two dropped clauses, so its `verus.items` cross-reference is checkable without leaving the block.)

⚠ **The third is inside a `required` entry, which is the sensitive case, so state
exactly what did and did not change: no BACKTICKED SPELLING moved.** The entry's
tokens — `std::alloc::dealloc(p, layout);`, `vstd::raw_ptr::deallocate`,
`deallocate`, `Option<Box<u8>>` — are the same tokens in the same order, so no
rung becomes admissible or inadmissible that was not before. Only the English
*around* the tokens changed.

**And that is CHECKED, not asserted — it failed once first.** The gate's
stage-`0b` audit counts every backticked span, so it is a decidable test of
"only the English moved", and the first draft of this correction FAILED it:
writing *"deallocate's six `requires`"* introduced a backticked `requires`, and
the audit went `62 → 63` spellings, `194 → 198` pairs, `pins_nothing 3 → 4`. The
shipped wording says "six preconditions" instead, and the audit reads **62
spellings, 194 pairs, 88 present, 3 pins-nothing, 36 scoped-absent, 2 forbidden
hits — identical on both sides of the edit.** A prose edit inside a `required`
entry is one careless backtick away from being a ruler edit, and the audit is
what tells the two apart.

**Checked the same way, and it is the same check:** a semantic JSON diff of the
two blocks reports **exactly three changed keys**, and undoing *only* those three
prose edits reproduces `a0e83e2f2ee2e3bb…` byte for byte. **No `forbidden`
entry, no backticked `required` spelling, and no `obligations`,
`twin_obligations`, `identity`, `miri`, `items`, `note` or `why` entry moved.**
**Direction test** (`.memory/01-ladder.md`): none of the three moves any
published figure — they replace a false count with the true one and a false
"verbatim" with the respelling this file was already disclosing — so there is no
direction in which they could flatter the thesis. The declaration got *more*
accurate about how much vstd this pattern actually re-states, which is the
direction that costs the author something.

**⚠ IT MOVED A THIRD TIME, at TASK_062, to
`371a680bb5b85f2bdbfb418ab6796b1665037aa199419fce32a5eafb9d5596ac`, and this one
is a RESTORATION rather than an edit: p27 shipped without the shared
named-spelling paragraph.** Every other pattern's `idiom.why` ends with the same
11 003 bytes, byte-identical — `NAMED-SPELLING STANDARD -- POLICY ADOPTED AT
TASK_018 …` through `… and p01 and p08 neither` — and that paragraph is what
**defines what a backticked pin means**: that a backticked `required` /
`forbidden` entry pins *that spelling* and not merely the property the expression
has, plus the three-part matching rule (whitespace deleted, comments and string
literals blanked, Verus ghost clauses blanked) that `check.py::spelling_matches`
implements. p27's `why` was **2 607 bytes of its own text** and carried none of
it, while p27 pins **62 backticked spellings**. So for three tasks and two
adversarial reviews **p27's pins were undefined by p27's own contract**, and every
argument the other seventeen patterns rest on that paragraph for did not apply
here in writing. It was found by the manager's standing one-liner, after p27 was
fully landed — not by a review, and not by the gate.

The invariant, and how to check it in one second:

```bash
python3 -c "import hashlib,glob;print({hashlib.sha256(open(f).read()[open(f).read().find('NAMED-SPELLING STANDARD'):open(f).read().find('p01 and p08 neither')+19].encode()).hexdigest()[:12] for f in glob.glob('patterns/*/spec.md')})"
# before TASK_062: {'59748cce2db5', 'e3b0c44298fc'}   <- e3b0c44298fc is sha256("")
# after:           {'59748cce2db5'}                   <- set size 1
```

⚠ **The paragraph says "this paragraph is byte-identical in all six patterns'
`why`", and that "six" is HISTORICAL — there are eighteen — and it is
deliberately NOT corrected.** The phrase sits *inside* the hashed
`slb-contract` block, so changing one adjective would move **eighteen**
`contract_sha256` values and cost eighteen gate re-runs (~50 minutes measured)
to buy nothing a reader of this note does not already have. It is copied
verbatim, "six" included, precisely so that the one-liner above stays a
one-liner: the invariant is *byte*-identity, and an invariant that tolerates a
per-pattern correction is not checkable by a hash. The count is **18** as of
TASK_062; the paragraph's own internal figures (82 obligations, 0 failing, "all
six patterns", "six p17 rungs") were all measured at TASK_019 over the six
patterns that existed then and are frozen as of that date.

**Byte-provable, the same way TASK_061's disclosure was.** Undoing *only* this
edit — deleting the appended `" " + paragraph + "."` from `idiom.why` and
nothing else — reproduces the previous block exactly:

```
contract_sha256 before  0c9f0e9784642dd9b6a68c9dee88fb03c15e07dcd7fb97df9bfb3058451524c5
contract_sha256 after   371a680bb5b85f2bdbfb418ab6796b1665037aa199419fce32a5eafb9d5596ac
undo -> contract_sha256 0c9f0e9784642dd9b6a68c9dee88fb03c15e07dcd7fb97df9bfb3058451524c5   (equal)
spec.md sha256 before   72383d55c0667f1002dd63aca0a73ff5448d6e11d7646232cd03b3fb0e8cf3f4
spec.md sha256 after    8225423c0ce70f8d8c25642bfc313022e3727cd7722922eea24bba2679fcbf89
undo -> spec.md sha256  72383d55c0667f1002dd63aca0a73ff5448d6e11d7646232cd03b3fb0e8cf3f4   (equal)
```

`git diff --stat` is **1 insertion, 1 deletion** — the `why` line and nothing
else. The insert/undo script is `.temp/t62/para.py`, and it never embeds the
paragraph: it reads it out of a donor `spec.md` at run time, so it cannot become
a nineteenth divergent copy.

**Direction test** (`.memory/01-ladder.md`): it passes trivially, and saying so
is not the same as assuming it. The edit moves **no published figure** — no
`Ir`, no `ns`, no static count, no `tcb_items`, no obligation count — and it
touches no `required`, `forbidden`, `obligations`, `twin_obligations`,
`identity`, `miri`, `items` or `note` entry. It only **adds** constraints: 62
pins that meant whatever a reader assumed now mean what the standard says, which
can only narrow the admissible class, never widen it. There is no direction in
which restoring a shared rule can flatter this pattern's numbers, and if it
changed the admissible class at all the change is *against* the author.

**Stage `0b`'s audit does not move, and the mechanism is worth naming** — this
is the check TASK_061's first draft failed, so it was the obvious thing for this
edit to break. It reads **62 spellings, 194 pairs, 88 present, 2 forbidden hits,
3 pins-nothing, 36 scoped-absent** on both sides of the edit, and every list
entry (`hits`, `pins_nothing`, `absent`) compares equal element for element.
That is *not* luck: the added paragraph contains **176 backticks, i.e. 88
backticked spans**, any one of which would have moved `spellings` if it were
seen. `idiom_audit` iterates `("required", "forbidden")` only
(`harness/check.py:922`) and never reads `why`, so prose inside `why` is
invisible to it by construction. The contrast with TASK_061 is exactly the key
the backtick landed in: `62 → 63` there because the backtick went into
`required[2].rust`; `62 → 62` here because 88 of them went into `why`.

**And the gate now enforces it** (TASK_062 deliverable 2,
`harness/check.py::named_spelling_problem`): stage `0b` fails a pattern whose
`idiom.why` does not carry the paragraph verbatim, against a sha256 pinned in
`check.py` and therefore inside every gate record's
`source_sha256["harness/check.py"]`. The check is **stricter than the one-liner
it mechanises**: the one-liner greps `spec.md` as a *file*, so a copy pasted
into the prose above the fenced block satisfies it — which is p05's original
accident exactly, a declaration at line 69 while the hashed block started at
line 309. The gate check reads `contract["idiom"]["why"]`, the parsed value
*inside* the hash, so a paragraph outside it does not count.

**⚠ IT MOVED A FOURTH TIME, at TASK_063, to
`01e2137f9a1bcce2453ecdb43ea9260dbc6d91e7e5073104d0e13b7800ddef07`, and this one
is the first edit to a `forbidden` ENTRY on this pattern.** `` `memset(tab` `` —
`forbidden[0]`, the entry **both of p27's own C rungs spelled** — is **deleted**,
and it is a deletion rather than a narrowing for reasons that are measured and
not argued. **13** below carries the decision and its controls; **13c** carries
the disclosure with its byte-provable undo. `git diff --stat` on `spec.md` is
**1 deletion, 0 insertions**, and the audit moves `62 → 60` spellings /
`194 → 188` pairs / `88 → 86` present / **`2 → 0` forbidden hits**, with
`required` untouched at `3` pins-nothing and `36` scoped-absent — which is the
decidable evidence that only the `forbidden` array moved. `controls/mkspec.py`
moves with it, and separately gains the repair for a staleness this task found
in it (13c).

**⚠ IT MOVED A FIFTH TIME, at TASK_065, to
`397de62b01eaa1e20bd4d16786c406de225313c223ba83b800c49afbcb84d79a`, and this one
corrects ARITHMETIC and moves no measured figure.** `obligations_note` said
`main 4`; `main` measures **5**:

```
$ ./verus_run.py patterns/p27-handle-table/verus.rs --verify-function main --verify-root
verification results:: 5 verified, 0 errors (partial verification with `--verify-*`)
```

`1+1+1+1+1+1+1+3+4 = 14` against this block's own pinned and separately measured
total of **15**; with `main 5` it is exactly 15, so the note was inconsistent
with its own pin from the first draft. Nothing in the gate checks the
decomposition — only the total — which is why it passed four reviews. The note's
closing sentence, *"the same off-by-one p03, p05, p06, p07, p11, p12, p14 and p17
record for the identical driver"*, is **deleted: none of those eight records 4**
— every pattern in this tree that records the term records `main 5`, and p27 was
the only 4 (`grep -o 'main [0-9]' patterns/*/spec.md`). Found by
TASK_064_REVIEW major 2, on p47, and fixed here because the error is p27's.

⚠ **And that sentence was wrong twice over.** The note those patterns carry is a
**prediction-minus-one** claim about `.memory/04-verus.md`'s
one-query-per-function-plus-one-per-loop rule of thumb — p10's reads *"body +
driver loop + one per by-block would predict 6 and Verus reports 5"* — not a
claim about the value 4 at all. p27's copy transposed it into *"would predict 5
and Verus reports 4"*, which is where the stray 4 entered the tree. With
`main 5`, p27's own stated prediction and its measurement agree, so **p27
records no off-by-one**.

**The direction test passes trivially and the undo is byte-provable.**
`git diff --stat patterns/p27-handle-table/spec.md` is **2 insertions, 2
deletions** — the `obligations_note` pin and the prose pin-table row that
restates it, nothing else — and

```
git checkout HEAD -- patterns/p27-handle-table/spec.md \
                     patterns/p27-handle-table/controls/mkspec.py
```

restores `01e2137f9a1bcce2453ecdb43ea9260dbc6d91e7e5073104d0e13b7800ddef07`. No
`required` or `forbidden` entry, no obligation total, no twin total, no rung, no
input and no published p27 figure moves; `verus.obligations` stays 15 and
`twin_obligations` stays 20. `controls/mkspec.py` carries the same correction, so
regenerating reproduces the corrected block rather than reverting it — the
generator and the artefact were checked to agree before and after (`mkspec.py`
re-run produced a byte-identical `spec.md` on the pre-edit tree).

---

## 0. The bug class, settled before anything was built

`.memory/06-catalogue.md` rates p27 *"singly linked list (build, traverse, free)
— use-after-free, leak"*. **The class is upheld; the shape is not.** Two
candidates were priced (`.temp/p27/NOTES.md` §0):

**Candidate A, the textbook list free** — `for (p = head; p; p = p->next)
free(p);`. Rejected, and the reason is not taste:

- Where the `next` field sits decides whether the bug is observable at all, and
  the answer is a **glibc implementation detail**. At offset 0 the freed chunk's
  first 16 bytes are the tcache `next`/`key`, safe-linked and therefore
  ASLR-dependent, and the traversal walks a scrambled pointer — a segfault, not
  a measurement. At offset ≥ 16 glibc does not touch the field and the traversal
  is *correct on every input on every build*, so R1 and R1h print the same
  checksum and the bug is invisible to the entire checksum column.
- The bug fires on **every** input, so it cannot be confined to adversarial
  rows — and TASK_055_REVIEW blocker B1 requires exactly that (see 7 below).
- Safe Rust cannot write it at all, so R2/R3 would not be a *spelling* of R1's
  program but a different program, and the reviewer checklist's "did a rung
  quietly change the algorithm" would have no good answer.

**Candidate B, the handle table** — chosen. An op stream from the file drives
OPEN/CLOSE/READ against a table of individually `malloc`'d records; the bug is
one conjunct on the READ path; it fires only on inputs that read a closed handle.

### 0b. What R1 KEEPS, and why the comparison is one program against its guard

Three things are in R1 that a lazier construction would have taken out, and each
is what makes R1-vs-R1h a guard rather than a rewrite:

1. **R1 keeps the slot bound `h < ntab`.** So `tab[h]` is always an entry some
   OPEN wrote, the table read itself is in bounds, and the bug is temporal and
   not spatial.
2. **R1 keeps `live[]` and maintains it** — CLOSE writes `live[h] = 0` in both C
   rungs, character for character. Only the READ path differs. This is not
   generosity: if R1 did not maintain it, CLOSE would not be idempotent and the
   epilogue could not tell a closed slot from a live one, so **R1 would
   double-free** on any input with two CLOSEs of the same handle, and that is a
   different bug in a different class. The measured difference would then be
   between two different programs rather than between one program and its guard.
   *This is also why the liveness bit cannot be "the pointer is NULL":* the
   handle is an integer, so nulling `tab[h]` would turn the stale read into a
   NULL dereference — a crash, not a use-after-free — and would leave the
   epilogue with nothing to consult.
3. **R1 keeps the epilogue**, so neither C rung leaks and **the allocator's state
   at the end of a call is its state at the start.** That is what makes a kernel
   that allocates legal in this benchmark at all — the driver calls it 200 000
   times and every call must return the same value — and it is *measured*, not
   assumed: all eight cells agree with `model.py` on `small` (200 000 calls, 8
   windows, 24 ops each) and on `large` (20 000 calls, 64 windows, 120 ops), and
   a kernel whose answer drifted with allocator state would not.

### 0a. What TASK_055 §2.8 predicted, and what actually happens

§2.8 predicted that safe Rust would be forced onto `(slot, generation)` and would
pay *"a wider handle plus an indirection plus a generation compare"*, i.e. that
the pattern's axis would be a **representation split** between the rungs.

**That is not what happens, and the reason is structural: the handle comes out of
a file, so it is an integer in every rung.** An op stream cannot name a pointer.
So there is no pointer-handle rung, no `(slot, gen)` rung, and no representation
split — and, as a direct consequence, **none of TASK_055_REVIEW M1's arity
problem arises** (see 1 below).

What safe Rust *is* forced into is `Option<Box<u8>>`, and the finding that
replaces §2.8's is better:

- **`Option<Box<u8>>` is niche-optimised to one pointer word**, `None` *is* the
  null pointer. The safe rung's table is byte-for-byte the hardened C rung's
  `tab[]` **minus** C's separate `live[]` array. The safe representation *is* the
  hardened representation, arrived at by construction rather than by discipline.
- **`tab[h] = None` frees the record and invalidates the handle in ONE
  operation.** C does those two things in two statements — `free(tab[h]);
  live[h] = 0;` — and R1's bug is that the *third* thing, asking, is missing.
- **At R4 the invalidation is a hand-written line, and at R5 the proof forces
  it.** Delete `arr_set_unchecked(&mut live, h, 0u8)` from the **CLOSE path** of
  `verus.rs` and the loop invariant cannot be re-established, because `rec_free`
  has consumed slot `h`'s permission while the liveness array still claims the
  record exists. That is mutant **M2** in 10 below, and it is the pattern's
  sentence made checkable.
  ⚠ **Do not confuse it with the store 8a deleted.** The epilogue used to carry a
  line that *looks* the same, `arr_set_unchecked(&mut live, j, 0u8)` — and that
  one was **dead**, because nothing reads `live[j]` after the epilogue passes
  `j`. The CLOSE-path store with `h` is load-bearing and is pinned; the
  epilogue's store with `j` was not, and deleting it is what let the epilogue's
  invariant weaken to the suffix `[j, ntab)`. **One line the proof forces, one
  line the proof never needed** — and telling them apart is the whole difference
  between a safety obligation and symmetry for its own sake.

**The sentence p27 exists for: the free and the invalidation are one operation in
safe Rust and two in C, and the bug is the third one — the asking — going
missing.**

---

## 1. §0.1 — the dead `slab` argument, measured, and why p27 does not need it

TASK_055_REVIEW M1 measured that `driver.aliases` / `driver.call_args` are keyed
by *language*, so all four Rust rungs share one table, and that
`harness/dloop.py:361` raises when the declared positions exceed a call's arity.
Its one escape — a **dead `slab` argument** at R4/R5 — was left unmeasured at
`-O3`, and TASK_060 made measuring it the gating deliverable.

**Probe:** `.temp/p27/deadarg/` — two programs identical but for an extra
`_slab: &[u8]` parameter the kernel never reads and the corresponding extra
argument at the call site. `build.py`'s own flags, both opt levels, both inline
modes.

| | `kernel` `md5_raw` | `main` `md5_raw` |
|---|---|---|
| `-O0 isolated` | **differs** (the three arg spills move `rdi,rsi,rdx` → `rdx,rcx,r8`) | **differs** |
| `-O0 whole` | **differs** | **differs** |
| `-O3 isolated` | **identical** | **identical** |
| `-O3 whole` | (inlined away) | **identical** |

```
cell                        kernel/call    main/call     k+m/call
bin-2arg-O0-isolated          1227.0000      25.0000    1252.0000
bin-3arg-O0-isolated          1227.0000      28.0000    1255.0000
bin-2arg-O0-whole             1227.0000      25.0000    1252.0000
bin-3arg-O0-whole             1227.0000      28.0000    1255.0000
bin-2arg-O3-isolated           372.0000      13.0000     385.0000
bin-3arg-O3-isolated           372.0000      13.0000     385.0000
bin-2arg-O3-whole                     -     399.0000     399.0000
bin-3arg-O3-whole                     -     399.0000     399.0000
```

**The dead argument is free at `-O3` — exactly, to the last digit, in both
inline modes — and costs `+3.0000` Ir/call at `-O0`, all of it at the call site
and none of it in the kernel.** LLVM's dead-argument elimination deletes it
outright at `-O3`; at `-O0` nothing is eliminated and the call site pays two
extra loads and a register move. The kernel's own `1227.0000` is unchanged even
at `-O0`, because an *unused* parameter is never spilled — the three spills are
the three live arguments in both builds and only the register assignment moves,
which is why `md5_raw` differs while `Ir` does not.

**So the escape survives `-O3`. And p27 does not use it**, because the shape that
needed it is not p27's shape: the driver loop is pinned identical across all
seven rungs, so there is nowhere rung-specific to build a slab, and the slab
therefore lives inside the kernel exactly as p14's scratch and field table do.
Every Rust rung is `kernel(buf, off, len)`; both C rungs are
`kernel(buf, buf_len, off, len)`; the gap is closed by **p14's existing
`driver.call_args` pin, unchanged**. No new harness surface and no `harness/`
change.

---

## 2. The equivalence argument, in writing

`.memory/02-bench-rules.md` and the reviewer checklist ask whether the rungs are
semantically equivalent or whether one quietly changed the algorithm. Because p27
is *not* a representation split (0a), the question is the ordinary one, and it
has two answers:

**Mechanically**, `harness/check.py` stage 2 derives it: every cell's stdout
equals `model.py`'s on every non-adversarial input, and all cells agree with each
other. That is the evidence `.memory/02-bench-rules.md` names.

**And it is measured, not only argued**: callgrind's per-function table gives
`malloc` `421.1211` Ir/call, `free` `310.2635`, `_int_malloc` `587.8332`,
`_int_free` `72.9715`, the unix shim `80.0680` and all three `__rust_*` symbols
`10.0085` — **identically, to the last digit, for `safe_tuned` and for `unsafe`
on `small.bin`, and the same on `large.bin`** — inside a decomposition whose sum
over every function equals the whole-program delta, so nothing outside those
symbols is hiding allocator work either (5e). *The two representations make the
same allocator calls, in the same number, of the same size.*

⚠ **This paragraph used to cite a second piece of evidence and that citation is
RETRACTED**: *"the sweep's `R3 − R4` regression puts `nopen`'s coefficient at
`−0.0157`, zero to within a residual of 2.92 over 80 blobs"*. The coefficient is
now `+0.9781` with the allocator table above unchanged (9c item 1), so it was
never measuring the allocation — it absorbs everything that scales with OPEN.
The per-function table is the direct evidence and it is enough on its own.

**Structurally**, per record, every rung does:

- **one allocation of `RECSZ` bytes from the same allocator.** Rust's default
  global allocator calls `malloc` for `align <= 8`, so `Box::new(a)` (R2/R3),
  `std::alloc::alloc` (R4/R5) and `malloc(1)` (R1/R1h) are the same glibc call in
  the same size class;
- **one `free` of it**, and every record is freed before the kernel returns;
- **per READ: one slot-bound test, one liveness test, one load of the record.**

**What the argument does NOT establish** is that the two representations have the
same *cache* behaviour. They have the same layout — one pointer word per slot,
plus C's and R4/R5's extra `TABCAP` liveness bytes — but not necessarily the same
addresses. Any `ns` claim therefore needs the layout population
(`.memory/05-layout.md`) and is not carried by this argument.

**And there is one asymmetry that is deliberate and is a result rather than an
oversight: R2 and R3 have no epilogue.** Dropping the table frees every record
still alive, so the loop the other five rungs write by hand is written by the
language. See 3.

---

## 3. `Ir` per call, and where the safety cost is

`-O3 isolated`, from `results/p27-handle-table.json` (kernel-exclusive) and from
`controls/ir_table.py --marginal` (whole-program marginal). `small.bin` is 8 windows of
24 operations at `n_iters` 200000; `large.bin` is 64 windows of 120 operations at
20000.

| rung | cell | kernel Ir/call small | large | **whole-program** Ir/call small | large |
|---|---|---:|---:|---:|---:|
| R1 | `c-gcc` | 844.5685 | 3440.0865 | 2291.6035 | 8414.6716 |
| R1 | `c-clang` | 869.5913 | 3641.8189 | 2275.7692 | 8487.3326 |
| R1h | `c-gcc-h` | 864.4959 | 3530.8879 | 2311.4302 | 8505.6792 |
| R1h | `c-clang-h` | 874.5739 | 3645.2917 | 2280.7224 | 8491.0960 |
| R2 | `safe_naive` | 1041.1426 | 4562.3795 | 2697.4293 | 9955.1610 |
| R3 | `safe_tuned` | 1031.6288 | 4530.3795 | 2687.9135 | 9923.1610 |
| R4 | `unsafe` | 921.6538 | 3868.5595 | 2457.8441 | 9130.4152 |
| R5 | `verus` | **921.6538** | **3868.5595** | **2457.8441** | 9130.4284 |

⚠ **The R4 and R5 rows moved at TASK_061** and no other row did: the epilogue's
dead liveness store was deleted, which is **−6.81 / −10.49 Ir/call**. The
before/after, the mechanism and the direction test are in **8a**; the old figures
were `928.4304 / 3879.0121` kernel-exclusive and `2464.6514 / 9140.9146`
whole-program, and `controls/`'s `r4_epiclear` reproduces them exactly.

### 3a. ⚠ TWO DENOMINATORS, and on p27 they are not interchangeable

**58–63% of this kernel's work is inside `malloc` and `free`, which are in glibc
and therefore inside no symbol `harness/measure.py`'s `_sum_rows` matches.**
`1 − 921.6538/2457.8441 = 62.50%` on `small` and `57.63%` on `large`. Every
kernel-exclusive figure above is therefore *the part of an operation that is not
the allocation*, and every whole-program figure is the operation.

Both are honest and neither is "the" number; **what is not honest is comparing
across the two**, and one control in this pattern does exactly that if you let
it (5d). Where a single figure is wanted below, it is the **whole-program**
marginal, because the allocator is what p27 is about.

### 3b. What the table says

- **`R5 − R4 = 0.0000` kernel-exclusive on both inputs, and `0.0000`
  whole-program on `small`.** Finding 1 reconfirmed on the first kernel in this
  project that allocates and frees — and it took the two source lines in 5 to
  get there.

  ⚠ **RETRACTED: the `large` whole-program `R5 − R4 = +0.0132` this section used
  to publish is a SCRATCH-PATH ARTEFACT, not a property of the code, and its
  gloss was wrong arithmetic too** (`0.0132 × 5000 = 66`, not the "132
  instructions" claimed). TASK_060_REVIEW minor 2 found it, and TASK_061
  re-measured the same two binaries on the same input from three different
  scratch directories:

  ```
  scratch dir                       unsafe        verus     R5 - R4
  .temp/p27/irt<pid>   (ir_table)   9140.9146   9140.9278   +0.0132   <- the published figure
  .temp/p27c/av<pid>   (argvlen)    9140.9154   9140.9258   +0.0104
  TASK_060_REVIEW's path                    -           -   +0.0020
  ```

  The binaries and the input bytes are identical across all three rows; only the
  path the input file sits at changes. **p27 is the only kernel here that calls
  `malloc`**, so the initial `brk` — which depends on the size of `argv`/`envp`
  — decides at which iteration glibc extends the heap, and that lands inside or
  outside the marginal window. The honest statement is **`R5 − R4` is `0.0000`
  kernel-exclusive on both inputs and `±0.02` whole-program on `large`, and the
  `±0.02` is the measurement's own floor**. It must not be quoted as a number.
  (The figure is stable *within* one scratch path: the same run reproduces
  `+0.0132` after the TASK_061 source change too.)
- **`R1h − R1 = +19.83` (gcc) / `+4.95` (clang) on `small`, `+91.01` / `+3.76`
  on `large`** (whole-program). **The two compilers disagree by 4× on `small`
  and by 24× on `large`** for one added conjunct — which is finding 5's shape
  ("static instruction counts are not a cost model") arriving on the *hardening*
  column. Kernel-exclusive the same pair reads `+19.93` / `+4.98` and `+90.80` /
  `+3.47`, so the disagreement is in the kernel and not in the allocator.
- **`R2 − R3 = +9.52` on `small` and `+32.00` on `large`**, whole-program, and
  the same to four decimals kernel-exclusive — the two R3 levers of 8.
  ⚠ **DISPUTED, and left standing only as a question.** This bullet used to end
  *"and they are **exactly** `nread + nclose` per call on each blob"*. Measured
  against the sweep's own regressors that is **false**: `9.5158` against
  `nread + nclose = 10.875` on `small`, and `32.0000` against `50.6094` on
  `large`. Either the English meant *"on the `nread` and `nclose` paths"* — a
  much weaker claim — or the identity is wrong. **It cannot be settled from what
  is committed**, because `safe_naive` is not in the sweep, so **no `R2 − R3` fit
  exists**. Flagged by TASK_061's engineer as adjacent to their task; it was in
  neither the review nor the task file, and it is the only unresolved claim in
  this pattern. **Whoever sweeps R2 settles it.** (Manager's edit, TASK_061
  boundary: the false half is removed rather than left to be quoted.)

⚠ **What must NOT be read off this table is "the cost of safe Rust's lifetime
guarantee".** `R3 − R4` is `+230.07` / `+792.75` whole-program, and **it is not
a safety number**. Two independent decompositions say so and 5e and 5f carry
them:

- **per function, and the decomposition is CLOSED** (5e): `+230.0694 =
  +109.6476` inside the kernel `+ 120.4218` of out-of-line drop glue `+ 0.0000`
  of allocator, and **the sum over *every* function in the program equals the
  whole-program delta**, so nothing else moved. **52% of it on `small` is the
  epilogue asymmetry** — the safe rungs' drop glue over all `TABCAP` slots
  against the unsafe rungs' inline loop over `ntab` — and 17% of it on `large`.
- **the in-kernel remainder is the SPATIAL bounds-check tax and nothing else**
  (5f): an R4 that keeps R3's bounds checks costs `+153.51` in the kernel where
  R3's whole in-kernel excess is `+109.65`, so **R3 pays 43.86 Ir/call LESS of
  that tax than an unsafe rung carrying the same checks. Not one instruction of
  `R3 − R4` is the lifetime guarantee.**

### 3c. Wall clock — recorded, not published

`results/p27-handle-table.json` carries `min_s` for all 16 `-O3` cells on both
inputs (`c-gcc` 0.03544 / 0.02699, `unsafe` 0.03741 / 0.03025, `safe_tuned`
0.03939 / 0.02974, …). **No `ns` claim is made from them and none may be**, for
two reasons that are each sufficient: they are whole-process **levels** and
carry the per-process constant (`.memory/03-measurement.md` finding 20a), and
**there is no layout population for this pattern yet** — `controls/clayout.py`
is ported and ready, and until it has been run the shipped binaries are one draw
of unknown width. p27 additionally has a reason no earlier pattern had: its wall
clock is a function of the *allocator's* state, and the allocator's state is not
a property of the code.

### 3d. Panic pads, checked before anything is called a safety cost

`.memory/03-measurement.md` trap: tail padding and landing pads inflate a static
count. `harness/asm.py stat`, `-O3 isolated`, kernel symbol:

| cell | `n_fn` | `n_fn_nopad` | `pad_insns` | `pad_bytes` |
|---|---:|---:|---:|---:|
| `c-gcc` | 154 | 146 | 0 | 0 |
| `c-gcc-h` | 155 | 149 | 0 | 0 |
| `c-clang` | 147 | 141 | 1 | 9 |
| `c-clang-h` | 146 | 142 | 1 | 9 |
| `safe_naive` | 210 | 206 | 15 | 15 |
| `safe_tuned` | 213 | 209 | 15 | 15 |
| `unsafe` | 154 | 150 | 7 | 7 |
| `verus` | 154 | 150 | 7 | 7 |

(R4/R5 were `156 / 151 / 2 / 2` before 8a's deletion: **one instruction out of
the padding-excluded count**, five bytes out of the symbol, and five bytes more
of tail padding in their place. `md5_fn` moved from `87ced153` to `38ae720c`,
**equal between the two rungs on both sides of the edit**.)

⚠ **`c-clang-h` has one FEWER static instruction than `c-clang` on the RAW count
— 146 vs 147 — while executing more.** That is finding 5's inversion on the
hardening column inside one compiler, and it is real. ⚠ **But it REVERSES on the
padding-excluded count, 142 vs 141, which is the one this project says to
quote** (`harness/asm.py`'s own docstring, `.memory/03-measurement.md`).
TASK_060_REVIEW minor 3. Both numbers are in the table and always were; what was
wrong was drawing the arrow from the convention the project tells you not to use,
over a one-instruction difference. **The honest reading is that the two counts
disagree about the sign of a 0.7% static difference while `Ir` says `c-clang-h`
executes `+4.95 / +3.76` more** — i.e. the static count is not a cost model here
in either convention, which is the finding, and it is *stronger* than the
one-sided version. The safe rungs' 15 pad instructions are
`int3` tail padding, not landing pads; the landing pads themselves are the
`_Unwind_Resume` block and the two `drop_glue` call sites, and they are counted
in `n_fn_nopad`. **`bulk_calls` is empty on all eight kernels**, so no rung is
winning or losing on a `memcpy`/`memset` idiom: gcc and clang inline the two
`memset`s of the table and the liveness array at `-O3`, and the Rust rungs'
`[const { None }; 32]` / `[0u8; 32]` are stores.

### 3e. Reproducibility control, taken for free

`harness/measure.py p27` was run **twice**, the second time after `inputs/gen.py`
had been edited (9b's band-S bug) in a way that leaves every matrix blob
byte-identical. **Every `kernel_exclusive_ir`, every `main_exclusive_ir` and
every `md5_fn` in the record is identical between the two runs**, on all 32
cells and both inputs, while `source_sha256` for `gen.py` moved from
`070c92ad0cace1d3…` to `19c9fe676bc074ef…`. So the `Ir` column is exactly
reproducible on this box, and `--check-stale`'s two-hash design
(`measure.py:238`) did the thing it is for: it said "the generator moved, the
blobs did not".

## 4. The table bounds check — a claim this pattern made and then refuted

The first draft of `unsafe.rs` and `verus.rs` indexed the handle table
**checked**, with a comment asserting that `h < ntab` together with
`ntab <= TABCAP` already deletes rustc's bounds check, so a `get_unchecked`
accessor would buy nothing and cost two trusted items.

**That was written without measuring it and it is false.** Three
`core::panicking::panic_bounds_check` call sites survive in the checked kernel
at `-O3` — 8 `call`s in the kernel symbol against 5 in the unchecked one, and
**resolved by SYMBOL and not by counting**: each is an indirect
`call *disp(%rip)` through a GOT slot whose `R_X86_64_RELATIVE` addend `nm` maps
to `core::panicking::panic_bounds_check` (`controls/gotresolve.py`, the probe
TASK_060_REVIEW clean negative 13 used and 5f re-uses):

```
unsafe::kernel         1x __rust_no_alloc_shim  1x __rust_alloc  1x __rust_dealloc
                       1x std::process::abort        -- ZERO panic sites
r4_tabchecked::kernel  3x core::panicking::panic_bounds_check   + the same four
```

The control `r4_tabchecked` — the draft itself, regenerated by
`controls/gen_controls.py` from the shipped rung by exact-string substitution —
measures (`controls/ir_table.py --closed`, marginal, `-O3 isolated`):

| | kernel Ir/call small | large | whole-program small | large |
|---|---:|---:|---:|---:|
| `unsafe` (shipped, unchecked) | 921.5427 | 3869.1756 | 2457.8441 | 9130.4152 |
| `r4_tabchecked` | 963.1643 | 4034.8228 | 2499.4656 | 9296.0708 |
| **difference** | **+41.6215** | **+165.6472** | **+41.6215** | **+165.6556** |

**+41.62 Ir/call on `small` and +165.66 on `large`** — and note that the two
denominators agree here to 4 decimals on `small` and to 0.009 on `large`, because
a bounds check is entirely inside the kernel and touches no allocator. `--closed`
proves that directly: the sum of the per-function deltas equals the
whole-program delta and **every term outside `kernel` is 0.0000**.

Per operation that is `41.62 / 24 = 1.73` on `small` and `165.66 / 120 = 1.38` on
`large`. So the shipped R4 and R5 index the table through `arr_get_unchecked` /
`arr_set_unchecked`, at the cost of two trusted items; 6 records what that does
to the TCB column.

**This is the sort of claim `.memory/01-ladder.md` finding 14 is about.** It was
plausible, it was p03's seeding mechanism applied by analogy, it was written in a
comment as though it had been measured, and it was wrong on the first thing that
could check it. `r4_tabchecked` is **not** an admissible R4 and is not offered as
one — it is the measurement that justifies two trusted items.

## 5. The `identity` pin, and the two lines it cost

`identity` is pinned `O3: exact`, `O0: norel` — the levels p08 and p14 pin.
Getting there needed two decisions, both measured, and **both are new to this
project because p27 is the first pattern whose kernel calls a vstd function that
is not `#[inline(always)]`.**

### 5a. vstd's allocation API cannot be called from a rung

`vstd::raw_ptr::ptr_ref`, `ptr_mut_write` and `ptr_mut_read` all carry
`#[inline(always)]` (`raw_ptr.rs:577`, `:601`, `:619`), which is why TASK_055
§2.4 measured byte-identity on a kernel that only *reads* through pointers.
**`allocate` and `deallocate` carry no `#[inline]` at all** (`raw_ptr.rs:908`,
`:948`). A rung that calls them emits

```
15a2f: call *0x41493(%rip)        # 56ec8 <_DYNAMIC+0x2d0>
```

— a **GOT-indirect cross-crate call**, whose target `nm` resolves to
`vstd::raw_ptr::allocate` at `0x15c10`. `unsafe.rs` is compiled by plain rustc
against no vstd and cannot produce that instruction; with vstd's own API the pair
measures **`differ` at both opt levels**, and at `-O3` the difference is not only
the call form but two extra `mov $0x1` argument set-ups, because the cross-crate
call cannot have its constants propagated into the callee.

So `verus.rs` carries `rec_alloc` and `rec_free`: `vstd::raw_ptr::allocate` and
`deallocate` copied into the crate, `#[inline(always)]`, **with vstd's own
`allocate` and `deallocate` as their verified twins**.

**The vstd-pure rung is built, verified and measured** —
`controls/gen_controls.py` emits it (`r5_vstdpure.rs`), and it additionally
deletes `rec_alloc`, `rec_free` and their twins, which are dead once the exec
code calls vstd directly:

```
verification results:: 15 verified, 0 errors
vstd-pure control tcb_items = 5 ['arr_get_unchecked', 'arr_set_unchecked',
                                 'buf_get_unchecked', 'emit', 'load_input']

r5_vstdpure vs unsafe, O3 isolated
  identical by raw machine-code bytes : False
  identical with pc-rel fields masked : False        <-- `differ`, not `norel`
```

**Two fewer trusted items, the same checksum on every input, and it is not a
rung.** `differ` rather than `norel` because the difference is not only the call
target: the cross-crate call cannot have its constants propagated into the
callee, so the call site also materialises `mov $0x1,%edi` / `mov $0x1,%esi`
that the local copy does not need.

### 5b. `*base = v` and not `core::ptr::write(base, v)`

`vstd::raw_ptr::ptr_mut_write`'s body is `core::ptr::write(ptr, v)`, but it is
`#[inline(always)]` over a **precompiled, already-optimised** vstd, so at `-O0`
R5 gets a bare store. `core::ptr::write` is `#[inline]` and not
`#[inline(always)]`, so in `unsafe.rs` at `-O0` it survives as

```
call 16590 <core::ptr::write::<u8>>
```

One instruction of difference, and `-O0` identity drops from `norel` to
`differ`. `unsafe.rs` writes `*base = v`, which is the same operation for a `u8`
and inlines at every level.

### 5c. What the pin measures now

```
O0/isolated    md5_raw: False   md5_raw_norel: True
O0/whole       md5_raw: False   md5_raw_norel: True
O3/isolated    md5_raw: True    md5_raw_norel: True
O3/whole       -- NO ROW, and the reason is not an omission --
```

⚠ **There is no `O3/whole` row because there is no `kernel` symbol to compare.**
At `-O3` in `whole` mode the kernel is inlined into `main`, so `asm.py syms`
finds no symbol containing `kernel` in either binary (558 symbols in `unsafe`,
none of them it) and `asm.py diff --sym kernel` raises `KeyError`. Section 1's
dead-argument table shows the same effect as "(inlined away)". The `identity`
pin is therefore over three cells, not four, and always was.

At `-O0` the crate names differ in length so call displacements differ — link
layout, not codegen. **This is the first pattern here where the `identity` pin
has a stated price in the TCB column**, and 6 argues that the price is a
relocation rather than an addition.

### 5d. What the vstd-pure rung costs, and the attribution trap in the middle of it

⚠ **Measured kernel-exclusive, `r5_vstdpure` looks 30.02 / 96.00 Ir/call CHEAPER
than the shipped pair. That reading is an artefact and it is the exact trap
3a exists to name.**

```
-O3 isolated     kernel Ir/call            whole-program Ir/call
                small       large           small        large
verus (shipped) 921.4525   3868.6520      2457.8441    9130.4284
r5_vstdpure     891.4458   3772.6520      2587.9546    9546.4256
difference      -30.0067    -96.0000       +130.1105    +415.9972
```

The kernel-exclusive column falls because the work **left the `kernel` symbol**:
`vstd::raw_ptr::allocate` is a separate function, so its layout construction and
null check stop being attributed to the kernel. Whole-program, the vstd-pure rung
is **130.11 / 416.00 Ir/call DEARER** — a cross-crate GOT-indirect call, twice
per record, that the local `#[inline(always)]` copy does not make.

**Both signs are real and they are of the same quantity.** Quoting the first
would have published "calling vstd is cheaper" out of a measurement that says
the opposite. It is `.memory/03-measurement.md`'s warning about
`kernel_exclusive_ir` in its sharpest available form, because here the two
columns disagree in **sign** rather than in magnitude.

### 5e. The epilogue asymmetry, priced — and the allocator contributes ZERO to the safe-vs-unsafe gap

R2 and R3 have no epilogue: dropping `[Option<Box<u8>>; TABCAP]` frees every
record still alive. R4, R5 and both C rungs walk `0..ntab` by hand.

**The clean measurement is not a control at all — it is callgrind's own
per-function table**, because rustc emits the drop as an out-of-line
`core::ptr::drop_glue::<[Option<Box<u8>>; 32]>` and glibc's `malloc` and `free`
are their own symbols.

⚠ **And it is a CLOSED decomposition, not four needles that agreed.** The first
version of this section looked up four function names and reported that three of
them accounted for the whole delta — which cannot answer *is anything else
moving?*. `controls/ir_table.py --closed` (ported from TASK_060_REVIEW's
`fndelta.py`, which is where the closure was first measured) parses the **entire**
`callgrind_annotate` table, normalises the object-path and crate-name
qualifiers so one function is one row, and prints the sum over **every**
function beside the whole-program delta. Marginal per call, `-O3 isolated`,
`small.bin` at `n_iters` 20000 → 40000 and `large.bin` at 5000 → 10000:

| function (`-O3 isolated`) | `safe_tuned` | `unsafe` | difference (small) | difference (large) |
|---|---:|---:|---:|---:|
| `kernel` | 1031.1904 | 921.5427 | **+109.6476** | **+661.6520** |
| `drop_glue::<[Option<Box<u8>>; 32]>` | 120.4218 | — | **+120.4218** | **+131.0938** |
| `malloc` | **421.1211** | **421.1211** | **0.0000** | **0.0000** |
| `free` | **310.2635** | **310.2635** | **0.0000** | **0.0000** |
| `_int_malloc` (`libc+0xab170`) | 587.8332 | 587.8332 | 0.0000 | 0.0000 |
| `_int_free` (`libc+0xab570`) | 72.9715 | 72.9715 | 0.0000 | 0.0000 |
| `__rdl_alloc` / `__rdl_dealloc` (the unix shim) | 80.0680 | 80.0680 | 0.0000 | 0.0000 |
| `__rust_alloc` / `__rust_dealloc` / `__rust_no_alloc_shim` | 10.0085 ea | 10.0085 ea | 0.0000 | 0.0000 |
| `main` | 14.0000 | 14.0000 | 0.0000 | 0.0000 |
| **SUM over EVERY function** | | | **+230.0694** | **+792.7458** |
| whole program | 2687.9135 | 2457.8441 | **+230.0694** | **+792.7458** |

**The sum over every function equals the whole-program delta to the last digit,
so `+230.0694 = +109.6476 + 120.4218 + 0.0000` is not three cherry-picked terms
— nothing else moved.** That is a much stronger statement than four needles
agreeing, and it is what licenses the next sentence:

**The ENTIRE allocator stack is equal to the last digit between the safe and the
unsafe rung** — not just `malloc` and `free` but `_int_malloc`, `_int_free`, the
unix shim and all three `__rust_*` symbols. The two representations make *the
same allocator calls*, in the same number, of the same size — the equivalence
argument of 2, measured rather than asserted, and the strongest form of it
available. ⚠ **This, and NOT the sweep's `nopen` coefficient, is the evidence for
that claim**; see 9c item 1, where the coefficient is shown to move by ~1 while
this table does not move at all.

**The epilogue asymmetry is `120.4218 / 230.0694 = 52.3%` of the gap on `small`
and `131.0938 / 792.7458 = 16.5%` on `large`** — the safe rungs' scope-exit drop,
which walks all `TABCAP` slots out of line, against the unsafe rungs' inline loop
over `ntab`. It is not a safety cost; it is what the language does with the table
on the way out. The share collapses on `large` because the drop glue is nearly
input-independent (it always walks 32 slots) while the kernel's own work is not.

The control `r2_epilogue` (R2 plus an explicit loop, on top of the drop glue)
measures `+115.4983` / `+324.9026`, which brackets the same quantity from the
other side and agrees with the 120.4218 above on `small` to within 5%. ⚠ It is
an **upper** bound and not the asymmetry itself, because it pays the drop glue
as well; the per-function table is the number to quote.

### 5f. The other 48% is the SPATIAL bounds-check tax, and none of it is the lifetime guarantee

5e leaves `+109.6476` "inside the kernel", and the sentence a reader supplies for
themselves is that *that* part is what the lifetime guarantee costs. **It is not,
and the pattern now owns the controls that say so.** Three one-lever siblings of
the shipped R4, all generated by `controls/gen_controls.py` and all printing the
shipped checksums on all seven inputs:

| | `panic_bounds_check` sites in `kernel` | kernel Ir/call small | vs R4ship | large | vs R4ship |
|---|---:|---:|---:|---:|---:|
| `unsafe` (shipped R4, 3 U-license items) | **0** | 921.5427 | — | 3869.1756 | — |
| `r4_tabchecked` (table read+store checked) | 3 | 963.1643 | +41.6215 | 4034.8228 | +165.6472 |
| `r4_bufchecked` (window read checked) | 2 | 1033.4335 | +111.8908 | 4387.4350 | +518.2594 |
| **`r4_allchecked`** (both — **zero** U-license items) | **5** | 1075.0550 | **+153.5123** | 4553.0822 | **+683.9066** |
| `safe_tuned` (R3) | **5** | 1031.1904 | +109.6476 | 4530.8276 | +661.6520 |

Read three things off it:

1. **The two levers are exactly additive**, in instructions *and* in panic sites:
   `111.8908 + 41.6215 = 153.5123` on `small` and `518.2594 + 165.6472 =
   683.9066` on `large`, to the last digit on both; and `2 + 3 = 5` sites, which
   is **the same number R3 has**. `r4_allchecked` is therefore the right control:
   it is an unsafe rung carrying exactly R3's surviving bounds checks. (Call
   targets resolved by symbol with `controls/gotresolve.py`, not by counting
   `call`s: `safe_tuned::kernel` has 5 `core::panicking::panic_bounds_check`,
   `unsafe::kernel` has 0.)
2. **An R4 that keeps R3's bounds checks costs `+153.51` in the kernel, and R3's
   whole in-kernel excess is `+109.65`.** So **R3 pays 43.86 Ir/call LESS of the
   spatial tax than an unsafe rung carrying the same checks** (22.25 less on
   `large`) — rustc's proofs delete more checks in the safe spelling than in the
   raw-pointer one.
3. Therefore **not one instruction of `R3 − R4` is the lifetime guarantee.** The
   gap is (i) three trusted items' worth of *spatial* checks, bought back at a
   discount by R3's better-typed table, and (ii) the epilogue asymmetry of 5e.
   The temporal property costs zero instructions, exactly as it costs zero
   trusted items (6).

⚠ **What this does NOT do is decompose the `+109.65` mnemonic by mnemonic.** It
attributes it — to a named, buildable, checksum-equal control that isolates one
lever — but it is an attribution by difference, not a listing-level derivation
like 9c item 2's `cmpb`/`je` pair. `r4_allchecked` and R3 are not the same
program, so "R3's in-kernel excess is the spatial tax" is a statement about two
measured endpoints and a bracket, not about instructions.

## 6. The TCB, and what the number does not rank

`tcb_items = 7` for `verus.rs`:

| item | class | what it licenses |
|---|---|---|
| `buf_get_unchecked` | U-license | the unchecked window read |
| `arr_get_unchecked` | U-license | the unchecked table read (4) |
| `arr_set_unchecked` | U-license | the unchecked table store (4) |
| `rec_alloc` | **relocation** | `vstd::raw_ptr::allocate`, 3 of its 5 `ensures`, twin = vstd's own |
| `rec_free` | **relocation** | `vstd::raw_ptr::deallocate`, all 6 `requires` respelled, twin = vstd's own |
| `load_input` | infra | argv, file I/O, LE decode; no `ensures` |
| `emit` | infra | `println!`; no `ensures` |

**Not one of the seven is the temporal property.** The whole lifetime
argument — a `PointsTo<u8>` consumed by a deallocation, a `Map<int,
PointsTo<u8>>` and a `Map<int, Dealloc>` maintained across open and close, and a
stale read that has no permission to present — rests on items that are
`external_body` *inside vstd* (`ptr_ref`, `ptr_mut_write`) or vstd `axiom fn`s
(`into_typed`, `into_raw`, `leak_contents`, the `Map` operations). p27 adds
**zero** project-local axioms for it.

### 6a. TASK_055 §2.5's alarm: confirmed in substance, wrong in its number

§2.5 predicted that a `raw_ptr` pattern would publish **`tcb_items = 2`** —
fewer than p01's array sum — while doing manual allocation, and that the TCB
column would therefore rank a raw-pointer kernel *safer* than a bounds-checked
one.

**The number is wrong and the concern is right.** A real pattern also indexes a
table and reads a window, so p27 publishes **7**, more than p01's 3 and more
than p14's 6. What survives, and is the honest form of the alarm, is this:

> **The part of p27 that does manual allocation contributes nothing to
> `tcb_items`.** Five of the seven items are the spatial accessors and the infra
> every pattern here ships, and the other two are a codegen device whose twins
> are vstd's own API. If p27 had been allowed to call vstd's `allocate`
> directly, it would publish **5** — and would not be a rung, because the
> `identity` pin would read `differ`.

So the two-column proposal's failure mode is real: **`tcb_items` counts this
project's own axioms and is not a safety ranking.** It is also, on this pattern,
**in tension with the `identity` pin** — a fact no previous pattern could
exhibit, and one worth stating plainly rather than burying: *you can have the
smaller trusted base or the byte-identical R4/R5 pair, not both.*

⚠ Do not compare p27's 7 with p01's 3 as if it meant p27 is less trustworthy.
The comparison that means something is 5 of p27's 7 against p01's 3, plus the
sentence above.

### 6b. **p27 ships 7, and that is FORCED, not chosen** — the trade is not this pattern's to make

The sentence above says the tension is real, and it is; what it under-sold is
that **only one side of it exists as a shipping option.** TASK_060_REVIEW A2 read
the `identity` pin out of every shipped `spec.md` in the tree:

> **18 of 18 pin `O0: norel, O3: exact`.**

So the alternative is not "publish 5 instead of 7". It is "p27 becomes the only
pattern in the tree whose R4/R5 pair is not byte-identical, i.e. the only one
that cannot contribute to `.memory/01-ladder.md` finding 1" — and it would be
that on the kernel where *"the proof erases"* is **least** a priori plausible,
because p27 carries the largest ghost state in the project (two tracked `Map`s
threaded through two loops, with `tracked_remove` in both). It would also make R5
the dearest Rust rung by `+130.11 / +416.00` (5d).

**What that costs is two items whose contracts the gate re-derives every run as
no stronger than vstd's own**, and which cost **zero** in the dimension the
pattern is about: the temporal property costs 0 trusted items in *both*
configurations — `r5_vstdpure`'s five are the same three spatial accessors plus
the same two infra items. **Ship 7.** Say it that way, and not "we chose the
bigger TCB", which invites a question the 18-of-18 fact has already answered.

---

## 7. The adversarial rows

A use-after-free has no magnitude axis — there is no "one byte past". What it has
is a **recycling** axis, and that decides whether the harm is disclosure or
noise. Measured, `-O3 isolated`, three runs each:

```
adversarial-uaf        c-gcc   : 1402190519230396416 1402190519230396416 1402190519230396416
adversarial-uaf        c-clang : 1402190519230396416 1402190519230396416 1402190519230396416
adversarial-noreuse    c-gcc   : 11043762887674013696 8077780024137721856 8060306882998740992
adversarial-noreuse    c-clang : 11096182311090956288 6147053158150809600 11078709169951975424
```

against the checked rungs' `4295919549966416896` and `3390747988282288128`, which
`c-gcc-h`, `c-clang-h`, `safe_naive`, `safe_tuned`, `unsafe` and `verus` all
print.

**`adversarial-uaf` is the row the pattern exists for**: OPEN, CLOSE, OPEN — the
tcache is LIFO, so the second OPEN gets the freed chunk back and writes the new
record into it — then READ the *closed* handle. R1 returns **the newer record's
byte under the older record's handle**: one record's contents delivered under
another record's name. It is deterministic across runs *and identical on gcc and
clang*, which is what makes it a measurement rather than an anecdote.

**`adversarial-noreuse` is the row that shows the harm is not always a
disclosure**: with no OPEN between the CLOSE and the READ the chunk is still in
the tcache, so R1 reads glibc's own safe-linked `next` word, which is a function
of the heap address and therefore of ASLR. ⚠ **Its `c-gcc` and `c-clang` cells
are deliberately not reproducible, and their recorded stdout in
`results/gate/p27-handle-table.json` changes on every gate run** — **and so are
`adversarial-many`'s, to the same measured count, which this file used to
disclose for only one of the two inputs (11a).** Stage 4 records
adversarial behaviour rather than requiring it, so this is a note and not a
failure — and it is the measurement behind `.memory/03-measurement.md`'s
constraint that a naked use-after-free is not a reproducible number.

### 7a. What catches it, and what does not

`harness/check.py` stage 7, `gcc -O1 -fsanitize=address,undefined` on
`c/kernel.c`, from `results/gate/p27-handle-table.json`:

```
adversarial-many.bin       expect=fires  fired=True  exit=1
adversarial-noreuse.bin    expect=fires  fired=True  exit=1
adversarial-stride3.bin    expect=clean  fired=False exit=0
adversarial-uaf.bin        expect=fires  fired=True  exit=1
degenerate.bin             expect=clean  fired=False exit=0
large.bin                  expect=clean  fired=False exit=0
small.bin                  expect=clean  fired=False exit=0

ERROR: AddressSanitizer: heap-use-after-free on address 0x502000000010
  READ of size 1 at 0x502000000010 thread T0
    #0 ... in kernel .../patterns/p27-handle-table/c/kernel.c
```

**Three for three on the adversarial rows, and clean on THREE benign ones — the
fourth is empty and no sanitiser evidence should be read into it.**
⚠ `adversarial-stride3.bin` declares `stride = 3` and the pinned driver loop
guards on `stride_w >= 4`, so the loop body never runs: **every rung prints 0
after ZERO kernel calls**, `inputs/gen.py:76-78` says exactly that, and the
gate's `proof_domain` records `"calls": 0, "ensures_checked": 0` for it. ASan is
`fired=False` there because there was no kernel to be clean about. The real
sanitiser evidence on this pattern is **3 firing / 3 clean**, and the empty row
is a *driver-guard* control, not a memory-safety one (TASK_060_REVIEW minor 4).
The expectation is *derived* by `model.py` from the simulated run rather than
tabulated per file, which is why the empty row is expected-clean automatically.

⚠ **This is the opposite of p02's result**, where idiomatic C
was silent in seven of eight builds: a use-after-free of a *freed chunk* is
exactly what ASan's quarantine is built to see, where p02's one-byte heap
overflow was absorbed by glibc's chunk rounding. **The interesting silence here
is not the sanitiser's, it is the CHECKSUM's**: on `adversarial-uaf` R1 exits 0,
prints a plausible 19-digit number, and prints *the same one on gcc and on
clang* — so a differential test against a second C implementation would not
catch it either. It takes a sanitiser, Miri, or a type system.

Miri is required and ran (`miri.required: true`, `ran: true`), over `unsafe.rs`
at `n_iters = 4`. It is the **only** tool in the matrix that checks the temporal
property on the *unsafe Rust* rung: ASan covers the C rungs, the proof and the
`identity` pin cover R5, and a wrong trusted body in `rec_free` — one that freed
a different pointer, or nothing at all — would satisfy every `ensures` in
`verus.rs` because `rec_free` has none to satisfy. See its
`SLB-TRUSTED-ARGUMENT` section below.

### 7b. Why the UAF is on adversarial rows only

Two independent reasons, either sufficient:

1. Stage 2 requires every non-adversarial cell to agree with `model.py` **and
   with every other cell**. R1 reading a freed record agrees with nothing.
2. **What a stale read returns is a function of the `-O` level**, and
   `build.py:67` puts both levels in one agreement set. TASK_055_REVIEW blocker
   B1 measured it: `gcc -O0..-O2` print `2582767925679282152` and `gcc -O3`
   prints `6789584477807083544`, because at `-O3` the stores into the recycled
   record are dead-store-eliminated — **the `-O3` binary does not contain the
   recycled record at all**, so that row would not have executed the bug it
   claimed to model.

`inputs/gen.py` enforces the rule by running a copy of the checked kernel over
every window of every blob it writes and refusing to emit a benign blob in which
any READ names a closed slot. **It fired on the first draft of
`degenerate.bin`**, which contained a `READ 0` after a `CLOSE 0`.

---

## 8. The R3 side: two in-contract spellings

`spec.md`'s `idiom` block pins the *operations* and deliberately leaves the
*spelling of the liveness test* free, exactly as p14 leaves its fold loop
unpinned. Two in-contract R3 spellings, both zero `unsafe` and zero TCB:

- **shipped**: CLOSE is `tab[h].take().is_some()` — one visit does the free, the
  invalidation and the test; READ is `match &tab[h] { Some(rec) => .., None =>
  .. }` — one discriminant test.
- **`r3_issome`** (`controls/`): R2's spelling — `is_some()` then
  `tab[h] = None`, and `is_some()` then `unwrap()` — two visits and two
  discriminant loads on each path.

```
-O3 isolated     whole-program Ir/call     small        large
safe_tuned (shipped)                      2687.9135    9923.1610
r3_issome                                 2697.4293    9955.1694
safe_naive                                2697.4293    9955.1610
```


**`r3_issome` is `safe_naive` — to the last digit on `small` and to within
0.0084 on `large`.** That is not a coincidence and it is worth stating: p27's R2
and R3 differ in *exactly* these two spellings and in nothing else, so the
control reproduces R2 from R3 and confirms that the whole `R2 − R3` gap is the
two fused tests.

**The cheapest R3 found is the shipped one**, on both inputs, by **9.52** on
`small` and **32.00** on `large`. ⚠ The word is "cheapest **found**", on a named
input, and never "minimum": three published floors on this project have been
refuted by the first lever the next agent pulled
(`.memory/01-ladder.md` finding 12). Two spellings is a two-lever search and is
not evidence of a floor.

**The fixed-R4 bound.** `R3ship − R4ship` is `+230.07` / `+792.75`
whole-program, and per finding 14 it bounds `inf(in-contract R3) − R4ship` and
nothing else — a bound only because R4 is held fixed **by fiat**. ⚠ And on p27
it is a bound on something that is **not the safety tax**, because of the
epilogue asymmetry in 5e and the spatial-check attribution in 5f. No pair
interval is reported, and 8a is why: the R4 endpoint **moved once**, so it has a
history rather than a width, and one endpoint that has moved once is not an
interval.

### 8a. THE R4 SIDE MOVED: a dead store the unsafe rung was carrying, deleted

TASK_060 shipped this sentence: *"the R4 side was searched once
(`r4_tabchecked`, which is dearer and inadmissible) and no admissible cheaper R4
was found, so the R4 endpoint is degenerate as far as this task searched"*.
**TASK_060_REVIEW major 2 falsified it with one deletion, and TASK_061 shipped
the deletion.** `.memory/01-ladder.md` finding 18 (p10) is the same sentence and
the same blocker: *an unsearched R4 side flatters the safe rung.* p27 would have
been the second pattern in a row to ship it.

**The line.** The epilogue used to read

```rust
if arr_get_unchecked(&live, j) == 1u8 {
    rec_close(arr_get_unchecked(&tab, j));
    arr_set_unchecked(&mut live, j, 0u8);      // <- DEAD
}
```

`live` is a kernel local, `j` only increases, and nothing reads `live[j]` again —
the store is dead in the plainest sense. It was there for symmetry with the CLOSE
path's line, which is **not** dead and which the pattern is *about*. **R3 has no
counterpart to it**, because R3's scope-exit drop does not maintain a liveness
array at all, so carrying it was a handicap on the unsafe rung.

**Before / after**, marginal, `-O3 isolated`, `controls/ir_table.py --closed`;
`r4_epiclear` regenerates the "before" rung from the shipped one by exact-string
substitution and reproduces it to the last digit:

```
                     whole small   whole large   kernel small   kernel large
r4_epiclear (before)   2464.6514     9140.9146       928.3500      3879.6750
unsafe      (shipped)  2457.8441     9130.4152       921.5427      3869.1756
                        -6.8073      -10.4994         -6.8073      -10.4994
```

**The two denominators agree to the last digit, and `--closed` says why: every
per-function term outside `kernel` is 0.0000.**

**The mechanism, three ways.**

1. **Counting.** The deleted line executes once per record still alive at scope
   exit, which is `nopen − nclose` — **6.75 on `small`, 10.50 on `large`**,
   computed from the blob with zero fitted parameters (`controls/sweep_ir.py`'s
   `regressors`). `10.4994 / 10.50 = 0.99994` and `6.8073 / 6.75 = 1.0085`
   instructions per surviving record. The 0.85% on `small` is codegen, not a
   second store.
2. **The regression, independently.** The 80-blob level fit for `unsafe` moved by
   **`nopen −0.9937`, `nclose +0.9952`**, and by `≤0.03` on every other
   regressor — i.e. the fit recovers *minus one instruction per OPEN, plus one
   per CLOSE*, which is exactly "one per surviving record" written in the fit's
   basis. Evaluated at the matrix inputs it predicts `−6.75 / −10.54` against the
   measured `−6.81 / −10.50`. Nothing told the regression what was deleted.
3. **Statically.** `n_fn_nopad` 151 → 150 and `fn_bytes` 638 → 633.

**It is admissible, and every leg was checked:**

- **R5 verifies `15 verified, 0 errors`** — the pinned count, unchanged — and
  `--cfg slb_twin` gives `20 verified, 0 errors`, also unchanged. The proof needs
  one edit and it is the ordinary one: the epilogue's invariant weakens from
  `wf(..)` over `[0, ntab)` to the same two conjuncts over `[j, ntab)`, after
  which neither `live[j]` nor the ghost `lv` needs updating. **A weakened
  invariant that DELETES exec work**, which is the shape worth noticing.
- **`R4 ≡ R5` `exact`**: `harness/asm.py diff --sym kernel` reports
  `identical by raw machine-code bytes : True` at `-O3 isolated`, and the
  `identity` pin is untouched.
- **Checksums identical on all seven inputs**, benign and adversarial, to the
  values `model.py` derives.
- **In contract**: `spec.md`'s `idiom.required[1]` pins
  `arr_set_unchecked(&mut live, h, 0u8);` — the **CLOSE**-path line, with `h` —
  and that line is untouched; `required[6]` pins `while j < ntab {`, also
  untouched. No `forbidden` token appears. The contract block did not move for
  this edit at all (the hash note at the top records the two prose keys that did
  move, for an unrelated reason).
- **`verus.items` did not move**: `controls/mkspec.py` regenerates `spec.md`
  byte-identically from the edited `verus.rs`, and `verus.items` is a mechanical
  `vparse` dump, so no item's `requires`/`ensures` changed.

**The direction test, in writing** (`.memory/01-ladder.md`): *an edit is
self-certification if it moves the pattern's own published figure in the
direction that flatters the author's thesis; for a safety-tax number that
direction is down.* This edit makes **R4 cheaper**, so the headline
`R3 − R4` goes **up**: `+223.26 / +782.25` → **`+230.07 / +792.75`**. Safe Rust
looks **worse** by 6.81 / 10.49 Ir/call than it did before. **Against interest —
passes**, and that is the reason to trust it rather than a reason to hesitate.

**And the word is "cheapest FOUND", not "minimum".** The R4 side has now been
searched **twice**: `r4_tabchecked` (dearer, and inadmissible — it spends the two
accessors 4 exists to justify) and `r4_epiclear` (dearer, admissible, and it was
the shipped rung). What was searched is: the two U-license levers (4, 5f), the
epilogue's per-slot work (here), and the vstd-call spelling (5a). What was **not**
searched: the fold's spelling, the cursor arithmetic, the table's layout, any
`#[inline]` placement, and anything at all on the R2 side. **A third lever may
exist and this section is the standing invitation to find it** — that is what
"cheapest found on `small.bin` and `large.bin`" means and "minimum" would not.

## 9. The sweep: what fits, what does not, and the DOMAIN

`inputs/gen.py --sweep` writes 80 blobs in three bands;
`controls/sweep_ir.py measure` takes the **whole-program** marginal Ir per call
over each (`(Ir(4000) − Ir(2000)) / 2000`, interleaved by cell, per-PID
scratch), and `... fit` does the regression. **Every number in 9a–9c is `-O3`,
inline mode `isolated`** — `sweep_ir.py`'s defaults, and named here because p10
fitted both modes and its regressors *swapped roles*
(`.memory/03-measurement.md`), so a mode-free per-call `Ir` is under-specified.
The `whole` mode was not swept. Four regressors, all computed from
the file with zero fitted parameters: `nopen`, `nclose`, `nread` (operations
*accepted*) and `nrej` (rejected on any path, folding `SENT`).

- **band O** — mix fixed, op count swept 8…128 in steps of 4 (31 blobs). Every
  regressor scales together, so this band alone cannot separate them.
- **band R** — op count held at 96, read fraction swept 0…0.80 (17 blobs). The
  allocator traffic falls exactly as the reads rise; this is what breaks band
  O's collinearity.
- **band S** — op count and mix held, the generator's live-record working set
  swept 1…32 (32 blobs).

### 9a. The LEVELS are not a law, and the number says so

```
c-gcc          nopen= 205.5226  nclose=  16.6407  nread=  22.4160  nrej=  24.2276  const= -72.2877   max|resid| 164.5959  n=80
c-gcc-h        nopen= 205.4624  nclose=  18.4425  nread=  24.3568  nrej=  24.1926  const= -72.9441   max|resid| 162.7976  n=80
c-clang        nopen= 207.1276  nclose=  10.5693  nread=  23.4968  nrej=  28.9165  const=-116.5077   max|resid| 152.6409  n=80
c-clang-h      nopen= 207.1377  nclose=  10.6064  nread=  24.7203  nrej=  27.9647  const=-116.1939   max|resid| 153.9943  n=80
safe_tuned     nopen= 223.1133  nclose=  25.5964  nread=  33.7158  nrej=  33.9437  const=  -4.1873   max|resid| 153.3527  n=80
unsafe         nopen= 222.1352  nclose=  13.6056  nread=  26.7180  nrej=  28.9652  const=-117.0837   max|resid| 153.5792  n=80
```

⚠ **`unsafe` is the TASK_061 rung** (8a). The old fit was
`nopen 223.1289 nclose 12.6104 nread 26.7182 nrej 28.9679 const −117.0504`; the
`c-gcc`, `c-gcc-h` and `safe_tuned` rows above reproduce the earlier sweep **to
the last digit**, which is what makes the `unsafe` row's `∓1` shift readable as
the deleted store and not as run-to-run noise. **The `c-clang` pair is new** —
TASK_060 did not sweep it (9c) and TASK_060_REVIEW did; both sweeps agree to the
last digit, and 9c now carries the result.

**A max residual of ~153–165 Ir/call on levels of 6 000–10 000 is 2%, and 2% is
not a law.** It is a fit with a missing column, and the residual has no band
structure (band means −1.4, +19.1, −8.8 for `unsafe`), so it is not a band
offset either. **This is not published as a law and the word is not used for
it.**

### 9b. The missing column is partly identified, and identifying it does not close the gap

Split `nopen` into tcache **hits** and **misses** — an OPEN reuses a chunk iff a
CLOSE has put one in the bin since the last OPEN took it out, which is
computable from the file with a 7-deep LIFO simulation and no fitted parameter.
`controls/sweep_ir.py hitmiss <sweep.json>`, all six swept cells:

```
cell            nopen (one)         hit      miss    resid 4-col  resid 5-col
c-gcc              205.5226    178.1106  221.9597       164.5959     142.1613
c-gcc-h            205.4624    177.8754  222.0046       162.7976     140.0339
c-clang            207.1276    178.0636  224.5555       152.6409     124.3984
c-clang-h          207.1377    178.3294  224.4121       153.9943     127.3678
safe_tuned         223.1133    194.2635  240.4126       153.3527     126.8890
unsafe             222.1352    193.3539  239.3934       153.5792     127.2230
```

**A recycled allocation is 43.8–46.5 Ir cheaper than a fresh one, consistently on
all six rungs** — and the split cuts the residual by only **14–19%**. So the op
*order* is a real column, it is now measured rather than hypothesised, and **it
is not the only one left**. This is p10's 3 → 4 → 6 arc arriving on the first
try: the domain is a list of missing columns, and the list is not closed.

⚠ Two bookkeeping notes. **The split used to be prose only** — the numbers were
printed by an ad-hoc probe and quoted here, so they could not be re-derived from
the tree and did not move when a rung did; `hitmiss` is now a shipped subcommand
and it reproduces the four previously published rows to the last digit. And **the
`unsafe` row is the TASK_061 rung**: `194.35 / 240.39` before the dead store went
(8a), `193.3539 / 239.3934` after, with the residual unchanged at `127.22` —
i.e. **deleting the store moved the level and not the fit's quality**, which is
what a single removed instruction should do.

### 9c. The DIFFERENCES, which is what may be quoted

The allocator is 58–63% of every level (3a) and **cancels exactly** in a
matched-spelling difference, which is why these residuals are two orders of
magnitude smaller:

```
  R1h - R1  (gcc)      nopen=  -0.0601  nclose=   1.8017  nread=   1.9408  nrej=  -0.0350  const=  -0.6564   max|resid|   6.4487
  R1h - R1  (clang)    nopen=   0.0100  nclose=   0.0370  nread=   1.2235  nrej=  -0.9519  const=   0.3138   max|resid|   5.9706
  R3 - R4              nopen=   0.9781  nclose=  11.9908  nread=   6.9978  nrej=   4.9785  const= 112.8963   max|resid|   2.5917
  R3 - R1h (gcc)       nopen=  17.6508  nclose=   7.1539  nread=   9.3590  nrej=   9.7510  const=  68.7568   max|resid|  33.5069
  R4 - R1h (gcc)       nopen=  16.6727  nclose=  -4.8369  nread=   2.3612  nrej=   4.7725  const= -44.1395   max|resid|  32.5951
```

Four things are worth reading off this, and one thing must not be:

1. ⚠ **RETRACTED, and this is the sharpest methodological result on the pattern:
   `R3 − R4`'s `nopen` coefficient is NOT a measurement of the allocation.** This
   section used to read *"`R3 − R4`'s `nopen` coefficient is `−0.0157` — zero to
   within the residual. The allocation itself costs the two representations the
   same"*, and cited it as the sweep's confirmation of the equivalence argument
   of 2. **It now reads `+0.9781` — with the same allocator, the same allocation
   sites, and a per-function table (5e) that still shows `malloc`, `free`,
   `_int_malloc`, `_int_free`, the unix shim and all three `__rust_*` symbols
   equal to the last digit.** The coefficient moved by ~1 while the thing it was
   claimed to measure did not move at all, because 8a's deleted store also scaled
   with `nopen`, and a regression coefficient absorbs *everything* that scales
   with its regressor. **The coefficient was never evidence for that claim**; the
   per-function decomposition was, and it is direct. Cite 5e, not this line.

   What `R3 − R4` does say: the gap is `≈1·nopen + 12·nclose + 7·nread +
   5·nrej + 113`, with `max|resid| 2.59` over 80 blobs — the per-operation
   bookkeeping plus the epilogue asymmetry, and **no term of it is the lifetime
   guarantee** (5f).
2. **`R1h − R1`'s `nread` coefficient is `1.9408`, with `max|resid| 6.4487` over
   80 blobs** — the liveness conjunct costs gcc about **2 Ir per READ**, and the
   attribution is mnemonic by mnemonic off the listing, not inferred from the
   fit. `harness/asm.py diff` on the two gcc kernels at `-O3`, on the READ path:

   ```
   R1                              R1h
   cmp    %r15,%rsi                cmp    %r15,%rcx          ; h < ntab
   jae    TGT                      jae    TGT
                                   cmpb   $1,(%rsp,%rcx,1)   ; <-- live[h] == 1
                                   je     TGT                ; <--
   mov    (%rsp,%rsi,8),%rax       mov    (%rsp,%rcx,8),%rdi
   movzbl (%rax),%r14d             ...
   ```

   **Exactly two instructions, one `cmpb` against the liveness byte and one
   `je`**, executed once per READ that passes the slot bound. `1.9408` fitted
   against `2` off the listing, with the shortfall in the `nclose` term below.
   Static counts agree: `n_fn_nopad` 146 → 149, `+3`.
3. ⚠ **But `R1h − R1` also carries `1.8017·nclose`, and R1's and R1h's CLOSE
   paths are character-identical** — the listing diff above shows gcc
   re-allocating registers across the whole function (`%rsi` → `%rcx`, `%rcx` →
   `%r8`) and moving its alignment padding (`xchg %ax,%ax` → `cs nopw`), which
   is where a per-CLOSE difference between two identical source paths can come
   from. That coefficient cannot be the conjunct; it
   is gcc's codegen shifting elsewhere in the function when the conjunct is
   added. **So "the hardening costs 2 Ir per protected read" is not what this
   fit says** — it says the two programs differ by about 2 Ir per read *and*
   about 1.8 per close, and only the first has a mechanism. Constraining the fit
   to `nread` alone gives `2.2180·nread + 13.8198` with `max|resid| 26.4193`,
   four times worse: the `nclose` term is carrying real signal.
4. **`R3 − R1h` carries `17.65·nopen` and `R4 − R1h` carries `16.67`** — Rust's
   allocation is ~17–18 Ir/record dearer than C's `malloc(1)`. That is
   `__rust_alloc`'s wrapper around `malloc`, not a safety cost, and it is why the
   C-vs-Rust rows of 3 must not be read as a safety column. ⚠ The two used to be
   `17.6508` and `17.6665` — *"identically on both Rust rungs"* — and they now
   differ by `0.98`, which is 8a's store again and **item 1's lesson a second
   time**: what looked like two rungs agreeing about the allocator was two rungs
   agreeing about the allocator *plus* an epilogue store that happened to cancel.

### 9e. The clang band, which TASK_060 named as the first thing to attack

TASK_060 swept four cells and wrote: *"**Not measured in this sweep: `c-clang`
and `c-clang-h`.** … A four-fold and twenty-four-fold compiler disagreement on
one added conjunct deserves the band and did not get it."* It cost one command —
`sweep_ir.py` already took `--cells` and already carried the fit pair — and
TASK_060_REVIEW ran it first; TASK_061's six-cell sweep reproduces it to the last
digit. **Three things it settles:**

1. **The conjunct's own cost differs by 1.59×, not by 4× or 24×.** The only term
   with a listing-level mechanism is `nread` (item 2), and it is `1.9408` for gcc
   against `1.2235` for clang. **The "4× / 24×" of 3b is a property of the two
   blobs' op mixes, not of the conjunct** — which is finding 5's shape one level
   deeper than 3b could see it.
2. **Item 3's hedge is confirmed by an independent compiler.** gcc's
   `1.8017·nclose` was flagged here as having no mechanism — R1's and R1h's CLOSE
   paths are character-identical — and clang's is **`0.0370`**. The same source
   change costs clang essentially nothing on CLOSE. On `large` that term alone is
   `21.5 × 1.8017 = +38.7` of gcc's `+91`. **So the term is gcc codegen churn,
   measured rather than argued.**
3. **Clang's `nrej = −0.9519` is what collapses its `large` total.** With 37.39
   rejected operations per call the hardened clang build *saves* about 35.6
   Ir/call on the reject path, which is why more work gives it a *smaller*
   hardening cost (`+3.76` on `large` against `+4.95` on `small`) — the paradox
   3b flags and could not explain.

Both fits predict the matrix-input totals inside their own residual:

| | predicted | measured |
|---|---:|---:|
| gcc, `small` | +19.29 | +19.83 |
| gcc, `large` | +91.34 | +91.01 |
| clang, `small` | +6.89 | +4.95 |
| clang, `large` | +1.45 | +3.76 |

And the clang LEVELS are the same 2% story as the four cells 9a swept —
`max|resid|` 152.6 and 154.0 on levels of 6 000–10 000 — so **9a's "2% is not a
law" reproduces on two more cells** rather than being a property of the four that
happened to be measured.

### 9d. The DOMAIN

⚠ **A law owes its domain, and the domain here is a list of MISSING COLUMNS.**
Four are known missing, one of them now measured (9b):

1. **`RECSZ`** — one byte per record, everywhere. glibc rounds `malloc(1)` to a
   32-byte chunk, so the entire sweep sits in **one size class and inside the
   tcache**. A record that crossed into another bin, or a workload that
   exceeded the tcache's 7-entries-per-bin, is a different allocator.
2. **`TABCAP`** — 32 slots, in every rung and every blob. It sets the table's
   extent, R2/R3's drop-glue trip count and R4/R5's epilogue trip count.
3. **the allocator** — glibc 2.39. Its tcache *is* the recycling mechanism the
   adversarial row depends on.
4. **the op ORDER** — swept in mix and count, not in interleaving. **Measured to
   matter (9b): ~44 Ir per record between a recycled and a fresh allocation.**

**The list is not closed**, and 9a's 2% residual is the standing evidence that
it is not.

## 10. The proof mutants

Two, both of which **fail**, and both aimed at the temporal property rather than
at a bound:

`controls/proof_mutants.py --run` regenerates both from `verus.rs` by exact-string
substitution and runs them; the levers are asserted to fire, so a mutant that
silently matched nothing cannot look like a measured null.

**M1 — delete the liveness conjunct from the READ path** (`if h < ntab &&
arr_get_unchecked(&live, h) == 1u8` → `if h < ntab`), *and the two ghost
`assert`s above the borrow with it*, so the failure is the real obligation and
not an assertion the author wrote. This is c/kernel.c's bug, written in the rung
that has to prove it:

```
verification results:: 14 verified, 1 errors
error: precondition not satisfied      <-- perms.tracked_borrow(h): dom().contains(h)
error: precondition not satisfied
```

**M2 — delete `arr_set_unchecked(&mut live, h, 0u8)` from the CLOSE path.** The
line the C programmer forgot:

```
verification results:: 14 verified, 1 errors
error: invariant not satisfied at end of loop body
```

**M2 is what makes "the proof forces the line C forgot" a fact rather than a
slogan.** `rec_free` has consumed slot `h`'s permission; the liveness array
still says the record exists; `wf` cannot be re-established. Note *which*
obligation fails: not a precondition at the deletion site, but the **loop
invariant** — the temporal property is a global fact about the table, and that
is why forgetting the line is invisible locally, in C as in Rust.

⚠ **M2 is the CLOSE path's store, with `h`. The EPILOGUE's store, with `j`, was
deleted at TASK_061 and the file still verifies 15/0** — see 8a and 0a. The two
lines are one character apart and could not be more different: deleting the first
fails the invariant, deleting the second lets the invariant get *weaker*. Both
mutants above were re-run after the TASK_061 edit and are unchanged (`14 verified,
1 errors` each, with the same diagnostics).

⚠ **The catcher is an ordinary `precondition not satisfied` / invariant failure,
NOT rustc's move checker.** TASK_055_REPORT §2.6's `E0382` is an artefact of a
hand-unrolled two-element probe and was retracted at TASK_055_REVIEW M2; with a
real permission map the permissions live in a `Map` and are removed with
`tracked_remove`, which is a *mutation* and not a move.

---

## SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[u8]`; the twin's body is `v[i]` on the
same `&[u8]` with the same parameters and the same clause text. `v[i]` is the
*checked* form of the identical operation — `<[u8] as Index<usize>>::index`
performs the bounds test `i < v.len()` that `get_unchecked` requires the caller
to have performed — so a `requires` too weak to license the unchecked read is too
weak to license the indexed one, and Verus sees the second. Nothing else can be
substituted: there is no other safe expression whose value is `v@[i as int]`.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** The body performs exactly one operation, a read of one element,
and returns it. `r == v@[i as int]` names that element and its value. There is no
second read, no write, no aliasing and no interior mutability: `v` is `&[u8]`, so
the item cannot modify anything, and `u8` has no padding or niche that could make
"the value read" ambiguous. The completeness question TASK_009_REVIEW raises — a
body that *also* reads `i + 1` — would be invisible to this contract, and that is
why Miri is mandatory on this pattern and runs over `unsafe.rs`, which contains
the same expression inline.

**(c) Does each clause mean the same in both configurations?** There is one
`requires` and one `ensures` and both are written in terms of `v@`, `i` and `r`
only. `v@` is `<[u8]>::view`, `i` is a `usize` parameter and `r` is the return
binding; none of the three is `#[cfg]`-dependent, none mentions a constant that
`slb_twin` could redefine, and `harness/check.py` separately rejects the token
`slb_twin` anywhere except in a twin's own attribute.

## SLB-TRUSTED-ARGUMENT verus.rs arr_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[T; N]`; the twin's body is `v[i]` on the
same `&[T; N]` with the same parameters and the same clause text. For a
fixed-size array `v[i]` is the checked form of the identical operation — rustc
emits the bounds test `i < N` that `get_unchecked` requires the caller to have
performed — so a `requires` too weak to license the unchecked read is too weak to
license the indexed one. **It is generic over `T: Copy` and `N` on purpose**: the
pointer table `[*mut u8; TABCAP]` and the liveness array `[u8; TABCAP]` are the
same operation on two element types, and one item is one axiom instead of two.
Genericity does not weaken the argument, because the body is `T`-independent and
`vstd::array`'s `array_len_matches_n` supplies `v@.len() == N` for every `N`.

**(b) Is the `ensures` complete?** The body performs exactly one operation, a
read of one element, and returns it; `r == v@[i as int]` names that element and
its value. `v` is `&[T; N]`, so nothing can be modified. **For `T = *mut u8` the
value is a POINTER, and "the value read" means the pointer's address *and* its
provenance** — `PtrData` carries both and `Seq<*mut u8>` equality is equality of
both, so the clause is complete in the sense the permission map needs: the
invariant `perms[j].ptr() == tab[j]` would not survive a body that returned a
pointer with the same address and different provenance. A body that also read
`i + 1` would be invisible here, which is why Miri is mandatory and runs over
`unsafe.rs`, whose `arr_get_unchecked` is the same expression.

**(c) Does each clause mean the same in both configurations?** One `requires` and
one `ensures`, both in terms of `v@`, `i` and `r` only, none `#[cfg]`-dependent
and none mentioning a constant `slb_twin` could redefine. `TABCAP` does appear in
the *call sites*' types, but not in this item's clauses.

## SLB-TRUSTED-ARGUMENT verus.rs arr_set_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked_mut(i) = x; }`; the twin's is `v[i] = x`, the checked
form of the identical store, with the same parameters and the same clause text.
Weaken the shared `requires` and Verus rejects the indexed store.

**(b) Is the `ensures` complete?** This is the harder of the two and the answer
is the whole-sequence form: `final(v)@ == old(v)@.update(i as int, x)` says both
*"slot `i` became `x`"* and *"nothing else moved"*. A trusted body that also
wrote `i + 1` would violate the second half and Verus would reject it **if it
could see the body** — it cannot, which is exactly TASK_009_REVIEW's x4 and
exactly why `miri.required` is `true` on this pattern and runs over `unsafe.rs`,
which performs the same store inline. There is no read, so there is nothing else
to state. **`x` is a pure VALUE parameter** — stored, never used as an address,
an index or a length — so it carries no precondition; that is the
parameter-coverage false positive `.memory/04-verus.md` names, `spec.md`'s
`verus.unsafe_justifications` declares it, and the gate shouts it every run.

**(c) Does each clause mean the same in both configurations?** `old(v)@`,
`final(v)@`, `i` and `x` only; no `#[cfg]`, no redefinable constant.

## SLB-TRUSTED-ARGUMENT verus.rs rec_alloc

**(a) Is the twin's body the right checked stand-in?** **The twin's body is
`allocate(size, align)` — `vstd::raw_ptr::allocate` itself.** That is the
strongest stand-in available anywhere in this project: the checked
implementation of the trusted item is the very API the item is a copy of, so
what step 5c-twin proves is that this crate's contract is **no stronger than the
one vstd already discharges**. If any `requires` here were weaker than vstd's, or
any `ensures` stronger, the twin would not verify.

⚠ **The obvious attack on that is circularity — "the twin's body *is* the axiom,
so it re-states it rather than re-deriving it" — and it is a CLEAN NEGATIVE,
broken four ways** (TASK_060_REVIEW A1, the strongest result of that review).
Weakening the trusted contract **and its twin together**, which is the only way
past the gate's signature-identity rule, is caught every time:

| mutant, edited on BOTH sides | shipped cfg | `--cfg slb_twin` |
|---|---|---|
| baseline | 15 verified, 0 errors | **20 verified, 0 errors** |
| `rec_alloc`: drop `size != 0` | 15/0 | **19 verified, 1 error** |
| `rec_alloc`: `valid_layout(size, align)` → `align != 0` | 15/0 | **19/1** |
| `rec_free`: `dealloc@.size() == size` → `>= size` | 15/0 | **19/1** |
| `rec_free`: delete the provenance conjunct | 15/0 | **19/1** |
| `rec_alloc`: drop `size != 0` from the **trusted item only** | 15/0 | 20/0 — *Verus does not catch it* |

The diagnostic names vstd's own site (`raw_ptr.rs:915`, which is vstd's
`size != 0`), and **vstd's `allocate` is not in this file's `external_body` set**,
so the twin is checked against a *different* axiom rather than against the item's
own — the "body calls the trusted item" rule is not being side-stepped. **The
last row is the important one: a ONE-SIDED weakening verifies 20/0 and is caught
by the gate's STRUCTURAL rule instead** (`norm_clause(twin.sig) ==
norm_clause(trusted.sig)`, `True` on the shipped file and `False` on that
mutant). **Both legs of the twin regime are load-bearing on p27**, which nothing
on this project had shown before.

**What the twin still cannot see is the item's BODY**, which here is a *copy* of
vstd's rather than a call to it, so body drift is invisible to Verus
(TASK_009_REVIEW ×4). Two backstops close it on this pattern and they belong in
the same breath: (i) both items are `#[inline(always)]` and inline into `kernel`,
and `md5_fn` of `unsafe::kernel` and `verus::kernel` are equal at `-O3 isolated`
— so R5's inlined body **is** R4's, byte for byte; (ii) Miri runs over
`unsafe.rs`, which contains that body. ⚠ Note the shape: the `identity` pin
certifies the two items whose reason for existing is to make the `identity` pin
`exact`. That is not vicious — **Miri is the independent leg** — but it is the
only place in the tree where the pin and a trusted item justify each other, and
it is worth saying out loud.

The item exists for **codegen and not for trust** (NOTES 5a): vstd carries no
`#[inline]` on `allocate`, so calling it emits a GOT-indirect cross-crate call
that `unsafe.rs` cannot produce and the `identity` pin drops to `differ`.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** The body performs one operation — `std::alloc::alloc(layout)`
after `Layout::from_size_align_unchecked(size, align)`, aborting on null — and
returns the pointer plus two tracked permissions. The three clauses state exactly
what a caller may conclude: the `PointsToRaw` covers `[addr, addr+size)`, the
`Dealloc` records the address, size, align and provenance the eventual
`rec_free` must match, and the returned pointer's provenance is the
`PointsToRaw`'s. **Three clauses, and `spec.md` says three** — it said "five"
until TASK_061, contradicting the same block's own `verus.items` dump two keys
away; the contract-hash note at the top of this file records the correction.
⚠ **Two further clauses were copied from vstd and then
DROPPED** — `addr + size <= usize::MAX + 1` and `addr % align == 0` — because
the gate's clause-mutation stage found them **not load-bearing**: this kernel
allocates at `align == 1`, where `addr % 1 == 0` is a tautology and the
`usize::MAX` bound is never used. Dropping them makes the item strictly weaker
and the twin still verifies, which is the direction the gate asks for. The
`requires` — `valid_layout(size, align)` and `size != 0` — is vstd's own, and the
second is deliberately not a tautology (`RECSZ` is 1, but the item is generic in
`size`).

**(c) Does each clause mean the same in both configurations?** Every clause is in
terms of `size`, `align` and the return binding `pt` only, and all three of
`PointsToRaw::is_range`, `Dealloc::view` and `DeallocData` are vstd items that
`slb_twin` cannot redefine. The shipped item and the twin sit in the same module
with the same imports and the same `opens_invariants none`.

## SLB-TRUSTED-ARGUMENT verus.rs rec_free

**(a) Is the twin's body the right checked stand-in?** **The twin's body is
`deallocate(p, size, align, pt, dealloc)` — `vstd::raw_ptr::deallocate`
itself**, for the same reason and with the same force as `rec_alloc`: the gate
proves this crate's copy is no stronger than vstd's original. Same codegen
motivation (NOTES 5a).

**(b) Is the `ensures` complete?** There is no `ensures`, and that is correct
rather than lazy: the item's whole semantic content is that it **consumes** the
`PointsToRaw` and the `Dealloc`. Linearity is the postcondition. A caller that
has given up slot `h`'s permission cannot later present it to `rec_read`, and
that is the temporal property this pattern is about — it is carried by the type
system rather than by a clause, which is why deleting `live[h] = 0` fails the
*invariant* rather than a precondition (NOTES 10, mutant M2). The `requires` is
vstd's own, six conjuncts, and covers every parameter: `p`, `size` and `align`
through the four `dealloc@.*` equalities, and both permissions through
`pt@.is_range(..)` and the provenance equality. **The body performs one
operation**, `std::alloc::dealloc(p, layout)`.

⚠ **Note what a wrong body here would do and what would catch it.** A body that
deallocated a *different* pointer, or that did nothing at all, would satisfy this
contract — there is nothing to satisfy. Nothing in Verus can catch it; **Miri
can**, and does, over `unsafe.rs`'s identical `rec_free`: a leak or a
mismatched free is a Miri error, and `miri.required` is `true` for exactly this
reason. This is the sharpest instance in the tree of `.memory/04-verus.md`'s
point that an `external_body` `ensures` is an axiom about a body no verifier
reads.

**(c) Does each clause mean the same in both configurations?** Every conjunct is
in terms of `p`, `size`, `align`, `pt@` and `dealloc@` only; `Dealloc::addr`,
`size`, `align`, `provenance` and `PointsToRaw::is_range`/`provenance` are vstd
items `slb_twin` cannot redefine. Both items sit in the same module with the same
imports and the same `opens_invariants none`.

---

## 11. What is NOT done, and what a reviewer should attack first

- **No layout population has been run.** `controls/clayout.py` is ported from
  p14 and takes p27's cells, but `--build`/`--time`/`--modes` have not been run,
  so **every `ns` number in `results/p27-handle-table.json` is one draw of
  unknown width** and none is quoted here (3c). p27 needs it more than p14 did,
  because its wall clock is a function of the allocator's state as well as of
  the code.
- ~~**The sweep measured four cells, not six.**~~ **DONE at TASK_061**: all six
  are swept and 9e is the result. The compiler disagreement of 3b is now
  explained — the conjunct itself differs by 1.59×, and the 4×/24× is the two
  blobs' op mixes plus clang's negative `nrej`.
- **The level fit is not a law and is not offered as one** (9a): max residual
  ~2% after the tcache hit/miss column is added (9b). At least one column is
  still missing, and 9c item 1 is the standing warning about what a coefficient
  of that fit does and does not measure.
- **`R2` was not searched, and the R4 side has now been searched twice.** Two
  in-contract R3 spellings were priced (8), two R4 levers (4, 8a) and the
  spatial-check attribution needed two more controls (5f); no attempt has been
  made to find a cheaper R2. **The R4 endpoint moved once** (8a) and is reported
  as *cheapest found on `small.bin` and `large.bin`*, never as a floor — 8a
  lists what was and was not searched.
- **`RECSZ` is 1 and was never varied** (9d). Everything here is one glibc size
  class inside the tcache.
- **`c/kernel.c`'s `abort()` on allocation failure is unreachable at `RECSZ = 1`
  on this box** and is present so that all seven rungs agree with
  `vstd::raw_ptr::allocate`'s own behaviour, not because it fires.
- **The `+109.65` in-kernel half of `R3 − R4` is attributed but not decomposed
  mnemonic by mnemonic** (5f). The attribution is by difference against a named
  buildable control, which is weaker than 9c item 2's listing-level derivation of
  the `cmpb`/`je` pair, and the section says so.
- **No `ns` claim, and none is possible yet** — see the first bullet.
- **Both `memset`s in the C rungs are DEAD and are kept anyway** (13a). Every
  read of `tab[]`/`live[]` is under `h < ntab` or `j < ntab` and every index
  below `ntab` was written by an OPEN, so deleting them changes no reproducible
  answer on any of 144 comparisons — while costing 98.23 / 279.10 Ir/call on
  gcc and 19.00 on clang. They are kept because they are the C spelling of the
  Rust rungs' compulsory initialisation and because deleting them would move
  every published C number; **a reviewer who thinks the C column should not
  carry a dead store has a real argument and 13a has the price of making it.**
- **`forbidden_hits` is recommended to become a hard failure and has NOT been
  implemented** (13d). The recommendation is the deliverable; `harness/` was out
  of scope for TASK_063.

### 11a. The gate JSON churns on every run, and here is the measured scope

⚠ This note exists so that a reviewer diffing two gate runs does not have to
re-derive whether the tree moved. **The scope it used to state was wrong in both
directions** (TASK_060_REVIEW major 3): it named `adversarial-noreuse` alone and
said the gate prints two notes.

**Both non-reproducible C inputs, not one.** Measured over the 8 buggy C cells
(2 compilers × 2 opt levels × 2 inline modes) × 3 runs:

```
adversarial-many       24 values, 21 DISTINCT  -> non-reproducible
adversarial-noreuse    24 values, 21 DISTINCT  -> non-reproducible
adversarial-uaf        24 values,  1 DISTINCT  -> 1402190519230396416
```

**`adversarial-many` is *exactly* as non-reproducible as `adversarial-noreuse`,
to the same count**, because most of its 24 stale reads land on a chunk still in
the tcache and return glibc's safe-linked `next` word, which is ASLR-dependent.
(TASK_060_REVIEW measured 24 of 24 distinct on its runs and TASK_061 21 of 24 on
its own — the collisions are two draws landing on the same address, and the
*equality* of the two rows is the reproducible part, not the count.)
`adversarial-uaf` recycles first and **is** deterministic, identically on both
compilers and at both opt levels. **And the gate already prints four notes, not
two:**

```
note: adversarial-many.bin/c-gcc:      opt/mode variants of this rung disagree (4 distinct behaviours)
note: adversarial-many.bin/c-clang:    opt/mode variants of this rung disagree (4 distinct behaviours)
note: adversarial-noreuse.bin/c-gcc:   opt/mode variants of this rung disagree (4 distinct behaviours)
note: adversarial-noreuse.bin/c-clang: opt/mode variants of this rung disagree (4 distinct behaviours)
```

**The measured churn**, two consecutive `check.py p27` runs on an unchanged tree,
diffed leaf by leaf (`controls/gatediff.py`):

```
verdict: PASS -> PASS | failures: 0 -> 0 | contract_sha256 unchanged
changed leaves: 33 of 1291
    16  adversarial stdout value
    14  adversarial cells[] group permutation
     3  ASan ==<pid>== in the recorded diagnostic
  by input: adversarial-many 15, adversarial-noreuse 17, adversarial-uaf 1
```

**Every one of the 33 is the adversarial non-determinism or an ASan PID**, and
the `adversarial-uaf` leaf is one of the three PIDs, not a checksum — that input
is deterministic. The count is not itself constant: TASK_060_REVIEW measured
`31 of 1290` on a different pair of runs, because how many `cells[]` groups end
up permuted depends on which values collide. **The invariant to check is the
categories, not the total.**

**Is the churn acceptable?** Yes, and the three things that could make it
otherwise were checked: `--check-stale` hashes `measurement_sources` and
`matrix_inputs` and never touches stdout (`measure.py:225-262`);
`results/p27-handle-table.json` records checksums for `small.bin` and `large.bin`
only, so **the measurement record does not churn at all**; and `source_sha256`
hashes files, not outputs. The only cost is the gate-JSON diff, and what it needed
was an accurate scope note.

⚠ **The ASan leaves are not p27's and should not be fixed here.**
`check.py:4575` records the sanitiser diagnostic verbatim, `==<pid>==` included,
so **every** pattern in the tree with a firing sanitiser row rewrites one leaf
per row on every gate run. Stripping `==\d+==` would make the block byte-stable;
that is a `harness/` change, it is reported and not made (TASK_060_REVIEW minor
8), and `.memory/02-bench-rules.md`'s "could this happen by accident?" test
applies to it.

---

## 12. The direction test, verified BYTE-EXACTLY — a method result, not a measurement

This is worth its own section because it is a first for the project and it cost
one line.

PROTOCOL definition-of-done 6 asks an engineer to record the `slb-contract`
block's sha256 *before* any cell is measured, because **a pattern lands in one
commit**: "no `required` or `forbidden` entry moved after I measured" is not
independently checkable, since a reviewer has no pre-edit snapshot to diff
against. That is exactly what happened at TASK_051 on p18, where the engineer
disclosed an edit honestly and the reviewer still could not verify its scope.

**On p27 the recorded hash was used, and it worked.** TASK_060 disclosed two
edits to the block and asserted nothing else moved. TASK_060_REVIEW clean
negative 25 reconstructed the pre-build block **from those two disclosures
alone** — restore `rec_alloc`/`slb_twin_rec_alloc`'s two `ensures` in vstd's
positions, restore `rec_free`/`slb_twin_rec_free`'s six `requires` to the
destructured spelling — re-serialised it, and got **`b1f2dbb3e48542af…`
exactly**. **Neither edit alone does** (`6d176cdf…`, `26a8ef39…`), so the
reconstruction is not a coincidence of a hash with slack in it: the two edits
are jointly necessary and jointly sufficient.

**So "no `required`, `forbidden`, `obligations`, `twin_obligations`, `identity`,
`miri`, `note` or `why` entry moved" became PROVABLE rather than asserted** — and
the direction of both edits (fewer `ensures`; more conjuncts judgeable, which the
gate's `requires_strength` record confirms as six `rec_free` conjuncts now judged
"not a tautology") is *toward* a stricter gate.

**TASK_061 did the same check on its own edit** and it is now the pattern's
habit: three prose keys moved, a semantic JSON diff names exactly those three,
and undoing only them reproduces `a0e83e2f2ee2e3bb…` byte for byte (the note at
the top of this file). One of the three is inside a `required` entry, which is
precisely the case where "I only changed the English" needs to be checkable — and
here it is, twice over: the reconstruction is byte-exact, and the gate's own
stage-`0b` audit reports the same 62 spellings / 88 present pairs on both sides. **The general lesson: one recorded line turns "editing the
declaration" from an unverifiable claim into a checkable one.** Editing a
declaration was never the problem; an unverifiable claim about it was.

## 13. `forbidden[0]` was the RULER and not the rungs — the entry is deleted

**The defect.** `idiom.forbidden[0]` was `` `memset(tab` ``, and `c/kernel.c:66`
and `c/kernel_hardened.c:46` both write `memset(tab, 0, sizeof tab);`.
`forbidden`'s scope is universal by the key's own meaning — `idiom_audit`'s
verdict line calls it *"decidable: no rung may spell a forbidden token"* — so
**both C rungs were out of p27's own contract**, and the gate has printed
`forbidden_hits: 2` in every p27 run since TASK_060. It is the only non-zero one
in eighteen patterns and it survived three tasks and two adversarial reviews.
`idiom.why` never said what the entry was forbidden *for*, though it explains
every other one.

### 13a. Which side is wrong, and the three measurements that decide it

**The entry is wrong. It is DELETED, not narrowed.** Three reasons, in
increasing order of how much they cost to check:

**(1) The entry excluded an operation that every rung performs, four of them
compulsorily.** All seven rungs zero the handle table before the op walk:

```
c/kernel.c:66-67           memset(tab, 0, sizeof tab);  memset(live, 0, sizeof live);
c/kernel_hardened.c:46-47  the same two lines
safe_naive.rs:48           let mut tab: [Option<Box<u8>>; TABCAP] = [const { None }; TABCAP];
safe_tuned.rs:40           the same
unsafe.rs:156-157          [core::ptr::null_mut(); TABCAP]   [0u8; TABCAP]
verus.rs:646-647           the same
```

In the four Rust rungs the zeroing is not a choice — Rust has no uninitialised
array. So `forbidden[0]` named a thing **all seven rungs do**, and could only
ever fire on the two that spell it in C. A universal-scope entry that excludes
what every rung is required to do is a bug in the ruler, not seven bugs in the
rungs.

**(2) An admissible respelling does the identical zeroing, at 0.0000 Ir/call.**
This is the measurement that makes the reading of (1) checkable rather than
rhetorical, and it is the p17 shape (`.memory/01-ladder.md`: an excluded
spelling and an admissible one compiling to the same 478 bytes). Three named
single-lever variants of **both** C rungs, generated by exact-string
substitution (`.temp/t63/mkvariants.py`) and built through `harness/build.py`'s
own flags at `-O3 isolated` (`.temp/t63/pricevariants.py`):

- **`A2_initlate`** — the two `memset`s replaced by `uint8_t *tab[TABCAP] =
  {NULL};` / `uint8_t live[TABCAP] = {0};`, declared in the memsets' **own
  position** (C99 mixed declarations), so the zeroing keeps its place after the
  `len < 4` and `nops == 0` early returns. It **satisfies `forbidden[0]`** and
  the program still zeroes the table.
- **`A_initlist`** — the same initialisers left at the top of the block. Kept
  because it is the obvious edit and it is **not** equivalent: an initialiser at
  block entry hoists the zeroing *above* both early returns, and gcc turns it
  into a `rep stos`.
- **`B_nozero`** — the two `memset`s deleted outright, no replacement.

Admission is decided by the gate's own matcher and not by eye —
`check.spelling_matches("memset(tab", src)` is `True` on both shipped C rungs
and `False` on `A2_initlate`'s two and on `B_nozero`'s.

Marginal whole-program Ir/call, `(Ir(2N) − Ir(N))/N`, n = 20000/40000 on `small`
and 5000/10000 on `large`, the convention `controls/ir_table.py --marginal` uses
and for the reason 3a gives (58–62% of this kernel's work is inside glibc's
`malloc`/`free`, which no `kernel` symbol contains):

| cell | gcc small | gcc large | clang small | clang large |
|---|---:|---:|---:|---:|
| `c/kernel.c` shipped | 2291.6035 | 8414.6688 | 2275.7692 | 8487.3410 |
| `A_initlist` | 2284.7963 | 8403.5766 | 2275.7692 | 8487.3326 |
| **`A2_initlate`** | **2285.7963** | **8404.5738** | **2275.7692** | **8487.3410** |
| `B_nozero` | 2193.3768 | 8135.5726 | 2256.7692 | 8468.3354 |
| `c/kernel_hardened.c` shipped | 2311.4302 | 8505.6792 | 2280.7224 | 8491.0960 |
| `A_initlist` h | 2304.6229 | 8494.5842 | 2281.7224 | 8492.1052 |
| **`A2_initlate` h** | **2305.6229** | **8495.5766** | **2280.7224** | **8491.0940** |
| `B_nozero` h | 2214.2034 | 8227.5914 | 2262.7224 | 8473.0932 |

**`A2_initlate − shipped` is `0.0000 / 0.0000` on clang for R1 and
`0.0000 / −0.0020` for R1h, and `−5.81 / −10.10` on gcc for both.** Statically
(`md5_fn` / `n_fn` / `n_fn_nopad`, `-O3 isolated`) clang gives the shipped rung
and `A2` **the same instruction counts** — 147/141 for R1, 146/142 for R1h — at
different `md5_fn` (`e828ef00fb01` vs `3f8ca64866d4`; `f785f3fc8712` vs
`2647789e5877`); gcc gives `154/146 → 156/148` and `155/149 → 158/151`.

> **So the entry could be satisfied without the program ceasing to do the thing,
> at exactly zero measured cost on clang and a small saving on gcc.** A `forbidden` entry that
> a rung can discharge by retyping one line, while performing the identical
> operation at the identical point for the identical instruction count, is a
> constraint on **typography** and not on the program. That is what settles
> (a)-vs-(b): if the entry were right, complying with it would have to change
> something, and it does not.

**(3) What it plausibly meant to exclude is unreachable by a token, and is
already pinned anyway.** The only subject in `idiom.why` adjacent to it is
*"THE HANDLE IS AN INTEGER AND THAT IS WHY NULLING IS NOT A DEFENCE"* — i.e. a
bulk clear of `tab` standing in for the per-slot invalidation, or NULL-ness
standing in for `live[]`. Neither is expressible as a narrowing of this token:

- **A bulk clear at CLOSE and the initialisation spell the same characters.**
  `spelling_matches` deletes all whitespace and has no notion of position
  (that is its point — `.memory/01-ladder.md`, *"the pin has no notion of which
  code runs"*), so no token distinguishes `memset(tab, 0, sizeof tab)` at
  line 66 from the same call inside the CLOSE arm. Narrowing is not available;
  the choice is delete or keep.
- **The hazard is already excluded by `required`, twice.** `required[1].c` pins
  `` `live[h] = 0;` `` in **both** C rungs and `required[0].c` pins
  `` `if (h < ntab && live[h] == 1) {` `` in the hardened one, so a rung that
  nulled `tab[h]` on close instead of maintaining `live[]` fails two `required`
  entries. A rung that bulk-cleared the table on CLOSE would additionally
  disagree with `model.py` at gate stage 2, because it would retire live slots.
  **Deleting `forbidden[0]` therefore removes no coverage** — it removes an
  entry that never covered the thing it was aimed at, while firing on the thing
  it was not.

**And the deletion makes `idiom.why` complete.** Before it, `why` explained 9 of
the 10 `forbidden` entries; after it, **9 of 9**. That is checkable in one line
and is the tidiest statement of the finding: the entry with no explanation was
the entry that did not belong.

⚠ **The task's own framing said "zeroing the table is not optional" and that is
false, measured.** `B_nozero` deletes both `memset`s and **every reproducible
cell still agrees**: 144 comparisons — 2 compilers × 2 opt levels × 3 variants ×
(5 inputs on R1 + 7 on R1h) — with **0 mismatches**, `.temp/t63/equiv.py`. The reads are all
guarded — `tab[h]`/`live[h]` only under `h < ntab`, `tab[j]`/`live[j]` only
under `j < ntab`, and every index below `ntab` was written by an OPEN — so both
`memset`s are **dead**, and on R1 gcc pays 98.23 / 279.10 Ir/call and clang
19.00 / 19.01 for them (R1h: 97.23 / 278.09 and 18.00 / 18.00).
The two rows excluded from that count are `adversarial-many` and
`adversarial-noreuse` on R1, which 11a already records as non-reproducible; the
same three runs of the **shipped** binary give 3 distinct values each, so they
disagree with themselves and not with the variant. **`B_nozero` is NOT
proposed**: the zeroing is what makes the C rungs the C spelling of the Rust
rungs' compulsory initialisation, deleting it would move every published C
number, and a defensive zero of a handle table is what real C does. It is here
because it is the measurement that refutes "not optional", and because it prices
the initialisation the pattern was forbidding itself from writing.

### 13b. Direction test, in writing

`.memory/01-ladder.md`'s repaired test: *an edit to a declaration is
self-certification if it moves the pattern's own published figure in the
direction that flatters the author's thesis; for a safety-tax number that
direction is **down**.*

**No published figure moves at all.** No rung source is touched, so every `Ir`,
`ns`, `md5_fn`, static count, `tcb_items` and obligation count in 3, 5, 6, 8 and
9 is the number it was; `source_sha256` for `c/kernel.c` and
`c/kernel_hardened.c` is unchanged. The edit is a pure widening of the
admissible class.

**And the widening is measured, in the direction that costs the author.** What
it admits is C spellings that bulk-zero the table, which on this tree is *only*
the shipped rungs and `A2_initlate`. `A2_initlate` is **cheaper** than the
shipped rung on gcc (−5.81 / −10.10) and identical on clang, so if it moved
anything it would move the C baseline **down**. Note which number that is and
which it is not: **the C-hardening delta `R1h − R1` does not move at all**,
because the lever moves *both* C rungs by the same amount (−5.8072 on R1 and
−5.8073 on R1h at `small`); what would move is the safe-Rust-vs-C gap, and it
would get **larger** — against the thesis. Rust cannot spell `memset(` in any of
these rungs, so the widening is C-only and the four Rust rungs' admissible class
is byte-for-byte what it was.

**A reproducibility control, taken for free.** The shipped-cell column of the
table above was measured by this task's own probe and reproduces 3's published
whole-program figures: `2291.6035 / 2311.4302 / 2280.7224` at `small` and
`8505.6792 / 8491.0960` at `large` are identical to the published values, with
the two gcc/clang `large` R1 cells differing by `0.0028` and `0.0084` — noise at
the fourth decimal, on a separate process and a separate scratch directory.

**The opposite resolution would have failed this test in the interesting
direction, which is why it is worth naming**: *keeping* the entry and respelling
the C rungs to `A2_initlate` would have made the C rungs **cheaper by 5.81 /
10.10 Ir/call on gcc** for a typographic reason — i.e. an idiom pin deciding a
measured number, which is the p13 shape `.memory/01-ladder.md` records
(TASK_045_REVIEW blocker 1: an idiom entry scoped to some rungs was worth 48% of
p13's published margin). Deleting the entry is the resolution that leaves the
measurements alone.

⚠ **`why` was NOT widened to bless the hits, and that is checkable**: `why` is
byte-identical across the edit, `contract["idiom"]["why"]` has the same length
and the same sha256, and the whole diff is one deleted array element.

### 13c. The disclosure, byte-provable

`.temp/t63/entry.py` deletes and re-inserts the single line and hashes both
ways. It never embeds the JSON; it operates on the exact line as it stands, so
it cannot drift from what shipped.

```
as it stands (with)    contract_sha256 371a680bb5b85f2bdbfb418ab6796b1665037aa199419fce32a5eafb9d5596ac
                       spec.md sha256  8225423c0ce70f8d8c25642bfc313022e3727cd7722922eea24bba2679fcbf89
removed                contract_sha256 01e2137f9a1bcce2453ecdb43ea9260dbc6d91e7e5073104d0e13b7800ddef07
                       spec.md sha256  ab10a2bb62907261d693a915759a56bbf9b3b83257b1e24ad35051f6d3f031b5
removed -> restored    contract_sha256 371a680bb5b85f2bdbfb418ab6796b1665037aa199419fce32a5eafb9d5596ac   (equal)
                       spec.md sha256  8225423c0ce70f8d8c25642bfc313022e3727cd7722922eea24bba2679fcbf89   (equal)
```

`371a680b…` is TASK_062's recorded hash and the one in the committed
`results/gate/p27-handle-table.json`, so the undo lands on the shipped block and
not merely on something with the same shape.

**The audit is the second, independent witness that only `forbidden` moved:**

```
              spellings  pairs  present  forbidden_hits  pins_nothing  scoped_absent
before             62     194       88               2             3             36
after              60     188       86               0             3             36
```

−2 spellings (one entry × two languages), −6 pairs (2 C rungs + 4 Rust rungs),
−2 present (exactly the two hits), and `required`'s two buckets **unchanged**.

**And a third witness, the semantic JSON diff TASK_061 introduced**: parsing the
block at `HEAD` and the block on disk and comparing key by key reports every
top-level key equal except `idiom`, `idiom.required` equal element for element,
`idiom.why` equal at **13 607 bytes and sha256 `2524f8677c04…` on both sides**,
and `idiom.forbidden` `10 → 9` with the removed element being exactly
`` "`memset(tab`" ``. So "only the `forbidden` array moved" is checked three
independent ways: the byte-exact undo, the stage-`0b` audit, and the semantic
diff.

⚠ **`controls/mkspec.py` had gone stale at TASK_062 and running it deleted the
named-spelling paragraph** — found here, by running it. `spec.md`'s generator
did not carry TASK_062's append, so the documented regeneration produced a `why`
of 2 602 bytes instead of 13 607 — 11 005 short, the 11 003-byte paragraph plus
the joining space and full stop — which `check.py::named_spelling_problem` now
hard-fails. **The generator would have silently reverted the fix that landed one
task ago.** Repaired in the same commit and **checked**: `mkspec.py` reads
the paragraph out of a donor `spec.md` at run time and asserts its sha256
against `check.NAMED_SPELLING_SHA256`, and running it now reproduces this
`spec.md` **byte for byte** (`ab10a2bb62907261…`, `diff` empty). It reads rather
than embeds because a nineteenth verbatim copy is the thing the byte-identity
invariant exists to prevent; the "reading from a sibling FAILS OPEN" objection
recorded beside that constant in `check.py` is about the **gate**, where a
missing paragraph must be a failure, whereas this reader raises on a missing or
altered donor and so fails closed. **And that is the project's existing
convention rather than a new idea**: `patterns/p10-fir-stencil/controls/mkcontract.py`
and `patterns/p18-varint-shift/controls/mkcontract.py` are the only other
in-tree `slb-contract` generators and **both** already read the paragraph out of
a donor `spec.md` at build time (p18 from p14, p10 from p18) and cross-check it.
p27's generator was the one that embedded its `why` whole, which is why it was
the one that went stale.

**The gate agrees with all of it.** `harness/check.py p27` after the edit:

```
  contract sha256 01e2137f9a1bcce2453ecdb43ea9260dbc6d91e7e5073104d0e13b7800ddef07
    ok   named-spelling standard present in idiom.why, verbatim (11003 bytes, sha256 59748cce2db5...)
    ok   idiom declared: 12 required, 9 forbidden spelling(s), 11 of them per-language
    audit  60 backticked spelling(s) over 6 rung(s) -> 188 (spelling, rung) pair(s), 86 present
    audit  forbidden: 18 spelling(s), 0 hit(s)  (decidable: no rung may spell a forbidden token)
    audit  required : 3 pin nothing, 36 scoped-absent pair(s)
check.py: PASS
```

### 13d. `forbidden_hits` across all eighteen patterns — the fail-vs-print measurement

`.memory/02-bench-rules.md` declined making `forbidden_hits` fail (TASK_053 →
TASK_056) because the accident it cited as precedent was structurally invisible
to the check; TASK_062 re-opened that on the strength of this defect, which is
visible to it. TASK_062 also measured the fact that cuts the other way: this
`2` was **printed in the verdict, written into the gate JSON, and transcribed
into this file**, across three tasks and two adversarial reviews, and nobody
acted. *A number that is printed is not a check.* So the question is
**fail-vs-print**. The measurement, computed from the tree by calling
`check.idiom_audit` over every pattern (`.temp/t63/sweep_forbidden.py` — a read
of `spec.md` plus the rung sources, not a gate run):

```
                        forb_sp  hits  raw          forb_sp  hits  raw
p01-array-sum                 0     0    0    p11-nul-scan        8   0   0
p02-buffer-copy               2     0    1    p12-strcat-fixed   12   0   0
p03-bounded-stack            10     0    2    p13-strncpy-trunc  14   0   3
p04-ring-buffer              12     0    3    p14-field-split    16   0   1
p05-index-flatten             0     0    0    p16-tlv-walk        4   0   2
p06-rotate                   14     0    0    p17-http-range      2   0   2
p07-binary-search            10     0    3    p18-varint-shift   16   0   3
p08-overlap-move              2     0    0    p27-handle-table   18   0   0
p09-bitset                   10     0    5
p10-fir-stencil              10     0    4    TOTAL             160   0  29
```

**With 13a landed, `forbidden_hits` is 0 on all 18 patterns, over 160 declared
(spelling × language) obligations.** Before it: `2 of 162`, both in p27, both
`memset(tab`. So **a failing check has zero false-positive surface on today's
tree** and costs a few lines in `check.py`.

The `raw` column is the number that decides how much of that zero is luck. It
matches the same tokens with whitespace deleted on both sides but **comments,
string literals and Verus ghost clauses NOT blanked** — i.e. it isolates exactly
what the blanking half of `spelling_matches` is worth — and it gives **29 hits
across 11 patterns** (p02 1, p03 2, p04 3, p07 3, p09 5, p10 4, p13 3, p14 1,
p16 2, p17 2, p18 3): hardened-C comments quoting the spelling they refuse,
p16's ghost loop invariant, p17's comment and format string, and so on. Every
one of them is killed by the blanking. So the zero is a property of the
**matching rule**, and a failing `forbidden_hits` would inherit all of the
rule's risk: a regression in comment-blanking or ghost-blanking would not shout,
it would fail 11 patterns at once. `spelling_matches` is selftested at stage 0 and hashed into
`source_sha256`, which is the mitigation, and it is the same mitigation the
current printed number already relies on.

**Recommendation: MAKE IT FAIL — but batch the `check.py` edit, do not pay a
sweep for it alone.** The reasoning, and the ratio, both ways:

- **The accident test passes with an instance rather than an argument**
  (`PROTOCOL.md` rule 5, and `.memory/02-bench-rules.md`'s own follow-up rule
  that the proposed check must be able to SEE the incident). p27's defect is
  hand-written, was an honest mistake, is exactly the kind of thing that happens
  again, and `forbidden_hits` computed it correctly from `rung_sources` on the
  first run and every run after.
- **The project already crossed this bridge, one task ago, in the same gate
  stage, for the same class of defect.** TASK_062 turned the standing prose
  one-liner into `named_spelling_problem`, a hard failure, precisely because a
  rule that lives in prose *did not fire across four tasks and two reviews*.
  `forbidden_hits` is that finding with the sign flipped: a rule that lives in a
  printed integer did not fire across three tasks and two reviews. Declining now
  is inconsistent with a decision the manager made a task ago on strictly weaker
  evidence.
- **The route out is honest and one-line**, which is what
  `.memory/02-bench-rules.md` asks of a new hard failure: either the entry is
  wrong (delete/narrow it, a declaration edit owing the direction test — this
  task) or the rung is wrong (respell it). No exemption mechanism is needed
  today because no legitimate hit exists; add one the day one does, rather than
  building it against a hypothetical.
- **The ratio, and it does NOT favour doing nothing.** 1 defect in 18 patterns
  shipped this way; the catalogue has 47, so ~29 patterns remain and the naive
  expectation is **~1.6 more**. Against that, the check is a few lines. The real
  cost is the **18-gate sweep** an edit to `check.py` forces (`source_sha256`
  moves in every record; TASK_062 measured ~50 minutes), and *that* is the
  argument for batching rather than for declining: paid alone it buys 1.6
  expected catches, paid alongside the next `check.py` change it is free.
  **And batching is already this project's rule for exactly this shape** —
  `RECAP.md` records `O3d` as built, measured inert and reverted, with *"landing
  it costs a full re-measure … Land it bundled with a pattern that is being
  re-measured anyway."* Same trade, one layer up: the check is cheap, the sweep
  is not, and the sweep is owed by the next `check.py` commit regardless.
- **The honest argument against, stated because it is the strongest one and it
  is mine.** 13a's own measurement shows a failing check would have been
  **dischargeable by the wrong fix**: respelling both C rungs to `A2_initlate`
  costs 0.0000 Ir/call on clang, satisfies the entry, and leaves the ruler bug
  and the silent `why` exactly where they were. A gate that can be turned green
  by retyping a line does not force the question this task actually answered. It
  does, however, force the line to be *retyped in a commit*, which moves
  `source_sha256` for the rung and every C cell's `md5_fn` with it, and is
  visible to a reviewer — whereas the status quo produced nothing at all for
  three tasks. **Weak forcing beats none.**
- **A latent false positive, bounded and named so nobody re-derives it.**
  `rung_sources` includes `CONTROL_CELLS` present in the pattern directory. That
  is `["safe_naive_verus"]` only — a real rung, which should honour the contract
  — and **no pattern ships one today** (all 18 report exactly 6 rungs), so the
  surface is empty. If a future pattern ever ships an out-of-contract *control*
  inside the pattern directory, that control's deliberate violation would become
  a gate failure. Same shape as the `no_rung` bucket TASK_021 closed: invisible
  until the first instance, and loud on that day rather than silent.

⚠ **Not implemented here.** TASK_063 forbids touching `harness/`, and the
recommendation is the deliverable. The number above is what it should be
measured against on the day it lands.
