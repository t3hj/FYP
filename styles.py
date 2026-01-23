"""
CSS styling for Local Lens application.
All custom styles are centralized here.
"""

CUSTOM_CSS = """
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
"""


# Tab header cards with gradient backgrounds
def get_tab_header(title, subtitle, gradient):
    """Generate HTML for a styled tab header card
    
    Args:
        title (str): Main title with emoji
        subtitle (str): Description text
        gradient (str): CSS gradient string
        
    Returns:
        str: HTML for the header card
    """
    return f"""
    <div style="background: {gradient}; padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0; color: white;">{title}</h2>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">{subtitle}</p>
    </div>
    """


# Predefined gradients for each tab
TAB_GRADIENTS = {
    'submit': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'view': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    'manage': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'map': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'export': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
}
