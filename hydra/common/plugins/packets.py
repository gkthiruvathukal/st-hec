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


from common.packet_builder import Data
from common.plugin import Packet
from common import packet_types, network_services
import  socket, struct

class AnnounceBuilder(Packet):
    """Builds an ANNOUNCE packet"""
    def __init__(self):
        self.format_str = '!4sHI'
    def pack(self,data):    
        ip = socket.inet_aton(data.ip)
        port = int(data.port)
        sid = int(data.serverid)
        return struct.pack(self.format_str, ip, port, sid)
        
    def unpack(self,reader):
        data = Data()
        (ip, port, serverid) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        ip = socket.inet_ntoa(ip)
        data.ip = ip
        data.port = port
        data.serverid = "%s" % serverid
        data.type = packet_types.ANNOUNCE
        return data
    
class AckBuilder(Packet):
    """Builds an ACK packet"""
    def pack(self, data):
        return ''
    def unpack(self,reader):
        data = Data()
        data.type = packet_types.ACK
        return data
        
class HeartbeatBuilder(Packet):
    """Builds an ANNOUNCE packet"""
    def __init__(self):
        self.format_str = '!4sHI'

    def pack(self,data):    
        ip = socket.inet_aton(data.ip)
        port = int(data.port)
        sid = int(data.serverid)
        return struct.pack(self.format_str, ip, port, sid)
        
    def unpack(self,reader):
        (ip, port, serverid) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        ip = socket.inet_ntoa(ip)

        data = Data()
        data.ip = ip
        data.port = port
        data.serverid = "%s" % serverid
        data.type = packet_types.ANNOUNCE
                
        return data

class FSCreateBuilder(Packet):
    """Builds an FS_CREATE packet"""
    def __init__(self):
        self.format_str = '!I255sII'
    def pack(self, data):
        return struct.pack(self.format_str, data.file_type, data.path, data.block_size, data.replicas)
        
    def unpack(self, reader):

        (file_type, path, block_size, replicas) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))

        data = Data()
        data.file_type = file_type
        data.path = self._short_string(path) #self._short_string(path)
        data.block_size = block_size
        data.replicas = replicas
        data.type = packet_types.FS_CREATE
        
        return data

class FSErrCreate(Packet):
    """Builds an FS_ERR_CREATE packet"""
    def pack(self, data):
        return ''
        
    def unpack(self, reader):
        data = Data()
        data.type = packet_types.FS_ERR_CREATE

        return data

class FSErrNoDataServers(FSErrCreate):
    def unpack(self,reader):
        return ''
        
    def unpack(self,reader):
        data = Data()
        data.type = packet_types.FS_ERR_NODATASERVERS

        return data

class FSErrDataserverFailed(Packet):
    """Builds an FS_ERR_DATASERVER_FAILED packet"""
    def __init__(self):
        self.format_str = '!I4sH'

    def pack(self,data):
        return struct.pack(self.format_str, data.oid, socket.inet_aton(data.ip), data.port)
        
    def unpack(self,reader):
        (oid,ip,port) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        ip = socket.inet_ntoa(ip)
        data = Data(params={'oid':oid,'ip':ip,'port':port})
        data.type = packet_types.FS_ERR_DATASERVER_FAILED
        return data

class FSCreateFileOK(Packet):
    """Builds an FS_CREATE_OK packet"""

    def __init__(self):
        self.format_str = '!4sHIIII'

    def pack(self,data):
        ip = socket.inet_aton(data.ip)
        port = int(data.port)
        serverid = int(data.serverid)
        oid = int(data.oid)
        version = int(data.version)
        block_size = int(data.block_size)

        return struct.pack(self.format_str, ip, port, serverid, oid, version,block_size)

    
    def unpack(self,reader):
        
        (ip, port, serverid, oid, version, block_size) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        ip = socket.inet_ntoa(ip)

        data = Data(params={'ip':ip,'port':port,'serverid':serverid,'oid':oid,'version':version,'block_size':block_size})
        data.type = packet_types.FS_CREATE_OK
                
        return data

