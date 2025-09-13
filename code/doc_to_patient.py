import streamlit as st

# The entire page is now wrapped in a condition to check for the 'patient' role.
if st.session_state.user_role == "patient":
    st.title("Translate My Health Reports 🗣️")
    st.write("Don't worry about confusing medical jargon. Upload your report and I'll translate it for you.")

    st.button("Upload Report / Prescription 📄", use_container_width=True)
    st.text_area("Or paste the text from your report here", height=200)
    st.slider("How simple should the language be?", 0, 10, 8)
    
    if st.button("Translate", type="primary"):
        st.session_state.model_output = "translation_results"

    # This is the results block that was missing, now restored.
    if 'model_output' in st.session_state and st.session_state.model_output == "translation_results":
        st.markdown("---")
        st.markdown("## Translated Report")
        with st.container(border=True):
            st.write("Hello! I've analyzed your report. Here's a simple summary:")
            st.success("Everything looks normal! ✅")
            st.markdown("---")
            st.info("**What does this mean?**")
            st.write("All your lab results are within the normal range. Keep up the good work!")
            st.button("Questions to ask my doctor")

# If the user is not a patient, this message is shown.
else:
    st.warning("This feature is available for patients only.")
    st.page_link("pages/1_🏠_Home.py", label="Return to Dashboard", icon="🏠")