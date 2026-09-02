# `common/census/` — the C-corpus census artefacts

Promoted at **TASK_132** from `TASK_129`/`TASK_131` scratch. Two ARTEFACTS live
here — the manifests (§1) and `ptr_cursor_regex.py` (§2) — and both exist
because a number was published that nobody could re-derive. ⚠ **§3 is a third
thing and it is NOT an artefact**: it records the `0 of 255` bound-site
denominator and its `p`-value at 33 kernels, because the instrument that
produces those two published numbers is **still** only in gitignored `.temp/`
(added TASK_166).

## 1. The three sha256 manifests

`php.manifest`, `coreutils.manifest`, `cgnu.manifest` — every `.c` and `.h`
file in the three C corpora `TASK_129`'s census read, with its sha256.
Regenerate with `sh common/census/manifest.sh` (**read-only on the corpora**);
`MANIFEST.sha256` is the digest-of-digests over the three files.

| corpus | files | root |
|---|---|---|
| `php` | 553 | `/home/apt/repos_common/php-in-safe-rust/build/php-4.0.2` |
| `coreutils` | 963 | `/home/apt/repos_common/unsafe-rust-pitfall/TASKS/TASK014_eng_coreutils_u2/.temp/work/coreutils` |
| `cgnu` | 3826 | `/home/apt/repos_common/unsafe-rust-pitfall/.temp/shared/artifacts/pr2/benchmarks/c-gnu` |

⚠⚠ **Why they are in the tree at all: two of the three corpora live under
ANOTHER PROJECT'S `.temp/`,** which that project's own convention makes
deletable at any time. A census whose corpus cannot be re-identified is a census
nobody can check.

⚠ **Size, judged against `.memory/00-environment.md`'s *"kilobytes, not
gigabytes"*: 506 K.** That is neither, so the judgement is written down rather
than assumed:

* the paths are **corpus-relative**, and that alone took 950 K → 506 K (46.8%)
  with **zero content lost** — the root is one header line. Verified line by
  line against `TASK_129`'s scratch manifests: 5342 of 5342 `(path, sha256)`
  pairs identical, symmetric difference 0.
* the remaining 506 K is sorted, diffable, greppable ASCII — the shape the
  policy is *for*. It is 0.9% of `.git` as it already stands.
* **Smaller forms were measured and rejected, and what each loses is stated:**
  gzip → 205 K but stops being greppable or diffable; a digest-of-digests plus
  per-program counts → ~2 K and keeps the *re-identification* guarantee in full
  (it still proves a candidate corpus is the measured one) but loses the two
  things that matter once a corpus is **deleted**: *which* file differs, and
  what the corpus contained.

✅ **And the manifests are SUFFICIENT to re-derive the census population, which
is the strongest justification for keeping them.**
`census_filelists.py` rebuilds `TASK_129`'s deduplicated corpus file lists from
these three files alone — *"distinct `.c` by sha256"* — and reproduces
**php 299 / coreutils 94 / cgnu 2162** exactly, the three counts `TASK_129`
published. It exits 1 if any of them moves, so the promotion is a check and not
just a copy. ⚠ Its output names absolute paths into other projects' trees and
goes to gitignored scratch, never into the tree.

⚠ **What a green manifest does NOT buy.** It says the bytes are the ones that
were measured. It says nothing about whether the corpus is representative — see
`TASK_131` on gnulib duplication surviving content-hash dedup — and nothing
about the labels `census.py` put on those bytes.

## 2. `ptr_cursor_regex.py` — the classifier-free pointer-cursor count

`RECAP` finding 45 published *"`845` over PHP, `0` over the kernels, both
numbers exact"*. ⚠⚠ **The regex behind it was never written down**, so neither
number was re-derivable; `TASK_131`'s reviewer reconstructed one, got **854**,
and shipped a *different* (earlier) spelling in that task's scratch that prints
**952** (`v0` below). Dated record: `.tasks/TASK_131_REPORT.md`. This file is
the instrument, with its guard as an explicit parameter, because **the number is
a property of the guard**:

    python3 common/census/ptr_cursor_regex.py --must-fire --ladder

| corpus | files | v0 | v1 | v2 | v3 |
|---|---|---|---|---|---|
| MUST-FIRE planted kernel | 1 | **2** | **2** | **2** | **2** |
| ladder `patterns/*/c/kernel.c` | **33** | 2 | 2 | **0** | **0** |
| ladder `patterns/*/c/*.{c,h}` | **131** | 9 | 7 | 2 | 0 |
| php | 299 | 952 | 920 | 916 | 781 |
| coreutils | 94 | 38 | 38 | 35 | 32 |
| cgnu | 2162 | 3570 | 3504 | 3315 | 2718 |

