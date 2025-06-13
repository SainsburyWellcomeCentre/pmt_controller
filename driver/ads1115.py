from machine import I2C
import time
from micropython import const


ADDRESSES = [const(0x48), const(0x49), const(0x4A), const(0x4B)]


REG_CONVERT = const(0x00)
REG_CONFIG = const(0x01)
REG_LOWTHRESH = const(0x02)
REG_HITHRESH = const(0x03)

MASK_OS = const(0x8000)
MASK_MUX = const(0x7000)
MASK_PGA_ = const(0x0E00)
MASK_MODE = const(0x0100)
MASK_DR = const(0x00E0)
MASK_CMODE = const(0x0010)
MASK_CPOL = const(0x0008)
MASK_CQUE = const(0x0003)


MUX_SINGLE_0 = const(0x4000)  # Single-ended AIN0
MUX_SINGLE_1 = const(0x5000)  # Single-ended AIN1
MUX_SINGLE_2 = const(0x6000)  # Single-ended AIN2
MUX_SINGLE_3 = const(0x7000)  # Single-ended AIN3

MUX = [MUX_SINGLE_0, MUX_SINGLE_1, MUX_SINGLE_2, MUX_SINGLE_3]

GAIN_6144 = const(0x0000)  # +/-6.144V range  =  Gain 2/3
GAIN_4096 = const(0x0200)  # +/-4.096V range  =  Gain 1
GAIN_2048 = const(0x0400)  # +/-2.048V range  =  Gain 2 (default)
GAIN_1024 = const(0x0600)  # +/-1.024V range  =  Gain 4
GAIN_512 = const(0x0800)  # +/-0.512V range  =  Gain 8
GAIN_256 = const(0x0A00)  # +/-0.256V range  =  Gain 16

LSB_UV = dict(
    [
        (GAIN_6144, 187.5),
        (GAIN_4096, 125),
        (GAIN_2048, 62.5),
        (GAIN_1024, 31.25),
        (GAIN_512, 15.625),
        (GAIN_256, 7.8125),
    ]
)

DR_8SPS = const(0x0000)  # 8 samples per second
DR_16SPS = const(0x0020)  # 16 samples per second
DR_32SPS = const(0x0040)  # 32 samples per second
DR_64SPS = const(0x0060)  # 64 samples per second
DR_128SPS = const(0x0080)  # 128 samples per second (default)
DR_250SPS = const(0x00A0)  # 250 samples per second
DR_475SPS = const(0x00C0)  # 475 samples per second
DR_860SPS = const(0x00E0)  # 860 samples per Second

SP_TIME_MS = dict(
    [
        (DR_8SPS, 125),
        (DR_16SPS, 62.5),
        (DR_32SPS, 31.25),
        (DR_64SPS, 15.625),
        (DR_128SPS, 7.8125),
        (DR_250SPS, 4),
        (DR_475SPS, 2),
        (DR_860SPS, 1.2),
    ]
)

MODE_CONTINUOUS = const(0x0000)  # Continuous conversion mode
MODE_SINGLE = const(0x0100)  # Single-shot conversion mode


class ADS1115:

    def __init__(self, i2c: I2C, addr, gain=GAIN_6144, rate=DR_860SPS, mode=MODE_CONTINUOUS):
        isAddrValid = False
        for address in ADDRESSES:
            if address == addr:
                isAddrValid = True
                self.addr = addr

        if not isAddrValid:
            raise ValueError("Invalid ads1115 address: " + addr)
        self.i2c = i2c
        self.gain = gain
        self.rate = rate
        self.mode = mode
        self.config()

    def config(self, channel=0):
        # os = MASK_OS and 0x8000  # Start a single conversion
        config = MUX[channel] | self.gain | self.mode | self.rate
        self._write_dat(REG_CONFIG, bytearray([(config >> 8) & 0xFF, config & 0xFF]))

    def read_voltage(self, channel=0):
        if channel < 0 or channel > 3:
            raise ValueError("Channel must be between 0 and 3")
        self.config(channel)
        # time.sleep_us(round(SP_TIME_MS.get(self.rate, 1) * 2000) + 1000)
        time.sleep_ms(2)
        raw = self._noise_check(self._read_raw())
        lsb_uv = LSB_UV.get(self.gain, 1)
        voltage = raw * lsb_uv * 1e-6
        return voltage

    def _noise_check(self, val):
        if val > 0xff00 or val < 128:
            return 0
        else:
            return val

    def _read_raw(self):
        temp = self._read_dat(REG_CONVERT, 2)
        val = (temp[0] << 8) + temp[1]
        return val

    def _read_dat(self, reg, length):
        return self.i2c.readfrom_mem(self.addr, reg, length)

    def _write_dat(self, reg, buf):
        self.i2c.writeto_mem(self.addr, reg, buf)
