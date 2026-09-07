# VERIFY.md — pristine excerpts for the top 5 TEMPORAL candidates

Single citation base:
```
TB=/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
# sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919  /home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
# bytes  5595997
```

Every block below was produced by running the command shown, in this shell, against that tarball.
Line numbers are added by the `awk` suffix and are the true 1-based line numbers of the pristine file.

---

## Rank 1 — `argstack-realloc-invalidates-borrowed-arg-slot` (CRASH-155 · CRASH-075 · CRASH-081 · CRASH-083 · CRASH-117)

**The growth site.** `erealloc` doubles `elements`; only the stack's own `top_element` is fixed up. Every `zval **` any caller obtained from `zend_get_parameters_ex` points into the old block and is now dangling.

```
tar -xzOf $TB php-5.0.0/Zend/zend_ptr_stack.h | sed -n '44,52p'
```

```c
  44  static inline void zend_ptr_stack_push(zend_ptr_stack *stack, void *ptr)
  45  {
  46  	if (stack->top >= stack->max) {		/* we need to allocate more memory */
  47  		stack->elements = (void **) erealloc(stack->elements, (sizeof(void *) * (stack->max *= 2 )));
  48  		stack->top_element = stack->elements+stack->top;
  49  	}
  50  	stack->top++;
  51  	*(stack->top_element++) = ptr;
  52  }
```

---

## Rank 1 (cont.) — the deref, CRASH-155

`obj` is an argument-stack-resident `zval **`. `zend_lookup_class` at :615 runs userland `__autoload`, whose nested calls push args and grow the stack. :619 / :621 then dereference `obj`.

```
tar -xzOf $TB php-5.0.0/Zend/zend_builtin_functions.c | sed -n '605,624p'
```

```c
 605  		RETURN_FALSE;
 606  	}
 607  	
 608  	/* TBI!! new object handlers */
 609  	if (!HAS_CLASS_ENTRY(**obj)) {
 610  		RETURN_FALSE;
 611  	}
 612  
 613  	convert_to_string_ex(class_name);
 614  
 615  	if (zend_lookup_class(Z_STRVAL_PP(class_name), Z_STRLEN_PP(class_name), &ce TSRMLS_CC) == FAILURE) {
 616  		retval = 0;
 617  	} else {
 618  		if (only_subclass) {
 619  			instance_ce = Z_OBJCE_PP(obj)->parent;
 620  		} else {
 621  			instance_ce = Z_OBJCE_PP(obj);
 622  		}
 623  
 624  		if (!instance_ce) {
```

---

## Rank 2 — `objstore-realloc-invalidates-cached-bucket-ptr` (CRASH-046)

`obj` is cached at :132. The userland destructor at :144 can call `zend_objects_store_put`, which ereallocs `object_buckets` (see next block). :147 then **reads** and :156 **writes** through the stale `obj`.

```
tar -xzOf $TB php-5.0.0/Zend/zend_objects_API.c | sed -n '129,165p'
```

```c
 129  ZEND_API void zend_objects_store_del_ref(zval *zobject TSRMLS_DC)
 130  {
 131  	zend_object_handle handle = Z_OBJ_HANDLE_P(zobject);
 132  	struct _store_object *obj = &EG(objects_store).object_buckets[handle].bucket.obj;
 133  	
 134  	/*	Make sure we hold a reference count during the destructor call
 135  		otherwise, when the destructor ends the storage might be freed
 136  		when the refcount reaches 0 a second time
 137  	*/
 138  	if (EG(objects_store).object_buckets[handle].valid) {
 139  		if (obj->refcount == 1) {
 140  			if (!EG(objects_store).object_buckets[handle].destructor_called) {
 141  				EG(objects_store).object_buckets[handle].destructor_called = 1;
 142  
 143  				if (obj->dtor) {
 144  					obj->dtor(obj->object, handle TSRMLS_CC);
 145  				}
 146  			}
 147  			if (obj->refcount == 1) {
 148  				if (obj->free_storage) {
 149  					obj->free_storage(obj->object TSRMLS_CC);
 150  				}
 151  				ZEND_OBJECTS_STORE_ADD_TO_FREE_LIST();
 152  			}
 153  		}
 154  	}
 155  
 156  	obj->refcount--;
 157  
 158  #if ZEND_DEBUG_OBJECTS
 159  	if (obj->refcount == 0) {
 160  		fprintf(stderr, "Deallocated object id #%d\n", handle);
 161  	} else {
 162  		fprintf(stderr, "Decreased refcount of object id #%d\n", handle);
 163  	}
 164  #endif
 165  }
```

