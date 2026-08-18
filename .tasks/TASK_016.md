# TASK_016 — make the declared idiom visible to the gate

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_015_REVIEW_REPORT.md`
**B2 and Part 2** (the argument this task implements), `.memory/01-ladder.md`
**finding 14** and the R3/R4 rung definitions at the top of that file,
`.memory/06-catalogue.md`'s first open cross-cutting issue, and
`.memory/02-bench-rules.md`'s top section (the gate's threat model).

This is the first `harness/` change since the gate-hardening arc closed, and it
is deliberately small.

## Why — and the "could this happen by accident?" test, passed

`.memory/02-bench-rules.md` says a new gate check must first answer *"could this
happen by accident?"* This one has the strongest answer any check in this project
has had: **it already happened, twice, to two different agents, in consecutive
tasks.**

`patterns/p05-index-flatten/spec.md:69-73` forbids `chunks_exact` and a
strength-reduced running row pointer **by name**, in a section titled *"Load-bearing,
do not improve"*, and `spec.md:3-4` says a rung that deviates "is a different
benchmark and its numbers are not comparable". TASK_014_REVIEW measured the
first, TASK_015 measured the second, both reported the result as p05's number,
and **neither cited `spec.md` once**. The manager then landed a retraction of
p05's headline on that basis, which has now had to be retracted in turn.

The root cause is not carelessness. `.memory/01-ladder.md`'s R3 definition
*listed `chunks_exact` as an R3 technique*, so a general file and a pattern file
disagreed, and the general one won twice. That contradiction is now fixed in
prose — but the deeper problem is that **the declaration is invisible to the
gate**: it is prose at line 69, and the hashed `slb-contract` block starts at
line 309, so `contract_sha256` cannot see it.

## What to build

### 1. A required `idiom` key in the `slb-contract` block

```json
"idiom": {
  "required":  ["i*ncol + j written out in every rung, not strength-reduced"],
  "forbidden": ["chunks_exact", "a running row pointer"],
  "why":       "either deletes the flattened index, which IS the pattern; a rung
                that does it is a different benchmark and its numbers are not
                comparable"
}
```

`harness/check.py` must:

- **require the key**, with `required` non-empty and `why` non-empty;
- allow `forbidden` to be **empty** — but only with `why` explaining why nothing
  is excluded. A pattern with no meaningful idiom restriction must be able to
  say so and pass. (`MAX_TWIN_JUSTIFICATIONS` was deleted at TASK_007 precisely
  because it could hard-fail an honest pattern with no route out; do not
  reintroduce that shape.)
- **print the declaration in the verdict output**, so a reviewer reading a run
  sees what was declared without opening `spec.md`;
- and **nothing else**. It must **not** try to check semantically whether a rung
  honours its idiom — grepping `safe_tuned.rs` for `chunks_exact` is exactly the
  check that fails open, and the threat model is honest mistake, not malicious
  author. The value is that the key is hashed: changing a rung's idiom must move
  `contract_sha256`, which is the signal review already knows how to read.

Add a selftest case or two in the same style as the existing ones.

### 2. Retrofit all six patterns

p05 (`spec.md:69-73`) and p17 (`spec.md:125-146`) **already have the prose** —
move it into the JSON block; do not rewrite it. p01, p02, p08 and p16 need one
declaration each, and the material exists: p02's is the `memcpy` idiom named in
its retraction, p16's is the byte fold's unroll, p08's is the `memmove` spelling
and the `SCR` scratch. **If you cannot state a pattern's idiom from what is
already written, say so rather than inventing one** — an invented restriction is
worse than an honest `forbidden: []`.

No cell source changes, so **no measured column may move**. Confirm that: the
`identity` `md5_fn` values must be unchanged in every refreshed record. All six
gates re-run (~12–15 min total on the observed times).

### 3. A spelling-spread section in `NOTES.md`, where spellings exist

Required for **p05, p16 and p17 only** — they have 11, 5 and 3 measured
spellings respectively, in `.temp/p05r3/` and `.temp/review015/`. Tabulate them
with the contract-conformant cell marked and an explicit **"not the headline"**
note. Publish the spread as a result *about method*; the matched pair stays the
number.

Do **not** generate new spellings for p01, p02 or p08 in this task. Record in
`.memory/05-layout.md`'s "Adding a pattern" list — via your report, since you
cannot edit `.memory/` — that the section is mandatory for new patterns.

### 4. Three corrections that ride along

They need the same gate re-runs, so they are free here:

1. `patterns/p08-overlap-move/spec.md:383` says "NOTES.md 7" and means **§9**.
   It is inside the hashed block. Confirmed at review to be the only
   mis-targeted cross-reference in `patterns/` out of 65 checked.
2. **p16's `NOTES.md` R3 constant.** The published "+27 / +77, O(1) per call" is
   `7 + 5·nrec` at `vlen ≡ 0 (mod 4)` and `7 + 7·nrec` otherwise — `O(nrec)`,
   and the two published points are nrec 4 and 10. Swept over 68 blobs at review.
3. **p17's `NOTES.md` R3 constant.** "+32 Ir/call flat" is flat **per byte**, not
   per call; both shipped bands happen to have `nsuf = 3`. Say so, and say that
   p17 ships no sweep inputs — a shipped sweep is its own task, not this one.

## Done when

`check.py` enforces the key with its selftests passing; all six patterns declare
an idiom; all six gate records refreshed, green, with `contract_sha256` moved in
all six and **every `md5_fn` unchanged**; the three spelling-spread sections
written; the three corrections landed. Report the `check.py` diff size — this
should be a small number of lines, and if it is not, stop and tell me why.

## Constraints

No root; no `/tmp` (scratch `.temp/p16idiom/`); **no `git add`/`git commit`**; do
not edit `pilot/` or `.memory/` (report durable facts; I land them). You **may**
edit `harness/check.py` for item 1 — that is the point of this task — but not
`build.py`, `asm.py`, `dloop.py`, `vparse.py`, `measure.py` or `common/`. Verus
only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Check `git status` before finishing.

Notes to `.temp/p16idiom/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Seventeen
agents have contradicted my written instructions and all seventeen were right;
the last two each refuted a headline I had just landed. What I am least sure of
here is **whether the `idiom` key belongs in the contract block at all** rather
than as a separate hashed section — putting it in moves `contract_sha256` for
every pattern, which invalidates the "the contract has not changed since
TASK_013" property that made B2 legible in the first place. If you think a
separate `idiom_sha256` alongside it is better, argue it and build that instead.
