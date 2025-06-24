from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont
import psutil
import socket
import time
import subprocess

# Inicializácia OLED
serial = i2c(port=0, address=0x3C)
device = ssd1306(serial)
font = ImageFont.load_default()

# IP adresa
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "No IP"

# Teplota CPU
def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return float(f.readline()) / 1000.0
    except:
        return 0.0

# Spoľahlivý počet SSH (aj dropbear, aj sshd)
def get_ssh_connection_count():
    try:
        output = subprocess.check_output("who | grep -Ei 'ssh|pts' | wc -l", shell=True)
        return int(output.strip())
    except:
        return 0

# Inicializuj CPU meranie
psutil.cpu_percent(interval=None)

while True:
    ram = psutil.virtual_memory()
    ram_free_mb = int(ram.available / (1024 * 1024))
    ram_total_mb = int(ram.total / (1024 * 1024))

    cpu = psutil.cpu_percent(interval=0.5)
    ip = get_ip_address()
    temp = get_cpu_temperature()
    ssh_count = get_ssh_connection_count()

    with canvas(device) as draw:
        draw.text((0, 0),   f"RAM (volne): {ram_free_mb}/{ram_total_mb}MB", font=font, fill=255)
        draw.text((0, 16),  f"CPU: {cpu:.0f} %", font=font, fill=255)
        draw.text((0, 26),  f"IP: {ip}", font=font, fill=255)
        draw.text((0, 36),  f"SSH: {ssh_count} prihl.", font=font, fill=255)
        draw.text((0, 46),  f"Tep: {temp:.1f} °C", font=font, fill=255)

    time.sleep(1)