# p19 — protocol state machine over a loaded transition table: findings

Read `spec.md` first; it carries the contract and the pins. This file carries
what was measured, what was refused, and what is still open.

---

## 0. The bug class, settled before any cell was built

`TASK_087` made this the first deliverable and the kill risk, in these words:
*"is a real protocol decoder's state index plausibly attacker-reachable out of
range, or is that shape manufactured? … If you conclude the framing is
contrived, REFUSE THE ROW."*

**It is not contrived, and it is not unconditional either.** The condition is
named, it is pinned in `spec.md`'s hashed block as two `forbidden` entries, and
it was settled by five runs before a single cell of this pattern existed.

⚠ **The unflattering sentence, first: p19's bug class is this tree's
THIRTEENTH `index >= len`.** p01, p02, p03, p05, p07, p11, p12, p13, p14, p16,
p17 and p36 all carry it. p36 shipped the twelfth and said so; this says so too.
Its nearest sibling is p36 — an index out of a dispatch table.

### 0a. The two conditions, and the runs that settle them

Probe: `.temp/t87/s0_bugclass.c` (kept; the binaries are deleted and the file
rebuilds them). Built exactly as the gate's stage-7 C recipe
(`gcc -std=c99 -Wall -Wextra -O1 -g -fsanitize=address,undefined
-fstrict-aliasing -static-libasan -static-libubsan`) and also plain `gcc -O2`.

| run | what it is | result |
|---|---|---|
| **A** | the table is a PROGRAM CONSTANT — what flex `-Cf`, ragel or re2c emit | `A pairs=2048 out_of_range_successors=0`; then `A after 1e6 adversarial bytes: max_state=7 NST=8`. **The OOB is UNREACHABLE.** `st` starts at 0 and only ever takes a table value, so if every one of the 2048 successors is in range no byte stream of any length can leave the range |
| **B** | the table is LOADED DATA, one entry names a state that does not exist | plain `-O2`: **exit 0, silent**. ASan: `heap-buffer-overflow` `READ of size 1`, `98 bytes after 2048-byte region`; UBSan: `load of address … with insufficient space for an object of type 'uint8_t'`. Entries 8, 200 and 255 all fire |
| **C** | **the same bug written as a `switch (st)`** | `C st=3 acc=6439731193235263960 default_taken=1` — a wrong answer, **no memory event at all**, ASan and UBSan both silent. **This is p31's death, demonstrated rather than argued** |
| **D** | AppArmor's fix: validate every entry once, then index unchecked | `D REJECT at 856 (entry 200 >= NST 8)`, clean |
| **E** | run B with the table in `.bss` rather than the heap | entry 8 → exit 0; entries 200 and 255 → **exit 139 SIGSEGV** |

**So the memory-unsafe framing holds iff BOTH:** the transition table is loaded
data (run A closes the constant case exhaustively), **and** the decoder
dispatches by indexing rather than by `switch` (run C is the logic-bug shape).
Both are `forbidden` entries in `spec.md`, which forbid a spelling for being
*safe* rather than for being *fast*.

⚠ **p19 is the THIRD pattern to do that, not the first, and an earlier version
of this paragraph claimed these were "the only entries in this tree" that do.
They are not** (TASK_087_REVIEW major 1). The precedent, each with its reason in
its own `idiom.why`:

* **p36** — `forbidden[2]` and `[3]` are `op & 7` and `op % 8`, and `[5]`/`[6]`
  are the same two again on the C side: *"masking the opcode into range is a
  THIRD program — it makes every byte a legal opcode, so the out-of-table input
  stops being adversarial and the pattern's whole security half evaporates."*
  ⚠ **That is the same exclusion for the same reason, in the pattern §0 above
  names as p19's nearest sibling.**
* **p03** — `forbidden[1]` is `& (STACK_CAP - 1)`: *"MASKING IS FORBIDDEN … it
  silently turns an out-of-range access into an in-range one, which is the
  opposite of what this pattern models."*

✅ **The practice is the right one and the correction is only to the
uniqueness.** Forbidding the *safe* spelling is not Rust-in-C-syntax in reverse:
the alternative is a benchmark whose bug is unreachable (run A) or absent (run
C), and p03 and p36 established the precedent before p19 existed.

**Both hold of real DFA decoders, and the precedent is in the Linux kernel.**
`security/apparmor/match.c` (fetched to `.temp/t87/apparmor_match.c`) folds with

```c
pos = base_idx(base[state]) + (u8) *str++;
if (check[pos] == state) state = next[pos]; else state = def[state];
```

— four unchecked loads — licensed by `verify_dfa()` having walked the whole
unpacked table once at policy load:

```c
for (i = 0; i < state_count; i++)
    if (DEFAULT_TABLE(dfa)[i] >= state_count) { pr_err("AppArmor DFA default state out of bounds"); goto out; }
for (i = 0; i < trans_count; i++) {
    if (NEXT_TABLE(dfa)[i]  >= state_count) goto out;
    if (CHECK_TABLE(dfa)[i] >= state_count) goto out;
}
```

The tables are unpacked from a userspace-supplied binary policy blob. Getting
that validator wrong is a live CVE class, and **the CVE this pattern models is
`CVE-2026-23407`** *"apparmor: fix missing bounds check on DEFAULT table in
`verify_dfa()`"* — published 2026-04-01, CVSS 7.8. ✅ **Its description is p19's
kernel, in the CVE's own words** (checked against the CVE Program's API at
`cveawg.mitre.org`, twice, by two agents):

> *"When the verification loop traverses the differential encoding chain, it
> reads `k = DEFAULT_TABLE[j]` and uses `k` as an array index without
> validation. A malformed DFA with `DEFAULT_TABLE[j] >= state_count`, therefore,
> causes both out-of-bounds reads and writes."*

**Validate-once-then-index-unchecked is not a benchmark contrivance; it is the
shipped kernel idiom, and it is exactly p19's R4/R5 rung.**

⚠ **CORRECTION — `CVE-2026-23269` was MISQUOTED AND MISATTRIBUTED, and it is
cited now for the class and never for the shape** (TASK_087_REVIEW major 3).
It is a real CVE, published 2026-03-18, CVSS 7.1, in the same file and the same
validator — but:

* its **real title** is *"apparmor: validate DFA start states are in bounds in
  `unpack_pdb`"*. This pattern used to quote *"AppArmor `unpack_pdb` DFA bounds
  validation hardening"* **in quotation marks**, which is a paraphrase presented
  as a title;
* and it is a **different bug**: an untrusted **start state** indexing
  `dfa->tables[YYTD_ID_BASE][start]`, rejected at unpack time. **p19's walk
  starts at `st = 0` by construction and models no start state at all**, so
  *"that is CVE-2026-23269's shape"* — which stood in `c/kernel.c` and
  `README.md` — named the wrong CVE. **The shape is 23407's.**

