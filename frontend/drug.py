# File: frontend/drug.py

import streamlit as st
from utilities import call_agent_api

def show_drug_page():
    """
    Displays the UI for the Drug Safety & Dosage agent and handles the API call.
    """
    st.title("Drug Safety & Dosage Agent 💊")
    st.write("Enter one or more medication names to check for potential interactions and get AI-powered information.")
    
    st.markdown("---")
    
    # --- 1. User Input ---
    # Use session state to remember the last input
    if 'medications_input' not in st.session_state:
        st.session_state.medications_input = "Aspirin, Warfarin" # Example default

    med_input = st.text_input(
        "Enter Medications (comma-separated)", 
        value=st.session_state.medications_input,
        placeholder="e.g., Aspirin, Warfarin, Ibuprofen"
    )
    st.session_state.medications_input = med_input # Update session state on each key press

    # Analyze button
    if st.button("Analyze My Meds", type="primary", use_container_width=True):
        # --- 2. API Call Logic ---
        if med_input:
            # Prepare data for the API
            medication_list = [med.strip() for med in med_input.split(',') if med.strip()]
            json_data = {"medications": medication_list}
            
            # Call the backend and store the full response in session state
            response = call_agent_api(agent_type='drug_safety', json_data=json_data)
            st.session_state.drug_safety_results = response
        else:
            st.warning("Please enter at least one medication name.")
            st.session_state.drug_safety_results = None

    # --- 3. Display Results ---
    # Check if results exist in the session state
    if 'drug_safety_results' in st.session_state and st.session_state.drug_safety_results:
        results = st.session_state.drug_safety_results
        
        st.markdown("---")
        st.markdown("## Analysis Results")

        # --- Display Agent 2 (Evaluation) First ---
        st.subheader("Agent 2: Quality & Safety Review")
        if "agent2_evaluation" in results and not results["agent2_evaluation"].get("error"):
            eval_data = results["agent2_evaluation"]
            score = eval_data.get("overall_quality_score", "N/A")
            recommendation = eval_data.get("final_recommendation", "No recommendation provided.")
            
            with st.container(border=True):
                st.markdown(f"##### Overall Quality Score: **{score} / 5.0**")
                st.info(f"**Reviewer's Note:** {recommendation}")
        else:
            st.warning("The evaluation agent could not review this result.")

        # --- Display Agent 1 (Analysis) ---
        st.subheader("Agent 1: Detailed Analysis")
        if "agent1_analysis" in results and not results["agent1_analysis"].get("error"):
            analysis = results["agent1_analysis"]
            
            # Display Safety Alerts from the Rule Engine
            with st.expander("🚨 Safety Alerts", expanded=True):
                alerts = analysis.get("safety_alerts", [])
                if not alerts:
                    st.success("No critical safety alerts were found by the Rule Engine.")
                else:
                    for alert in alerts:
                        severity = alert.get("severity", "Medium")
                        if severity == "High" or severity == "Critical":
                            st.error(f"**{alert.get('type')}:** {alert.get('message')}")
                        else:
                            st.warning(f"**{alert.get('type')}:** {alert.get('message')}")

            # Display Drug Information from the Gemini Agent
            with st.expander("ℹ️ Drug Information", expanded=True):
                drug_info = analysis.get("drug_information", [])
                if drug_info:
                    for drug in drug_info:
                        st.markdown(f"##### {drug.get('drug_name')}")
                        st.write(drug.get('info'))
                else:
                    st.write("No detailed information was generated for the provided drugs.")

            # Display Questions for Doctor
            with st.expander("❓ Questions for Your Doctor", expanded=False):
                questions = analysis.get("questions_for_your_doctor", [])
                if questions:
                    for q in questions:
                        st.markdown(f"- {q}")

        else:
            st.error("The analysis agent failed to produce a valid result.")
        
        # --- For Debugging/Judges: Show the full JSON response ---
        with st.expander("Show Full JSON Response"):
            st.json(results)