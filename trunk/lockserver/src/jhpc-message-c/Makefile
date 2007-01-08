INCLUDE = ../../include
LIBALL_INCLUDE = ../../liball
LIBPATH = ../../lib

CC = gcc

CFLAGS = -g -Wall

AR = ar

RANLIB = ranlib

LIBMESSAGE_A_OBJECTS =  message.o messageClient.o javasendrecv.o

all: libmessage.a testsend testrecv vanillaClient

libmessage.a: $(LIBMESSAGE_A_OBJECTS)
	rm -f ../../lib/libmessage.a
	$(AR) cru ../../lib/libmessage.a $(LIBMESSAGE_A_OBJECTS)
	$(RANLIB) ../../lib/libmessage.a

.c.o:
	$(CC) $(CFLAGS) -I$(INCLUDE) -I$(LIBALL_INCLUDE) -c $<

clean:
	rm -f *.o *.exe testsend testrecv ../../lib/libmessage.a

testsend: testsend.o libmessage.a
	$(CC) $(CFLAGS) -o $@ testsend.o ../../lib/libmessage.a
	
testrecv: testrecv.o libmessage.a
	$(CC) $(CFLAGS) -o $@ testrecv.o ../../lib/libmessage.a
	
vanillaClient: vanillaClient.o libmessage.a
	$(CC) -lm $(CFLAGS) -o $@ vanillaClient.o ../../lib/libmessage.a ../../lib/liball.a
