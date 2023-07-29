# -*- coding: utf-8 -*-
#beamng.drive motion config 100hz, smooth=0,0,0
import wizmo
import time
import threading
import socket
import struct
import math

#IIRFilter Class
class IIRFilter:
    
    LOW_PASS = 0
    LOW_PASS_ODR1 = 1
    HIGH_PASS = 2
    HIGH_PASS_ODR1 = 3
    ALL_PASS = 4

    def __init__(self, filterMode, sampleRate, cutoff):
        self.ft_o = cutoff
        self.sampleRate = sampleRate

        self.a1 = 0
        self.a2 = 0
        self.a3 = 0
        self.b1 = 0
        self.b2 = 0
        self.in_prev = [0,0]
        self.out_prev = [0,0]

        if filterMode == self.LOW_PASS:
            self._lowPassFilter(sampleRate, cutoff)
        elif filterMode == self.LOW_PASS_ODR1:
            self._lowPassFilter1(sampleRate, cutoff)
        elif filterMode == self.HIGH_PASS:
            self._highPassFilter(sampleRate, cutoff)
        elif filterMode == self.HIGH_PASS_ODR1:
            self._highPassFilter1(sampleRate, cutoff)
        else:   #ALL PASS
            self._allPassFilter(sampleRate, cutoff)

    def compute(self, in_data:float) -> float:
        ret = self.a1 * in_data + self.a2 * self.in_prev[0] + self.a3 * self.in_prev[1] - \
          self.b1 * self.out_prev[0] - self.b2 * self.out_prev[1]

        self.in_prev[1] = self.in_prev[0]
        self.in_prev[0] = in_data
        self.out_prev[1] = self.out_prev[0]
        self.out_prev[0] = ret
        return ret

    def _lowPassFilter(self, sample_rate, fc):
        fa = 1.0 / (2.0*math.pi) * math.tan(math.pi*fc/sample_rate)
        pfc = 2.0*math.pi*fa;
        RT2 = math.sqrt(2.0);

        self.a1 = pfc*pfc / (1 + RT2*pfc + pfc*pfc)
        self.a2 = 2.0*pfc*pfc / (1 + RT2*pfc + pfc*pfc)
        self.a3 = pfc*pfc / (1 + RT2*pfc + pfc*pfc)
        self.b1 = (-2.0 + 2.0*pfc*pfc) / (1 + RT2*pfc + pfc*pfc)
        self.b2 = (1.0 - RT2*pfc + pfc*pfc) / (1 + RT2*pfc + pfc*pfc)

    def _lowPassFilter1(self, sample_rate, fc):
        fa = 1.0 / (2.0*math.pi) * math.tan(math.pi*fc/sample_rate)
        pfc = 2.0*math.pi*fa;
        RT2 = math.sqrt(2.0);

        self.a1 = pfc / (pfc + 1.0)
        self.a2 = pfc / (pfc + 1.0)
        self.a3 = 0.0
        self.b1 = (pfc - 1.0) / (pfc + 1.0)
        self.b2 = 0.0

    def _highPassFilter(self, sample_rate, fc):
        fa = 1.0 / (2.0*math.pi) * math.tan(math.pi*fc/sample_rate)
        pfc = 2.0*math.pi*fa;
        RT2 = math.sqrt(2.0);
	
        self.a1 = 1.0 / (pfc*pfc + RT2*pfc + 1.0)
        self.a2 = -2.0 / (pfc*pfc + RT2*pfc + 1.0)
        self.a3 = 1.0 / (pfc*pfc + RT2*pfc + 1.0)
        self.b1 = (2.0*pfc*pfc - 2.0) / (pfc*pfc + RT2*pfc + 1.0)
        self.b2 = (pfc*pfc - RT2*pfc + 1.0) / (pfc*pfc + RT2*pfc + 1.0)

    def _highPassFilter1(self, sample_rate, fc):
        fa = 1.0 / (2.0*math.pi) * math.tan(math.pi*fc/sample_rate)
        pfc = 2.0*math.pi*fa;
        RT2 = math.sqrt(2.0);
	
        self.a1 = 1.0 / (pfc + 1.0)
        self.a2 = -1.0 / (pfc + 1.0)
        self.a3 = 0.0
        self.b1 = (pfc - 1.0) / (pfc + 1.0)
        self.b2 = 0.0

    def _allPassFilter(self, sample_rate, fc):
        fa = 1.0 / (2.0*math.pi) * math.tan(math.pi*fc/sample_rate)
        pfc = 2.0*math.pi*fa;
        RT2 = math.sqrt(2.0);

        w0 = 2.0 * math.pi*fc / sample_rate;
        alpha = math.sin(w0) / 2.0;
	
        self.a1 = (1.0 - alpha) / (1.0 + alpha)
        self.a2 = -2.0 * math.cos(w0) / (1.0 + alpha)
        self.a3 = (1.0 + alpha) / (1.0 + alpha)
        self.b1 = -2.0 * math.cos(w0) / (1.0 + alpha)
        self.b2 = (1.0 - alpha) / (1.0 + alpha)

