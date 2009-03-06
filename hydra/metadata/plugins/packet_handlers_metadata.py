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
from common.fs_db import FileSystemError

import threading

from operations_metadata import *
from common.fs_objects import *


        
class Handle_ANNOUNCE(PacketHandler):
    def process(self, data):
        
        #add client to the active clients list
        
        #print "Client %s@%s:%s has announced itself" % (data.serverid,data.ip, data.port)
        
        self.app.serverList.add(data.serverid,data.ip,data.port)
        
        #return an ACK to the client
        self.net.write(self.pb.build(packet_types.ACK, None))
        

        return None

class Handle_HEARTBEAT(PacketHandler):
    def process(self, data):

        print "Client %s@%s:%s has sent a heartbeat" % (data.serverid,data.ip, data.port)

        #add client to the active clients list
        self.app.serverList.add(data.serverid,data.ip,data.port)
        
        #return an ACK to the client
        self.net.write(self.pb.build(packet_types.ACK, None))

        return None

class Handle_FS_CREATE(PacketHandler):
    def process(self, data):
        
        #check if there are any active dataservers where we can store this file
        l = len(self.app.serverList.get())
        
        #if there are none, tell the client
        if not l:
            self.net.write(self.pb.build(packet_types.FS_ERR_NODATASERVERS, None))
            return None
        
        #check if the file already exists
        file = self.fs.get_file(path=data.path)

                
        if file:
            self.net.write(self.pb.build(packet_types.FS_ERR_CREATE, None))
            return None

        type = data.file_type
        version = 1 #this is the first revision of the file
        
        if type == 1: #it's a file
            #set the number of replicas for this file
            desired_replicas = data.replicas
            if not desired_replicas:
                desired_replicas = self.cfg.REPLICAS

            #set the block size for this file
            block_size = data.block_size
            if block_size == 0:
                block_size = self.cfg.BLOCK_SIZE
        elif type == 0: #it's a folder
            block_size = 0
        
        #store the file in our database        
        (path,name) = os.path.split(data.path)
        f = FSObject(0,1,name,0,type,0, block_size)
        
        try:            
            oid = self.fs.insert_file(path,f)
            
        
        # if this exception occurs at this point, it means the file doesn't have one or more parent directories.
        except FileSystemError: 
            
            dirs = []
            tmp = (path,None)
                        
            while 1:                
                tmp = os.path.split(tmp[0])                                            
                dirs.insert(0, tmp)
                if tmp[0] == '/':
                    break            
            
            # lets start trying to create those parent directories!
            print "-----------"            
            print dirs
            print "-----------"
            for i in dirs:
                
                # check if directory already exists
                tmp = i[0] + '/' + i[1]
                if self.fs.get_file(path=tmp):
                    print str(tmp) + " exists. Continue.................................."
                    continue
                
                # create the directory                                
                print str(tmp) + " is being created................"
                x = FSObject(0,1,i[1],0,0,0,0)
                self.fs.insert_file(i[0],x)                
                
            # store the file
            oid = self.fs.insert_file(path,f)

        
        try:
            
            if type == 1: #it's a file
            
                #set the number of replicas for this file
                desired_replicas = data.replicas
                if not desired_replicas:
                    desired_replicas = self.cfg.REPLICAS

                #set the block size for this file
                block_size = data.block_size
                if not block_size:
                    block_size = self.cfg.BLOCK_SIZE
                    
                (ip,port,serverid) = self.app.serverList.select_dataserver(oid)
    
                data = packet_builder.Data(params={'ip':ip,'port':port,'serverid':serverid,'oid':oid,'version':version,'block_size':block_size,'replicas':desired_replicas})
                self.net.write(self.pb.build(packet_types.FS_CREATE_OK, data))
                
                
            else: #it's a folder
            
                desired_replicas = 0 #no replicas for a folder
                block_size = 0
            
                data = packet_builder.Data(params={'oid':oid,'length':0,'version':version,'serverid':0})
                self.net.write(self.pb.build(packet_types.FS_NODE_CREATED,data))
                


        except fs_db.FileSystemError:
            self.net.write(self.pb.build(packet_types.FS_ERR_CREATE, None))
            
        return None

class Handle_FS_BLOCK_STORED(PacketHandler):
    def process(self,data):
        global fs
        
        #a dataserver is telling us that it successfully stored a replica of a file object
#        print "%s now has oid %s, block %s (version %s)" % (data.serverid, data.oid, data.block_id, data.version)
        
