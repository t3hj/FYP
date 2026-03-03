import streamlit as st
from src.services.upload_service import UploadService
from src.services.backup_service import BackupService

def main():
    st.title("Image Upload and Management Application")
    upload_service = UploadService()
    backup_service = BackupService()

    # Upload Image Section
    st.header("Upload Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        result = upload_service.upload_image(uploaded_file)

        if result['success']:
            st.success("Image uploaded successfully!")
        else:
            st.error(f"Error uploading image: {result['message']}")

    st.header("Stored Reports")
    reports = upload_service.list_uploaded_images()
    if reports:
        st.dataframe(reports, use_container_width=True)
    else:
        st.info("No reports found yet.")

    # Backup Section
    st.header("Backup Management")
    if st.button("Run Backup"):
        backup_result = backup_service.run_backup()

        if backup_result['success']:
            st.success("Backup completed successfully!")
        else:
            st.error(f"Error during backup: {backup_result['message']}")

if __name__ == "__main__":
    main()