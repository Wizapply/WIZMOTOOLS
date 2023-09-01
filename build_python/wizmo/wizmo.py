# -*- coding: utf-8 -*-
# Import
from ctypes import *
import time, platform, os, sys
from enum import IntEnum

#define
WIZMO_HANDLE_ERROR = -1

# Status Define
class wizmoStatus(IntEnum):
    CanNotFindUsb = 0
    CanNotFindWizmo = 1
    CanNotCalibration = 2
    TimeoutCalibration = 3
    ShutDownActuator = 4
    CanNotCertificate = 5
    Initial = 6
    Running = 7
    StopActuator = 8
    CalibrationRetry = 9

class wizmoSpeedGain(IntEnum):
    Normal = 0
    Variable = 1
    Manual = 2

# WIZMO Data Packet
class wizmoPacket(Structure):  
    _fields_ = [  
            ("axis1", c_float),
            ("axis2", c_float),
            ("axis3", c_float),
            ("axis4", c_float),
            ("axis5", c_float),
            ("axis6", c_float),
            ("speed1_all", c_float),
            ("speed2", c_float),
            ("speed3", c_float),
            ("speed4", c_float),
            ("speed5", c_float),
            ("speed6", c_float),
            ("accel", c_float),
            ("roll", c_float),  
            ("pitch", c_float),  
            ("yaw", c_float),
            ("heave", c_float),  
            ("sway", c_float),  
            ("surge", c_float),
            ("rotationMotionRatio", c_float),  
            ("gravityMotionRatio", c_float),  
            ("commandSendCount", c_int),  
            ("command", c_char*256)
            ]
  
    def __init__(self):  
        self.axis1 = 0.5  #default param
        self.axis2 = 0.5  
        self.axis3 = 0.5
        self.axis4 = 0.5
        self.axis5 = 0.5
        self.axis6 = 0.5

        self.speed1_all = 0.667
        self.speed2 = 0.667
        self.speed3 = 0.667
        self.speed4 = 0.667
        self.speed5 = 0.667
        self.speed6 = 0.667
        self.accel = 0.5

        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.heave = 0.0
        self.sway = 0.0
        self.surge = 0.0
        self.rotationMotionRatio = 1.0
        self.gravityMotionRatio = 1.0
        self.commandSendCount = 0 

