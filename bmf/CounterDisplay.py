# -*- coding: utf-8 -*-

"""
copyright:
Copyright (C) 2008,2009  Peter Silva (Peter.A.Silva@gmail.com)
comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""


from PyQt4 import QtGui
from PyQt4 import QtCore


class CounterDisplay(QtGui.QMainWindow):
  """
     provides a GUI pane with counters, currently absolute x,y,z and relative x,y,z

  """

  def __init__(self,parent=None):
     super(CounterDisplay, self).__init__(parent)

     dock = QtGui.QDockWidget( "Counters", self)
     dock.setAllowedAreas( QtCore.Qt.AllDockWidgetAreas )
     #dock.setWidget(cdl)
     cdl = QtGui.QGridLayout()
     self.qw = QtGui.QWidget(self)
     dock.setWidget(self.qw)

     self.qw.al = QtGui.QLabel("Position")
     self.qw.axc = QtGui.QLCDNumber(5,self.qw)
     self.qw.ayc = QtGui.QLCDNumber(5,self.qw)
     self.qw.azc = QtGui.QLCDNumber(5,self.qw)
     self.qw.rl = QtGui.QLabel("Compteur")
     self.qw.rxc = QtGui.QLCDNumber(5,self.qw)
     self.qw.ryc = QtGui.QLCDNumber(5,self.qw)
     self.qw.rzc = QtGui.QLCDNumber(5,self.qw)
     self.qw.axcl = QtGui.QLabel("x",self.qw)
     self.qw.aycl = QtGui.QLabel("y",self.qw)
     self.qw.azcl = QtGui.QLabel("D",self.qw)
     self.qw.rxcl = QtGui.QLabel("x",self.qw)
     self.qw.rycl = QtGui.QLabel("y",self.qw)
     self.qw.rzcl = QtGui.QLabel("P",self.qw)
     
     cdl.addWidget(   self.qw.al, 0, 0, 1, 2 )
     cdl.addWidget( self.qw.axcl, 1, 0 )
     cdl.addWidget(  self.qw.axc, 1, 1 )
     cdl.addWidget( self.qw.aycl, 2, 0 )
     cdl.addWidget(  self.qw.ayc, 2, 1 )
     cdl.addWidget( self.qw.azcl, 3, 0 )
     cdl.addWidget(  self.qw.azc, 3, 1 )
     cdl.addWidget(   self.qw.rl, 0, 2, 1, 2 )
     cdl.addWidget( self.qw.rxcl, 1, 2 )
     cdl.addWidget(  self.qw.rxc, 1, 3 )
     cdl.addWidget( self.qw.rycl, 2, 2 )
     cdl.addWidget(  self.qw.ryc, 2, 3 )
     cdl.addWidget( self.qw.rzcl, 3, 2 )
     cdl.addWidget(  self.qw.rzc, 3, 3 )
     self.qw.setLayout(cdl)
     self.qw.axc.display(0)
     self.qw.ayc.display(0)
     self.qw.azc.display(0)
     self.qw.rxc.display(0)
     self.qw.ryc.display(0)
     self.qw.rzc.display(0)
     self.showing_window=1
     parent.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
     parent.viewMenu.addAction(dock.toggleViewAction())


     
  def Show(self):
     if self.showing_window:
        self.hide()
        self.showing_window=0
     else:
        self.show()
        self.showing_window=1


