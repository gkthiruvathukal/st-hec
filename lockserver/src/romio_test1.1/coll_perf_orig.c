#include "mpi.h"
#include "mpio.h"  /* not necessary with MPICH 1.1.1 or HPMPI 1.4 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include "lockserverapi.h"

/* The file name is taken as a command-line argument. */

/* Measures the I/O bandwidth for writing/reading a 3D
   block-distributed array to a file corresponding to the global array
   in row-major (C) order.
   Note that the file access pattern is noncontiguous.
  
   Array size 128^3. For other array sizes, change array_of_gsizes below.*/

#define POSIX      0
#define DATASIEVE  1
#define LISTIO     2
#define DATATYPE   3
#define COLLECTIVE 4
#define READ       5
#define WRITE      6

#define NO_DARRAY
#define LOCKING

#ifdef LOCKING
#define FILE_LOCK   0
#define REGION_LOCK 1
#define LIST_LOCK   2
#endif

void parse_args(int argc, char **argv,
		int *gsize,
		int *testtype,
		int *rw_type,
		int *filename_len,
		char **filename);

int main(int argc, char **argv)
{
    MPI_Datatype newtype;
    int i, ndims, array_of_gsizes[3], array_of_distribs[3];
    int order, nprocs, bufcount, mynod;
    char *buf = NULL;
    int array_of_dargs[3], array_of_psizes[3];
    MPI_File fh;
    MPI_Status status;
    MPI_Info info;
    double stim, write_tim, new_write_tim, write_bw;
    double read_tim, new_read_tim, read_bw;
    char *filename = NULL;
    int gsize = -1, testtype = -1, rw_type = -1, filename_len = -1;
#ifdef NO_DARRAY
    int blocklens[2];
    MPI_Aint indices[2];
    MPI_Datatype old_types[2];
    MPI_Datatype face, cube;
#endif
#ifdef LOCKING
    int lockid = -1, j, lock_type, total_locks;
    int64_t *offsets = NULL;
    int64_t *lengths = NULL;
#endif

    MPI_Init(&argc,&argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &mynod);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);

    if (nprocs != 1 && nprocs != 8 && nprocs != 27 &&
	nprocs != 64 && nprocs != 125 && nprocs != 216 && nprocs != 343)
    {
	if (mynod == 0)
	    fprintf(stderr, "%d procs is not a cube root\n", nprocs);
	MPI_Finalize();
	exit(1);
    }

    /* process 0 takes the file name as a command-line argument and 
     * broadcasts it to other processes */
    if (mynod == 0)
    {
	parse_args(argc, argv,
		   &gsize, &testtype, &rw_type, &filename_len, &filename);
	MPI_Bcast(&filename_len, 1, MPI_INT, 0, MPI_COMM_WORLD);
	MPI_Bcast(filename, filename_len+1, 
		  MPI_CHAR, 0, MPI_COMM_WORLD);
    }
    else 
    {
	MPI_Bcast(&filename_len, 1, MPI_INT, 0, MPI_COMM_WORLD);
	filename = (char *) malloc(filename_len+1);
	MPI_Bcast(filename, filename_len+1, 
		  MPI_CHAR, 0, MPI_COMM_WORLD);
    }
    MPI_Bcast((void *) &gsize, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast((void *) &testtype, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast((void *) &rw_type, 1, MPI_INT, 0, MPI_COMM_WORLD);

    ndims = 3;
    order = MPI_ORDER_C;

    array_of_gsizes[0] = gsize;
    array_of_gsizes[1] = gsize;
    array_of_gsizes[2] = gsize;

    array_of_distribs[0] = MPI_DISTRIBUTE_BLOCK;
    array_of_distribs[1] = MPI_DISTRIBUTE_BLOCK;
    array_of_distribs[2] = MPI_DISTRIBUTE_BLOCK;

    array_of_dargs[0] = MPI_DISTRIBUTE_DFLT_DARG;
    array_of_dargs[1] = MPI_DISTRIBUTE_DFLT_DARG;
    array_of_dargs[2] = MPI_DISTRIBUTE_DFLT_DARG;

    for (i=0; i<ndims; i++) array_of_psizes[i] = 0;
    MPI_Dims_create(nprocs, ndims, array_of_psizes);
    
    if (mynod == 0)
	fprintf(stderr, "array_of_psizes[0] = %d\n"
		"array_of_psizes[1] = %d\n"
		"array_of_psizes[2] = %d\n",
		array_of_psizes[0],
		array_of_psizes[1],
		array_of_psizes[2]);

#ifdef NO_DARRAY
    MPI_Type_hvector(array_of_gsizes[1] / array_of_psizes[1], 
		     array_of_gsizes[0] / array_of_psizes[0], 
		     array_of_gsizes[0],
		     MPI_CHAR,
		     &face);
    MPI_Type_hvector(array_of_gsizes[2] / array_of_psizes[2],
		     1,
		     array_of_gsizes[0] * array_of_gsizes[1],
		     face,
		     &cube);
    blocklens[0] = 1;
    blocklens[1] = 1;
    indices[0] = 0;
    indices[1] = 
	((mynod % array_of_psizes[0])*
	 (array_of_gsizes[0] / array_of_psizes[0])) +
	(((mynod % (array_of_psizes[0] * array_of_psizes[1])) / array_of_psizes[0])*
	 (array_of_gsizes[0]*(array_of_gsizes[1] / array_of_psizes[1]))) +
	((mynod / (array_of_psizes[0] * array_of_psizes[1]))*
	 (array_of_gsizes[0] * array_of_gsizes[1]) * (array_of_gsizes[2] / array_of_psizes[2]));
    old_types[0] = MPI_LB;
    old_types[1] = cube;

    MPI_Type_struct(2,
		    blocklens,
		    indices,
		    old_types,
		    &newtype);
#else
    MPI_Type_create_darray(nprocs, mynod, ndims, array_of_gsizes,
			   array_of_distribs, array_of_dargs,
			   array_of_psizes, order, MPI_CHAR, &newtype);
#endif

/* 3 different locking mentalities 
 * 1. File lock the whole thing.  One lock from 0 - MAX_INT 
 * 2. Lock from offset to extent 
 * 3. List-lock */
#ifdef LOCKING
    lock_type = LIST_LOCK;
    //lock_type = FILE_LOCK;
    //lock_type = REGION_LOCK;
    if (lock_type == FILE_LOCK)
    {
	acquireFileLock(filename);
    }
    else if (lock_type == REGION_LOCK)
    {
	if ((offsets = malloc(sizeof(int64_t))) == NULL)
	{
	    fprintf(stderr, "malloc offsets failed\n");
	    MPI_Finalize();
	    exit(1);
	}	    
	if ((lengths = malloc(sizeof(int64_t))) == NULL)
	{
	    fprintf(stderr, "malloc lengths failed\n");
	    MPI_Finalize();
	    exit(1);
	}	    
	offsets[0] = indices[1];
        int l;
	MPI_Type_extent(newtype, &l);
        lengths[0] = l;
	fprintf(stderr, "myid = %d lock[%d] = (%Ld, %Ld)\n\n",
		    mynod, i,
		    offsets[0],
		    lengths[0]);
	lockid = acquireLocks(filename, 1, offsets, lengths);
    }
    else if (lock_type == LIST_LOCK)
    {
	total_locks = (array_of_gsizes[1] / array_of_psizes[1])*
	    (array_of_gsizes[2] / array_of_psizes[2]);

	if ((offsets = malloc(total_locks*sizeof(int64_t))) == NULL)
	{
	    fprintf(stderr, "malloc offsets failed\n");
	    MPI_Finalize();
	    exit(1);
	}	    
	if ((lengths = malloc(total_locks*sizeof(int64_t))) == NULL)
	{
	    fprintf(stderr, "malloc lengths failed\n");
	    MPI_Finalize();
	    exit(1);
	}	    

	for (i = 0; i < array_of_gsizes[2] / array_of_psizes[2]; i++)
	{
	    for (j = 0; j < array_of_gsizes[1] / array_of_psizes[1]; j++)
	    {
		offsets[(i*(array_of_gsizes[1] / array_of_psizes[1]))+j] = 
		    indices[1] + 
		    (array_of_gsizes[0] * j) +
		    (array_of_gsizes[0] * array_of_gsizes[1] * i);
		lengths[(i*(array_of_gsizes[1] / array_of_psizes[1]))+j] = 
		    array_of_gsizes[0] / array_of_psizes[0];
	    }
	}
	for (i = 0; i < total_locks; i++)
	{
	    fprintf(stderr, "myid = %d lock[%d] = (%Ld, %Ld)\n",
		    mynod, i,
		    offsets[i],
		    lengths[i]);
	}
	fprintf(stderr, "\n");
	lockid = acquireLocks(filename, total_locks, offsets, lengths);
    }

#endif
    MPI_Type_commit(&newtype);

    MPI_Type_size(newtype, &bufcount);
    buf = (char *) malloc(bufcount * sizeof(char));
    for (i = 0; i < bufcount; i++) {
      buf[i] = mynod + 48;
    }

    MPI_Info_create(&info);
    switch (testtype)
    {
	case POSIX:
	    MPI_Info_set(info, "romio_pvfs2_posix_read", "enable");
	    MPI_Info_set(info, "romio_pvfs2_posix_write", "enable");
	    MPI_Info_set(info, "romio_cb_read", "disable");
	    MPI_Info_set(info, "romio_cb_write", "disable");
	    MPI_Info_set(info, "romio_pvfs2_dtype_read", "disable");
	    MPI_Info_set(info, "romio_pvfs2_dtype_write", "disable");
	    break;
	case DATASIEVE:
	    MPI_Info_set(info, "romio_pvfs2_posix_read", "enable");
	    MPI_Info_set(info, "romio_pvfs2_posix_write", "enable");
	    MPI_Info_set(info, "romio_cb_read", "enable");
	    MPI_Info_set(info, "romio_cb_write", "enable");
	    MPI_Info_set(info, "romio_pvfs2_dtype_read", "disable");
	    MPI_Info_set(info, "romio_pvfs2_dtype_write", "disable");
	    break;
	case LISTIO:
	    MPI_Info_set(info, "romio_pvfs2_posix_read", "disable");
	    MPI_Info_set(info, "romio_pvfs2_posix_write", "disable");
	    MPI_Info_set(info, "romio_cb_read", "disable");
	    MPI_Info_set(info, "romio_cb_write", "disable");
	    MPI_Info_set(info, "romio_pvfs2_dtype_read", "disable");
	    MPI_Info_set(info, "romio_pvfs2_dtype_write", "disable");
	    break;
	case DATATYPE:
	    MPI_Info_set(info, "romio_pvfs2_posix_read", "disable");
	    MPI_Info_set(info, "romio_pvfs2_posix_write", "disable");
	    MPI_Info_set(info, "romio_cb_read", "disable");
	    MPI_Info_set(info, "romio_cb_write", "disable");
	    MPI_Info_set(info, "romio_pvfs2_dtype_read", "enable");
	    MPI_Info_set(info, "romio_pvfs2_dtype_write", "enable");
	    break;
	case COLLECTIVE:
	    MPI_Info_set(info, "romio_pvfs2_posix_read", "disable");
	    MPI_Info_set(info, "romio_pvfs2_posix_write", "disable");
	    MPI_Info_set(info, "romio_cb_read", "enable");
	    MPI_Info_set(info, "romio_cb_write", "enable");
	    MPI_Info_set(info, "romio_pvfs2_dtype_read", "disable");
	    MPI_Info_set(info, "romio_pvfs2_dtype_write", "disable");
	    break;
	default:
	    printf("Impossible testtype. Exiting...\n");
	    exit(1);
    }

    MPI_Barrier(MPI_COMM_WORLD);

    if (rw_type == WRITE)
    {
	
	/* now time write_all */
	/* Removing old files */
	if (mynod == 0) {
	    printf("Removing old file...\n");
	    MPI_File_delete(filename, info);
	}
	MPI_Barrier(MPI_COMM_WORLD);
	
	MPI_File_open(MPI_COMM_WORLD, filename, 
		      MPI_MODE_CREATE | MPI_MODE_RDWR, 
		      info, &fh);
	MPI_File_set_view(fh, 0, MPI_CHAR, newtype, "native", info);

	MPI_Barrier(MPI_COMM_WORLD);
	stim = MPI_Wtime();

	if (testtype == COLLECTIVE)
	    MPI_File_write_all(fh, buf, bufcount, MPI_CHAR, &status);
	else
	    MPI_File_write(fh, buf, bufcount, MPI_CHAR, &status);
#ifdef LOCKING
	releaseLocks(filename, lockid);
#endif
	MPI_File_sync(fh);
	write_tim = MPI_Wtime() - stim;
	MPI_File_close(&fh);

	MPI_Allreduce(&write_tim, &new_write_tim, 1, MPI_DOUBLE, MPI_MAX,
		      MPI_COMM_WORLD);

	if (mynod == 0) {
	    write_bw = (array_of_gsizes[0]*array_of_gsizes[1]*
			array_of_gsizes[2]*sizeof(char))/
		(new_write_tim*1024.0*1024.0);
	    fprintf(stderr, "Global array size %d x %d x %d chars"
		    " (%.4f MBytes)\n", 
		    array_of_gsizes[0], array_of_gsizes[1], array_of_gsizes[2],
		    array_of_gsizes[0]*array_of_gsizes[1]*array_of_gsizes[2]
		    *sizeof(char)/1024.0/1024.0);
	    fprintf(stderr, "Collective write time = %f sec, Collective write bandwidth = %f Mbytes/sec\n", new_write_tim, write_bw);
	}
    }
    else /* rw_type == READ */
    {
	MPI_Barrier(MPI_COMM_WORLD);
	/* now time read_all */
	MPI_File_open(MPI_COMM_WORLD, filename, MPI_MODE_RDONLY, 
		      info, &fh); 
	MPI_File_set_view(fh, 0, MPI_CHAR, newtype, "native", info);
	
	MPI_Barrier(MPI_COMM_WORLD);
	stim = MPI_Wtime();

	if (testtype == COLLECTIVE)
	    MPI_File_read_all(fh, buf, bufcount, MPI_CHAR, &status);
	else
	    MPI_File_read(fh, buf, bufcount, MPI_CHAR, &status);    

	read_tim = MPI_Wtime() - stim;
	MPI_File_close(&fh);

	MPI_Allreduce(&read_tim, &new_read_tim, 1, MPI_DOUBLE, MPI_MAX,
                    MPI_COMM_WORLD);

	if (mynod == 0) {
	    read_bw = (array_of_gsizes[0]*array_of_gsizes[1]*
		       array_of_gsizes[2]*sizeof(char))/
		(new_read_tim*1024.0*1024.0);
	    fprintf(stderr, "Global array size %d x %d x %d chars"
		    " (%.4f MBytes)\n", 
		    array_of_gsizes[0], array_of_gsizes[1], array_of_gsizes[2],
		    array_of_gsizes[0]*array_of_gsizes[1]*array_of_gsizes[2]
		    *sizeof(char)/1024.0/1024.0);
	    fprintf(stderr, "Collective read time = %f sec, Collective read bandwidth = %f Mbytes/sec\n", new_read_tim, read_bw);
	}
    }

    MPI_Type_free(&newtype);
    free(buf);
    free(filename);
    
    MPI_Finalize();
    return 0;
}

void parse_args(int argc, char **argv,
		int *gsize,
		int *testtype,
		int *rw_type,
		int *filename_len,
		char **filename)
{
    int i = -1;

    if (argc == 1)
    {
	printf("coll_perf: requires that you specify:\n"
	       "gsize, "
	       "testtype(posix, datasieve, listio, datatype, collective)"
	       ", read/write, and filename\n"
	       "i.e. coll_perf -gsize 10 -posix -write -filename test.txt\n");
	exit(1);
    }
    for (i = 1; i < argc; i++)
    {
	if (strcmp(argv[i], "-gsize") == 0)
	{
	    i++;
	    *gsize = atoi(argv[i]);
	}
	else if (strcmp(argv[i], "-posix") == 0)
	    *testtype = POSIX;
	else if (strcmp(argv[i], "-datasieve") == 0)
	    *testtype = DATASIEVE;
	else if (strcmp(argv[i], "-listio") == 0)
	    *testtype = LISTIO;
	else if (strcmp(argv[i], "-datatype") == 0)
	    *testtype = DATATYPE;
	else if (strcmp(argv[i], "-collective") == 0)
	    *testtype = COLLECTIVE;
	else if (strcmp(argv[i], "-read") == 0)
	    *rw_type = READ;
	else if (strcmp(argv[i], "-write") == 0)
	    *rw_type = WRITE;
	else if (strcmp(argv[i], "-filename") == 0)
	{
	    i++;
	    *filename_len = strlen(argv[i]);
	    *filename = (char *) malloc((*filename_len)+1);
	    strcpy(*filename, argv[i]);
	}
	else
	{
	    printf("Erroneous parameter: %s\n", argv[i]);
	    exit(1);
	}
    }

    if (*testtype == DATASIEVE && *rw_type == WRITE)
    {
	printf("Cannot use datasieve during a write.  Exiting..\n");
	exit(1);
    }

    printf("parameters:\ntesttype %d (POSIX,DATASIEVE,LISTIO,DATATYPE"
	   ",COLLECTIVE) = (%d,%d,%d,%d,%d)\n"
	   "gsize = %d\n"
	   "read/write %d (read,write) = (%d,%d)\n"
	   "filename_len = %d\n"
	   "filename = %s\n", *testtype, POSIX, DATASIEVE, 
	   LISTIO, DATATYPE, COLLECTIVE, *gsize, *rw_type, READ, WRITE,
	   *filename_len, *filename);
}
