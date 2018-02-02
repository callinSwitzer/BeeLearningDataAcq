#! python

import numpy as np
import cv2
import datetime
import PyCapture2 as fc2
import sys
import time
import os
import re
import skimage.io as io



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
    
def enableEmbeddedTimeStamp(cam, enableTimeStamp):
    embeddedInfo = cam.getEmbeddedImageInfo()
    if embeddedInfo.available.timestamp:
        cam.setEmbeddedImageInfo(timestamp = enableTimeStamp)
        if(enableTimeStamp):
            print("\nTimeStamp is enabled.\n")
        else:
            print("\nTimeStamp is disabled.\n")
            
    
def img2array(image):
    return(np.array(image.getData(), dtype="uint8").reshape( (image.getRows(), image.getCols()) ))


    
# display images via live preview for two cameras
def livePreview2(c, d):
    
    '''
    Previews images from two cameras --  triggered with arduino
    
    Args:
        c: camera 1, with recording started
        d: camera 2, with recording started

    Returns:
        NA
        
    '''
    cv2.namedWindow('image',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('image', 1000,800)
    while(True):
        stt = time.time()
        # Capture frame-by-frame
        image = c.retrieveBuffer()
        image2 = d.retrieveBuffer()
        img = np.concatenate((img2array(image), img2array(image2)), axis = 1)

        # Our operations on the frame come here
        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Display the resulting frame
        cv2.imshow('image', img)
        
        print(time.time() - stt)

        # break when "q" is pressed on keyboard
        if cv2.waitKey(1) & 0xFF == ord('q'):
            for jj in range(10):
                cv2.destroyAllWindows()
            break


def main():    
    # check number of cameras
    bus = fc2.BusManager()
    numCams = bus.getNumOfCameras()
    print("Number of cameras detected: ", numCams)
    if not numCams:
        #raise ValueError("Insufficient number of cameras. Exiting...")
        print("Insufficient number of cameras. Exiting...")
        exit()
        
   
    # print camera info
    c = fc2.Camera()
    c.connect(bus.getCameraFromIndex(0))
    printCameraInfo(c)

    d = fc2.Camera()
    d.connect(bus.getCameraFromIndex(1))
    printCameraInfo(d)
    
    # start capture
    enableEmbeddedTimeStamp(c, True)
    c.startCapture()
    enableEmbeddedTimeStamp(c, True)
    d.startCapture()
    
    # live preview
    livePreview2(c,d)
    
    
    # When everything done, release the capture
    #c.stopCapture()
    #c.disconnect()

   # d.stopCapture()
    #d.disconnect()
    #cv2.destroyAllWindows()
    
        
        

if __name__ == "__main__":
    main()
    print(c)