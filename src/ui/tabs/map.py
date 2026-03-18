import streamlit as st
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium

from src.services.ai_service import VALID_SEVERITIES
from src.ui.theme import SEVERITY_COLOURS

SEVERITY_HEX = {
    "Low": "#22c55e",
    "Medium": "#f59e0b",
    "High": "#ef4444",
    "Critical": "#7c3aed",
}

STATUS_COLORS = {
    "Open": "#ef4444",
    "In Progress": "#f59e0b",
    "Resolved": "#22c55e",
    "Won't Fix": "#6b7280",
}


def _normalise_status(raw) -> str:
    """Treat NULL / empty status as 'Open'."""
    s = str(raw).strip() if raw else ""
    return s if s in STATUS_COLORS else "Open"


def _popup_html(report: dict, color: str) -> str:
    title = str(report.get("title") or report.get("filename") or "Untitled")[:70]
    category = report.get("category", "Unknown")
    location = report.get("location", "Unknown")
    date = str(report.get("upload_date", ""))[:10]
    sev = report.get("severity", "Medium")
    status = _normalise_status(report.get("status"))
    details = str(report.get("additional_details") or "")
    if len(details) > 180:
        details = details[:177] + "…"
    image_url = report.get("cloud_storage_url") or report.get("image_path") or ""
    assigned = report.get("assigned_to") or ""
    upvotes = int(report.get("upvotes") or 0)

    scolor = STATUS_COLORS.get(status, "#6b7280")
    img_html = (
        f'<img src="{image_url}" style="width:100%;border-radius:8px;'
        f'margin-top:10px;max-height:140px;object-fit:cover;" />'
    ) if image_url else ""
    assigned_html = (
        f'<tr><td style="padding:3px 6px 3px 0;">👤</td>'
        f'<td style="padding:3px 0;color:#334155;">{assigned}</td></tr>'
    ) if assigned else ""

    return f"""
    <div style="font-family:system-ui,sans-serif;min-width:240px;max-width:300px;padding:4px;">
        <div style="font-weight:700;font-size:0.97rem;color:#0f172a;
            margin-bottom:8px;line-height:1.3;">{title}</div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px;">
            <span style="background:{color}20;color:{color};border:1px solid {color}50;
                border-radius:999px;padding:2px 9px;font-size:0.73rem;font-weight:700;">{sev}</span>
            <span style="background:{scolor}20;color:{scolor};border:1px solid {scolor}50;
                border-radius:999px;padding:2px 9px;font-size:0.73rem;font-weight:700;">{status}</span>
            <span style="background:rgba(99,102,241,0.12);color:#6366f1;
                border:1px solid rgba(99,102,241,0.3);border-radius:999px;
                padding:2px 9px;font-size:0.73rem;font-weight:700;">▲ {upvotes}</span>
        </div>
        <table style="width:100%;font-size:0.82rem;color:#475569;border-collapse:collapse;">
            <tr><td style="padding:3px 6px 3px 0;">🏷️</td><td style="padding:3px 0;">{category}</td></tr>
            <tr><td style="padding:3px 6px 3px 0;">📍</td><td style="padding:3px 0;">{location}</td></tr>
            <tr><td style="padding:3px 6px 3px 0;">📅</td><td style="padding:3px 0;">{date}</td></tr>
            {assigned_html}
        </table>
        {f'<p style="font-size:0.82rem;color:#64748b;margin-top:8px;border-top:1px solid #e2e8f0;padding-top:8px;line-height:1.5;">{details}</p>' if details else ''}
        {img_html}
    </div>
    """


