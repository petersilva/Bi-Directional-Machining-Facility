# -*- coding: utf-8 -*-

"""
copyright:
Copyright (C) 2008,2009  Peter Silva (Peter.A.Silva@gmail.com)
comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""


from PyQt4 import QtGui
from PyQt4 import QtCore


class CounterDisplay(QtGui.QDialog):

  def __init__(self,parent=None):
     super(CounterDisplay, self).__init__(parent)

     cdl = QtGui.QGridLayout()

     self.al = QtGui.QLabel("Absolute")
     self.axc = QtGui.QLCDNumber(5,self)
     self.ayc = QtGui.QLCDNumber(5,self)
     self.azc = QtGui.QLCDNumber(5,self)
     self.rl = QtGui.QLabel("Relative")
     self.rxc = QtGui.QLCDNumber(5,self)
     self.ryc = QtGui.QLCDNumber(5,self)
     self.rzc = QtGui.QLCDNumber(5,self)
     self.axcl = QtGui.QLabel("X",self)
     self.aycl = QtGui.QLabel("Y",self)
     self.azcl = QtGui.QLabel("Z",self)
     self.rxcl = QtGui.QLabel("X",self)
     self.rycl = QtGui.QLabel("Y",self)
     self.rzcl = QtGui.QLabel("Z",self)
     
     cdl.addWidget(   self.al, 0, 0, 1, 2 )
     cdl.addWidget( self.axcl, 1, 0 )
     cdl.addWidget(  self.axc, 1, 1 )
     cdl.addWidget( self.aycl, 2, 0 )
     cdl.addWidget(  self.ayc, 2, 1 )
     cdl.addWidget( self.azcl, 3, 0 )
     cdl.addWidget(  self.azc, 3, 1 )
     cdl.addWidget(   self.rl, 0, 2, 1, 2 )
     cdl.addWidget( self.rxcl, 1, 2 )
     cdl.addWidget(  self.rxc, 1, 3 )
     cdl.addWidget( self.rycl, 2, 2 )
     cdl.addWidget(  self.ryc, 2, 3 )
     cdl.addWidget( self.rzcl, 3, 2 )
     cdl.addWidget(  self.rzc, 3, 3 )
     self.setLayout(cdl)
     self.axc.display(0)
     self.ayc.display(0)
     self.azc.display(0)
     self.rxc.display(0)
     self.ryc.display(0)
     self.rzc.display(0)
     self.showing_window=1
     
  def Show(self):
     if self.showing_window:
        self.hide()
        self.showing_window=0
     else:
        self.show()
        self.showing_window=1


