/* ph64 control -- the C half of `controls/differential.py`. NOT a rung.
 *
 * ONE QUESTION: what u64 does ph64's kernel return for a window handed to it,
 * at R1 and at R1h?  `differential.py` drives it and compares against
 * `../model.py`'s TWO implementations, so that the shipped C and the reference
 * model are checked against each other over a domain `inputs/` cannot carry.
 *
 * It links the ROW's own `c/kernel.c` (R1) or `c/kernel_hardened.c` (R1h) and
 * supplies its own `main`, so `../c/main.c` is not used and the row's driver
 * loop is not involved.
 *
 * ⚠⚠ IT LIVES UNDER `controls/`, NOT UNDER `c/`, AND THAT IS DELIBERATE.
 * `harness/build.py` compiles exactly three translation units and everything
 * under `<row>/c/` is in the gate and measurement digests; a fourth `main` in
 * there would be compiled into the row. `PROTOCOL_PHP.md` §B3a: only `c/`,
 * `inputs/` and `controls/` may exist, and only `c/` is built.
 *
 * Windows come from stdin as hex, one per line:  <stride> <hexbytes>
 * Output:  <stride> <u64>            or          <stride> CRASH <signal>
 *
 * Each window runs in a FORKED CHILD so a SEGV is a reported outcome and not a
 * probe abort -- the fault is the result (TASK_PHP_031's oracle_probe shape).
 *
 * built by `controls/differential.py`; it is not on any build path.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/wait.h>

#include "../c/kernel.h"

static int hexval(int c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

int main(void)
{
    char line[1 << 16];
    while (fgets(line, sizeof line, stdin)) {
        unsigned long stride;
        char *p = line;
        unsigned char *buf;
        size_t n = 0;
        int fd[2], st;
        pid_t pid;
        uint64_t r = 0;

        stride = strtoul(p, &p, 10);
        while (*p == ' ') p++;
        buf = malloc(stride ? stride : 1);
        while (hexval((unsigned char)p[0]) >= 0 && hexval((unsigned char)p[1]) >= 0
               && n < stride) {
            buf[n++] = (unsigned char)(hexval((unsigned char)p[0]) * 16
                                       + hexval((unsigned char)p[1]));
            p += 2;
        }
        if (n != stride) { printf("%lu BADLINE %zu\n", stride, n); free(buf); continue; }

        if (pipe(fd)) { perror("pipe"); return 2; }
        pid = fork();
        if (pid == 0) {
            uint64_t v = kernel(buf, 0, (size_t)stride);
            ssize_t w = write(fd[1], &v, sizeof v);
            _exit(w == (ssize_t)sizeof v ? 0 : 2);
        }
        close(fd[1]);
        {
            ssize_t got = read(fd[0], &r, sizeof r);
            close(fd[0]);
            waitpid(pid, &st, 0);
            if (got != (ssize_t)sizeof r || WIFSIGNALED(st))
                printf("%lu CRASH %d\n", stride,
                       WIFSIGNALED(st) ? WTERMSIG(st) : -1);
            else
                printf("%lu %llu\n", stride, (unsigned long long)r);
        }
        fflush(stdout);
        free(buf);
    }
    return 0;
}
