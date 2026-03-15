import streamlit as st
import pandas as pd

from config.settings import ENABLE_OLLAMA, REQUIRE_AI, REQUIRE_GEOLOCATION, COUNCIL_ADMIN_PASSWORD
from src.services.ai_service import VALID_CATEGORIES, VALID_SEVERITIES
from src.services.backup_service import BackupService
from src.services.upload_service import UploadService

BRAND_COLORS = {
    "primary": "#2563eb",
    "primary_soft": "#dbeafe",
    "accent": "#f97316",
    "accent_soft": "#fff7ed",
    "neutral_100": "#f9fafb",
    "neutral_200": "#e5e7eb",
    "neutral_300": "#d1d5db",
    "neutral_600": "#4b5563",
    "neutral_700": "#374151",
    "neutral_900": "#111827",
}

SEVERITY_COLOURS = {
    "Low": "#22c55e",
    "Medium": "#f97316",
    "High": "#ef4444",
    "Critical": "#7c3aed",
}

SPACING_SCALE = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
}


def init_theme() -> str:
    """Initialise light/dark theme from session state or URL and return active theme."""
    # Read from query params first for persistence between reloads
    try:
        params = st.query_params  # streamlit >= 1.36 style API
        url_theme = params.get("theme", ["light"])
        url_theme = url_theme[0] if isinstance(url_theme, list) else url_theme
    except Exception:
        # Fallback for older Streamlit versions
        params = st.experimental_get_query_params()
        url_theme = params.get("theme", ["light"])[0] if params.get("theme") else "light"

    if "theme" not in st.session_state:
        st.session_state.theme = url_theme if url_theme in {"light", "dark"} else "light"

    return st.session_state.theme


def set_theme(theme: str) -> None:
    if theme not in {"light", "dark"}:
        return
    st.session_state.theme = theme
    try:
        st.query_params["theme"] = theme  # type: ignore[index]
    except Exception:
        st.experimental_set_query_params(theme=theme)


