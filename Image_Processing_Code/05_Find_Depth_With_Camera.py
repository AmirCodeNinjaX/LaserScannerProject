import cv2
import numpy as np
from Additional._00_Camera_Calibration_Modules import load_camera_config
from time import sleep

# -------- Camera parameters --------
K, dist = load_camera_config('Additional/config.cfg')

#dist = np.array([-0.1,0.05,0,0,0])  # distortion coefficients

K_inv = np.linalg.inv(K)

# فاصله لیزر تا دوربین (متر)
baseline = 0.062

# زاویه صفحه لیزر
laser_angle = np.deg2rad(90)

laser_normal = np.array([
    np.sin(laser_angle),
    0,
    -np.cos(laser_angle)
])

laser_point = np.array([baseline,0,0])


def intersect_ray_plane(ray, plane_normal, plane_point):
    t = np.dot(plane_point, plane_normal) / np.dot(ray, plane_normal)
    return ray * t


cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # -------- Undistort --------
    frame = cv2.undistort(frame, K, dist)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 150, 180])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 150, 180])
    upper_red2 = np.array([180, 255, 255])

    mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)

    h,w = mask.shape

    points3d = []

    # -------- استخراج خط لیزر --------
    for x in range(0,w,5):   # هر 5 پیکسل یک نمونه
        ys = np.where(mask[:,x] > 0)[0]

        if len(ys) == 0:
            continue

        y = int(np.mean(ys))

        pixel = np.array([x,y,1.0])
        ray = K_inv @ pixel
        ray = ray / np.linalg.norm(ray)

        p3d = intersect_ray_plane(ray, laser_normal, laser_point)

        dist_cam = np.linalg.norm(p3d)

        print(dist_cam)
        #sleep(1)

        points3d.append(p3d)

        cv2.circle(frame,(x,y),2,(0,255,0),-1)
        cv2.putText(frame,f"{dist_cam:.2f}m",(x,y),
                    cv2.FONT_HERSHEY_SIMPLEX,0.3,(0,255,0),1)

    cv2.imshow("frame",frame)
    cv2.imshow("mask",mask)

    if cv2.waitKey(5)==27:
        break

cap.release()
cv2.destroyAllWindows()
