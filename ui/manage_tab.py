"""
Manage Reports tab for Local Lens application.
Includes admin authentication for destructive actions.
"""
import streamlit as st

from config import ISSUE_CATEGORIES, STATUS_OPTIONS, PRIORITY_OPTIONS
from database import (
    get_all_reports, update_report_status, update_report_priority,
    update_report, delete_report, get_similar_reports_count, get_report_clusters
)
from utils import get_community_urgency_badge, get_urgency_indicator
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
    
    # Show Community Urgency Overview (Issue Clusters)
    st.markdown("---")
    st.subheader("🔥 Community Urgency Overview")
    st.caption("Issues reported by multiple community members - prioritize these for faster response!")
    
    clusters = get_report_clusters()
    if clusters:
        cluster_cols = st.columns(min(len(clusters), 4))
        for i, cluster in enumerate(clusters[:4]):
            with cluster_cols[i]:
                urgency_icon = "🔥🔥🔥" if cluster['count'] >= 5 else "🔥🔥" if cluster['count'] >= 3 else "🔥"
                st.metric(
                    label=f"{urgency_icon} {cluster['category']}",
                    value=f"{cluster['count']} reports",
                    delta="High priority" if cluster['count'] >= 3 else "Monitor"
                )
    else:
        st.info("No issue clusters detected. Each report appears to be unique.")
    
    st.markdown("---")
    
    # Create a selectbox for choosing report with urgency indicators
    report_options = []
    for r in all_reports:
        report_id = r[0]
        category = r[2]
        location = r[3][:30]
        # Get GPS coords if available
        latitude = r[9] if len(r) > 9 else None
        longitude = r[10] if len(r) > 10 else None
        similar_count = get_similar_reports_count(report_id, category, latitude, longitude)
        urgency = get_urgency_indicator(similar_count)
        report_options.append(f"{urgency} #{report_id} - {category} - {location}..." + (f" (+{similar_count} similar)" if similar_count > 0 else ""))
    
    selected_index = st.selectbox(
        "Select Report to Manage",
        options=range(len(all_reports)),
        format_func=lambda i: report_options[i]
    )
    
    if selected_index is not None:
        selected_report = all_reports[selected_index]
        # Handle records with varying column counts (8, 9, or 11 with GPS)
        if len(selected_report) >= 11:
            report_id, image_path, category, location, additional_details, timestamp, status, priority, email, latitude, longitude = selected_report
        elif len(selected_report) >= 9:
            report_id, image_path, category, location, additional_details, timestamp, status, priority, email = selected_report
            latitude, longitude = None, None
        else:
            report_id, image_path, category, location, additional_details, timestamp, status, priority = selected_report
            email, latitude, longitude = None, None, None
        
        # Calculate community urgency
        similar_count = get_similar_reports_count(report_id, category, latitude, longitude)
        if similar_count >= 5:
            urgency_level = "Critical"
        elif similar_count >= 3:
            urgency_level = "High"
        elif similar_count >= 1:
            urgency_level = "Elevated"
        else:
            urgency_level = "Normal"
        
        # Display report details
        st.markdown("---")
        
        # Show community urgency badge if applicable
        if similar_count > 0:
            st.markdown(get_community_urgency_badge(similar_count, urgency_level), unsafe_allow_html=True)
            st.warning(f"⚠️ **Community Priority**: {similar_count} other community member(s) reported similar issues at this location. Consider prioritizing!")
        
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
