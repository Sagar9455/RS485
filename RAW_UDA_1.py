import can
from udsoncan import Connection, Request, Response, services
from udsoncan.connections import IsoTPConnection
import isotp
import time

# CAN Interface Setup
bus = can.interface.Bus(channel='can0', bustype='socketcan')
stack = isotp.CanStack(bus, txid=0x7E0, rxid=0x7E8, padding_byte=0x00)  # 11-bit identifiers
conn = IsoTPConnection(stack)

# UDS Connection
with Connection(conn) as my_connection:

    # 1. Tester Present (0x3E 0x00)
    req = Request(services.TesterPresent, subfunction=0x00)
    my_connection.send(req.get_payload())
    print("Sent Tester Present")
    time.sleep(0.5)

    # 2. Default Session Control (0x10 0x01)
    req = Request(services.DiagnosticSessionControl, session=0x01)
    my_connection.send(req.get_payload())
    print("Sent Default Session Control")
    time.sleep(0.5)

    # 3. Extended Session Control (0x10 0x03)
    req = Request(services.DiagnosticSessionControl, session=0x03)
    my_connection.send(req.get_payload())
    print("Sent Extended Session Control")
    time.sleep(0.5)

    # 4. ReadDataByIdentifier (0x22 0xF1 0x01)
    req = Request(services.ReadDataByIdentifier, didlist=[0xF101])
    my_connection.send(req.get_payload())
    print("Sent RDBI request for 0xF101")

    # Receive Response
    payload = my_connection.wait_frame(timeout=1)
    if payload:
        response = Response.from_payload(payload)
        print(f"Response: {response}")
    else:
        print("No response received.")
