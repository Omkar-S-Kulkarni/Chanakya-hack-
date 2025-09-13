# File: frontend/utilities.py

import requests
import json
import streamlit as st

# The URL of your running Flask backend server
# This should match the port you are running app.py on.
API_URL = "http://127.0.0.1:5001/api/unified_analysis"

def call_agent_api(agent_type: str, json_data: dict, file=None):
    """
    A single, reusable function to call any agent in your backend.

    Args:
        agent_type (str): The name of the agent to call (e.g., 'drug_safety').
        json_data (dict): The text-based data for the agent (e.g., medications, symptoms).
        file (UploadedFile, optional): An uploaded file for agents that need one.

    Returns:
        dict: The JSON response from the backend API.
    """
    try:
        # Prepare the data and files to be sent in the POST request.
        # This structure matches what the Flask server expects.
        form_data = {
            'agent_type': agent_type,
            'json_data': json.dumps(json_data)
        }
        
        files = {}
        if file:
            # If a file is provided, we read its content into memory to send.
            files['file'] = (file.name, file.getvalue(), file.type)

        # Show a spinner in the UI while waiting for the response.
        with st.spinner(f"🧠 Agents are collaborating on your request... Please wait."):
            # Make the API call with a long timeout, as AI models can take time.
            response = requests.post(API_URL, data=form_data, files=files, timeout=300)
            
            # This will raise an error if the server returned a bad status (e.g., 404, 500)
            response.raise_for_status()
            
            return response.json()

    except requests.exceptions.RequestException as e:
        # If the request fails (e.g., server is down, network error), we return a helpful error.
        st.error(f"API Connection Error: Could not connect to the backend. Please ensure the Flask server (`app.py`) is running. Details: {e}")
        return None