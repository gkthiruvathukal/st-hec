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


from common import network_services, packet_builder, packet_types, rep_db, hydra_client_api, fs_objects
from common.plugin import PacketHandler
import threading, socket, os




class Handle_FS_BEGIN_WRITE(PacketHandler):
    def process(self,data):
        print "Request to write to file oid=%s" % data.oid
        
        #tell client we are ready
        self.net.write(self.pb.build(packet_types.FS_WRITE_READY, data))

        return STATE_STORE_BLOCK_INFO()
        
class STATE_STORE_BLOCK_INFO(PacketHandler):
    def process(self,data):
        data = self.pb.extract_stream(self.fp)
        if data.type == packet_types.FS_END_WRITE:
            #TODO: notify metadata that write operations to this file are done
            return None
        elif data.type == packet_types.FS_MODIFY_BLOCK:
            self.net.write(self.pb.build(packet_types.FS_MODIFY_OK, data))
            return STATE_FS_MODIFY_BLOCK(data.oid, data.block_id, data.length, data.version, data.offset)
            
        elif data.type == packet_types.FS_STORE_BLOCK:
            print "Request to store block (oid=%s | block=%s): (length: %s, version %s)" % (data.oid, data.block_id, data.length, data.version)
        
            #TODO: check that we actually have the space to store this file
#            print "Client wants to store the file, sending response"
            #tell the client it's ok to send the file
            self.net.write(self.pb.build(packet_types.FS_STORE_OK, None))
#            print "Response sent"
        
            return STATE_STORE_BLOCK_WRITE(data.oid, data.block_id, data.length, data.version, data.offset)
        
class STATE_STORE_BLOCK_WRITE(PacketHandler):
    def __init__(self, oid, block_id, length, version, file_offset):
        self.oid = oid
        self.block_id = block_id
        self.length = length
        self.version = version
        self.file_offset = file_offset #distance from the begining of the file to the beginning of this block
    
    def rollback(self, fout):
        """Erase the file and entry we were dealing with"""
        if fout:
            fout.close()
            
        #TODO: Notify metadata server we no longer have this file
        
    def process(self,data):
    
        try:
            #open the file, read the data from the network and store it in the filesystem
            fout = open(os.path.join(self.app.get_storage_path(self.oid,self.block_id),'__%s__%s' % (self.oid, self.block_id)), "wb")
        
#            print "Trying to read %s bytes" % self.length
            remaining = self.length
            buf_size = 60000
            l = 0
            
            while remaining > 0:
                if buf_size > remaining:
                    buf_size = remaining
                    
                buf = self.net.read_buffered(buf_size)
                fout.write(buf)
                
                l += len(buf)
                remaining -= len(buf)
    
            fout.close()
            
            data = packet_builder.Data(params={'oid':self.oid,'block_id':self.block_id,'length':l,'version':self.version,'serverid':self.cfg.SERVER_ID, 'offset':self.file_offset})
            
            #store the replica information in the data server's local database
            self.fs.add(self.oid, self.block_id, self.version)
            
            #tell metadata server we have the file now
            mds = network_services.NetworkTransport()
            mds.open(self.cfg.CURR_MD_IP,self.cfg.CURR_MD_PORT)
            mds.write(self.pb.build(packet_types.FS_BLOCK_STORED,data))
            mds_reply = self.pb.extract_stream(mds.sock)
            mds.close()
            
#            print 'MDSERVER REPLY: %s' % mds_reply
            if mds_reply.type == packet_types.ACK:
                #tell client everything went ok
                self.net.write(self.pb.build(packet_types.FS_BLOCK_STORED,data))
            

            return STATE_STORE_BLOCK_INFO()
            
            
        except socket.timeout:
            print "Socket timed out. File transfer failed for %s:%s." % (self.oid, self.block_id)
            self.rollback(fout)
            #TODO: tell metadata that the client crashed on this operation
            return None
        except IOError:
            print "Error while creating file __%s__%s." % (self.oid, self.block_id)
            data = Data()
            data.oid = self.oid
            data.block_id = self.block_id
            #Notify client there was an error creating this file
            self.net.write(pb.build(packet_types.FS_ERR_STORE, data))
            return None

