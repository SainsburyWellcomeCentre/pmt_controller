from pimoroni_bus import SPIBus
from picographics import PicoGraphics, DISPLAY_LCD_240X240, PEN_P8
from primitives import Queue
from machine import Pin, PWM

class PmtDisplay():
  
    def __init__(self, cs, dc, sck, mosi, bl):
        
        self.regs = {
            'status': False,
            'voltage': (2244, False),
            'set_voltage': (0000, 0),
            'interlock': 0,
            'set_interlock': (0000, 0),
            'mode': 0
        }
        
        self.regs_old = self.regs.copy()
        
        self.pwm = PWM(Pin(bl), freq=2000, duty_u16=15000)
        spibus = SPIBus(cs=cs, dc=dc, sck=sck, mosi=mosi)
        
        self.display = PicoGraphics(display=DISPLAY_LCD_240X240, bus=spibus, pen_type=PEN_P8, rotate=90)

        self.BLACK = self.display.create_pen(0, 0, 0)
        self.WHITE = self.display.create_pen(255, 255, 255)
        self.RED = self.display.create_pen(255, 0, 0)
        self.GREEN = self.display.create_pen(0, 255, 0)
        self.BLUE = self.display.create_pen(0, 0, 255)
        self.GREY = self.display.create_pen(200, 200, 200)
        self.LIGHT_GREY = self.display.create_pen(100, 100, 100)
        
        self.display.set_font("sans")
        self.display.set_pen(self.BLACK)
        self.display.clear()
        self.display.update()

    def clear_screen(self):
        self.display.set_pen(self.BLACK)
        self.display.clear()
        self.display.update()
        
    def update_voltage(self):
        self.display.set_pen(self.BLACK)
        self.display.set_thickness(3)
        self.display.rectangle(0, 80, 240, 80)
        if self.regs['voltage'][1]:
            self.display.set_pen(self.RED)
        else:
            self.display.set_pen(self.WHITE)
        self.display.text("{:04.0f}V".format(self.regs['voltage'][0]),25,120,scale=2)
        
    def set_voltage(self):
        self.display.set_pen(self.BLACK)
        self.display.set_thickness(3)
        self.display.rectangle(0, 80, 240, 80)
        self.display.set_pen(self.BLUE)
        self.display.text("{:04.0f}V".format(self.regs['set_voltage'][0]),25,120,scale=2)
        self.display.rectangle(150-(self.regs['set_voltage'][1]*40), 145, 30, 4)
        self.display.rectangle(150-(self.regs['set_voltage'][1]*40), 85, 30, 4)
        
    def update_interlock_level(self):
        self.display.set_pen(self.BLACK)
        self.display.set_thickness(2)
        self.display.rectangle(121, 201, 119, 39)
        self.display.set_pen(self.WHITE)
        self.display.text("{:04.0f}u".format(self.regs['interlock']),130,221,scale=1)
        
    def set_interlock_level(self):
        self.display.set_pen(self.BLACK)
        self.display.set_thickness(2)
        self.display.rectangle(121, 201, 119, 39)
        self.display.set_pen(self.BLUE)
        self.display.text("{:04.0f}u".format(self.regs['set_interlock'][0]),130,221,scale=1)
        self.display.rectangle(195-(self.regs['set_interlock'][1]*10), 233, 10, 2)
        self.display.rectangle(195-(self.regs['set_interlock'][1]*10), 203, 10, 2)  
        
    def update_pmt_status(self):
        if self.regs['status']:
            self.display.set_pen(self.BLACK)
            self.display.set_thickness(3)
            self.display.rectangle(0, 0, 240, 39)
            self.display.set_pen(self.RED)
            self.display.text("PMT ON", 62, 24, scale=1)
        else:
            self.display.set_pen(self.BLACK)
            self.display.set_thickness(2)
            self.display.rectangle(0, 0, 240, 39)
            self.display.set_pen(self.GREY)
            self.display.text("PMT OFF", 56, 24, scale=1)
              
    def update_user_mode(self):
        if self.regs['mode'] == 0:
            self.display.set_pen(self.BLACK)
            self.display.set_thickness(2)
            self.display.rectangle(0, 201, 119, 39)
            self.display.set_pen(self.RED)
            self.display.text("INT", 40, 221, scale=1)
            self.display.update()
        elif self.regs['mode'] == 1:
            self.display.set_pen(self.BLACK)
            self.display.set_thickness(2)
            self.display.rectangle(0, 201, 119, 39)
            self.display.set_pen(self.BLUE)
            self.display.text("TRACK", 15, 221, scale=1)
            self.display.update()
        else:
            self.display.set_pen(self.BLACK)
            self.display.set_thickness(2)
            self.display.rectangle(0, 201, 119, 39)
            self.display.set_pen(self.BLUE)
            self.display.text("EXT", 40, 221, scale=1)
            self.display.update()

    def set_background(self):
        self.display.set_pen(self.LIGHT_GREY)
        self.display.rectangle(0, 199, 240, 2)	# bottom box top line
        self.display.rectangle(119, 199, 2, 42)	# bottom box dividing line
        self.display.rectangle(0, 180, 240, 2)	# title box top line
        self.display.rectangle(119, 179, 2, 22)	# title box dividing line
        self.display.rectangle(0, 42, 240, 2)	# top box bottom line
        self.display.set_pen(self.WHITE)
        self.display.set_thickness(1)
        self.display.text("MODE", 40, 190, scale=0.5)
        self.display.text("LEVEL", 160, 190, scale=0.5)
        
    def update(self):
        if self.regs['voltage'] != self.regs_old['voltage']:
            self.update_voltage()
        if self.regs['set_voltage'] != self.regs_old['set_voltage']:
            self.set_voltage()
        if self.regs['interlock'] != self.regs_old['interlock']:
            self.update_interlock_level()
        if self.regs['set_interlock'] != self.regs_old['set_interlock']:
            self.set_interlock_level()
        if self.regs['status'] != self.regs_old['status']:
            self.update_pmt_status()
        if self.regs['mode'] != self.regs_old['mode']:
            self.update_user_mode()
        
        self.regs_old = self.regs.copy()
        self.display.update()
