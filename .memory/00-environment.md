# Environment — the box, the toolchain, the constraints

Facts about the machine every agent works on. Verify before contradicting; update
this file (and say so in your report) if a fact goes stale.

## Machine

- 2× Intel Xeon Gold 6230 @ 2.10 GHz, 20 cores/socket, 2 threads/core = **80 logical CPUs**.
- Governor `powersave`, frequency scaling active (observed ~24% of max at idle).
- **Shared box, containerised** (`/dev/vg1/containers_apt`). Wall-clock timing is noisy.
- ~134 GB free on `/`.
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
| binutils | objdump, readelf, nm | `/usr/bin` |
| cmake | present | `/usr/bin/cmake` |
| taskset | present (use for pinning) | `/usr/bin/taskset` |
| python3 | present | `/usr/bin/python3` |

Verus is deliberately **not on PATH**. Use `./verus_run.py`, which locates it and
sets up the pinned rustc. See `TOOLCHAIN.md`.

## Missing, and why it matters

| Missing | Consequence | Fix |
|---|---|---|
| `perf` | — | needs root to install |
| `perf_event_paranoid=3` | **no hardware counters at all** (IPC, branch miss, cache miss) even if perf were installed | needs root to relax to ≤1 |
| `valgrind` | no deterministic executed-instruction count | builds from source into `~/tools`, no root — TASK_001 |
| `clang` | only C baseline is gcc, so C-vs-Rust confounds *safety cost* with *gcc-vs-LLVM codegen* | LLVM release tarball into `~/tools`, no root — TASK_001 |
| `hyperfine`, `gdb`, `numactl`, `ninja` | minor; work around | — |

## Hard constraints (non-negotiable)

1. **No `/tmp`.** All scratch goes under the repo's `.temp/`, one subdir per
   category (`.temp/verus/`, `.temp/build/`, ...). `rm` is only auto-permitted there.
2. **No blind process killing.** Never `pkill`/`killall`/substring match. Resolve an
   exact PID, confirm its full command line, kill that PID. Prefer `timeout <N> <cmd>`.
3. **No GitHub/CI infrastructure.** No `.github/`, no CI config, no badges.
4. **Subagents never run `git commit`/`git add`** or any history-mutating git command.
   Read-only git is fine. The manager commits at task boundaries.
5. **No root, no system package installs.** `~/tools/` only.
