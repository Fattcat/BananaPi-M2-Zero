import os
import time
from datetime import datetime
from flask import Flask, render_template, Response, request, redirect, url_for, session, flash
import cv2
import signal
import sys
from collections import defaultdict

# === NASTAVENIA ===
IPAddress = '0.0.0.0'
USERNAME = 'YourUsername'
PASSWORD = 'YourPassword'
SECRET_KEY = 'StrOngPreSession123!'  # !Zmeň na silnejšie v produkcii

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auth_attempts.log')

# Brute-force ochrana
MAX_ATTEMPTS = 3
BASE_BAN_TIME = 60   # 1 min
MAX_BAN_TIME = 900   # 15 min

failed_attempts = defaultdict(list)
banned_until = {}

app = Flask(__name__)
app.secret_key = SECRET_KEY  # Nutné pre použitie session

camera = None
running = True

# Logovanie
def log_attempt(ip, username, success):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "FAILED"
    log_entry = f"[{timestamp}] IP: {ip} | Username: '{username}' | Status: {status}\n"
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def is_ip_banned(ip):
    now = time.time()
    if ip in banned_until:
        if now < banned_until[ip]:
            return True
        else:
            del banned_until[ip]
            failed_attempts[ip].clear()
    return False

def record_failed_attempt(ip):
    now = time.time()
    failed_attempts[ip] = [t for t in failed_attempts[ip] if now - t < 900]
    failed_attempts[ip].append(now)

    if len(failed_attempts[ip]) >= MAX_ATTEMPTS:
        attempt_cycle = (len(failed_attempts[ip]) - 1) // MAX_ATTEMPTS
        ban_duration = min(BASE_BAN_TIME * (5 ** attempt_cycle), MAX_BAN_TIME)
        banned_until[ip] = now + ban_duration

# Inicializácia kamery
def init_camera():
    global camera
    camera = cv2.VideoCapture(1, cv2.CAP_V4L2)  # Zmeň na 0 ak 1 nefunguje
    if not camera.isOpened():
        print("[ERROR] Kamera sa nedá otvoriť!")
        sys.exit(1)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

# Stream
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

            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            frame = buffer.tobytes()
            last_frame_time = current_time

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# === Routy ===

@app.route('/login', methods=['GET', 'POST'])
def login():
    ip = request.remote_addr

    if is_ip_banned(ip):
        remaining = int(banned_until[ip] - time.time())
        flash(f"Príliš veľa zlých pokusov. Skúste znova o {remaining} sekúnd.", "error")
        return render_template('login.html'), 429

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if username == USERNAME and password == PASSWORD:
            log_attempt(ip, username, True)
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            log_attempt(ip, username, False)
            record_failed_attempt(ip)
            flash("Nesprávne meno alebo heslo.", "error")
            return render_template('login.html'), 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

def require_login(f):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/')
@require_login
def index():
    return render_template('index.html')

@app.route('/video_feed')
@require_login
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Signal handler
def signal_handler(sig, frame):
    global running
    print("\n[INFO] Ukončovanie...")
    running = False
    if camera is not None:
        camera.release()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    init_camera()
    print(f"[INFO] Server beží na http://{IPAddress}:80")
    print(f"[INFO] Log súbor: {LOG_FILE}")
    app.run(host=IPAddress, port=80, debug=False, threaded=True)
