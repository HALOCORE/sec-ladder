// content.js — the prose layer of the sec-ladder report.
//
// Everything numeric on this site comes from `data/` (built by build_data.py
// straight out of `results/` and `results/gate/`).  Everything *interpretive*
// lives here, hand-written from RECAP.md, .memory/ and each pattern's NOTES.md,
// so that a claim and the number under it never drift apart silently.
//
// Inline markup understood by the renderer: **bold**, `code`, and nothing else.

const LADDER = [
  {
    rung: "R1", key: "R1", track: "C", cells: ["c-gcc", "c-clang"], lang: "C",
    title: "C",
    line: "The baseline. No language-level safety.",
    check: "Absent. The program trusts the wire.",
    guarantee: "None. The bug is reachable from the input file.",
    body: "Written the way the CVE is actually written — the sizes are usually right there as parameters, and this rung trusts the wire instead. Two compilers, because `gcc` and `clang` disagree often enough that a single-compiler claim about \"C\" has been wrong here twice.",
    tcb: "everything",
  },
  {
    rung: "R1h", key: "R1h", track: "C", cells: ["c-gcc-h", "c-clang-h"], lang: "C",
    title: "hardened C",
    line: "The same C, plus the missing check.",
    check: "Hand-written, and only where you remembered to write it.",
    guarantee: "Safe on the modelled bug — if you remember to write the check, everywhere, forever.",
    body: "Without this rung, \"C is faster\" and \"C is unsafe\" risk being the same sentence, because some of C's speed is simply the check it never ran. R1 vs R1h is what that check costs inside one language, with no cross-language noise at all. ⚠ Measured, the median is under 1% and on about a third of the rows the check is free or better — which is the reason to build the rung, not a reason to skip it.",
    tcb: "everything",
  },
  {
    rung: "R2", key: "R2", track: "Rust", cells: ["safe_naive"], lang: "Rust",
    title: "safe Rust, naive",
    line: "The mechanical port a working programmer writes first.",
    check: "The language, at every single access.",
    guarantee: "Memory-safe. Out-of-bounds is a panic, not a corruption.",
    body: "Indexed element by element, `v[i]`, checked by the language. This is the rung most benchmarks publish as \"what safe Rust costs\". Doing that overstates the cost by **2.75× to 5.8×** on p01 depending on the workload, and by **77×** on p16's small input (222× on the large one). ⚠ The corpus median is about **6.75×**, over a range wide enough to include rows where the naive spelling is the cheaper one.",
    tcb: "zero",
  },
  {
    rung: "R3", key: "R3", track: "Rust", cells: ["safe_tuned"], lang: "Rust",
    title: "safe Rust, tuned",
    line: "The same program, written to let LLVM hoist the check out.",
    check: "The language still — but spelled so it leaves the loop.",
    guarantee: "Identical to R2 — same language, same guarantee.",
    body: "Reslice once, then iterate; `copy_from_slice`; `chunks_exact`. Still zero `unsafe`. **No safety-cost claim on this site ships without this column**, because the difference between R2 and R3 is a spelling difference, not a safety difference.",
    tcb: "zero",
  },
  {
    rung: "R4", key: "R4", track: "Rust", cells: ["unsafe"], lang: "Rust",
    // Measured on every pattern, but it is not a destination: the guarantee is
    // given up here and only R5 gives it back.  Shown de-emphasised so the
    // ladder does not read as though the climb ends at "unsafe".
    aside: "measured for comparison — not a destination",
    title: "unsafe Rust",
    line: "C's performance, C's (un)safety, inside a Rust program.",
    check: "Removed. The obligation moves to the programmer.",
    guarantee: "None, at the access. The obligation is now the programmer's.",
    body: "`get_unchecked`, raw pointers, `copy_nonoverlapping`. The check is gone and so is the guarantee — but the scope is small and named, which is the whole argument for `unsafe` as a language feature.",
    tcb: "every unsafe block",
  },
  {
    rung: "R5", key: "R5", track: "Rust", cells: ["verus"], lang: "Rust + Verus",
    title: "unsafe Rust + Verus proof",
    line: "R4's machine code, with a machine-checked proof that R4's unchecked steps really are safe. **Verus** is the prover; it reads the Rust and either proves the claim or refuses.",
    check: "Removed from the binary, and settled before it ever runs — by an automatic theorem prover, at compile time.",
    guarantee: "Memory-safe, machine-checked, at R4's speed.",
    body: "Same executable code as R4 — the kernels are byte-identical at `-O3` on most patterns, and on the rest they hold the same instructions in the same order with only pc-relative addresses differing (see finding 1). The `requires`/`ensures`/`invariant`/`decreases` clauses are ghost and erase completely. What is left is a trusted base of a few `external_body` wrappers, counted per pattern, whose `ensures` every caller must then discharge.",
    tcb: "the external_body wrappers, counted",
  },
  {
    rung: "R2v", key: "R2v", track: "Rust", cells: ["safe_naive_verus"], lang: "Rust + Verus",
    title: "safe Rust + Verus",
    line: "A control, built once (p01): prove the safe rung panic-free.",
    check: "Still emitted — proving it unreachable does not remove it.",
    guarantee: "Memory-safe, plus a proof that the panic is unreachable.",
    body: "It changes nothing in the binary. **rustc never learns what the solver knew** — the bounds check is still emitted. This cell is why finding 2 exists.",
    tcb: "zero",
  },
];

const RUNG_BLURB = Object.fromEntries(LADDER.map(r => [r.rung, r]));

// The four diffs worth showing, which are the ladder's own transitions.
//
// There is no gcc-vs-clang diff because there is no gcc-vs-clang difference to
// show: both C cells compile the SAME FILE, and so do both hardened C cells.
// That pair differs by compiler, not by source, and its cost shows up in the
// instruction columns rather than here.
const DIFF_PAIRS = [
  {
    id: "c-check", a: "c-gcc", b: "c-gcc-h", label: "C → hardened C",
    // one source diff, two compiled ones: gcc and clang disagree often enough
    // here that a single-compiler claim about "C" has been wrong twice.
    asm: ["c-gcc-check", "c-clang-check"],
    isolates: "The check, written out by hand. This is the whole of what R1h adds, and it is what makes \"C is faster\" and \"C is unsafe\" the same sentence — C is faster **precisely in that it skipped these lines**.",
  },
  {
    id: "r2-r3", a: "safe_naive", b: "safe_tuned", label: "R2 → R3 · spelling", asm: ["r2-r3"],
    isolates: "Two safe Rust programs with the **identical guarantee**, differing only in how they are written. Everything here is a spelling difference, not a safety difference — which is why no cost claim on this site ships without the R3 column.",
  },
  {
    id: "r3-r4", a: "safe_tuned", b: "unsafe", label: "R3 → R4 · the check", asm: ["r3-r4"],
    isolates: "Where the language's check is removed and the obligation moves to the programmer. This is the only one of the four diffs in which the **guarantee changes**.",
  },
  {
    id: "r4-r5", a: "unsafe", b: "verus", label: "R4 → R5 · the proof", asm: ["r4-r5"],
    isolates: "The proof, and nothing else. The R4 and R5 kernels are **byte-identical machine code**, so every line added here compiles to nothing at all — this diff is a picture of exactly what a machine-checked proof costs at run time, which is zero. What it costs instead is on this page's proof tab.",
  },
  {
    // Cross-language: the two sources are different LANGUAGES, so there is no
    // line diff to take and `sourceDiff: false` puts them side by side
    // unchanged.  The comparison lives in the compiled kernels.
    id: "ch-r4", a: "c-clang-h", b: "unsafe", label: "hardened C → R4 · language",
    sourceMode: "pair", asm: ["ch-r4-clang"],
    isolates: "**The comparison that counts, and the only one with no backend difference in it.** clang 22.1.6 is bit-for-bit the LLVM that rustc 1.97.1 ships, so hardened C compiled by clang against unsafe Rust is one middle-end asked the same question twice — any difference here is the *language*, not the compiler. **gcc is deliberately not in this comparison**: it would confound backend with language, and this project has published that mistake before. The gcc-against-clang tab is where the backend's own contribution is measured, and it is the control this one needs.\n\nThere is no source diff because the two sources are not the same language; they sit side by side instead. ⚠ Expect the instruction streams to share **almost nothing** line for line — two compilers rarely emit the same sequence — so read the instruction *count* and the *shape*, not a line-by-line correspondence.",
  },
  {
    // One source file, two backends.  Not a language comparison at all — it is
    // the control that says how much of any C-vs-Rust gap was never about Rust.
    id: "c-backend", a: "c-gcc-h", b: "c-clang-h", label: "gcc vs clang · same source",
    sourceMode: "single", asm: ["ch-gcc-clang"],
    isolates: "**One file, two backends.** Both rungs compile the *same* `kernel_hardened.c` — there is nothing to diff in the source, so it is shown once. Everything that differs below is the compiler and only the compiler.\n\nThis is the control the C-vs-Rust tab depends on. A gap between hardened C and unsafe Rust means nothing until you know what two C compilers do to the identical source, and on this project they disagree often enough that a single-compiler claim about \"C\" has already been wrong twice. Click a line to see both backends' instructions for it at once.",
  },
];

// The Verus highlight classes, explained where the reader meets them.  These
// four are not decoration: they are the categories this project's own claims are
// made in, which is why `trusted` gets the loudest treatment.
const VERUS_LEGEND = [
  ["vspec", "specification", "`requires` `ensures` `invariant` `decreases` — what the kernel promises. Checked by the solver, erased before codegen."],
  ["vproof", "proof", "`proof` `assert` `by` `forall` `lemma_*` — the work that discharges the obligation. Also erased."],
  ["vghost", "ghost", "`spec fn` `ghost` `tracked` `Seq` `int` `nat` — values that exist only for the proof. No run-time representation."],
  ["vtrust", "trusted — NOT verified", "`external_body` `assume` `#[verifier::…]` — the trusted base. These bodies are **taken on faith**, and every one is a place the guarantee can be silently wrong. This project counts them per pattern."],
];

// The two tracks the ladder is really made of.  The languages approach the same
// destination from opposite ends, and saying so is the clearest statement of
// what this benchmark is for.
const TRACKS = [
  {
    id: "C", name: "C", start: "performance first",
    arc: "starts fast and unchecked, then has the check added by hand",
    dir: "adding safety →",
  },
  {
    id: "Rust", name: "Rust", start: "safety first",
    arc: "starts checked by the language, then has the cost taken back out",
    dir: "removing cost →",
  },
];

// --------------------------------------------------------------- the patterns --

