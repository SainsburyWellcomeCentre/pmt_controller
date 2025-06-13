from machine import I2C
import time
from micropython import const


ADDRESS = const(0x49)


REG_INPUT = const(0x00)
REG_OUTPUT = const(0x01)
REG_POLARITY = const(0x02)
REG_CONFIG = const(0x03)

INPUT = const(0x01)
OUTPUT = const(0x00)
MASK_INPUT = const(0xF0)
MASK_OUTPUT = const(0x0F)


class TCA9537:

    def __init__(self, i2c: I2C, ch1=OUTPUT, ch2=OUTPUT, ch3=OUTPUT, ch4=OUTPUT):

        self.i2c = i2c
        self.addr = ADDRESS
        config = ch1 + (ch3 << 1) + (ch2 << 2) + (ch4 << 3)
        self.config(config)
        self.status = 0

    def config(self, config):
        self._write_dat(REG_CONFIG, bytearray([config]))

    def set_output(self, value):
        if value < 0 or value > 15:
            raise ValueError("Channel must be between 0 and 0b1111")
        self.status = value
        self._write_dat(REG_OUTPUT, bytearray([value]))

    def set_output_ch(self, channel, value):
        if channel < 0 or channel > 3:
            raise ValueError("Channel must be between 0 and 3")
        if value not in (INPUT, OUTPUT):
            raise ValueError("Value must be INPUT or OUTPUT")
        self._write_dat(REG_OUTPUT, bytearray([self.status & ~(1 << channel) | (value << channel)]))

    def _write_dat(self, reg, buf):
        self.i2c.writeto_mem(self.addr, reg, buf)