class BuildFSStoreBlock(Packet):
    """Builds an FS_STORE_BLOCK packet"""
    def __init__(self):
        self.format_str = '!IIIII'
        
    def pack(self,data):
        oid = int(data.oid)
        block_id = int(data.block_id)
        length = int(data.length)
        version = int(data.version)
        offset = int(data.offset)
        
        return struct.pack(self.format_str, oid, block_id, length, version, offset)

    def unpack(self,reader):
        (oid, block_id, length,version,offset) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
            
        data = Data(params={'oid':oid,'block_id':block_id,'length':length,'version':version,'offset':offset})
        data.type = packet_types.FS_STORE_BLOCK
                    
        return data
        
class BuildFSBeginWrite(Packet):
    """Builds an FS_BEGIN_WRITE packet"""
    def __init__(self):
        self.format_str = '!II'
    def pack(self,data):
        oid = int(data.oid)
        version = int(data.version)
        return struct.pack(self.format_str, oid, version)

    def unpack(self,reader):
        (oid, version) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))

        data = Data(params={'oid':oid,'version':version})
        data.type = packet_types.FS_BEGIN_WRITE
        return data
        
class BuildFSWriteReady(Packet):
    """Builds an FS_WRITE_READY packet"""
    def __init__(self):
        self.format_str = '!II'
        
    def pack(self,data):
        oid = int(data.oid)
        version = int(data.version)
        return struct.pack(self.format_str, oid, version)

    def unpack(self,reader):
        (oid, version) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        
        data = Data(params={'oid':oid,'version':version})
        data.type = packet_types.FS_WRITE_READY
        return data
    
class BuildFSEndWrite(Packet):
    """Builds an FS_END_WRITE packet"""
    def __init__(self):
        self.format_str = '!II'
    def pack(self,data):
        oid = int(data.oid)
        version = int(data.version)
        return struct.pack(self.format_str, oid, version)

    def unpack(self,reader):
        (oid, version) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        
        data = Data(params={'oid':oid,'version':version})
        data.type = packet_types.FS_END_WRITE
                
        return data

# ----- ok to store the file
class BuildFSStoreOK(Packet):
    """Builds an FS_STORE_OK Packet"""
    def pack(self,data):
        return ''
    def unpack(self,reader):
        data = Data()
        data.type = packet_types.FS_STORE_OK
        return data
    
# ------ Block stored        
class BuildFSBlockStored(Packet):
    """Builds an FS_BLOCK_STORED packet"""
    def __init__(self):
        self.format_str = '!IIIIII'

    def pack(self, data):
        return struct.pack(self.format_str, int(data.oid), int(data.block_id), int(data.length), int(data.version), int(data.serverid), int(data.offset))

    def unpack(self,reader):
        (oid, block_id, length, ver,serverid, offset) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid, 'block_id':block_id, 'length':length,'version':ver,'serverid':serverid,'offset':offset})
        data.type = packet_types.FS_BLOCK_STORED
        return data

class BuildFSGet(Packet):
    """Builds an FS_GET packet"""
    def __init__(self):
        self.format_str = '!255s'
        
    def pack(self,data):
        return struct.pack(self.format_str, data.path)
        
    def unpack(self,reader):
        data = Data()        
        path = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data.path = self._short_string(path[0])
        data.type = packet_types.FS_GET
        
        return data

class FSGetOK(Packet):
    """Builds an FS_GET_OK packet"""
    def __init__(self):
        self.format_str = '!IIIIII'
        self.child_format_str = '!IIIII4sH'

    def pack(self,data):

        buf = struct.pack(self.format_str, int(data.oid), int(data.file_size), int(data.block_size), int(data.version), int(data.file_type), len(data.blocks))
        blocks = data.blocks
        
        for block in blocks:
            ip = socket.inet_aton(block.ip)
            port = int(block.port)
            block_id = int(block.block_id)
            version = int(block.version)
            block_size = int(block.block_size)
            offset = int(block.offset)
            serverid = int(block.serverid)
            buf += struct.pack(self.child_format_str, block_id, version, offset, block_size, serverid, ip, port)
        return buf
        
    def unpack(self,reader):
    
        data = Data()        
        (oid,file_size,block_size, version,file_type,num_blocks) = struct.unpack(self.format_str,reader.read(struct.calcsize(self.format_str)))
        
        blocks = []
        for i in range(num_blocks):
            (block_id, version, offset, length, serverid, ip, port) = struct.unpack(self.child_format_str, reader.read(struct.calcsize(self.child_format_str)))
            ip = socket.inet_ntoa(ip)
            block_data = Data(params={'block_id':block_id,'version':version,'offset':offset,'length':length,'serverid':serverid,'ip':ip,'port':port})
            blocks.append(block_data)
            
        data.oid = oid
        data.file_size = file_size
        data.version = version
        data.block_size = block_size
        data.file_type = file_type
        data.blocks = blocks
        data.type = packet_types.FS_GET_OK
        
        return data

