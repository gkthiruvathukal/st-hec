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

import sys,os
from fs_objects import *

class RepDBError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return self.value   
       
class RepDB:
    def __init__(self, path, module):
                
        # import module
        sys.path.append(module)                                        
        import_string = "from "+ os.path.splitext(module)[0] + " import RepDB as RepDBParent"
        exec import_string
        
        self.parent = RepDBParent(path)
                
    def open(self):
        self.parent.open()
        
    def add(self, oid, block_id, version):
        self.parent.add(oid, block_id, version)
        
    def get(self, oid, block_id):
        return self.parent.get(oid, block_id)
        
    def update(self, oid, block_id, version):        
        self.parent(oid, block_id, version)
        
    def delete(self, oid, block_id):
        self.parent.delete(oid, block_id)
        
    def close(self):
        self.parent.close()

    def getIterator(self):
        return self.parent.getIterator() 