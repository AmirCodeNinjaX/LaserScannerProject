import cv2
import numpy as np
from picamera2 import Picamera2
from Additional._00_Camera_Calibration_Modules import CONFIG_PATH,update_camera_config,load_camera_config,MAX_WIDTH,MAX_HEIGHT

def nothing(x):
    pass

# Create a window
cv2.namedWindow('image')
#cv2.resizeWindow("Image", 720, 480)

# create trackbars for color change
cv2.createTrackbar('HMin1','image',0,179,nothing) # Hue is from 0-179 for Opencv
cv2.createTrackbar('HMin2','image',0,179,nothing)
cv2.createTrackbar('SMin','image',0,255,nothing)
cv2.createTrackbar('VMin','image',0,255,nothing)
cv2.createTrackbar('HMax1','image',0,179,nothing)
cv2.createTrackbar('HMax2','image',0,179,nothing)
cv2.createTrackbar('SMax','image',0,255,nothing)
cv2.createTrackbar('VMax','image',0,255,nothing)

# Set default value for MAX HSV trackbars.
cv2.setTrackbarPos('HMax1', 'image', 179)
cv2.setTrackbarPos('HMax2', 'image', 0)
cv2.setTrackbarPos('HMin2', 'image', 179)
cv2.setTrackbarPos('SMax', 'image', 255)
cv2.setTrackbarPos('VMax', 'image', 255)

# Initialize to check if HSV min/max value changes
hMin1 = hMin2 = sMin = vMin = hMax1 = hMax2 = sMax = vMax = 0
phMin1 = phMin2 = psMin = pvMin = phMax1 = phMax2 = psMax = pvMax = 0
 
# img = cv2.imread('Additional/Laser Tuning_screenshot_One_Side.png')
img = cv2.imread('3.png')
output = img
waitTime = 33


picam2 = Picamera2()

config = picam2.create_preview_configuration(
    main={"size": (480, 320), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

configs = load_camera_config(CONFIG_PATH)

exposure = int(configs["exposure"])
gain_x10 = float(configs["gain"])
initial_colour_gains = configs["initial_colour_gains"]
a, b = map(float, initial_colour_gains.strip("()").split(","))
initial_colour_gains = (float(a),float(b))
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


while(1):

    # get current positions of all trackbars
    hMin1 = cv2.getTrackbarPos('HMin1','image')
    hMin2 = cv2.getTrackbarPos('HMin2','image')
    sMin = cv2.getTrackbarPos('SMin','image')
    vMin = cv2.getTrackbarPos('VMin','image')

    hMax1 = cv2.getTrackbarPos('HMax1','image')
    hMax2 = cv2.getTrackbarPos('HMax2','image')
    sMax = cv2.getTrackbarPos('SMax','image')
    vMax = cv2.getTrackbarPos('VMax','image')

    # Set minimum and max HSV values to display
    lower1 = np.array([hMin1, sMin, vMin])
    upper1 = np.array([hMax1, sMax, vMax])

    lower2 = np.array([hMin2, sMin, vMin])
    upper2 = np.array([hMax2, sMax, vMax])

    rpi_Frame = picam2.capture_array()

    # Create HSV Image and threshold into a range.
    hsv1 = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv1, lower1, upper1) | cv2.inRange(hsv1, lower2, upper2)
    output1 = cv2.bitwise_and(img,img, mask= mask1)
    #
    hsv2 = cv2.cvtColor(rpi_Frame, cv2.COLOR_BGR2HSV)
    mask2 = cv2.inRange(hsv2, lower1, upper1) | cv2.inRange(hsv2, lower2, upper2)
    output2 = cv2.bitwise_and(rpi_Frame,rpi_Frame, mask= mask2)

    # Print if there is a change in HSV value
    if( (phMin1 != hMin1) | (phMin2 != hMin2) | (psMin != sMin) | (pvMin != vMin) | (phMax1 != hMax1) | (phMax2 != hMax2) | (psMax != sMax) | (pvMax != vMax) ):
        print("(hMin1 = %d , hMin2 = %d , sMin = %d, vMin = %d), (hMax1 = %d , hMax2 = %d , sMax = %d, vMax = %d)" % (hMin1 , hMin2 , sMin , vMin, hMax1, hMax2, sMax , vMax))
        phMin1 = hMin1
        phMin2 = hMin2
        psMin = sMin
        pvMin = vMin
        phMax1 = hMax1
        phMax2 = hMax2
        psMax = sMax
        pvMax = vMax


    h = min(output1.shape[0], output2.shape[0])

    imgres1 = cv2.resize(output1, (int(output1.shape[1] * h / output1.shape[0]), h))
    imgres2 = cv2.resize(output2, (int(output2.shape[1] * h / output2.shape[0]), h))

    result = np.hstack((imgres1, imgres2))

    h, w = result.shape[:2]

    # ?????? ???? ?????????
    scale = min(MAX_WIDTH / w, MAX_HEIGHT / h, 1.0)

    result = cv2.resize(
        result,
        (int(w * scale), int(h * scale)),
        interpolation=cv2.INTER_AREA
    )
    # Display output image
    cv2.imshow('image',result)

    # Wait longer to prevent freeze for videos.
    key = cv2.waitKey(waitTime) & 0xFF

    if(key == ord('c')):
        update_camera_config(CONFIG_PATH,{
            "HMin1":phMin1,
            "HMin2":phMin2,
            "SMin":psMin,
            "VMin":pvMin,
            "HMax1":phMax1,
            "HMax2":phMax2,
            "SMax":psMax,
            "VMax":pvMax
        })

    if key == ord('q'):
        break

cv2.destroyAllWindows()