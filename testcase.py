import unittest
import can
import csv
import udsoncan
import isotp
from udsoncan.client import Client
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.services import DiagnosticSessionControl, SecurityAccess, ReadDataByIdentifier, WriteDataByIdentifier
import logging
import os

# CAN Configuration
CAN_CHANNEL = "can0"
TX_ID = 0x7A0
RX_ID = 0x7A8


class TestUDSFromText(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Setup UDS client and CAN connection before running tests."""
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
        cls.bus = can.interface.Bus(channel=CAN_CHANNEL, bustype="socketcan", fd=True)
        cls.tp_layer = isotp.CanStack(cls.bus, 
        address=isotp.Address(txid=TX_ID, rxid=RX_ID),
        params={"tx_padding": 0x00})
        cls.conn = PythonIsoTpConnection(cls.tp_layer)
        cls.client = Client(cls.conn)
        client =  Client(cls.conn, request_timeout=10)
        cls.client.open()

        # Load test cases from file
        cls.test_cases = []
        with open("test_cases.txt", "r") as f:
             reader = csv.reader(f)
             next(reader)  # Skip header
             for row in reader:
                 if not row[0].startswith("#"):  # Ignore comments
                     cls.test_cases.append(row)
                 print(cls.test_cases)
       
    @classmethod
    def tearDownClass(cls):
        """Close UDS client and CAN connection after tests."""
        cls.client.close()
        cls.bus.shutdown()

    def test_uds_sequence(self):
        """Execute UDS test cases dynamically from a file."""
        
        for case in self.test_cases:
            tc_id, step, service_id, subfunction, expected_response = case

            service_id = int(service_id, 16)
            subfunction = int(subfunction, 16)
            expected_response = int(expected_response, 16)

            print(f"Executing {tc_id}: {step}")
        
            if service_id == 0x10:  # Diagnostic Session Control
                #response = client.change_session(subfunction)
                try:
                    if service_id == 0x10:  # Diagnostic Session Control
                       response = self.client.change_session(subfunction)
                    if response.positive:
                        logging.info("Switched to Extended Session")
                    else:
                        logging.warning("Failed to switch to Extended Session")
                except Exception as e:
                      logging.error(f"Error in Extended Session: {e}")
             
            elif service_id == 0x27:  # Security Access
                if subfunction == 0x01:
                    response = self.client.request_seed(SecurityAccess.Level.requestSeed)
                else:
                    response = self.client.send_key(b"\x12\x34\x56\x78")  # Mock key
            elif service_id == 0x22:  # Read Data By Identifier
                response = self.client.read_data_by_identifier(subfunction)
            elif service_id == 0x2E:  # Write Data By Identifier
                response = self.client.write_data_by_identifier(subfunction, b"\x01\x02\x03\x04")
            else:
                self.fail(f"Unsupported service {hex(service_id)}")

            self.assertEqual(response.service_data[0], expected_response, f"Test {tc_id} failed")


if __name__ == "__main__":
    unittest.main()
