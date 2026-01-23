# Local Lens: Community Issue Reporter

A Streamlit web application for reporting and tracking community issues in your local area. Upload images of problems like potholes, broken streetlights, graffiti, and more. Now enhanced with AI-powered automatic location detection and issue categorization!

## Features

### Core Features
- **📸 Image Upload**: Support for multiple image formats (PNG, JPG, JPEG, GIF, BMP, WEBP, HEIC)
- **💾 Data Storage**: SQLite database for storing report metadata with enhanced schema
- **📊 Dashboard & Statistics**: Sidebar with real-time report counts and category breakdown
- **✅ Input Validation**: Client-side validation for required fields and file sizes
- **🆔 Unique File Naming**: UUID-based naming to prevent file conflicts
- **📝 Detailed Reports**: Track location, category, additional details, status, and priority
- **🎨 Modern UI**: Clean interface with forms, expanders, and helpful tooltips
- **👀 Recent Reports View**: Preview of last 5 submitted reports with images

### 🤖 AI-Powered Features
- **🗺️ GPS Location Extraction**: Automatically extracts GPS coordinates from image EXIF data
- **📍 Reverse Geocoding**: Converts GPS coordinates to human-readable addresses
- **🤖 AI Category Detection**: Uses OpenAI GPT-4 Vision to automatically suggest the most appropriate issue category
- **✨ Smart Auto-fill**: Location and category fields are automatically populated based on image analysis

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone or download this project
2. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # On Windows PowerShell
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Setting Up AI Features (Multiple Free Options)

The app supports multiple AI backends for image analysis, trying them in order:

#### **Option 1: Ollama (Recommended - 100% Free, Unlimited)**

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Install the LLaVA vision model:
   ```bash
   ollama pull llava
   ```
3. Keep Ollama running in the background
4. The app will automatically use it - no API key needed!

#### **Option 2: Hugging Face (Free Tier)**

- Uses CLIP model from Hugging Face
- Automatically works without setup
- Has rate limits but generous for personal use

#### **Option 3: Google Gemini (Limited Free Tier)**

1. Get an API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Set it as an environment variable:
   ```powershell
   # Windows PowerShell
   $env:GOOGLE_API_KEY="your-api-key-here"
   ```

**Note**: The app tries all methods automatically - GPS location extraction works without any AI setup.

### Running the Application

1. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to the provided local URL (typically `http://localhost:8501`)

3. Use the application:
   - **Submit Reports**: Upload an image and watch AI auto-detect location and category
   - **Review AI Suggestions**: Edit the auto-filled location and category if needed
   - **View Statistics**: Check the sidebar for report counts and category breakdown
   - **Recent Reports**: Toggle the checkbox to view the last 5 submitted reports
   - **Track Issues**: Each report gets a unique ID for tracking

### AI Features in Action

When you upload an image:
1. 🗺️ **GPS Extraction**: If your image has GPS metadata (from a smartphone), location is auto-detected
2. 📍 **Reverse Geocoding**: GPS coordinates are converted to a readable address
3. 🤖 **AI Analysis**: GPT-4 Vision analyzes the image to suggest the appropriate category
4. ✨ **Auto-fill**: Location and category fields are populated automatically
5. ✏️ **Manual Override**: You can edit any auto-filled fields before submitting


## Project Structure

```
FYP/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .github/
│   └── copilot-instructions.md
├── uploads/              # Directory for uploaded images (created automatically)
└── reports.db            # SQLite database (created automatically)
```

## Database Schema

The application uses a SQLite database (`reports.db`) with the following table structure:

```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path TEXT NOT NULL,
    category TEXT NOT NULL,
    location TEXT NOT NULL,
    additional_details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Reported',
    priority TEXT DEFAULT 'Medium'
);
```

## Code Improvements (Phase 1)

✅ **Completed Refactoring:**
- Added constants for better maintainability (DATABASE_NAME, UPLOAD_DIR, etc.)
- Implemented UUID-based unique file naming to prevent conflicts
- Enhanced database schema with status, priority, and additional_details fields
- Added comprehensive input validation with helpful error messages
- Improved error handling with try-except blocks throughout
- Created helper functions: `save_uploaded_file()`, `validate_inputs()`, `display_sidebar()`
- Added statistics functions: `get_all_reports()`, `get_report_statistics()`
- Implemented Streamlit forms for better UX and single submission
- Added sidebar dashboard with real-time statistics
- Enhanced UI with expanders, tooltips, and better visual feedback
- Added celebration effects (balloons) on successful submission
- Implemented "Recent Reports" viewer with image previews

## Phase 2 Features - Data & Visualization

✅ **Completed Features:**
- **Advanced Filtering Dashboard**: Filter reports by category, status, date range, and location with real-time results
- **Report Management System**: 
  - Update report status (Reported, In Progress, Resolved, Closed)
  - Change priority levels (Low, Medium, High, Critical)
  - Edit report details (category, location, additional information)
  - Delete reports with confirmation safeguards
- **Data Export**: Export all reports to CSV format with timestamps
- **Interactive Map View**: Folium-powered map showing all reports with GPS coordinates
  - Color-coded markers by priority level
  - Interactive popups with report details
  - Legend for easy interpretation
  - Automatic centering on report locations
- **Tabbed Interface**: Organized UI with separate tabs for Submit, View/Filter, Manage, Map, and Export

**New Database Functions:**
- `get_filtered_reports()`: Advanced filtering with multiple criteria
- `update_report_status()`, `update_report_priority()`: Status and priority management
- `update_report()`: Edit report details
- `delete_report()`: Remove reports from database
- `get_report_by_id()`: Retrieve specific reports
- `export_reports_to_csv()`: Generate CSV exports

## Future Enhancements

**Phase 3 - Advanced Features:**
- User authentication and profiles
- Search and advanced filtering
- AI-powered image classification
- Duplicate report detection
- Email notifications

**Phase 4 - Scaling:**
- REST API development
- Cloud deployment
- Performance optimization
- Mobile app support

## Development

This project is set up for easy development and extension. The modular structure allows for easy addition of new features and components.

## License

This project is for educational purposes as part of a Final Year Project (FYP).
