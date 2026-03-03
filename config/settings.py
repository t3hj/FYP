import os

import streamlit as st


SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
SUPABASE_BUCKET = st.secrets.get("SUPABASE_BUCKET", os.getenv("SUPABASE_BUCKET", "report-images"))
SUPABASE_TABLE = st.secrets.get("SUPABASE_TABLE", os.getenv("SUPABASE_TABLE", "reports"))

BACKUP_DIRECTORY = "backups/"  # Directory for storing metadata exports
LOGGING_LEVEL = "INFO"