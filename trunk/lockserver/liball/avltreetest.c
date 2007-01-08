#include <stdio.h>

#include "avltbl.h"
#include "iavltbl.h"

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

    AVLTable atbl = AVLTableNew(NULL);

    AVLTablePut(atbl, key1, &val1, V_Void);
    AVLTablePut(atbl, key2, &val2, V_Void);
    AVLTablePut(atbl, key3, val3, V_Void);
    AVLTablePut(atbl, key4, &val4, V_Void);
    
    int* retrieved1 = (int*) AVLTableFind(atbl, key1, V_Void);
    int* retrieved2 = (int*) AVLTableFind(atbl, key2, V_Void);
    char* retrieved3 = (char*) AVLTableFind(atbl, key3, V_Void);
    boolean* retrieved4 = (boolean*) AVLTableFind(atbl, key4, V_Void);
    
    printf("retrieved1 = %d\n", *retrieved1);
    printf("retrieved2 = %d\n", *retrieved2);
    printf("retrieved3 = %s\n", retrieved3);
    printf("retrieved4 = %d\n", *retrieved4);

    printf("heap size: %d\n", atbl->Space->size);

    AVLTableIterator ati = AVLTableIteratorNew(atbl, 1);

    while (!AVLTableIteratorAtBottom(ati)) {
        AVLTableItem item = AVLTableIteratorCurrentData(ati);
        printf("key: %s\n", item->key);
        printf("element addr: %x\n", item->element);
        AVLTableIteratorAdvance(ati);
    }

    return 0;
}

