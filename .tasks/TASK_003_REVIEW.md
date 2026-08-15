# TASK_003_REVIEW — can you still get past the hardened gate?

**Role:** research reviewer
**Read first:** `.tasks/PROTOCOL.md`, `.tasks/TASK_003.md`, `.tasks/TASK_002_REVIEW.md`
(the six bypasses that were fixed), then the new code.

The gate now catches all six previously-demonstrated bypasses. **Do not spend your
budget replaying those** — spot-check one or two cheaply and put your effort into
the three things below.

## Priority 1 — find bypass number seven

The gate grew two hand-rolled parsers (`harness/vparse.py`, `harness/dloop.py`)
and a pin-based trust model. Hand-rolled parsers are where bypasses live. Invent
**new** attacks. Angles, not a limit:

- **`vparse.py`**: raw strings (`r#"..."#`), nested block comments (Rust allows
  them), `//` inside a string, deeper `cfg_attr` nesting, macro-generated items,
  attributes on `mod`, a second `fn main`, `#[path]` includes, a `verus!` token
  inside a string literal. Can you hide an `external_body`, or make a real item
  invisible to the TCB inventory?
- **`dloop.py`**: it strips non-call parentheses by design. What *else* vanishes?
  Try reordering independent statements, a cast-width change, swapping
  `wrapping_mul` for `*` in a release build, or aliasing two genuinely different
  variables to one canonical name via `spec.md`'s alias table.
- **`check.py`**: can a pattern pass with a rung silently missing, or a stale
  binary? Can a `model.py` agree *by construction* — e.g. by re-deriving the
  checksum the same wrong way the rungs do, or by calling into the built binary?

For anything you get past, give the exact mutation and the green output.

## Priority 2 — the pin model may be self-certifying

**This is the most important question in the review.** The gate moved trust out of
the code and into `spec.md` — a file the same author writes. Ask:

- What stops someone weakening the *pin* instead of the code? If a pattern author
  lowers `collapse.min_marginal_ir_per_call` to 0, weakens a pinned `requires`,
  drops an item from the pinned TCB list, or adds a permissive driver alias, does
  anything object?
- Is `verus.obligations` tied to anything real, or is it whatever the author last
  measured? A pin that is regenerated from the code it is meant to constrain is
  decoration — the same failure mode as the `ensures` that verified for free.
- Concretely: is there a defensible design where some pins are *derived* rather
  than *declared*? Recommend one, or argue the declared model is fine and say what
  makes it safe.

Then re-derive the pins the engineer admits it measured rather than derived:

- The obligation count 5 — what are the five obligations?
- The identity pins, under both digest conventions.
- The collapse floor is pinned at **400** while the measured minimum across 28
  cells is **915**. Defensible, arbitrary, or too loose to catch anything? What
  would a principled floor be?
- `verus --verify-function main --verify-root` reports **2 verified** for one
  function and nobody chased why. Find out. If the second obligation is something
  incidental, the "≥1 means it has a verified body" heuristic is weaker than it looks.

## Priority 3 — does the gate now produce false failures?

A gate that cries wolf gets switched off.

- Would a **legitimate** pattern fail? Specifically one where R4 and R5 are
  genuinely *not* byte-identical — which is expected for any non-trivial proof.
  `.memory/02-bench-rules.md` says that must be recorded as a finding, not a gap.
  Trace the code path and confirm it is.
- Miri cannot be installed for the pinned toolchain, and policy makes it mandatory
  when R4≠R5. So **the first interesting pattern fails the gate on a tool we do not
  have.** Is that the right failure mode? Recommend what should happen instead.
- `--skip` and `--no-callgrind` now hard-fail. Is there a legitimate fast-iteration
  path left for someone developing a new pattern, or will people route around the
  gate entirely?

## Also

- Name the **specific** assumptions in `harness/` that p02 (a length-prefixed
  buffer copy with an attacker-controlled length, a real OOB-write bug, and an
  adversarial input that actually exercises the kernel) will break. Genericity is
  currently argued from code structure, never exercised.
- `results/gate/` is a new committed artefact — should it be, or gitignored?
- The barrier was **not** swapped to multiply-shift (deferred as re-measurement).
  Agree or disagree; say what deferring costs.
- Scope/hygiene: nothing staged or committed; `pilot/`, `PLAN.md`,
  `pilot/README.md` untouched; `.memory/` edits accurate and not overreaching.

## Deliverable

Findings ranked `blocker`/`major`/`minor` with file:line and a concrete failure
scenario, plus the explicit "verified correct" list. **A new bypass, or a sound
argument that the pin model is self-certifying, is worth more than ten style
notes.** Do not fix anything.
