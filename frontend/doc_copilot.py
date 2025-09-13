# File: frontend/doc_copilot.py

import streamlit as st
from utilities import call_agent_api

def show_doc_copilot_page():
    """
    Displays the UI for the Doctor's Co-Pilot agent.
    This page is restricted to users with the 'doctor' role.
    """
    # --- 1. Role Check ---
    if st.session_state.user_role != "doctor":
        st.warning("This feature is available for doctors only.")
        st.info("Please select another tool from the sidebar.")
        return

    st.title("Doctor's Co-Pilot 👨‍⚕️")
    st.write("Streamline your clinical documentation. Paste an encounter note to generate a structured SOAP summary, check it against guidelines, and draft orders.")
    
    st.markdown("---")

    # --- 2. User Input ---
    if 'encounter_note_input' not in st.session_state:
        st.session_state.encounter_note_input = "Pt c/o sore throat x 3 days, fever 101.2F. Exam shows erythematous pharynx. Rapid strep test is positive. Plan to start Amoxicillin 500mg TID for 10 days."

    note_text = st.text_area(
        "Paste short encounter note or transcript here", 
        height=200,
        value=st.session_state.encounter_note_input
    )
    st.session_state.encounter_note_input = note_text

    if st.button("Generate Clinical Summary", type="primary", use_container_width=True):
        # --- 3. API Call Logic ---
        if note_text:
            json_data = {"note": note_text}
            response = call_agent_api(agent_type='doctors_copilot', json_data=json_data)
            st.session_state.copilot_results = response
        else:
            st.warning("Please enter an encounter note.")
            st.session_state.copilot_results = None

    # --- 4. Display Results ---
    if 'copilot_results' in st.session_state and st.session_state.copilot_results:
        results = st.session_state.copilot_results
        
        st.markdown("---")
        st.markdown("## Co-Pilot Generated Output")

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

        # --- Display Agent 1 (Co-Pilot Analysis) ---
        st.subheader("Agent 1: Clinical Analysis")
        if "agent1_analysis" in results and not results["agent1_analysis"].get("error"):
            analysis = results["agent1_analysis"]
            
            # Display Editable SOAP Note Draft
            with st.expander("📝 SOAP Note Draft", expanded=True):
                soap = analysis.get("soap_summary", {})
                st.text_area("S: Subjective", value=soap.get("subjective", ""), height=100)
                st.text_area("O: Objective", value=soap.get("objective", ""), height=100)
                st.text_area("A: Assessment", value=soap.get("assessment", ""), height=75)
                st.text_area("P: Plan", value=soap.get("plan", ""), height=100)

            # Display Guideline Checklist
            with st.expander("✅ Guideline Checklist (from RAG)", expanded=True):
                checklist = analysis.get("guideline_checklist", [])
                if checklist:
                    for item in checklist:
                        status = item.get("status", "Unknown").lower()
                        icon = "✅" if status == "addressed" else ("⚠️" if status == "partially addressed" else "❌")
                        st.markdown(f"**{icon} Guideline:** {item.get('guideline')}")
                        st.caption(f"Status: {item.get('status')} - Reason: {item.get('reason')}")
                else:
                    st.info("No specific guidelines were retrieved from the knowledge base for this note.")

            # Display Draft Orders
            with st.expander("📋 Draft Orders", expanded=True):
                orders = analysis.get("draft_orders", {})
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("##### Suggested Labs")
                    labs = orders.get("suggested_labs", [])
                    if labs:
                        for lab in labs: st.markdown(f"- {lab}")
                    else:
                        st.write("None")
                with col2:
                    st.markdown("##### Suggested Medications")
                    meds = orders.get("suggested_medications", [])
                    if meds:
                        for med in meds: st.markdown(f"- {med}")
                    else:
                        st.write("None")
        else:
            st.error("The analysis agent failed to produce a valid clinical summary.")

        # For Debugging/Judges: Show the full JSON response
        with st.expander("Show Full JSON Response"):
            st.json(results)