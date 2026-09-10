/* ph29 -- drive the SHIPPED `../c/kernel.c` on one window built from argv.
 * `controls/oracle.py` builds this and compares its `u64` against an
 * independent re-derivation. This file is not on any build path.
 *
 *   argv[1]  to_read   (decimal, may be negative)
 *   argv[2]  ctl
 *   argv[3]  want
 *   argv[4]  stride
 *
 * ⚠ It `#include`s the shipped kernel rather than re-typing it, so the thing
 * measured is the thing that ships. `c/kernel.c` defines PHP_SHIM_IMPL, so this
 * TU carries the allocator state exactly as a measured cell does. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include "kernel.c"

int main(int argc, char **argv)
{
	long to_read;
	unsigned ctl, want, stride, i;
	uint8_t *win;
	uint64_t r;

	if (argc < 5) {
		fprintf(stderr, "usage: %s to_read ctl want stride\n", argv[0]);
		return 2;
	}
	to_read = strtol(argv[1], NULL, 10);
	ctl = (unsigned)strtoul(argv[2], NULL, 10);
	want = (unsigned)strtoul(argv[3], NULL, 10);
	stride = (unsigned)strtoul(argv[4], NULL, 10);
	if (stride < 16) {
		fprintf(stderr, "stride must be >= 16\n");
		return 2;
	}
	win = (uint8_t *)malloc(stride);
	if (!win)
		return 2;
	for (i = 0; i < 8; i++)
		win[i] = (uint8_t)(((uint64_t)to_read >> (8 * i)) & 0xFF);
	win[8] = (uint8_t)(ctl & 0xFF);
	win[9] = (uint8_t)((ctl >> 8) & 0xFF);
	win[10] = (uint8_t)(want & 0xFF);
	win[11] = (uint8_t)((want >> 8) & 0xFF);
	/* the same deterministic payload controls/oracle.py generates */
	for (i = 12; i < stride; i++)
		win[i] = (uint8_t)((0xA5u + 7u * (i - 12u)) & 0xFFu);

	r = kernel(win, 0, (size_t)stride);
	printf("%llu\n", (unsigned long long)r);
	free(win);
	return 0;
}
