import time
import random
from machine import Pin,PWM
from pimoroni_bus import SPIBus
from picographics import PicoGraphics, DISPLAY_LCD_240X240, PEN_P8

pwm1 = PWM(Pin(12), freq=2000, duty_u16=15000)	# 32768 Range = 0 - 65535
pwm2 = PWM(Pin(20), freq=2000, duty_u16=15000)	# 32768 Range = 0 - 65535

spibus0 = SPIBus(cs=17, dc=16, sck=18, mosi=19)
spibus1 = SPIBus(cs=13, dc=11, sck=14, mosi=15)

display1 = PicoGraphics(display=DISPLAY_LCD_240X240, bus=spibus1, pen_type=PEN_P8)
display2 = PicoGraphics(display=DISPLAY_LCD_240X240, bus=spibus0, pen_type=PEN_P8)

WIDTH, HEIGHT = display1.get_bounds()

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
for i in range(0, 10):
    r = random.randint(0, 10) + 3
    balls1.append(
        Ball(
            random.randint(r, r + (WIDTH - 2 * r)),
            random.randint(r, r + (HEIGHT - 2 * r)),
            r,
            (14 - r) / 2,
            (14 - r) / 2,
            display1.create_pen(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        )
    )

for i in range(0, 20):
    r = random.randint(0, 10) + 3
    balls2.append(
        Ball(
            random.randint(r, r + (WIDTH - 2 * r)),
            random.randint(r, r + (HEIGHT - 2 * r)),
            r,
            (14 - r) / 2,
            (14 - r) / 2,
            display2.create_pen(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        )
    )

BG1 = display1.create_pen(40, 40, 40)
BG2 = display2.create_pen(40, 40, 40)

while True:
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
        
        display2.set_pen(ball.pen)
        display2.circle(int(ball.x), int(ball.y), int(ball.r))

    display1.update()
    display2.update()
    
    time.sleep(0.01)