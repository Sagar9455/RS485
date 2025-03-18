import unittest
import can
import csv
import udsoncan
from udsoncan.client import Client
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.services import DiagnosticSessionControl, SecurityAccess, ReadDataByIdentifier, WriteDataByIdentifier

# CAN Configuration
CAN_CHANNEL = "vcan0"
TX_ID = 0x7E0
RX_ID = 0x7E8


class TestUDSFromText(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Setup UDS client and CAN connection before running tests."""
        cls.bus = can.interface.Bus(channel=CAN_CHANNEL, bustype="socketcan")
        cls.conn = PythonIsoTpConnection(cls.bus, txid=TX_ID, rxid=RX_ID)
        cls.client = Client(cls.conn)
        cls.client.open()

        # Load test cases from file
        cls.test_cases = []
        with open("test_cases.txt", "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if not row[0].startswith("#"):  # Ignore comments
                    cls.test_cases.append(row)

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
                response = self.client.change_session(subfunction)
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
