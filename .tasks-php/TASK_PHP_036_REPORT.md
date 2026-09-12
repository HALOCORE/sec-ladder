# TASK_PHP_036_REPORT — `ph45-htmlent-cache-int` is BUILT and GATED

**Role: research engineer. One agent, alone.** The row exists at
`patterns-php/ph45-htmlent-cache-int/`: five rungs + R1h, `spec.md`, `model.py`,
`inputs/gen.py`, seven controls, `NOTES.md`, `README.md`.

---

## §0 Headline

| | |
|---|---|
| **gate verdict**, read out of `results-php/gate/ph45-htmlent-cache-int.json` | ⭐ **`PASS-WITH-BLOCKED-ROWS`, `failures: []`**, zero `[…]` problems in the run's output. `contract_sha256 d3cb3219ef3ef5c84a7a82601adbca76dcc70fef090c9c8dd5fef9114ff1186f`. ⚠ **NOT bare `PASS`, and the one blocked row is named**: stage 5c-twin certified **2 twins for 3 trusted items**, with `verus.rs:ent_table` justified away in `spec.md` and argued in `NOTES.md`. It is the same verdict `p01-array-sum`, `p35-tagged-union` and `ph00-smoke` carry. |
| **brackets** | **first** `66 record(s) examined, 0 STALE` / `12 record(s) examined, 0 STALE`; **last** `66/0` / **`14/0`** — the expected figure, two new measure records. ⚠ The FIRST php reading was `12/0`, not `12/0`-after-damage: `TASK_PHP_035`'s work was already committed and the tree was clean. |
| **Verus** | **`41 verified, 0 errors`** in ~3 s at the default `rlimit` for every item but `run`; **`43 verified, 0 errors`** under `--cfg slb_twin`. Three trusted items, two twins, one axiom, one `#[verifier::rlimit(60)]`. |
| **tier** | ⚠ **`narrowed`, as the manager ruled — and §2.2's `projection` call is ACCEPTED with the counter-argument written into `spec.md`'s `divergences_note` where a reviewer will find it.** My reasons are in §3 below; the short form is that the *mechanism* is lifted character for character and only the allocator *behind* it is substituted, and upstream that allocator is a function-pointer table entry PHP itself rebinds at `mbstring.c:764`. ⚠⚠ **The strongest argument for `modelled` is that the window's `place` word has NO PRE-IMAGE IN PHP AT ALL**, and I have written it down next to the ruling rather than only in this report. |
| ⭐⭐⭐ **the ladder result — and it CONTRADICTS the brief** | **The task file's §1 and `_034` §6.8 are both wrong**: *"safe Rust cannot store a pointer in an `i32` at all"* is **measured false**. `(&x[0] as *const u8) as i32` is ordinary SAFE Rust, it truncates, and rustc 1.97.1 emits **ZERO diagnostics even under `-D warnings`** — where the same C emits **FOUR**. ⭐⭐ **What safe Rust refuses is O2, and only O2**: `*(t as usize as *const u8)` is `error[E0133]`. **The immunity is on the DEREFERENCE side, not the storage side.** So all four Rust rungs carry **R1's own idiom, not R1h's** — `cache` is an `i32`, `idx as i32`, `cache as usize`, no `void *opaque` anywhere — and are safe anyway, because the value stored is an index into an arena the program owns. |
| ⭐⭐ **three toolchains, three answers** | **gcc/clang: FOUR warnings** at exactly the four sites `e8901dc17087` rewrites (bug #30573 itself), zero on R1h, measured in all 8 cells of both compilers. **rustc: NOTHING.** **Verus: REFUSES** — `(idx as i32) as usize == idx` verifies under `idx < 0x8000_0000` and fails without it, with `recommendation not met: value may be out of range of the target type` **at both cast sites**. |
| **the oracle** | ⚠ **The catalogue's proposal measures NOTHING** — R1 ≡ R1h on **32 of 32** `small.bin` windows, exactly as §2.4 predicted. ⭐ **The replacement measures, non-fatally**: filter A decodes `&amp;` to **65** (`A`) where R1h gives **38**, with one double free and one leak. ⚠ **`_034` §6.4's `674` is NOT reproducible and the row re-derived it**: 674 came from that probe's interleaving (`'m','p'`), mine from `'6','5'`. **The mechanism transfers; the number does not.** |
| ⚠⚠ **the biggest thing I found that nobody asked for** | **`kernel_exclusive_ir` sees 5.8 % of the C and 9.5 % of the Rust on this row**, so **family A and whole-program `Ir` DISAGREE ON SIGN on the row's headline**: `R3ship − R4ship` is **+0.37 %** in A1 and **−3.06 %** whole-program, and `R2 − R4` is **+0.37 %** against **+19.55 %**. ⚠ **And `|Δinside_share|` is 0.0034, INSIDE F74's 0.02 threshold** — the condition PASSES and A1 is still the wrong number. `NOTES.md` §8. |
| **sanitizers** | `clean` on every input, and it is a finding: the defect is a TYPE error and the address it produces is a legitimately mapped page. **§A4 fidelity is relocated to `controls/fatal.c`, where it matches exactly** — SEGV/WRITE at `:183`-equivalent, and SEGV/READ in `php_shim_efree` on `"hello, world"`. **60 of 60 runs fault.** |
| **two adjacent defects found, reported, not pursued** | `:123`'s stack OOB in the encode half (`_034`'s, commit still unidentified) and ⭐ **`:193`'s SIGNED OVERFLOW, which is MINE and is in the row's own function** — `&#abcdefghijkl;` reaches ~7.4e12 in an `int`, reachable from an ordinary `mb_convert_encoding` call, not in `index.csv`. |

