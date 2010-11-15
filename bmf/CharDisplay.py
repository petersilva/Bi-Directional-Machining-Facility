# -*- coding: utf-8 -*-
class CharDisplay:
  """
     A character buffer to store characters in an array of the given number of rows and columns.
     
     this class handles updates to the buffer, and does no display.

  """
  def __init__(self,log,rows=24,columns=80):

     self.msgcallback=log
     self.rows = rows
     self.columns = columns
     self.msg = [ "", "" ]
     j=0
     while j < self.rows:
         self.msg.append( "" )
         j+=1
     self.clearUpdates()

  def clearUpdates(self):
     self.updates=[]

  def clear(self):
     j=0
     while j < self.rows:
         self.msg[j]= ""
         j+=1

  def writeStringXY(self,x,y,str):
     """
        display a given str at row y in column x.

     """

     # refuse to draw out of bounds...
     if ( x > self.columns ) or ( y >= self.rows ):
        self.msgcallback( "origin off of screen: row=%d, column=%d" % ( y, x ) )
        return

     #print "write, self.msg[%d] before: +%s+" % ( y, self.msg[y] )

     # if msg is too short, pump it up...
     oldy=len(self.msg[y])
     if oldy < x:
         self.msg[y] = self.msg[y] + " " * (x-oldy)

     xend = x + len(str)
     if xend < self.columns:
         # if it fits on the screen, just substitute the string within the line.
         self.msg[y]= self.msg[y][0:x] + str + self.msg[y][xend:]
     else:
         # if it replaces the end of the line, then change the end...
         str_cutoff = len(str) - (xend - self.columns)
         self.msg[y]= self.msg[y][0:x] + str[0:str_cutoff]

     self.msg[y].strip()
     self.updates.append(y)

