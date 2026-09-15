/* ph97 rung R1h -- `c/kernel.c` plus the ONE LINE of `f7326d627962`.
 *
 * ============================================================================
 * THE PATCH, WHOLE
 * ============================================================================
 *   From f7326d6279629ccd80cc77fa389584f36434a2fd
 *   Antony Dovgal <tony2001@php.net>, Fri 28 Jan 2005 02:00:39 +0000
 *   "MFB: fix #31732"
 *   ext/mbstring/mbstring.c | 2 +-      1 insertion, 1 deletion
 *
 *   -	if (!strcasecmp("all", typ)) {
 *   +	if (!typ || !strcasecmp("all", typ)) {
 *
 * `git apply` PLACES it on the pristine 5.0.0 file -- *Hunk #1 succeeded at
 * 3216 (offset -13 lines)* -- and the post-image line at `:3219` is byte for
 * byte the `+` line above. ../NOTES.md §5 has the run, the offset and the
 * bytes; `controls/r1h_backport.py` re-derives them on every invocation.
 *
 * ⭐⭐ THE FIX WIDENS THE BENIGN DOMAIN RATHER THAN NARROWING IT. With the
 * argument supplied, behaviour is byte-identical -- `||` short-circuits and the
 * added test is a load of a pointer that is not NULL. With the argument absent,
 * the patched build ANSWERS WITH THE `all` ARRAY where the unpatched one
 * faults. So the input whose answer changes is one that previously CRASHED, and
 * the two C rungs agree on every call in `inputs/small.bin` and
 * `inputs/large.bin`. ../NOTES.md §5 and §9.
 *
 * ⚠ THIS FILE DIFFERS FROM `c/kernel.c` IN EXACTLY ONE LINE. `diff` them.
 * Everything below, including the header that follows, is that file's.
 *
 * ============================================================================
 * -- and, unchanged, c/kernel.c's own header ---------------------------------
 * ============================================================================
 *
 * PHP 5.0.0's `PHP_FUNCTION(mb_get_info)` and the parser that feeds it,
 * NARROWED.
 *
 * ============================================================================
 * PROVENANCE
 * ============================================================================
 *   php-5.0.0.tar.gz  sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa
 *                            8f936dc6301d6919
 *   tar -xzOf <tarball> php-5.0.0/ext/mbstring/mbstring.c | sed -n '3209,3252p'
 *   plus  Zend/zend_API.c | sed -n '463,549p'    -- `zend_parse_va_args`
 *   plus  Zend/zend_API.c | sed -n '290,333p'    -- the 's' arm of the arg
 *                                                   converter
 *   plus  ext/mbstring/libmbfl/mbfl/mbfl_encoding.c | sed -n '253,265p'
 *   Corpus row CRASH-126. Tier `narrowed`: the WRAPPER comes off (zvals become
 *   a fixed record, the `va_list` becomes two out-parameters, TSRM plumbing
 *   goes); THE BODIES ARE UNCHANGED. Every divergence is itemised in
 *   ../spec.md's `provenance.divergences`, individually and with a citation.
 *
 * ============================================================================
 * THE DEFECT, IN ONE LINE  (⚠ describes `c/kernel.c`; the line above removes it)
 * ============================================================================
 * `:3215` tests one proposition and `:3219` needs another:
 *
 *     if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "|s",
 *                               &typ, &typ_len) == FAILURE) {   <- :3215
 *         RETURN_FALSE;                                          <- :3216
 *     }
 *
 *     if (!strcasecmp("all", typ)) {                             <- :3219
 *
 * The guard is PRESENT and it PASSES. `"|s"` puts the optional marker FIRST, so
 * `min_num_args` is set from a `max_num_args` that is still 0 (zend_API.c:486),
 * the count test at :511 admits `num_args == 0`, the write loop at :537 runs
 * zero times, and `zend_parse_parameters` returns SUCCESS having written
 * NOTHING. `typ` keeps its `:3211` initialiser and goes into libc.
 *
 * ⭐⭐ MEASURED, NOT REASONED. A PHP 5.0.0 CLI on this box, under
 * `.tasks-php/probes/segaddr.c`:
 *
 *     mb_get_info()                     -> SIG11 si_code=1 si_addr=(nil), 139
 *     mb_get_info("internal_encoding")  -> string(10) "ISO-8859-1",         0
 *
 * ../NOTES.md §1 has the runs, the build they were taken on, and the two
 * cautions that travel with them.
 *
 * ============================================================================
 * ⚠ THE FOUR `!= NULL` TESTS IN THIS FUNCTION ARE DEAD, AND THEY ARE DEAD
 *   UPSTREAM -- NOT ONLY HERE
 * ============================================================================
 * `:3221`, `:3224`, `:3227` and `:3230` each test
 * `mbfl_no_encoding2name(...) != NULL`, and that callee CANNOT return NULL:
 *
 *     encoding = mbfl_no2encoding(no_encoding);
 *     if (encoding == NULL) {
 *         return "";                                mbfl_encoding.c:260-261
 *
 * ▶ So the arm is unreachable in any 5.0.0 build, and the measured
 *   `http_input => string(0) ""` is that line firing: `MBSTRG(http_input_
 *   identify)` is `mbfl_no_encoding_invalid` (mbstring.c:726), `mbfl_no2
 *   encoding` returns NULL for it, and the caller gets `""` rather than NULL.
 *   This kernel keeps both the tests and the reason they are dead. ../NOTES.md
 *   §4.
 */
