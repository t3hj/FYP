"""
Map View tab for Local Lens application.
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
from collections import Counter

from database import get_all_reports
from styles import get_tab_header, TAB_GRADIENTS
from auth import is_admin


def map_view_tab():
    """Tab 4: Interactive map showing report locations"""
    
    admin_mode = is_admin()
    
    # Header card - different subtitle for admin
    if admin_mode:
        subtitle = "Admin view: Precise coordinates, contact info, and hotspot analysis"
    else:
        subtitle = "View all reports with GPS coordinates on an interactive map"
    
    st.markdown(get_tab_header(
        "🗺️ Map View",
        subtitle,
        TAB_GRADIENTS['map']
    ), unsafe_allow_html=True)
    
    # Get all reports
    reports = get_all_reports()
    
    if not reports:
        st.info("No reports to display on map. Submit reports with GPS data first!")
        return
    
    # Extract reports with GPS coordinates
    map_reports = []
    location_counter = Counter()  # Track reports at similar locations
    
    for report in reports:
        # Handle records with varying column counts (8, 9, or 11 with GPS)
        if len(report) >= 11:
            report_id, image_path, category, location, additional_details, timestamp, status, priority, email, latitude, longitude = report
        elif len(report) >= 9:
            report_id, image_path, category, location, additional_details, timestamp, status, priority, email = report
            latitude, longitude = None, None
        else:
            report_id, image_path, category, location, additional_details, timestamp, status, priority = report
            email, latitude, longitude = None, None, None
        
        # Use stored GPS coordinates if available, otherwise try to extract from location string
        lat, lon = latitude, longitude
        
        if lat is None or lon is None:
            # Try to extract GPS from location string if it contains coordinates
            if "Coordinates:" in location:
                try:
                    coords_str = location.split("Coordinates:")[-1].strip()
                    coords_str = coords_str.rstrip(")")  # Remove trailing parenthesis if present
                    lat, lon = map(float, coords_str.split(","))
                except:
                    pass
        
        if lat is not None and lon is not None:
            # Create location key for nearby report counting (round to ~100m precision)
            loc_key = (round(lat, 3), round(lon, 3))
            location_counter[loc_key] += 1
            
            map_reports.append({
                'id': report_id,
                'lat': lat,
                'lon': lon,
                'category': category,
                'location': location,
                'status': status,
                'priority': priority,
                'timestamp': timestamp,
                'email': email,
                'loc_key': loc_key
            })
    
    if not map_reports:
        st.warning("No reports with GPS coordinates found. Upload images with GPS metadata to see them on the map.")
        return
    
    st.success(f"Displaying {len(map_reports)} report(s) with GPS coordinates out of {len(reports)} total reports")
    
    # Admin: Show hotspot summary
    if admin_mode:
        hotspots = [(loc, count) for loc, count in location_counter.items() if count > 1]
        if hotspots:
            st.info(f"🔥 **{len(hotspots)} hotspot area(s)** with multiple reports detected")
    
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
        nearby_count = location_counter[report['loc_key']]
        
        # Build popup HTML - different for admin vs civilian
        if admin_mode:
            # Admin gets full details: coordinates, email, nearby report count
            popup_html = f"""
            <div style="min-width: 250px;">
                <h4>Report #{report['id']}</h4>
                <p><b>Category:</b> {report['category']}</p>
                <p><b>Status:</b> {report['status']}</p>
                <p><b>Priority:</b> {report['priority']}</p>
                <p><b>Submitted:</b> {str(report['timestamp'])[:19]}</p>
                <hr style="margin: 8px 0;">
                <p><b>📍 Coordinates:</b></p>
                <p style="font-family: monospace; font-size: 12px;">{report['lat']:.6f}, {report['lon']:.6f}</p>
                <p><b>📧 Contact:</b> {report['email'] if report['email'] else 'Not provided'}</p>
                <p><b>🔥 Nearby Reports:</b> {nearby_count} in this area</p>
            </div>
            """
            tooltip = f"#{report['id']} - {report['category']} | {nearby_count} nearby"
        else:
            # Civilian gets basic info
            popup_html = f"""
            <div style="min-width: 200px;">
                <h4>Report #{report['id']}</h4>
                <p><b>Category:</b> {report['category']}</p>
                <p><b>Status:</b> {report['status']}</p>
                <p><b>Priority:</b> {report['priority']}</p>
                <p><b>Submitted:</b> {str(report['timestamp'])[:19]}</p>
            </div>
            """
            tooltip = f"#{report['id']} - {report['category']}"
        
        # Use different icon for hotspots
        if nearby_count > 1 and admin_mode:
            icon = folium.Icon(color=color, icon='fire', prefix='fa')
        else:
            icon = folium.Icon(color=color, icon='info-sign')
        
        folium.Marker(
            location=[report['lat'], report['lon']],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=tooltip,
            icon=icon
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
    
    # Admin: Show detailed location table
    if admin_mode:
        st.markdown("---")
        st.subheader("📋 Detailed Location Data")
        
        import pandas as pd
        
        detail_data = []
        for r in map_reports:
            detail_data.append({
                'ID': r['id'],
                'Category': r['category'],
                'Latitude': f"{r['lat']:.6f}",
                'Longitude': f"{r['lon']:.6f}",
                'Nearby Reports': location_counter[r['loc_key']],
                'Status': r['status'],
                'Priority': r['priority'],
                'Contact': r['email'] if r['email'] else '—'
            })
        
        detail_df = pd.DataFrame(detail_data)
        detail_df = detail_df.sort_values('Nearby Reports', ascending=False)
        st.dataframe(detail_df, use_container_width=True)
