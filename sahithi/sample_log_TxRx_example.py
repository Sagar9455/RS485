import can
import time

# UDS Service Request: Read DTC (Diagnostic Trouble Codes)
# Format: [Service ID, Sub-function ID (0x01 for DTCs), 0x00 for request]
def create_uds_read_dtc_request():
    # Service ID 0x19 (Read DTC) + Sub-function 0x01
    return [0x19, 0x01, 0x00]  # Example: Request to read DTCs

# Define the log file path
log_file = 'can_communication_log.asc'

# Open the log file in append mode, or create it if it doesn't exist
with open(log_file, 'w') as f:
    # Write the header to the ASC file
    f.write('Vector CANalyzer CAN Logfile\n')
    f.write('date: {}\n'.format(time.strftime('%Y-%m-%d')))
    f.write('comment: Logging CAN communication with UDS service\n')
    f.write('begin of logfile\n')

    # Define the CAN bus interface (you might need to change this to your CAN interface)
    bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000)  # Example for Linux

    # Create the UDS Read DTC request (Tx)
    request_data = create_uds_read_dtc_request()
    
    # Send the UDS Request message (Tx)
    message_tx = can.Message(arbitration_id=0x7E0, data=request_data, is_extended_id=False)
    bus.send(message_tx)

    # Log the Tx message
    f.write('{:.6f} Tx 0 8 {:#010x} {} 00 00 00 00 00 00 00 00\n'.format(
        time.time(), message_tx.arbitration_id, ' '.join([f'{x:02X}' for x in message_tx.data])
    ))

    print(f"Sent Tx: {message_tx}")

    # Wait for the Rx response (Example: The ECU might respond on arbitration ID 0x7E8)
    response_rx = bus.recv(timeout=1.0)  # Timeout after 1 second if no response is received

    if response_rx:
        # Log the Rx message
        f.write('{:.6f} Rx 0 8 {:#010x} {} 00 00 00 00 00 00 00 00\n'.format(
            time.time(), response_rx.arbitration_id, ' '.join([f'{x:02X}' for x in response_rx.data])
        ))
        
        print(f"Received Rx: {response_rx}")
    else:
        print("No response received from ECU.")
    
    # Write the footer to the ASC file
    f.write('end of logfile\n')

