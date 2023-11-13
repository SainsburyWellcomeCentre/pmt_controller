import time
import random
from micropython import const
from machine import ADC, I2C, Pin
from rotary_irq_rp2 import RotaryIRQ
from pimoroni_bus import SPIBus
from picographics import PicoGraphics, DISPLAY_LCD_240X240, PEN_P8
import mcp4725

spibus1 = SPIBus(cs=17, dc=16, sck=18, mosi=19)
spibus2 = SPIBus(cs=13, dc=11, sck=14, mosi=15)

display1 = PicoGraphics(display=DISPLAY_LCD_240X240, bus=spibus1, pen_type=PEN_P8)
display2 = PicoGraphics(display=DISPLAY_LCD_240X240, bus=spibus2, pen_type=PEN_P8)

#display1.set_backlight(1.0)
#display2.set_backlight(1.0)

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
dac1 = mcp4725.MCP4725(i2c)
#dac1 = mcp4725.MCP4725(i2c,address=const(0x60))
dac2 = mcp4725.MCP4725(i2c,address=const(0x61))

vref_ext1 = ADC(Pin(26))
vref_ext2 = ADC(Pin(28))
lux = ADC(Pin(27))

encoder1 = RotaryIRQ(pin_num_clk=2,
              pin_num_dt=3,
              pin_num_bt=1,
              min_val=0,
              max_val=9,
              reverse=False,
              half_step=True,
              range_mode=RotaryIRQ.RANGE_WRAP)

encoder2 = RotaryIRQ(pin_num_clk=8,
              pin_num_dt=9,
              pin_num_bt=7,
              min_val=0,
              max_val=9,
              reverse=False,
              half_step=True,
              range_mode=RotaryIRQ.RANGE_WRAP)

enable_15V2 = Pin(21, Pin.OUT)
enable_15V2.off()
user_mode2 = Pin(10, Pin.IN)
enable_15V1 = Pin(22, Pin.OUT)
enable_15V1.off()
user_mode1 = Pin(6, Pin.IN)


WIDTH, HEIGHT = display1.get_bounds()

# We're creating 100 balls with their own individual colour and 1 BG colour
# for a total of 101 colours, which will all fit in the custom 256 entry palette!

class Ball:
    def __init__(self, x, y, r, dx, dy, pen1):
        self.x = x
        self.y = y
        self.r = r
        self.dx = dx
        self.dy = dy
        self.pen = pen1
#        self.pen = pen2


# initialise shapes
balls1 = []
balls2 = []
for i in range(0, 2):
    r = random.randint(0, 10) + 3
    balls1.append(
        Ball(
            random.randint(r, r + (WIDTH - 2 * r)),
            random.randint(r, r + (HEIGHT - 2 * r)),
            r,
            (14 - r) / 2,
            (14 - r) / 2,
            display1.create_pen(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
#            display2.create_pen(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
        )
    )

for i in range(0, 2):
    r = random.randint(0, 10) + 3
    balls2.append(
        Ball(
            random.randint(r, r + (WIDTH - 2 * r)),
            random.randint(r, r + (HEIGHT - 2 * r)),
            r,
            (14 - r) / 2,
            (14 - r) / 2,
#            display1.create_pen(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
            display2.create_pen(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
        )
    )

BG1 = display1.create_pen(40, 40, 40)
BG2 = display2.create_pen(40, 40, 40)


um1 = user_mode1.value()
um2 = user_mode2.value()
um1_old = um1
um2_old = um2


while True:
#    print(encoder1.value())
#    print(encoder1.button())
#    print(encoder2.value())
#    print(encoder2.button())
    extern_voltage1 = vref_ext1.read_u16()
    time.sleep(0.003)
    extern_voltage2 = vref_ext2.read_u16()
    time.sleep(0.003)
    lux_voltage = lux.read_u16()
    time.sleep(0.003)
    um1 = user_mode1.value()
    um2 = user_mode2.value()

    print(lux_voltage)
#    print(extern_voltage1)
#    print(extern_voltage2)

    if um1 != um1_old:    
        if user_mode1.value()==1:
            enable_15V1.on()
            dac1.write_dac(3000)
            print(dac1.read_dac())
        else:
            enable_15V1.off()
            dac1.write_dac(0)
            print(dac1.read_dac())

    if um2 != um2_old: 
        if user_mode2.value()==1:
            enable_15V2.on()
            dac2.write_dac(4000)
            print(dac2.read_dac())
        else:
            enable_15V2.off()
            dac2.write_dac(0)
            print(dac2.read_dac())

    um1_old = um1
    um2_old = um2

    display1.set_pen(BG1)
    display1.clear()
    display2.set_pen(BG2)
    display2.clear()

    for ball in balls1:
        ball.x += ball.dx
        ball.y += ball.dy

        xmax = WIDTH - ball.r
        xmin = ball.r
        ymax = HEIGHT - ball.r
        ymin = ball.r

        if ball.x < xmin or ball.x > xmax:
            ball.dx *= -1

        if ball.y < ymin or ball.y > ymax:
            ball.dy *= -1
        display1.set_pen(ball.pen)
        display1.circle(int(ball.x), int(ball.y), int(ball.r))
        
#        display2.set_pen(ball.pen)
#        display2.circle(int(ball.x), int(ball.y), int(ball.r))

    for ball in balls2:
        ball.x += ball.dx
        ball.y += ball.dy

        xmax = WIDTH - ball.r
        xmin = ball.r
        ymax = HEIGHT - ball.r
        ymin = ball.r

        if ball.x < xmin or ball.x > xmax:
            ball.dx *= -1

        if ball.y < ymin or ball.y > ymax:
            ball.dy *= -1
#        display1.set_pen(ball.pen)
#        display1.circle(int(ball.x), int(ball.y), int(ball.r))
        
        display2.set_pen(ball.pen)
        display2.circle(int(ball.x), int(ball.y), int(ball.r))

    display1.update()
    display2.update()
    
#    time.sleep(0.01)