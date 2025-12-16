import cv2
import numpy as np
import serial
import time

# Connect to ESP32
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)
print("✅ Connected to ESP32")

# Use IMX219 CSI camera on Jetson Nano
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

print("🚗 Starting Line Following with ROI Optimization")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Camera read failed")
        break

    # Use only bottom 1/3 of the frame as ROI
    height, width, _ = frame.shape
    roi = frame[int(height * 2 / 3):height, :]

    # Convert to grayscale and blur
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Mask for black line
    _, mask = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        if M['m00'] > 0:
            cx = int(M['m10'] / M['m00'])

            # Draw only one line to visualize direction
            cv2.line(roi, (cx, 0), (cx, roi.shape[0]), (0, 255, 0), 2)

            # Decide motion
            if cx < width / 3:
                ser.write(b'L')
                cv2.putText(roi, "LEFT", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            elif cx > 2 * width / 3:
                ser.write(b'R')
                cv2.putText(roi, "RIGHT", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                ser.write(b'F')
                cv2.putText(roi, "FORWARD", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            ser.write(b'S')
    else:
        ser.write(b'S')

    cv2.imshow("Line Tracker (ROI)", roi)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
