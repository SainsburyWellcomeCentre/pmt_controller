import uasyncio as asyncio
from primitives import Switch
from machine import Pin

enable_15V = Pin(21, Pin.OUT)	#GP22 = Enc 2, GP21 = Enc 1
enable_15V.off()

async def foo1(evt):
    while True:
        evt.clear()  # re-enable the event
        await evt.wait()  # minimal resources used while paused
        print("15V On.")
        enable_15V.on()
        # Omitted code runs each time the switch closes

async def foo2(evt):
    while True:
        evt.clear()  # re-enable the event
        await evt.wait()  # minimal resources used while paused
        print("15V Off.")
        enable_15V.off()
        # Omitted code runs each time the switch closes

async def main():
    sw = Switch(Pin(10, Pin.IN))	#GP6 = Enc 2, GP10 = Enc 1
    sw.close_func(None)  # Use event based interface
    sw.open_func(None)
    foo1_task = asyncio.create_task(foo1(sw.close))
    foo2_task = asyncio.create_task(foo2(sw.open))
#    await foo(sw.close)  # Pass the bound event to foo


    # keep the event loop active
    while True:
        await asyncio.sleep_ms(10)

asyncio.run(main())