const PATTERNS = {
  "p01-array-sum": {
    title: "Array sum over a window",
    family: "A · buffers",
    bug: "none — calibration",
    role: "The template every later pattern clones.",
    story: [
      "Sum `v[off .. off+len)` with wrapping `u64` addition. It models no bug; its job is to prove that the harness, the driver, the input format and all five rungs work, and to give every later pattern a number to be compared against.",
      "It produced the two results the whole programme rests on. **A proof costs exactly zero instructions** — the verified and unverified binaries are byte-identical. And **a proof alone buys nothing**: proving the *safe* rung panic-free leaves every bounds check in place, because rustc never learns what the solver knew.",
    ],
    caveat: "On this kernel LLVM hoists the bounds check clean out of the vectorised loop, so safety costs a per-call constant regardless of `n`. That is a warning about the method, not a conclusion about Rust — the patterns that matter are the ones where the optimiser *cannot* hoist.",
    convention: "Kernel-exclusive and marginal agree here.",
  },
  "p02-buffer-copy": {
    title: "Length-prefixed buffer copy",
    family: "A · buffers",
    bug: "CWE-787 — out-of-bounds write",
    role: "The security result: idiomatic C is silent in seven of eight builds.",
    story: [
      "A `u16` length prefix off the wire says how many bytes to `memcpy` into a fixed 64-byte destination. Both sizes are right there as parameters; R1 has them and trusts the wire instead. That is the common shape of the CVE, and it is what makes the comparison honest.",
      "On a **one-byte** overflow, idiomatic C prints a plausible answer and exits 0 in **seven of eight builds** — heap corruption absorbed by glibc's chunk rounding. The eighth aborts only because Ubuntu defaults `_FORTIFY_SOURCE 3`. Every Rust cell and every hardened-C cell handles it.",
      "The control matters as much as the result: delete the check from safe Rust and it *panics* rather than corrupting. \"Rust makes the check non-optional\" is a measurement here, not a slogan.",
    ],
    caveat: "\"Safe Rust pays an O(n) bounds-check tax\" was published from this pattern and is **retracted**. The indexed fold's bounds checks cost zero; the whole delta was one spelling of an overflow check defeating LLVM's `memcpy` idiom recognition. Three other spellings are +10 flat.",
    convention: "Marginal Ir per call; the kernel-exclusive column distorts a ratio by 0.19 here without reordering anything.",
  },
  "p03-bounded-stack": {
    title: "Bounded stack over an opcode stream",
    family: "D · state machines",
    bug: "CWE-124 / CWE-125 — buffer underwrite, underflow read",
    role: "The safety tax IS the price of the optimiser failing the invariant the proof proves.",
    story: [
      "The first kernel here whose **control flow is in the file**: each 5-byte record says push or pop, so the attacker picks the path, not just the data. The first whose safety law is per *executed operation*.",
      "The control that settles it: `m_clamp` is R3 plus a **dead** `if sp > STACK_CAP { return 0; }` — R5's own invariant, handed to LLVM as ordinary code. Safe drops 17 → 13 Ir per executed pop, unsafe 14 → 13, and the **gap becomes exactly zero on both sides**, with zero fitted parameters.",
      "It is the invariant and not range propagation: `sp > 1000` is byte-identical to shipped R3 (i.e. changes nothing), `sp > 65` leaves the check standing *and* is dearer.",
    ],
    caveat: "Two qualifications, both measured. It is **not Rust-specific** — clang keeps a manual C bounds check at exactly 4.00 Ir per executed pop, gcc keeps it too, and both delete 100% of it given the identical clamp. And LLVM does eventually derive the fact, so this is analysis **seeding**, not inability. The shipped 3.00 is one spelling's rate; in contract the class runs +3.00 … −1.00 per executed pop.",
    convention: "Kernel-exclusive. The whole-program marginal carries a ±7 Ir alignment term here — `main`'s frame puts a 512-byte stack array at a different alignment and glibc `memset` takes a different path.",
  },
  "p04-ring-buffer": {
    title: "Ring buffer with wraparound",
    family: "D · state machines",
    bug: "CWE-787 — overwrite, entirely in bounds",
    role: "Known bits survive a loop-carried phi where a range does not.",
    story: [
      "A bounded FIFO — `uint64_t ring[64]`, two live cursors, an opcode stream deciding enqueue or dequeue. **The bug is a missing fullness check and every index it forms stays inside the array.** A push over a full ring overwrites the oldest element: no OOB access at all.",
      "Which makes it invisible to memory safety, and that is the finding. With the functional spec stripped, dropping either guard — or both — still verifies **9 obligations, 0 errors**, against five positive controls that correctly fail.",
      "The three-operator series closes here. Does a bound survive a **multiply** (p05: no — nonlinear), a **shift** (p09: yes alone, no through the composition), a **modulus**? The measured rule, zero fitted parameters: `urem x, C` implies `x < next_pow2(C)`, and `next_pow2(CAP) ≤ ARR_LEN` is **necessary** for the check to be elided.",
    ],
    caveat: "The published explanation of the `% 60` case — \"it fixes no bits\" — was **false**; it fixes `< 64`, and that survives the phi. And the shipped R3 is not the cheapest found: a two-step reslice is 1 Ir/call cheaper by **register allocation**, not by deleting a check. Both bounds ship, labelled.",
    convention: "Kernel-exclusive; the whole-program marginal carries a stack-alignment term as on p03.",
  },
  "p05-index-flatten": {
    title: "2-D index flattening",
    family: "A · buffers",
    bug: "CWE-129 / CWE-190 — improper index, overflow one width down",
    role: "The first vectorised kernel, and the first causal link from proof to performance.",
    story: [
      "Fold `data[i*ncol + j]` — what performance-critical numerical C actually looks like. The header declares `nrow × ncol`; the kernel checks `nrow*ncol <= avail`, so R2's panic is **dead on every run**.",
      "Per element *inside* the vector body the check is free: 1.375 Ir/element, five rungs identical. But it is hoisted into a 22-instruction per-row trip-count computation and survives in the scalar epilogue, so the cost is `O(nrow)` — and **wider lanes make it worse**: at AVX2 the gap is 4.58× against SSE2's 1.42×.",
      "The cause is the interesting part. LLVM cannot eliminate the dead panic because `nrow*ncol <= avail ⟹ i*ncol+j < avail` is **nonlinear** — which is exactly the obligation R5 discharges with `lemma_mul_inequality`. Linearise the guard and the whole per-row apparatus disappears.",
    ],
    caveat: "p05 has no minimum and neither does any pattern here. Three floors were published and all three refuted, each by the first lever the next agent pulled. `min(R3) − min(R4)` differences two upper bounds and bounds nothing in either direction. What ships is the fixed-R4 bound and the R3-side span.",
    convention: "Marginal Ir per call.",
  },
  "p06-rotate": {
    title: "In-place rotate",
    family: "A · buffers",
    bug: "unreduced rotation amount — two regimes, one of them not a memory error",
    role: "The pattern where the instruction count gets the sign of the answer wrong.",
    story: [
      "Copy a record into a fixed local `uint8_t scr[64]` and rotate the live prefix left by an attacker-supplied `r`, spelled as the classic three in-place reverses. The safety line is `r %= m` — **the first one in this project that is a division** rather than a compare-and-branch.",
      "Which is why it breaks the headline metric. callgrind prices a hardware `div` at exactly **1 Ir**; Cascade Lake charges tens of cycles. Measured: `R1h − R1` is **+41/+95 Ir under gcc and −45/−108 under clang**, while the clock says **+18.8%/+57.9%** and **+10.3%/+11.6%** over a 30-layout population. Two hardened spellings with *exactly the same* Ir differ by 8.5% and 16.5% in wall clock.",
      "And on `large` under clang, **hardening is faster than the bug** — the cheapest in-contract hardening runs 6.9% faster than the unhardened kernel, and the worst layout pair in a 30-layout population is still 2.5% faster. Reducing `r` proves `r < 64`, which lets LLVM fold a four-byte header decode into one `mov`.",
      "The safety line also pays for itself in safe Rust: `R2 − R4` is `32.00·nrec + 13` and **0.00000 Ir per rotated byte**, and decomposed one loop at a time, 100% of it is the record-header decode — writing `get_unchecked` in the three reverse loops produces a **byte-identical** kernel, because `r %= m` already bounds every cursor by the array's own constant capacity.",
    ],
    caveat: "Two more things this pattern is careful about. **23% of gcc's exact, zero-residual safety law is executed alignment padding** — per record, 1.000 Ir is the `divq` and 1.833 is executed `.p2align` `nop`s; `-fno-align-loops` moves the law from +8.00 to +73.00 per record without changing any semantics. And the bug has **two regimes**: while the unreduced rotate stays inside the array, five unchecked programs — C on both compilers, two safe-Rust rungs with the check deleted and zero `unsafe`, and unsafe Rust — print the same wrong answer, exit 0, ASan and UBSan clean.",
    convention: "Kernel-exclusive; and on this pattern the instruction count is explicitly *not* the cost model — quote the bracketed wall clock beside it.",
  },
  "p10-fir-stencil": {
    title: "Weighted FIR stencil",
    family: "A · buffers",
    bug: "out-of-bounds read on the tap window",
    role: "A headline that was wrong in the flattering direction.",
    story: [
      "The first kernel here with **several indexed reads per iteration** at fixed offsets from a cursor — a `2r+1`-tap dot product whose radius is read from the file. So it can finally ask whether safe Rust's tax is proportional to the *number* of indexing operations.",
      "**The answer is neither flat nor proportional.** At `-O3` the tap loop vectorises in *every* spelling, including the naive indexed one, to the same seventeen-instruction SSE2 body. The per-tap checks survive only in the scalar epilogue: **0.00 Ir on every tap the vectoriser reached, +3.00 Ir on every tap it did not**, plus a 41.00 Ir per-output constant whose largest identified component is a 24-instruction `cmp`/`cmov` chain computing how many taps may be vectorised safely.",
      "That bounds the \"safety is cheap\" finding by naming a **mechanism** rather than a data size, and it reproduces p05's `O(nrow)` hoisted-guard result on a kernel whose obligation is **linear** — where p05's stated excuse had been that its own was nonlinear.",
    ],
    caveat: "The delivered headline said safe Rust beat unsafe Rust, and **none of that gap was safety**; review corrected fourteen interpretive claims. Every figure has to name its `-O3` mode — `isolated` and `whole` disagree about the mechanism — and its domain, because a *rejected* call is a fifth and sixth model parameter rather than a caveat.",
  },
  "p19-state-machine": {
    title: "Protocol state machine",
    family: "D · state machines",
    bug: "CVE-2026-23407 shape — unvalidated transition table",
    role: "Safe Rust's bounds check and the validation pass C omits are the same predicate.",
    story: [
      "Each window is a 2048-byte transition table followed by a message; the decoder folds the message through the table one indexed load per byte. The C rung never validates the table it was handed, so an entry naming a state that does not exist becomes the next row index and the load leaves the blob — the shape of the AppArmor `verify_dfa()` bug.",
      "The result is a coincidence worth stating precisely: LLVM lowers safe Rust's per-access bounds check to `cmp $0x8`, a **state-range check** — the very predicate C's missing validation pass enforces. The difference is *when*: the validation pass is `O(table)`, once per call; the bounds check is `O(message)`, once per access.",
      "So which is cheaper depends on the message: **the buggy C rung is cheaper than unsafe Rust at `small` and dearer at `large`**. The same two programs swap places on input size alone.",
    ],
    caveat: "An earlier version of this pattern named CVE-2026-23269 — a real but *different* AppArmor bug about start states, which this kernel does not model, since its walk starts at state 0 by construction. The review confirmed the headline and refuted three numbers the research manager had written himself.",
  },
  "p22-hash-probe": {
    title: "Open-addressing hash probe",
    family: "C · containers",
    bug: "non-terminating probe loop — not a memory-safety bug",
    role: "The first pattern where safe Rust does not help.",
    story: [
      "A fixed-capacity open-addressed table with linear probing. The C rung inserts without checking how full the table is, so on a full table the probe loop walks every slot and **never terminates**.",
      "Both plain-C rungs hit the declared 2-second timeout on `adversarial-full`; both hardened-C rungs and **all four Rust rungs return the model's answer**. The fix is a fill count, not a bounds check — and that is the point. **Memory safety is not the property violated here**: every index stays in the table forever, so Miri is silent, ASan is silent, and safe Rust's bounds checks buy nothing at all.",
      "What sees it is the proof obligation nothing else in the ladder carries: **termination**. This is the outcome class the rest of the corpus does not have — not corruption, not a wrong answer, but a service that never comes back.",
    ],
    caveat: "The hang is *declared* in the contract (with its timeout), so the gate can tell \"never returned\" from \"crashed\" — and the pattern read `PASS-WITH-BLOCKED-ROWS` until the gate learned to read a per-**rung** hang column instead of a per-input flag, because a per-input boolean cannot say which rung is the one that hangs.",
  },
  "p27-handle-table": {
    title: "Handle table over per-record allocations",
    family: "E · lifetimes",
    bug: "CWE-416 — use after free",
    role: "The one temporal bug class, and the lifetime guarantee costs zero.",
    story: [
      "Opcodes from the file open, close and read records held in a handle table. The C rung's READ checks that the handle is in range but not that the record is still live, so it dereferences a freed allocation.",
      "**Every other bug in this project is spatial or logical** — an index outside an allocation, or a wrong answer inside a live one. Here the address is inside **no live allocation at all**, which is the one class safe Rust rejects at *compile* time rather than at run time.",
      "Measured, the lifetime guarantee costs **zero instructions**, and on this kernel safe Rust pays *less* spatial tax than unsafe Rust does.",
    ],
    caveat: "This is also the first pattern with a **multi-clause trusted accessor**, which is where the verified twin starts earning its keep — the earlier claim that the twin's value began at p17 was retracted, because that pattern's accessor is single-clause too.",
  },
  "p36-vtable-dispatch": {
    title: "Function-pointer table dispatch",
    family: "F · dispatch",
    bug: "index ≥ len — but the harm is a control transfer",
    role: "The prover excludes the mechanism, not a spelling.",
    story: [
      "A one-byte bytecode interpreter: the opcode indexes a table of eight callables and the interpreter **calls what it finds**. Omit `op < NOPS` and an out-of-table opcode loads a code pointer from past the table and jumps to it — a deterministic SIGSEGV on 24 of 24 runs across both compilers and four optimisation levels.",
      "**No checker in the matrix names the call.** ASan reports a global-buffer-overflow on the *array read*; UBSan reports an index out of bounds on the *array read*; gcc has no `-fsanitize=function`, and clang's is defeated because the garbage is not a function so the signature read faults first. Only `-fsanitize=cfi-icall` names the call, and it needs LTO and lld, so it cannot be a rung. The matrix is blind in **vocabulary**, not in coverage.",
      "And the sharpest instance of the R4-is-chained-to-the-prover result: **Verus cannot type `fn(u64) -> u64` at all**, so C's dispatch mechanism has no admissible Rust rung. The substitute costs **3.00000 Ir per dispatch** — the prover excluding a *mechanism* rather than a spelling.",
    ],
    caveat: "This is the pattern where the proof is **not free in bytes** (finding 1's scope clause): a `spec fn` declared in a trait takes a vtable slot in the erased build. And its identity pin covers the kernel function's bytes and **not** the dispatch table — reversing the table's entries leaves `md5_fn` identical and is caught by the checksum stage instead, which the pattern says out loud rather than leaving implied.",
  },
  "p38-alias-pun": {
    title: "Strict aliasing / type punning",
    family: "G · undefined behaviour",
    bug: "strict-aliasing violation — the harm is a miscompile",
    role: "The first class unsafe Rust does not reintroduce.",
    story: [
      "A wire format whose 32-bit record length arrives as two 16-bit halves. The parser clamps an over-long length in place through a `uint16_t*` and reads it back through a `uint32_t*` accessor — so the compiler is entitled to assume the two pointers do not alias, and is entitled to drop the clamp.",
      "The harm is therefore not a bad address computed by the program: it is **the optimiser removing the check the programmer wrote**. `c/kernel.c` is the first here whose bounds check *is written* and ignored anyway.",
      "R2 through R5 are immune by construction — Rust's punning goes through `from_le_bytes` and friends with defined semantics — which makes this **the first bug class unsafe Rust does not reopen**. It is also the only pattern whose adversarial behaviour is build-dependent: SIGSEGV at `-O3`, the right answer at `-O0`, from one source file.",
    ],
    caveat: "Shipped labelled a **demonstration kernel**, not a claim about code in the field: the harm needs four conjunctive conditions, and **six defined spellings of the same kernel are cheaper on gcc than the undefined one** — five of them by exactly 6.00 Ir/call. The earlier line that \"real parsers are written this way\" was uncited and is withdrawn. The ladder result is unaffected.",
  },
  "p47-ct-compare": {
    title: "Constant-time tag comparison",
    family: "H · side channels",
    bug: "data-dependent timing — not memory unsafety",
    role: "The rung that certifies a leaking kernel.",
    story: [
      "Tags are compared and only the *verdict* is folded, so two windows with the same verdict sequence and different first-mismatch positions produce the same checksum in every rung — the functional contract cannot see the leak.",
      "**Both C `memcmp` rungs and safe Rust's `a == b` on two slices leak** in executed instructions; hardened C, tuned safe Rust and both unsafe rungs accumulate over every byte and do not. So on this pattern **safe Rust leaks and hardened C does not** — the ladder's ordering says nothing about the property at issue, because the property is not memory safety.",
      "R5 verifies the same contract as R4 and **the obligation count does not move**. The proof certifies a leaking kernel not because it is weak but because nobody asked it the question: a specification of *what* is computed cannot constrain *how long* it takes.",
    ],
    caveat: "Read the non-leaking column as `Ir` being constant, which is a **necessary** condition and not a sufficient one — constant instruction count is not constant time on real hardware, and this box cannot measure the difference.",
  },
  "p07-binary-search": {
    title: "Binary search",
    family: "A · buffers",
    bug: "CWE-125 / CWE-129 / CWE-190",
    role: "The first kernel where R3's tax never amortises.",
    story: [
      "`Θ(log n)` probes, no inner loop — so there is no axis along which the check gets cheap. R3 costs **6.0000 Ir per probe**, and its share of kernel instructions *rises* in both `n` and the query count: 42.53% → 46.63% over `n` = 7 … 16 385, asymptote in [46.15%, 50.00%].",
      "Confirmed across six deliberately different workloads — all-hit, all-miss, all-below, all-above, clustered, shipped — monotone rising in every one. The cost laws are exact integers verified **out of sample** on 30 fresh blobs: `R3 − R4 = 9 + 4·nq + 6·probes`, 30/30 exact.",
      "It is also the sharpest demonstration that instruction count is not time. Disabling one LLVM pass on unchanged source gives **+10.07% instructions and −18.13% wall clock**; changing only the *workload* makes the same binary execute **+7.84% more instructions in 71.75% less time**.",
    ],
    caveat: "This is not \"the first counterexample to safety is cheap\" — p16/p17 carry a swept R2 tax and p05 an `O(nrow)` R3 tax. What is new is that p07's tax vanishes along nothing. Do not quote p07's R2 wall-clock numbers: that rung's code-layout band is 28.47%, the widest measured here.",
    convention: "Marginal Ir per call.",
  },
  "p08-overlap-move": {
    title: "Overlapping move",
    family: "A · buffers",
    bug: "CWE-1341-adjacent — memcpy where memmove is required",
    role: "The bug safe Rust cannot express.",
    story: [
      "Shift a read buffer right to make room at the front — the nested-encapsulation idiom. `memmove` is correct; `memcpy` is undefined behaviour whenever the ranges overlap, and the displacement comes from the file.",
      "Safe Rust **cannot write this bug**: the borrow checker rejects it at compile time. There is no runtime check, so there is nothing to measure — the safety is structural and free. `unsafe` re-opens it through `copy_nonoverlapping`.",
      "**R5 does not close it.** Substituting `copy_nonoverlapping` into the trusted body verifies 11/0, and 15/0 under the verified twin — invisible to Verus, to the twin and to the contract pins. Only Miri and the byte-identity pin catch it. A proof that a `requires` holds is not a proof that the trusted body honours it.",
    ],
    caveat: "On this libc the UB **executes and is unobservable** — glibc 2.39's `memcpy` *is* `memmove`, so R1 ≡ R1h at 0.00 Ir/call. That is a property of this libc and must never be quoted as \"memmove is free\". ASan does see the overlap — unless `_FORTIFY_SOURCE` rewrites the call to `__memcpy_chk`, which blinds it under clang as well as gcc.",
    convention: "Marginal Ir per call, with a ±0.08 environment drift through glibc's alignment-dependent path.",
  },
  "p09-bitset": {
    title: "Bitset probe",
    family: "A · buffers",
    bug: "CWE-125 — out-of-bounds read",
    role: "One character separates a bug everything catches from a bug nothing catches.",
    story: [
      "The guard is `q < nbits`; the access is `words[q >> 6]`. The bound the access needs is derived from the guard **through a shift**, and neither the guard's operand nor the array's length appears in it.",
      "`words[q >> 5]` is caught by memory safety alone — bounds check, ASan, Miri, and the proof's precondition, on every input. `words[q >> 7]` is caught by **nothing**: `q/128 ≤ q/64`, so under the guard it is always a legal word index. It verifies 19/0 with the functional spec stripped, costs **zero instructions**, and the whole 368-byte kernel differs in **one byte**. Every build prints the same wrong answer.",
      "And it is a class of at least nine, not an instance: the obligation reduces to `C·(nwords−1) + 8 ≤ 8·nwords`, so every shift digit above 6 and every scale below 8 qualifies.",
    ],
    caveat: "Quote `q >> 7`, not `q & 31` — the latter is a *two*-character edit costing +32% on R4, and p09 shipped calling both \"one-character bugs\". This pattern also carries the project's only R3 > R2 inversion, and it is a lost 8-byte load-merge idiom, not deleted checks.",
    convention: "Marginal Ir per call.",
  },
  "p11-nul-scan": {
    title: "NUL-terminated string scan",
    family: "B · strings",
    bug: "CWE-125 — out-of-bounds read",
    role: "Library, spelling and safety, separated three ways.",
    story: [
      "The first kernel here whose **loop bound is not known before the loop** — a NUL scan runs until it finds a sentinel that may not be there.",
      "The decomposition is the pattern's point. C `strlen` reaches glibc's IFUNC and AVX2 at **0.078 Ir/byte**; `CStr::from_bytes_until_nul` reaches `core::slice::memchr`'s SWAR at **0.94**; `iter().position()` is a scalar byte loop at **5.00**; unsafe `get_unchecked` at **6.00**; naive indexing at **9.00**. So **12.0× is a library difference, 5.3× is which Rust spelling, and 3.00 Ir/byte is the bounds check** — where the naive report would have been one ratio.",
      "It is also the largest instance of \"R4 is chained to the prover\": the `CStr` spelling would be **−35% of the kernel** and is rejected with four `is not supported` errors. The safe class reaches that library at zero trusted lines; the unsafe class cannot reach it at all.",
    ],
    caveat: "p11 discharges an overflow obligation with one line in the program where p17 had to buy a second `requires`, and shipped calling that free. It is not: it costs 1.00 Ir per scanned byte, **8.5% of R4**, because the guard forces the scan's exit reason into a register. Neither route is free.",
    convention: "Marginal Ir per call — the kernel-exclusive column reverses real rung comparisons here, because the scan calls out of the kernel symbol.",
  },
  "p12-strcat-fixed": {
    title: "strcat into a fixed buffer",
    family: "B · strings",
    bug: "CWE-121 / CWE-787 — stack buffer overflow",
    role: "The bulk-copy lowering needs BOTH ends of the copy free of a per-iteration check.",
    story: [
      "The classic stack overflow: append NUL-terminated strings into a fixed local `uint8_t dst[128]` and never ask whether the next one fits. The first bug here that is a **write** safe Rust cannot express, and the first time `c-gcc` and `c-clang` differ in *behaviour*.",
      "The control the pattern did not build, and the reviewer did: a **safe byte loop** with no bulk call anywhere in its source still lowers to `memcpy`. So the recovery is about *where the check is*, not about `copy_from_slice` carrying its own bound. And checking only the **source** per byte kills the lowering too — both ends must be free.",
      "Observability is a function of magnitude and compiler: **+1…+8 bytes is silent and wrong on both compilers**, then gcc's canary and clang's caller-frame corruption, then clang's SIGSEGV.",
    ],
    caveat: "p12's structural claim was too strong and the reviewer built the row it said could not exist. The premise generalises by the guard's **threshold**, not by the write: a threshold at the allocation's extent makes \"the guard fired\" and \"the unguarded rung committed UB\" the same event; a threshold inside the allocation makes them independent — and then write patterns behave exactly like read patterns. It reaches 2 of the 5 patterns it was written for.",
    convention: "Marginal Ir per call.",
  },
  "p13-strncpy-trunc": {
    title: "strncpy truncation",
    family: "B · strings",
    bug: "CWE-170 / CWE-125 — missing terminator, then an OOB read",
    role: "A bound the optimiser can SEE outweighs the check that supplies it.",
    story: [
      "The first bug here that is a **correctly-called library function** rather than an omitted line, and the first whose harm lands at a *different site* from the bug. `strncpy(dst, src, sizeof dst)` is textbook C and still wrong: it does not terminate when the source is at least as long as `n`.",
      "The corrected mechanism is better than the published one. R4 makes the same two library calls at the same cost; 72% (`small`) and 91% (`large`) of the gap is the **consumer scan**, and the direction is the reverse of what was published: a consumer whose bound LLVM can see fully unrolls to 2 Ir/byte, an unbounded walk stays a 4-instruction loop at 4.",
      "**The discriminator is the bound, not the check.** An *unchecked but bounded* scan costs exactly what safe `position()` costs, to the instruction. This is p03's and p04's seeding result arriving from the other direction: there the invariant had to be handed to LLVM as dead code; here the safety check supplies it as a side effect and more than pays for itself.",
    ],
    caveat: "The margin was inflated by p13's own contract, which pinned the byte-loop copy in the unsafe rungs and exempted the safe rung **by name**. Allow R4 a bounded unchecked consumer — it verifies 19/0 with no new trusted items — and `R3 − R4` becomes **+44 / +77**. Three numbers ship. Separately: C's whole advantage here is a *library* difference, and with `-fno-builtin-strlen` the sign of every same-backend C-vs-Rust row flips.",
    convention: "Totals, not the kernel-exclusive column — the first pattern whose rungs call *different* libc routines.",
  },
  "p16-tlv-walk": {
    title: "TLV record walk",
    family: "C · parsing",
    bug: "CWE-125 — out-of-bounds read",
    role: "The first data-dependent loop bound, and safety is still free per byte.",
    story: [
      "Walk a chain of length-prefixed records inside a window and fold every byte visited. A length field claims more than remains, and a walker that trusts it folds its way off the end. Nothing is hoistable, no bulk idiom to lose — the case p01 said not to generalise to.",
      "**The per-byte safety tax is 0.00000, and that is the sentence to quote.** Swept over 127 consecutive value lengths at six spellings: slope of the safe-minus-unsafe difference `0.0000000` Ir/byte, max residual 0.00. The mechanism is why it cannot be otherwise — the reslice (safe) and the `get_unchecked` (unsafe) both sit **outside** the fold loop, so the chunk body is mnemonic-identical at K = 4, 8, 16, 32 and 64.",
      "Only the naive indexed spelling is `O(n)`: +4.25 Ir/byte. A rolled-vs-rolled control shows **exactly 2.00 is the check and 2.25 is the 4× unroll it forecloses**, zero residual — and it costs +0.27% of wall clock, because the fold is latency-bound at 3.03 cycles/byte on both L1- and L3-resident inputs.",
    ],
    caveat: "Never quote a bare per-byte rate from this pattern. In contract, one exact-string substitution apart, p16's rate ranges 5.05 … 6.63 — a 31% spread — and the measured rates carry ±0.01 Ir/byte from the driver's `println`, which is 20× the gap between two published rates. A cross-spelling *difference* of two such rates is worse; one reached four files as a headline and was wrong.",
    convention: "Marginal Ir per call.",
  },
  "p17-http-range": {
    title: "HTTP suffix-range parser",
    family: "C · parsing",
    bug: "CWE-191 — integer underflow, gated on the sign",
    role: "The limit: provably memory-safe, and still leaking.",
    story: [
      "CVE-2017-7529, in miniature. `start = content_length − N` is signed, so an `N` larger than the body makes it negative, and the only validation — `if (start < end)` — passes for every negative start. The served range is the *last* `s` bytes, so one attacker `u16` picks the harm.",
      "For `content_len < s <= len` the bad read is **inside the allocation**: ASan clean, exit 0, and **safe Rust with the check deleted prints C's value bit-for-bit**. Only for `s > len` does it leave the allocation and Rust panic. Memory safety is a property of *addresses*, and this attack does not need to leave the object.",
      "Then the artefact. Guard the **slice**-relative index — `start >= -((off + body_start) as i64)`, which is exactly what a bounds check buys, no more — and Verus discharges **every access obligation**; the single remaining error is the *functional* invariant. The program reads a neighbouring window's bytes: output tracks the victim's secret, no panic, no `unsafe`. **A provably memory-safe program that leaks.**",
    ],
    caveat: "Two corrections are baked into the paragraph above. The *shipped* adversarial-leak row discloses only the attacker's own request table — it shows memory-safe-but-wrong, not disclosure. And the first delivered guard was strictly *stronger* than a bounds check, which made its leak vacuous. The distinction is one token, and it is the whole finding: write \"what a bounds check buys\" **slice**-relative.",
    convention: "Marginal Ir per call.",
  },

  // Reviewed upstream, and the review moved BOTH of its headlines — which is
  // why this entry leads with the corrections rather than the claims.
  "p42-goto-cleanup": {
    title: "goto cleanup — a leak on the error path",
    family: "E · lifetimes",
    bug: "an early return that skips the cleanup chain",
    role: "The rung where the resource is freed on every path but one.",
    story: [
      "The kernel takes a heap digest buffer sized from the window, then validates the record's tag. A malformed tag is an error, and the C rung returns from inside the validation **without joining its own `cleanup:` chain**. The hardened rung is the same file with that `return 0;` replaced by `goto cleanup;`, returning the same value on that path. Nothing else differs.",
      "**The interesting question is not whether the leak happens but whether a proof can say it does not — and this row has now been wrong about that twice, in opposite directions.** First it published that the prover could not state leak-freedom. Then it published a ghost-ledger encoding that supposedly did, at `18 verified, 0 errors`. ⚠ **That second answer was refuted in turn and is withdrawn in full**: the ledger's removal call is the very call the release path already makes, so a kernel that leaks on the error path still verifies at `18 verified, 0 errors`. A third encoding was built and it too admits a verifying leaker.",
      "So what stands is a negative, and it is the more useful result: **at this prover and this library, the natural encodings do not force the cleanup to happen.** The proof discharges what it was asked, and \"the resource is released on every path\" was not among the things it was asked — even when the author believed it was, and had written a mechanism intended to ask it.",
      "**The comparative headline was refuted too.** A published result that tuned safe Rust beat the unsafe rung does not stand: the unsafe side had not been searched hard enough, and an admissible spelling that never leaves the allocation flips the sign — a difference reported as favouring safe Rust becomes a small difference the other way. The pattern's own hashed contract had predicted exactly this failure, in writing, before it happened.",
    ],
    caveat: "⚠ **Three published proof claims on this one row, and the first two are withdrawn.** The current statement is the negative one: the encodings tried here do not state leak-freedom, and a leaking kernel verifies clean under each of them. Treat this as the project's sharpest example of the difference between *what a proof checks* and *what its author believed it checked*. The cost result is now a pair of overlapping spans rather than a comparison — which is the honest shape when neither side's search is finished. Its Miri run on the larger input is a declared, disclosed timeout rather than a silent gap.",
  },

  // ⚠ Written while this pattern was still landing upstream — its gate went
  // from FAIL to PASS in the course of one afternoon — and BEFORE its review.
  // So everything here comes from `spec.md`, the contract, which is hashed into
  // the gate record; nothing comes from its measurements. Note the caveat does
  // not state the gate's verdict: the page renders that live, and a sentence
  // here claiming it was already false within the hour. Add the cost and proof
  // claims once its review has landed and its NOTES.md carries the findings.
  "p23-partition": {
    title: "In-place Hoare partition",
    family: "C · containers",
    bug: "two cursors, each bounded only by the other",
    role: "The first bound here that comes from inside the loop.",
    story: [
      "A record's elements are copied into a fixed `scr[64]` and partitioned in place around a pivot **taken from the input** rather than from the sub-array. The clamp `m = min(nelem, SCR)` is in every rung; what the buggy rung drops is the `i < j` conjunct on each of the two scans.",
      "**Every earlier bound in this project comes from outside the loop** — a header field, a compile-time capacity, a live length. Here `i` is bounded by `j`, `j` is bounded by `i`, **and both move**. The fact that makes the pair sufficient, `j <= m <= SCR`, is established once before the loop and never re-read.",
      "Textbook Hoare partition gets its stopping condition for free by taking the pivot *from* the sub-array, which guarantees an element on each side. This kernel is handed a pivot instead, so it does not — and **the code that relies on that guarantee looks identical to the code that does not.**",
      "**The project's own headline for this pattern: the safety tax is a function of the data's shape, not its size.** The safe-versus-unsafe difference moves by a factor of **1.315×** with the element count, the record count and the copied bytes all held fixed, and only the pivot's rank changing. The mechanism was isolated rather than argued: the compiler already removes the check on the *upward* cursor and not on the *downward* one, so the direction of the cursor is the whole tax. ⚠ This row first published that factor as **3.11×**; a later review corrected it.",
    ],
    caveat: "⚠ **This row's headline was corrected by review, and the correction is large.** It was published at 3.11× and re-measured at 1.315× — the mechanism survived, the magnitude did not. The description above is written from `spec.md`, the kernel contract hashed into the gate record. Its own notes also record what is *not* done: two sweep bands ship unfitted, and one band's fit has ±30 residuals and **must not be quoted as a law**.",
  },

  "p25-realloc-growth": {
    title: "A pointer held across a reallocation",
    family: "E · lifetimes",
    bug: "use-after-free through a pointer a growth invalidated",
    role: "The only bug here that needs no free at all — growth retires the memory.",
    story: [
      "You save `cur = &toks[i]` into a growable array, then push one more element. `realloc` may move the block, and the moment it does your saved pointer names memory the allocator has handed to someone else. **No `free` appears anywhere in this kernel** — the growth itself retired the storage. The buggy rung omits one conjunct on the read path; the whole repair is **two net lines of C**.",
      "The striking part is what that guard buys. Because `realloc` copies the old contents, re-deriving the element after a move gives back exactly the byte the stale pointer named — so **both rungs compute the same answer on every input, and the harm is invisible to every checksum.** The guard buys memory safety and nothing else. It is not free: it runs on every benign call, costing roughly **+15 to +164 instructions per call** depending on compiler, workload and optimisation level.",
      "Then the pattern turns on itself. Under the C standard the old pointer is indeterminate the moment `realloc` returns, whether or not the block moved — so even *comparing* it is a read of an indeterminate value, and **the shipped hardened C is not standard-clean either.** A control that simply re-derives the element unconditionally is measured at 2–2.5× cheaper on gcc and 5–5.5× on clang.",
      "Above C the bug stops existing. Safe Rust cannot hold a reference across a push, so every Rust rung stores an **index** instead — and because `realloc` copies, the index is correct by construction. Safe Rust delivers the hardened answer at no cost, not by checking harder but by making the mistake unspellable.",
    ],
    caveat: "Two cautions the pattern states itself. The compile error is **not** the evidence: a 12-line control with no container, no growth and no saved reference produces the same `E0502`, which is the fourth time in this project a compiler code was read as saying more than it does. And the setup is tuned — under this driver `realloc` relocates at exactly one growth step, so this measures a bug that is *reachable*, not one that fires often. At the proof rung the temporal obligation has no analogue at all: Verus cannot express provenance for a `Vec`'s buffer, so only the spatial residue is proved.",
  },

  "p28-intrusive-lists": {
    title: "One object, two lists, one destroy path",
    family: "E · lifetimes",
    bug: "an object freed while a second list still links to it",
    role: "The only row where the missing check is a write, not a test.",
    story: [
      "A bounded cache wants each object reachable two ways: by recency, and by key. C programmers put both sets of links **inside** the object — one allocation, O(1) removal from either list. That is why intrusive lists exist, and it is also the trap: the object is now a member of two containers, and **membership is not ownership**. Deleting by key already holds the cursor it needs; evicting the oldest does not, and the buggy rung frees the object without going to fetch one.",
      "The repair is **nine lines, a pure addition** — a splice, not a test. That makes it the only pattern here whose safety line is a piece of work rather than a question, and it is why the usual mental model (\"safety costs a compare and a branch\") does not fit this row.",
      "**One omitted block produces three different harms, and the input picks which.** A later read of that bucket reads freed heap; a write puts one byte inside a freed chunk; a delete splices through a word the allocator has already reused, and the process crashes. The third shape is a **double free**, and it was found late — only an allocator interposer sees it, because the crash arrives two statements before ASan would report anything.",
      "Safe Rust **cannot reproduce this bug at all**, and the reason is the data structure rather than the language: one object on two intrusive lists is two owners, so every Rust rung stores slot numbers instead of pointers. The project tested that claim hard rather than asserting it — 3.25 million exhaustively enumerated operation sequences and 20,000 randomised windows, **zero wrong answers** — and then named the two structural facts it depends on. Change either and the result is gone.",
    ],
    caveat: "This pattern deliberately publishes **no cost comparison between C and Rust**, on three declared confounds: the C objects are 40 bytes against Rust's 6, the epilogues differ, and ten checks in the Rust rungs have no C spelling. Its own notes warn that a differently-built version of this row would have published \"safe Rust is 6× cheaper\" with most of the gap in the allocator. The proof rung is also weaker than it looks: deleting the safety line from **both** the code and the specification still verifies, so the proof forces the specification and not the free.",
  },

  "p34-refcount-stack": {
    title: "The retain that was never paid",
    family: "E · lifetimes",
    bug: "a missing reference-count increment on the acquire path",
    role: "The smallest safety line in the project — one line — and it costs exactly zero.",
    story: [
      "Manual reference counting is supposed to make objects valid by construction: allocate at one, increment when you take another reference, free at zero. The bug is a missing `rc++` when an operation publishes a **second** stack entry naming the same object. The repair is **one line, a pure addition** — the smallest safety line in the corpus.",
      "It costs **exactly 0.00 instructions per call on all sixteen measured cells**, and the reason is structural rather than lucky. That statement is the kernel's only increment, so in the buggy rung every object's count is permanently one; any input that reaches the line at all is already an input on which the program goes on to free memory it still uses. **There is no input where the guard runs and the program stays safe** — checked exhaustively over 33.6 million operation sequences.",
      "The harm is sometimes invisible to the answer. On two adversarial inputs the buggy and fixed rungs produce **bit-identical checksums** and only ASan can tell them apart; on a third the allocator hands the freed block straight back and the answer diverges. Which one you get depends on the allocator's reuse policy, not on the bug.",
      "The Rust side splits in two, and that split is the finding. In the reference-counted port the bug is **not expressible** — it will not compile. But an index-arena port, written under `#![forbid(unsafe_code)]`, **reproduces the buggy C bit for bit on all eight inputs, with Miri silent.** Same language, same guarantee, opposite outcome: what protected you was the ownership discipline you chose, not the language you chose.",
    ],
    caveat: "⚠ This row does **not** show \"safe Rust is worse than C\", and an earlier version of that claim was withdrawn after measurement. Neither C rung leaks on any shipped input, and the buggy rung frees too **early**, so it cannot leak. It also does not support a C-versus-Rust ratio: the C side had no spelling search, and the shipped-pair gap at `-O0` was itself overstated by about 3× before both sides were searched. Read the zero as belonging to the **site** — an acquire the correct program never reaches — and not to reference counting as a technique: an alternative repair on the destroy path costs 5–22% of the kernel.",
  },

  "p35-tagged-union": {
    title: "The tag that lied",
    family: "F · dispatch",
    bug: "type confusion — the tag is published before the payload lands",
    role: "The only safety line here that is a statement ordering, not a check.",
    story: [
      "A tagged union is a byte saying which type, beside storage holding one of them. The bug is ordinary and easy to write: the buggy rung **writes the tag first and then attempts the store**, and when the store fails for want of space the cell claims a type its bytes are not. A later read dispatches on that lie. The entire repair is **moving two statements** — same lines, different order.",
      "One ordering produces two harms and the detectors disagree about them. The pointer arm dereferences an attacker-derived integer and ASan fires. The floating-point arm compares a garbage value and **nothing reports it** — not ASan, not UBSan, not either compiler at `-Wall -Wextra` — because reading a union through the wrong member is *defined* in C. It is simply wrong.",
      "In safe Rust the check has nowhere to live. An `enum` carries its tag and its payload as **one value written by one assignment**, so there is no window between them and no site for a safety line at all — the boundary moved to compile time. Unsafe Rust reproduces C's shape and gets the obligation back by hand.",
      "In C the safety line is **better than free**: the hardened rung is cheaper on all sixteen measured cells, and at `-O0` the mechanism closes exactly at **5 instructions per failed tag store**. The honest reading is not \"safety is free\" but \"the bug wastes work\" — the buggy rung performs a tag store roughly 33 times per call that nothing ever reads.",
    ],
    caveat: "⚠ The proof rung on this pattern is the project's own gate making things worse, and it is disclosed rather than fixed. Verus checks union variants natively, but the gate's rule that every `unsafe` token must sit inside a trusted wrapper moves the union read **out** of the checked region — and Rust has no safe spelling of a union read, so the verified-twin stage cannot run either. The gate records this as blocked rows rather than a pass. Worse, a control deletes the central correctness clause from all three readers and the proof still reports no errors: only an author-written pin catches it. A cost comparison between safe and unsafe Rust was also published from this row and then retracted.",
  },

  "p29-bst-delete": {
    title: "Deleting from a search tree, with a cached lookup",
    family: "E · lifetimes",
    bug: "a cached record pointer used after the record was freed — or reused",
    role: "One omitted line, two different bug classes, and the input picks which.",
    story: [
      "A search tree keeps each record in its own allocation. Deleting a key does one of two things depending on the victim: a node with fewer than two children is unlinked and **freed**, while a node with two children has its successor's contents copied **into** it and the successor freed — so that allocation is never released, it just acquires a **new occupant**. A cached pointer from an earlier lookup is wrong in both cases, and the buggy rung omits the one line that would notice.",
      "**That is the finding: the same missing line produces a use-after-free and a use-after-recycle, and only the first is detectable.** ASan, Miri, Rust's `Option`, and the proof's linear permissions are all mechanisms about the *allocation*. On the recycle input Miri runs the buggy program to completion, reports nothing, and prints the wrong answer. The half every tool can see is the half you did not need help with.",
      "It inverts on reproducibility too, which is worse for testing. Reading freed memory gives a different answer nearly every run — obviously broken. Reading a **recycled** record gives the *same* wrong answer every time, on both compilers, at both optimisation levels: a stable, plausible, wrong number. The bug that hides from the sanitizer is also the bug that looks deterministic in your test suite.",
      "⚠ **This pattern's original headline was measured and retracted.** It shipped claiming the fix needed two checks where a sibling pattern needed one; a later task built two single-check versions and both were clean, one of them adding no state at all. What survives is the two-bug-class mechanism; the counting claim is gone.",
    ],
    caveat: "This row publishes **no cost numbers at all** — neither rung's spelling was searched, and the project is explicit that the absence must not be read as a zero. Its safe-versus-unsafe gap is also not licensed for comparison. And safe Rust does **not** catch this by itself: the safe rungs are correct because the author wrote the occupant-identity check by hand. The language supplies the first half through `Option` and nothing at all for the second.",
  },

  "p32-free-list-pool": {
    title: "A pool that recycles its own blocks",
    family: "E · lifetimes",
    bug: "a stale handle used after its slot was recycled",
    role: "The row where every memory-safety tool in the project is silent — correctly.",
    story: [
      "This pool never calls the allocator. It is one fixed array carved into blocks with a free list; a block is **popped and pushed, never allocated and freed**, so the storage belongs to the program from first instruction to last. Handles are a `(slot, generation)` pair, and every release bumps the generation. The buggy rung asks only whether a handle exists, not whether it is still *this* incarnation. The whole repair is **two lines**.",
      "**Because nothing is ever allocated, nothing can detect the bug.** ASan, UBSan and Miri are silent on all nine inputs while four of them return a wrong answer and two produce two live handles naming one block. This is not a tooling failure — those tools reason about allocations, and there are none. The bug is real, the memory is legitimately owned, and the safety property being violated is one nobody instrumented.",
      "The comparison that makes it concrete: the same C source built on `malloc` storage instead **aborts** on two of the three harms. Identical logic, identical bug, and the allocator turns an invisible corruption into a loud crash. But the third harm, the use-after-recycle itself, is **bit-identical and silent in both** — that one is storage-independent.",
      "**And safe Rust reproduces the buggy C exactly.** A version written under `#![forbid(unsafe_code)]` matches the C arena rung on all ten measured cells, wrong answers included. This is the sharpest statement of a rule the project arrived at the hard way: Rust's temporal guarantee is a guarantee about the **allocator**. A structure that recycles its own storage gets no guarantee at all, and no amount of `forbid(unsafe_code)` changes that.",
    ],
    caveat: "⚠ **This pattern ships with no cost axis, and the absence is declared rather than measured** — neither rung's spellings were searched, so any safe-versus-unsafe number computed from it elsewhere on this site is a number without a search behind it. The proof result is also a gap rather than a success: deleting the safety check from the code alone fails, from the specification alone fails, but deleting it from **both** verifies cleanly — because there is no linear resource for it to attach to. The proof forces the specification, and here the specification is all there is.",
  },

  "p49-interned-pool": {
    title: "An interned string pool, from a real CVE",
    family: "C · containers",
    bug: "a write through a shared buffer the writer does not own",
    role: "The one pattern ported from a published CVE — and the aliasing is the feature, not the defect.",
    story: [
      "String interning saves memory: when a short string is already in the table, the new record just **borrows** the existing buffer. Two records then legitimately name one buffer, on purpose, breaking no rule. The defect is that a later cleanup step writes through that buffer without first asking whether it owns it — so one record silently corrupts another's value. This is a port of **CVE-2022-40304**, where the same shape corrupted a hash key and ended in a double free.",
      "**Nothing is allocated, nothing is freed, and every index is in bounds — so no tool sees it.** Across 216 sanitizer cells (both C rungs × two compilers × two optimisation levels × plain/ASan/UBSan × nine inputs) there are **zero diagnostics**, and Miri adds eighteen more silent cells. The checksum is the only instrument that separates the two rungs. The project ships positive controls alongside, precisely to prove the detectors were switched on at all.",
      "**Safe Rust offers both the bug and the repair, with no `unsafe` in either.** Written with a shared mutable cell, it reproduces the buggy C bit for bit; written with `Rc::make_mut`, it reproduces the fixed one — because copy-on-write is what the standard library hands you. The language did not decide the outcome here. The data structure the author reached for did.",
      "The repair is also **not** the upstream project's own patch, and that was decided by measurement rather than deference. Upstream fixed it by never borrowing, which deletes the deduplication the pool exists for — it moves three of three benign answers. Copy-on-write moves none.",
    ],
    caveat: "The port is faithful to the aliasing mechanism and explicitly not to the rest: allocation is banned outright, so **the CVE's double free is not modelled at all**, there is no hash and therefore no collision path, and the buffers are a few bytes each in a 64-byte pool. There is no single price for the safety line either — it is `+25` instructions per call on one build and `−3` on another of the same input, and the law explaining the sign is gcc-only. The three Rust arms were checked for their answers and **never priced**, so \"safe Rust offers both\" is a claim about expressiveness carrying no cost number.",
  },

  "p14-field-split": {
    title: "Delimiter-framed field split",
    family: "C · parsing",
    bug: "unbounded field count against a fixed descriptor table",
    role: "The pattern whose headline was refused, and the refusal is the result.",
    story: [
      "The bound here is **a count of a byte value, not a length** — how many `,` the line contains, against a 16-entry descriptor table. R1 omits `if (nt == MAXTOK) break;` and nothing else.",
      "Hardening fits an **exact** law: `c-gcc-h − c-gcc = 1.00·bytes + 2.00·fields − 3.00`, max residual 0.0000 over 66 blobs. On the inputs this pattern exists to model, the same difference **inverts** — −551, −823, −611 against +93, +93, +429 — which reads as *hardening is cheaper than the bug*.",
      "**That headline was proposed and refused, and the refusal is the finding.** Past the cap the two cells no longer compute the same function, the unhardened rung is already committing UB, and on one blob the `c-clang` cell is not a function of its arguments at all. What ships is **the law with its domain stated**, and outside that domain *behaviour* rather than *cost*.",
    ],
    caveat: "The law is fitted entirely on inputs where the guard never fires — every `Ir` figure in this project is, by construction: `measure.py`'s plan is six entries, all `small.bin`/`large.bin`, so no published cost number anywhere is measured on a bug-triggering input. Read the law as describing the in-contract kernel, and read the adversarial table for what happens outside it.",
  },

  "p18-varint-shift": {
    title: "LEB128 varint decoder",
    family: "G · undefined behaviour",
    bug: "out-of-range shift count — UB that touches no memory",
    role: "The bug the memory-safety ladder is not built to see.",
    story: [
      "Every other defect here is spatial or logical-but-in-bounds. This one addresses nothing, allocates nothing and stores nothing: it shifts past the accumulator's width and returns a silently wrong integer. **ASan is silent.**",
      "**Four things do catch it — UBSan, `-C debug-assertions`, Miri and Verus — and every one of them is outside the 24-cell matrix.** So the matrix says *clean* and the answer is wrong. ⚠ Miri catches it as a **panic**, not as an `Undefined Behavior` report, so a gate keying on the UB flag alone calls it clean too.",
      "The row this pattern exists for: **safe Rust with the guard deleted — containing zero `unsafe` — is bit-identical to C's R1 on every adversarial blob** at `-O3 -C debug-assertions=off`. Safety here was never in the language; it was in the line.",
      "`R1h − R1 = 2.00·bytes`, zero fitted parameters, **and it does not amortise** — 11.89% of `small`'s kernel instructions and 11.11% of `large`'s.",
    ],
    caveat: "*“Verus catches this bug”* is spelling-conditional — `wrapping_shl` verifies, because it is defined. And the sanitizer catches the **undefinedness, not the wrongness**: a deliberately *defined* `<< (shift & 63)` control has R1's cost law and R1's wrong answer with UBSan silent throughout.",
  },

  "p46-bignum-mac": {
    title: "Schoolbook bignum multiply-accumulate",
    family: "A · buffers",
    bug: "product width unchecked against a fixed output buffer",
    role: "The pattern where the rung boundary did not shrink — it vanished.",
    story: [
      "Two bignums whose limb counts arrive in the input, multiplied schoolbook into a fixed-capacity product buffer. Every rung checks the operands fit the *window*; the buggy C rung never checks the product fits the *buffer*. The model is OpenSSL's `BN_mul()` and its `bn_wexpand()` — the classic bignum miscount.",
      "**The safety tax is `0.00000` per MAC, and the ordering is `safe_naive < safe_tuned < unsafe`.** `n` and `m` are `u8`-derived and `n + m <= OUTCAP` is tested, which is all LLVM needs to discharge `i + j < 96` itself and delete all three bounds checks. The safe inner loop contains no conditional branch but its own `jne`.",
      "**So “safe beats unsafe” here is entirely an unroll decision.** Rolled against rolled, shipped sources unedited: `R2 − R4 = +2.00000·n·m` exactly, over five shapes with zero residual — *against* safe Rust. Safe pays `xor` + `setb` to materialise the carry plus a separate store; unsafe pays one extra `adc`. Net +2, the measured coefficient, and neither loop bounds-checks anything.",
      "**A pre-build probe predicted `+5.05 Ir/MAC` and was wrong in sign.** The first published explanation blamed `black_box` and was also wrong — every probe kernel has external linkage, so a caller-side `black_box` cannot reach the callee's codegen, and rebuilding without it gives byte-identical binaries. The real cause is one level up: **a probe whose kernel signature differs from the shipped kernel's loses the range facts the shipped kernel derives from its input header.**",
    ],
    caveat: "The method result is the sharpest in the corpus and it is about fitting, not about Rust: **a two-parameter law fitted on two axis-aligned bands is underdetermined, and no in-sample residual can reveal it.** Four equations, three independent; a whole family of coefficients fits both bands exactly. One off-axis point pins it, and the remaining band blobs then have zero residual out of sample. Ship one off-axis point in every band.",
  },
};

