# p17 — HTTP suffix-range parser: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, and **the two sides carry exactly the
same information**: `&[u8]` is a pointer and a length, and C spells the pair
out. C is handed the blob length and R1 ignores it, so R1-vs-R1h is a comparison
with the calling convention, the argument count and the register allocation all
held fixed. The only difference between those two cells is one conjunct.

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a four-argument call into a three-argument one. See "Driver loop".)

The return type is a plain `u64` and **not** a struct out-parameter, which is a
known harness hard stop (`dloop._apply_call_args` refuses a non-identifier
argument) and which this design does not need.

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..2        nsuf        u16 LE   number of suffix requests
byte 2..2+2n     suffixes    u16 LE each   ATTACKER DATA
body_start   =   2 + 2*nsuf
content_len  =   len - body_start           # the REAL body length, derived
```

## Semantics

```
if len < 2:                       return 0
nsuf = buf[off] + 256*buf[off+1]
if 2 + 2*nsuf > len:              return 0        # present in EVERY rung
body_start  = 2 + 2*nsuf
content_len = len - body_start
acc = 0; nserved = 0

for i in 0 .. nsuf:
    s     = buf[off+2+2i] + 256*buf[off+3+2i]     # u16, attacker-controlled
    start = content_len - s                       # <<< SIGNED (i64). May be < 0.
    end   = content_len
    if start < end && start >= 0:                 # >>> R1 KEEPS ONLY `start < end` <<<
        base = (off + body_start) + start
        n    = end - start
        for j in 0 .. n:
            acc = acc *64 31 +64 buf[base + j]
        nserved += 1

