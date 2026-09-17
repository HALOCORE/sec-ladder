#!/usr/bin/env python3
"""ITEM 139 -- `F133`(i) across every built row, AS A GREP (the binding form).

    python3 .tasks-php/probes/item139_sibling_census.py
    python3 .tasks-php/probes/item139_sibling_census.py --selftest

⭐ WHY THIS EXISTS. `F133`(i) claims *the R1h's strategy was already present
elsewhere in the same construct*, and `TASK_PHP_061`'s reviewer bound the
generalisation to **one grep per row, NOT ten censuses**. This is that grep.

=============================================================================
⭐⭐⭐ THE RESULT IS NOT A TALLY. IT IS THAT THE QUESTION IS ONLY WELL-FORMED
FOR ONE KIND OF REPAIR.
=============================================================================
Sorting the twelve built rows (plus `ph66`, row 13's candidate) by WHAT KIND OF
CHANGE the R1h is:

  GUARD      the repair adds or copies a TEST at one site.
             ▶ `F133`(i) is well-formed: a sibling site can already have it.
  API-SWAP   the repair exchanges one call for a safer one.
             ▶ Well-formed only at TREE scope -- and the answer FLIPS with the
               scope, which is itself the finding.
  STRUCT     the repair changes the DATA STRUCTURE.
             ▶ ⛔ NOT well-formed. Nothing could have "already been present":
               the fix creates the thing it then uses.
  DELETION   the repair only removes a line.
             ▶ ⛔ NOT well-formed. There is no strategy to locate.
  BUILD      the repair is cross-cutting / build-level.
             ▶ ⛔ NOT well-formed. It is not a code idiom.

⭐ `F133`(i) is well-formed on **8 of 13** rows.
⛔⛔⛔ ITS POSITIVE EVIDENCE IS **4 clear + 1 borderline**, NOT the `7 of 8`
THIS FILE PUBLISHED UNTIL 2026-09-17. The old single `held` column counted
*the repair's ingredient was already in the file* (`ph64`, for another
purpose entirely) and *the siblings are a different construct* (`ph66`,
whose signatures cannot express the choice) AS IF THEY WERE *a sibling
chose the correct spelling* -- and only the third licenses `F133`'s
re-worded rule, `what was CHOSEN, not always what was DISCOVERED`.
▶ `_063` §7.1. ⭐ This does not weaken `F133`; it makes its headline
survivable, because the weaker claim was the one being published.
The row it fails on (`ph97`) fails for a reason worth more than the tally:
**the construct's NORM was the defect** -- 0 of the 5 optional-string parse
sites in `ext/mbstring/mbstring.c` test the pointer before use.

⭐⭐ AND THE POSITIVES HAVE A SHAPE: every one is a SIBLING -- a second site in
the same file doing the SAME JOB, spelled correctly.
  ph03  `php_uuencode` clamps `if (ee > e)`; `php_uudecode`, 60 lines down,
        does not, and the 2014 repair adds exactly that clamp.
  ph07  `mb_strimwidth` guards `if (from < 0 || from > Z_STRLEN_PP(arg1))`;
        `mb_strcut`, 163 lines up, does not.
  ph55  the repair's three lines -- `if (increment_opline) { INC_OPCODE(); }` --
        are ALREADY IN THE FILE, verbatim, in another handler.
  ph64  ⭐ THE PUREST: the `calling` flag the fix reads is ALREADY MAINTAINED
        by the same file (`:157` declares it, `:2108-2109` sets it, `:2135`
        clears it) -- and the comparator the delete uses never consults it.
  ph66  9 of 10 `p->h == h` predicates already use the required-conjunct form.
  ph96  7 of 23 call sites already pass NULL for the unused out-parameter.

⛔⛔⛔ AND `TASK_PHP_062`'s ENGINEER WEAKENED THE HEADLINE FROM INSIDE THE ROW,
WHICH THIS FILE MUST CARRY BECAUSE IT IS A CORRECTION TO ITS OWN CLAIM.
**A "held" count may be counting sites that HAD NO CHOICE.** On `ph66` the nine
siblings are not merely single-kind -- they are **structurally unable** to face
`:464`'s choice: `_zend_hash_add_or_update` takes `arKey`/`nKeyLength` and
nothing else, `_zend_hash_index_update_or_next_insert` takes `h` and nothing
else, and **neither has a parameter that could express the other kind.** Only
`zend_hash_del_key_or_index` has `flag`.
  ✅ SHARPENED: the split is a **type-level fact about one signature**, not a
     statistic about nine siblings.
  ⚠ WEAKENED: those nine are **NOT evidence of intent** --
     `_zend_hash_add_or_update`'s conjunct is there because a string lookup HAS
     to compare lengths before `memcmp`; it would be a bug without it.
  ▶ So `F133`(i) survives on this row but **`ph66` is a WEAK instance of it, not
    the strong one the 9-of-10 ratio suggests.** ⛔⛔ **AND THE SAME DOUBT
    APPLIES TO EVERY `held` COLUMN BELOW**: none of them distinguishes *a
    sibling that chose the correct spelling* from *a sibling that could not have
    spelled it any other way*. **That distinction is not measured anywhere in
    this programme and it is what `F133`(i) actually needs.**

⚠ ONE SITE THIS CENSUS CANNOT SEE, named by the same engineer: `HANDLE_NUMERIC`
(`Zend/zend_hash.h:283-317`) is a TENTH place PHP decides a key's kind, applied
by `zend_symtable_del` BEFORE hashing. It is a macro in a header, not an `if`
in `zend_hash.c`, so the grep misses it by construction. **Said here rather than
left for the next reader to discover.**

⛔⛔ AND THE SCOPE DOES REAL WORK, WHICH `F133`(i) AS WORDED HIDES. On `ph29`
the answer is **NO within the file** (`safe_emalloc` appears 0 times in
`ext/standard/streamsfuncs.c`) and **overwhelmingly YES within the tree** (250
call sites across 78 `.c` files -- it was the codebase's established idiom and
the defective file was the holdout). `ph53` is the same shape. ▶ *"The same
construct"* is not defined, and the answer flips with the definition.

=============================================================================
⚠⚠⚠ WHAT THE `tok` COLUMN IS, AND WHAT IT IS NOT -- READ THIS BEFORE QUOTING
=============================================================================
⛔⛔ `tok` IS A TRIPWIRE, NOT THE CLAIM. It counts one hand-chosen regex in one
file, right now, over the pinned tarball. It does **not** compute the `claim`
column beside it: `ph96`'s claim is *7 of 23 call sites* measured across two
files by `_060`, and this file's token reads **3**; `ph66`'s claim is *9 of 10
predicates* measured by `probes/ph66_djbx33a_collide.py` arms N6-N8, and the
token reads **7**. ▶ **The `claim` column names its own generator. Quote that.**

⭐ The first draft of this file printed one number under a bare heading `n`,
beside a claim it did not compute. That is the defect this programme has caught
most often (`.memory-php/04-process.md` law 6; `F132`: a count is a valid
TRIPWIRE and an invalid ADJUDICATION), and it is recorded here rather than
silently fixed. **`tok` earns its place as a staleness alarm**: if a token that
should be present reads 0, the tarball or the reading has moved.

**MEASURED**: every `tok` is a grep run at display time. Nothing is a literal.
**ADJUDICATED BY HAND**: the `kind`, the choice of token, and every `claim`.
⛔ Those are mine and a reviewer may overturn them.

⚠ NOT AN ADMISSION ARGUMENT and never usable to refuse a candidate
(`CLAUDE.md` rule 6).
"""
import os
import re
import subprocess
import sys

