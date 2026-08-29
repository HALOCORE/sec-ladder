# `common/census/` — the C-corpus census artefacts

Promoted at **TASK_132** from `TASK_129`/`TASK_131` scratch. Two things live
here, and both exist because a number was published that nobody could
re-derive.

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
| ladder `patterns/*/c/kernel.c` | 26 | 2 | 2 | **0** | **0** |
| ladder `patterns/*/c/*.{c,h}` | 103 | 9 | 7 | 2 | 0 |
| php | 299 | 952 | 920 | 916 | 781 |
| coreutils | 94 | 38 | 38 | 35 | 32 |
| cgnu | 2162 | 3570 | 3504 | 3315 | 2718 |

`v0` no guard · `v1` byte-adjacent · `v2` whitespace-skipping · `v3` `v2` plus
rejecting a preceding `)`.

⚠ **Read that table before quoting any figure from it.** The `0` over the 26
`kernel.c` reproduces — but **only under `v2`/`v3`**; under the guard that
actually shipped in `TASK_131` it is **2**, and both hits are `8 * (n + m)` in
`p46`, i.e. a *multiplication* counted as a dereference. And **no variant
reproduces `845` or `854`**: the four honest spellings span `952 → 781` over
PHP, a ±10% range, so the "1% off" reading of the `845`/`854` disagreement
understates it by an order of magnitude.

## Digest note — the price of this directory

⚠⚠ **Nothing here may be imported by `harness/check.py`, `harness/measure.py`
or `harness/build.py`.** `check.py`'s `source_sha256` globs `common/*.py` and
`common/layout/*.py` **non-recursively**, and `measure.py::measurement_sources`
does not reach `common/` at all — so this directory is outside both digests and
costs no sweep and no re-measure to maintain. An `import` from the gate would
silently pull it back in, and a comment fix here would then cost 57 minutes.

**Verified, not assumed** (TASK_132 §F): `results/gate/p23-partition.json`'s
`source_sha256` key set is identical before and after this directory existed.
