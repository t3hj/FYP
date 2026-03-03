import streamlit as st
from config.settings import ENABLE_OLLAMA, REQUIRE_AI, REQUIRE_GEOLOCATION
from src.services.upload_service import UploadService
from src.services.backup_service import BackupService


def main():
    st.set_page_config(page_title="Local Lens", page_icon="📸", layout="wide")

    st.title("📸 Local Lens")
    st.caption("Upload images, view shared reports, and export Supabase backups.")

    if REQUIRE_AI:
        if ENABLE_OLLAMA:
            st.success("AI-required mode is ON. Every upload must be analyzed by Ollama.")
        else:
            st.error("AI-required mode is ON but Ollama is disabled. Uploads will be blocked until ENABLE_OLLAMA is true.")
    if REQUIRE_GEOLOCATION:
        st.info("Geolocation-required mode is ON. Uploads must include valid coordinates.")

    upload_service = UploadService()
    backup_service = BackupService()
    reports = upload_service.list_uploaded_images()

    if "pending_upload" not in st.session_state:
        st.session_state.pending_upload = None

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Total Reports", len(reports))
    with col_b:
        latest_report = reports[0].get("upload_date") if reports else "-"
        st.metric("Latest Upload", latest_report)

    tab_upload, tab_reports, tab_map, tab_backup = st.tabs(["Upload", "Reports", "Map", "Backup"])

    with tab_upload:
        st.subheader("Upload and Auto-Fill")
        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=["jpg", "jpeg", "png"],
            help="Supported formats: JPG, JPEG, PNG",
            key="upload_file",
        )

        if st.button("Analyze Image", use_container_width=True):
            if uploaded_file is None:
                st.warning("Please choose an image first.")
            else:
                analysis_result = upload_service.analyze_image(uploaded_file)
                if not analysis_result.get("success"):
                    st.error(analysis_result.get("message", "Image analysis failed."))
                else:
                    st.session_state.pending_upload = analysis_result
                    st.success("AI analysis complete. Review details and submit.")

        pending = st.session_state.pending_upload
        if pending:
            analysis = pending.get("analysis", {})
            st.caption("AI prefilled these details. You can edit before submitting.")
            with st.form("submit_report_form"):
                category = st.text_input("Category", value=str(analysis.get("category") or "Other"))
                details = st.text_area("Details", value=str(analysis.get("details") or ""))
                location = st.text_input("Location", value=str(analysis.get("location") or ""))
                latitude_text = st.text_input(
                    "Latitude",
                    value="" if analysis.get("latitude") is None else str(analysis.get("latitude")),
                )
                longitude_text = st.text_input(
                    "Longitude",
                    value="" if analysis.get("longitude") is None else str(analysis.get("longitude")),
                )

                submit_report = st.form_submit_button("Submit Report")

            if submit_report:
                try:
                    latitude = float(latitude_text) if latitude_text.strip() else None
                    longitude = float(longitude_text) if longitude_text.strip() else None
                except ValueError:
                    st.error("Latitude and longitude must be valid numbers.")
                    return

                if (latitude is None or longitude is None) and not location.strip():
                    st.warning("Could not extract geolocation. Please enter a location before submitting.")
                    return

                final_analysis = {
                    **analysis,
                    "category": category,
                    "details": details,
                    "location": location,
                    "latitude": latitude,
                    "longitude": longitude,
                }

                upload_result = upload_service.upload_image_bytes(
                    file_bytes=pending.get("file_bytes"),
                    original_name=pending.get("filename"),
                    content_type=pending.get("content_type"),
                    manual_location=location or None,
                    manual_latitude=latitude,
                    manual_longitude=longitude,
                    analysis_override=final_analysis,
                )

                if upload_result.get("success"):
                    st.success("Report submitted successfully!")
                    st.session_state.pending_upload = None
                    st.rerun()
                else:
                    st.error(upload_result.get("message", "Upload failed."))

            if st.button("Clear Analysis", use_container_width=True):
                st.session_state.pending_upload = None
                st.rerun()

    with tab_reports:
        st.subheader("Stored Reports")
        if reports:
            search_term = st.text_input("Search by filename", "")
            if search_term.strip():
                filtered_reports = [
                    report
                    for report in reports
                    if search_term.lower() in str(report.get("filename", "")).lower()
                ]
            else:
                filtered_reports = reports

            st.dataframe(filtered_reports, use_container_width=True)
        else:
            st.info("No reports found yet.")

    with tab_map:
        st.subheader("Map View")
        if reports:
            map_points = []
            for report in reports:
                latitude = report.get("latitude")
                longitude = report.get("longitude")

                if latitude is None or longitude is None:
                    continue

                try:
                    map_points.append({"lat": float(latitude), "lon": float(longitude)})
                except (TypeError, ValueError):
                    continue

            if map_points:
                st.map(map_points)
                st.caption(f"Showing {len(map_points)} report locations.")
            else:
                st.info("No report coordinates found yet. Add latitude/longitude fields to report data to use map view.")
        else:
            st.info("No reports found yet.")

    with tab_backup:
        st.subheader("Backup Management")
        if st.button("Run Backup"):
            backup_result = backup_service.run_backup()
            if backup_result["success"]:
                st.success(backup_result.get("message", "Backup completed successfully!"))
                st.caption(backup_result.get("backup_file", ""))
            else:
                st.error(f"Error during backup: {backup_result['message']}")

        backups = backup_service.list_backups()
        if backups:
            st.write("Recent backup files")
            st.write(backups)
        else:
            st.info("No backups available yet.")

if __name__ == "__main__":
    main()