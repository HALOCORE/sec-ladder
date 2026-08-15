/* sec-ladder shared C driver helpers -- see common/driver.h. */
#include "driver.h"

#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const char *slb_arg_path(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "usage: %s <input-file>\n", argc > 0 ? argv[0] : "prog");
        exit(SLB_EXIT_USAGE);
    }
    return argv[1];
}

static uint64_t slb_le64(const unsigned char *p)
{
    return (uint64_t)p[0] | ((uint64_t)p[1] << 8) | ((uint64_t)p[2] << 16) |
           ((uint64_t)p[3] << 24) | ((uint64_t)p[4] << 32) | ((uint64_t)p[5] << 40) |
           ((uint64_t)p[6] << 48) | ((uint64_t)p[7] << 56);
}

void slb_load(const char *path, slb_input *out)
{
    unsigned char header[16];
    FILE *f = fopen(path, "rb");
    if (!f) {
        fprintf(stderr, "slb: cannot open %s\n", path);
        exit(SLB_EXIT_OPEN);
    }
    if (fread(header, 1, sizeof header, f) != sizeof header) {
        fprintf(stderr, "slb: %s: short header\n", path);
        fclose(f);
        exit(SLB_EXIT_HEADER);
    }
    out->n_iters = slb_le64(header);
    out->payload_len = slb_le64(header + 8);

    /* Read exactly payload_len bytes and insist they were all there. This is the
     * "length field larger than the payload" adversarial case; a sloppy driver
     * would trust the field and read uninitialised memory. */
    out->payload = NULL;
    if (out->payload_len > 0) {
        long here, end;
        size_t want = (size_t)out->payload_len;
        if ((uint64_t)want != out->payload_len) { /* 32-bit size_t guard */
            fprintf(stderr, "slb: %s: payload_len %" PRIu64 " exceeds size_t\n", path,
                    out->payload_len);
            fclose(f);
            exit(SLB_EXIT_TRUNCATED);
        }
        /* Check the declared length against the bytes actually present BEFORE
         * allocating. Rust's driver::load does not allocate on the declared
         * length either (it read_to_end's and compares), so without this the two
         * languages diverge on a huge payload_len: C would fail the malloc and
         * exit SLB_EXIT_NOMEM (6) where Rust exits SLB_EXIT_TRUNCATED (5), and
         * an adversarial input would look like a rung difference when it is a
         * driver difference. (TASK_002_REVIEW, minors.) */
        here = ftell(f);
        if (here >= 0 && fseek(f, 0, SEEK_END) == 0) {
            end = ftell(f);
            if (fseek(f, here, SEEK_SET) != 0) {
                fprintf(stderr, "slb: %s: cannot seek\n", path);
                fclose(f);
                exit(SLB_EXIT_TRUNCATED);
            }
            if (end >= 0 && (uint64_t)(end - here) < out->payload_len) {
                fprintf(stderr, "slb: %s: payload_len %" PRIu64 " exceeds file size\n",
                        path, out->payload_len);
                fclose(f);
                exit(SLB_EXIT_TRUNCATED);
            }
        }
        out->payload = (unsigned char *)malloc(want);
        if (!out->payload) {
            fprintf(stderr, "slb: %s: out of memory for %zu payload bytes\n", path, want);
            fclose(f);
            exit(SLB_EXIT_NOMEM);
        }
        if (fread(out->payload, 1, want, f) != want) {
            fprintf(stderr, "slb: %s: payload_len %" PRIu64 " exceeds file size\n", path,
                    out->payload_len);
            fclose(f);
            exit(SLB_EXIT_TRUNCATED);
        }
    }
    fclose(f);
}

uint64_t *slb_head_u64_body(const slb_input *in, uint64_t *head, size_t *n_body)
{
    size_t nwords = (size_t)(in->payload_len / 8);
    size_t i;
    uint64_t *body;

    if (nwords == 0) {
        *head = 0;
        *n_body = 0;
        return NULL;
    }
    *head = slb_le64(in->payload);
    *n_body = nwords - 1;
    if (*n_body == 0)
        return NULL;
    body = (uint64_t *)malloc(*n_body * sizeof *body);
    if (!body) {
        fprintf(stderr, "slb: out of memory for %zu body words\n", *n_body);
        exit(SLB_EXIT_NOMEM);
    }
    for (i = 0; i < *n_body; i++)
        body[i] = slb_le64(in->payload + 8 + 8 * i);
    return body;
}

unsigned char *slb_head2_u64_bytes(const slb_input *in, uint64_t *h0, uint64_t *h1,
                                   size_t *n_body)
{
    size_t len = (size_t)in->payload_len;
    unsigned char *body;

    if (in->payload_len < 16) {
        *h0 = 0;
        *h1 = 0;
        *n_body = 0;
        return NULL;
    }
    *h0 = slb_le64(in->payload);
    *h1 = slb_le64(in->payload + 8);
    *n_body = len - 16;
    if (*n_body == 0)
        return NULL;
    body = (unsigned char *)malloc(*n_body);
    if (!body) {
        fprintf(stderr, "slb: out of memory for %zu body bytes\n", *n_body);
        exit(SLB_EXIT_NOMEM);
    }
    memcpy(body, in->payload + 16, *n_body);
    return body;
}

unsigned char *slb_zeroed(uint64_t cap)
{
    unsigned char *p;
    if (cap == 0 || cap > SLB_MAX_CAP) {
        fprintf(stderr, "slb: destination capacity %" PRIu64 " out of range (1..%" PRIu64 ")\n",
                cap, (uint64_t)SLB_MAX_CAP);
        exit(SLB_EXIT_CAP);
    }
    p = (unsigned char *)calloc((size_t)cap, 1);
    if (!p) {
        fprintf(stderr, "slb: out of memory for %" PRIu64 " destination bytes\n", cap);
        exit(SLB_EXIT_NOMEM);
    }
    return p;
}

void slb_emit(uint64_t acc) { printf("%" PRIu64 "\n", acc); }
