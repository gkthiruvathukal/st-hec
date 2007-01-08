#include <stdio.h>

#include "queue.h"
#include "iqueue.h"

#define INT_VALUE 1000

int main (int argc, char* argv[]) {
    int val1 = 1;
    int val2 = 2;
    int val3 = 3;
    int val4 = 4;

    Queue q = QueueNew();

    QueuePut(q, &val1, INT_VALUE);
    QueuePut(q, &val2, INT_VALUE);
    QueuePut(q, &val3, INT_VALUE);
    QueuePut(q, &val4, INT_VALUE);

    QueueItem qptr = q->head;
    while (qptr != NULL) {
        int* val = (int*) qptr->element;
        printf("value: %d\n", *val);
        qptr = qptr->next;
    }

    QueueIterator qiter = QueueIteratorNew(q, 1);

    while (qiter->currentItem != NULL) {
        int* val = (int*) qiter->currentItem->element;
        printf("iterator value: %d\n", *val);
        QueueIteratorAdvance(qiter);
    }
}
