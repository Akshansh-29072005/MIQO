import cv2
import socket
import struct
import pickle
import serial
import threading
import time

# ============================
# CONFIGURATION
# ============================
SERIAL_PORT = '/dev/ttyUSB0'    # Change if needed
BAUD_RATE = 115200
HOST_IP = ''                    # Listen on all interfaces
PORT = 8000                     # Port for video + commands
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

# ============================
# CAMERA SETUP (GStreamer + Fallback)
# ============================

def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=640,
    display_height=480,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        f"video/x-raw(memory:NVMM), width=(int){capture_width}, height=(int){capture_height}, "
        f"format=(string)NV12, framerate=(fraction){framerate}/1 ! "
        f"nvvidconv flip-method={flip_method} ! "
        f"video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
    )

def open_camera():
    """Try CSI camera first, then fallback to USB webcam."""
    print("🎥 Trying to open CSI camera...")
    cap = cv2.VideoCapture(gstreamer_pipeline(display_width=FRAME_WIDTH, display_height=FRAME_HEIGHT), cv2.CAP_GSTREAMER)
    if cap.isOpened():
        print("✅ CSI camera opened successfully!")
        return cap

    print("⚠️ CSI camera not found. Trying USB camera...")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("✅ USB camera opened successfully!")
        return cap

    print("❌ No camera detected. Exiting.")
    return None

# ============================
# SERIAL (ESP32) SETUP
# ============================

def open_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"🔌 Connected to ESP32 on {SERIAL_PORT}")
        return ser
    except Exception as e:
        print(f"❌ Failed to connect to ESP32: {e}")
        return None

# ============================
# COMMAND HANDLER THREAD
# ============================

def handle_commands(conn, ser):
    """Receive control commands from laptop and send to ESP32."""
    while True:
        try:
            cmd = conn.recv(1024).decode().strip()
            if not cmd:
                break
            print(f"📩 Command from laptop: {cmd}")
            if ser:
                ser.write((cmd + "\n").encode())
        except Exception as e:
            print(f"⚠️ Command thread ended: {e}")
            break

# ============================
# MAIN SERVER FUNCTION
# ============================

def start_server():
    # Initialize Serial and Camera
    ser = open_serial()
    cap = open_camera()
    if not cap:
        return

    # Setup Socket Server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST_IP, PORT))
    server_socket.listen(1)
    print(f"🚀 Waiting for laptop connection on port {PORT} ...")

    conn, addr = server_socket.accept()
    print(f"✅ Connected to {addr}")

    # Start command listener thread
    threading.Thread(target=handle_commands, args=(conn, ser), daemon=True).start()

    # Main loop: capture + stream frames
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Frame read failed, retrying...")
            time.sleep(0.1)
            continue

        # Encode frame as JPEG for streaming
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        data = pickle.dumps(buffer)
        message = struct.pack("Q", len(data)) + data

        try:
            conn.sendall(message)
        except Exception as e:
            print(f"⚠️ Connection lost: {e}")
            break

    cap.release()
    conn.close()
    server_socket.close()
    print("🛑 Server shut down cleanly.")


if __name__ == "__main__":
    start_server()

