# ph07-strcut-cursor — notes

`spec.md` is the contract, `README.md` is the entry point, this file is the
evidence. Everything here was run; the logs are named per claim.

---

## §00 ⚠⚠⚠ READ THIS FIRST — `TASK_PHP_018` REBUILT THE ROW, AND EVERY NUMBER MOVED

**R1h changed, the corpus changed, and therefore every measured figure in this
file was re-derived.** What follows is what changed, why, and which sections of
this file are superseded. Nothing below §00 has been silently updated: where a
figure moved, the old one is quoted beside it.

### What R1h was, and what it is

| | |
|---|---|
| **was** | `cb3cca21b345` **entire** — both hunks — the 2005 security commit, cited as the `fix_commit` |
| **is** | the guard configuration **upstream converged on**: `php-5.2.12 … php-5.2.17`, `PHP_FUNCTION(mb_strcut)` body sha256 `26e2099e33433c74`, which is that commit's hunk **(a)** and nothing else |

**Why.** `c2471b495009` (Moriyoshi Koizumi, 2009-09-23) **removed hunk (b)** as
**bug #49354** — *"mb_strcut() cuts wrong length when offset is within a
multibyte character"* — and shipped `ext/mbstring/tests/bug49354.phpt` with it.
⭐ The removal was committed **three times in the same second**
(`c2471b495009`, `0c974164e248`, `ce3c028803aa`), one per live branch, so it is
not one branch's local decision. `controls/c2471b495009.patch` has the bytes.

### ⭐⭐ AND THE ROW'S OWN GATE HAD ALREADY SAID SO, IN THE FIRST HOUR IT EXISTED

`check.py` **stage 7h** requires R1h to be byte-identical to R1 on every
non-adversarial input. Hunk (b) is not: it changes the answer on **15 870 of
117 612** benign calls (13.5 %) while removing **none** of the 15 333
out-of-bounds reads (`controls/fix_scope.py` Q1/Q2 — those two numbers are
unchanged and re-run at `TASK_PHP_018`). The row read that refusal as a
**harness limitation** and worked around it by restricting `inputs/gen.py` so
the guard could never fire.

⚠⚠⚠ **The refusal was correct.** The gate detected the same defect PHP's own
maintainers detected four years later, from a bug report. **The workaround was
the defect, and it lived in the fixture rather than in any rung, which is why
row-level review did not see it for two tasks.**

`controls/bug49354.py` is the decisive control and it is upstream's own test:

```
call                      --EXPECT--                R1                      R1h_ab                  R1h
mb_strcut($crap,2,100)    string(11) "åBäCöDü"      string(11) "åBäCöDü"    string(9) "åBäCöD" ✗    string(11) "åBäCöDü"
mb_strcut($crap,13,100)   bool(false)               <<OOB READ>> ✗          bool(false)             bool(false)

R1     : 1 of 6 wrong  -- the over-read, CRASH-124
R1h_ab : 1 of 6 wrong  -- bug #49354, and it is a DIFFERENT row of the table
R1h    : AGREES with upstream on all 6
```

⭐ **Case 3 and case 6 are two different defects in two different
configurations, and hunk (a) alone fixes one while leaving the other correct.**
That is the whole argument for this row's R1h, in six lines of upstream's own
regression test.

### What moved, mechanically

1. `c/kernel_hardened.c` — hunk (b) deleted.
2. **All four Rust rungs, and `verus.rs`'s SPEC as well as its exec code.** F41
   says R2–R5 are ports of R1h, and they were: every one of them carried
   `frm.saturating_add(length) > slen { slen - frm }`, and `strcut_fold` — the
   *postcondition* — carried `if f0 + l0 > slen { slen - f0 } else { l0 }`.
   ⭐ **That is the strongest argument this row has for a VALUE postcondition
   over a memory-safety-only one**: when R1h changed function, the `ensures`
   had to change with it. A safety-only `ensures` would have stayed green.
3. `model.py` — all **three** implementations (`_window`, `strcut_fold`,
   `_dumb`), plus `selfcheck` check 2, which is **reversed**: it used to refuse
   a corpus containing `from + length > string->len` and now refuses one
   without it.
4. `inputs/gen.py` — the restriction is gone and its inverse is asserted. See
   §00a.
5. `spec.md` — `idiom.required[4]`, a new `forbidden[3]`, `provenance`'s two
   new `extra_spans`, `fix_commit_removal`, `r1h_configuration`. **`contract_sha256`
   moved; §0 records it.**
6. `controls/` — `c2471b495009.patch` and `bug49354.py` added, `fix_scope.py`
   relabelled (`R1h` now means the shipped configuration and `R1h_ab` the
   withdrawn one — ⚠ the labels **swapped meaning**, so `.temp/php16/` and
   `.temp/php17/` logs read the other way round), `guard_equiv.{c,py}` extended
   to compare both configurations, `negatives.py`'s `noguard` anchor updated,
   and `spellings.py` added (§12).

### §00a The corpus — the restriction is gone and its INVERSE is asserted

`inputs/gen.py::_check_span` used to refuse a window on which *either* guard
fires. It now refuses one on which **hunk (a)** fires — that is the
**adversarial** case, and keeping it out is what "benign" means here — and
**requires** windows with `from + length > string->len`, with a second, sharper
assertion that some of them are windows where hunk (b) **would have changed the
answer**.

```
span ok: small.bin   windows=32    steps=[1,2,3,4,5,6] k>=len=10  k<len=22
                     start==from=14 start<from=18 from==len=3
                     hunk(a)-fires=0 from+len>len=6   hunk(b)-would-move=4
span ok: large.bin   windows=2050  steps=[1,2,3,4,5,6] k>=len=662 k<len=1388
                     start==from=885 start<from=1165 from==len=205
                     hunk(a)-fires=0 from+len>len=410 hunk(b)-would-move=297
```

- **20.0 %** of windows are in the newly admitted region; **14.5 %** are windows
  where hunk (b) would have moved the answer. ⭐ Against `fix_scope.py` Q2's
  independent **13.5 %** over a uniform sweep — which is the cross-check that
  the fixture is neither over- nor under-weighting the region it re-admitted.
- ⚠ **Measured before deleting it**: over the eight shipped `FRACTIONS` entries
  the `min(..., slen - frm)` clamp in `window()` **never once fired** — clamped
  and unclamped produced byte-identical corpora (`.temp/php18/fractions.log`).
  The restriction was carried by the `FRACTIONS` table alone. The dead clamp was
  deleted anyway, because a clamp that would silently re-impose the old domain
  the moment somebody added a fraction pair is the failure mode this task exists
  to remove.
- ⚠ **The two new assertions have must-fire controls**
  (`.temp/php18/gen-negatives.log`, five cases, all as declared): the
  pre-`TASK_PHP_018` table is REFUSED on `from+len>len`; a table with over-sum
  windows that can never move the answer is REFUSED on the sharper one; a
  hand-edited byte setting `from = slen + 1` is REFUSED on hunk (a); the shipped
  table PASSES; and `_cut` is shown separating the two configurations on
  `bug49354.phpt`'s own case 3.
- ⚠ `_check_residues()` did **not** depend on the restriction and is unchanged.
  It is the only other `_check_*` in the file.
- ⚠ The hunk-(a) branch of `_check_span` cannot be reached through `FRACTIONS`:
  `window()`'s own `assert 0 <= frm <= slen` refuses `ff > 1.00` first. That is
  defence in depth and the right layering; the control exercises it on bytes.

---

## §0 `PROTOCOL.md` rule 6 — the `contract_sha256` disclosure

```
13bb0b70d031be7354077ee852e80f3dced307729fee71eb5b418e43816176a0   AS FIRST WRITTEN
```

Recorded **before any cell was built through `harness/build.py`**, which is the
only evidence rule 6 can have on a row that lands in one commit. ⚠ Rule 6's
`git show HEAD:` command is **vacuous on a new pattern** — it compares the
working tree to HEAD and prints nothing on a clean tree — and this line says so
rather than citing a check that cannot fire.

⚠ **Two things happened before that hash and neither is hidden.** (1) An
earlier draft of the contract hashed to `09b46bfecaab118d0ade88f876f8f2c1…`; it
pinned `` `n > frm` `` as the Rust spelling of the start walk's exit test, which
**appears in no Rust rung** because the rungs use the rotated `while n <= frm`
form. Caught by grepping the pins against the sources before the first gate
run, corrected to `` `while n <= frm` ``, and the row was never built or gated
at the old hash. (2) The cells under `.temp/php16/tb/` were built by hand with
`gcc`/`rustc` during development, outside `harness/build.py`; they measure
nothing and are deleted.

**The hash MOVED ONCE, after the measurement and before the first gate run:**

```
be5f5818ffa625c72af87eea036735219de01b8d61e05ce3b8271805d241359c   AS SHIPPED
```

⚠ **One edit inside the fence, and it is the `identity` entry.** `spec.md`
cannot pin `identity.O3` before the measurement exists — the honest level is
`norel`, not `exact`, and I could not know that until the record showed
`md5_fn` differing while `md5_fn_norel` and both instruction counts matched.
The `why` is written from the record, and `spec.md` is **not** in
`measure.py::measurement_sources`, so no re-measure was owed and none was
taken.

**IT MOVED A SECOND TIME AT `TASK_PHP_018`, AND THAT MOVE IS A REBUILD:**

```
be5f5818ffa625c72af87eea036735219de01b8d61e05ce3b8271805d241359c   BEFORE
1f1508531bd41975927e07f0bca9d592a65a9b6f0620ce4d8a2ca7b3d0e00c0c   AFTER
```

Both taken with `check.py::read_contract`'s exact regex — the capture keeps the
newline before the closing fence — and the second one is what
`results-php/gate/ph07-strcut-cursor.json` carries, so the disclosure is
checkable against the record rather than against a re-derivation.

⚠⚠ **THE `TASK_PHP_018` DISCLOSURE HERE SAID *"Four edits inside the fence"* AND
THAT IS AN UNDERCOUNT BY A FACTOR OF NEARLY SEVEN** (`TASK_PHP_022` m3; re-derived at
`TASK_PHP_024` §1.3 with `.temp/php24/fencediff.py`, which parses both fences and
diffs them leaf by leaf). **Measured, `8214b5f` → `8e2d834`: 27 leaf values
changed — 6 moved and 21 added — across 10 second-level keys**, 191 leaves before
and 212 after:

```
MOVED   .idiom.required[4]          .provenance.divergences[6].why
        .idiom.why                  .provenance.divergences[8].why
        .provenance.fix_commit_note .verus.twin_obligations_note
ADDED   .idiom.forbidden[3].{c,rust}
        .provenance.extra_spans[0].{c_file,c_lines[0],c_lines[1],extract_cmd,
                                    extract_sha256,why}
        .provenance.extra_spans[1].{ same six }
        .provenance.extra_spans_note   .provenance.fix_commit_removal
        .provenance.r1h_configuration.{body_bytes,body_sha256_16,function,
                                       respelled_as,tags}
```

