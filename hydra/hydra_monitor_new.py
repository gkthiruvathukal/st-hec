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



from Tkinter import *                   # get widgets
import tkFileDialog
import ImageFile
import ImageTk
import Image
import ImageEnhance
import StringIO

import os,stat
import threading


import socket,  signal, sys, traceback
import getopt

from common import fs_objects,network_services
import client_lib
import struct

import sys

client = client_lib.DataClient('conf/fileclient1.xml')

lock = threading.Lock()

class ServerCanvas(Canvas):
    def __init__(self, master, w,h):
        Canvas.__init__(self, master, width=w, height=h, background="#000000")
        self.max_servers = 8
        self.cols = 4
        self.rows = int(self.max_servers/self.cols)
        self.spacing = 5
        self.width = int(w)
        self.heigth = int(h)
        
        self.servers = {}
        self.backgrounds = {'active':'#00aa00','inactive':'#444444','last':'#00ff00','error':'#ff0000'}
        self.foregrounds = {'active':'#000000','inactive':'#888888','last':'#000000','error':'#000000'}
        self.current = {}
        
        if not self.rows:
            self.rows = 1
            
        self.init_servers()

    def init_servers(self):
        w = (self.width - (self.cols)*self.spacing-self.spacing/2)/self.cols
        h = (self.heigth - self.rows*self.spacing-self.spacing/2)/self.rows
        
        pos = [self.spacing,self.spacing]
        n = 1
        for i in range(self.rows):
            for j in range(self.cols):
                self.create_rectangle(pos[0],pos[1],w+pos[0],h+pos[1],width=0,fill='#444444',tag='rect_%s'%n)
                self.create_text(pos[0]+15,pos[1]+15,font=("Helvetica",20),text=str(n),fill='#888888',tag='lbl_%s'%n)
                self.create_text(pos[0]+w/2,pos[1]+h/2,font=("Helvetica",20),text=str(0),fill='#444444',tag='ver_%s'%n)
                pos[0] += self.spacing + w                
                self.servers[n] = 'inactive'
                self.current[n] = False
                self.set_inactive(n)
                n += 1

            pos[0] = self.spacing
            pos[1] += self.spacing + h
        
    def set_active(self, num):
        self.itemconfig(self.find_withtag('rect_%s' % num)[0],fill=self.backgrounds['active'])
        self.itemconfig(self.find_withtag('lbl_%s' % num)[0],fill=self.foregrounds['active'])
        if self.current[num]:
            self.itemconfig(self.find_withtag('ver_%s' % num)[0],fill=self.foregrounds['active'])
        else:
            self.itemconfig(self.find_withtag('ver_%s' % num)[0],fill=self.backgrounds['active'])
        self.servers[num] = 'active'
    
    def set_last(self, num):
        self.itemconfig(self.find_withtag('rect_%s' % num)[0],fill=self.backgrounds['last'])
        self.itemconfig(self.find_withtag('lbl_%s' % num)[0],fill=self.foregrounds['last'])

        if self.current[num]:
            self.itemconfig(self.find_withtag('ver_%s' % num)[0],fill=self.foregrounds['last'])
        else:
            self.itemconfig(self.find_withtag('ver_%s' % num)[0],fill=self.backgrounds['last'])
        
        for id in [x for x in self.servers.keys() if self.servers[x] == 'last']:
            self.set_active(id)

        self.servers[num] = 'last'
    
    def set_inactive(self,num):
        self.itemconfig(self.find_withtag('rect_%s' % num)[0],fill=self.backgrounds['inactive'])
        self.itemconfig(self.find_withtag('lbl_%s' % num)[0],fill=self.foregrounds['inactive'])
        if self.current[num]:
            self.itemconfig(self.find_withtag('ver_%s' % num)[0],fill=self.foregrounds['inactive'])
        else:
            self.itemconfig(self.find_withtag('ver_%s' % num)[0],fill=self.backgrounds['inactive'])
        self.servers[num] = 'inactive'
    
    def set_error(self,num):
        self.itemconfig(self.find_withtag('rect_%s' % num)[0],fill=self.backgrounds['error'])
        self.itemconfig(self.find_withtag('lbl_%s' % num)[0],fill=self.foregrounds['error'])
        if self.current[num]:
            self.itemconfig(self.find_withtag('ver_%s' % num)[0],fill=self.foregrounds['error'])
        else:
            self.itemconfig(self.find_withtag('ver_%s' % num)[0],fill=self.backgrounds['error'])
        self.servers[num] = 'error'
        
    def set_version(self,num,ver=None):
        
        handle = self.find_withtag('ver_%s' % num)
        if not handle:
            return
        
        status = self.servers[num]
        
        if not ver:
            self.itemconfig(handle, text='0')
            self.itemconfig(handle, fill=self.backgrounds[status])
            self.current[num] = False
        else:
            self.itemconfig(handle, text=ver)
            self.itemconfig(handle, fill=self.foregrounds[status])
            self.current[num] = True
        
        

