# File: frontend/doc_to_patient.py

import streamlit as st
from utilities import call_agent_api

def show_translator_page():
    """
    Displays the UI for the Doctor-to-Patient Translator agent.
    """
    st.title("Translate My Health Report 🗣️")
    st.write("Confused by medical jargon? Upload your lab report, prescription, or doctor's note, and the AI will explain it in simple terms.")
    
    st.markdown("---")

    # --- 1. User Input: File Uploader ---
    # Use st.file_uploader for a better user experience
    uploaded_file = st.file_uploader(
        "Upload your report (PDF or Image)", 
        type=['pdf', 'png', 'jpg', 'jpeg'],
        key="translator_file_uploader"
    )

    if st.button("Translate My Report", type="primary", use_container_width=True):
        # --- 2. API Call Logic ---
        if uploaded_file is not None:
            # Call the backend API with the file
            # No additional JSON data is needed for this agent, so we pass an empty dict
            response = call_agent_api(agent_type='translator', json_data={}, file=uploaded_file)
            st.session_state.translator_results = response
        else:
            st.warning("Please upload a file first.")
            st.session_state.translator_results = None

    # --- 3. Display Results ---
    if 'translator_results' in st.session_state and st.session_state.translator_results:
        results = st.session_state.translator_results

        st.markdown("---")
        st.markdown("## Analysis Results")

        # --- Display Agent 2 (Evaluation) First ---
        st.subheader("Agent 2: Quality & Safety Review")
        if "agent2_evaluation" in results and not results["agent2_evaluation"].get("error"):
            eval_data = results["agent2_evaluation"]
            score = eval_data.get("overall_quality_score", "N/A")
            recommendation = eval_data.get("final_recommendation", "No recommendation.")
            
            with st.container(border=True):
                st.markdown(f"##### Overall Quality Score: **{score} / 5.0**")
                st.info(f"**Reviewer's Note:** {recommendation}")
        else:
            st.warning("The evaluation agent could not review this result.")
        
        # --- Display Agent 1 (Translator Analysis) ---
        st.subheader("Agent 1: Translated Report")
        if "agent1_analysis" in results and not results["agent1_analysis"].get("error"):
            analysis = results["agent1_analysis"]
            
            # Display Summary
            with st.expander("📄 Plain-Language Summary", expanded=True):
                st.markdown(analysis.get("summary", "No summary provided."))

            # Display Key Findings in a structured way
            with st.expander("🔬 Key Findings", expanded=True):
                key_findings = analysis.get("key_findings", [])
                if key_findings:
                    for finding in key_findings:
                        is_abnormal = finding.get("is_abnormal", False)
                        icon = "⚠️" if is_abnormal else "✅"
                        
                        st.markdown(f"**{icon} {finding.get('finding')}**: {finding.get('value')}")
                        st.caption(f"Interpretation: {finding.get('interpretation')}")
                else:
                    st.write("No specific key findings were extracted.")

            # Display Next Steps and Urgency
            col1, col2 = st.columns(2)
            with col1:
                with st.container(border=True):
                    st.markdown("##### ➡️ Next Steps")
                    st.write(analysis.get("next_steps", "Not specified."))
            with col2:
                with st.container(border=True):
                    st.markdown("##### ❗ Urgency Level")
                    urgency = analysis.get("urgency", "Not specified.")
                    if urgency.lower() == 'high':
                        st.error(urgency)
                    elif urgency.lower() == 'medium':
                        st.warning(urgency)
                    else:
                        st.success(urgency)

        else:
            st.error("The analysis agent failed to produce a valid translation.")

        # For Debugging/Judges: Show the full JSON response
        with st.expander("Show Full JSON Response"):
            st.json(results)