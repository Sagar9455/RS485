import json
import logging
import can
import isotp
import os
from udsoncan.client import Client
from udsoncan.connections import PythonIsoTpConnection
import udsoncan.configs
import time
import RPi.GPIO as GPIO
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Define button pins
BTN_FIRST = 12
BTN_SECOND = 16
BTN_ENTER = 20
BTN_THANKS = 21
buttons = [BTN_FIRST, BTN_SECOND, BTN_ENTER, BTN_THANKS]

# Set up buttons as input with pull-up resistors
for btn in buttons:
    GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize I2C and OLED
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

time.sleep(0.5)  # Added delay for OLED stability

# Load font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 9)

# Menu combinations
menu_combinations = {
    (BTN_FIRST, BTN_ENTER): "ECU Information",
    (BTN_SECOND, BTN_ENTER): "Testcase Execution",
    (BTN_FIRST, BTN_SECOND, BTN_ENTER): "ECU Flashing",
    (BTN_SECOND, BTN_FIRST, BTN_ENTER): "File Transfer\ncopying log files\nto USB device",
    (BTN_FIRST, BTN_FIRST, BTN_ENTER): "Reserved1\nfor future versions",
    (BTN_SECOND, BTN_SECOND, BTN_ENTER): "Reserved2\nfor future versions"
}
selected_sequence = []

# Load configuration from JSON
with open('config.json') as config_file:
    config_data = json.load(config_file)

# Extract configuration
def setup_can_interface(interface):
    if os.system(f'ip link show {interface} > /dev/null 2>&1') == 0:
        logging.info(f"{interface} is already active")
    else:
        os.system(f'sudo ip link set {interface} up type can bitrate 500000 dbitrate 1000000 restart-ms 1000 berr-reporting on fd on')

def get_ecu_information():
    setup_can_interface(config_data["can_interface"])

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
    bus = can.interface.Bus(channel=config_data["can_interface"], bustype="socketcan", fd=True)
    bus.set_filters([{"can_id": int(config_data["can_ids"]["rx_id"], 16), "can_mask": 0xFFF}])

    tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, 
                            txid=int(config_data["can_ids"]["tx_id"], 16),
                            rxid=int(config_data["can_ids"]["rx_id"], 16))

    stack = isotp.CanStack(bus=bus, address=tp_addr, params=config_data["isotp_params"])
    conn = PythonIsoTpConnection(stack)

    config = dict(udsoncan.configs.default_client_config)
    config["ignore_server_timing_requirements"] = config_data["uds_config"]["ignore_server_timing_requirements"]
    config["data_identifiers"] = {
        int(key, 16): udsoncan.AsciiCodec(value)
        for key, value in config_data["uds_config"]["data_identifiers"].items()
    }

    with Client(conn, request_timeout=2, config=config) as client:
        logging.info("UDS Client Started")

        try:
            client.tester_present()
            logging.info("Tester Present sent successfully")
        except Exception as e:
            logging.warning(f"Tester Present failed: {e}")

        change_session_with_retry(client, 0x01)
        change_session_with_retry(client, 0x03)

        for did in config["data_identifiers"]:
            try:
                response = client.read_data_by_identifier(did)
                if response.positive:
                    logging.info(f"ECU information (DID {hex(did)}): {response.service_data.values[did]}")
                else:
                    logging.warning(f"Failed to read ECU information (DID {hex(did)})")
            except Exception as e:
                logging.error(f"Error reading ECU information (DID {hex(did)}): {e}")

        logging.info("UDS Client Closed")

def change_session_with_retry(client, session_type, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.change_session(session_type)
            if response.positive:
                logging.info(f"Switched to session {session_type} successfully")
                return
            else:
                logging.warning(f"Attempt {attempt + 1}: Failed to switch to session {session_type}")
        except Exception as e:
            logging.error(f"Attempt {attempt + 1}: Error in session {session_type} - {e}")
        time.sleep(0.5)

variable = 0
varFinal = 0
try:
    while True:
        if GPIO.input(BTN_FIRST) == GPIO.LOW:
            time.sleep(0.2)
            variable = (variable * 10) + 1
            selected_sequence.append(BTN_FIRST)

        if GPIO.input(BTN_SECOND) == GPIO.LOW:
            time.sleep(0.2)
            variable = (variable * 10) + 2
            selected_sequence.append(BTN_SECOND)

        if GPIO.input(BTN_ENTER) == GPIO.LOW:
            varFinal = variable
            variable = 0
            selected_sequence.append(BTN_ENTER)

            selected_option = menu_combinations.get(tuple(selected_sequence), "Invalid Input")

            if selected_option == "ECU Information":
                time.sleep(0.5)
                get_ecu_information()

            if selected_option == "Exit":
                os.system("exit")

            selected_sequence.clear()

        if GPIO.input(BTN_THANKS) == GPIO.LOW:
            time.sleep(0.1)
            os.system('sudo poweroff')

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.cleanup()
