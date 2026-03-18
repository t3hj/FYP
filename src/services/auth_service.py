"""
Authentication service — wraps Supabase Auth.
Handles sign-up, sign-in, sign-out, and session management.
"""
import streamlit as st
from src.database.supabase_client import get_supabase_client


class AuthService:
    def __init__(self):
        self.client = get_supabase_client()

    # ── Sign up ───────────────────────────────────────────────────────────────
    def register(self, email: str, password: str, display_name: str = "") -> dict:
        try:
            response = self.client.auth.sign_up({
                "email": email.strip(),
                "password": password,
                "options": {
                    "data": {"display_name": display_name.strip() or email.split("@")[0]}
                },
            })
            if response.user:
                return {"success": True, "user": response.user}
            return {"success": False, "message": "Registration failed. Please try again."}
        except Exception as e:
            msg = str(e)
            if "already registered" in msg.lower() or "already exists" in msg.lower():
                return {"success": False, "message": "This email is already registered. Please log in."}
            return {"success": False, "message": msg}

    # ── Sign in ───────────────────────────────────────────────────────────────
    def login(self, email: str, password: str) -> dict:
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email.strip(),
                "password": password,
            })
            if response.user and response.session:
                return {
                    "success": True,
                    "user": response.user,
                    "session": response.session,
                }
            return {"success": False, "message": "Invalid email or password."}
        except Exception as e:
            msg = str(e).lower()
            if "invalid" in msg or "credentials" in msg or "password" in msg:
                return {"success": False, "message": "Invalid email or password."}
            return {"success": False, "message": str(e)}

    # ── Sign out ──────────────────────────────────────────────────────────────
    def logout(self) -> None:
        try:
            self.client.auth.sign_out()
        except Exception:
            pass
        for key in ("ll_user", "ll_session", "ll_user_votes"):
            st.session_state.pop(key, None)

    # ── Restore session from stored access token ──────────────────────────────
    def restore_session(self, access_token: str, refresh_token: str) -> dict:
        try:
            response = self.client.auth.set_session(access_token, refresh_token)
            if response.user:
                return {"success": True, "user": response.user, "session": response.session}
        except Exception:
            pass
        return {"success": False}

    # ── Get current user (from Supabase directly) ─────────────────────────────
    def get_current_user(self):
        try:
            return self.client.auth.get_user().user
        except Exception:
            return None


# ── Session state helpers ─────────────────────────────────────────────────────

def init_auth_state() -> None:
    """Initialise auth-related session state keys."""
    for key in ("ll_user", "ll_session", "ll_user_votes"):
        if key not in st.session_state:
            st.session_state[key] = None


def get_logged_in_user():
    """Return the current user dict from session state, or None."""
    return st.session_state.get("ll_user")


def is_logged_in() -> bool:
    return st.session_state.get("ll_user") is not None


def get_user_display_name() -> str:
    user = get_logged_in_user()
    if not user:
        return ""
    meta = getattr(user, "user_metadata", {}) or {}
    return meta.get("display_name") or getattr(user, "email", "User").split("@")[0]


def get_user_id() -> str | None:
    user = get_logged_in_user()
    return str(user.id) if user else None