// ------------------------------------------------------------- the findings --
// `status`: standing | corrected | retracted.  Corrections are shown, not hidden:
// four of these were published wrong first and the correction is the result.

// The two halves of the Findings lede, either side of a count that index.js
// derives. It read "Twelve results ... Four of them are marked corrected" as a
// constant while the list held fifteen and five.
const FINDINGS_LEDE = {
  a: "results that are about the *landscape*, not about one pattern.",
  b: "of them are marked **corrected**: they were published wrong first, and the correction is the more interesting half — so it is shown rather than quietly folded in.",
};

const FINDINGS = [
  {
    id: 1, title: "A Verus proof costs exactly zero executed instructions.",
    status: "corrected", tags: ["proof"],
    body: [
      "Ghost code — `requires`, `ensures`, `invariant`, `decreases`, every proof block and lemma — erases completely before codegen. The proven kernel is **byte-identical** to the unproven one, verified on **raw machine-code bytes** of the kernel symbol at `-O3`. Not on a normalised disassembly: an earlier oracle erased every immediate and displacement, and a review built two kernels with **different answers** and the same normalised digest.",
      "⚠ **The scope clause, and it took 22 patterns to find:** on **p36** the two kernels are 55 instructions and 170 bytes each with identical normalised text, and **exactly one instruction differs** — a `lea` whose pc-relative displacement moved. The cause is not the proof's *code* but its *declaration*: a `spec fn` declared in a trait **occupies a vtable slot in the erased build**, codegenned as a stub, so R5's vtables are 40 bytes where R4's are 32. The proof there costs **64 bytes of `.data.rel.ro` and a 26-byte `.text` stub** that R4 does not have, and that shift is what moved the displacement.",
      "⚠ **And the exception is no longer a single pattern.** As the corpus grew past the first two dozen, four more rows joined p36 at the weaker level — the pointer-backed structures. On all five the two kernels have the **same instructions in the same order**, and differ only in pc-relative address fields; each row documents its own reason in its own notes, and they are **not** all p36's vtable story. Do not read them as one finding.",
      "So the sentence that survives everywhere is the narrow one: **zero executed instructions, and zero instructions inside the kernel symbol** — `R5 − R4 = 0.00` on every pattern and both workloads. The wider sentence, *“the proved binary is byte-identical to the unproved one”*, is true on most patterns and false on the rest, and the count is on the **Proof & trusted base** tab where it is derived rather than typed. ⚠ Note the `Ir` zero is *entailed* by byte-identity where that holds, so it is not independent evidence there; the raw-byte digest is.",
    ],
  },
  {
    id: 2, title: "A proof alone buys nothing. It has to license unsafe code.",
    status: "standing", tags: ["proof"],
    body: [
      "Proving *safe* Rust panic-free leaves every bounds check exactly where it was — rustc never learns what the SMT solver knew. p01's `safe_naive` and `safe_naive_verus` are byte-identical too.",
      "The payoff arrives only when the proof is used to *license* `unsafe`: R5 is R4's machine code with the obligations discharged at compile time by the verifier instead of at run time by the CPU. The interesting axis is therefore not \"does verification slow things down\" (it does not) but **what you must move into the trusted base to get C's assembly, and how much proof it takes to keep that base sound**.",
    ],
  },
  {
    id: 3, title: "Reporting the naive safe rung overstates safe Rust by 3.7× to 75×.",
    status: "standing", tags: ["cost", "method"],
    body: [
      "R2 (indexed, `v[i]`) and R3 (reslice once, then iterate) are the same language with the same guarantee. The gap between them is a **spelling** difference and it dwarfs the safety difference on several patterns.",
      "3.7× on p01, ~75× on p16. No safety-cost claim on this site ships without the R3 column — a rule this project broke itself, one pattern after writing it.",
    ],
  },
  {
    id: 4, title: "Static instruction counts are not a cost model.",
    status: "standing", tags: ["method"],
    body: [
      "The static ranking has inverted the dynamic one twice. gcc emits **fewer** instructions than clang on p01 and executes **43% more**. The tuned safe rung is statically the *largest* cell in the p01 ladder while being within ~6 executed instructions of unsafe.",
      "Every static count on this site is paired with an executed-instruction count, and reported both raw and padding-excluded.",
    ],
  },
  {
    id: 5, title: "Executed instructions and wall clock can disagree in direction.",
    status: "standing", tags: ["method", "cost"],
    body: [
      "On p02, gcc executes 10% fewer instructions and runs 23% slower. On p07, disabling one LLVM pass on unchanged source gives **+10.07% instructions and −18.13% time**, and changing only the workload makes the same binary run **+7.84% more instructions in 71.75% less time**.",
      "Instruction count is the deterministic, noise-free metric and it is the headline here. It is not a proxy for time, and this site never presents it as one.",
    ],
  },
  {
    id: 6, title: "The only honest C-vs-Rust comparison is same-backend.",
    status: "standing", tags: ["method"],
    body: [
      "clang 22.1.6 is bit-for-bit the LLVM that rustc 1.97.1 ships. On p01's `large` input, C-clang and unsafe Rust execute **exactly 143,740,000** kernel instructions. The residual static gap is **+1 instruction**, padded and unpadded, from an induction-variable choice — not an ABI cost.",
      "The pilot's \"C beats Rust\" was a **gcc-only** measurement generalised to \"C\", and the sign was backwards. gcc stays on this site as the \"what a distro ships\" baseline; every C-vs-Rust claim carries the clang column.",
    ],
  },
  {
    id: 7, title: "Every rung is a spelling. The gap does not converge.",
    status: "corrected", tags: ["method"],
    body: [
      "An audit found **all three shipped safe-tuned rungs beaten**, each beater also cheaper than its own unsafe rung. The control that answered it — apply the same idiom to the *unsafe* rung — put unsafe back on top at +11.00 Ir/call flat. Then one more round on each side: replace the unsafe loop counter with the canonical C test `while rp < end`, and it becomes `nrow + 9`. **`O(1)` became `O(nrow)` and the sign of the conclusion flipped on the first thing a reader would try.**",
      "So the project ships a **named-spelling standard**: every pattern's hashed contract names the tokens each rung must spell literally, and a rung that deviates is a different benchmark. What the pin buys is **decidability, not attributability** — on p17 an excluded and an admissible spelling compile to the same 478 bytes.",
      "What that leaves is one quantity, stated exactly: `R3ship − R4ship` bounds `inf(in-contract R3) − R4ship`, and **only because R4 is held fixed by fiat rather than minimised**. It is not an upper bound on \"the safety tax\".",
    ],
  },
  {
    id: 8, title: "The unsafe rung is chained to the prover — so the safe class can reach spellings the unsafe class cannot.",
    status: "corrected", tags: ["proof", "method"],
    body: [
      "The published argument was that safe-beats-unsafe is impossible *by construction*, because every safe program is textually an admissible unsafe rung. **That is refuted**, and it is the most consequential correction in the project: every pattern pins `unsafe ≡ verus, byte-exact at O3`, so an unsafe rung is not a program that *may* use `unsafe` — it is a program that **must have a byte-identical twin that Verus verifies**.",
      "So R4 is bounded by what vstd can express and R3 is bounded by nothing. The classes are **incomparable, not nested**. Measured: p16's `chunks_exact(32)` fold is admissible as R3 at **zero** trusted lines and needs **five** new trusted items as R4. p11's `CStr` scan would be −35% of the kernel and is rejected with four `is not supported`. p03's one-line `assert!` is `panic is not supported` on the unsafe side.",
      "Practical rule that follows: run the prover on an unsafe-side variant **before** differencing it. That one check would have caught five published figures across two patterns.",
    ],
  },
  {
    id: 9, title: "Code layout moves wall clock by up to 27% at an unchanged instruction stream.",
    status: "standing", tags: ["method"],
    body: [
      "Two binaries from identical source, differing only in where the linker put the kernel — same instruction count, same normalised digest, same executed instructions — differ by up to **27% of wall clock**, and the difference can flip the sign of a rung-to-rung comparison.",
      "The mechanism is identified and static: either the loop body occupies one more **32-byte fetch window**, or a loop branch crosses a 32-byte boundary so the chunk is not cached (this box is Cascade Lake, carrying Intel's SKX102 JCC erratum). Both computable from the disassembly with **zero fitted parameters**, confirmed out of sample on 20 pre-registered layouts whose predictions were SHA-256'd before timing.",
      "It does not hit everything: real on p07 and p01, marginal on p08, **absent** on p02, p05, p16, p17 — the geometry flips on all seven, but only a front-end-bound loop pays for it. The methodological result outlives the finding: **interleave by cell, never by block, and measure the noise floor on byte-identical copies before believing any effect.**",
    ],
  },
  {
    id: 10, title: "Memory safety is not correctness — and most of these bugs are not memory-safety bugs.",
    status: "standing", tags: ["security"],
    body: [
      "p17 ships a program that Verus proves memory-safe on every access and that still reads a neighbouring window's bytes. p09 ships a one-character edit that no bounds check, no sanitizer, no Miri run and no memory-safety proof detects, at zero instruction cost. p04 drops a fullness check and overwrites the oldest element with no out-of-bounds access at all.",
      "The common shape: **memory safety is a property of addresses**. Where the attacker's harm can be expressed with in-bounds addresses, every tool in this study is silent — including the proof, when the proof's specification is memory safety alone. On p04 the memory-safety-only configuration is blind to *every* functional change, including reading the wrong cursor.",
      "The corpus has since added three harms that are not addresses at all, and the ladder does not order any of them: **p22** never returns (a full table makes the probe loop non-terminating — Miri and ASan silent, safe Rust's checks useless, because the missing guard is a fill count); **p47** leaks through timing, and there **safe Rust's `a == b` leaks where hardened C does not**; **p38**'s harm is the optimiser deleting a check the programmer wrote, which is the one class unsafe Rust does *not* reopen.",
      "The repair is not a better sanitizer. It is a **functional** specification — which is exactly the part of a proof that costs the most and that no compiler flag supplies.",
    ],
  },
  {
    id: 11, title: "Where safety does cost something, the price is usually the optimiser missing a fact the proof states.",
    status: "corrected", tags: ["cost", "proof"],
    body: [
      "p05: the dead panic survives because `nrow*ncol ≤ avail ⟹ i*ncol+j < avail` is **nonlinear** — the obligation R5 discharges with `lemma_mul_inequality`. p03 generalises it to a **linear** fact: hand LLVM the proof's own invariant as a dead clamp and the safe-vs-unsafe gap goes to exactly zero on both sides. p13 shows it from the other direction — there, the safety check *supplies* a bound the optimiser can see, and more than pays for itself.",
      "Two qualifications, both measured, both of which change what the claim says. It is **not Rust-specific**: clang keeps a manual C bounds check at exactly **4.00 instructions per executed pop**, gcc keeps it too at its own workload-varying rate, and given the identical clamp both delete 100% of it. And LLVM does eventually derive the fact — so this is analysis **seeding**, not an inability to prove the lemma.",
    ],
  },
  {
    id: 13, title: "The optimisation level can decide what the bug does.",
    status: "standing", tags: ["security", "method"],
    body: [
      "A handful of rung/input pairs across the corpus **do not behave the same way in every build** — the exact count is on the Hostile-input tab, where it is derived rather than typed. The sharpest is p38: one source file, one input — SIGSEGV at `-O3`, the correct answer at `-O0`, because the harm *is* an optimiser decision.",
      "So \"what the bug does\" is not a property of the program alone, and a report that names the outcome without naming the build is unsound. The gate now records one entry per distinct behaviour with the builds that produced it, and the outcome matrix marks those cells with a corner notch rather than averaging them away.",
    ],
  },
  {
    id: 14, title: "A sanitizer's vocabulary is not its coverage.",
    status: "standing", tags: ["security"],
    body: [
      "On p36 the harm is a **control transfer**: an out-of-table opcode loads a code pointer from past the table and the interpreter jumps to it. ASan and UBSan both fire — and both name the *array read*. gcc has no `-fsanitize=function`; clang's is defeated because the garbage is not a function, so the signature read faults first. Only `-fsanitize=cfi-icall` names the call, and it needs LTO and lld, so it cannot be a rung here.",
      "The distinction matters for how a tool result is read: on this pattern the checkers are blind in **vocabulary**, not in **coverage** — every input on which the call is wrong is one on which the array read is out of bounds, so the same input set fires them. A diagnostic that names the wrong operation still catches the bug; it just tells you the wrong thing about it.",
    ],
  },
  {
    id: 12, title: "Two measurement defects, found in passing, that invalidated published numbers.",
    status: "corrected", tags: ["method"],
    body: [
      "**(a)** The wall-clock column is a whole-process *level*, never a difference. The per-process constant — argv, file I/O, payload decode — is inside every published time, and on p09 it is 55% of `small` and 73% of `large`. A whole mechanism died on this: p09's \"the extra instructions retire cheaper than average\" came from an uncorrected 2–4× ratio, and corrected, the largest surviving factor is 1.5×.",
      "**(b)** A `forbidden` contract entry written without backticks was audited **zero** times while the verdict line two rows above still counted it. One pattern shipped 5 forbidden entries and 0 audited spellings, and its \"forbidden: 0 hits\" was kept by auditing nothing.",
      "Both were found by a *pattern* task, not by a tooling task — which is the argument for reviewing every delivery adversarially rather than trusting a green run.",
    ],
  },
  {
    id: 15, title: "Eight bug classes were probed and all eight refused — and three attempts to say why have now died.",
    status: "corrected", tags: ["method"],
    body: [
      "**The refusals are the durable part, and each was a measurement rather than an opinion.** Recursion depth: the three Rust rungs `call` the same merged symbol, so there is one rung, not three. Unaligned load: the cast and the `memcpy` spelling compile to identical kernels on both toolchains, and the harm is invisible without a sanitizer across 36 plain builds. `qsort` comparator: 80 builds and zero sanitizer reports, because this C library's `qsort` is mergesort plus heapsort and all its bounds are counts. Double fetch: the two loads are merged into one.",
      "⚠⚠ **What does NOT survive is every attempt to generalise from them.** The natural conclusion — that this instrument can only price a property some rung emits as a compare-and-branch — was published, reviewed, and **refuted on its own corpus**: p38 prices a *type-based* aliasing property at exactly 6.00 instructions per call, from five one-line fixes agreeing to the unit, **none of them a compare or a branch, and one of them a compiler flag**. Two more replacements were written and both died as well. **Three generalisations, three failures**, and the standing decision is to keep the eight refusals and publish no law over them.",
      "⚠ **The apparent unanimity is also weaker than it looks**, and the project says so against itself: all eight candidates were selected for *bug-class novelty*, which its own admission bar says predicts neither way. So \"two independent lists, both at a hit rate of zero\" is one list plus a differently-selected second list, and the zero is not evidence of structure.",
      "**One keeper did come out of it, on a different resource: a termination proof does not bound the stack.** A recursive kernel verifies `3 verified, 0 errors` with `decreases buf.len() - i`, and the compiled binary at depth 10⁶ prints `fatal runtime error: stack overflow`. The proof discharges exactly what it says and the program still dies — the same shape as the pattern where a proof certifies a leaking kernel, on a second resource. That limb was not attacked by the review.",
    ],
    caveat: "⚠ This entry is on the page in its corrected form. An earlier version of it stated the *“if and only if”* law as a standing result; the research marks that sentence **DISPUTED — do not quote** and preserves it only so the evidence against it can sit underneath. Read this as a record of eight refusals plus one keeper, not as a rule about what the instrument can price.",
  },
];

