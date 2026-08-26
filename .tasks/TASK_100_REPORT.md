# TASK_100_REPORT — the leak-detector claim, and the nine unreviewed refusals

**Role: research reviewer.** Nothing was fixed. Nothing outside `.temp/r100/` and
this file was written. `harness/check.py`, `harness/measure.py`,
`harness/build.py`, `synthesis/`, `results/` and every `patterns/*/` file were
**read only** — no execution, no edit; `TASK_099` was in flight throughout. No
`git add`, no `git commit`. Every hand-run sanitizer used `env -u LD_PRELOAD`;
every sanitizer log was `grep`'d, never `head`'d.

Scratch and rebuild scripts: `.temp/r100/` (264 KB, **zero binaries left**;
`a1_lsan.sh`, `a3_shape.sh`, `a4_selfopt.sh`, `a5_perturb.sh`, `a6_hookctl.sh`,
`a7_gatecell.sh`, `synth/setup.sh`, `b/rebuild.sh` re-derive every artefact).

---

## HEADLINE

**Both §A claims are correct measurements of two different programs, so the
manager's contradiction is manufactured — least-sure call #1 was the right one to
name. And `.memory/`'s CONCLUSION is false anyway, for a reason neither side
gave: the false negative is a stale STACK ROOT, it is removable in ONE LINE of a
pattern's own C source, and the removal costs `0.00 Ir`.**

**In §B the verdicts mostly stand and the manager's ranking was wrong: the real
defect is in `p37`, one of the three "confirm briefly and move on" rows.**

---

# §A — the leak detector

## A1 (blocker, against the manager's probe) — the contradiction is manufactured. `.memory/`'s TABLE reproduces EXACTLY.

`.temp/r93/c/leak3.c` — the program TASK_093 measured, still on disk — rebuilt at
the gate's exact stage-7 flags (`a1_lsan.sh`, flags read out of
`check.py::check_sanitizers`):

```
p93(leak3.c)  -O0 leak exit=1 120B/5   noleak exit=0 NO-REPORT   <- .memory/'s table
p93           -O1 leak exit=0 NO-REPORT noleak exit=0 NO-REPORT
p93           -O2 leak exit=0 NO-REPORT
p93           -O3 leak exit=0 NO-REPORT
m99(mgr99/leak.c) -O0 leak exit=1  80B/5
m99           -O1 leak exit=1  16B/1                             <- the manager's table
m99           -O2 leak exit=1  16B/1
m99           -O3 leak exit=1  16B/1
```

The two probes are different programs:

| | `.temp/r93/c/leak3.c` (`.memory/`) | `.temp/mgr99/leak.c` (manager) |
|---|---|---|
| structure | **doubly** linked, appended | **singly** linked, prepended |
| built in | a callee, `run()` | `main` |
| after building | a 16 KiB `volatile` stack `scrub()` | nothing |

**§A.1 is exactly what happened. Both results stand; neither refutes the other.**
This is the fourth "you measured a different thing", and the manager found it
first by naming it.

## A2 (major, against the manager's probe) — "ACCOUNTING, not DETECTION" is FALSE on the program `.memory/` measured.

The manager's `--wrap` counter, run on `leak3.c` itself:

```
p93wrap.O0 arg=1 : SLB-LEAK allocs=5 frees=0 outstanding=5 bytes_alloc=120
p93wrap.O1 arg=1 : SLB-LEAK allocs=5 frees=0 outstanding=5 bytes_alloc=120
p93wrap.O2 arg=1 : SLB-LEAK allocs=5 frees=0 outstanding=5 bytes_alloc=120
p93wrap.O0 arg=0 : allocs=5 frees=5 outstanding=0        (negative arm)
```

**Five blocks, 120 bytes, genuinely outstanding at `-O1`/`-O2`, and LSan reports
zero.** The count goes to zero. That is a detection failure, and the manager's
80→16 / 5→1 "accounting degradation" is a property of the manager's own
singly-linked program, not a general one. (It also is not constant folding: the
allocations are still there, counted.)

## A3 (blocker, against `.memory/`) — the mechanism is a stale STACK word, and it is INLINING, not shape and not `-O`.

Three diagnostics, all in `a1_lsan.sh` / `a3_shape.sh`:

```
p93.O1 LSAN_OPTIONS=''                          exit=0 NO-SUMMARY
p93.O1 LSAN_OPTIONS='use_stacks=0'              exit=1 120 byte(s) leaked in 5 allocation(s)
p93.O1 LSAN_OPTIONS='use_registers=0'           exit=0 NO-SUMMARY
p93.O1 LSAN_OPTIONS='use_stacks=0:use_registers=0' exit=1 120B/5
p93.O2  ... identical to p93.O1 in all four
shape0 -O1 (inline ok)   exit=0 NO-REPORT
shape0 -O1 -fno-inline   exit=1 120 byte(s) leaked in 5 allocation
shape0 -O2 -fno-inline   exit=1 120 byte(s) leaked in 5 allocation
```

