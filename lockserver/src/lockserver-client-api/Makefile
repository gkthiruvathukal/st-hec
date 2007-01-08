INCLUDE = ../../include
LIBALL_INCLUDE = ../../liball

CC = gcc

CFLAGS = -Wall -g

.c.o:
	$(CC) $(CFLAGS) -I$(INCLUDE) -I$(LIBALL_INCLUDE) -c $<

all: lockservertest lockservertest2
	
lockservertest: lockservertest.o lockserverapi.o
	$(CC) $(CFLAGS) -o lockservertest -lm lockservertest.o lockserverapi.o ../../lib/libmessage.a ../../lib/liball.a

lockservertest2: lockservertest2.o lockserverapi.o
	$(CC) $(CFLAGS) -o lockservertest2 -lm lockservertest2.o lockserverapi.o ../../lib/libmessage.a ../../lib/liball.a

clean:
	rm -f *.o lockservertest *.exe
