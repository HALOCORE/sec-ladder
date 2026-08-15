# Pattern catalogue — master tracker

The C patterns the benchmark aims to cover. **This file is the single source of
truth for what exists and what state it is in.** The manager updates `Status`
after each task closes; agents read it to know what is already done.

Status values: `planned` · `wip` · `done` · `partial` (some rungs missing, documented)
· `blocked` (with a note). R5 column records the Verus outcome specifically, since
"R5 defeated" is itself a result worth publishing.

## Wave 0 — infrastructure

| ID | Item | Status |
|---|---|---|
| T001 | clang 22.1.6 + valgrind 3.27.1 into `~/tools`; pilot re-measured | **done**, reviewed |
| T002 | `harness/` + `common/` + p01 as the template | **done**, reviewed |
| T003 | harden the gate against the six demonstrated bypasses | **done**, reviewed |
| T005 | derive the pins; unblock p02; the barrier swap | **done**, unreviewed |
| T004 | p02 buffer copy — first real bug, first adversarial table | draft spec, **unblocked by T005** |

Each task has been reviewed adversarially and each review found real defects. The
cumulative lesson, worth reading before adding a pattern: **a green gate is
evidence about the gate, not about the work.** T001's review found the identity
oracle could not detect difference (a collision was constructed) and that the
pilot's proof had no verified call site. T002's review got six defects past a
28/28 PASS, including the pilot's exact fatal defect. T003 fixed those and its own
engineer then found a seventh defect in its own delivery after reporting.

Findings are folded into `.memory/01`–`05`; those files supersede the pilot and
supersede any earlier task report they contradict.

## Open cross-cutting issues

- ~~**Miri is not installable**~~ — **closed at T005.** `nightly` +
  `cargo miri setup` alongside the pinned toolchain; R4 has no vstd dependency,
  and Miri checks source for UB rather than measuring codegen, so the toolchain
  difference is not a confound. `TOOLCHAIN.md` has the arrangement. The gate now
  runs it. Residual: a *big payload* is unchecked, because `n_iters` can be
  clamped from the file header and the payload cannot — p01's `large.bin` times
  out and is recorded as a blocked row.
- ~~**The barrier swap to multiply-shift is deferred**~~ — **closed at T005.**
  Swapped to `(acc * nwin) >> 64` in 128-bit arithmetic, p01 re-measured. Cost:
  three lines of ghost proof in R5 (`lemma_u128_shr_is_div` plus two
  `nonlinear_arith` steps) and the obligation count 5 → 7. R4's `-O3` driver loop
  went 18 → 13 instructions, because the high half of `mul` lands in `%rdx`,
  which is already the kernel's third argument register.
- **A width change applied to every rung at once is invisible to the driver
  diff.** `harness/dloop.py` must erase casts for the C/Rust reconciliation to
  work at all. Not fixed; recorded in `.memory/02-bench-rules.md`.
- **`results/gate/<pattern>.json` is the last complete run, pass or fail**, so a
  red run replaces a green record. Mitigated at T005 by hashing the contract
  block and every source into it, so a stale record is detectable. Whether the
  directory should be tracked at all is still open.
- **18 of 28 wall-clock cells exceed the 10% spread threshold** and are marked
  discarded. No claim rests on them. Fixing needs a quieter box.
- **`perf_event_paranoid = 3`** — no hardware counters without root. This is the
  only way to explain *why* gcc's shorter loop runs 43% slower.

## Family A — buffers & bounds (spatial safety core)

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p01 | array reduce / prefix scan | none (calibration) | trivial | **done** (T002/T003/T005), gate green, R5 == R4 byte-identical at O3 |
| p02 | length-prefixed buffer copy (`memcpy` w/ attacker length) | spatial OOB write | easy | planned |
| p03 | bounded queue / stack, array-backed | index underflow on empty pop | easy | planned |
| p04 | ring buffer with wraparound | modular index, aliasing | moderate | planned |
| p05 | 2-D index flattening / matmul (`i*n+j`) | overflow in index arithmetic | moderate | planned |
| p06 | in-place reverse / rotate / swap | aliasing, permutation invariant | moderate | planned |
| p07 | binary search | midpoint overflow (`(lo+hi)/2`) | moderate | planned |
| p08 | memmove with overlapping regions | overlap UB | moderate | planned |
| p09 | bit vector / bitset ops (set, test, popcount) | word-index vs bit-index confusion | easy–moderate | planned |
| p10 | sliding-window / stencil over array | off-by-one at boundaries | moderate | planned |

