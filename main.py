import streamlit as st
from scidiscover.ui.pages import main_page
import os

def main():
    # Set page config
    st.set_page_config(
        page_title="SciDiscover",
        page_icon="🧬",
        layout="wide"
    )
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("ANTHROPIC_API_KEY"):
        st.error("Please set the required API keys in environment variables.")
        return
    
    # Run the main application
    main_page()

if __name__ == "__main__":
    main()
