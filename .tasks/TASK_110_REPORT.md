# TASK_110 — landing TASK_109's corrections into `p42`, and SHIPPING TWO RUNGS

**Role: research engineer.** Scratch: `.temp/t110/` — 684 KB, **no binaries**,
nine probe/generator scripts (`mk`, `csha`, `ladder`, `idprobe`, `parity`,
`terms`, `wpmarg`, `clauseprobe`, `leakteeth`), an inventory table at the end of
`.temp/t110/NOTES.md` saying which script rebuilds what. **No `git add`, no
`git commit`, no history-mutating git.** `.memory/` and `RECAP.md` untouched.
`harness/` untouched — including `check.py`, `build.py`, `asm.py` and
`measure.py`.

---

## HEADLINE

**BOTH RUNGS SHIP. Neither refusal condition triggered.**

| the manager's stop condition | result |
|---|---|
| the ledger R5 must pass `--cfg slb_twin` | **`21 verified, 0 errors`**, matching the pin |
| …and `check.py::_is_trusted` | **`False` for all three new items; TCB unchanged at 5 / 3** |
| `r4_foldonly` must pass Miri | **11 of 12 inputs clean at the gate; `large.bin` BLOCKED as declared; seeds 0–7 clean; the positive control fires** |
| …and the full gate | **`PASS-WITH-BLOCKED-ROWS`, 0 failures** |

**And the two rungs together make `p42` publish something true where it
published something false, twice.**

- **R5 now covers p42's own bug class.** `18 verified, 0 errors`, and
  `controls/ledger_leak.py` deletes each release in turn and Verus names the
  exit it rejects — `return 0;` on the error path, the end of the body on the
  success path.
- **R4 is the do-while.** `R3ship − R4ship` kernel-exclusive goes
  **`−198.00 / −8696.00` → `+12.00 / +11.00`**. The sign flips, and `NOTES.md`
  11b now refuses the directional headline **in both directions**.

**Running count: 389 → 399** (+10, itemised at the end; **397** if you discount
the two method items).

---

## Did

### `patterns/p42-goto-cleanup/verus.rs` — §A, the ghost ledger

`Ledger = Map<int, Dealloc>`, plus `led_alloc` (escrows the token under a ghost
key), `led_free` (withdraws and spends it) and `kbody` (`#[inline(always)]`,
`ensures final(led).dom() =~= Set::<int>::empty()`). `kernel` keeps its **pinned
signature byte-for-byte** and is a two-line wrapper holding the ledger as a
local, so `spec.md`'s `kernel` string, `driver.canonical` and every rung's
driver region are untouched — gate stage 6 passes unchanged.
**Neither wrapper is `external_body` and neither contains `unsafe`.**

### `patterns/p42-goto-cleanup/{verus,unsafe}.rs` — §B, the do-while fold

Both fold loops replaced by a descending cursor from `dig_at(p, base, len - 1)`,
breaking on `q == p`. One induction variable instead of two, and **it never
forms the one-past-the-end pointer** — which is why `r4_endptr` is inadmissible
and this is not.

### `patterns/p42-goto-cleanup/controls/ledger_leak.py` — NEW

Three arms, **two of which must fail**, generated from the shipped `verus.rs` by
substitution with the anchors asserted. It also requires Verus to **name the
exit**, and fails if no exit is named — an arm that fires for another reason is
not the claim.

### `spec.md` — six declaration edits, `contract_sha256` moved TWICE

| | |
|---|---|
| as TASK_104 shipped it | `4a252569067081a55c55c8e6177bc8f6a4f897a57cd59a00c7c000a3da8d29a4` |
| after edits 4–8 (gate-green at this value) | `2be2bf3f04df0d95890cb59c85c78edc4b98082f5efaecb64a9cffb94438dd6c` |
| **as shipped, after edit 9** | **`437ae31512cf250acac91e64e289b8cd200dfd83b78797aa3467945b86718d76`** |

**Rule 6 disclosure is in `NOTES.md` 0 and it is no longer the vacuous form**:
p42 now has a landing commit to diff against, `git show
096d870:patterns/p42-goto-cleanup/spec.md | diff -`, **eleven hunks**, and
`NOTES.md` 0 tabulates every one of them against the edit that made it and says
which four are prose above the fence (`source_sha256` only) and which seven are
inside it.

