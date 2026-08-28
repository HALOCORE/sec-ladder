# TASK_116 — review of `TASK_109` + `TASK_110`: `p42`, the ghost ledger

**Role: research reviewer.** Scratch: `.temp/r116/` (472 KB, **no binaries**, six
probe/generator scripts, an inventory in `.temp/r116/NOTES.md` saying which
script rebuilds what). No `git add`, no `git commit`. `.memory/`, `RECAP.md`,
`results/`, `synthesis/`, `harness/`, `pilot/` and every `patterns/*/` file
**untouched** — every variant measured here is a COPY under `.temp/r116/`.
`harness/check.py`, `build.py` and `measure.py` were **not** run (except
`measure.py --check-stale`, clean: 52 records, 0 STALE).

---

## HEADLINE

⚠⚠ **§A.1 LANDS. THE GHOST LEDGER DOES NOT PROVE LEAK-FREEDOM. HERE IS THE
LEAKING PROGRAM.**

One line, substituted into the shipped `verus.rs`, replacing the error path's
`led_free`:

```rust
        proof { let tracked _dl = led.tracked_remove(0int); }
        return 0;
```

| | shipped `verus.rs` | the leaking variant |
|---|---|---|
| `./verus_run.py` | `18 verified, 0 errors` | **`18 verified, 0 errors`** |
| `--cfg slb_twin` | `21 verified, 0 errors` | **`21 verified, 0 errors`** |
| `spec.md` `verus.obligations` / `twin_obligations` / `axioms` | 18 / 21 / 0 | **18 / 21 / 0 — nothing moves** |
| every `requires` / `ensures` textual pin | — | **unchanged; `led_free` is still in the file** |
| bytes leaked, `adversarial-notag.bin` | 0 | **256 = `model.py::leak_bytes`** |
| `adversarial-mixed.bin` / `adversarial-win1.bin` / `small.bin` | 0 / 0 / 0 | **624 / 16 / 0 — `model.py`'s figures exactly** |

**It leaks exactly `n_err × win_len` bytes — the same quantity `controls/leak.sh`
asserts against LeakSanitizer for the buggy C rung.** It is not a contrived
leak; it is *p42's own bug class*, transplanted into R5, satisfying the
obligation that was published as catching it.

⚠⚠ **And the sharpest form of it:**

```
R5 that satisfies the ledger's leak-freedom `ensures`   md5_fn d3f1194cb10bce2057e0e1f3e28c1e21
R4 with p42's bug planted (error-path `dig_free` deleted) md5_fn d3f1194cb10bce2057e0e1f3e28c1e21
                                                          md5_raw and md5_raw_norel also identical
```

**The verified R5 and the bugged R4 are the same machine code.**

**`Map::tracked_remove` is not an escape hatch I invented — it is the call
`led_free` itself makes** (`verus.rs:472`), and the one `kbody`'s fold makes on
`perms` (`verus.rs:615`). Wrapping an affine resource in a map does not make it
linear. **It makes the drop take one more line.**

⚠ **The refutation is written in p42's own `NOTES.md`, one paragraph below the
claim it refutes** — 6c: *"a tracked `Map` is as droppable as the token inside
it."* The engineer wrote that about deleting the *clause* and did not notice it
also licenses emptying the *map*. This is PROTOCOL rule 9's documented shape.

**Verdict on the task's call 3 (*"if `109`/`110` are self-checking, say so and
stop"*): NO. They are not. Finding 39's PROVISIONAL marker must not be cleared;
its central positive claim is false.**

---

## §A — the ledger

### A.1 — BLOCKER. A leaking program satisfies the `ensures`.

**Both directions of the task's test come apart, and the first one is the one
nobody disclosed.**

**Direction 1 — a token can leave the map without a `dealloc`. YES.**
`vstd::map::Map::tracked_remove` (`~/tools/verus/vstd/map.rs:143`) is a public
proof-mode `axiom fn`. A proof block withdraws the escrowed `Dealloc` and lets
it fall out of scope; `Dealloc` is affine, which p42's own
`controls/affine_leak.rs` measures. The domain comes back empty, the
postcondition holds, and `std::alloc::dealloc` is never called.

`.temp/r116/ledger_attack.py`, six arms, **one of which must fail**:

