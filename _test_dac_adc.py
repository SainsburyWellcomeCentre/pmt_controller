import time
import random
from micropython import const
from machine import ADC, I2C, Pin
import mcp4725

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
dac1 = mcp4725.MCP4725(i2c)
#dac1 = mcp4725.MCP4725(i2c,address=const(0x60))
dac2 = mcp4725.MCP4725(i2c,address=const(0x61))

vref_ext1 = ADC(Pin(26))
vref_ext2 = ADC(Pin(28))
lux = ADC(Pin(27))

while True:
#    extern_voltage1 = vref_ext1.read_u16()
#    time.sleep(0.003)
#    extern_voltage2 = vref_ext2.read_u16()
#    time.sleep(0.003)
    lux_voltage = min(lux.read_u16()>>3, 4095)
    time.sleep(0.003)

    print(lux_voltage)
#    print(extern_voltage1)
#    print(extern_voltage2)
#    if lux_voltage > 4095:
#        lux_voltage = 4095

#    dac1.write_dac(2000)
#    print(dac1.read_dac())
    dac2.write_dac(lux_voltage)
#    print(dac2.read_dac())
    
#    time.sleep(1)