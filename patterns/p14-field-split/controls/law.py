#!/usr/bin/env python3
"""p14's ZERO-PARAMETER laws, DERIVED FROM THE LISTING and checked against the
sweep -- not fitted to it.

`.memory/03-measurement.md`: *"A five-decimal rate must come from the
DISASSEMBLY (`body_len / K`), never from a marginal"*, and trap 3's dynamic half:
*"before naming a per-iteration `Ir` law after a mechanism, disassemble and
attribute it mnemonic by mnemonic."* Everything below is read off
`objdump -d` of the shipped `-O3 isolated` kernels and then **predicted forward**
onto blobs the derivation never saw.

    python3 patterns/p14-field-split/controls/law.py .temp/p14/sweep_all.json

THE FOLD, R4 (`unsafe.rs` / `verus.rs`), read off the listing
-------------------------------------------------------------
The inner byte loop is **4x unrolled with a scalar epilogue of `L mod 4`**:

    per field, before the inner loop      `test;je`                        2
    if L > 0                              `mov;and;cmp;jae`               +4
    if L >= 4  enter the unrolled form    `mov;and;lea;xor;xchg`          +5
               main body, per 4 bytes     5 instr x 4 + `add;cmp;jne`  = 23
               after it                   `test;je`                       +2
       if L mod 4 != 0                    `add` + 8 per byte + `jmp`
    if 1 <= L <= 3                        `xor;jmp` + `add` + 8/byte + `jmp`

so, with `r = L mod 4`,

    fold4(0)      = 2
    fold4(1..3)   = 10 + 8*L
    fold4(L>=4)   = 13 + 23*(L div 4) + [r>0]*(2 + 8*r)

⚠ **One of those instructions is a NOP.** `xchg %ax,%ax` at the top of the
unrolled preamble is executed once per field with `L >= 4` -- `.memory/03`'s
trap 3, third instance in this project after p06's two. It is 1.000 of the 5,
i.e. **20% of the per-field entry cost and 1/13 of `fold4(4)`**, and a
coefficient fitted without disassembling would have absorbed it silently.

Outside the inner loop the fold costs a flat **19.00 Ir per field** (the table
read, the length fold, the cursor update and the outer back-edge).

THE FOLD, R2 (`safe_naive.rs`), read off the listing
----------------------------------------------------
NOT unrolled, and the reason is visible: the loop body is

    `cmp $0x3f,%rax` ; `ja <panic>`            <- THE BOUNDS CHECK on scr[cur+q]
    `mov;shl;sub;movzbl;add;inc;dec;jne`

= **10.00 Ir per folded byte flat**, against R4's **5.75** in the unrolled body.
`10.00 - 5.75 = 4.25`, which is `.memory/01-ladder.md`'s `4.25 = 2.00 + 2.25`
-- 2.00 for the `cmp; ja` and 2.25 for the 4x unroll the check blocks -- on a
FOURTH kernel after p16, p17 and p11.

WHY BAND `t` IS THE TEST
------------------------
`sweep-t*` holds `nline`, `llen` and therefore the copy, the scan and the header
decode all FIXED at 8 lines of 60 bytes, and moves only the number of
delimiters. So `Ir(t_k) - Ir(t_1)` contains the fold and nothing else, and the
law above predicts it with no free parameter at all.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sweep_ir  # noqa: E402

SCR, MAXTOK, DELIM = 64, 16, 0x2C
PER_FIELD_R4 = 19.0        # outside the inner byte loop, read off the listing
PER_BYTE_R2 = 10.0         # R2's inner loop body, read off the listing


def fold4(L):
    """R4's inner byte loop, in instructions, for one field of length `L`."""
    if L == 0:
        return 2
    if L < 4:
        return 10 + 8 * L
    r = L % 4
    return 13 + 23 * (L // 4) + ((2 + 8 * r) if r else 0)


def field_lengths(blob):
    """Every recorded field's length, per window, read out of the blob."""
    f = sweep_ir.slb.read(blob)
    stride, body = sweep_ir.slb.head1_u64_bytes(f.payload[: f.declared_len])
    win = body[:stride]
    nline = int.from_bytes(win[:4], "little")
    p, out = 4, []
    for _ in range(nline):
        if stride - p < 4:
            break
        llen = int.from_bytes(win[p:p + 4], "little")
        p += 4
        m = min(llen, SCR)
        if stride - p < llen:
            break
        scr = bytes(win[p:p + m])
        p += llen
        out.extend(len(x) for x in scr.split(bytes([DELIM]))[:MAXTOK])
    return out


def r4_fold_cost(blob):
    ls = field_lengths(blob)
    return sum(fold4(L) for L in ls) + PER_FIELD_R4 * len(ls)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json")
    ap.add_argument("--band", default="sweep-t")
    ap.add_argument("--cell", default="unsafe")
    a = ap.parse_args()
    d = json.load(open(a.json))
    rows = [r for r in d["rows"] if r["blob"].startswith(a.band)]
    rows.sort(key=lambda r: r["blob"])
    if not rows:
        raise SystemExit(f"no rows for band {a.band}")
    base = rows[0]
    bp = os.path.join(sweep_ir.INPUTS, base["blob"])
    b_pred = r4_fold_cost(bp)
    b_meas = base["ir"][a.cell]
    print(f"reference {base['blob']}  measured {b_meas:.4f}  "
          f"derived fold {b_pred:.2f}")
    print(f"\n{'blob':18s} {'fields':>7s} {'derived d':>12s} "
          f"{'measured d':>12s} {'residual':>10s}")
    worst = 0.0
    for r in rows[1:]:
        p = os.path.join(sweep_ir.INPUTS, r["blob"])
        dp = r4_fold_cost(p) - b_pred
        dm = r["ir"][a.cell] - b_meas
        res = dm - dp
        worst = max(worst, abs(res))
        print(f"{r['blob']:18s} {len(field_lengths(p)):7d} {dp:12.2f} "
              f"{dm:12.4f} {res:10.4f}")
    print(f"\nWORST |residual| over {len(rows) - 1} blob(s): {worst:.4f}  "
          f"(ZERO fitted parameters)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
