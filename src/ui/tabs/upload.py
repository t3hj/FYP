import streamlit as st

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

    # Custom styled upload zone
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
            "✏️ All fields are editable. Correct anything the AI got wrong, then submit."
        )

        with st.form("submit_report_form"):
            # Essential info section
            st.markdown("#### Essential Information")
            title = st.text_input(
                "Report Title *",
                value=str(analysis.get("title") or ""),
                placeholder="Short one-line summary of the issue",
                help="Required: Brief, clear description of the problem",
            )
            if not title.strip():
                st.caption("⚠️ Title is required")

            col_cat, col_sev = st.columns(2)
            with col_cat:
                ai_category = str(analysis.get("category") or "Other")
                cat_index = (
                    valid_categories.index(ai_category)
                    if ai_category in valid_categories
                    else len(valid_categories) - 1
                )
                category = st.selectbox("Category *", options=valid_categories, index=cat_index,
                                       help="Type of issue: Road, Sidewalk, Park, etc.")
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

            # Details section
            st.markdown("#### Details")
            description = st.text_area(
                "Description *",
                value=str(analysis.get("details") or ""),
                height=100,
                placeholder="Describe what you see and why it's a problem…",
                help="Provide context and specific details",
            )
            
            recommended_action = st.text_area(
                "Recommended Action",
                value=str(analysis.get("recommended_action") or ""),
                height=80,
                placeholder="What should the council do? (e.g., repair surface, add signs)…",
                help="Optional: Your suggestion for fixing the issue",
            )

            # Location section
            st.markdown("#### Location Information")
            location = st.text_input(
                "Street Address or Landmark *",
                value=str(analysis.get("location") or ""),
                placeholder="e.g., Main Street near Town Hall, or postcode SW1A 1AA",
                help="Required: Where exactly is this issue?",
            )
            if not location.strip():
                st.caption("⚠️ Location is required (either address or coordinates)")

            col_lat, col_lon = st.columns(2)
            with col_lat:
                lat_val = analysis.get("latitude")
                latitude_text = st.text_input(
                    "Latitude (optional)",
                    value="" if lat_val is None else str(lat_val),
                    placeholder="e.g., 51.5074",
                    help="Decimal degrees (e.g., 51.5074). Find yours at google.com/maps",
                )
            with col_lon:
                lon_val = analysis.get("longitude")
                longitude_text = st.text_input(
                    "Longitude (optional)",
                    value="" if lon_val is None else str(lon_val),
                    placeholder="e.g., -0.1278",
                    help="Decimal degrees (e.g., -0.1278)",
                )
            
            st.caption("💡 **Pro tip:** Open Google Maps on your phone, long-press the exact spot, and you'll see the coordinates.")

            # Contact section
            st.markdown("#### Your Contact Info")
            reporter_email = st.text_input(
                "Email Address (optional)",
                value="",
                placeholder="you@example.com",
                help="We use this only to verify you and prevent duplicate reports from the same person.",
            )
            if reporter_email and "@" not in reporter_email:
                st.caption("⚠️ Please enter a valid email address")

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
                st.warning("📍 No location found. Please enter at least a street name or postcode.")
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

            # ── Check for nearby similar reports ──────────────────────────────────────
            nearby_reports = []
            if latitude is not None and longitude is not None:
                nearby_reports = upload_service.find_nearby_similar_reports(
                    latitude, longitude, category, location_text=location, radius_km=0.5
                )
            elif location:
                # If no GPS coordinates, search by location text
                nearby_reports = upload_service.find_nearby_similar_reports(
                    None, None, category, location_text=location
                )
            
            if nearby_reports and "show_duplicate_warning" not in st.session_state:
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
            
            # If user confirmed after warning, proceed with upload
            if st.session_state.get("show_duplicate_warning") and st.session_state.get("confirmed_despite_duplicates"):
                st.session_state.show_duplicate_warning = False
                st.session_state.confirmed_despite_duplicates = False
                nearby_reports = []  # Clear to proceed with actual upload
            
            # Show duplicate warning modal
            if st.session_state.get("show_duplicate_warning") and nearby_reports:
                st.warning("⚠️ **Similar reports already exist nearby!**")
                st.markdown(
                    "We found **{} {} issue{}** within 500 meters of your location. "
                    "Please review them before submitting — it helps councils avoid duplicate work.".format(
                        len(nearby_reports),
                        category,
                        "s" if len(nearby_reports) != 1 else ""
                    )
                )
                
                for i, nearby in enumerate(nearby_reports, 1):
                    sev = nearby["severity"]
                    match_type = nearby.get("match_type", "proximity")
                    
                    # Format distance text
                    if match_type == "location_text":
                        dist_text = "same location name"
                    elif nearby["distance_m"] is not None:
                        if nearby["distance_m"] >= 100:
                            dist_text = f"~{nearby['distance_m']}m away"
                        else:
                            dist_text = "very close by"
                    else:
                        dist_text = "nearby"
                    
                    sev_color = SEVERITY_COLOURS.get(sev, "#6b7280")
                    
                    with st.container(border=True):
                        col_info, col_action = st.columns([4, 1])
                        with col_info:
                            st.markdown(
                                f"""
                                <div style="display: flex; align-items: start; gap: 0.5rem;">
                                    <div style="flex: 1;">
                                        <div style="font-weight: 600; margin-bottom: 0.3rem;">#{i} {nearby['title']}</div>
                                        <div style="font-size: 0.9rem; color: #64748b; margin-bottom: 0.3rem;">
                                            📍 {nearby['location']} • {dist_text}
                                        </div>
                                        <div style="font-size: 0.85rem; color: #94a3b8;">
                                            🕐 {nearby['upload_date']}
                                        </div>
                                    </div>
                                    <div style="flex-shrink: 0;">
                                        {severity_badge(sev)}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        with col_action:
                            if st.button("👁 View", key=f"view_nearby_{i}", use_container_width=True):
                                st.session_state.view_nearby_id = nearby['id']
                
                st.markdown("---")
                col_continue, col_cancel = st.columns(2)
                with col_continue:
                    if st.button("➡️ Continue submitting anyway", use_container_width=True, type="primary"):
                        st.session_state.confirmed_despite_duplicates = True
                        st.rerun()
                with col_cancel:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.show_duplicate_warning = False
                        st.session_state.nearby_duplicate_reports = []
                        st.session_state.pending_report_data = None
                        st.rerun()
                
                return
            
            # Proceed with actual upload
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

