# TASK_PHP_027 — build `ph29-recvfrom-alloc`, row 4

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_027_REPORT.md` — **write the FILE** (rule 10).

Read `.tasks/PROTOCOL.md`, **`.memory-php/`** (authoritative), `PLAN_PHP.md`
§3–§4, **`.tasks-php/PROTOCOL_PHP.md` in full — §B (the allocator rule) is this
row's centre of gravity, and §G/§H are new**, `patterns-php/SOURCES.md`, and
**`patterns-php/ph16-fdset-index/` in full** — row 3, built yesterday, is your
template. Then `patterns-php/CATALOGUE.md`'s `ph29` block,
`.tasks-php/UPSTREAM_001.md` §4, and `RECAP_PHP.md` F46 (which **closed this
row's C-side question by measurement** — read it before doubting anything).

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **No `git add` / `git commit`.** Never touch `.web/`.
⚠ Scratch under `.temp/php27/`. **Never `/tmp`.** Reuse `.temp/php25/` (row 3)
and `.temp/php4/real_size_probe.c` (the `REAL_SIZE` probe that settled F46).

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`8/0`**, first and last.

---

## §0 Why this row, and not a temporal one

**All three built rows are SPATIAL** (`ph03`/`ph07` in `S1`, `ph16` in `S2`), and
the **type and temporal axes have zero.** That is the programme's largest
unmeasured gap and I considered jumping straight to it.

⭐ **`ph29` first anyway, for one reason that is about the LATER rows:** it is
**one of only two rows in the corpus where the `_emalloc` truncation is
load-bearing** (`PLAN_PHP.md` §4.3). Under plain `malloc`, `malloc(2^63)` simply
fails and PHP exits — **the defect vanishes.** So this row **cannot pass without
`common-php/emalloc_shim.h` being faithful**, which makes it the only honest
proof that the shim is right. ⚠⚠ **The temporal axis — 31 rows of
use-after-free, double-free and refcount defects — leans on that shim
throughout.** Proving it on a row that cannot pass without it, *before* an axis
that merely links it, is worth one task.

## §1 The row, verified at source by the manager

`ext/standard/streamsfuncs.c`, pristine 5.0.0 (sha256 `5783e0c0…d6919`).
`PHP_FUNCTION(stream_socket_recvfrom)` opens at `:300`:

```c
	long to_read = 0;                                                   /* :304 */
	...
	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "rl|lz",       /* :309 */
	        &zstream, &to_read, &flags, &zremote) == FAILURE) { ... }
	...
	read_buf = emalloc(to_read + 1);                                    /* :321 */
