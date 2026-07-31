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
wm.simple_motion_power_update(0.1,0.667)
wm.simple_motion_ratio_update(0.0,1.0)
wm.speed_gain_mode(wizmo.wizmoSpeedGain.Normal)

while wm.is_running():
    #print(wm.get_status())
    wm.simple_pose_update(1.0,0.0,0.0,0.0,0.0,0.0
    time.sleep(0.5)
    wm.simple_pose_update(-1.0,0.0,0.0,0.0,0.0,0.0)
    wm.get_backlog(True)
    time.sleep(0.5) #500ms

wm.close()
wm.get_backlog(True)

print('-------- FINISH WIZMO-TOOLS --------')
