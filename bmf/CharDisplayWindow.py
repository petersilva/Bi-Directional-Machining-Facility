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
    A Character addressable display based on the CharDisplay class.
    It uses a Courier as a standard fixed-width font to ensure letters show up 
     where they should.

    FIXME:
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

     path = QtGui.QPainterPath()
     painter = QtGui.QPainter(self)
     painter.setFont(self.myfont)
     painter.setBackgroundMode(QtCore.Qt.OpaqueMode)  # default is TransparentMode
     # FIXME: perhaps painter.setStretch(... some function of xmag... ) to fill window...


     # print all the characters on the "screen."
     
     for j in xrange(0,self.display.rows):
         if self.display.msg[j] == "":
            continue
         painter.drawText(QtCore.QPoint(0,ymag*(j+1)),self.display.msg[j])

     self.display.clearUpdates()


  def setDisplay(self,display):
     self.display = display

  def resizeEvent(self,event):
     # FIXME: crappy heuristic to get the font to fit in the window.
     # need to select a monospaced / fixed character width font for co-ordinates to work.
     xmag=self.width()/self.display.columns
     ymag=self.height()/self.display.rows
     self.myfont.setPixelSize(int(xmag*1.7)) 



  def mousePressEvent(self,e):
     if e.button() == QtCore.Qt.LeftButton: # send left clicks to device
        # FIXME, extend protocol to send mouse events.
        print 'not implemented click... char address x,y,button: ', \
           int(e.x()*self.display.columns/self.width()), \
           int(e.y()*self.display.rows/self.height()), \
           e.button()      
        print 'left button!'
     elif e.button() == QtCore.Qt.RightButton: # post font menu for right click.
        f,ok = QtGui.QFontDialog.getFont(self.myfont)
        if ok :
           self.myfont=f
           self.resizeEvent(None)


  def __init__(self,log,display=None,parent=None):
     """
     Initialize the character display. 
     """
     super(CharDisplayWindow, self).__init__(parent)

     self.setObjectName('CharDisplayWindow')
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
     self.myfont=QtGui.QFont("Courier")

     
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