// ------------------------------------------------------------ retractions --

const RETRACTED = [
  ["\"Safe Rust pays an O(n) bounds-check tax\" (p02)", "The indexed fold's bounds checks cost zero. The whole delta was one spelling of an overflow check defeating LLVM's `memcpy` idiom recognition. Restated as a codegen-fragility finding: one spelling loses the idiom, three others are +10 flat."],
  ["\"C beats Rust\" (pilot)", "A gcc-only measurement generalised to \"C\", with the sign backwards. gcc emits fewer instructions and runs 43% slower. The clang result was never affected."],
  ["\"p16 is the first true O(n) safety cost\"", "Written from an engineer's report without re-measuring. R3's per-byte rate equals R4's exactly, so the O(n) cost belongs to one spelling, not to safety."],
  ["\"gcc is 36% behind clang on p16\"", "A flag default, not a codegen limit. With `-funroll-loops` gcc reaches 2823 and beats clang's 2993. Reproduced on p17."],
  ["\"On a vectorised loop the bounds check costs 0.0000 Ir/element\" and \"wider lanes make safety cheaper\" (p05)", "The first is true only of the vector steady state; the check is hoisted into a per-row trip-count computation and survives in the scalar epilogue. The second is refuted: at AVX2 the gap is 4.58× against SSE2's 1.42×."],
  ["\"inf(R4) ≤ inf(R3) by construction\"", "Offered as a reason available without measuring, and carried in three files for six patterns. The identity pin chains every unsafe rung to the prover, so the classes are incomparable, not nested. See finding 8."],
  ["\"Compare idiom-matched rungs\"", "Retracted one turn after being invented. \"Same idiom\" has no fixed point; its members differ by O(nrow)."],
  ["\"p17's leak is an information disclosure\"", "As shipped it is not — the excess bytes are the attacker's own request table. Corrected to a slice-relative guard, which does disclose a neighbour window."],
  ["\"Overlap UB is not caught by ASan\"", "It is caught, exact to the byte — unless the call site is fortified to `__memcpy_chk`, which blinds ASan under clang as well as gcc. A gate row records `clean` for both reasons identically."],
  ["\"The bug is not expressible at R5\" (p08's own README)", "It is, and it verifies clean. A proof that a `requires` holds is not a proof that the trusted body honours it."],
  ["\"p17's R3 costs +32 Ir/call, flat\"", "Flat per byte, not per call. Both published bands happened to have the same suffix count; swept, the difference runs 18…63. The pattern ships no sweep inputs, which is how a two-point constant became a law."],
  ["\"p16's R3 cost is O(1) per call\"", "`7 + 5·nrec` or `7 + 7·nrec` depending on residue — O(nrec). The two published points were nrec 4 and 10."],
];

