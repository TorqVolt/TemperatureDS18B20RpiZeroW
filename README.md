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

## 6) Optional loop (live reading every 2 seconds)

```bash
watch -n 2 "awk -F't=' '/t=/{printf \"%.3f °C\n\", \$2/1000}' /sys/bus/w1/devices/28-*/w1_slave"
```

## 7) Python script to read temperature

Create a Python script (e.g., `read_temperature.py`) on your RPi Zero W:

```python
#!/usr/bin/env python3

import time
import os

# Find DS18B20 sensor
sensor_folder = None
devices_path = '/sys/bus/w1/devices/'

for folder in os.listdir(devices_path):
    if folder.startswith('28-'):
        sensor_folder = folder
        break

if not sensor_folder:
    print("Error: DS18B20 sensor not found!")
    exit(1)

sensor_file = os.path.join(devices_path, sensor_folder, 'w1_slave')

def read_temperature():
    """Read temperature from DS18B20 sensor."""
    try:
        with open(sensor_file, 'r') as f:
            lines = f.readlines()
            # Check if CRC is valid
            if lines[0].strip().endswith('YES'):
                # Extract temperature from second line
                if 't=' in lines[1]:
                    parts = lines[1].split('t=')
                    if len(parts) > 1:
                        temp_str = parts[1].strip()
                        try:
                            temp_celsius = int(temp_str) / 1000.0
                            return temp_celsius
                        except ValueError:
                            return None
                    else:
                        return None
                else:
                    return None
            else:
                return None
    except Exception as e:
        print(f"Error reading sensor: {e}")
        return None

# Example: Read temperature once
temp = read_temperature()
if temp is not None:
    print(f"Temperature: {temp:.3f} °C")

# Example: Continuous reading every 2 seconds
# Uncomment to use:
# try:
#     while True:
#         temp = read_temperature()
#         if temp is not None:
#             print(f"Temperature: {temp:.3f} °C")
#         time.sleep(2)
# except KeyboardInterrupt:
#     print("\nStopped by user")
```

Make the script executable:

```bash
chmod +x read_temperature.py
```

Run the script:

```bash
python3 read_temperature.py
```

## 8) Deploy Python script from VSCode to RPi Zero W

### Method 1: Using VSCode Remote SSH (Recommended)

1. **Install Remote SSH extension** in VSCode (if not already installed):
   - Open VSCode Extensions `Ctrl+Shift+X` / `Cmd+Shift+X`
   - Search for "Remote - SSH"
   - Click Install

2. **Connect to RPi Zero W**:
   - Press `Ctrl+Shift+P` / `Cmd+Shift+P` and select "Remote-SSH: Connect to Host"
   - Enter your RPi connection: `ssh pi@<your-pi-ip>` (or use your configured host alias)
   - Select the OS (Linux)
   - VSCode will install remote server on your RPi

3. **Open project folder on RPi**:
   - After connecting, click "File" → "Open Folder"
   - Navigate to your desired directory (e.g., `/home/pi/temperature-sensor`) and click "OK"
   - Open integrated terminal (`` Ctrl+` `` / `` Cmd+` ``)

4. **Create or edit Python script**:
   - Create a new file: `read_temperature.py`
   - Copy the Python script code (from section 7) into the file
   - Save the file (`Ctrl+S` / `Cmd+S`)

5. **Run the script**:
   - In VSCode terminal, run: `python3 read_temperature.py`

### Method 2: Clone repository and push changes from VSCode

1. **Clone the repository on your local machine**:
   - Open VSCode
   - Press `Ctrl+Shift+P` / `Cmd+Shift+P` and select "Git: Clone"
   - Enter the repository URL
   - Select a local folder to clone into

2. **Add your Python script**:
   - Create `read_temperature.py` in the cloned folder
   - Add your Python code to the file

3. **Connect to RPi and transfer files**:
   - Open Remote SSH connection to RPi (see Method 1, steps 1-2)
   - In a new VSCode window, open the folder on your RPi
   - Copy files from local repository to RPi:
     - Option A: Drag and drop files from local folder to remote folder in Explorer
     - Option B: Open terminal on RPi and use git to pull/clone the repository
     - Option C: Use `scp` command from local terminal: `scp read_temperature.py pi@<your-pi-ip>:/home/pi/temperature-sensor/`

### Method 3: Direct file transfer with SCP (Terminal)

1. **From your local machine terminal**:
   ```bash
   scp read_temperature.py pi@<your-pi-ip>:/home/pi/temperature-sensor/
   ```

2. **Or copy entire project**:
   ```bash
   scp -r . pi@<your-pi-ip>:/home/pi/temperature-sensor/
   ```

3. **Then SSH into RPi and run**:
   ```bash
   ssh pi@<your-pi-ip>
   cd /home/pi/temperature-sensor/
   python3 read_temperature.py
   ```

### Tips for VSCode Remote SSH Development

- **Keep files in sync**: Use git to push/pull changes between local and RPi
- **Run scripts directly**: Use VSCode's integrated terminal on the RPi
- **Debug easily**: Monitor output in real-time from VSCode
- **SSH config file**: Add entries to `~/.ssh/config` for quick access:
  ```
  Host rpi-zero
      HostName <your-pi-ip>
      User pi
      IdentityFile ~/.ssh/id_rsa
  ```
  Then connect with: "Remote-SSH: Connect to Host" → select "rpi-zero"

## Troubleshooting

- Check wiring and resistor value (4.7k between data and 3.3V).
- Confirm 1-Wire is enabled in `raspi-config`.
- Verify sensor appears as `28-*` in `/sys/bus/w1/devices/`.
- **Python script errors**: Ensure 1-Wire is enabled and sensor is detected (see section 3).
- **VSCode Remote SSH connection fails**: Check SSH is enabled on RPi and firewall allows SSH (port 22).
- **File transfer issues**: Verify you have write permissions to the target directory on RPi.
