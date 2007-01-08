#define _ISOC99_SOURCE /* to avoid warning about llabs() being undeclared */

#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <string.h>
#include <strings.h>
#include <stdint.h>
#include <math.h>
#include <netinet/in.h>

#include "message.h"
#include "avltbl.h"
#include "avltree.h"
#include "iavltbl.h"
#include "javasendrecv.h"

/* Cygwin doesn't define MSG_WAITALL */
#ifndef MSG_WAITALL
#define MSG_WAITALL 0
#endif

Message newMessage() {
    Message m = (Message) malloc(sizeof(_Message));
    bzero(m, sizeof(_Message));
    AVLTable tbl = AVLTableNew(NULL);
    m->parameters = tbl;
    return m;
}

static void disposeItem(void* item) {
	AVLTableItem ati = (AVLTableItem) item;
	free(ati->key);
	free(ati->element);
}

void destroyMessage(Message m) {
	AVLTreeDispose(m->parameters->Space, disposeItem);
	free(m->parameters);
    free(m);
}

static int getArrayLength(const Message m, const char* key) {
	char* tmpKey;
	tmpKey = (char*) calloc(strlen(key) + 4, sizeof(char)); /* 4 = 3-char prefix + NUL */
	strncpy(tmpKey, P_ARRAY_LENGTH, strlen(P_ARRAY_LENGTH));
	strncat(tmpKey, key, strlen(key));
	int len = getIntegerParam(m, tmpKey);
	free(tmpKey);
	return len;
}

static void setArrayLength(const Message m, const char* key, int length) {
	char* tmpKey;
	tmpKey = (char*) calloc(strlen(key) + 4, sizeof(char)); /* 4 = 3-char prefix + NUL */
	strncpy(tmpKey, P_ARRAY_LENGTH, strlen(P_ARRAY_LENGTH));
	strncat(tmpKey, key, strlen(key));
	setIntegerParam(m, tmpKey, length);
	free(tmpKey);
}

static void encodeIntArray(const int sockOut, const void* array, const int len) {
	ssize_t rc = 0;
	int i = 0;
	int* values = (int*) array;
	int netLen = htonl(len);
	rc = send(sockOut, &netLen, sizeof(int), 0);
    if (rc < 0) {
        perror("Message->encodeIntArray(): error sending array length");
		return;
    }
	for (i=0; i < len; i++) {
		int netVal = htonl(values[i]);
		rc = send(sockOut, &netVal, sizeof(int), 0);
		if (rc < 0) {
			perror("Message->encodeIntArray(): error sending array value");
			return;
		}
	}
}

static void encodeLongArray(const int sockOut, const void* array, const int len) {
	ssize_t rc = 0;
	int i = 0;
	int64_t* values = (int64_t*) array;
	int netLen = htonl(len);
	rc = send(sockOut, &netLen, sizeof(int), 0);
    if (rc < 0) {
        perror("Message->encodeLongArray(): error sending array length");
		return;
    }
	for (i=0; i < len; i++) {
		int64_t val = values[i];
//#if __BYTE_ORDER == __BIG_ENDIAN
#if __BYTE_ORDER == __LITTLE_ENDIAN
		unsigned int firstWordToSend = htonl(val >> 32);
#else
		unsigned int firstWordToSend = htonl(0xffffffff & val);
#endif
		rc = send(sockOut, &firstWordToSend, sizeof(unsigned int), 0);
		if (rc < 0) {
			perror("Message->encodeLongArray(): error sending array value");
			return;
		}
//#if __BYTE_ORDER == __BIG_ENDIAN
#if __BYTE_ORDER == __LITTLE_ENDIAN
		unsigned int secondWordToSend = htonl(0xffffffff & val);
#else
		unsigned int secondWordToSend = htonl(val >> 32);
#endif
		rc = send(sockOut, &secondWordToSend, sizeof(unsigned int), 0);
		if (rc < 0) {
			perror("Message->encodeLongArray(): error sending array value");
			return;
		}		
	}
}

