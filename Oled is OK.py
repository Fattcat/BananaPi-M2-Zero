from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from time import sleep

serial = i2c(port=0, address=0x3C)
device = ssd1306(serial)

while True:
    with canvas(device) as draw:
        draw.text((10, 10), "OLED is OK", fill="white")
    sleep(1)  # refresh every second to be not stucked
