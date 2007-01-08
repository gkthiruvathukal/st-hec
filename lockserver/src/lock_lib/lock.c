#include <assert.h>
#include "lock.h"
#include "lockserverapi.h"

#define MAX_OL_COUNT 64
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
                  int servicePort)
{
    /* Parameters for list I/O */
    int etype_size = -1, i;
    int num_etypes_in_filetype = -1, num_filetypes = -1;
    int etypes_in_filetype = -1, size_in_filetype = -1;
    int bytes_into_filetype = -1;
    int64_t cur_io_size, io_size = -1, tmp_filetype_size = -1;
    int64_t first_offset = -1, last_offset = -1;
    int first_round = 1;
    int lockid = -1;

    /* Parameters for flattened file datatypes */
    int flat_file_index = 0;
    int64_t cur_flat_file_reg_off = 0;
    ADIOI_Flatlist_node *flat_file;
    int buftype_size = -1,
	filetype_size = -1, filetype_extent = -1;
    int filetype_is_contig = -1;

    /* Locking arrays */
    int32_t file_ol_count = 0;
    int64_t file_off_arr[MAX_OL_COUNT];
    int64_t file_len_arr[MAX_OL_COUNT];
    int64_t range_off_arr[1];
    int64_t range_len_arr[1];
    
    if (locktype == NO_LOCK) { return -1; }

    /* If we are doing a file lock, this is simple */
    if (locktype == LOCK_FILE)
    {
        lockid = acquireFileLock(serviceName, servicePort, fileName);
        return lockid;
    }

    MPI_Type_size(filetype, &filetype_size);
    if (filetype_size == 0) {
        return -1;
    }
    MPI_Type_extent(filetype, &filetype_extent);

    /* Calculate how much data we are accessing to figure out 
     * how far to go into the file datatype */
    MPI_Type_size(buftype, &buftype_size);
    io_size = count * buftype_size;

    /* Flatten the file datatype */
    ADIOI_Datatype_iscontig(filetype, &filetype_is_contig);
    if (filetype_is_contig == 0)
    {
	ADIOI_Flatten_datatype(filetype);
	flat_file = ADIOI_Flatlist;
	while (flat_file->type != filetype)
	    flat_file = flat_file->next;
    }
    else
    {
	/* flatten and add to the list */
	flat_file = (ADIOI_Flatlist_node *) ADIOI_Malloc
            (sizeof(ADIOI_Flatlist_node));
        flat_file->blocklens = (int *) ADIOI_Malloc(sizeof(int));
        flat_file->indices = (ADIO_Offset *) ADIOI_Malloc(sizeof(ADIO_Offset));
        flat_file->blocklens[0] = filetype_size;
        flat_file->indices[0] = 0;
        flat_file->count = 1;
    }

    /* Using the offset and the etype, find out where we are
     * in the flattened filetype, both the block index and how far
     * into the block */
    MPI_Type_size(etype, &etype_size);
    num_etypes_in_filetype = filetype_size / etype_size;
    num_filetypes = (int) (offset / num_etypes_in_filetype);
    etypes_in_filetype = (int) (offset % num_etypes_in_filetype);
    size_in_filetype = etypes_in_filetype * etype_size;

    tmp_filetype_size = 0;
    for (i=0; i<flat_file->count; i++) {
        tmp_filetype_size += flat_file->blocklens[i];
        if (tmp_filetype_size > size_in_filetype)
        {
            flat_file_index = i;
            cur_flat_file_reg_off = flat_file->blocklens[i] -
                (tmp_filetype_size - size_in_filetype);
            break;
        }
    }
    bytes_into_filetype = offset * filetype_size;

    cur_io_size = 0;
    while (cur_io_size != io_size)
    {
	/* Initialize the temporarily unrolling lists and
         * and associated variables */
        file_ol_count = 0;
	
	memset(file_off_arr, 0, MAX_OL_COUNT*sizeof(int64_t));
	memset(file_len_arr, 0, MAX_OL_COUNT*sizeof(int64_t));

	gen_listio_arr(flat_file,
		       &flat_file_index,
		       &cur_flat_file_reg_off,
		       filetype_size,
		       filetype_extent,
		       MAX_OL_COUNT,
		       disp,
		       bytes_into_filetype,
		       &cur_io_size,
		       io_size,
		       file_off_arr,
		       file_len_arr,
		       &file_ol_count);

#ifdef DEBUG
	print_buf_file_ol_pairs(file_off_arr,
				file_len_arr,
				file_ol_count);
#endif

	switch (locktype) {
	    case LOCK_REGION:
		if (first_round == 1) {
		    first_offset = file_off_arr[0];
		    first_round = 0;
		}
		if (cur_io_size == io_size) {
		    last_offset = file_off_arr[file_ol_count] +
			file_len_arr[file_ol_count];
		    /* Actual locking acquiring done later on. */
		}
		break;

	    case LOCK_LIST:
                if (lockid == -1) {
                    //printf("acquiring %d locks\n", file_ol_count);
                    lockid = acquireLocks(serviceName, servicePort, fileName,
                                 file_ol_count, file_off_arr, file_len_arr);
                } else {
                    //printf("acquiring %d locks\n", file_ol_count);
                    acquireMoreLocks(serviceName, servicePort, fileName,
                                     lockid, file_ol_count, file_off_arr,
                                     file_len_arr);
                }
		break;

	    case LOCK_BLOCK_LIST:
		/* Convert the offset-length pairs into block
		 * offset-length pairs */
		convert_ol_blocks(&file_ol_count, file_off_arr, file_len_arr,
				  block_size);
#ifdef DEBUG
		fprintf(stderr, "After conversion to block ol_pairs:\n");
		print_buf_file_of_pairs(file_off_arr,
					 file_len_arr,
					 file_ol_count);
#endif

		if (lockid == -1) {
		    //printf("acquiring %d locks\n", file_ol_count);
		    lockid = acquireBlockLocks(serviceName, servicePort,
                                               fileName, file_ol_count,
                                               file_off_arr, file_len_arr);
		} else {
		    //printf("acquiring %d locks\n", file_ol_count);
		    acquireMoreBlockLocks(serviceName, servicePort, fileName,
                                          lockid, file_ol_count, file_off_arr,
                                          file_len_arr);
		}
		break;		

	    default:
		fprintf(stderr, "Impossible locktype %d.  Exiting...\n",
			locktype);
	}
	
    }
    if (locktype == LOCK_REGION) {
        range_off_arr[0] = first_offset;
        range_len_arr[0] = last_offset - first_offset;
#ifdef DEBUG
	fprintf(stderr, "After conversion to a single region lock:\n");
	fprintf(stderr, "single file_ol_pair(offset,length) = (%Ld,%Ld)"
		range_off_arr[0], rangle_len_arr[0]);
#endif
        lockid = acquireLocks(serviceName, servicePort, fileName,
                              1, range_off_arr, range_len_arr);
    }

    if (filetype_is_contig == 0)
        ADIOI_Delete_flattened(filetype);
    else
    {
        ADIOI_Free(flat_file->blocklens);
        ADIOI_Free(flat_file->indices);
        ADIOI_Free(flat_file);
    }

    return lockid;
}


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
                   int32_t *file_ol_count_p)
{
    int64_t region_size = -1;
    int64_t cur_flat_file_reg_left = 0;

    /* Start on a non-zero file region
     * Note this does not affect the bytes_completed
     * since no data is in these regions.  Initialize the
     * first file offsets. */
    while (flat_file->blocklens[(*flat_file_index_p)] == 0)
    {
        (*flat_file_index_p) = ((*flat_file_index_p) + 1) %
            flat_file->count;
    }
    file_off_arr[*file_ol_count_p] = disp +
        (((bytes_into_filetype + *bytes_completed) / flat_file_size) *
         flat_file_extent) +
        flat_file->indices[*flat_file_index_p] +
        *cur_flat_file_reg_off_p;
    file_len_arr[*file_ol_count_p] = 0;

    while (*bytes_completed != total_io_size
           && (*file_ol_count_p) < max_ol_count)
    {
	/* How much data is left in the current piece in our 
	 * flattened datatype */
	cur_flat_file_reg_left = flat_file->blocklens[*flat_file_index_p]
	    - *cur_flat_file_reg_off_p;

	region_size = cur_flat_file_reg_left;
	/* We only process a portion of the remaining file region */
	if (region_size > total_io_size - *bytes_completed)
	{
	    region_size = total_io_size - *bytes_completed;
	    (*cur_flat_file_reg_off_p) += region_size;
	}
	else /* We process the entire remaining file region */
	{
	    (*flat_file_index_p) = ((*flat_file_index_p) + 1) %
		flat_file->count;
	    while (flat_file->blocklens[(*flat_file_index_p)] == 0)
	    {
		(*flat_file_index_p) = ((*flat_file_index_p) + 1) %
		    flat_file->count;
	    }
	    (*cur_flat_file_reg_off_p) = 0;
	    
	}

	/* Add the piece to the file lengths 
	 * - First check can we add to the last offset-length pair? 
	 * - If not, add it to the current piece */
	if (file_off_arr[(*file_ol_count_p) - 1] + 
	    file_len_arr[(*file_ol_count_p) - 1] ==
	    file_off_arr[*file_ol_count_p])
	{
	    file_len_arr[(*file_ol_count_p) - 1] += region_size;
	}
	else
	{
	    file_len_arr[*file_ol_count_p] = region_size;
	    (*file_ol_count_p)++;
	}
	/* Don't prepare for the next piece if we have reached
	 * the limit or else it will segment fault. */
	if ((*file_ol_count_p) != max_ol_count)
	{
	    file_off_arr[*file_ol_count_p] = disp +
                    (((bytes_into_filetype + *bytes_completed + region_size)
                      / flat_file_size) *
                     flat_file_extent) +
                    flat_file->indices[*flat_file_index_p] +
                    (*cur_flat_file_reg_off_p);
                file_len_arr[*file_ol_count_p] = 0;
	}
	
	*bytes_completed += region_size;
    }

    /* Increment the count if we stopped in the middle of a
     * file region */
    if (*cur_flat_file_reg_off_p != 0)
        (*file_ol_count_p)++;

    return 0;
}

