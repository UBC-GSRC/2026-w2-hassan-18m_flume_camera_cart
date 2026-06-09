# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 13:10:14 2024

@author: Katrin Tanner
"""

import struct
import socket  
import time

from Network import Axis
from Network import Controller

class BinaryCommunication:
  
    GETLONG = '88'
    GETIEEE32 = '8a'
    SETLONG = '89'
    SETIEEE32 = '8b'
    
    def __init__(self): 
#defines function cart and sets first input to be the IP address, second input to be the port used
        self.port = 5002
        self.s = None
        self.msg = bytearray()
        
    def connect(self, controller:Controller):                                              #function to connect to cart
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #sets the address to be IPV4 and the connection to be TCP protocal
        self.s.connect((controller.ip, self.port))                        #calling connect uses the inputs provided when calling Cart
   
    def disconnect(self, controller:Controller):
        self.s.close()

    def enableDrive(self, axis:Axis):                                  #function to connect to cart
        if axis.Number==0:
            self.msg = bytes.fromhex('1c112100')
        self.s.send(self.msg)                                 #sends the command as a byte to the controller for Port 5002
        time.sleep(0.05)

    def disableDrive(self, axis:Axis):                                 # function to send command to cart
        if axis.Number==0:
            self.msg = bytes.fromhex('1d112100')
        self.s.send(self.msg)                                 #sends the command as a byte to the controller for Port 5002
        time.sleep(0.05)

    def setBit(self, axis:Axis, bitNumber:int):
        self.msg = bytearray.fromhex('1C')                     # header ID = 0x1C
        paramhex = format(bitNumber, 'x')
        while len(paramhex) <= 3:                           # two byte parameter index, if the parameter is to small it has to be filled up
            paramhex = '0'+ paramhex                        
        paramhexlobf = paramhex[2:] + paramhex[:2]          # low order byte first so bytes have to be swapt
        self.msg += bytearray.fromhex(paramhexlobf)
        self.s.send(self.msg)                                 #sends the command as a byte to the controller for Port 5002
        time.sleep(0.05)
    
    def clrBit(self, axis:Axis, bitNumber:int):
        self.msg = bytearray.fromhex('1D')                     # header ID = 0x1D
        paramhex = format(bitNumber, 'x')
        while len(paramhex) <= 3:                           # two byte parameter index, if the parameter is to small it has to be filled up
            paramhex = '0'+ paramhex                        
        paramhexlobf = paramhex[2:] + paramhex[:2]          # low order byte first so bytes have to be swapt
        self.msg += bytearray.fromhex(paramhexlobf)
        self.s.send(self.msg)                                 #sends the command as a byte to the controller for Port 5002
        time.sleep(0.05)

    def move(self, axis:Axis, pos, Movement:str ='r', VarType:str ='IEEE32', vel = 0, acc = 0):
        self.msg = bytearray.fromhex('04')                      # 0x04=headercode00, 
        
        HeaderCode0 ='01001110'                             # default bits to be set (refer to ACR-Programmers-Guide p.254)
        if vel != 0:                                        # set bit if velo
            HeaderCode0 = HeaderCode0[:3] + '1' + HeaderCode0[4:] 
        if acc != 0:
            HeaderCode0 = HeaderCode0[:2] + '1' + HeaderCode0[3:] 
        HeaderCode0hex = format(int(HeaderCode0,2), 'x')    # conversion to hex number
        if len(HeaderCode0hex)==1:                          # ad additional 0 if hex number to short
            HeaderCode0hex = '0' + HeaderCode0hex
        self.msg += bytearray.fromhex(HeaderCode0hex)       # ad HeaderCode to msg
        
        HeaderCode1 = '00011000'
        HeaderCode1hex = format(int(HeaderCode1,2), 'x')
        if len(HeaderCode1hex)==1:
            HeaderCode1hex = '0' + HeaderCode1hex
        self.msg += bytearray.fromhex(HeaderCode1hex)
        
        HeaderCode2 = '00000001'
        HeaderCode2hex = format(int(HeaderCode2,2), 'x')
        if len(HeaderCode2hex)==1:
            HeaderCode2hex = '0' + HeaderCode2hex
        self.msg += bytearray.fromhex(HeaderCode2hex) 
        
        HeaderCode3 = '00000000'
        if Movement == 'r':                             # set bit for relative movement in asked
            HeaderCode3 = HeaderCode3[:7] + '1' 
        if VarType=='IEEE32':                           # set variable type float or long
            HeaderCode3 = HeaderCode3[:5] + '1' + HeaderCode3[6:] 
        HeaderCode3hex = format(int(HeaderCode3,2), 'x')
        if len(HeaderCode3hex)==1:
            HeaderCode3hex = '0' + HeaderCode3hex
        self.msg += bytearray.fromhex(HeaderCode3hex) 
        while len(self.msg) % 4 != 0:                       # message consists of 4 bytes
            self.msg += bytearray.fromhex('00')
        
        if VarType == 'long':
            Data3 = format(pos, 'x')                            # position data long to hex
        if VarType == 'IEEE32':
            Data3 = hex(struct.unpack('<I', struct.pack('<f', pos))[0])
            Data3 = Data3[2:]
        if len(Data3)%8 != 0:
            Data3 = '0' + Data3
        Data3 = Data3[6:] + Data3[4:6] + Data3[2:4] + Data3[:2] 
        self.msg += bytearray.fromhex(Data3)
        
        while len(self.msg) % 4 != 0:                       # amount of bytes have to be devidable by 4. If the message is for example 6 byte long 2 additional 0x00 bytes have to ge added to the end.
            self.msg += bytearray.fromhex('00')
            
        self.s.send(self.msg)                                 #sends the command as a byte to the controller for Port 5002
        time.sleep(0.05)
     
    def requestBit(self, axis:Axis, param:int, bitnr: int):
        self.msg = bytearray.fromhex('00')
        self.msg += bytearray.fromhex('88')
        paramhex = format(param, 'x')
        while len(paramhex) <= 3:                           # two byte parameter index, if the parameter is to small it has to be filled up
            paramhex = '0'+ paramhex                        
        paramhexlobf = paramhex[2:] + paramhex[:2]          # low order byte first so bytes have to be swapt
        self.msg += bytearray.fromhex(paramhexlobf)
        self.s.send(self.msg)                                 #sends the command as a byte to the controller for Port 5002
        
        respons = self.s.recv(1024)

        valueBytes = respons[4:]                                # seperate Bytes containing Message
        valueByteshex = valueBytes.hex()  

        relevantByte = int((bitnr - bitnr % 8) / 8)
        valueBytes = valueByteshex[(relevantByte*2):(relevantByte*2+2)]                                # extract Byte containing Bit
        valueBytesint = int(valueBytes, 16)                                                        # convert hex to int
        # print (relevantByte)
        #valueBytesbin = format(valueBytesint, 'b')                                                 # convert int to binary
        
        relevantBit = bitnr % 8
        bitshift = (valueBytesint >> (relevantBit-1))

        value = bitshift % 2     #int.from_bytes(valueBytes).bit_length()
        return value
    
    def requestParameter(self, axis:Axis, param:int, VarType:str = 'IEEE32'):
        self.msg = bytearray.fromhex('00')
        if VarType == 'IEEE32':
            self.msg += bytearray.fromhex('8a')
        if VarType == 'long':
            self.msg += bytearray.fromhex('88')
        paramhex = format(param, 'x')
        while len(paramhex) <= 3:                           # two byte parameter index, if the parameter is to small it has to be filled up
            paramhex = '0'+ paramhex                        
        paramhexlobf = paramhex[2:] + paramhex[:2]          # low order byte first so bytes have to be swapt
        self.msg += bytearray.fromhex(paramhexlobf)
        request = self.msg.hex()
        self.s.send(self.msg)                                 #sends the command as a byte to the controller for Port 5002
        
        respons = self.s.recv(1024)
        controlBytes = respons[:4]                              # seperate HeaderID, PacketID and Parameter Index to know what parameter is contained
        controlByteshex = controlBytes.hex()                # convert bytes to hexstring
        parameterType = controlByteshex[2:4]
        parameterIndexhex = controlByteshex[6:] + controlByteshex[4:6]
        parameterIndex = int(parameterIndexhex,16)
        
        valueBytes = respons[4:]                                # seperate Bytes containing Message
        valueByteshex = valueBytes.hex()                    # convert bytes to hexstring
        valuehex = valueByteshex[6:] + valueByteshex[4:6] + valueByteshex[2:4] + valueByteshex[:2]      # message arrives low order byte first, to read out the value low order byte has to be last
        
        if parameterType == '88':                               # conversion for parametertype "long"
            value = int(valuehex,16)                            # conversion to readable integer value
        
        if parameterType == '8a':                               # conversion for parameter type "IEEE" (float)
            value = struct.unpack('!f', bytes.fromhex(valuehex))[0]      #convert hex to float
        
        return parameterIndex, value
        
    def setParameter(self, axis:Axis, param:int, value, VarType:str = 'IEEE32'):
        self.msg = bytearray.fromhex('00')
        if VarType == 'IEEE32':
            self.msg += bytearray.fromhex('8b')
        if VarType == 'long':
            self.msg += bytearray.fromhex('89')
        paramhex = format(param, 'x')
        while len(paramhex) <= 3:                           # two byte parameter index, if the parameter is to small it has to be filled up
            paramhex = '0'+ paramhex                        
        paramhexlobf = paramhex[2:] + paramhex[:2]          # low order byte first so bytes have to be swapt
        self.msg += bytearray.fromhex(paramhexlobf)

        if VarType == 'long':
            Data3 = format(value, 'x')                            # position data long to hex
        if VarType == 'IEEE32':
            Data3 = hex(struct.unpack('<I', struct.pack('<f', value))[0])
            Data3 = Data3[2:]
        if len(Data3)%8 != 0:
            Data3 = '0' + Data3
        Data3 = Data3[6:] + Data3[4:6] + Data3[2:4] + Data3[:2] 
        self.msg += bytearray.fromhex(Data3)
        
        while len(self.msg) % 4 != 0:                       # amount of bytes have to be devidable by 4. If the message is for example 6 byte long 2 additional 0x00 bytes have to ge added to the end.
            self.msg += bytearray.fromhex('00')
        self.s.send(self.msg)                                 #sends the command as a byte to the controller for Port 5002
        time.sleep(0.05)