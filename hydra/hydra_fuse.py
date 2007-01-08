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


#!/usr/bin/env python
#@+leo-ver=4
#@+node:@file xmp.py
#@@first
#
#    Copyright (C) 2001  Jeff Epler  <jepler@unpythonic.dhs.org>
#
#    This program can be distributed under the terms of the GNU LGPL.
#    See the file COPYING.
#

#@+others
#@+node:imports

from fuse import Fuse
import os
from errno import *
from stat import *

from common import HydraFile
from common.hydra_client_api import HydraClientException
import struct
import copy

import thread
#@-node:imports
#@+node:class Xmp
class HydraFuse(Fuse):

    #@	@+others
    #@+node:__init__
    def __init__(self, *args, **kw):

        Fuse.__init__(self, *args, **kw)
    
        if True:
            print "xmp.py:Xmp:mountpoint: %s" % repr(self.mountpoint)
            print "xmp.py:Xmp:unnamed mount options: %s" % self.optlist
            print "xmp.py:Xmp:named mount options: %s" % self.optdict
    
        # do stuff to set up your filesystem here, if you want
        #thread.start_new_thread(self.mythread, ())
        
        self.cfg_location = kw['cfg_location']
        self.hf = HydraFile.HydraFile(self.cfg_location)
        self.openfiles = {}
    #@-node:__init__
    #@+node:mythread
    def mythread(self):
    
        """
        The beauty of the FUSE python implementation is that with the python interp
        running in foreground, you can have threads
        """    
        print "mythread: started"
        #while 1:
        #    time.sleep(120)
        #    print "mythread: ticking"
    
    #@-node:mythread
    #@+node:attribs
    flags = 1
    
    #@-node:attribs
    #@+node:getattr
    def getattr(self, path):
        print "Hydra:getattr"
        try:
            x = self.hf.stat_file(path)
            print x
            return x
        except HydraClientException,e:
            print "Exception: %s" % e.value
            return -ENOENT
    #@-node:getattr
    #@+node:readlink
    def readlink(self, path):
        print "readlink"
    	return os.readlink(path)
    #@-node:readlink
    #@+node:getdir
    def getdir(self, path):
        print "getdir: %s" % path
        (file, children) = self.hf.stat(path)
        if children:
            dirlist = [(x.path.split('/')[-1],0) for x in children]
            print dirlist
            dirlist.insert(0,('..',0))
            dirlist.insert(0,('.',0))            
            return dirlist
        else:
            return -EINVAL
    #@-node:getdir
    #@+node:unlink
    def unlink(self, path):
        print "unlink"
    	return os.unlink(path)
    #@-node:unlink
    #@+node:rmdir
    def rmdir(self, path):
        print "rmdir"
    	return os.rmdir(path)
    #@-node:rmdir
    #@+node:symlink
    def symlink(self, path, path1):
        print "symlink"
    	return os.symlink(path, path1)
    #@-node:symlink
    #@+node:rename
    def rename(self, path, path1):
        print "rename"
#        print "Hydra: rename %s -> %s" % (path, path1)
        try:
            return self.hf.rename(path, path1)
        except HydraClientException,e:
            print "Exception: %s" % e.value
            return -EINVAL
    #@-node:rename
    #@+node:link
    def link(self, path, path1):
        print "link"
    	return os.link(path, path1)
    #@-node:link
    #@+node:chmod
    def chmod(self, path, mode):
        print "chmod"
    	return os.chmod(path, mode)
    #@-node:chmod
    #@+node:chown
    def chown(self, path, user, group):
        print "chown"
    	return os.chown(path, user, group)
    #@-node:chown
    #@+node:truncate
    def truncate(self, path, size):
        print "Truncate1"
    	f = open(path, "w+")
    	f.truncate(size)
        return None
    
    #@-node:truncate
    #@+node:mknod
    def mknod(self, path, mode, dev):
        print "Mknod"
        """ Python has no os.mknod, so we can only do some things """
#        print "Hydra: mknod (%s,%s,%s)" % (path,mode,dev)
        if S_ISREG(mode):
            self.hf.open(path, "w")
            self.hf.close()
        else:
            return -EINVAL
    #@-node:mknod
    #@+node:mkdir
    def mkdir(self, path, mode):
        print "mkdir"
#        print "MKDIR: %s %s" % (path, mode)
        self.hf.mkdir(path)
    #@-node:mkdir
    #@+node:utime
    def utime(self, path, times):
        print "utime"
    	return os.utime(path, times)
    #@-node:utime
    #@+node:open
    def open(self, path, flags):
        print "open"
#        print "Hydra:open: %s (%s)" % (path,flags)
        if not self.openfiles.has_key(path):
            f = copy.copy(self.hf)
            f.open(path, flags)
            self.openfiles[path] = f
    	return 0
    
    #@-node:open
    #@+node:read
    def read(self, path, length, offset):
        print "read"
#        print "Hydra:read: %s, %s, %s" % (path,length,offset)
        if not self.openfiles.has_key(path):
            self.open(self,path,'r+w')
        
        f = self.openfiles[path]
        f.seek(offset)
        return f.read(length)
    
    #@-node:read
    #@+node:write
    def write(self, path, buf, off):
        print "write"
#        print "Hydra:write: %s @ %s" % (path, off)
        f = self.openfiles[path]
        f.seek(off)
        f.write(buf)
        return len(buf)
    
    #@-node:write
    #@+node:release
    def release(self, path, flags):
        print "release"
#        print "Hydra:release: %s %s" % (path, flags)
        if self.openfiles.has_key(path):
            f = self.openfiles[path]
            f.close()
            del self.openfiles[path]
        return 0
    #@-node:release
    #@+node:statfs
    def statfs(self):
        """
        Should return a tuple with the following 6 elements:
            - blocksize - size of file blocks, in bytes
            - totalblocks - total number of blocks in the filesystem
            - freeblocks - number of free blocks
            - totalfiles - total number of file inodes
            - freefiles - nunber of free file inodes
    
        Feel free to set any of the above values to 0, which tells
        the kernel that the info is not available.
        """
        print "xmp.py:Xmp:statfs: returning fictitious values"
        blocks_size = 1024
        blocks = 100000
        blocks_free = 25000
        files = 100000
        files_free = 60000
        namelen = 80
        return (blocks_size, blocks, blocks_free, files, files_free, namelen)
    #@-node:statfs
    #@+node:fsync
    def fsync(self, path, isfsyncfile):
        print "xmp.py:Xmp:fsync: path=%s, isfsyncfile=%s" % (path, isfsyncfile)
        return 0
    
    #@-node:fsync
    #@-others
#@-node:class Xmp
#@+node:mainline

if __name__ == '__main__':
    server = HydraFuse(cfg_location='conf/fileclient1.xml')
    server.multithreaded = 1;
    server.main()
#@-node:mainline
#@-others
#@-node:@file xmp.py
#@-leo
