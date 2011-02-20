BMF, the bi-directional machining facility is a PC-based interface
for embedded controllers.  the main interface, obmf.py, communicates
with an embedded system over a serial interface.  

The protocol used for data exchange is described in detail in PROTOCOL.txt
In general, it consists of OpCodes (single byte commands) followed by the 
arguments for each command, and lines usually terminated by a line feed 
character.  The exception to this is that intel-hex format is used to 
transfer file data.  The protocol is symmetrical in that either the PC or 
the embedded host can send commands.


Requirements
------------

You need a PC (windows or Linux), running python ( 2.5 < x < 3 ) and QT
bindings (pyQT4, pyside not tested yet.), and an embedded processor, on which
you have implemented the protocol, and a serial interface connection between 

The serial interface can be either via a hardware serial port, a port 
connected via a USB-serial cable, or even connection via a terminal-server 
over a network connection, wired or wireless.   The application should 
auto-discover all local serial ports, but remote ports would have to be
entered manually.

Startup
-------

open a command window, navigate to the directory containing obmf.py,
then type:

python ./obmf.py



Testing Without a Device
------------------------

To try out the software without a device that implements the protocol, there 
is an emulation mode which replaces the actual device by a software 
implementation.  One can start up the tool in a embedded processor emulation 
mode, like so::

	python obmf.py --port="localhost:5050" --flags=4 read

which reads the commands sent to it by a client connecting to the
given port.  A client is then started up in a conventional way::

        python obmf.py --port="localhost:5050" --flags=8 view

You can do the same with a nullmodem cable:
	python obmf.py --port=/dev/ttyUSB1 --speed=115200 read
	python obmf.py --port=/dev/ttyUSB0 --speed=115200 view

Under View->Testing, one can bring up the arbitrary hex code dialog, and
then send the magic sequence AA,A (0xAA,0xA) which will trigger code in
the emulator to send many commands, putting strings on the screen, updating
counters, and setting key labels.   This demonstrates the results which
the embedded processor is able to perform.



