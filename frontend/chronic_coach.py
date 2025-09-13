# File: frontend/chronic_coach.py

import streamlit as st
import pandas as pd
import altair as alt
from utilities import call_agent_api

def show_chronic_coach_page():
    """
    Displays the UI for the Chronic Care Coach, handles file uploads,
    visualizes the data, and shows AI-powered trend analysis.
    """
    st.title("Chronic Care Coach 📈")
    st.write("Upload your health log (CSV or Excel) to track your trends and get personalized insights from your AI coach.")

    st.markdown("---")

    # --- 1. User Input: File Uploader ---
    uploaded_file = st.file_uploader(
        "Upload your BP or Glucose log",
        type=['csv', 'xlsx', 'xls'],
        key="chronic_care_uploader"
    )

    if st.button("Analyze Trends", type="primary", use_container_width=True):
        # --- 2. API Call & Data Processing Logic ---
        if uploaded_file is not None:
            # First, process the file for charting
            try:
                # Read the uploaded file into a Pandas DataFrame
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Store the DataFrame in session state so we can display it later
                st.session_state.chronic_care_df = df
                
                # Now, call the backend API with the same file
                response = call_agent_api(agent_type='chronic_care', json_data={}, file=uploaded_file)
                st.session_state.chronic_care_results = response

            except Exception as e:
                st.error(f"Failed to read or process the file. Please ensure it's a valid CSV or Excel file. Error: {e}")
                st.session_state.chronic_care_results = None
                st.session_state.chronic_care_df = None
        else:
            st.warning("Please upload a file first.")
            st.session_state.chronic_care_results = None
            st.session_state.chronic_care_df = None

    # --- 3. Display Results ---
    if 'chronic_care_results' in st.session_state and st.session_state.chronic_care_results:
        results = st.session_state.chronic_care_results
        
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

        # --- Display Agent 1 (Chronic Care Analysis) ---
        st.subheader("Agent 1: Your AI Coach's Insights")
        if "agent1_analysis" in results and not results["agent1_analysis"].get("error"):
            analysis = results["agent1_analysis"]
            
            # Display Risk Assessment with color coding
            risk = analysis.get("risk_assessment", {})
            risk_level = risk.get("level", "Unknown").lower()
            
            if risk_level in ["high", "elevated"]:
                st.error(f"**Risk Assessment:** {risk.get('level')} - {risk.get('reason')}", icon="⚠️")
            else:
                st.success(f"**Risk Assessment:** {risk.get('level')} - {risk.get('reason')}", icon="✅")

            # Display Trend Summary and Nudges
            col1, col2 = st.columns(2)
            with col1:
                with st.container(border=True):
                    st.markdown("#####  Trend Summary")
                    st.write(analysis.get("trend_summary", "No summary provided."))
            with col2:
                with st.container(border=True):
                    st.markdown("##### Behavioral Nudges")
                    nudges = analysis.get("behavioral_nudges", [])
                    for nudge in nudges:
                        st.markdown(f"- {nudge}")

        # --- Display the Dynamic Chart ---
        st.subheader("Your Health Data Visualization")
        if 'chronic_care_df' in st.session_state and st.session_state.chronic_care_df is not None:
            df = st.session_state.chronic_care_df
            # A simple attempt to find date and value columns for charting
            try:
                # Basic column name cleaning for robustness
                df.columns = df.columns.str.lower().str.strip()
                date_col = next((col for col in df.columns if 'date' in col or 'time' in col), df.columns[0])
                value_cols = [col for col in df.columns if col not in [date_col]]
                
                df[date_col] = pd.to_datetime(df[date_col])

                chart = alt.Chart(df).mark_line(point=True).encode(
                    x=alt.X(f'{date_col}:T', title='Date'),
                    y=alt.Y(f'{value_cols[0]}:Q', title=value_cols[0].capitalize()),
                    tooltip=[date_col] + value_cols
                ).interactive()
                st.altair_chart(chart, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not automatically generate a chart from the uploaded file. Error: {e}")
                st.dataframe(df) # Show the raw data instead
        
        # For Debugging/Judges: Show the full JSON response
        with st.expander("Show Full JSON Response"):
            st.json(results)