The four the disclosure named are all real and all forced by §00: `idiom.required[4]`
(R1h is now a tagged configuration, and the entry states the alternative it was
chosen against), a new `idiom.forbidden[3]` (hunk (b)'s two spellings, pinned
ABSENT), `provenance.extra_spans` (§1), and
`provenance.fix_commit_removal` / `r1h_configuration`. ⚠ **None of the six it
missed is a defect in itself** — `.verus.twin_obligations_note` had to move for
the rlimit finding and `.idiom.why` for §00 — **but rule 6 exists so a reviewer
can check the SCOPE of a declaration edit against a statement of it, and a
statement narrower than the edit removes the check it was written to enable.**
⚠ The reviewer's *"10 top-level keys"* is the same 10 counted one level down;
there are **three** top-level keys (`idiom`, `provenance`, `verus`).
⚠ A re-gate AND a
re-measure were owed and both were taken — `spec.md` is not in
`measure.py::measurement_sources`, but `c/kernel_hardened.c`, the four `.rs`
rungs and every `.bin` are.

**IT MOVED A THIRD TIME AT `TASK_PHP_024`, AND THAT MOVE IS A CORRECTION, NOT A
REBUILD:**

```
1f1508531bd41975927e07f0bca9d592a65a9b6f0620ce4d8a2ca7b3d0e00c0c   BEFORE
a70c115a9fa05520c64f334fcd8903c8da06140aefc47c1b31d0c209fcd4b1a1   AFTER
```

⚠ **One edit inside the fence: `identity[0].why`, and nothing else.** Verified
leaf-by-leaf with the same `fencediff.py` — `8e2d834 → WORKTREE` reports
**1 changed leaf, 0 added, 0 removed**, and that leaf is `.identity[0].why`.
It carried **nine** figures the `TASK_PHP_018` rebuild had refuted; they are
re-derived from the current record in §0a below. **No `required`, `forbidden`,
`identity` level, `provenance` field or `verus` entry moved**, so nothing about
what the row is obliged to changed — only what it says it measured.

⚠⚠ **AND ONE SCHEMA FACT, MEASURED THE HARD WAY**: `check.py` stage 0
hard-fails on ANY key inside `idiom` other than `required`, `forbidden` and
`why` — *"a mistyped key is silently empty"*. A first draft carried a
`forbidden_note` sibling and the gate refused it; the note is inside the entry,
which is where the named-spelling standard says an entry's English belongs.
⚠⚠ **And every backtick inside a `forbidden` entry is a PINNED SPELLING that
hard-fails if any rung contains it.** The same draft wrote `` `length` `` in
that entry's prose — a token every rung contains. Caught before the gate ran,
by extracting the tokens the way `check.py` does; the prose is now backtick-free
except for the one spelling the entry exists to pin.

⚠ **Any later move is disclosed here with its reason**, per rule 6.

⚠⚠⚠ **THE RULE-6-ADDENDUM SENTENCE THAT USED TO STAND HERE WAS A FALSE
DISCLOSURE, AND A FALSE DISCLOSURE IS WORSE THAN THE STALE THING IT DESCRIBES,
BECAUSE IT IS WHAT A REVIEWER TRUSTS *INSTEAD OF* RE-CHECKING.** It read:

> ~~Also per rule 6's addendum: the hashed `idiom.why` and every rung-source doc
> comment were re-read against the measured numbers in §8 before this row was
> finished, not only against what they said when written.~~

**`idiom.why` was** — it carries no stale ladder figure, checked twice.
**Two things it names were not** (`TASK_PHP_022` M1/M2):

- **`identity[0].why` is also hashed and also carries measured numbers**, and
  nine of its eleven were pre-rebuild values. §0a.
- **`c/kernel.h:20-25` is a rung-source doc comment** — it is in the measurement
  record's `source_sha256` — and it named the **wrong upstream commit** as R1h,
  from the day the row was built. §4b-bis.
- **And so did `safe_naive.rs:7-17`**, which `TASK_PHP_022` did not find because
  it looked at `c/`. Same error, second measured source, and it contradicted its
  own ladder table four lines below. §4b-bis.

⚠ **The sentence was narrower than the rule and did not say so.** What is true,
as of `TASK_PHP_024`: `idiom.why`, `identity[0].why` and every doc comment in
`c/kernel.h`, `c/kernel.c`, `c/kernel_hardened.c`, `c/main.c` and the four `.rs`
rungs have been read against `results-php/ph07-strcut-cursor.json` as it stands
after this task's re-measure. **The two that were wrong are corrected in place
and the correction is disclosed above rather than made quietly.**

### §0a The nine refuted figures in `identity[0].why`, re-derived

⚠⚠ **The `contract_sha256` MATCHED THROUGHOUT. That is the point.** The entry
was written from the pre-rebuild record and never edited, so `PROTOCOL.md`
rule 6's evidence — *"no `required`/`forbidden`/`identity`/`why` moved after I
measured"* — was **true and useless**: it certifies *when* a declaration was
written, not whether it is still true (p46's hole, PAT `TASK_089_REVIEW`,
reproduced here on the first php row to be rebuilt).

`.temp/php24/identity_rederive.py` reads the record and prints every cell beside
every claim; run it with `--record` against `git show 8214b5f:` for the left
column.

| claim in the hashed `why` | pre-rebuild (`8214b5f`) | current record | |
|---|---:|---:|---|
| O3/iso instructions, both cells | 255 | **251** | moved |
| O3/iso bytes, both cells | 953 | 953 | survives |
| O3/iso `md5_fn_norel`, identical | `702235d5f057…` | **`cc8d629987e1196f…`** | moved |
| O3/iso `md5_fn` `unsafe` | `b20b2fd9aa42e532` | **`909a1a4db15d5bb8`** | moved |
| O3/iso `md5_fn` `verus` | `b3ecc80e00209841` | **`f6fec880e0ec2b0f`** | moved |
| O0/iso instructions | 442 vs 464 | **427 vs 449** | moved ×2 |
| O0/iso bytes | 2530 vs 2683 | **2432 vs 2585** | moved ×2 |
| O3/`whole` instructions | 875 vs 888 | 875 vs **883** | moved ×1 |

**All eleven numerals reproduce EXACTLY against the pre-rebuild record**, which
is what identifies the entry as a snapshot rather than a set of typos.

⭐ **Every QUALITATIVE claim in the entry survived, and that is why nothing
caught it**: at O3/isolated the two cells still have equal instruction counts
and equal `fn_bytes`, `md5_fn_norel` is still identical and `md5_fn` still
differs, so **`norel` was the right level before and after and no gate verdict
ever moved**. ⚠ **A declaration can be wrong in every number and right in every
verdict** — which is exactly the configuration no check in this project can see.

⚠ `TASK_PHP_022` M1 found **four** of the nine. The other five (the O0
instruction pair, the O0 byte pair, and the `whole` 888) came out of re-deriving
**every cell the entry names** rather than the first sentence. The cheap
generalisation, and it is the answer to the question the task asked: **re-derive
the whole declaration, not the figures a reader's eye lands on.**

---

## §1 The row

**`mbfl_strcut`'s `mblen_table` arm, `mbfilter.c:1179-1259`, narrowed.** The
extraction is line-for-line identical to the tarball except for what
`spec.md`'s `provenance.divergences` itemises: the encoding lookup, the two
WCS arms, the filter-chain `else` arm, two struct fields, the allocator
substitution, and the Rust rungs' `usize` spelling of the caller's clamps.

⚠⚠⚠ **THE ROW LIFTS THREE SPANS AND PINNED ONE UNTIL `TASK_PHP_018`**
(`TASK_PHP_017` M1, `RECAP_PHP.md` open item 25). `provenance.c_lines` named the
walk; the row also lifts the step table (disclosed as `divergences[6]`, pinned
nowhere) and **`mbstring.c:1774-1812`, the caller frame, which was disclosed
nowhere at all — and which is exactly the frame R1h occupies.** So the overlap
number this row published certified a span containing **neither the fix nor the
frame the fix goes in**. Closed by `provenance.extra_spans`, an ADDITIVE schema
key in `harness-php/provenance.py`: the primary four fields do not move, so
`ph03` and `ph00-smoke` are byte-identical and owe nothing.

`harness-php/provenance.py ph07-strcut-cursor`:

```
mbfilter.c, mbfilter_utf8.c, mbstring.c are in the manifest
OK   ext/mbstring/libmbfl/mbfl/mbfilter.c:1179-1259          1489 B  5edc6c04b7ff5f64  tier=narrowed
OK+1 ext/mbstring/libmbfl/filters/mbfilter_utf8.c:39-56       852 B  716ba3fb219d4fb4  -- the step table
OK+2 ext/mbstring/mbstring.c:1774-1812                        845 B  4ef738b3546c31c1  -- the caller frame, where R1h lives
per-span overlap: span0 75% (39/52), span1 100% (5/5), span2 15% (3/20)
kernel overlap 61% (46/76 excerpt lines in kernel.c, kernel.h, kernel_hardened.c)
    tier=narrowed is expected to clear 25% -- REPORTED, NOT ENFORCED
1 preprocessor condition this heuristic cannot evaluate: ['#ifndef PH07_KERNEL_H']
1 row(s) checked, 0 FAILED
```

### §1a ⚠ `PROTOCOL_PHP.md` §F item 9 asks what I think of that number

⚠⚠ **THE HEADLINE FELL FROM 75 % TO 61 % AND THAT IS THE POINT.** The
denominator went from 52 lines to 76 because the row now cites what it lifts.
**The interesting number is not 61 % — it is `span2` at 15 % (3/20).**

**Why the caller frame scores 15 %, and it is not a fidelity problem.** The
kernel's wrapper *is* `PHP_FUNCTION(mb_strcut)` semantically —
`TASK_PHP_017` §3 verified that by function diff — but almost none of it is the
same TEXT. Where PHP writes `zend_parse_parameters`, `Z_STRVAL_PP(arg1)` and
`RETVAL_STRINGL`, the benchmark writes a little-endian unpack out of the window,
`str_len`, and a Horner fold. The three lines that DO match are the two negative
clamps and the call. ⭐ **So the overlap heuristic measures exactly what its own
warning says it measures — TEXT IN A FILE, not code in the benchmark — and on
this span it is measuring a re-expression rather than a lift.** A reader should
take `span2`'s 15 % as *"the caller frame is `modelled`, inside a `narrowed`
row"*, and the row should be read as citing three spans at three different
fidelities. **The load-bearing artefact is still the divergence ledger, and
nothing checks it.**

**`span0` is unchanged at 75 %, and the 13 missing lines are exactly the
declared ones**: the `mbfl_no2encoding` call and its NULL test, the twelve lines
of the two WCS arms, and the `} else if (encoding->mblen_table != NULL) {` line
itself. Nothing is missing that I did not itemise. **`span1`, the step table, is
100 % (5/5)** — it is lifted byte-for-byte, and that is what a real `verbatim`
lift scores.

⚠ **And the number is not evidence that the cited lines are compiled.**
`provenance.py` reads `c/kernel*.{c,h}` and never `main.c`, the driver loop or
the build; it says so itself on every run. **What ties the cited lines to the
benchmark on this row is the ASan backtrace** (§4b): `ph07_strcut` appears at
`kernel.c:171` with `kernel` above it and `main.c:59` above that. That is the
evidence a reviewer should want; the overlap is a spelling check.

⚠ **The first `narrowed` row is where `TASK_PHP_008` §2's demotion stops being
free**, exactly as `PROTOCOL_PHP.md` §F item 9 predicted for the first
`verbatim` one. My reading: for a `narrowed` row the number is *less*
informative than for a `verbatim` one, because narrowing is defined as removing
lines — so a low score is expected and a high one only says the removals were
small. **The load-bearing artefact is the divergence ledger, and nothing checks
it.**

---

## §2 Reachability — `PROTOCOL_PHP.md` §A3, settled before any rung existed

