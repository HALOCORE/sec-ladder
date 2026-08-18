# TASK_021 — close the hash gap, then give p05 a floor

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.temp/p20/NOTES.md` (what TASK_020
left), `.memory/02-bench-rules.md`'s residual list (first entry is Part 1),
`.memory/01-ladder.md` finding 6 and the named-spelling-standard block, and
`patterns/p16-tlv-walk/NOTES.md` §10a as the shape Part 3 copies.

## Part 1 — the `source_sha256` generator gap

`source_sha256` globs `harness/*.py`, `common/driver.*` and `patterns/*.md` +
rung sources. It **omits `patterns/*/inputs/gen.py` and `common/slb.py`**. Third
sighting, and it stopped being hygiene at TASK_020: **p16 §10a's swept `nrec`
laws are reproducible only through `gen.py`**, so a generator edit that changed
what the sweep produces would move nothing in any gate artefact — the exact
"stale record is undetectable" failure the hash exists to prevent.

One-line glob fix. It costs a gate round on all six; do it **first** so the rest
of the task rides the same rounds.

While you are there, confirm what else is outside the hash that a claim depends
on. If there is a third file, name it rather than fixing it silently.

## Part 2 — the `idiom_audit` residual

A per-language `required`/`forbidden` entry naming a language the pattern ships
no rung for is **silently dropped**. Unreachable today (all six patterns ship
both languages), which is exactly why it should be closed now rather than when a
pattern first ships one language. Report it, don't just drop it.

## Part 3 — p05's in-contract spelling spread

Three patterns have one; **p05 does not**, and this is the one that matters most.
`.memory/01-ladder.md` finding 6 quotes p05's `6·nrow + 9` as its safety cost,
and every pattern that has been given a floor turned out to have published an
**upper bound**: p16 `+27/+77` → `+19/+45`, p17 `+32` → `−19`, p02 `+10` →
`+6/+5`. Until p05 has a floor, finding 6 is quoting a bound as a number.

Use p16 §10a's shape. **The variants must be in contract** — p05's declaration
forbids `chunks_exact` and the running row pointer, and two earlier tasks
violated exactly that, which is how this whole arc started. Run the new
`idiom_audit` against each variant before measuring it.

Sweep rather than sample: p05's residue modulus is 8 and it ships 144 sweep
blobs. If a law needs an `nrow` axis the committed blobs cannot supply, say so
rather than fitting three points — that mistake has been made twice here.

## Part 4 — p16's variants, if the session allows

Three of p16 §10a's four laws rest on binaries in gitignored `.temp/p18/`. The
input axis ships now; the variants do not. Ship them behind a **committed
generator** under `patterns/p16-tlv-walk/controls/`, the way p08's
`controls/gen_controls.py` does, so the laws are reproducible end to end.

**Drop this if time runs short and say so.** Parts 1–3 are the priority.

## Done when

The hash covers the generators and a generator edit is demonstrated to move a
gate record; the audit residual is closed or reported with a reason; p05 has an
in-contract spread with its measured floor and its published figure restated as
an upper bound; all six gates green; `md5_fn` unchanged 28/28.

Prose first, gates last.

## Constraints

No root; no `/tmp` (scratch `.temp/p21/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. You may edit `harness/check.py`, `harness/report.py`
and any `patterns/*/inputs/gen.py` — nothing else in `harness/`, and **no cell
source may change**. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Check `git status`
before finishing.

Notes to `.temp/p21/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Twenty-five
agents have contradicted my written instructions and all twenty-five were right;
the last one refuted my audit-scope rule with a count and showed that a
correction I had landed was backwards. What I am least sure of here is **Part 3's
premise** — I am assuming p05 will behave like the other three and turn out to
have published an upper bound. If its shipped R3 really is the cheapest
in-contract spelling, that is a *more* interesting result than the other three
put together, and it needs the same care in the other direction: do not stop at
two variants because the first two were not cheaper.
