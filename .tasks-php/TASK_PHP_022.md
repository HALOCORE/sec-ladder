# TASK_PHP_022 — adversarial review of the `ph07` rebuild, and of the manager's R1h decision

**Role:** research **reviewer**. **One agent, alone.** `PROTOCOL.md` rule 1 — you
are **not** the engineer who did this.
**Report:** `.tasks-php/TASK_PHP_022_REPORT.md` — **write the FILE** (rule 10).

Read `.tasks/PROTOCOL.md` (the reviewer checklist), **`.memory-php/`**
(authoritative — it supersedes any task report it contradicts),
`.tasks-php/PROTOCOL_PHP.md`, **`.tasks-php/UPSTREAM_002.md`** (**manager work,
unreviewed — §2 below attacks it**), **`.tasks-php/TASK_PHP_018.md` and
`TASK_PHP_018_REPORT.md`** (what you are reviewing), and
`patterns-php/ph07-strcut-cursor/` in full.

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **Do not edit `patterns-php/CATALOGUE.md`** — a landing task is queued on it.
⚠ **`.web/` belongs to a CONCURRENT SESSION — never `git add -A`, never touch it.**
⚠ **No `git add` / `git commit`.** Read-only git is fine.
⚠ Scratch under `.temp/php22/`. **Never `/tmp`.** `.temp/php18/` has the
engineer's `REBUILD.sh` and probes, `.temp/php17/` the previous review's,
`.temp/mgr165/` mine — **reuse them.**

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`6/0`**, first and last.

⚠⚠ **`grep -a` ALWAYS**; **ask about a FUNCTION, not about text** (a grep for
the hunk's own line reports it absent from php-5.3.0, where it is present and
respelled). ⚠ **And a probe that CANNOT EVALUATE must say so** — the manager's
own counting script printed a positive claim about the C for eight cases it had
failed to parse, and that output was quoted twice before an agent caught it.

---

## §1 ⚠⚠⚠ THE HEADLINE, AND IT IS REFUTABLE BY CONSTRUCTION — DO THAT FIRST

`TASK_PHP_018` §1a produced the rebuild's biggest claim, and I have promoted it
to F47's headline:

> *"A memory-safety-only `ensures` would have stayed green through the entire
> rebuild."*

**It is an assertion about a proof nobody wrote.** ⚠ **Write it.** Take
`verus.rs`, **weaken the postcondition to memory safety alone** (no value
equality — the buffer is in bounds, the walk terminates, nothing is read past
`slen`), keep hunk (b)'s clamp in the exec the way the row shipped it before
`TASK_PHP_018`, and **verify.**

- **If it verifies**, the claim is *demonstrated* rather than asserted, and it
  becomes the single most quotable thing this programme has produced for the
  crash course. **Say exactly what the weakened `ensures` was**, because the
  claim is only as strong as that spelling.
- **If it does NOT verify**, the headline is wrong and I have put it in the
  handoff. ⚠ **Report that plainly and say which obligation caught it** — a
  refutation here is worth more than a confirmation.
- ⚠ **Either way, state what "memory-safety-only" cost you to define.** If a
  faithful memory-safety-only spec turns out to be *hard to state* for this
  kernel, **that is itself the finding**, and it is a more interesting one.

## §2 ⚠⚠ THE R1h DECISION IS MINE AND IT IS UNREVIEWED

`UPSTREAM_002` is manager work. `TASK_PHP_018` built on it and **refused my
protocol extension** (correctly, and I accepted). **The decision underneath is
still uncleared** (`PROTOCOL.md` rule 3 — never clear your own design).

1. **Is hunk (a) alone really memory-safety-complete?** The row says hunk (b)
   removes **none** of the 15 333 reads past `val[slen]`. **Re-derive it, do not
   re-read it.** ⚠ And attack the boundary: `from == string->len` is *admitted*
   by hunk (a) (`>` not `>=`) and is safe only because `mblen_table_utf8[0] == 1`
   at the terminator. **Is that true for every encoding this kernel admits, or
   only for the one the fixture uses?**