def render_map_tab(reports: list[dict]) -> None:
    st.subheader("Report Locations")

    if not reports:
        st.markdown(
            """<div class="ll-empty-state"><div class="ll-empty-emoji">🗺️</div>
            <div class="ll-empty-title">No reports yet</div>
            <div class="ll-empty-subtitle">Submitted reports with location data appear here.</div>
            </div>""",
            unsafe_allow_html=True,
        )
        return

    # Extract geo-tagged reports
    geo_reports = []
    for r in reports:
        try:
            lat = float(r.get("latitude") or 0)
            lon = float(r.get("longitude") or 0)
            if abs(lat) < 0.001 and abs(lon) < 0.001:
                continue
            geo_reports.append({**r, "_lat": lat, "_lon": lon})
        except (TypeError, ValueError):
            continue

    if not geo_reports:
        st.markdown(
            """<div class="ll-empty-state"><div class="ll-empty-emoji">🗺️</div>
            <div class="ll-empty-title">No geo-tagged reports yet</div>
            <div class="ll-empty-subtitle">
                Reports need coordinates to appear on the map.<br>
                Use the map pin when submitting a report, or enter a postcode so
                Local Lens can look up the coordinates automatically.
            </div></div>""",
            unsafe_allow_html=True,
        )
        return

    # ── Filters ───────────────────────────────────────────────────────────────
    f1, f2, f3, f4 = st.columns([2, 2, 2, 2])
    with f1:
        all_cats = ["All"] + sorted(
            {r.get("category", "Unknown") for r in geo_reports if r.get("category")}
        )
        cat_filter = st.selectbox("Category", all_cats, key="map_cat_filter")
    with f2:
        sev_filter = st.selectbox("Severity", ["All"] + VALID_SEVERITIES, key="map_sev_filter")
    with f3:
        # Build status options from actual data (normalising NULLs → "Open")
        present_statuses = sorted(
            {_normalise_status(r.get("status")) for r in geo_reports}
        )
        status_options = ["All"] + present_statuses
        status_filter = st.selectbox("Status", status_options, key="map_status_filter")
    with f4:
        view_mode = st.radio(
            "View mode", ["📍 Pins", "🔥 Heatmap"],
            horizontal=True, key="map_view_mode",
        )

    # Apply filters — normalise status before comparing
    filtered = geo_reports
    if cat_filter != "All":
        filtered = [r for r in filtered if r.get("category") == cat_filter]
    if sev_filter != "All":
        filtered = [r for r in filtered if r.get("severity") == sev_filter]
    if status_filter != "All":
        filtered = [r for r in filtered if _normalise_status(r.get("status")) == status_filter]

    # Show how many have/don't have coords as a hint
    no_coords = len(reports) - len(geo_reports)
    hint_parts = [f"**{len(geo_reports)}** of {len(reports)} reports have map coordinates"]
    if no_coords:
        hint_parts.append(
            f"{no_coords} report{'s' if no_coords > 1 else ''} "
            f"without coordinates {'are' if no_coords > 1 else 'is'} not shown"
        )
    st.caption(" · ".join(hint_parts))

    if not filtered:
        st.info(
            f"No geo-tagged reports match the selected filters. "
            f"({len(geo_reports)} total mapped, {len(reports) - len(geo_reports)} without coordinates)"
        )
        return

    # ── Build map ─────────────────────────────────────────────────────────────
    lats = [r["_lat"] for r in filtered]
    lons = [r["_lon"] for r in filtered]
    center = [sum(lats) / len(lats), sum(lons) / len(lons)]

    # Auto-zoom: fit to spread of points rather than a fixed level
    if len(filtered) == 1:
        zoom = 15
    else:
        lat_spread = max(lats) - min(lats)
        lon_spread = max(lons) - min(lons)
        spread = max(lat_spread, lon_spread)
        if spread > 5:
            zoom = 6
        elif spread > 2:
            zoom = 8
        elif spread > 0.5:
            zoom = 10
        elif spread > 0.1:
            zoom = 12
        else:
            zoom = 14

    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="CartoDB positron",
        control_scale=True,
    )

    if "Pins" in view_mode:
        cluster = MarkerCluster(
            name="Reports",
            options={
                "maxClusterRadius": 50,
                "spiderfyOnMaxZoom": True,
                "showCoverageOnHover": False,
                "zoomToBoundsOnClick": True,
            },
        ).add_to(m)

        for report in filtered:
            sev = report.get("severity", "Medium")
            color = SEVERITY_HEX.get(sev, "#6b7280")
            folium.CircleMarker(
                location=[report["_lat"], report["_lon"]],
                radius=9,
                color="white",
                weight=2,
                fill=True,
                fill_color=color,
                fill_opacity=0.88,
                popup=folium.Popup(_popup_html(report, color), max_width=320),
                tooltip=folium.Tooltip(
                    f"<b>{report.get('title') or 'Untitled'}</b><br>"
                    f"<span style='color:{color}'>{sev}</span> · "
                    f"▲ {int(report.get('upvotes') or 0)}",
                    sticky=True,
                    style="font-family:system-ui;font-size:0.85rem;",
                ),
            ).add_to(cluster)

    else:
        HeatMap(
            [[r["_lat"], r["_lon"]] for r in filtered],
            min_opacity=0.35,
            radius=22,
            blur=18,
            gradient={
                "0.3": "#3b82f6",
                "0.5": "#22c55e",
                "0.7": "#f97316",
                "1.0": "#ef4444",
            },
        ).add_to(m)

    st_folium(m, use_container_width=True, height=530, returned_objects=[], key="main_map")

    # ── Stats ─────────────────────────────────────────────────────────────────
    st.divider()
    s1, s2, s3, s4 = st.columns(4)
    high_crit = sum(1 for r in filtered if r.get("severity") in ("High", "Critical"))
    open_count = sum(1 for r in filtered if _normalise_status(r.get("status")) == "Open")
    resolved_count = sum(1 for r in filtered if _normalise_status(r.get("status")) == "Resolved")

    with s1:
        st.metric("Mapped", len(filtered))
    with s2:
        st.metric("🚨 High Priority", high_crit)
    with s3:
        st.metric("🔄 Open", open_count)
    with s4:
        st.metric("✅ Resolved", resolved_count)

    # ── Legend ────────────────────────────────────────────────────────────────
    st.markdown("**Severity Legend**")
    leg_cols = st.columns(4)
    for col, (sev, color) in zip(leg_cols, SEVERITY_HEX.items()):
        count = sum(1 for r in filtered if r.get("severity") == sev)
        with col:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;padding:6px 0;">'
                f'<div style="width:13px;height:13px;border-radius:50%;'
                f'background:{color};flex-shrink:0;"></div>'
                f'<span style="font-size:0.9rem;font-weight:500;">{sev}</span>'
                f'<span style="font-size:0.85rem;color:#64748b;">({count})</span>'
                f'</div>',
                unsafe_allow_html=True,
            )