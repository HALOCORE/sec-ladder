# TASK_026_REVIEW — p07 claims the first counterexample to "safety is cheap"

**Role:** research reviewer. You do **not** fix; you report.
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_026.md` (the spec —
including its `§0` addendum), then **`patterns/p07-binary-search/NOTES.md` in
full**, then its `spec.md`, `model.py`, `inputs/gen.py` and
`controls/gen_controls.py`.

## Why this one matters more than the last four reviews

Six patterns have said *safety is cheap*. **Every one of them is a linear fold**,
so a per-call safety constant divided by `n` bytes goes to zero — which may be
why that answer kept coming out. p07 has `Θ(log n)` probes and **no inner loop to
amortise over**, and it reports that R3's share of kernel `Ir` **rises
monotonically with `n`**, 42.53% → 46.63% over `n` = 7 … 16 385, converging to
48.0%.

If that survives you, it is the project's first real counterexample and it
rewrites the headline. If it does not, we have been about to publish a defect.
**Nothing is in `.memory/` yet** (PROTOCOL rule 9) — this review decides what goes
in.

## Start where the engineer told you to

It shipped a **defective input generator and caught it with its own control**: the
first `inputs/gen.py` drew every miss as `element + 1`, so **no key was ever below
`elements[0]`**, and the inclusive-`hi` control therefore printed the *correct*
checksum — making its own headline claim unsupported by its own inputs. It fixed
that, re-ran everything, and said in its report that **the workload, not the
kernel, is what a reviewer should attack.** Take the invitation.

- Does the *current* `gen.py` actually produce the distribution `NOTES.md` claims
  — hit fraction exactly 1/2, at least one below-min and one above-max miss per
  window? Verify by decoding the shipped blobs, not by reading the generator.
- **Does the measured cost depend on that distribution?** The probe count is
  data-dependent, and `R3 − R4 = 9 + 4·nq + 6·probes` is denominated in *probes*.
  A workload with a different hit ratio, or keys clustered rather than uniform,
  changes `probes` per query. Does the **fraction** — the 42.53% → 46.63% claim,
  which is the finding — move with it? If a plausible alternative workload flattens
  or reverses that curve, the finding is about the workload.
- `small` and `large` differ in `n` **and** in cache residency. Is the rising
  fraction a `log n` effect or a cache effect? The sweep should separate them; say
  whether it does.

## The other attacks, in the order I would run them

1. **The exact-integer laws.** `R3 − R4 = 9 + 4·nq + 6·probes`, residual 0.00 over
   113 blobs, with 6 = one two-sided slice range check derived from the listing.
   Zero residual over 113 points is either a real invariant or a fit with a
   free parameter hiding in the x-axis — and the x-axis here is **the exact probe
   count replayed from the file**, which is itself computed by something. Who
   computes it, and can it absorb error? Re-derive one law from the disassembly
   independently.
2. **The `Ir`/`ns` direction reversal**, which is finding 15's second half:
   `-C llvm-args=-x86-cmov-converter=false` on unchanged source gives +10.07% `Ir`
   → −18.13% `ns`. The engineer flags this as an **inference**, and says nothing
   rules out a front-end effect from the shorter body rather than branch
   misprediction, and that the flag is whole-program rather than isolated to the
   kernel. Can you tighten or break it? This box has **no branch-miss counter**
   (`perf_event_paranoid = 3`), so a direct measurement is not available — say what
   *is* available.
3. **The layout band.** Two binaries with identical `Ir` differ **32%** in `ns`;
   the same machine code at seven addresses spans **6%** on `small`. That is the
   widest confound this project has measured, and every `ns` claim in `NOTES.md`
   is supposed to be bracketed by it. **Check that they actually are** — an
   unbracketed `ns` claim on an L1-resident kernel is a finding.
4. **R5, and the claim that makes it interesting.** 10/0 first try, and `kernel`
   costs 3 obligations where p05's costs 5 because every multiply is by the
   literal 4 — *zero* nonlinear arithmetic. And the half-open spelling **removes**
   the underflow obligation rather than discharging it, so "the spelling that makes
   the proof trivial is the one that makes the bug impossible, at zero cost in
   instructions, obligations and TCB" — a strong claim, cheap to check. Recount the
   TCB. Does R5's exec code match R4's?
5. **The catalogue correction.** Midpoint overflow unreachable by 2.1e9 because
   `n` is a `u32` field; the reachable overflow is `4·n + 4·nq` needing 36 bits,
   fooled at an 88-byte window. Check the arithmetic and check that
   `adversarial-width.bin` actually exercises it on the cells that claim to fail.
6. **The three-bugs table.** Each bug is claimed invisible to the others' inputs,
   and `k_incl` is claimed to SIGSEGV on p07's *own* `small.bin`. Run them.

## Clean negatives are worth as much as findings

PROTOCOL rule 6. For every attack that does not land, say so with the evidence so
the next agent does not re-run it. And **if the headline survives, say that
plainly** — a confirmed first counterexample is a bigger result than any defect
you could find here, and hedging it would be its own failure.

## Constraints

No root; no `/tmp` — scratch under `.temp/r26/`, and per
`.memory/00-environment.md` constraint 6 **delete your binaries and generated
blobs when you finish, keep your scripts, notes and results**. **No `git add`/`git
commit`** — read-only git. Do not edit `pilot/`, `.memory/`, or anything under
`patterns/` — you report, you do not fix. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never
`pkill`/`killall`; confirm an exact PID's full command line before any kill.

**Run measurements in the FOREGROUND** — background `nohup` jobs on this box are
reported "completed" while still running, which corrupted a data point three
tasks ago. Per-PID scratch paths. p07's blobs regenerate in ~40 s from
`inputs/gen.py --sweep` if you need them.

Notes to `.temp/r26/NOTES.md` as you go so you can be resumed; four agents on the
previous arc died to transient API errors.

Report in PROTOCOL's format, severity-ranked, file:line and a concrete failure
scenario per finding. Paste actual command output.

**Contradicting the manager with a measurement is the highest-value thing you can
do.** Thirty-seven agents have and all thirty-seven were right — p07's own
engineer refuted both of the prescriptions I gave it, including the bug class this
pattern was catalogued around for the life of the project. I have no independent
view of p07's numbers; I am relaying them.
