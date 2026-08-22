# TASK_064_REVIEW — p47, the denominator, the punchline, and the branch that never came back

Reviewer, adversarial. Everything below was run on this box; probes and logs in
`.temp/p47rev/` (my own subdirectory — nothing of mine was left in `.temp/p47/`).

**Verdict on the three named attacks: A1 UPHOLDS the engineer with a mechanism
they did not have. A2 reproduces to the instruction and the framing is right.
A3 could not be broken by a strictly larger search than the delivery's.** The
defects I found are elsewhere, and two of them are in the *replacement* claims
the task file said had no adversary.

---

## Findings

### major 1 — `m_leak`'s binary has NO generator; p47's headline number is not reproducible from the committed tree

`patterns/p47-ct-compare/controls/gen_controls.py:416-418`

```python
for name, p, kind, _src in made:
    if kind == "verus":
        continue
```

`m_leak` is declared `("m_leak", VERUS_RS, [...], "verus")` at
`gen_controls.py:346-391`, so `--build` writes its **source** and never builds
its **binary**. `ir_table.py::binary()` (`controls/ir_table.py:52-58`) then
returns `None` and `cmd_leak_controls` prints `MISSING`. Measured:

```
$ python3 patterns/p47-ct-compare/controls/ir_table.py --mode isolated \
      --leak-controls --cells m_leak,n_early,h_vol-clang,h_vol-gcc
binary                    k=0        k=127        equal   klast-k000  verdict
m_leak           MISSING
n_early               354.300     6450.300     6482.300    +6096.000  LEAKS
h_vol-clang          5390.720     5390.720     5390.720       +0.000  constant in k
h_vol-gcc            8426.720     8426.720     8426.720       +0.000  constant in k
```

So `NOTES.md:451` (`m_leak … +7088.000`), `NOTES.md:716-718` and
`README.md:69-75` — **the pattern's deliverable** — rest on a binary the tree
cannot rebuild. `CLAUDE.md` "Don't" #1 is explicit: *if a blob has no script
that rebuilds it, write one before finishing.*

**The number itself is correct.** I rebuilt it by hand with the command
`harness/build.py --dry-run` prints for the `verus` cell:

```
$ python3 verus_run.py --compile .temp/p47/ctl/m_leak.rs \
      -o .temp/p47rev/mleakbin/m_leak-O3-isolated \
      -C codegen-units=1 -C opt-level=3 -C debug-assertions=off --cfg slb_isolated
verification results:: 14 verified, 0 errors

m_leak                276.300     7364.300     7364.300    +7088.000  LEAKS
```

Exactly `NOTES.md:451`. **Failure scenario:** the next agent runs the two
documented commands, gets `MISSING`, and cannot tell whether the generator is
broken or the claim is false. Fix is three lines in `build()` (a `verus`-kind
branch calling `verus_run.py --compile`). *I deliberately deleted my own
`m_leak` binary out of `.temp/p47/ctlbin/` — leaving it there would have hidden
this defect from the next reader.*

Two adjacent, smaller reproduction defects in the same file:

- `ir_table.py --leak-controls` iterates `a.cells`, whose default is the **8
  shipped cells** — not `CONTROLS`/`C_CONTROLS`. `README.md:124`'s reproduction
  line therefore prints 8 rows where `NOTES.md:443-454` publishes 12. The four
  control rows need an explicit `--cells`.
- `binary()` falls back to `CTLBIN/{name}-O3-isolated` when a `whole` build is
  absent (`ir_table.py:55`). `h_vol-gcc`/`h_vol-clang` have only isolated
  builds, so `--mode whole` would silently label an isolated figure `whole`. **No
  published figure is affected** — every `h_vol` number in `NOTES.md` 8c is
  isolated — but it is a silent-wrong-answer path in the tool that produced the
  pattern's tables.

### major 2 — "the 4 that ten patterns record" is wrong about NINE of the ten, and the tenth's own 4 is a transcription error

`patterns/p47-ct-compare/NOTES.md:257-259` and `spec.md:380`:

> ⚠ `main` reports **5**, not the 4 that p03, p05, p06, p07, p10, p11, p12, p14,
> p17 and p27 record for the byte-identical driver loop. … the shared off-by-one
> note does not transfer.

Read out of each pattern's own `slb-contract`:

| pattern | its `obligations_note` records |
|---|---|
| p03, p05, p06, p07, p10, p11, p12, p14, p17 | **`main 5`** |
| p27 | `main 4` |

**Nine of the ten already record 5 — the same value p47 measured.** p47 is the
rule, not the exception, and the ⚠ inverts that.

Recounted by direct measurement on three of them (task asked for two):

```
$ ./verus_run.py patterns/p10-fir-stencil/verus.rs   --verify-function main --verify-root
verification results:: 5 verified, 0 errors (partial verification with `--verify-*`)
$ ./verus_run.py patterns/p03-bounded-stack/verus.rs --verify-function main --verify-root
verification results:: 5 verified, 0 errors (partial verification with `--verify-*`)
$ ./verus_run.py patterns/p27-handle-table/verus.rs  --verify-function main --verify-root
verification results:: 5 verified, 0 errors (partial verification with `--verify-*`)
```

**p27 measures 5 and its `spec.md:421` pins 4.** Its decomposition then does not
add up. Every term measured:

```
TABCAP 1  RECSZ 1  SENT 1  run 1  rec_open 1  rec_close 1  rec_read 1
kernel 3  main 5      -> 15        total: verification results:: 15 verified, 0 errors
```

`1+1+1+1+1+1+1+3+4 = 14`, against a pinned and measured total of **15**. p27's
note is arithmetically inconsistent with p27's own pin; nothing in the gate
checks the decomposition, only the total, which is why it passed.

Also mis-stated: the "shared off-by-one note" is not about the value 4. p03 and
p27 both describe *predicted-minus-one* (`p03: predict 6, report 5`;
`p27: predict 5, report 4`). "Does not transfer" is a claim about the wrong
thing.

**Failure scenario:** the manager lands "p47's `main` is anomalous" in
`.memory/04-verus.md` as a durable Verus fact. It is the opposite of anomalous,
and the one pattern that looks different is the one with the error. *Adjacent
work, reported not fixed: p27's `spec.md:421` needs `main 4` → `main 5`.*

### major 3 — `spec.md`'s pinned `collapse.note` still describes the OLD denominator, and `NOTES.md` §12 claims it was changed

`patterns/p47-ct-compare/spec.md:504`, inside the hashed `slb-contract` block:

> `"note": "work_per_call is **bytes of the window** -- \`stride\`, 200 on small
> and 1032 on large -- which is p16's, p05's, p11's, p12's, …"`

Measured, from `model.py` itself:

```
$ python3 patterns/p47-ct-compare/model.py inputs/small.bin inputs/large.bin
small.bin   … stride=200  … work/call=96cmp  …
large.bin   … stride=1032 … work/call=512cmp …
```

`work_per_call` is **96 and 512 byte comparisons**, not 200 and 1032 window
bytes. The note is the pre-repair text verbatim, including both numbers, and it
is the *contract*. The same staleness is in `model.py:10-11`:

```
    work_per_call **bytes of the window** -- `stride`.
    work_unit     "byte"; `work_unit_bits` 8.
```

against `model.py:224-278`, which return `"byte comparison"` and `ncmp*tlen`.

And `NOTES.md:902` — the PROTOCOL definition-of-done item 6 disclosure table —
carries the row

> \| `collapse.note` \| window bytes \| byte comparisons \| the denominator repair of §3 \| …

**That edit was not made.** Confirmed against the commit, not the worktree:

```
$ git show HEAD:patterns/p47-ct-compare/spec.md | grep -o 'work_per_call is [^-]*-- .\{0,80\}'
work_per_call is **bytes of the window** -- `stride`, 200 on small and 1032 on large -- which is p16's, p05's, p11's, p12's,
```

p47 lands in exactly one commit (`e6e86fc`), so the disclosure table *is* the
snapshot — and one of its five rows describes an edit the tree does not contain.
**Failure scenario:** a reader auditing A1 reads the contract, sees "window
bytes, 200 and 1032", recomputes `d(Ir)/d(work) = 0.206 < 0.25`, and concludes
the gate is passing a floor it fails. That is exactly the audit A1 exists to
invite.

### minor 1 — `work_unit_bits = 8` for a two-byte unit, against p10's identical-shape precedent of 16

`patterns/p47-ct-compare/model.py:227-231` declares 8 for a unit its own
docstring describes as *"two window bytes read, one xor"*.
`patterns/p10-fir-stencil/model.py` has the structurally identical unit and says:

> "One unit is one tap: one sample byte times one coefficient byte, accumulated.
> **Two bytes are consumed per unit, so 16 bits.**" → `return 16`

p07 declares 32 for a probe that reads one u32. p47's 8 is the only two-byte
unit in the tree declared as one byte. **Latent, not live:** `work_unit_bits`
only sets `bound = MIN_DECLARABLE_IR_PER_BIT × work_unit_bits`, which is
consulted only when `min_ir_per_work` is declared, and p47 declares none. It
does put a 2×-low `collapse_floor_min_declarable: 0.015625` in
`results/gate/p47-ct-compare.json` where p10's shape records 0.03125. It is also
the second of the two knobs `.memory/02-bench-rules.md:376-393` warns compose,
moved in the loosening direction in the same commit as the first.

### minor 2 — `m_hdr` is quoted as "11 verified, 2 errors"; the verification-results line says 1

`patterns/p47-ct-compare/NOTES.md:694-697`. Measured:

```
$ ./verus_run.py .temp/p47/ctl/m_hdr.rs
7:  error: invariant not satisfied at end of loop body
19: error: precondition not satisfied
32: verification results:: 11 verified, 1 errors
33: error: aborting due to 2 previous errors
```

The 2 is rustc's *previous-errors* count, not Verus's. Both error **texts** in
`NOTES.md` are correct and the mutant fails as required; only the count is
transposed from the wrong line, in a block presented as pasted output.
(`m_noguard` reproduces exactly: `11 verified, 1 errors`.)

### minor 3 — `README.md` carries none of `NOTES.md` §14's scoping

`README.md:47-48`: *"`Ir` under callgrind is not a proxy for the harm here — it
**is** the harm"*, and the rung table at `README.md:17-24` says "leaks? **no**"
for five rungs unqualified. `NOTES.md:947-956` is careful and correct — *"`Ir(k)`
constant is a necessary condition that p47 measures exactly, not a sufficient
one"*, with cache and port pressure named as unmeasured and the branchless /
data-independent-address argument read off the disassembly. **None of that
reaches the summary file**, which is the one a reader quotes. This is the p10
shape the task named: the headline states more than its own metric supports.
One sentence in `README.md` closes it.

### minor 4 — `NOTES.md` §8e's prose on `u_winu` reads as a near-miss; it is the shipped object

`NOTES.md:625`: *"`u_winu` removes that panic pad and is `exact`"*. Measured:

```
unsafe        md5_raw=4d99e76e0b10  md5_raw_norel=c52ba8187b22  n_raw=174
u_winu        md5_raw=4d99e76e0b10  md5_raw_norel=c52ba8187b22  n_raw=174
u_winu_verus  md5_raw=4d99e76e0b10  md5_raw_norel=c52ba8187b22  n_raw=174
```

`u_winu` is **byte-identical to the shipped R4**, not a variant that removes
something from it. The table's own 434.000 / 605.700 says so; the prose does
not. The conclusion drawn ("nothing found moves it down at `exact`") is right
and *stronger* than the prose suggests.

### minor 5 — `P(R3>R4) = 1.000` is the retracted statistic wearing the sanctioned one's clothes

`.memory/03-measurement.md:1075-1076` licenses pairwise `P(A > B)` over all `N²`
layout pairs, *"a genuine proportion, flat at every `N` (58.1 → 58.4 across
N = 4…30)"* — measured at ≈0.58, mid-range. p47's value is **saturated**:
`P = 1.000` ⟺ `min(R3) > max(R4)` ⟺ the bands are disjoint, which is exactly
the *"worst-vs-best range / disjoint bands"* statistic retracted six lines above
for widening 28.91% → 30.78% on the same binaries and flipping a verdict. The
flatness measurement does not cover the ceiling. Nothing is withdrawn — the
engineer publishes the convergent median beside it (+21.95% paired n=24 /
+21.62% cross n=576) and correctly refuses a magnitude for R2-vs-R4 at
`P = 0.043` with a range crossing zero — but `README.md:104,106` quotes the
saturated proportion as the evidence and it should be the median.

### minor 6 — `NOTES.md` §1's "vector ops" column is the one column I could not reproduce

`NOTES.md:171-178` gives 18 / 22 / 22 / 22 / 22. An independent count of
instructions mentioning `xmm|ymm|zmm` in the same kernel symbols gives
27 / 32 / 32 / 32 / 32. A definition difference, almost certainly; no claim
rests on it; but the column is not checkable as written. Every other column of
that table reproduced exactly (below).

