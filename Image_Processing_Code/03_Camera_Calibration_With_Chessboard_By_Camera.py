import numpy as np
import cv2 as cv
import glob
import os
import matplotlib.pyplot as plt

def calibrate(ShowPics=True,Camera_Index=0):
    #ReadImage
    root = os.getcwd()
    calibrationDir = os.path.join(root,"ChessImages")
    imagePathlist = glob.glob(os.path.join(calibrationDir,'*.jpg'))

    #Initialize
    nRows = 6
    nCols = 8
    termCriteria = (cv.TERM_CRITERIA_EPS+cv.TERM_CRITERIA_MAX_ITER,30,0.001)
    worldPtsCur = np.zeros((nRows*nCols,3),np.float32)
    worldPtsCur[:,:2] = np.mgrid[0:nRows,0:nCols].T.reshape(-1,2)
    worldPtsList = []
    imgPtsList = []

    #FindCorners
    # for curImgPath in imagePathlist:
    #     print(curImgPath)
    
    cam = cv.VideoCapture(Camera_Index)
    img_index = 0
    while True:
        ret, imgBGR = cam.read()
        if(not(ret)): continue
        cv.imshow('Camera',imgBGR)
        imgGray = cv.cvtColor(imgBGR,cv.COLOR_BGR2GRAY)
        # cv.imshow('bgr image',imgBGR)
        # cv.imshow('grayscale image',imgGray)
        cornersFound, cornersOrg = cv.findChessboardCorners(imgGray,(6,7),None)

        if cornersFound:
            print('corners found')
            cv.imwrite('chessImages\\'+str(img_index)+'.jpg',imgBGR)
            img_index += 1
            # worldPtsList.append(worldPtsCur)
            # cornersRefind = cv.cornerSubPix(imgGray,cornersOrg,(11,11),(-1,-1),termCriteria)
            # imgPtsList.append(cornersRefind)
            # if ShowPics:
            #     cv.drawChessboardCorners(imgBGR,(nRows,nCols),cornersRefind,cornersFound)
            #     cv.imshow("Chessboard",imgBGR)
            #     cv.waitKey(300)
        # if cv.waitKey(1) == ord('s'):
        #     cv.imwrite(img_index+'.jpg')
        #     img_index += 1
        if cv.waitKey(1) == ord('q'):
            break
    cv.destroyAllWindows()
    exit()


    #Calibrait
    repError,camMatrix,distCoeff,rvecs,tvecs = cv.calibrateCamera(worldPtsList,imgPtsList,imgGray.shape[::-1],None,None)
    print("Camera Matrix: \n",camMatrix)
    print("Reproj Error (pixels): {:.4f}".format(repError))

    #Save Calibration Parameters
    curFolder = os.path.dirname(os.path.abspath(__file__))
    paramPath = os.path.join(curFolder,"calibration.npz")
    np.savez(paramPath,
             repError=repError,
             camMatrix=camMatrix,
             distCoeff=distCoeff,
             rvecs=rvecs,
             tvecs=tvecs)
    return camMatrix,distCoeff


def runCalibration():
    calibrate(ShowPics=False)


if __name__ == '__main__':
    runCalibration()


