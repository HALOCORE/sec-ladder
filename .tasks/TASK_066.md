# TASK_066 — p38, strict aliasing: the bug class where even UNSAFE Rust is immune

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then **`.memory/06-catalogue.md`'s p38 entry and its feasibility triage** — and
then the section below headed *"The manager's probes"*, **because they already
refute part of that catalogue entry**. Then `.memory/03-measurement.md` (**the two
`Ir` conventions, the INLINE-MODE rule, the DOMAIN rule, "name the routine" at
`:551`**), `.memory/01-ladder.md` (**findings 18 (p10) and 19 (p27)** — two
consecutive patterns with an unsearched R4 side), and **`patterns/p47-ct-compare/`
and `patterns/p18-varint-shift/`** as templates. p18 is the closest relative:
**UB that is not memory-unsafety, with every catcher outside the measured matrix.**

## Why this pattern is different from every other one here

**This is the first bug class that unsafe Rust does not reintroduce.** Every
pattern so far has the shape *"C has the bug; safe Rust rejects it; R4 gets it
back"*. Here **Rust has no type-based aliasing rule at all** — `noalias` on
`&mut` is *uniqueness*, which is a provenance property, not a type one — so
`ptr::read_unaligned::<u32>` into a `[u8]` is **fully defined**, and R2, R3, R4
and R5 are immune **by construction, not by checking**.

⚠ **That is the pattern's headline candidate and also its biggest risk.** If four
of six rungs are immune and identical, p38 is thin. **The load is therefore
carried by the C side**: the R1 spellings, R1h, and the flag. Say so in §0 and
decide whether that is enough. **If you conclude p38 should not be built as
specified, say that with the measurement** — that is a real outcome and cheaper
than a thin pattern.

## The manager's probes — provisional, and they already move the catalogue

I ran four probes to decide whether this pattern was feasible at all. Sources are
in **`.temp/p38probe/`** (`alias.c`, `weap.c`, `bytebuf.c`, `s_single.c`,
`s_lib.c`, `s_main.c`). ⚠ **These are MANAGER measurements and PROTOCOL rule 3
applies — re-derive the two marked load-bearing before building on them.**

**1. The bug class is REAL on this box. The catalogue's NULL-result risk is
refuted for the two-type shape.** `weap.c`, both compilers, `-O1/-O2/-O3`:
returns **1** under `-fstrict-aliasing` and **0** under `-fno-strict-aliasing`,
12 of 12 cells. The compiler is ignoring a store on the strength of the type rule.

**2. ⚠ LOAD-BEARING, AND IT REFUTES THE CATALOGUE'S OWN FRAMING. The idiomatic
byte-buffer shape is NOT weaponised.** `.memory/06-catalogue.md:400` describes
p38 as *"endian conversion / type punning (`memcpy` vs union)"* — i.e. reading a
`uint32_t` out of an `unsigned char` array. That is UB by 6.5p7, and **both
compilers produce the defined answer anyway**, at `-O2` and `-O3`, with and
without the flag (`bytebuf.c`, `via_cast=0` in 8 of 8 cells). Only
`two_types` — **two incompatible NON-char types aliasing** — moves (`1` vs `0`,
8 of 8).

> **So the pattern cannot be "parse a u32 out of a byte buffer".** That spelling
> is UB on paper and identical in practice, and a pattern built on it produces a
> null result *for the wrong reason* — not "the compiler declines to exploit
> strict aliasing" but "you chose the one aliasing direction that is benign".
> **§0 must pick a shape from the weaponised direction, and must show it is
> weaponised in the SHIPPED build, not in a probe** (p13's lesson: a text pin
> binds the source, not the object).

**3. TySan EXISTS and FIRES.** `~/tools/llvm/.../libclang_rt.tysan.a` is present,
`-fsanitize=type` links, and it reports
`TypeSanitizer: type-aliasing-violation … WRITE of size 4 with type int accesses
an existing object of type float`. **This is a catcher the project has never
used** and it belongs in the p18 box — outside the measured matrix.

**4. ⚠ LOAD-BEARING. TySan's blind spot is INLINING, not optimisation level.**
Same violation, same source, varying only whether the punning function is in its
own TU:

| | `-O0` | `-O1` | `-O2` | `-O3` |
|---|---|---|---|---|
| two TUs (not inlined) | fires | fires | fires | fires |
| one TU, `static` (inlined) | fires | **silent** | **silent** | **silent** |

