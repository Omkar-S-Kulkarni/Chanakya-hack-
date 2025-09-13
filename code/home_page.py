import streamlit as st

# --- DOCTOR'S VIEW (MODIFIED) ---
if st.session_state.user_role == "doctor":
    st.title("Doctor Dashboard 👨‍⚕️")
    st.write("Welcome back, Doctor! Here are your core tools.")

    # Display the remaining, doctor-specific skill tiles.
    st.markdown("## Core Tools")
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("### Doctor’s Co-Pilot 🧠")
            st.markdown("Turn notes into SOAP & orders.")
            # Using st.page_link for robust navigation
            st.page_link("pages/6_👨‍⚕️_Doctors_Co_Pilot.py", label="Go to Co-Pilot", use_container_width=True)

    with col2:
        with st.container(border=True):
            st.markdown("### Patient Insights 📊")
            st.markdown("View consented patient activity.")
            st.page_link("pages/8_📊_Patient_Insights.py", label="View Dashboard", use_container_width=True)

    with col3:
        with st.container(border=True):
            st.markdown("### Knowledge Base 📚")
            st.markdown("Access guidelines & WHO updates.")
            st.page_link("pages/7_🧠_Knowledge_Base.py", label="Access KB", use_container_width=True)

    st.markdown("---")

    # Quick Actions Row remains unchanged
    st.markdown("## Quick Actions")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    with q_col1:
        st.button("Scan Prescription", use_container_width=True)
    with q_col2:
        st.button("Log Vitals", use_container_width=True)
    with q_col3:
        st.button("Start Voice Note", use_container_width=True)
    with q_col4:
        st.button("Import File", use_container_width=True)

# --- PATIENT'S VIEW (UNCHANGED) ---
elif st.session_state.user_role == "patient":
    st.title("Patient Dashboard 🧑‍⚕️")
    st.write("Welcome, John! Here are your personalized health tools.")
    
    # ... (The rest of the patient dashboard code remains the same)
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