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



from common import HydraFile
import os
import sys

global hf_dir

hf = HydraFile.HydraFile('conf/fileclient1.xml')

def create_file(path,filename):
    global hf
    global hf_dir
    
    if not os.path.exists(path):
        return False

    print path

    if os.path.isdir(path):
        print path
        hf.mkdir(os.path.join(hf_dir,filename))
    else:
        fp = open(path, 'rb')
        hf.open(os.path.join(hf_dir,filename),'w')
        while 1:
            buf = fp.read()
            if not buf:
                break
            hf.write(buf)
        
        fp.close()
        hf.close()


def callback(arg, directory, files):
    for file in files:
        full_path = os.path.abspath(os.path.join(directory, file))
        create_file(full_path,file)

if __name__ == '__main__':
    path = sys.argv[1]    
    hf_dir = '/' + os.path.split(path)[1]
    write = True

    hf.mkdir(hf_dir)
        
    os.path.walk(path, callback, None)