class BuildFSRequestBlock(Packet):
    def __init__(self):
        self.format_str = '!III'
    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.block_id), int(data.version))
        
    def unpack(self,reader):
        (oid, block_id, version) = struct.unpack(self.format_str,reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid,'block_id':block_id, 'version':version})
        data.type = packet_types.FS_REQUEST_BLOCK
        return data

class BuildFSRequestOK(Packet):
    """Builds an FS_REQUEST_OK packet"""
    def __init__(self):
        self.format_str = '!IIII'

    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.block_id), int(data.version), int(data.length))
        
    def unpack(self,reader):

        (oid, block_id, version, length) = struct.unpack(self.format_str,reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid,'block_id':block_id,'version':version,'length':length})
        data.type = packet_types.FS_REQUEST_OK
        return data
        
#----------- Path not found error
class BuildFSErrPathNotFound(Packet):
    """Builds an FS_ERR_PATH_NOT_FOUND packet"""
    def pack(self,data):
        return ''

    def unpack(self,reader):
        data = Data()
        data.type = packet_types.FS_ERR_PATH_NOT_FOUND

        return data
class BuildFSErrNoReplicas(Packet):
    """Builds an FS_ERR_NO_REPLICAS packet"""
    def pack(self,data):
        return ''
        
    def unpack(self,reader):
        data = Data()
        data.type = packet_types.FS_ERR_NO_REPLICAS

        return data

#----------- No oid in dataserver error
class BuildFSErrBlockNotFound(Packet):
    """Builds an FS_ERR_BLOCK_NOT_FOUND packet"""
    def __init__(self):
        self.format_str = '!III'
    def pack(self,data):
        return struct.pack(self.format_str, data.oid, data.block_id, data.version)
        
    def unpack(self,reader):
        (oid, block_id, version) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid, 'block_id':block_id, 'version':version})
        data.type = packet_types.FS_ERR_BLOCK_NOT_FOUND

        return data

#----------- Incorrect oid version  in dataserver error
class BuildFSErrIncorrectVersion(Packet):
    """Builds an FS_INCORRECT_VERSION packet"""
    def __init__(self):
        self.format_str = '!III'
    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.block_id), int(data.version))
        
    def unpack(self,reader):
        (oid, block_id, version) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid,'block_id':block_id,'version':version})
        data.type = packet_types.FS_ERR_INCORRECT_VERSION

        return data

class BuildFSWriteFile(Packet):
    """Builds an FS_WRITE_FILE packet"""
    def __init__(self):
        self.format_str = '!255siI'
        
    def pack(self,data):
        return struct.pack(self.format_str, data.path, data.offset, data.length)
    
    def unpack(self,reader):
        (path,offset,length) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'path':self._short_string(path),'offset':offset,'length':length})
        data.type = packet_types.FS_WRITE_FILE
        
        return data

class BuildFSWriteOK(Packet):
    """Builds an FS_WRITE_OK packet"""
    def __init__(self):
        self.format_str = '!III'
        self.child_format_str = '!IIIII4sH'
    def pack(self,data):
        buf = struct.pack(self.format_str, int(data.oid), int(data.version), len(data.blocks))
        
        for block in blocks:
            ip = socket.inet_aton(block.ip)
            port = int(block.port)
            block_id = int(block.block_id)
            version = int(block.version)
            block_size = int(block.block_size)
            offset = int(block.offset)
            buf += struct.pack(self.child_format_str, block_id, version, offset, block_size, serverid, ip, port)
        return buf
        
    def unpack(self,reader):
        data = Data()        
        (oid,version,num_blocks) = struct.unpack(self.format_str,reader.read(struct.calcsize(self.format_str)))
        
        blocks = []
        for i in range(num_blocks):
            (block_id, version, offset, length, serverid, ip, port) = struct.unpack(self.child_format_str, reader.read(struct.calcsize(self.child_format_str)))
            ip = socket.inet_ntoa(ip)
            block_data = Data(params={'block_id':block_id,'version':version,'offset':offset,'length':length,'serverid':serverid,'ip':ip,'port':port})
            blocks.append(block_data)
            
        data[blocks] = blocks
        data.type = packet_types.FS_WRITE_OK
        
        return data

