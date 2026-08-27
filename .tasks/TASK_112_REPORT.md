# TASK_112 — landing TASK_111 into `results/SYNTHESIS.md`: report

**Role: research writer/engineer.** B2 was done first, as instructed. No
`git add`/`git commit`. No `check.py`, `build.py` or `measure.py` except
`--check-stale`. `.memory/` and `RECAP.md` untouched. Scratch in `.temp/t112/`.

---

## Did

| path | what |
|---|---|
| `results/SYNTHESIS.md` | **636 → 975 lines.** B1, B2, M1–M9, m1–m12, and nine restored findings. |
| `synthesis/synthesize.py` | M3 (derive the whole-mode symbol breakdown instead of asserting it) and **four** `SEARCH_REVIEWED` entries, not three. |
| `results/synthesis.md` | regenerated (do not hand-edit). |
| `synthesis/census.py` | **new** — M7. `.temp/t108/census.py` moved out of the gitignore, extended with two arms. |
| `.temp/t112/NOTES.md`, `.temp/t112/m3_control.py`, `.temp/t112/{licence,outward_ir}.json` | notes, the M3 failing-arm control, and the two re-emitted sidecars kept as evidence. |

### B2 first (§1 R4 row + a new paragraph + §2's caveat)

The R4 row now reads *"⚠ **Not "correct, just unverified": at this pin an R4 must
have a byte-identical R5 twin that Verus verifies** — `identity: exact` on 25 of
26 patterns and `norel` on the 26th"*, followed by a paragraph carrying finding
14's load-bearing half: **R4 is bounded by what vstd can express, R3 by nothing,
the classes are incomparable not nested**, the constraint **holds R4 above its
true floor so every `R3 − R4` here reads more favourably to safe Rust than the
pattern warrants**, p11's `r4_cstr` at −17 526 `Ir`/call (−35%) with four
`is not supported`, and p16 running the other way (zero trusted items as R3, five
as R4). §2's caveat is now explicitly **two** caveats: search depth ("nobody
looked hard enough") and the pin ("one side is not allowed to look"), with the
second named as the stronger.

### B1 (§3, a new subsection)

p02's one-byte overflow, in §3 as the measured counterweight, **with its
conditions attached**: seven of eight builds print `198979479034752` and exit 0;
the eighth aborts on the *distro's* `_FORTIFY_SOURCE 3`, which as hardening
catches *1 of 8 builds of 1 of 3 attacks*; the delete-the-check control prints
C's checksum bit-for-bit on well-formed input and exits 101 on the adversarial
one. And the scope the record carries and the review did not quote: **no shipped
Rust rung ever reaches its own bounds check on any p02 input** — R2–R5 all carry
hardened C's three-term rejection test, so the panic belongs to the control, not
the matrix — and a third p02 blob is silently wrong in **eight** of eight C
builds.

### The nine restored findings

| finding | where | note |
|---|---|---|
| **4** | §3 | B1 above |
| **14** | §1, §2 | B2 above |
| **7** | §2 | `143 740 000` exact on `large`, **`large`-only** (`small` is 180 000 000 vs 180 200 000) |
| **32** (price) | §3 | corrected — see "where the record disagrees with the task file" |
| **35** | §2, new sub-head "The three results that are easy to get backwards" | −5 071 / +3 569, `2.25·m − 5647` |
| **34** | §4, new sub-head "What a proof forbids, and it is priced" | `3.00000 Ir`/dispatch, plus p47's `u_win` excluded by the identity level alone |
| **8** | §6 trap 2 | the positive control the trap list had none of |
| **23** | §2 | `next_pow2(CAP) ≤ ARR_LEN`, and `+5 → +479` at `RING_CAP = 60` |
| **21** | §2 | both ends of the copy free of a per-iteration check; p12's `−26.00` is fixed-R4 |

### The nine majors

