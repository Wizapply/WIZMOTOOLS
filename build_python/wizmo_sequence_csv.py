# -*- coding: utf-8 -*-
import wizmo, time
import asyncio as aio

import csv
import sys

#req: pip install keyboard
import keyboard

# -------- data --------

CSV_FILE_PATH = './example_datas/sample1.csv'
if len(sys.argv) >= 2:
    CSV_FILE_PATH = sys.argv[1]

# -------- global var --------

simvr_variable = {'heave':0.0, 'sway':0.0, 'surge':0.0,
               'pitch':0.0, 'roll':0.0, 'yaw':0.0, 
               'accel_gain':0.5, 'speed_gain':0.5, 'is_origin':0 }
simvr_endflag = False

# -------- sequence --------

async def simvr_sequence(lock, work_data):
    global simvr_variable, simvr_endflag

    #start end time
    start_time = float(work_data[0]['time'])
    end_time = float(work_data[-1]['time'])
    
    print('DATA START:{0}s, END:{1}s'.format(start_time, end_time))
    
    #stopper
    work_data.append({'time': end_time+1.0})
    work_data_length = len(work_data)-1

    #////////sequence////////

    #1s wait
    await aio.sleep(1.0)

    for _i in range(work_data_length):
        cur_data = work_data[_i]
        print('CURRENT DATA:{0}s'.format(cur_data['time']))
        nexttime = float(work_data[_i+1]['time']) - float(cur_data['time'])
        if nexttime <= 0.01: continue

        async with lock:
            if 'speed' in cur_data: simvr_variable['speed_gain'] = float(cur_data['speed'])
            if 'accel' in cur_data: simvr_variable['accel_gain'] = float(cur_data['accel'])
            if 'roll' in cur_data:  simvr_variable['roll'] = float(cur_data['roll'])
            if 'pitch' in cur_data: simvr_variable['pitch'] = float(cur_data['pitch'])
            if 'yaw' in cur_data:   simvr_variable['yaw'] = float(cur_data['yaw'])
            if 'heave' in cur_data: simvr_variable['heave'] = float(cur_data['heave'])
            if 'sway' in cur_data:  simvr_variable['sway'] = float(cur_data['sway'])
            if 'surge' in cur_data: simvr_variable['surge'] = float(cur_data['surge'])
            if 'is_origin' in cur_data: simvr_variable['is_origin'] = float(cur_data['is_origin'])
        # wait
        await aio.sleep(nexttime - 0.01)

    #////////sequence////////

    #reset
    async with lock:
        simvr_variable['speed_gain'] = 0.667
        simvr_variable['accel_gain'] = 0.03
        simvr_variable['roll'] = 0.0
        simvr_variable['pitch'] = 0.0
        simvr_variable['yaw'] = 0.0
        simvr_variable['heave'] = 0.0
        simvr_variable['sway'] = 0.0
        simvr_variable['surge'] = 0.0

    print('DATA FINISH')

    await aio.sleep(1.0)#1s wait
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
        
    #csv data reader
    print('Read CSV file name :',CSV_FILE_PATH)
    with open(CSV_FILE_PATH, 'r') as file_csv:
        csvreader = csv.DictReader(file_csv)
        data_content = [row for row in csvreader]

    #time sort
    data_content = sorted(data_content, key=lambda x: float(x['time']))
    
    # data debug
    #for _dat in data_content:
    #    print(_dat)
    
    wm.starter('')
    wm.simple_motion_ratio_update(0.5,0.5)

    while wm.get_status() == wizmo.wizmoStatus.Initial:
        time.sleep(0.1)    #wait 0.1s

    print('Press spacebar key to START!')
    while not keyboard.is_pressed('space'):
        time.sleep(0.1)    #wait 0.1s

    print('-------- START SCRIPT --------')
    lock = aio.Lock()
    sc_task = aio.create_task(simvr_sequence(lock, data_content))
    
    while wm.is_running():
        async with lock:
            wm.origin_mode(simvr_variable['is_origin'] == 1)
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
