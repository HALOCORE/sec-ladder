# TASK_055 — two prover-capability probes: can p08 drop a trusted item, and can a LIFETIME bug ever have a rung?

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.memory/04-verus.md` **in full** —
especially the corrected `copy_from_slice` rule and the **TCB accounting
section** (PROVISIONAL, from TASK_048) — then `.tasks/TASK_047_REVIEW_REPORT.md`
**B1**, `.tasks/TASK_048.md` **item 1**, and
`.tasks/TASK_049_REPORT.md` **§0's candidate-3 rejection**.

Both probes are **experiments, not deliveries**. Neither ends in a pattern edit.

## Probe 1 — p08's `copy_in` is the last known relocatable trusted item

TASK_048's census classified all 57 trusted items across the tree and measured
**exposure at 2 of 58 (3.4%)**: p06's `scr_load` (**removed**, TCB 6 → 5, at
byte-identical `-O3` codegen) and **p08's `copy_in`, which is untried**. It would
take p08 from **4 items to 3**.

⚠ **Do not assume it is free. p02's equivalent was NOT.** The discriminator is
measured and it is **what R4's body spells**:

| pattern | R4 spells | outcome |
|---|---|---|
| p06 | `copy_from_slice` | wrapper removed, **byte-identical `-O3`**, TCB 6 → 5 |
| p02 | `copy_nonoverlapping` (unsupported at the pin) | codegen moved **+5.00 `Ir`/call**, one extra panic pad, **broke `identity: exact`** — **not landed**, price recorded |

**So the first thing to establish is what p08's R4 actually spells**, and predict
from the table before you measure.

Deliver: whether the contract discharges without the wrapper; the Verus counts
(shipped and `--cfg slb_twin`); the `-O3` codegen comparison (`md5_raw`,
`md5_fn`, instruction counts, panic pads); whether `identity` would still hold;
and **the recommendation with its price**. ⚠ **Do not edit p08** — p08 is
published and reviewed, and landing this is the manager's call with the
measurement in hand, exactly as it was for p02.

⚠ **And answer the accounting question explicitly**: if the wrapper comes out,
does the trust *disappear* or *relocate into vstd*? That is what `.memory/04-verus.md`'s
classification exists for — say which of **U-license / V-gap / infra** the item
is before and after.

## Probe 2 — `vstd::raw_ptr`, and the project's missing bug class

**Every bug this project models is spatial or logical. None is a LIFETIME bug** —
the one class safe Rust rejects at compile time rather than at run time. p14's
§0 considered it and **rejected it for a stated reason**: the descriptors have to
be **pointers**, safe Rust cannot hold them, and `as_ptr` / `add` /
`from_raw_parts` are unsupported at the pinned vstd — **so R4 would not be a
rung.**

**Nobody has tried `vstd::raw_ptr`.** `.memory/04-verus.md` names it as the route
for raw pointers and manual memory (`PointsTo` permissions) and this project has
never used it. p14's reviewer expected it to fail — *"a stack local cannot supply
a `PointsTo`"* — and **recorded that as untested.**

Settle it, under `.temp/p55/`, on a **minimal probe** — not a pattern:

1. Can a rung hold an array of raw pointers into a buffer, dereference them, and
   **verify**, using `vstd::raw_ptr`?
2. If the buffer is a **stack local**, can it supply the permission at all? If
   not, does it work for a `Vec`/heap buffer, and would that still model the bug?
3. What does it cost — TCB items, obligations, and does the exec code stay
   R4-shaped enough for an `identity` pin against R5?

**A clean negative is a full result here.** If `raw_ptr` cannot do it, say
exactly which obligation or missing spec stops it, paste the Verus error, and
**that closes the question** — p14's rejection becomes measured rather than
predicted, and the catalogue's pointer-heavy family (p09-arena, p10-intrusive
list in `PLAN.md`'s old numbering; see `.memory/06-catalogue.md` for the real
rows) inherits the answer.

**Budget: one session across both probes.** Probe 1 first — it is bounded and has
a known comparison table. If probe 2 is still open when the budget runs out, stop
and report where it stuck; a stalled probe reported with its exact error IS the
deliverable (`.memory/06-catalogue.md`'s proof-effort rule).

## Deliverable

**Write `.tasks/TASK_055_REPORT.md` yourself before your final message**
(PROTOCOL rule 10): the two probes, their measurements, the recommendation for
p08 **with its price**, and a plain verdict on whether a lifetime bug can ever
have a full ladder here.

## Constraints

No root; no `/tmp` (scratch `.temp/p55/`, **per-PID paths**); **no `git
add`/`git commit`**; do not edit `pilot/`, `.memory/`, `harness/`, `common/`,
**or any pattern — both probes are experiments and land nothing.** Read-only
outside `.temp/p55/`. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never
`pkill`/`killall`; **no `nohup … &`**; no self-matching `pgrep` wait-loops.
⚠ **Other agents are running concurrently.** Stay inside `.temp/p55/`.
⚠ **Do not run wall-clock measurements** — concurrent timing jobs corrupt each
other. `Ir`, codegen and Verus are fine.

Notes to `.temp/p55/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Eighty agents
have contradicted the manager and all eighty were right — including on the
`copy_from_slice` claim that stood in `.memory/04-verus.md` from TASK_004 to
TASK_048 and was false in both halves. **Check `~/tools/verus/vstd/` before
recording that anything "has no spec"**; that is the single most repeated mistake
on this project.

**What I am least sure of is probe 2's framing.** I am assuming a lifetime bug
needs raw pointers *in the kernel*. It may be expressible with indices plus a
generation counter, or with a `Vec` that is dropped and reallocated — in which
case safe Rust catches it at run time rather than compile time and it is a
different, possibly better, pattern. **If you see a formulation I have not, say
so** — that would unlock a bug class the ladder has never touched.
