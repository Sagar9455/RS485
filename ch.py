import can
from python_uds import UdsClient, services
# Function to pad the data to a multiple of 8 bytes for CAN FD
def pad_data(data):
    padding_needed = (8 - (len(data) % 8)) % 8
    return data + [0] * padding_needed  # Pad with 0x00
# Create CAN interface (using can0 for Raspberry Pi CAN interface)
can_interface = 'can0'
bus = can.interface.Bus(can_interface, bustype='socketcan', fd=True)
# Create UDS client
client = UdsClient(bus)
# Example UDS service (Diagnostic Session Control)
session_control_service = services.DiagnosticSessionControl()
# Example data for UDS request (should be padded to match the CAN FD requirements)
data = [0x10, 0x01]  # Example data: Service 0x10 with Mode 0x01
padded_data = pad_data(data)  # Pad data to ensure multiple of 8 bytes
# Send the UDS request with padded data
try:
    response = client.send_request(service=session_control_service, data=padded_data)
    print("Response received:", response)
except Exception as e:
    print("Error sending UDS request:", str(e))