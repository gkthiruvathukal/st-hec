#!/usr/bin/python
"""
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
"""


import socket, threading, signal, sys, traceback, os
import getopt

from common import packet_builder, packet_types, fs_objects, fs_db, synchronized, network_services
from common.dispatch import Dispatcher
from common import plugin
from operations_metadata import *

from xml.dom import minidom
   
class MDServer:
    def __init__(self, cfg):
        self.socket = 0
        self.cfg = cfg       #configuration parameters
        self.fs_db = synchronized.SynchronizedObject(fs_db.DB(self.cfg.STORAGE_PATH)) #initialize the database
        self.fs_db.setup_fs_db()
        
        self.pb = packet_builder.PacketBuilder()
        self.serverList = synchronized.SynchronizedObject(DataServerList())
        
        self.dispatcher = Dispatcher(cfg, self.fs_db,self.pb, self)
        
    def handle_sigint(self, signum, frame):
        self.shutdown()
        sys.exit(0)
        
    def addHandler(self, pckt_type, handler_class, priority=50):
        self.dispatcher.addHandler(pckt_type, handler_class, priority)
        
    def registerPacket(self, code, builder):
        self.pb.registerPacket(code,builder)
        
    def shutdown(self):
        global run_timer
    
        run_timer = False
        curr_thread = threading.currentThread()
        for t in threading.enumerate():
            if t == curr_thread: continue

            if hasattr(t,'shutdown'):
                t.shutdown()

        if self.socket:
            self.socket.close()

        print "Waiting for threads..."
        
        for t in threading.enumerate():
            if t != curr_thread:
                t.join()
            
        print "Done!"
        self.fs_db.close_fs_db();
        sys.exit(0)

    def listen(self):
    
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.socket.bind(('', self.cfg.PORT))

        signal.signal(signal.SIGINT, self.handle_sigint)

        self.socket.listen(self.cfg.BACKLOG)
    
        #loop and serve request
    
        while 1:
            (fd, address) = self.socket.accept()
            self.dispatcher.handle(fd,address)

        print "Shutting down"
        if self.socket:
            self.socket.close()
        if fd:
            fd.close()

    def replicate_block(self,oid,block_id,version,original_serverid,force=False):

        block = self.fs_db.get_block(oid, block_id)
        reps = self.fs_db.get_block_replicas(oid,block_id)

    
        #make sure the block we are replicating is the most current version
        if block.version != version:
            print "This version has expired! (%s) %s" % (version, block)
            return

        #replicate the file
        done = False
    
        while 1:
            if len(reps.replicas.keys()) > self.cfg.REPLICAS and not force:
                return None
    
            #see if we need to do any more replicas
            rep = self.serverList.select_new_replica_server(reps.replicas)
            server = self.serverList.get_server(original_serverid)

            if rep:
    #            print "REPLICATE FILE: server: %s replica %s" % (server, rep)
                try:
                    (ip,port,serverid) = rep
                    data = packet_builder.Data(params={'oid':oid,'block_id':block_id,'version':version,'serverid':original_serverid,'ip':server[0],'port':server[1]})
                    net = network_services.NetworkTransport()
                    net.open(ip,port)
                    net.write(self.pb.build(packet_types.FS_REPLICATE_BLOCK,data))
                    net.close()
                    done = True
                except network_services.NetworkError, e:
                    print "OOOOOOOOOOO: %s" % e.value
                    #if the dataserver didn't work remove it from the active server list
                    self.serverList.remove(serverid)
                    print e
                    os._exit(1)
                
            if done or not rep:
                break

    def update_file_replicas(self,oid,block_id,version,original_serverid):
        """Updates all replicas of oid, where the new version is in original_serverid"""
    
        reps = self.fs_db.get_block_replicas(oid,block_id)
        server = self.serverList.get_server(original_serverid)
        
        if not server:
            return
        
        reps_done = 0
        
        for rep in reps.replicas.keys():
            dest = self.serverList.get_server(rep)
            
    #        print version
    #        print reps.replicas[rep]
    #        print dest
            
            if not dest or reps.replicas[rep] >= version:
                continue
                
            try:
                print "UPDATE REPLICA: server: %s replica %s" % (server, dest)
                data = packet_builder.Data(params={'oid':oid,'block_id':block_id,'version':version,'serverid':original_serverid,'ip':server[0],'port':server[1]})
    
                net = network_services.NetworkTransport()
                net.open(dest[0],dest[1])
                net.write(self.pb.build(packet_types.FS_REPLICATE_BLOCK,data))
                net.close()
                reps_done += 1
                
            except network_services.NetworkError,e:
                print "OOOOOOOOOOO: %s" % e.value
             
                
                #if the dataserver didn't work remove it from the active server list
                self.serverList.remove(str(rep))
    
    
    #if we could not update any of our current replicas of the file, at least store it somewhere else
    #    if not reps_done:
      #      replicate_file(oid,version,original_serverid)

    def get_current_replica_server(self,oid, block_id,version):
        """Finds an online server with this version of the file"""
        reps = self.fs_db.get_block_replicas(oid,block_id)
        
        for rep in reps.replicas.keys():
            if reps.replicas[rep] != version:
                continue
            
            server = self.serverList.get_server(rep)
        
            if not server:
                continue
                
            return str(rep)
        return None

            
