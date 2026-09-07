# TASK_PHP_001_REPORT_TYPE — the TYPE axis mining report

**Agent:** research engineer (read-only). **Status:** delivered, **NOT REVIEWED**.
**Evidence:** `.tasks-php/TASK_PHP_001_MINE/type/{candidates.json,NOTES.md,VERIFY.md}`
— promoted out of gitignored `.temp/`, because the earlier PHP effort lost
regeneration scripts permanently that way.

> ⚠ **`PROTOCOL.md` rule 9: nothing here goes into `.memory-php/` until a review
> lands.** The three claims the manager re-derived independently are marked ✅
> **and nothing else is.** Everything unmarked is the agent's, unverified.

## Delivered

**15 candidates over 12 distinct mechanism families**, schema-validated (19
required keys on every entry). Manager-verified count: `len(candidates) == 15`.

## ⚠⚠ THE MANAGER'S NAMED CLAIM WAS REFUTED, AND THE REFUTATION IS THE USEFUL PART

`TASK_PHP_001` asked the agent to attack: *"the 11 CWE-843 rows are ONE mechanism
at eleven sites, and the CoW / reference-separation rows are a genuinely
different second mechanism."*

**Half right, and wrong in a way that would have cost a row.**

- ✅ The CoW half **stands, and is stronger than the manager put it**:
  `CRASH-104` and `CRASH-058` share one *named* root cause —
  `SEPARATE_ZVAL_IF_NOT_REF` (`zend.h:568-571`) **is a no-op exactly when
  `is_ref == 1`**, so `convert_to_*_ex` silently degrades from copy-on-write to
  in-place retype. Callee side and caller side of one defect.
- ⚠⚠ The *"one mechanism"* half is **wrong — there are five** — and the
  manager's *"different second mechanism"* **is not outside the eleven, it is
  two of them.** `string.c:1945` and `zend_execute_API.c:730` both carry
  `cwe = CWE-843` in `index.csv`, and the manager had listed both inside its own
  eleven in the same prompt. The split:

  | family | rows |
  |---|---|
  | missing read guard | 036, 037, 039, 093, 101 |
  | `HASH_OF` laundering | 079, 111 |
  | CoW / `is_ref` degradation | 058, 104 |
  | wrong tag **namespace** | 144 |
  | type inferred from creation path | 085 |

  ⚠ **Grouping by CWE would have merged the WRITE family into the READ family
  and lost the read/write split.** The blind labelling reaches the same split
  independently — `I4/O1` (n=8, read) vs `I4/O2` (n=3, *"a type established by an
  earlier check must still hold at the point of use"*).

## ✅✅ THE FIND, AND THE MANAGER RE-DERIVED IT FROM THE PRISTINE TARBALL

**PHP 5.0.0 has two `IS_*` enumerations whose values collide.** ✅ Verified:

```
Zend/zend_compile.h:285  #define IS_CONST   (1<<0)   = 1
Zend/zend_compile.h:287  #define IS_VAR     (1<<2)   = 4
Zend/zend.h:388          #define IS_LONG    1
Zend/zend.h:391          #define IS_ARRAY   4
```

✅ And `Zend/zend_compile.c:1196-1197`, verified verbatim:

```c
if ((last_op->op2.op_type == IS_CONST) && (last_op->op2.u.constant.value.str.len == sizeof(ZEND_CLONE_FUNC_NAME)-1)
    && !zend_binary_strcasecmp(last_op->op2.u.constant.value.str.val, last_op->op2.u.constant.value.str.len, ZEND_CLONE_FUNC_NAME, sizeof(ZEND_CLONE_FUNC_NAME)-1)) {
```

The guard tests the **operand-type** namespace (`op_type == IS_CONST`) and then
reads the **zval union** (`.value.str.val`, `.str.len`) with **no `Z_TYPE`
check**. A guard that is *present and passes* while interrogating the wrong
namespace.

The agent's claim about the harm, **not** independently re-derived by the
manager: it produces **both limbs in one expression** — `.str.val` overlays
`lval` (an attacker-chosen `char*`) while `.str.len` reads bytes the `lval` write
never touched (uninitialised), and the stale length is *what makes the guard
pass*. Only row on the axis labelled both `I4` and `I3`. One-line reproducer,
crashes during compilation.

Second standout, unverified by the manager: `zend_execute.c:1769` takes an early
exit via `NEXT_OPCODE()` (stride 1) on a two-word instruction while the normal
exit at `:1792-1795` correctly strides 2, and
`zend_opcode_handlers[ZEND_OP_DATA] = NULL` (`:4427`) — so the trailing data word
is decoded as an instruction and indirect-called through NULL. ⚠ **Its original
C shape already IS the pinned kernel shape**, which is rare.

## Citation audit

**Zero corrections needed.** All 19 citations checked resolved exactly. Two rows
carry corrections the corpus authors had already made inline (CRASH-093,
CRASH-061).

## Problems the agent reported

⚠⚠ **No hotness evidence is obtainable for this axis, and the reason is not
"cold" — it is that the instrument cannot see it.** (a) All 2534 ASan reports are
spatial/temporal (2450 heap-buffer-overflow, 490 UAF, 189 use-after-poison, 70
global-overflow); **there is no type-confusion or uninit class at all**, and MSan
was never run. (b) The census build is max-LTO, so `zend_hash_find` /
`convert_to_long` return **zero hits across all 2534 logs** while
`zend_do_fcall_common_helper` returns 11445 — inlining, not absence.

✅ **That ASan is structurally blind to this axis is itself an argument for the
axis existing**, and it is the same class as the PAT programme's *"a detector
that is not running looks exactly like a detector that found nothing."*

One `root_cause_id` is misleading (not a line error): CRASH-053's *"unchecked
`make_real_object`"* — `:1632` **is** followed by an explicit
`object->type != IS_OBJECT` at `:1635`. Recorded, not silently fixed.

## Unsure / not done (the agent's own list)

- Whether to split #5 from #11 (the corpus merges both into CRASH-153). Split,
  because the ordering window and the discarded status code are independently
  extractable and the blind labelling separates the obligations. **Manager's
  call, still open.**
- #4 / #13 should probably be **one row with two limbs** (same `HASH_OF` macro,
  opposite misuses); the pairing is a better finding than either alone.
  **Flagged, not decided.**
- CRASH-061's `:513` claim not verified (row rejected as an ordinary null-deref).
- Rejections were **only** for C-side duplication or wrong-axis routing.
  ✅ **No Rust/Verus/Miri reasoning entered any ranking** — the bar held.

## Manager's adjudication

**Accepted as an engineer report; not yet authoritative.** Three claims
re-derived from the pristine tarball (the enum collision, the two enum value
sets, `zend_compile.c:1196-1197`) and marked ✅ above. **Everything else is
unmarked on purpose** — `RECAP_PAT.md`'s standing rule is that a `✅` goes on a
sentence only after running it, and four consecutive PAT reviews found a mark
the manager had not earned.

**Owed to the review:** the both-limbs claim on candidate #2, the
`ZEND_OP_DATA` NULL-handler claim on #3, and the two open groupings above.
