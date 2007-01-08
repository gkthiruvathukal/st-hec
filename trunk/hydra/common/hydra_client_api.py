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
from fs_db import FileSystemError
import network_services,packet_builder,packet_types,fs_objects, plugin
from xml.dom import minidom
from fs_objects import FSBlock
from fs_objects import FSObject

class HydraClientException(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self)

class ConfigException(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self)

class Config:
    def __init__(self):
        self.CURR_MD_IP = '' #ip of the metadata server we managed to contact
        self.CURR_MD_PORT = '' #port of the metadata server we managed to contact
        self.mdservers = [] #list of metadata servers to contact
        
    
    def loadConfigFile(self, file):

        if not os.path.exists(os.path.abspath(file)):
            raise ConfigException("Could not find config file")
        
        try:
            xmldoc = minidom.parse(os.path.abspath(file))
            
            for c in xmldoc.getElementsByTagName('mdserver'):
                self.mdservers.append((c.attributes['ip'].value,int(c.attributes['port'].value)))
    
        except:
            raise ConfigException("Error in config file")
        
    def viewConf(self):
        print "MDServers: %s" % self.mdservers

class HydraClientAPI:
    def __init__(self, cfg_path):
    
        self.cfg = Config()
        if cfg_path:
            self.cfg.loadConfigFile(cfg_path)

        self.net = None
        self.pb = packet_builder.PacketBuilder()
        
        plugin.initPlugins(self,'./common/plugins')

    def registerPacket(self, code, builder):
        self.pb.registerPacket(code,builder)

    def set_mdservers(self, mdservers):
        """Sets the client's list of metadata servers to contact"""
        self.cfg.mdservers = mdservers
        
    def set_primary_mdserver(self, ip, port):
        """Sets the client's primary mdserver to try"""
        self.cfg.CURR_MD_IP = ip
        self.cfg.CURR_MD_PORT = port

    def __open_mdserver(self):
        """Open a connection to the metadata server"""
        
        #first try the primary metadata server we have defined
        try:
            if self.cfg.CURR_MD_IP and self.cfg.CURR_MD_PORT:
                net = network_services.NetworkTransport()
                net.open(self.cfg.CURR_MD_IP, self.cfg.CURR_MD_PORT)
                return net
        except Exception, e:
            pass
            
        #if that didn't work, then try one from our list of data servers
        
        if not len(self.cfg.mdservers):
            print "No metadata servers defined! Shutting down..."
            return None
    
        for server in self.cfg.mdservers:
            try:
                net = network_services.NetworkTransport()
                net.open(server[0],server[1])
                self.cfg.CURR_MD_IP = server[0]
                self.cfg.CURR_MD_IP = server[1]
                return net
            except Exception, e:
                pass
                
        #if we couldn't find anything, then there's nothing else we can do!
        
        print "No alive metadata servers found!"
        return None
        
    def __open_dataserver(self, ip, port):
#        print "Contacting dataserver %s:%s" % (ip, port)
        try:
            net = network_services.NetworkTransport()
            net.open(ip,port)
            return net
        except network_services.NetworkError:
            print "Could not contact dataserver"
            return None
                
    def __tell_server(self, net, ptype, data):
        net.write(self.pb.build(ptype, data))

    def make_object(self, path, type):

        print "Creating: %s" % path
        net = self.__open_mdserver()

        data = packet_builder.Data()
        data.path = path
        data.file_type = type
        data.block_size = 0
        data.replicas = 0

        self.__tell_server(net,packet_types.FS_CREATE,data)

        #Let's see what the metadata server thinks about it
        data = self.pb.extract_stream(net.sock)
        net.close()

        if data.type == packet_types.FS_CREATE_OK:
            pass
#            print "Success! OID: %s Store it at: %s:%s" % (data.oid,data.ip,data.port)
        elif data.type == packet_types.FS_NODE_CREATED:
#            print "folder created (oid=%s)" % (data.oid)
            return (True,data)

        elif data.type == packet_types.FS_ERR_NODATASERVERS:
            raise FileSystemError("Server says there are no dataservers")
            return (False, None)
        
        elif data.type == packet_types.FS_ERR_CREATE:
            raise FileSystemError("Server says file already exists")
            return (False, None)
        
        data.port = int(data.port)
        
        return (True, data)

    def get_file_info(self,path):

