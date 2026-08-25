# TASK_090 — probe `p24`'s R5 obligation, the queue's cheapest open question

**Role: research engineer (probe).** You are **not** building `p24`. You are
answering the one question `TASK_086` left open about it, which it called
**"the single cheapest thing the next task could add."**

Read `.tasks/PROTOCOL.md`, then this file, then `.tasks/TASK_086_REPORT.md`'s
**p24 block**, then `.memory/04-verus.md`.

Scratch in `.temp/t90/` — free, I checked.

---

## ⚠⚠ 0. ANOTHER AGENT IS BUILDING A PATTERN. STAY IN `.temp/t90/`.

`TASK_089` owns `patterns/`, `harness/`, `results/` and `synthesis/`.

- **Do NOT run `harness/check.py` or `harness/measure.py`.**
- **Write NOTHING outside `.temp/t90/`.** Reading anything is fine.
- `./verus_run.py <file.rs>` **single-file mode is concurrency-safe**
  (`tempfile.mkdtemp()` per invocation). **Do not use `--cargo`.**
- The box has **80 cores** and is near-idle; you are not competing for CPU.

---

## 1. The question

`TASK_086` ranked `p24` (binary heap sift) **fourth**, and put it in the second
tier **for exactly one reason**: it did not probe R5.

Everything else is measured: boundary at R3-vs-R4 on `v[l]`/`v[r]`/`v.swap`;
machine code distinct (`k24_checked` 217 B `8036932e…` vs `k24_unchecked` 138 B
`725b65bb…`); cost **+7.85 `Ir`/element, +22.1%** measured on **heapify, not one
sift** (one sift is `+34.00` and the clone dominates); `::get_unchecked` **0
hits** in the pinned vstd, so the ordinary wrapper route. Harm: **silent at
`gcc -O2`, and only UBSan sees it — ASan did NOT report a heap-buffer-overflow
for the same read.**

**The unprobed obligation, and it is the interesting one:**

> the **heap-order invariant** `∀i: v[i] ≥ v[2i+1] ∧ v[i] ≥ v[2i+2]`
> **re-established after a swap** — a non-bound obligation like `p23`'s, and
> **unlike `p23`'s it is untested.**

## 2. What to run

In `.temp/t90/`, build the smallest Verus file that answers it and **report
`N verified, M errors` verbatim**:

1. **`sift_down` preserving heap order** on a `Vec<u64>`, with the invariant
   above as a `spec fn`, `decreases` on the remaining subtree height or index
   distance, and a postcondition that heap order holds after the call.
2. **If that closes, try `heapify`** — the loop that calls `sift_down` from
   `n/2` down to `0`, whose invariant is *"every node above `i` roots a heap"*.
   **That is the real obligation and it is where I expect it to stall.**

⚠ **Report the bar you met, precisely.** A postcondition that says *"heap order
holds on the subtree rooted at `i`"* is **not** the same as *"heap order holds
on the whole array"*, and a `requires` that assumes what the loop is supposed to
establish is the vacuity a reviewer looks for first.
⚠⚠ **`TASK_085` measured the general form of this trap: `ensures res ==>
valid_utf8(b@)` with a body of `false` verifies `2 verified, 0 errors`.** **State
which direction, and which scope, you proved.**

⚠⚠ **IF IT STALLS, IT STALLS — REPORT THAT AND STOP.** Do **not** reach for
`assume`, `admit`, `external_body` or `assume_specification`. **A measured "the
heapify invariant does not close in one session" is a GOOD deliverable** — it
would move `p24` down the queue or reshape its contract, and that is worth
knowing *before* an engineer spends a session on it, not after.

## 3. Two cheap extras, only if the main question is answered

- **The ASan-vs-UBSan asymmetry.** `TASK_086` measured that ASan did **not**
  report the OOB read that UBSan caught. ⚠ **`p19` just showed that an OOB
  read's loudness is set by the object's STORAGE CLASS** — the same read from
  `.bss` SIGSEGVs and from the heap exits 0. **Is p24's asymmetry the same
  artefact?** Re-run the harm with the array on the heap *and* as a `static`,
  and say.
- **Does the `+7.85 Ir`/element slope survive a residue check?** `TASK_086`
  measured one `n`. ⚠ **Only a slope transfers from a probe**
  (`.memory/03-measurement.md`, landed this task) — so do not re-fit an
  intercept, but **do** check whether the slope moves with `n mod 2` or across a
  power-of-two boundary, since heap arity makes that plausible.

## 4. Constraints

- `.temp/t90/` only. **No `/tmp`.** Keep the generator, delete the artefact.
- **Notes in `.temp/t90/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- `.memory/` is manager-only. Report durable facts; do not write them.
- Do not edit `pilot/`. Do not bump the Verus/vstd pin.
- `timeout <N> <cmd>` on anything long. Never `pkill`/`killall`.
- ⚠ **Grep `~/tools/verus/vstd/` — the PINNED vstd — before saying no spec
  exists.** `../LearnVeri/_VERUS_DOC_/vstd/` is a **different, older snapshot**
  and trusting it produced a false claim that stood 44 tasks. **Grep the
  INHERENT spelling as well as the free one.**
- Two gotchas already paid for by other agents, so you do not pay again:
  postconditions on `&mut` need **`final(v)@`**, not a bare `v@`; and
  `broadcast use group_to_multiset_ensures` needs an explicit
  `use vstd::seq_lib::group_to_multiset_ensures;`.

---

⚠ **PROTOCOL rule 2's running count is 253.** **Every agent that has contradicted
the manager with a measurement has been right — 253 times.** My least-sure calls
here: **(a) that `heapify`'s loop invariant is where this stalls** — `p23`'s
partition invariant was predicted to be the hard part and verified **`4/0` first
attempt**, so my prediction record on this exact kind of guess is poor; and
**(b) that p24's ASan-vs-UBSan asymmetry is p19's storage-class artefact** — a
pattern-match, not a measurement. **Contradict either plainly.** Carry **253**
forward incremented by what you find.