---

## Rank 2 (cont.) — the growth site

`EG(objects_store).object_buckets` is ereallocd at :93 when `top == size`. The store is initialised with 1024 slots at `Zend/zend_execute_API.c:174`.

```
tar -xzOf $TB php-5.0.0/Zend/zend_objects_API.c | sed -n '82,99p'
```

```c
  82  ZEND_API zend_object_handle zend_objects_store_put(void *object, zend_objects_store_dtor_t dtor, zend_objects_free_object_storage_t free_storage, zend_objects_store_clone_t clone TSRMLS_DC)
  83  {
  84  	zend_object_handle handle;
  85  	struct _store_object *obj;
  86  	
  87  	if (EG(objects_store).free_list_head != -1) {
  88  		handle = EG(objects_store).free_list_head;
  89  		EG(objects_store).free_list_head = EG(objects_store).object_buckets[handle].bucket.free_list.next;
  90  	} else {
  91  		if (EG(objects_store).top == EG(objects_store).size) {
  92  			EG(objects_store).size <<= 1;
  93  			EG(objects_store).object_buckets = (zend_object_store_bucket *) erealloc(EG(objects_store).object_buckets, EG(objects_store).size * sizeof(zend_object_store_bucket));
  94  		}
  95  		handle = EG(objects_store).top++;
  96  	}
  97  	obj = &EG(objects_store).object_buckets[handle].bucket.obj;
  98  	EG(objects_store).object_buckets[handle].destructor_called = 0;
  99  	EG(objects_store).object_buckets[handle].valid = 1;
```

---

## Rank 3 — `hash-cursor-freed-under-traversal` (CRASH-002 · CRASH-022 · CRASH-040): the cursor type

`HashPosition` is not an index. It is a bare `Bucket *`, so `zend_hash_move_forward_ex` advances by dereferencing a pointer the table is free to have pefreed.

```
tar -xzOf $TB php-5.0.0/Zend/zend_hash.h | sed -n '86,90p'
```

```c
  86  typedef zend_bool (*merge_checker_func_t)(HashTable *target_ht, void *source_data, zend_hash_key *hash_key, void *pParam);
  87  
  88  typedef Bucket* HashPosition;
  89  
  90  BEGIN_EXTERN_C()
```

---

## Rank 3 (cont.) — the driver, CRASH-002

`pos` is live across `zend_call_function` at :1045. A callback that unsets the current element pefrees that Bucket; :1062 then reads `pListNext` out of it.

```
tar -xzOf $TB php-5.0.0/ext/standard/array.c | sed -n '1007,1063p'
```

