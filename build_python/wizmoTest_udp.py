# -*- coding: utf-8 -*-
import wizmo
import time
import threading
import socket
import struct

print('-------- START WIZMO-TOOLS --------')

HOST = ''
PORT = 40000
ADDRESS = "127.0.0.1"

sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sc.bind((HOST, PORT))
sc.settimeout(0.1)

try:
    wm = wizmo.wizmo(True)
except FileNotFoundError:
    print("WIZMO DLL NOT FOUND ERROR!")
    sc.close()
    exit()

wm.starter('')

print("This program can change ROLL, PITCH, YAW of wizmo from UDP/IP\n")

while wm.is_running():
    rolldata = 0.0
    pitchdata = 0.0
    yawdata = 0.0
    
    try:
        #data ex: 1.0,1.0,1.0
        data, addr = sc.recvfrom(256)
        res = data.decode('utf-8')
        dataraw = res.split(',')
        rolldata = float(dataraw[0])
        pitchdata = float(dataraw[1])
        yawdata = float(dataraw[2])
    except socket.timeout:
        pass
    except socket.error:
        print("UDP ERROR")
        break
    
    wm.simple_pose_update(rolldata, pitchdata, yawdata, 0.0,0.0,0.0)
    wm.get_backlog(True)
    time.sleep(0.1) #100ms

wm.close()
wm.get_backlog(True)
sc.close()

print('-------- FINISH WIZMO-TOOLS --------')
