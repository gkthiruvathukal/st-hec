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
import struct

BLOCK_SIZE = 65536
BLOCKS = 8

import sys
file = '/' + sys.argv[1].split('/')[-1]

hf = HydraFile.HydraFile('conf/fileclient1.xml')
hf.open(file, 'w')

buf = '0'# + struct.pack('b',0)
buf *= BLOCK_SIZE

for i in range(BLOCKS):
    hf.write(buf)
hf.close()

print "Waiting 5 seconds..."
import time
time.sleep(5)

print "Initializing clients..."
clients = []
for i in range(BLOCKS):
    clients.append(HydraFile.HydraFile('conf/fileclient1.xml'))

print "Setting everything to the client's number + 1.."
for i in range(BLOCKS):
    buf = '%s' % (i+1)# + struct.pack('b',0)
    buf *= BLOCK_SIZE

    print "Client %s" % i
    clients[i].open(file,'r+w')
    clients[i].show_block_locations()
    clients[i].seek(i*BLOCK_SIZE,0)
    clients[i].write(buf)
    clients[i].close()
