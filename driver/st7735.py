import framebuf
from time import sleep_ms, sleep_us
from machine import SPI, Pin, PWM


SWRESET = 0x01  # Software Reset
RDDID = 0x04  # Read Display ID
RDDST = 0x09  # Read Display Status
RDDPM = 0x0A  # Read Display Power Mode
RDDMADCTL = 0x0B  # Read Display MADCTL
RDDCOLMOD = 0x0C  # Read Display Pixel Format
RDDIM = 0x0D  # Read Display Image Mode
RDDSM = 0x0E  # Read Display Signal Mode
RDDSDR = 0x0F  # Read Display Self-Diagnostic Result
SLPIN = 0x10  # Sleep In
SLPOUT = 0x11  # Sleep Out
PTLON = 0x12  # Partial Display Mode On
NORON = 0x13  # Normal Display Mode On
INVOFF = 0x20  # Display Inversion Off
INVON = 0x21  # Display Inversion On
GAMSET = 0x26  # Gamma Set
DISPOFF = 0x28  # Display Off
DISPON = 0x29  # Display On
CASET = 0x2A  # Column Address Set
RASET = 0x2B  # Row Address Set
RAMWR = 0x2C  # Memory Write
RGBSET = 0x2D  # Color Setting 4k, 65k, 262k
RAMRD = 0x2E  # Memory Read
PTLAR = 0x30  # Partial Area
SCRLAR = 0x33  # Scroll Area Set
TEOFF = 0x34  # Tearing Effect Line OFF
TEON = 0x35  # Tearing Effect Line ON
MADCTL = 0x36  # Memory Data Access Control
VSCSAD = 0x37  # Vertical Scroll Start Address of RAM
IDMOFF = 0x38  # Idle Mode Off
IDMON = 0x39  # Idle Mode On
COLMOD = 0x3A  # Interface Pixel Format
FRMCTR1 = 0xB1  # Frame Rate Control in normal mode, full colors
FRMCTR2 = 0xB2  # Frame Rate Control in idle mode, 8 colors
FRMCTR3 = 0xB3  # Frame Rate Control in partial mode, full colors
INVCTR = 0xB4  # Display Inversion Control
PWCTR1 = 0xC0  # Power Control 1
PWCTR2 = 0xC1  # Power Control 2
PWCTR3 = 0xC2  # Power Control 3 in normal mode, full colors
PWCTR4 = 0xC3  # Power Control 4 in idle mode 8colors
PWCTR5 = 0xC4  # Power Control 5 in partial mode, full colors
VMCTR1 = 0xC5  # VCOM Control 1
VMOFCTR = 0xC7  # VCOM Offset Control
GMCTRP1 = 0xE0  # Gamma '+'Polarity Correction Characteristics Setting
GMCTRN1 = 0xE1  # Gamma '-'Polarity Correction Characteristics Setting
GCV = 0xFC  # Gate Pump Clock Frequency Variable */


@micropython.viper
def byteswap(data: ptr8, length: int):
    i = 0
    while i < length:
        temp = data[i]
        data[i] = data[i + 1]
        data[i + 1] = temp
        i += 2


