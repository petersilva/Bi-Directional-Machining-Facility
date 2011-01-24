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
     dock.setObjectName('Counters')
     dock.setAllowedAreas( QtCore.Qt.AllDockWidgetAreas )
     #dock.setWidget(cdl)
     cdl = QtGui.QGridLayout()
     self.qw = QtGui.QWidget(self)
     dock.setWidget(self.qw)

     self.qw.al = QtGui.QLabel("Position")

     self.qw.axci = QtGui.QLCDNumber(2,self.qw)
     self.qw.axcp = QtGui.QLabel(".")
     self.qw.axcd= QtGui.QLCDNumber(3,self.qw)

     self.qw.ayci = QtGui.QLCDNumber(2,self.qw)
     self.qw.aycp = QtGui.QLabel(".")
     self.qw.aycd = QtGui.QLCDNumber(3,self.qw)

     self.qw.azci = QtGui.QLCDNumber(2,self.qw)
     self.qw.azcp = QtGui.QLabel(".")
     self.qw.azcd = QtGui.QLCDNumber(3,self.qw)

     self.qw.rxci = QtGui.QLCDNumber(2,self.qw)
     self.qw.rxcp = QtGui.QLabel(".")
     self.qw.rxcd= QtGui.QLCDNumber(3,self.qw)

     self.qw.ryci = QtGui.QLCDNumber(2,self.qw)
     self.qw.rycp = QtGui.QLabel(".")
     self.qw.rycd = QtGui.QLCDNumber(3,self.qw)

     self.qw.rzci = QtGui.QLCDNumber(2,self.qw)
     self.qw.rzcp = QtGui.QLabel(".")
     self.qw.rzcd = QtGui.QLCDNumber(3,self.qw)


     self.qw.rl = QtGui.QLabel("Compteur")
     self.qw.axcl = QtGui.QLabel("x",self.qw)
     self.qw.aycl = QtGui.QLabel("y",self.qw)
     self.qw.azcl = QtGui.QLabel("z",self.qw)
     self.qw.rxcl = QtGui.QLabel("x",self.qw)
     self.qw.rycl = QtGui.QLabel("y",self.qw)
     self.qw.rzcl = QtGui.QLabel("z",self.qw)
     
     cdl.addWidget(   self.qw.al, 0, 0, 1, 2 )
     cdl.addWidget( self.qw.axcl, 1, 0, QtCore.Qt.AlignRight )
     cdl.addWidget(  self.qw.axci, 1, 1, QtCore.Qt.AlignRight )
     cdl.addWidget(  self.qw.axcp, 1, 2, QtCore.Qt.AlignCenter )
     cdl.addWidget(  self.qw.axcd, 1, 3, QtCore.Qt.AlignLeft )

     cdl.addWidget( self.qw.aycl, 2, 0, QtCore.Qt.AlignRight )
     cdl.addWidget(  self.qw.ayci, 2, 1, QtCore.Qt.AlignRight )
     cdl.addWidget(  self.qw.aycp, 2, 2, QtCore.Qt.AlignCenter )
     cdl.addWidget(  self.qw.aycd, 2, 3, QtCore.Qt.AlignLeft )

     cdl.addWidget( self.qw.azcl, 3, 0, QtCore.Qt.AlignRight )
     cdl.addWidget(  self.qw.azci, 3, 1, QtCore.Qt.AlignRight )
     cdl.addWidget(  self.qw.azcp, 3, 2, QtCore.Qt.AlignCenter )
     cdl.addWidget(  self.qw.azcd, 3, 3, QtCore.Qt.AlignLeft )

     cdl.addWidget(   self.qw.rl, 0, 4, 1, 3 )
     cdl.addWidget( self.qw.rxcl, 1, 4, QtCore.Qt.AlignRight )
     cdl.addWidget(  self.qw.rxci, 1, 5, QtCore.Qt.AlignRight )
     cdl.addWidget(  self.qw.rxcp, 1, 6, QtCore.Qt.AlignCenter )
     cdl.addWidget(  self.qw.rxcd, 1, 7, QtCore.Qt.AlignLeft )

     cdl.addWidget( self.qw.rycl, 2, 4, QtCore.Qt.AlignRight )
     cdl.addWidget(  self.qw.ryci, 2, 5, QtCore.Qt.AlignRight )
     cdl.addWidget(  self.qw.rycp, 2, 6, QtCore.Qt.AlignCenter )
     cdl.addWidget(  self.qw.rycd, 2, 7, QtCore.Qt.AlignLeft )

     cdl.addWidget( self.qw.rzcl, 3, 4, QtCore.Qt.AlignRight )
     cdl.addWidget(  self.qw.rzci, 3, 5, QtCore.Qt.AlignRight )
     cdl.addWidget(  self.qw.rzcp, 3, 6, QtCore.Qt.AlignCenter )
     cdl.addWidget(  self.qw.rzcd, 3, 7, QtCore.Qt.AlignLeft )


     self.qw.setLayout(cdl)

     self.qw.axci.display(0)
     self.qw.axcd.display(0)
     self.qw.ayci.display(0)
     self.qw.aycd.display(0)
     self.qw.azci.display(0)
     self.qw.azcd.display(0)

     self.qw.rxci.display(0)
     self.qw.rxcd.display(0)
     self.qw.ryci.display(0)
     self.qw.rycd.display(0)
     self.qw.rzci.display(0)
     self.qw.rzcd.display(0)

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


