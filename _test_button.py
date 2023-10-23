from machine import Pin
import uasyncio as asyncio
from primitives import Pushbutton

btn = Pin(7, Pin.IN, Pin.PULL_UP)	#GP1 = Enc 2, GP7 = Enc 1
pb = Pushbutton(btn, suppress=True)

def _short_press():
    print("SHORT")

def _double_press():
    print("DOUBLE")
    
def _long_press():
    print("LONG")

async def main():
    short_press = pb.release_func(_short_press, ())
    double_press = pb.double_func(_double_press, ())
    long_press = pb.long_func(_long_press, ())
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