#        mon.log(1,data.oid,data.serverid, ver=data.version)
        
        serverid = data.serverid
        
        
        #update the new file info with version & length
        oid = data.oid
        block_id = data.block_id
        

        block = self.fs.get_block(oid, block_id)

        
        
        if not block:
            block = FSBlock(0,0,0,0,0)
            block.oid = data.oid
            block.block_id = data.block_id

        block.offset = data.offset
        block.version = data.version
        block.size = data.length
        
        #add the block to the database

        self.fs.add_block(block, data.serverid)
        
        #tell dataserver the block has been stored
        data = packet_builder.Data()
#        print "Sending ACK: %s" % data
        self.net.write(self.pb.build(packet_types.ACK,data))
        
        self.app.replicate_block(block.oid, block.block_id, block.version, serverid)

class Handle_FS_GET(PacketHandler):
    def process(self,data):
        global fs

        #client wants a file
        print "Client requests %s" % (data.path)
        

        file = self.fs.get_file(path=data.path)

        
        #if there is no such file tell the client so
        if not file:
            data = packet_builder.Data()
            self.net.write(self.pb.build(packet_types.FS_ERR_PATH_NOT_FOUND, data))
            return None
        
        #get the file's blocks and replicas

        blocks = self.fs.get_blocks(file.oid,byte_start=0,byte_end=0)
        replicas = self.fs.get_file_replicas(file.oid)
        
        #get an online dataserver where this file is stored
        block_replicas = self.app.serverList.select_blocks_replicas(file.blocks, replicas)
        
        #if the file size > 0 but there are no online servers that can serve all blocks
        if file.size > 0 and not block_replicas:
            data = packet_builder.Data()
            self.net.write(self.pb.build(packet_types.FS_ERR_NO_REPLICAS,data))
            return None
 
        #tell the client where it can get the file
        data = packet_builder.Data(params={'oid':file.oid,'file_size':file.size, 'version':file.version,'block_size':file.block_size, 'file_type':file.type})


        #build the list of blocks and servers
        data.blocks = []

        for block_id in file.blocks.keys():
            block = packet_builder.Data()
            block.block_id = block_id
            block.version = blocks[block_id].version
            block.block_size = blocks[block_id].size
            block.offset = blocks[block_id].offset
            
            block.ip = block_replicas[block_id][0]
            block.port = block_replicas[block_id][1]
            block.serverid = block_replicas[block_id][2]
            
            data.blocks.append(block)    
        

        #send the client the ok signal and a list of servers where it can get each block
        self.net.write(self.pb.build(packet_types.FS_GET_OK,data))
        
        
#        ds_list_lock.acquire()
#        replicate_further = serverList.oid_used(file.oid)
#        ds_list_lock.release()
        
#        if replicate_further:
#            serverid = get_current_replica_server(file.oid,file.version)
#            replicate_file(file.oid, file.version, serverid,force=True)


        return None

class Handle_FS_GET_LOCK(PacketHandler):
    def process(self,data):
        print "Server %s wants a lock on oid %s:%s" % (data.serverid, data.oid, data.block_id)

        #check if the file is locked
        block_lock_success = self.app.serverList.add_lock(data.oid,data.block_id, data.version, data.serverid)

        data = packet_builder.Data(params={'oid':data.oid,'block_id':data.block_id,'version':data.version})

        
        #the file is locked so tell the client better luck next time
        if not block_lock_success:
            self.net.write(self.pb.build(packet_types.FS_ERR_LOCK_DENIED,data))
        else:
            self.net.write(self.pb.build(packet_types.FS_LOCK_OK,data))

        return None

class Handle_FS_MODIFY_DONE(PacketHandler):
    def process(self,data):
#        print "FS_MODIFY_DONE: %s" % data
        
        serverid = data.serverid
        
        #release lock
        self.app.serverList.release_lock(data.oid,data.block_id,data.version)
        
        #update info in the database

        file = self.fs.get_file(oid=data.oid)
        block = self.fs.get_block(data.oid,data.block_id)

        #if the versions differ, tell the dataserver it has an invalid version
        if int(block.version) != int(data.version):
            print "Server has a different version %s != %s" % (int(file.version),int(data.version))
            data = packet_builder.Data(params={'oid':file.oid,'block_id':block.block_id,'version':file.version})
            self.net.write(self.pb.build(packet_types.FS_ERR_INCORRECT_VERSION,data))
            return None
        
        #increment the file version and update our records
        block.version += 1
        block.block_size = data.block_size
        block.size = data.block_size
        file.set_block(block)

        #add the block to the database
        self.fs.add_block(block, data.serverid)

        #tell the dataserver the new version
        data = packet_builder.Data(params={'oid':file.oid, 'block_id':block.block_id, 'version':block.version})
 #       print "Sending FS_MODIFY_ACK: %s" % data
        self.net.write(self.pb.build(packet_types.FS_MODIFY_ACK,data))
        ds_reply = self.pb.extract_stream(self.net.sock)

        if ds_reply.type == packet_types.FS_VERSION_UPDATED:
            self.app.update_file_replicas(block.oid, block.block_id, block.version, serverid)
        


        return None

