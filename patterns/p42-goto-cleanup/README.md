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
wrong. R4 does not — because the author checked, and nothing else did.**

**Precedent, fetched and quoted.** Linux `505d9dcb0f7d`, *"crypto: ccp - fix
resource leaks in `ccp_run_aes_gcm_cmd()`"* — `goto e_ctx` where `goto e_aad`
was needed, skipping the AAD work area's release. **CVE-2021-3764**, CVSS 5.5.
The generic form is SEI CERT **MEM12-C**.

## The results, in one screen

| | |
|---|---|
| gate | **0 failures**, 32 cells × 12 inputs, `contract_sha256 4a252569067081a5…`. ⚠ The VERDICT STRING is `PASS` or `PASS-WITH-BLOCKED-ROWS` depending on whether Miri finishes `large.bin` inside `check.py`'s 180 s `MIRI_TIMEOUT` — a run-dependent fact this file deliberately does not transcribe (`.tasks/PROTOCOL.md` rule 6). `spec.md`'s `miri.blocked_reason` declares that row, and a timeout is recorded as BLOCKED, never as a failure |
| Verus | **15 verified, 0 errors**; twin **18/0**; hand-written axioms **0** |
| TCB | 5 `external_body` items, **3** trusted by `_is_trusted`, each with a verified twin |
| identity | `unsafe ≡ verus` **exact** at `-O3` (`md5_fn 1ab63fde449d`, 122 insns), **`norel`** at `-O0` |
| **R1 − R1h** | **`+0.00` / `+0.00` on gcc** — the leak is free on the success path, exactly. **`−4.00` / `−5.00` on clang**, and the mechanism is a branch merge, not memory safety (`NOTES.md` 5) |
| R3 − R4 | **−198.00 / −8696.00** `Ir`/call — safe-tuned beats unsafe; **the spans OVERLAP** and the surviving claim is about the two infima (`NOTES.md` 11b) |
| R2 − R4 | +389.00 / +16385.00 |
| leak, detected | LSan at the gate's own stage-7 flags, **no hook**: the three erroring inputs report **exactly `n_err × win_len` bytes** — `model.py::leak_bytes` derives it from the file, so it is an invariant and not a transcript — at `-O0`…`-O3`, **88 control points**, hardened rung silent at all of them |
| Miri | seeds **0..7**, nine small inputs, no UB and no leak; `large.bin` exceeds the 180 s budget under interpretation; **the deleted-`dig_free` positive control fires** |

*(`Ir` figures are kernel-exclusive, `-O3`, inline mode `isolated`, from
`results/p42-goto-cleanup.json`. Section 5 of `NOTES.md` has the full table and
the two conventions.)*

### ⚠⚠ The headline is a negative result about the proof rung

> **Verus at the pinned version cannot state *"this allocation is released on
> every path"*.** `Tracked<Dealloc>` is **affine**, not linear: a proof may drop
> it, so an R5 that forgot the error path's release verifies with `0 errors`.
> Measured, with a positive control that fires —
> `controls/affine_leak.rs`, `2 verified, 0 errors` for the leaking arm and
> `error[E0382]: use of moved value` for the control.

**p42 is the first pattern here whose R5 proof does not cover the pattern's own
bug class.** `p27`'s `Tracked<Dealloc>` makes a deallocation *legal*; nothing
makes it *happen*, and p27's leak-freedom rests on a spelling pin rather than on
its proof. What stands behind leak-freedom on p42's Rust side is **Miri**, which
is why `miri.required` is `true` and why the control that deletes `dig_free` is
shipped: an unexercised checker is indistinguishable from a satisfied one.

### ⚠ And a per-element rate would have been wrong

`controls/sweep.py` fits `Ir/call = a + b·win_len` on windows 64..79 and
predicts windows 512..527. **Every rung's out-of-band residual is 3× to 25× its
in-sample residual**, and `safe_tuned` — the rung a headline would quote —
mispredicts its own shipped `large.bin` by **−2545 `Ir`/call** off an in-sample
residual of 12.57. So **p42 publishes two measured points per rung and no rate**
(`NOTES.md` 11d). One candidate mechanism — the allocator's size class — is
**refuted by isolation**; the real one is **OPEN** (`NOTES.md` 11e).

## What is in this directory

| path | what it is |
|---|---|
| `spec.md` | the kernel contract and the hashed pin block. Its `forbidden` list carries the CONDITIONS of p42's claim — heap not stack, a real `free` not a freelist, an error path a committed input reaches, and no measured input that reaches it |
| `model.py` | the independent reference. Two implementations; `sanitizer_expect` and `leak_bytes` are **derived**, not declared |
| `c/kernel.c`, `c/kernel_hardened.c` | R1 and R1h, one statement apart |
| `safe_naive.rs`, `safe_tuned.rs`, `unsafe.rs`, `verus.rs` | R2, R3, R4, R5 |
| `controls/leak.sh` | 88 points: LSan **specifically**, byte counts against the model's invariant, 4 opt levels, hardened rung as the control |
| `controls/affine_leak.rs` | the Verus negative result, with its own must-fail arm |
| `controls/spellings.py` | four R3 and four R4 spellings, generated from the shipped rungs |
| `controls/miri_seeds.sh` | seeds 0..7 plus the deleted-`dig_free` positive control |
| `controls/sweep.py` | the out-of-band prediction test |
| `inputs/gen.py` | deterministic inputs, with four assertions that would each have shipped a broken row |
