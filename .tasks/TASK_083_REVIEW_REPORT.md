# TASK_083_REVIEW_REPORT — review of TASK_082, and the next pattern

**Role:** research reviewer. Written incrementally from `.temp/r83/NOTES.md`;
every number below was run on this box, and the command is beside it.

Scratch: `.temp/r83/` (`ls`'d first — did not exist). Nothing in `patterns/`,
`.memory/`, `harness/`, `results/`, `synthesis/`, `common/` or `pilot/` was
edited. No `git add`/`git commit`.

---

## Findings at a glance

| # | sev | where | one line |
|---|---|---|---|
| 1 | **blocker** | `vparse.py:513-519` | `#[verifier::external_trait_specification]` is a body-less trusted declaration the matcher misses; `2 verified, 0 errors` while the program prints 7 |
| 2 | **blocker** | `vparse.py:475-478`, `check.py:3739` | `#[verifier::external_fn_specification]` verifies a lie and is neither an axiom nor a TCB item |
| 3 | **blocker** | `check.py:3615`, `:3759` | an `assume_specification` in a `#[path]`-included subdir module is invisible; `os.listdir` is flat |
| 4 | **major** | `synthesis/synthesize.py:854` | the published TCB column reads `tcb_items` and never `axiom_decls` — blocker 1 is half fixed |
| 5 | minor | `vparse.py:559-591` | two false positives (never-invoked macro body, `#[cfg]`-gated decl), safe direction |
| 6 | **major** | `p17/NOTES.md` §10b | the mod-4 sawtooth is the **inner byte fold**, not a 4×-unrolled table walk — disassembly + a generator experiment |
| 7 | **major** | `p17/NOTES.md` §10b | `6.50/request` is band-specific; both of p17's own shipped inputs pay **7.00** |
| 8 | minor | `.memory/01-ladder.md:30`, `:86` | *"eighteen"* and *"the six patterns"* are both **22** now |
| 9 | minor | `TOOLCHAIN.md` (absent) | **valgrind memcheck cannot run on this box** — callgrind can |

**Part B:** build **`p15`**. Named kill risk: R5's verified UTF-8 validator.

---

# PART A — review of TASK_082

## A1 — the new gate stage (`_check_axiom_decls`, `check.py:3511`; matcher `vparse.py:513-591`)

### BLOCKER 1 — `#[verifier::external_trait_specification]` is a body-less trusted declaration the matcher does not count, and it verifies a falsehood at `2 verified, 0 errors`

`harness/vparse.py:513-519` keys on exactly three keywords — `axiom fn`,
`uninterp spec fn`, `assume_specification`. **There is a fourth body-less
trusted form, it is in the pinned vstd 54 times, and no file in `harness/`
mentions it:**

```
$ grep -rn "external_trait_specification\|external_type_specification" harness/*.py
(no output)

$ cd ~/tools/verus/vstd && grep -rn "external_trait_specification" --include=*.rs . | wc -l
54
$ cd ~/tools/verus/vstd && grep -rn "external_type_specification" --include=*.rs . | wc -l
55
```

**The demonstration** — `.temp/r83/a1/p_ets.rs`, 33 lines, re-runnable:

```rust
pub trait Widget { fn width(&self) -> usize; }
pub struct W;
impl Widget for W { fn width(&self) -> usize { 7 } }   // ACTUALLY 7

verus! {
#[verifier::external_type_specification]
pub struct ExW(crate::W);

#[verifier::external_trait_specification]
pub trait ExWidget {
    type ExternalTraitSpecificationFor: Widget;
    fn width(&self) -> (r: usize)
        ensures r == 0,          // A LIE. Nothing checks it.
    ;
}
fn exploit<T: Widget>(w: &T) -> (r: usize) ensures r == 0 { w.width() }
fn main() { let w = W; let r = exploit(&w); assert(r == 0); print_u64(r as u64); }
}
```

```
$ ./verus_run.py --compile .temp/r83/a1/p_ets.rs -o .temp/r83/a1/p_ets
verification results:: 2 verified, 0 errors
$ .temp/r83/a1/p_ets
RUNTIME r = 7
```

Verus proves `r == 0`. The program prints `7`.

**What the gate sees:**

```
$ python3 -c "import sys; sys.path.insert(0,'harness'); import vparse
t=open('.temp/r83/a1/p_ets.rs').read()
print('axiom_decls:', vparse.axiom_decls(t))
print('parse():', [(i.name,i.external,i.line) for i in vparse.parse(t)])"
axiom_decls: []
parse() items: [('width', 'fn', None, 9), ('exploit', 'fn', None, 27), ('main', 'fn', None, 33)]
```

- `vparse.axiom_decls()` → **`[]`** — the new stage prints
  `body-less trusted declarations …: 0 (spec.md declares 0)` and passes.
- `vparse.parse()` sees only the *plain-Rust* `fn width` at `:9` (the honest
  impl) — the trait declaration at `:19` carrying the lie is body-less, so
  `parse()` drops it, exactly as `.memory/05-layout.md` describes.
- No item has `.external` (`vparse.py:475-478` only recognises
  `verifier::external_body` and `verifier::external`, and only **on `fn`
  items** — here the attributes sit on a `struct` and a `trait`), so the
  **TCB inventory at `check.py:3739` is empty**, `_is_trusted` is empty,
  5c-twin shouts *"no trusted item … so no twin is required"*, and
  `_axiom_items` (`check.py:6312`) returns `{}` so **`check_miri` prints the
  no-trusted-base sentence** that `_axiom_items`' own docstring was written to
  stop being printable.
- The obligation count moves by exactly the number of *verified* fns, which the
  author pins anyway.

**This is TASK_081_REVIEW blocker 1, verbatim, one keyword to the left.**

**And it is accident-shaped by the same argument TASK_082 was justified on — I
did not go looking for the declaration, Verus printed it for me.** The first
run of the probe (without `ExW`) failed with:

```
error: cannot use type `p_ets::W` which is ignored because it is either declared
       outside the verus! macro or it is marked as `external`.
   = help: The following declaration may resolve this error:
           #[verifier::external_type_specification]
           pub struct ExW(crate::W);
```

I pasted that line verbatim and the file went green. `.memory/04-verus.md`'s
*"the escape Verus PRINTS FOR YOU is VACUOUS"* is about `assume_specification`;
it is the same tool behaviour on a different keyword.

**Concrete failure scenario, on this tree:** `p36-vtable-dispatch` is the trait
pattern. Its R5 declares `trait Op { fn apply(&self, x: u64) -> (r: u64); }`
*inside* `verus!`, so it is proved. The moment any pattern wants to speak about
a **std** trait — `Index`, `From`, `Iterator`, `Clone` — the only route at the
pinned Verus is `external_trait_specification`, its method declarations are
body-less by construction, and every `ensures` on them is hand-written and
checked by nothing. The pattern ships with `verus.axioms` absent (default 0),
the gate is green, the TCB column reads what it reads today, and the published
`R5 − R4` is a difference between a real program and a proof of a falsehood.

**Fix shape (reporting, not fixing):** `_AXIOM_RE` needs a fourth and fifth
entry, and they cannot be `fn`-keyed — the attribute is on the enclosing
`trait`/`struct`. The honest count is *"one axiom per body-less `fn` inside an
`external_trait_specification` trait, plus one per `external_type_specification`
item"*. `vparse.py`'s selftest already pins the negative direction (a plain
trait method decl is **not** an axiom) — that pin must survive, and the
discriminator is the enclosing item's attribute, which `parse()` already
computes for `fn` items and does not compute for `trait`s.

