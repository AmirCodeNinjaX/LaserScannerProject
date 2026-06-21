import cv2
import numpy as np

# =====================================================
# 1. تنظیمات سخت‌افزاری واقعی شما
# =====================================================
WIDTH, HEIGHT = 3280, 2464  # رزولوشن کامل IMX219
FOCAL_LENGTH = 3.04         # mm (بر اساس پارامتر جدید شما)
SENSOR_W = 3.68             # mm
SENSOR_H = 2.76             # mm

# محاسبه پارامترهای داخلی دوربین (Intrinsic Matrix)
fx = FOCAL_LENGTH * WIDTH / SENSOR_W
fy = FOCAL_LENGTH * HEIGHT / SENSOR_H
cx, cy = WIDTH / 2, HEIGHT / 2

K = np.array([
    [fx, 0, cx],
    [0, fy, cy],
    [0, 0, 1]
])

# پارامترهای فیزیکی نصب
CAM_HEIGHT = 25.0    # mm (فاصله لنز تا سطح)
BASELINE = 12.02     # mm (فاصله مرکز لنز تا خروجی لیزر)
LASER_ANGLE = np.deg2rad(25.68) # زاویه لیزر نسبت به خط عمود (فرض ۳۰ درجه)

# =====================================================
# 2. ایجاد سطح جسم (یک برآمدگی کوچک)
# =====================================================
# محدوده دید دوربین در فاصله 25 میلی‌متری حدود 55mm در 41mm است
grid_size = 60
x_range = np.linspace(-30, 30, 500)
y_range = np.linspace(-25, 25, 500)
X, Y = np.meshgrid(x_range, y_range)

# سطح صاف + یک برآمدگی 5 میلی‌متری در مرکز
Z = 5.0 * np.exp(-(X**2 + Y**2) / 100) 

# =====================================================
# 3. محاسبه صفحه لیزر (Laser Plane)
# =====================================================
# لیزر در (BASELINE, 0, CAM_HEIGHT) قرار دارد و با زاویه شلیک می‌کند
laser_origin = np.array([BASELINE, 0, CAM_HEIGHT])
# بردار نرمال صفحه لیزر (فرض می‌کنیم خط لیزر در راستای Y گسترده شده)
# معادله صفحه: ax + by + cz + d = 0
# برای زاویه LASER_ANGLE نسبت به Z:
n_x = np.cos(LASER_ANGLE)
n_z = np.sin(LASER_ANGLE)
laser_normal = np.array([n_x, 0, n_z])
D = -np.dot(laser_normal, laser_origin)

# =====================================================
# 4. تولید تصویر دوربین (Simulation)
# =====================================================
img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

# پیدا کردن نقاطی از سطح که با صفحه لیزر برخورد می‌کنند
# شرط برخورد: |n.P + D| < threshold
points_3d = []
for i in range(len(y_range)):
    for j in range(len(x_range)):
        P = np.array([X[i, j], Y[i, j], Z[i, j]])
        dist = np.dot(laser_normal, P) + D
        if abs(dist) < 0.1: # ضخامت مجازی خط لیزر
            points_3d.append(P)

# رسم نقاط روی تصویر
for P in points_3d:
    # تبدیل به مختصات دوربین (دوربین در 0,0,CAM_HEIGHT نگاهش به سمت پایین است)
    # در این مدل ساده: Pc = [P.x, P.y, CAM_HEIGHT - P.z]
    Pc = np.array([P[0], P[1], CAM_HEIGHT - P[2]])
    
    if Pc[2] <= 0: continue
    
    uvw = K @ Pc
    u = int(uvw[0] / uvw[2])
    v = int(uvw[1] / uvw[2])
    
    if 0 <= u < WIDTH and 0 <= v < HEIGHT:
        cv2.circle(img, (u, v), 2, (0, 0, 255), -1) # خط قرمز لیزر

# نمایش مرکز تصویر
cv2.circle(img, (int(cx), int(cy)), 10, (0, 255, 0), 2)

# =====================================================
# 5. بازسازی سه‌بعدی (Triangulation) - این بخش حیاتی است
# =====================================================
# فرض کنید فقط تصویر 'img' را داریم و می‌خواهیم ارتفاع Z را به دست آوریم
def reconstruct_z(u, v):
    # تبدیل پیکسل به بردار جهت در فضای دوربین
    ray = np.linalg.inv(K) @ np.array([u, v, 1.0])
    
    # حل معادله برخورد Ray با Plane
    # P = t * ray (در فضای دوربین) -> باید به فضای جهان منتقل شود
    # در فضای جهان: P_world = [ray_x * t, ray_y * t, CAM_HEIGHT - ray_z * t]
    # جایگذاری در معادله صفحه لیزر: n_x*(ray_x*t) + n_z*(CAM_HEIGHT - ray_z*t) + D = 0
    
    denom = (laser_normal[0] * ray[0] - laser_normal[2] * ray[2])
    if abs(denom) < 1e-6: return None
    
    t = -(laser_normal[2] * CAM_HEIGHT + D) / denom
    z_world = CAM_HEIGHT - (t * ray[2])
    return z_world

# تست بازسازی برای مرکز خط
test_z = reconstruct_z(cx, cy)
print(f"Reconstructed Z at center: {test_z:.2f} mm")

# نمایش خروجی (Resize برای مانیتور)
display_img = cv2.resize(img, (800, 600))
cv2.imshow("Macro Laser Scanner Sim", display_img)
print("Simulation finished. Press any key to exit.")
cv2.waitKey(0)
cv2.destroyAllWindows()
