#!/usr/bin/env python3
import sys
import argparse
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
        print("Attempting test print to MAC address \"%s\"" % config.macaddress)
        if self.printer_hardware.connected:
            self.printer_hardware.sendSelfTestToBt()

    def print_image_file(self, path):
        if self.printer_hardware.connected:
            image = ski.io.imread(path)
            if image.shape[-1] != 3:  # Ensure the image has 3 channels
                from skimage.color import gray2rgb
                if image.shape[-1] == 2:  # Handle 2-channel images
                    image = gray2rgb(image[..., 0])  # Convert to RGB using the first channel
                else:
                    raise ValueError(f"Unsupported image shape: {image.shape}")
            self.printer_hardware.sendImageToBt(
                image_data.binimage2bitstream(image_data.im2binimage(image, conversion="threshold"))
            )
    
    def print_dithered_image(self, path):
        if self.printer_hardware.connected:
            self.printer_hardware.sendImageToBt(image_data.im2binimage2(path))

def main():
    parser = argparse.ArgumentParser(description="Print images using the Paperang printer.")
    parser.add_argument("image_path", help="Path to the image file to print.")
    parser.add_argument(
        "-d", "--dither", action="store_true", 
        help="Use dithered processing for the image."
    )
    args = parser.parse_args()

    try:
        printer = Paperang_Printer()
        if args.dither:
            printer.print_dithered_image(args.image_path)
        else:
            printer.print_image_file(args.image_path)
        
        printer.printer_hardware.sendFeedLineToBt(1)
        print(f"Successfully sent {args.image_path} to the printer{' with dithered processing' if args.dither else ''}.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
