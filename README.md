# BananaPi-M2-Zero
## tested on ArmbianOS Allwiner H2+
## this repository contains:
- Files, README.md tutorials (for how to do something)
- Reccommendation and setup

## Files for different scope of usage

- ```Microphone```
  - simple (only) microphone recording system to local IP website 
- ```CamToWeb```
  - Simple Camera recording system to local IP website
- ```PIR sensor```
  - the camera will take a photo if PIR sensor catches someone in room (like for thief detector)
  - Supported buzzer
- ```OledDisplay```
  - For showing status like RAM, CPU, Temperature, apache2 ...

- in folder ```Microphone``` u can find streaming sound and listening on website with IP of device & port 4999
## Install

### for PIR use this
- install modules with pip3 cv2 gpiod
- sudo python3 PIR-MotionCameraShot.py

```
sudo apt update
sudo apt install python3-pip
pip3 install numpy arp-scan psutil luma.oled
sudo pip3 install luma.oled psutil luma.core smbus2 pillow
```

```
pip3 install opencv-python
sudo apt install python3-opencv -y
sudo apt install v4l-utils -y
v4l2-ctl --list-devices
sudo apt install  mplayer -y
```

```
sudo nano /boot/armbianEnv.txt
```

- and paste on bottom this

```
extraargs=usbcore.autosuspend=-1 dwc_otg.lpm_enable=0
```
- then press CTRL o, then enter, and CTRL x.

- now ```sudo reboot```

- ! MAKE SURE YOU HAVE commented g_serial !! (otherwise will not detect any USB device)
- So check here ```sudo nano /etc/modules```
- if there is this ```#g_serial```, then u are good to go (if not then simply add ```#``` at the beginning of the line)

# for Oled display
- we now add support for oled i2c display

```
echo "overlays=i2c0" | sudo tee -a /boot/armbianEnv.txt
```
- now reboot with ```sudo reboot```