`.temp/php16/02-reach.log`, an **offset** interpreter of the extracted walk (it
never holds a pointer, so it records an access it does not perform), over
133 932 `(string, from, length)` calls spanning six lead-byte families ×
`slen ∈ {0,1,2,3,5,8,13,21,34,48}` × every `from`/`length` in
`[-slen-2, slen+8]`:

```
calls interpreted                          : 133932
  of which the wrapper left `from` >= slen : 18444

  R1   reads past val[slen] :  15333   first: ('ascii/0', from=1, length=0)
  R1h  reads past val[slen] :      0
```

**The smallest instance is the EMPTY string with `from = 1`** — a one-byte
allocation holding only the terminator. It ships as
`inputs/adversarial-empty.bin`.

⚠ **"Past `val[slen]`", not "past `val[slen-1]`", and the distinction is the
model of a PHP string.** `string->val` is `emalloc(len + 1)` with
`val[len] == '\0'`; index `len` is the terminator and is **inside** the
allocation. Both upstream guards admit `from == string->len` for exactly that
reason (§4). A kernel handed a source without a terminator would make the fix
look wrong by one byte, so `inputs/gen.py` writes it into every window and
`c/kernel.h` says why.

---

## §3 ⭐ The `mblen_table` lifts as static data — `TASK_PHP_016` §5.2 answered

The manager's second doubt was *"that the `mblen_table` can be lifted as static
data without becoming a `modelled` row — if reproducing it faithfully means
dragging in the encoding registry, the tier is wrong."*

**It does not, and the tier is right.** The evidence, in four parts:

1. **It is 256 bytes of `static const` in PHP too.** `mbfilter_utf8.c:39-56`,
   `static const unsigned char mblen_table_utf8[]`, reached as
   `encoding->mblen_table` — a field of a `const mbfl_encoding`
   (`mbfilter_utf8.c:58-65`). *Nothing* about it is dynamic. `c/kernel.c`'s copy
   is **byte-identical to the tarball's 16 lines**, diffed
   (`.temp/php16` table diff, `TABLE IDENTICAL (16 lines)`).
2. **The registry is what `narrowed` removes, and removing it is sound because
   the flag is a compile-time constant.** UTF-8's record is
   `{mbfl_no_encoding_utf8, "UTF-8", "UTF-8", aliases, mblen_table_utf8,
   MBFL_ENCTYPE_MBCS}`. `MBFL_ENCTYPE_MBCS` is neither `SBCS` nor any `WCS`
   bit, so the two WCS arms at `:1182-1193` are dead and the `else` arm at
   `:1260+` is unreachable. That is one checkable fact, it is in the tarball,
   and it is written into all three ledger entries rather than assumed.
3. ⭐ **It costs the PROOF one lemma, not a tier.** `verus.rs::lemma_mbtab_matches`
   proves `MBTAB@[b] == mbtab_of(b)` for **all 256 `b`** mechanically —
   `by (compute_only)` over a recursive conjunction plus one induction, ph03's
   `emit_ok_upto` recipe applied to static data — with **no `assume`, no
   `external_body`, and no sixth trusted item**. `controls/negatives.py --emit
   notable` changes ONE table entry and the proof fails.
4. **It must NOT be in the blob.** An attacker who could choose the table could
   put a zero in it, and the start walk would then spin for ever — a defect PHP
   does not have. `model.py::selfcheck` check 4 asserts every entry is ≥ 1 and
   check 5 re-parses the 256 numbers out of `c/kernel.c` and compares.

⚠ **The one place it cost something is `provenance.c_lines`, which pins a
single span.** The table is a second span in a second file, and `extract_sha256`
does not cover it. That is `TASK_PHP_015` §2.5's deferred schema decision
arriving on a second row, and this row does not fix it either — it declares the
span in the ledger and pins the bytes three other ways (the diff, check 5, and
the Verus lemma).

---

## §4 ⚠⚠ The fix commit — and it is in the CALLER, in another file

### 4a. What was found, and how

`TASK_PHP_016` §2 sent me to look for the commit that introduced 5.4.0's
prologue clamp `if (from >= string->len) { from = string->len; }`. **I found
it, and it is not the fix.** The manager then found the actual `fix_commit` in
a place neither of us had looked — **the corpus's own `index.csv` has a
`fix_commit` column** (`PLAN_PHP.md:109`), and `CRASH-124`'s cell reads
`cb3cca21b345`. Verified here:

```
CRASH-124  fix_commit  'cb3cca21b345'
CRASH-124  c_file_line 'ext/mbstring/libmbfl/mbfl/mbfilter.c:1203 (OOB read site);
                        missing guard at ext/mbstring/mbstring.c:1807'
CRASH-115  fix_commit  'f95c1df58349'      <- the column is trustworthy: this is
                                              exactly what ph03 established
                                              independently
```

⚠ **The `c_file_line` field said `missing guard at mbstring.c:1807` all along,
and I read the catalogue's paraphrase of it instead of the CSV.** That is
`.memory-php/00-corpus.md`'s standing rule — *the label is a hint; the line is
the claim* — with the roles swapped: the field was right and the derived prose
was where I stopped.

### 4b. The commit

```
cb3cca21b34518caf45852ed90597052e99294c3
Ilia Alshanetsky, 2005-12-15
"Fixed possible memory corruption inside mb_strcut()."
ext/mbstring/mbstring.c, +7 lines, ONE hunk, TWO guards
controls/cb3cca21b345.patch, 829 B, sha256 14dbafc9a3b970d0…
```

```c
+	if (from > Z_STRLEN_PP(arg1)) {          /* hunk (a) */
+		RETURN_FALSE;
+	}
+	if (((unsigned) from + (unsigned) len) > Z_STRLEN_PP(arg1)) {   /* hunk (b) */
+		len = Z_STRLEN_PP(arg1) - from;
+	}
+
 	ret = mbfl_strcut(&string, &result, from, len);
```

### 4b-bis ⚠⚠ `c/kernel.h` NAMED THE WRONG COMMIT AS R1h, FOR THE WHOLE LIFE OF THE ROW

`TASK_PHP_022` M2. `c/kernel.h:20-25` described `c/kernel_hardened.c` as

> *"the same file plus the prologue hunk of the real upstream fix
> `d9dda48f8a7e182ed8c0f56e5fde9e367131a07a` (Moriyoshi Koizumi, 2010-03-12),
> and nothing else"*

while the file ships `if (from > str_len) { return 0xFFFFFFFFu ^ php_shim_tally(); }`
— **`cb3cca21b345` hunk (a)**, in the caller's frame — and says so itself at
`kernel_hardened.c:10` and `:81`.

⚠⚠ **These are different programs and `spec.md` says so in the same block.**
`idiom.forbidden[2]` pins the 2010 clamp **ABSENT** with the reason
*"cb3cca21b345 returns FALSE where the clamp returns a cut"*, so the header
described R1h as **the very thing the contract forbids the Rust rungs from
being.** Measured, `controls/fix_scope.py` Q1 re-run at `TASK_PHP_024`
(`.temp/php24/fix_scope-rerun.log`): over 133 932 interpreted calls the two
guards are not the same function —

```
    variant    reads past val[slen]  answer != R1
    R1                        15333             0
    R1h                           0         16320     <- cb3cca21b345 hunk (a), SHIPPED
    R1_2010                       0          5717     <- d9dda48f8a7e's clamp
```

**Failure scenario, and it is concrete:** an agent reading `c/` to answer *"what
is this row's R1h?"* gets a guard that moves **5 717** answers where the shipped
one moves 16 320, and the two disagree on every call with `from > slen`.

⚠ **It is in the measurement record's `source_sha256`**, so correcting a comment
in it cost a re-measure — taken at `TASK_PHP_024`. ⚠ **And it survived three
passes** — the row's build, `TASK_PHP_016`, `TASK_PHP_017` and the
`TASK_PHP_018` rebuild — **including the one whose §0 disclosure claimed every
rung-source doc comment had been re-read.** The 2010 commit is still cited,
correctly, at `controls/d9dda48f8a7e-mbfilter.patch`,
`controls/fix_scope.py::R1_2010`, `spec.md`'s `forbidden[2]` and §4c below; the
defect was one sentence in one header, and nothing but a person could see it.

⚠⚠⚠ **AND IT HAD A SECOND COPY, IN `safe_naive.rs`, WHICH `TASK_PHP_022` DID
NOT FIND — IT LOOKED AT `c/` AND NOBODY GREPPED THE RUNGS** (`TASK_PHP_024`
§6a). `safe_naive.rs:7-17` said the four Rust rungs implement *"`mbfl_strcut`'s
mblen_table arm with **`d9dda48f8a7e`'s prologue**"* — **and contradicted the
ladder table four lines below it**, which names `cb3cca21b345`. It is in
`measure.py::measurement_sources` exactly as `c/kernel.h` is, and it would have
been a claim that the rungs carry the spelling `forbidden[2]` pins ABSENT.

**The sweep that found it, and it is three lines** — every hash-shaped token in
every measured source, asked what it is:

```sh
for f in c/kernel.c c/kernel.h c/kernel_hardened.c c/main.c \
         safe_naive.rs safe_tuned.rs unsafe.rs verus.rs model.py inputs/gen.py; do
  grep -a -o -E '\b[0-9a-f]{8,}\b' "$f" | grep -a -E '[a-f]' | sort -u; done
```

Everything else resolved to a commit sha, a tarball sha, a patch sha or a
body-sha pin. ✅ **The four OTHER `d9dda48f8a7e` mentions in measured sources —
`c/kernel.c:243`, `model.py:506`, `inputs/gen.py:27` and `:383` — are CORRECT**:
they describe that commit's `from < 0 || length < 0` hunk and its clamp to
`string->len`, and both really are in it
(`controls/d9dda48f8a7e-mbfilter.patch:106` and `:110`). `safe_tuned.rs`,
`unsafe.rs` and `verus.rs` name `cb3cca21b345` and do not mention 2010 at all.

⚠⚠ **THE COST LESSON: I RAN THAT SWEEP AFTER THE FIRST RE-MEASURE INSTEAD OF
BEFORE, AND IT COST A SECOND FULL PASS OF THE SIX-COMMAND CHAIN.**
`PROTOCOL.md` rule 6 says *"batch every rung-source doc fix into ONE pass"*;
**the enumeration that tells you what to batch is three lines of shell and
belongs before the first `--tool build`, not after it.**

### 4c. ⭐ The history, and it is the row's second finding

`mbfl_strcut`'s **body** is byte-identical — sha256 `613648930a3d2551…`,
4 693 B — at six release tags (5.0.0, 5.1.0, 5.2.17, 5.3.0, 5.3.1, 5.3.2).
`.temp/php16/07-history.log`, `.temp/php16/01-fixcommit.log`,
`controls/fix_scope.py` Q4.

| tag | `mb_strcut`'s own guards before the call | `mbfilter.c` prologue |
|---|---|---|
| php-5.0.0 **← THIS ROW** | — | — |
| php-5.0.5 / 5.1.0 / 5.1.1 | — | — |
| **php-5.1.2** ← `cb3cca21b345` | **`from >` + the sum clamp** | — |
| php-5.2.17 | `from >` only (**sum clamp GONE**) | — |
| php-5.3.0 / 5.3.1 | `from >` + the sum clamp **(back)** | — |
| php-5.3.2 | `from >` only (**gone again**) | — |
| **php-5.3.3** ← `d9dda48f8a7e` | `from >` only | **YES** |
| php-5.3.29 / 5.4.0 | `from >` only | YES |

