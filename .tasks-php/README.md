# `.tasks-php/` — task files for the PHP programme

Mirrors `.tasks/` exactly. **`.tasks/PROTOCOL.md` is the protocol and is reused
unchanged** — roles, the manager's own rules, the definition of done and the
reviewer checklist are programme-independent. `PROTOCOL_PHP.md` (a Phase 0
deliverable, not yet written) will be an **addendum** carrying only what is new
here: extraction tiers, provenance, the allocator shim.

## Naming

| | |
|---|---|
| spec | `TASK_PHP_NNN.md` — written by the manager **before** the agent starts |
| report | `TASK_PHP_NNN_REPORT.md` — the agent's return message, landed by the manager |
| review | `TASK_PHP_NNN_REVIEW.md` / `_REVIEW_REPORT.md` |

⚠ **`PROTOCOL.md` rule 10: write the report file BEFORE citing it.** A
subagent's report exists only in its return message; if the manager lands the
corrections and moves on, the `_REPORT.md` everything now points at was never
created. Check before every commit that cites one:

```sh
grep -rho '\.tasks-php/TASK_PHP_[A-Za-z0-9_]*\.md' .memory-php/ .tasks-php/ RECAP_PHP.md PLAN_PHP.md \
  | sort -u | while read p; do [ -e "$p" ] || echo "MISSING: $p"; done
```

## Sibling directory convention

`.tasks-php/` is dotted and `results-php/` is not — **because `.tasks/` is dotted
and `results/` is not.** The point of the mirror is auditability, so the php
tree matches the PAT tree name for name rather than being internally tidy.

## The running count

`PROTOCOL.md` rule 2's *"number of times an agent refuted the manager with a
measurement"* is a **rigour signal, not a ledger**. The PAT programme's stands at
≈965. **This programme starts its own count at 0** — they measure different
things and must never be added together. It lives in the closing paragraph of
the newest `TASK_PHP_NNN*.md` and **nowhere else**; two copies have already gone
stale on the PAT side.

⚠ Under concurrency each task file states the count **it was launched from**;
the manager reconciles once, at the commit that lands them.
