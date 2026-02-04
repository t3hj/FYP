"""
Authentication module for Local Lens application.
Handles admin/council login and role-based access control.
"""
import streamlit as st


# Admin password - in production, use st.secrets["ADMIN_PASSWORD"]
def get_admin_password():
    """Get admin password from secrets or use default for demo"""
    try:
        return st.secrets.get("ADMIN_PASSWORD", "admin123")
    except:
        return "admin123"  # Default for local development


def is_admin():
    """Check if current user is logged in as admin"""
    return st.session_state.get("admin_authenticated", False)


def login_admin(password):
    """Attempt to log in as admin
    
    Args:
        password (str): Password to verify
        
    Returns:
        bool: True if login successful
    """
    if password == get_admin_password():
        st.session_state.admin_authenticated = True
        return True
    return False


def logout_admin():
    """Log out the admin user"""
    st.session_state.admin_authenticated = False


def display_auth_header():
    """Display login/logout button in the header area"""
    
    # Create columns for header with login on the right
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("📍 Local Lens")
    
    with col2:
        if is_admin():
            st.markdown("👤 **Council Admin**")
            if st.button("🔓 Logout", key="header_logout"):
                logout_admin()
                st.rerun()
        else:
            with st.popover("🔐 Council Login"):
                st.markdown("**Council/Admin Access**")
                password = st.text_input("Password", type="password", key="header_password")
                if st.button("Login", key="header_login"):
                    if login_admin(password):
                        st.success("✅ Logged in!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid password")


def require_admin(func):
    """Decorator to require admin access for a function"""
    def wrapper(*args, **kwargs):
        if not is_admin():
            st.warning("🔒 This feature requires admin access.")
            return None
        return func(*args, **kwargs)
    return wrapper