`v0` no guard · `v1` byte-adjacent · `v2` whitespace-skipping · `v3` `v2` plus
rejecting a preceding `)`.

⚠⚠ **THE TWO LADDER DENOMINATORS WERE `26` AND `103` UNTIL TASK_166 AND THE
FOUR GUARD COUNTS DID NOT MOVE WITH THEM.** Re-run today
(`python3 common/census/ptr_cursor_regex.py --ladder`) over the 33-pattern tree:
`33` kernels give `2 / 2 / 0 / 0` and `131` `c/*.{c,h}` files give `9 / 7 / 2 / 0`
— **every one of the eight counts identical to the 26-pattern figures.** ✅ That
is the strongest form of the out-of-sample result, because `p28` (intrusive
lists), `p29` (BST delete) and `p34` (refcount) are **pointer-structure** rows
and were the obvious place for the gap to close by accident. **Seven new
kernels, zero new pointer-cursor sites.**

⚠ **Read that table before quoting any figure from it.** The `0` over the 33
`kernel.c` reproduces — but **only under `v2`/`v3`**; under the guard that
actually shipped in `TASK_131` it is **2**, and both hits are `8 * (n + m)` in
`p46`, i.e. a *multiplication* counted as a dereference. And **no variant
reproduces `845` or `854`**: the four honest spellings span `952 → 781` over
PHP, a ±10% range, so the "1% off" reading of the `845`/`854` disagreement
understates it by an order of magnitude.

## 3. The `0 of 255` denominator, and what it is at 33 kernels

⚠ **`results/SYNTHESIS.md` §7 quotes `ptr_offset` as `0` of the built tree's
**255** bound sites, with a size-matched `p ≈ 0.06` caveat.** Both come from
`TASK_129`'s classifier and `TASK_131`'s size probe, and **neither is committed**
— they live in gitignored `.temp/t129/` and `.temp/t131/` with a `REBUILD.sh`
each. They are re-runnable and they were re-run at `TASK_166`; recording the
numbers here so the published ones stop resting on scratch nobody can find:

| population | bound sites | `ptr_offset` | site-carrying functions | files |
|---|---:|---:|---:|---:|
| the 26 kernels the caveat was computed on | **255** | **0** | **30** | 26 |
| all 33 kernels today | **464** | **0** | **40** | 33 |

The 26-row is a **control**: it reproduces the published `255` / `30` / `26`
exactly from `git HEAD`, so the 33-row is the same instrument and not a new one.

**And the caveat needs RE-COMPUTING, not re-wording — it gets ~5× stronger.**
The honest figure is the FUNCTION unit, size-matched against the largest corpus
(`cgnu`, 2162 files):

```
26 kernels, 30 site-carrying functions:  expected walkers 2.66   P(zero) = 0.0612   <- the published "p ~ 0.06"
33 kernels, 40 site-carrying functions:  expected walkers 4.12   P(zero) = 0.0123
```

⚠ The other two corpora move the same way (php `0.0047 → 0.0006`, coreutils
`0.0499 → 0.0149`), and the SITE unit — which the review rejected as
over-counting, because the sites are not independent draws — runs
`1.2e-05 → 5.0e-11`. ⚠⚠ **`p ≈ 0.06` is therefore STALE AND CONSERVATIVE**, and
the sentence *"suggestive, not decisive"* should be re-taken at `p ≈ 0.012`
rather than reworded.

⚠ **The `0 of 255` framing is still the wrong one** for the reason `TASK_131`
gave: the sites sit in a small number of functions across files cloned from one
template, so quote the function-unit p-value and the site count together.

## Digest note — the price of this directory

⚠⚠ **Nothing here may be imported by `harness/check.py`, `harness/measure.py`
or `harness/build.py`.** `check.py`'s `source_sha256` globs `common/*.py` and
`common/layout/*.py` **non-recursively**, and `measure.py::measurement_sources`
does not reach `common/` at all — so this directory is outside both digests and
costs no sweep and no re-measure to maintain. An `import` from the gate would
silently pull it back in, and a comment fix here would then cost 57 minutes.

**Verified, not assumed** (TASK_132 §F): `results/gate/p23-partition.json`'s
`source_sha256` key set is identical before and after this directory existed.
