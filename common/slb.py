"""sec-ladder benchmark input format: read and write.

The format is fixed for every pattern (`.memory/02-bench-rules.md`), little-endian:

    offset 0   u64  n_iters      # times the driver calls the kernel
    offset 8   u64  payload_len  # bytes following
    offset 16  u8[payload_len]   # pattern-defined payload

`payload_len` is a *declared* length. A well-formed file has exactly that many
bytes after the header; an adversarial file may declare more than it carries, and
the drivers are required to notice. So the reader here keeps the declared length
and the bytes actually present as separate facts and never conflates them.

Stdlib only, no dependencies: `inputs/gen.py` and `harness/check.py` both use it.
"""

import struct

HEADER_FMT = "<QQ"
HEADER_LEN = struct.calcsize(HEADER_FMT)  # 16


class SlbFile:
    """One parsed input file.

    n_iters       — the driver's outer loop bound, as declared.
    declared_len  — the `payload_len` header field, verbatim.
    payload       — the bytes actually present after the header.
    truncated     — declared_len > len(payload); a conforming driver must exit
                    non-zero rather than read past the end.
    """

    def __init__(self, n_iters, declared_len, payload):
        self.n_iters = n_iters
        self.declared_len = declared_len
        self.payload = payload

    @property
    def truncated(self):
        return self.declared_len > len(self.payload)

    def __repr__(self):
        return (
            f"SlbFile(n_iters={self.n_iters}, declared_len={self.declared_len}, "
            f"present={len(self.payload)}, truncated={self.truncated})"
        )


def write(path, n_iters, payload, declared_len=None):
    """Write an input file.

    `declared_len` defaults to len(payload); pass a larger value to build the
    "length field bigger than the payload" adversarial case.
    """
    if declared_len is None:
        declared_len = len(payload)
    with open(path, "wb") as f:
        f.write(struct.pack(HEADER_FMT, n_iters, declared_len))
        f.write(payload)


def read(path):
    """Parse an input file. Raises ValueError only if the 16-byte header is
    itself incomplete — every other malformation is reported through SlbFile so
    the caller can compare it against what the drivers did."""
    with open(path, "rb") as f:
        blob = f.read()
    if len(blob) < HEADER_LEN:
        raise ValueError(f"{path}: short header ({len(blob)} bytes, need {HEADER_LEN})")
    n_iters, declared_len = struct.unpack(HEADER_FMT, blob[:HEADER_LEN])
    return SlbFile(n_iters, declared_len, blob[HEADER_LEN:])


def u64s(payload):
    """Decode a byte payload as little-endian u64s, ignoring a trailing partial
    word. Mirrors `slb_u64s` in common/driver.c and `le_u64s` in
    common/driver.rs — keep the three in step."""
    n = len(payload) // 8
    return list(struct.unpack("<%dQ" % n, payload[: 8 * n]))


def head_u64_body(payload):
    """Split a payload into (head word, remaining words).

    Mirrors `slb_head_u64_body` (C) and `driver::head_u64_body` (Rust). Patterns
    whose payload is "one header word, then a u64 array" use this shape; p01 is
    the first. An empty payload yields (0, []).
    """
    w = u64s(payload)
    if not w:
        return 0, []
    return w[0], w[1:]


def pack_head_body(head, body):
    """Inverse of head_u64_body: build a payload from a head word and a list."""
    return struct.pack("<%dQ" % (1 + len(body)), head, *body)
