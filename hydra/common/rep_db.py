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



"""
This is the database each data server uses to keep track of the blocks & versions it's
storing in local disk.
Key: (oid,block_id)
Data: version
"""


from bsddb3 import db as bsdDB
import os
from fs_objects import *
from pickle import *

class RepDBError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return self.value
        
class RepDBIterator:
    def __init__(self, cursor):
        self.cursor = cursor
        self.curr_row = self.cursor.get('1',flags=bsdDB.DB_FIRST)
    
    def hasNext(self):
        return self.curr_row != None
        
    def next(self):
        row = self.curr_row
        
        if row != None:
            self.curr_row = self.cursor.get('1',flags=bsdDB.DB_NEXT)
            if self.curr_row == None:
                self.cursor.close()
        return row
            
        
        
class RepDB:
    def __init__(self, path):
        self.path = path
        self.dbh_stored_blocks = bsdDB.DB() #objects table
        
    def open(self):
        self.dbh_stored_blocks.open(filename=self.path,dbname='stored_blocks',dbtype=bsdDB.DB_BTREE,flags=bsdDB.DB_CREATE,mode=0666)
    
    def add(self, oid, block_id, version):
        key = str((oid, block_id))
        self.dbh_stored_blocks.put(key, str(version))
    
    def get(self, oid, block_id):
        key = str((oid, block_id))
        return self.dbh_stored_blocks.get(key)
        
    def update(self, oid, block_id, version):
        self.add(oid, block_id, version)
        
    def delete(self, oid, block_id):
        key = str((oid, block_id))
        self.dbh_stored_blocks.delete(key)
        
    def close(self):
        self.dbh_stored_blocks.close()

    def getIterator(self):
        return RepDBIterator(self.dbh_stored_blocks.cursor())
    
    def get_all(self):
        cursor = self.dbh_stored_blocks.cursor()
        row = cursor.get('1',flags=bsdDB.DB_FIRST)
        
        result = []
        
        if row == None:
            return result
        
        result.append(row)
        
        while 1:
            row = cursor.get('1',flags=bsdDB.DB_NEXT)
            if row == None:
                break
                
            result.append(row)
    
        cursor.close()
        
        return result
    
        
if __name__ == '__main__':

    db = RepDB('/tmp/repdb.db')
    db.open()
    db.add(1,1)
    print db.get(1)
    db.update(1,2)
    print db.get(1)
    db.delete(1)
    print db.get(1)
    