```
  base               18 verified,  0 errors   MUST verify         OK
  mustfire_err       17 verified,  1 errors   MUST FAIL           OK   <- names `return 0;` [at this exit]
  atk_remove_err     18 verified,  0 errors   ATTACK  *** SUCCEEDS ***
  atk_remove_ok      18 verified,  0 errors   ATTACK  *** SUCCEEDS ***
  atk_remove_both    18 verified,  0 errors   ATTACK  *** SUCCEEDS ***
  atk_assign_err     18 verified,  0 errors   ATTACK  *** SUCCEEDS ***
```

`mustfire_err` is `controls/ledger_leak.py`'s own `leak_err` arm, reproduced
byte-for-byte including the named exit — **so the harness is the one the project
already trusts, and it fires when it should.**

⚠ **`atk_assign_err` is worse than `atk_remove_err` and refutes the claim in its
own words.** `spec.md`'s hashed `idiom.why` says *"a proof cannot drop the MAP
that holds it if a postcondition names that map"*. It can:

```rust
        proof { *led = Map::<int, Dealloc>::tracked_empty(); }   // 18 verified, 0 errors
```

The whole map, tokens and all, is dropped. **The key is not even mentioned.**

**Direction 2 — memory can be allocated without entering the map. YES, and it is
disclosed** (`verus.rs` module comment, `NOTES.md` 6d, `idiom.why`: *"a direct
call to `dig_alloc` still drops its token silently … a MODULE-LEVEL
DISCIPLINE"*). ⚠ **But the disclosure is understated in a way that matters: it
implies the guarantee HOLDS for allocations that DO go through `led_alloc`. It
does not.** That is direction 1.

**The run-time half**, because "satisfies the `ensures`" is only half the claim
(`.temp/r116/leakprobe.py`; valgrind's memcheck is unusable on this box —
`libc6-dbg`, fatal at startup — so the instrument is a counting
`#[global_allocator]` on a `.temp/` copy, reporting from `emit()`):

```
base             verify: 18 verified, 0 errors      <- the CONTROL
    adversarial-notag.bin   leaked=1028  kernel_delta=0     model=256
    adversarial-mixed.bin   leaked=1028  kernel_delta=0     model=624
    small.bin               leaked=1028  kernel_delta=0     model=0
    adversarial-win1.bin    leaked=1028  kernel_delta=0     model=16
atk_remove_err   verify: 18 verified, 0 errors
    adversarial-notag.bin   leaked=1284  kernel_delta=256   model=256   == model's leak_bytes
    adversarial-mixed.bin   leaked=1652  kernel_delta=624   model=624   == model's leak_bytes
    small.bin               leaked=1028  kernel_delta=0     model=0     == model's leak_bytes
    adversarial-win1.bin    leaked=1044  kernel_delta=16    model=16    == model's leak_bytes
```

Two arms that must fire: the base floor (live driver buffers, `emit()` runs
before main's locals drop) is **1028 on every input** — constant, so the
instrument is not measuring the kernel — and the delta must equal `model.py`'s
`leak_bytes`, **which it does on all four inputs including the zero**. The
printed checksum is identical to the shipped rung on every input: *a leak is not
a wrong answer*, which is exactly why the checksum cross-check cannot see it.

**What the ledger actually proves:** *the proof author wrote something on every
exit that empties a map the proof author controls.* That is strictly weaker than
leak-freedom, and the gap is not narrow — it is one proof line wide.

**So `.memory/04-verus.md`'s heading — *"VERUS **CAN** STATE LEAK-FREEDOM — A
GHOST LEDGER DOES IT AT ZERO COST"* — is FALSE as written.** ⚠⚠ **And note what
that makes the retraction it carried out: the struck sentence (*"Verus at the
pin cannot state leak-freedom"*) is NOT re-established by my result, but it is
no longer refuted.** The honest state is the one `.memory/04-verus.md` already
holds two paragraphs below its own strikethrough: **"Whether leak-freedom is
expressible by some other encoding is OPEN."** That sentence should govern.

**Is there a repair?** Two measurements, `.temp/r116/receipt{,_priv}.rs`:

```
receipt.rs                       -> 2 verified, 0 errors   (honest arm)
receipt.rs --cfg forge_struct    -> 3 verified, 0 errors   *** A MODULE-LOCAL `struct Freed {}`
                                                               IS FORGEABLE IN PROOF MODE ***
receipt.rs --cfg forge_assume    -> error: `assume_new` is not supported   (must-fail arm, fires)
receipt_priv.rs                  -> 2 verified, 0 errors
receipt_priv.rs --cfg forge      -> error: cannot construct `res::Freed` with struct literal
                                    syntax due to private fields            (must-fail arm, fires)
```

So the obvious repair — make trusted `dig_free` return an unforgeable
`Tracked<Freed>` receipt and have `kbody` `ensures` one on every exit — **is dead
if the receipt type is module-local, and survives rustc privacy if it is not.**
⚠ **UNBUILT and OPEN.** It would change trusted item 3's pinned signature and
would additionally need the receipt tied to the allocation (otherwise: free a
dummy 1-byte block, keep the receipt, leak the real one). **I am not
recommending it; I am recording that the space is not empty and that a
module-local receipt is not the answer.**

### A.2 — the control fires, but not for the reason published

`controls/ledger_leak.py` is **not vacuous** — reproduced above at `17 verified,
1 errors` with the exit named. ⚠ **But it distinguishes *"no exit-emptying
statement"* from *"some exit-emptying statement"*, not *"freed"* from
*"leaked"*.** The task asked whether it would fire for a program with no ledger
at all: it would fire for *any* deletion that leaves the domain non-empty, and
it does **not** fire for a program that empties the domain by hand. **A control
that fires is not the same as a control that fires because of the thing under
test**, and this is that case.

⚠ **Partial tripwire, worth knowing:** run against the error-path attack, the
script's `ERR_ARM` anchor assert *does* fire (`"verus.rs no longer contains
exactly one copy of this release"`), so a reviewer who ran it would notice. Its
`OK_ARM` anchor does **not**. And the script is not a gate stage, so nothing runs
it automatically.

### A.3 — the "no linear mode" negative SURVIVES a broader census

The task flagged the absence argument as RECAP's rule-6 failure mode. I widened
it and it holds.

```
verifier:: attribute names in the pinned rust_verify (sort -u):  22   <- TASK_110's figure, confirmed
  accept_recursive_types allow allow_complex_invariants assume_termination decreases_by
  deprecated_postcondition_mut_ref_style exec exec_allows_no_decreases_clause external_body
  external_trait_specification external_type_specification internal_trait loop_isolation
  nonlinear prophetic recommends_by reject_recursive_types
  reject_recursive_types_in_ground_variants spinoff_prover truncate type_invariant verify
other attribute namespaces in the binary: verus::{v, verus_builtin, vstd}  (no modes)
keyword sweep of the BINARY: affine 0, must_consume 0, unforgeable 0, relinquish 0,
  must_use 0, nodrop 0; `no_drop` 4 and `leak_check` 2 are RUSTC internals
  (`consider_builtin_bikeshed_guaranteed_no_drop_candidate`, region leak check) — chased, not modes
vstd: affine 0, must_consume 0, no_drop 0, unforgeable 0; `relinquish` 2 (prose in invariant.rs);
  `linear` 66, every one of them `nonlinear` arithmetic or "linearization point" (atomic.rs, logatom.rs)
~/tools/verus/vstd/std_specs/  — 26 files, no drop/dealloc specification of any kind
  (only `manually_drop.rs`, which specifies `ManuallyDrop`, i.e. the OPPOSITE)
```

**It remains an absence argument and I say so.** But it is now an absence
argument over the attribute *enumeration* plus ten candidate names plus
`std_specs/` specifically, not a single keyword. ⚠ **And A.1 makes it matter
much more than before: the ledger was the workaround for the missing linear
mode, and the workaround does not work.**

### A.4 — TCB recount: TASK_110 IS RIGHT

`check.py::_is_trusted` imported and driven over the shipped `verus.rs` (import
only; no gate run, no `results/` write):

```
external_body items: ['v_get_unchecked','dig_alloc','dig_free','load_input','emit']   5
_is_trusted items  : ['v_get_unchecked','dig_alloc','dig_free']                       3
led_alloc  external=None  trusted=False
led_free   external=None  trusted=False
kbody      external=None  trusted=False
```

**5 / 3, unchanged. The ledger costs zero trusted items and zero instructions —
and, per A.1, delivers zero additional guarantee.** The price table in
`.memory/04-verus.md` and `NOTES.md` 6b is accurate about the *price*. It is the
*product* that is wrong.

---

## §B — the sign, and whether `+12.00 / +11.00` is a fair comparison

⚠ **I did §A first. The task's call 2 asked whether §B outranks §A: it does not.
§B produced only clean negatives, and they SUPPORT the published number.**

### B1 — the R3 side, searched with the effort the R4 side got. CLEAN NEGATIVE.

The R4 win came from changing the fold loop's **shape**. Nobody tried that on
R3: all three non-shipped R3 spellings in `controls/spellings.py` are *dearer*
than `r3_ship`, so the R3 endpoint has never had a candidate that could move it.
I added **six** in-contract spellings covering exactly that class
(`.temp/r116/r3_search.py`, `--measure`, callgrind, plus a must-fire arm):

```
BROKEN_fwd     checksums agree with shipped? False   OK -- rejected, the checksum gate is running

marginal Ir/call, -O3, isolated, whole-program
r3_ship             1419.00       51138.00      <- reproduces TASK_110 to the hundredth
r3_rfold            1419.00       51138.00      .iter().rfold(..)
r3_forrev           1419.00       51138.00      for &b in dig.iter().rev()
r3_intoiter         1419.00       51138.00      dig.into_iter().rev().fold(..)
r3_copiedrev        1419.00       51138.00      .iter().copied().rev().fold(..)
r3_revslice         1419.00       51138.00      dig[..].iter().rev().fold(..)
r3_extcopied        1419.00       51138.00      write side: .iter().copied().map(..)

all seven:  n_fn=159   md5_fn=f8a2e4b430800fd189a0eaa54e59c17e   <- BYTE-IDENTICAL
```

**Seven spellings, one binary.** LLVM canonicalises the whole class. **The R3
endpoint is not held by fiat in the way the R4 one is: it is measured, and it
does not move.**

### B2 — a sixth and seventh R4 spelling. CLEAN NEGATIVE.

`.temp/r116/r4_search.py`. The write loop was still an index; a do-while
ascending cursor that advances only after the `i == len` test never forms the
one-past-the-end pointer, so it is in the same admissible vocabulary as the
shipped fold.

```
r4_ship        n_fn=128  md5_fn=28432cb8…      1407.00    51127.00   <- reproduces TASK_110 exactly
r4_wdowhile    n_fn=131  md5_fn=a45a7777…      1503.00    55223.00   DEARER
r4_wdw_ptreq   n_fn=137  md5_fn=afccbc25…      1409.00    51128.00   DEARER
BROKEN_nofree  n_fn=128  md5_fn=d3f1194c…      (must-fire arm: deleting a free DOES move md5_fn)
```

**Admissibility not established for either candidate — and it does not matter,
because both are dearer.** TASK_110's *"the R4 endpoint is held by fiat"* is
honest, and **two more spellings did not dislodge it.**

### B3 — the comparison is more robust than TASK_110 claims

At **matched fold shape** the difference is a per-call constant:

```
r3_ship 1419 − r4_ship 1407 = +12        r3_revidx 1627 − r4_idxfold 1617 = +10
r3_ship 51138 − r4_ship 51127 = +11      r3_revidx 59845 − r4_idxfold 59834 = +11
```

**Shape-independent, ~+11 Ir/call, which is the `Vec` bookkeeping and drop
branch.** `NOTES.md` 11b's refusal to publish a directional headline off two
overlapping *spans* remains correct — but the *paired* quantity is stable and
`TASK_113` was right that the number reproduces.

### B4 — MINOR: two of the four published R3 span endpoints are out of contract

`spec.md` `required[4]`: *"R3 acquires with `Vec::with_capacity` and fills with
`extend` … Scoped one entry per rung, by name."* Under the pattern's own
named-spelling standard (*a backticked span in a `required` entry pins THAT
SPELLING*), `r3_zeroed` drops `Vec::with_capacity` (it is R2's acquisition) and
`r3_push` drops `extend`. `NOTES.md` 11b marks both **✅ admissible** and quotes
the R3 span as **`1419 … 2634` / `51138 … 102846`**.

**The in-contract R3 span is `1419 … 1627` / `51138 … 59845`.** The published one
is 4.5× too wide on `small` because its top endpoint is a rung that is not R3.
⚠ **This is `p05`'s two-task detour exactly — out-of-contract spellings measured
and reported as the pattern's numbers.** ✅ **The conclusion survives**: the
narrowed R3 span still overlaps R4's `1407 … 1617` at both ends. Only the
published width is wrong.

---

## §C — does p42's Miri evidence survive `MIRI_FLAGS = ()`? YES, and I re-ran it.

**Scope respected: `TASK_114` owns the `MIRIFLAGS` decision and
`miri.blocked_reason`. I answer only "does p42's own Miri evidence survive".**

`controls/miri_seeds.sh` does **not** use `MIRIFLAGS`. It passes
`-Zmiri-disable-isolation -Zmiri-seed=$s` **on the miri command line**
(`miri_seeds.sh:73–76`), and `check.py` passes `-Zmiri-disable-isolation` on the
command line too (`check.py:7869–7872`) with `MIRIFLAGS` popped from the
environment. **TASK_107's 4.6× is about the environment variable being present;
the seed sweep never set it.** So the sweep's regime differs from the gate's in
exactly one respect — an explicit `-Zmiri-seed=N` — and it covers **eight**
values where the gate uses miri's default.

**"Seeds 0–7 clean" therefore still describes a SUPERSET of the shipped
configuration**, not a removed regime. Two caveats a citation should carry:

1. ⚠ **The sweep runs `unsafe.rs` only** (`run_miri "$PDIR/unsafe.rs"`), and
   `spec.md`'s `miri.sources` is `["unsafe.rs"]`. **R5 is never Miri-checked.**
   Combined with §A.1: **nothing checks R5 for leaks directly** — R5's
   leak-freedom is inferred from R4's Miri result plus the `identity` pin.
2. `large.bin` remains outside Miri entirely (BLOCKED), so the inference has a
   hole on the one input the ladder's `large` column is measured on.

**I re-ran Miri in the gate's own configuration** (MIRIFLAGS unset, `n_iters`
clamped to 4, `adversarial-notag.bin`), two arms:

```
SHIPPED_R4   rc=0   (no leak, no UB)
LEAKING_R4   rc=1   error: memory leaked: alloc7468 (Rust heap, size: 32, align: 1)
                    error: memory leaked: alloc7490 (Rust heap, size: 32, align: 1)
```

✅ **The post-TASK_107 configuration still catches p42's own bug class.** ⚠
**MINOR, and it is a record-hygiene point, not a gate defect:**
`check.py:7883` computes `ub = "Undefined Behavior" in r.stderr or "error:
unsupported" in r.stderr`. **A Miri leak is neither**, so a leaking rung is
recorded with `ub: False` and is caught by the *next* branch — `r.returncode !=
want_exit`. The gate fails correctly; the failure message reads *"miri exited 1,
model expects 0"*, and `results/gate/*.json`'s `miri.runs[*].ub` would read
`False` for a leaking tree. **A reader auditing the record by the `ub` key would
see nothing.**

---

## §D — clean negatives asked for

- ✅ **R3 and R4 are semantically equivalent.** All 12 matrix inputs, stdout and
  exit code, `r3_ship` vs `r4_ship`: **12/12 agree**, including
  `adversarial-shortlen.bin` (exit 5, empty stdout) and `adversarial-win1.bin`
  (`len == 1`, the input that decides whether the do-while's first pass is
  correct). The do-while is a control-flow change, not an algorithm change:
  `requires 1 <= len` makes the body's unconditional first pass sound, and the
  cursor visits `base+len-1 … base` exactly.
- ✅ **`identity` reproduces**: `unsafe` vs `verus`, `-O3 isolated`, `n_fn=128`,
  `md5_fn 28432cb848832a692454c3bcc2aee83e`, `md5_raw
  044ae7cbea73ebb349f6dcc901d63716` — TASK_110's figures to the character.
  `-O0`: `n_fn=104`, `md5_raw_norel` equal.
- ✅ **The identity pin CATCHES the attacked R5 at BOTH pinned levels**, so the
  shipped tree is protected — by the pin, not by the proof:
  `-O3` `md5_fn d3f1194c…` ≠ `28432cb8…`; `-O0` `n_fn 97` vs `104`,
  `md5_raw_norel` differs. ⚠ **But a leak planted in BOTH rungs passes identity
  (proved above: the two leaking rungs are byte-identical), passes every
  `spec.md` pin, passes the obligation counts, and is caught only by Miri.**
- ✅ **`controls/sweep.py` docstring, confirmed as TASK_110 disclosed**: line 27
  *"Cells default to the six measured ones"*; line 43 `CELLS = [...]` lists
  **seven** (`c-gcc, c-gcc-h, c-clang, safe_naive, safe_tuned, unsafe, verus`).
- ✅ `harness/measure.py --check-stale`: **52 records examined, 0 STALE**;
  `git status --porcelain` shows only the two concurrent agents' report files.

---

## Findings, ranked

**BLOCKER 1 — the ghost ledger's leak-freedom `ensures` is satisfied by a
leaking program.** `patterns/p42-goto-cleanup/verus.rs:504–508` (`kbody`'s
`ensures`), reachable via `vstd/map.rs:143`. Failure scenario: replace either
`led_free` call with `proof { let tracked _dl = led.tracked_remove(0int); }` —
`18 verified, 0 errors`, `21 verified, 0 errors` under `--cfg slb_twin`, every
`spec.md` pin intact, and `n_err × win_len` bytes leaked per run. **Everything
that says the ledger states leak-freedom or covers p42's bug class must be
retracted.** Sites, complete:

| file | where | hashed into |
|---|---|---|
| `patterns/p42-goto-cleanup/spec.md` | `idiom.why` (*"a proof cannot drop the MAP…"*, *"That is exactly p42's bug class"*) | **contract + measurement** |
| — | `identity[0].why` (*"Leak-freedom on R5 is stated by the GHOST LEDGER and checked by Verus on every exit"*) | **contract + measurement** |
| — | `miri.reason` (see BLOCKER 2) | **contract + measurement** |
| — | `verus.twin_obligations_note` (*"the GHOST LEDGER that states leak-freedom"*) | **contract + measurement** |
| `patterns/p42-goto-cleanup/verus.rs` | module comment ¶3–¶5; the `------ ledger ------` block | **measurement** |
| `patterns/p42-goto-cleanup/unsafe.rs` | SAFETY (5)'s TASK_110 retraction paragraph | **measurement** |
| `patterns/p42-goto-cleanup/NOTES.md` | §6 heading, 6b, 6c, 6d | gate |
| `patterns/p42-goto-cleanup/README.md` | 3 hits | gate |
| `controls/{ledger_leak.py, affine_leak.rs, miri_seeds.sh}` | headers | gate |
| `.memory/04-verus.md` | §1727–1790, incl. the heading and the *"THE HONEST CLAIM"* block | — |
| `.memory/06-catalogue.md` | p42 row, *(1)* | — |
| `RECAP.md` | finding 39 | — |
| `results/SYNTHESIS.md` | 647–673 | — |
| `results/tables/p42-goto-cleanup.md` | generated from `idiom.why` — **fix the generator too** | — |

⚠ **Budget (PROTOCOL rule 6's table): `spec.md` inside the fence ⇒
`contract_sha256` moves; `verus.rs`/`unsafe.rs` ⇒ MEASUREMENT. Batch it into one
pass.** ⚠ **The `identity` and `miri` numbers themselves are unaffected — this
is a retraction of prose, not of a measurement.**

**BLOCKER 2 — `spec.md::miri.reason`'s TASK_110 amendment replaced a TRUE
sentence with a FALSE one, inside `contract_sha256`.** Verbatim: *"AMENDED AT
TASK_110: this sentence used to read `Verus does NOT prove that dig_free is
reached on every path`, and since the ghost ledger landed it does."* ⚠⚠ **The
struck sentence was right.** `atk_remove_err` is an exit on which `dig_free` is
not reached and the file verifies. **This is PROTOCOL rule 9's `TASK_099` shape,
second occurrence, and this time the false replacement is inside the hashed
block and the true original is gone.** ⚠ **The rule's own remedy applies: the
original should be restored and the ledger annotated, not the other way round.**

**MAJOR 3 — the `.memory/` layer and `RECAP` still carry the attribute count
`TASK_110` corrected.** `.memory/04-verus.md:1778` *"gives **23** attributes"*
and `RECAP.md:1998` *"(23 verifier attributes…)"*, against
`patterns/…/NOTES.md:648` and the hashed `idiom.why`, both **22**, and against my
own run, **22**. ⚠ **`TASK_110`'s running-count item 1 — the correction that
cost a second gate and a second measure because it sat inside the fence —
**never reached the authoritative layer**.** PROTOCOL rule 13's shape: the fix
landed where the detail is.

**MINOR 4 — `controls/sweep.py:27` says six, `CELLS` has seven.** Reproduced;
disclosed by TASK_110 and still open.

**MINOR 5 — the published R3 span is 4.5× too wide** (§B4): `r3_zeroed` and
`r3_push` are outside `required[4]`'s R3-scoped acquisition idiom.
`NOTES.md:1064–1088` marks both admissible.

**MINOR 6 — `check.py`'s Miri `ub` key is `False` for a leak** (§C). The gate
fails on the exit code, which is correct; the *record* carries no leak signal
under a field a reader would search.

**MINOR 7 — `controls/ledger_leak.py`'s tripwire is half a tripwire** (§A.2):
`ERR_ARM`'s anchor assert fires on the error-path attack, `OK_ARM`'s does not,
and nothing in the gate runs the script.

---

## Clean negatives (so nobody re-runs them)

1. **`controls/ledger_leak.py` is not vacuous** — `17 verified, 1 errors`, exit
   named, reproduced independently.
2. **TCB is 5 / 3 and the ledger adds nothing to it** — `_is_trusted` driven
   directly.
3. **Six new in-contract R3 spellings are byte-identical to `r3_ship`**
   (`md5_fn f8a2e4b4…`, `n_fn 159`); the R3 endpoint does not move.
4. **Two new R4 spellings in the admissible vocabulary are both dearer**; the R4
   endpoint holds against a sixth and seventh try.
5. **Every TASK_110 figure I re-derived reproduced exactly**: `1407.00 /
   51127.00`, `1419.00 / 51138.00`, `md5_fn 28432cb8…`, `md5_raw 044ae7cb…`,
   identity `exact` at O3 / `norel` at O0, `18 verified, 0 errors`,
   `21 verified, 0 errors`.
6. **The "no linear must-consume tracked mode" negative survives** a full
   attribute enumeration, a ten-name keyword sweep of the binary, a vstd sweep
   and a `std_specs/` sweep.
7. **The identity pin catches the attacked R5 at both pinned optimisation
   levels**, so the shipped tree is not at risk.
8. **Miri in the post-`TASK_107` configuration still catches the leak**
   (`rc=1`, `memory leaked`), with the shipped rung silent.
9. **R3 and R4 agree on all 12 inputs**, stdout and exit code.

---

## THE THREE CALLS THE MANAGER WAS LEAST SURE OF

**1. *"That the ghost ledger is sound."* — IT IS NOT, and the leaking program is
in `.temp/r116/ledger/atk_remove_err.rs`.** The manager's instinct was right for
the reason stated: it replaced a false claim within hours, it is clever, and
clever is where this project's errors live. **The specific failure is that the
encoding inherits the affineness it was built to escape** — a map is a container
for affine resources, not a linear type, and `tracked_remove` is in the same
public API the shipped proof already calls twice.

**2. *"That `TASK_113` was right to say don't aim at the number."* — RIGHT, and
§B confirms it from the other side.** The number reproduces *and* survives eight
new spellings across both endpoints. **§A outranked §B and I did it first.** The
one number that is wrong is the R3 **span**, not the difference.

**3. *"That reviewing this pair is worth a task at all."* — YES, decisively.**
`TASK_113`'s triage put this second and was right to keep it. ⚠ **Do not clear
finding 39's PROVISIONAL marker.** The pattern's gate is green, its record
reproduces, its corrections landed — **and its central positive claim is false.
"Self-checking" would have missed it, because nothing in the gate checks that an
`ensures` means what its prose says it means.**

---

## What I did NOT do, and what I am unsure about

1. **I did not build the receipt repair against p42's actual kernel.** The two
   probes are standalone. Whether a privacy-scoped `Tracked<Freed>` tied to the
   allocation verifies inside `kbody`, and at what cost to trusted item 3's
   pinned signature, is **OPEN**.
2. **I did not prove that leak-freedom is inexpressible at the pin.** My result
   refutes one encoding. The absence claim remains an absence claim.
3. **I did not establish admissibility for `r4_wdowhile` / `r4_wdw_ptreq`** — no
   R5 twin was built. Both are dearer, so it does not bear on the endpoint.
4. **I did not re-run `controls/{spellings,sweep,leak,miri_seeds}.py/sh`
   end-to-end** — they write into `.temp/t104/` and `.temp/t110/`, other tasks'
   scratch, and two agents are live. I reproduced the arms I needed inside
   `.temp/r116/` instead, from the same shipped sources by the same
   substitution method.
5. **My leak instrument is a counting global allocator, not LeakSanitizer.**
   valgrind memcheck cannot start on this box. The instrument is validated by a
   constant base floor and by agreement with `model.py::leak_bytes` on four
   inputs, but it is not the tool `controls/leak.sh` uses for the C rungs.
6. **I did not check whether other patterns cite the ghost ledger as precedent.**
   `.memory/04-verus.md`'s *"family of three"* and `SYNTHESIS.md` §4 both do;
   `p47` and the stack-overflow member are untouched by this result and, if
   anything, **p42 rejoins the family unconditionally.**
7. **§B4's out-of-contract reading rests on `required[4]`'s prose scoping**, not
   on a gate stage — `spelling_matches` cannot express per-rung scoping, which
   is why the entry says it in English. A different reading of that entry would
   restore the wide span.

## Memory updates

**None — `.memory/` and `RECAP.md` are manager-only and I did not touch them.**
Everything durable is in this report and in `.temp/r116/NOTES.md`.

---

## RUNNING COUNT — **425 + 9 on this branch**

⚠ **Branch delta, as the task file asks. `TASK_114` and `TASK_115` ran
concurrently from 414; reconciliation is the manager's job, not mine.**

1. **The ghost ledger's leak-freedom `ensures` is satisfied by a program that
   leaks exactly `n_err × win_len` bytes** — one proof line, `18 verified, 0
   errors`, `21/0` under the twin.
2. **The verifying leaking R5 is BYTE-IDENTICAL to an R4 with p42's bug
   planted** (`md5_fn d3f1194c…`), so "R5 covers its own bug class" collapses
   onto identity + Miri, which is what it was before the ledger.
3. **`spec.md::miri.reason`'s TASK_110 amendment struck a TRUE sentence and
   replaced it with a FALSE one, inside `contract_sha256`** — rule 9's
   `TASK_099` shape, second occurrence.
4. **`.memory/04-verus.md:1778` and `RECAP.md:1998` still say 23 `verifier::`
   attributes**; the corrected 22 reached the pattern and not the authoritative
   layer.
5. **A module-local tracked receipt struct is FORGEABLE in proof mode** — `let
   tracked f = Freed {};` gives `3 verified, 0 errors`, so the obvious repair
   fails as stated.
6. **rustc privacy DOES make one unforgeable** — the `--cfg forge` arm is
   rejected — so the repair space is not empty. UNBUILT.
7. **Six new in-contract R3 spellings compile to one binary** (`md5_fn
   f8a2e4b4…`): the R3 endpoint is measured, not fiat, and the fold shape is not
   an R3 lever at all.
8. **Two new R4 spellings are dearer** (`1503` / `1409` against `1407`), and the
   safe-Rust penalty is **shape-independent**: `+12/+11` at the do-while pair and
   `+10/+11` at the index pair.
9. **The published R3 span `1419 … 2634` includes two spellings outside
   `required[4]`'s R3 acquisition idiom**; the in-contract span is `1419 … 1627`.

Items 1–4 and 7–9 are corrections to or confirmations of measured claims; 5–6
are new measurements on an open question. **If you prefer to count only the
corrections, the figure is 425 + 5** (items 1, 2, 3, 4, 9).
