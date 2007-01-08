#include <stdio.h>

#define INT    0
#define INT64  1
#define CHAR   2
#define DOUBLE 3

void type_print(int el_type, void *buf, int buf_index);
void buf_print(char *buf_name, int buf_type, void *buf,
	       int buf_begin, int buf_end);
int compare_buf(int el_type, void *test_buf, 
		void *correct_buf, int buf_length);
int print_compared_buf(int el_type, 
		       void *test_buf, void *correct_buf,
		       int buf_lengths, char *error_msg, 
		       char *test_buf_name, char *correct_buf_name);