class BuildFSModifyBlock(Packet):
    """Builds an FS_MODIFY_BLOCK packet"""
    def __init__(self):
        self.format_str = '!IIIII'
    
    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.block_id), int(data.version), int(data.offset), int(data.length))
    
    def unpack(self,reader):
        (oid, block_id, version, offset, length) = struct.unpack(self.format_str,reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid,'block_id':block_id,'version':version,'offset':offset,'length':length})
        data.type = packet_types.FS_MODIFY_BLOCK
        
        return data

class BuildFSModifyOK(Packet):
    """Builds an FS_MODIFY_OK packet"""
    def __init__(self):
        self.format_str = '!III'
    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.block_id), int(data.version))

    def unpack(self,reader):
        (oid, block_id, version) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid,'block_id':block_id,'version':version})
        data.type = packet_types.FS_MODIFY_OK
        return data

class BuildFSModifyDone(Packet):
    """Builds an FS_MODIFY_DONE packet"""
    def __init__(self):
        self.format_str = '!IIIIiII'
    def pack(self,data):
        return struct.pack(self.format_str, int(data.serverid), int(data.oid), int(data.block_id), int(data.version), int(data.offset), int(data.length), int(data.block_size))

    def unpack(self,reader):
        (serverid,oid,block_id,version,offset,length,block_size) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'serverid':serverid,'oid':oid,'block_id':block_id,'version':version,'offset':offset,'length':length,'block_size':block_size})
        data.type = packet_types.FS_MODIFY_DONE
        return data

class BuildFSModifyAck(Packet):
    """Builds an FS_MODIFY_ACK packet"""
    def __init__(self):
        self.format_str = '!III'
    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.block_id), int(data.version))

    def unpack(self,reader):
        (oid, block_id, version) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid,'block_id':block_id,'version':version})
        data.type = packet_types.FS_MODIFY_ACK
        return data

class BuildFSGetLock(Packet):
    """Builds an FS_GET_LOCK packet"""
    def __init__(self):
        self.format_str = '!IIII'

    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.block_id), int(data.version), int(data.serverid))
    
    def unpack(self,reader):
        (oid, block_id, version,serverid) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid, 'block_id':block_id, 'version':version,'serverid':serverid})
        data.type = packet_types.FS_GET_LOCK
        return data

class BuildFSLockOK(Packet):
    """Builds an FS_LOCK_OK packet"""
    def __init__(self):
            self.format_str = '!III'
            
    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.block_id), int(data.version))
        
    def unpack(self,reader):
        (oid,block_id,version) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid,'block_id':block_id,'version':version})
        data.type = packet_types.FS_LOCK_OK
        return data

class BuildFSVersionUpdated(Packet):
    """Builds an FS_VERSION_UPDATED packet"""
    def __init__(self):
        self.format_str = '!III'
    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.block_id), int(data.version))

    def unpack(self,reader):
        (oid, block_id, version) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid,'block_id':block_id,'version':version})
        data.type = packet_types.FS_VERSION_UPDATED
        return data

class BuildFSBufferOutOfRange(Packet):
    """Builds an FS_ERR_BUFFER_OUT_OF_RANGE packet"""
    def __init__(self):
        self.format_str = '!II'
        
    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.version))

    def unpack(self,reader):
        (oid,version) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid,'version':version})
        data.type = packet_types.FS_ERR_BUFFER_OUT_OF_RANGE
        return data

