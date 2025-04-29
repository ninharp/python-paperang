#!/usr/bin/env python3
import sys
import hardware
import image_data
import skimage.io
import skimage as ski
import config

class Paperang_Printer:
    def __init__(self):
        if hasattr(config, "macaddress"):
            self.printer_hardware = hardware.Paperang(config.macaddress)
        else:
            self.printer_hardware = hardware.Paperang()

    def print_self_test(self):
        print("attempting test print to MAC address \"% s\""% config.macaddress)
        if self.printer_hardware.connected:
            self.printer_hardware.sendSelfTestToBt()

    def print_image_file(self, path):
        if self.printer_hardware.connected:
            self.printer_hardware.sendImageToBt(image_data.binimage2bitstream(
                image_data.im2binimage(ski.io.imread(path),conversion="threshold")))
    
    def print_dithered_image(self, path):
        if self.printer_hardware.connected:
            self.printer_hardware.sendImageToBt(image_data.im2binimage2(path))

if __name__=="__main__":
    if len(sys.argv) != 2:
        print("Usage: printer.py /path/to/image.png")
        sys.exit(1)

    image_path = sys.argv[1]

    try:
        printer = Paperang_Printer()
        printer.print_dithered_image(image_path)
        printer.printer_hardware.sendFeedLineToBt(1)
        print(f"Successfully sent {image_path} to the printer.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
