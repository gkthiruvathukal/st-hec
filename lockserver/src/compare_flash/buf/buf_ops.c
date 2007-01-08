#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "buf_ops.h"

void type_print(int el_type, void *buf, int buf_index)
{
    switch (el_type)
    {
	case INT:
	    printf("%d", ((int *) buf)[buf_index]);
	    break;
	case CHAR:
	    printf("%c", ((char *) buf)[buf_index]);
	    break;
	case DOUBLE:
	    printf("%4.0f", ((double *) buf)[buf_index]);
	    break;
	default:
	    printf("type_print: Impossible type\n");
    }
}

void buf_print(char *buf_name, int buf_type, void *buf,
	       int buf_begin, int buf_end)
{
    int i = 0, begin_row = 0, begin_offset = 0;

    printf("%s:\n", buf_name);
    if (buf_begin >= buf_end)
    {
	printf("buf_print: invalid buf_begin or buf_end\n");
	return;
    }

    begin_offset = buf_begin % 10;
    begin_row = buf_begin / 10;

    for (i = begin_row*10; i < buf_end; i++)
    {
	if (i < buf_begin)
	    continue;
	
	type_print(buf_type, buf, i);
	printf(" ");
	
	if (i % 10 == 4)
	    printf(" ");
	else if (i % 10 == 9) 
	    printf("\n");
    }
    printf("\n");
}

int compare_buf(int el_type, void *test_buf, 
		void *correct_buf, int buf_length)
{
    int ret = 0, i;
    
    for (i = 0; i < buf_length; i++)
    {
	switch (el_type)
	{
	    case INT:
		if (((int *) test_buf)[i] != ((int *) correct_buf)[i])
		{
		    printf("test[%d] = %d NOT EQUAL correct[%d]"
			   " = %d\n", i, ((int *) test_buf)[i], 
			   i, ((int *) correct_buf)[i]);
		    ret = -1;
		}
		break;
	    case CHAR:
		if (((char *) test_buf)[i] != ((char *) correct_buf)[i])
		{
		    printf("test[%d] = %c NOT EQUAL correct[%d]"
			   " = %c\n", i, ((char *) test_buf)[i], 
			   i, ((char *) correct_buf)[i]);
		    ret = -1;
		}
		break;
	    default:
		printf("compare_buf: Impossible type\n");
	}
    }
    return ret;
}

int print_compared_buf(int el_type, 
		       void *test_buf, void *correct_buf,
		       int buf_lengths, char *error_msg, 
		       char *test_buf_name, char *correct_buf_name)
{
    int ret = -1;
    ret = compare_buf(el_type, test_buf, correct_buf, buf_lengths);
    if (ret == -1)
    {
	printf("%s...\n", error_msg);
	buf_print(test_buf_name, CHAR, test_buf, 0, buf_lengths);
	buf_print(correct_buf_name, CHAR, correct_buf, 0, buf_lengths);
    }
    return ret;
}
