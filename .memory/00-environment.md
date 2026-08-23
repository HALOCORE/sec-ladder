# Environment — the box, the toolchain, the constraints

Facts about the machine every agent works on. Verify before contradicting; update
this file (and say so in your report) if a fact goes stale.

## Machine

- 2× Intel Xeon Gold 6230 @ 2.10 GHz, 20 cores/socket, 2 threads/core = **80 logical CPUs**.
- Governor `powersave`, frequency scaling active (observed ~24% of max at idle).
- **`scaling_cur_freq` is unusable on this box.** Re-confirmed twice: it reports
  **800 MHz under load** while the pinned core is retiring ~2.8 G dependent
  `addq`s per second. Never derive cycles from it.
- **And the replacement is not stable either — this box's clock is set by other
  tenants.** The dependent-chain probe (time a 1-cycle-per-iteration loop,
  divide) is the right *method*, but it does not give a reusable constant:

  | session | CPU 3 | CPU 5 |
  |---|---|---|
  | TASK_011_REVIEW | 3801–3888 MHz | 3771–3874 MHz |
  | TASK_012 (same `clock.c`, same pinning) | **2764–2861 MHz** | **2551–2719 MHz** |

  That is the Xeon Gold 6230's one-core turbo (3.9 GHz) against its all-core
  turbo (~2.8 GHz) on a shared, containerised host. The same 0.784–0.791 ns/byte
  is therefore **2.2 or 3.1 cycles/byte depending on when you ask**.

  **Rule: never quote cycles from a clock measured in a different session.**
  Measure it *interleaved* with the wall-clock reps — the probe costs ~300 ms —
  or report ns and stop. Quoting a cross-session clock is the same class of error
  as writing up a finding from a report without re-measuring, one level down.

  **Interleaving is necessary but not sufficient.** At TASK_013 the probe was run
  interleaved with the wall reps, on one pinned core, inside one session — and
  still read **3236 / 3732 / 3816 MHz** (min / med / max). So even done correctly,
  a cycles figure carries **±15%**. Quote the band or do not quote cycles.

  Consequence worth knowing: **`ns` is a measurement on this box and `cycles` is
  an inference.** Prefer ns for anything published.
- **Shared box, containerised** (`/dev/vg1/containers_apt`). Wall-clock timing is noisy.
- ~111 GB free on `/` (of 252 GB) after the 2026-08-18 sweep below. The 12 GB LLVM
  install is the big fixed consumer; re-check with `df -h /` rather than trusting
  this line.
- **`.temp/` is the other big consumer and it grows without bound.** It reached
  **12 GB across 24 tasks** — 6.4 GB of compiled cell binaries, 4.9 GB of
  generated input blobs, 0.2 GB of `.o`/`.pyc` — against **36 MB of the text that
  was actually the evidence**. Swept 2026-08-18 to 574 MB; see constraint 6.
- **No root.** Everything installs into `~/tools/` or `~/.cargo/`. No `sudo`.
- Network works (GitHub, crates.io, static.rust-lang.org all reachable).

## Installed

| Tool | Version | Location |
|---|---|---|
| Verus | `0.2026.08.09.92f466f` | `~/tools/verus` (symlink) |
| vstd pin | `=0.0.0-2026-08-09-0044` | must match driver; on crates.io |
| rustc/cargo | 1.97.1 — `stable` **and** `1.97.1-x86_64-unknown-linux-gnu` | `~/.cargo/bin` (rustup) |
| z3 | bundled | `~/tools/verus/z3` |
| gcc | 13.3.0 | `/usr/bin/gcc` |
| **clang / LLVM** | **22.1.6** | `~/tools/llvm` (symlink → `llvm-22.1.6`); 12 GB on disk |
| **valgrind + callgrind** | **3.27.1**, built from source | `~/tools/valgrind` (symlink → `valgrind-3.27.1`) |
| binutils | objdump, readelf, nm | `/usr/bin` |
| cmake | present | `/usr/bin/cmake` |
| taskset | present (use for pinning) | `/usr/bin/taskset` |
| python3 | present | `/usr/bin/python3` |
| perl | 5.38.2 — `callgrind_annotate` needs it | `/usr/bin/perl` |

