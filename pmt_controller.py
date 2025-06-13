from pmt import PMT
from micropython import const
from driver.ads1115 import ADS1115
from driver.tca9537 import TCA9537
from driver.mcp7428 import MCP4728
from driver.dac5571 import DAC5571
from machine import ADC, Pin


class PMTController:

    MODE_NORMAL = const(0)
    MODE_SELECT = const(1)
    MODE_MENU = const(2)
    MODE_LOCK = const(3)

    def __init__(
        self,
        PMTs: list[PMT],
        vin: ADS1115,
        vref: ADS1115,
        en: TCA9537,
        lock_threshold: DAC5571,
        vout: MCP4728,
        interlock: Pin,
        brightness: ADC,
    ):
        self.PMTs = PMTs
        self._highlightedPMT: PMT = None
        self.mode = self.MODE_NORMAL
        self.vin = vin
        self.vref = vref
        self.en = en
        self.lock_threshold = lock_threshold
        self.vout = vout
        self.interlock = interlock
        self.brightness = brightness

        for pmt in self.PMTs:
            pmt.isHighlighted = False
            pmt.isSelected = False
            pmt.isModeChanged = True
            pmt.isValueChanged = True
            pmt.channel = self.PMTs.index(pmt)  # Assign channel based on index

    @property
    def highlightedPMT(self):
        return self._highlightedPMT

    @highlightedPMT.setter
    def highlightedPMT(self, target: PMT):
        for pmt in self.PMTs:
            pmt.isHighlighted = False
        self._highlightedPMT = target
        self._highlightedPMT.isHighlighted = True

    def value_update(self, val):
        self.vin_update()
        if self.mode == self.MODE_NORMAL:
            self._normal_update(val)

        elif self.mode == self.MODE_SELECT:
            self._select_update(val)

        elif self.mode == self.MODE_MENU:
            return

    def vin_update(self):
        # v1 = round(self.vin.read_voltage(0) * 1000)  # read voltage and convert to mV
        # v2 = round(self.vin.read_voltage(1) * 1000)  # read voltage and convert to mV
        # v3 = round(self.vin.read_voltage(2) * 1000)  # read voltage and convert to mV
        # v4 = round(self.vin.read_voltage(3) * 1000)  # read voltage and convert to mV
        # vs = [v1, v2, v3, v4]
        # print(v1, v2, v3, v4)
        for idx, pmt in enumerate(self.PMTs):
            if pmt.mode == pmt.MODE_REMOTE:
                # pmt.value = vs[idx]
                pmt.value = round(self.vin.read_voltage(idx) * 1000)

    def _normal_update(self, val):
        local_ch = [pmt for pmt in self.PMTs if pmt.mode == pmt.MODE_LOCAL]

        if len(local_ch):
            if self._highlightedPMT is None:
                self.highlighted_update()
            else:
                if self.highlightedPMT in local_ch:
                    idx = (local_ch.index(self.highlightedPMT) + val) % len(local_ch)
                    self.highlightedPMT = local_ch[idx]
                else:
                    self.highlightedPMT = local_ch[0]

                self.highlightedPMT.isHighlighted = True

    def _select_update(self, val):
        if self.highlightedPMT and val != 0:
            self.highlightedPMT.value += val

    def highlighted_update(self):
        for pmt in self.PMTs:
            if pmt.mode == pmt.MODE_LOCAL:
                self.highlightedPMT = pmt
                pmt.isHighlighted = True
                break

    def mode_update(self):
        if self.mode is self.MODE_SELECT:
            checked = False
            for pmt in self.PMTs:
                if pmt.isSelected:
                    checked = True
                    break
            if not checked:
                self.mode = self.MODE_NORMAL