class BuildFSWriteError(Packet):
    """Builds an FS_WRITE_ERROR packet"""
    def __init__(self):
        self.format_str = '!III'
    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.block_id), int(data.version))

    def unpack(self,reader):
        (oid,version) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid,'block_id':block_id,'version':version})
        data.type = packet_types.FS_WRITE_ERROR
        return data
class BuildFSErrLockDenied(Packet):
    """Builds an FS_ERR_LOCK_DENIED packet"""
    def __init__(self):
        self.format_str = '!III'
    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.block_id), int(data.version))

    def unpack(self,reader):
        
        (oid,block_id,version) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid,'block_id':block_id,'version':version})
        data.type = packet_types.FS_ERR_LOCK_DENIED
        return data
        
class BuildFSDeleteFile(Packet):
    """Builds an FS_DELETE_FILE packet"""    
    def __init__(self):
        self.format_str = '!255s'

    def pack(self,data):
        return struct.pack(self.format_str, data.path)
        
    def unpack(self,reader):
        path = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data()        
        data.path = self._short_string(path[0])
        data.type = packet_types.FS_DELETE_FILE
        
        return data

class BuildFSRenameFile(Packet):
    """Builds an FS_RENAME_FILE packet"""
    def __init__(self):
        self.format_str = '!255s255s'
    def pack(self, data):
        return struct.pack(self.format_str, data.src_path, data.dest_path)
    def unpack(self,reader):
        (src_path, dest_path) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'src_path':self._short_string(src_path), 'dest_path':self._short_string(dest_path)})
        data.type = packet_types.FS_RENAME_FILE
        return data
        
class BuildFSRenameDone(Packet):
    """Builds an FS_RENAME_FILE packet"""
    def __init__(self):
        self.format_str = '!255s255s'
    def pack(self, data):
        return struct.pack(self.format_str, data.src_path, data.dest_path)
    def unpack(self,reader):
        (src_path, dest_path) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'src_path':self._short_string(src_path), 'dest_path':self._short_string(dest_path)})
        data.type = packet_types.FS_RENAME_DONE
        return data

class BuildFSErrRename(Packet):
    """Builds an FS_ERR_RENAME packet"""
    def __init__(self):
        self.format_str = '!255s255s'
    def pack(self, data):
        return struct.pack(self.format_str, data.src_path, data.dest_path)
    def unpack(self,reader):
        (src_path, dest_path) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'src_path':self._short_string(src_path), 'dest_path':self._short_string(dest_path)})
        data.type = packet_types.FS_ERR_RENAME
        return data

class BuildFSDeleteBlock(Packet):
    """Builds an FS_DELETE_BLOCK packet"""
    def __init__(self):
        self.format_str = '!II'
    
    def pack(self,data):
        return struct.pack(self.format_str, data.oid, data.block_id)
        
    def unpack(self,reader):
        (oid,block_id) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data()        
        data.oid = oid
        data.block_id = block_id
        data.type = packet_types.FS_DELETE_BLOCK
        
        return data

class BuildFSDeleteDone(Packet):
    """Builds an FS_DELETE_DONE packet"""
    def __init__(self):
        self.format_str = '!I'
    def pack(self,data):
        return struct.pack(self.format_str, data.oid)
        
    def unpack(self,reader):
        oid = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data()        
        data.oid = oid
        data.type = packet_types.FS_DELETE_DONE
        
        return data

class BuildFSBlockDeleted(Packet):
    """Builds an FS_BLOCK_DELETED packet"""
    def __init__(self):
        self.format_str = '!II'
    def pack(self, data):
        return struct.pack(self.format_str, data.oid, data.block_id)
        
    def unpack(self,reader):
        (oid,block_id) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data()        
        data.oid = oid
        data.block_id = block_id
        data.type = packet_types.FS_BLOCK_DELETED
        
        return data
class BuildFSReplicateBlock(Packet):
    """Builds an FS_REPLICATE_BLOCK packet"""
    def __init__(self):
        self.format_str = '!IIII4sH'
    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.block_id), int(data.version), int(data.serverid), socket.inet_aton(data.ip), int(data.port))
        
    def unpack(self,reader):
        
        (oid,block_id, version,serverid,ip,port) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        ip = socket.inet_ntoa(ip)
        data = Data(params={'oid':oid,'block_id':block_id,'version':version,'serverid':serverid,'ip':ip,'port':port})
        data.type = packet_types.FS_REPLICATE_BLOCK
        return data

