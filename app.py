import streamlit as st
from PIL import Image
import sqlite3
import os
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Local Lens: Community Issue Reporter",
    page_icon="�",
    layout="wide"
)

def create_database():
    """Create SQLite database and reports table if they don't exist"""
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()
    
    # Create the reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_report(image_path, category, location):
    """Insert a new record into the reports table"""
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO reports (image_path, category, location)
            VALUES (?, ?, ?)
        ''', (image_path, category, location))
        
        conn.commit()
        report_id = cursor.lastrowid
        return report_id
    
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return None
    
    finally:
        conn.close()

def main():
    # Initialize database
    create_database()
    
    # Title
    st.title("📍 Local Lens: Community Issue Reporter")
    st.markdown("Report community issues in your local area")
    st.markdown("---")
    
    # File uploader for images
    uploaded_file = st.file_uploader(
        "Upload an image of the issue",
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
        help="Please upload a clear image showing the community issue"
    )
    
    # Text input for location description
    location_description = st.text_input(
        "Location Description",
        placeholder="e.g., Corner of Main St and Oak Ave, near the bus stop"
    )
    
    # Selectbox for category
    category = st.selectbox(
        "Issue Category",
        options=['Pothole', 'Broken Streetlight', 'Graffiti', 'Other']
    )
    
    # Additional description text area
    additional_details = st.text_area(
        "Additional Details (Optional)",
        placeholder="Provide any additional information about the issue..."
    )
    
    # Submit button
    if st.button("Submit Report", type="primary"):
        # Check if required fields are filled
        if uploaded_file is not None and location_description.strip():
            try:
                # Create uploads directory if it doesn't exist
                os.makedirs("uploads", exist_ok=True)
                
                # Save the image file
                image_path = os.path.join("uploads", uploaded_file.name)
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Insert report into database
                report_id = insert_report(image_path, category, location_description)
                
                if report_id:
                    st.success(f"✅ Report submitted successfully! Report ID: {report_id}")
                    st.markdown("---")
                    
                    # Display the submitted data
                    st.subheader("📋 Report Summary")
                    
                    # Create two columns for better layout
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.write("**Report ID:**", report_id)
                        st.write("**Location:**", location_description)
                        st.write("**Category:**", category)
                        st.write("**Image Path:**", image_path)
                        if additional_details.strip():
                            st.write("**Additional Details:**", additional_details)
                    
                    with col2:
                        # Display the uploaded image
                        image = Image.open(uploaded_file)
                        st.image(
                            image, 
                            caption="Uploaded Issue Image", 
                            use_column_width=True
                        )
                        
                        # Display image info
                        st.write("**Image Details:**")
                        st.write(f"- Filename: {uploaded_file.name}")
                        st.write(f"- File size: {uploaded_file.size} bytes")
                        st.write(f"- Image format: {image.format}")
                        st.write(f"- Image size: {image.size[0]} x {image.size[1]} pixels")
                else:
                    st.error("❌ Failed to save report to database.")
            
            except Exception as e:
                st.error(f"❌ Error saving report: {str(e)}")
        
        else:
            # Show error message if required fields are missing
            st.error("❌ Please upload an image and provide a location description before submitting.")
            
            if uploaded_file is None:
                st.warning("📸 Image is required")
            if not location_description.strip():
                st.warning("📍 Location description is required")

if __name__ == "__main__":
    main()
