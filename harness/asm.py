#!/usr/bin/env python3
"""Kernel assembly: extraction, normalisation, counting, digests, diffing.

This module is the *only* place in the repo that runs objdump. Everything else
calls it. `.memory/03-measurement.md` records what happened the last time there
were two pipelines: they disagreed, one of them could not have produced the
published numbers, and three separate defects hid in the gap.

The two things to understand before using this:

1. **The identity oracle is `md5_raw` -- the machine-code bytes.** Not
   `md5_norm`. Normalisation erases every immediate, displacement and branch
   target, so two kernels that compute *different answers* can normalise
   identically; TASK_001_REVIEW built such a pair. Normalised text exists so a
   human can read a diff. Any "R5 is R4" claim must cite `md5_raw`.

   `md5_raw_norel` is the fallback when, and only when, the two binaries lay the
   kernel out at different addresses: it is `md5_raw` with pc-relative
   displacement *fields* zeroed, so a `call rel32` to a callee that moved stops
   mattering while every immediate and register field still does. At `-O0` the
   Rust kernels still call `Iterator::next`, so `md5_raw` differs there for link
   reasons alone -- report both, and say which one you are quoting.

2. **Report `n_raw` and `n_nopad` together.** The instruction range objdump
   attributes to a symbol includes LLVM's `int3` tail padding and alignment
   `nop`s. Counting them overstates the safe-vs-unsafe gap (pilot: 57 vs 37 raw,
   46 vs 33 real). And a static count without a paired dynamic `Ir` is not a
   cost model at all -- gcc's 32-instruction pilot kernel executed 43% *more*
   than LLVM's 37-instruction one.

Two normalisation hazards from `.memory/03-measurement.md`, both fixed here:
  * the old width-based `s/\\b[0-9a-f]{4,}\\b//g` ate the `fadd` mnemonic. Gone;
    there is no width-based strip.
  * bare-hex branch targets under 4 digits survived. The strip is now
    *positional*: the operand of a branch or call, whatever its width.

CLI:
    harness/asm.py show <binary> [--sym kernel] [--raw]
    harness/asm.py stat <binary> [--sym kernel] [--json]
    harness/asm.py diff <binary-a> <binary-b> [--sym kernel]
    harness/asm.py selftest            # reproduces the pilot numbers
"""

import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys

OBJDUMP = os.environ.get("SLB_OBJDUMP", "objdump")

# Instructions that are padding, not work: LLVM's int3 traps between functions,
# and every spelling of nop that gas/objdump emits for alignment.
# `ud2` is deliberately NOT here: it is emitted code (the tail of an
# unreachable/panic path), not alignment, and excluding it would understate the
# safe rungs.
_PAD_MNEMONICS = {
    "int3", "nop", "nopw", "nopl", "nopq", "nopb",
}
# Prefixes objdump prints as a separate leading token.
_PREFIXES = {"cs", "ds", "es", "fs", "gs", "ss", "data16", "rex.W", "rex"}

# Positional branch-target strip: these take a code address as their (single)
# operand when that operand is a bare hex literal.
_BRANCH_RE = re.compile(r"^(j[a-z]+|call|callq|loop|loope|loopne|loopz|loopnz|xbegin|bnd)$")

_INSN_RE = re.compile(r"^\s*([0-9a-f]+):\t([0-9a-f ]+?)\s*(?:\t(.*))?$")
_SYMHDR_RE = re.compile(r"^([0-9a-f]+)\s+<(.+)>:$")


class Insn:
    __slots__ = ("addr", "raw", "text")

    def __init__(self, addr, raw, text):
        self.addr = addr          # int
        self.raw = raw            # bytes
        self.text = text          # str, objdump's rendering, addresses intact

    @property
    def mnemonic(self):
        toks = self.text.split()
        i = 0
        while i < len(toks) and toks[i] in _PREFIXES:
            i += 1
        return toks[i] if i < len(toks) else ""

    @property
    def is_padding(self):
        if self.mnemonic in _PAD_MNEMONICS:
            return True
        # 66 90 / 87 c0 style two-byte nops render as `xchg %ax,%ax`. objdump
        # pads mnemonics with spaces, so compare on collapsed whitespace.
        flat = " ".join(self.text.split("#")[0].split())
        return flat in ("xchg %ax,%ax", "xchg %eax,%eax")

    def __repr__(self):
        return f"Insn(0x{self.addr:x}, {self.raw.hex()}, {self.text!r})"


