#!/usr/bin/env python3
import argparse
import hardware
import image_data
import skimage as ski

class Paperang_Printer:
    def __init__(self, address=None):
        self.address = address
        self.printer_hardware = None

    def connect(self):
        """Connect to the Paperang printer."""
        self.printer_hardware = hardware.Paperang(self.address)
        if not self.printer_hardware.connect():
            raise ConnectionError("Failed to connect to the Paperang printer.")

    def disconnect(self):
        """Disconnect from the Paperang printer."""
        if self.printer_hardware:
            self.printer_hardware.disconnect()

    def print_self_test(self):
        """Print a self-test page."""
        print("Attempting test print...")
        self.printer_hardware.sendSelfTestToBt()

    def print_image_file(self, path):
        """Print an image file."""
        image = ski.io.imread(path)
        if image.shape[-1] != 3:  # Ensure the image has 3 channels
            from skimage.color import gray2rgb
            if image.shape[-1] == 2:  # Handle 2-channel images
                image = gray2rgb(image[..., 0])  # Convert to RGB using the first channel
            else:
                raise ValueError(f"Unsupported image shape: {image.shape}")
        binary_img = image_data.binimage2bitstream(image_data.im2binimage(image, conversion="threshold"))
        self.printer_hardware.sendImageToBt(binary_img)

    def print_dithered_image(self, path):
        """Print a dithered image."""
        binary_img = image_data.im2binimage2(path)
        self.printer_hardware.sendImageToBt(binary_img)

def main():
    parser = argparse.ArgumentParser(description="Print images using the Paperang printer.")
    parser.add_argument("image_path", help="Path to the image file to print.")
    parser.add_argument(
        "-d", "--dither", action="store_true", 
        help="Use dithered processing for the image."
    )
    parser.add_argument(
        "-f", "--feed", type=int, default=1,
        help="Number of feed lines after printing (default: 1)."
    )
    parser.add_argument(
        "-a", "--address", type=str, default=None,
        help="Bluetooth address of the Paperang printer (optional)."
    )
    args = parser.parse_args()

    printer = Paperang_Printer(address=args.address)

    try:
        printer.connect()
        if args.dither:
            printer.print_dithered_image(args.image_path)
        else:
            printer.print_image_file(args.image_path)
        
        printer.printer_hardware.sendFeedLineToBt(args.feed)
        print(f"Successfully sent {args.image_path} to the printer{' with dithered processing' if args.dither else ''}. Feed lines: {args.feed}.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        printer.disconnect()

if __name__ == "__main__":
    main()