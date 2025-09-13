# File: frontend/home_page.py

import streamlit as st

def show_home_page():
    """
    Displays the main dashboard for either a doctor or a patient,
    based on the user_role stored in the session state.
    """
    
    # --- DOCTOR'S VIEW ---
    if st.session_state.user_role == "doctor":
        st.title("Doctor Dashboard 👨‍⚕️")
        st.write("Welcome back, Doctor! Select a tool from the sidebar to begin.")

        # Display the doctor-specific skill tiles.
        st.markdown("## Core Tools")
        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container(border=True):
                st.markdown("### Doctor’s Co-Pilot 🧠")
                st.markdown("Turn notes into SOAP summaries, check guidelines, and draft orders.")
                # NOTE: The button is removed as navigation is now handled by the sidebar.
        
        with col2:
            with st.container(border=True):
                st.markdown("### Patient Insights 📊")
                st.markdown("View high-level summaries and trends for your patients.")
                # NOTE: The button is removed as navigation is now handled by the sidebar.

        with col3:
            with st.container(border=True):
                st.markdown("### Knowledge Base 📚")
                st.markdown("Access clinical guidelines and information from trusted sources.")
                # NOTE: The button is removed as navigation is now handled by the sidebar.

        st.markdown("---")

        # Quick Actions Row (kept as placeholders for future functionality)
        st.markdown("## Quick Actions")
        q_col1, q_col2, q_col3, q_col4 = st.columns(4)
        with q_col1:
            st.button("Scan Prescription", use_container_width=True, disabled=True)
        with q_col2:
            st.button("Log Vitals", use_container_width=True, disabled=True)
        with q_col3:
            st.button("Start Voice Note", use_container_width=True, disabled=True)
        with q_col4:
            st.button("Import File", use_container_width=True, disabled=True)

    # --- PATIENT'S VIEW ---
    elif st.session_state.user_role == "patient":
        st.title("Patient Dashboard 🧑‍⚕️")
        st.write("Welcome! Use the tools in the sidebar to manage your health.")
        
        st.markdown("## Your Co-pilot 🤝")
        st.info("Your personal health assistant is here to help. Select a tool from the sidebar to get started.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.header("My Health Snapshot")
            # These are placeholder metrics. In a real app, this data would be dynamic.
            st.metric(label="Recent BP", value="120/80 mmHg", delta="Normal")
            st.metric(label="Last Glucose Reading", value="95 mg/dL", delta="Normal")
            st.button("Log New Vitals", use_container_width=True, disabled=True)
        
        with col2:
            st.header("Your Personalized Care Plan")
            # Placeholder care plan items
            st.write("✓ Walk 30 mins a day")
            st.write("✓ Take medications at 8 AM and 8 PM")
            st.write("✓ Follow up with Dr. Smith next month")

        st.markdown("---")
        st.header("Explore Your Tools")
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.subheader("Understand My Meds 💊")
                st.write("Check for drug safety and interactions using the 'Drug Safety' tool.")
        with col2:
            with st.container(border=True):
                st.subheader("Chronic Care Tracker 📈")
                st.write("Monitor your trends and get alerts via the 'Chronic Care Coach'.")
        with col3:
            with st.container(border=True):
                st.subheader("Translate My Report 📄")
                st.write("Get a simple explanation of your lab reports.")