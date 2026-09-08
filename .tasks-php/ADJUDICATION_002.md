# ADJUDICATION_002 — `RECAP_PHP.md` open item 4 and `TASK_PHP_012` rider m8

**Author: the manager.** Two standing items, both flagged as *"the most likely
place the spatial axis lost a real row"*. ✅ **One was already closed and the
handoff did not know it; the other is real, and both candidates are admitted.**

⚠ **EVIDENCE, NOT A LANDED DECISION.** Every catalogue edit below is **blocked
by `PROTOCOL.md` rule 11** — `TASK_PHP_016` is reading `CATALOGUE.md`. Land with
item 21's batch (`PROTOCOL.md` rule 6).

---

## §1 Open item 4 (CRASH-136, exif) — ✅ **ALREADY CLOSED. Close the item.**

`RECAP_PHP.md` open item 4 says *"rejected on EXTRACTION COST … **Manager must
re-adjudicate**"*. **It was re-adjudicated**, in the very file the item's own
neighbours cite: `ADJUDICATION_001.md` **§Item 4 — "CRASH-136 (exif): ADMIT, and
CRASH-134 with it"**. The row exists:

```
CATALOGUE.md:91   | ph13 | spatial | base + attacker 32-bit offset, lower-bounded only | narrowed | I1/O1 | CRASH-136 | — | catalogued |
CATALOGUE.md:288  **ph13 · exif: base + attacker 32-bit offset, lower-bounded only** — `ext/exif/exif.c:3071-3079` · CRASH-136 · `narrowed` · I1/O1
```

⚠ **The open-items table outlived the work that closed it.** `PROTOCOL.md`
rule 13's shape — *when you correct an item, re-read its header* — one level up:
**when you close a finding, re-read the open-items table.** ⭐ **And it hid a
second result**: `ADJUDICATION_001` admitted **CRASH-134 alongside it, which no
open item had ever named**, so a row was recovered that nothing was tracking.

**→ Mark item 4 `~~4~~ ✅ CLOSED at `ADJUDICATION_001` item 4 → `ph13` (+ CRASH-134).**

## §2 Rider m8 — `CRASH-106` and `CRASH-109` are killed against a bar that does not exist here

`CATALOGUE.md` **C.1** is headed *"Kills — **exact** C-side duplication
(criterion: `PLAN_PHP.md` §3.1)"*. §3.1 says, in a table:

| duplicates another `patterns-php/` row's C mechanism | ⚠ **a slight variation is ADMITTED as its own row** |
|---|---|
| **C-side duplication, exact** | kill |

**and the user decision it quotes is explicit**: *"Even within patterns-php,
slight variations I am still okay with as a different pattern."*

⚠⚠ **Neither kill note claims exactness. Both name the distinguishing feature
and then discount it for COST** — the move `PLAN_PHP.md` §3 forbids and F8
names:

| | the note says | the forbidden word |
|---|---|---|
| CRASH-106 | *"distinct only in needing a ~358 MB input, **which is a worse kernel**"* | **worse kernel** = cost |
| CRASH-109 | *"the second `alloced` growth path at `:692` **muddies the extraction** without changing the mechanism"* | **muddies the extraction** = cost |

**Both are ADMITTED.** Verified at source in the pinned tarball:

### `ph92` — `nl2br`: the only sizing wrap in the corpus with ONE attacker degree of freedom

`ext/standard/string.c:3593`, inside `PHP_FUNCTION(nl2br)` → tier **`narrowed`**.

```c
int	new_length;                                                        /* :3558 */
int	repl_cnt = 0;                                                      /* :3560 */
…
new_length = Z_STRLEN_PP(zstr) + repl_cnt * (sizeof("<br />") - 1);         /* :3593  == + repl_cnt * 6 */
tmp = target = emalloc(new_length + 1);                                    /* :3594 */
```

⭐ **The multiplier is a compile-time constant and `repl_cnt <= strlen`, so the
attacker has exactly ONE free value.** That is what makes the wrap need
`len >= 2^31/7 ≈ 307 MB` — **the input size is a CONSEQUENCE of the mechanism,
not a property of our test harness**, which is precisely why *"it needs a big
input"* cannot be the reason to refuse it. Every other member of the family
(`ph19` attacker×attacker, `ph20` collapsed into `safe_emalloc`'s first argument,
`ph21` narrowed by the store, `ph22` accumulated across two passes) gives the
attacker two or more.

✅ **The sizing pass is otherwise exact** — `\r\n` costs 8 emitted bytes and is
budgeted 2 + 6; a lone `\n` costs 7 and is budgeted 1 + 6. **The `int` overflow
is the whole defect**, which makes it a *clean* kernel, not a muddy one.

⚠ **Rider (m5)**: the emit loop is unbounded, so the adversarial cell needs
≥ 307 MB **resident**. `ph28` should keep its uniqueness claim narrowed to that
word rather than to *"the only row needing a memory budget"*.

### `ph93` — `wordwrap`: a buffer RESIZED MID-EMIT, with unchecked growth arithmetic

`ext/standard/string.c:682` and **`:692-694`**, inside `PHP_FUNCTION(wordwrap)`
→ tier **`narrowed`**.

```c
int textlen, breakcharlen = 1, newtextlen, alloced, chk;                    /* :635 */
…
if (linelength > 0) { chk = (int)(textlen/linelength + 1);                  /* :678 */
                      alloced = textlen + chk * breakcharlen + 1; }         /* :679 */
