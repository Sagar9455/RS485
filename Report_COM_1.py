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


def TestUDSFromText(unittest.TestCase):
    test_cases = []
      with open("test_cases.txt", "r") as f:
           reader = csv.reader(f)
           next(reader)  # Skip header
           for row in reader:
               if not row[0].startswith("#"):  # Ignore comments
                  test_cases.append(row)
           print(test_cases)
           
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
      bus.set_filters([{"can_id":0x18DAF110,"can_mask":0xFFF}])

      # Define ISO-TP addressing for 11-bit CAN IDs
      tp_addr = isotp.Address(isotp.AddressingMode.Normal_29bits, txid=0x18DA34FA, rxid=0x18DAFA34)

      # Create ISO-TP stack
      stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)

      # Create UDS connection
      conn = PythonIsoTpConnection(stack)
      
      # Start UDS Client
      with Client(conn, request_timeout=5,config=config) as client:
           logging.info("UDS Client Started")
           display_text("Executing Testcases...")
                
            
           """Execute UDS test cases dynamically from a file."""
        
           for case in test_cases:
               tc_id, step, service_id, subfunction, expected_response = case

               service_id = int(service_id, 16)
               subfunction = int(subfunction, 16)
               expected_response = int(expected_response, 16)
 
               logging.info(f"Executing {tc_id}: {step}")
               time.sleep(0.5)
               if service_id == 0x10:  # Diagnostic Session Control                           
                   try:
                       response = client.change_session(subfunction)
                       if response.positive:
                          logging.info("Switched to Extended Session")
                          test_report.append({
                              'request': '0x10 0x01',
                              
                              'actual_response': hex(response.original_payload) if response.original_payload else "N/A",  # Example actual response
                              'status': 'Pass'
                          })
                          
                       else:
                            logging.warning("Failed to switch to Extended Session")
                   except Exception as e:
                          logging.error(f"Error in Extended Session: {e}")
                          
               elif service_id == 0x22:  # Read Data By Identifier
                     try:
                        response = client.read_data_by_identifier(subfunction)
                        if response.positive:
                           logging.info("Switched to rdbi  ")
                           test_report.append({
                               'request': '0x22 subfunction',
                               
                               'actual_response': hex(response.original_payload) if response.original_payload else "N/A",  
                               'status': 'Pass'
                           })
                        else:
                           logging.warning("Failed to switch to RDBI ")
                     except Exception as e:
                           logging.error(f"Error in RDBI : {e}")        
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
        try:
            response = client.change_session(0x01)  # 0x01: Default Session
            if response.positive:
                logging.info("Successfully switched to Default Session (0x10 0x01)")
                test_report.append({
                    'request': '0x10 0x01',
                    'expected_response': '0x02 0x60',  # Example expected response
                    'actual_response': hex(response.original_payload) if response.original_payload else "N/A",  # Example actual response
                    'status': 'Pass'
                })
            else:
                logging.warning("Failed to switch to Default Session (0x10 0x01)")
                test_report.append({
                    
                    'request': '0x10 0x01',
                    'expected_response': '0x7F 0x10 0x00',
                    'actual_response': 'N/A',
                    'status': 'Fail'
                })
        except Exception as e:
            logging.error(f"Error switching to Default Session (0x10 0x01): {e}")
            test_report.append({
                
                'request': '0x10 0x01',
                'expected_response': '0x7F 0x10 0x00',
                'actual_response': f'Error: {e}',
                'status': 'Fail'
            })

        try:
            response = client.change_session(0x03)  # 0x01: Default Session
            if response.positive:
                logging.info("Successfully switched to Default Session (0x10 0x01)")
                test_report.append({
                    
                    'request': '0x10 0x03',
                    'expected_response': '0x02 0x60',  # Example expected response
                    'actual_response': hex(response.original_payload) if response.original_payload else "N/A",  # Example actual response
                    'status': 'Pass'
                })
            else:
                logging.warning("Failed to switch to Default Session (0x10 0x01)")
                test_report.append({
                    
                    'request': '0x10 0x03',
                    'expected_response': '0x7F 0x10 0x00',
                    'actual_response': 'N/A',
                    'status': 'Fail'
                })
        except Exception as e:
            logging.error(f"Error switching to Default Session (0x10 0x01): {e}")
            test_report.append({
                
                'request': '0x10 0x03',
                'expected_response': '0x7F 0x10 0x00',
                'actual_response': f'Error: {e}',
                'status': 'Fail'
            })
        for did in config["data_identifiers"]:
            try:
                response = client.read_data_by_identifier(did)
                
                if response.positive:
                    logging.info(f"ECU information (DID {hex(did)}): {response.service_data.values[did]}")
                    sid = 0x22  # ReadDataByIdentifier (RDBI) request SID
                    expected_first_byte = sid + 0x40  # Expected first byte (0x62)
                    actual_response_bytes = response.original_payload  # Get raw response

                    if actual_response_bytes and actual_response_bytes[0] == expected_first_byte:
                        status = "Pass"
                    else:
                        status = "Fail"

                    test_report.append({
                        
                        'request': f'0x22 {hex(did)}',
                        'actual_response': hex(actual_response_bytes[0]) if actual_response_bytes else "N/A",
                        'status': status
                    })                                 
                else:
                    logging.warning(f"Failed to read ECU information (DID {hex(did)})")
                    test_report.append({
                        
                        'request': f'0x22 {hex(did)}',
                        'actual_response': 'N/A',
                        'status': 'Fail'
                    })
                    
                    
            except Exception as e:
                logging.error(f"Error reading ECU information (DID {hex(did)}): {e}")

        logging.info("UDS Client Closed")
        
    generate_html_report(test_report)
   
def generate_html_report(did_results, output_file="DID_Report.html"):
    html_content = """
    <html>
    <head>
        <title>DID Test Report</title>
        <style>
            body { font-family: Arial, sans-serif; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h2>DID Test Report</h2>
        <table>
            <tr>
                <th>Request</th>
                <th>Response</th>
                <th>Status</th>
            </tr>
    """
    
    for did, result in did_results.items():
        html_content += f"""
            <tr>
                <td>{request}</td>
                <td>{result['response']}</td>
                <td style='color: {"green" if result['status'] == "Success" else "red"};'>
                    {result['status']}
                </td>
            </tr>
        """
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open(output_file, "w") as file:
        file.write(html_content)
    
    print(f"Report generated: {output_file}")



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
                
            if selected_option == "Testcase Execution":
                time.sleep(0.5)
                display_text("Executing Testcase...")
                TestUDSFromText()
                display_text("Testcase Execution Completed")
            
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
