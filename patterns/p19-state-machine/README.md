# p19 — protocol state machine over a loaded transition table

A byte-at-a-time protocol decoder whose **transition table arrives in the
input**. Each window is `[2048-byte table][message]`; the decoder validates the
table once, then folds the message through it one indexed load per byte.

```c
for (p = 0; p < TBL; p++) if (w[p] >= NST) return REJ;   /* c/kernel.c omits this */
for (p = TBL; p < len; p++) { st = w[st * 256 + w[p]]; acc = acc * 31 + st; }
```

## The C bug

`c/kernel.c` has no validation pass: it trusts the table it was handed. An entry
naming a state that does not exist becomes the next row index, and
`w[st * 256 + b]` reads outside the blob.

That is **CVE-2026-23269**'s shape — the AppArmor fix titled *"`unpack_pdb` DFA
bounds validation hardening"* — and `c/kernel_hardened.c` is the same file with
the pass that closes it and nothing else changed.

## Why this is a memory-safety bug at all — the condition is named

A textbook "state confusion" bug is a **logic** bug with no out-of-bounds
access. p19 escapes that only because **both** of the following hold, and each
was settled by a run before any cell was built (`NOTES.md` 0a):

1. **the table is loaded data, not a program constant.** With a tool-generated
   table every entry is in range by construction — 0 out-of-range successors
   over all 2048 (state, byte) pairs, and 1e6 adversarial bytes never leave
   state 7. The out-of-bounds read is unreachable.
2. **the decoder dispatches by indexing, not by `switch`.** The identical bad
   entry written as `switch (st) { … default: }` is a wrong answer with **no
   memory event at all** — ASan and UBSan both silent.

Both are `forbidden` entries in `spec.md`'s hashed block: the only entries in
this tree that forbid a spelling for being *safe* rather than for being *fast*.

Both hold of real DFA decoders. The Linux kernel's AppArmor policy engine
(`security/apparmor/match.c`) indexes four tables with no test at all in
`aa_dfa_match()`, licensed by `verify_dfa()` having walked every entry once at
policy load — and CVE-2026-23407 is that validator getting one of the four
tables wrong.

⚠ **The bug class is this tree's THIRTEENTH `index >= len`**, and the row says
so rather than letting a reader discover it. Nearest sibling: **p36**.

## What is new

| | measured in |
|---|---|
| **the obligation is a loop-carried DATA invariant.** `st < NST` holds because 2048 bytes read at run time were checked once before the loop — not because of arithmetic on a loop counter | `NOTES.md` 6 |
| **a rung boundary inside the SAFE class, worth exactly one instruction per byte.** Safe Rust reaches within `1.00000 Ir/byte` of unsafe Rust by masking, and not to it. p47's shape — and *"the only other pattern with one"* is `.memory/06-catalogue.md`'s reading of its own probes, quoted here and not re-measured | `NOTES.md` 8a |
| **safe Rust's bounds check and the validation pass C omits are the SAME PREDICATE.** LLVM lowers `st * 256 + b < 2048` to `cmp $0x8` — a state-range check — enforced once per access instead of once per call | `NOTES.md` 8b |
| **the two hardening strategies have different asymptotics**: `O(table)` once per call versus `O(message)` per byte. Which is cheaper depends on the message length, not on the language | `NOTES.md` 9 |
| **one byte of one table entry decides what a checker can say.** Entry 8 reads the window's own message — defined, silent, wrong, ASan clean. Entry 10 is 5 bytes past the blob — ASan names the object *and* its allocation site. Entry 255 is 65 280 bytes past — ASan reports a bare `SEGV on unknown address` and *"can not provide additional info"*. Three shipped inputs, pairwise one byte apart, and `gen.py` asserts the distance | `NOTES.md` 0c |

## The rungs

| rung | the row expression | how it knows `st < NST` | Ir per message byte |
|---|---|---|---|
| R1 `c/kernel.c` | `w[st * 256 + w[p]]` | **it does not** | gcc 11.00 · clang 8.75 |
| R1h `c/kernel_hardened.c` | `w[st * 256 + w[p]]` | the validation pass | gcc 11.00 · clang 8.75 |
| R2 `safe_naive.rs` | `tbl[st * 256 + b as usize]` | the language checks it, per access | **15.00000** |
| R3 `safe_tuned.rs` | `tbl[(st & (NST - 1)) * 256 + b as usize]` | it forces it, per access, with a mask | **9.75000** |
| R4 `unsafe.rs` | `*tbl.get_unchecked(st * 256 + b)` | the author asserts it | **8.75000** |
| R5 `verus.rs` | the same, verbatim | **Verus proves it** — `12 verified, 0 errors` | **8.75000** |

Rates are `fold-loop instructions / bytes per iteration` off the disassembly of
the shipped `-O3 isolated` binaries, not marginals. `R3 − R4 = 1.00000` and
`R2 − R4 = 6.25000`, the latter decomposing as **3.00 check + 3.25 foreclosed
4× unroll** against a rolled-vs-rolled control.

⚠ **gcc's *unchecked* C fold is dearer per byte than safe Rust's masked one**
(11.00 vs 9.75) because gcc does not unroll it. Any C-vs-Rust claim here needs
the clang column.

## Files

```
spec.md        the contract, the pins, and the two forbidden entries that ARE the bug class
model.py       the independent Python reference; computes `sanitizer_expect` rather than declaring it
inputs/gen.py  deterministic blobs; audits the harm it ships, not just the bytes
c/             kernel.c (the bug) · kernel_hardened.c (R1h) · main.c (driver)
safe_naive.rs  safe_tuned.rs  unsafe.rs  verus.rs
NOTES.md       the measurements, the proof, the TCB tally and the spelling spread
```

Run `harness/check.py p19` before believing any of it.
