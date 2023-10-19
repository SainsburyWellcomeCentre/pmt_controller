import time
import random
from machine import Pin,PWM
from pimoroni_bus import SPIBus
from picographics import PicoGraphics, DISPLAY_LCD_240X240, PEN_P8

pwm1 = PWM(Pin(12), freq=2000, duty_u16=15000)	# 32768 Range = 0 - 65535
pwm2 = PWM(Pin(20), freq=2000, duty_u16=15000)	# 32768 Range = 0 - 65535

spibus0 = SPIBus(cs=17, dc=16, sck=18, mosi=19)
spibus1 = SPIBus(cs=13, dc=11, sck=14, mosi=15)

display1 = PicoGraphics(display=DISPLAY_LCD_240X240, bus=spibus1, pen_type=PEN_P8, rotate=90)
display2 = PicoGraphics(display=DISPLAY_LCD_240X240, bus=spibus0, pen_type=PEN_P8, rotate=90)

WIDTH, HEIGHT = display1.get_bounds()

BLACK = display1.create_pen(0, 0, 0)
WHITE = display1.create_pen(255, 255, 255)
RED = display1.create_pen(255, 0, 0)
GREEN = display1.create_pen(0, 255, 0)
BLUE = display1.create_pen(0, 0, 255)

display1.set_pen(BLACK)
display1.clear()
display1.update()

display2.set_pen(BLACK)
display2.clear()
display2.update()

display1.set_font("sans")

set = 1

display1.set_pen(BLACK)
display1.rectangle(0, 80, 240, 80)
display1.set_pen(WHITE)
display1.text("{:04.0f}".format(1234),5,120,scale=3)
display1.rectangle(195-(set*60), 150, 40, 2)
display1.update()