M1 p09 (the "half" attached to the wrong quantity; the row now says *the checks*
and carries the zero-parameter 48 885.00 = 48 885.00) · M2 (below) · M3
(generator + §7) · M4 p27 (marginal vs kernel-exclusive `+109.98 / +661.82`) ·
M5 (`098` and `100` added to §7) · M6 (p42 marked PROVISIONAL) · M7
(`synthesis/census.py`) · M8 (drop glue and p36's callees, not "library
routines") · M9 (`endbr64`, `1.00000·nrw + 1`, its own §1 paragraph).

### The twelve minors

m1 `8 434` · m2 `+11` with the `+10`'s convention named · m3 `90%` (the
authoritative value; the manager's `1947f6d` moved RECAP) · m4 (below) · m5
(coincidence, not a partition; p18 twice, p16 nowhere) · m6 p23's rank sweep
706.37 → 227.00 · m7 p37 REFUSED-REASON-REFUTED, named inside the hit-rate-zero
argument · m8 p48 added mid-project · m9 the refused headline demoted out of the
bold and *"no C rung was ever built"* stated · m10 the 2.00-vs-3.00 control is
**inside p11** · m11 2× Xeon Gold 6230, 80 logical CPUs · m12 entries cited, with
the struck member named.

---

## Evidence

```
$ wc -l harness/check.py                     8434 harness/check.py
$ python3 -c "...results/p01-array-sum.json"
  c-clang large.bin 143740000   unsafe large.bin 143740000     <- exact
  c-clang small.bin 180000000   unsafe small.bin 180200000     <- NOT exact
$ grep -c '^| p[0-9]' .memory/06-catalogue.md                48
$ awk '/^## Retracted/,/^## Working method/' RECAP.md | grep -c '^- \*\*'   19
$ (catalogue rows whose status says REFUS)  p15 p28 p29 p30 p31 p32 p33 p34
                                            p35 p37 p39 p43 p44 p45 p48   = 15
```

**The census, `python3 synthesis/census.py`** (reads `results/synthesis.md` only):

```
--- ARM A (shipped cells): buckets over the 22 LICENSED rows ---
  within +-32 on both (9/22): p01 p02 p04 p08 p12 p17 p18 p22 p38
  negative on both    (4/22): p10 p13 p18 p46
  > 100 on either     (9/22): p03 p05 p06 p07 p09 p14 p19 p23 p47
  ⚠ NOT a partition: in two buckets ['p18']; in none ['p16']  (sum 9+4+9=22)

--- ARM C (record substitutions applied) ---
  within +-32 on both (7/22): p01 p02 p04 p08 p17 p18 p38
  negative on both    (3/22): p10 p18 p46
  > 100 on either     (10/22): p03 p05 p06 p07 p09 p14 p19 p22 p23 p47
  ⚠ in none ['p12', 'p13', 'p16']
      p10: (-323,-603) -> (-129,-241)      p12: (3,-26)  -> (20,66)   SIGN FLIP
      p13: (-177,-1054) -> (44,77) SIGN    p22: (2,2)    -> (125,1021)  510x
      ⚠ every one of those four moves AGAINST safe Rust.

--- ARM B: R2-R4 over R3-R4 on `large`, LICENSED rows with R3-R4 > 0 (17) ---
  range -1.37x (p47) .. 3536.19x (p08);  median 7.26x (p05, the 9th of 17)
  ⚠ rows where R2 is NOT dearer than R3 (3): p47 p09 p14
--- ARM B with the four substitutions (19 rows) ---
  median 7.26x (p05, the 10th of 19)          <- UNMOVED; p22 falls 1033x -> 2.02x
Over ALL 20 positive rows: median 17.40x
  ⚠ p27 is 1.05x and is NOT-LIC — must not set an endpoint of this range
```

**The regeneration, in the pinned order:**

```
licence.py --emit .temp/t112/licence.json  -> 26 patterns, 104 pair verdicts, EXIT 0
                                              BYTE-IDENTICAL to the committed sidecar
synthesize.py                              -> results/synthesis.md
outward_ir.py --emit .temp/t112/outward_ir.json -> 26 patterns, EXIT 0  ⚠ NOT LANDED
synthesize.py  x3                          -> md5 f5a5ba891804e5af9f0e769f5afc9989
                                              identical on every run (deterministic)
measure.py --check-stale                   -> 52 record(s) examined, 0 STALE, EXIT=0
git diff --stat  results/synthesis.md  40 +++++--   synthesize.py 183 ++++++---
```

**The M3 fix has a demonstrated failing arm** (`.temp/t112/m3_control.py`, EXIT 0):

```
ARM A (real records, must NOT be uniform): 20 rows, 2 symbols ['kernel','kernel.part.0']
     -> the 20 that DID keep a symbol carry 2 DIFFERENT symbols — 16 are
        `kernel.part.0`, 4 are `kernel`                                    PASS
ARM B (p46 rewritten uniform, must be uniform): 20 rows, 1 symbol
     -> all 20 that DID keep a symbol are `kernel.part.0`                  PASS
        the original hard-coded sentence is reproduced exactly, so the
        derivation is not biased toward 'not uniform'
ARM C (a third symbol injected, must count 3): 20 rows, 3 symbols          PASS
```

**Citation lint on `results/SYNTHESIS.md`:** 14 backticked file paths, all
resolve except `spec.md` (a template reference, as TASK_111 clean negative 16
already found) and the two input-blob *names* `small.bin` / `adversarial-cap1.bin`
(both exist under `patterns/p02-buffer-copy/inputs/`). PROTOCOL rule 10's
dangling-report check over `.memory/`, `.tasks/`, `RECAP.md` and the synthesis:
only the `TASK_NNN` placeholders and this report, now written.

---

## ⚠ Where the RECORD disagrees with the task file or the review

The task file told me to read the record and not the reports. Four places where
that changed what shipped.

1. ⚠⚠ **M2 is right about p22 and its arithmetic does not stop there. I did not
   ship `8 / 4 / 10`.** Substituting p22's searched R4 while leaving p13's and
   p12's shipped is a *selective* correction, and p13's known move is a **sign
   flip** — larger in kind than p22's bucket change. Four of the 22 licensed rows
   have a measured, verifying, in-contract cheaper R4 in `.memory/`, and applying
   all four gives **`7 / 3 / 10` with p12 and p13 joining p16 in no bucket**.
   So the document now prints the **shipped-cell** buckets (`9 / 4 / 9`, which is
   what the generated table and the census derive and what the header's word
   *"shipped"* actually means) and immediately beneath them a four-row table of
   the searched counterparts, the resulting `7 / 3 / 10`, and the note that
   **every one of the four moves against safe Rust while the two known R3-side
   levers (p17, p06) move the other way** — because R3 levers cost zero trusted
   items and R4 levers must clear the prover. That asymmetry is finding 14's
   shape and it is the reason the errors run one way; `8 / 4 / 10` would have
   stated the correction and hidden the mechanism.
2. ⚠ **The task file's *"every fix saves exactly `6.00 Ir`/call"* (finding 32) is
   a rounding of the record.** `patterns/p38-alias-pun/NOTES.md:962-974`: **six**
   defined spellings are cheaper, **five by exactly 6.00 and one (`c_noback`) by
   2.00**; on clang `c_once` is 8.00 cheaper, `c_noback` 7.00 and the other four
   are byte-identical. And the record's own next clause is the one that must ride
   along: **the only defined spelling that costs *more* is `c_halves`, `+12.00`
   gcc / `+32.00` clang — the two-half read the Rust rungs are forced into.** The
   restored paragraph carries all of it.
3. ⚠ **`p06` is not a plain "reviewed" `SEARCH_REVIEWED` entry, and the review's
   adjacent-work item said it was.** `.memory/01-ladder.md:1914` marks the whole
   `c_idx` bullet **`⊘` — "landed at TASK_048 and has not been through a second
   review"**. And `0.00000 Ir/byte, 105 flat` is a **band-M sweep** figure: on the
   shipped blobs `c_idx − R4` is `+80.00 / +187.00` against a shipped
   `+334 / +172`, so **on `large` the shipped R3 is the cheaper of the two**. The
   entry ships with both facts in it, tagged `⊘ PROVISIONAL`, rather than being
   omitted or silently promoted.
4. ⚠ **p22's `+2.00` is *not* on RECAP's "Retracted — do not reinstate" list**,
   which M2's headline says it is. It is in RECAP finding 33, RECAP's standing
   trap box and `.memory/01-ladder.md` finding 22; **p17's `+32 flat` is the one
   that is actually on the list.** The substance of M2 is untouched — the
   document was quoting a figure its own §6 corrects by 510× — but the generator
   note says which record carries which, because that distinction decides whether
   the shipped cell may still be published (it may: `.memory/02-bench-rules.md`,
   never re-ship a rung because a cheaper spelling was found).

**One further correction, to a figure I declined to print.** RECAP finding 7 says
p01's static gap is `+2`. `results/p01-array-sum.json` gives `n_fn 37 / 35` for
`c-clang` and `36 / 34` for `unsafe` — **`+1` by either measure, padded or not.**
The restored paragraph quotes only the exact `Ir` equality, which does reproduce.
`RECAP.md` finding 7's static half is for the manager to check; I did not touch
`.memory/` or `RECAP.md`.

**And a fourth missing `SEARCH_REVIEWED` entry the review did not name.** `p12`
printed `undeclared` although `TASK_040_REVIEW` **built** the cheaper R4 (route A:
`15/0`, twin `18/0`, `R4 ≡ R5 exact`, 17.00 / 92.00 cheaper) and
`.memory/01-ladder.md:1629-1636` records it. So the column understated the record
by **four**, not three, and the *"18 of 26 print `undeclared`, only five report a
real search"* sentence is now **14 of 26** and **nine**.

---

## The three calls you named

### 1. Did restoring coverage become advocacy?

**No, and the guard was making every restoration carry the condition that
weakens it.** Each of the nine ships with the clause a hostile reader would
reach for first, taken from the record and not from a report:

- p02's seven-of-eight is *one of three* adversarial blobs (a second is silent in
  **eight** of eight), the eighth build's abort is a **distro default** catching
  1-of-8-of-1-of-3, and the panic belongs to a control because **no shipped Rust
  rung reaches its own check on any p02 input**.
