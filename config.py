"""
Configuration and constants for Local Lens application.
"""
from pathlib import Path

# Database settings
DATABASE_NAME = "reports.db"

# File upload settings
UPLOAD_DIR = "uploads"
SUPPORTED_IMAGE_TYPES = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'heic']
MAX_IMAGE_SIZE_MB = 10

# Issue categories
ISSUE_CATEGORIES = [
    'Pothole', 
    'Broken Streetlight', 
    'Graffiti', 
    'Litter', 
    'Damaged Road Sign', 
    'Other'
]

# Status options for reports
STATUS_OPTIONS = ['Reported', 'In Progress', 'Resolved', 'Closed']

# Priority levels
PRIORITY_OPTIONS = ['Low', 'Medium', 'High', 'Critical']

# Category icons mapping
CATEGORY_ICONS = {
    'Pothole': '🕳️',
    'Broken Streetlight': '💡',
    'Graffiti': '🎨',
    'Litter': '🗑️',
    'Damaged Road Sign': '🚧',
    'Other': '📌'
}

# Priority colors (background, text)
PRIORITY_COLORS = {
    'Critical': ('#dc3545', 'white'),
    'High': ('#fd7e14', 'white'),
    'Medium': ('#ffc107', 'black'),
    'Low': ('#28a745', 'white')
}

# Status colors (background, text)
STATUS_COLORS = {
    'Reported': ('#6c757d', 'white'),
    'In Progress': ('#17a2b8', 'white'),
    'Resolved': ('#28a745', 'white'),
    'Closed': ('#343a40', 'white')
}

# Resolve base paths to avoid CWD issues when launching Streamlit
BASE_DIR = Path(__file__).parent.resolve()
DATABASE_PATH = BASE_DIR / DATABASE_NAME
UPLOAD_PATH = BASE_DIR / UPLOAD_DIR
