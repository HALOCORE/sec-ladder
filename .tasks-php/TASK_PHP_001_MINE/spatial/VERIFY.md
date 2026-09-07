# VERIFY — re-derivable pristine excerpts for the top 5 spatial candidates

Every block below is **actual output**, produced by the command shown immediately above it, from
the pristine tarball only:

```
T=/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
sha256sum $T
```
```
5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919  /home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
```

Set `T` as above once; every command below uses it. No patched tree was consulted.

---

## A. The `_emalloc` truncation (required for every CWE-190 answer)

### A1 — the truncating store and its consumption

```
tar -xzOf $T php-5.0.0/Zend/zend_alloc.c | sed -n '128,136p;146,148p;180,182p'
```
```c
#define DECLARE_CACHE_VARS()	\
	unsigned int real_size;		\
	unsigned int cache_index

#define REAL_SIZE(size) ((size+7) & ~0x7)

#define CALCULATE_REAL_SIZE_AND_CACHE_INDEX(size)	\
	real_size = REAL_SIZE(size);				\
	cache_index = real_size >> 3;
	TSRMLS_FETCH();

	CALCULATE_REAL_SIZE_AND_CACHE_INDEX(size);
		}
#endif
		p  = (zend_mem_header *) ZEND_DO_MALLOC(sizeof(zend_mem_header) + MEM_HEADER_PADDING + SIZE + END_MAGIC_SIZE);
```

Line map (the `sed` ranges are `128–136`, `146–148`, `180–182`, so the lines are exactly):
`:129 unsigned int real_size;` · `:132 #define REAL_SIZE(size) ((size+7) & ~0x7)` ·
`:135 real_size = REAL_SIZE(size);` · `:148 CALCULATE_REAL_SIZE_AND_CACHE_INDEX(size);` ·
`:182` the `ZEND_DO_MALLOC`. This matches CRASH-017's `c_file_line` (`:129 + :148 … :182`) exactly.

`_emalloc` is declared `ZEND_API void *_emalloc(size_t size ...)` — the parameter is 64-bit and
`real_size` is 32-bit. `emalloc(2^32)` therefore mallocs `sizeof(header) + PADDING + 0 + MAGIC`
and **returns a valid pointer to a header-sized block**.

### A2 — `safe_emalloc` checks in 64-bit and then calls the truncating `_emalloc`

```
tar -xzOf $T php-5.0.0/Zend/zend_alloc.c | sed -n '221,244p'
```
```c
ZEND_API void *_safe_emalloc(size_t nmemb, size_t size, size_t offset ZEND_FILE_LINE_DC ZEND_FILE_LINE_ORIG_DC)
{

	if (nmemb < LONG_MAX
			&& size < LONG_MAX
			&& offset < LONG_MAX
			&& nmemb >= 0
			&& size >= 0
			&& offset >= 0) {
		long lval;
		double dval;
		int use_dval;

		ZEND_SIGNED_MULTIPLY_LONG(nmemb, size, lval, dval, use_dval);

		if (!use_dval
				&& lval < (long) (LONG_MAX - offset)) {
			return emalloc_rel(lval + offset);
		}
	}

	zend_error(E_ERROR, "Possible integer overflow in memory allocation (%zd * %zd + %zd)", nmemb, size, offset);
	return 0;
}
```

**`safe_emalloc` does not protect against the truncation.** It validates the 64-bit product and
then hands it to `_emalloc`, which narrows it to 32 bits.

### A3 — a second truncation the brief does not mention: the recorded size is a 31-bit bitfield

```
tar -xzOf $T php-5.0.0/Zend/zend_alloc.h | sed -n '/typedef struct _zend_mem_header/,/} zend_mem_header/p'
```
```c
typedef struct _zend_mem_header {
#if ZEND_DEBUG
	long magic;
	char *filename;
	uint lineno;
	int reported;
	char *orig_filename;
	uint orig_lineno;
# ifdef ZTS
	THREAD_T thread_id;
# endif
#endif
#if ZEND_DEBUG || !defined(ZEND_MM)
    struct _zend_mem_header *pNext;
    struct _zend_mem_header *pLast;
#endif
	unsigned int size:31;
	unsigned int cached:1;
} zend_mem_header;
```

`p->size = size` (`zend_alloc.c`, both the cache branch and the fresh branch) stores into
`unsigned int size:31`, so the size recorded for later `free`/accounting is truncated to 31 bits
independently of the malloc path. That is a second, distinct violation of I11/O3.

