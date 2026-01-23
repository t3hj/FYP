"""
Map View tab for Local Lens application.
"""
import streamlit as st
import folium
from streamlit_folium import st_folium

from database import get_all_reports
from styles import get_tab_header, TAB_GRADIENTS


def map_view_tab():
    """Tab 4: Interactive map showing report locations"""
    
    # Header card
    st.markdown(get_tab_header(
        "🗺️ Map View",
        "View all reports with GPS coordinates on an interactive map",
        TAB_GRADIENTS['map']
    ), unsafe_allow_html=True)
    
    # Get all reports
    reports = get_all_reports()
    
    if not reports:
        st.info("No reports to display on map. Submit reports with GPS data first!")
        return
    
    # Extract reports with GPS coordinates
    map_reports = []
    for report in reports:
        report_id, image_path, category, location, additional_details, timestamp, status, priority = report
        
        # Try to extract GPS from location string if it contains coordinates
        if "Coordinates:" in location:
            try:
                coords_str = location.split("Coordinates:")[-1].strip()
                lat, lon = map(float, coords_str.split(","))
                map_reports.append({
                    'id': report_id,
                    'lat': lat,
                    'lon': lon,
                    'category': category,
                    'location': location,
                    'status': status,
                    'priority': priority,
                    'timestamp': timestamp
                })
            except:
                pass
    
    if not map_reports:
        st.warning("No reports with GPS coordinates found. Upload images with GPS metadata to see them on the map.")
        return
    
    st.success(f"Displaying {len(map_reports)} report(s) with GPS coordinates out of {len(reports)} total reports")
    
    # Create map centered on average location
    avg_lat = sum(r['lat'] for r in map_reports) / len(map_reports)
    avg_lon = sum(r['lon'] for r in map_reports) / len(map_reports)
    
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
    
    # Priority colors for markers
    priority_colors = {
        'Critical': 'red',
        'High': 'orange',
        'Medium': 'blue',
        'Low': 'green'
    }
    
    # Add markers for each report
    for report in map_reports:
        color = priority_colors.get(report['priority'], 'blue')
        
        popup_html = f"""
        <div style="min-width: 200px;">
            <h4>Report #{report['id']}</h4>
            <p><b>Category:</b> {report['category']}</p>
            <p><b>Status:</b> {report['status']}</p>
            <p><b>Priority:</b> {report['priority']}</p>
            <p><b>Submitted:</b> {str(report['timestamp'])[:19]}</p>
        </div>
        """
        
        folium.Marker(
            location=[report['lat'], report['lon']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"#{report['id']} - {report['category']}",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
    
    # Display map
    st_folium(m, width=1200, height=600)
    
    # Legend
    st.markdown("---")
    st.write("**Map Legend:**")
    legend_col1, legend_col2, legend_col3, legend_col4 = st.columns(4)
    
    with legend_col1:
        st.markdown("🔴 **Critical**")
    with legend_col2:
        st.markdown("🟠 **High**")
    with legend_col3:
        st.markdown("🔵 **Medium**")
    with legend_col4:
        st.markdown("🟢 **Low**")
