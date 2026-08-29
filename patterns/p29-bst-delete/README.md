# p29 — binary search tree delete, with a cached lookup result

**The project's second temporal row, and it is `p27`'s row with one term added
to the safety line.**

| | |
|---|---|
| **Bug** | CWE-416 use-after-free, reached through CWE-672. A `FIND` caches the address of the record it found; a later `USE` reads through it without asking whether the record is still there or still the same record. |
| **Safety line** | `if (g_saved != NULL && live[g_slot] == 1 && tab[g_slot][0] == g_key)` — **two conjuncts**, where `p27`'s hardened cell adds **one**. |
| **Rungs** | R1 `c/kernel.c` · R1h `c/kernel_hardened.c` · R2 `safe_naive.rs` · R3 `safe_tuned.rs` · R4 `unsafe.rs` · R5 `verus.rs` |
| **R5** | `25 verified, 0 errors` (twin config `30 / 0`), TCB **7 trusted items** — the same seven `p27` ships. The full functional refinement: `ensures r == bst_fold(buf@, off, len)`. |
| **Headline** | **One omitted line, two bug classes, selected by the DEGREE of the deleted node — and the two conjuncts that catch them fail in different currencies.** |

## The row in one table

Deleting a key does one of two things to the record that held it:

| victim | the splice | R1's cached read | who sees it |
|---|---|---|---|
| 0 or 1 child | unlinks and **frees** it | `heap-use-after-free`, value **not reproducible** | ASan · Miri · `Option` · `PointsTo` — all four |
| 2 children | copies the successor's key/val **into** it, frees the **successor** | in-bounds read of a **live** allocation whose occupant changed; **stable** wrong answer | **nothing** |

Every mechanism in the *who sees it* column is a mechanism about the
**allocation**, and the second bug class never touches the allocation. That is why the safety line
needs a second conjunct — an **occupant-identity** test — and why that conjunct
is an ordinary value equality with nothing linear about it.

## Where to look

- `c/kernel.h` — the kernel contract in pseudocode, and the argument for every
  defensive conjunct the rungs carry.
- `c/kernel.c` vs `c/kernel_hardened.c` — **the diff is the row.**
- `spec.md` — the machine-readable contract and the reasoning behind each pin.
- `NOTES.md` — every measurement, including the two design questions
  `TASK_139` settled and the arms that lost.
- `controls/arms.py` — the losing safety lines, derived from the shipped
  `c/kernel.c` by substitution so they cannot drift, built and scored.
- `controls/proof_mutants.py` — the R5 mutation battery, including the attack
  arm that puts `c/kernel.c`'s bug into the proof and requires it to be rejected.
- `controls/miri_arms.py` — what Miri sees and what it does not, on the same
  source with the safety line deleted. The gate cannot measure this: it runs the
  rung that is right.
- `controls/repro.py` — `p25`'s "nondeterministic R1" kill, asked of both bug
  classes; publishes the invariant and no pinned count.
- `verus.rs` — the proof. `walk` is the refinement lemma; `wf`'s last two
  conjuncts are `p29`'s own.
