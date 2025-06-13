from machine import I2C
from micropython import const


ADDRESS = const(0x60)

REG_GENERAL_CALL = 0x00

CMD_RESET = 0x06
CMD_WAKEUP = 0x09
CMD_SOFTWARE_UPDATE = 0x08
CMD_VREF = 0x80
CMD_GAIN = 0xC0
CMD_PD = 0xA0

VREF_VDD = 0
VREF_INTERNAL = 1

GAIN_1X = 0
GAIN_2X = 1

PD_NC = 0
PD_1K = 1
PD_100K = 2
PD_500K = 3


class MCP4728:

    def __init__(self, i2c: I2C, gain=GAIN_1X, vref=VREF_VDD, pulldown=PD_NC, vdd=5.0):

        self.i2c = i2c
        self.addr = ADDRESS
        self.gain = gain
        self.vref = vref
        self.pulldown = pulldown
        self.vdd = vdd if vref is VREF_VDD else 2.048
        self._write_dat(REG_GENERAL_CALL, bytearray([CMD_SOFTWARE_UPDATE]))
        self.set_vref(vref)
        self.set_gain(gain)
        self.set_pulldown(pulldown)

    def _voltage_to_raw(self, vol=0):
        if vol == 0:
            return 0
        vol = self.vdd if vol > self.vdd else vol
        return round(self.vdd / vol * 0xFFF)

    def write_all(self, va, vb, vc, vd):
        buf = bytearray(8)
        voltage = [va, vb, vc, vd]
        raw = [self._voltage_to_raw(v) for v in voltage]

        for idx, val in enumerate(raw):
            buf[idx] = (self.pulldown << 4) + (val >> 8)
            buf[idx + 1] = val & 0xFF

        self._write_reg(buf)
        self._write_dat(REG_GENERAL_CALL, bytearray([CMD_RESET]))

    def set_pulldown(self, val=PD_NC):
        pd = (val << 2) + val
        reg = CMD_PD + pd
        msg = bytearray([pd << 4])
        self._write_dat(reg, msg)

    def set_gain(self, val=GAIN_1X):
        gain = 0xF if val is GAIN_2X else 0
        msg = bytearray([CMD_GAIN + gain])
        self._write_reg(msg)

    def set_vref(self, val=VREF_INTERNAL):
        vref = 0xF if val is VREF_INTERNAL else 0
        msg = bytearray([CMD_VREF + vref])
        self._write_reg(msg)

    def _write_dat(self, reg, buf):
        self.i2c.writeto_mem(self.addr, reg, buf)

    def _write_reg(self, reg):
        self.i2c.writeto(self.addr, reg)
