import configparser
import numpy as np
import os
import cv2 as cv

CONFIG_PATH = "./Additional/config.cfg"
MAX_WIDTH = 1080
MAX_HEIGHT = 720

def update_camera_config(filename, params_dict, section='CAMERA_PARAMS'):
    config = configparser.ConfigParser()

    if os.path.exists(filename):
        config.read(filename)

    if not config.has_section(section):
        config.add_section(section)

    for key, value in params_dict.items():
        if isinstance(value, np.ndarray):
            value = ','.join(map(str, value.flatten()))
        config.set(section, str(key), str(value))

    with open(filename, 'w') as configfile:
        config.write(configfile)

    print(f"Configuration updated in {filename}")

def load_camera_config(filename, section='CAMERA_PARAMS'):
    config = configparser.ConfigParser()
    config.read(filename)

    if not config.has_section(section):
        return {}

    data = dict(config[section])

    result = {}

    if 'intrinsic_matrix' in data and 'rows' in data and 'cols' in data:
        rows = int(data['rows'])
        cols = int(data['cols'])
        result['intrinsic_matrix'] = np.fromstring(
            data['intrinsic_matrix'], sep=','
        ).reshape(rows, cols)
        result['rows'] = rows
        result['cols'] = cols

    if 'distortion_coefficients' in data:
        result['distortion_coefficients'] = np.fromstring(
            data['distortion_coefficients'], sep=','
        )

    for key, value in data.items():
        if key not in result and key not in ('intrinsic_matrix', 'distortion_coefficients'):
            if key == 'rows':
                result[key] = int(value)
            elif key == 'cols':
                result[key] = int(value)
            else:
                result[key] = value

    return result

def draw_center_vertical_line(frame, color=(0, 0, 255), thickness=2):
    if frame is None:
        return None

    height, width = frame.shape[:2]
    center_x = width // 2

    start_point = (center_x, 0)
    end_point = (center_x, height)

    cv.line(frame, start_point, end_point, color, thickness)
    return frame

def fit_line_abc(frame):
    """
    Fit laser centerline using:

        1) Intensity weighted centroid of every row
        2) Weighted Total Least Squares

    Returns
    -------
    a,b,c

        ax + by = c

    normalized so

        sqrt(a�+b�)=1
    """

    #ret = True
    # --------------------------
    # grayscale
    # --------------------------
    if frame.ndim == 3:
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    else:
        gray = frame.copy()
    
    gray = gray.astype(np.float64)

    xs = []
    ys = []
    ws = []

    # --------------------------------------------------
    # Extract ONE center point from every image row
    # --------------------------------------------------
    for y in range(gray.shape[0]):

        row = gray[y]

        #print(row)
        row = row.astype(np.float64)

        m = row.max()
        idx = np.where(row > 0.1 * m)[0]

        if len(idx) == 0:
            continue

        intensity = row[idx]

        # centroid of this row
        xc = np.sum(idx * intensity) / np.sum(intensity)

        xs.append(xc)
        ys.append(y)

        # confidence of this row
        ws.append(np.sum(intensity))

    if len(xs) < 2:
        return False, (None,None,None)
        #raise ValueError("Not enough points.")

    xs = np.asarray(xs)
    ys = np.asarray(ys)
    ws = np.asarray(ws)

    # normalize weights
    ws /= ws.max()

    # --------------------------
    # weighted centroid
    # --------------------------
    W = np.sum(ws)

    x0 = np.sum(ws * xs) / W
    y0 = np.sum(ws * ys) / W

    X = xs - x0
    Y = ys - y0

    # --------------------------
    # Weighted covariance
    # --------------------------
    Sxx = np.sum(ws * X * X)
    Sxy = np.sum(ws * X * Y)
    Syy = np.sum(ws * Y * Y)

    C = np.array([
        [Sxx, Sxy],
        [Sxy, Syy]
    ])

    # eigenvector of smallest eigenvalue
    eigvals, eigvecs = np.linalg.eigh(C)

    a = eigvecs[0, 0]
    b = eigvecs[1, 0]

    norm = np.hypot(a, b)

    a /= norm
    b /= norm

    c = a * x0 + b * y0

    return True, (float(a), float(b), float(c))

