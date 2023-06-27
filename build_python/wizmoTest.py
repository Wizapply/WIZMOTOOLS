# -*- coding: utf-8 -*-
import wizmo
import time
import threading

print('-------- START WIZMO-TOOLS --------')

try:
    wm = wizmo.wizmo(True)
except FileNotFoundError:
    print("WIZMO DLL NOT FOUND ERROR!")
    exit()

wm.starter('')

while wm.is_running():

    wm.simple_pose_update(0.0,0.0,0.0,0.0,0.0,0.0)
    wm.get_backlog(True)
    time.sleep(0.1) #100ms

wm.close()
wm.get_backlog(True)

print('-------- FINISH WIZMO-TOOLS --------')
