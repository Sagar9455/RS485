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

time.sleep(0.5)  # Added delay for OLED stability

# Load font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 9)

# Menu options mapped to button sequences
menu_combinations = {
    (BTN_FIRST, BTN_ENTER): "ECU Information",
    (BTN_SECOND, BTN_ENTER): "Testcase Execution",
    (BTN_FIRST, BTN_SECOND, BTN_ENTER): "ECU Flashing",
    (BTN_SECOND, BTN_FIRST, BTN_ENTER): "File Transfer\ncopying log files\nto USB device",
    (BTN_FIRST, BTN_FIRST, BTN_ENTER): "Reserved1\nfor future versions",
    (BTN_SECOND, BTN_SECOND, BTN_ENTER): "Reserved2\nfor future versions"
}
selected_sequence = []
selected_option = None
last_displayed_text = ""

def display_text(text):
    """Function to display text on OLED only if changed"""
    global last_displayed_text
    if text != last_displayed_text:
        oled.fill(0)  # Clear screen
        oled.show()
        
        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)
        draw.text((5, 25), text, font=font, fill=255)
        
        oled.image(image)
        oled.show()
        last_displayed_text = text

display_text("Give input")
time.sleep(0.2)

def get_ecu_information():
    """Retrieve and display ECU information."""
    os.system('sudo ip link set can0 up type can bitrate 500000 dbitrate 1000000 restart-ms 1000 berr-reporting on fd on')  # Set bitrate to 500kbps
    os.system('sudo ifconfig can0 up')


    # Logging setup
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
    # Define ISO-TP parameters for CAN FD with 11-bit identifiers
    isotp_params = {
        'stmin': 32,
        'blocksize': 8,
        'wftmax': 0,
        'tx_padding': 0x00,
        'rx_flowcontrol_timeout': 1000,
        'rx_consecutive_frame_timeout': 1000,
        'max_frame_size': 4095,
        'can_fd': True,    
        'bitrate_switch': True# Enable CAN FD mode
    }

    # UDS Client Configuration
    config = dict(udsoncan.configs.default_client_config)
    config["ignore_server_timing_requirements"] = True
    #config["padding_byte"] = 0x00
    config["data_identifiers"] = {
        0xF100: udsoncan.AsciiCodec(8),
        0xF101: udsoncan.AsciiCodec(8),
        0xF187: udsoncan.AsciiCodec(13),
        0xF1AA: udsoncan.AsciiCodec(13),
        0xF1B1: udsoncan.AsciiCodec(13),
        0xF193: udsoncan.AsciiCodec(13),
        0xF120: udsoncan.AsciiCodec(16),
        0xF18B: udsoncan.AsciiCodec(8),
        0xF102: udsoncan.AsciiCodec(13) 
    }

    # Define CAN interface
    interface = "can0"

    # Create CAN bus interface
    bus = can.interface.Bus(channel=interface, bustype="socketcan", fd=True)
    bus.set_filters([{"can_id":0x7A8,"can_mask":0xFFF}])

    # Define ISO-TP addressing for 11-bit CAN IDs
    tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=0x7A0, rxid=0x7A8)

    # Create ISO-TP stack
    stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)

    # Create UDS connection
    conn = PythonIsoTpConnection(stack)

    # Start UDS Client
    with Client(conn, request_timeout=2,config=config) as client:
        logging.info("UDS Client Started")

        # Tester Present (0x3E)
        try:
            client.tester_present()
            logging.info("Tester Present sent successfully")
        except Exception as e:
            logging.warning(f"Tester Present failed: {e}")

        # Default Session (0x10 0x01)
        try:
            response = client.change_session(0x01)
            if response.positive:
                logging.info("Switched to Default Session")
            else:
                logging.warning("Failed to switch to Default Session")
        except Exception as e:
            logging.error(f"Error in Default Session: {e}")

        # Extended Session (0x10 0x03)
        try:
            response = client.change_session(0x03)
            if response.positive:
                logging.info("Switched to Extended Session")
            else:
                logging.warning("Failed to switch to Extended Session")
        except Exception as e:
            logging.error(f"Error in Extended Session: {e}")

        try:
            response = client.read_data_by_identifier(0xF100)
            if response.positive:
                logging.info(f"ECU information: {response.service_data.values[0xF100]}")
            else:
                logging.warning("Failed to Read ECU information")
        except Exception as e:
            logging.error(f"Error reading ECU information: {e}")
            
        try:
            response = client.read_data_by_identifier(0xF101)
            if response.positive:
                logging.info(f"ECU information: {response.service_data.values[0xF101]}")
            else:
                logging.warning("Failed to Read ECU information")
        except Exception as e:
            logging.error(f"Error reading ECU information: {e}")
            
        # Read VIN (DID 0xF190)
        try:
            response = client.read_data_by_identifier(0xF187)
            if response.positive:
                logging.info(f"ECU information: {response.service_data.values[0xF187]}")
            else:
                logging.warning("Failed to Read ECU information")
        except Exception as e:
            logging.error(f"Error reading ECU information: {e}")
            
        try:
            response = client.read_data_by_identifier(0xF193)
            if response.positive:
                logging.info(f"ECU information: {response.service_data.values[0xF193]}")
            else:
                logging.warning("Failed to Read ECU information")
        except Exception as e:
            logging.error(f"Error reading ECU information: {e}")
        
        try:
            response = client.read_data_by_identifier(0xF102)
            if response.positive:
                logging.info(f"ECU information: {response.service_data.values[0xF102]}")
            else:
                logging.warning("Failed to Read ECU information")
        except Exception as e:
            logging.error(f"Error reading ECU information: {e}")

        try:
            response = client.read_data_by_identifier(0xF18B)
            if response.positive:
                logging.info(f"ECU information: {response.service_data.values[0xF18B]}")
            else:
                logging.warning("Failed to Read ECU information")
        except Exception as e:
            logging.error(f"Error reading ECU information: {e}")        

        
            
        try:
            response = client.read_data_by_identifier(0xF1B1)
            if response.positive:
                logging.info(f"ECU information: {response.service_data.values[0xF1B1]}")
            else:
                logging.warning("Failed to Read ECU information")
        except Exception as e:
            logging.error(f"Error reading ECU information: {e}")  
            
                

        try:
            response = client.read_data_by_identifier(0xF120)
            if response.positive:
                logging.info(f"ECU information: {response.service_data.values[0xF120]}")
            else:
                logging.warning("Failed to Read ECU information")
        except Exception as e:
            logging.error(f"Error reading ECU information: {e}")    
         
    logging.info("UDS Client Closed")