class StatCanvas(Canvas):
    def __init__(self, master, w,h):
        Canvas.__init__(self, master, width=w, height=h, background="#000000")
        self.max_servers = 8
        self.cols = 4
        self.rows = int(self.max_servers/self.cols)
        self.spacing = 1
        self.padding = {'top':12,'left':5,'right':5,'bottom':10}
        self.bar_width = int(w)/self.max_servers - self.spacing
        self.bar_height = int(h) - self.padding['bottom'] - self.padding['top']
        self.canvas_width = int(w)
        self.canvas_height = int(h)
        
        self.servers = {}
        self.backgrounds = {'active':'#00aa00','inactive':'#444444','last':'#00ff00','error':'#ff0000'}
        self.foregrounds = {'active':'#00ff00','inactive':'#888888','last':'#000000','error':'#000000'}
        self.current = {}
        
        self.server_activity = {}
        self.total_activity = 0.00
        
        self.init_servers()
        
    def __hex_convert(self,num):
        num = str(hex(int(num)))[2:]
        if len(num) < 2:
            num = '0%s' % num
        return num

    def create_gradient_bar(self,x1,y1,x2,y2,start_color,end_color,steps,gradient_id):
        height = y2-y1
        if (height < steps):
            steps = height
        
        y_inc = height/(steps*1.)
        
        start_color = start_color[1:]
        start_color = (eval('0x'+start_color[0:2]),eval('0x'+start_color[2:4]),eval('0x'+start_color[4:6]))
        curr_color = start_color[:]

        end_color = end_color[1:]
        end_color = (eval('0x'+end_color[0:2]),eval('0x'+end_color[2:4]),eval('0x'+end_color[4:6]))
    
        dr = (end_color[0] - start_color[0])/(steps*1.)
        dg = (end_color[1] - start_color[1])/(steps*1.)
        db = (end_color[2] - start_color[2])/(steps*1.)

        for y in range(steps):
            curr_color = (curr_color[0] + dr,curr_color[1]+dg,curr_color[2]+db)
            fill = '#' + ''.join([self.__hex_convert(c) for c in curr_color])
            self.create_rectangle(x1,y1+y*y_inc,x2,y1+(y+1)*y_inc,width=0,fill=fill,tag=gradient_id)

    def init_servers(self):
        pos = self.spacing
        base_height = 0
        n = 1
        for j in range(self.max_servers):
            self.create_gradient_bar(pos,self.padding['top'], self.bar_width+pos,self.padding['top'] + self.bar_height,'#00ff00','#8888ff',100,'grad_%s'%n)
            self.create_rectangle(pos,self.padding['top'],self.bar_width+pos,self.padding['top']+self.bar_height,width=0,fill='#444444',tag='rect_%s'%n)
            print "self.create_rectangle(%s,%s,%s,%s)" % (pos,self.padding['top'],self.bar_width+pos,self.padding['top']+self.bar_height)
            self.create_text(pos+self.bar_width/2,self.canvas_height - self.padding['bottom']/2,font=("Helvetica",12),text=str(n),fill='#888888',tag='lbl_%s'%n)
            pos += self.bar_width + 1
            self.current[n] = False
            self.set_inactive(n)
            self.server_activity[n] = 0
            n += 1
            
    def set_bar_percent(self,n,percent):
            print "set_bar_percent(%s,%s)" % (n,percent)
            pos = self.spacing + (self.bar_width+1)*(n-1)
            new_height = self.bar_height*(1-percent)
            self.coords(self.find_withtag('rect_%s'%n)[0],pos,self.padding['top'],self.bar_width+pos,self.padding['top']+new_height)
            
    
    def server_transaction(self,n):
        self.server_activity[n] += 1
        self.total_activity += 1.00
        self.set_bar_percent(n,self.server_activity[n]/self.total_activity)
