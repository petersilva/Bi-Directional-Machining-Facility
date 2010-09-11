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

     self.axc = QtGui.QLCDNumber(5,self)
     self.ayc = QtGui.QLCDNumber(5,self)
     self.azc = QtGui.QLCDNumber(5,self)
     self.rxc = QtGui.QLCDNumber(5,self)
     self.ryc = QtGui.QLCDNumber(5,self)
     self.rzc = QtGui.QLCDNumber(5,self)
     self.axcl = QtGui.QLabel("Abs. X",self)
     self.aycl = QtGui.QLabel("Abs. Y",self)
     self.azcl = QtGui.QLabel("Abs. Z",self)
     self.rxcl = QtGui.QLabel("Rel. X",self)
     self.rycl = QtGui.QLabel("Rel. Y",self)
     self.rzcl = QtGui.QLabel("Rel. Z",self)
     cdl.addWidget( self.axcl, 0, 0 )
     cdl.addWidget(  self.axc, 0, 1 )
     cdl.addWidget( self.aycl, 1, 0 )
     cdl.addWidget(  self.ayc, 1, 1 )
     cdl.addWidget( self.azcl, 2, 0 )
     cdl.addWidget(  self.azc, 2, 1 )
     cdl.addWidget( self.rxcl, 3, 0 )
     cdl.addWidget(  self.rxc, 3, 1 )
     cdl.addWidget( self.rycl, 4, 0 )
     cdl.addWidget(  self.ryc, 4, 1 )
     cdl.addWidget( self.rzcl, 5, 0 )
     cdl.addWidget(  self.rzc, 5, 1 )
     self.setLayout(cdl)
     self.axc.display(0)
     self.ayc.display(0)
     self.azc.display(0)
     self.rxc.display(0)
     self.ryc.display(0)
     self.rzc.display(0)
     
  def Show(self):
     if self.showing_window:
        self.hide()
        self.showing_window=0
     else:
        self.show()
        self.showing_window=1


