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

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Total Reports", len(reports))
    with col_b:
        latest_report = reports[0].get("upload_date") if reports else "-"
        st.metric("Latest Upload", latest_report)

    tab_upload, tab_reports, tab_map, tab_backup = st.tabs(["Upload", "Reports", "Map", "Backup"])

    with tab_upload:
        st.subheader("Upload Image")
        with st.form("upload_form", clear_on_submit=True):
            uploaded_file = st.file_uploader(
                "Choose an image...",
                type=["jpg", "jpeg", "png"],
                help="Supported formats: JPG, JPEG, PNG",
            )
            manual_location = st.text_input("Location (optional)")
            manual_latitude_text = st.text_input("Latitude (optional)", placeholder="e.g. -37.8136")
            manual_longitude_text = st.text_input("Longitude (optional)", placeholder="e.g. 144.9631")
            submitted = st.form_submit_button("Upload")

        if submitted:
            if uploaded_file is None:
                st.warning("Please choose an image before uploading.")
            else:
                try:
                    manual_latitude = float(manual_latitude_text) if manual_latitude_text.strip() else None
                    manual_longitude = float(manual_longitude_text) if manual_longitude_text.strip() else None
                except ValueError:
                    st.error("Latitude and longitude must be valid numbers.")
                    return

                result = upload_service.upload_image(
                    uploaded_file,
                    manual_location=manual_location or None,
                    manual_latitude=manual_latitude,
                    manual_longitude=manual_longitude,
                )
                if result["success"]:
                    st.success("Image uploaded successfully!")
                    analysis = result.get("analysis", {})
                    if analysis:
                        st.caption("Detected metadata")
                        st.write(
                            {
                                "category": analysis.get("category"),
                                "details": analysis.get("details"),
                                "location": analysis.get("location"),
                                "latitude": analysis.get("latitude"),
                                "longitude": analysis.get("longitude"),
                            }
                        )
                        if analysis.get("ollama_error"):
                            st.info(
                                "Ollama analysis unavailable for this upload. "
                                f"Reason: {analysis.get('ollama_error')}"
                            )
                    st.rerun()
                else:
                    st.error(f"Error uploading image: {result['message']}")

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