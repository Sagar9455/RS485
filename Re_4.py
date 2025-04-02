import time
import RPi.GPIO as GPIO
from udsoncan.client import Client
from udsoncan.connections import IsoTPConnection
import isotp
import can

# Setup GPIO button
BUTTON_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Setup CAN bus
bus = can.interface.Bus("can0", bustype="socketcan")
isotp_layer = isotp.CanStack(bus, txid=0x7E0, rxid=0x7E8)
conn = IsoTPConnection(isotp_layer)
client = Client(conn)

def generate_report(request_status, response_status):
    html_content = f"""
    <html>
    <head>
        <style>
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
            .pass {{ background-color: lightgreen; }}
            .fail {{ background-color: lightcoral; }}
        </style>
    </head>
    <body>
        <h2>UDS Diagnostic Report</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Action</th>
                <th>Status</th>
            </tr>
            <tr class="{request_status.lower()}">
                <td>{time.time()}</td>
                <td>Request Sent</td>
                <td>{request_status}</td>
            </tr>
            <tr class="{response_status.lower()}">
                <td>{time.time()}</td>
                <td>Positive Response Received</td>
                <td>{response_status}</td>
            </tr>
        </table>
    </body>
    </html>
    """
    with open("DID_Report.html", "w") as file:
        file.write(html_content)
    print("Report generated: DID_Report.html")

try:
    print("Waiting for button press...")
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            print("Button pressed! Sending UDS request...")
            request_status = "Pass"
            response_status = "Fail"
            try:
                response = client.change_request(0x22, [0xF1, 0x90])
                if response.positive:
                    response_status = "Pass"
            except Exception as e:
                print(f"Error: {e}")
                request_status = "Fail"
            generate_report(request_status, response_status)
            time.sleep(1)  # Prevent multiple detections
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()
