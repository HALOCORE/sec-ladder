# `.memory-php/00-corpus.md` — the citation base, and what is authoritative

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


- **PHP 5.0.0, the pinned tarball**, sha256 `5783e0c0…d6919`, 5 595 997 B,
  3 815 entries. Read recipe and per-file manifest: `patterns-php/SOURCES.md`.
  ⚠ **Every extracted tree on this box is patched to some degree — 8 of 12 match
  the tarball, 4 do not.** Citations resolve against the **tarball**, never a
  build tree.
- ⚠⚠ **`index.csv`'s `c_file_line` is AUTHORITATIVE. The reproducer `.php`
  header comment is NOT** — six of them describe **4.0.2**, and `CRASH-017.php`
  self-labels as such. Following one **inverts the verdict**. (F2, found
  independently by two miners on two axes.)
- ⚠ **Three corpus `root_cause_id` strings are known wrong**, not merely
  imprecise: CRASH-053 (*"unchecked `make_real_object`"* — the check IS there),
  CRASH-033, and CRASH-071. **The label is a hint; the line is the claim.**
- **The corpus is 166 rows.** `patterns-php/CATALOGUE.md` catalogues 91.
- ⚠ **`.temp/san_tests/`'s ASan census cannot speak to the spatial axis.**
  3 199 reports, and **zero of the 2 520 spatial ones fault in `Zend/` or
  `ext/standard/`** — 2 156 are inside `libmysqlclient.so.14`'s XML charset
  parser, a different shared object. Every spatial `hotness` field is
  **reasoned**, and the census is not evidence for it. (F9.)
