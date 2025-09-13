import streamlit as st
from utils.common_elements import show_patient_summary

if st.session_state.user_role == "doctor":
    st.title("Doctor Dashboard 👨‍⚕️")
    st.write("Welcome back, Doctor! Here are your quick actions and key skills.")

    # 5 Big Skill Tiles
    st.markdown("## Quick Skills")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        with st.container(border=True):
            st.markdown("### Drug Safety & Dose 💊")
            st.markdown("Check interactions & dosing")
            st.button("Scan Rx", use_container_width=True, key="dsd_button")
    
    with col2:
        with st.container(border=True):
            st.markdown("### Doctor → Patient 🗣️")
            st.markdown("Translate Rx & reports")
            st.button("Upload Report", use_container_width=True, key="dtp_button")
            
    with col3:
        with st.container(border=True):
            st.markdown("### Symptom Triage 🤕")
            st.markdown("Where to go, what to do now")
            st.button("Quick Triage", use_container_width=True, key="st_button")
            
    with col4:
        with st.container(border=True):
            st.markdown("### Chronic Coach 📈")
            st.markdown("Trends, nudges & alerts")
            st.button("Import CSV", use_container_width=True, key="cc_button")
            
    with col5:
        with st.container(border=True):
            st.markdown("### Doctor's Co-Pilot 🧠")
            st.markdown("Turn notes into SOAP & orders")
            st.button("Summarize Note", use_container_width=True, key="dcp_button")

    st.markdown("---")
    
    # Quick Actions Row
    st.markdown("## Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("Scan Prescription", use_container_width=True)
    with col2:
        st.button("Log Vitals", use_container_width=True)
    with col3:
        st.button("Start Voice Note", use_container_width=True)
    with col4:
        st.button("Import File", use_container_width=True)

elif st.session_state.user_role == "patient":
    st.title("Patient Dashboard 🧑‍⚕️")
    st.write("Welcome, John! Here are your personalized health tools.")
    
    # Patient Dashboard with Co-pilot
    st.markdown("## Your Co-pilot 🤝")
    st.info("Your personal health assistant is here to help you manage your health. What would you like to do?")
    
    col1, col2 = st.columns(2)
    with col1:
        st.header("Quick Actions")
        st.button("Talk to My Coach", use_container_width=True)
        st.button("Check My Symptoms", use_container_width=True)
        st.button("Translate My Report", use_container_width=True)
    
    with col2:
        st.header("My Health Snapshot")
        st.metric(label="Recent BP", value="120/80 mmHg", delta="Normal")
        st.metric(label="Last Glucose Reading", value="95 mg/dL", delta="Normal")
        st.button("Log New Vitals", use_container_width=True)
        st.markdown("---")
        st.subheader("Your Personalized Care Plan")
        st.write("✓ Walk 30 mins a day")
        st.write("✓ Take medications at 8 AM and 8 PM")
        
    st.markdown("---")
    st.header("Explore More Features")
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.subheader("Understand My Meds 💊")
            st.write("Check for drug safety and interactions.")
    with col2:
        with st.container(border=True):
            st.subheader("Chronic Care Tracker 📈")
            st.write("Monitor your trends and get alerts.")
    with col3:
        with st.container(border=True):
            st.subheader("My Health Journal ✍️")
            st.write("Log notes and voice memos.")