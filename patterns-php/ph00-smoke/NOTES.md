# `ph00-smoke` — notes

## `PROTOCOL.md` rule 6 — the contract hash, as first written, and it MOVED

| # | when | `contract_sha256` |
|---|---|---|
| 1 | **as first written, before any cell was built** | `6e20789ef14e867495ff66f0489885acb00224249ba10b21c9edef27ed31ff58` |
| 2 | **intermediate, never gated**: the row-specific `why` still contained the literal `NAMED-SPELLING STANDARD`, which the gate's own reproduction command (`str.find`, first occurrence) made it hash the wrong bytes for; the prose was reworded | **not recorded** — see below |
| 3 | **as shipped**, after gate run 1 required the named-spelling standard | `91d88e1e18b192258a1acc577672b2989e33f84c112615b03090bb011dad5e8b` |

⚠ **This table showed TWO states and there were at least THREE**
(`TASK_PHP_003` m7). State 2 is described in `.tasks-php/TASK_PHP_002_REPORT.md`
("Building `ph00-smoke`" §1) and its hash was **never recorded**, so it cannot
be reconstructed — which is the point of rule 6 and exactly the gap rule 6
exists to close. Row 2 is listed with `not recorded` rather than omitted,
because a two-row table read as *"it moved once"* and it moved at least twice.

⚠⚠ **THE FIRST NUMBER THIS FILE RECORDED WAS WRONG, AND IT IS DISCLOSED HERE
RATHER THAN QUIETLY REPLACED, BECAUSE A FALSE DISCLOSURE IS WORSE THAN THE
STALE THING IT DESCRIBES** (`.tasks/PROTOCOL.md` rule 6). It said
`8c941e54f7ae…`, which is the hash of the fence body under the *obvious*
regex `` ```slb-contract\n(.*?)\n``` ``. **The gate does not use that
spelling.** `check.py::read_contract` uses

```python
re.search(r"```slb-contract\s*\n(.*?)```", txt, re.S)
```

whose capture **keeps the newline before the closing fence**, so it hashes one
extra byte. The two differ for every pattern in the tree — verified on `p01`:

```
p01 committed contract_sha256: 5360d6f3dd7a4607eaf3599433ca95c0ed43dd66fe20fc85c86d52661597e1e7
  naive  `\n``` spelling     : b5d7dc8dd173c583b9918d1a1f2e952f8160437322158343194dc8ebce2ce3c2
  check.py::read_contract    : 5360d6f3dd7a4607eaf3599433ca95c0ed43dd66fe20fc85c86d52661597e1e7
  they differ by             : '\n'
```

**`5360d6f3…` is what `results/gate/p01-array-sum.json` carries**, so the
gate's spelling is the authoritative one and the naive one is a number that
matches nothing. ⚠ **Compute a rule-6 disclosure with `check.py::read_contract`'s
regex, or the disclosure is unverifiable against the record it is meant to be
checked against.**

### Why the hash moved, in full

The block is `patterns/p01-array-sum/spec.md`'s `5360d6f3dd7a…` with exactly
**three** edits, and the third was forced by the gate:

1. `idiom.why`'s **row-specific prefix** replaced — 1220 chars /
   **200 words**, against p01's 1177 chars / 201.
2. a `provenance` object added (`php_provenance: false`, with a `why`).
3. ⚠ **the 11,003-byte shared named-spelling paragraph put back, verbatim.**
   Gate run 1 hard-failed `[idiom-named-spelling]`: *"`idiom.why` does NOT
   carry the shared named-spelling paragraph (11003 bytes, sha256
   59748cce2db5…)… Without it this pattern's backticked pins are undefined by
   its own contract."* Trimming p01's `why` to 200 words had deleted it.
   ⚠⚠ **`RECAP_PHP.md`'s size rule as worded — "A `spec.md` `why` stays ≤ 200
   words" — is therefore UNSATISFIABLE**; it can only mean 200 words of
   row-specific text *before* the mandatory standard. See
   `.tasks-php/TASK_PHP_002_REPORT.md`.

**No `required`, no `forbidden`, no `identity`, no `miri`, no `collapse`, no
`verus` and no `driver` entry was touched** — that is the point of the
relocation, since a row whose pins were rewritten would prove the gate runs,
not that it runs the same.

⚠ **The `git show HEAD:… | diff -` disclosure command is VACUOUS here and this
says so rather than citing it.** `.tasks/PROTOCOL.md` rule 6 spells this out:
on a **new** row the command compares the working tree to `HEAD`, not *first
written* to *shipped*, so on a clean tree it always prints nothing and always
looks like it passed. The recorded hashes above are the only evidence. The
independently checkable half is the *other* direction — that this row's pins
still equal p01's:

