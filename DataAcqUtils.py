"""
Utility functions for Bee Flower Choice Data Acquisition
"""

# import packages and print some version information

import matplotlib.pyplot as plt
plt.ion()
import numpy as np
from PyDAQmx import * #works with python 3.5 -- need to install NiDACmx (takes like a day to download)
import PyCapture2 as fc2
from sys import exit
import serial
import time
import os
import peakutils 
import msvcrt
import winsound
import shutil
import pandas as pd
import skimage.io as io
import sys
from datetime import datetime
import glob

print(sys.version)
now = datetime.now()
print("last run on " + str(now))

outDir = "C:\\Users\\Combes4\\Desktop\\temp3\\"

if not os.path.isdir(outDir):
    os.mkdir(outDir)
    print('new directory created for data: ' + str(outDir))
else: 
    print('directory where data will be deposited: '  + str(outDir))

print("_____________________________________________")

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


# check serial connections
assert(serial_ports() == ['COM3', 'COM5']),"Serial Ports for arduino unavailable"

# connect to Arduinos
PORT1 = "COM3"
connected1 = False
ser1 = serial.Serial(PORT1,115200)
while not connected1:
    serin1 = ser1.read()
    connected1 = True
    print("connected to arduino on " + PORT1)

PORT2 = "COM5"
connected2 = False
ser2 = serial.Serial(PORT2,115200)
while not connected2:
    serin2 = ser2.read()
    connected2 = True
    print("connected to arduino on " + PORT2)

class accelDta:
    
    '''read accelerometer data, fft, and plot'''
    
    def __init__(self, accNum = "Dev2/ai0", N_samples = 20000, log_rate = 200000.0):
        self.data = np.zeros((N_samples,), dtype=np.float64)
        self.N_samples = N_samples
        self.log_rate = log_rate
        self.read = int32()
        self.accNum = accNum
    
    
    def readAccel(self, ): 
        taskHandle = TaskHandle()

        DAQmxCreateTask("", byref(taskHandle))
        # I have an piezoelectric accelerometer pluged into channel ai1 with range +/-10V
        DAQmxCreateAIVoltageChan(taskHandle, self.accNum, 
                                 "Accelerometer", DAQmx_Val_Diff, 
                                 -10.0, 10.0, DAQmx_Val_Volts, None)
        DAQmxCfgSampClkTiming(taskHandle, "", self.log_rate, 
                              DAQmx_Val_Rising, 
                              DAQmx_Val_FiniteSamps, self.N_samples)

        DAQmxStartTask(taskHandle)
        DAQmxReadAnalogF64(taskHandle, self.N_samples, 10.0, 
                           DAQmx_Val_GroupByChannel, self.data, 
                           self.N_samples, byref(self.read), None)

        if taskHandle:
            DAQmxStopTask(taskHandle);
            DAQmxClearTask(taskHandle);
            
        # get amplitude    
        self.amp = np.max(self.data) - np.min(self.data)

    def FFT(self, fmin = 20, fmax= 450):
        n =int(len(self.data))
        k = np.arange(n, step = 1)
        T = n/self.log_rate
        frq = k/T # two sides frequency range
        frq = frq[range(int(n/2))] # one side frequency range

        # trim frq
        keepInd = (frq > fmin) & (frq < fmax)
        frqKeep = frq[keepInd]

        Y = np.fft.fft(self.data)/n # fft computing and normalization
        Y = Y[range(int(n/2))]

        # remove Y that is outside the frequency rang of interest
        Ykeep = Y[keepInd]



        # calculate top frequency
        ind = np.argpartition(abs(Ykeep), -4)[-4:]
        # Find highest point on the spectrum
        peakFrq = frqKeep[ind[::-1]]
        pwr = (abs(Ykeep)[ind[::-1]])

        domPK = [x for (y,x) in sorted(zip(pwr,peakFrq), reverse = True)][0]

        domPkPwr = pwr[peakFrq == domPK]

        self.frq = frq
        self.peakFrq = peakFrq
        self.pwr = pwr
        self.domPK = domPK
        self.domPkPwr = domPkPwr 
        self.Y = Y
        


    def plotFFT(self, fmin =0, fmax = 1000, reward = 'F'):
         # create subplot 1
        ax1 = plt.subplot(121)
        ax1.plot(np.array(range(len(self.data)))/ float(self.log_rate), self.data)
        ax1.set_ylabel("Volts")
        ax1.set_xlabel("time (s)")
        if reward == 'T':
            ax1.set_facecolor('grey')

        # create subplot 2
        ax2 = plt.subplot(122)
        ax2.plot(self.frq,abs(self.Y),'r')
        ax2.plot(self.peakFrq,self.pwr, 'ro')
        ax2.set_xlim(fmin, fmax)
        ax2.set_ylabel('power')
        ax2.set_xlabel('frequency')
        ax2.plot(self.domPK, self.domPkPwr,'o', color = 'black', markersize = 5)
        ax2.annotate(str(self.domPK) + ' Hz', 
                     xy=(self.domPK, self.domPkPwr), 
                     xytext=(self.domPK + 40, 
                             self.domPkPwr- 0.0001), size = 12)
        plt.tight_layout()
        plt.show()


