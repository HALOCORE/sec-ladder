#include <stdio.h>
#include <stdlib.h>
__attribute__((noinline)) unsigned long kernel(const unsigned long *v, size_t n) {
    unsigned long acc = 0;
    for (size_t i = 0; i < n; i++) acc = acc + v[i];
    return acc;
}
int main(int argc, char **argv) {
    size_t n = argc - 1;
    unsigned long *v = malloc(n * sizeof *v);
    for (size_t i = 0; i < n; i++) v[i] = strtoul(argv[i + 1], 0, 10);
    printf("%lu\n", kernel(v, n));
}