void print_buf_file_ol_pairs(int64_t file_off_arr[],
                             int64_t file_len_arr[],
                             int32_t file_ol_count)
{
    int i = -1;
    fprintf(stderr, "file_ol_pairs(offset,length) count = %d\n",
            file_ol_count);
    for (i = 0; i < file_ol_count; i++)
    {
        fprintf(stderr, "[%d](%Ld,%Ld) ", 
		i, file_off_arr[i], file_len_arr[i]);
	if ((i + 1) % 5 == 0)
	    fprintf(stderr, "\n");
    }
    fprintf(stderr, "\n");

}

int convert_ol_blocks(int32_t *ol_count_p, int64_t *off_arr, int64_t *len_arr,
		      int block_size)
{
    int i;
    int64_t temp_block_off = -1;
    int64_t temp_block_len = -1;
    int32_t temp_ol_count = 0;
    int64_t temp_off_arr[MAX_OL_COUNT];
    int64_t temp_len_arr[MAX_OL_COUNT];
    
    memset(temp_off_arr, 0, MAX_OL_COUNT*sizeof(int64_t));
    memset(temp_len_arr, 0, MAX_OL_COUNT*sizeof(int64_t));
    
    for (i = 0; i < *ol_count_p; i++)
    {
	temp_block_off = off_arr[i] / block_size;
	temp_block_len = (off_arr[i] + len_arr[i]) / block_size;
	/* Include the next block if we need to */
	if ((off_arr[i] + len_arr[i]) % block_size > 0)
	    temp_block_len++;
	
	if (temp_ol_count == 0)
	{
	    temp_off_arr[temp_ol_count] = temp_block_off;
	    temp_len_arr[temp_ol_count] = temp_block_len;
	    temp_ol_count++;
	}
	else
	{
	    /* It's possible that the last block ol_pair could overlap
	     * by up to 1 block. */
	    if ((temp_off_arr[temp_ol_count] + temp_len_arr[temp_ol_count])
		== temp_block_off + 1)
	    {
		temp_len_arr[temp_ol_count] += temp_block_len - 1;
	    }
	    else if ((temp_off_arr[temp_ol_count] + 
		      temp_len_arr[temp_ol_count]) == temp_block_off)
	    {
		temp_len_arr[temp_ol_count] += temp_block_len;
	    }
	    else
	    {
		temp_off_arr[temp_ol_count] = temp_block_off;
		temp_len_arr[temp_ol_count] = temp_block_len;
		temp_ol_count++;
	    }
	}
    }

    /* It can be proven that the conversion from offset-length pairs
     * to block offset-length pairs will always require the same or
     * less pairs. */
    
    assert(temp_ol_count <= *ol_count_p);
    
    memset(off_arr, 0, MAX_OL_COUNT*sizeof(int64_t));
    memset(len_arr, 0, MAX_OL_COUNT*sizeof(int64_t));

    /* Reset the off_arr and len_arr to the new block ol pairs. */

    for (i = 0; i < temp_ol_count; i++)
    {
	off_arr[i] = temp_off_arr[i];
	len_arr[i] = temp_len_arr[i];
    }

    return 0;
}
