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



import time
import random


class DataServerList:
    def __init__(self):
        self.active_clients = {}
        self.locks = {}
        self.lock_timeout = 60 #timeout for locks to expire
        
        self.oid_usage = {}
        
    def add(self, name, ip, port):
        """store name, ip, port and timestamp of last announce/heartbeat, timestamp of last access"""
        
        if self.active_clients.has_key(name):
            self.active_clients[name] = [ip,port,time.time(),self.active_clients[name][3]]
        else:
            self.active_clients[name] = [ip,port,time.time(),time.time()]
    
    def select_dataserver(self,oid):
        if not len(self.active_clients):
            return None
        q = [(k,self.active_clients[k][3]) for k in self.active_clients.keys()]
        q.sort(lambda x,y: (-1)*(x[1] < y[1]) + (1)*(x[1] > y[1]))
        key = q[0][0]
        self.active_clients[key][3] = time.time()
        return (self.active_clients[key][0],self.active_clients[key][1], key)

    def select_blocks_replicas(self, blocks, replicas):
        
        block_servers = {} #maps which servers have the latest versions of each block

        for block_id in blocks.keys():
            block_version = blocks[block_id]
            block_reps = replicas[block_id]
            
            if block_reps:
                block_reps = block_reps.replicas
            else:
                return None #there are no replicas of this block, so there's no point
            
            #create a list with only the ONLINE servers with the latest version for this block
            block_servers[block_id] = [x for x in block_reps.keys() if block_reps[x] == block_version and self.active_clients.has_key(str(int(x)))]
            
            #there are no servers online with this block, so don't go on
            if not block_servers[block_id]:
                return None
                
#        print "block_servers: %s" % block_servers
            
        server_blocks = {} #how many blocks does each server have
        for block in block_servers.keys():
            for server in block_servers[block]:
                if not server_blocks.has_key(server):
                    server_blocks[server] = 0
                server_blocks[server] += 1
                
#        print "server_blocks: %s" % server_blocks
        
        #sort the online servers depending on how many blocks they have
        sorted_servers = [(k,server_blocks[k]) for k in server_blocks.keys()]
        sorted_servers.sort(lambda x,y: (-1)*(x[1] > y[1]) + (1)*(x[1] < y[1]))

        #for now also sort them by access time
        q = [(k,blocks,self.active_clients[str(int(k))][3]) for (k,blocks) in sorted_servers]
        q.sort(lambda x,y: (-1)*(x[2] < y[2]) + (1)*(x[2] > y[2]))
        
        sorted_servers = [(k,blocks) for (k,blocks,t) in q]
        
#        print "sorted_servers: %s" % sorted_servers

        t = time.time()
        
        #list of blocks with the server that will serve each block
        chosen_replicas = {}
        for block in block_servers.keys():
            for (server,count) in sorted_servers:
                if server in block_servers[block]:
                    server = str(int(server))
                    chosen_replicas[block] = (self.active_clients[server][0],self.active_clients[server][1], server)
                    self.active_clients[server][3] = time.time()
                    break
                    
#        print "chosen_replicas: %s" % chosen_replicas
        
        return chosen_replicas #format: chosen_replicas[block_id] = (ip, port, serverid)
        
    def select_new_replica_server(self, replicas):
        
        #we filter the active server list against the servers that already have that file
        curr_replicas = map(str, replicas.keys())
        possible_pics = [x for x in self.active_clients.keys() if x not in curr_replicas]
        
#        print curr_replicas
#        print self.active_clients.keys()
#        print possible_pics
        
        #if there's nowhere that we can replicate the file to, return none
        if not len(possible_pics):
            return None
        
        #randomly pick a server to replicate to
        idx = random.randint(0, len(possible_pics)-1)
        key = possible_pics[idx]
        self.active_clients[key][3] = time.time()        
        return (self.active_clients[key][0],self.active_clients[key][1], key)
        
        
        pass
        
    def add_lock(self,oid,block_id,version,serverid):
        oid = str(oid)
        block_id = str(block_id)
        if self.is_locked(oid, block_id):
            return False
        else:
            if not self.locks.has_key(oid):
                self.locks[oid] = {}
            self.locks[oid][block_id] = [serverid,version,time.time()]
            return True
    
    def is_locked(self,oid,block_id):
        oid = str(oid)
        block_id = str(block_id)
        has_lock = False
        #if the timeout has expired, delete this lock
        if self.locks.has_key(oid):
            if self.locks[oid].has_key(block_id):
                if time.time() > (self.locks[oid][block_id][2] + self.lock_timeout):
                    del self.locks[oid][block_id]
                else:
                    has_lock = True
                    
        return has_lock
        
    def file_has_locks(self, oid):
        """Returns True if at least one block of this file is locked"""
        oid = str(oid)
        is_file_locked = False
        
        if self.locks.has_key(oid):
            for block_id in self.locks[oid]:
                if is_locked(oid, block_id):
                    is_file_locked = True
                    break
        
        return is_file_locked
        

    def release_lock(self,oid,block_id,version):
        oid = str(oid)
        block_id = str(block_id)
        
        if self.locks.has_key(oid):
            if self.locks[oid].has_key(block_id):
                del self.locks[oid][block_id]
    
    def view(self):
        print self.active_clients
    
    def remove(self,name):
        del self.active_clients[name]
        
    def get(self):
        return self.active_clients
    
    def get_server(self, serverid):
        serverid = str(serverid)
        if self.active_clients.has_key(serverid):
            return (self.active_clients[serverid][0],self.active_clients[serverid][1]) #return ip & port of server
        else:
            return None
            
    def get_name(self, ip, port):
        for key in self.active_clients.keys():
            if self.active_clients[key][0] == ip and self.active_clients[key][1] == port:
                return key
                
        return None

    def remove_address(self, ip, port):
        for key in self.active_clients.keys():
            if self.active_clients[key][0] == ip and self.active_clients[key][1] == port:
                del self.active_clients[key]
                self.remove_locks(key)
                return True
                
        return False

    def remove_locks(self,serverid):
        """Removes all locks server 'serverid' had"""
        for oid in self.locks.keys():
            for block_id in self.locks[oid].keys():
                if self.locks[oid][block_id][0] == serverid:
                    del self.locks[key]
                
    def oid_used(self,oid):
        if not self.oid_usage.has_key(oid):
            self.oid_usage[oid] = 0
        self.oid_usage[oid] += 1
        
        return not self.oid_usage[oid] % 15

