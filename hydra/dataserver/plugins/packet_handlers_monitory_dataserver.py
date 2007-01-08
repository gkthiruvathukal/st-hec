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


import os

from common import network_services, packet_builder, packet_types, fs_db
from common.plugin import PacketHandler, initPlugins

import threading

from operations_metadata import *
from common.fs_objects import *

import struct
mon_lock = threading.Lock()

class Monitor:
    def __init__(self, ip, port):

        try:
            self.net = network_services.NetworkTransport()
            self.net.open(ip,port)
        except Exception, e:
            print e
            self.net.close()
            self.net = None

    def log(self, t, obj, arg,ver=0):
        if self.net:
            mon_lock.acquire()
            try:
                format = '!IIII'
                data = struct.pack(format, int(t), int(obj), int(arg),int(ver))
                self.net.write(data)
            except Exception, e:
                print e
                self.net.close()
                self.net = None
            mon_lock.release()
        
    def close(self):
        if self.net:
            mon_lock.acquire()
            self.net.close(data)
            mon_lock.release()

    def __del__(self):
        """Loop on all base classes, and invoke their destructors.
        Protect against diamond inheritance."""
        
        self.close()
        
        for base in self.__class__.__bases__:
            # Avoid problems with diamond inheritance.
            basekey = 'del_' + str(base)
            if not hasattr(self, basekey):
                setattr(self, basekey, 1)
            else:
                continue
            # Call this base class' destructor if it has one.
            if hasattr(base, "__del__"):
                base.__del__(self)

class MonitorHandler(PacketHandler):
    def __init__(self,mon):
        self.mon = mon

class Handle_FS_BEGIN_WRITE(MonitorHandler):
    def process(self, data):
        self.mon.log(0,self.app.cfg.SERVER_ID,1,data.oid)

class Handle_FS_REQUEST_BLOCK(MonitorHandler):
    def process(self, data):
        print "Serving block"
        self.mon.log(0,self.app.cfg.SERVER_ID,1,data.oid)

class Handle_FS_DELETE_BLOCK(MonitorHandler):
    def process(self, data):
        self.mon.log(0,self.app.cfg.SERVER_ID,1,data.oid)

class Handle_FS_REPLICATE_BLOCK(MonitorHandler):
    def process(self, data):
        self.mon.log(0,self.app.cfg.SERVER_ID,1,data.oid)

def initialize(app):
    mon = Monitor('127.0.0.1',15000)
    """This function gets called by the plugin initializer"""
    app.addHandler(packet_types.FS_BEGIN_WRITE,Handle_FS_BEGIN_WRITE(mon),priority=90)
    app.addHandler(packet_types.FS_REQUEST_BLOCK,Handle_FS_REQUEST_BLOCK(mon),priority=90)
    app.addHandler(packet_types.FS_DELETE_BLOCK,Handle_FS_DELETE_BLOCK(mon),priority=90)
    app.addHandler(packet_types.FS_REPLICATE_BLOCK,Handle_FS_REPLICATE_BLOCK(mon),priority=90)
    
