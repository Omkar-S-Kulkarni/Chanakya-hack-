import os
import faiss
import json
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import numpy as np
from PIL import Image


# File: app/gemini_agent.py

# ... (keep the imports) ...

class GeminiAgent:
    def __init__(self, api_key, kb_folder="../data/my_final_kb"):
        """
        Initializes the agent, Gemini model, and loads the local Knowledge Base.
        CORRECTED PATH: Looks one level up for the 'data/my_final_kb' folder.
        """
        if not api_key:
            raise ValueError("Google API Key is missing. Please set it in your .env file.")
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Load the local vector store for RAG
        print("Loading local Knowledge Base...")
        try:
            self.index = faiss.read_index(os.path.join(kb_folder, "kb.faiss"))
            with open(os.path.join(kb_folder, "kb_chunks.json"), 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Knowledge Base loaded successfully.")
        except Exception as e:
            print(f"CRITICAL: Failed to load Knowledge Base. RAG features will be disabled. Error: {e}")
            print(f"--> Please ensure the folder '{kb_folder}' exists and contains 'kb.faiss' and 'kb_chunks.json'.")
            self.index = None
    
    # ... (the rest of the class remains the same) ...
    def _retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Retrieves relevant context from the local FAISS index."""
        if not self.index:
            return "No local knowledge base loaded."
        
        query_embedding = self.embedding_model.encode([query])
        _, indices = self.index.search(np.array(query_embedding), top_k)
        
        context = "\n\n".join([self.chunks[i]['content_chunk'] for i in indices[0] if i != -1])
        return context

# ... (keep the rest of the file the same) ...

    def run_drug_safety_agent(self, data: dict, safety_alerts: list) -> dict:
        """
        Uses Gemini to interpret rule engine alerts and retrieve general drug info.
        UPDATED: Now falls back to Gemini's general knowledge if local KB is insufficient.
        """
        medications = data.get("medications", [])
        
        # Generate explanations for each medication using RAG with a fallback
        drug_info_list = []
        for med in medications:
            query = f"Provide a brief, patient-friendly description of the drug {med}, including its common use and important considerations."
            context = self._retrieve_context(query)
            
            # --- NEW, MORE FLEXIBLE PROMPT ---
            prompt = f"""
            You are a helpful healthcare assistant. Your task is to answer the user's query about a medication.

            1. First, try to answer the query using ONLY the "Context from local knowledge base" provided below.
            2. If the context is empty, not relevant, or does not contain the answer, then use your own general knowledge to answer.
            3. When you use your own general knowledge, you MUST start your response with the phrase "Based on my general knowledge,...".

            Context from local knowledge base:
            ---
            {context}
            ---
            User's Query: {query}
            """
            response = self.model.generate_content(prompt)
            drug_info_list.append({
                "drug_name": med,
                "info": response.text
            })
            
        return {
            "agent_type": "Drug Safety & Dosage",
            "safety_alerts": safety_alerts,
            "drug_information": drug_info_list,
            "questions_for_your_doctor": [
                "Are these medications safe for my specific health condition?",
                "What are the most common side effects I should watch for?",
                "How should I take these medications (with food, at what time)?",
            ]
        }
# ... (the rest of the file remains the same) ...
    def run_translator_agent(self, text_content: str, image_path: str = None) -> dict:
        """
        Uses Gemini's multimodal capabilities to translate medical documents.
        """
        prompt = """
        You are a Doctor-to-Patient Translator. Your task is to analyze the provided medical document (text and/or image) and explain it in simple, clear language.

        Your output MUST be a JSON object with the following structure:
        {
          "summary": "A brief, one-paragraph summary of the document.",
          "key_findings": [
            {
              "finding": "The specific medical term or result (e.g., 'Hemoglobin').",
              "value": "The measured value (e.g., '9.5 g/dL').",
              "interpretation": "A plain-language explanation of what this means (e.g., 'This is lower than the normal range, indicating anemia.').",
              "is_abnormal": true
            }
          ],
          "next_steps": "Recommended actions for the patient (e.g., 'Discuss these results with your doctor.').",
          "urgency": "Low | Medium | High"
        }

        Analyze the following content:
        """
        
        if image_path:
            print(f"Analyzing image: {image_path}")
            img = Image.open(image_path)
            response = self.model.generate_content([prompt, text_content, img])
        else:
            response = self.model.generate_content([prompt, text_content])
            
        # Clean and parse the JSON response from Gemini
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse AI model's response.", "raw_response": cleaned_response}

    def run_symptom_triage_agent(self, data: dict, red_flag_alerts: list) -> dict:
        """
        Provides a triage recommendation based on symptoms.
        """
        if red_flag_alerts:
            # If the rule engine found a red flag, the decision is made.
            urgency = "Go to ER now"
            reasoning = red_flag_alerts[0]['message'] # Use the rule's reason
        else:
            # If no red flags, use the LLM for nuanced advice
            symptoms = data.get("symptoms", "No symptoms provided.")
            query = f"A patient reports the following symptoms: '{symptoms}'. Based on this, what is the recommended triage level (Home care, Book GP, Go to ER now) and what are some basic first-aid steps?"
            context = self._retrieve_context(query)
            prompt = f"""
            Context from WHO/CDC guidelines:
            {context}
            ---
            Based ONLY on the context provided, analyze the patient's query and provide a triage recommendation.
            Patient Query: {query}
            """
            response = self.model.generate_content(prompt)
            # In a real app, you would parse this response more carefully.
            # For the hackathon, we'll just pass the text.
            urgency_and_reasoning = response.text

        return {
            "agent_type": "Symptom Urgency Triage",
            "recommendation": urgency if red_flag_alerts else "See reasoning below",
            "reasoning": reasoning if red_flag_alerts else urgency_and_reasoning
        }
    
    # ... (keep the __init__, _retrieve_context, run_drug_safety_agent, run_translator_agent methods as they are) ...
# Just add the two new methods below inside the GeminiAgent class.

    def run_chronic_care_agent(self, records: list) -> dict:
        """
        Analyzes time-series data (like BP or Glucose logs) to find trends and give advice.
        """
        prompt = f"""
        You are a Chronic Care Coach. Your task is to analyze the following patient-provided data log and provide a helpful, safe summary. The data contains a list of readings over time.

        Your output MUST be a JSON object with the following structure:
        {{
          "trend_summary": "A brief, one-paragraph summary of the data trends (e.g., 'Blood pressure readings are consistently high', 'Glucose levels show high variability after meals').",
          "risk_assessment": {{
            "level": "Low | Normal | Elevated | High",
            "reason": "A brief explanation for the risk level assigned."
          }},
          "behavioral_nudges": [
            "A simple, safe, actionable diet-related suggestion.",
            "A simple, safe, actionable lifestyle suggestion (e.g., related to exercise or stress).",
            "A suggestion to consult a doctor for a specific reason."
          ]
        }}

        Analyze this data:
        {json.dumps(records, indent=2)}
        """
        response = self.model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse AI model's response.", "raw_response": cleaned_response}

    def run_doctors_copilot_agent(self, note: str) -> dict:
        """
        Processes a doctor's encounter note to generate a SOAP summary and check against guidelines.
        """
        # For the co-pilot, we use RAG to find relevant clinical guidelines in our KB
        context = self._retrieve_context(f"Clinical guidelines related to the following note: {note}", top_k=5)

        prompt = f"""
        You are a Doctor's Co-Pilot, an AI assistant for clinicians. Your task is to process a raw encounter note and structure it for efficiency.

        1.  Analyze the "Encounter Note".
        2.  Use the "Retrieved Guideline Snippets" to inform your output.
        3.  Your output MUST be a JSON object with the exact following structure:
        {{
          "soap_summary": {{
            "subjective": "What the patient reported.",
            "objective": "Verifiable observations and measurements.",
            "assessment": "A summary of the diagnosis or condition.",
            "plan": "The course of action."
          }},
          "guideline_checklist": [
            {{
              "guideline": "A specific recommendation from the retrieved snippets.",
              "status": "Addressed | Not Addressed | Partially Addressed",
              "reason": "A brief justification for the status."
            }}
          ],
          "draft_orders": {{
            "suggested_labs": ["A list of common lab tests to consider."],
            "suggested_medications": ["A list of common medications to consider."]
          }}
        }}

        Retrieved Guideline Snippets (for context):
        ---
        {context}
        ---
        Encounter Note:
        ---
        {note}
        ---
        """
        response = self.model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse AI model's response.", "raw_response": cleaned_response}