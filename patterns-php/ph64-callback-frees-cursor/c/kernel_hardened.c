/* ph64 rung R1h -- c/kernel.c PLUS `562f886ecb14` AND NOTHING ELSE.
 *
 * ============================================================================
 * WHAT R1h IS, AND WHERE IT LANDS
 * ============================================================================
 * `562f886ecb14` -- Antony Dovgal <tony2001@php.net>, 2007-04-10 09:37:09 +0000,
 * *"MFH: fix #41037 (unregister_tick_function() inside the tick function crash
 * PHP)"*. ONE hunk, 7 added / 2 deleted lines, in ONE function:
 * `user_tick_function_compare` (`ext/standard/basic_functions.c:2146-2161` at
 * 5.0.0). Three artefacts are INSIDE the commit: the bug number #41037 in the
 * subject, the NEWS line it adds, and the 23-line regression test
 * `ext/standard/tests/general_functions/bug41037.phpt` it adds --
 * `controls/bug41037.phpt` replays it. First tag carrying the guard: php-5.2.2
 * (absent at php-5.2.1), and the php-5.2.1 -> php-5.2.2 diff of the function IS
 * this hunk, line for line, so the window admits no second candidate.
 *
 * It applies to the PRISTINE 5.0.0 tarball with `patch -p1`, rc = 0, and the
 * result is byte-identical to php-5.2.2's function (body sha256
 * 4ae3d1c82072e782) -- 5.0.0's `user_tick_function_compare` is byte-identical
 * to php-5.2.1's. Backport cost: zero. `controls/562f886ecb14.patch` holds the
 * commit's bytes.
 *
 * ⚠⚠⚠ IT PATCHES NEITHER SITE. Not `Zend/zend_llist.c:190` (the loop that
 * reads the freed link -- this row's primary span, and never repaired at ANY
 * tag) and not `basic_functions.c:2135` (the corpus's cited line, the write
 * into the freed block -- untouched at php-5.2.2 and still there in master). It
 * makes the FREE UNREACHABLE from a third function instead, and both
 * dereferences survive verbatim. `grep -ac 'calling = 0'` over the 86-line
 * patch is 0.
 *
 * ⭐ AND UPSTREAM STRENGTHENED IT RATHER THAN REVERTING IT: the guard survives
 * into master, 18 years on, with `php_error_docref(E_WARNING)` upgraded to
 * `zend_throw_error(NULL, "Registered tick function cannot be unregistered
 * while it is being executed")`.
 *
 * ⚠⚠ THE ONE THING THE HUNK CARRIES THAT THIS RUNG DOES NOT: its refusal path
 * calls `php_error_docref(NULL TSRMLS_CC, E_WARNING, ...)`, and that reaches
 * `zend_error`'s user-handler arm -- i.e. ARBITRARY USERLAND -- from inside
 * `zend_llist_del_element`'s own `while` loop, which holds `current` and
 * `next`. This rung PROJECTS the warning to `ph64_refusals++`, and that
 * projection is the one whose `why` cannot end in "no semantics": it removes a
 * re-entry point the fix itself introduces. Stated at
 * `TASK_PHP_031_REPORT.md` §4.3 as a STATIC READING and NOT MEASURED; see
 * ../spec.md `provenance.divergences` and NOTES.md §4d. `zend_throw_error`
 * cannot run userland, which is a partial answer from upstream itself.
 *
 * ============================================================================
 * WHAT FOLLOWS IS c/kernel.c, UNCHANGED EXCEPT FOR THAT ONE HUNK
 * ============================================================================
 * The diff against c/kernel.c is: this header, `int ret;`, three assignments in
 * place of two `return`s and one fallthrough, and the five-line guard --
 * exactly the commit's shape. `controls/hunk_diff.py` re-derives it.
 *
 * ph64 rung R1 -- PHP 5.0.0's tick-function dispatch over `zend_llist_apply`,
 * NARROWED. THE BUG (corpus row CRASH-086).
 *
 * ============================================================================
 * PROVENANCE
 * ============================================================================
 *   php-5.0.0.tar.gz  sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa
 *                            8f936dc6301d6919
 *   tar -xzOf <tarball> php-5.0.0/Zend/zend_llist.c | sed -n '186,193p'
 *   -> sha256 fce26e38389ba9fb7909f94c7fcfaed8a48f7960ba92c6d132812a958c40e917
 *   plus TEN more spans, every one pinned in ../spec.md's
 *   `provenance.extra_spans` and hashed the same way:
 *     Zend/zend_llist.h            :25-29    :37-45
 *     Zend/zend_llist.c            :26-34    :37-52   :73-104  :107-121
 *     ext/standard/basic_functions.c
 *                                  :154-158  :2074-2082  :2102-2137
 *                                  :2139-2144 :2146-2161 :2799-2835 :2840-2862
 *   Tier `narrowed`: `Zend/zend_llist.{c,h}` lifts VERBATIM (only `TSRMLS_*`
 *   comes off and `pemalloc`/`pefree` redirect at the shim); the four
 *   `basic_functions.c` frames lose their zval WRAPPER and keep their body.
 *   Every divergence is itemised in ../spec.md's `provenance.divergences`,
 *   individually and with a line citation.
 *
 * ============================================================================
 * THE DEFECT, IN ONE LINE
 * ============================================================================
 * `zend_llist_apply` advances its cursor in the `for` header, AFTER the
 * callback has returned:
 *
 *     for (element=l->head; element; element=element->next)   <- :190  SITE L
 *         func(element->data);                                <- :191
 *
 * `func` here is `user_tick_function_call`, which runs USERLAND PHP, and
 * userland PHP can call `unregister_tick_function()` on itself. That reaches
 * `zend_llist_del_element` -> `DEL_LLIST_ELEMENT` -> `pefree(current)`, which
 * frees the very element `element` points at. Control then returns to
 * `user_tick_function_call`, which writes `tick_fe->calling = 0` into the freed
 * block (`basic_functions.c:2135`, SITE C, the corpus's cited line and the FIRST
 * fault), and then to the `for` header, which reads `element->next` out of it
 * and FOLLOWS it (SITE L).
 *
 * ⭐⭐ AND THE SAME FILE HAS THE DEFENCE, FIFTEEN LINES ABOVE.
 * `zend_llist_apply_with_del` (`:171-183`) takes the same caller-supplied
 * `func` and caches `next = element->next` at `:177` BEFORE calling it. Three
 * of `zend_llist.c`'s six callback-driven walks cache the successor
 * (`del_element`, `destroy`, `apply_with_del`) and three advance in the `for`
 * header (`apply`, `apply_with_argument`, `apply_with_arguments`) -- and the
 * three that do not are exactly the three this defect can reach. One file, one
 * author, one idiom written both ways. That asymmetry is this row's finding and
 * it needs no Rust and no ladder to state; `controls/next_cache.c` prices the
 * counterfactual against the real fix. NOTES.md §5.
 *
 * ⚠ AND `zend_llist_apply` IS NEVER REPAIRED. Its body's sha256 is identical at
 * twelve tags from php-5.0.0 to php-5.6.0 and differs at php-7.0.0 and master
 * only by the `TSRMLS_DC`/`TSRMLS_CC` deletion. Upstream closed the one exposure
 * instead: of `zend_llist_apply`'s eight 5.0.0 call sites, SEVEN cannot re-enter
 * userland, and the eighth is this one. NOTES.md §4.
 *
 * ============================================================================
 * WHAT NARROWING REMOVED, AND WHY NONE OF IT IS A SEMANTIC CHANGE
 * ============================================================================
 * 1. `TSRMLS_DC` / `TSRMLS_CC` / `TSRMLS_FETCH()` at five sites. Thread
 *    plumbing.
 * 2. `pemalloc`/`pefree` -> `php_shim_emalloc`/`php_shim_efree`. ⚠ Not a
 *    substitution of a DIFFERENT allocator: `register_tick_function:2823` passes
 *    `0` for `persistent`, so `pemalloc(n, 0)` IS `emalloc(n)` and
 *    `pefree(p, 0)` IS `efree(p)` (`Zend/zend_alloc.h`'s `pemalloc` macro), and
 *    `common-php/emalloc_shim.h` is 5.0.0's own `_emalloc`/`_efree` line-cited
 *    to the same tarball.
 * 3. `zval **arguments` -> an opaque 8-byte block holding the function NAME
 *    inline. PHP allocates `safe_emalloc(sizeof(zval*), arg_count, 0)` = 8 bytes
 *    for `arg_count == 1` and points it at a separately-allocated `zval` string;
 *    this kernel allocates the same 8 bytes and puts the name in them. The
 *    allocation the dtor frees, its size class, and therefore the whole cache
 *    behaviour are unchanged.
 * 4. `call_user_function(EG(function_table), NULL, function, &retval,
 *    arg_count - 1, arguments + 1)` (`:2111-2116`) -> a direct call to
 *    `ph64_userland`. That is the executor, and the row's whole point is what
 *    userland does to the list while the walk holds a cursor.
 * 5. The three `php_error_docref(E_WARNING)` arms at `:2118-2132` -- the
 *    `call_user_function == FAILURE` branch. `ph64_userland` always succeeds, so
 *    the arms are dead.
 * 6. `zend_binary_zval_strcmp(func1, func2)` -> an 8-byte binary compare, and
 *    the `Z_TYPE_P(...) == IS_ARRAY` arm of `user_tick_function_compare` is
 *    projected away: every name here is a string, which is the reachable arm.
 * 7. The zval unpack, `ZEND_NUM_ARGS`, `convert_to_string_ex`, the refcount
 *    bumps and the `BG(user_tick_functions)` lazy init in
 *    `PHP_FUNCTION(register_tick_function)` / `(unregister_tick_function)`.
 *    That is the wrapper, and removing a wrapper is what `narrowed` means.
 *
 * ============================================================================
 * WHAT IS *NOT* CHANGED, AND MUST NOT BE
 * ============================================================================
 *   * `for (element=l->head; element; element=element->next)` stays exactly
 *     that. Caching `next` before the callback -- which the same file does
 *     fifteen lines above -- DELETES THE ROW. `../spec.md`'s `forbidden[0]`
 *     pins it absent and `controls/next_cache.c` measures it as a control.
 *   * `DEL_LLIST_ELEMENT` keeps all four arms and its trailing `--l->count`.
 *   * `zend_llist_del_element` keeps `next = current->next` BEFORE the compare
 *     (`:97`). It is the walk §4.3's open item lives in, and it is the exact
 *     idiom `zend_llist_apply` does not use.
 *   * `user_tick_function_call` keeps its reentrancy guard `if (!tick_fe->
 *     calling)` (`:2108`) and both flag writes (`:2109`, `:2135`). `:2135` is
 *     SITE C and `:2109`/`:2135` are what make R1h's predicate true.
 *   * `user_tick_function_compare` reads `tick_fe1->arguments[0]` -- the LIST
 *     element -- and not `tick_fe2`'s. R1h's guard reads `tick_fe1->calling` for
 *     the same reason; `controls/predicate.py` measures what reading the other
 *     one would cost.
 */
