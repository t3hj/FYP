"""
Submit Report tab for Local Lens application.
"""
import streamlit as st
from PIL import Image

from config import ISSUE_CATEGORIES, PRIORITY_OPTIONS, SUPPORTED_IMAGE_TYPES, MAX_IMAGE_SIZE_MB
from database import insert_report, get_recent_reports
from ai_analysis import analyze_image_with_ai
from utils import save_uploaded_file, validate_inputs, extract_gps_from_image, get_address_from_coordinates
from styles import get_tab_header, TAB_GRADIENTS


def submit_report_tab():
    """Tab 1: Submit new report with AI features"""
    
    # Header card
    st.markdown(get_tab_header(
        "📝 Submit a New Report",
        "Upload an image and let AI help categorize your report",
        TAB_GRADIENTS['submit']
    ), unsafe_allow_html=True)
    
    with st.expander("ℹ️ How to use this app", expanded=False):
        st.markdown("""
        ### Quick Guide
        
        | Step | Action | AI Help |
        |------|--------|---------|
        | 1️⃣ | Upload an image | 🤖 Auto-detects category |
        | 2️⃣ | Review details | 📍 Auto-fills location from GPS |
        | 3️⃣ | Add description | ✏️ Optional extra details |
        | 4️⃣ | Submit | 🎉 Get unique report ID |
        
        ---
        
        **🤖 AI Features Available:**
        - **Ollama LLaVA** - 100% free, unlimited, runs locally
        - **Smart Fallback** - Basic image analysis always works
        - **GPS Extraction** - Auto-detects location from photos
        
        > 💡 **Tip:** For best results, install [Ollama](https://ollama.ai) and run `ollama pull llava`
        """)
    
    st.markdown("---")
    
    # Create session state for AI suggestions
    if 'extracted_location' not in st.session_state:
        st.session_state.extracted_location = ""
    if 'suggested_category' not in st.session_state:
        st.session_state.suggested_category = None
    if 'last_analyzed_file' not in st.session_state:
        st.session_state.last_analyzed_file = None
    
    st.subheader("📝 Submit New Report")
    
    # File uploader outside form for immediate AI analysis
    uploaded_file = st.file_uploader(
        "Upload an image of the issue * 🤖",
        type=SUPPORTED_IMAGE_TYPES,
        help=f"Supported formats: {', '.join(SUPPORTED_IMAGE_TYPES).upper()}. Max size: {MAX_IMAGE_SIZE_MB}MB. AI will auto-detect location and category!",
        key="image_uploader"
    )
    
    # When a new file is uploaded, analyze it with AI
    if uploaded_file is not None and uploaded_file != st.session_state.last_analyzed_file:
        st.session_state.last_analyzed_file = uploaded_file
        
        with st.spinner("🤖 AI analyzing image..."):
            # Save temporarily to extract GPS
            temp_path = save_uploaded_file(uploaded_file)
            
            # Try to extract GPS coordinates
            lat, lon = extract_gps_from_image(temp_path)
            
            if lat and lon:
                # Get address from coordinates
                address = get_address_from_coordinates(lat, lon)
                if address:
                    st.session_state.extracted_location = f"{address}\n(Coordinates: {lat:.6f}, {lon:.6f})"
                    st.success(f"📍 Location detected from image GPS data!")
                else:
                    st.session_state.extracted_location = f"Coordinates: {lat:.6f}, {lon:.6f}"
                    st.info("📍 GPS coordinates found, but couldn't get address.")
            else:
                st.session_state.extracted_location = ""
                st.info("📍 No GPS data in image. Please enter location manually.")
            
            # Try AI category detection
            suggested = analyze_image_with_ai(uploaded_file)
            if suggested:
                st.session_state.suggested_category = suggested
                st.success(f"🤖 AI suggests category: **{suggested}**")
            else:
                st.session_state.suggested_category = None
    
    # Display image preview
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 2])
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            uploaded_file.seek(0)  # Reset file pointer
    
    # Use form for better UX and single submission
    with st.form("report_form", clear_on_submit=True):
        st.write("### Report Details")
        
        # Category selection with AI suggestion
        default_category_index = 0
        if st.session_state.suggested_category and st.session_state.suggested_category in ISSUE_CATEGORIES:
            default_category_index = ISSUE_CATEGORIES.index(st.session_state.suggested_category)
        
        category = st.selectbox(
            "Issue Category *",
            options=ISSUE_CATEGORIES,
            index=default_category_index,
            help="Select the type of issue. AI may suggest a category based on the image."
        )
        
        # Location with GPS auto-fill
        location = st.text_area(
            "Location Description *",
            value=st.session_state.extracted_location,
            placeholder="e.g., Corner of Main St and Oak Ave, near the post office",
            help="Describe where the issue is located. GPS location will be auto-filled if available in the image."
        )
        
        # Priority selection
        priority = st.selectbox(
            "Priority Level",
            options=PRIORITY_OPTIONS,
            index=1,  # Default to "Medium"
            help="How urgent is this issue?"
        )
        
        # Additional details
        additional_details = st.text_area(
            "Additional Details (Optional)",
            placeholder="Any other relevant information about the issue...",
            help="Provide any extra details that might help address the issue."
        )
        
        # Submit button
        submitted = st.form_submit_button("📤 Submit Report", type="primary")
        
        if submitted:
            # Validate inputs
            errors = validate_inputs(uploaded_file, location)
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Save file with unique name
                file_path = save_uploaded_file(uploaded_file)
                
                # Insert into database
                report_id = insert_report(file_path, category, location, additional_details)
                
                if report_id:
                    st.success(f"✅ Report submitted successfully! Report ID: #{report_id}")
                    st.balloons()
                    
                    # Clear session state
                    st.session_state.extracted_location = ""
                    st.session_state.suggested_category = None
                    st.session_state.last_analyzed_file = None
                else:
                    st.error("❌ Failed to submit report. Please try again.")

    # Add section to view recent reports
    st.markdown("---")
    if st.checkbox("👀 View Recent Reports", help="Show the last 5 submitted reports"):
        recent_reports = get_recent_reports(5)
        
        if recent_reports:
            st.subheader("📋 Recent Reports")
            for report in recent_reports:
                report_id, image_path, cat, loc, details, timestamp, status, priority = report
                
                with st.expander(f"Report #{report_id} - {cat} ({status})"):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        try:
                            st.image(image_path, caption=f"Report #{report_id}", use_container_width=True)
                        except:
                            st.write("Image not available")
                    with col2:
                        st.write(f"**Category:** {cat}")
                        st.write(f"**Location:** {loc}")
                        st.write(f"**Priority:** {priority}")
                        st.write(f"**Status:** {status}")
                        st.write(f"**Submitted:** {timestamp}")
                        if details:
                            st.write(f"**Details:** {details}")
        else:
            st.info("No reports submitted yet.")