4. `verus.obligations` 15 → 18, `twin_obligations` 18 → 21, three items added.
5. **M3.** `required[1]`, `required[2]` and `required[3]`'s C side backticked.
6. `idiom.why`'s *"Verus … CANNOT state"* clause retracted and replaced.
7. `identity[0].why`'s closing sentence retracted; its `O3` counts re-measured.
8. `miri.reason` amended.
9. `idiom.why`'s attribute count **23 → 22** — a correction to TASK_109, found
   by re-deriving it. **This one landed after the first measure/gate pass and
   cost a second of each.**

### Prose, all eight+1 sites of the retraction

`verus.rs` module comment, `unsafe.rs` SAFETY (5), `spec.md` ×2 (hashed),
`NOTES.md` 6 and the `dig_free` trusted argument, `README.md`,
`controls/affine_leak.rs` header, **and a ninth the review did not list —
`controls/miri_seeds.sh`'s paragraph (2)**. `affine_leak.rs` is **kept**: its
premise is true and its two arms are the evidence for the encoding half.

### Also landed

- **parity** (`NOTES.md` 5): the size claim replaced by parity, with **four**
  terms, not three (below).
- **352** (`NOTES.md` 3, `README.md`, `controls/leak.sh` header **and its
  success message, which now DERIVES the count from the loop that prints the
  rows** so it cannot go stale again).
- **m1**: `controls/spellings.py` rewrites the `#[path]` to an absolute one, so
  it no longer depends on a gitignored `.temp/common/driver.rs`. It also gained
  the fifth R4 spelling and its anchors were re-cut for the new fold.
- **m2**: `.temp/t104/allocclass/rebuild.sh` written — it carries both compile
  lines **and asserts the two arms agree on the checksum before fitting**. The
  zero-byte `main_shim.c` was referenced by nothing and is deleted.
- **m3**: the `dig_free` trusted argument's corollary corrected. ⚠ The sentence
  about `dig_free` **itself** was right; only the inference from it was wrong,
  and the note now says which is which.

---

## Evidence

### §A — the ledger, and the two things the review did not test

```
$ ./verus_run.py .temp/t110/build/cand_verus.rs                 -> 18 verified, 0 errors
$ ./verus_run.py .temp/t110/build/cand_verus.rs --cfg slb_twin  -> 21 verified, 0 errors
```

```
$ python3 patterns/p42-goto-cleanup/controls/ledger_leak.py
  base       18 verified,  0 errors  OK
  leak_err   17 verified,  1 errors  OK
            Verus names the exit: return 0; [at this exit]
  leak_ok    17 verified,  1 errors  OK
            Verus names the exit: acc [at the end of the function body]
```

`check.py` imported and its own predicates driven over the shipped file:

```
led_alloc  fn  external=None  trusted=False
led_free   fn  external=None  trusted=False
kbody      fn  external=None  trusted=False
external_body: 5     _is_trusted: 3      (both UNCHANGED)
_scan_unsafe_sites -> 0 failures; 5 `unsafe` tokens, all inside a trusted body
```

Gate stage 5c-twin, verbatim:

> `verus.rs: 21 verified, 0 errors with --cfg slb_twin -- matches the pinned
> verus.twin_obligations (18 without it, pinned 18; the twins are cfg'd out of
> every build, so they cost zero instructions)`

⚠ **And the negative that justifies pinning the clause:** delete the
leak-freedom `ensures` instead of the release and the file gives **`18 verified,
0 errors`** — the obligation vanishes and no count moves. Only `spec.md`'s
`verus.items[*].ensures` pin catches that, which is why it is pinned and why
`spec.md` now carries a row saying so.

### §B — `r4_foldonly`, identity, checksums, Miri

```
O3: unsafe n_fn=128 md5_fn=28432cb848832a692454c3bcc2aee83e md5_raw=044ae7cbea73ebb349f6dcc901d63716
    verus  n_fn=128 md5_fn=28432cb848832a692454c3bcc2aee83e md5_raw=044ae7cbea73ebb349f6dcc901d63716
    identity -> exact, md5_raw_equal: True
O0: identity -> norel                          <- both the pinned levels
```

