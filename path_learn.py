import cv2
import numpy as np
import serial
import time
import csv
import os

# Connect to ESP32
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)
print("✅ Connected to ESP32")

# File to log the path
LOG_FILE = "path_memory.csv"

# --- Function: Create new log or append to existing ---
def init_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'command'])
    print("🧠 Path memory ready!")

def log_command(command):
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([time.time(), command])

# --- Function: Replay the learned path ---
def replay_path():
    if not os.path.exists(LOG_FILE):
        print("⚠️ No path memory found!")
        return

    print("🔁 Replaying learned path...")
    with open(LOG_FILE, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        last_time = None
        for row in reader:
            t, cmd = float(row[0]), row[1]
            if last_time:
                delay = t - last_time
                time.sleep(delay)
            ser.write(cmd.encode())
            print(f"↩️ Sent: {cmd}")
            last_time = t
    print("✅ Replay complete!")

# --- IMX219 Camera Pipeline ---
def gstreamer_pipeline(
    capture_width=1280, capture_height=720,
    display_width=640, display_height=360,
    framerate=30, flip_method=0
):
    return (
        "nvarguscamerasrc ! "
        f"video/x-raw(memory:NVMM), width=(int){capture_width}, height=(int){capture_height}, "
        f"format=(string)NV12, framerate=(fraction){framerate}/1 ! "
        f"nvvidconv flip-method={flip_method} ! "
        f"video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)BGRx ! "
        "videoconvert ! video/x-raw, format=(string)BGR ! appsink"
    )

# --- Initialize camera ---
cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
if not cap.isOpened():
    print("❌ Camera could not be opened.")
    exit()

init_log()
print("🚗 Starting Line Following with Path Memory")

current_command = None
last_command_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Camera read failed")
        break

    height, width, _ = frame.shape
    roi = frame[int(height * 2 / 3):height, :]  # bottom third

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    command = 'S'

    if contours:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        if M['m00'] > 0:
            cx = int(M['m10'] / M['m00'])
            cv2.line(roi, (cx, 0), (cx, roi.shape[0]), (0, 255, 0), 2)

            # Decide command
            if cx < width / 3:
                command = 'L'
                cv2.putText(roi, "LEFT", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            elif cx > 2 * width / 3:
                command = 'R'
                cv2.putText(roi, "RIGHT", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                command = 'F'
                cv2.putText(roi, "FORWARD", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            command = 'S'
    else:
        command = 'S'

    # --- Send and log command if changed ---
    if command != current_command:
        ser.write(command.encode())
        log_command(command)
        current_command = command
        last_command_time = time.time()
        print(f"➡️ Sent: {command}")

    cv2.imshow("Line Tracker (Memory Mode)", roi)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC → quit
        break
    elif key == ord('r'):  # press 'r' to replay path
        replay_path()

cap.release()
cv2.destroyAllWindows()
print("🧭 Path memory saved in 'path_memory.csv'")