#include <stdint.h>
#include <stddef.h>

#include "kernel.h"

#define PHP_SHIM_IMPL /* exactly one TU defines the allocator state */
#include "emalloc_shim.h"

/* ==================================================================== zval ==
 * The argument, as `zend_parse_arg` sees it. `zval` is a tagged union plus a
 * refcount; the 's' arm of the converter reads the TYPE, and for a string the
 * VALUE and the LENGTH. Nothing else in this row reads a zval, so nothing else
 * is here. ../spec.md `provenance.divergences`. */
typedef struct {
    uint8_t type;             /* Z_TYPE_PP(arg)          */
    uint8_t lval;             /* Z_LVAL_PP(arg), for the non-string arms */
    uint8_t len;              /* Z_STRLEN_PP(arg)        */
    const uint8_t *val;       /* Z_STRVAL_PP(arg)        */
} ph97_zval;

/* ============================================================ the globals ==
 * `MBSTRG(...)`, as PHP 5.0.0 initialises them and as the measured CLI reports
 * them. Four `enum mbfl_no_encoding` values; `mbfl_no_encoding_invalid` is the
 * one `mbfl_no2encoding` does not know.
 *
 *   internal_encoding  ISO-8859-1              mbstring.c:3221-3222
 *   http_input         invalid   -> ""         mbstring.c:3224-3225, :726
 *   http_output        pass                    mbstring.c:3227-3228
 *   func_overload      pass (0)                mbstring.c:3230-3231
 */
#define PH97_ENC_INVALID 0
#define PH97_ENC_PASS 1
#define PH97_ENC_8859_1 2
#define PH97_NENC 3

/* ⚠ NUL-PADDED TO THE FRAME WIDTH, in C by the array initialiser's own rule:
 * `char x[21] = "pass"` zero-fills the tail. Every rung's compare and fold stop
 * at the first NUL, so the padding is invisible to the answer and present only
 * so that both operands of `ph97_strcasecmp` have one width. */
static const char ph97_enc_name[PH97_NENC][PH97_BUFSZ] = {
    /* PH97_ENC_INVALID */ "",
    /* PH97_ENC_PASS    */ "pass",
    /* PH97_ENC_8859_1  */ "ISO-8859-1"
};

/* `mbfl_no2encoding` -- NULL for an encoding number nothing knows. */
static const char *ph97_no2encoding(int no_encoding)
{
    if (no_encoding < 0 || no_encoding >= PH97_NENC) {
        return (const char *) 0;
    }
    return ph97_enc_name[no_encoding];
}

/* `mbfl_no_encoding2name` -- mbfl_encoding.c:253-265. ⚠ IT NEVER RETURNS NULL,
 * and that is what makes `mb_get_info`'s four NULL tests dead. */
static const char *ph97_no_encoding2name(int no_encoding)
{
    const char *encoding = ph97_no2encoding(no_encoding);
    if (encoding == (const char *) 0) {
        return "";
    }
    return encoding;
}

#define PH97_G_INTERNAL PH97_ENC_8859_1
#define PH97_G_HTTP_IN PH97_ENC_INVALID
#define PH97_G_HTTP_OUT PH97_ENC_PASS
#define PH97_G_OVERLOAD PH97_ENC_PASS

