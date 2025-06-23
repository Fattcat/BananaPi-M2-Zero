from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont
import psutil
import socket
import time
import os

# Inicializácia OLED (I2C port 0, adresa 0x3C)
serial = i2c(port=0, address=0x3C)
device = ssd1306(serial)

# Používame vstavaný jednoduchý font
font = ImageFont.load_default()

def get_ip_address():
    """Získaj lokálnu IP adresu zariadenia (napr. wlan0 alebo eth0)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Neodosiela nič
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "No IP"

def get_cpu_temperature():
    """Získaj teplotu CPU v stupňoch Celzia."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_str = f.readline()
            return float(temp_str) / 1000.0
    except:
        return 0.0

def get_ssh_connection_count():
    """Spoľahlivo zistí počet aktívnych SSH spojení na porte 22."""
    try:
        output = os.popen("ss -tnp | grep ':22' | grep -v LISTEN | wc -l").read()
        return int(output.strip())
    except:
        return 0

# Hlavná slučka
while True:
    # RAM info
    ram = psutil.virtual_memory()
    ram_free_mb = int(ram.available / (1024 * 1024))
    ram_total_mb = int(ram.total / (1024 * 1024))

    # CPU info
    cpu = psutil.cpu_percent(interval=0.2)

    # IP adresa
    ip = get_ip_address()

    # Teplota CPU
    temp = get_cpu_temperature()

    # SSH počet pripojených zariadení
    ssh_count = get_ssh_connection_count()

    # Zobrazenie na OLED
    with canvas(device) as draw:
        draw.text((0, 0),   f"RAM: {ram_free_mb} / {ram_total_mb} MB", font=font, fill=255)
        draw.text((0, 10),  f"CPU: {cpu:.0f} %", font=font, fill=255)
        draw.text((0, 20),  f"IP:   {ip}", font=font, fill=255)
        draw.text((0, 30),  f"SSH: {ssh_count} pripojenie", font=font, fill=255)
        draw.text((0, 40),  f"Teplota:   {temp:.1f} °C", font=font, fill=255)

    time.sleep(1)
