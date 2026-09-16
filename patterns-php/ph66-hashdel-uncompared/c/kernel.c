/* ph66 rung R1 -- PHP 5.0.0's `Zend/zend_hash.c` container, VERBATIM.
 * THE BUG (corpus row LOGIC-001).
 *
 * ============================================================================
 * PROVENANCE
 * ============================================================================
 *   php-5.0.0.tar.gz  sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa
 *                            8f936dc6301d6919
 *   tar -xzOf <tarball> php-5.0.0/Zend/zend_hash.c | sed -n '450,503p'
 *   plus SEVEN more spans, every one pinned in ../spec.md's
 *   `provenance.extra_spans` and hashed the same way:
 *     Zend/zend_hash.h   :48-58   :243-271
 *     Zend/zend_hash.c   :24-42   :103-133   :135-174   :192-263   :339-402
 *                        :506-528
 *   Tier `verbatim`: the function bodies lift as-is. What comes off is
 *   `TSRMLS_*` plumbing, `ZEND_FILE_LINE_*`, the `ZEND_DEBUG` arms, the
 *   `persistent` arm of `pemalloc`/`pefree`, and the two interrupt macros --
 *   every one itemised individually with a line citation in ../spec.md's
 *   `provenance.divergences`.
 *
 * ============================================================================
 * THE DEFECT
 * ============================================================================
 * `zend_hash_del_key_or_index` settles a bucket's KEY KIND with a DISJUNCT:
 *
 *     if ((p->h == h) && ((p->nKeyLength == 0) ||        :464
 *         ((p->nKeyLength == nKeyLength) && ...)))       :465
 *
 * and a NUMERIC bucket has `nKeyLength == 0`, so for a numeric bucket the left
 * disjunct fires and `memcmp` is never reached. Hash equality alone stands in
 * for key identity.
 *
 * ⭐ IT IS THE ONLY ONE OF THE FILE'S TEN `p->h == h` PREDICATES THAT DOES
 * THIS, and it is also the only one that serves BOTH key kinds from one call
 * site (its `flag` parameter). The other nine are single-kind and already spell
 * the repair's required-conjunct form. `.tasks-php/probes/
 * ph66_djbx33a_collide.py` runs that census; ../NOTES.md section 5 reads it.
 *
 * ============================================================================
 * ⛔⛔ EVERY FREE BELOW IS A CORRECT FREE, AND THAT IS THE ROW
 * ============================================================================
 * `:466-489` unlinks the bucket from the bucket chain, from the global list AND
 * from `ht->pInternalPointer` BEFORE `pefree(p, ...)`; nothing holds it
 * afterwards. The harm is that the WRONG BUCKET was chosen, not that a freed
 * one is read. ../NOTES.md section 3.
 */
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "kernel.h"

#define PHP_SHIM_IMPL /* exactly one TU defines the allocator state */
#include "emalloc_shim.h"

/* Upstream's own type spellings, so the lifted bodies read as they do in the
 * tarball. `Zend/zend_types.h:25` `typedef unsigned char zend_bool;` and `:28`
 * `typedef unsigned long zend_ulong;`; `ulong`/`uint` reach zend_hash.c through
 * `Zend/zend_config.h`. Defined AFTER every system header so nothing is
 * re-typedef'd. */
#define ulong unsigned long
#define uint unsigned int
#define zend_bool unsigned char

/* `Zend/zend_alloc.h`'s pemalloc/pefree with `persistent == 0`, which is what
 * `array()` uses (`ZEND_INIT_SYMTABLE_EX(ht, 2, 0)`, zend_hash.h:287-288). */
#define pemalloc(n, persistent) php_shim_emalloc(n)
#define pemalloc_rel(n, persistent) php_shim_emalloc(n)
#define pefree(p, persistent) php_shim_efree(p)
#define pefree_rel(p, persistent) php_shim_efree(p)
#define ecalloc_rel(n, s) php_shim_ecalloc(n, s)