```

✅ **`:309` and `:321` are exact, and `to_read` comes from USERLAND, not from the
socket.** ⚠ Tier `narrowed` is already correct and consistent both ways: the
site is inside a `PHP_FUNCTION` frame (the M4 test) **and** a `zend_parse_parameters`
wrapper comes off (`PLAN_PHP.md` §4's definition). ⭐ **Unlike `ph16`, the two
agree here** — say so, and do not re-litigate it.

**The mechanism is CLOSED and MEASURED** (F46, `.temp/php4/real_size_probe.c`,
replicating `zend_alloc.c:129/132/135/182/201` verbatim): `to_read = LONG_MAX` →
`size = 2^63` → **`real_size = 0`** → a header-sized `malloc` **succeeds**.
⚠⚠ **The truncation is `REAL_SIZE` at `zend_alloc.c:129`, NOT `emalloc`'s
signature**, and ⚠ **the row is 64-bit-ONLY** — the manager hypothesised the
exact opposite and was wrong in all three limbs (F36, retracted). **Do not
re-derive this; do re-run the probe once and paste it.**

**▸ trigger: `stream_socket_recvfrom($s, 4294967295)`** — any `to_read` with
`to_read + 1 ≡ 0 (mod 2^32)`. ⚠⚠ **PREFER THIS TO `PHP_INT_MAX`**, whose
`to_read + 1` is **signed-overflow UB the compiler may fold**, so a kernel built
to it can behave differently at `-O0` and `-O3` for a reason that is not the
defect. ⭐ It also **zeroes `CHECK_MEMORY_LIMIT`'s accumulator** and **reaches the
second truncation** (`zend_alloc.h:53`'s `size:31`) — three strengthenings, all
from F46.

## §2 R1h — ⚠ TWO STAGES, AND THE ROW MUST CHOOSE AND DEFEND

```
5.0.0   read_buf = emalloc(to_read + 1);                     long to_read, unchecked
5.1.0   if (to_read <= 0) { RETURN_FALSE; }   <-- stage 1    then emalloc(to_read + 1)
5.3.0   if (to_read <= 0) { RETURN_FALSE; }   then safe_emalloc(1, to_read, 1);  <-- stage 2
```

**Fix windows: 5.0.0 → 5.1.0** for the guard, **5.2.0 → 5.3.0** for the wrapper
(`UPSTREAM_001.md` §4). ⚠⚠ **So *"the fix"* is a choice, exactly as `ph03`'s two
hunks were, and `ph03` is the precedent for how to present it.** ⚠ **Verify both
at the commit, not at the column** — `PROTOCOL_PHP.md` §F5(iii), and item 45 is a
live instance of that column naming a fix **in the wrong function**.

⭐ **The interesting question, and I want it answered rather than assumed:**
stage 1 alone makes the *defect* unreachable; stage 2 makes the *arithmetic*
safe. **Are they the same rung?** If R1h is stage 1 the row measures the cost of
a comparison; if stage 1 + stage 2 it measures the cost of a checked multiply.
**Publish whichever you ship, labelled, and say what the other one costs.**

## §3 ⚠⚠⚠ The allocator shim is LOAD-BEARING — this is the row it exists for

`PROTOCOL_PHP.md` §B, and §B2's rule that **the shim is a HEADER the row
symlinks into `c/`**. ⚠ **Under plain `malloc` this row's defect DOES NOT
EXIST** — `malloc(2^63)` fails, PHP exits at `zend_alloc.c:191`, and there is
nothing to measure.

- **State, in `NOTES.md`, what the shim reproduces and what it does not.**
  ⚠⚠ **F6 is the standing warning: the allocator shim INVENTED DEFECTS once
  already**, in the file written to prevent that. **This row is where its
  fidelity is finally tested by something that fails without it.**
- ⚠ **A must-fire and a must-NOT-fire control on the shim itself** (§H): the
  adversarial input must fault **with** the shim and must be **clean** under
  plain `malloc` — *and the clean case is the interesting one, because it is the
  row disappearing.* **Both, run, output pasted.**

## §4 ⚠ Check `_FORTIFY_SOURCE` on this row — F56, one day old

Ubuntu's gcc injects **`-D_FORTIFY_SOURCE=3` whenever it optimises**, and it
silently put a bounds check into `ph16`'s `FD_SET` worth **+60.6 %**. ✅ Measured
clean for `ph03` and `ph07` (no `_chk` symbols at `-O3`). ⚠⚠ **`ph29` is NEW and
allocation-shaped, and level 3 uses `__builtin_dynamic_object_size`, which tracks
allocation sizes level 2 cannot** — **so check it, do not inherit the result.**
`nm -u` the kernel object at `-O3` and look for `__*_chk`. ⚠ **Use a runtime
value, never a literal**: a constant lets the compiler prove the bound and elide
the check, which is a setup that encodes the answer (F52).

## §5 Deliverables, rules

- **The fixture rule** (`PROTOCOL_PHP.md` §A2a, both limbs) and the `model.py`
  independence rule. ⚠ `ph03` shipped for a full task with `model.py` and
  `verus.rs` computing different functions.
- ⚠⚠ **`PROTOCOL_PHP.md` §H — your `controls/*.py` are VALIDATORS.** Each ships
  with a must-fire **and** a must-not-fire case, run. A green gate *exercises* a
  control; it does not *attack* it.
- **Write `spec.md`'s hashed `why` LAST**, re-deriving every numeral from the
  record you are shipping, and say in your report that you did. ⚠ `ph07`'s was a
  **whole pre-rebuild snapshot — nine stale numerals, every verdict still right**
  (F54), which is the configuration no check here can see.
- ⚠ **`controls/spellings.py` is NOT this task's job.** Two of three rows owe it
  and carrying it turned row 3 into two tasks; **`TASK_PHP_028` will discharge
  the debt across all rows at once.** **Declare the debt and move on.**
- ⚠⚠ **`grep -a` ALWAYS**; ask about a FUNCTION, not text. **A probe whose SETUP
  encodes the answer evaluates fine and is wrong** — five shapes now (F52).
  **Paste output you actually saw**, not what the probe was meant to print.
- ⚠ `timeout <N> <cmd>`; **no `pkill`/`killall`**; **no `until … sleep` waiter
  loops** — foreground `sleep` is blocked here so they return instantly and read
  like a completed wait, and backgrounded they match their own shell and spin
  forever (item 44).

## §6 What I am least sure of

1. ⚠⚠ **That the shim's fidelity survives being tested.** F6 says it invented
   defects once. **If this row can only be made to fault by a shim behaviour the
   real `zend_alloc.c` does not have, that is a MAJOR finding and the row must
   stop and report it** — not paper over it. `PLAN_PHP.md` §4.3 rests on this.
2. ⚠ **That stage 1 and stage 2 are one rung** (§2). I genuinely do not know,
   and `ph03`'s answer may not transfer.
3. ⚠ **That `narrowed` is right when the wrapper coming off is
   `zend_parse_parameters` itself.** The whole defect is *"a `long` from
   userland"*, and the parse is how it gets there. **If lifting it faithfully
   means the blob supplies the `long` directly, say whether that is still the
   same defect** — `ph94` had to declare exactly this as a `projection`.
