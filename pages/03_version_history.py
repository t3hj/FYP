# Version History Page for Streamlit Application

import streamlit as st
from src.services.upload_service import UploadService

def display_version_history():
    st.title("Version History")
    version_history = UploadService().list_uploaded_images()
    
    if version_history:
        st.write("### Uploaded Images Version History")
        for version in version_history:
            st.write(f"**Report ID:** {version.get('id')}")
            st.write(f"**Filename:** {version.get('filename')}")
            st.write(f"**Version:** {version.get('version', 1)}")
            st.write(f"**Uploaded On:** {version.get('upload_date')}")
            if version.get('cloud_storage_url'):
                st.write(f"**Cloud URL:** {version.get('cloud_storage_url')}")
            st.write("---")
    else:
        st.write("No version history available.")

if __name__ == "__main__":
    display_version_history()