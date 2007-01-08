#ifndef INFO_JHPC_MESSAGE_MESSAGECLIENT_H
#define INFO_JHPC_MESSAGE_MESSAGECLIENT_H

#include <netdb.h> /* for struct hostent and gethostbyname() */
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <unistd.h>

#include "message.h"

typedef struct _MessageClient {
    int sock;
    struct hostent*    remoteHost;
    struct sockaddr_in localAddr;
    struct sockaddr_in serverAddr;
} _MessageClient, *MessageClient;

MessageClient newClient(const char* host, const int port);

Message clientCall(const MessageClient c, const Message m);

void clientDisconnect(MessageClient c);
#endif /* INFO_JHPC_MESSAGE_MESSAGECLIENT_H */
