import os

import streamlit as st


SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
SUPABASE_BUCKET = st.secrets.get("SUPABASE_BUCKET", os.getenv("SUPABASE_BUCKET", "report-images"))
SUPABASE_TABLE = st.secrets.get("SUPABASE_TABLE", os.getenv("SUPABASE_TABLE", "reports"))
OLLAMA_URL = st.secrets.get("OLLAMA_URL", os.getenv("OLLAMA_URL", "http://localhost:11434"))
OLLAMA_MODEL = st.secrets.get("OLLAMA_MODEL", os.getenv("OLLAMA_MODEL", "llava"))
ENABLE_OLLAMA = str(st.secrets.get("ENABLE_OLLAMA", os.getenv("ENABLE_OLLAMA", "false"))).lower() == "true"

BACKUP_DIRECTORY = "backups/"  # Directory for storing metadata exports
LOGGING_LEVEL = "INFO"