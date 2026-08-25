# TASK_091 — close `p28`'s one remaining gap: is `wf` ESTABLISHABLE?

**Role: research engineer (probe).** Not building `p28`. Answering the single
question `TASK_086` left open about it, which it called *"the honest one"*.

Read `.tasks/PROTOCOL.md`, then this file, then `.tasks/TASK_086_REPORT.md`'s
**p28 block**, then `patterns/p27-handle-table/verus.rs` — **p27 already ships
the machinery you need** — and `.memory/04-verus.md`'s `raw_ptr` section.

Scratch in `.temp/t91/` — free, I checked.

---

## ⚠⚠ 0. ANOTHER AGENT IS BUILDING A PATTERN. STAY IN `.temp/t91/`.

`TASK_089` owns `patterns/`, `harness/`, `results/`, `synthesis/`.

- **Do NOT run `harness/check.py` or `harness/measure.py`.**
- **Write NOTHING outside `.temp/t91/`.** Reading anything is fine.
- `./verus_run.py <file.rs>` single-file mode is **concurrency-safe**. **Not
  `--cargo`.**
- 80 cores, near-idle. Build freely.

---

## 1. The question, and why it is the whole risk

`TASK_086` proved **`unlink` preserves `wf`** on an intrusive doubly linked list
over `Ghost<Seq<*mut Node>>` + `Tracked<Map<usize, PointsTo<Node>>>` —
`4 verified, 0 errors`, ~25 lines of ghost proof, **no lemma, no `assume`, no
`external_body`** — which **contradicts the catalogue's standing prediction**
that *"p28/p30 will defeat R5 within budget"*.

⚠ **But it proved PRESERVATION, not ESTABLISHABILITY, and said so:**

> *"There is no constructor in the probe, so nothing discharges `unlink`'s
> `requires`; a 0- or 1-node list satisfies `wf` **vacuously**. Building a
> ≥3-node list needs `raw_ptr::allocate` plus a **disjointness argument for the
> injectivity conjunct**. p27 already ships `allocate`/`deallocate`, so the
> machinery exists — but I did not run it, and this is exactly the reviewer's
> 'is the function dead/vacuous?' check."*

**That is your job. Build the constructor.**

## 2. What to run

In `.temp/t91/`, extend the probe's `v28_dll.rs` (regenerate it from
`.temp/t86/` — ⚠ `ls` it first, do not assume it survived) with:

1. **`new()` / `push_front()`**, or whichever shape reaches a **≥3-node** list,
   using `vstd::raw_ptr::allocate` the way `patterns/p27-handle-table/verus.rs`
   does (`rec_alloc` / `rec_open`). **Report `N verified, M errors` verbatim.**
2. ⚠ **The named hard part is the INJECTIVITY conjunct** — `wf` asserts the node
   addresses are pairwise distinct, and a fresh `allocate` must be proved
   disjoint from every address already in `ptrs`. **If anything stalls, this is
   where.**
3. **Then close the loop:** a `main` that builds a ≥3-node list and calls
   `unlink` on a **middle** node, with `unlink`'s `requires` **discharged by the
   constructor's postcondition alone**. That is what turns the existing 4/0 from
   a vacuous proof into a real one.

⚠⚠ **STATE WHICH BAR YOU MET.** *"`wf` holds after `new()`"* on an empty list is
**vacuous** and is not the answer. **The bar is a ≥3-node list whose `wf`
discharges `unlink`'s precondition at a real call site.**
⚠ **Two vacuity controls this project has already paid for, and you should run
their analogue:** `ensures res ==> P` with a body of `false` verifies `2/0`
(TASK_085); and deleting a **multiset** clause let a body that **zeroes the
array** still satisfy `is_heap` (TASK_090). **Find p28's equivalent — the clause
whose deletion lets a degenerate body pass — and say what it is.**

⚠⚠ **IF IT STALLS, REPORT THE STALL AND STOP.** No `assume`, `admit`,
`external_body` or `assume_specification` beyond what p27 already justifies.
**A measured "the injectivity argument does not close in one session" is a GOOD
deliverable** — it would move p28 down the queue or reshape its contract, and
that is worth knowing before an engineer spends a session, not after.

## 3. If the main question closes, one cheap extra

p28 is ranked **5 and not 2 for exactly one reason: no rung pair was built**, so
it has **no probe 2 and no probe 3**. If time remains, build the two throwaway
kernels and report sizes + md5 **from the LINKED binary** (⚠ a relocated field is
zero in a `.o`, so two kernels differing only in a call target md5 identically
there — `TASK_086` #238, manager-verified), plus marginal whole-program `Ir`.
⚠ **Declare the convention in advance and remember only a SLOPE transfers from a
probe** (`.memory/03-measurement.md`).

## 4. Constraints

- `.temp/t91/` only. **No `/tmp`.** Keep the generator, delete the artefact.
- **Notes in `.temp/t91/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- `.memory/` is manager-only. Report durable facts; do not write them.
- Do not edit `pilot/`. Do not bump the Verus/vstd pin.
- `timeout <N> <cmd>` on anything long. Never `pkill`/`killall`.
- ⚠ **Grep `~/tools/verus/vstd/` — the PINNED vstd** — before saying no spec
  exists, and **grep the INHERENT spelling as well as the free one**.
- Gotchas already paid for: `&mut` postconditions need **`final(v)@`**;
  `broadcast use group_to_multiset_ensures` needs an explicit
  `use vstd::seq_lib::group_to_multiset_ensures;`.

---

⚠ **PROTOCOL rule 2's running count is 256.** **Every agent that has contradicted
the manager with a measurement has been right — 256 times, and the last three
were `TASK_090` on this same class of prediction.** ⚠ **My record on guessing
which Verus obligation stalls is now 0 for 2**: I predicted `p23`'s partition
invariant would be the hard part (it verified **4/0 first attempt**) and
`p24`'s `heapify` loop (it needed **no proof at all** — the content was in
`sift_down`). **So treat my naming of injectivity as the hard part as a weak
prior and tell me where the difficulty actually sits.** Carry **256** forward
incremented by what you find.
