# TASK_PHP_017_REPORT — adversarial review of `ph07`, and of the manager's four surveys

**Role:** research reviewer, `PROTOCOL.md` rule 1 — I did not build this row.
**Verdict in one line:** ⚠⚠⚠ **the row's headline is REFUTED BY CONSTRUCTION** —
an in-contract safe-Rust re-slice takes R3 from **+13.50 %** to **+2.62 %** over
R4 and deletes the bounds check from *both* walks — **and everything else about
the row survives an unusually hard attack**, including a proof that killed
**18 of 18** mutants.

⚠ **Reconciliation of the running count is the manager's job.** Launched from
**74**; I do not carry it forward.

**Bracket.** Open (first two commands) and close (last two), both green:

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE
$ python3 harness-php/gate.py --tool measure --check-stale
6 record(s) examined, 0 STALE
```

`git status --porcelain` at the close: **empty**. No file under `harness/`,
`common/`, `patterns/`, `results/`, `pilot/`, `.web/`, `.memory-php/`,
`patterns-php/` or `RECAP_PHP.md` was created, edited or deleted. No `git add`,
no `git commit`. Scratch: `.temp/php17/` (generators kept, binaries and
callgrind dumps deleted, `spell/REBUILD.sh` and `r1h/REFETCH.sh` regenerate
every one). `.temp/php12–16/` were read, never written.

---

# §1 THE ROW

## 1. ⚠⚠⚠ BLOCKER B1 — the headline is refuted. A safe re-slice removes the check.

**The claim under attack** (`NOTES.md` §8b, `safe_tuned.rs:12-19`, report §6,
`RECAP_PHP.md` F41, START HERE box line 57):

> *"R3's two walks are BYTE-FOR-BYTE R2's … no reslice lets LLVM discharge
> `n < s.len()` … The row's cost sits exactly where safe Rust cannot reach it."*

**It is wrong, and the counter-example is three characters of Rust.** After
`cb3cca21b345` hunk (a) the kernel knows `frm <= slen` and `s.len() == slen+1`;
the start walk reads only at `n <= frm` and the end walk only at `n <= k < slen`.
So both walks' reads are covered by a slice whose length the compiler can see:

```rust
let w0: &[u8] = &s[..=frm];          // one check, hoisted OUT of the loop
let mut n: usize = mbtab(w0[0]) as usize;
let mut start: usize = 0;
while n <= frm { start = n; let m: usize = mbtab(w0[n]) as usize; n = n + m; }
...
    let w1: &[u8] = &s[..=k];
    end = start;
    while n <= k { end = n; let m: usize = mbtab(w1[n]) as usize; n = n + m; }
```

**Measured** (`.temp/php17/spell/`, `-O3 isolated`, the harness's own rustc
flags, kernel-exclusive `Ir` via the pinned callgrind). My pipeline first
reproduced the shipped R3 **exactly** — `50,735,617 / 25000 = 2029.42` and
`169,914,706 / 12000 = 14159.56`, against the record's `2029.4 / 14159.6`:

```
cell                                             Ir/call small Ir/call large  Ir/win-byte fixed/call    vs R4
safe_naive (R2, shipped)                                2818.3       19669.9       4.7860      171.6  +57.67%
safe_tuned (R3, shipped)                                2029.4       14159.6       3.4451      124.3  +13.50%
unsafe     (R4, shipped)                                1796.2       12483.8       3.0354      117.6   -0.00%
-------------------------------------------------------------------------------------------------------------
v1  reslice `&s[..=frm]`/`&s[..=k]`                     1845.6       12813.7       3.1151      123.0   +2.62%
v2  reslice `&s[..frm+1]`/`&s[..k+1]`                   1845.6       12813.7       3.1151      123.0   +2.62%
v4  `s.get(n).unwrap_or(&0)`                            2098.4       14669.1       3.5702      124.0  +17.62%
v6  safe_naive + the same reslice                       2635.3       18324.9       4.4560      171.1  +46.80%
```

**Zero `unsafe`. Identical checksums on all seven inputs**, adversarial cells
included, against `model.py`'s `expected` and against the shipped R4:

```
adversarial-empty.bin      AGREE base=11424172624523374464 v1=11424172624523374464 unsafe=11424172624523374464
adversarial-nowin.bin      AGREE base=0 v1=0 unsafe=0
adversarial-offbyone.bin   AGREE base=11424172624523374464 v1=... unsafe=...
adversarial-silent.bin     AGREE   adversarial-wild.bin AGREE
large.bin                  AGREE base=7546772105060097026 v1=... unsafe=...
small.bin                  AGREE base=1771235065085513576 v1=... unsafe=...
```

**The mechanism, off `objdump`** — my loop census reproduces `23-loops.log`'s
figures for the shipped rungs exactly (R2 `9,1`/`8,1`; R4 `7,0`/`6,0`), which is
what licenses the comparison:

```
shipped R3 (base)  start walk 9 insns cond-exits=1   end walk 8 insns cond-exits=1
v1                 start walk 7 insns cond-exits=0   end walk 7 insns cond-exits=0
shipped R4         start walk 7 insns cond-exits=0   end walk 6 insns cond-exits=0
```

**v1's start walk is instruction-for-instruction R4's** — same seven opcodes,
different register allocation:

```
shipped R3, start walk          v1, start walk               shipped R4, start walk
  cmp    %rcx,%rax   <- CHECK     movzbl (%rdi,%r9,1),%r8d     movzbl (%rax,%r11,1),%r10d
  jae    <panic>     <- CHECK     movzbl (%r8,%rax,1),%r8d     movzbl (%r10,%r9,1),%r10d
  movzbl (%rdi,%rax,1),%r9d       add    %r9,%r8               add    %r11,%r10
  movzbl (%r9,%rsi,1),%r9d        mov    %r9,%r13              mov    %r11,%r13
  add    %rax,%r9                 mov    %r8,%r9               mov    %r10,%r11
  mov    %rax,%r13                cmp    %rdx,%r8              cmp    %rsi,%r10
  mov    %r9,%rax                 jbe    <top>                 jbe    <top>
  cmp    %rdx,%r9
  jbe    <top>
```

**It is IN CONTRACT, by the gate's own matcher.** I imported
`harness/check.py::spelling_matches` (read-only) and ran ph07's declaration
against each variant:

```
=== REQUIRED (rust spellings) ===
  `while n <= frm`             base=OK  v1=OK  v2=OK  v3=MISS v4=OK
  `MBTAB`                      base=OK  v1=OK  v2=OK  v3=OK  v4=OK
  `if k >= slen`               base=OK  v1=OK  v2=OK  v3=OK  v4=OK
  `s.len() - 1`                base=OK  v1=OK  v2=OK  v3=OK  v4=OK
=== FORBIDDEN (must NOT match) ===
  `if (n >= from)`                       base=clean v1=clean v2=clean v3=clean v4=clean
  `p - string->val < (int)string->len`   base=clean v1=clean v2=clean v3=clean v4=clean
  `frm = slen`                           base=clean v1=clean v2=clean v3=clean v4=clean
