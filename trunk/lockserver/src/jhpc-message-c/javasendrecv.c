#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "javasendrecv.h"

/* Send string pointed to by msg of length len to socket s with given flags */
void sendStringToJava(int s, const char* msg, int len, int flags) {
	int rc;
	unsigned short totalBytes, netTotalBytes;
	/* unsigned short bufPos; */
	/*unsigned char c; */
	/*char buf[2];*/
	/* char* buf; */
	
	/* First, the total number of bytes needed to represent all the characters
	 * of msg is calculated.
	 */
#if 0
	totalBytes = 0;
		 
	for (i = 0; i < len; ++i) {
		c = msg[i];
		if (0x01 <= c && 0x7f >= c) {
			totalBytes += 1;
		} else if (c == 0x0 || 0x80 <= c) {
			totalBytes += 2;
		}
		/* Higher-valued characters are represented as 3 bytes, but
		 * we don't worry about that since we are just handling ASCII
		 * characters
		 */
	}
#endif
	
	/* buf = (char*) calloc(totalBytes, sizeof(char)); */

	/* Transform the string for sending */
	/*
	bufPos = 0;

	for (i = 0; i < len; ++i) {
		c = msg[i];
		if (0x01 <= c && 0x7f >= c) {
			buf[bufPos] = c;
			bufPos += 1;
		} else if (c == 0x0 || 0x80 <= c) {
			buf[bufPos] = 0xc0 | (0x1f & (c >> 6));
			buf[bufPos + 1] = 0x80 | (0x3f & c);
			bufPos += 2;
		}
	}
	*/

	totalBytes = strlen(msg);
	netTotalBytes = htons(totalBytes);

	/* Send the string buffer length first */
	rc = send(s, &netTotalBytes, sizeof(unsigned short), flags);
	if (rc < 0) {
		perror("error sending string length");
		return;
	}

	/* Now send the buffer... 
     * note that this fails for non-ASCII strings!
     */

	rc = send(s, msg, totalBytes, flags);
	if (rc < 0) {
		perror("error sending string buffer");
		return;
	}
	
	/*
	for (i = 0; i < len; ++i) {
		c = msg[i];
		if (0x01 <= c && 0x7f >= c) {
			rc = send(s, &c, sizeof(char), flags);
			if (rc < 0) {
				perror("error sending char");
				return;
			}
		} else if (c == 0x0 || 0x80 <= c) {
			buf[0] = 0xc0 | (0x1f & (c >> 6));
			buf[1] = 0x80 | (0x3f & c);
			rc = send(s, buf, sizeof(char) * 2, flags);
			if (rc < 0) {
				perror("error sending char");
				return;
			}
		}
	}*/
}

char* recvStringFromJava(int s, int flags) {
	int rc;
	unsigned short len, netLen;
	char* buf;
	
	rc = recv(s, &netLen, sizeof(short), 0);
	if (rc < 0) {
		perror("error reading buffer length");
		return NULL;
	}
	
	len = ntohs(netLen);
	
	/* For simplicity, we're assuming that the received string is all ASCII
	 * characters with no NULs - see docs for java.io.DataOutput for details
	 * on how non-ASCII chars (and NUL) are represented */
	buf = (char*) calloc(len + 1, sizeof(char));
	
	rc = recv(s, buf, len, 0);
	if (rc < 0) {
		perror("error reading buffer length");
		return NULL;
	}
	
	buf[len] = 0;
	
	return buf;
}
