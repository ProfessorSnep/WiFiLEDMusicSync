"""MagicHome Python API.

Modified from Adam Kempenich
"""
import socket
import csv
import struct
import datetime


class Device:
    def __init__(self, device_ip, keep_alive=True):
        self.device_ip = device_ip
        self.API_PORT = 5577
        self.keep_alive = keep_alive
        self.make_socket()
                
    def make_socket(self):
        try:
            self.s.close()
        except:
            pass
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(3)
        self.latest_connection = datetime.datetime.now()
        try:
            print("Establishing connection with the device.")
            self.s.connect((self.device_ip, self.API_PORT))
        except socket.error as exc:
            print("Caught exception socket.error : %s" % exc)
            if self.s:
                self.s.close()

    def turn_on(self):
        self.send_message([0x71, 0x23, 0x0F])

    def turn_off(self):
        self.send_message([0x71, 0x24, 0x0F])

    def get_status(self):
        self.send_message([0x81, 0x8A, 0x8B])
        return self.s.recv(14)

    def set_color(self, r=0, g=0, b=0):
        message = [0x31, r, g, b, 0x00, 0x00, 0x0f]
        self.send_message(message)
            
    def set_custom(self, *steps):
        # 0x51 0xF0 STEP[ NUM SPEED COLOR1(R, G, B) COLOR2(R, G, B) 0x0F ]
        # STEP 9 BYTES, 32 STEPS
        empty_step = [0x00] * 8 + [0x0F]
        message = [0x51, 0xF0]
        for step in steps:
            message += step
            message += [0x0F]
        message += empty_step * (32 - len(steps))
        self.send_message(message)

    def set_preset(self, preset_number, speed):
        preset_number += 99
        if speed < 0:
            speed = 0
        if speed > 100:
            speed = 100

        preset_a = int(preset_number / 255) % 255
        preset_b = preset_number % 255
        message = [0x61, preset_a, preset_b, speed, 0x0F]
        self.send_message(message)
            
    def send_message(self, message):
        data = message + [self.calculate_checksum(message)]
        self.send_bytes(*data)

    def calculate_checksum(self, bytes):
        return sum(bytes) & 0xFF

    def send_bytes(self, *bytes):
        check_connection_time = (datetime.datetime.now() -
                                 self.latest_connection).total_seconds()
        try:
            if check_connection_time >= 295:
                print("Connection timed out, reestablishing.")
                self.make_socket()
            message_length = len(bytes)
            self.s.send(struct.pack("B"*message_length, *bytes))
            # Close the connection unless requested not to
            if self.keep_alive is False:
                self.s.close
        except socket.error as exc:
            print("Caught exception socket.error : %s" % exc)
            if self.s:
                self.s.close()
