import uasyncio as asyncio
from threadsafe import ThreadSafeQueue
import _thread
from time import sleep_ms
from pmt_display import PmtDisplay, display
from machine import ADC, Pin

disp1 = display()
disp_regs1 = disp1.registers

disp2 = display()
disp_regs2 = disp2.registers

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
        

async def read_adc(channel, period_ms, q1, q2):
    while True:
        adc = ADC(Pin(26+channel))
        reading = min(adc.read_u16()>>3, 4095)        
        disp_regs1['voltage'] = (True, reading, True)        
        disp_regs2['voltage'] = (True, reading>>1, True)
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
    disp1_to_core2 = ThreadSafeQueue(disp_regs1)
    disp2_to_core2 = ThreadSafeQueue(disp_regs2)
    _thread.start_new_thread(core_2, (disp1_to_core2, disp2_to_core2))
    asyncio.create_task(read_adc(1, 3, disp1_to_core2, disp2_to_core2))
    
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
