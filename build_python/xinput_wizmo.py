# xinput_wizmo.py 2023/02/14
# WIZAPPLY CO., LTD.
# Request import
# -> pip install XInput-Python

import XInput
import wizmo
import time

print('-------- START WIZMO-TOOLS --------')

try:
    wm = wizmo.wizmo(True)
except FileNotFoundError:
    print("WIZMO DLL NOT FOUND ERROR!")
    exit()

wm.starter("")

XInput.set_deadzone(XInput.DEADZONE_TRIGGER,10)

l_thumb_stick_pos = (0.0, 0.0)
r_thumb_stick_pos = (0.0, 0.0)

wm.simple_motion_power_update(0.5,0.66)

while wm.is_running():
    events = XInput.get_events()
    for event in events:
        if event.user_index == 0:
            if event.type == XInput.EVENT_CONNECTED:
                print('CONTROLLER ON')
            elif event.type == XInput.EVENT_DISCONNECTED:
                print('CONTROLLER OFF')
            elif event.type == XInput.EVENT_STICK_MOVED:
                if event.stick == XInput.LEFT:
                    l_thumb_stick_pos = (round(event.x,1), round(event.y,1))
                    print('    LEFT THUMB STICK' + str(l_thumb_stick_pos))
                elif event.stick == XInput.RIGHT:
                    r_thumb_stick_pos = (round(event.x,1), round(event.y,1))
                    print('    RIGHT THUMB STICK' + str(r_thumb_stick_pos))
    #update wizmo
    wm.simple_pose_update(l_thumb_stick_pos[0],-l_thumb_stick_pos[1],0.0,0.0,0.0,0.0)
    wm.get_backlog(True)
    time.sleep(0.1) #100ms

wm.close()
wm.get_backlog(True)

print('-------- FINISH WIZMO-TOOLS --------')