---

## §1 What is built, and what every command said

```
patterns-php/ph45-htmlent-cache-int/
  c/kernel.c (447)  c/kernel_hardened.c (486)  c/kernel.h (90)  c/main.c (85)
  c/arena.h (254)   c/mbfl__html_entities.h (278, GENERATED)  c/emalloc_shim.h -> symlink
  model.py (1106)   inputs/gen.py (418)   spec.md (79 509 B)   NOTES.md   README.md
  safe_naive.rs (680)  safe_tuned.rs (679)  unsafe.rs (644)  verus.rs (1332)
  controls/  e8901dc17087.patch  entity_table.py  fatal.c  native.py
             o1_roundtrip.rs  o1_roundtrip_nopre.rs  oracle.py  strchr_equiv.c
             vacuity.py  warnings.py
  inputs/  small.bin large.bin + SIX adversarial-*.bin
```

Every command, with what it actually printed:

| command | result |
|---|---|
| `harness-php/provenance.py ph45-htmlent-cache-int` | `1 row(s) checked, 0 FAILED`. 12 spans, all in the manifest, all `extract_sha256` green. |
| `--tool build … --all` | `all builds ok` (28 cells) |
| `--tool measure` | `wrote results/ph45-htmlent-cache-int.json` |
| `--tool report` | `wrote results/tables/ph45-htmlent-cache-int.md` |
| `harness-php/gate.py ph45-htmlent-cache-int` | **`PASS-WITH-BLOCKED-ROWS`**, `failures: []` |
| `./verus_run.py verus.rs` | `41 verified, 0 errors` |
| `./verus_run.py verus.rs --cfg slb_twin` | `43 verified, 0 errors` |
| `controls/warnings.py` | `PASS (0 problem(s))` — 4 warnings on R1, 0 on R1h, in all 8 gcc **and** 8 clang cells |
| `controls/native.py` | `PASS` — `strchr` equiv 0/256 disagreements + must-fire 1; `fatal` **60 of 60 faulted**; 4 ASan SEGVs with the right access types |
| `controls/oracle.py` | `PASS` — R1 ≡ R1h on 32/32 `small.bin` windows; four placements; the six shipped binaries agree |
| `controls/vacuity.py` | `PASS` — 4 of 5 mutants fail, V2 is redundant and says so |
| `controls/entity_table.py --selftest` | `PASS` — 6/6 shipped tables match the tarball; must-fire rejects 6/6 |
| `model.py <input>` | `selfcheck=ok (604 synthetic windows, 9 arms, must-fire 126/126/126)` |

