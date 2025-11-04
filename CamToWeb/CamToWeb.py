from flask import Flask, render_template, Response
import cv2
import time
import signal
import sys
import threading

IPAddress = '0.0.0.0' # change to your device IP (type iwconfig and then ifconfig to your terminal and checkout IP wlan0 or else ...)

app = Flask(__name__)
camera = None
running = True  # Globálny prepínač cyklu

# Nastavenie kamery
def init_camera():
    global camera
    camera = cv2.VideoCapture(1, cv2.CAP_V4L2)

     # Zníž rozlíšenie ak seká (napr. 640x480 alebo 320x240)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Zapni MJPEG (ak kamera podporuje)
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

# Funkcia na zachytenie snímok
def gen_frames():
    global running
    target_fps = 10
    frame_interval = 1.0 / target_fps
    last_frame_time = 0

    while running:
        current_time = time.time()
        if current_time - last_frame_time >= frame_interval:
            success, frame = camera.read()
            if not success:
                break

            # JPEG kvalita 90% (vyššia hodnota = lepšia kvalita, väčší prenos)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            frame = buffer.tobytes()
            last_frame_time = current_time

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Čisté ukončenie pomocou CTRL+C
def signal_handler(sig, frame):
    global running
    print("\n[INFO] Ukončovanie...")
    running = False
    if camera is not None:
        camera.release()
    sys.exit(0)

if __name__ == '__main__':
    # Signal handling
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    init_camera()
    print("[INFO] Server beží na http://<IP_ADRESA>:5000")
    app.run(host=IPAddress, port=5000, debug=False, threaded=True)
