"""
Local Lens - Community Issue Reporter
Main application entry point.

A Streamlit application for reporting and managing local community issues
with AI-powered image analysis and GPS location extraction.
"""
import streamlit as st

# Import database initialization
from database import create_database

# Import authentication
from auth import display_auth_header, is_admin

# Import UI components
from ui.sidebar import display_sidebar
from ui.submit_tab import submit_report_tab
from ui.view_tab import view_and_filter_tab
from ui.manage_tab import manage_reports_tab
from ui.map_tab import map_view_tab
from ui.export_tab import export_data_tab

# Import styles
from styles import get_custom_css


def main():
    """Main application entry point."""
    
    # Page configuration
    st.set_page_config(
        page_title="Local Lens - Community Issue Reporter",
        page_icon="📍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS (theme-aware)
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Initialize database
    create_database()
    
    # Display auth header with login
    display_auth_header()
    
    # Display sidebar
    display_sidebar()
    
    # Main content area - Tabs (different for admin vs civilian)
    if is_admin():
        # Admin sees all tabs including analytics
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📝 Submit Report",
            "📊 View & Filter", 
            "⚙️ Manage Reports",
            "🗺️ Map View",
            "📈 Analytics",
            "📥 Export Data"
        ])
        
        with tab1:
            submit_report_tab()
        
        with tab2:
            view_and_filter_tab()
        
        with tab3:
            manage_reports_tab()
        
        with tab4:
            map_view_tab()
        
        with tab5:
            from ui.analytics_tab import analytics_tab
            analytics_tab()
        
        with tab6:
            export_data_tab()
    else:
        # Civilian sees limited tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Submit Report",
            "📊 View Reports", 
            "🗺️ Map View",
            "📥 Export Data"
        ])
        
        with tab1:
            submit_report_tab()
        
        with tab2:
            view_and_filter_tab()
        
        with tab3:
            map_view_tab()
        
        with tab4:
            export_data_tab()


if __name__ == "__main__":
    main()
