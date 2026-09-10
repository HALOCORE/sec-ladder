# ph16 — `FD_SET` past an on-stack `fd_set`

**PHP 5.0.0, `ext/standard/streamsfuncs.c:541`, corpus row CRASH-098.**

```c
if (SUCCESS == php_stream_cast(stream, PHP_STREAM_AS_FD_FOR_SELECT
                               | PHP_STREAM_CAST_INTERNAL, (void*)&this_fd, 1)) {
    FD_SET(this_fd, fds);            /* :541 -- FD_SETSIZE is never mentioned */
    if (this_fd > *max_fd) {
        *max_fd = this_fd;
    }
}
```

`FD_SET(d, s)` is `s->__fds_bits[d / 64] |= 1UL << (d % 64)` and consults no
file-descriptor table, so an index of 2048 writes **256 bytes into a 128-byte
object**. And `fds` is not the callee's: `PHP_FUNCTION(stream_select)` declares
`fd_set rfds, wfds, efds;` at `:658` and reads all three back at `:706`.

**So the bytes an over-index reaches are the other two `fd_set`s — live, and the
function's own result depends on them.**

## The three things this row is for

1. ⚠⚠ **Stock ASan sees this for 32 bytes and then stops.** Index 1024…1279
   reports `stack-buffer-overflow`; index 1280…3071 is **silent**, because past
   the redzone the write lands in a real object. `adversarial-redzone.bin` and
   `adversarial-silent.bin` differ in that one number and in nothing else.
   ⭐ The row does not need a canary: PHP's own neighbours are the witness, and
   `controls/oracle.py` **predicts the corrupted checksum from the measured
   stack layout and reproduces the binary bit for bit**, under both compilers.

2. ⚠⚠⚠ **One of the four measured C cells already carried the row's own bound,
   and the toolchain put it there.** Ubuntu's gcc adds `-D_FORTIFY_SOURCE=3`
   when it optimises; glibc's fortified `FD_SET` is `__fdelt_chk`. `c-gcc-O3`
   aborted with `*** bit out of range 0 - FD_SETSIZE on fd_set ***` and charged
   **14.87 Ir per benign `FD_SET`** — +60.6 % whole-program. Both C kernels
   therefore `#undef _FORTIFY_SOURCE`; `controls/fortify.py` measures both
   configurations.

3. ⭐ **The same defect is invisible to the C detector and visible to the Rust
   one.** `controls/miri_vs_asan.py`: ASan on R1 at index 2048 says nothing;
   Miri on an R4 mutant with the guard deleted reports `Undefined Behavior` at
   `core::slice::get_unchecked`'s own precondition. **The asymmetry is about
   where the bound is written down** — Rust puts it in a contract, C puts it
   nowhere — and not about one checker watching memory harder.

## The upstream fix is three guards, not one

`99e290f882c9` (2004-09-17, *"Bug #24189: possibly unsafe select(2) usage"*),
POSIX branch: `&& this_fd >= 0` at the call site, `PHP_SAFE_FD_SET`'s
`if (fd < FD_SETSIZE)`, and **`PHP_SAFE_MAX_FD`'s clamp of `max_fd` in the
caller's frame** — which is not about the write at all. `controls/fix_scope.py`
prices each one separately; guard (a) is measurably **dead** on this kernel's
domain and is carried anyway because it is what upstream shipped.

⭐ **A macro named `PHP_SAFE_…` whose safety is `#ifdef`-conditional**, and the
Win32 comment is *correct*: there `fd_set` is a counted array of `SOCKET`s, so
the bound lives in the platform's data structure instead of in the code.
`c/kernel_hardened.c` states which branch it compiles.

## Where to look

| | |
|---|---|
| `spec.md` | the contract the gate enforces, and the hashed declaration |
| `NOTES.md` | **the measurements** — §2 fortify, §3 the oracle, §4 the fix, §8 the ladder and its mechanism, §10 Verus |
| `model.py` | three independent implementations, and the arm table over the calls the driver actually makes |
| `controls/` | `oracle.py` `fortify.py` `fix_scope.py` `guard_equiv.py` `negatives.py` `miri_vs_asan.py` — each with its must-fire and must-NOT-fire cases |

⚠ `NOTES.md` §11 lists what this row does **not** do; the largest item is that
`controls/spellings.py` was not built, so **no figure here is a `fixed-R4
bound`**.
