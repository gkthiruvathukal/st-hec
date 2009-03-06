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
import network_services,packet_builder,packet_types,fs_objects
import getopt
import os
import sys
import threading
import signal

from xml.dom import minidom

from fs_objects import FSBlock
from fs_db import FileSystemError
from hydra_client_api import HydraClientAPI, HydraClientException
        
class HydraFile:
    def __init__(self,cfg_path):
        self.name = None
        self.mode = None
        self.closed = True
        self.encoding = None
        #self.newlines
        self.softspace = 0
        
        self.current_block = 0
        self.current_buf = ''
        self.current_byte = 0
        
        self.blocks = {} #blocks the file is composed of
        self.block_locations = {} #location of each block [block_id] = (ip,port,serverid)
        
        if cfg_path:
            self.hydra = HydraClientAPI(cfg_path)
        
    
    def show_block_locations(self):
        locs = {}
        
        for block_id in self.block_locations.keys():
            (ip,port,serverid) = self.block_locations[block_id]
            if not locs.has_key(serverid):
                locs[serverid] = 0
            locs[serverid] += 1
        
        for serverid in locs.keys():
            print "Server: %s, blocks: %s" % (serverid, locs[serverid])
    
    def __get_file_info(self, path):
        print "HydraFile.__get_file_info: %s" % path
        (file, block_locations) = self.hydra.get_file_info(path)

        self.block_locations = block_locations
        self.blocks = file.blocks
        self.name = path
        self.oid = file.oid
        self.version = file.version
        self.block_size = file.block_size
        self.file_size = file.size


    def delete_file(self, file):        
        self.__exists_object(file)
    
    def __exists_object(self, obj):
        (file, children) = self.hydra.stat_file(obj)
        if not file:
            raise HydraClientException("File not found: %s" % path)
    
        return (file,children)
    
    def stat_file(self,path):
        import stat
        st_mode = 0
        
        #print "HydraFile.stat_file(%s)" % path
        (file, children) = self.__exists_object(path)
        #print "HydraFile.stat_file: %s" % file        
        
        if file.type == 1: #this is a file
            st_mode |= stat.S_IFREG
        elif file.type == 0: #this is a folder
            st_mode |= stat.S_IFDIR
        
        #set permisions
        st_mode |= stat.S_IRWXU | stat.S_IRWXO | stat.S_IRWXG
        
        st_ino = file.oid #node
        st_dev = 2051L #device
        st_nlink = 2 #number of hard links
        if children:
            st_nlink = len([x for x in children if x.type == 1])
        st_uid = 500 #owner of the file
        st_gid = 500 #group owner
        st_size = file.size #file size
        st_atime = st_mtime = st_ctime = 1140711837 #temp file times
        
        return(st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime, st_mtime, st_ctime)
        
    def __transfer_buffer(self,buf):
    
        length = len(buf)
        
        if not length:
            return
        
        bytes_transferred = 0
        
        prev_ip = None
        prev_port = None
        
        while bytes_transferred < length:
            (block_id,offset,l) = self.__calc_next_block(self.current_byte, self.current_byte + length - bytes_transferred)
#            print "Current byte: %s" % self.current_byte
#            print "Block id: %s, offset: %s, length: %s" % (block_id, offset, l)
            
            if block_id:
                #the block exists, so we only have to modify it
                oid = self.oid
                version = self.blocks[block_id].version
                buf_size = l
                
                (ip,port,serverid) = self.block_locations[block_id]
                
                #if the specified server location is not the one we were using previously
                if ip != prev_ip and port != prev_port:
                    
                    if prev_ip != None:
                        #close the write session and open a new one
                        self.hydra.end_write_session(self.oid, self.version)
                    
                    #open a new write session
                    self.hydra.start_write_session(self.oid, self.version, ip, port)
                    (prev_ip,prev_port) = (ip,port)

                data = self.hydra.modify_block(oid, block_id, version, buf[bytes_transferred:bytes_transferred+buf_size], offset)
                
                #if the block has grown in size, update our file size too
                self.file_size += data.block_size - self.blocks[block_id].size
                self.blocks[block_id].size = data.block_size
                self.blocks[block_id].version = data.version
                
            else:
                #there is no block to accomdate this byte location, so create a new one at the end of the file
                
                #if we don't already have a write session with a dataserver
                if prev_ip == None:
#                    print "NB: Start write session"
                    self.hydra.start_write_session(self.oid, self.version, self.ip, self.port)
                    (prev_ip, prev_port) = (self.ip, self.port)
                
                oid = self.oid
                version = 1
                block_id = self.__last_block() + 1 #get the block at the end of the file and create a new one after that
                offset = self.current_byte
            
                buf_size = 64000
                if self.block_size > 0:
                    buf_size = self.block_size

                if len(buf[bytes_transferred:]) < buf_size:
                    buf_size = len(buf[bytes_transferred:])
                
                self.hydra.create_block(oid, block_id, buf[bytes_transferred:bytes_transferred+buf_size], offset)

                b = FSBlock(oid, block_id, version, offset, buf_size)
                self.blocks[b.block_id] = b
                self.block_locations[b.block_id] = (self.ip, self.port, self.serverid)
                
                self.file_size += buf_size
            
            self.current_block += 1
            bytes_transferred += buf_size
            self.current_byte += buf_size
            
                
            if len(buf[bytes_transferred:]) < buf_size:
                buf_size = len(buf[bytes_transferred:])
                
        if prev_ip:
            self.hydra.end_write_session(self.oid, self.version)

#        print "Current byte: %s" % self.current_byte
#        print "__transfer_buffer: buffer size: %s" % buf_size
            
    
    def __calc_block(self, byte_loc):
        """Returns the block in which byte_loc is located or 0 if not found"""
        
        sorted_block_list = self.blocks.keys()
        sorted_block_list.sort()
        
#        print "Searching for block @ %s" % byte_loc
        found_block_id = 0
        for block_id in sorted_block_list:
            if self.blocks[block_id].offset <= byte_loc:
                if byte_loc < (self.blocks[block_id].size + self.blocks[block_id].offset):
                    found_block_id = block_id
        
        return found_block_id
        
    def __calc_next_block(self, start_byte, end_byte):
        """Returns the first block that can contain the byte range start_byte:end_byte
        as well as the block's offset and the amount of data that can be stored in the
        block for that range"""
        
        block_id = self.__calc_block(start_byte)
#        print "start_byte: %s, end_byte: %s" % (start_byte, end_byte)

        if block_id > 0:
            block = self.blocks[block_id]
            offset = start_byte - block.offset
            
            if end_byte <= (block.size + block.offset):
                length = end_byte - start_byte
            else:
                length = end_byte - (block.size + block.offset)
        else:
            #it might happen that the last block is still to be completed
            last_block_id = self.__last_block()

            if last_block_id > 0:
                last_block = self.blocks[last_block_id]
                
            if last_block_id > 0 and last_block.offset <= start_byte:

                if start_byte < (self.block_size + last_block.offset):
                    block_id = last_block.block_id
                    offset = last_block.size
                    if end_byte < (self.block_size + last_block.offset):
                        length = end_byte - start_byte
                    else:
                        length = self.block_size - offset
                else:
                    block_id = offset = length = 0
            else:
                    block_id = offset = length = 0
        
        return (block_id, offset, length)
                
    def __last_block(self):
        
        last_block = 0
        highest_offset = 0
        for block_id in self.blocks.keys():
            if self.blocks[block_id].offset >= highest_offset:
                last_block = block_id
                highest_offset = self.blocks[block_id].offset
        
        return last_block
        
    def __get_block(self, block_id):
    
        buf = None
        
        while 1:
            if not self.blocks.has_key(block_id):
                self.__get_file_info(self.name) #refresh file info in case block has just been added
                
                if not self.blocks.has_key(block_id): #there is no block with that id
                    return None
            
            block = self.blocks[block_id]
            (ip,port,serverid) = self.block_locations[block_id]
            try:
                buf = self.hydra.get_block(block,ip,port)
                break
            except FileSystemError, e:
                #if there was an error, then retry getting information from the metadata
                #and see if we get a different server for this block
                print 'FilesystemError: %s' % e.value
                self.__get_file_info(self.name)
        return buf

    def mkdir(self, pathname):
        (status, data) = self.hydra.make_object(pathname, 0)
        return status
        
    def stat(self, pathname):
        (file, children) = self.hydra.stat_file(pathname)
        return (file, children)
    
    def rename(self, src, dest):
        self.hydra.rename_file(src,dest)
        
    def delete(self, file):
        self.delete_file(file)
        
        
    
    def open(self,name,mode='r',bufsize=0):
        """Contacts the metadata server about a file and requests/sends information
        depending on the mode the file was opened"""

        print "HydraFile.open: (%s,%s,%s)" % (name,mode,bufsize)
        self.__init__(None)
        self.mode = mode
        
        path = name

        if mode == 'w':
            #Tell metadata server we want to create this file
            (status, data) = self.hydra.make_object(path, 1)
            if status == True:
                (self.oid, self.ip, self.port, self.serverid, self.version, self.block_size) = (data.oid, data.ip, data.port, data.serverid, data.version, data.block_size)
                self.file_size = 0
