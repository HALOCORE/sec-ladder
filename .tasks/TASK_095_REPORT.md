# TASK_095 — `p29` §0: REFUSED, with measurements

**Role: research engineer.** **UNREVIEWED.** ⚠ **Written by the MANAGER from the
agent's return message** — the engineer did not write this file, and flagged that
itself under rule 10. Every number below is the engineer's; the four marked
✅ **manager-verified** were re-run independently before anything reached
`.memory/`.

**PROTOCOL rule 2 running count: 270 → 274.**

**No pattern was built** — no `patterns/p29-*/`, no `spec.md`, no
`slb-contract` block, no `model.py`, no `inputs/gen.py`, no rung sources, no
`check.py`, no `measure.py`. §0's authority to refuse was exercised.

Evidence in `.temp/t95/` (248 K, sources + logs, zero binaries);
`bash .temp/t95/build.sh` rebuilds and re-runs every claim in **37.5 s**.

---

## VERDICT

**REFUSE `p29`.** The §0 question — *"is same bug class, different rejection
mechanism enough to carry a pattern?"* — **does not have to be answered in
general, because `p29`'s rejection mechanism is NOT different.**

`TASK_094`'s limb **(a)** (the safe representation really frees) **survives**.
Limb **(b)** (the mechanism is `E0502` at compile time, not `p27`'s runtime ask)
is **refuted three independent ways.**

---

## E1 — `E0502` IS GENERIC BORROWCK. It is not a fact about the BST.

✅ **MANAGER-VERIFIED** — `c0_scalar`, `c2_p27_ref` and `c4_bst` re-compiled
independently; all three exit 1 with **one `error[E0502]`** and the **identical**
message.

`rustc 1.97.1 -O --crate-type=lib --edition 2021`, all `#![forbid(unsafe_code)]`:

```
c0_scalar    exit=1  1 error[E0502]   <- struct S { v: u32 }. NO DATA STRUCTURE.
c1_vec       exit=1  1 error[E0502]
c2_p27_ref   exit=1  1 error[E0502]   <- p27's OWN Vec<Option<Box<Rec>>>
c3_hashmap   exit=1  1 error[E0502]
c4_bst       exit=1  1 error[E0502]   <- TASK_094's p29_borrow.rs, byte-identical

all five: "cannot borrow `*X` as mutable because it is also borrowed as immutable"
```

⚠⚠ **This is `TASK_093`'s `E0382` failure mode ONE ROW LATER.** `TASK_093_REVIEW`
killed that claim with a control containing no data structure; `c0_scalar.rs` is
that control here. **`c2` is the load-bearing one: `p27`'s own structure,
transcribed through a reference-returning `get`, prints `p29`'s "novel"
diagnostic.**

## E2 — a BST is not FORCED into the compile-time mechanism

`.temp/t95/e2/k0_bst_key.rs`, same `Option<Box<Node>>` BST, **key-addressed**,
`#![forbid(unsafe_code)]`:

```
k0_bst_key COMPILES AND RUNS: before=Some(100) removed=true after=None
```

**That is `p27`'s published sentence verbatim, on a BST**: `*cur = None` frees
and invalidates in one operation, and the second `find` — the ASKING — gets
`None` **at run time**. Same type as `p27`'s table slot.

## E2b — key-addressed, THE C RUNG HAS NO BUG AT ALL

`gcc -O1 -g -fsanitize=address`, `env -u LD_PRELOAD`, counted with
`grep -c AddressSanitizer` (never `head`), positive controls firing:

```
key  before=100 after=NULL              asan_exit=0  AddressSanitizer_lines=0  <- NO BUG
ptr  before=100 after=5                 asan_exit=1  AddressSanitizer_lines=2  heap-use-after-free
p27  payload=51784690615687241 02       asan_exit=1  AddressSanitizer_lines=2  heap-use-after-free
```

⚠⚠ **`p29`'s UAF REQUIRES the saved raw pointer. `p27`'s does not** — C's
`tab[h]` retains the dangling pointer after `free`, so **`p27`'s bug survives
integer naming**; a BST's parent link is nulled by `remove`, so a re-walk cannot
reach the freed node.

## E3 — in the SHIPPED kernel shape the `E0502` cannot arise

**22 of 24 patterns declare `kernel(buf: &[u8], off: usize, len: usize) -> u64`;
all 24 take their payload from a file blob.** `p27`'s own shipped `why` already
states the consequence: *"THE HANDLE IS AN INTEGER AND THAT IS WHY NULLING IS NOT
A DEFENCE: the op stream comes out of a file and a file cannot name a pointer."*

So a `p29` kernel names nodes by key — and by **E2b there is then no bug.** The
only saved pointer available is an internal memo cache:

```
s0 (cache: Option<&Node>)           : error[E0106] missing lifetime specifier
s1 (Bst<'a>, as a LIBRARY)          : exit=0 (compiles)
s2 (a real CALL SITE)               : 2 error[E0499]   <- the struct is write-once
s3 value-cache, forbid(unsafe_code) : before=Some(100) removed=true
                                      after=Some(100)  CORRECT=false
miri s3 (safe value cache)          : exit=0 UB=0      <- SILENT
miri s4 (POSITIVE CONTROL)          : exit=1 UB=3      <- "dangling reference (use-after-free)"
```

⚠⚠ **A shipped `p29` with a memo cache lands in `.memory/01-ladder.md`'s
OUTCOME 3 — *"the type system is SILENT"* — which is `p04`'s finding and is
already the stated reason `p32`/`p33` are refused.**

## E5 — the `remove`-inclusive cost pair. ⚠ CONTRADICTS the task file's §2.

`TASK_094`'s conventions exactly. Checksums agree across sides; allocation
counted and real (`allocs=12301 frees=4098 freed_bytes=98432`, identical both
sides).

| pair | Δ `Ir`/call | Δ `Ir`/key |
|---|---|---|
| lookup, tree pre-built | **−1.00** | **−0.00024** ✅ reproduces `TASK_094` exactly |
| build + free | +119041 | **+29.06** |
| build + lookup + free | +119049 | +29.06 (additive to 0.008%) |
| build + lookup + **remove**, best R3 | **+196664** | **+48.01** (first R3 spelling: +52.00) |
| the `remove` term alone | +77623 | **+18.95** |

⚠⚠ **THE `−0.00024` IS REAL AND IT IS A ZERO ABOUT THE *WALK*** — the part of
the program the pattern is not about. **The task file instructed the engineer to
write that zero into `spec.md` §0 before measuring. That would have shipped a
FALSE declaration.** Kill risk 2 was correct and is now closed with a number.

**Mechanism** (callgrind function attribution, per key, `build_free`):

| term | safe | raw | Δ |
|---|---|---|---|
| descent | 180.66 | 149.59 | **+31.07** |
| the FREE (`drop_glue::<Box<SNode>>` vs hand-written `rfree`) | 16.99 | 19.00 | **−2.01** |
| `malloc`/`free`/libc | — | — | **byte-identical, 0.00** |
| total | 197.65 | 168.59 | **+29.06** |

✅ **The temporal guarantee still costs zero, and the SAFE FREE IS CHEAPER than
the hand-written one.** That is `p27`'s published decomposition
(`230.07 = 109.65 kernel + 120.42 drop_glue + 0.00 allocator`) **a third time**,
not a new result.

**Levers — R3 side 3 tried, R4 side 0, declared.** Double-match vs single-match
`insert` → `1603416.00` both (LLVM identical-code-folded them). `sremove` vs
`sremove_v3` → −16331. ⚠ **`sremove_v2` — the single-match descent that works for
`insert` — DOES NOT COMPILE for `remove`** (`1 error[E0499]`, `3 error[E0506]`):
**the double-match is forced, not chosen**, which is the answer to *"is your R3
pessimised?"*

## E6 — the R5 cell. ⚠ CONTRADICTS the task file's least-sure call #3, FAVOURABLY.

✅ **MANAGER-VERIFIED — re-run independently: `9 verified, 0 errors`, and the TCB
grep returns `0`.**

```
contains                      -> 4 verified, 0 errors   (t94 baseline reproduced)
+ insert                      -> 5 verified, 0 errors
+ is_leaf, remove_min, remove -> 8 verified, 0 errors
+ call_site                   -> 9 verified, 0 errors
TCB (assume|external_body|admit|assume_specification|external): 0
```

`remove` carries **all three cases including the two-child in-order successor**,
`ensures res.bst() && res.keys() =~= self.keys().remove(key)` — it re-establishes
`bst()` **and** relates `keys()` across the mutation, which `TASK_094` named as
*"the real budget"*. **No lemma, no `decreases_by`, no `assume`.**

**Non-vacuity, twice:** `call_site()` discharges `bst()` from `insert`'s own
postcondition and then removes a **two-child** key; and a mutant battery:

```
M0 baseline                                            9 verified, 0 errors
M1 splice the VICTIM's key, not the successor's        8 verified, 1 errors  assertion failed
M2 remove_min base returns the LEFT subtree            8 verified, 1 errors  postcondition not satisfied
M3 descend RIGHT when key < k   ⚠ NOT A VALID MUTANT: rustc E0382 use of moved value
M4 remove_min recursive drops k and the right subtree  6 verified, 3 errors  assertion failed
```

**3 of 4 are valid mutants; all 3 fail. M3 is disclosed as invalid** — it does
not typecheck.

---

## ✅ THE ARTEFACT THAT MUST NOT BE LOST WITH THE ROW

`.temp/` is gitignored and a refused row has no pattern dir, so per
`.memory/05-layout.md`'s refused-row corollary the source is **embedded below
verbatim**. `sha256 90a338c7567936464786e439a3f4e8e5da1ac3919e0853efaefcc31288811487`,
232 lines. **Manager-verified `9 verified, 0 errors`, TCB 0 at the pin.**

A fully verified BST — recursive `Box<Tree>`, `Set`-valued `keys()`, `bst()`,
`contains`, `insert`, `remove_min` and a three-case `remove` with the in-order
successor — **with zero trusted items.** The `p15` precedent applies: the row is
refused, the artefact is reusable.

```rust
// TASK_094 / p29 probe: is a RECURSIVE `Box` datatype admissible at the Verus
// pin at all, and can a BST lookup carry a real postcondition?
//
// This is p29's R5 feasibility question. The catalogue rates p29 "hard" and
// nothing has been run.
//
// Run: ./verus_run.py .temp/t94/v29_bst.rs --crate-type=lib
use vstd::prelude::*;

verus! {

pub enum Tree {
    Leaf,
    Node(Box<Tree>, u32, Box<Tree>),
}

impl Tree {
    // ghost: the set of keys in the tree
    pub open spec fn keys(self) -> Set<u32>
        decreases self,
    {
        match self {
            Tree::Leaf => Set::empty(),
            Tree::Node(l, k, r) => l.keys().insert(k).union(r.keys()),
        }
    }

    // ghost: the BST ordering invariant
    pub open spec fn bst(self) -> bool
        decreases self,
    {
        match self {
            Tree::Leaf => true,
            Tree::Node(l, k, r) =>
                l.bst() && r.bst()
                && (forall|j: u32| l.keys().contains(j) ==> j < k)
                && (forall|j: u32| r.keys().contains(j) ==> k < j),
        }
    }

    pub fn contains(&self, key: u32) -> (res: bool)
        requires self.bst(),
        ensures res == self.keys().contains(key),
        decreases self,
    {
        match self {
            Tree::Leaf => {
                assert(*self is Leaf);
                assert(self.keys() == Set::<u32>::empty());
                assert(!self.keys().contains(key));
                false
            }
            Tree::Node(l, k, r) => {
                if key == *k {
                    assert(self.keys().contains(key));
                    true
                } else if key < *k {
                    let res = l.contains(key);
                    assert(!r.keys().contains(key));
                    assert(self.keys() =~= l.keys().insert(*k).union(r.keys()));
                    res
                } else {
                    let res = r.contains(key);
                    assert(!l.keys().contains(key));
                    assert(self.keys() =~= l.keys().insert(*k).union(r.keys()));
                    res
                }
            }
        }
    }

    // ------------------------------------------------ TASK_095: insert, by value
    pub fn insert(self, key: u32) -> (res: Tree)
        requires self.bst(),
        ensures
            res.bst(),
            res.keys() =~= self.keys().insert(key),
        decreases self,
    {
        match self {
            Tree::Leaf => {
                let t = Tree::Node(Box::new(Tree::Leaf), key, Box::new(Tree::Leaf));
                assert(t.keys() =~= Set::<u32>::empty().insert(key));
                t
            }
            Tree::Node(l, k, r) => {
                if key == k {
                    let t = Tree::Node(l, k, r);
                    assert(t.keys() =~= t.keys().insert(key));
                    t
                } else if key < k {
                    let ghost oldl = *l;
                    let nl = (*l).insert(key);
                    let t = Tree::Node(Box::new(nl), k, r);
                    assert(t.keys() =~= oldl.keys().insert(key).insert(k).union(r.keys()));
                    t
                } else {
                    let ghost oldr = *r;
                    let nr = (*r).insert(key);
                    let t = Tree::Node(l, k, Box::new(nr));
                    assert(t.keys() =~= l.keys().insert(k).union(oldr.keys().insert(key)));
                    t
                }
            }
        }
    }

    // -------------------------------------------- TASK_095: is_leaf, an exec test
    pub fn is_leaf(&self) -> (b: bool)
        ensures b == (*self is Leaf),
    {
        match self { Tree::Leaf => true, _ => false }
    }

    // ------------------------------------- TASK_095: remove_min (in-order successor)
    pub fn remove_min(self) -> (res: (u32, Tree))
        requires self.bst(), !(self is Leaf),
        ensures
            res.1.bst(),
            self.keys().contains(res.0),
            forall|j: u32| res.1.keys().contains(j) ==> res.0 < j,
            res.1.keys() =~= self.keys().remove(res.0),
        decreases self,
    {
        let ghost s0 = self;
        match self {
            Tree::Leaf => { assert(false); (0u32, Tree::Leaf) }
            Tree::Node(l, k, r) => {
                if l.is_leaf() {
                    assert(l.keys() =~= Set::<u32>::empty());
                    assert(!r.keys().contains(k));
                    assert(r.keys() =~= s0.keys().remove(k));
                    (k, *r)
                } else {
                    let ghost oldl = *l;
                    let (m, nl) = (*l).remove_min();
                    let t = Tree::Node(Box::new(nl), k, r);
                    assert(oldl.keys().contains(m));
                    assert(m < k);
                    assert(!r.keys().contains(m));
                    assert(t.keys() =~= s0.keys().remove(m));
                    (m, t)
                }
            }
        }
    }

    // ---------------------------------------------- TASK_095: remove, all three cases
    pub fn remove(self, key: u32) -> (res: Tree)
        requires self.bst(),
        ensures
            res.bst(),
            res.keys() =~= self.keys().remove(key),
        decreases self,
    {
        let ghost s0 = self;
        match self {
            Tree::Leaf => {
                assert(s0.keys() =~= Set::<u32>::empty());
                Tree::Leaf
            }
            Tree::Node(l, k, r) => {
                if key < k {
                    let ghost oldl = *l;
                    let nl = (*l).remove(key);
                    let t = Tree::Node(Box::new(nl), k, r);
                    assert(!r.keys().contains(key));
                    assert(key != k);
                    assert(t.keys() =~= s0.keys().remove(key));
                    t
                } else if key > k {
                    let ghost oldr = *r;
                    let nr = (*r).remove(key);
                    let t = Tree::Node(l, k, Box::new(nr));
                    assert(!l.keys().contains(key));
                    assert(key != k);
                    assert(t.keys() =~= s0.keys().remove(key));
                    t
                } else {
                    // key == k: splice in the in-order successor
                    if r.is_leaf() {
                        assert(r.keys() =~= Set::<u32>::empty());
                        assert(!l.keys().contains(key));
                        assert(l.keys() =~= s0.keys().remove(key));
                        *l
                    } else {
                        let ghost oldr = *r;
                        let (m, nr) = (*r).remove_min();
                        let t = Tree::Node(l, m, Box::new(nr));
                        assert(oldr.keys().contains(m));
                        assert(k < m);
                        assert(!l.keys().contains(m));
                        assert(t.keys() =~= s0.keys().remove(key));
                        t
                    }
                }
            }
        }
    }
}


// ------------------------------------------------------------- TASK_095 call site
// Reviewer checklist: "Do the requires hold at a REAL call site, or is the fn
// dead/vacuous?"  This discharges `bst()` from `insert`'s own postcondition and
// then checks `keys()` across a remove of a TWO-CHILD node.
fn call_site() {
    let t = Tree::Leaf;
    let t = t.insert(50);
    let t = t.insert(25);
    let t = t.insert(75);
    let t = t.insert(10);
    let t = t.insert(30);
    assert(t.bst());
    assert(t.keys().contains(25));
    assert(t.keys().contains(10));
    assert(t.keys().contains(30));
    // 25 has TWO children (10 and 30) -- the in-order-successor case
    let u = t.remove(25);
    assert(u.bst());
    assert(!u.keys().contains(25));
    assert(u.keys().contains(10));
    assert(u.keys().contains(30));
    assert(u.keys().contains(50));
    assert(u.keys().contains(75));
    let b = u.contains(25);
    assert(b == false);
}

fn main() {}

}
```

---

## §0 verdict, in the engineer's words

> I do not have to answer *"is same class, different mechanism enough"* in
> general, because **p29's rejection mechanism is NOT different.** (a) is
> confirmed. (b) is refuted three ways: the `E0502` is generic borrowck
> reproduced on a one-field scalar struct *and on p27's own structure*; the
> key-addressed BST exhibits p27's runtime mechanism verbatim; and the shipped
> kernel shape cannot host the pointer at all, so what would ship is either
> **outcome 2** (p27's `Option<Box<T>>` discriminant — the same type and the same
> `*slot = None` operation) or **outcome 3** (silent, Miri-clean, p04's class).
> **p29 is not a fifth outcome of the allocator-guarantee rule.** The "matched
> pair" framing fails because **both mechanisms are available to both structures
> and the API, not the data structure, picks one.**

## Problems

- The task file's §2 instruction would have shipped a **false** declaration.
- ASan's `p27` payload word is ASLR-dependent and changes per run; recorded as
  such (`p27`'s own `NOTES.md` §7 has the same).

## Unsure / not done

- **R4 levers: ZERO searched.** This biases `+48.01` the *unflattering* way for
  safe Rust (the raw `rfree` measures dearer than the safe drop glue), but the
  sides are **not comparably searched** and `+48.01` must be read as best-found
  R3 minus a **non-minimised** R4.
- No six-rung set was built, so **there is no gate-flagged ASan/Miri matrix** —
  only the hand-run one in E2b/E3, each with a positive control that fired.
- **Adjacent, unmeasured, NOT proposed:** the BST's *other* C bug — a double free
  / dangling parent link in the two-child `remove` — is a different sub-class
  inside temporal, and `p27`'s `why` explicitly excluded double-free from its own
  scope. **It would need its own §0.**
- Did not re-check whether `p23` is still ranked 2.

## Memory updates owed (manager applies, after review)

1. `.memory/01-ladder.md`: **strike the `p29` "fifth outcome" paragraph.** Limb
   (a) survives; limb (b) is refuted.
2. `.memory/06-catalogue.md` `p29`: **REFUSED at TASK_095**, with E1/E2/E2b/E3.
   Keep the `v29_remove.rs` artefact.
3. `.memory/03-measurement.md`: **a cost pair that omits the alloc/free measures
   the WALK, not the class.** Third instance after `TASK_091`'s `p28` and
   `TASK_093_REVIEW`; here the same instrument reads `−0.00024` and `+48.01
   Ir/key` **on the same program**.
4. `.memory/01-ladder.md`: **`allocator = 0.00` is now THREE-FOR-THREE** (`p27`,
   `p28`'s `box_arena`, `p29`), and on `p29` the safe drop glue is *cheaper* than
   the hand-written recursive free (16.99 vs 19.00 `Ir`/key).
5. ⚠⚠ **Method rule: a BORROW-CHECKER DIAGNOSTIC IS NOT EVIDENCE ABOUT A DATA
   STRUCTURE UNTIL A CONTROL WITH NO DATA STRUCTURE HAS BEEN COMPILED.** Second
   occurrence (`TASK_093`'s `E0382`, `TASK_094`'s `E0502`).

## The four contradictions

| # | contradiction |
|---|---|
| 271 | the rejection-mechanism novelty is **false**, which also removes the fifth outcome |
| 272 | **the declared cost zero is false once the pair frees** — the manager's least-sure call #2 |
| 273 | **`remove`'s proof DOES fit one session** — `9/0`, TCB 0, first attempt — least-sure call #3, contradicted *favourably* |
| 274 | the catalogue's *"hard"* / *"expect R5 defeated"* is extended from `contains` to **the mutating operations** |
