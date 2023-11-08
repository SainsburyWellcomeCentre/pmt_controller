import uasyncio as asyncio
from threadsafe import ThreadSafeQueue
import _thread
from time import sleep_ms
from micropython import const
from pmt_display import PmtDisplay, PmtController
from machine import ADC, I2C, Pin, PWM
import mcp4725
from primitives import Queue, Pushbutton, Encoder, Switch

max_interlock_value = 500	# max value to set for the interlock trigger
max_voltage_value = 1234 # change to 800

pmt1 = PmtController()
pmt1_regs = pmt1.registers
pmt1_regs['controller'] = 1

pmt2 = PmtController()
pmt2_regs = pmt2.registers
pmt2_regs['controller'] = 2

pmt_enable1 = Pin(21, Pin.OUT)	#GP22 = Enc 2, GP21 = Enc 1
pmt_enable1.off()
pmt_enable2 = Pin(22, Pin.OUT)	#GP22 = Enc 2, GP21 = Enc 1
pmt_enable2.off()

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
#    print("enc 1", pos, delta)
    if pmt1_regs['state'][1] == 1:
        pass
    if pmt1_regs['state'][1] == 2:
        pmt1_regs['state'] = (True, pmt1_regs['state'][1], True)
        interlock_val = pmt1_regs['set_interlock'][1] + (delta * pow(10, pmt1_regs['set_interlock'][2]))
        interlock_val = 0 if interlock_val < 0 else max_interlock_value if interlock_val > max_interlock_value else interlock_val
        pmt1_regs['set_interlock'] = (True, interlock_val, pmt1_regs['set_interlock'][2])
    if pmt1_regs['state'][1] == 3:
        pmt1_regs['state'] = (True, pmt1_regs['state'][1], True)
        if pmt1_regs['mode'][1] != 2:
#            if pmt1_regs['mode'][1] == 0:
            if delta > 0:
                pmt1_regs['mode'] = (True, 1)
            else:
                pmt1_regs['mode'] = (True, 0)
    if pmt1_regs['state'][1] == 4 and pmt1_regs['mode'][1] == 0:
        pmt1_regs['state'] = (True, pmt1_regs['state'][1], True)
        voltage_val = pmt1_regs['set_voltage'][1] + (delta * pow(10, pmt1_regs['set_voltage'][2]))
        voltage_val = 0 if voltage_val < 0 else max_voltage_value if voltage_val > max_voltage_value else voltage_val
        pmt1_regs['set_voltage'] = (True, voltage_val, pmt1_regs['set_voltage'][2])
        

def cb2(pos, delta):
    print("enc 2", pos, delta)

# i2c for DACs
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
# 2 DACs - one for each channel
dac1 = mcp4725.MCP4725(i2c,address=const(0x61))
dac2 = mcp4725.MCP4725(i2c)		# mcp4725.MCP4725(i2c,address=const(0x60))

def _short_press1():
#    print("1:SHORT")
    if not pmt1_regs['state'][2]:
        state = pmt1_regs['state'][1] + 1
        if state > 4:
            state = 0            
        elif state < 0:
            state = 4    
        pmt1_regs['state'] = (True, state, pmt1_regs['state'][2])
        
    print(pmt1_regs['controller'], pmt1_regs['state'])
    
def _double_press1():
#    print("1:DOUBLE")
#    pmt1_regs['state'] = (pmt1_regs['state'][0], True)
    if pmt1_regs['state'][1] == 2:
        pmt1_regs['state'] = (True, pmt1_regs['state'][1], True)
        interlock_dec = pmt1_regs['set_interlock'][2] + 1
        if interlock_dec > 3:
            interlock_dec = 0            
        elif interlock_dec < 0:
            interlock_dec = 3   
        pmt1_regs['set_interlock'] = (True, pmt1_regs['set_interlock'][1], interlock_dec)
        print(pmt1_regs['controller'], pmt1_regs['state'], pmt1_regs['set_interlock'])
    elif pmt1_regs['state'][1] == 4:
        pmt1_regs['state'] = (True, pmt1_regs['state'][1], True)
        voltage_dec = pmt1_regs['set_voltage'][2] + 1
        if voltage_dec > 3:
            voltage_dec = 0            
        elif voltage_dec < 0:
            voltage_dec = 3   
        pmt1_regs['set_voltage'] = (True, pmt1_regs['set_voltage'][1], voltage_dec)
        print(pmt1_regs['controller'], pmt1_regs['state'], pmt1_regs['set_voltage'])
        
def _long_press1():
#    print("1:LONG")
#    pmt1_regs['state'] = (True, pmt1_regs['state'][1], False) # this keeps the existing state which means the rotary switch can still modify the values
    print(pmt1_regs['controller'], pmt1_regs['state'])
    pmt1_regs['state'] = (True, 0, False)	# reset the state to the void state
    print(pmt1_regs['controller'], pmt1_regs['state'])

def _short_press2():
    print("2:SHORT")
    
def _double_press2():
    print("2:DOUBLE")
    
def _long_press2():
    print("2:LONG")

