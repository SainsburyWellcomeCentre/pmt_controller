from machine import Pin
from driver.debounce import DebouncedInput


class SPDT:
    def __init__(self, pin_a: int, pin_b: int, debounce_ms=10):

        self.pin_a = DebouncedInput(pin_a, Pin.IRQ_FALLING, debounce_ms)
        self.pin_b = DebouncedInput(pin_b, Pin.IRQ_FALLING, debounce_ms)
        self.pin_a.callback = self.reset
        self.pin_b.callback = self.reset
        self.status = 0
        self.callback = self._doNothing
        self.reset()

    def reset(self, pin=None):

        if self.pin_a.value() == 0:
            self.pin_a.trigger = Pin.IRQ_RISING
            self.pin_a.enable()
            self.pin_b.disable()
            self.status = 2
        elif self.pin_b.value() == 0:
            self.pin_b.trigger = Pin.IRQ_RISING
            self.pin_b.enable()
            self.pin_a.disable()
            self.status = 0
        else:
            self.pin_a.trigger = Pin.IRQ_FALLING
            self.pin_b.trigger = Pin.IRQ_FALLING
            self.pin_a.enable()
            self.pin_b.enable()
            self.status = 1
        self.callback(self.status)

    def _doNothing(self, val=-1):
        return
