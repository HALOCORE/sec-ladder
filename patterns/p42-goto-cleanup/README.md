# p42 — `goto cleanup` error handling: a leak on the error path

**The 26th pattern.** The kernel takes a heap digest buffer sized from the
window, then validates the record's tag. A malformed tag is an error and the
kernel returns 0 — and the C rung leaves without joining its own cleanup chain.

```c
    dig = (uint8_t *)malloc(len);
    if (dig == NULL)          goto cleanup;
    if ((v[off] & 0xffu) != P42_TAG)
        return 0;             /* THE BUG: leaves without joining the chain */
    ...
cleanup:
    free(dig);
    return acc;
```

`c/kernel_hardened.c` is that file with `return 0;` replaced by `goto cleanup;`,
and it returns the same value on that path. Nothing else differs.

## Why this row exists

**The bug class is absent from the built tree.** A 25-pattern census of
`.memory/06-catalogue.md`'s own bug-class column finds **zero leak rows**;
`p27` is the only other temporal pattern and it is built *not* to leak **by
contract** — its `spec.md` forbids `ManuallyDrop`, `mem::forget`, `Box::leak`
and `Box::into_raw` and says the epilogue frees every record still alive. **p42
adds exactly the path p27 forbids itself.**

**The rung boundary is real and it is where the release comes from.** R2 and R3
own a `Vec`; the compiler emits its `Drop` glue on every path out of the
function, early return included, and there is no second spelling to get wrong.
R1 and R4 write the release by hand, twice, once per exit. **R1 gets one of them
wrong. R4 does not — because the author checked, and nothing else did. R5 is the
same machine code with a proof that checks it**, which is the row's point and,
since TASK_110, the row's headline.

**Precedent, fetched and quoted.** Linux `505d9dcb0f7d`, *"crypto: ccp - fix
resource leaks in `ccp_run_aes_gcm_cmd()`"* — `goto e_ctx` where `goto e_aad`
was needed, skipping the AAD work area's release. **CVE-2021-3764**, CVSS 5.5.
The generic form is SEI CERT **MEM12-C**.

## The results, in one screen

| | |
|---|---|
| gate | **0 failures**, 32 cells × 12 inputs, `contract_sha256` in `NOTES.md` 0. ⚠ The VERDICT STRING is `PASS` or `PASS-WITH-BLOCKED-ROWS` depending on whether Miri finishes `large.bin` inside `check.py`'s 180 s `MIRI_TIMEOUT` — a run-dependent fact this file deliberately does not transcribe (`.tasks/PROTOCOL.md` rule 6). `spec.md`'s `miri.blocked_reason` declares that row, and a timeout is recorded as BLOCKED, never as a failure |
| Verus | **18 verified, 0 errors**; twin **21/0**; hand-written axioms **0** |
| TCB | 5 `external_body` items, **3** trusted by `_is_trusted`, each with a verified twin. **The ghost ledger adds none — and, since TASK_118, buys none** |
| identity | `unsafe ≡ verus` **exact** at `-O3` (`md5_fn 28432cb84883`, 128 insns), **`norel`** at `-O0` |
| **R1 − R1h** | **`+0.00` / `+0.00` on gcc** — the leak is free on the success path, exactly. **`−4.00` / `−5.00` on clang**, and there the variable is the window's **PARITY**, not its size: four terms, isolated per instruction, none of them about memory safety (`NOTES.md` 5) |
| R3 − R4 | **`+12.00` / `+11.00`** `Ir`/call. ⚠ **The sign flipped at TASK_110** and the R3/R4 spans **overlap at both ends**, so p42 publishes two spans and one bounded quantity between two named cells — **not** "safe beats unsafe" and **not** its mirror (`NOTES.md` 11b) |
| R2 − R4 | +599.00 / +25092.00 |
| leak, detected | LSan at the gate's own stage-7 flags, **no hook**: the three erroring inputs report **exactly `n_err × win_len` bytes** — `model.py::leak_bytes` derives it from the file, so it is an invariant and not a transcript — at `-O0`…`-O3`, **352 control points**, hardened rung silent at all of them |
| Miri | seeds **0..7**, nine small inputs, no UB and no leak; `large.bin` exceeds the 180 s budget under interpretation; **the deleted-`dig_free` positive control fires** |

*(`Ir` figures are kernel-exclusive, `-O3`, inline mode `isolated`, from
`results/p42-goto-cleanup.json`. Section 5 of `NOTES.md` has the full table and
the two conventions.)*

### ⚠⚠⚠ THE HEADLINE OF THIS ROW HAS NOW BEEN RETRACTED TWICE, IN OPPOSITE DIRECTIONS. THIS IS THE THIRD VERSION AND IT IS AN OPEN QUESTION.

