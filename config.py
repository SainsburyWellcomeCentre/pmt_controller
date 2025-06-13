from machine import Pin, SPI, I2C, PWM, ADC
from micropython import const
from driver.ads1115 import ADS1115
from driver.mcp7428 import MCP4728
from driver.dac5571 import DAC5571
from driver.tca9537 import TCA9537

BK_PIN = const(4)
bl = PWM(Pin(BK_PIN), freq=300_000, duty_u16=0)

ENCO_A_PIN = const(0)
ENCO_B_PIN = const(1)
ENCO_BTN_PIN = const(2)

CS1_PIN = const(11)
CS2_PIN = const(10)
CS3_PIN = const(9)
CS4_PIN = const(8)
DC_PIN = const(5)
RST_PIN = const(3)
SCK_PIN = const(6)
STX_PIN = const(7)


SW1_A_PIN = const(14)
SW1_B_PIN = const(15)
SW2_A_PIN = const(13)
SW2_B_PIN = const(12)
SW3_A_PIN = const(19)
SW3_B_PIN = const(18)
SW4_A_PIN = const(17)
SW4_B_PIN = const(16)

I2C_SDA_PIN = const(20)
I2C_SCL_PIN = const(21)

BRIGHTNESS_PIN = const(27)
INTERLOCK_PIN = const(26)

W = const(160)
H = const(128)

from toggle_switch import SPDT
from pmt_controller import PMTController
from pmt import PMT
from display import LCD

SW_1 = SPDT(SW1_A_PIN, SW1_B_PIN)
SW_2 = SPDT(SW2_A_PIN, SW2_B_PIN)
SW_3 = SPDT(SW3_A_PIN, SW3_B_PIN)
SW_4 = SPDT(SW4_A_PIN, SW4_B_PIN)


from knob import Knob

knob = Knob(ENCO_A_PIN, ENCO_BTN_PIN)

dc = Pin(DC_PIN, Pin.OUT)


spi = SPI(0, 31_250_000, sck=Pin(SCK_PIN), mosi=Pin(STX_PIN))
css = [Pin(CS1_PIN, Pin.OUT), Pin(CS2_PIN, Pin.OUT), Pin(CS3_PIN, Pin.OUT), Pin(CS4_PIN, Pin.OUT)]
pmts = [PMT(SW_1), PMT(SW_2), PMT(SW_3), PMT(SW_4)]


lcd = LCD(css, W, H, spi, dc, bl, 0x0)


i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=400_000)
vref = ADS1115(i2c, addr=0x48)
vin = ADS1115(i2c, addr=0x4A)
pmt_en = TCA9537(i2c)
interlock_th = DAC5571(i2c)
vout = MCP4728(i2c)
lock = Pin(INTERLOCK_PIN, Pin.IN)
bright = ADC(BRIGHTNESS_PIN)


device = PMTController(pmts, vin, vref, pmt_en, interlock_th, vout, lock, bright)
