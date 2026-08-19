# TASK_033 — p11, NUL-terminated scan: the first kernel whose loop bound is not known at all

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**
(the distilled rules from seventeen tasks of methodology — they are the whole
reason p11 should not need correcting afterwards), then `.memory/01-ladder.md`
(findings 3–5 and 8, and the "R4 is defined by permission" paragraph),
`.memory/02-bench-rules.md`, `.memory/03-measurement.md`, `.memory/04-verus.md`,
`.memory/05-layout.md` ("Adding a pattern" **and** "Adding a sweep band costs a
gate re-run, not a re-measure"), then **`patterns/p07-binary-search/` in full** —
p07 is the template you clone, being the only pattern built natively to the
current standard. Where this spec is silent, **do what p07 did.**

## Why this pattern

**1. Family B is empty.** Seven patterns exist and all seven are in Family A
(buffers) or Family C (parsing). **NUL-termination is the most notorious bug
family in C** and this project has not touched it. Coverage argument alone would
justify it.

**2. It is the first kernel whose loop bound is not known before the loop.**
p16's bound is data-dependent but *read from a header*; p07's is `⌈log2 n⌉`;
everything else is a length. **A NUL scan has no bound at all** — the loop runs
until it finds a sentinel that may not be there. That is a structurally new shape
and it is where the safety story should be most interesting: safe Rust cannot
express "scan until NUL" without *either* a per-byte bounds check *or* an idiom
(`iter().position()`, `memchr`) that carries the bound implicitly.

**3. It is the first pattern where C's rung calls a hand-written SIMD libc
routine and Rust has to match it.** glibc's `strlen` is AVX2. p02 had `memcpy`,
but as a bulk *copy*; this is a bulk *search*, and the R1-vs-R3 comparison is the
one a systems reader will care about most. **Expect the C rung to win and report
it honestly if it does** — a large, mechanism-attributed C win is a result this
project does not yet have, and `.memory/01-ladder.md` records that "C beats Rust"
was retracted once for being a gcc-only artefact. Do not repeat that: **the clang
column decides**, gcc is the distro baseline.

## The bug class

**CWE-125 via a missing sentinel.** A record is *declared* to contain a
NUL-terminated string; the scan trusts the sentinel and not the buffer. If the
terminator is absent, the scan runs past the record, past the window, and out of
the allocation. This is a different shape from every existing pattern: p16 walks
one step past a *length*, p17 computes a wrong-but-in-bounds *index*, p07
underflows an *inclusive bound*. **Here nothing is computed wrongly at all — the
loop simply does not stop.**

## Kernel contract

| Rung | Signature |
|---|---|
| R1, R1h | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

### Window layout and semantics

```
byte 0..4    nstr   u32 LE     -- number of strings in this window
data_start = 4 ;  avail = len - 4
strings follow, each NUL-terminated, packed
```

```
if len < 4:                     return 0
nstr from the header
if nstr == 0:                   return 0

acc = 0
p = data_start
for s in 0 .. nstr:
    # >>> THE SCAN. R1 omits exactly the bound, and nothing else. <<<
    q = p
    while buf[off + q] != 0:        # R1: unbounded
        q += 1                      # R2..R5: q < len must hold
    slen = q - p
    h = 0
    for i in p .. q:
        h = h *64 31 +64 buf[off + i]
    acc = acc *64 31 +64 (h ^64 slen)
    p = q + 1
    if p >= len: break
return acc *64 31 +64 nstr
```

Load-bearing, do not "improve":

- **The scan and the fold are separate loops on purpose.** Fusing them
  (`while b != 0 { h = h*31 + b }`) deletes the pattern: it makes the length
  never materialise and forecloses the `memchr`/`strlen` idiom that R1 and an
  idiomatic R3 both want. Keep them separate in **every** rung and pin it in
  `idiom.required`.
- **`slen` is folded into the result**, so a rung that finds a different
  terminator cannot produce the same checksum.
- **R1's C rung uses `strlen`** — that is the point of the pattern, and it is
  what makes the R1-vs-R3 comparison a libc-vs-Rust comparison. R1h adds the
  bound (`strnlen` or an explicit `memchr` over the remaining window; say which
  and why).
- Wrapping arithmetic throughout.

### Contract

```
requires:  off + len <= buf_len
ensures:   result == nul_scan_fold(buf, off, len)
```

## What to measure that no prior pattern could

1. **The idiom axis, which is this pattern's whole R3 question.** At least:
   indexed `while buf[q] != 0`, `iter().position(|&b| b == 0)`, and
   `CStr::from_bytes_until_nul` if it is admissible. **These are different
   spellings and TASK_026 §0 applies in full**: name the spelling beside every
   rate, difference rates only at matched spelling, and derive any five-decimal
   figure from the disassembly rather than a marginal.
2. **Does any Rust rung reach a SIMD scan?** Report `vector_regs` per rung,
   kernel-only, and say explicitly whether the R1 build calls
   `__strlen_avx2`/`strlen@plt` and what each Rust rung emits instead. If R1 is
   4–16× faster per byte, **that is the finding** — decompose it (SIMD width vs
   the check) rather than reporting a ratio.
3. **The safety cost per byte, and whether it amortises.** p07 showed the answer
   depends on loop shape. Here the scan is `O(total bytes)` with a per-byte
   sentinel test; predict before measuring and say whether you were right.
4. **`ns` needs the layout treatment.** Use `common/layout/order.py` for the
   identical-copy noise floor **before** believing any wall-clock number, and
   `common/layout/layout_gen.py` + `loopfit.py` if a mode shows. This is
   non-optional now: two patterns' `ns` rows have been withdrawn for exactly this.

## Inputs

| stem | shape | purpose |
|---|---|---|
| `small` | L1-resident, many short strings | perf row |
| `large` | past L2, **different mean length** from `small` | perf row |
| `sweep-len*` | mean string length band — the axis the laws are swept on, named `sweep-*` | the swept laws |
| `adversarial-nonul` | **one window**, last string missing its terminator | **the bug**: the scan runs out of the allocation; ASan must fire on R1 |
| `adversarial-empty` | strings of length 0 (immediate NUL) | the degenerate scan; every rung agrees |
| `adversarial-count` | `nstr` far exceeding the strings actually present | the scan walks past the window |

Adversarial rows are **exactly one window** (`n_blob == stride`) — with several
windows the malformed one is hit probabilistically and an overrun from a middle
window stays inside the allocation. **Window 0 must serve something**, or `acc`
pins at 0 and the driver's Lemire index has an absorbing state.

Name the sweep band `sweep-*` and nothing else — that prefix is the entire
mechanism (`check.py:459-460`, `measure.py:60`), and appended last it costs a gate
re-run and not a re-measure (`.memory/05-layout.md`).

## Done when

The p07 checklist, unchanged, plus §"What to measure" 1–4. In particular: a
complete green `check.py p11`; checksums against an independent `model.py`; the
adversarial table **per rung** with `adversarial-nonul` firing ASan on R1; the
`idiom` block written **before** the cells and its shared paragraph verified
byte-identical against p07's; a shipped sweep from day one; an in-contract
**R3-side span** with R4 held by fiat (**no pair interval** — both this project
has published were built from R4s that are not rungs); two proof mutants failing
the gate; the TCB tally; the `#[cfg(slb_twin)]` twin with its arithmetic written
out; and an `SLB-TRUSTED-ARGUMENT` block with labels (a)(b)(c).

**Run `./verus_run.py` on an R5 twin BEFORE differencing any unsafe-side
variant** — an R4 candidate vstd cannot express at the pinned version is not a
rung, and this has cost five published figures across two patterns. Read the error
text, not the exit code: `is not supported` disqualifies; *"postcondition not
satisfied"* disqualifies nothing.

**Budget: one session for R5.** A stalled proof reported with its exact Verus
error, the obligation it could not discharge, and what it tried **is** the
deliverable for that row. Expect the unbounded scan to be the work: the loop needs
a decreasing measure and an invariant that `q < len`, and the *natural* C spelling
has neither.

## Constraints

No root; no `/tmp` (scratch `.temp/p11/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/` (report durable facts; the manager lands them); do not
touch `harness/` or `common/` — **if p11 seems to need a change there, stop and
report it**. Do not edit any existing pattern's sources. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; confirm an exact PID's full command
line before any kill. **Measurements in the FOREGROUND, interleaved by cell**, and
delete your binaries and blobs once the gate is green.

Notes to `.temp/p11/NOTES.md` as you go so you can be resumed; five agents on this
project have died to transient API errors.

**If a prescription here is wrong, say so with the measurement.** Forty-two agents
have contradicted the manager and all forty-two were right — the last one showed
my premise about `source_sha256` was false by reading the code that writes it.
Two things I am least sure of:

- **whether the two-loop split survives the optimiser.** LLVM may fuse the scan
  and the fold back together, or hoist the sentinel test, and if it does in *every*
  rung then the pattern measures something other than what it is designed to.
  Check that first, on the disassembly, before building five rungs on it.
- **whether an idiomatic safe Rust scan reaches `memchr`.** If
  `iter().position()` lowers to a byte loop while C gets `__strlen_avx2`, the gap
  is a *library* difference and not a safety cost, and saying so clearly is more
  important than the number. This project retracted "C beats Rust" once for
  exactly this class of error.
