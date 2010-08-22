
# -*- coding: utf-8 -*-

"""
copyright:
Copyright (C) 2008,2009  Peter Silva (Peter.A.Silva@gmail.com)
comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

import serial
import binascii


BMF_BULK_RECORD_LENGTH = 24 

keycodes = { 
     #key pad 1.                         ASCII characters:
     '1' : '1', '2' : 50, '3' : 51,           # 1,2,3
     '4' : 52, '5' : 53, '6' : 54,           # 4,5,6
     '7' : 55, '8' : 56, '9' : 57,           # 7,8,9
     '0' : 48, '.' : 46, '+/-' : 94,         # 0,.,^
     # keypad 2.
     'NW' : 113, 'Up' : 119, 'NE': 101,      # q,w,e
     'Left': 97, 'Stop': 115, 'Right': 100,  # a,s,d
     'SW' : 122, 'Down':120, 'SE':99,        # z,x,c
     '+' : 43,  'Speed': 83, '-': 45,        # +,<,=
     'Hi/Lo': 60, 'Origin': 61,
     # commands...
     'Status': 83,  'Reset': 82,             # S,R
     'Block' : 66,  'Hello': 72,             # B,H  
}

TRIGGER_INTERRUPT = 0x0A
FRAME_TYPE_KEY    = 0x4B    # 'K'
FRAME_TYPE_HEX    = 0x3A
 
class bmf:
  """
    bidirectional machining facility - python interface to the z80 over 
       a serial port

    target function:
	send keys from virtual keypad?
        send binary file content to be stored in memory.	

   Notes:
    perhaps
    use intel hex format to exchange binary data: https://launchpad.net/intelhex/

  """

  def __init__(self,dev,speed=38400,dbg=0):
     """
       device = port to open. ("COM2:" or "/dev/ttyUSB0", etc...)
       speed  = baudrate for communications.
 
       test harness:
                if speed=0, then device is the name of a file to dump
                ourput to
     """
     self.speed = speed
     self.dev = dev

     if dbg & 1:
        print "opening in simulation mode, writing binary to ", dev
        self.serial = open(dev,'w')
        self.dbg = dbg | 2   # append supression of ack's.
     else:
        self.dbg = dbg
        self.serial = serial.Serial(dev,baudrate=speed)
     
  def writechk(self,buf,message):
     self.serial.write(buf)
     if (self.dbg & 2) == 0:
        response = self.serial.read(3)
        if response[0] != '0' : 
           print message



  def sendKey(self,str):
     key=keycodes[str]
     print "Sending Key for +%s+, key: %c" % ( str, key )
     self.writechk(
          "%c%c%c" % ( FRAME_TYPE_KEY, key, TRIGGER_INTERRUPT ),
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
        binrec = ':' + chunk + chr(cksum) 
        padlen = BMF_BULK_RECORD_LENGTH - len(binrec) 
        binrec += '\0' * padlen

        self.writechk( binrec,
              "error between bytes %d and %d" % (i,last) )
        i=last

     # switch back to command mode...
     self.writechk( ':' + '\00' * 3 + "\x01\xFF" + '\0' * 18,
              "error on return to command mode" )   

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
    print "record: +%s+, length=%d" % ( record[1:-2], len(record[1:-2]))
    record_to_write = ':' + binascii.unhexlify(record[1:-2])

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
         binrec = self.__hexrecord2bin(hexstringrecord)

         line_number +=1
         self.writechk(binrec, "error on line %d" % line_number )
         # FIXME: does not abort transfer... on error.

         byte_count += len(binrec) 

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