# Main Class
class wizmo():
    
    m_wizmolib = None

    def __init__(self, verbose:bool=False):
        libloadpath = os.path.dirname(__file__)
        if platform.system() == 'Windows':
            if platform.architecture()[0] == '64bit':
                libloadpath += '\\wizmo.dll'
            else:
                libloadpath += '\\wizmo32.dll'
        else:
            if platform.architecture()[0] == '64bit':
                libloadpath += '\\libwizmo.so'
            else:
                libloadpath += '\\libwizmo32.so'

        #For pyinstaller build
        if getattr(sys, 'frozen', False):
            if platform.system() == 'Windows':
                if platform.architecture()[0] == '64bit':
                    libloadpath = 'wizmo.dll'
                else:
                    libloadpath = 'wizmo32.dll'
            else:
                if platform.architecture()[0] == '64bit':
                    libloadpath = 'libwizmo.so'
                else:
                    libloadpath = 'libwizmo32.so'
        
        if wizmo.m_wizmolib == None:
            wizmo.m_wizmolib = cdll.LoadLibrary(libloadpath)

        self.wizmolib = wizmo.m_wizmolib
        self.verbose = verbose
        self.simplePacket = wizmoPacket()
        self.wizmoHandle = WIZMO_HANDLE_ERROR

        self.wizmolib.wizmoGetBackLog.restype = c_int
        self.wizmolib.wizmoGetBackLog.argtypes = (c_char_p, c_int)
        self.wizmolib.wizmoWrite.argtypes = (c_int, POINTER(wizmoPacket))
        if self.verbose: print ("LOADED WIZMO DLL.")

    @staticmethod
    def get_backlog(printing:bool=False):
        buf_res = ''
        size = wizmo.m_wizmolib.wizmoBackLogDataAvailable();
        if(size > 0) :
            p = create_string_buffer(size)
            iRef = wizmo.m_wizmolib.wizmoGetBackLog(p, size)
            if iRef > 0:
                bufferString = p.value.decode()
                buf_res += bufferString.rstrip("\n")

        if printing and buf_res != '': print(buf_res)

        return buf_res

    def starter(self, appCode:str):
        if self.wizmoHandle >= 0:
            if self.verbose: print("WIZMO IS ALREADY OPEN.")
            return WIZMO_HANDLE_ERROR

        whandle = int(self.wizmolib.wizmoOpen(appCode.encode()))
        if whandle < 0:
            if self.verbose: print("WIZMO OPEN ERROR!")
            self.wizmoHandle = WIZMO_HANDLE_ERROR
        else:
            if self.verbose: print ("STARTED WIZMO.")
            time.sleep(1) #wait
        self.wizmoHandle = whandle
        return self.wizmoHandle

    def starter_serialassign(self, appCode:str, assign:str):
        if self.wizmoHandle >= 0:
            if self.verbose: print("WIZMO IS ALREADY OPEN.")
            return WIZMO_HANDLE_ERROR

        whandle = int(self.wizmolib.wizmoOpenSerialAssign(appCode.encode(), assign.encode()))
        if whandle < 0:
            if self.verbose: print("WIZMO OPEN ERROR!")
            self.wizmoHandle = WIZMO_HANDLE_ERROR
        else:
            if self.verbose: print ("STARTED WIZMO.")
            time.sleep(1) #wait
        self.wizmoHandle = whandle
        return self.wizmoHandle

    def close(self):
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            if self.verbose: print("WIZMO IS NOT OPEN.")
            return
    
        self.wizmolib.wizmoClose(self.wizmoHandle)
        self.wizmoHandle = WIZMO_HANDLE_ERROR

    def get_status(self):
        return self.wizmolib.wizmoGetState(self.wizmoHandle)

    def is_running(self) -> bool:
        return bool(self.wizmolib.wizmoIsRunning(self.wizmoHandle))

    def simple_pose_update(self, roll:float, pitch:float, yaw:float, heave:float, sway:float, surge:float):
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            return

        self.simplePacket.roll = roll
        self.simplePacket.pitch = pitch
        self.simplePacket.yaw = yaw
        self.simplePacket.heave = heave
        self.simplePacket.sway = sway
        self.simplePacket.surge = surge
        self.wizmolib.wizmoWrite(self.wizmoHandle, pointer(self.simplePacket))

    def simple_pose_update_tuple(self, value:tuple):
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            return

        if len(value) < 6:
            if self.verbose: print("ERROR TUPLE FORMAT.")
            return

        self.simplePacket.roll = value[0]
        self.simplePacket.pitch = value[1]
        self.simplePacket.yaw = value[2]
        self.simplePacket.heave = value[3]
        self.simplePacket.sway = value[4]
        self.simplePacket.surge = value[5]
        self.wizmolib.wizmoWrite(self.wizmoHandle, pointer(self.simplePacket))

    def simple_motion_ratio_update(self, rotation:float, gravity:float):
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            return

        self.simplePacket.rotationMotionRatio = rotation
        self.simplePacket.gravityMotionRatio = gravity
        self.wizmolib.wizmoWrite(self.wizmoHandle, pointer(self.simplePacket))

    def simple_motion_speed_update(self, accel:float, speed1:float, speed2:float, speed3:float, speed4:float, speed5:float, speed6:float):
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            return

        self.simplePacket.accel = accel
        self.simplePacket.speed1_all = speed1
        self.simplePacket.speed2 = speed2
        self.simplePacket.speed3 = speed3
        self.simplePacket.speed4 = speed4
        self.simplePacket.speed5 = speed5
        self.simplePacket.speed6 = speed6
        self.wizmolib.wizmoWrite(self.wizmoHandle, pointer(self.simplePacket))

    def simple_motion_power_update(self, accel:float, speed:float):
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            return

        self.simplePacket.accel = accel
        self.simplePacket.speed1_all = speed
        self.simplePacket.speed2 = speed
        self.simplePacket.speed3 = speed
        self.simplePacket.speed4 = speed
        self.simplePacket.speed5 = speed
        self.simplePacket.speed6 = speed
        self.wizmolib.wizmoWrite(self.wizmoHandle, pointer(self.simplePacket))

    def packet_update(self, packet:wizmoPacket):
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            return

        self.wizmolib.wizmoWrite(self.wizmoHandle, pointer(packet))

    def axis_processing_mode(self, value:bool=None):
        if value==None:
            return self.wizmolib.wizmoGetAxisProcessingMode(self.wizmoHandle)
        else:
            self.wizmolib.wizmoSetAxisProcessingMode(self.wizmoHandle, value)
    
    def origin_mode(self, value:bool=None):
        if value==None:
            return self.wizmolib.wizmoGetOriginMode(self.wizmoHandle)
        else:
            self.wizmolib.wizmoSetOriginMode(self.wizmoHandle, value)

    def speed_gain_mode(self, value:wizmoSpeedGain=None):
        if value==None:
            return self.wizmolib.wizmoGetSpeedGainMode(self.wizmoHandle)
        else:
            self.wizmolib.wizmoSetSpeedGainMode(self.wizmoHandle, int(value))
