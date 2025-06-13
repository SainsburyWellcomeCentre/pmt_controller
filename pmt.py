from toggle_switch import SPDT
import micropython
from micropython import const


class PMT:

    MODE_STRING = ["off", "local", "remote", "locked"]
    MODE_OFF = const(0)
    MODE_LOCAL = const(1)
    MODE_REMOTE = const(2)
    MODE_LOCKED = const(3)
    MIN_VAL = const(0)
    MAX_VAL = const(5000)

    def __init__(self, switch: SPDT):
        switch.callback = self.sw_callback
        self.mode = switch.status
        self._value = -1
        self.offset = 0
        self.channel = 0
        self.enabled = True
        self.min = PMT.MIN_VAL
        self.max = PMT.MAX_VAL
        self.isSelected = False
        self.isHighlighted = False
        self.isModeChanged = True
        self.isValueChanged = True

    def sw_callback(self, val=-1):
        self.mode = val
        self.isModeChanged = True
        if self.mode is not PMT.MODE_LOCAL:
            self.isSelected = False
            self.isHighlighted = False
        self.value = 0
        self.isValueChanged = True

    @property
    def value(self):
        return self._clamp(self._value)

    @value.setter
    def value(self, val):
        tmp = self._value
        self._value = self._clamp(val)
        self.isValueChanged = tmp != self._value

    @micropython.native
    def _clamp(self, val):
        return max(self.min, min(self.max, val))
