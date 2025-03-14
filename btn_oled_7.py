import time
import RPi.GPIO as GPIO
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import udsoncan
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.client import Client
import udsoncan.configs
import isotp
import can
import logging
import os

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Define button pins
BTN_FIRST = 12  # First button in combination
BTN_SECOND = 16  # Second button in combination
BTN_ENTER = 20  # Confirm selection
BTN_THANKS = 21  # System is shutting down
buttons = [BTN_FIRST, BTN_SECOND, BTN_ENTER, BTN_THANKS]

# Set up buttons as input with pull-up resistors
for btn in buttons:
    GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize I2C and OLED
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

# Load font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)

# Menu options mapped to button sequences
menu_combinations = {
    (BTN_FIRST, BTN_ENTER): "ECU Information",
    (BTN_SECOND, BTN_ENTER): "Testcase Execution",
    (BTN_FIRST, BTN_SECOND, BTN_ENTER): "ECU Flashing",
    (BTN_SECOND, BTN_FIRST, BTN_ENTER): "File Transfer (copying log files into USB device)",
    (BTN_FIRST, BTN_SECOND, BTN_ENTER): "Reserved for future versions",
    (BTN_SECOND, BTN_SECOND, BTN_ENTER): "Reserved for future versions"
}
selected_sequence = []
selected_option = None
last_displayed_text = ""

def display_text(text):
    """Function to display text on OLED only if changed"""
    global last_displayed_text
    if text != last_displayed_text:  # Avoid redundant updates
        oled.fill(0)  # Clear screen
        oled.show()
        
        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)
        draw.text((10, 25), text, font=font, fill=255)
        
        oled.image(image)
        oled.show()
        last_displayed_text = text

def get_ecu_information():
    """Retrieve and display ECU information."""
    os.system('sudo ip link set can0 up type can bitrate 500000 dbitrate 1000000 restart-ms 1000 berr-reporting on fd on')
    os.system('sudo ifconfig can0 up')

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

    isotp_params = {
        'stmin': 32,
        'blocksize': 8,
        'wftmax': 0,
        'tx_data_length': 8, 
        'tx_padding': 0x00,
        'rx_flowcontrol_timeout': 1000,
        'rx_consecutive_frame_timeout': 1000,
        'max_frame_size': 4095,
        'can_fd': True,    
        'bitrate_switch': True
    }

    config = dict(udsoncan.configs.default_client_config)
    config["ignore_server_timing_requirements"] = True
    config["data_identifiers"] = {
        0xF187: udsoncan.AsciiCodec(13),
        0xF1AA: udsoncan.AsciiCodec(7),
        0xF1B1: udsoncan.AsciiCodec(7),
        0xF193: udsoncan.AsciiCodec(7)
    }

    bus = can.interface.Bus(channel="can0", bustype="socketcan", fd=True)
    bus.set_filters([{"can_id": 0x7A8, "can_mask": 0xFFF}])
    tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=0x7A0, rxid=0x7A8)
    stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)
    conn = PythonIsoTpConnection(stack)

    with Client(conn, request_timeout=5, config=config) as client:
        logging.info("UDS Client Started")
        client.tester_present()
        client.change_session(0x01)
        client.change_session(0x03)

        for did in [0xF187, 0xF193, 0xF1AA, 0xF1B1]:
            try:
                response = client.read_data_by_identifier(did)
                if response.positive:
                    logging.info(f"ECU information (DID {hex(did)}): {response.service_data.values[did]}")
            except Exception as e:
                logging.error(f"Error reading ECU information (DID {hex(did)}): {e}")

        logging.info("UDS Client Closed")

try:
    while True:
        if GPIO.input(BTN_FIRST) == GPIO.LOW:
            selected_sequence.append(BTN_FIRST)
            time.sleep(0.3)  # Improved debounce
        
        if GPIO.input(BTN_SECOND) == GPIO.LOW:
            selected_sequence.append(BTN_SECOND)
            time.sleep(0.3)  # Improved debounce
        
        if GPIO.input(BTN_ENTER) == GPIO.LOW:
            selected_sequence.append(BTN_ENTER)
            selected_option = menu_combinations.get(tuple(selected_sequence), "Unknown Option")
            display_text(f"Confirmed: {selected_option}")
            
            if selected_option == "ECU Information":
                get_ecu_information()
            
            selected_sequence.clear()  # Reset sequence after confirmation
            time.sleep(1)
        
        if GPIO.input(BTN_THANKS) == GPIO.LOW:
            display_text("System is shutting down")
            time.sleep(1)
        
        time.sleep(0.1)  # Shorter general debounce delay

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.cleanup()