class Kernel:
    """One symbol's disassembly, plus everything derived from it."""

    def __init__(self, binary, symbol, insns):
        self.binary = binary
        self.symbol = symbol
        self.insns = insns

    # ---- counts -------------------------------------------------------------
    @property
    def n_raw(self):
        """Every instruction objdump attributes to the symbol, padding included.
        This is the number the pilot published; it overstates the gap."""
        return len(self.insns)

    @property
    def n_nopad(self):
        """Instructions that are actually work. Quote this one, or say which."""
        return sum(1 for i in self.insns if not i.is_padding)

    @property
    def n_bytes(self):
        return sum(len(i.raw) for i in self.insns)

    # ---- bytes: the identity oracle ----------------------------------------
    @property
    def raw_bytes(self):
        return b"".join(i.raw for i in self.insns)

    @property
    def md5_raw(self):
        """Bit-exact machine code. The strongest oracle, and the right one when
        the two binaries you are comparing lay the kernel out identically."""
        return hashlib.md5(self.raw_bytes).hexdigest()

    @property
    def _reloc(self):
        out, n = [], 0
        for i in self.insns:
            b, k = _mask_pcrel(i)
            out.append(b)
            n += k
        return b"".join(out), n

    @property
    def raw_bytes_norel(self):
        """Machine code with pc-relative *displacement fields only* zeroed.

        Needed because two binaries that contain the same kernel can still
        differ byte-for-byte when the kernel calls out: a `call rel32` encodes
        the distance to the callee, and a one-character difference in a crate
        name shifts every symbol. That bit at `-O0`, where the Rust kernel still
        calls `Iterator::next`, and it is a link-layout artefact, not a codegen
        difference.

        This is still an oracle over machine-code bytes, not over text: every
        immediate, every non-pc-relative displacement, every opcode and every
        register field survives. The `0x1234`-vs-`0x5678` collision that broke
        the normalised-text digest (`.memory/03-measurement.md`) is caught here.
        Quote `md5_raw` when it matches; quote this one, and say so, when it
        does not."""
        return self._reloc[0]

    @property
    def md5_raw_norel(self):
        return hashlib.md5(self.raw_bytes_norel).hexdigest()

    @property
    def n_reloc_masked(self):
        return self._reloc[1]

    # ---- normalised text: for reading, never for identity -------------------
    @property
    def normalised(self):
        return [normalise_text(i.text) for i in self.insns]

    @property
    def md5_norm(self):
        return hashlib.md5(("\n".join(self.normalised) + "\n").encode()).hexdigest()

    # ---- shape --------------------------------------------------------------
    @property
    def backward_branches(self):
        """Branches whose bare-hex target is an earlier address inside this
        symbol -- i.e. loops. A kernel that got constant-folded has none."""
        lo = self.insns[0].addr if self.insns else 0
        out = []
        for i in self.insns:
            if not _BRANCH_RE.match(i.mnemonic):
                continue
            tgt = _branch_target(i.text)
            if tgt is not None and lo <= tgt <= i.addr:
                out.append((i.addr, tgt, i.text))
        return out

    @property
    def has_loop(self):
        return bool(self.backward_branches)

    @property
    def vector_regs(self):
        found = set()
        for i in self.insns:
            for m in re.finditer(r"%(x|y|z)mm\d+", i.text):
                found.add(m.group(1) + "mm")
        return sorted(found)

    def summary(self):
        return {
            "binary": self.binary,
            "symbol": self.symbol,
            "n_raw": self.n_raw,
            "n_nopad": self.n_nopad,
            "n_bytes": self.n_bytes,
            "md5_raw": self.md5_raw,
            "md5_raw_norel": self.md5_raw_norel,
            "n_reloc_masked": self.n_reloc_masked,
            "md5_norm": self.md5_norm,
            "has_loop": self.has_loop,
            "n_backward_branches": len(self.backward_branches),
            "vector_regs": self.vector_regs,
        }


# --------------------------------------------------------------------------
# normalisation
# --------------------------------------------------------------------------

def _branch_target(text):
    """Bare-hex operand of a branch/call, or None. Positional: an indirect
    `jmp *%rax` has no bare-hex operand and is left alone."""
    parts = text.split()
    i = 0
    while i < len(parts) and parts[i] in _PREFIXES:
        i += 1
    if i >= len(parts) or not _BRANCH_RE.match(parts[i]):
        return None
    if i + 1 >= len(parts):
        return None
    op = parts[i + 1]
    if re.fullmatch(r"[0-9a-f]+", op):
        return int(op, 16)
    return None


_RIPREL_RE = re.compile(r"#\s*([0-9a-f]+)\b")