```c
1007  	zend_hash_internal_pointer_reset_ex(target_hash, &pos);
1008  
1009  	/* Iterate through hash */
1010  	while (zend_hash_get_current_data_ex(target_hash, (void **)&args[0], &pos) == SUCCESS) {
1011  		if (recursive && Z_TYPE_PP(args[0]) == IS_ARRAY) {
1012  			HashTable *thash;
1013  			
1014  			thash = HASH_OF(*(args[0]));
1015  			if (thash == target_hash) {
1016  				php_error_docref(NULL TSRMLS_CC, E_WARNING, "recursion detected");
1017  				return 0;
1018  			}
1019  			php_array_walk(thash, userdata, recursive TSRMLS_CC);
1020  		} else {
1021  			zend_fcall_info fci;
1022  
1023  			/* Allocate space for key */
1024  			MAKE_STD_ZVAL(key);
1025  
1026  			/* Set up the key */
1027  			if (zend_hash_get_current_key_ex(target_hash, &string_key, &string_key_len, &num_key, 0, &pos) == HASH_KEY_IS_LONG) {
1028  				Z_TYPE_P(key) = IS_LONG;
1029  				Z_LVAL_P(key) = num_key;
1030  			} else {
1031  				ZVAL_STRINGL(key, string_key, string_key_len-1, 1);
1032  			}
1033  
1034  			fci.size = sizeof(fci);
1035  			fci.function_table = EG(function_table);
1036  			fci.function_name = *BG(array_walk_func_name);
1037  			fci.symbol_table = NULL;
1038  			fci.object_pp = NULL;
1039  			fci.retval_ptr_ptr = &retval_ptr;
1040  			fci.param_count = userdata ? 3 : 2;
1041  			fci.params = args;
1042  			fci.no_separation = 0;
1043  
1044  			/* Call the userland function */
1045  			if (zend_call_function(&fci, &BG(array_walk_fci_cache) TSRMLS_CC) == SUCCESS) {
1046  				zval_ptr_dtor(&retval_ptr);
1047  			} else {
1048  				char *func_name;
1049  
1050  				if (zend_is_callable(*BG(array_walk_func_name), 0, &func_name)) {
1051  					php_error_docref(NULL TSRMLS_CC, E_WARNING, "Unable to call %s()", func_name);
1052  				} else {
1053  					php_error_docref(NULL TSRMLS_CC, E_WARNING, "Unable to call %s() - function does not exist", func_name);
1054  				}
1055  
1056  				efree(func_name);
1057  				break;
1058  			}
1059  		}
1060  
1061  		zval_ptr_dtor(&key);
1062  		zend_hash_move_forward_ex(target_hash, &pos);
1063  	}
```

---

## Rank 4 — `unserialize-backref-table-holds-freed-zval` (CRASH-121)

`zval_ptr_dtor(rval)` at :887 releases a zval that is **still an entry in `var_hash`**; `rval_ref` can be that entry, so :890 increments a refcount inside freed storage. Identical text at `var_unserializer.re:292-296`.

```
tar -xzOf $TB php-5.0.0/ext/standard/var_unserializer.c | sed -n '874,894p'
```

```c
 874  yy88:
 875  {
 876  	int id;
 877  
 878   	*p = YYCURSOR;
 879  	if (!var_hash) return 0;
 880  
 881  	id = parse_iv(start + 2) - 1;
 882  	if (id == -1 || var_access(var_hash, id, &rval_ref) != SUCCESS) {
 883  		return 0;
 884  	}
 885  
 886  	if (*rval != NULL) {
 887  		zval_ptr_dtor(rval);
 888  	}
 889  	*rval = *rval_ref;
 890  	(*rval)->refcount++;
 891  	(*rval)->is_ref = 0;
 892  	
 893  	return 1;
 894  }
```

---

## Rank 5 — `hash-del-numeric-bucket-shortcircuits-key-compare` (LOGIC-001)

`(p->nKeyLength == 0)` is a **left disjunct**: for a numeric bucket the key is never compared at all, so a string-key delete whose `zend_inline_hash_func` collides with an existing integer index destroys that unrelated live element.

```
tar -xzOf $TB php-5.0.0/Zend/zend_hash.c | sed -n '450,470p'
```

```c
 450  ZEND_API int zend_hash_del_key_or_index(HashTable *ht, char *arKey, uint nKeyLength, ulong h, int flag)
 451  {
 452  	uint nIndex;
 453  	Bucket *p;
 454  
 455  	IS_CONSISTENT(ht);
 456  
 457  	if (flag == HASH_DEL_KEY) {
 458  		h = zend_inline_hash_func(arKey, nKeyLength);
 459  	}
 460  	nIndex = h & ht->nTableMask;
 461  
 462  	p = ht->arBuckets[nIndex];
 463  	while (p != NULL) {
 464  		if ((p->h == h) && ((p->nKeyLength == 0) || /* Numeric index */
 465  			((p->nKeyLength == nKeyLength) && (!memcmp(p->arKey, arKey, nKeyLength))))) {
 466  			HANDLE_BLOCK_INTERRUPTIONS();
 467  			if (p == ht->arBuckets[nIndex]) {
 468  				ht->arBuckets[nIndex] = p->pNext;
 469  			} else {
 470  				p->pLast->pNext = p->pNext;
```
