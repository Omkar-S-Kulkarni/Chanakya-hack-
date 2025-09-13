import easyocr
import spacy
import re
import os

# --- INITIALIZATION (Done once when the app starts) ---
print("Initializing EasyOCR Reader for image processing...")
try:
    reader = easyocr.Reader(['en'])
except Exception as e:
    print(f"Error initializing EasyOCR: {e}")
    reader = None

print("Loading SciSpacy model for image processing...")
try:
    nlp = spacy.load("en_core_sci_sm")
except OSError:
    print("CRITICAL: SciSpacy model 'en_core_sci_sm' not found.")
    nlp = None
    
# --- HELPER FUNCTIONS ---

def clean_and_structure_text(text: str) -> dict:
    """Cleans text and extracts medical entities."""
    if not nlp:
        raise ConnectionError("SciSpacy model is not available.")
        
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    doc = nlp(cleaned_text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    
    return {
        "cleaned_text": cleaned_text,
        "extracted_data": {"generic_entities": entities}
    }

# --- MAIN PROCESSOR FUNCTION ---

def process_image(image_path: str) -> dict:
    """
    Main function to process a single image file.
    Called by the Flask app.
    """
    try:
        if not os.path.exists(image_path):
            return {"error": f"File not found: {image_path}"}
        if not reader:
            raise ConnectionError("EasyOCR reader is not available.")

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