#include <stdint.h>
#include <stddef.h>
#include <string.h>

#include "kernel.h"

#define PHP_SHIM_IMPL /* exactly one TU defines the allocator state */
#include "emalloc_shim.h"

/* `Zend/zend_alloc.h`'s pemalloc/pefree with `persistent == 0`. */
#define pemalloc(n, persistent) php_shim_emalloc(n)
#define pefree(p, persistent) php_shim_efree(p)
#define emalloc(n) php_shim_emalloc(n)
#define efree(p) php_shim_efree(p)

/* ======================= Zend/zend_llist.h:25-29 ========================= */
typedef struct _zend_llist_element {
	struct _zend_llist_element *next;
	struct _zend_llist_element *prev;
	char data[1]; /* Needs to always be last in the struct */
} zend_llist_element;

typedef void (*llist_dtor_func_t)(void *);
typedef void (*llist_apply_func_t)(void *);

/* ======================= Zend/zend_llist.h:37-45 ========================= */
typedef struct _zend_llist {
	zend_llist_element *head;
	zend_llist_element *tail;
	size_t count;
	size_t size;
	llist_dtor_func_t dtor;
	unsigned char persistent;
	zend_llist_element *traverse_ptr;
} zend_llist;

/* ================= ext/standard/basic_functions.c:154-158 ================ */
typedef struct _user_tick_function_entry {
	void *arguments;                /* zval **arguments, NARROWED */
	int arg_count;
	int calling;                    /* <- SITE C's target AND R1h's predicate */
} user_tick_function_entry;

