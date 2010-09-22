
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

FLAG_WRITE_FILE = 1 # simulation mode. (does writing to a file)
FLAG_NO_ACK     = 2 # do not wait for acknowledgements (implied by 01)
FLAG_NET_SERVER = 4 # network server 'port=<port>'  <port> -> tcpip port # 8888
FLAG_NET_CLIENT = 8 # network client 'port=<host>:<port>' -> localhost:8888



BMF_BULK_RECORD_LENGTH = 24 

keycodes = { 
     #key pad 1.                         ASCII characters:
     '1' : 1, '2' : 2, '3' : 3,           # 1,2,3
     '4' : 4, '5' : 5, '6' : 6,           # 4,5,6
     '7' : 7, '8' : 8, '9' : 9,           # 7,8,9
     '0' : 0, '.' : 46, '+/-' : 94,         # 0,.,^
     # keypad 2.
     'NW' : 113, 'Up' : 119, 'NE': 101,      # q,w,e
     'Left': 97, 'Stop': 115, 'Right': 100,  # a,s,d
     'SW' : 122, 'Down':120, 'SE':99,        # z,x,c
     '+' : 43,  'Speed': 83, '-': 45,        # +,<,=
     'Hi/Lo': 60, 'Origin': 61, 'Start/Stop': 62,   # , , >
     'FF': 255, 'Up': 63, 'Down': 64,
     # commands...
     'Status': 83,  'Reset': 82,             # S,R
     'Block' : 0x80,  'Hello': 72,             # B,H  
}

