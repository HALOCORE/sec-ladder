#!/usr/bin/env python3
"""p10: enumerate every backward-branch loop of a kernel symbol, with its body
instruction count and whether any alignment `nop` is INSIDE the body.

    python3 patterns/p10-fir-stencil/controls/loops.py <binary> <symbol>
    python3 patterns/p10-fir-stencil/controls/loops.py <binary> <symbol> --body

**Why this exists.** TASK_057: *"attribute every per-iteration `Ir` law mnemonic
by mnemonic before naming it after a mechanism -- executed alignment padding has
landed inside a published law three times."* p10 names two per-iteration
coefficients after mechanisms -- `vecit = 17.00` (the SSE2 tap body) and
`scaltap` (the scalar epilogue, 7 on c-clang, 9 on R3 and R4, 12 on R2) -- and
this is what checks that neither contains a padding instruction. It reports
`nops_inside=0` for BOTH loops on all four LLVM cells (../NOTES.md 8c).

It also shows why the PER-CALL and PER-OUTPUT coefficients are NOT named after
mechanisms here: the outer loop's span contains 2-3 alignment `nop`s, and a
`nop` sitting immediately before an inner loop's head is on the FALL-THROUGH
path into that loop, so it retires once per output. Up to 2 of R4's 29.00
Ir/output really is padding.

A loop is a backward branch whose target is an instruction of the same symbol;
the body is every instruction from the target to the branch inclusive. That
over-counts a nested loop's outer body (it swallows the inner loops), which is
why the outer rows are reported and not used.
"""
import re, subprocess, sys
OBJ = '/usr/bin/objdump'

def loops(binary, sym):
    out = subprocess.run([OBJ, '-d', '--no-show-raw-insn', binary],
                         capture_output=True, text=True).stdout.splitlines()
    st = next(i for i, l in enumerate(out) if re.search(r'<[^>]*' + re.escape(sym) + r'[^>]*>:', l))
    en = len(out)
    for i in range(st + 1, len(out)):
        if re.search(r'^[0-9a-f]+ <', out[i]):
            en = i
            break
    blk = [l for l in out[st + 1:en] if re.match(r'\s*[0-9a-f]+:', l)]
    addr = [int(l.split(':')[0].strip(), 16) for l in blk]
    txt = [l.split('\t')[-1].strip() if '\t' in l else l.split(':', 1)[1].strip() for l in blk]
    res = []
    for k, l in enumerate(txt):
        m = re.match(r'j(ne|e|b|be|a|ae|mp)\s+([0-9a-f]+)', l)
        if m and int(m.group(2), 16) < addr[k] and int(m.group(2), 16) in addr:
            i0 = addr.index(int(m.group(2), 16))
            body = txt[i0:k + 1]
            res.append((addr[i0], addr[k], len(body),
                        [x for x in body if 'nop' in x], body))
    return res

if __name__ == '__main__':
    for lo, hi, n, nops, body in loops(sys.argv[1], sys.argv[2]):
        print(f"loop {lo:x}..{hi:x}  body={n:3d}  nops_inside={len(nops)}")
        if "--body" in sys.argv[3:]:
            for x in body:
                print("     ", x)
