#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2008,2009  Peter Silva (Peter.A.Silva@gmail.com)
comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
Operate BMF - wrapper to operate the bi-directional machining facility.

 usually used to fire up a GUI to talk to the BMF over a serial line, that would just be:

      obmf.py

 (default is ´view´ to fire up the GUI, and one can use the settings tab to identify the port.)

      obmf.py --port=localhost:50007 --flags=4 read
         - start up a line mode interface that will only read commands, in network server mode.


      obmf.py --port=localhost:5007 --flasgs=8 view 
         - start up a gui in net client mode, will connect to above...


"""

import bmf
import string
import time
import platform

def usage():
  print """
  obmf <options> command <arguments> 
    -p / --port = "COM2:", or "/dev/ttyS0"
    -s / --speed = 38400 
    -l / --logfile = "bmf.log"
    -f / --flags = <flags>    
           flags:  1 - simulate: port is a write only file.
		   2 - require keys sent to be acknowledged.
                   4 - network server
		   8 - network client
                  16 - print TRACE output 
                       (hexlification of every byte transferred)
    -h / --help  -- print this usage information.

  command is one of:
        view  - start the keyboard GUI.
        send file.hex  - write a file in intel hex format 0
             file.bin  - write a binary, encoding in intel hex.
 
        key  <command>
        key is one of: """ + string.join(bmf.keycodes.keys(),',') + """
  """


import sys
import getopt

last_update=0

def print_msg(s):

    global last_update

    now=time.time()
    print '%s - %s' % ( str(time.time()), s)


def operate_bmf(port=None,cmd="view",speed=38400,dbg=0):
    
    #if port != None:
    b = bmf.bmf(dev=port,speed=speed,flags=dbg,msgcallback=print_msg)
    #else:
    #  b = None
    
    if cmd == 'view':
      from PyQt4 import QtGui
      from PyQt4 import QtCore
      from bmf.GUI import GUI
     
      app = QtGui.QApplication(sys.argv)
      #app.setStyle("windows")
      #app.setStyle("macintosh")
      #app.setStyle("plastique")
      #app.setStyle("windowsxp")
      tb = GUI(b)
      tb.show()
      QtGui.qApp = app
      app.exec_()
      QtGui.qApp = None
      app = None
      return
 
    b.connect()
    if cmd  == 'key' :
      print "Send a key"
      b.sendKey(args[1])
    elif cmd == 'read' :
      while True:
          b.readcmd(True)
    elif cmd == 'test':
          b.sendTestCommands()
    elif cmd == 'send':
      print "Send Intel Hex file"
      filename = args[1]
      if (filename[-4:].lower() == '.hex'):
         b.sendbulkhex(filename)
      else:
         b.sendbulkbin(filename)
    
    else:
      print "some other command..."

if __name__ == '__main__':
    #port="COM2:"

    #FIXME: code for testing purposes...
    #    hardcoded defaults to make testing go quickly.
    #    would be nice to replace with a detection scan...
    #
    #if platform.system() == "Windows":
    #    port="COM1"
    #    dbg=0
    #else:
    #    # I test with a socket back to myself now...
    #    port='localhost:50007'
    #    dbg=8

    speed=115200
    port=None 
    dbg=0

    opts, args = getopt.getopt(sys.argv[1:],"f:hp:s:V",[ 
    "flags=", "f=", "help", "port=", "speed=", "version" ])
    
    for o, a in opts:
      if o in ( "-f", "--f", "--flags"):
         dbg = int(a)
      elif o in ( "-l", "--logfile"):
         logfile = a
      elif o in ( "-p", "--port"):
         port = a
      elif o in ( "-s", "--speed"):
         speed = int(a)
      elif o in ( "-V", "--version"):
         print "my version..."
      else:  # includes -h --help...
         usage()
         sys.exit()

    if len(args) == 0:
      cmd = 'view'
    else:
      cmd = args[0]

    operate_bmf(port,cmd,speed,dbg)