TRIGGER_INTERRUPT = 0x0A
FRAME_TYPE_HEX    = ':'    # ':'
FRAME_ACK_OK      = '\x00'
 
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

  def __init__(self,dev,speed=38400,flags=0,msgcallback=None,display=None):
     """

       device = port to open. ("COM2:" or "/dev/ttyUSB0", etc...)
       speed  = baudrate for communications.
 
       flags = 
                01 - simulation mode. (does writing to a file)
                02 - do not wait for acknowledgements (implied by 01)
		04 - network server 'port=<port>'  <port> -> tcpip port # 8888
		08 - network client 'port=<host>:<port>' -> localhost:8888

     """
     self.speed = speed
     self.dev = dev
     self.flags = flags
     self.msgcallback=msgcallback
     self.display=display

     if self.flags & FLAG_WRITE_FILE:
        self.msgcallback( "simulation by writing to: %s" % dev )
        self.serial = open(dev,'w')
        self.flags = flags | FLAG_NO_ACK   # append supression of ack's.
     elif self.flags & (FLAG_NET_SERVER|FLAG_NET_CLIENT):
       if self.flags & FLAG_NET_SERVER:
           self.sockserv()
       elif flags & FLAG_NET_CLIENT:
           self.sockcli()

       self.poll = select.poll()
       self.poll.register(self.serial.fileno(),select.POLLIN)

       return
     else:
	self.msgcallback( "serial port: connecting to %s at %d" % (self.dev,speed) )
        self.serial = serial.Serial(dev,baudrate=speed)

     self.counters = []
     i=0
     while i < 255:
        self.counters.append(0) 
        i+=1



  def sockserv(self):
     """
	
	this routine hangs the application, until someone connects.

     """
     print 'port is:', self.dev
     host, port = self.dev.split(':')
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
       print 'could not open socket'
       return

     self.serial, addr = s.accept()
     self.msgcallback( "connection accepted. " )
 

  def sockcli(self):
     """
         initialize a socket client.

     """
     host, port = self.dev.split(':')
     
     self.msgcallback( "connecting to host: %s, port: %s" % ( host, port ))
     s = None
     for res in socket.getaddrinfo( str(host), int(port), socket.AF_UNSPEC, socket.SOCK_STREAM ):
        af, socktype, proto, canonname, sa = res

        print res
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
        print 'could not open socket'
        sys.exit(1)

     self.serial=s



 
  def resync(self):
     """ 
         received a garbled command, do work to get back to known state.
     """
     return
     
  def __readn(self,nbytes=1):
     if self.flags & (FLAG_NET_CLIENT|FLAG_NET_SERVER):
	return self.serial.recv(nbytes)
     else:
	return self.serial.read(nbytes)

  def __readline(self):
     """ calls readn to read an entire line, returns the string, with the\n
     """
     s=""
     c=' ' 
     while c != '\n':
          c=self.__readn()
          s+=c

     return s
          

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

     if self.flags & FLAG_WRITE_FILE : 
	return 0 # by definition, file will never answer.
 
     if not block:
       if self.flags & (FLAG_NET_CLIENT|FLAG_NET_SERVER):
           if self.poll.poll(0) == [] :# check, without waiting, for pending read.   
              return 0 # no pending data, we are done.
       elif self.serial.inWaiting() == 0:   # pyserial specific call...
        return 0 # no data received, we are done!

     r=self.__readn()
     if r == '':
        return 0 # FIXME: on socket, polling not working?
     cmd=ord(r)
   
     if cmd == 0x80: #enter blockmode, prepare to rx data.
        print "Not Implemented: receive Intel Hex format data. "
        return 1
     elif cmd == 0x81: # display character string
        coords = self.__readn(2)
        if (len(coords) < 2):
	      self.resync()
	      return
        s = self.__readline()       
        x = 0x7f & ord(coords[0])
        y = 0x7f & ord(coords[1])
        if (x == 0x7f) and (y == 0x7f):
           self.display.clear()
           self.msgcallback( "clear screen" )
        else:
           x = 0x7f & ord(coords[0])
           y = 0x7f & ord(coords[1])
           self.display.writeStringXY(x,y,s[0:-1])
           self.msgcallback( "display: %s" % s)

        self.updateReceived=True
        return 0 
     elif cmd == 0x82: # update 16-bit Counter
        buf=self.__readn(4)
        counter_index = ord(buf[0])
        counter_value  = ord(buf[1])*256+ord(buf[2])
        if buf[3] != TRIGGER_INTERRUPT:
           self.msgcallback( "malformed counter update, lost sync..." )
           self.resync()
        self.counters[counter_index] = counter_value       
        self.updateReceived=True
        return 0
     elif cmd == 0x83: # response status from last command received.
        buf=self.__readn(2)
        if ord(buf[1]) != 0x0a:
            self.msgcallback( "response corrupted" )
            return 2
        if ord(buf[0]) == 0x00:
            return 0  # command succeeded.
        if ord(buf[0]) == 0x01: # blockmode resend current binrec
            self.serial.write(self.binrec)
            self.serial.flush()
            self.last_command_message="resent."
            self.msgcallback( "resending block" )
            return self.readcmd(True)
        else: # undefined error 
            print "error %d: %s" % (ord(buf[0]), self.last_command_message )
            return ord(buf[0])
            self.msgcallback( "error: %d", ord(buf[0]) )
     else: # command...
        s = self.__readline()
        self.msgcallback( "Received Key: %02x" % cmd)
        return 1
      


  def writecmd(self,buf,message,block=False):
     """
       write buf to the port, wait for ack, if bad exit, post message.

       return 0 on success, otherwise, an error message.
     """
     if self.flags & (FLAG_NET_CLIENT|FLAG_NET_SERVER):
         self.serial.send(buf)
     else:
         self.serial.write(buf)
         self.serial.flush()

     self.last_command_message=message

     return self.readcmd(block)

  def sendKey(self,str):
     key=keycodes[str]
     self.msgcallback( "%02x sent for key: +%s+" % ( key, str ) )
     self.writecmd(
          "%c%c" % ( key, TRIGGER_INTERRUPT ),
           "error on send of key: %s" % str
     )

  def sendbulkbinbuffer(self,data,baseaddress=4000):
     """
       encode in intel hex format.  stuff with nuls to 24 chars.
       use given baseaddress and count upwards.
       send each line, wait for status:
             0 - good, 1 - error.
       send eo text as last record.

       : <datacount> <AddrH> <AddrL> <type> <data> <chksum> <padding... >
       
     """

     # switch to block transfer mode...
     self.sendKey('Block')

     i=0
     chunksz=16
     mx = len(data)
     addr=baseaddress
     while i < mx:
        last=i+chunksz
        if last >= mx:
          last=mx

        # build chunk of data for xfer...
        addr=baseaddress + i
        print "addr: %04x" % addr
        address1= (addr & 0xff00) >> 8
        address2= (addr & 0x00ff)
        print "last-i=%d, address1=%02x, address2=%02x" % \
               (last-i,address1,address2)
        prefix = "%c%c%c\0" % (last-i,address1,address2)
        chunk = prefix + data[i:last]

        # calculate checksum for chunk...
        cksum=0
        for s in chunk :
            cksum += ord(s) 
        cksum = (256 - (cksum & 0xff)) & 0xff

        # build binary record, including checksum and padding.
        self.binrec = FRAME_TYPE_HEX + chunk + chr(cksum) 
        padlen = BMF_BULK_RECORD_LENGTH - len(self.binrec) 
        self.binrec += '\0' * padlen

        self.writecmd( self.binrec,
              "error between bytes %d and %d" % (i,last), True )
        i=last

     # switch back to command mode...
     self.writecmd( FRAME_TYPE_HEX + '\00' * 3 + "\x01\xFF" + '\0' * 18,
              "error on return to command mode", True )   

  def sendbulkbin(self,filename,baseaddress=0x4000):
    f=open(filename, 'r')  # might need binary mode 'b' under windows.
    data=f.read()
    f.close()
    self.sendbulkbinbuffer(data,baseaddress)



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
    
    print "record: +%s+, length=%d" % ( rec, len(rec))
    record_to_write = FRAME_TYPE_HEX + binascii.unhexlify(rec)

    # pad to 24 characters long with NULLS.
    padlen = BMF_BULK_RECORD_LENGTH - len(record_to_write) 
    record_to_write += '\0' * padlen

    return( record_to_write )


    

  def sendbulkhex(self,filename):
     """
        decode ascii to raw hex code.  stuff with nuls to 24 chars per line.
        send each line, wait for status:
             0 - good, 1 - error.
        send the result.
     """

     # switch to block transfer mode...
     self.sendKey('Block')
     f=open(filename,'r')
     line_number=0
     byte_count=0
     for hexstringrecord in f :
         print "hexstringrecord: ", hexstringrecord
         self.binrec = self.__hexrecord2bin(hexstringrecord)

         line_number +=1
         self.writecmd(self.binrec, "error on line %d" % line_number )
         # FIXME: does not abort transfer... on error.

         byte_count += len(self.binrec) 

     #FIXME: pray hex file is well-formed so switch back to command 
     #       mode happens.
     #print( "lines: %d, bytes: %d written." % ( line_number, byte_count ) )
     f.close()


  
  def __del__(self):
     self.serial.close()

  def __getattr__(self,name):
     if name == 'keys':
       return(keycodes.keys())

if __name__ == '__main__':
  
   p = bmf("toto.bin",0)
   p.sendbulkhex("../intel_hex_sample.hex")
   p.sendbulkbinbuffer("\xCD\x03\x70\x21\x11\x00\xF9\xCD\x22\x72\xCD\x7C\x71\x3E\x52\x32\x20\xf0\x3e\x48\x32\x21\xf0\x3e\x52\x32\x22\xf0\x3e\x54\x32\x40\xf0\x3e\x48\x32\x41\xf0\x3e\x52\x32\x42\xf0\x3e\x49\x32\x60\xf0\xCC\xEE", 0x7000 )
   p.sendbulkbin("../k.asm")
   print p.keys
