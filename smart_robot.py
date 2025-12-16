import cv2
import numpy as np
import serial
import time
import csv
import os

# === Serial Setup ===
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)
print("✅ Connected to ESP32")

# === Directory for saved paths ===
os.makedirs("paths", exist_ok=True)

# === Helper functions ===
def list_paths():
    files = [f for f in os.listdir("paths") if f.endswith(".csv")]
    if not files:
        print("⚠️ No saved paths found.")
        return []
    print("\n📁 Available saved paths:")
    for i, f in enumerate(files):
        print(f"  {i+1}. {f}")
    return files

def init_log(filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'command'])
    print(f"🧠 Logging started → {filename}")

def log_command(filename, command):
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([time.time(), command])

def replay_path(filename):
    print(f"🔁 Replaying learned path from {filename}")
    with open(filename, 'r') as f:
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

# === Camera Setup (IMX219) ===
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

# === Startup menu ===
print("\n🤖 Select operation mode:")
print("1️⃣  Learn a NEW path (record and save)")
print("2️⃣  Replay an EXISTING path")
print("3️⃣  Just FOLLOW the line (no recording)\n")

mode = input("Enter 1 / 2 / 3: ").strip()

if mode == "2":
    files = list_paths()
    if not files:
        exit()
    choice = int(input("\nEnter file number to replay: ")) - 1
    replay_path(os.path.join("paths", files[choice]))
    exit()

elif mode == "1":
    path_name = input("Enter a name for this new path: ").strip()
    LOG_FILE = os.path.join("paths", f"{path_name}.csv")
    init_log(LOG_FILE)
    record = True
else:
    LOG_FILE = None
    record = False
    print("🟢 Following line only (no recording)")

# === Initialize camera ===
cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
if not cap.isOpened():
    print("❌ Camera could not be opened.")
    exit()

print("🚗 Starting Line Following System")
print("Press [P] to save current path anytime.")
print("Press [ESC] to stop safely.\n")

current_command = None

# === Main loop ===
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

            if cx < width / 3:
                command = 'L'
                cv2.putText(roi, "LEFT", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            elif cx > 2 * width / 3:
                command = 'R'
                cv2.putText(roi, "RIGHT", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                command = 'F'
                cv2.putText(roi, "FORWARD", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # --- Send command if changed ---
    if command != current_command:
        ser.write(command.encode())
        if record:
            log_command(LOG_FILE, command)
        current_command = command
        print(f"➡️ Sent: {command}")

    cv2.imshow("Line Tracker", roi)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC → quit safely
        print("\n🛑 Stopping...")
        break
    elif key == ord('p') and record:  # save current CSV
        print(f"💾 Path saved successfully as {LOG_FILE}")
        record = False  # stop logging further to prevent corruption

cap.release()
cv2.destroyAllWindows()
print("✅ Program terminated.")

