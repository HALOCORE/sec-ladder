# p49 — interned / deduplicated string pool, and a write through a borrowed buffer

**The one-sentence version.** Two records legitimately share one buffer, because
that is what an intern pool *is*; the cycle-breaker then writes through it and
silently rewrites the other record's value. `spec.md` has the reasoning and the
pins, `c/kernel.h` the kernel in pseudocode, `NOTES.md` the numbers and what they
do not support.

The C mechanism is `CVE-2022-40304`'s, admitted at `TASK_143` and re-adjudicated
and **upheld at `TASK_160` by running it** against the 32-row tree.

## What makes this row unlike every other one

⚠⚠ **Nothing is freed. Nothing is allocated. Every index is in bounds. ASan,
UBSan, Miri and the glibc allocator are silent on every input, adversarial ones
included, at both optimisation levels on both compilers.**

> **The checksum is the only instrument this row has.**

`model.py` therefore carries the whole result, and `controls/detectors.py`'s
positive controls are load-bearing here in a way they are not elsewhere: on a row
where every column is silent, a control that *fires* is the only thing separating
*silent* from *not linked in*.

✅ **That is the exact inverse of `p34`'s detector-only cell**, where the two
rungs' checksums are bit-identical and ASan is the only discriminator. **The two
rows bracket *which instrument sees the harm* from opposite ends.**

## The kernel, in one screen

```
mem[64]                       the pool: mem[0..20) SHARED arena, mem[20..64) PRIVATE
ekey/elen/eoff[8]             the dedup table
roff/rlen/rshd[12]            the records: offset, width, "is this buffer shared?"

per op (2 bytes: opcode c, operand a):
  w = 1 + a % 6 ; key = a % 7          <- THE WIDTH COMES FROM THE FILE
  DEFINE (c%4 in {0,1}):
      w < 4  ->  INTERN: look (key,w) up in the table.
                 HIT  -> roff[nrec] = eoff[f]   <<< THE ALIAS, AND IT IS CORRECT
                 MISS -> materialise w bytes at abump, record the entry
      w >= 4 ->  OWN: materialise w bytes at pbump
  BREAK  (c%4 == 2):  t = a % nrec
                      <<< THE SAFETY LINE GOES HERE >>>
                      mem[roff[t]] = 0          <<< THE WRITE
  READ   (c%4 == 3):  fold record t's content
epilogue: fold every record's content AND its rshd flag, then nrec
```

`c/kernel.c` has no safety line. `c/kernel_hardened.c` has

```c
if (rshd[t]) {                                  /* not mine to write */
    if (pbump + rlen[t] > P49_MEM) v = P49_SENT;         /* cannot un-share */
    else { copy w bytes to pbump; roff[t] = pbump; rshd[t] = 0; ... }
}
```

## Four things a reader should not have to dig for

1. **Why this is not `p08`.** `p08` is one `memcpy` whose ranges overlap: the
   overlap is UB, lasts one call, is an arithmetic accident, and the repair is a
   different function. Here the sharing is by design, is correct, is not UB at
   all, persists, and the repair is an ownership test before a write.
   `controls/no_overlap.py` re-derives from the shipped blobs that this kernel
   has **no overlapping copy at all** and that two records' content ranges either
   coincide exactly or are disjoint — never partial, which is the only kind
   `p08` has.
2. **Why the safety line is `cow` and not the upstream patch.** Upstream fixes
   the *provenance* — never borrow — which deletes the deduplication and
   **changes a benign observable**. `controls/spellings.py` builds both and
   prices them.
3. **Why the reduction this row came from had a dead branch, and what fixing it
   cost.** `.temp/t160/red/k40304.c` fixed the content width at 3 against a
   threshold of 5, so the guard could never be false. Deriving the width from the
   input made both branches live — and turned three straight-line operations
   into loops, which at R5 cost three recursive spec functions, four verified
   helper loops and two induction lemmas. `NOTES.md` 8 counts it.
4. **Safe Rust offers both the bug and the repair.** `Rc<RefCell<Buf>>`
   reproduces `c/kernel.c` bit for bit, safely; `Rc<Buf>` with `Rc::make_mut` is
   copy-on-write supplied by the standard library. `controls/safe_arms.py` builds
   all three ports. **That is the opposite of `p34`.**

## Reproducing

```sh
python3 patterns/p49-interned-pool/inputs/gen.py
harness/build.py p49
harness/measure.py p49
harness/report.py p49
harness/check.py p49
```

Every control in `controls/` is a standalone script; `spec.md`'s *Reproducing*
section lists them in order.
