from driver.st7735 import ST7735
from machine import SPI, Pin, PWM
from font.microfont import MicroFont
import framebuf
import time


class LCD(ST7735):
    def __init__(self, css: list[Pin], width: int, height: int, spi: SPI, dc: Pin, bl: PWM, init_colour=0x0):
        super().__init__(width, height, spi, css, dc, bl, init_colour)
        self.css = css
        self.cs = css
        self.font_s = MicroFont("font/victor_R_24.mfnt", cache_index=True)
        self.font_ss = MicroFont("font/victor_R_15.mfnt", cache_index=True)
        # self.font_m = MicroFont("font/victor_B_32.mfnt", cache_index=True)
        # self.font_l = MicroFont("font/victor_B_70.mfnt", cache_index=True)

        self.font_h = 24

    def show_mode(self, string, color=0xFFFF):
        buf = self.font_s.write(string, framebuf.RGB565, 80, self.font_h, 0, 0, 0xFFFF)
        self.show_region(40, 120, 10, 10 + self.font_h, buf)

    def show_value(self, val=-1, color=0xFFFF):
        if val < 0:
            word = "     "
        elif val < 10:
            word = "00" + str(val)
        elif val < 100:
            word = "0" + str(val)
        else:
            word = str(val)
        buf = self.font_s.write(word, framebuf.RGB565, 80, self.font_h, 0, 0, color)
        self.show_region(40, 120, 40, 40 + self.font_h, buf)

    def show_border(self, color=0x0000):
        color_2btye = [color >> 8, color & 0xFF]
        buf_h = bytearray(color_2btye * 160 * 3)
        buf_v = bytearray(color_2btye * 128 * 3)
        self.show_region(0, 159, 0, 2, buf_h)
        self.show_region(0, 159, 124, 127, buf_h)
        self.show_region(0, 3, 0, 127, buf_v)
        self.show_region(156, 159, 0, 127, buf_v)

    def show_brightness(self, val, color=0xFFFF):
        # buf = self.font_ss.write("Brtnss:" + str(val) + "(cd/m2)", framebuf.RGB565, 140, 15, 0, 0, color)
        buf = self.font_ss.write(str(val), framebuf.RGB565, 140, 15, 0, 0, color)
        self.show_region(10, 150, 105, 105 + 15, buf)

    def show_pmt_type(self, string, color=0xFFFF):
        buf = self.font_ss.write("PMT type:" + string, framebuf.RGB565, 140, 15, 0, 0, color)
        self.show_region(10, 150, 85, 85 + 15, buf)

    def opening(self):
        buf = bytearray([0xFF, 0x00] * 120 * 88)
        self.show_region(20, 140, 20, 108, buf)
        buf = bytearray(120 * 2)
        for i in range(88 // 2):
            self.show_region(20, 140, 20 + i, 20 + i + 1, buf)
            self.show_region(20, 140, 108 - i - 1, 108 - i, buf)
            time.sleep_ms(20)