variable=0
varFinal=0
try:
    while True:
        if GPIO.input(BTN_FIRST) == GPIO.LOW:
            variable=(variable*10)+1
            selected_sequence.append(BTN_FIRST)
            b = str(variable)
            display_text(b)
            #time.sleep(0.2)

        if GPIO.input(BTN_SECOND) == GPIO.LOW:
            variable=(variable*10)+2
            selected_sequence.append(BTN_SECOND)
            a = str(variable)
            display_text(a)
            #time.sleep(0.2)      

        if GPIO.input(BTN_ENTER) == GPIO.LOW:
            varFinal=variable
            variable=0
            selected_sequence.append(BTN_ENTER)
                
            selected_option = menu_combinations.get(tuple(selected_sequence), "Invalid Input")
            display_text(f"{selected_option}")

            if selected_option == "ECU Information":
                time.sleep(0.5)
                display_text("Fetching\nECU Information...")
                get_ecu_information()
                display_text("Completed")
           # if selected_option == "Testcase Execution":
               # time.sleep(0.5)
            #    display_text("Sahithi is working...")
                #get_ecu_information()
                #display_text("Completed")
            if selected_option == "Exit":
                os.system("exit")
            selected_sequence.clear()  # Reset sequence after confirmation
            #time.sleep(0.1)

        if GPIO.input(BTN_THANKS) == GPIO.LOW:
            display_text("Shutting Down")
            time.sleep(0.1)
            os.system('sudo poweroff')

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.cleanup()