/* ZEND_DEBUG is 0 in the shipped build (zend_hash.c:44-72's `#else` arm). */
#define IS_CONSISTENT(a)
#define SET_INCONSISTENT(n)
/* Zend/zend.h:514-515 -- `if (zend_block_interruptions) { ... }`. The CLI SAPI
 * installs neither hook, so both are `if (NULL) {}`. Projected to nothing. */
#define HANDLE_BLOCK_INTERRUPTIONS()
#define HANDLE_UNBLOCK_INTERRUPTIONS()

/* ======================= Zend/zend_hash.h:48-58 ========================== */
typedef struct bucket {
	ulong h;						/* Used for numeric indexing */
	uint nKeyLength;
	void *pData;
	void *pDataPtr;
	struct bucket *pListNext;
	struct bucket *pListLast;
	struct bucket *pNext;
	struct bucket *pLast;
	char arKey[1]; /* Must be last element */
} Bucket;

typedef void (*dtor_func_t)(void *pDest);

/* ======================= Zend/zend_hash.h:60-78 ========================== */
typedef struct _hashtable {
	uint nTableSize;
	uint nTableMask;
	uint nNumOfElements;
	ulong nNextFreeElement;
	Bucket *pInternalPointer;	/* Used for element traversal */
	Bucket *pListHead;
	Bucket *pListTail;
	Bucket **arBuckets;
	dtor_func_t pDestructor;
	zend_bool persistent;
	unsigned char nApplyCount;
	zend_bool bApplyProtection;
} HashTable;

/* ⚠ `sizeof(Bucket) - 1` IS 71 ON LP64, AND `model.py`, all four Rust rungs and
 * `verus.rs` all hard-code that number as `BUCKET_BASE`. It decides the size
 * class every bucket request lands in, so a padding change on another ABI would
 * move the allocator tally and therefore the row's u64 -- silently. Held here at
 * COMPILE time instead: a negative array size is a build failure, not a
 * disagreement a reviewer has to notice. Same idiom as ph96's zval offsets. */
typedef char ph66_layout_assert[(sizeof(Bucket) - 1 == 71) ? 1 : -1];

/* ======================= Zend/zend_hash.h:243-271 ========================
 * `zend_inline_hash_func` -- DJBX33A accumulating in a `ulong`, i.e. 64-bit on
 * LP64. ⚠ `*arKey` is a PLAIN `char`, signed on x86-64; every byte this kernel
 * hashes is 'a'..'z' or NUL, so the sign never bites and every rung agrees.  */
static inline ulong zend_inline_hash_func(char *arKey, uint nKeyLength)
{
	register ulong hash = 5381;

	/* variant with the hash unrolled eight times */
	for (; nKeyLength >= 8; nKeyLength -= 8) {
		hash = ((hash << 5) + hash) + *arKey++;
		hash = ((hash << 5) + hash) + *arKey++;
		hash = ((hash << 5) + hash) + *arKey++;
		hash = ((hash << 5) + hash) + *arKey++;
		hash = ((hash << 5) + hash) + *arKey++;
		hash = ((hash << 5) + hash) + *arKey++;
		hash = ((hash << 5) + hash) + *arKey++;
		hash = ((hash << 5) + hash) + *arKey++;
	}
	switch (nKeyLength) {
		case 7: hash = ((hash << 5) + hash) + *arKey++; /* fallthrough... */
		case 6: hash = ((hash << 5) + hash) + *arKey++; /* fallthrough... */
		case 5: hash = ((hash << 5) + hash) + *arKey++; /* fallthrough... */
		case 4: hash = ((hash << 5) + hash) + *arKey++; /* fallthrough... */
		case 3: hash = ((hash << 5) + hash) + *arKey++; /* fallthrough... */
		case 2: hash = ((hash << 5) + hash) + *arKey++; /* fallthrough... */
		case 1: hash = ((hash << 5) + hash) + *arKey++; break;
		case 0: break;
	}
	return hash;
}

/* ======================= Zend/zend_hash.c:24-42 ========================== */
#define CONNECT_TO_BUCKET_DLLIST(element, list_head)		\
	(element)->pNext = (list_head);							\
	(element)->pLast = NULL;								\
	if ((element)->pNext) {									\
		(element)->pNext->pLast = (element);				\
	}