- p01's `143 740 000` is **`large`-only** and is a statement about *one backend*;
  `c-gcc` on the same row is 205 180 000 and carries an `endbr64` term.
- p38's price paragraph ends on `c_halves`, the spelling that is **dearer** and
  is the one the Rust rungs are forced into.
- p46's "safe beats unsafe" keeps its PROVISIONAL marker and its "relax either
  pin and it inverts".
- p12's and p22's restored mechanisms both say **none of it is a bounds check**,
  and p12's ends on the sign flip that runs against it.
- B2 itself ends *"This is not a claim that safe Rust is cheaper; it is a
  statement that the comparison is not a language fact in either direction."*

**Two places where I checked myself specifically.** §3's new closing tally
("seven entries where the safe rungs buy nothing, one where they buy the whole
bug, two with no cost axis") is followed immediately by *"that ratio is a
property of which patterns were built … it is not a score. Read the entries, not
the tally"* — a tally is exactly where advocacy would hide. And §3's ledger
subsection is headed *"and one of the three is measured"*, which is the count of
measured counterweights, not a rhetorical claim.

**The one thing I did add that is not a restoration** is §7's disclosure of the
coverage bias itself, and §0's pointer to it. That is deflationary about *this
document*, which is the only direction the document is allowed to flatter.

### 2. Were §3's six judgement calls worth restoring?

**Four yes, two no.**

| finding | verdict | why |
|---|---|---|
| **8** (p02 sawtooth) | **restored**, §6 trap 2 | It is the only model here tested by *prediction* — re-derived at seven unsampled lengths and 8× the scale. A trap list with no worked success is a list of reasons not to measure; this is the arm that fires. It also lands next to the traps it satisfies, not as a separate claim. |
| **23** (p04 `next_pow2`) | **restored**, §2 | The document quoted nine flat rows and gave mechanisms for three. p04's is zero-parameter, reproduces on capacities p04 never built, and **has a dial**: `RING_CAP = 60` takes the same row `+5 → +479`. A "flat" row that can be made 96× larger by an operator choice is not evidence that safety is cheap, and that is the honest use of it. |
| **21** (p12) | **restored**, §2 | p12 appeared once, in a list. Its rule is transferable (*both* ends of the copy free of a per-iteration check — checking only the source kills the lowering too), and restoring it is what surfaced the fourth missing `SEARCH_REVIEWED` entry. |
| **17** (p11) | **restored**, folded into B2 | Its headline *is* B2's measured instance; a second telling would be advocacy by repetition. |
| **5** (static counts are not a cost model) | **declined** | `results/synthesis.md` §4 already opens *"A static count is not a cost model"* in bold, at the point of use, with the pilot's 32-instructions-125 019-`Ir` counterexample. `SYNTHESIS.md` quotes **no** static figure — I removed the one candidate (p01's disputed `+2`). Restoring it here would be advice guarding a misuse this document does not enable, and the guard is already where the reader meets the table. |
| **22** (decode the panic pad's `Location`) | **declined** | It is a *technique*, and **nothing in `SYNTHESIS.md` counts pads** — there is no claim for it to qualify. Its lesson ("counting pads says how many survived, never which") is already carried in substance by §6 trap 5's *"a pinned entry with no backticks pins nothing"* and by §2's p06 row, which cites the identical-pads result without needing the tool. Adding it would be the fourth paragraph of methodology in a section that is supposed to be evidence. |

⚠ **The two I declined are the two with no figure in this document to attach to.**
That was the test I used, and I would apply it again: a restored item earns its
place if some sentence already in the document is wrong or unqualified without
it.

### 3. Should it stay one file?

**No — but not yet, and not by cutting.** It is now **975 lines**, and the shape
is lopsided: §2 alone is **311 lines**, a third of the document, while §5 is 60
and §7 is 87.

The honest split is **argument + evidence appendix**, and the seam is already
visible in the section numbering:

- **the argument** — §0, §1, §5, §6, §7 (≈ 330 lines). This is the half that
  transfers: the apparatus and its two caveats, what the instrument can and
  cannot price, the eight traps, and what the project does not know. A benchmark
  author outside this repo needs exactly this and none of §2.
- **the evidence** — §2, §3, §4 (≈ 610 lines). Per-pattern, cited, and read by
  someone checking a specific claim.

⚠⚠ **Three conditions on doing it, and the third is the one this task exists
because of.** (1) The four results must stay stated in the argument half, with
the evidence half as citation — otherwise the split re-creates the compression.
(2) §1's R4 constraint and §2's caveat must appear in the *argument* half, since
B2 exists because a reader quoting a figure never reached them. (3) ⚠ **A split
is a compression, and TASK_111's finding is that compression is exactly where the
coverage bias entered this document — nine reviewed results, five of them in one
direction, with no arithmetic signature at all.** So a split must be a **pure
move**: `diff` the concatenation against the original and require it to be empty
of deletions. **I did not split it**, because a 339-line restoration and a
structural change in one pass would make that diff unreadable, and because the
split is the kind of change that should be reviewed as its own artefact.

**In the meantime the cheap mitigation is in.** The document's masthead now names
its own revision history, §0 points at §7's disclosure, and §7 lists the nine
dropped results by name — so a reader who quotes the short version can at least
find out what the short version left out.

---

## Problems

- **`synthesis/outward_ir.py --emit` produced a different sidecar and I did not
  land it.** 4 of 26 patterns differ (p03, p04, p08, p46) and **every** differing
  leaf is a documented environment-phase term: p03/p04 `safe_tuned` and `verus`
  outward move `43.0 ↔ 50.0` (glibc `memset`'s alignment-dependent tail, the `‡`
  bistable term swept over a full 32-pad period at TASK_098), taking
  `p03 /large.bin/pairs/R3-R4/moves_by` from `−7.0` to `0.0`; p08's and p46's are
  the one-off IFUNC/lazy-binding resolver term (`259.3769594 → 259.3764594`) and
  p46's documented ±7.00 on `c-clang-h`. The committed sidecar's own pin prints
  **FRESH** on every `synthesize.py` run, nothing in this task touches what it
  calibrates, and landing a different draw would silently move the calibration
  figures §2 prints (hit / miss / false-alarm counts, residual median, the
  "Misses:" list) **with no measurement behind the change**. *Quote the support,
  never the draw* — the file's own rule. Kept as evidence at
  `.temp/t112/outward_ir.json`; the emit command is in
  `.temp/t112/NOTES.md`. ⚠ **If the manager wants the sidecar refreshed, it
  should be its own task with the phase stated, not a side effect of a prose
  edit.**
- `licence.py --emit` needs a PATH argument; the task file's `licence.py --emit`
  exits 2 with a usage error. I emitted to `.temp/t112/licence.json`, diffed it
  against the committed sidecar (**byte-identical, 26 patterns, 104 verdicts**),
  and copied it over — `git status` on `synthesis/licence.json` is empty.

## Unsure / not done

- **I did not re-measure anything.** Every restored figure is a read of
  `results/*.json`, `results/gate/*.json`, `results/synthesis.md`, `.memory/` or a
  pattern's `NOTES.md`, and where two sources disagreed I said which I took and
  why (p01's static gap, p13's 90%, p38's 6.00-vs-2.00, p06's 105-vs-80/187).
- **The `7 / 3 / 10` divergence from the task file's `8 / 4 / 10` is a
  judgement**, not a measurement dispute: the arithmetic of both is in
  `synthesis/census.py` arms A and C and reproduces. If the manager prefers the
  narrower correction, the change is one table and two sentences — but I think
  the four-row version is the one that survives a hostile read, and it is
  strictly more deflationary.
- **I did not check `results/tables/*.md`** (26 files) against the document;
  `SYNTHESIS.md` still does not cite them. Same gap TASK_111 disclosed.
- **I did not read `RECAP.md`'s "Owed" queue (2427–3529) in full.** Third
  consecutive task to inherit that gap. If a live caveat lives only there, it is
  still missing.
- **`.memory/` and `RECAP.md` are untouched**, per the task. Two things are owed
  there and are the manager's: RECAP finding 7's static `+2` (the record says
  `+1`), and `.memory/01-ladder.md`'s p06 `⊘` block, which now has a downstream
  consumer in `SEARCH_REVIEWED` and should say so if the ⊘ is ever cleared.
- **I did not split the file** (call 3), for the reasons above.
- **Nothing measurement-hashed was touched and no gate stage changed**;
  `measure.py --check-stale` is `52 record(s) examined, 0 STALE`.

## Memory updates

**None** — `.memory/` and `RECAP.md` are manager-only for this task. Durable
facts that belong there are listed under "Unsure / not done"; the transferable
ones are written into `synthesis/synthesize.py`'s `SEARCH_REVIEWED` header
comment and `synthesis/census.py`'s docstring, where the next agent editing
those files will meet them.

---

⚠ **`PROTOCOL` rule 2 running count: 409 → 414.** Five things contradicted what I
was told or what the record was said to say, each checked against the committed
record: **(1)** the task file's *"every fix saves exactly 6.00 `Ir`/call"* is
five-at-6.00-and-one-at-2.00, and the record's next clause names a *dearer*
defined spelling that the Rust rungs are forced into; **(2)** `p06` is marked `⊘`
unreviewed in the authoritative layer and its `105 flat` is a band-M figure whose
shipped-blob counterpart makes the **shipped** R3 cheaper on `large`; **(3)**
p22's `+2.00` is **not** on RECAP's do-not-reinstate list (p17's `+32` is);
**(4)** RECAP finding 7's p01 static gap of `+2` does not reproduce — the record
says `+1` padded or unpadded — so I quoted only the exact `Ir` equality; and
**(5)** a **fourth** pattern, `p12`, was missing from `SEARCH_REVIEWED` with a
reviewed R4 search that flips its sign, which the review named three of.
⚠ **And one instruction I declined:** applying the record to p22's bucket alone
gives `8 / 4 / 10`, but three other licensed rows have the same kind of
counterpart and two of them flip sign; the document prints the shipped buckets
with all four movers beside them and `7 / 3 / 10`. **B2 landed first and the
document is quotable again**, with the caveat a hostile reader finds first now on
the same page as the ladder table.
