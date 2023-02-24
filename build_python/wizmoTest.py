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

while wm.isRunning():

    wm.simplePoseUpdate(0.0,0.0,0.0,0.0,0.0,0.0)
    wm.getBackLog(True)
    time.sleep(0.1) #100ms

wm.close()
wm.getBackLog(True)

print('-------- FINISH WIZMO-TOOLS --------')
