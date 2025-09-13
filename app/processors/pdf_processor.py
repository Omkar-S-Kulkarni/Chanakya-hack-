# File: app/processors/pdf_processor.py

import streamlit as st
import fitz  # PyMuPDF
import pdfplumber
import easyocr
import spacy
import re
import os

# --- NEW: Helper function to download SpaCy model ---
@st.cache_resource
def download_spacy_model():
    model_name = "en_core_sci_sm"
    try:
        # Check if model is already loaded
        spacy.load(model_name)
    except OSError:
        # If not, download it
        print(f"Downloading SpaCy model: {model_name}...")
        spacy.cli.download(model_name)
        print("Download complete.")
    return spacy.load(model_name)

# --- INITIALIZATION ---
print("Initializing EasyOCR Reader for PDF processing...")
reader = easyocr.Reader(['en'])

print("Loading SciSpacy model for PDF processing...")
# Call the helper function to ensure the model is available
nlp = download_spacy_model()

# --- HELPER FUNCTIONS ---
def is_pdf_scanned(pdf_path: str) -> bool:
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
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text

def clean_and_structure_text(text: str) -> dict:
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    doc = nlp(cleaned_text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    return {
        "cleaned_text": cleaned_text,
        "extracted_data": {"generic_entities": entities}
    }

# --- MAIN PROCESSOR FUNCTION ---
def process_pdf(pdf_path: str) -> dict:
    try:
        if not os.path.exists(pdf_path):
            return {"error": f"File not found: {pdf_path}"}
        is_scanned = is_pdf_scanned(pdf_path)
        raw_text = extract_text_from_scanned_pdf(pdf_path) if is_scanned else extract_text_from_digital_pdf(pdf_path)
        if not raw_text.strip():
            return {"error": "Could not extract any text from the document."}
        structured_result = clean_and_structure_text(raw_text)
        return {
            "source_file": os.path.basename(pdf_path),
            "is_scanned": is_scanned,
            "cleaned_text": structured_result["cleaned_text"],
            "extracted_data": structured_result["extracted_data"]
        }
    except Exception as e:
        return {"error": f"An unexpected error occurred during PDF processing: {str(e)}"}