void encode(const Message m, const int sockOut) {
    ssize_t  rc = 0;
    int netType   = htonl(m->type);
    int netTag    = htonl(m->tag);
    int netLength = htonl(m->length);
    int netSize   = htonl(m->parameters->Space->size);
    
    sendStringToJava(sockOut, MESSAGE_HEADER, strlen(MESSAGE_HEADER), 0);

    rc = send(sockOut, &netLength, sizeof(int), 0);
    if (rc < 0) {
        perror("Message->encode(): error sending length");
		return;
    }
    rc = send(sockOut, &netType, sizeof(int), 0);
    if (rc < 0) {
        perror("Message->encode(): error sending type");
		return;
    }
    rc = send(sockOut, &netTag, sizeof(int), 0);
    if (rc < 0) {
        perror("Message->encode(): error sending tag");
		return;
    }
    rc = send(sockOut, &netSize, sizeof(int), 0);
    if (rc < 0) {
        perror("Message->encode(): error sending size");
		return;
    }
    
    /* Enumerate way through parameters, sending keys and values... */
    AVLTableIterator ati = AVLTableIteratorNew(m->parameters, 1);
    while (!AVLTableIteratorAtBottom(ati)) {
		AVLTableItem item = AVLTableIteratorCurrentData(ati);
		char* key   = item->key;
		void* value = item->element;
		
		sendStringToJava(sockOut, key, strlen(key), 0);
		
		if (strncmp(key, P_INTEGER_ARRAY, strlen(P_INTEGER_ARRAY)) == 0) {
			char* tmpKey = calloc(strlen(key)-2, sizeof(char));
			strcpy(tmpKey, key + 3);
			int len = getArrayLength(m, tmpKey);
			if (len == -1) {
				perror("Message->encode(): no valid length found for array!");
				return;
			}
			free(tmpKey);
			encodeIntArray(sockOut, value, len);
		} else if (strncmp(key, P_LONG_ARRAY, strlen(P_LONG_ARRAY)) == 0) {
			char* tmpKey = calloc(strlen(key)-2, sizeof(char));
			strcpy(tmpKey, key + 3);
			int len = getArrayLength(m, tmpKey);
			if (len == -1) {
				perror("Message->encode(): no valid length found for array!");
				return;
			}
			free(tmpKey);
			encodeLongArray(sockOut, value, len);
		} else {
			sendStringToJava(sockOut, (char*) value, strlen((char*) value), 0);
		}
		
		AVLTableIteratorAdvance(ati);
    }
}

static void* decodeIntArray(Message m, const char* key, const int sockIn) {
	ssize_t rc;
    uint32_t tmp;
    int length;
    int i;
	rc = recv(sockIn, &tmp, sizeof(int), MSG_WAITALL);
    if (rc < 0) {
		perror("Message->decodeIntArray(): error receiving array length");
		return NULL;
    }
    length = ntohl(tmp);
    setArrayLength(m, key, length);
    
	int* values = (int*) calloc(length, sizeof(int));
	for (i=0; i < length; i++) {
		rc = recv(sockIn, &tmp, sizeof(int), MSG_WAITALL);
	    if (rc < 0) {
			perror("Message->decodeIntArray(): error receiving array value");
			return NULL;
	    }
	    values[i] = ntohl(tmp);
	}
	
	return values;
}

static void* decodeLongArray(Message m, const char* key, const int sockIn) {
	ssize_t rc;
    uint32_t tmp;
    uint64_t tmp2;
    uint64_t tmp3;
    int length;
    int i;
	rc = recv(sockIn, &tmp, sizeof(int), MSG_WAITALL);
    if (rc < 0) {
		perror("Message->decodeLongArray(): error receiving array length");
		return NULL;
    }
    length = ntohl(tmp);
    setArrayLength(m, key, length);
    
	int64_t* values = (int64_t*) calloc(length, sizeof(int64_t));
	for (i=0; i < length; i++) {
		rc = recv(sockIn, &tmp, sizeof(int), MSG_WAITALL);
	    if (rc < 0) {
			perror("Message->decodeIntArray(): error receiving array value");
			return NULL;
	    }
	    tmp2 = ntohl(tmp);
//#if __BYTE_ORDER == __BIG_ENDIAN	    
#if __BYTE_ORDER == __LITTLE_ENDIAN	    
	    tmp2 = tmp2 << 32;
#endif
		rc = recv(sockIn, &tmp, sizeof(int), MSG_WAITALL);
	    if (rc < 0) {
			perror("Message->decodeIntArray(): error receiving array value");
			return NULL;
	    }
//#if __BYTE_ORDER == __BIG_ENDIAN	    
#if __BYTE_ORDER == __LITTLE_ENDIAN	    
	    tmp2 += ntohl(tmp);
#else
		tmp3 = ntohl(tmp);
		tmp3 = tmp3 << 32;
		tmp2 += tmp3;
#endif  
	    values[i] = tmp2;
	}
	return values;
}