## Family B — strings & NUL-termination

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p11 | `strlen`/`strcpy` over NUL-terminated buffer | missing terminator → OOB read | moderate | planned |
| p12 | `strcat` into fixed stack buffer | classic stack overflow | moderate | planned |
| p13 | `strncpy`/`snprintf` truncation semantics | silent truncation, missing NUL | moderate | planned |
| p14 | tokenizer (`strtok`-style, in-place mutation) | in-place mutation + aliasing | hard | planned |
| p15 | UTF-8 validation + decode | malformed continuation bytes | moderate–hard | planned |

## Family C — parsing & protocol decoding

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p16 | TLV / length-prefixed record walker | length field vs remaining buffer | easy–moderate | planned |
| p17 | HTTP `Range:` style header parser | int overflow → OOB (cf. CVE-2017-7529) | moderate | planned |
| p18 | varint / LEB128 decoder | unbounded shift, truncation | easy–moderate | planned |
| p19 | protocol state machine (byte-at-a-time) | state confusion | moderate | planned |
| p20 | length/offset pair validation (heartbeat-style) | trusted length field (cf. CVE-2014-0160) | moderate | planned |
| p21 | CSV/field splitter with escapes | quote-state off-by-one | moderate | planned |

## Family D — data structures, array-backed

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p22 | open-addressing hash table (linear probe) | capacity mask, probe termination | moderate–hard | planned |
| p23 | in-place quicksort partition | aliasing, permutation invariant | hard | planned |
| p24 | binary heap (sift up/down) | parent/child index arithmetic | moderate–hard | planned |
| p25 | dynamic array with `realloc` growth | growth overflow, stale pointer | moderate–hard | planned |
| p26 | run-length encode/decode | expansion overflow on decode | moderate | planned |

## Family E — data structures, pointer-backed (Verus stress tests)

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p27 | singly linked list (build, traverse, free) | use-after-free, leak | hard (`vstd::raw_ptr`) | planned |
| p28 | intrusive doubly linked list | aliasing, ownership | research-grade | planned |
| p29 | binary search tree insert/lookup | recursive ownership | hard | planned |
| p30 | chained hash table (buckets of lists) | combines p22 + p27 | research-grade | planned |

Expect p28/p30 to defeat R5 within budget. **Document where the proof got stuck —
that is the deliverable for these rows**, not a green checkmark.

## Family F — memory management

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p31 | bump / arena allocator | alignment, exhaustion, provenance | hard | planned |
| p32 | free-list allocator | double free, corruption | research-grade | planned |
| p33 | object pool with recycling | use-after-recycle | hard | planned |
| p34 | reference counting | leak, premature free | hard | planned |

## Family G — systems idioms & representation

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p35 | tagged union / discriminated dispatch | tag-payload mismatch | moderate | planned |
| p36 | function-pointer table dispatch (vtable-like) | index out of table | moderate | planned |
| p37 | callback with `void*` userdata | type confusion | moderate–hard | planned |
| p38 | endian conversion / type punning (`memcpy` vs union) | strict-aliasing UB | moderate | planned |
| p39 | bitfield pack/unpack into wire format | shift/mask off-by-one | moderate | planned |
| p40 | struct-of-arrays vs array-of-structs traversal | none — pure perf axis | easy | planned |
| p41 | flexible array member struct | size computation overflow | moderate–hard | planned |
| p42 | `goto cleanup` error handling | leak on error path | moderate | planned |

## Family H — numeric & crypto-adjacent

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p43 | checksum / CRC over untrusted length | loop bound from input | easy | planned |
| p44 | fixed-point arithmetic | overflow, rounding | moderate | planned |
| p45 | saturating / wrapping arithmetic helpers | signed overflow UB | easy–moderate | planned |
| p46 | bignum limb add/mul (schoolbook) | carry propagation, limb bounds | hard | planned |
| p47 | constant-time compare / select | **timing side channel** — compiler may reintroduce a branch | moderate | planned |

p47 is special: the "security" axis is timing, not memory safety, and the threat is
the *optimiser*. Worth doing precisely because it inverts the usual story.

## Sequencing

Depth-first, template-first. Do not start a wave until the previous one's patterns
are green in `harness/check.py`.

- **Wave 1** (template + core): p01, p02, p16, p17 — establishes the pattern
  template, the adversarial-input protocol, and one real-CVE mirror.
- **Wave 2** (bounds breadth): p03–p10.
- **Wave 3** (strings + parsing): p11–p15, p18–p21.
- **Wave 4** (array structures): p22–p26, p43–p45.
- **Wave 5** (representation/idioms): p35–p42.
- **Wave 6** (pointers, the hard wall): p27–p34, p46, p47.
- **Wave 7**: cross-pattern analysis and writeup.
