import json
from itertools import combinations

class RuleEngine:
    """
    A deterministic rule engine for critical healthcare safety checks.
    It loads knowledge bases into memory for fast, efficient lookups.
    """
    def __init__(self, drug_db_path='../data/drug_db.json', interactions_path='../data/interactions.json'):
        """
        Initializes the Rule Engine by loading the knowledge bases from file.
        CORRECTED PATH: Looks one level up for the 'data' folder.
        """
        print("Initializing Rule Engine...")
        try:
            # NOTE: Make sure you have created 'drug_db.json' and 'interactions.json'
            # and placed them inside your main 'data' folder.
            with open(drug_db_path, 'r') as f:
                self.drug_db = json.load(f)
            with open(interactions_path, 'r') as f:
                self.interactions_db = json.load(f)
            
            # --- Optimizations: Create fast lookup maps for performance ---
            self.drug_map_by_name = {d['name'].lower(): d for d in self.drug_db}
            
            print("Rule Engine initialized successfully.")
        except FileNotFoundError as e:
            print(f"CRITICAL: Could not initialize Rule Engine. Knowledge base file not found: {e.filename}")
            print("--> Please ensure 'drug_db.json' and 'interactions.json' exist in your 'Chanakya-hack-/data/' folder.")
            self.drug_db = []
            self.interactions_db = []
            self.drug_map_by_name = {}
        # Define symptom red flags
        self.symptom_red_flags = [
            "crushing chest pain", "chest pressure", "cannot breathe", "can't breathe",
            "loss of consciousness", "unconscious", "unresponsive",
            "uncontrolled bleeding", "severe bleeding",
            "seizure", "vision loss", "slurred speech", "face drooping"
        ]

    def check_drug_interactions(self, drug_names: list[str]) -> list[dict]:
        """
        Checks for known severe interactions between a list of drugs.
        """
        alerts = []
        # Find the drug objects from our DB corresponding to the input names
        known_drugs = [self.drug_map_by_name[name.lower()] for name in drug_names if name.lower() in self.drug_map_by_name]
        
        if len(known_drugs) < 2:
            return [] # Not enough drugs to have an interaction

        # Check all unique pairs of drugs using their RxCUI IDs
        for drug1, drug2 in combinations(known_drugs, 2):
            combo_set = {drug1['rxcui'], drug2['rxcui']}
            for interaction in self.interactions_db:
                if set(interaction['drugs']) == combo_set:
                    alerts.append({
                        "type": "DRUG_INTERACTION",
                        "severity": interaction['severity'],
                        "message": f"Interaction between {drug1['name']} and {drug2['name']}. Reason: {interaction['description']}"
                    })
        return alerts

    def check_duplicate_therapy(self, drug_names: list[str]) -> list[dict]:
        """
        Checks for multiple drugs from the same therapeutic class.
        """
        alerts = []
        drug_classes = {}
        for name in drug_names:
            drug_info = self.drug_map_by_name.get(name.lower())
            if drug_info:
                drug_class = drug_info.get('class')
                if drug_class:
                    if drug_class not in drug_classes:
                        drug_classes[drug_class] = []
                    drug_classes[drug_class].append(drug_info['name'])

        for drug_class, drugs in drug_classes.items():
            if len(drugs) > 1:
                alerts.append({
                    "type": "DUPLICATE_THERAPY",
                    "severity": "Medium",
                    "message": f"Multiple drugs from the '{drug_class}' class found: {', '.join(drugs)}. This may increase the risk of side effects."
                })
        return alerts

    def check_allergies(self, drug_names: list[str], patient_allergies: list[str]) -> list[dict]:
        """
        Checks if any prescribed drugs match the patient's known allergies.
        """
        alerts = []
        # Normalize patient allergies for robust matching
        normalized_patient_allergies = {allergy.lower().strip() for allergy in patient_allergies}

        for name in drug_names:
            drug_info = self.drug_map_by_name.get(name.lower())
            if drug_info:
                # The 'allergies' field in drug_db.json should list all known identifiers (class, name, etc.)
                drug_allergy_triggers = {trigger.lower() for trigger in drug_info.get('allergies', [])}
                
                # Check for any overlap
                if not normalized_patient_allergies.isdisjoint(drug_allergy_triggers):
                     alerts.append({
                        "type": "ALLERGY_ALERT",
                        "severity": "High",
                        "message": f"Critical allergy alert: Patient is allergic to a substance in '{drug_info['name']}'. Do not administer."
                    })
        return alerts

    def check_symptom_red_flags(self, symptom_text: str) -> list[dict]:
        """
        Scans free-text symptoms for critical, life-threatening keywords.
        """
        alerts = []
        text_lower = symptom_text.lower()
        for flag in self.symptom_red_flags:
            if flag in text_lower:
                alerts.append({
                    "type": "SYMPTOM_RED_FLAG",
                    "severity": "Critical",
                    "message": f"Detected critical symptom: '{flag}'. This may indicate a medical emergency."
                })
                # For red flags, we can stop after the first one is found.
                return alerts
        return alerts

    def run_all_checks(self, drug_names: list[str] = None, patient_allergies: list[str] = None, symptom_text: str = None) -> list[dict]:
        """
        Orchestrator method to run all relevant checks based on the provided input.
        """
        all_alerts = []
        
        if drug_names:
            all_alerts.extend(self.check_drug_interactions(drug_names))
            all_alerts.extend(self.check_duplicate_therapy(drug_names))
            if patient_allergies:
                all_alerts.extend(self.check_allergies(drug_names, patient_allergies))
        
        if symptom_text:
            all_alerts.extend(self.check_symptom_red_flags(symptom_text))
            
        return all_alerts

# --- This block allows you to test the script directly ---
if __name__ == '__main__':
    # This assumes your kb_data is in a sibling directory to 'app'
    # To run this test, you'd navigate to the 'app' folder and run 'python rule_engine.py'
    engine = RuleEngine(drug_db_path='../kb_data/drug_db.json', interactions_path='../kb_data/interactions.json')
    
    print("\n--- Testing Drug Safety Checks ---")
    prescription1 = ["Aspirin", "Warfarin", "Ibuprofen"]
    allergies1 = ["Penicillin"]
    alerts1 = engine.run_all_checks(drug_names=prescription1, patient_allergies=allergies1)
    print(f"Alerts for prescription {prescription1} with allergies {allergies1}:")
    print(json.dumps(alerts1, indent=2))
    
    print("\n--- Testing Allergy Alert ---")
    prescription2 = ["Amoxicillin"]
    allergies2 = ["penicillin"]
    alerts2 = engine.run_all_checks(drug_names=prescription2, patient_allergies=allergies2)
    print(f"Alerts for prescription {prescription2} with allergies {allergies2}:")
    print(json.dumps(alerts2, indent=2))
    
    print("\n--- Testing Symptom Triage Red Flags ---")
    symptoms1 = "I have a mild headache and a runny nose"
    alerts3 = engine.run_all_checks(symptom_text=symptoms1)
    print(f"Alerts for symptoms: '{symptoms1}'")
    print(json.dumps(alerts3, indent=2))
    
    symptoms2 = "My father has crushing chest pain and feels faint"
    alerts4 = engine.run_all_checks(symptom_text=symptoms2)
    print(f"Alerts for symptoms: '{symptoms2}'")
    print(json.dumps(alerts4, indent=2))