Gate stage 3c: `ok unsafe vs verus O0: norel` / `ok unsafe vs verus O3: exact`.
All 8 cells agree on all 12 committed inputs, exit codes included.
Gate stage 8: 11 of 12 Miri rows `no UB`, `large.bin` BLOCKED (declared).
`controls/miri_seeds.sh` re-run: **seeds 0–7 × nine small inputs, no UB and no
leak; positive control fires on `-notag`/`-mixed`/`-win1` and is silent on
`small`.** `adversarial-win1.bin` is the sharp input — `len == 1`, so the
do-while runs once and breaks on the first `q == p`.

### The ladder, read out of `results/p42-goto-cleanup.json`

```
rung           small win 97   large win 4096
c-gcc               1873.00         77854.00
c-gcc-h             1873.00         77854.00
c-clang             1506.00         61487.00
c-clang-h           1510.00         61492.00
safe_naive          1850.00         75826.00
safe_tuned          1263.00         50745.00
unsafe              1251.00         50734.00      <- was 1461.00 / 59441.00
verus               1251.00         50734.00

c-gcc      - c-gcc-h      +0.00      +0.00
c-clang    - c-clang-h    -4.00      -5.00
safe_tuned - unsafe      +12.00     +11.00        <- was -198.00 / -8696.00
safe_naive - unsafe     +599.00  +25092.00
verus      - unsafe       +0.00      +0.00
```

### The spelling spans, my own session (`controls/spellings.py --measure`)

```
r4_ship       1407.00    51127.00   SHIPPED, Verus-verified 18/0
r4_idxfold    1617.00    59834.00   admissible; was the shipped rung
r4_add        1407.00    51127.00   NO -- no vstd spec for <*mut T>::add
r4_movptr     1491.00    54710.00   NO -- same
r4_endptr     1455.00    53174.00   NO -- one-past-the-end pointer
r3_ship       1419.00    51138.00   SHIPPED
r3_revidx     1627.00    59845.00
r3_zeroed     1572.00    55298.00
r3_push       2634.00   102846.00
```

**Every one of TASK_109's six figures reproduced to the hundredth.** R4 span
`1407…1617` / `51127…59834`; R3 span `1419…2634` / `51138…102846`. **They
overlap at both ends**, and `NOTES.md` 11b now says a difference whose endpoints
overlap is not a difference — **and refuses the mirror claim too.**

### parity — my own re-derivation, on `build.py`'s own binaries

12 rows, windows **64…527 plus both shipped inputs**, `-5.00` even and `-4.00`
odd throughout, **zero size term over a 32× range**, and the two shipped windows
**predicted from parity rather than fitted**. The size arm is refutable by the
probe's own measurement and did not fire.

⚠ **FOUR terms, not three, and TASK_109's split is corrected.** Attributed by
callgrind `--dump-instr=yes` per instruction inside the kernel symbol
(`.temp/t110/terms.py`), so a register rename cancels:

| term | even | odd |
|---|---|---|
| tag test goes branchless: `setne`+`sete`+`or` replace one `jne` and one `cmp` | +1 | +1 |
| one extra alignment NOP executed per call | +1 | +1 |
| fold-loop preheader address arithmetic: one `lea` → two `mov` + one `add` | +2 | +2 |
| odd-remainder guard's extra `jmp`, **even windows only** | +1 | 0 |
| **`R1h − R1`** | **+5** | **+4** |

TASK_109 called the merge `+3`; it is **`+1` net** — it did not subtract the two
instructions the merge deletes. **The totals were right and the split was not**,
which is why the third term looked even-only-and-positive rather than a `jmp`.

### `controls/leak.sh`, both arms (`.temp/t110/leakteeth.sh`, scratch replica, no repo file touched)

```
ARM 1  unplanted                              exit=0   352 rows, 0 flagged
                                              "ALL 352 POINTS AS DECLARED"
ARM 2  the missing `goto cleanup` PLANTED     exit=1   12 rows flagged
```

The twelve are `kernel` × `{-O0,-O1,-O2,-O3}` × the three inputs that reach the
error path. **The count is now derived from the loop, not written down.**

### `controls/sweep.py`, all seven cells, one session

**The five cells whose rungs did not change reproduced their TASK_104 rows
EXACTLY** — fit, in-sample residual, worst band-B residual and both shipped
residuals — which is what makes the two that moved readable.

```
unsafe/verus  165.611 + 13.04274*w   in-sample 11.69   band-B -310.83
                                     small -23.76   large -2461.65 / -2492.65
              (was 203.161 + 14.59274*w, 5.21, +47.05, -1.66, -141.00 / -172.00)
```

