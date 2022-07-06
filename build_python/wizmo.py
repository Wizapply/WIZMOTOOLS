# -*- coding: utf-8 -*-
# Import
from ctypes import *
import time, platform
from enum import IntEnum

# Status Define
class wizmoStatus(IntEnum):
    CanNotFindUsb = 0
    CanNotFindwizmo = 1
    CanNotCalibration = 2
    TimeoutCalibration = 3
    ShutDownActuator = 4
    CanNotCertificate = 5
    Initial = 6
    Running = 7
    StopActuator = 8
    CalibrationRetry = 9

# WIZMO Data Packet
class wizmoPacket(Structure):  
    _fields_ = [  
            ("axis1", c_float),
            ("axis2", c_float),
            ("axis3", c_float),
            ("axis4", c_float),
            ("axis5", c_float),
            ("axis6", c_float),
            ("speedAxis", c_float),  
            ("accelAxis", c_float),
            ("speedAxis4", c_float),  
            ("accelAxis4", c_float),
            ("roll", c_float),  
            ("pitch", c_float),  
            ("yaw", c_float),
            ("heave", c_float),  
            ("sway", c_float),  
            ("surge", c_float),
            ("rotationMotionRatio", c_float),  
            ("gravityMotionRatio", c_float),  
            ("commandSendCount", c_int),  
            ("commandStride", c_int),
            ("command", c_char*256)
            ]
  
    def __init__(self):  
        self.axis1 = 0.5  #default param
        self.axis2 = 0.5  
        self.axis3 = 0.5
        self.axis4 = 0.5
        self.axis5 = 0.5
        self.axis6 = 0.5
        self.speedAxis = 0.666
        self.accelAxis = 0.5
        self.speedAxis4 = 0.0	#not use
        self.accelAxis4 = 0.0	#not use
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.heave = 0.0
        self.sway = 0.0
        self.surge = 0.0
        self.rotationMotionRatio = 0.8
        self.gravityMotionRatio = 0.8
        self.commandSendCount = 0 

# Main Class
class wizmo():

    def __init__(self, verbose=False):
        libloadpath = ''
        if platform.system() == 'Windows':
            if platform.architecture()[0] == '64bit':
                libloadpath = './wizmo.dll'
            else:
                libloadpath = './wizmo32.dll'
        else:
            if platform.architecture()[0] == '64bit':
                libloadpath = './libwizmo.so'
            else:
                libloadpath = './libwizmo32.so'
        
        self.wizmolib = cdll.LoadLibrary(libloadpath)
        self.wizmoIsOpen = False
        self.verbose = verbose
        self.simplePacket = wizmoPacket()
        self.wizmoHandle -1
        if self.verbose: print ("LOADED WIZMO DLL.")

    def starter(self, appCode):
        self.starterAssign(appCode, serialAssign)

    def starterAssign(self, appCode, serialAssign):
        if self.wizmoIsOpen == True:
            return
        
        self.wizmoHandle = self.wizmolib.wizmoOpenSerialAssign(appCode.encode(), serialAssign.encode())
        if self.wizmoHandle >= 0:
            if self.verbose: print ("STARTED WIZMO.")
            time.sleep(1) #wait
            self.wizmoIsOpen = True
        else:
            if self.verbose: print("WIZMO OPEN ERROR!")

    def close(self):
        if self.wizmoIsOpen == False:
            return
    
        self.wizmolib.wizmoClose(self.wizmoHandle)
        self.wizmoIsOpen = False

    def updateBackLog(self):
        buf_res = ''
        size = self.wizmolib.wizmoBackLogDataAvailable();
        if(size > 0) :
            self.wizmolib.wizmoGetBackLog.restype = c_int
            self.wizmolib.wizmoGetBackLog.argtypes = (c_char_p, c_int)
        
            p = create_string_buffer(size)
            iRef = self.wizmolib.wizmoGetBackLog(p, size)
            if iRef > 0:
                bufferString = p.value.decode()
                buf_res += bufferString.rstrip("\n")

        if self.verbose and buf_res != '': print(buf_res)
        return buf_res

    def updateState(self):
        stateNo = self.wizmolib.wizmoGetState(self.wizmoHandle)

        #State OK
        if stateNo <= wizmoStatus.Initial:
            return False
        return True

    def getStatus(self):
        return self.wizmolib.wizmoGetState(self.wizmoHandle)

    def isRunning(self):
        return self.wizmolib.wizmoGetState(self.wizmoHandle) == Running

    def simplePoseUpdate(self, roll, pitch, yaw, heave, sway, surge):
        if self.wizmoIsOpen == False:
            return

        self.simplePacket.roll = roll
        self.simplePacket.pitch = pitch
        self.simplePacket.yaw = yaw
        self.simplePacket.heave = heave
        self.simplePacket.sway = sway
        self.simplePacket.surge = surge
        self.wizmolib.wizmoWrite(self.wizmoHandle, byref(self.simplePacket))

    def simplePoseUpdateTuple(self, value):
        if self.wizmoIsOpen == False:
            return
        
        if len(value) < 6:
            return
        
        self.simplePacket.roll = value[0]
        self.simplePacket.pitch = value[1]
        self.simplePacket.yaw = value[2]
        self.simplePacket.heave = value[3]
        self.simplePacket.sway = value[4]
        self.simplePacket.surge = value[5]
        self.wizmolib.wizmoWrite(self.wizmoHandle, byref(self.simplePacket))

    def simpleMotionRatioUpdate(self, rotation, gravity):
        if self.wizmoIsOpen == False:
            return
        
        self.simplePacket.rotationMotionRatio = rotation
        self.simplePacket.gravityMotionRatio = gravity
        self.wizmolib.wizmoWrite(self.wizmoHandle, byref(self.simplePacket))

    def simpleMotionPowerUpdate(self, accel, speed):
        if self.wizmoIsOpen == False:
            return
        
        self.simplePacket.accelAxis123 = accel
        self.simplePacket.speedAxis123 = speed
        self.wizmolib.wizmoWrite(self.wizmoHandle, byref(self.simplePacket))

    def packetUpdate(self, packet):
        if self.wizmoIsOpen == False:
            return
        
        self.wizmolib.wizmoWrite(self.wizmoHandle, byref(packet))

    def setOriginMode(self, value):
        self.wizmolib.wizmoSetOriginMode(self.wizmoHandle, value)

    def setAxisProcessingMode(self, value):
        self.wizmolib.wizmoSetAxisProcessingMode(self.wizmoHandle, value)

    def setVariableGainMode(self, value):
        self.wizmolib.wizmoSetVariableGainMode(self.wizmoHandle, value)

    def getOriginMode(self):
        return self.wizmolib.wizmoGetOriginMode(self.wizmoHandle)

    def getAxisProcessingMode(self):
        return self.wizmolib.wizmoGetAxisProcessingMode(self.wizmoHandle)

    def getVariableGainMode(self):
        return self.wizmolib.wizmoGetVariableGainMode(self.wizmoHandle)