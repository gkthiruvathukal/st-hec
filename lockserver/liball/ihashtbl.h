/******************************************************************
**
** IQUEUE.H:
**
**    ADT Queue Iterator Implementation
**
** This file is part of Apt Abstract Data Types (ADT)
** Copyright (c) 1991 -- Apt Technologies
** All rights reserved
**
******************************************************************/

#ifndef IHASHTBL_H
#define IHASHTBL_H

/* ---------- Headers */

#include "hashtbl.h"
#include "queue.h"
#include "iqueue.h"

/* ---------- Types */

typedef struct _HashTableIterator {
  Queue tableQueue;
  QueueIterator iter;
} _HashTableIterator, *HashTableIterator;

/* ---------- Exported Function Prototypes */

HashTableIterator HashTableIteratorNew(HashTable, int);
void HashTableIteratorDispose(HashTableIterator);

int HashTableIteratorAtTop(HashTableIterator);
int HashTableIteratorAtBottom(HashTableIterator);
int HashTableIteratorAtPosition(HashTableIterator, int);

int HashTableIteratorPosition(HashTableIterator);
void* HashTableIteratorCurrentData(HashTableIterator);
void* HashTableIteratorPreviousData(HashTableIterator);

void HashTableIteratorAdvance(HashTableIterator);
void HashTableIteratorBackup(HashTableIterator);
void HashTableIteratorAbsoluteSeek(HashTableIterator, int);
void HashTableIteratorRelativeSeek(HashTableIterator, int);

#endif /* IHASHTBL_H */
