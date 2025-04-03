import os

def generate_html_report(test_report, output_file="uds_test_report.html"):
    """
    Generates an HTML report from the UDS test report list.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>UDS Test Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid black; padding: 10px; text-align: left; }
            th { background-color: #f2f2f2; }
            .pass { background-color: #d4edda; }
            .fail { background-color: #f8d7da; }
        </style>
    </head>
    <body>
        <h2>UDS Test Report</h2>
        <table>
            <tr>
                <th>Request</th>
                <th>Expected Response</th>
                <th>Actual Response</th>
                <th>Status</th>
            </tr>
    """

    for test in test_report:
        request = test.get("request", "N/A")
        expected_response = test.get("expected_response", "N/A")
        actual_response = test.get("actual_response", "N/A")
        status = test.get("status", "N/A")
        status_class = "pass" if status == "PASS" else "fail"

        html_content += f"""
            <tr class='{status_class}'>
                <td>{request}</td>
                <td>{expected_response}</td>
                <td>{actual_response}</td>
                <td>{status}</td>
            </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    with open(output_file, "w") as f:
        f.write(html_content)

    print(f"HTML report generated: {output_file}")

# Example usage:
if __name__ == "__main__":
    test_data = [
        {"request": "0x10 0x01", "expected_response": "0x50 0x01", "actual_response": "0x50 0x01", "status": "PASS"},
        {"request": "0x10 0x03", "expected_response": "0x50 0x03", "actual_response": "0x50 0x03", "status": "PASS"},
        {"request": "0x22 0xF1 0x90", "expected_response": "0x62 0xF1 0x90 0x12 0x34", "actual_response": "0x62 0xF1 0x90 0x12 0x34", "status": "PASS"},
        {"request": "0x22 0xF1 0xA0", "expected_response": "0x62 0xF1 0xA0 0x56 0x78", "actual_response": "0x7F 0x22 0x31", "status": "FAIL"}
    ]

    generate_html_report(test_data)
