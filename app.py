import streamlit as st
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import sqlite3
import os
from datetime import datetime
import uuid
from pathlib import Path
import pandas as pd
from geopy.geocoders import Nominatim
try:
    import google.genai as genai
except ImportError:
    import google.generativeai as genai
import base64
import io
import folium
from streamlit_folium import st_folium
import requests
from io import BytesIO

# Set page configuration
st.set_page_config(
    page_title="Local Lens: Community Issue Reporter",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for improved aesthetics
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(90deg, #1e88e5, #43a047);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
    }
    
    /* Card-like containers / Expander styling */
    .stExpander {
        background-color: #f8f9fa;
        border-radius: 10px;
        border: 2px solid #1e88e5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stExpander summary {
        font-weight: 600 !important;
        color: #1e88e5 !important;
    }
    
    .stExpander summary:hover {
        background-color: #e3f2fd;
    }
    
    /* Expander content text visibility */
    .stExpander [data-testid="stExpanderDetails"] {
        color: #333 !important;
    }
    
    .stExpander [data-testid="stExpanderDetails"] p,
    .stExpander [data-testid="stExpanderDetails"] li,
    .stExpander [data-testid="stExpanderDetails"] td,
    .stExpander [data-testid="stExpanderDetails"] th {
        color: #333 !important;
    }
    
    .stExpander [data-testid="stExpanderDetails"] strong {
        color: #1e88e5 !important;
    }
    
    /* Table styling in expanders */
    .stExpander table {
        color: #333 !important;
    }
    
    .stExpander th {
        background-color: #e3f2fd !important;
        color: #1565c0 !important;
        font-weight: 600 !important;
    }
    
    .stExpander td {
        color: #333 !important;
    }
    
    /* Metric cards styling */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
    }
    
    [data-testid="metric-container"] label {
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar text visibility */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #333 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown p {
        color: #333 !important;
    }
    
    /* Progress bar text in sidebar */
    [data-testid="stSidebar"] [data-testid="stProgressBar"] span {
        color: #333 !important;
        font-weight: 500 !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        color: #1e88e5 !important;
        border: 2px solid #1e88e5;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #1e88e5, #43a047) !important;
        color: white !important;
        border: 2px solid transparent !important;
    }
    
    /* Button styling - Primary buttons */
    .stButton > button {
        background: linear-gradient(90deg, #1e88e5, #2196f3) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 2px 6px rgba(30, 136, 229, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #1565c0, #1e88e5) !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.5);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(90deg, #43a047, #66bb6a) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 600 !important;
        box-shadow: 0 2px 6px rgba(67, 160, 71, 0.3);
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(90deg, #2e7d32, #43a047) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(67, 160, 71, 0.5);
    }
    
    /* Form submit button */
    .stFormSubmitButton > button {
        background: linear-gradient(90deg, #7c4dff, #651fff) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px;
        padding: 0.75rem 2.5rem;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 3px 8px rgba(124, 77, 255, 0.4);
        width: 100%;
    }
    
    .stFormSubmitButton > button:hover {
        background: linear-gradient(90deg, #651fff, #536dfe) !important;
        color: white !important;
        box-shadow: 0 5px 15px rgba(124, 77, 255, 0.5);
        transform: translateY(-2px);
    }
    
    /* Form styling */
    .stForm {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #1e88e5;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background-color: #f8f9fa;
        border: 2px dashed #1e88e5;
        border-radius: 10px;
        padding: 20px;
    }
    
    /* Success/Info/Warning boxes */
    .stSuccess, .stInfo, .stWarning {
        border-radius: 10px;
    }
    
    /* DataFrame styling */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Image display */
    .stImage {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Selectbox styling */
    .stSelectbox [data-baseweb="select"] {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    
    .stSelectbox [data-baseweb="select"]:hover {
        border-color: #1e88e5;
    }
    
    /* Selectbox label styling */
    .stSelectbox label, .stTextInput label, .stTextArea label, .stDateInput label {
        font-weight: 600 !important;
        color: #333 !important;
        font-size: 0.95rem !important;
    }
    
    /* Text input styling */
    .stTextInput input, .stTextArea textarea {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        font-size: 1rem;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #1e88e5;
        box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.15);
    }
    
    /* Alert boxes styling */
    .stSuccess {
        background-color: #d4edda !important;
        border-left: 4px solid #28a745 !important;
        border-radius: 8px;
    }
    
    .stInfo {
        background-color: #d1ecf1 !important;
        border-left: 4px solid #17a2b8 !important;
        border-radius: 8px;
    }
    
    .stWarning {
        background-color: #fff3cd !important;
        border-left: 4px solid #ffc107 !important;
        border-radius: 8px;
    }
    
    .stError {
        background-color: #f8d7da !important;
        border-left: 4px solid #dc3545 !important;
        border-radius: 8px;
    }
    
    /* Priority badges */
    .priority-critical { background-color: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; }
    .priority-high { background-color: #fd7e14; color: white; padding: 2px 8px; border-radius: 4px; }
    .priority-medium { background-color: #ffc107; color: black; padding: 2px 8px; border-radius: 4px; }
    .priority-low { background-color: #28a745; color: white; padding: 2px 8px; border-radius: 4px; }
    
    /* Status badges */
    .status-reported { background-color: #6c757d; color: white; padding: 2px 8px; border-radius: 4px; }
    .status-in-progress { background-color: #17a2b8; color: white; padding: 2px 8px; border-radius: 4px; }
    .status-resolved { background-color: #28a745; color: white; padding: 2px 8px; border-radius: 4px; }
    .status-closed { background-color: #343a40; color: white; padding: 2px 8px; border-radius: 4px; }
    
    /* Divider styling */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
        margin: 2rem 0;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 20px;
        color: #6c757d;
        font-size: 0.9rem;
    }
    
    /* Report cards */
    .report-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 4px solid #1e88e5;
    }
    
    .report-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Global text visibility - ensure dark text on light backgrounds */
    .main .stMarkdown p, .main .stMarkdown li, .main .stMarkdown td {
        color: #333 !important;
    }
    
    .main .stMarkdown h1, .main .stMarkdown h2, .main .stMarkdown h3, 
    .main .stMarkdown h4, .main .stMarkdown h5 {
        color: #1e88e5 !important;
    }
    
    .main .stMarkdown strong {
        color: #1565c0 !important;
    }
    
    .main .stMarkdown code {
        background-color: #e3f2fd !important;
        color: #1565c0 !important;
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    /* Blockquote styling */
    .main .stMarkdown blockquote {
        border-left: 4px solid #1e88e5;
        background-color: #f8f9fa;
        padding: 10px 15px;
        margin: 10px 0;
        color: #333 !important;
    }
    
    /* Link styling */
    .main .stMarkdown a {
        color: #1e88e5 !important;
        text-decoration: underline;
    }
    
    .main .stMarkdown a:hover {
        color: #1565c0 !important;
    }
    
    /* DataFrame/Table text */
    .stDataFrame, .stDataFrame td, .stDataFrame th {
        color: #333 !important;
    }
    
    /* Ensure all regular text is visible */
    .element-container p, .element-container span {
        color: #333 !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions for styled badges
def get_priority_badge(priority):
    """Return HTML for a styled priority badge"""
    colors = {
        'Critical': ('#dc3545', 'white'),
        'High': ('#fd7e14', 'white'),
        'Medium': ('#ffc107', 'black'),
        'Low': ('#28a745', 'white')
    }
    bg, text = colors.get(priority, ('#6c757d', 'white'))
    return f'<span style="background-color: {bg}; color: {text}; padding: 3px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: 500;">{priority}</span>'

def get_status_badge(status):
    """Return HTML for a styled status badge"""
    colors = {
        'Reported': ('#6c757d', 'white'),
        'In Progress': ('#17a2b8', 'white'),
        'Resolved': ('#28a745', 'white'),
        'Closed': ('#343a40', 'white')
    }
    bg, text = colors.get(status, ('#6c757d', 'white'))
    return f'<span style="background-color: {bg}; color: {text}; padding: 3px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: 500;">{status}</span>'

def get_category_icon(category):
    """Return emoji icon for a category"""
    icons = {
        'Pothole': '🕳️',
        'Broken Streetlight': '💡',
        'Graffiti': '🎨',
        'Litter': '🗑️',
        'Damaged Road Sign': '🚧',
        'Other': '📌'
    }
    return icons.get(category, '📌')

# Constants
DATABASE_NAME = "reports.db"
UPLOAD_DIR = "uploads"
SUPPORTED_IMAGE_TYPES = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'heic']
ISSUE_CATEGORIES = ['Pothole', 'Broken Streetlight', 'Graffiti', 'Litter', 'Damaged Road Sign', 'Other']
STATUS_OPTIONS = ['Reported', 'In Progress', 'Resolved', 'Closed']
PRIORITY_OPTIONS = ['Low', 'Medium', 'High', 'Critical']
MAX_IMAGE_SIZE_MB = 10

# Resolve base paths to avoid CWD issues when launching Streamlit
BASE_DIR = Path(__file__).parent.resolve()
DATABASE_PATH = BASE_DIR / DATABASE_NAME
UPLOAD_PATH = BASE_DIR / UPLOAD_DIR

def create_database():
    """Create SQLite database and reports table if they don't exist"""
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        
        # Create the reports table with enhanced schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                additional_details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Reported',
                priority TEXT DEFAULT 'Medium'
            )
        ''')
        
        conn.commit()
        
        # Check if we need to migrate the schema (add missing columns)
        cursor.execute("PRAGMA table_info(reports)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns if they don't exist
        if 'additional_details' not in columns:
            cursor.execute('ALTER TABLE reports ADD COLUMN additional_details TEXT')
            conn.commit()
        
        if 'status' not in columns:
            cursor.execute("ALTER TABLE reports ADD COLUMN status TEXT DEFAULT 'Reported'")
            conn.commit()
        
        if 'priority' not in columns:
            cursor.execute("ALTER TABLE reports ADD COLUMN priority TEXT DEFAULT 'Medium'")
            conn.commit()
        
    except sqlite3.Error as e:
        st.error(f"Database creation error: {e}")
    finally:
        if conn:
            conn.close()

def insert_report(image_path, category, location, additional_details=None):
    """Insert a new record into the reports table
    
    Args:
        image_path (str): Path to the saved image file
        category (str): Issue category
        location (str): Location description
        additional_details (str, optional): Additional information about the issue
        
    Returns:
        int: Report ID if successful, None otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reports (image_path, category, location, additional_details)
            VALUES (?, ?, ?, ?)
        ''', (image_path, category, location, additional_details))
        
        conn.commit()
        report_id = cursor.lastrowid
        return report_id
    
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return None
    
    finally:
        if conn:
            conn.close()

def get_all_reports():
    """Retrieve all reports from the database
    
    Returns:
        list: List of all report records
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reports ORDER BY timestamp DESC')
        reports = cursor.fetchall()
        return reports
    
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return []
    
    finally:
        if conn:
            conn.close()

def get_recent_reports(limit: int = 5):
    """Retrieve the most recent reports limited by count
    
    Args:
        limit (int): Number of most recent reports to return
    Returns:
        list: List of recent report records
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reports ORDER BY timestamp DESC LIMIT ?', (limit,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_filtered_reports(category=None, status=None, date_from=None, date_to=None, location=None):
    """Get reports with optional filters
    
    Args:
        category (str, optional): Filter by category
        status (str, optional): Filter by status
        date_from (datetime, optional): Filter by start date
        date_to (datetime, optional): Filter by end date
        location (str, optional): Filter by location (partial match)
    
    Returns:
        list: Filtered report records
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        
        query = 'SELECT * FROM reports WHERE 1=1'
        params = []
        
        if category and category != 'All':
            query += ' AND category = ?'
            params.append(category)
        
        if status and status != 'All':
            query += ' AND status = ?'
            params.append(status)
        
        if date_from:
            query += ' AND date(timestamp) >= date(?)'
            params.append(date_from.strftime('%Y-%m-%d'))
        
        if date_to:
            query += ' AND date(timestamp) <= date(?)'
            params.append(date_to.strftime('%Y-%m-%d'))
        
        if location:
            query += ' AND location LIKE ?'
            params.append(f'%{location}%')
        
        query += ' ORDER BY timestamp DESC'
        
        cursor.execute(query, params)
        return cursor.fetchall()
    
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return []
    
    finally:
        if conn:
            conn.close()

def update_report_status(report_id, status):
    """Update the status of a report
    
    Args:
        report_id (int): ID of the report to update
        status (str): New status value
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute('UPDATE reports SET status = ? WHERE id = ?', (status, report_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_report_priority(report_id, priority):
    """Update the priority of a report
    
    Args:
        report_id (int): ID of the report to update
        priority (str): New priority value
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute('UPDATE reports SET priority = ? WHERE id = ?', (priority, report_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_report(report_id, category, location, additional_details):
    """Update report details
    
    Args:
        report_id (int): ID of the report to update
        category (str): New category
        location (str): New location
        additional_details (str): New additional details
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE reports 
            SET category = ?, location = ?, additional_details = ? 
            WHERE id = ?
        ''', (category, location, additional_details, report_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_report(report_id):
    """Delete a report from the database
    
    Args:
        report_id (int): ID of the report to delete
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute('DELETE FROM reports WHERE id = ?', (report_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_report_by_id(report_id):
    """Get a single report by ID
    
    Args:
        report_id (int): ID of the report
    
    Returns:
        tuple: Report record or None
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def export_reports_to_csv():
    """Export all reports to CSV format
    
    Returns:
        str: CSV data as string
    """
    reports = get_all_reports()
    if not reports:
        return None
    
    # Create DataFrame
    df = pd.DataFrame(reports, columns=['ID', 'Image Path', 'Category', 'Location', 
                                        'Additional Details', 'Timestamp', 'Status', 'Priority'])
    return df.to_csv(index=False)

def get_report_statistics():
    """Get statistics about submitted reports
    
    Returns:
        dict: Dictionary with statistics (total_count, category_counts)
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Total count
        cursor.execute('SELECT COUNT(*) FROM reports')
        total_count = cursor.fetchone()[0]
        
        # Count by category
        cursor.execute('SELECT category, COUNT(*) as count FROM reports GROUP BY category')
        category_counts = dict(cursor.fetchall())
        
        return {
            'total_count': total_count,
            'category_counts': category_counts
        }
    
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return {'total_count': 0, 'category_counts': {}}
    
    finally:
        if conn:
            conn.close()

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
        errors.append("📸 Image is required")
    elif uploaded_file.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        errors.append(f"📸 Image size must be less than {MAX_IMAGE_SIZE_MB}MB")
    
    if not location_description or not location_description.strip():
        errors.append("📍 Location description is required")
    elif len(location_description.strip()) < 5:
        errors.append("📍 Location description is too short (minimum 5 characters)")
    
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
        
        # Get GPS info
        gps_info = {}
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == 'GPSInfo':
                for gps_tag in value:
                    gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                    gps_info[gps_tag_name] = value[gps_tag]
        
        if not gps_info:
            return None, None
        
        # Convert GPS coordinates to decimal degrees
        def convert_to_degrees(value):
            d, m, s = value
            return d + (m / 60.0) + (s / 3600.0)
        
        lat = convert_to_degrees(gps_info.get('GPSLatitude', [0, 0, 0]))
        lon = convert_to_degrees(gps_info.get('GPSLongitude', [0, 0, 0]))
        
        # Check for North/South and East/West
        if gps_info.get('GPSLatitudeRef') == 'S':
            lat = -lat
        if gps_info.get('GPSLongitudeRef') == 'W':
            lon = -lon
        
        return lat, lon
    
    except Exception as e:
        st.warning(f"Could not extract GPS data: {str(e)}")
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
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
        
        if location:
            return location.address
        return None
    
    except Exception as e:
        st.warning(f"Could not get address: {str(e)}")
        return None

def analyze_image_with_ai(uploaded_file):
    """Use AI to analyze image and suggest category - tries multiple free options
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        str: Suggested category or None
    """
    # Try Ollama first (local, free, unlimited)
    category = try_ollama_analysis(uploaded_file)
    if category:
        return category
    
    # Fallback to simple image analysis (always works, no external deps)
    category = try_simple_image_analysis(uploaded_file)
    if category:
        return category
    
    return None

def try_ollama_analysis(uploaded_file):
    """Try Ollama LLaVA for local AI analysis (100% free, no limits)"""
    try:
        # Check if Ollama is running locally
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code != 200:
            return None
        
        # Check if llava model is available
        models = response.json().get("models", [])
        if not any("llava" in m.get("name", "").lower() for m in models):
            return None
        
        # Read image
        uploaded_file.seek(0)
        image_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        
        # Convert to base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Create prompt
        categories_str = ", ".join(ISSUE_CATEGORIES)
        prompt = f"""Analyze this image and determine which community issue category it best fits.

Available categories: {categories_str}

Look for:
- Pothole: Damaged road surface, holes in pavement
- Broken Streetlight: Non-functioning street lamps, damaged light fixtures
- Graffiti: Spray paint, unauthorized markings on walls/surfaces
- Litter: Trash, garbage on streets or public areas
- Damaged Road Sign: Bent, broken, or missing traffic signs
- Other: Any other community issues not listed above

Respond with ONLY the category name that best matches, nothing else."""

        # Call Ollama API with longer timeout (model may need to load)
        ollama_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llava",
                "prompt": prompt,
                "images": [image_b64],
                "stream": False
            },
            timeout=120  # Increased timeout for model loading
        )
        
        if ollama_response.status_code == 200:
            result = ollama_response.json()
            suggested_category = result.get("response", "").strip()
            
            # Validate the response
            if suggested_category in ISSUE_CATEGORIES:
                return suggested_category
            
            # Try to match partial responses
            for category in ISSUE_CATEGORIES:
                if category.lower() in suggested_category.lower():
                    return category
        
        return None
    
    except Exception:
        return None

def try_simple_image_analysis(uploaded_file):
    """Simple image analysis using color and texture patterns (always works)
    
    This is a basic heuristic classifier that analyzes image characteristics
    to suggest a category. It's not as accurate as AI but works instantly.
    """
    try:
        from PIL import Image
        import io
        from collections import Counter
        
        # Read image
        uploaded_file.seek(0)
        image = Image.open(io.BytesIO(uploaded_file.read()))
        uploaded_file.seek(0)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize for faster processing
        image = image.resize((100, 100))
        pixels = list(image.getdata())
        
        # Analyze color distribution
        total_pixels = len(pixels)
        
        # Count color categories
        dark_count = 0  # For potholes (dark areas)
        bright_count = 0  # For streetlights
        colorful_count = 0  # For graffiti (vibrant colors)
        brown_green_count = 0  # For litter in outdoor settings
        red_yellow_count = 0  # For road signs
        gray_count = 0  # For roads/pavement
        
        for r, g, b in pixels:
            brightness = (r + g + b) / 3
            saturation = max(r, g, b) - min(r, g, b)
            
            # Dark pixels (potential pothole)
            if brightness < 60:
                dark_count += 1
            
            # Very bright pixels (potential streetlight)
            if brightness > 200:
                bright_count += 1
            
            # Colorful/vibrant (potential graffiti)
            if saturation > 100 and brightness > 50 and brightness < 200:
                colorful_count += 1
            
            # Brown/green tones (outdoor litter setting)
            if (g > r and g > b) or (r > 100 and g > 70 and b < 100):
                brown_green_count += 1
            
            # Red/yellow (road signs)
            if (r > 180 and g < 100 and b < 100) or (r > 180 and g > 150 and b < 100):
                red_yellow_count += 1
            
            # Gray (pavement/road)
            if saturation < 30 and 60 < brightness < 180:
                gray_count += 1
        
        # Calculate percentages
        dark_pct = dark_count / total_pixels
        bright_pct = bright_count / total_pixels
        colorful_pct = colorful_count / total_pixels
        red_yellow_pct = red_yellow_count / total_pixels
        gray_pct = gray_count / total_pixels
        
        # Decision logic based on color analysis
        scores = {
            'Pothole': dark_pct * 0.5 + gray_pct * 0.3,
            'Broken Streetlight': bright_pct * 0.4 + dark_pct * 0.2,
            'Graffiti': colorful_pct * 0.6,
            'Litter': brown_green_count / total_pixels * 0.3,
            'Damaged Road Sign': red_yellow_pct * 0.5,
            'Other': 0.1  # Default low score
        }
        
        # Get best match
        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]
        
        # Only return if we have reasonable confidence
        if best_score > 0.15:
            return best_category
        
        return 'Other'
    
    except Exception:
        return None

def display_sidebar():
    """Display sidebar with app information and statistics"""
    with st.sidebar:
        # Logo/Brand area
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="font-size: 2.5rem; margin: 0;">📍</h1>
            <h2 style="background: linear-gradient(90deg, #1e88e5, #43a047); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;">Local Lens</h2>
            <p style="color: #6c757d; font-size: 0.85rem;">Community Issue Reporter</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.header("📊 Dashboard")
        
        # Get statistics
        stats = get_report_statistics()
        
        # Display total reports with styled metric
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📋 Total", stats['total_count'])
        with col2:
            # Count resolved
            resolved = stats['category_counts'].get('Resolved', 0) if stats['category_counts'] else 0
            st.metric("✅ Active", stats['total_count'])
        
        st.markdown("---")
        
        # Display reports by category with progress bars
        if stats['category_counts']:
            st.subheader("📈 Reports by Category")
            total = stats['total_count'] if stats['total_count'] > 0 else 1
            
            # Category icons mapping
            category_icons = {
                'Pothole': '🕳️',
                'Broken Streetlight': '💡',
                'Graffiti': '🎨',
                'Litter': '🗑️',
                'Damaged Road Sign': '🚧',
                'Other': '📌'
            }
            
            for category, count in sorted(stats['category_counts'].items(), key=lambda x: x[1], reverse=True):
                icon = category_icons.get(category, '📌')
                progress = count / total
                st.markdown(f"**{icon} {category}**")
                st.progress(progress, text=f"{count} reports")
        
        st.markdown("---")
        
        # Quick tips
        with st.expander("💡 Quick Tips"):
            st.markdown("""
            - 📸 Take clear photos in good lighting
            - 📍 Enable GPS on your phone for auto-location
            - 📝 Add detailed descriptions
            - 🗺️ Check the map for nearby reports
            """)
        
        # AI Status indicator
        st.markdown("---")
        st.subheader("🤖 AI Status")
        
        # Check Ollama status
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if any("llava" in m.get("name", "").lower() for m in models):
                    st.success("✅ Ollama LLaVA Ready")
                else:
                    st.warning("⚠️ Ollama running (no LLaVA)")
            else:
                st.info("ℹ️ Using basic analysis")
        except:
            st.info("ℹ️ Using basic analysis")
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #6c757d; font-size: 0.8rem;">
            <p>Local Lens v2.0</p>
            <p>Made with ❤️ for communities</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Initialize database
    create_database()
    
    # Display sidebar
    display_sidebar()
    
    # Main title and description with hero section
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">📍 Local Lens</h1>
        <p style="font-size: 1.2rem; color: #6c757d; margin-bottom: 1rem;">
            Community Issue Reporter
        </p>
        <p style="color: #495057;">
            Help improve your neighborhood by reporting local issues. 
            Our AI-powered system makes it quick and easy!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Submit Report", 
        "📊 View & Filter", 
        "⚙️ Manage", 
        "🗺️ Map View", 
        "📥 Export"
    ])
    
    # ===== TAB 1: SUBMIT REPORT =====
    with tab1:
        submit_report_tab()
    
    # ===== TAB 2: VIEW & FILTER REPORTS =====
    with tab2:
        view_and_filter_tab()
    
    # ===== TAB 3: MANAGE REPORTS =====
    with tab3:
        manage_reports_tab()
    
    # ===== TAB 4: MAP VIEW =====
    with tab4:
        map_view_tab()
    
    # ===== TAB 5: EXPORT DATA =====
    with tab5:
        export_data_tab()

def submit_report_tab():
    """Tab 1: Submit new report with AI features"""
    
    # Header card
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0; color: white;">📝 Submit a New Report</h2>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">Upload an image and let AI help categorize your report</p>
    </div>
    """, unsafe_allow_html=True)
    
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
            
            # Extract GPS coordinates
            lat, lon = extract_gps_from_image(temp_path)
            
            if lat and lon:
                st.success(f"📍 GPS coordinates found: {lat:.6f}, {lon:.6f}")
                
                # Get address from coordinates
                address = get_address_from_coordinates(lat, lon)
                if address:
                    st.session_state.extracted_location = address
                    st.success(f"🗺️ Location detected: {address}")
                else:
                    st.session_state.extracted_location = f"Coordinates: {lat:.6f}, {lon:.6f}"
                    st.info(f"📌 Using coordinates: {lat:.6f}, {lon:.6f}")
            else:
                st.info("📍 No GPS data found in image. Please enter location manually.")
                st.session_state.extracted_location = ""
            
            # Analyze image for category suggestion
            suggested = analyze_image_with_ai(uploaded_file)
            if suggested:
                st.session_state.suggested_category = suggested
                st.success(f"🤖 AI suggests category: **{suggested}**")
            else:
                st.info("🤖 AI category detection unavailable. Please select manually.")
                st.session_state.suggested_category = None
    
    # Use form for better UX and single submission
    with st.form("report_form", clear_on_submit=True):
        # Two columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            # Text input for location description - pre-filled if GPS found
            default_location = st.session_state.extracted_location if st.session_state.extracted_location else ""
            location_description = st.text_input(
                "Location Description *",
                value=default_location,
                placeholder="e.g., Corner of Main St and Oak Ave, near the bus stop",
                help="Auto-filled from GPS data if available. You can edit this."
            )
        
        with col2:
            # Selectbox for category - default to AI suggestion if available
            default_index = 0
            if st.session_state.suggested_category and st.session_state.suggested_category in ISSUE_CATEGORIES:
                default_index = ISSUE_CATEGORIES.index(st.session_state.suggested_category)
            
            category = st.selectbox(
                "Issue Category * 🤖",
                options=ISSUE_CATEGORIES,
                index=default_index,
                help="AI-suggested category selected by default. You can change this."
            )
        
        # Additional description text area
        additional_details = st.text_area(
            "Additional Details (Optional)",
            placeholder="Provide any additional information about the issue, severity, or impact...",
            help="Any extra context that might be helpful for addressing the issue"
        )
        
        # Submit button
        submit_button = st.form_submit_button("📤 Submit Report", type="primary")
        
        if submit_button:
            # Validate inputs
            validation_errors = validate_inputs(uploaded_file, location_description)
            
            if validation_errors:
                st.error("❌ Please fix the following issues:")
                for error in validation_errors:
                    st.warning(error)
            else:
                try:
                    with st.spinner("Processing your report..."):
                        # Save the image file with unique name (might already be saved from AI analysis)
                        image_path = save_uploaded_file(uploaded_file)
                        
                        # Insert report into database
                        report_id = insert_report(
                            image_path, 
                            category, 
                            location_description,
                            additional_details if additional_details.strip() else None
                        )
                        
                        if report_id:
                            st.success(f"✅ Report submitted successfully! Report ID: **#{report_id}**")
                            st.balloons()  # Celebration effect
                            
                            # Display confirmation details
                            st.info("📋 **Your report has been recorded and will be reviewed by community managers.**")
                            
                            # Create columns for report summary
                            summary_col1, summary_col2 = st.columns([1, 1])
                            
                            with summary_col1:
                                st.write(f"**🆔 Report ID:** #{report_id}")
                                st.write(f"**📍 Location:** {location_description}")
                                st.write(f"**🏷️ Category:** {category}")
                                st.write(f"**⏰ Submitted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                if additional_details and additional_details.strip():
                                    st.write(f"**📝 Details:** {additional_details}")
                            
                            with summary_col2:
                                # Display the uploaded image
                                image = Image.open(uploaded_file)
                                st.image(
                                    image, 
                                    caption=f"Issue Image - Report #{report_id}", 
                                    width=None
                                )
                                
                                # Display image info in smaller text
                                with st.expander("View Image Details"):
                                    st.write(f"**Filename:** {uploaded_file.name}")
                                    st.write(f"**File size:** {uploaded_file.size / 1024:.2f} KB")
                                    st.write(f"**Format:** {image.format}")
                                    st.write(f"**Dimensions:** {image.size[0]} x {image.size[1]} pixels")
                        else:
                            st.error("❌ Failed to save report to database. Please try again.")
                
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {str(e)}")
                    st.error("Please try again or contact support if the problem persists.")

    # Add section to view recent reports
    st.markdown("---")
    if st.checkbox("👀 View Recent Reports", help="Show the last 5 submitted reports"):
        st.subheader("📋 Recent Reports")
        
        reports = get_recent_reports(5)
        if reports:
            # Display recent reports
            for report in reports:
                report_id, image_path, category, location, additional_details, timestamp, status, priority = report

                # Robust timestamp formatting
                ts_text = str(timestamp)
                if len(ts_text) > 19:
                    ts_text = ts_text[:19]

                with st.expander(f"Report #{report_id} - {category} | {ts_text}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**📍 Location:** {location}")
                        st.write(f"**🏷️ Category:** {category}")
                        st.write(f"**📊 Status:** {status}")
                        st.write(f"**⚡ Priority:** {priority}")
                        if additional_details:
                            st.write(f"**📝 Details:** {additional_details}")
                        st.write(f"**⏰ Reported:** {ts_text}")
                    
                    with col2:
                        # Try to display image if it exists
                        # Support both absolute and relative paths stored in DB
                        stored_path = Path(image_path)
                        candidate_paths = [stored_path, BASE_DIR / stored_path]
                        resolved_path = next((p for p in candidate_paths if p.exists()), None)

                        if resolved_path and resolved_path.exists():
                            try:
                                image = Image.open(resolved_path)
                                st.image(image, width=250)
                            except Exception:
                                st.write("🖼️ Image not available")
                        else:
                            st.write("🖼️ Image file missing")
        else:
            st.info("No reports submitted yet. Submit the first one above!")

def view_and_filter_tab():
    """Tab 2: View and filter reports"""
    
    # Header card
    st.markdown("""
    <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0; color: white;">📊 View & Filter Reports</h2>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">Search and filter through all submitted reports</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter section in a styled container
    with st.container():
        st.markdown("##### 🔎 Filters")
        
        # Create filter columns
        filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        filter_category = st.selectbox(
            "Filter by Category",
            options=['All'] + ISSUE_CATEGORIES,
            key="filter_category"
        )
    
    with filter_col2:
        filter_status = st.selectbox(
            "Filter by Status",
            options=['All'] + STATUS_OPTIONS,
            key="filter_status"
        )
    
    with filter_col3:
        filter_location = st.text_input(
            "Search Location",
            placeholder="Enter location keywords...",
            key="filter_location"
        )
    
    # Date range filters
    date_col1, date_col2 = st.columns(2)
    
    with date_col1:
        date_from = st.date_input(
            "From Date",
            value=None,
            key="date_from"
        )
    
    with date_col2:
        date_to = st.date_input(
            "To Date",
            value=None,
            key="date_to"
        )
    
    if st.button("🔍 Apply Filters", type="primary"):
        # Get filtered reports
        reports = get_filtered_reports(
            category=None if filter_category == 'All' else filter_category,
            status=None if filter_status == 'All' else filter_status,
            date_from=date_from,
            date_to=date_to,
            location=filter_location if filter_location else None
        )
        
        if reports:
            st.success(f"Found {len(reports)} report(s)")
            
            # Display filtered reports in a table
            df_data = []
            for report in reports:
                report_id, image_path, category, location, additional_details, timestamp, status, priority = report
                df_data.append({
                    'ID': report_id,
                    'Category': category,
                    'Location': location[:50] + '...' if len(location) > 50 else location,
                    'Status': status,
                    'Priority': priority,
                    'Timestamp': str(timestamp)[:19]
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, width='stretch')
            
            st.markdown("---")
            st.write("**Detailed View:**")
            
            # Display detailed view with images
            for report in reports:
                report_id, image_path, category, location, additional_details, timestamp, status, priority = report
                
                with st.expander(f"Report #{report_id} - {category}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**📍 Location:** {location}")
                        st.write(f"**🏷️ Category:** {category}")
                        st.write(f"**📊 Status:** {status}")
                        st.write(f"**⚡ Priority:** {priority}")
                        if additional_details:
                            st.write(f"**📝 Details:** {additional_details}")
                        st.write(f"**⏰ Reported:** {str(timestamp)[:19]}")
                    
                    with col2:
                        stored_path = Path(image_path)
                        candidate_paths = [stored_path, BASE_DIR / stored_path]
                        resolved_path = next((p for p in candidate_paths if p.exists()), None)
                        
                        if resolved_path and resolved_path.exists():
                            try:
                                image = Image.open(resolved_path)
                                st.image(image, width=250)
                            except Exception:
                                st.write("🖼️ Image not available")
                        else:
                            st.write("🖼️ Image file missing")
        else:
            st.info("No reports found matching the filters.")

def manage_reports_tab():
    """Tab 3: Manage existing reports"""
    
    # Header card
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0; color: white;">⚙️ Manage Reports</h2>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">Update status, priority, or edit report details</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get all reports
    all_reports = get_all_reports()
    
    if not all_reports:
        st.info("No reports to manage. Submit a report first!")
        return
    
    # Create a selectbox for choosing report
    report_options = [f"#{r[0]} - {r[2]} - {r[3][:30]}..." for r in all_reports]
    selected_index = st.selectbox(
        "Select Report to Manage",
        options=range(len(all_reports)),
        format_func=lambda i: report_options[i]
    )
    
    if selected_index is not None:
        selected_report = all_reports[selected_index]
        report_id, image_path, category, location, additional_details, timestamp, status, priority = selected_report
        
        st.markdown("---")
        st.write(f"### Managing Report #{report_id}")
        
        # Display current report
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**Current Information:**")
            st.write(f"**📍 Location:** {location}")
            st.write(f"**🏷️ Category:** {category}")
            st.write(f"**📊 Status:** {status}")
            st.write(f"**⚡ Priority:** {priority}")
            if additional_details:
                st.write(f"**📝 Details:** {additional_details}")
            st.write(f"**⏰ Reported:** {str(timestamp)[:19]}")
        
        with col2:
            stored_path = Path(image_path)
            candidate_paths = [stored_path, BASE_DIR / stored_path]
            resolved_path = next((p for p in candidate_paths if p.exists()), None)
            
            if resolved_path and resolved_path.exists():
                try:
                    image = Image.open(resolved_path)
                    st.image(image, caption=f"Report #{report_id}", use_column_width=True)
                except Exception:
                    st.write("🖼️ Image not available")
            else:
                st.write("🖼️ Image file missing")
        
        st.markdown("---")
        
        # Management tabs
        mgmt_tab1, mgmt_tab2, mgmt_tab3 = st.tabs(["Update Status/Priority", "Edit Details", "Delete Report"])
        
        with mgmt_tab1:
            st.write("**Update Status and Priority:**")
            
            update_col1, update_col2 = st.columns(2)
            
            with update_col1:
                new_status = st.selectbox(
                    "New Status",
                    options=STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(status) if status in STATUS_OPTIONS else 0,
                    key="new_status"
                )
                
                if st.button("Update Status", type="primary"):
                    if update_report_status(report_id, new_status):
                        st.success(f"✅ Status updated to '{new_status}'")
                        st.rerun()
                    else:
                        st.error("Failed to update status")
            
            with update_col2:
                new_priority = st.selectbox(
                    "New Priority",
                    options=PRIORITY_OPTIONS,
                    index=PRIORITY_OPTIONS.index(priority) if priority in PRIORITY_OPTIONS else 1,
                    key="new_priority"
                )
                
                if st.button("Update Priority", type="primary"):
                    if update_report_priority(report_id, new_priority):
                        st.success(f"✅ Priority updated to '{new_priority}'")
                        st.rerun()
                    else:
                        st.error("Failed to update priority")
        
        with mgmt_tab2:
            st.write("**Edit Report Details:**")
            
            with st.form(f"edit_form_{report_id}"):
                edit_category = st.selectbox(
                    "Category",
                    options=ISSUE_CATEGORIES,
                    index=ISSUE_CATEGORIES.index(category) if category in ISSUE_CATEGORIES else 0
                )
                
                edit_location = st.text_input(
                    "Location",
                    value=location
                )
                
                edit_details = st.text_area(
                    "Additional Details",
                    value=additional_details if additional_details else ""
                )
                
                if st.form_submit_button("💾 Save Changes", type="primary"):
                    if update_report(report_id, edit_category, edit_location, edit_details):
                        st.success("✅ Report updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update report")
        
        with mgmt_tab3:
            st.warning("⚠️ **Warning:** Deleting a report is permanent and cannot be undone!")
            
            confirm_delete = st.checkbox("I understand this action cannot be undone")
            
            if confirm_delete:
                if st.button("🗑️ Delete Report", type="secondary"):
                    if delete_report(report_id):
                        st.success("✅ Report deleted successfully")
                        st.rerun()
                    else:
                        st.error("Failed to delete report")

def map_view_tab():
    """Tab 4: Interactive map showing report locations"""
    
    # Header card
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0; color: white;">🗺️ Map View</h2>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">View all reports with GPS coordinates on an interactive map</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get all reports
    reports = get_all_reports()
    
    if not reports:
        st.info("No reports to display on map. Submit reports with GPS data first!")
        return
    
    # Extract reports with GPS coordinates
    map_reports = []
    for report in reports:
        report_id, image_path, category, location, additional_details, timestamp, status, priority = report
        
        # Try to extract GPS from location string if it contains coordinates
        if "Coordinates:" in location:
            try:
                coords_str = location.split("Coordinates:")[-1].strip()
                lat, lon = map(float, coords_str.split(","))
                map_reports.append({
                    'id': report_id,
                    'lat': lat,
                    'lon': lon,
                    'category': category,
                    'location': location,
                    'status': status,
                    'priority': priority,
                    'timestamp': str(timestamp)[:19]
                })
            except:
                pass
        else:
            # Try to extract GPS from image
            stored_path = Path(image_path)
            candidate_paths = [stored_path, BASE_DIR / stored_path]
            resolved_path = next((p for p in candidate_paths if p.exists()), None)
            
            if resolved_path and resolved_path.exists():
                lat, lon = extract_gps_from_image(str(resolved_path))
                if lat and lon:
                    map_reports.append({
                        'id': report_id,
                        'lat': lat,
                        'lon': lon,
                        'category': category,
                        'location': location,
                        'status': status,
                        'priority': priority,
                        'timestamp': str(timestamp)[:19]
                    })
    
    if not map_reports:
        st.warning("No reports with GPS coordinates found. Upload images with GPS metadata to see them on the map.")
        return
    
    st.success(f"Displaying {len(map_reports)} report(s) with GPS coordinates out of {len(reports)} total reports")
    
    # Create map centered on average location
    avg_lat = sum(r['lat'] for r in map_reports) / len(map_reports)
    avg_lon = sum(r['lon'] for r in map_reports) / len(map_reports)
    
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
    
    # Add markers for each report
    for report in map_reports:
        # Color code by priority
        color_map = {
            'Low': 'green',
            'Medium': 'blue',
            'High': 'orange',
            'Critical': 'red'
        }
        color = color_map.get(report['priority'], 'blue')
        
        # Create popup content
        popup_html = f"""
        <div style="font-family: Arial; font-size: 12px; width: 200px;">
            <b>Report #{report['id']}</b><br>
            <b>Category:</b> {report['category']}<br>
            <b>Status:</b> {report['status']}<br>
            <b>Priority:</b> {report['priority']}<br>
            <b>Location:</b> {report['location'][:50]}...<br>
            <b>Date:</b> {report['timestamp']}
        </div>
        """
        
        folium.Marker(
            location=[report['lat'], report['lon']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"Report #{report['id']} - {report['category']}",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
    
    # Display map
    st_folium(m, width=1200, height=600)
    
    # Legend
    st.markdown("---")
    st.write("**Map Legend:**")
    legend_col1, legend_col2, legend_col3, legend_col4 = st.columns(4)
    
    with legend_col1:
        st.markdown("🟢 **Low Priority**")
    with legend_col2:
        st.markdown("🔵 **Medium Priority**")
    with legend_col3:
        st.markdown("🟠 **High Priority**")
    with legend_col4:
        st.markdown("🔴 **Critical Priority**")

def export_data_tab():
    """Tab 5: Export data"""
    
    # Header card
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0; color: white;">📥 Export Data</h2>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">Download your reports data in various formats</p>
    </div>
    """, unsafe_allow_html=True)
    
    reports = get_all_reports()
    
    if not reports:
        st.info("No reports to export. Submit some reports first!")
        return
    
    st.success(f"**{len(reports)} report(s)** available for export")
    
    # Export options
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        st.write("### 📄 CSV Export")
        st.write("Export all reports as a CSV file for use in spreadsheet applications.")
        
        if st.button("Download as CSV", type="primary"):
            csv_data = export_reports_to_csv()
            if csv_data:
                st.download_button(
                    label="⬇️ Download CSV File",
                    data=csv_data,
                    file_name=f"local_lens_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.error("Failed to generate CSV")
    
    with export_col2:
        st.write("### 📊 Data Preview")
        st.write("Preview of reports to be exported:")
        
        # Create preview DataFrame
        df_data = []
        for report in reports[:10]:  # Show first 10
            report_id, image_path, category, location, additional_details, timestamp, status, priority = report
            df_data.append({
                'ID': report_id,
                'Category': category,
                'Location': location[:40] + '...' if len(location) > 40 else location,
                'Status': status,
                'Priority': priority,
                'Date': str(timestamp)[:19]
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, width='stretch')
        
        if len(reports) > 10:
            st.caption(f"Showing first 10 of {len(reports)} reports")
    
    st.markdown("---")
    
    # Statistics summary
    st.write("### 📈 Export Statistics Summary")
    
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    
    with stats_col1:
        st.metric("Total Reports", len(reports))
    
    with stats_col2:
        status_counts = {}
        for r in reports:
            status_counts[r[6]] = status_counts.get(r[6], 0) + 1
        st.metric("Unique Statuses", len(status_counts))
    
    with stats_col3:
        category_counts = {}
        for r in reports:
            category_counts[r[2]] = category_counts.get(r[2], 0) + 1
        st.metric("Unique Categories", len(category_counts))
    
    with stats_col4:
        priority_counts = {}
        for r in reports:
            priority_counts[r[7]] = priority_counts.get(r[7], 0) + 1
        st.metric("Unique Priorities", len(priority_counts))

if __name__ == "__main__":
    main()
