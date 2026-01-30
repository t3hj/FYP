"""
View & Filter Reports tab for Local Lens application.
"""
import streamlit as st
import pandas as pd

from config import ISSUE_CATEGORIES, STATUS_OPTIONS
from database import get_filtered_reports
from styles import get_tab_header, TAB_GRADIENTS


def view_and_filter_tab():
    """Tab 2: View and filter reports"""
    
    # Header card
    st.markdown(get_tab_header(
        "📊 View & Filter Reports",
        "Search and filter through all submitted reports",
        TAB_GRADIENTS['view']
    ), unsafe_allow_html=True)
    
    # Filter section in a styled container
    with st.container():
        st.markdown("##### 🔎 Filters")
        
        # Create filter columns
        filter_col1, filter_col2, filter_col3 = st.columns(3)
    
        with filter_col1:
            filter_category = st.selectbox(
                "Filter by Category",
                options=['All'] + ISSUE_CATEGORIES,
                key="filter_category"
            )
        
        with filter_col2:
            filter_status = st.selectbox(
                "Filter by Status",
                options=['All'] + STATUS_OPTIONS,
                key="filter_status"
            )
        
        with filter_col3:
            filter_location = st.text_input(
                "Search Location",
                placeholder="Enter location keywords...",
                key="filter_location"
            )
    
    # Date range filters
    date_col1, date_col2 = st.columns(2)
    
    with date_col1:
        date_from = st.date_input(
            "From Date",
            value=None,
            key="date_from"
        )
    
    with date_col2:
        date_to = st.date_input(
            "To Date",
            value=None,
            key="date_to"
        )
    
    if st.button("🔍 Apply Filters", type="primary"):
        # Get filtered reports
        reports = get_filtered_reports(
            category=None if filter_category == 'All' else filter_category,
            status=None if filter_status == 'All' else filter_status,
            date_from=date_from,
            date_to=date_to,
            location=filter_location if filter_location else None
        )
        
        if reports:
            st.success(f"Found {len(reports)} report(s)")
            
            # Display filtered reports in a table
            df_data = []
            for report in reports:
                # Handle both old records (8 columns) and new records (9 columns with email)
                if len(report) >= 9:
                    report_id, image_path, category, location, additional_details, timestamp, status, priority, email = report
                else:
                    report_id, image_path, category, location, additional_details, timestamp, status, priority = report
                    email = None
                df_data.append({
                    'ID': report_id,
                    'Category': category,
                    'Location': location[:50] + '...' if len(location) > 50 else location,
                    'Status': status,
                    'Priority': priority,
                    'Timestamp': str(timestamp)[:19]
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Show detailed view for each report
            st.markdown("---")
            st.subheader("📋 Report Details")
            
            for report in reports:
                # Handle both old records (8 columns) and new records (9 columns with email)
                if len(report) >= 9:
                    report_id, image_path, category, location, additional_details, timestamp, status, priority, email = report
                else:
                    report_id, image_path, category, location, additional_details, timestamp, status, priority = report
                    email = None
                
                with st.expander(f"Report #{report_id} - {category}"):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        try:
                            st.image(image_path, caption=f"Report #{report_id}", use_container_width=True)
                        except:
                            st.write("Image not available")
                    with col2:
                        st.write(f"**Category:** {category}")
                        st.write(f"**Location:** {location}")
                        st.write(f"**Priority:** {priority}")
                        st.write(f"**Status:** {status}")
                        st.write(f"**Submitted:** {timestamp}")
                        if email:
                            st.write(f"**Contact Email:** {email}")
                        if additional_details:
                            st.write(f"**Details:** {additional_details}")
        else:
            st.info("No reports found matching your filters.")
