# 📟 OLED System Monitor for Armbian SBC

This project displays key system information (RAM, CPU usage, IP address, SSH connections, CPU temperature) on a small I2C OLED display (SSD1306) connected to a Single Board Computer (SBC) running Armbian, such as the Banana Pi M2 Zero.

## ✨ Features

- Shows available and total RAM (in MB)
- Real-time CPU usage display (in %)
- Displays the local IP address
- Indicates the number of active SSH connections
- Displays the CPU temperature in °C

## 🧰 Hardware Requirements

- SBC with Armbian (e.g. Banana Pi, Orange Pi, Raspberry Pi)
- I2C OLED display (SSD1306, 128x64 resolution)
- Wiring:
  - VCC → 3.3V or 5V
  - GND → GND
  - SDA → GPIO SDA (e.g. GPIO2)
  - SCL → GPIO SCL (e.g. GPIO3)

## 💻 Software Requirements

- Armbian OS (Debian Buster, Bullseye, Bookworm, etc.)
- Python 3
- Required Python packages:
  - `psutil`
  - `Adafruit_SSD1306`
  - `Pillow`

## 📦 Installation

Run the following commands:

```bash
## Update system packages
sudo apt update && sudo apt upgrade -y

- we now add support for oled i2c display

```
echo "overlays=i2c0" | sudo tee -a /boot/armbianEnv.txt
```
- now reboot with ```sudo reboot```

## Install necessary system packages
- sudo apt install -y python3 python3-pip i2c-tools git python3-pil python3-dev

## Enable I2C if not already enabled
- sudo armbian-config
- Go to: System → Hardware → Enable i2c0 and i2c1
- Alternatively, edit /boot/armbianEnv.txt manually:
- Add this line:
- overlays=i2c0 i2c1

## Reboot the system
- sudo reboot

# Verify I2C bus is available
- ls /dev/i2c*
- i2cdetect -y 1

# Install Python libraries( normal and V2)
- sudo pip3 install luma.oled psutil
- pip3 install psutil Adafruit_SSD1306 Pillow
- sudo pip3 install luma.core smbus2 pillow