**Cross-rung agreement, every cell, every input** (`.temp/php36/`): all 32
non-R1 cells (gcc/clang × O0/O3 × isolated/whole) equal `model.checksum` on all
8 inputs; **R1's own value is deterministic across all four of its cells on
every input, adversarial included**, which is what makes the oracle quotable.

---

## §2 What I re-derived rather than transcribed, and what moved

* ⭐ **All twelve `extract_sha256` values: 12/12 MATCH** `_034` §6.1
  (`.temp/php36/logs-01-spans.log`). Nothing in that table needed correcting.
* ⭐ **The placement, re-measured under all 8 `{gcc,clang} × {-O0,-O3} ×
  {-DSLB_ISOLATED,-flto}` combinations** (`logs-02`), not the 4 `_034` ran.
  `MAP_32BIT` always lands in `[0x40000000, 0x42000000)`; `(int)HI == (int)LO`.
  ⚠ `_034`'s two clang-LTO cells failed only because its probe omitted
  `-fuse-ld=lld`; with it, 8/8.
* ⭐ **The 60-of-60 fault, reproduced** (`controls/native.py`), including the
  `"hello, world"` cell that has no `&` in it.
* ⚠ **`_034` §6.4's `674` does NOT reproduce and the row says so.** Same
  mechanism, different interleaving, **65**.
* ⚠ **`_034` §6.8's central claim is FALSE** (see §0).
* ⚠ **`_034` §6.8's R5 vacuity prediction is wrong for the reason it gave.** It
  expected Verus's raw-pointer provenance to make O2 true by typing. In an
  **index** representation there is no provenance at all, so `wf_ptr` must be
  established and carried — mutant V5 deletes it and the proof fails.

**`contract_sha256` moved twice and `NOTES.md` §0 has the field-by-field diff.**
`identity: []` → one entry (stage 8 requires it and a pin is a measurement);
`verus.axioms` + `unsafe_justifications['ent_table']` + `twin_justifications`
(the gate demanded all three by name); `verus.items` re-derived after a rename;
and **`idiom.required`/`forbidden` rewritten** — see §5.

---

## §3 §2.2 — the tier, and why I ship `narrowed` with the counter-argument attached

**Accepted, and the argument is in `spec.md`'s `provenance.divergences_note`
where it can be attacked rather than only in this report.** My reasons:

1. **Not `verbatim`**: §A1 clause (b) wants a `why` ending in *"no semantics"*
   and the allocator substitution's cannot — the address it returns **is** the
   mechanism. (Agreeing with `_034`.)
2. **Not `modelled`**: `modelled` means *the mechanism is re-expressed because
   the original cannot be lifted*, and the mechanism **is** lifted — `(int)
   mbfl_malloc(...)`, `(char*)filter->cache`, `mbfl_free((void*)filter->cache)`
   and all four decode functions at `[155,258]`, character for character. What
   is substituted is the allocator **behind** it, and §A1 clause (c) is
   satisfied by **demonstration**: at `place == 0` the conversion is the
   IDENTITY and R1 ≡ R1h bit for bit on **2 082** measured and **604** synthetic
   windows.
3. **`narrowed` fits its own definition**: two wrappers come off —
   `mbfl_buffer_converter_feed`'s memory device and
   `mbfl_convert_filter_new`'s vtable dispatch.
4. **Precedent, not liberty**: `ph64` already ships `narrowed` with one
   divergence whose `why` does not end in "no semantics" and states it in the
   same field.