def draw_line_from_abc(frame, a, b, c,color=(0, 0, 255),thickness=2):
    """
    Draw line:

        a*x + b*y = c

    on an image.

    Returns
    -------
    output : image
    (pt1, pt2) : endpoints used for drawing
    """

    output = frame.copy()

    if output.ndim == 2:
        output = cv.cvtColor(output, cv.COLOR_GRAY2BGR)

    h, w = output.shape[:2]

    pts = []

    eps = 1e-12

    # -------------------------
    # x = 0
    # -------------------------
    if abs(b) > eps:
        y = c / b
        if 0 <= y <= h - 1:
            pts.append((0, int(round(y))))

    # -------------------------
    # x = w-1
    # -------------------------
    if abs(b) > eps:
        y = (c - a * (w - 1)) / b
        if 0 <= y <= h - 1:
            pts.append((w - 1, int(round(y))))

    # -------------------------
    # y = 0
    # -------------------------
    if abs(a) > eps:
        x = c / a
        if 0 <= x <= w - 1:
            pts.append((int(round(x)), 0))

    # -------------------------
    # y = h-1
    # -------------------------
    if abs(a) > eps:
        x = (c - b * (h - 1)) / a
        if 0 <= x <= w - 1:
            pts.append((int(round(x)), h - 1))

    # ??? ???? ??????
    unique_pts = []
    for p in pts:
        if p not in unique_pts:
            unique_pts.append(p)

    if len(unique_pts) < 2:
        return output, None

    # ??? ????? ?? ?? ???? ??????? ??????? ?? ???? ?? ?????? ??
    if len(unique_pts) > 2:
        max_dist = -1

        for i in range(len(unique_pts)):
            for j in range(i + 1, len(unique_pts)):
                d = (unique_pts[i][0] - unique_pts[j][0]) ** 2 + \
                    (unique_pts[i][1] - unique_pts[j][1]) ** 2

                if d > max_dist:
                    max_dist = d
                    pt1 = unique_pts[i]
                    pt2 = unique_pts[j]
    else:
        pt1, pt2 = unique_pts

    cv.line(output, pt1, pt2, color, thickness)

    return output, (pt1, pt2)

def crop_centered_on_line(frame, a, b, c, strip_width):
    """
    خط را پیدا کرده، دو نقطه تقاطع آن با لبه‌های عکس را محاسبه می‌کند،
    سپس تصویر را حول آن خط با عرض مشخص کراپ و صاف (Rotate) می‌کند.
    """
    h, w = frame.shape[:2]
    
    # 1. تبدیل ضرایب به مختصات استاندارد (Ax + By = C)
    # فرمول خط در مبدأ بالا-راست: a*x' + b*y = c => a*(W-1-x) + b*y = c
    A = -a
    B = b
    C = c - a * (w - 1.0)
    
    # 2. پیدا کردن نقاط تقاطع خط با لبه‌های عکس
    # لبه‌ها: x=0, x=W-1, y=0, y=H-1
    points = []
    
    # تقاطع با x=0
    if B != 0:
        y = C / B
        if 0 <= y < h: points.append((0, y))
    
    # تقاطع با x=W-1
    if B != 0:
        y = (C - A * (w - 1)) / B
        if 0 <= y < h: points.append((w - 1, y))
        
    # تقاطع با y=0
    if A != 0:
        x = C / A
        if 0 <= x < w: points.append((x, 0))
        
    # تقاطع با y=H-1
    if A != 0:
        x = (C - B * (h - 1)) / A
        if 0 <= x < w: points.append((x, h - 1))
        
    # اگر خط از داخل تصویر عبور نکند
    if len(points) < 2:
        return frame # یا raise Error
        
    # دو نقطه انتهایی خط در تصویر (P1, P2)
    p1, p2 = points[0], points[1]
    
    # 3. محاسبه مرکز خط و زاویه
    center = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    length = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    angle = np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))
    
    # 4. کراپ کردن (استفاده از getRectSubPix برای چرخش و کراپ همزمان)
    # ابعاد مستطیل: (عرض خط، طول خط)
    # توجه: cv2.getRectSubPix مرکز را بر اساس (x,y) می‌گیرد
    crop_size = (int(length), int(strip_width))
    
    # برای چرخش از getRotationMatrix2D استفاده می‌کنیم
    matrix = cv.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv.warpAffine(frame, matrix, (w, h))
    
    # حالا یک کراپ ساده از وسط تصویر می‌زنیم
    # چون تصویر چرخانده شده، خط حالا افقی است
    x_c, y_c = int(center[0]), int(center[1])
    h_crop, w_crop = int(strip_width), int(length)
    
    # استخراج مستطیل
    cropped = cv.getRectSubPix(rotated, (w_crop, h_crop), center)
    
    return cropped

