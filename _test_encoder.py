# encoder_test.py Test for asynchronous driver for incremental quadrature encoder.

# Copyright (c) 2021-2022 Peter Hinch
# Released under the MIT License (MIT) - see LICENSE file

from machine import Pin
import uasyncio as asyncio
from primitives.encoder import Encoder


px = Pin(8, Pin.IN, Pin.PULL_UP)	#GP2 = Enc 2, GP8 = Enc 1
py = Pin(9, Pin.IN, Pin.PULL_UP)	#GP3 = Enc 2, GP9 = Enc 1

def cb(pos, delta):
    print(pos, delta)

async def main():
    while True:
        await asyncio.sleep(1)

def test():
    print('Running encoder test. Press ctrl-c to teminate.')
    enc = Encoder(px, py, div=4, v=0, vmin=0, vmax=9, wrap=True, callback=cb)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        asyncio.new_event_loop()

test()