import streamlit as st
from src.services.upload_service import UploadService
from src.utils.validators import validate_image_format

def main():
    st.title("Image Upload")
    st.write("Upload your images here.")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        if validate_image_format(uploaded_file):
            upload_service = UploadService()
            result = upload_service.upload_image(uploaded_file)

            if result['success']:
                st.success("Image uploaded successfully!")
            else:
                st.error("Error uploading image: " + result['message'])
        else:
            st.error("Invalid file format. Please upload a JPG or PNG image.")

if __name__ == "__main__":
    main()