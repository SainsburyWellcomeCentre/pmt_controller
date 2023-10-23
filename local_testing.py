import uasyncio as asyncio
from micropython import const
from machine import ADC, I2C, Pin, PWM
import mcp4725
from primitives import Queue, Pushbutton, Encoder
from pmt_display import PmtDisplay

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

display1 = PmtDisplay(cs=13, dc=11, sck=14, mosi=15, bl=20)
display2 = PmtDisplay(cs=17, dc=16, sck=18, mosi=19, bl=12)


def cb(pos, delta):
    print(pos, delta)
    
enc = Encoder(px, py, div=4, v=0, vmin=0, vmax=9, wrap=True, callback=cb)

enable_15V = Pin(21, Pin.OUT)	#GP22 = Enc 2, GP21 = Enc 1
enable_15V.off()

def _short_press():
    print("SHORT")
    display1.set_background()
    display1.update_display_voltage(1234)
    display1.update_display_pmt_status(True)
    
def _double_press():
    print("DOUBLE")
    display1.update_display_user_mode(2)
    display1.update_display_interlock_level(4234)
    display1.update_display_pmt_status(False)
    
def _long_press():
    print("LONG")
    display1.set_display_voltage(1234, 1)

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

async def update_dac(q):
    while True:
        lux_volt = await q.get()
        dac1.write_dac(lux_volt)
#        print(lux_volt)
        if lux_volt < 130:
            enable_15V.on()
        else:
            enable_15V.off()
        
        dac1.write_dac(lux_volt)
#        display1.update_display_voltage(lux_volt)

async def print_adc(q):
    while True:
        value = await q.get()
#        print(value)

async def main():
    short_press = pb.release_func(_short_press, ())
    double_press = pb.double_func(_double_press, ())
    long_press = pb.long_func(_long_press, ())
#    enc = Encoder(px, py, div=4, v=0, vmin=0, vmax=9, wrap=True, callback=cb)
    q = Queue()
#    q0 = Queue()
#    q2 = Queue()
#    asyncio.create_task(read_adc(0, 100, q0))
#    asyncio.create_task(read_adc(0, 100, q2))
#    asyncio.create_task(read_adc(1, 3, q))
#    asyncio.create_task(update_dac(q))
#    asyncio.create_task(print_adc(q0))
#    asyncio.create_task(print_adc(q2))
    while True:
        await asyncio.sleep(1)
         
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Interrupted')




