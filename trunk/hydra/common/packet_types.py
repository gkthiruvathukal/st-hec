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


import types

#-------- Client announces & heartbeats
ACK = 0x0000        # Usual server response to acknowledge a request
ANNOUNCE = 0x0001   # Client announces itself to server
HEARTBEAT = 0x0002  # Client tells server it's alive

#---------- Version checking
CHK_VER = 0x0100            # Client tells metadata server it wants to check versions
CURR_BLOCK = 0x0101          # Client's current filelist
CHK_DONE = 0x102            # Client is done sending the current file list

#SYNC_REPLY                  # Server's reply with actions to take

#-------- File Operations
FS_CREATE = 0x200           # Client tells metadata server it wants to create a file
FS_CREATE_OK = 0x201        # Metadata server tells client it's ok to create the file, and gives it an address to create it
FS_STORE_BLOCK = 0x202       # Client tells dataserver to store this file
FS_STORE_OK = 0x204         # Data server tells the client is ok to store the file
FS_BLOCK_STORED = 0x205      # Data server tells the cmetadataserver the file has been stored
FS_BEGIN_WRITE = 0x206        #Client tells dataserver it's going to write to a file
FS_WRITE_READY = 0x207      # Data server tells client it's ready to receive blocks
FS_END_WRITE = 0x208        # Client tells dataserver it's done sending blocks
FS_FILE_STORED = 0x209      # Data server tells the client the file has been stored
FS_NODE_CREATED = 0x210 # Metadata server tells the client it has created a new node

FS_ERR_CREATE = 0x2F0       # Metadata server tells client that file already exists
FS_ERR_NODATASERVERS = 0x2F1 #Metadata server tells client there are currently no servers to replicate this file to
FS_ERR_STORE = 0x2F2        # Dataserver tells client there was an error storing the file
FS_ERR_DATASERVER_FAILED = 0x2F3 #Client tells Metadata server that the given dataserver failed to store the file

FS_GET = 0x216              # Client tells metadata server it wants to read a file
FS_GET_OK = 0x217           # Metadata server tells client where to get the object from
FS_REQUEST_BLOCK = 0x218      # Client tells dataserver it wants this oid
FS_REQUEST_OK = 0x219       # Dataserver tells client it has the oid and is about to send it

FS_ERR_PATH_NOT_FOUND = 0x2F4      # Metadata server tells client there's no such file
FS_ERR_NO_REPLICAS = 0x2F5         # Metadata server tells client there are currently no replicas of this file online
FS_ERR_BLOCK_NOT_FOUND = 0x2F6       # Dataserver tells client there's no such oid
FS_ERR_INCORRECT_VERSION = 0x2F7   # Server tells client it has a different version

FS_WRITE_FILE = 0x22A       # Client tells metadata server it wants to modify a file
FS_WRITE_OK = 0x22B         # Metadata server tells client it's ok to write the file, and where to write it to
FS_MODIFY_BLOCK = 0x22C       # Client tells data server it wants to  write to a block
FS_MODIFY_OK = 0x22D        # Dataserver tells client to go ahead and send buffer to write to block
FS_MODIFY_DONE = 0x22E      # Dataserver tells metadata server/client it succesfully modified the file
FS_MODIFY_ACK = 0x22F       # Metadata server acknowledges the modify and provides a new version number
FS_GET_LOCK = 0x230         # Dataserver asks for an extension of the file lock
FS_LOCK_OK = 0x231          # Metadata server grants the lock
FS_VERSION_UPDATED = 0x240 #Data server informs metadata that it's version has been updated
FS_ERR_BUFFER_OUT_OF_RANGE = 0x2F8  # Metadata/data server tell client the seek position is out of range
FS_WRITE_ERROR = 0x2F9               # Data server tells client that it had problems writing to file
FS_ERR_LOCK_DENIED = 0x2FA          # Metadata server denies the lock

FS_DELETE_FILE = 0x242      # Client tells the Metadata server it wants to delete a file
FS_DELETE_BLOCK = 0x245       # Metadata server tells data server to delete this block
FS_DELETE_DONE = 0x244      # Metadata server tells client the file has been deleted
FS_RENAME_FILE = 0x247 # Client tells Metadata server to rename a file
FS_RENAME_DONE = 0x248 #Metadata tells server that the rename was successful
FS_ERR_RENAME = 0x249 #Metadata tells client that an error ocurred and the file could not be renamed

FS_REPLICATE_BLOCK = 0x300    # Metadata server tells data server to get a copy of this block
FS_REPLICATE_DONE = 0x301   # Data server tells metadata server the file has been replicated

FS_STAT_FILE = 0x250        # Client tells metadata server it wants info on a file or directory
FS_FILE_INFO = 0x251        # Metadata server sends info on the file to client

FS_GET_BLOCK_REPLICAS = 0x260     # Client wants to know which servers have which replicas of a file
FS_BLOCK_REPLICAS = 0x261     # Metadata server sends info to the client about it
FS_GET_OID_BLOCK_INFO = 0x262 # Client wants to know which blocks compose oid
FS_OID_BLOCKS = 0x263       # Metadata server sends block list to client

#packet_types maps packet codes to their actual names
local_vars = locals().copy()
reverse_map = dict([(local_vars[x],x) for x in local_vars if type(local_vars[x]) == types.IntType])

if __name__ == '__main__':
    print reverse_map
