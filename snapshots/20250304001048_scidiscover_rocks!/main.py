import streamlit as st
from scidiscover.ui.pages import main_page
import os

def main():
    # Set page config
    st.set_page_config(
        page_title="SciDiscover",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Check for required environment variables
    if not os.getenv("ANTHROPIC_API_KEY"):
        st.error("Please set the ANTHROPIC_API_KEY environment variable to use Claude-3 for analysis.")
        st.info("This application requires the Anthropic Claude API for scientific analysis with extended thinking capabilities.")
        st.markdown("""
        ### Claude 3.7 Sonnet Extended Thinking

        This application leverages Claude 3.7 Sonnet's extended thinking capabilities:
        - 128K output tokens - providing comprehensive scientific analysis
        - 32K thinking budget - enabling complex multi-step reasoning
        - Beta features for specialized scientific discovery

        Please set the ANTHROPIC_API_KEY environment variable to continue.
        """)
        return

    # Run the main application
    main_page()

if __name__ == "__main__":
    main()