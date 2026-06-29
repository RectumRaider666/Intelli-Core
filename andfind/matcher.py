import sys
import cv2

screen_path, target_path, threshold_raw = sys.argv[1], sys.argv[2], sys.argv[3]
threshold = float(threshold_raw)
screen = cv2.imread(screen_path, cv2.IMREAD_COLOR)
target = cv2.imread(target_path, cv2.IMREAD_COLOR)

if screen is None:
    print("Error: Bad Screen")
    sys.exit(2)
if target is None:
    print("Error: Bad_Target")
    sys.exit(2)

result = cv2.matchTemplate(screen, target, cv2.TM_CCOEFF_NORMED)
_, max_val, _, max_loc = cv2.minMaxLoc(result)

h, w = target.shape[:2]
center_x = max_loc[0] + (w // 2)
center_y = max_loc[1] + (h // 2)

if max_val >= threshold:
    print(f"Found: {center_x} {center_y} {max_val:.4f}")
else:
    print(f"Not Found:\nClosest Match: {center_x} {center_y} {max_val:.4f}")