2. ⚠⚠ **Is `controls/bug49354.py` a faithful replay of upstream's test?** It is
   now the load-bearing evidence for the whole rebuild — it is what declined my
   stopping point. **Open `ext/mbstring/tests/bug49354.phpt` in
   `c2471b495009.patch` and check the six cases, the encoding, and the expected
   strings against what the control asserts.** ⚠ **A control that replays a test
   incorrectly and passes is worse than no control.**
3. **Is the corpus really unrestricted now?** `inputs/gen.py` should refuse only
   windows where **hunk (a)** fires (the adversarial case). **Verify no residue
   of the hunk-(b) restriction survives**, and that windows with
   `from + length > slen` are actually *present* in the shipped `.bin`s.

## §3 THE NUMBERS — re-derive, do not re-read

1. **The ladder**: R2 **+59.77 %**, R3 **+11.98 %**, R4 ≡ R5 byte-identical.
2. ⚠⚠ **`spellings.py` is the FIRST in `patterns-php/` and every later php row
   will clone it. Review it as a template, not as a control.** Its own first
   draft *"measured the wrong statistic and came out 1 % from the record"* —
   ✅ disclosed, and the fix reproduces the record at **0.000 %**. **Check that
   the statistic it computes really is `measure.py`'s**, on all four cells.
3. ⚠⚠⚠ **ATTACK THE R4 SIDE. The row calls it DEGENERATE and explicitly does not
   claim it is exhausted** — *"four R4 spellings and five R3, about one working
   session."* **This is the claim with the most riding on it**: it is what makes
   `+11.98 %` a bound over a *searched* endpoint, and it is the 12th of 20 rows
   in a corpus-wide statistic. ⭐ **A cheaper admissible R4 would be a first-rate
   result. Try to find one.**
4. **`r4_index0`** — *"the same bytes at the same addresses, verifies 21/0, one
   fewer `get_unchecked` site."* **Check the disassembly claim yourself.** ⭐ If
   it holds it is a *smaller trusted surface at the same price*, which is a
   different axis from the bench rule's and may deserve its own name.
5. ⚠ **(c) got smaller without getting cleaner, and the §5c cross-check
   evaporated.** ✅ The engineer reported this against its own task file's
   prediction. **Check the replacement argument stands on its own** — and
   whether anything *else* in the row still leans on the vanished agreement.

## §4 THE SCHEMA AND THE SPANS

`extra_spans` landed in `harness-php/provenance.py`. **Confirm `ph03` and
`ph00-smoke` really are byte-identical** and that the validation of an extra
span is as strict as the primary's. ⚠ **Then the finding**: the caller frame
scores **15 %** overlap, i.e. `modelled` text inside a row declaring `narrowed`.
**Is `ph07`'s declared tier now wrong?** `tier` is a **cost statement, never a
filter** — so this cannot kill anything — but the row may owe a correction.

## §5 What I am least sure of

1. ⚠⚠⚠ **That I was right to accept §4.1's refusal of my own rule.** The
   engineer argued a norm needs n ≥ 2 and I agreed within minutes. **Check I did
   not simply defer to a well-argued report**: is the four-disclosure worked
   example *itself* a norm wearing an observation's clothes? **If landing 4.1-A
   already commits us to 4.1-B in practice, say so** — that is the failure mode
   I would not see from here.
2. ⚠⚠ **That rebuilding row 2 was worth it at all.** It cost a task, moved every
   number, and retired a cross-check. **The counterfactual is landing
   `TASK_PHP_017`'s guard clause and keeping the old R1h.** Argue it either way,
   with the evidence — ⚠ and note the rebuild's own best result (§1a) was an
   *accident* of it, which cuts both ways.
3. ⚠ **That `bug49354.py` and `fix_scope.py` do not share an assumption that
   would make them agree for the same wrong reason.** They are the two pillars
   under the R1h choice. **If they share a helper, a fixture or a model, say so.**

---

**Running count: launched from 74.** ⚠ **The last three reviews each refuted
something load-bearing** — a row's headline, four of the manager's claims, and a
protocol rule the manager wrote. **§1 and §5.1 are where I think this one is.**