⚠ p19 uses the **uncompressed** table (`w[st * 256 + b]`), not AppArmor's
comb-compressed `base[state] + c` with a `check[]` guard. The compressed form
adds a second mechanism this pattern is not about. p19 models `verify_dfa`'s
obligation, not `aa_dfa_match`'s addressing.

### 0b. ⚠ CONTRADICTION OF THE TASK FILE — the harm is SILENT, not SIGSEGV

`TASK_087` §1 and `.memory/06-catalogue.md`'s p19 row both state the harm as
`gcc -O2` **exit 139 SIGSEGV**, from `TASK_086`'s probe. **Runs B and E show
that is a storage-class artefact of the probe, not a property of the bug.**
`TASK_086`'s `harms.c` declared `static uint8_t TBL[NST][256]`, i.e. a
2048-byte object in `.bss`, where row 200 is 51 200 bytes past it and leaves the
segment. p19's table **must** be loaded data — run A shows a constant table
cannot reach the bug at all — and in this harness loaded data lives in the
driver's heap payload buffer, where the identical read is **exit 0, silent**.
ASan and UBSan see it either way.

**So p19's harm row is p02's shape: silent in plain builds, sanitizer-visible.**
The `exit 139` line must not be quoted for this pattern. What *is* reusable, and
is a small finding in its own right: **the same out-of-bounds read is exit 139
or exit 0 depending only on which segment the object lives in, with nothing else
changed.**

### 0c. The behaviour matrix, and the one byte that decides it

**Three blobs that differ in ONE BYTE of ONE TABLE ENTRY behave three different
ways.** `inputs/gen.py` asserts the one-byte distance and prints it every run:

```
adversarial-confuse.bin vs adversarial-oobnear.bin: 1 byte(s) differ, at [769] (8 -> 10)
adversarial-confuse.bin vs adversarial-oob.bin:     1 byte(s) differ, at [769] (8 -> 255)
```

| input | entry | where row `entry` starts | plain `gcc -O2` R1 | ASan + UBSan on R1 |
|---|---|---|---|---|
| `adversarial-confuse` | **8** | window byte 2048 — **inside the window's own message** | exit 0, `16818929156795360448` | **clean**. Defined behaviour: the message is read as a transition row |
| `adversarial-oobnear` | **10** | window byte 2560 — **5 bytes past a 2 560-byte blob** | exit 0, `16147079484928987648` | **`heap-buffer-overflow`**, `READ of size 1`, *"5 bytes after 2560-byte region"*, allocation site `slb_head1_u64_bytes common/driver.c:157` |
| `adversarial-oob` | **255** | window byte 65 280 | exit 0, `4296831195264771264` | **`SEGV on unknown address`**, *"caused by a READ memory access"*, *"AddressSanitizer can not provide additional info"* |

**All three are silent at plain `-O2` — exit 0, wrong checksum, 8 of 8 C cells
at both opt levels and both inline modes.** Every non-R1 cell returns `REJ`
(`16962378195829258944`) on all three.

**So "the sanitizer catches it" is bounded as well**: one attacker byte decides
between no diagnostic at all, a diagnostic that names the object and its
allocation site, and a diagnostic that cannot name anything because the address
is too far out for the shadow map. ⚠ **The middle row is the one an
`index >= len` pattern usually ships, and p19 would have shipped only the
outer two if the family had not been swept** — the first version of this
pattern had `confuse` and `oob` and no `oobnear`, and the ASan line it published
(`heap-buffer-overflow`) was true of neither.

**That family is why p19's memory-safety claim is bounded rather than blanket,
and it is the honest version of the probe's "panic / silent-remap / OOB"
matrix.** ⚠ **The probe's version is NOT what shipped, and the reason is worth
recording**: it needed three *rungs* that compute three different functions on a
bad table (safe-checked panics, safe-masked silently remaps, C reads out of
bounds), and making that the ladder costs the R3-vs-R4 boundary — R4 has no
sound spelling without the validation pass, and masking to make it sound
collapses R4 onto R3, which is `p41`'s death. So all six rungs compute one
function, and the matrix is carried by **three inputs one byte apart** and by
the one rung that skips the pass. The reject / confuse / named-overflow /
unnameable-overflow matrix is strictly more informative than the rung-shaped
one, and it costs no boundary.

⚠ **`sanitizer_expect` is COMPUTED, not declared by name.** `model.py`
simulates `c/kernel.c` and reports whether the walk leaves `[0, n_blob)`;
`inputs/gen.py` re-implements the same detector independently and refuses to
write a blob whose declaration disagrees. Neither half of the matrix can be
mislabelled by editing prose.

---

## 1. The rungs

| rung | cell | the row expression | how it knows `st < NST` |
|---|---|---|---|
| R1 | `c-gcc` / `c-clang` | `w[st * 256 + w[p]]` | **it does not** — the validation pass is missing, and that is the bug |
| R1h | `c-gcc-h` / `c-clang-h` | `w[st * 256 + w[p]]` | the validation pass |
| R2 | `safe_naive` | `tbl[st * 256 + b as usize]` | the language checks it, per access |
| R3 | `safe_tuned` | `tbl[(st & (NST - 1)) * 256 + b as usize]` | it forces it, per access, with a mask |
| R4 | `unsafe` | `*tbl.get_unchecked(st * 256 + b)` | the author asserts it |
| R5 | `verus` | the same, verbatim | **Verus proves it** |

---

## 2. ⚠ The `slb-contract` hash, and the one time it moved

PROTOCOL rule 6. The block's sha256 **as first written, before any measurement**
of this pattern's own cells:

    177d47841871d90c589d083111f84cf0f94f714a6d3a83588a77edd8a10e5c35

Shipped:

    db6e6c5184e9d2203ad461abad41ce11fd7542ee0e08ab4381fec336c720218f

**It moved once, and here is exactly what moved and why.** The first gate run
failed four `[idiom-forbidden]` rows: `forbidden[2]`'s prose said *"the `off`
add cannot be folded into the base pointer"*, and `idiom_audit` extracts **every**
backticked span in an entry as a forbidden spelling — so `` `off` `` was audited
as one and hit all four Rust rungs. The edit removed the two stray backtick
pairs (`` `off` ``, `` `buf.len()` ``) from that entry's explanation and added a
sentence saying the backticked span is the whole of what the entry pins. **No
`required` entry, no `forbidden` spelling, no obligation count, no `identity`
level and no driver token changed.** The `why` gained one sentence and the two
backtick pairs were removed; nothing else in 24 KB of block moved.

