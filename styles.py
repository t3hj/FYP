"""
CSS styling for Local Lens application.
Supports dark and light themes with toggle.
"""
import streamlit as st


def get_theme():
    """Get current theme from session state"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'
    return st.session_state.theme


def toggle_theme():
    """Toggle between dark and light themes"""
    if st.session_state.theme == 'dark':
        st.session_state.theme = 'light'
    else:
        st.session_state.theme = 'dark'


# Loading animation CSS
LOADING_ANIMATION_CSS = """
<style>
    /* ========== LOADING ANIMATION ========== */
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.95); }
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes bounce {
        0%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
    }
    
    .ai-loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 30px;
        border-radius: 12px;
        margin: 20px 0;
    }
    
    .ai-loading-spinner {
        width: 60px;
        height: 60px;
        border: 4px solid rgba(88, 166, 255, 0.2);
        border-top: 4px solid #58a6ff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 20px;
    }
    
    .ai-loading-text {
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 10px;
    }
    
    .ai-loading-dots {
        display: flex;
        gap: 8px;
    }
    
    .ai-loading-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #58a6ff;
        animation: bounce 1.4s ease-in-out infinite;
    }
    
    .ai-loading-dot:nth-child(1) { animation-delay: 0s; }
    .ai-loading-dot:nth-child(2) { animation-delay: 0.2s; }
    .ai-loading-dot:nth-child(3) { animation-delay: 0.4s; }
    
    .ai-loading-steps {
        margin-top: 15px;
        font-size: 0.9rem;
        opacity: 0.8;
    }
</style>
"""


# Dark theme CSS
DARK_THEME_CSS = """
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


