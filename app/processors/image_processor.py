# File: app/processors/image_processor.py

import streamlit as st
import easyocr
import spacy
import re
import os

# --- NEW: Helper function to download SpaCy model ---
@st.cache_resource
def download_spacy_model():
    model_name = "en_core_sci_sm"
    try:
        spacy.load(model_name)
    except OSError:
        print(f"Downloading SpaCy model: {model_name}...")
        spacy.cli.download(model_name)
        print("Download complete.")
    return spacy.load(model_name)

# --- INITIALIZATION ---
print("Initializing EasyOCR Reader for image processing...")
reader = easyocr.Reader(['en'])

print("Loading SciSpacy model for image processing...")
nlp = download_spacy_model()
    
# --- HELPER FUNCTIONS ---
def clean_and_structure_text(text: str) -> dict:
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    doc = nlp(cleaned_text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    return {
        "cleaned_text": cleaned_text,
        "extracted_data": {"generic_entities": entities}
    }

# --- MAIN PROCESSOR FUNCTION ---
def process_image(image_path: str) -> dict:
    try:
        if not os.path.exists(image_path):
            return {"error": f"File not found: {image_path}"}
        results = reader.readtext(image_path)
        raw_text = ' '.join([res[1] for res in results])
        if not raw_text.strip():
            return {"error": "Could not extract any text from the image."}
        structured_result = clean_and_structure_text(raw_text)
        return {
            "source_file": os.path.basename(image_path),
            "cleaned_text": structured_result["cleaned_text"],
            "extracted_data": structured_result["extracted_data"]
        }
    except Exception as e:
        return {"error": f"An unexpected error occurred during image processing: {str(e)}"}