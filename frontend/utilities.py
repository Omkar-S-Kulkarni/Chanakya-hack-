# File: frontend/utilities.py

import requests
import json
import streamlit as st

# URL of the running Flask backend server
# Make sure this matches the port your app.py uses.
API_URL = "http://127.0.0.1:5001/api/unified_analysis"

def call_agent_api(agent_type: str, json_data: dict, file=None):
    """
    Reusable function to call any backend agent.

    Args:
        agent_type (str): Name of the agent to call (e.g., 'drug_safety').
        json_data (dict): Text-based input for the agent (e.g., medications, symptoms).
        file (UploadedFile, optional): Uploaded file for agents that require it.

    Returns:
        dict: JSON response from the backend API.
    """
    try:
        # Prepare the POST form data
        form_data = {
            'agent_type': agent_type,
            'json_data': json.dumps(json_data)
        }

        files = {}
        if file:
            # Read the file content into memory to send
            files['file'] = (file.name, file.getvalue(), file.type)

        # Display spinner while waiting for response
        with st.spinner("🧠 Agents are collaborating on your request... Please wait."):
            response = requests.post(API_URL, data=form_data, files=files, timeout=300)
            response.raise_for_status()  # Raise error for bad HTTP status
            return response.json()

    except requests.exceptions.RequestException as e:
        st.error(
            f"API Connection Error: Could not connect to the backend. "
            f"Ensure the Flask server (`app.py`) is running. Details: {e}"
        )
        return None
