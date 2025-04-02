def get_ecu_information():
    """Retrieve and display ECU information."""
    os.system('sudo ip link set can0 up type can bitrate 500000 dbitrate 1000000 restart-ms 1000 berr-reporting on fd on')
    os.system('sudo ifconfig can0 up')

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

    isotp_params = {
        'stmin': 32,
        'blocksize': 8,
        'wftmax': 0,
        'tx_padding': 0x00,
        'rx_flowcontrol_timeout': 1000,
        'rx_consecutive_frame_timeout': 1000,
        'max_frame_size': 4095,
        'can_fd': True,    
        'bitrate_switch': True
    }

    config = dict(udsoncan.configs.default_client_config)
    config["ignore_server_timing_requirements"] = True
    config["data_identifiers"] = {
        0xF100: udsoncan.AsciiCodec(8),
        0xF101: udsoncan.AsciiCodec(8),
        0xF187: udsoncan.AsciiCodec(13),
        0xF1AA: udsoncan.AsciiCodec(13),
        0xF1B1: udsoncan.AsciiCodec(13),
        0xF193: udsoncan.AsciiCodec(13),
        0xF120: udsoncan.AsciiCodec(16),
        0xF18B: udsoncan.AsciiCodec(8),
        0xF102: udsoncan.AsciiCodec(13) 
    }

    interface = "can0"
    bus = can.interface.Bus(channel=interface, bustype="socketcan", fd=True)
    bus.set_filters([{"can_id":0x7A8,"can_mask":0xFFF}])
    tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=0x7A0, rxid=0x7A8)
    stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)
    conn = PythonIsoTpConnection(stack)

    test_report = []

    with Client(conn, request_timeout=2, config=config) as client:
        logging.info("UDS Client Started")
        try:
            client.tester_present()
            logging.info("Tester Present sent successfully")
        except Exception as e:
            logging.warning(f"Tester Present failed: {e}")

        for did in config["data_identifiers"]:
            try:
                logging.info(f"Sending request for DID {hex(did)}")
                response = client.read_data_by_identifier(did)
                test_report.append({
                    'request': f'0x22 {hex(did)}',
                    'request_status': 'Pass',
                    'response_status': 'Pass' if response.positive else 'Fail'
                })
            except Exception as e:
                logging.error(f"Error reading ECU information (DID {hex(did)}): {e}")
                test_report.append({
                    'request': f'0x22 {hex(did)}',
                    'request_status': 'Fail',
                    'response_status': 'Fail'
                })

        logging.info("UDS Client Closed")
    
    generate_html_report(test_report)

def generate_html_report(test_report):
    """Generates an HTML report with request status and response status."""
    html_content = """
    <html>
    <head>
        <title>ECU Diagnostic Report</title>
        <style>
            table { width: 100%%; border-collapse: collapse; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h2>ECU Diagnostic Report</h2>
        <table>
            <tr>
                <th>Request</th>
                <th>Request Status</th>
                <th>Response Status</th>
            </tr>
    """
    for entry in test_report:
        html_content += f"""
        <tr>
            <td>{entry['request']}</td>
            <td>{entry['request_status']}</td>
            <td>{entry['response_status']}</td>
        </tr>
        """
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open("ecu_report.html", "w") as report_file:
        report_file.write(html_content)
    logging.info("ECU diagnostic report generated successfully.")
