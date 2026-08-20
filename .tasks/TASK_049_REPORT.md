# TASK_049 report — p14, field split

**Role:** research engineer. **Status:** delivered; `check.py p14` PASS, complete
run, `failures []`, 30 records 0 STALE. **Not yet reviewed** — every number here
is PROVISIONAL until `TASK_049_REVIEW` lands (PROTOCOL rule 9).

Running count of agents that contradicted the manager with a measurement: **75**.

## §0 — the decision. All four candidates rejected; a fifth ships.

- **The catalogue row ("in-place mutation + aliasing") is EXCLUDED BY THE
  HARNESS, not merely wrong.** A `strtok` that tokenises the driver's payload is
  not a function of its arguments: on a one-window blob the checksum stops
  satisfying `acc(n) = r·Σ31^j` at the first repeat, on **both** compilers
  (`.temp/p14/probe1_repeat.py`). **The mandated per-call scratch copy deletes
  the mutation.** The aliasing half is `rustc` `E0506`/`E0515` — p08's
  compile-time rejection, **no run-time check to price**.
- **Candidate 1 is p11**, built as `k_unbnd`: the omitted line is literally
  `i < m`, the harm is an OOB read, the loop body is p11's `strlen` shape.
- **Candidate 3 (lifetime) rejected, and the manager's stated reason for ranking
  it second is refuted.** It is **not** "observably wrong": at `-O3` both
  compilers print the *correct* answer — p08 exactly. (The `noinline` worry came
  out *better* than predicted: removing `noinline` does not erase the UB.) What
  kills it is that the lifetime bug needs **pointer** descriptors, which safe
  Rust cannot hold and which `as_ptr` / `add` / `from_raw_parts` make
  un-provable — **so R4 would not be a rung.**
- **Candidate 2 kept, but promoted from the bug to its TRIGGER.** Real glibc
  `strtok` collapses runs: `a,,,…,z` is 2 fields against 17. Against a fixed
  table that is a correct parse vs a **stack-buffer-overflow WRITE** on
  byte-identical input. Counterweight shipped: an *alternating* line has no runs
  and gives 33 fields under both.

**Shipped bug: an unbounded FIELD COUNT against a fixed descriptor table.** The
first bound in this project that is a **count of a byte value**, not a length —
and the only candidate that leaves a run-time check on the safe-Rust side, which
was the decision criterion.

## Evidence

```
check.py: PASS   verdict PASS | complete_run True | failures []
contract_sha256 91b88dd8...
verus {'verus.rs': (19 verified, 0 errors, 19 pinned, 6 tcb)}
identity [('O0','norel'), ('O3','exact')]   miri 8/8 runs, 0 blocked   32/32 cells built
--check-stale: 30 record(s) examined, 0 STALE
```

Verus **19/0 on the second attempt, twin 23/0**; per-item decomposition measured
with `--verify-function`. **TCB 6 items / 11 lines = 4 U-license + 2 infra**
under the TASK_048 classification; `scr_load` **verified, not trusted**, from the
start.

Laws — whole-program marginals; **26 published numbers re-verified against the
JSON, 0 mismatches**:

- `c-gcc-h − c-gcc = 1.00·bytes + 2.00·fields − 3.00`, **max residual 0.0000 over
  66 blobs**, **leave-one-length-out worst error 0.0000 over 29 hold-outs**, and
  it predicts both perf rows **out of sample** (+238.00 / +91.00).
- `verus − unsafe = 0.0000` on all 66 sweep blobs and both perf rows.
- **A zero-parameter fold law read off the listing**, predicted forward: worst
  residual **0.0177** over 15 blobs.
- clang `R1h − R1 = +663.00`: mechanism is a **lost 2× unroll plus an un-peeled
  `i == m`**, attributed mnemonic by mnemonic.
- **`4.25 = 2.00 + 2.25` on a fourth kernel**, and the first time both halves
  appear in one listing (R4's epilogue 8.00/byte, its unrolled body 5.75,
  R2 10.00).