**Bottom line for §4 of NOTES.md:** all 16 candidates are allocator-independent. Only CRASH-017
(rawurlencode) and CRASH-097 (`stream_socket_recvfrom`) depend on the truncation, and neither is
among the candidates.

---

## C1 — Candidate 1: `unserialize-lexer-limit-never-set` (CRASH-066)

### The no-op refill hook, at `var_unserializer.c:106`

```
tar -xzOf $T php-5.0.0/ext/standard/var_unserializer.c | sed -n '104,110p'
```
```c
/* }}} */

#define YYFILL(n) do { } while (0)
#define YYCTYPE unsigned char
#define YYCURSOR cursor
#define YYLIMIT limit
#define YYMARKER marker
```

### The true end of the buffer is a parameter — and is never compared to anything

```
tar -xzOf $T php-5.0.0/ext/standard/var_unserializer.c | grep -n 'max'
```
```
150:#define UNSERIALIZE_PARAMETER zval **rval, const char **p, const char *max, php_unserialize_data_t *var_hash TSRMLS_DC
151:#define UNSERIALIZE_PASSTHRU rval, p, max, var_hash TSRMLS_CC
160:		if (!php_var_unserialize(&key, p, max, NULL TSRMLS_CC)) {
168:		if (!php_var_unserialize(&data, p, max, var_hash TSRMLS_CC)) {
```

**Four occurrences in the whole file.** One declaration, one pass-through macro, two recursive
calls. `max` is never on the left or right of a comparison anywhere.

### The limit is initialised to the START of the buffer, at `:243`

```
tar -xzOf $T php-5.0.0/ext/standard/var_unserializer.c | sed -n '238,250p'
```
```c
PHPAPI int php_var_unserialize(UNSERIALIZE_PARAMETER)
{
	const unsigned char *cursor, *limit, *marker, *start;
	zval **rval_ref;

	limit = cursor = *p;
	
	if (var_hash && cursor[0] != 'R') {
		var_push(var_hash, rval);
	}

	start = cursor;

```

### The consequence: an unbounded `++YYCURSOR` walk with a dead limit test

```
tar -xzOf $T php-5.0.0/ext/standard/var_unserializer.c | sed -n '388,401p'
```
```c
	return 0; /* not sure if it should be 0 or 1 here? */
}
yy16:	yych = *++YYCURSOR;
	goto yy4;
yy17:	yych = *++YYCURSOR;
	if(yybm[0+yych] & 128)	goto yy19;
	if(yych != '+')	goto yy2;
	goto yy18;
yy18:	yych = *++YYCURSOR;
	if(yybm[0+yych] & 128)	goto yy19;
	goto yy2;
yy19:	++YYCURSOR;
	if(YYLIMIT == YYCURSOR) YYFILL(1);
	yych = *YYCURSOR;
```

`:390` is the `yy16:` line the corpus names as the OOB read site. `YYLIMIT == YYCURSOR` is true
only while `cursor == *p`, and `YYFILL` expands to nothing. **`ptr_cursor: true`** — 7 pointer
derefs with advance, 0 index expressions.

---

## C2 — Candidate 2: `uudecode-declared-length-drives-loop-bound` (CRASH-115)

```
tar -xzOf $T php-5.0.0/ext/standard/uuencode.c | sed -n '126,171p'
```
```c
PHPAPI int php_uudecode(char *src, int src_len, char **dest)
{
	int len, total_len=0;
	char *s, *e, *p, *ee;

	p = *dest = emalloc(ceil(src_len * 0.75) + 1);
	s = src;
	e = src + src_len;

	while (s < e) {
		if ((len = PHP_UU_DEC(*s++)) <= 0) {
			break;
		}
		total_len += len;

		ee = s + (len == 45 ? 60 : (int) floor(len * 1.33));

		while (s < ee) {
			*p++ = PHP_UU_DEC(*s) << 2 | PHP_UU_DEC(*(s + 1)) >> 4;
			*p++ = PHP_UU_DEC(*(s + 1)) << 4 | PHP_UU_DEC(*(s + 2)) >> 2;
			*p++ = PHP_UU_DEC(*(s + 2)) << 6 | PHP_UU_DEC(*(s + 3));
			s += 4;
		}

		if (len < 45) {
			break;
		}

		/* skip \n */
		s++;
	}

	if ((len = total_len > (p - *dest))) {
		*p++ = PHP_UU_DEC(*s) << 2 | PHP_UU_DEC(*(s + 1)) >> 4;
		if (len > 1) {
			*p++ = PHP_UU_DEC(*(s + 1)) << 4 | PHP_UU_DEC(*(s + 2)) >> 2;
			if (len > 2) {
				*p++ = PHP_UU_DEC(*(s + 2)) << 6 | PHP_UU_DEC(*(s + 3));
			}
		}
	}

	*(*dest + total_len) = '\0';

	return total_len;
}
```