class Handle_FS_REQUEST_BLOCK(PacketHandler):
    def process(self,data):
        oid = data.oid
        block_id = data.block_id
        version = self.fs.get(oid,block_id)

 #       print "Client wants %s:%s (version %s)" % (oid, block_id, data.version)
        
        #check if we have the file and if not tell the client so
        if not version:
            print "Block not found: (%s,%s)" % (oid, block_id)
            d = packet_builder.Data(params={'oid':oid,'block_id':block_id,'version':data.version})
            self.net.write(self.pb.build(packet_types.FS_ERR_BLOCK_NOT_FOUND, d))
            return None
        
        #check if we have the correct version and if not tell the client which version we have
        if int(version) != int(data.version):
            d = packet_builder.Data(params={'oid':oid,'block_id':block_id,'version':version})
            print "Incorrect version: I have (%s) and client wants (%s)" % (version, data.version)
            self.net.write(self.pb.build(packet_types.FS_ERR_INCORRECT_VERSION, d))
            return None
            
        #get the file length
        try:
            file = os.path.join(self.app.get_storage_path(oid,block_id),'__%s__%s' % (oid,block_id))
            length = os.path.getsize(file)
        except OSError:
            #if we didn't find a file tell the client
            d = packet_builder.Data(params={'oid':oid,'block_id':block_id,'version':data.version})
            self.net.write(self.pb.build(packet_types.FS_ERR_BLOCK_NOT_FOUND, d))
            #and update our database
            self.fs.delete(oid)
            return None
        
        try:
            #confirm the file transfer
            data = packet_builder.Data(params={'oid':oid,'block_id':block_id,'version':version,'length':length})

            self.net.write(self.pb.build(packet_types.FS_REQUEST_OK, data))

            #send the file!
            f = open(file,'rb')

            while 1:
                buf = f.read(64000)
                if not buf:
                    break
                self.net.write(buf)            

            f.close()
            
        except socket.timeout:
            print "Socket timed out. File transfer failed for %s:%s." % (oid,block_id)
        except IOError:
            print "Something went wrong while reading %s:%s" % (oid, block_id)
            
        return None

class STATE_FS_MODIFY_BLOCK(PacketHandler):
    def __init__(self, oid, block_id, length, version, block_offset):
        self.oid = oid
        self.block_id = block_id
        self.length = length
        self.version = version
        self.block_offset = block_offset #distance from the begining of the file to the beginning of this block
        
    def process(self,data):
#        print "Request to modify block: %s:%s version %s (%s:%s)" % (self.oid, self.block_id, self.version, self.block_offset, self.length)
        oid = self.oid
        block_id = self.block_id
        stored_version = self.fs.get(oid,block_id)

        #check if we have the file and if not tell the client so
        if not stored_version:
            d = packet_builder.Data(params={'oid':oid,'block_id':self.block_id,'version':self.version})
            self.net.write(self.pb.build(packet_types.FS_ERR_BLOCK_NOT_FOUND, d))
            return None
        
        #check if we have the correct version and if not tell the client which version we have
        if int(stored_version) != int(self.version):
            print "We have a different version! (%s vs %s)" % (stored_version, data.version)
            d = packet_builder.Data(params={'oid':oid,'block_id':block_id,'version':self.version})
            self.net.write(self.pb.build(packet_types.FS_ERR_INCORRECT_VERSION, d))
            return None
        
        #try to get a lock for this block from the metadata server
 #       print "Getting lock..."
        if not self.app.get_block_lock(self.oid, self.block_id, self.version):
            d = packet_builder.Data(params={'oid':oid,'block_id':self.block_id,'version':self.version})
            self.net.write(self.pb.build(packet_types.FS_ERR_LOCK_DENIED, d))
            return None
            
        #TODO: release locks after each failure
        
        #get the file length
        try:
            file = os.path.join(self.app.get_storage_path(oid,block_id),'__%s__%s' % (oid, block_id))
            file_size = os.path.getsize(file)
        except OSError:
            #if we didn't find a file tell the client
            d = packet_builder.Data(params={'oid':oid,'version':self.version})
            self.net.write(self.pb.build(packet_types.FS_ERR_OID_NOT_FOUND, d))
            #and update our database
            self.fs.delete(oid)
            return None

        offset = self.block_offset
        #check that if the client is not appending it's not trying to write outside the file bounds
        if offset != -1:
  #          print "Block size: %s, block offset: %s" % (file_size, offset)
            if offset > file_size:
                data = packet_builder.Data(params={'oid':oid,'block_id':self.block_id,'version':self.version,'serverid':self.cfg.SERVER_ID,})
                self.net.write(self.pb.build(packet_types.FS_ERR_BUFFER_OUT_OF_RANGE,data))
                return None

        return STATE_MODIFY_BLOCK(self.oid, self.block_id, self.block_offset, self.length, self.version)

class STATE_MODIFY_BLOCK(PacketHandler):
    def __init__(self, oid, block_id, offset, length, version):
        self.oid = oid
        self.block_id = block_id
        self.offset = offset
        self.length = length
        self.version = version

    
    
    def rollback(self, fout):
        """Erase the file and entry we were dealing with"""
        self.fs.delete(self.oid)

        if fout:
            fout.close()
            
        #TODO: Notify metadata server we no longer have this file
        
    def process(self,data):
        try:
            #open the file, read the data from the network and store it in the filesystem
            if self.offset == -1:
                fout = open(os.path.join(self.app.get_storage_path(self.oid,self.block_id),'__%s__%s' % (self.oid, self.block_id)), "ab+")
            else:
                fout = open(os.path.join(self.app.get_storage_path(self.oid,self.block_id),'__%s__%s' % (self.oid, self.block_id)), "r+w")
                fout.seek(self.offset)
            