TARBALL = ("/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/"
           "build-5.0.0/php-5.0.0.tar.gz")

# ⭐⭐⭐ `held` IS SPLIT, AND THE SPLIT IS THE POINT (`_063` §7.1, item 139).
# `_061` re-worded `F133` to *"what was CHOSEN, not always what was DISCOVERED."*
# ⛔ The old single `held` column COUNTED BOTH AND THE RULE ONLY LICENSES ONE:
#
#   (A) CHOSEN      a sibling site INSTANTIATING THE SAME CONSTRUCT spelled it
#                   correctly -> authorial choice -> ✅ licences the rule
#   (B) DISCOVERED  the repair's INGREDIENT already existed, for another
#                   purpose -> available material -> ⛔ says nothing about choice
#   (C) NEITHER     the siblings are a DIFFERENT CONSTRUCT -> not evidence
#
# ▶ `same_construct?` is a TYPE/SIGNATURE question answerable from the source.
# ⛔⛔ THE COLUMN THAT WAS *NOT* ADDED, AND THE REFUSAL IS DELIBERATE: `_062`'s
#   engineer proposed *"did this site FACE the choice?"*. It asks about a
#   counterfactual authorial state and **cannot be filled from a repository**.
#   `_063` §7.1(c) refused it and named this substitute. Do not re-add it.
#
# ⚠⚠ THESE TWO COLUMNS ARE HAND-ADJUDICATED, EXACTLY LIKE `kind` AND `claim`,
#   AND THE ADJUDICATION IS `_063`'s REVIEWER'S, NOT MINE -- from the census's
#   own claim column plus two reads of the pristine source. The reviewer said
#   so in terms: *"It is a reading, not a measured column, and I say so."*
#   ▶ CARRIED WITH ITS ATTRIBUTION rather than laundered into a measurement.
YES, NO_, BORDER = "YES", "NO", "BORDERLINE"

