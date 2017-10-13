"""
xbee.py
By Calin Ciordas, 2014
"""

import serial, struct
from zigbee import *

class XBee:
    """
    """

    # header (pre-compiled for performance reasons)
    unpacker = struct.Struct(">BH")
    
    def __init__(self):
        pass

    def connect(self, name):
        self.cxn = serial.Serial(name)

    def send_frame(self, frame):
        self.cxn.write(frame.pack())
                
    def read_frame(self):
        header  = self.cxn.read(3)
        SOM, sz = XBee.unpacker.unpack_from(header)
        payload = self.cxn.read(sz)
        chksum  = self.cxn.read(1)
    
        frametype = struct.unpack(">B", payload[0])[0]        
        return ZigBeeAPIFrames[frametype](payload, chksum)
    
