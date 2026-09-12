/* ph53 control -- THE WILD POINTER, **CHOSEN RATHER THAN OBSERVED**.
 *
 *   ~/tools/llvm/bin/clang -std=c99 -O1 -I ../../../common-php \
 *       -o wild_choice controls/wild_choice.c && ./wild_choice
 *   (or through `controls/wild_choice.py`, which also runs the negatives)
 *
 * ============================================================================
 * ⚠⚠ WHY A CONTROL NEEDS A CHOSEN VALUE
 * ============================================================================
 * The defect is an uninitialised read, so what the slot holds is whatever the
 * allocator left there -- and a control that merely OBSERVES that is a control
 * whose answer changes with the libc, the heap history and the sanitizer.
 * `controls/r1h_consumers.py` shows the OBSERVED case (under ASan it is
 * deterministic at `0xbe` fill bytes, and under plain `malloc` it is not).
 * This probe CHOOSES it.
 *
 * The mechanism is PHP 5.0.0's own size-class cache, `zend_alloc.c:150-168`
 * and `:263-279`, modelled in `common-php/emalloc_shim.h`: `_efree` on a block
 * whose recorded size falls in a cache class does **not** return it to
 * `malloc` -- it pushes the block onto `AG(cache)[real_size>>3]` **with its
 * payload intact** -- and the next same-class `_emalloc` pops it straight back.
 * So:
 *
 *     1. emalloc(8 * n_decl)          same size class as the interface array
 *     2. write a CHOSEN value into every slot
 *     3. efree                        -> the shim's cache, contents intact
 *     4. erealloc(NULL, 8 * n_decl)   -> zend_compile.c:2571, cache HIT
 *     5. the "uninitialised" tail now holds exactly what step 2 chose
 *
 * ⚠ Step 4 is why `php_shim_reset()` is NOT called between 3 and 4: the kernel
 * calls it at the top of every call precisely so that call N does not depend on
 * call N-1, and this probe is deliberately the configuration that does.
 *
 * ============================================================================
 * ⭐⭐ WHAT IT SHOWS, AND IT IS SHARPER THAN "R1h GIVES A CORRECT NO-MATCH"
 * ============================================================================
 * With the value chosen, the COMPARE-ONLY consumer (`zend_compile.c:1951`,
 * which does NOT dereference) gives a **silent wrong answer** on R1: the
 * unwritten slot compares EQUAL to an interface the class never implemented,
 * so `zend_do_inherit_interfaces` reports a duplicate that is not there. On
 * R1h the slot is NULL, which can never equal a pool address, so the answer is
 * RIGHT.
 *
 * ▶ **So the 2005 fix is COMPLETE on the comparing consumer and USELESS on the
 * dereferencing one** -- which is a stronger statement than
 * `controls/r1h_consumers.py` can make, because there the unprimed garbage
 * happened not to match and "correct" could have been luck.
 *
 * The dereferencing consumer (`zend_operators.c:1535`) is reported for both
 * primings too: with a chosen VALID pool address it returns the chosen id and
 * does not crash -- a silent wrong answer from a wild dereference that happened
 * to land on live memory, which is what CWE-824 costs when it does not kill
 * the process.
 *
 * ⚠ This TU is a STANDALONE PROBE and is not on `harness/build.py`'s path --
 * that compiles exactly three translation units (`PROTOCOL_PHP.md` §B2). It is
 * under `controls/` and `harness-php/gate.py::c_digest_audit` does not reach
 * it, so nothing it does can move a measured number.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#define PHP_SHIM_IMPL
#include "emalloc_shim.h"

#define MAXP 8

typedef struct { uint64_t id; } iface;
typedef struct { iface **interfaces; unsigned int num_interfaces; } ce_t;

static iface pool[MAXP];

/* zend_operators.c:1534-1535, narrowed -- THE FAULTING CONSUMER. */
static int deref_scan(const ce_t *ce, const iface *target, uint64_t *got)
{
    unsigned i;
    for (i = 0; i < ce->num_interfaces; i++) {
        if (ce->interfaces[i]->id == target->id) {   /* the dereference */
            *got = ce->interfaces[i]->id;
            return 1;
        }
    }
    *got = 0;
    return 0;
}

