#ifndef PH52_D0_NOINL_H
#define PH52_D0_NOINL_H
/* Mirrors `common/driver.h`'s SLB_NOINLINE exactly, so the probe's
 * isolated / whole distinction is the harness's. */
#ifdef SLB_ISOLATED
#define SLB_NOINLINE __attribute__((noinline))
#else
#define SLB_NOINLINE
#endif

/* NOINL models the TRANSLATION-UNIT BOUNDARY between `Zend/zend_operators.c`
 * (concat_function), `Zend/zend.c` (zend_make_printable_zval) and
 * `Zend/zend_variables.c` (_zval_dtor) -- THREE TUs upstream, which
 * `harness/build.py` cannot reproduce because it compiles exactly three for the
 * whole row.  `-DPH52_INLINE_CALLEE` turns it off, which is the control, and
 * `c/kernel.h`'s PH52_NOINLINE is the shipped spelling. */
#ifdef PH52_INLINE_CALLEE
#define NOINL
#else
#define NOINL __attribute__((noinline))
#endif
#endif
