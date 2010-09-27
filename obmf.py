#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2008,2009  Peter Silva (Peter.A.Silva@gmail.com)
comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
Operate BMF - le programme pour opérer un BMF. part le GUI

"""

import bmf
import string

def usage():
  print """
  obmf <options> command <arguments> 
    -p / --port = "COM2:", or "/dev/ttyS0"
    -s / --speed = 38400 
    -D / --debug = <flags>    
           flags:  1 - simulate: port is a write only file.
		   2 - suppress/ignore acknowledgements
                          (implied by 1)
  command is one of:
        view  - start the keyboard GUI.
        send file.hex  - write a file in intel hex format 0
             file.bin  - write a binary, encoding in intel hex.
 
        key  <command>
        key is one of: """ + string.join(bmf.keycodes.keys(),',') + """
  """


import sys
import getopt

def operate_bmf():
    #port="COM2:"
    port=None
    speed=38400
    dbg=2
    
    opts, args = getopt.getopt(sys.argv[1:],"D:p:s:V",[ 
    "dbg=", "debug=", "port=", "speed=", "version" ])
    
    for o, a in opts:
      if o in ( "-D", "--dbg", "--debug"):
         dbg = int(a)
      elif o in ( "-p", "--port"):
         port = a
      elif o in ( "-s", "--speed"):
         speed = int(a)
      elif o in ( "-V", "--version"):
         print "my version..."
      else:
         usage()
         sys.exit()
    
    if port != None:
      b = bmf.bmf(port,speed,dbg)
    else:
      b = None
    
    
    if len(args) == 0:
      cmd = 'view'
    else:
      cmd = args[0]
    
    if cmd == 'view':
      from PyQt4 import QtGui
      from PyQt4 import QtCore
      from bmf.GUI import GUI
     
      app = QtGui.QApplication(sys.argv)
      tb = GUI(b)
      tb.show()
      app.exec_()
    
    elif cmd  == 'key' :
      print "Send a key"
      b.sendKey(args[1])
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
    operate_bmf()
