# TASK_034 — p11's prose owes its review two majors and six minors, and two harness one-liners ride along free

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_033_REVIEW_REPORT.md`
in full** — it is your whole task — then `.memory/04-verus.md`'s new section *"A
proof-enabling program change is not automatically free"* and
`.memory/03-measurement.md`'s new section *"Separate the safety cost from the
LIBRARY cost by naming the routine"*. **Both are already written by the manager
and are the wording to follow rather than re-invent**, as is
`.memory/01-ladder.md` finding 9.

**Your headline survived** — the 12× / 5.3× / 3.00000 decomposition was
re-measured independently and every term is exact, the induction-variable
mechanism is confirmed, and `4.25 = 2.00 + 2.25` is now a third reproduction *by
isolation*. Every number in the report is already measured; **land them rather
than re-deriving them.**

**This is not a new arc.** After it, the next task is a pattern — p03 or p09.

## The two majors

1. **`if q >= len { break; }` is not free, and the corrected version is a better
   result.** `verus.rs:32-34`, `NOTES.md:364` and `unsafe.rs:38` all claim zero
   cost *in instructions*; `c/main.c:29` is the only one that is right (it claims
   zero cost in driver statements and preconditions only). Measured: **1.00000 Ir
   per scanned byte + 3 per string + 1 per call**, `guard = 24·L + 97` at `k=24`,
   zero residual over four string lengths — **8.5% of R4**. Mechanism: the guard
   forces the scan's exit reason into a register (`sete %bpl` exists only for the
   post-loop `test; je`); delete it and the loop falls through and the `sete`
   disappears.
   **Publish the trade, not the retraction.** p17 bought the same fact with a
   second `requires` at **zero instructions**; p11 buys it with a program change
   at **zero preconditions**. Neither is free, and that table is now in
   `.memory/04-verus.md`. Also record where the cost lands: the C rungs do not pay
   it per byte, so of R4's 6.00000 Ir/byte scan **1.00000 is bookkeeping that
   `strlen`/`memchr` get for free** — which qualifies §4c's "the entire difference
   is R4's byte loop, with nothing left over".
   ⚠ **Do not "fix" this by deleting the guard.** It is in `idiom.required` for
   all six rungs, every cell pays it, and it does not contaminate the 3.00000
   (without it the loops are 8 and 5; the difference is `lea; cmp; jae` either
   way). The defect is the word "free", not the line.

2. **The `adversarial-count` / `zerotail` pair differs in 33 bytes, not 20.**
   `NOTES.md:556-558` and `inputs/gen.py:252` describe it as "identical first
   three strings … 20 tail bytes and nothing else". The three strings share
   lengths and terminator positions but **not** their bytes, because `gen.py:341`
   and `:347` each call `strings(rng, …)` on the same sequentially-advancing RNG.
   **Fix the generator** (build `body` once and reuse it) so the sentence becomes
   true, rather than weakening the sentence — the controlled pair is worth having.
   Regenerating changes those two blobs, so **re-verify the adversarial table and
   the ASan rows**, and note that `inputs/*.bin` is gitignored so only `gen.py`
   ships.

## The minors

3. **`NOTES.md:85`** puts R1h's `memchr` on `strlen`'s 0.078125 row. Measured
   **0.1023 Ir/byte**, 31% dearer, because `memchr` must also test its count —
   which §3(3) already says in prose. Both are AVX2; the qualitative claim stands.
4. **Stale line citations, all +2**, from a `verus.rs` edit made after the logs
   were pasted: `NOTES.md:471` (252→254), `:500` (333→335), `:525` (346→348),
   `:382` (`external_body` 202/251/263 → 204/253/265), and `NOTES.md:546` +
   `README.md:63` (ASan frame `kernel.c:65` → `:68`).
5. **`NOTES.md:846-849`** says four `(loop, property)` pairs separate the
   population; `analyze.py` reports **seven**, in two opposite orientations. The
   conclusion is *strengthened*, so say seven.
6. **`NOTES.md:291-292`'s `−6.00000` / `−3.75000` are fitted, not read off a
   listing** — against this file's own opening rule. Per residue class they are
   −5.99563…−6.00219 and −3.74563…−3.75219. The claim is true and corroborated to
   0.04%; present it as a fit corroborating a listing count, not as a
   five-decimal measurement. Same section's c-gcc intercept range "−60 … −170" is
   really +39 … −170.
7. **`NOTES.md:419-421`** — a **hashed** `SLB-TRUSTED-ARGUMENT` clause — says the
   token `slb_twin` occurs in the file exactly once. It occurs twice (line 233 is
   a comment, 235 the attribute). A comment cannot change codegen, so argument (c)
   survives; the count does not.
8. **`NOTES.md` §10b** can retire "*likely* is not *measured*": the SWAR R4 twin
   was built and gives `from_le_bytes is not supported`, and `from_le_bytes` is
   *separately* forbidden by p11's own `idiom.forbidden[1]`. All three routes
   closed by measurement.

## The two harness one-liners — they ride along free because all eight gates re-run anyway

9. **`harness/report.py:483` tells every reader to use the wrong column.** The
   generated boilerplate says *"Use the `isolated` kernel-exclusive figure, which
   needs no correction."* On p11 that column is off by **9830 Ir/call and inverts
   the R3-vs-R4 sign**; it is false on **p02** too. Replace it with guidance that
   is true for both cases: the kernel-exclusive figure is the one to use **when
   every rung calls the same routines**, and the whole-program marginal is
   required when they do not — with a pointer to the pattern's `NOTES.md` for
   which convention that pattern publishes.
10. **`harness/asm.py::is_bulk_symbol` knows `mem*` and not `str*`.** `strlen`,
    `strnlen`, `__strlen_chk` all return `False`; `memchr` returns `True`. Harmless
    on p11 (its kernels keep a fold loop so stage 3a's back-edge alternative
    fires), but **a kernel that is only a `strlen` would have neither a back edge
    nor a recognised bulk call and stage 3a would fail a healthy cell** — the exact
    false-failure the bulk alternative exists to prevent. Add the `str*` family
    including the `_chk` forms, and **add selftest cases** — `asm.py` has 20 for
    the `mem*` family and they are the model.

## Done when

Items 1–10 land. **All eight gates green** (`report.py` and `asm.py` are in every
pattern's `source_sha256`); `md5_fn` unchanged everywhere; **all eight tables
regenerated** with `harness/report.py`. p11's two regenerated blobs re-verified
against `model.py` and ASan.

Expect the documented churn class only (`.memory/03-measurement.md`): ASan PIDs —
note that a gate record **can never** reproduce byte-identically for the 6 of 8
patterns that carry an ASan diagnostic — p05's two nondeterministic
`adversarial-dims` stdouts, and p08's `marginal_ir_per_call` jitter, whose
recorded series is now **8 → 23 → 75 → 0**: quote the magnitude, budget 0…75,
re-measure the count.

## Constraints

No root; no `/tmp` (scratch `.temp/p34/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. **`harness/` is in scope for exactly items 9 and 10
and nothing else** — no other logic, no rung source, and **do not delete p11's
guard**. Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; confirm an exact PID's full command
line before any kill. **Measurements in the FOREGROUND, interleaved by cell.**
Delete your binaries and blobs when the gates are green; keep scripts and notes.

Notes to `.temp/p34/NOTES.md` as you go. The reviewer's scratch is `.temp/r33/`
with working probes (`marginal.py`, `ctrl_marginal.py`, `u_noqguard.rs`,
`r4_swar_twin.rs`) — **reuse rather than rebuild**.

**If a prescription here is wrong, say so with the measurement.** Forty-four
agents have contradicted the manager and all forty-four were right — you were two
of them on p11 alone. What I am least sure of is **item 9's replacement wording**:
I do not know whether "same routines in every rung" is a condition an author can
actually check without disassembling, and if it is not, the boilerplate should
probably just say "see this pattern's `NOTES.md` §3" and stop giving advice it
cannot justify.
