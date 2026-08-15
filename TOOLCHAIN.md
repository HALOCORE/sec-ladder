# Toolchain

Install record for this box, and how to reproduce it. Installed 2026-08-15.

## What's installed

| Tool | Version | Location |
|---|---|---|
| Verus | `0.2026.08.09.92f466f` | `~/tools/verus` → `~/tools/verus-0.2026.08.09.92f466f` |
| rustc/cargo | 1.97.1 (`stable`, and the pinned `1.97.1-x86_64-unknown-linux-gnu`) | `~/.cargo/bin` (rustup) |
| z3 | bundled with Verus | `~/tools/verus/z3` |
| gcc | 13.3.0 | `/usr/bin/gcc` |
| binutils | objdump / readelf / nm | `/usr/bin` |

`~/.cargo/bin` is on PATH via `~/.bashrc`/`~/.profile`. Verus is **not** on PATH
by design — `verus_run.py` locates it, so nothing depends on shell setup.

## Reproducing the Verus install

Verus prebuilt releases bundle `verus`, `rust_verify`, `cargo-verus`, `z3` and
`vstd`, but **not** rustc — they demand the exact toolchain named in the
release's `version.json`, installed under its full version name (`stable` being
the same version is not enough; the wrapper looks up the literal name).

```bash
ver=0.2026.08.09.92f466f
curl -L -o verus.zip \
  "https://github.com/verus-lang/verus/releases/download/release%2F$ver/verus-$ver-x86-linux.zip"
unzip -q verus.zip -d ~/tools && mv ~/tools/verus-x86-linux ~/tools/verus-$ver
ln -sfn verus-$ver ~/tools/verus
chmod +x ~/tools/verus/{verus,rust_verify,z3,cargo-verus}
rustup toolchain install 1.97.1-x86_64-unknown-linux-gnu   # from version.json
```

### Picking a release

For whole-crate `cargo verus` the driver's **vstd must exist on crates.io** —
cargo-verus always fetches vstd from there and recompiles it through the driver;
a mismatch is a version-skew panic (LearnVeri's `PITFALLS.md` has the details and
the error signatures). Check before upgrading:

```bash
curl -s https://crates.io/api/v1/crates/vstd | python3 -c \
  "import json,sys; [print(v['num']) for v in json.load(sys.stdin)['versions'][:5]]"
```

`0.2026.08.09.92f466f` ↔ `vstd = "=0.0.0-2026-08-09-0044"` — verified working
here. Avoid the `release/rolling/*` tags. Crate setup for `cargo verus`
(that vstd pin, `[package.metadata.verus] verify = true`, an
`unexpected_cfgs` allow-list, and an empty `[workspace]`) is in `PITFALLS.md`.

## Running Verus

Use `./verus_run.py` — it finds the Verus install, puts rustup on PATH so Verus
can resolve its pinned rustc, and runs in a scratch dir under `.temp/` so build
artefacts stay out of the tree.

```bash
./verus_run.py --info                       # resolved paths + versions
./verus_run.py file.rs                      # verify
./verus_run.py file.rs --crate-type=lib     # verify a lib
./verus_run.py --compile file.rs -o out -C opt-level=3   # verify + compile
./verus_run.py --keep --compile file.rs     # keep scratch dir to inspect artefacts
./verus_run.py --cargo build                # whole crate, run from the crate dir
```

A clean run prints `verification results:: N verified, 0 errors`.

## Verified working

- single-file verify, and `--compile` → runnable binary
- `cargo verus build`: vstd (2044 obligations) + local lib verified, plain-Rust
  bin passed through, then compiled
- ghost erasure produces byte-identical machine code to plain rustc (see `pilot/`)

## Missing / constrained on this box

Relevant to benchmarking — see `PLAN.md` "Measurement methodology".

- **`perf` not installed, and `perf_event_paranoid=3`** → no hardware counters
  even if installed (needs root to relax).
- **`valgrind` not installed** → no callgrind instruction counts yet. Builds from
  source without root.
- **`clang` not installed** → the only C baseline is gcc, so C-vs-Rust
  comparisons currently confound *safety cost* with *gcc-vs-LLVM codegen*.
- **`hyperfine`, `gdb`, `numactl` absent**; `taskset` is available for pinning.
- CPU: 2× Xeon Gold 6230 (80 threads), `powersave` governor, shared box → wall
  clock is noisy; pin and use min-of-N.

## Pilot reproduction

```bash
cd pilot
../verus_run.py --compile k_verus.rs        -o /tmp_out/k_verus        -C opt-level=3
../verus_run.py --compile k_unsafe_verus.rs -o /tmp_out/k_unsafe_verus -C opt-level=3
rustc -C opt-level=3 k_rust.rs   -o k_rust
rustc -C opt-level=3 k_unsafe.rs -o k_unsafe
gcc   -O3            k.c         -o k_c
# kernel body, addresses and symbol hashes normalised away:
objdump -d --no-show-raw-insn <bin> | awk '/kernel>:/,/^$/' \
  | sed -E 's/^\s+[0-9a-f]+:\s+//; s/0x[0-9a-f]+//g; s/<[^>]*>//g' | grep -v '^$'
```

## Verus conventions

- Files start with `use vstd::prelude::*;` and wrap verified code in `verus! { ... }`.
- After any non-trivial proof edit, re-run Verus and report the obligation count.
- Unverifiable exec code (`println!`, `get_unchecked`) goes in a
  `#[verifier::external_body]` helper with an explicit `requires` — Verus has no
  statement-level skip. Every such helper is trusted base: keep it minimal and
  justify it in a comment. `PLAN.md` counts these lines as a reported metric.
- Run Verus from a scratch dir (`verus_run.py` does this) so `.vir`/build
  artefacts stay out of the tree.