#        print "Looking up: %s" % path
        net = self.__open_mdserver()
#        print "Connected! Getting file info..."

        #Tell metadata server we want to create this file
        data = packet_builder.Data()
        data.path = path
        
        self.__tell_server(net,packet_types.FS_GET,data)
        data = self.pb.extract_stream(net.sock)
        net.close()

        if data.type == packet_types.FS_GET_OK:
            (oid,version,file_size,block_size,blocks) = (data.oid,data.version,data.file_size,data.block_size,data.blocks)
#            print "Found file: oid=%s version=%s" % (oid, version)
        elif data.type == packet_types.FS_ERR_PATH_NOT_FOUND:
            raise HydraClientException("File not found")
        elif data.type == packet_types.FS_ERR_NO_REPLICAS:
            raise HydraClientException("No available replicas for this file")
        else:
            raise HydraClientException("Unknown packet: %s" % data.type)
        
        parent=0
        
        file = FSObject(oid, version, path, file_size, data.file_type, parent, block_size)
        block_locations = {}
        
        for b in blocks:
            block = FSBlock(oid, b.block_id, b.version, b.offset, b.length)
            file.blocks[block.block_id] = block
            block_locations[block.block_id] = (b.ip, b.port, b.serverid)
        
        return (file, block_locations)
    
    def rename_file(self, src, dest):
        #Tell metadata server we want to create this file
        data = packet_builder.Data(params={'src_path':src,'dest_path':dest})

        net = self.__open_mdserver()
        self.__tell_server(net,packet_types.FS_RENAME_FILE,data)
        data = self.pb.extract_stream(net.sock)
        net.close()

        if data.type == packet_types.FS_RENAME_DONE:
            pass
#           print "Rename successful %s -> %s" % (data.src_path, data.dest_path)
        elif data.type == packet_types.FS_ERR_RENAME:
            raise HydraClientException("Could not rename file %s -> %s" % (data.src_path, data.dest_path))
        else:
            raise HydraClientException("Unknown packet: %s" % data.type)
        
    
    def get_block(self, block, ip, port, offset=0, length=0):

#        print "Getting block from %s:%s" % (ip,port)
        net = self.__open_dataserver(ip, port)

        #if something went wrong then tell the metadata server about it
        if not net:
            data = packet_builder.Data(params={'oid':block.oid,'block_id':block.block_id,'ip':ip,'port':port})

            net = self.__open_mdserver()
            self.__tell_server(net,packet_types.FS_ERR_DATASERVER_FAILED,data)
            
        #tell dataserver we want to get this block
        data = packet_builder.Data(params={'oid':block.oid,'block_id':block.block_id,'version':block.version})
        self.__tell_server(net, packet_types.FS_REQUEST_BLOCK, data)
        data = self.pb.extract_stream(net.sock)
        