def mask_centered_on_line(frame, a, b, c, strip_width):
    """
    ???? ????? ?? ?? ??? ??????? ? ???? ????? ?? ?????? ???? ??????.

    ?????:
        frame       : ?????
        a, b, c     : ????? ??
        strip_width : ??? ???? (?????)

    ?????:
        ????? ????????? ????? ???? ?? ??? ???? ????? ?? ???? ????? ???.
    """

    h, w = frame.shape[:2]

    # ????? ?????
    A = -a
    B = b
    C = c - a * (w - 1.0)

    # ???? ???? ???? ?????
    points = []

    if B != 0:
        y = C / B
        if 0 <= y < h:
            points.append((0.0, y))

        y = (C - A * (w - 1)) / B
        if 0 <= y < h:
            points.append((w - 1.0, y))

    if A != 0:
        x = C / A
        if 0 <= x < w:
            points.append((x, 0.0))

        x = (C - B * (h - 1)) / A
        if 0 <= x < w:
            points.append((x, h - 1.0))

    if len(points) < 2:
        return np.zeros_like(frame)

    p1 = np.array(points[0], dtype=np.float32)
    p2 = np.array(points[1], dtype=np.float32)

    # ????? ?????? ??
    direction = p2 - p1
    direction /= np.linalg.norm(direction)

    # ????? ???? ?? ??
    normal = np.array([-direction[1], direction[0]], dtype=np.float32)

    half = strip_width / 2.0

    # ???? ???? ????
    quad = np.array([
        p1 + normal * half,
        p2 + normal * half,
        p2 - normal * half,
        p1 - normal * half
    ], dtype=np.int32)

    # ???? ????
    mask = np.zeros((h, w), dtype=np.uint8)
    cv.fillConvexPoly(mask, quad, 255)

    # ????? ????
    result = cv.bitwise_and(frame, frame, mask=mask)

    return result

def crop_by_two_points(frame, pt1, pt2, extra_width_px=0):

    """
    frame: تصویر ورودی
    pt1: نقطه اول به شکل (x, y)
    pt2: نقطه دوم به شکل (x, y)
    extra_width_px: تعداد پیکسل اضافه به عرض از هر طرف

    مثلا اگر 2 بدی:
    - 2 پیکسل از چپ
    - 2 پیکسل از راست
    اضافه می‌شود.
    """
    h, w = frame.shape[:2]

    x1, y1 = pt1
    x2, y2 = pt2

    left = min(x1, x2) - extra_width_px
    right = max(x1, x2) + extra_width_px
    top = min(y1, y2)
    bottom = max(y1, y2)

    # جلوگیری از خروج از محدوده تصویر
    left = max(0, left)
    right = min(w, right)
    top = max(0, top)
    bottom = min(h, bottom)

    if left >= right or top >= bottom:
        return None

    return frame[top:bottom, left:right]

