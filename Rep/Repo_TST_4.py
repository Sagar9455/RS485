import datetime

# Sample structured UDS log data (each request-response grouped)
uds_log_data = [
    {
        "step": "11. Diagnostic Service",
        "time": "2445.661885",
        "details": [
            {"message": "Set P2 to 3000ms, P2ex to 5000ms", "status": "-"},
            {"message": "Sending request '/MSW_27770110/P1ALA_Read/RQ_P1ALA_Read'", "status": "-"},
            {"message": "Request sent successfully", "status": "pass"},
            {"message": "Receiving diagnostic response", "status": "-"},
            {"message": "Resume on Diagnostics response from 'MSW_27770110'", "status": "-"},
            {"message": "Positive response received", "status": "pass"},
            {"message": "Received primitive can be interpreted as diagnostic primitive 'PR_P1ALA_Read'", "status": "-"},
        ],
        "status": "Passed"
    }
]

# HTML template for the report
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>UDS System Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
        th {{ background-color: #4d4d4d; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        tr:nth-child(odd) {{ background-color: #d9d9d9; }}
        .passed {{ background-color: #4CAF50; color: white; }}
        .failed {{ background-color: #FF6347; color: white; }}
    </style>
</head>
<body>
    <h2>UDS System Report</h2>
    <p>Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <table>
        <tr>
            <th>Step</th>
            <th>Timestamp</th>
            <th>Details</th>
            <th>Status</th>
        </tr>
"""

# Add log entries to table
for entry in uds_log_data:
    status_class = "passed" if "pass" in entry["status"].lower() else "failed"
    html_template += f"""
        <tr class="{status_class}">
            <td>{entry['step']}</td>
            <td>{entry['time']}</td>
            <td>
                <ul>
    """
    for detail in entry["details"]:
        html_template += f"<li>{detail['message']}</li>"

    html_template += """
                </ul>
            </td>
            <td>{entry['status']}</td>
        </tr>
    """

# Close HTML structure
html_template += """
    </table>
</body>
</html>
"""

# Save the HTML file
html_file_path = "/home/mobase/Testz/Rep/uds_report_4.html"
with open(html_file_path, "w") as file:
    file.write(html_template)

print(f"UDS HTML report generated: {html_file_path}")
