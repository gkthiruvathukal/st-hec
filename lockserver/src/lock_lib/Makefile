mpi_dir  = $(HOME)/mpich2-1.0.2p1
romio_dir = $(mpi_dir)/src/mpi/romio
cc       = $(mpi_dir)/bin/mpicc
INCLUDE_DIRS = -I ${romio_dir}/adio/include -I ${romio_dir}/include -I ${romio_dir}/../include -I ${romio_dir}/../../include  -I ${romio_dir}/../../../include -I ../../include
#CFLAGS      =  -I/home/aching/locking/mpich2-1.0.2p1/src/binding/f77 -I/home/aching/locking/mpich2-1.0.2p1/src/binding/f77 -I/home/aching/locking/mpich2-1.0.2p1/src/mpid/ch3/include -I/home/aching/locking/mpich2-1.0.2p1/src/mpid/ch3/include -I/home/aching/locking/mpich2-1.0.2p1/src/mpid/common/datatype -I/home/aching/locking/mpich2-1.0.2p1/src/mpid/common/datatype -I/home/aching/locking/mpich2-1.0.2p1/src/mpid/ch3/channels/sock/include -I/home/aching/locking/mpich2-1.0.2p1/src/mpid/ch3/channels/sock/include -I/home/aching/locking/mpich2-1.0.2p1/src/mpid/common/sock -I/home/aching/locking/mpich2-1.0.2p1/src/mpid/common/sock -I/home/aching/locking/mpich2-1.0.2p1/src/mpid/common/sock/poll -I/home/aching/locking/mpich2-1.0.2p1/src/mpid/common/sock/poll -I /home/aching/locking/pvfs-1.6.2/include -I /home/aching/locking/pvfs-1.6.2/include -DFORTRANDOUBLEUNDERSCORE -I /home/aching/locking/pvfs-1.6.2/include -I /home/aching/locking/pvfs-1.6.2/include -DFORTRANDOUBLEUNDERSCORE -D_LARGEFILE64_SOURCE -D_FILE_OFFSET_BITS=64 -DHAVE_ROMIOCONF_H ${INCLUDE_DIRS}  -Wall -Wstrict-prototypes -g
CFLAGS = $(INCLUDE_DIRS) -Wall -Wstrict-prototypes -g

MY_LIBS = -lm ../lockserver-client-api/lockserverapi.o ../../lib/libmessage.a ../../lib/liball.a

EXECUTABLE = coll_perf

all: $(EXECUTABLE)

#object files
.c.o:
	$(cc) $(CFLAGS) -c $*.c -o $*.o

coll_perf: coll_perf.o lock.o lock.h
	$(cc) $(CFLAGS) -o coll_perf *.c $(MY_LIBS)

clean:
	rm -f *.o core $(EXECUTABLE) *~ 
