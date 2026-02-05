"""
Sidebar component for Local Lens application.
"""
import streamlit as st
import requests

from config import CATEGORY_ICONS
from database import get_report_statistics
from ai_analysis import check_ollama_status
from styles import get_theme, toggle_theme


def display_sidebar():
    """Display sidebar with app information and statistics"""
    with st.sidebar:
        # Logo/Brand area
        theme = get_theme()
        gradient_style = "background: linear-gradient(90deg, #1e88e5, #43a047); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"
        subtitle_color = "#6c757d" if theme == 'dark' else "#57606a"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="font-size: 2.5rem; margin: 0;">📍</h1>
            <h2 style="{gradient_style} margin: 0;">Local Lens</h2>
            <p style="color: {subtitle_color}; font-size: 0.85rem;">Community Issue Reporter</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Theme toggle - styled for visibility
        st.markdown("---")
        theme_label = "🌙 Dark Mode" if theme == 'dark' else "☀️ Light Mode"
        toggle_label = "Switch to ☀️ Light" if theme == 'dark' else "Switch to 🌙 Dark"
        
        st.caption(f"Current: {theme_label}")
        if st.button(toggle_label, key="theme_toggle", help="Toggle theme", type="primary", use_container_width=True):
            toggle_theme()
            st.rerun()
        
        st.markdown("---")
        
        st.header("📊 Dashboard")
        
        # Get statistics
        stats = get_report_statistics()
        
        # Display total reports with styled metric
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📋 Total", stats['total_count'])
        with col2:
            st.metric("✅ Active", stats['total_count'])
        
        st.markdown("---")
        
        # Display reports by category with progress bars
        if stats['category_counts']:
            st.subheader("📈 Reports by Category")
            total = stats['total_count'] if stats['total_count'] > 0 else 1
            
            for category, count in sorted(stats['category_counts'].items(), key=lambda x: x[1], reverse=True):
                icon = CATEGORY_ICONS.get(category, '📌')
                progress = count / total
                st.markdown(f"**{icon} {category}**")
                st.progress(progress, text=f"{count} reports")
        
        st.markdown("---")
        
        # Quick tips
        with st.expander("💡 Quick Tips"):
            st.markdown("""
            - 📸 Take clear photos in good lighting
            - 📍 Enable GPS on your phone for auto-location
            - 📝 Add detailed descriptions
            - 🗺️ Check the map for nearby reports
            """)
        
        # AI Status indicator
        st.markdown("---")
        st.subheader("🤖 AI Status")
        
        # Check Ollama status
        is_running, has_llava, message = check_ollama_status()
        if is_running and has_llava:
            st.success(f"✅ {message}")
        elif is_running:
            st.warning(f"⚠️ {message}")
        else:
            st.info(f"ℹ️ {message}")
        
        st.markdown("---")
        footer_color = "#6c757d" if theme == 'dark' else "#57606a"
        st.markdown(f"""
        <div style="text-align: center; color: {footer_color}; font-size: 0.8rem;">
            <p>Local Lens v2.0</p>
            <p>Made with ❤️ for communities</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Demo disclaimer
        st.markdown("---")
        st.caption("🧪 **Prototype Demo** - This is a university FYP project. Data may be reset periodically.")
