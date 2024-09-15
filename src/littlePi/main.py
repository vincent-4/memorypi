import time
import machine
from picographics import PicoGraphics, DISPLAY_INKY_PACK
from pimoroni import Button
import json
from phew import server, connect_to_wifi
import _thread

display = PicoGraphics(display=DISPLAY_INKY_PACK)

TEXT_SIZE = 8
TEXT_SCALE = 1
DOUBLE_TEXT_SIZE = 16
DOUBLE_TEXT_SCALE = 2
MSG_TEXT_SIZE = DOUBLE_TEXT_SIZE
MSG_TEXT_SCALE = DOUBLE_TEXT_SCALE
DATE_TEXT_SIZE = TEXT_SIZE
DATE_TEXT_SCALE = TEXT_SCALE
SIGNOFF_TEXT_SIZE = TEXT_SIZE
SIGNOFF_TEXT_SCALE = TEXT_SCALE
LABEL_TEXT_SIZE = TEXT_SIZE
LABEL_TEXT_SCALE = TEXT_SCALE
BORDER_SIZE = 4
SPACING_SIZE = 2
BITMAP_SIZE = 30

BUTTON_1_OFFSET = 18
BUTTON_2_OFFSET = 60
BUTTON_3_OFFSET = 102

WIFI_SSID = "HackMIT.2024"
WIFI_PASS = "H@cker2024"

messages_lock = False
state = 0

