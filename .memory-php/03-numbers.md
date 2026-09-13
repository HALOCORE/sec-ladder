# `.memory-php/03-numbers.md` — what may and may not be compared

> ⚠ **`.memory-php/` is the AUTHORITATIVE layer for the PHP programme, and it
> SUPERSEDES any task report it contradicts** (`.tasks/PROTOCOL.md` rule 9).
> Only findings that have survived a full engineer→reviewer cycle are here.
>
> ⚠⚠ **SCOPE: this carries ONLY what is php-specific.** The PAT `.memory/`
> 00–06 applies unchanged — same harness, same bench rules, same measurement
> discipline, same Verus notes. **Do not restate any of it here; two copies of
> one rule is how both go stale.**
>
> The narrative, the open items and findings **F1–F101** live in `RECAP_PHP.md`
> (⚠ this said *F1–F41* for **forty-nine** findings, then *F1–F90* for **eleven** more — `PROTOCOL.md` rule 13, **and it has now rotted THREE TIMES.** ✅ **`.tasks-php/boxcheck.py` CHECKS THIS LINE against the actual highest finding as of 2026-09-13, so it is the last time.**
> **Count it yourself: `grep -c '^### F' RECAP_PHP.md`.**)
> ⭐ **And the statistic decision — which column every row publishes in — is
> `.tasks-php/STATISTICS_001.md`, committed. It was in gitignored `.temp/`.**

---


- ⚠⚠ **NEVER quote a `phNN` figure against a `pNN` one**, anywhere, including
  in prose. `repo_path_bytes` is **15 B** longer through the shim and
  `gate.py`'s `PYTHONDONTWRITEBYTECODE=1` adds **+34** and one env var.
- ⚠⚠ **And no two php runs are comparable to each other** unless the invoking
  shell matches: `ph00`'s own `envp_stack_bytes` moved **3 686 → 3 695** between
  two runs of the same gate with no source change. **Measure a mechanism; never
  difference two records taken in two shells and call the result its cost.**
- ⚠⚠ **`0 STALE` does NOT mean "everything is pinned".** `measure.py::_compare`
  iterates the **recorded** keys, so an **added** file is invisible — it has no
  key, so it cannot be stale. It means *every source that was pinned still
  matches*. What closes the gap is the **preflight**, not the digest. ⚠ This is
  a `harness/` property and affects all 33 PAT rows identically. (F14.)
- **The allocator is pinned by an UNCONDITIONAL symlink** — every php row
  carries `c/emalloc_shim.h` whether or not it allocates. ⚠ **Do not reintroduce
  a detector**: *"does this row use the allocator?"* was answered twice (a string
  search, then `gcc -MM`) and bypassed twice. **The question is not meant to be
  load-bearing.** (F10, F16.)