class ST7735(framebuf.FrameBuffer):
    def __init__(self, width: int, height: int, spi: SPI, cs, dc: Pin, bl: PWM, init_colour=0x0):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.width = width
        self.height = height
        self.bl = bl
        self.brightness = 0
        self.buffer = bytearray(width * height * 2)  # 2 bytes needed for every pixel (RGB565 format)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        self.fill(init_colour)
        self.show()
        self.backlight_on()  # Turn backlight on

    def init_display(self):

        self.write_cmd(SWRESET)  # software reset
        sleep_us(150)
        self.write_cmd(SLPOUT)  # sleep out, turn off sleep mode
        sleep_ms(1)
        self.write_cmd(DISPOFF)  # output from frame mem disabled
        sleep_ms(10)

        self.write_reg(FRMCTR1, [0x01, 0x2C, 0x2D])  # frame frequency normal mode (highest frame rate in normal mode)
        self.write_reg(FRMCTR2, [0x01, 0x2C, 0x2D])  # frame frequency idle mode */
        self.write_reg(
            FRMCTR3, [0x01, 0x2C, 0x2D, 0x01, 0x2C, 0x2D]
        )  # frame freq partial mode: 1-3 dot inv, 4-6 col inv */
        self.write_reg(INVCTR, [0x07])  # display inversion control: 3-bit 0=dot, 1=col */

        self.write_reg(PWCTR1, [0xA2, 0x02, 0x84])  # power control */
        self.write_reg(PWCTR2, [0xC5])
        self.write_reg(PWCTR3, [0x0A, 0x00])
        self.write_reg(PWCTR4, [0x8A, 0x2A])
        self.write_reg(PWCTR5, [0x8A, 0xEE])  # partial mode power control */
        self.write_reg(VMCTR1, [0x0E])  # VCOM voltage setting */

        self.write_cmd(INVOFF)

        self.write_reg(VMOFCTR, [0x10])  # ligthness of black color 0-0x1f */
        self.write_reg(GAMSET, 0x08)  # gamma 1, 2, 4, 8 */

        self.write_reg(MADCTL, [0x60])  # row oder, col order, row colum xchange
        self.write_reg(COLMOD, [0x05])  # 3=12bit, 5=16-bit, 6=18-bit  pixel color mode */

        self.write_reg(
            GMCTRP1, [0x04, 0x22, 0x07, 0x0A, 0x2E, 0x30, 0x25, 0x2A, 0x28, 0x26, 0x2E, 0x3A, 0x00, 0x01, 0x03, 0x13]
        )
        self.write_reg(
            GMCTRN1, [0x04, 0x16, 0x06, 0x0D, 0x2D, 0x26, 0x23, 0x27, 0x27, 0x25, 0x2D, 0x3B, 0x00, 0x01, 0x04, 0x13]
        )

        self.write_reg(CASET, [0, 0, 0, self.width - 1])
        self.write_reg(RASET, [0, 0, 0, self.height - 1])

        self.write_cmd(DISPON)  # recover from display off, output from frame mem enabled */
        self.write_cmd(NORON)  # normal display mode on */

    def show(self):
        self.show_region(0, self.width, 0, self.height, self.buffer)

    def show_region(self, x_min, x_max, y_min, y_max, buf):
        x_max -= 1
        y_max -= 1

        x_offset = 1
        y_offset = 2

        self.write_reg(CASET, [x_min >> 8, (x_min + x_offset) & 0xFF, x_max >> 8, (x_max + x_offset) & 0xFF])
        self.write_reg(RASET, [y_min >> 8, (y_min + y_offset) & 0xFF, y_max >> 8, (y_max + y_offset) & 0xFF])

        self.write_cmd(RAMWR)
        self.dc(1)
        self.cs_low()
        self.spi.write(buf)
        self.cs_high()

    def backlight_on(self):
        self.brightness = 65535

    @property
    def brightness(self):
        return self.brightness

    @brightness.setter
    def brightness(self, value):
        self.bl.duty_u16(value)

    def backlight_off(self):
        self.brightness = 0

    def load_img_file(self, filepath, startX, startY, width, height, a=-1):
        with open(filepath, "rb") as f:
            f.read(72)  # header
            for y in range(height - 1, 0, -1):
                buf = bytearray(f.read(width * 2))
                byteswap(buf, len(buf))
                tmp_buf = framebuf.FrameBuffer(buf, width, 1, framebuf.RGB565)
                self.blit(tmp_buf, startX, startY + y, a)

    def write_cmd(self, cmd):
        self.dc(0)
        self.cs_low()
        self.spi.write(bytearray([cmd]))
        self.cs_high()

    def write_data(self, data):
        self.dc(1)
        self.cs_low()
        self.spi.write(bytearray(data))
        self.cs_high()

    def write_reg(self, reg, data):
        self.write_cmd(reg)
        self.write_data(data)

    def cs_low(self):
        if type(self.cs) is list:
            for cs in self.cs:
                cs(0)
        else:
            self.cs(0)

    def cs_high(self):
        if type(self.cs) == list:
            for cs in self.cs:
                cs(1)
        else:
            self.cs(1)
