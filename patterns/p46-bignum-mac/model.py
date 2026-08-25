#!/usr/bin/env python3
"""p46-bignum-mac: the independent reference model the gate checks against.

A *second* implementation of ../spec.md, in Python, from the file bytes alone.
It shares no code with the rungs beyond `common/slb.py`. The API `check.py`
requires is documented at the top of `patterns/p01-array-sum/model.py`.

--------------------------------------------------------------------------
Bindings
--------------------------------------------------------------------------

Each `iter_calls()` dict binds `buf` (the whole blob), `off`, `len`, `buf_len`
and `result`, and `helpers` supplies `bn_fold`. That is p19's set, because p46's
kernel likewise takes a *window* of an attacker-supplied blob and its `requires`
is about the window's placement inside it.

--------------------------------------------------------------------------
`work_per_call`, and the argument for its unit
--------------------------------------------------------------------------

**MAC steps per call -- `n * m` -- minimised over the windows of the blob.**
The unit is one 64x64 -> 128 multiply-accumulate, so `work_unit` is
`"MAC step"` and `work_unit_bits` is **64**: the operands are 64-bit limbs.

`.memory/05-layout.md` step 2 says the unit has to be argued rather than
assumed, because ALPHA = 0.25 Ir per unit is justified in 64-bit-lane terms.
Here that constant is very conservative and deliberately so: **x86-64 has no
SIMD widening 64x64 -> 128 multiply at all**, so a MAC step cannot be
vectorised, and the cheapest possible schoolbook step is `mulx` + `adcx` +
`adox` = 3 instructions. Measured on this box the unsafe rung runs about 10
Ir/MAC including the loop, so the floor is cleared by roughly 40x -- inside
`LOOSE_FLOOR_MARGIN` and honest. `min_ir_per_work` is NOT declared and the
harness default stands.

It is a LOWER bound and never inflated: a window that fails any of the four
guards does 0 MAC steps and contributes 0, and the minimum is taken.

--------------------------------------------------------------------------
Two implementations, cross-checked in `selfcheck()`
--------------------------------------------------------------------------

`bn_fold()` -- the helper the `ensures` is re-derived through -- runs the
schoolbook nest limb by limb with an explicit carry, exactly as the rungs do.
`_fold_bigint()` computes the same answer by converting both operands to Python
integers, multiplying once, and splitting the product back into limbs. Same
function, completely different arithmetic; `selfcheck()` fails if they ever
disagree.

⚠ **That second implementation is also the only thing in this repo that checks
the schoolbook nest against the MATHEMATICAL product.** ../verus.rs proves the
kernel matches a recursive specification of the algorithm and does NOT prove
that the algorithm computes `a * b` (../NOTES.md 6b); `_fold_bigint` closes that
gap by testing rather than by proof, on every window of every committed input.

--------------------------------------------------------------------------
`sanitizer_expect` is COMPUTED, not declared by name
--------------------------------------------------------------------------

The model simulates `c/kernel.c` -- the rung with no output-side bound -- and
reports whether any window drives a write outside `[0, OUTCAP)` of the product
scratch. That is the whole of p46's harm, and computing it means the adversarial
rows cannot be mislabelled.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1

#: Must equal `SLB_P46_OUTCAP` in c/kernel.h and `OUTCAP` in every Rust rung.
OUTCAP = 96
#: Must equal `SLB_P46_BCAP` in c/kernel.h and `BCAP` in every Rust rung.
BCAP = 256
#: What an over-long product folds to.
REJ = 0x9E3779B97F4A7C15


def _ld64(w, p):
    """Little-endian limb decode, additively -- the spelling every rung uses."""
    return (w[p] + 256 * w[p + 1] + 65536 * w[p + 2] + 16777216 * w[p + 3]
            + 4294967296 * w[p + 4] + 1099511627776 * w[p + 5]
            + 281474976710656 * w[p + 6] + 72057594037927936 * w[p + 7])


def _guards(w, ln):
    """The four tests every conforming rung makes, in order.

    Returns `(n, m)` for a window that reaches the nest, `None` for one that
    returns 0, and `"rej"` for one that returns REJ."""
    if ln < 8:
        return None
    n, m = w[0], w[1]
    if n == 0 or m == 0:
        return None
    if 8 + 8 * (n + m) > ln:
        return None
    if n + m > OUTCAP:                 # <-- c/kernel.c omits exactly this
        return "rej"
    return (n, m)


def bn_fold(buf, off, ln):
    """../spec.md's kernel, run limb by limb with an explicit carry. This is the
    helper the `ensures` is re-derived through, so it must not share code with
    `_fold_bigint`."""
    w = buf[off:off + ln]
    g = _guards(w, ln)
    if g is None:
        return 0
    if g == "rej":
        return REJ
    n, m = g
    bl = [_ld64(w, 8 + 8 * (n + j)) for j in range(m)]
    out = [0] * OUTCAP
    for i in range(n):
        ai = _ld64(w, 8 + 8 * i)
        carry = 0
        for j in range(m):
            t = ai * bl[j] + out[i + j] + carry
            out[i + j] = t & MASK
            carry = t >> 64
        out[i + m] = carry
    acc = 0
    for k in range(n + m):
        acc = (acc * 31 + out[k]) & MASK
    return ((acc * 31 + n) * 31 + m) & MASK


def _fold_bigint(buf, off, ln):
    """The same function computed as ONE Python big-integer multiply, then split
    back into limbs. Shares no arithmetic with `bn_fold`, and it is what pins the
    schoolbook nest to the mathematical product."""
    w = buf[off:off + ln]
    g = _guards(w, ln)
    if g is None:
        return 0
    if g == "rej":
        return REJ
    n, m = g
    a = sum(_ld64(w, 8 + 8 * i) << (64 * i) for i in range(n))
    b = sum(_ld64(w, 8 + 8 * (n + j)) << (64 * j) for j in range(m))
    p = a * b
    acc = 0
    for k in range(n + m):
        acc = (acc * 31 + ((p >> (64 * k)) & MASK)) & MASK
    return ((acc * 31 + n) * 31 + m) & MASK


def _unvalidated_oob(buf, off, ln):
    """`c/kernel.c`: the nest with NO output-side bound. Returns the highest
    product-scratch index the window would touch, or `None` if the window never
    reaches the nest. `>= OUTCAP` means the write leaves the array.

    This is the only place the model describes the buggy rung, and it exists so
    that `sanitizer_expect` is a measurement rather than a declaration. It does
    not simulate the corrupted values: what a real run finds past the array is
    not defined, and on this box the run usually does not survive to be asked
    (../NOTES.md 0a)."""
    w = buf[off:off + ln]
    if ln < 8:
        return None
    n, m = w[0], w[1]
    if n == 0 or m == 0:
        return None
    if 8 + 8 * (n + m) > ln:
        return None
    return n + m - 1                   # the index `out[i + m]` reaches at i = n-1


class Model:
    """Simulates ../spec.md's driver loop and kernel from the file alone.

    The kernel is evaluated once per *window* and memoised: the driver makes up
    to 20 000 calls but a blob has only a handful of distinct windows, and the
    window index is a pure function of `acc`."""

    def __init__(self, path):
        f = slb.read(path)
        self.path = path
        self.n_iters = f.n_iters
        self.declared_len = f.declared_len
        self.truncated = f.truncated
        # The drivers read exactly `payload_len` bytes and reject a short file.
        self.payload = f.payload[:f.declared_len]
        self.stride_w, self.blob = slb.head1_u64_bytes(self.payload)
        self.n_blob = len(self.blob)
        self.n_calls = 0
        self.checksum = None
        self.entered = False
        self._nwin = 0
        self._stride = 0
        self._res = []
        self._work = 0
        self._oob = False
        if not self.truncated:
            self._run()

    # -- simulation --------------------------------------------------------
    def _run(self):
        if not (0 < self.stride_w <= self.n_blob):
            self.checksum = 0
            return
        self.entered = True
        stride = int(self.stride_w)
        nwin = self.n_blob // stride
        self._stride, self._nwin = stride, nwin
        self._res = [bn_fold(self.blob, k * stride, stride) for k in range(nwin)]
        self._work = min(self._macs(k * stride, stride) for k in range(nwin))
        hi = [_unvalidated_oob(self.blob, k * stride, stride) for k in range(nwin)]
        self._oob = any(h is not None and h >= OUTCAP for h in hi)
        acc = 0
        for _ in range(self.n_iters):
            k = (acc * nwin) >> 64
            acc = (acc * 31 + self._res[k]) & MASK
        self.n_calls = self.n_iters
        self.checksum = acc

    def _macs(self, off, ln):
        """MAC steps a conforming kernel really runs on this window."""
        g = _guards(self.blob[off:off + ln], ln)
        if g is None or g == "rej":
            return 0
        return g[0] * g[1]

    def iter_calls(self):
        """Replay the driver loop, one binding per kernel call. Regenerated
        rather than stored: `small.bin` alone is thousands of calls."""
        if not self.entered:
            return
        stride, nwin = self._stride, self._nwin
        acc = 0
        for _ in range(self.n_iters):
            k = (acc * nwin) >> 64
            r = self._res[k]
            yield {"buf": self.blob, "off": k * stride, "len": stride,
                   "buf_len": self.n_blob, "result": r}
            acc = (acc * 31 + r) & MASK

    def sample_calls(self, k):
        if not self.entered or k <= 0:
            return []
        step = max(1, self.n_calls // k)
        return list(itertools.islice(
            (c for i, c in enumerate(self.iter_calls()) if i % step == 0), k))

    @property
    def helpers(self):
        return {"bn_fold": bn_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """MAC steps per call, minimised over windows -- see the module
        docstring. A lower bound on the real work, never inflated: an
        overstated `work_per_call` raises the anti-collapse floor on the
        pattern's own cells."""
        return int(self._work) if self.entered else 0

    @property
    def work_unit(self):
        return "MAC step (one 64x64 -> 128 multiply-accumulate)"

    @property
    def work_unit_bits(self):
        return 64

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Computed from the bytes: does `c/kernel.c` write outside the 96-limb
        product scratch on any window of this input? See the module docstring."""
        return "fires" if self._oob else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.truncated else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} n_blob={self.n_blob} "
                f"stride={self.stride_w} nwin={self._nwin} "
                f"calls={self.n_calls} macs/call={self.work_per_call} "
                f"san={self.sanitizer_expect} truncated={self.truncated} "
                f"expected={self.checksum}")

    def selfcheck(self):
        """Limb-by-limb schoolbook fold vs one big-integer multiply, on every
        distinct window."""
        problems = []
        if not self.entered:
            return problems
        stride = self._stride
        for k in range(self._nwin):
            a = self._res[k]
            b = _fold_bigint(self.blob, k * stride, stride)
            if a != b:
                problems.append(
                    f"schoolbook fold {a} disagrees with big-integer fold {b} "
                    f"at window {k} (off={k * stride} len={stride})")
                break
        return problems


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):30s} {m.describe()}  "
              f"selfcheck={m.selfcheck()}")
