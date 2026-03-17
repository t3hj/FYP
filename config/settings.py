import os

import streamlit as st


SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
SUPABASE_BUCKET = st.secrets.get("SUPABASE_BUCKET", os.getenv("SUPABASE_BUCKET", "report-images"))
SUPABASE_TABLE = st.secrets.get("SUPABASE_TABLE", os.getenv("SUPABASE_TABLE", "reports"))
OLLAMA_URL = st.secrets.get("OLLAMA_URL", os.getenv("OLLAMA_URL", "http://localhost:11434"))
OLLAMA_MODEL = st.secrets.get("OLLAMA_MODEL", os.getenv("OLLAMA_MODEL", "llava"))
ENABLE_OLLAMA = str(st.secrets.get("ENABLE_OLLAMA", os.getenv("ENABLE_OLLAMA", "false"))).lower() == "true"
REQUIRE_AI = str(st.secrets.get("REQUIRE_AI", os.getenv("REQUIRE_AI", "false"))).lower() == "true"
REQUIRE_GEOLOCATION = str(st.secrets.get("REQUIRE_GEOLOCATION", os.getenv("REQUIRE_GEOLOCATION", "false"))).lower() == "true"
ENABLE_GEOCODING = str(st.secrets.get("ENABLE_GEOCODING", os.getenv("ENABLE_GEOCODING", "true"))).lower() == "true"
# Anthropic Claude API key — used for cloud-hosted AI image analysis
ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))


# Optional password protecting council-only views such as analytics.
# Set COUNCIL_ADMIN_PASSWORD in `.streamlit/secrets.toml` or environment variables.
COUNCIL_ADMIN_PASSWORD = st.secrets.get(
    "COUNCIL_ADMIN_PASSWORD",
    os.getenv("COUNCIL_ADMIN_PASSWORD", ""),
)

BACKUP_DIRECTORY = "backups/"  # Directory for storing metadata exports
LOGGING_LEVEL = "INFO"