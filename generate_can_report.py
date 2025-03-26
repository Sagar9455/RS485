import pandas as pd

def parse_text_to_dataframe(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue  # Skip comments and empty lines
            
            parts = line.split('|')
            if len(parts) == 5:
                timestamp, can_id, dlc, data_bytes, msg_type = [p.strip() for p in parts]
                data.append([timestamp, can_id, int(dlc), data_bytes, msg_type])
    
    return pd.DataFrame(data, columns=['Timestamp', 'CAN ID', 'DLC', 'Data', 'Message Type'])

def save_to_excel(df, output_file):
    df.to_excel(output_file, index=False)
    print(f"Excel report saved: {output_file}")

if __name__ == "__main__":
    text_file = "zzzZ.asc"  # Ensure this file exists with structured data
    excel_file = "can_report.xlsx"
    df = parse_text_to_dataframe(text_file)
    save_to_excel(df, excel_file)
