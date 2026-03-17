import streamlit as st


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

    map_points: list[dict] = []
    for report in reports:
        try:
            lat = float(report.get("latitude") or 0)
            lon = float(report.get("longitude") or 0)
            if lat == 0.0 and lon == 0.0:
                continue
            map_points.append({"lat": lat, "lon": lon})
        except (TypeError, ValueError):
            continue

    if map_points:
        st.map(map_points)
        st.caption(f"Showing {len(map_points)} geo-tagged report locations.")
    else:
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