#define CONNECT_TO_GLOBAL_DLLIST(element, ht)				\
	(element)->pListLast = (ht)->pListTail;					\
	(ht)->pListTail = (element);							\
	(element)->pListNext = NULL;							\
	if ((element)->pListLast != NULL) {						\
		(element)->pListLast->pListNext = (element);		\
	}														\
	if (!(ht)->pListHead) {									\
		(ht)->pListHead = (element);						\
	}														\
	if ((ht)->pInternalPointer == NULL) {					\
		(ht)->pInternalPointer = (element);					\
	}

/* ====================== Zend/zend_hash.c:103-133 ========================= */
#define UPDATE_DATA(ht, p, pData, nDataSize)											\
	if (nDataSize == sizeof(void*)) {													\
		if (!(p)->pDataPtr) {															\
			pefree_rel((p)->pData, (ht)->persistent);										\
		}																				\
		memcpy(&(p)->pDataPtr, pData, sizeof(void *));									\
		(p)->pData = &(p)->pDataPtr;													\
	}

#define INIT_DATA(ht, p, pData, nDataSize);								\
	if (nDataSize == sizeof(void*)) {									\
		memcpy(&(p)->pDataPtr, pData, sizeof(void *));					\
		(p)->pData = &(p)->pDataPtr;									\
	}

/* ====================== Zend/zend_hash.c:135-174 ========================= */
static int _zend_hash_init(HashTable *ht, uint nSize, dtor_func_t pDestructor, zend_bool persistent)
{
	uint i = 3;
	Bucket **tmp;

	SET_INCONSISTENT(HT_OK);

	while ((1U << i) < nSize) {
		i++;
	}

	ht->nTableSize = 1 << i;
	ht->nTableMask = ht->nTableSize - 1;
	ht->pDestructor = pDestructor;
	ht->arBuckets = NULL;
	ht->pListHead = NULL;
	ht->pListTail = NULL;
	ht->nNumOfElements = 0;
	ht->nNextFreeElement = 0;
	ht->pInternalPointer = NULL;
	ht->persistent = persistent;
	ht->nApplyCount = 0;
	ht->bApplyProtection = 1;

	/* Uses ecalloc() so that Bucket* == NULL */
	tmp = (Bucket **) ecalloc_rel(ht->nTableSize, sizeof(Bucket *));
	if (tmp) {
		ht->arBuckets = tmp;
	}

	return SUCCESS;
}

/* ====================== Zend/zend_hash.c:192-263 =========================
 * `_zend_hash_add_or_update`. ⭐ ITS PREDICATE AT `:215` IS THE REPAIR'S OWN
 * FORM ALREADY -- `(p->h == h) && (p->nKeyLength == nKeyLength)`, a required
 * conjunct -- which is the census's point and this file's own counter-example
 * to "nobody knew".  */
static int _zend_hash_add_or_update(HashTable *ht, char *arKey, uint nKeyLength, void *pData, uint nDataSize, void **pDest, int flag)
{
	ulong h;
	uint nIndex;
	Bucket *p;

	IS_CONSISTENT(ht);

	if (nKeyLength <= 0) {
		return FAILURE;
	}

	h = zend_inline_hash_func(arKey, nKeyLength);
	nIndex = h & ht->nTableMask;

	p = ht->arBuckets[nIndex];
	while (p != NULL) {
		if ((p->h == h) && (p->nKeyLength == nKeyLength)) {
			if (!memcmp(p->arKey, arKey, nKeyLength)) {
				if (flag & HASH_ADD) {
					return FAILURE;
				}
				HANDLE_BLOCK_INTERRUPTIONS();
				if (ht->pDestructor) {
					ht->pDestructor(p->pData);
				}
				UPDATE_DATA(ht, p, pData, nDataSize);
				if (pDest) {
					*pDest = p->pData;
				}
				HANDLE_UNBLOCK_INTERRUPTIONS();
				return SUCCESS;
			}
		}
		p = p->pNext;
	}

	p = (Bucket *) pemalloc(sizeof(Bucket)-1+nKeyLength, ht->persistent);
	if (!p) {
		return FAILURE;
	}
	memcpy(p->arKey, arKey, nKeyLength);
	p->nKeyLength = nKeyLength;
	INIT_DATA(ht, p, pData, nDataSize);
	p->h = h;
	CONNECT_TO_BUCKET_DLLIST(p, ht->arBuckets[nIndex]);
	if (pDest) {
		*pDest = p->pData;
	}

	HANDLE_BLOCK_INTERRUPTIONS();
	CONNECT_TO_GLOBAL_DLLIST(p, ht);
	ht->arBuckets[nIndex] = p;
	HANDLE_UNBLOCK_INTERRUPTIONS();

	ht->nNumOfElements++;
	return SUCCESS;
}

