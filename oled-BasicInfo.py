from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont
import psutil
import socket
import time

# Inicializácia OLED displeja (I2C zbernica a adresa)
serial = i2c(port=0, address=0x3C)
device = ssd1306(serial)

# Font (systémový štandardný)
font = ImageFont.load_default()

def get_ip_address():
    """Získaj lokálnu IP adresu."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "No IP"

while True:
    # Získanie údajov
    ram = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.2)
    ip = get_ip_address()

    ram_usage = f"RAM: {ram.percent:.0f}%"
    cpu_usage = f"CPU: {cpu:.0f}%"
    ip_info = f"IP: {ip}"

    # Vykreslenie na OLED displej
    with canvas(device) as draw:
        draw.text((0, 0), ram_usage, font=font, fill=255)
        draw.text((0, 12), cpu_usage, font=font, fill=255)
        draw.text((0, 24), ip_info, font=font, fill=255)

    time.sleep(1)  # obnov každú sekundu
