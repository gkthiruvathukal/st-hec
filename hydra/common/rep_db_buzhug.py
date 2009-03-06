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

from buzhug import Base
import os
from fs_objects import *
from rep_db import RepDBError

class RepDBIterator:
    def __init__(self, set):
        self.set = set
        self.last_index = len(self.set)-1
        self.curr_index = 0
        
        # fetch first row        
        if self.set != []:
            record = self.set[0]
            self.curr_row = (record.key, record.version)
        else:
            self.curr_row = None
    
    def hasNext(self):
        return self.curr_row != None
        
    def next(self):
        row = self.curr_row
        
        if row != None:
            if self.curr_index < self.last_index:
                self.curr_index += 1
                record = self.set[self.curr_index]
                self.curr_row = (record.key, record.version)                
            else:
                self.curr_row = None
        return row
       
        
class RepDB:
    def __init__(self, path):
        self.path = path        
        self.dbh_stored_blocks = Base(self.path)
        try:
            self.dbh_stored_blocks.create(('key', str), ('version', str))
        except IOError:    
            pass            
        
    def open(self):
        self.dbh_stored_blocks.open()
        
    def add(self, oid, block_id, version):
        
        key = str((oid, block_id))        
        
        # lets see if we already have a key stored
        set = self.dbh_stored_blocks.select_for_update(['key','version'],key=key)
        if set == []:                    
            self.dbh_stored_blocks.insert(key, str(version))
        else:
            set[0].update()
        
    def get(self, oid, block_id):
        key = str((oid, block_id))        
        result = self.dbh_stored_blocks.select(['key','version'],key=key)        
                
        return result[0].version
        
    def update(self, oid, block_id, version):        
        self.add(oid, block_id, version)
        
    def delete(self, oid, block_id):
        key = str((oid, block_id))
                
        set = self.dbh_stored_blocks.select_for_update(['key','version'],key=key)                
        self.dbh_stored_blocks.delete(set[0])
        
    def close(self):
        self.dbh_stored_blocks.close()

    def getIterator(self):        
        return RepDBIterator([record for record in self.dbh_stored_blocks])