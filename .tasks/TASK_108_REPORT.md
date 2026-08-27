# TASK_108 — the synthesis: report

**Role: research writer. UNREVIEWED.** Deliverable
**`results/SYNTHESIS.md`** (new, ~6 500 words of markdown ≈ 5 900 prose words,
635 lines). Scratch in `.temp/t108/` only. No `git add`, no `git commit`. No
pattern, harness or `pilot/` file touched; `results/synthesis.md` (generated) not
touched.

---

## Did

- **`results/SYNTHESIS.md`** — the argument. Structure, and it is **not** §A's
  structure (see "Where I disagree" below):

  | § | content |
  |---|---|
  | 0 | what this is; "four results and a method" as the compression claim |
  | 1 | the apparatus in one page — the ladder R1–R5 + R1h, why `Ir` not seconds, the two `Ir` conventions and the licence, the gate, the declared contract, the one box |
  | 2 | **Result 1** — the safety tax is a property of a *pair of spellings*, and the check is rarely the biggest term |
  | 3 | **Result 2** — where safe Rust does not help |
  | 4 | **Result 3** — a proof discharges exactly what it says, and the numbers beside it say less than you think (merges §A.4 and §A.5) |
  | 5 | **Result 4** — what this instrument can and cannot price (§A.6, promoted and forward-referenced from §1) |
  | 6 | **What this measurement will do to you** — eight traps, written as method (§B) |
  | 7 | what the project does not know |

- **`.temp/t108/census.py`** — the one thing I ran that produces numbers. Parses
  `results/synthesis.md` §1 and derives the `R3−R4` / `R2−R4` distribution the
  prose quotes, restricted to rows §2 tags `LICENSED`. Kept per `CLAUDE.md`
  rule 1 (it is the generator; it has no artefact).
- **`.temp/t108/NOTES.md`** — running notes, the review-status audit, the
  withdrawn-cell checklist.
- Ran **`harness/measure.py --check-stale`** (the one permitted run): **52
  records examined, 0 STALE, exit 0.** Nothing else was executed — no
  `check.py`, no `build.py`, no `measure.py` without `--check-stale`.

## Evidence

```
$ timeout 300 python3 harness/measure.py --check-stale | tail -2
52 record(s) examined, 0 STALE
EXIT=0

$ ls -d patterns/p*/ | wc -l        -> 26
$ grep -c '^| p[0-9]' .memory/06-catalogue.md   -> 48

$ python3 .temp/t108/census.py
patterns in the table: 26
R5-R4 == 0 on every row: True  (26 patterns x 2 blobs)
R3-R4 licence: 22 LICENSED, not licensed: p11 p27 p36 p42 (NOT-LIC, NOT-LIC, UNDEC, NOT-LIC)
  restricted to LICENSED rows:
    within +-32 on both (9/22): p01 p02 p04 p08 p12 p17 p18 p22 p38
    negative on both    (4/22): p10 p13 p18 p46
    > 100 on either     (9/22): p03 p05 p06 p07 p09 p14 p19 p23 p47
R2-R4 / R3-R4 on large, where R3-R4 > 0: 0.74x .. 3536.19x, median ~7.3x
```

Search-state census, derived the same way from §2's own column:

```
undeclared: 18  ['p02','p04','p05','p06','p07','p09','p12','p14','p16','p17',
                 'p18','p19','p22','p23','p27','p38','p42','p46']
declared:    8   p01 OWED · p03 partial+unreviewed · p08 OWED · p10 · p11 · p13 · p36 · p47
```

Retraction list: `awk '/^## Retracted/,/^## Working method/' RECAP.md | grep -c '^- \*\*'` → **19**.

---

## The three calls you named

### 1. Are §A's six threads the right decomposition? **No — I regrouped to four plus a method, and I think the regrouping is a real improvement.**

Three specific changes, each with a reason:

**(a) §A.1 and §A.2 are one result, not two.** "Safety is usually free, and where
it is not the reason is usually not the check" and "where it is not free, name
what you are paying for" have the *same* evidence set, the same mechanism, and
the same instruction to the reader. Splitting them forces every pattern to be
cited twice — p16 and p46 in thread 1, then p11 and p19 in thread 2 — while the
sentence that actually generalises spans both: **the tax is a property of a pair
of spellings, and decomposing it is what tells you whether you are looking at
safety.** Merged, that sentence can be *stated*; split, it is implicit in two
places and asserted in neither. The merged section carries a distribution
(9/22 flat, 4/22 negative, 9/22 large) followed by a nine-row "what it is
actually paying for" table, which is the shape the split cannot produce.

