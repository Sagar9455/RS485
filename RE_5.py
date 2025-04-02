import os
import time
import logging
import RPi.GPIO as GPIO
import can
import isotp
import udsoncan
from udsoncan.client import Client
from udsoncan.connections import PythonIsoTpConnection

# Setup GPIO button
BUTTON_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Bring up CAN interface
os.system('sudo ip link set can0 up type can bitrate 500000 dbitrate 1000000 restart-ms 1000 berr-reporting on fd on')
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
bus = can.interface.Bus(channel=interface, bustype="socketcan", fd=True)
bus.set_filters([{"can_id": 0x7A8, "can_mask": 0xFFF}])

# Define ISO-TP addressing for 11-bit CAN IDs
tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=0x7A0, rxid=0x7A8)

# Create ISO-TP stack
stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)
conn = PythonIsoTpConnection(stack)

def generate_report(request_status, response_status):
    html_content = f"""
    <html>
    <head>
        <style>
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
            .pass {{ background-color: lightgreen; }}
            .fail {{ background-color: lightcoral; }}
        </style>
    </head>
    <body>
        <h2>UDS Diagnostic Report</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Action</th>
                <th>Status</th>
            </tr>
            <tr class="{request_status.lower()}">
                <td>{time.strftime('%Y-%m-%d %H:%M:%S')}</td>
                <td>Request Sent</td>
                <td>{request_status}</td>
            </tr>
            <tr class="{response_status.lower()}">
                <td>{time.strftime('%Y-%m-%d %H:%M:%S')}</td>
                <td>Positive Response Received</td>
                <td>{response_status}</td>
            </tr>
        </table>
    </body>
    </html>
    """
    with open("DID_Report.html", "w") as file:
        file.write(html_content)
    print("Report generated: DID_Report.html")

# Run UDS Client
try:
    with Client(conn, request_timeout=2, config=config) as client:
        print("Waiting for button press...")
        while True:
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                print("Button pressed! Sending UDS request...")
                request_status = "Pass"
                response_status = "Fail"
                try:
                    response = client.read_data_by_identifier(0xF190)
                    if response.positive:
                        response_status = "Pass"
                except Exception as e:
                    print(f"Error: {e}")
                    request_status = "Fail"

                generate_report(request_status, response_status)
                time.sleep(1)  # Prevent multiple detections
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()
