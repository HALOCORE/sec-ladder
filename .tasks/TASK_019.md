# TASK_019 — make the declaration describe the tree, per language

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_018_REVIEW_REPORT.md`
**in full** (B1, M1, M2, M3 — this task is exactly its findings), then
`.memory/01-ladder.md`'s "named-spelling standard" block, which now carries the
retraction.

## The problem, stated exactly

The tree holds **two incompatible sentences**. The standard — in six hashed
blocks, in `results/tables/*.md`, in `.memory/` — says no shipped cell is out of
contract. The standard *applied* says **4 to 10 are**, depending on whether you
normalise whitespace.

The rescue clause I approved (*"a rung spells the same operands the way its
language forces"*) **does not fire**, and the review proved why: its antecedent
is *"the language cannot express it"*, which is false for the four cells that
matter. Rust **can** spell p02's `src_len`, and a p02 R3 variant that does is
**byte-identical to the shipped cell** (`md5_fn e207ec6c8697…`, same marginal).

## The decision, which is mine — attack it if it is wrong

**The declaration must describe the shipped tree, per language, and matching is
whitespace-normalised.** Three parts:

1. **Normalise whitespace when matching.** Six of the ten literal misses are
   nothing but spacing — `2 + 2*nsuf` declared against `2 + 2 * nsuf` written, in
   all six p17 rungs. Spacing is not a spelling. This is free and obviously
   right; do it first and report the count it fixes.
2. **Make `required` entries per-language where the languages genuinely differ.**
   A single string cannot name a check whose operands are `src_len` in C and
   `src.len()` in Rust. Give each entry the spelling **each language actually
   uses**, e.g.
   `{"c": "len > src_len - (src_off + 2)", "rust": "len > src.len() - (src_off + 2)"}`,
   with a plain string still allowed when one spelling covers every rung.
   Schema change in `check.py` stage `0b`; keep it as dumb as the existing check
   — presence, non-emptiness, hashing, printing. **No semantic checking.**
3. **Delete the cross-language prose clause** from all six `why` blocks. It was
   measured not to fire; leaving it in is a sentence that sounds like a rule and
   is not one.

After this, **every shipped cell must match its own declaration**, and I want
that stated as a *measured* count in the report, not asserted. If any cell still
does not match, the declaration is wrong — fix the declaration, **never the
cell**. No cell source may change in this task.

If you think the right answer is instead to admit that four p02 cells are out of
contract and say so, argue it. That is a coherent position and I would rather
have it argued than assumed away.

## The three defects the review found

1. **M1 — p02's published `+10` is an upper bound too.** p02's `forbidden`
   additive guard builds in Rust (`n_fn 87`), is equally unmatched by the token
   pin (**neither** spelling contains `src_len`), and measures **3.00 Ir/call
   cheaper** than the shipped R3 — 30% of the published `+10`. Only a prose
   adjective excludes it. So p02 joins p16 and p17: **write p02's in-contract
   spelling spread** (`NOTES.md`, the §10a shape), and state `+10` as an upper
   bound with its measured in-contract minimum.
2. **M2 — `patterns/p16-tlv-walk/NOTES.md:188-189` and `:206-208`** still assert
   "the only admissible spelling anybody has measured" and "unestablished",
   **refuted at `:1129-1130` of the same file**. There is no `TASK_018` reference
   between lines 33 and 983. Fix the early text; do not just add another note at
   the bottom, which is how this happened.
3. **M3 — `patterns/p01-array-sum/spec.md:178`**, inside the hashed
   `collapse.note`, still says the loader and environment terms "cancel exactly".
   Refuted and reproduced twice (7292.10 … 7292.22 on the same binary, env length
   only). Correct it; it needs p01's gate re-run anyway.

## Also worth doing while the gates are running

p16's `nrec` coefficients were flagged "3-point fit, do not quote as laws" and
the review **swept them** — 11 `nrec` values × 2 residue classes, 110 marginals,
**zero residual**. Promote them from fits to laws in p16's `NOTES.md`, and record
that the 68 committed blobs *could not* have tested the axis (both bands sit at
`nrec` 2 and 4). Whether p16 should ship sweep inputs that do is a question for
your report, not an action here.

## Done when

Whitespace normalisation lands; the schema takes per-language entries; the dead
clause is gone from all six; **every shipped cell matches its declaration, with
the count measured and pasted**; M1's spread, M2's early text and M3's hashed
note are fixed; all six gates green; `md5_fn` unchanged 28/28. Expect p08's
marginals to drift ≤~0.2 Ir/call — documented, do not chase.

Prose first, gates last: `source_sha256` globs `patterns/*.md`.

## Constraints

No root; no `/tmp` (scratch `.temp/p19/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/` (report durable facts; I land them). You may edit
`harness/check.py` for the schema and the whitespace normalisation, and
`harness/report.py` if the per-language shape needs rendering — nothing else in
`harness/`. **No cell source may change.** Verus only via `./verus_run.py`.
clang `~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Check `git status`
before finishing.

Notes to `.temp/p19/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Twenty-three
agents have contradicted my written instructions and all twenty-three were right;
the last two each refuted a claim I had landed one commit earlier. What I am
least sure of here is **whether a per-language schema is a fix or a retreat** —
it makes the declaration describe the tree, which is honest, but a declaration
that is edited until it matches whatever the rungs happen to say is exactly the
self-certification the mechanism exists to prevent. The distinction I am relying
on is that these edits are forced by *shipped* code that predates the standard,
not by a number anyone wants. Tell me if that distinction does not survive
contact with the work.