// ---------------------------------------------------------- recurring traps --

const TRAPS = [
  ["A green gate is evidence about the gate.", "Reviews have repeatedly found real defects past a fully green run — twice with an unchanged contract hash. One review forked a pattern with a **forbidden** rung and got a complete green run, `failures: []`, and a byte-identical contract hash."],
  ["A vacuous truth in a log reads like a discharged obligation.", "Six instances of \"every X is Y\" printed over an empty collection. Now a rule: a count-bearing success line prints its `n`, and `n == 0` fails."],
  ["Checks fail open.", "Three times a malformed mutant that failed to *compile* was read as \"the check passed\"."],
  ["Declared pins are self-certifying.", "They move in the same commit as the code they constrain. Derive where possible; the Miri cross-check and the \"did this code actually run\" callgrind check are the models."],
  ["Residues bite at whatever width the codegen chose.", "p01 mod 4, p02 mod 16, p16 mod 4, p05 mod 8 with residue 0 the outlier — so every power-of-two dimension pays a full extra vector iteration. **The size a benchmark author reaches for first is the trap.** Sweep two full cycles; never sample two points."],
  ["Attribute nothing without decomposing.", "Change one loop at a time. This is what killed the O(n) claim."],
  ["You are measuring a spelling until you have written two — and then you are still measuring a spelling.", "Three retractions came from one plausible safe rung published as what *safe Rust* costs. Writing a second spelling does not fix it: on p05 the spread across eleven exceeds the safe-vs-unsafe gap."],
  ["A tool that reports nothing may be a tool that cannot see.", "ASan is silent on p08's overlap not because there is none but because fortify rewrote the call. The record says `clean` for both reasons identically."],
  ["A cited artefact can refute the claim it is cited for.", "One committed probe, named as the evidence for an identity claim, prints `identical=False` when re-run. The claim happens to be true — a reviewer re-derived it — but nobody would have known which. **Re-run the artefact, do not cite it.**"],
  ["Ask to be corrected, not obeyed.", "Every agent that has contradicted the research manager with a measurement has been right — 55 times at last count. The highest-yield sentence in the project's history is some version of \"I think X; prove me wrong.\""],
];

