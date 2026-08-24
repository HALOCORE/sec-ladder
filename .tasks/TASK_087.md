# TASK_087 — build `p19`, the protocol state machine

**Role: research engineer.** Build the pattern. Read `.tasks/PROTOCOL.md` first
(especially **Definition of done**, and **rule 6** — record the `slb-contract`
sha256 *before building any cell*), then this file, then
`.tasks/TASK_086_REPORT.md`'s **p19 block** (the probes that selected it), then
`.tasks/TASK_026.md` §0 — **if you read only one thing after PROTOCOL, read
that**: every pattern built after it needed only prose corrections, and every
pattern built before it needed re-measurement.

`patterns/p01-array-sum/` is the template every later pattern clones. Scratch in
`.temp/t87/` — free, I checked.

---

## ⚠ 0. Another agent may be working. It stays out of `patterns/`, `harness/`,
`results/` and `synthesis/`.

You own those. **You may and must run `harness/check.py p19`.** Do not run a
full 22-pattern sweep — you are adding a pattern, not changing the harness.

---

## 1. Why `p19`, and what is already measured

`TASK_086` probed 11 catalogue rows and ranked `p19` **first**. All four probes
pass and every number below was **run**, on throwaway kernels, whole-program
marginal `Ir`, `-O3`, **inline mode `isolated`**:

- **Two rung boundaries, and the second is the interesting one.** R3-vs-R4
  *and* **inside the safe class** — `table[st*256+b]` against
  `table[(st&7)*256+b]`. **That is p47's shape** (a boundary that is not
  safe-vs-unsafe), and p47 is one of only two patterns that have one.
- **The cost is a per-byte SLOPE, not a level**: naive **+5.25 `Ir`/byte**,
  2-D rows **+4.25**, masked **+0.999**, all against the same R4.
- ⚠ **The mechanism is worth more than the numbers and you should confirm it
  first:** the checked kernel is **76 bytes against the unchecked one's 173**
  and executes **1.91× the instructions**. `cmp $0x8,%r9 / jae <panic>` sits
  **inside** the loop because `st` is **loop-carried and data-dependent**, so it
  cannot be hoisted, and the exit edge **blocks unrolling**; the panic body is
  out of line, which is why *smaller code runs more instructions*. **The masked
  rung is 4× unrolled with exactly one extra `and $0x7` per byte, and +0.999 is
  that one instruction.**
- **The harm is adversarial-only and real:** `gcc -O2` **exit 139 SIGSEGV**;
  ASan/UBSan `index 200 out of bounds for type 'uint8_t [8][256]'`; the
  non-adversarial run is clean 18/18 on both.
- **vstd:** `::get_unchecked` → **0 hits** in the pinned vstd, so p19 takes the
  ordinary `external_body` route and the twin (`table[i]`) is writable.
  **p19 is NOT blocked by `_scan_unsafe_sites`** the way `p15` and `p35` are.

⚠ **All of that is from throwaway kernels and NONE of it has been through
`check.py`.** Treat it as a well-supported prior, not as p19's numbers.

---

## 2. ⚠⚠ THE FIRST DELIVERABLE IS THE BUG CLASS, AND IT IS ALSO THE KILL RISK

**Settle the bug class before building any cell.** It has been overturned on
four patterns and upheld on two, and `p19`'s is the one the probe itself flagged:

> ⚠ **The memory-unsafe framing may be contrived.** A textbook "state
> confusion" CVE is a **logic** bug with no out-of-bounds access at all. The
> harm as probed needs a **table entry naming a state that does not exist**. If
> the honest spec turns out to be the logic-bug shape, **the row loses its rung
> boundary and dies `p31`'s death** — and `p31` was refused for exactly that:
> *"no rung differed."*

