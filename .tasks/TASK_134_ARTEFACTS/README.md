# TASK_134 artefacts — the six files that decided four candidate rows

⚠ **Promoted out of `.temp/t134/` and `.temp/mgr134/` deliberately.** `CLAUDE.md`
rule 17 — *promote, don't publish* — and `.memory/00-environment.md` constraint 6:
a `.temp/` path cited from a committed file is one `.temp/` cleanup away from
being a citation that resolves to nothing. **`TASK_122` already lost evidence
exactly this way.** RECAP finding 48 rests on these six; the rest of the probe
tree stays in `.temp/t134/` and is re-runnable from its own `run.sh` scripts.

Nothing here is imported by `check.py`, `measure.py` or `build.py`, and `.tasks/`
is outside both digests, so these files cost no sweep.

| file | what it decided |
|---|---|
| `realloc_move.c` | ⚠⚠ **The `p25` kill.** `realloc`'s move behaviour in four heap topologies. **Regime A is `p25`'s shipped shape and `realloc` NEVER MOVES there** — `moved=0/12` under both compilers — so the stale pointer is never stale and the UB is unobservable. |
| `accept_recycle.rs` | ⚠⚠ **The borrow checker ACCEPTS a real use-after-recycle.** `forbid(unsafe_code)`, zero `unsafe` blocks, Miri-clean: `pop` ends the element's lifetime, `push` recycles the slot, `v[2]` reads `9999` where `30` was marked. |
| `miri_positive_control.rs` | **The control that makes the line above mean anything.** A genuine use-after-free; Miri must report UB on it. If it ever goes quiet, `accept_recycle.rs`'s clean result is uninterpretable. |
| `ctl1_nostruct.rs` | **The borrow checker REJECTS what cannot have the bug**, extreme case: a `struct S { v: u32 }`, no heap, no container — and the `E0502` message is **identical** to `p25`'s safe rung's. |
| `ctl4_reserved.rs` | Same, sharper: a `Vec` with capacity 64 reserved and length 1, which **provably cannot reallocate**, still `E0502`. |
| `r2_idx.rs` | ⚠ **The manager's catalogue prediction was wrong.** The index port does not put the bug in `p04`'s class — **it has no bug at all**, because `realloc` copies, so `v[k]` still names the same element. |

## Reproducing

```sh
gcc -O2 realloc_move.c -o /tmp/x && /tmp/x          # use .temp/, not /tmp -- see rule 1
~/tools/llvm/bin/clang -O2 realloc_move.c -o ... && ...

~/.cargo/bin/rustc --edition 2021 -O accept_recycle.rs -o ... && ...
~/.cargo/bin/rustc --edition 2021 -O ctl1_nostruct.rs   # expect error[E0502]
~/.cargo/bin/rustc --edition 2021 -O ctl4_reserved.rs   # expect error[E0502]
~/.cargo/bin/rustc --edition 2021 -O r2_idx.rs          # expect COMPILES, prints 0

SYSROOT=$(~/.cargo/bin/cargo +nightly-x86_64-unknown-linux-gnu miri setup --print-sysroot)
MIRI=~/.rustup/toolchains/nightly-x86_64-unknown-linux-gnu/bin/miri
env -u LD_PRELOAD $MIRI --sysroot "$SYSROOT" --edition 2021 miri_positive_control.rs  # MUST report UB
env -u LD_PRELOAD $MIRI --sysroot "$SYSROOT" --edition 2021 accept_recycle.rs         # expect 0 UB
```

⚠ **`env -u LD_PRELOAD` is not optional on this box** — this shell inherits
`LD_PRELOAD=/usr/libexec/coreutils/libstdbuf.so` and a dynamically linked
sanitiser binary refuses to start behind it, **failing to the same exit code as
a clean run**.

⚠ **Run the positive control first, every time.** A detector that has silently
stopped working reports exactly what a clean program reports.