// ----------------------------------------------------------------- method --

const METHOD = [
  {
    h: "What one cell is",
    p: [
      "One pattern × one rung × one optimisation level × one inline mode. All data and all loop bounds come from a file named in `argv`, so nothing can be partially evaluated to its answer, and every kernel return is folded into a checksum that is printed — so nothing can be optimised away either.",
      "**Isolated** builds keep the kernel in its own translation unit, `#[inline(never)]` / `-fno-inline`, no LTO: that is the cell whose assembly is read. **Whole-program** builds turn inlining and LTO on: that is what a real program gets. Both are measured, and on several patterns they disagree about the sign of a comparison — which is itself reported rather than resolved by picking one.",
    ],
  },
  {
    h: "The primary metric, and why",
    p: [
      "**Executed instructions (`Ir`), counted by callgrind.** Deterministic, immune to a noisy neighbour, reproducible across runs. Hardware counters are unavailable on this box (`perf_event_paranoid=3`, no root), so IPC and cache-miss data do not exist here — with one exception: branch simulation *is* available through callgrind and was used on p07.",
      "Two columns are reported and they are **not interchangeable**. *Kernel-exclusive Ir per call* counts instructions inside the kernel symbol — right only when every rung does its own work inside its own symbol, and wrong on p11 and p08, where it reverses real rung comparisons. *Marginal Ir per call* is a whole-program slope and therefore symbol-independent — but it does not cancel the environment on p03, p04 and p08, where a stack or heap alignment term moves it by up to ±7. **Each pattern states which column its numbers are in**; that is the `convention` line on every pattern page.",
    ],
  },
  {
    h: "Wall clock is a sanity check, never the headline",
    p: [
      "`taskset`-pinned to one core, ≥30 reps, interleaved **by cell** (never in blocks — blocked round-robin manufactured an entire published effect on p05), min and median reported with the spread. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised.",
      "Times include process start-up and reading the input file, so **a time is a level, not a difference** — subtract a one-iteration run before quoting any ratio. On one pattern the per-process constant is 73% of the published number.",
      "And the deeper reason, which is not about this box's noise: **the same machine code has no single wall-clock cost.** The committed layout control builds one pattern's rungs many ways from identical source and times each; every rung-to-rung comparison it produces **changes sign** depending on which build you got. That is charted, with the data, at the foot of **Cost of safety** — and it is why wall clock appears here per pattern, as a sanity check, and never as a cross-pattern headline.",
    ],
  },
  {
    h: "What the gate checks before a number is believed",
    p: [
      "`harness/check.py <pattern>` runs every stage: all cells build and agree with an independent Python model on every input; the contract's declared obligations match the Verus source; the proof's domain covers the measured domain (an early pilot published a run that falsified its own postcondition, because `main` was trusted and no call site ever had to satisfy the precondition); each trusted `requires` is tested for tautology and each `ensures` for load-bearingness by deletion; a verified twin re-derives each trusted item; Miri runs wherever there is a trusted item; ASan/UBSan run on the adversarial inputs; and the kernel is checked not to have collapsed to a constant.",
      "**And a green gate is evidence about the gate.** Every pattern here was reviewed adversarially by a second agent after passing, and every review found real defects — including in tooling written one task earlier.",
    ],
  },
  {
    h: "What this benchmark cannot tell you",
    p: [
      "**It cannot tell you what safe Rust costs.** It can tell you what one *declared spelling* of a safe kernel costs against one declared spelling of an unsafe kernel, on this machine, with these compilers. Every attempt here to publish a class minimum has been refuted by the next lever pulled.",
      "**It cannot rank languages.** Half the C-vs-Rust deltas measured here are backend differences (gcc vs LLVM) or library differences (glibc's IFUNC `strlen`, `memcpy`-is-`memmove`), and on p13 a single `-fno-builtin` flag flips the sign of every same-backend row.",
      "**It cannot tell you a program is correct.** The proofs here are memory-safety proofs unless a pattern says otherwise, and several patterns ship bugs that a memory-safety proof provably cannot see — an in-bounds overwrite, a one-character index that verifies clean, a non-terminating probe loop and a timing leak among them.",
      "**It cannot claim both endpoints were searched equally hard.** Both sides were searched on only about a third of the rows; most declare a search on one side, and three declare none on either. Several of those searches, once run, moved a published number or flipped its sign — so a bar's size is partly a fact about how much effort went into the two programs behind it. The per-row search state is on the Cost tab.",
      "**It cannot generalise off this machine.** One CPU, one C library, one Verus build, one instruction set. The layout finding in particular is tied to this processor's instruction-fetch behaviour, and every claim about what the prover will and will not accept is a claim about one pinned version of it.",
      "**It cannot tell you what happens when your build inlines the kernel.** These numbers are from builds that deliberately keep the kernel as its own function so it can be measured. In the whole-program builds the kernel usually vanishes into its caller entirely — leaving no symbol to count — which is what a real build would do.",
    ],
  },
];

