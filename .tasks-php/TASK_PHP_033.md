# TASK_PHP_033 — execute item 51 on `ph29`, then discharge its spellings debt

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_033_REPORT.md` — **write the FILE** (rule 10).

**Two stages, and Stage A is the gate on Stage B.** Stage A applies the
manager's item 51 decision to `ph29/spec.md` and re-gates. Stage B is the
spellings search that item 51 was blocking. ⚠ **They are one task because
separating them costs TWO `ph29` re-gates** — `idiom` is inside
`contract_sha256` and a `controls/*.py` addition re-gates the row as well.

⭐ **YOU ARE AUTHORISED TO STOP AFTER STAGE A AND REPORT.** `TASK_PHP_028` spent
a whole task on one row's spellings search and that was the right call. If
Stage A's re-gate surprises you, or Stage B's search is larger than it looks,
**stop and write the report**. A half-task that reports honestly beats a whole
one that hurries. Say which stages you completed, in the headline.

**Read**, in this order:
1. `.tasks/PROTOCOL.md` — rules 9, 10, 11, 13, **14**.
2. `.tasks-php/PROTOCOL_PHP.md` — **§H binds Stage B** (a validator lands with
   its must-fire negatives or it does not land).
3. `.memory-php/02-ladder.md` **in full** — authoritative, and **it states the
   spellings debt in terms**. It supersedes any task report it contradicts.
4. `.memory/02-bench-rules.md`'s **`fixed-R4 bound`** rule.
5. ⭐ `patterns-php/ph07-strcut-cursor/controls/spellings.py` + `spellings.json`
   — **the template.** `ph07` is the only fully discharged row.
   **Read it; do not touch it.**
6. `.tasks-php/TASK_PHP_028_REPORT.md` — `ph16` discharged, and §4.1's refuted
   hypothesis is the shape your Stage B conclusion may also take.
7. `harness/check.py::idiom_audit` and `::exec_code` — **docstrings only.**
   They are the authority on what a pin means. ⚠ **Read, never edit.**

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **No `git add` / `git commit`.** Never touch `.web/` — a **concurrent session**
edits it.
⚠ Scratch under `.temp/php33/`. **Never `/tmp`.**
⚠ **`grep -a` ALWAYS** — plain `grep` dispatches to `ugrep` and exits 1 with no
output on 41 of 1170 corpus files, silently (F35).
⚠ **No `until … sleep` poller loops.** Foreground `sleep` is blocked. A previous
build task leaked ~60 shells that way. Use **one** tracked background job and
wait for its notification.

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`12/0`**, first and last.
Both measured by the manager at 2026-09-11, immediately before this file was
written. ⚠ The php figure moved `10 → 12` when row 5 landed — **a row adds TWO
measure records.** Report the figures you actually get.

---

## §1 The decision you are executing, and the evidence behind it

Item 51 asked whether `ph29`'s `idiom.required` pinning **zero** tokens is a
defect or a `p05`-style prose-only declaration. **The manager decided: it is a
defect, and it is repaired.** The whole derivation is
`.temp/mgr169/NOTES.md` §1 with three self-tested probes beside it:

| probe | what it settles | run it |
|---|---|---|
| `.temp/mgr169/ph29_pins.py` | **7 of 8** leading spans already pin a rung → these are spellings with the ticks dropped, not propositions | `--selftest`, then bare |
| `.temp/mgr169/charlit_reach.py` | the char-literal blind spot is **latent**: 0 affected spellings in 33 PAT + 6 PHP rows | `--selftest`, then bare |
| `.temp/mgr169/ph29_predict.py` | **the numbers your re-gate must produce** | bare |

⭐ **Run all three before you edit anything.** They are read-only. If any
`--selftest` is not PASS, or `ph29_predict.py`'s `committed` and `now` columns
disagree, **stop and report** — the tree has moved under the decision.

⚠ **`ph29` is the only real PHP row that pins zero required tokens** —
`ph03` 5, `ph07` 14, `ph16` 13, `ph64` 7, **`ph29` 0**. (`ph00-smoke` is 0 too
and is not a counter-example: it is a relocated PAT calibration kernel with no
PHP provenance, and it prices nothing.)

---

## §2 STAGE A — the `spec.md` edit

Backtick the leading span of `required[0]`…`required[3]`, both language keys.
**Three of the eight need thought and the reasons all differ.**

| entry | the pin to write | note |
|---|---|---|
| `required[0].c` | `` `emalloc(to_read + 1)` `` | as-is |
| `required[0].rust` | ⚠ **`` `.wrapping_add(1)` ``** | **RESPELLED** — §2.1 |
| `required[1].c` | ⚠ **`` `read_buf[recvd] =` ``** | **RESPELLED** — §2.2 |
| `required[1].rust` | `` `vset_unchecked(&mut read_buf, recvd, 0)` `` | kept, but ⚠ **owes English** — §2.3 |
| `required[2].c` | `` `php_shim_tally()` `` | as-is |
| `required[2].rust` | `` `1000039` `` | as-is |
| `required[3].c` | `` `php_shim_reset` `` | as-is |
| `required[3].rust` | `` `real_size` `` | as-is, ⚠ **weak** — §2.4 |

### §2.1 `required[0].rust` — do NOT pin a binding name

All four Rust rungs compute the allocation request, and that request **is** this
row's defining idiom, so the entry must bind all four. But they spell it
differently: `safe_naive.rs:100` and `safe_tuned.rs:64` write
`(to_read as u64).wrapping_add(1)`, while `unsafe.rs:88` writes
`tr.wrapping_add(1)`.

**Quoting `tr.…` would put the two safe rungs out of their own contract on a
VARIABLE NAME** — p17's whitespace disaster in a new costume, where six cells
fell out of contract on two space characters.

`.wrapping_add(1)` pins all four at **exactly one line each** — `safe_naive:100`,
`safe_tuned:64`, `unsafe:88`, `verus:450` — and nothing else. ⚠ Verify that at
**line** level, not just rung membership: `idiom_audit`'s docstring warns that
substring matching is a real false-positive shape, and the closing paren is what
keeps this span off `.wrapping_add(1000039)`.

### §2.2 `required[1].c` — ⚠⚠ NEVER BACKTICK A CHARACTER LITERAL

`required[1].c` today reads `read_buf[recvd] = '\0'` and **pins nothing**, and
that is a **matcher artefact, not a kernel defect**: `c/kernel.c:247` really does
spell the row's own fault line, but `exec_code` layer 1 blanks *"comments and
string/char literals"*, so the matcher sees `read_buf[recvd] =     ;`.

> **The rule this yields, and it is a WRITING rule:** a declared spelling
> containing a character literal can never match. In `required` it reports
> `pins nothing`; in `forbidden` it is **a ban that cannot fire**, and since
> TASK_068 `forbidden_hits` is the half that **FAILS** the gate — a check that
> silently cannot fail, `PROTOCOL_PHP.md` §H's exact target.

⚠ **This is NOT a bug report against `harness/`.** The blanking is deliberate
and documented in `exec_code`'s own docstring. `exec_code` is hashed into all 33
PAT gate records; **no `harness/` edit is proposed, wanted, or permitted.**

⚠⚠ **And the blind spot is LATENT, which is what decides the repair:**
`charlit_reach.py` measures **0 affected spellings across 33 PAT and 6 PHP
rows**. Backticking `read_buf[recvd] = '\0'` would **create the first one in
either programme**, on the row's own fault line.

`read_buf[recvd] =` pins `c/kernel.c:247` and `c/kernel_hardened.c:175`, one
line each — the fault line and its hardened twin, exactly.

### §2.3 `required[1].rust` — the one GENUINE scope, and it owes a sentence

⚠⚠ **`required[0]` and `required[1]` carry NO ENGLISH AT ALL today** — a bare
span per language and nothing else. That is the finding that changes this edit
from "add backticks" into something you have to think about. `required` is given
**no verdict by design**, precisely because *which rungs an entry binds lives in
its English*; an entry with no English declares a spelling and says neither what
it binds nor what it is required **for**.

Here the rungs differ **semantically**, and the difference is the whole point of
the ladder at this line:

* safe rungs — the **checked** `read_buf[recvd as usize] = 0` (`safe_naive.rs:142`)
* unsafe side — the **unchecked** `vset_unchecked(&mut read_buf, recvd, 0)`

There is **no shared span**, and per-language keys cannot express it because both
spellings are Rust. So the spelling is kept and **the entry must gain the
sentence that scopes it to R4/R5 and names what the safe rungs write instead.**
Without that sentence the record carries two absences no reader can adjudicate.

⚠ `required[0]` should gain a sentence too, saying it binds **all four** Rust
rungs and why the request is the row's idiom.

### §2.4 `required[3].rust` — weak, and left alone on purpose

`real_size` is a bare identifier occurring **3–7 times per rung**. It pins "this
name occurs", not a construction. Its English carries the `PROTOCOL_PHP.md` B1.3
argument, so it stays as it is — **recorded here so that nobody later reads it as
a tight pin.** Do not respell it; do not strengthen it in this task.

### §2.5 ⚠ The correction owed inside the same hashed block

`forbidden[0]` closes: *"NOTE THE ABSENCE OF BACKTICKS throughout this entry and
the three below."* **That is false about its own scope.** `forbidden[2]` carries
`` `calloc` `` and `forbidden[3]` carries `` `#undef _FORTIFY_SOURCE` `` —
`forbidden_unaudited_entries` is **2**, not 4. Correct the sentence. The block is
being rehashed anyway, so the correction is free.

### §2.6 ⚠⚠ THE TRAP THAT ALREADY CAUGHT TWO PEOPLE

`forbidden[0]` records, at length, that the gate refused this row **twice**
because the entry quoted the expression it was **PROTECTING** — in a `forbidden`
entry *every* backticked span becomes a ban.

**The manager then reproduced it while writing this task.** The first draft of
`ph29_predict.py` put the old span **in backticks** into the explanatory tail —
which would have added a second pin, including, on `required[1].c`, the very dead
char-literal pin §2.2 exists to avoid. Caught before it ran.

▶ **So: when your new English explains what a rung "really writes", write that
span WITHOUT backticks.** Say so in the prose, as the shipped entries do.

⭐ The transferable half: *a trap that has bitten the author, been documented at
length by the author, and then bites the next reader of the documentation is a
trap whose write-up is aimed at the wrong half.* If you see a cheaper way to
make this unmissable, put it in the report — **do not** invent a new gate check.

### §2.7 The falsifiable prediction — Stage A's definition of done

`ph29_predict.py` applies the edit to an **in-memory** copy and runs the
**shipped** `idiom_audit` over the **shipped** rungs. Your re-gate must produce:

| key | committed | **required after your edit** |
|---|---|---|
| `spellings` | 4 | **12** |
| `forbidden_spellings` | 4 | **4** |
| `pairs` | 12 | **36** |
| `present` | 0 | **22** |
| `required_pins_nothing` | 0 | **0** |
| `required_absent` | 0 | **2** |
| `forbidden_hits` | 0 | **0** |
| `forbidden_unaudited_entries` | 2 | **2** |

Both predicted absences are `required[1].rust` on `safe_naive.rs` and
`safe_tuned.rs` — the one genuine scope, per §2.3.

⚠⚠ **If you get different numbers, STOP AND REPORT. Do not adjust the
declaration until the prediction comes out.** A prediction that is quietly
edited to match the result measures nothing. This is the same discipline
`TASK_PHP_032`'s stage-7h prediction was given, and it came out green first try.

⚠ For contrast, the **naive** edit — quote all eight exactly as written — gives
`present 20`, `required_absent 4` and one dead pin. The two respellings are worth
**+2 present, −2 absent, and no dead pin.** If your numbers look like the naive
column, you skipped §2.1 or §2.2.

### §2.8 What this edit does and does NOT buy — state it in the report

⚠ **`required` cannot fail the gate, by design, and this edit does not change
that.** It adds **no check that can fail.** What it buys is **Stage B**: the
named-spelling standard makes the admissible class decidable by grep, and with
zero pins `ph29`'s class was not decidable at all. That is the whole reason item
51 blocked the spellings task.

**Do not claim in the report that `ph29` is now "enforced".** It is now
**searchable**. Those are different, and the difference is exactly what the
`required`/`forbidden` asymmetry is about.

---

## §3 STAGE B — the spellings debt

`ph29`'s published spread is **−6.06 %** (`safe_tuned` 23,441,029 `Ir` vs
`unsafe` 24,951,895, O3/isolated). ⚠ **It is NEGATIVE, so no figure in this row
is a `fixed-R4 bound` at all** — the same position `ph16` was in, and
`TASK_PHP_028` §4.1 resolved that one by **refuting** the spelling-artefact
hypothesis and publishing the negative spread as a **result**.

**Search both sides.** `ph03` owes it for having searched neither; `ph16` and
`ph29` owe it because the spread is negative. Your question is `ph16`'s
question, asked of a different row:

> **Is `ph29`'s negative spread a spelling artefact, or a result?**

Ship `controls/spellings.py` + `controls/spellings.json` **under
`patterns-php/ph29-recvfrom-alloc/`**, to `ph07`'s template. **§H binds**: it
lands with its must-fire negatives or it does not land. ⚠ The path is split
across two spans on purpose — written whole it is a forward reference to a file
that does not exist yet, and `citecheck.py` rightly flags those in a LIVE doc.

⚠ **`identity: unsafe == verus, O3 exact` still binds.** An R4 respelling that
has no byte-identical Verus twin is a **control, not a rung**, and shipping it
would cost a new TRUSTED item. Read the **error text**, not the exit code:
`is not supported` disqualifies; `postcondition not satisfied` disqualifies
nothing.

⚠ **Publish two quantities, never three**: `R3ship − R4ship` (the `fixed-R4`
bound) and the **R3-side span**, cheapest-found to dearest-found in contract,
both labelled. **No pair interval.** `min(R3 found) − min(R4 found)` is **not**
the repair — two upper bounds differenced bound nothing in either direction.

⚠ **Do not re-ship a rung for a cheaper spelling.** R4 is held fixed by fiat;
that is what makes the bound a bound.

---

## §4 Definition of done

1. All three `.temp/mgr169/` probes run, `--selftest` PASS reported verbatim.
2. `ph29/spec.md` edited per §2, including §2.3's new English and §2.5's
   correction.
3. `ph29` re-gated **green**, and §2.7's eight numbers reported **beside** the
   predicted ones, whether or not they match.
4. Stage B either complete (control + `spellings.json` + a labelled verdict on
   the negative spread) **or explicitly deferred with a reason**.
5. Both brackets, first and last.
6. ⚠⚠ **Your headline and your gate are two separate claims, and only the gate
   record settles the second.** A previous build task reported "built" while its
   own gate was still running, and that gate then failed twice before passing.
   **Do not write a verdict you have not read out of `results-php/gate/`.**
7. Anything you found that contradicts this file — say so. §1's probes are the
   manager's own work and carry **no** review.
