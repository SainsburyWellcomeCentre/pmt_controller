import uasyncio as asyncio
from machine import ADC, Pin
from primitives import AADC
from rotary_irq_rp2 import RotaryIRQ

pico_pwm_mode = Pin(23, Pin.OUT)
pico_pwm_mode.on()

aadc1 = AADC(ADC(Pin(26)))
aadc2 = AADC(ADC(Pin(27)))

async def foo1():
    while True:
        value = await aadc1(100)  # Trigger if value changes by 2000
        print('adc1',value)

async def foo2():
    while True:
        value = await aadc2(80)  # Trigger if value changes by 2000
        print('adc2',value)

#async def main():
#    foo1_task = asyncio.create_task(foo1())
#    foo2_task = asyncio.create_task(foo2())
#    while True:
#        await asyncio.sleep(0)

#asyncio.run(main())


class Application2():
    def __init__(self, r1, r2):
        self.r1 = r1
        self.r2 = r2
        self.myevent = asyncio.Event()
        asyncio.create_task(self.action())
        r1.add_listener(self.callback)
        r2.add_listener(self.callback)

    def callback(self):
        self.myevent.set()

    async def action(self):
        while True:
            await self.myevent.wait()
            print('App 2:  rotary 1 = {}, button 1 = {}, rotary 2 = {}, button 2 = {}'. format(
                self.r1.value(),self.r1.button(), self.r2.value(), self.r2.button()))
            # do something with the encoder results ...
            self.myevent.clear()


async def main():
    rotary_encoder_1 = RotaryIRQ(pin_num_clk=2,
                                 pin_num_dt=3,
                                 pin_num_bt=1,
                                 min_val=0,
                                 max_val=5,
                                 reverse=True,
                                 range_mode=RotaryIRQ.RANGE_WRAP)

    rotary_encoder_2 = RotaryIRQ(pin_num_clk=8,
                                 pin_num_dt=9,
                                 pin_num_bt=7,
                                 min_val=0,
                                 max_val=20,
                                 reverse=True,
                                 range_mode=RotaryIRQ.RANGE_WRAP)

    # create tasks that use the rotary encoders
#    app1 = Application1(rotary_encoder_1)
    app2 = Application2(rotary_encoder_1, rotary_encoder_2)
    foo1_task = asyncio.create_task(foo1())
    foo2_task = asyncio.create_task(foo2())

    # keep the event loop active
    while True:
        await asyncio.sleep_ms(10)

try:
    asyncio.run(main())
except (KeyboardInterrupt, Exception) as e:
    print('Exception {} {}\n'.format(type(e).__name__, e))
finally:
    ret = asyncio.new_event_loop()  # Clear retained uasyncio state