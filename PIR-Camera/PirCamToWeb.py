import cv2
import time
import gpiod
from datetime import datetime
from flask import Flask, render_template_string, url_for
import os
import threading

# ---------- Konfigurácia PIR senzora ----------
CHIP = gpiod.Chip('gpiochip0')
LINE = CHIP.get_line(1)
LINE.request(consumer="pir_motion", type=gpiod.LINE_REQ_DIR_IN)

# ---------- Inicializácia kamery ----------
camera = cv2.VideoCapture(1)
if not camera.isOpened():
    print("Chyba: Nedá sa otvoriť kamera.")
    exit(1)

# ---------- Flask aplikácia ----------
app = Flask(__name__)
IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(IMAGE_DIR, exist_ok=True)

LATEST_FILENAME = "latest.jpg"  # Vždy prepíše starý obrázok

@app.route('/')
def index():
    image_path = os.path.join(IMAGE_DIR, LATEST_FILENAME)
    if os.path.exists(image_path):
        return render_template_string("""
        <html>
        <head>
            <title>Aktuálna snímka</title>
            <meta http-equiv="refresh" content="3">  <!-- Obnova každé 3 sekundy -->
        </head>
        <body style="text-align: center;">
            <h2>Posledná detekcia pohybu</h2>
            <img src="{{ url_for('static', filename=latest) }}?t={{ timestamp }}" width="640"><br>
            <p>{{ latest }}</p>
        </body>
        </html>
        """, latest=LATEST_FILENAME, timestamp=int(time.time()))
    else:
        return "<h2>Zatiaľ žiadna snímka</h2>"

def start_flask():
    app.run(host="192.168.1.15", port=8080)

# ---------- Hlavná slučka ----------
def motion_loop():
    print("Systém pripravený. Čakám na pohyb...")

    try:
        while True:
            if LINE.get_value() == 1:
                print("Pohyb zaznamenaný!")
                time.sleep(0.5)

                ret, frame = camera.read()
                if ret:
                    filepath = os.path.join(IMAGE_DIR, LATEST_FILENAME)
                    cv2.imwrite(filepath, frame)
                    print(f"Obrázok uložený ako: {LATEST_FILENAME}")
                else:
                    print("Chyba: Nedá sa načítať snímka z kamery.")

                while LINE.get_value() == 1:
                    time.sleep(0.1)
                print("Čakám na ďalší pohyb...")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nUkončujem program...")

    finally:
        camera.release()
        LINE.release()
        CHIP.close()

# ---------- Spustenie ----------
if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    motion_loop()
