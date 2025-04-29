# Paperang(喵喵机) Python API

## Requirements & Dependencies

OS: Linux (tested Linux Arch)  
Python: 3.12 (tested)

Required arch packages: `python-pilkit python-scikit-image llvm`

Required debian packages: `libbluetooth-dev libhidapi-dev libatlas-base-dev python3-llvmlite python3-numba python-llvmlite llvm-dev`

Python Modules: install with `pip3 install -r requirements.txt`

### Set up and test your printer
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

## Printing via the printer.py Script
The `printer.py` script allows you to print images using the Paperang printer. Below are the available command-line parameters:

### Usage

```sh
python3 printer.py [image_path] [options]
```

#### Positional Arguments

`image_path`: The path to the image file you want to print. This is a required argument.

#### Optional Arguments

`-d`, `--dither`: Use dithered processing for the image. If this flag is provided, the image will be processed with dithering before printing.

Example: 
```sh
python3 printer.py /path/to/image.png --dither -a 00:11:22:33:44:55
```

`-f`, `--feed`: Specify the number of feed lines after printing. The default value is 1.

Example: 
```sh
python3 printer.py /path/to/image.png -f 5 -a 00:11:22:33:44:55
```

#### Required Arguments

`-a`, `--address`: Specify the Bluetooth address of the Paperang printer.

Example: 
```sh
python3 printer.py /path/to/image.png -a 00:11:22:33:44:55
```

#### Examples
Print an image with default settings:

```sh
python3 printer.py /path/to/image.png -a 00:11:22:33:44:55
```

Print an image with dithering:

```sh
python3 printer.py /path/to/image.png --dither -a 00:11:22:33:44:55
```

Print an image with 3 feed lines after printing:

```sh
python3 printer.py /path/to/image.png -f 3 -a 00:11:22:33:44:55
```

## Establishing a connection via API

`BtManager()` Leave the parameters blank to search for nearby paperang devices

`BtManager("AA:BB:CC:DD:EE:FF")` Calling with a specific MAC address skips searching for devices, saving time

## Printing images via API

The printer's API only accepts binary images for printing, so we need to convert text to images on the client side.

The format of the printed image is binary data, each bit represents black (1) or white (0), and 384 dots per line.

```python
mmj = BtManager()
mmj.sendImageToBt(img)
mmj.disconnect()
```

## Other Features

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

## Complaints

Why can't this thing have a multi-print feature? Printing at a lower temperature multiple times and then advancing the paper should allow for grayscale printing.

I've reverse-engineered the firmware for a long time but haven't figured out much. I'm really bad at this. I hope some expert can give me some life advice.

By the way, here are two chip models: `NUC123LD4BN0`, `STM32F071CBU6`, which seem to be Cortex-M0.

PS: This code is for non-commercial use only. If used for commercial purposes, please consult an expert.

## Acknowledgement
Thanks for all the reverse engineering work done by the original author of this project.

