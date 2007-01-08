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


from common.network_services import NetworkTransport
#from common import packet_types, fs_db
import os,sys,fnmatch,copy

class PacketHandler:
    def __init__(self):
	"""You should add your own plugin instance initialization stuff here"""
	pass

    def initialize(self, fp, cfg, fs, pb, app):
	"""This gets called everytime a packet arrives to this handler"""
        self.fp = fp #network socket from where the packet came from
        self.cfg = cfg #main app's configuration parameters
        self.fs = fs #reference to the object database
        self.pb = pb #packet builder
        self.app = app #reference to the application

        #if the socket is active, construct objects to access it
        if fp:
            self.net = NetworkTransport(fp)
        else:
            self.net = self.pb = 0

    def process(self, data):
	"""Process the incoming packet"""
        pass

            
    def setPriority(self, priority):
        self.priority = priority
    
    def clone(self):
        """Returns a shallow copy of the Handler. This is used by the dispatcher to get a new instance for each request (to make it thread safe). Override this method if you require a deep copy or any special operations that must be performe before your handler gets cloned"""
        return copy.copy(self)
        
class Packet:
    def __init__(self):
        self.build_string = ''

    def _short_string(self,s):
        for i in range(len(s)):
            if s[i] == '\x00':
                return s[0:i]
        return s

    def pack(self, data):
        pass
        
    def unpack(self,reader):
        pass

def initPlugins(app, path):
        
    plugins_path = os.path.abspath(path)
    sys.path.insert(0,plugins_path)
        
    plugin_list = [x for x in os.listdir(plugins_path) if fnmatch.fnmatch(x,'*.py')] # get the list of modules in the 'plugins' folder
        
    for file in plugin_list:
        (name,ext) = os.path.splitext(file)
        plugin = __import__(name, globals(), locals(), [])
        if not plugin.__dict__.has_key('initialize'): continue
        plugin.initialize(app)
            
    del sys.path[0]