### `.temp/t104/allocclass/rebuild.sh` (m2)

```
checksum agrees on small.bin / sweep-w512.bin
var   184.177 + 18.91424*w   in-sample 1.356   band-B +37.61 .. +39.23
fixed 377.177 + 18.91424*w   in-sample 1.356   band-B +37.61 .. +39.23
```

Refutation reproduces to the digit.

### The two hashed `identity.why` claims, re-measured with arms that must fire

```
  O0  base  identity=norel  n_fn R4= 104 R5= 104  want=norel   OK
  O0  P2    identity=differ n_fn R4= 106 R5= 104  want=!norel  OK -- FIRED
  O3  base  identity=exact  n_fn R4= 128 R5= 128  want=exact   OK
  O3  P1    identity=differ n_fn R4= 127 R5= 128  want=!exact  OK -- FIRED
```

**Both mechanisms reproduce. One count moved and is corrected**: the `O3` pair
is `127` against `128`, in `%r9`, where the hashed `why` said *"120 vs 122 …
`%r8` … two instructions"*. The `O0` pair reproduced exactly (106/104).

### Idiom audit, before → after the M3 repair

| | before | after |
|---|---|---|
| backticked spellings | 16 | **18** |
| (spelling, rung) pairs | 52 | **56** |
| **pairs PRESENT** | **7** | **17** |
| `required_pins_nothing` | 7 | **5** |

The five remaining are the correct C-side scoping of a Rust-only entry.
`goto cleanup` now pins both C rungs; `(uint8_t)(run >> 24)` / `(run >> 24) as
u8` pins all six; `dig[len - 1 - i]` pins both C rungs.

---

## THE THREE CALLS THE MANAGER WAS LEAST SURE OF

### 1. *"That shipping both rungs is right at all."* — **RIGHT, both of them, and neither stop condition triggered.**

The ledger passes the twin regime (**21/0**, the untested item), `_is_trusted`
leaves it out, `_scan_unsafe_sites` is clean, and the gate is green.
`r4_foldonly` passes Miri at the gate and across seeds 0–7, is `exact` at `-O3`
and `norel` at `-O0`, and agrees on all 12 inputs. **There is no refusal to
report.**

⚠ **But temper the framing of the second one.** Shipping `r4_foldonly` does not
give p42 a better headline; it **removes** one. The row used to publish
*"safe-tuned beats unsafe"*; it now publishes *"the R3 and R4 admissible classes
are not separated by this measurement"*, plus two overlapping spans and one
bounded quantity between two named cells. **That is the honest result and it is
weaker than what it replaces** — and `NOTES.md` 11b says so explicitly, and
refuses `+12.00 / +11.00` as a headline in the other direction for the same
reason the old one failed. **The case for shipping is not that the new number is
better; it is that the old one was wrong.**

### 2. *"That the ledger belongs in `verus.rs` rather than in `controls/`."* — **`verus.rs`, and I have a measurement the argument did not have.**

**Delete the leak-freedom `ensures` and the file still reports `18 verified, 0
errors`.** So the obligation is protected by exactly one thing: the textual pin
in `spec.md`'s `verus.items`, and `contract_sha256` as its tripwire. **A control
in `controls/` cannot be pinned that way** — it is not in `verus.obligations`,
its items are not in the item set, and nothing would notice it rotting. Ship it
where the pin can reach it.