---

## A1 — the denominator. UPHELD, with the mechanism the delivery did not have

**The premise is exact.** Recomputed from the committed gate JSON, and matching
`.temp/p47/gate1.log:273-282` line for line:

| denominator | O3 cells failing `d(Ir)/d(work) ≥ 0.25` |
|---|---|
| window bytes (200 → 1032) | **10 of 16** — 0.189 … 0.245 |
| byte comparisons (96 → 512) | **0 of 16** — 0.377 … 0.567 |

`(606−434)/(1032−200) = 0.2067`; `(606−434)/(512−96) = 0.4135`. Both figures in
`NOTES.md` §3 are right.

**Is "byte comparisons" the honest unit? Yes, and the disassembly settles it
where the delivery only argued from two whole-program marginals.** Extracted
independently (the `$0x10`/`$0x20`-bump loop, `.temp/p47rev/`):

```
safe_tuned / c-clang-h   11 insns per iteration, 32 bytes of EACH tag = 64 window bytes
unsafe / verus           12 insns per iteration, 32 bytes of EACH tag = 64 window bytes
```

**11/64 = 0.172 and 12/64 = 0.188 Ir per window byte at the asymptote.** A
0.25 Ir/window-byte floor does not merely embarrass this kernel — *it forbids
it*, which is precisely the test `.memory/02-bench-rules.md` names ("a floor
that forbids the fastest correct implementation is not a floor"). And it gets
worse on wider ISAs: under `clang -march=native` LLVM fuses the xor and the or
into `vpternlogq` and reaches 11 insns per 128 bytes per side = **0.043 Ir per
window byte**, 5.8× under the floor.

**Is p47 the only pattern whose unit consumes more than one input byte? No —
and it is the third pattern to re-denominate away from window bytes, two of them
in direct response to this same gate stage failing.**

| pattern | unit | bytes per unit | why it moved |
|---|---|---|---|
| p07 | `probe` | 4 | a byte floor "would fail a perfectly healthy pattern" — 262 229 Ir/call against ~21 400 achieved |
| p10 | `tap` | **2** | a byte floor "would understate the work by a factor of `taps`" — moved to make the check *stricter* |
| p13 | `DST_CAP*K + S` | — | *"`stride` … is WRONG for p13, **and the gate caught it**"*: `d(Ir)/d(work)` negative in 16 of 32 cells |
| p47 | `byte comparison` | **2** | this task |

p13's `model.py` calls its own version of this event *"the gate doing exactly
its job: the denomination, not the kernel, was the defect."* p47's move is the
prescribed repair, and `harness/check.py:1755-1760` prescribes it in so many
words: *"the fix is to **re-denominate `work_per_call` in the thing the kernel
touches**."*

**Would it have been chosen the same way if the gate had passed?** The honest
answer is *probably not, and it does not matter* — because the alternative the
engineer names (`min_ir_per_work`) would have been **wrong**, not merely more
visible. Any declared rate had to sit at or below 0.189 to admit `c-clang`, and
the true achievable rate is 0.043; a declared 0.189 would have been a number
fitted to the measurement, which is the direction test's actual target. The
denominator is a fact about the algorithm, and it is the same fact on every
input. **The direction test does not bite here.**

**Is `collapse-ir` now a check each pattern can define its way past?** It always
was, and the project already says so — `.memory/02-bench-rules.md:215`
(*"`work_per_call` is unbounded; shrinking it 16× passes with a shout. Nothing
checks it is denominated in the unit `work_unit_bits` names"*) and :353-364,
recorded since TASK_008_REVIEW. p47 neither creates nor widens that. Two
measurements on how much it matters here:

1. **The redenomination did not neuter p47's floor — it left p47 with the
   tightest anti-collapse margin in the tree, by a factor of 2.4.**

   ```
   p47-ct-compare      2.93x    <- tolerates a 65.9% work loss
   p01-array-sum       7.02x
   p03-bounded-stack   7.47x
   …
   p02-buffer-copy    35.94x
   p14-field-split    57.76x
   p27-handle-table  134.45x    <- tolerates a 99.3% work loss
   ```

2. **The unit change is in the record; the magnitude is not.**
   `results/gate/p47-ct-compare.json` carries
   `"collapse_work_unit": "byte comparison"` where p02 and p27 carry `"byte"`,
   so a reader diffing gate records sees it. But `work_per_call` itself appears
   **nowhere** in any gate JSON (`grep -c work_per_call` → 0), so a *halving of
   the denominator under an unchanged unit name* would leave no trace. That is
   the documented residual, unchanged by p47, and it is the one thing about this
   stage I would still call open.

---

## A2 — the punchline. VERIFIED, and the framing is right

Everything re-run from scratch:

```
verus.rs                                            12 verified, 0 errors
verus.rs --cfg slb_twin                             13 verified, 0 errors
verus.rs --verify-function kernel --verify-root       3 verified, 0 errors
verus.rs --verify-function main   --verify-root       5 verified, 0 errors
m_leak.rs                                           14 verified, 0 errors
m_leak.rs --verify-function kernel --verify-root      3 verified, 0 errors
m_leak.rs --verify-function lemma_xacc_sticky --verify-root
                                                      2 verified, 0 errors
m_noguard.rs   11 verified, 1 errors  (invariant not satisfied before loop)
m_hdr.rs       11 verified, 1 errors  (invariant … end of loop body; precondition not satisfied)
```

`12 + 2 = 14`, and **`kernel`'s own term is 3 in both files**. Rebuilt binary:
`276.300 / 7364.300 / 7364.300`, **`+7088.000`**, and identical checksums to the
shipped `verus` cell *and* to `model.py` on all seven inputs.

**Is `m_leak` the same program modulo the leak?** Diffed. Not one character of
the kernel signature, the `requires`, or the `ensures` differs. The exec delta
is exactly one conjunct — `while i < tlen` → `while i < tlen && d == 0`.
Everything else added is a `proof fn`, a `proof {}` block and two `assert`s, all
erased before codegen — confirmed on the object: `m_leak`'s kernel is 68
instructions against the shipped 162, and the difference is the early exit, not
the lemma.

**Does the shipped `verus.rs` prove anything `m_leak` does not? Yes — but not in
the specification, and that is the sharpest form of p47's point.**

- Shipped (`verus.rs:338-364`): the loop invariant is
  `xacc(buf@, base, tlen, i, d) == xacc(buf@, base, tlen, 0, 0)`, and the single
  exit gives `i == tlen`, so the base case yields `d == xacc(…, 0, 0)` — **the
  accumulator's exact value**.
- `m_leak`: the same invariant survives, but the loop can exit with `i < tlen`,
  so the base case splits and `lemma_xacc_sticky` gives only
  `d == 0 <==> xacc(…, 0, 0) == 0` — **the accumulator's zero-ness**.

The shipped file therefore proves a strictly stronger *intermediate* fact. It
buys nothing at the interface, because `tag_fold` folds the **verdict** and
never the accumulator, so both discharge the identical `ensures`. **No clause of
the contract distinguishes the two programs.** The sentence *"the proof
certifies a leaking kernel"* is exactly right, and the precise version — *the
extra strength the honest proof carries is invisible in the specification the
ladder certifies* — is stronger than what `NOTES.md` §9c currently says.

---

## A3 — "the optimiser never reintroduces a branch". I could not break it either

Probe `.temp/p47rev/a3/ct.c`: seven spellings — plain or-accumulate,
`__builtin_expect(d==0,1)`, `__builtin_expect(d!=0,1)`, `__builtin_expect` **on
the accumulator inside the loop**, wide-word or, a caller that branches on the
result with the callee `static inline`, and the same caller with
`__builtin_expect` on its branch. Plus `.temp/p47rev/a3rs/ct.rs`: the **exact
shipped R3 spelling** `fold(0u8, |acc,(x,y)| acc | (x ^ y))`, the shipped R4
`get_unchecked` spelling, a branching caller with `#[inline(always)]`, and the
leaking `a == b` as a **detector control**.

Detector: whole-program *and* per-function self-`Ir` at `k = 0` vs `k = n−1`,
n = 256, 400 reps, callgrind with name-compression and `calls=` inclusive-cost
handling done properly (`.temp/p47rev/a3/cgfn.py`).

| configuration | gcc 13.3 | clang 22.1 | rustc 1.97 |
|---|---|---|---|
| `-O3` | 0 | 0 | 0 |
| `-O3 -flto` / `-C lto=fat` | 0 | 0 | 0 |
| **PGO**, trained 100% on mismatch-at-byte-0 | 0 | 0 | — |
| `-march=native -mno-avx512f` (AVX2) + LTO | 0 | 0 | 0 (`target-cpu=skylake`) |
| AVX2 + LTO + PGO | 0 | 0 | — |

`0` means `Ir(k=0) − Ir(k=n−1) = 0` **exactly**, per function, for every
spelling. Sixteen binaries; not one grew a data-dependent exit.

**The detector is not blind:** the same instrument, same runs, reports the
leaking Rust `a == b` at **+18 448 Ir** whole-program over the same `k` range.

**`-march=native` / AVX-512, read statically** (see the method gap below).
`clang`'s `ct_plain`:

```
vmovdqu (%rsi,%rcx,1),%ymm4 … x4
vpternlogq $0xf6,(%rdi,%rcx,1),%ymm4,%ymm1 … x4     <- xor and or FUSED
sub $0xffffffffffffff80,%rcx ; cmp %rcx,%rax ; jne  <- latch on the index
…
test %cl,%cl ; sete %al                             <- verdict is a SETE, not a branch
```

`gcc`'s emits a fully peeled 15-way scalar tail whose every `jae` tests
`lea 0x_(%rax),%r8` against `%rsi` (the **length**) and never `%edx` (the
accumulator). A scripted check across all five AVX-512 binaries × seven
spellings — *does any `test`/`or`/`ptest`/`pmovmskb`/`kortest` feed a
conditional jump?* — returns **0 hits in 33 of 33 functions**.

**Verdict: the claim survives a strictly larger search than the delivery's** —
LTO, PGO with an adversarially biased profile, AVX-512, `__builtin_expect` in
three placements, and a branching caller, in both C compilers and in rustc.
Where the delivery could say "not one of 5 × 2 × 5 spellings", this can add
"and not under LTO, PGO or AVX-512 either". Optimisers here move *away* from
branching: `vpternlogq`, `cmovne`, `sete`, `pcmpeqb/pmovmskb/cmove`.

### …but A3's instrument has a hole, and it is worth recording

**`-march=native` binaries cannot be measured by `Ir` on this box at all.**

```
$ valgrind --tool=callgrind ./ct_gcc_native 256 0 2
vex amd64->IR: unhandled instruction bytes: 0x62 0xE2 0xFD 0x28 0x7C 0xC1 …
valgrind: Unrecognised instruction at address 0x400113e.
Process terminating with default action of signal 4 (SIGILL)
```

valgrind 3.27.1 cannot decode the EVEX encodings gcc, clang and rustc all emit
for Cascade Lake. So **p47's entire instrument — `Ir(k)` — does not exist for any
AVX-512 build**, and the AVX-512 third of A3 rests on disassembly alone.
`.memory/02-bench-rules.md:224-229` says *"Nothing on this box builds with
`-march`, so it is not live — but a pattern that adds one must re-argue ALPHA."*
It should also say that such a pattern **cannot be measured**, which is a harder
constraint than re-arguing a constant. (It also strengthens A1: at AVX-512 the
window-byte rate is 0.043, so the floor would have to move regardless.)

---

## Clean negatives — every attack I ran that did not land

**Reproduction (all exact, independent of the pattern's own tooling where noted)**

1. Gate re-run `harness/check.py p47`: **PASS**, and the written JSON is
   **byte-identical** to the committed one — 0 of 850 flattened keys differ.
2. `collapse-ir` first-run failure reproduces from the committed gate JSON to
   three decimals on all ten cells.
3. `NOTES.md` §1 kernel table, counted independently with objdump:
   89/1, 69/1, 203/11, 282/10, 174/0, 174/0, 215/0, 176/0 — **exact on both
   columns**.
4. `safe_naive` = 1 `bcmp` + 2 `slice_index_fail` + 8 `panic_bounds_check`;
   `safe_tuned` = 2 + 8. The "identical panic-path structure, R2's only extra
   call is the `bcmp`" claim holds — this is what makes `R2 − R3` the clean pair.
5. `NOTES.md` §1a tag-loop table, extracted independently by induction-bump:
   7/16 = 0.437500, 11/32 = 0.343750 ×2, 12/32 = 0.375000 ×2. **Exact to six
   decimals, and interior conditional branches = 0 in all five.**
6. `safe_tuned` and `c-clang-h` do emit the same eleven mnemonics in the same
   order (register allocation differs; the listing quoted in `NOTES.md` is
   `c-clang-h`'s).
7. `unsafe`'s twelfth instruction is the second induction bump
   (`add $0x20,%r14` **and** `add $0x20,%r11`) — confirmed.
8. `unsafe ≡ verus` byte-identical, `md5_fn a3898fc70d69` — the exact digest
   `NOTES.md` §8 quotes.
9. `c-gcc → R_X86_64_JUMP_SLOT memcmp`, `c-clang → JUMP_SLOT bcmp`,
   `safe_naive → GLOB_DAT bcmp`. The clang `memcmp==0 → bcmp` rewrite is real,
   and the consequence (*`c-clang` vs `safe_naive` is a **library** result*) is
   stated in `spec.md:150-157` and separated in `NOTES.md` §4b. **Attack failed.**
10. No `rep` and no `div` in any of the eight kernel symbols — recounted
    independently. Both `.memory/03-measurement.md` hazards are genuinely empty.
11. The headline `Ir(k)` table: **all 16 numbers reproduce, both inline modes**,
    spread exactly `0.000` / `184.000`.
12. Additivity extrapolation: 40/40 exact, `max|resid| = 0.000000` per rung, in
    **both** modes. Re-run.
13. `volatile`: `h_vol-clang` 646.000 / 2829.280 → 1.46× / 4.55×; `h_vol-gcc`
    914.000 / 4329.280 → 2.17× / 6.71×; on the adversarial window
    5390.720/798.720 = **6.75×** and 8426.720/870.720 = **9.68×**. **Every figure
    exact.** The claim inverts the received advice and is correct on this
    toolchain.
14. `n_early` +6096.000 over 8 × 127 = **6.000 Ir per leaked byte exactly** —
    reproduces.
15. R3-side span: `t_win` 520.000/735.700, shipped 524.000/747.700, `t_split`
    532.000/759.700, `t_iter` 1328.000/5419.700 — all exact.
16. R4-side: `u_win` 410.000/581.700 (−24.000 on both blobs), `u_winu`
    434.000/605.700, `u_end` 475.000/674.700 (+41.000/+69.000) — all exact.

**R4-side spot-checks (the two the task named)**

17. `u_win` identity: `md5_raw` c822209a2c79 vs its twin's 781306e1b3e7 —
    **differ**; `md5_raw_norel` 5aadd4131a6f — **match**. Level is `norel`, not
    `exact`, exactly as claimed, and `u_win_verus.rs` verifies 12/0. Excluded by
    the identity pin alone. **Attack failed.**
18. `u_winu` identity: `md5_raw` 4d99e76e0b10 on both — `exact`, and equal to the
    **shipped** R4's. Verifies 12/0.
19. **Is `u_winu`'s fourth trusted item really forced? Yes — and it is worse than
    the delivery says.** `get_unchecked` appears **nowhere** in
    `~/tools/verus/vstd/`, for any index type, so no route to it exists without a
    new axiom. And `slice_unchecked` is `external_body` + `requires` + `ensures`
    + `unsafe` body, which puts it *inside* the verified-twin regime
    (`.memory/04-verus.md:820`) — `u_winu_verus.rs` supplies no twin for it, so
    shipping it costs a fourth axiom **and** a fifth item, and would fail gate
    stage 5c-twin as written. The conclusion "nothing found moves it down at
    `exact`" holds a fortiori.

**Verus**

20. Both must-fail mutants fail, with the stated error texts.
21. `--cfg slb_twin` → 13/0, i.e. 12 + the single trusted item, as pinned.
22. `verus.rs` contains no `assume`, no `assume_specification`, and exactly three
    `#[verifier::external_body]` items — recounted. TCB 3 is right, and the
    SLB-TRUSTED-ARGUMENT (a)/(b)/(c) block's factual claims check out: the
    trusted body contains one `*`, one `get_unchecked` and nothing else.

**Wall clock**

23. The population arithmetic is internally consistent: 24 layouts/cell,
    24 × 24 = 576 cross pairs, medians +21.95% paired / +21.62% cross.
24. `P(A>B)` over `N²` pairs is the **sanctioned** statistic
    (`.memory/03-measurement.md:1075-1076`), not the retracted range or
    dominance. My "inflated n" attack **fails** — the pairing is the project's
    own convention. (What survives is narrower and is minor 5 above: the value is
    saturated.)
25. The refusal to publish an R2-vs-R4 magnitude at `P = 0.043` with a range
    crossing zero is correct and conservative.
26. The withdrawal of the `large.bin` wall-clock row (estimator dominated by an
    8.4 MB load, produced negative ns/call) is correct.

**Scratch-directory contamination**

27. **No p14 figure depended on the deleted `.temp/p14/clay`.** p14's published
    layout figures are inline text in `NOTES.md` §11a (`n_fn [185]`,
    `md5_fn_norel 9bdc8469333f`, 24 builds/cell, CONTROL 1 quoted), the
    population is `.temp/` and gitignored, and
    `patterns/p14-field-split/controls/clayout.py:59` still points at
    `.temp/p14/clay` and recreates it on `--build`. p27's is repointed to
    `.temp/p27/clay` at commit `915bb8a` and its gate is PASS / 0 failures.
    *Residual, reported not chased:* p27's **own** published population was
    produced while its control wrote into p14's directory. p27's CONTROL 1
    (single-valued `n_fn`/`md5_fn_norel` per cell) would have caught a foreign
    binary — p14's kernel is `n_fn 185` — so p27's figures are protected by its
    own control rather than by luck.

**Other**

28. `model.py`'s `selfcheck()` is a real two-implementation check — Python's
    early-exiting `bytes.__eq__` against a byte-wise or-accumulate mirroring the
    Verus spec fns — and returns `[]` on all 7 non-sweep inputs.
29. `sanitizer_expect = "clean"` unconditionally is honest, not a swept-up
    table: `c/kernel.c` reads only inside the window its own guard proved
    present, and the window guard is in **every** rung including R1.
30. The `-O0` cells clear the floor by 23× … 82×, so no perf claim in this
    pattern rests on an `O0` row; every published figure names `-O3` and its
    inline mode.
31. Both `forbidden` edits disclosed in `NOTES.md` §12 check out as *narrowing*:
    `memcmp` is genuinely `required` in `c/kernel.c`, so the universal entry was
    self-contradictory from the first draft, before any `Ir` was taken.
32. The four `adversarial-*` rows do what they claim: `k000` and `klast` print
    the identical checksum `15618968502624590848` on the shipped `verus` cell,
    on `m_leak`, and in `model.py`.

---

## Premises in the task file that are wrong

- **"the 4 that ten patterns record"** — wrong about nine of the ten (they
  record 5); the tenth records 4 and measures 5. The task file was right that
  one of the two statements is wrong about ten patterns; it is the engineer's,
  and the error also propagates backwards into p27. See major 2.
- **"A1 is the direction test's exact shape"** — it has the shape and fails the
  test on the merits: the repair is prescribed by `harness/check.py:1755-1760`,
  by `.memory/02-bench-rules.md`, and by three prior patterns (p07, p10, p13),
  two of which made the identical move after the identical gate stage failed.
  See A1.
- **"the engineer chose it over the alternative they name (`min_ir_per_work`),
  which would have been a visible declaration edit"** — the visible alternative
  would also have been the **wrong** one: it requires declaring a rate fitted to
  the measurement (≤0.189) when the achievable rate is 0.043.

## Not done / unsure

- I did not re-measure the 61-row `R3 − R4` difference laws (§8a), the closed
  per-function decompositions (§8e/§8f), or the `sweep-t*` band. The `sweep-k`,
  `sweep-x` and `ir_table` figures I did re-measure were all exact, so I have no
  reason to doubt them, but they are unattacked.
- I did not re-run `controls/clayout.py --build/--time`; the wall-clock review is
  a read of the method and the published statistics, not a re-measurement. 13
  reps × 72 binaries was out of proportion to the remaining scope.
- The `-march=native` half of A3 is **static only**, for the SIGILL reason above.
  A dynamic AVX-512 result is not obtainable on this box with this valgrind.
- I could not reproduce `NOTES.md` §1's "vector ops" column under any counting
  rule I tried (minor 6); it may simply be a different mnemonic set in
  `controls/loops.py`.
- `harness/check.py p47` was re-run once (permitted). No other pattern's gate was
  touched. I ran `verus_run.py` read-only against p03, p10 and p27's `verus.rs`
  — it copies into `.temp/verus/run.*` and cleans up, and writes nothing under
  `patterns/`.
