#!/bin/sh
# Rebuilds ./src/ — the pristine php-5.0.0 sources this mining pass read.
# src/ is a derivable artefact; this script is the generator.  Run from this dir.
set -e
TB=/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
# sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919  (5595997 bytes)
mkdir -p src
tar -xzf "$TB" -C src \
  php-5.0.0/Zend/zend.c php-5.0.0/Zend/zend.h \
  php-5.0.0/Zend/zend_API.c php-5.0.0/Zend/zend_builtin_functions.c \
  php-5.0.0/Zend/zend_compile.c php-5.0.0/Zend/zend_constants.c \
  php-5.0.0/Zend/zend_execute.c php-5.0.0/Zend/zend_execute.h \
  php-5.0.0/Zend/zend_execute_API.c php-5.0.0/Zend/zend_globals.h \
  php-5.0.0/Zend/zend_hash.c php-5.0.0/Zend/zend_hash.h \
  php-5.0.0/Zend/zend_llist.c php-5.0.0/Zend/zend_llist.h \
  php-5.0.0/Zend/zend_object_handlers.c php-5.0.0/Zend/zend_objects.c \
  php-5.0.0/Zend/zend_objects_API.c php-5.0.0/Zend/zend_opcode.c \
  php-5.0.0/Zend/zend_operators.c php-5.0.0/Zend/zend_ptr_stack.h \
  php-5.0.0/Zend/zend_variables.c \
  php-5.0.0/ext/mbstring/mbstring.c php-5.0.0/ext/mbstring/php_mbregex.c \
  php-5.0.0/ext/pcre/php_pcre.c \
  php-5.0.0/ext/standard/array.c php-5.0.0/ext/standard/basic_functions.c \
  php-5.0.0/ext/standard/http_fopen_wrapper.c php-5.0.0/ext/standard/streamsfuncs.c \
  php-5.0.0/ext/standard/string.c php-5.0.0/ext/standard/user_filters.c \
  php-5.0.0/ext/standard/uuencode.c php-5.0.0/ext/standard/var.c \
  php-5.0.0/ext/standard/var_unserializer.c php-5.0.0/ext/standard/var_unserializer.re \
  php-5.0.0/main/streams/streams.c
echo "src/ rebuilt: $(find src -type f | wc -l) files"
