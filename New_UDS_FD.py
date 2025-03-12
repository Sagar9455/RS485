import can
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.client import Client
import udsoncan.configs
import isotp

# IsoTP parameters for CAN FD with 11-bit identifier
isotp_params = {
    'stmin': 32,
    'blocksize': 8,
    'wftmax': 0,
    'tx_data_length': 64,                 # CAN FD max payload
    'tx_data_min_length': None,
    'tx_padding': 0x00,                   # Padding with 0x00
    'rx_flowcontrol_timeout': 1000,
    'rx_consecutive_frame_timeout': 1000,
    'squash_stmin_requirement': False,
    'max_frame_size': 4095,
    'can_fd': True,                       # Enable CAN FD mode
    'bitrate_switch': True,               # Enable bitrate switching
    'rate_limit_enable': False,
    'listen_mode': False,
}

uds_config = udsoncan.configs.default_client_config.copy()

try:
    # Initialize CAN bus
    bus = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=500000, fd=True)
    notifier = can.Notifier(bus, [can.Printer()])
    tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=0x8A0, rxid=0x8A8)

    # Initialize ISO-TP stack
    stack = isotp.NotifierBasedCanStack(bus=bus, notifier=notifier, address=tp_addr, params=isotp_params)
    conn = PythonIsoTpConnection(stack)

    # UDS Client Operations
    with Client(conn, config=uds_config) as client:
        try:
            client.change_session(1)  # Default Session
            print("[INFO] Session changed successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to change session: {e}")

except can.CanError as e:
    print(f"[CAN ERROR] CAN bus error occurred: {e}")

except isotp.CanStackError as e:
    print(f"[ISOTP ERROR] ISO-TP stack error occurred: {e}")

except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")

finally:
    # Cleanup to release CAN interface properly
    try:
        bus.shutdown()
        print("[INFO] CAN interface shut down successfully.")
    except NameError:
        print("[WARNING] CAN interface was not initialized, no shutdown required.")