```sh
python3 - <<'EOF'
import json, re
def block(p):
    return json.loads(re.search(r"```slb-contract\s*\n(.*?)```", open(p).read(), re.S).group(1))
a = block("patterns/p01-array-sum/spec.md")
b = block("patterns-php/ph00-smoke/spec.md")
print("keys only in ph00 :", sorted(set(b) - set(a)))
print("keys only in p01  :", sorted(set(a) - set(b)))
print("differing keys    :", sorted(k for k in set(a) & set(b) if a[k] != b[k]))
print("idiom subkeys     :", sorted(k for k in a['idiom'] if a['idiom'][k] != b['idiom'][k]))
EOF
```

Expected, and it is what a working check looks like rather than silence:
`only in ph00 = ['provenance']`, `only in p01 = []`, `differing = ['idiom']`,
`idiom subkeys = ['why']`.

## What this row is

Infrastructure. `TASK_PHP_002` §1.7. The php pipeline is unproven until a gate
has actually run green through `.temp/php-root/` and written into
`results-php/gate/`; this is the row that proves it. It carries **no PHP
provenance, no CWE, no `fix_commit`, no adversarial claim and no result**.

⚠⚠ **THIS SAID *"Delete it once a real php row has gated green"*. FOUR HAVE
(`ph03`, `ph07`, `ph16`, `ph29`) AND THE DECISION IS TO KEEP IT** —
`RECAP_PHP.md` open item 43, decided 2026-09-10. It is not merely *"the only
regression test the shim has"*: it is the **only row that exercises the
`php_provenance: false` path**, where open item 42's sibling defect lives, so
retiring it removes the only live test of that branch.

⚠ **Its records are FIXTURES — subtract it from any population count.** See
`README.md` for the full statement.

## Why relocating `p01` was the right call, measured rather than assumed

`TASK_PHP_002` §4 claim 2 asked whether a minimal fresh kernel would be
cheaper, on the theory that `p01` would drag PAT-specific pins. Checked
against the actual contract before copying anything:

| pin | drags? |
|---|---|
| `collapse` `Ir` floor | **no.** Not declared at all — `check.py` derives it as `ALPHA_IR_PER_WORK * model.work_per_call` and asserts `d(Ir)/d(work) >= alpha` across the two probe shapes. This was the pin most likely to break on a path change, and it does not exist. |
| `identity` | **no.** `[{"a":"unsafe","b":"verus","O0":"norel","O3":"exact"}]` — a property of the two binaries, not of the tree they live in. |
| `miri` | **no.** `pair: [unsafe, verus]`, `sources: [unsafe.rs]` — row-local. |
| `verus.obligations` | **no.** A count over `verus.rs`, which is copied verbatim. |
| `idiom.why` | **yes, and it is the only one — and it dragged harder than the cap allows.** p01's `why` is 12181 chars, of which **11,003 are the shared named-spelling paragraph the gate hard-requires** and only 1177 are row-specific. Only the row-specific half was rewritten (200 words). Gate run 1 `[idiom-named-spelling]` FAILED when the paragraph was dropped; see the rule-6 section above. |

A minimal fresh kernel would have needed a `spec.md` contract, a `model.py`, an
`inputs/gen.py`, five rungs **and a Verus proof** — against one string edit. The
manager's claim stands.

⚠ **One real cost the claim did not mention, and it is not only a path-length
one.** `check.py`'s `domain` string says a record is comparable only against
one with **the same `repo_path_bytes`, the same `envp_stack_bytes` and the
same `tuning_vars`**, and `TASK_114` measured `±7 Ir/call` from a 2-character
`argv` change. Two of those three move through the shim. Measured from the two
**committed** gate records at `TASK_PHP_003` (M1):

```
p01  gate record : repo_path_bytes 33   envp_stack_bytes 3653  nvars 48
ph00 gate record : repo_path_bytes 48   envp_stack_bytes 3686  nvars 49
'/home/apt/repos_common/sec-ladder'                 33
'/home/apt/repos_common/sec-ladder/.temp/php-root'  48   delta +15
```

⚠⚠ **This paragraph said `repo_path_bytes` was 20 bytes longer. It is 15**,
and `repo_path_bytes` **is not the only term that moved**: `nvars` is **+1**
and `envp_stack_bytes` moves too, because `harness-php/gate.py` injects
`PYTHONDONTWRITEBYTECODE=1` into every child. **The mitigation for the
`__pycache__` escape is itself a second domain violation**, and nobody named it
until the review.

⚠⚠⚠ **BUT THE MAGNITUDE `TASK_PHP_003` GAVE FOR IT — `envp_stack_bytes` +33 —
IS NOT THE VARIABLE'S COST, AND THE DIFFERENCE MATTERS.** Measured directly at
`TASK_PHP_004` (`.temp/php4/m1_env_test.py`), same shell, the variable added
and removed:

```
                         bytes  nvars  envp_stack_bytes
without the var           3279     48              3663
with    the var           3305     49              3697
DELTA                      +26     +1              +34
len('PYTHONDONTWRITEBYTECODE=1') + NUL + one 8-byte envp slot = 25 + 1 + 8 = 34
```

