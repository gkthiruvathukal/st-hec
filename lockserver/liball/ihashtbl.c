/******************************************************************
**
** IHASHTBL.C:
**
**    ADT Hash Table Iterator Implementation
**
** This file is part of Apt Abstrct Data Types (ADT)
** Copyright (c) 1991 -- Apt Technologies
** All rights reserved
**
** The concept of an iterator for an Abstract Data Type is derived
** from research on Smalltalk.
******************************************************************/

/* ---------- C Headers */

#include "cheaders.h"

/* ---------- Headers */

#include "adterror.h"
#include "allocate.h"
#include "ihashtbl.h"
#include "iqueue.h"

/* ---------- Functions */

PRIVATE void GetAllElems(void* item, void* args[] ) {
	HashTableElement hte;
	if (item) {
		hte = (HashTableElement) ((AVLTreeItem) item)->element;
	}
	if (args[0]) {
		QueuePut(args[0], hte, 0);
	}
}

PUBLIC void HashTableIteratorDispose(HashTableIterator hti) {
	QueueIteratorDispose(hti->iter);
	QueueDispose(hti->tableQueue, NULL);
	free(hti);
}

PUBLIC HashTableIterator HashTableIteratorNew(HashTable ht, int start) {
  	HashTableIterator hti;
  	int i;

	if (ht) {
	    hti = (HashTableIterator) Allocate(sizeof(_HashTableIterator));
	} else {
		ADTError(ADT_HashTableIter, E_NullHashTable, "HashTableIteratorNew");
	}
	if (hti) {
	    Queue tableQueue = QueueNew();
	    void* args[1];
	    args[0] = tableQueue;
	    HashTableApply(ht, GetAllElems, args);
	    hti->tableQueue = tableQueue;
		hti->iter = QueueIteratorNew(tableQueue, start);
	} else {
	    ADTError(ADT_HashTableIter, E_Allocation, "HashTableIteratorNew");
	}
	return hti;
}

PUBLIC int HashTableIteratorAtTop(HashTableIterator hti) {
	if (!hti) {
		ADTError(ADT_HashTableIter, E_NullHashTableIter, "HashTableIteratorAtTop");
	}
	return QueueIteratorAtTop(hti->iter);
}

PUBLIC int HashTableIteratorAtBottom(HashTableIterator hti) {
	if (!hti) {
		ADTError(ADT_HashTableIter, E_NullHashTableIter, "HashTableIteratorAtBottom");
	}
	return QueueIteratorAtBottom(hti->iter);
}

PUBLIC int HashTableIteratorAtPosition(HashTableIterator hti, int position) {
	if (!hti) {
		ADTError(ADT_HashTableIter, E_NullHashTableIter, "HashTableIteratorAtPosition");
	}
	return QueueIteratorAtPosition(hti->iter, position);
}

PUBLIC int HashTableIteratorPosition(HashTableIterator hti) {
	if (!hti) {
		ADTError(ADT_HashTableIter, E_NullHashTableIter, "HashTableIteratorPosition");
	}
	return QueueIteratorPosition(hti->iter);
}

PUBLIC void* HashTableIteratorCurrentData(HashTableIterator hti) {
	if (!hti) {
		ADTError(ADT_HashTableIter, E_NullHashTableIter, "HashTableIteratorCurrentData");
	}
	return QueueIteratorCurrentData(hti->iter);
}

PUBLIC void* HashTableIteratorPreviousData(HashTableIterator hti) {
	if (!hti) {
		ADTError(ADT_HashTableIter, E_NullHashTableIter, "HashTableIteratorPreviousData");
	}
	return QueueIteratorPreviousData(hti->iter);
}

PUBLIC void HashTableIteratorAdvance(HashTableIterator hti) {
	if (!hti) {
		ADTError(ADT_HashTableIter, E_NullHashTableIter, "HashTableIteratorAdvance");
	}
	QueueIteratorAdvance(hti->iter);
}

PUBLIC void HashTableIteratorBackup(HashTableIterator hti) {
	if (!hti) {
		ADTError(ADT_HashTableIter, E_NullHashTableIter, "HashTableIteratorBackup");
	}
	QueueIteratorBackup(hti->iter);
}

PUBLIC void HashTableIteratorAbsoluteSeek(HashTableIterator hti, int position) {
	if (!hti) {
		ADTError(ADT_HashTableIter, E_NullHashTableIter, "HashTableIteratorAbsoluteSeek");
	}
	QueueIteratorAbsoluteSeek(hti->iter, position);
}

PUBLIC void HashTableIteratorRelativeSeek(HashTableIterator hti, int disp) {
	if (!hti) {
		ADTError(ADT_HashTableIter, E_NullHashTableIter, "HashTableIteratorRelativeSeek");
	}
	QueueIteratorRelativeSeek(hti->iter, disp);
}