⚠⚠ **THE STRONGEST ARGUMENT AGAINST, WHICH THE MANAGER SHOULD WEIGH AND WHICH I
HAVE WRITTEN INTO `spec.md` AND `NOTES.md` §3 AS WELL AS HERE: the window's
`place` word has no pre-image in PHP at all.** No input chooses where `emalloc`
puts a block, so R1's behaviour at `place != 0` is not PHP's behaviour on any
input — it is PHP's behaviour on a *different platform*. My counter is that
every **measured** window is `place == 0`, that this is the platform the code
shipped on, and that the other placements live in `adversarial-*.bin` where the
gate **records** rather than requires. ⚠ **If a reviewer reads (4) as
precedent-stretching, the row is `modelled` and nothing else about it changes.
A tier is a cost, never a filter** — I did not let the question shape the build.

---

## §4 §3 — which statistic, and the methodological finding it turned up

⚠⚠ **The task's §3 instruction produced a result about the instruction.**

`inside_share = (kernel_exclusive_ir / n_iters) / marginal_ir_per_call`. On this
row `kernel_exclusive_ir` captures **5.8 % of the C's instructions and 9.5 % of
the Rust's**, because the filter body is a separate symbol in **every** rung —
the C reaches `mbfl_filt_conv_html_dec` through `filter->filter_function`, a
call through a POINTER — and **44 % of the C's instructions are in glibc's AVX2
`strcmp`**, which lands in no column of the published table at all.

| comparison | **A1** (`Ir(kernel)`/call, `small`) | whole-program |
|---|---:|---:|
| **`fixed-R4 bound` = R3ship − R4ship** | **+0.37 %** | **−3.06 %** |
| R2 − R4 | +0.37 % | +19.55 % |
| R2 − R3 (the tuning) | 0.00 % | +23.32 % |
| R5 − R4 — the NULL control | −0.04 % | +0.21 % |
| R1h − R1 (the upstream fix) | 0.00 % | **−0.042 %** |
| R3 − R1 (C vs safe Rust) | −17.49 % | −51.80 % |

▶ **What the row publishes, LABELLED, two quantities and not three, no pair
interval**: `fixed-R4 bound` **A1 `+0.37 %`**, and **whole-program `−3.06 %`**.

⚠⚠ **AND `|Δinside_share|` BETWEEN R3 AND R4 IS 0.0034 — INSIDE §3's 0.02
THRESHOLD — AND THE TWO FAMILIES STILL DISAGREE ON SIGN.** F74's condition
PASSES here and A1 is still the wrong number. The mechanism: a small
`Δinside_share` says the two cells have the same callee *share*, and on this row
**both** cells put 90 % of the work in a callee. The rule catches cells that
*differ*; it cannot catch cells that agree on being mostly outside. ⚠ **Offered
as an observation on one row with a mechanism, NOT as a correction to F74**,
which is a 310-comparison result.

⭐ **Three further things §3 did not ask for and the measurement gave:**

1. **The upstream fix is CHEAPER than the defect.** `c-gcc-h` is **68,613 Ir
   cheaper** than `c-gcc` over 1,500 calls (−0.042 %), all of it inside
   `mbfl_filt_conv_html_dec`: `(char*)filter->cache` sign-extends (`movslq`)
   and `(char*)filter->opaque` does not. **A1 reports it as `0.00 %`.** It is
   `.memory-php/02-ladder.md`'s *"negative-cost safety"* for a NEW reason — not
   a check LLVM can drop, but a type that needs no conversion.
2. **R5 − R4 = −0.04 % / +0.21 %. The proof costs nothing at run time.** ⚠ And
   a **10× artefact** had to be removed first: left to LLVM, R5 inlined `dec`
   and R2/R3/R4 did not, which made R5's `kernel_exclusive_ir` read **76.2 M
   against R4's 7.8 M**. `#[cfg_attr(slb_isolated, inline(never))]` on `dec` in
   all four Rust rungs fixes it and is declared at the site.
3. **The C-vs-Rust column on this row is mostly a measurement of glibc**, and
   the row refuses to publish `−51.80 %` bare.

---

## §5 ⚠⚠ The gate found five real defects in my own work. All five are worth a sentence.

