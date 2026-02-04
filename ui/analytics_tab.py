"""
Analytics tab for Local Lens application.
Admin-only view with detailed statistics and insights.
"""
import streamlit as st
import pandas as pd
from collections import Counter

from database import get_all_reports
from styles import get_tab_header, TAB_GRADIENTS
from auth import is_admin


def analytics_tab():
    """Tab: Analytics dashboard for admin/council users"""
    
    if not is_admin():
        st.warning("🔒 This section requires admin access.")
        return
    
    # Header card
    st.markdown(get_tab_header(
        "📈 Analytics Dashboard",
        "Detailed insights and statistics for council decision-making",
        TAB_GRADIENTS['export']  # Reuse export gradient
    ), unsafe_allow_html=True)
    
    reports = get_all_reports()
    
    if not reports:
        st.info("No reports available for analysis.")
        return
    
    # Convert to DataFrame for easier analysis
    if reports and len(reports[0]) >= 11:
        df = pd.DataFrame(reports, columns=[
            'ID', 'Image Path', 'Category', 'Location',
            'Additional Details', 'Timestamp', 'Status', 'Priority', 'Email',
            'Latitude', 'Longitude'
        ])
    elif reports and len(reports[0]) >= 9:
        df = pd.DataFrame(reports, columns=[
            'ID', 'Image Path', 'Category', 'Location',
            'Additional Details', 'Timestamp', 'Status', 'Priority', 'Email'
        ])
    else:
        df = pd.DataFrame(reports, columns=[
            'ID', 'Image Path', 'Category', 'Location',
            'Additional Details', 'Timestamp', 'Status', 'Priority'
        ])
        df['Email'] = None
    
    # Overview metrics
    st.subheader("📊 Overview")
    
    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
    
    with metric_col1:
        st.metric("Total Reports", len(reports))
    
    with metric_col2:
        pending = len(df[df['Status'] == 'Reported'])
        st.metric("Pending", pending)
    
    with metric_col3:
        in_progress = len(df[df['Status'] == 'In Progress'])
        st.metric("In Progress", in_progress)
    
    with metric_col4:
        resolved = len(df[df['Status'] == 'Resolved'])
        st.metric("Resolved", resolved)
    
    with metric_col5:
        with_email = len(df[df['Email'].notna() & (df['Email'] != '')])
        st.metric("With Contact", with_email)
    
    st.markdown("---")
    
    # Two column layout for charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("📁 Reports by Category")
        category_counts = df['Category'].value_counts()
        st.bar_chart(category_counts)
    
    with chart_col2:
        st.subheader("🚦 Reports by Status")
        status_counts = df['Status'].value_counts()
        st.bar_chart(status_counts)
    
    st.markdown("---")
    
    # Priority analysis
    priority_col1, priority_col2 = st.columns(2)
    
    with priority_col1:
        st.subheader("⚠️ Reports by Priority")
        priority_counts = df['Priority'].value_counts()
        st.bar_chart(priority_counts)
    
    with priority_col2:
        st.subheader("🔥 High Priority Issues")
        high_priority = df[df['Priority'].isin(['High', 'Critical'])]
        st.write(f"**{len(high_priority)} reports** require urgent attention")
        
        if not high_priority.empty:
            for _, row in high_priority.head(5).iterrows():
                with st.expander(f"#{row['ID']} - {row['Category']} ({row['Priority']})"):
                    st.write(f"**Location:** {row['Location'][:100]}...")
                    st.write(f"**Status:** {row['Status']}")
                    if row.get('Email'):
                        st.write(f"**Contact:** {row['Email']}")
    
    st.markdown("---")
    
    # Location analysis - find duplicate locations
    st.subheader("📍 Location Hotspots")
    st.write("Areas with multiple reports (potential recurring issues)")
    
    # Simple location clustering - find similar locations
    location_counts = Counter()
    for loc in df['Location']:
        # Extract first part of address or coordinates
        if 'Coordinates:' in str(loc):
            # Extract rough area (round coordinates)
            try:
                coords_str = loc.split("Coordinates:")[-1].strip()
                lat, lon = map(float, coords_str.split(","))
                # Round to ~100m precision
                area_key = f"{round(lat, 3)}, {round(lon, 3)}"
                location_counts[area_key] += 1
            except:
                pass
        else:
            # Use first 30 chars as location key
            area_key = str(loc)[:30] if loc else "Unknown"
            location_counts[area_key] += 1
    
    # Show areas with multiple reports
    hotspots = [(loc, count) for loc, count in location_counts.items() if count > 1]
    hotspots.sort(key=lambda x: x[1], reverse=True)
    
    if hotspots:
        hotspot_df = pd.DataFrame(hotspots, columns=['Location', 'Report Count'])
        st.dataframe(hotspot_df, use_container_width=True)
    else:
        st.info("No location hotspots detected (no areas with multiple reports)")
    
    st.markdown("---")
    
    # Contact information summary
    st.subheader("📧 Reporter Contact Information")
    
    reports_with_email = df[df['Email'].notna() & (df['Email'] != '')]
    
    if not reports_with_email.empty:
        st.write(f"**{len(reports_with_email)} reports** have contact information for follow-up")
        
        contact_df = reports_with_email[['ID', 'Category', 'Email', 'Status', 'Priority']].copy()
        contact_df = contact_df.sort_values('Priority', ascending=False)
        st.dataframe(contact_df, use_container_width=True)
    else:
        st.info("No reports with contact information available")
    
    st.markdown("---")
    
    # Time analysis
    st.subheader("📅 Reports Over Time")
    
    if df['Timestamp'].notna().any():
        try:
            df['Date'] = pd.to_datetime(df['Timestamp']).dt.date
            daily_counts = df.groupby('Date').size()
            st.line_chart(daily_counts)
        except:
            st.info("Unable to parse timestamps for time analysis")
    else:
        st.info("No timestamp data available for time analysis")
