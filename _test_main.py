import uasyncio as asyncio
from threadsafe import ThreadSafeQueue
import _thread
from time import sleep_ms
from micropython import const
from pmt_display import PmtDisplay, display
from machine import ADC, I2C, Pin, PWM
import mcp4725
from primitives import Queue, Pushbutton, Encoder, Switch

disp1 = display()
disp_regs1 = disp1.registers

disp2 = display()
disp_regs2 = disp2.registers

btn1 = Pin(7, Pin.IN, Pin.PULL_UP)	#GP1 = Enc 2, GP7 = Enc 1
pb1 = Pushbutton(btn1, suppress=True)
px1 = Pin(8, Pin.IN, Pin.PULL_UP)	#GP2 = Enc 2, GP8 = Enc 1
py1 = Pin(9, Pin.IN, Pin.PULL_UP)	#GP3 = Enc 2, GP9 = Enc 1

btn2 = Pin(1, Pin.IN, Pin.PULL_UP)	#GP1 = Enc 2, GP7 = Enc 1
pb2 = Pushbutton(btn2, suppress=True)
px2 = Pin(2, Pin.IN, Pin.PULL_UP)	#GP2 = Enc 2, GP8 = Enc 1
py2 = Pin(3, Pin.IN, Pin.PULL_UP)	#GP3 = Enc 2, GP9 = Enc 1

# Callbacks for encoders
def cb1(pos, delta):
    print("enc 1", pos, delta)

def cb2(pos, delta):
    print("enc 2", pos, delta)

# i2c for DACs
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
# 2 DACs - one for each channel
dac1 = mcp4725.MCP4725(i2c,address=const(0x61))
dac2 = mcp4725.MCP4725(i2c)		# mcp4725.MCP4725(i2c,address=const(0x60))

def _short_press1():
    print("1:SHORT")
    
def _double_press1():
    print("1:DOUBLE")
    
def _long_press1():
    print("1:LONG")

def _short_press2():
    print("2:SHORT")
    
def _double_press2():
    print("2:DOUBLE")
    
def _long_press2():
    print("2:LONG")

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

def core_2(q1, q2):  # Run on core 2
    display1 = PmtDisplay(cs=13, dc=11, sck=14, mosi=15, bl=20)
    display2 = PmtDisplay(cs=17, dc=16, sck=18, mosi=19, bl=12)
    
    display1.set_background()
    display1.regs['voltage'] = (True, 1234, True)
    display1.regs['status'] = (True, True)
    display1.regs['mode'] = (True, 2)
    display1.update()
    
    display2.set_background()
    display2.regs['voltage'] = (True, 5678, True)
    display2.regs['status'] = (True, True)
    display2.regs['mode'] = (True, 2)
    display2.update()
    
    while True:
        display1.regs = q1.get_sync(block=True)
        display1.update()
        display2.regs = q2.get_sync(block=True)
        display2.update()
        
async def switch_close1(evt):
    while True:
        evt.clear()  # re-enable the event
        await evt.wait()  # minimal resources used while paused
        print("Switch 1 closed.")
        # Omitted code runs each time the switch closes

async def switch_open1(evt):
    while True:
        evt.clear()  # re-enable the event
        await evt.wait()  # minimal resources used while paused
        print("Switch 1 open.")
        # Omitted code runs each time the switch closes

async def switch_close2(evt):
    while True:
        evt.clear()  # re-enable the event
        await evt.wait()  # minimal resources used while paused
        print("Switch 2 closed.")
        # Omitted code runs each time the switch closes

async def switch_open2(evt):
    while True:
        evt.clear()  # re-enable the event
        await evt.wait()  # minimal resources used while paused
        print("Switch 2 open.")
        # Omitted code runs each time the switch closes

async def read_adc(channel, period_ms, q1, q2):
    while True:
        adc = ADC(Pin(26+channel))
        reading = min(adc.read_u16()>>3, 4095)        
        disp_regs1['interlock'] = (True, reading)        
        disp_regs2['interlock'] = (True, reading>>1)
        if reading < 2000:
            disp_regs1['status'] = (True, True)
        else:
            disp_regs1['status'] = (True, False)
        try:
            q1.put_sync(disp_regs1)
        except IndexError:
            pass
            # Queue is full
        try:
            q2.put_sync(disp_regs2)
        except IndexError:
            pass
            # Queue is full
          
        await asyncio.sleep_ms(period_ms)       

async def main():
    # Set up thread safe queue for displays and tasks
    disp1_to_core2 = ThreadSafeQueue(disp_regs1)
    disp2_to_core2 = ThreadSafeQueue(disp_regs2)
    _thread.start_new_thread(core_2, (disp1_to_core2, disp2_to_core2))
    # set up reading ADC for light measurement
    asyncio.create_task(read_adc(1, 3, disp1_to_core2, disp2_to_core2))
    # set up button presses
    short_press1 = pb1.release_func(_short_press1, ())
    double_press1 = pb1.double_func(_double_press1, ())
    long_press1 = pb1.long_func(_long_press1, ())
    short_press2 = pb2.release_func(_short_press2, ())
    double_press2 = pb2.double_func(_double_press2, ())
    long_press2 = pb2.long_func(_long_press2, ())
    # set up encoders
    enc1 = Encoder(px1, py1, div=4, v=0, vmin=0, vmax=9, wrap=True, callback=cb1)
    enc2 = Encoder(px2, py2, div=4, v=0, vmin=0, vmax=9, wrap=True, callback=cb2)
    # set up switches
    sw1 = Switch(Pin(10, Pin.IN))	#GP6 = Enc 2, GP10 = Enc 1
    sw1.close_func(None)  # Use event based interface
    sw1.open_func(None)
    switch_close1_task = asyncio.create_task(switch_close1(sw1.close))
    switch_open1_task = asyncio.create_task(switch_open1(sw1.open))
    sw2 = Switch(Pin(6, Pin.IN))	#GP6 = Enc 2, GP10 = Enc 1
    sw2.close_func(None)  # Use event based interface
    sw2.open_func(None)
    switch_close2_task = asyncio.create_task(switch_close2(sw2.close))
    switch_open2_task = asyncio.create_task(switch_open2(sw2.open))
    
    
    while True:
        await asyncio.sleep(1)

asyncio.run(main())