/* The 8-byte `arguments` block -- `safe_emalloc(sizeof(zval *), 1, 0)` at
 * basic_functions.c:2811 -- holding the function NAME as `[u32 le id][u32 le
 * slot]`. The id half makes names unique BY CONSTRUCTION, so "unregister my own
 * name" cannot silently mean "unregister somebody else's" -- which is exactly
 * the way TASK_PHP_031's own first probe was wrong (its report §8.8). The slot
 * half is FOUR window bytes, so every byte of the window past the head is read
 * by exactly one entry and none is dead. */
#define PH64_NAME_BYTES 8
#define PH64_SLOT 4

/* ⚠⚠ THE LAYOUT IS LOAD-BEARING AND IT IS ASSERTED, NOT COMMENTED. The oracle
 * is `REAL_SIZE(sizeof(element) + sizeof(entry) - 1) >> 3 < MAX_CACHED_MEMORY`,
 * i.e. 40 >> 3 = 5 < 11, so a freed element is CACHED and its payload survives.
 * If any of these ever moved, the row would measure something else and say
 * nothing about it. */
typedef char ph64_layout_assert[
	(sizeof(zend_llist_element) == 24
	 && sizeof(user_tick_function_entry) == 16
	 && offsetof(zend_llist_element, next) == 0
	 && offsetof(zend_llist_element, data) == 16
	 && offsetof(user_tick_function_entry, calling) == 12) ? 1 : -1];