# Light theme CSS
LIGHT_THEME_CSS = """
<style>
    /* ========== BASE LIGHT THEME ========== */
    
    /* Main background and text */
    .stApp {
        background-color: #f5f5f5 !important;
        color: #24292f !important;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* All text defaults to dark */
    h1, h2, h3, h4, h5, h6 {
        color: #24292f !important;
    }
    
    p, span, li, td, th, label, div {
        color: #24292f !important;
    }
    
    /* ========== SIDEBAR ========== */
    
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #d0d7de;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #24292f !important;
    }
    
    /* ========== CARDS & CONTAINERS ========== */
    
    .stForm, .stExpander {
        background-color: #ffffff !important;
        border: 1px solid #d0d7de !important;
        border-radius: 8px;
    }
    
    .stExpander summary {
        color: #24292f !important;
    }
    
    .stExpander [data-testid="stExpanderDetails"] * {
        color: #24292f !important;
    }
    
    /* ========== TABS ========== */
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: #ffffff;
        border-radius: 8px;
        gap: 4px;
        border: 1px solid #d0d7de;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f6f8fa !important;
        color: #24292f !important;
        border-radius: 6px;
        border: 1px solid #d0d7de;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f883d !important;
        color: #ffffff !important;
        border: 1px solid #1f883d !important;
    }
    
    /* ========== BUTTONS ========== */
    
    .stButton > button {
        background-color: #1f883d !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500 !important;
    }
    
    .stButton > button:hover {
        background-color: #2da44e !important;
        color: #ffffff !important;
    }
    
    /* Sidebar buttons - ensure visible text */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #1f883d !important;
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #2da44e !important;
        color: #ffffff !important;
    }
    
    /* Popover trigger button */
    [data-testid="stPopover"] > button,
    button[data-testid="stPopoverButton"],
    .stPopover > button {
        background-color: #1f883d !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px;
        font-weight: 500 !important;
    }
    
    [data-testid="stPopover"] > button:hover,
    button[data-testid="stPopoverButton"]:hover {
        background-color: #2da44e !important;
        color: #ffffff !important;
    }
    
    /* Popover content */
    [data-testid="stPopoverBody"],
    [data-testid="stPopover"] [data-testid="stPopoverBody"] {
        background-color: #ffffff !important;
        border: 1px solid #d0d7de !important;
    }
    
    [data-testid="stPopoverBody"] * {
        color: #24292f !important;
    }
    
    [data-testid="stPopoverBody"] button {
        color: #ffffff !important;
    }
    
    .stDownloadButton > button {
        background-color: #1f883d !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px;
    }
    
    .stFormSubmitButton > button {
        background-color: #1f883d !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px;
        padding: 0.6rem 1.5rem;
        font-weight: 600 !important;
    }
    
    /* ========== INPUTS ========== */
    
    /* Text inputs */
    .stTextInput input,
    .stTextArea textarea,
    .stDateInput input,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        color: #24292f !important;
        border: 1px solid #d0d7de !important;
        border-radius: 6px;
    }
    
    /* Selectbox / Dropdown - comprehensive override */
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"],
    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] > div > div,
    .stMultiSelect [data-baseweb="select"],
    .stMultiSelect [data-baseweb="select"] > div,
    [data-baseweb="select"],
    [data-baseweb="select"] > div,
    [data-baseweb="select"] > div > div,
    div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #24292f !important;
        border-color: #d0d7de !important;
    }
    
    /* The control container */
    [data-baseweb="select"] [class*="control"] {
        background-color: #ffffff !important;
    }
    
    /* Value container */
    [data-baseweb="select"] [class*="valueContainer"],
    [data-baseweb="select"] [class*="singleValue"] {
        color: #24292f !important;
    }
    
    /* Dropdown selected value */
    [data-baseweb="select"] span,
    [data-baseweb="select"] [data-testid="stMarkdownContainer"],
    .stSelectbox span,
    .stSelectbox div[data-baseweb] span {
        color: #24292f !important;
    }
    
    /* Dropdown icon */
    [data-baseweb="select"] svg,
    .stSelectbox svg {
        fill: #24292f !important;
    }
    
    /* Placeholder text */
    [data-baseweb="select"] [class*="placeholder"] {
        color: #57606a !important;
    }
    
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: #0969da !important;
        box-shadow: 0 0 0 2px rgba(9, 105, 218, 0.3) !important;
    }
    
    .stSelectbox label,
    .stTextInput label,
    .stTextArea label,
    .stDateInput label {
        color: #24292f !important;
    }
    
    /* Dropdown menu */
    [data-baseweb="menu"], 
    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-baseweb="list"] {
        background-color: #ffffff !important;
        border: 1px solid #d0d7de !important;
    }
    
    [data-baseweb="menu"] li,
    [data-baseweb="list"] li,
    [data-baseweb="menu"] ul li,
    [role="option"] {
        color: #24292f !important;
        background-color: #ffffff !important;
    }
    
    [data-baseweb="menu"] li:hover,
    [data-baseweb="list"] li:hover,
    [role="option"]:hover {
        background-color: #f6f8fa !important;
    }
    
    /* ========== FILE UPLOADER ========== */
    
    [data-testid="stFileUploader"] {
        background-color: #ffffff !important;
        border: 2px dashed #d0d7de !important;
        border-radius: 8px;
    }
    
    [data-testid="stFileUploader"] * {
        color: #24292f !important;
    }
    
    [data-testid="stFileUploader"] button {
        background-color: #1f883d !important;
        color: #ffffff !important;
    }
    
    /* File uploader section styling */
    [data-testid="stFileUploader"] section {
        background-color: #ffffff !important;
    }
    
    /* Subheader styling */
    .stSubheader, [data-testid="stSubheader"] {
        color: #24292f !important;
    }
    
    /* ========== ALERTS / NOTIFICATIONS ========== */
    
    /* Success - Green */
    .stSuccess, [data-testid="stNotification"][aria-label*="success"],
    div[data-baseweb="notification"]:has([data-testid="stNotificationContentSuccess"]) {
        background-color: #dafbe1 !important;
        border: 1px solid #1f883d !important;
        border-radius: 6px;
    }
    
    .stSuccess *, [data-testid="stNotificationContentSuccess"] * {
        color: #116329 !important;
    }
    
    /* Info - Blue */
    .stInfo, [data-testid="stNotification"][aria-label*="info"],
    div[data-baseweb="notification"]:has([data-testid="stNotificationContentInfo"]) {
        background-color: #ddf4ff !important;
        border: 1px solid #0969da !important;
        border-radius: 6px;
    }
    
    .stInfo *, [data-testid="stNotificationContentInfo"] * {
        color: #0550ae !important;
    }
    
    /* Warning - Yellow */
    .stWarning, [data-testid="stNotification"][aria-label*="warning"],
    div[data-baseweb="notification"]:has([data-testid="stNotificationContentWarning"]) {
        background-color: #fff8c5 !important;
        border: 1px solid #bf8700 !important;
        border-radius: 6px;
    }
    
    .stWarning *, [data-testid="stNotificationContentWarning"] * {
        color: #9a6700 !important;
    }
    
    /* Error - Red */
    .stError, [data-testid="stNotification"][aria-label*="error"],
    div[data-baseweb="notification"]:has([data-testid="stNotificationContentError"]) {
        background-color: #ffebe9 !important;
        border: 1px solid #cf222e !important;
        border-radius: 6px;
    }
    
    .stError *, [data-testid="stNotificationContentError"] * {
        color: #a40e26 !important;
    }
    
    /* ========== METRICS ========== */
    
    [data-testid="metric-container"] {
        background-color: #f6f8fa !important;
        border: 1px solid #d0d7de !important;
        border-radius: 8px;
        padding: 12px;
    }
    
    [data-testid="metric-container"] label,
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #24292f !important;
    }
    
    /* ========== DATAFRAME / TABLE ========== */
    
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    .stDataFrame, .stDataFrame td, .stDataFrame th {
        background-color: #ffffff !important;
        color: #24292f !important;
        border-color: #d0d7de !important;
    }
    
    /* ========== IMAGES ========== */
    
    .stImage {
        border-radius: 8px;
        overflow: hidden;
    }
    
    .stImage figcaption {
        color: #57606a !important;
    }
    
    /* ========== CHECKBOX ========== */
    
    .stCheckbox label span {
        color: #24292f !important;
    }
    
    /* ========== DIVIDER ========== */
    
    hr {
        border: none;
        height: 1px;
        background-color: #d0d7de;
        margin: 1.5rem 0;
    }
    
    /* ========== PROGRESS BAR ========== */
    
    .stProgress > div > div {
        background-color: #1f883d !important;
    }
    
    .stProgress {
        background-color: #eaeef2 !important;
    }
    
    /* ========== SPINNER ========== */
    
    .stSpinner > div {
        color: #24292f !important;
    }
    
    /* ========== LINKS ========== */
    
    a {
        color: #0969da !important;
    }
    
    a:hover {
        color: #0550ae !important;
    }
    
    /* ========== CODE ========== */
    
    code {
        background-color: #f6f8fa !important;
        color: #24292f !important;
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    /* ========== BLOCKQUOTE ========== */
    
    blockquote {
        border-left: 3px solid #d0d7de;
        padding-left: 1rem;
        color: #57606a !important;
    }
    
    /* ========== MARKDOWN CONTAINERS ========== */
    
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        color: #24292f !important;
    }
    
    /* Form section headers */
    .stForm h3, .stForm h2, .stForm p {
        color: #24292f !important;
    }
    
    /* Main content area */
    .main [data-testid="stVerticalBlock"] {
        color: #24292f !important;
    }
    
    /* Ensure all form text is dark */
    .stForm * {
        color: #24292f !important;
    }
    
    .stForm button, .stForm button span {
        color: #ffffff !important;
    }
</style>
"""


