from functools import lru_cache

from supabase import create_client

from config.settings import SUPABASE_KEY, SUPABASE_URL


@lru_cache(maxsize=1)
def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "Supabase credentials are missing. Set SUPABASE_URL and SUPABASE_KEY in .streamlit/secrets.toml"
        )

    return create_client(SUPABASE_URL, SUPABASE_KEY)