**So §0 of your `NOTES.md` answers, with runs:** is a real protocol decoder's
state index plausibly attacker-reachable out of range, or is that shape
manufactured? **Look at how the state is derived from the byte stream.** If you
conclude the framing is contrived, ⚠ **REFUSE THE ROW AND SAY SO** — that is a
fully acceptable outcome here; four rows have been refused and every refusal was
the right call.

⚠ **State the bug class as the tree's THIRTEENTH `index >= len` and say so up
front, the way p36 said it was the twelfth.** **Twelve BUILT patterns carry that
class** (TASK_086 #240 corrected an earlier count of fourteen, which had counted
two refused rows). Its nearest sibling is **p36** (index out of a dispatch
table). ⚠ **A thirteenth is not disqualifying** — p36 shipped the twelfth and was
worth building — **but the row must name it rather than let a reader discover
it.**

✅ **What is NOT p09's, and this is the part worth defending:** the masked rung
is **p09's `q & 31` used as the FIX rather than as the bug**, and the three-way
behaviour matrix — **panic / silent-remap / OOB** — is not p09's.

---

## 3. ⚠⚠ SEARCH BOTH SIDES. A DIFFERENCE IS ONLY AS HONEST AS ITS WEAKER-SEARCHED ENDPOINT.

This is the trap that keeps firing and it has now caught **five** patterns.

- p10 published *"safe Rust cheaper than unsafe"*: 60% was an **unsearched R4
  side**. p27 repeated it one pattern later. p38 made it four (`+21/+25`
  published against a true `+24/+32`). **p22 made it five and widest — `+2.00`
  published against `+125/+1021`, 510×.**
- ⚠⚠ **And then p36 fell into the MIRROR IMAGE, which is the newer lesson: it
  searched R4 properly and left R3 with ONE lever, which moved R3 the wrong
  way.** Published `R3 − R4 = +15.00 flat`; the review's first in-contract R3
  respelling made it **+7**, and **+2** against the cheapest R4.

**So: count the levers on each side, say whether they are comparable, and
publish the count.** `p19` has an obvious R3 lever family (the `masked` /
`rows` / `naive` spellings the probe already measured) — **that is a starting
point, not a search.** Ask what **both** rungs' spellings are worth before
publishing any difference.

⚠ **`p41` died in this task's own selection probe for exactly this**: an
apparent 9.6× that was **100% R3 spelling**, and the tuned safe rung actually
**beat** the unsafe one by 17 `Ir`/call.

---

## 4. Deliverables

Clone p01's structure. Everything in `patterns/p19-<slug>/`:

1. **`spec.md`** — prose contract, then the ```slb-contract``` block with the
   pins the gate enforces (obligation count, every `requires`/`ensures`, the
   driver loop, the `Ir` floor, `identity` levels, Miri policy, and the `idiom`
   object). ⚠ **PROTOCOL rule 6: record the block's sha256 in `NOTES.md` the
   moment you first write it, before building any cell**, with the words *"as
   first written, before any measurement"*. ⚠ **`git show HEAD: | diff` is
   VACUOUS on a new pattern** — it compares worktree to HEAD, a pattern lands in
   one commit, so on a clean tree it always prints nothing and always looks like
   it passed. **Say in `NOTES.md` that the diff is unavailable and why; the
   recorded hash is the only evidence.**
2. **`model.py`** — the independent Python reference implementation the gate
   drives over every input. **Mandatory.**
3. **`inputs/gen.py`** — deterministic generation, blobs gitignored. Include a
   **sweep band** so the per-byte slope is derivable from committed inputs and a
   hashed generator, not from uncommitted ones. **Regenerate twice and diff** for
   determinism.
4. **The rungs** — `c/kernel.c`, `c/kernel_hardened.c` (**R1h: ship it, this
   pattern models a bug** — without it *"C is faster"* and *"C is unsafe"* are
   the same sentence), `c/main.c`, `safe_naive.rs`, `safe_tuned.rs`,
   `unsafe.rs`, `verus.rs`.