// Short labels for chart rows — long titles truncate mid-word and read badly in
// a 148px gutter.  A pattern with no entry falls back to its directory name.
const SHORT = {
  "p01-array-sum": "array sum",
  "p02-buffer-copy": "buffer copy",
  "p03-bounded-stack": "bounded stack",
  "p04-ring-buffer": "ring buffer",
  "p05-index-flatten": "index flatten",
  "p06-rotate": "in-place rotate",
  "p07-binary-search": "binary search",
  "p08-overlap-move": "overlap move",
  "p09-bitset": "bitset probe",
  "p11-nul-scan": "NUL scan",
  "p12-strcat-fixed": "strcat fixed",
  "p13-strncpy-trunc": "strncpy trunc",
  "p14-field-split": "field split",
  "p10-fir-stencil": "FIR stencil",
  "p19-state-machine": "state machine",
  "p22-hash-probe": "hash probe",
  "p27-handle-table": "handle table",
  "p36-vtable-dispatch": "vtable dispatch",
  "p38-alias-pun": "alias pun",
  "p47-ct-compare": "ct compare",
  "p46-bignum-mac": "bignum MAC",
  "p23-partition": "Hoare partition",
  "p25-realloc-growth": "realloc growth",
  "p28-intrusive-lists": "intrusive lists",
  "p29-bst-delete": "BST delete",
  "p32-free-list-pool": "free-list pool",
  "p34-refcount-stack": "refcount stack",
  "p35-tagged-union": "tagged union",
  "p49-interned-pool": "interned pool",
  "p42-goto-cleanup": "goto cleanup",
  "p16-tlv-walk": "TLV walk",
  "p17-http-range": "HTTP range",
  "p18-varint-shift": "varint shift",
};

// Why the precondition is the same clause on nearly every pattern, and why
// that is the point rather than a weakness. Sourced from the kernels' own
// headers (p03's verus.rs states it at length) and `.memory/02-bench-rules.md`.
// The measurements that back it are derived in index.js from `proof_domain`.
const CONTRACT = {
  requires: "**Structural, not semantic** — it is about the *shape* of the buffer the driver built, never about its contents. The driver reads the file, then calls the kernel with a window it computed itself, so this is the driver's own arithmetic and it discharges it. Nearly every pattern carries the same clause because it is the harness's calling convention, not the pattern's subject.",
  ensures: "**This is where the content is.** The precondition is shared; the postcondition is the pattern — it names the exact function the kernel must compute, and it is checked against an independent reference implementation rather than against the kernel's own idea of itself.",
  domain: "That is the test that matters. **Everything an attacker controls lives inside the window** — the declared lengths, the counts, the indices, every byte — and none of it is assumed. A precondition about *contents* (“the length field is honest”, “the opcode stream is balanced”) would be a different thing entirely: no honest loader could discharge it, and it would quietly place exactly the malformed inputs this project exists to run **outside** the proof, leaving a green result that means nothing. The obligation to reject bad contents stays where it belongs — inside the kernel, in code that has to be proved.",
};

// Provenance of the four cross-cutting results. Every word here is the
// research synthesis's own account of its out-of-sample test (§0); the counts
// are derived in index.js. This is disclosed rather than smoothed over because
// "derived on a smaller set, then re-tested on all of it" is a stronger claim
// than "derived on all of it", and reads weaker.
const PROVENANCE = {
  body: [
    "The four cross-cutting results were worked out on the patterns that existed at the time. Seven more were built afterwards — the pointer-and-lifetime ones, which are the hardest cases — and for a long stretch they were folded into no result at all.",
    "Every result was then **re-derived against the whole corpus**, and the verdicts published. That is an out-of-sample test, and it is worth more than deriving on everything at once would have been: the seven late patterns had no chance to shape the conclusions they were then used to check.",
  ],
  // ⚠ These land in a dataTable, which renders cells RAW. No markdown here.
  verdicts: [
    ["The safety tax belongs to a pair of spellings", "Survives. Three numbers move, and it gains a structural caveat larger than the numbers."],
    ["Where safe Rust does not help", "Survives, and it is the one that grows — the temporal cases went from one to six, and the six disagree with each other."],
    ["A proof discharges exactly what it says", "Survives — but NOT strengthened. The fit appears to improve only because the range widened, and the seven new patterns are the worst-fitting in the corpus."],
    ["What this instrument can price", "Scope only. The one cost law it proposed is still a ONE-ROW law: the pattern that should have corroborated it does not."],
  ],
  warnHead: "Nothing fell, and the research says that is less reassuring than it reads",
  warn: [
    "The synthesis makes this point against itself, and it is the right instinct: a set of results that survives every test may be a set of results that is not sharp enough to fail one. The only other out-of-sample test this project ran did fail once.",
    "There is a second limitation the count does not show. The corpus was assembled under a rule for admitting patterns that the project has **since withdrawn** — the original bar was measuring the wrong thing, and re-adjudication under the replacement admitted seven rows and left no refusals standing. So this is not a random sample of C bugs, and no claim here should be read as a frequency claim about real code.",
  ],
};

