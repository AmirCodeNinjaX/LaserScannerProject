import configparser
import numpy as np
import io
import os
import cv2 as cv
import matplotlib.pyplot as plt
from _00_Camera_Calibration_Modules import load_camera_config


def RemoveDistotion(camMatirx, dist_Coeff,Camera_Index=0):
    # root = os.getcwd()
    # imgPath = os.path.join(root,"DistortionImage//2.jpg")
    # img = cv.imread(imgPath)
    cam = cv.VideoCapture(Camera_Index)
    while True:
        ret,img = cam.read()

        if(not(ret)): continue

        height, width = img.shape[:2]
        CameraMatrixNew, _ = cv.getOptimalNewCameraMatrix(camMatirx, dist_Coeff, (width, height), 1, (width, height))
        imgUndist = cv.undistort(img, camMatirx, dist_Coeff, None, CameraMatrixNew)

        # Draw the line to see Distotion Change
        # cv.line(img,(1769,103),(1730,922),(255,255,255),2)
        # cv.line(imgUndist,(1769,103),(1730,922),(255,255,255),2)


        plt.figure()
        plt.subplot(121)
        plt.imshow(img)
        plt.subplot(122)
        plt.imshow(imgUndist)
        plt.show()

def RunRemoveDistotion():
    curFolder = os.path.dirname(os.path.abspath(__file__))
    paramPath = os.path.join(curFolder,"config.cfg")

    CamMatrix, dist_Coeff = load_camera_config(paramPath)
    print(CamMatrix)
    print(dist_Coeff)

    RemoveDistotion(CamMatrix, dist_Coeff)


if __name__ == '__main__':
    RunRemoveDistotion()