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
    HIGH_PASS_1ST = 1
    HIGH_PASS_2ND = 2

    def __init__(self, filterMode, sampleRate, o, z=0.0):
        self.ft_o = o
        self.ft_z = z
        self.sampleRate = sampleRate

        self.a1 = 0
        self.a2 = 0
        self.a3 = 0
        self.b1 = 0
        self.b2 = 0
        self.in_prev = [0,0]
        self.out_prev = [0,0]

        if filterMode == self.LOW_PASS:
            self._lowPassFilter(sampleRate,self.ft_o,self.ft_z)
        elif filterMode == self.HIGH_PASS_1ST:
            self._highPassIIRFilter1(sampleRate,self.ft_o,self.ft_z)
        else:
            self._highPassIIRFilter2(sampleRate,self.ft_o)

    def compute(self, in_data) -> float:
        ret = self.a1 * in_data + self.a2 * self.in_prev[0] + self.a3 * self.in_prev[1] - \
          self.b1 * self.out_prev[0] - self.b2 * self.out_prev[1]

        self.in_prev[1] = self.in_prev[0]
        self.in_prev[0] = in_data
        self.out_prev[1] = self.out_prev[0]
        self.out_prev[0] = ret
        return ret

    def _lowPassFilter(self, sample_rate, Wn, Z):
        # H(s) = Wn^2 / ( s^2 + 2*Z*Wn s + Wn^2) 
        alpha = Wn*Wn
        beta = 2.0*Z*Wn
        Wac = math.tan(Wn/(sample_rate*2.0))
        norm = 1.0/(Wac*Wac) + beta/Wac + alpha
        self.a1 = alpha/norm
        self.a2 = 2.0*alpha/norm
        self.a3 = alpha/norm
        self.b1 = (-2.0/(Wac*Wac)+2.0*alpha)/norm
        self.b2 = (1.0/(Wac*Wac)-beta/Wac+alpha)/norm

    def _highPassIIRFilter2(self,sample_rate, Wb):
        # H(s) = s / s + Wb
        # Calculate 1st order IIR filter coefficients by bilinear z-transform
        Wac = math.tan(Wb/(sample_rate*2.0))
        norm = 1.0+Wb*Wac
	
        self.a1 = 1.0/norm
        self.a2 = -1.0/norm
        self.a3 = 0.0
        self.b1 = (-1.0+Wb*Wac)/norm
        self.b2 = 0.0

    def _highPassIIRFilter1(self, sample_rate, Wn, Z):
        # H(s) = s^2 / ( s^2 + 2*Z*Wn s + Wn^2)   
        # Calculate 2nd order IIR filter coefficients by bilinear z-transform
        Wac = math.tan(Wn/(sample_rate*2.0))
        norm = 1.0+2.0*Z*Wn*Wac+Wn*Wn*Wac*Wac
	
        self.a1 = 1.0/norm
        self.a2 = -2.0/norm
        self.a3 = 1.0/norm
        self.b1 = (-2.0+2.0*Wn*Wn*Wac*Wac)/norm
        self.b2 = (1.0-2.0*Z*Wn*Wac+Wn*Wn*Wac*Wac)/norm
#-----------------------------------------------------------

print('-------- START WIZMO-TOOLS --------')

HOST = '127.0.0.1'
PORT = 4444

sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sc.bind(('', PORT))
sc.settimeout(0.5)

_filter = [IIRFilter(IIRFilter.LOW_PASS, 100, 3.0, 0.707),
           IIRFilter(IIRFilter.LOW_PASS, 100, 3.0, 0.707),
           IIRFilter(IIRFilter.LOW_PASS, 100, 3.0, 0.707),
           IIRFilter(IIRFilter.LOW_PASS, 100, 2.95, 0.707),
           IIRFilter(IIRFilter.LOW_PASS, 100, 2.95, 0.707),
           IIRFilter(IIRFilter.LOW_PASS, 100, 2.95, 0.707)]

try:
    wm = wizmo.wizmo(True)
except FileNotFoundError:
    print("WIZMO DLL NOT FOUND ERROR!")
    exit()

wm.starter('')
wm.simple_motio_power_update(1.0,1.0)
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
