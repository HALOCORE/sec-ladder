# TASK_033_REVIEW — p11 separates a library difference from a safety cost. Check that it did.

**Role:** research reviewer. You do **not** fix; you report.
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_033.md` (the spec), then
**`patterns/p11-nul-scan/NOTES.md` in full**, then its `spec.md`, `model.py`,
`inputs/gen.py`, `controls/gen_controls.py`, and `.memory/01-ladder.md`'s
"R4 is defined by permission" paragraph.

p11 is built, gate `PASS` on its first complete run, R5 12/0, and **unreviewed** —
per rule 9 none of its findings are in `.memory/`. This review decides what goes
in.

## Start with the trap its own engineer flagged

**`results/tables/p11-nul-scan.md` publishes the kernel-exclusive `Ir` column, and
for four of eight p11 cells that column is wrong** — `strlen`, `memchr` and
`CStr::from_bytes_until_nul` all live outside the `kernel` symbol, so it is off by
up to **9830 Ir/call, 43% of the cell**. Read off it, R3 looks **30% cheaper** than
R4 on `small`; on the whole-program marginal it is **21% dearer**.

The engineer says it nearly published the false version, and that `NOTES.md` §3 is
the correction. **Verify that every published p11 number is the marginal one**, in
`NOTES.md` *and* `README.md`, and that no sentence anywhere reads the wrong column.
This is the highest-probability place for a real defect.

## The claims, in the order I would attack them

1. **`3.00000` Ir/byte, the new constant, and its mechanism.** The headline says
   the *same* bounds check costs 3 per byte in the scan and 2 in the fold, because
   the scan's induction variable is window-relative where the fold's was hoisted
   to blob-absolute. That is a strong mechanistic claim and it is the pattern's
   only genuinely new number. Re-derive it from the listing. Is it the induction
   variable, or is it the loop shape, or the `jae` target? A wrong mechanism in
   `.memory/` is worse than no mechanism — this project has said so twice.
2. **The three-way decomposition — 12.0× library, 5.3× spelling, 3.00 safety.**
   Each factor is a comparison between *different* things (glibc AVX2 vs a SWAR
   fallback; `CStr::from_bytes_until_nul` vs `iter().position()`; checked vs
   unchecked at matched spelling). Only the third is a safety number. **Check the
   matched-spelling discipline held**: is the 3.00000 measured between two rungs
   that scan the same way, or across two different scans? p16's headline was
   sign-wrong for exactly that error.
3. **`4.25000 = 2.00 + 2.25`, claimed as a third reproduction.** p16 and p17
   established it. Is p11's really the same constant with the same split, or a
   coincidence of a similar fold? The claim is that a *rustc property* has now
   been reproduced on three unrelated kernels — which is one of this project's
   better results if it holds. Check the split, not just the total.
4. **`r4_cstr` is rejected with four `is not supported`, worth −35%.** This is the
   largest instance of finding 14 and it will be quoted. Re-run
   `./verus_run.py` on the twin yourself. And ask the harder question the engineer
   left open: **is a hand-written SWAR scan in unsafe Rust admissible?** It needs
   a `u64` load out of `&[u8]`, so `from_le_bytes` / `read_unaligned` / raw
   pointers — all previously rejected — but *likely* is not *measured*, and this
   project has been wrong about likely before.
5. **The `adversarial-zerotail` pair.** The engineer built a control the spec did
   not ask for: two inputs differing in 20 tail bytes, the same inflated `nstr`,
   one overrunning and one not. Does it actually isolate "the sentinel is the
   bound, not the count"? Run both against all eight cells.
6. **The `p = q + 1` removal.** One line (`if q >= len { break; }`) is claimed to
   remove an overflow obligation at zero cost in instructions *and* to be
   semantically the right statement. Check both halves — especially that R4's
   machine code really is unchanged by it.

## The wall-clock work is done; check that it was done right

p11 reports an identical-copy floor of 1.25–4.95%, protocol-insensitivity to 0.04
points, a 31-layout population, an R4-only mode on `small`, and no sign flips with
`P(A>B)` at 0 or 100 in all eight rows. That is the full `.memory/03-measurement.md`
protocol and it is the first pattern to ship it natively. **Spot-check it rather
than re-running it** — one `common/layout/order.py` run and one partition is
enough to say whether the numbers are the numbers.

## Clean negatives are worth as much as findings

PROTOCOL rule 6. For every attack that does not land, say so with the evidence.
And **if the decomposition holds, say that plainly** — "a 12× C win that is a
library difference, a 5.3× Rust-vs-Rust spread, and a 3.00 Ir/byte safety cost"
is the most useful sentence this project could publish about strings, and hedging
it would be its own failure.

## Constraints

No root; no `/tmp` — scratch under `.temp/r33/`, and per constraint 6 delete your
binaries and blobs when you finish, keep scripts and notes. **No `git add`/`git
commit`** — read-only git. Do not edit `pilot/`, `.memory/`, or anything under
`patterns/`. Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`,
valgrind `~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on
PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`; confirm an exact PID's full
command line before any kill. **Measurements in the FOREGROUND, interleaved by
cell.** p11's blobs regenerate from `inputs/gen.py --sweep` (87 blobs, verified
deterministic).

Notes to `.temp/r33/NOTES.md` as you go so you can be resumed.

Report in PROTOCOL's format, severity-ranked, file:line and a concrete failure
scenario per finding. Paste actual command output.

**Contradicting the manager with a measurement is the highest-value thing you can
do.** Forty-three agents have and all forty-three were right. p11's own engineer
refuted two of my prescriptions — my `adversarial-count` does not overrun, and p11
does not need p17's second `requires` — and both refutations improved the pattern.
I have no independent view of its numbers; I am relaying them.
