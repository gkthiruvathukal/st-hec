#ifndef _LOCK_H
#define _LOCK_H

#include "adio.h"
#include "adio_extern.h"

#define NO_LOCK         -1
#define LOCK_FILE        0
#define LOCK_REGION      1
#define LOCK_LIST        2
#define LOCK_BLOCK_LIST  3
#define MAX_LOCK         4

int lock_datatype(int locktype,
		  int block_size,
                  int count,
                  MPI_Datatype buftype,
                  MPI_Offset disp,
                  MPI_Offset offset,
                  MPI_Datatype filetype,
                  MPI_Datatype etype,
                  char* fileName,
                  char* serviceName,
                  int servicePort);
int gen_listio_arr(ADIOI_Flatlist_node *flat_file,
                   int *flat_file_index_p,
                   int64_t *cur_flat_file_reg_off_p,
                   int flat_file_size,
                   int flat_file_extent,
                   int max_ol_count,
                   ADIO_Offset disp,
                   int bytes_into_filetype,
                   int64_t *bytes_completed,
                   int64_t total_io_size,
                   int64_t file_off_arr[],
                   int64_t file_len_arr[],
                   int32_t *file_ol_count_p);
void print_buf_file_ol_pairs(int64_t file_off_arr[],
                             int64_t file_len_arr[],
                             int32_t file_ol_count);
int convert_ol_blocks(int *ol_count_p, int64_t *off_arr, int64_t *len_arr,
		      int block_size);
#endif