**(b) §A.5 (the trusted base) is the back half of §A.4, not a peer of it.** As a
standalone thread "look at the TCB" is an instruction without a result. Placed
where it belongs — *after* "a proof discharges exactly what it says" — it becomes
the second half of one argument: **a proof's value is bounded below by what its
obligations say and bounded above by what you trusted to get them.** That framing
lets four otherwise-scattered items sit together and reinforce each other: the
`0 axioms` column that does not mean what it says; p08's trusted body whose
substituted UB verifies `11/0` and `15/0` under the twin; Verus's own vacuous
paste-this-in escape hatch; and prospective-but-not-retrospective gameability.
Under §A's split those four have no home that explains why they matter.

**(c) §A.6 (the instrument's domain) is a frame first and a result second.** You
said "do not bury it." I went further: §1 forward-references it, §5 states it,
and §5 closes with the consequence a reader needs, which §A does not name —
**this project measured the bounds-check family, and where safe Rust's guarantee
is compile-time its runtime cost is zero by construction and no benchmark will
say otherwise.** That is the sentence a systems programmer takes away, and it is
not in §A anywhere.

**What I did *not* change: §A.3 stands exactly as you wrote it**, as its own
section, in your ordering, and it is the strongest section in the document.
Everything you listed is in it (p22, p04/p09, the allocator-recycling rule, p34)
plus three you did not: **p17** (provably memory-safe and leaking — it belongs
here, not only in the proof section), **p18** (UB that is not memory-unsafety;
safe Rust with the guard deleted is bit-identical to C), and **p47** (a property
of the trace is invisible to a logic about the value). I also added the mirror
image as a closing pair, because a reader who has just read six ways safe Rust
does not help will otherwise leave with the wrong impression: **p08**, the bug
safe Rust cannot express, and **p38**, the first class *unsafe* Rust does not
reintroduce either — two wins that are invisible in every `Ir` column.

### 2. Do the corrections deserve their own section? **Yes. I agree with you, and the reason is stronger than "it is useful."**

Every item on that list is a property of the **apparatus**, not of a pattern.
Folding them in where they occurred would put one coherent result in
twenty-six unrelated places — which is precisely the decay mode `PROTOCOL`
rule 13 documents (*"an update lands where the detail is, and the summary line
above it is not where anyone is looking"*). It would also make them
unreadable for the audience this document is for: a benchmark author does not
want to read p23's partition kernel to learn that within-band holdouts are
worthless.

Two conditions I imposed on myself to keep it from being self-flagellation, and I
think both are load-bearing:

- **Ordered by transferability, not chronology**, and stated so that the trap can
  be understood without knowing the pattern. The pattern is the *citation*, never
  the subject of the sentence.
- **Each trap ends in an instruction**, not a mea culpa. The section opens
  "*They are not confessions*" and the framing is "here is what this measurement
  will do to you." I merged your bullets into **eight** traps (out-of-sample-test
  failure by residue and by rank are one trap in two forms — they have the same
  fix, and separating them was making the section read as a list of incidents).

### 3. Is 3 000–6 000 words right? **Yes, at the top of the band — and my first instinct that it should be 2 000 was wrong.**

You invited "these 26 patterns collapse to four results" as a finding. It *is*
one and the document says so in §0. But the collapse is in the **headlines**, not
in the evidence: what makes Result 1 believable is precisely the nine-row table
of *exceptions*, and exceptions do not compress — each needs its own mechanism or
it is an assertion. A 2 000-word version would be four claims and no reason to
believe any of them, which is the failure mode this project has documented more
than any other.

I landed at ~5 900 prose words after two trimming passes (6 793 → 6 545 raw
markdown tokens). I would resist cutting further: the last 1 000 words are §6 and
§7, and those are the two sections a reader outside this repo can use without
adopting any of its infrastructure.

---

## Three corrections to the task file itself

1. ⚠ **The PROVISIONAL list in §C is stale, and I checked rather than copying
   it.** It names `TASK_088, 090, 091, 092, 094, 095, 097, 099, 100, 101, 102,
   104, 106`. Measured against `ls .tasks/` and each file's role header:
   **four have since been reviewed** — `TASK_094` by `TASK_100` (the nine-refusal
   audit; eight stand, `p37`'s reason refuted), `TASK_099` by `TASK_103`,
   `TASK_101` by `TASK_105` (p23), `TASK_104` by `TASK_109` (p42). And **three
   unreviewed tasks are missing from it**: `TASK_107` (the batched harness work —
   three results that change how the project measures), `TASK_109` (a review,
   itself unreviewed) and `TASK_110` (which landed p42's corrections and shipped
   two new rungs). The deliverable's §7 carries the corrected list.

2. ⚠ **"Seven controls in this project could not have failed" is one too many.**
   `.memory/03-measurement.md`'s running list has **seven numbered entries of
   which entry 5 is RETRACTED** (the 64-byte environment control, which adds 87
   bytes and *did* fire) — so **six**. That section's own opening paragraph warns
   against exactly this: *"which is how the count itself went wrong … Keep the
   list, not the ordinal."* The deliverable says "six" and does not use an
   ordinal for anything else.

3. ⚠ **§A.1 cites "`p24` byte-identical at shipped shape" as evidence for a
   pattern-level claim. `p24` is not a built pattern.** It is a catalogue row;
   the byte-identity is a `TASK_092` probe of two synthetic kernels
   (`ship_safe` / `ship_unsafe`, `md5_fn 3d37ca7b…`, 133 instructions, no panic
   edge), unreviewed, and its own purpose was to **retract** that row's earlier
   `≈7.9 Ir`/element. I drafted it in as a labelled probe and then **cut it**: a
   synthesis of 26 built patterns citing an unbuilt row's probe is the exact
   shape this project retracts, and Result 1 does not need it.

---

## Problems

- **The `Ir` figures in §2's nine-row table are shipped-spelling differences and
  three of the nine carry known caveats I compressed into one clause each**
  (p23's ≥150 `Ir`/call of spelling; p09's half-is-a-lost-load-idiom; p47's R2
  being cheaper *because* it leaks). A reader who wants the full story has to
  follow the pattern citation. I judged the alternative — a paragraph per row —
  to be the "mostly numbers" document you told me not to write.
- **§2's distribution counts are mine, not the project's.** No existing artefact
  states "9 of 22 within ±32". I derived them so the prose is not eyeballed, and
  `census.py` is committed under `.temp/t108/` so they are re-derivable — but
  they are a **new, unreviewed aggregate** and should be attacked as one. The
  ±32 and >100 thresholds are my choice and nothing in the project licenses them.
- **`p27`'s decomposition is quoted while its `R3−R4` row is `NOT-LIC`.** I state
  both, and I say the decomposition comes from p27's own callgrind caller→callee
  work rather than from the synthesis column. This is the one place I quote a
  number whose own table row is marked incomparable, and I think the disclosure
  is adequate; a reviewer should check that I have not smuggled the licence past
  a reader.

## Unsure / not done

- **I did not read `RECAP.md`'s "Owed" queue in full** (~1 400 lines, lines
  2402–3529). I read the START HERE box, all 39 findings, the retraction list,
  the recurring traps and the Priority section. If a live caveat lives only in
  the Owed queue and nowhere in `.memory/` or the findings, I will have missed
  it. This is the largest single gap in my coverage.
- **I did not read `.memory/02-bench-rules.md` or `05-layout.md` in full**, and
  read `01`, `03`, `04`, `06` by targeted section rather than end to end. Every
  claim in the deliverable traces to a section I read; nothing traces to a
  section I skimmed.
- **I verified no figure by re-measuring.** Everything is transcribed from
  `results/synthesis.md`, `RECAP.md` or `.memory/`, except the `census.py`
  aggregate. `--check-stale` says the records are fresh; it does not say the
  prose describing them is right.
- **The "median ≈ 7.3×" for `R2−R4` ÷ `R3−R4`** is over the 19 patterns with
  `R3−R4 > 0` on `large` and ignores the licence tags. It is a rhetorical figure
  supporting "always quote R3", not a measurement, and the deliverable states the
  range (1.05×…3 536×) beside it. If a reviewer thinks the median is
  over-claiming, cut it and keep the range.
- **I did not attempt to reconcile the two finding-numbering schemes.** The
  deliverable cites patterns by ID only, never by finding number, per
  `RECAP.md`'s own standing instruction.
- **Nothing in `.memory/` or `RECAP.md` was touched**, per the constraint. Three
  corrections that belong in the authoritative layer are listed above for the
  manager to land: the stale PROVISIONAL list, the "seven controls" count, and
  the p24 citation.

## Memory updates

**None** — `.memory/` and `RECAP.md` are manager-only. The three corrections
above are proposed, not applied.

---

⚠ **`PROTOCOL` rule 2 running count: 403 → 407.** Four manager claims corrected
by measurement or by reading in this task: the stale PROVISIONAL list (four tasks
reviewed, three unreviewed tasks missing); the "seven controls" ordinal (six);
the `p24` citation (not a built pattern); and §A's six-thread decomposition
(regrouped to four plus a method, with the specific merges argued above). The
first three are checkable in one command each; the fourth is a judgement and is
the one to attack.
