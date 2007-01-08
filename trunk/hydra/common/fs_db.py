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



from bsddb3 import db as bsdDB
import os, threading
from fs_objects import *
from pickle import *

class FileSystemError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return self.value    


def getOID(key, val):
    file = loads(val)
    return str(file.parent)
    
def getPath(key, val):
    file = loads(val)
    key = str((file.parent, file.path))
    return key
    
class DB:
    def __init__(self, storage_path):
        self.dbh_objects = bsdDB.DB() #objects table
        self.dbh_blocks = bsdDB.DB() # blocks table
        self.dbh_replicas = bsdDB.DB() #replicas table
        self.dbh_tree = bsdDB.DB() #tree index
        self.dbh_paths = bsdDB.DB() #path index
        self.dbh_id = bsdDB.DB() #current id
        self.storage_path = storage_path
        
    def __create_root(self):
        """ Check if the filesystem has a / and if not create it"""
        
        print "Initializing filesystem..."

        if self.get_file(path='/'):
           return
          
        f = FSObject(1,1,'/',0,0,0,0)
        self.dbh_objects.put(str(f.oid), dumps(f),flags=bsdDB.DB_NOOVERWRITE)
        
        #set the current oid for the id increment sequence
        if self.dbh_id.get('curr_oid') == None:
            self.dbh_id.put('curr_oid','1')
        
    def setup_fs_db(self):
        self.dbh_objects.open(filename=os.path.join(self.storage_path,'fsobjects.db'),dbname='fsobjects',dbtype=bsdDB.DB_BTREE,flags=bsdDB.DB_CREATE,mode=0666)

        self.dbh_blocks.open(filename=os.path.join(self.storage_path,'fsblocks.db'),dbname='fsblocks',dbtype=bsdDB.DB_BTREE,flags=bsdDB.DB_CREATE,mode=0666)

        self.dbh_replicas.open(filename=os.path.join(self.storage_path,'fsreplicas.db'),dbname='fsreplicas',dbtype=bsdDB.DB_BTREE,flags=bsdDB.DB_CREATE,mode=0666)
        
        self.dbh_tree.set_flags(bsdDB.DB_DUPSORT)
        self.dbh_tree.open(filename=os.path.join(self.storage_path,'fstree.db'),dbname='fstree',dbtype=bsdDB.DB_BTREE,flags=bsdDB.DB_CREATE,mode=0666)
        self.dbh_objects.associate(self.dbh_tree, getOID,flags=bsdDB.DB_CREATE)
        
        self.dbh_paths.open(filename=os.path.join(self.storage_path,'fspaths.db'),dbname='fspaths',dbtype=bsdDB.DB_BTREE,flags=bsdDB.DB_CREATE,mode=0666)
        self.dbh_objects.associate(self.dbh_paths, getPath)
        
        self.dbh_id.open(filename=os.path.join(self.storage_path,'fsid.db'), dbname='fsid',dbtype=bsdDB.DB_BTREE,flags=bsdDB.DB_CREATE,mode=0666)
        
        self.__create_root()
    
    def get_path_oid(self, path):
        """Gets the parent filenode for path"""
        
        nodes = []
        parent_path = path
        while 1:
            (parent_path,node) = os.path.split(parent_path)
            if node == '':
                nodes.insert(0,'/')
                break
            nodes.insert(0,node)
   
        parent_oid = 0
        for node_name in nodes:
            key = str((parent_oid, node_name))
            print "looking up: %s" % key
            f = self.dbh_paths.get(key)
            print "found it!"
            if not f:
                return 0
            f = loads(f)
            parent_oid = f.oid
        
        return parent_oid
        
    
    def insert_file(self, path, fsobj):
        #check first if there is a parent directory to store this file
        
        f = self.get_file(path=path)
        
        if not f:
            print "ERR: [%s]" % os.path.split(fsobj.path)[0]
            raise FileSystemError('No parent directory to store: %s' % fsobj.path)
        
        #the parent of this object is the path
        fsobj.parent = f.oid
    
        curr_oid = int(self.dbh_id.get('curr_oid'))
        curr_oid += 1
        fsobj.oid = curr_oid
        print "Inserting OID: %s" % fsobj
        try:
            self.dbh_objects.put(str(fsobj.oid), dumps(fsobj),flags=bsdDB.DB_NOOVERWRITE)
            self.dbh_id.put('curr_oid', str(curr_oid))
        except bsdDB.DBInvalidArgError, e:
            raise FileSystemError('File already exists')
        

        return curr_oid
    
    def get_file(self, oid='', path=''):
        if oid:
            f = self.dbh_objects.get(str(oid))
        elif path:
            if path == '/':
                key = str((0,'/'))
            else:
                parent_oid = self.get_path_oid(os.path.split(path)[0])
                node_name = os.path.split(path)[1]
                key = str((parent_oid, node_name))
            f = self.dbh_paths.get(key)
        else:
            f = None

        if f:
            f = loads(f)
        return f
            
    def get_children(self, oid):
        file_array = []
    
        cursor = self.dbh_tree.cursor()
        
        row = cursor.get(str(oid),flags=bsdDB.DB_SET)
        
        if row == None:
            return []

        (key,data) = row
        file_array.append(loads(data))
            
        while 1:
            row = cursor.get(str(oid),flags=bsdDB.DB_NEXT_DUP)    
            if row == None:
                break
            (key,data) = row
            file_array.append(loads(data))
        
        cursor.close()
        return file_array

    def debug_print_db(self, db):
        cursor = db.cursor()
        
        row =  cursor.get('1',flags=bsdDB.DB_FIRST)
        
        if row == None:
            return
        
        (key,data) = row
        print loads(data)
        
        while 1:
            row = cursor.get('1',flags=bsdDB.DB_NEXT)
            if row == None:
                break
            (key,data) = row
            print loads(data)
    
        cursor.close()
        
    def print_object_db(self):
        self.debug_print_db(self.dbh_objects)
        
    def delete_dir(self,oid):
        oid = str(oid)
        f = self.get_file(oid)
        
        if not f or f.type != 0:
            return

        for child in self.get_children(f.oid):
            if child.type == 1:
                self.delete_file(child.oid)
            else:
                self.delete_dir(child.oid)
                self.dbh_objects.delete(str(child.oid))
        
    def delete_file(self, oid):
        oid = str(oid)
        f = self.get_file(oid)
        if not f:
            return
        
        if f.type == 0:
            self.delete_dir(oid)
            self.dbh_objects.delete(oid)
        else:
            print "deleting %s from db_objects" % oid
            self.dbh_objects.delete(oid)
            
            for block_id in f.blocks.keys():
                self.dbh_replicas.delete(oid,block_id)
            
    def rename_file(self,src,dest):
        file_src = self.get_file(path=src)
        file_dest = self.get_file(path=dest)
        
        if not file_src:
            raise FileSystemError('rename_file: File does not exist %s' % src)
        
        if file_dest:
            #if dest is a folder raise an error
            if file_dest.type == 0:
                raise FileSystemError('rename_file: Cannot overwrite folder %s' % dest)
            
            #move the file to the new location/name
            file_dest.parent = file_src.parent
            file_dest.path = file_src.path
            #delete the destination file
            self.delete_file(file_dest.oid)
        else:
            #check if the parent path actually exists
            (path, file_name) = os.path.split(dest)
            if not file_name:
                raise FileSystemError('rename_file: Invalid filename %s' % file_name)
            
            parent_oid = self.get_path_oid(path)
            
            #set the new destination folder/name
            file_src.parent = parent_oid
            file_src.path = file_name
        
        self.update_file(file_src)
        
        
    def update_file(self, fsobj):
        self.dbh_objects.put(str(fsobj.oid), dumps(fsobj))
    
    def add_block(self, block, serverid):
    
        f = self.get_file(oid=str(block.oid))
        if not f:
            raise FileSystemError('add_block: Object %s does not exist' % block.oid)
        
        key = str((long(block.oid),long(block.block_id))) #the key is both the oid and the block_id
        
        replicas = self.dbh_replicas.get(key)
        
        if replicas == None:
            replicas = FSReplicas(block.oid, block.block_id)
        else:
            replicas = loads(replicas)
        
        f.blocks[block.block_id] = block.version
        b = self.dbh_blocks.get(key)
        if b:
            b = loads(b)
            diff = block.size - b.size
        else:
            diff = block.size
        
        f.size += diff
        
        self.dbh_blocks.put(key, dumps(block))
        self.update_file(f)
        replicas.add(serverid, block.version)
        self.dbh_replicas.put(key,dumps(replicas))

    def add_block_replica(self, block, serverid):
        f = self.get_file(str(block.oid))
        
        if not f:
            raise FileSystemError('add_block_replica: Object %s does not exist' % block.oid)
            
        key = str((block.oid, block.block_id))
        
        replicas = self.dbh_replicas.get(key)
        
        if replicas == None:
            replicas = FSReplicas(block.oid, block.block_id)
        else:
            replicas = loads(replicas)
        
        replicas.add(serverid, block.version)
        self.dbh_replicas.put(key,dumps(replicas))
        

        
    def get_block_replicas(self, oid, block_id):
        key = str((long(oid), long(block_id)))
        r = self.dbh_replicas.get(key)

        if r:
            r = loads(r)
        
        return r
        
    def get_file_replicas(self, oid):
        """Returns a list with all the blocks of a file and their current replicas"""
        f = self.get_file(oid=oid)
        if not f:
            return []
        
        block_list = {}
        for block_id in f.blocks.keys():
            curr_block_replicas = self.get_block_replicas(oid, block_id)
            block_list[block_id] = curr_block_replicas
        
        return block_list
    
    def get_blocks(self, oid, byte_start=0, byte_end=0):
        
        f = self.get_file(oid=oid)
        
        if f.size < byte_end:
            raise FileSystemError('get_blocks: Requested range does not exist: %s [%s:%s]' % (f, byte_start, byte_end))
        if byte_end == 0:
            byte_end = f.size

        block_list = {}
        for block_id in f.blocks.keys():
            b = self.get_block(oid, block_id)
            
            if (not byte_start or byte_start <= b.offset+b.size-1) and (not byte_end or byte_end >= b.offset):
                block_list[b.block_id] = b
        return block_list
            
    def get_block(self, oid, block_id):
        key = str((long(oid), long(block_id)))
        block = self.dbh_blocks.get(key)
        if block:
            return loads(block)
        else:
            return None
        
    def print_replicas_db(self):
        self.debug_print_db(self.dbh_replicas)
        
    def close_fs_db(self):
        self.dbh_blocks = bsdDB.DB() # blocks table
        self.dbh_replicas.close()
        self.dbh_tree.close()
        self.dbh_id.close()
        self.dbh_paths = bsdDB.DB() #path index
        self.dbh_objects.close()
        
    

