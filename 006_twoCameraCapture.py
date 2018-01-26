# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# setup arduino
import matplotlib.pyplot as plt
import numpy as np
import cv2

import datetime

import PyCapture2 as fc2
import sys

import time

import os
import peakutils 
import msvcrt
import winsound
import shutil
import pandas as pd
import re

import skimage.io as io

print("last update: "  +  str(datetime.datetime.now()))

# capture image with point grey camera
bus = fc2.BusManager()
numCams = bus.getNumOfCameras()
print("Number of cameras detected: ", numCams)
if not numCams:
    print("Insufficient number of cameras. Exiting...")
    exit()
    
def enableEmbeddedTimeStamp(cam, enableTimeStamp):
    embeddedInfo = cam.getEmbeddedImageInfo()
    if embeddedInfo.available.timestamp:
        cam.setEmbeddedImageInfo(timestamp = enableTimeStamp)
        if(enableTimeStamp):
            print("\nTimeStamp is enabled.\n")
        else:
            print("\nTimeStamp is disabled.\n")
            
def printCameraInfo(cam):
    camInfo = cam.getCameraInfo()
    print("\n*** CAMERA INFORMATION ***\n")
    print("Serial number - ", camInfo.serialNumber)
    print("Camera model - ", camInfo.modelName)
    print("Camera vendor - ", camInfo.vendorName)
    print("Sensor - ", camInfo.sensorInfo)
    print("Resolution - ", camInfo.sensorResolution)
    print("Firmware version - ", camInfo.firmwareVersion)
    print("Firmware build time - ", camInfo.firmwareBuildTime)
    fRateProp = cam.getProperty(fc2.PROPERTY_TYPE.FRAME_RATE)
    print("FrameRate - ", fRateProp.absValue)
    print()
    
    
    
c = fc2.Camera()
c.connect(bus.getCameraFromIndex(0))
printCameraInfo(c)

d = fc2.Camera()
d.connect(bus.getCameraFromIndex(1))
printCameraInfo(d)


# When everything done, release the capture
#c.stopCapture()
c.disconnect()

#d.stopCapture()
d.disconnect()
cv2.destroyAllWindows()