> **p42's R5 does NOT cover p42's own bug class.** Three encodings have been
> built to make Verus state *"this allocation is released on every path"*, and
> **all three admit a program that verifies and leaks**:
>
> | encoding | verdict | the leaker | measured on p42's kernel? |
> |---|---|---|---|
> | bare `Tracked<Dealloc>` | affine — a proof may just drop it | `controls/affine_leak.rs`, `2 verified, 0 errors` | no — a standalone 64-byte probe |
> | ghost ledger (**shipped**) | `18 verified, 0 errors` | `proof { let tracked _dl = led.tracked_remove(0int); }` | **yes** |
> | privacy-scoped ledger (TASK_118, **not shipped**) | `19 verified, 0 errors` | escrow into a ledger the body mints for itself | **yes** |
>
> ⚠ **The last two are measured on this pattern's own kernel and the first is
> not**, which is why the column is there. **Each of the two leaks exactly
> `n_err × win_len`** — `model.py::leak_bytes`, 256 / 624 / 0 / 16 on the four
> inputs measured — and each compiles at `-O3` to `md5_fn d3f1194c…`,
> **byte-identical to R4 with p42's bug planted in it**. ⚠ **Whether some OTHER
> encoding could state leak-freedom at this pin is OPEN.** Three failures are
> not an impossibility proof, and *"Verus cannot state leak-freedom"* has
> already been retracted once.

⚠⚠ **The two retractions, because the shape of the mistake is the durable
part.** (1) This README used to head that box *"Verus at the pinned version
cannot state 'this allocation is released on every path'"* — struck at TASK_110,
because what was measured was that ONE encoding fails and what was published was
that the property is unstateable. (2) The replacement — *"the natural encoding
cannot state leak-freedom; escrowing the token can … a proof cannot drop a MAP
whose contents a postcondition names"* — is **struck at TASK_118**, because a
proof can: `TASK_116` found the one-line leaker and `TASK_118` reproduced it and
killed a third encoding. **Both retractions are the same generalisation error
with the sign flipped**, and the counterexample to the second was sitting in
this pattern's own `NOTES.md`, one paragraph below the claim, for six tasks
(`NOTES.md` 6c).

**What p42 does price, and this part is unchanged and was never wrong:** a
ledger obligation costs **0 `Ir`, 0 trusted items, +3 verification conditions**.
**The price is right; the product is nothing.** What the obligation certifies is
that the author wrote *something* on every exit that empties a map the author
controls — a named, greppable discipline for a reader, not a guarantee from the
verifier. **`controls/ledger_leak.py` runs five arms**: two deleted releases
that Verus rejects **and two attacks that it accepts**, pinned so the hole
cannot rot back into a claim.

**The residual trust, and it is three routes rather than the one this README
used to name:** acquire outside the wrapper (`vstd::raw_ptr::allocate`,
`dig_alloc`); acquire through the wrapper and then empty the ledger without
freeing; or acquire into a ledger of your own. **Privacy can make a ledger's
contents unforgeable — rustc rejects the forgery — and it cannot make the ledger
unique.** A clean negative beside it: **there is no linear
must-consume tracked mode at the pinned Verus** (22 `verifier::` attribute names
in the pinned binary, the only `linear` among them being `nonlinear`;
`grep -rn affine vstd/` → 0 hits; widened at TASK_116 to the whole attribute
enumeration, vstd and `std_specs/`), so nobody need re-run that search — **but
it is an absence argument and not a proof.** `p27`'s `Tracked<Dealloc>` makes a
deallocation *legal*; nothing makes it *happen*, and p27's leak-freedom rests on
a spelling pin rather than on its proof — **that part stands, and p42 is now the
same kind of claim rather than a different one.** On **both** rungs what stands
behind leak-freedom is **Miri plus the `identity` pin**, which is why
`miri.required` is `true` and why the control that deletes `dig_free` is
shipped. ⚠ **The pin protected the pattern; the proof did not.**

### ⚠ And a per-element rate would have been wrong

`controls/sweep.py` fits `Ir/call = a + b·win_len` on windows 64..79 and
predicts windows 512..527. **Every rung's out-of-band residual is 2.8× to 33×
its in-sample residual**, and `unsafe` — now the cheapest rung, the one a
headline would quote — mispredicts its own shipped `large.bin` by
**−2462 `Ir`/call** off an in-sample residual of 11.69. So **p42 publishes two
measured points per rung and no rate** (`NOTES.md` 11d). One candidate mechanism
— the allocator's size class — is **refuted by isolation**; the real one is
**OPEN** (`NOTES.md` 11e).

## What is in this directory

| path | what it is |
|---|---|
| `spec.md` | the kernel contract and the hashed pin block. Its `forbidden` list carries the CONDITIONS of p42's claim — heap not stack, a real `free` not a freelist, an error path a committed input reaches, and no measured input that reaches it |
| `model.py` | the independent reference. Two implementations; `sanitizer_expect` and `leak_bytes` are **derived**, not declared |
| `c/kernel.c`, `c/kernel_hardened.c` | R1 and R1h, one statement apart |
| `safe_naive.rs`, `safe_tuned.rs`, `unsafe.rs`, `verus.rs` | R2, R3, R4, R5 |
| `controls/leak.sh` | 352 points: LSan **specifically**, byte counts against the model's invariant, 4 opt levels, hardened rung as the control |
| `controls/affine_leak.rs` | the NEGATIVE half — a bare token is affine — with its own must-fail arm |
| `controls/ledger_leak.py` | the POSITIVE half — the shipped ledger — with **two** arms that must fire, one per exit |
| `controls/spellings.py` | four R3 and **five** R4 spellings, generated from the shipped rungs |
| `controls/miri_seeds.sh` | seeds 0..7 plus the deleted-`dig_free` positive control |
| `controls/sweep.py` | the out-of-band prediction test |
| `inputs/gen.py` | deterministic inputs, with four assertions that would each have shipped a broken row |
