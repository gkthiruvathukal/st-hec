/******************************************************************
**
** HASHTBL.H:
**
**    ADT Symbol Table Manager - Hash Table Implementation
**
** This file is part of Apt Abstract Data Types (ADT)
** Copyright (c) 1991 -- Apt Technologies
** All rights reserved
**
******************************************************************/
#ifndef HASHTBL_H
#define HASHTBL_H

/* ---------- Headers */
#include "queue.h"
#include "avltree.h"

/* ---------- Defines */

#define OneToOne 1
#define OneToMany 2
#define DEFAULT_TYPE 30000

/* ---------- Types */
typedef long int (*HashFunction) (void *);

/* Moved from hashtbl.c 03/22/2005 pma */
typedef struct _HashTableElement {
  void *key;
  int tag;
  int type;
  union {
    void *dataPtr;
    Queue qPtr;
  } u;
} _HashTableElement, *HashTableElement;

typedef struct _HashTable {
  int size;
  HashFunction hash;
  ComparisonFunction compare;
  DisposeFunction dispose;
  AVLTree *bucket;
  struct _HashTable *scopeLink;
} _HashTable, *HashTable;

/* ---------- Prototypes */

int CompareStrings(void *, void *);
long int StringHash1(void *);
HashTable HashTableNew(int,HashFunction,ComparisonFunction,HashTable);
HashTable HashTableGetScopeLink(HashTable);
void HashTableDispose(HashTable);
void *HashTableLookUpFirst(HashTable, void *);
void *HashTableLookUpFirstScoped(HashTable, void *);
void *HashTableLookUpTypedFirst(HashTable, void *, int);
void *HashTableLookUpTypedFirstScoped(HashTable, void *, int);
Queue HashTableLookUpAll(HashTable, void *);
Queue HashTableLookUpAllScoped(HashTable, void *);
Queue HashTableLookUpTypedAll(HashTable, void *, int);
Queue HashTableLookUpTypedAllScoped(HashTable, void *, int);
void *HashTableInsert(HashTable, void *, void *);
void *HashTableInsertTyped(HashTable, void *, void *, int);
void *HashTableDeleteFirst(HashTable, void *);
void *HashTableDeleteTypedFirst(HashTable, void *, int);
Queue HashTableDeleteTypedAll(HashTable, void *, int);
Queue HashTableDeleteAll(HashTable, void *);

/* Added 03/25/2005 pma - old-style function decls removed */
void HashTableApply(HashTable, ApplyFunctionGeneric, void**);
void DisposeHashTableElement(void *);
void HashTableElementDispose(void *element);

#endif /* HASHTBL_H */
