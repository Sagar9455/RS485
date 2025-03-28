import unittest
import can
import csv
import isotp
import udsoncan
from udsoncan.client import Client
from udsoncan.connections import PythonIsoTpConnection
import udsoncan.configs
import logging
import os
import time

# Define CAN interface
interface = "can0"

# Set up CAN bus
bus = can.interface.Bus(channel=interface, bustype="socketcan", fd=True)

# Set up CAN message filters (Optional: To focus on specific IDs)
bus.set_filters([{"can_id": 0x7A8, "can_mask": 0xFFF}])

# Define ASC log file
log_filename = "can_log.asc"

# Create ASC Logger and Notifier
asc_logger = can.ASCWriter(log_filename)
notifier = can.Notifier(bus, [asc_logger])  # Logs both TX and RX messages

# Initialize ASC log file
with open(log_filename, "w") as asc_file:
    asc_file.write(f"date {time.strftime('%Y-%m-%d %H:%M:%S.000000')}\n")
    asc_file.write("base hex timestamps absolute\n\n")

# Function to log CAN messages manually in `.asc` format
def log_can_message_asc(msg, direction):
    timestamp = time.time()
    with open(log_filename, "a") as asc_file:
        asc_file.write(f"{timestamp:.6f} 1 {msg.arbitration_id:X} {direction} d {msg.dlc} " +
                       " ".join(f"{byte:02X}" for byte in msg.data) + "\n")

# Modify your CAN send/receive section:
def send_can_message(bus, msg):
    """Send CAN message and log it."""
    bus.send(msg)
    logging.info(f"CAN Message Sent: ID={hex(msg.arbitration_id)}, Data={msg.data.hex()}")
    log_can_message_asc(msg, "Tx")  # Log sent message

def receive_can_message(bus, timeout=2):
    """Receive CAN message and log it."""
    msg = bus.recv(timeout=timeout)
    if msg:
        logging.info(f"CAN Message Received: ID={hex(msg.arbitration_id)}, Data={msg.data.hex()}")
        log_can_message_asc(msg, "Rx")  # Log received message
    return msg


class TestUDSFromText(unittest.TestCase):
    """Run UDS test cases dynamically from a file."""
    
    test_cases = []
    with open("test_cases_.txt", "r") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if not row[0].startswith("#"):  # Ignore comments
                test_cases.append(row)

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
        0xF102: udsoncan.AsciiCodec(0),
        0xF188: udsoncan.AsciiCodec(16),
        0xF18C: udsoncan.AsciiCodec(16),
        0xF197: udsoncan.AsciiCodec(16),
        0xF1A1: udsoncan.AsciiCodec(16)
    }

    # Define ISO-TP addressing for 11-bit CAN IDs
    tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=0x7A0, rxid=0x7A8)

    # Create ISO-TP stack
    stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)

    # Create UDS connection
    conn = PythonIsoTpConnection(stack)

    # Start UDS Client
    with Client(conn, request_timeout=2, config=config) as client:
        logging.info("UDS Client Started")

        for case in test_cases:
            tc_id, step, service_id, subfunction, expected_response = case

            service_id = int(service_id, 16)
            subfunction = int(subfunction, 16)
            expected_response = int(expected_response, 16)

            print(f"Executing {tc_id}: {step}")

            if service_id == 0x10:  # Diagnostic Session Control
                try:
                    response = client.change_session(subfunction)
                    send_can_message(bus, can.Message(arbitration_id=0x7A0, data=[service_id, subfunction], is_extended_id=False))
                except Exception as e:
                    logging.error(f"Error in Extended Session: {e}")

            elif service_id == 0x22:  # Read Data By Identifier
                try:
                    response = client.read_data_by_identifier(subfunction)
                    send_can_message(bus, can.Message(arbitration_id=0x7A0, data=[service_id, subfunction], is_extended_id=False))
                except Exception as e:
                    logging.error(f"Error in RDBI: {e}")

            elif service_id == 0x27:  # Security Access
                try:
                    if subfunction == 0x01:
                        response = client.request_seed(SecurityAccess.Level.requestSeed)
                    else:
                        response = client.send_key(b"\x12\x34\x56\x78")
                    send_can_message(bus, can.Message(arbitration_id=0x7A0, data=[service_id, subfunction], is_extended_id=False))
                except Exception as e:
                    logging.error(f"Error in Security Access: {e}")

            elif service_id == 0x2E:  # Write Data By Identifier
                try:
                    response = client.write_data_by_identifier(subfunction, b"\x01\x02\x03\x04")
                    send_can_message(bus, can.Message(arbitration_id=0x7A0, data=[service_id, subfunction, 0x01, 0x02, 0x03, 0x04], is_extended_id=False))
                except Exception as e:
                    logging.error(f"Error in WDBI: {e}")

        print(f"Logging CAN messages in {log_filename}")

        try:
            while True:
                receive_can_message(bus)
        except KeyboardInterrupt:
            print("Stopping logging.")
            notifier.stop()


if __name__ == "__main__":
    unittest.main()