class BuildFSReplicateDone(Packet):
    """Builds an FS_REPLICATE_DONE packet"""
    def __init__(self):
        self.format_str = '!IIII4sH'
    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.block_id), int(data.version), int(data.serverid), socket.inet_aton(data.ip), int(data.port))
        
    def unpack(self,reader):
        
        (oid,block_id,version,serverid,ip,port) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        ip = socket.inet_ntoa(ip)
        data = Data(params={'oid':oid,'block_id':block_id, 'version':version,'serverid':serverid,'ip':ip,'port':ip})
        data.type = packet_types.FS_REPLICATE_DONE
        return data

class BuildFSStatFile(Packet):
    """Builds an FS_STAT_FILE packet"""
    def __init__(self):
        self.format_str = '!255s'
    def pack(self,data):
        return struct.pack(self.format_str, data.path)
        
    def unpack(self,reader):
        data = Data()        
        path = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data.path = self._short_string(path[0])
        data.type = packet_types.FS_STAT_FILE
        
        return data

class BuildFSFileINFO(Packet):
    """Builds an FS_FILE_INFO packet"""
    def __init__(self):
        self.format_str = '!IIIIIII255s'
        self.child_format_str = '!I'
        
    def pack(self,data):
        buf = struct.pack(self.format_str, int(data.oid), int(data.num_blocks), int(data.version), int(data.size), int(data.file_type), int(data.parent), int(data.block_size), data.path)
        
        if data.file_type == 0: #it's a folder
            children = data.children
            buf += struct.pack(self.child_format_str, len(children))
            
            for child in children:
                buf += struct.pack(self.format_str, int(child.oid), int(data.num_blocks), int(child.version), int(child.size), int(child.file_type), int(child.parent), int(child.block_size), child.path)
            
        return buf
        

    def unpack(self,reader):
        
        (oid,num_blocks,version,size,type,parent,block_size,path,) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        path = self._short_string(path)
        data = Data(params={'oid':oid,'num_blocks':num_blocks,'path':path,'version':version,'size':size,'file_type':type,'parent':parent,'block_size':block_size})

        if data.file_type == 0:
            (children_len,) = struct.unpack(self.child_format_str, reader.read(struct.calcsize(self.child_format_str)))
            
            childs = []
            for i in range(children_len):
                
                (oid,num_blocks,version,size,type,parent,block_size,path,) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
                path = self._short_string(path)
                child = Data(params={'oid':oid,'num_blocks':num_blocks,'path':path,'version':version,'size':size,'file_type':type,'parent':parent,'block_size':block_size})
                childs.append(child)

            data.children = childs
        
        data.type = packet_types.FS_FILE_INFO
        
        return data
class BuildChkVer(Packet):
    """Builds a CHK_VER packet"""
    def __init__(self):
        self.format_str = '!4sHI'
    def pack(self,data):    
        ip = socket.inet_aton(data.ip)
        port = int(data.port)
        sid = int(data.serverid)
        return struct.pack(self.format_str, ip, port, sid)
        
    def unpack(self,reader):
        data = Data()
        (ip, port, serverid) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        ip = socket.inet_ntoa(ip)
        
        data.ip = ip
        data.port = port
        data.serverid = "%s" % serverid
        data.type = packet_types.CHK_VER
                
        return data
class BuildCurrBlock(Packet):
    """Builds a CURR_BLOCK packet"""
    def __init__(self):
        self.format_str = '!IIII'
    
    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.block_id), int(data.version),int(data.serverid))
    
    def unpack(self,reader):
        (oid,block_id,version,serverid) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid,'block_id':block_id,'version':version,'serverid':serverid})
        data.type = packet_types.CURR_BLOCK

        return data

class BuildChkDone(Packet):
    """Builds a CHK_DONE  packet"""
    def __init__(self):
        self.format_str = '!4sHI'

    def pack(self,data):    
        ip = socket.inet_aton(data.ip)
        port = int(data.port)
        sid = int(data.serverid)
        return struct.pack(self.format_str, ip, port, sid)
        
    def unpack(self,reader):
        """Extracts data from an heartbeat packet"""
    
        (ip, port, serverid) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        ip = socket.inet_ntoa(ip)
        
        data = Data()
        data.ip = ip
        data.port = port
        data.serverid = "%s" % serverid
        data.type = packet_types.CHK_DONE
                
        return data
