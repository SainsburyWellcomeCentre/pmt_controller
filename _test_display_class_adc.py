import asyncio
from micropython import const
from machine import ADC, I2C, Pin, PWM
import mcp4725
from primitives import Queue
from pmt_display import PmtDisplay

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
dac2 = mcp4725.MCP4725(i2c)
#dac1 = mcp4725.MCP4725(i2c,address=const(0x60))
dac1 = mcp4725.MCP4725(i2c,address=const(0x61))

#Pin 26 ADC0 = vref_ext1
#Pin 28 ADC2 = vref_ext2
#Pin 27 ADC1 = lux

display1 = PmtDisplay(cs=13, dc=11, sck=14, mosi=15, bl=20)
display2 = PmtDisplay(cs=17, dc=16, sck=18, mosi=19, bl=12)


async def read_adc(channel, period_ms, q):
    while True:
        adc = ADC(Pin(26+channel))
        reading = min(adc.read_u16()>>3, 4095)
        await q.put(reading)
        await asyncio.sleep_ms(period_ms)

async def update_dac(q):
    while True:
        lux_volt = await q.get()
        print(lux_volt)
        dac1.write_dac(lux_volt)
        display1.update_display_voltage(lux_volt)

async def print_adc(q):
    while True:
        value = await q.get()
        print(value)

async def main():
    q = Queue()
    q0 = Queue()
    q2 = Queue()
    asyncio.create_task(read_adc(0, 100, q0))
    asyncio.create_task(read_adc(0, 100, q2))
    asyncio.create_task(read_adc(1, 3, q))
    asyncio.create_task(update_dac(q))
    asyncio.create_task(print_adc(q0))
    asyncio.create_task(print_adc(q2))
    while True:
        await asyncio.sleep(1)
         
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Interrupted')