⭐ **So the bound was restored TWICE, four years and three months apart, in two
different files.** The 2005 fix repaired the userland entry point;
`mbfl_strcut` itself — a library function any other caller could reach — stayed
unbounded until `d9dda48f8a7e` (2010-03-12), *"— Update the bundled libmbfl to
the latest on upstream"*, **64 files, +3435 −4164, no CVE, no bug number, no
security label**. Its `mbfilter.c` half is at
`controls/d9dda48f8a7e-mbfilter.patch`.

⚠ **And hunk (b) went out, came back and went again** — dropped at 5.2, present
at 5.3.0/5.3.1, gone from 5.3.2 on. §4e measures what it does; a guard that
changes benign output and cannot settle down for three minor releases is a guard
nobody was sure about.

### 4c-bis ⚠⚠ TWO GREPS, TWO OPPOSITE ERRORS, AND THE TABLE ABOVE IS THE REPAIR

**The first version of this table was wrong and the mistake is worth more than
the table.** I built it twice with two `grep`s over `mbstring.c`:

* `if (from > Z_STRLEN_PP(arg1))` — the 5.1.2 spelling. It scored **php-5.3.0
  through 5.4.0 as UNGUARDED**, because by 5.3 the same guard is spelled
  `if ((unsigned int)from > string.len)`. **A spelling-dependent grep reporting
  ABSENCE.**
* `from > Z_STRLEN_PP(arg1)` unanchored — it scored **php-5.0.5 and 5.1.1 as
  GUARDED**, because the hit is inside `PHP_FUNCTION(mb_strimwidth)`. **A
  function-blind grep reporting PRESENCE.**

⚠ **Neither error is visible from its own output; both are visible from the
other's.** What caught it was running the broader pattern *and then chasing the
discrepancy instead of taking the newer answer.**The repair is to stop matching
text and ask a question about a function**: `07-history.log` now parses
`PHP_FUNCTION(mb_strcut)` out of the file and looks only between its opening
brace and its `mbfl_strcut(` call. That is `.memory-php/`'s own recurring
lesson — *a guard that is a string search is a guard with a spelling* — arriving
in a **history table** rather than in a gate.

### 4c-ter ⭐⭐ AND THE SIBLING ENTRY POINT ALREADY HAD THE GUARD, IN 2004

Chasing that discrepancy turned up the finding this row should be remembered
for. In the **pinned 5.0.0 tarball**, `ext/mbstring/mbstring.c:1900`:

```c
/* PHP_FUNCTION(mb_strimwidth) */
if (from < 0 || from > Z_STRLEN_PP(arg1)) {
    RETURN_FALSE;
}
```

**It is the only occurrence of that text in the whole file.** `mb_strimwidth`
clamps `from` from above; `mb_strcut`, one screen away in the same file, written
in the same style against the same zval accessor, clamps it only from below —
and `cb3cca21b345` is, five and a half years later, that same line copied down.

⭐ **So this row's asymmetry is not one asymmetry, it is three, at three scales:**

| scale | guarded | unguarded |
|---|---|---|
| **within one function** | `mbfl_strcut`'s END walk, `:1213` | its START walk, `:1202` |
| **within one file** | `mb_strimwidth`, `mbstring.c:1900` | `mb_strcut`, `:1807` |
| **across time** | the caller, 2005 · the library, 2010 | 5.0.0 – 5.1.1 |

⚠ **That is the shape of the finding, and it is a stronger one than "the author
forgot a bound":** at every scale the correct code is *adjacent* to the
incorrect code. The bound was never unknown — it was never in the one place it
was needed.

### 4d. ⚠ The fidelity question, stated rather than smoothed over

**`kernel_hardened.c`'s citation is a different function from the extracted
one.** The manager asked for this to be said plainly, and here it is.

**Why I think it is nevertheless faithful.** This row's kernel is *two frames*.
`ph07_strcut` is `mbfl_strcut`'s arm; the `kernel()` wrapper **is**
`PHP_FUNCTION(mb_strcut)` — it already carries that function's two negative
clamps (`mbstring.c:1787-1805`), because they decide the kernel's domain and
without them a negative `from` would reach the walk, which `mb_strcut` cannot
produce. The fix's seven lines therefore land in the wrapper in **upstream's own
position**: after those two clamps, immediately before `mbstring.c:1807`'s call.
The diff between `c/kernel.c` and `c/kernel_hardened.c` is upstream's diff, in
upstream's place, against upstream's neighbouring lines.

**What a reviewer should attack.** R1 and R1h differ in the *wrapper*, not in
the *extracted function*. So this row cannot answer *"what does the fix cost
inside `mbfl_strcut`?"* — nothing was added there. It answers *"what does the
fix cost `mb_strcut`?"*, which is the question PHP's users had. ⚠ **If the
project wants the first question, the row it needs is R1h built from
`d9dda48f8a7e`'s prologue instead**, and `controls/fix_scope.py` already
measures that variant (`R1_2010`) so the swap is a decision, not a rebuild.

### 4e. What each guard buys — `controls/fix_scope.py`, `.temp/php16/08-fixscope.log`

```
calls interpreted                     : 133932
cb3cca21b345 hunk (a) would fire      : 16320
cb3cca21b345 hunk (b) would fire      : 32238   (with (a) not firing)

variant    reads past val[slen]  answer != R1
R1                        15333             0
R1h_a                         0         16320      <- (a) ALONE closes it
R1h                           0         32190
R1_2010                       0          5717      <- the 2010 clamp also closes it
R1_walk                   13293             0      <- the 2010 WALK REWRITE does NOT
```

⭐⭐ **`R1_walk` is the result to carry.** `d9dda48f8a7e` rewrote the start walk
to test before it reads (`for (m=0, p=val, q=p+from; p<q; p += (m=mbtab[*p]))`),
and **that rewrite alone still over-reads on 13 293 of the same calls.** The
loop shape is not the fix; the bound on `from` is. This is the variant a reader
guesses at, and it is wrong — which is why it is in the file.

⚠⚠ **Hunk (b) CHANGES BENIGN OUTPUT.** Q2, over the 117 612 calls that neither
over-read nor hit hunk (a):

```
of those, hunk (b) CHANGES the answer : 15870   (13.5 %)
e.g. 2byte/1 from=1 length=1
     (a) alone -> start=0 end=1 len=1
     (a)+(b)   -> start=0 end=0 len=0
```

It shortens `length`, which moves `k = start + length` out of the
`k >= string->len` shortcut and into the bounded end walk, and the cut comes
back shorter — on an input that never crashed. ⭐ **Upstream itself withdrew
it: php-5.2.17 carries (a) alone.** `check.py` stage 7h requires R1h to be
byte-identical to R1 on every non-adversarial input, so `inputs/gen.py`
`_check_span` refuses to write a measured window with
`from + length > string->len` and asserts `cb3cca21b345-fires=0`. **The change
is measured where it belongs and the measured corpus is not contaminated by
it.**

### 4f. ⭐ The `(unsigned)` casts are adequate, and the reason is the order

`controls/guard_equiv.py`, `.temp/php16/12-guardequiv.log`. Hunk (b)'s
`((unsigned) from + (unsigned) len)` is a 32-bit sum on two `long`s and looks
like an overflow waiting to happen. It is not:

```
SHIPPED    must NOT fire  disagreements=0
VARIANT c32 must NOT fire disagreements=0     <- the C's own 32-bit sum, in place
VARIANT ord must NOT fire disagreements=0     <- the two guards swapped
VARIANT m1 must FIRE      disagreements=2276
VARIANT m2 must FIRE      disagreements=269
VARIANT m3 must FIRE      disagreements=509
triples compared: 5122
```

`c32` is a **result**: hunk (a) runs first and has already bounded
`from <= string->len <= INT_MAX`, so the sum cannot reach 2³². ⚠ **`ord` is a
refuted prediction and it is left visible**: I expected swapping the guards to
fire, and it does not, because hunk (a)'s `RETURN_FALSE` *discards* whatever
hunk (b) computed. A control written to fire and then quietly reclassified is
how a probe stops measuring anything, so the prediction and its refutation both
stay in the file.

`SHIPPED must NOT fire, 0 disagreements` is the demonstration
`PROTOCOL_PHP.md` §A1(c) asks for on the Rust rungs' `usize` spelling of the
clamps, against a build of the C itself, with three firing mutants.

---

## §5 ⭐⭐ THE ROW'S FINDING: one function, one guarded walk and one unguarded one

`mbfl_strcut` does two cursor walks over the same buffer with the same table.

```c
/* :1202-1210 -- the START search.  UNBOUNDED. */
for (;;) { m = mbtab[*p]; n += m; p += m; if (n > from) break; start = n; }

/* :1212-1223 -- the END search.  BOUNDED. */
k = start + length;
if (k >= (int)string->len) { end = string->len; }
else { end = start; while (n <= k) { end = n; m = mbtab[*p]; n += m; p += m; } }
```

The second one's `else` branch is entered only when `k < string->len`, and it
steps while `n <= k`, so **every byte it reads is in range for a reason that is
in the 5.0.0 source already.** The first one has the same author, the same
table, the same cursor, three lines earlier, and no bound at all.

⭐ **The proof makes the asymmetry visible as an obligation.** In `verus.rs`,
`walk_start`'s reads are discharged from `frm <= slen` — a fact that does not
exist in 5.0.0 and arrives only with `cb3cca21b345` — while `walk_end`'s are
discharged from `k < slen`, which `mbfilter.c:1213` establishes. Delete the
2005 guard and only one of the two loops stops verifying:
`controls/negatives.py --emit noguard` fails on `invariant not satisfied before
loop: frm <= slen`, the start walk's bound, and the end walk is untouched.

⚠ **It is not "the author forgot".** The end search *needs* a bound because `k`
is `start + length` and `length` is unbounded; the start search's cursor is
compared against `from`, which *looks* like a bound and is not one, because
nothing relates `from` to `string->len`. **The defect is that a comparison
against an attacker-controlled scalar reads as a bounds check.**

---

## §6 ⭐ The over-read does not change the answer, and that is why it survived

`controls/fix_scope.py` Q3, `.temp/php16/08-fixscope.log`:

```
over-reading calls re-run under 7 different fillers : 15333
calls whose answer MOVED                            : 0
MUST-FIRE CONTROL (mbfilter.c:1227's `start > len` clamp DELETED): 13293 of 15333 moved
```

