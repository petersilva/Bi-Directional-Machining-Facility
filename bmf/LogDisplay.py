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

     self.log_entries[self.log_index] = ( time.time(), msg )
     self.log_index +=1 
     self.updated=True
     if self.log_index >= self.max_entries:
           self.log_index=0

     self.post_callback(msg)
     return
  
  def logUpdate(self):
      
     if self.updated:
        for i in range(0,self.max_entries):
           j=(self.log_index+i) % self.max_entries
           #print "log update, i=%d, j=%d " % (i,j, )
           if self.log_entries[j][0] == 0:
             tstring=""
           else:
             tstring= time.strftime("%H:%M:%S", time.localtime(self.log_entries[j][0]) )
             tstring += ".%02d" % int( (self.log_entries[j][0]%1) * 100 )

           #print "log update, i=%d, j=%d, tstring=%s, item=%s" % (i,j,tstring, self.log_entries[j][1] )
           leTime = self.messageTable.item(i,0)
           leTime.setText( tstring )
           lemsg =  self.messageTable.item(i,1)
           lemsg.setText( self.log_entries[j][1] )

        self.messageTable.setCurrentCell(self.max_entries-1,0)
        self.updated=False

  def __init__(self,post_callback=None,parent=None,max_entries=100):
     super(LogWindow, self).__init__(parent)
     
     self.post_callback=post_callback


     self.log_index = 0
     self.updated=False

     self.max_entries=max_entries
     self.messageTable = QtGui.QTableWidget(1,2,self)
     self.resize(400,400)
     self.messageTable.setHorizontalHeaderLabels(("Time","Message"))
     self.messageTable.horizontalHeader().setResizeMode( 0, QtGui.QHeaderView.Fixed)
     self.messageTable.horizontalHeader().setResizeMode( 1, QtGui.QHeaderView.Stretch)
     self.showing_window=1

     self.log_entries=[]

     for i in xrange(0,max_entries):
        #self.log_entries[i]= ("    ","")
        self.log_entries.append( (0,"") )

        self.messageTable.insertRow(i)
        leTime = QtGui.QTableWidgetItem("     ") 
        self.messageTable.setItem(i,0, leTime)
        leMsg = QtGui.QTableWidgetItem("") 
        self.messageTable.setItem(i,1, leMsg)
        

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