Line map: `:131` the allocation · `:133` `e = src + src_len` (the true end) · **`:141`
`ee = s + (len == 45 ? 60 : (int) floor(len * 1.33));`** — the bound derived from the declared
length instead of from `e` · `:143-148` the read/write loop, which tests `s < ee` and never
`s < e` · `:158` the `=`-for-`==` boolean assignment that makes `:160`/`:162` dead · `:168` the
terminator write at the sum of the *declared* lengths.

The densest pointer-offset walk in the whole spatial set: **17** `*(s + n)` / `*p++` / `*s++`
forms, **0** `arr[i]` forms, four cursors (`s`, `e`, `p`, `ee`) and no index variable. `p` has no
companion end pointer, so the output cursor is unbounded.

---

## C3 — Candidate 3 and 7: `url-scheme-fixed-offset-peek` (CRASH-110) and `url-length-not-decremented-cursor-desync` (CRASH-073)

```
tar -xzOf $T php-5.0.0/ext/standard/url.c | sed -n '88,148p'
```
```c
	int length = strlen(str);
	char port_buf[6];
	php_url *ret = ecalloc(1, sizeof(php_url));
	char const *s, *e, *p, *pp, *ue;
		
	s = str;
	ue = s + length;

	/* parse scheme */
	if ((e = strchr(s, ':')) && (e-s)) {
		/* 
		 * certain schemas like mailto: and zlib: may not have any / after them
		 * this check ensures we support those.
		 */
		if (*(e+1) != '/') {
			/* check if the data we get is a port this allows us to 
			 * correctly parse things like a.com:80
			 */
			p = e + 1;
			while (isdigit(*p)) {
				p++;
			}
			
			if ((*p) == '\0' || *p == '/') {
				goto parse_port;
			}
			
			ret->scheme = estrndup(s, (e-s));
			php_replace_controlchars(ret->scheme);
			
			length -= ++e - s;
			s = e;
			goto just_path;
		} else {
			ret->scheme = estrndup(s, (e-s));
			php_replace_controlchars(ret->scheme);
		
			if (*(e+2) == '/') {
				s = e + 3;
				if (!strncasecmp("file", ret->scheme, sizeof("file"))) {
					if (*(e + 3) == '/') {
						/* support windows drive letters as in:
						   file:///c:/somedir/file.txt
						*/
						if (*(e + 5) == ':') {
							s = e + 4;
						}
						goto nohost;
					}
				}
			} else {
				s = e + 1;
				if (!strncasecmp("file", ret->scheme, sizeof("file"))) {
					goto nohost;
				} else {
					length -= ++e - s;
					s = e;
					goto just_path;
				}	
			}
		}
```

Line map: `:94 ue = s + length;` — the true end, **computed and then never used anywhere in this
block** · `:125 *(e+2)` · `:128 *(e+3)` · **`:132 if (*(e + 5) == ':')`** (CRASH-110) ·
`:139 s = e + 1;` · **`:143 length -= ++e - s;`** (CRASH-073) · `:144 s = e;`.

**CRASH-110.** For `parse_url("file:///")` — 8 bytes, a 9-byte NUL-terminated allocation — `e`
lands at index 4, `*(e+2)` and `*(e+3)` are the last `/` and the NUL, and `*(e+5)` is index **9**:
one byte past the end.

**CRASH-073.** Compare `:118` with `:143`. They are the *same statement*, `length -= ++e - s;`.
At `:118` it is correct, because `s` still holds the original start. At `:143` it is wrong,
because `:139` already set `s = e + 1` four lines earlier, so `++e - s == 0` and `length` is not
decremented at all. `just_path` then recomputes `ue = s + length` (`:167`) from the desynced pair,
placing `ue` past the true end, and `:292` does `estrndup(s, (ue-s))`. Confirm `:167` and `:292`:

```
tar -xzOf $T php-5.0.0/ext/standard/url.c | sed -n '165,168p;291,294p'
```
```c
	} else {
		just_path:
		ue = s + length;
		goto nohost;
	} else {
		ret->path = estrndup(s, (ue-s));
		php_replace_controlchars(ret->path);
	}
```