1. ⚠⚠⚠ **`model.py::selfcheck` returned a STRING.** `check.py::build_models`
   does `for p in sb(m.selfcheck): rep.fail(…)`, so a string is iterated
   **character by character** and the gate reported `)` as a problem. It must
   return a **list**. *Nothing in `PROTOCOL_PHP.md` says so and `ph64`'s only
   evidence is its code.*
2. ⚠⚠⚠ **Every ASan and UBSan run exited 9 on all eight inputs.**
   AddressSanitizer maps its shadow over `[0x7fff8000, 0x10007fff7fff]`, which
   swallows **every** `LO + k·2³²` for `k` up to ~4096 — so `MAP_FIXED_NOREPLACE`
   at `k == 1` fails and `c/arena.h` exited. ⭐ **The row does not need `k == 1`,
   only `(int)HI == (int)LO`**, which holds for any multiple, so the arena now
   searches upward for the first free `k`. Verified: plain, ASan and UBSan all
   exit 0 with **identical** checksums on benign and adversarial inputs.
3. ⚠⚠ **`vparse.unique_names` RAISES on a duplicate item name and it took out
   FIVE stages at once** (`proof-rule2`, `clause-mut`, `req-mut`, `twin`,
   `contract-source`): `Ctx::emit` and a free `emit`. Renamed to `emit_result`.
4. ⚠⚠⚠ **`idiom.forbidden` was catastrophically over-pinned, and this is the
   finding I would most want a future builder to read.**
   `check.py::spelling_matches` treats **every backticked span in a `forbidden`
   entry** as a spelling that must be ABSENT FROM EVERY RUNG OF THAT LANGUAGE.
   My entries used backticks freely in their *explanatory prose*, so
   `` `int` ``, `` `size_t` ``, `` `cache` ``, `` `mbfl_filt_conv_html_dec` ``
   and `` `filter->status` `` became **nineteen refusals across six files** —
   and `` `void *opaque` `` refused `c/kernel_hardened.c` **for containing its
   own fix**. Rewritten to backtick only tokens grepped absent beforehand
   (`intptr_t`, `i64`, `memcpy`, `memmove`, `copy_within`).
   ⭐ **The named-spelling standard says the POLARITY and the SCOPE of a quoted
   span live in the entry's English. What this row learned is that so does
   everything you did not mean to pin.**
5. ⚠⚠ **`idiom.required` had the same disease and the gate CANNOT catch it** —
   `required` cannot fail the gate by design. As first written it made **34**
   (spelling × rung) obligations, most of them prose tokens like `` `why` ``,
   `` `:161` `` and `` `controls/warnings.py` ``. Rewritten it makes **21**.
   The shipped `.idiom_audit` reads:

   ```
   spellings 14 · rungs 6 · pairs 42 · present 15
   forbidden_spellings 8 · forbidden_hits 0
   required_pins_nothing 0 · no_rung_entries 0
   required_absent 3  -- the three C spellings against c/kernel_hardened.c,
                         which MUST NOT contain them: removing those three
                         casts is the whole of e8901dc17087
   forbidden_unaudited_entries 1  -- forbidden[0], prose-only BY NECESSITY
   ```

   ⭐ **Every number in that audit is explainable**, which is the state
   `RECAP_PHP.md` open item 51 was about from the other direction.

⚠ Two `[doc-citation]` refusals as well: `check.py:9628` and `check.py:2861`
→ `check.py::check_miri` and `check.py::build_models`.

---

## §6 §2.4's oracle, re-derived — and `ph64`'s lesson is now TWICE

| `place` | regions | R1 vs R1h | R1's alloc/free/dfree/wfree/leak |
|---|---|---|---|
| **0** | LO / LO | **identical** — the must-**not**-fire control | 2/2/0/0/0 |
| **2** | LO / HI | `&amp;` → **65** where R1h gives **38** | 2/**1**/**1**/0/**1** |
| **1** | HI / LO | the mirror: same `u64`, same 65 | 2/**1**/**1**/0/**1** |
| **3** | HI / HI | **decode CORRECT**, allocator wrong only — O3 in isolation | 2/**0**/0/**2**/**2** |

