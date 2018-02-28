

import numpy as np
import cv2
import datetime
import PyCapture2 as fc2
import sys
import time
import os
import re
import skimage.io as io


import beeDataAcq.cameraSetup as cs


# avi recording function
bus = fc2.BusManager()
numCams = bus.getNumOfCameras()
    
    
c = fc2.Camera()
c.connect(bus.getCameraFromIndex(0))
d = fc2.Camera()
d.connect(bus.getCameraFromIndex(1))

# start capture
cs.enableEmbeddedTimeStamp(c, True)
c.startCapture()
cs.enableEmbeddedTimeStamp(c, True)
d.startCapture()


def saveAviHelper2(cam, cam2, fileFormat, fileName, fileName2, frameRate, maxImgs = 500):
    
    numImages = 0

    avi = fc2.AVIRecorder()
    avi2 = fc2.AVIRecorder()

    for i in range(maxImgs):
        
        try:
            image = cam.retrieveBuffer()
            image2 = cam2.retrieveBuffer()
        except fc2.Fc2error as fc2Err:
            print("Error retrieving buffer : ", fc2Err)
            continue

        print("Grabbed image {}".format(i))

        if (i == 0):
            if fileFormat == "AVI":
                avi.AVIOpen(fileName, frameRate)
                avi2.AVIOpen(fileName2, frameRate)
            elif fileFormat == "MJPG":
                avi.MJPGOpen(fileName, frameRate, 75)
                avi2.MJPGOpen(fileName2, frameRate, 75)
            elif fileFormat == "H264":
                avi.H264Open(fileName, frameRate, image.getCols(), image.getRows(), 1000000)
                avi2.H264Open(fileName2, frameRate, image2.getCols(), image2.getRows(), 1000000)
            else:
                print("Specified format is not available.")
                return
            
            # show still image
            img = np.concatenate((cs.img2array(image), cs.img2array(image2)), axis = 1)

            # Display the resulting frame
            cv2.imshow('image', img)

        # break when "q" is pressed on keyboard
        if cv2.waitKey(1) & 0xFF == ord('q'):
            for jj in range(10):
                cv2.destroyAllWindows()
            break

        # refref add image timestamp

        avi.append(image)
        avi2.append(image2)
        numImages += 1
        print("Appended image {}...".format(i))

    # close windows if loop ends
    for jj in range(10):
        cv2.destroyAllWindows()
        
    print("Appended {} images to {} file: {}...".format(numImages, fileFormat, fileName))
    avi.close()
    avi2.close()
    
def main():
    
    directory = os.path.join("C:\\Users\\Combes4\Desktop\\temp3")
    movieID = str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S_%f")[:-3])
    fileName = os.path.join(directory,   movieID + "_cam1" + ".avi")
    fileName2 = os.path.join(directory,  movieID + "_cam2" + ".avi")
    saveAviHelper2(c,d, "AVI", fileName.encode("utf-8"), fileName2.encode("utf-8"), 10, maxImgs = 10000)

if __name__ == "__main__":
    main()
   