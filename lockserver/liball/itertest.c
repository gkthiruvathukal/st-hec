#include <stdio.h>

#include "hashtbl.h"
#include "ihashtbl.h"

typedef char boolean;

#ifndef TRUE
#define TRUE 1
#endif

#ifndef FALSE
#define FALSE 0
#endif

#define INTEGER_TYPE 1000
#define LONG_TYPE    2000
#define STRING_TYPE  3000
#define BOOLEAN_TYPE 4000

int main(int argc, char* argv[]) {
	char* key1 = "Hello";
	char* key2 = "There";
	char* key3 = "World!";
	char* key4 = "Joy!";
	
	int val1     = 123;
	int val2     = 456;
	char* val3   = "Foobar";
	boolean val4 = TRUE;
	
	HashTable ht = HashTableNew(32, StringHash1, CompareStrings, NULL);
	HashTableInsertTyped(ht, key1, &val1, INTEGER_TYPE);
	HashTableInsertTyped(ht, key2, &val2, INTEGER_TYPE);
	HashTableInsertTyped(ht, key3, val3, STRING_TYPE);
	HashTableInsertTyped(ht, key4, &val4, BOOLEAN_TYPE);
	
}