### BLOCKER 2 — `#[verifier::external_fn_specification]` is accepted at the pin, is not an axiom to `axiom_decls`, and is not a TCB item either

`vparse.py:475-478` classifies attributes with

```python
ext = "verifier::external_body"                       # :475
...
if re.search(r"\bverifier::external\b", a): ext = "verifier::external"   # :477
```

`\bverifier::external\b` does **not** match `verifier::external_fn_specification`
(the next character is `_`, a word character), so `.external` comes back
**`None`**. The TCB inventory at `check.py:3739` is
`[i for i in item_list if i.external]`, so the item is not in it.

`.temp/r83/a1/p_extfn.rs`:

```rust
#[verifier::external_fn_specification]
pub fn ex_count_ones(x: u64) -> (r: u32)
    ensures r == 0,       // A LIE about real Rust semantics.
{ x.count_ones() }

fn exploit(x: u64) -> (r: u32) ensures r == 0 { x.count_ones() }
fn main() { let r = exploit(7); assert(r == 0); print_u32(r); }
```

```
$ ./verus_run.py --compile .temp/r83/a1/p_extfn.rs -o .temp/r83/a1/p_extfn
verification results:: 2 verified, 0 errors
$ .temp/r83/a1/p_extfn
RUNTIME r = 3
```

```
parse(): [('print_u32', 'verifier::external_body', 7, []),
          ('ex_count_ones', None, 11, ['r == 0']),
          ('exploit', None, 18, ['r == 0']),
          ('main', None, 24, [])]
axiom_decls: []
TCB inventory (i.external truthy): ['print_u32']
```

It is *not* body-less, so it is outside A1's literal framing — and that is
precisely why it is dangerous. **In `spec.md`'s `verus.items` pin it is
indistinguishable from an ordinary verified function**: `external: null`,
`ensures: ["r == 0"]`. The one mechanism that would notice it (the item-set
pin, `added=[...]`) reports it as a *new verified item*, which is what an author
adding a genuine lemma also looks like. The published TCB column does not move.

### BLOCKER 3 — an `assume_specification` in a `#[path]`-included module is invisible to the stage that was built for it

`_check_axiom_decls` is called **once**, at `check.py:3759`, inside
`for src, want_n in sorted(pinned_obl.items())` — i.e. only over the files
`spec.md`'s `verus.obligations` names. The one guard against an unpinned Verus
source is `check.py:3615`:

```python
for f in sorted(os.listdir(pdir)):
    if f.endswith(".rs") and vparse.verus_span(open(os.path.join(pdir, f)).read()):
        if f not in pinned_obl: rep.fail("proof-pin", ...)
```

`os.listdir` is **flat**. A `.rs` file one directory down is not enumerated, and
`p01/verus.rs` already ends its header with
`#[path = "../../common/driver.rs"] mod driver;`, so the include mechanism is
live in the tree today.

`.temp/r83/a1/macro/ax_mod.rs` + `.temp/r83/a1/p_hidden.rs`:

```rust
// ax_mod.rs, one directory down
verus! {
pub assume_specification [ u64::count_ones ] (x: u64) -> (r: u32)
    ensures r == 0,        // A LIE.
;
}
// p_hidden.rs
#[path = "macro/ax_mod.rs"] mod ax_mod;
verus! { fn exploit(x: u64) -> (r: u32) ensures r == 0 { x.count_ones() }
         fn main() { let r = exploit(7); assert(r == 0); print_u32(r); } }
```

```
$ ./verus_run.py --compile .temp/r83/a1/p_hidden.rs -o .temp/r83/a1/p_hidden
verification results:: 2 verified, 0 errors
$ .temp/r83/a1/p_hidden
RUNTIME r = 3
$ python3 -c "...; print(vparse.axiom_decls(open('.temp/r83/a1/p_hidden.rs').read()))"
[]
```

The obligation count does not move (an `assume_specification` verifies nothing),
the TCB inventory does not move, and the new stage reports `0 (spec.md declares
0)`.

⚠ **The repair is one line and the machinery already exists**:
`_scan_unsafe_sites` (`check.py:3307`) already scans `_path_includes(pdir, srcs)`
for exactly this reason — *"a helper in the shared `common/driver.rs`, which no
pattern-local parse ever reads"* — and `_check_axiom_decls` does not. The two
stages have the same threat and different file lists.
⚠ **And `common/` is shared by all 22 patterns**, so this is the one vector here
whose blast radius is the whole tree from a single edit.

### MAJOR 4 — the published TCB column still cannot see an axiom. Blocker 1 is half fixed.

`synthesis/synthesize.py:854`:

```python
items = vb.get("tcb_items") or []
lines = sum(i.get("body_lines", 0) for i in items)
```

and

```
$ grep -rn "axiom" synthesis/*.py results/*.md | wc -l
0
```

The gate record now carries `axiom_decls` (`check.py:3775`) and **nothing
reads it**. `results/synthesis.md`'s `TCB items` column and its `**total** 92`
are computed from `tcb_items` alone, so a pattern with five hand-written axioms
publishes `TCB items = <its external_body count>` and a reader of
`results/synthesis.md` sees no axiom at all.

