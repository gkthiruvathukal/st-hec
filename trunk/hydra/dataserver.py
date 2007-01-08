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



from common import network_services,packet_builder,packet_types,synchronized
from common.dispatch import Dispatcher
from common.rep_db import *
from common import plugin

from common import log_exception

from xml.dom import minidom
import getopt,os,sys,threading,signal,traceback,socket

global run_timer
excLog = log_exception.LogException()

class ConfigException(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self)

class Config:
    def __init__(self):
        self.IP = '127.0.0.1' #ip server listens to
        self.PORT = 10000 #port server listens to
        self.BACKLOG = 5  #max concurrent connections
        self.SERVER_ID = 0 # server id
        self.CURR_MD_IP = '' #ip of the metadata server we managed to contact
        self.CURR_MD_PORT = '' #port of the metadata server we managed to contact
        
        self.mdservers = [] #list of metadata servers to contact
    
    def loadConfigFile(self, file):

        if not os.path.exists(os.path.abspath(file)):
            raise ConfigException("Could not find config file")
        
        try:
            xmldoc = minidom.parse(os.path.abspath(file))
            self.SERVER_ID = xmldoc.getElementsByTagName('name')[0].attributes['id'].value
            self.IP = xmldoc.getElementsByTagName('address')[0].attributes['ip'].value
            self.PORT = xmldoc.getElementsByTagName('address')[0].attributes['port'].value
            self.BACKLOG = int(xmldoc.getElementsByTagName('backlog')[0].attributes['number'].value)
            self.STORAGE_PATH = xmldoc.getElementsByTagName('storage')[0].attributes['path'].value
            self.STORAGE_DB = xmldoc.getElementsByTagName('storage')[0].attributes['db'].value
            
            if not self.STORAGE_PATH or not os.path.exists(self.STORAGE_PATH):
                raise ConfigException("Storage path %s does not exist" % self.STORAGE_PATH)
            
            for c in xmldoc.getElementsByTagName('mdserver'):
                self.mdservers.append((c.attributes['ip'].value,int(c.attributes['port'].value)))
    
        except ConfigException, e:
            raise ConfigException(e.value)
        except Exception, e:
            print e
            raise ConfigException("Error in config file")
        
        
    def viewConf(self):
        print "Name: %s | ip: %s | port: %s | backlog: %s" % (self.NAME, self.IP, self.PORT, self.BACKLOG)
        print "MDServers: %s" % self.mdservers
        

def usage():
    print """Usage: client.py -c configfile
    """


class DataSync(threading.Thread):
    def __init__(self, cfg, db, pb):
        threading.Thread.__init__(self)
        self.cfg = cfg
        self.db = db
        self.pb = pb
       
    def sync_fs(self):
        print "Syncing with metadata server..."
        try:
            net = network_services.NetworkTransport()
            net.open(self.cfg.CURR_MD_IP,self.cfg.CURR_MD_PORT)

            data = packet_builder.Data()
            data.serverid = self.cfg.SERVER_ID
            data.ip = self.cfg.IP
            data.port = self.cfg.PORT

            pckt = self.pb.build(packet_types.CHK_VER, data)
            net.write(pckt)
            data = self.pb.extract_stream(net.sock)
                
            #metadata server said we can start checking versions
            if data.type == packet_types.ACK:
                dbIterator = self.db.getIterator()
                i  = 0
                print "start sync"
                while dbIterator.hasNext():
                    file = dbIterator.next()
                    data = packet_builder.Data()
                    #the key (oid, block_id) is returned as a string, so we have to eval it to make it an array
                    #and extract the elements
                    data.oid = eval(file[0])[0]
                    data.block_id = eval(file[0])[1]
                    data.version = file[1]
                    data.serverid = self.cfg.SERVER_ID
                    pckt = self.pb.build(packet_types.CURR_BLOCK, data)
                    net.write(pckt)
                    i += 1
                    if not i % 1000:
                        print i
                print "end sync"
            #tell metadata server we are done with our files
            data = packet_builder.Data()
            data.serverid = self.cfg.SERVER_ID
            data.ip = self.cfg.IP
            data.port = self.cfg.PORT

            pckt = self.pb.build(packet_types.CHK_DONE, data)
            net.write(pckt)

            net.close()
        except Exception, e:
            global excLog
            sys.exc_info()
            v1,v2 = excLog.GetExceptionData()
            excLog.Log("Exception within connection",v1,v2)
            print "Could not sync versions with metadata server! Aborting..."
            net.close()

    def run(self):
        self.sync_fs()
            