```

v1 and v2 satisfy every backticked Rust spelling the shipped R3 satisfies and
violate none. (`v3`, which rewrites the guard as `while n < lim0`, is out of
contract and I am not offering it. It measures the same.)

⚠ **On `forbidden[1]`'s English** — *"the in-loop bound a reader adds on
sight … the bound is computed and then not consulted until `:1227`"*. The
re-slice adds **no in-loop bound**; it re-expresses, once, outside the loop, a
fact `cb3cca21b345` hunk (a) has *already* established two lines above, and it
cannot panic for that reason. It does not touch R1, which has no hunk (a) and
no re-slice available. **The row's finding — that `mbfl_strcut` computes a bound
and does not consult it — is untouched. What falls is the claim about safe Rust.**

**The mechanism predicts the measurement with no fitting**, using the row's own
step rates:

```
start-walk steps/window byte = 0.441/3.5 = 0.126
end-walk   steps/window byte = 0.291/3.5 = 0.0831
base->v1 deletes 2 insns from the start walk + 1 from the end walk -> 0.3351 predicted
measured 0.3300  -> agreement 1.5%
v1->R4 residue is the ONE surviving `mov` in the end walk: 0.0831 predicted vs 0.0797 measured
```

⭐ **So the whole R3→R4 gap decomposes exactly: 80.6 % of it was a safe-Rust
spelling, and the entire remainder is one register move.**

### What this changes, and what it does not

- ❌ **RETRACT**: *"no safe spelling removes that check"*, *"R4's entire gain
  over R3 is the two walks"*, *"the row's cost sits exactly where safe Rust
  cannot reach it"* — `NOTES.md` §8b, `safe_tuned.rs:12-19`, report §6,
  `RECAP_PHP.md` F41 ¶2 and START HERE line 57.
- ✅ **KEEPS STANDING**: *"a variable-stride cursor is not an iterator"* is true
  — there is no `Iterator` whose `next()` is this step, and none of my variants
  is one. The false step is the inference from *"not an iterator"* to *"no safe
  spelling"*. **Re-slicing is not iteration; it is telling the compiler the
  invariant the guard already proved.**
- ⚠ **DO NOT RE-SHIP R3.** `.memory/02-bench-rules.md` — *never re-ship a rung
  because a cheaper in-contract spelling was found*. The shipped cell stays and
  is published as a **`fixed-R4 bound`** with v1 beside it as the
  **cheapest-found in-contract R3**, both labelled. ⭐ **This is F39's own
  prescription, and `ph07` is now the first php row that can discharge it** —
  the spread exists, it is measured, and it cost one afternoon rather than a
  `controls/spellings.py`.
- ⚠ **AND IT MOVES THE OTHER WAY FROM F39's PRIOR.** F39's PAT table is
  R4-side; this is R3-side, and it moves **for** safe Rust. See §2.4.

**Not done:** v1 has not been through `harness-php/gate.py`, has no `O0`/`whole`
cells, and has no Verus twin (it does not need one — it is an R3). It is a
measured counter-example, not a shipped rung.

---

## 2. ✅ THE PROOF — attacked hard, survived. 18 of 18 mutants killed.

Reproduced independently: **`21 verified, 0 errors`** plain and
**`24 verified, 0 errors`** under `--cfg slb_twin`.

I wrote **18 mutants of my own** (`.temp/php17/mut/mutants.py`, anchor-validated
before any edit so a silent no-op is reported rather than run). **17 must-FAIL,
all failed; 1 must-PASS, passed. Zero unexpected.**

```
spec_walkstart_ge    FAIL FAIL ok   20 verified, 1 errors   walk_start exit n>frm -> n>=frm
spec_walkend_ge      FAIL FAIL ok   20 verified, 1 errors   walk_end exit n>k -> n>=k
spec_fold31          FAIL FAIL ok   20 verified, 1 errors   fold_out multiplier 31 -> 33
spec_tally_mask      FAIL FAIL ok   20 verified, 1 errors   tally_of mask !7 -> !3
spec_headu32_shift   FAIL FAIL ok   20 verified, 1 errors   head_u32 top shift 24 -> 25
spec_guardfrom_sign  FAIL FAIL ok   20 verified, 1 errors   guard_from slen-d -> slen+d
spec_guardlen_sub    FAIL FAIL ok   20 verified, 1 errors   guard_len a-d -> d-a
spec_hunkA_ge        FAIL FAIL ok   20 verified, 1 errors   strcut_fold hunk-(a) f0>slen -> >=
spec_kge_gt          FAIL FAIL ok   20 verified, 1 errors   strcut_fold k>=slen -> k>slen
spec_cap             FAIL FAIL ok   20 verified, 1 errors   tally arg cnt+8 -> cnt+16
exec_kge_gt          FAIL FAIL ok   20 verified, 1 errors   exec `if k >= slen` -> `>`
exec_walk_lt         FAIL FAIL ok   20 verified, 1 errors   exec `while n <= frm` -> `<`
exec_cap16           FAIL FAIL ok   20 verified, 1 errors   exec cap = cnt+8 -> cnt+16
exec_hunkb_gone      FAIL FAIL ok   20 verified, 1 errors   delete ONLY hunk (b) from exec
tcb_get_noval        FAIL FAIL ok   17 verified, 4 errors   get_unchecked's ensures dropped
tcb_vset_weak        FAIL FAIL ok   20 verified, 1 errors   vset ensures weakened to v@[i]==x
proof_no_foldshift   FAIL FAIL ok   20 verified, 1 errors   delete the lemma_fold_shift call
proof_rlimit_default PASS PASS ok   21 verified, 0 errors   drop rlimit(30) -- plain still verifies
```

**The postcondition says something.** Ten of the seventeen are *spec-side* edits
— they change what `strcut_fold` means without touching the exec code — and the
proof rejects every one. `r == strcut_fold(buf@, off, len)` pins the walks' exit
tests, the fold's multiplier, the allocator tally's alignment mask, the header
decode, both caller clamps and the `k >= slen` shortcut. **This is not a
memory-safety-only postcondition.**

⭐ `tcb_vset_weak` is the interesting one: weakening `vset_unchecked`'s
`ensures` from the whole post-state `old(v)@.update(i,x)` to
`final(v)@[i as int] == x` **breaks the proof**. So the strong form the module
comment defends on soundness grounds is *also* load-bearing for this file — the
comment understates its own item.

### `lemma_mbtab_matches` — the specific claim, verified

> *"the 256-entry table costs the proof one lemma with no `assume` and no sixth
> trusted item."*

**CONFIRMED.**

```
$ grep -n 'assume|external_body|external\b|assume_specification|admit' verus.rs
316,346,372,398,409:  #[verifier::external_body]      <- five, and only these
(zero `assume`, zero `assume_specification`, zero `admit`)
```

Five `external_body` items; `spec.md`'s `verus.items` independently lists the
same five. `NOTES.md` §10c **reconciles this itself** — *"That is five
`external_body` items and four trusted contracts"* — so the tally is accurate
and the "no sixth" is measured against the right baseline. **Recount agrees.**

The lemma is genuinely load-bearing: the row's own `notable` mutant (one MBTAB
entry changed) dies at exactly `assert(mbtab_matches_upto(256)) by
(compute_only)`. All four shipped negatives re-ran clean:

```
noguard    expect FAIL got FAIL   20 verified, 1 errors      ok
nopos      expect FAIL got FAIL   p.rs:159 compute_only      ok
notable    expect FAIL got FAIL   p.rs:159 compute_only      ok
noconsume  expect PASS got PASS   21 verified, 0 errors      ok
verus.rs sha256 unchanged: 28811d6d6f45c3b2
```

### `broadcast use` scoping — did it weaken a spec? **No, and it cannot.**

`broadcast use` only *adds* facts to a proof context. Scoping
`group_array_axioms` from module level down to three items removes facts from
every *other* context, which can only make verification **harder**, never
weaker — a spec cannot be weakened by withdrawing a lemma. The empirical check
agrees: all 18 mutants plus all 4 shipped negatives die, and the one connection
the scoping could have severed (`MBTAB@` ↔ `mbtab_of`) is exactly what `notable`
proves is intact. **Clean negative.**

### `#[verifier::rlimit(30)]` — the disclosure is exactly right

The engineer asked a reviewer to check whether 30 hides a fragile proof. It does
not, and the disclosure reproduces on both sides:

```
rlimit removed, PLAIN:  21 verified, 0 errors        <- verifies at the default
rlimit removed, TWIN:   23 verified, 1 errors        <- FAILS at the default
```

**Exactly what `NOTES.md` §10b claims.** ✅

### ⚠ MINOR m1 — `negatives.py --emit nopos` fails at the wrong obligation

`nopos`'s docstring says it tests termination: *"The start walk's `decreases`
stops decreasing."* It does not. Setting `mbtab_of` to 0 for a class also breaks
`mbtab_matches_upto`, so the mutant dies at **`p.rs:159`, the `compute_only`
assert — the identical error site as `notable`.** Two controls, one failure
mode; the termination premise the row calls *"the termination premise of the
whole row"* has **no control that isolates it**.

I built the isolating mutant (`mbtab_of` **and** `MBTAB` both set to 0 on the
`0xFE/0xFF` class, so the table lemma still holds):

```
error: postcondition not satisfied        <- mbtab()'s `r >= 1`, a DIFFERENT site
verification results:: 20 verified, 1 errors
```

**So the property holds and `lemma_mbtab_pos` is load-bearing — but the shipped
control does not show it.** Severity `minor`: `nopos`'s docstring should say it
tests the table agreement, and a second mutant should carry the termination
claim. `.temp/php17/mut/` has it.

---

## 3. ⚠⚠ THE R1h FIDELITY QUESTION — faithful, and here is the rule for the other 8

**Verdict: `ph07`'s R1h is FAITHFUL, and it is faithful for a reason that does
not generalise to most of the eight.**

I extracted `PHP_FUNCTION(mb_strcut)` **by brace-matched function body**, not by
grep, from the pinned tarball and from five later tags.

**(i) The wrapper really is the caller frame.** 5.0.0's `mb_strcut`
(`mbstring.c:1737`, 1778 B, sha256 `10ac89a0be1719da`) ends:

```c
string.val = Z_STRVAL_PP(arg1);  string.len = Z_STRLEN_PP(arg1);
if (from < 0) { from = Z_STRLEN_PP(arg1) + from; if (from < 0) from = 0; }
if (len  < 0) { len = (Z_STRLEN_PP(arg1) - from) + len; if (len < 0) len = 0; }
ret = mbfl_strcut(&string, &result, from, len);
if (ret != NULL) RETVAL_STRINGL(...); else RETVAL_FALSE;
```

`c/kernel.c`'s `kernel()` carries **every one of those**, in order, including the
`int` truncation of the two `long`s (it reads them as `int32_t`). What it drops
is `mbfl_string_init`, the arg-parsing switch and the encoding lookup — wrapper,
i.e. `narrowed`. ✅

**(ii) The fix lands in upstream's own position.** The 5.1.1 → 5.1.2 *function*
diff:

```
@@ -68,6 +68,13 @@
 	}
+	if (from > Z_STRLEN_PP(arg1)) {
+		RETURN_FALSE;
+	}
+	if (((unsigned) from + (unsigned) len) > Z_STRLEN_PP(arg1)) {
+		len = Z_STRLEN_PP(arg1) - from;
+	}
+
 	ret = mbfl_strcut(&string, &result, from, len);
```

After the two negative clamps, immediately before the call. **That is exactly
where `c/kernel_hardened.c` puts it.** So the diff between R1 and R1h is
upstream's diff, in upstream's place, against upstream's neighbouring lines.
**It is not a hand-written control wearing a real sha.** ✅

**(iii) The history table is right, and the row's byte-identity claim is
understated.** By function extraction over twelve tags:

```
mbfl_strcut body sha256 613648930a3d2551, 4693 B, at NINE tags:
  5.0.0 5.0.5 5.1.0 5.1.1 5.1.2 5.2.17 5.3.0 5.3.1 5.3.2
  5.3.3   -> a509b376b777812c (d9dda48f8a7e's rewrite)
  5.3.29 / 5.4.0 -> 0a33db6c8f4070b7
```

The row says **six**; it is **nine**. Understated, not wrong.

⚠⚠ **AND THE ROW'S §2c TRAP CAUGHT ME.** My first pass used a
spelling-dependent regex for hunk (b) and scored **5.3.0/5.3.1 as UNGUARDED**.
Reading the *function* shows both carry it, re-spelled `(unsigned int)` where
5.1.2 wrote `(unsigned)`:

```
php-5.3.0:2668   if (((unsigned int)from + (unsigned int)len) > string.len) { len = string.len - from; }
php-5.3.1:2668   (same)
php-5.3.2        GONE
```

**The engineer's "went out, came back, went again" table is CORRECT.** This is
the third independent instance of `PROTOCOL_PHP.md` §F item 6, and it landed on
the reviewer this time. `.memory-php/00-corpus.md`'s *"ask about a FUNCTION, not
about text"* earned its capitals again.

### ⚠⚠ MAJOR M1 — the row pins ONE span and lifts THREE, and the unpinned third is where R1h lives

```
provenance.c_file  = ext/mbstring/libmbfl/mbfl/mbfilter.c
provenance.c_lines = [1179, 1259]
extract_sha256     = 5edc6c04b7ff5f64...   (covers that span only)
```

The row also lifts `mbfilter_utf8.c:39-56` (the table — disclosed as
`divergences[6]`) **and `mbstring.c:1774-1812` (the wrapper), which is disclosed
nowhere as a lifted span** — it appears only obliquely inside `divergences[8]`,
an entry about how the *Rust* rungs spell the clamps. **And `mbstring.c` is
exactly the frame R1h occupies.**

Consequence: `provenance.py`'s overlap report — `75 % (39/52)` — is computed
against a span that contains **neither the fix nor the frame the fix goes in**.
It certifies nothing about the artefact this row's second-most-important claim
rests on.

**→ `RECAP_PHP.md` open item 25 should read "pins ONE span, lifts THREE", and
the sharp half is that the unpinned one carries R1h.**

### ⭐ THE RULE FOR THE OTHER EIGHT ROWS (this is what the manager asked for)

The transplant is faithful **because the repair frame was already inside the
kernel, executing on every call, for reasons independent of the fix** — the two
negative clamps are there because they decide the kernel's domain, not because
the fix needed a home. That is a checkable test, and it is not the same as *"the
fix is in another file"*.

> **R1h TRANSPLANT RULE.** An upstream fix may be transplanted into a frame the
> kernel **already contains and already executes on every call**, at upstream's
> own position relative to its neighbouring statements — and the row must then
> **pin that frame in `provenance`** like any other lifted span. It may **not**
> be transplanted into a frame the kernel does not contain. Where the repair
> frame is absent, `R1h` is **not available** and the row must say so and price
> the gap, rather than synthesise a guard.
>
> **The test, in one question:** *does the kernel run the repair frame's code
> today, before the fix is added?* `ph07`: **yes** (`mbstring.c:1787-1805` is in
> `kernel()`). `ph54`/`ph82`/`ph83`: **no, and it never can** — the repair is in
> `Zend/zend_compile.c`, which runs at a *different time* from the executor the
> kernel extracts; there is no position in a VM handler where a compiler hunk
> could land. `FIXSURVEY_001` already says *"`R1h` for these rows is not a line
> you can add to the kernel"* — **this is the general form of that sentence, and
> it makes it a test rather than an observation about three rows.**
> `ph27` (`reg.c` → `ereg.c`) is a **file move**, not a frame change, so it
> passes trivially. `ph88`/`ph89`/`ph90` need the question asked per row.

---

## 4. ⚠⚠ OPEN ITEM 24 — the §A2a clause. **Do not land it as written.**

