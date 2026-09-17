/* ============================================================================
 * asan_reach.c -- THE INSTRUMENT BEHIND **F50**'s bytes x ASan x canary TABLE
 *
 * !!! WHY IT IS COMMITTED. It was written under `.temp/mgr166/`, which is
 * GITIGNORED, and `RECAP_PHP.md:8396` (F50, landed 2026-09-09, commits
 * d2f0a18/2d780ea) cites it BY PATH as the measurement that produced the
 * published table and the claim *"the cliff is at 32 bytes, not near 384"*.
 * `.memory-php/04-process.md` LAW 11: a published finding whose only evidence
 * is a gitignored probe will not survive a clean checkout. Promoted by
 * `TASK_PHP_064`, 2026-09-17, repo at commit f4bda71.
 *
 * !! IT IS CITED FOUR TIMES AND ONLY ONE IS THE DEBT. Under F52 and F150 the
 * same file is ruled HISTORY -- it is the SUBJECT of a sentence about a defect
 * class (the `CANARY_BYTE 0xA5` no-op below), and those sentences state the
 * claim in full. `probes/scratchdeps.py::ADJUDICATION` carries the reason per
 * (finding, file); read that, not the bucket.
 *
 * *** RE-DERIVED ON PROMOTION, 2026-09-17, clang -O1 -fsanitize=address on this
 * box -- the published table reproduces TO THE ROW:
 *
 *      8, 16        REPORTED  stack-buffer-overflow
 *      32 .. 512    SILENT    canary CAUGHT IT   (offsets 0/32/96/352/480)
 *      4096         SILENT    canary INTACT -- past its own 512 B
 *
 * So the cliff really is at 32 (the redzone width) and not near 384, and the
 * canary oracle works across the whole range where ASan fails.
 *
 * !! WHAT IT NEEDS THAT IS NOT COMMITTED: a clang with ASan
 * (`~/tools/llvm/bin/clang` on this box) and nothing else. It is 60 lines of
 * C99 + `<sys/select.h>`, reads no repo file, and the BINARY is deliberately
 * NOT committed -- `CLAUDE.md` Don't #1: keep the generator, delete the
 * artefact. There is no registry entry because `checkers.py::_disk()` files
 * `.py` and `.sh` only; a `.c` probe is evidence, not a checker.
 *
 * !!! WHAT IS STILL OWED. (1) F50 is flagged MANAGER, UNREVIEWED, n = 1 in its
 * own heading. (2) The reach measured here is bounded BY THE CANARY, not by the
 * defect -- 4096 reads INTACT because the canary is 512 B, which is a limit of
 * the instrument and not a property of ph16. (3) `volatile` on the canary is
 * LOAD-BEARING and nothing here fails if it is removed; an arm that compiles
 * both ways and compares would be the cheap next step and is NOT written.
 * (4) The numbers above were taken at -O1 only today; F50 claims identity at
 * -O0/-O1/-O3 and that three-way check was NOT re-run on promotion.
 * ============================================================================
 */
/* TASK_PHP_025 premise check (PROTOCOL rule 14): HOW FAR PAST an on-stack
 * fd_set can ASan still see a write -- and WHAT ABSORBS the ones it misses?
 *
 * CATALOGUE.md's ph16 block claims, and TASK_PHP_025 §3 is built on it:
 *   "a write 8 bytes past the object reports stack-buffer-overflow; the same
 *    write 384 bytes past is SILENT, because it jumps clean over the redzone
 *    into unpoisoned stack."
 *
 * If that is wrong the whole oracle section of the build task is wrong, so the
 * manager runs it rather than citing it.
 *
 * ONE write per process, at a chosen distance, so the first report is the only
 * report and there is no ordering effect. The `canary` array stands in for the
 * caller's other locals -- stream_select() really does have three fd_sets and
 * several ints in the same frame -- and is checked afterwards, because a write
 * ASan misses may still be VISIBLE TO A CANARY, which is the difference
 * between "no oracle exists" and "a sanitizer is the wrong oracle".
 *
 *   gcc -O1 -g -fsanitize=address -o asan_reach asan_reach.c
 *   for d in 8 16 32 64 128 384 512 4096; do ./asan_reach $d; done
 *
 * Prints SILENT/REPORTED and whether the canary caught it. A run that cannot
 * decide says CANNOT EVALUATE and exits non-zero.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>

#define CANARY_LEN 512
#define CANARY_BYTE 0xA4   /* bit 0 CLEAR: `|= 1` must be VISIBLE. 0xA5 made it a no-op
                            and the probe reported "nothing saw it" -- a confident wrong negative. */

int main(int argc, char **argv)
{
	if (argc != 2) {
		fprintf(stderr, "CANNOT EVALUATE: usage: %s <byte-distance-past-fd_set>\n", argv[0]);
		return 2;
	}
	long d = strtol(argv[1], NULL, 10);

	fd_set fds;
	volatile unsigned char canary[CANARY_LEN];
	FD_ZERO(&fds);
	memset((void *)canary, CANARY_BYTE, sizeof canary);

	unsigned char *base = (unsigned char *)&fds;
	long off = (long)sizeof(fds) + d;

	printf("d=%-5ld fd_set@%p canary@%p (canary is %+ld from fd_set)\n",
	       d, (void *)base, (void *)canary, (long)((char *)canary - (char *)base));
	fflush(stdout);

	base[off] |= 1;                       /* the write ph16 performs */

	/* reached only if ASan did not abort */
	int hit = -1;
	for (int i = 0; i < CANARY_LEN; i++)
		if (canary[i] != CANARY_BYTE) { hit = i; break; }

	printf("  SILENT under ASan.  canary: %s\n",
	       hit < 0 ? "INTACT -- nothing in this frame saw it"
	               : "CAUGHT IT");
	if (hit >= 0)
		printf("  canary[%d] = 0x%02X (was 0x%02X)\n", hit, canary[hit], CANARY_BYTE);
	return 0;
}
