import numpy as np
import cv2 as cv
import ast
from picamera2 import Picamera2
from Additional._00_Camera_Calibration_Modules import load_camera_config, CONFIG_PATH

def calibrate():
    #Initialize
    nRows = 6
    nCols = 8
    
    worldPtsCur = np.zeros((nRows*nCols,3),np.float32)
    worldPtsCur[:,:2] = np.mgrid[0:nRows,0:nCols].T.reshape(-1,2)

    configs = load_camera_config(CONFIG_PATH)

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
    main={"size": (480, 320), "format": "RGB888"}
)
    picam2.configure(config)
    picam2.start()

    exposure = int(configs["exposure"])
    gain_x10 = float(configs["gain"])
    initial_colour_gains = configs["initial_colour_gains"]

    a, b = map(float, initial_colour_gains.strip("()").split(","))

    initial_colour_gains = (float(a),float(b))

    print(a,b)

    exposure = max(exposure, 1)
    gain_x10 = max(gain_x10, 1)
    gain = gain_x10 / 10.0

    picam2.set_controls({
        "AeEnable": False,
        "AwbEnable": False,
        "ExposureTime": exposure,
        "AnalogueGain": gain,
        "ColourGains": initial_colour_gains
    })


    img_index = 0
    while True:
        imgBGR = picam2.capture_array()
        
        cv.imshow('Camera',imgBGR)
        imgGray = cv.cvtColor(imgBGR,cv.COLOR_BGR2GRAY)
        cornersFound, _ = cv.findChessboardCorners(imgGray,(nRows,nCols),None)

        if cornersFound:
            print('corners found')
            cv.imwrite('./chessImages/'+str(img_index)+'.jpg',imgBGR)
            img_index += 1
        if cv.waitKey(1) == ord('q'):
            break
    cv.destroyAllWindows()
    picam2.stop()


if __name__ == '__main__':
    calibrate()


