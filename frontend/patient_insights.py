import streamlit as st

# This page is only for doctors
if st.session_state.user_role == "doctor":
    st.title("Patient Activity Dashboard 📊")
    
    if st.session_state.selected_patient:
        st.write(f"Showing insights for **{st.session_state.selected_patient}**.")
        st.info("ℹ️ *This information is displayed based on permissions granted by the patient.*")
    else:
        st.warning("Please select a patient from the sidebar to view their activity.")

    st.markdown("---")

    # Mock data for demonstration
    if st.session_state.selected_patient == "John Doe":
        # Card for Drug Safety
        with st.container(border=True):
            st.subheader("💊 Drug Safety Usage")
            st.write("**Last Check:** September 12, 2025")
            st.write("**Query:** Checked for interactions between `Lisinopril` and `Ibuprofen`.")
            st.success("**Result:** Low-risk interaction identified and flagged to patient.")

        # Card for Doctor to Patient Translator
        with st.container(border=True):
            st.subheader("🗣️ Report Translator Usage")
            st.write("**Last Use:** September 11, 2025")
            st.write("**Action:** Translated a lab report regarding cholesterol levels.")
            st.info("**Patient Note:** Patient viewed the 'Questions to ask my doctor' section.")
        
        # Card for Symptom Triage
        with st.container(border=True):
            st.subheader("🤕 Symptom Triage Usage")
            st.write("**Last Triage:** September 10, 2025")
            st.write("**Symptoms Reported:** 'Persistent cough, mild fever for 3 days'.")
            st.warning("**Recommendation Given:** Book GP appointment.")

        # Card for Chronic Coach
        with st.container(border=True):
            st.subheader("📈 Chronic Coach Activity")
            st.write("**Last Data Import:** September 13, 2025")
            st.write("**Latest Trend:** Blood pressure readings show a stable trend within the target range.")
            st.info("**Nudge:** Patient received a nudge to reduce salt intake, which they marked as 'completed'.")

    else:
        st.write(f"No recent activity recorded for **{st.session_state.selected_patient}**.")