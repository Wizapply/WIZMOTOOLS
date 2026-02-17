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

class wizmoAxisMode(IntEnum):
    Manual = 0
    Global = 1
    Local = 2

class wizmoDevice(IntEnum):
    NONE = 0
    SIMVR4DOF = 1
    SIMVR6DOF = 2
    SIMVR6DOF_MASSIVE = 3
    DRIVE_X = 4
    ANTSEAT = 5
    SIMVRMASSIVE_KV = 6
    SIMVR2DOF_KV = 7
    SIMVR2DOF = 8
    SIMVRKICKBOARD_KV = 9

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
        self.gravityMotionRatio = 0.0
        self.commandSendCount = 0 

# Main Class
class wizmo():

    _wizmo_lib = None

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def __init__(self, verbose:bool=False):
        os_name = platform.system()
        arch_is64bit = platform.architecture()[0] == '64bit'
        arch_isARM = False
        if 'armv' in platform.machine() or 'aarch64' in platform.machine():
            arch_isARM = True
        
        #For pyinstaller build
        if getattr(sys, 'frozen', False):
            libloadpath = ""
        else:
            libloadpath = os.path.dirname(__file__)
            
        if os_name == 'Windows':
            if arch_is64bit:
                if arch_isARM:
                    libloadpath += '\\wizmoARM64.dll'
                else:
                    libloadpath += '\\wizmo.dll'
            else:
                libloadpath += '\\wizmo32.dll'
            
        else:
            if arch_isARM:
                if arch_is64bit: libloadpath += '/libwizmoRPi64.so'
                else: libloadpath += '/libwizmoRPi32.so'
            else:
                if arch_is64bit: libloadpath += '/libwizmo.so'
                else: libloadpath += '/libwizmo32.so'
        
        if wizmo._wizmo_lib is None:
            try:
                wizmo._wizmo_lib = cdll.LoadLibrary(libloadpath)
            except OSError as e:
                raise RuntimeError(f"WIZMO Load Library Error:{libloadpath}") from e

        self.wizmolib = wizmo._wizmo_lib
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
        size = wizmo._wizmo_lib.wizmoBackLogDataAvailable()
        if(size > 0) :
            p = create_string_buffer(size)
            iRef = wizmo._wizmo_lib.wizmoGetBackLog(p, size)
            if iRef > 0:
                bufferString = p.value.decode()
                buf_res += bufferString.rstrip("\n")

        if printing and buf_res != '': print(buf_res)

        return buf_res

    def starter(self, appCode:str, blocking:bool=False):
        if self.wizmoHandle >= 0:
            if self.verbose: print("WIZMO IS ALREADY OPEN.")
            return WIZMO_HANDLE_ERROR

        self.wizmoHandle = int(self.wizmolib.wizmoOpen(appCode.encode()))
        if self.wizmoHandle < 0:
            if self.verbose: print("WIZMO OPEN ERROR!")
            self.wizmoHandle = WIZMO_HANDLE_ERROR
        else:
            if self.verbose: print ("STARTED WIZMO.")
            if blocking == True:
                while self.get_status() <= wizmoStatus.Initial:
                    print(self.get_status())
                    time.sleep(0.1)

        return self.wizmoHandle

    def starter_serialassign(self, appCode:str, assign:str, blocking:bool=False):
        if self.wizmoHandle >= 0:
            if self.verbose: print("WIZMO IS ALREADY OPEN.")
            return WIZMO_HANDLE_ERROR

        self.wizmoHandle = int(self.wizmolib.wizmoOpenSerialAssign(appCode.encode(), assign.encode()))
        if self.wizmoHandle < 0:
            if self.verbose: print("WIZMO OPEN ERROR!")
            self.wizmoHandle = WIZMO_HANDLE_ERROR
        else:
            if self.verbose: print ("STARTED WIZMO.")
            if blocking == True:
                while self.get_status() == wizmoStatus.Initial:
                    time.sleep(0.1)

        return self.wizmoHandle

    def close(self) -> None:
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            if self.verbose: print("WIZMO IS NOT OPEN.")
            return
    
        self.wizmolib.wizmoClose(self.wizmoHandle)
        self.wizmoHandle = WIZMO_HANDLE_ERROR

    def get_status(self) -> int:
        return self.wizmolib.wizmoGetState(self.wizmoHandle)

    def is_running(self) -> bool:
        return bool(self.wizmolib.wizmoIsRunning(self.wizmoHandle))

    def simple_pose_update(self, roll:float, pitch:float, yaw:float, heave:float, sway:float, surge:float) -> None:
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

        if len(value) != 6:
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

    def axis_processing_mode(self, value:wizmoAxisMode=None):
        if value is None:
            return self.wizmolib.wizmoGetAxisProcessingMode(self.wizmoHandle)
        else:
            self.wizmolib.wizmoSetAxisProcessingMode(self.wizmoHandle, int(value))
    
    def origin_mode(self, value:bool=None):
        if value is None:
            return self.wizmolib.wizmoGetOriginMode(self.wizmoHandle)
        else:
            self.wizmolib.wizmoSetOriginMode(self.wizmoHandle, value)

    def speed_gain_mode(self, value:wizmoSpeedGain=None):
        if value is None:
            return self.wizmolib.wizmoGetSpeedGainMode(self.wizmoHandle)
        else:
            self.wizmolib.wizmoSetSpeedGainMode(self.wizmoHandle, int(value))

    def get_device_name(self) -> wizmoDevice:
        return self.wizmolib.wizmoGetDevice(self.wizmoHandle)
