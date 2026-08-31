#!/usr/bin/env python3
"""p25 CONTROLS: **WHICH growth relocates, under the SHIPPED driver?**

    python3 patterns/p25-realloc-growth/controls/reloc_probe.py

⚠⚠ **THIS IS THE CONTROL THAT `TASK_134` NEEDED AND DID NOT HAVE.** That task
refused p25 on `moved = 0/12`, measured with a hand-rolled driver in which the
token vector was the newest allocation, so glibc extended it in place. **That is
a fact about a heap topology, not a fact about C**, and the only way to keep the
distinction honest is to measure the relocation under the driver the pattern
actually ships.

So: `../c/kernel.c`, `../c/main.c` and `common/driver.c` are compiled
**unmodified**, with `-Drealloc=slb_p25_probe_realloc` on the command line, and
`probe_realloc.c` -- compiled WITHOUT that define -- supplies the name and
records every event. Nothing about the program changes; only the name of the
function the kernel calls.

WHAT IT REPORTS, per shipped input, at gcc `-O1` and clang `-O1`
----------------------------------------------------------------
one row per `realloc` call: the requested size, and whether the block MOVED.

⚠ **The claim `../c/kernel.h` and `../spec.md` make is narrow and this is what
checks it:** *the harm window is ONE GROWTH wide.* glibc's minimum chunk gives a
4-byte `malloc` 24 usable bytes, so `4 -> 8` and `8 -> 16` are satisfied in
place; it is `16 -> 32` that has to move, and only because the string vector was
allocated after the token vector and is still live.

WHAT IT ASSERTS
---------------
  * on `adversarial-move`, the token vector's `16 -> 32` growth MOVES;
  * on `adversarial-nogrow`, **no** `realloc` moves at all -- that is the
    negative control, and it is what stops "relocation" from being an artefact
    of running the probe;
  * the two compilers agree, because relocation is an allocator fact and not a
    codegen one. ⚠ If they ever stop agreeing, that is a finding and this
    control is where it surfaces.

⚠ The input is a ONE-ITERATION copy of the shipped blob, written into `.temp/`
by this script: the payload is byte-identical and only the `n_iters` header word
is rewritten, so what is probed is the shipped window and not a re-derived one.
"""

import glob
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
COMMON = os.path.join(REPO, "common")
CDIR = os.path.join(PDIR, "c")
INDIR = os.path.join(PDIR, "inputs")
TMP = os.path.join(REPO, ".temp", "p25ctl")

GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")
CLANG = os.environ.get("SLB_CLANG", os.path.expanduser("~/tools/llvm/bin/clang"))

PROBED = ["adversarial-move.bin", "adversarial-lateread.bin",
          "adversarial-many.bin", "adversarial-nogrow.bin", "small.bin"]

_EV = re.compile(r"^P25REALLOC (\d+) old=(\S+) new=(\S+) size=(\d+) moved=(\d)$")


