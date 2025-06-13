from machine import Pin, Timer
import micropython
from array import array
import rp2


# Closure enables Viper to retain state. Currently (V1.17) nonlocal doesn't
# work: https://github.com/micropython/micropython/issues/8086
# so using arrays.
def make_isr(pos):
    old_x = array("i", (0,))

    @micropython.viper
    def isr(sm):
        i = ptr32(pos)
        p = ptr32(old_x)
        while sm.rx_fifo():
            v: int = int(sm.get()) & 3
            x: int = v & 1
            y: int = v >> 1
            s: int = 1 if (x ^ y) else -1
            i[1] *= i[2]
            sc: int = 20 if (i[1] > 63) else 1
            i[0] = i[0] + ((s if (x ^ p[0]) else (0 - s)) * sc)
            i[1] = i[1] + 1
            p[0] = x

    return isr


# Args:
# StateMachine no. (0-7): each instance must have a different sm_no.
# An initialised input Pin: this and the next pin are the encoder interface.
# Pins must have pullups (internal or, preferably, low value 1KΩ to 3.3V).
class Encoder:
    def __init__(self, sm_no, base_pin):
        self._pos = array("i", (0, 0, 0))  # [pos]
        self.sm = rp2.StateMachine(sm_no, self.pio_quadrature, in_base=Pin(base_pin))
        self.sm.irq(make_isr(self._pos))  # Instantiate the closure
        self.sm.exec("set(y, 99)")  # Initialise y: guarantee different to the input
        self._timer = Timer(-1)
        self._timer.init(mode=Timer.PERIODIC, period=3000, callback=self.ct_rst)
        self.tmp_val = 0

    def enable(self):
        self.sm.active(1)

    def disable(self):
        self.sm.active(0)

    @property
    def boost(self):
        return self._pos[2] > 0

    @boost.setter
    def boost(self, value: bool):
        self._pos[2] = value

    @rp2.asm_pio()
    def pio_quadrature(in_init=rp2.PIO.IN_LOW):
        wrap_target()
        label("again")
        in_(pins, 2)
        mov(x, isr)
        jmp(x_not_y, "push_data")
        mov(isr, null)
        jmp("again")
        label("push_data")
        push()
        irq(block, rel(0))
        mov(y, x)
        wrap()

    @property
    def value(self):
        # if self._pos[1] > 47:
        #     self._pos[0] = round(self._pos[0], -1)
        return self._pos[0] // 2

    @value.setter
    def value(self, value):
        self._pos[0] = value

    def ct_rst(self, timer):
        if abs(self.tmp_val - self._pos[1]) < 15:
            self._pos[1] = 0
            self._timer.init(mode=Timer.PERIODIC, period=3000, callback=self.ct_rst)
        else:
            self._timer.init(mode=Timer.PERIODIC, period=100, callback=self.ct_rst)
        self.tmp_val = self._pos[1]
