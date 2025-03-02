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
        st.info("This application requires the Anthropic Claude API for scientific analysis.")
        return

    # Run the main application
    main_page()

if __name__ == "__main__":
    main()