import time
import can
import logging
import os
import csv
import unittest
import isotp
import udsoncan
from udsoncan.client import Client
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.services import SecurityAccess

# Define ASC log file
asc_log_filename = "can_log.asc"

# Initialize ASC log file
with open(asc_log_filename, "w") as asc_file:
    asc_file.write(f"date {time.strftime('%Y-%m-%d %H:%M:%S.000000')}\n")
    asc_file.write("base hex timestamps absolute\n\n")

# Function to log CAN messages in `.asc` format
def log_can_message_asc(msg, direction):
    timestamp = time.time()
    with open(asc_log_filename, "a") as asc_file:
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
    test_cases = []

    # Read test cases from file
    with open("test_cases.txt", "r") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if not row[0].startswith("#"):  # Ignore comments
                test_cases.append(row)

    os.system("sudo ip link set can0 up type can bitrate 500000 dbitrate 1000000 restart-ms 1000 berr-reporting on fd on")
    os.system("sudo ifconfig can0 up")

    # Logging setup
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

    # ISO-TP parameters
    isotp_params = {
        "stmin": 32,
        "blocksize": 8,
        "wftmax": 0,
        "tx_padding": 0x00,
        "rx_flowcontrol_timeout": 1000,
        "rx_consecutive_frame_timeout": 1000,
        "max_frame_size": 4095,
        "can_fd": True,
        "bitrate_switch": True,
    }

    # UDS Client Configuration
    config = dict(udsoncan.configs.default_client_config)
    config["ignore_server_timing_requirements"] = True

    # Define CAN interface
    interface = "can0"
    bus = can.interface.Bus(channel=interface, bustype="socketcan", fd=True)
    bus.set_filters([{"can_id": 0x7A8, "can_mask": 0xFFF}])

    # Define ISO-TP addressing
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

            logging.info(f"Executing {tc_id}: {step}")

            if service_id == 0x10:  # Diagnostic Session Control
                try:
                    response = client.change_session(subfunction)
                    if response.positive:
                        logging.info("Switched to Extended Session")
                    else:
                        logging.warning("Failed to switch to Extended Session")
                except Exception as e:
                    logging.error(f"Error in Extended Session: {e}")

            elif service_id == 0x22:  # Read Data By Identifier
                try:
                    response = client.read_data_by_identifier(subfunction)
                    if response.positive:
                        logging.info("Received RDBI Response")
                    else:
                        logging.warning("Failed to read RDBI")
                except Exception as e:
                    logging.error(f"Error in RDBI: {e}")

            elif service_id == 0x27:  # Security Access
                try:
                    if subfunction == 0x01:  # Request Seed
                        response = client.request_seed(SecurityAccess.Level.requestSeed)
                    else:  # Send Key
                        response = client.send_key(b"\x12\x34\x56\x78")  # Mock key
                    if response.positive:
                        logging.info("Security Access Granted")
                    else:
                        logging.warning("Security Access Failed")
                except Exception as e:
                    logging.error(f"Error in Security Access: {e}")

            elif service_id == 0x2E:  # Write Data By Identifier
                try:
                    response = client.write_data_by_identifier(subfunction, b"\x01\x02\x03\x04")
                    if response.positive:
                        logging.info("WDBI executed successfully")
                    else:
                        logging.warning("WDBI failed")
                except Exception as e:
                    logging.error(f"Error in WDBI: {e}")

            else:
                self.fail(f"Unsupported service {hex(service_id)}")

            # Log CAN messages
            logging.info("Listening for CAN responses...")

            # Read and log CAN messages
            while True:
                msg = receive_can_message(bus, timeout=2)
                if not msg:
                    logging.info("No more CAN messages")
                    break


if __name__ == "__main__":
    unittest.main()
