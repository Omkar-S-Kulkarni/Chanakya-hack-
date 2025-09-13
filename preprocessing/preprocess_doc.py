import os
import glob
import json
import argparse
import docx
import spacy
import re

# --- CONFIGURATION & INITIALIZATION ---
try:
    nlp = spacy.load("en_core_sci_sm")
except OSError:
    print("SciSpacy model 'en_core_sci_sm' not found. Please ensure it's installed.")
    exit()

# --- HELPER FUNCTIONS (No changes needed) ---

def clean_extracted_text(text: str) -> str:
    """Applies regex to clean up text."""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_medical_entities(text: str) -> dict:
    """Uses SciSpacy to perform NER on the text."""
    doc = nlp(text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    return {"generic_entities": entities}

# --- MAIN PROCESSING LOGIC ---

def process_single_doc(doc_path: str) -> dict:
    """Processes a single .docx file."""
    try:
        document = docx.Document(doc_path)
        full_text = "\n".join([para.text for para in document.paragraphs])
        
        if not full_text.strip():
            return {"error": "Document is empty."}

        cleaned_text = clean_extracted_text(full_text)
        structured_data = extract_medical_entities(cleaned_text)
        
        return {
            "source_file": os.path.basename(doc_path),
            "cleaned_text": cleaned_text,
            "extracted_data": structured_data
        }
    except Exception as e:
        return {"error": f"Failed to process file. Reason: {e}"}

def process_doc_folder(input_folder: str, output_folder: str):
    """
    Finds and processes all .docx files, saving each result to a new JSON file.
    """
    print(f"Searching for .docx files in '{input_folder}'...")
    # Create the output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    doc_files = glob.glob(os.path.join(input_folder, "*.docx"))
    
    if not doc_files:
        print("No .docx files found.")
        return

    for doc_path in doc_files:
        base_name = os.path.basename(doc_path)
        output_filename = os.path.splitext(base_name)[0] + ".json"
        output_path = os.path.join(output_folder, output_filename)
        
        print(f"Processing '{base_name}' -> '{output_path}'...")
        
        result = process_single_doc(doc_path)
        
        # Write the result for this single file to its own JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
            
    print("\nBatch processing complete.")

# --- COMMAND-LINE INTERFACE ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch process .docx files and save outputs individually.")
    parser.add_argument("input_folder", type=str, help="The path to the folder containing .docx files.")
    parser.add_argument("output_folder", type=str, help="The path to the folder where JSON outputs will be saved.")
    
    args = parser.parse_args()
    process_doc_folder(args.input_folder, args.output_folder)