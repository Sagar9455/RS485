import can
import time

# Define the log file path
log_file = 'can_communication_log.asc'

# Open the log file in append mode, or create it if it doesn't exist
with open(log_file, 'w') as f:
    # Writing the header to the ASC file
    f.write('Vector CANalyzer CAN Logfile\n')
    f.write('date: {}\n'.format(time.strftime('%Y-%m-%d')))
    f.write('comment: Logging CAN communication\n')
    f.write('begin of logfile\n')
    
    # Define the CAN bus interface (you might need to change this to your CAN interface)
    bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000)  # Example for Linux

    # Continuously read messages from the CAN bus
    try:
        while True:
            # Receive a CAN message
            message = bus.recv()
            timestamp = message.timestamp
            msg_id = message.arbitration_id
            msg_data = message.data.hex()
            msg_type = 'Rx' if message.is_rx else 'Tx'
            
            # Format the message to match .asc format
            log_entry = '{:.6f} {} 0 8 {:#010x} 00 00 00 00 00 00 00 00 00 {}\n'.format(
                timestamp, msg_type, msg_id, msg_data)
            
            # Write the message to the log file
            f.write(log_entry)
            
            # Print to console as well (optional)
            print(log_entry)
            
            # Sleep to prevent too high CPU usage
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("Logging stopped by user.")
    
    # Write the footer to the ASC file
    f.write('end of logfile\n')
