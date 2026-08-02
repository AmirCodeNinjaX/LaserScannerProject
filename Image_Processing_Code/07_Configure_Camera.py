from picamera2 import Picamera2
import cv2
import time
import numpy as np
from Additional._00_Camera_Calibration_Modules import update_camera_config,CONFIG_PATH


picam2 = Picamera2()

config = picam2.create_preview_configuration(
    main={"size": (480, 320), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

time.sleep(1.5)

initial_exposure = 200
initial_gain = 1.0
initial_colour_gains = (1.0, 1.0)

for _ in range(10):
    frame = picam2.capture_array()
    metadata = picam2.capture_metadata()
    time.sleep(0.05)

metadata = picam2.capture_metadata()

if "ExposureTime" in metadata:
    initial_exposure = int(metadata["ExposureTime"])

if "AnalogueGain" in metadata:
    initial_gain = float(metadata["AnalogueGain"])

if "ColourGains" in metadata and metadata["ColourGains"] is not None:
    cg = metadata["ColourGains"]
    if len(cg) >= 2:
        initial_colour_gains = (float(cg[0]), float(cg[1]))

initial_gain_x10 = int(round(initial_gain * 10))
if initial_gain_x10 < 1:
    initial_gain_x10 = 1

print("Auto detected values:")
print(f"ExposureTime = {initial_exposure} us")
print(f"AnalogueGain = {initial_gain:.2f}")
print(f"ColourGains = {initial_colour_gains}")

picam2.set_controls({
    "AeEnable": False,
    "AwbEnable": False,
    "ExposureTime": initial_exposure,
    "AnalogueGain": initial_gain,
    "ColourGains": initial_colour_gains
})

time.sleep(0.3)

window_name = "Laser Tuning"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 1080, 720)

max_exposure = max(5000, initial_exposure * 3)
max_gain_x10 = max(80, initial_gain_x10 * 3)

cv2.createTrackbar("Exposure(us)", window_name, initial_exposure, max_exposure, lambda x: None)
cv2.createTrackbar("Gain x10", window_name, initial_gain_x10, max_gain_x10, lambda x: None)

last_exposure = -1
last_gain = -1

while True:
    exposure = cv2.getTrackbarPos("Exposure(us)", window_name)
    gain_x10 = cv2.getTrackbarPos("Gain x10", window_name)

    exposure = max(exposure, 1)
    gain_x10 = max(gain_x10, 1)
    gain = gain_x10 / 10.0

    if exposure != last_exposure or gain != last_gain:
        picam2.set_controls({
            "AeEnable": False,
            "AwbEnable": False,
            "ExposureTime": exposure,
            "AnalogueGain": gain,
            "ColourGains": initial_colour_gains
        })
        last_exposure = exposure
        last_gain = gain
        time.sleep(0.05)

    frame = picam2.capture_array()
    bgr = frame # cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    #matrix, dist_Coff = load_camera_config('./config.cfg')
    #print(matrix)
    #print(dist_Coff)

    combined = bgr.copy()
    cv2.putText(combined, f"Exposure: {exposure} us", (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(combined, f"Gain: {gain:.2f}", (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow(window_name, combined)
    #cv2.imshow(window_name,frame)
    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord("q"):
        break
    elif key == ord("c"):
        update_camera_config(CONFIG_PATH,{
            "Exposure":exposure,
            "Gain":gain,
            "initial_colour_gains":initial_colour_gains
        })
        print(type(initial_colour_gains))
    elif key == ord("s"):
        filename = f"laser_exp{exposure}_gain{gain:.2f}.png"
        cv2.imwrite(filename, combined)
        print(f"Saved: {filename}")

cv2.destroyAllWindows()
picam2.stop()
