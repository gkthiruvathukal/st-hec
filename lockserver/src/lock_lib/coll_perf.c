#include "lock.h"
#include "mpi.h"
#include "mpio.h"  /* not necessary with MPICH 1.1.1 or HPMPI 1.4 */
#include "lockserverapi.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

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

void parse_args(int argc, char **argv,
		int *gsize,
		int *testtype,
		int *rw_type,
		int *filename_len,
		char **filename,
                int *lockservername_len,
                char **lockservername,
                int *lockserverport,
                int *locktype);

int main(int argc, char **argv)
{
    MPI_Datatype newtype;
    int i, ndims, array_of_gsizes[3], array_of_distribs[3];
    int order, nprocs, *buf, bufcount, mynod;
    int array_of_dargs[3], array_of_psizes[3];
    MPI_File fh;
    MPI_Status status;
    MPI_Info info;
    double stim, write_tim, new_write_tim, write_bw;
    double read_tim, new_read_tim, read_bw;
    char *filename = NULL;
    int gsize = -1, testtype = -1, rw_type = -1, filename_len = -1, lockid = -1;
    int lockservername_len = -1;
    char *lockservername = NULL;
    int lockserverport = -1;
    int locktype = -1; //effectively, this defaults to no locking

    MPI_Init(&argc,&argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &mynod);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);

    /* process 0 takes the file name as a command-line argument and 
     * broadcasts it to other processes */
    if (mynod == 0)
    {
	parse_args(argc, argv, &gsize, &testtype, &rw_type,
                   &filename_len, &filename, &lockservername_len,
                   &lockservername, &lockserverport, &locktype);
	MPI_Bcast(&filename_len, 1, MPI_INT, 0, MPI_COMM_WORLD);
	MPI_Bcast(filename, filename_len+1, MPI_CHAR, 0, MPI_COMM_WORLD);
        MPI_Bcast(&lockservername_len, 1, MPI_INT, 0, MPI_COMM_WORLD);
        MPI_Bcast(lockservername, lockservername_len + 1, MPI_CHAR, 0, 
                  MPI_COMM_WORLD);
    }
    else 
    {
	MPI_Bcast(&filename_len, 1, MPI_INT, 0, MPI_COMM_WORLD);
	filename = (char *) malloc(filename_len+1);
	MPI_Bcast(filename, filename_len+1, MPI_CHAR, 0, MPI_COMM_WORLD);
        MPI_Bcast(&lockservername_len, 1, MPI_INT, 0, MPI_COMM_WORLD);
        lockservername = (char*) malloc(lockservername_len + 1);
        MPI_Bcast(lockservername, lockservername_len + 1, MPI_CHAR, 0,
                  MPI_COMM_WORLD);
    }
    MPI_Bcast((void *) &gsize, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast((void *) &testtype, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast((void *) &rw_type, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast((void *) &lockserverport, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast((void *) &locktype, 1, MPI_INT, 0, MPI_COMM_WORLD);


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

    MPI_Type_create_darray(nprocs, mynod, ndims, array_of_gsizes,
			   array_of_distribs, array_of_dargs,
			   array_of_psizes, order, MPI_INT, &newtype);
    MPI_Type_commit(&newtype);

    MPI_Type_size(newtype, &bufcount);
    bufcount = bufcount/sizeof(int);
    buf = (int *) malloc(bufcount * sizeof(int));
    for (i = 0; i < bufcount; i++) {
      buf[i] = i;
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
	MPI_File_set_view(fh, 0, MPI_INT, newtype, "native", info);

	MPI_Barrier(MPI_COMM_WORLD);
	stim = MPI_Wtime();

	//printf("proc %d: before lock_datatype\n", mynod);
	fflush(stdout);

	lockid = lock_datatype(locktype,
		      bufcount,
		      MPI_INT,
		      0,
		      0,
		      newtype,
		      MPI_INT,
                      filename,
                      lockservername,
                      lockserverport);

	//printf("proc %d: after lock_datatype, before write\n", mynod);
	fflush(stdout);


	if (testtype == COLLECTIVE)
	    MPI_File_write_all(fh, buf, bufcount, MPI_INT, &status);
	else
	    //MPI_File_write(fh, buf, bufcount, MPI_INT, &status);

	//printf("proc %d: after write, before close\n", mynod);
	fflush(stdout);

        if (locktype != NO_LOCK) {
            releaseLocks(lockservername, lockserverport, filename, lockid);
        }

	MPI_File_sync(fh);
	write_tim = MPI_Wtime() - stim;
	MPI_File_close(&fh);

	//printf("proc %d: after close, before release\n", mynod);
	fflush(stdout);


	//printf("proc %d: after release\n", mynod);
	fflush(stdout);

	MPI_Allreduce(&write_tim, &new_write_tim, 1, MPI_DOUBLE, MPI_MAX,
		      MPI_COMM_WORLD);

	if (mynod == 0) {
	    write_bw = (array_of_gsizes[0]*array_of_gsizes[1]*array_of_gsizes[2]*sizeof(int))/(new_write_tim*1024.0*1024.0);
	    /*fprintf(stderr, "Global array size %d x %d x %d integers"
		    " (%.4f MBytes)\n", 
		    array_of_gsizes[0], array_of_gsizes[1], array_of_gsizes[2],
		    array_of_gsizes[0]*array_of_gsizes[1]*array_of_gsizes[2]
		    *sizeof(int)/1024.0/1024.0);
	    fprintf(stderr, "Collective write time = %f sec, Collective write bandwidth = %f Mbytes/sec\n", new_write_tim, write_bw);*/
            fprintf(stderr, "%f:%f\n", new_write_tim, write_bw);
	}
    }
    else /* rw_type == READ */
    {
	MPI_Barrier(MPI_COMM_WORLD);
	/* now time read_all */
	MPI_File_open(MPI_COMM_WORLD, filename, MPI_MODE_RDONLY, 
		      info, &fh); 
	MPI_File_set_view(fh, 0, MPI_INT, newtype, "native", info);
	
	MPI_Barrier(MPI_COMM_WORLD);
	stim = MPI_Wtime();

	if (testtype == COLLECTIVE)
	    MPI_File_read_all(fh, buf, bufcount, MPI_INT, &status);
	else
	    MPI_File_read(fh, buf, bufcount, MPI_INT, &status);    

	read_tim = MPI_Wtime() - stim;
	MPI_File_close(&fh);

	MPI_Allreduce(&read_tim, &new_read_tim, 1, MPI_DOUBLE, MPI_MAX,
                    MPI_COMM_WORLD);

	if (mynod == 0) {
	    read_bw = (array_of_gsizes[0]*array_of_gsizes[1]*array_of_gsizes[2]*sizeof(int))/(new_read_tim*1024.0*1024.0);
	    fprintf(stderr, "Global array size %d x %d x %d integers"
		    " (%.4f MBytes)\n", 
		    array_of_gsizes[0], array_of_gsizes[1], array_of_gsizes[2],
		    array_of_gsizes[0]*array_of_gsizes[1]*array_of_gsizes[2]
		    *sizeof(int)/1024.0/1024.0);
	    fprintf(stderr, "Collective read time = %f sec, Collective read bandwidth = %f Mbytes/sec\n", new_read_tim, read_bw);
	}
    }

    MPI_Info_free(&info);
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
		char **filename,
                int *lockservername_len,
                char **lockservername,
                int *lockserverport,
                int *locktype)
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
        else if (strcmp(argv[i], "-lsname") == 0)
        {
            i++;
            *lockservername_len = strlen(argv[i]);
            *lockservername = (char*) malloc((*filename_len)+1);
            strcpy(*lockservername, argv[i]);
        }
        else if (strcmp(argv[i], "-lsport") == 0)
        {
            i++;
            *lockserverport = atoi(argv[i]);
        }
        else if (strcmp(argv[i], "-locktype") == 0)
        {
            i++;
            *locktype = atoi(argv[i]);
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