return acc *64 31 +64 nserved
```

`*64`/`+64` are wrapping, as in p01/p02/p16, so the kernel has **no precondition
on values** and every measured input is inside the verified domain by
construction. `nserved + 1` wraps too; C's `uint64_t` wraps by definition
(6.2.5p9) and the Rust rungs write `nserved.wrapping_add(1)`.

### The identity the whole design rests on

```
abs = body_start + start = body_start + content_len - s = len - s
n   = end - start        = content_len - (content_len - s) = s
```

So the served range is `[len - s, len)` — **exactly the last `s` bytes of the
window**, which is what a suffix range *means*. The kernel is therefore
semantically faithful to `Range: bytes=-N` rather than a contrivance, and note
that `abs + n == len` **always**: the read never runs *past* the window. It only
runs **backwards**, and how far back is one attacker-controlled `u16`:

| `len` | `nsuf` | `body_start` | `content_len` | `s` | `start` | `abs` | regime |
|---:|---:|---:|---:|---:|---:|---:|---|
| 64 | 3 | 8 | 56 | 10 | 46 | 54 | correct |
| 64 | 3 | 8 | 56 | 56 | 0 | 8 | correct (whole body) |
| 64 | 3 | 8 | 56 | 58 | **−2** | 6 | **leak** — in bounds, into the suffix table |
| 64 | 3 | 8 | 56 | 64 | −8 | 0 | leak — the whole window incl. `nsuf` |
| 64 | 3 | 8 | 56 | 70 | −14 | **−6** | **OOB** — before the allocation |

That table is `inputs/gen.py`'s `adversarial-leak.bin` and `adversarial-oob.bin`
verbatim, and the two files differ in **one `u16`**.

### Three harms, two of which a bounds check cannot tell apart from correct

| attacker's suffix `s` | what the unchecked read does | ASan | safe Rust | Verus `requires i < v@.len()` | Verus `ensures r == range_fold(..)` |
|---|---|---|---|---|---|
| `s <= content_len` | correct | — | correct | holds | holds |
| `content_len < s <= len` | reads the window's own **metadata** — *in bounds of the allocation* | **silent** | **also reads it** | **holds** | **FAILS** |
| `s > len` | reads **before** the allocation | fires | **panics** | FAILS | FAILS |

**The middle row is why p17 is in the catalogue.** That read is in bounds, so
bounds checking cannot see it — not C's, not Rust's, and not a proof of memory
safety. Safe Rust eliminates the third row and does **nothing** about the
second. The only thing that fixes the second row is `start >= 0`, which is
identical in C and in Rust and costs the same in both.

**Be precise about *what* the middle row discloses, because it depends on the
input and the two cases are not equally interesting.** On a **one-window** input
(`adversarial-leak.bin`, `nwin == 1`, `off == 0`) the excess over what the caller
is entitled to is a suffix of `[0, body_start)` — the `nsuf` word and the suffix
table, i.e. **the attacker's own request header, byte for byte**. That is a
memory-safe *wrong answer*, not an information disclosure, and it is structural:
with `off == 0` the read `[len - s, len)` can never reach anything but this
window. On a **multi-window** input the same arithmetic reaches into the
*previous window*, which is another caller's data and a real disclosure — but
only for a guard that permits a negative *window*-relative index, which
`start >= 0` does not and `start >= -((off + body_start) as i64)` does. That is
`adversarial-crosswin-{lo,hi}.bin` and `NOTES.md` §1c.

Correspondingly, on the Verus side, a proof that every access is in bounds
discharges the third row and **not** the second, because the second row *is* in
bounds. Only the functional `ensures` catches it. p17 is therefore the pattern
where *proving memory safety* and *proving the program right* come apart with a
measurement rather than an assertion — a distinction this project has asserted
since finding 2 and has never been able to put a number on. `NOTES.md` §7 has
both Verus diagnostics from the same one-conjunct mutation.

### Load-bearing, do not "improve"

- **`start` and `end` are `int64_t` / `i64`.** That is the CVE. Making them
  unsigned "to be safe" deletes the pattern: `start < 0` would be
  unrepresentable and the second row of the table above could not exist.
  The *spec functions* are correspondingly written over `int`, not `nat`.
- **R1 omits only `&& start >= 0`.** It keeps `len < 2` and `2 + 2*nsuf > len`,
  exactly as p16's R1 kept `end - p >= 3`. One conjunct between `c/kernel.c` and
  `c/kernel_hardened.c`, and `if (start < end)` is nginx's line 371 verbatim.
- **No `Range:` text parsing.** Byte fields, not ASCII — string parsing is
  p11–p15 and would add a second new variable.
- **`nserved` is folded into the result**, so a rung that serves a different
  *set* of ranges cannot produce the same checksum even if the bytes happened to
  fold the same way.
- **`if start < end && start >= 0 { ... }` rather than two `continue`s.**
  `.memory/05-layout.md`'s rule is that the rungs are semantically equivalent
  and that R4/R5 are textually identical; the `continue` spelling in `TASK_011`'s
  pseudocode is **not expressible in Verus** — `error: for-loops do not yet
  support continue` — and the `while` workaround has to hoist the increment
  above the guard, which is unidiomatic in all six rungs. The conjunctive
  spelling has the same semantics, gives R1-vs-R1h a one-conjunct diff, and is
  what nginx actually wrote. Measured; see `NOTES.md` §9.

### What p17 is *not*: an unbounded walk

p16's missing check made `end - p` underflow `size_t` and the walk never
terminated. **Nothing like that happens here.** `n = end - start = s <= 65535`,
so every served range is bounded and every loop ends. A signed underflow in an
*index* is quieter than an unsigned underflow in a *bound*, which is exactly why
this one shipped in nginx and was exploited rather than crashing in testing:
`adversarial-oob.bin` on a plain (non-sanitizer) R1 build **prints a wrong
number and exits 0**, where p16's R1 segfaulted.

## Contract

```
requires:  off + len <= buf_len
           buf_len <= 9223372036854775807