#                print "Using block_size: %s" % self.block_size
            else:
                print "Failed creating file"
        elif mode == 'r+w':
            self.__get_file_info(path)
        elif mode == 'r':
            self.__get_file_info(path)
        else:
            self.__get_file_info(path)

        self.current_block = 1L
        self.name = name
        

        
    def close(self):
        self.__init__(None) #clear internal state

    def flush(self):
        pass
        
#    def fileno(self):
#        pass

    def isatty(self):
        return False
        
    def next(self):
        pass

    def read(self,size=0):
        data = ''
#        print "Read @ %s, buf_size=%s" % (self.current_byte, size)
#        print "File size: %s" % self.file_size
        #determine the upper limit of the file's section we are reading
        if size > 0:
            top_byte = self.current_byte + size
            if top_byte > self.file_size:
                top_byte = self.file_size
        else:
            top_byte = self.file_size
        
        #read while we are within limits
        while self.current_byte < top_byte:
            try:
                self.current_block = self.__calc_block(self.current_byte)
                buf = self.__get_block(self.current_block)

                if not buf:
                    break

                lower_bound = 0
                upper_bound = len(buf)
                
                if self.blocks[self.current_block].offset < self.current_byte:
                    lower_bound = self.current_byte - self.blocks[self.current_block].offset
                
                if (top_byte - self.current_byte) < len(buf):
                    upper_bound = lower_bound + top_byte - self.current_byte
                
                buf = buf[lower_bound:upper_bound]
                data += buf
                self.current_byte += len(buf)

                #if we are trying to read the whole file, and we reach the end, query again for the
                #file info, just to make sure that in the meantime no more blocks were added
                if self.current_byte >= self.file_size:
                    self.__get_file_info(self.name)
                    if size == 0:
                        top_byte = self.file_size
                        
                    
            #if something goes wrong getting a block, then retry until we run out of dataservers
            except (HydraClientException, socket.error),e:
                print "Error while reading: %s (retrying)" % e
                try:
                    self.__get_file_info(self.name)
                except HydraClientException, e:
                    print "*** UNRECOVERABLE ERROR: %s" % e.value
                    return False
#        print "HydraFile.read: returning buffer size: %s" % len(data)
        return data
            

    def readline(self,size=0):
        pass
    def readlines(self,sizehint=0):
        pass
    def xreadlines(self):
        pass
        
    def seek(self,offset,whence=0):
    
        if whence == 0: #absolute positioning
            self.current_byte = offset
        
        elif whence == 1: #relative to current position
            self.current_byte += offset
        
        elif whence == 2: #relative to file's end
            self.file_size += offset
            
        if self.current_byte < 0:
            self.current_byte = 0
            
        if self.current_byte > self.file_size:
            self.current_byte = self.file_size
        
#        print "seek: positioned current byte at: %s" % self.current_byte
            
    def tell(self):
        pass
    def truncate(self,size=0):
        pass
    
    def write(self,str):
        #contact the dataserver
        print "HydraFile.write @byte: %s" % (self.current_byte)
        while 1:
            try:
                self.__transfer_buffer(str)
                break
            except (FileSystemError, socket.error), e:
                print "Error while writing: %s (retrying)" % e
                try:
                    self.__get_file_info(self.name)
                except HydraClientException, e:
                    print "*** UNRECOVERABLE ERROR: %s" % e.value
                    return False
        
        return True

    def writelines(self,sequence):
        pass


        
if __name__ == '__main__':
    
    import sys
    
    file = sys.argv[1]
    
    rounds = 5
    letters = 10
    from random import randint
    
    hf = HydraFile('../conf/fileclient1.xml')
    hf.open(file, 'w')
    for i in range(rounds):
        buf = ''
        for j in range(letters-1):
            buf += chr(randint(60,126))
        buf+= '\n'
        print buf,
        hf.write(buf)
    hf.close()
    
    
    hf.open(file,'r')
    buf = hf.read()
    print buf
    hf.close()

    hf.open(file,'r+w')
    hf.write('1234')
    hf.seek(19,0)
    hf.write('5\n678')
    hf.seek(27,0)
    hf.write('90')
    hf.close()

    hf.open(file,'r')
    buf = hf.read()
    hf.close()
    print buf