def apply_theme_css(theme: str) -> None:
    is_dark = theme == "dark"

    bg = BRAND_COLORS["neutral_900"] if is_dark else "#ffffff"
    surface = "#020617" if is_dark else "#ffffff"
    border = BRAND_COLORS["neutral_700"] if is_dark else BRAND_COLORS["neutral_200"]
    text_primary = "#f9fafb" if is_dark else BRAND_COLORS["neutral_900"]
    text_secondary = "#9ca3af" if is_dark else BRAND_COLORS["neutral_600"]

    st.markdown(
        f"""
        <style>
        :root {{
            --brand-primary: {BRAND_COLORS["primary"]};
            --brand-primary-soft: {BRAND_COLORS["primary_soft"]};
            --brand-accent: {BRAND_COLORS["accent"]};
            --brand-accent-soft: {BRAND_COLORS["accent_soft"]};
            --brand-border: {border};
            --brand-bg: {bg};
            --brand-surface: {surface};
            --brand-text-primary: {text_primary};
            --brand-text-secondary: {text_secondary};
            --space-xs: {SPACING_SCALE["xs"]};
            --space-sm: {SPACING_SCALE["sm"]};
            --space-md: {SPACING_SCALE["md"]};
            --space-lg: {SPACING_SCALE["lg"]};
            --space-xl: {SPACING_SCALE["xl"]};
        }}

        body {{
            background: var(--brand-bg);
            color: var(--brand-text-primary);
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text",
                         "Inter", "Segoe UI", sans-serif;
        }}

        /* Typography hierarchy */
        .ll-hero-title {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Display",
                         "Inter", "Segoe UI", sans-serif;
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            margin-bottom: var(--space-xs);
        }}

        .ll-hero-subtitle {{
            font-size: 0.95rem;
            color: var(--brand-text-secondary);
            max-width: 520px;
        }}

        .ll-meta-text {{
            font-size: 0.8rem;
            color: var(--brand-text-secondary);
        }}

        .ll-helper-text {{
            font-size: 0.8rem;
            color: var(--brand-text-secondary);
        }}

        .ll-status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 2px 10px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            background: rgba(15, 118, 110, 0.08);
            color: var(--brand-text-secondary);
        }}

        /* Hero + cards */
        .ll-hero-card {{
            padding: var(--space-lg);
            border-radius: 18px;
            border: 1px solid var(--brand-border);
            background: radial-gradient(circle at top left,
                        rgba(37, 99, 235, 0.10),
                        transparent 60%),
                        var(--brand-surface);
            margin-bottom: var(--space-lg);
        }}

        .ll-step-card {{
            padding: var(--space-md);
            border-radius: 14px;
            border: 1px dashed var(--brand-border);
            background: rgba(15, 23, 42, 0.02);
        }}

        .ll-step-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 26px;
            height: 26px;
            border-radius: 999px;
            background: var(--brand-primary-soft);
            color: var(--brand-primary);
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: var(--space-sm);
        }}

        /* Report cards & badges */
        .ll-report-card {{
            border-radius: 14px;
            border: 1px solid var(--brand-border);
            padding: var(--space-md);
            background: var(--brand-surface);
        }}

        .ll-empty-state {{
            border-radius: 18px;
            border: 1px dashed var(--brand-border);
            padding: var(--space-lg);
            text-align: center;
            background: rgba(15, 23, 42, 0.02);
        }}

        .ll-empty-emoji {{
            font-size: 2rem;
            margin-bottom: var(--space-sm);
        }}

        .ll-empty-title {{
            font-weight: 600;
            margin-bottom: var(--space-xs);
        }}

        .ll-empty-subtitle {{
            font-size: 0.9rem;
            color: var(--brand-text-secondary);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def severity_badge(severity: str) -> str:
    colour = SEVERITY_COLOURS.get(severity, "#6b7280")
    return (
        f'<span class="ll-status-pill" '
        f'style="background:{colour}1a;color:#111827;">'
        f"{severity}</span>"
    )


def main():
    st.set_page_config(page_title="Local Lens", page_icon="📸", layout="wide")

    active_theme = init_theme()
    apply_theme_css(active_theme)

    header_col, toggle_col = st.columns([6, 1])
    with header_col:
        st.markdown(
            """
            <div class="ll-hero-card">
                <div class="ll-hero-title">📸 Local Lens</div>
                <p class="ll-hero-subtitle">
                    Turn quick snapshots into structured council-ready reports.
                    Upload an image, let AI analyse it, and submit in under a minute.
                </p>
                <div style="margin-top:16px; display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
                    <button disabled style="
                        background: var(--brand-primary);
                        color: #ffffff;
                        border: none;
                        border-radius: 999px;
                        padding: 8px 16px;
                        font-size: 0.9rem;
                        font-weight: 600;
                        cursor: pointer;
                    ">
                        Start a new report ↓
                    </button>
                    <span class="ll-helper-text">
                        Go to <strong>Report an Issue</strong> below to begin.
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with toggle_col:
        st.markdown("<div style='text-align:right'>", unsafe_allow_html=True)
        is_dark = active_theme == "dark"
        new_is_dark = st.toggle("Dark mode", value=is_dark)
        if new_is_dark != is_dark:
            set_theme("dark" if new_is_dark else "light")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 3-step visual guide
    step_col1, step_col2, step_col3 = st.columns(3)
    with step_col1:
        st.markdown(
            """
            <div class="ll-step-card">
                <div class="ll-step-badge">1</div>
                <div><strong>Upload an image</strong></div>
                <div class="ll-helper-text">
                    Snap a quick photo of a street, park, or public space issue.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with step_col2:
        st.markdown(
            """
            <div class="ll-step-card">
                <div class="ll-step-badge">2</div>
                <div><strong>AI analyses it</strong></div>
                <div class="ll-helper-text">
                    Our AI suggests a title, severity, category, and recommended action.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with step_col3:
        st.markdown(
            """
            <div class="ll-step-card">
                <div class="ll-step-badge">3</div>
                <div><strong>Submit to council</strong></div>
                <div class="ll-helper-text">
                    Review the auto-filled form, edit if needed, then submit your report.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if REQUIRE_AI:
        if ENABLE_OLLAMA:
            st.success("✅ AI mode active — every report is automatically analysed by Ollama.")
        else:
            st.error(
                "⚠️ AI-required mode is ON but Ollama is disabled. "
                "Set ENABLE_OLLAMA = true in your secrets."
            )
    if REQUIRE_GEOLOCATION:
        st.info("📍 Geolocation required — reports must include valid coordinates.")

    upload_service = UploadService()
    backup_service = BackupService()
    reports = upload_service.list_uploaded_images()

    for key in ("pending_upload", "analyzed_file_id", "council_authed"):
        if key not in st.session_state:
            st.session_state[key] = None if key != "council_authed" else False

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Total Reports", len(reports))
    with col_b:
        by_category = {}
        for r in reports:
            cat = r.get("category", "Unknown")
            by_category[cat] = by_category.get(cat, 0) + 1
        top_category = max(by_category, key=by_category.get) if by_category else "-"
        st.metric("Top Category", top_category)
    with col_c:
        latest = reports[0].get("upload_date", "-") if reports else "-"
        if latest and latest != "-":
            latest = str(latest)[:10]
        st.metric("Latest Report", latest)

    st.divider()

    tab_upload, tab_reports, tab_map, tab_insights, tab_backup = st.tabs(
        ["📤 Report an Issue", "📋 View Reports", "🗺️ Map", "🏛 Council Insights", "💾 Backup"]
    )

    # ── TAB 1: Report an Issue ────────────────────────────────────────────────
    with tab_upload:
        st.subheader("Report a Community Issue")
        st.markdown(
            "Take a photo of the problem, upload it below, and **AI automatically fills "
            "the entire report** for you. Review, adjust if needed, and submit."
        )

        uploaded_file = st.file_uploader(
            "📷 Upload your photo",
            type=["jpg", "jpeg", "png"],
            help="Supported formats: JPG, JPEG, PNG",
            key="upload_file",
        )

        if uploaded_file is not None:
            file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            if st.session_state.analyzed_file_id != file_id:
                with st.spinner("🤖 AI is analysing your image — this takes a few seconds…"):
                    result = upload_service.analyze_image(uploaded_file)
                st.session_state.analyzed_file_id = file_id
                if result.get("success"):
                    st.session_state.pending_upload = result
                    st.toast("✅ Analysis complete! Review the pre-filled report below.", icon="🤖")
                else:
                    st.session_state.pending_upload = None
                    st.error(result.get("message", "AI analysis failed."))

        pending = st.session_state.pending_upload

        if pending is None:
            if not ENABLE_OLLAMA:
                st.warning(
                    "Ollama is **disabled**. Set `ENABLE_OLLAMA = true` in secrets to enable "
                    "automatic AI form-filling."
                )
            else:
                st.info("⬆️ Upload an image above and AI will instantly fill the report for you.")
        else:
            analysis = pending.get("analysis", {})
            file_bytes = pending.get("file_bytes", b"")
            filename = pending.get("filename", "image")

            col_img, col_form = st.columns([1, 2], gap="large")

            with col_img:
                st.markdown("**📷 Your Photo**")
                st.image(file_bytes, use_container_width=True)
                sev = analysis.get("severity") or "Medium"
                st.markdown(
                    f"<span class='ll-meta-text'>AI severity assessment</span> {severity_badge(sev)}",
                    unsafe_allow_html=True,
                )
                st.caption(f"File: {filename}")
                if analysis.get("ai_raw"):
                    with st.expander("🔍 Raw AI output"):
                        st.code(analysis["ai_raw"], language="json")
                if analysis.get("ollama_error"):
                    st.warning(f"AI error: {analysis['ollama_error']}")

            with col_form:
                st.markdown("**📝 Report Details — AI has pre-filled these for you**")
                st.caption(
                    "All fields are editable. Correct anything the AI got wrong, then submit. "
                    "To avoid duplicates, we limit how often the same issue can be re-reported."
                )

                with st.form("submit_report_form"):
                    title = st.text_input(
                        "Report Title",
                        value=str(analysis.get("title") or ""),
                        placeholder="Short one-line summary of the issue",
                    )

                    col_cat, col_sev = st.columns(2)
                    with col_cat:
                        ai_category = str(analysis.get("category") or "Other")
                        cat_index = (
                            VALID_CATEGORIES.index(ai_category)
                            if ai_category in VALID_CATEGORIES
                            else len(VALID_CATEGORIES) - 1
                        )
                        category = st.selectbox("Category", options=VALID_CATEGORIES, index=cat_index)
                    with col_sev:
                        ai_severity = str(analysis.get("severity") or "Medium")
                        sev_index = (
                            VALID_SEVERITIES.index(ai_severity)
                            if ai_severity in VALID_SEVERITIES
                            else 1
                        )
                        severity = st.selectbox(
                            "Severity",
                            options=VALID_SEVERITIES,
                            index=sev_index,
                            help="Low=minor | Medium=inconvenience | High=safety risk | Critical=immediate danger",
                        )

                    description = st.text_area(
                        "Description",
                        value=str(analysis.get("details") or ""),
                        height=120,
                        placeholder="Describe the issue in detail…",
                    )
                    recommended_action = st.text_area(
                        "Recommended Action",
                        value=str(analysis.get("recommended_action") or ""),
                        height=80,
                        placeholder="What should the council do?",
                    )
                    location = st.text_input(
                        "Location",
                        value=str(analysis.get("location") or ""),
                        placeholder="Street name, landmark, or postcode",
                    )

                    col_lat, col_lon = st.columns(2)
                    with col_lat:
                        lat_val = analysis.get("latitude")
                        latitude_text = st.text_input(
                            "Latitude",
                            value="" if lat_val is None else str(lat_val),
                            placeholder="e.g. 51.5074",
                        )
                    with col_lon:
                        lon_val = analysis.get("longitude")
                        longitude_text = st.text_input(
                            "Longitude",
                            value="" if lon_val is None else str(lon_val),
                            placeholder="e.g. -0.1278",
                        )

                    reporter_email = st.text_input(
                        "Your email (optional)",
                        value="",
                        placeholder="Used only to avoid repeated reports of the same issue.",
                        help="We use this to prevent duplicate reports of the same issue from the same person within a short time window.",
                    )

                    st.markdown("---")
                    col_submit, col_clear = st.columns([3, 1])
                    with col_submit:
                        submit_report = st.form_submit_button(
                            "✅ Submit Report", use_container_width=True, type="primary"
                        )
                    with col_clear:
                        clear_btn = st.form_submit_button("🗑️ Clear", use_container_width=True)

                if clear_btn:
                    st.session_state.pending_upload = None
                    st.session_state.analyzed_file_id = None
                    st.rerun()

                if submit_report:
                    try:
                        latitude = float(latitude_text) if latitude_text.strip() else None
                        longitude = float(longitude_text) if longitude_text.strip() else None
                    except ValueError:
                        st.error("Latitude and longitude must be valid numbers.")
                        return

                    if (latitude is None or longitude is None) and not location.strip():
                        st.warning(
                            "📍 No location found. Please enter at least a street name or postcode."
                        )
                        return

                    if not title.strip():
                        st.warning("Please provide a report title.")
                        return

                    reporter_id = reporter_email.strip() or None

                    final_analysis = {
                        **analysis,
                        "title": title,
                        "category": category,
                        "severity": severity,
                        "details": description,
                        "recommended_action": recommended_action,
                        "location": location,
                        "latitude": latitude,
                        "longitude": longitude,
                    }

                    with st.spinner("Submitting report…"):
                        upload_result = upload_service.upload_image_bytes(
                            file_bytes=pending.get("file_bytes"),
                            original_name=pending.get("filename"),
                            content_type=pending.get("content_type"),
                            manual_location=location or None,
                            manual_latitude=latitude,
                            manual_longitude=longitude,
                            reporter_id=reporter_id,
                            analysis_override=final_analysis,
                        )

                    if upload_result.get("success"):
                        st.success("🎉 Report submitted! Thank you for helping improve your community.")
                        st.session_state.pending_upload = None
                        st.session_state.analyzed_file_id = None
                        st.rerun()
                    else:
                        st.error(upload_result.get("message", "Upload failed."))

    # ── TAB 2: View Reports ────────────────────────────────────────────────────
    with tab_reports:
        st.subheader("Community Reports")
        if not reports:
            st.markdown(
                """
                <div class="ll-empty-state">
                    <div class="ll-empty-emoji">🗂️</div>
                    <div class="ll-empty-title">No reports yet</div>
                    <div class="ll-empty-subtitle">
                        When residents start submitting reports, they will appear here with
                        AI-assessed severity, categories, and locations.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            with filter_col1:
                search_term = st.text_input("🔍 Search by filename or location", "")
            with filter_col2:
                all_categories = ["All"] + sorted(
                    {r.get("category", "Unknown") for r in reports if r.get("category")}
                )
                category_filter = st.selectbox("Category", all_categories)
            with filter_col3:
                all_severities = ["All"] + VALID_SEVERITIES
                severity_filter = st.selectbox("Severity", all_severities)

            filtered = reports
            if search_term.strip():
                term = search_term.lower()
                filtered = [
                    r for r in filtered
                    if term in str(r.get("filename", "")).lower()
                    or term in str(r.get("location", "")).lower()
                ]
            if category_filter != "All":
                filtered = [r for r in filtered if r.get("category") == category_filter]
            if severity_filter != "All":
                filtered = [r for r in filtered if r.get("severity") == severity_filter]

            st.caption(f"Showing {len(filtered)} of {len(reports)} reports")

            for report in filtered:
                sev = report.get("severity", "Medium")
                badge = severity_badge(sev)
                title_text = report.get("title") or report.get("filename", "Untitled")
                cat = report.get("category", "Unknown")
                loc = report.get("location", "Unknown location")
                date = str(report.get("upload_date", "")).split("T")[0] or "Unknown date"
                details_text = report.get("additional_details") or report.get("details", "")
                action_text = report.get("recommended_action", "")
                image_url = report.get("cloud_storage_url") or report.get("image_path")

                with st.container(border=True):
                    header_col, meta_col = st.columns([3, 1])
                    with header_col:
                        st.markdown(f"**{title_text}**&nbsp;&nbsp;{badge}", unsafe_allow_html=True)
                        st.caption(
                            f"<span class='ll-meta-text'>🏷️ {cat}  |  📍 {loc}  |  "
                            f"📅 {date}</span>",
                            unsafe_allow_html=True,
                        )
                    with meta_col:
                        if image_url:
                            st.image(image_url, width=120)
                    if details_text:
                        st.markdown(f"*{details_text}*")
                    if action_text:
                        st.markdown(f"**💡 Recommended action:** {action_text}")

    # ── TAB 3: Map ─────────────────────────────────────────────────────────────
    with tab_map:
        st.subheader("Report Locations")
        if reports:
            map_points = []
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
        else:
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
    # ── TAB 4: Council Insights ────────────────────────────────────────────────
    with tab_insights:
        st.subheader("Council Insights")

        if not COUNCIL_ADMIN_PASSWORD:
            st.warning(
                "Council analytics password is not configured. "
                "Set `COUNCIL_ADMIN_PASSWORD` in `.streamlit/secrets.toml` to protect this view."
            )

        if not st.session_state.get("council_authed", False) and COUNCIL_ADMIN_PASSWORD:
            st.info("This area is reserved for council staff.")
            password = st.text_input("Council admin password", type="password", key="council_password")
            if st.button("Log in", key="council_login_button"):
                if password == COUNCIL_ADMIN_PASSWORD:
                    st.session_state["council_authed"] = True
                    st.success("Logged in as council.")
                else:
                    st.error("Incorrect password.")

        if st.session_state.get("council_authed", False) or not COUNCIL_ADMIN_PASSWORD:
            if not reports:
                st.markdown(
                    """
                    <div class="ll-empty-state">
                        <div class="ll-empty-emoji">📊</div>
                        <div class="ll-empty-title">Analytics will appear here</div>
                        <div class="ll-empty-subtitle">
                            Once residents start submitting reports, you will see breakdowns
                            by category, severity, and trends over time.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                df = pd.DataFrame(reports)

                # Normalise dates for charting
                if "upload_date" in df.columns:
                    df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Reports by Category**")
                    cat_counts = (
                        df["category"]
                        .fillna("Unknown")
                        .value_counts()
                        .rename_axis("Category")
                        .reset_index(name="Reports")
                    )
                    st.bar_chart(cat_counts.set_index("Category"))

                with col2:
                    st.markdown("**Reports by Severity**")
                    if "severity" in df.columns:
                        sev_counts = (
                            df["severity"]
                            .fillna("Medium")
                            .value_counts()
                            .rename_axis("Severity")
                            .reset_index(name="Reports")
                        )
                        st.bar_chart(sev_counts.set_index("Severity"))

                st.markdown("---")
                st.markdown("**Reports Over Time**")
                if "upload_date" in df.columns and df["upload_date"].notna().any():
                    time_series = (
                        df.dropna(subset=["upload_date"])
                        .groupby(df["upload_date"].dt.date)
                        .size()
                        .rename("Reports")
                        .reset_index()
                        .rename(columns={"upload_date": "Date"})
                    )
                    st.line_chart(time_series.set_index("Date"))
                else:
                    st.caption("Report dates are not available yet for time-based analytics.")

    # ── TAB 5: Backup ──────────────────────────────────────────────────────────
    with tab_backup:
        st.subheader("Backup Management")
        if COUNCIL_ADMIN_PASSWORD and not st.session_state.get("council_authed", False):
            st.info("Backups are restricted to council staff. Log in on the Council Insights tab to access this area.")
        else:
            if st.button("▶️ Run Backup"):
                backup_result = backup_service.run_backup()
                if backup_result["success"]:
                    st.success(backup_result.get("message", "Backup completed."))
                    st.caption(backup_result.get("backup_file", ""))
                else:
                    st.error(f"Backup failed: {backup_result['message']}")
            backups = backup_service.list_backups()
            if backups:
                st.write("Recent backup files:")
                st.write(backups)
            else:
                st.info("No backups yet.")


if __name__ == "__main__":
    main()
