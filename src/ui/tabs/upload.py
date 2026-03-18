import folium
import streamlit as st
from streamlit_folium import st_folium

from src.ui.theme import severity_badge, SEVERITY_COLOURS


def render_upload_tab(
    upload_service,
    *,
    enable_ollama: bool,
    require_ai: bool,
    valid_categories: list[str],
    valid_severities: list[str],
) -> None:
    st.subheader("Report a Community Issue")
    st.markdown(
        "Take a photo of the problem, upload it below, and **AI automatically fills "
        "the entire report** for you. Review, adjust if needed, and submit."
    )

    st.markdown(
        """
        <div class="ll-upload-zone">
            <div class="ll-upload-icon">📸</div>
            <div class="ll-upload-title">Drag and drop your photo here</div>
            <div class="ll-upload-subtitle">or click below to browse files</div>
            <div class="ll-upload-requirements">
                Supported formats: JPG, JPEG, PNG • Max 20MB per file
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "📷",
        type=["jpg", "jpeg", "png"],
        help="Supported formats: JPG, JPEG, PNG. Max 20MB.",
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
                # Reset map pin when a new image is uploaded
                st.session_state.map_picked_lat = None
                st.session_state.map_picked_lon = None
                st.toast("✅ Analysis complete! Review the pre-filled report below.", icon="🤖")
            else:
                st.session_state.pending_upload = None
                st.error(result.get("message", "AI analysis failed."))

    pending = st.session_state.pending_upload

    if pending is None:
        st.info("⬆️ Upload an image above and AI will instantly fill the report for you.")
        return

    analysis = pending.get("analysis", {})
    file_bytes = pending.get("file_bytes", b"")
    filename = pending.get("filename", "image")

    # Initialise map pin session keys
    if "map_picked_lat" not in st.session_state:
        st.session_state.map_picked_lat = None
    if "map_picked_lon" not in st.session_state:
        st.session_state.map_picked_lon = None

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
        st.caption("✏️ All fields are editable. Correct anything the AI got wrong, then submit.")

        # ── PART 1: form fields above location ───────────────────────────────
        with st.form("submit_report_form_top"):
            st.markdown("#### Essential Information")
            title = st.text_input(
                "Report Title *",
                value=str(analysis.get("title") or ""),
                placeholder="Short one-line summary of the issue",
                help="Required: Brief, clear description of the problem",
            )

            col_cat, col_sev = st.columns(2)
            with col_cat:
                ai_category = str(analysis.get("category") or "Other")
                cat_index = (
                    valid_categories.index(ai_category)
                    if ai_category in valid_categories
                    else len(valid_categories) - 1
                )
                category = st.selectbox(
                    "Category *",
                    options=valid_categories,
                    index=cat_index,
                    help="Type of community issue",
                )
            with col_sev:
                ai_severity = str(analysis.get("severity") or "Medium")
                sev_index = (
                    valid_severities.index(ai_severity)
                    if ai_severity in valid_severities
                    else 1
                )
                severity = st.selectbox(
                    "Severity *",
                    options=valid_severities,
                    index=sev_index,
                    help="Low: Minor | Medium: Inconvenience | High: Safety Risk | Critical: Immediate Danger",
                )

            st.markdown("#### Details")
            description = st.text_area(
                "Description *",
                value=str(analysis.get("details") or ""),
                height=100,
                placeholder="Describe what you see and why it's a problem…",
            )
            recommended_action = st.text_area(
                "Recommended Action",
                value=str(analysis.get("recommended_action") or ""),
                height=80,
                placeholder="What should the council do?",
            )

            st.markdown("#### Location Information")
            location = st.text_input(
                "Street Address or Landmark *",
                value=str(analysis.get("location") or ""),
                placeholder="e.g., Main Street near Town Hall, or postcode SW1A 1AA",
            )

            # Lat/lon fields — seeded from map pin (via session state) or AI
            col_lat, col_lon = st.columns(2)
            with col_lat:
                lat_default = st.session_state.map_picked_lat or analysis.get("latitude")
                latitude_text = st.text_input(
                    "Latitude",
                    value="" if lat_default is None else str(lat_default),
                    placeholder="e.g. 51.5074",
                    help="Auto-filled from map pin or image EXIF data.",
                )
            with col_lon:
                lon_default = st.session_state.map_picked_lon or analysis.get("longitude")
                longitude_text = st.text_input(
                    "Longitude",
                    value="" if lon_default is None else str(lon_default),
                    placeholder="e.g. -0.1278",
                    help="Auto-filled from map pin or image EXIF data.",
                )

            st.markdown("#### Your Contact Info")
            reporter_email = st.text_input(
                "Email Address (optional)",
                value="",
                placeholder="you@example.com",
                help="Used only to prevent duplicate submissions from the same person.",
            )

            st.markdown("---")
            col_submit, col_clear = st.columns([3, 1])
            with col_submit:
                submit_report = st.form_submit_button(
                    "✅ Submit Report", use_container_width=True, type="primary"
                )
            with col_clear:
                clear_btn = st.form_submit_button("🗑️ Clear", use_container_width=True)

        # ── MAP PICKER — must live outside st.form ────────────────────────────
        # Determine best center: pinned → AI coords → London fallback
        c_lat = st.session_state.map_picked_lat or analysis.get("latitude") or 51.5074
        c_lon = st.session_state.map_picked_lon or analysis.get("longitude") or -0.1278
        has_pin = st.session_state.map_picked_lat is not None

        with st.expander(
            "📍 Pin exact location on map" + (" ✅" if has_pin else ""),
            expanded=has_pin,
        ):
            st.caption(
                "Click anywhere on the map to drop a pin. "
                "This will override the coordinates above."
            )

            picker_map = folium.Map(
                location=[c_lat, c_lon],
                zoom_start=15,
                tiles="CartoDB positron",
                control_scale=True,
            )

            if has_pin:
                folium.Marker(
                    [st.session_state.map_picked_lat, st.session_state.map_picked_lon],
                    tooltip="📍 Your pinned location",
                    icon=folium.Icon(color="blue", icon="map-pin", prefix="fa"),
                ).add_to(picker_map)

            map_result = st_folium(
                picker_map,
                use_container_width=True,
                height=340,
                key="upload_location_picker",
                returned_objects=["last_clicked"],
            )

            # Update pin on click
            if map_result and map_result.get("last_clicked"):
                clicked = map_result["last_clicked"]
                new_lat = round(clicked["lat"], 6)
                new_lon = round(clicked["lng"], 6)
                # Only rerun if the click is actually different from current pin
                if (
                    new_lat != st.session_state.map_picked_lat
                    or new_lon != st.session_state.map_picked_lon
                ):
                    st.session_state.map_picked_lat = new_lat
                    st.session_state.map_picked_lon = new_lon
                    st.rerun()

            if has_pin:
                pc1, pc2 = st.columns([3, 1])
                with pc1:
                    st.success(
                        f"📍 Pinned at {st.session_state.map_picked_lat}, "
                        f"{st.session_state.map_picked_lon}"
                    )
                with pc2:
                    if st.button("🗑️ Clear pin", key="clear_map_pin", use_container_width=True):
                        st.session_state.map_picked_lat = None
                        st.session_state.map_picked_lon = None
                        st.rerun()
            else:
                st.info("👆 Click the map to drop a pin at the exact problem location.")

        # ── Form submission logic ─────────────────────────────────────────────
        if clear_btn:
            st.session_state.pending_upload = None
            st.session_state.analyzed_file_id = None
            st.session_state.map_picked_lat = None
            st.session_state.map_picked_lon = None
            st.rerun()

        if submit_report:
            # Map pin takes priority over manually typed coords
            if st.session_state.map_picked_lat is not None:
                latitude_text = str(st.session_state.map_picked_lat)
                longitude_text = str(st.session_state.map_picked_lon)

            try:
                latitude = float(latitude_text) if latitude_text.strip() else None
                longitude = float(longitude_text) if longitude_text.strip() else None
            except ValueError:
                st.error("Latitude and longitude must be valid numbers.")
                return

            if (latitude is None or longitude is None) and not location.strip():
                st.warning(
                    "📍 No location found. "
                    "Either drop a pin on the map or enter a street name / postcode."
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

            # ── Nearby duplicate check ────────────────────────────────────────
            nearby_reports = []
            if latitude is not None and longitude is not None:
                nearby_reports = upload_service.find_nearby_similar_reports(
                    latitude, longitude, category, location_text=location, radius_km=0.5
                )
            elif location:
                nearby_reports = upload_service.find_nearby_similar_reports(
                    None, None, category, location_text=location
                )

            if nearby_reports and not st.session_state.get("show_duplicate_warning"):
                st.session_state.nearby_duplicate_reports = nearby_reports
                st.session_state.pending_report_data = {
                    "file_bytes": pending.get("file_bytes"),
                    "filename": pending.get("filename"),
                    "content_type": pending.get("content_type"),
                    "location": location,
                    "latitude": latitude,
                    "longitude": longitude,
                    "reporter_id": reporter_id,
                    "analysis": final_analysis,
                }
                st.session_state.show_duplicate_warning = True
                st.rerun()

            # Clear flags once user confirms
            if st.session_state.get("show_duplicate_warning") and st.session_state.get("confirmed_despite_duplicates"):
                st.session_state.show_duplicate_warning = False
                st.session_state.confirmed_despite_duplicates = False
                nearby_reports = []

            # Show duplicate warning
            if st.session_state.get("show_duplicate_warning") and nearby_reports:
                st.warning("⚠️ **Similar reports already exist nearby!**")
                st.markdown(
                    "We found **{} {} issue{}** within 500 metres of your location. "
                    "Please review before submitting — it helps councils avoid duplicate work.".format(
                        len(nearby_reports),
                        category,
                        "s" if len(nearby_reports) != 1 else "",
                    )
                )

                for i, nearby in enumerate(nearby_reports, 1):
                    sev = nearby["severity"]
                    match_type = nearby.get("match_type", "proximity")

                    if match_type == "location_text":
                        dist_text = "same location name"
                    elif nearby["distance_m"] is not None:
                        dist_text = (
                            f"~{nearby['distance_m']}m away"
                            if nearby["distance_m"] >= 100
                            else "very close by"
                        )
                    else:
                        dist_text = "nearby"

                    with st.container(border=True):
                        col_info, col_action = st.columns([4, 1])
                        with col_info:
                            st.markdown(
                                f"""
                                <div style="display:flex;align-items:start;gap:0.5rem;">
                                    <div style="flex:1;">
                                        <div style="font-weight:600;margin-bottom:0.3rem;">
                                            #{i} {nearby['title']}
                                        </div>
                                        <div style="font-size:0.9rem;color:#64748b;margin-bottom:0.3rem;">
                                            📍 {nearby['location']} • {dist_text}
                                        </div>
                                        <div style="font-size:0.85rem;color:#94a3b8;">
                                            🕐 {nearby['upload_date']}
                                        </div>
                                    </div>
                                    <div style="flex-shrink:0;">{severity_badge(sev)}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        with col_action:
                            if st.button("👁 View", key=f"view_nearby_{i}", use_container_width=True):
                                st.session_state.view_nearby_id = nearby["id"]

                st.markdown("---")
                col_continue, col_cancel = st.columns(2)
                with col_continue:
                    if st.button(
                        "➡️ Continue submitting anyway",
                        use_container_width=True,
                        type="primary",
                    ):
                        st.session_state.confirmed_despite_duplicates = True
                        st.rerun()
                with col_cancel:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.show_duplicate_warning = False
                        st.session_state.nearby_duplicate_reports = []
                        st.session_state.pending_report_data = None
                        st.rerun()
                return

            # ── Proceed with upload ───────────────────────────────────────────
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
                st.session_state.map_picked_lat = None
                st.session_state.map_picked_lon = None
                st.rerun()
            else:
                st.error(upload_result.get("message", "Upload failed."))