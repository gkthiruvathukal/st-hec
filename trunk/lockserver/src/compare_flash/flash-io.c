#include <string.h>
#include <stdio.h>
#include "mpi.h"
#include <stdlib.h>
#include <sys/time.h>
#include <unistd.h>
#include "buf/buf_ops.h"

/* Locking files */
#include "lock.h"
#include "lockserverapi.h"

//#define DEBUG

#define POSIX 0
#define DATASIEVE 1
#define LISTIO 2
#define DATATYPE 3
#define COLLECTIVE 4
#define UFS 5
#define NONCONTIG_TYPES 6

void parse_args(int argc, char **argv,
        int *posix,
        int *datasieve,
        int *listio,
        int *datatype,
        int *collective,
        int *ufs,
        int *lockservername_len,
        char **lockservername,
        int *lockserverport,
        int *locktype);

int run_test(int test_type, 
         int myid, int numprocs,
         char *filename, 
         MPI_Datatype *mem_dtype, 
         MPI_Datatype *file_dtype,
     char *lockservername,
     int lockserverport,
     int locktype);

/* orignial parameters */

enum {
    mblk = 8, /* was 80 */
    nxb = 8,
    nyb = 8,
    nzb = 8,
    nvar = 24,
    varsz = sizeof(double),
    nguard = 4,
};

/*
AC - Fails but we're looking for something simpler.
enum {
    mblk = 10,
    nxb = 6,
    nyb = 6,
    nzb = 6,
    nvar = 10,
    varsz = sizeof(double),
    nguard = 4,
};
*/
#if 0
enum {
    mblk = 2,
    nxb = 1,
    nyb = 1,
    nzb = 1,
    nvar = 3,
    varsz = sizeof(double),
    nguard = 2,
};
#endif

typedef struct test_param_s test_param;

/* this is the flash i/o unknown array */
double unknowns[mblk][nzb+2*nguard][nyb+2*nguard][nxb+2*nguard][nvar];

