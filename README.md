# TemperatureDS18B20RpiZeroW

Simple tutorial: read temperature from a **DS18B20** on **Raspberry Pi Zero W** using **VSCode Remote SSH Terminal**.

## 1) Hardware wiring (3.3V mode)

DS18B20 pins (flat side facing you):

- Left pin: **GND** -> RPi **GND**
- Middle pin: **DQ (data)** -> RPi **GPIO4** (physical pin 7)
- Right pin: **VDD** -> RPi **3.3V**

Also add a **4.7k or 10k resistor** between **DQ** and **3.3V** (pull-up).

## 2) Enable 1-Wire on Raspberry Pi Zero W

In VSCode, connect to the Pi using Remote SSH and open terminal.

Run:

```bash
sudo raspi-config
```

Go to:

- `Interface Options` -> `1-Wire` -> `Yes`

Then reboot:

```bash
sudo reboot
```

Reconnect over SSH after reboot.

## 3) Verify sensor is detected

Run:

```bash
ls /sys/bus/w1/devices/
```

You should see a folder starting with `28-` (this is your DS18B20).

If not visible yet, load modules and check again:

```bash
sudo modprobe w1-gpio
sudo modprobe w1-therm
ls /sys/bus/w1/devices/
```

## 4) Read temperature quickly in terminal

Replace `28-xxxxxxxxxxxx` with your sensor folder:

```bash
cat /sys/bus/w1/devices/28-xxxxxxxxxxxx/w1_slave
```

Example output:

```text
73 01 4b 46 7f ff 0d 10 2b : crc=2b YES
73 01 4b 46 7f ff 0d 10 2b t=23187
```

`t=23187` means **23.187 °C**.

## 5) One-line command for Celsius in SSH terminal

```bash
awk -F't=' '/t=/{printf "%.3f °C\n", $2/1000}' /sys/bus/w1/devices/28-*/w1_slave
```

## 6) Python script for live reading every 5 seconds

Run the script from this repository:

```bash
python3 read_sensor_loop.py
```

It will print the detected sensor value every **5 seconds** until you stop it with `Ctrl+C`.

## 7) Optional shell loop (live reading every 2 seconds)

```bash
watch -n 2 "awk -F't=' '/t=/{printf \"%.3f °C\n\", \$2/1000}' /sys/bus/w1/devices/28-*/w1_slave"
```

## Troubleshooting

- Check wiring and resistor value (4.7k between data and 3.3V).
- Confirm 1-Wire is enabled in `raspi-config`.
- Verify sensor appears as `28-*` in `/sys/bus/w1/devices/`.