Once the function inlines, SROA promotes the object to a register and the access
— with it the type-tag check — **stops existing**. **This project already has an
axis for exactly that: `isolated` vs `whole`.** If it holds up, p38 is the first
pattern where **the CATCHER has an inline-mode domain**, and that is a better
finding than the flag price. ⚠ It is also a single toy; **it may be SROA rather
than inlining as such.** Establish the mechanism, not the correlation
(PROTOCOL rule 12).

**5. The environment line is wrong: gcc here is 13.3.0, not 14.** The catalogue
(`:548`) and RECAP both say "gcc 14". p47's review had it right. The manager will
fix both; do not spend time on it, but **do not quote "gcc 14" either.**

## §0 — settle the bug class and the HARM first

`.memory/06-catalogue.md` calls it *"strict-aliasing UB"*. Probe 2 shows the
catalogue's own *spelling* of it is benign, so **the row is now a prior with a
known error in it** — four patterns overturned their row, two upheld it, and p47
overturned its own. §0's deliverable is a written decision in `NOTES.md` §0: the
bug, the wire format, what each cell does, and **why the rejected candidates were
rejected**.

⚠ **§0's second deliverable is the HARM, and it decides what kind of pattern this
is.** As probed, the observable is *"a function returns 1 instead of 0"* — which
is a wrong answer, not a memory-safety failure. That would make p38 p18's
sibling (**UB that is not memory-unsafety**) and the tree already has one.

> **My proposal, and it is the thing I am least sure of in this file — kill it if
> it does not reproduce:** make the deleted store a **bounds-narrowing** one. A
> parser reads a length field, clamps it, and the clamp is written through one
> type and read through an incompatible one; the compiler keeps the **stale,
> unclamped** length and the subsequent bounds check passes against it. **That
> turns a "wrong answer" into p02's harm — an out-of-bounds read — reached by a
> mechanism no pattern here has.** If it reproduces on the shipped binary, p38 is
> a memory-safety pattern and a strong one. **If it does not, say so plainly and
> fall back to the wrong-answer framing**, which is still publishable and still
> pairs with p18. ⚠ **Do not force it.** A contrived struct pair nobody would
> write fails the reviewer checklist's *"is the C rung idiomatic C, or
> Rust-in-C-syntax written to lose?"* — inverted, but the same defect.

## The measurement, and where it is unusually cheap here

Two of the three questions are **static** and cost no measurement:

1. **Does the UB spelling buy anything?** `harness/asm.py` on the `memcpy`
   spelling vs the cast spelling. Expected byte-identical.
2. **Is the store actually gone in the shipped cell?** Disassemble; do not infer
   it from the printed value.

The third is the one nobody here has priced:

> **What does `-fno-strict-aliasing` cost?** The Linux kernel builds with it.
> **No pattern in this tree has priced a whole-program-semantics flag**, and it
> is a genuinely useful number. ⚠ **But it is a BUILD-FLAG change and
> `build.py` is hashed into the MEASUREMENT records** (RECAP, settled answer 4):
> adding a flag to the shared matrix costs a full re-measure of every pattern.
> **Price it INSIDE p38's own `controls/`, not by touching `build.py`. If p38
> seems to need a `harness/` change, STOP and report it.**

## The rungs, and where I think this collapses

My proposal — **argue with it, and measure before adopting it:**

| rung | spelling | expected |
|---|---|---|
| R1 | the punning cast, in the weaponised direction | **UB**; store deleted |
| R1h | the same, built `-fno-strict-aliasing` | defined; **price it** |
| R2 | `u32::from_be_bytes(…try_into()?)` | immune by construction |
| R3 | the same, bounds-check-free spelling | immune |
| R4 | `ptr::read_unaligned` | **immune — Rust has no TBAA** |
| R5 | R4 plus a proof of the read's precondition | immune; proof says nothing about aliasing |

**Where it collapses, and settle each in §0 before building six rungs:**

- **If `memcpy` and the cast emit identical code** — the likely case — then *"the
  UB buys literally nothing and can delete your bounds check"* is the headline.
  That is a **clean, quotable, useful** result. Do not treat a zero difference as
  a failed pattern; it is the answer.
- **If `-fno-strict-aliasing` costs ~0 on a straight-line parser**, find the
  case where it does not — it should block vectorisation on a loop that writes
  through one type and reads through another. **A law owes its DOMAIN, and the
  domain is a missing column, not a caveat.** Two structural parameters that vary
  independently give you **additivity extrapolation**, the only out-of-sample
  test here that has ever been able to fail.
- **If R2–R5 really are all identical**, say it once, precisely, and do not pad
  the tables to look like six rungs did six different things.