/* The five selectors, in `mb_get_info`'s own chain order -- which is
 * load-bearing, because the arms are tried one at a time and the first match
 * wins. mbstring.c:3219, :3233, :3237, :3241, :3245. The same five strings are
 * also the four KEYS `add_assoc_string` writes at :3222, :3225, :3228 and
 * :3231, so the table is used twice and spelled once. */
#define PH97_NSEL 5
static const char ph97_sels[PH97_NSEL][PH97_BUFSZ] = {
    "all", "internal_encoding", "http_input", "http_output", "func_overload"
};

/* ================================================== the compare, IN-KERNEL ==
 * ⛔⛔ THIS IS A MEASUREMENT DECISION AS MUCH AS A FIDELITY ONE, AND
 * ../NOTES.md §6 PRICES IT. `kernel_exclusive_ir` (family A1) is SYMBOL-SCOPED
 * and structurally excludes callee work, so a kernel whose entire work sits
 * inside libc `strcasecmp` would read ~0 in the statistic this programme
 * publishes. The compare is therefore implemented HERE, inside the measured
 * symbol. `controls/libc_compare.py` builds the libc-calling variant beside it
 * and reports `inside_share` for both, which prices the exclusion directly.
 *
 * ⚠ The consequence for the obligation: `I12/O3` says *a possibly-NULL pointer
 * must not be passed to a callee -- INCLUDING LIBC -- that dereferences it
 * without testing it*, and with the compare in-kernel the operative half is
 * *a callee that does not test its argument*, which this one does not.
 *
 * Semantics: `strcasecmp(3)`, C locale -- compare byte by byte after folding
 * A-Z to a-z, stop at the first NUL, return the difference of the folded
 * bytes. `controls/libc_compare.py` drives this against the real one. */
#define PH97_LOWER(c) ((uint8_t) (((c) >= 'A' && (c) <= 'Z') ? (c) + 32 : (c)))

static int ph97_strcasecmp(const char *a, const char *b)
{
    for (;;) {
        uint8_t ca = PH97_LOWER((uint8_t) *a);
        uint8_t cb = PH97_LOWER((uint8_t) *b); /* <- :3219's second operand */
        if (ca != cb) {
            return (int) ca - (int) cb;
        }
        if (ca == 0) {
            return 0;
        }
        a++;
        b++;
    }
}

/* ================================================== zend_parse_arg, 's' arm ==
 * zend_API.c:297-333, narrowed to the four type tags this row distinguishes.
 *
 * ⭐ THE `IS_NULL` FALL-THROUGH IS UPSTREAM'S AND IT IS LOAD-BEARING. `*p =
 * NULL; *pl = 0;` at :304-305 happens only `if (return_null)`, which is set by
 * the `!` modifier; `"|s"` carries no `!`, so IS_NULL falls through to
 * `convert_to_string_ex` and `typ` becomes the EMPTY STRING. Upstream's own
 * comment on the missing break is *break omitted intentionally* (:308).
 *
 * ▶ That is why the NULL VALUE and the ABSENT ARGUMENT are different states:
 *   `mb_get_info(null)` answers `bool(false)` on the measured CLI and
 *   `mb_get_info()` faults. ../NOTES.md §1.
 *
 * `frame` is the NUL-terminated `Z_STRVAL` the conversion materialises. */
static int ph97_parse_arg(const ph97_zval *arg, char *frame,
                          const char **p, int *pl)
{
    unsigned n = 0;

    switch (arg->type) {
    case PH97_IS_NULL:
        /* return_null is 0 for "|s" -- break omitted intentionally, :308 */
    case PH97_IS_BOOL:
    case PH97_IS_STRING:
        /* convert_to_string_ex, :314 */
        if (arg->type == PH97_IS_STRING) {
            unsigned i;
            for (i = 0; i < arg->len && i < PH97_STRMAX; i++) {
                frame[i] = (char) arg->val[i];
            }
            n = i;
        } else if (arg->type == PH97_IS_BOOL) {
            if (arg->lval & 1u) {
                frame[0] = '1';
                n = 1;
            }
        }
        frame[n] = '\0';
        *p = frame;                                        /* :315 */
        *pl = (int) n;                                     /* :316 */
        break;
    case PH97_IS_ARRAY:
    default:
        return PH97_FAILURE;             /* :330 -- "string", then E_WARNING */
    }
    return PH97_SUCCESS;
}

