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
       repaints the entire display, based on current contents of self.display
        which defines rows, columns, and msg provides contents.

     """

     if self.display == None:
        return

     xmag=self.width()/self.display.columns
     ymag=self.height()/self.display.rows

     
     # FIXME: crappy heuristic to get the font to fit in the window.
     myfont=QtGui.QFont("Courier")
     #myfm=QtGui.QFontMetrics(myfont)
     myfont.setPixelSize(int(xmag*1.7)) 
     myfont.setWeight(QtGui.QFont.Bold)


     path = QtGui.QPainterPath()
     painter = QtGui.QPainter(self)
     # need to select a monospaced / fixed character width font for co-ordinates to work.
     painter.setFont(myfont)
     painter.setBackgroundMode(QtCore.Qt.OpaqueMode)  # default is TransparentMode
     # FIXME: perhaps painter.setStretch(... some function of xmag... ) to fill window...


     # print all the characters on the "screen."
     
     for j in xrange(0,self.display.rows-1):
         if self.display.msg[j] == "":
            continue
         painter.drawText(QtCore.QPoint(0,ymag*(j+1)),self.display.msg[j])

     self.display.clearUpdates()


  def setDisplay(self,display):
     self.display = display

  def __init__(self,log,display=None,parent=None):
     """
     Initialize the character display. 
     """
     super(CharDisplayWindow, self).__init__(parent)

     self.log = log
     self.setDisplay(display)

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