def _mask_pcrel(insn):
    """Zero the pc-relative displacement field(s) of one instruction.

    The field's *value* is known -- objdump already decoded the target -- so it
    is recovered as `target - end_of_instruction` and located in the encoding by
    searching for its little-endian form. Branch displacements are the last
    field, so they are found from the right; a rip-relative displacement
    precedes any immediate, so it is found from the left. If the field cannot be
    located the instruction is left alone and the count reflects that.

    Returns (bytes, n_fields_masked)."""
    raw = bytearray(insn.raw)
    end = insn.addr + len(raw)
    n = 0

    def zero(value, from_right):
        nonlocal n
        for width in (4, 2, 1):
            try:
                b = value.to_bytes(width, "little", signed=True)
            except OverflowError:
                continue
            idx = raw.rfind(b) if from_right else raw.find(b)
            if idx > 0:  # never index 0: that would be the opcode
                raw[idx:idx + width] = b"\x00" * width
                n += 1
                return True
        return False

    t = _branch_target(insn.text)
    if t is not None:
        zero(t - end, from_right=True)
    m = _RIPREL_RE.search(insn.text)
    if m and "%rip" in insn.text:
        zero(int(m.group(1), 16) - end, from_right=False)
    return bytes(raw), n


def normalise_text(text):
    """Canonical normalisation. Strips link-dependent detail so two builds of
    the same source diff cleanly. Emphatically NOT an identity oracle."""
    s = text
    s = re.sub(r"\s+#.*$", "", s)          # rip-relative annotations
    s = re.sub(r"<[^>]*>", "", s)          # symbol names and +0x.. offsets
    # positional: branch/call target -> placeholder, before the 0x strip so an
    # indirect target keeps its shape.
    parts = s.split()
    i = 0
    while i < len(parts) and parts[i] in _PREFIXES:
        i += 1
    if i < len(parts) and _BRANCH_RE.match(parts[i]) and i + 1 < len(parts):
        if re.fullmatch(r"[0-9a-f]+", parts[i + 1]):
            parts[i + 1] = "TGT"
            s = " ".join(parts)
    s = re.sub(r"0x[0-9a-f]+", "", s)      # immediates and displacements
    # NOTE: deliberately no width-based bare-hex strip here. The old
    # s/\b[0-9a-f]{4,}\b//g ate `fadd`.
    s = re.sub(r"\s+", " ", s).strip()
    return s


# --------------------------------------------------------------------------
# extraction
# --------------------------------------------------------------------------