// The spelling search: the qualification that decides whether a safe-vs-unsafe
// bar is a safety cost or an artefact of which two programs were chosen.
const SEARCH = {
  body: [
    "Every bar on this page compares **two specific programs**, not two languages. If a cheaper way of writing either one exists and was not found, the bar is too big or too small by however much that cheaper version would have saved — and nothing in the measurement can tell you which.",
    "So each pattern records how hard both sides were searched, and the answers are not uniform: some were searched on both sides and moved, some were searched on one, and some carry an explicit **owed**. Several rows below record the sign of the comparison **flipping** once the unsafe side was searched, which is the clearest possible statement of why this column is not \"the cost of safety\".",
    "This is the project's own text, unedited. Read the row before quoting its bar.",
  ],
};

// The honest reading of the all-green Rust columns. This was the site's
// weakest disclosure: it implied better adversarial inputs would strengthen the
// matrix, when the research tested that and found the opposite.
const MATRIX = {
  green: "It says these cells matched the reference implementation on the inputs this project **built** — and on this corpus no input could do otherwise. Across every pattern and every adversarial input, the four Rust rungs have **never once disagreed with each other**, and tens of thousands of additional fuzzed inputs produced no Rust-rung split either. That is a property of how these kernels are specified — the precondition bounds a *length* and never mentions the contents — so **more adversarial inputs is not the fix; there is nothing here for them to be adversarial to.** Read the green as \"the bug being modelled is a C-side bug\", not as a robustness result.",
  zerocall: "⚠ **And a quarter of the adversarial inputs never reach the kernel at all.** 43 of 186 make zero kernel calls on 30 of the 33 patterns: the shared driver rejects the malformed file before the kernel runs, and every rung then agrees trivially. Those rows are green because nothing happened, and the project names this as a real weakness — input templates copied forward without being re-aimed at the pattern they were copied into.",
};

// Why "the proof is free" needs two sentences, not one. The zero is a rule the
// gate enforces, and the rule itself costs something — in the rungs it then
// forbids you to write. Both halves are measured; the site headlined only one.
const PROOFCOST = {
  head: "That zero is a rule, not a discovery — and the rule has its own price",
  body: [
    "A pattern's numbers do not count here unless the proved version and the unsafe version compile to **the same machine code**. So the proof costing zero instructions is something this project *required* and then checked, not something it went looking for and found.",
    "⚠ **And the rule is not free, because it decides which unsafe programs you are allowed to write.** The unsafe rung must have a proved twin, so it is bounded by what the prover's library can express — while the safe rung is bounded by nothing. Measured, that has cost real speed: one pattern's fastest unsafe spelling is **35% cheaper** and is refused because the prover does not support the calls it makes; another pays exactly **3 instructions per dispatch** for a signature the prover cannot type at all.",
    "So the honest form of \"what does a proof cost\" is **two numbers, not one**: zero for the proof itself, and whatever the rule costs you in the rung you are then permitted to ship.",
  ],
};

// What the proof-goal count does and does not tell you. The site headlined it
// without a unit and without the caveat the research attaches to it.
const GOALS = {
  head: "What that count does not tell you",
  body: [
    "A proof goal is a small check the prover discharges on its own — *this index is inside the array*, *this loop terminates*, *this addition does not overflow*. More of them means a bigger kernel, not a stronger guarantee.",
    "⚠ **Measured, this count tracks the size of the code, not what the proof covers**: across the corpus it correlates 0.92 with syntactic size. It moves when you split a function and does not move when you delete a clause you needed. On one pattern the entire ledger clause can be removed and the count is unchanged; on another, a kernel that leaks memory verifies at exactly the same number as one that does not.",
    "**So read it as scale, and read the trusted base as the price.** The thing that actually catches a missing clause is not this number — it is the deletion probes and the pinned contract text described below.",
  ],
};

// Which patterns were built, and who decided. The site had no answer to this
// on any tab; the research tree's answer is unflattering and is used verbatim.
const SELECTION = {
  lede: "The rest were refused, each on a stated reason — usually that the bug class turned out to duplicate one already built, or that it left no run-time check for this instrument to price. **This is not a random sample of C bugs, and nothing here is a claim about how often any of them occurs in real code.**",
  body: [
    "⚠ **The rule used to admit patterns was itself withdrawn part-way through.** The original bar was measuring the wrong thing; when it was replaced and every earlier refusal re-adjudicated under the new one, **seven previously refused rows were admitted and none of the refusals survived unchanged**. So the corpus was assembled partly under a standard the project no longer stands behind, and the composition is the part of this work that would move most if it were done again.",
    "The replacement bar is about **mechanism** rather than bug class: a candidate earns a place if it brings a new operator on the safety line, a new source of the bound, or a new reason the compiler does or does not remove the check. “Another out-of-range index” is not the question; “another comparison in the same place for the same reason” is.",
    "The build programme is now closed — every admitted candidate is either built or refused on the grounds that its C side duplicates one already here.",
    "⚠ **One measured coverage gap is worth stating plainly**, because it is the kind a reader cannot see: every kernel here reaches memory by **indexing**. None walks memory with a moving pointer — 0 of 464 bound sites across all 33 — while a survey of nearly a million lines of real C found pointer-walking in **all 22 programs examined**, typically the second or third most common form. Whatever this corpus says, it says about indexed code.",
  ],
};

// The licence: whether a rung-to-rung difference may be taken at all. This is
// the most important qualification on the cost view, and the page drew those
// differences for a long time without it. Counts and row lists are derived in
// index.js from the verdicts `synthesis/` publishes; the explanation is here.
const LICENCE = {
  body: [
    "The cost column on this page counts instructions **inside the kernel function** and nothing it calls out to. That is what makes the number comparable at all — it excludes the driver, the file reading and the process start-up that would otherwise swamp it.",
    "It also means two rungs may only be subtracted when they hand the same work to the **outside**. If one rung calls the C library's `memcpy` and the other writes its own loop, the difference between their kernel columns is not a safety cost — it is the cost of the work one of them moved somewhere this column cannot see. The research checks this per row, from the disassembly, and publishes a verdict.",
    "**A row that is not licensed is not a small caveat: its difference is known to be wrong.** Those rows are marked `‡` in the chart above and listed below. They are shown rather than deleted, because the measurement is real and the pattern's own page explains what it means — but no unlicensed row should ever be quoted as the price of safety.",
  ],
  cnote: "⚠ **The research does not publish a verdict for this pair**, so this page applies the same rule to the same disassembly and reports the result here. It matters: the C-against-hardened-C chart is the cleanest comparison on the site — one source, one compiler, one added check — and it was the only one with no licence check on it. On one pattern the unfixed rung calls the C library's `memcmp` while the fixed rung compares inline, so the largest bar on that chart was a library call leaving the measured function, not the price of a check.",
  foot: "`UNDEC` means the check could not be run at all, because both rungs dispatch through a pointer the disassembler cannot resolve. That is a limit of the instrument, not a verdict about the code — and it is counted here as unlicensed rather than assumed fine.",
  missing: "This page could not read the licence verdicts out of the research synthesis, so it cannot tell you which of the differences above are permitted. **Treat every one of them as unverified** until this is fixed — a missing check must never be read as a passed one. The build prints the same warning.",
};

// The idiom contract. Every claim here is the harness's own account of what
// each bucket means (`harness/check.py::_idiom_audit`'s docstring), not an
// inference from the counts — the distinction matters because two of the four
// buckets are NORMALLY non-zero and reading them as defects would be wrong.
const IDIOM = {
  lede: "Every rung is a *spelling*, and the wrong pairing flips the sign of the answer — so each pattern declares the tokens its rungs must and must not use, and that declaration is hashed into the gate record along with the sources. The gate then checks each spelling against each rung. These are the corpus-wide results.",
  detail: "Only `hits` is a defect — a rung containing something this pattern forbade. `forbidden_unaudited` is a declaration with nothing quoted in it, so the gate could not check it and a reader has to. `pins_nothing` is a bug in the ruler rather than in the code. `absent` is usually deliberate: several entries exist precisely to record that a token is **missing** from the unhardened rung.",
  readHead: "How to read these four, because two of them are normally non-zero",
  read: [
    "**Forbidden spellings found is the one that must be zero**, and is. A hit means a rung contains something its own pattern ruled out — the comparison is not the comparison it claims to be.",
    "**Declared but never checked is the honest gap.** A `forbidden` entry written as prose, with no quoted spelling in it, gives the audit nothing to search for. It is recorded as a declaration and it constrains nothing mechanically; only a reader enforces it.",
    "**Pins nothing** means a required spelling appears in no rung of a language that names it — a defect in the ruler rather than in the code, and the bucket that caught two real declaration bugs when it was introduced. **Scoped-absent** means the spelling is present in some rungs of that language and not others, which is usually deliberate: the point of several entries is that a token is *missing* from the unhardened rung. A non-zero count in either is normal here; **what is worth reading is a change in it.**",
    "And the audit reports *presence*, not correctness. Where an entry says “written `%` and not `&`”, a naive presence check counts the wrong rungs as matching — the harness documents nine such cases and reports the two shapes separately so the reader judges each against the entry beside it.",
  ],
};

// The code-layout control's prose.  The numbers around it — how many builds,
// how many instructions, how wide the band, which comparisons change sign — are
// all derived in build_data.py and composed in index.js, so nothing here can go
// stale against the data.  What is here is the part no measurement supplies:
// what the control means and why the whole site is arranged around it.
const LAYOUT = {
  lede: "from identical source. Within a rung every build has the same instruction stream and the same executed instruction count. **Only the address moves.**",
  chartTitle: "What one wall-clock comparison would have told you, depending on which build you got",
  chartSub: "Each row is a rung-to-rung difference in wall clock, as a percentage of the second rung. The band is the range across every layout; each tick is one build. The line down the middle is zero.",
  foot: "A control, not part of the gate — it is the reproduction path for the layout finding, and it is hashed into every pattern's `source_sha256` so that it cannot change without the record noticing.",
  flip: "Pick one build and you get a number; pick another and you get the opposite conclusion, with nothing in the source to tell them apart. **This is why every headline on this site is an executed-instruction count** — deterministic on this box — and why wall clock appears only per pattern, only as a sanity check, and never as a ratio.",
  withheld: "This chart's entire claim is that the machine code did not change, only its address. The control's builds no longer agree on their normalised machine code, so that premise does not hold and these times are not comparable. Rebuild the control before believing anything here.",
};

const INTRO = {
  lede: "\"C is fast, Rust is safe\" is most of what gets said about memory safety, and it settles nothing — because C is fast **precisely in that it skipped the check**. Comparing the two languages compares two different programs. To learn what safety costs you have to hold the program fixed and vary only the mechanism that enforces it.",

  // The motivating argument.  No figures: every number on this site is one tab away,
  // and a front page that opens with statistics answers a question nobody asked yet.
  problem: [
    "So that is what this is. A catalogue of memory-safety bugs as they are actually written in C — a length read off the wire, a validated index used later without re-checking, an overlapping copy, a suffix range with one missing comparison — each one rebuilt at every rung of a ladder that runs from unchecked C to unsafe Rust with a machine-checked proof.",
    "Every rung solves the *same* problem, against the same driver, the same input files and the same harness, and is compared at the level of executed instructions rather than wall clock alone. What changes between one rung and the next is only who enforces the check: nobody, the programmer, the language, or a solver.",
  ],

  // Deliberately three claims about METHOD and STAKES, not three results.
  points: [
    ["Safety is not one bit.",
     "Six rungs, and each buys something different. Between \"C\" and \"proved safe\" sit a hand-written check you have to remember everywhere, two spellings of safe Rust that differ by more than safety does, and unsafe Rust — which is **permission**, not a guarantee."],
    ["A comparison is only as honest as its weaker-searched side.",
     "Every rung is a **spelling** — one of many ways to write the same program with the same guarantee — and the wrong pairing flips the sign of the answer. That has happened here, in the flattering direction, seven times. So each pattern pins the tokens every rung must use in a hashed contract, and every published cost carries a statement of how hard each side was searched — including the rows that say plainly that one side, or neither, was searched at all."],
    ["Memory safety is not the property most of these bugs violate.",
     "Some of these patterns ship a program that a prover certifies memory-safe on every access and that still returns the wrong answer, or reads a neighbour's bytes, or never terminates. The repair is a **functional specification** — the expensive half of a proof, and the half no compiler flag supplies."],
  ],

  // Pointers, not previews.  Each is a tab id from TABS.
  next: [
    ["cost", "Cost of safety", "What the check costs per call, per byte and per rung — and how much of the gap is spelling rather than safety."],
    ["security", "Hostile input", "What each rung actually does when the malformed file arrives: caught, crashed, or silently wrong."],
    ["proof", "Proof & trusted base", "What the proof discharges, what it still trusts, and how many lines of that trusted base you have to read."],
    ["patterns", "Patterns", "Every pattern's own numbers, contract, sources and gate record."],
    ["findings", "Findings", "The cross-cutting results — including the ones this project has had to retract."],
  ],
};