/* ===================================================== zend_parse_va_args ===
 * zend_API.c:463-549, narrowed: the `va_list` becomes the two out-parameters
 * the one spec letter needs, and the `EG(argument_stack)` consistency check at
 * :527-534 goes (itemised in ../spec.md). THE SPEC SCANNER AND THE COUNT TEST
 * ARE UPSTREAM'S, CHARACTER FOR CHARACTER, BECAUSE THEY ARE THE MECHANISM. */
static int ph97_parse_va_args(int num_args, const char *type_spec,
                              const ph97_zval *args, char *frame,
                              const char **p, int *pl)
{
    const char *spec_walk;
    int c, i;
    int min_num_args = -1;                                       /* :467 */
    int max_num_args = 0;                                        /* :468 */

    for (spec_walk = type_spec; *spec_walk; spec_walk++) {       /* :474 */
        c = *spec_walk;
        switch (c) {
        case 'l': case 'd':
        case 's': case 'b':
        case 'r': case 'a':
        case 'o': case 'O':
        case 'z': case 'Z':
            max_num_args++;                                      /* :482 */
            break;

        case '|':
            min_num_args = max_num_args;                         /* :486 */
            break;

        case '/':
        case '!':
            /* Pass */                                           /* :489-492 */
            break;

        default:
            return PH97_FAILURE;                                 /* :503 */
        }
    }

    if (min_num_args < 0) {                                      /* :507 */
        min_num_args = max_num_args;
    }

    if (num_args < min_num_args || num_args > max_num_args) {    /* :511 */
        return PH97_FAILURE;                                     /* :524 */
    }

    i = 0;                                                       /* :536 */
    while (num_args-- > 0) {                                     /* :537 */
        if (*type_spec == '|') {                                 /* :539 */
            type_spec++;
        }
        if (ph97_parse_arg(&args[i], frame, p, pl) == PH97_FAILURE) {
            return PH97_FAILURE;                                 /* :543 */
        }
        i++;
    }

    return PH97_SUCCESS;                                         /* :548 */
}

/* ============================================================ the fold ======
 * `array_init` + `add_assoc_string` and `RETVAL_STRING` are the two ways this
 * function answers, and `RETURN_FALSE` is the third. The row's `u64` is *the
 * selected settings' checksum, plus the count of RETURN_FALSE outcomes*, so
 * each of the three lands in it distinguishably. ⚠ BOTH `RETURN_FALSE` sites
 * fold the SAME tag, deliberately: upstream returns `bool(false)` from both and
 * the measured CLI cannot tell them apart either. */
#define PH97_TAG_FALSE 0x0Fu
#define PH97_TAG_ALL 0x0Au
#define PH97_TAG_SEL1 0x10u
#define PH97_TAG_SEL2 0x11u
#define PH97_TAG_SEL3 0x12u
#define PH97_TAG_SEL4 0x13u

static uint64_t ph97_fold_str(uint64_t acc, const char *s)
{
    while (*s) {
        acc = acc * 31u + (uint8_t) *s;
        s++;
    }
    return acc * 31u + 1u; /* the terminator, so "a" and "a\0b" differ */
}

/* ================================================== PHP_FUNCTION(mb_get_info)
 * mbstring.c:3209-3252, verbatim in structure. */
