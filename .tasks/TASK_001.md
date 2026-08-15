# TASK_001 — measurement tooling: clang + valgrind

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, `.memory/00-environment.md`, `.memory/03-measurement.md`

## Why

Two gaps make the benchmark's headline numbers unusable as-is:

1. **No deterministic dynamic metric.** Wall clock on this shared, frequency-scaling
   80-thread box is mush, and hardware counters are unavailable (`perf` absent,
   `perf_event_paranoid=3`, no root). Callgrind's executed-instruction count (`Ir`)
   is the only noise-free dynamic measurement available to us.
2. **Only one C compiler.** gcc-vs-LLVM codegen differences are currently
   indistinguishable from the cost of Rust's safety. The pilot's C-33 vs
   unsafe-Rust-38 gap is very likely backend, not language — a clang column would
   settle it.

## Deliverables

### 1. Valgrind in `~/tools`

Build the latest stable valgrind from source (sourceware.org) with
`--prefix=$HOME/tools/valgrind-<ver>`, symlink `~/tools/valgrind` → it. No root,
no system install. Build in `.temp/build/valgrind/`.

Verify:
- `~/tools/valgrind/bin/valgrind --version` runs.
- `--tool=callgrind` produces an `Ir` count on a pilot binary.
- **Determinism check:** run the same binary+input twice, confirm identical `Ir`.
  If not identical, investigate and report — a non-deterministic Ir count would
  undermine the whole measurement plan.

### 2. Clang in `~/tools`

Install a prebuilt LLVM/clang release tarball (github.com/llvm/llvm-project
releases, `x86_64-linux-gnu-ubuntu-*` build; host is Ubuntu 24.04) into
`~/tools/llvm-<ver>`, symlink `~/tools/llvm`. Prefer a version whose LLVM major
is close to rustc 1.97.1's LLVM, and **report both LLVM versions** — if they are
far apart, say so, it weakens the same-backend argument.

Verify `clang --version`, and that it compiles `pilot/k.c` at `-O3` and produces
the correct answer (`./k_c 10 20 30 40` → `100`).

### 3. First real data: the pilot measured properly

Build all five pilot rungs at `-O3`/`opt-level=3` per `.memory/01-ladder.md`
(build into `.temp/build/pilot/`, **do not** put binaries in `pilot/`), plus a
sixth: **clang -O3**. Then report a table:

| cell | kernel instrs (static) | callgrind Ir | notes |

Use a large-ish input so `Ir` is dominated by the kernel, and use the **same**
input for every cell. Pilot drivers take numbers on argv — you may need a few
thousand args, or (cleaner) note the limitation and report what you can. Do not
modify `pilot/` sources; copy to `.temp/` if you need to adapt them, and say so.

The specific question to answer: **is the gcc-33 vs unsafe-Rust-38 gap a backend
artefact?** If clang -O3 also emits ~38, that settles it and it goes in the
findings. If clang emits ~33, the gap is real and needs explaining.

### 4. Doc updates

- `TOOLCHAIN.md`: add both tools to the installed table, exact reproduction
  commands, and move them out of the "Missing" table.
- `.memory/00-environment.md`: same, keep the table accurate.
- Record the LLVM-version-vs-rustc-LLVM-version caveat wherever it belongs.

## Constraints

- No root. No system packages. `~/tools/` only.
- Scratch in `.temp/build/`, never `/tmp`.
- `timeout` on long builds (valgrind's build is ~5–15 min; give it 1800s and run
  it in the background if useful).
- **No `git add` / `git commit`.** The manager commits.
- Do not edit `pilot/` sources.

## Done when

Both tools run, the determinism check passed (or its failure is explained), the
six-cell table exists with real numbers, the backend question has an answer, and
the docs are accurate.
