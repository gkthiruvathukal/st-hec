mpi_dir   = $(HOME)/mpich2-1.0.2p1
romio_dir = $(mpi_dir)/src/mpi/romio
cc        = $(mpi_dir)/bin/mpicc

INCLUDE_DIRS = -I ${romio_dir}/adio/include -I ${romio_dir}/include -I ${romio_dir}/../include -I ${romio_dir}/../../include  -I ${romio_dir}/../../../include -I ../../include -I ../lock_lib

CFLAGS	= $(INCLUDE_DIRS) -Wall -Wstrict-prototypes -g 

OBJECTS	= buf/buf_ops.o flash-io.o ../lock_lib/lock.o
MY_LIBS = -lm ../lockserver-client-api/lockserverapi.o ../../lib/libmessage.a ../../lib/liball.a

EXECUTABLE = flash-io

all: $(EXECUTABLE)

#object files
.c.o:
	$(cc) $(CFLAGS) -c $*.c

flash-io: $(OBJECTS)
	mv -f buf_ops.o buf/
	$(cc) $(CFLAGS) -o $(EXECUTABLE) $(OBJECTS) $(MY_LIBS)

clean:
	rm -f *.o *~ core $(EXECUTABLE) buf/*.o

superclean:
	rm -f *.o *~ core $(EXECUTABLE) buf/*.o buf/*~ \
	posix listio collective datatype ufs