# (row, kind, construct file, tripwire regex, (same_construct, chose_correctly,
#  why THAT call), claim + ITS GENERATOR, why)
# ⚠ `construct` is the DEFECT's own file -- the narrowest honest reading of
#   "the same construct", chosen so the scope-sensitivity is VISIBLE rather
#   than hidden by picking a generous boundary per row.
ROWS = [
    ("ph03", "GUARD", "ext/standard/uuencode.c", r"if \(ee > e\)",
     (YES, YES, "⭐⭐⭐ FOR A GUARD REPAIR THE DEFECTIVE SITE IS ITSELF THE "
      "EXISTENCE PROOF that the construct can be spelled without the guard: "
      "`php_uudecode` 46 lines below IS `php_uuencode` without the clamp. "
      "`_063` §7.1(a), from the pristine source."),
     "the clamp is at :80 in php_uuencode; php_uudecode has none (this file)",
     "sibling function, 60 lines apart, same author, same commit"),
    ("ph07", "GUARD", "ext/mbstring/mbstring.c", r"> Z_STRLEN_PP\(arg1\)",
     (YES, YES, "two `mb_*` functions taking the same optional offset "
      "argument; one range-checks it and one does not -- same construct, "
      "opposite spelling."),
     "mb_strimwidth guards at :1900; mb_strcut at :1737 does not (this file)",
     "sibling mb_* function, 163 lines apart"),
    ("ph16", "BUILD", "main/php_network.h", r"FD_SETSIZE", None,
     "n/a — 10 files + configure.in",
     "a build-level repair; there is no single construct to search"),
    ("ph29", "API-SWAP", "ext/standard/streamsfuncs.c", r"safe_emalloc\(",
     None, "⭐ NO in-file (0) / YES tree-wide (250 sites, 78 .c files)",
     "the answer FLIPS with the scope — the defective file was the holdout"),
    ("ph45", "STRUCT", "ext/mbstring/libmbfl/mbfl/mbfl_convert.h",
     r"void \*opaque", None, "n/a — the repair ADDS the field it then uses",
     "a pointer was being stored in an int; the fix changes the struct"),
    ("ph52", "DELETION", "Zend/zend.c", r"zval_dtor\(expr_copy\)", None,
     "n/a — the entire patch is ONE REMOVED LINE",
     "⚠ tok counts the DEFECT here, not a strategy — a different quantity"),
    ("ph53", "API-SWAP", "Zend/zend_compile.c", r"memset\(", None,
     "NO in-file (never adjacent to an emalloc) / YES tree-wide (~100 files)",
     "same shape as ph29: zero-what-you-allocate was a tree-wide convention"),
    ("ph55", "GUARD", "Zend/zend_execute.c", r"if \(increment_opline\)",
     (BORDER, YES, "⚠ THE ONE THE REVIEWER LEFT OPEN. The repair's three "
      "lines exist verbatim at another VM handler -- a sibling EXIT PATH, "
      "so arguably the same construct and arguably just available material. "
      "`_063` §7.1(b) calls it borderline and does not resolve it; neither "
      "does this table. ▶ A BORDERLINE IS PRINTED, NOT ROUNDED."),
     "⭐ the repair's OWN THREE LINES are already in the file, verbatim",
     "another VM handler at :1792 carries the identical block"),
    ("ph56", "GUARD", "Zend/zend_compile.c", r"IS_UNUSED",
     (YES, YES, "the guarded and unguarded cases are ARMS OF ONE `switch` -- "
      "the same construct by construction."),
     "BP_VAR_R / BP_VAR_UNSET already guarded — `_061`'s reviewer",
     "carried from the round that opened F133; not re-measured here"),
    ("ph64", "GUARD", "ext/standard/basic_functions.c", r"->calling|\.calling",
     (NO_, None, "⛔ THE GROUND-TRUTH (B). The `calling` flag exists for "
      "REENTRANCY, in the CALL PATH; the defect is in the DELETE's "
      "comparator, and no other site in the file instantiates that "
      "comparator. `held ✅ YES` here meant *the repair's ingredient was "
      "already in the file*, NOT *a sibling chose the correct spelling*. "
      "`_063` §7.1(a), from the pristine source."),
     "⭐⭐ the `calling` flag is ALREADY MAINTAINED at :157/:2108/:2135",
     "the comparator the delete uses never reads a flag its own file keeps"),
    ("ph66", "GUARD", "Zend/zend_hash.c", r"p->nKeyLength == nKeyLength",
     (NO_, None, "⛔⛔ THE ROW THAT PRODUCED THE WEAKENING, and it is (C). "
      "`_zend_hash_add_or_update` takes `arKey`/`nKeyLength` and nothing "
      "else; `_zend_hash_index_update_or_next_insert` takes `h` and nothing "
      "else. NEITHER HAS A PARAMETER THAT COULD EXPRESS THE OTHER KIND, so "
      "the nine siblings were STRUCTURALLY UNABLE to face `:464`'s choice. "
      "A type-level fact about one signature, not a statistic about nine."),
     "9 of 10 predicates — probes/ph66_djbx33a_collide.py arms N6-N8",
     "⚠ but 0 of the 9 faced :464's problem (both key kinds, one site)"),
    ("ph96", "GUARD", "Zend/zend_object_handlers.c",
     r"zend_call_method_with_1_params",
     (YES, YES, "23 call sites of ONE function; 7 already passed NULL for "
      "the unused out-parameter. Same construct by identity of the callee."),
     "7 of 23 call sites — TASK_PHP_060 §2.3, two files",
     "the repair copied the sibling 99 lines up, it did not invent it"),
    ("ph97", "GUARD", "ext/mbstring/mbstring.c", r'"\|s',
     (YES, NO_, "⭐ THE INFORMATIVE NEGATIVE, AND THE SPLIT KEEPS IT: the "
      "five optional-string parses ARE the same construct, and NONE of them "
      "tests the pointer. Same construct, wrong spelling everywhere -- the "
      "construct's NORM is the defect."),
     "⛔ 0 of the 5 optional-string parses test the pointer (this file)",
     "the construct's NORM is the defect — the file had 5 chances, took 0"),
]


