from micropython import const

from machine import ADC, I2C, Pin
from rotary_irq_rp2 import RotaryIRQ
from picographics import PicoGraphics, DISPLAY_LCD_240X240, PEN_P8

import mcp4725
import time

BUS_VOLTAGE = const(4.98)

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)

dac = mcp4725.MCP4725(i2c)

vref_ext = ADC(Pin(26))
lux = ADC(Pin(27))
vref_out = ADC(Pin(28))

enable_15V = Pin(22, Pin.OUT)
interlock = Pin(21, Pin.IN)
user_mode = Pin(11, Pin.IN)

display = PicoGraphics(display=DISPLAY_LCD_240X240, pen_type=PEN_P8, rotate=90)
display.set_backlight(1)
display.set_font("sans")

BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(255, 0, 0)
GREEN = display.create_pen(0, 255, 0)
BLUE = display.create_pen(0, 0, 255)

encoder = RotaryIRQ(pin_num_clk=8,
              pin_num_dt=9,
              pin_num_bt=7,
              min_val=0,
              max_val=9,
              reverse=False,
              half_step=True,
              range_mode=RotaryIRQ.RANGE_WRAP)

def dac_value(voltage):
    return int(4096/BUS_VOLTAGE*voltage)

def dac_voltage(value):
    return value / 4096 * BUS_VOLTAGE

def update_display_interlock():
    if interlock_status:
        display.set_pen(BLACK)
        display.rectangle(0, 0, 240, 40)
        display.set_pen(RED)
        display.text("PMT ON", 20, 20, scale=1)
        display.update()
    else:
        display.set_pen(BLACK)
        display.rectangle(0, 0, 240, 40)
        display.set_pen(BLUE)
        display.text("PMT OFF", 20, 20, scale=1)
        display.update()
          
def update_display_user_mode():
    if user_mode_status:
        display.set_pen(BLACK)
        display.rectangle(0, 200, 240, 40)
        display.set_pen(RED)
        display.text("MODE DEBUG", 20, 220, scale=1)
        display.update()
    else:
        display.set_pen(BLACK)
        display.rectangle(0, 200, 240, 40)
        display.set_pen(BLUE)
        display.text("MODE EXT", 20, 220, scale=1)
        display.update()

def update_display_voltage():
    if user_mode_status:
        display.set_pen(BLACK)
        display.rectangle(0, 80, 240, 80)
        display.set_pen(RED)
        display.text("{:04.0f}".format(debug_voltage),5,120,scale=3)
        display.rectangle(195-(set*60), 150, 40, 2)
        display.update()
    else:
        display.set_pen(BLACK)
        display.rectangle(0, 80, 240, 80)
        display.set_pen(BLUE)
        display.text("{:04.0f}".format(extern_voltage*250),5,120,scale=3)
        display.update()

def get_pos_nums(num):
    pos_nums = [0, 0, 0, 0]
    i = 0
    while num != 0:
        pos_nums[i] = (num % 10)
        num = num // 10
        i = i + 1
    return pos_nums

def get_num(pos_nums):
    if len(pos_nums) == 1:
        return pos_nums[0]
    elif len(pos_nums) == 2:
        return pos_nums[0] + 10 * pos_nums[1]
    elif len(pos_nums) == 3:
        return pos_nums[0] + 10 * pos_nums[1] + 100 * pos_nums[2]
    elif len(pos_nums) == 4:
        return pos_nums[0] + 10 * pos_nums[1] + 100 * pos_nums[2] + 1000 * pos_nums[3]

interlock_status = interlock.value()
user_mode_status = user_mode.value()
dac_v = dac.read_dac()
debug_voltage = dac_voltage(dac_v)
extern_voltage = vref_ext.read_u16() * 6.2 / 65536

if dac_v > 0:
    dac.write_eeprom(0)
    dac.write_dac(0)
    debug_voltage = 0

val_old = encoder.value()
but_old = encoder.button()
set = 0
voltage_set = get_pos_nums(int(debug_voltage*250))
debug_voltage = get_num(voltage_set)

display.set_pen(BLACK)
display.clear()

display.update()

enable_15V.on()

while True:
    val_new = encoder.value()
    but_new = encoder.button()  
           
    if but_old != but_new:
        but_old = but_new
        #print('button = ', but_new)
        if but_new == 0: set = set + 1
        if set > 3: set = 0
        encoder.set(value=voltage_set[set])

    if val_old != val_new:
        voltage_set[set] = val_new
        val_old = val_new
        debug_voltage = get_num(voltage_set)
        dac.write_dac(dac_value(debug_voltage/250))
        
        
    interlock_status = interlock.value()
    update_display_interlock()
    
    user_mode_status = user_mode.value()
    update_display_user_mode()
    
    #debug_voltage = dac_voltage(dac.read_dac())
    extern_voltage = vref_ext.read_u16() * 6.2 / 65536
    update_display_voltage()
        
    time.sleep_ms(100)
