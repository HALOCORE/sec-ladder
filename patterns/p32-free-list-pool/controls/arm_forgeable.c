/* p32 CONTROLS -- **the variant that was NOT shipped, and the measurement that
 * is the reason.**
 *
 * `TASK_143`'s admitted demonstration packed the handle into the OPERAND BYTE:
 * `h = a & (SLOTS-1)`, `g = a >> SLOTBITS`. The shipped rungs do not; they make
 * ALLOC issue the handle into a REGISTER and let the file name the register.
 * ../c/kernel.h and ../spec.md say why, and this file is the evidence:
 *
 *   **with a file-supplied handle the HARDENED kernel self-loops its own free
 *   list on an input of four operations**, because the attacker can always
 *   spell the CURRENT incarnation of a block that is already free, and
 *   `gen[h] == g` then passes on a block that is on the list.
 *
 * That is not a harder version of this row. It is a broken R1h, and the
 * admission bar's question 1 asks the C kernel to be correct on benign inputs
 * (`.memory/02-bench-rules.md`). Everything else about this file -- the LIFO
 * free list, the intrusive `nx[]`, the generation bumped on every free, the
 * fold -- is the shipped kernel's.
 *
 *   cc -std=c99 -O1 arm_forgeable.c && ./a.out
 *
 * It prints the slot each ALLOC returns under the HARDENED guard, walks the
 * free list with a visited set, and exits non-zero if the list is still simple
 * -- because if it is, this control has stopped demonstrating anything.
 */
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>

#define SLOTS 8
#define SLOTBITS 3
#define BLK 4
#define NIL 255
#define SENT 251

/* The HARDENED kernel of the file-supplied-handle variant: `gen[h] != g` is
 * present at the one site where a handle is consumed. This is R1h's spelling in
 * that design, not R1's. */
int main(void)
{
    uint8_t pool[SLOTS * BLK];
    uint8_t nx[SLOTS];
    uint32_t gen[SLOTS];
    uint8_t freehead = 0;
    size_t j;
    uint64_t acc = 0;
    int allocs[8];
    int nal = 0;
    /* (opcode, operand). Opcodes: 0 ALLOC, 1 FREE, 2 READ, 3 WRITE.
     * The operand IS the handle for 1/2/3: slot in the low 3 bits, generation
     * above. Four operations:
     *   ALLOC          -> slot 0 at generation 0, so the caller's handle is 0x00
     *   FREE  0x00     -> legitimate. gen[0] becomes 1 and slot 0 goes on the list
     *   FREE  0x08     -> h = 0, g = 1.  gen[0] IS 1, so THE HARDENED GUARD
     *                     PASSES, and `nx[0] = freehead` with `freehead == 0`
     *                     SELF-LOOPS the list
     *   ALLOC, ALLOC   -> both return slot 0: TWO LIVE HANDLES ALIAS ONE BLOCK */
    const uint8_t ops[][2] = {
        {0, 0x11}, {1, 0x00}, {1, 0x08}, {0, 0x22}, {0, 0x33},
    };
    const size_t nops = sizeof ops / sizeof ops[0];

    for (j = 0; j < SLOTS; j++) {
        nx[j] = (uint8_t)((j + 1 < SLOTS) ? (j + 1) : NIL);
        gen[j] = 0;
        pool[j * BLK] = 0;
        pool[j * BLK + 1] = 0;
        pool[j * BLK + 2] = 0;
        pool[j * BLK + 3] = 0;
    }

    for (j = 0; j < nops; j++) {
        uint8_t c = ops[j][0], a = ops[j][1];
        uint8_t h = (uint8_t)(a & (SLOTS - 1));
        uint32_t g = (uint32_t)(a >> SLOTBITS);
        if (c == 0) {
            if (freehead == NIL) {
                acc = acc * 31 + SENT;
                printf("  op%zu ALLOC   -> pool EXHAUSTED\n", j);
            } else {
                uint8_t s = freehead;
                freehead = nx[s];
                pool[(size_t)s * BLK + 1] = (uint8_t)(a * 7u + 1u);
                acc = acc * 31 + (uint64_t)s;
                if (nal < 8)
                    allocs[nal++] = s;
                printf("  op%zu ALLOC   -> slot %u  (handle would be "
                       "%u|gen %u)\n", j, s, s, gen[s]);
            }
        } else {
            /* THE HARDENED GUARD, present. */
            if (gen[h] != g) {
                acc = acc * 31 + SENT;
                printf("  op%zu op%u a=0x%02x -> REJECTED (gen[%u]=%u != g=%u)\n",
                       j, c, a, h, gen[h], g);
            } else if (c == 1) {
                gen[h] = gen[h] + 1;
                nx[h] = freehead;
                freehead = h;
                acc = acc * 31 + 1;
                printf("  op%zu FREE  a=0x%02x -> ACCEPTED: push slot %u, "
                       "nx[%u]=%u, freehead=%u%s\n", j, a, h, h, nx[h], freehead,
                       nx[h] == h ? "   <<< SELF-LOOP" : "");
            } else {
                acc = acc * 31 + (uint64_t)pool[(size_t)h * BLK + 1];
                printf("  op%zu READ  a=0x%02x -> ACCEPTED\n", j, a);
            }
        }
    }

    {
        /* Walk the free list with a visited set -- the property no rung ever
         * computes, and the one the shipped design keeps true. */
        uint8_t seen[SLOTS];
        uint8_t t = freehead;
        int simple = 1, alias = 0;
        int i;
        for (j = 0; j < SLOTS; j++)
            seen[j] = 0;
        while (t != NIL) {
            if (seen[t]) { simple = 0; break; }
            seen[t] = 1;
            t = nx[t];
        }
        for (i = 1; i < nal; i++)
            if (allocs[i] == allocs[i - 1])
                alias = 1;
        printf("\n  free list simple: %s\n", simple ? "YES" : "NO  <<< CYCLIC");
        printf("  two ALLOCs returned the same slot: %s\n",
               alias ? "YES <<< TWO LIVE HANDLES ALIAS ONE BLOCK" : "no");
        printf("  checksum %llu\n", (unsigned long long)acc);
        if (simple && !alias) {
            fprintf(stderr, "arm_forgeable: the HARDENED file-supplied-handle "
                            "kernel did NOT break, so this control no longer "
                            "demonstrates the reason the shipped design names a "
                            "REGISTER. Re-derive it before quoting NOTES.md 1b.\n");
            return 1;
        }
    }
    return 0;
}