Both rows: **`ptr_cursor: true`** — five `char const *` cursors, 5 pointer-offset derefs against
2 index forms, and CRASH-073's defect *is* pointer arithmetic feeding a length variable.

---

## C4 — Candidate 4: `sprintf-appendstring-sizing-guard-defeated` (CRASH-001 + CRASH-011)

```
tar -xzOf $T php-5.0.0/ext/standard/formatted_print.c | sed -n '171,218p'
```
```c
inline static void
php_sprintf_appendstring(char **buffer, int *pos, int *size, char *add,
						   int min_width, int max_width, char padding,
						   int alignment, int len, int neg, int expprec, int always_sign)
{
	register int npad;
	int req_size;
	int copy_len;

	copy_len = (expprec ? MIN(max_width, len) : len);
	npad = min_width - copy_len;

	if (npad < 0) {
		npad = 0;
	}
	
	PRINTF_DEBUG(("sprintf: appendstring(%x, %d, %d, \"%s\", %d, '%c', %d)\n",
				  *buffer, *pos, *size, add, min_width, padding, alignment));

	req_size = *pos + MAX(min_width, copy_len) + 1;

	if (req_size > *size) {
		while (req_size > *size) {
			*size <<= 1;
		}
		PRINTF_DEBUG(("sprintf ereallocing buffer to %d bytes\n", *size));
		*buffer = erealloc(*buffer, *size);
	}
	if (alignment == ALIGN_RIGHT) {
		if ((neg || always_sign) && padding=='0') {
			(*buffer)[(*pos)++] = (neg) ? '-' : '+';
			add++;
			len--;
			copy_len--;
		}
		while (npad-- > 0) {
			(*buffer)[(*pos)++] = padding;
		}
	}
	PRINTF_DEBUG(("sprintf: appending \"%s\"\n", add));
	memcpy(&(*buffer)[*pos], add, copy_len + 1);
	*pos += copy_len;
	if (alignment == ALIGN_LEFT) {
		while (npad--) {
			(*buffer)[(*pos)++] = padding;
		}
	}
}
```

