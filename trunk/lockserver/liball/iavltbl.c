/******************************************************************
**
** IAVLTBL.C:
**
**    ADT AVL Table Iterator Implementation
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
#include "iavltbl.h"
#include "iqueue.h"

/* ---------- Functions */

PRIVATE void GetElem(void* element, void* args[] ) {
    if (args[0]) {
        QueuePut((Queue) args[0], element, 0);
    } else {
    		ADTError(ADT_TableIter, E_NullQueue, "GetElem");
    }
}

PUBLIC void AVLTableIteratorDispose(AVLTableIterator ati) {
    QueueIteratorDispose(ati->iter);
    QueueDispose(ati->tableQueue, NULL);
    free(ati);
}

PUBLIC AVLTableIterator AVLTableIteratorNew(AVLTable at, int start) {
    AVLTableIterator ati;
    int i;

    if (at) {
        ati = (AVLTableIterator) Allocate(sizeof(_AVLTableIterator));
    } else {
        ADTError(ADT_TableIter, E_NullAVLTable, "AVLTableIteratorNew");
    }
    if (ati) {
        Queue tableQueue = QueueNew();
        void* args[1];
        args[0] = tableQueue;
        AVLTableApply(at, GetElem, args);
        ati->tableQueue = tableQueue;
        ati->iter = QueueIteratorNew(tableQueue, start);
    } else {
        ADTError(ADT_TableIter, E_Allocation, "AVLTableIteratorNew");
    }
    return ati;
}

PUBLIC int AVLTableIteratorAtTop(AVLTableIterator ati) {
    if (!ati) {
        ADTError(ADT_TableIter, E_NullAVLTableIter, "AVLTableIteratorAtTop");
    }
    return QueueIteratorAtTop(ati->iter);
}

PUBLIC int AVLTableIteratorAtBottom(AVLTableIterator ati) {
    if (!ati) {
        ADTError(ADT_TableIter, E_NullAVLTableIter, "AVLTableIteratorAtBottom");
    }
    return QueueIteratorAtBottom(ati->iter);
}

PUBLIC int AVLTableIteratorAtPosition(AVLTableIterator ati, int position) {
    if (!ati) {
        ADTError(ADT_TableIter, E_NullAVLTableIter, "AVLTableIteratorAtPosition");
    }
    return QueueIteratorAtPosition(ati->iter, position);
}

PUBLIC int AVLTableIteratorPosition(AVLTableIterator ati) {
    if (!ati) {
        ADTError(ADT_TableIter, E_NullAVLTableIter, "AVLTableIteratorPosition");
    }
    return QueueIteratorPosition(ati->iter);
}

PUBLIC AVLTableItem AVLTableIteratorCurrentData(AVLTableIterator ati) {
    if (!ati) {
        ADTError(ADT_TableIter, E_NullAVLTableIter, "AVLTableIteratorCurrentData");
    }
    return (AVLTableItem) QueueIteratorCurrentData(ati->iter);
}

PUBLIC AVLTableItem AVLTableIteratorPreviousData(AVLTableIterator ati) {
    if (!ati) {
        ADTError(ADT_TableIter, E_NullAVLTableIter, "AVLTableIteratorPreviousData");
    }
    return (AVLTableItem) QueueIteratorPreviousData(ati->iter);
}

PUBLIC void AVLTableIteratorAdvance(AVLTableIterator ati) {
    if (!ati) {
        ADTError(ADT_TableIter, E_NullAVLTableIter, "AVLTableIteratorAdvance");
    }
    QueueIteratorAdvance(ati->iter);
}

PUBLIC void AVLTableIteratorBackup(AVLTableIterator ati) {
    if (!ati) {
        ADTError(ADT_TableIter, E_NullAVLTableIter, "AVLTableIteratorBackup");
    }
    QueueIteratorBackup(ati->iter);
}

PUBLIC void AVLTableIteratorAbsoluteSeek(AVLTableIterator ati, int position) {
    if (!ati) {
        ADTError(ADT_TableIter, E_NullAVLTableIter, "AVLTableIteratorAbsoluteSeek");
    }
    QueueIteratorAbsoluteSeek(ati->iter, position);
}

PUBLIC void AVLTableIteratorRelativeSeek(AVLTableIterator ati, int disp) {
    if (!ati) {
        ADTError(ADT_TableIter, E_NullAVLTableIter, "AVLTableIteratorRelativeSeek");
    }
    QueueIteratorRelativeSeek(ati->iter, disp);
}