## read in data, and take a photo if accel power is high enough
class processAndReward:
    
    '''Process data and reward bee if the bee meets the criteria
       Save amplitude, frequency information
    '''
    
    def __init__(self, ampThresh = 0.07, accNum1 = "Dev2/ai0", 
                 accNum2= "Dev2/ai1", rewardMin = 220, rewardMax = 450, 
                reward1 = True, reward2 = True, saveDirectory = "C:\\Users\\Combes4\\Desktop"):
        self.ampThresh = ampThresh
        acc1 = accelDta(accNum1)
        acc2 = accelDta(accNum2)
        self.rewardMin = rewardMin
        self.rewardMax = rewardMax
        self.reward1 = reward1
        self.reward2 = reward2
        self.startTime = str(datetime.now().strftime("%Y_%m_%d__%H_%M_%S_%f")[:-3]) # time with milliseconds
        self.treatment = accNum1 + "_" + str(reward1) +  "__" + accNum2 + "_" + str(reward2)
        self.LastVisitTime = time.time()
        self.rewardCounter = 0
        self.saveDirectory = saveDirectory
        
        
        # refref: make new folder, and change put all data in that folder
        newpath =os.path.join(saveDirectory, self.startTime)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        else:
            raise ValueError('Cannot create new folder')
        
        self.saveDirectory = newpath
        
           
        # open file and write header
        self.f = open(os.path.join(self.saveDirectory, self.startTime + ".csv"), 'a')
        header = "Amp_V"+ "," +  "freq_Hz"+ "," +  "accNum"+ "," + "rewardStatus" + "," +  "timestamp" + "," + "treatment" +  "\n"
        self.f.write(header)
        
        
        
    def saveAmpFreq(self, accNum):
        self.timestamp = str(datetime.now().strftime("%Y_%m_%d__%H_%M_%S_%f")[:-3])
        
        var1 = (str(accNum.amp) + "," + 
                str(accNum.domPK) + "," 
                + accNum.accNum + ","+ str(self.rewardYesNo) + "," +
                self.timestamp + "," +
                self.treatment + 
                '\n')
        self.f.write(var1)
    

        
    # if frequency is in a certain range, deliver reward
    def reward(self, gg, serialPort, reward = True):
        self.rewardYesNo = reward
        if((gg.domPK > self.rewardMin) and (gg.domPK < self.rewardMax) and (gg.amp > self.ampThresh)):
            written = serialPort.write("s".encode("utf-8"))
            written = serialPort.write("v".encode("utf-8"))
            self.saveAmpFreq(gg)
           
            # write raw accel to file
            np.savetxt(os.path.join(self.saveDirectory, self.timestamp + ".txt"), 
                       (np.array(range(len(gg.data)))/ float(gg.log_rate), gg.data), delimiter = ' ')
            
            print(gg.amp, gg.accNum)
            gg.plotFFT()
            return(True)
        else:
            return(False)
        
    def procReward(self, acc1, acc2):
        # read in data
        [j.readAccel() for j in [acc1, acc2]]
        
        # only go on if the reading is above amplitude cutoff
        # refref should adjust this, based on acc sensitivity
        if((acc1.amp > self.ampThresh) or (acc2.amp > self.ampThresh)):
            
            
            # calculate fft
            [k.FFT() for k in [acc1, acc2]]
            
            # only proceed if fft signal is strong
            if (acc1.domPkPwr > 0.001) or (acc2.domPkPwr > 0.001):
                #refref save raw accel data
                
        
                # reward only one accel at once
                if(acc1.amp > acc2.amp):
                    if self.reward(acc1, ser2, reward = self.reward1):
                        self.rewardCounter += 1
                        self.LastVisitTime = time.time()
                        
                        
                else:
                    if self.reward(acc2, ser1, reward = self.reward2):
                        self.rewardCounter +=1
                        self.LastVisitTime = time.time()
                        
                        
def run_trial(reward_1, reward_2, acc1, acc2):
    while msvcrt.kbhit():
        msvcrt.getch()
        print('clearing characters ...')

    # instantiate
    procR = processAndReward(reward1 = reward_1, reward2 = reward_2, saveDirectory = "C:\\Users\\Combes4\\Desktop\\temp3\\")

    # start timer

    timeOUT = 5.0 * 60 # seconds
    close = False


    while(True):
        procR.procReward(acc1, acc2)

        # break loop if someone presses the 'q' while in terminal
        if msvcrt.kbhit():
            if msvcrt.getch() == b'q':
                close = True
                print("keyboard q pressed")

        elif (time.time() - procR.LastVisitTime  > timeOUT):

            close = True
            print("time out")

        elif (procR.rewardCounter >= 100):
            close = True
            print("reached 100 rewards")

        if close:
            procR.f.close()
            print('now quitting loop')
            print(r"data saved to " + str(procR.saveDirectory))
            #print('Experiment started at ' + str(procR.startTime))
            for i in range(5):
                winsound.Beep(450,100)
            break
            
    return(procR.f.name)