⚠ **This is exactly why TASK_082's acceptance limb *"`results/synthesis.md`
regenerates byte-identical"* passed**: it passed because nothing published
consumes the new key. The Outcome block reads that as *"adding `axiom_decls` to
22 gate records moved no published number, which is the claim the acceptance
test was really making"* — the byte-identity is equally consistent with the
column being blind, and it is.

### CLEAN NEGATIVES (rule 6) — named attacks that did NOT land

| attack | result |
|---|---|
| **spelling variants of the three counted keywords** — `pub(crate)`, keyword split across lines, a `/* comment */` between `uninterp` and `spec`, a generic with `where` on its own line, a declaration nested in a `mod`, `assume_specification` with its `[target]` on the next line | `.temp/r83/a1/p_forms.rs`: Verus `1 verified, 0 errors`; `axiom_decls` counts **7 of 7**, right names, right lines. `blank_noncode` is length-preserving (`vparse.py:64-67`) so a comment between keywords cannot break `\s+`. **Does not land.** |
| **the `broadcast proof fn`-with-a-body boundary** the manager asked about | `.temp/r83/a1/p_bcast.rs`, Verus `2 verified, 0 errors`. `lemma_real` (bodied `proof fn`, `ensures x == x`) → `axiom_decls` `[]`, `_is_trusted` **False**. `ax_with_body` (`#[verifier::external_body] proof fn`, `ensures x == 0`) → `_is_trusted` **True**, in the TCB inventory, twin demanded. **The boundary is drawn exactly where the engineer says.** |
| **is `verus.axioms` defaulting to 0 the right default, and does the message tell an author what to write?** | Driven directly (`_check_axiom_decls` with a stub `rep`): `{}` → 1 `proof-axiom` fail naming ``verus.axioms['verus.rs'] = 7``; `{"axioms":{"verus.rs":7}}` → 0 fails; `{"axioms":{"verus.rs":[names…]}}` → 0 fails. Both the integer and the name-list escapes work, the message names the exact JSON key path, and the `slb-contract` block has **no key whitelist** under `verus` (only `run` at `check.py:629` and `idiom` at `:1242` reject unknown keys), so the key an author is told to write is accepted. The `tcb-axiom` shout still fires after the declaration, which is the stated "visibility, not prohibition" design. **Does not land.** |
| **the `_is_trusted` exclusion reason** (the manager's second-least-sure call) | **The engineer's reason is TRUE, and here is the measurement.** `.temp/r83/a1/p_twin.rs`, the twin 5c-twin would demand — same signature modulo whitespace, checked body: <br>`error: function is marked `uninterp` but it has a body`<br>A twin of an `uninterp spec fn` is a Verus error, and for an `assume_specification` the twin is not even nameable (`TWIN_PREFIX + "u64::count_ones"` = `slb_twin_u64::count_ones`). Feeding axiom decls to `_is_trusted` would make a legal declaration unpassable, exactly as `check.py:3538-3541` says. ⚠ **But the manager's stated *consequence* points at the wrong function**: the published TCB column is `tcb_items` (`i.external`), not `_is_trusted` — see MAJOR 4, which is the real under-count. |
| **does `check_miri` still print *"no trusted item"* over a proof resting on an axiom?** | No. `_axiom_items` (`check.py:6312`) is wired into `check_miri` at `:6436-6454` and `:6472`, and it uses `vparse.axiom_decls` directly rather than `_is_trusted`. The Miri limb of "Owed" 0 is genuinely closed — **for the three keywords**; it inherits blockers 1–3 verbatim. |

### MINOR 5 — two false positives, both in the safe direction

`.temp/r83/a1/p_fp.rs` (Verus: warning only, compiles):

```
{'kind': 'uninterp spec fn', 'name': 'ghost_thing', 'line': 6, 'in_verus': False}
{'kind': 'uninterp spec fn', 'name': 'cfgd_out',    'line': 11, 'in_verus': True}
N = 2
```

- `ghost_thing` lives in a **never-invoked `macro_rules!` body**, outside
  `verus!`. `axiom_decls` records `in_verus: False` and
  `_check_axiom_decls` never filters on it, so the pattern must declare an
  "axiom" that is not an item.
- `cfgd_out` is `#[cfg(slb_twin)]`, a cfg no build ever sets — `parse()` has a
  `cfg_gated` field and the item-set stage uses it (`check.py:3718`);
  `axiom_decls` has no cfg awareness.

Both force a *larger* declared count than the truth, which is the safe
direction, hence minor. But note the asymmetry: a macro that **is** invoked *n*
times is counted **once** (its definition), so the number in `verus.axioms`
would under-state the axioms in the crate.

---

## A2 — p17's `6.50 Ir/request` law (`patterns/p17-http-range/NOTES.md` §10b)

### The re-measurement: the TABLE reproduces exactly, on a different recipe

`.temp/r83/a2/remeasure.py` deliberately does **not** use
`.temp/t82/fit_nsuf.py`'s `n_iters` pair. That used 200/400; this uses
**100/200**, which is §2's own recipe and `check.py` stage 3b's. A true marginal
slope is recipe-independent.

```
nsuf= 1 [committed] R3=   2975.00  R4=   2957.00  R3-R4=  18.00  checksums_agree=True
nsuf= 2 [committed] R3=   5664.30  R4=   5641.30  R3-R4=  23.00  checksums_agree=True
nsuf= 3 [committed] R3=   8154.00  R4=   8124.00  R3-R4=  30.00  checksums_agree=True
nsuf= 4 [committed] R3=  10429.00  R4=  10392.00  R3-R4=  37.00  checksums_agree=True
nsuf= 5 [committed] R3=  12489.00  R4=  12445.00  R3-R4=  44.00  checksums_agree=True
nsuf= 6 [committed] R3=  14326.70  R4=  14277.70  R3-R4=  49.00  checksums_agree=True
nsuf= 7 [committed] R3=  15965.70  R4=  15909.70  R3-R4=  56.00  checksums_agree=True
nsuf= 8 [committed] R3=  17390.00  R4=  17327.00  R3-R4=  63.00  checksums_agree=True
nsuf= 9 [OOS      ] R3=  18599.00  R4=  18529.00  R3-R4=  70.00  checksums_agree=True
nsuf=10 [OOS      ] R3=  19586.00  R4=  19511.00  R3-R4=  75.00  checksums_agree=True
nsuf=11 [OOS      ] R3=  20373.70  R4=  20291.70  R3-R4=  82.00  checksums_agree=True
nsuf=12 [OOS      ] R3=  20946.70  R4=  20857.70  R3-R4=  89.00  checksums_agree=True
```

**`18 23 30 37 44 49 56 63` — §10b's row, exact, on a different recipe.**
✅ **Two points independently re-measured and then all eight; they agree.**

### Out-of-sample: the LAW holds — and `gen.py` was not edited

The task said a generator change means "say so and skip it". It does not need
one: `SWEEP_NSUFS` can be **rebound at import time**, which touches no file.
`.temp/r83/a2/gen_oos.py` imports `gen.py` as a module, points `HERE` at
`.temp/r83/a2/oos/` and widens `SWEEP_NSUFS` to `range(1, 13)`.

```
-- self-check: committed 01..08 vs regenerated --
  sweep-nsuf-01.bin  4e892641927d3f1a  4e892641927d3f1a  SAME
  ... (8 of 8) ...
  sweep-nsuf-08.bin  f325badc7c19387e  f325badc7c19387e  SAME
  sweep-nsuf-09.bin  dc4377a357d91191  (OUT OF SAMPLE)
  sweep-nsuf-10.bin  6faa0c4be2f0c077  (OUT OF SAMPLE)
  sweep-nsuf-11.bin  d2764b74c8e717ab  (OUT OF SAMPLE)
  sweep-nsuf-12.bin  2da6ee820b5d8427  (OUT OF SAMPLE)
differing: 0
```

8 of 8 byte-identical, so the four new points are on the same band.
`git status --porcelain patterns/p17-http-range/inputs/gen.py` is empty.

Lag-4 differences over the extended band, `d(n+4) − d(n)`:

```
n=1..4 (in sample):  44-18=26  49-23=26  56-30=26  63-37=26
n=5..8 (OUT OF SAMPLE): 70-44=26  75-49=26  82-56=26  89-63=26
```

**8 for 8, zero residual. `6.50 Ir/request at lag 4` predicts the out-of-sample
points exactly.** The arithmetic claim survives.

### MAJOR 6 — the MECHANISM is wrong. §10b names the wrong loop, and the disassembly says so.

§10b: *"a 4×-unrolled walk over the **suffix table** with a scalar epilogue, so
the cost is flat across a group of four and steps at the group boundary."*

**Neither rung's suffix-table walk is unrolled at all.** `.temp/r83/a2/r3.asm`,
R3 `safe_tuned::kernel`, the outer per-request loop — **one request per
iteration**:

```
15760: inc    rax
15763: inc    r15
15766: cmp    r15,r11
15769: je     158a3
1576f: movzx  r13d,BYTE PTR [r8+r15*2]        <- suffix lo
15774: movzx  ebp,BYTE PTR [r8+r15*2+0x1]     <- suffix hi
```

The 4× unroll is the **inner byte fold**, and it is keyed on the **served
length**:

```
157b4: mov    r10d,r13d
157b7: and    r10d,0x3            <- n & 3, the remainder
157bb: cmp    ecx,0x3
157be: jae    157d0
15800: movzx  esi,BYTE PTR [rdx+rcx*1-0x3]    \
   ...                                        |  four fold steps
15836: movzx  esi,BYTE PTR [rdx+rcx*1]        /
15847: add    rcx,0x4
1584b: cmp    r14,rcx
1584e: jne    15800
15850: test   r10,r10             <- scalar epilogue guard
15880: movzx  r9d,BYTE PTR [rcx+rdx*1]        <- scalar epilogue
```

R4 `unsafe::kernel` has the same shape (`and r15d,0x3` at `156d6`, four `movzx`
at `1571a/1572d/15740/15753`, `add rbp,0x4` at `1575b`, scalar tail at `15790`),
and its table walk is scalar too (`inc rbx` at `15693`).

**And the generator, not the kernel, is what sets the period — measured, not
argued.** `.temp/r83/a2/mech.py` re-emits the band with only
`sweep_suffixes`'s step changed (`497 − (i·step) % 490`); the request count is
still 1…8 in every row, so a 4×-unrolled *request* loop would keep its staircase:

```
step=36 (==0 mod 4)  R3-R4 = 18 25 32 39 46 53 60 67
            steps = +7 +7 +7 +7 +7 +7 +7   served_len mod 4 = [1,1,1,1,1,1,1,1]
step=37 (==1 mod 4)  R3-R4 = 18 23 30 37 44 49 56 63
            steps = +5 +7 +7 +7 +5 +7 +7   served_len mod 4 = [1,0,3,2,1,0,3,2]
step=38 (==2 mod 4)  R3-R4 = 18 25 32 39 46 53 60 67
            steps = +7 +7 +7 +7 +7 +7 +7   served_len mod 4 = [1,3,1,3,1,3,1,3]
step=39 (==3 mod 4)  R3-R4 = 18 25 32 37 44 51 58 63
            steps = +7 +7 +5 +7 +7 +7 +5   served_len mod 4 = [1,2,3,0,1,2,3,0]
```

⚠ **At step 36 and step 38 the sawtooth is GONE and the law is `7·nsuf + 11`
with zero residual — 7.00 per request, not 6.50.** The `+5` step lands exactly
and only where the *newly added* request's served length is `≡ 0 (mod 4)`. The
shipped band shows period 4 because `37 ≡ 1 (mod 4)`, so the residue advances by
one per request — **a property of `inputs/gen.py`'s suffix spread, not of any
loop.**

⚠ **`inputs/gen.py` says so itself, and it is measurement-hashed.** Its
`SWEEP_NSUFS` comment argues for 8 consecutive points on the ground that
*"`nsuf` is a REQUEST COUNT, the outer loop's trip count, not a byte length —
**no unrolled epilogue is keyed on it, so it has no residue class to hide a
sawtooth in**"*, and `_check_residues`' docstring calls the suffix values *"the
inner fold's trip counts, one per served range"*. **The generator is right and
§10b contradicts it.** So does §2 of the same NOTES file, which already
published *"**+16 (served length ≡ 0 mod 4) or +18** on the sweep's one-range
windows"* — the same 2-instruction step, correctly attributed, twelve hundred
lines earlier.

### The replacement law, and its falsification test

```
R3ship − R4  =  11 + 7·nsuf − 2 · #{ i < nsuf : s_i ≡ 0 (mod 4) }
```

Zero free parameters. `.temp/r83/a2/predict.py` predicts each row **before**
running it, all at `nsuf = 3` (the shipped shape) with only the residues moved:

```
small.bin residues (2,3,2)   sufs=(498, 251, 122) mod4=(2, 3, 2) predicted= 32  measured= 32.00  OK
all three == 0 mod 4         sufs=(496, 248, 120) mod4=(0, 0, 0) predicted= 26  measured= 26.00  OK
all three == 1 mod 4         sufs=(497, 249, 121) mod4=(1, 1, 1) predicted= 32  measured= 32.00  OK
two of three == 0 mod 4      sufs=(496, 248, 121) mod4=(0, 0, 1) predicted= 28  measured= 28.00  OK
one of three == 0 mod 4      sufs=(496, 249, 121) mod4=(0, 1, 1) predicted= 30  measured= 30.00  OK
```

5 of 5 exact. Together with the 12 sweep points and the 32 points of the
four step-bands, the law predicts **all 49 measured points with zero residual**,
and it also predicts the two *published* ones:

| input | suffixes | mod 4 | `#{≡0}` | law | published |
|---|---|---|---|---:|---:|
| `small.bin` | 498, 251, 122 | 2, 3, 2 | 0 | `11 + 21 − 0` = **32** | **+32.0** (§2) |
| `large.bin` | 4085, 2041, 1019 | 1, 1, 3 | 0 | `11 + 21 − 0` = **32** | **+32.0** (§2) |

### The `30 ≠ 32` disclosure: explained, and no published number is off by 2

§10b says the gap is because *"the inputs are not the shipped ones"*. That is
true but not a mechanism, and the shapes are in fact **identical** —
`SWEEP_BODY == SMALL_BODY == 498`, `SWEEP_WINS == SMALL_WINS == 32`, and at
`nsuf = 3` the stride is 506, which *is* `small.bin`'s. The only thing that
differs is the suffix values, and the table above is the whole of it:
`sweep-nsuf-03` has suffixes `497, 460, 423` → residues `1, 0, 3` → **one**
`≡ 0 (mod 4)` → `32 − 2 = 30`. ✅ **The difference is fully explained, and
`+32` is correct for both shipped inputs.**

### MAJOR 7 — `6.50/request` is band-specific, and quoting it makes p17's own shipped inputs *less* accurate

`6.50` is `7 − 2/4`: the mean over a band that happens to sample each residue
class once per four requests. **Both of p17's shipped inputs have NO served
length `≡ 0 (mod 4)`** (table above), so they pay **7.00 per request**.

§10b's advice — *"A reader applying `7·nsuf` to 20 ranges gets ≈ +149 where the
lag-4 law gives ≈ +140; quote 6.5 per request at lag 4, not `7·nsuf + 9`"* — is
therefore backwards for p17's own inputs. For a 20-range request with
`small.bin`'s residue profile the law gives `11 + 140 = 151`; `7·nsuf + 9`
gives 149 and is nearly right; `6.50/request` gives ≈ 140 and is **11 low**.
The correction moves the reader away from the answer.

**What is safe to publish:** `+7 per request, less 2 for every served range
whose length is a multiple of 4`, with the disassembly above as the mechanism.
It is a *level* law with zero residual on 49 points and it subsumes both the
`+32` headline and the `18…63` band. ⚠ **§10b is PROVISIONAL and rule 9 keeps it
out of `.memory/` until this review lands — it should not go in as written.**

### A2 clean negatives

- **"the table is a fit that will not reproduce"** — it reproduces byte-for-byte
  on an independent `n_iters` pair. **Does not land.**
- **"lag-4 is numerology and will break out of sample"** — it does not; 26 four
  more times at `nsuf` 9…12. **Does not land.** The arithmetic is sound; only
  the *mechanism* and the *scope* are wrong.
- **"a sweep run forces a re-measure"** — `harness/measure.py --check-stale`
  needs no re-run to settle this: the OOS blobs were written to
  `.temp/r83/a2/oos/`, never to `patterns/`, and
  `git status --porcelain patterns/p17-http-range/` is empty. **Does not land.**
- **all three rungs print one checksum per blob on all 12 points**
  (`checksums_agree=True`, column above), so no rung entered an adversarial band
  and the differences are between rungs doing the same work.

---

## A3 — the two things TASK_082 reported but did not do

### Confirmed: it is only p01, and the sentence is genuinely retracted

```
$ grep -rn "not a gate condition" --include=*.md --include=*.py . | grep -v '^./.temp'
RECAP.md:2286
.tasks/TASK_082.md:268
.tasks/TASK_083.md:80
.tasks/TASK_027_REVIEW_REPORT.md:37
patterns/p01-array-sum/spec.md:82        <-- the only pattern file
harness/check.py:72                      <-- the correction, not the claim
```

`patterns/p01-array-sum/spec.md:82` is the only `patterns/*/spec.md` carrying it.
`grep -rn "recorded as a \*\*result\*\*\|recorded as a result" patterns/*/spec.md`
returns that one line and nothing else.

And it *is* retracted — `harness/check.py:2943`:

```
head("3c. structural identity R4-vs-R5 (recorded as a result AND enforced)")
```

with `check.py:2924-2927`: *"This header said 'a RESULT, not a gate condition'
until TASK_028. That was … makes the run's verdict FAIL."* and `check.py:67-72`:
*"A level at or above the one `spec.md` pins is a result; a drop below it calls
`rep.fail` and the run's verdict is FAIL."* **p01's `spec.md` states the
opposite of what `check.py` does.** Reported, not fixed — editing it stales
p01's gate record.

### MINOR 8 — the substring-grep sweep found one more, and it is inside `.memory/`

The trick to look for is *a correction that appended rather than replaced*, so a
naive `grep` for the claim keeps hitting. One pass over `RECAP.md` and
`.memory/` for the tell-tale phrasings (`still reads|still says|still
carries|still shows|still contains|still spells|still prints`) turns up seven
hits, five of which are correctly-marked history. Two are live:

**(a) `.memory/01-ladder.md:84-92` — the correction is itself stale by 4.**

> *"every pattern carries a byte-identical statement of it — ⚠ this sentence
> said **"all six"**, **there are eighteen** … ⚠ The paragraph's own text still
> says "all six patterns" — that is historical and is deliberately NOT
> corrected, because … one adjective would move eighteen `contract_sha256`
> values."*

Measured now:

```
$ grep -rl "byte-identical in all six patterns" patterns/*/spec.md | wc -l
22
$ grep -rl '"why"' patterns/*/spec.md | wc -l
22
$ ls -d patterns/p*/ | wc -l
22
```

**22, not eighteen** — and the file gives eighteen twice, once as a count of
patterns and once as a count of `contract_sha256` values it would move. The
*decision* (leave the hashed text alone) is right; the *number attached to it*
is four short, and it sits in the layer `CLAUDE.md` calls authoritative.

**(b) `.memory/01-ladder.md:30`** — *"**Every one of the six patterns** pins
`identity: unsafe ≡ verus, O3 exact` (checked, all six `results/gate/*.json`)"*.
Parsed out of the `slb-contract` blocks: **22 of 22** carry a contract block and
**22 of 22** pin `unsafe`≡`verus` `exact`. The invariant still holds; the
verification claim is over a set that has since quadrupled, and unlike (a) this
one is **not** marked historical.

Not fixed (reviewers do not fix, and `.memory/` is the manager's surface).

---

# PART B — the next pattern

## Recommendation, ranked

| rank | row | verdict |
|---|---|---|
| **1** | **`p15` — UTF-8 validation + decode** | **BUILD IT.** All three probes pass, and the manager's question (i) is answered *the opposite way* from what the task expected. |
| 2 | `p23` — quicksort partition | **Strong fallback.** Its R5 novelty probe landed cleanly; the risk is the partition loop, not the vocabulary. |
| 3 | `p25` — `realloc` growth | **Defer.** The stale-pointer harm is p27's, measured at the detector. |
| 4 | `p42` — `goto cleanup` leak | **Refuse.** `Ir` sees the leak with the *wrong sign*. |

⚠ **Probe-2 caveat, stated up front as the task requires:** p15's probe 2 is a
**PRE-check on throwaway kernels in one object file**, the way `p45` was killed.
It is not a measurement of built rungs, because built rungs do not exist.

---

## `p15` — the probes

### Probe 1 — the rung boundary, NAMED

**R3 `core::str::from_utf8` (validates, returns `Result`) against R4
`str::from_utf8_unchecked` (assumes, `unsafe fn`).** The boundary is at
R3-vs-R4 and the unsafe function's safety precondition *is* the validation — the
cleanest instance of the project's own question the tree has.

### ⚠ Question (i) — the manager's *first* worry is REVERSED: `from_utf8_unchecked` IS supported at the pin

And **I nearly reported the opposite**, so this is worth the paragraph.

```
$ ./verus_run.py .temp/r83/b/p15_r4.rs          # core::str::from_utf8_unchecked
error: `core::str::converts::from_utf8_unchecked` is not supported
  = help: The following declaration may resolve this error:
          pub assume_specification [std::str::from_utf8_unchecked] (_0: &[u8]) -> &str;
```

That is the **wrong path**. The pinned vstd specs the **inherent** associated
function, `vstd/string.rs:136`:

```rust
pub assume_specification[ str::from_utf8_unchecked ](v: &[u8]) -> (res: &str)
    requires valid_utf8(v@),
    ensures  res.spec_bytes() =~= v@,
;
```

```
$ ./verus_run.py .temp/r83/b/p15_r4b.rs         # str::from_utf8_unchecked
verification results:: 2 verified, 0 errors
```

`.temp/r83/b/p15_r4b.rs` is `fn kernel(b: &[u8]) requires valid_utf8(b@) { unsafe
{ str::from_utf8_unchecked(b) }.unicode_len() }`. **Supported, with the
precondition already being exactly the validation.** ⚠ This is the fifth
instance of `CLAUDE.md`'s *"grep the pinned vstd before claiming no spec
exists"*, and the free-vs-inherent path distinction is what makes it a trap —
Verus's `is not supported` message is *correct about the function you named* and
still the wrong answer to the question you asked.

⚠ **One asymmetry the task did not anticipate: the SAFE side has no spec.**
`core::str::from_utf8` is `is not supported` and `grep -rn "from_utf8"
~/tools/verus/vstd` returns **one** line, the unchecked one. That is harmless —
only R5 goes through Verus and R5 is R4's code — but it means p15 can never
ship a *verified* R3, which p01 does (`safe_naive_verus.rs`).

### Question (ii) — Verus can state "valid UTF-8", and vstd already does

`vstd/utf8.rs` is a whole module: `valid_utf8` (`:272`, a recursive
`open spec fn` over `Seq<u8>` with `decreases bytes.len()`), `decode_utf8`,
`valid_first_scalar`, `pop_first_scalar`, `length_of_last_scalar`,
`is_continuation_byte`. **R5 is not a stall for lack of vocabulary.**

### Probe 2 — the rungs differ AS MACHINE CODE (pre-check)

`.temp/r83/b/probe2_p15.rs`, two `#[no_mangle] #[inline(never)]` kernels with the
identical fold, one object file, `rustc -O -C codegen-units=1`:

```
k_checked      Ndx=  3 sec=.text.k_checked     size=  206 md5=47d94b6d54c110973c0e9a5cdea70129
k_unchecked    Ndx=  5 sec=.text.k_unchecked   size=  146 md5=e6ae62c14c87ba02fd24e180f142f891
```

**No collision.** p15 is not `p45`.

### Probe 3 — the `0.00` rule: there is no zero, and here is the axis anyway

Marginal `Ir` per call, `.temp/r83/b/cost_p15.rs`, 4096-byte buffer built at run
time from `argv`, `n_iters` 100 vs 200, callgrind:

```
ascii checked   marginal_Ir_per_call = 46922
ascii unchecked marginal_Ir_per_call = 45071      ->  +1851  (+4.1%)
wide  checked   marginal_Ir_per_call = 86077
wide  unchecked marginal_Ir_per_call = 43023      -> +43054 (+100.1%)
```

⚠ **The axis is the input alphabet, and the tree has nothing like it.**
Validation is ~free on ASCII (`from_utf8`'s word-at-a-time ASCII fast path) and
**doubles the kernel** on 2–3-byte scalars. Declared in advance, as probe 3
requires: *the convention is marginal `Ir` per kernel call at `-O3 isolated`
(p17 §2's recipe), and the published quantity is a **slope in the fraction of
non-ASCII bytes**, not a level.*

### ⚠ Question (iii) — the manager's named least-sure call, DECIDED

**The manager was right to worry: the C rung's harm IS the thirteenth
`index >= len`.** `.temp/r83/b/c_harm.c` — the idiomatic C decoder that trusts
the lead byte's declared length — on a buffer whose last byte is `0xF0`:

```
$ .temp/r83/b/c_harm trunc
c_harm.c:18:30: runtime error: load of address 0x502000000018 with insufficient space ...
==138631==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x502000000018
READ of size 1 at 0x502000000018 thread T0
```

**But the row is not p31, and the reason is measured, not argued.** `p31` was
refused for *"no boundary anywhere"* — the arena's carve is correct C, so **no
rung differed**. p15 has a boundary at R3-vs-R4 with a 4%–100% cost and
non-colliding machine code (probes 1–3 above). The bug-class question is the
one `.memory/06-catalogue.md` explicitly demotes: *"Novelty of the bug class
predicts neither way. The ladder test does."*

**And the R4-side harm really is a new class, in two measured rows that no
pattern in the tree has:**

| adversarial input | release binary (`rustc -O`) | Miri | ASan-equivalent | bounds violation? |
|---|---|---|---|---|
| `61 C3 28 62` — invalid continuation | `len=4 fold=100507`, **exit 0** | **clean** | n/a | **none** |
| `61 F0` — truncated lead | **prints NOTHING, exit 0** | **UB: `entering unreachable code`**, `core/src/str/validations.rs:48` | n/a | **none** |

```
$ cargo +nightly miri run     # truncated-lead
error: Undefined Behavior: entering unreachable code
  --> .../core/src/str/validations.rs:48:23
   |
48 |     let y = unsafe { *bytes.next().unwrap_unchecked() };
   |                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Undefined Behavior occurred here
```

⚠ **Row 2 is the strongest adversarial cell in the tree: the optimiser deleted
the program's own `println!`.** The `-O` binary produces no output and exits 0,
because `unreachable_unchecked` inside `next_code_point` let LLVM treat the
whole continuation as dead. That is *"the optimiser deleted the programmer's
code"* — the harm class the manager proposed for `p45` and which was **refuted
as stated** there (`.memory/06-catalogue.md`: *"gcc never deletes any of them"*).
Here it is real, measured, and in the shipped-language rung.

⚠ **Row 1 is the honest weakness and must be disclosed in `spec.md`, not
discovered later:** an invalid *continuation* is a silent wrong answer that
**Miri does not catch** — that is `p18`'s harm, and `p18`'s harm is what killed
`p45`. p15 is worth building because of row 2 and the cost axis, **not** because
every invalid byte string is detectable.

### ⚠ The named KILL RISK for `p15` — the call site, and it is the one that bites

`.memory/02-bench-rules.md` rule 2: R5's `main` must be a **real verified call
site**, not `external_body`. So R5 must **discharge `valid_utf8(b@)`** over bytes
read from a file at run time. That needs a *verified UTF-8 validator* whose
postcondition is `vstd::utf8::valid_utf8` — proved against a recursive spec with
`pop_first_scalar` in its `decreases`, inside a loop. **I did not build it and I
do not know it closes.**

⚠ **And the escape hatch is precisely the defect this same review opened.** If
the validator stalls, the only route to green is an `assume_specification` or an
`external_body` validator — a hand-written axiom saying *"these bytes are valid
UTF-8"*, which is **the strongest possible false axiom for this pattern** and,
per BLOCKERS 1–3 above, one the published TCB column cannot see. **Budget one
engineer session for the validator; if it stalls, REFUSE the row rather than
axiomatise it**, and say so in the task file up front.

Second, smaller risk: `.memory/02-bench-rules.md`'s proof-domain rule. The gate
evaluates `requires` at **every call the benchmark makes, `adversarial-*`
included** — and p15's adversarial inputs are invalid UTF-8 *by construction*,
so `valid_utf8(b@)` is **false on them**. The kernel contract must therefore be
`kernel(bytes) -> u64` with the validation *inside* the measured kernel (R3
validates and returns 0; R4 assumes and is UB), not a `requires valid_utf8` on
the kernel — otherwise the adversarial rows are outside the verified domain and
p15 repeats the pilot's defect. **This is a `spec.md` design decision and it
must be made before the first cell is built.**

---

## `p23` — quicksort partition (rank 2)

**Probe 1 (boundary):** exists — safe Rust needs `split_at_mut`/indices and pays
bounds checks; unsafe uses raw pointer swaps. Not measured here.

**The novelty probe, which is the one that matters, LANDED.** The task calls the
permutation invariant *"the tree's first proof obligation that is not a bound"*.
It is statable **and provable** at the pin, with no `assume`:

```rust
fn swap_two(v: &mut Vec<u64>, i: usize, j: usize)
    requires i < old(v).len(), j < old(v).len(),
    ensures  final(v)@.len() == old(v)@.len(),
             final(v)@.to_multiset() =~= old(v)@.to_multiset(),
{ let a = v[i]; let b = v[j]; v.set(i, b); v.set(j, a);
  assert(v@ =~= old(v)@.update(i as int, b).update(j as int, a));
  broadcast use group_to_multiset_ensures; }
```

```
$ ./verus_run.py .temp/r83/b/p23_perm.rs
verification results:: 2 verified, 0 errors
```

**Kill risk:** this is a *two-element swap*, not a partition loop. The loop
invariant — the multiset is preserved while two moving indices partition the
range — is the `hard` the catalogue rates it. Recommend p23 **only** as the
fallback if p15's validator stalls, and with the same one-session budget.

⚠ Note `final(v)`/`old(v)` — the pinned Verus rejects a bare `v@` in a
postcondition (*"to dereference a mutable reference parameter in a
postcondition, disambiguate by wrapping it in either `old` or `final`"*). Worth
putting in `.memory/04-verus.md`; it cost me two runs and it will cost the next
agent the same.

---

## `p25` — `realloc` growth (rank 3, defer)

**The manager's own question answered with a measurement: yes, it is p27's UAF
in a costume — at the detector.** `.temp/r83/b/c_p42_p25.c`, `stale()` saves a
pointer, grows through `realloc`, then reads the saved pointer:

```
==139448==ERROR: AddressSanitizer: heap-use-after-free on address 0x502000000010
READ of size 1 at 0x502000000010 thread T0
```

`patterns/p27-handle-table/NOTES.md:999` already publishes
`ERROR: AddressSanitizer: heap-use-after-free on address 0x502000000010` — the
same class, and p27's own `NOTES.md:951` and `:983` record that *"a use-after-free
has no magnitude axis"* and *"a naked use-after-free is not a reproducible
number"*. p25 inherits both.

✅ **Clean negative on the manager's second worry:** TASK_079's *"both compilers
DELETE a non-escaping `malloc`/`free` pair at `-O2`"* does **not** bite this
shape. At `/usr/bin/gcc -O2`, `leaky` and `stale` are inlined into `main` and the
allocator calls survive:

```
$ objdump -d .temp/r83/b/c42 | awk '/<main>:/,/^$/' | grep -o "call.*<[a-z]*@plt>" | sort | uniq -c
      1 call   10a0 <free@plt>
      1 call   10b0 <strcmp@plt>
      1 call   10c0 <malloc@plt>
      1 call   10d0 <realloc@plt>
```

So `-fno-builtin-*` is **not** needed for a kernel of this shape. The reason to
defer p25 is the duplicate harm, not the allocator.

---

## `p42` — `goto cleanup` leak (rank 4, REFUSE)

**The manager asked *"is a LEAK a harm this ladder can price at all?"* — the
answer is no, and the sign is the proof.** Same C file, the same kernel with and
without the missing `free`, whole-program callgrind:

```
leak Ir=211255
ok   Ir=211489
```

**The leaking path is 234 `Ir` CHEAPER.** The bug is a *missing* call, so the
"cost of safety" p42 would publish is the cost of calling `free` — which is
`p27`'s drop-glue number (120.42 `Ir`) measured on a different allocator path.
The ladder's cost axis runs the wrong way and the pattern's headline would be
*"the buggy rung is faster"*, which is true of every leak and says nothing about
memory safety.

And the detector matrix has exactly one new cell:

```
$ .temp/r83/b/c42a leak      # gcc -O2 -fsanitize=address
==139450==ERROR: LeakSanitizer: detected memory leaks
Direct leak of 4096 byte(s) in 1 object(s) allocated from:
SUMMARY: AddressSanitizer: 4096 byte(s) leaked in 1 allocation(s).
```

LeakSanitizer fires; nothing else does, because **nothing is read or written out
of bounds** — there is no memory-safety violation to find. **Refuse p42.**

---

## Did I consider "none of these, build X instead"?

Yes, and the answer is **no** — but only because `p15`'s probes came back
stronger than the manager expected, not because the shortlist was a menu. p15
has (a) a supported R4 at the pin, (b) a vstd vocabulary for the R5 property,
(c) non-colliding machine code, (d) a 4%→100% cost axis on a variable no pattern
in the tree varies, and (e) an adversarial row in which the optimiser deletes the
program's output. **I did not survey all 24 unbuilt rows** — I probed the four
named plus nothing else, so "p15 beats the other 20" is not established, only
"p15 beats the other three and clears all three probes".

---

# MINOR 9 — valgrind memcheck cannot run on this box, and nothing records it

Found while probing `p42`, whose stated catcher is *"Miri's leak check or
valgrind"*:

```
$ ~/tools/valgrind/bin/valgrind .temp/r83/b/c42 ok
valgrind:  was not found whilst processing
valgrind:  symbols from the object with soname: ld-linux-x86-64.so.2
valgrind:  ... The package you need to install for fix (1) is called
valgrind:    On Debian, Ubuntu:                 libc6-dbg
valgrind:  Cannot continue -- exiting now.  Sorry.

$ ~/tools/valgrind/bin/valgrind --tool=callgrind --callgrind-out-file=/dev/null .temp/r83/b/c42 ok
==140334== I   refs:      211,429

$ ls /usr/lib/debug/.build-id
ls: cannot access '/usr/lib/debug/.build-id': No such file or directory
```

**callgrind works; memcheck and `--leak-check` do not.** `TOOLCHAIN.md` lists
valgrind 3.27.1 as available with no qualification, and
`.memory/00-environment.md` does not mention memcheck at all. Any future task
that plans a memcheck row (p42 was one) is planning on a tool this box does not
have — the same failure shape `TOOLCHAIN.md`'s *"what's missing on this box"*
section exists for. **Reported, not fixed.**

---

# Deliverable check (PROTOCOL rule 10)

```
$ grep -rho '\.tasks/TASK_[A-Za-z0-9_]*\.md' .memory/ .tasks/ RECAP.md \
    | sort -u | while read p; do [ -e "$p" ] || echo "MISSING: $p"; done
```

Result is pasted in the return message; this file was written **before**
anything cited it.

# What I did NOT do, and what I am unsure of

- **I did not fix anything.** `git status --porcelain` shows one untracked
  file, this report. `patterns/`, `.memory/`, `harness/`, `common/`,
  `results/`, `synthesis/`, `pilot/` are byte-clean, `gen.py` included
  (`git status --porcelain patterns/p17-http-range/` is empty).
- **BLOCKER 3 is a code read plus an equivalent standalone demonstration, not a
  demonstration inside a real pattern.** Showing it end-to-end through
  `check.py` needs writing a `.rs` file into a pattern directory, which is
  forbidden here. The two line numbers (`check.py:3615` `os.listdir`,
  `:3759` inside the `pinned_obl` loop) are the whole argument and they are
  short; the Verus half is demonstrated in `.temp/r83/a1/`.
- **I did not re-run `harness/check.py` on any pattern.** Nothing I did could
  change a gate record, and the task's established context (22 verdicts, 0
  failures, TCB 92→92, 0 STALE) is manager-verified.
- **`p15`'s R5 validator is unbuilt and is the whole risk.** I established that
  the *vocabulary* exists and the *unchecked call* verifies; I did **not**
  establish that `valid_utf8(b@)` is dischargeable from a verified exec
  validator at the pin. That is the one thing a p15 task must budget for.
- **Probe 1 for `p23` and `p25` was not measured** — only p15's was. For p23 I
  probed the R5 novelty (which is what the row is for) and for p25 the harm and
  the allocator survival, not the rung cost.
- **I did not survey the other 20 unbuilt catalogue rows.**
- **The four `p17` step-bands and the five prediction rows are all on
  GENERATED inputs under `.temp/r83/a2/`**, never in `patterns/`. The two
  *published* p17 points (`small`, `large`) were not re-measured — they are
  predicted by the replacement law and match, which is weaker than a re-run.
