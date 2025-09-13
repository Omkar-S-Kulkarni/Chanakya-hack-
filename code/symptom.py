import streamlit as st

# The entire page is now wrapped in a condition to check for the 'patient' role.
if st.session_state.user_role == "patient":
    st.title("Symptom Triage 🤕")
    st.write("Tell me what you're feeling and I'll help you figure out what to do.")
    
    st.text_area("Describe your symptoms", placeholder="e.g., headache, sore throat, fever for 2 days")
    
    if st.button("Quick Triage", type="primary", use_container_width=True):
        st.session_state.model_output = "triage_results_patient"

    # This is the results block that was missing, now restored.
    if 'model_output' in st.session_state and st.session_state.model_output == "triage_results_patient":
        st.markdown("---")
        st.markdown("## My Recommendation")
        st.success("### Home care is likely appropriate ✅")
        st.write("Your symptoms suggest a common cold. You can likely manage this at home.")
        
        with st.expander("Show steps for home care"):
            st.write("- Get plenty of rest.")
            st.write("- Stay hydrated by drinking water and warm tea.")
            st.write("- Use over-the-counter pain relievers for headache or fever.")
            st.button("Save to My Care Plan")
            
        st.markdown("---")
        st.warning("🚨 **This is not a substitute for professional medical advice. If your symptoms worsen, please contact a doctor or go to the ER.**")

# If the user is not a patient, this message is shown.
else:
    st.warning("This feature is available for patients only.")
    st.page_link("pages/1_🏠_Home.py", label="Return to Dashboard", icon="🏠")