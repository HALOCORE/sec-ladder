#include <stdio.h>
#include <string.h>
static const char html_entity_chars[] = "#0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
static int range_pred(int c) {
    return c == 0 || c == '#' || (c >= '0' && c <= '9')
        || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
}
int main(void){
    int bad = 0, c;
    printf("expectation: strchr(s,0) is NON-NULL, and the range predicate agrees on all 256 bytes\n");
    printf("strchr(s,0) = %p (s = %p, s+strlen = %p)\n", (void*)strchr(html_entity_chars,0),
           (void*)html_entity_chars, (void*)(html_entity_chars+strlen(html_entity_chars)));
    for (c = 0; c < 256; c++) {
        int a = strchr(html_entity_chars, c) != NULL;
        int b = range_pred(c);
        if (a != b) { printf("  DISAGREE c=%d strchr=%d range=%d\n", c, a, b); bad++; }
    }
    printf("-> %s (%d disagreements over 256 byte values)\n", bad ? "FAIL" : "PASS", bad);
    /* must-fire: a predicate that forgets c==0 must disagree exactly once */
    { int d = 0; for (c = 0; c < 256; c++) { int a = strchr(html_entity_chars,c)!=NULL;
        int b = (c=='#'||(c>='0'&&c<='9')||(c>='a'&&c<='z')||(c>='A'&&c<='Z')); if (a!=b) d++; }
      printf("MUST-FIRE (predicate without the c==0 arm): %d disagreement(s), expected 1 -> %s\n",
             d, d == 1 ? "PASS" : "FAIL"); }
    return bad != 0;
}
