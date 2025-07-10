import gpiod                                                                import time                                                                 import cv2                                                                  import os                                                                   from datetime import datetime



# start with sudo python3 PIR-MotionCameraShot.py
# PIR Pin pripojený na GPIO17 (fyzický pin číslo 11)




# Nastavenie GPIO linky podľa CON2-P11 → line 1
CHIP_NAME = "gpiochip0"
LINE_NUM = 1  # ← uprav podľa výstupu PIR senzora
                                                                            # Inicializácia GPIO                                                        chip = gpiod.Chip(CHIP_NAME)
line = chip.get_line(LINE_NUM)
line.request(consumer="pir", type=gpiod.LINE_REQ_DIR_IN)

# Inicializácia kamery
camera = cv2.VideoCapture(1)
if not camera.isOpened():
    raise IOError("Kamera sa nedá otvoriť")

print("Systém pripravený. Čakám na pohyb...")

try:
    while True:
        if line.get_value() == 1:
            print("Pohyb zistený!")
            ret, frame = camera.read()
            if ret:
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"obrazok_{now}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Obrázok uložený ako: {filename}")
            else:
                print("Chyba pri získavaní obrázku z kamery.")
            # Čakaj, kým pohyb zmizne (debounce)
            while line.get_value() == 1:
                time.sleep(0.1)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nUkončujem program...")
finally:
    line.release()
    chip.close()
    camera.release()
    cv2.destroyAllWindows()