# MANAGER NOTES while `TASK_PHP_048` runs — **PENDING MERGE INTO `RECAP_PHP.md`**

> ⛔ Rule 11: `_048` reads `RECAP_PHP.md`, `.memory-php/`, `PROTOCOL_PHP.md`,
> `patterns-php/`, `results-php/` and the committed checkers, so I may not edit
> or commit any of them while it runs. ⭐ **Committed rather than left in
> `.temp/`, which is F99's own defect.** ▶ **Merge into `RECAP_PHP.md` item 62 on
> `_048`'s landing and DELETE this file.**

---

## ⛔ `_049` §5's MOST PROMISING UNCHASED LEAD — **CHASED, AND IT DOES NOT WORK**

`_049` flagged: *"`O3`/`whole`'s `main_exclusive_ir` already contains the inlined
kernel on every cell and may be a cheap family-C proxy."* ▶ **Tested against the
one row where family C is known. It fails, for a structural reason.**

**`ph29`, `large.bin`, `O3`, `c-gcc` → `c-clang`** (`results-php/ph29-recvfrom-alloc.json`):

| quantity | gcc → clang |
|---|---:|
| A1 (`kernel_exclusive_ir`, `isolated`) | **−28.09 %** ✅ reproduces `_049` |
| ⭐ **proxy** (`main_exclusive_ir`, `whole`) | ⛔ **−32.34 %** |
| **family C** (`_049`, measured) | **−27.01 %** |
| W1 (`_049`, measured) | **−26.74 %** |

⛔ **The proxy is 5.3 pp from family C** — ~20 % relative error on the effect.

⭐⭐ **AND THE REASON IS STRUCTURAL, SO NO CALIBRATION FIXES IT: `main_exclusive_ir`
at `O3/whole` IS A W1-LIKE QUANTITY, NOT A C-LIKE ONE.** It includes `main`'s own
driver work and everything inlined, and **excludes nothing** — whereas family C is
*the kernel symbol inclusive of its callees*. ▶ **Their relationship is governed
entirely by `inside_share`**, measured across 8 rows as
`whole main_exclusive` against `isolated (kernel + main)`:

* **high-`inside_share` rows nearly coincide** — `ph52` `−1.2 … −4.3 %`,
  `ph53` `−0.1 … +4.4 %`;
* ⛔ **low-`inside_share` rows diverge by an order of magnitude** — `ph45`'s Rust
  cells read **+847 % to +1168 %**, because `ph45`'s levers live in the callee
  `dec` and its `inside_share` is **~9.5 %**.

▶ **So the proxy would be accurate exactly where family C is least needed and
useless exactly where it is most needed.** ⓘ **Item 62 still needs the real
thing, for both C cells per row** (`_049` §3.3).

## ⛔ AND A HYPOTHESIS OF MINE, KILLED AT `n = 8` BY MY OWN PROBE

From `ph29` alone I read *"clang exploits cross-TU visibility at `whole` and gcc
does not"* — clang's `whole` figure was **5.2 M Ir below** its `isolated`
`kernel + main`, while gcc's matched to **0.1 %**. ⛔ **Not supported across the
corpus**: mean `whole` − `isolated(k+m)` is **`c-clang` −1.05 %** against
**`c-gcc` +0.74 %**, with per-row spread `−5.97 … +8.98` on both. **The means are
small, the spread swamps them, and `ph29` is an outlier.**
⭐ **Law 12 again, on a hypothesis I formed and killed inside one probe** — worth
recording only because it is the second time in two days that a `ph29`-shaped
n = 1 reading of mine has not survived n = 8.

⚠ **All figures A1/`main_exclusive_ir`, `large.bin`, `O3`, from
`results-php/*.json`. No `O0` figure is quoted as a performance result.**
