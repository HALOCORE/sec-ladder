/* maxfd_probe.c -- does an UNCLAMPED max_fd handed to select(2) touch memory
 * past the end of the caller's fd_set?
 *
 * Isolates limb #3 of PHP fix 99e290f882c9 (`PHP_SAFE_MAX_FD`) from limb #1
 * (`PHP_SAFE_FD_SET`, which is row ph16). PHP 5.0.0 does:
 *
 *     ext/sockets/sockets.c:635        select(max_fd+1, &rfds, &wfds, &efds, tv);
 *     ext/standard/streamsfuncs.c:706  php_select(max_fd+1, ...);
 *
 * where max_fd is the largest fd in a USERLAND-supplied array, unclamped.
 * Upstream clamps it to FD_SETSIZE-1 and warns.
 *
 * ⚠ THE ISOLATION IS THE POINT: only SMALL fds are ever FD_SET(). A big fd in
 * the set would be measuring ph16 instead.
 *
 * ================= THREE VERSIONS, TWO OF THEM WRONG =================
 * v1  opened 4 fds and swept nfds to 1048576. Everything came back INTACT and I
 *     nearly wrote down "the kernel is safe". Wrong: core_sys_select() does
 *         max_fds = fdt->max_fds;  if (n > max_fds) n = max_fds;
 *     so with 4 fds open the cap fires long before the buffer is approached.
 *     THE SETUP ENCODED THE ANSWER. v2 grows the fdtable first.
 * v2  grew the fdtable with dup()s of /dev/zero -- which are ALL READABLE. The
 *     canary bytes (0xA4) were therefore read as "fd requested", the fds were
 *     ready, and the kernel WROTE THE SAME BITS BACK. Bytes it had definitely
 *     written still compared equal, and printed INTACT. A SECOND setup that
 *     encoded the answer, in the probe written to avoid the first one.
 * v3  grows the fdtable with PIPE READ-ENDS, which are never ready, and arms the
 *     canary to 0xFF. Now every bit the kernel writes back must be CLEARED, so
 *     any byte it touches changes. The signal is unambiguous in both directions.
 * =====================================================================
 *
 *   gcc -O0 -Wall -o maxfd_probe maxfd_probe.c && ./maxfd_probe
 */
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>
#include <sys/time.h>
#include <unistd.h>

#define CANARY 0xFF     /* every bit SET: a not-ready fd must be cleared, so any
                         * byte the kernel writes back is guaranteed to change */
#define SLACK  4096
#define PIPES  2600     /* 2 fds each -> highest fd comfortably over FD_SETSIZE */

static long backing[(sizeof(fd_set) + SLACK) / sizeof(long) + 1];

static int canary_dirty(void)
{
    unsigned char *p = (unsigned char *)backing + sizeof(fd_set);
    for (int i = 0; i < SLACK; i++)
        if (p[i] != CANARY)
            return i;
    return -1;
}

static void arm(int small_fd)
{
    memset(backing, 0, sizeof(backing));
    memset((unsigned char *)backing + sizeof(fd_set), CANARY, SLACK);
    FD_SET(small_fd, (fd_set *)backing);   /* in-bounds: NOT ph16 */
}

int main(void)
{
    int small_fd = open("/dev/zero", O_RDONLY);   /* small + always readable */
    if (small_fd < 0) { perror("open /dev/zero"); return 2; }

    printf("FD_SETSIZE=%d  sizeof(fd_set)=%zu  small_fd=%d  canary=0x%02X x%d\n",
           FD_SETSIZE, sizeof(fd_set), small_fd, CANARY, SLACK);

    /* ---- MUST-FIRE (§H): prove the canary can go dirty at all ---------- */
    arm(small_fd);
    ((unsigned char *)backing)[sizeof(fd_set) + 7] ^= 0xFF;
    int mf = canary_dirty();
    printf("\nMUST-FIRE  scribble one byte at +7 past the fd_set -> %s\n",
           mf == 7 ? "DETECTED at +7  ✅ the canary works"
                   : "❌ THE PROBE IS BLIND -- do not believe anything below");
    if (mf != 7) return 3;

    /* ---- grow the fdtable with fds that are NEVER READY ----------------- */
    int held = 0, npipes = 0;
    for (int i = 0; i < PIPES; i++) {
        int fds[2];
        if (pipe(fds) < 0) break;
        held = fds[0] > fds[1] ? fds[0] : fds[1];
        npipes++;                       /* both ends stay open; read end never
                                         * becomes readable, nothing is written */
    }
    printf("grew the fdtable with %d pipes: highest fd %d  (need > %d)\n",
           npipes, held, FD_SETSIZE);
    if (held <= FD_SETSIZE) {
        fprintf(stderr, "aborting: fdtable did not pass FD_SETSIZE, so the "
                        "kernel's own cap would decide the sweep\n");
        return 3;
    }

    /* ---- MUST-NOT-FIRE: nfds that fits must never touch the canary ------ */
    { struct timeval tv = { 0, 0 };
      arm(small_fd);
      select(FD_SETSIZE, (fd_set *)backing, NULL, NULL, &tv);
      int d = canary_dirty();
      printf("MUST-NOT-FIRE  nfds=%d (exactly fills the set) -> %s\n",
             FD_SETSIZE, d < 0 ? "INTACT ✅" : "DIRTY ❌ THE PROBE OVER-REPORTS"); }

    /* ---- the sweep ------------------------------------------------------ */
    printf("\n%10s  %8s  %14s  %s\n", "nfds", "ret", "errno", "canary");
    int probes[] = { 64, 1023, 1024, 1025, 1032, 1088, 2048, 4096 };
    for (unsigned i = 0; i < sizeof(probes) / sizeof(probes[0]); i++) {
        int nfds = probes[i];
        struct timeval tv = { 0, 0 };
        arm(small_fd);
        errno = 0;
        int ret = select(nfds, (fd_set *)backing, NULL, NULL, &tv);
        int e = errno, d = canary_dirty();
        printf("%10d  %8d  %14s  %s", nfds, ret,
               ret < 0 ? strerror(e) : "-", d < 0 ? "INTACT" : "DIRTY");
        if (d >= 0)
            printf("  first at +%d past a %zu-byte set (nfds wants %d bytes)",
                   d, sizeof(fd_set), (nfds + 7) / 8);
        putchar('\n');
    }

    printf("\nnote: no fd >= FD_SETSIZE is ever FD_SET() here, so this says\n"
           "nothing about ph16. It measures ONLY the unclamped nfds limb.\n");
    return 0;
}
