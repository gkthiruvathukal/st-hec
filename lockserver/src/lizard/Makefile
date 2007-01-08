#MPI_DIR = /chibahomes/ching/mpich-1.2.4
#MPI_DIR = /home/aching/datatype/mpich2-1.0.1
mpi_dir = $(HOME)/mpich2-1.0.2p1
romio_dir = $(mpi_dir)/src/mpi/romio
SH = /bin/sh
MPICC=$(mpi_dir)/bin/mpicc

INCLUDE_DIRS = -I ${romio_dir}/adio/include -I ${romio_dir}/include -I ${romio_dir}/../include -I ${romio_dir}/../../include  -I ${romio_dir}/../../../include -I ../../include -I ../lock_lib

MY_CFLAGS = $(INCLUDE_DIRS) -Wall -g $(CFLAGS) -DDEBUG

MY_LDFLAGS = $(LDFLAGS)	
MY_LIBS = -lm ../lockserver-client-api/lockserverapi.o ../lock_lib/lock.o ../../lib/libmessage.a ../../lib/liball.a

L_LIBS = $(MY_LIBS)


.c.o:	$?
	$(MPICC) $(MY_CFLAGS) -c $?

default: lizard 

all: lizard lizard-tile lizard-dtype-tile lizard-listio-tile lizard-coll-tile lizard-frame

lizard: lizard.o
	$(MPICC) $(MY_CFLAGS) -o $@ $(LDFLAGS) $(?) $(L_LIBS)

lizard-coll: lizard.c
	$(MPICC) $(MY_CFLAGS) -DUSE_COLLECTIVE -DUSE_SUBTILE_READS -o $@ $(LDFLAGS) \
	lizard.c $(L_LIBS)

lizard-listio: lizard.c
	$(MPICC) $(MY_CFLAGS) -DUSE_LISTIO -o $@ $(LDFLAGS) \
	lizard.c $(L_LIBS)

lizard-coll-tile: lizard.c
	$(MPICC) $(MY_CFLAGS) -DUSE_COLLECTIVE -DUSE_TILE_READS -o $@ $(LDFLAGS) \
	lizard.c $(L_LIBS)

lizard-tile: lizard.c
	$(MPICC) $(MY_CFLAGS) -DUSE_TILE_READS -o $@ $(LDFLAGS) lizard.c $(L_LIBS)

lizard-listio-tile: lizard.c
	$(MPICC) $(MY_CFLAGS) -DUSE_LISTIO -DUSE_TILE_READS -o $@ $(LDFLAGS) \
	lizard.c $(L_LIBS)

lizard-dtype-tile: lizard.c
	$(MPICC) $(MY_CFLAGS) -DUSE_DTYPE -DUSE_TILE_READS -o $@ $(LDFLAGS) \
	lizard.c $(L_LIBS)


lizard-frame: lizard.c
	$(MPICC) $(MY_CFLAGS) -DUSE_FRAME_READS -o $@ $(LDFLAGS) lizard.c $(L_LIBS)


clean:
	rm -f *.o *~ lizard lizard-coll lizard-listio lizard-frame lizard-tile lizard-coll-tile lizard-listio-tile lizard-dtype-tile