/* ====================== Zend/zend_hash.c:339-402 =========================
 * `_zend_hash_index_update_or_next_insert`. ⭐⭐ `:356`'s predicate is
 * `(p->nKeyLength == 0) && (p->h == h)` -- a required conjunct again -- and
 * `:387` is where the NUMERIC MARKING is stated in upstream's own words. `p->h
 * = h` at `:388` stores THE RAW USER INDEX, which is what makes the collision
 * constructible forwards and needs no preimage. */
static int _zend_hash_index_update_or_next_insert(HashTable *ht, ulong h, void *pData, uint nDataSize, void **pDest, int flag)
{
	uint nIndex;
	Bucket *p;

	IS_CONSISTENT(ht);

	nIndex = h & ht->nTableMask;

	p = ht->arBuckets[nIndex];
	while (p != NULL) {
		if ((p->nKeyLength == 0) && (p->h == h)) {
			if (flag & HASH_ADD) {
				return FAILURE;
			}
			HANDLE_BLOCK_INTERRUPTIONS();
			if (ht->pDestructor) {
				ht->pDestructor(p->pData);
			}
			UPDATE_DATA(ht, p, pData, nDataSize);
			HANDLE_UNBLOCK_INTERRUPTIONS();
			if ((long)h >= (long)ht->nNextFreeElement) {
				ht->nNextFreeElement = h + 1;
			}
			if (pDest) {
				*pDest = p->pData;
			}
			return SUCCESS;
		}
		p = p->pNext;
	}
	p = (Bucket *) pemalloc_rel(sizeof(Bucket)-1, ht->persistent);
	if (!p) {
		return FAILURE;
	}
	p->nKeyLength = 0;			/*  Numeric indices are marked by making the nKeyLength == 0 */
	p->h = h;
	INIT_DATA(ht, p, pData, nDataSize);
	if (pDest) {
		*pDest = p->pData;
	}

	CONNECT_TO_BUCKET_DLLIST(p, ht->arBuckets[nIndex]);

	HANDLE_BLOCK_INTERRUPTIONS();
	ht->arBuckets[nIndex] = p;
	CONNECT_TO_GLOBAL_DLLIST(p, ht);
	HANDLE_UNBLOCK_INTERRUPTIONS();

	if ((long)h >= (long)ht->nNextFreeElement) {
		ht->nNextFreeElement = h + 1;
	}
	ht->nNumOfElements++;
	return SUCCESS;
}

/* ====================== Zend/zend_hash.c:450-503 =========================
 * ⚠⚠⚠ THE PRIMARY SPAN. `zend_hash_del_key_or_index`, unmodified.  */