- **New axis.** Band `t` holds 480 bytes and 8 lines fixed and moves only the
  field count: the safety tax reads **6.456 → 3.506 Ir per line byte — a 1.84×
  range at constant input size** — and the direction is counter-intuitive (R4
  loses its unroll).
- Three proof mutants, all failing as predicted. **`pm3_msonly` shows memory
  safety alone SUFFICES here, where it did not on p06.** `pm2_weakreq` is a
  **Verus-level** sole catcher — the contract pin also fires (2 clause diffs,
  measured with `check.py`'s own comparator).

## Problems

- ⚠ **I corrupted a full sweep by running two `sweep_ir.py` jobs concurrently**
  on a shared scratch path — byte-identical `unsafe` / `verus` read 3654 and
  11550 Ir/call. Detected; scratch made per-PID; **everything re-measured.**
  This is TASK_026 §0 item 7's rule, and the script now carries the warning.
- `attr.py` first read callgrind's *line number* as the cost and silently
  produced a table of zeros; it now asserts a non-zero total.
- ⚠ **No `ns` claim is published, and the reason is measured.** `verus − unsafe`
  — **byte-identical kernels with exactly equal `Ir`** — differ by **+8.97% /
  +8.91%** in differenced alternating pinned wall clock over two passes,
  *larger than the gcc hardening gap*. **I propose the R4/R5 pair as a free null
  control the project already has and has never used.**

## Unsure / not done

- **No layout population** (`clayout.py` not ported). With no `ns` claim there is
  nothing to defend, but the `win32` / `jcc32` question is **unasked, not
  answered**.
- **clang's hardening law is not solved** — mechanism plus mnemonic table only,
  no closed form.
- `-O0` rows unexplained (R3 is 23% dearer than R2 there and the sign inverts at
  `-O3`); no claim rests on them.
- ⚠ **`spec.md` self-disclosure**: one `required` entry (`flen = i - s;`) was
  added **in response to a gate measurement** (`-O0 identity: differ`). I put
  that in the `why` explicitly rather than let the "written before anything was
  measured" sentence stand as a blanket claim. **A reviewer should judge whether
  the disclosure is adequate.**
- **`c_hcond` and `t_pos` are out of contract** and priced as the declaration's
  cost; whether the declaration should have permitted them is **a judgement I
  made, not a measurement**.
- Did **not** edit `.memory/`, `harness/`, `common/`, `pilot/` or any existing
  pattern.

## Memory updates

**None written** (subagents are forbidden). For the manager to land *after
review*:

1. `.memory/06-catalogue.md` p14 row — bug class is **unbounded field count vs a
   fixed descriptor table**; the guessed row is **excluded by the driver's repeat
   protocol**, measured.
2. `.memory/02-bench-rules.md` threshold table — p14's "not as stated" is
   **settled**: the sentence's mechanism is real and is p11's, so p14 puts its
   bug in the outer loop, and p14 **inherits** the WRITE rule where p06 did not.
3. `.memory/01-ladder.md` finding 9 — the `2.00`-vs-`3.00` discriminator is
   **whether the base is a compile-time-constant frame offset**, not how many
   exit tests the loop has: p14's scan has two and still costs 2.00.
4. `.memory/03-measurement.md` trap 3 — third instance, and the **first inside a
   zero-parameter derivation** (`xchg %ax,%ax`) and the first hiding inside a
   **null coefficient** (`−1.00 nop/line` under `nline = 0.00000`).
5. `.memory/03-measurement.md` — **the R4/R5 identity pair is a free wall-clock
   null control**; 8.97% on p14, 8× the identical-copy floor.
6. `.memory/04-verus.md` — **carry ghost sequences, do not re-derive them**:
   `Seq::new(nt, |k| tl@[k])` needs a prefix lemma per invariant; `Seq::push`
   needs none. The failed draft's error text is in p14 `NOTES.md` §5.
7. `.memory/00-environment.md` / `03` — **per-PID scratch is not optional**: two
   concurrent `sweep_ir.py` runs produce plausible-looking nonsense.
