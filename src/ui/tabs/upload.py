import folium
import streamlit as st
from streamlit_folium import st_folium

from src.services.auth_service import get_user_id
from src.ui.components.auth import require_auth_prompt
from src.ui.theme import severity_badge

_CONFIDENCE_COLOURS = {
    "high":   ("#22c55e", "✓ High confidence"),
    "medium": ("#f59e0b", "~ Medium confidence"),
    "low":    ("#ef4444", "⚠ Low confidence — please review carefully"),
}


def _k(name: str) -> str:
    """Namespaced session-state key for upload form fields."""
    return f"uf_{name}"


def _init_state() -> None:
    """Ensure all required session-state keys exist on first run."""
    defaults = {
        "pending_upload":              None,
        "analyzed_file_id":            None,
        "map_picked_lat":              None,
        "map_picked_lon":              None,
        "show_duplicate_warning":      False,
        "nearby_duplicate_reports":    None,
        "pending_report_data":         None,
        "confirmed_despite_duplicates": False,
        # Incrementing this key forces st.file_uploader to mount a fresh widget
        "upload_file_version":         0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_upload_tab(
    upload_service,
    *,
    enable_ollama: bool,
    require_ai: bool,
    valid_categories: list[str],
    valid_severities: list[str],
) -> None:
    _init_state()

    st.subheader("Report a Community Issue")

    if not require_auth_prompt("submit a Local Lens report"):
        return

    st.markdown(
        "Take a photo of the problem, upload it below, and **AI automatically fills "
        "the entire report** for you. Review, adjust if needed, and submit."
    )

    # ── File uploader ─────────────────────────────────────────────────────────
    # Key includes a version counter — incrementing it mounts a fresh widget,
    # which is the only reliable way to clear a file_uploader in Streamlit.
    st.markdown(
        """
        <div class="ll-upload-zone">
            <div class="ll-upload-icon">📸</div>
            <div class="ll-upload-title">Drag and drop your photo here</div>
            <div class="ll-upload-subtitle">or click below to browse files</div>
            <div class="ll-upload-requirements">
                Supported formats: JPG, JPEG, PNG · Max 20MB
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    version = st.session_state.upload_file_version
    uploaded_file = st.file_uploader(
        "📷",
        type=["jpg", "jpeg", "png"],
        help="Supported formats: JPG, JPEG, PNG. Max 20MB.",
        key=f"upload_file_{version}",
    )

    # ── Run AI analysis once per new file ────────────────────────────────────
    if uploaded_file is not None:
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.analyzed_file_id != file_id:
            with st.spinner("🤖 AI is analysing your image — this takes a few seconds…"):
                result = upload_service.analyze_image(uploaded_file)
            st.session_state.analyzed_file_id = file_id

            if result.get("success"):
                st.session_state.pending_upload = result
                st.session_state.map_picked_lat = None
                st.session_state.map_picked_lon = None

                # Pre-seed form fields — set values directly in session state.
                # IMPORTANT: do NOT also pass index= to selectboxes that use these
                # keys, or Streamlit will throw a "default value conflict" error.
                a = result.get("analysis", {})
                st.session_state[_k("title")]    = str(a.get("title") or "")
                st.session_state[_k("desc")]     = str(a.get("details") or "")
                st.session_state[_k("action")]   = str(a.get("recommended_action") or "")
                st.session_state[_k("location")] = str(a.get("location") or "")

                # Selectbox values must be a valid option string, not an index
                ai_cat = a.get("category") or valid_categories[-1]
                st.session_state[_k("category")] = (
                    ai_cat if ai_cat in valid_categories else valid_categories[-1]
                )
                ai_sev = a.get("severity") or "Medium"
                st.session_state[_k("severity")] = (
                    ai_sev if ai_sev in valid_severities else "Medium"
                )

                st.toast("✅ Analysis complete! Review the pre-filled report below.", icon="🤖")
            else:
                st.session_state.pending_upload = None
                st.error(result.get("message", "AI analysis failed."))

    pending = st.session_state.pending_upload

    if pending is None:
        st.info("⬆️ Upload an image above and AI will instantly fill the report for you.")
        return

    analysis   = pending.get("analysis", {})
    file_bytes = pending.get("file_bytes", b"")
    filename   = pending.get("filename", "image")

    # ── SECTION 1: Photo + Report Details ────────────────────────────────────
    st.markdown("---")
    col_img, col_form = st.columns([1, 2], gap="large")

    with col_img:
        st.markdown("**📷 Your Photo**")
        st.image(file_bytes, use_container_width=True)

        sev  = st.session_state.get(_k("severity"), "Medium")
        conf = str(analysis.get("ai_confidence") or "medium").lower()
        conf_colour, conf_label = _CONFIDENCE_COLOURS.get(conf, ("#f59e0b", "~ Medium confidence"))

        st.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;flex-wrap:wrap;"
            f"margin-top:6px;'>"
            f"{severity_badge(sev)}"
            f"<span style='font-size:0.75rem;font-weight:600;color:{conf_colour};'>"
            f"{conf_label}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.caption(f"File: {filename}")

        if analysis.get("ai_raw"):
            with st.expander("🔍 Raw AI output"):
                st.code(analysis["ai_raw"], language="json")
        if analysis.get("ollama_error"):
            st.warning(f"AI error: {analysis['ollama_error']}")
        if not analysis.get("ai_enabled"):
            st.info("ℹ️ AI analysis is disabled. Fill in the form manually.")

    with col_form:
        st.markdown("**📝 Report Details — AI has pre-filled these for you**")
        st.caption("✏️ All fields are editable. Correct anything the AI got wrong.")

        st.text_input(
            "Report Title *",
            key=_k("title"),
            placeholder="Short one-line summary of the issue",
        )

        col_cat, col_sev = st.columns(2)
        with col_cat:
            # index= intentionally omitted — value comes from session state set above
            st.selectbox("Category *", options=valid_categories, key=_k("category"))
        with col_sev:
            st.selectbox(
                "Severity *",
                options=valid_severities,
                key=_k("severity"),
                help="Low: Minor · Medium: Inconvenience · High: Safety Risk · Critical: Immediate Danger",
            )

        st.text_area(
            "Description *",
            key=_k("desc"),
            height=110,
            placeholder="Describe what you see and why it's a problem…",
        )
        st.text_area(
            "Recommended Action",
            key=_k("action"),
            height=75,
            placeholder="What should the council do?",
        )

    # ── SECTION 2: Location — address left, map right ─────────────────────────
    st.markdown("---")
    st.markdown("**📍 Location**")
    st.caption(
        "Enter a street address or postcode, or click the map to drop a pin. "
        "Both help the council find the issue quickly."
    )

    pin_lat  = st.session_state.map_picked_lat
    pin_lon  = st.session_state.map_picked_lon
    exif_lat = analysis.get("latitude")
    exif_lon = analysis.get("longitude")

    loc_col, map_col = st.columns([1, 2], gap="large")

    with loc_col:
        st.text_input(
            "Street address, landmark or postcode *",
            key=_k("location"),
            placeholder="e.g. High Street, Harrow, HA1 1AA",
        )

        display_lat = pin_lat if pin_lat is not None else (exif_lat if exif_lat is not None else "")
        display_lon = pin_lon if pin_lon is not None else (exif_lon if exif_lon is not None else "")

        lc, lonc = st.columns(2)
        with lc:
            st.text_input(
                "Latitude",
                value="" if display_lat == "" else str(display_lat),
                key=_k("lat"),
                placeholder="51.5074",
                help="Auto-filled from map pin or photo EXIF.",
            )
        with lonc:
            st.text_input(
                "Longitude",
                value="" if display_lon == "" else str(display_lon),
                key=_k("lon"),
                placeholder="-0.1278",
                help="Auto-filled from map pin or photo EXIF.",
            )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if pin_lat is not None:
            st.success(f"📍 Pinned at {pin_lat:.5f}, {pin_lon:.5f}")
            if st.button("🗑️ Clear pin", key="clear_map_pin", use_container_width=True):
                st.session_state.map_picked_lat = None
                st.session_state.map_picked_lon = None
                st.rerun()
        elif exif_lat:
            st.info("📡 Coordinates extracted from photo EXIF data.")
        else:
            st.caption("👉 Click the map to place a pin at the exact location.")

    with map_col:
        c_lat = pin_lat or exif_lat or 51.5074
        c_lon = pin_lon or exif_lon or -0.1278
        zoom  = 15 if (pin_lat or exif_lat) else 13

        picker_map = folium.Map(
            location=[c_lat, c_lon],
            zoom_start=zoom,
            tiles="CartoDB positron",
            control_scale=True,
        )
        if pin_lat is not None:
            folium.Marker(
                [pin_lat, pin_lon],
                tooltip="📍 Your pinned location",
                icon=folium.Icon(color="blue", icon="map-pin", prefix="fa"),
            ).add_to(picker_map)
        elif exif_lat:
            folium.CircleMarker(
                location=[exif_lat, exif_lon],
                radius=9,
                color="#6366f1",
                fill=True,
                fill_color="#6366f1",
                fill_opacity=0.55,
                tooltip="📡 Location from photo EXIF",
            ).add_to(picker_map)

        map_result = st_folium(
            picker_map,
            use_container_width=True,
            height=290,
            key="upload_location_picker",
            returned_objects=["last_clicked"],
        )

        if map_result and map_result.get("last_clicked"):
            clicked = map_result["last_clicked"]
            new_lat = round(clicked["lat"], 6)
            new_lon = round(clicked["lng"], 6)
            if new_lat != pin_lat or new_lon != pin_lon:
                st.session_state.map_picked_lat = new_lat
                st.session_state.map_picked_lon = new_lon
                st.rerun()

    # ── SECTION 3: Duplicate warning + Submit / Clear ─────────────────────────
    st.markdown("---")

    if st.session_state.show_duplicate_warning:
        nearby_reports = st.session_state.nearby_duplicate_reports or []
        if nearby_reports:
            st.warning("⚠️ **Similar reports already exist nearby!**")
            cat_label = st.session_state.get(_k("category"), "")
            st.markdown(
                "We found **{}** nearby **{}** report{}. Review before submitting.".format(
                    len(nearby_reports), cat_label,
                    "s" if len(nearby_reports) != 1 else "",
                )
            )
            for i, nearby in enumerate(nearby_reports, 1):
                dm = nearby.get("distance_m")
                dist_text = (
                    "same location name"
                    if nearby.get("match_type") == "location_text"
                    else (f"~{dm}m away" if dm and dm >= 100 else "very close by")
                )
                with st.container(border=True):
                    ci, cb = st.columns([4, 1])
                    with ci:
                        st.markdown(
                            f"**#{i} {nearby['title']}**  \n"
                            f"<span style='font-size:0.85rem;color:#94a3b8;'>"
                            f"📍 {nearby['location']} · {dist_text} · "
                            f"📅 {nearby['upload_date']}</span>",
                            unsafe_allow_html=True,
                        )
                    with cb:
                        st.markdown(severity_badge(nearby["severity"]), unsafe_allow_html=True)

            st.markdown("---")
            ca, cb2 = st.columns(2)
            with ca:
                if st.button("➡️ Submit anyway", use_container_width=True,
                             type="primary", key="dup_submit_anyway"):
                    st.session_state.confirmed_despite_duplicates = True
                    st.session_state.show_duplicate_warning = False
                    st.rerun()
            with cb2:
                if st.button("❌ Cancel", use_container_width=True, key="dup_cancel"):
                    st.session_state.show_duplicate_warning = False
                    st.session_state.nearby_duplicate_reports = None
                    st.session_state.pending_report_data = None
                    st.rerun()
            return

    btn_col, clear_col = st.columns([4, 1])
    with btn_col:
        if st.button(
            "✅ Submit Report to Local Lens",
            use_container_width=True,
            type="primary",
            key="upload_submit_btn",
        ):
            _handle_submit(pending, analysis, upload_service)
    with clear_col:
        if st.button("🗑️ Clear", use_container_width=True, key="upload_clear_btn"):
            _clear_upload_state()
            st.rerun()


# ── Submit handler ─────────────────────────────────────────────────────────────

def _handle_submit(pending: dict, analysis: dict, upload_service) -> None:
    title       = str(st.session_state.get(_k("title"),    "")).strip()
    category    = str(st.session_state.get(_k("category"), "Other"))
    severity    = str(st.session_state.get(_k("severity"), "Medium"))
    description = str(st.session_state.get(_k("desc"),     "")).strip()
    action      = str(st.session_state.get(_k("action"),   "")).strip()
    location    = str(st.session_state.get(_k("location"), "")).strip()
    lat_text    = str(st.session_state.get(_k("lat"),      "")).strip()
    lon_text    = str(st.session_state.get(_k("lon"),      "")).strip()

    # Map pin takes precedence over manually typed coords
    if st.session_state.map_picked_lat is not None:
        lat_text = str(st.session_state.map_picked_lat)
        lon_text = str(st.session_state.map_picked_lon)

    if not title:
        st.warning("Please provide a report title.")
        return
    if not description:
        st.warning("Please provide a description.")
        return

    try:
        latitude  = float(lat_text)  if lat_text  else None
        longitude = float(lon_text)  if lon_text  else None
    except ValueError:
        st.error("Latitude and longitude must be valid numbers.")
        return

    if latitude is None and not location:
        st.warning(
            "📍 No location found. Drop a pin on the map or enter a street address / postcode."
        )
        return

    reporter_id  = get_user_id()  # always set — auth gate above ensures login
    final_analysis = {
        **analysis,
        "title":              title,
        "category":           category,
        "severity":           severity,
        "details":            description,
        "recommended_action": action,
        "location":           location,
        "latitude":           latitude,
        "longitude":          longitude,
    }

    # Nearby duplicate check (skip if user already confirmed)
    if not st.session_state.confirmed_despite_duplicates:
        nearby = upload_service.find_nearby_similar_reports(
            latitude, longitude, category,
            location_text=location,
            radius_km=0.5,
        )
        if nearby:
            st.session_state.nearby_duplicate_reports = nearby
            st.session_state.pending_report_data = {
                "file_bytes":   pending.get("file_bytes"),
                "filename":     pending.get("filename"),
                "content_type": pending.get("content_type"),
                "location":     location,
                "latitude":     latitude,
                "longitude":    longitude,
                "reporter_id":  reporter_id,
                "analysis":     final_analysis,
            }
            st.session_state.show_duplicate_warning = True
            st.rerun()
            return

    with st.spinner("Submitting your Local Lens report…"):
        result = upload_service.upload_image_bytes(
            file_bytes=pending.get("file_bytes"),
            original_name=pending.get("filename"),
            content_type=pending.get("content_type"),
            manual_location=location or None,
            manual_latitude=latitude,
            manual_longitude=longitude,
            reporter_id=reporter_id,
            analysis_override=final_analysis,
        )

    if result.get("success"):
        st.success("🎉 Report submitted! Thank you for helping your community.")
        _clear_upload_state()
        st.rerun()
    else:
        st.error(result.get("message", "Upload failed."))


# ── State helpers ──────────────────────────────────────────────────────────────

def _clear_upload_state() -> None:
    """Reset all upload form state, including forcing the file uploader to remount."""
    # Increment version → file_uploader gets a new key → mounts fresh with no file
    st.session_state.upload_file_version = (
        st.session_state.get("upload_file_version", 0) + 1
    )

    st.session_state.pending_upload              = None
    st.session_state.analyzed_file_id            = None
    st.session_state.map_picked_lat              = None
    st.session_state.map_picked_lon              = None
    st.session_state.show_duplicate_warning      = False
    st.session_state.nearby_duplicate_reports    = None
    st.session_state.pending_report_data         = None
    st.session_state.confirmed_despite_duplicates = False

    # Remove all form field values so widgets render with empty defaults
    for name in ("title", "category", "severity", "desc", "action", "location", "lat", "lon"):
        st.session_state.pop(_k(name), None)