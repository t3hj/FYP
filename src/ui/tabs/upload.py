import streamlit as st

from src.ui.theme import severity_badge


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
        if not enable_ollama:
            st.warning(
                "Ollama is **disabled**. Set `ENABLE_OLLAMA = true` in secrets to enable "
                "automatic AI form-filling."
            )
        else:
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
                    valid_categories.index(ai_category)
                    if ai_category in valid_categories
                    else len(valid_categories) - 1
                )
                category = st.selectbox("Category", options=valid_categories, index=cat_index)
            with col_sev:
                ai_severity = str(analysis.get("severity") or "Medium")
                sev_index = (
                    valid_severities.index(ai_severity)
                    if ai_severity in valid_severities
                    else 1
                )
                severity = st.selectbox(
                    "Severity",
                    options=valid_severities,
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