void decode(Message m, const int sockIn) {
    ssize_t rc;
    uint32_t tmp;
    uint32_t parameterCount;
    int i;
    char* key;
    void* value;
    char* header;
    
    header = recvStringFromJava(sockIn, 0);
    if (header == NULL) {
		perror("Message->decode(): error receiving header");
		return;
    }
    /* Dispose of header right away */
    free(header);
    
    rc = recv(sockIn, &tmp, sizeof(int), MSG_WAITALL);
    if (rc < 0) {
		perror("Message->decode(): error receiving length");
		return;
    }
    m->length = ntohl(tmp);

    rc = recv(sockIn, &tmp, sizeof(int), MSG_WAITALL);
    if (rc < 0) {
		perror("Message->decode(): error receiving type");
		return;
    }
    m->type = ntohl(tmp);

    rc = recv(sockIn, &tmp, sizeof(int), MSG_WAITALL);
    if (rc < 0) {
		perror("Message->decode(): error receiving tag");
		return;
    }
    m->tag = ntohl(tmp);

    rc = recv(sockIn, &tmp, sizeof(int), MSG_WAITALL);
    if (rc < 0) {
		perror("Message->decode(): error receiving parameter count");
		return;
    }
    parameterCount = ntohl(tmp);
    
    /* Read all keys and values based on parameter count... */
    for (i = 0; i < parameterCount; ++i) {
    		key = recvStringFromJava(sockIn, 0);
        if (key == NULL) {
			perror("Message->decode(): error receiving key");
			return;
		}
		if (strncmp(key, P_INTEGER_ARRAY, strlen(P_INTEGER_ARRAY)) == 0) {
			value = decodeIntArray(m, key, sockIn);
		} else if (strncmp(key, P_LONG_ARRAY, strlen(P_LONG_ARRAY)) == 0) {
			value = decodeLongArray(m, key, sockIn);
		} else {
			value = recvStringFromJava(sockIn, 0);
		}
		if (value == NULL) {
			perror("Message->decode(): error receiving value");
			return;
		}

        /* Place key/value in m->parameters */
        AVLTablePut(m->parameters, key, value, V_Void);
    }
}

void setStringParam(Message m, char* key, char* value) {
	char* newKey;
	char* newValue;
	newKey = (char*) calloc(strlen(key) + 3, sizeof(char)); /* 3 = 2-char prefix + NUL */
	newValue = (char*) calloc(strlen(value) + 1, sizeof(char));
	strncpy(newKey, P_STRING, strlen(P_STRING));
	strncat(newKey, key, strlen(key));
	strcpy(newValue, value);
	AVLTablePut(m->parameters, newKey, newValue, V_Void);
}

void setIntegerParam(Message m, char* key, int value) {
	char* newKey;
	char* newValue;
	int numDigitsValue;
	newKey = (char*) calloc(strlen(key) + 3, sizeof(char)); /* 3 = 2-char prefix + NUL */
	strncpy(newKey, P_INTEGER, strlen(P_INTEGER));
	strncat(newKey, key, strlen(key));
	if (value == 0) {
		numDigitsValue = 1;
	} else {
		numDigitsValue = (int) floor(log10(abs(value))) + 1;
		/* Add one more "digit" if value < 0 */
		if (value < 0) {
			numDigitsValue += 1;
		}
	}
	newValue = (char*) calloc(numDigitsValue + 1, sizeof(char));
	sprintf(newValue, "%d", value);
	AVLTablePut(m->parameters, newKey, newValue, V_Void);
}