**The variable costs exactly +34 and +1 var.** The `+33` was a *record-to-record*
difference between two runs taken in two different shells, i.e. the 34 plus
whatever those shells differed by — and the residue is not constant:

| record | `repo_path_bytes` | `envp_stack_bytes` | `nvars` |
|---|--:|--:|--:|
| `p01`, committed | 33 | 3653 | 48 |
| `ph00`, the record `TASK_PHP_003` measured | 48 | 3686 | 49 |
| `ph00`, re-gated at `TASK_PHP_004` | 48 | **3695** | 49 |

⚠⚠ **`ph00`'s own `envp_stack_bytes` moved 9 bytes between two runs of the same
gate on the same box with no source change**, so the p01→ph00 delta was `+33`
and is now `+42`. **That does not weaken the conclusion, it strengthens it:**
not only is no php marginal `Ir` comparable to any PAT one, **two php runs are
not comparable to each other unless the invoking shell is byte-identical.**
`repo_path_bytes` (+15) is the only one of the three terms that is a property
of the tree rather than of whoever typed the command.

A future agent who "fixed" the path length — by shortening the shim's name,
say — would still not have comparable records and would not know why.

**So this row's marginal `Ir` is NOT comparable to `p01`'s, by the harness's
own rule, and no claim in this repo should compare them.** That is a property
of every php row, not of this one.

## Provenance

`provenance.php_provenance = false`, with a `why`. `harness-php/provenance.py`
accepts a row with no `c_file`/`c_lines`/`extract_sha256` **only** on that
declaration, and rejects a row that merely omits the block — so a missing
provenance is always a defect and never a shrug.

## The trusted-item argument, carried over verbatim from `p01`

⚠ `harness/check.py`'s stage 5c-twin **fails the gate** if this section is absent, and prints it in full on every run. It is reproduced here **byte-identical to `patterns/p01-array-sum/NOTES.md`** because `verus.rs`, `unsafe.rs` and the trusted `get_unchecked` wrapper in this row are byte-identical to p01's — the argument is about *that* code, so re-writing it would be a different argument about the same bytes. ⚠ It is **p01's** argument, not a php result, and like everything else in this row it disappears when the row does.

### The per-item argument only a human can make

Required by `harness/check.py` step 5c-twin since TASK_010, which fails the gate
if this section is missing and **prints it in full on every run**. Three of the
four questions that decide whether a trusted item is sound are outside every
oracle the gate has, and TASK_009_REVIEW demonstrated the worst of them: a body
of `unsafe { let _peek = *v.get_unchecked(i + 1); *v.get_unchecked(i) }` leaves
the contract, the twin, the pins and every Verus stage unchanged and green, while
nothing licenses the `i + 1` read.

SLB-TRUSTED-ARGUMENT verus.rs get_unchecked

(a) **Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*v.get_unchecked(i)` on `&[u64]`; the twin is `v[i]` — the same
operation on the same slice at the same index, with the bound Verus can check.
The standard library documents `get_unchecked(i)` as `index(i)` minus the bounds
check, so the pair is an exact checked/unchecked correspondence rather than an
analogy. A *defensive* twin would not do: it satisfies a weakened `requires` and
then fails the `ensures`, which is the point of lifting the whole contract rather
than the precondition alone.

(b) **Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes as the body stands: one expression, one unchecked read, at
index `i` of slice `v`, and `ensures r == v@[i as int]` names exactly that index
of exactly that slice, so no twin can satisfy it without doing the same read.
That completeness is a property of the body being one line and **nothing
mechanical enforces it** — a second unchecked read the `ensures` never mentions
is invisible to 5a, 5c, 5c-req and 5c-twin. The two measured backstops (TASK_010,
on p02's identical wrapper) are both tests, not proofs: stage 3c identity fails
when only R5 gains the read, because R4 and R5 stop being the same machine code;
and when R4 gains it too, step 8 Miri finds the UB — but only on the input that
actually indexes the last element, 1 of 9 there. Alignment and provenance need no
clause here: the slice comes from a `Vec<u64>`, so it is aligned and wholly
initialised by construction, and `i < v@.len()` is the entire obligation.

(c) **Does the clause mean the same in both configurations?** Yes. `i < v@.len()`
contains no pattern-defined name, only the parameters and vstd's `@`/`len()`, so
there is nothing a `#[cfg]` could redefine. Since TASK_010 the gate additionally
forbids the token `slb_twin` anywhere in this file except the twin's own
`#[cfg(slb_twin)]` attribute, and pins the twin-configuration obligation count
(`verus.twin_obligations`: 8, against 7 shipped) — because a `#[cfg]`-selected
`const` inside a shared `spec fn` was measured passing the whole gate while
shipping `i < v@.len() + 1`.
