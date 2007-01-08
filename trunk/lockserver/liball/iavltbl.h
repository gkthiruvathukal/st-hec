/******************************************************************
**
** IAVLTBL.H:
**
**    ADT AVL Table Iterator Header
**
** This file is part of Apt Abstract Data Types (ADT)
** Copyright (c) 1991 -- Apt Technologies
** All rights reserved
**
******************************************************************/

#ifndef IAVLTBL_H
#define IAVLTBL_H

/* ---------- Headers */

#include "avltbl.h"
#include "queue.h"
#include "iqueue.h"

/* ---------- Types */

typedef struct _AVLTableIterator {
  Queue tableQueue;
  QueueIterator iter;
} _AVLTableIterator, *AVLTableIterator;

/* ---------- Exported Function Prototypes */

AVLTableIterator AVLTableIteratorNew(AVLTable, int);
void AVLTableIteratorDispose(AVLTableIterator);

int AVLTableIteratorAtTop(AVLTableIterator);
int AVLTableIteratorAtBottom(AVLTableIterator);
int AVLTableIteratorAtPosition(AVLTableIterator, int);

int AVLTableIteratorPosition(AVLTableIterator);
AVLTableItem AVLTableIteratorCurrentData(AVLTableIterator);
AVLTableItem AVLTableIteratorPreviousData(AVLTableIterator);

void AVLTableIteratorAdvance(AVLTableIterator);
void AVLTableIteratorBackup(AVLTableIterator);
void AVLTableIteratorAbsoluteSeek(AVLTableIterator, int);
void AVLTableIteratorRelativeSeek(AVLTableIterator, int);

#endif /* IAVLTBL_H */
