import can
from udsoncan import Request, Response, services
from udsoncan.connections import IsoTPConnection
import isotp
import time

# CAN Interface Setup
isotp_params = {
    'tx_padding': 0x00,
    'rx_padding': 0x00,
    'stmin': 0,
    'blocksize': 8,
    'wftmax': 0
}

bus = can.interface.Bus(channel='can0', bustype='socketcan')
stack = isotp.CanStack(bus, address=isotp.Address(isotp.AddressingMode.Normal_11bits, txid=0x7E0, rxid=0x7E8), params=isotp_params)
conn = IsoTPConnection(stack)

# 1. Raw Connection
with conn as my_connection:
    my_connection.send(b'\x3E\x00')  # Tester Present
    print("Sent Tester Present")
    time.sleep(0.5)

    my_connection.send(b'\x10\x01')  # Default Session
    print("Sent Default Session Control")
    time.sleep(0.5)

    my_connection.send(b'\x10\x03')  # Extended Session
    print("Sent Extended Session Control")
    time.sleep(0.5)

    my_connection.send(b'\x22\xF1\x01')  # RDBI Request
    print("Sent RDBI request for 0xF101")

    # Receive Response
    payload = my_connection.wait_frame(timeout=1)
    if payload:
        print(f"Response: {payload}")
    else:
        print("No response received.")

# 2. Request & Response
with conn as my_connection:
    req = Request(services.TesterPresent, subfunction=0x00)
    my_connection.send(req.get_payload())
    print("Sent Tester Present")
    time.sleep(0.5)

    req = Request(services.DiagnosticSessionControl, session=0x01)
    my_connection.send(req.get_payload())
    print("Sent Default Session Control")
    time.sleep(0.5)

    req = Request(services.DiagnosticSessionControl, session=0x03)
    my_connection.send(req.get_payload())
    print("Sent Extended Session Control")
    time.sleep(0.5)

    req = Request(services.ReadDataByIdentifier, didlist=[0xF101])
    my_connection.send(req.get_payload())
    print("Sent RDBI request for 0xF101")

    payload = my_connection.wait_frame(timeout=1)
    if payload:
        response = Response.from_payload(payload)
        print(f"Response: {response}")
    else:
        print("No response received.")

# 3. Services
with conn as my_connection:
    req = services.TesterPresent.make_request()  # Tester Present
    my_connection.send(req.get_payload())
    print("Sent Tester Present")
    time.sleep(0.5)

    req = services.DiagnosticSessionControl.make_request(session=0x01)  # Default Session
    my_connection.send(req.get_payload())
    print("Sent Default Session Control")
    time.sleep(0.5)

    req = services.DiagnosticSessionControl.make_request(session=0x03)  # Extended Session
    my_connection.send(req.get_payload())
    print("Sent Extended Session Control")
    time.sleep(0.5)

    req = services.ReadDataByIdentifier.make_request(didlist=[0xF101])  # RDBI Request
    my_connection.send(req.get_payload())
    print("Sent RDBI request for 0xF101")

    payload = my_connection.wait_frame(timeout=1)
    if payload:
        response = Response.from_payload(payload)
        print(f"Response: {response}")
    else:
        print("No response received.")
