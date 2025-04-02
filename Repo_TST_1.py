import datetime

# Sample UDS log data
uds_log_data = [
    {"step": "16. Wait", "time": "2449.533827", "message": "Waited for 100.000 ms", "status": "-"},
    {"step": "17. Diagnostic Service", "time": "2449.533827", "message": "Set P2 to 3000ms, P2ex to 5000ms", "status": "Passed"},
    {"step": "", "time": "2449.535929", "message": "Request sent successfully", "status": "Pass"},
    {"step": "", "time": "2449.634271", "message": "Positive response received", "status": "Pass"},
]

# HTML Template with vTestStudio styling
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
    </style>
</head>
<body>
    <h2>UDS System Report</h2>
    <p>Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <table>
        <tr>
            <th>Step</th>
            <th>Timestamp</th>
            <th>Message</th>
            <th>Status</th>
        </tr>
"""

# Add log entries to table
for entry in uds_log_data:
    status_class = "passed" if "pass" in entry["status"].lower() else ""
    html_template += f"""
        <tr class="{status_class}">
            <td>{entry['step']}</td>
            <td>{entry['time']}</td>
            <td>{entry['message']}</td>
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
html_file_path = "/mnt/data/uds_report.html"
with open(html_file_path, "w") as file:
    file.write(html_template)

print(f"UDS HTML report generated: {html_file_path}")