- ⚠ **`.memory/`'s "stale register/stack reachability" is half wrong**:
  `use_registers=0` changes **nothing**; `use_stacks=0` restores **every** cell.
  It is a stack word, full stop.
- **`-fno-inline` restores it too.** Mechanism: at `-O1` gcc inlines `run()` into
  `main`, so the node pointers live in **main's** frame — and `scrub()`'s 16 KiB
  is a *deeper* frame, so it never overwrites them. At `-O0` `run()` has its own
  frame, `scrub()` sits on top of it, the roots die, LSan reports. **The scrub
  the probe added to make detection more likely is what makes the `-O` level
  matter.**
- **Answering §A.3's shape question directly: shape is NOT the variable.**
  `c/shape.c`, one source, three graphs, everything else identical:

  ```
  shape    -O   leak-arm(default)   noleak-arm(control)  leak-arm(use_stacks=0)
  SHAPE=0 singly  -O0 exit=1 120B/5   exit=0             exit=1 120B/5
  SHAPE=0         -O1 exit=0          exit=0             exit=1 120B/5
  SHAPE=1 doubly  -O1 exit=0          exit=0             exit=1 120B/5
  SHAPE=2 cyclic  -O1 exit=0          exit=0             exit=1 120B/5
  ```

  Singly, doubly and **cyclic** (p34's Rc-cycle shape) behave identically. **So
  the answer to "is there a leak SHAPE where the count goes to zero" is: yes, and
  it is every shape — the variable is the FRAME, not the graph.** The graph does
  show up in the *classification*: `leak3.c` at `-O0` reports `Indirect leak of
  120 byte(s) in 5 object(s)` with **no direct leak at all** (every node is
  pointed at by another leaked node — the doubly-linked signature), while the
  manager's singly-linked chain reports `Direct leak 16 + Indirect leak 64`.

## A4 (blocker, against `.memory/`) — ⚠⚠ THE KILL IS REMOVABLE IN ONE LINE, AND THE GATE NEEDS NO CHANGE.

ASan looks up a **weak hook the program under test may define**. Put this in the
pattern's own `c/main.c`:

```c
const char *__lsan_default_options(void) { return "use_stacks=0"; }
```

`a4_selfopt.sh` — same body as `leak3.c`, `HOOK=0` is the positive control:

```
HOOK=0 -O0  leak: exit=1 120 byte(s) leaked in 5 allocation   noleak: exit=0 NO-REPORT
HOOK=0 -O1  leak: exit=0 NO-REPORT                            noleak: exit=0 NO-REPORT
HOOK=0 -O2  leak: exit=0 NO-REPORT
HOOK=0 -O3  leak: exit=0 NO-REPORT
HOOK=1 -O0  leak: exit=1 120 byte(s) leaked in 5 allocation   noleak: exit=0 NO-REPORT
HOOK=1 -O1  leak: exit=1 120 byte(s) leaked in 5 allocation   noleak: exit=0 NO-REPORT
HOOK=1 -O2  leak: exit=1 120 byte(s) leaked in 5 allocation   noleak: exit=0 NO-REPORT
HOOK=1 -O3  leak: exit=1 120 byte(s) leaked in 5 allocation   noleak: exit=0 NO-REPORT
```

Works under `-static-libasan`. `check.py`'s `fired` predicate matches on both
`"ERROR:"` and `"AddressSanitizer"`, and the report carries both.

Three things I checked before recommending it, because a reviewer who recommends
an instrument owes the same controls it demands:

1. **It does not perturb the measured cell.** `a5_perturb.sh`, callgrind `Ir` on
   the measured C config (`-O3 -DSLB_ISOLATED`, `harness/build.py::c_flags`),
   real `common/driver.c` + p01's `c/kernel.c`:

   ```
   base  small 257362037   large 209367011
   hook  small 257362037   large 209367011    <- IDENTICAL, to the instruction
   wrap  small 257364247   large 209369261    <- +2210 / +2250
   ```

   Kernel disassembly identical modulo one trailing alignment `nopl` (an
   inter-function pad, never executed).
2. **It does not blind any other check.** `a6_hookctl.sh`, six cells, `HOOK=0`
   vs `HOOK=1`, byte-identical verdicts: `ERROR: AddressSanitizer:
   heap-use-after-free` (exit 1), `runtime error: load of address` (exit 1),
   `runtime error: signed integer overflow` (exit 0).
3. **`use_stacks=0` does not false-positive on a real pattern cell.** All eight
   p01 inputs (small, large, six adversarial) through the unmodified p01 C rung:
   silent under both default and `use_stacks=0`; `adversarial-shortlen` exits 5
   under both. (p01's `main` frees `vals` and `inp.payload`; a leak row must do
   the same on its clean path, which it must anyway.)

## A5 — answering §A.4's two questions about `--wrap`

- **Does it perturb the measured cell? YES, measured: `+2210` / `+2250` `Ir`.**
  Small, but the project's primary metric is deterministic `Ir` and this is a
  non-zero move on it. ⚠ **So `--wrap` is a HARM-PROBE-ONLY instrument. The
  `__lsan_default_options` hook is the one that can ride in the measured build.**
- **What does it miss, and does that matter for a leak-on-error-path row?** It
  counts calls, not reachability, so "freed a block, leaked a different one" nets
  to zero, and it sees only call sites in objects linked with the wrap flag (not
  allocations made inside libc, and not Rust's allocator unless linked the same
  way). ⚠ **For `p42` specifically this does not matter** — the whole shape is
  exactly one `free` skipped on one path, so the counter is off by exactly one
  and cannot cancel. It is the *wrong* instrument for `p34`, whose Rust half is a
  cycle under Rust's `GlobalAlloc`.

## A6 — ARE `p34` AND `p42` UNBLOCKED?

### `p42` — **YES on the detector axis, and it is the strongest row §A produces.**

`a7_gatecell.sh` builds a **synthetic pdir cell in scratch** — real
`common/driver.c` + p01's real `c/kernel.c` + p01's real `main.c` with a
`goto cleanup` that skips `free(vals)` — at the gate's exact stage-7 flags:

```
clean  small.bin  LSAN=''             exit=0  fired=no
clean  small.bin  LSAN='use_stacks=0' exit=0  fired=no
clean  large.bin  LSAN=''             exit=0  fired=no
clean  large.bin  LSAN='use_stacks=0' exit=0  fired=no
leak   small.bin  LSAN=''             exit=1  fired=YES  16000 byte(s) leaked in 1 allocation
leak   small.bin  LSAN='use_stacks=0' exit=1  fired=YES  16000 byte(s) leaked in 1 allocation
leak   large.bin  LSAN=''             exit=1  fired=YES  12000000 byte(s) leaked in 1 allocation
leak   large.bin  LSAN='use_stacks=0' exit=1  fired=YES  12000000 byte(s) leaked in 1 allocation
```

⚠ **My first version of this probe used `if (acc & 1)` and `acc` is EVEN for
both p01 inputs — a control that could not fire.** Caught by printing `acc`
(`17245669606222259694`, `8088771909753396726`), changed to `acc != 0`, re-run.
That is the sixth entry for the "controls that could not have failed" list, and
it is mine.

Applying the three probes + probe 4 to `p42`:

- **Probe 1 (a boundary, NAMED): PASSES.** `Drop`/RAII frees on every path in
  R2/R3; C's hand-written `goto cleanup` can miss one; R4's raw
  alloc/dealloc can too. The boundary is **R1/R4 against R2/R3**, the direction
  the tree already knows how to publish.
- **Bug class the tree does not have: CONFIRMED, and this is the strongest part.**
  A census of all 24 built patterns (spec/README/NOTES, file:line) finds **zero
  leak rows**. `p27` is constructed *not* to leak — its hashed `required` block
  says "the EPILOGUE frees every record still alive, **so neither C rung
  leaks**" (`patterns/p27-handle-table/spec.md:372`) — and forbids
  `ManuallyDrop` / `mem::forget` / `Box::leak` / `Box::into_raw`
  (`spec.md:399-402`). p16/p17/p47's "leak" is information disclosure, not memory.
- **A kernel the file-blob driver can host: YES — the probe above IS one.**
- **Probe 3 (the `0.00` axis, declared in advance):** the axis must be the
  **behaviour matrix + detector**, not cost; a skipped `free` costs nothing.
  Say so in `spec.md` §0 or this becomes p45's *"safety is free"*.
- **Probe 4 (vstd):** R5 needs a `dealloc` obligation; `p27` already threads
  `Tracked<Dealloc>`, so the route exists and is precedented.

### `p34` — **the NAMED KILL is dead. The row is still not worth building, for a DIFFERENT reason.**

The kill sentence in `.memory/06-catalogue.md:408` (*"there is NO WORKING LEAK
DETECTOR FOR THE C RUNGS ON THIS BOX"*) is refuted by A4. But `p34` does not
become buildable, and the binding constraint was never the detector:

- **Probe 1 is genuinely contested, and TASK_094's reason for that is the wrong
  one.** TASK_094 said *"every rung leaks, which is p31's condition"*. That is
  not quite it — the real problem is that the safe rung leaks **only in the
  `Rc`-both-ways spelling**, and `Weak` is equally safe, equally idiomatic and
  does not leak (`b/p34_leak.rs`: `weak: allocs=2 frees=2 delta=+0`). So the
  headline *"safe Rust loses on SAFETY"* survives only if `Rc`-both-ways is
  **pinned as the safe spelling**. The tree has exactly one precedent for pinning
  a spelling *for being safe* — p19's `forbidden` entries — and p19's whole
  headline does not rest on it. **p34's would.**
- **No cost axis has ever been measured at shipped shape** (TASK_094 says so
  itself: *"p34's cost side was not measured"*).
- So: **correct `.memory/`, do not schedule p34.** ⚠ And if it is ever
  rescheduled, note that the cyclic shape is the *hardest* case for LSan under
  default options (`SHAPE=2` above) — it needs the A4 hook, not luck.

---

# §B — the nine refusals

**Every load-bearing measurement I re-ran reproduces exactly** (`b/rebuild.sh`):

```
k39_id_masked 36895.00   k39_id_offbyone 36895.00   k39_id_unchecked 19496.00
k43_naive     26664.00   k43_tuned       23593.00   k43_unchecked   26661.00
k44_plain     12849.00   k44_unchecked   12849.00   k44_wrapping    12849.00
k44_{plain,wrapping,unchecked}  insns=67  normalised-text=fed7c19bd69d  x3  -> ONE RUNG
p30 flood  maxchain=4096 of 4096 keys in 1024 buckets
p32 DOUBLE FREE aliased=true slot[z]=1111 ; p33 USE AFTER RECYCLE 7000 -> 9000
ASAN+UBSAN gcc/clang: p32df, p33uar silent; p27ctl and p29uaf BOTH fire   <- the controls
```

| row | reason is | verdict | reason |
|---|---|---|---|
| `p34` | measurement + an **environment claim** | **stands, new reason** | ⚠ **KILL REFUTED** (§A4). Real reason: the spelling pin. |
| `p30` | measurement + an **inherited argument** | **stands** | ⚠ limb 2 reuses the retracted `E0382`/`E0499`. |
| `p43` | measurement | **stands** | ⚠ minor: corroborated against an **unbuilt** row. |
| `p44` | **measurement** | stands | sound — normalised-text, the only working form |
| `p39` | measurement + a cross-row **argument** | stands | sound, and p39 is a strict subset of p09 |
| `p29` | measurement (TASK_095) | stands | already self-corrected its own denominator |
| `p32`/`p33` | **measurement** (probe 1) | stands | sound, controls fire on both compilers |
| `p37` | measurement + an **argument** | ⚠⚠ **DOES NOT SURVIVE** | **the argument is measurably FALSE** |

## B1 (blocker) — `p37`: the second limb of the refusal is FALSE, and unlike `p28` the verdict does NOT survive it.

`p37`'s refusal has two limbs. **Limb (i) is a measurement and it reproduces**
(`b/v37_callback.rs` at the pin):

```
error: The verifier does not yet support the following Rust feature: function pointer types
  --> v37_callback.rs:17:1     <- on the STRUCT FIELD DECLARATION
  --> v37_callback.rs:22:5     <- and on the call
```

**Limb (ii) is an argument with nothing run**: *"with fn pointers inadmissible,
R5 must use `dyn Trait` — and then the userdata rides inside the trait object,
TYPED, so the erasure that IS the bug disappears."* It assumes the only carrier
for the userdata is the trait object. It is not.

```
b/v37_sub.rs   dyn Op table + an ERASED u64 userdata            -> 4 verified, 0 errors
b/v37_sub2.rs  dyn Op table + a RAW-POINTER userdata (*mut u64
               + PointsTo, read via vstd::raw_ptr::ptr_ref)     -> 3 verified, 0 errors
b/v37_sub2_mut.rs  same, one `requires` deleted                 -> 2 verified, 1 errors
                                                     "precondition not satisfied"
```

Both files carry **zero `unsafe` tokens, zero `external_body`, zero
`assume`/`assume_specification` — TCB 0** (`grep` shows only prose matches:
"assumes", "admit"). The mutation is the anti-vacuity control and it fires.

**Consequences, and they run the other way from the catalogue's ordering:**

- **`p37` is NOT "strictly worse than `p35`".** `p35` is dead on
  `_scan_unsafe_sites` (its read is `unsafe { v.i }` in a *verified* fn) and on
  *"no configuration in which its obligation is CHECKED"*. The R5 above has **no
  `unsafe` token to scan** and its obligation (`pt.ptr() == ud`, `pt.is_init()`)
  **is** checked, by Verus, non-vacuously. On both axes that killed `p35`,
  `p37` is **better**, not worse.
- **The class survives the substitution in both a value form and a pointer
  form**, so *"the erasure disappears"* is false as written.
- ⚠ **What I did NOT establish:** a C rung, a cost axis, a harm matrix, or that
  a `PointsTo<u64>` R5 is the right R5 (Verus's type discipline arguably makes
  the confusion *unrepresentable*, which would be a p08-shaped compile-time
  boundary — admissible under probe 1, but it needs saying). **I am not
  overturning `p37`; I am reporting that its stated reason is refuted and the
  verdict is not independently supported. It needs a re-triage, not a rubber
  stamp.**

⚠⚠ **This is the manager's least-sure call #2, and the manager ranked it wrong:
`p37` was in the "confirm briefly and move on" group.**

## B2 (major) — `p34`: `.memory/`'s leak number is scoped to the wrong window.

`.memory/06-catalogue.md:408` publishes *"TASK_094 measured `3 allocs / 0 frees /
324 bytes`"*. TASK_094's `band!` macro returns a `format!` String **from inside
the measured window** — TASK_094's own report says so (*"the constant +1 alloc /
0 free skew in every band is the `format!` String"*) — and the catalogue quotes
the raw triple anyway. Re-measured with nothing else in the window
(`b/p34_leak.rs`, counting `GlobalAlloc`, rows under `#![forbid(unsafe_code)]`):

```
size_of::<RcNode>() = 104
cycle : allocs=2 frees=0 live_bytes_delta=+240     <- the leak
weak  : allocs=2 frees=2 live_bytes_delta=+0       <- the control, balanced
format!: allocs=1 bytes=44 (len=44)                <- what the band! added
```

**The leak is 2 allocations / 240 bytes** (104-byte node + 16-byte `Rc` header =
120, ×2), not 3 / 324. This is the same *class* of defect the manager asked about
in §B (`p29`'s `−0.00024` vs `+48.01`): a number scoped to a window that includes
something that is not the phenomenon. It does not change the verdict.

## B3 (major) — `p30`: the refusal's second limb reuses the argument the catalogue itself retracted.

`p30`'s primary reason is a measurement and it reproduces exactly
(`p30 flood maxchain=4096 of 4096 keys in 1024 buckets`, terminates). But
TASK_094's chain continues: *"the only spelling that would hang is an intrusive
chain … and TASK_093 measured that safe Rust cannot express an owned intrusive
list (`E0382` + `E0499`)."* ⚠ **That is the exact sentence `TASK_093_REVIEW`
rejected**, and `.memory/06-catalogue.md:380` says in as many words: *"do not
reuse TASK_093's `E0382`/`E0499` argument, which is false."* The refusal's
second limb is dead on arrival; the first carries the row.

**And the grep the manager asked for, run** (24-pattern census, file:line):

- **An unreduced bucket index is NOT novel.** No built pattern models one — but
  the *missing modulo* is `p06`'s exact line (`patterns/p06-rotate/spec.md:374`,
  *"the only line `c/kernel.c` omits: `r %= m;`"*) and the resulting access is an
  `index >= len`, which **14 patterns already carry and 13 already model a bug
  on** (`patterns/p46-bignum-mac/spec.md:28-31` enumerates them). It would be the
  15th.
- **The resize path is NOT `p30`'s to take.** No built pattern models a
  realloc/growth bug — zero hits for `realloc|resize|reserve|push|with_capacity`
  in any exec kernel — but the class is already catalogued as its own row:
  `p25 | dynamic array with realloc growth | growth overflow, stale pointer |
  planned` (`.memory/06-catalogue.md:372`). Refusing `p30` does not lose it.

**So `p30`'s verdict stands, and now for a reason that was measured rather than
inherited.**

## B4 (minor) — `p43`: corroborated against a row that does not exist.

`.memory/06-catalogue.md:427` says p43 is *"`p16`/`p20` verbatim"*. **`p20` is
`planned`, not built** (`.memory/06-catalogue.md:362`), and the `+10.00 flat`
traces to `TASK_086_REPORT.md:260` — an **unreviewed probe of an unbuilt row**.
Duplication against an unbuilt row is not duplication; if anything it says p43
*is* p20. The `p16` half is a built, reviewed pattern and carries the refusal on
its own. The measurement reproduces (`+3.00 Ir`/call, `−3068 = −0.749 Ir`/byte
for tuned-beats-unsafe).

## B5 (confirmed, brief) — `p44`, `p39`, `p32`/`p33`, `p29`

- **`p44` — sound, and it is the best-evidenced refusal of the nine.** The kill
  is intra-row and uses the **only form of probe 2 that works**: normalised
  disassembly text, `insns=67 / mnemonic-multiset f815d5d3b2f4 / normalised-text
  fed7c19bd69d` for all three, corroborated by `12849.00` three times. **None of
  the three rows the manager worried about (`p43`/`p44`/`p39`) was refused on a
  broken probe** — `p44` is the row that *discovered* the defect.
- **`p39` — sound, and the similarity claim is a strict-subset one.** The
  complete disassembly diff of `k39_id_masked` vs `k39_id_offbyone` is, modulo
  addresses / jump targets / `%rip` displacements, exactly `and $0x1ff,%r8d` →
  `and $0x3ff,%r8d`, at `36895.00` vs `36895.00`. ⚠ **The cross-row half is an
  argument, not a normalised comparison** — p39's kernels were never diffed
  against p09's. It survives anyway, and *more* strongly than stated: p09 ships
  **both** halves of *"one character between a bug everything catches and one
  nothing does"* (`q >> 5` overshoots and is caught; `q >> 7` undershoots and is
  caught by nothing — `p09/spec.md:365`), while p39's measured bug is only the
  **caught** half. p39 is a subset of p09, not a sibling.
- **`p32`/`p33` — sound.** Probe 1 is the strongest kill available and it is a
  measurement, and the detector matrix has a **positive control that fires on
  both compilers**: `p27ctl` and `p29uaf` → `ERROR: AddressSanitizer:
  heap-use-after-free` on gcc and clang, in exactly the configurations where
  `p32df`/`p33uar` are silent (`logs/detect.log`).
- **`p29` — sound, and TASK_095 already caught its own denominator error.** The
  one *other* wrongly-scoped number I found is `p34`'s (B2), not `p29`'s.

---

## Clean negatives — named attacks that did NOT land. Do not re-run these.

1. **"`.memory/`'s table is a probe artefact of a mid-program
   `__lsan_do_recoverable_leak_check()`" — the manager's own untested §A.2
   hypothesis. FALSE.** `.temp/r93/c/leak4.c` at gate flags: at `-O0` the
   mid-program call **fires**, printing *two* reports (the recoverable one and
   the at-exit one; stdout is lost because ASan `Die()`s without flushing stdio).
   At `-O1`/`-O2` it returns 0, matching the at-exit result exactly. The
   mid-program call is not the explanation — the stale stack root is.
2. **"The `-O1` silence is constant folding / malloc elision." FALSE.** The
   `--wrap` counter reads `allocs=5 outstanding=5 bytes_alloc=120` at every level
   on the same source.
3. **"Leak-graph shape (singly / doubly / cyclic) is what decides detection."
   FALSE.** `a3_shape.sh`: all three shapes fire at `-O0`, all three go silent at
   `-O1`/`-O2`, all three come back under `use_stacks=0`.
4. **"`use_stacks=0` will false-positive across the tree." FALSE** on the one
   pattern I could test end-to-end: all 8 p01 inputs silent under it.
5. **"The `__lsan_default_options` hook blinds ASan or UBSan." FALSE** —
   `a6_hookctl.sh`, six cells identical with and without.
6. **"The hook perturbs the measured cell." FALSE** — `Ir` identical to the
   instruction on both inputs; only `--wrap` moves it.
7. **"`p43`/`p44`/`p39` were refused on the broken form of probe 2." FALSE** —
   all three used the normalised-text form; `p44` is where the defect was found.
8. **"`p32`/`p33`'s silence is the harness's, not the bug's." FALSE** —
   `p27ctl`/`p29uaf` fire in every configuration where they are silent.
9. **valgrind memcheck**: I did not re-run it. The manager's Result 1 already
   reports it as a clean negative with both `LD_PRELOAD` arms, and it needs root.
10. **`LSAN_OPTIONS=use_globals=0`** is **not** a usable substitute for
    `use_stacks=0`: it adds a 4096-byte false leak (stdio's buffer, rooted in a
    global) at every level.

---

## The three calls the manager was least sure of

**1. "That my leak probe contradicts `.memory/` at all."**
⚠ **You were right to doubt it — it does not.** Both tables reproduce exactly at
the gate's own flags, on two programs that differ in three ways (§A1). This would
have been the fourth manager claim to die to *"you measured a different thing"*,
and you found it before `.memory/` did. **But `.memory/` still needs correcting**,
because its *conclusion* is false for a reason neither probe reached: the failure
is a stale **stack** root (not a register, not the graph, not the `-O` level per
se), it is caused by **inlining the allocating frame into a frame nothing
overwrites**, and it is removed by **one line in the pattern's own C source** at
**zero `Ir`**. Your probe is not the evidence that refutes `.memory/`; `a4_selfopt.sh`
and `a7_gatecell.sh` are.

**2. "That the nine refusals are mostly sound." — Mostly, and you ranked it wrong.**
Eight verdicts stand. The one that does not survive its reason is **`p37`**, which
you put in the "confirm briefly and move on" group; its second limb is refuted by
two Verus runs and, on both axes that killed `p35`, `p37` measures *better* than
`p35` rather than *"strictly worse"*. The rows you ranked highest were fine:
`p30`'s measurement is sound (its inherited `E0382` limb is not), `p43`/`p44`/`p39`
all used the working form of probe 2, and `p29`'s report had already disclosed its
own denominator error. **The other wrongly-scoped number is in `p34`, in
`.memory/` (B2).**

**3. "That `p34` is worth reopening even if §A clears it." — No, and that is the
honest answer you said you would accept.**
The detector exists now, so the row's **named kill is wrong and must be
corrected** — but the detector was never the binding constraint. `p34`'s headline
needs `Rc`-both-ways **pinned as the safe spelling** when `Weak` is equally safe,
equally idiomatic and measured leak-free, and the tree's one precedent for such a
pin (p19) does not rest its headline on it. **`p42` is the row §A actually
unblocks**, and it is worth more than `p34`: it fires at the gate's exact
stage-7 flags today with no hook at all, its boundary is RAII-vs-`goto cleanup`,
and the 24-pattern census says **memory leak is a bug class the built tree does
not have** — the only such class left that a file-blob kernel can host.

---

## Problems / worked around

- I could not run `harness/check.py`, so every gate-behaviour claim is from a
  **synthetic pdir built in `.temp/r100/synth/`** out of copies of
  `common/driver.c` and p01's `c/{kernel.c,kernel.h,main.c}` at the flag string
  read out of `check_sanitizers`. If those flags move, my §A6 result moves.
- My first `p42` probe used `acc & 1`, which is 0 for both p01 inputs — a control
  that could not fire. Found by printing `acc`. Disclosed in
  `.temp/r100/synth/setup.sh` and in `NOTES.md`.

## Unsure / not done

- **`p37` is reported, not overturned.** No C rung, no cost axis, no harm matrix,
  no full R5. Whether a `PointsTo<u64>` R5 makes the confusion *unrepresentable*
  (a p08-shaped boundary) rather than *checked* is open and matters for probe 1.
- **`p42` is unblocked on the DETECTOR axis only.** I did not build a kernel, did
  not check that a leak row's `model.py` can express `sanitizer_expect: "fires"`
  on an adversarial input against the actual gate, and did not price R5's
  `dealloc` obligation.
- **`use_stacks=0` was validated against exactly one pattern (p01)**, and only
  the C rung. A pattern that legitimately holds an allocation on the stack at
  exit would false-positive under it; that is the hook's one cost.
- **`--wrap`'s `+2210 Ir`** was measured on the synthetic p01 cell; the constant
  will differ per pattern. The sign will not.
- I did not re-run **valgrind**, **Miri**, `p29`'s R5, or `p95`'s mutant battery;
  I did not re-derive `p34`'s Rust-side Miri leak counts (`5 memory leaked`).
- `p32`/`p33`, `p29`, `p44` were confirmed rather than attacked hard — the time
  went to `p37` and §A, per the evidence.

## Memory updates owed (manager applies, after this review)

1. ⚠⚠ **`.memory/00-environment.md`, the section "THERE IS NO WORKING LEAK
   DETECTOR FOR THE C RUNGS ON THIS BOX": the heading is FALSE and the table is
   TRUE.** Keep the table (it reproduces exactly, on `.temp/r93/c/leak3.c`).
   Replace the conclusion with the mechanism: **a stale STACK root**
   (`use_registers=0` changes nothing; `use_stacks=0` restores every cell), kept
   alive by **inlining the allocating callee into a frame nothing overwrites**
   (`-fno-inline` also restores it), independent of leak-graph shape. Record the
   fix — `const char *__lsan_default_options(void){ return "use_stacks=0"; }` in
   the pattern's own `c/main.c` — with its three controls: `Ir`-neutral, does not
   blind ASan/UBSan, does not false-positive on p01's eight inputs.
   Cite `.tasks/TASK_100_REPORT.md` §A3–A4 and `.temp/r100/`.
2. **`.memory/06-catalogue.md` `p34`: strike the NAMED KILL** and replace it with
   the real one — **the row needs `Rc`-both-ways pinned as the safe spelling
   while `Weak` is equally safe and measured leak-free** — and **correct the leak
   number from `3 allocs / 0 frees / 324 bytes` to `2 allocs / 0 frees / 240
   bytes`** (the 324 includes TASK_094's own `format!` String).
3. **`.memory/06-catalogue.md` `p42`: UNBLOCK.** The named blocker is refuted; the
   shape fires at the gate's exact stage-7 flags today, both arms, with
   `common/driver.c` and a real kernel. Note that **leak is a bug class the built
   tree does not have** (24-pattern census) and that `p27` forbids it by contract.
4. ⚠⚠ **`.memory/06-catalogue.md` `p37`: the refusal's second limb is FALSE.**
   `dyn Op` + an erased userdata verifies at the pin in both a value form (`4/0`)
   and a raw-pointer form (`3/0`), TCB 0, zero `unsafe`, non-vacuous by mutation.
   **Strike *"strictly worse than p35"*** — on `_scan_unsafe_sites` and on
   *"the obligation is checked"* it measures better. Mark the row
   **REFUSED-REASON-REFUTED, needs re-triage**, not REFUSED.
5. **`.memory/06-catalogue.md` `p30`: the second limb reuses the retracted
   `E0382`/`E0499` argument.** Replace it with the census result: an unreduced
   bucket index is `p06`'s missing modulo reaching the tree's 15th `index >= len`,
   and the resize path is **`p25`'s** row, still `planned`. Verdict unchanged.
6. **`.memory/06-catalogue.md` `p43`: `p20` is `planned`, not built**, and its
   `+10.00` is TASK_086's unreviewed probe. Cite `p16` alone.
7. **`.memory/02-bench-rules.md` (or `03-measurement.md`): a linker `--wrap`
   allocation counter PERTURBS the measured cell** (`+2210` / `+2250 Ir` on the
   p01-shaped cell at `-O3 isolated`) and is therefore **harm-probe-only**;
   `__lsan_default_options` does not (`Ir` identical to the instruction).
8. **Controls-that-could-not-fire list: add `acc & 1` on p01's inputs** (both
   `acc` values are even). Mine, caught before it reached a conclusion.

---

⚠ **PROTOCOL rule 2 running count: 301 → 313.** (`TASK_099` carries its own
increment; the manager reconciles.)

| # | contradiction, with the run that produced it |
|---|---|
| 302 | The manager's probe does **not** contradict `.memory/`; both tables reproduce exactly on two different programs (`a1_lsan.sh`). Least-sure call #1, upheld. |
| 303 | *"The `-O` dependence is ACCOUNTING, not DETECTION"* is false on `.memory/`'s program: 5 blocks / 120 bytes outstanding, 0 reported (`--wrap` on `leak3.c`). |
| 304 | The manager's untested mid-program `__lsan_do_recoverable_leak_check` hypothesis is false — it fires at `-O0` (`leak4.c`). |
| 305 | Leak-graph **shape** is not the variable: singly, doubly and cyclic behave identically (`a3_shape.sh`). |
| 306 | `.memory/`'s *"stale register/stack"* is stack-only: `use_registers=0` changes nothing, `use_stacks=0` restores every cell. |
| 307 | ⚠⚠ `.memory/`'s conclusion *"no leak detector at the gate's configuration"* is false — one in-source line makes LSan fire at every level (`a4_selfopt.sh`). |
| 308 | `--wrap` perturbs the measured cell (`+2210`/`+2250 Ir`); the hook does not (`a5_perturb.sh`). |
| 309 | `p42`'s shape already fires at the gate's exact stage-7 flags with default options, on a real driver + kernel (`a7_gatecell.sh`). |
| 310 | ⚠⚠ `p37`'s second limb is false: `dyn Op` + erased userdata verifies `4/0`, + raw-pointer userdata `3/0`, TCB 0, non-vacuous. |
| 311 | `p34`'s `.memory/` leak figure is scoped wrong: 2 allocs / 240 bytes, not 3 / 324 (`b/p34_leak.rs`). |
| 312 | `p30`'s refusal reuses the `E0382`/`E0499` argument the catalogue itself retracts. |
| 313 | `p43`'s refusal corroborates against `p20`, which is `planned`, not built. |
