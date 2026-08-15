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
        size_t want = (size_t)out->payload_len;
        if ((uint64_t)want != out->payload_len) { /* 32-bit size_t guard */
            fprintf(stderr, "slb: %s: payload_len %" PRIu64 " exceeds size_t\n", path,
                    out->payload_len);
            fclose(f);
            exit(SLB_EXIT_TRUNCATED);
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

void slb_emit(uint64_t acc) { printf("%" PRIu64 "\n", acc); }
