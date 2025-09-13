# File: frontend/symptom.py

import streamlit as st
from utilities import call_agent_api
import re

def show_symptom_page():
    """
    Displays the UI for the Symptom Triage agent and handles the API call.
    This page is accessible to both doctors and patients.
    """
    st.title("Symptom Triage Agent 🤕")
    st.write("Describe your symptoms, and the AI will provide a preliminary triage recommendation based on its knowledge base.")
    
    st.markdown("---")
    
    # --- 1. User Input ---
    if 'symptom_input' not in st.session_state:
        st.session_state.symptom_input = "I have a sharp headache and feel dizzy."

    symptom_text = st.text_area(
        "Describe your symptoms in detail:", 
        value=st.session_state.symptom_input,
        height=150,
        placeholder="e.g., I have a crushing chest pain and feel faint..."
    )
    st.session_state.symptom_input = symptom_text

    if st.button("Get Triage Recommendation", type="primary", use_container_width=True):
        # --- 2. API Call Logic ---
        if symptom_text:
            json_data = {"symptoms": symptom_text}
            response = call_agent_api(agent_type='symptom_triage', json_data=json_data)
            st.session_state.symptom_triage_results = response
        else:
            st.warning("Please describe your symptoms.")
            st.session_state.symptom_triage_results = None

    # --- 3. Display Results ---
    if 'symptom_triage_results' in st.session_state and st.session_state.symptom_triage_results:
        results = st.session_state.symptom_triage_results

        st.markdown("---")
        st.markdown("## Analysis Results")

        # --- Display Agent 2 (Evaluation) ---
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

        # --- Display Agent 1 (Triage Analysis) ---
        st.subheader("Agent 1: Triage Recommendation")
        if "agent1_analysis" in results and not results["agent1_analysis"].get("error"):
            analysis = results["agent1_analysis"]
            rec = analysis.get("recommendation", "No recommendation generated.")
            reasoning = analysis.get("reasoning", "No reasoning provided.")
            
            # Use color-coded containers based on urgency
            if re.search(r'er|emergency', rec, re.IGNORECASE):
                st.error(f"### Recommendation: {rec}", icon="🚨")
                with st.container(border=True):
                    st.markdown("**Reasoning:**")
                    st.write(reasoning)
            elif re.search(r'gp|doctor|clinic', rec, re.IGNORECASE):
                st.warning(f"### Recommendation: {rec}", icon="👨‍⚕️")
                with st.container(border=True):
                    st.markdown("**Reasoning:**")
                    st.write(reasoning)
            else: # Assume home care
                st.success(f"### Recommendation: {rec}", icon="✅")
                with st.container(border=True):
                    st.markdown("**Reasoning & First Aid:**")
                    st.write(reasoning)
        else:
            st.error("The analysis agent failed to produce a valid triage result.")

        # --- CRITICAL DISCLAIMER ---
        st.markdown("---")
        st.warning(
            "**Disclaimer:** This AI-powered triage is for informational purposes only and is NOT a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. If you think you may have a medical emergency, call your doctor or emergency services immediately.",
            icon="⚠️"
        )

        # For Debugging/Judges: Show the full JSON response
        with st.expander("Show Full JSON Response"):
            st.json(results)