/* ======================= Zend/zend_llist.c:26-34 ========================= */
static void zend_llist_init(zend_llist *l, size_t size, llist_dtor_func_t dtor, unsigned char persistent)
{
	l->head  = NULL;
	l->tail  = NULL;
	l->count = 0;
	l->size  = size;
	l->dtor  = dtor;
	l->persistent = persistent;
}

/* ======================= Zend/zend_llist.c:37-52 ========================= */
static void zend_llist_add_element(zend_llist *l, void *element)
{
	zend_llist_element *tmp = pemalloc(sizeof(zend_llist_element)+l->size-1, l->persistent);

	tmp->prev = l->tail;
	tmp->next = NULL;
	if (l->tail) {
		l->tail->next = tmp;
	} else {
		l->head = tmp;
	}
	l->tail = tmp;
	memcpy(tmp->data, element, l->size);

	++l->count;
}

/* ======================= Zend/zend_llist.c:73-88 ========================= */
#define DEL_LLIST_ELEMENT(current, l) \
			if ((current)->prev) {\
				(current)->prev->next = (current)->next;\
			} else {\
				(l)->head = (current)->next;\
			}\
			if ((current)->next) {\
				(current)->next->prev = (current)->prev;\
			} else {\
				(l)->tail = (current)->prev;\
			}\
			if ((l)->dtor) {\
				(l)->dtor((current)->data);\
			}\
			pefree((current), (l)->persistent);\
			--l->count;

/* ======================= Zend/zend_llist.c:91-104 ======================== */
static void zend_llist_del_element(zend_llist *l, void *element, int (*compare)(void *element1, void *element2))
{
	zend_llist_element *current=l->head;
	zend_llist_element *next;

	while (current) {
		next = current->next;
		if (compare(current->data, element)) {
			DEL_LLIST_ELEMENT(current, l);
			break;
		}
		current = next;
	}
}

/* ====================== Zend/zend_llist.c:107-121 ======================== */
static void zend_llist_destroy(zend_llist *l)
{
	zend_llist_element *current=l->head, *next;

	while (current) {
		next = current->next;
		if (l->dtor) {
			l->dtor(current->data);
		}
		pefree(current, l->persistent);
		current = next;
	}

	l->count = 0;
}

/* ====================== Zend/zend_llist.c:186-193 ========================
 * ⚠⚠⚠ SITE L. THE PRIMARY SPAN. The cursor advances in the `for` header,
 * which runs AFTER `func` has returned -- and `func` was allowed to free
 * `element`. `zend_llist_apply_with_del` at `:171-183` caches `next` first;
 * this one does not, and never has at any tag. */
