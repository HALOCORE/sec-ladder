# `.memory-php/02-ladder.md` — how an EXTRACTED row's ladder differs

> ⚠ **`.memory-php/` is the AUTHORITATIVE layer for the PHP programme, and it
> SUPERSEDES any task report it contradicts** (`.tasks/PROTOCOL.md` rule 9).
> Only findings that have survived a full engineer→reviewer cycle are here.
>
> ⚠⚠ **SCOPE: this carries ONLY what is php-specific.** The PAT `.memory/`
> 00–06 applies unchanged — same harness, same bench rules, same measurement
> discipline, same Verus notes. **Do not restate any of it here; two copies of
> one rule is how both go stale.**
>
> The narrative, the open items and findings F1–F34 live in `RECAP_PHP.md`.

---


- ⚠⚠⚠ **R2–R5 ARE NOT PORTS OF R1h.** Where the real upstream fix is
  **incomplete**, a safe-Rust rung built to it **panics** on the surviving
  inputs — **and a rung that panics is not a translation of the C.** So the
  hardened C rung carries the historical fix, the Rust rungs carry whatever is
  actually memory-safe, and only R1 diverges. ✅ **Reviewed and upheld.**
- ⭐⭐ **And an upstream fix can be BOTH dead and incomplete.** `ph03`'s 2004
  fix has two hunks: hunk 1 is **provably redundant** (Verus verifies 25/0 with
  it deleted from exec *and* with it neutralised in the spec; all 1 953 of its C
  firings are also refused by hunk 2), and hunk 2 leaves **144 over-reads in
  12 600 documents**. ⚠ **Do not assume a shipped fix is minimal OR sufficient —
  measure both ends.**
- ⚠ **A sanitizer limb is a claim about YOUR allocator, not about PHP.** `ph03`'s
  ASan evidence is **silent** when the source is allocated the way `emalloc`
  really allocates a zval string (`ALIGN8(len+1)`) — the over-read lands in
  padding. **Say "a detector fires under this allocator", never "PHP faults",
  unless the row models PHP's allocator.**
- **R1h = the real upstream `fix_commit`**, not a hand-written control.
  ⚠ `git fetch` of a bare SHA is refused by the server; **the patch URL works**:
  `https://github.com/php/php-src/commit/<sha>.patch` (~1.4 KB). Keep the patch
  bytes under the row so the citation survives without network. (F26.)
- ⚠ **A green php gate does NOT mean the upstream fix is complete, and cannot.**
  `check_sanitizers_hardened` hard-fails on any R1h diagnostic — correct for a
  hand-written PAT control, wrong for a shipped fix that is incomplete. That
  evidence lives in the row's `controls/`. **Standing limitation, not a bug to
  file.** (F31.)
- ⚠ **`harness/build.py` links no `-lm`.** `floor()` emits a real call at `-O0`
  and is inlined at `-O3`, and libm was never merged into libc — so a `verbatim`
  libm kernel fails to link in the `-O0` cells. **Batched, not fixed.**
  ⭐ Whoever does it should know **`-lm` is link-only**, so for every pattern
  calling no libm function the re-measured numbers must be byte-identical —
  the re-measure is self-verifying. (F31.)

- ⭐ **WHERE TO LOOK FOR THE FIX: a missing bound is often restored in the
  PROLOGUE, not at the site.** `ph07`'s `mbfl_strcut` was characterised — by the
  catalogue *and* by an engineer — **by its loop**, so both checked the loop in
  the fixed version, found it still expressed in terms of `from`, and concluded
  no fix existed. ✅ 5.4.0's **prologue** carries the guard:
  `if (from >= string->len) { from = string->len; }`. **The guard moved; it did
  not vanish.** This is `01-extraction.md`'s three-frames problem arriving in the
  **repair** instead of the defect. (F34.)
- ⚠ **A fix can ship inside an unlabelled rewrite.** `ph07`'s vulnerable code went
  out **byte-identical from 5.0.0 through 5.3.x** and was repaired by a 5.4.0
  rewrite carrying no security label — so *"no CVE, no security commit"* is **not**
  evidence that a defect was never fixed. Check the code at later tags.

## The ladder, as row 1 actually measured it

`ph03`, `Ir(kernel)`, `small.bin`, `O3 / isolated` — ⚠ **within-row ratios only**
(`03-numbers.md` forbids any comparison with a `pNN` figure):

| `safe_naive` | `safe_tuned` | `unsafe` | `verus` | `c-gcc-h` (real 2004 fix) |
|---:|---:|---:|---:|---:|
| **+26.8 %** | **+3.7 %** | **−7.6 %** | **−7.6 %** | **−0.4 %** |

- **Tuning recovers 86.4 % of the naive-safe gap**, so *"safe Rust costs 27 %"*
  and *"safe Rust is nearly free"* are **the same pattern written two ways.**
- ⭐ **`verus` is BYTE-IDENTICAL to `unsafe`** (`md5_fn 33850579` on both) — **the
  proof costs nothing at run time.**
- ⭐ **The safety check can be NEGATIVE-cost**: the hardened C beats the unchecked
  C, because the check lets gcc drop a `setae` and two `cmove`s. (F30, F33.)
- ⚠⚠ **Two things in that same table are NOT safety effects and will be misread
  as such**: `c-clang` beats `c-gcc` by **15.4 %** (larger than every safety
  effect on the row), and **both C compilers vectorise while no Rust rung does** —
  the latter is a property of *how the translation is written*, not of Rust.
- ⚠ **No ratio here is *the* cost of safety.** `controls/spellings.py` was not
  built, so each figure is the cost of *these spellings* of these rungs.