/* zend_compile.c:1951, narrowed -- THE COMPARE-ONLY CONSUMER. */
static unsigned cmp_scan(const ce_t *ce, const iface *entry)
{
    unsigned i;
    for (i = 0; i < ce->num_interfaces; i++) {
        if (ce->interfaces[i] == entry) {            /* no dereference */
            break;
        }
    }
    return i;
}

/* One run.  `chosen` is the pool index every primed slot is set to point at,
 * or -1 for "do not prime".  `hardened` selects `d09cdd9f71f3`'s phase 2.
 * `fill0` writes slot 0 legitimately, leaving the rest uncovered.
 *
 * ⚠ THE DEREFERENCING CONSUMER IS RUN IN A FORKED CHILD, because on the
 * hardened arm it dereferences NULL and dies -- which is the row's result and
 * must be REPORTED rather than allowed to take the probe with it.  The parent
 * prints the child's wait status, so `signal=11` is a measurement. */
static void run(int chosen, int hardened, unsigned n_decl, int fill0,
                int target, const char *label)
{
    ce_t ce;
    unsigned i;
    unsigned stop;
    pid_t pid;
    int status = 0;
    size_t bytes = sizeof(iface *) * (size_t)n_decl;

    php_shim_reset();

    if (chosen >= 0) {
        /* steps 1-3: prime the size-class cache with a CHOSEN payload */
        iface **prime = (iface **) php_shim_emalloc(bytes);
        for (i = 0; i < n_decl; i++)
            prime[i] = &pool[chosen];
        php_shim_efree(prime);          /* -> the shim's cache, intact */
    }

    /* zend_compile.c:3747-3748 */
    ce.interfaces = NULL;
    ce.num_interfaces = 0;
    for (i = 0; i < n_decl; i++)
        ce.num_interfaces++;            /* :2591, and no slot is written */

    /* zend_compile.c:2569-2572, R1 or R1h */
    if (ce.num_interfaces > 0) {
        if (hardened) {
            ce.interfaces = (iface **) php_shim_emalloc(bytes);
            memset(ce.interfaces, 0, bytes);
        } else {
            ce.interfaces = (iface **) php_shim_erealloc(ce.interfaces, bytes);
        }
    }

    if (fill0 && n_decl > 0)
        ce.interfaces[0] = &pool[0];    /* one legitimate ADD_INTERFACE */

    /* the COMPARE-ONLY consumer: never fatal, so it runs in-process */
    stop = cmp_scan(&ce, &pool[target]);
    printf("  %-24s cmp_scan=%u %-26s", label, stop,
           stop == ce.num_interfaces ? "(no match, CORRECT)"
                                     : (stop == 0 ? "(matched slot 0)"
                                                  : "(MATCHED UNWRITTEN SLOT)"));
    fflush(stdout);

    /* the DEREFERENCING consumer, in a child */
    pid = fork();
    if (pid == 0) {
        uint64_t got = 0;
        int hit = deref_scan(&ce, &pool[target], &got);
        printf("deref hit=%d id=%016llx\n", hit, (unsigned long long) got);
        fflush(stdout);
        _exit(0);
    }
    waitpid(pid, &status, 0);
    if (WIFSIGNALED(status))
        printf("deref DIED signal=%d\n", WTERMSIG(status));
    else if (WEXITSTATUS(status) != 0)
        printf("deref exit=%d\n", WEXITSTATUS(status));

    if (ce.num_interfaces > 0 && ce.interfaces)
        php_shim_efree(ce.interfaces);
}

int main(void)
{
    unsigned j;
    for (j = 0; j < MAXP; j++)
        pool[j].id = 0x0C1A5500000001ULL + j;

    printf("ph53 controls/wild_choice.c -- the wild pointer, CHOSEN\n");
    printf("  pool[j].id = 0x0C1A5500000001 + j, j in 0..7; n_decl = 2; "
           "slot 0 filled with &pool[0]; query target = pool[3]\n\n");

    printf("R1  (erealloc, no memset) -- the unwritten slot is whatever the "
           "cache handed back:\n");
    run(3, 0, 2, 1, 3, "primed with &pool[3]");
    run(5, 0, 2, 1, 3, "primed with &pool[5]");
    printf("\nR1h (d09cdd9f71f3: emalloc + memset) -- history is irrelevant:\n");
    run(3, 1, 2, 1, 3, "primed with &pool[3]");
    run(5, 1, 2, 1, 3, "primed with &pool[5]");
    return 0;
}
