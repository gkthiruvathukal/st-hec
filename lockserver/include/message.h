#ifndef INFO_JHPC_MESSAGE_MESSAGE_H
#define INFO_JHPC_MESSAGE_MESSAGE_H

#include <stdint.h>
#include "avltbl.h"

#ifndef TRUE
#define TRUE 1
#endif

#ifndef FALSE
#define FALSE 0
#endif

#define DEBUG TRUE
#define MAX_DEBUG_LEVEL 1
#define DEFAULT_HASH_SIZE 32

/* Constants */
#define P_STRING "S$"
#define P_INTEGER "I$"
#define P_INTEGER_ARRAY "IA$"
#define P_ARRAY_LENGTH "AL$"
#define P_LONG "L$"
#define P_LONG_ARRAY "LA$"
#define P_BOOLEAN "B$"
#define MESSAGE_HEADER "SMA"

typedef char boolean;

typedef struct _Message {
	AVLTable parameters;
	int type;
	int tag;
	int length;
} _Message, *Message;

Message newMessage();
void destroyMessage(Message m);

void encode(Message m, int sockOut);
void decode(Message m, int sockIn);

void setStringParam(Message m, char* key, char* value);
char* getStringParam(Message m, char* key);

void setIntegerParam(Message m, char* key, int value);
int getIntegerParam(Message m, char* key);

void createIntegerArrayParam(Message m, char* key, int items);
int* getIntegerArrayParam(Message m, char* key);
void setIntegerArrayParamValue(Message m, char* key, int pos, int value);
int getIntegerArrayParamValue(Message m, char* key, int pos);

void setLongParam(Message m, char* key, int64_t value);
int64_t getLongParam(Message m, char* key);

void createLongArrayParam(Message m, char* key, int items);
int64_t* getLongArrayParam(Message m, char* key);
void setLongArrayParamValue(Message m, char* key, int pos, int64_t value);
int64_t getLongArrayParamValue(Message m, char* key, int pos);

void setBooleanParam(Message m, char* key, boolean value);
boolean getBooleanParam(Message m, char* key);

void printMessage(Message m);

/* TODO: Implement merge() function below... */
/* Message* merge(Message m1, Message m2); */

#endif /* INFO_JHPC_MESSAGE_MESSAGE_H */
