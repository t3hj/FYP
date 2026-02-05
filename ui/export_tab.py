"""
Export Data tab for Local Lens application.
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta

from database import get_all_reports, export_reports_to_csv
from styles import get_tab_header, TAB_GRADIENTS, get_theme
from config import ISSUE_CATEGORIES, STATUS_OPTIONS, PRIORITY_OPTIONS


def export_data_tab():
    """Tab 5: Export data with multiple formats and filtering"""
    
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
    
    # Create DataFrame for filtering
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
    
    # Filter section
    with st.expander("🔍 **Filter Data Before Export**", expanded=False):
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            filter_categories = st.multiselect(
                "Categories",
                options=ISSUE_CATEGORIES,
                default=[],
                help="Leave empty to include all"
            )
        
        with filter_col2:
            filter_status = st.multiselect(
                "Status",
                options=STATUS_OPTIONS,
                default=[],
                help="Leave empty to include all"
            )
        
        with filter_col3:
            filter_priority = st.multiselect(
                "Priority",
                options=PRIORITY_OPTIONS,
                default=[],
                help="Leave empty to include all"
            )
        
        # Date range filter
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            date_from = st.date_input("From Date", value=None)
        with date_col2:
            date_to = st.date_input("To Date", value=None)
    
    # Apply filters
    filtered_df = df.copy()
    
    if filter_categories:
        filtered_df = filtered_df[filtered_df['Category'].isin(filter_categories)]
    if filter_status:
        filtered_df = filtered_df[filtered_df['Status'].isin(filter_status)]
    if filter_priority:
        filtered_df = filtered_df[filtered_df['Priority'].isin(filter_priority)]
    if date_from:
        filtered_df = filtered_df[filtered_df['Timestamp'] >= str(date_from)]
    if date_to:
        filtered_df = filtered_df[filtered_df['Timestamp'] <= str(date_to + timedelta(days=1))]
    
    # Show count
    theme = get_theme()
    if len(filtered_df) == len(df):
        st.success(f"**{len(filtered_df)} report(s)** available for export")
    else:
        st.info(f"**{len(filtered_df)} of {len(df)} report(s)** selected for export (filters applied)")
    
    st.markdown("---")
    
    # Export format cards
    st.subheader("📦 Export Formats")
    
    format_col1, format_col2, format_col3 = st.columns(3)
    
    with format_col1:
        # CSV Export card
        card_bg = "#ffffff" if theme == 'light' else "#161b22"
        card_border = "#d0d7de" if theme == 'light' else "#30363d"
        text_color = "#24292f" if theme == 'light' else "#e6edf3"
        
        st.markdown(f"""
        <div style="background-color: {card_bg}; padding: 20px; border-radius: 10px; border: 1px solid {card_border}; text-align: center;">
            <h3 style="color: {text_color}; margin: 0;">📄 CSV</h3>
            <p style="color: {text_color}; opacity: 0.8; font-size: 0.9rem;">Spreadsheet format</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate filtered CSV
        csv_columns = ['ID', 'Category', 'Location', 'Additional Details', 'Timestamp', 'Status', 'Priority']
        if 'Email' in filtered_df.columns:
            csv_columns.append('Email')
        if 'Latitude' in filtered_df.columns:
            csv_columns.extend(['Latitude', 'Longitude'])
        
        csv_data = filtered_df[csv_columns].to_csv(index=False)
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"local_lens_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
    
    with format_col2:
        st.markdown(f"""
        <div style="background-color: {card_bg}; padding: 20px; border-radius: 10px; border: 1px solid {card_border}; text-align: center;">
            <h3 style="color: {text_color}; margin: 0;">📋 JSON</h3>
            <p style="color: {text_color}; opacity: 0.8; font-size: 0.9rem;">Developer format</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate JSON
        json_data = filtered_df[csv_columns].to_dict(orient='records')
        json_str = json.dumps(json_data, indent=2, default=str)
        
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"local_lens_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            type="secondary",
            use_container_width=True
        )
    
    with format_col3:
        st.markdown(f"""
        <div style="background-color: {card_bg}; padding: 20px; border-radius: 10px; border: 1px solid {card_border}; text-align: center;">
            <h3 style="color: {text_color}; margin: 0;">📊 Summary</h3>
            <p style="color: {text_color}; opacity: 0.8; font-size: 0.9rem;">Text report</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate summary report
        summary_lines = [
            "=" * 50,
            "LOCAL LENS - COMMUNITY ISSUE REPORT SUMMARY",
            "=" * 50,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Reports: {len(filtered_df)}",
            "",
            "BREAKDOWN BY CATEGORY:",
            "-" * 30,
        ]
        
        for cat in filtered_df['Category'].value_counts().items():
            summary_lines.append(f"  • {cat[0]}: {cat[1]} reports")
        
        summary_lines.extend([
            "",
            "BREAKDOWN BY STATUS:",
            "-" * 30,
        ])
        
        for status in filtered_df['Status'].value_counts().items():
            summary_lines.append(f"  • {status[0]}: {status[1]} reports")
        
        summary_lines.extend([
            "",
            "BREAKDOWN BY PRIORITY:",
            "-" * 30,
        ])
        
        for priority in filtered_df['Priority'].value_counts().items():
            summary_lines.append(f"  • {priority[0]}: {priority[1]} reports")
        
        summary_lines.extend([
            "",
            "=" * 50,
            "END OF REPORT",
            "=" * 50,
        ])
        
        summary_text = "\n".join(summary_lines)
        
        st.download_button(
            label="📥 Download Summary",
            data=summary_text,
            file_name=f"local_lens_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            type="secondary",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Data Preview section
    st.subheader("👁️ Data Preview")
    
    # Preview columns selector
    available_cols = list(filtered_df.columns)
    display_cols = ['ID', 'Category', 'Location', 'Status', 'Priority', 'Timestamp']
    display_cols = [c for c in display_cols if c in available_cols]
    
    preview_df = filtered_df[display_cols]
    
    # Show dataframe with better formatting
    st.dataframe(
        preview_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "Category": st.column_config.TextColumn("Category", width="medium"),
            "Location": st.column_config.TextColumn("Location", width="large"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Priority": st.column_config.TextColumn("Priority", width="small"),
            "Timestamp": st.column_config.TextColumn("Date", width="medium"),
        }
    )
    
    if len(filtered_df) > 10:
        st.caption(f"Showing all {len(filtered_df)} reports. Scroll to see more.")
    
    st.markdown("---")
    
    # Quick Statistics
    st.subheader("📈 Quick Statistics")
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric("📋 Total Reports", len(filtered_df))
    
    with stat_col2:
        pending = len(filtered_df[filtered_df['Status'] == 'Reported'])
        st.metric("⏳ Pending", pending)
    
    with stat_col3:
        resolved = len(filtered_df[filtered_df['Status'].isin(['Resolved', 'Closed'])])
        st.metric("✅ Resolved", resolved)
    
    with stat_col4:
        high_priority = len(filtered_df[filtered_df['Priority'].isin(['High', 'Critical'])])
        st.metric("🔴 High Priority", high_priority)
    
    # Visual breakdown
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.write("**📊 By Category**")
        category_counts = filtered_df['Category'].value_counts()
        st.bar_chart(category_counts)
    
    with chart_col2:
        st.write("**📊 By Status**")
        status_counts = filtered_df['Status'].value_counts()
        st.bar_chart(status_counts)