def _objdump(binary):
    r = subprocess.run(
        [OBJDUMP, "-d", "--no-show-raw-insn=false", binary],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        # older binutils reject --no-show-raw-insn=false; raw bytes are the default
        r = subprocess.run([OBJDUMP, "-d", binary], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"objdump failed on {binary}: {r.stderr.strip()}")
    return r.stdout


def symbols(binary):
    """All disassembled symbols: {name: [Insn, ...]}, in file order.

    Boundaries come from objdump's own symbol grouping, which is what the pilot
    numbers were derived from. The `<addr> <sym>:` header line is NOT an
    instruction -- keeping it is defect 1 in `.memory/03-measurement.md` and made
    every published count exactly one too high."""
    out = {}
    cur = None
    pending = None  # (addr, raw_hex_parts, text) awaiting continuation lines
    for line in _objdump(binary).splitlines():
        m = _SYMHDR_RE.match(line.strip())
        if m:
            cur = m.group(2)
            out.setdefault(cur, [])
            pending = None
            continue
        if cur is None:
            continue
        if not line.strip():
            cur = None
            pending = None
            continue
        m = _INSN_RE.match(line)
        if not m:
            continue
        addr, raw_hex, text = int(m.group(1), 16), m.group(2), m.group(3)
        raw = bytes(int(b, 16) for b in raw_hex.split())
        if text is None:
            # continuation line: more machine-code bytes for the previous insn
            if pending is not None:
                pending.raw += raw
            continue
        pending = Insn(addr, bytearray(raw), text.strip())
        out[cur].append(pending)
    # freeze bytearrays
    for name, insns in out.items():
        for i in insns:
            i.raw = bytes(i.raw)
    return out


def find_symbol(binary, needle="kernel", pick="largest"):
    """Rust symbols are v0-mangled (`_RNvCs..._6kernel`), so match on substring,
    never an exact name. `pick`: 'largest' (most instructions -- the right choice
    for `main`, where the C runtime shim also matches) or 'only' (error if the
    substring is ambiguous)."""
    syms = symbols(binary)
    hits = {k: v for k, v in syms.items() if needle in k and v}
    if not hits:
        raise KeyError(f"{binary}: no symbol containing {needle!r} "
                       f"(have {len(syms)} symbols)")
    if len(hits) > 1 and pick == "only":
        raise KeyError(f"{binary}: {needle!r} is ambiguous: {sorted(hits)}")
    name = max(hits, key=lambda k: len(hits[k]))
    return name, hits[name]


def kernel(binary, needle="kernel", pick="largest"):
    name, insns = find_symbol(binary, needle, pick)
    return Kernel(binary, name, insns)


def try_kernel(binary, needle="kernel", pick="largest"):
    """Like kernel() but returns None when the symbol is gone -- which is the
    expected outcome in `whole` builds, where the kernel is inlined away."""
    try:
        return kernel(binary, needle, pick)
    except KeyError:
        return None


def text_size(binary):
    """Bytes of .text in the whole binary."""
    r = subprocess.run(["readelf", "-S", "-W", binary], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        parts = line.replace("[", " ").replace("]", " ").split()
        if len(parts) > 6 and parts[1] == ".text" and parts[2] == "PROGBITS":
            return int(parts[5], 16)
    return None


# --------------------------------------------------------------------------
# diffing
# --------------------------------------------------------------------------

def diff(a, b, needle="kernel"):
    """Compare two binaries' kernels. Returns (same_bytes, same_norel, diff_text)
    where the diff is of the *normalised text* -- for reading only."""
    ka, kb = kernel(a, needle), kernel(b, needle)
    d = "\n".join(difflib.unified_diff(
        ka.normalised, kb.normalised,
        fromfile=f"{os.path.basename(a)}:{ka.symbol}",
        tofile=f"{os.path.basename(b)}:{kb.symbol}",
        lineterm="",
    ))
    return ka.md5_raw == kb.md5_raw, ka.md5_raw_norel == kb.md5_raw_norel, d


# --------------------------------------------------------------------------
# selftest -- the pilot binaries in .temp/build/docrepro are the fixture
# --------------------------------------------------------------------------

_SELFTEST = [
    # binary, needle, n_raw, n_nopad   (from .memory/01-ladder.md + 03-measurement.md)
    ("k_gcc", "kernel", 32, 30),
    ("k_clang", "kernel", 33, 31),
    ("k_rust", "kernel", 57, 46),
    ("k_verus", "kernel", 57, 46),
    ("k_unsafe", "kernel", 37, 33),
    ("k_unsafe_verus", "kernel", 37, 33),
]
_SELFTEST_PAIRS = [("k_rust", "k_verus"), ("k_unsafe", "k_unsafe_verus")]


def selftest(root=None):
    """Reproduce the numbers `.memory/` records for the pilot. If this fails,
    either the extraction changed or the memory file is wrong -- do not paper
    over it."""
    root = root or os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), ".temp", "build", "docrepro")
    if not os.path.isdir(root):
        print(f"selftest: fixture dir missing: {root}", file=sys.stderr)
        return 77
    bad = 0
    for name, needle, want_raw, want_nopad in _SELFTEST:
        p = os.path.join(root, name)
        if not os.path.exists(p):
            print(f"  MISSING {p}")
            bad += 1
            continue
        k = kernel(p, needle)
        ok = (k.n_raw, k.n_nopad) == (want_raw, want_nopad)
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {name:16s} raw={k.n_raw:3d} (want {want_raw:3d})  "
              f"nopad={k.n_nopad:3d} (want {want_nopad:3d})  md5_raw={k.md5_raw[:8]}")
    for a, b in _SELFTEST_PAIRS:
        pa, pb = os.path.join(root, a), os.path.join(root, b)
        if not (os.path.exists(pa) and os.path.exists(pb)):
            continue
        same, norel, _ = diff(pa, pb)
        bad += 0 if same else 1
        print(f"  {'ok  ' if same else 'FAIL'} {a} == {b} by raw bytes: {same} "
              f"(reloc-masked: {norel})")
    print("selftest:", "PASS" if bad == 0 else f"FAIL ({bad})")
    return 0 if bad == 0 else 1


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("show", help="print the kernel's normalised asm")
    p.add_argument("binary")
    p.add_argument("--sym", default="kernel")
    p.add_argument("--raw", action="store_true", help="objdump text, not normalised")

    p = sub.add_parser("stat", help="counts and digests")
    p.add_argument("binary")
    p.add_argument("--sym", default="kernel")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("diff", help="diff two binaries' kernels")
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("--sym", default="kernel")

    p = sub.add_parser("syms", help="list disassembled symbols and sizes")
    p.add_argument("binary")

    sub.add_parser("selftest", help="reproduce the pilot numbers from .memory/")

    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "syms":
        for k, v in symbols(a.binary).items():
            print(f"{len(v):6d}  {k}")
        return 0
    if a.cmd == "diff":
        same, norel, d = diff(a.a, a.b, a.sym)
        print(f"identical by raw machine-code bytes      : {same}")
        print(f"identical with pc-rel fields masked      : {norel}")
        if d:
            print(d)
        else:
            print("(normalised text identical)")
        return 0 if norel else 1
    k = kernel(a.binary, a.sym)
    if a.cmd == "stat":
        s = k.summary()
        if a.json:
            print(json.dumps(s, indent=2))
        else:
            for kk, vv in s.items():
                print(f"{kk:22s} {vv}")
        return 0
    for i, n in zip(k.insns, k.normalised):
        print(i.text if a.raw else n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
