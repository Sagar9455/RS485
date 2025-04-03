import datetime

# Sample UDS diagnostic log data (replace with actual parsed data)
uds_log_data = [
    {"step": 16, "type": "Wait", "details": "Waited for 100.000 ms", "status": "-"},
    {"step": 17, "type": "Diagnostic Service", "details": "Set P2 to 3000ms, P2ex to 5000ms", "status": "Passed"},
    {"step": 17, "type": "Request", "details": "Sending request to MSW_27770110", "status": "Sent"},
    {"step": 17, "type": "Response", "details": "Positive response received", "status": "Pass"},
]

# HTML Template
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>UDS System Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .pass {{ color: green; }}
        .fail {{ color: red; }}
    </style>
</head>
<body>
    <h2>UDS System Report</h2>
    <p>Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <table>
        <tr>
            <th>Step</th>
            <th>Type</th>
            <th>Details</th>
            <th>Status</th>
        </tr>
"""

# Populate table rows
for entry in uds_log_data:
    status_class = "pass" if "pass" in entry["status"].lower() else "fail"
    html_template += f"""
        <tr>
            <td>{entry['step']}</td>
            <td>{entry['type']}</td>
            <td>{entry['details']}</td>
            <td class="{status_class}">{entry['status']}</td>
        </tr>
    """

# Close HTML
html_template += """
    </table>
</body>
</html>
"""

# Save the report
with open("uds_report.html", "w") as file:
    file.write(html_template)

print("UDS HTML report generated: uds_report.html")
