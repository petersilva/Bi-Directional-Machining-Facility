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

import bmf
from . import CounterDisplay
from . import LogDisplay
from . import CharDisplay
from . import CharDisplayWindow



class GUI(QtGui.QMainWindow):
  """ GUI du bi-directional machining facility
      fournit une interface graphique pour le module bmf.py
  """

  def __logit( self, text ):
    self.log.add(text)

  def __logUI(self,msg):
    self.statusBar().showMessage(msg)

  def __button( self, text, parent, action, otheraction=None ):
    w = QtGui.QPushButton(text, parent)
    w.setAutoRepeat(True)
    self.connect(w, QtCore.SIGNAL('clicked()'), action)
    if otheraction != None:
       self.connect(w, QtCore.SIGNAL('clicked()'), otheraction)
    return(w)


  def __sendkey(self): 
    kk= QtCore.QObject.sender(self)
    self.__logit( "%s key sent" % kk.text() )
    self.bmf.sendKey(str(kk.text()))

  def __sendhex(self):
    kk= str(self.tst.hexedit.text())
    try:
        hxa = map( lambda x: chr(int(x,16)), kk.split(","))
        #x = int(kk,16)
    except:
        self.__logit("%s contains an invalid hex number" % kk)
        return 

    self.bmf.writecmd(''.join(hxa), "returned error from send of %s" % kk)
    self.__logit( "%s code sent" % kk )

  def __sendToggleKey(self): 
    kk= QtCore.QObject.sender(self)
    self.__logit( "%s toggle flipped" % kk.text() )
    self.bmf.sendKey(str(kk.text()))
    # add somthing so toggle stays depressed.

  def __mark(self):
    self.counters.rxc.display(0)
    self.counters.ryc.display(0)
    self.counters.rzc.display(0)
    

  def __go(self,xoff,yoff,zoff):

    x=self.counters.axc.value()
    y=self.counters.ayc.value()
    z=self.counters.azc.value()
    print "go at: %d,%d,%d" % (x, y, z)
    limit=False
    x+=xoff
    y+=yoff
    z+=zoff

    #limit switch
    if (x < 0) or (y <0) or (z<0) or (x > 25000) or (y > 40000) or (z >1000) :
       return 

 
    print "going to: %d,%d,%d" % (x, y, z)

    self.bmf.counters[0] = x
    self.bmf.counters[1] = y
    self.bmf.counters[2] = z

    self.bmf.counters[3] = self.counters.rxc.value()+xoff
    self.bmf.counters[4] = self.counters.ryc.value()+yoff
    self.bmf.counters[5] = self.counters.rzc.value()+zoff

    self.updateGUICounters()


  def updateGUICounters(self):
    self.counters.axc.display(self.bmf.counters[0])
    self.counters.ayc.display(self.bmf.counters[1])
    self.counters.azc.display(self.bmf.counters[2])
    self.counters.rxc.display(self.bmf.counters[3])
    self.counters.ryc.display(self.bmf.counters[4])
    self.counters.rzc.display(self.bmf.counters[5])

  def __goNW(self):
    self.__go(-1,-1,0)

  def __goN(self):
    self.__go(0,-1,0)

  def __goNE(self):
    self.__go(-1,1,0)

  def __goW(self):
    self.__go(-1,0,0)

  def __goE(self):
    self.__go(1,0,0)

  def __goSW(self):
    self.__go(-1,1,0)

  def __goS(self):
    self.__go(0,1,0)

  def __goSE(self):
    self.__go(1,1,0)

  def __goUp(self):
    self.__go(0,0,1)

  def __goDown(self):
    self.__go(0,0,-1)

  def __connect(self):
    #self.serial.connect( ... with baud etc.. set.

    #self.__logit( "connecting..." )
    #self.__logit( "speed: %s " % self.stg.bps.currentText() )
    #self.__logit( "device: %s " % self.stg.portselect.currentText() )
    #self.__logit( "file write: %d " % self.stg.sim.isChecked() )
    #self.__logit( "no ack: %d " % self.stg.noack.isChecked() )
    #self.__logit( "network server: %d " % self.stg.netsrv.isChecked() )
    #self.__logit( "network client: %d " % self.stg.netcli.isChecked() )

    flags = 0 
    if self.stg.sim.isChecked() : 
        flags = flags | 1
    if self.stg.noack.isChecked(): 
        flags = flags | 2
    if self.stg.netsrv.isChecked():
        flags = flags | 4
    if self.stg.netcli.isChecked():
        flags = flags | 8

    #if self.bmf != None:
    #   del self.bmf

    self.bmf = bmf.bmf(str(self.stg.portselect.currentText()),
             speed=int(str(self.stg.bps.currentText())), 
             flags=flags,
	     msgcallback=self.__logit,
             display=self.charDisplay )
    self.connected = True
  
  def sendfile(self):
    filename = QtGui.QFileDialog.getOpenFileName(self, 
                  "Find Files", QtCore.QDir.currentPath())

    self.__logit( "sending file: %s" % filename )

    if filename == None:
        self.__logit( "aborted" )
    else:
         if (str(filename[-4:]).lower() == '.hex'):
              self.bmf.sendbulkhex(filename)
         else:
              baseaddress, ok = QtGui.QInputDialog.getInteger(self,
                   "Où placer les données", "Addresse", 0x4000, 0, 0xffff)
              if ok:
                self.bmf.sendbulkbin(filename,baseaddress)


  def __initKP1(self):

    self.kp1 = QtGui.QWidget()
    self.kp1.setObjectName("Keypad 1")

    kp1layout=QtGui.QGridLayout(self.kp1)

    self.kp1.one = self.__button('1',self.kp1,self.__sendkey)
    kp1layout.addWidget(self.kp1.one,0,0)

    self.kp1.two = self.__button('2', self.kp1, self.__sendkey)
    kp1layout.addWidget(self.kp1.two,0,1)

    self.kp1.three = self.__button('3', self.kp1, self.__sendkey)
    kp1layout.addWidget(self.kp1.three,0,2)

    self.kp1.four = self.__button('4', self.kp1, self.__sendkey)
    kp1layout.addWidget(self.kp1.four,1,0)

    self.kp1.five = self.__button('5', self.kp1, self.__sendkey)
    kp1layout.addWidget(self.kp1.five,1,1)

    self.kp1.six = self.__button('6', self.kp1, self.__sendkey)
    kp1layout.addWidget(self.kp1.six,1,2)

    self.kp1.seven = self.__button('7', self.kp1, self.__sendkey)
    kp1layout.addWidget(self.kp1.seven,2,0)

    self.kp1.eight = self.__button('8', self.kp1, self.__sendkey)
    kp1layout.addWidget(self.kp1.eight,2,1)

    self.kp1.nine = self.__button('9', self.kp1, self.__sendkey)
    kp1layout.addWidget(self.kp1.nine,2,2)

    self.kp1.zero = self.__button('0', self.kp1, self.__sendkey)
    kp1layout.addWidget(self.kp1.zero,3,0)

    self.kp1.decimal = self.__button('.', self.kp1, self.__sendkey)
    kp1layout.addWidget(self.kp1.decimal,3,1)

    self.kp1.plusminus = self.__button('+/-', self.kp1, self.__sendkey)
    kp1layout.addWidget(self.kp1.plusminus,3,2)

    self.tab.addTab(self.kp1,"Numbers")

  def __initKP2(self):

    self.kp2 = QtGui.QWidget()
    self.kp2.setObjectName("Commands")

    kp2layout=QtGui.QGridLayout(self.kp2)

    self.kp2.nw = self.__button('NW', self.kp2, self.__sendkey, self.__goNW)
    kp2layout.addWidget(self.kp2.nw,0,0)

    self.kp2.up = self.__button('N', self.kp2, self.__sendkey, self.__goN)
    kp2layout.addWidget(self.kp2.up,0,1)

    self.kp2.ne = self.__button('NE', self.kp2, self.__sendkey, self.__goNE)
    kp2layout.addWidget(self.kp2.ne,0,2)

    self.kp2.left = self.__button('Left', self.kp2, self.__sendkey, self.__goW)
    kp2layout.addWidget(self.kp2.left,1,0)

    self.kp2.stop = self.__button('Stop', self.kp2, self.__sendkey )
    kp2layout.addWidget(self.kp2.stop,1,1)

    self.kp2.right = self.__button('Right', self.kp2, self.__sendkey, self.__goE)
    kp2layout.addWidget(self.kp2.right,1,2)

    self.kp2.sw = self.__button('SW', self.kp2, self.__sendkey, self.__goSW)
    kp2layout.addWidget(self.kp2.sw,2,0)

    self.kp2.down = self.__button('S', self.kp2, self.__sendkey, self.__goS)
    kp2layout.addWidget(self.kp2.down,2,1)

    self.kp2.se = self.__button('SE', self.kp2, self.__sendkey, self.__goSE)
    kp2layout.addWidget(self.kp2.se,2,2)

    self.kp2.plus = self.__button('+', self.kp2, self.__sendkey)
    kp2layout.addWidget(self.kp2.plus,3,0)

    self.kp2.speed = self.__button('Speed', self.kp2, self.__sendkey)
    kp2layout.addWidget(self.kp2.speed,3,1)

    self.kp2.minus = self.__button('-', self.kp2, self.__sendkey)
    kp2layout.addWidget(self.kp2.minus,3,2)

    self.kp2.hilo = self.__button('Hi/Lo', self.kp2, self.__sendToggleKey)
    kp2layout.addWidget(self.kp2.hilo,4,0)

    self.kp2.origin = self.__button('Origin', self.kp2, self.__sendkey)
    kp2layout.addWidget(self.kp2.origin,4,1)

    self.kp2.send = self.__button('Send', self.kp2, self.__sendkey)
    kp2layout.addWidget(self.kp2.send,4,2)

    self.kp2.ss = self.__button('Start/Stop', self.kp2, self.__sendToggleKey)
    kp2layout.addWidget(self.kp2.ss,5,0)

    self.kp2.cd = self.__button('Up', self.kp2, self.__sendkey, self.__goUp)
    kp2layout.addWidget(self.kp2.cd,6,0)

    self.kp2.cd = self.__button('Down', self.kp2, self.__sendkey, self.__goDown)
    kp2layout.addWidget(self.kp2.cd,6,1)

    self.kp2.cd = self.__button('Mark', self.kp2, self.__mark)
    kp2layout.addWidget(self.kp2.cd,6,2)

    self.tab.addTab(self.kp2,"Commands")

  def __routineUpdate(self):

    if self.connected:
        self.bmf.readcmd()

        if self.bmf.updateReceived:
           self.updateGUICounters()
           self.charDisplayWindow.update()
           self.bmf.updateReceived = False
        
    # ensure radio button consistency.
    if self.stg.sim.isChecked() : 
       if not self.stg.noack.isChecked(): 
           self.stg.noack.setChecked(True)
    if self.stg.netsrv.isChecked():
       if self.stg.sim.isChecked() : 
           self.stg.sim.setChecked(False)
       if self.stg.netcli.isChecked():
           self.stg.netcli.setChecked(False)
    if self.stg.netcli.isChecked():
       if self.stg.sim.isChecked() : 
           self.stg.sim.setChecked(False)

  def __otherPort(self):
    op, ok = QtGui.QInputDialog.getText(self,"Other Port", "Port Address")
    if ok:
      last = self.stg.portselect.count()    
      self.stg.portselect.addItem(op)    
      self.stg.portselect.setCurrentIndex(last)
    

  def __initSerialPortSettings(self):
    self.stg = QtGui.QWidget()
    self.stg.setObjectName("Settings")

    stglayout=QtGui.QGridLayout(self.stg)
    #stglayout.setColumnStretch(0,19)
    #stglayout.setColumnStretch(1,1)
    #stglayout.setVerticalSpacing(4)

    # Port
    import platform

    if platform.system() == 'Windows' :
       from . import scanwin32

       ports=[]
       for order, port, desc, hwid in sorted(scanwin32.comports()):
          ports.append(port)
   

    else : # assume Linux...
       import glob
       ports=glob.glob("/dev/ttyS*") + glob.glob("/dev/ttyUSB*")

  
    
    if (self.bmf != None) and (self.bmf.dev != None):
      ports.append(self.bmf.dev)
       
    ports.append("localhost:50007")

    self.stg.pslabel = QtGui.QLabel("&Port:")

    self.stg.portselect = QtGui.QComboBox()
    self.stg.portselect.addItems(ports)    

    if (self.bmf != None) and (self.bmf.dev != None):
       self.stg.portselect.setCurrentIndex(ports.index(self.bmf.dev))
    
    self.stg.pslabel.setBuddy(self.stg.portselect)
    stglayout.addWidget(self.stg.pslabel,0,0)
    stglayout.addWidget(self.stg.portselect,0,1,1,3)

    self.stg.connect = self.__button('Other', self.stg, self.__otherPort)
    stglayout.addWidget(self.stg.connect,0,4,1,1)

    # baud
    self.stg.bpslabel = QtGui.QLabel("&Baud:")
    self.stg.bps = QtGui.QComboBox()
    speeds=[ "300","900","1200","4800","9600","19200","38400","57600","119200" ]
    self.stg.bps.addItems(speeds)    
    if (self.bmf != None) and (self.bmf.dev != None):
        self.stg.bps.setCurrentIndex( speeds.index(str(self.bmf.speed)))
    else:
        self.stg.bps.setCurrentIndex( 6 ) # ought to be 38400

    self.stg.bpslabel.setBuddy(self.stg.bps)
    stglayout.addWidget(self.stg.bpslabel,1,0,1,1)
    stglayout.addWidget(self.stg.bps,1,2,1,3)

    # Flags
    self.stg.flaglabel = QtGui.QLabel("Flags:")
    stglayout.addWidget(self.stg.flaglabel,2,0)

    self.stg.sim = QtGui.QRadioButton('write file', self.stg)
    self.stg.sim.setAutoExclusive(False)
    stglayout.addWidget(self.stg.sim,3,0,1,2)
    self.stg.noack = QtGui.QRadioButton('No Ack', self.stg)
    self.stg.noack.setAutoExclusive(False)
    stglayout.addWidget(self.stg.noack,3,3,1,2)
    self.stg.netsrv = QtGui.QRadioButton('Net Server', self.stg)
    self.stg.netsrv.setAutoExclusive(False)
    stglayout.addWidget(self.stg.netsrv,4,0,1,2)
    self.stg.netcli = QtGui.QRadioButton('Net Client', self.stg)
    self.stg.netcli.setAutoExclusive(False)
    stglayout.addWidget(self.stg.netcli,4,3,1,2)

    self.stg.connect = self.__button('Connect', self.stg, self.__connect)
    stglayout.addWidget(self.stg.connect,5,0,1,4)


    self.stg.showlabel = QtGui.QLabel("Show:")
    stglayout.addWidget(self.stg.showlabel,6,0)

    self.stg.log = self.__button('Log', self.stg, self.log.Show)
    stglayout.addWidget(self.stg.log,7,0,1,1)

    self.stg.dsp = self.__button('Display', self.stg, self.charDisplayWindow.Show)
    stglayout.addWidget(self.stg.dsp,7,1,1,2)

    self.stg.cnt = self.__button('Counters', self.stg, self.counters.Show)
    stglayout.addWidget(self.stg.cnt,7,3,1,2)


    self.tab.addTab(self.stg,"Settings")

  def __initTesting(self):

    self.tst = QtGui.QWidget()
    self.tst.setObjectName("Testing")

    tstlayout=QtGui.QGridLayout(self.tst)

    self.tst.hexlabel = QtGui.QLabel("Hex:")
    tstlayout.addWidget(self.tst.hexlabel,0,0)
    self.tst.hexedit = QtGui.QLineEdit()
    tstlayout.addWidget(self.tst.hexedit,0,1)


    self.tst.dt = self.__button('Send Hex', self.tst, self.__sendhex)
    tstlayout.addWidget(self.tst.dt,1,0)

    self.tst.dt = self.__button('DisplayTest', self.tst, self.exercise)
    tstlayout.addWidget(self.tst.dt,2,0)

    self.tab.addTab(self.tst,"Testing")




  def __exit( self ):
     del self.bmf
     #self.Display.hide()
     self.log.close()
     self.counters.close()
     self.close()
     
  def exercise( self ):
     self.charDisplay.writeStringXY(0,0, "0123456789012345678901234567890123456789012345678")
     self.charDisplay.writeStringXY(self.exx,self.exy,"Hello")

     self.exy+=1
     self.exx+=4

     if self.connected:
         self.bmf.counters[0]=1000*self.exx
         self.bmf.counters[1]=1000*self.exy
         self.bmf.updateReceived=True
     else:
         self.charDisplayWindow.update()

      

  def __init__(self, bmf=None, parent=None):

     QtGui.QMainWindow.__init__(self)
  
     self.exx=4
     self.exy=4

     self.log=LogDisplay.LogWindow(self.__logUI)
     self.__logit("Startup...")

     self.bmf=bmf

     self.connected = (self.bmf != None) 

     self.charDisplay=CharDisplay.CharDisplay(self.log) 
     self.charDisplayWindow=CharDisplayWindow.CharDisplayWindow(self.log,self.charDisplay)

     self.counters=CounterDisplay.CounterDisplay(self)

     self.setMinimumSize(900, 500)
     self.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )

     self.setWindowTitle('BMF - Panel')
     exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
     exit.setShortcut('Ctrl+Q')
     exit.setStatusTip('Exit application')
     #self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
     self.connect(exit, QtCore.SIGNAL('triggered()'), self.__exit)

     menubar = self.menuBar()
     file = menubar.addMenu('&File')
     file.addAction(exit)

     help = menubar.addMenu('&Help')

     
     self.mainwin = QtGui.QWidget()
     #self.mainlayout= QtGui.QGridLayout() 
     self.mainlayout= QtGui.QHBoxLayout() 

     #self.mainlayout.addWidget(self.counters,0,0)
     self.mainlayout.addWidget(self.counters,1)
     #self.mainlayout.addWidget(self.log,0,1)
     self.mainlayout.addWidget(self.log,5)

     self.tab = QtGui.QTabWidget(self.mainwin)
     self.__initKP2()     
     self.__initKP1()     
     self.__initSerialPortSettings()     
     self.__initTesting()     
     #self.mainlayout.addWidget(self.tab,1,0)
     self.mainlayout.addWidget(self.tab,4)

     #self.mainlayout.addWidget(self.charDisplayWindow,1,1)
     self.mainlayout.addWidget(self.charDisplayWindow,8)

     self.mainwin.setLayout(self.mainlayout)
   
     self.show()
     self.setCentralWidget(self.mainwin)

     self.updateTimer = QtCore.QTimer(self)
     self.connect(self.updateTimer, QtCore.SIGNAL("timeout()"), self.__routineUpdate )
     self.updateTimer.setInterval(500)
     self.updateTimer.start()


     self.__logit("Ready.")