**Mechanism.** `start` is assigned the cursor of the iteration *before* the
break, so the first read at index `i > slen` happens with `start == i > slen`
already set; `start` only grows; `mbfilter.c:1227`'s `if (start > len) start =
len;` then forces `start = end = slen` and an empty cut. **R1's return value is
a deterministic function of the in-bounds input on every call, over-reading or
not.**

⭐⭐ **So the clamp that arrives too late to PREVENT the over-read is exactly
the clamp that HIDES it.** That is what the must-fire control demonstrates: the
same probe, with `:1227` deleted, moves on 13 293 of the same calls.

⚠ **My first must-fire control did not fire and I am leaving that visible.** It
moved `start = n` past the break test — so `start` took the cursor that had read
out of bounds — and the answer *still* did not move, for the same reason. **A
control that does not fire is not a passed control; it is a probe measuring
nothing**, and chasing why it did not fire is what produced this section.

**Consequence for the ladder.** `inputs/adversarial-silent.bin` and
`adversarial-offbyone.bin` differ only in the shape of the LAST CHARACTER
(all-ASCII vs a truncated four-byte sequence) and in nothing else. R1 reads one
byte past the heap block on both. The pair is here so the reader can see that
the *trajectory* differs while the *effect* does not.

---

## §7 The allocator

`uses_allocator: true`, and it is real: `mbfl_malloc` is
`(__mbfl_allocators->malloc)` (`mbfl_allocators.h:48`) and `mbstring.c:764`
points that vtable at `_php_mb_allocators`, whose `malloc` is `emalloc`
(`:240-243`) and whose `free` is `efree` (`:255-258`). So `mbfl_malloc((n + 8))`
at `:1245` **is** PHP's allocator and the row links
`common-php/emalloc_shim.h`.

⚠ **The truncations are not the defect here.** `n = end - start` is clamped to
`string->len` *before* the allocation, so `cap` is at most the window plus
eight and T1/T2/T3 sit ~2⁴⁰ below their moduli. The tally is folded into the
checksum so a rung that sized the result differently cannot agree by accident.

⚠ **The Rust rungs reproduce `php_shim_tally()` ARITHMETICALLY** and do not
link the shim. That pins the allocation SIZE across rungs; it is **not**
evidence that any Rust rung ran PHP's allocator. `ph03` says the same thing and
`TASK_PHP_013` §11 warns the technique does not carry to a row where the tally
*is* the defect. It carries here for the reason above.

---

## §8 The measurement, and the mechanism for every delta

`-O3 isolated`, kernel-exclusive `Ir`, from `results-php/ph07-strcut-cursor.json`
(`.temp/php16/22-irtable.log`). `small` = 25 000 calls over a 553-byte window;
`large` = 12 000 over 4 074. The two strides differ mod 4, 8 and 16.

⚠⚠ **EVERY FIGURE BELOW IS THE `TASK_PHP_018` RE-MEASURE.** The pre-rebuild
column is kept beside it, because the two are about different corpora and the
comparison is a result in its own right (§00).

| cell | `Ir`/call small | `Ir`/call large | **`Ir` / window byte** | fixed `Ir`/call | vs R4 | *was, pre-018* |
|---|--:|--:|--:|--:|--:|--:|
| `c-gcc` (R1) | 2 482.4 | 17 023.0 | **4.1297** | 198.7 | +28.72 % | *3.8643* |
| `c-gcc-h` (R1h) | 2 485.2 | 17 026.1 | **4.1298** | 201.4 | +28.72 % | *3.8643* |
| `c-clang` (R1) | 2 078.5 | 13 862.3 | **3.3467** | 227.7 | +4.32 % | *3.1814* |
| `c-clang-h` (R1h) | 2 084.7 | 13 868.4 | **3.3467** | 233.9 | +4.31 % | *3.1813* |
| `safe_naive` (R2) | 2 966.3 | 21 014.3 | **5.1258** | 131.7 | **+59.77 %** | *4.7860, +57.67 %* |
| `safe_tuned` (R3) | 2 061.3 | 14 711.1 | **3.5926** | 74.6 | **+11.98 %** | *3.4451, +13.50 %* |
| `unsafe` (R4) | 1 850.5 | 13 146.8 | **3.2083** | 76.3 | 0.00 % | *3.0354* |
| `verus` (R5) | 1 850.5 | 13 146.8 | **3.2083** | 76.3 | 0.00 % | *3.0354* |

⭐ **R4 and R5 are still byte-identical**, and the `identity` pin is unmoved.

⚠ **Every rate went UP and every ratio moved.** The new corpus admits windows
with `from + length > string->len`, which take the `k >= string->len` shortcut
more often (**16 % → 32 %** of windows), so a larger share of each call is start
walk and copy rather than end walk. **That is a property of the domain, not of
any rung** — the point of §00 is that the row is now measured over the whole
benign domain instead of the 86.5 % of it the withdrawn guard happened to agree
with 5.0.0 on.

⚠ **`RECAP_PHP.md` open item 9 / F14 respected: no number here is put beside a
`pNN` number, in a table or in prose.**

### 8a ⭐ THE UPSTREAM FIX COSTS A CONSTANT, NOT A RATE — and it is now ONE guard

**The claim survives and gets stronger; the WORDING that carried it does not.**

R1h is now **one** branch per call, outside both loops, where it used to be two.
The measured cost:

| | gcc | clang |
|---|--:|--:|
| `Ir`/call delta on `small` (553 B window) | **+2.8164** | **+6.1863** |
| `Ir`/call delta on `large` (4 074 B window) | **+3.0734** | **+6.1046** |
| fixed-term delta | **+2.7761** | **+6.1991** |
| *pre-018 fixed-term delta, TWO guards* | *+7.3022* | *+9.2685* |

⭐ **A 7.4× change in window size moves the R1h cost by 0.26 `Ir` on gcc and
0.08 on clang.** That is a constant, and it is measured across the widest lever
the fixture has.

⚠⚠ **DID IT GET CLEANER? IT GOT SMALLER ON BOTH COMPILERS AND CLEANER ON ONLY
ONE — SAID PLAINLY BECAUSE THE TASK THAT COMMISSIONED THIS PREDICTED IT WOULD DO
BOTH.** Measuring one guard instead of two halved the number, as expected. The
*dispersion* went two different ways:

```
                    marginal delta   4-dp equal?   small -> large delta   spread
pre-018  gcc        -3.504e-05       YES           7.2828 -> 7.1594       0.1234
pre-018  clang      -3.518e-05       no            9.2490 -> 9.1252       0.1238
TASK_018 gcc        +7.298e-05       no            2.8164 -> 3.0734       0.2570   2.1x WORSE
TASK_018 clang      -2.320e-05       YES           6.1863 -> 6.1046       0.0817   1.5x better
```

⚠ **And the "same marginal to four decimal places" test SWAPPED WHICH COMPILER
IT HOLDS FOR.** ⭐ Before the rebuild the two compilers' marginal residuals were
`-3.504e-05` and `-3.518e-05` — *identical to three significant figures*, which
`TASK_PHP_017` §5c read as the cross-check that the residual is a decomposition
artefact rather than an effect. **After the rebuild they are `+7.3e-05` and
`-2.3e-05`: different magnitudes AND opposite signs.** That agreement was
therefore a coincidence of one corpus, not a property of the decomposition.

**So the four-decimal-place phrasing is retired here**, and what replaces it is a
bound that does not sit on a rounding boundary: **the marginal moves by at most
7.3e-05 on a rate of 3.3–4.1, i.e. within 0.002 % on both compilers**, while the
delta is **2.82–3.07 `Ir`/call (gcc) and 6.10–6.19 (clang) across a 7.4× range of
window size**. That is a statement about a constant, supported by two points per
compiler, and it does not depend on a digit.

⚠ **Contrast ph03**, where the 2004 fix moved the marginal by ∓3.0 `Ir`/line
and the sign was compiler-dependent — because *that* fix is a test inside the
outer loop and hands the optimiser a trip-count fact. **The same question,
"what does the upstream fix cost?", has a different SHAPE on the two rows, and
the shape is decided by where in the loop nest the guard sits.** That contrast
is untouched by the rebuild.

⚠ **Contrast ph03**, where the 2004 fix moved the marginal by ∓3.0 `Ir`/line
and the sign was compiler-dependent — because *that* fix is a test inside the
outer loop and hands the optimiser a trip-count fact. **The same question,
"what does the upstream fix cost?", has a different SHAPE on the two rows, and
the shape is decided by where in the loop nest the guard sits.**

### 8b The mechanism, per loop, read off `objdump`

`.temp/php16/23-loops.log` — the tight loops, classified and counted:

| loop | body | R2 | R3 | R4 / R5 |
|---|---|--:|--:|--:|
| **start walk** | per character | **9 insns**, 1 bounds branch | **9**, 1 | **7**, 0 |
| **end walk** | per character | **8**, 1 | **8**, 1 | **6**, 0 |
| **copy** | per byte | **13**, 1 | *`memcpy@GLIBC_2.14`* | *`memcpy@GLIBC_2.14`* |
| **fold** | per byte | **10**, 0 | **8**, 0 | **8**, 0 |

R2's start walk, in full:

```
cmp    %rcx,%rax          <- the bounds check on s[n]
jae    <panic>
movzbl (%rbx,%rax,1),%r10d    <- s[n]
movzbl (%r10,%r8,1),%r10d     <- MBTAB[s[n]]   (no check: u8 index, [u8;256])
add    %rax,%r10
mov    %rax,%rbp
mov    %r10,%rax
cmp    %rsi,%r10
jbe    <top>
```

R4's is the same seven instructions with the `cmp`/`jae` pair deleted.

⚠⚠⚠ **THE PARAGRAPH THAT STOOD HERE IS RETRACTED, AND IT WAS THIS ROW'S
HEADLINE.** It read:

> *"R3's two walks are BYTE-FOR-BYTE R2's — 9 and 8 instructions, one bounds
> branch each. That is `safe_tuned.rs`'s header claim, measured: a
> variable-stride cursor is not an iterator, `n` advances by a value read out of
> the byte it is standing on, and **no reslice lets LLVM discharge
> `n < s.len()`**. R3's entire gain over R2 is the copy and the fold; **R4's
> entire gain over R3 is the two walks. The row's cost sits exactly where safe
> Rust cannot reach it.**"*

**`TASK_PHP_017` B1 refuted it by construction, in three characters of Rust**,
and `controls/spellings.py` now re-derives that refutation on this row's own
corpus rather than inheriting it. What survives and what falls:

- ✅ **KEEPS STANDING:** *a variable-stride cursor is not an iterator.* There is
  no `Iterator` whose `next()` is this step, and none of the variants is one.
- ❌ **RETRACTED:** *no reslice lets LLVM discharge the check*, and therefore
  *the row's cost sits exactly where safe Rust cannot reach it*. The false step
  is the inference from *"not an iterator"* to *"no safe spelling"*.
  **Re-slicing is not iteration; it is telling the compiler the invariant the
  guard has already proved** — after R1h the kernel knows `frm <= slen`, and the
  end walk is entered only when `k < slen`, so `&s[..=frm]` and `&s[..=k]` are
  facts, not new checks, and their panic branches are unreachable.
- ⚠ **`forbidden[1]` is NOT violated by it.** That entry excludes
  `p - string->val < (int)string->len`, *"the in-loop bound a reader adds on
  sight"*. The re-slice adds no in-loop bound: it re-expresses, ONCE and OUTSIDE
  the loop, something two lines above already established. The row's finding —
  that `mbfl_strcut` computes a bound and does not consult it — is untouched;
  what falls is the claim about safe Rust. Audited by
  `harness/check.py::spelling_matches` itself, in `controls/spellings.py` stage 0.
- ⚠ **DO NOT RE-SHIP R3.** `.memory/02-bench-rules.md` forbids re-shipping a
  rung because a cheaper in-contract spelling was found. §12 publishes BOTH,
  labelled.

⭐ **THE LOOP CENSUS ITSELF DID NOT MOVE AT `TASK_PHP_018`**
(`.temp/php18/loops-new.log`): 9/1 and 8/1 on R2 and R3, 7/0 and 6/0 on R4 and
R5, 13/1 copy and 10/1 fold on R2, 8/0 fold on R3 and R4. **Only the RATES
moved, because the corpus did.** That is the cleanest evidence that §00's rebuild
changed the domain and not the code generation.

**Arithmetic check on the R3 → R4 delta, re-derived on the new corpus.**
`.temp/php18/steps.py` replays the DRIVER's own window selection — not a uniform
average over windows, which is what the pre-`TASK_PHP_018` estimate used — and
counts walk iterations per call:

```
             start-walk steps/call   end-walk steps/call
