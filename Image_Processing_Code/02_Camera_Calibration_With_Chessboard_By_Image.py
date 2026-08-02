import numpy as np
import cv2 as cv
import glob
import os
from Additional._00_Camera_Calibration_Modules import update_camera_config,CONFIG_PATH

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
        imgBGR = cv.imread(curImgPath)
        imgGray = cv.cvtColor(imgBGR,cv.COLOR_BGR2GRAY)
        cornersFound, cornersOrg = cv.findChessboardCorners(imgGray,(nCols,nRows),None)

        if cornersFound:
            worldPtsList.append(worldPtsCur)
            cornersRefind = cv.cornerSubPix(imgGray,cornersOrg,(11,11),(-1,-1),termCriteria)
            imgPtsList.append(cornersRefind)
            if ShowPics:
                cv.drawChessboardCorners(imgBGR,(nCols,nRows),cornersRefind,cornersFound)
                cv.imshow("Chessboard",imgBGR)
                cv.waitKey(300)
        
    cv.destroyAllWindows()

    #Calibrait
    repError,camMatrix,distCoeff,_,_ = cv.calibrateCamera(worldPtsList,imgPtsList,imgGray.shape[::-1],None,None)
    print("Camera Matrix: \n",camMatrix)
    print("Camera Distortion Coeffitiont: \n",distCoeff)
    print("Reproj Error (pixels): {:.4f}".format(repError))

    #Save Calibration Parameters
    update_camera_config(CONFIG_PATH,{
        "intrinsic_matrix":camMatrix,
        'rows': camMatrix.shape[0],
        'cols': camMatrix.shape[1],
        "distortion_coefficients":distCoeff
    })




if __name__ == '__main__':
    calibrate(ShowPics=True)


