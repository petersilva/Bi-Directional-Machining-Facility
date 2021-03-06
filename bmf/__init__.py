# -*- coding: utf-8 -*-

"""
copyright:
Copyright (C) 2008,2009  Peter Silva (Peter.A.Silva@gmail.com)
comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

import serial
import binascii
import platform
import time
import socket
import select
import sys
import random
import os.path
import struct

FLAG_WRITE_FILE = 0x01 # simulation mode. (does writing to a file)
FLAG_KEY_ACK    = 0x02 # after sending each key, wait for acknowledgements 
FLAG_NET_SERVER = 0x04 # network server 'port=<port>'  <port> -> tcpip port # 8888
FLAG_NET_CLIENT = 0x08 # network client 'port=<host>:<port>' -> localhost:8888
FLAG_TRACE      = 0x10 # dump byte stream to log file for tracing...

# Flag values for updateReceived...
# if a new value rx'd from peer since the last UI update. (like a dirty bit)

FLAG_UPDATE_STRING  = 0x01
FLAG_UPDATE_COUNTER = 0x02
FLAG_UPDATE_LEDS    = 0x04
FLAG_UPDATE_LABELS  = 0x08
FLAG_UPDATE_LOG     = 0x10

BMF_BULK_RECORD_LENGTH = 24 

keycodes = { 
     # key pad 1.                         
     u'10' : 0x10, u'11' : 0x11, u'12' : 0x12, u'13' : 0x13, 
     u'14' : 0x14, u'15' : 0x15, u'16' : 0x16, u'17' : 0x17, 
     u'18' : 0x18, u'19' : 0x19, u'1a' : 0x1a, u'1b' : 0x1b,        
     u'1c' : 0x1c, u'1d' : 0x1d, u'1e' : 0x1e, u'1f' : 0x1f, 
     # key pad 2.                         
     u'20' : 0x20, u'21' : 0x21, u'22' : 0x22, u'23' : 0x23, 
     u'24' : 0x24, u'25' : 0x25, u'26' : 0x26, u'27' : 0x27, 
     u'28' : 0x28, u'29' : 0x29, u'2a' : 0x2a, u'2b' : 0x2b,        
     u'2c' : 0x2c, u'2d' : 0x2d, u'2e' : 0x2e, u'2f' : 0x2f, 
     # keypad 2 old...
     #u'\u2196' : 113, u'\u2191' : 119, u'\u2197': 101,      # nw,n,e : q,w,e
     #u'\u2190': 97, 'Stop': 115, u'\u2192': 100,  # W,,E : a,s,d
     #u'\u2199' : 122, u'\u2193':120, u'\u2198':99,        # SW,S,SE :z,x,c
     #'+' : 43,  'Speed': 83, '-': 45,        # +,<,=
     #'Hi/Lo': 60, 'Origin': 61, 'Start/Stop': 62,   # , , >
     #'FF': 255, u'\u21e7': 63, u'\u21e9': 64,       # FF, Up, Down
     # commands...
     'Status': 83,  'Reset': 82,             # S,R
     'Block' : 0x80,  'Mark': 72,             # B,H  
}

TRIGGER_INTERRUPT = 0x0A
FRAME_TYPE_HEX    = ':'    # ':'
FRAME_ACK_OK      = '\x00'
 
def chksum(chunk):
  """
     calculate a intel hex algorithm checksum for the given chunk of data.
  """
  ck=0
  for s in chunk :
      ck += ord(s) 
  ck = (256 - (ck & 0xff)) & 0xff
  return ck

class bmf:
  """
    bidirectional machining facility - python interface to the z80 over 
       a serial port.  

    The protocol is symmmetrical, so the serial port can be substituted by another instance
    of the software for testing purposes.  This also means that one could connect to a terminal server
    for control at greater distances than permitted by RS-232. 

    target function:
	send keys from virtual keypad?
        send binary file content to be stored in memory.	

   Notes:
    perhaps
    use intel hex format to exchange binary data: https://launchpad.net/intelhex/
  """
  def __bindOpCode(self,code,fun):
    self.opCodeBindings[code] = [ binascii.hexlify(struct.pack('B',0x4f)), fun ]

  def __init__(self,dev,speed=57600,flags=0,msgcallback=None,display=None,logfile="bmf.log"):
     """

       device = port to open. ("COM2:" or "/dev/ttyUSB0", etc...)
       speed  = baudrate for communications.
 
       flags = 
                01 - simulation mode. (does writing to a file)
                02 - do not wait for acknowledgements (implied by 01)
		04 - network server 'port=<port>'  <port> -> tcpip port # 8888
		08 - network client 'port=<host>:<port>' -> localhost:8888

     """
     self.key_ack_pending=False
     self.read_buffer=''
     self.speed = speed
     self.dev = dev
     self.serial = None

     self.flags = 0
     if flags != None:
       self.flags = int(flags)

     print("__init__ self.flags=%d, dev=%s" % (self.flags,self.dev))
     #self.flags = flags | FLAG_TRACE
     self.msgcallback=msgcallback
     self.display=display
     self.updateReceived=0xff
     self.logfilename=logfile
     self.leds=0                   # state of the LED indicators received via op-code 0x85
     # labels for LED indicators received via op-code 0x86, default settings...
     self.labels= [ 'Home XY', 'Step On', 'Coolant', 'Full Time',
                    'Absolute', 'X', 'Y', 'Z', 
                    'Counter', 'X', 'Y', 'Z',
                    '', '', '', '', 
                    '10', '11', '12', '13', # keypad 1
                    '14', '15', '16', '17', 
                    '18', '19', '1a', '1b', 
                    '1c', '1d', '1e', '1f', 
                    '20', '21', '22', '23', # keypad 2
                    '24', '25', '26', '27', 
                    '28', '29', '2a', '2b', 
                    '2c', '2d', '2e', '2f', 
                    '30', '31', '32', '33', # keypad 3
                    '34', '35', '36', '37', 
                    '38', '39', '3a', '3b', 
                    '3c', '3d', '3e', '3f', 
                    '', '', '', '' 
            	  ] 

     self.counters = []
     self.counter_display = []
     i=0
     while i < 15:
        self.counters.append(0) 
        self.counter_display.append(None)
        i+=1

     self.opCodeBindings={}
     i=0
     while i < 255:
        self.__bindOpCode(i, self.readcmd_undefined )
        i+=1

     #self.__bindOpCode( TRIGGER_INTERRUPT, self.readcmd_ignore )
     self.__bindOpCode( 0x80, self.readcmd_enterBlockMode )
     self.__bindOpCode( 0x3a, self.readcmd_rxIntelHexRecord)
     self.__bindOpCode( 0x81, self.readcmd_displayString)
     #self.__bindOpCode( 0x82, self.readcmd_updateCounter)
     self.__bindOpCode( 0x82, self.readcmd_key)
     self.__bindOpCode( 0x83, self.readcmd_response)
     self.__bindOpCode( 0x84, self.readcmd_moveCounter)
     self.__bindOpCode( 0x85, self.readcmd_updateLEDs)
     self.__bindOpCode( 0x86, self.readcmd_setLabel)
     self.__bindOpCode( 0x87, self.readcmd_pullFile)

     i=0x90
     while i < 0x9f:
         self.__bindOpCode( i, self.readcmd_updateCounterByOpcode)
         i+=1

     self.__bindOpCode( 0xaa, self.readcmd_invokeEmulator)
     #if self.dev != None:
     #   self.connect()

      
  def connect(self):
     print("connect... self.flags=%d, dev=%s" % (self.flags,self.dev))
     self.msgcallback("self.flags=%d, dev=%s" % (self.flags,self.dev))
     if self.flags & FLAG_WRITE_FILE:
        self.msgcallback( "simulation by writing to: %s" % self.dev )
        self.serial = open(self.dev,'w')
     elif self.flags & (FLAG_NET_SERVER|FLAG_NET_CLIENT):
       if self.flags & FLAG_NET_SERVER:
           self.sockserv()
       elif self.flags & FLAG_NET_CLIENT:
           self.sockcli()

       self.poll = select.poll()
       self.poll.register(self.serial.fileno(),select.POLLIN)

     else:
        try:
          self.serial = serial.Serial(self.dev, baudrate=self.speed, 
                rtscts=False, timeout=10, writeTimeout=10 )
          # http://pyserial.sourceforge.net/pyserial_api.html
          # with timeouts set, application should never hang.
        except:
	  pass

        if self.serial != None:
          print self.serial
	  self.msgcallback( "serial port: connected to %s at %d" % 
				(self.dev,self.speed) )
        else:
	  self.msgcallback( "ERROR: failed to connect to %s at %d" % 
				(self.dev,self.speed) )



  def sockserv(self):
     """
	Bind to a socket to await a connection from a client.

	this routine hangs the application, until someone connects.

     """
     host, port = self.dev.split(':')
     print "waiting for connection to: %s, on port: %s" % ( host, port )
     host = None
     for res in socket.getaddrinfo(host, int(port), socket.AF_UNSPEC,
                              socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
	af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except socket.error, msg:
            s = None
            continue
        try:
            s.bind(sa)
            s.listen(1)
        except socket.error, msg:
            s.close()
            s = None
            continue

     if s is None:
       self.msgcallback( 'could not open socket' )
       return

     self.serial, addr = s.accept()
     self.msgcallback( "connection accepted. " )
 

  def sockcli(self):
     """
         initialize a socket client (connect to a server.)

     """
     print "sockcli=%s\n" % self.dev
     host, port = self.dev.split(':')
     
     s = None
     for res in socket.getaddrinfo( str(host), int(port), socket.AF_UNSPEC, socket.SOCK_STREAM ):
        af, socktype, proto, canonname, sa = res

        try:
            s = socket.socket(af, socktype, proto)
        except socket.error, msg:
            s = None
            continue

        try:
            s.connect(sa)
        except socket.error, msg:
            s = None
            continue
        break

     if s is None:
        self.msgcallback( "ERROR: failed to connect to host: %s, port: %s" % ( host, port ))
     else:
        self.msgcallback( "connected to host: %s, port: %s" % ( host, port ))

     self.serial=s


 
  def resync(self):
     """ 
         received a garbled command, do work to get back to known state.
     """
     self.msgcallback("resync!")
     self.__readline()
     return
     
  def __readn(self,nbytes=1,noTrace=False):
     """
          read n bytes... blocking until you do...

          there is a read-ahead buffer in serial mode, use that to minimize io calls.
     """

     if self.flags & (FLAG_NET_CLIENT|FLAG_NET_SERVER):
         while len(self.read_buffer) < nbytes:
            to_add = self.serial.recv(nbytes-len(self.read_buffer))
            # FIXME: This is debug code anyways.  code loops infinitely on
            #   remote hangup.  Good fix would be to catch the hangup, this
            #   is an unfortunate place holder.
            if len(to_add) == 0:
                print "FIXME: read 0 bytes when there really should have been more..."
                print "so I decided to exit... more elegant ideas welcome!"
		sys.exit()  
	    self.read_buffer += to_add

     else:
         # read any bytes that are ready...
         self.read_buffer += self.serial.read(self.serial.inWaiting())

         # if that isn't enough, then block and ready until it is...
         while len(self.read_buffer) < nbytes:
	    self.read_buffer += self.serial.read(nbytes-len(self.read_buffer))


     buf=self.read_buffer[0:nbytes]
     self.read_buffer = self.read_buffer[nbytes:]

     if (self.flags & FLAG_TRACE) and not noTrace:
         self.msgcallback( "TRACE Read: " + binascii.hexlify(buf) )

     return buf


  def __readline(self):
     """ calls readn to read an entire line, returns the string, with the
         TRIGGER_INTERRUPT character as termination.
     """
     s=""
     c=' ' 
     while c != chr(TRIGGER_INTERRUPT):
          c=self.__readn(1,True)
          s+=c

     if self.flags & FLAG_TRACE:
         self.msgcallback( "TRACE readline: " + binascii.hexlify(s) )

     return s
          

  def pending(self):
    """
      return True if there is some data the peer has sent, that has not been read.
      return Fals if there is no data waiting for processing.

    """
    if self.flags & (FLAG_NET_CLIENT|FLAG_NET_SERVER):
         pollresult = self.poll.poll(0)
     
         if pollresult == [] :# check, without waiting, for pending read.   
              return False # no pending data, we are done.

         return True

    elif ( len(self.read_buffer) > 0 ) or ( self.serial.inWaiting() > 0): 
         return True

    else:
         return False # no data received, we are done!


  def readpending(self,callback=None):
     """
        process any data that has been received but not processed.
     """
     while self.pending():
	self.readcmd()
        if callback != None:
            callback()

  def readcmd_ignore(self,cmd):
     """
          noticed receipt of extra line feeds,  default action was to skip the next command, which caused problems.
          now just ignore the line feed, next char is next command.
     """
     return

  def readcmd_enterBlockMode(self,cmd):
     """
        puts FSM in block transfer mode, ready to rx intel hex records.
     """
     
     filename=self.__readline()
     filename=filename.strip()
     if filename != "":
           self.writefilename=filename
     else:
           self.writefilename="bmf_dump_%s" % time.strftime("%Y%m%d_%H%M%S", 
                time.localtime(time.time()))

     self.writefile=open(self.writefilename,'w')
     self.file_length=0
     self.sendAck(unconditional=True)
     return 0

  def readcmd_rxIntelHexRecord(self,cmd):
     """
        receive an intel hex block (assume already in block transfer mode.)
     """
     line = self.__readn(23)  # read the line
     datalen=ord(line[0])
     self.file_length += datalen

     #validate checksum.
     sum=chksum(line[0:datalen+4])
     if sum == ord(line[datalen+4]) :
         ack=0
     else:
         ack=1
        
     #print  "rx blk, file_length=%d, len=%d, ack=%d, sum=%d vs. pkt:%d" \
     #       %  ( self.file_length, datalen, ack, sum, ord(line[datalen+4]) )

     if ack == 0: #line is good, write it out.
        #FIXME:  if no file open, behavious undefined...
        #write data to currently open write file.
        if self.writefilename[-4:].lower() == '.hex':
           record_to_write = FRAME_TYPE_HEX + \
             binascii.hexlify(line[0:datalen+5]).upper() + chr(TRIGGER_INTERRUPT)
        else:
           record_to_write = line[4:datalen+4]

        self.writefile.write( record_to_write )

        if datalen==0:
           self.writefile.close()
        
     self.writecmd("%c%c%c" % ( 0x83, ack, TRIGGER_INTERRUPT )) # ack the line.
     return 0

  def readcmd_displayString(self,cmd):
        coords = self.__readn(2)
        if (len(coords) < 2):
	    self.resync()
	    return

        s = self.__readline().decode("utf-8")       
        x = 0x7f & ord(coords[0])
        y = 0x7f & ord(coords[1])
        if (x == 0x7f) and (y == 0x7f):
            self.display.clear()
            self.msgcallback( "clear screen" )
        else:
            self.display.writeStringXY(x,y,s[0:-1])

        self.updateReceived= self.updateReceived | FLAG_UPDATE_STRING

  def readcmd_updateCounter(self,cmd):
        buf=self.__readn(4)
        counter_index = ord(buf[0])
        counter_value  = ord(buf[1])*256+ord(buf[2])
        self.counters[counter_index] = counter_value       
        if self.counter_display[counter_index] != None:
            self.display.writeStringXY(
                self.counter_display[counter_index][0],
                self.counter_display[counter_index][1],
                "%02d.%03d" % ( counter_value / 1000 , counter_value % 1000 ))

        self.updateReceived= self.updateReceived | FLAG_UPDATE_COUNTER
        if ord(buf[3]) != TRIGGER_INTERRUPT:
           self.msgcallback( 
             "malformed counter update. last char is: 0x%02x " % ord(buf[3]) )
        return 0

  def readcmd_response(self,cmd):
        self.key_ack_pending=False
        buf=self.__readn(2)
        if ord(buf[1]) != 0x0a:
            self.msgcallback( "no line feed! response corrupted" )
            return 2
        if ord(buf[0]) == 0x00:
            self.msgcallback( "acknowledged!" )
            return 0  # command succeeded.
        if ord(buf[0]) == 0x01: # blockmode resend current binrec
            self.writecmd(self.binrec)
            self.last_command_message="resent."
            self.msgcallback( "nack! resending block" )
            return self.readcmd(True)
        else: # undefined error 
            self.msgcallback( "error %d: %s" % 
                       (ord(buf[0]), self.last_command_message ) )
            return ord(buf[0])

  def readcmd_moveCounter(self,cmd):
        # receipt from sendCounterXY 

        counter_index=ord(self.__readn()) &0x0f
        coords = self.__readn(2)
        self.__readline()
         
        x = 0x7f & ord(coords[0])
        y = 0x7f & ord(coords[1])

        if (x == 0x7f) and (y == 0x7f):
            self.counter_display[counter_index] = None
            self.msgcallback( "stop counter %d display" % counter_index )
        else:
            self.msgcallback( "show counter %d @ %d,%d" % (counter_index,x,y))
            self.counter_display[counter_index] = ( x, y )
        return 0

  def readcmd_updateLEDs(self,cmd):
        buf=self.__readn(2)
        self.leds=ord(buf[0])
        self.updateReceived= self.updateReceived | FLAG_UPDATE_LEDS

        if ord(buf[1]) != TRIGGER_INTERRUPT:
           self.msgcallback( 
             "malformed LED update. cmd=0x%02x, last char is: 0x%02x " % (cmd,ord(buf[1])) )
        return 0

  def readcmd_setLabel(self,cmd):
        lbl_index=ord(self.__readn()) 
        self.labels[lbl_index] = self.__readline().rstrip().decode("utf-8") 
        self.updateReceived= self.updateReceived | FLAG_UPDATE_LABELS
        if 0x10 <= lbl_index <= 0x30 :
            keycodes[ self.labels[lbl_index] ] = lbl_index
        return 0

  def readcmd_pullFile(self,cmd):
        buf=self.__readn(4)
        start  = ord(buf[0])*256+ord(buf[1])
        mxlen  = ord(buf[2])*256+ord(buf[3])
        filename=self.__readline().rstrip()
        if filename[-4:].tolower() == '.hex':
           self.sendbulkhex(filename)
        else:
           self.sendbulkbin(filename,start,mxlen)
        return 0

  def readcmd_updateCounterByOpcode(self,cmd):
        # receipt from sendCounterUpdate 
        buf=self.__readn(2)
        counter_index = cmd & 0x0f
        counter_value  = ord(buf[0])*256+ord(buf[1])
        #self.msgcallback( "counter[%d]: %d" % (counter_index,counter_value) )
        self.counters[counter_index] = counter_value       

        if self.counter_display[counter_index] != None:
            self.display.writeStringXY(
                self.counter_display[counter_index][0],
                self.counter_display[counter_index][1],
                "%02d.%03d" % ( counter_value / 1000 , counter_value % 1000 ))

        self.updateReceived=self.updateReceived | FLAG_UPDATE_COUNTER

        return 0

  def readcmd_invokeEmulator(self,cmd):

        self.msgcallback("loop-back self-test: start.")
        self.__readline()
        self.sendTestCommands()
        self.msgcallback("loop-back self-test: end")
        return 0

  def readcmd_key(self,cmd):
        (keyc, evt, lf) = self.__readn(3)
        key=ord(keyc)
        self.msgcallback( "key: %02x,%02x received\n" % ( key, ord(evt)))
        print "key: %02x,%02x received\n" % ( key, ord(evt))  
        self.opCodeBindings[key][1](key)

  def readcmd_undefined(self,cmd):
        self.msgcallback( "Received undefined: %02x " % cmd)
        #s = self.__readline()
        self.sendAck()
        return 0

  def readcmd(self,block=False):
     """
     purpose:
       read a command from port.  
       By default, only reads if a command is already partially available. 
       waitforcommand=True will have the routine block and wait for a command
       to arrive.

     return code:
         0 if command read successfully.  non-zero for error.
         1 error: not implemented 
         2 response corrupted.

     algotrithm

       if block, then wait until data is available.
       if there is data available, 
	    read and process, 
       otherwise 
            return immediately.

        FIXME: assumes whole command is available at once...
               does not retry reads for incomplete... 
     """

     self.disable_updates=True
     if self.flags & FLAG_WRITE_FILE : 
	return 0 # by definition, file will never answer.
 
     if not block:
        if not self.pending():
		return 0

     r=self.__readn()
     if r == '':
        #sys.exit() 
        return 0 # FIXME: on socket, polling not working?
     cmd=ord(r)
   
     self.opCodeBindings[cmd][1](cmd)


     return

  def writecmd(self,buf,message='write failed',block=False):
     """
       write buf to the port, wait for ack, if bad exit, post message.

       silent on success, otherwise, post given error message.
     """
     if self.serial == None:
         self.msgcallback( "ERROR: port %s not connected" % self.dev )
         return

     if self.flags & FLAG_TRACE:
         self.msgcallback( "TRACE Write: " + binascii.hexlify(buf) )

     if self.flags & (FLAG_NET_CLIENT|FLAG_NET_SERVER):
         self.serial.send(buf)
     else:
         self.serial.write(buf)
         self.serial.flush()

     self.last_command_message=message

  def __go(self,xoff,yoff,zoff):
    """
      Z80 emulation bit...
      move counters 0 through 5 around appropriately for a displacement in any and all dimensions.
      adjusts counters and sends them to the peer.
 
    """
    self.__readn()  # consume the end of line char...
    if xoff != 0:
         newval=self.counters[0]+xoff
         if (newval < 0 ) or (newval > 25000):
            self.msgcallback('x limit switch')
         else:
            self.counters[0]=newval
            self.sendCounterUpdate(0,newval)
            self.counters[3]+=xoff
            self.sendCounterUpdate(3,self.counters[3])

    if yoff != 0:
         newval=self.counters[1]+yoff
         if (newval < 0 ) or (newval > 40000):
            self.msgcallback('y limit switch')
         else:
            self.counters[1]=newval
            self.sendCounterUpdate(1,newval)
            self.counters[4]+=yoff
            self.sendCounterUpdate(4,self.counters[4])

    if zoff != 0:
         newval=self.counters[2]+zoff
         if (newval < 0 ) or (newval > 1000):
            self.msgcallback('z limit switch')
         else:
            self.counters[2]=newval
            self.sendCounterUpdate(2,newval)
            self.counters[5]+=zoff
            self.sendCounterUpdate(5,self.counters[5])
    self.sendAck()

  def __mark(self):

      self.counters[3]=0
      self.sendCounterUpdate(3,self.counters[3])
      self.counters[4]=0
      self.sendCounterUpdate(4,self.counters[4])
      self.counters[5]=0
      self.sendCounterUpdate(5,self.counters[5])

  def sendAck(self,unconditional=False):
      if unconditional or ( self.flags & FLAG_KEY_ACK ) :
         self.writecmd( 
            struct.pack( "BBB", 0x83, ord(FRAME_ACK_OK), TRIGGER_INTERRUPT ) 
         )
     

  def sendTouchXY(self,x,y,buf):
      """
         send a touch to embedded system.

      """
      self.writecmd( 
          struct.pack( "BBB", 0x88, (x|0x80), (y|0x80))
          + struct.pack("B", TRIGGER_INTERRUPT ))

  def sendStringXY(self,x,y,buf):
      """
         send a frame to display a string on the peer´s character display.
         (part of pseudo-Z80 emulation for testing only)
      """
      self.writecmd( 
          struct.pack( "BBB", 0x81, (x|0x80), (y|0x80))
          +  buf + struct.pack("B", TRIGGER_INTERRUPT ))
   
  def sendCounterUpdate(self,i,v):
      """
         send a frame to initiate a counter update on the peer.
         (part of pseudo-Z80 emulation for testing only)
      """
      self.writecmd( struct.pack( "BBB", 0x90|i, v>>8, v&0xff ) )

  def sendCounterXY(self,i,x,y):
      """
         Send a frame to position a counter on the peer´s character display.
         (part of pseudo-Z80 emulation for testing only)
      """
      self.writecmd( struct.pack( "BBBBB", 0x84, i, (x|0x80), (y|0x80), TRIGGER_INTERRUPT ) )

  def sendLabel(self,i,l):
      """ change the label with index i, to the value l
         (part of pseudo-Z80 emulation for testing only)
      """
      self.writecmd( struct.pack( "BB",  0x86, i) + l.encode("utf-8") +
           struct.pack("B", TRIGGER_INTERRUPT ))


  def sendLEDs(self):
      """
         change the values of the 8 LEDS (four are not visible)
         the value of self.leds is sent.  is a bitmask for the values of each one.
         (part of pseudo-Z80 emulation for testing only)
      """
      self.writecmd( struct.pack( "BBB", 0x85, self.leds, TRIGGER_INTERRUPT ) )

  def sendPullFile(self,filename,start,count):
      """
        send a request for the peer to ship me a file that it knows.
        data will be sent in intel hex format, which includes memory 
        locations.  So have the locations begin at start, and have 
        count bytes sent.
      """
      self.writecmd( 
          struct.pack( "BBBBB", 0x87, start>>8, start&0xff, count>>8, count&0xff)
          +  filename + struct.pack("B", TRIGGER_INTERRUPT ))
      return

  def sendBulkStart(self,filename):
     """  send frame to initiate bulk transfer
          strips out directory part.  assume all use cwd.
                (concession to 24 char limit in z80 uart management code.)
     """
     self.msgcallback(  "name: %s, basename: %s" % ( filename, os.path.basename(filename)))
     self.writecmd( "%c%s\n" % ( chr(0x80), os.path.basename(filename) ))
     self.readcmd(block=True) # wait for an ack...

  def sendKey(self,str,evt):
     """
        send a key to the peer.
     """
     if self.key_ack_pending:
        return

     key=keycodes[str]
     #self.msgcallback( "%02x,%02x sent for key: +%s+" % ( key, evt, str ) )
     self.writecmd( 
        struct.pack( "BBBB", 0x82, key, evt, TRIGGER_INTERRUPT ),
        "error on send of key: %s" % str
     )
     if self.flags & FLAG_KEY_ACK :
        self.key_ack_pending=True
     self.readpending()

  def sendbulkbinbuffer(self,data,filename,baseaddress=4000):
     """
       encode in intel hex format.  stuff with nuls to 23 chars, LF as 24th.
       use given baseaddress and count upwards.
       send each line, wait for status:
             0 - good, 1 - error.
       send eo text as last record.

       : <datacount> <AddrH> <AddrL> <type> <data> <chksum> <padding... >
       
     """

     # switch to block transfer mode...
     self.sendBulkStart(filename)

     i=0
     chunksz=16
     mx = len(data)
     addr=baseaddress
     while i < mx:
        self.msgcallback( "sendbulkbin looping: %d, mx:%d" % (i,mx) )
        last=i+chunksz
        if last >= mx:
          last=mx

        # build chunk of data for xfer...
        addr=baseaddress + i
        address1= (addr & 0xff00) >> 8
        address2= (addr & 0x00ff)
        prefix = "%c%c%c\0" % (last-i,address1,address2)
        chunk = prefix + data[i:last]

        cksum=chksum(chunk)

        # build binary record, including checksum and padding.
        self.binrec = FRAME_TYPE_HEX + chunk + chr(cksum) 
        padlen = BMF_BULK_RECORD_LENGTH - len(self.binrec) 
        self.binrec += '\0' * padlen
        #self.binrec += '\0' * (padlen - 1)
        #self.binrec += chr(TRIGGER_INTERRUPT) 

        self.writecmd( self.binrec,
              "error between bytes %d and %d" % (i,last), True )
        self.readcmd(True)
        i=last

     # switch back to command mode...
     self.msgcallback('Completed file send of %d bytes' % mx )
     self.writecmd( FRAME_TYPE_HEX + '\00' * 3 + "\x01\xFF" + '\0' * 18,
              "error on return to command mode", True )   
     self.readpending()


  def sendbulkbin(self,filename,baseaddress=0x4000,max=0x4000):
    f=open(filename, 'r')  # might need binary mode 'b' under windows.
    data=f.read()
    f.close()
    if len(data) > max:
        self.msgcallback('Error: file %s is %d, but only reserverd %d bytes' % (filename, len(data), max ))
        return

    self.sendbulkbinbuffer(data,filename,baseaddress)

  def __hexrecord2bin(self,record):
    """ convert intel hex string representation to a true binary format.
        do not verify anything (pass-through)
        pad each record with nulls to BMF_BULK_RECORD_LENGTH

        record[1:-2] 
          1 - do not convert :
         -2 - trim <CR><LF> line termination.
    """
    if platform.system() == "Windows":
       end=-1
    else:
       end=-2

    rec=record[1:end]
    
    record_to_write = FRAME_TYPE_HEX + binascii.unhexlify(rec)

    # pad to 24 characters long with NULLS.
    padlen = BMF_BULK_RECORD_LENGTH - len(record_to_write) 
    record_to_write += '\0' * padlen
    #record_to_write += '\0' * (padlen-1)
    #record_to_write += chr(TRIGGER_INTERRUPT) 

    return( record_to_write )


    

  def sendbulkhex(self,filename):
     """
        decode ascii to raw hex code.  stuff with nuls to 24 chars per line.
        send each line, wait for status:
             0 - good, 1 - error.
        send the result.
     """

     # switch to block transfer mode...
     self.sendBulkStart(filename)
     f=open(filename,'r')
     line_number=0
     byte_count=0
     for hexstringrecord in f :
         self.binrec = self.__hexrecord2bin(hexstringrecord)

         line_number +=1
         self.writecmd(self.binrec, "error on line %d" % line_number )
         # FIXME: does not abort transfer... on error.
         self.readcmd(block=True)

         byte_count += len(self.binrec) 

     #FIXME: pray hex file is well-formed so switch back to command 
     #       mode happens.
     self.msgcallback( "lines: %d, bytes: %d written." % ( line_number, byte_count ) )
     f.close()

  def TestCharCounters(self):
     self.counter_display[0] = ( 4, 4 )
     self.counter_display[1] = ( 4, 5 )
     self.counter_display[2] = ( 4, 6 )
     self.counter_display[3] = ( 4, 7 )
     self.counter_display[4] = ( 4, 8 )
     self.counter_display[5] = ( 4, 9 )
  
  def sendTestCommands(self):
     """
        Pretending to be the other side, send a bunch of commands to demonstrate that it works.
     """

     dstart=time.time()
     self.sendLabel(0,"Test Mode")
     self.sendLabel(1,"Running")
     self.sendLabel(2,"Complete")
     self.sendLabel(0x20,'Ho!')
     self.sendLabel(0x20,u'\u2196')
     self.__bindOpCode( 0x20, lambda cmd : self.__go(-1,-1,0))
     self.sendLabel(0x21,u'\u2191')
     self.__bindOpCode( 0x21, lambda cmd : self.__go(0,-1,0))
     self.sendLabel(0x22,u'\u2197')
     self.__bindOpCode( 0x22, lambda cmd : self.__go(+1,-1,0))
     self.sendLabel(0x24,u'\u2190')
     self.__bindOpCode( 0x24, lambda cmd : self.__go(-1,0,0))
     self.sendLabel(0x26,u'\u2192')
     self.__bindOpCode( 0x26, lambda cmd : self.__go(1,0,0))
     self.sendLabel(0x28,u'\u2199')
     self.__bindOpCode( 0x28, lambda cmd : self.__go(-1,1,0))
     self.sendLabel(0x29,u'\u2193')
     self.__bindOpCode( 0x29, lambda cmd : self.__go(0,1,0))
     self.sendLabel(0x2a,u'\u2198')
     self.__bindOpCode( 0x2a, lambda cmd : self.__go(1,1,0))
     self.leds=0x03
     self.sendLEDs()

     self.sendStringXY(0,0, "0123456789012345678901234567890123456789012345678")
     self.sendStringXY(2,2,"welcome.")
     self.sendCounterXY(0,4,4)
     self.sendCounterXY(1,4,5)
     self.sendCounterXY(2,4,6)
     
     for i in range(0,400):
        self.sendCounterUpdate(0,i)
        self.sendCounterUpdate(1,i/3)
        self.sendCounterUpdate(1,i/2)

     self.sendStringXY(2,8,"That took %f s" % (time.time()-dstart))

     rows=20
     columns=48
     for i in range(0,1000):
         self.sendStringXY(
                random.randint(0,columns-1),
                random.randint(9,rows-1),
                   "Hello")

     self.sendStringXY(0,9," "*columns)
     self.sendStringXY(0,10," "*columns)
     self.sendStringXY(2,10,"including 1000 hellos took %f s" % (time.time()-dstart))
     self.sendStringXY(0,11," "*columns)
     self.leds=0x05
     self.sendLEDs()

     

  #def __getattr__(self,name):
  #   if name == 'keys':
  #     return(keycodes.keys())

if __name__ == '__main__':
   # FIXME: does this test stuff work anymore?  
   p = bmf("toto.bin",0)
   p.sendbulkhex("../intel_hex_sample.hex")
   p.sendbulkbinbuffer("\xCD\x03\x70\x21\x11\x00\xF9\xCD\x22\x72\xCD\x7C\x71\x3E\x52\x32\x20\xf0\x3e\x48\x32\x21\xf0\x3e\x52\x32\x22\xf0\x3e\x54\x32\x40\xf0\x3e\x48\x32\x41\xf0\x3e\x52\x32\x42\xf0\x3e\x49\x32\x60\xf0\xCC\xEE", 0x7000 )
   p.sendbulkbin("../k.asm")
   print p.keys