else                { chk = textlen;
                      alloced = textlen * (breakcharlen + 1) + 1; }         /* :681-682 */
newtext = emalloc(alloced);                                                 /* :684 */
…
for (current = 0; current < textlen; current++) {
    if (chk <= 0) {
        alloced += (int) (((textlen - current + 1)/linelength + 1) * breakcharlen) + 1;   /* :692 */
        newtext  = erealloc(newtext, alloced);                              /* :693 */
```

⭐⭐ **The distinctness is NOT the sizing expression — it is `:692-694`.** No
row in the 91 has a buffer that is **grown during the emit pass by arithmetic
that is itself unchecked `int`, and that divides by an attacker-controlled
`linelength`.** `ph19`–`ph22` all size once and then write. **A realloc-in-loop
is a different C shape and a different proof obligation**, and the kill note
concedes it exists before discounting it.

⚠ **Two sizing formulas, not one** (`linelength > 0` vs not), so the row must say
which arm it lifts. ⚠ **And `:692` divides by `linelength`**, which the else-arm
reaches with `linelength <= 0` — **a possible second defect (SIGFPE) that is NOT
this row's claim.** Flagged, not folded in: `PLAN_PHP.md` §4.2's invented
non-defect rule cuts both ways.

### What is NOT established here

⚠ **Criterion 2 — *"exhibits the target error on ≥1 adversarial input,
demonstrated with a detector firing and a positive control that must also
fire"* — is NOT demonstrated for either candidate.** Neither was it for the
other 91 when they were catalogued; it is discharged at build. **These two are
admitted to the CATALOGUE on C-side distinctness, and they face the full bar
like every other row.**

## §3 The count this makes

`ADJUDICATION_001`'s closing line: *"That is now **four** instances in one audit
(CRASH-136, CRASH-157, CRASH-033, CRASH-053) — enough that it is the audit's
main result, not an anecdote."*

⚠⚠ **With CRASH-106 and CRASH-109 it is SIX, and the last two were sitting in
the catalogue's own kill list the whole time, under a heading that says
`exact`.** The audit found the instances it went looking for; **the two that
survived were the two written down as settled.** `.memory-php/01-extraction.md`
already carries *"an audit that re-examines only what it doubts measures its own
priors"* — **this is that finding's second confirmation, and it argues the
remaining C.1 rows deserve the same read.** ⚠ **`CRASH-090`, `V5C-116`,
`V5C-173`, `V5C-015`, `CRASH-037/101`, `CRASH-061/126/163` are NOT re-examined
here** — four of them say *"merged by the corpus itself"*, which is a different
and stronger claim than a reviewer's judgement, but nobody has checked that
either.

## §4 The catalogue edits, exactly

**Three sites, all blocked on rule 11.** New ids: the catalogue has **91** rows,
max `ph91` → **`ph92`** (nl2br), **`ph93`** (wordwrap).

1. **Part A** — two rows after `ph91`:

```
| ph92 | spatial | `base + count*CONST` in `int`: one attacker degree of freedom | narrowed | I11/O2 | CRASH-106 | p13 | catalogued |
| ph93 | spatial | buffer regrown mid-emit; the growth arithmetic is unchecked `int` | narrowed | I11/O2 | CRASH-109 | — | catalogued |
```

2. **Part B** — the two blocks in §2 above, in the `int`-sizing family, beside
   `ph19`–`ph22`.
3. **Part C** — **delete** the `CRASH-106` and `CRASH-109` rows from `C.1` and
   add one line under the table recording that they were **re-adjudicated and
   admitted as `ph92`/`ph93`**, with a pointer here. ⚠ **Do not silently drop
   them** — `TASK_PHP_012` M1 found that six of twelve "merges" were silent
   drops, and a kill that vanishes is worse than a kill that was wrong.
4. ⚠ **`ph28`'s uniqueness sentence** narrowed to *resident* (m5 rider).