**The mechanism** (rule 12): under truncation A's and B's buffers are the same
17 bytes. B writes `#` over A's index 1; when A's `;` arrives `:190`'s
`buffer[1]=='#'` is true, so the **named** entity `&amp;` takes the **numeric**
arm and `:193` reads B's digits. **`&amp;` decodes to `A`.** Filter B's answer,
delivered to filter A, silently — no crash, no sanitizer, no allocator damage.

⚠ **The must-NOT-fire control ships as an INPUT**
(`inputs/adversarial-noalias.bin`), byte-for-byte the same text and interleaving
at `place == 0`, so the gate records it beside the others. Without it the
divergence could be the interleaving.

⭐⭐ **`ph64`'s lesson has now happened twice and it is worth a sentence in
`.memory-php/`**: two rows, two unrelated mechanisms, and in both the
catalogue's proposed `benign`/oracle line measures **nothing** — `ph64`'s
because a freed 39-byte element is cached with its payload intact, `ph45`'s
because at the platform the code shipped on the truncation is the identity.
**A catalogue entry's `benign` line is a proposal, not a measurement, and the
first thing a build task should do with one is try to falsify it.**

---

## §7 §F9 — the overlap number, read rather than quoted

`provenance.py` reports **15 %** against a `narrowed` expectation of 25 %, and
**both that number and "the row's C is a near-verbatim lift" are true.**
Decomposition: **span0** (`mbfilter_htmlent.c:155-258`, the four decode
functions) is **91 % (42/46)** and **span1** (the struct with the defect) is
**86 % (12/14)** — while **span3, the 251-entity table, is 0 % of 253**, because
the heuristic reads `c/kernel*.{c,h}` and the table is in
`c/mbfl__html_entities.h`, flattened exactly as §B3 spelling 1 wants. Drop the
two `html_entities` spans and the number is **61/162 = 38 %**.

⚠ **I did NOT rename the file to `c/kernel_entities.h` to make the number go
up**, although `kernel*` is the glob and the table genuinely is a kernel source.
A number moved by a file name is not a number about the code. ⚠ And the
heuristic's own caveat bites both ways: 91 % on span0 is text in a file, not
code in the benchmark. **What says those lines are compiled is
`controls/warnings.py`** — `-Wpointer-to-int-cast` fires at `kernel.c:191`,
which is `:161`, in every one of the sixteen cells.

---

## §8 Problems, and things I am unsure of

1. ⚠⚠ **`controls/spellings.py` is NOT built. The R4 endpoint is UNSEARCHED**,
   so the published `fixed-R4 bound` is over an unsearched endpoint —
   `.memory-php/02-ladder.md`'s standing debt, and this row makes it **three**
   with `ph03` and `ph64`. ⭐ The **R3 side is partially searched** and the
   search is in `safe_tuned.rs`'s header: four candidates measured
   whole-program on both inputs, **three of them pessimisations including the
   obvious sub-slice hoist (+6.9 %)**, the shipped `&[u8; REQ]` lever at
   **−18.9 %**, and a fifth (`c3`, a first-byte early-out at −24.6 %) measured
   and **deliberately not shipped** because it makes R3 and R4 different
   *algorithms*. That is not a `spellings.py` and has no `.idiom_audit`.
2. ⚠⚠ **The shipped R3 is CHEAPER than R4 whole-program**, which is `ph16`'s
   F67 shape on a second row. **It does NOT make F67 n = 2 by itself**: `ph16`'s
   evidence included a mirror control and a demonstrated-degenerate R4 side, and
   this row has neither. **Read it as a pointer for whoever discharges the
   spellings debt.**
3. ⚠ **`PASS-WITH-BLOCKED-ROWS`, not bare `PASS`.** One trusted item
   (`ent_table`) has no twin and cannot: its `ensures` is `r@ == tbl()` with
   `tbl()` uninterpreted, and no checked body can prove an equation about a
   function with no definition. ⭐ **The alternative was considered and does not
   work**: threading the table through every spec function would remove both the
   item and the axiom, but `kernel`'s `ensures` would have to call an **exec**
   function, which Verus forbids. What replaces the twin is
   `controls/entity_table.py` (6/6 copies byte-exact, must-fire rejects 6/6) and
   stage 2's cross-rung checksum.
