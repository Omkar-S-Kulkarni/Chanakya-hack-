import streamlit as st
import webbrowser

# This page is now only for doctors
if st.session_state.user_role == "doctor":
    st.title("Knowledge Base & Updates 🧠")
    st.write("Access the internal knowledge base and get summaries of the latest medical updates.")

    st.markdown("### Internal Knowledge Base")
    st.text_input("Search the knowledge base", placeholder="e.g., Warfarin interactions, hypertension guidelines")
    st.button("Search", type="primary")
    
    st.markdown("---")
    
    st.markdown("### External Resources & Summaries")
    st.subheader("WHO Healthcare Updates")
    
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Go to WHO Website"):
            webbrowser.open_new_tab('https://www.who.int')
            
    st.text_input("Paste URL from WHO website to summarize", placeholder="https://www.who.int/news/...")

    if st.button("Generate Summary"):
        # This is a placeholder for the real summarization model output
        st.session_state.summary_output = True

    if 'summary_output' in st.session_state and st.session_state.summary_output:
        st.markdown("#### Summary of Update:")
        with st.container(border=True):
            st.success("**Key Findings:** A new study indicates a strong correlation between Vitamin D deficiency and increased risk of respiratory infections.")
            st.markdown("""
                - **Population:** Study included over 50,000 participants across multiple countries.
                - **Recommendation:** Clinicians should consider screening at-risk patient populations.
                - **Action:** Advise patients on safe sun exposure and dietary sources of Vitamin D.
            """)
        st.info("Disclaimer: This is an AI-generated summary. Please refer to the original article for full details.")