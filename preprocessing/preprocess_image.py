import os
import cv2
import easyocr
import spacy
import re
import json

# --- CONFIGURATION ---
image_folder = r"C:\Users\svks6\Chanakya-hack-\data\sample_images"
output_folder = r"C:\Users\svks6\Chanakya-hack-\preprocessing\ocr_results"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Initialize EasyOCR
print("Initializing EasyOCR Reader... (This may download models on first run)")
reader = easyocr.Reader(['en'])

# Load SciSpacy model
try:
    nlp = spacy.load("en_core_sci_sm")
except OSError:
    print("SciSpacy model 'en_core_sci_sm' not found. Please install it.")
    exit()

# --- HELPER FUNCTIONS ---

def preprocess_image_for_ocr(image_path: str):
    img = cv2.imread(image_path)
    # Optional preprocessing can be added here (grayscale, thresholding, etc.)
    return img

def clean_extracted_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_medical_entities(text: str) -> dict:
    doc = nlp(text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    return {"generic_entities": entities}

def process_image(image_path: str) -> dict:
    print(f"Processing image '{image_path}'...")
    try:
        # Stage 1: Preprocess
        processed_img = preprocess_image_for_ocr(image_path)
        
        # Stage 2: OCR
        results = reader.readtext(processed_img)
        raw_text = ' '.join([res[1] for res in results])
        if not raw_text.strip():
            return {"error": "Could not extract any text from the image."}
        
        # Stage 3: Clean text
        cleaned_text = clean_extracted_text(raw_text)
        
        # Stage 4: NER
        structured_data = extract_medical_entities(cleaned_text)
        
        # Final output
        return {
            "file_name": image_path,
            "cleaned_text": cleaned_text,
            "extracted_data": structured_data
        }
    except Exception as e:
        print(f"Error processing '{image_path}': {e}")
        return {"error": str(e), "file_name": image_path}

# --- MAIN SCRIPT ---

if __name__ == '__main__':
    if not os.path.exists(image_folder):
        print(f"Error: Folder '{image_folder}' not found.")
        exit()
    
    for image_file in os.listdir(image_folder):
        if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder, image_file)
            result = process_image(image_path)
            
            # Save JSON result
            json_filename = os.path.splitext(image_file)[0] + ".json"
            output_path = os.path.join(output_folder, json_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            
            print(f"Processed '{image_file}' → Saved JSON: '{output_path}'\n")
