# TASK_115 — the two live rows, and the six adjudications that never landed

**Role: research engineer (probe only — you build NO pattern).** Read
`.tasks/PROTOCOL.md`, then this file, then `.memory/06-catalogue.md`'s rows for
**`p26`** and **`p37`**, then `.tasks/TASK_086_REPORT.md` §6 and §8–§11, then
`.tasks/TASK_092_REPORT.md` **PART B**, then `.tasks/TASK_100_REPORT.md`'s `p37`
section.

Scratch in **`.temp/t115/`**.

⚠ **YOU ARE NOT THE ONLY AGENT RUNNING.** `TASK_113` (reviewing `TASK_102`) and
`TASK_114` (reviewing `TASK_107`) are both live, both read-only, in `.temp/r113/`
and `.temp/r114/`. **See Constraints — the limits on you are hard.**

---

## Why this task exists

The project has declared itself **measured out** and RECAP says *do not start a
27th pattern*. That rests on **RECAP finding 37**, generalised from `TASK_102`,
which probed **eight candidates and refused all eight**.

⚠⚠ **BUT `TASK_102`'s EIGHT WERE NEW AXES — `B1 B2 B3 C1 C2 C3 D6` — NOT
CATALOGUE ROWS.** ✅ **Manager-verified by reading the report.** Meanwhile the
catalogue has **six rows whose status cell is the bare word `planned`**:
`p20 p21 p25 p26 p40 p41`.

✅ **And `TASK_086` ADJUDICATED ALL SIX. None of the six adjudications reached
the catalogue.** Verified by reading `TASK_086_REPORT.md`:

| row | `TASK_086` verdict | catalogue says |
|---|---|---|
| **`p26`** RLE decode expansion | ⚠⚠ **BUILD** (third tier) | `planned` |
| `p20` length/offset pair (Heartbleed) | **DEFER**, with a measurement | `planned` |
| `p21` CSV/field splitter | **DEFER** | `planned` |
| `p25` dynamic array `realloc` | defer stands, out of scope | `planned` |
| `p40` SoA vs AoS | **REFUSE, with the measurement** | `planned` |
| `p41` flexible array member | **REFUSE, with the measurement** | `planned` |

⚠ **RECAP flagged only the `p40`/`p41` half of this.** **A `BUILD` verdict has
been invisible in the catalogue for 29 tasks while the project concluded it had
nothing left to build.**

**Your job is to settle `p26` and `p37`, and to hand the manager the six
adjudications in a form it can land.** ⚠ **You do not edit `.memory/`.**

## §A — ⚠⚠ `p26`, AND THE QUESTION IS BIGGER THAN THE ROW

**What is measured already** (`TASK_092` PART B, kernel-exclusive, both opt
levels, shipped shape):

```
input                ship_safe ship_unsafe        S-U
p26-np016r016.bin      7570.30     6837.30    +733.00
p26-np016r200.bin     24450.30    32837.30   -8387.00     <- SIGN INVERTS
p26-np200r020.bin     55794.00    44381.00  +11413.00
```

**And the mechanism is already half-identified:** at run length 200 the two
shipped spellings reach **different fill strategies** — `ship_safe` 166 insns,
**one** `memset@GLIBC` and `xmm` registers; `ship_unsafe` 116 insns, **two**
`memset@GLIBC`, no vector registers (loop-idiom-recognize turned the unchecked
writes into a `memset` call). ⚠⚠ **AND `TASK_092` RECORDS THAT *NEITHER HAS A
PANIC EDGE*.**

### A.1 — ⚠⚠ the question that outranks the row

**RECAP finding 37 says this benchmark can price a safety property *if and only
if* some rung emits it as a compare-and-branch and another omits it.**

⚠⚠ **`p26` at run length 200 appears to be a large safe-vs-unsafe difference
with NO compare-and-branch on either side.** **Is that a counterexample to
finding 37, or is it the best ILLUSTRATION of it — i.e. the 8387 is not a safety
price at all, but an idiom-selection artefact that a naive reading would publish
as one?**

⚠ **STATE THIS AS A QUESTION AND MEASURE IT. Do not assume either answer.** **I
think it is the second** — that `p26`'s headline number is precisely the trap
finding 37 warns about — **but I have been wrong on exactly this kind of call
repeatedly and the record says so. Contradict me with a measurement.**

