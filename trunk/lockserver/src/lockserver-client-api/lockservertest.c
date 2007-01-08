#include <stdio.h>
#include <unistd.h>

#include "lockserverapi.h"

#define SERVICE_NAME "localhost"
#define SERVICE_PORT 46822

int main(int argc, char* argv[]) {
	int64_t offsets[] = {0LL, 128LL, 256LL};
	int64_t lengths[] = {32LL, 64LL, 128LL};
	int64_t offsets2[] = {512LL, 600LL, 700LL};
	int64_t lengths2[] = {80LL, 75LL, 200LL};
	char* fileName = "/tmp/test";
	char* fileName2 = "/tmp/test2";
	
	int lockID = acquireLocks(SERVICE_NAME, SERVICE_PORT, fileName,
                                  3, offsets, lengths);
	printf("lockservertest: Locks acquired; lock ID=%d\n", lockID);
	printf("lockservertest: Sleeping to emulate work...\n");
	sleep(1);
	acquireMoreLocks(SERVICE_NAME, SERVICE_PORT, fileName, lockID,
                         3, offsets2, lengths2);
	printf("lockservertest: More locks acquired\n");
	printf("lockservertest: Sleeping to emulate work...\n");
	sleep(1);
	releaseLocks(SERVICE_NAME, SERVICE_PORT, fileName, lockID);
	printf("lockservertest: Locks on %s released\n", fileName);
	sleep(1);
	int lockID2 = acquireFileLock(SERVICE_NAME, SERVICE_PORT, fileName2);
	printf("lockservertest: file lock acquired on file %s; lock ID=%d\n",
		  fileName, lockID2);
	printf("lockservertest: Sleeping to emulate work...\n");
	sleep(1);
	releaseLocks(SERVICE_NAME, SERVICE_PORT, fileName2, lockID2);
	printf("lockservertest: Locks on %s released\n", fileName2);
	return 0;
}
