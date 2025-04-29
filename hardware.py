#!/usr/bin/python3
# -*-coding:utf-8-*-

import struct
import zlib
import logging
import socket
from const import BtCommandByte
from platform import system


class Paperang:
    standardKey = 0x35769521
    padding_line = 300
    max_send_msg_length = 1536
    max_recv_msg_length = 1024

    def __init__(self, address=None):
        self.address = address
        self.sock = None
        self.crckeyset = False

    def connect(self):
        """Connect to the Paperang printer using Classic Bluetooth."""
        if not self.address:
            raise ValueError("Bluetooth address is required to connect.")
        try:
            self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            self.sock.connect((self.address, 1))  # Port 1 is typically used for SPP
            self.sock.settimeout(60)
            logging.info(f"Connected to {self.address}.")
            self.registerCrcKeyToBt()
            return True
        except Exception as e:
            logging.error(f"Failed to connect to {self.address}: {e}")
            return False

    def disconnect(self):
        """Disconnect from the Paperang printer."""
        if self.sock:
            try:
                self.sock.close()
                logging.info("Disconnected.")
            except Exception as e:
                logging.error(f"Failed to disconnect: {e}")

    def send_to_bt(self, data_bytes, control_command, need_reply=True):
        """Send data to the printer."""
        if not self.sock:
            raise ConnectionError("Not connected to any device.")

        bytes_list = self.add_bytes_to_list(data_bytes)
        for i, bytes_chunk in enumerate(bytes_list):
            packet = self.pack_per_bytes(bytes_chunk, control_command, i)
            self.sock.send(packet)
            logging.info(f"Sent packet {i + 1}/{len(bytes_list)}.")

        if need_reply:
            return self.recv()

    def recv(self):
        """Receive data from the printer."""
        try:
            data = self.sock.recv(self.max_recv_msg_length)
            logging.info(f"Received data: {data}")
            return data
        except Exception as e:
            logging.error(f"Failed to receive data: {e}")
            return None

    def crc32(self, content):
        """Calculate CRC32 checksum."""
        return zlib.crc32(content, self.crcKey if self.crckeyset else self.standardKey) & 0xffffffff

    def pack_per_bytes(self, bytes_chunk, control_command, i):
        """Pack data into a format suitable for the printer."""
        result = struct.pack('<BBB', 2, control_command, i)
        result += struct.pack('<H', len(bytes_chunk))
        result += bytes_chunk
        result += struct.pack('<I', self.crc32(bytes_chunk))
        result += struct.pack('<B', 3)
        return result

    def add_bytes_to_list(self, bytes_data):
        """Split data into chunks for sending."""
        length = self.max_send_msg_length
        return [bytes_data[i:i + length] for i in range(0, len(bytes_data), length)]

    def registerCrcKeyToBt(self, key=0x6968634 ^ 0x2e696d):
        """Register the CRC32 key with the printer."""
        logging.info("Setting CRC32 key...")
        msg = struct.pack('<I', int(key ^ self.standardKey))
        self.send_to_bt(msg, BtCommandByte.PRT_SET_CRC_KEY)
        self.crcKey = key
        self.crckeyset = True
        logging.info("CRC32 key set.")

    def sendPaperTypeToBt(self, paperType=0):
        """Set the paper type."""
        msg = struct.pack('<B', paperType)
        self.send_to_bt(msg, BtCommandByte.PRT_SET_PAPER_TYPE)

    def sendPowerOffTimeToBt(self, poweroff_time=0):
        """Set the auto power-off time."""
        msg = struct.pack('<H', poweroff_time)
        self.send_to_bt(msg, BtCommandByte.PRT_SET_POWER_DOWN_TIME)

    def sendImageToBt(self, binary_img):
        """Send an image to the printer."""
        self.sendPaperTypeToBt()
        msg = b"".join(map(lambda x: struct.pack("<c", x.to_bytes(1, byteorder="little")), binary_img))
        self.send_to_bt(msg, BtCommandByte.PRT_PRINT_DATA, need_reply=False)
        self.sendFeedLineToBt(self.padding_line)

    def sendSelfTestToBt(self):
        """Send a self-test command to the printer."""
        msg = struct.pack('<B', 0)
        self.send_to_bt(msg, BtCommandByte.PRT_PRINT_TEST_PAGE)

    def sendDensityToBt(self, density):
        """Set the print density."""
        msg = struct.pack('<B', density)
        self.send_to_bt(msg, BtCommandByte.PRT_SET_HEAT_DENSITY)

    def sendFeedLineToBt(self, length):
        """Send a feed line command to the printer."""
        msg = struct.pack('<H', length)
        self.send_to_bt(msg, BtCommandByte.PRT_FEED_LINE)

    def queryBatteryStatus(self):
        """Query the battery status."""
        msg = struct.pack('<B', 1)
        self.send_to_bt(msg, BtCommandByte.PRT_GET_BAT_STATUS)

    def queryDensity(self):
        """Query the print density."""
        msg = struct.pack('<B', 1)
        self.send_to_bt(msg, BtCommandByte.PRT_GET_HEAT_DENSITY)

    def sendFeedToHeadLineToBt(self, length):
        """Send a feed-to-head-line command."""
        msg = struct.pack('<H', length)
        self.send_to_bt(msg, BtCommandByte.PRT_FEED_TO_HEAD_LINE)

    def queryPowerOffTime(self):
        """Query the auto power-off time."""
        msg = struct.pack('<B', 1)
        self.send_to_bt(msg, BtCommandByte.PRT_GET_POWER_DOWN_TIME)

    def querySNFromBt(self):
        """Query the serial number."""
        msg = struct.pack('<B', 1)
        self.send_to_bt(msg, BtCommandByte.PRT_GET_SN)

    def queryHardwareInfo(self):
        """Query the hardware information."""
        msg = struct.pack('<B', 1)
        self.send_to_bt(msg, BtCommandByte.PRT_GET_HW_INFO)