#        print "self.create_gradient_bar(%s,%s,%s,%s)" % (self.spacing,self.padding['top'], self.bar_width+self.spacing,self.padding['top'] + self.bar_height)
        
        
    def set_active(self, num):
        self.itemconfig(self.find_withtag('lbl_%s' % num)[0],fill=self.foregrounds['active'])
        self.servers[num] = 'active'
    
    def set_last(self, num):
        self.itemconfig(self.find_withtag('lbl_%s' % num)[0],fill=self.foregrounds['last'])
        for id in [x for x in self.servers.keys() if self.servers[x] == 'last']:
            self.set_active(id)
        self.servers[num] = 'last'
    
    def set_inactive(self,num):
        self.itemconfig(self.find_withtag('lbl_%s' % num)[0],fill=self.foregrounds['inactive'])
        self.servers[num] = 'inactive'
    
    def set_error(self,num):
        self.itemconfig(self.find_withtag('lbl_%s' % num)[0],fill=self.foregrounds['error'])
        self.servers[num] = 'error'
        


                
class Monitor(Frame):                     # container subclass
    def __init__(self, parent=None):
        Frame.__init__(self, parent)    # superclass init
        self.pack()
        self.make_widgets()             # attach to self
        self.curr_oid = 0

    def make_widgets(self):
        button_frame = Frame(self)
        button_frame.pack(side=BOTTOM)
#        btn = Button(button_frame, text='Refresh', command=self.onRefresh)
#        btn.pack(side=RIGHT)

        self.serverdisplay = ServerCanvas(self, w="320", h="240")
        self.serverdisplay.pack(side=LEFT, fill=Y)
        
        self.statdisplay = StatCanvas(self, w="320", h="240")

        self.statdisplay.pack(side=RIGHT, fill=BOTH, expand=1)


    def update_version(self, oid, server, version):
        print "updating for: oid=%s server=%s version=%s (curr=%s)" %(oid,server,version,self.curr_oid)
        if self.curr_oid == oid:
            self.serverdisplay.set_version(server, version)
            

class GUI(threading.Thread):
    def __init__(self, mon):
        threading.Thread.__init__(self)
        self.mon = mon
    
    def run(self):
        self.mon.mainloop()

        
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

class Dispatch(threading.Thread):

    def __init__(self, fd,mon):
        threading.Thread.__init__(self)
        self.fd = fd    #socket descriptor passed from the server
        self.mon = mon
#        self.fd.settimeout(1)
        
    def close(self):
        self.fd.close()
        
    def error(self, err_code):
        print err_code
        
    def run(self):
        """Takes care of the incoming packet, and sends it to the class that will handle it"""
        global lock
        net = network_services.NetworkTransport(self.fd)
        
        format = '!IIII'
        packet_size = struct.calcsize(format)
        
        
        while 1:
            try:
                data = net.read(packet_size)
                (t,obj,arg,ver) = struct.unpack(format,data)
                
                print "t=%s obj=%s arg=%s ver=%s" % (t,obj,arg,ver)
                
                lock.acquire()
                
                if t == 0: #server
                    if arg == 0: #server up
                        self.mon.serverdisplay.set_active(obj)
                    elif arg == 1: #server used
                        self.mon.serverdisplay.set_last(obj)
                        self.mon.statdisplay.server_transaction(obj)
                    elif arg == 2: #server down
                        self.mon.serverdisplay.set_error(obj)
                    elif arg == 3: #server inactive
                        self.mon.serverdisplay.set_inactive(obj)
                    
                elif t == 1: #oid
                    self.mon.update_version(obj,arg,ver)

                lock.release()
            except Exception, e:
                self.close()
                sys.exc_info()
                v1,v2 = GetExceptionData()
                Log("Exception within connection",v1,v2)
                lock.release()
                break

        
class TCPServer(threading.Thread):
    def __init__(self,mon):
        threading.Thread.__init__(self)
        self.socket = 0
        self.mon = mon
        
    def handle_sigint(self, signum, frame):
        print "Closing socket"
        if self.socket:
            self.socket.close()
        
        print "Shutting down"
        sys.exit(0)
    
    def run(self):
        self.listen()

    def listen(self):
    
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)         
        self.socket.bind(('', 15000))

        
        self.socket.listen(300)
        
        #loop and serve request
    
        while 1:
            (fd, address) = self.socket.accept()
            print "Monitor: received connection from %s:%s" % address
            th = Dispatch(fd,self.mon)
            th.start()

        print "Shutting down"
        if self.socket:
            self.socket.close()
        if fd:
            fd.close()
            
def handle_sigint(signum, frame):
    print "Closing socket"        
    print "Shutting down"
    sys.exit(0)

if __name__ == '__main__':
    
    signal.signal(signal.SIGINT, handle_sigint)
    monitor = Monitor()

    transport = TCPServer(monitor)
    transport.start()
    GUI(monitor).run()
