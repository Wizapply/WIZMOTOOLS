# -*- coding: cp932 -*-
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


# wizmo Data Packet
class wizmoPacket(Structure):  
    _fields_ = [  
            ("axis1", c_float),
            ("axis2", c_float),
            ("axis3", c_float),
            ("axis4", c_float),
            ("axis5", c_float),
            ("axis6", c_float),
            ("speedAxis123", c_float),  
            ("accelAxis123", c_float),
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
            ("commandCount", c_int),  
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
        self.speedAxis123 = 1.0
        self.accelAxis123 = 0.5
        self.speedAxis4 = 1.0
        self.accelAxis4 = 0.5
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.heave = 0.0
        self.sway = 0.0
        self.surge = 0.0
        self.rotationMotionRatio = 0.3
        self.gravityMotionRatio = 0.7
        self.commandCount = 0 
# Load dll
try:
    if platform.system() == 'Windows':
        wizmolib = cdll.LoadLibrary("./wizmo.dll");             #Windows
    else:
        wizmolib = cdll.LoadLibrary("./libwizmo.so");          #Linux
except FileNotFoundError:
    print("WIZMO DLL NOT FOUND ERROR!")
    exit()
wizmoIsOpen = False

# Methods
def wizmoAwake(appCode) :
    global wizmoIsOpen
    global wizmolib
    if(wizmoIsOpen == True) :
        return
    if(wizmolib.wizmoOpen(appCode.encode()) == 0):
        wizmoIsOpen = True
    else:
        print("wizmo DLL ERROR!")

def wizmoDestroy() :
    global wizmoIsOpen
    global wizmolib
    
    if(wizmoIsOpen == False) :
        return
    
    wizmoUpdateBackLog()
    wizmolib.wizmoClose()
    wizmoIsOpen = False

def wizmoUpdateBackLog() :
    global wizmoIsOpen
    global wizmolib
    
    if(wizmoIsOpen == False) :
        return

    size = wizmolib.wizmoBackLogDataAvailable();
    if(size > 0) :
        wizmolib.wizmoGetBackLog.restype = c_int
        wizmolib.wizmoGetBackLog.argtypes = (c_char_p, c_int)
        
        p = create_string_buffer(size)
        iRef = wizmolib.wizmoGetBackLog(p, size)
        if iRef > 0:
            bufferString = p.value.decode()
            print(bufferString.rstrip("\n"))

def wizmoUpdateState() :
    global wizmoIsOpen
    global wizmolib
    
    stateNo = wizmolib.wizmoGetState();

    #State
    if(stateNo <= wizmoStatus.Initial) :
        return False
    return True
    
def wizmoUpdate(roll, pitch, yaw) :
    global wizmoIsOpen
    global wizmolib
    
    if(wizmoIsOpen == False) :
        return

    packet = wizmoPacket()
    packet.roll = roll
    packet.pitch = pitch
    packet.yaw = yaw

    packet.rotationMotionRatio = 1.0
    packet.gravityMotionRatio = 0.0
    wizmolib.wizmoWrite(byref(packet));

#---------------------------------------------------
# Main Program
wizmoAwake("")
print ("WIZMO-START...")

time.sleep(1) #wait

wizmolib.wizmoSetOriginMode(False)
wizmolib.wizmoSetAxisProcessingMode(True)

wizmoUpdateBackLog()

time.sleep(5) #wait
if(wizmoUpdateState()) : 
    print("This program can change ROLL, PITCH, YAW of SIMVR. \nSpecification value [-1.0 to 1.0]. And, this is ended in an [exit] input.\n")

while(wizmoUpdateState()) :
    rolldata = input('ROLL >> ')
    if(rolldata == 'exit') : break
    pitchdata = input('PITCH >> ')
    if(pitchdata == 'exit') : break
    yawdata = input('YAW >> ')
    if(yawdata == 'exit') : break
    
    wizmoUpdate(float(rolldata), float(pitchdata), float(yawdata))
    print("WIZMO RUN")
    
print("WIZMO-SHUTDOWN")

wizmoDestroy()
#---------------------------------------------------