class BuildFSGetBlockReplicas(Packet):
    """Builds an FS_GET_BLOCK_REPLICAS packet"""
    def __init__(self):
        self.format_str = '!II'

    def pack(self,data):
        return struct.pack(self.format_str, data.oid, data.block_id)
        
    def unpack(self, reader):
        data = Data()
        (oid,block_id) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data.oid = oid
        data.block_id = block_id
        data.type = packet_types.FS_GET_BLOCK_REPLICAS
        return data

class BuildFSBlockReplicas(Packet):
    """Builds an FS_BLOCK_REPLICAS packet"""
    def __init__(self):
        self.format_str = '!III'
        self.child_format_str = '!II'
    
    def pack(self,data):
        buf = struct.pack(self.format_str, int(data.oid), int(data.block_id), len(data.replicas))
        
        for key in data.replicas:
            buf += struct.pack(self.child_format_str, int(key), int(data.replicas[key]))
            
        return buf
        
    def unpack(self, reader):
        (oid,block_id,length) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data()
        data.oid = oid
        data.block_id = block_id
        
        data.replicas = {}
        
        for i in range(length):
            (key,val) = struct.unpack(self.child_format_str, reader.read(struct.calcsize(self.child_format_str)))
            data.replicas[key] = val
        
        data.type = packet_types.FS_BLOCK_REPLICAS
        return data

class BuildFSGetOIDBlockInfo(Packet):
    def __init__(self):
        self.format_str = '!I'

    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid))
        
    def unpack(self,data):
        data = Data()
        (oid,) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data.oid = oid
        return data
      
class BuildFSOIDBlocks(Packet):
    """Builds an FS_OID_BLOCKS packet"""
    def __init__(self):
        self.format_str = '!III'
        self.child_format_str = '!II'
        
    def pack(self,data):
        buf = struct.pack(self.format_str, int(data.oid), int(data.version), len(data.blocks))
        
        for key in data.blocks:
            buf += struct.pack(self.child_format_str, int(key), int(data.replicas[key]))
            
        return buf
        
    def unpack(self, reader):
        (oid,version,length) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data()
        data.oid = oid
        data.version = version
        
        data.blocks = {}
        
        for i in range(length):
            (key,val) = struct.unpack(self.child_format_str, reader.read(struct.calcsize(self.child_format_str)))
            data.blocks[key] = val
        
        data.type = packet_types.FS_OID_BLOCKS
        return data

class BuildFSNodeCreated(Packet):
    """Builds an FS_NODE_CREATED packet"""
    def __init__(self):
        self.format_str = '!III'
    
    def pack(self,data):
        return struct.pack(self.format_str, int(data.oid), int(data.length), int(data.version))

    def unpack(self, reader):
        (oid,length,version) = struct.unpack(self.format_str, reader.read(struct.calcsize(self.format_str)))
        data = Data(params={'oid':oid,'length':length,'version':version})
        data.type = packet_types.FS_NODE_CREATED
        return data

