# -*- coding: utf-8 -*-
import wizmo, time
import asyncio as aio

# -------- global var --------

simvr_variable = {'heave':0.0, 'sway':0.0, 'surge':0.0,
               'pitch':0.0, 'roll':0.0, 'yaw':0.0, 
               'accel_gain':0.5, 'speed_gain':0.5 }
simvr_endflag = False

# -------- sequence --------

async def simvr_sequence(lock):
    global simvr_variable, simvr_endflag
    await aio.sleep(3.0)

    #////////sequence////////

    #1s wait
    await aio.sleep(1.0)

    for _i in range(2):
        async with lock:
            simvr_variable['accel_gain'] = 0.6
            simvr_variable['sway'] = -1.0
            simvr_variable['yaw'] = -0.3

        # 1s wait
        await aio.sleep(1.0 + 0.5)

        async with lock:
            simvr_variable['accel_gain'] = 0.2
            simvr_variable['sway'] = 0.0
            simvr_variable['yaw'] = 0.0

        # 1s wait
        await aio.sleep(1.0 + 0.5)

        async with lock:
            simvr_variable['accel_gain'] = 0.6
            simvr_variable['sway'] = 1.0
            simvr_variable['yaw'] = 0.3

        # 1s wait
        await aio.sleep(1.0 + 0.5)

        async with lock:
            simvr_variable['accel_gain'] = 0.2
            simvr_variable['sway'] = 0.0
            simvr_variable['yaw'] = 0.0

        # 1s wait
        await aio.sleep(1.0 + 0.5)

    #////////sequence////////

    await aio.sleep(3.0)
    simvr_endflag = True

# -------- main func --------

async def main():
    global simvr_variable, simvr_endflag
    
    #main
    print('-------- START WIZMO-TOOLS --------')

    try:
        wm = wizmo.wizmo(True)
    except FileNotFoundError:
        print("WIZMO DLL NOT FOUND ERROR!")
        exit()

    wm.starter('')
    wm.simple_motion_ratio_update(0.8,0.9)

    while wm.get_status() == wizmo.wizmoStatus.Initial:
        time.sleep(0.1)    #wait 0.1s

    print('-------- START SCRIPT --------')
    lock = aio.Lock()
    sc_task = aio.create_task(simvr_sequence(lock))
    
    while wm.is_running():
        async with lock:
            wm.simple_motion_power_update(simvr_variable['accel_gain'],simvr_variable['speed_gain'])
            wm.simple_pose_update(simvr_variable['roll'],simvr_variable['pitch'],simvr_variable['yaw'],
                                  simvr_variable['heave'],simvr_variable['sway'],simvr_variable['surge'])
        wm.get_backlog(True)
        await aio.sleep(0.1)    #wait 0.1s

        if simvr_endflag:
            break

    wm.close()
    wm.get_backlog(True)

    print('-------- FINISH WIZMO-TOOLS --------')

    #await sc_task      #wait
    sc_task.cancel()    #cancel
    print('-------- FINISH SCRIPT --------')

#main
if __name__ == "__main__":
    aio.run(main())
