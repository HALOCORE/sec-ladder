/* segaddr.c -- print the FAULTING ADDRESS of a SIGSEGV/SIGBUS, without gdb.
 *
 * This is `PROTOCOL_PHP.md` §A3's cheap instrument: it turns *"this input
 * crashes PHP 5.0.0"* into *"this input faults at si_addr=X with si_code=Y"*,
 * which is what separates a NULL dereference from a wild one and lets a row
 * check the faulting address against a claimed `offsetof`.
 *
 *     gcc -shared -fPIC -O0 -o <somewhere>/segaddr.so .tasks-php/probes/segaddr.c
 *     LD_PRELOAD=<somewhere>/segaddr.so <the 5.0.0 CLI> -n <script.php>
 *
 * ⚠ Build the `.so` under `.temp/` and delete it when your gates are green --
 * `CLAUDE.md` "Don't" rule 1: keep the generator, delete the artefact. THIS
 * FILE is the generator.
 *
 * ============================ WHY THIS EXISTS ============================
 * There is no gdb on this box, and valgrind 3.27.1 REFUSES TO START memcheck
 * ("a function redirection which is mandatory ... memcmp ... in
 * ld-linux-x86-64.so.2 ... cannot be set up" -- it wants glibc debuginfo).
 * So the only instrument available is the one the faulting process installs
 * on itself. `TASK_PHP_054` agent B wrote the first version of this file and
 * ran it over 36 corpus reproducers; 14 SIGSEGV'd.
 *
 * =========================== HOW TO READ IT =============================
 *   si_code=1 (SEGV_MAPERR)  the address is not mapped at all
 *   si_code=2 (SEGV_ACCERR)  mapped, but the access was not permitted
 *   si_addr=(nil)            a NULL dereference at offset 0
 *   si_addr=0x10             a NULL dereference at offset 0x10 -- e.g. a field
 *                            read off a NULL struct pointer; check the offsetof
 *   si_addr=<large/garbage>  a WILD pointer, NOT a NULL deref. Say so.
 *
 * ⚠⚠ TWO CAUTIONS THAT TRAVEL WITH EVERY RESULT FROM THIS PROBE:
 *
 * 1. **Name the build you measured on.** The 5.0.0 CLI on this box is
 *    php-in-safe-rust's ORACLE build, mysql+webext -- and it is built **-O0**.
 *    NOT a museum-default one. A fault address is a property of a build.
 *
 *    /!\ THIS LINE SAID `-O3 -march=native -flto` FOR ONE DAY AND THAT WAS
 *    WRONG. Those flags belong to the SIBLING variants `-O3lto` and `-maxlto`,
 *    which carry `.buildinfo` files; the plain `-mysql-webext` binary has none
 *    and its `config.status` says `-O0`. The caution whose entire point is SAY
 *    WHICH BUILD named the wrong build. Found by TASK_PHP_057's reviewer.
 *    +  Measured on all THREE tiers, ph97's trigger: si_code=1 si_addr=(nil)
 *       rc=139 on each. So the label was wrong and nothing downstream moved --
 *       which is luck, not a reason to relax the rule.
 *
 * 2. **A clean run is NOT evidence of absence** -- `RECAP_PHP.md` F3. A
 *    reproducer that does not fault here may still fault on another build, at
 *    another -O, or under ASan. ⭐ The converse DOES hold and is new: a run
 *    that faults, executed, IS evidence of PRESENCE, and that is the half the
 *    programme spent ten rows arguing instead of measuring.
 *
 * ⚠ `_exit(139)` rather than re-raising: re-raising on the alternate stack was
 * tried and lost the address on nested faults. 139 = 128 + SIGSEGV, so a shell
 * that reads `$?` sees what it would have seen without the preload.
 */
#define _GNU_SOURCE
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

static void handler(int sig, siginfo_t *si, void *uc)
{
	char buf[128];
	int n = snprintf(buf, sizeof buf,
	                 "\n[segaddr] SIG%d si_code=%d si_addr=%p\n",
	                 sig, si->si_code, si->si_addr);
	ssize_t r = write(2, buf, (size_t) n);
	(void) r; (void) uc;
	_exit(139);
}

__attribute__((constructor))
static void install(void)
{
	struct sigaction sa;
	memset(&sa, 0, sizeof sa);
	sa.sa_sigaction = handler;
	sa.sa_flags = SA_SIGINFO | SA_NODEFER;
	sigemptyset(&sa.sa_mask);
	sigaction(SIGSEGV, &sa, NULL);
	sigaction(SIGBUS, &sa, NULL);
}