#        print data
        
        if data.type == packet_types.FS_REQUEST_OK:
            pass
        elif data.type == packet_types.FS_ERR_BLOCK_NOT_FOUND:
            raise FileSystemError("Data server does not have that block! (%s,%s)" % (block.oid,block.block_id))
        elif data.type == packet_types.FS_ERR_INCORRECT_VERSION:
            raise FileSystemError("Data server has a different version of this block!")
        
        length = data.length
        buf = ''
        
        try:
            buf_size = 64000
            if length < buf_size:
                buf_size = length
    
            while len(buf) < length:
                buf += net.read_buffered(buf_size)
            
        except IOError:
            print "Error reading buffer!"
            raise FileSystemError("Error reading data from file server!")
        
        return buf
    
    def modify_block(self, oid, block_id, version, buf, offset=0):

        data = packet_builder.Data()
        data.oid = oid
        data.block_id = block_id
        data.version = version
        data.length = len(buf)
        data.offset = offset
        
        try:
            #ask the dataserver if we can store this block
            self.__tell_server(self.net,packet_types.FS_MODIFY_BLOCK,data)
            data = self.pb.extract_stream(self.net.sock)
                    
            #if it's not ok, then raise an exception
            if data.type == packet_types.FS_MODIFY_OK:
                pass
            elif data.type == packet_types.FS_ERR_BUFFER_OUT_OF_RANGE:
                raise FileSystemError("Server said our buffer is out of range")
            elif data.type == packet_types.FS_ERR_BUFFER_OUT_OF_RANGE:
                raise FileSystemError("Dataserver says our buffer is out of range!")
            elif data.type == packet_types.FS_ERR_OID_NOT_FOUND:
                raise FileSystemError("Dataserver says it doesn't have this file!")
            elif data.type == packet_types.FS_ERR_INCORRECT_VERSION:
                raise FileSystemError("Dataserver says we have a different version")
            else:
                raise FileSystemError("Unknown error!")
                    
            #send the block data
            self.net.write(buf)
            
            data = self.pb.extract_stream(self.net.sock)
            
            #if our block was stored successfully
            if data.type != packet_types.FS_MODIFY_DONE:
                raise FileSystemError("0Error writing (%s:%s): Data server failed" % (oid,block_id))
            
            return data
            
        except IOError, e:
            raise FileSystemError("1Error writing (%s:%s): Data server failed" % (oid,block_uid))
    
    def create_block(self, oid, block_id, buf, offset):
        data = packet_builder.Data()
        data.oid = oid
        data.block_id = block_id
        data.version = 1
        data.length = len(buf)
        data.offset = offset
        
        try:
            #ask the dataserver if we can store this block
            self.__tell_server(self.net,packet_types.FS_STORE_BLOCK,data)
            data = self.pb.extract_stream(self.net.sock)
                    
            #if it's not ok, then raise an exception
            if data.type != packet_types.FS_STORE_OK:
                raise FileSystemError("Data server won't store our block!")
                    
            #send the block data
            self.net.write(buf)
            
            data = self.pb.extract_stream(self.net.sock)
                    
            #if our block was stored successfully
            if data.type != packet_types.FS_BLOCK_STORED:
                raise FileSystemError("Error writing %s (%s:%s): Data server failed" % (self.name, self.oid, self.current_block))
                
        except IOError, e:
            print e
            raise FileSystemError("Error writing %s (%s:%s): Data server failed" % (oid,block_id))
        
    
    
    def start_write_session(self, oid, version, ip, port):
        self.net = self.__open_dataserver(ip, port)
        
        #if something went wrong then tell the metadata server about it
        if not self.net:
            data = packet_builder.Data(params={'oid':oid,'ip':ip,'port':port})
            net = self.__open_mdserver()
            self.__tell_server(net,packet_types.FS_ERR_DATASERVER_FAILED,data)
            raise FileSystemError("Error writing %s: Could not contact a data server" % oid)

        #tell dataserver we want to store this file
        data = packet_builder.Data(params={'oid':oid,'version':version})
        self.__tell_server(self.net, packet_types.FS_BEGIN_WRITE, data)
        
#        print "Waiting for response from server"
        data = self.pb.extract_stream(self.net.sock)
        
#        print "Received response from server"

        if data.type == packet_types.FS_WRITE_READY:
            pass
#            print "Dataserver said it's ok to store the file"
        elif data.type == packet_types.FS_ERR_STORE:
            raise FileSystemError("Data server won't store our block!")
    
    
            
    def end_write_session(self, oid, version):
        
        data = packet_builder.Data()
        data.oid = oid
        data.version = version
        
        self.__tell_server(self.net, packet_types.FS_END_WRITE, data)
        self.net.close()
        self.net = None
        
    def stat_file(self,path):
#        print "Getting info on: %s" % path
        net = self.__open_mdserver()
        
        if not net:
            return False

        #Tell metadata server we want to get info on this file
        data = packet_builder.Data(params={'path':path})
        
        self.__tell_server(net,packet_types.FS_STAT_FILE,data)
        data = self.pb.extract_stream(net.sock)
        net.close()

        if data.type == packet_types.FS_ERR_PATH_NOT_FOUND:
            print "Server said file does not exist"
            return (None,None)
            
        if data.type == packet_types.FS_FILE_INFO:
            file = fs_objects.FSObject(data.oid, data.version, data.path, data.size, data.file_type, data.parent, data.block_size)
            
            if file.type == 0:
                children = []
                for child in data.children:
                    children.append(fs_objects.FSObject(child.oid, child.version, child.path, child.block_size, child.size, child.file_type, child.parent))
                
                return (file, children)
            else:
                return (file,None)
