import uasyncio as asyncio
from threadsafe import ThreadSafeQueue
import _thread
from time import sleep_ms
from pmt_display import PmtDisplay
from machine import ADC, Pin

disp_regs = {
    'status': (False, False),
    'voltage': (0000, False),
    'set_voltage': (False, 0000, 0),
    'interlock': (False, 0000),
    'set_interlock': (False, 0000, 0),
    'mode': (False, 0)
}

def core_2(getq, putq):  # Run on core 2
    display1 = PmtDisplay(cs=13, dc=11, sck=14, mosi=15, bl=20)
    display2 = PmtDisplay(cs=17, dc=16, sck=18, mosi=19, bl=12)
    
    display1.set_background()
    display1.regs['voltage'] = (True, 1234, True)
    display1.regs['status'] = (True, True)
    display1.regs['mode'] = (True, 2)
    display1.update()
    
    display2.set_background()
    display2.regs['voltage'] = (True, 1234, True)
    display2.regs['status'] = (True, True)
    display2.regs['mode'] = (True, 2)
    display2.update()
    
    while True:
        display1.regs = getq.get_sync(block=True)
        display1.update()

async def read_adc(channel, period_ms, q):
    while True:
        adc = ADC(Pin(26+channel))
        reading = min(adc.read_u16()>>3, 4095)        
        disp_regs['voltage'] = (True, reading, True)
        try:
            q.put_sync(disp_regs)
        except IndexError:
            pass
            # Queue is full
            
        await asyncio.sleep_ms(period_ms)       

async def main():
    to_core2 = ThreadSafeQueue(disp_regs)
    from_core2 = ThreadSafeQueue(disp_regs)
    _thread.start_new_thread(core_2, (to_core2, from_core2))
    asyncio.create_task(read_adc(1, 3, to_core2))
    
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