## What p38 must have regardless

- **Record the `slb-contract` sha256 in `NOTES.md` before building any cell**, and
  ⚠ **read the shared named-spelling paragraph from a DONOR `spec.md` if you write
  a contract generator — never embed it** (`.memory/05-layout.md`).
  ⚠ **And if `spec.md` is generated, fix the GENERATOR too** — three tasks in a
  row shipped an edit the generator would have silently reverted, and one of them
  was the task fixing that defect.
- ⚠ **VERIFY YOUR OWN DISCLOSURE AGAINST `git`.** A false disclosure is worse
  than the stale thing it describes (p47, TASK_064_REVIEW M3):
  `git show HEAD:patterns/p38-*/spec.md | diff - patterns/p38-*/spec.md`.
- **Search the R4 side.** *"Degenerate as far as this task searched"* was **false
  on two consecutive patterns** and both times it flattered the safe rung.
  Publish the fixed-R4 bound **and** the span, "cheapest found", input named.
  ⚠ Here R4 is expected to be *immune*, which makes the search cheap — do it
  anyway, and say what you searched.
- **NAME THE INLINE MODE at every figure.** p10 fitted both and its regressors
  **swapped roles**, and probe 4 says the inline mode may govern the catcher too.
- **Adversarial rows per rung with distinct harms in distinct columns.**
  ⚠ **If four rungs are immune, four columns say so — that is the finding, not a
  gap.** But state what an adversarial row *means* when the harm is a
  miscompilation rather than a crash.
- **TySan belongs in the catcher table** with its domain from probe 4, alongside
  UBSan, ASan and Miri. ⚠ **Check whether UBSan catches it at all** — `-fsanitize=undefined`
  historically does **not** include a strict-aliasing check; if so, that is a
  fifth catcher-shaped hole and TySan is the only tool that sees this class.
- **No `ns` claim without a layout population**; port `controls/clayout.py`.
  ⚠ **Point `OUT` and the scratch default at `.temp/p38/`** — p27's copy still
  said `.temp/p14/` and overwrote p14's `meta.json` (`915bb8a`).
- **Two proof mutants that FAIL.**

## Verus

Budget **well under one session** — this is the cheapest R5 on the slate. The
read's precondition is an in-bounds one and the pattern is not about the proof.
**The deliverable is the honest statement that Verus has nothing to say about
type-based aliasing either**, which is p47's shape one axis over: state precisely
what is proved, what is not, and why. Use `~/tools/verus/vstd/` — **not**
`../LearnVeri/_VERUS_DOC_/vstd/`, an older snapshot missing specs that exist.
`global size_of usize == 8;` may be needed. **TCB: one number plus the
U-license / V-gap / infra classification.**

## Done when

The p47 checklist, plus §0's two decisions. Complete green `check.py p38`;
checksums against an independent `model.py`; the `idiom` block written **before**
the cells, **carrying the shared paragraph**; the flag price with its domain;
the catcher table including TySan and UBSan's outcome; both R3 numbers; two
failing proof mutants; TCB equal to the gate's own `tcb_items`;
`measure.py --check-stale` clean. **Paste actual output.** ⚠ Doc edits make a
gate record STALE — re-run after editing, not before.

## Constraints

No root; no `/tmp` (scratch **`.temp/p38/`** — your own subdirectory; the
manager's probes are in `.temp/p38probe/`, leave them alone); **no `git add`/`git
commit`**; do not edit `pilot/`, `.memory/`, `harness/`, `common/`, or any
existing pattern. **If p38 seems to need a `harness/` change, STOP and report
it** — especially for the flag, see above. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, gcc `/usr/bin/gcc` (**13.3.0**), valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none but gcc on
PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**.
Measurements in the FOREGROUND, interleaved by cell, per-PID scratch paths.
**You are the only agent running.** `harness/check.py p38` only. Delete binaries
and blobs once green; **keep every generator.**

Notes to `.temp/p38/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** The running
count is **130**, and it is a count of *agents* who corrected the manager — but
note that **two of this file's five probes corrected the manager's own catalogue
before you started**, so the prior on the rest of this file is not good.

**What I am least sure of, by name: the bounds-narrowing harm in §0.** I have not
built it. I do not know whether a clamp written through one type and read through
an incompatible one survives into a shipped binary as a real out-of-bounds read,
or whether every spelling of it that reproduces is too contrived to be idiomatic
C. **Measure that before building six rungs on it**, and if it does not
reproduce, the wrong-answer framing is the fallback and p38 is a smaller pattern.
Say which, with the output.
