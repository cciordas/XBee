"""
ATCommands.py
By Calin Ciordas, 2014

This module implements the AT commands supported by the XBee/XBee-PRO modules.
Based on the Digi document "XBee/XBee-PRO ZB RF Modules" downloaded
from 'http://ftp1.digi.com/support/documentation/90000976_V.pdf'.
"""

import abc, struct


# ----- ACommand ----- #

class ATCommand(object):
    """
    Abstract class representing a generic
    Base of the hierarchy of classes describing such commands.
    """    
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, command, param, name, category, descr):
        """
        @command  two letter command representation (w/o the 'AT' prefix)
        @param    None when querying a register, else the value to save in the register
        @name     explicit command name
        @category category to which the command belongs
        @descr    command descripton
        """        
        self.command  = command
        self.param    = param
        self.name     = name
        self.category = category
        self.descr    = descr
        
    def describe(self):
        """
        Detailed description of the command instance.
        """        
        s  = "\n"
        s += " command:     " +          self.command  + "\n"
        s += " param:       " + "0x%x" % self.param    + "\n"
        s += " name:        " +          self.name     + "\n"
        s += " category:    " +          self.category + "\n"
        s += " description: " +          self.descr    + "\n"
        return s

    @abc.abstractmethod
    def pack(self):
        """ 
        Convert the two letter command code and the command parameter (if any)
        into binary format and pack the two chunks into one buffer.
        Return buffer to caller.
        """
        return


# ----------- DH ---------- #

class ATCommandDH(ATCommand):
    """
    DH - Destination Address High
    """

    command     = "DH"
    name        = "Destination Address High"
    category    = "Addressing"
    description = \
    """\n            
    Set/Get the upper 32 bits of the 64-bit destination address. 
    When combined with DL, it defines the 64-bit destination address for data transmission. 
    Special definitions for DH and DL include 0x000000000000FFFF (broadcast) and 0x0000000000000000 (coordinator).
    """

    # command packer (pre-compiled for performance reasons)
    packer   = struct.Struct(">2sI")

    # payload unpacker (pre-compiled for performance reasons)
    unpacker1 = struct.Struct(">B")
    unpacker2 = struct.Struct(">H")    
    unpacker4 = struct.Struct(">I")    
    
    def __init__(self, param):
        ATCommand.__init__(self,
                           ATCommandDH.command,
                           param,
                           ATCommandDH.name,
                           ATCommandDH.category,
                           ATCommandDH.description)

    def pack(self):
        return ATCommandDH.packer.pack(self.command, self.param)


# ----------- DL ---------- #

class ATCommandDL(ATCommand):
    """
    DL - Destination Address Low
    """
    
    command     = "DL"
    name        = "Destination Address Low"
    category    = "Addressing"
    description = \
    """\n            
    Set/Get the lower 32 bits of the 64-bit destination address. 
    When combined with DH, it defines the 64-bit destination address for data transmissions.
    Special definitions for DH and DL include 0x000000000000FFFF (broadcast) and 0x0000000000000000 (coordinator).
    """

    # command packer (pre-compiled for performance reasons)
    packer = struct.Struct(">2sI")

    # payload unpacker (pre-compiled for performance reasons)
    unpacker1 = struct.Struct(">B")
    unpacker2 = struct.Struct(">H")    
    unpacker4 = struct.Struct(">I")    
    
    def __init__(self, param):
        ATCommand.__init__(self,
                           ATCommandDL.command,
                           param,
                           ATCommandDL.name,
                           ATCommandDL.category,
                           ATCommandDL.description)
    
    def pack(self):
        return ATCommandDL.packer.pack(self.command, self.param)


# ----------- SH ---------- #

class ATCommandSH(ATCommand):
    """
    SH - Serial Number High
    """

    command     = "SH"
    name        = "Serial Number High"
    category    = "Diagnostics"
    description = \
    """\n            
    Used to read the high 32 bits of the RF module's unique IEEE 64-bit addresss.
    The module serial number is set at the factory and is read-only.
    """


# ----------- SL ---------- #

class ATCommandSL(ATCommand):
    """
    SL - Serial Number Low
    """
    
    command     = "SL"
    name        = "Serial Number Low"
    category    = "Diagnostics"
    description = \
    """\n            
    Used to read the low 32 bits of the RF module's unique IEEE 64-bit addresss.
    The module serial number is set at the factory and is read-only.
    """




    



    
# ========================= #

ATCommands = \
{
    "DH" : ATCommandDH,
    "DL" : ATCommandDL
}


def make_command(cmd, param):
    """
    Factory method; constructs instances of classes derived from ATCommand.

    @cmd   two letter command representation (w/o the 'AT' prefix)
    @param None when querying a register, else the value to save in the register
    """
    if ATCommands.has_key(cmd): return ATCommands[cmd](param)
    else:                       return None
        

def parse_command(cmd, payload):
    """
    Creates an ATCommand instance using binary data received from the radio module.
    @command two letter command representation (w/o the 'AT' prefix)
    @payload binary buffer storing data received from the module (frame specific data only, no SOM and size)
    """
    if ATCommands.has_key(cmd):
        offset  = 4                     # FrameType (1 byte) + FrameID (1 byte) + ATCommand (2 bytes)
        paramsz = len(payload) - offset

        if   paramsz == 1: param = ATCommands[cmd].unpacker1.unpack_from(payload, offset)[0]
        elif paramsz == 2: param = ATCommands[cmd].unpacker2.unpack_from(payload, offset)[0]
        elif paramsz == 4: param = ATCommands[cmd].unpacker4.unpack_from(payload, offset)[0]                
        
        return  ATCommands[cmd](param)
    else:
        return None
    