void setLongParam(Message m, char* key, int64_t value) {
	char* newKey;
	char* newValue;
	int numDigitsValue;
	newKey = (char*) calloc(strlen(key) + 3, sizeof(char)); /* 3 = 2-char prefix + NUL */
	strncpy(newKey, P_LONG, strlen(P_LONG));
	strncat(newKey, key, strlen(key));
	if (value == 0) {
		numDigitsValue = 1;
	} else {
		numDigitsValue = (int) floor(log10(llabs(value))) + 1;
		/* Add one more "digit" if value < 0 */
		if (value < 0) {
			numDigitsValue += 1;
		}
	}
	newValue = (char*) calloc(numDigitsValue + 1, sizeof(char));
	sprintf(newValue, "%lld", value);
	AVLTablePut(m->parameters, newKey, newValue, V_Void);
}

void setBooleanParam(Message m, char* key, boolean value) {
	char* newKey;
	char* newValue;
	newKey = (char*) calloc(strlen(key) + 3, sizeof(char)); /* 3 = 2-char prefix + NUL */
	strncpy(newKey, P_BOOLEAN, strlen(P_BOOLEAN));
	strncat(newKey, key, strlen(key));
	newValue = (char*) calloc(2, sizeof(char));
	/* Ensure we have only one digit for our boolean value */
	if (value != 0) {
		value = 1;
	}
	sprintf(newValue, "%d", value);
	AVLTablePut(m->parameters, newKey, newValue, V_Void);
}

char* getStringParam(Message m, char* key) {
	char* tmpKey;
	tmpKey = (char*) calloc(strlen(key) + 3, sizeof(char)); /* 3 = 2-char prefix + NUL */
	strncpy(tmpKey, P_STRING, strlen(P_STRING));
	strncat(tmpKey, key, strlen(key));
	
	char* retval = (char*) AVLTableFind(m->parameters, tmpKey, V_Void);
	free(tmpKey);
	return retval;
}

int getIntegerParam(Message m, char* key) {
	char* tmpKey;
	int retVal;
	/*printf("getIntegerParam:m=%x\n", m);
	printf("getIntegerParam:key=<%s>\n", key);*/
	tmpKey = (char*) calloc(strlen(key) + 3, sizeof(char)); /* 3 = 2-char prefix + NUL */
	strncpy(tmpKey, P_INTEGER, strlen(P_INTEGER));
	strncat(tmpKey, key, strlen(key));
	/*printf("getIntegerParam:tmpKey=<%s>\n", tmpKey);*/
	char* value = (char*) AVLTableFind(m->parameters, tmpKey, V_Void);
	/*printf("getIntegerParam:value=<%s>\n", value);*/
	if (value != NULL) {
		retVal = atoi(value);
	} else {
		/* printf("getIntegerParam: returned value NULL\n"); */
		retVal = -1;
	}
	free(tmpKey);
	return retVal;
}

int64_t getLongParam(Message m, char* key) {
	char* tmpKey;
	int64_t retVal;
	tmpKey = (char*) calloc(strlen(key) + 3, sizeof(char)); /* 3 = 2-char prefix + NUL */
	strncpy(tmpKey, P_LONG, strlen(P_LONG));
	strncat(tmpKey, key, strlen(key));

	char* value = (char*) AVLTableFind(m->parameters, tmpKey, V_Void);
	if (value != NULL) {
		retVal = atoll(value);
	} else {
		retVal = -1;
	}
	free(tmpKey);
	return retVal;
}

boolean getBooleanParam(Message m, char* key) {
	char* tmpKey;
	boolean retVal;
	tmpKey = (char*) calloc(strlen(key) + 3, sizeof(char)); /* 3 = 2-char prefix + NUL */
	strncpy(tmpKey, P_BOOLEAN, strlen(P_BOOLEAN));
	strncat(tmpKey, key, strlen(key));
	
	char* value = (char*) AVLTableFind(m->parameters, tmpKey, V_Void);
	if (value != NULL) {
		retVal = atoi(value);
	} else {
		retVal = -1;
	}
	free(tmpKey);
	return retVal;
}

