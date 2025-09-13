import os
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import our modules
from processors.pdf_processor import process_pdf
from processors.image_processor import process_image
from processors.spreadsheet_processor import process_spreadsheet
from rule_engine import RuleEngine
from gemini_agent import GeminiAgent
from evaluation_agent import EvaluationAgent # <-- IMPORT AGENT 2

load_dotenv()

# --- CONFIGURATION ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'xlsx', 'xls', 'csv'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- INITIALIZE MODULES (SINGLETONS) ---
print("Initializing all modules...")
rule_engine = RuleEngine()
gemini_agent_1 = GeminiAgent(api_key=os.getenv("GOOGLE_API_KEY"))
evaluation_agent_2 = EvaluationAgent(api_key=os.getenv("GOOGLE_API_KEY")) # <-- INITIALIZE AGENT 2
print("Initialization complete. Server is ready.")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/api/unified_analysis', methods=['POST'])
def unified_analysis():
    """A single, powerful endpoint to handle all agent tasks."""
    print("\n--- NEW REQUEST RECEIVED ---")
    
    agent_type = request.form.get('agent_type')
    json_data_string = request.form.get('json_data', '{}')
    
    print(f"Agent Type Received: {agent_type}")
    print(f"JSON Data String Received: {json_data_string}")

    try:
        data = json.loads(json_data_string)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data provided in the form."}), 400

    file_path = None
    processed_file_data = None
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_subfolder = os.path.join(app.config['UPLOAD_FOLDER'], agent_type)
            os.makedirs(upload_subfolder, exist_ok=True)
            file_path = os.path.join(upload_subfolder, filename)
            file.save(file_path)

            print(f"File '{filename}' saved. Processing...")
            ext = filename.rsplit('.', 1)[1].lower()
            
            if ext == 'pdf':
                processed_file_data = process_pdf(file_path)
            elif ext in {'png', 'jpg', 'jpeg'}:
                processed_file_data = process_image(file_path)
            elif ext in {'xlsx', 'xls', 'csv'}:
                 processed_file_data = process_spreadsheet(file_path)
        else:
            return jsonify({"error": "File type not allowed."}), 400

    # --- AGENT 1: ANALYSIS ---
    agent1_result = {}
    print(f"Routing to agent: {agent_type}")
    
    if agent_type == 'drug_safety':
        medications = data.get('medications', [])
        safety_alerts = rule_engine.run_all_checks(drug_names=medications)
        agent1_result = gemini_agent_1.run_drug_safety_agent(data, safety_alerts)
    elif agent_type == 'translator':
        text_content = processed_file_data.get('cleaned_text', '') if processed_file_data else ''
        agent1_result = gemini_agent_1.run_translator_agent(text_content=text_content, image_path=file_path)
    elif agent_type == 'symptom_triage':
        symptom_text = data.get('symptoms', '')
        red_flag_alerts = rule_engine.run_all_checks(symptom_text=symptom_text)
        agent1_result = gemini_agent_1.run_symptom_triage_agent(data, red_flag_alerts)
    elif agent_type == 'chronic_care':
        records = processed_file_data.get('records', []) if processed_file_data else []
        agent1_result = gemini_agent_1.run_chronic_care_agent(records)
    elif agent_type == 'doctors_copilot':
        note = data.get('note', '')
        agent1_result = gemini_agent_1.run_doctors_copilot_agent(note)
    else:
        return jsonify({"error": f"Unknown agent_type: {agent_type}"}), 400
    
    # --- AGENT 2: EVALUATION ---
    print("Passing Agent 1 output to Agent 2 for evaluation...")
    agent2_evaluation = evaluation_agent_2.evaluate_output(agent1_result)

    # --- FINAL COMBINED RESPONSE ---
    final_response = {
        "agent1_analysis": agent1_result,
        "agent2_evaluation": agent2_evaluation
    }

    print("--- REQUEST COMPLETED SUCCESSFULLY ---")
    return jsonify(final_response)

if __name__ == '__main__':
    app.run(debug=True, port=5001)