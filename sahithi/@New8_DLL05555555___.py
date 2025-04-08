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
import threading
import os

# ========== Logging Setup ==========
# Log to debug file with timestamp
logging.basicConfig(
    filename="debug_can.log",
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ASC-like file
asc_filename = "can_log.asc"

# Initialize asc file
with open(asc_filename, "w") as f:
    f.write(f"date {time.strftime('%Y-%m-%d %H:%M:%S.000000')}\n")
    f.write("base hex timestamps absolute\n\n")

def log_to_asc(msg, direction="Rx"):
    ts = time.time()
    line = f"{ts:.6f} 1 {msg.arbitration_id:X} {direction} d {msg.dlc} " + " ".join(f"{b:02X}" for b in msg.data)
    with open(asc_filename, "a") as f:
        f.write(line + "\n")

# ========== CAN Setup ==========
interface = "can0"
bus = can.interface.Bus(channel=interface, bustype="socketcan", fd=True)

# ISO-TP Setup for CAN FD
tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=0x7A0, rxid=0x7A8)

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

stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)
conn = PythonIsoTpConnection(stack)

# ========== Listener Thread for RX ==========
stop_rx = threading.Event()

def rx_logger():
    while not stop_rx.is_set():
        msg = bus.recv(timeout=0.5)
        if msg:
            logging.info(f"RX  ID={hex(msg.arbitration_id)} Data={msg.data.hex()}")
            log_to_asc(msg, direction="Rx")

rx_logger_thread = threading.Thread(target=rx_logger, daemon=True)
rx_logger_thread.start()

# ========== UDS Test Runner ==========
class TestUDSFromText(unittest.TestCase):
    test_cases = []
    with open("test_cases_.txt", "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if row and not row[0].startswith("#"):
                test_cases.append(row)

    def test_uds_cases(self):
        with Client(conn, request_timeout=2, config=udsoncan.configs.default_client_config) as client:
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

                    # Manual Tx logging from last frame
                    if stack.last_tx_frame:
                        log_to_asc(stack.last_tx_frame, direction="Tx")
                        logging.info(f"TX  ID={hex(stack.last_tx_frame.arbitration_id)} Data={stack.last_tx_frame.data.hex()}")

                except Exception as e:
                    logging.error(f"UDS error in {tc_id}: {e}")

# ========== Run ==========
if __name__ == "__main__":
    try:
        unittest.main()
    finally:
        stop_rx.set()
        rx_logger_thread.join()
        logging.info("CAN logging stopped.")