The other two arguments hold up on measurement: **zero object code**
(`md5_fn`/`md5_raw` identical to R4's, `identity` still `exact`) and **zero
trusted items** (`_is_trusted` 3, unchanged).

⚠ **The cost you should weigh, and it is real:** `verus.rs` grew from 549 lines
to 712 (about half of that comment),
`kernel` is now a two-line wrapper around `kbody`, and that indirection exists
**for the proof and for nothing else** in a rung whose stated job is to be R4's
exec code plus specs. I kept the pinned signature and put the reason in a
comment at the split, but a reader now meets one more layer before the kernel.
**I still think shipping is right; I would not call the readability cost zero.**

### 3. *"That `r4_foldonly` is really admissible."* — **Yes, and NOT by p23's lever — but the honest answer is sharper than that and you should have it.**

**No tautological conjunct was added and no declaration entry was edited to
admit it.** Driving the real audit: `unsafe.rs`'s and `verus.rs`'s spelling
profile is **unchanged** — they match `std::alloc::alloc` and
`std::alloc::dealloc` (in `dig_alloc`/`dig_free`, which I did not touch),
`(run >> 24) as u8`, and no `forbidden` entry. It is in contract for exactly the
reason the previous R4 was.

⚠⚠ **But that is the point, and it is a finding rather than a reassurance: the
declaration never constrained the fold loop at all.** p23's failure mode is
*"edit the pin to admit a cheaper spelling"*. p42's is *"the pin never reached
the thing that moved"* — which is why a fifth spelling could shift the endpoint
by 210 / 8707 `Ir` with the contract untouched. I **strengthened** what could be
strengthened (`required[3]` now pins `dig[len - 1 - i]` on both C rungs), and
⚠ **I could not strengthen the Rust side**: the four Rust rungs spell the
backwards fold four different ways, and a per-language entry keys on the
LANGUAGE and not on the rung, so no single Rust token covers them.
**So the R4 endpoint is still free to move again**, and `NOTES.md` 11b is
written on that assumption rather than on the assumption that the search is now
finished.

---

## Problems

1. ⚠⚠ **THREE measure/gate passes, and that is a process failure worth naming
   because the task file warned about exactly it.** The pass structure:
   - pass 1 green at `2be2bf3f04df…`;
   - **pass 2** because edit 9 (the 23 → 22 recount) is *inside* the fence — a
     wrong number in the hashed block is worse than a hash move;
   - **pass 3** because a final sweep of the rung sources against my own
     measurements found two more stale comments: `verus.rs` trusted item 2's
     *"still gave `15 verified, 0 errors`"* (a TASK_104-era base count that
     reads as current now the file verifies 18), and `unsafe.rs` SAFETY (3)/(4),
     which described the fold as an index after the do-while replaced it.
     Neither moved `contract_sha256`; both moved `source_sha256`.

   **The transferable part: there is no comment-only escape in a rung source, so
   the rule-6 sweep belongs BEFORE the first measurement and not after it.** I
   did it after, twice. All three passes are green and disclosed in `NOTES.md` 0.
2. **The pattern violated its own rule about run-dependent numbers.**
   `NOTES.md` 11c transcribed Miri **allocation IDs** (`alloc7447` …) into a file
   the gate re-hashes; they came back different on the re-run. Removed. Sizes
   and counts are derived from the input and stay.
3. **The M3 repair nearly created the defect it fixed.** My first draft put file
   names and the retracted span in backticks *inside the entries' explanatory
   prose*, and the audit pinned all of them — **27 spellings, 11 pinning
   nothing**. Caught by driving `idiom_audit` before and after. **Every backtick
   in an entry is a pin, including in the prose that explains the entry.**
4. `large.bin` remains BLOCKED under Miri (>180 s), exactly as
   `miri.blocked_reason` declares. Unchanged by this task.

## Unsure / not done

1. **I did not re-run the R3-side or C-side rungs' Verus/Miri work** beyond what
   the gate does — those rungs are byte-identical to what TASK_104 shipped.
2. **The `strings`-based attribute count is a lower bound.** `strings` over
   `rust_verify` shows what the binary spells literally; it cannot prove no
   further `verifier::` attribute exists. What the negative rests on is (a) none
   of the 22 is a linear mode and (b) `grep -rn affine vstd/` is 0 hits, which is
   where such a mode would have to be *used*. `NOTES.md` 6d says this in the
   text rather than leaving the bullet to overclaim.
3. **The mechanism of the superlinearity is still OPEN** and I did not chase it.
   The refutation reproduces; the cause does not follow from it.
4. **I did not re-derive `NOTES.md` 4's clang-elision table** (`k_arr`/`k_one`/
   `k_cap`/`k_dead`). Nothing in this task bears on it and the C rungs did not
   move.
5. ⚠ **I cannot show that five spellings is enough on the R4 side.** Four was not,
   and nothing in the declaration constrains the fold shape (call 3). The R4
   endpoint is held **by fiat**, and `NOTES.md` 9 now says the measure of a
   search is whether it reached the shapes the pin permits — not how many
   spellings it counted.
6. **Adjacent, not fixed, reported as asked:** `controls/sweep.py`'s docstring
   says *"Cells default to the six measured ones"* while `CELLS` lists **seven**
   (it includes `c-gcc-h`). One word, in a file this task otherwise did not
   touch.

## Memory updates

