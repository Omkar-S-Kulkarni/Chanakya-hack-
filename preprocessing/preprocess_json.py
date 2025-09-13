import os
import glob
import json
import argparse

def process_single_json(file_path: str) -> dict:
    """Processes a single JSON file, wrapping it with metadata."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # We wrap the original data with metadata
        return {
            "source_file": os.path.basename(file_path),
            "original_data": data
        }
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format."}
    except Exception as e:
        return {"error": f"Failed to read file. Reason: {e}"}

def process_json_folder(input_folder: str, output_folder: str):
    """Finds and processes all .json files, saving each to a new JSON file."""
    print(f"Searching for .json files in '{input_folder}'...")
    os.makedirs(output_folder, exist_ok=True)
    
    json_files = glob.glob(os.path.join(input_folder, "*.json"))
    
    if not json_files:
        print("No .json files found.")
        return

    for file_path in json_files:
        base_name = os.path.basename(file_path)
        # The output filename will be the same as the input
        output_path = os.path.join(output_folder, base_name)

        print(f"Processing '{base_name}' -> '{output_path}'...")
        result = process_single_json(file_path)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
            
    print("\nBatch processing complete.")

# --- COMMAND-LINE INTERFACE ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch process JSON files and save outputs individually.")
    parser.add_argument("input_folder", type=str, help="The path to the folder containing .json files.")
    parser.add_argument("output_folder", type=str, help="The path to the folder where new JSON files will be saved.")
    
    args = parser.parse_args()
    process_json_folder(args.input_folder, args.output_folder)