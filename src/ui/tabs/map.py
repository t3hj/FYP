import streamlit as st

from src.services.ai_service import VALID_SEVERITIES
from src.ui.theme import SEVERITY_COLOURS


def render_map_tab(reports: list[dict]) -> None:
    st.subheader("Report Locations")
    if not reports:
        st.markdown(
            """
            <div class="ll-empty-state">
                <div class="ll-empty-emoji">🗺️</div>
                <div class="ll-empty-title">No reports yet</div>
                <div class="ll-empty-subtitle">
                    Start by submitting a report in the first tab. Locations will appear
                    on the map as geo-tagged reports are created.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Extract geo-tagged reports
    geo_reports = []
    for report in reports:
        try:
            lat = float(report.get("latitude") or 0)
            lon = float(report.get("longitude") or 0)
            if lat == 0.0 and lon == 0.0:
                continue
            geo_reports.append(report)
        except (TypeError, ValueError):
            continue

    if not geo_reports:
        st.markdown(
            """
            <div class="ll-empty-state">
                <div class="ll-empty-emoji">🗺️</div>
                <div class="ll-empty-title">No map data yet</div>
                <div class="ll-empty-subtitle">
                    Reports with valid latitude and longitude will automatically appear
                    on this map once residents submit them.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Filters
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        all_categories = ["All"] + sorted(
            {r.get("category", "Unknown") for r in geo_reports if r.get("category")}
        )
        category_filter = st.selectbox("Filter by Category", all_categories, key="map_category")
    with filter_col2:
        all_severities = ["All"] + VALID_SEVERITIES
        severity_filter = st.selectbox("Filter by Severity", all_severities, key="map_severity")

    # Apply filters
    filtered_reports = geo_reports
    if category_filter != "All":
        filtered_reports = [r for r in filtered_reports if r.get("category") == category_filter]
    if severity_filter != "All":
        filtered_reports = [r for r in filtered_reports if r.get("severity") == severity_filter]

    # Build map data with severity color coding
    map_points = []
    for report in filtered_reports:
        lat = float(report.get("latitude") or 0)
        lon = float(report.get("longitude") or 0)
        severity = report.get("severity", "Low")
        color = SEVERITY_COLOURS.get(severity, "#6b7280")
        map_points.append({
            "lat": lat,
            "lon": lon,
            "color": color,
        })

    if map_points:
        st.map(map_points)
        st.caption(f"Showing {len(map_points)} of {len(geo_reports)} geo-tagged locations")
        
        # Legend
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        legend_col1, legend_col2, legend_col3, legend_col4 = st.columns(4)
        for col, (severity, color) in zip(
            [legend_col1, legend_col2, legend_col3, legend_col4],
            SEVERITY_COLOURS.items()
        ):
            with col:
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem;">
                        <div style="width: 12px; height: 12px; border-radius: 50%; background-color: {color}; flex-shrink: 0;"></div>
                        <span>{severity}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        
        # Summary stats
        st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
        stat1, stat2, stat3 = st.columns(3)
        
        with stat1:
            st.metric("Total Locations", len(map_points))
        
        with stat2:
            severity_counts = {}
            for r in filtered_reports:
                sev = r.get("severity", "Low")
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            high_critical = severity_counts.get("High", 0) + severity_counts.get("Critical", 0)
            st.metric("High Priority", high_critical, 
                      help="High and Critical severity issues")
        
        with stat3:
            categories = {r.get("category", "Unknown") for r in filtered_reports}
            st.metric("Categories", len(categories))
    else:
        st.info("No reports match the selected filters. Try adjusting your category or severity filter.")