small.bin           67.3276                35.4800        (553 B window)
large.bin          522.2337               257.4870        (4 074 B window)

marginal steps per window byte, slope through the two:
  start walk   (522.2337 - 67.3276)/3521 = 0.129198
  end walk     (257.4870 - 35.4800)/3521 = 0.063052
```

R4 deletes **2** instructions from the start walk (9 → 7) and **2** from the end
walk (8 → 6), so with no fitting at all:

```
predicted   2 x 0.129198 + 2 x 0.063052 = 0.384500 Ir/window byte
measured    3.592647 - 3.208273         = 0.384374
agreement                                  0.03 %
```

✅ **Within 0.03 %** — from the disassembly and the corpus alone, and **an order
of magnitude tighter than the pre-`TASK_PHP_018` version of this check (2 %)**,
because the step rate is now measured over the calls the driver makes instead of
estimated from `FRACTIONS` means and a mean character width.

### 8c ⚠⚠ THE CAVEAT THAT MATTERS: `memcpy` IS OUTSIDE `kernel_exclusive_ir`

`.memory/03-measurement.md` rule 7 — *kernel-exclusive `Ir` misses whatever the
rung calls out to* — **bites on this row**, and the record shows it: R3, R4 and
R5 carry `bulk_calls: ['memcpy@GLIBC_2.14']` and R2 and the C rungs do not.
So the table above charges R2 for a byte-at-a-time copy it performs inline and
does **not** charge R3/R4/R5 for the copy they delegate.

**Measured, hand-run, with the pinned valgrind** (`.temp/php18/totalir.py`,
re-derived on the `TASK_PHP_018` corpus; `--tool=callgrind`, TOTAL process `Ir`,
which includes the `memcpy`):

| rung | total `Ir`/window byte | kernel-exclusive | difference | *pre-018 difference* |
|---|--:|--:|--:|--:|
| `safe_naive` | 5.2578 | 5.1258 | +0.1319 | *+0.0377* |
| `safe_tuned` | 3.7605 | 3.5926 | +0.1679 | *+0.0696* |
| `unsafe` | 3.3761 | 3.2083 | +0.1679 | *+0.0696* |
| `verus` | 3.3711 | 3.2083 | +0.1629 | — |

**R2 vs R4 is +55.73 % on total `Ir` against +59.77 % kernel-exclusive; R3 vs R4
is +11.39 % against +11.98 %.** ✅ **The ordering and the magnitudes survive.**

⚠⚠ **BUT THE HIDDEN TERM GREW, AND THE OLD "~2 %" IS RETIRED.** It is now
**4.5–5.0 %** of total `Ir` on R3/R4 and 2.5 % on R2, where before it was ~2 %
across the board. The cause is §00's corpus: with `from + length > string->len`
admitted, more windows take the `k >= string->len` shortcut, `end` lands at
`string->len` and the **copy is longer relative to the walks**. So the term the
kernel-exclusive figure does not see is a larger share of the work than it was.

⚠ **`safe_naive`'s +0.1319 against R3/R4's +0.1679 is the bound on the
`memcpy`-specific part.** R2 calls no `memcpy` and still shows +0.1319 (its own
`_ecalloc`-shaped work and the driver), so the `memcpy` term is at most
`0.1679 − 0.1319 = 0.0360`, i.e. **≈ 1.0 % of R3's total** — the same
conclusion `TASK_PHP_017` §6 reached before the rebuild, and it survives at the
new magnitude. ⚠ `verus`'s +0.1629 against `unsafe`'s +0.1679 on
**byte-identical machine code** is a 0.15 % difference in TOTAL `Ir` and is the
size of the run-to-run residue in this measurement; read the third column to two
decimal places, not four.

**The caveat is real, it is bounded, and it is bounded by a measurement rather
than by an argument** — and the bound moved when the domain did, which is
exactly why it is re-derived here instead of carried forward.

### 8d ⚠ The wall clock says NOTHING here, and I am not going to pretend it does

`results-php/ph07-strcut-cursor.json`, `-O3 isolated`, 30 reps, `taskset -c 3`,
re-measured at `TASK_PHP_018` (`.temp/php18/wall-new.txt`):

```
cell         ns/win-byte small   ns/win-byte large   marginal   vs unsafe   worst spread
safe_naive          1.2430              1.0601        1.0314      -5.83%       6.9 %
safe_tuned          1.2339              1.0651        1.0386      -5.18%       8.1 %
unsafe              1.2055              1.1102        1.0953       0.00%       8.1 %
verus               1.2109              1.1368        1.1252      +2.73%       9.0 %
```

⚠⚠ **R4 and R5 are the same machine code** (§`identity`, `md5_fn_norel`
identical, 255 instructions in both) **and their wall marginals differ by
2.73 %, with `verus` the SLOWER of the two.** ⚠ And on this corpus the wall
clock says **safe Rust is 5–6 % FASTER than unsafe Rust**, in flat contradiction
to the `Ir` table above, which says it is 12 % slower **with the safe rung
executing measurably more instructions**.

⭐ **That contradiction is the finding, and it is a stronger one than the
pre-`TASK_PHP_018` version of this section carried.** Then, the argument was
*"the R4-vs-R5 gap (5.4 %) is larger than every difference in the table"*, and
`TASK_PHP_017` m2 correctly objected that one cell exceeded it. Now the point
does not depend on any comparison of magnitudes: **two byte-identical binaries
disagree by 2.7 %, and the sign of the safe-vs-unsafe difference is OPPOSITE to
the sign of an instruction count that is not in dispute.** A measurement that
reverses a fact you can count is measuring the box, not the program. **The wall
numbers are reported and are evidence for nothing on this row** —
`.memory/03-measurement.md` rule 6's spirit, one step further: report ns, and
then say when ns cannot decide.

### 8e What these numbers are NOT

- ✅ **This IS now a searched comparison — on both sides.** `controls/spellings.py`
  (§12) was written at `TASK_PHP_018` and it is the first one in
  `patterns-php/`. Read §12 before quoting any figure in §8: the `+11.98 %`
  above is a **`fixed-R4 bound`**, not "the cost of safe Rust", and its
  cheapest-found in-contract counterpart is beside it.
- ⚠ **Not a bounds-check tax in aggregate.** A ph07 call walks, walks again,
  allocates, copies and folds; only the two walks and (in R2) the copy carry a
  check R4 removes. §8b separates them.
- ⚠ **Not a bounds-check tax in aggregate.** A ph07 call walks, walks again,
  allocates, copies and folds; only the two walks and (in R2) the copy carry a
  check R4 removes. §8b separates them.
- ⚠ **The C-vs-Rust column is confounded by a choice this row made and ph03
  made too**: `vec![0u8; cap]` ZEROES the destination and `mbfl_malloc` does
  not, so every Rust rung pays `cap` bytes of zeroing the C never pays. It
  cancels in every safe-vs-unsafe delta and does **not** cancel in
  C-vs-Rust — which is one reason `c-clang` (3.3467) lands so close to
  `unsafe` (3.2083) while `c-gcc` (4.1297) does not. ⭐ **And `TASK_PHP_018`
  put a number on what that zeroing costs, by accident**: `r4_nozero` (§12b)
  deletes it and measures IDENTICALLY to the shipped R4 — because the zeroing is
  a `memset` CALL and therefore outside `kernel_exclusive_ir` altogether. So the
  confound is real but it is invisible to the column it confounds, and §8c is
  where it shows.
- ⚠ **`c-clang` beats `c-gcc` by 19.0 %** on the marginal, which is larger than
  the R3→R4 safety effect and is **not a safety effect at all**. The C rungs
  vectorise their copy (`vector_regs: ['xmm']`, 22–25 backward branches); the
  Rust rungs either call `memcpy` or emit a scalar loop. `.memory/03-measurement.md`
  rule 2 is why both C columns are here. ⚠ It was 17.7 % before `TASK_PHP_018`;
  it moved with the corpus, like everything else in §8.

---

## §9 ⚠ Scope: what this row deliberately does NOT model

`mbfilter.c:1212` is `k = start + length` on two `int`s and **overflows** for a
`length` near `INT_MAX`. That is a **second, distinct defect**, fixed upstream
in 2016 by `f8dd10508bd6` / `64f42c73efc5` (bug #71906) — the only php-src
commit whose subject names an `mbfl_strcut` memory-safety bug, and it fixes the
*rewritten* function, not this one. R1h does not guard it either, so an input
that reached it would trip UBSan on the **hardened** rung and `check.py` stage
7h would hard-fail.

`inputs/gen.py::_check_span` therefore asserts `max(start + length) < 2^31` and
refuses a corpus that leaves `int`. **Stated as a boundary, not hidden**: a row
that models two defects at once cannot attribute a number to either.

---

## §10 R5 — Verus

**21 verified, 0 errors; 24 under `--cfg slb_twin`.** Three runs of each,
identical (`.temp/php16/10-rlimit.log`).

```
requires  off + len <= buf@.len(),  9 <= len
ensures   r == strcut_fold(buf@, off as int, len as int)
```

A full functional postcondition, not a memory-safety-only retreat.
`model.py::strcut_fold` re-derives the same `u64` from a different
decomposition, and `model.py::_dumb` from a third.

### 10a. The two facts the proof rests on, and they come from two places

1. **`mbtab_of(b) >= 1`** — every table entry is at least one, so `n` strictly
   increases and the start walk has a `decreases` at all. A fact about STATIC
   DATA, proved out of the literal 256-byte table by `lemma_mbtab_matches`
   (`by (compute_only)` over a recursive conjunction, plus one induction).
   **No `assume`, no `external_body`, no sixth trusted item** — §3.
2. **`from <= string->len`** — which is `cb3cca21b345` hunk (a), and is what
   discharges every `get_unchecked`. **Delete that one line and the proof
   fails.**

⭐ And the end walk needs neither: `mbfilter.c:1213` bounds it in the 5.0.0
source already (§5).

### 10b. ⚠⚠ The proof-budget finding, and the reduction came first

`.temp/php16/09-profile.log`, `.temp/php16/10-rlimit.log`.

The kernel first **did not verify at `--rlimit 100`** — ten times the default —
and `--profile` said why: **4 127 instantiations of vstd's
`Seq::new(len, f)[i] == f(i)`, 88 % of the total cost.** The cause is that
`MBTAB@` is `array_view`, which vstd defines as `Seq::new(256, …)`, so **every
mention of the table inside a spec function drags a 256-element sequence axiom
into the SMT context** — and `walk_start`/`walk_end` mentioned it on every
recursive step.

✅ **The repair was to take the table OUT of the spec path**: `mbtab_of` became
a closed form over the byte's range, `lemma_mbtab_matches` ties it to the
literal table once, and the `broadcast use vstd::array::group_array_axioms` was
scoped to the three items that need it instead of being module-level. **Same
kernel, same postcondition: from "does not verify at rlimit 100" to "verifies
at the default in five seconds."**

⚠ **`#[verifier::rlimit(30)]` is still on the kernel, and its JUSTIFICATION
CHANGED AT `TASK_PHP_018`.** It used to be load-bearing. Measured after the
reduction and BEFORE the rebuild: the kernel needed ~10–12 plain and **15 under
`--cfg slb_twin`**, where the three verified twins add to the module's context.
At the default 10 it verified plain and **failed twin**; with two `assert`s
removed it verified twin and **failed plain**.