4. ⚠⚠ **`results-php/preflight/_norow.preflight.json` gained 188 lines.** That
   is §E's documented *"a FAILING run grows a COMMITTED file"*: the mid-task
   `--check-stale` that reported `2 STALE` (my own `model.py` citation fix) is a
   failing run. **Nothing under `harness/`, `common/`, `patterns/`, `results/`
   or `pilot/` was touched**; `git status` is this row plus its four
   `results-php/` records plus that one line.
5. ⚠ **I did NOT build PHP and did not run `CRASH-123.php`.** The corpus's
   `n_fault: 3/3` is its measurement; mine is `controls/fatal.c`, and the two
   agree on signal, access type, function and line.
6. ⚠ **`mbfl_convert_filter_copy`'s aliasing double free is CITED and NOT
   PRICED** — `_034` §8.4 says in terms it is an inference. The span is in
   `extra_spans` only because the fix removes it as a consequence, which makes
   the fix *larger* than the catalogued defect.
7. ⚠ **`echoes: ["p38"]` was not re-derived**; carried from the catalogue.
8. ⚠ **`spec.md` was assembled once by `.temp/php36/mkspec.py` and is
   hand-maintained from here.** `.memory/05-layout.md`'s artefact-vs-generator
   skew is why the generator is not re-run; it exists as evidence of how the 46
   item pins and the 11 003-byte named-spelling tail got in without retyping.
9. ⚠ **The `place` word's tier consequence is the one call I would most like
   attacked** (§3), and the `inside_share` observation in §4 is the one
   *finding* I would most like checked, because it says a standing rule's
   condition can pass while the statistic it guards is still wrong.
10. ⚠ **`:193`'s signed overflow is mine and unfixed anywhere.** I did not trace
    it to an upstream commit and **nobody should act on it without doing so**.
    `inputs/gen.py` refuses a corpus whose largest `|ent|` comes within 100× of
    `INT_MAX` **on either rung**, so no shipped number is taken over that path.

---

## §9 Evidence index — `.temp/php36/`, 792 KB, all text

| path | what |
|---|---|
| `logs-01-spans.log` | all twelve `extract_sha256`, **12/12 MATCH** `_034` §6.1 |
| `logs-02-placement.log` | the placement under **8** build-flag combinations, gcc and clang |
| `logs-03-strchr.log` | `strchr(s,0)` is the terminator; 0/256 disagreements; must-fire 1 |
| `logs-04-vacuity.log` | the five Verus mutants, **including V2 which did not fire** |
| `logs-05-cgbreakdown.log` | the C's callgrind breakdown — **43.9 % in glibc `strcmp`** |
| `logs-06-r3search.log` | the four R3 candidates plus `c3`, both inputs |
| `logs-07-wholeprogram.log` | whole-program `Ir` for all eight shipped cells |
| `spans.sh` | re-derives every span hash from the tarball |
| `mkspec.py` | the one-shot `spec.md` assembly (see §8.8) |
| `a1.py` | the A1 / `inside_share` computation from the records |
| `verus_items.json` | the 46 item pins, from `vparse` |
| `named_spelling_tail.txt` | the mandatory 11 003-byte tail, extracted not retyped |
| `probe/`, `verus/`, `vac/`, `r3try/`, `src/`, `dec.diff` | the probes, the five Verus mutants, the R3 candidates, the eight tarball files, the R4-vs-R5 `dec` diff |

⚠ Every binary, `.o`, `__pycache__` and callgrind blob is deleted per rule 1;
`spans.sh`, `mkspec.py`, `a1.py`, `probe/*.c`, `probe/*.rs` and the `tar`/`sed`
recipe re-derive all of it. **No `/tmp` file was created.** **No `git add` and no
`git commit`.** **`.web/` was not touched.**