**What settles it:** does the `memset`-strategy divergence *depend on the safety
check*, or is it a spelling difference that survives deleting the check from the
safe rung and adding one to the unsafe rung? ⚠ **The control is symmetric and
you must run BOTH directions** — one-sided search is this project's most
repeated methodological failure (RECAP: *"a difference is only as honest as its
WEAKER-searched endpoint"*).

### A.2 — the input band, which is the row's stated blocker

`TASK_092`: *"`p26`'s sign is a property of the RUN LENGTH, not of the row, so
`p26` cannot be costed until its input band is designed"*, and ⚠ **its inversion
threshold is NOT LOCATED — run lengths 16/20 (+) and 200 (−), nothing
between.** **Locate it.** Sweep run length, find where `S−U` crosses zero, and
report the curve.

⚠⚠ **CHECK THE RESIDUE CLASS of anything your bands hold constant.** `p38`'s
out-of-sample failure was 100% attributable to two of three bands sitting at
`nw ≡ 0 (mod 8)`. **A run-length sweep that only samples multiples of 4 is the
same trap** — `p23`'s own `sweep_fit.py` sampled `[2,4,8,16,24,32,40,48]`, seven
of eight multiples of 4.

### A.3 — the two novelty claims, RUN, not argued

⚠ **`TASK_086` recorded its own kill risk:** *"the finding would be **p13's
finding, second instance** — worth building only if §0 can say what is not
p13's."* **Settle it.**

1. **Is `p26` `p13`'s finding again?** `p13` is *"a bound the optimiser can SEE
   outweighs the check that supplies it."* **Is `p26`'s mechanism the same, or is
   it an idiom-recognition cliff — a different thing?**
2. **Is `p26`'s sign inversion `p19`'s (finding 35)?** `p19` inverts for a
   **complexity** reason — validation is `O(table)`, the check is `O(message)`,
   crossing at `m ≈ 2509`. ⚠ **If `p26` inverts because of a codegen CLIFF rather
   than a crossing of two rates, that is a DIFFERENT mechanism with the same
   phenomenology, and that is a result worth having** — but **measure it, do not
   assert it.**

### A.4 — the defect in the existing probe, which you must not inherit

⚠⚠ **`TASK_086`'s `p26` probe-3 number `5.33×` IS INVALID and `TASK_092` says
why: the probe pair is NOT THE SAME FUNCTION** — `k26_checked` early-returns on
capacity, `k26_unchecked` has **no capacity test at all**. **Do not reuse it.**
✅ `TASK_092`'s matched shipped-shape pair is the trustworthy one.

⚠ **AND PROBE 2 HAS FOUR KNOWN DEFECTS, THREE OF THEM FALSE-NEGATIVES ON THE
KILL CRITERION.** The object-file md5 **false-positives on relocations**; the
linked md5 **false-negatives on any kernel with a branch or a global**.
**The form that works is normalised-disassembly text — use
`.temp/t104/probe2.py`, which keeps `<SELF+0xNN>`.**

## §B — `p37`, the row whose refusal reason is refuted

The catalogue says **REFUSED-REASON-REFUTED, NEEDS RE-TRIAGE**, and names exactly
what is missing: **no C rung, no cost axis, no harm matrix, no full R5.**

✅ **What `TASK_100` established and you may build on** — `dyn Op` + an **erased
`u64`** userdata gives `4 verified, 0 errors`; `dyn Op` + a **raw-pointer**
userdata (`*mut u64` + `PointsTo`, read through `vstd::raw_ptr::ptr_ref`) gives
`3 verified, 0 errors`; **both TCB 0, zero `unsafe`, zero `external_body`, zero
`assume`**, anti-vacuity control firing. Starting material: `.temp/p37/gen_p37.py`
and `.temp/t94/v37_callback.rs`.

**Run the four probes it is missing**, and answer the one open question the
catalogue names:

⚠ **Does a `PointsTo<u64>` R5 make the type confusion UNREPRESENTABLE (`p08`'s
shape — the bug safe Rust cannot express) rather than CHECKED?** **That decides
probe 1 and it decides the row**: an unrepresentable-bug row is `p08`'s finding a
second time, which is a *weaker* reason to build; a checked-obligation row is
new.

⚠ **`p37`'s bug class is type confusion, which `p35`'s row calls ABSENT from the
built tree.** ✅ **Verify that independently** — a census, not a `grep` whitelist.
**RECAP's rule 6 exists because a whitelist grep was passed off as a census and
produced a committed false finding.**

## §C — hand the manager the six adjudications (cheap, do it last)

For each of **`p20 p21 p25 p26 p40 p41`**: extract from `TASK_086_REPORT.md` (and
any later report that moved it) **the verdict, the reason, and the measurement
that supports it**, in a form the manager can paste into a catalogue status cell.
⚠ **Quote the measurement; do not summarise it away.** ⚠ **And say for each
whether a LATER task superseded it** — `TASK_090`, `TASK_092`, `TASK_093` and
`TASK_100` all touch these rows.

⚠ **`p20` is the one to look hardest at.** It is Heartbleed-shaped — a *trusted
length field* — and `TASK_086` deferred it partly because it *"is p16's and
p02's"*. ⚠ **`p17` is already built and IS a trusted-length-field leak.** **Say
whether `p20`'s deferral reason still holds with `p17` shipped**, and note
`TASK_086`'s own disclosure that ⚠ **`p20`'s `leaked_secret_bytes=1616` counts
coincidental `0x53` bytes**, i.e. that figure is contaminated.

---

## Constraints

- **`.temp/t115/` only. No `/tmp`.** **Notes in `.temp/t115/NOTES.md` as you go.**
  Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠⚠ **DO NOT create a `patterns/p26-*/` or `patterns/p37-*/` directory. You are
  probing, not building.** The BUILD/REFUSE call is the manager's, from your
  measurements.
- ⚠⚠ **DO NOT RUN `harness/check.py`, `harness/build.py` or `harness/measure.py`**
  (except `measure.py --check-stale`). **A gate run rewrites `results/gate/*.json`,
  which both concurrent reviewers are READING.** Build your probes with direct
  `clang`/`gcc`/`rustc` calls under `.temp/t115/`, the way `.temp/t86/build.sh`
  does.
- ⚠ **Do not edit `.memory/`, `RECAP.md`, `results/`, `synthesis/`, `harness/`,
  `pilot/` or any `patterns/*/` file.**
- ⚠ **Callgrind `Ir` is deterministic and immune to the other agents' load.**
  **Wall clock is not — if you take any timing, repeat it and say a second and
  third agent were running.** ⚠ **Prefer `Ir`; this project's rules already say
  deterministic metrics are primary.**
- ⚠ **Every probe needs an arm that MUST FIRE.** The list at the end of
  `.memory/03-measurement.md` holds **six live entries numbered 1–7** (entry 5 is
  retracted). ⚠ **Do not quote its ordinal — doing so is itself a documented
  failure, committed five times by the manager after writing the rule against it.**
- ⚠⚠ **Hand-run ASan needs `env -u LD_PRELOAD`** — this shell inherits
  `LD_PRELOAD=/usr/libexec/coreutils/libstdbuf.so` and a dynamically linked ASan
  binary **refuses to start behind it, exiting 1 with no `AddressSanitizer`
  string**, which looks exactly like "no bug found". ⚠ **NEVER truncate a
  sanitiser log with `head`** — `TASK_086`'s `head -4` hid ASan's banner for
  **four rows, including `p26`'s and `p41`'s**, and that is a defect in the very
  report you are reading. **Use `grep`, and give every harm probe a positive
  control that must fire.**
- Verus via `./verus_run.py` only, single-file mode. Do not bump the pin.
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_115_REPORT.md` as well as returning it.
**Recommend BUILD or REFUSE for each of `p26` and `p37`, with the measurement
that decides it.**

---

⚠ **PROTOCOL rule 2's running count is 414, and `TASK_113` and `TASK_114` were
launched from the same value in parallel.** ⚠ **Report YOUR increment as a branch
delta — *"414 + N on this branch"* — and do not reconcile with the other agents.
Reconciliation is the manager's job.**

The calls I am least sure of:

1. ⚠⚠ **That `p26`'s 8387 is an idiom artefact rather than a real safety price
   (§A.1).** If I am wrong, **finding 37's "only if" half has a counterexample**
   and the reason this project stopped building is weaker than it looks.
   **This is the single most valuable thing in the task.**
2. **That `p26` is worth building at all** given `TASK_086`'s own kill risk that
   it is *"p13's finding, second instance"*. ⚠ **If §A.3 says it IS p13 again,
   REFUSE it and say so plainly** — a second instance of a known finding is not
   worth a pattern, and *"the catalogue really is measured out"* is a perfectly
   good answer that I would rather have with evidence than by assumption.
3. ⚠ **That `p37` is re-triageable at all without a C rung.** Its whole
   distinguishing feature is `void*` erasure, which is a **C** idiom; if the Rust
   side cannot express the confusion at all, the row may be `p08`'s shape and
   should be refused on that ground rather than kept open.

Carry **414** forward, incremented by what you find, **as a branch delta.**