def get_custom_css():
    """Get the appropriate CSS based on current theme"""
    theme = get_theme()
    if theme == 'light':
        return LOADING_ANIMATION_CSS + LIGHT_THEME_CSS
    else:
        return LOADING_ANIMATION_CSS + DARK_THEME_CSS


# For backwards compatibility
CUSTOM_CSS = LOADING_ANIMATION_CSS + DARK_THEME_CSS


# Tab header cards - theme-aware style
def get_tab_header(title, subtitle, gradient=None):
    """Generate HTML for a styled tab header card
    
    Args:
        title (str): Main title with emoji
        subtitle (str): Description text
        gradient (str): Unused - kept for compatibility
        
    Returns:
        str: HTML for the header card
    """
    theme = get_theme()
    if theme == 'light':
        bg_color = "#f6f8fa"
        border_color = "#d0d7de"
        title_color = "#24292f"
        subtitle_color = "#57606a"
    else:
        bg_color = "#161b22"
        border_color = "#30363d"
        title_color = "#e6edf3"
        subtitle_color = "#8b949e"
    
    return f"""
    <div style="background-color: {bg_color}; padding: 20px; border-radius: 8px; border: 1px solid {border_color}; margin-bottom: 20px;">
        <h2 style="margin: 0; color: {title_color};">{title}</h2>
        <p style="margin: 10px 0 0 0; color: {subtitle_color};">{subtitle}</p>
    </div>
    """


def get_loading_animation(message="AI analyzing image...", steps=None):
    """Generate HTML for a custom loading animation
    
    Args:
        message (str): Loading message to display
        steps (list): Optional list of steps being performed
        
    Returns:
        str: HTML for the loading animation
    """
    theme = get_theme()
    if theme == 'light':
        bg_color = "#f6f8fa"
        border_color = "#d0d7de"
        text_color = "#24292f"
        spinner_color = "#0969da"
    else:
        bg_color = "#161b22"
        border_color = "#30363d"
        text_color = "#e6edf3"
        spinner_color = "#58a6ff"
    
    steps_html = ""
    if steps:
        steps_html = f'<div class="ai-loading-steps" style="color: {text_color};">{"<br>".join(steps)}</div>'
    
    return f"""
    <div class="ai-loading-container" style="background-color: {bg_color}; border: 1px solid {border_color};">
        <div class="ai-loading-spinner" style="border-color: rgba(88, 166, 255, 0.2); border-top-color: {spinner_color};"></div>
        <div class="ai-loading-text" style="color: {text_color};">🤖 {message}</div>
        <div class="ai-loading-dots">
            <div class="ai-loading-dot" style="background-color: {spinner_color};"></div>
            <div class="ai-loading-dot" style="background-color: {spinner_color};"></div>
            <div class="ai-loading-dot" style="background-color: {spinner_color};"></div>
        </div>
        {steps_html}
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