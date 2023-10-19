from machine import Pin
import uasyncio as asyncio
from primitives import Pushbutton

btn = Pin(1, Pin.IN, Pin.PULL_UP)	#GP1 = Enc 2, GP7 = Enc 1
pb = Pushbutton(btn, suppress=True)

async def main():
    short_press = pb.release_func(print, ("SHORT",))
    double_press = pb.double_func(print, ("DOUBLE",))
    long_press = pb.long_func(print, ("LONG",))
    while True:
        await asyncio.sleep(1)

asyncio.run(main())