static int zend_hash_del_key_or_index(HashTable *ht, char *arKey, uint nKeyLength, ulong h, int flag)
{
	uint nIndex;
	Bucket *p;

	IS_CONSISTENT(ht);

	if (flag == HASH_DEL_KEY) {
		h = zend_inline_hash_func(arKey, nKeyLength);
	}
	nIndex = h & ht->nTableMask;

	p = ht->arBuckets[nIndex];
	while (p != NULL) {
		if ((p->h == h) && ((p->nKeyLength == 0) || /* Numeric index */
			((p->nKeyLength == nKeyLength) && (!memcmp(p->arKey, arKey, nKeyLength))))) {
			HANDLE_BLOCK_INTERRUPTIONS();
			if (p == ht->arBuckets[nIndex]) {
				ht->arBuckets[nIndex] = p->pNext;
			} else {
				p->pLast->pNext = p->pNext;
			}
			if (p->pNext) {
				p->pNext->pLast = p->pLast;
			}
			if (p->pListLast != NULL) {
				p->pListLast->pListNext = p->pListNext;
			} else {
				/* Deleting the head of the list */
				ht->pListHead = p->pListNext;
			}
			if (p->pListNext != NULL) {
				p->pListNext->pListLast = p->pListLast;
			} else {
				ht->pListTail = p->pListLast;
			}
			if (ht->pInternalPointer == p) {
				ht->pInternalPointer = p->pListNext;
			}
			if (ht->pDestructor) {
				ht->pDestructor(p->pData);
			}
			if (!p->pDataPtr) {
				pefree(p->pData, ht->persistent);
			}
			pefree(p, ht->persistent);
			HANDLE_UNBLOCK_INTERRUPTIONS();
			ht->nNumOfElements--;
			return SUCCESS;
		}
		p = p->pNext;
	}
	return FAILURE;
}

/* ====================== Zend/zend_hash.c:506-528 ========================= */
static void zend_hash_destroy(HashTable *ht)
{
	Bucket *p, *q;

	IS_CONSISTENT(ht);

	SET_INCONSISTENT(HT_IS_DESTROYING);

	p = ht->pListHead;
	while (p != NULL) {
		q = p;
		p = p->pListNext;
		if (ht->pDestructor) {
			ht->pDestructor(q->pData);
		}
		if (!q->pDataPtr && q->pData) {
			pefree(q->pData, ht->persistent);
		}
		pefree(q, ht->persistent);
	}
	pefree(ht->arBuckets, ht->persistent);

	SET_INCONSISTENT(HT_DESTROYED);
}

/* ---- Zend/zend_hash.h:102-151, the four call-site macros the stream uses. -- */
#define zend_hash_update(ht, arKey, nKeyLength, pData, nDataSize, pDest) \
		_zend_hash_add_or_update(ht, arKey, nKeyLength, pData, nDataSize, pDest, HASH_UPDATE)
#define zend_hash_index_update(ht, h, pData, nDataSize, pDest) \
		_zend_hash_index_update_or_next_insert(ht, h, pData, nDataSize, pDest, HASH_UPDATE)
#define zend_hash_del(ht, arKey, nKeyLength) \
		zend_hash_del_key_or_index(ht, arKey, nKeyLength, 0, HASH_DEL_KEY)
#define zend_hash_index_del(ht, h) \
		zend_hash_del_key_or_index(ht, NULL, 0, h, HASH_DEL_INDEX)

/* ==========================================================================
 * THE PROJECTED DESTRUCTOR -- `ZVAL_PTR_DTOR`, i.e. `_zval_ptr_dtor`
 * ==========================================================================
 * `array()` installs `ZVAL_PTR_DTOR` (zend_hash.h:287-288). `_zval_ptr_dtor`
 * decrements the refcount and frees ONLY at zero (zend_execute_API.c:388-408),
 * which is exactly why this defect has no use-after-free variant: the last
 * holder's free is a correct free of a value nobody else names.
 *
 * Every payload in this kernel is held once, so the destructor's reachable
 * behaviour is "the value is destroyed now". It is projected to a COUNTER and a
 * FOLD -- which makes WHAT WAS DESTROYED observable in the u64, and that is the
 * half of the oracle the surviving-key fold cannot see. */
static uint64_t ph66_n_dtor;
static uint64_t ph66_dtor_fold;

static void ph66_zval_ptr_dtor(void *pDest)
{
	uint64_t v = (uint64_t)(uintptr_t)(*(void **)pDest);
	ph66_n_dtor++;
	ph66_dtor_fold = ph66_dtor_fold * 31u + (v & 0xFFFFu);
}

