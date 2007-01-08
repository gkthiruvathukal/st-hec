MPICC=mpicc

INCLUDE = ../../include
LIBALL_INCLUDE = ../../liball

MY_CFLAGS = -Wall -g $(CFLAGS) 

MY_LDFLAGS = $(LDFLAGS)	
MY_LIBS = -lm ../lockserver-client-api/lockserverapi.o ../../lib/libmessage.a ../../lib/liball.a

.c.o:	$?
	$(MPICC) -I$(INCLUDE) -I$(LIBALL_INCLUDE) $(MY_CFLAGS) -c $? -o $(@)

default: coll_perf

all: coll_perf

coll_perf: coll_perf.o
	$(MPICC) $(MY_CFLAGS) -o $@ $(LDFLAGS) $(?) $(MY_LIBS)

clean:
	rm -f *.o *~ coll_perf 


