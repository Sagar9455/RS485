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

# Prepare the report
test_report = []
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
        'bitrate_switch': True  # Enable CAN FD mode
    }

    # UDS Client Configuration
    config = dict(udsoncan.configs.default_client_config)
    config["ignore_server_timing_requirements"] = True
    # Define data identifiers for UDS communication
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

    with Client(conn, request_timeout=2, config=config) as client:
        logging.info("UDS Client Started")
        try:
            client.tester_present()
            logging.info("Tester Present sent successfully")
        except Exception as e:
            logging.warning(f"Tester Present failed: {e}")

        # Change Session Request - Default Session (0x10 0x01)
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        try:
            response = client.change_session(0x01)  # 0x01: Default Session
            request_status = "Pass"
            if response.positive:
                response_status = "Pass"
                logging.info("Successfully switched to Default Session (0x10 0x01)")
                
            else:
                logging.warning("Failed to switch to Default Session (0x10 0x01)")
                request_status = "Fail"
                response_status = "Fail"
                
        except Exception as e:
            logging.error(f"Error switching to Default Session (0x10 0x01): {e}")
            request_status = "Fail"
            response_status = "Fail"
        report_data.append({"timestamp": timestamp, "action": "Extended Session (0x10 0x03)", "request_status": request_status, "response_status": response_status})
        time.sleep(0.5)    
           
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 
        try:
            response = client.change_session(0x03)  # 0x01: Default Session
            request_status = "Pass"
            if response.positive:
                response_status = "Pass"
                logging.info("Successfully switched to Default Session (0x10 0x01)")
                
            else:
                logging.warning("Failed to switch to Default Session (0x10 0x01)")
                request_status = "Fail"
                response_status = "Fail"
                
                
        except Exception as e:
            logging.error(f"Error switching to Default Session (0x10 0x01): {e}")
            request_status = "Fail"
            response_status = "Fail"
        
        report_data.append({"timestamp": timestamp, "action": "Extended Session (0x10 0x03)", "request_status": request_status, "response_status": response_status})
        time.sleep(0.5)

               
                
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')    
        for did in config["data_identifiers"]:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            try:
                response = client.read_data_by_identifier(did)
                request_status = "Pass"
                
                if response.positive:
                    response_status = "Pass"
                    logging.info(f"ECU information (DID {hex(did)}): {response.service_data.values[did]}")
                   
                                                
                else:
                    logging.warning(f"Failed to read ECU information (DID {hex(did)})")
                    request_status = "Fail"
                    response_status = "Fail"
                    
                    
            except Exception as e:
                logging.error(f"Error reading ECU information (DID {hex(did)}): {e}")
                request_status = "Fail"
                response_status = "Fail"
            report_data.append({"timestamp": timestamp, "action": "Extended Session (0x10 0x03)", "request_status": request_status, "response_status": response_status})
            
        # Generate Report
            generate_report(report_data)
            time.sleep(1)  # Prevent multiple detections
    
    
def generate_report(data):
    html_content = """
    <!DOCTYPE html>
    <head>
    <title>UDS Diagnostic Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { width: 80%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid black; padding: 10px; text-align: center; }
        th { background-color: #b0b0b0; color: black; } /* Darker Grey Header */
        .pass { background-color: #c8e6c9; color: green; font-weight: bold; }
        .fail { background-color: #ffcdd2; color: red; font-weight: bold; }
        .section-title { background-color: #f0f0f0; font-weight: bold; } /* Light Grey Section */
    </style>
    </head>
    <body>
        <h2>UDS Diagnostic Report</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Description</th>
                <th>Step</th>
                <th>Status</th>
            </tr>
    """
    
    for entry in data:
        html_content += f"""
            <tr class="section-title">
                <td rowspan="2">{entry["timestamp"]}</td>
                <td rowspan="2">{entry["action"]}</td>
                <td>Request Sent</td>
                <td class="{ 'pass' if entry['request_status'] == 'Pass' else 'fail' }">{entry['request_status']}</td>
            </tr>
            <tr>
                <td>Positive Response Received</td>
                <td class="{ 'pass' if entry['response_status'] == 'Pass' else 'fail' }">{entry['response_status']}</td>
            </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    with open("UDS_Report.html", "w") as file:
        file.write(html_content)
    print("Report generated: UDS_Report.html")



variable = 0
varFinal = 0
try:
    while True:
        if GPIO.input(BTN_FIRST) == GPIO.LOW:
            variable = (variable * 10) + 1
            selected_sequence.append(BTN_FIRST)
            b = str(variable)
            display_text(b)

        if GPIO.input(BTN_SECOND) == GPIO.LOW:
            variable = (variable * 10) + 2
            selected_sequence.append(BTN_SECOND)
            a = str(variable)
            display_text(a)

        if GPIO.input(BTN_ENTER) == GPIO.LOW:
            varFinal = variable
            variable = 0
            selected_sequence.append(BTN_ENTER)
            
            selected_option = menu_combinations.get(tuple(selected_sequence), "Invalid Input")
            display_text(f"{selected_option}")

            if selected_option == "ECU Information":
                time.sleep(0.5)
                display_text("Fetching\nECU Information...")
                get_ecu_information()
                display_text("Completed")
            
            if selected_option == "Exit":
                os.system("exit")
            selected_sequence.clear()  # Reset sequence after confirmation

        if GPIO.input(BTN_THANKS) == GPIO.LOW:
            display_text("Shutting Down")
            time.sleep(0.1)
            os.system('sudo poweroff')

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.cleanup()
