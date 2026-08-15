# Environment — the box, the toolchain, the constraints

Facts about the machine every agent works on. Verify before contradicting; update
this file (and say so in your report) if a fact goes stale.

## Machine

- 2× Intel Xeon Gold 6230 @ 2.10 GHz, 20 cores/socket, 2 threads/core = **80 logical CPUs**.
- Governor `powersave`, frequency scaling active (observed ~24% of max at idle).
- **Shared box, containerised** (`/dev/vg1/containers_apt`). Wall-clock timing is noisy.
- ~118 GB free on `/` (of 252 GB). The 12 GB LLVM install is the big consumer;
  re-check with `df -h /` rather than trusting this line.
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
| `perf_event_paranoid=3` | **no hardware counters at all** (IPC, branch miss, cache miss) even if perf were installed | needs root to relax to ≤1 |
| `hyperfine`, `gdb`, `numactl`, `ninja` | minor; work around | — |

`valgrind` and `clang` were the other two gaps. Both closed in TASK_001; they are
in the installed table above. Hardware counters remain the only hard gap.

## Hard constraints (non-negotiable)

1. **No `/tmp`.** All scratch goes under the repo's `.temp/`, one subdir per
   category (`.temp/verus/`, `.temp/build/`, ...). `rm` is only auto-permitted there.
2. **No blind process killing.** Never `pkill`/`killall`/substring match. Resolve an
   exact PID, confirm its full command line, kill that PID. Prefer `timeout <N> <cmd>`.
3. **No GitHub/CI infrastructure.** No `.github/`, no CI config, no badges.
4. **Subagents never run `git commit`/`git add`** or any history-mutating git command.
   Read-only git is fine. The manager commits at task boundaries.
5. **No root, no system package installs.** `~/tools/` only.
