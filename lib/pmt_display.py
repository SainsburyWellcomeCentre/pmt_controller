from pimoroni_bus import SPIBus
from picographics import PicoGraphics, DISPLAY_LCD_240X240, PEN_P8
from primitives import Queue
from machine import Pin, PWM

class PmtDisplay():
    
    def __init__(self, cs, dc, sck, mosi, bl):
        self.pwm = PWM(Pin(bl), freq=2000, duty_u16=15000)
        spibus = SPIBus(cs=cs, dc=dc, sck=sck, mosi=mosi)
        
        self.display = PicoGraphics(display=DISPLAY_LCD_240X240, bus=spibus, pen_type=PEN_P8, rotate=90)

#        super().__init__(display=DISPLAY_LCD_240X240, bus=spibus, pen_type=PEN_P8, rotate=90)

        self.BLACK = self.display.create_pen(0, 0, 0)
        self.WHITE = self.display.create_pen(255, 255, 255)
        self.RED = self.display.create_pen(255, 0, 0)
        self.GREEN = self.display.create_pen(0, 255, 0)
        self.BLUE = self.display.create_pen(0, 0, 255)
        
        self.display.set_font("sans")
        self.display.set_pen(self.BLACK)
        self.display.clear()
        self.display.update()

    def clear_screen(self):
        self.display.set_pen(self.BLACK)
        self.display.clear()
        self.display.update()
        
    def update_display_voltage(self, voltage):
        self.display.set_pen(self.BLACK)
        self.display.rectangle(0, 80, 240, 80)
        self.display.set_pen(self.WHITE)
        self.display.text("{:04.0f}".format(voltage),5,120,scale=3)
        self.display.update()      
