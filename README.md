# BananaPi-M2-Zero
## tested on ArmbianOS Allwiner H2+
## this repository contains:
- Files, README.md tutorials (for how to do something)
- Reccommendation and setup

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


# for Oled display
- we now add support for oled i2c display

```
echo "overlays=i2c0" | sudo tee -a /boot/armbianEnv.txt
```
- now reboot with ```sudo reboot```