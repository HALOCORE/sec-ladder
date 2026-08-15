/* sec-ladder shared C driver helpers.
 *
 * What lives here: reading the input file (.memory/02-bench-rules.md format),
 * decoding the payload, and printing the checksum. What deliberately does NOT
 * live here: the driver *loop*. Rung 5's loop has to sit inside `verus!` so the
 * kernel call site is verified (.memory/02-bench-rules.md, "Proof domain must
 * cover the measured domain", rule 2), and a shared loop cannot be both plain
 * Rust and Verus. So every rung carries its own copy of the loop, delimited by
 * SLB-DRIVER-BEGIN / SLB-DRIVER-END markers, and harness/check.py diffs them.
 *
 * common/driver.rs is the line-for-line Rust mirror of this file. Exit codes and
 * stderr messages are part of the contract: the `adversarial` inputs compare
 * rung behaviour, so a divergence here would show up as a fake finding.
 */
#ifndef SLB_DRIVER_H
#define SLB_DRIVER_H

#include <stddef.h>
#include <stdint.h>

/* `isolated` build mode: kernel in its own TU, not inlined, no LTO. Defined by
 * harness/build.py as -DSLB_ISOLATED; the Rust mirror is --cfg slb_isolated. */
#ifdef SLB_ISOLATED
#define SLB_NOINLINE __attribute__((noinline))
#else
#define SLB_NOINLINE
#endif

/* Exit codes, shared with common/driver.rs. */
#define SLB_EXIT_USAGE 2     /* wrong argument count */
#define SLB_EXIT_OPEN 3      /* cannot open / stat the input file */
#define SLB_EXIT_HEADER 4    /* file shorter than the 16-byte header */
#define SLB_EXIT_TRUNCATED 5 /* payload_len declares more bytes than are present */
#define SLB_EXIT_NOMEM 6     /* allocation failed */

typedef struct {
    uint64_t n_iters;
    uint64_t payload_len; /* declared == present; slb_load rejects the mismatch */
    unsigned char *payload;
} slb_input;

/* argv[1] or exit(SLB_EXIT_USAGE). */
const char *slb_arg_path(int argc, char **argv);

/* Read `path` into `out`, or exit with one of the codes above. */
void slb_load(const char *path, slb_input *out);

/* Decode the payload as little-endian u64s: `*head` gets word 0, the return
 * value is a freshly allocated array of the remaining `*n_body` words. An empty
 * payload yields head 0, n_body 0, NULL. Mirrors driver::head_u64_body.
 *
 * The copy is deliberate: it gives the C rungs the same freshly-allocated,
 * naturally-aligned u64 array the Rust rungs get from `Vec<u64>`, so no rung
 * enjoys an alignment or aliasing advantage the others lack. */
uint64_t *slb_head_u64_body(const slb_input *in, uint64_t *head, size_t *n_body);

/* Print the checksum as a decimal u64 and a newline. Nothing else on stdout. */
void slb_emit(uint64_t acc);

#endif /* SLB_DRIVER_H */
