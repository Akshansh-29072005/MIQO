import cv2
import numpy as np
import serial
import time
import csv
import threading

# ======== SERIAL SETUP ========
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)
print("✅ Connected to ESP32")

# ======== CAMERA (IMX219 CSI) SETUP ========
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

cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
if not cap.isOpened():
    print("❌ Camera could not be opened.")
    exit()

print("🚗 Starting Line Following with Path Recording...")

# ======== GLOBAL VARIABLES ========
current_left_pwm = 0
current_right_pwm = 0
base_speed = 80
turn_speed = 50
run_flag = True

imu_data = [0, 0, 0]  # gx, gy, gz

# ======== THREAD: READ IMU DATA CONTINUOUSLY ========
def read_imu():
    global imu_data, run_flag
    while run_flag:
        if ser.in_waiting:
            line = ser.readline().decode().strip()
            if line.startswith("IMU:"):
                try:
                    gx, gy, gz = map(int, line[4:].split(","))
                    imu_data = [gx, gy, gz]
                except:
                    pass

imu_thread = threading.Thread(target=read_imu, daemon=True)
imu_thread.start()

# ======== CSV LOGGING ========
csv_file = open("path_log.csv", "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["time", "gx", "gy", "gz", "leftPWM", "rightPWM"])

# ======== MAIN LOOP ========
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Camera read failed")
            break

        height, width, _ = frame.shape
        roi = frame[int(height * 2 / 3):height, :]  # Bottom third

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, mask = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])

                # Draw single visual indicator line
                cv2.line(roi, (cx, 0), (cx, roi.shape[0]), (0, 255, 0), 2)

                if cx < width / 3:
                    # LEFT
                    current_left_pwm = turn_speed
                    current_right_pwm = base_speed
                    ser.write(f"A{turn_speed}B{base_speed}\n".encode())
                    cv2.putText(roi, "LEFT", (20, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                elif cx > 2 * width / 3:
                    # RIGHT
                    current_left_pwm = base_speed
                    current_right_pwm = turn_speed
                    ser.write(f"A{base_speed}B{turn_speed}\n".encode())
                    cv2.putText(roi, "RIGHT", (20, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    # FORWARD
                    current_left_pwm = base_speed
                    current_right_pwm = base_speed
                    ser.write(f"A{base_speed}B{base_speed}\n".encode())
                    cv2.putText(roi, "FORWARD", (20, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                ser.write(b"S\n")
        else:
            ser.write(b"S\n")

        # ======== LOG CURRENT STATE ========
        timestamp = time.time()
        gx, gy, gz = imu_data
        csv_writer.writerow([timestamp, gx, gy, gz, current_left_pwm, current_right_pwm])

        # ======== SHOW OUTPUT (ROI only) ========
        cv2.imshow("Line Follower (ROI)", roi)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC to stop
            break

except KeyboardInterrupt:
    pass

# ======== CLEANUP ========
run_flag = False
csv_file.close()
ser.write(b"S\n")
cap.release()
cv2.destroyAllWindows()
print("✅ Path recording stopped and saved as path_log.csv")

