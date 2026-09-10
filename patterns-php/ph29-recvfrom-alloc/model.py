#!/usr/bin/env python3
"""ph29-recvfrom-alloc: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where ph29 differs.

    bindings      buf/off/len/buf_len/result. The kernel's destination is a
                  buffer of its own that it frees before returning, so there is
                  no destination to bind before and after. What escapes the call
                  is the u64.
    work_per_call the WINDOW, in bytes -- `stride`, constant across every call
                  on a given input. Argued below.
    sanitizer     derived, not tabulated: "fires" iff some call the driver makes
                  writes more bytes than `_emalloc` actually returned.

⚠⚠ WHICH ALGORITHM THIS MODEL IMPLEMENTS, BECAUSE IT IS NOT R1's AND IT IS NOT
R1h's EITHER. It is `stream_socket_recvfrom` **made memory-safe**, which is
exactly `safe_naive.rs` / `safe_tuned.rs` / `unsafe.rs` / `verus.rs`:

    R1     streamsfuncs.c:300-345 as shipped in 5.0.0 -- CRASH-097. The receive
           is given `to_read` and the block is `real_size` bytes.
    R1h    + 445daac3ab1a (Ilia Alshanetsky, 2004-07-28), `if (to_read <= 0)
           RETURN_FALSE`. ⚠⚠ THAT FIX DOES NOT REMOVE THE DEFECT: it refuses
           `to_read <= 0` and lets `to_read = 4294967295` through to the same
           truncation. `controls/fix_scope.py` measures exactly what it buys.
    R2-R5  the same function with the copy bounded by the buffer.

⚠ So on an ADVERSARIAL input there are THREE behaviours, not two -- R1 writes
out of bounds, R1h returns its refusal sentinel, and R2-R5 clamp -- and
`check.py` stage 4 records all three rather than requiring agreement. On every
BENIGN input all six rungs agree, and that is what stage 2 checks.

Three independent implementations, as p01/p02/p16, ph03, ph07 and ph16 do:

  * the **simulation** (`_window`) walks each window once with imperative loops
    over integer cursors and returns the folded result. Per-window results go in
    a table, which is what makes 25 000 driver iterations tractable;
  * the **helper** `recv_fold` -- the one the derived `ensures` is evaluated
    against -- is built out of RECURSIVE folds with no cursor variable and no
    table, mirroring the Verus spec functions `foldb` / `recv_win` in
    ../verus.rs;
  * `_dumb`, a third spelling that materialises the destination buffer as a
    Python list, performs the copy and the NUL store into it, and folds the
    list -- i.e. it models the BUFFER rather than the arithmetic.

`selfcheck()` runs them against each other -- on the shipped inputs AND on
synthetic windows it builds itself over a domain no input file contains -- and a
disagreement is reported there rather than absorbed into a green line.

⚠⚠ **THE SYNTHETIC SWEEP IS NOT DECORATION.** `PROTOCOL_PHP.md` §A2a rule 2: a
second implementation is only as strong as the domain it is exercised over, and
`inputs/` is not a domain -- it is six files. ph03 shipped for a full task with
its two implementations computing different functions because its corpus took
one arm of a two-armed branch.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
U32 = (1 << 32) - 1

#: The window's head, in bytes. `c/kernel.c` pins it as `PH29_HEAD` and
#: `selfcheck` check 5 parses it back out rather than trusting this line.
HEAD = 12

#: zend_alloc.h:63-64 / zend_alloc.c:136 -- a block with `real_size <= 87` is
#: pushed onto the size-class cache by `_efree` and never returned to `malloc`.
CACHE_MAX_REAL = 87

#: `php_shim_tally()`'s mixing constants -- `common-php/emalloc_shim.h`.
T_ALLOC, T_FREE, T_HIT, T_BYTES = 1000003, 1000033, 1000037, 1000039


def real_size_of(size):
    """`Zend/zend_alloc.c:129` + `:135` -- truncation T1. The rounding is done
    in 64 bits and the STORE into `unsigned int real_size` is what truncates."""
    return ((size + 7) & ~7) & U32


def recorded_size_of(size):
    """`Zend/zend_alloc.h:53` -- truncation T2, `unsigned int size:31`. A
    DIFFERENT modulus from T1, and the only size the block itself records."""
    return (size & U32) & 0x7FFFFFFF


def tally_of(n_free, real_size):
    """`php_shim_tally()` after ONE request. `php_shim_reset()` empties the
    cache at the top of every kernel call, so `n_alloc` is 1 and `n_cache_hit`
    is 0; `n_free` is 1 exactly when the zval destructor ran."""
    return ((1 * T_ALLOC) ^ (n_free * T_FREE) ^ (0 * T_HIT)
            ^ ((real_size * T_BYTES) & MASK)) & MASK


class Model:
    """Simulates ../spec.md's driver loop and kernel from the file alone."""

    def __init__(self, path):
        f = slb.read(path)
        self.path = path
        self.n_iters = f.n_iters
        self.declared_len = f.declared_len
        self.truncated = f.truncated
        # The drivers read exactly `payload_len` bytes and reject a short file.
        self.payload = f.payload[: f.declared_len]
        self.stride, self.buf = slb.head1_u64_bytes(self.payload)
        self.n_blob = len(self.buf)
        self.n_calls = 0
        self.checksum = None
        self.entered = False
        self.nwin = 0
        self._win = []                # per window: (result, oob_bytes)
        self.any_oob = False          # some call the driver makes writes OOB
        if not self.truncated:
            self._run()

    # -- decoding ----------------------------------------------------------
    @staticmethod
    def _unpack(win):
        """(to_read, ctl, want, navail, n_pay) for one window's bytes."""
        tr = int.from_bytes(win[0:8], "little")          # the u64 bit pattern
        to_read = tr - (1 << 64) if tr >= (1 << 63) else tr
        ctl = win[8] | (win[9] << 8)
        want = win[10] | (win[11] << 8)
        n_pay = len(win) - HEAD
        return to_read, ctl, want, want % (n_pay + 1), n_pay

    # -- implementation 1 of 3: the imperative simulation -------------------
    def _window(self, off):
        """(result, bytes R1 would write past the block) for one window.

        The second element is what makes `sanitizer_expect` a derivation: it
        records the access R1 performs and this model does not."""
        win = self.buf[off: off + self.stride]
        to_read, ctl, want, navail, n_pay = self._unpack(win)

        size = (to_read + 1) & MASK                      # :321 emalloc(to_read+1)
        real_size = real_size_of(size)                   # T1 -- what it RETURNS
        recorded = recorded_size_of(size)                # T2 -- what it RECORDS
        cap = real_size

        # :323 php_stream_xport_recvfrom -> php_stream_read(stream, buf, to_read)
        remote_len = 0
        oob = 0
        if ctl & 2:
            recvd = -1
        else:
            buflen = to_read & MASK                      # (size_t)to_read
            n_c = min(navail, buflen)                    # what R1 copies
            n = min(n_c, cap)                            # what a bounded copy does
            # R1 writes `n_c` bytes plus the NUL at `read_buf[n_c]`; the block
            # is `cap` bytes. Anything past that is outside the malloc region,
            # because `_emalloc` allocates `header + cap` and hands back
            # `header + 0` (zend_alloc.c:182, :216).
            if n_c + 1 > cap:
                oob = n_c + 1 - cap
            if ctl & 1:
                remote_len = n % 32
            recvd = n

        h = 0
        n_free = 0
        remote_is_string = 0
        if recvd >= 0:
            if (ctl & 1) and remote_len:
                remote_is_string = 1
            for i in range(recvd):
                h = (h * 31 + win[HEAD + i]) & MASK
            n_free = 1

        acc = 0
        acc = (acc * 31 + h) & MASK
        acc = (acc * 31 + (recvd & U32)) & MASK
        acc = (acc * 31 + remote_len) & MASK
        acc = (acc * 31 + remote_is_string) & MASK
        acc = (acc * 31 + recorded) & MASK
        acc = (acc * 31 + tally_of(n_free, real_size)) & MASK
        return acc, oob

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if 16 <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                r, oob = self._win[k]
                if oob > 0:
                    self.any_oob = True
                acc = (acc * 31 + r) & MASK
            self.n_calls = self.n_iters
        self.checksum = acc

    def iter_calls(self):
        """Replay the driver loop, yielding one binding per kernel call."""
        if not self.entered:
            return
        acc = 0
        for _ in range(self.n_iters):
            k = (acc * self.nwin) >> 64
            r = self._win[k][0]
            yield {"buf": self.buf, "off": k * self.stride, "len": self.stride,
                   "buf_len": self.n_blob, "result": r}
            acc = (acc * 31 + r) & MASK

    def sample_calls(self, k):
        if not self.entered or k <= 0:
            return []
        step = max(1, self.n_calls // k)
        return list(itertools.islice(
            (c for i, c in enumerate(self.iter_calls()) if i % step == 0), k))

    # -- implementation 2 of 3: the recursive helper ------------------------
    # This is what the derived `ensures` is evaluated against, so it must not be
    # the simulation in disguise. It mirrors the *Verus* spec functions
    # (../verus.rs `foldb` / `recv_win`): RECURSIVE where `_window` is
    # iterative, and reading the WINDOW rather than a destination buffer,
    # because after the copy the two agree on every index the fold touches.
    @staticmethod
    def _foldb(s, base, i, n, acc):
        """One application of ../verus.rs's `foldb`, driven to its fixpoint.

        ⚠ Written as a loop over a pure transition rather than as Python
        recursion: a window can carry 4 064 payload bytes, which would be 4 064
        frames and a `RecursionError` on the default limit. Each step is exactly
        one unfolding of the spec function."""
        while i < n:
            acc = (acc * 31 + s[base + i]) & MASK
            i += 1
        return acc

    def recv_fold(self, buf, off, ln):
        """`recv_fold` in ../verus.rs: what the kernel must return."""
        win = buf[off: off + ln]
        to_read, ctl, want, navail, n_pay = self._unpack(win)
        size = (to_read + 1) & MASK
        rs = real_size_of(size)
        rec = recorded_size_of(size)
        failed = bool(ctl & 2)
        n = 0 if failed else min(navail, to_read & MASK, rs)
        remote_len = ((n % 32) if (ctl & 1) else 0) if not failed else 0
        ris = 1 if (not failed and (ctl & 1) and remote_len) else 0
        h = 0 if failed else self._foldb(win, HEAD, 0, n, 0)
        n_free = 0 if failed else 1
        acc = 0
        acc = (acc * 31 + h) & MASK
        acc = (acc * 31 + (U32 if failed else n)) & MASK
        acc = (acc * 31 + remote_len) & MASK
        acc = (acc * 31 + ris) & MASK
        acc = (acc * 31 + rec) & MASK
        acc = (acc * 31 + tally_of(n_free, rs)) & MASK
        return acc

    @property
    def helpers(self):
        return {"recv_fold": self.recv_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone.

        **Why the window and not the datagram.**
        `check.py::check_marginal_ir` needs one scalar per input and hard-fails
        on `work_per_call = 0`. The bytes actually copied are
        `navail = want % (n_pay + 1)`, which is ATTACKER DATA and varies per
        window; the stride is what the payload header fixes and the attacker
        cannot move. It is a strict over-estimate -- a call copies `navail`
        bytes, folds `recvd` of them and allocates `real_size` -- and an
        over-estimate raises the derived floor, which is the direction a floor
        should err.

        ⚠ `inputs/gen.py` draws BOTH `navail` and `to_read` relative to
        `n_pay = stride - 12`, so the copy, the fold and the allocation all
        scale with `work_per_call`; the per-call allocator overhead (one
        `php_shim_reset`, one `_emalloc`, one `_efree`, one
        `php_shim_shutdown`) is a FIXED term that does not, and ../NOTES.md §8
        decomposes the marginal rather than presenting it as a pure copy
        rate."""
        return self.stride if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        ⭐ **UNLIKE ph16 THERE IS NO SILENT BAND HERE, AND THE REASON IS THE
        SHIM's OWN LAYOUT.** `php_shim_emalloc` calls
        `malloc(sizeof(header) + padding + real_size)` and returns
        `p + sizeof(header) + padding` (`zend_alloc.c:182`, `:216`), so the
        payload ends exactly where the malloc region ends. Every byte past
        `real_size` is past the region and ASan reports it -- there is no
        redzone-versus-live-neighbour cliff to straddle. Measured:
        `controls/oracle.py`, and `.temp/php27/reach.c` reports
        `0 bytes after 24-byte region` on the row's own trigger.

        Note "the driver makes": windows are picked from a checksum-derived
        index, so a hostile window that is never selected must not be declared.
        That is why every adversarial input has exactly one window --
        `inputs/gen.py`. (`adversarial-nowin.bin` has ZERO, which is its whole
        point, and declares `clean`.)"""
        return "fires" if self.any_oob else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # The DRIVER allocates nothing from an attacker-controlled size, so
        # p02's exit 7 has no analogue here; the KERNEL's allocation goes
        # through the shim, whose failure arm returns NULL rather than exiting.
        # `slb_load` rejecting a short file is the only non-zero exit this
        # pattern's driver produces.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B san={self.sanitizer_expect} "
                f"oob={self.any_oob} truncated={self.truncated} "
                f"expected={self.checksum}")

    # -- implementation 3 of 3 ---------------------------------------------
    @staticmethod
    def _dumb(win):
        """A third spelling of one window's answer: materialise the destination
        buffer as a Python list of zeroes, do the copy and the NUL store into
        it, then fold the list. Deliberately naive, deliberately modelling the
        BUFFER where `recv_fold` models the arithmetic, and deliberately NOT
        sharing either one's code.

        ⚠ **The buffer is materialised only as far as anything touches it, and
        `cap` is carried separately as the LENGTH.** `real_size` can be 2^31 --
        the synthetic sweep drives `to_read = 2^31 - 1` on purpose -- and a
        Python list that long is ~16 GiB. The indices this spelling ever reads
        or writes are `[0, n]` with `n <= navail <= n_pay`, and every element
        past that is provably still zero, so `min(cap, n_pay + 2)` elements are
        the whole of the modelled object. ⚠ The elision was NOT free: the first
        version of this method allocated `[0] * real_size` and took the process
        to 25 GB RSS on the shipped corpus."""
        to_read, ctl, want, navail, n_pay = Model._unpack(win)
        size = (to_read + 1) & MASK
        rs = ((size + 7) & ~7) & U32
        rec = (size & U32) & 0x7FFFFFFF
        cap = rs                                      # the block's LENGTH
        remote_len = 0
        if ctl & 2:
            recvd = -1
            n = 0
        else:
            n = navail
            if (to_read & MASK) < n:
                n = to_read & MASK
            if n > cap:
                n = cap
            if ctl & 1:
                remote_len = n % 32
            recvd = n
        dest = [0] * min(cap, n + 2)
        if recvd >= 0:
            for i in range(n):
                dest[i] = win[HEAD + i]
        h = 0
        n_free = 0
        ris = 0
        if recvd >= 0:
            if (ctl & 1) and remote_len:
                ris = 1
            if recvd < cap:
                dest[recvd] = 0
            for i in range(recvd):
                h = (h * 31 + dest[i]) & MASK
            n_free = 1
        acc = 0
        for v in (h, recvd & U32, remote_len, ris, rec,
                  tally_of(n_free, rs)):
            acc = (acc * 31 + v) & MASK
        return acc

    # -- driving BOTH implementations on a window no input file contains ----
    @staticmethod
    def _both(win):
        """(simulated, recv_fold) for an arbitrary window, off-corpus.

        `Model.__new__` skips `__init__` deliberately: `_window` and
        `recv_fold` read only `buf` and `stride`, so this drives the SHIPPED
        code paths on bytes chosen here rather than on bytes `inputs/` happens
        to carry."""
        m = Model.__new__(Model)
        m.buf, m.stride = win, len(win)
        return m._window(0)[0], m.recv_fold(win, 0, len(win))

    @staticmethod
    def _synthetic_windows():
        """Windows spanning a domain `inputs/` cannot, built here, yielded as
        (label, bytes). ⚠ **`inputs/` is not the domain and must never be
        mistaken for it** -- see the module docstring.

        Five families, each isolating one thing the implementations could
        disagree about:

          a. `to_read` on and around EVERY truncation boundary -- 0, +-1, the
             two ends of the 32-bit window, `2^32 - 1`, `2^32`, `2^33 - 1`,
             `LONG_MAX`, `LONG_MIN`, and the values whose `real_size` is
             exactly 0 or exactly 8. This is the parameter the defect switches
             on and it is what `inputs/` structurally cannot span, because a
             benign corpus may not contain a truncating window at all;
          b. every `ctl` in 0..3, so the `zremote` and transport-failure arms
             are driven in every combination;
          c. `navail` at 0, 1, 31, 32, 33 and `n_pay` -- 32 being where
             `remote_len = n % 32` returns to zero, which is the `:329` arm;
          d. five strides, including the smallest the driver admits (16);
          e. `to_read` straddling the size-class cache boundary, `real_size`
             86 / 88, which is the `_efree` branch."""
        def w(stride, to_read, ctl, navail, fill=0xA5):
            n_pay = stride - HEAD
            navail = min(navail, n_pay)
            body = bytes(((fill + 7 * i) & 0xFF) for i in range(n_pay))
            return (((to_read & MASK).to_bytes(8, "little"))
                    + bytes((ctl & 0xFF, (ctl >> 8) & 0xFF,
                             navail & 0xFF, (navail >> 8) & 0xFF))
                    + body)

        trs = [0, 1, -1, 2, -2, 7, 8, 86, 87, 88,
               (1 << 31) - 1, 1 << 31, (1 << 32) - 2, (1 << 32) - 1, 1 << 32,
               (1 << 33) - 1, (1 << 63) - 1, -(1 << 63),
               -4294967297, -4294967296, -8, -9,
               (1 << 32) - 9, (1 << 32) - 8]
        for tr in trs:
            for ctl in range(4):
                yield (f"to_read={tr} ctl={ctl}", w(64, tr, ctl, 20))
        for navail in (0, 1, 31, 32, 33, 52):
            for tr in (0, 1, 16, 31, 32, 64, -1, (1 << 32) - 1):
                yield (f"navail={navail} to_read={tr}", w(64, tr, 1, navail))
        for stride in (16, 17, 20, 45, 550):
            for tr in (1, 5, 100, -1, (1 << 32) - 1):
                yield (f"stride={stride} to_read={tr}",
                       w(stride, tr, 0, stride - HEAD))
        for tr in (78, 79, 80, 86, 87, 88, 200):
            yield (f"cache-boundary to_read={tr}", w(64, tr, 3, 40))

    def selfcheck(self):
        """Six checks, five of them about this row specifically.

        1a. the imperative simulation against the recursive `recv_fold`, on the
            calls this input actually makes;
        1b. ⚠⚠ the same two implementations on **synthetic windows this file
            builds**, spanning every truncation boundary, every `ctl`, both
            sides of the size-class cache and five strides.
            `PROTOCOL_PHP.md` §A2a rule 2 -- 1a alone is what let ph03 ship a
            model that computed a different function from its own proof;
        2.  ⚠⚠ **THE ARM TABLE, OVER THE CALLS THE DRIVER ACTUALLY MAKES.**
            `inputs/gen.py::_check_span` asserts the same table over EVERY
            window in the file, which is a superset condition: the driver picks
            windows from a checksum-derived index and need not visit them all.
            This is the sharper half and the one that is true of the
            measurement;
        3.  ⚠ every window's result is reproduced by a THIRD, deliberately dumb
            spelling that materialises the destination buffer;
        4.  no window of a NON-adversarial input makes `445daac3ab1a`'s guard
            fire OR truncates the allocation. That is what "benign" means here
            and it is what `check.py` stage 7h requires of R1h;
        5.  the constant this row turns on -- `PH29_HEAD` -- still equals what
            `c/kernel.c` compiles against. This file writes it as a Python
            integer and the C gets it from a `#define`; check 5 parses the C
            and compares, so the two cannot drift apart in this file's head.
        """
        problems = []
        for c in self.sample_calls(8):
            want = self.recv_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != recv_fold() {want} "
                    f"at off={c['off']}")
                break
        for label, win in self._synthetic_windows():
            sim, helper = self._both(win)
            if sim != helper:
                problems.append(
                    f"synthetic window [{label}]: simulated {sim} != "
                    f"recv_fold() {helper}. The two implementations have come "
                    f"apart OFF the corpus; inputs/ cannot see this and it is "
                    f"why this sweep exists (PROTOCOL_PHP.md A2a rule 2)")
                break
            dumb = Model._dumb(win)
            if dumb != sim:
                problems.append(
                    f"synthetic window [{label}]: simulated {sim} != third "
                    f"spelling {dumb}")
                break

        adversarial = os.path.basename(self.path).startswith("adversarial")
        if not adversarial and self.entered:
            problems += self._arm_table()

        for k in range(self.nwin):
            got = self._win[k][0]
            want = self._dumb(self.buf[k * self.stride:(k + 1) * self.stride])
            if got != want:
                problems.append(f"window {k}: {got} != third spelling {want}")
                break

        if not adversarial:
            for k in range(self.nwin):
                win = self.buf[k * self.stride:(k + 1) * self.stride]
                to_read = self._unpack(win)[0]
                size = (to_read + 1) & MASK
                if to_read <= 0:
                    problems.append(
                        f"window {k}: to_read = {to_read} <= 0, so "
                        f"445daac3ab1a's guard FIRES. ../spec.md pins it dead "
                        f"on the measured corpus, because check.py stage 7h "
                        f"requires R1h == R1 on every non-adversarial input")
                    break
                if real_size_of(size) != ((size + 7) & ~7):
                    problems.append(
                        f"window {k}: to_read = {to_read} truncates at "
                        f"zend_alloc.c:135, which is an out-of-bounds write "
                        f"and must not be in a file the gate calls benign")
                    break
                if self._win[k][1] > 0:
                    problems.append(
                        f"window {k}: R1 writes {self._win[k][1]} byte(s) past "
                        f"the block")
                    break

        chead = _c_constants()
        if chead != HEAD:
            problems.append(
                f"c/kernel.c compiles against PH29_HEAD={chead}, this model "
                f"uses {HEAD}; every offset in this row means something else")
        return problems

    def _arm_table(self):
        """`PROTOCOL_PHP.md` §A2a rule 1, over the VISITED calls."""
        cached = uncached = False
        recv_ok = recv_fail = False
        zrem = no_zrem = False
        is_str = not_str = False
        clamp_hit = clamp_miss = False
        navail_zero = navail_full = False
        seen = set()
        for c in self.iter_calls():
            if c["off"] in seen:
                continue
            seen.add(c["off"])
            win = self.buf[c["off"]:c["off"] + c["len"]]
            to_read, ctl, want, navail, n_pay = self._unpack(win)
            rs = real_size_of((to_read + 1) & MASK)
            if rs <= CACHE_MAX_REAL:
                cached = True
            else:
                uncached = True
            if ctl & 1:
                zrem = True
            else:
                no_zrem = True
            if ctl & 2:
                recv_fail = True
                continue
            recv_ok = True
            n = min(navail, to_read & MASK, rs)
            if to_read < navail:
                clamp_hit = True
            else:
                clamp_miss = True
            if navail == 0:
                navail_zero = True
            if navail == n_pay:
                navail_full = True
            if ctl & 1:
                if (n % 32) != 0:
                    is_str = True
                else:
                    not_str = True
        bad = []
        if not (cached and uncached):
            bad.append(f"the VISITED calls do not straddle the size-class cache "
                       f"(real_size <= {CACHE_MAX_REAL}: {cached}, above: "
                       f"{uncached}) -- zend_alloc.c:270-279 takes one arm only")
        if not (recv_ok and recv_fail):
            bad.append(f"`if (recvd >= 0)` at :328 takes only one arm on a "
                       f"VISITED call (ok: {recv_ok}, fail: {recv_fail})")
        if not (zrem and no_zrem):
            bad.append(f"`if (zremote)` at :315 takes only one arm on a VISITED "
                       f"call (passed: {zrem}, absent: {no_zrem})")
        if not (is_str and not_str):
            bad.append(f"`if (zremote && Z_STRLEN_P(zremote))` at :329 takes "
                       f"only one arm on a VISITED call (non-zero: {is_str}, "
                       f"zero: {not_str})")
        if not (clamp_hit and clamp_miss):
            bad.append(f"the transport's clamp at transports.c:406-407 takes "
                       f"only one arm on a VISITED call (to_read < navail: "
                       f"{clamp_hit}, to_read >= navail: {clamp_miss})")
        if not (navail_zero and navail_full):
            bad.append(f"navail does not reach both ends on a VISITED call "
                       f"(0: {navail_zero}, n_pay: {navail_full})")
        return [f"visited-call arm coverage: {b}" for b in bad]


def _c_constants():
    """`PH29_HEAD` as `c/kernel.c` literally pins it. Parsed rather than
    trusted: check 5."""
    import re
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c", "kernel.c")
    txt = open(p).read()
    m = re.search(r"#define\s+PH29_HEAD\s+(\d+)", txt)
    return int(m.group(1)) if m else None


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):28s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
