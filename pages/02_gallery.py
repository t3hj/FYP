import streamlit as st
from src.services.upload_service import UploadService

def gallery_page():
    st.title("Image Gallery")
    images = UploadService().list_uploaded_images()
    
    if images:
        st.dataframe(images, use_container_width=True)
    else:
        st.write("No images found in the gallery.")

if __name__ == "__main__":
    gallery_page()