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

    # Check for required environment variables and provide guidance
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("ANTHROPIC_API_KEY"):
        st.error("Please set the required API keys in environment variables.")
        st.info("""
        This application requires both OpenAI and Anthropic API keys.

        ### Anthropic API Key
        This application uses Claude 3.7 Sonnet with extended thinking capabilities.
        Get your API key from [Anthropic Console](https://console.anthropic.com/).

        ### OpenAI API Key
        Get your API key from [OpenAI Platform](https://platform.openai.com/).
        """)
        return

    # Run the main application
    main_page()

if __name__ == "__main__":
    main()