"""
Auth UI component.
Renders the top-right user widget and the login / register modal.
"""
import streamlit as st
import streamlit.components.v1 as components

from src.services.auth_service import (
    AuthService,
    get_user_display_name,
    is_logged_in,
)


def _scroll_to_top() -> None:
    """Inject JS to scroll the Streamlit app to the top so the modal is visible."""
    components.html(
        """
        <script>
            const containers = window.parent.document.querySelectorAll(
                'section[data-testid="stMainBlockContainer"], .main, .block-container'
            );
            containers.forEach(el => el.scrollTo({ top: 0, behavior: 'smooth' }));
            window.parent.scrollTo({ top: 0, behavior: 'smooth' });
        </script>
        """,
        height=0,
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
                st.session_state.ll_scroll_to_modal = True
                st.rerun()
        with col_r:
            if st.button("Register", key="ll_register_btn",
                         use_container_width=True, type="primary"):
                st.session_state.ll_auth_modal = "register"
                st.session_state.ll_scroll_to_modal = True
                st.rerun()


def render_auth_modal() -> None:
    """
    Full login / register modal. Call this once near the top of main(),
    BEFORE the hero section so it renders at the top of the page.
    Shows only when st.session_state.ll_auth_modal is 'login' or 'register'.
    """
    mode = st.session_state.get("ll_auth_modal")
    if not mode:
        return

    # Scroll to top so the modal is immediately visible
    if st.session_state.get("ll_scroll_to_modal"):
        _scroll_to_top()
        st.session_state.ll_scroll_to_modal = False

    auth = AuthService()

    cols = st.columns([1, 2, 1])
    with cols[1]:
        icon = "🔐" if mode == "login" else "✨"
        title = "Welcome back to Local Lens" if mode == "login" else "Join Local Lens"
        subtitle = (
            "Log in to submit reports and upvote issues."
            if mode == "login"
            else "Create a free account to report and upvote community issues."
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

        with st.container(border=True):
            if mode == "login":
                _render_login_form(auth)
            else:
                _render_register_form(auth)

        cc1, cc2, cc3 = st.columns([1, 2, 1])
        with cc2:
            if st.button("✕ Cancel", key="ll_auth_cancel", use_container_width=True):
                st.session_state.ll_auth_modal = None
                st.session_state.ll_registration_pending_email = None
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
            st.session_state.ll_user_votes = None  # reload on next render
            st.toast("Welcome back to Local Lens! 👋", icon="✅")
            st.rerun()
        else:
            msg = result["message"]
            if "confirm" in msg.lower() or "verif" in msg.lower() or "email" in msg.lower():
                st.warning(
                    "📧 Please confirm your email first. "
                    "Check your inbox for the Local Lens verification link, "
                    "then try logging in again."
                )
            else:
                st.error(msg)

    # Switch to register
    st.markdown(
        '<div style="text-align:center;margin-top:0.75rem;">'
        '<span style="font-size:0.875rem;color:var(--text-secondary);">'
        "Don't have an account?</span></div>",
        unsafe_allow_html=True,
    )
    if st.button(
        "Create a free Local Lens account →",
        key="ll_switch_to_register",
        use_container_width=True,
    ):
        st.session_state.ll_auth_modal = "register"
        st.rerun()


def _render_register_form(auth: AuthService) -> None:
    # ── Post-registration: show email confirmation notice ─────────────────────
    if st.session_state.get("ll_registration_pending_email"):
        pending_email = st.session_state.ll_registration_pending_email
        st.success("🎉 Account created!")
        st.markdown(
            f'<div style="border-radius:12px;border:1px solid rgba(99,102,241,0.3);'
            f'background:rgba(99,102,241,0.08);padding:1.25rem;margin:0.75rem 0;">'
            f'<div style="font-weight:700;margin-bottom:0.5rem;color:var(--text-primary);">'
            f'📧 One more step — confirm your email</div>'
            f'<div style="font-size:0.9rem;color:var(--text-secondary);line-height:1.65;">'
            f'We sent a confirmation link to <strong>{pending_email}</strong>.<br><br>'
            f'Click the link in that email to activate your Local Lens account, '
            f'then come back here and log in.'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "Go to Log in →",
            key="ll_confirm_to_login",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.ll_auth_modal = "login"
            st.session_state.ll_registration_pending_email = None
            st.rerun()

        if st.button(
            "Resend confirmation email",
            key="ll_resend_confirm",
            use_container_width=True,
        ):
            try:
                auth.client.auth.resend({"type": "signup", "email": pending_email})
                st.toast("Confirmation email resent! Check your inbox.", icon="📧")
            except Exception:
                st.toast("Could not resend — please try again shortly.", icon="⚠️")
        return

    # ── Registration form ─────────────────────────────────────────────────────
    with st.form("ll_register_form"):
        display_name = st.text_input("Display name", placeholder="How should we call you?")
        email = st.text_input("Email address", placeholder="you@example.com")
        password = st.text_input(
            "Password",
            type="password",
            placeholder="At least 6 characters",
            help="Minimum 6 characters.",
        )
        password2 = st.text_input(
            "Confirm password", type="password", placeholder="Repeat password"
        )
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
            st.session_state.ll_registration_pending_email = email.strip()
            st.rerun()
        else:
            st.error(result["message"])

    # Switch to login — shown at bottom of registration form
    st.markdown(
        '<div style="text-align:center;margin-top:0.75rem;">'
        '<span style="font-size:0.875rem;color:var(--text-secondary);">'
        "Already have an account?</span></div>",
        unsafe_allow_html=True,
    )
    if st.button(
        "Log in to Local Lens →",
        key="ll_switch_to_login",
        use_container_width=True,
    ):
        st.session_state.ll_auth_modal = "login"
        st.rerun()


def require_auth_prompt(action: str = "do this") -> bool:
    """
    Show a polished prompt asking users to log in.
    Returns True if logged in (caller can proceed), False if not.
    """
    if is_logged_in():
        return True

    st.markdown(
        f'<div style="border-radius:14px;border:1px solid var(--border-accent);'
        f'background:rgba(99,102,241,0.08);padding:1.5rem;text-align:center;margin:1rem 0;">'
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
            st.session_state.ll_scroll_to_modal = True
            st.rerun()
    with c2:
        if st.button("Register free", key=f"prompt_reg_{action[:8]}",
                     use_container_width=True, type="primary"):
            st.session_state.ll_auth_modal = "register"
            st.session_state.ll_scroll_to_modal = True
            st.rerun()
    return False