**None — `.memory/` and `RECAP.md` are manager-only and I did not touch them.**
Durable facts went into `patterns/p42-goto-cleanup/NOTES.md` (sections 0, 3, 5,
6a–6d, 7, 8, 9, 9a, 10, 11a–11e) and `.temp/t110/NOTES.md`. **RECAP finding 39's
material is §A/§B above plus the three calls.**

---

## RUNNING COUNT — 389 → 399

Itemised so any of them can be discounted.

1. **The pinned Verus has 22 `verifier::` attributes, not 23** — a correction to
   TASK_109 A1, and it sat inside `idiom.why`, i.e. inside `contract_sha256`.
2. **The clang `R1h − R1` has FOUR terms and the merge is `+1` net, not `+3`.**
   TASK_109 counted the three `setcc`/`or` without the `jne` and `cmp` they
   replace; the totals agreed only because the parity term absorbed the
   difference. Attributed per instruction by callgrind, both parities.
3. **Deleting the ledger's leak-freedom `ensures` gives `18 verified, 0
   errors`** — the obligation vanishes and no count moves, so the `spec.md` pin
   is the only thing protecting it. This is also the answer to call 2.
4. **`NOTES.md` 11c transcribed Miri ALLOCATION IDs**, which are run-dependent
   and changed on re-run (`7447→7533`, `13213→13345`, `3233→3279`) — the exact
   rule `NOTES.md` 3 quotes against, in the same file.
5. **`NOTES.md` 11d's *"3× to 25×"* was wrong on its own table in BOTH
   directions** (c-clang 2.8×, safe_naive 33.2×) before the rungs moved, and is
   2.8×–33× now.
6. **The do-while R4's out-of-band residual FLIPS SIGN and grows 6.6×**
   (`+47.05` → `−310.83`), so the rung that was best-behaved under extrapolation
   is now among the worst. A structural second reason not to publish a rate: the
   residual shape is a property of the loop, and the loop is what a respelling
   is free to change.
7. **`identity.why`'s `O3` figures were stale for the shipped tree** — `127`
   against `128` in `%r9`, not `120` against `122` in `%r8`. Both hashed claims
   re-measured with arms that must fire; the `O0` pair reproduced exactly.
8. **Every backtick inside an `idiom` entry is a pin, including in the entry's
   explanatory prose** — a repair for an unenforced pin created eleven new
   unenforced pins before it was measured.
9. **`NOTES.md` 11z folded a `rep.block` into the `rep.shout` count**
   (*"five shouts"*); the gate record keeps `loud: 4` and `blocked: 1`.
10. **Wall clock does not resolve the `+11.00 Ir`/call this row now publishes,
    and two `measure.py` runs of the same tree prove it** — `unsafe` vs
    `safe_tuned` on `large` reads `14.93/14.96` in one run and `14.93/14.91` in
    the other. The ordering flips; the `Ir` does not.

Items 1–8 are corrections to measured claims; 9–10 are method. **If you prefer
to count only the first eight, the figure is 397.**

---

## Verdicts asked for, verbatim

```
$ harness/check.py p42
check.py: PASS-WITH-BLOCKED-ROWS

  results/gate/p42-goto-cleanup.json:  failures 0   loud 4   blocked 1
  the four shouts are stage 0b on `idiom.forbidden[0..3]` -- permanent and
  correct, they forbid a STRUCTURE; the blocked row is Miri on large.bin,
  declared in advance by `miri.blocked_reason`.

$ harness/measure.py --check-stale
FRESH       results/gate/p42-goto-cleanup.json    38 source(s)
FRESH       results/p42-goto-cleanup.json         18 source(s) + 12 input(s)
52 record(s) examined, 0 STALE

  and, checked separately, all 37 `source_sha256` entries in the gate record
  hash-match the tree, so the record is about THIS tree.

contract_sha256:
  4a252569067081a55c55c8e6177bc8f6a4f897a57cd59a00c7c000a3da8d29a4   (before)
  2be2bf3f04df0d95890cb59c85c78edc4b98082f5efaecb64a9cffb94438dd6c   (after edits 4-8, gate-green)
  437ae31512cf250acac91e64e289b8cd200dfd83b78797aa3467945b86718d76   (SHIPPED, after edit 9)
```

⚠ **Two gate runs and two `measure.py` runs**, because edit 9 landed after the
first pass. Both are green and `--check-stale` is clean tree-wide.