The proposed clause: *"where the upstream fix changes benign behaviour, the
measured corpus must leave its guards DEAD, `gen.py` must assert it, and the
behaviour change is measured in `controls/`."*

I attacked it as a rule. **Three objections; the third is decisive.**

**(a) It makes "does the fix fire?" a corpus-selection criterion, with no
bound.** Re-run of `fix_scope.py` (`.temp/php17/fixscope-rerun.log`) confirms
the numbers: hunk (b) **changes the answer on 15 870 of 117 612 (13.5 %)**
non-crashing calls. The clause permits excluding that 13.5 %, requires no
statement of its size beside the ladder, and sets no ceiling. On `ph07` the
fraction *is* published (`NOTES.md` §4e) — **that is the engineer's virtue, not
the rule's.** The next engineer whose R1h trips stage 7h can narrow until it
passes, and cite protocol.

**(b) It is stated as a property of the FIX when the binding constraint is a
property of the GATE.** The reason the corpus must leave the guards dead is
`check.py` stage 7h. `.memory-php/02-ladder.md` **F31 already records the
sibling defect** — *"`check_sanitizers_hardened` hard-fails on any R1h
diagnostic — correct for a hand-written PAT control, wrong for a shipped fix …
Standing limitation, not a bug to file."* **Stage 7h is the same defect on the
same axis.** Encoding a workaround for a known-wrong gate check into §A2a puts
it in the wrong layer: it should extend F31, so that when stage 7h learns to
express *"this R1h legitimately differs on benign inputs"*, the workaround
retires with it instead of outliving it as protocol.

**(c) ⚠⚠⚠ THE CLAUSE WAS INVENTED TO RESCUE A CHOICE OF R1h THE ROW'S OWN
EVIDENCE SAYS WAS AVOIDABLE.** Two facts, both in `NOTES.md`, are not connected
anywhere in the row or the report:

```
§4e  R1h_a   reads past val[slen] = 0   <- hunk (a) ALONE closes the defect
     R1h     reads past val[slen] = 0   <- (b) removes NONE of them
§4e  hunk (b) changes the answer on 15 870 benign calls; (a) changes none
§2b  php-5.2.17 ships hunk (a) and NOT hunk (b)
```

I verified the third at source, by function extraction:

```
5.1.2 -> 5.2.17 diff of PHP_FUNCTION(mb_strcut):
-	if (((unsigned) from + (unsigned) len) > Z_STRLEN_PP(arg1)) {
-		len = Z_STRLEN_PP(arg1) - from;
-	}
php-5.3.2, php-5.3.3, php-5.3.29:  hunk (a) present, hunk (b) absent
```

**So an R1h of hunk (a) alone is memory-safety-complete, is byte-for-byte what
PHP shipped at 5.2.17 / 5.3.2 / 5.3.3 / 5.3.29, changes no benign output, passes
stage 7h on an unrestricted corpus, and needs no protocol clause at all.** It is
not a hand-edited sub-commit — it is a **later upstream configuration**, citable
as such, and `ph03` already set the precedent that a multi-hunk fix has hunks
worth pricing separately.

⚠ **In fairness to the engineer:** `idiom.required[4]` pins R1h as *"the real
upstream fix `cb3cca21b345` and NOTHING ELSE"*, and honouring that pin is what
forces the corpus restriction. The choice is real. But it is a choice between
two disclosable options, and the report presents only one and then proposes
protocol to support it.

### The guard clause, if the manager wants to land something

> **Where the upstream fix changes behaviour on benign inputs, a corpus
> restriction alone is not sufficient. The row owes three things:**
> 1. **The benign-change RATE, over an unrestricted interpretation of the row's
>    own domain, published beside the ladder and not only in `controls/`.**
>    `ph07`'s is 15 870 / 117 612 = **13.5 %**.
> 2. **An explicit answer to: does a memory-safety-SUFFICIENT SUBSET of the fix
>    exist that does not change benign output?** If yes, ship it as R1h with the
>    upstream tag that shipped it, or record why not. `ph07`'s answer is **yes —
>    hunk (a), php-5.2.17**.
> 3. **Only then** may `inputs/gen.py` restrict the measured corpus; it must
>    assert the restriction **and record what fraction of the benign domain the
>    restriction removes.**
>
> ⚠ **And file the restriction under `.memory-php/02` F31 as a `check.py` stage
> 7h limitation, not under §A2a as a fixture rule** — so it retires when the
> gate check does.
>
> **What stops the next engineer narrowing until the fix goes quiet:** (1) puts
> the number in the open, (2) forces the cheaper alternative to be *considered*
> before the corpus is touched, (3) makes the size of the restriction a
> published quantity instead of an invisible precondition.

---

## 5. THE THREE MEASURED CLAIMS — re-derived from the record

### (a) *"the over-read does not change the answer"* — **TRUE, and the stated evidence is the weak form of it**