⭐ **Removing `cb3cca21b345` hunk (b) made the proof CHEAPER on both sides** —
one fewer branch on `length` in `strcut_fold` and one fewer in the kernel — and
the requirement is now **9 on BOTH**. Bisected at `TASK_PHP_018`
(`.temp/php18/rlimit-sweep.log`):

```
rlimit   PLAIN                          TWIN
   7     20 verified, 1 errors          23 verified, 1 errors
   8     20 verified, 1 errors          24 verified, 0 errors   <- twin's floor is 8
   9     21 verified, 0 errors          24 verified, 0 errors   <- plain's floor is 9
  10     21 verified, 0 errors          24 verified, 0 errors   <- the DEFAULT
```

⚠ **So both sides now pass at the default, with a margin of ONE.** The override
stays, and it stays for a different reason than it went on: not *"twin fails at
the default"* but *"the requirement is 9 against a default of 10, which is the
width of a coin flip"*. 30 is 3.3× the measured requirement. A proof that passes
on one side of a coin flip is not a proof, and one that passes by a single
rlimit unit is on the same coin. ⚠ `harness/check.py::_verus` passes no
`--rlimit`, so this has to be an attribute rather than a flag.
**It is 30 and not 300 because the cost was attacked first.**

⚠⚠ **AND THE DIRECTION OF THE PLAIN/TWIN ASYMMETRY REVERSED.** Before, twin
needed MORE than plain (15 vs 10–12); now plain needs more than twin (9 vs 8).
Nothing was done to cause that and I do not have a mechanism for it. **It is
reported because a disclosure that only survives while its number is convenient
is not a disclosure** — and because it is a second, independent sign that
rlimit-adjacent measurements on this kernel sit close to a threshold rather than
on a plateau.

⚠ **The reusable lesson, and it is not about this row**: *a module-level
`broadcast use` is a cost every function in the file pays.* Scoping the groups
to the items that need them is free and, on a row that lifts a lookup table,
decides whether the file verifies at all.

### 10c. TCB — four trusted items

| item | why it is trusted | twin |
|---|---|---|
| `get_unchecked(v: &[u8], i)` | vstd ships no spec for `<[T]>::get_unchecked`; the `requires` is std's documented contract | ✅ `slb_twin_get_unchecked` |
| `vget_unchecked(v: &Vec<u8>, i)` | same, for the destination read | ✅ |
| `vset_unchecked(v: &mut Vec<u8>, i, x)` | the destination WRITE; `ensures` is the whole post-state `old(v)@.update(i, x)` | ✅ |
| `load_input`, `emit` | file I/O and `println!`; **no `ensures` at all**, deliberately — an `ensures` here would axiomatise the contents of a file | n/a (no `unsafe`) |

⚠ **That is five `external_body` items and four trusted *contracts*** — `emit`
and `load_input` state nothing, so nothing can be wrong about them except that
they run; they are counted anyway, because `.memory/04-verus.md` records a pilot
published as *"one 3-line wrapper"* whose true tally was three.

### 10c-bis. Trusted items — the arguments no oracle can make

`harness/check.py` stage `5c-twin` requires one written argument per trusted
item, for the three things no stage of the gate can judge. It prints them and
fails without them; **only a human can judge them.**

SLB-TRUSTED-ARGUMENT verus.rs get_unchecked

(a) **Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*v.get_unchecked(i)`; the twin's body is `v[i]`. The standard
library documents `get_unchecked(i)` as `index(i)` with the bounds check
removed, so it is the same operation on the same slice at the same index, and
Verus checks the bound `v[i]` needs against the same `requires`. A defensive
twin — `if i < v.len() { v[i] } else { 0 }` — cannot satisfy the `ensures` and
fails the stage rather than passing it.

(b) **Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes *as the body stands*: one expression, one unchecked read,
at index `i` of slice `v`, and `ensures r == v@[i as int]` names that index and
that slice. ⚠ **Nothing mechanical enforces it.** A second unchecked read the
`ensures` never mentions — `let _peek = *v.get_unchecked(i + 1);` — is invisible
to 5a, 5c, 5c-req and 5c-twin alike.

⚠⚠ **AND THIS ROW'S BACKSTOPS ARE WEAKER THAN ph03's, WHICH IS WORTH SAYING
RATHER THAN COPYING ph03's PARAGRAPH.** ph03 can lean on its `exact` O3
identity pin: an extra read added to `verus.rs` alone moves `md5_fn` and stage
3c fails. **ph07's O3 pin is `norel`, not `exact`** (§`identity`), because the
kernel calls `memcpy@GLIBC` and the two crates lay their PLT out differently —
so identity here compares `md5_fn_norel`, which is a weaker instrument. It
would still catch an added `movzbl` (the instruction count 255 and the byte
count 953 are both pinned and both would move), but it is a normalised
comparison rather than a byte one. **Miri is the other backstop and it needs an
input that reaches the boundary**: on ph07 that is
`adversarial-offbyone.bin`/`-empty.bin`/`-wild.bin`, whose whole point is that
`from` sits past the end — except that R4/R5 REFUSE those calls at
`cb3cca21b345` hunk (a) and never reach the walk at all. ⚠ **So on the
adversarial inputs Miri exercises the refusal, not the boundary; the boundary
read `s[slen]` (the zval terminator) is reached on the benign windows whose
`from == string->len`, which `inputs/gen.py` guarantees exist (`from==len=4` on
`small.bin`, 256 on `large.bin`) and `_check_span` asserts.** That is the input
class a reviewer should check the body against. **Read the body, every time.**

(c) **Does the clause mean the same in both configurations?** Yes. `i < v@.len()`
mentions only `i`, `v` and vstd's `@`/`len()`, and `v: &[u8]` / `i: usize` are
concrete types with no generic or associated item that a `#[cfg]` could
redefine. The gate additionally forbids the token `slb_twin` anywhere in the
file except each twin's own `#[cfg(slb_twin)]`.

SLB-TRUSTED-ARGUMENT verus.rs vget_unchecked

(a) Yes, and it is `get_unchecked`'s argument with `&Vec<u8>` in place of
`&[u8]`: the unchecked operation is `*v.get_unchecked(i)` reached through
`Vec`'s `Deref<Target = [T]>`, and the twin is `v[i]`, which is `Vec`'s `Index`
— documented as the slice index. ⚠ **It is a separate item rather than a reuse
of item 1 for a real reason**: `out` is a `Vec` the kernel owns and `s` is a
borrowed slice, and passing `out.as_slice()` to item 1 would put a `Deref` call
between the proof and the fold loop that R4 does not have, which would move the
`norel` identity pin.

(b) Yes as the body stands — one expression, one unchecked read at `i`, and the
`ensures` names it. Same residual and the same two backstops as item 1, with
the same weakening noted there. ⚠ **Its boundary input is different and easier**:
this wrapper reads `out[j]` for `j < cnt`, and `cnt == 0` on every adversarial
input (the refusal path) while `cnt` is hundreds of bytes on `small`/`large`,
so the boundary `j == cnt - 1` is reached on every benign call.

(c) Yes, and identically to item 1: `i < v@.len()` over `&Vec<u8>` / `usize`.

SLB-TRUSTED-ARGUMENT verus.rs vset_unchecked

(a) **Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*v.get_unchecked_mut(i) = x`; the twin is `v.set(i, x)`, vstd's
verified `Vec` store, whose own `ensures` is `v@ == old(v)@.update(i, x)` —
character for character this item's postcondition. ⚠ It is **not** `v[i] = x`,
because `IndexMut` on `Vec` has no vstd specification; `set` is the checked
spelling Verus can reason about, and the twin rules forbid `unsafe` in a twin
so there is no third option.

(b) **Is the `ensures` complete?** Yes, and **this is the item where the answer
is load-bearing rather than routine.** The postcondition is the WHOLE
post-state, `final(v)@ == old(v)@.update(i as int, x)`, not `v@[i] == x`. A body
that also clobbered `v[i + 1]` would satisfy `v@[i] == x` and violate
`update(i, x)`, so **for a body whose only writes are through this contract the
`ensures` is complete by construction** — which is exactly why it is spelled
this way and not the shorter way. ⚠ The residual is a body that performs an
extra unchecked **READ**, which no `ensures` about the post-state can see; that
is item 1's residual and has item 1's backstops.

(c) **Does the clause mean the same in both configurations?** Yes.
`i < old(v)@.len()` and `final(v)@ == old(v)@.update(i as int, x)` mention only
`i`, `v`, `x` and vstd's `@` / `len()` / `update()`. `v: &mut Vec<u8>`,
`i: usize` and `x: u8` are concrete, and `#[cfg(slb_twin)]` is the only `cfg` in
the file (the gate checks that).

SLB-TRUSTED-ARGUMENT verus.rs load_input

(a) There is **no twin and there must not be**: this item contains no `unsafe`,
so the twin regime does not apply to it, and a checked stand-in for argument
parsing and file I/O does not exist. It is trusted because it is I/O.

(b) The `ensures` is **empty, deliberately**. An `ensures` here would be an
axiom about the contents of a file, which nothing can justify. Every fact the
proof needs — `buf@.len() == n_blob`, `stride >= 9`, `stride <= n_blob` — is
re-derived at run time inside verified code from `bytes.len()` and the driver's
own guard.

(c) N/A — no clause, and no `cfg`.

SLB-TRUSTED-ARGUMENT verus.rs emit

(a) No twin, no `unsafe`: `println!` through `common/driver.rs`. Trusted
because printing is not verifiable.

(b) No `ensures`, so nothing to be complete about. What it prints is checked
elsewhere and much more strongly: stage 2 compares this rung's stdout against
`model.py`'s expectation on every input, across all 32 cells.

(c) N/A.

### 10d. The mutants — `controls/negatives.py`, `.temp/php24/negatives-rerun.log`

```
noguard    expect FAIL got FAIL  verification results:: 20 verified, 1 errors  ok
nopos      expect FAIL got FAIL  p.rs:159:12  assert(mbtab_matches_upto(256))
                                 by (compute_only);  error: aborting  ok
notable    expect FAIL got FAIL  p.rs:159:12  assert(mbtab_matches_upto(256))
                                 by (compute_only);  error: aborting  ok
noconsume  expect PASS got PASS  verification results:: 21 verified, 0 errors  ok
  verus.rs sha256 unchanged: d1c61785e44185f8
EXIT=0
```

⚠⚠ **THE BLOCK THAT USED TO STAND HERE WAS `\.temp/php16/13-negatives.log` — a
PRE-REBUILD RUN — and it announced the fact in its own last line without acting
on it** (`TASK_PHP_022` m4): it ended `verus.rs sha256 unchanged: 28811d6d6f45c3b2`,
which is `git show 8214b5f:`'s hash, while the rebuilt `verus.rs` is
`d1c61785e44185f8`. ✅ **The substance was true and stayed true** — the reviewer
re-ran it, and so did `TASK_PHP_024`; all four mutants behave, on the file the
row actually ships. **Only the pasted evidence was stale, and pasting the run is
the whole repair.** ⚠ It is the same class as §0a's hashed `why`: a block of
evidence that is correct about a program the row no longer contains.

⭐⭐ **`noguard` NOW ISOLATES ONE GUARD, AND IT DID NOT BEFORE.** It used to have
to delete **both** `cb3cca21b345` hunks, because hunk (b)'s `slen - frm` needs
`frm <= slen` too — so a hunk-(a)-only mutant died on an ARITHMETIC UNDERFLOW
one line later and never reached the walk (`.temp/php16/13-noguard.log`). With
hunk (b) withdrawn (§00) there is nothing between the guard and the walk, and
the mutant now fails **at the walk's own loop invariant**
(`.temp/php18/noguard-site.log`):

