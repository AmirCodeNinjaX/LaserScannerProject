from picamera2 import Picamera2
import cv2
import numpy as np
import time
from Additional._00_Camera_Calibration_Modules import load_camera_config,CONFIG_PATH,fit_line_abc,draw_line_from_abc,mask_by_two_points,apply_threshold,keep_max_pixel_per_row,split_frame_height,concat_images_vertical,crop_by_two_points,RemoveDistotion

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

Camera_Matrix = configs["intrinsic_matrix"]
Dist_Coeff = configs["distortion_coefficients"]


prev_time = time.perf_counter()
while True:
    frame = picam2.capture_array()
    #frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
    #frame = draw_center_vertical_line(frame, color=(0,255,0),thickness=3)

    frame = RemoveDistotion(frame,Camera_Matrix,Dist_Coeff)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)

    frame2 = cv2.bitwise_and(frame, frame, mask=mask)

    Splited_Frames = split_frame_height(frame2,1)
    #for i in range(len(Splited_Frames)):

    splited_frame = Splited_Frames[0]

    r,g,r = cv2.split(splited_frame)
    #cv2.imshow(str(r.shape),r)
    frame3 = r
    # cv2.imshow("g",g)
    # cv2.imshow("b",b)

    #frame3 = cv2.cvtColor(splited_frame, cv2.COLOR_BGR2GRAY)
    
    ret, (a,b,c) = fit_line_abc(frame3)

    if(not(ret)): continue
    frame4 ,(pt1,pt2) = draw_line_from_abc(frame3,a,b,c,(0,255,0))

    frame5 = mask_by_two_points(frame3,pt1,pt2,20)
    #frame5 = crop_by_two_points(frame3,pt1,pt2,20)
    if(frame5 is None): continue
    frame6 = apply_threshold(frame5,0)

    frame7 = keep_max_pixel_per_row(frame6)
    #Splited_Frames[i] = frame7

    #Final_Frame = concat_images_vertical(Splited_Frames)

    #current_time = time.perf_counter()
    #fps = 1.0 / (current_time - prev_time)
    #print(fps)
    # cv2.putText(
    #     frame7,
    #     f"FPS: {fps:.1f}",
    #     (10, 30),
    #     cv2.FONT_HERSHEY_SIMPLEX,
    #     1,
    #     (0, 255, 0),
    #     2,
    #     cv2.LINE_AA)
    #cv2.imshow("Image1",frame)
    #cv2.imshow("image2",frame2)
    cv2.imshow("image3",frame3)
    #cv2.imshow("image4",frame4)
    #cv2.imshow("image5",frame5)
    #cv2.imshow("image6",frame6)
    cv2.imshow("image7",frame7)
    #cv2.imshow(str(fps),frame7)
    #cv2.imshow("Final Frame",Final_Frame)
    #cv2.imwrite('output.jpg',frame3)
    #cv2.imwrite('output1.jpg',frame4)
    if cv2.waitKey(1) & 0xFF == 27:
        break

picam2.stop()
cv2.destroyAllWindows()
