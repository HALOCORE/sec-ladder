# p12 — `strcat` into a fixed buffer

**The classic stack buffer overflow**, and the pattern this project was missing:
every other bug here is a *read*, and p02's write is a bulk `memcpy` into a
caller-supplied buffer whose length came from the file. p12 appends
NUL-terminated strings into a **fixed local `uint8_t dst[128]`** and R1 never
asks whether the next one fits.

```
window:  nstr:u32 LE, then packed NUL-terminated strings
kernel:  for each declared string
             q    = first NUL at or after p, capped at the window end
             slen = q - p
             if dlen + slen <= DST_CAP:        <<< R1 omits THIS LINE
                 append buf[off+p .. off+q] to dst
             acc = acc*31 + slen
         acc = fold(dst[0 .. dlen], acc)
         return (acc*31 + dlen)*31 + nstr
```

## What is new here

- **The first pattern whose safe rung cannot express the bug at all.** `dst` is a
  `[u8; 128]`; there is no safe Rust that writes past it. p08 established that
  shape for *aliasing*; p12 is the same shape on *length*.
- **The first pattern where the two C cells differ in behaviour, not in speed.**
  On `adversarial-overflow` gcc aborts on its `-fstack-protector-strong` canary
  (exit 134) and clang segfaults (139), on identical source at identical flags.
  On `adversarial-off1` — one byte over — **both exit 0 with a wrong answer**.
  `NOTES.md` 0 has the ladder: the failure mode is a function of the overflow
  magnitude, not of the input's position in the blob.
- **The bounds check costs the copy IDIOM, not a per-byte surcharge.** The copy
  is a hand-written byte loop in the source of five of the seven cells, and gcc,
  clang and rustc all turn it back into `memcpy` — in every one of them *except*
  the safe-naive rung, which is the only cell in the pattern with no
  bulk-memory call at all. `NOTES.md` 3.
- **The second trusted item in this project that writes**, and the first whose
  licensing guard sits a loop level above the store rather than in the same basic
  block. `NOTES.md` 2 and 6.

## What it cannot do, and why that is a result

`harness/check.py` requires every cell *including R1* to agree with `model.py` on
every non-adversarial input. R1 omits the capacity check, so any window where the
check fires makes R1 fold different bytes and a different `dlen`. **A row on
which a write bug fires cannot also be a checksum-agreeing row** — where p11 has
`adversarial-zerotail`, a header lie on which even R1 agrees, p12 has nothing.
So `small` and `large` are 100% accept by construction, they exercise the check
on the accept path only, and the acceptance axis lives in `sweep-a*` and the
adversarial rows. `NOTES.md` 1.

## Files

| file | what |
|---|---|
| `spec.md` | the contract, and the pins `harness/check.py` enforces |
| `model.py` | the independent Python reference (two implementations, cross-checked) |
| `inputs/gen.py` | deterministic input generation; `.bin` is gitignored |
| `c/kernel.c` | R1 — no capacity check. **the bug** |
| `c/kernel_hardened.c` | R1h — one `if`, and that is the whole diff |
| `c/main.c` | the C driver loop |
| `safe_naive.rs` | R2 — indexed, byte-loop copy |
| `safe_tuned.rs` | R3 — reslice, `copy_from_slice`, iterator fold |
| `unsafe.rs` | R4 — `get_unchecked` / `get_unchecked_mut` |
| `verus.rs` | R5 — R4's exec code plus the proof |
| `controls/gen_controls.py` | the mutants and the out-of-contract variants |
| `NOTES.md` | what was measured |

## Running

```bash
python3 patterns/p12-strcat-fixed/inputs/gen.py           # the 8 matrix inputs
python3 patterns/p12-strcat-fixed/inputs/gen.py --sweep    # + the two sweep bands
python3 harness/check.py p12                               # the gate
python3 harness/measure.py p12                             # the numbers
```
