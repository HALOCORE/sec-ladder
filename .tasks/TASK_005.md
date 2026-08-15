# TASK_005 — make the pins derived, and unblock every future pattern

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, `.tasks/TASK_003_REVIEW.md` (this task is its
remediation — it contains every exact mutation and the green output it produced),
`.memory/02-bench-rules.md` (note the **new** first section on structural
preconditions).

## Why

A review demonstrated, with a **full green gate**, that R5's trusted base can be
made to axiomatise "reading any index of any slice is defined and yields `v@[i]`"
— by editing three lines of `verus.rs` and three lines of `spec.md` in the same
commit. The proof then establishes nothing about memory safety and the gate
certifies it as matching spec.

That is the whole hardening defeated by its own trust model. Fix that first.

It also found the gate **false-fails p02 twice before p02 exists**, so no further
pattern can be added until that is resolved.

## Part A — the pin model (blocker 2)

The diagnosis: every declared pin moves with the code it constrains, so weakening
a pin costs one extra edit. The obligation count cannot backstop it — the review
derived what the count actually measures: **one Verus query per function, plus one
per loop body**. It is a checksum over the function/loop *skeleton*, invariant
under exactly the semantic weakenings it was introduced to catch. (That also
answers the open `--verify-function main → 2 verified` question: the second query
is the driver's loop body, entirely incidental to the call site.)

Adopt the review's design. **The rule: a declared pin is acceptable only for
something a reviewer can check by reading `spec.md` alone. Everything else is
derived.** `check.py:800`'s Miri cross-check — declared value tested against a
*measured* one — is the model to copy.

1. **Derive the collapse floor.** Add `work_per_call(input)` to the `model.py` API
   and assert `marginal_Ir_per_call >= alpha * work_per_call` with `alpha` a
   harness constant. Better if cheap: probe two payload shapes and require
   `d(Ir)/d(work)` to track the model's ratio. Pattern-independent, untunable from
   `spec.md`. (The current floor of 400 against a measured minimum of 915 is
   0.80 Ir/element versus 1.83 achieved — it catches only near-total collapse.)
2. **Single-source the `requires`.** `contract["requires"]` (Python) and
   `verus.items[…]["requires"]` (Verus text) are two independent transcriptions of
   one predicate and nothing checks they correspond. Generate one from the other
   through a declared, reviewed translation table.
3. **An `external_body` item whose body contains `unsafe` must have a non-empty
   `requires`** — a hard failure, not a pinnable value — unless `spec.md` carries a
   per-item justification string that the gate prints prominently in the verdict.
4. **Hash the contract block** into the committed gate JSON, so weakening a pin
   shows up in review as a contract change rather than a source diff.

## Part B — unblock p02 (blocker 3, and the major)

None of these can wait for p02 to be written; they are why it cannot be.

5. **Sanitizers must be allowed to fire on adversarial inputs.** `check.py:770-777`
   fails on any ASan/UBSan hit on any input. p02's adversarial input is *defined*
   as the one that triggers the OOB write, and `.memory/02-bench-rules.md` says the
   adversarial row **records** whether the sanitizer fired. Add a per-input
   expectation; a C rung trapping with exit −6/−11 on an adversarial input is the
   expected result, not a failure.
6. **Anti-collapse must accept a bulk-memory call.** `check.py:266-272` requires a
   backward branch in the kernel. Measured on a p02-shaped kernel: gcc `-O3` gives
   11 instructions, `has_loop=False`, tailing into `call memcpy@plt` — a perfectly
   healthy kernel that fails. Accept "a backward branch **or** a call to a known
   bulk-memory routine", or fall through to the dynamic check alone.
7. **Provide a green path for R4 ≠ R5.** Currently both branches fail: not `exact`
   with `miri.required=false` fails, and with `true` it fails because Miri is not
   installable for the pinned toolchain. Any pattern with a non-trivial proof is
   therefore un-greenable. Three changes:
   - Accept `>= norel` as byte-identical. `norel` means the same machine code at a
     different link address — `spec.md`'s own O0 `why` says exactly that.
   - **Install Miri properly.** It is available on nightly, and R4 is plain unsafe
     Rust with no vstd dependency, so a `nightly` toolchain alongside the pinned
     one can run Miri on R4's source. The toolchain difference is irrelevant: Miri
     checks the source for UB, it does not measure codegen. Do this rather than
     weakening the policy. Record the arrangement in `TOOLCHAIN.md`.
   - If Miri is still unavailable for some rung, record a **documented failure for
     that row**, not a pattern-wide gate failure, with a pinned `blocked_reason`
     the report prints. Failing a whole pattern on a missing tool is how gates get
     switched off. Also drop the hard-coded `"unsafe vs verus"` pair string.

## Part C — the remaining demonstrated bypasses

Each was shown green; each needs a demonstrated failure.

8. **Decoy driver region** (`dloop.py:78-80`) — leftmost non-greedy match means the
   *first* `SLB-DRIVER-BEGIN…END` wins, so a decoy in a block comment above the
   real loop is what gets diffed. Demonstrated with a 2×-unrolled real loop and a
   full green gate. Also: deleting the markers makes a rung **vanish silently**
   (`check.py:705-721` only requires ≥2 found). Fix: `region()` raises on more than
   one BEGIN or END, and `spec.md` pins the *set* of files that must carry a region.
9. **`model.py` can agree by construction** (`check.py:130-148`) — a model whose
   `checksum` shells out to the built C binary passes, and the log reports the
   checksum was "re-derived". Step 2 is the gate's only load-bearing check; it must
   not be satisfiable by running the thing under test.
10. **`vparse` items keyed by name, last wins** (`check.py:511`, `:593`) — a decoy
    `fn kernel` in a `#[cfg(any())] mod` supplies the pinned contract while the
    real, weakened kernel is measured. Fix: return a list, fail on duplicate names,
    require `in_verus`, reject items reachable only under a `cfg`.
11. **The alias table is an unconstrained rewriting program** (`dloop.py:215-231`)
    — destinations are unconstrained and an empty value *deletes statements*,
    reviving the M9 prefetch/barrier payload with two lines of `spec.md`. Restrict
    to single-token identifier↔identifier renames, both sides non-empty.
12. **`dloop` strips `assert(...)` in C**, where it is live code (`_GHOST_RE`
    applied without branching on language; `build.py` never defines `NDEBUG`).
    Ghost-stripping must be Rust-only.
13. **Vacuous pins print as green evidence** (`check.py:654-683`) — an empty
    `requires` list prints "holds on all 200000 kernel calls"; a model returning no
    samples prints "re-derived on 0 sampled calls". Both must fail.
14. **`--skip` re-opens blocker B3 from the command line** (`check.py:108-118`) —
    skipping the adversarial stems means the contract is never evaluated on them
    and nothing is recorded, verdict PASS. `--skip` must refuse adversarial stems,
    and any skip must force a partial verdict and a loud banner.

## Part D — the barrier swap

Do it. The review disagrees with deferring and the argument is sound: the `div` is
~0.1% of `Ir` (safe for the primary metric) but 20–40 cycles on the serial
dependency chain is a **rung-independent additive constant**, so it compresses
every cross-rung wall-clock *ratio* toward 1 — the direction that flatters our own
headline. Swap to multiply-shift (`(acc as u128 * nwin as u128) >> 64`), which
keeps the cache randomisation, and re-measure p01. Cost now is 28 cells; after p02
it is 47×28.

If you disagree after measuring, the fallback is to state in `results/tables/` that
every wall-clock ratio is a lower bound — but swapping is preferred.

## Minors — fix the cheap ones, list the rest

Source→binary provenance under `--no-build` (`check.py:852-864`); casts erased by
`dloop` so width changes are invisible; the obligation pin false-fails on benign
refactors and its message misdiagnoses ("code stopped being verified"); the
`verus.obligations` file list is author-chosen so dropping an entry un-checks it;
`results/gate/*.json` is tracked but rewritten on failing runs and records no
source hashes; **`dloop.py` has no selftest** and every bypass above lives in it.

## Done when

Each demonstrated bypass has a pasted before/after showing the gate now catches it;
`check.py p01` is green on a **complete** run after the barrier swap; a p02-shaped
kernel (memcpy-style, no backward branch, adversarial input that trips ASan) passes
the structural and sanitizer stages when hand-fed. `.memory/` updated where
behaviour changed.

## Constraints

No root; no `/tmp`; **no `git add`/`git commit`**; do not edit `pilot/`, `PLAN.md`,
`pilot/README.md`. Installing a `nightly` toolchain for Miri is sanctioned and
expected.
