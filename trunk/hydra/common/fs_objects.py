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


class FSObject:
    def __init__(self, oid, version, path, size, type, parent, block_size):
        self.oid  = oid
        self.path = path
        self.version = version
        self.size = size
        self.type = type #1 = file, 0 = folder
        self.parent = parent
        self.block_size = block_size
        self.blocks = {}
    
    def set_block(self, block):
        self.blocks[block.block_id] = block
        
    def unset_block(self, block_id):
        if self.blocks.has_key(block_id):
            del self.blocks[block_id]
        
    def __str__(self):
        return "oid=%s | path=%s | version=%s | size=%s | type=%s | parent=%s | block_size=%s | blocks=%s" % (self.oid, self.path, self.version, self.size, self.type, self.parent, self.block_size, self.blocks)

class FSBlock:
    def __init__(self, oid, block_id, version, offset, size):
        self.oid = oid
        self.block_id = block_id
        self.version = version
        self.offset = offset
        self.size = size
        
    def __str__(self):
        return "oid=%s | block_id=%s | version=%s | offset=%s | size=%s" % (self.oid, self.block_id, self.version, self.offset, self.size)
        
class FSReplicas:
    def __init__(self, oid, block_id):
        self.oid = oid
        self.block_id = block_id
        self.replicas = {}
    
    def add(self, serverid, version):
        self.replicas[serverid] = version
        
        
    def __str__(self):
        return "oid=%s | block_id=%s | %s" % (self.oid, self.block_id, self.replicas)
