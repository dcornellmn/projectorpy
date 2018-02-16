#!/usr/bin/env python3
#
# Serial projector control interface
#
import serial
import time
import logging

class Projector:
    """ Enables interaction with projector over serial """
    
    def __init__(self, port, timeout=2, baud=9600):
        self._logger = logging.getLogger(__name__)
        self._serial = serial.serial_for_url(port, do_not_open=True)
        self._serial.baud_rate = baud
        self._serial.timeout = timeout
        
    def __del__(self):
        if self._serial.is_open:
            self._serial.close() 
    
    def open(self):
        """ open serial port connection to projector """
        if self._serial.is_open:    # close and re-open if already open
            self._serial.close()
        self._serial.open() # open the port
        time.sleep(1)   # allow the port to settle before returning
        self._logger.debug('Serial port opened')
        
    def ensure_open(self):
        """ open serial connection if it is not already open """
        if not self._serial.is_open:
            self.open()
        
    
    def close(self):
        """ close serial port """
        self._serial.close()
        self._logger.debug('Serial port closed')

    
    def send(self, command):
        """ Send a bytestring command to the projector. """
        cmd_bytes = command.encode(encoding='ascii')
        self.ensure_open()
        
        # clear buffers and send our command
        self._serial.reset_input_buffer()
        self._serial.reset_output_buffer()
        self._serial.write(cmd_bytes)
        self._logger.debug('Serial wrote %d bytes', len(cmd_bytes))
    
    def receive(self, expect=1, wait=False):
        """ Deprecated. Receive input from the projector, optionally waiting for 'expect' characters """
        self._logger.warning('Use of deprecated method Projector.receive(). Replace with Projector.readline().')
        
        if expect < 1:
            expect = 1
        
        self.ensure_open()
        
        bytes = self._serial.read(expect)
        
        # if we were told to wait (block), keep looping through the read until 
        # we've gotten at least the requested number of bytes, regardless of timeout
        while (self._serial.in_waiting or wait) and len(bytes) < expect:
            bytes += self._serial.read(expect - len(bytes))
        
        return bytes.decode(encoding='ascii', errors='ignore')
    
    def readline(self, blocking=False):
        """ Read input until EOL. Does not return the EOL character(s). """
        
        # Ensure our serial port has been opened
        self.ensure_open()
        
        # Ensure that the blocking parameter and the PySerial timeout are compatible
        prev_timeout = -1
        if blocking and self._serial.timeout != 0:
            prev_timeout = self._serial.timeout
            self._serial.timeout = 0
        elif not blocking and self._serial.timeout == 0:
            prev_timeout = 0
            self._serial.timeout = 1
        
        # Pythonic do-while loop...
        # Attempt at least one read() - subject to timeout unless blocking==True
        # If the read included an EOL character (CR or LF), break out of the loop
        # Continue looping while there is input in the buffer, or indefinitely
        # if blocking==True
        self._logger.debug('Beginning Projector.readline() loop. blocking=%s; timeout=%d', blocking, self._serial.timeout)
        resp = bytearray()
        more = True
        while more:
            try:
                last = self._serial.read()
            except:
                logging.exception('Caught exception in read loop.')
            else:
                if b'\r' in last or b'\n' in last:
                    if len(last) > 1:
                        # if we got more than the 1 byte we requested, save
                        # anything before the first CR or LF
                        eol = last.find(b'\r')
                        if eol == -1:
                            eol = last.find(b'\n')
                        if eol > 0 and eol < len(last):
                            resp += last[0:eol]
                    break
                resp += last
            finally:
                more = self._serial.in_waiting or blocking
        self._logger.debug('Projector.readline() read loop returned %d bytes.', len(resp))
        
        # Restore the original timeout if we changed it above
        if prev_timeout >= 0:
            self._serial.timeout = prev_timeout
        
        # Convert the bytearray response to a string and return it
        rv = resp.decode(encoding='ascii', errors='ignore')
        self._logger.debug('Projector.readline() finished. resp=%s', rv)
        return rv