def initialize(app):
    app.registerPacket(packet_types.ANNOUNCE,AnnounceBuilder())
    app.registerPacket(packet_types.ACK,AckBuilder())
    app.registerPacket(packet_types.HEARTBEAT,HeartbeatBuilder())
    app.registerPacket(packet_types.FS_CREATE,FSCreateBuilder())
    app.registerPacket(packet_types.FS_ERR_CREATE,FSErrCreate())
    app.registerPacket(packet_types.FS_ERR_NODATASERVERS,FSErrNoDataServers())
    app.registerPacket(packet_types.FS_ERR_DATASERVER_FAILED,FSErrDataserverFailed())
    app.registerPacket(packet_types.FS_CREATE_OK,FSCreateFileOK())
    app.registerPacket(packet_types.FS_STORE_BLOCK,BuildFSStoreBlock())
    app.registerPacket(packet_types.FS_BEGIN_WRITE,BuildFSBeginWrite())
    app.registerPacket(packet_types.FS_WRITE_READY,BuildFSWriteReady())
    app.registerPacket(packet_types.FS_END_WRITE,BuildFSEndWrite())
    app.registerPacket(packet_types.FS_STORE_OK,BuildFSStoreOK())
    app.registerPacket(packet_types.FS_BLOCK_STORED,BuildFSBlockStored())
    app.registerPacket(packet_types.FS_GET,BuildFSGet())
    app.registerPacket(packet_types.FS_GET_OK,FSGetOK())
    app.registerPacket(packet_types.FS_REQUEST_BLOCK,BuildFSRequestBlock())
    app.registerPacket(packet_types.FS_REQUEST_OK,BuildFSRequestOK())
    app.registerPacket(packet_types.FS_ERR_PATH_NOT_FOUND,BuildFSErrPathNotFound())
    app.registerPacket(packet_types.FS_ERR_NO_REPLICAS,BuildFSErrNoReplicas())
    app.registerPacket(packet_types.FS_ERR_BLOCK_NOT_FOUND,BuildFSErrBlockNotFound())
    app.registerPacket(packet_types.FS_ERR_INCORRECT_VERSION,BuildFSErrIncorrectVersion())
    app.registerPacket(packet_types.FS_WRITE_FILE,BuildFSWriteFile())
    app.registerPacket(packet_types.FS_WRITE_OK,BuildFSWriteOK())
    app.registerPacket(packet_types.FS_MODIFY_BLOCK,BuildFSModifyBlock())
    app.registerPacket(packet_types.FS_MODIFY_OK,BuildFSModifyOK())
    app.registerPacket(packet_types.FS_MODIFY_DONE,BuildFSModifyDone())
    app.registerPacket(packet_types.FS_MODIFY_ACK,BuildFSModifyAck())
    app.registerPacket(packet_types.FS_GET_LOCK,BuildFSGetLock())
    app.registerPacket(packet_types.FS_LOCK_OK,BuildFSLockOK())
    app.registerPacket(packet_types.FS_VERSION_UPDATED, BuildFSVersionUpdated())
    app.registerPacket(packet_types.FS_ERR_BUFFER_OUT_OF_RANGE,BuildFSBufferOutOfRange())
    app.registerPacket(packet_types.FS_WRITE_ERROR,BuildFSWriteError())
    app.registerPacket(packet_types.FS_ERR_LOCK_DENIED,BuildFSErrLockDenied())
    app.registerPacket(packet_types.FS_DELETE_FILE,BuildFSDeleteFile())
    app.registerPacket(packet_types.FS_DELETE_BLOCK,BuildFSDeleteBlock())
    app.registerPacket(packet_types.FS_DELETE_DONE,BuildFSDeleteDone())
    app.registerPacket(packet_types.FS_REPLICATE_BLOCK,BuildFSReplicateBlock())
    app.registerPacket(packet_types.FS_REPLICATE_DONE,BuildFSReplicateDone())
    app.registerPacket(packet_types.FS_STAT_FILE,BuildFSStatFile())
    app.registerPacket(packet_types.FS_FILE_INFO,BuildFSFileINFO())
    app.registerPacket(packet_types.CHK_VER,BuildChkVer())
    app.registerPacket(packet_types.CURR_BLOCK,BuildCurrBlock())
    app.registerPacket(packet_types.CHK_DONE,BuildChkDone())
    app.registerPacket(packet_types.FS_GET_BLOCK_REPLICAS,BuildFSGetBlockReplicas())
    app.registerPacket(packet_types.FS_BLOCK_REPLICAS,BuildFSBlockReplicas())
    app.registerPacket(packet_types.FS_GET_OID_BLOCK_INFO,BuildFSGetOIDBlockInfo())
    app.registerPacket(packet_types.FS_OID_BLOCKS,BuildFSOIDBlocks())
    app.registerPacket(packet_types.FS_NODE_CREATED,BuildFSNodeCreated())
    app.registerPacket(packet_types.FS_RENAME_FILE, BuildFSRenameFile())
    app.registerPacket(packet_types.FS_RENAME_DONE, BuildFSRenameDone())
    app.registerPacket(packet_types.FS_ERR_RENAME,BuildFSErrRename())
