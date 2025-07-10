import cv2                                                                  import time                                                                 import gpiod
from datetime import datetime

# Vyber čip a číslo linky podľa zapojenia (GPIO17 zvyčajne line 17)
chip = gpiod.Chip('gpiochip0')
line = chip.get_line(1)

# Požiadaj o prístup k linke ako vstup (input)
line.request(consumer="pir_motion", type=gpiod.LINE_REQ_DIR_IN)

# Inicializácia kamery
camera = cv2.VideoCapture(1)
if not camera.isOpened():
    print("Chyba: Nedá sa otvoriť kamera.")
    exit(1)

print("Systém pripravený. Čakám na pohyb...")

try:
    while True:
        if line.get_value() == 1:
            print("Pohyb zaznamenaný!")
            time.sleep(0.5)

            ret, frame = camera.read()
            if ret:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")                        filename = f"motion_{timestamp}.jpg"                                        cv2.imwrite(filename, frame)
                print(f"Uložené: {filename}")
            else:
                print("Chyba: Nedá sa načítať snímka z kamery.")

            while line.get_value() == 1:
                time.sleep(0.1)
            print("Čakám na ďalší pohyb...")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nUkončujem program...")

finally:
    camera.release()
    line.release()
    chip.close()