def build(cc, tag):
    out = os.path.join(TMP, f"reloc_{tag}")
    cmd = [cc, "-std=c99", "-O1", "-I", COMMON, "-I", CDIR,
           "-Drealloc=slb_p25_probe_realloc",
           "-o", out,
           os.path.join(CDIR, "kernel.c"), os.path.join(CDIR, "main.c"),
           os.path.join(COMMON, "driver.c")]
    # The interposer is compiled SEPARATELY, without the define, so that the
    # `realloc` inside it is the real one.
    obj = os.path.join(TMP, f"probe_{tag}.o")
    r = subprocess.run([cc, "-std=c99", "-O1", "-c", "-o", obj,
                        os.path.join(HERE, "probe_realloc.c")],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise SystemExit(f"reloc_probe.py: probe_realloc.c failed:\n{r.stderr}")
    r = subprocess.run(cmd + [obj], capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise SystemExit(f"reloc_probe.py: build failed ({tag}):\n{r.stderr}")
    return out


def one_iter_copy(name):
    """The shipped blob with `n_iters` rewritten to 1 and the payload untouched."""
    src = os.path.join(INDIR, name)
    blob = open(src, "rb").read()
    n_iters, decl = struct.unpack("<QQ", blob[:16])
    dst = os.path.join(TMP, "one_" + name)
    with open(dst, "wb") as f:
        f.write(struct.pack("<QQ", 1, decl))
        f.write(blob[16:])
    return dst, n_iters


def run(binary, blob):
    env = dict(os.environ)
    env.pop("LD_PRELOAD", None)
    r = subprocess.run([binary, blob], capture_output=True, text=True,
                       timeout=600, env=env)
    events = []
    for ln in r.stderr.splitlines():
        m = _EV.match(ln.strip())
        if m:
            events.append({"n": int(m.group(1)), "size": int(m.group(4)),
                           "moved": m.group(5) == "1"})
    return events, r.stdout.strip()


def derived_from():
    out = {}
    for rel in ("patterns/p25-realloc-growth/c/kernel.c",
                "patterns/p25-realloc-growth/c/main.c",
                "patterns/p25-realloc-growth/controls/probe_realloc.c",
                "patterns/p25-realloc-growth/controls/reloc_probe.py",
                "patterns/p25-realloc-growth/inputs/gen.py",
                "common/driver.c"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    os.makedirs(TMP, exist_ok=True)
    missing = [n for n in PROBED if not os.path.exists(os.path.join(INDIR, n))]
    if missing:
        print(f"reloc_probe.py: missing input(s) {missing} -- run inputs/gen.py",
              file=sys.stderr)
        return 1

    bins = {"gcc": build(GCC, "gcc")}
    if os.path.exists(CLANG):
        bins["clang"] = build(CLANG, "clang")
    else:
        print(f"  NOTE: {CLANG} not found; this run measures gcc only")

    table, problems = {}, []
    for name in PROBED:
        blob, orig_iters = one_iter_copy(name)
        for cc, b in bins.items():
            events, out = run(b, blob)
            key = f"{name}/{cc}"
            table[key] = events
            moved = [e for e in events if e["moved"]]
            sizes = [e["size"] for e in events]
            print(f"  {name:26s} {cc:6s} n_iters {orig_iters}->1  "
                  f"{len(events)} realloc(s), sizes {sizes}, "
                  f"MOVED at size(s) {[e['size'] for e in moved] or '[]'}  "
                  f"stdout={out}")

    def moved_sizes(name, cc):
        return sorted(e["size"] for e in table.get(f"{name}/{cc}", [])
                      if e["moved"])

    for cc in bins:
        m = moved_sizes("adversarial-move.bin", cc)
        if 32 not in m:
            problems.append(
                f"adversarial-move/{cc}: the token vector's 16 -> 32 growth did "
                f"NOT relocate (moved at {m}). The adversarial window is tuned "
                f"to that growth, so if it stops moving the row's harm is not "
                f"being exercised -- and it is a heap-topology change, not a "
                f"source change")
        n = moved_sizes("adversarial-nogrow.bin", cc)
        if n:
            problems.append(
                f"adversarial-nogrow/{cc}: something relocated (at {n}), and "
                f"this is the NEGATIVE control -- its whole point is that the "
                f"pushes after the SAVE stay inside the current capacity")
    if len(bins) == 2:
        for name in PROBED:
            g, c = moved_sizes(name, "gcc"), moved_sizes(name, "clang")
            if g != c:
                problems.append(
                    f"{name}: gcc moved at {g} and clang at {c}. Relocation is "
                    f"an ALLOCATOR fact and the two compilers are supposed to "
                    f"agree; a disagreement is a finding")

    doc = {"pin": {"regenerate": "python3 patterns/p25-realloc-growth/controls/"
                                 "reloc_probe.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "compilers": sorted(bins),
           "events": table,
           "problems": problems,
           "invariant": "Under the SHIPPED driver and the SHIPPED kernel, the "
                        "token vector's 16 -> 32 growth RELOCATES on "
                        "adversarial-move (both compilers), NOTHING relocates "
                        "on adversarial-nogrow, and the two compilers agree -- "
                        "because relocation is an allocator fact, not a codegen "
                        "one. This is the measurement TASK_134's `moved = 0/12` "
                        "lacked: that number was taken under a different driver."}
    out = os.path.join(HERE, "reloc_probe.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    for f in glob.glob(os.path.join(TMP, "reloc_*")) + \
            glob.glob(os.path.join(TMP, "probe_*.o")) + \
            glob.glob(os.path.join(TMP, "one_*.bin")):
        os.unlink(f)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
