import os
import can
import time
from datetime import datetime

# Set up CAN interface (Modify based on your setup)
os.system("sudo ip link set can0 up type can bitrate 500000")
bus = can.interface.Bus(channel='can0', bustype='socketcan')

def send_uds_request(did):
    """Send UDS ReadDataByIdentifier request."""
    request_id = 0x8A0  # Modify according to ECU CAN ID
    request_data = [0x22, (did >> 8) & 0xFF, did & 0xFF]
    msg = can.Message(arbitration_id=request_id, data=request_data, is_extended_id=True)
    bus.send(msg)

def receive_uds_response():
    """Receive and parse UDS response."""
    response_id = 0x8A8  # Modify based on ECU response ID
    timeout = 2  # Timeout for response in seconds
    start_time = time.time()
    while time.time() - start_time < timeout:
        msg = bus.recv(timeout)
        if msg and msg.arbitration_id == response_id:
            return msg.timestamp, msg.data[2:]
    return None, None

def generate_report(did_list):
    """Generate an HTML report based on UDS responses."""
    report_data = []
    for did in did_list:
        send_uds_request(did)
        timestamp, response_data = receive_uds_response()
        if response_data:
            response_str = ''.join(f'{byte:02X}' for byte in response_data)
            status = "Pass"
            row_class = "pass-row"
        else:
            response_str = "Error: No response"
            status = "Fail"
            row_class = "fail-row"
        
        report_data.append((f'0x{did:04X}', response_str, status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), row_class))
    
    # HTML Template
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            table { border-collapse: collapse; width: 80%; margin: auto; }
            th, td { border: 1px solid black; padding: 10px; text-align: center; }
            th { background-color: green; color: white; }
            .pass-row { background-color: #d4edda; }
            .fail-row { background-color: #f8d7da; }
        </style>
    </head>
    <body>
        <h2 style='text-align:center;'>DID Read Test Report</h2>
        <table>
            <tr>
                <th>DID</th>
                <th>Response</th>
                <th>Status</th>
                <th>Timestamp</th>
            </tr>
    """
    for did, response, status, timestamp, row_class in report_data:
        html_content += f"""
            <tr class='{row_class}'>
                <td>{did}</td>
                <td>{response}</td>
                <td>{status}</td>
                <td>{timestamp}</td>
            </tr>
        """
    html_content += """
        </table>
    </body>
    </html>
    """
    
    # Save Report
    with open("DID_Report.html", "w") as file:
        file.write(html_content)
    print("Report generated: DID_Report.html")

# List of DIDs to request
did_list = [0xF190, 0xF18C, 0xF195]
generate_report(did_list)
