#!/usr/bin/python

#######################################################################################
#
#   Copyright (c) 2006 Loyola University Chicago and Contributors. All rights reserved.
#   This file is part of The Hydra Filesystem.
#
#   The Hydra Filesystem is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   The Hydra Filesystem is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with the Hydra Filesystem; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#######################################################################################



import socket
import sys

class NetworkError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self)


class NetworkTransport:
    def __init__(self, sock=None):
        self.sock = sock
    
    def open(self, host, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host,int(port)))
            self.sock.settimeout(10)
        except Exception, e:
            raise NetworkError(str(e))
        
    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
        
    def read(self, length):
        """Read *exactly* length bytes and if not raise an error"""
#        print "Expecting %s bytes" % length
        buf = ''

#        print "Read %s from socket: %s" % (length, self.sock)
#        print "R",
        sys.stdout.flush()
        
        while length > 0:
            
            msg = self.sock.recv(length)
            
            if not msg:
                raise NetworkError("Socket connection broken while reading")
                
            length -= len(msg)
            buf += msg
            
        return buf
        
    def read_buffered(self, length):
        """Attempt to read up to length bytes, and if not return whatever we have"""

#        print "Read %s from socket: %s" % (length, self.sock)
#        print "r%s " % length,
        sys.stdout.flush()
        
        buf = ''
        
        try:
            while length > 0:
                msg = self.sock.recv(length)
                if not msg:
                    print "!",
                    sys.stdout.flush()
                    return buf
                length -= len(msg)
                buf += msg
        except socket.timeout:
                print "Only received %s bytes!" % len(buf)
                return buf
            
        return buf
        
    def write(self, data):

        length = len(data)
#        print "Writing %s bytes" % length
#        print "Write %s to socket: %s" % (length, self.sock)
#        print "w",
        sys.stdout.flush()
        
        sent_bytes = 0
        while length > 0:
            sent = self.sock.send(data[sent_bytes:])
            
            if not sent:
                raise NetworkError("Socket connection broken while writing")

            sent_bytes += sent
            length -= sent
            
