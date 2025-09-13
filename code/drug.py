import streamlit as st
from utils.common_elements import show_patient_summary

# The entire page is now wrapped in a condition to check for the 'patient' role.
if st.session_state.user_role == "patient":
    st.title("Understand My Medications 💊")
    st.write("Find out more about your medications and check for potential interactions.")
    
    st.markdown("---")
    st.text_input("Search for a medication", placeholder="e.g., Aspirin")
    st.text_area("Or paste your full prescription text here")
    
    if st.button("Analyze My Meds", type="primary"):
        # This sets the flag to show the results section below
        st.session_state.model_output = "drug_safety_results"

    # This is the results block that was missing, now restored.
    if 'model_output' in st.session_state and st.session_state.model_output == "drug_safety_results":
        st.markdown("## My Analysis")
        st.success("No critical interactions found for your current medications.")
        with st.container(border=True):
            st.subheader("Common Side Effects for Aspirin")
            st.write("- Stomach upset, heartburn")
            st.write("- Mild headache")
            st.write("If these persist, talk to your doctor.")
            
        st.button("Questions to ask my doctor")

# If the user is not a patient (i.e., a doctor), this message is shown.
else:
    st.warning("This feature is available for patients only.")
    st.page_link("pages/1_🏠_Home.py", label="Return to Dashboard", icon="🏠")