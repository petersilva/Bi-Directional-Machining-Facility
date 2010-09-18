# -*- coding: utf-8 -*-

"""
copyright:
Copyright (C) 2008,2009  Peter Silva (Peter.A.Silva@gmail.com)
comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

from PyQt4 import QtGui
from PyQt4 import QtCore
from . import LogDisplay

class CharDisplayWindow(QtGui.QWidget):
  """
    A Character addressable display having dimension columns width, by rows tall.
    main data structure is an array of character strings: self.msg
    there are ROWS elements in self.msg, and each element is COLUMNS long.
    It uses a Courier as a standard fixed-width font to ensure letters show up 
     where they should.

    FIXME:
        -- ideally, would check actual dimensions and adjust font to fully fill rectangle.
           would mean adjusting point size and perhaps Stretch and Spacing (see QFont).
        -- does not do colour yet.
        -- flashing would have to be done by repainting the screen, blech...

  """

  def paintEvent(self,event):
     """
       repaints the entire display, based on current contents of self.msg

     """

     if self.display == None:
        return

     xmag=self.width()/self.display.columns
     ymag=self.height()/self.display.rows
     sz=10
     path = QtGui.QPainterPath()
     painter = QtGui.QPainter(self)
     # need to select a monospaced / fixed character width font for co-ordinates to work.
     painter.setFont(QtGui.QFont("Courier" ))
     # FIXME: perhaps painter.setStretch(... some function of xmag... ) to fill window...

     painter.begin(self)

     painter.save()

     # print all the characters on the "screen."
     j=0
     y=0
     while j < self.display.rows:
         y+=ymag
         pt = QtCore.QPoint(0,y)
         #print "printing: %d, %s" % (  j, self.msg[j] ) 
         painter.drawText(pt,self.display.msg[j])
         j+=1

     painter.restore()
     painter.end()


#  def write(self,x,y,str):
#     """
#        write a given str at row y in column x.
#
#     """
# 
#     # refuse to draw out of bounds...
#     if ( x > self.columns ) or ( y >= self.rows ):
#        self.add( "origin off of screen: row=%d, column=%d" % ( y, x ) )
#	return
#
#     #print "write, self.msg[%d] before: +%s+" % ( y, self.msg[y] )
#
#     xend = x + len(str)
#     if xend < self.columns:
#         # if it fits on the screen, just substitute the string within the line.
#         self.msg[y]= self.msg[y][0:x] + str + self.msg[y][xend:]
#     else:
#         # if it replaces the end of the line, then change the end...
#         str_cutoff = len(str) - (xend - self.columns)
#         self.msg[y]= self.msg[y][0:x] + str[0:str_cutoff] 
#     self.update() 

  def setDisplay(self,display):
     self.display = display

  def __init__(self,log,display=None,parent=None):
     """
     Initialize the character display of columns width  x rows height.
     """
     super(CharDisplayWindow, self).__init__(parent)

     print "hi from z80 init"

     self.log = log
     self.setDisplay(display)

     #self.msg = [ "", "" ]
     #j=0
     #while j < self.rows:
     #    self.msg.append( " " * self.columns )
     #    j+=1

     self.pixmap = QtGui.QPixmap()
     self.pen = QtGui.QPen()
     self.brush = QtGui.QBrush()
     self.pixmap = QtGui.QPixmap()

     self.setBackgroundRole(QtGui.QPalette.Base)
     self.setAutoFillBackground(True)
     
     style = QtCore.Qt.PenStyle(QtCore.Qt.SolidLine)
     cap = QtCore.Qt.PenCapStyle(QtCore.Qt.FlatCap)
     join = QtCore.Qt.PenJoinStyle(QtCore.Qt.MiterJoin)
     width = 10
     self.pen = QtGui.QPen(QtCore.Qt.blue, width, style, cap, join)

     self.showing_window=1
     
  def minimumSizeHint(self):
     return(QtCore.QSize(480,200))

  def sizeHint(self):
     return(QtCore.QSize(480,200))


  def Show(self):
     if self.showing_window:
        self.hide()
        self.showing_window=0
     else:
        self.show()
        self.showing_window=1



