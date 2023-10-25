import uasyncio as asyncio
from micropython import const
from machine import ADC, I2C, Pin, PWM
import mcp4725
from primitives import Queue, Pushbutton, Encoder
from pmt_display import PmtDisplay
from threadsafe import ThreadSafeQueue
import _thread
from time import sleep_ms

btn = Pin(7, Pin.IN, Pin.PULL_UP)	#GP1 = Enc 2, GP7 = Enc 1
pb = Pushbutton(btn, suppress=True)

px = Pin(8, Pin.IN, Pin.PULL_UP)	#GP2 = Enc 2, GP8 = Enc 1
py = Pin(9, Pin.IN, Pin.PULL_UP)	#GP3 = Enc 2, GP9 = Enc 1


i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
dac2 = mcp4725.MCP4725(i2c)
#dac1 = mcp4725.MCP4725(i2c,address=const(0x60))
dac1 = mcp4725.MCP4725(i2c,address=const(0x61))

#Pin 26 ADC0 = vref_ext1
#Pin 28 ADC2 = vref_ext2
#Pin 27 ADC1 = lux

disp_regs = {
    'status': (False, False),
    'voltage': (2244, False),
    'set_voltage': (False, 0000, 0),
    'interlock': (False, 0000),
    'set_interlock': (False, 0000, 0),
    'mode': (False, 0)
}

disp_regs_from = {
    'status': (False, False),
    'voltage': (2244, False),
    'set_voltage': (False, 0000, 0),
    'interlock': (False, 0000),
    'set_interlock': (False, 0000, 0),
    'mode': (False, 0)
}

def cb(pos, delta):
    print(pos, delta)
    
enc = Encoder(px, py, div=4, v=0, vmin=0, vmax=9, wrap=True, callback=cb)

enable_15V = Pin(21, Pin.OUT)	#GP22 = Enc 2, GP21 = Enc 1
enable_15V.off()

def core_2(getq, putq):  # Run on core 2
    print("core_2")
    display1 = PmtDisplay(cs=13, dc=11, sck=14, mosi=15, bl=20)
    display2 = PmtDisplay(cs=17, dc=16, sck=18, mosi=19, bl=12)
    
    display1.set_background()
    display1.regs['voltage'] = (True, 1234, True)
    display1.regs['status'] = (True, True)
    display1.regs['mode'] = (True, 2)
    display1.update()
#    print("displays set")
    
    while True:
#        print("in core2")
        display1.regs = await getq.get(block=True) 
#        print("got a val")
        display1.update()
#        sleep_ms(30)

def _short_press():
    print("SHORT")
    display1.set_background()
    display1.regs['voltage'] = (True, 1234, True)
    display1.regs['status'] = (True, True)
    display1.regs['mode'] = (True, 2)
    display1.update()
    
def _double_press():
    print("DOUBLE")
    display1.regs['voltage'] = (True, 1023, True)
#    display1.update_volatge()
    display1.update()
    
def _long_press():
    print("LONG")
    display1.regs['set_voltage'] = (True, 1234, 2)
#    display1.set_voltage()
    display1.update()

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


async def read_adc(channel, period_ms, q):
    while True:
        adc = ADC(Pin(26+channel))
        reading = min(adc.read_u16()>>3, 4095)
        await q.put(reading)
        await asyncio.sleep_ms(period_ms)

async def update_dac(q, to_core2):
    while True:
        lux_volt = await q.get()
        dac1.write_dac(lux_volt)
        print(lux_volt)
        if lux_volt < 130:
            enable_15V.on()
        else:
            enable_15V.off()
        
        dac1.write_dac(lux_volt)
        disp_regs['interlock'] = (True, lux_volt)
        await to_core2.put(disp_regs)
#        display1.regs['interlock'] = (True, lux_volt)
#        display1.update_interlock_level()
#        display1.update()

async def print_adc(q):
    while True:
        value = await q.get()
        display1.regs['voltage'] = (True, value)
        display1.update()
#        print(value)

async def main():
    to_core2 = ThreadSafeQueue(disp_regs)
    from_core2 = ThreadSafeQueue(disp_regs_from)
    print("before thread")
    _thread.start_new_thread(core_2, (to_core2, from_core2))
    print("after thread start")
    short_press = pb.release_func(_short_press, ())
    double_press = pb.double_func(_double_press, ())
    long_press = pb.long_func(_long_press, ())
#    enc = Encoder(px, py, div=4, v=0, vmin=0, vmax=9, wrap=True, callback=cb)
    q = Queue()
#    q0 = Queue()
#    q2 = Queue()
#    asyncio.create_task(read_adc(2, 100, q0))
#    asyncio.create_task(read_adc(0, 100, q2))
    asyncio.create_task(read_adc(1, 1000, q))	# changed (1, 3, q)
    asyncio.create_task(update_dac(q, to_core2))
#    asyncio.create_task(print_adc(q0))
#    asyncio.create_task(print_adc(q2))
    while True:
        await asyncio.sleep(1)
         
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Interrupted')





