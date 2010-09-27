# -*- coding: utf-8 -*-

"""
copyright:
Copyright (C) 2008,2009  Peter Silva (Peter.A.Silva@gmail.com)
comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""


from PyQt4 import QtGui
from PyQt4 import QtCore

import time


class LogWindow(QtGui.QDialog):

  def add(self,msg):

     #self.log_entries.append( [ self.log_index, msg ] )
     self.log_index +=1 
     #leTime.setFlags(QtCore.QtItemIsEnabled | QtCore.Qt.ItemIsSelectable)
     #scroll, remove last...
     if self.log_index >= self.max_entries:
          self.messageTable.removeRow(self.max_entries)

     # insert new item...
     self.messageTable.insertRow(0)
     leTime = QtGui.QTableWidgetItem(time.strftime("%H:%M",time.localtime())) 
     self.messageTable.setItem(0,0, leTime)
     leMsg = QtGui.QTableWidgetItem(msg) 
     self.messageTable.setItem(0,1, leMsg)
     self.messageTable.setCurrentCell(0,0)

     self.last_message = msg
     #print msg
     self.post_callback(msg)



  def __init__(self,post_callback=None,parent=None,max_entries=100):
     super(LogWindow, self).__init__(parent)
     
     self.post_callback=post_callback
     #self.log_entries = []
     self.log_index = 0
     self.max_entries=max_entries
     self.messageTable = QtGui.QTableWidget(1,2,self)
     self.resize(400,400)
     self.messageTable.setHorizontalHeaderLabels(("Time","Message"))
     self.messageTable.horizontalHeader().setResizeMode( 0, QtGui.QHeaderView.Fixed)
     self.messageTable.horizontalHeader().setResizeMode( 1, QtGui.QHeaderView.Stretch)
     self.showing_window=1

     loglayout= QtGui.QVBoxLayout()
     loglayout.addWidget(self.messageTable)
     self.setLayout(loglayout)
     
  def minimumSizeHint(self):
     return(QtCore.QSize(200,200))

  def sizeHint(self):
     return(QtCore.QSize(200,200))



  def Show(self):
     if self.showing_window:
        self.hide()
        self.showing_window=0
     else:
        self.show()
        self.showing_window=1


