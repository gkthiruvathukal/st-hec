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


from buzhug import Base
from fs_db import FileSystemError
import os, threading, sys
from fs_objects import *
from cPickle import *

class DB:
    def __init__(self, storage_path):
                        
        self.dbh_objects = Base(os.path.join(storage_path, 'objects'))
        self.dbh_blocks = Base(os.path.join(storage_path, 'blocks'))
        self.dbh_replicas = Base(os.path.join(storage_path, 'replicas'))
        self.dbh_tree = Base(os.path.join(storage_path, 'tree'))
        self.dbh_paths = Base(os.path.join(storage_path, 'paths'))
        self.dbh_id = Base(os.path.join(storage_path, 'id'))
        self.dbh_tags = Base(os.path.join(storage_path, 'tags'))
        self.storage_path = storage_path        
    
    def __create_root(self):
        """ Check if the filesystem has a / and if not create it"""
        
        print "Initializing filesystem..."

        if self.get_file(path='/'):
           return
                
        print "Creating root..."
        
        f = FSObject(1,1,'/',0,0,0,0)
        
        # lets see if we already have a key stored
        set = self.dbh_objects.select(['oid'],oid=str(f.oid))
        if set == []:
            # we have create tree and paths first
            self.dbh_tree.insert(str(f.oid), str(f.parent))
            self.dbh_paths.insert(str((f.parent, f.path)))
            
            self.dbh_objects.insert(str(f.oid), dumps(f), self.dbh_tree[len(self.dbh_tree)-1], self.dbh_paths[len(self.dbh_paths)-1])    
        
        
        #set the current oid for the id increment sequence
        set = self.dbh_id.select(['curr_oid'])
        if set == []:
            self.dbh_id.insert('1')
         
        
    def setup_fs_db(self):                
                
        try:
            self.dbh_blocks.create(('key', str), ('blocks', str))
        except IOError:    
            self.dbh_blocks.open()
        
        try:
            self.dbh_replicas.create(('key', str), ('replicas', str))
        except IOError:    
            self.dbh_replicas.open()
        
        try:
            self.dbh_tree.create(('oid', str), ('parent', str))
        except IOError:    
            self.dbh_tree.open()
        
        try:
            self.dbh_tags.create(('oid', str), ('tag', str))
        except IOError:    
            self.dbh_tags.open()
            
        try:
            self.dbh_paths.create(('key', str))
        except IOError:    
            self.dbh_paths.open()
        
        try:
            self.dbh_id.create(('curr_oid', str))
        except IOError:    
            self.dbh_id.open()
                
        try:
            self.dbh_objects.create(('oid', str), ('fsobj', str), ('tree', self.dbh_tree), ('paths', self.dbh_paths))
        except IOError:    
            self.dbh_objects.open()
        
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
                      
            # search for a match
            f = None
            for record in [record for record in self.dbh_objects]:
                if record.paths.key == key:
                    f = loads(record.fsobj)
                    break
            
            print "found it!"      
            if not f:
                return 0
                                    
            parent_oid = f.oid
                
        return parent_oid
        
    
    def insert_file(self, path, fsobj):
        #check first if there is a parent directory to store this file        
        
        f = self.get_file(path=path)
        
        print "inserting file with path: "+path
        print fsobj
        
        if not f:
            print "ERR: [%s]" % os.path.split(fsobj.path)[0]
            raise FileSystemError('No parent directory to store: %s' % fsobj.path)
        
        #the parent of this object is the path
        fsobj.parent = f.oid
            
        set = self.dbh_id.select_for_update(['curr_oid'])        
        
        curr_oid = int(set[0].curr_oid) + 1                
        fsobj.oid = curr_oid
        print "Inserting OID: %s" % fsobj        
            
        # lets see if we already have a key stored
        result = self.dbh_objects.select(['oid','fsobj'],oid=str(fsobj.oid))
        if result != []:
            raise FileSystemError('File already exists')
        else:
            
            # we have create tree and paths first         
            self.dbh_tree.insert(str(fsobj.oid), str(fsobj.parent))
            self.dbh_paths.insert(str((fsobj.parent, fsobj.path)))
            
            self.dbh_objects.insert(str(fsobj.oid), dumps(fsobj), self.dbh_tree[len(self.dbh_tree)-1], self.dbh_paths[len(self.dbh_paths)-1])
            
            set[0].update(curr_oid=str(curr_oid))
                    

        return curr_oid
    
    def get_file(self, oid='', path=''):
        if oid:            
            set = self.dbh_objects.select(['oid', 'fsobj'], oid=str(oid))
            if set == []:
                f = None
            else:
                f = set[0].fsobj
            
        elif path:
            if path == '/':
                key = str((0,'/'))
            else:
                parent_oid = self.get_path_oid(os.path.split(path)[0])
                node_name = os.path.split(path)[1]
                key = str((parent_oid, node_name))
            
            # search for a match
            f = None                      
            for record in [record for record in self.dbh_objects]:
                print record.paths.key
                if record.paths.key == key:
                    f = record.fsobj
                    break
            
        else:
            f = None

        if f:
            f = loads(f)
                    
        return f
            
    def get_children(self, oid):            
        
        # lookup FSOBJECT with given oid
        set = self.dbh_objects.select(['oid', 'fsobj'], oid=str(oid))
        if set == []:
            return []
        
        file_array = []                
                        
        # lookup objects with parent oid
        set = self.dbh_tree.select(['oid', 'parent'], parent=str(oid))        
        for i in set:
            obj = self.dbh_objects.select(['oid', 'fsobj'], oid=str(i.oid))            
            if obj != []:                
                file_array.append(loads(obj[0].fsobj))
        
                            
        return file_array
                        

    def debug_print_db(self, db):
        pass
        
    def print_object_db(self):
        self.debug_print_db(self.dbh_objects)
        
    def delete_dir(self,oid):
        pass
                              
    def delete_file(self, oid):
        pass
        
    def rename_file(self,src,dest):
        pass     
        
    def update_file(self, fsobj):
        
        set = self.dbh_objects.select_for_update(['oid', 'fsobj'], oid=str(fsobj.oid))
        if set != []:
            set[0].update(fsobj=dumps(fsobj))                
        
    
    def add_block(self, block, serverid):
    
        f = self.get_file(oid=str(block.oid))
        if not f:
            raise FileSystemError('add_block: Object %s does not exist' % block.oid)
        
        key = str((long(block.oid),long(block.block_id))) #the key is both the oid and the block_id
        
        set1 = self.dbh_replicas.select_for_update(['key', 'replicas'], key=key)
        if set1 == []:            
            replicas = FSReplicas(block.oid, block.block_id)
        else:
            replicas = loads(set1[0].replicas)
        
        f.blocks[block.block_id] = block.version
        
        set2 = self.dbh_blocks.select_for_update(['key', 'blocks'], key=key)
        if set2 == []:
            b = None
        else:
            b = set2[0].block
        
        if b:
            b = loads(b)
            diff = block.size - b.size
        else:
            diff = block.size
        
        f.size += diff
                
        # update or insert?
        if set1 == []:
            self.dbh_blocks.insert(key, dumps(block))
        else:
            set1[0].update(blocks=dumps(block))
        
        self.update_file(f)
        replicas.add(serverid, block.version)
        
        # update or insert?
        if set2 == []:
            self.dbh_replicas.insert(key,dumps(replicas))
        else:
            set2[0].update(replicas=dumps(replicas))


    def add_block_replica(self, block, serverid):
        f = self.get_file(str(block.oid))
        
        if not f:
            raise FileSystemError('add_block_replica: Object %s does not exist' % block.oid)
            
        key = str((block.oid, block.block_id))                
        
        set = self.dbh_replicas.select_for_update(['key', 'replicas'], key=key)
        if set == []:        
            replicas = FSReplicas(block.oid, block.block_id)
        else:
            replicas = loads(set[0].replicas)
        
        replicas.add(serverid, block.version)
        
        # update or insert?
        if set == []:
            self.dbh_replicas.insert(key,dumps(replicas))
        else:
            set[0].update(replicas=dumps(replicas))

        
    def get_block_replicas(self, oid, block_id):
        key = str((long(oid), long(block_id)))
        
        set = self.dbh_replicas.select(['key', 'replicas'], key=key)
        if set == []:
            return None
        
        return loads(set[0].replicas)

      
    def get_block(self, oid, block_id):
        key = str((long(oid), long(block_id)))
        
        set = self.dbh_blocks.select(['key', 'blocks'], key=key)
        if set == []:
            return None
        
        return loads(set[0].blocks)        
        
    def print_replicas_db(self):
        self.debug_print_db(self.dbh_replicas)
        
    def close_fs_db(self):
        self.dbh_blocks.close()
        self.dbh_replicas.close()
        self.dbh_tree.close()
        self.dbh_id.close()
        self.dbh_paths.close()
        self.dbh_objects.close()
        
    

if __name__ == '__main__':
    d = DB('C:\support\hydrafs\db1\c1_rep_db.db')
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