```
error: invariant not satisfied before loop
   |  frm <= slen,
verification results:: 20 verified, 1 errors
```

**That is the obligation the control exists to demonstrate.** A control that
could only ever fire for a confounded reason now fires for the right one —
which is a second, independent thing the rebuild bought and which nobody asked
for.

⚠⚠ **`nopos` DOES NOT TEST TERMINATION AND ITS DOCSTRING SAID IT DID**
(`TASK_PHP_017` m1, fixed in `controls/negatives.py` at `TASK_PHP_018`). Setting
`mbtab_of` to 0 for a lead-byte class also breaks `mbtab_matches_upto`, so the
mutant dies at `p.rs:159`'s `compute_only` assert — the **same error site as
`notable`**. Two controls, one failure mode. ⭐ The termination premise IS
load-bearing and IS provable separately: zeroing `mbtab_of` **and** the matching
`MBTAB` entries together keeps the table lemma true and dies at `mbtab()`'s
`r >= 1` postcondition instead (`.temp/php17/mut/`). ⚠ **No shipped control
isolates it, and that is a stated gap rather than a repaired one** — adding a
fifth mutant is a task, not an edit, and it would move `contract_sha256`
again.

⚠ `noconsume` is a **must-PASS** control and is therefore weaker than the other
three: it shows the postcondition is unconsumed decoration unless `main` reads
it, and it cannot show the file is still being mutated. `noguard` shares the
emit path and is must-FAIL, so a `negatives.py` that had stopped editing
anything would be caught there.

---

## §12 ⭐ THE SPELLING SPAN — `controls/spellings.py`, BOTH SIDES SEARCHED

**The first `controls/spellings.py` in `patterns-php/`.** `.memory-php/02`
records the debt on both built php rows — *"NO RATIO HERE IS THE COST OF SAFETY,
AND THESE ARE `fixed-R4 bound`s"* — and `ph03`'s own hashed `why` has demanded
one since that row was built. `ph07` is the first php row to discharge it.

⚠⚠ **The pipeline reproduces the shipped record to 0.000 % on all four cells
before any variant is quoted**, because it computes the row's own statistic —
`kernel_exclusive_ir / n_iters` on the shipped inputs — and not `check.py`'s
100-vs-200 marginal. ⚠ A first draft used the marginal and came out **1 %** from
the record; those are different statistics (200 iterations visit a different
sample of the 32 or 2 050 windows) and a control quoted beside the headline has
to compute the headline. The 1 % near-miss is recorded because it is exactly the
size of error that gets absorbed as noise.

⚠⚠⚠ **`TASK_PHP_017` B1's `+2.62 %` IS NOT CARRIED OVER AND MUST NOT BE
QUOTED.** It was measured against the corpus §00 deleted.

### 12a The R3 side — the headline moves, and the mechanism predicts it

```
cell                Ir/call small  Ir/call large  Ir/win-byte  fixed/call  vs R4ship
R3 v0_shipped              2061.3        14711.1       3.5926        74.6   +11.98%
R3 r3_reslice              1892.6        13410.5       3.2712        83.6    +1.96%
R3 r3_reslice_st           1926.7        13666.6       3.3343        82.8    +3.93%
R3 r3_reslice_en           2027.2        14454.9       3.5296        75.4   +10.02%
R3 r3_get_unwrap           2163.6        15490.2       3.7849        70.6   +17.97%
R4 v0_shipped              1850.5        13146.8       3.2083        76.3    +0.00%
```

**Loop census of the variants** (`.temp/php18/loops-variants.log`):

| | start walk | end walk |
|---|--:|--:|
| R3 shipped | 9 insns, 1 cond-exit | 8, 1 |
| `r3_reslice` | **7, 0** | **7, 0** |
| R4 shipped | 7, 0 | **6, 0** |

⭐ **`r3_reslice`'s start walk is instruction-for-instruction R4's, in safe Rust
with zero `unsafe`**, and the entire residue between them is **one instruction
in the end walk**.

**Predicted from the mechanism with no fitting**, using §8b's measured step
rates (0.129198 start-walk steps and 0.063052 end-walk steps per window byte):

```
R3 -> r3_reslice   2 x 0.129198 + 1 x 0.063052 = 0.32145   measured 0.32137   0.02%
r3_reslice -> R4   1 x 0.063052               = 0.06305   measured 0.06290   0.24%
```

✅ **`r3_reslice` captures 83.6 % of the R3 → R4 gap in safe Rust**, and the
remainder is one `mov`.

⚠ **`r3_get_unwrap` is the calibrating negative**: `s.get(n).unwrap_or(&0)` is
safe, total, and the spelling most people reach for — and it is **6 % WORSE than
the shipped R3**. A search with no losing entry is a search nobody can calibrate.

### 12b The R4 side — **DEGENERATE, and that is a clean negative**

`SYNTHESIS.md:271-277`: *the headline moves toward whichever side you did not
search*, and on 19 searched PAT rows **eleven found no cheaper R4**. `ph07`
makes it twelve.

```
r4_fused      3.2082 Ir/window byte   -0.004%   fixed/call 88.3   TIE (< 0.05%)
v0_shipped    3.2083                  +0.000%   fixed/call 76.3   SHIPPED
r4_index0     3.2083                  +0.000%   fixed/call 76.3   TIE (< 0.05%)
r4_nozero     INADMISSIBLE -- no verifying twin
```

- **`r4_index0` is FREE and STRICTLY BETTER on the trusted side.** Spelling the
  first table read `s[0]` instead of `*s.get_unchecked(0)` compiles to **the
  same bytes at the same addresses** (`.temp/php18/loops-variants.log`: every
  loop at an identical offset), its twin verifies at **21/0**, and it removes
  one of `get_unchecked`'s four call sites. ⚠ **It is not shipped** —
  `.memory/02-bench-rules.md` forbids re-shipping a rung for a cheaper in-contract
  spelling, and this one is not even cheaper; it is a *smaller trusted surface at
  the same price*, which is a finding for a future row and not a licence to edit
  this one.
- **`r4_fused` is a TIE, not a win.** Merging the copy and fold loops moves the
  marginal by **0.004 %** and makes the fixed term **12 `Ir`/call WORSE**.
  ⚠ Its twin verifies (`20 verified, 0 errors`) but at a DIFFERENT obligation
  count from the pinned 21 — `lemma_fold_shift` becomes unnecessary — so
  shipping it would move `verus.obligations` as well. Reading −0.004 % as "the
  R4 endpoint moves" is exactly the over-reading this file exists to prevent,
  and `spellings.py` carries a `TIE_PCT` threshold so that it cannot.
- **`r4_nozero` is the refusal, and it has a reason.** `Vec::with_capacity` +
  `set_len` instead of `vec![0u8; cap]` is `set_len` over uninitialised memory;
  the pinned vstd has no spec that makes it sound and the twin does not verify.
  ⭐ **It would also have bought nothing**: it measures identically to the
  shipped R4, because `vec![0u8; cap]`'s zeroing is a `memset` call and
  therefore **outside `kernel_exclusive_ir`** — the same blind spot §8c prices.
  A refusal with a reason is a result (`p42`'s `endptr` precedent).

### 12c ⚠⚠ THE TWO NUMBERS THE CRASH COURSE MAY QUOTE, AND ONLY THESE

```
fixed-R4 bound              R3ship - R4ship          +11.98 %
cheapest-found in-contract  inf(R3 found) - R4ship    +1.96 %   spelling `r3_reslice`
```

⚠⚠ **NO PAIR INTERVAL.** `min(R3 found) - min(R4 found)` differences two upper
bounds and bounds nothing in either direction; `ph03`'s hashed `why` retracts
that construction in terms and this row does not resurrect it. ⭐ Here the R4
side is **degenerate** — no admissible R4 moved by more than 0.004 % — so the
`fixed-R4 bound` is a bound over a *searched* endpoint, which is a materially
stronger thing to publish than the same number was before `TASK_PHP_018`.

---

## §11 What I did NOT do, and what I am unsure about

1. ✅ **`controls/spellings.py` EXISTS as of `TASK_PHP_018`** — §12, both sides
   searched, the R4 side degenerate. ⚠ **The search is not exhaustive**: five R3
   spellings and four R4 spellings were tried, over roughly one working session.
   `r3_reslice` leaves **one instruction** between safe Rust and R4 and I did not
   find a spelling that closes it; I do not claim none exists. ⚠ `ph03` still
   owes its own, and the debt there is untouched.
2. ⚠ **No `sweep-*` band.** `work_per_call` moves between `small` and `large`
   (553 vs 4074, different residues mod 4/8/16), which is what
   `check_marginal_ir` needs, but two points and a line is not a curve.
3. ✅ **`provenance` now pins all THREE lifted spans** (`extra_spans`, added to
   `harness-php/provenance.py` at `TASK_PHP_018` — §1). ⚠ **What it exposed is
   worse than what it fixed**: the caller frame scores **15 % overlap**, so the
   row cites three spans at three different fidelities and the tier is a single
   word. §1a says what I think of that.
4. ⚠ **R1h is cited to a different function from the extracted one** — §4d —
   **and it is now also a SUBSET of the commit that fix is labelled with.** §00
   argues the tagged configuration is the stronger citation and `spec.md`
   `idiom.required[4]` states the alternative it was chosen against. **This is
   the thing to attack.**
5. ⚠ **`#[verifier::rlimit(30)]`** — §10b. Both sides now verify at the default
   with a margin of one, and the plain/twin asymmetry reversed for no reason I
   can give.
6. ⚠ **`r202895` is UNRESOLVED.** `c2471b495009`'s message blames *"the commit
   by r202895"* for introducing hunk (b). `TASK_PHP_018` could not map that SVN
   revision to a git sha: php-src's converted history carries **no `git-svn-id`
   trailer** (checked on the commits either side), `svn.php.net` no longer
   resolves, and a harvest of self-referencing revision numbers from php-src
   commit messages in four windows around 2005-12, 2006-06, 2008-01 and 2009-09
   returned **only the three copies of this very commit**
   (`.temp/php18/svnprobe.py`). **The attribution is not relied on anywhere.**
   What is measured is the code: the three lines removed in 2009 are
   byte-identical to three of the seven added in 2005, and the function carries
   them continuously at every tag from php-5.1.2 to php-5.2.11.
6. **Unsure: whether `adversarial-silent.bin` earns its measurement slot.** It
   costs eight iterations over a 105-byte window and it is the only cell that
   shows the over-read's *effect* is invisible while its *trajectory* is not.
   A reviewer may reasonably say §6's numbers already say that and the file is
   redundant.
7. **Unsure: the `FRACTIONS` table.** `from` and `length` are drawn as fixed
   fractions of the window so the work scales with `work_per_call`. That is a
   design choice with a consequence: **every window's `from` is at the same
   relative position**, so the corpus spans lead-byte classes and the two arms
   of `:1213` but *not* the distribution of `from` a real workload has.
   `model.py::selfcheck`'s synthetic sweep covers the domain; the *measurement*
   does not.
8. **Unsure: `work_per_call = stride` over-estimates by more than ph03's does.**
   A ph07 call walks `from` bytes, then up to `length` more, then copies
   `end - start` — none of which is the window. The over-estimate raises the
   derived `Ir` floor, which is the safe direction, but the denominator is
   further from the work than on a row that touches every byte once.
