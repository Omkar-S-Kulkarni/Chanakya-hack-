import os
import glob
import json
import argparse
import fitz  # PyMuPDF
import pdfplumber
import easyocr
import spacy
import re

# --- CONFIGURATION & INITIALIZATION ---
# Initialize the EasyOCR reader. Done once for efficiency.
print("Initializing EasyOCR Reader... (This may download models on first run)")
reader = easyocr.Reader(['en'])

# Load the SciSpacy model
try:
    nlp = spacy.load("en_core_sci_sm")
except OSError:
    print("SciSpacy model 'en_core_sci_sm' not found. Please ensure it's installed.")
    exit()

# --- HELPER FUNCTIONS (No changes needed) ---

def is_pdf_scanned(pdf_path: str) -> bool:
    """Checks if a PDF is scanned or digital."""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                if len(page.get_text().strip()) > 100:
                    return False
        return True
    except Exception as e:
        print(f"Error checking PDF type for {pdf_path}: {e}")
        return False

def extract_text_from_scanned_pdf(pdf_path: str) -> str:
    """Extracts text from a scanned PDF using EasyOCR."""
    full_text = ""
    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            results = reader.readtext(img_bytes)
            page_text = ' '.join([res[1] for res in results])
            full_text += page_text + "\n"
    return full_text

def extract_text_from_digital_pdf(pdf_path: str) -> str:
    """Extracts text from a digital PDF."""
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text

def clean_extracted_text(text: str) -> str:
    """Applies regex to clean up text."""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_medical_entities(text: str) -> dict:
    """Uses SciSpacy to perform NER on the text."""
    doc = nlp(text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    # You could add your lab result parsing here as well if needed
    return {"generic_entities": entities}

# --- MAIN PROCESSING LOGIC ---

def process_single_pdf(pdf_path: str) -> dict:
    """Processes one PDF file from start to finish."""
    try:
        is_scanned = is_pdf_scanned(pdf_path)
        raw_text = extract_text_from_scanned_pdf(pdf_path) if is_scanned else extract_text_from_digital_pdf(pdf_path)

        if not raw_text.strip():
            return {"error": "Could not extract any text from the document."}

        cleaned_text = clean_extracted_text(raw_text)
        structured_data = extract_medical_entities(cleaned_text)

        return {
            "source_file": os.path.basename(pdf_path),
            "is_scanned": is_scanned,
            "cleaned_text": cleaned_text,
            "extracted_data": structured_data
        }
    except Exception as e:
        return {"error": f"Failed to process file. Reason: {e}"}

def process_pdf_folder(input_folder: str, output_folder: str):
    """

    Finds and processes all .pdf files, saving each result to a new JSON file.
    """
    print(f"Searching for .pdf files in '{input_folder}'...")
    os.makedirs(output_folder, exist_ok=True)

    pdf_files = glob.glob(os.path.join(input_folder, "*.pdf"))

    if not pdf_files:
        print("No .pdf files found.")
        return

    for pdf_path in pdf_files:
        base_name = os.path.basename(pdf_path)
        output_filename = os.path.splitext(base_name)[0] + ".json"
        output_path = os.path.join(output_folder, output_filename)

        print(f"Processing '{base_name}' -> '{output_path}'...")
        result = process_single_pdf(pdf_path)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)

    print("\nBatch processing complete.")

# --- COMMAND-LINE INTERFACE ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch process PDF files and save outputs individually.")
    parser.add_argument("input_folder", type=str, help="The path to the folder containing .pdf files.")
    parser.add_argument("output_folder", type=str, help="The path to the folder where JSON outputs will be saved.")
    args = parser.parse_args()
    process_pdf_folder(args.input_folder, args.output_folder)