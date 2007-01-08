#ifndef LOCKSERVERAPI_H
#define LOCKSERVERAPI_H

#include <stdint.h>

/* Returns the lock ID after acquiring the specified locks */
int acquireLocks(char* serviceName, int servicePort, char* fileName,
                 int numLocks, int64_t offsets[], int64_t lengths[]);

void acquireMoreLocks(char* serviceName, int servicePort, char* fileName,
                      int lockID, int numLocks, int64_t offsets[],
                      int64_t lengths[]);

int acquireBlockLocks(char* serviceName, int servicePort, char* fileName,
                      int numLocks, int64_t startBlocks[], int64_t lengths[]);

void acquireMoreBlockLocks(char* serviceName, int servicePort, char* fileName,
                           int lockID, int numLocks, int64_t startBlocks[],
                           int64_t lengths[]);

/* 
 * General file lock function - just calls
 * acquireLocks(serviceName, servicePort, fileName, 1, {0}, {INT64_MAX});
 */
int acquireFileLock(char* serviceName, int servicePort, char* fileName);

void releaseLocks(char* serviceName, int servicePort, char* fileName,
                  int lockID);

void releaseBlockLocks(char* serviceName, int servicePort, char* fileName,
                       int lockID);

#endif