static void zend_llist_apply(zend_llist *l, llist_apply_func_t func)
{
	zend_llist_element *element;

	for (element=l->head; element; element=element->next) {
		func(element->data);
	}
}

/* ========================================================================= */
/* The projected userland, and the per-call state it needs. All of it is reset
 * by `ph64_reset()` at the top of every kernel call, beside `php_shim_reset()`
 * (PROTOCOL_PHP.md B1 rule 3). */

enum { PH64_UNREG_NONE = 0, PH64_UNREG_SELF, PH64_UNREG_AHEAD, PH64_UNREG_BEHIND };

static zend_llist  ph64_list;
static const uint8_t *ph64_win;   /* the window, for the name bytes */
static uint32_t ph64_n;           /* entries registered */
static uint32_t ph64_trigger;     /* which entry's callback acts, 0 = none */
static uint32_t ph64_mode;
static uint32_t ph64_reuse;
static uint64_t ph64_fold;        /* the names the walk actually visited */
static uint64_t ph64_visits;
static uint64_t ph64_dtors;
static uint64_t ph64_refusals;    /* R1h's projection of php_error_docref. In
                                   * R1 nothing ever writes it -- that IS the
                                   * hunk -- and both rungs fold it, so the two
                                   * kernels differ in the guard and in nothing
                                   * else. */
static void *ph64_reuse_block;

static void ph64_reset(void)
{
	ph64_n = 0; ph64_trigger = 0; ph64_mode = 0; ph64_reuse = 0;
	ph64_fold = 0; ph64_visits = 0; ph64_dtors = 0; ph64_refusals = 0;
	ph64_reuse_block = NULL;
}

