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

# for exercise
import random

gui_update_total_time = 0
gui_update_total_count = 0
gui_update_next_time = time.time()


class GUI(QtGui.QMainWindow):
  """ GUI for the bi-directional machining facility
      provide a graphical user interface.

      key aspect is to limit update frequency, and amount of work for accepting updates.
      (accept far more updates than are actually posted.)
      this is necessary to support Z80 sending several hundred updates per second, GUI could not keep up.

  """

  def __logit( self, text ):
    """
       save the given text to the application log, and trigger a conditional ui update.
    """
    self.log.add(text)
    self.logfile.write(text.encode("utf-8"))
    self.logfile.write("\n")

    if self.connected:
       self.bmf.updateReceived|= bmf.FLAG_UPDATE_LOG
    self.__guiupdate()

  def __logUI(self,msg):
    """
        sets the status message at bottom left of GUI, (at the followup update.)
    """
    self.msg = msg

  def __button( self, text, parent, action ):
    """
       define a standard button.
    """
    w = QtGui.QPushButton(text, parent)
    w.setAutoRepeat(True)
    #w.setAutoRepeatDelay(2000)
    w.setAutoRepeatInterval(5)
    self.connect(w, QtCore.SIGNAL('clicked()'), action)

    return(w)


  def __sendkey(self): 
    """
       send a key stroke event to the peer. 
    """
    kk= QtCore.QObject.sender(self)
    self.bmf.sendKey(unicode(kk.text()))
    self.__logit( "%s key sent" % kk.text() )

  def __sendhex(self):
    """
      send raw hexadecimal sequence to the peer.  for Testing purposes only.
      
    """
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
    """
      send a key event, where the key is a toggle.
      
      FIXME:  add somthing so toggle stays depressed. a visual cue to toggle-hood.
    """
    kk= QtCore.QObject.sender(self)
    self.__logit( "%s toggle flipped" % kk.text() )
    self.bmf.sendKey(str(kk.text()))

  def updateGUICounters(self):
    """
        Actually do the work to update the GUI, not just the internal counters.
    """
    #if self.connected:
    #   for i in range(0,0xf):
    #      if self.bmf.counter_display[i] != None:
    #          self.bmf.display.writeStringXY( self.bmf.counter_display[i][0], self.bmf.counter_display[i][1],
    #            "%2d.%03d" % ( self.bmf.counters[i] / 1000 , self.bmf.counters[i] % 1000 ))

    self.counters.qw.axc.display(self.bmf.counters[0])
    self.counters.qw.ayc.display(self.bmf.counters[1])
    self.counters.qw.azc.display(self.bmf.counters[2])
    self.counters.qw.rxc.display(self.bmf.counters[3])
    self.counters.qw.ryc.display(self.bmf.counters[4])
    self.counters.qw.rzc.display(self.bmf.counters[5])


  def __connect(self):
    """
       setup up a connection to the BMF peer.

    """

    if self.connected:
       return

    flags = 0 
    if self.stg.sim.isChecked() : 
        flags = flags | 1
    if self.stg.noack.isChecked(): 
        flags = flags | 2
    if self.stg.netsrv.isChecked():
        flags = flags | 4
    if self.stg.netcli.isChecked():
        flags = flags | 8

    self.bmf = bmf.bmf(str(self.stg.portselect.currentText()),
             speed=int(str(self.stg.bps.currentText())), 
             flags=flags,
	     msgcallback=self.__logit,
             display=self.charDisplay )
    self.connected = True
  
  def __disconnect(self):
     """
        disconnect from the BMF peer.
     """
     if not self.connected:
       return

     self.bmf.serial.close()
     self.bmf=None
     self.connected = False
     self.__logit( "Disconnected" )


  def pullfile(self):
    """
       FIXME: Not yet Implemented!

       GUI element to have Z80 send requested data to PC.
       Post a filename dialog.
       Post a start address.
       Post a byte count.

       issue a pullfile command, to the bmf.

       FIXME: Cheapie triple dialog, should probably have a single one.
    """
    filename = QtGui.QFileDialog.getOpenFileName(self, 
                  "File to Pull", QtCore.QDir.currentPath())

    self.__logit( "asking for file: %s" % filename )

    if filename == None:
        self.__logit( "aborted" )
        return

    baseaddress, ok = QtGui.QInputDialog.getInteger(self,
        "Start Address", "Address", 0x4000, 0, 0xffff)
    if not ok:
        self.__logit( "aborted, no base address given." )
        return

    count, ok = QtGui.QInputDialog.getInteger(self,
        "How many bytes?", "Count", 0x4000, 0, 0xffff)
             
    if not ok:
        self.__logit( "aborted, no count given." )
        return

    self.bmf.sendPullFile(filename,basaddress,count)

  def sendfile(self):
    """
       GUI element to send file data to the BMF peer.  This is done using intel hex format binary transfers.
       each intel hex record is limited 24 bytes long.  The maximum data payload is 16 bytes.
       frames are padded to the length using ASCII NUL's and a single ASCII LF for the last character.

       if the filename chosen ends in .hex, then the file is read as an ASCII rendition of intel hex format, converted
       into binary, and sent (assumed to be correctly formatted intel hex.)

       If the file chosen ends with some other suffix, it is read as binary data.  The user is prompted for a start
       memory location, and then the data is send as chunks in intel-hex format.
       
    """
    filename = QtGui.QFileDialog.getOpenFileName(self, 
                  "File to Send", QtCore.QDir.currentPath())

    self.__logit( "sending file: %s" % filename )

    if filename == None:
        self.__logit( "aborted" )
    else:
         if (str(filename[-4:]).lower() == '.hex'):
              self.bmf.sendbulkhex(str(filename))
         else:
              baseaddress, ok = QtGui.QInputDialog.getInteger(self,
                   "Où placer les données", "Addresse", 0x4000, 0, 0xffff)
              if ok:
                self.bmf.sendbulkbin(str(filename),baseaddress)


  def __initKP1(self):
    """
        initialize keypad 1.
    """

    self.kp1 = QtGui.QWidget()
    self.kp1.setObjectName("Keypad 1")

    self.kp1.dock = QtGui.QDockWidget("Numbers",self)
    self.kp1.dock.setAllowedAreas( QtCore.Qt.AllDockWidgetAreas )
    self.kp1.dock.setWidget(self.kp1)

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

    #self.tab.addTab(self.kp1,"Numbers")
    self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.kp1.dock)
    self.viewMenu.addAction(self.kp1.dock.toggleViewAction())


  def __initKP2(self):
    """
        initialize keypad 2.
    """

    self.kp2 = QtGui.QWidget()
    self.kp2.setObjectName("Commands")

    self.kp2.dock = QtGui.QDockWidget("Command Keypad",self)
    self.kp2.dock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas )
    self.kp2.dock.setWidget(self.kp2)

    kp2layout=QtGui.QGridLayout(self.kp2)

    self.kp2.nw = self.__button(u'\u2196', self.kp2, self.__sendkey)
    kp2layout.addWidget(self.kp2.nw,0,0)

    self.kp2.up = self.__button(u'\u2191', self.kp2, self.__sendkey)
    kp2layout.addWidget(self.kp2.up,0,1)

    self.kp2.ne = self.__button(u'\u2197', self.kp2, self.__sendkey)
    kp2layout.addWidget(self.kp2.ne,0,2)

    self.kp2.left = self.__button(u'\u2190', self.kp2, self.__sendkey)
    kp2layout.addWidget(self.kp2.left,1,0)

    self.kp2.stop = self.__button('Stop', self.kp2, self.__sendkey )
    kp2layout.addWidget(self.kp2.stop,1,1)

    self.kp2.right = self.__button(u'\u2192', self.kp2, self.__sendkey)
    kp2layout.addWidget(self.kp2.right,1,2)

    self.kp2.sw = self.__button(u'\u2199', self.kp2, self.__sendkey)
    kp2layout.addWidget(self.kp2.sw,2,0)

    self.kp2.down = self.__button(u'\u2193', self.kp2, self.__sendkey)
    kp2layout.addWidget(self.kp2.down,2,1)

    self.kp2.se = self.__button(u'\u2198', self.kp2, self.__sendkey)
    kp2layout.addWidget(self.kp2.se,2,2)

    #self.tab.addTab(self.kp2,"Commands")
    self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.kp2.dock)
    self.viewMenu.addAction(self.kp2.dock.toggleViewAction())



  def __initKP3(self):
    """
        initialize keypad 3.
    """

    self.kp3 = QtGui.QWidget()
    self.kp3.setObjectName("Other Com")

    self.kp3.dock = QtGui.QDockWidget("Keypad 3",self)
    self.kp3.dock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas )
    self.kp3.dock.setWidget(self.kp3)

    kp2layout=QtGui.QGridLayout(self.kp3)


    self.kp3.plus = self.__button('+', self.kp3, self.__sendkey)
    kp2layout.addWidget(self.kp3.plus,0,0)

    self.kp3.speed = self.__button('Speed', self.kp3, self.__sendkey)
    kp2layout.addWidget(self.kp3.speed,0,1)

    self.kp3.minus = self.__button('-', self.kp3, self.__sendkey)
    kp2layout.addWidget(self.kp3.minus,0,2)

    self.kp3.hilo = self.__button('Hi/Lo', self.kp3, self.__sendToggleKey)
    kp2layout.addWidget(self.kp3.hilo,1,0)

    self.kp3.origin = self.__button('Origin', self.kp3, self.__sendkey)
    kp2layout.addWidget(self.kp3.origin,1,1)

    self.kp3.send = self.__button('Send', self.kp3, self.sendfile)
    kp2layout.addWidget(self.kp3.send,1,2)

    self.kp3.ss = self.__button('Start/Stop', self.kp3, self.__sendToggleKey)
    kp2layout.addWidget(self.kp3.ss,2,0)

    self.kp3.cd = self.__button( u'\u21e7', self.kp3, self.__sendkey)
    kp2layout.addWidget(self.kp3.cd,2,0)

    self.kp3.cd = self.__button( u'\u21e9', self.kp3, self.__sendkey)
    kp2layout.addWidget(self.kp3.cd,2,1)

    self.kp3.cd = self.__button('Mark', self.kp3, self.__sendkey)
    kp2layout.addWidget(self.kp3.cd,2,2)

    #self.tab.addTab(self.kp3,"Commands")
    self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.kp3.dock)
    self.viewMenu.addAction(self.kp3.dock.toggleViewAction())

  def __guiupdate(self):
    """
      gui refresh routine, called very often, but limits actual refresh frequency.
      For example, at frequency limit of every 0.1 seconds... on a 1 GHz machine, has about 100 million clocks to 
      do something useful !

      When it does decide to refresh, it brings the GUI uptodate with all the elements that were updated separately.
      between gui updates, raw data structures with no gui impact are updated (much more efficient.)
    """
    global gui_update_total_time
    global gui_update_total_count
    global gui_update_next_time
    
    gustart=time.time()
    if gustart < gui_update_next_time:
        return

    if self.connected:
        if self.bmf.updateReceived & bmf.FLAG_UPDATE_LOG:
           self.log.logUpdate()
        if self.bmf.updateReceived & bmf.FLAG_UPDATE_COUNTER:
           self.updateGUICounters()
        if self.bmf.updateReceived & ( bmf.FLAG_UPDATE_STRING | bmf.FLAG_UPDATE_COUNTER ):
           self.charDisplayWindow.update()
        if self.bmf.updateReceived & bmf.FLAG_UPDATE_LEDS:
           self.updateLEDS()
        if self.bmf.updateReceived & bmf.FLAG_UPDATE_LABELS:
           self.updateLabels()
        self.bmf.updateReceived = 0
    else:
        self.log.logUpdate()
 
    self.statusBar().showMessage(self.msg)

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

    duration=time.time()-gustart
    gui_update_total_time += (time.time()-gustart)
    gui_update_total_count+=1
    gui_update_average=1.0*gui_update_total_time/gui_update_total_count

    # updating > 10 times a second is a waste of time, since human requires order of 150 - 250 ms. to recognize a number
    # http://en.wikipedia.org/wiki/Mental_chronometry , so set a minimum interval of 100 ms. If computer is too slow,
    # may require lengthening.  2 comes from saying computer should spend at least half the time doing something else,
    # like reading the serial port...

    gui_update_next_time += max(0.1,2*gui_update_average)
    if ( gui_update_total_count % 300 ) == 100:
       self.__logit("guiupdate: this one took: %f" % duration )
       self.__logit("guiupdate took: total_time=%f, count=%d, average=%.5f" % \
              ( gui_update_total_time, gui_update_total_count, gui_update_average ))


  def __routineUpdate(self):
    """
      time triggerred update.
          Polls i/o to see of we have received anything to process.
          trigger a conditional screen update.

    """

    # try to avoid updates piling on each other...
    if self.update_in_progress:
       return
    self.update_in_progress=True

    if self.connected:
        self.bmf.readpending(self.__guiupdate)

    self.__guiupdate()

    self.update_in_progress=False

        

  def __otherPort(self):
    """
        post a dialog to allow the user to use a name not presented in the initial list of ports.
        the other port is then added to the list, and selected.
    """
    op, ok = QtGui.QInputDialog.getText(self,"Other Port", "Port Address")
    if ok:
      last = self.stg.portselect.count()    
      self.stg.portselect.addItem(op)    
      self.stg.portselect.setCurrentIndex(last)
    

  def __initSerialPortSettings(self):
    """
        initialize settings keypad.

    """
    self.stg = QtGui.QWidget()
    self.stg.setObjectName("Settings")

    self.stg.dock = QtGui.QDockWidget("Settings",self)
    self.stg.dock.setAllowedAreas( QtCore.Qt.AllDockWidgetAreas )
    self.stg.dock.setWidget(self.stg)

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
    speeds=[ "300","900","1200","4800","9600","19200","38400","57600","115200" ]
    self.stg.bps.addItems(speeds)    
    if (self.bmf != None) and (self.bmf.dev != None):
        self.stg.bps.setCurrentIndex( speeds.index(str(self.bmf.speed)))
    else:
        self.stg.bps.setCurrentIndex( 6 ) # ought to be 38400

    self.stg.bpslabel.setBuddy(self.stg.bps)
    stglayout.addWidget(self.stg.bpslabel,1,0,1,1)
    stglayout.addWidget(self.stg.bps,1,2,1,3)

    # Flags
    self.stg.sim = QtGui.QRadioButton('write file', self.stg)
    self.stg.sim.setAutoExclusive(False)
    stglayout.addWidget(self.stg.sim,2,0)
    self.stg.noack = QtGui.QRadioButton('No Ack', self.stg)
    self.stg.noack.setAutoExclusive(False)
    stglayout.addWidget(self.stg.noack,2,1)
    self.stg.netsrv = QtGui.QRadioButton('Net Server', self.stg)
    self.stg.netsrv.setAutoExclusive(False)
    stglayout.addWidget(self.stg.netsrv,2,2)
    self.stg.netcli = QtGui.QRadioButton('Net Client', self.stg)
    self.stg.netcli.setAutoExclusive(False)
    stglayout.addWidget(self.stg.netcli,2,3)

    self.stg.connect = self.__button('Connect', self.stg, self.__connect)
    stglayout.addWidget(self.stg.connect,5,0,1,2)
    self.stg.connect.setAutoRepeat(False)

    self.stg.disconnect = self.__button('DisConnect', self.stg, self.__disconnect)
    stglayout.addWidget(self.stg.disconnect,5,2,1,2)
    self.stg.disconnect.setAutoRepeat(False)


    #self.tab.addTab(self.stg,"Settings")
    self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.stg.dock)
    self.viewMenu.addAction(self.stg.dock.toggleViewAction())
    self.stg.dock.hide()

  def __initLEDS(self):

    self.leds = QtGui.QWidget()
    self.leds.setObjectName("LEDS")

    self.leds.dock = QtGui.QDockWidget("LEDS",self)
    self.leds.dock.setAllowedAreas( QtCore.Qt.AllDockWidgetAreas )
    self.leds.dock.setWidget(self.leds)

    ledlayout=QtGui.QVBoxLayout(self.leds)

    self.leds.led = []
    self.leds.led.append(QtGui.QRadioButton('Home ZZ', self.leds))
    self.leds.led[0].setAutoExclusive(False)
    ledlayout.addWidget(self.leds.led[0])
    self.leds.led.append(QtGui.QRadioButton('Step Off', self.leds))
    self.leds.led[1].setAutoExclusive(False)
    ledlayout.addWidget(self.leds.led[1])
    self.leds.led.append( QtGui.QRadioButton('Heating', self.leds) )
    self.leds.led[2].setAutoExclusive(False)
    ledlayout.addWidget(self.leds.led[2])
    self.leds.led.append( QtGui.QRadioButton('Part Time', self.leds) )
    self.leds.led[3].setAutoExclusive(False)
    ledlayout.addWidget(self.leds.led[3])


    self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.leds.dock)
    self.viewMenu.addAction(self.leds.dock.toggleViewAction())

  def updateLabels(self):
    """
       update the GUI with labels from bmf
    """
    for i in xrange(0,4):
        self.leds.led[i].setText(self.bmf.labels[i])

    self.counters.qw.al.setText(self.bmf.labels[4])
    self.counters.qw.axcl.setText(self.bmf.labels[5])
    self.counters.qw.aycl.setText(self.bmf.labels[6])
    self.counters.qw.azcl.setText(self.bmf.labels[7])
    self.counters.qw.rl.setText(self.bmf.labels[8])
    self.counters.qw.rxcl.setText(self.bmf.labels[9])
    self.counters.qw.rycl.setText(self.bmf.labels[10])
    self.counters.qw.rzcl.setText(self.bmf.labels[11])


  def updateLEDS(self):
    """
       read the led flag settings from the bmf, apply to GUI.
    """
    for i in xrange(0,3):
        self.leds.led[i].setChecked((int(self.bmf.leds)&(1<<i)))

  def __initTesting(self):
    """
        initialize Testing keypad.

    """

    self.tst = QtGui.QWidget()
    self.tst.setObjectName("Testing")

    self.tst.dock = QtGui.QDockWidget("Testing",self)
    self.tst.dock.setAllowedAreas( QtCore.Qt.AllDockWidgetAreas )
    self.tst.dock.setWidget(self.tst)

    tstlayout=QtGui.QGridLayout(self.tst)

    self.tst.hexlabel = QtGui.QLabel("Hex:")
    tstlayout.addWidget(self.tst.hexlabel,0,0)
    self.tst.hexedit = QtGui.QLineEdit()
    tstlayout.addWidget(self.tst.hexedit,0,1)


    self.tst.dt = self.__button('Send Hex', self.tst, self.__sendhex)
    tstlayout.addWidget(self.tst.dt,1,0)

    self.tst.dt = self.__button('DisplayTest', self.tst, self.exercise)
    tstlayout.addWidget(self.tst.dt,2,0)

    self.tst.dc = self.__button('Clear', self.tst, self.__clear)
    tstlayout.addWidget(self.tst.dc,2,1)

    #self.tab.addTab(self.tst,"Testing")
    self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.tst.dock)
    self.viewMenu.addAction(self.tst.dock.toggleViewAction())
    self.tst.dock.hide()



  def __exit( self ):
     self.__disconnect()
     self.log.close()
     self.counters.close()
     self.logfile.close()
     self.close()
     
  def __clear(self):
     """
        clear the character addressable display.
     """
     self.charDisplay.clear()
     if self.connected:
        self.bmf.updateReceived=0xff
     self.charDisplayWindow.update()
     

  def exercise( self ):
     """
        test the character addressable display by drawing in random ways.

     """
     self.charDisplay.writeStringXY(0,0, "0123456789012345678901234567890123456789012345678")
     self.charDisplay.writeStringXY(self.exx,self.exy,"Hello")

     self.exy=random.randint(0,self.charDisplay.rows-1)
     self.exx=random.randint(0,self.charDisplay.columns-1)

     #if self.connected:
     #    self.bmf.counters[0]=1000*self.exx
     #    self.bmf.counters[1]=1000*self.exy
     #    self.bmf.updateReceived=True
     #else:

     self.charDisplayWindow.update()

      

  def __init__(self, bmf=None, parent=None):

     QtGui.QMainWindow.__init__(self)
 
     self.exx=4
     self.exy=4

     self.msg = "almost ready?"
     self.connected = (bmf != None)

     exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)

     self.menubar = self.menuBar()
     file = self.menubar.addMenu('&File')
     file.addAction(exit)

     self.EditMenu = self.menubar.addMenu("&Edit")
     self.viewMenu = self.menubar.addMenu("&View")

     self.menuBar().addSeparator()
     help = self.menubar.addMenu('&Help')
     
     self.log=LogDisplay.LogWindow(self.__logUI,self)
     #self.__logit("Startup...")

     self.bmf=bmf


     self.charDisplay=CharDisplay.CharDisplay(self.__logit) 
     self.charDisplayWindow=CharDisplayWindow.CharDisplayWindow(self.__logit,self.charDisplay)

     if self.connected:
           self.bmf.display = self.charDisplay

     self.counters=CounterDisplay.CounterDisplay(self)

     self.setMinimumSize(900, 500)
     self.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )

     self.setWindowTitle('BMF - Panel')
     exit.setShortcut('Ctrl+Q')
     exit.setStatusTip('Exit application')
     self.connect(exit, QtCore.SIGNAL('triggered()'), self.__exit)

     self.mainwin = QtGui.QWidget()
     self.mainlayout= QtGui.QHBoxLayout() 

     self.mainlayout.addWidget(self.counters,1)
     self.mainlayout.addWidget(self.log,5)

     self.__initLEDS()     
     self.__initKP3()     
     self.__initKP2()     
     self.__initKP1()     
     self.__initSerialPortSettings()     
     self.__initTesting()     
   
     #self.show()
     self.setCentralWidget(self.charDisplayWindow)

     self.update_in_progress=False
     self.updateTimer = QtCore.QTimer(self)
     self.connect(self.updateTimer, QtCore.SIGNAL("timeout()"), self.__routineUpdate )
     self.updateTimer.setInterval(50)
     self.updateTimer.start()

     self.logfile=open("bmf.log","w")
     self.__logit("Ready")