def draw_messages(msg, date, signoff, bitmap, page_index, num_pages):
    display.set_pen(15)
    display.clear()
    disp_w, disp_h = display.get_bounds()
    forward_str = "fwd >"
    back_str = "back>"
    menu_str = "menu>"
    menu_pos = disp_w - max(display.measure_text(forward_str, LABEL_TEXT_SCALE), display.measure_text(back_str, LABEL_TEXT_SCALE), display.measure_text(menu_str, LABEL_TEXT_SCALE)) - SPACING_SIZE * 2 - 1
    message_space_w = menu_pos - (BITMAP_SIZE * 3 + SPACING_SIZE * 2)
    page_count = str(page_index + 1) + "/" + str(num_pages)
    page_count_w = display.measure_text(page_count, TEXT_SCALE)
    date_w = display.measure_text(date, DATE_TEXT_SCALE)
    msg_w = display.measure_text(msg, MSG_TEXT_SCALE)
    signoff_w = display.measure_text('-'+signoff, SIGNOFF_TEXT_SCALE)
    
    display.set_pen(0)
    display
    display.set_font("bitmap8")

    # menu
    display.line(menu_pos + SPACING_SIZE - BORDER_SIZE//2, BORDER_SIZE, menu_pos + SPACING_SIZE - BORDER_SIZE//2, disp_h - BORDER_SIZE)
    display.text(forward_str, menu_pos + SPACING_SIZE * 2 + 1, BUTTON_1_OFFSET, scale = LABEL_TEXT_SCALE)
    display.text(back_str, menu_pos + SPACING_SIZE * 2 + 1, BUTTON_2_OFFSET, scale = LABEL_TEXT_SCALE)
    display.text(menu_str, menu_pos + SPACING_SIZE * 2 + 1, BUTTON_3_OFFSET, scale = LABEL_TEXT_SCALE)
    # date & page count
    display.text(page_count, BORDER_SIZE, BORDER_SIZE, scale = TEXT_SCALE)
    display.line(BORDER_SIZE + page_count_w + SPACING_SIZE, BORDER_SIZE+DATE_TEXT_SIZE//2, menu_pos-BORDER_SIZE-date_w-SPACING_SIZE, BORDER_SIZE+DATE_TEXT_SIZE//2)
    display.text(date, menu_pos-BORDER_SIZE-date_w, BORDER_SIZE, scale = DATE_TEXT_SCALE)
    # msg
    msg_index = 0
    line_count = 0
    buffer = ""
    while msg_index < len(msg):
        if display.measure_text(buffer + msg[msg_index], MSG_TEXT_SCALE) > message_space_w - BORDER_SIZE * 2:
            display.text(buffer, BORDER_SIZE, BORDER_SIZE+DATE_TEXT_SIZE+SPACING_SIZE+(MSG_TEXT_SIZE+SPACING_SIZE)*line_count, scale = MSG_TEXT_SCALE)
            buffer = ""
            line_count += 1
        buffer += msg[msg_index]
        msg_index += 1
    display.text(buffer, BORDER_SIZE, BORDER_SIZE+DATE_TEXT_SIZE+SPACING_SIZE+(MSG_TEXT_SIZE+SPACING_SIZE)*line_count, scale = MSG_TEXT_SCALE)
    # bitmap
    x_loc = message_space_w + SPACING_SIZE
    y_loc = BORDER_SIZE+DATE_TEXT_SIZE+SPACING_SIZE
    x = 0
    y = 0
    while y < BITMAP_SIZE:
        while x < BITMAP_SIZE:
            display.set_pen((not bitmap[x + y * BITMAP_SIZE]) * 15)
            display.rectangle(x_loc + x * 3, y_loc + y * 3, 3, 3)
            x += 1
        x = 0
        y += 1
    display.set_pen(0)
    # signoff
    display.text('-'+signoff, menu_pos -BORDER_SIZE-signoff_w, disp_h-BORDER_SIZE-SIGNOFF_TEXT_SIZE, scale = SIGNOFF_TEXT_SCALE)
    display.update()

def run_messages_screen():
    global messages_lock
    messages = []
    while messages_lock:
        time.sleep(0.1)
    messages_lock = True
    with open("messages.json") as f:
        messages = json.loads(f.read())["messages"]
    messages_lock = False
    curr_msg = 0
    draw_messages(messages[curr_msg]["message"], messages[curr_msg]["date"], messages[curr_msg]["signoff"], messages[curr_msg]["bitmap"], curr_msg, len(messages))
    forward_button = Button(12)
    back_button = Button(13)
    menu_button = Button(14)
    while True:
        if forward_button.read():
            curr_msg = (curr_msg + 1) % len(messages)
            draw_messages(messages[curr_msg]["message"], messages[curr_msg]["date"], messages[curr_msg]["signoff"], messages[curr_msg]["bitmap"], curr_msg, len(messages))
        elif back_button.read():
            curr_msg = (curr_msg - 1) % len(messages)
            draw_messages(messages[curr_msg]["message"], messages[curr_msg]["date"], messages[curr_msg]["signoff"], messages[curr_msg]["bitmap"], curr_msg, len(messages))
        elif menu_button.read():
            return 0

states = ["messages screen", "test option", "other option"]
def draw_main_menu(curr_state):
    display.set_pen(15)
    display.clear()
    disp_w, disp_h = display.get_bounds()
    up_str = "up >"
    down_str = "dwn>"
    select_str = "sel>"
    message_space_w = disp_w - max(display.measure_text(up_str, LABEL_TEXT_SCALE), display.measure_text(down_str, LABEL_TEXT_SCALE), display.measure_text(select_str, LABEL_TEXT_SCALE)) - SPACING_SIZE * 2 - 1
    # option display
    offset = 0
    for state_index in range(len(states)):
        if state_index == curr_state:
            display.set_pen(0)
            display.rectangle(BORDER_SIZE, BORDER_SIZE + offset, display.measure_text(states[state_index], DOUBLE_TEXT_SCALE) + SPACING_SIZE * 2, DOUBLE_TEXT_SIZE + SPACING_SIZE * 2)
            display.set_pen(15)
            display.text(states[state_index], BORDER_SIZE + SPACING_SIZE, BORDER_SIZE + SPACING_SIZE + offset, scale = DOUBLE_TEXT_SCALE)
        else:
            display.set_pen(0)
            display.text(states[state_index], BORDER_SIZE + SPACING_SIZE, BORDER_SIZE + SPACING_SIZE + offset, scale = DOUBLE_TEXT_SCALE)
        offset += DOUBLE_TEXT_SIZE + SPACING_SIZE * 2
    # menu
    display.line(message_space_w + SPACING_SIZE - BORDER_SIZE//2, BORDER_SIZE, message_space_w + SPACING_SIZE - BORDER_SIZE//2, disp_h - BORDER_SIZE)
    display.text(up_str, message_space_w + SPACING_SIZE * 2 + 1, BUTTON_1_OFFSET, scale = LABEL_TEXT_SCALE)
    display.text(down_str, message_space_w + SPACING_SIZE * 2 + 1, BUTTON_2_OFFSET, scale = LABEL_TEXT_SCALE)
    display.text(select_str, message_space_w + SPACING_SIZE * 2 + 1, BUTTON_3_OFFSET, scale = LABEL_TEXT_SCALE)
    
    display.update()

def run_main_menu():
    new_state = 0
    draw_main_menu(new_state)
    up_button = Button(12)
    down_button = Button(13)
    select_button = Button(14)
    count = 0
    while True:
        if up_button.read():
            new_state = (new_state - 1) % len(states)
            draw_main_menu(new_state)
            print(str(count) + " " + str(new_state))
        elif down_button.read():
            new_state = (new_state + 1) % len(states)
            draw_main_menu(new_state)
            print(str(count) + " " + str(new_state))
        elif select_button.read():
            print("sel " + str(new_state))
            return new_state + 1
        count += 1


def main():
    state = 1
    response = None
    while response == None:
        response = connect_to_wifi(WIFI_SSID, WIFI_PASS)
        print(response)
    
    @server.route("/messages?json=<json_string>", methods=["POST"])
    def refresh_messages(json_string):
        global messages_lock
        while messages_lock:
            time.sleep(0.1)
        messages_lock = True
        with open("messages.json", "w") as f:
            f.write(json_string)
        messages_lock = False
    
    @server.catchall()
    def catchall(request):
        return "Not found", 404
        
    _thread.start_new_thread(server.run, ())
    
    while True:
        if state == 0:
            state = run_main_menu()
        elif state == 1:
            state = run_messages_screen()
        else:
            state = 0
    
main()
