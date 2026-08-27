#!/usr/bin/env python3
"""Census over `results/synthesis.md` §1 and §2 — the aggregates
`results/SYNTHESIS.md` §2 quotes, so every count in that prose is re-derivable
from a clone rather than eyeballed.

    python3 synthesis/census.py

Reads ONE committed file (`results/synthesis.md`). Runs nothing, builds nothing,
measures nothing, and imports nothing outside the standard library.

Provenance: written at TASK_108 as `.temp/t108/census.py`, which was gitignored
— so the only new aggregate in a committed, outward-facing document was **not
re-derivable from a clone**, and `CLAUDE.md` rule 1 told the next agent to delete
it (TASK_111 M7). Moved here at TASK_112 and extended with the two arms below.

Three arms:

  A. the bucket census (within +-32 on both blobs / negative on both / >100 on
     either), over the rows §2 LICENSES for the `R3-R4` pair;
  B. the R2-overstatement ratio population, which the prose quotes as a range
     and a median — reported over the LICENSED rows only, because the section
     that quotes it excludes the unlicensed ones;
  C. arm A and arm B recomputed with p22's `R3-R4` at the value the RECORD
     carries rather than the shipped cell's. `+2.00` is a fixed-R4 bound against
     an under-searched R4; `.memory/01-ladder.md` finding 22 and RECAP finding
     33 put the gap at `+125.00 / +1021.00` against the cheapest admissible R4
     (`r4_reslice`: in contract, `20 verified, 0 errors`, byte-identical to its
     own R5 at -O3). That is 510x on the large band and it moves a bucket.
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "results" / "synthesis.md"

# Every row with a MEASURED, VERIFYING, IN-CONTRACT R4 counterpart cheaper than
# the shipped one, cited to the authoritative layer.  The shipped cell stays the
# published figure (`.memory/02-bench-rules.md`: never re-ship a rung because a
# cheaper in-contract spelling was found); this arm exists so a reader can see
# what the buckets look like when the fixed-R4 bounds are replaced by the
# searched values, and in which direction they move.
# (pattern, (small, large), citation)
RECORD_R3R4 = {
    "p22": ((125.00, 1021.00),
            ".memory/01-ladder.md finding 22 / RECAP finding 33: `r4_reslice` "
            "is in contract, verifies 20/0 and is byte-identical to its own R5 "
            "at -O3; the shipped +2.00 is a fixed-R4 bound. 510x on `large`"),
    "p13": ((44.00, 77.00),
            ".memory/01-ladder.md finding 14 (p13) / results/synthesis.md §2 "
            "search column: a bounded unchecked consumer verifies 19/0 with no "
            "new trusted item and is excluded by nothing but spec.md's English. "
            "SIGN FLIP"),
    "p12": ((20.00, 66.00),
            ".memory/01-ladder.md p12 (TASK_040_REVIEW built route A): "
            "15/0, twin 18/0, `R4 = R5 exact`, 17.00/92.00 cheaper than the "
            "shipped R4, so R3ship is +66.00 dearer on `large`. SIGN FLIP"),
    "p10": ((-129.00, -241.00),
            ".memory/01-ladder.md finding 18 (p10): the rejected R4 candidate "
            "`u_win` verifies 10/0 with no new trusted item; 60% of the "
            "published margin was R4 SPELLING"),
}

# For completeness of the direction argument: the two rows whose known lever is
# on the R3 side move the difference DOWN, i.e. toward safe Rust.  They are not
# applied above, because a cheaper R3 against a fixed R4 is a different
# quantity from a cheaper R4 against a fixed R3.
R3_SIDE_LEVERS = {
    "p17": ("-19.00 flat (in-contract respelling, byte-identical to a row an "
            "earlier task had excluded; .memory/01-ladder.md p17, TASK_018, "
            "reviewed at TASK_018_REVIEW)"),
    "p06": ("+80.00 / +187.00 for `c_idx` against a shipped +334 / +172 "
            "(.memory/01-ladder.md p06 — marked PROVISIONAL: landed at "
            "TASK_048 and not through a second review; and on `large` the "
            "SHIPPED R3 is the cheaper of the two)"),
}

rows = {}
for line in SRC.read_text().splitlines():
    m = re.match(r"^\| (p\d\d)-\S+ \| (small|large) \|(.*)\|\s*$", line)
    if not m:
        continue
    pat, blob, rest = m.group(1), m.group(2), m.group(3)
    cells = [c.strip() for c in rest.split("|")]
    if len(cells) != 8:
        continue

    def num(s):
        return None if s == "-" else float(s)
    cg, cgh, cc, cch, r2, r3, r4, r5 = (num(c) for c in cells)
    rows[(pat, blob)] = dict(c_gcc=cg, c_gcc_h=cgh, c_clang=cc, c_clang_h=cch,
                             r2=r2, r3=r3, r4=r4, r5=r5)

if not rows:
    sys.exit(f"no §1 rows parsed out of {SRC} — has the table format changed?")

pats = sorted({p for p, _ in rows})
print(f"patterns in the table: {len(pats)}")


def diff(pat, a, b):
    return tuple(rows[(pat, blob)][a] - rows[(pat, blob)][b]
                 for blob in ("small", "large"))


def r3r4(pat, use_record=False):
    if use_record and pat in RECORD_R3R4:
        return RECORD_R3R4[pat][0]
    return diff(pat, "r3", "r4")


print("\npattern  R3-R4 small/large        R2-R4 small/large       R5-R4")
for p in pats:
    d3, d2, d5 = r3r4(p), diff(p, "r2", "r4"), diff(p, "r5", "r4")
    print(f"{p}  {d3[0]:12.2f} {d3[1]:12.2f}   "
          f"{d2[0]:12.2f} {d2[1]:12.2f}   {d5[0]:.2f} {d5[1]:.2f}")

print(f"\nR5-R4 == 0 on every row: "
      f"{all(diff(p, 'r5', 'r4') == (0.0, 0.0) for p in pats)}  "
      f"({len(pats)} patterns x 2 blobs)")

# ---- the licence, read out of §2's own `R3-R4` table -------------------------
# The licence tag answers ONLY "may this row be differenced", never "by how much".
text = SRC.read_text()
sec = text.split("### `R3-R4`")[1].split("###")[0]
lic = {}
for line in sec.splitlines():
    m = re.match(r"^\| (p\d\d)-\S+ \|[^|]*\|[^|]*\| (\S+) \|", line)
    if m:
        lic[m.group(1)] = m.group(2)
unlic = sorted(p for p in pats if lic.get(p) != "LICENSED")
ok = [p for p in pats if lic.get(p) == "LICENSED"]
print(f"\nR3-R4 licence: {len(ok)} LICENSED, not licensed: {' '.join(unlic)} "
      f"({', '.join(lic[p] for p in unlic)})")


def buckets(use_record):
    flat32 = [p for p in ok if all(abs(v) <= 32 for v in r3r4(p, use_record))]
    neg = [p for p in ok if all(v < 0 for v in r3r4(p, use_record))]
    big = [p for p in ok if any(v > 100 for v in r3r4(p, use_record))]
    return flat32, neg, big


def show_buckets(tag, use_record):
    flat32, neg, big = buckets(use_record)
    print(f"\n--- ARM {tag}: buckets over the {len(ok)} LICENSED rows ---")
    print(f"  within +-32 on both ({len(flat32)}/{len(ok)}): {' '.join(flat32)}")
    print(f"  negative on both    ({len(neg)}/{len(ok)}): {' '.join(neg)}")
    print(f"  > 100 on either     ({len(big)}/{len(ok)}): {' '.join(big)}")
    covered = set(flat32) | set(neg) | set(big)
    both = sorted(set(flat32) & set(neg))
    none = sorted(set(ok) - covered)
    print(f"  ⚠ NOT a partition: in two buckets {both or '-'}; "
          f"in none {none or '-'}  (sum {len(flat32)}+{len(neg)}+{len(big)}="
          f"{len(flat32) + len(neg) + len(big)} vs {len(ok)} rows)")


show_buckets("A (shipped cells)", False)
show_buckets("C (record substitutions applied)", True)
for p, (v, why) in sorted(RECORD_R3R4.items()):
    print(f"      {p}: shipped {r3r4(p)} -> searched R4 {v}\n         {why}")
print("      ⚠ every one of those four moves AGAINST safe Rust.")
print("      The two known R3-side levers move the other way and are NOT "
      "applied:")
for p, why in sorted(R3_SIDE_LEVERS.items()):
    print(f"      {p}: {why}")


def ratios(use_record):
    """R2 overstatement against R3, on `large`, where R3-R4 > 0."""
    out = []
    for p in ok:
        d3 = r3r4(p, use_record)[1]
        d2 = diff(p, "r2", "r4")[1]
        if d3 > 0:
            out.append((d2 / d3, p, d2, d3))
    return sorted(out)


def show_ratios(tag, use_record):
    rs = ratios(use_record)
    med = rs[len(rs) // 2] if len(rs) % 2 else None
    print(f"\n--- ARM B{tag}: R2-R4 over R3-R4 on `large`, LICENSED rows with "
          f"R3-R4 > 0 ({len(rs)} rows) ---")
    for r, p, d2, d3 in rs:
        print(f"  {p}  R2-R4 {d2:10.2f}  R3-R4 {d3:9.2f}  ratio {r:8.2f}x")
    print(f"  range {rs[0][0]:.2f}x ({rs[0][1]}) .. {rs[-1][0]:.2f}x "
          f"({rs[-1][1]})")
    if med:
        print(f"  median {med[0]:.2f}x ({med[1]}, the "
              f"{len(rs)//2 + 1}th of {len(rs)})")
    below1 = [p for r, p, _, _ in rs if r < 1.0]
    print(f"  ⚠ rows where R2 is NOT dearer than R3 ({len(below1)}): "
          f"{' '.join(below1)} — the ratio is not an 'overstatement' there")


show_ratios(" (shipped cells)", False)
show_ratios(" (record substitutions applied)", True)

# The population the prose used to quote from, and why it is the wrong one.
allpos = sorted((diff(p, "r2", "r4")[1] / diff(p, "r3", "r4")[1], p)
                for p in pats if diff(p, "r3", "r4")[1] > 0)
mids = [r for r, _ in allpos][len(allpos)//2 - 1:len(allpos)//2 + 1]
print(f"\nOver ALL {len(allpos)} positive rows (licensed or not): "
      f"range {allpos[0][0]:.2f}x ({allpos[0][1]}) .. "
      f"{allpos[-1][0]:.2f}x ({allpos[-1][1]}), median "
      f"{sum(mids)/2:.2f}x (mean of {mids[0]:.2f} and {mids[1]:.2f})")
for r, p in allpos:
    if p in unlic:
        print(f"  ⚠ {p} is {r:.2f}x and is {lic[p]} — §2's own licence rule "
              f"excludes it, so it must not set an endpoint of this range")