Verus, clang and valgrind are deliberately **not on PATH**. Use `./verus_run.py`
for Verus and absolute paths for the others (`~/tools/llvm/bin/clang`,
`~/tools/valgrind/bin/valgrind`, `~/tools/valgrind/bin/callgrind_annotate`).
Reproduction commands: `TOOLCHAIN.md`.

**`rustc`/`cargo` are not on PATH either** in a non-interactive shell (rustup's
`~/.cargo/env` is only sourced by login shells). Use `~/.cargo/bin/rustc`.
`harness/build.py` does; `verus_run.py` prepends `~/.cargo/bin` for Verus's
benefit. A bare `rustc` gives "command not found".

**This box's gcc default-enables `_FORTIFY_SOURCE` at level 3.** Ubuntu 24.04,
gcc 13.3.0 (`Ubuntu 13.3.0-6ubuntu2~24.04.1`); confirm with
`/usr/bin/gcc -O2 -dM -E - </dev/null | grep -i fortify` → `#define _FORTIFY_SOURCE 3`.
`harness/build.py` passes no `-D_FORTIFY_SOURCE` either way, so **every gcc `-O`
build in this repo is a fortified build** and clang's is not. Two consequences,
both already bitten: a `memcpy` whose destination size gcc can see becomes
`__memcpy_chk@plt` (so any symbol matching in `harness/asm.py` must recognise the
`_chk` forms — fixed at TASK_006, 20 selftest cases), and a gcc `-O3 -flto` build
of a deliberately-overflowing kernel *aborts* where the same source under clang
is silent, which is a distro default and not a property of the program
(p02 `NOTES.md` §1a). Level 3 uses `__builtin_dynamic_object_size`, so it fires
on more shapes than level 2 would.

**`_FORTIFY_SOURCE` blinds ASan to `mem*` misuse, under clang as well as gcc.**
Measured at TASK_014 and reproduced at TASK_014_REVIEW. ASan's overlap and
bounds checks for `memcpy` live in its **`memcpy` interceptor**; at fortify
level 3 a call whose destination has a computable
`__builtin_dynamic_object_size` is rewritten to **`__memcpy_chk`**, which ASan
does **not** intercept. Isolated to that one flag, same source:

| build | call emitted | overlapping `memcpy` |
|---|---|---|
| gcc, box default (fortify 3) | `__memcpy_chk@plt` | **silent, exit 0** |
| gcc `-U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0` | `__interceptor_memcpy` | fires, exit 1 |
| clang, default (no fortify) | `__asan_memcpy` | fires, exit 1 |
| clang `-D_FORTIFY_SOURCE=3` | `__memcpy_chk@plt` | **silent, exit 0** |

**The discriminator is `_chk`, not the compiler.** Consequence for the gate:
`harness/check.py` stage 7 builds gcc-only at this box's defaults, so it is
structurally blind to any `mem*`/`str*` misuse gcc rewrites to a `_chk` form.
p02 was checked and is **not** affected — its ASan kernel calls
`__interceptor_memcpy` and fires on three inputs.

**glibc 2.39 x86-64 `memcpy` *is* `memmove`.** One function, one address, with a
`dst-src < n → backward copy` branch; `__memcpy_chk` and `__memmove_chk` alias
the same way. So overlapping-`memcpy` UB cannot be made to misbehave on this
box, at any size, under any `GLIBC_TUNABLES` hwcaps setting (320 runs, TASK_014).

**valgrind memcheck is partly usable, and the earlier blanket "unusable" was too
strong** (corrected at TASK_042_REVIEW, which used it successfully). Precisely:

- **Dynamic binaries: no.** Refuses to start (`must-be-redirected ... memcmp in
  ld-linux-x86-64.so.2`, wants `libc6-dbg`, which needs root).
- **`mem*`/`str*` interception: no**, even static — `--trace-redir=yes` shows
  three vDSO redirections and **zero** `mem*`/`str*` ones, so the interceptors
  that would report an **overlap** are not installed. p08's detection story
  genuinely cannot use memcheck, which is where the blanket claim came from.
