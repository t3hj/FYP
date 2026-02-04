"""
Utility functions for Local Lens application.
Includes GPS extraction, geocoding, file handling, and badge generators.
"""
import uuid
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim

from config import (
    UPLOAD_PATH, MAX_IMAGE_SIZE_MB, CATEGORY_ICONS,
    PRIORITY_COLORS, STATUS_COLORS
)


def save_uploaded_file(uploaded_file):
    """Save uploaded file with unique filename to prevent conflicts
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        str: Path to saved file
    """
    # Create uploads directory if it doesn't exist (absolute path)
    UPLOAD_PATH.mkdir(exist_ok=True)
    
    # Generate unique filename using UUID
    file_extension = Path(uploaded_file.name).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_PATH / unique_filename
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return str(file_path)


def validate_inputs(uploaded_file, location_description):
    """Validate user inputs before submission
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        location_description (str): Location text input
        
    Returns:
        list: List of error messages (empty if valid)
    """
    errors = []
    
    if uploaded_file is None:
        errors.append("Please upload an image of the issue.")
    elif uploaded_file.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        errors.append(f"Image size exceeds {MAX_IMAGE_SIZE_MB}MB limit.")
    
    if not location_description or not location_description.strip():
        errors.append("Please provide a location description.")
    elif len(location_description.strip()) < 5:
        errors.append("Location description must be at least 5 characters.")
    
    return errors


def extract_gps_from_image(image_path):
    """Extract GPS coordinates from image EXIF data
    
    Args:
        image_path: Path to the image file
        
    Returns:
        tuple: (latitude, longitude) or (None, None) if no GPS data
    """
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if not exif_data:
            return None, None
        
        gps_info = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for gps_tag_id, gps_value in value.items():
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_info[gps_tag] = gps_value
        
        if not gps_info:
            return None, None
        
        # Extract latitude
        lat = gps_info.get("GPSLatitude")
        lat_ref = gps_info.get("GPSLatitudeRef")
        
        # Extract longitude
        lon = gps_info.get("GPSLongitude")
        lon_ref = gps_info.get("GPSLongitudeRef")
        
        if lat and lon and lat_ref and lon_ref:
            # Convert to decimal degrees
            lat_decimal = float(lat[0]) + float(lat[1])/60 + float(lat[2])/3600
            lon_decimal = float(lon[0]) + float(lon[1])/60 + float(lon[2])/3600
            
            if lat_ref == "S":
                lat_decimal = -lat_decimal
            if lon_ref == "W":
                lon_decimal = -lon_decimal
            
            return lat_decimal, lon_decimal
        
        return None, None
    
    except Exception as e:
        print(f"Error extracting GPS: {e}")
        return None, None


def get_address_from_coordinates(lat, lon):
    """Convert GPS coordinates to human-readable address
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        
    Returns:
        str: Human-readable address or None
    """
    try:
        geolocator = Nominatim(user_agent="local_lens_app")
        location = geolocator.reverse(f"{lat}, {lon}", exactly_one=True)
        
        if location:
            return location.address
        return None
    
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None


def get_priority_badge(priority):
    """Return HTML for a styled priority badge"""
    bg, text = PRIORITY_COLORS.get(priority, ('#6c757d', 'white'))
    return f'<span style="background-color: {bg}; color: {text}; padding: 3px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: 500;">{priority}</span>'


def get_status_badge(status):
    """Return HTML for a styled status badge"""
    bg, text = STATUS_COLORS.get(status, ('#6c757d', 'white'))
    return f'<span style="background-color: {bg}; color: {text}; padding: 3px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: 500;">{status}</span>'


def get_community_urgency_badge(similar_count, urgency_level):
    """Return HTML for a community urgency badge
    
    Displays how many community members have reported similar issues,
    helping council prioritize high-impact problems.
    
    Args:
        similar_count (int): Number of similar reports
        urgency_level (str): Urgency level (Critical, High, Elevated, Normal)
        
    Returns:
        str: HTML badge string
    """
    if similar_count == 0:
        return ""
    
    # Colors for different urgency levels
    urgency_colors = {
        'Critical': ('#dc3545', 'white', '🔥🔥'),
        'High': ('#fd7e14', 'white', '🔥'),
        'Elevated': ('#ffc107', 'black', '⚠️'),
        'Normal': ('#6c757d', 'white', '')
    }
    
    bg, text, icon = urgency_colors.get(urgency_level, ('#6c757d', 'white', ''))
    
    report_text = "report" if similar_count == 1 else "reports"
    
    return f'''<span style="background-color: {bg}; color: {text}; padding: 4px 12px; 
               border-radius: 12px; font-size: 0.85rem; font-weight: 600; 
               display: inline-flex; align-items: center; gap: 4px;
               box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
               {icon} +{similar_count} similar {report_text}
               </span>'''


def get_urgency_indicator(similar_count):
    """Return a simple urgency indicator for compact displays
    
    Args:
        similar_count (int): Number of similar reports
        
    Returns:
        str: Emoji indicator string
    """
    if similar_count >= 5:
        return "🔥🔥🔥"  # Critical - many reports
    elif similar_count >= 3:
        return "🔥🔥"    # High urgency
    elif similar_count >= 1:
        return "🔥"      # Elevated
    return ""            # Normal


def get_category_icon(category):
    """Return emoji icon for a category"""
    return CATEGORY_ICONS.get(category, '📌')