#            print "Trying to get and write %s bytes at %s" % (self.length, self.offset)
            l = 0
            remaining = self.length
            buf_size = 64000

            while remaining > 0:
                if buf_size > remaining:
                    buf_size = remaining

                buf = self.net.read_buffered(buf_size)
                l += len(buf)
                remaining -= len(buf)
                fout.write(buf)
    
            fout.close()
            
            #get the new size of the block
            block_size = os.path.getsize(os.path.join(self.app.get_storage_path(self.oid,self.block_id),'__%s__%s' % (self.oid,self.block_id)))
            
#            print "Update block: %s:%s" % (self.oid, self.block_id)
            
            data = packet_builder.Data(params={'oid':self.oid,'block_id':self.block_id, 'length':l,'version':self.version,'serverid':self.cfg.SERVER_ID,'offset':self.offset,'block_size':block_size})
            
            #tell metadata server we succesfully modified the block
            mds = network_services.NetworkTransport()
            mds.open(self.cfg.CURR_MD_IP,self.cfg.CURR_MD_PORT)
            mds.write(self.pb.build(packet_types.FS_MODIFY_DONE,data))
            mds_reply = self.pb.extract_stream(mds.sock)

            
            print 'MDSERVER REPLY: %s' % mds_reply
            if mds_reply.type == packet_types.FS_MODIFY_ACK:
                #store the replica information in the data server's local database
                self.fs.add(mds_reply.oid, mds_reply.block_id, mds_reply.version)
                mds.write(self.pb.build(packet_types.FS_VERSION_UPDATED,mds_reply))

                data.version = mds_reply.version 
                #tell client everything went ok
                self.net.write(self.pb.build(packet_types.FS_MODIFY_DONE,data))
            else:
                self.rollback(None)
            
            mds.close()

            return STATE_STORE_BLOCK_INFO()
            
        except socket.timeout:
            print "Socket timed out. File transfer failed for %s." % self.oid
            self.rollback(fout)
            return None
        except IOError:
            print "Error while creating file __%s." % self.oid
            data = Data()
            data.oid = self.oid
            #Notify client there was an error creating this file
            self.net.write(pb.build(packet_types.FS_ERR_STORE, data))
            self.rollback(fout)
            return None

class Handle_FS_DELETE_BLOCK(PacketHandler):
    def process(self,data):
#        print "Request to delete block: (%s,%s) " % (data.oid, data.block_id)
        
        oid = data.oid
        block_id = data.block_id
        version = self.fs.get(oid, block_id)
        
        #if we have the block, delete it from the database and the file system
        if version:
            file = os.path.join(self.app.get_storage_path(oid,block_id),'__%s' % oid)
            self.fs.delete(oid, block_id)
            if os.path.exists(file):
                os.unlink(file)
        
        #confirm the block delete
        data = packet_builder.Data(params={'oid':oid, 'block_id':block_id})
        self.net.write(self.pb.build(packet_types.FS_DELETE_DONE,data))

        return None

class Handle_FS_REPLICATE_BLOCK(PacketHandler):
    def process(self,data):
        (oid, block_id, version, serverid, ip, port) = (data.oid, data.block_id, data.version,data.serverid,data.ip,data.port)
        
        client = hydra_client_api.HydraClientAPI(None)
        client.set_primary_mdserver(self.cfg.CURR_MD_IP, self.cfg.CURR_MD_PORT)
        client.set_mdservers(self.cfg.mdservers)
        
        dest = os.path.join(self.app.get_storage_path(oid,block_id),'__%s__%s' % (oid, block_id))
        data.ip = self.cfg.IP
        data.port = self.cfg.PORT
        data.serverid = self.cfg.SERVER_ID
        
        block = fs_objects.FSBlock(oid, block_id, version, 0, 0)
        buf = client.get_block(block, ip, port)
        
        file = open(dest, 'wb')
        file.write(buf)
        file.close()
        
        self.fs.add(oid,block_id, version)
#        print "Successfully replicated oid %s, block_id %s (version %s)" % (oid, block_id, version)
        
        #tell metadata that we have now replicated this block
        mds = network_services.NetworkTransport()
        mds.open(self.cfg.CURR_MD_IP,self.cfg.CURR_MD_PORT)
        mds.write(self.pb.build(packet_types.FS_REPLICATE_DONE,data))
        mds.close()
        
def initialize(app):
	"""This function gets called by the plugin initializer"""
	app.addHandler(packet_types.FS_BEGIN_WRITE,Handle_FS_BEGIN_WRITE())
	app.addHandler(packet_types.FS_REQUEST_BLOCK,Handle_FS_REQUEST_BLOCK())
	app.addHandler(packet_types.FS_DELETE_BLOCK,Handle_FS_DELETE_BLOCK())
	app.addHandler(packet_types.FS_REPLICATE_BLOCK,Handle_FS_REPLICATE_BLOCK())
