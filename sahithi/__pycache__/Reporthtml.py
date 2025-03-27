# Python script to generate an HTML report

def generate_html_report(report_title, data):
    # Define the HTML structure for the report
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{report_title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
            }}
            h1 {{
                color: #333;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            table, th, td {{
                border: 1px solid black;
            }}
            th, td {{
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
        </style>
    </head>
    <body>
        <h1>{report_title}</h1>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Name</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Add rows to the table
    for i, (name, value) in enumerate(data, start=1):
        html_content += f"""
            <tr>
                <td>{i}</td>
                <td>{name}</td>
                <td>{value}</td>
            </tr>
        """
    
    # Close the HTML tags
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    # Save the content to an HTML file
    with open("report.html", "w") as file:
        file.write(html_content)
    
    print("HTML report generated successfully: report.html")

# Example data to include in the report
data = [
    ("Item 1", "100"),
    ("Item 2", "200"),
    ("Item 3", "300"),
]

# Call the function to generate the report
generate_html_report("Sample Report", data)
