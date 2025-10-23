import os
from dotenv import load_dotenv

load_dotenv()

# Support both .env (local) and Streamlit secrets.toml (cloud)
# Streamlit automatically loads from secrets.toml when running on share.streamlit.io

def get_secret(key, default=None):
    """
    Get secret from environment or Streamlit secrets.
    Supports both local (.env) and cloud (secrets.toml) deployments.
    """
    # Try environment variable first
    value = os.getenv(key)
    if value:
        return value

    # Try Streamlit secrets (if running in Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except (ImportError, AttributeError):
        pass

    return default

GOOGLE_API_KEY = get_secret('GOOGLE_API_KEY')
GOOGLE_SEARCH_ENGINE_ID = get_secret('GOOGLE_SEARCH_ENGINE_ID')
GEMINI_API_KEY = get_secret('GEMINI_API_KEY')
