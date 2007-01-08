#include <stdlib.h>

#include "messageClient.h"
#include "message.h"

#define VANILLA_SERVICE_PORT    1999
#define VANILLA_SERVICE_MESSAGE 100

int main(int argc, char* argv[]) {
	char* host;
	MessageClient conn;
	Message m, reply;
	int lockId = 25;
	int numberOfLocks = 2;
	int offset0 = 10;
	int length0 = 5;
	int offset1 = 20;
	int length1 = 5;
	int64_t long0 = 12345678901234567LL;
	int64_t long1 = -23456789012345678LL;
	int i = 0;
	
	int offsets1[] = {10, 20};
	int lengths1[] = {5, 5};
	int64_t offsets2[] = { 12345678901234567LL, 23456789012345678LL };
	int64_t lengths2[] = { 1000000000000000LL,  1000000000000000LL };
	
	if (argc >= 2) {
		host = argv[1];
	} else {
		host = "localhost";
	}

	if ((conn = newClient(host, VANILLA_SERVICE_PORT)) == NULL) {
		printf("%s: failed to create message client\n", argv[0]);
		return 1;
	}

	m = newMessage();
	m->type = VANILLA_SERVICE_MESSAGE;
	setStringParam(m, "functionName", "acquire");
	setIntegerParam(m, "lockId", lockId);
	setStringParam(m, "fileName", "xyz.dat");
	setIntegerParam(m, "numberOfLocks", numberOfLocks);

	setIntegerParam(m, "offset0", offset0);
	setIntegerParam(m, "length0", length0);

	setIntegerParam(m, "offset1", offset1);
	setIntegerParam(m, "length1", length1);
	
	setLongParam(m, "long0", long0);
	setLongParam(m, "long1", long1);
	
	printf("finished setting initial params\n");
	fflush(stdout);

	createIntegerArrayParam(m, "offsets1", 2);
	printf("finished createIntegerArrayParam\n");
	for (i = 0; i < 2; ++i) {
		setIntegerArrayParamValue(m, "offsets1", i, offsets1[i]);
	}
	
	createIntegerArrayParam(m, "lengths1", 2);
	for (i = 0; i < 2; ++i) {
		setIntegerArrayParamValue(m, "lengths1", i, lengths1[i]);
	}
	
	createLongArrayParam(m, "offsets2", 2);
	for (i = 0; i < 2; ++i) {
		setLongArrayParamValue(m, "offsets2", i, offsets2[i]);
	}
	
	createLongArrayParam(m, "lengths2", 2);
	for (i = 0; i < 2; ++i) {
		setLongArrayParamValue(m, "lengths2", i, lengths2[i]);
	}
	
	printf("Message:\n");
	printMessage(m);
	printf("functionName:%s\n", getStringParam(m, "functionName"));
	printf("lockId:%d\n", getIntegerParam(m, "lockId"));

	reply = clientCall(conn, m);
	printf("Message instance received from server:\n");
	printMessage(reply);
	printf("numberOfLocksGranted:%d\n", getIntegerParam(reply, "numberOfLocksGranted"));
	printf("lockId:%d\n", getIntegerParam(reply, "lockId"));
	clientDisconnect(conn);
	
	destroyMessage(reply);
	destroyMessage(m);
	return 0;
}
