# File: frontend/main.py

import streamlit as st
import os
import threading
import sys

# --- Add the parent 'app' directory to the Python path ---
# This is a crucial step to allow imports from the sibling 'app' folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

# --- Import your Flask app and your page functions ---
from app import app as flask_app # Import the 'app' object from app/app.py
from home_page import show_home_page
from drug import show_drug_page
from doc_to_patient import show_translator_page
from symptom import show_symptom_page
from chronic_coach import show_chronic_coach_page
from doc_copilot import show_doc_copilot_page
# Note: knowledge_base.py and patient_insights.py are not in the provided file list,
# so they are commented out. If you create them, you can uncomment these lines.
# from knowledge_base import show_knowledge_base_page
# from patient_insights import show_patient_insights_page

# --- Function to run the Flask app in a background thread ---
def run_flask():
    # Runs the Flask server on host 0.0.0.0, which is required for cloud deployment
    flask_app.run(host='0.0.0.0', port=5001, debug=False)

# --- Start the Flask server if it's not already running ---
# We use session state to ensure this only runs once.
if 'flask_thread_started' not in st.session_state:
    print("Starting Flask server in a background thread...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    st.session_state.flask_thread_started = True
    print("Flask server thread started.")


# --- Your Existing Streamlit App Code Starts Here ---

# Set a custom page title and icon
st.set_page_config(
    page_title="Agentic Healthcare Copilot",
    page_icon="🏥",
    layout="wide"
)

# Load custom CSS
def local_css(file_name):
    # Check if file exists before trying to open it
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

# --- Initialize Session State ---
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# --- Role Selection / Login Screen ---
if not st.session_state.user_role:
    st.title("Welcome to the Agentic Healthcare Copilot 🤖")
    st.write("Please select your role to continue:")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("I am a Doctor 👨‍⚕️", use_container_width=True, key="doctor_login"):
            st.session_state.user_role = "doctor"
            st.rerun()
    with col2:
        if st.button("I am a Patient 🧑‍⚕️", use_container_width=True, key="patient_login"):
            st.session_state.user_role = "patient"
            st.rerun()
    st.markdown('<style>div.stButton > button {height:80px; font-size: 20px;}</style>', unsafe_allow_html=True)

# --- Main Application View (after role is selected) ---
else:
    # --- Top Bar ---
    st.markdown(
        """
        <div class="top-bar">
            <h3 style="margin: 0; color: white;">Agentic Healthcare Copilot</h3>
            <span class="online-badge">🟢 Online</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Sidebar Navigation ---
    st.sidebar.title("Navigation")
    st.sidebar.markdown(f"**Role:** {st.session_state.user_role.capitalize()} 👋")
    st.sidebar.markdown("---")

    if st.session_state.user_role == "doctor":
        doctor_pages = {
            "🏠 Home": show_home_page,
            "💊 Drug Safety": show_drug_page,
            "🩺 Symptom Triage": show_symptom_page,
            "📈 Chronic Care Coach": show_chronic_coach_page,
            "🧑‍⚕️ Doctor's Co-Pilot": show_doc_copilot_page,
            # "💡 Patient Insights": show_patient_insights_page, # Uncomment if you create this page
            # "📚 Knowledge Base": show_knowledge_base_page, # Uncomment if you create this page
        }
        selection = st.sidebar.radio("Go to", list(doctor_pages.keys()))
        page = doctor_pages[selection]
        page()

    elif st.session_state.user_role == "patient":
        patient_pages = {
            "🏠 Home": show_home_page,
            "💊 Drug Safety": show_drug_page,
            "📄 Translate My Report": show_translator_page,
            "🩺 Symptom Triage": show_symptom_page,
            "📈 Chronic Care Coach": show_chronic_coach_page,
        }
        selection = st.sidebar.radio("Go to", list(patient_pages.keys()))
        page = patient_pages[selection]
        page()