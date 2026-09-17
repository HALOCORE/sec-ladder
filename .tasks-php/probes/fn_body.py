#!/usr/bin/env python3
# =============================================================================
# fn_body.py -- `TASK_PHP_017`'s brace-matching extractor, PROMOTED BECAUSE
# **F50's REGENERATOR CANNOT RUN WITHOUT IT**
#
# ⛔⛔ WHY IT IS COMMITTED, AND IT IS A SECOND-ORDER LAW-11 CASE. It was written
# as `.temp/php17/r1h/fn.py` and no finding cites it, so the law-11 census does
# not see it. But `probes/refetch_upstream002.sh` -- which **F50 names as the
# script that regenerates all of its evidence** (`RECAP_PHP.md:8335`) -- opens
# with `FN=../php17/r1h/fn.py` and calls it once per tag. ▶ **Promoting the
# regenerator and leaving this in deletable scratch would have produced a
# committed generator that cannot generate**: exactly the shape `PROMOTE_001`
# left behind when it promoted two probes whose caches made them crash, one
# level further out. ⓘ Same call `probes/sweep_cg.sh` got, for the same reason.
#
# Promoted by `TASK_PHP_064`, 2026-09-17, repo at commit f4bda71. RENAMED from
# `fn.py`: `.tasks-php/` already has a `refetch.sh` that is a DIFFERENT script
# from the one promoted beside this, and a two-character basename in a flat
# `probes/` directory is how that collision happens a second time.
#
# WHAT IT DOES: given a C file and a definition token, brace-match the body and
# print `line · bytes · sha256[:16]`; `--body` prints the body. ⭐ It is F35's
# rule in code -- *ask about a FUNCTION, not about text* -- and the reason
# `refetch_upstream002.sh` can hash `PHP_FUNCTION(mb_strcut)` across 19 tags
# when a `grep` for the guard's text MISSES 5.3.0, which spells it differently.
#
#   python3 .tasks-php/probes/fn_body.py <file.c> '<token>' [--body]
#
# ✅ NEEDS NOTHING BUT ITS ARGUMENT. Pure stdlib, reads one file, writes
# nothing. ⛔ WHAT IS OWED: **it has NO must-fire negatives.** It is filed
# `negatives="none", kind="tool"` in `.tasks-php/checkers.py` and that is
# honest, not a pass -- the `^token` + `\s*\{` heuristic has never been shown
# failing on a prototype, a macro-generated definition or a K&R header, and
# every number `refetch_upstream002.sh` prints goes through it.
# =============================================================================
"""Extract a C function BODY by its DEFINITION token, brace-matched.
Ask about a FUNCTION, not about text (RECAP_PHP F35 / .memory-php/00)."""
import re,sys,hashlib
def body(path, tok):
    src=open(path,encoding='utf-8',errors='replace').read()
    # the DEFINITION is the occurrence at column 0 followed (after optional ws/newlines) by '{'
    for m in re.finditer(r'^'+re.escape(tok), src, re.M):
        rest=src[m.end():]
        k=re.match(r'\s*\{', rest)
        if not k: continue
        i=m.end()+k.end()-1
        d=0
        for j in range(i,len(src)):
            if src[j]=='{': d+=1
            elif src[j]=='}':
                d-=1
                if d==0:
                    return src[:m.start()].count('\n')+1, src[m.start():j+1]
    return None
if __name__=='__main__':
    r=body(sys.argv[1], sys.argv[2])
    if r is None: print("NOT FOUND"); sys.exit(1)
    ln,b=r
    print(f"--- {sys.argv[1]} :: {sys.argv[2]}  line {ln}  {len(b)} B  sha256 {hashlib.sha256(b.encode()).hexdigest()[:16]}")
    if '--body' in sys.argv: print(b)
