import time
from config import lcd, device, knob


def main():
    last_knob = knob.value
    while True:
        t_now = time.ticks_ms()

        knob_diff = knob.value - last_knob
        last_knob = knob.value

        device.mode_update()

        knob.boost = device.mode is device.MODE_SELECT  # to boost the knob sensitivity in select mode

        if device.mode == device.MODE_LOCK:
            break

        else:
            device.value_update(knob_diff)

        # display
        display()

        # print("Time taken: ", time.ticks_diff(time.ticks_ms(), t_now))
        # print("FPS: ", 1000 // time.ticks_diff(time.ticks_ms(), t_now))
        # print("device mode: ", device.mode)
        # for pmt in device.PMTs:
        #     print(f"PMT {pmt.channel} - Mode: {pmt.mode}, Value: {pmt.value}, Selected: {pmt.isSelected}, Highlighted: {pmt.isHighlighted}, ValueChanged: {pmt.isValueChanged}")


def display():
    lcd.cs = lcd.css
    lcd.show_brightness(device.brightness.read_u16())
    for idx, pmt in enumerate(device.PMTs):
        lcd.cs = [lcd.css[idx]]

        if pmt.isModeChanged:
            pmt.isModeChanged = False
            lcd.show_mode(pmt.MODE_STRING[pmt.mode])
            if pmt.mode == pmt.MODE_OFF:
                pmt.isValueChanged = False
                lcd.show_value()

        if pmt.isValueChanged and (pmt.mode is not pmt.MODE_OFF):
            pmt.isValueChanged = False
            color = 0x00FF if pmt.isSelected else 0xFFFF
            lcd.show_value(pmt.value, color)

        color = 0xFD7F if pmt.isHighlighted else 0
        lcd.show_border(color)


def menu():
    lcd.show_menu_a()
    lcd.show_menu_b()


def test_main():
    lcd.opening()

    knob.enable()
    knob.click.callback = knob_callback

    device.highlighted_update()
    menu()
    time.sleep_ms(100)


def knob_callback(pin=None):
    if device.highlightedPMT:
        if device.highlightedPMT.isSelected:
            device.highlightedPMT.isSelected = False
            device.mode = device.MODE_NORMAL
        else:
            device.highlightedPMT.isSelected = True
            device.mode = device.MODE_SELECT
        device.highlightedPMT.isValueChanged = True


test_main()
