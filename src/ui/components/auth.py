"""
Auth UI component.
Renders the top-right user widget and the login / register modal.
"""
import streamlit as st

from src.services.auth_service import (
    AuthService,
    get_logged_in_user,
    get_user_display_name,
    is_logged_in,
)


def render_auth_widget() -> None:
    """
    Compact top-right widget: shows user name + logout if logged in,
    or Login / Register buttons if not.
    """
    if is_logged_in():
        name = get_user_display_name()
        col_name, col_out = st.columns([3, 1])
        with col_name:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;justify-content:flex-end;">'
                f'<div style="width:30px;height:30px;border-radius:50%;'
                f'background:linear-gradient(135deg,#4f46e5,#a855f7);'
                f'display:flex;align-items:center;justify-content:center;'
                f'color:#fff;font-weight:700;font-size:0.85rem;flex-shrink:0;">'
                f'{name[0].upper()}</div>'
                f'<span style="font-size:0.9rem;font-weight:600;color:var(--text-primary);">'
                f'{name}</span></div>',
                unsafe_allow_html=True,
            )
        with col_out:
            if st.button("Sign out", key="ll_signout_btn", use_container_width=True):
                AuthService().logout()
                st.rerun()
    else:
        col_l, col_r = st.columns(2)
        with col_l:
            if st.button("Log in", key="ll_login_btn", use_container_width=True):
                st.session_state.ll_auth_modal = "login"
                st.rerun()
        with col_r:
            if st.button("Register", key="ll_register_btn",
                         use_container_width=True, type="primary"):
                st.session_state.ll_auth_modal = "register"
                st.rerun()


def render_auth_modal() -> None:
    """
    Full login / register modal. Call this once near the top of main().
    Shows only when st.session_state.ll_auth_modal is 'login' or 'register'.
    """
    mode = st.session_state.get("ll_auth_modal")
    if not mode:
        return

    auth = AuthService()

    st.markdown("---")
    cols = st.columns([1, 2, 1])
    with cols[1]:
        # Header
        icon = "🔐" if mode == "login" else "✨"
        title = "Welcome back to Local Lens" if mode == "login" else "Join Local Lens"
        subtitle = (
            "Log in to submit reports and upvote issues."
            if mode == "login"
            else "Create a free account to report issues and upvote."
        )
        st.markdown(
            f'<div style="text-align:center;margin-bottom:1.5rem;">'
            f'<div style="font-size:2rem;margin-bottom:0.5rem;">{icon}</div>'
            f'<div style="font-size:1.4rem;font-weight:800;letter-spacing:-0.02em;'
            f'color:var(--text-primary);">{title}</div>'
            f'<div style="font-size:0.9rem;color:var(--text-secondary);margin-top:0.4rem;">'
            f'{subtitle}</div></div>',
            unsafe_allow_html=True,
        )

        # Toggle between modes
        toggle_label = "Don't have an account? Register" if mode == "login" else "Already have an account? Log in"
        toggle_target = "register" if mode == "login" else "login"
        tc1, tc2, tc3 = st.columns([1, 2, 1])
        with tc2:
            if st.button(toggle_label, key="ll_auth_toggle", use_container_width=True):
                st.session_state.ll_auth_modal = toggle_target
                st.rerun()

        with st.container(border=True):
            if mode == "login":
                _render_login_form(auth)
            else:
                _render_register_form(auth)

        # Close / cancel
        cc1, cc2, cc3 = st.columns([1, 2, 1])
        with cc2:
            if st.button("✕ Cancel", key="ll_auth_cancel", use_container_width=True):
                st.session_state.ll_auth_modal = None
                st.rerun()

    st.markdown("---")


def _render_login_form(auth: AuthService) -> None:
    with st.form("ll_login_form"):
        email = st.text_input("Email address", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Your password")
        submitted = st.form_submit_button(
            "Log in to Local Lens", use_container_width=True, type="primary"
        )

    if submitted:
        if not email.strip() or not password:
            st.error("Please enter your email and password.")
            return
        with st.spinner("Logging in…"):
            result = auth.login(email, password)
        if result["success"]:
            st.session_state.ll_user = result["user"]
            st.session_state.ll_session = result["session"]
            st.session_state.ll_auth_modal = None
            st.toast(f"Welcome back to Local Lens! 👋", icon="✅")
            st.rerun()
        else:
            st.error(result["message"])


def _render_register_form(auth: AuthService) -> None:
    with st.form("ll_register_form"):
        display_name = st.text_input("Display name", placeholder="How should we call you?")
        email = st.text_input("Email address", placeholder="you@example.com")
        password = st.text_input(
            "Password", type="password",
            placeholder="At least 6 characters",
            help="Minimum 6 characters.",
        )
        password2 = st.text_input("Confirm password", type="password", placeholder="Repeat password")
        submitted = st.form_submit_button(
            "Create my Local Lens account", use_container_width=True, type="primary"
        )

    if submitted:
        if not email.strip() or not password:
            st.error("Email and password are required.")
            return
        if "@" not in email:
            st.error("Please enter a valid email address.")
            return
        if len(password) < 6:
            st.error("Password must be at least 6 characters.")
            return
        if password != password2:
            st.error("Passwords do not match.")
            return
        with st.spinner("Creating your account…"):
            result = auth.register(email, password, display_name)
        if result["success"]:
            # Auto-login after registration
            login_result = auth.login(email, password)
            if login_result["success"]:
                st.session_state.ll_user = login_result["user"]
                st.session_state.ll_session = login_result["session"]
            st.session_state.ll_auth_modal = None
            st.toast("Welcome to Local Lens! 🎉", icon="✨")
            st.rerun()
        else:
            st.error(result["message"])


def require_auth_prompt(action: str = "do this") -> bool:
    """
    Show a polished prompt asking users to log in.
    Returns True if the user is logged in (caller can proceed),
    False if not (prompt is shown instead).
    """
    from src.services.auth_service import is_logged_in
    if is_logged_in():
        return True

    st.markdown(
        f'<div style="border-radius:14px;border:1px solid var(--border-accent);'
        f'background:{"rgba(99,102,241,0.08)" };padding:1.5rem;text-align:center;'
        f'margin:1rem 0;">'
        f'<div style="font-size:1.6rem;margin-bottom:0.5rem;">🔐</div>'
        f'<div style="font-weight:700;font-size:1rem;color:var(--text-primary);'
        f'margin-bottom:0.4rem;">Sign in to {action}</div>'
        f'<div style="font-size:0.875rem;color:var(--text-secondary);">'
        f'Local Lens accounts are free and take 30 seconds to create.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Log in", key=f"prompt_login_{action[:8]}", use_container_width=True):
            st.session_state.ll_auth_modal = "login"
            st.rerun()
    with c2:
        if st.button("Register free", key=f"prompt_reg_{action[:8]}",
                     use_container_width=True, type="primary"):
            st.session_state.ll_auth_modal = "register"
            st.rerun()
    return False