class Handle_FS_RENAME_FILE(PacketHandler):
    def process(self, data):
        global fs
        #client wants to rename a file
        print "Client wants to rename %s -> %s" % (data.src_path, data.dest_path)
        
        try:
            dest_file = self.fs.get_file(path=data.dest_path)
    
            self.fs.rename_file(data.src_path, data.dest_path)
            self.net.write(self.pb.build(packet_types.FS_RENAME_DONE,data))
            
            if dest_file:
                pass #add file deletion code here
        
        except fs_db.FileSystemError, e:
            print "FS_RENAME_FILE: %s" % e.value
            self.net.write(self.pb.build(packet_types.FS_ERR_RENAME,data))
        
        return None
        
class Handle_FS_DELETE_FILE(PacketHandler):
    def process(self,data):
        global fs
        #client wants a file
        print "Client wants to delete %s" % (data.path)
        

        file = self.fs.get_file(path=data.path)

        
        #if there is no such file tell the client so
        if not file:
            data = packet_builder.Data()
            self.net.write(self.pb.build(packet_types.FS_ERR_PATH_NOT_FOUND, data))
            return None
            
        #get current replicas of this file

        reps = self.fs.get_replicas(file.oid)

        
        #if the file is currently in use, tell the client so
        file_has_locks = self.app.serverList.file_has_locks(file.oid)
        
        if not file_has_locks:
            data = packet_builder.Data(params={'oid':file.oid,'version':file.version})
            self.net.write(self.pb.build(packet_types.FS_ERR_LOCK_DENIED,data))
            return None
        
        #delete everything we have on that file

        self.fs.delete_file(file.oid)


        #tell the client the file is gone
        
        data = packet_builder.Data(params={'oid':file.oid})
        self.net.write(self.pb.build(packet_types.FS_DELETE_DONE,data))
        self.net.close()


        if reps:
            #get a list of ip & ports of online servers that have such replica
            servers = map(self.app.serverList.get_server, reps.replicas.keys())
            
            for server in servers:
                try:
                    
                    print "Trying %s..." % str(server)
                    
                    out = network_services.NetworkTransport()
                    out.open(server[0],server[1])
                    out.write(self.pb.build(packet_types.FS_DELETE_OID,data))
                    out.close()
                except Exception,e:
                    print e
        
        return None

class Handle_FS_REPLICATE_DONE(PacketHandler):
    def process(self,data):
        global fs
        
        #a dataserver is telling us that it successfully stored a replica of a file object
#        print "%s now has object %s, version %s" % (data.serverid, data.oid, data.version)
        (serverid,oid,block_id,version) = (data.serverid,data.oid,data.block_id,data.version)
        

        block = self.fs.get_block(oid, block_id)

        
        if not block:
            print "This block does not exist in the database, returning"
            #TODO: possibly tell dataserver to delete the offending block
            return None

        block.version = version
        
        #add the dataserver to the replicas database

        self.fs.add_block_replica(block, serverid)




        self.app.replicate_block(block.oid, block.block_id, block.version, serverid)
        
        return None

class Handle_FS_STAT_FILE(PacketHandler):
    def process(self,data):
        global fs
        
        print "Client wants to know about %s" % data.path
        

        file = self.fs.get_file(path=data.path)

        
        #if there is no such file tell the client so
        if not file:
            self.net.write(self.pb.build(packet_types.FS_ERR_PATH_NOT_FOUND, data))
            return None

        data = packet_builder.Data(params={'oid':file.oid,'path':file.path,'num_blocks':len(file.blocks),'version':file.version,'size':file.size,'file_type':file.type,'parent':file.parent,'block_size':file.block_size})        
    
        if file.type == 0:
            children = []
            
            for child in self.fs.get_children(file.oid):
                    data_child = packet_builder.Data(params={'oid':child.oid,'path':child.path,'num_blocks':len(child.blocks),'version':child.version,'size':child.size,'file_type':child.type,'parent':child.parent,'block_size':child.block_size})                    
                    children.append(data_child)
            
            data.children = children
        
        #print data
        self.net.write(self.pb.build(packet_types.FS_FILE_INFO, data))
            

