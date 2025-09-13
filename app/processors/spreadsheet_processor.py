import pandas as pd
import os

# --- CONFIGURATION ---
COLUMN_NAME_MAPPING = {
    'date': 'date', 'timestamp': 'date', 'day': 'date',
    'systolic': 'systolic', 'sys': 'systolic', 'bp_sys': 'systolic',
    'diastolic': 'diastolic', 'dia': 'diastolic', 'bp_dia': 'diastolic',
    'glucose': 'glucose', 'blood_sugar': 'glucose', 'gl': 'glucose',
}

# --- HELPER FUNCTIONS ---

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renames DataFrame columns to a standard format."""
    df.columns = df.columns.str.lower().str.strip()
    renamed_columns = {col: COLUMN_NAME_MAPPING[col] for col in df.columns if col in COLUMN_NAME_MAPPING}
    df = df.rename(columns=renamed_columns)
    
    standard_columns = list(set(COLUMN_NAME_MAPPING.values()))
    columns_to_keep = [col for col in df.columns if col in standard_columns]
    return df[columns_to_keep]

# --- MAIN PROCESSOR FUNCTION ---

def process_spreadsheet(file_path: str) -> dict:
    """
    Main function to process a single spreadsheet file.
    Called by the Flask app.
    """
    try:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
            
        file_extension = file_path.rsplit('.', 1)[1].lower()
        df = pd.read_excel(file_path) if file_extension in ['xlsx', 'xls'] else pd.read_csv(file_path)

        if df.empty:
            return {"error": "Spreadsheet is empty."}
            
        normalized_df = normalize_columns(df)

        if normalized_df.empty:
            return {"error": "Spreadsheet does not contain recognizable columns (e.g., 'date', 'systolic', 'glucose')."}

        # Convert to a JSON-serializable format
        records = normalized_df.to_dict(orient='records')
        
        return {
            "source_file": os.path.basename(file_path),
            "data_type": "structured_log",
            "records": records
        }
    except Exception as e:
        return {"error": f"An unexpected error occurred during spreadsheet processing: {str(e)}"}