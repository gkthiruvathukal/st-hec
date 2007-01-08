#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <strings.h>
#include <string.h>

#include "messageClient.h"
#include "message.h"

MessageClient newClient(const char* host, const int port) {
	int sd, rc;
	
    MessageClient client = (MessageClient) malloc(sizeof(_MessageClient));
    bzero(client, sizeof(_MessageClient));
    
    if ((client->remoteHost = gethostbyname(host)) == NULL) {
		printf("MessageClient::newClient(): unknown host '%s'\n", host);
		perror(NULL);
		free(client);
		return NULL;
	}

 	client->serverAddr.sin_family = client->remoteHost->h_addrtype;
	memcpy((char *) &client->serverAddr.sin_addr.s_addr,
	       client->remoteHost->h_addr_list[0],
	       client->remoteHost->h_length);
	client->serverAddr.sin_port = htons(port);

 	/* create socket */
  	sd = socket(AF_INET, SOCK_STREAM, 0);
	if (sd < 0) {
		perror("cannot open socket");
		free(client);
		return NULL;
	}

	/* bind any port number */
	client->localAddr.sin_family = AF_INET;
	client->localAddr.sin_addr.s_addr = htonl(INADDR_ANY);
	client->localAddr.sin_port = htons(0);

	rc = bind(sd, (struct sockaddr*) &client->localAddr, sizeof(client->localAddr));
	if (rc < 0) {
		printf("MessageClient::newClient(): cannot bind port TCP %u\n", port);
		perror(NULL);
		free(client);
		return NULL;
	}
    
    client->sock = sd;
    
	/* connect to server */
	rc = connect(client->sock,
				(struct sockaddr*) &client->serverAddr,
				sizeof(client->serverAddr));
	if (rc < 0) {
		perror("cannot connect");
		free(client);
		return NULL;
	}

    return client;
}

Message clientCall(const MessageClient c, const Message m) {
    encode(m, c->sock);
    Message reply = newMessage();
    decode(reply, c->sock);
    return reply;
}

void clientDisconnect(MessageClient c) {
    Message m = newMessage();
    m->type = 0;
    setStringParam(m, "$disconnect", "$disconnect");
    clientCall(c, m);
    shutdown(c->sock, SHUT_RDWR);
    free(c);
}
