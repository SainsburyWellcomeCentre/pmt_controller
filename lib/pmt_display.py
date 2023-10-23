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
        self.GREY = self.display.create_pen(200, 200, 200)
        
        self.display.set_font("sans")
        self.display.set_pen(self.BLACK)
        self.display.clear()
        self.display.update()

    def clear_screen(self):
        self.display.set_pen(self.BLACK)
        self.display.clear()
        self.display.update()
        
    def update_display_voltage(self, value):
        self.display.set_pen(self.BLACK)
        self.display.set_thickness(3)
        self.display.rectangle(0, 80, 240, 80)
        self.display.set_pen(self.WHITE)
        self.display.text("{:04.0f}V".format(value),25,120,scale=2)
        self.display.update()      

    def set_display_voltage(self, value, set):
        self.display.set_pen(self.BLACK)
        self.display.set_thickness(3)
        self.display.rectangle(0, 80, 240, 80)
        self.display.set_pen(self.RED)
        self.display.text("{:04.0f}V".format(value),25,120,scale=2)
        self.display.rectangle(150-(set*40), 145, 30, 4)
        self.display.rectangle(150-(set*40), 85, 30, 4)
        self.display.update()
        
    def update_display_interlock_level(self, value):
        self.display.set_pen(self.BLACK)
        self.display.set_thickness(2)
        self.display.rectangle(121, 201, 119, 39)
        self.display.set_pen(self.WHITE)
        self.display.text("{:04.0f}u".format(value),130,220,scale=1)
        self.display.update() 
        
    def update_display_pmt_status(self, status):
        if status:
            self.display.set_pen(self.BLACK)
            self.display.set_thickness(3)
            self.display.rectangle(0, 0, 240, 39)
            self.display.set_pen(self.RED)
            self.display.text("PMT ON", 62, 24, scale=1)
            self.display.update()
        else:
            self.display.set_pen(self.BLACK)
            self.display.set_thickness(2)
            self.display.rectangle(0, 0, 240, 39)
            self.display.set_pen(self.GREY)
            self.display.text("PMT OFF", 56, 24, scale=1)
            self.display.update()
              
    def update_display_user_mode(self, mode):
        if mode == 0:
            self.display.set_pen(self.BLACK)
            self.display.set_thickness(2)
            self.display.rectangle(0, 201, 119, 39)
            self.display.set_pen(self.RED)
            self.display.text("DEBUG", 20, 220, scale=0.75)
            self.display.update()
        elif mode == 1:
            self.display.set_pen(self.BLACK)
            self.display.set_thickness(2)
            self.display.rectangle(0, 201, 119, 39)
            self.display.set_pen(self.BLUE)
            self.display.text("FOLLOW", 20, 220, scale=0.75)
            self.display.update()
        else:
            self.display.set_pen(self.BLACK)
            self.display.set_thickness(2)
            self.display.rectangle(0, 201, 119, 39)
            self.display.set_pen(self.BLUE)
            self.display.text("PASS", 20, 220, scale=0.75)
            self.display.update()

    def set_background(self):
        self.display.set_pen(self.GREY)
        self.display.rectangle(0, 199, 240, 2)
        self.display.rectangle(119, 199, 2, 42)
        self.display.rectangle(0, 42, 240, 2)
#        self.display.rectangle(119, 0, 2, 42)
        self.display.set_pen(self.WHITE)
        self.display.set_thickness(1)
        self.display.text("MODE", 20, 190, scale=0.5)
        self.display.text("LEVEL", 190, 190, scale=0.5)
        
        