def held_of(adj):
    """PURE. `held` = BOTH, which is what the old single column claimed to be.

    ⛔ `same_construct = NO` yields `--` and NEVER `✅ YES` -- that is the whole
    repair (`_063` §7.1(c) negative (i), the `ph66` ground truth).
    """
    if adj is None:
        return None
    sc, cc, _ = adj
    if sc == NO_:
        return None            # not evidence about choice at all
    if sc == BORDER:
        return BORDER
    return cc == YES


WELL_FORMED = ("GUARD",)


def buckets():
    """PURE over ROWS. -> (well_formed, chosen, borderline, refuted, not_evidence)"""
    wf = [r for r, k, _, _, _, _, _ in ROWS if k in WELL_FORMED]
    h = {r: held_of(a) for r, k, _, _, a, _, _ in ROWS if k in WELL_FORMED}
    return (wf,
            [r for r in wf if h[r] is True],
            [r for r in wf if h[r] == BORDER],
            [r for r in wf if h[r] is False],
            [r for r in wf if h[r] is None])


def member(path):
    """The pinned tarball's copy of `path`, or None if the tarball is absent."""
    if not os.path.exists(TARBALL):
        return None
    r = subprocess.run(["tar", "-xzOf", TARBALL, f"php-5.0.0/{path}"],
                       capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def tok(path, pattern):
    src = member(path)
    return None if src is None else len(re.findall(pattern, src))


def table():
    return [(r, k, p, tok(p, pat), adj, claim, why)
            for r, k, p, pat, adj, claim, why in ROWS]


def selftest():
    bad = []

    def ck(name, cond, why):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}: {why}")
        if not cond:
            bad.append(name)

    if not os.path.exists(TARBALL):
        print(f"  ⓘ EVERY ARM VACUOUS TODAY -- no tarball at {TARBALL}. "
              "THEY ARE NOT PASSING; they could not fire. See "
              "patterns-php/SOURCES.md.")
        print("\nSELFTEST PASS (vacuously -- read the line above)")
        return 0

    rows = table()
    n = {r: t for r, _, _, t, _, _, _ in rows}

    ck("N1", not [r for r, t in n.items() if t is None],
       f"every row's construct file is IN the pinned tarball — missing: "
       f"{[r for r, t in n.items() if t is None] or 'none'}. ⛔ A missing "
       "file would read 0 and manufacture a false NEGATIVE.")

    ck("N2", n["ph55"] >= 1,
       f"ph55's `if (increment_opline)` is in PRISTINE 5.0.0 ({n['ph55']}x) "
       "— the strongest positive, because the repair's own text already "
       "existed verbatim in the same file.")

    ck("N3", n["ph64"] >= 3,
       f"ph64's `calling` flag appears {n['ph64']}x in pristine "
       "basic_functions.c — declared, set and cleared three years before the "
       "fix that finally READS it at the delete site.")

    # ⛔ N4 NON-VACUITY: a token that cannot occur must read 0, or a nonzero
    #   count above means the matcher is broken rather than the token found.
    ck("N4", tok("Zend/zend_hash.c", r"zzz_no_such_token_zzz") == 0,
       "a token that cannot occur counts 0, so the counts above mean FOUND "
       "and not 'the matcher matches anything'.")

    # ⛔⛔ N5 MUST-FIRE: the taxonomy must not be unanimous, or it is a
    #   relabelling. And the well-formed set must not be everything.
    kinds = {k for _, k, _, _, _, _, _ in ROWS}
    wf = [r for r, k, _, _, _, _, _ in ROWS if k in WELL_FORMED]
    ck("N5", len(kinds) >= 4 and 0 < len(wf) < len(ROWS),
       f"kinds={sorted(kinds)}; `F133`(i) well-formed on {len(wf)} of "
       f"{len(ROWS)} — a taxonomy that sorted every row into one bucket "
       "would be a relabelling, not a finding.")

    # ⛔⛔⛔ N6 MUST-FIRE, AND IT IS THE ONE THAT CAUGHT ME: the prose in the
    #   docstring must agree with what the table computes. The first draft
    #   said "7 of 13 well-formed" while the table said 8 — a number asserted
    #   beside a derivation that contradicted it (law 6, in the file whose
    #   whole subject is claims outrunning their evidence).
    _wf, chosen, border, refuted, notev = buckets()
    doc = __doc__ or ""
    ck("N6", f"**{len(wf)} of {len(ROWS)}**" in doc
       and f"**{len(chosen)} clear + {len(border)} borderline**" in doc,
       f"the docstring's headline matches the table: well-formed "
       f"{len(wf)}/{len(ROWS)}, positive evidence {len(chosen)} clear + "
       f"{len(border)} borderline. ⛔ If this fires, the prose was edited and "
       "the table was not, or vice versa.")

    # ⛔⛔⛔ N7 / N8 -- THE TWO §H NEGATIVES `_063` §7.1(c) PRESCRIBED BY NAME,
    #   and they are ground truth, not self-consistency. N7 is the row that
    #   PRODUCED the weakening: before the split, `ph66` read `held = ✅ YES`
    #   off nine siblings whose SIGNATURES CANNOT EXPRESS the choice, and that
    #   single ✅ was 1 of the 7 in the published "7 of 8".
    _adj = {r: a for r, _, _, _, a, _, _ in ROWS}
    ck("N7", _adj["ph66"][0] == NO_ and held_of(_adj["ph66"]) is None,
       f"ph66 reports same_construct={_adj['ph66'][0]} and therefore "
       f"held={held_of(_adj['ph66'])!r} -- ⛔ NOT ✅ YES. A sibling that "
       "CANNOT SPELL the choice is not evidence ABOUT the choice.")

    ck("N8", _adj["ph03"][:2] == (YES, YES) and held_of(_adj["ph03"]) is True,
       "ph03 reports same_construct=YES, chose_correctly=YES -- the positive "
       "control, so N7 is not passing because the column says NO to "
       "everything.")

    # ⛔⛔ N9 MUST-FIRE: the split must have CHANGED the answer, or it is a
    #   relabelling. The old column counted 7; if the new one also counts 7
    #   the repair did nothing and the published figure was never over-stated.
    ck("N9", len(chosen) + len(border) < 7,
       f"the split MOVED the number: {len(chosen)} clear + {len(border)} "
       f"borderline < the published 7. ⛔ If this fires, `same_construct` is "
       "rubber-stamping and the over-statement `_063` found is not repaired.")

    # ⛔ N10 MUST-NOT-FIRE: `held` is still BOTH, so no row may be `held=True`
    #   while its `same_construct` is anything but YES.
    ck("N10", not [r for r, a in _adj.items()
                   if a and held_of(a) is True and a[0] != YES],
       "no row is held=YES without same_construct=YES -- `held` is still the "
       "CONJUNCTION it always claimed to be, not a third independent column.")

    print("\nSELFTEST " + ("FAIL: " + " ".join(bad) if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print("ITEM 139 — was the R1h's strategy already present in the construct?")
    print("⛔ `tok` is a TRIPWIRE (one regex, one file, measured now). It does "
          "NOT compute `claim`. Quote `claim` and its generator.\n")
    print(f"{'row':<6} {'kind':<9} {'tok':>4} {'same':<5} {'chose':<5} "
          f"{'held':<8} claim")
    MARK = {"YES": "✅YES", "NO": "⛔NO", "BORDERLINE": "⚠BORD", None: "  --"}
    for row, kind, path, t, adj, claim, why in table():
        sc, cc, adjwhy = adj if adj else (None, None, None)
        h = held_of(adj)
        hm = {True: "✅ YES", False: "⛔ NO", BORDER: "⚠ BORD", None: "  --"}[h]
        print(f"{row:<6} {kind:<9} {'--' if t is None else t:>4} "
              f"{MARK[sc]:<5} {MARK[cc]:<5} {hm:<8} {claim}")
        print(f"{'':<27}{path} — {why}")
        if adjwhy:
            print(f"{'':<27}▸ same_construct: {adjwhy}")
    wf, chosen, border, refuted, notev = buckets()
    print(f"\n▶ `F133`(i) is WELL-FORMED on {len(wf)} of {len(ROWS)} rows "
          f"({' '.join(wf)}).")
    print(f"▶ ⭐⭐ ITS POSITIVE EVIDENCE IS **{len(chosen)} CLEAR + "
          f"{len(border)} BORDERLINE of {len(wf)}**, NOT `7 of 8`: "
          f"CHOSE {' '.join(chosen)} · BORDERLINE {' '.join(border) or '—'} · "
          f"SAME-CONSTRUCT-BUT-DIDN'T {' '.join(refuted) or '—'} · "
          f"NOT-EVIDENCE-ABOUT-CHOICE {' '.join(notev) or '—'}.")
    print("▶ ⛔ The old single `held` column read `7 of 8` because it counted "
          "DISCOVERED (`ph64`: the repair's ingredient existed, for another\n"
          "     purpose) and NOT-THE-SAME-CONSTRUCT (`ph66`: the siblings' "
          "signatures cannot express the choice) as if they were CHOSEN.")
    print("▶ For the rest the repair changes a STRUCT, DELETES a line, alters "
          "the BUILD, or imports a TREE-WIDE api, and the question has NO "
          "ANSWER rather than a NO.")
    print("\n⚠ Scoping only. Not an admission argument (CLAUDE.md rule 6).")
    sys.exit(0)
