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



import os, threading, sys
from fs_objects import *
from cPickle import *

class FileSystemError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return self.value     

class DB:
    def __init__(self, storage_path, module):
        
        # import module        
        import_string = "from "+ os.path.splitext(module)[0] + " import DB as DBParent"
        exec import_string
        
        self.parent = DBParent(storage_path)
    
    def setup_fs_db(self):
        self.parent.setup_fs_db()
    
    def get_path_oid(self, path):
        return self.parent.get_path_oid(path)
            
    def insert_file(self, path, fsobj):
        return self.parent.insert_file(path, fsobj)
    
    def get_file(self, oid='', path=''):
        return self.parent.get_file(oid, path)
            
    def get_children(self, oid):
        return self.parent.get_children(oid)

    def debug_print_db(self, db):
        self.parent.debug_print(db)
        
    def print_object_db(self):
        self.parent.print_object_db()
        
    def delete_dir(self,oid):
        self.parent.delete_dir(oid)
                              
    def delete_file(self, oid):
        self.parent.delete_file(oid)
        
    def rename_file(self,src,dest):
        self.parent.rename_file(src,dest)
        
    def update_file(self, fsobj):
        self.parent.update_file(fsobj)
    
    def add_block(self, block, serverid):    
        self.parent.add_block(block,serverid)

    def add_block_replica(self, block, serverid):
        self.parent.add_block_replica(block,serverid)
        
    def get_block_replicas(self, oid, block_id):
        return self.parent.get_block_replicas(oid, block_id)
        
    def get_file_replicas(self, oid):
        """Returns a list with all the blocks of a file and their current replicas"""
        f = self.parent.get_file(oid=oid)
        if not f:
            return []
        
        block_list = {}
        for block_id in f.blocks.keys():
            
            curr_block_replicas = self.parent.get_block_replicas(oid, block_id)
            block_list[block_id] = curr_block_replicas
                
        return block_list
    
    def get_blocks(self, oid, byte_start=0, byte_end=0):
        
        f = self.parent.get_file(oid=oid)
        
        if f.size < byte_end:
            raise FileSystemError('get_blocks: Requested range does not exist: %s [%s:%s]' % (f, byte_start, byte_end))
        if byte_end == 0:
            byte_end = f.size

        block_list = {}
        for block_id in f.blocks.keys():
            b = self.parent.get_block(oid, block_id)
            
            if (not byte_start or byte_start <= b.offset+b.size-1) and (not byte_end or byte_end >= b.offset):
                block_list[b.block_id] = b
            
        return block_list
    
    def get_block(self, oid, block_id):
        return self.parent.get_block(oid, block_id)
    
    def print_replicas_db(self):
        self.parent.print_replicas_db()
        
    def close_fs_db(self):
        self.parent.close_fs_db()            