void createIntegerArrayParam(Message m, char* key, int items) {
	char* newKey;
	newKey = (char*) calloc(strlen(key) + 4, sizeof(char)); /* 4 = 3-char prefix + NUL */
	strncpy(newKey, P_INTEGER_ARRAY, strlen(P_INTEGER_ARRAY));
	strncat(newKey, key, strlen(key));
	void* values = calloc(items, sizeof(int));
	AVLTablePut(m->parameters, newKey, values, V_Void);
	setArrayLength(m, key, items);
}
int* getIntegerArrayParam(Message m, char* key) {
	char* tmpKey;
	tmpKey = (char*) calloc(strlen(key) + 4, sizeof(char)); /* 4 = 3-char prefix + NUL */
	strncpy(tmpKey, P_INTEGER_ARRAY, strlen(P_INTEGER_ARRAY));
	strncat(tmpKey, key, strlen(key));
	int* value = (int*) AVLTableFind(m->parameters, tmpKey, V_Void);
	free(tmpKey);
	return value;
}
void setIntegerArrayParamValue(Message m, char* key, int pos, int value) {
	getIntegerArrayParam(m, key)[pos] = value;
}
int getIntegerArrayParamValue(Message m, char* key, int pos) {
	return getIntegerArrayParam(m, key)[pos];
}

void createLongArrayParam(Message m, char* key, int items) {
	char* newKey;
	newKey = (char*) calloc(strlen(key) + 4, sizeof(char)); /* 4 = 3-char prefix + NUL */
	strncpy(newKey, P_LONG_ARRAY, strlen(P_LONG_ARRAY));
	strncat(newKey, key, strlen(key));
	void* values = calloc(items, sizeof(int64_t));
	AVLTablePut(m->parameters, newKey, values, V_Void);
	setArrayLength(m, key, items);
}
int64_t* getLongArrayParam(Message m, char* key) {
	char* tmpKey;
	tmpKey = (char*) calloc(strlen(key) + 4, sizeof(char)); /* 4 = 3-char prefix + NUL */
	strncpy(tmpKey, P_LONG_ARRAY, strlen(P_LONG_ARRAY));
	strncat(tmpKey, key, strlen(key));
	int64_t* value = (int64_t*) AVLTableFind(m->parameters, tmpKey, V_Void);
	free(tmpKey);
	return value;
}
void setLongArrayParamValue(Message m, char* key, int pos, int64_t value) {
	getLongArrayParam(m, key)[pos] = value;
}
int64_t getLongArrayParamValue(Message m, char* key, int pos) {
	return getLongArrayParam(m, key)[pos];
}

void printMessage(Message m) {
	printf("Message: type=%d\n", m->type);
	printf("Parameters:\n");
	
	AVLTableIterator ati = AVLTableIteratorNew(m->parameters, 1);
    while (!AVLTableIteratorAtBottom(ati)) {
    		AVLTableItem item = AVLTableIteratorCurrentData(ati);
		char* key   = item->key;
		void* value = (void*) item->element;
		printf("'%s'=", key);
		if (strncmp(key, P_INTEGER_ARRAY, strlen(P_INTEGER_ARRAY)) == 0) {
			int* array = (int*) value;
			char* tmpKey = calloc(strlen(key)-2, sizeof(char));
			strcpy(tmpKey, key + 3);
			int arraySize = getArrayLength(m, tmpKey);
			int i;
			for (i = 0; i < arraySize; ++i) {
				printf("[%d]", array[i]);
			}
			printf("\n");
			free(tmpKey);
		} else if (strncmp(key, P_LONG_ARRAY, strlen(P_LONG_ARRAY)) == 0) {
			int64_t* array = (int64_t*) value;
			char* tmpKey = calloc(strlen(key)-2, sizeof(char));
			strcpy(tmpKey, key + 3);
			int arraySize = getArrayLength(m, tmpKey);
			int i;
			for (i = 0; i < arraySize; ++i) {
				printf("[%lld]", array[i]);
			}
			printf("\n");
			free(tmpKey);
		} else {
			printf("'%s'\n", (char*) value);
		}
		AVLTableIteratorAdvance(ati);
    }
}