class DataServer:
    def __init__(self, cfg):
        
        self.socket = 0
        self.cfg = cfg
        self.timer = None
        self.db = synchronized.SynchronizedObject(RepDB(cfg.STORAGE_DB)) #objects stored database
        self.db.open()
        self.pb = packet_builder.PacketBuilder()
        self.dispatcher = Dispatcher(cfg, self.db, self.pb, self) #dispatches handlers for incoming packets
        
        self.dir_hash_lock = threading.Lock() #lock for creating hash directories for storing blocks

    def addHandler(self, pckt_type, handler_class, priority=50):
        self.dispatcher.addHandler(pckt_type, handler_class, priority)

    def registerPacket(self, code, builder):
        self.pb.registerPacket(code,builder)        
    
    def handle_sigint(self, signum, frame):
        self.shutdown()

    def find_mdserver(self):
        if not len(self.cfg.mdservers):
            print "No metadata servers defined! Shutting down..."
            return
    
        for server in self.cfg.mdservers:
            try:
                
                print "Trying %s..." % str(server)
                
                net = network_services.NetworkTransport()
                net.open(server[0],server[1])
    
                print "Connected! Announcing ourselves..."
    
                data = packet_builder.Data()
                data.serverid = cfg.SERVER_ID
                data.ip = cfg.IP
                data.port = cfg.PORT

                pckt = self.pb.build(packet_types.ANNOUNCE, data)
                net.write(pckt)
                
                data = self.pb.extract_stream(net.sock)
                print "Server response: %s" % data.type
                
                if data.type == packet_types.ACK:
                    print "Success! %s" % str(server)
                
                self.cfg.CURR_MD_IP = server[0]
                self.cfg.CURR_MD_PORT = server[1]
                break
            
            except Exception, e:
                print e
                
        if not self.cfg.CURR_MD_IP:
            print "No metadata servers found!"
            return False
        else:
            return True
    
    def start_heartbeat(self):
        global run_timer
        run_timer = True
        self.timer = threading.Timer(1, self.heartbeat)
        self.timer.start()
    
    def heartbeat(self):
#        print "Heartbeat"
        global run_timer
        
        try:
            net = network_services.NetworkTransport()
            net.open(self.cfg.CURR_MD_IP,self.cfg.CURR_MD_PORT)
    
#            print "Sending heartbeat..."
    
            data = packet_builder.Data()
            data.serverid = cfg.SERVER_ID
            data.ip = cfg.IP
            data.port = cfg.PORT
            pckt = self.pb.build(packet_types.HEARTBEAT, data)
            net.write(pckt)
            
            data = self.pb.extract_stream(net.sock)
#            print "Server response: %s" % data.type
                
            if data.type == packet_types.ACK:
                pass
#                print "Successful heartbeat!"
        except:
            print "Something went wrong with the mdserver"

        if run_timer:
            self.timer = threading.Timer(5, self.heartbeat)
            self.timer.start()
        
    def start(self):
        signal.signal(signal.SIGINT, self.handle_sigint)

        #try to contact any of the data servers in the list
        if not self.find_mdserver():
            self.shutdown()
            return
        
        #sync our filesystem to the metadata server
        DataSync(self.cfg, self.db, self.pb).start()
        
        #start sending keepalive messages to mdserver
        self.start_heartbeat()

        #listen for incoming requests
        self.listen()

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
        
        self.db.close()
        print "Done!"
        sys.exit(0)

    def listen(self):
    
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)         
        self.socket.bind(('', int(self.cfg.PORT)))

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

    def get_block_lock(self, oid, block_id, version):
            data = packet_builder.Data(params={'oid':oid, 'block_id':block_id,'version':version,'serverid':self.cfg.SERVER_ID})
    
            mds = network_services.NetworkTransport()
            mds.open(self.cfg.CURR_MD_IP,self.cfg.CURR_MD_PORT)
            mds.write(self.pb.build(packet_types.FS_GET_LOCK,data))
            mds_reply = self.pb.extract_stream(mds.sock)
            mds.close()
            
            return mds_reply.type == packet_types.FS_LOCK_OK

    def create_storage_path(self,oid,block_id):
        hash_levels = [100000,10000,1000]
        bucket = 0
        curr_path = self.cfg.STORAGE_PATH
        self.dir_hash_lock.acquire()
        for level in hash_levels:
            for folder in range(level,level*10,level):
                if oid < folder:
                    break
            curr_path = os.path.join(curr_path,str('obj_%s-%s' % (folder-level,folder)))

            if not os.path.exists(curr_path):
                os.mkdir(curr_path)
        self.dir_hash_lock.release()
        return curr_path

    def get_storage_path(self,oid,block_id):
            """returns the path where the block for this oid should be stored"""
            
            #return self.cfg.STORAGE_PATH
            return self.create_storage_path(oid,block_id)

        
if __name__ == '__main__':

    try:
        opts,args = getopt.getopt(sys.argv[1:], "hc:")

    except getopt.GetoptError:
        
        usage()
        sys.exit(2)
        
    cfg = Config()
    
    for o,a in opts:
        if o == "-h":
            usage()
            sys.exit()
        if o == "-c":
            try:
                cfg.loadConfigFile(a)
            except ConfigException, e:
                print e.value
                usage()
                sys.exit()
            except:
                usage()
                sys.exit()

    
    server = DataServer(cfg)
    plugin.initPlugins(server,'./dataserver/plugins') #add & initialize all plugins
    plugin.initPlugins(server,'./common/plugins')
    server.start() #start server operations
