"""
Export Data tab for Local Lens application.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from database import get_all_reports, export_reports_to_csv
from styles import get_tab_header, TAB_GRADIENTS


def export_data_tab():
    """Tab 5: Export data"""
    
    # Header card
    st.markdown(get_tab_header(
        "📥 Export Data",
        "Download your reports data in various formats",
        TAB_GRADIENTS['export']
    ), unsafe_allow_html=True)
    
    reports = get_all_reports()
    
    if not reports:
        st.info("No reports to export. Submit some reports first!")
        return
    
    st.success(f"**{len(reports)} report(s)** available for export")
    
    # Export options
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        st.write("### 📄 CSV Export")
        st.write("Export all reports as a CSV file for use in spreadsheet applications.")
        
        csv_data = export_reports_to_csv()
        if csv_data:
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"local_lens_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                type="primary"
            )
    
    with export_col2:
        st.write("### 📊 Data Preview")
        st.write("Preview the data before exporting.")
        
        # Create preview DataFrame - handle records with varying column counts
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
        
        # Show preview with limited columns
        preview_df = df[['ID', 'Category', 'Location', 'Status', 'Priority', 'Timestamp']]
        st.dataframe(preview_df.head(10), use_container_width=True)
        
        if len(reports) > 10:
            st.caption(f"Showing 10 of {len(reports)} reports. Download CSV for full data.")
    
    # Statistics section
    st.markdown("---")
    st.subheader("📈 Export Statistics")
    
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    
    with stat_col1:
        st.metric("Total Reports", len(reports))
    
    with stat_col2:
        categories = len(set(r[2] for r in reports))
        st.metric("Categories Used", categories)
    
    with stat_col3:
        if reports:
            timestamps = [r[5] for r in reports if r[5] is not None]
            if timestamps:
                oldest = min(timestamps)
                newest = max(timestamps)
                st.metric("Date Range", f"{str(oldest)[:10]} to {str(newest)[:10]}")
            else:
                st.metric("Date Range", "N/A")
