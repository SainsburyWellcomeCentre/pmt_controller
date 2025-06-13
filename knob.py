from driver.encoder import Encoder
from driver.debounce import DebouncedInput
from machine import Pin


class Knob(Encoder):
    def __init__(self, pin_a: int, pin_sw: int, debounce_ms=10):
        super().__init__(4, Pin(pin_a))
        self.click = DebouncedInput(pin_sw, Pin.IRQ_FALLING, debounce_ms)
