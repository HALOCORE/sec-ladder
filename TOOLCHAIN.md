# Toolchain

Install record for this box, and how to reproduce it. Installed 2026-08-15.

## What's installed

| Tool | Version | Location |
|---|---|---|
| Verus | `0.2026.08.09.92f466f` | `~/tools/verus` → `~/tools/verus-0.2026.08.09.92f466f` |
| rustc/cargo | 1.97.1 (`stable`, and the pinned `1.97.1-x86_64-unknown-linux-gnu`) | `~/.cargo/bin` (rustup) |
| **rustc nightly + Miri** | `1.99.0-nightly (d453bdd8f 2026-08-14)` / miri `0.1.0`. **Never used for a measured build** — see "Miri, and why it lives on a second toolchain" | `~/.rustup/toolchains/nightly-x86_64-unknown-linux-gnu` |
| z3 | bundled with Verus | `~/tools/verus/z3` |
| gcc | 13.3.0 | `/usr/bin/gcc` |
| **clang / LLVM** | **22.1.6** (matches rustc 1.97.1's LLVM exactly) | `~/tools/llvm` → `~/tools/llvm-22.1.6` |
| **valgrind** | **3.27.1** (built from source) | `~/tools/valgrind` → `~/tools/valgrind-3.27.1` |
| binutils | objdump / readelf / nm | `/usr/bin` |

`~/.cargo/bin` is on PATH via `~/.bashrc`/`~/.profile`. Verus, clang and valgrind
are **not** on PATH by design — call them by absolute path
(`~/tools/llvm/bin/clang`, `~/tools/valgrind/bin/valgrind`) so nothing depends on
shell setup. `verus_run.py` locates Verus itself.

### clang and rustc share a backend — exactly

`rustc 1.97.1 --version --verbose` reports `LLVM version: 22.1.6`, and the
installed clang is `clang version 22.1.6`. **Same major, minor and patch.** So a
clang-vs-rustc comparison is genuinely same-backend and any remaining difference
is language/ABI, not codegen vintage. If either side is ever bumped, re-check
this and re-state the caveat — a multi-major gap would weaken every
same-backend claim in `results/`.

`~/tools/llvm-22.1.6` is **12 GB on disk** (the upstream `LLVM-*-Linux-X64`
tarball is the full distribution — static libs, lldb, flang, all of it). LLVM no
longer publishes the slim `clang+llvm-*-x86_64-linux-gnu-ubuntu-*` tarball that
older instructions reference; `LLVM-<ver>-Linux-X64.tar.xz` is the replacement.

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

## Reproducing the clang install

No root, no package manager. Pick the release whose version equals rustc's
`LLVM version:` field.

```bash
ver=22.1.6                                  # == rustc 1.97.1's LLVM version
cd .temp/build
curl -L -o "LLVM-$ver-Linux-X64.tar.xz" \
  "https://github.com/llvm/llvm-project/releases/download/llvmorg-$ver/LLVM-$ver-Linux-X64.tar.xz"
tar -xf "LLVM-$ver-Linux-X64.tar.xz" -C ~/tools
mv ~/tools/"LLVM-$ver-Linux-X64" ~/tools/llvm-$ver
ln -sfn llvm-$ver ~/tools/llvm
~/tools/llvm/bin/clang --version
```

Download is ~1.9 GB, unpacks to ~12 GB, and `tar -xf` of the xz takes several
minutes (single-threaded decompression). `sha256(LLVM-22.1.6-Linux-X64.tar.xz)`
= `c5ac8ef89ca39d30cb32e9b83772f995dd891c685ebc188d593c943a64d5f8b5`.

## Reproducing the valgrind install

```bash
ver=3.27.1
cd .temp/build
curl -L -O "https://sourceware.org/pub/valgrind/valgrind-$ver.tar.bz2"
tar xf valgrind-$ver.tar.bz2 && cd valgrind-$ver
./configure --prefix=$HOME/tools/valgrind-$ver
make -j16 && make install
ln -sfn valgrind-$ver ~/tools/valgrind
~/tools/valgrind/bin/valgrind --version
```

Stock `./configure` is enough on this box (`supported CPU... ok (x86_64)`,
`supported CPU/OS combination... ok (amd64-linux)`); no root, no extra deps, and
`callgrind_annotate` only needs the system perl. ~211 MB installed, ~4 min build.
`sha256(valgrind-3.27.1.tar.bz2)` =
`5d589152eb8071c02feab8ce6ab719e431a1fbc3e2b1700f5432632a8b9264dc`.

Usage — see `.memory/03-measurement.md` for the protocol, especially why the
**per-function exclusive** `Ir` is the metric and the whole-program `summary:`
line is not:

```bash
mkdir -p .temp/build/cg          # callgrind will NOT create the output dir
~/tools/valgrind/bin/valgrind --tool=callgrind \
    --callgrind-out-file=.temp/build/cg/x.out ./bin/x <args>
~/tools/valgrind/bin/callgrind_annotate --threshold=100 .temp/build/cg/x.out \
  | grep kernel
```

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
- ghost erasure produces byte-identical machine code to plain rustc (see `pilot/`);
  re-confirmed at TASK_001 by md5 of the normalised kernel, not just by count
- `~/tools/llvm/bin/clang -O3 pilot/k.c -o k_clang && ./k_clang 10 20 30 40` → `100`
- `valgrind --tool=callgrind` gives a repeat-identical `Ir` for all six pilot cells

## Miri, and why it lives on a second toolchain

Installed at TASK_005. `.memory/02-bench-rules.md` makes Miri **mandatory for any
pattern whose R4 and R5 are not the same machine code**, and until TASK_005 that
made the first such pattern un-greenable: `rustup component add miri` is not
available for `stable-x86_64-unknown-linux-gnu` (nor for the pinned `1.97.1`),
so the policy demanded a tool the box did not have.

```bash
rustup toolchain install nightly --component miri --profile minimal
cargo +nightly miri setup          # builds the interpreter sysroot, ~20 s, cached
```

| | |
|---|---|
| toolchain | `nightly-x86_64-unknown-linux-gnu`, rustc `1.99.0-nightly (d453bdd8f 2026-08-14)` |
| miri | `0.1.0 (d453bdd8f0 2026-08-14)` |
| binary | `~/.rustup/toolchains/nightly-x86_64-unknown-linux-gnu/bin/miri` |
| sysroot | `~/.cache/miri` (from `cargo +nightly miri setup --print-sysroot`) |

**The toolchain difference is not a confound, and this is the whole argument for
doing it this way.** Miri interprets *source* for undefined behaviour; it does
not measure codegen, and no number in `results/` comes from it. The measured
builds still use the pinned `1.97.1` + Verus's own toolchain, exactly as before.
What Miri checks is R4 — plain unsafe Rust with **no vstd dependency** — so
nightly can compile and interpret it without Verus being involved at all. The
alternative on the table was weakening the Miri policy, which would have been
trading a real check for a green light.

`harness/check.py` runs it directly on the rung source, no Cargo project:

```bash
SR=$(cargo +nightly miri setup --print-sysroot)
~/.rustup/toolchains/nightly-x86_64-unknown-linux-gnu/bin/miri \
    --sysroot "$SR" --edition 2021 -Zmiri-disable-isolation \
    patterns/p01-array-sum/unsafe.rs -- <input>.bin
```

`-Zmiri-disable-isolation` is required because every rung reads its input from a
file named in `argv` (`.memory/02-bench-rules.md` rule 1). The gate rewrites
`n_iters` to 4 first — Miri is ~1000× slower than native, and `small.bin`'s
200 000 iterations would never finish; 4 iterations of the real driver on the
real payload is enough to exercise every unsafe read at several distinct
offsets. It then checks the printed checksum against `model.py`'s prediction, so
a rung that is UB-free but *wrong* under interpretation still fails.

Confirmed load-bearing, not decorative — R4 with the index shifted by 1600:

```
error: Undefined Behavior: `assume` called with `false`
  --> unsafe.rs:19:42
19 |    acc = acc.wrapping_add(unsafe { *v.get_unchecked(off + i + 1600) });
   |                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ UB occurred here
```

Unmutated R4 on the same probe input prints `5680969448682675282`, which is what
`model.py` predicts.

**Limitation to keep in mind:** Miri checks the paths the probe inputs actually
take. It is a UB *test*, not a proof, and it says nothing about the four inputs
it was not run on. That is why the policy is "mandatory when R4 ≠ R5", not
"sufficient".

## Missing / constrained on this box

Relevant to benchmarking — see `PLAN.md` "Measurement methodology".

- **`perf` not installed, and `perf_event_paranoid=3`** → no hardware counters
  even if installed (needs root to relax). This is the only remaining hard gap:
  no IPC, no branch-miss, no cache-miss data.
- **`hyperfine`, `gdb`, `numactl`, `ninja`, `rsync` absent**; `taskset` is
  available for pinning.
- CPU: 2× Xeon Gold 6230 (80 threads), `powersave` governor, shared box → wall
  clock is noisy; pin and use min-of-N.

## Pilot reproduction

Binaries go to `.temp/build/pilot/bin/`; `pilot/` itself stays source-only.
Ladder flags (`.memory/01-ladder.md`), run from the repo root:

```bash
O=.temp/build/pilot/bin; mkdir -p $O
gcc                -std=c99 -Wall -Wextra -O3 pilot/k.c -o $O/k_gcc
~/tools/llvm/bin/clang -std=c99 -Wall -Wextra -O3 pilot/k.c -o $O/k_clang
rustc -C opt-level=3 -C debug-assertions=off -C codegen-units=1 pilot/k_rust.rs   -o $O/k_rust
rustc -C opt-level=3 -C debug-assertions=off -C codegen-units=1 pilot/k_unsafe.rs -o $O/k_unsafe
./verus_run.py --compile pilot/k_verus.rs        -o $O/k_verus \
    -C opt-level=3 -C debug-assertions=off -C codegen-units=1
./verus_run.py --compile pilot/k_unsafe_verus.rs -o $O/k_unsafe_verus \
    -C opt-level=3 -C debug-assertions=off -C codegen-units=1
```

Kernel body with addresses and symbol hashes normalised away — note this is
**not** the snippet that produced the 33/58/38 numbers in `pilot/README.md` and
`PLAN.md`; see `.memory/03-measurement.md` for what was wrong with that one
(it counts the `<addr> <sym>:` header line as an instruction, so every published
count is one too high, and it leaves bare-hex branch targets in so two builds
never diff clean):

```bash
objdump -d --no-show-raw-insn <bin> | awk '/kernel[^ ]*>:$/,/^$/' | grep -v '>:$' \
  | sed -E 's/^\s+[0-9a-f]+:\s+//; s/\s+#.*$//; s/<[^>]*>//g;
            s/0x[0-9a-f]+//g; s/\b[0-9a-f]{4,}\b//g; s/\s+$//' | grep -v '^$'
```

**Superseded at TASK_002. Use `harness/asm.py`, not this.** The snippet above
still has two defects of its own (`s/\b[0-9a-f]{4,}\b//g` eats the `fadd`
mnemonic; branch targets under four hex digits survive), and — more importantly —
its *output is text*, which cannot establish identity: two kernels with different
answers can normalise to the same md5. `harness/asm.py` owns the one pipeline and
exposes the machine-code-byte digest that can.

```bash
python3 harness/asm.py stat <bin> [--sym kernel]   # counts + every digest
python3 harness/asm.py show <bin> [--raw]          # normalised / objdump text
python3 harness/asm.py diff <bin-a> <bin-b>        # verdict + readable diff
python3 harness/fixture.py --check                 # build the pilot fixture,
                                                   #   then re-derive its numbers
python3 harness/asm.py selftest                    # re-derives the pilot numbers
python3 harness/vparse.py selftest                 # attribute/clause parser
python3 harness/vparse.py <file.rs>                # items, attrs, clauses
python3 harness/dloop.py <file.rs|main.c> [alias-json]   # driver loop, canonical
```

`fixture.py` is what makes `selftest` meaningful on a fresh checkout — it builds
`.temp/build/docrepro/` from `pilot/` with the flags above. Verified at TASK_003:
a clean rebuild reproduces all six kernels bit-exactly under **both** digest
conventions (`md5_raw`, objdump grouping; `md5_fn`, the `nm --print-size`
extent). `harness/check.py` builds it automatically and fails if it cannot.

## The `.temp/` citation check

`CLAUDE.md` rule 1 puts every agent's evidence under gitignored `.temp/`, and
`.memory/00-environment.md` constraint 6 then deletes the re-derivable half of
it. Both are deliberate. The gap they leave is that a committed file can name a
`.temp/` path and **nothing notices when that path goes away** — the loss needs
an `rm`, not a clone.

```bash
python3 harness/tools/temp_citations.py            # exit 1 on a NEW dangling citation
python3 harness/tools/temp_citations.py --list     # the classified baseline, with its notes
python3 harness/tools/temp_citations.py --census   # what a strict "promote" rule would cost
python3 harness/tools/temp_citations.py --update   # re-skeleton the baseline after a fix
```

Run it before a commit that adds or moves prose. ⚠ **It is a THIS-BOX check**:
`.temp/` is gitignored, so in a fresh clone every citation dangles and the output
means nothing. And it is blind to the failure that motivated it — a probe source
that is still on disk but has been *edited* since the number was taken resolves
fine (TASK_122's `Ir` drift). Existence is the cheap half; the expensive half
needs a content pin, which is what promoting a file into the tree buys for free.

⚠ **It lives in `harness/tools/`, not `harness/`, on purpose.** `check.py`'s gate
digest globs `harness/*.py` — non-recursively — into every pattern's
`source_sha256`, so a file in `harness/` costs a **26-pattern gate sweep** every
time it is edited, and this tool decides no pattern's verdict. Nothing under
`harness/tools/` may be imported by `check.py`, `measure.py` or `build.py`; if it
were, the digest would silently stop covering a file that does decide one.

The policy (TASK_121 §B, implemented at TASK_125): **promote, don't publish** —
if a reader is meant to be able to check a `.temp/` artefact, promote it into the
tree (`patterns/pNN/controls/` for a pattern probe, `common/` for cross-pattern
data); otherwise make the citation say what rebuilds it. `.tasks/*_REPORT.md` is
exempt, because a report is a dated record of what was true when it was written.

## Verus conventions

- Files start with `use vstd::prelude::*;` and wrap verified code in `verus! { ... }`.
- After any non-trivial proof edit, re-run Verus and report the obligation count.
- Unverifiable exec code (`println!`, `get_unchecked`) goes in a
  `#[verifier::external_body]` helper with an explicit `requires` — Verus has no
  statement-level skip. Every such helper is trusted base: keep it minimal and
  justify it in a comment. `PLAN.md` counts these lines as a reported metric.
- Run Verus from a scratch dir (`verus_run.py` does this) so `.vir`/build
  artefacts stay out of the tree.
