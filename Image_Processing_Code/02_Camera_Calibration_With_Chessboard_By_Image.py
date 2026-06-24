import numpy as np
import cv2 as cv
import glob
import os
import matplotlib.pyplot as plt
import configparser

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
    paramPath = os.path.join(curFolder,"config.cfg")

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


def save_camera_config(filename, camera_matrix, dist_coeffs=None):
    config = configparser.ConfigParser()
    
    # Convert matrix to string (comma-separated for readability)
    # We use flatten to make it a single line or keep it as is
    matrix_str = ','.join(map(str, camera_matrix.flatten()))
    
    config['CAMERA_PARAMS'] = {
        'intrinsic_matrix': matrix_str,
        'rows': str(camera_matrix.shape[0]),
        'cols': str(camera_matrix.shape[1])
    }
    
    if dist_coeffs is not None:
        config['CAMERA_PARAMS']['distortion_coefficients'] = ','.join(map(str, dist_coeffs.flatten()))

    with open(filename, 'w') as configfile:
        config.write(configfile)
    print(f"Configuration saved to {filename}")

if __name__ == '__main__':
    runCalibration()


