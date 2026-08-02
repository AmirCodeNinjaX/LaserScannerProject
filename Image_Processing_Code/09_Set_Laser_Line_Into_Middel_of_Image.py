from picamera2 import Picamera2
import cv2
import numpy as np
from Additional._00_Camera_Calibration_Modules import load_camera_config,CONFIG_PATH

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

lower_red1 = np.array([int(configs["hmin1"]),int(configs["smin"]),int(configs["vmin"])])
upper_red1 = np.array([int(configs["hmax1"]),int(configs["smax"]),int(configs["vmax"])])

lower_red2 = np.array([int(configs["hmin2"]),int(configs["smin"]),int(configs["vmin"])])
upper_red2 = np.array([int(configs["hmax2"]),int(configs["smax"]),int(configs["vmax"])])

def draw_center_vertical_line(frame, color=(0, 0, 255), thickness=2):
    if frame is None:
        return None

    height, width = frame.shape[:2]
    center_x = width // 2

    start_point = (center_x, 0)
    end_point = (center_x, height)

    cv2.line(frame, start_point, end_point, color, thickness)
    return frame

Is_Draw_Line = True
while True:
    frame = picam2.capture_array()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)

    frame = cv2.bitwise_and(frame, frame, mask=mask)

    #frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
    if(Is_Draw_Line):
        frame = draw_center_vertical_line(frame, color=(0,255,0),thickness=3)

    cv2.imshow("Camera", frame)


    key = cv2.waitKey(1) & 0xFF
    if(key == ord('l')):
        Is_Draw_Line = not(Is_Draw_Line)
    if(key == ord('s')):
        cv2.imwrite('output3.jpg',frame)
    if key == 27:
        break

picam2.stop()
cv2.destroyAllWindows()