class ConfigException(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self)

            
class Config:
    def __init__(self):
        self.PORT = 50000 #port server listens to
        self.BACKLOG = 5  #max concurrent connections
    
    def loadConfigFile(self,file):
        if not os.path.exists(os.path.abspath(file)):
            raise ConfigException("Could not find config file")
        
        try:
            xmldoc = minidom.parse(os.path.abspath(file))
            self.SERVER_ID = xmldoc.getElementsByTagName('name')[0].attributes['id'].value
            self.IP = xmldoc.getElementsByTagName('address')[0].attributes['ip'].value
            self.PORT = int(xmldoc.getElementsByTagName('address')[0].attributes['port'].value)
            self.BACKLOG = int(xmldoc.getElementsByTagName('backlog')[0].attributes['number'].value)
            self.STORAGE_PATH = xmldoc.getElementsByTagName('storage')[0].attributes['path'].value
            
            if not self.STORAGE_PATH or not os.path.exists(self.STORAGE_PATH):
                raise ConfigException("Storage path %s does not exist" % self.STORAGE_PATH)
                
            self.BLOCK_SIZE = xmldoc.getElementsByTagName('block')[0].attributes['size'].value
            self.REPLICAS = xmldoc.getElementsByTagName('replicas')[0].attributes['number'].value
    
        except ConfigException, e:
            raise ConfigException(e.value)
        except Exception, e:
            raise ConfigException("Error in config file")
    
    def viewConf(self):
        print "Name: %s | ip: %s | port: %s | backlog: %s | storage_path: %s" % (self.SERVER_ID, self.IP, self.PORT, self.BACKLOG, self.STORAGE_PATH)
        print "Block_size: %s | replicas: %s" % (self.BLOCK_SIZE, self.REPLICAS)

    
def usage():
    print """Usage: server.py -p [port] -c [configfile]
    """
        
        
if __name__ == '__main__':

    try:
        opts,args = getopt.getopt(sys.argv[1:], "hc:")
    except getopt.GetoptError:
        print "Invalid option"
        usage()
        sys.exit(2)
        
    cfg = None
    
    for o,a in opts:
        if o == "-h":
            usage()
            sys.exit()
        if o == "-c":
            try:
                cfg = Config()
                cfg.loadConfigFile(a)
#                cfg.viewConf()
            except ConfigException, e:
                print e.value
                usage()
                sys.exit()
#            except:
#                print "jiji"
#                usage()
#                sys.exit()

    if not cfg:
        usage()
        sys.exit()

    md_server = MDServer(cfg) #create a metadata server instance
    plugin.initPlugins(md_server,'./metadata/plugins') #add & initialize all plugins
    plugin.initPlugins(md_server,'./common/plugins')
    md_server.listen() #start the listener loop