def core_2(q1, q2):  # Run on core 2
    display1 = PmtDisplay(cs=13, dc=11, sck=14, mosi=15, bl=20)
    display2 = PmtDisplay(cs=17, dc=16, sck=18, mosi=19, bl=12)
    
    display1.set_background()
    display1.regs['voltage'] = (True, 0, False)
    display1.regs['pmt_status'] = (True, False, False)
    display1.update()
    
    display2.set_background()
    display2.regs['voltage'] = (True, 0, False)
    display2.regs['pmt_status'] = (True, False, False)
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
        pmt1_regs['mode'] = (True, 2)

async def switch_open1(evt):
    while True:
        evt.clear()  # re-enable the event
        await evt.wait()  # minimal resources used while paused
        print("Switch 1 open.")
        pmt1_regs['mode'] = (True, 1)

async def switch_close2(evt):
    while True:
        evt.clear()  # re-enable the event
        await evt.wait()  # minimal resources used while paused
        print("Switch 2 closed.")
        pmt2_regs['mode'] = (True, 2)

async def switch_open2(evt):
    while True:
        evt.clear()  # re-enable the event
        await evt.wait()  # minimal resources used while paused
        print("Switch 2 open.")
        pmt2_regs['mode'] = (True, 1)

async def read_adc(channel, period_ms, _pmt1_regs, _pmt2_regs, q1, q2):
    while True:
        adc = ADC(Pin(26+channel))
        reading = min(adc.read_u16()>>3, 4095)        
        _pmt1_regs['interlock'] = (True, reading)        
        _pmt2_regs['interlock'] = (True, reading)
        
        if reading < _pmt1_regs['set_interlock'][1]:
            _pmt1_regs['interlock_status'] = (True, True)
        else:
            pmt_enable1.off()
            _pmt1_regs['interlock_status'] = (True, False)
            _pmt1_regs['pmt_status'] = (True, False, False)
        
        if reading < _pmt2_regs['set_interlock'][1]:
            _pmt2_regs['interlock_status'] = (True, True)
        else:
            pmt_enable2.off()
            _pmt2_regs['interlock_status'] = (True, False)
            _pmt2_regs['pmt_status'] = (True, False, False)
            
        try:
            q1.put_sync(pmt1_regs)
        except IndexError:
            pass
            # Queue is full
        try:
            q2.put_sync(pmt2_regs)
        except IndexError:
            pass
            # Queue is full
         
        dac1.write_dac(reading)	# just temp to test ext track
        dac2.write_dac(reading)	# just temp to test ext track
        await asyncio.sleep_ms(period_ms)        

async def read_DAQ(channel, period_ms, pmt_regs, q):
    while True:
        adc = ADC(Pin(26+channel))
        reading = adc.read_u16() #* 6.2 / 65536
        reading = int(reading * 0.096) - 64
#        print(reading)
#        reading = int((reading * 6.2))>>16
#        reading = (reading * 775)>>15
#        disp_regs['voltage'] = (True, reading, True) # x, x, True for now - update for PMT power pmt_status
        if pmt_regs['mode'][1] != 0:
            pmt_regs['voltage'] = (True, reading, pmt_regs['pmt_status'][1])
        else:
            pmt_regs['set_voltage'] = (True, pmt_regs['set_voltage'][1], pmt_regs['set_voltage'][2])
        try:
            q.put_sync(pmt_regs)
        except IndexError:
            pass
            # Queue is full
            
#        await q.put(reading)
        await asyncio.sleep_ms(period_ms)

async def main():
    # Set up thread safe queue for displays and tasks
    pmt1_to_core2 = ThreadSafeQueue(pmt1_regs)
    pmt2_to_core2 = ThreadSafeQueue(pmt2_regs)
    _thread.start_new_thread(core_2, (pmt1_to_core2, pmt2_to_core2))
    # set up reading ADC for light measurement
    asyncio.create_task(read_adc(1, 3, pmt1_regs, pmt2_regs, pmt1_to_core2, pmt2_to_core2))
    # set up reading ADCs for DAQ input
    asyncio.create_task(read_DAQ(2, 100, pmt1_regs, pmt1_to_core2))
    asyncio.create_task(read_DAQ(0, 100, pmt2_regs, pmt2_to_core2))
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
    _sw1 = Pin(10, Pin.IN)
    sw1 = Switch(_sw1)	#GP6 = Enc 2, GP10 = Enc 1
    if _sw1.value():
        pmt1_regs['mode'] = (True, 1)
    else:
        pmt1_regs['mode'] = (True, 2)
        
    sw1.close_func(None)  # Use event based interface
    sw1.open_func(None)
    switch_close1_task = asyncio.create_task(switch_close1(sw1.close))
    switch_open1_task = asyncio.create_task(switch_open1(sw1.open))
    _sw2 = Pin(6, Pin.IN)
    sw2 = Switch(_sw2)	#GP6 = Enc 2, GP10 = Enc 1
    if _sw2.value():
        pmt2_regs['mode'] = (True, 1)
        sw2_state = False
    else:
        pmt2_regs['mode'] = (True, 2)
        sw2_state = True
    
    sw2.close_func(None)  # Use event based interface
    sw2.open_func(None)
    switch_close2_task = asyncio.create_task(switch_close2(sw2.close))
    switch_open2_task = asyncio.create_task(switch_open2(sw2.open))
         
    while True:
        await asyncio.sleep(1)

asyncio.run(main())