int main(int argc, char **argv)
{
    int m, z, y, x, v, myid = -1, numprocs = -1, extent = -1;
    int i;
#ifdef DEBUG
    int j;
#endif
    int noncontig_use[NONCONTIG_TYPES] = {0, 0, 0, 0, 0, 0};
    int noncontig_types[NONCONTIG_TYPES] = {POSIX, 
                        DATASIEVE, 
                        LISTIO, 
                        DATATYPE, 
                        COLLECTIVE,
                        UFS};
    char *noncontig_names[NONCONTIG_TYPES] = {"posix",
                          "datasieve",
                          "listio",
                          "datatype",
                          "collective",
                          "ufs"};
    int lens[3], disps[3];
    MPI_Datatype xh, xguard, yh, yguard, zh, zguard, bh, mem_dtype, 
    file_xyz, file_blk, fixed_file_blk, file_dtype, types[3];
    double value = -1;
    char filename[100];
    //char *dir = "pvfs2:/mnt/pvfs2";
    char *dir = "/pvfs/scratch/aarestad";
    //char *dir = ".";

    /* Lock server stuff */
    int lockservername_len = -1;
    char *lockservername = NULL;
    int lockserverport = -1;
    int locktype = -1;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &myid);
    MPI_Comm_size(MPI_COMM_WORLD, &numprocs);

    /* argument passing */
    if (myid == 0) {
        parse_args(argc, argv,
           &noncontig_use[POSIX],
           &noncontig_use[DATASIEVE],
           &noncontig_use[LISTIO],
           &noncontig_use[DATATYPE],
           &noncontig_use[COLLECTIVE],
           &noncontig_use[UFS],
           &lockservername_len,
           &lockservername, &lockserverport, &locktype);
        MPI_Bcast(&lockservername_len, 1, MPI_INT, 0, MPI_COMM_WORLD);
        MPI_Bcast(lockservername, lockservername_len+1, MPI_CHAR,
                  0, MPI_COMM_WORLD);
    } else {
        MPI_Bcast(&lockservername_len, 1, MPI_INT, 0, MPI_COMM_WORLD);
        lockservername = (char*) malloc(lockservername_len+1);
        MPI_Bcast(lockservername, lockservername_len+1, MPI_CHAR,
                  0, MPI_COMM_WORLD);
    }
    
    MPI_Bcast((void *) &noncontig_use[POSIX], 
          1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast((void *) &noncontig_use[DATASIEVE], 
          1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast((void *) &noncontig_use[LISTIO], 
          1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast((void *) &noncontig_use[DATATYPE], 
          1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast((void *) &noncontig_use[COLLECTIVE], 
          1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast((void *) &noncontig_use[UFS], 
          1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast((void*) &lockserverport, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast((void*) &locktype, 1, MPI_INT, 0, MPI_COMM_WORLD);

    //printf("proc %d: lsname=<%s>\n", myid, lockservername);
    //printf("proc %d: lockserverport=%d\n", myid, lockserverport);
    //printf("proc %d: locktype=%d\n", myid, locktype);

    /* Initialize the FLASH blocks */
    value = -1.0;
    for (v=0; v < nvar; v++) {
    for (m=0; m < mblk; m++) {
        for (z=0; z < nzb + 2*nguard; z++) {
        for (y=0; y < nyb + 2*nguard; y++) {
            for (x=0; x < nxb + 2*nguard; x++) {
            unknowns[m][z][y][x][v] = value;
            value = value - 1.0;
            }
        }
        }
    }
    }
    
    /* Initialize the data parts of the FLASH blocks */
    value = (myid+1)*1000000.0;
    for (v=0; v < nvar; v++) {
    for (m=0; m < mblk; m++) {
        for (z=nguard; z < nguard + nzb; z++) {
        for (y=nguard; y < nguard + nyb; y++) {
            for (x=nguard; x < nguard + nxb; x++) {
            unknowns[m][z][y][x][v] = value;
            value = value + 1.0;
            }
        }
        }
    }
    }

    /* datatype to grab one variable across all X values (row) */
    MPI_Type_vector(nxb, 1, nvar, MPI_DOUBLE, &xh);

    /* resize to jump over guardcells in X */
    lens[0]  = 1;
    lens[1]  = 1;
    lens[2]  = 1;
    disps[0] = 0;
    disps[1] = nguard*nvar*varsz;
    disps[2] = (2*nguard+nxb)*nvar*varsz;
    types[0] = MPI_LB;
    types[1] = xh;
    types[2] = MPI_UB;
    MPI_Type_struct(3, lens, disps, types, &xguard);

    /* datatype to grab a plane of variables in Y */
    MPI_Type_contiguous(nyb, xguard, &yh);
   
    /* resize to jump guardcells in Y */
    lens[0]  = 1;
    lens[1]  = 1;
    lens[2]  = 1;
    disps[0] = 0;
    disps[1] = (2*nguard+nxb)*nguard*nvar*varsz;
    disps[2] = (2*nguard+nxb)*(2*nguard+nyb)*nvar*varsz;
    types[0] = MPI_LB;
    types[1] = yh;
    types[2] = MPI_UB;
    MPI_Type_struct(3, lens, disps, types, &yguard);

    /* datatype for cube of variables in Z */
    MPI_Type_contiguous(nzb, yguard, &zh);

    /* resize to jump guardcells in Z */
    lens[0]  = 1;
    lens[1]  = 1;
    lens[2]  = 1;
    disps[0] = 0;
    disps[1] = (2*nguard+nxb)*(2*nguard+nyb)*nguard*nvar*varsz;
    disps[2] = (2*nguard+nxb)*(2*nguard+nyb)*(2*nguard+nzb)*nvar*varsz;
    types[0] = MPI_LB;
    types[1] = zh;
    types[2] = MPI_UB;
    MPI_Type_struct(3, lens, disps, types, &zguard);

    /* datatype to cover all blocks */
    MPI_Type_contiguous(mblk, zguard, &bh);
    MPI_Type_extent(bh, &extent);
  
    /* datatype to cover all variables */
    MPI_Type_hvector(nvar, 1, varsz, bh, &mem_dtype);  
    MPI_Type_commit(&mem_dtype);

    /* file datatype */
    /* The block of x,y,z */
    MPI_Type_contiguous(nxb*nyb*nzb, MPI_DOUBLE, &file_xyz); 

    MPI_Type_extent(file_xyz, &extent);

    /* Vectors of blocks for procs */
    MPI_Type_vector(mblk, 1, numprocs, file_xyz, &file_blk); 

    MPI_Type_extent(file_blk, &extent);

    /* Add the extra file_xyz s to the end of the last mblk */
    lens[0]  = 1;
    lens[1]  = 1;
    disps[0] = 0;
    disps[1] = mblk*numprocs*nzb*nyb*nxb*varsz;

    types[0] = file_blk;
    types[1] = MPI_UB;

    /*printf("unknowns initial address = %x new extent = %d\n", 
       (int) &unknowns,
       disps[1]);*/
    MPI_Type_struct(2, lens, disps, types, &fixed_file_blk);
    MPI_Type_contiguous(nvar, fixed_file_blk, &file_dtype);
    MPI_Type_commit(&file_dtype);

    /* size of datatypes and supposed size */
#ifdef DEBUG
    if (myid == 0) 
    {
    int size;
    MPI_Type_size(mem_dtype, &size);
    MPI_Type_extent(mem_dtype, &extent);
    /*printf("Memory datatype size   = %d and should be %d\n", 
           size, mblk*nxb*nyb*nzb*nvar*varsz);
    printf("Memory datatype extent = %d and should be %d\n", 
           extent, mblk
           *(nxb+2*nguard)*(nyb+2*nguard)*(nzb+2*nguard)*
           nvar*varsz);*/
    MPI_Type_size(file_dtype, &size);
    MPI_Type_extent(file_dtype, &extent);
    /*printf("File datatype size   = %d and should be %d\n", 
           size, mblk*nxb*nyb*nzb*nvar*varsz);
    printf("File datatype extent = %d and should be %d\n",
           extent, numprocs*mblk*nxb*nyb*nzb*nvar*varsz);*/

    }
#endif

#ifdef DEBUG
    /* Initialize all file data to 0 */
    for (i = 0; i < NONCONTIG_TYPES; i++)
    {
    if (myid == 0 && noncontig_use[i] == 1)
    {

        int err;
        MPI_File fh;
        MPI_Status status;
        double *buf = NULL;
        if ((buf = malloc(extent)) == NULL)
        {
        printf("malloc failed with size %d\n", 
               extent);
        exit(1);
        }
        for (j = 0; j < extent / sizeof(double); j++)
        buf[j] = 0.1;
        if (i != UFS)
        err = sprintf(filename, "%s/%s", dir, noncontig_names[i]);
        else
        err = sprintf(filename, "%s", noncontig_names[i]);
            //printf("filename: %s\n", filename);
        MPI_File_delete(filename, MPI_INFO_NULL);
        err = MPI_File_open(MPI_COMM_SELF, filename,
                MPI_MODE_CREATE | 
                MPI_MODE_WRONLY, MPI_INFO_NULL, &fh);
        MPI_File_set_view(fh, 0, MPI_DOUBLE, MPI_DOUBLE, "native", 
                  MPI_INFO_NULL);
        //MPI_File_write(fh, buf, extent / sizeof(double), MPI_DOUBLE, &status);
        MPI_File_close(&fh);
        free(buf);
    }
    }
#endif

    /* Run at least one of these tests to gather timing results
     * and perhaps use to diff later */
    for (i = 0; i < NONCONTIG_TYPES; i++)
    {
    if (noncontig_use[i] == 1)
    {
        if (i != UFS)
        sprintf(filename, "%s/%s", dir, noncontig_names[i]);
        else
        sprintf(filename, "%s", noncontig_names[i]);
        run_test(noncontig_types[i], myid, numprocs, filename,
             &mem_dtype, &file_dtype, lockservername, lockserverport, locktype);
    }
    }             
  
#ifdef DEBUG
    /* Read all file data back to see changes */
    for (i = 0; i < NONCONTIG_TYPES; i++)
    {
    if (myid == 0 && noncontig_use[i] == 1)
    {
        int err;
        MPI_File fh;
        MPI_Status status;
        double *buf = NULL;
        if ((buf = malloc(extent)) == NULL)
        {
        printf("malloc failed with size %d\n", 
               extent);
        exit(1);
        }
        for (j = 0; j < extent / sizeof(double); j++)
                buf[j] = 999.0;
        if (i != UFS)
        sprintf(filename, "%s/%s", dir, noncontig_names[i]);
        else 
        sprintf(filename, "%s", noncontig_names[i]);
        err = MPI_File_open(MPI_COMM_SELF, filename,
                MPI_MODE_RDONLY, MPI_INFO_NULL, &fh);
        MPI_File_set_view(fh, 0, MPI_DOUBLE, MPI_DOUBLE, "native", 
                  MPI_INFO_NULL);
        MPI_File_read(fh, buf, extent / sizeof(double), 
              MPI_DOUBLE, &status);
        switch(i)
        {
        case POSIX:
            buf_print("POSIX buffer", DOUBLE, 
                  buf, 0, extent/sizeof(double)); 
            break;
        case DATASIEVE:
            buf_print("DATASIEVE buffer", DOUBLE, 
                  buf, 0, extent/sizeof(double)); 
            break;
        case LISTIO:
            buf_print("LISTIO buffer", DOUBLE, 
                  buf, 0, extent/sizeof(double)); 
            break;
        case DATATYPE:
            buf_print("DATATYPE buffer", DOUBLE, 
                  buf, 0, extent/sizeof(double)); 
            break;
        case COLLECTIVE:
            buf_print("COLLECTIVE buffer", DOUBLE, 
                  buf, 0, extent/sizeof(double)); 
            break;
        case UFS:
            buf_print("UFS buffer", DOUBLE, 
                  buf, 0, extent/sizeof(double)); 
            break;
        default:
            printf("Impossible type %d\n", i);
            exit(1);
        }            
        MPI_File_close(&fh);
        free(buf);
    }
    }
#endif

    MPI_Barrier(MPI_COMM_WORLD);
    MPI_Finalize();
    return 0;
}

void parse_args(int argc, char **argv,
        int *posix,
        int *datasieve,
        int *listio,
        int *datatype,
        int *collective,
        int *ufs,
        int *lockservername_len,
        char **lockservername,
        int *lockserverport,
        int *locktype)
{
    int i;
    if (argc == 1) {
    printf("Flash I/O requires you specify at least one test:\n"
           "i.e. (posix, datasieve, listio, datatype, "
           "collective)\n"
           "For example, if you want just posix and collective,\n"
           "type 'mpirun flash-io posix collective\n");
    exit(1);
    } else {
        for (i = 1; i < argc; i++) {
            if (strcmp(argv[i], "posix") == 0) 
                *posix = 1;
            else if (strcmp(argv[i], "datasieve") == 0) 
                *datasieve = 1;
            else if (strcmp(argv[i], "listio") == 0) 
                *listio = 1;
            else if (strcmp(argv[i], "datatype") == 0) 
                *datatype = 1;
            else if (strcmp(argv[i], "collective") == 0) 
                *collective = 1;
            else if (strcmp(argv[i], "ufs") == 0) 
                *ufs = 1;
            else if (strcmp(argv[i], "-lsname") == 0) {
                i++;
                *lockservername_len = strlen(argv[i]);
                *lockservername = (char*) malloc((*lockservername_len)+1);
                strcpy(*lockservername, argv[i]);
            } else if (strcmp(argv[i], "-lsport") == 0) {
                i++;
                *lockserverport = atoi(argv[i]);
            } else if (strcmp(argv[i], "-locktype") == 0) {
                i++;
                *locktype = atoi(argv[i]);
            }
        }
    }
    
    if (*posix == 0 && *datasieve == 0 && *listio == 0 &&
    *datatype == 0 && *collective == 0 && ufs == 0)
    {
    printf("Your arguments entered are not listed in the choices.\n"
           "Flash I/O requires you specify at least one test:\n"
           "i.e. (posix, datasieve, listio, datatype, "
           "collective, ufs)\n"
           "For example, if you want just posix and collective,\n"
           "type 'mpirun flash-io posix collective\n");
    exit(1);
    }
}

int run_test(int test_type, 
         int myid, int numprocs,
         char *filename, 
         MPI_Datatype *mem_dtype, 
         MPI_Datatype *file_dtype,
     char *lockservername,
     int lockserverport,
     int locktype)
{
    int err = -1;
    MPI_File fh;
    MPI_Info info;
    MPI_Status status;
    double begin, lock, write, unlock, sync, close;
    double lockt, writet, unlockt, synct, closet, totalt;
    double locktime, writetime, unlocktime, synctime, closetime, totaltime;

    int lockid = -1;
    
    MPI_Barrier(MPI_COMM_WORLD); 
    MPI_Info_create(&info);
    switch (test_type) {
    case POSIX:
        MPI_Info_set(info, "romio_pvfs2_posix_write", "enable");
        MPI_Info_set(info, "romio_pvfs2_dtype_write", "disable");
        MPI_Info_set(info, "romio_cb_write", "disable");
        break;
    case DATASIEVE:
        MPI_Info_set(info, "romio_pvfs2_posix_write", "enable");
        MPI_Info_set(info, "romio_pvfs2_dtype_write", "disable");
        MPI_Info_set(info, "romio_cb_write", "enable");
        break;
    case LISTIO:
        MPI_Info_set(info, "romio_pvfs2_posix_write", "disable");
        MPI_Info_set(info, "romio_pvfs2_dtype_write", "disable");
        break;
    case DATATYPE:
        MPI_Info_set(info, "romio_pvfs2_posix_write", "disable");
        MPI_Info_set(info, "romio_pvfs2_dtype_write", "enable");
        break;
    case COLLECTIVE:
        MPI_Info_set(info, "romio_pvfs2_dtype_write", "disable");
        MPI_Info_set(info, "romio_pvfs2_listio_write", "disable");
        MPI_Info_set(info, "romio_cb_write", "enable");
        break;
    case UFS:
        MPI_Info_set(info, "romio_cb_write", "disable");
        break;
    default:
        printf("Impossible test type.  Exiting.\n");
        exit(1);
    }
#ifndef DEBUG
    MPI_File_delete(filename, MPI_INFO_NULL);    
#endif
    err = MPI_File_open(MPI_COMM_WORLD, filename, 
            MPI_MODE_CREATE | MPI_MODE_WRONLY, info, &fh);

    if (err != 0)
        printf("MPI_File_open failed\n");

    MPI_File_set_view(fh, myid*nxb*nyb*nzb*varsz, 
              MPI_DOUBLE, *file_dtype, "native", info);

    MPI_Barrier(MPI_COMM_WORLD);
    begin = MPI_Wtime();

    if (locktype != NO_LOCK) {
        lockid = lock_datatype(locktype, 1, *mem_dtype,
                               myid*nxb*nyb*nzb*varsz, 0, 
                               *file_dtype, MPI_DOUBLE, filename,
                               lockservername, lockserverport);
    }
    lock = MPI_Wtime();

    if (test_type == COLLECTIVE)
        err = MPI_File_write_all(fh, unknowns, 1, *mem_dtype, &status);    
    else
        //err = MPI_File_write(fh, unknowns, 1, *mem_dtype, &status);
    if (err != 0)
        printf("MPI_File_write/write_all failed\n");

    write = MPI_Wtime();

    if (locktype != NO_LOCK) {
        releaseLocks(lockservername, lockserverport, filename, lockid);
    }

    unlock = MPI_Wtime();

    MPI_File_sync(fh);

    sync = MPI_Wtime();

    MPI_File_close(&fh);

    close = MPI_Wtime();

    lockt   = lock - begin;
    writet  = write - lock;
    unlockt = unlock - write;
    synct   = sync - unlock;
    closet  = close - sync;
    totalt  = close - begin;

    MPI_Allreduce(&lockt,   &locktime, 1, MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD);
    MPI_Allreduce(&writet,  &writetime, 1, MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD);
    MPI_Allreduce(&unlockt, &unlocktime, 1, MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD);
    MPI_Allreduce(&synct,   &synctime, 1, MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD);
    MPI_Allreduce(&closet,  &closetime, 1, MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD);
    MPI_Allreduce(&totalt,  &totaltime, 1, MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD);

    if (myid == 0) 
    {
    switch (test_type)
    {
        case POSIX:
        /*printf("Flash : %d bytes %4.5f secs"
               " - %3.5fMbytes/sec - POSIX\n",
               numprocs*mblk*nxb*nyb*nzb*nvar*varsz,
               time, 
               ((float) numprocs*mblk*nxb*nyb*nzb*nvar*varsz) / 
               (1024*1024*time));*/
        /*fprintf(stdout, "posix:%d:%d:%4.5f:%3.5f\n",
                locktype,
                numprocs*mblk*nxb*nyb*nzb*nvar*varsz,
                time,
                ((float) numprocs*mblk*nxb*nyb*nzb*nvar*varsz) /
                (1024*1024*time));*/
        printf("posix:%d:%d:%4.5f:%4.5f:%4.5f:%4.5f:%4.5f:%4.5f:%3.5f\n",
                locktype,
                numprocs*mblk*nxb*nyb*nzb*nvar*varsz,
                locktime,
                writetime,
                unlocktime,
                synctime,
                closetime,
                totaltime,
                ((float) numprocs*mblk*nxb*nyb*nzb*nvar*varsz) /
                (1024*1024*totaltime));
        break;
        case DATASIEVE:
        /*printf("Flash : %d bytes %4.5f secs"
               " - %3.5fMbytes/sec - DATASIEVE\n",
               numprocs*mblk*nxb*nyb*nzb*nvar*varsz,
               time, 
               ((float) numprocs*mblk*nxb*nyb*nzb*nvar*varsz) / 
               (1024*1024*time));*/
        printf("datasieve:%d:%d:%4.5f:%4.5f:%4.5f:%4.5f:%4.5f:%4.5f:%3.5f\n",
                locktype,
                numprocs*mblk*nxb*nyb*nzb*nvar*varsz,
                locktime,
                writetime,
                unlocktime,
                synctime,
                closetime,
                totaltime,
                ((float) numprocs*mblk*nxb*nyb*nzb*nvar*varsz) /
                (1024*1024*totaltime));
        break;
        case LISTIO:
        /*printf("Flash : %d bytes %4.5f secs"
               " - %3.5fMbytes/sec - LISTIO\n",
               numprocs*mblk*nxb*nyb*nzb*nvar*varsz,
               time, 
               ((float) numprocs*mblk*nxb*nyb*nzb*nvar*varsz) / 
               (1024*1024*time));*/
        printf("listio:%d:%d:%4.5f:%4.5f:%4.5f:%4.5f:%4.5f:%4.5f:%3.5f\n",
                locktype,
                numprocs*mblk*nxb*nyb*nzb*nvar*varsz,
                locktime,
                writetime,
                unlocktime,
                synctime,
                closetime,
                totaltime,
                ((float) numprocs*mblk*nxb*nyb*nzb*nvar*varsz) /
                (1024*1024*totaltime));
        break;
        case DATATYPE:
        /*printf("Flash : %d bytes %4.5f secs"
               " - %3.5fMbytes/sec - DATATYPE\n",
               numprocs*mblk*nxb*nyb*nzb*nvar*varsz,
               time, 
               ((float) numprocs*mblk*nxb*nyb*nzb*nvar*varsz) / 
               (1024*1024*time));*/
        printf("datatype:%d:%d:%4.5f:%4.5f:%4.5f:%4.5f:%4.5f:%4.5f:%3.5f\n",
                locktype,
                numprocs*mblk*nxb*nyb*nzb*nvar*varsz,
                locktime,
                writetime,
                unlocktime,
                synctime,
                closetime,
                totaltime,
                ((float) numprocs*mblk*nxb*nyb*nzb*nvar*varsz) /
                (1024*1024*totaltime));
        break;
        case COLLECTIVE:
        /*printf("Flash : %d bytes %4.5f secs"
               " - %3.5fMbytes/sec - COLLECTIVE\n",
               numprocs*mblk*nxb*nyb*nzb*nvar*varsz,
               time, 
               ((float) numprocs*mblk*nxb*nyb*nzb*nvar*varsz) / 
               (1024*1024*time));*/
        printf("collective:%d:%d:%4.5f:%4.5f:%4.5f:%4.5f:%4.5f:%4.5f:%3.5f\n",
                locktype,
                numprocs*mblk*nxb*nyb*nzb*nvar*varsz,
                locktime,
                writetime,
                unlocktime,
                synctime,
                closetime,
                totaltime,
                ((float) numprocs*mblk*nxb*nyb*nzb*nvar*varsz) /
                (1024*1024*totaltime));
        break;
        case UFS:
        /*printf("Flash : %d bytes %4.5f secs"
               " - %3.5fMbytes/sec - UFS\n",
               numprocs*mblk*nxb*nyb*nzb*nvar*varsz,
               time, 
               ((float) numprocs*mblk*nxb*nyb*nzb*nvar*varsz) / 
               (1024*1024*time));*/
        printf("ufs:%d:%d:%4.5f:%4.5f:%4.5f:%4.5f:%4.5f:%4.5f:%3.5f\n",
                locktype,
                numprocs*mblk*nxb*nyb*nzb*nvar*varsz,
                locktime,
                writetime,
                unlocktime,
                synctime,
                closetime,
                totaltime,
                ((float) numprocs*mblk*nxb*nyb*nzb*nvar*varsz) /
                (1024*1024*totaltime));
        break;
    }
    }
    return 0;
}
