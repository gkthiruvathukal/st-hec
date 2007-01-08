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


import threading, traceback, sys, os

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


class LogException:
    def __init__(self):
        self.ansi = Ansi()
        self.print_lock = threading.Lock() #lock for std output

    def GetExceptionData(self):
        (type, value,tb) = sys.exc_info()
        v1 = '\n'.join(map(lambda a : a.strip(),traceback.format_tb(tb)))
        v2 = '\n'.join(map(lambda a : a.strip(),traceback.format_exception_only(type,value)))
        return (str(v2),str(v1))
    
    def Log(self,*msg_list):
        self.print_lock.acquire()
        msg_num= 0
        for msg in msg_list:
            for line in msg.split('\n'):
                if msg_num == 0:
                    print self.ansi.BOLD + self.ansi.RED + line
                else:
                    print self.ansi.CYAN + line
            print "%s%s%s"%(self.ansi.RESET+self.ansi.YELLOW,"-"*80,self.ansi.RESET)
            msg_num = msg_num+1
    
        self.print_lock.release()