⚠ **`git show HEAD:patterns/p19-state-machine/spec.md | diff - …` IS VACUOUS
HERE and is not cited.** It compares the working tree to HEAD, and p19 is a new
pattern that lands in one commit, so on a clean tree it always prints nothing
and always looks like it passed — the failure mode PROTOCOL rule 6 records
against p22. **The two hashes above are the only evidence**, and the first was
written into `.temp/t87/NOTES.md` before `harness/build.py` had ever been
invoked on this pattern.

What *had* been run when the first hash was recorded, stated rather than
implied: `./verus_run.py patterns/p19-state-machine/verus.rs` (`12 verified, 0
errors`; `13` with `--cfg slb_twin`) — those two numbers are the obligation pins
— and the throwaway probes under `.temp/t87/`, which is where the `Ir` figures
quoted inside `idiom.why` and the md5 in `identity.why` come from. No cell of
this pattern had been built.

---

## 3. Inputs

`inputs/gen.py`, deterministic; **regenerated twice into two fresh directories
and diffed: 0 differences**, and the second run reproduced the committed set
byte for byte. ⚠ Two generator edits landed after the first gate run; both times
the blob set was diffed before and after and **only the intended blobs moved**
(`.memory/05-layout.md`'s re-convergence rule): the `degenerate.bin` repair
moved that one blob, and adding `adversarial-oobnear.bin` moved none — each blob
here draws from its own seeded LCG rather than from one advancing stream, so
there is no shared sequence to shift. The gate hashes `gen.py` and never the blobs, so
that determinism is the whole basis of the reproducibility claim.

| input | stride | m | windows | iters | note |
|---|---|---|---|---|---|
| `small.bin` | 2304 | 256 | 16 | 8000 | |
| `large.bin` | 6144 | 4096 | 16 | 2000 | 16× small's fold |
| `degenerate.bin` | 2176 | 128 | 4 | 2000 | all-zero table (valid, folds to 0), all-zero message |
| `adversarial-confuse.bin` | 2560 | 512 | 1 | 100 | entry 8 — state confusion, no memory event |
| `adversarial-oobnear.bin` | 2560 | 512 | 1 | 100 | entry 10 — 5 bytes past the blob; ASan names the object |
| `adversarial-oob.bin` | 2560 | 512 | 1 | 100 | entry 255 — 65 280 bytes past; ASan reports a bare SEGV |
| `adversarial-tiny.bin` | 64 | — | 4 | 100 | below the table size; the kernel's `len <= TBL` branch |
| `adversarial-shortlen.bin` | 2304 | 256 | 2 | 100 | `payload_len` over-declared by 64; exit 5 |
| `sweep-m*.bin` | 2048+m | 19 values | 4 | 400 | the length axis the laws are fitted on |

⚠ **THE REJ PATH CANNOT LIVE IN A NON-ADVERSARIAL BLOB, and the first version
of `degenerate.bin` tried.** A window with an out-of-table entry is exactly a
window on which `c/kernel.c` disagrees with every other rung, so a blob carrying
one is adversarial by construction. The first gate run failed **8 checksum rows
plus the whole-blob agreement row plus the sanitizer row** on it. REJ is covered
by the two adversarial rows, where the four Rust rungs and both hardened C cells
all return it. `gen.py`'s comment carries the reason so it is not rediscovered.

⚠ **Residue classes** (`.memory/03-measurement.md`, the rule that came out of
p38). The regressor is `m`; the unchecked fold unrolls **4×**, so `m mod 4` is
the class that could hide a term. The band covers **all four residues mod 4 and
all eight mod 8** — `gen.py` prints the coverage every run:
`sweep band m: 19 lengths, m mod 4 covers [0, 1, 2, 3], m mod 8 covers [0, 1, 2, 3, 4, 5, 6, 7]`.

---

## 4. Correctness, and what the gate found

`harness/check.py p19` → **PASS**, 0 failures, 0 blocked rows, first complete
run (the run before it failed 16 rows; §2 and §3 say what they were and what
fixed them). `results/gate/p19-state-machine.json`, `complete_run: true`.

* **checksums**: `small.bin` all 32 of 32 cells agree → `4421624378116726888`;
  `large.bin` 32 of 32 → `18289686085753579055`; `degenerate.bin` 32 of 32 →
  `16891030843067612262`.
* **`requires` on every measured input, adversarial included**:
  `off + len <= buf_len` holds on 8000 (`small`) / 2000 (`large`) / 2000
  (`degenerate`) / 100 each on `adversarial-confuse`, `-oob`, `-oobnear` and
  `-tiny` kernel calls, `off` 0…92160 on `large.bin`. ⚠ **That is seven of the
  eight `inputs_checked`, and the eighth is not an omission**:
  `adversarial-shortlen.bin` over-declares `payload_len`, so the driver exits 5
  before the kernel is called at all and `proof_domain` records **0 calls** for
  it. **`ensures` re-derived independently** by `model.py` on 128 sampled calls
  per matrix input.
* **anti-collapse**: 64 cell/probe pairs, marginal `Ir` per call 2269…290931,
  tightest margin 3.9× over the derived floor; `d(Ir)/d(work)` 8.75…56.00.
* **identity**: `unsafe vs verus O0: norel`, `O3: exact` (`md5_fn 0ddbc5381b7d`,
  `md5_raw equal=True`).
* **Verus**: `12 verified, 0 errors`, 3 TCB items, all contracts identical to
  the pins; `main` and `kernel` both have real verified bodies (5 and 3);
  2 `ensures` conjuncts deleted and both load-bearing; 2 `requires` conjuncts
  probed, neither a tautology; 1 verified twin, none justified away.
* **driver**: 5 loops normalise to the pinned 12-statement token sequence.
* **idiom audit**: `20 backticked spelling(s) over 6 rung(s) -> 62 (spelling,
  rung) pair(s), 19 present`; **forbidden: 9 spellings, 0 hits, 0 entries with
  no backticked spelling**; required: 3 pin nothing, 7 scoped-absent pairs.

  ⚠ **The seven absences are the declaration working and `spec.md`'s `why` says
  so in advance**, but the sharpest of them is worth quoting on its own, because
  the gate prints p19's vulnerability as a line of audit output:

  ```
  audit    absent        required[0]  c    c/kernel.c            `>= SLB_P19_NST`
  ```

  Six of the other pairs are `required[2]`'s two row-expression spellings, each
  present in exactly one Rust rung by construction — they **are** the R2/R3
  boundary.

  ⚠ **The three "pins nothing" rows are stray backticks in prose and they are
  left deliberately.** `required[0]` backticks `c/kernel.c`,
  `c/kernel_hardened.c` and `st < NST` while explaining itself; none is a token
  any rung spells, so each audits zero rungs. It is the same class of accident
  as the `` `off` `` that failed the first gate run (§2) — but on the `required`
  side, where the audit *reports* and cannot fail. **Fixing them would move
  `contract_sha256` a second time to remove three benign report rows**, and a
  second unexplained declaration edit is worth less than this paragraph. Noted
  rather than silently carried.
* **Miri**: **8 of 8 inputs** (`miri.runs` in the gate record, one per entry of
  `inputs_checked`), **no UB**, exits and stdout all match the model. No
  blocked rows — the inputs were sized for it (§3). ⚠ This line said *"7 of 7"*;
  the record has eight, and `inputs_checked` has eight (TASK_087_REVIEW minor 3).
* **sanitizers**: `adversarial-oobnear` and `adversarial-oob` fire as declared;
  the other five are clean, and the three matrix inputs match the model's
  stdout under `-O1 -fsanitize=address,undefined`.

### ⚠ The gate's own `Ir` numbers reproduce the disassembly rates

`marginal_ir_per_call` in the gate record is measured by `n_iters` differencing
on the two probe inputs, entirely independently of §8's instruction counting.
The `d(Ir)/d(work)` column is the slope between `small.bin` (stride 2304) and
`large.bin` (stride 6144); the table half of the stride is constant at 2048, so
**`d(work)` is `d(m)` and this column IS the per-message-byte rate**:

| cell (O3, isolated) | small.bin | large.bin | `d(Ir)/d(work)` | §8's disassembly rate |
|---|---|---|---|---|
| `safe_naive` | 9510.00 | 67110.30 | **15.0000781** | 15.00000 |
| `safe_tuned` | 8176.00 | 45616.30 | **9.7500781** | 9.75000 |
| `unsafe` | 7916.00 | 41516.30 | **8.7500781** | 8.75000 |
| `verus` | 7916.00 | 41516.30 | **8.7500781** | 8.75000 |
| `c-gcc` / `c-gcc-h` | 2845.00 / 13087.00 | 45085.72 / 55327.72 | **11.0001875** | 11.00000 |
| `c-clang` / `c-clang-h` | 2274.00 / 7911.00 | 35874.72 / 41511.72 | **8.7501875** | 8.75000 |

The excess over the disassembly rate is `0.0000781` for the Rust rungs and
`0.0001875` for the C ones — a per-call constant divided by 3840 message bytes,
which is the driver's own `println!`/loader term and not a property of the fold.

**Two-point slopes of the differences, exact:**

```
R2 - R4 :  (25594 - 1594) / (4096 - 256) = 24000 / 3840 = 6.25000
R3 - R4 :  ( 4100 -  260) / (4096 - 256) =  3840 / 3840 = 1.00000
```

### ⚠ And two C columns that a reader will not predict

| | small.bin (m=256) | large.bin (m=4096) |
|---|---|---|
| `c-gcc` (R1, **the buggy rung**) − `unsafe` | **−5071** | **+3569** |
| `c-clang-h` (R1h) − `unsafe` | **−5** | **−4.58** |

* **The buggy C rung is cheaper than unsafe Rust at `small` and DEARER at
  `large`, and the sign flip is not about safety at all.** R1 saves the whole
  2048-byte validation pass (a per-call constant, `10242` Ir under gcc) and pays
  11.00 Ir/byte instead of 8.75 in the fold (a slope), because gcc does not
  unroll it. The difference is `2.25·m − 5647`, zero at **m ≈ 2510**.
  **A percentage quoted at either input would be wrong at the other, in sign.**
* **Hardened C on clang and unsafe Rust are within 5 `Ir` per call of each other
  at both inputs** — `0.06 %` at `small` and `0.011 %` at `large`. Same LLVM
  22.1.6 backend, same fold shape (35 instructions for 4 bytes), so **the
  same-backend result** — *clang 22.1.6 is bit-for-bit rustc 1.97.1's LLVM, so
  every C-vs-Rust claim needs the clang column* — gets a fresh instance on a
  data-dependent loop.

  ⚠ **NAMED, NOT NUMBERED, AND AN EARLIER VERSION OF THIS LINE GOT IT WRONG.**
  It cited *"`.memory/01-ladder.md` finding 7"*. That result is **RECAP's**
  finding 7; `.memory/01-ladder.md`'s finding 7 is **p08** and its finding 5 is
  **p17**. The two numbering schemes are the live collision RECAP maps and p36's
  `spec.md` records as having *"already sent agents to the wrong finding"* —
  **cite the result by its sentence, never by a number** (TASK_087_REVIEW minor
  1).

---

## 5. R4 ≡ R5, and the one place the identity pin dictated a spelling

`identity` pins `O0: norel, O3: exact`, which is what the other 22 patterns pin.
**It was established before either rung was written**, not asserted afterwards:
`.temp/t87/id_r4.rs` (plain `rustc`) against `.temp/t87/v19_probe2c.rs` compiled
through `verus_run.py --compile`, both `-C opt-level=3 -C codegen-units=1`, gave
`235 B  ac3fb207cd05963419d722adcd8b9da2` for **both** kernels — extracted from
the **linked** binaries, because a relocated field is zero in an object file and
two kernels differing only in a call target md5 identically there (`TASK_086`
#238).

⚠ **AND THE PIN DICTATED ONE LINE OF `unsafe.rs`.** `verus.rs` takes its
sub-slices with `vstd::slice::slice_subrange`, which is an ordinary out-of-line
call at `O0`. With R4 written as the inline expression `&buf[off..off + len]`,
the two rungs measured `differ` at `O0` — `md5_fn 6b308491b6b4 vs 5e64306475da,
counts [113, 113, 583] vs [83, 83, 395]` — which would have made p19 the only
pattern in the tree not pinning `norel` there. Writing R4's sub-slicing as a
`fn subrange(v, i, j) -> &[u8] { &v[i..j] }` makes both a call at `O0` and both
inline at `O3`:

```
$ python3 harness/asm.py diff .temp/build/p19/unsafe-O0-isolated .temp/build/p19/verus-O0-isolated --sym kernel
identical by raw machine-code bytes      : False
identical with pc-rel fields masked      : True
$ python3 harness/asm.py diff .temp/build/p19/unsafe-O3-isolated .temp/build/p19/verus-O3-isolated --sym kernel
identical by raw machine-code bytes      : True
identical with pc-rel fields masked      : True
```

**This is a case of `.memory/01-ladder.md`'s "a rung covered by an `identity`
pin is chained to the prover", showing up at `O0` rather than in what vstd can
express.** It costs nothing at `O3` — the shipped comparison — and it is
disclosed here because "R4's spelling was chosen to match R5's" is exactly the
kind of thing a reader should be told rather than left to infer.

---

## 6. The proof

`./verus_run.py patterns/p19-state-machine/verus.rs` → **`12 verified, 0
errors`**. With `--cfg slb_twin` → **`13 verified, 0 errors`**.

**The obligation is a LOOP-CARRIED DATA INVARIANT, and that is what is new.**
`st < NST` holds not because of arithmetic on a loop counter but because 2048
bytes read out of the input at run time were all checked once, before the loop,
and `st` is only ever assigned one of them. The two loops:

```
validation:  forall|j: int| 0 <= j < i ==> ((#[trigger] w@[j]) as int) < NST as int
fold:        st < NST,  tbl_ok(w@),
             run(w@, TBL as int, 0, 0) == run(w@, p as int, st as int, acc)
```

and the step that closes it:

```
assert(st * 256 + b < TBL);
assert(((w@[(st * 256 + b) as int]) as int) < NST as int);
```

⚠ **THE OBLIGATION IS EXACTLY WHAT `c/kernel.c` WALKS THROUGH.** That rung is
this program with the validation pass deleted; the invariant then has no
establishing step, the first `assert` is false, and the read leaves the window.
There is no Verus spelling of `c/kernel.c` that verifies. That is the strongest
form of *"the proof is load-bearing"* available: the deleted lines are not an
optimisation the prover happens to reject, they are the premise.

### Sticking points, in the order they were hit

1. **`Could not automatically infer triggers for this quantifier`** on
   `tbl_ok`'s `forall`. Needs an explicit `#[trigger]` on the sequence index.
2. **⚠ And the trigger needs an extra paren pair.**
   `(#[trigger] w[j]) as int < NST` is `error: expected ','`;
   `((#[trigger] w[j]) as int) < NST` parses. Worth writing down — the error
   message names the `as`, not the parens.
3. **`possible arithmetic underflow/overflow` on `off + i`.** The broadcast
   `group_slice_axioms` plus `assert(buf@.len() == vstd::slice::spec_slice_len(buf))`
   supplies `buf@.len() <= usize::MAX`, but it has to be carried **into the loop
   invariants** explicitly.
4. **The `REJ` early exit could not discharge the postcondition** until both
   loop invariants carried `w@ == buf@.subrange(off as int, off + len)`.
   `slice_subrange`'s `ensures` gives it at the point of the call; the loop
   forgets it.

⚠ **A first version of the proof used absolute `buf[off + …]` indexing and also
verified `8 verified, 0 errors` (`.temp/t87/v19_probe.rs`).** It was discarded
on **cost**, not on provability — see §10.

---

## 7. TCB tally — RECOUNTED, not copied

**Three `external_body` items in `verus.rs`, one of them with a contract.**
Counted by hand off the file and cross-checked against the gate's own inventory:

| item | contract | in the TCB because |
|---|---|---|
| `buf_get_unchecked` | `requires i < v@.len()`, `ensures r == v@[i as int]` | the unchecked read. vstd ships no specification for `<[T]>::get_unchecked` — **0 hits at the pinned version**, re-run here rather than inherited from `TASK_086`: `grep -rn "::get_unchecked" ~/tools/verus/vstd/ \| wc -l` → `0` — so the wrapper route is the only one |
| `load_input` | none | argv, file I/O and little-endian decoding. **No `ensures` deliberately**: an `ensures` here would be an axiom about the contents of a file |
| `emit` | none | `println!` is not verifiable |

`slb_twin_buf_get_unchecked` is **not** in the tally: it is `#[cfg(slb_twin)]`,
a cfg no measured build sets, and it is *verified*, not trusted.

⚠ **`vstd::slice::slice_subrange` IS an `external_body` item and it is NOT in
this tally.** The tally counts project-local trusted items (`.memory/04-verus.md`),
which is what `synthesize.py` publishes; a *used* vstd trusted item is a
standing open question about the gate (`RECAP`, the sixth route) and p19 does
not settle it. Saying so beside the number rather than leaving it implied is the
point.

⚠⚠ **AND THE NOVELTY CLAIM THAT USED TO SIT HERE IS FALSE — STRUCK, WITH ITS
METHOD** (TASK_087_REVIEW major 4; re-derived at TASK_088). It read *"p19 is the
only pattern in the tree that calls a vstd exec `external_body` function from
its kernel's exec path … the first pattern for which the sixth-route gap is not
hypothetical."* Three things are wrong with it and the first is the one to
learn:

1. **The `grep` behind it was a WHITELIST of four slice-shaped names**
   (`slice_subrange(`, `slice_index_get(`, `slice_to_vec(`,
   `u64_from_le_bytes(`), so it could only ever have found slice-shaped calls.
   ⚠ **A grep that can only find what you already thought of is not a census.**
   Enumerating **every** exec `#[verifier::external_body]` fn in the pinned vstd
   and grepping all 23 patterns finds **`p27`**: `vstd/raw_ptr.rs:579
   ptr_mut_write` and `:620 ptr_ref` are both exec `external_body`, and
   `patterns/p27-handle-table/verus.rs` calls them at `:586` (in `rec_open`) and
   `:620` (in `rec_read`), both reached from `kernel` at `:626` via `:708` and
   `:776`. **p27's own comment at `verus.rs:564` says so.** So **p19 is the
   SECOND such pattern, not the first.**
2. **The framing re-opened a decision `.memory/04-verus.md` had already closed**
   at TASK_055_REVIEW: one number = project-local trusted items, prose beside
   it, and a second *"vstd relied upon"* column refuted by census and *"must not
   be reinstated"*. That section names this exact case in advance — *"a pattern
   built on `vstd::raw_ptr` … decide how such a pattern is counted BEFORE
   building one"* — and p27 is that pattern.
3. **It was not even the route it named.** The sixth route is about *used* vstd
   `assume_specification`s reaching `check_miri`'s *"no trusted item ⇒ Miri not
   required"* branch. `slice_subrange` is `external_body`, and p19 has three
   local trusted items with `miri.required: true`, so it never reaches that
   branch — while the literal sixth route has been live in nearly every pattern
   all along through `bytes.len()` / `bytes.as_slice()`
   (`vstd/std_specs/vec.rs`).

✅ **None of this moves the number.** Under the decided accounting p19's
`tcb_items` is **3**, and the prose beside it — this section and
`verus.rs:31-35` — is exactly what `.memory/04-verus.md` asks for.

### SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }`; the twin's is `v[i]`. These are the same
operation with and without the language's bounds check, and that is precisely
the substitution the twin regime exists to make: a `requires` too weak to
license the unchecked read is too weak to license the checked one, and Verus can
see the second. The signature, the `requires` and the `ensures` are
character-identical between the two, so nothing but the body differs, and the
gate diffs both against `spec.md`'s pins in both configurations
(`12` shipped, `13` under `--cfg slb_twin`).

**(b) Is the `ensures` COMPLETE with respect to every unchecked operation the
body performs?** The body performs exactly one unchecked operation — a single
one-byte read at index `i` — and the contract states exactly that: `i <
v@.len()` guards it and `r == v@[i as int]` describes its whole result. There is
no second read, no write, no pointer arithmetic beyond the one index, and no
aliasing. This is the clause no oracle covers (TASK_009_REVIEW x4: a body that
also read `i + 1` would pass the contract pin, the twin and the `--cfg` run
unchanged), so it is asserted here on a reading of five lines of code, and Miri
is the backstop: p19's Miri policy is `required: true` and the pair
`unsafe`/`verus` is interpreted on every input, including the two adversarial
ones. **p19 is a pattern where an incomplete `ensures` would be unusually
dangerous, because the index of the unchecked read is a value read out of the
buffer being read** — which is why Miri is not waived here despite R4 and R5
being byte-identical.

**(c) Does each clause mean the same thing in both configurations?** Both
clauses are written in terms of `v@` and `i` only. `v@` is the sequence view of
the slice and `i` a `usize` parameter; neither is `#[cfg]`-dependent, neither
mentions a constant that varies with `slb_twin`, and the token `slb_twin`
appears in this file **only** inside the twin's own `#[cfg(slb_twin)]`
attribute — which the gate enforces, because a `#[cfg]`-varying `const` used in
a `requires` was the bypass that rule closes. So the predicate discharged in the
shipped configuration is the predicate discharged in the twin's.

---

## 8. The cost, and the mechanism — this is the headline

⚠ **Convention, named at every figure**: rates below are
**`fold-loop instructions / bytes per iteration`, read off the disassembly of
the shipped `-O3 isolated` binaries** — not marginals
(`.tasks/TASK_026.md` §0 item 2: a five-decimal rate must come from
`body_len / K`, because the driver's `println!` term does not cancel inside a
single marginal). Inline mode is **`isolated`** everywhere in this section.
`harness/loopbody`-style extraction is in `.temp/t87/loopbody.py`.

| cell | fold-loop instructions | bytes/iteration | **Ir per message byte** |
|---|---|---|---|
| `safe_naive` (R2) | 15 | 1 — **not unrolled** | **15.00000** |
| `safe_tuned` (R3) | 39 | 4 | **9.75000** |
| `unsafe` (R4) | 35 | 4 | **8.75000** |
| `verus` (R5) | 35 | 4 | **8.75000** |
| `c-gcc` (R1) | 11 | 1 | 11.00000 |
| `c-gcc-h` (R1h) | 11 | 1 | 11.00000 |
| `c-clang` (R1) | 35 | 4 | 8.75000 |
| `c-clang-h` (R1h) | 35 | 4 | 8.75000 |

**`R3 − R4 = 1.00000` and `R2 − R4 = 6.25000` Ir per message byte.**

### 8a. The +1.00 is one `and`, and it is attributed by a control, not by eye

The masked fold body is the unchecked fold body plus **literally one
`and $0x7,%edi` per byte**. Two independent routes say so:

* **rolled-vs-rolled** (`-C llvm-args=-unroll-count=1`, a control that changes no
  source): R2 **15**, R3 **13**, R4 **12** instructions per byte. `R3 − R4` is
  `1.00000` rolled *and* unrolled, so the mask is not an unrolling artefact that
  happens to land near 1.
* **add the mask to the UNSAFE rung.** `k_unchecked_mask` — `get_unchecked` with
  the mask applied anyway — measures `+1.00024` Ir/byte against plain
  `k_unchecked`, and its fold body is 39 instructions for 4 bytes, the same as
  R3's. **The +1 is the mask, not the check.**

⚠ **`TASK_087` named this as the manager's least-sure call (c) — *"that
`+0.999 Ir/byte` really is the one `and` instruction rather than an unrolling
artefact that happens to land near 1"*. CONFIRMED, twice over.**

### 8b. The 6.25 is 3.00 check + 3.25 foreclosed unroll, and the third instruction has a name

Rolled-vs-rolled, `R2 − R4` is **3.00**. Unrolled it is **6.25**. So:

```
6.25  =  3.00 (the check)  +  3.25 (the 4x unroll the check forecloses)
```

The rolled bodies name all three instructions:

```
R4 (12):  movzbl b ; shl $0x8,%rdx ; add %rdi,%rdx ; movzbl tbl ; mov ; shl $0x5 ; sub ; mov ; add ; inc ; cmp ; jne
R2 (15):  movzbl b ; mov %rdx,%rax ; shl $0x8,%rax ; or  %r9,%rax ; cmp $0x8,%rdx ; jae <panic>
          ; movzbl tbl ; mov ; shl $0x5 ; sub ; mov ; add ; inc ; cmp ; jne
```

`cmp` + `jae` are the check. **The third is `mov %rdx,%rax`**: the checked
spelling must keep `st` live for the compare, so it cannot destroy it with the
shift the way the unchecked one does. A per-byte cost that is *register
pressure created by the check* rather than the check itself is not something
this project has priced before.

⚠ **AND LLVM LOWERS THE BOUNDS CHECK TO A STATE-RANGE CHECK.** The emitted test
is `cmp $0x8,%rdx / jae`, i.e. `st < 8` — not `st*256 + b < 2048`. **Safe Rust's
automatic bounds check and the validation pass `c/kernel.c` omits are the same
predicate, enforced in two different places**: once per access here, once per
call there. That equality is p19's cleanest sentence.

### 8c. Smaller code, more instructions — reproduced

`safe_naive`'s kernel is **0xe8 = 232 bytes** and `unsafe`'s is **0x19b = 411**,
and the smaller one executes **1.7×** the instructions per byte. The panic body
is out of line; what is in line is a loop the check refuses to let LLVM unroll.
`TASK_086`'s observation holds on the shipped tree.

### 8d. The same-backend column

`c-clang`'s fold is **35 instructions for 4 bytes** — the same shape and the
same rate as `unsafe.rs`'s, on the same LLVM 22.1.6 backend. `c-gcc`'s is
**11 for 1**: gcc does not unroll it at all, so gcc's *unchecked* C fold is
**dearer per byte than safe Rust's masked one** (11.00 vs 9.75). ⚠ Any
C-vs-Rust claim on this pattern needs the clang column — **the same-backend
result again, cited by its sentence and not by a number** (§4; an earlier
version of this line said *"`.memory/01-ladder.md` finding 5"*, which is
**p17**).

---

## 9. The two hardening strategies have different asymptotics

This is p19's second result and it is not about Rust at all.

| strategy | cost | where |
|---|---|---|
| validate the table once per call | **O(table)** — 2048 byte-compares | `c/kernel_hardened.c`, and every Rust rung |
| check every access | **O(message)** — one compare per message byte | `safe_naive.rs` |

Measured per *table* byte in the validation loop, same convention as §8:
`c-gcc-h` **5.00** (rolled, not vectorised), `c-clang-h` and all four Rust rungs
**2.75** (11 instructions for 4 bytes). So the pass costs `2048 x 5.00 = 10240`
Ir/call under gcc and `2048 x 2.75 = 5632` under clang and rustc — a
**constant**, which amortises in the message length, against a bounds check that
does not.

**Both predictions check out against the gate's independent marginals** (§4),
which differ the hardened cell against the unhardened one at fixed input and so
isolate the pass exactly:

```
gcc   :  c-gcc-h  - c-gcc    = 13087 - 2845 = +10242   (predicted 10240)
clang :  c-clang-h - c-clang =  7911 - 2274 =  +5637   (predicted  5632)
```

and the same differences at `large.bin` are `+10242` and `+5637` — **identical,
which is what "a constant, not a slope" means and is the whole claim.**

**They are therefore not interchangeable, and which is cheaper depends on the
message length**, not on the language. At p19's `small.bin` (m = 256) the
validation pass dominates; at `large.bin` (m = 4096) the per-access check does.
⚠ This is exactly the shape `.memory/01-ladder.md` warns about when a pattern
publishes a percentage: quote the slope and name the input.

**And it has a measured instance with a SIGN FLIP in it** (§4): the buggy C rung
`c-gcc`, which pays no validation at all, is **5071 `Ir`/call cheaper** than
unsafe Rust at `small.bin` (m = 256) and **3569 dearer** at `large.bin`
(m = 4096). The difference is `2.25·m − 5647`, so it crosses zero at
**m ≈ 2510**. Neither number is about safety: one is the pass it skips, the other
is the unroll gcc does not do.

---

## 10. Spelling spread — and BOTH sides were searched

`.memory/05-layout.md` step 13 makes this mandatory. `.tasks/TASK_087.md` §3
makes it the trap that has now caught five patterns, plus p36's mirror image.
**So: the lever count on each side, and whether they are comparable.**

Convention: **marginal whole-program `Ir` per kernel call**, `n_iters` 100↔200,
callgrind `I refs:` program total, `rustc -O3 -C codegen-units=1`, every kernel
`#[inline(never)]` (**inline mode `isolated`**), payload from `argv` at run
time, `m = 4096`. Probe: `.temp/t87/cost.rs` + `cost.py`. **Every spelling
prints the same checksum `12831604495418020041`.**

| side | spelling | Ir/call | Δ vs `unchecked` | per message byte |
|---|---|---|---|---|
| **R2** | `tbl[st * 256 + b]` — **shipped** | 67134 | +25592 | +6.24805 |
| R2 | row reslice, then `row[b]` | 67129 | +25587 | +6.24683 |
| R2 | `.get(…).unwrap_or(&0)` | 67141 | +25599 | +6.24976 |
| **R3** | `tbl[(st & 7) * 256 + b]` — **shipped** | 45636 | +4094 | **+0.99951** |
| R3 | mask + row reslice | 45640 | +4098 | +1.00049 |
| R3 | mask on a `&[u8; 2048]` via `try_into` | 45647 | +4105 | +1.00220 |
| **R4** | `get_unchecked` — **shipped** | 41542 | 0 | 0 |
| R4 | `get_unchecked` on both, explicit index | 41540 | −2 | −0.00049 |
| R4 | raw-pointer walk | 41553 | +11 | +0.00269 |

**Three levers a side, spreads of 12 / 11 / 13 Ir/call at m = 4096. The lever
counts are comparable and all three sides are DEGENERATE** — the word
`.tasks/TASK_026.md` §0 item 4 asks for, because it is falsifiable where
"unavailable" is not. **The published `R3 − R4` and `R2 − R4` do not depend on
which of the three is shipped on either side.**

### Levers that are IN CONTRACT and DEARER — the ones worth publishing

| spelling | side | per message byte vs shipped R4 | why it is not shipped |
|---|---|---|---|
| `if st < NST { st } else { 0 }` | R3 | **+8.25000** | the branch clamp is **dearer than the bounds check it replaces** |
| absolute `buf[off + …]`, no sub-slice | R4 | **+2.25220** | the window offset cannot be folded into the base pointer; the fold unrolls 2× instead of 4× |
| absolute `buf[off + …]`, no sub-slice | R3 | **+10.87207** | worse still: the blob length is a runtime value, so the masked index is no longer provably in range and **the check comes back** |

The last two are why `spec.md` forbids `buf[off +` by name and why every rung
takes sub-slices. ⚠ **The absolute-indexing R4 was put through Verus before it
was rejected** — `.temp/t87/v19_probe.rs`, `8 verified, 0 errors` — so it was
rejected on cost with its admissibility established, not waved away
(`.tasks/TASK_026.md` §0 item 3).

### ⚠ Two of `TASK_086`'s probe numbers do not reproduce, and here is why

| `TASK_086` | measured here | cause |
|---|---|---|
| naive **+5.25** Ir/byte | **+6.25** | the probe's fold was `acc.wrapping_add(st)`; p19's is `acc * 31 + st`, which needs `st` in a register the check also needs (§8b) |
| 2-D rows **+4.25** Ir/byte | **+6.25**, i.e. no different from naive | the probe's `k19_rows` took a `&[[u8; 256]; 8]` built by an **`unsafe` cast in its driver**. With the table arriving as payload bytes there is no safe route to that type without a 2048-byte copy, and the reslice spelling that *is* reachable measures the same as naive |

**Neither moves the headline** — both are R2-side spellings and R2 is not the
rung `R3 − R4` is about — but both are corrections to the catalogue row.

### Not the headline

**The number is the matched pair**, `R3ship − R4ship` and `R2ship − R4ship`,
R4 held fixed by fiat. This spread is a result *about method*: it says the
declaration decides which spelling is measured, and that on p19 the declaration
happens to be nearly free on all three sides.

---

## 11. What was NOT done

* **No `safe_naive_verus.rs` control.** p01 ships one to hold up
  `.memory/01-ladder.md` finding 2; p19 does not, and the finding is not
  re-tested here.
* ~~**The `sweep-m*` laws are not re-fitted from the committed blobs in this
  file.**~~ **DONE at TASK_088, and the re-fit CORRECTED them — see §12.** The
  laws this file used to publish, `R2 − R4 = 6.25·m − 8` and
  `R3 − R4 = 1.00·m − 2`, came from a throwaway probe at five message lengths
  and **their intercepts are wrong at every residue class**.
* **No wall-clock analysis.** p19's fold is a serial dependent-load chain
  (`st` gates the next load's address), so it should be latency-bound and `Ir`
  should understate the safe rungs' penalty rather than overstate it — a
  prediction, not a measurement.
* **The compressed (`base[state] + c` with a `check[]` guard) table form is not
  modelled** — see §0a.
* **`sanitizer_expect` on `adversarial-confuse` is "clean" by computation**, and
  no attempt was made to find a build on which it fires. It should not: the read
  is inside the object.

---

## 12. The two laws, RE-FITTED from the committed band — and the intercepts were wrong

**⚠ CORRECTION.** This pattern shipped `R2 − R4 = 6.25·m − 8` and
`R3 − R4 = 1.00·m − 2` in §11 and in `inputs/gen.py`'s docstring. Both came from
the **throwaway five-length probe of §10** (`.temp/t87/cost.rs`, m =
1024/2048/4096/8192/16384). **The slopes survive exactly. The intercepts are
wrong, and they are wrong for TWO INDEPENDENT REASONS — which is worth separating
because only one of them is the residue rule.**

1. ⚠ **The probe was a DIFFERENT BINARY, so its per-call constant was its own
   driver's and never the shipped cells'.** All five of its lengths are
   `m ≡ 0 (mod 4)`, where the re-fit below gives `6.25·m − 6` and `1.00·m + 4`;
   the probe gave `− 8` and `− 2`. The gap is **exactly `+2` and `+6` at every
   `m ≡ 0 (mod 4)`, constant** — the signature of a fixed per-program offset,
   not of a modelling error. **An intercept measured on a probe binary does not
   transfer to the shipped one; only the slope does.** §10's own numbers
   (`+25592`, `+4094` at m = 4096) are the probe's and are correct *as the
   probe's*.
2. ⚠ **And there is a real `m mod 4` term that the probe could not have seen**,
   because a five-point band all at one residue fits in sample and misses out of
   it with no in-sample residual to warn you — `.memory/03-measurement.md`'s
   residue rule, stepped in by the pattern that ships the residue-covering band
   precisely so it would not be.

⚠⚠ **And the shipped laws disagreed with this file's own §4 numbers, two
sections above them**: §4 prints `1594` / `25594` / `260` / `4100` and the laws
say `1592` / `25592` / `254` / `4094` — the `+2` / `+6` of reason 1.

**Re-fitted here from the 19 COMMITTED `sweep-m*.bin` blobs**, on the shipped
`-O3 isolated` binaries, marginal `Ir` per kernel call by `n_iters` 100↔200
differencing (the gate's own convention, §4). Probe: `.temp/t88/refit.py`, log
`.temp/t88/refit.log`. **Zero residual over all 19 lengths, both laws:**

```
R2 - R4  =  6.25*m  -  6  -  2.25*(m mod 4)  -  4*[m mod 4 != 0]
R3 - R4  =  1.00*m  +  4                     -  1*[m mod 4 != 0]
```

Per residue class, which is how the review first stated it, and every class is
exact with zero scatter:

| `m mod 4` | n | `R2 − R4` | `R3 − R4` |
|---|---|---|---|
| 0 | 10 | `6.25·m − 6` | `1.00·m + 4` |
| 1 | 5 | `6.25·m − 12.25` | `1.00·m + 3` |
| 2 | 2 | `6.25·m − 14.5` | `1.00·m + 3` |
| 3 | 2 | `6.25·m − 16.75` | `1.00·m + 3` |

**The slopes are the part that was right, and they are right to six places**:
two-parameter OLS over all 19 lengths gives **`6.250530`** and **`1.000035`**,
and the whole of §8's rate argument stands unchanged.

### 12a. The mechanism, read off the disassembly rather than fitted

`.memory/03-measurement.md` asks for the mechanism, not the residual. **The
`m mod 4` term is R4's and R3's scalar epilogue, and every one of its
coefficients is a counted instruction** (`harness/asm.py show … --sym kernel
--raw` on the shipped `-O3 isolated` binaries):

| | main fold | epilogue body | epilogue preheader, taken | preheader, not taken |
|---|---|---|---|---|
| R4 `unsafe` | 35 / 4 B = **8.75** | **11** / 1 B | `test`,`je`,`add %rsi,%rdx`,`xor`,`mov`,`nop` = **6** | `test`,`je` = **2** |
| R3 `safe_tuned` | 39 / 4 B = **9.75** | **12** / 1 B (the extra `and $0x7,%edi`) | `test`,`je`,`xor`,`mov`,`nopw` = **5** | **2** |
| R2 `safe_naive` | **not unrolled**, 15 / 1 B | — none — | — | — |

So with `r = m mod 4`:

* **R4's excess over a pure `8.75·m` line is `2.25·r + 4·[r ≠ 0]`.** The `2.25`
  is the epilogue byte costing 11 where an unrolled byte costs 8.75; the flat
  `4` is entering the epilogue loop at all (6 instructions instead of 2).
* **R3's is `2.25·r + 3·[r ≠ 0]`** — same `2.25` (12 against 9.75), but its
  preheader is **one instruction shorter**.
* **R2 has no epilogue at all**, so `R2 = 15·m + const` with no residue term —
  which is why the whole `m mod 4` structure of `R2 − R4` is R4's, with the
  sign flipped.

⚠ **The `−1` in `R3 − R4` is therefore one named instruction: R4's
`add %rsi,%rdx`.** R4 rebases the message pointer before the epilogue; R3 keeps
`%rax` as the message base and indexes `(%rax,%rcx,1)`. That is the entire
`m ≡ 0` vs `m ≢ 0` difference in the second law.

### 12b. What a reader should quote

* **The slopes**, `6.25` and `1.00` `Ir` per message byte, which are what §8 is
  about and which nothing here moves.
* If an *absolute* difference at a given `m` is wanted, **the closed forms
  above**, and only with the `m mod 4` term. Extrapolating the old
  `1.00·m − 2` to a small `m` is off by **6** at `m = 64` (measured **68**,
  law **62**) and by **5** at `m = 97` (measured **100**, law **95**) — on a
  quantity of order 60 to 100, i.e. 5–10 %.
* ⚠ **Never a rate divided out of a single small `m`.** R3's own epilogue term
  is `0` at `m = 64` and would be `5.25` at `m = 65`; the per-byte quotient
  moves by more than the mask it is supposed to be measuring.