5. **`README.md`** and **`NOTES.md`** (per-rung findings, proof sticking points,
   TCB tally — **recount it, do not copy it**).
6. **`harness/check.py p19` GREEN.**

---

## 5. Rules that govern the numbers

- ⚠ **Name the INLINE MODE at every figure.** p10 fitted both and the regressors
  **swapped**.
- ⚠ **A law owes its DOMAIN** — usually *missing columns*, not a caveat.
  **Additivity extrapolation is the only out-of-sample test here that can fail,
  and it HAS failed once**, on p38, **100% attributable to three missing
  columns, none of them the one named.**
- ⚠ **Check the RESIDUE CLASS of any parameter your bands hold constant.** Two
  of p38's three bands sat at `nw ≡ 0 (mod 8)` and the third did not — fits in
  sample, misses out of it, with no in-sample residual to warn you.
- ⚠ **Never publish a "minimum".** Write **"cheapest found"** and **name the
  input** — on p03 and p16 the cheapest spelling changes with it.
- ⚠ **Do not publish a pair interval.** Both this project ever published were
  built from R4s that are not rungs.
- ⚠ **If you extract kernel bytes to compare rungs, do it on the LINKED
  binary** — `TASK_086` #238, manager-verified: a relocated field is **zero** in
  an object file, so two kernels differing only in a call target **md5
  identically** there. In a `.o`, extract per **section**
  (`objcopy --only-section=`), never by address.
- ⚠⚠ **STATE NOVELTY CLAIMS AS QUESTIONS TO BE MEASURED.** *"The first
  termination proof in the project"* was a manager sentence in a task file; it
  was **false**, the engineer had no reason to doubt it, and it shipped into
  **eight places, two inside `contract_sha256`**. **Rule 9 protects `.memory/`
  from unreviewed findings and protects NOTHING from a task file.**

---

## 6. Constraints

- Scratch under `.temp/t87/` only. **No `/tmp`.** Keep the generator, delete the
  artefact.
- **Notes in `.temp/t87/NOTES.md` as you go** — agents here die to transient API
  errors; the ones who kept notes lost nothing.
- **No `git add` / `git commit`.** Read-only git is fine.
- `.memory/` is manager-only. Put durable facts in your report; the manager
  lands them **after** the review (rule 9).
- Do not edit `pilot/`. Do not bump the Verus/vstd pin.
- ⚠ **Do not touch `harness/build.py` or `harness/asm.py`** — they are
  **MEASUREMENT**-hashed, and an edit costs a full 43-minute re-measure of 17
  records rather than a gate re-run.
- `timeout <N> <cmd>` on anything long. Never `pkill`/`killall`.
- ⚠ **Cite `check.py` by FUNCTION NAME, never `check.py:NNNN`.**
  `.memory/02-bench-rules.md`: *"Line citations into `check.py` decay"* — 5 of 9
  in the authoritative layer pointed at the wrong code when audited, and the
  *"line as a hint"* compromise failed inside one session. ⚠ **The manager's own
  `TASK_084.md` violated this and the habit propagated into a shipped hashed
  `spec.md`. Do not copy it.**

---

⚠ **PROTOCOL rule 2's running count is 241.** **Every agent that has
contradicted the manager with a measurement has been right — 241 times.** The
calls I am least sure of here, by name: **(a) that p19's memory-unsafe framing
is not contrived** — §2, and it is the kill risk; **(b) that the
inside-the-safe-class boundary (`st*256+b` vs `(st&7)*256+b`) is a rung
distinction and not two different programs** — if the masked spelling changes
what the kernel *computes* on an out-of-range state, it is not a rung, it is a
different benchmark; and **(c) that `+0.999 Ir/byte` really is the one `and`
instruction** rather than an unrolling artefact that happens to land near 1.
**Measure all three and contradict me plainly if they do not hold.** Carry
**241** forward incremented by what you find.
