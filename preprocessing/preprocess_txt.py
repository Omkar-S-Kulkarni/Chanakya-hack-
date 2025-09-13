import os
import json
from typing import List, Dict, Union

def clean_text(text: str) -> str:
    """
    Cleans raw text:
    - Removes leading/trailing whitespace
    - Collapses multiple newlines into one
    - Collapses multiple spaces into one
    """
    text = text.strip()

    # Replace multiple newlines with one
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    # Replace multiple spaces with one
    while "  " in text:
        text = text.replace("  ", " ")

    return text


def preprocess_txt_file(file_path: str) -> Dict[str, Union[str, Dict]]:
    """
    Preprocess a single .txt file and return JSON-like dict.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()

        cleaned_text = clean_text(raw_text)

        return {
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "type": "text",
            "content": cleaned_text
        }
    except Exception as e:
        return {
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "type": "error",
            "content": str(e)
        }


def preprocess_txt_folder(folder_path: str) -> List[Dict]:
    """
    Process all .txt files in a folder.
    """
    results = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(".txt"):
            file_path = os.path.join(folder_path, file)
            results.append(preprocess_txt_file(file_path))
    return results


def preprocess_inputs(paths: List[str], output_json: str = "txt_output.json"):
    """
    Process multiple files and/or folders.
    """
    all_results = []

    for path in paths:
        if os.path.isfile(path) and path.lower().endswith(".txt"):
            all_results.append(preprocess_txt_file(path))

        elif os.path.isdir(path):
            all_results.extend(preprocess_txt_folder(path))

        else:
            all_results.append({
                "file_name": os.path.basename(path),
                "file_path": path,
                "type": "error",
                "content": "Not a .txt file or valid folder"
            })

    # Save combined results
    with open(output_json, "w", encoding="utf-8") as out:
        json.dump(all_results, out, indent=4, ensure_ascii=False)

    print(f" Processed {len(all_results)} text entries. Output saved to {output_json}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Preprocess .txt files")
    parser.add_argument("paths", nargs="+", help="One or more .txt files or folders containing .txt files")
    parser.add_argument("--out", default="txt_output.json", help="Output JSON file")
    args = parser.parse_args()

    preprocess_inputs(args.paths, args.out)
