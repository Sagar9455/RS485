import udsoncan
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.client import Client
import udsoncan.configs
import isotp
import can
import logging

# Logging setup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

# Define ISO-TP parameters for CAN FD with 11-bit identifiers
isotp_params = {
    'stmin': 32,
    'blocksize': 8,
    'wftmax': 0,
    'tx_data_length': 64,  # CAN FD supports up to 64 bytes
    'tx_padding': None,     # No padding for CAN FD
    'rx_flowcontrol_timeout': 1000,
    'rx_consecutive_frame_timeout': 1000,
    'squash_stmin_requirement': False,
    'max_frame_size': 4095,
    'can_fd': True          # Enable CAN FD mode
}

# UDS Client Configuration
config = dict(udsoncan.configs.default_client_config)
config["ignore_server_timing_requirements"] = True
config["padding_byte"] = None  # No padding for CAN FD
config["data_identifiers"] = {
    0xF190: udsoncan.AsciiCodec(17)  # VIN is a 17-character ASCII string
}

# Define CAN interface
interface = "can0"

# Create CAN bus interface
bus = can.interface.Bus(channel=interface, bustype="socketcan", fd=True, bitrate=500000, data_bitrate=2000000)

# Define ISO-TP addressing for 11-bit CAN IDs
tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=0x8A0, rxid=0x8A8)

# Create ISO-TP stack
stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)

# Create UDS connection
conn = PythonIsoTpConnection(stack)

# Start UDS Client
with Client(conn, request_timeout=2, config=config) as client:
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

    # Read VIN (DID 0xF190)
    try:
        response = client.read_data_by_identifier(0xF190)
        if response.positive:
            logging.info(f"VIN: {response.service_data.values[0xF190]}")
        else:
            logging.warning("Failed to Read VIN")
    except Exception as e:
        logging.error(f"Error reading VIN: {e}")

logging.info("UDS Client Closed")
