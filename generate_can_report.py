import pandas as pd
import re

def parse_asc_to_dataframe(asc_file):
    data = []
    with open(asc_file, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            match = re.match(r'^(\d+\.\d+)\s+(\d+)\s+Rx\s+(0x[0-9A-Fa-f]+)\s+(\d)\s+([0-9A-Fa-f ]+)', line)
            if match:
                timestamp, channel, can_id, dlc, data_bytes = match.groups()
                data.append([float(timestamp), channel, can_id, int(dlc), data_bytes.strip()])
    
    return pd.DataFrame(data, columns=['Timestamp', 'Channel', 'CAN ID', 'DLC', 'Data'])

def save_to_excel(df, output_file):
    df.to_excel(output_file, index=False)
    print(f"Excel report saved: {output_file}")

if __name__ == "__main__":
    asc_file = "Rasp_can_log3.asc"  # Ensure this file exists
    excel_file = "can_report.xlsx"
    df = parse_asc_to_dataframe(asc_file)
    save_to_excel(df, excel_file)
