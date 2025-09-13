import streamlit as st

def show_patient_summary():
    """Displays a simple patient summary bar."""
    st.markdown("---")
    st.markdown(
        """
        <div style="background-color: #e0f7fa; padding: 15px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
            <div style="display: flex; gap: 20px;">
                <span style="font-weight: bold;">👤 John Doe</span>
                <span>Age: 45</span>
                <span>Weight: 80 kg</span>
                <span>Allergies: Penicillin, NSAIDs</span>
                <span><span style="background-color: #ffcdd2; color: #b71c1c; padding: 3px 8px; border-radius: 5px;">Renal Flag</span></span>
            </div>
            <button style="background-color: #0078D4; color: white; border: none; padding: 8px 15px; border-radius: 5px;">EDIT</button>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")