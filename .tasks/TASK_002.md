# TASK_002 — the harness, and p01 as its proving ground

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.memory/` files 00, 01, 02, 03, 05.
`.memory/04-verus.md` when you get to the R5 rung.

## Why

Everything downstream is a clone of what you build here. 47 patterns are queued
(`.memory/06-catalogue.md`); if the template is wrong, all 47 are wrong. Build it
once, properly, and validate it on one real pattern.

`pilot/` is frozen and is **not** the template — it takes data on `argv` (capped at
~50 000 elements), has no `safe_tuned` rung, and has a `requires n < 1000` that
does not cover its own measured inputs. p01 supersedes it.

## Deliverable 1 — shared driver + input format

`common/` per `.memory/05-layout.md`:

- `common/slb.py` — read/write the input format from `.memory/02-bench-rules.md`
  (`u64 n_iters`, `u64 payload_len`, payload).
- `common/driver.c` / `common/driver.h` and `common/driver.rs` — the shared driver.

Driver contract, identical in both languages:

```
usage: <prog> <input-file>
  read the file, call the kernel, fold every result into
  acc = acc.wrapping_mul(31).wrapping_add(result)
  print acc as a decimal u64 and a newline. Nothing else on stdout.
```

### The hard requirement: the benchmark must not evaporate

Calling a pure kernel `n_iters` times on identical data invites LLVM to CSE the
calls and hoist them out of the loop — you would then be timing `printf`. The
mechanism that prevents this **must be identical across all five rungs**, or the
comparison is rigged.

Recommended (use unless you find something better): **thread `acc` into every
kernel call**, so call *i+1* depends on the result of call *i*. A serial
dependency cannot be hoisted or CSE'd, needs no `black_box`, and is expressible
identically in C and Rust. The natural form is to let `acc` select which record
the kernel operates on (`rec = acc % n_records`) — that also defeats prefetch
games and is realistic.

Do **not** reach for `std::hint::black_box` / `__asm__ volatile` as the primary
mechanism: the two are not equally strong barriers, so they would introduce an
asymmetry between the C and Rust rungs. If you end up needing one anyway, say so
loudly and document the asymmetry.

**Prove it worked** by disassembling and showing the loop is real. This is the
single most important thing in this task.

## Deliverable 2 — `harness/`

- **`harness/asm.py`** — owns the canonical extraction/normalisation from
  `.memory/03-measurement.md`. Read that whole section: TASK_001 found three
  defects in the old pipeline and TASK_001_REVIEW found two more in the fix.
  API: extract kernel asm normalised; instruction count **both raw and
  padding-excluded**; **raw machine-code bytes of the kernel symbol**; digests of
  both; diff two binaries' kernels. Everything else calls this — no ad-hoc
  `objdump | sed` anywhere else in the repo.

  **The identity oracle is raw bytes, not normalised text.** The normalisation
  erases every immediate and displacement; a review constructed two kernels with
  different *answers* and the same normalised md5. Any "R5 ≡ R4" claim the harness
  emits must be backed by the raw-byte digest. Normalised text is for reading
  diffs.

  Two known hazards to fix while you are in there: the width-based hex strip eats
  the `fadd` mnemonic, and branch targets under 4 hex digits survive. Make the
  branch-target strip **positional** (operand of a branch), not width-based.
- **`harness/build.py`** — build the matrix from `.memory/01-ladder.md`: 6 cells
  (R1-gcc, R1-clang, R2, R3, R4, R5) × {O0, O3} × {isolated, whole}. Outputs to
  `.temp/build/pNN/`, never into the pattern dir. Must be able to build one cell
  or all. R5 goes through `./verus_run.py`.
- **`harness/check.py`** — the correctness gate. Must:
  1. build every cell,
  2. run each on `small` and `large`, assert **all cells print the same checksum**,
  3. disassemble each kernel and assert it did not collapse — a real loop
     (backward branch) exists and the body exceeds a plausible floor,
  4. run `adversarial` and *record* each rung's behaviour (exit code, stdout,
     stderr, signal) rather than requiring agreement,
  5. **enforce the four "Proof domain must cover the measured domain" rules** in
     `.memory/02-bench-rules.md` — in particular that the R5 kernel has a
     *verified* call site (not one hidden behind `#[verifier::external_body] fn
     main`), and that every measured input satisfies its `requires` and every
     measured output its `ensures`,
  6. exit non-zero with a readable report on any failure.
- **`harness/measure.py`** — static counts + `.text` size + callgrind per-function
  exclusive `Ir` (**never** the whole-program summary — see `.memory/03-measurement.md`)
  + pinned wall clock, into `results/pNN-<slug>.json`. Record toolchain versions
  and the git commit in every JSON.
- **`harness/report.py`** — JSON → markdown tables into `results/tables/`.

Python 3, stdlib only. These are research tools: readable and obvious beats clever.

## Deliverable 3 — `patterns/p01-array-sum/`

The pilot kernel, done properly: file input, all **five** rungs (the pilot has no
`safe_tuned.rs` — write one, e.g. iterator-based), layout per `.memory/05-layout.md`,
with `README.md`, `spec.md`, `inputs/gen.py`, `NOTES.md`.

- `spec.md` fixes the kernel contract every rung implements — signature, semantics,
  and the precondition R5 will prove.
- **R5 must have a verified call site, and its `requires`/`ensures` must cover
  every input the benchmark runs.** The pilot failed both: `main` was
  `external_body` so no precondition was ever discharged, and the published run
  printed a value its `ensures` forbids. Concretely — the driver's call into the
  kernel goes *inside* `verus!` and must verify; only the argument-*reading* helper
  may be `external_body`, and its `ensures` must supply exactly the facts the
  kernel's `requires` needs. Bounds must hold for `small`, `large` **and**
  `adversarial`. Read `.memory/02-bench-rules.md` "Proof domain must cover the
  measured domain" — all four rules — before writing `verus.rs`.
- **R3 is not optional.** The pilot's missing safe-tuned rung caused its headline
  to overstate safe Rust's cost ~3.7×. A ~6-line iterator version was enough to
  close most of the gap.
- `NOTES.md` records the TCB tally per `.memory/04-verus.md` — **every**
  `external_body` item listed individually, not just the interesting one — and any
  proof sticking points.

p01 models no bug (it is the calibration pattern), so its `adversarial` input
should be the degenerate-shape case — `n_iters=0`, empty payload, a length field
larger than the payload — i.e. the inputs that catch a sloppy driver.

## Deliverable 4 — evidence

Run it. In your report:
- `harness/check.py` output, green, for p01.
- The results table for p01 (all 6 cells × O3, at minimum) with static counts,
  padding-excluded counts, md5s, and kernel `Ir`.
- The disassembly evidence that the driver loop survived.
- Confirmation that R2v≡R2 and R5≡R4 by md5 — the structural finding, now on a
  real pattern instead of the toy.

## Constraints

- No root, no `/tmp`, scratch under `.temp/`. **No `git add`/`git commit`.**
- Do not edit `pilot/`.
- Do not touch `PLAN.md` or `pilot/README.md` — the manager owns those.
- If a `.memory/` fact turns out wrong, fix the `.memory/` file and say so.

## Done when

`harness/check.py` is green on p01, the results JSON exists, the table is in your
report, and the anti-collapse mechanism is *demonstrated* by disassembly rather
than asserted.
