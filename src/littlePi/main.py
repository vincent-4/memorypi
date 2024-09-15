import time
import machine
from picographics import PicoGraphics, DISPLAY_INKY_PACK
from pimoroni import Button
import json

display = PicoGraphics(display=DISPLAY_INKY_PACK)

bigger_text_size = 16
text_size = 8
msg_text_size = bigger_text_size
date_text_size = text_size
signoff_text_size = text_size
border_size = 4
spacing_size = 2

def message_screen(msg, date, signoff, page_index, num_pages):
    display.set_pen(15)
    display.clear()
    disp_w, disp_h = display.get_bounds()
    forward_str = "fwd >"
    back_str = "back>"
    menu_str = "menu>"
    message_space_w = disp_w - max(display.measure_text(forward_str, 1), display.measure_text(back_str, 1), display.measure_text(menu_str, 1)) - spacing_size * 2 - 1
    page_count = str(page_index + 1) + "/" + str(num_pages)
    page_count_w = display.measure_text(page_count, 1)
    date_w = display.measure_text(date, 1)
    msg_w = display.measure_text(msg, 2)
    signoff_w = display.measure_text('-'+signoff, 1)
    
    display.set_pen(0)
    display
    display.set_font("bitmap8")

    # menu
    display.line(message_space_w + spacing_size - border_size//2, border_size, message_space_w + spacing_size - border_size//2, disp_h - border_size)
    display.text(forward_str, message_space_w + spacing_size * 2 + 1, 18, scale = 1)
    display.text(back_str, message_space_w + spacing_size * 2 + 1, 60, scale = 1)
    display.text(menu_str, message_space_w + spacing_size * 2 + 1, 101, scale = 1)
    # date & page count
    display.text(page_count, border_size, border_size, scale = 1)
    display.line(border_size + page_count_w + spacing_size, border_size+date_text_size//2, message_space_w-border_size-date_w-spacing_size, border_size+date_text_size//2, 1)
    display.text(date, message_space_w-border_size-date_w, border_size, scale = 1)
    # msg
    msg_index = 0
    line_count = 0
    buffer = ""
    while msg_index < len(msg):
        if display.measure_text(buffer + msg[msg_index], 1) > message_space_w - border_size * 2:
            display.text(buffer, border_size, border_size+date_text_size+spacing_size+(msg_text_size+spacing_size)*line_count, scale = 2)
            buffer = ""
            line_count += 1
        buffer += msg[msg_index]
        msg_index += 1
    display.text(buffer, border_size, border_size+date_text_size+spacing_size+(msg_text_size+spacing_size)*line_count, scale = 2)
    # signoff
    display.text('-'+signoff, message_space_w + border_size-signoff_w, disp_h-border_size-signoff_text_size, scale = 1)
    display.update()

def run_messages_screen(state):
    messages = json.loads(open("messages.json").read())["messages"]
    curr_msg = 0
    message_screen(messages[curr_msg]["message"], messages[curr_msg]["date"], messages[curr_msg]["signoff"], curr_msg, len(messages))
    forward_button = Button(12)
    back_button = Button(13)
    menu_button = Button(14)
    while state == 1:
        if forward_button.read():
            curr_msg = (curr_msg + 1) % len(messages)
            message_screen(messages[curr_msg]["message"], messages[curr_msg]["date"], messages[curr_msg]["signoff"], curr_msg, len(messages))
        elif back_button.read():
            curr_msg = (curr_msg - 1) % len(messages)
            message_screen(messages[curr_msg]["message"], messages[curr_msg]["date"], messages[curr_msg]["signoff"], curr_msg, len(messages))
        elif menu_button.read():
            state = 0



def main():
    state = 1
    while True:
        # if state == 0:
        #     # run_main_menu(state)
        #     pass()
        # elif state == 1:
        run_messages_screen(state)
    
main()

# message_screen("Hihi :)", "14/09/2024", "Aidan from the UK")

# led = machine.Pin('LED', machine.Pin.OUT)
# while True:
#     led.toggle()
#     time.sleep(0.5)