/* ==========================================================================
 * THE DRIVER OVER THE KEY STREAM
 * ==========================================================================
 * The record decode is stated in ../c/kernel.h; ../model.py carries a second
 * transcription of it. `key_of` is the only arithmetic here; everything else is
 * a call into the lifted container. */
static uint ph66_key_of(unsigned sel, char *out)
{
	uint kl = (uint)(1u + (sel % 7u));
	uint i;
	for (i = 0; i < kl; i++) {
		out[i] = (char)('a' + (int)(((sel / 7u) * 5u + i * 7u) % 26u));
	}
	out[kl] = '\0';
	return kl + 1; /* nKeyLength INCLUDES the NUL -- zend_execute.c:3612 */
}

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
	const uint8_t *win = buf + off;
	size_t nrec = len / PH66_REC;
	HashTable ht;
	Bucket *p;
	char key[PH66_KMAX + 2];
	size_t r;
	uint64_t acc = 0;
	uint64_t n_del_ok = 0, n_del_fail = 0, tally;

	php_shim_reset();
	ph66_n_dtor = 0;
	ph66_dtor_fold = 0;

	/* `array()` is `zend_hash_init(ht, 0, NULL, ZVAL_PTR_DTOR, 0)`; this kernel
	 * passes the record count instead, which is the `zend_hash_init(ht, n, ...)`
	 * spelling PHP uses wherever the size is known. It is what makes
	 * `nNumOfElements > nTableSize` unreachable and `zend_hash_do_resize` out of
	 * the extracted span -- ../spec.md `provenance.divergences`. */
	_zend_hash_init(&ht, (uint)nrec, ph66_zval_ptr_dtor, 0);

	for (r = 0; r < nrec; r++) {
		const uint8_t *b = win + r * PH66_REC;
		unsigned ctl = b[0];
		unsigned sel = b[1] & (PH66_NKEY - 1u);
		uint64_t val = (uint64_t)b[2] | ((uint64_t)b[3] << 8);
		void *data = (void *)(uintptr_t)(0x10000u | (unsigned)val);
		uint nkl = ph66_key_of(sel, key);
		int op = (int)(ctl & 1u);
		int kind = (int)((ctl >> 1) & 1u);
		int coll = (int)((ctl >> 2) & 1u);
		ulong idx = coll ? zend_inline_hash_func(key, nkl) : (ulong)b[1];
		int rc;

		if (op == 0) {
			if (kind == 0) {
				zend_hash_update(&ht, key, nkl, &data, sizeof(void *), NULL);
			} else {
				zend_hash_index_update(&ht, idx, &data, sizeof(void *), NULL);
			}
		} else {
			if (kind == 0) {
				rc = zend_hash_del(&ht, key, nkl);   /* ⚠⚠⚠ THE DEFECT'S CALL */
			} else {
				rc = zend_hash_index_del(&ht, idx);
			}
			if (rc == SUCCESS) {
				n_del_ok++;
			} else {
				n_del_fail++;
			}
		}
	}

	/* The fold, over the SURVIVING keys, in the global list's own order. */
	for (p = ht.pListHead; p != NULL; p = p->pListNext) {
		uint i;
		acc = acc * 31u + (uint64_t)p->nKeyLength;
		acc = acc * 31u + (uint64_t)p->h;
		for (i = 0; i < p->nKeyLength; i++) {
			acc = acc * 31u + (uint64_t)(unsigned char)p->arKey[i];
		}
		acc = acc * 31u + ((uint64_t)(uintptr_t)p->pDataPtr & 0xFFFFu);
	}
	acc = acc * 31u + (uint64_t)ht.nNumOfElements;
	acc = acc * 31u + (uint64_t)ht.nNextFreeElement;
	acc = acc * 31u + ph66_n_dtor;
	acc = acc * 31u + ph66_dtor_fold;
	acc = acc * 31u + n_del_ok;
	acc = acc * 31u + n_del_fail;

	tally = php_shim_tally();
	zend_hash_destroy(&ht);
	return acc ^ tally;
}