if __name__ == '__main__':
    d = DB()
    d.setup_fs_db()
    print "-----"
    print d.get_path_oid('/home/lurker/a.txt')
    print d.get_path_oid('/home/a.txt')
    print d.get_path_oid('/home')
    print d.get_path_oid('/')
    print "-----"
    
    oid = 0
    version = 1
    path = '/'
    replicas = 0
    
    size = 0
    type = 0
    parent = 0
    
    path = 'usr'
   
    f = FSObject(oid,version,path,replicas,size,type,parent)
    d.insert_file('/',f)

    path = 'lib'
    f = FSObject(oid,version,path,replicas,size,type,parent)
    d.insert_file('/usr',f)
    
    path = 'src'

    f = FSObject(oid,version,path,replicas,size,type,parent)
    d.insert_file('/usr',f)
    
    block = FSBlock(f.oid, 1, 1, 0, 1024)
    d.add_block(block,'server1')
    block = FSBlock(f.oid, 2, 1, 1024, 1024)
    d.add_block(block,'server1')
    
    print "adding a.h"
    path = 'a.h'
    f = FSObject(oid,version,path,replicas,size,type,parent)
    d.insert_file('/usr/src',f)
    
    block = FSBlock(f.oid, 1, 1, 0, 1024)
    d.add_block(block,'server1')
    block = FSBlock(f.oid, 2, 1, 1024, 1024)
    d.add_block(block,'server1')
    
    print "File: %s" % d.get_file(path='/usr/src')
    print "File: %s" % d.get_file(4)
    
    f = d.get_file(4)
    f.version = 2
    d.update_file(f)
    
    for file in d.get_children(2):
        print "Child: %s" % file
        
    d.print_object_db()
    
    f = d.get_file(path='/usr/src')
    for block_id in f.blocks:
        print block_id
        print d.get_block_replicas(f.oid, block_id)
    
    f = d.get_file(path='/usr/src/a.h')
    for block_id in f.blocks:
        print d.get_block_replicas(f.oid, block_id)
    for block in d.get_blocks(f.oid, byte_start=1, byte_end=2048):
        print d.get_block(f.oid, block)

    d.rename_file('/usr/src/a.h', '/usr/lib/a.h')
    d.rename_file('/usr/lib', '/lib2')
    d.print_object_db()
    d.close_fs_db()