static uint32_t ph64_rd32(const uint8_t *p)
{
	return (uint32_t)p[0] | ((uint32_t)p[1] << 8)
	     | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

/* the 8 name bytes of entry `id` (1-based), as PHP's `arguments[0]` string. */
static void ph64_name_of(uint32_t id, unsigned char *out)
{
	const uint8_t *src = ph64_win + 16 + (size_t)(id - 1) * PH64_SLOT;
	out[0] = (unsigned char)(id & 0xFF);
	out[1] = (unsigned char)((id >> 8) & 0xFF);
	out[2] = (unsigned char)((id >> 16) & 0xFF);
	out[3] = (unsigned char)((id >> 24) & 0xFF);
	out[4] = src[0]; out[5] = src[1]; out[6] = src[2]; out[7] = src[3];
}

/* ============ basic_functions.c:2146-2161  user_tick_function_compare =====
 * NARROWED: `zend_binary_zval_strcmp` becomes the 8-byte binary compare it is
 * on two equal-length strings, and the `IS_ARRAY` arm is projected away.
 * ⚠⚠ THIS IS THE ONE FUNCTION `562f886ecb14` TOUCHES, AND THE WHOLE DIFF
 * AGAINST c/kernel.c IS BELOW. */
static int user_tick_function_compare(void *a, void *b)
{
	user_tick_function_entry *tick_fe1 = (user_tick_function_entry *)a;
	user_tick_function_entry *tick_fe2 = (user_tick_function_entry *)b;
	const unsigned char *func1 = (const unsigned char *)tick_fe1->arguments;
	const unsigned char *func2 = (const unsigned char *)tick_fe2->arguments;
	int ret;                                           /* 562f886ecb14 + */
	int i, d = 0;

	for (i = 0; i < PH64_NAME_BYTES; i++) {
		if (func1[i] != func2[i]) { d = 1; break; }
	}
	ret = (d == 0);                                    /* 562f886ecb14 ~ */

	if (ret && tick_fe1->calling) {                    /* 562f886ecb14 + */
		/* PHP: php_error_docref(NULL TSRMLS_CC, E_WARNING,
		 *      "Unable to delete tick function executed at the moment");
		 * PROJECTED to a refusal counter. ⚠⚠ THIS PROJECTION REMOVES A
		 * USERLAND RE-ENTRY -- php_error_docref -> php_verror -> php_error ->
		 * zend_error's user-handler arm, reached from inside
		 * zend_llist_del_element's own walk. TASK_PHP_031_REPORT §4.3; it is a
		 * divergence whose `why` CANNOT end in "no semantics". */
		ph64_refusals++;
		return 0;                                      /* 562f886ecb14 */
	}
	return ret;                                        /* 562f886ecb14 + */
}

/* ============ basic_functions.c:2074-2082  user_tick_function_dtor ======== */
static void user_tick_function_dtor(void *p)
{
	user_tick_function_entry *tick_function_entry = (user_tick_function_entry *)p;

	ph64_dtors++;
	efree(tick_function_entry->arguments);
}

/* ============ basic_functions.c:2840-2862  unregister_tick_function ======
 * NARROWED to the four statements after the zval unpack. ⚠ `tick_fe.calling`
 * is NOT set here in PHP either -- the key's flag is indeterminate, and R1h's
 * guard reads `tick_fe1->calling`, the LIST element's, which is why that is
 * sound. This rung zeroes it so no rung reads an indeterminate `int`;
 * ../spec.md `provenance.divergences` and `controls/predicate.py`. */
static void ph64_unregister_tick_function(uint32_t id)
{
	user_tick_function_entry tick_fe;

	tick_fe.arguments = emalloc(PH64_NAME_BYTES);
	ph64_name_of(id, (unsigned char *)tick_fe.arguments);
	tick_fe.arg_count = 1;
	tick_fe.calling = 0;
	zend_llist_del_element(&ph64_list, &tick_fe, user_tick_function_compare);
	efree(tick_fe.arguments);
}

/* ============ basic_functions.c:2111-2116  call_user_function ============
 * PROJECTED to a direct call: this is the userland PHP a tick function runs.
 * It folds its own name, then does what the window told it to. */
static void ph64_userland(user_tick_function_entry *tick_fe)
{
	unsigned char nm[PH64_NAME_BYTES];
	uint32_t me;

	/* ⚠ The name is COPIED first, and that is not tidying. A PHP tick function
	 * holds its own name in the executor's frame, not in the tick entry -- and
	 * on the self-unregistration path `user_tick_function_dtor` `efree`s
	 * `tick_fe->arguments` before this function returns, so reading it after
	 * the switch would be a THIRD use-after-free that PHP does not have here.
	 * The row models the two dereferences the corpus names, not one it invents
	 * (PLAN_PHP.md §4.2). */
	memcpy(nm, tick_fe->arguments, PH64_NAME_BYTES);
	me = ph64_rd32(nm);

	ph64_fold = ph64_fold * 31 + (uint64_t)me;
	ph64_fold = ph64_fold * 31 + (uint64_t)ph64_rd32(nm + 4);
	ph64_visits++;

	if (me != ph64_trigger)
		return;

	switch (ph64_mode) {
	case PH64_UNREG_SELF:
		ph64_unregister_tick_function(me);
		break;
	case PH64_UNREG_AHEAD:
		if (me < ph64_n) ph64_unregister_tick_function(me + 1);
		break;
	case PH64_UNREG_BEHIND:
		if (me > 1) ph64_unregister_tick_function(me - 1);
		break;
	default:
		break;
	}

	if (ph64_reuse && ph64_reuse_block == NULL) {
		/* Exactly the request `zend_llist_add_element` makes, i.e. exactly the
		 * size class the freed element went into. Any ordinary small allocation
		 * inside a PHP tick function reaches this class. The block is filled
		 * with THIS ENTRY'S OWN NAME BYTES, repeated -- so on the reuse path
		 * the walk's next cursor is a value the WINDOW chose. */
		unsigned char *blk = (unsigned char *)emalloc(
			sizeof(zend_llist_element) + sizeof(user_tick_function_entry) - 1);
		size_t i;
		for (i = 0; i < sizeof(zend_llist_element)
		                + sizeof(user_tick_function_entry) - 1; i++)
			blk[i] = nm[i % PH64_NAME_BYTES];
		ph64_reuse_block = blk;
	}
}

/* ============ basic_functions.c:2102-2137  user_tick_function_call ========
 * ⚠⚠⚠ SITE C. `:2135` -- `tick_fe->calling = 0` -- is the corpus's cited
 * line and, on plain malloc/free under ASan, the FIRST faulting access
 * (`heap-use-after-free`, `WRITE of size 4`). The defect is one frame up. */
static void user_tick_function_call(void *p)
{
	user_tick_function_entry *tick_fe = (user_tick_function_entry *)p;

	/* Prevent reentrant calls to the same user ticks function */
	if (! tick_fe->calling) {
		tick_fe->calling = 1;                      /* :2109 */

		ph64_userland(tick_fe);                    /* :2111-2116 */

		tick_fe->calling = 0;                      /* :2135  <== SITE C */
	}
}

/* ============ basic_functions.c:2799-2835  register_tick_function =========
 * NARROWED to the entry construction: `calling = 0` (`:2804`), `arg_count`
 * (`:2805`), the `arguments` allocation (`:2811`) and the `add_element`
 * (`:2832`). */
static void ph64_register_tick_function(uint32_t id)
{
	user_tick_function_entry tick_fe;

	tick_fe.calling = 0;
	tick_fe.arg_count = 1;
	tick_fe.arguments = emalloc(PH64_NAME_BYTES);
	ph64_name_of(id, (unsigned char *)tick_fe.arguments);
	zend_llist_add_element(&ph64_list, &tick_fe);
}

/* ============ basic_functions.c:2139-2144  run_user_tick_functions ======== */
static void run_user_tick_functions(void)
{
	zend_llist_apply(&ph64_list, user_tick_function_call);   /* :2143 */
}

/* ========================================================================= */
/* The benchmark wrapper. It plays the part of one `php_run_ticks()` round
 * (`main/php_ticks.c:67-72`) over a tick list the window describes.
 *
 * `php_shim_reset()` at the top is PROTOCOL_PHP.md B1 rule 3 and is NOT
 * optional here for a second reason: the size-class cache IS this row's
 * oracle, so a cache that survived across driver iterations would make call N's
 * reuse depend on call N-1's frees. `php_shim_tally()` at the bottom is B1
 * rule 2 -- (n_alloc, n_free, n_cache_hit, bytes_mallocked) lands in the
 * checksum the gate compares across rungs, and it is HALF the R1-vs-R1h oracle:
 * R1 frees an element R1h refuses to free, so all four fields move.
 *
 * ⚠ The Rust rungs do not link the shim; they reproduce this tally
 * ARITHMETICALLY from the same allocation sequence. That is a pin on the
 * ALLOCATION SEQUENCE across rungs and it is NOT evidence that any Rust rung
 * ran PHP's allocator. ../spec.md and NOTES.md §7 say so in terms. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
	const uint8_t *win = buf + off;
	uint32_t nmax, nent_w, trig_w, mode_w, post_w, post;
	uint64_t acc, count_after;
	uint32_t i;

	php_shim_reset();
	ph64_reset();

	ph64_win = win;
	nmax   = (uint32_t)((len - 16) / PH64_SLOT);
	nent_w = ph64_rd32(win + 0);
	trig_w = ph64_rd32(win + 4);
	mode_w = ph64_rd32(win + 8);
	post_w = ph64_rd32(win + 12);

	ph64_n       = 1 + (nent_w % nmax);
	ph64_trigger = trig_w % (ph64_n + 1);
	ph64_mode    = mode_w % 4;
	ph64_reuse   = (mode_w >> 16) & 1;
	post         = post_w % (ph64_n + 1);

	zend_llist_init(&ph64_list, sizeof(user_tick_function_entry),
	                user_tick_function_dtor, 0);          /* :2822-2825 */
	for (i = 1; i <= ph64_n; i++)
		ph64_register_tick_function(i);

	run_user_tick_functions();                            /* the walk */

	if (post)
		ph64_unregister_tick_function(post);              /* top-level userland */

	count_after = (uint64_t)ph64_list.count;

	acc = ph64_fold;
	acc = acc * 31 + count_after;
	acc = acc * 31 + ph64_dtors;
	acc = acc * 31 + ph64_visits;
	acc = acc * 31 + ph64_refusals;
	acc = acc * 31 + (uint64_t)ph64_n;

	if (ph64_reuse_block)
		efree(ph64_reuse_block);
	zend_llist_destroy(&ph64_list);

	return acc ^ php_shim_tally();
}
