import streamlit as st
from scidiscover.ui.pages import main_page
import os
from pathlib import Path

def load_env_from_file():
    """Load environment variables from .env file if it exists"""
    env_path = Path('.') / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Parse key-value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Set environment variable if not already set
                    if not os.getenv(key.strip()):
                        os.environ[key.strip()] = value.strip()

def render_disclaimer():
    """Render a small disclaimer link in the footer"""
    st.markdown("<a href='https://github.com/ardeshirlab/scidiscover/blob/main/DISCLAIMER.md' target='_blank'>Disclaimer</a>", unsafe_allow_html=True)

def main():
    # Load environment variables from .env file
    load_env_from_file()
    
    # Set page config
    st.set_page_config(
        page_title="SciDiscover",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Check for required environment variables
    if not os.getenv("ANTHROPIC_API_KEY"):
        st.error("API Key Missing: ANTHROPIC_API_KEY environment variable not found.")
        
        env_file = Path('.env')
        env_example = Path('.env.example')
        
        if env_example.exists() and not env_file.exists():
            st.warning("The .env file is missing. Copy .env.example to .env and add your API key.")
            st.code("cp .env.example .env", language="bash")
            st.info("Then edit the .env file to add your Anthropic API key.")
        
        st.markdown("""
        ### How to Set Up Your API Key
        
        1. Create an account on [Anthropic's website](https://console.anthropic.com/)
        2. Generate an API key from the Anthropic console
        3. Add your API key to the .env file:
           ```
           ANTHROPIC_API_KEY=your_actual_key_here
           ```
        
        ### Why This is Needed
        
        SciDiscover uses Claude 3.7 Sonnet's extended thinking capabilities:
        - Comprehensive scientific analysis with 128K output tokens
        - Complex multi-step reasoning with up to 64K thinking tokens
        - Advanced scientific discovery features for hypothesis generation
        
        Once your API key is set up, reload this page to continue.
        """)
        return

    # Run the main application
    main_page()

if __name__ == "__main__":
    main()