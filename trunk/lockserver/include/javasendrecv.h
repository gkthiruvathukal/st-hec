#ifndef JAVASENDRECV_H
#define JAVASENDRECV_H

void sendStringToJava(int s, const char* msg, int strlen, int flags);
char* recvStringFromJava(int s, int flags);

#endif /* JAVASENDRECV_H */

