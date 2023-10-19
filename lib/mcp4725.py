"""MCP4725 Driver for Raspberry Pi Pico"""
from micropython import const

from machine import I2C, Pin

MCP4725_ADDR0 = const(0x60)
MCP4725_ADDR1 = const(0x61)

MCP4725_WRITE_DAC = const(0x40)
MCP4725_WRITE_EEPROM = const(0x60)

POWER_DOWN_MODE = {'Off':0, '1k':1, '100k':2, '500k':3}
        
class MCP4725:
    def __init__(self, i2c, value=0, address=MCP4725_ADDR0) :
        self.i2c=i2c
        self.address=address
        self._writeBuffer=bytearray(3)
        self._readBuffer=bytearray(6)
        self.value = value
        
    def write_dac(self, value):
        if value < 0 : value = 0
        if value > 4095 : value = 4095
        self.value = value
        self._writeBuffer[0] = MCP4725_WRITE_DAC;
        self._writeBuffer[1] = self.value >> 4;
        self._writeBuffer[2] = self.value << 4;
        self.i2c.writeto(self.address,self._writeBuffer)
        
    def write_eeprom(self, value):
        if value < 0 : value = 0
        if value > 4095 : value = 4095
        self.value = value
        self._writeBuffer[0] = MCP4725_WRITE_EEPROM;
        self._writeBuffer[1] = self.value >> 4;
        self._writeBuffer[2] = self.value << 4;
        self.i2c.writeto(self.address,self._writeBuffer)
        
    def power_down(self, mode='1k'):
        """Power OFF output of DAC with a default 1k pull down"""
        self._writeBuffer[0] = MCP4725_WRITE_DAC | (POWER_DOWN_MODE[mode] << 1);
        self._writeBuffer[1] = self.value >> 4;
        self._writeBuffer[2] = self.value << 4;
        self.i2c.writeto(self.address,self._writeBuffer)
        
    def power_up(self):
        """Power ON output of DAC"""
        self._writeBuffer[0] = MCP4725_WRITE_DAC | (POWER_DOWN_MODE['Off'] << 1);
        self._writeBuffer[1] = self.value >> 4;
        self._writeBuffer[2] = self.value << 4;
        self.i2c.writeto(self.address,self._writeBuffer)
        
    def read_dac(self):
        self._readBuffer = self.i2c.readfrom(self.address, 6)
        return (self._readBuffer[1] << 4) + ((self._readBuffer[2] >> 4) & 0x0F)
        
    def read_eeprom(self):
        self._readBuffer = self.i2c.readfrom(self.address, 6)
        return ((self._readBuffer[3] & 0x0F) << 8) + (self._readBuffer[4])
        
        
        
        