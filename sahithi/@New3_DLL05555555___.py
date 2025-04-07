import unittest
import can
import csv
import isotp
import udsoncan
from udsoncan.client import Client
from udsoncan.connections import PythonIsoTpConnection
import udsoncan.configs
import logging
import time

# Logging config (with timestamps)
logging.basicConfig(
    filename="debug_can.log",
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# CAN Interface
interface = "can0"
bus = can.interface.Bus(channel=interface, bustype="socketcan", fd=True)

# Optional CAN filters
bus.set_filters([
    {"can_id": 0x7A8, "can_mask": 0xFFF},
    {"can_id": 0x7A0, "can_mask": 0xFFF}
])

# ASC log file
asc_filename = "can_log.asc"
asc_logger = can.ASCWriter(asc_filename)

# Add Listener for debug logging
class DebugLogger(can.Listener):
    def on_message_received(self, msg):
        logging.info(f"RX  ID={hex(msg.arbitration_id)} Data={msg.data.hex()}")

# Start notifier with both ASC log and debug listener
notifier = can.Notifier(bus, [asc_logger, DebugLogger()])

# ISO-TP config for CAN FD
isotp_params = {
    'stmin': 32,
    'blocksize': 8,
    'wftmax': 0,
    'tx_padding': 0x00,
    'rx_flowcontrol_timeout': 1000,
    'rx_consecutive_frame_timeout': 1000,
    'max_frame_size': 4095,
    'can_fd': True,
    'bitrate_switch': True
}

# UDS client config
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

# ISO-TP addressing
tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=0x7A0, rxid=0x7A8)
stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)
conn = PythonIsoTpConnection(stack)

class TestUDSFromText(unittest.TestCase):
    test_cases = []
    with open("test_cases_.txt", "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if row and not row[0].startswith("#"):
                test_cases.append(row)

    def test_uds_cases(self):
        with Client(conn, request_timeout=2, config=config) as client:
            logging.info("UDS Client Started")
            for case in self.test_cases:
                tc_id, step, service_id, subfunction, expected_response = case
                service_id = int(service_id, 16)
                subfunction = int(subfunction, 16)

                logging.info(f"Executing {tc_id}: {step}")
                try:
                    if service_id == 0x10:
                        client.change_session(subfunction)
                    elif service_id == 0x22:
                        client.read_data_by_identifier(subfunction)
                    elif service_id == 0x27:
                        if subfunction == 0x01:
                            client.request_seed(udsoncan.services.SecurityAccess.Level.requestSeed)
                        else:
                            client.send_key(b"\x12\x34\x56\x78")
                    elif service_id == 0x2E:
                        client.write_data_by_identifier(subfunction, b"\x01\x02\x03\x04")
                except Exception as e:
                    logging.error(f"UDS error in {tc_id}: {e}")

if __name__ == "__main__":
    try:
        unittest.main()
    finally:
        notifier.stop()
        logging.info("Stopped CAN logging.")
