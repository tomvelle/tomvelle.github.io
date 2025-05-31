import time
import pytesseract
import pyautogui
import pygetwindow as gw
import cv2
import numpy as np

# Find window by title
window_title = 'Pleasantville'
window = None

for w in gw.getAllWindows():
    if window_title.lower() in w.title.lower():
        window = w
        break

if window is None:
    print(f"Window titled '{window_title}' not found.")
    exit(1)

# Adjust for window borders
title_bar_height = 30
side_border_width = 8

min_blind_thickness = 10
last_show = None
last_action = None  # 'up', 'down', or None
locked_in = False

print("Press 'q' in the OpenCV window to quit.")

while True:
    left, top, right, bottom = window.left, window.top, window.right, window.bottom
    content_left = left + side_border_width
    content_top = top + title_bar_height
    content_width = right - left - (2 * side_border_width)
    content_height = bottom - top - title_bar_height - side_border_width

    screenshot = pyautogui.screenshot(region=(content_left, content_top, content_width, content_height))
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    h, w, _ = img.shape

    # Detect SHOW number
    bottom_crop = img[int(h * 0.85):h, 0:w]
    gray = cv2.cvtColor(bottom_crop, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
    extracted_text = pytesseract.image_to_string(thresh, config=custom_config)
    show_number = ''.join(filter(str.isdigit, extracted_text))

    if not show_number.isdigit():
        continue

    show_number = int(show_number)

    # Count blinds (LEAVE THIS LOGIC UNTOUCHED)
    blinds_area = img[0:h, int(w * 0.4):int(w * 0.6)]
    blinds_gray = cv2.cvtColor(blinds_area, cv2.COLOR_BGR2GRAY)
    blinds_blur = cv2.GaussianBlur(blinds_gray, (3, 3), 0)
    _, blinds_thresh = cv2.threshold(blinds_blur, 128, 255, cv2.THRESH_BINARY)

    row_sums = np.sum(blinds_thresh == 255, axis=1)
    full_width = (int(w * 0.2)) * 0.8

    blind_count = 0
    in_band = False
    current_band_thickness = 0

    debug_img = cv2.cvtColor(blinds_thresh, cv2.COLOR_GRAY2BGR)

    for idx, s in enumerate(row_sums):
        if s >= full_width:
            if not in_band:
                in_band = True
                current_band_thickness = 1
            else:
                current_band_thickness += 1
            cv2.line(debug_img, (0, idx), (debug_img.shape[1], idx), (0, 0, 255), 1)
        else:
            if in_band:
                if current_band_thickness >= min_blind_thickness:
                    blind_count += 1
                in_band = False
                current_band_thickness = 0

    if in_band and current_band_thickness >= min_blind_thickness:
        blind_count += 1

    # LOCKING MECHANISM WITH HARD MATCH LOCK
    if blind_count == show_number:
        if not locked_in:
            pyautogui.keyUp('up')
            pyautogui.keyUp('down')
            last_action = None
            locked_in = True
    else:
        locked_in = False
        if blind_count > show_number:
            if last_action != 'up':
                pyautogui.keyUp('down')
                pyautogui.keyDown('up')
                last_action = 'up'
        elif blind_count < show_number:
            if last_action != 'down':
                pyautogui.keyUp('up')
                pyautogui.keyDown('down')
                last_action = 'down'

    print(f"SHOW Number: {show_number} | Counted Blinds: {blind_count} | Locked: {locked_in}")

    cv2.imshow('Blinds Debug', debug_img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        pyautogui.keyUp('up')
        pyautogui.keyUp('down')
        break

    time.sleep(0.05)

cv2.destroyAllWindows()