Line map: `:180 copy_len = (expprec ? MIN(max_width, len) : len);` ·
**`:190 req_size = *pos + MAX(min_width, copy_len) + 1;`** (CRASH-001's `c_file_line`) ·
`:192` the one and only guard · **`:207 (*buffer)[(*pos)++] = padding;`** (CRASH-001's sink) ·
**`:211 memcpy(&(*buffer)[*pos], add, copy_len + 1);`** (CRASH-011's `c_file_line` and sink).

The feeding narrowing — `strtol` returns `long`, the caller stores into `int`:

```
tar -xzOf $T php-5.0.0/ext/standard/formatted_print.c | sed -n '439,452p'
```
```c
inline static long
php_sprintf_getnumber(char *buffer, int *pos)
{
	char *endptr;
	register long num = strtol(&buffer[*pos], &endptr, 10);
	register int i = 0;

	if (endptr != NULL) {
		i = (endptr - &buffer[*pos]);
	}
	PRINTF_DEBUG(("sprintf_getnumber: number was %d bytes long\n", i));
	*pos += i;
	return num;
}
```

`:443` returns `long` from an unbounded `strtol`; the caller's `width`/`precision` are `int`
(`:483`), and the stores are at `:614` and `:626`.

**Two mechanisms, one guard.** CRASH-001: a near-INT_MAX `min_width` makes `:190` wrap negative,
`:192` is false, no grow, and the `:206-208` pad loop writes ~2^31 bytes. CRASH-011: the
`long`→`int` store makes `precision = INT_MIN`, so `:180` gives `copy_len = INT_MIN`, `npad` is
clamped to 0, `MAX(min_width, copy_len)` picks `min_width`, `:190` is *honestly small*, the guard
passes — and `:211` does `memcpy(dst, add, INT_MIN + 1)`, i.e. ~1.8e19 as `size_t`.

**Note for the density question.** `php_sprintf_appendstring` spans `:171–:218`. CRASH-149 is at
`:96`, inside `php_convert_to_decimal` (`:65–:155`); CRASH-016 is at `:599`, inside
`php_formatted_print` (`:478`–). **Four causes, three functions — not one function.**

---

## C5 — Candidate 5: `string-offset-signed-index-no-lower-bound` (CRASH-145)

```
tar -xzOf $T php-5.0.0/Zend/zend_execute.c | sed -n '4025,4038p'
```
```c
		} else if ((*container)->type == IS_STRING) { /* string offsets */
			switch (opline->extended_value) {
				case ZEND_ISSET:
					if (offset->value.lval <= Z_STRLEN_PP(container)) {
						result = 1;
					}
					break;
				case ZEND_ISEMPTY:
					if (offset->value.lval <= Z_STRLEN_PP(container) && Z_STRVAL_PP(container)[offset->value.lval] != '0') {
						result = 1;
					}
					break;
			}
		}
```

`:4033` is the `ZEND_ISEMPTY` line — matching CRASH-145's `c_file_line` exactly. `lval` is the
`long` field of a zval, so the guard `lval <= Z_STRLEN_PP(container)` has **no lower bound at
all** and `empty($s[-1000000])` indexes a megabyte before the buffer. The `<=` is also off by one
on the upper side; that half is masked by the zval's guaranteed NUL, which is why the lower-bound
hole survived.

Three lines, no arithmetic, no cursor, no allocation — the minimal spatial defect and the natural
floor of the ladder.

---

## D. The one correction that changes an analysis: CRASH-017 is **not** `emalloc(3 * len + 1)` in 5.0.0

The CRASH-017 reproducer comment says *"php-4.0.2:ext/standard/url.c:345: `str = emalloc(3 * len + 1);`
// int arith, with `register int x, y;` (url.c:342)"*. Pristine 5.0.0:

```
tar -xzOf $T php-5.0.0/ext/standard/url.c | sed -n '492,501p'
```
```c
/* {{{ php_raw_url_encode
 */
PHPAPI char *php_raw_url_encode(char const *s, int len, int *new_length)
{
	register int x, y;
	unsigned char *str;

	str = (unsigned char *) safe_emalloc(3, len, 1);
	for (x = 0, y = 0; len--; x++, y++) {
		str[y] = (unsigned char) s[x];
```

`:499` is **`safe_emalloc(3, len, 1)`**, not `emalloc(3 * len + 1)`. The 4.0.2 int overflow is
already fixed at 5.0.0. That is exactly why the corpus row's `c_file_line` points at
`Zend/zend_alloc.c:129 + :148 … :182` and its `history_status` is `fixed-by-rewrite`: on 5.0.0,
**the remaining defect is the allocator.**

Chain: `len = 1431655765` → `_safe_emalloc(3, len, 1)` computes `3*len + 1 = 4294967296` in
64-bit `long` (A2), which passes → `_emalloc(2^32)` → `real_size = (2^32 + 7) & ~7` truncated to
`unsigned int` = **0** (A1) → a header-sized malloc **succeeds** → the encode loop writes ~4.29e9
bytes into it.

**Substituting plain `malloc` inverts the result.** `malloc(4 GiB)` succeeds on a 64-bit Linux
with overcommit, the loop runs to completion, and the defect would be reported as unreachable.
This is the failure mode the brief describes.

---

## E. Citation corrections, re-derivable

### E1 — `var_unserializer.re` cross-references in CRASH-017's row drift by 5 and 6 lines

CSV claims `var_unserializer.c:243 … :106 == var_unserializer.re:243/:111`.

```
tar -xzOf $T php-5.0.0/ext/standard/var_unserializer.re | grep -n 'YYFILL(n)\|limit = cursor'
```
```
105:#define YYFILL(n) do { } while (0)
248:	limit = cursor = *p;
```
```
tar -xzOf $T php-5.0.0/ext/standard/var_unserializer.c | grep -n 'YYFILL(n)\|limit = cursor'
```
```
106:#define YYFILL(n) do { } while (0)
243:	limit = cursor = *p;
```

**The `.c` citations (`:243`, `:106`) are both correct. The `.re` cross-references are not:**
`limit = cursor` is at `.re:248` (claimed `:243`, +5) and `YYFILL` at `.re:105` (claimed `:111`,
−6). CRASH-120's `.c:208-210 == .re:213-215` mapping *is* exact, so the drift is specific to this
row.

### E2 — four entity tables are short, not the two the corpus records

```
tar -xzOf $T php-5.0.0/ext/standard/html.c | python3 -c "
import sys,re
src=sys.stdin.buffer.read().decode('latin-1')
seen=set()
for m in re.finditer(r'\{\s*cs_\w+,\s*((?:0x)?[0-9a-fA-F]+),\s*((?:0x)?[0-9a-fA-F]+),\s*(\w+)\s*\}',src):
    lo,hi,name=int(m.group(1),0),int(m.group(2),0),m.group(3)
    if (name,lo,hi) in seen: continue
    seen.add((name,lo,hi))
    t=re.search(r'static entity_table_t '+name+r'\[\] = \{(.*?)\n\};',src,re.S)
    if not t: continue
    body=re.sub(r'/\*.*?\*/','',t.group(1),flags=re.S)
    n=len([x for x in body.split(',') if x.strip()])
    need=hi-lo+1
    print('%-20s actual=%-4d declared %d..%d needs=%-4d %s'%(name,n,lo,hi,need,'SHORT by %d'%(need-n) if n<need else 'ok'))
"
```
```
ent_cp_1252          actual=32   declared 128..159 needs=32   ok
ent_iso_8859_1       actual=96   declared 160..255 needs=96   ok
ent_iso_8859_15      actual=96   declared 160..255 needs=96   ok
ent_uni_338_402      actual=63   declared 338..402 needs=65   SHORT by 2
ent_uni_spacing      actual=22   declared 710..732 needs=23   SHORT by 1
ent_uni_greek        actual=70   declared 913..982 needs=70   ok
ent_uni_punct        actual=66   declared 8194..8260 needs=67   SHORT by 1
ent_uni_euro         actual=1    declared 8364..8364 needs=1    ok
ent_uni_8465_8501    actual=37   declared 8465..8501 needs=37   ok
ent_uni_8592_9002    actual=410  declared 8592..9002 needs=411  SHORT by 1
ent_uni_9674         actual=1    declared 9674..9674 needs=1    ok
ent_uni_9824_9830    actual=7    declared 9824..9830 needs=7    ok
ent_koi8r            actual=93   declared 163..255 needs=93   ok
ent_cp_1251          actual=128  declared 128..255 needs=128  ok
ent_iso_8859_5       actual=64   declared 192..255 needs=64   ok
ent_cp_866           actual=64   declared 192..255 needs=64   ok
ent_macroman         actual=245  declared 11..255 needs=245  ok
```

The corpus records `ent_uni_338_402` (CRASH-089) and `ent_uni_punct` (CRASH-090). **`ent_uni_spacing`
and `ent_uni_8592_9002` are also short and are not in the corpus.** The counter is trustworthy
because it comes out **exactly right on 13 of 17 tables**, including three with hand-computed
non-obvious extents (245, 410, 128). Eyeball confirmation of the smallest new one:

```
tar -xzOf $T php-5.0.0/ext/standard/html.c | sed -n '128,136p'
```
```c
static entity_table_t ent_uni_spacing[] = {
	/* 710 */
	"circ",
	/* 711 - 731 */
	NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
	NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
	/* 732 */
	"tilde",
};
```

`"circ"` + 20 `NULL` + `"tilde"` = **22** entries. Note the author's own comment says
`/* 711 - 731 */` — that is **21** codepoints, and only 20 `NULL`s follow it. The declared range
and the read loop:

```
tar -xzOf $T php-5.0.0/ext/standard/html.c | sed -n '396,402p;894,906p'
```
```c
	{ cs_8859_15, 		0xa0, 0xff, ent_iso_8859_15 },
	{ cs_utf_8, 		0xa0, 0xff, ent_iso_8859_1 },
	{ cs_utf_8, 		338,  402,  ent_uni_338_402 },
	{ cs_utf_8, 		710,  732,  ent_uni_spacing },
	{ cs_utf_8, 		913,  982,  ent_uni_greek },
	{ cs_utf_8, 		8194, 8260, ent_uni_punct },
	{ cs_utf_8, 		8364, 8364, ent_uni_euro }, 
				continue;

			for (k = entity_map[j].basechar; k <= entity_map[j].endchar; k++) {
				unsigned char entity[32];
				int entity_length = 0;

				if (entity_map[j].table[k - entity_map[j].basechar] == NULL)
					continue;
			
				
				entity[0] = '&';
				entity_length = strlen(entity_map[j].table[k - entity_map[j].basechar]);
				strncpy(&entity[1], entity_map[j].table[k - entity_map[j].basechar], sizeof(entity) - 2);
```

`:399 { cs_utf_8, 710, 732, ent_uni_spacing }` declares 23 slots. `:896` walks `k` from 710 to
732 **inclusive** and indexes `table[k - basechar]` at `:900` and `:905`, so `k == 732` reads slot
22 of a 22-entry array — one `char *` past the end of the static object, which `:905` then passes
to `strlen()`. Same shape as CRASH-089 (`:398`, 63 entries for 65 slots) and CRASH-090 (`:401`,
66 for 67).
