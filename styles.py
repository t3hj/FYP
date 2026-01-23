"""
CSS styling for Local Lens application.
Simple dark theme following standard practices.
"""

CUSTOM_CSS = """
<style>
    /* ========== BASE DARK THEME ========== */
    
    /* Main background and text */
    .stApp {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* All text defaults to light */
    h1, h2, h3, h4, h5, h6 {
        color: #e6edf3 !important;
    }
    
    p, span, li, td, th, label, div {
        color: #e6edf3 !important;
    }
    
    /* ========== SIDEBAR ========== */
    
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #e6edf3 !important;
    }
    
    /* ========== CARDS & CONTAINERS ========== */
    
    .stForm, .stExpander {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px;
    }
    
    .stExpander summary {
        color: #e6edf3 !important;
    }
    
    .stExpander [data-testid="stExpanderDetails"] * {
        color: #e6edf3 !important;
    }
    
    /* ========== TABS ========== */
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161b22;
        border-radius: 8px;
        gap: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #21262d !important;
        color: #e6edf3 !important;
        border-radius: 6px;
        border: 1px solid #30363d;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #238636 !important;
        color: #ffffff !important;
        border: 1px solid #238636 !important;
    }
    
    /* ========== BUTTONS ========== */
    
    .stButton > button {
        background-color: #238636 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500 !important;
    }
    
    .stButton > button:hover {
        background-color: #2ea043 !important;
    }
    
    .stDownloadButton > button {
        background-color: #238636 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px;
    }
    
    .stFormSubmitButton > button {
        background-color: #238636 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px;
        padding: 0.6rem 1.5rem;
        font-weight: 600 !important;
    }
    
    /* ========== INPUTS ========== */
    
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox [data-baseweb="select"],
    .stDateInput input {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px;
    }
    
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.3) !important;
    }
    
    .stSelectbox label,
    .stTextInput label,
    .stTextArea label,
    .stDateInput label {
        color: #e6edf3 !important;
    }
    
    /* Dropdown menu */
    [data-baseweb="menu"], [data-baseweb="popover"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
    }
    
    [data-baseweb="menu"] li {
        color: #e6edf3 !important;
    }
    
    [data-baseweb="menu"] li:hover {
        background-color: #21262d !important;
    }
    
    /* ========== FILE UPLOADER ========== */
    
    [data-testid="stFileUploader"] {
        background-color: #161b22 !important;
        border: 2px dashed #30363d !important;
        border-radius: 8px;
    }
    
    [data-testid="stFileUploader"] * {
        color: #e6edf3 !important;
    }
    
    /* ========== ALERTS / NOTIFICATIONS ========== */
    
    /* Success - Green */
    .stSuccess, [data-testid="stNotification"][aria-label*="success"],
    div[data-baseweb="notification"]:has([data-testid="stNotificationContentSuccess"]) {
        background-color: #1f3d2a !important;
        border: 1px solid #238636 !important;
        border-radius: 6px;
    }
    
    .stSuccess *, [data-testid="stNotificationContentSuccess"] * {
        color: #56d364 !important;
    }
    
    /* Info - Blue */
    .stInfo, [data-testid="stNotification"][aria-label*="info"],
    div[data-baseweb="notification"]:has([data-testid="stNotificationContentInfo"]) {
        background-color: #1a3a4a !important;
        border: 1px solid #58a6ff !important;
        border-radius: 6px;
    }
    
    .stInfo *, [data-testid="stNotificationContentInfo"] * {
        color: #79c0ff !important;
    }
    
    /* Warning - Yellow */
    .stWarning, [data-testid="stNotification"][aria-label*="warning"],
    div[data-baseweb="notification"]:has([data-testid="stNotificationContentWarning"]) {
        background-color: #3d3421 !important;
        border: 1px solid #d29922 !important;
        border-radius: 6px;
    }
    
    .stWarning *, [data-testid="stNotificationContentWarning"] * {
        color: #e3b341 !important;
    }
    
    /* Error - Red */
    .stError, [data-testid="stNotification"][aria-label*="error"],
    div[data-baseweb="notification"]:has([data-testid="stNotificationContentError"]) {
        background-color: #3d1f20 !important;
        border: 1px solid #f85149 !important;
        border-radius: 6px;
    }
    
    .stError *, [data-testid="stNotificationContentError"] * {
        color: #ff7b72 !important;
    }
    
    /* ========== METRICS ========== */
    
    [data-testid="metric-container"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px;
        padding: 12px;
    }
    
    [data-testid="metric-container"] label,
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #e6edf3 !important;
    }
    
    /* ========== DATAFRAME / TABLE ========== */
    
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    .stDataFrame, .stDataFrame td, .stDataFrame th {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        border-color: #30363d !important;
    }
    
    /* ========== IMAGES ========== */
    
    .stImage {
        border-radius: 8px;
        overflow: hidden;
    }
    
    .stImage figcaption {
        color: #8b949e !important;
    }
    
    /* ========== CHECKBOX ========== */
    
    .stCheckbox label span {
        color: #e6edf3 !important;
    }
    
    /* ========== DIVIDER ========== */
    
    hr {
        border: none;
        height: 1px;
        background-color: #30363d;
        margin: 1.5rem 0;
    }
    
    /* ========== PROGRESS BAR ========== */
    
    .stProgress > div > div {
        background-color: #238636 !important;
    }
    
    .stProgress {
        background-color: #21262d !important;
    }
    
    /* ========== SPINNER ========== */
    
    .stSpinner > div {
        color: #e6edf3 !important;
    }
    
    /* ========== LINKS ========== */
    
    a {
        color: #58a6ff !important;
    }
    
    a:hover {
        color: #79c0ff !important;
    }
    
    /* ========== CODE ========== */
    
    code {
        background-color: #21262d !important;
        color: #e6edf3 !important;
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    /* ========== BLOCKQUOTE ========== */
    
    blockquote {
        border-left: 3px solid #30363d;
        padding-left: 1rem;
        color: #8b949e !important;
    }
</style>
"""


# Tab header cards - simple dark style
def get_tab_header(title, subtitle, gradient=None):
    """Generate HTML for a styled tab header card
    
    Args:
        title (str): Main title with emoji
        subtitle (str): Description text
        gradient (str): Unused - kept for compatibility
        
    Returns:
        str: HTML for the header card
    """
    return f"""
    <div style="background-color: #161b22; padding: 20px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 20px;">
        <h2 style="margin: 0; color: #e6edf3;">{title}</h2>
        <p style="margin: 10px 0 0 0; color: #8b949e;">{subtitle}</p>
    </div>
    """


# Kept for compatibility - not used in simple theme
TAB_GRADIENTS = {
    'submit': None,
    'view': None,
    'manage': None,
    'map': None,
    'export': None,
}
