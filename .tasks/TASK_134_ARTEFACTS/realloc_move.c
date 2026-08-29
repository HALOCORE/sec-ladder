/* TASK_134 probe A2 -- DOES glibc's realloc EVER MOVE THE BLOCK HERE?
 *
 * Probe A found grows=4 moved=0 in a plain -O2 build and moved=4 under ASan.
 * If realloc never moves in the SHIPPED link mode, p25's stale pointer is
 * never stale in the shipped build and the harm is an ASan artefact.
 *
 * Four regimes, all doubling from CAP0=4:
 *   A  vector alone, at the top of the heap                (p25's shipped shape)
 *   B  a "pin" malloc taken right after vinit, so the vector is NOT at the top
 *   C  two vectors grown alternately (each pins the other)
 *   D  vector alone but grown past the 128 KiB mmap threshold
 *
 * Build + run: ./run.sh (this file is built by it)
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct { uint8_t *d; size_t n, cap; int grows, moved; } vec;

static void vinit(vec *v, size_t c0)
{ v->d = malloc(c0); if (!v->d) abort(); v->n = 0; v->cap = c0; v->grows = v->moved = 0; }

static void vgrow(vec *v)
{
    uint8_t *old = v->d, *nd = realloc(v->d, v->cap * 2);
    if (!nd) abort();
    v->grows++; if (nd != old) v->moved++;
    v->d = nd; v->cap *= 2;
}

int main(void)
{
    vec a, b, pin_v; void *pin; int i;

    /* A: alone at the top */
    vinit(&a, 4);
    for (i = 0; i < 12; i++) vgrow(&a);          /* 4 -> 16384 */
    printf("A alone            cap=%zu grows=%d moved=%d\n", a.cap, a.grows, a.moved);
    free(a.d);

    /* B: pinned by a later malloc */
    vinit(&b, 4);
    pin = malloc(64); if (!pin) abort();
    for (i = 0; i < 12; i++) vgrow(&b);
    printf("B pinned by malloc cap=%zu grows=%d moved=%d\n", b.cap, b.grows, b.moved);
    free(b.d); free(pin);

    /* C: two vectors alternately grown */
    { vec x, y; vinit(&x, 4); vinit(&y, 4);
      for (i = 0; i < 12; i++) { vgrow(&x); vgrow(&y); }
      printf("C two alternating x moved=%d/%d  y moved=%d/%d\n",
             x.moved, x.grows, y.moved, y.grows);
      free(x.d); free(y.d); }

    /* D: alone, past the 128 KiB mmap threshold */
    vinit(&pin_v, 4);
    for (i = 0; i < 20; i++) vgrow(&pin_v);      /* 4 -> 4 MiB */
    printf("D alone past mmap  cap=%zu grows=%d moved=%d\n",
           pin_v.cap, pin_v.grows, pin_v.moved);
    free(pin_v.d);
    return 0;
}
