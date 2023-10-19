import uasyncio as asyncio
from primitives import Switch
from machine import Pin

async def foo1(evt):
    while True:
        evt.clear()  # re-enable the event
        await evt.wait()  # minimal resources used while paused
        print("Switch closed.")
        # Omitted code runs each time the switch closes

async def foo2(evt):
    while True:
        evt.clear()  # re-enable the event
        await evt.wait()  # minimal resources used while paused
        print("Switch open.")
        # Omitted code runs each time the switch closes

async def main():
    sw = Switch(Pin(6, Pin.IN))	#GP6 = Enc 2, GP10 = Enc 1
    sw.close_func(None)  # Use event based interface
    sw.open_func(None)
    foo1_task = asyncio.create_task(foo1(sw.close))
    foo2_task = asyncio.create_task(foo2(sw.open))
#    await foo(sw.close)  # Pass the bound event to foo


    # keep the event loop active
    while True:
        await asyncio.sleep_ms(10)

asyncio.run(main())