import os
import cv2 as cv
from Additional._00_Camera_Calibration_Modules import load_camera_config,RemoveDistotion,CONFIG_PATH

def RunRemoveDistotion():
    curFolder = os.path.dirname(os.path.abspath(__file__))
    paramPath = os.path.join(curFolder,CONFIG_PATH)

    configs = load_camera_config(paramPath)
    CamMatrix = configs["intrinsic_matrix"]
    dist_Coeff = configs["distortion_coefficients"]

    print(CamMatrix)
    print(dist_Coeff)

    img = cv.imread('Image Path') # Change This Parameter
    img = RemoveDistotion(img,CamMatrix,dist_Coeff)
    while True:
        cv.imshow("test",img)
        key = cv.waitKey(1) & 0xFF
        if key == 27 or key == ord("q"):
            break


if __name__ == '__main__':
    RunRemoveDistotion()