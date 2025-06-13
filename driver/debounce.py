from machine import Pin, Timer


class DebouncedInput(Pin):

    def __init__(self, pin_num: int, trigger=Pin.IRQ_RISING, debounce_ms=50):

        pull = Pin.PULL_DOWN if trigger == Pin.IRQ_RISING else Pin.PULL_UP
        super().__init__(pin_num, Pin.IN, pull)
        self.pin_num = pin_num
        self._db_timer = Timer(-1)
        self._debounce_ms = debounce_ms
        self.trigger = trigger
        self.callback = self._doNothing
        self.enable()

    def enable(self):
        self._act_logic = 1 if self.trigger == Pin.IRQ_RISING else 0
        self.irq(self._irqHandler, self.trigger)

    def disable(self):
        self.irq(trigger=0)

    def _DebounceTimerExpired(self, timer=None):
        if self.value() == self._act_logic:
            self.callback(self.pin_num)
        self.enable()

    def _irqHandler(self, pin=None):
        self._db_timer.init(
            mode=Timer.ONE_SHOT,
            period=self._debounce_ms,
            callback=self._DebounceTimerExpired,
        )
        self.disable()

    def _doNothing(self, pin=None):
        return
