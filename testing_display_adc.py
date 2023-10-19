import asyncio
from micropython import const
from machine import ADC, I2C, Pin, PWM
import mcp4725
from primitives import Queue
from pimoroni_bus import SPIBus
from picographics import PicoGraphics, DISPLAY_LCD_240X240, PEN_P8

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
dac1 = mcp4725.MCP4725(i2c)
#dac1 = mcp4725.MCP4725(i2c,address=const(0x60))
dac2 = mcp4725.MCP4725(i2c,address=const(0x61))

#Pin 26 ADC0 = vref_ext1
#Pin 28 ADC2 = vref_ext2
#Pin 27 ADC1 = lux

pwm1 = PWM(Pin(12), freq=2000, duty_u16=15000)	# 32768 Range = 0 - 65535
spibus1 = SPIBus(cs=13, dc=11, sck=14, mosi=15)
display1 = PicoGraphics(display=DISPLAY_LCD_240X240, bus=spibus1, pen_type=PEN_P8, rotate=90)

BLACK = display1.create_pen(0, 0, 0)
WHITE = display1.create_pen(255, 255, 255)
RED = display1.create_pen(255, 0, 0)
GREEN = display1.create_pen(0, 255, 0)
BLUE = display1.create_pen(0, 0, 255)

display1.set_pen(BLACK)
display1.clear()
display1.update()
display1.set_font("sans")

def update_display_voltage(voltage):
    display1.set_pen(BLACK)
    display1.rectangle(0, 80, 240, 80)
    display1.set_pen(BLUE)
    display1.text("{:04.0f}".format(voltage),5,120,scale=3)
    display1.update()

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
        dac2.write_dac(lux_volt)
        update_display_voltage(lux_volt)

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

