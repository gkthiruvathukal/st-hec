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


import os,time,threading,traceback,sys

print_lock = threading.Lock() #lock for std output


class Ansi:
	def __init__(self):
		l = None
		try:
			if os.isatty(sys.stdout.fileno()):
				l = ('\033[30m','\033[31m','\033[32m','\033[33m','\033[34m','\033[35m','\033[36m','\033[37m',
					'\033[0;0m', '\033[1m', '\033[2m', 
					'\033[40m', '\033[41m', '\033[42m', '\033[43m', '\033[44m', '\033[45m', '\033[46m', '\033[47m')
		except Exception,e:
			print e
			pass	
		
		l = l or tuple(['' for i in range(0,19)])
			
		(self.BLACK, self.RED, self.GREEN, self.YELLOW, self.BLUE, self.MAGENTA, self.CYAN, self.WHITE, 
			self.RESET, self.BOLD, self.REVERSE, 
			self.BLACKBG, self.REDBG, self.GREENBG, self.YELLOWBG, self.BLUEBG, self.MAGENTABG, self.CYANBG, self.WHITEBG) = l

ansi = Ansi()


def GetExceptionData():
	(type, value,tb) = sys.exc_info()
	v1 = '\n'.join(map(lambda a : a.strip(),traceback.format_tb(tb)))
	v2 = '\n'.join(map(lambda a : a.strip(),traceback.format_exception_only(type,value)))
	return (str(v2),str(v1))


def Log(*msg_list):
	print_lock.acquire()



	msg_num= 0
	for msg in msg_list:
		for line in msg.split('\n'):
			if msg_num == 0:
				print ansi.BOLD + ansi.RED + line
			else:
				print ansi.CYAN + line
		print "%s%s%s"%(ansi.RESET+ansi.YELLOW,"-"*80,ansi.RESET)
		msg_num = msg_num+1

	print_lock.release()


class Dispatcher:
    def __init__(self, cfg, fs_db, pb, app):
        self.cfg = cfg
        self.fs_db = fs_db
        self.pb = pb
        self.app = app
        self.packets = {}
        self.handlers = {}
        
    def addHandler(self, pckt_code, handler,priority=50):
        if not self.handlers.has_key(pckt_code):
            self.handlers[pckt_code] = []
        
        handler.setPriority(priority)
        self.handlers[pckt_code].append(handler)
        self.handlers[pckt_code].sort(lambda x,y: x.priority - y.priority)
        
    def clearHandlers(self,pckt_code):
        self.handlers[pckt_code] = []
    
    def handle(self, fd, address):
        data = self.pb.extract_stream(fd)
        data.REQUEST_ADDRESS = address
        
        th = Worker(fd, self.cfg, self.fs_db, self.pb, self.app,self.handlers[data.type],data)
        th.start()

class Worker(threading.Thread):

    def __init__(self, fd, cfg, fs_db, pb, app, handlers,data):
        threading.Thread.__init__(self)
        self.fd = fd    #socket descriptor passed from the server
        self.cfg = cfg  #application's configuration file
        self.pb = pb
        self.data = data
        self.handlers = handlers #list of handlers passed from the dispatcher
        self.fs = fs_db
        self.app = app

        self.fd.settimeout(300)
        
    def close(self):
        if self.fd:
            self.fd.close()

    def shutdown(self):
        print "Thread: shutting down"
        self.shutdown()
            
    def error(self, err_code):
        print err_code
        
    def run(self):
        """Takes care of the incoming packet, and sends it to the class that will handle it"""
        try:
            for proto in self.handlers:
                handler = proto.clone()
                handler.initialize(self.fd, self.cfg, self.fs, self.pb, self.app)
                
                next_state = handler.process(self.data)
                
                while next_state != None:
                    next_state.initialize(self.fd, self.cfg, self.fs,self.pb, self.app)
#                    state_data = self.pb.extract_stream(self.fd)
                    next_state = next_state.process(self.data)
    
                
                #keep processing communications with a state pattern until we're done
                
            self.close()

        except Exception, e:
            self.close()
            sys.exc_info()
            v1,v2 = GetExceptionData()
            Log("Exception within connection",v1,v2)