static uint64_t ph97_get_info(const uint8_t *b, uint64_t acc, uint64_t *falses)
{
    ph97_zval arg;
    char frame[PH97_BUFSZ];
    int num_args;

    const char *typ = (const char *) 0;                          /* :3211 */
    int typ_len;                                                 /* :3212 */
    const char *name;                                            /* :3213 */

    /* ⭐⭐ TWO INDEPENDENT BYTES: `num_args` is read from b[0] and `arg.type`
     * from b[1], and neither is computed from the other. They stand for
     * *was an argument supplied?* and *is it well-typed?*. Why that
     * independence is the row, and what a kernel that gave it up would be
     * measuring instead, is argued in ../spec.md `idiom.required[0]` and
     * ../NOTES.md §14 -- this comment points at the argument and does not
     * state its verdict (PROTOCOL_PHP.md §F6a). */
    num_args = (int) (b[0] % 3u);
    arg.type = (uint8_t) (b[1] % 4u);
    arg.len = (uint8_t) (b[2] % (PH97_STRMAX + 1u));
    arg.lval = b[3];
    arg.val = b + 4;

    if (ph97_parse_va_args(num_args, "|s", &arg, frame, &typ, &typ_len)
            == PH97_FAILURE) {                                   /* :3215 */
        (*falses)++;
        return acc * 31u + PH97_TAG_FALSE;                       /* :3216 */
    }

    /* ⛔⛔ :3219. `typ` is the caller's own NULL whenever the optional argument
     * was not supplied, and nothing between :3215 and here tests it. */
    if (!typ || !ph97_strcasecmp(ph97_sels[0], typ)) {          /* :3219, R1h */
        acc = acc * 31u + PH97_TAG_ALL;                          /* :3220 */
        if ((name = ph97_no_encoding2name(PH97_G_INTERNAL)) != (const char *) 0) {
            acc = ph97_fold_str(acc * 31u + 1u, ph97_sels[1]);
            acc = ph97_fold_str(acc, name);                      /* :3222 */
        }
        if ((name = ph97_no_encoding2name(PH97_G_HTTP_IN)) != (const char *) 0) {
            acc = ph97_fold_str(acc * 31u + 2u, ph97_sels[2]);
            acc = ph97_fold_str(acc, name);                      /* :3225 */
        }
        if ((name = ph97_no_encoding2name(PH97_G_HTTP_OUT)) != (const char *) 0) {
            acc = ph97_fold_str(acc * 31u + 3u, ph97_sels[3]);
            acc = ph97_fold_str(acc, name);                      /* :3228 */
        }
        if ((name = ph97_no_encoding2name(PH97_G_OVERLOAD)) != (const char *) 0) {
            acc = ph97_fold_str(acc * 31u + 4u, ph97_sels[4]);
            acc = ph97_fold_str(acc, name);                      /* :3231 */
        }
    } else if (!ph97_strcasecmp(ph97_sels[1], typ)) {            /* :3233 */
        if ((name = ph97_no_encoding2name(PH97_G_INTERNAL)) != (const char *) 0) {
            acc = ph97_fold_str(acc * 31u + PH97_TAG_SEL1, name);
        }
    } else if (!ph97_strcasecmp(ph97_sels[2], typ)) {            /* :3237 */
        if ((name = ph97_no_encoding2name(PH97_G_HTTP_IN)) != (const char *) 0) {
            acc = ph97_fold_str(acc * 31u + PH97_TAG_SEL2, name);
        }
    } else if (!ph97_strcasecmp(ph97_sels[3], typ)) {            /* :3241 */
        if ((name = ph97_no_encoding2name(PH97_G_HTTP_OUT)) != (const char *) 0) {
            acc = ph97_fold_str(acc * 31u + PH97_TAG_SEL3, name);
        }
    } else if (!ph97_strcasecmp(ph97_sels[4], typ)) {            /* :3245 */
        if ((name = ph97_no_encoding2name(PH97_G_OVERLOAD)) != (const char *) 0) {
            acc = ph97_fold_str(acc * 31u + PH97_TAG_SEL4, name);
        }
    } else {                                                     /* :3249 */
        (*falses)++;
        return acc * 31u + PH97_TAG_FALSE;                       /* :3250 */
    }
    return acc;
}

/* ================================================================ kernel ====
 * One window = one run of 24-byte call records. Each record is one
 * `mb_get_info(...)` call with its own argument count, type tag and bytes.
 *
 * ⚠ The kernel allocates NOTHING: `frame` is a 21-byte frame object and the
 * four settings are a fixed table, so allocations per kernel call are ZERO,
 * which satisfies `PROTOCOL_PHP.md` §B1a's O(1) precondition with room to
 * spare. `provenance.uses_allocator` is `false` and says so. The
 * `c/emalloc_shim.h` symlink is carried anyway, because that rule is
 * UNCONDITIONAL (`PROTOCOL_PHP.md` §B2). */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
    const uint8_t *win = buf + off;
    size_t nrec = len / PH97_REC;
    uint64_t acc = 0;
    uint64_t falses = 0;
    size_t r;

    for (r = 0; r < nrec; r++) {
        acc = ph97_get_info(win + r * PH97_REC, acc, &falses);
    }

    return acc * 31u + falses;
}
