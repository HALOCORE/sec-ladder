# TASK_039 — p09 is holding the weaker example, and its `forbidden` list audits nothing

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_038_REVIEW_REPORT.md`
in full** — it is your whole task — then `.memory/01-ladder.md` **finding 11
(p09)**, `.memory/03-measurement.md`'s new *"`measure.py`'s `ns` column is a
whole-process LEVEL"* section, and `.memory/02-bench-rules.md`'s new backticking
paragraph. **All three are already written by the manager and are the wording to
follow rather than re-invent.**

**Your invisibility claim survived four vacuity attacks and is confirmed.** What
follows is the prose around it — and the pattern is currently shipping a weaker
example than the one it found.

## The blocker

1. **Lead with `q >> 7`, not `q & 31`.** `q >> 7` = `q/128 ≤ q/64`, so under
   `q < nbits` it is **always a legal word index**: `m_shift7_msonly` **19/0**,
   `m_shift7_spec2` **20/0**. Edit distance **1**, in the *same position* as
   `q >> 5`. **Zero instruction cost** (6691.70 vs 6692.30), identical `n_fn`
   (102), guarded body identical **but for one immediate**. Silent under ASan and
   UBSan at the gate's own flags on every input; Miri `exit=0 UB=0`; all five
   builds print the same wrong `3393155352413092229`.
   **The sentence to publish**: `q >> 5` and `q >> 7` differ in one character in
   one position — the first is caught by memory safety alone on every input, the
   second by nothing at all.
   `q & 31` is a **two**-character edit costing **+32% on R4**, so "two
   one-character bugs" (`NOTES.md:21,906`, `spec.md:211,346`, `README.md:56`) is
   wrong on both counts. Keep `q & 31` as the *second* example with its real cost;
   **ship `m_shift7*` and `x_shift7*` in `controls/gen_controls.py`** so the
   headline is re-derivable.
   `spec.md:116-121,346,389` are inside the hashed block — `contract_sha256` will
   move, which is expected.

## The majors

2. **The obligation that fires is `load_u64`'s, a VERIFIED item's — not the
   trusted accessor's.** `NOTES.md:576` annotates it `<- the ACCESSOR's`; the
   error points at `verus.rs:427`. Deleting `buf_get_unchecked`'s `requires`
   changes nothing (18/0→18/0, 19/0→19/0, 17/1→17/1); delete the *decoders'* and
   it fires inside them, so the trusted clause is **shadowed, not dead**. p09 is
   the only pattern with decoder wrappers carrying their own `requires` — **this
   is the first time the memory-safety obligation sits outside the TCB boundary,
   and it is a better result than the one you shipped.** Fix `NOTES.md:576,600,909`,
   `spec.md:118`, `README.md:62` and the hashed `spec.md:346`.
3. **The ILP mechanism is refuted for R3.** `NOTES.md:362-368` / `README.md:84-86`
   read a 2–4× `Ir`-vs-`ns` gap as instructions retiring cheaply. Corrected by
   differencing against `n_iters = 1`, **R3's `ns` penalty EXCEEDS its `Ir`
   penalty** (+215.4% vs +205.6% on `small`); it survives for R2 only at 1.2–1.5×.
   Republish p09's `ns` rows in the corrected form, **label the raw ones "includes
   the per-process constant"**, and carry the caveat that the correction subtracts
   two noisy minima (R5−R4 reads +2.7% where it must be 0 — quote it only where
   the effect is 25–80× that, as p09's R2/R3 are).
4. **`NOTES.md:294-302`'s merge mechanism is wrong, and the true one is better.**
   R2 *does* merge the eight byte loads on the shift-derived access; the merge
   fails in exactly **one** of eight loops — **reslice + a data-derived index + a
   multi-byte decode at it** — and that single failure is the whole R3 > R2
   inversion: `+21` lost merge, `+1` spill, `−5` cheaper query checks = `+17` net.
   Ship the 2×2 table. And say what it means for §8: **half of the `m_clampb`
   seeding win is the restored load idiom, not deleted checks** (82→40 = −20
   checks, −21 merge, −1 spill).
5. **`q & 31`'s R4 cost is the same mechanism** (`NOTES.md:623-630`) — there is no
   `and`. It lets LLVM prove the tested bit is in the low 32 bits, so it **narrows
   the load** and the merged 8-byte `mov` splits into 4+2+1+1 with a 32-bit `bt`.
   Saying so **unifies p09's two cost stories** instead of leaving them unrelated.
6. **TCB is 7 lines / 4 items**, per the gate's own `tcb_items`
   (`buf_get_unchecked 1, popcount64 1, load_input 4, emit 1`). `NOTES.md:431-433`
   and `README.md:99` say 12 with a per-item column matching no item but
   `load_input`. **Every other pattern's declared figure equals its gate total
   exactly** — p09 has the *second-smallest* TCB here, not one of the largest.
7. **Backtick every `forbidden` and `required` entry.** `check.py:929` audits only
   backticked tokens, so p09's five bare-string `forbidden` entries are audited
   **zero** times while the verdict line still reports "5 forbidden spelling(s)".
   Its "forbidden: 0 hits" was kept **by auditing nothing**.
   ⚠ **Backticking makes the audit real, so run it and report what fires.** The
   reviewer checked that `spelling_matches('q / 64', verus.rs)` is `False` as
   shipped — but that is the *matcher*, not the audit, and `_blank_ghost` does not
   blank `spec fn` bodies. **If the audit now fires on p09's own `verus.rs`, do
   not respell the spec to dodge it — report it**, because that is a real gate
   defect and the manager owns whether it is fixed in `harness/`.

## The minor

8. **`m_clampb_lo` is explained** (`NOTES.md:747-751`, "unexplained"). LLVM does
   not delete the 8th byte's check; it **fuses it into the clamp** with a
   three-way split — `cmp ; ja <return 0> ; jb <loop top>`, `==` falling through
   to the panic block. Zero extra hot instructions (both bodies 40); +3 static for
   the landing block; the −1.00 Ir is one `mov` in `m_clampb`'s *prologue*. **So
   p03's "one past the invariant" control does separate here** — by 3 static and 0
   dynamic, because the extra obligation rides a branch that was already there.

## Done when

Items 1–8 land; `check.py p09` green; `md5_fn` unchanged; the table regenerated;
`harness/measure.py --check-stale` clean. `contract_sha256` moves (items 1, 2, 7).

## Constraints

No root; no `/tmp` (scratch `.temp/p39/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. **Prose and `patterns/p09-bitset/controls/*.py` only
— nothing in `harness/`, no rung source.** Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`.
**No `nohup … &` background jobs** — one reported exit 0 after 1 of 8 cells on
this pattern. **Measurements in the FOREGROUND, interleaved by cell.**

The reviewer's scratch is `.temp/r38/` with 19 Verus probes, 5 exec controls and
`wall.py` — **reuse rather than rebuild**. Notes to `.temp/p39/NOTES.md`.

**If a prescription here is wrong, say so with the measurement.** Fifty agents
have contradicted the manager and all fifty were right. What I am least sure of is
**item 1's finality**: `q >> 7` beat `q & 31` on every axis and was found by
looking one step past the first answer. **Look one step further before writing it
down** — is there an index edit that is invisible *and* changes the answer on
`small` (p09's headline blob) rather than only on thin windows? If so it is
sharper still, and I would rather have it now.
