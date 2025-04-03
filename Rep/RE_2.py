import pandas as pd
from datetime import datetime

def generate_html_report(data, output_file="DID_Report.html"):
    html_template = f"""
    <html>
    <head>
        <title>DID Read Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
            th {{ background-color: green; color: white; }}
            .pass {{ background-color: #d0f0c0; }}
            .fail {{ background-color: #f8d7da; }}
            h2 {{ text-align: center; }}
        </style>
    </head>
    <body>
        <h2>DID Read Test Report</h2>
        <table>
            <tr>
                <th>DID</th>
                <th>Response</th>
                <th>Status</th>
                <th>Timestamp</th>
            </tr>
    """
    
    for entry in data:
        did, response, status, timestamp = entry
        row_class = "pass" if status == "Pass" else "fail"
        html_template += f"""
            <tr class='{row_class}'>
                <td>{did}</td>
                <td>{response}</td>
                <td>{status}</td>
                <td>{timestamp}</td>
            </tr>
        """
    
    html_template += """
        </table>
    </body>
    </html>
    """
    
    with open(output_file, "w") as file:
        file.write(html_template)
    
    print(f"Report generated: {output_file}")

# Example data: (DID, Response, Status, Timestamp)
data = [
    ("0xF190", "123456789ABCDEF", "Pass", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    ("0xF18C", "Error: No response", "Fail", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    ("0xF195", "9876543210ABCDEF", "Pass", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
]

generate_html_report(data)