- **V-bit (uninitialised-value) tracking on a STATIC build: YES, and it works.**
  That is exactly what *"is this rung reading memory nobody wrote?"* needs — the
  question behind every "is R1's answer reproducible across runs?" claim.

```bash
gcc ... -static -o prog          # static is required
~/tools/valgrind/bin/valgrind --tool=memcheck --track-origins=yes -q ./prog ...
```

Ignore the one `__libc_setup_tls` → `_IO_cleanup` report: it is glibc's own
static-TLS artefact, present on a program that does nothing. **Scope any verdict
to the kernel symbol**; a clean kernel with that one report standing is a pass.

**ASan/UBSan need `-static-libasan -static-libubsan`.** The container ships
`LD_PRELOAD=/usr/libexec/coreutils/libstdbuf.so`, and the *shared* ASan runtime
then refuses to start ("ASan runtime does not come first in initial library
list"). Static linking sidesteps it; `harness/check.py` builds that way.

**clang 22.1.6 == rustc 1.97.1's LLVM 22.1.6** — identical major/minor/patch, so
clang-vs-rustc is a genuine same-backend comparison and needs no version caveat
today. Re-check with `rustc --version --verbose | grep LLVM` after any toolchain
bump; if they diverge, every same-backend claim in `results/` must be re-labelled.

## Missing, and why it matters

| Missing | Consequence | Fix |
|---|---|---|
| `perf` | — | needs root to install |
| `perf_event_paranoid=3` | **no hardware counters at all** (IPC, branch miss, cache miss) even if perf were installed — but see the simulator note below, which is what the project should have been using for 28 tasks | needs root to relax to ≤1 |
| `hyperfine`, `gdb`, `numactl`, `ninja` | minor; work around | — |

`valgrind` and `clang` were the other two gaps. Both closed in TASK_001; they are
in the installed table above. Hardware counters remain the only hard gap.

## Branch and cache behaviour ARE measurable here — by simulation (TASK_026_REVIEW)

**This was missed for 28 tasks and it cost real work.** The table above says "no
hardware counters", and that was read across the project as *branch misprediction
is unmeasurable on this box*, so p07 built a whole `cmov`-pass control to infer by
construction what one flag reports directly. Callgrind 3.27.1 has both simulators
and both run here:

```
valgrind --tool=callgrind --branch-sim=yes  ->  Bc, Bcm, Bi, Bim
valgrind --tool=callgrind --cache-sim=yes   ->  D1mr, DLmr, I1mr, ...
```

Measured on p07 (`.temp/r26/branchsim.py`, `cachesim.py`), per call:

| build | input | `Ir` | `Bc` | `Bcm` | `Bcm/Bc` |
|---|---|---:|---:|---:|---:|
| unsafe branchy | small | 6582.98 | 1392.09 | 271.16 | 0.1948 |
| unsafe branchless | small | 7245.77 | 958.40 | 59.45 | 0.0620 |
| unsafe branchy | large | 21356.70 | 4825.21 | 853.98 | 0.1770 |
| unsafe branchless | large | 23691.98 | 3264.14 | 93.07 | 0.0285 |

0.586 mispredicts per probe on a binary search is exactly what a coin-flip branch
should give, which is the sanity check that the simulator is modelling the right
thing.

**Three rules, because a simulator is not a counter:**

1. **It is a MODEL, not this CPU.** Callgrind's predictor is a generic
   two-level scheme, not Cascade Lake's. Report `Bcm` as *simulated* and never
   convert it to cycles without saying so. It is strong evidence about
   *direction* and *ratio*, weak about magnitude.
2. **`--cache-sim` is how you rule out the locality confound**, which is
   otherwise entangled with every branch story: on p07 the `cmov` lever moved
   `Bcm` by −78% while `D1mr` was **identical** (1076.82 both builds), which is
   what makes the branch attribution stick.
3. **Both slow callgrind down substantially.** Use them for a named question on
   a few cells, not across a matrix.
4. ⚠ **THE CONDITIONAL AND INDIRECT HALVES ARE NOT EQUALLY GOOD, AND THE ABOVE
   IS ESTABLISHED ONLY FOR THE CONDITIONAL HALF** (TASK_073, on p36 — added
   because rule 1's *"strong evidence about direction"* was read as covering
   both, and on p36 it is wrong in **direction**).
   **`Bi` COUNTS and is exact; `Bim` DOES NOT PREDICT.** Measured on p36, one
   binary, inputs differing only in the *order* of a fixed opcode multiset:
   `mixrun001` simulates **99.87%** mispredict and is among the **fastest**
   cells; `mixrand` simulates 86.6% and is the **slowest**. Sharper still,
   `mixrand6` and `mixrand` have **identical `Ir` (3359.0000) and identical `Bi`
   (513089)**, `Bim/Bi` of **0.8730 vs 0.8662** — a 0.8-point simulated
   difference — and **1843.56 ns vs 789.86 ns, a 2.33× wall-clock gap.**
   **The mechanism is that callgrind's indirect predictor is LAST-VALUE**, so it
   cannot represent the history-based target prediction a real BTB does; a
   periodic target sequence is trivial for the hardware and maximally bad for
   the model. **Use `Bi` as a count of indirect branches. Do not read `Bim` as
   evidence about time, in either direction.**

**⚠ And the limit, restated correctly at TASK_030_REVIEW.** An earlier version of
this paragraph said the simulators are *"blind to code layout"*. **They are not** —
callgrind's cache model is address-indexed and its branch predictor address-hashed,
and both register a layout move. They are blind to the **front end**: no model of
instruction fetch, the uop cache, or the JCC-erratum mitigation, which is where
100% of the effect lives. The surviving sentence, and it is the one to quote:

> **Callgrind's simulators are address-sensitive but model no part of the front
> end, so across a 27% layout mode they move by ≤6 events in 10⁸. Use them to
> attribute a cache or branch mechanism, never to detect or rank a layout
> effect.**

(TASK_029's "all cache counters 0.00 both" were *per-call marginal* values rounded
to two decimals, not absolute counts — which is how the stronger claim got made.)

**This box is Cascade Lake and carries the JCC erratum.** `family 6 model 85
stepping 7`, microcode `0x5000024` — the mitigated microcode for **Intel SKX102**,
where a 32-byte chunk containing a jump that crosses or ends on a 32-byte boundary
is not cached in the DSB. That, plus plain 32-byte fetch-window count, is the
mechanism behind every layout mode measured here. Full treatment, including the
levers for building a layout population and the two that do not work:
`.memory/03-measurement.md`, "Code layout: the 32-byte fetch grid".

**And a lever that needs no simulator at all: the workload.** Same binary, same
alignment, same element arrays, only the query distribution changed — p07's
`allbelow` executes **+7.84% more instructions and takes 71.75% less time** than
its shipped workload. That is a sharper `Ir`-vs-`ns` direction reversal than any
compiler flag produced, and it is available on any data-dependent kernel.

## Hard constraints (non-negotiable)

1. **No `/tmp`.** All scratch goes under the repo's `.temp/`, one subdir per
   category (`.temp/verus/`, `.temp/build/`, ...). `rm` is only auto-permitted there.

   ⚠ **`.temp/pNN/` IS AMBIGUOUS BETWEEN A PATTERN AND A TASK, AND IT IS A LIVE
   COLLISION** (TASK_074, caught by the engineer before any damage). `.temp/p48/`
   is **TASK_048's evidence directory** — it holds `gate-p06-BEFORE.json`,
   `oldctl/` and `resid.json`, and its `NOTES.md` opens *"TASK_048 working notes"*.
   A task file prescribing `.temp/p48/` for **pattern p48** would have had the
   engineer overwrite it. **The manager wrote exactly that prescription.**
   **Before naming a scratch dir in a task file, `ls` it.** If it exists and is
   not yours, pick another name (`.temp/p48pat/` was used) — and ⚠ **the same
   check applies to `clayout.py`'s `OUT` default**, which has already overwritten
   one pattern's `meta.json` from another pattern's copy.
2. **No blind process killing.** Never `pkill`/`killall`/substring match. Resolve an
   exact PID, confirm its full command line, kill that PID. Prefer `timeout <N> <cmd>`.

   ⚠ **And no self-matching `pgrep` wait-loops — this has now cost real time
   twice and was in nobody's file until TASK_070.** A loop like

   ```bash
   until ! pgrep -f "harness/check.py p22"; do sleep 30; done      # NEVER EXITS
   ```

   **contains its own pattern in its own command line**, so it matches itself —
   and several such loops match each other. p22's engineer ran six, none could
   ever exit, and **no `python3 harness/check.py` process existed at all**; the
   "still running" report was entirely self-inflicted. Diagnosed by reading
   `/proc/<pid>/cmdline` for each PID, which is the right way.

   **Use `timeout <N> <cmd>` in the FOREGROUND and read the exit status.** If you
   genuinely must wait on something, match on a file or a marker the job writes,
   never on a command line your own waiter also has. ⚠ **And no `nohup … &`** —
   a job you cannot see the exit status of is a job whose failure you will
   attribute to something else.
3. **No GitHub/CI infrastructure.** No `.github/`, no CI config, no badges.
4. **Subagents never run `git commit`/`git add`** or any history-mutating git command.
   Read-only git is fine. The manager commits at task boundaries.
5. **No root, no system package installs.** `~/tools/` only.
6. **Keep the generator, delete the artefact.** Anything under `.temp/` that a
   committed script re-derives — compiled binaries, `.o`, `.pyc`, callgrind
   scratch, and the `.bin` input blobs that `inputs/gen.py` produces
   deterministically — is **not evidence and must not be hoarded**. The evidence
   is the text: your `NOTES.md`, the `.py` generator or probe that built the
   variant, the `.rs`/`.c` source you measured, the `.json` results and the
   `.log` of the run that produced them. Two rules follow:

   - **A binary you cannot regenerate from a file in the tree is a defect, not
     an asset.** If a probe's inputs came from an ad-hoc shell command, write the
     command into a `.py` beside the blob *before* you finish the task. This is
     the same standard `source_sha256` already enforces for patterns.
   - **Delete your task's binaries and blobs when the task's gates are green.**
     `harness/build.py` rebuilds `.temp/build/` on demand, `check.py` recreates
     `.temp/check/` and `.temp/clausemut/`, `fixture.py` rebuilds
     `.temp/build/docrepro/`, and every pattern's blobs come back from
     `inputs/gen.py` — all with `exist_ok=True`, so an absent directory costs
     time and nothing else. Do **not** delete another task's directory; report it
     and let the manager sweep.

   The 2026-08-18 sweep is recorded in `.temp/CLEANUP-MANIFEST-2026-08-18.txt`
   (path, size and mime of all 10,567 deleted files).

   ⚠ **The rule as first written here was WRONG AND DESTRUCTIVE, and it did not
   describe the sweep that was actually run** (found at TASK_042, which lost three
   evidence files to it). It said *"`file --mime-type` every file, delete the
   non-`text/*` ones"* — but **`file` reports JSON as `application/json`**, which
   is not `text/*`:

   ```
   $ file --mime-type -N results/gate/p04-ring-buffer.json
   results/gate/p04-ring-buffer.json: application/json
   ```

   That rule deletes **every `results/*.json` and every gate record** it is pointed
   at. The 2026-08-18 sweep survived only because the script actually used a
   **deny-list** — `application/x-pie-executable`, `application/octet-stream`,
   `application/x-bytecode.python`, `application/x-executable`,
   `application/x-object`, `image/x-sony-tim` — and kept everything else. **The
   documented rule and the executed rule were different**, which is the failure
   mode this project keeps finding one level up.

   **Use an explicit KEEP list by extension**, which cannot fail open:

   ```bash
   # keep .json .log .md .py .rs .c .h .txt .sh .toml ; delete the rest
   ```

   and dry-run it against a manifest before deleting anything.

   **Not covered by this, deliberately**: `patterns/*/inputs/*.bin` (p05 ~189 MB,
   p08 ~33 MB) are gitignored and equally regenerable, but they live outside
   `.temp/` where `rm` stalls on human review. They are the manager's call, not
   an agent's.
