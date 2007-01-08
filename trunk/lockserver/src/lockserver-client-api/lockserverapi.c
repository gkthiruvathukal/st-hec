#include <math.h>
#include <stdlib.h>

#include "lockserverapi.h"
#include "messageClient.h"
#include "message.h"

#define FILE_LOCK_CLIENT_SERVICE_CLIENT_MESSAGE 201

int acquireLocks(char* serviceName, int servicePort, char* fileName,
                 int numLocks, int64_t offsets[], int64_t lengths[]) {
    int i;
    int lockID;

    printf("acquiring %d locks\n", numLocks);
    MessageClient client = newClient(serviceName, servicePort);

    Message m = newMessage();
    m->type = FILE_LOCK_CLIENT_SERVICE_CLIENT_MESSAGE;
    setStringParam(m, "functionName", "acquire");
    setStringParam(m, "fileName", fileName);
    setIntegerParam(m, "numLocks", numLocks);
    
    createLongArrayParam(m, "offsets", numLocks);
    createLongArrayParam(m, "lengths", numLocks);
    
    for (i = 0; i < numLocks; ++i) {
        setLongArrayParamValue(m, "offsets", i, offsets[i]);
        setLongArrayParamValue(m, "lengths", i, lengths[i]);
    }

    //printf("acquirelocks: Message to be sent:\n");
    //printMessage(m);

    Message reply = clientCall(client, m);
    clientDisconnect(client);
    //printf("acquirelocks: Reply:\n");
    //printMessage(reply);
    //printf("acquirelocks: before getIntegerParam()\n");
    lockID = getIntegerParam(reply, "lockID");

    destroyMessage(m);
    destroyMessage(reply);

    return lockID;
}

void acquireMoreLocks(char* serviceName, int servicePort, char* fileName,
                      int lockID, int numLocks, int64_t offsets[],
                      int64_t lengths[]) {
    int i;

    MessageClient client = newClient(serviceName, servicePort);

    Message m = newMessage();
    m->type = FILE_LOCK_CLIENT_SERVICE_CLIENT_MESSAGE;
    setStringParam(m, "functionName", "acquiremore");
    setStringParam(m, "fileName", fileName);
    setIntegerParam(m, "numLocks", numLocks);
    setIntegerParam(m, "lockID", lockID);
    
    createLongArrayParam(m, "offsets", numLocks);
    createLongArrayParam(m, "lengths", numLocks);
    
    for (i = 0; i < numLocks; ++i) {
        setLongArrayParamValue(m, "offsets", i, offsets[i]);
        setLongArrayParamValue(m, "lengths", i, lengths[i]);
    }
    //printf("acquiremorelocks: Message to be sent:\n");
    //printMessage(m);

    Message reply = clientCall(client, m);
    clientDisconnect(client);
    //printf("acquiremorelocks: Reply:\n");
    //printMessage(reply);
    
    destroyMessage(m);
    destroyMessage(reply);
}

int acquireBlockLocks(char* serviceName, int servicePort, char* fileName,
                      int numLocks, int64_t startBlocks[], int64_t lengths[]) {
    int i;
    int lockID;

    MessageClient client = newClient(serviceName, servicePort);

    Message m = newMessage();
    m->type = FILE_LOCK_CLIENT_SERVICE_CLIENT_MESSAGE;
    setStringParam(m, "functionName", "acquireblock");
    setStringParam(m, "fileName", fileName);
    setIntegerParam(m, "numLocks", numLocks);
    
    createLongArrayParam(m, "startblocks", numLocks);
    createLongArrayParam(m, "lengths", numLocks);
    
    for (i = 0; i < numLocks; ++i) {
        setLongArrayParamValue(m, "startblocks", i, startBlocks[i]);
        setLongArrayParamValue(m, "lengths", i, lengths[i]);
    }

    //printf("acquireblocklocks: Message to be sent:\n");
    //printMessage(m);

    Message reply = clientCall(client, m);
    clientDisconnect(client);
    //printf("acquirelocks: Reply:\n");
    //printMessage(reply);
    lockID = getIntegerParam(reply, "lockID");

    destroyMessage(m);
    destroyMessage(reply);

    return lockID;
}

void acquireMoreBlockLocks(char* serviceName, int servicePort, char* fileName,
                           int lockID, int numLocks, int64_t startBlocks[],
                           int64_t lengths[]) {
    int i;

    MessageClient client = newClient(serviceName, servicePort);

    Message m = newMessage();
    m->type = FILE_LOCK_CLIENT_SERVICE_CLIENT_MESSAGE;
    setStringParam(m, "functionName", "acquiremoreblock");
    setStringParam(m, "fileName", fileName);
    setIntegerParam(m, "numLocks", numLocks);
    setIntegerParam(m, "lockID", lockID);
    
    createLongArrayParam(m, "startblocks", numLocks);
    createLongArrayParam(m, "lengths", numLocks);
    
    for (i = 0; i < numLocks; ++i) {
        setLongArrayParamValue(m, "startblocks", i, startBlocks[i]);
        setLongArrayParamValue(m, "lengths", i, lengths[i]);
    }
    //printf("acquiremoreblocklocks: Message to be sent:\n");
    //printMessage(m);

    Message reply = clientCall(client, m);
    clientDisconnect(client);
    //printf("acquiremorelocks: Reply:\n");
    //printMessage(reply);
    
    destroyMessage(m);
    destroyMessage(reply);
}

void releaseLocks(char* serviceName, int servicePort,
                  char* fileName, int lockID) {

    MessageClient client = newClient(serviceName, servicePort);
    Message m = newMessage();
    m->type = FILE_LOCK_CLIENT_SERVICE_CLIENT_MESSAGE;
    setStringParam(m, "functionName", "release");
    setStringParam(m, "fileName", fileName);
    setIntegerParam(m, "lockID", lockID);
    Message reply = clientCall(client, m);
    clientDisconnect(client);
    
    destroyMessage(m);
    destroyMessage(reply);
}

void releaseBlockLocks(char* serviceName, int servicePort,
                       char* fileName, int lockID) {

    MessageClient client = newClient(serviceName, servicePort);
    Message m = newMessage();
    m->type = FILE_LOCK_CLIENT_SERVICE_CLIENT_MESSAGE;
    setStringParam(m, "functionName", "releaseblock");
    setStringParam(m, "fileName", fileName);
    setIntegerParam(m, "lockID", lockID);
    Message reply = clientCall(client, m);
    clientDisconnect(client);
    
    destroyMessage(m);
    destroyMessage(reply);
}

int acquireFileLock(char* serviceName, int servicePort, char* fileName) {
    int64_t offsets[] = {0LL};
    int64_t lengths[] = {INT64_MAX};
    return acquireLocks(serviceName, servicePort, fileName, 1, offsets, lengths);
}
