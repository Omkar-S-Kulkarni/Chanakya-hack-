import streamlit as st

if st.session_state.user_role == "doctor":
    st.title("Doctor's Co-Pilot 👨‍⚕️")
    st.write(f"Enhance your encounter with **{st.session_state.selected_patient}**.")

    # Patient records access
    st.markdown("### Patient Record & History")
    if st.session_state.selected_patient:
        patient_records_data = {
            "Name": st.session_state.selected_patient,
            "Age": 45,
            "Previous Visit Date": "2025-08-01",
            "Diagnosis": "Hypertension",
            "Recommended Medicine": "Lisinopril (10mg/day)"
        }
        st.json(patient_records_data)

    st.markdown("---")
    # Inputs
    st.text_area("Paste short encounter note or transcript", height=200)
    st.selectbox("Select Guideline", ["Hypertension Guideline v1", "Diabetes Care v2"])
        
    if st.button("Generate SOAP", type="primary"):
        st.session_state.model_output = "copilot_results"

    if 'model_output' in st.session_state and st.session_state.model_output == "copilot_results":
        st.markdown("---")
        st.markdown("## Generated Output")
        
        # SOAP card
        st.subheader("SOAP Note Draft")
        with st.container(border=True):
            st.text_area("S: Subjective", value="Patient reports mild cough and fever since yesterday.")
            st.text_area("O: Objective", value="Vital signs: Temp 38.2°C, HR 85. Lung sounds clear.")
            st.text_area("A: Assessment", value="Acute viral upper respiratory infection.")
            st.text_area("P: Plan", value="Symptomatic treatment, rest, hydration. Return if symptoms worsen.")
            st.button("Accept Changes")
            st.button("Copy to Clipboard")
            
        st.markdown("---")
        st.subheader("Guideline Check")
        st.success("✅ Patient's symptoms and vitals align with standard viral URI guidelines.")

elif st.session_state.user_role == "patient":
    st.title("My Patient Co-Pilot 🧠")
    st.write("Your personal co-pilot to help you manage your health journey.")

    st.text_area("Ask me anything about your health", placeholder="e.g., What does my lab report mean? Should I be worried about my cough?")
    
    if st.button("Get an answer", type="primary"):
        st.session_state.model_output = "patient_copilot_answer"
    
    if 'model_output' in st.session_state and st.session_state.model_output == "patient_copilot_answer":
        st.markdown("---")
        st.markdown("## Your Answer")
        with st.container(border=True):
            st.write("The results from your lab report indicate that your blood pressure is a bit high. While this is not an immediate emergency, it's a good idea to schedule a check-up with your doctor to discuss lifestyle changes or possible treatment options.")
            st.button("Call My Doctor")