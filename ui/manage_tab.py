"""
Manage Reports tab for Local Lens application.
Includes admin authentication for destructive actions.
"""
import streamlit as st

from config import ISSUE_CATEGORIES, STATUS_OPTIONS, PRIORITY_OPTIONS
from database import (
    get_all_reports, update_report_status, update_report_priority,
    update_report, delete_report
)
from styles import get_tab_header, TAB_GRADIENTS


# Admin password - in production, use st.secrets["ADMIN_PASSWORD"]
def get_admin_password():
    """Get admin password from secrets or use default for demo"""
    try:
        return st.secrets.get("ADMIN_PASSWORD", "admin123")
    except:
        return "admin123"  # Default for local development


def check_admin_auth():
    """Check if admin is authenticated in session"""
    return st.session_state.get("admin_authenticated", False)


def manage_reports_tab():
    """Tab 3: Manage existing reports (admin protected)"""
    
    # Header card
    st.markdown(get_tab_header(
        "⚙️ Manage Reports",
        "Update status, priority, or edit report details (Admin only)",
        TAB_GRADIENTS['manage']
    ), unsafe_allow_html=True)
    
    # Admin authentication section
    if not check_admin_auth():
        st.warning("🔒 This section requires admin authentication to prevent unauthorized changes.")
        
        with st.form("admin_login"):
            st.write("### Admin Login")
            password = st.text_input("Enter admin password", type="password")
            
            if st.form_submit_button("🔓 Login"):
                if password == get_admin_password():
                    st.session_state.admin_authenticated = True
                    st.success("✅ Authentication successful!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password")
        
        st.info("💡 For demo purposes, contact the developer for access.")
        return
    
    # Show logout option
    col_logout, col_spacer = st.columns([1, 4])
    with col_logout:
        if st.button("🔒 Logout"):
            st.session_state.admin_authenticated = False
            st.rerun()
    
    st.success("✅ Logged in as Admin")
    
    # Get all reports
    all_reports = get_all_reports()
    
    if not all_reports:
        st.info("No reports to manage. Submit a report first!")
        return
    
    # Create a selectbox for choosing report
    report_options = [f"#{r[0]} - {r[2]} - {r[3][:30]}..." for r in all_reports]
    selected_index = st.selectbox(
        "Select Report to Manage",
        options=range(len(all_reports)),
        format_func=lambda i: report_options[i]
    )
    
    if selected_index is not None:
        selected_report = all_reports[selected_index]
        # Handle both old records (8 columns) and new records (9 columns with email)
        if len(selected_report) >= 9:
            report_id, image_path, category, location, additional_details, timestamp, status, priority, email = selected_report
        else:
            report_id, image_path, category, location, additional_details, timestamp, status, priority = selected_report
            email = None
        
        # Display report details
        st.markdown("---")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            try:
                st.image(image_path, caption=f"Report #{report_id}", use_container_width=True)
            except:
                st.write("Image not available")
        
        with col2:
            st.subheader(f"Report #{report_id}")
            st.write(f"**Submitted:** {timestamp}")
            st.write(f"**Current Category:** {category}")
            st.write(f"**Location:** {location}")
            st.write(f"**Current Status:** {status}")
            st.write(f"**Current Priority:** {priority}")
            if email:
                st.write(f"**Contact Email:** {email}")
            if additional_details:
                st.write(f"**Details:** {additional_details}")
        
        st.markdown("---")
        
        # Management actions
        st.subheader("🔧 Quick Actions")
        
        action_col1, action_col2 = st.columns(2)
        
        with action_col1:
            # Update status
            new_status = st.selectbox(
                "Update Status",
                options=STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(status) if status in STATUS_OPTIONS else 0,
                key=f"status_{report_id}"
            )
            if st.button("Update Status", key=f"btn_status_{report_id}"):
                if update_report_status(report_id, new_status):
                    st.success(f"Status updated to: {new_status}")
                    st.rerun()
                else:
                    st.error("Failed to update status")
        
        with action_col2:
            # Update priority
            new_priority = st.selectbox(
                "Update Priority",
                options=PRIORITY_OPTIONS,
                index=PRIORITY_OPTIONS.index(priority) if priority in PRIORITY_OPTIONS else 1,
                key=f"priority_{report_id}"
            )
            if st.button("Update Priority", key=f"btn_priority_{report_id}"):
                if update_report_priority(report_id, new_priority):
                    st.success(f"Priority updated to: {new_priority}")
                    st.rerun()
                else:
                    st.error("Failed to update priority")
        
        # Edit full report
        st.markdown("---")
        st.subheader("✏️ Edit Report Details")
        
        with st.form(f"edit_form_{report_id}"):
            edit_category = st.selectbox(
                "Category",
                options=ISSUE_CATEGORIES,
                index=ISSUE_CATEGORIES.index(category) if category in ISSUE_CATEGORIES else 0
            )
            edit_location = st.text_area("Location", value=location)
            edit_details = st.text_area("Additional Details", value=additional_details or "")
            
            if st.form_submit_button("💾 Save Changes"):
                if update_report(report_id, edit_category, edit_location, edit_details):
                    st.success("Report updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update report")
        
        # Delete report
        st.markdown("---")
        st.subheader("🗑️ Delete Report")
        st.warning("⚠️ This action cannot be undone!")
        
        if st.checkbox("I understand this will permanently delete the report", key=f"confirm_{report_id}"):
            if st.button("🗑️ Delete Report", type="primary", key=f"delete_{report_id}"):
                if delete_report(report_id):
                    st.success("Report deleted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to delete report")
