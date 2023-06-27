# -*- coding: utf-8 -*-
import wizmo
import time
import threading
import mmap, io
from ctypes import *

# WRC Data Packet
class wrcPacket(Structure):  
    _fields_ = [  
            ("sequence_number", c_int32),
            ("version", c_int32),
            ("gear", c_int32),
            ("velocity_x", c_float),
            ("velocity_y", c_float),
            ("velocity_z", c_float),
            ("acceleration_x", c_float),
            ("acceleration_y", c_float),
            ("acceleration_z", c_float),
            ("engine_idle_rpm", c_int32),
            ("engine_max_rpm", c_int32),
            ("engine_rpm", c_int32),
            ("suspension_travel_LF", c_float),
            ("suspension_travel_LR", c_float),
            ("suspension_travel_RR", c_float),
            ("suspension_travel_RF", c_float),
            ("suspension_position_LF", c_float),
            ("suspension_position_LR", c_float),
            ("suspension_position_RR", c_float),
            ("suspension_position_RF", c_float),
            ("unknown", c_float*4)
            ]

print('-------- START WIZMO-TOOLS --------')

#Shared Memory
mm = mmap.mmap(0, sizeof(wrcPacket), access=mmap.ACCESS_DEFAULT, tagname="Local\\WRC-8wSotWzFKAhBlbW10ZJBKaWMdWszbBXg")
wrcpkt = wrcPacket()

try:
    wm = wizmo.wizmo(True)
except FileNotFoundError:
    print("WIZMO DLL NOT FOUND ERROR!")
    exit()

wm.starter('')

print("This program can change ROLL, PITCH, YAW of wizmo from SharedMemory\n")

while wm.is_running():
    rolldata = 0.0
    pitchdata = 0.0
    heavedata = 0.0
    
    try:
        mm.seek(0)
        buffer = io.BytesIO(mm.read())
        buffer.readinto(wrcpkt)
        rolldata = round(-wrcpkt.acceleration_x*0.08,4)
        pitchdata = round(wrcpkt.acceleration_z*0.06,4)
        heavedata = round(wrcpkt.acceleration_y*0.05,4)
    except OSError:
        print("MMAP ERROR")
        break
    
    wm.simple_pose_update(rolldata, pitchdata, 0.0, heavedata,0.0,0.0)
    wm.get_backlog(True)
    time.sleep(0.1) #100ms

wm.close()
wm.get_backlog(True)

print('-------- FINISH WIZMO-TOOLS --------')
