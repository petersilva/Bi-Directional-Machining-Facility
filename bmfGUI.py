# -*- coding: utf-8 -*-

"""
copyright:
Copyright (C) 2008,2009  Peter Silva (Peter.A.Silva@gmail.com)
comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""


from PyQt4 import QtGui
from PyQt4 import QtCore
import bmf

class bmfGUI(QtGui.QMainWindow):
  """ GUI du bi-directional machining facility
      fournit une interface graphique pour le module bmf.py
  """

  def __sendkey(self): 
    kk= QtCore.QObject.sender(self)
    print "bmf.sendKey( ", kk.text(), ") "
    self.bmf.sendKey(str(kk.text()))

  def __connect(self):
    #self.serial.connect( ... with baud etc.. set.
    print "connecting..."
    print "speed: ", self.stg.bps.currentText()
    print "device: ", self.stg.portselect.currentText()

    del self.bmf
    self.bmf = bmf.bmf(self.stg.portselect.currentText(), 
                  int(self.stg.bps.currentText()))
  
  def sendfile(self):
    filename = QtGui.QFileDialog.getOpenFileName(self, 
                  "Find Files", QtCore.QDir.currentPath())

    print "filename: ", filename

    if filename == None:
        print "send aborted"
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
    kp1layout.setColumnStretch(0,19)
    kp1layout.setColumnStretch(1,1)
    kp1layout.setVerticalSpacing(4)


    self.kp1.one = QtGui.QPushButton('1', self.kp1)
    kp1layout.addWidget(self.kp1.one,0,0)
    self.connect(self.kp1.one, QtCore.SIGNAL('clicked()'), self.__sendkey)


    self.kp1.two = QtGui.QPushButton('2', self.kp1)
    kp1layout.addWidget(self.kp1.two,0,1)
    self.connect(self.kp1.two, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp1.three = QtGui.QPushButton('3', self.kp1)
    kp1layout.addWidget(self.kp1.three,0,2)
    self.connect(self.kp1.three, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp1.four = QtGui.QPushButton('4', self.kp1)
    kp1layout.addWidget(self.kp1.four,1,0)
    self.connect(self.kp1.four, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp1.five = QtGui.QPushButton('5', self.kp1)
    kp1layout.addWidget(self.kp1.five,1,1)
    self.connect(self.kp1.five, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp1.six = QtGui.QPushButton('6', self.kp1)
    kp1layout.addWidget(self.kp1.six,1,2)
    self.connect(self.kp1.six, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp1.seven = QtGui.QPushButton('7', self.kp1)
    kp1layout.addWidget(self.kp1.seven,2,0)
    self.connect(self.kp1.seven, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp1.eight = QtGui.QPushButton('8', self.kp1)
    kp1layout.addWidget(self.kp1.eight,2,1)
    self.connect(self.kp1.eight, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp1.nine = QtGui.QPushButton('9', self.kp1)
    kp1layout.addWidget(self.kp1.nine,2,2)
    self.connect(self.kp1.nine, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp1.zero = QtGui.QPushButton('0', self.kp1)
    kp1layout.addWidget(self.kp1.zero,3,0)
    self.connect(self.kp1.zero, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp1.decimal = QtGui.QPushButton('.', self.kp1)
    kp1layout.addWidget(self.kp1.decimal,3,1)
    self.connect(self.kp1.decimal, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp1.plusminus = QtGui.QPushButton('+/-', self.kp1)
    kp1layout.addWidget(self.kp1.plusminus,3,2)
    self.connect(self.kp1.plusminus, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.tab.addTab(self.kp1,"Numbers")

  def __initKP2(self):

    self.kp2 = QtGui.QWidget()
    self.kp2.setObjectName("Commands")

    kp2layout=QtGui.QGridLayout(self.kp2)
    kp2layout.setColumnStretch(0,19)
    kp2layout.setColumnStretch(1,1)
    kp2layout.setVerticalSpacing(4)


    self.kp2.nw = QtGui.QPushButton('NW', self.kp2)
    kp2layout.addWidget(self.kp2.nw,0,0)
    self.connect(self.kp2.nw, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp2.up = QtGui.QPushButton('Up', self.kp2)
    kp2layout.addWidget(self.kp2.up,0,1)
    self.connect(self.kp2.up, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp2.ne = QtGui.QPushButton('NE', self.kp2)
    kp2layout.addWidget(self.kp2.ne,0,2)
    self.connect(self.kp2.ne, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp2.left = QtGui.QPushButton('Left', self.kp2)
    kp2layout.addWidget(self.kp2.left,1,0)
    self.connect(self.kp2.left, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp2.stop = QtGui.QPushButton('Stop', self.kp2)
    kp2layout.addWidget(self.kp2.stop,1,1)
    self.connect(self.kp2.stop, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp2.right = QtGui.QPushButton('Right', self.kp2)
    kp2layout.addWidget(self.kp2.right,1,2)
    self.connect(self.kp2.right, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp2.sw = QtGui.QPushButton('SW', self.kp2)
    kp2layout.addWidget(self.kp2.sw,2,0)
    self.connect(self.kp2.sw, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp2.down = QtGui.QPushButton('Down', self.kp2)
    kp2layout.addWidget(self.kp2.down,2,1)
    self.connect(self.kp2.down, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp2.se = QtGui.QPushButton('SE', self.kp2)
    kp2layout.addWidget(self.kp2.se,2,2)
    self.connect(self.kp2.se, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp2.plus = QtGui.QPushButton('+', self.kp2)
    kp2layout.addWidget(self.kp2.plus,3,0)
    self.connect(self.kp2.plus, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp2.speed = QtGui.QPushButton('Speed', self.kp2)
    kp2layout.addWidget(self.kp2.speed,3,1)
    self.connect(self.kp2.speed, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp2.minus = QtGui.QPushButton('-', self.kp2)
    kp2layout.addWidget(self.kp2.minus,3,2)
    self.connect(self.kp2.minus, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp2.hilo = QtGui.QPushButton('Hi/Lo', self.kp2)
    kp2layout.addWidget(self.kp2.hilo,4,0)
    self.connect(self.kp2.hilo, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp2.origin = QtGui.QPushButton('Origin', self.kp2)
    kp2layout.addWidget(self.kp2.origin,4,1)
    self.connect(self.kp2.origin, QtCore.SIGNAL('clicked()'), self.__sendkey)

    self.kp2.send = QtGui.QPushButton('Send', self.kp2)
    kp2layout.addWidget(self.kp2.send,4,2)
    self.connect(self.kp2.send, QtCore.SIGNAL('clicked()'), self.sendfile)

    self.tab.addTab(self.kp2,"Commands")

  def __initSerialPortSettings(self):
    self.stg = QtGui.QWidget()
    self.stg.setObjectName("Settings")

    stglayout=QtGui.QGridLayout(self.stg)
    stglayout.setColumnStretch(0,19)
    stglayout.setColumnStretch(1,1)
    stglayout.setVerticalSpacing(4)

    # Port
    import platform

    if platform.system() == 'Windows' :
       import scanwin32

       ports=[]
       for order, port, desc, hwid in sorted(scanwin32.comports()):
          print "%-10s: %s (%s) ->" % (port, desc, hwid),
          ports.append(port)
   

    else : # assume Linux...
       import glob
       ports=glob.glob("/dev/ttyS*") + glob.glob("/dev/ttyUSB*")

    if self.bmf.dev != None:
      ports.append(self.bmf.dev)
       
    self.stg.pslabel = QtGui.QLabel("&Port:")

    self.stg.portselect = QtGui.QComboBox()
    self.stg.portselect.addItems(ports)    
    self.stg.portselect.setCurrentIndex(ports.index(self.bmf.dev))
    
    self.stg.pslabel.setBuddy(self.stg.portselect)
    stglayout.addWidget(self.stg.pslabel,0,0)
    stglayout.addWidget(self.stg.portselect,0,1)

    # baud
    self.stg.bpslabel = QtGui.QLabel("&Baud:")
    self.stg.bps = QtGui.QComboBox()
    speeds=[ "300","900","1200","4800","9600","19200","38400","57600","119200", "0" ]
    self.stg.bps.addItems(speeds)    
    self.stg.bps.setCurrentIndex( speeds.index(str(self.bmf.speed)))
    self.stg.bpslabel.setBuddy(self.stg.bps)
    stglayout.addWidget(self.stg.bpslabel,1,0)
    stglayout.addWidget(self.stg.bps,1,2)

    # Parity
    self.stg.even = QtGui.QRadioButton('Even', self.stg)
    stglayout.addWidget(self.stg.even,2,0)
    self.stg.odd = QtGui.QRadioButton('Odd', self.stg)
    stglayout.addWidget(self.stg.odd,2,1)
    self.stg.none = QtGui.QRadioButton('None', self.stg)
    stglayout.addWidget(self.stg.none,2,2)

    self.stg.connect = QtGui.QPushButton('Connect', self.stg)
    stglayout.addWidget(self.stg.connect,3,0)
    self.connect(self.stg.connect, QtCore.SIGNAL('clicked()'), self.__connect)

    self.tab.addTab(self.stg,"Settings")


  def __init__(self, bmf=None, parent=None):

     QtGui.QMainWindow.__init__(self)
  
     self.bmf=bmf
     self.setMinimumSize(300, 350)
     self.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )

     self.setWindowTitle('BMF - Panel')
     exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
     exit.setShortcut('Ctrl+Q')
     exit.setStatusTip('Exit application')
     self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

     menubar = self.menuBar()
     file = menubar.addMenu('&File')
     file.addAction(exit)

     help = menubar.addMenu('&Help')

     
     self.mainlayout= QtGui.QGridLayout() 

     self.status = QtGui.QLabel('Not Connected')

     self.mainlayout.addWidget(self.status,0,0)

     self.tab = QtGui.QTabWidget(self)
     self.mainlayout.addWidget(self.tab,1,0)

     self.setCentralWidget(self.tab)

     self.__initKP2()     
     self.__initKP1()     
     self.__initSerialPortSettings()     
   
