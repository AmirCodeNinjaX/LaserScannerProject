import numpy as np
import cv2 as cv
import glob
import os
import matplotlib.pyplot as plt
import configparser
from Additional._00_Camera_Calibration_Modules import save_camera_config

def calibrate(ShowPics=True):
    #ReadImage
    root = os.getcwd()
    calibrationDir = os.path.join(root,"ChessImages")
    imagePathlist = glob.glob(os.path.join(calibrationDir,'*.jpg'))

    #Initialize
    nRows = 8
    nCols = 6
    termCriteria = (cv.TERM_CRITERIA_EPS+cv.TERM_CRITERIA_MAX_ITER,30,0.001)
    worldPtsCur = np.zeros((nRows*nCols,3),np.float32)
    worldPtsCur[:,:2] = np.mgrid[0:nCols,0:nRows].T.reshape(-1,2)
    worldPtsList = []
    imgPtsList = []

    #FindCorners
    for curImgPath in imagePathlist:
        # print(curImgPath)
        imgBGR = cv.imread(curImgPath)
        imgGray = cv.cvtColor(imgBGR,cv.COLOR_BGR2GRAY)
        # cv.imshow('bgr image',imgBGR)
        # cv.imshow('grayscale image',imgGray)
        cornersFound, cornersOrg = cv.findChessboardCorners(imgGray,(nCols,nRows),None)

        if cornersFound:
            # print('corners found')
            worldPtsList.append(worldPtsCur)
            cornersRefind = cv.cornerSubPix(imgGray,cornersOrg,(11,11),(-1,-1),termCriteria)
            imgPtsList.append(cornersRefind)
            if ShowPics:
                cv.drawChessboardCorners(imgBGR,(nCols,nRows),cornersRefind,cornersFound)
                cv.imshow("Chessboard",imgBGR)
                cv.waitKey(300)
        
    cv.destroyAllWindows()


    #Calibrait
    repError,camMatrix,distCoeff,rvecs,tvecs = cv.calibrateCamera(worldPtsList,imgPtsList,imgGray.shape[::-1],None,None)
    print("Camera Matrix: \n",camMatrix)
    print("Reproj Error (pixels): {:.4f}".format(repError))

    #Save Calibration Parameters
    curFolder = os.path.dirname(os.path.abspath(__file__))
    paramPath = os.path.join(curFolder,"Additional\\config.cfg")

    save_camera_config(paramPath,camMatrix,distCoeff)

    # np.savez(paramPath,
    #          repError=repError,
    #          camMatrix=camMatrix,
    #          distCoeff=distCoeff,
    #          rvecs=rvecs,
    #          tvecs=tvecs)
    return camMatrix,distCoeff


def runCalibration():
    calibrate(ShowPics=True)


if __name__ == '__main__':
    runCalibration()


