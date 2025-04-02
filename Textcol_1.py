<!DOCTYPE html>
<html>
<head>
    <title>UDS Diagnostic Report</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; }
        table { width: 80%; border-collapse: collapse; margin: 20px auto; }
        th, td { border: 1px solid black; padding: 10px; text-align: center; }
        th { background-color: #8a8a8a; color: black; font-weight: bold; } /* Darker Grey Header */
        .pass { background-color: #c8e6c9; color: green; }
        .fail { background-color: #ffcdd2; color: red; }
        .section-title { background-color: #e0e0e0; } /* Light Grey Section */
    </style>
</head>
<body>
    <h2>UDS Diagnostic Report</h2>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Description</th>
            <th>Step</th>
            <th>Status</th>
        </tr>
        <tr class="section-title">
            <td rowspan="2">2025-04-02 18:19:35</td>
            <td rowspan="2">Default Session (0x10 0x01)</td>
            <td>Request Sent</td>
            <td class="pass">Pass</td>
        </tr>
        <tr class="section-title">
            <td>Positive Response Received</td>
            <td class="pass">Pass</td>
        </tr>
        <tr class="section-title">
            <td rowspan="2">2025-04-02 18:19:35</td>
            <td rowspan="2">Extended Session (0x10 0x03)</td>
            <td>Request Sent</td>
            <td class="pass">Pass</td>
        </tr>
        <tr class="section-title">
            <td>Positive Response Received</td>
            <td class="pass">Pass</td>
        </tr>
        <tr class="section-title">
            <td rowspan="2">2025-04-02 18:19:36</td>
            <td rowspan="2">Read DID (0xF190)</td>
            <td>Request Sent</td>
            <td class="fail">Fail</td>
        </tr>
        <tr class="section-title">
            <td>Positive Response Received</td>
            <td class="fail">Fail</td>
        </tr>
    </table>
</body>
</html>