def mask_by_two_points(frame, pt1, pt2, extra_width_px=0):
    """
    ????? ???????? ?? ??? ??????? ? ???? ????? ?? ?????? ???? ??????.

    frame: ????? ?????
    pt1: ???? ??? (x, y)
    pt2: ???? ??? (x, y)
    extra_width_px: ????? ????? ????? ?? ??? ?? ?? ???
    """

    h, w = frame.shape[:2]

    x1, y1 = pt1
    x2, y2 = pt2

    left = min(x1, x2) - extra_width_px
    right = max(x1, x2) + extra_width_px
    top = min(y1, y2)
    bottom = max(y1, y2)

    # ??????? ?? ???? ?? ?????? ?????
    left = max(0, left)
    right = min(w, right)
    top = max(0, top)
    bottom = min(h, bottom)

    if left >= right or top >= bottom:
        return np.zeros_like(frame)

    # ????? ????? ?????? ????
    result = np.zeros_like(frame)

    # ??? ????? ??????? ?? ??? ??
    result[top:bottom, left:right] = frame[top:bottom, left:right]

    return result

def keep_max_pixel_per_row(gray_image):
    """
    gray_image: تصویر grayscale / سیاه و سفید به صورت numpy array با ابعاد (H, W)

    خروجی:
        تصویری هم‌اندازه‌ی ورودی که در هر سطر فقط پیکسل با بیشترین مقدار
        نگه داشته می‌شود و بقیه صفر می‌شوند.
    """
    if gray_image.ndim != 2:
        raise ValueError("Input image must be a 2D grayscale image.")

    height, width = gray_image.shape
    output = np.zeros_like(gray_image)

    # اندیس بیشترین مقدار هر سطر
    max_indices = np.argmax(gray_image, axis=1)

    # در هر سطر فقط همان پیکسل را نگه می‌داریم
    for row in range(height):
        col = max_indices[row]
        output[row, col] = 255

    return output

def apply_threshold(frame, threshold_value):
    """
    frame: تصویر ورودی
    threshold_value: مقدار threshold

    خروجی:
        تصویر threshold شده
    """
    if len(frame.shape) == 3:
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    else:
        gray = frame.copy()

    _, thresholded = cv.threshold(gray, threshold_value, 255, cv.THRESH_BINARY)
    
    frame = cv.bitwise_and(frame,frame,mask=thresholded)
    return frame

def split_frame_width(frame, parts):
    """
    ????? ????? ?? ??? (?? ?? ????) ?? ????? ???? ????.

    Args:
        frame (numpy.ndarray): ????? ????? (OpenCV Frame)
        parts (int): ????? ???????

    Returns:
        list: ????? ?? ?????? ????????? ?? ????? ?? ?? ?? ????
    """

    if parts <= 0:
        raise ValueError("parts must be greater than 0")

    height, width = frame.shape[:2]
    slice_width = width // parts

    images = []

    for i in range(parts):
        x1 = i * slice_width

        # ????? ???? ???????????? ????? ?? ?? ???? ??????
        if i == parts - 1:
            x2 = width
        else:
            x2 = (i + 1) * slice_width

        images.append(frame[:, x1:x2])

    return images

def split_frame_height(frame, parts):
    """
    ????? ????? ?? ???? ?? ?????.
    """

    if parts <= 0:
        raise ValueError("parts must be greater than 0")

    height, width = frame.shape[:2]
    slice_height = height // parts

    images = []

    for i in range(parts):
        y1 = i * slice_height

        if i == parts - 1:
            y2 = height
        else:
            y2 = (i + 1) * slice_height

        images.append(frame[y1:y2, :])

    return images

def concat_images_vertical(images):
    """
    ?????? ?? ?? ????? ?? ???? ?? ????? ?? ?? ?????????.

    Args:
        images (list[np.ndarray]): ???? ??????

    Returns:
        np.ndarray: ????? ?????
    """

    if len(images) == 0:
        return None

    return cv.vconcat(images)

def RemoveDistotion(frame,camMatirx, dist_Coeff):
    height, width = frame.shape[:2]
    CameraMatrixNew, _ = cv.getOptimalNewCameraMatrix(camMatirx, dist_Coeff, (width, height), 1, (width, height))
    imgUndist = cv.undistort(frame, camMatirx, dist_Coeff, None, CameraMatrixNew)
    
    return imgUndist

