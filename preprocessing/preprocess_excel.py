import os
import glob
import json
import argparse
import pandas as pd

# --- CONFIGURATION & HELPER FUNCTIONS (No changes needed) ---
COLUMN_NAME_MAPPING = {
    'date': 'date', 'timestamp': 'date', 'day': 'date',
    'systolic': 'systolic', 'sys': 'systolic', 'bp_sys': 'systolic',
    'diastolic': 'diastolic', 'dia': 'diastolic', 'bp_dia': 'diastolic',
    'glucose': 'glucose', 'blood_sugar': 'glucose', 'gl': 'glucose',
}

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renames DataFrame columns to a standard format."""
    df.columns = df.columns.str.lower().str.strip()
    renamed_columns = {col: COLUMN_NAME_MAPPING[col] for col in df.columns if col in COLUMN_NAME_MAPPING}
    df = df.rename(columns=renamed_columns)
    standard_columns = list(set(COLUMN_NAME_MAPPING.values()))
    columns_to_keep = [col for col in df.columns if col in standard_columns]
    return df[columns_to_keep]

# --- MAIN PROCESSING LOGIC ---
def process_single_spreadsheet(file_path: str) -> dict:
    """Processes a single spreadsheet file."""
    try:
        file_extension = file_path.rsplit('.', 1)[1].lower()
        df = pd.read_excel(file_path) if file_extension in ['xlsx', 'xls'] else pd.read_csv(file_path)

        if df.empty: return {"error": "Spreadsheet is empty."}
        normalized_df = normalize_columns(df)
        if normalized_df.empty: return {"error": "No recognizable columns found."}

        return {
            "source_file": os.path.basename(file_path),
            "records": normalized_df.to_dict(orient='records')
        }
    except Exception as e:
        return {"error": f"Failed to process file. Reason: {e}"}

def process_excel_folder(input_folder: str, output_folder: str):
    """Finds and processes all spreadsheets, saving each result to a new JSON file."""
    print(f"Searching for spreadsheets in '{input_folder}'...")
    os.makedirs(output_folder, exist_ok=True)
    
    file_patterns = ["*.xlsx", "*.xls", "*.csv"]
    files_to_process = []
    for pattern in file_patterns:
        files_to_process.extend(glob.glob(os.path.join(input_folder, pattern)))
    
    if not files_to_process:
        print("No spreadsheet files found.")
        return

    for file_path in files_to_process:
        base_name = os.path.basename(file_path)
        output_filename = os.path.splitext(base_name)[0] + ".json"
        output_path = os.path.join(output_folder, output_filename)

        print(f"Processing '{base_name}' -> '{output_path}'...")
        result = process_single_spreadsheet(file_path)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
            
    print("\nBatch processing complete.")

# --- COMMAND-LINE INTERFACE ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch process spreadsheets and save outputs individually.")
    parser.add_argument("input_folder", type=str, help="The path to the folder containing spreadsheet files.")
    parser.add_argument("output_folder", type=str, help="The path to the folder where JSON outputs will be saved.")
    
    args = parser.parse_args()
    process_excel_folder(args.input_folder, args.output_folder)