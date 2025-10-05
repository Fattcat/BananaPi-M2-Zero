# OledSysInfoV2.py
# Zobrazuje systémové informácie na OLED displeji
# Požiadavky: luma.oled, luma.core, psutil, smbus2, PIL, arp-scan
# sudo pip3 install luma.oled luma.core psutil smbus2 pillow

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont, Image
import psutil
import socket
import time
import subprocess
import smbus2
import os

# ======= Font =======
# Zmeň cestu podľa reálneho umiestnenia súboru TTF
FONT_PATH = "fonts/DejaVuSans-Bold.ttf"
FONT_SIZE = 10
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

# ======= Automatické nájdenie OLED =======
def find_ssd1306_address(bus=0):
    possible_addresses = [0x3C, 0x3D]
    for address in possible_addresses:
        try:
            bus_obj = smbus2.SMBus(bus)
            bus_obj.write_quick(address)
            bus_obj.close()
            return address
        except OSError:
            continue
    return None

oled_address = find_ssd1306_address(bus=0)
if oled_address is None:
    print("❌ OLED displej nebol nájdený. Skontroluj pripojenie a napájanie.")
    exit(1)

serial = i2c(port=0, address=oled_address)
device = ssd1306(serial)

# ======= Checkmark bitmapa =======
checkmark_data = [
    0b00000000,
    0b00000001,
    0b00000011,
    0b00000110,
    0b10001100,
    0b11011000,
    0b01110000,
    0b00100000
]
checkmark_img = Image.new("1", (8, 8))
checkmark_img.frombytes(bytes(checkmark_data))

# ======= Pomocné funkcie =======
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "No IP"

def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return float(f.readline()) / 1000.0
    except:
        return 0.0

def get_ssh_connection_count():
    try:
        output = subprocess.check_output("who | grep -Ei 'ssh|pts' | wc -l", shell=True)
        return int(output.strip())
    except:
        return 0

def is_apache_running():
    try:
        output = subprocess.check_output("systemctl is-active apache2", shell=True)
        return output.strip() == b'active'
    except:
        return False

def is_tor_running():
    try:
        output = subprocess.check_output("systemctl is-active tor", shell=True)
        return output.strip() == b'active'
    except:
        return False

def get_wifi_clients():
    try:
        output = subprocess.check_output("arp-scan --interface=wlan0 --localnet", shell=True, stderr=subprocess.DEVNULL)
        lines = output.decode().splitlines()
        clients = [line for line in lines if ":" in line and "ARP" not in line]
        return len(clients)
    except:
        return -1

# Inicializácia CPU metriky
psutil.cpu_percent(interval=None)

# Prvý WiFi scan
wifi_client_count = get_wifi_clients()
last_wifi_check = time.time()

# ======= Hlavná slučka =======
while True:
    now = time.time()

    # Aktualizácia počtu WiFi klientov každých 30 sekúnd
    if now - last_wifi_check >= 30:
        new_count = get_wifi_clients()
        if new_count != -1:
            wifi_client_count = new_count
        last_wifi_check = now

    # Získanie systémových dát
    ram = psutil.virtual_memory()
    ram_free_mb = int(ram.available / (1024 * 1024))
    ram_total_mb = int(ram.total / (1024 * 1024))
    cpu = psutil.cpu_percent(interval=0.5)
    ip = get_ip_address()
    temp = get_cpu_temperature()
    ssh_count = get_ssh_connection_count()
    apache_ok = is_apache_running()
    tor_ok = is_tor_running()

    # Zobrazenie na OLED
    with canvas(device) as draw:
        draw.text((0, 0),   f"RAM: {ram_free_mb}/{ram_total_mb} MB", font=font, fill=255)
        draw.text((0, 16),  f"CPU: {cpu:.0f} %", font=font, fill=255)
        draw.text((0, 26),  f"IP: {ip}", font=font, fill=255)
        draw.text((0, 36),  f"SSH: {ssh_count}", font=font, fill=255)
        draw.text((0, 46),  f"Tep: {temp:.1f} °C", font=font, fill=255)

        if apache_ok:
            draw.bitmap((120, 0), checkmark_img, fill=255)
        if tor_ok:
            draw.bitmap((120, 20), checkmark_img, fill=255)

        wifi_text = "?" if wifi_client_count < 0 else str(wifi_client_count)
        draw.text((112, 50), wifi_text, font=font, fill=255)

    time.sleep(1)