#-----------------------------------------------------------

print('-------- START WIZMO-TOOLS --------')

HOST = '127.0.0.1'
PORT = 4444

sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sc.bind(('', PORT))
sc.settimeout(0.5)

_filter = [IIRFilter(IIRFilter.LOW_PASS, 100, 2.55),
           IIRFilter(IIRFilter.LOW_PASS, 100, 2.55),
           IIRFilter(IIRFilter.LOW_PASS, 100, 2.55),
           IIRFilter(IIRFilter.LOW_PASS, 100, 1.25),
           IIRFilter(IIRFilter.LOW_PASS, 100, 1.25),
           IIRFilter(IIRFilter.LOW_PASS, 100, 1.25)]

try:
    wm = wizmo.wizmo(True)
except FileNotFoundError:
    print("WIZMO DLL NOT FOUND ERROR!")
    exit()

wm.starter('')
wm.simple_motion_power_update(1.0,1.0)
wm.speed_gain_mode(wizmo.wizmoSpeedGain.Variable)

time.sleep(3)

print("This program can change ROLL, PITCH, YAW of wizmo from UDP/IP\n")

while wm.is_running():
    rolldata = 0.0
    pitchdata = 0.0
    yawdata = 0.0
    heavedata = 0.0
    swaydata = 0.0
    surgedata = 0.0
    try:
        data, addr = sc.recvfrom(128)
        if data[0:4].decode() == "BNG1":
            [posX, posY, posZ] = struct.unpack('3f', data[4:4+12])
            [velX, velY, velZ] = struct.unpack('3f', data[16:16+12])
            [accX, accY, accZ] = struct.unpack('3f', data[28:28+12])
            [upVecX, upVecY, upVecZ] = struct.unpack('3f', data[40:40+12])
            [rollPos, pitchPos, YawPos] = struct.unpack('3f', data[52:52+12])
            heavedata = round(accZ,2) / 10.0
            swaydata = round(accX,2) / 10.0
            surgedata = round(accY,2) / 10.0
            
            rolldata = round(math.degrees(rollPos),2) / 10.0
            pitchdata = round(math.degrees(pitchPos),2) /10.0

            heavedata = _filter[0].compute(heavedata)
            swaydata = _filter[1].compute(swaydata)
            surgedata = _filter[2].compute(surgedata)
            rolldata = _filter[3].compute(rolldata)
            pitchdata = _filter[4].compute(pitchdata)

    except socket.timeout:
        pass
    except socket.error:
        print("UDP ERROR")
        break
    
    wm.simple_pose_update(rolldata, pitchdata, yawdata, heavedata, swaydata, surgedata)
    print('{0}, {1}, {2}, {3}, {4}, {5}'.format(rolldata, pitchdata, yawdata, heavedata, swaydata, surgedata))
    wm.get_backlog(True)

wm.close()
wm.get_backlog(True)
sc.close()

print('-------- FINISH WIZMO-TOOLS --------')
