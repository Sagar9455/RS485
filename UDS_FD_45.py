import can
import isotp
import udsoncan
from udsoncan.client import Client
from udsoncan.connections import IsoTPConnection
from threading import Timer
import logging

# Configure Logging
logging.basicConfig(level=logging.DEBUG)

# CAN Bus Configuration
CAN_INTERFACE = 'socketcan'
CAN_CHANNEL = 'can0'
TX_ID = 0x7A0
RX_ID = 0x7A8

# Configure CAN Bus
os.system("sudo ip link set can0 type can bitrate 500000 dbitrate 2000000 fd on brs on")
os.system("sudo ip link set up can0")

# ISO-TP Configuration
isotp_params = {
    'tx_padding': 0x00,
    'rx_padding': 0x00,
    'tx_data_length': 64,  # Full CAN FD frame size
    'can_fd': True,
    'bitrate_switch': True
}

bus = can.interface.Bus(channel=CAN_CHANNEL, interface=CAN_INTERFACE)
connection = IsoTPConnection(bus, TX_ID, RX_ID, params=isotp_params)

client = Client(connection, request_timeout=3, config={'exception_on_negative_response': False})

# Periodic Tester Present to Maintain Session
def send_tester_present():
    try:
        client.tester_present()
        logging.info("Tester Present Sent")
    except Exception as e:
        logging.error(f"Tester Present Failed: {e}")
    Timer(2, send_tester_present).start()

# Start Communication
try:
    client.open()
    logging.info("UDS Client Started")

    send_tester_present()  # Start periodic Tester Present

    # Switch to Default Session
    client.change_session(udsoncan.Session.DefaultSession)
    logging.info("Default Session Activated")

    # Switch to Extended Diagnostic Session
    client.change_session(udsoncan.Session.ExtendedDiagnosticSession)
    logging.info("Extended Session Activated")

except Exception as e:
    logging.error(f"Error: {e}")
finally:
    client.close()
    logging.info("UDS Client Closed")
