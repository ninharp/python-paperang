# Paperang(喵喵机) Python API

### Requirements & Dependencies

OS: OSX (tested on Catalina)/Linux (tested Debian Buster on a Raspberry Pi 4)  
Python: 3.5-3.7 (tested)

Required debian packages: `libbluetooth-dev libhidapi-dev libatlas-base-dev python3-llvmlite python3-numba python-llvmlite llvm-dev`

Python Modules: install with `pip3 install -r requirements.txt`

### macOS instructions

#### Set up and test your printer
You'll need python3 installed; check if you have it by typing `which python3` in Terminal or your favorite console application.

1. Install necessary python modules:
```sh
pip3 install -r requirements.txt
```
2. Ensure bluetooth is enabled on your computer. You do *not* need to connect your Paperang to your computer yet! We'll do that later, via the command line.
3. Turn on your Paperang and set it near your computer
4. Run the test script, which will tell your Paperang to print a self-test if it's successful:
```sh
python3 testprint.py
```
If you've never paired your Paperang with your computer, you might get a dialog asking you to allow the Paperang to pair with your system. Click `connect`. You should only have to do this once.

5. If the test print was successful, the script will print out your device's MAC address on the console, as well as on the printer. You can enter that into the script to connect to your Paperang directly, avoiding the wait time for scanning for printers.

If you need to look up your Paperang's MAC address quickly, you can use the `system_profiler` command to output information on all paired bluetooth devices:
```sh
system_profiler SPBluetoothDataType
```

#### Print Little Printer data



### Establishing a connection

`BtManager()` Leave the parameters blank to search for nearby paperang devices

`BtManager("AA:BB:CC:DD:EE:FF")` Calling with a specific MAC address skips searching for devices, saving time

### Printing images

The printer's API only accepts binary images for printing, so we need to convert text to images on the client side.

The format of the printed image is binary data, each bit represents black (1) or white (0), and 384 dots per line.

```python
mmj = BtManager()
mmj.sendImageToBt(img)
mmj.disconnect()
```

### Other Features

`registerCrcKeyToBt(key=123456)` Change the communication CRC32 KEY (not sure why this is necessary, logically, listening to this packet would allow you to get the key).

`sendPaperTypeToBt(paperType=0)` Change the paper type

`sendPowerOffTimeToBt(poweroff_time=0)` Change the auto power-off time.

`sendSelfTestToBt()` Print a self-test page.

`sendDensityToBt(density)` Set the print density.

`sendFeedLineToBt(length)`  Control the padding after printing.

`queryBatteryStatus()` Query the remaining battery level.

`queryDensity()` Query the print density.

`sendFeedToHeadLineToBt(length)` Not sure how this differs from `sendFeedLineToBt` , but it seems to be called after printing as well.

`queryPowerOffTime()` Query the auto power-off time.

`querySNFromBt()` Query the device's serial number.

There are actually quite a few operations. If you're interested, you can look at `const.py` and guess what they do.

### Image Tools

`ImageConverter.image2bmp(path)` Convert any image to binary data suitable for printing.
 
`TextConverter.text2bmp(text)` Convert specified text to binary data suitable for printing.

### WeChat Public Platform Tools

Two small scripts to implement automatic printing after sending an image to a WeChat public account.

`wechat.php` Used on a VPS to receive data from Tencent. By default, only specified users are allowed to print.

`printer_server.py` Run on a Raspberry Pi or other Bluetooth-enabled machine near the Paperang. You can use `tinc` or similar to establish a VPN for the VPS to directly access it.

### Complaints

Why can't this thing have a multi-print feature? Printing at a lower temperature multiple times and then advancing the paper should allow for grayscale printing.

I've reverse-engineered the firmware for a long time but haven't figured out much. I'm really bad at this. I hope some expert can give me some life advice.

By the way, here are two chip models: `NUC123LD4BN0`, `STM32F071CBU6`, which seem to be Cortex-M0.

PS: This code is for non-commercial use only. If used for commercial purposes, please consult an expert.

### Acknowledgement
Thanks for all the reverse engineering work done by the original author of this project.