ensures:   result == range_fold(buf, off, len)
```

`range_fold` is the spec function; `model.py` is its independent Python twin.

Both `requires` clauses are **structural** — about the shape of the buffer the
driver built, not about its contents — so they hold on every input this
benchmark runs, `adversarial-*` included, and `harness/check.py` evaluates them
at every one of the kernel calls to prove that they do. Every suffix value a
`u16` can express is an *argument* of the problem; the kernel is total in all
65 536 of them.

The second clause is new for this project and it is not bureaucracy. p17 does
its index arithmetic in `i64`, so `(len - body_start) as i64` and
`(off + body_start) as i64` have to be shown lossless, and **vstd has no axiom
that a slice's length is at most `isize::MAX`**: `vstd::slice::axiom_spec_len`
gives `spec_slice_len(s) == s@.len()`, i.e. `<= usize::MAX`, and nothing more.
Verus also models `usize` as *possibly 32-bit*, so `x <= i64::MAX` does not even
imply `x <= usize::MAX` — both bounds appear in the loop invariants for that
reason. The driver therefore **checks** `n_blob <= 9223372036854775807` once,
outside the measured loop, rather than assuming it, and that is the third
conjunct of its guard. See `NOTES.md` §9.

### The `ensures` IS the security property here — the opposite of p16

p16's `spec.md` says, correctly for p16, that a read-only kernel's `ensures`
cannot be its security property, because "no byte outside the window was read"
is not a property of the return value. That is still true of the *third* row of
the table above, and `get_unchecked`'s discharged `requires i < v@.len()` is
still what rules it out.

But p17's *second* row is a defect that is **memory-safe**. There is no
precondition on any accessor that excludes it, because the access it makes is
legal. The only thing that excludes it is `result == range_fold(buf, off, len)`,
because `range_fold` — unlike any bounds property — *says which bytes* the
result is a fold of.

So p16 and p17 together bracket the question:

| | what rules out the harm |
|---|---|
| p16, unsigned underflow, walks forward off the end | the trusted accessor's `requires`; there is no `ensures` that says it |
| p17 row 3, signed underflow, indexes before the buffer | the same `requires` |
| **p17 row 2, signed underflow, indexes inside the buffer** | **the functional `ensures`, and nothing else** |

Consequences, both recorded in `NOTES.md` §5:

1. p17 is the first pattern where deleting one conjunct produces a **failing
   `ensures` with every memory-safety obligation still discharged**. §7 pastes
   the Verus output.
2. The verified twin (`check.py` 5c-twin) is **still idle**, and this is worth
   saying plainly because `.memory/04-verus.md` predicted its value would
   "accrue from p17 on". It does not: p17's accessor is the same single-clause
   `i < v@.len()` p01, p02 and p16 ship, precisely *because* p17's interesting
   harm is not a memory error and so cannot be a conjunct of an accessor
   precondition. Manufacturing a multi-clause accessor to exercise the mechanism
   would be gaming the gate.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p17's payload is p16's:

```
word 0     u64  stride      # bytes per window; the kernel parses one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes` — the functions p16 added to `common/`, reused verbatim,
with **nothing added to `common/` for p17**. All three are a bulk copy rather
than an element-by-element decode, which is what keeps every p17 row
Miri-checkable (`.memory/02-bench-rules.md`: `head_u64_body`'s per-element loop
is why p01's `large.bin` blocks).

Nothing is a compile-time constant: `n_iters`, `stride`, `n_blob`, every `nsuf`
and every suffix value come from the file.

**There is no `cap` and nothing is allocated from an attacker-controlled size**,
so p02's `SLB_MAX_CAP` range check and its exit 7 have no analogue here and are
deliberately not copied across, exactly as for p16.

## Driver loop

Identical in all six rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers. `harness/check.py` normalises every copy — the C one included — and
diffs it against `driver.canonical` below.

```
n_blob := bytes.len()
buf    := bytes
acc    := 0
if stride_w >= 2 and stride_w <= n_blob and n_blob <= 9223372036854775807:
    stride := stride_w as usize
    nwin   := (n_blob / stride) as u64
    it     := 0
    while it < n_iters:
        k   := ((acc as u128 * nwin as u128) >> 64) as usize
        r   := kernel(buf, k * stride, stride)
        acc := acc *64 31 +64 r
        it  := it + 1
emit(acc)
```

Three differences from p16's, all deliberate:

- **`stride_w >= 2`** rather than `>= 3`: p17's window header is the 2-byte
  `nsuf` word, not a 3-byte TLV header. `adversarial-stride1.bin` attacks it.
- **`n_blob <= 9223372036854775807`**: the `i64` bound argued under "Contract"
  above. It is *outside* the measured `while`, so it costs nothing per call, and
  it is a real range check on a real quantity — `stride_w` is a `u64` read
  straight out of the file, and the blob length is the file's length.
- the comparison is in `u64` *before* the `as usize` cast, so a truncating
  driver cannot sneak a 2^40 stride past it. (Unchanged from p16, and still
  load-bearing.)

### Why this does not evaporate

Same mechanism as p01, p02 and p16: `k` is derived from `acc`, and `acc` from
the previous call's result, so call *i+1* cannot begin until call *i* has
returned. Nothing to CSE, nothing to hoist, no `black_box` and no `asm volatile`
— the same arithmetic in both languages, so neither gets a stronger barrier than
the other. `k = (acc * nwin) >> 64` is Lemire's map onto `[0, nwin)`; see p01's
`spec.md` for why it is a multiply-shift and not a modulo.

### Why `adversarial-leak` and `adversarial-oob` are exactly one window

`k` is pseudo-random over `[0, nwin)`, so with several windows a malformed one
would be hit only probabilistically. On p17 that matters far more than it did on
p16, because p17's bad read runs **backwards**: a negative `abs` from a *middle*
window is still a valid index into the blob, so the OOB row would become a
silent wrong answer with no ASan and a gate that passed by luck. With
`nwin == 1`, `k` is always 0, `off` is always 0, and `abs < 0` is an absolute
negative index deterministically. `model.py`'s `sanitizer_expect` is written
against `off + len - s < 0` rather than `start < 0` for the same reason.

### Why `adversarial-crosswin` is two windows, and why it is exempt

`adversarial-crosswin-lo.bin` and `adversarial-crosswin-hi.bin` break that rule
deliberately, and the paragraph above is precisely the reason they are generated
as a **pair**.

The one-window rule exists because a *positional* claim — "this call reads before
the allocation" — is a coin flip once `k` can select a window. **This input makes
no positional claim.** It is a **differential**: two files identical in every byte
except window 0's secret, so the claim is *"change the victim's bytes and the
output changes, with no panic and no sanitizer report"*, and that claim is true
however `k` lands. If `k` never selects the attacker's window the two outputs
agree and nothing is asserted; if it selects it once, the disclosure is visible in
the checksum. Determinism is not needed — only the *difference* is read, and the
difference is zero unless a byte of window 0's secret reached the result.

The layout, with `stride = 64` and `n_blob = 128`:

| | `nsuf` | suffixes | `body_start` | `content_len` | what it serves |
|---|---:|---|---:|---:|---|
| window 0, `off = 0` — **the victim** | 1 | `(32)` | 4 | 60 | `buf[32..64)` only. `buf[4..32)` is the **secret** and no rung that keeps `start >= 0` ever reads it |
| window 1, `off = 64` — **the attacker** | 3 | `(10, 56, 122)` | 8 | 56 | `s = 122` ⇒ `start = −66`, `abs = off + len − s = 6` |

Two design constraints are load-bearing and must survive any edit.

- **Window 0 has to serve something.** A window that serves no range returns 0,
  `acc` stays 0, and `k = (acc * nwin) >> 64` is then 0 for ever — the driver's
  multiply-shift has an **absorbing state at `acc == 0`** and window 1 would never
  be visited at all. Serving 32 bytes makes window 0's result a full-width
  pseudo-random `u64` on the first call.
- **`s = 122` keeps `abs = 6 ≥ 0`.** Every read on this input, in *every* rung
  including R1, is inside the blob, so `model.py` derives `sanitizer_expect =
  "clean"` and ASan must stay silent. This input is about disclosure, not about
  memory safety; `adversarial-oob.bin` is the memory-safety input and this one
  must not accidentally become a second copy of it.

The guards, and what each does with the third request — this is the whole
experiment and rows 2 and 3 are one token apart:

| guard | third request | discloses window 0? |
|---|---|---|
| none (R1, `c/kernel.c`) | served | **yes** |
| `start >= -(body_start as i64)` — window-relative (`NOTES.md` §7 M4) | rejected, `−66 < −8` | no |
| `start >= -((off + body_start) as i64)` — **slice**-relative, i.e. all a bounds check or `get_unchecked`'s `requires i < v@.len()` actually demands | served, `−66 ≥ −72` | **yes** |
| `start >= 0` — R1h, R2, R3, R4, R5 | rejected | no |

Measured outputs for all four, and the Verus verdicts that go with them, are in
`NOTES.md` §1c.

### The C/Rust arity gap, and `driver.call_args`

The C loop calls `kernel(buf, n_blob, k * stride, stride)` and the Rust loop
calls `kernel(buf, k * stride, stride)`. `driver.aliases` cannot reconcile that
— both sides of an alias are a dotted identifier path, so an alias renames and
can do nothing else. `driver.call_args` declares which argument *positions* of a
named call are the canonical ones (`{"c": {"kernel": [0, 2, 3]}}`), and
`harness/dloop.py` refuses to drop anything that is not a single bare
identifier, so no prefetch, no side effect and no extra statement can hide in
the argument the diff stops looking at.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. p01's `spec.md` explains what each pin closes;
what is worth saying here is the arithmetic behind the two obligation counts,
because a declared number a reviewer cannot check from `spec.md` alone is
exactly what `.memory/02-bench-rules.md` forbids.

| pin | why |
|---|---|
| `verus.obligations` = 10 | **`fold_bytes` 1 + `range_walk` 1 + `kernel` 3 + `main` 5 = 10.** Every term is checkable with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained: the two *recursive* spec fns carry one termination query each; `nsuf_at`, `suf_at` and `range_fold` are non-recursive and carry **0**; the three `external_body` items carry **0**; `kernel` is 1 for the body + 1 per loop body (there are two loops); and `main` is 1 for the body + 1 for the driver loop + one per `by (nonlinear_arith)`/`by { .. }` sub-proof in its two ghost blocks. `.memory/04-verus.md`'s rule of thumb — one query per function plus one per loop — gives **7** here and is therefore not the derivation, exactly as on p16. The two patterns landing on the same total is a coincidence of skeleton, not evidence of anything. |
| `verus.twin_obligations` = 11 | the count in the **other** configuration, `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twin. **10 shipped + 1**, and the 1 is measured the same way: `--cfg slb_twin --verify-function slb_twin_get_unchecked --verify-root` reports `1 verified` — one function, no loop body, no `by`-block. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`. Since TASK_010 that no longer makes Miri optional: it is mandatory for any pattern with a trusted item, because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`. `check.py` derives this from `verus.rs` rather than reading the flag. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": ["off + len <= buf_len", "buf_len <= 9223372036854775807"],
  "ensures": ["result == range_fold(buf, off, len)"],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (range_fold). NOTE WHAT THE ensures IS, AND THAT IT IS THE OPPOSITE OF p16's: on p16 the ensures was the value and the security property was the trusted accessor's requires, because the harm was a read outside the buffer. p17 has TWO harms. The one that leaves the allocation is still excluded by `i < v@.len()`. The one that stays INSIDE it -- content_len < s <= len, a read of the window's own suffix table -- is memory-safe, so no accessor precondition can exclude it and `result == range_fold(buf, off, len)` is the only thing that does. See the prose above and NOTES.md 5.",

  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "r": "result"
    },
    "obligations": {"verus.rs": 10},
    "twin_obligations": {"verus.rs": 11},
    "obligations_note": "10 = fold_bytes 1 + range_walk 1 + kernel 3 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`. nsuf_at, suf_at and range_fold are non-recursive spec fns and carry 0; get_unchecked, load_input and emit are external_body and carry 0; kernel is body + 2 loop bodies. **main's 5 does not decompose from the command line and is quoted AS MEASURED**: body + driver loop + one per `by`-block predicts 1 + 1 + 4 = 6 -- two `by (nonlinear_arith)` and one `by { lemma2_to64_rest() }` in the first ghost block, one `by (nonlinear_arith)` in the second -- and Verus reports 5, so at least one sub-proof is not its own query. The earlier text here asserted that 6-term derivation as if it were the count and was arithmetically wrong; p05's spec.md carries the same correction for a character-identical driver and its NOTES.md 5 flagged this one. `.memory/04-verus.md`'s one-per-function-plus-one-per-loop rule of thumb gives 7 here and is therefore not the derivation either.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twin. 10 shipped + 1, and the 1 is measured: `--cfg slb_twin --verify-function slb_twin_get_unchecked --verify-root` reports `1 verified` -- one function, no loop body, no `by`-block. Pinned for the same reason the shipped count is: `tv > base_v` only says something extra compiled, and a twin that quietly lost its body, or an item that exists only under the cfg, moves this number and nothing else.",
    "items": {
      "verus.rs": {
        "nsuf_at":    {"external": null, "requires": [], "ensures": []},
        "suf_at":     {"external": null, "requires": [], "ensures": []},
        "fold_bytes": {"external": null, "requires": [], "ensures": []},
        "range_walk": {"external": null, "requires": [], "ensures": []},
        "range_fold": {"external": null, "requires": [], "ensures": []},
        "get_unchecked": {"external": "verifier::external_body",
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "slb_twin_get_unchecked": {"external": null,
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "load_input": {"external": "verifier::external_body",
                       "requires": [], "ensures": []},
        "emit":       {"external": "verifier::external_body",
                       "requires": [], "ensures": []},
        "kernel":     {"external": null,
                       "requires": ["off + len <= buf@.len()",
                                    "buf@.len() <= 9223372036854775807"],
                       "ensures": ["r == range_fold(buf@, off as int, len as int)"]},
        "main":       {"external": null, "requires": [], "ensures": []}
      }
    }
  },

  "driver": {
    "statements": 12,
    "c_source": "c/main.c",
    "regions": ["safe_naive.rs", "safe_tuned.rs", "unsafe.rs", "verus.rs",
                "c/main.c"],
    "aliases": {"c": {"n_body": "bytes.len()",
                      "bytes": "bytes.as_slice()",
                      "inp.n_iters": "n_iters"}},
    "call_args": {"c": {"kernel": [0, 2, 3]}},
    "canonical": [
      "n_blob = bytes . len ( ) ;",
      "buf = bytes . as_slice ( ) ;",
      "acc = 0 ;",
      "if stride_w >= 2 && stride_w <= n_blob && n_blob <= 9223372036854775807",
      "{",
      "stride = stride_w ;",
      "nwin = n_blob / stride ;",
      "it = 0 ;",
      "while it < n_iters",
      "{",
      "k = acc * nwin >> 64 ;",
      "r = kernel ( buf , k * stride , stride ) ;",
      "acc = acc * 31 + r ;",
      "it = it + 1 ;",
      "}",
      "}"
    ]
  },

  "collapse": {
    "probe_inputs": ["small.bin", "large.bin"],
    "probe_iters": [100, 200],
    "note": "work_per_call is the WINDOW in bytes -- the stride, 506 on small and 4093 on large -- and the two differ precisely so that check.py's d(Ir)/d(work) assertion has two probe shapes and can run at all. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per byte applies unchanged; that is legitimate here for p16's reason -- the inner loop is a serial `acc = acc*31 + byte` Horner chain, so there is no bulk-memory instruction and no vector form that could undercut the default. ONE HONEST DIFFERENCE FROM p16: there the window was a strict OVER-estimate of the bytes folded, so the derived floor erred strict. Here it is an UNDER-estimate -- every suffix serves a slice of the same body, so nsuf requests can each serve nearly all of it, and the shipped inputs fold 871 bytes per 506-byte window and 7145 per 4093-byte window (1.72x and 1.75x the unit). The floor is therefore looser than the work actually done. Measured margins are in NOTES.md 4."
  },

  "identity": [
    {"a": "unsafe", "b": "verus", "O0": "norel", "O3": "exact",
     "why": "R4 == R5: the proof licenses unsafe code at zero cost, on a kernel doing signed index arithmetic whose two loop bounds both come from attacker data (10 obligations, a recursive spec function over the suffix table, a nested fold invariant, and two nonlinear steps in the driver). At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."}
  ],

  "miri": {
    "pair": ["unsafe", "verus"],
    "sources": ["unsafe.rs"],
    "required": true,
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. On p17 there is a second reason worth stating: R4's kernel casts an i64 to usize on every served byte, and a cast that is only sound because of a check the C rung omits is exactly the shape a UB checker should be pointed at. Every input here is Miri-checkable: the cost is 4 iterations x the bytes folded per call, and the largest is 7145 bytes against a budget of ~3 M.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed."
  }
}
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success; checksum on stdout |
| 2 | wrong argument count |
| 3 | cannot open input file |
| 4 | file shorter than the 16-byte header |
| 5 | `payload_len` exceeds the bytes present |
| 6 | allocation failure (C only) |

There is no exit 7 here, for p16's reason: p17's payload names no allocation
size, so p02's `SLB_MAX_CAP` check would be dead code.

## Degenerate shapes

`stride_w >= 2 && stride_w <= n_blob && n_blob <= 9223372036854775807` is the
driver's whole input validation. A stride below 2 cannot hold the `nsuf` word
(`adversarial-stride1.bin`); a stride above `n_blob` leaves no whole window, so
`nwin` would be 0 and `k` would have nothing to index. Either way the loop is
skipped and the driver prints `0` after **zero** kernel calls.

A window whose `nsuf` does not fit (`adversarial-nsuf.bin`) is different and the
difference is deliberate: there the calls *do* happen and the **kernel** is what
rejects, on `2 + 2*nsuf > len` — the test **every** rung including R1 keeps — so
all eight cells return 0 on every call and print 0. It is the control for the
two real adversarial inputs: the same "the header lied" shape with the suffix
*values* innocent.

The kernel's `len < 2` guard is, given the driver's `stride_w >= 2`, unreachable
in this benchmark. It is kept anyway so the kernel is **total** and its
`requires` stays purely structural; the alternative — a `len >= 2` precondition
— would be a precondition about the driver's own guard rather than about the
buffer, and `.memory/02-bench-rules.md` is explicit that a `requires` narrow
enough to make the proof easy is a `requires` no caller should have to
discharge. `NOTES.md` §9 records that it is dead and why it stays.
