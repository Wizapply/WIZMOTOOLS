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

while wm.updateState():

    wm.simplePoseUpdate(0.0,0.0,0.0,0.0,0.0,0.0)
    wm.updateBackLog()
    time.sleep(0.1) #100ms

wm.close()
wm.updateBackLog()

print('-------- FINISH WIZMO-TOOLS --------')