Re-ran `fix_scope.py`: `15 333` over-reading calls, `7` fillers, **`0` moved**;
must-fire control (delete `mbfilter.c:1227`'s `start > len`) **`13 293` of
`15 333` moved**. Reproduces exactly.

**Is 7 fillers enough?** ⚠ **The question is moot, and that is the finding.**
The zero is **structurally forced**, not sampled. `start` is assigned the cursor
of the iteration *before* each read, so a read at index `i > slen` happens with
`start == i > slen` already set; `start` only grows; `:1227` then forces
`start = slen`, `k = start + length > slen` forces `end = slen`, and
`start > end` is impossible so `cnt == 0`. **No filler, and no crafted
*sequence* of fillers, can move the answer.** `fix_scope.py`'s Q3 output states
exactly this mechanism — **so the control already contains the strong argument,
and the report, `NOTES.md` §6 and `RECAP_PHP.md` F41 all lead with the sampled
number instead.** Recommend leading with the mechanism and demoting the 7
fillers to a regression test on the model.

⚠ **Are the fillers adversarial or merely different?** *Merely different*, on
two counts, neither of which matters given the above but both of which would
matter if the structural argument did not hold:

```
0x00->1  0x41->1  0xC3->2  0xE3->3  0xF0->4  0xFC->6  0xFF->1
step classes exercised: [1, 2, 3, 4, 6]
step classes that exist: [1, 2, 3, 4, 5, 6]
MISSING: [5]   (lead bytes 0xF8..0xFB)
```

and every filler is a **constant byte**, so the over-read walk takes a constant
stride; an adversarial filler is a chosen *sequence*. Severity `minor` **only
because the structural argument covers both gaps.**

### (b) *"the 2010 walk rewrite alone still over-reads on 13 293 calls"* — ✅ CONFIRMED

```
variant    reads past val[slen]  answer != R1
R1                        15333             0
R1h_a                         0         16320
R1h                           0         32190
R1_2010                       0          5717
R1_walk                   13293             0   <- the walk rewrite alone
```

Reproduced. ⚠ **Note for the writer-up**: `13 293` appears in *both* claim (a)
and claim (b) and they are different quantities (calls whose answer moves when
the clamp is deleted; calls that still over-read under the walk rewrite). They
coincide because both are "the over-reading calls whose `start` lands strictly
past the end", but a reader will take one for a typo of the other. **Say so.**

### (c) *"the fix costs a constant, not a rate"* — ✅ CONFIRMED, and `NOTES.md` is more careful than the task file

Re-derived from `results-php/ph07-strcut-cursor.json` (`.temp/php17/rederive.txt`):

```
cell         Ir/call small Ir/call large    marginal  fixed/call
c-gcc            2376.4676    15982.7369    3.864320    239.4989
c-gcc-h          2383.7504    15989.8963    3.864285    246.8010
c-clang          2026.5814    13228.2013    3.181375    267.2813
c-clang-h        2035.8304    13237.3265    3.181339    276.5497

gcc   marginal 4dp equal? True    diff = -3.504e-05
clang marginal 4dp equal? False   diff = -3.518e-05    (3.1814 vs 3.1813)
gcc   fixed/call delta = +7.3022      clang fixed/call delta = +9.2685
```

**+7.3 / +9.2 exact.** The marginal moves by −3.5e-05 on *both* compilers —
identical magnitude, which is itself the cross-check that it is a decomposition
artefact and not an effect.

⚠ **The task file's paraphrase — *"marginal identical to four decimals"* — is
wrong for clang. `NOTES.md` §8a is not**: it says *"same marginal to four
decimal places (3.8643 both); **on clang they differ by 0.0001, which is the
last digit**"*. **The row's own text is more careful than the summary of it** —
the same shape `CLAUDE.md` warns about when `SYNTHESIS.md` was more careful than
the page built from it. **Quote §8a, not the paraphrase.**

---

## 6. THE ROW'S OWN CAVEATS

### `memcpy` outside `kernel_exclusive_ir` — ✅ bounded as claimed

`NOTES.md` §8c's three total-`Ir` figures re-derive: R2 4.8237 / R3 3.5147 /
R4 3.1050 against kernel-exclusive 4.7860 / 3.4451 / 3.0354. **R2-vs-R4 is
+55.35 % total against +57.67 % kernel-exclusive; R3-vs-R4 +13.19 % against
+13.50 %.** Ordering and magnitudes survive. ✅

⚠ One refinement: the "~2 %" is the whole **out-of-kernel** term, not the
`memcpy` term. R2 calls no `memcpy` and still shows +0.0377; so the
`memcpy`-specific part is at most `0.0696 − 0.0377 = 0.0319` ≈ **1 %** of total.
The caveat is if anything **smaller** than stated.

### The wall clock — ✅ the numbers reproduce exactly; ⚠ MINOR m2 on one word

All four `ns/window-byte` marginals and all four spreads reproduce to the digit:

```
safe_naive 1.1542  +5.04%  worst spread 12.2%
safe_tuned 1.1725  +6.71%               13.7%
unsafe     1.0987   0.00%                8.0%
verus      1.0391  -5.43%                3.0%
```

⚠ *"their wall medians differ by 5.4 %, **… and it is larger than every
difference the table contains**"* — **false for one cell**: `safe_tuned`'s
+6.71 % exceeds the 5.43 % floor. The **conclusion is unaffected and arguably
better stated correctly**: the noise floor is *comparable to* every difference
the table contains (5.0 %, 6.7 %), so none of them is resolvable. Severity
`minor`. ✅ **The refusal to draw conclusions from the wall clock is correct and
I did not shake it.**

### `whole`-mode identity (report §7 item 6) — confirmed, and the O0 gap is the larger one

```
whole O0  unsafe n_fn=123   verus n_fn=86     <- 37 instructions apart
whole O3  unsafe n_fn=875   verus n_fn=888    <- 13
```

The report gives only the O3 pair. The O0 divergence is **three times larger**
and in the opposite direction. Still uninvestigated; the `identity` pin is
`isolated`-scoped so the gate is right not to object. Flagged, not a defect.

---

# §2 REVIEWING THE MANAGER'S FOUR SURVEYS

`PROTOCOL.md` rule 3. All four attacked; **all four have real defects, and in
three of them the document's own quoted evidence contradicts its prose.**

## 2.1 `FIXSURVEY_001` + F38/F40 — the load-bearing claim survives on **2 of 5**, not 3

The claim — *"the column names **a** fix, not necessarily the one that removes
the 5.0.0 defect"* — is **still true**, but one of its three supporting
hand-checks is refuted.

### ⚠⚠ `ph12` — **REFUTED. `896a5216d73d` IS the fix.**

`UPSTREAM_001` §1b calls it *"❌ LATER fix … Fixes bug #33605 instead"*. The
pre-image quote is byte-exact, but the inference is wrong. Replaying each
version's guard chain against the corpus PoC `substr_compare("aa","a",-99999999,0,0)`:

```
5.0.0  REACHES SINK  offset=-99999999   cmp_len=100000001
5.1.0  REACHES SINK  offset=-99999997   cmp_len=99999999
PRE    REACHES SINK  (896a5216d73d's pre-image -- still crashes)
POST   REJECTED      (896a5216d73d's post-image)
```

Both of the commit's additions defuse the PoC independently. ⚠ **And the survey
contradicts itself**: `UPSTREAM_001` §3's block headed *"5.2.0 — the
short-circuit is deleted"* **is that commit's post-image**, and the commit's
date (2006-04-25) sits inside §3's own declared 5.1.0 → 5.2.0 window. §3 quotes
it as the fix; §1b rejects it as not-the-fix.

Also refuted: §3 presents 5.0.0 and 5.1.0 as identical. 5.1.0 adds an
**unclamped** rebase at `string.c:4884-4886` that 5.0.0 lacks — material, since
the row's mechanism is the negative offset.

### ⚠⚠ `ph22` — the withdrawal stands, the **replacement finding is wrong three ways**

(i) *"survived 5.1.0 → 2025, nineteen years"* — the identical UB is in the
5.0.0 line the same paragraph quotes: `(arg+1)/2` overflows at `arg == INT_MAX`
exactly as `(arg + (arg%2))/2` does (UBSan, both forms). The window is **21
years**, not 19 — so *"PHP shipped it for 21 years"* was withdrawn on the wrong
grounds: **false for the accumulation defect, true for the argument defect the
survey itself nominates as the survivor.**

(ii) *"`+1` over-counted for even `arg`"* — **exhaustively false**. Over
`[0, INT_MAX-1]`, all three forms agree on every value; `(arg+1)/2` is exact
ceiling division. The 5.1.0 → 5.2.0 edit is a semantic no-op.

(iii) *"an overflow-checking macro receives an already-wrapped value … the
wrapper is present and bypassed"* — **refuted; it is not bypassed.** The wrap
lands **negative**, straight into `INC_OUTPUTPOS`'s own `(a) < 0` disjunct:

```
arg = 2147483647
5.0.0:  outputpos=-1073741824 outputsize=0  emalloc(1)      <- the defect
5.1.0:  GUARD FIRES (a=-1073741824) : RETURN_FALSE
2025 :  outputpos=1073741824  emalloc(1073741825)           <- the fix RELAXES it
```

`865739e5b196` makes a formerly-**rejected** format succeed with a ~1 GB
allocation (its own test carries `memory_limit=-1`). It is a UB-hygiene fix,
**not** a memory-safety fix, and **not `ph20`'s shape**. ⚠ **F40 and
`FIXSURVEY_001` both publish the `ph20` analogy; it should be withdrawn.**
✅ Confirmed: the 5.1.0 macro body is byte-exact as quoted, `ph22`'s R1h is
correctly the 5.1.0 arrival, and `arg` genuinely reaches `INT_MAX` — **proved by
upstream's own regression test**, `pack('h2147483647', 1)`.

### ⚠ `ph21` — verdict right, reasoning inverted

`c591f022f8ab` is a later fix ✅, but it **repairs a regression the nominated
R1h introduced**. 5.2.0's `size_t` + `safe_emalloc` allocates *correctly* on
64-bit; the hole moved to the zval boundary, where `RETURN_STRINGL` stuffs a
`size_t` into an `int str.len`:

```
strlen  mult     result_len   alloc bytes   (int)str.len   5.0.0's deleted int guard
100000  21475    2147500000   2147500001    -2147467296    would have REJECTED
```

**R1h for `ph21` must be recorded as *incomplete*, not as *the repair*.**

### The two the manager called correct — ✅ both confirmed, one annotation refuted

- **`ph29` `445daac3ab1a`** — ✅ *"exact, minimal"* is exactly right: 1 file,
  5 insertions, inside the window. Two-stage repair confirmed.
  ⚠⚠ **But `UPSTREAM_001` §4's doubt about the catalogue is itself REFUTED —
  it paraphrases `CATALOGUE.md:434` and then refutes the paraphrase.** The
  catalogue's real claim is about `REAL_SIZE`, and it is **correct at source**:
  `zend_alloc.c:129 unsigned int real_size; :132 REAL_SIZE(size) ((size+7)&~0x7);
  :182` allocates from the truncated value. `REAL_SIZE(2^63)` → `0`.
  **`.memory-php/04-process.md`'s standing finding — *the citation and the story
  about it are two different claims* — fired again, in the survey that cites it.**
- **`ph16` `99e290f882c9`** — ✅ 10 files, ~27 KB, introduces `PHP_SAFE_FD_SET`,
  applies it at the row's statement; the macro quote is byte-exact.
  ⚠ **REFUTED: `&& this_fd >= 0` is annotated `/* new */` on a patch line that
  carries no `+`.** It is unchanged context; a *different, earlier* commit in
  the window added it. This matters — on POSIX `PHP_SAFE_FD_SET` is
  `if (fd < FD_SETSIZE)`, which a **negative** fd passes, so the two guards the
  survey attributes to one commit come from two.

## 2.2 `ADJUDICATION_002` — both admissions stand; **three of four load-bearing claims are wrong**

**The conclusion is right: `ph92` and `ph93` clear the C-side bar.** Nothing I
found is a kill. But:

### ⚠⚠ The headline is refuted by the document's own quote

`ADJUDICATION_002:45` — *"Neither kill note claims exactness."* The two notes,
verbatim from `a197dc4`, **both end on an exactness assertion**:

```
:923  CRASH-106 ... same wrap-down-then-unbounded-*target++; distinct only in
      needing a ~358 MB input, which is a *worse* kernel, NOT A DIFFERENT MECHANISM
:924  CRASH-109 ... the second `alloced` growth path at `:692` muddies the
      extraction WITHOUT CHANGING THE MECHANISM
```

**ADJ line 52 quotes CRASH-109's exactness clause seven lines below the sentence
denying it exists**, and its CRASH-106 quote silently drops both the mechanism
claim and *"not a different mechanism"*. **The surviving correct finding is
narrower and still worth landing:** *both notes assert exactness but ground it
in a cost word.* The admissions follow; the stated reason does not.

### ⚠⚠ `ph92` as LANDED carries two wrong facts

- **`307 MB` → ≈ `614 MB`.** At `2^31/7` the value goes **negative** and the
  allocation simply fails. The wrap-down-to-small-positive that produces the
  heap overflow needs `2^32/7 = 613,566,757`. `CATALOGUE.md:379` and `:382`
  both carry 307 MB as the trigger and the resident budget.
- **It is not an `int` expression overflow.** `sizeof` yields `size_t`, so the
  RHS is computed in **64-bit unsigned** and **truncated by the store** into
  `int new_length`. That is **`ph21`'s class, not `ph19`'s** — which *strengthens*
  the admission, and makes `CATALOGUE.md:378`'s *"the `int` overflow is the whole
  defect"* wrong.

✅ **Clean negatives on `ph92`:** every line number exact; no `is_xhtml` in 5.0.0
(the one-degree-of-freedom claim survives); the sizing pass is exact —
**9 832 strings, 0 mismatches**.

### ⚠⚠⚠ `ph93` as LANDED prices the wrong frame — ADJ's own headline defect

`CATALOGUE.md:384` cites `string.c:682` + `:692-694`, and `:386` states the
trigger as the `textlen × breakcharlen` product — that is the **else-arm**
(`linelength <= 0`). Measured:

```
CASE 1  else-arm, linelength=0, breakcharlen=2: loop finished WITHOUT reaching :692 (min chk = 32)
CASE C  IF-arm,   linelength=2e9, breakcharlen=2: *** :692 REACHED at iter=2, chk=0
```

`chk` starts at `textlen` in the else-arm and `current` advances ≥1 per
iteration, so `:691 if (chk <= 0)` **never fires there**. **The stated trigger
and the stated distinctness are on mutually exclusive executions.** Correct
citation: **`:679` + `:692-694`, `linelength > 0`.**

⚠⚠ **And `CATALOGUE.md:385` as landed is FALSE:** *"No other row in the
catalogue grows a buffer DURING the emit pass by arithmetic that is itself
unchecked `int`."* Refuted by **three rows in its own S3 section** —
`ph18` (`formatted_print.c:190-197`), `ph25` (`metaphone.c:147-153`),
`ph27` (`reg.c:337-343`). ADJ's original sentence survives only on its trailing
conjunct *"and divides by an attacker-controlled `linelength`"* — **which the
landing deleted.**

⚠ The SIGFPE rider is a **real second defect** but needs `breakcharlen == 0`
stated: `wordwrap("\0AAAA", 0, "")` reaches `:692` with `linelength == 0`.

### The unchecked C.1 rows — **2 of 12 reverse, and not for ADJ's reason**

All three *"merged by the corpus itself"* claims are **true** — `index.csv`'s
`merged_members` records `V5C-116→ph03`, `V5C-173→ph11`, `V5C-015→ph22`.
⚠ ADJ says *"four of them"*; it is **three**.

`CRASH-090→ph32` upheld with the C (same array, same expression at
`html.c:900`). `CRASH-037→ph39` upheld. `CRASH-101→ph39` and `CRASH-061→ph60`
are **slight variations** that §3.1 admits.

⚠⚠ **`CRASH-126` and `CRASH-163` REVERSE.** The kill note says *"same fallible
call's failure not tested"*. In both, **the failure IS tested**:

```
CRASH-126  mbstring.c:3215  if (zend_parse_parameters(..., "|s", &typ, ...) == FAILURE) RETURN_FALSE;
           -> `|` makes it optional; zero args returns SUCCESS and `typ` keeps its NULL initialiser
CRASH-163  zend.c:1078      if (call_user_function_ex(...) == SUCCESS) {...} else { :1083 handler }
           -> the NULL comes from :1075, where the function nulled the global itself
```

Different C mechanisms, and `index.csv`'s own `root_cause_id` for CRASH-126 says
so. ⚠ Both were killed **twice** for reasons the bar forbids — once in C.4's
*"ordinary null-deref set"*, then again under C.1. `TASK_PHP_012` rider **M5** is
the same finding reached independently.

⚠⚠ **The general lesson: ZERO of the remaining C.1 notes contains a cost word,
so ADJ's predicted re-read finds nothing. The two that do reverse need a
DIFFERENT test — *does the C support the mechanism claim?* — which ADJ never
runs on anything, including on its own two admissions.**

⚠ **Process:** `C.1` has **already been landed** despite `ADJUDICATION_002:7`
saying every edit is blocked by rule 11, and the landed quote of CRASH-109
(`CATALOGUE.md:955`) is **less accurate than ADJ's own** — it deletes exactly
the words that falsify the claim it supports.

## 2.3 `UPSTREAM_001` — one window spot-checked end-to-end

Covered above (`ph12` refuted, `ph21` refined, `ph16`/`ph29` confirmed with one
annotation refuted each). ✅ **All four §1 citations verified byte-exact against
the tarball.** ✅ §3's caution that 5.4.0's smaller guard is not a regression is
**verified at the sink** — `zend_operators.c:1959` mins all three lengths.
✅ §5's `grep` hazard **reproduced by me, typed into a Bash call**:

```
grep  -n "PHP_FUNCTION(str_repeat)" string.c        -> exit 1, NO output
grep  -an "PHP_FUNCTION(str_repeat)" string.c       -> 4115:...
/usr/bin/grep -n "..." string.c                     -> 4115:...
grep  -n "..." string_clean.c   (one byte apart)    -> 4115:...
type grep -> "grep is a function"
```

## 2.4 F39 — **the direction IS overstated.** Every number is exact; the inference is not.

✅ All four table cells re-derive exactly from the pattern `NOTES.md`
(`p22` 4401.61−4276.61 = +125.00 / +1021.00, **510.5×**; `p13`, `p12`, `p10` all
exact). ✅ Result 1 quoted verbatim (`SYNTHESIS.md:206`). ✅ *"neither php row has
a `spellings.py`"* confirmed; the PAT set is exactly `p13 p34 p42 p49`.
✅ Per-row directions all correct: **4 of 4 against safe Rust, 3 of 4 out of
their buckets** — F39 is, if anything, *understated* against `SYNTHESIS.md:250`.

**But the three things the sentence does rhetorically are all unsupported:**

1. ⚠⚠⚠ **THE DIRECTION IS ARITHMETICALLY FORCED, NOT MEASURED.** The statistic
   is `R3ship − min(R4 found)`, R3 is held fixed, and a minimum can only fall.
   **A row in that column that moved *toward* safe Rust cannot exist.**
   *"Every one against safe Rust"* is a theorem about taking a minimum. The only
   empirical content is the base rate and the magnitude.
2. ⚠⚠ **The denominator hides the base rate.** *"Four rows of 22"* — the 22 is
   stale **inside `SYNTHESIS.md` itself** (`:212-213` says the licensed set *"was
   22 of 26 and is 23 of 33"* while `:249` still says 22), and *"where anyone
   searched the R4 side"* is false: `results/synthesis.md:369-401` records an
   R4-side search on **19 of 33 rows**, and **eleven found nothing**
   (`p05`: 46 spellings, *"the R4 side has NEVER moved"*; `p19`: *"ALL THREE
   SIDES ARE DEGENERATE"*; `p46`: *"BOTH sides searched, BOTH degenerate"*).
3. ⚠⚠ **"admissible" is refuted on 3 of the 4** by the patterns' own records —
   `p13` *"out of contract by the consumer entry's English"* (`NOTES.md:1198`),
   `p12` *"a control and not a rung"* (`:1331`), `p10` *"out of its own pattern's
   declaration … the reason it cannot ship"* (`:1232`), and `.memory/01-ladder.md`
   calls `p10`'s *"the **rejected** R4 candidate"*. **Only `p22` is clean.**

⚠⚠ **AND `SYNTHESIS.md:271-277` ALREADY SAYS THE ASYMMETRY IS A SEARCH-EFFORT
ARTEFACT** — *"the R3-side levers cost zero trusted items and are easy to find;
the R4-side levers have to clear the prover. That is why the unsearched side is
systematically the unsafe one."* **F39 converts that into a prior about the true
value.** On the **R3** side the PAT record moves overwhelmingly *for* safe Rust
and usually bigger: `p16 +27/+77 → −199/−2545`, `p09` a 65× R3-side span,
`p23` headline 3.11× → 1.31×, `p06 +334 → +80`, `p14 +425 → +225`, `p02`, `p04`,
`p17`, `p36` — **≥9 rows for safe Rust on the R3 side against 4 on the R4 side.**

⭐⭐ **AND §1.1 IS THE DIRECT CONFIRMATION.** I searched `ph07`'s **R3** side and
found **+13.50 % → +2.62 %**, a move **for** safe Rust larger than three of
F39's four R4-side moves. **A row that has searched neither side is unbounded in
both directions, and the cheap search — the one to run first — historically
moves the number FOR safe Rust.**

**Corrected sentence, drop-in for F39's *"So the prior is not neutral"*:**

> Of the 19 PAT rows whose R4 side was searched, **eight found a cheaper R4 and
> eleven found none** — the R4 endpoint is degenerate more often than not. Where
> one was found the published gap necessarily widens against safe Rust, **because
> the statistic is `R3ship − min(R4 found)` and a minimum can only fall**; the
> direction of those four is forced by the arithmetic and is not evidence about
> an unsearched number. ⚠ Three of the four counterparts are **out of contract**
> by their own patterns' records; only `p22`'s is admissible. What the record
> actually says (`SYNTHESIS.md:271-277`) is that *the number moves toward
> whichever side you did not search*, and the R3-side levers are the cheap ones
> — on ≥9 PAT rows an R3-side respelling moved the headline **toward** safe
> Rust, **and `ph07`'s R3-side search now does the same, +13.50 % → +2.62 %.**
> `ph03` has searched neither side, so its `+3.7 %` is unbounded in both
> directions.

⚠ **Two incidental defects:** `RECAP_PHP.md:59` (START HERE) still says the
ladders are *"UNLABELLED fixed-R4 bounds"* while `:1384` records the labelling as
`✅ DONE` and `.memory-php/02:97` confirms it — **the box is stale against its own
item 26**. And F39's *"byte-identical across six PAT patterns"* is false about the
tree: the paragraph is in **all 33** PAT specs in four variants; F39 is repeating
the paragraph's own stale self-description.

---

# §3 THE MANAGER'S THREE UNCERTAINTIES

**3.1 — Is `ph07`'s R1h admissible?** ✅ **Yes**, and §1.3 gives the test that
makes it a rule for the other eight rather than a judgement about this one.
⚠ The real cost is **M1**: it lands in a frame `provenance` does not pin.

**3.2 — Was the split (landing §F 5–6, holding the §A2a clause) self-serving?**
⚠ **The split is right and the stated reason is not, which is exactly how a
self-serving rule survives review.** §F 5–6 are **observations** — *grep is
blind to 41 files*, *the column exists and names a fix* — settled by one command
each, and I reproduced both. The §A2a clause is a **normative rule about what a
corpus may exclude**, and a norm is settled by surviving adversarial use, which
needs n ≥ 2. **So the criterion is the KIND OF CLAIM, not whose it is** — and it
happens the manager's were observations and the engineer's a norm. ⚠ **Write the
criterion into `PROTOCOL_PHP.md` so it binds symmetrically**, because as it
stands the split *is* indistinguishable from "the manager's unreviewed work
counts and the engineer's does not". ✅ **And on the merits the manager was right
twice over**: §1.4 shows the clause is not merely unreviewed, it is *avoidable*.

**3.3 — Is n = 2 enough for the `ph03`-vs-`ph07` contrast?** ⚠ **One of its three
legs has just broken.** *"tuning recovers most vs tuning recovers none of the
pattern's own loop"* is **refuted** — an in-contract safe tuning recovers
**80.6 %** of `ph07`'s walk gap, so both rows now say *tuning recovers most*.
The other two legs survive and I re-derived both: **rate vs constant** ✅
(§1.5c), **dead-and-incomplete vs complete** ✅ (§1.5b).

**What a third row would have to look like to settle it** — three properties,
and the first is the one this review makes non-negotiable:

1. ⭐ **It must ship a `controls/spellings.py`, or at minimum an R3-side spread,
   BEFORE its headline is written.** `ph07` shows the headline claim of a row is
   exactly what an unsearched spread destroys. **No third row is worth building
   for this contrast without one.**
2. **Its guard must sit INSIDE the innermost loop** — `ph03`'s is in the outer
   loop and `ph07`'s outside both, so the *"where in the loop nest"* mechanism
   has been sampled at two of three positions and never at the deepest. That is
   what makes it a mechanism rather than two anecdotes. `ph21` (`str_repeat`) and
   `ph16` (`FD_SET`) are both *outside*; **`ph12` (`substr_compare`) is the
   nearest candidate in the batch** and its sink mins three lengths per call.
3. **Its upstream fix must be complete AND change no benign output**, so the
   `R2–R5-are-ports-of-R1h` conditional gets its third data point without a
   corpus restriction confounding it. ✅ **`ph29`'s `445daac3ab1a` is exactly
   that** — verified minimal in §2.1.

---

# SEVERITY SUMMARY

| | finding | where |
|---|---|---|
| **blocker** | **B1** the headline non-existence claim is refuted by construction; R3 +13.50 % → **+2.62 %** in contract, safe, checksums identical | §1.1 |
| **major** | **M1** `provenance` pins ONE span, the row lifts **THREE**, and the unpinned one (`mbstring.c:1774-1812`) is where R1h lives | §1.3 |
| **major** | **M2** open item 24's clause rescues an R1h choice the row's own evidence says was avoidable (hunk (a) alone = php-5.2.17) | §1.4 |
| **major** | **M3** `ph12`'s `896a5216d73d` **is** the fix; `UPSTREAM_001` §1b and §3 contradict each other | §2.1 |
| **major** | **M4** F39's direction claim is a theorem about a minimum; denominator wrong; 3 of 4 counterparts out of contract | §2.4 |
| **major** | **M5** ADJ's *"neither kill note claims exactness"* is refuted by ADJ's own quote seven lines below | §2.2 |
| **major** | **M6** `ph93` as landed prices the wrong frame — `:682` provably cannot reach `:692` | §2.2 |
| **major** | **M7** `ph92` landed trigger 307 MB → **≈614 MB**; mechanism is store-truncation, not `int`-expression wrap | §2.2 |
| **major** | **M8** `ph22`'s replacement finding wrong three ways; the `ph20` analogy should be withdrawn | §2.1 |
| **major** | **M9** `CATALOGUE.md:385` as landed is refuted by `ph18`/`ph25`/`ph27` (the landing deleted the saving conjunct) | §2.2 |
| **major** | **M10** `CRASH-126` and `CRASH-163` reverse — the failure **is** tested in both | §2.2 |
| **major** | **M11** `ph21`'s R1h must be recorded **incomplete**: 5.2.0 deleted a bound `c591f022f8ab` restored in 2015 | §2.1 |
| **minor** | m1 `negatives.py --emit nopos` fails at `notable`'s obligation; termination has no isolating control | §1.2 |
| **minor** | m2 *"larger than every difference the table contains"* — `safe_tuned` +6.71 % > the 5.43 % floor | §1.6 |
| **minor** | m3 `mbfl_strcut` byte-identical at **nine** tags, not six (understated) | §1.3 |
| **minor** | m4 `RECAP_PHP.md:59` contradicts `:1384` on whether the ladders are labelled | §2.4 |
| **minor** | m5 Q3's fillers miss step class 5 and are all constants — moot, the zero is structurally forced | §1.5a |
| **minor** | m6 `C.1` was landed while `ADJUDICATION_002:7` says it is rule-11 blocked; the landed quote is worse than ADJ's | §2.2 |
| **minor** | m7 `UPSTREAM_001` §4 refutes its own paraphrase of `CATALOGUE.md:434`; the catalogue is right about `REAL_SIZE` | §2.1 |
| **minor** | m8 `UPSTREAM_001` §4 annotates `&& this_fd >= 0` as `/* new */` on an unchanged context line | §2.1 |

---

# ⭐ CLEAN NEGATIVES — attacks that did NOT land

These cost real time and should stop the next agent re-running them.

1. **The proof.** 18 reviewer mutants + the row's own 4: **22 of 22 behaved as
   declared.** The postcondition is a genuine functional value spec and pins the
   walks, the fold, the tally, the header decode and both clamps.
2. **`lemma_mbtab_matches`.** No `assume`, no `assume_specification`, no
   `admit`, no sixth trusted item. TCB recount: 5 `external_body` / 4 trusted
   contracts, and `NOTES.md` §10c states exactly that.
3. **The `broadcast use` scoping.** Cannot weaken a spec — it only withdraws
   facts. Empirically confirmed by `notable`.
4. **`#[verifier::rlimit(30)]`.** Plain verifies at the default; twin fails at
   the default. The disclosure is exact and 30 is justified.
5. **R1h positional fidelity.** The wrapper *is* `PHP_FUNCTION(mb_strcut)`; the
   fix lands between `mbstring.c:1801` and `:1807`, verified by function diff.
6. **The §2b history table** — including *"the sum clamp went out, came back,
   went again"*, which my own spelling-dependent regex initially contradicted.
   ⚠ **I reproduced the row's own §2c trap on myself.**
7. **`fix_scope.py` Q1/Q2/Q3/Q4** — every number re-runs identically.
8. **`NOTES.md` §8c** (memcpy) and **§8d** (wall clock) — every figure
   re-derives from the record to the digit; the caveat is if anything smaller
   than stated.
9. **The `+7.3` / `+9.2` constant** — exact, and §8a's four-decimals wording is
   correct where the task file's paraphrase is not.
10. **`ph29`'s `445daac3ab1a`** is genuinely 1 file, 5 lines, minimal.
11. **`ph16`'s `99e290f882c9`** — 10 files, ~27 KB, macro quote byte-exact.
12. **`ph92`'s uniqueness** — no `is_xhtml` in 5.0.0; sizing pass exact over
    9 832 strings.
13. **All three "merged by the corpus itself" claims** — true in
    `index.csv::merged_members`.
14. **`CRASH-090 → ph32`** — exact duplication, upheld with the C.
15. **Both `ADJUDICATION_002` admissions** — `ph92` and `ph93` clear the
    C-side bar. Nothing above is a kill.
16. **F39's arithmetic** — every one of the four PAT cells is exact at source.
17. **All four `UPSTREAM_001` §1 citations** — byte-exact against the tarball.
18. **`v4`** (`s.get(n).unwrap_or(&0)`) is **worse** than shipped R3 (+17.62 %
    vs +13.50 %) — a plausible-looking safe spelling that does not work.

---

# NOT DONE / UNSURE

1. **`v1` is not a gated rung.** No `O0`, no `whole`, no `check.py` run, no
   `results-php/` record. It is a measured counter-example. **Landing it as the
   cheapest-found R3 beside the shipped one is a task, not an edit** — and per
   `.memory/02-bench-rules.md` the shipped cell must NOT be replaced.
2. **I did not search the R4 side of `ph07`.** F39's prior is about that side
   and I have not tested it here. My result is R3-side only.
3. **I did not exhaust the R3 search.** v1 leaves **one `mov`** (0.0797
   `Ir`/window byte) between safe Rust and R4. I did not find a spelling that
   closes it; I do not claim none exists — that is the same error I am reporting.
4. **`ph88`/`ph89`/`ph90`** were not put through the §1.3 transplant test. Only
   `ph07`, the three compiler-fix rows and `ph27` were classified.
5. **`ph93`'s SIGFPE** — I have the reachability but did not build the PHP-level
   PoC.
6. **The `whole`-mode identity divergence** (§1.6) is still uninvestigated; I
   only measured that the O0 gap is three times the O3 one.
7. **Not re-run:** `harness-php/gate.py` for `ph07`. Nothing I did touches the
   tree, and both staleness brackets are green, so a re-gate certifies nothing
   new. B1 does **not** stale the row — it is a claim about text, not a
   measurement, and `contract_sha256` and every `Ir` in the record stand.

# MEMORY UPDATES

**None written.** `PROTOCOL.md` rule 9 and rule 4 — `.memory-php/` and
`RECAP_PHP.md` are manager-only, and a reviewer does not fix. Every claim above
is in this file with the command output that decides it.
