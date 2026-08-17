# p17 — HTTP suffix-range parser

**The pattern:** serve a list of HTTP suffix ranges (`Range: bytes=-N`, "the last
N bytes") out of a fixed-size window, folding every byte served into a checksum.

**The bug class:** CWE-191, integer **underflow**, gated on the **sign**.
`start = content_length - N` is signed, so an `N` larger than the body makes it
negative, and the only validation the code has — `if (start < end)` — passes for
a negative `start`. CVE-2017-7529, nginx's range filter.

The exact contract, the pins the gate enforces and the argument for every design
decision are in `spec.md`. The findings, the adversarial table, the TCB tally and
the perf decomposition are in `NOTES.md`.

## Why this pattern exists — it is about a limit, not a cost

Every result on this project so far is about **cost**: what safety is worth in
instructions. p17 is the first one about a **limit**, and the answer to "does
Rust fix it?" is *partly no*.

One missing `start >= 0` produces **two different harms**, and which one you get
is decided by a single attacker-controlled `u16`. The identity
`abs = body_start + start = len - s` means the served range is always
`[len - s, len)` — the read never runs past the window, it runs **backwards**:

| the attacker's `s` | what the unchecked read does | ASan | safe Rust | a proof of memory safety |
|---|---|---|---|---|
| `s <= content_len` | correct | — | correct | — |
| `content_len < s <= len` | reads the window's own **metadata** — *in bounds of the allocation* | **silent** | **reads it too** | **does not exclude it** |
| `s > len` | reads **before** the allocation | fires | panics | excludes it |

**The middle row is the point.** That read is in bounds, so bounds checking
cannot see it — not C's, not Rust's, and not a proof that every access is in
bounds. It is a **legal read of the wrong bytes**. Safe Rust eliminates the third
row and does **nothing** about the second; the only thing that fixes the second
row is the explicit `start >= 0` check, which is identical in C and in Rust and
costs the same in both.

**Which wrong bytes, though, depends on the input, and only one of the two cases
is an information disclosure.** On the single-window inputs the extra bytes are
the attacker's *own* `nsuf` word and suffix table — memory-safe and functionally
wrong, not a leak. Give the blob a second window (`adversarial-crosswin-{lo,hi}`)
and the same arithmetic reaches into the *previous* window, which is another
caller's data: that is Heartbleed's shape, and it needs a guard on the
*slice*-relative index — which is all a bounds check, or `get_unchecked`'s
`requires i < v@.len()`, ever demanded. `NOTES.md` §1b and §1c.

**Every half is demonstrated rather than asserted**, with controls built under
`.temp/` and never shipped as rungs — safe Rust with the conjunct deleted, safe
Rust and Verus with the conjunct replaced by each of the two bounds-safe guards,
and Verus with the conjunct deleted. `NOTES.md` §1a, §1c and §7 have the stdout,
the Verus diagnostics and the reproduction commands.

There is a matching result on the proof side, and it is the reason p17 is worth
more than another perf row. A proof that every access is in bounds discharges
the third row and **not** the second, *because the second row is in bounds*.
Only the functional `ensures` (`result == range_fold(..)`) catches it. So p17
measures the difference between **proving memory safety** and **proving the
program right** — a distinction this project has asserted since finding 2 and
has never been able to put a number on. p16 said, correctly for p16, that a
read-only kernel's security claim is entirely the trusted accessor's `requires`;
p17 is the counter-example, and the two together bracket the question.

## The six cells

| Rung | File | What it is |
|---|---|---|
| R1 | `c/kernel.c` | idiomatic C99, **with the bug**: `if (start < end)` and no more |
| R1h | `c/kernel_hardened.c` | R1 plus `&& start >= 0`. The whole diff is one conjunct |
| R2 | `safe_naive.rs` | the mechanical safe port: `buf[i]`, `for j in 0..n` |
| R3 | `safe_tuned.rs` | reslice the header, the suffix table and the served range |
| R4 | `unsafe.rs` | `get_unchecked` everywhere; the range test survives |
| R5 | `verus.rs` | R4's exec code with every unchecked read discharged |

R1 and R1h are built with both gcc and clang, so the pattern has 32 cells rather
than 24 (`.memory/01-ladder.md`).

## Contrast with p16, which it deliberately mirrors

p17 is p16 plus signed arithmetic: same payload head, same window/Lemire driver,
same `work_per_call = stride` convention, same trusted accessor. Everything that
differs, differs because of the sign.

| | p16 | p17 |
|---|---|---|
| underflow in | `size_t` (a *bound*) | `int64_t` (an *index*) |
| the walk runs | **forward, unboundedly** — `end - p` wraps and the loop never ends | backward, and **bounded**: `n = s <= 65535` |
| R1 on the adversarial input | SIGSEGV | **exit 0 and a wrong number** |
| ASan says | `0 bytes **after** a 3072-byte region` | `6 bytes **before** a 64-byte region` |
| harms | one | **two**, and a bounds check sees only one |
| what rules the harm out | the trusted accessor's `requires` | that for one harm; the functional `ensures` for the other |

The second row is why this one shipped in nginx and was exploited rather than
crashing in testing.

## Running it

```bash
python3 patterns/p17-http-range/inputs/gen.py     # regenerate the .bin (gitignored)
harness/check.py p17                              # the gate
harness/build.py p17                              # the 32 builds
harness/measure.py p17                            # results/p17-http-range.json
```
