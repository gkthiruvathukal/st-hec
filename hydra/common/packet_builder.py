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



import packet_types
import network_services
import socket
import struct
#from mdserver import packet_handlers
#import packet_handlers

import time

class PacketError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return self.value
        

class Data:
    def __init__(self, params=None):
        if params:
            if type(params) == type({}):
                for key in params:
                    self.__dict__[key] = params[key]

    def __setattr__(self, name, value):
        self.__dict__[name] = value
    
    def __repr__(self):
        str = ''
        for key in self.__dict__:
            str += '%s=%s; ' % (key, self.__dict__[key])
        return str

class PacketBuilder:
    def __init__(self):
        self._builders = {}
        
    def registerPacket(self, code, builder, override=False):
        if self._builders.has_key(code) and not override:
            raise PacketError("There is already a builder registered for packet: %s" % code)
            
        self._builders[code] = builder
    
    def build(self,code, data):
        """Creates a packet of type code, with parameters specified in data"""
        
        if not self._builders.has_key(code):
            raise PacketError("There is no registered builder for packet code: %s" % code)
        
        builder = self._builders[code]
        pckt_data = builder.pack(data)
        
        #insert packet code & total length at the head of the packet
        
        total_length = len(pckt_data) + struct.calcsize('!II')
        format_str = '!II%ss' % len(pckt_data)
        packet = struct.pack(format_str, code, total_length, pckt_data)
        
        return packet
    
    def extract_stream(self, fp):
        """Extracts the data from a stream, and returns it in a data object"""

        try:
            reader = network_services.NetworkTransport(sock=fp)

            #unpack the first two fields of the packet (code & len)
            format_str = '!II' # code & length
            header_len = struct.calcsize(format_str)
            (code, packet_length) = struct.unpack(format_str, reader.read(header_len))
            
            #find & call a suitable method for dealing with this type of packet
            
            if not self._builders.has_key(code):
                raise PacketError("There is no registered builder for packet code: %s" % code)
            
            builder = self._builders[code]
            return builder.unpack(reader)
        except IOError, e:
            raise PacketError("Could not read from stream: %s" % e)

    def extract(self, pckt):
        """Extracts the data from a packet, and returns it in a data object"""
        
        try:
            format_str = '!II' #code & length
            header_len = struct.calcsize(format_str) #len of first two fields
            (code, packet_length) = struct.unpack(format_str, pckt[0:header_len])

            #find & call a suitable method for dealing with this type of packet
            if not self._builders.has_key(code):
                raise PacketError("There is no registered builder for packet code: %s" % code)
            
            builder = self._builders[code]

            #call it with the remainder of the packet
            return builder.unpack(pckt[header_len:])#, packet_length - header_len)
        except IOError, e:
            raise PacketError("Could not read from stream: %s" % e)

        
if __name__ == '__main__':
    
    ip = '192.168.0.101'
    port = '5000'
    
    PBuilder = Packet()
    data = Data()
    data.path = '/usr'
    
    pckt = PBuilder.build(packet_types.FS_CREATE, data)
    print repr(pckt)
#    print PBuilder.extract(pckt).items