class Handle_CHK_VER(PacketHandler):
    def process(self,data):
    
        global fs
        
        serverid = data.serverid
        serverip = data.ip
        serverport = data.port

        self.net.write(self.pb.build(packet_types.ACK, None))
        
        print "Syncing with %s" % data.serverid
        
        return STATE_CURR_BLOCK(serverid, serverip, serverport)

class STATE_CURR_BLOCK(PacketHandler):
    def __init__(self, serverid, ip, port):
        self.serverid = serverid
        self.serverport = port
        self.serverip = ip
        
    def process(self, data):
        data = self.pb.extract_stream(self.fp)
        #if we are done then don't process any more incoming sync packets
        if data.type == packet_types.CHK_DONE:
            print "Sync done"
            return None
    
        oid = data.oid
        block_id = data.block_id

        block = self.fs.get_block(oid,block_id)

        #if the block has been deleted, tell the data server to delete the block too
        if not block:
            print "Block deleted"
            data = packet_builder.Data(params={'oid':oid,'block_id':block_id})
            try:
                out = network_services.NetworkTransport()
                out.open(self.serverip,self.serverport)
                out.write(self.pb.build(packet_types.FS_DELETE_BLOCK,data))
                out.close()
                
            except Exception,e:
                print e


                self.app.serverList.remove_address(self.serverip,self.serverport)
                return None
        else:
            if int(block.version) != int(data.version):
                print "Inconsistent oid %s, block_id %s (version %s) for %s (correct version: %s)" % (block.oid, block.block_id, data.version, self.serverid, block.version)
                
                curr_rep = self.app.get_current_replica_server(block.oid, block.block_id, block.version)
                if curr_rep:
                    print "Updating %s:%s with %s" % (block.oid, block.block_id, curr_rep)
                    self.app.update_file_replicas(block.oid, block.block_id, block.version, curr_rep)
            
        return STATE_CURR_BLOCK(self.serverid, self.serverip, self.serverport)

    
class Handle_FS_ERR_DATASERVER_FAILED(PacketHandler):
    def process(self,data):
        print "Something is wrong with %s:%s" % (data.ip, data.port)

        self.app.serverList.remove_address(data.ip,data.port)
        return None
        
class Handle_FS_GET_REPLICAS(PacketHandler):
    def process(self, data):
#        print "Client wants to know about the replicas of %s" % data.oid
        
        #get current replicas of this file

        reps = self.fs.get_replicas(data.oid)


        data.replicas = reps.replicas
        
        self.net.write(self.pb.build(packet_types.FS_OID_REPLICAS, data))


def initialize(app):
    """This function gets called by the plugin initializer"""
    app.addHandler(packet_types.ANNOUNCE,Handle_ANNOUNCE())
    app.addHandler(packet_types.FS_CREATE,Handle_FS_CREATE())
    app.addHandler(packet_types.FS_BLOCK_STORED,Handle_FS_BLOCK_STORED())
    app.addHandler(packet_types.FS_GET,Handle_FS_GET())
#	app.addHandler(packet_types.FS_WRITE_FILE,Handle_FS_WRITE_FILE())
    app.addHandler(packet_types.FS_GET_LOCK,Handle_FS_GET_LOCK())
    app.addHandler(packet_types.FS_MODIFY_DONE,Handle_FS_MODIFY_DONE())
    app.addHandler(packet_types.FS_DELETE_FILE,Handle_FS_DELETE_FILE())
    app.addHandler(packet_types.FS_REPLICATE_DONE,Handle_FS_REPLICATE_DONE())
    app.addHandler(packet_types.FS_STAT_FILE,Handle_FS_STAT_FILE())
    app.addHandler(packet_types.CHK_VER,Handle_CHK_VER())
    app.addHandler(packet_types.FS_ERR_DATASERVER_FAILED,Handle_FS_ERR_DATASERVER_FAILED())
    app.addHandler(packet_types.FS_RENAME_FILE, Handle_FS_RENAME_FILE())
#	app.addHandler(packet_types.FS_GET_REPLICAS,Handle_FS_GET_REPLICAS())

