"""
Main application file for the Agentic Healthcare Copilot.

This script sets up the Streamlit page configuration, loads custom CSS,
and handles the initial user role selection (Doctor vs. Patient).
It also creates the main top bar and sidebar navigation structure.
"""

import streamlit as st
import os

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

# A simple role selection to start the app
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'selected_patient' not in st.session_state:
    st.session_state.selected_patient = None

def set_role(role):
    st.session_state.user_role = role
    st.experimental_rerun()

if not st.session_state.user_role:
    st.title("Welcome to the Agentic Healthcare Copilot 🤖")
    st.write("Please select your role to continue:")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("I am a Doctor 👨‍⚕️", use_container_width=True):
            set_role("doctor")
    with col2:
        if st.button("I am a Patient 🧑‍⚕️", use_container_width=True):
            set_role("patient")
    st.markdown('<style>div.stButton > button {width:100%; height:80px; font-size: 20px;}</style>', unsafe_allow_html=True)

else:
    # This is a placeholder for model integration.
    if 'model_output' not in st.session_state:
        st.session_state.model_output = None

    # Top bar
    st.markdown(
        """
        <div class="top-bar">
            <div style="display: flex; align-items: center;">
                <h3 style="margin: 0; color: white;">Agentic Healthcare Copilot</h3>
                <span class="offline-badge">Offline</span>
            </div>
            <input class="search-input" type="text" placeholder="Search medicine, report, symptom...">
            <div>
                👤 User
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.title("Navigation")
    st.sidebar.markdown(f"**Current Role:** {st.session_state.user_role.capitalize()} 👋")

    # Patient/Record Access feature for Doctors
    if st.session_state.user_role == "doctor":
        st.sidebar.markdown("---")
        st.sidebar.subheader("Patient Records")
        patient_list = ["John Doe", "Jane Smith", "Patient 3"]
        st.session_state.selected_patient = st.sidebar.selectbox("Select a Patient", patient_list)
        st.sidebar.button("View Records")

    st.markdown("---")