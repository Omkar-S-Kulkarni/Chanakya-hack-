# File: frontend/main.py

import streamlit as st
import os

# --- Import functions from your other page files ---
# We assume each file has a main function like 'show_home_page()'
from home_page import show_home_page
from drug import show_drug_page
from doc_to_patient import show_translator_page
from symptom import show_symptom_page
from chronic_coach import show_chronic_coach_page
from doc_copilot import show_doc_copilot_page
from knowledge_base import show_knowledge_base_page
from patient_insights import show_patient_insights_page

# Set a custom page title and icon
st.set_page_config(
    page_title="Agentic Healthcare Copilot",
    page_icon="🏥",
    layout="wide"
)

# Load custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

# --- Initialize Session State ---
# This holds variables across page reruns
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# --- Role Selection / Login Screen ---
if not st.session_state.user_role:
    st.title("Welcome to the Agentic Healthcare Copilot 🤖")
    st.write("Please select your role to continue:")
    col1, col2 = st.columns([1,1])
    with col1:
        # When a button is clicked, it sets the role and Streamlit automatically reruns the script
        if st.button("I am a Doctor 👨‍⚕️", use_container_width=True, key="doctor_login"):
            st.session_state.user_role = "doctor"
            st.rerun() # Use st.rerun() which is the modern standard
    with col2:
        if st.button("I am a Patient 🧑‍⚕️", use_container_width=True, key="patient_login"):
            st.session_state.user_role = "patient"
            st.rerun()
    # Apply custom styling to the buttons
    st.markdown('<style>div.stButton > button {height:80px; font-size: 20px;}</style>', unsafe_allow_html=True)

# --- Main Application View (after role is selected) ---
else:
    # --- Top Bar ---
    # NEW: Updated the badge to show online status
    st.markdown(
        """
        <div class="top-bar">
            <h3 style="margin: 0; color: white;">Agentic Healthcare Copilot</h3>
            <span class="online-badge">🟢 Online (Connected to Gemini)</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Sidebar Navigation ---
    st.sidebar.title("Navigation")
    st.sidebar.markdown(f"**Role:** {st.session_state.user_role.capitalize()} 👋")
    st.sidebar.markdown("---")

    # Define navigation options based on user role
    if st.session_state.user_role == "doctor":
        # Options available only to doctors
        doctor_pages = {
            "🏠 Home": show_home_page,
            "💊 Drug Safety": show_drug_page,
            "🩺 Symptom Triage": show_symptom_page,
            "📈 Chronic Care Coach": show_chronic_coach_page,
            "🧑‍⚕️ Doctor's Co-Pilot": show_doc_copilot_page,
            "💡 Patient Insights": show_patient_insights_page,
            "📚 Knowledge Base": show_knowledge_base_page
        }
        selection = st.sidebar.radio("Go to", list(doctor_pages.keys()))
        # Call the function corresponding to the selection
        page = doctor_pages[selection]
        page()

    elif st.session_state.user_role == "patient":
        # Options available only to patients
        patient_pages = {
            "🏠 Home": show_home_page,
            "💊 Drug Safety": show_drug_page,
            "📄 Translate My Report": show_translator_page,
            "🩺 Symptom Triage": show_symptom_page,
            "📈 Chronic Care Coach": show_chronic_coach_page,
        }
        selection = st.sidebar.radio("Go to", list(patient_pages.keys()))
        # Call the function corresponding to the selection
        page = patient_pages[selection]
        page()